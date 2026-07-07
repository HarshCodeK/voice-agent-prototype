import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "business.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS orders")
c.execute("""
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        customer_name TEXT,
        status TEXT,
        expected_delivery TEXT
    )
""")

orders = [
    ("ORD-1001", "Alice Johnson", "Shipped", "2026-07-10"),
    ("ORD-1002", "Bob Smith", "Processing", "2026-07-14"),
    ("ORD-1003", "Carol Davis", "Delivered", "2026-07-05"),
    ("ORD-1004", "David Lee", "Delayed", "2026-07-12"),
    ("ORD-1005", "Eva Martinez", "Shipped", "2026-07-09"),
]
c.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)

c.execute("DROP TABLE IF EXISTS appointments")
c.execute("""
    CREATE TABLE appointments (
        slot_id INTEGER PRIMARY KEY,
        date TEXT,
        time TEXT,
        is_booked INTEGER DEFAULT 0
    )
""")

slots = [
    ("2026-07-15", "09:00"),
    ("2026-07-15", "10:00"),
    ("2026-07-15", "11:00"),
    ("2026-07-16", "09:00"),
    ("2026-07-16", "10:00"),
    ("2026-07-16", "11:00"),
]
c.executemany("INSERT INTO appointments (date, time) VALUES (?, ?)", slots)

conn.commit()
conn.close()

print(f"Database created at {DB_PATH}")
print("Orders:", len(orders), "rows inserted")
print("Appointments:", len(slots), "rows inserted")
