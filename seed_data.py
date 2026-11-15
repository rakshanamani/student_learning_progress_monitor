"""
Realistic Sample Academic Data Seeder for Student Learning Progress Monitor.
Seeds students across multiple departments, subjects, and consecutive exams
to demonstrate analytics, weak subject identification, and progress tracking.
"""

from typing import Optional
from database import (
    init_db, add_student, add_subject, add_exam, save_or_update_mark,
    get_connection, DEFAULT_DB_PATH
)

SAMPLE_STUDENTS = [
    # Computer Science & Engineering (Semester 3)
    ("CS202401", "Aarav Sharma", "Computer Science", 3, "aarav.sharma@campus.edu", "+91 98765 43210"),
    ("CS202402", "Priya Patel", "Computer Science", 3, "priya.patel@campus.edu", "+91 98765 43211"),
    ("CS202403", "Rohan Verma", "Computer Science", 3, "rohan.verma@campus.edu", "+91 98765 43212"),
    ("CS202404", "Ananya Iyer", "Computer Science", 3, "ananya.iyer@campus.edu", "+91 98765 43213"),
    ("CS202405", "Vikram Singh", "Computer Science", 3, "vikram.singh@campus.edu", "+91 98765 43214"),
    ("CS202406", "Neha Gupta", "Computer Science", 3, "neha.gupta@campus.edu", "+91 98765 43215"),
    ("CS202407", "Kabir Mehta", "Computer Science", 3, "kabir.mehta@campus.edu", "+91 98765 43216"),
    ("CS202408", "Ishita Roy", "Computer Science", 3, "ishita.roy@campus.edu", "+91 98765 43217"),

    # Electronics & Communication (Semester 3)
    ("EC202401", "Siddharth Nair", "Electronics", 3, "siddharth.nair@campus.edu", "+91 98765 43220"),
    ("EC202402", "Tanvi Deshmukh", "Electronics", 3, "tanvi.deshmukh@campus.edu", "+91 98765 43221"),
    ("EC202403", "Aditya Joshi", "Electronics", 3, "aditya.joshi@campus.edu", "+91 98765 43222"),

    # Mechanical Engineering (Semester 3)
    ("ME202401", "Rahul Chawla", "Mechanical", 3, "rahul.chawla@campus.edu", "+91 98765 43230"),
    ("ME202402", "Sneha Kulkarni", "Mechanical", 3, "sneha.kulkarni@campus.edu", "+91 98765 43231"),
]

SAMPLE_SUBJECTS = [
    # Computer Science
    ("CS301", "Data Structures & Algorithms", "Computer Science", 3, 4),
    ("CS302", "Database Management Systems", "Computer Science", 3, 4),
    ("CS303", "Operating Systems", "Computer Science", 3, 3),
    ("CS304", "Computer Networks", "Computer Science", 3, 3),
    ("MA301", "Discrete Mathematics & Calculus", "Computer Science", 3, 4),

    # Electronics
    ("EC301", "Analog Electronic Circuits", "Electronics", 3, 4),
    ("EC302", "Digital Signal Processing", "Electronics", 3, 4),
    ("EC303", "Microprocessors & Microcontrollers", "Electronics", 3, 4),
    ("MA302", "Engineering Mathematics III", "Electronics", 3, 4),

    # Mechanical
    ("ME301", "Thermodynamics", "Mechanical", 3, 4),
    ("ME302", "Fluid Mechanics", "Mechanical", 3, 4),
    ("ME303", "Mechanics of Materials", "Mechanical", 3, 4),
    ("MA303", "Applied Engineering Mathematics", "Mechanical", 3, 4),
]

SAMPLE_EXAMS = [
    ("Midterm Examination 1", "2025-2026", 3, "2025-09-20"),
    ("Midterm Examination 2", "2025-2026", 3, "2025-11-15"),
    ("Semester End Examination", "2025-2026", 3, "2026-01-10"),
]

# Student performance profiles:
# (student_id, exam_index [0, 1, or 2], {subject_code: marks_obtained})
STUDENT_MARKS_BLUEPRINT = [
    # --- CS202401: Aarav Sharma (Consistently High Scorer) ---
    ("CS202401", 0, {"CS301": 92, "CS302": 88, "CS303": 85, "CS304": 89, "MA301": 95}),
    ("CS202401", 1, {"CS301": 94, "CS302": 90, "CS303": 88, "CS304": 91, "MA301": 96}),
    ("CS202401", 2, {"CS301": 96, "CS302": 93, "CS303": 90, "CS304": 94, "MA301": 98}),

    # --- CS202402: Priya Patel (Remarkable Improvement Journey: 58% -> 73% -> 85%) ---
    ("CS202402", 0, {"CS301": 55, "CS302": 62, "CS303": 58, "CS304": 52, "MA301": 64}),
    ("CS202402", 1, {"CS301": 70, "CS302": 76, "CS303": 72, "CS304": 68, "MA301": 80}),
    ("CS202402", 2, {"CS301": 84, "CS302": 88, "CS303": 85, "CS304": 81, "MA301": 90}),

    # --- CS202403: Rohan Verma (Weak in Math: <40% in Midterms, slight recovery) ---
    ("CS202403", 0, {"CS301": 68, "CS302": 72, "CS303": 65, "CS304": 70, "MA301": 32}), # Math Weak!
    ("CS202403", 1, {"CS301": 72, "CS302": 74, "CS303": 68, "CS304": 72, "MA301": 36}), # Math Weak!
    ("CS202403", 2, {"CS301": 75, "CS302": 78, "CS303": 72, "CS304": 76, "MA301": 46}), # Math recovered to pass

    # --- CS202404: Ananya Iyer (Solid steady performer: 75-78%) ---
    ("CS202404", 0, {"CS301": 74, "CS302": 78, "CS303": 76, "CS304": 72, "MA301": 79}),
    ("CS202404", 1, {"CS301": 76, "CS302": 77, "CS303": 79, "CS304": 75, "MA301": 81}),
    ("CS202404", 2, {"CS301": 78, "CS302": 80, "CS303": 82, "CS304": 77, "MA301": 84}),

    # --- CS202405: Vikram Singh (Declining Trajectory: 75% -> 58% -> 44% with multiple weak subjects in Final) ---
    ("CS202405", 0, {"CS301": 78, "CS302": 80, "CS303": 74, "CS304": 72, "MA301": 73}),
    ("CS202405", 1, {"CS301": 60, "CS302": 64, "CS303": 55, "CS304": 52, "MA301": 58}),
    ("CS202405", 2, {"CS301": 50, "CS302": 54, "CS303": 36, "CS304": 34, "MA301": 48}), # OS & Networks Weak!

    # --- CS202406: Neha Gupta (Good consistent student: 82-87%) ---
    ("CS202406", 0, {"CS301": 82, "CS302": 85, "CS303": 80, "CS304": 84, "MA301": 86}),
    ("CS202406", 1, {"CS301": 84, "CS302": 86, "CS303": 82, "CS304": 85, "MA301": 88}),
    ("CS202406", 2, {"CS301": 87, "CS302": 89, "CS303": 85, "CS304": 88, "MA301": 91}),

    # --- CS202407: Kabir Mehta (Critical in Programming/DSA: <40% across all exams) ---
    ("CS202407", 0, {"CS301": 28, "CS302": 52, "CS303": 54, "CS304": 50, "MA301": 48}), # DSA Weak!
    ("CS202407", 1, {"CS301": 34, "CS302": 55, "CS303": 58, "CS304": 52, "MA301": 52}), # DSA Weak!
    ("CS202407", 2, {"CS301": 38, "CS302": 58, "CS303": 60, "CS304": 55, "MA301": 56}), # DSA Weak!

    # --- CS202408: Ishita Roy (Great coder, struggled with Discrete Math) ---
    ("CS202408", 0, {"CS301": 88, "CS302": 84, "CS303": 82, "CS304": 80, "MA301": 38}), # Math Weak!
    ("CS202408", 1, {"CS301": 90, "CS302": 86, "CS303": 84, "CS304": 82, "MA301": 50}),
    ("CS202408", 2, {"CS301": 92, "CS302": 88, "CS303": 87, "CS304": 85, "MA301": 65}),

    # --- EC202401: Siddharth Nair (High Scorer ECE) ---
    ("EC202401", 0, {"EC301": 86, "EC302": 84, "EC303": 88, "MA302": 90}),
    ("EC202401", 1, {"EC301": 88, "EC302": 87, "EC303": 90, "MA302": 92}),
    ("EC202401", 2, {"EC301": 91, "EC302": 89, "EC303": 93, "MA302": 95}),

    # --- EC202402: Tanvi Deshmukh (Weak in Analog Circuits < 40%) ---
    ("EC202402", 0, {"EC301": 35, "EC302": 66, "EC303": 62, "MA302": 58}), # Analog Weak!
    ("EC202402", 1, {"EC301": 38, "EC302": 70, "EC303": 65, "MA302": 64}), # Analog Weak!
    ("EC202402", 2, {"EC301": 45, "EC302": 74, "EC303": 70, "MA302": 68}),

    # --- EC202403: Aditya Joshi (Consistent average) ---
    ("EC202403", 0, {"EC301": 65, "EC302": 68, "EC303": 70, "MA302": 66}),
    ("EC202403", 1, {"EC301": 68, "EC302": 71, "EC303": 72, "MA302": 70}),
    ("EC202403", 2, {"EC301": 72, "EC302": 75, "EC303": 76, "MA302": 74}),

    # --- ME202401: Rahul Chawla (Struggles with Thermodynamics < 40%) ---
    ("ME202401", 0, {"ME301": 33, "ME302": 58, "ME303": 62, "MA303": 54}), # Thermo Weak!
    ("ME202401", 1, {"ME301": 36, "ME302": 60, "ME303": 64, "MA303": 56}), # Thermo Weak!
    ("ME202401", 2, {"ME301": 42, "ME302": 65, "ME303": 68, "MA303": 60}),

    # --- ME202402: Sneha Kulkarni (Top Performer Mechanical) ---
    ("ME202402", 0, {"ME301": 88, "ME302": 89, "ME303": 91, "MA303": 92}),
    ("ME202402", 1, {"ME301": 90, "ME302": 92, "ME303": 93, "MA303": 95}),
    ("ME202402", 2, {"ME301": 94, "ME302": 95, "ME303": 96, "MA303": 97}),
]


def seed_database(db_path: Optional[str] = None, verbose: bool = False) -> dict:
    """Populates the database with initial realistic test data."""
    init_db(db_path)

    # 1. Add Students
    students_added = 0
    for sid, name, dept, sem, email, contact in SAMPLE_STUDENTS:
        ok, _ = add_student(sid, name, dept, sem, email, contact, db_path=db_path)
        if ok:
            students_added += 1

    # 2. Add Subjects
    subjects_added = 0
    for code, name, dept, sem, creds in SAMPLE_SUBJECTS:
        ok, _ = add_subject(code, name, dept, sem, creds, db_path=db_path)
        if ok:
            subjects_added += 1

    # 3. Add Exams
    exam_id_map = {}
    for idx, (ename, ayear, sem, edate) in enumerate(SAMPLE_EXAMS):
        ok, msg, eid = add_exam(ename, ayear, sem, edate, db_path=db_path)
        if ok and eid is not None:
            exam_id_map[idx] = eid
        else:
            # Look up existing exam id
            conn = get_connection(db_path)
            c = conn.cursor()
            c.execute("SELECT exam_id FROM exams WHERE exam_name=? AND academic_year=? AND semester=?", (ename, ayear, sem))
            row = c.fetchone()
            conn.close()
            if row:
                exam_id_map[idx] = row[0]

    # 4. Add Marks
    marks_recorded = 0
    for sid, exam_idx, sub_marks in STUDENT_MARKS_BLUEPRINT:
        eid = exam_id_map.get(exam_idx)
        if eid is None:
            continue
        for scode, mark_val in sub_marks.items():
            ok, _ = save_or_update_mark(sid, eid, scode, float(mark_val), 100.0, db_path=db_path)
            if ok:
                marks_recorded += 1

    if verbose:
        print(f"Seeding completed: {students_added} students, {subjects_added} subjects, {len(exam_id_map)} exams, {marks_recorded} marks.")

    return {
        "students": students_added,
        "subjects": subjects_added,
        "exams": len(exam_id_map),
        "marks": marks_recorded
    }


if __name__ == "__main__":
    seed_database(verbose=True)
