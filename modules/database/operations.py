import sqlite3
import os
from datetime import datetime
from modules.utils.file_io import ensure_user_folder

DB_FILE = "data/users.db"
os.makedirs("data", exist_ok=True)

def _get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_at TEXT,
        photos_count INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def add_user(name):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        # Verificar si el usuario ya existe
        cur.execute("SELECT id FROM users WHERE name = ?", (name,))
        exists = cur.fetchone()
        
        if exists:
            # Usuario existe, no hacer nada
            conn.close()
            return False
            
        # Insertar nuevo usuario
        cur.execute(
            "INSERT INTO users (name, created_at, photos_count) VALUES (?, ?, ?)", 
            (name, datetime.utcnow().isoformat(), 0)
        )
        conn.commit()
        return True
    except Exception as e:
        Logger.error(f"Error al agregar usuario {name}: {e}")
        return False
    finally:
        conn.close()

def update_photo_count(user_name):
    """Actualiza el contador de fotos para un usuario existente"""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE users SET photos_count = photos_count + 1 WHERE name = ?",
            (user_name,)
        )
        conn.commit()
    except Exception as e:
        Logger.error(f"Error al actualizar contador de {user_name}: {e}")
    finally:
        conn.close()
def list_users():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at, photos_count FROM users ORDER BY name")
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

def increment_photo_count(user_name):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE users SET photos_count = photos_count + 1 WHERE name = ?",
            (user_name,)
        )
        conn.commit()
    except Exception as e:
        print(f"Error al actualizar contador de fotos: {e}")
    finally:
        conn.close()