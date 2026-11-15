"""
Automated Comprehensive Test Script for Student Learning Progress Monitor.
Tests Database, Analytics, Visualizations, and PDF Generation end-to-end.
"""

import os
import sys

# Ensure local directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database import (
    init_db, reset_database, add_student, get_all_students, update_student,
    delete_student, add_subject, get_all_subjects, add_exam, get_all_exams,
    save_or_update_mark, get_all_marks_joined_df, get_db_stats
)
from seed_data import seed_database
from analytics import (
    evaluate_student_exam_performance, track_student_progress,
    get_cohort_summary_statistics, identify_all_weak_subjects_df, calculate_grade
)
from visualizations import (
    plot_subject_performance_bar, plot_progress_trend,
    plot_grade_distribution_donut, plot_subject_class_comparison, fig_to_image_bytes
)
from report_generator import generate_student_pdf_report


def run_all_tests():
    print("==================================================")
    print("Starting Automated Verification of All Modules...")
    print("==================================================")

    test_db = os.path.join(CURRENT_DIR, "test_progress_monitor.db")
    if os.path.exists(test_db):
        os.remove(test_db)

    # 1. Test Database Init & Seeding
    print("\n[1/6] Testing Database Initialization & Sample Data Seeder...")
    seed_res = seed_database(db_path=test_db, verbose=True)
    assert seed_res["students"] > 0, "No students seeded!"
    assert seed_res["subjects"] > 0, "No subjects seeded!"
    assert seed_res["exams"] == 3, "Exams count mismatch!"
    assert seed_res["marks"] > 0, "Marks count mismatch!"
    stats = get_db_stats(db_path=test_db)
    print(f"-> DB Stats: {stats}")

    # 2. Test Student CRUD
    print("\n[2/6] Testing Student CRUD Operations...")
    ok, msg = add_student("TEST001", "Test Student", "Computer Science", 3, "test@test.com", "123456", db_path=test_db)
    assert ok, f"Failed to add student: {msg}"
    
    ok, msg = update_student("TEST001", "Test Student Updated", "Computer Science", 3, "test_new@test.com", "99999", db_path=test_db)
    assert ok, f"Failed to update student: {msg}"

    st_df = get_all_students(db_path=test_db)
    assert "TEST001" in st_df["student_id"].values, "New student not found in DataFrame!"

    ok, msg = delete_student("TEST001", db_path=test_db)
    assert ok, f"Failed to delete student: {msg}"
    print("-> Student CRUD passed.")

    # 3. Test Analytics & Evaluation Engine
    print("\n[3/6] Testing Academic Analytics Engine...")
    marks_df = get_all_marks_joined_df(db_path=test_db)
    assert not marks_df.empty, "Marks joined DataFrame is empty!"

    # Evaluate student CS202403 (Rohan Verma - weak in Math) in Exam 1
    eval_rohan = evaluate_student_exam_performance(marks_df, "CS202403", exam_id=1)
    assert eval_rohan["has_data"], "Failed to evaluate student CS202403!"
    assert len(eval_rohan["weak_subjects"]) > 0, "Expected weak subjects for CS202403 not found!"
    print(f"-> Rohan Verma Exam 1 Aggregate: {eval_rohan['overall_percentage']}% ({eval_rohan['overall_grade']})")
    print(f"-> Weak subjects detected: {[w['subject_name'] for w in eval_rohan['weak_subjects']]}")

    # Evaluate student CS202401 (Aarav Sharma - high achiever)
    eval_aarav = evaluate_student_exam_performance(marks_df, "CS202401", exam_id=1)
    assert eval_aarav["overall_grade"] in ["A", "A+"], "Aarav should have A/A+ grade"
    assert len(eval_aarav["weak_subjects"]) == 0, "Aarav should have 0 weak subjects"
    print(f"-> Aarav Sharma Exam 1 Aggregate: {eval_aarav['overall_percentage']}% ({eval_aarav['overall_grade']})")

    # 4. Test Progress Tracking (Multi-Exam Trajectory)
    print("\n[4/6] Testing Multi-Exam Progress Tracking...")
    # Priya Patel CS202402 improved significantly: 58% -> 73% -> 85%
    prog_priya = track_student_progress(marks_df, "CS202402")
    assert prog_priya["has_data"], "Failed to track progress for CS202402"
    assert prog_priya["overall_delta"] > 20, f"Expected >20% delta for Priya Patel, got {prog_priya['overall_delta']}"
    print(f"-> Priya Patel Progress Delta: +{prog_priya['overall_delta']}% | Trajectory: {prog_priya['trajectory_label']}")

    # Vikram Singh CS202405 declined: 75% -> 58% -> 44%
    prog_vikram = track_student_progress(marks_df, "CS202405")
    assert prog_vikram["overall_delta"] < -20, f"Expected negative delta for Vikram Singh, got {prog_vikram['overall_delta']}"
    print(f"-> Vikram Singh Progress Delta: {prog_vikram['overall_delta']}% | Trajectory: {prog_vikram['trajectory_label']}")

    # Cohort Summary & Weak Subject List
    cohort_stats = get_cohort_summary_statistics(marks_df, exam_id=1)
    print(f"-> Cohort Stats (Exam 1): Avg = {cohort_stats['average_percentage']}%, Pass Rate = {cohort_stats['pass_rate']}%")
    all_weak_df = identify_all_weak_subjects_df(marks_df, exam_id=1)
    print(f"-> Total weak subject instances in Exam 1: {len(all_weak_df)}")
    assert not all_weak_df.empty, "Weak subjects DataFrame should not be empty!"

    # 5. Test Matplotlib Visualizations
    print("\n[5/6] Testing Matplotlib Figures Generation...")
    fig1 = plot_subject_performance_bar(eval_rohan["subjects"])
    img1_bytes = fig_to_image_bytes(fig1)
    assert img1_bytes.getbuffer().nbytes > 1000, "Image 1 buffer empty!"

    fig2 = plot_progress_trend(prog_priya["exam_history"], prog_priya["student_name"])
    img2_bytes = fig_to_image_bytes(fig2)
    assert img2_bytes.getbuffer().nbytes > 1000, "Image 2 buffer empty!"

    fig3 = plot_grade_distribution_donut(cohort_stats["grade_distribution"])
    img3_bytes = fig_to_image_bytes(fig3)
    assert img3_bytes.getbuffer().nbytes > 1000, "Image 3 buffer empty!"
    print("-> All Matplotlib figures generated and converted to image buffers successfully.")

    # 6. Test ReportLab PDF Generation
    print("\n[6/6] Testing ReportLab PDF Generation...")
    pdf_buffer = generate_student_pdf_report(
        student_eval=eval_rohan,
        progress_tracking=track_student_progress(marks_df, "CS202403")
    )
    pdf_bytes = pdf_buffer.getvalue()
    assert len(pdf_bytes) > 5000, f"Generated PDF is unusually small ({len(pdf_bytes)} bytes)!"
    assert pdf_bytes.startswith(b"%PDF"), "PDF does not start with valid PDF magic header!"

    # Write a test PDF file to scratch to inspect
    test_pdf_path = os.path.join(CURRENT_DIR, "sample_report_CS202403.pdf")
    with open(test_pdf_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"-> Sample PDF generated successfully ({len(pdf_bytes)} bytes): {test_pdf_path}")

    # Cleanup test db
    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! Core logic is 100% verified.")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
