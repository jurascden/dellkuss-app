import sqlite3
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "invoices.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE,
            invoice_date TEXT,
            customer_name TEXT,
            total REAL,
            payload TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_invoice(invoice_number, invoice_date, customer_name, total, payload):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO invoices (invoice_number, invoice_date, customer_name, total, payload, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(invoice_number) DO UPDATE SET
            invoice_date=excluded.invoice_date,
            customer_name=excluded.customer_name,
            total=excluded.total,
            payload=excluded.payload,
            updated_at=excluded.updated_at
    """, (
        invoice_number,
        invoice_date,
        customer_name,
        total,
        json.dumps(payload),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_invoices():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, invoice_number, invoice_date, customer_name, total, updated_at
        FROM invoices
        ORDER BY invoice_date DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_invoice_by_number(invoice_number):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT payload FROM invoices WHERE invoice_number = ?
    """, (invoice_number,))
    row = cur.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def delete_invoice(invoice_number):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM invoices WHERE invoice_number = ?",
        (invoice_number,)
    )
    conn.commit()
    conn.close()
