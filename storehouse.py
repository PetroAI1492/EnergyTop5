# storehouse.py
import sqlite3
from datetime import datetime

DB_PATH = r"c:\Thor\storehouse.db"

def db():
    return sqlite3.connect(DB_PATH)

def latest_two(series_id):
    with db() as conn:
        rows = conn.execute("""
            SELECT period, value
            FROM observations
            WHERE series_id = ?
            ORDER BY period DESC
            LIMIT 2
        """, (series_id,)).fetchall()
    return rows if rows else None

def daily_change(series_id):
    rows = latest_two(series_id)
    if not rows:
        return None

    if len(rows) == 1:
        (p1, v1) = rows[0]
        return {
            "period": p1,
            "value": v1,
            "delta": 0.0,
            "pct": 0.0,
            "fresh": True,
        }

    (p1, v1), (p2, v2) = rows
    delta = v1 - v2
    pct = (delta / v2) * 100 if v2 not in (0, None) else 0.0

    try:
        dt = datetime.fromisoformat(p1)
        fresh = (datetime.utcnow() - dt).days <= 7
    except Exception:
        fresh = False

    return {
        "period": p1,
        "value": v1,
        "delta": delta,
        "pct": pct,
        "fresh": fresh,
    }

def latest_value(series_id):
    rows = latest_two(series_id)
    if not rows:
        return None

    (p1, v1) = rows[0]

    try:
        dt = datetime.fromisoformat(p1)
        fresh = (datetime.utcnow() - dt).days <= 7
    except Exception:
        fresh = False

    return {
        "period": p1,
        "value": v1,
        "fresh": fresh,
    }
