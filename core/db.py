# core/db.py
import sqlite3
from pathlib import Path
import json
from typing import Optional, Dict, Any

DB_PATH = Path(__file__).resolve().parent.parent / "neurosentry.db"

def get_db_connection():
    """
    Returns a SQLite connection to neurosentry.db
    """
    return sqlite3.connect(
        str(DB_PATH),
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_threat INTEGER NOT NULL,
            confidence REAL,
            explanation TEXT,
            findings_json TEXT
        )
        """)
        conn.commit()

def insert_scan_result(is_threat, confidence, explanation, findings):
    import sqlite3
    from datetime import datetime

    conn = sqlite3.connect("neurosentry.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO scan_history 
        (scan_timestamp, is_threat, confidence, explanation, findings_json)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        int(is_threat),
        float(confidence),
        explanation,
        json.dumps(findings)
    ))

    conn.commit()
    conn.close()

