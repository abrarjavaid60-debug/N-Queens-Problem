"""SQLite persistence for Smart Campus complaints."""
from pathlib import Path
import sqlite3
import uuid
from datetime import datetime
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "smart_campus.db"
CATEGORIES = ["Wi-Fi / Internet", "Classroom Equipment", "Water Supply", "Cleanliness", "Electricity", "Washroom", "Other"]
PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["Pending", "In Progress", "Resolved"]


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                priority TEXT NOT NULL CHECK(priority IN ('Low','Medium','High','Urgent')),
                status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','In Progress','Resolved')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()


def create_complaint(title, description, category, location, priority):
    title = str(title).strip()
    description = str(description).strip()
    category = str(category).strip()
    location = str(location).strip()
    priority = str(priority).strip()
    if not title or not description or not category or not location:
        raise ValueError("All fields are required.")
    if len(title) > 120:
        raise ValueError("Title must be 120 characters or fewer.")
    if len(description) > 3000:
        raise ValueError("Description must be 3000 characters or fewer.")
    if category not in CATEGORIES or priority not in PRIORITIES:
        raise ValueError("Please choose a valid category and priority.")
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    complaint_id = f"SC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    with get_connection() as conn:
        conn.execute("""INSERT INTO complaints
            (complaint_id,title,description,category,location,priority,status,created_at,updated_at)
            VALUES (?,?,?,?,?,?,'Pending',?,?)""",
            (complaint_id, title, description, category, location, priority, now, now))
        conn.commit()
    return complaint_id


def get_complaint(complaint_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM complaints WHERE complaint_id = ?", (str(complaint_id).strip().upper(),)).fetchone()
    return dict(row) if row else None


def get_all_complaints():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT complaint_id, title, description, category, location, priority, status, created_at, updated_at FROM complaints ORDER BY id DESC", conn)
    return df


def update_status(complaint_id, status):
    if status not in STATUSES:
        raise ValueError("Invalid complaint status.")
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute("UPDATE complaints SET status=?, updated_at=? WHERE complaint_id=?", (status, now, complaint_id))
        conn.commit()
        return cur.rowcount > 0


def add_sample_data():
    samples = [
        ("Wi-Fi not working", "Internet is unavailable in the study area.", "Wi-Fi / Internet", "Library, first floor", "High"),
        ("Projector not starting", "The projector does not turn on during lectures.", "Classroom Equipment", "Block A, Room 204", "Medium"),
        ("Water tap leaking", "A tap is leaking near the drinking-water area.", "Water Supply", "Block B, ground floor", "Low"),
        ("Classroom needs cleaning", "The classroom floor needs attention.", "Cleanliness", "Block C, Room 101", "Medium"),
    ]
    added = []
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        if count:
            return 0
    for item in samples:
        added.append(create_complaint(*item))
    return len(added)
