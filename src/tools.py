import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "business.db")

def _get_conn():
    return sqlite3.connect(DB_PATH)

def get_order_status(order_id: str) -> dict:
    conn = _get_conn()
    row = conn.execute("SELECT status, expected_delivery FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    if row:
        return {"found": True, "status": row[0], "expected_delivery": row[1]}
    return {"found": False}

def book_appointment(date: str, time: str) -> dict:
    conn = _get_conn()
    slot = conn.execute(
        "SELECT slot_id FROM appointments WHERE date = ? AND time = ? AND is_booked = 0",
        (date, time)
    ).fetchone()
    if slot:
        conn.execute("UPDATE appointments SET is_booked = 1 WHERE slot_id = ?", (slot[0],))
        conn.commit()
        conn.close()
        return {"success": True}
    conn.close()
    return {"success": False, "reason": "Slot not available or already booked"}
