import sqlite3
from db import get_connection

def get_lessons_for_course(course_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lesson_id, lesson_title, content FROM lessons WHERE course_name=?", (course_name,))
    lessons = cursor.fetchall()
    conn.close()
    # Each row -> (lesson_id, lesson_title, content)
    return lessons

def get_lesson_by_id(lesson_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lesson_id, course_name, lesson_title, content FROM lessons WHERE lesson_id=?", (lesson_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def load_demo_data():
    """
    Insert some sample lessons/courses if not already present.
    For demonstration only; remove or adapt as needed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Example: Insert a sample course "Physics 101" if no lessons exist
    cursor.execute("SELECT COUNT(*) FROM lessons")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_lessons = [
            ("Physics 101", "Introduction to Physics", "Physics is the study of matter, energy, and the interactions..."),
            ("Physics 101", "Newton's Laws of Motion", "Newton's First Law states that an object..."),
            ("Chemistry 101", "Atomic Structure", "All matter is composed of atoms...")
        ]
        for (course, title, content) in sample_lessons:
            cursor.execute("INSERT INTO lessons (course_name, lesson_title, content) VALUES (?,?,?)",
                           (course, title, content))
    conn.commit()
    conn.close()
