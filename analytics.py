"""
Academic Performance Analytics Module.
Calculates student grades, percentages, weak subject diagnostics, progress tracking deltas,
and cohort/batch level statistical summaries.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np


# ============================================================================
# GRADING SYSTEM CONSTANTS & HELPERS
# ============================================================================

GRADE_SCALE = [
    (90.0, "A+", 10, "Outstanding", "#10B981"),       # Green
    (80.0, "A",   9, "Excellent",   "#34D399"),       # Mint
    (70.0, "B",   8, "Very Good",   "#3B82F6"),       # Blue
    (60.0, "C",   7, "Good",        "#6366F1"),       # Indigo
    (50.0, "D",   6, "Satisfactory","#F59E0B"),       # Amber
    (40.0, "E",   5, "Pass",        "#FB923C"),       # Orange
    (0.0,  "F",   0, "Fail / Weak", "#EF4444"),       # Red
]

WEAK_SUBJECT_THRESHOLD = 40.0
STRONG_SUBJECT_THRESHOLD = 75.0


def calculate_grade(percentage: float) -> Tuple[str, int, str, str]:
    """
    Returns (grade, grade_point, description, hex_color) for a given percentage.
    """
    try:
        pct = float(percentage)
    except (ValueError, TypeError):
        return "N/A", 0, "No Grade", "#9CA3AF"

    for min_score, grade, point, desc, color in GRADE_SCALE:
        if pct >= min_score:
            return grade, point, desc, color
    return "F", 0, "Fail / Weak", "#EF4444"


def get_subject_recommendation(subject_name: str, percentage: float) -> str:
    """
    Provides contextual pedagogical advice for a weak subject based on subject domain and score.
    """
    sub_lower = subject_name.lower()
    
    severity = "Urgent: " if percentage < 30.0 else "Action Required: "

    if any(k in sub_lower for k in ["math", "calculus", "algebra", "discrete", "statistics", "numerical"]):
        return (f"{severity}Devote at least 45 minutes daily to step-by-step problem sets. "
                "Schedule a 1-on-1 session with the math faculty to review foundational formulas and proof methods.")
    elif any(k in sub_lower for k in ["program", "code", "python", "java", "c++", "data structure", "algorithm"]):
        return (f"{severity}Engage in hands-on coding practice on lab exercises. "
                "Dry-run algorithms on paper, write pseudocode before typing, and complete 3 code reviews weekly.")
    elif any(k in sub_lower for k in ["data", "dbms", "database", "sql"]):
        return (f"{severity}Practice ER diagrams, normalization forms (1NF to BCNF), and write live SQL queries. "
                "Build a small schema from scratch to cement relational concepts.")
    elif any(k in sub_lower for k in ["network", "operating system", "os", "architecture", "microprocessor"]):
        return (f"{severity}Use visual mind maps and flowcharts to understand protocols, OSI layers, and CPU scheduling. "
                "Review past exam papers to practice standard descriptive and numerical problems.")
    elif any(k in sub_lower for k in ["circuit", "analog", "digital", "vlsi", "electronics", "signal"]):
        return (f"{severity}Review circuit laws (KVL/KCL), component characteristics, and simulate circuits in software. "
                "Prioritize numerical problem-solving and lab component verification.")
    elif any(k in sub_lower for k in ["physics", "chemistry", "mechanics", "thermodynamics"]):
        return (f"{severity}Focus on free-body diagrams, fundamental laws, and unit conversions. "
                "Re-solve all lecture practice problems before attempting advanced question banks.")
    else:
        return (f"{severity}Review lecture notes daily, summarize key definitions in flashcards, "
                "and consult course instructor during office hours for targeted remedial instruction.")


# ============================================================================
# INDIVIDUAL STUDENT PERFORMANCE EVALUATION
# ============================================================================

def evaluate_student_exam_performance(marks_df: pd.DataFrame, student_id: str, exam_id: int) -> Dict[str, Any]:
    """
    Evaluates the performance of a student in a specific examination cycle.
    """
    student_records = marks_df[
        (marks_df["student_id"] == student_id) & 
        (marks_df["exam_id"] == exam_id)
    ].copy()

    if student_records.empty:
        return {
            "has_data": False,
            "message": f"No marks recorded for Student '{student_id}' in selected exam."
        }

    total_obtained = student_records["marks_obtained"].sum()
    total_max = student_records["max_marks"].sum()
    overall_percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0.0

    overall_grade, grade_point, grade_desc, grade_color = calculate_grade(overall_percentage)

    # Subject details
    subject_list = []
    weak_subjects = []
    strong_subjects = []

    for _, row in student_records.iterrows():
        pct = float(row["percentage"])
        g, gp, desc, color = calculate_grade(pct)
        is_weak = pct < WEAK_SUBJECT_THRESHOLD
        is_strong = pct >= STRONG_SUBJECT_THRESHOLD

        item = {
            "subject_code": row["subject_code"],
            "subject_name": row["subject_name"],
            "marks_obtained": row["marks_obtained"],
            "max_marks": row["max_marks"],
            "percentage": pct,
            "grade": g,
            "grade_point": gp,
            "grade_desc": desc,
            "color": color,
            "is_weak": is_weak,
            "is_strong": is_strong,
            "status": "PASS" if not is_weak else "FAIL / AT RISK",
            "credits": row.get("credits", 3)
        }
        subject_list.append(item)

        if is_weak:
            recommendation = get_subject_recommendation(row["subject_name"], pct)
            weak_subjects.append({
                "subject_code": row["subject_code"],
                "subject_name": row["subject_name"],
                "percentage": pct,
                "marks": f"{row['marks_obtained']}/{row['max_marks']}",
                "recommendation": recommendation
            })
        elif is_strong:
            strong_subjects.append({
                "subject_code": row["subject_code"],
                "subject_name": row["subject_name"],
                "percentage": pct,
                "marks": f"{row['marks_obtained']}/{row['max_marks']}"
            })

    # Academic Standing Status
    if len(weak_subjects) == 0:
        standing = "CLEAR PASS"
        standing_color = "#10B981"
    elif len(weak_subjects) <= 2:
        standing = f"PROMOTED WITH REMEDIAL NEEDS ({len(weak_subjects)} Weak Subjects)"
        standing_color = "#F59E0B"
    else:
        standing = f"CRITICAL - REMEDIAL INTERVENTION REQUIRED ({len(weak_subjects)} Failed Subjects)"
        standing_color = "#EF4444"

    first_row = student_records.iloc[0]

    return {
        "has_data": True,
        "student_id": student_id,
        "student_name": first_row["student_name"],
        "department": first_row["department"],
        "semester": first_row["student_semester"],
        "email": first_row.get("email", ""),
        "exam_id": exam_id,
        "exam_name": first_row["exam_name"],
        "academic_year": first_row["academic_year"],
        "total_obtained": round(total_obtained, 2),
        "total_max": round(total_max, 2),
        "overall_percentage": overall_percentage,
        "overall_grade": overall_grade,
        "grade_point": grade_point,
        "grade_description": grade_desc,
        "grade_color": grade_color,
        "standing": standing,
        "standing_color": standing_color,
        "subject_count": len(subject_list),
        "subjects": subject_list,
        "weak_subjects": weak_subjects,
        "strong_subjects": strong_subjects,
        "passed_subject_count": len(subject_list) - len(weak_subjects),
        "failed_subject_count": len(weak_subjects)
    }


# ============================================================================
# MULTI-EXAM PROGRESS TRACKING & TRAJECTORY ANALYSIS
# ============================================================================

def track_student_progress(marks_df: pd.DataFrame, student_id: str) -> Dict[str, Any]:
    """
    Analyzes student trajectory across all examinations taken to detect improvement or decline.
    """
    student_records = marks_df[marks_df["student_id"] == student_id].copy()

    if student_records.empty:
        return {
            "has_data": False,
            "message": f"No examination records found for Student ID '{student_id}'."
        }

    # Aggregate by exam
    exam_summary = []
    unique_exams = student_records[["exam_id", "exam_name", "academic_year"]].drop_duplicates()

    for _, ex in unique_exams.iterrows():
        eid = ex["exam_id"]
        ex_marks = student_records[student_records["exam_id"] == eid]
        tot_obt = ex_marks["marks_obtained"].sum()
        tot_max = ex_marks["max_marks"].sum()
        pct = round((tot_obt / tot_max) * 100, 2) if tot_max > 0 else 0.0
        g, gp, _, _ = calculate_grade(pct)

        # Count weak subjects in this exam
        weak_count = (ex_marks["percentage"] < WEAK_SUBJECT_THRESHOLD).sum()

        exam_summary.append({
            "exam_id": eid,
            "exam_name": ex["exam_name"],
            "academic_year": ex["academic_year"],
            "total_obtained": tot_obt,
            "total_max": tot_max,
            "percentage": pct,
            "grade": g,
            "weak_count": weak_count
        })

    # Sort exams in order of ID / chronology
    exam_summary = sorted(exam_summary, key=lambda x: x["exam_id"])

    # Calculate Deltas
    for i in range(len(exam_summary)):
        if i == 0:
            exam_summary[i]["delta_from_previous"] = 0.0
        else:
            prev_pct = exam_summary[i-1]["percentage"]
            curr_pct = exam_summary[i]["percentage"]
            exam_summary[i]["delta_from_previous"] = round(curr_pct - prev_pct, 2)

    # Overall Trajectory
    first_pct = exam_summary[0]["percentage"]
    latest_pct = exam_summary[-1]["percentage"]
    overall_delta = round(latest_pct - first_pct, 2)

    if len(exam_summary) == 1:
        trajectory_label = "Initial Baseline Established"
        trajectory_type = "neutral"
        trajectory_color = "#3B82F6"
    elif overall_delta >= 10.0:
        trajectory_label = f"Substantial Academic Improvement (+{overall_delta}%)"
        trajectory_type = "positive_strong"
        trajectory_color = "#10B981"
    elif overall_delta > 2.0:
        trajectory_label = f"Positive Progress Trend (+{overall_delta}%)"
        trajectory_type = "positive"
        trajectory_color = "#34D399"
    elif overall_delta >= -2.0:
        trajectory_label = f"Stable Performance ({overall_delta:+.2f}%)"
        trajectory_type = "neutral"
        trajectory_color = "#6366F1"
    elif overall_delta >= -8.0:
        trajectory_label = f"Noticeable Performance Decline ({overall_delta}%)"
        trajectory_type = "negative"
        trajectory_color = "#F59E0B"
    else:
        trajectory_label = f"Severe Performance Decline ({overall_delta}%) - Immediate Intervention Needed"
        trajectory_type = "negative_critical"
        trajectory_color = "#EF4444"

    # Subject-wise comparison across exams
    pivot_subjects = student_records.pivot_table(
        index=["subject_code", "subject_name"],
        columns="exam_name",
        values="percentage",
        aggfunc="first"
    ).reset_index()

    subject_trends = []
    for _, srow in pivot_subjects.iterrows():
        scode = srow["subject_code"]
        sname = srow["subject_name"]
        exam_scores = {col: srow[col] for col in pivot_subjects.columns if col not in ["subject_code", "subject_name"]}
        
        # calculate change between first and last known exam
        valid_scores = [val for val in exam_scores.values() if pd.notna(val)]
        if len(valid_scores) >= 2:
            s_delta = round(valid_scores[-1] - valid_scores[0], 2)
        else:
            s_delta = 0.0

        subject_trends.append({
            "subject_code": scode,
            "subject_name": sname,
            "scores": exam_scores,
            "delta": s_delta,
            "status": "Improved" if s_delta > 2 else ("Declined" if s_delta < -2 else "Steady")
        })

    first_rec = student_records.iloc[0]

    return {
        "has_data": True,
        "student_id": student_id,
        "student_name": first_rec["student_name"],
        "department": first_rec["department"],
        "semester": first_rec["student_semester"],
        "total_exams_taken": len(exam_summary),
        "exam_history": exam_summary,
        "overall_delta": overall_delta,
        "trajectory_label": trajectory_label,
        "trajectory_type": trajectory_type,
        "trajectory_color": trajectory_color,
        "subject_trends": subject_trends,
        "pivot_table": pivot_subjects
    }


# ============================================================================
# BATCH / COHORT LEVEL AGGREGATIONS
# ============================================================================

def get_cohort_summary_statistics(marks_df: pd.DataFrame, exam_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Computes overall cohort analytics (average, pass rate, grade counts, subject stats).
    """
    filtered_df = marks_df.copy()
    if exam_id and exam_id != 0:
        filtered_df = filtered_df[filtered_df["exam_id"] == exam_id]

    if filtered_df.empty:
        return {
            "has_data": False,
            "total_students": 0,
            "average_percentage": 0.0,
            "pass_rate": 0.0,
            "at_risk_students_count": 0,
            "grade_distribution": {},
            "subject_statistics": pd.DataFrame()
        }

    # Student-level aggregates
    student_aggs = filtered_df.groupby("student_id").agg(
        student_name=("student_name", "first"),
        department=("department", "first"),
        total_obtained=("marks_obtained", "sum"),
        total_max=("max_marks", "sum"),
        has_fail_subject=("percentage", lambda x: (x < WEAK_SUBJECT_THRESHOLD).any())
    ).reset_index()

    student_aggs["percentage"] = (student_aggs["total_obtained"] / student_aggs["total_max"]) * 100
    student_aggs["grade"] = student_aggs["percentage"].apply(lambda p: calculate_grade(p)[0])

    total_students = len(student_aggs)
    avg_percentage = round(student_aggs["percentage"].mean(), 2)
    highest_percentage = round(student_aggs["percentage"].max(), 2)
    lowest_percentage = round(student_aggs["percentage"].min(), 2)
    passed_students = (~student_aggs["has_fail_subject"]).sum()
    pass_rate = round((passed_students / total_students) * 100, 2) if total_students > 0 else 0.0
    at_risk_count = int(student_aggs["has_fail_subject"].sum())

    # Grade distribution counts
    grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
    grade_counts = student_aggs["grade"].value_counts().to_dict()
    ordered_grades = {g: grade_counts.get(g, 0) for g in grade_order}

    # Subject-wise statistics
    subject_stats = filtered_df.groupby(["subject_code", "subject_name"]).agg(
        enrolled_count=("student_id", "count"),
        average_percentage=("percentage", lambda x: round(x.mean(), 2)),
        max_percentage=("percentage", "max"),
        min_percentage=("percentage", "min"),
        weak_students_count=("percentage", lambda x: (x < WEAK_SUBJECT_THRESHOLD).sum()),
        pass_percentage=("percentage", lambda x: round((x >= WEAK_SUBJECT_THRESHOLD).mean() * 100, 2))
    ).reset_index()

    return {
        "has_data": True,
        "total_students": total_students,
        "average_percentage": avg_percentage,
        "highest_percentage": highest_percentage,
        "lowest_percentage": lowest_percentage,
        "pass_rate": pass_rate,
        "passed_students": int(passed_students),
        "at_risk_students_count": at_risk_count,
        "grade_distribution": ordered_grades,
        "student_level_df": student_aggs,
        "subject_statistics": subject_stats
    }


def identify_all_weak_subjects_df(marks_df: pd.DataFrame, exam_id: Optional[int] = None) -> pd.DataFrame:
    """
    Returns a structured DataFrame of all instances where a student scored below 40%,
    complete with subject details and pedagogical recommendations.
    """
    filtered_df = marks_df.copy()
    if exam_id and exam_id != 0:
        filtered_df = filtered_df[filtered_df["exam_id"] == exam_id]

    weak_df = filtered_df[filtered_df["percentage"] < WEAK_SUBJECT_THRESHOLD].copy()

    if weak_df.empty:
        return pd.DataFrame(columns=[
            "student_id", "student_name", "department", "exam_name",
            "subject_code", "subject_name", "marks_obtained", "max_marks",
            "percentage", "recommendation"
        ])

    weak_df["recommendation"] = weak_df.apply(
        lambda r: get_subject_recommendation(r["subject_name"], r["percentage"]), 
        axis=1
    )

    weak_df = weak_df[[
        "student_id", "student_name", "department", "exam_name",
        "subject_code", "subject_name", "marks_obtained", "max_marks",
        "percentage", "recommendation"
    ]].sort_values(by=["percentage", "student_id"], ascending=[True, True])

    return weak_df
