"""
Database Management Module for Student Learning Progress Monitor.
Handles SQLite database initialization, connection, migrations, and CRUD operations.
"""

import os
import sqlite3
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress_monitor.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates and returns a SQLite connection with row factory and foreign keys enabled."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the database schema if tables do not exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        semester INTEGER NOT NULL,
        email TEXT,
        contact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Subjects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_code TEXT PRIMARY KEY,
        subject_name TEXT NOT NULL,
        department TEXT NOT NULL,
        semester INTEGER NOT NULL,
        credits INTEGER DEFAULT 3
    );
    """)

    # Exams table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_name TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        semester INTEGER NOT NULL,
        exam_date TEXT,
        UNIQUE(exam_name, academic_year, semester)
    );
    """)

    # Marks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        exam_id INTEGER NOT NULL,
        subject_code TEXT NOT NULL,
        marks_obtained REAL NOT NULL,
        max_marks REAL NOT NULL DEFAULT 100.0,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
        FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE,
        UNIQUE(student_id, exam_id, subject_code)
    );
    """)

    # Performance indices for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_marks_student ON marks(student_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_marks_exam ON marks(exam_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_marks_subject ON marks(subject_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_dept_sem ON students(department, semester);")

    conn.commit()
    conn.close()


# ============================================================================
# STUDENT CRUD OPERATIONS
# ============================================================================

def add_student(student_id: str, name: str, department: str, semester: int, 
                email: str = "", contact: str = "", db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Adds a new student to the database."""
    student_id = student_id.strip().upper()
    name = name.strip()
    department = department.strip()
    email = email.strip()
    contact = contact.strip()

    if not student_id or not name or not department:
        return False, "Student ID, Name, and Department are required fields."
    
    if semester < 1 or semester > 8:
        return False, "Semester must be between 1 and 8."

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (student_id, name, department, semester, email, contact) VALUES (?, ?, ?, ?, ?, ?)",
            (student_id, name, department, semester, email, contact)
        )
        conn.commit()
        return True, f"Student '{name}' ({student_id}) added successfully."
    except sqlite3.IntegrityError:
        return False, f"Student with ID '{student_id}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def update_student(student_id: str, name: str, department: str, semester: int,
                   email: str = "", contact: str = "", db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Updates an existing student's record."""
    student_id = student_id.strip().upper()
    name = name.strip()
    department = department.strip()

    if not name or not department:
        return False, "Name and Department cannot be empty."

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE students 
            SET name = ?, department = ?, semester = ?, email = ?, contact = ?
            WHERE student_id = ?
            """,
            (name, department, semester, email.strip(), contact.strip(), student_id)
        )
        if cursor.rowcount == 0:
            return False, f"No student found with ID '{student_id}'."
        conn.commit()
        return True, f"Student '{student_id}' updated successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def delete_student(student_id: str, db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Deletes a student and their associated marks (via cascade)."""
    student_id = student_id.strip().upper()
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        if cursor.rowcount == 0:
            return False, f"Student '{student_id}' not found."
        conn.commit()
        return True, f"Student '{student_id}' and related records deleted successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def get_all_students(department: Optional[str] = None, semester: Optional[int] = None, 
                     db_path: Optional[str] = None) -> pd.DataFrame:
    """Fetches students matching optional filters as a pandas DataFrame."""
    conn = get_connection(db_path)
    query = "SELECT student_id, name, department, semester, email, contact, created_at FROM students WHERE 1=1"
    params: List[Any] = []

    if department and department != "All":
        query += " AND department = ?"
        params.append(department)
    if semester and semester != 0:
        query += " AND semester = ?"
        params.append(semester)

    query += " ORDER BY department, semester, student_id"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_student_by_id(student_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetches a single student's dictionary by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id.strip().upper(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============================================================================
# SUBJECT CRUD OPERATIONS
# ============================================================================

def add_subject(subject_code: str, subject_name: str, department: str, semester: int, 
                credits: int = 3, db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Adds a new subject."""
    code = subject_code.strip().upper()
    name = subject_name.strip()
    dept = department.strip()

    if not code or not name or not dept:
        return False, "Subject Code, Name, and Department are required."

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO subjects (subject_code, subject_name, department, semester, credits) VALUES (?, ?, ?, ?, ?)",
            (code, name, dept, semester, credits)
        )
        conn.commit()
        return True, f"Subject '{name}' ({code}) added successfully."
    except sqlite3.IntegrityError:
        return False, f"Subject code '{code}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def get_all_subjects(department: Optional[str] = None, semester: Optional[int] = None, 
                     db_path: Optional[str] = None) -> pd.DataFrame:
    """Fetches subjects as a pandas DataFrame."""
    conn = get_connection(db_path)
    query = "SELECT subject_code, subject_name, department, semester, credits FROM subjects WHERE 1=1"
    params: List[Any] = []

    if department and department != "All":
        query += " AND department = ?"
        params.append(department)
    if semester and semester != 0:
        query += " AND semester = ?"
        params.append(semester)

    query += " ORDER BY department, semester, subject_code"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def delete_subject(subject_code: str, db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Deletes a subject by code."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM subjects WHERE subject_code = ?", (subject_code.strip().upper(),))
        if cursor.rowcount == 0:
            return False, f"Subject '{subject_code}' not found."
        conn.commit()
        return True, f"Subject '{subject_code}' deleted successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


# ============================================================================
# EXAM CRUD OPERATIONS
# ============================================================================

def add_exam(exam_name: str, academic_year: str, semester: int, 
             exam_date: Optional[str] = None, db_path: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
    """Adds a new examination cycle."""
    exam_name = exam_name.strip()
    academic_year = academic_year.strip()

    if not exam_name or not academic_year:
        return False, "Exam Name and Academic Year are required.", None

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO exams (exam_name, academic_year, semester, exam_date) VALUES (?, ?, ?, ?)",
            (exam_name, academic_year, semester, exam_date)
        )
        exam_id = cursor.lastrowid
        conn.commit()
        return True, f"Exam '{exam_name} ({academic_year})' created.", exam_id
    except sqlite3.IntegrityError:
        return False, f"Exam '{exam_name}' for year '{academic_year}' & semester {semester} already exists.", None
    except Exception as e:
        return False, f"Database error: {str(e)}", None
    finally:
        conn.close()


def get_all_exams(db_path: Optional[str] = None) -> pd.DataFrame:
    """Fetches all exams as a pandas DataFrame."""
    conn = get_connection(db_path)
    df = pd.read_sql_query(
        "SELECT exam_id, exam_name, academic_year, semester, exam_date FROM exams ORDER BY academic_year DESC, semester ASC, exam_id ASC",
        conn
    )
    conn.close()
    return df


def delete_exam(exam_id: int, db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Deletes an exam and all related marks."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM exams WHERE exam_id = ?", (exam_id,))
        if cursor.rowcount == 0:
            return False, f"Exam ID {exam_id} not found."
        conn.commit()
        return True, f"Exam ID {exam_id} and related marks deleted.", None
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


# ============================================================================
# MARKS OPERATIONS
# ============================================================================

def save_or_update_mark(student_id: str, exam_id: int, subject_code: str, 
                        marks_obtained: float, max_marks: float = 100.0, 
                        db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Inserts or updates a student's mark for a specific exam and subject."""
    student_id = student_id.strip().upper()
    subject_code = subject_code.strip().upper()

    if marks_obtained < 0 or marks_obtained > max_marks:
        return False, f"Marks obtained ({marks_obtained}) must be between 0 and {max_marks}."

    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO marks (student_id, exam_id, subject_code, marks_obtained, max_marks)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, exam_id, subject_code) 
            DO UPDATE SET 
                marks_obtained = excluded.marks_obtained,
                max_marks = excluded.max_marks,
                recorded_at = CURRENT_TIMESTAMP
        """, (student_id, exam_id, subject_code, marks_obtained, max_marks))
        conn.commit()
        return True, f"Mark recorded for {student_id} in {subject_code}."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def save_marks_batch(records: List[Dict[str, Any]], db_path: Optional[str] = None) -> Tuple[bool, str, int]:
    """
    Saves a batch of mark records.
    Each record must have: student_id, exam_id, subject_code, marks_obtained, max_marks (default 100)
    """
    if not records:
        return False, "No records provided.", 0

    conn = get_connection(db_path)
    cursor = conn.cursor()
    saved_count = 0
    try:
        for rec in records:
            cursor.execute("""
                INSERT INTO marks (student_id, exam_id, subject_code, marks_obtained, max_marks)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(student_id, exam_id, subject_code)
                DO UPDATE SET
                    marks_obtained = excluded.marks_obtained,
                    max_marks = excluded.max_marks,
                    recorded_at = CURRENT_TIMESTAMP
            """, (
                rec["student_id"].strip().upper(),
                int(rec["exam_id"]),
                rec["subject_code"].strip().upper(),
                float(rec["marks_obtained"]),
                float(rec.get("max_marks", 100.0))
            ))
            saved_count += 1
        conn.commit()
        return True, f"Successfully saved {saved_count} mark records.", saved_count
    except Exception as e:
        conn.rollback()
        return False, f"Batch save failed: {str(e)}", 0
    finally:
        conn.close()


def delete_mark(mark_id: int, db_path: Optional[str] = None) -> Tuple[bool, str]:
    """Deletes a specific mark record."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM marks WHERE mark_id = ?", (mark_id,))
        if cursor.rowcount == 0:
            return False, f"Mark record {mark_id} not found."
        conn.commit()
        return True, "Mark record deleted successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


# ============================================================================
# COMPREHENSIVE QUERY & REPORTING HELPERS
# ============================================================================

def get_all_marks_joined_df(department: Optional[str] = None, semester: Optional[int] = None, 
                            exam_id: Optional[int] = None, db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Returns an enriched DataFrame joining marks, students, exams, and subjects with computed percentages.
    """
    conn = get_connection(db_path)
    query = """
    SELECT 
        m.mark_id,
        s.student_id,
        s.name AS student_name,
        s.department,
        s.semester AS student_semester,
        s.email,
        e.exam_id,
        e.exam_name,
        e.academic_year,
        sub.subject_code,
        sub.subject_name,
        sub.credits,
        m.marks_obtained,
        m.max_marks,
        ROUND((m.marks_obtained / m.max_marks) * 100, 2) AS percentage,
        m.recorded_at
    FROM marks m
    JOIN students s ON m.student_id = s.student_id
    JOIN exams e ON m.exam_id = e.exam_id
    JOIN subjects sub ON m.subject_code = sub.subject_code
    WHERE 1=1
    """
    params: List[Any] = []

    if department and department != "All":
        query += " AND s.department = ?"
        params.append(department)
    if semester and semester != 0:
        query += " AND s.semester = ?"
        params.append(semester)
    if exam_id and exam_id != 0:
        query += " AND e.exam_id = ?"
        params.append(exam_id)

    query += " ORDER BY s.student_id, e.exam_id, sub.subject_code"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_db_stats(db_path: Optional[str] = None) -> Dict[str, int]:
    """Returns total counts for dashboard cards."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students;")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM subjects;")
    total_subjects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM exams;")
    total_exams = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM marks;")
    total_marks = cursor.fetchone()[0]

    conn.close()
    return {
        "students": total_students,
        "subjects": total_subjects,
        "exams": total_exams,
        "marks_records": total_marks
    }


def reset_database(db_path: Optional[str] = None) -> None:
    """Drops all tables and re-initializes an empty database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS marks;")
    cursor.execute("DROP TABLE IF EXISTS exams;")
    cursor.execute("DROP TABLE IF EXISTS subjects;")
    cursor.execute("DROP TABLE IF EXISTS students;")
    conn.commit()
    conn.close()
    init_db(db_path)
