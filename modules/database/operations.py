import sqlite3
import os
from datetime import datetime

DB_FILE = "data/users.db"
os.makedirs("data", exist_ok=True)

def _get_conn():
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_user(name):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (name, created_at) VALUES (?, ?)", (name, datetime.utcnow().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        # ya existe
        pass
    conn.close()

def list_users():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at FROM users ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def user_exists(name):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return row is not None
