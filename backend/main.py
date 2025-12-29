from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path - one level up from backend folder
DB = Path(__file__).parent.parent / "neurosentry.db"

def get_db():
    return sqlite3.connect(str(DB))


@app.get("/")
def root():
    return {"status": "NeuroSentry API is running", "database": str(DB)}


@app.get("/stats")
def get_stats():
    """Get overall statistics from entire database"""
    conn = get_db()
    cur = conn.cursor()

    # Total scans
    cur.execute("SELECT COUNT(*) FROM scan_history")
    total = cur.fetchone()[0]

    # Total threats
    cur.execute("SELECT COUNT(*) FROM scan_history WHERE is_threat = 1")
    threats = cur.fetchone()[0]

    conn.close()

    percent = (threats / total * 100) if total > 0 else 0

    return {
        "total": total,
        "threats": threats,
        "percent": round(percent, 1)
    }


@app.get("/logs")
def get_logs():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT scan_timestamp, is_threat, confidence, explanation
        FROM scan_history
        ORDER BY scan_timestamp DESC
        LIMIT 100
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "timestamp": r[0],
            "is_threat": bool(r[1]),
            "confidence": float(r[2]),
            "ai_explanation": r[3] if r[3] else "No explanation available"
        }
        for r in rows
    ]
