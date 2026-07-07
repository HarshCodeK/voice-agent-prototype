import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agent_logs.db")

def _get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            transcript TEXT,
            intent TEXT,
            response TEXT,
            latency_ms REAL
        )
    """)
    conn.commit()
    conn.close()

def log_interaction(transcript: str, intent: str, response: str, latency_ms: float):
    init_db()
    conn = _get_conn()
    conn.execute(
        "INSERT INTO logs (timestamp, transcript, intent, response, latency_ms) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), transcript, intent, response, latency_ms)
    )
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 20) -> list[dict]:
    init_db()
    conn = _get_conn()
    rows = conn.execute(
        "SELECT timestamp, transcript, intent, response, latency_ms FROM logs ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "transcript": r[1], "intent": r[2], "response": r[3], "latency_ms": r[4]}
        for r in rows
    ]
