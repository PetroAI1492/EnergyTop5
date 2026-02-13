#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
load_observations.py

Unified loader for FRED + EIA observations using series_new schema.

Supports:
    --eia   Load only EIA series
    --fred  Load only FRED series
    (no flags) Load both
"""

import sqlite3
import requests
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# Paths & Keys
# ==============================================================================

DB_PATH = r"c:\Thor\storehouse.db"
SECRETS = Path(r"c:\mygit\secrets")

FRED_KEY = (SECRETS / "fred.key").read_text().strip()
EIA_KEY  = (SECRETS / "eia.key").read_text().strip()

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
EIA_BASE  = "https://api.eia.gov/v2"

NOW_UTC = datetime.now(timezone.utc).isoformat()

# ==============================================================================
# Series to skip (these will be marked inactive)
# ==============================================================================

SKIP_FRED = {
    "IPG33441A2N",
    "WCREXUS",
    "WCRIMUS"
}

SKIP_EIA = {
    "PET.WCRFPUS2.W",
    "PET.WCRRIUS2.W",
    "PET.WPULEUS3.W"
}

# ==============================================================================
# DB Helpers
# ==============================================================================

def db():
    return sqlite3.connect(DB_PATH)

def max_period(conn, series_id):
    row = conn.execute(
        "SELECT MAX(period) FROM observations WHERE series_id = ?",
        (series_id,)
    ).fetchone()
    return row[0]

# ==============================================================================
# Fetch Series (series_new)
# ==============================================================================

def fetch_series(source_filter=None):
    with db() as conn:

        # EIA: load ALL active EIA series
        if source_filter == "eia":
            return conn.execute("""
                SELECT series_id, source, frequency, endpoint, facet_key, facet_value
                FROM series_new
                WHERE active = 1
                  AND source = 'eia'
                ORDER BY series_id
            """).fetchall()

        # FRED only
        elif source_filter == "fred":
            return conn.execute("""
                SELECT series_id, source, frequency, endpoint, facet_key, facet_value
                FROM series_new
                WHERE active = 1
                  AND source = 'fred'
                ORDER BY series_id
            """).fetchall()

        # Default: load everything active
        else:
            return conn.execute("""
                SELECT series_id, source, frequency, endpoint, facet_key, facet_value
                FROM series_new
                WHERE active = 1
                ORDER BY source, series_id
            """).fetchall()

# ==============================================================================
# UPSERT Observation
# ==============================================================================

def upsert(conn, series_id, period, value, source):
    conn.execute("""
        INSERT OR REPLACE INTO observations (
            series_id, period, value, source, ingested_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (series_id, period, value, source, NOW_UTC))

# ==============================================================================
# EIA Retry Logic (2 attempts only)
# ==============================================================================

def eia_request_with_retry(url, params, retries=2, timeout=60):
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
        except requests.exceptions.ReadTimeout:
            print(f"  [WARN] Timeout on attempt {attempt+1}/{retries}")
            continue

        if r.status_code == 200:
            return r

        if 500 <= r.status_code < 600:
            print(f"  [WARN] EIA 500 on attempt {attempt+1}/{retries}")
            continue

        r.raise_for_status()

    return None

# ==============================================================================
# FRED Loader
# ==============================================================================

def load_fred(series_id):
    # Skip = mark inactive
    if series_id in SKIP_FRED:
        with db() as conn:
            conn.execute("UPDATE series_new SET active = 0 WHERE series_id = ?", (series_id,))
        print(f"[INACTIVE] {series_id}: marked inactive (FRED skip)")
        return 0

    with db() as conn:
        last = max_period(conn, series_id)

    params = {
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json"
    }

    r = requests.get(FRED_BASE, params=params, timeout=30)
    r.raise_for_status()

    observations = r.json().get("observations", [])
    inserts = 0

    with db() as conn:
        for obs in observations:
            period = obs["date"]
            value_str = obs["value"]

            if value_str in ("", ".", "NaN"):
                continue
            if last and period <= last:
                continue

            upsert(conn, series_id, period, float(value_str), "fred")
            inserts += 1

    return inserts

# ==============================================================================
# EIA Loader
# ==============================================================================

def load_eia(series_id, frequency, endpoint, facet_key, facet_value):

    # Skip = mark inactive
    if series_id in SKIP_EIA:
        with db() as conn:
            conn.execute("UPDATE series_new SET active = 0 WHERE series_id = ?", (series_id,))
        print(f"[INACTIVE] {series_id}: marked inactive (EIA skip)")
        return 0

    with db() as conn:
        last = max_period(conn, series_id)

    # base params
    params = {
        "api_key": EIA_KEY,
        "data[]": "value",
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
    }

    # frequency if present
    if frequency:
        params["frequency"] = frequency

    # facet handling:
    # - if facet_key/facet_value are empty → no facets (stocks etc.)
    # - if they contain commas → split and emit one facet per pair
    if facet_key and facet_value:
        if "," in facet_key:
            keys = [k.strip() for k in facet_key.split(",")]
            values = [v.strip() for v in facet_value.split(",")]
            for k, v in zip(keys, values):
                params[f"facets[{k}][]"] = v
        else:
            params[f"facets[{facet_key}][]"] = facet_value

    url = f"{EIA_BASE}/{endpoint}/data"

    r = eia_request_with_retry(url, params)

    if r is None:
        print(f"  [SKIP] EIA unavailable after retries")
        return 0

    rows = r.json().get("response", {}).get("data", [])
    inserts = 0

    with db() as conn:
        for row in rows:
            period = row["period"]
            value  = row.get("value")

            if value is None:
                continue
            if last and period <= last:
                continue

            upsert(conn, series_id, period, float(value), "eia")
            inserts += 1

    return inserts

# ==============================================================================
# Main
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Load observations from FRED and/or EIA")
    parser.add_argument("--fred", action="store_true", help="Load only FRED series")
    parser.add_argument("--eia", action="store_true", help="Load only EIA series")
    args = parser.parse_args()

    if args.fred and not args.eia:
        source_filter = "fred"
    elif args.eia and not args.fred:
        source_filter = "eia"
    else:
        source_filter = None

    print("=== Storehouse Observation Load ===")
    print(NOW_UTC)

    series_list = fetch_series(source_filter)
    print(f"Series to load: {len(series_list)}")

    for series_id, source, frequency, endpoint, facet_key, facet_value in series_list:
        try:
            if source == "fred":
                n = load_fred(series_id)
                print(f"[FRED] {series_id}: {n} new rows")

            elif source == "eia":
                n = load_eia(series_id, frequency, endpoint, facet_key, facet_value)
                print(f"[EIA ] {series_id}: {n} new rows")

        except Exception as e:
            print(f"[ERROR] {series_id}: {e}")

if __name__ == "__main__":
    main()
