#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fred_reconcile.py

Sentinel — FRED Reconciliation (Read-Only)

Purpose:
- Verify storehouse completeness vs FRED API
- Detect missing or trailing observations
- NO writes, NO updates, NO inserts
- Safe to run daily or on-demand

Control Plane:
- series_new (source='fred', active=1)

Assumptions:
- observations table exists
- observations keyed by (series_id, period)
"""

import sqlite3
import requests
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

DB_PATH = Path(r"c:\Thor\storehouse.db")
FRED_KEY_PATH = Path(r"c:\mygit\secrets\fred.key")
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

REQUEST_TIMEOUT = 30

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def load_fred_key():
    return FRED_KEY_PATH.read_text(encoding="utf-8").strip()

def db():
    return sqlite3.connect(DB_PATH, timeout=30)

# ---------------------------------------------------------------------
# Control Plane
# ---------------------------------------------------------------------

def fred_series():
    with db() as conn:
        return conn.execute("""
            SELECT series_id
            FROM series_new
            WHERE source = 'fred'
              AND active = 1
            ORDER BY series_id
        """).fetchall()

# ---------------------------------------------------------------------
# Storehouse Queries
# ---------------------------------------------------------------------

def storehouse_periods(series_id):
    with db() as conn:
        row = conn.execute("""
            SELECT COUNT(*), MIN(period), MAX(period)
            FROM observations
            WHERE series_id = ?
        """, (series_id,)).fetchone()
        return row

# ---------------------------------------------------------------------
# FRED API
# ---------------------------------------------------------------------

def fred_periods(series_id, api_key):
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
    }

    r = requests.get(
        FRED_BASE_URL,
        params=params,
        timeout=REQUEST_TIMEOUT
    )
    r.raise_for_status()

    data = r.json().get("observations", [])
    if not data:
        return 0, None, None

    periods = [o["date"] for o in data if o.get("value") not in (".", None)]
    return len(periods), min(periods), max(periods)

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("=== FRED RECONCILIATION REPORT ===")
    print(f"Timestamp: {utc_now()}")
    print(f"Database : {DB_PATH}")
    print()

    api_key = load_fred_key()
    series_list = [s[0] for s in fred_series()]

    for series_id in series_list:
        try:
            fred_count, fred_min, fred_max = fred_periods(series_id, api_key)
            db_count, db_min, db_max = storehouse_periods(series_id)

            if fred_count == db_count:
                print(f"[OK] {series_id}")
            else:
                print(f"[WARN] {series_id}")

            print(f"  FRED periods      : {fred_count}")
            print(f"  Storehouse periods: {db_count}")
            print(f"  FRED range        : {fred_min} → {fred_max}")
            print(f"  Storehouse range  : {db_min} → {db_max}")
            print()

        except Exception as e:
            print(f"[ERROR] {series_id}: {e}")
            print()

if __name__ == "__main__":
    main()
