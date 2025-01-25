import sqlite3
import os

DB_FILENAME = "science_tutor.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS user_progress (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    current_course TEXT,
    achievements TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS quiz_history (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    quiz_name TEXT,
    score INTEGER,
    date_taken TEXT
);

CREATE TABLE IF NOT EXISTS lessons (
    lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT,
    lesson_title TEXT,
    content TEXT
);
"""

def init_db():
    """Initialize SQLite database, create tables if they don't exist."""
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)
    conn.commit()
    conn.close()

def get_connection():
    """Utility function to get a new DB connection."""
    return sqlite3.connect(DB_FILENAME)

def create_or_get_user(username):
    """Create a new user record if not existing, else return the user data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT user_id, username, current_course, achievements FROM user_progress WHERE username=?", (username,))
    row = cursor.fetchone()
    
    if row:
        conn.close()
        return row  # (user_id, username, current_course, achievements)
    else:
        cursor.execute("INSERT INTO user_progress (username) VALUES (?)", (username,))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT user_id, username, current_course, achievements FROM user_progress WHERE user_id=?", (new_id,))
        row = cursor.fetchone()
        conn.close()
        return row

def update_user_course(user_id, course_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_progress SET current_course=? WHERE user_id=?", (course_name, user_id))
    conn.commit()
    conn.close()

def record_quiz_score(user_id, quiz_name, score):
    import datetime
    conn = get_connection()
    cursor = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO quiz_history (user_id, quiz_name, score, date_taken) VALUES (?,?,?,?)",
                   (user_id, quiz_name, score, date_str))
    conn.commit()
    conn.close()

def get_user_achievements(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT achievements FROM user_progress WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return row[0].split(",")
    return []

def add_user_achievement(user_id, achievement):
    """Add a new achievement to the user record if not already earned."""
    achievements = get_user_achievements(user_id)
    if achievement not in achievements:
        achievements.append(achievement)
        new_str = ",".join(achievements)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user_progress SET achievements=? WHERE user_id=?", (new_str, user_id))
        conn.commit()
        conn.close()

def load_demo_data():
    """Load sample data into the lessons table for demonstration."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM lessons")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_lessons = [
            ("Physics", "Introduction to Physics", "Physics is the study of matter, energy, and the interaction between them."),
            ("Chemistry", "Atomic Structure", "Atomic structure refers to the arrangement of protons, neutrons, and electrons in an atom."),
            ("Biology", "Cell Structure", "Cells are the basic units of life, and all organisms are composed of one or more cells.")
        ]
        for course, title, content in sample_lessons:
            cursor.execute("INSERT INTO lessons (course_name, lesson_title, content) VALUES (?, ?, ?)",
                           (course, title, content))
    conn.commit()
    conn.close()
