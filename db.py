import sqlite3

DB_PATH = "health_assistant.db"


def init_db():
    """Creates the tables if they don't exist yet. Safe to call every run."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            allergies TEXT,
            conditions TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_profile(name, age, allergies, conditions):
    """
    MVP simplification: this is a single-user app for the hackathon demo,
    so we just keep ONE row and overwrite it every time the form is saved.
    (No login system needed — good enough for a 36hr build.)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users")  # clear old profile
    c.execute(
        "INSERT INTO users (name, age, allergies, conditions) VALUES (?, ?, ?, ?)",
        (name, age, allergies, conditions),
    )
    conn.commit()
    conn.close()


def get_profile():
    """Returns the profile as a dict, or None if nothing saved yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    row = c.execute("SELECT * FROM users LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None
import sqlite3
import hashlib
import os
 
DB_PATH = "health_assistant.db"
 
 
# ---------- Add this block inside init_db(), alongside your existing tables ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
 
    # ... your existing CREATE TABLE statements for users / medicines / etc stay here ...
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)
 
    conn.commit()
    conn.close()
 
 
# ---------- New functions — add these anywhere in db.py ----------
 
def _hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()
 
 
def create_account(username, password):
    """Registers a new account. Returns True on success, False if username taken."""
    salt = os.urandom(16).hex()
    password_hash = _hash_password(password, salt)
 
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO accounts (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # username already exists
    finally:
        conn.close()
 
 
def verify_login(username, password):
    """Returns True if username + password match a stored account."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    row = c.execute(
        "SELECT password_hash, salt FROM accounts WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
 
    if row is None:
        return False
 
    stored_hash, salt = row
    return _hash_password(password, salt) == stored_hash
 
 
def has_any_account():
    """Used to decide whether to show 'Create account' or 'Log in' first."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    row = c.execute("SELECT COUNT(*) FROM accounts").fetchone()
    conn.close()
    return row[0] > 0
 