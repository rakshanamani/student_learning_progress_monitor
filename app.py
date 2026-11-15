"""
Student Learning Progress Monitor - Main Streamlit Application.
A complete academic management, analytics, progress tracking, and PDF reporting system.
"""

import os
import sys
import tempfile
from datetime import datetime

# Configure temporary cache for matplotlib before importing it
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_cache"))

import streamlit as st
import pandas as pd
import numpy as np

# Ensure local directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database import (
    init_db, get_connection, add_student, update_student, delete_student,
    get_all_students, get_student_by_id, add_subject, get_all_subjects,
    delete_subject, add_exam, get_all_exams, delete_exam, save_or_update_mark,
    save_marks_batch, delete_mark, get_all_marks_joined_df, get_db_stats,
    reset_database, DEFAULT_DB_PATH
)
from seed_data import seed_database
from analytics import (
    evaluate_student_exam_performance, track_student_progress,
    get_cohort_summary_statistics, identify_all_weak_subjects_df,
    calculate_grade, WEAK_SUBJECT_THRESHOLD
)
from visualizations import (
    plot_subject_performance_bar, plot_progress_trend,
    plot_grade_distribution_donut, plot_subject_class_comparison
)
from report_generator import generate_student_pdf_report


# ============================================================================
# STREAMLIT PAGE CONFIGURATION & CUSTOM STYLES
# ============================================================================

st.set_page_config(
    page_title="Student Learning Progress Monitor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern card designs, badges, and clean tables
st.markdown("""
<style>
    /* Global Container Tweaks */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Header Branding */
    .app-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 1.2rem 1.6rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .app-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF !important;
    }
    .app-header p {
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.9;
        color: #E0E7FF !important;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card-label {
        font-size: 0.85rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .metric-card-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #111827;
    }
    .metric-card-sub {
        font-size: 0.8rem;
        color: #9CA3AF;
        margin-top: 0.2rem;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 700;
        border-radius: 9999px;
        text-align: center;
    }
    .badge-pass { background-color: #D1FAE5; color: #065F46; }
    .badge-fail { background-color: #FEE2E2; color: #991B1B; }
    .badge-warning { background-color: #FEF3C7; color: #92400E; }
    .badge-info { background-color: #DBEAFE; color: #1E40AF; }

    /* Advisory Card */
    .advice-card {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 0.8rem;
    }
    .advice-card-critical {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INITIALIZATION & CACHE HELPERS
# ============================================================================

# Ensure database tables exist
init_db()

def refresh_db():
    """Forces cache clearing for database queries."""
    st.cache_data.clear()


# ============================================================================
# SIDEBAR NAVIGATION & QUICK CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("### 🎓 Academic Monitor")
    st.caption("Student Progress & Learning Analytics")

    # Quick DB Stats Pill
    stats = get_db_stats()
    st.markdown(
        f"""
        <div style="background-color: #F3F4F6; padding: 0.6rem; border-radius: 6px; font-size: 0.8rem; margin-bottom: 1rem;">
            <b>Database Status:</b><br/>
            👨‍🎓 <b>{stats['students']}</b> Students &nbsp;|&nbsp; 
            📚 <b>{stats['subjects']}</b> Subjects<br/>
            📝 <b>{stats['exams']}</b> Exams &nbsp;|&nbsp; 
            📊 <b>{stats['marks_records']}</b> Marks Recorded
        </div>
        """,
        unsafe_allow_html=True
    )

    # Empty State Quick Seed Prompt
    if stats['students'] == 0:
        st.warning("Database is empty!")
        if st.button("🌱 Load Sample Academic Data", use_container_width=True, type="primary"):
            seed_res = seed_database(verbose=False)
            st.success(f"Seeded {seed_res['students']} students & {seed_res['marks']} marks!")
            refresh_db()
            st.rerun()

    menu_option = st.radio(
        "Navigation Modules",
        [
            "📊 Dashboard & Overview",
            "👨‍🎓 Student Management",
            "📝 Academic Records",
            "📈 Performance Analysis",
            "⚠️ Weak Subject Identification",
            "🚀 Progress Tracking",
            "📄 Individual Progress Reports",
            "⚙️ Database & Settings"
        ],
        index=0
    )

    st.markdown("---")
    st.caption("Version 1.0.0 • SQLite & Streamlit")


# Load common dataset
marks_df = get_all_marks_joined_df()
students_df = get_all_students()
exams_df = get_all_exams()
subjects_df = get_all_subjects()


# ============================================================================
# MODULE 1: DASHBOARD & OVERVIEW
# ============================================================================

if menu_option == "📊 Dashboard & Overview":
    st.markdown("""
    <div class="app-header">
        <h1>📊 Student Learning Progress Dashboard</h1>
        <p>Comprehensive academic performance monitoring, class benchmarks, and early-warning metrics.</p>
    </div>
    """, unsafe_allow_html=True)

    if marks_df.empty:
        st.info("ℹ️ No academic data found. Please navigate to the **Settings** tab or click the sidebar button to seed sample academic records.")
    else:
        # Top-level Filters Bar
        col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 2])
        with col_f1:
            dept_options = ["All"] + sorted(marks_df["department"].unique().tolist())
            selected_dept = st.selectbox("Filter Department:", dept_options, index=0)
        with col_f2:
            sem_options = [0] + sorted(marks_df["student_semester"].unique().tolist())
            selected_sem = st.selectbox("Filter Semester:", sem_options, format_func=lambda s: "All Semesters" if s == 0 else f"Semester {s}")
        with col_f3:
            exam_records = exams_df.to_dict("records")
            exam_choices = {0: "All Exams Aggregate"} | {e["exam_id"]: f"{e['exam_name']} ({e['academic_year']})" for e in exam_records}
            selected_exam_id = st.selectbox("Filter Examination:", list(exam_choices.keys()), format_func=lambda k: exam_choices[k])

        # Apply Filters to dataset
        filtered_df = marks_df.copy()
        if selected_dept != "All":
            filtered_df = filtered_df[filtered_df["department"] == selected_dept]
        if selected_sem != 0:
            filtered_df = filtered_df[filtered_df["student_semester"] == selected_sem]
        if selected_exam_id != 0:
            filtered_df = filtered_df[filtered_df["exam_id"] == selected_exam_id]

        cohort_metrics = get_cohort_summary_statistics(filtered_df)

        # 4 Key Metrics Cards
        mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
        with mcol1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Enrolled Students</div>
                <div class="metric-card-value">{cohort_metrics['total_students']}</div>
                <div class="metric-card-sub">Active in Selection</div>
            </div>
            """, unsafe_allow_html=True)

        with mcol2:
            avg_color = "#10B981" if cohort_metrics['average_percentage'] >= 70 else ("#F59E0B" if cohort_metrics['average_percentage'] >= 50 else "#EF4444")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Cohort Average</div>
                <div class="metric-card-value" style="color: {avg_color};">{cohort_metrics['average_percentage']:.1f}%</div>
                <div class="metric-card-sub">Range: {cohort_metrics['lowest_percentage']:.1f}% - {cohort_metrics['highest_percentage']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with mcol3:
            pass_color = "#10B981" if cohort_metrics['pass_rate'] >= 75 else "#F59E0B"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Cohort Pass Rate</div>
                <div class="metric-card-value" style="color: {pass_color};">{cohort_metrics['pass_rate']:.1f}%</div>
                <div class="metric-card-sub">{cohort_metrics['passed_students']} Passed All Subjects</div>
            </div>
            """, unsafe_allow_html=True)

        with mcol4:
            risk_color = "#EF4444" if cohort_metrics['at_risk_students_count'] > 0 else "#10B981"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">At-Risk Students</div>
                <div class="metric-card-value" style="color: {risk_color};">{cohort_metrics['at_risk_students_count']}</div>
                <div class="metric-card-sub">Score &lt; 40% in ≥ 1 Subject</div>
            </div>
            """, unsafe_allow_html=True)

        with mcol5:
            weak_total_instances = (filtered_df["percentage"] < WEAK_SUBJECT_THRESHOLD).sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Weak Subject Marks</div>
                <div class="metric-card-value" style="color: {'#EF4444' if weak_total_instances > 0 else '#10B981'};">{weak_total_instances}</div>
                <div class="metric-card-sub">Remedial Needs</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # Visualizations Row: Grade Donut + Subject Class Benchmark Bar
        chart_col1, chart_col2 = st.columns([1, 1.4])
        with chart_col1:
            st.subheader("🎯 Grade Distribution")
            fig_donut = plot_grade_distribution_donut(cohort_metrics["grade_distribution"], title="Cohort Grade Breakdown")
            st.pyplot(fig_donut)

        with chart_col2:
            st.subheader("📊 Subject Benchmarks (Min / Avg / Max)")
            fig_bars = plot_subject_class_comparison(cohort_metrics["subject_statistics"])
            st.pyplot(fig_bars)

        # Subject-wise Detailed Statistics Table
        st.subheader("📚 Subject Performance Summary")
        if not cohort_metrics["subject_statistics"].empty:
            sub_display_df = cohort_metrics["subject_statistics"].rename(columns={
                "subject_code": "Code",
                "subject_name": "Subject Name",
                "enrolled_count": "Records",
                "average_percentage": "Class Avg (%)",
                "min_percentage": "Lowest (%)",
                "max_percentage": "Highest (%)",
                "weak_students_count": "Weak Students (<40%)",
                "pass_percentage": "Pass Rate (%)"
            })
            st.dataframe(sub_display_df, use_container_width=True, hide_index=True)


# ============================================================================
# MODULE 2: STUDENT MANAGEMENT
# ============================================================================

elif menu_option == "👨‍🎓 Student Management":
    st.markdown("""
    <div class="app-header">
        <h1>👨‍🎓 Student Management System</h1>
        <p>Register new students, update profiles, view department rosters, or delete records.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_view, tab_add, tab_edit, tab_delete = st.tabs([
        "📋 View & Search Students",
        "➕ Register New Student",
        "✏️ Edit Student Details",
        "🗑️ Delete Student Record"
    ])

    # Tab 1: View Students
    with tab_view:
        st.subheader("Student Roster Directory")
        vcol1, vcol2, vcol3 = st.columns([1.5, 1.5, 3])
        with vcol1:
            depts = ["All"] + sorted(students_df["department"].unique().tolist()) if not students_df.empty else ["All"]
            v_dept = st.selectbox("Filter by Department:", depts, key="view_st_dept")
        with vcol2:
            sems = [0] + sorted(students_df["semester"].unique().tolist()) if not students_df.empty else [0]
            v_sem = st.selectbox("Filter by Semester:", sems, format_func=lambda s: "All Semesters" if s == 0 else f"Semester {s}", key="view_st_sem")
        with vcol3:
            search_query = st.text_input("🔍 Search by Name or Student ID:", placeholder="e.g. Aarav, CS202401...")

        view_filtered = get_all_students(v_dept, v_sem)
        if search_query.strip():
            sq = search_query.strip().lower()
            view_filtered = view_filtered[
                view_filtered["name"].str.lower().str.contains(sq) | 
                view_filtered["student_id"].str.lower().str.contains(sq)
            ]

        st.markdown(f"**Showing {len(view_filtered)} Students:**")
        if not view_filtered.empty:
            st.dataframe(view_filtered, use_container_width=True, hide_index=True)

            # Export to CSV
            csv_data = view_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Student Roster (CSV)",
                data=csv_data,
                file_name=f"student_roster_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No students found matching the selected filters.")

    # Tab 2: Add Student
    with tab_add:
        st.subheader("Add New Student Record")
        with st.form("add_student_form", clear_on_submit=True):
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                new_id = st.text_input("Student ID (Unique) *", placeholder="e.g. CS202409").strip().upper()
                new_name = st.text_input("Full Name *", placeholder="e.g. Maya Sharma")
                new_dept = st.selectbox("Department *", [
                    "Computer Science", "Electronics", "Mechanical",
                    "Civil", "Information Technology", "Electrical"
                ])
            with fcol2:
                new_sem = st.slider("Semester *", min_value=1, max_value=8, value=3)
                new_email = st.text_input("Email Address", placeholder="e.g. maya@campus.edu")
                new_contact = st.text_input("Contact Number", placeholder="+91 98765 00000")

            submitted = st.form_submit_button("✅ Add Student to Database", use_container_width=True, type="primary")
            if submitted:
                if not new_id or not new_name:
                    st.error("Student ID and Full Name are mandatory fields.")
                else:
                    success, msg = add_student(new_id, new_name, new_dept, new_sem, new_email, new_contact)
                    if success:
                        st.success(msg)
                        refresh_db()
                    else:
                        st.error(msg)

    # Tab 3: Edit Student
    with tab_edit:
        st.subheader("Update Student Information")
        if students_df.empty:
            st.info("No students registered yet.")
        else:
            student_map = {f"{r['student_id']} - {r['name']} ({r['department']})": r["student_id"] for _, r in students_df.iterrows()}
            selected_st_label = st.selectbox("Select Student to Edit:", list(student_map.keys()))
            st_id_to_edit = student_map[selected_st_label]
            curr_student = get_student_by_id(st_id_to_edit)

            if curr_student:
                with st.form("edit_student_form"):
                    ecol1, ecol2 = st.columns(2)
                    with ecol1:
                        st.text_input("Student ID (Read-only)", value=curr_student["student_id"], disabled=True)
                        edit_name = st.text_input("Full Name *", value=curr_student["name"])
                        dept_list = ["Computer Science", "Electronics", "Mechanical", "Civil", "Information Technology", "Electrical"]
                        dept_idx = dept_list.index(curr_student["department"]) if curr_student["department"] in dept_list else 0
                        edit_dept = st.selectbox("Department *", dept_list, index=dept_idx)
                    with ecol2:
                        edit_sem = st.slider("Semester *", min_value=1, max_value=8, value=int(curr_student["semester"]))
                        edit_email = st.text_input("Email Address", value=curr_student.get("email") or "")
                        edit_contact = st.text_input("Contact Number", value=curr_student.get("contact") or "")

                    update_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                    if update_btn:
                        ok, msg = update_student(st_id_to_edit, edit_name, edit_dept, edit_sem, edit_email, edit_contact)
                        if ok:
                            st.success(msg)
                            refresh_db()
                        else:
                            st.error(msg)

    # Tab 4: Delete Student
    with tab_delete:
        st.subheader("Delete Student Record")
        if students_df.empty:
            st.info("No students in database.")
        else:
            st.warning("⚠️ Warning: Deleting a student permanently removes all their examination marks and progress history.")
            del_map = {f"{r['student_id']} - {r['name']} ({r['department']})": r["student_id"] for _, r in students_df.iterrows()}
            del_label = st.selectbox("Select Student to Delete:", list(del_map.keys()), key="del_student_select")
            del_id = del_map[del_label]

            confirm_del = st.checkbox(f"I understand and confirm deletion of {del_label}")
            if st.button("🚨 Delete Student Permanently", disabled=not confirm_del, type="secondary"):
                ok, msg = delete_student(del_id)
                if ok:
                    st.success(msg)
                    refresh_db()
                    st.rerun()
                else:
                    st.error(msg)


# ============================================================================
# MODULE 3: ACADEMIC RECORDS (MARKS ENTRY)
# ============================================================================

elif menu_option == "📝 Academic Records":
    st.markdown("""
    <div class="app-header">
        <h1>📝 Academic Examination Marks Entry</h1>
        <p>Record, update, and manage subject-wise marks across exams for cohorts and individuals.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_single_entry, tab_batch_entry, tab_view_marks, tab_manage_exams = st.tabs([
        "👤 Individual Marks Entry",
        "👥 Class Batch Marks Entry",
        "🔍 View & Filter Recorded Marks",
        "⚙️ Manage Exam Cycles & Subjects"
    ])

    # Tab 1: Single Student Marks Entry
    with tab_single_entry:
        st.subheader("Enter Marks for a Single Student")
        if students_df.empty or exams_df.empty or subjects_df.empty:
            st.error("Please ensure Students, Exams, and Subjects exist before entering marks.")
        else:
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st_lookup = {f"{r['student_id']} - {r['name']} ({r['department']}, Sem {r['semester']})": r["student_id"] for _, r in students_df.iterrows()}
                sel_st_lbl = st.selectbox("Select Student:", list(st_lookup.keys()), key="single_entry_st")
                target_st_id = st_lookup[sel_st_lbl]
                st_info = get_student_by_id(target_st_id)
            with s_col2:
                exam_lookup = {f"{r['exam_name']} ({r['academic_year']})": r["exam_id"] for _, r in exams_df.iterrows()}
                sel_exam_lbl = st.selectbox("Select Examination:", list(exam_lookup.keys()), key="single_entry_exam")
                target_exam_id = exam_lookup[sel_exam_lbl]

            # Filter subjects relevant to student's department and semester
            eligible_subjects = subjects_df[
                (subjects_df["department"] == st_info["department"]) &
                (subjects_df["semester"] == st_info["semester"])
            ]

            if eligible_subjects.empty:
                st.info(f"No subjects registered specifically for {st_info['department']} Semester {st_info['semester']}. Showing all subjects.")
                eligible_subjects = subjects_df

            # Pre-fetch any existing marks
            existing_marks_df = marks_df[
                (marks_df["student_id"] == target_st_id) &
                (marks_df["exam_id"] == target_exam_id)
            ]
            existing_map = dict(zip(existing_marks_df["subject_code"], existing_marks_df["marks_obtained"]))

            st.markdown(f"**Entering marks for {st_info['name']} ({st_info['student_id']}) in {sel_exam_lbl}:**")

            with st.form("single_student_marks_form"):
                entered_marks = {}
                sub_cols = st.columns(2)
                for i, (_, sub) in enumerate(eligible_subjects.iterrows()):
                    col_target = sub_cols[i % 2]
                    curr_val = float(existing_map.get(sub["subject_code"], 0.0))
                    with col_target:
                        entered_val = st.number_input(
                            f"{sub['subject_name']} ({sub['subject_code']})",
                            min_value=0.0,
                            max_value=100.0,
                            value=curr_val,
                            step=1.0,
                            help=f"Credits: {sub.get('credits', 3)} | Max Marks: 100"
                        )
                        entered_marks[sub["subject_code"]] = entered_val

                save_single_btn = st.form_submit_button("💾 Save Examination Marks", use_container_width=True, type="primary")
                if save_single_btn:
                    save_records = [
                        {
                            "student_id": target_st_id,
                            "exam_id": target_exam_id,
                            "subject_code": scode,
                            "marks_obtained": sval,
                            "max_marks": 100.0
                        }
                        for scode, sval in entered_marks.items()
                    ]
                    ok, msg, count = save_marks_batch(save_records)
                    if ok:
                        st.success(f"✅ Successfully saved marks for {count} subjects!")
                        refresh_db()
                    else:
                        st.error(msg)

    # Tab 2: Class Batch Marks Entry
    with tab_batch_entry:
        st.subheader("Batch Marks Entry by Subject & Class")
        if students_df.empty or exams_df.empty or subjects_df.empty:
            st.error("Required data not found.")
        else:
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                b_exam_lookup = {f"{r['exam_name']} ({r['academic_year']})": r["exam_id"] for _, r in exams_df.iterrows()}
                b_exam_lbl = st.selectbox("Select Examination:", list(b_exam_lookup.keys()), key="batch_exam")
                b_exam_id = b_exam_lookup[b_exam_lbl]
            with b_col2:
                b_depts = sorted(students_df["department"].unique().tolist())
                b_dept = st.selectbox("Select Department:", b_depts, key="batch_dept")
            with b_col3:
                b_subjs = subjects_df[subjects_df["department"] == b_dept]
                if b_subjs.empty:
                    b_subjs = subjects_df
                b_sub_lookup = {f"{r['subject_code']} - {r['subject_name']}": r["subject_code"] for _, r in b_subjs.iterrows()}
                b_sub_lbl = st.selectbox("Select Subject:", list(b_sub_lookup.keys()), key="batch_subject")
                b_sub_code = b_sub_lookup[b_sub_lbl]

            cohort_students = students_df[students_df["department"] == b_dept]
            st.markdown(f"**Found {len(cohort_students)} students in {b_dept}:**")

            # Load any existing marks for this exam + subject
            existing_batch = marks_df[
                (marks_df["exam_id"] == b_exam_id) & 
                (marks_df["subject_code"] == b_sub_code)
            ]
            batch_map = dict(zip(existing_batch["student_id"], existing_batch["marks_obtained"]))

            with st.form("batch_marks_form"):
                batch_inputs = {}
                b_grid = st.columns(2)
                for idx, (_, st_row) in enumerate(cohort_students.iterrows()):
                    col_t = b_grid[idx % 2]
                    curr_m = float(batch_map.get(st_row["student_id"], 0.0))
                    with col_t:
                        batch_inputs[st_row["student_id"]] = st.number_input(
                            f"{st_row['name']} ({st_row['student_id']})",
                            min_value=0.0,
                            max_value=100.0,
                            value=curr_m,
                            step=1.0,
                            key=f"batch_in_{st_row['student_id']}"
                        )

                submit_batch = st.form_submit_button("💾 Save Batch Marks for All Students", use_container_width=True, type="primary")
                if submit_batch:
                    batch_payload = [
                        {
                            "student_id": sid,
                            "exam_id": b_exam_id,
                            "subject_code": b_sub_code,
                            "marks_obtained": sval,
                            "max_marks": 100.0
                        }
                        for sid, sval in batch_inputs.items()
                    ]
                    ok, msg, count = save_marks_batch(batch_payload)
                    if ok:
                        st.success(f"✅ Successfully saved marks for {count} students in {b_sub_code}!")
                        refresh_db()
                    else:
                        st.error(msg)

    # Tab 3: View & Manage Recorded Marks
    with tab_view_marks:
        st.subheader("All Recorded Marks")
        if marks_df.empty:
            st.info("No marks recorded yet.")
        else:
            filter_m1, filter_m2 = st.columns(2)
            with filter_m1:
                vm_dept = st.selectbox("Filter Department:", ["All"] + sorted(marks_df["department"].unique().tolist()), key="vm_dept")
            with filter_m2:
                vm_exam = st.selectbox("Filter Examination:", ["All"] + sorted(marks_df["exam_name"].unique().tolist()), key="vm_exam")

            display_marks = marks_df.copy()
            if vm_dept != "All":
                display_marks = display_marks[display_marks["department"] == vm_dept]
            if vm_exam != "All":
                display_marks = display_marks[display_marks["exam_name"] == vm_exam]

            st.dataframe(
                display_marks[[
                    "mark_id", "student_id", "student_name", "department",
                    "exam_name", "subject_code", "subject_name",
                    "marks_obtained", "max_marks", "percentage"
                ]],
                use_container_width=True,
                hide_index=True
            )

            # Delete single mark record
            with st.expander("🗑️ Delete a specific mark record"):
                del_mark_id = st.number_input("Enter Mark ID to Delete:", min_value=1, step=1)
                if st.button("Delete Mark", type="secondary"):
                    ok, msg = delete_mark(int(del_mark_id))
                    if ok:
                        st.success(msg)
                        refresh_db()
                        st.rerun()
                    else:
                        st.error(msg)

    # Tab 4: Manage Exam Cycles & Subjects
    with tab_manage_exams:
        st.subheader("Manage Examinations & Subject Catalog")
        mecol1, mecol2 = st.columns(2)

        with mecol1:
            st.markdown("#### ➕ Add New Exam Cycle")
            with st.form("add_exam_form", clear_on_submit=True):
                new_ename = st.text_input("Exam Name *", placeholder="e.g. Midterm 1, Final Exam")
                new_ayear = st.text_input("Academic Year *", value="2025-2026")
                new_esem = st.slider("Semester", 1, 8, 3)
                new_edate = st.date_input("Exam Date")
                if st.form_submit_button("Add Examination", use_container_width=True):
                    ok, msg, _ = add_exam(new_ename, new_ayear, new_esem, str(new_edate))
                    if ok:
                        st.success(msg)
                        refresh_db()
                    else:
                        st.error(msg)

        with mecol2:
            st.markdown("#### ➕ Add New Subject")
            with st.form("add_subject_form", clear_on_submit=True):
                new_scode = st.text_input("Subject Code *", placeholder="e.g. CS305").strip().upper()
                new_sname = st.text_input("Subject Name *", placeholder="e.g. Artificial Intelligence")
                new_sdept = st.selectbox("Department", ["Computer Science", "Electronics", "Mechanical", "Civil"])
                new_ssem = st.slider("Semester", 1, 8, 3, key="add_sub_sem")
                new_scred = st.number_input("Credits", min_value=1, max_value=6, value=4)
                if st.form_submit_button("Add Subject", use_container_width=True):
                    ok, msg = add_subject(new_scode, new_sname, new_sdept, new_ssem, new_scred)
                    if ok:
                        st.success(msg)
                        refresh_db()
                    else:
                        st.error(msg)


# ============================================================================
# MODULE 4: PERFORMANCE ANALYSIS
# ============================================================================

elif menu_option == "📈 Performance Analysis":
    st.markdown("""
    <div class="app-header">
        <h1>📈 Individual Academic Performance Analysis</h1>
        <p>In-depth student evaluation, aggregate scores, letter grades, and subject-level diagnostics.</p>
    </div>
    """, unsafe_allow_html=True)

    if marks_df.empty:
        st.info("No marks data found. Please add or seed academic records.")
    else:
        pacol1, pacol2 = st.columns([1.5, 1.5])
        with pacol1:
            st_options = {f"{r['student_id']} - {r['name']} ({r['department']})": r["student_id"] for _, r in students_df.iterrows()}
            sel_st_lbl = st.selectbox("Select Student:", list(st_options.keys()), key="pa_student")
            selected_st_id = st_options[sel_st_lbl]

        # Available exams for this student
        st_exams = marks_df[marks_df["student_id"] == selected_st_id][["exam_id", "exam_name", "academic_year"]].drop_duplicates()
        if st_exams.empty:
            st.warning("No examination records found for this student.")
        else:
            with pacol2:
                exam_opts = {f"{r['exam_name']} ({r['academic_year']})": r["exam_id"] for _, r in st_exams.iterrows()}
                sel_ex_lbl = st.selectbox("Select Examination:", list(exam_opts.keys()), key="pa_exam")
                selected_exam_id = exam_opts[sel_ex_lbl]

            # Run evaluation
            eval_result = evaluate_student_exam_performance(marks_df, selected_st_id, selected_exam_id)

            if eval_result.get("has_data"):
                # Top Scorecard Metrics Row
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                with sc1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-card-label">Total Marks</div>
                        <div class="metric-card-value">{eval_result['total_obtained']:.0f}<span style="font-size: 1rem; color: #9CA3AF;"> / {eval_result['total_max']:.0f}</span></div>
                        <div class="metric-card-sub">{eval_result['subject_count']} Subjects</div>
                    </div>
                    """, unsafe_allow_html=True)

                with sc2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-card-label">Overall Percentage</div>
                        <div class="metric-card-value" style="color: {eval_result['grade_color']};">{eval_result['overall_percentage']:.1f}%</div>
                        <div class="metric-card-sub">Weighted Aggregate</div>
                    </div>
                    """, unsafe_allow_html=True)

                with sc3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-card-label">Grade Awarded</div>
                        <div class="metric-card-value" style="color: {eval_result['grade_color']};">{eval_result['overall_grade']}</div>
                        <div class="metric-card-sub">{eval_result['grade_description']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with sc4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-card-label">Pass / Fail</div>
                        <div class="metric-card-value">{eval_result['passed_subject_count']} <span style="font-size: 1rem; color: #10B981;">Passed</span></div>
                        <div class="metric-card-sub" style="color: {'#EF4444' if eval_result['failed_subject_count'] > 0 else '#10B981'};">
                            {eval_result['failed_subject_count']} Failed (&lt; 40%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with sc5:
                    # Class Average Benchmark
                    class_subset = marks_df[marks_df["exam_id"] == selected_exam_id]
                    class_mean = class_subset["percentage"].mean() if not class_subset.empty else 0.0
                    delta_from_mean = eval_result['overall_percentage'] - class_mean
                    mean_color = "#10B981" if delta_from_mean >= 0 else "#EF4444"
                    sign = "+" if delta_from_mean >= 0 else ""
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-card-label">Class Benchmark</div>
                        <div class="metric-card-value" style="color: {mean_color};">{sign}{delta_from_mean:.1f}%</div>
                        <div class="metric-card-sub">Class Mean: {class_mean:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br/>", unsafe_allow_html=True)

                # Visual Bar Chart + Subject Table
                pcol1, pcol2 = st.columns([1.3, 1])
                with pcol1:
                    st.subheader("📊 Subject Marks vs. 40% Passing Threshold")
                    fig_bar = plot_subject_performance_bar(eval_result["subjects"])
                    st.pyplot(fig_bar)

                with pcol2:
                    st.subheader("📋 Subject-Wise Breakdown")
                    sub_table_rows = []
                    for s in eval_result["subjects"]:
                        sub_table_rows.append({
                            "Code": s["subject_code"],
                            "Subject": s["subject_name"],
                            "Score": f"{s['marks_obtained']:.0f}/{s['max_marks']:.0f}",
                            "Pct (%)": f"{s['percentage']:.1f}%",
                            "Grade": s["grade"],
                            "Status": s["status"]
                        })
                    st.dataframe(pd.DataFrame(sub_table_rows), use_container_width=True, hide_index=True)

                # Strengths & Weaknesses Callouts
                st.markdown("<br/>", unsafe_allow_html=True)
                wcol1, wcol2 = st.columns(2)
                with wcol1:
                    st.markdown("#### 🌟 Key Academic Strengths (≥ 75%)")
                    if eval_result["strong_subjects"]:
                        for s in eval_result["strong_subjects"]:
                            st.success(f"**{s['subject_name']}** ({s['subject_code']}): Scored **{s['percentage']:.1f}%** ({s['marks']})")
                    else:
                        st.info("No subjects currently scored at or above distinction level (75%).")

                with wcol2:
                    st.markdown("#### ⚠️ Weak Subjects & Improvement Needs (< 40%)")
                    if eval_result["weak_subjects"]:
                        for w in eval_result["weak_subjects"]:
                            st.error(f"**{w['subject_name']}** ({w['subject_code']}): Scored **{w['percentage']:.1f}%** ({w['marks']})\n\n💡 *Action Plan:* {w['recommendation']}")
                    else:
                        st.success("🎉 Excellent! No weak subjects detected. All subjects passed successfully!")


# ============================================================================
# MODULE 5: WEAK SUBJECT IDENTIFICATION
# ============================================================================

elif menu_option == "⚠️ Weak Subject Identification":
    st.markdown("""
    <div class="app-header">
        <h1>⚠️ Weak Subject Identification & Remedial Advisor</h1>
        <p>Early-warning detection of subjects scored below 40%, with automated diagnostic recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    if marks_df.empty:
        st.info("No marks records found.")
    else:
        # Filter controls
        w_col1, w_col2, w_col3 = st.columns([1.5, 1.5, 2])
        with w_col1:
            w_dept = st.selectbox("Filter Department:", ["All"] + sorted(marks_df["department"].unique().tolist()), key="weak_dept")
        with w_col2:
            w_exam_records = exams_df.to_dict("records")
            w_exam_choices = {0: "All Exams"} | {e["exam_id"]: f"{e['exam_name']}" for e in w_exam_records}
            w_exam_id = st.selectbox("Filter Examination:", list(w_exam_choices.keys()), format_func=lambda k: w_exam_choices[k], key="weak_exam")
        with w_col3:
            w_subs = ["All Subjects"] + sorted(marks_df["subject_name"].unique().tolist())
            w_sub_sel = st.selectbox("Filter Subject:", w_subs, key="weak_sub")

        # Build Weak Subjects DataFrame
        weak_df = identify_all_weak_subjects_df(marks_df, exam_id=w_exam_id)

        if w_dept != "All":
            weak_df = weak_df[weak_df["department"] == w_dept]
        if w_sub_sel != "All Subjects":
            weak_df = weak_df[weak_df["subject_name"] == w_sub_sel]

        # Metric summary
        total_weak_records = len(weak_df)
        unique_at_risk_students = weak_df["student_id"].nunique() if not weak_df.empty else 0
        most_affected_subject = weak_df["subject_name"].mode()[0] if not weak_df.empty else "None"

        wk1, wk2, wk3 = st.columns(3)
        with wk1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Weak Subject Incidents</div>
                <div class="metric-card-value" style="color: #EF4444;">{total_weak_records}</div>
                <div class="metric-card-sub">Individual Fails (&lt;40%)</div>
            </div>
            """, unsafe_allow_html=True)

        with wk2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Students Needing Remedial Attention</div>
                <div class="metric-card-value" style="color: #F59E0B;">{unique_at_risk_students}</div>
                <div class="metric-card-sub">Unique Student Profiles</div>
            </div>
            """, unsafe_allow_html=True)

        with wk3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">Most Challenging Subject</div>
                <div class="metric-card-value" style="font-size: 1.2rem; color: #3B82F6; padding-top: 0.5rem;">{most_affected_subject}</div>
                <div class="metric-card-sub">Highest Frequency of &lt;40%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        if weak_df.empty:
            st.balloons()
            st.success("🎉 Outstanding performance! Zero students scored below 40% under the current filters.")
        else:
            st.subheader(f"📋 Critical At-Risk Records ({len(weak_df)} Incidents)")

            # Detailed table
            st.dataframe(
                weak_df.rename(columns={
                    "student_id": "Student ID",
                    "student_name": "Student Name",
                    "department": "Department",
                    "exam_name": "Examination",
                    "subject_code": "Code",
                    "subject_name": "Weak Subject",
                    "marks_obtained": "Marks",
                    "percentage": "Score (%)",
                    "recommendation": "Remedial Recommendation"
                }),
                use_container_width=True,
                hide_index=True
            )

            # Download CSV
            weak_csv = weak_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Remedial At-Risk List (CSV)",
                data=weak_csv,
                file_name=f"at_risk_students_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

            st.markdown("---")
            st.subheader("💡 Individual Remedial Action Plans")

            # Group by Student for actionable teacher view
            for sid, group in weak_df.groupby("student_id"):
                first_row = group.iloc[0]
                with st.expander(f"⚠️ {first_row['student_name']} ({sid}) - {len(group)} Weak Subject(s)"):
                    for _, row in group.iterrows():
                        st.markdown(f"""
                        <div class="advice-card-critical">
                            <b>Subject:</b> {row['subject_name']} ({row['subject_code']}) &nbsp;|&nbsp; 
                            <b>Exam:</b> {row['exam_name']} &nbsp;|&nbsp; 
                            <b>Score:</b> <span style="color: #DC2626; font-weight: bold;">{row['percentage']:.1f}% ({row['marks_obtained']}/{row['max_marks']})</span><br/><br/>
                            <b>🎯 Targeted Pedagogical Recommendation:</b><br/>
                            {row['recommendation']}
                        </div>
                        """, unsafe_allow_html=True)


# ============================================================================
# MODULE 6: PROGRESS TRACKING
# ============================================================================

elif menu_option == "🚀 Progress Tracking":
    st.markdown("""
    <div class="app-header">
        <h1>🚀 Multi-Exam Academic Progress Tracking</h1>
        <p>Monitor performance trajectory across exams, calculate progression deltas, and detect learning trends.</p>
    </div>
    """, unsafe_allow_html=True)

    if marks_df.empty:
        st.info("No marks records available for progress tracking.")
    else:
        tr_st_options = {f"{r['student_id']} - {r['name']} ({r['department']})": r["student_id"] for _, r in students_df.iterrows()}
        selected_tr_lbl = st.selectbox("Select Student to Track:", list(tr_st_options.keys()), key="progress_student")
        selected_tr_id = tr_st_options[selected_tr_lbl]

        progress_data = track_student_progress(marks_df, selected_tr_id)

        if not progress_data.get("has_data"):
            st.warning("No multi-exam history found for this student.")
        else:
            exam_hist = progress_data["exam_history"]
            overall_delta = progress_data["overall_delta"]
            traj_label = progress_data["trajectory_label"]
            traj_color = progress_data["trajectory_color"]

            # Progress KPI Cards
            p_col1, p_col2, p_col3, p_col4 = st.columns(4)
            with p_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">Exams Completed</div>
                    <div class="metric-card-value">{progress_data['total_exams_taken']}</div>
                    <div class="metric-card-sub">Recorded Cycles</div>
                </div>
                """, unsafe_allow_html=True)

            with p_col2:
                first_score = exam_hist[0]["percentage"]
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">Baseline Score</div>
                    <div class="metric-card-value">{first_score:.1f}%</div>
                    <div class="metric-card-sub">{exam_hist[0]['exam_name']}</div>
                </div>
                """, unsafe_allow_html=True)

            with p_col3:
                latest_score = exam_hist[-1]["percentage"]
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">Latest Exam Score</div>
                    <div class="metric-card-value">{latest_score:.1f}%</div>
                    <div class="metric-card-sub">{exam_hist[-1]['exam_name']}</div>
                </div>
                """, unsafe_allow_html=True)

            with p_col4:
                sign = "+" if overall_delta > 0 else ""
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">Net Delta (Progress)</div>
                    <div class="metric-card-value" style="color: {traj_color};">{sign}{overall_delta:.1f}%</div>
                    <div class="metric-card-sub">{traj_label.split(' - ')[0]}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br/>", unsafe_allow_html=True)

            # Trajectory Banner Alert
            if overall_delta >= 10:
                st.success(f"🌟 **Outstanding Growth:** {traj_label}. Student shows consistent improvement in analytical understanding.")
            elif overall_delta <= -8:
                st.error(f"🚨 **Urgent Alert:** {traj_label}. Student is experiencing a marked decline in performance. Immediate mentor counseling recommended.")
            else:
                st.info(f"ℹ️ **Trajectory Status:** {traj_label}.")

            # Progress Trend Chart
            t_chart_col1, t_chart_col2 = st.columns([1.5, 1])
            with t_chart_col1:
                st.subheader("📈 Examination Progress Trendline")
                fig_trend = plot_progress_trend(exam_hist, student_name=progress_data["student_name"])
                st.pyplot(fig_trend)

            with t_chart_col2:
                st.subheader("📋 Exam-over-Exam History")
                hist_display = []
                for eh in exam_hist:
                    d_str = f"{eh.get('delta_from_previous', 0):+.1f}%" if eh != exam_hist[0] else "Baseline"
                    hist_display.append({
                        "Examination": eh["exam_name"],
                        "Aggregate %": f"{eh['percentage']:.1f}%",
                        "Grade": eh["grade"],
                        "Delta": d_str,
                        "Weak Subjects": eh["weak_count"]
                    })
                st.dataframe(pd.DataFrame(hist_display), use_container_width=True, hide_index=True)

            # Subject-wise Trajectory Table
            st.markdown("<br/>", unsafe_allow_html=True)
            st.subheader("🔍 Subject-by-Subject Evolution Across Examinations")
            if not progress_data["pivot_table"].empty:
                st.dataframe(progress_data["pivot_table"], use_container_width=True, hide_index=True)


# ============================================================================
# MODULE 7: INDIVIDUAL PROGRESS REPORTS (PDF GENERATION)
# ============================================================================

elif menu_option == "📄 Individual Progress Reports":
    st.markdown("""
    <div class="app-header">
        <h1>📄 Downloadable Academic Progress Reports</h1>
        <p>Generate publication-quality official PDF progress reports with embedded performance charts and advice.</p>
    </div>
    """, unsafe_allow_html=True)

    if marks_df.empty:
        st.info("No student marks available to generate reports.")
    else:
        rep_col1, rep_col2 = st.columns(2)
        with rep_col1:
            st_map_rep = {f"{r['student_id']} - {r['name']} ({r['department']})": r["student_id"] for _, r in students_df.iterrows()}
            sel_st_rep = st.selectbox("Select Student:", list(st_map_rep.keys()), key="pdf_st_select")
            rep_st_id = st_map_rep[sel_st_rep]

        # Available exams for this student
        st_avail_exams = marks_df[marks_df["student_id"] == rep_st_id][["exam_id", "exam_name", "academic_year"]].drop_duplicates()
        if st_avail_exams.empty:
            st.warning("No examination marks found for this student.")
        else:
            with rep_col2:
                ex_map_rep = {f"{r['exam_name']} ({r['academic_year']})": r["exam_id"] for _, r in st_avail_exams.iterrows()}
                sel_ex_rep = st.selectbox("Select Examination:", list(ex_map_rep.keys()), key="pdf_ex_select")
                rep_exam_id = ex_map_rep[sel_ex_rep]

            # Institution custom branding options
            with st.expander("⚙️ Customize Report Header & Institution Details"):
                inst_title = st.text_input("Institution Name:", value="NATIONAL INSTITUTE OF HIGHER EDUCATION")
                dept_label = st.text_input("Department / Center Heading:", value="Office of Academic Evaluation & Progress Monitoring")

            # Evaluate Student
            eval_data = evaluate_student_exam_performance(marks_df, rep_st_id, rep_exam_id)
            track_data = track_student_progress(marks_df, rep_st_id)

            # Live Preview Section
            st.markdown("---")
            st.subheader(f"📑 Live Report Preview: {eval_data['student_name']} ({rep_st_id})")

            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Student ID", eval_data["student_id"])
            p2.metric("Department", eval_data["department"])
            p3.metric("Aggregate Score", f"{eval_data['overall_percentage']:.1f}%")
            p4.metric("Awarded Grade", eval_data["overall_grade"])

            st.write(f"**Academic Standing:** `{eval_data['standing']}`")
            if eval_data["weak_subjects"]:
                st.warning(f"⚠️ **Weak Subjects Detected ({len(eval_data['weak_subjects'])}):** {', '.join([w['subject_name'] for w in eval_data['weak_subjects']])}")
            else:
                st.success("✅ **Clear Pass:** All registered subjects passed with no weak areas.")

            # Generation Button
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🖨️ Generate Official PDF Progress Report", type="primary", use_container_width=True):
                with st.spinner("Compiling academic data, rendering matplotlib charts, and building ReportLab PDF..."):
                    pdf_buffer = generate_student_pdf_report(
                        student_eval=eval_data,
                        progress_tracking=track_data,
                        institution_name=inst_title,
                        department_label=dept_label
                    )
                    pdf_bytes = pdf_buffer.getvalue()

                file_clean_exam = eval_data["exam_name"].replace(" ", "_")
                pdf_filename = f"Progress_Report_{rep_st_id}_{file_clean_exam}.pdf"

                st.success(f"🎉 PDF Report successfully generated! ({len(pdf_bytes):,} bytes)")
                st.download_button(
                    label=f"📥 Download {pdf_filename}",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )


# ============================================================================
# MODULE 8: DATABASE & SETTINGS
# ============================================================================

elif menu_option == "⚙️ Database & Settings":
    st.markdown("""
    <div class="app-header">
        <h1>⚙️ System Administration & Database Tools</h1>
        <p>Manage SQLite database storage, restore sample testing cohorts, and view system specifications.</p>
    </div>
    """, unsafe_allow_html=True)

    db_col1, db_col2 = st.columns(2)

    with db_col1:
        st.subheader("📦 Database Storage Statistics")
        current_stats = get_db_stats()
        st.write(f"• **Database Location:** `{DEFAULT_DB_PATH}`")
        st.write(f"• **Registered Students:** `{current_stats['students']}`")
        st.write(f"• **Academic Subjects:** `{current_stats['subjects']}`")
        st.write(f"• **Examination Cycles:** `{current_stats['exams']}`")
        st.write(f"• **Total Marks Recorded:** `{current_stats['marks_records']}`")

        st.markdown("<br/>", unsafe_allow_html=True)
        st.subheader("🌱 Seed Sample Academic Records")
        st.caption("Populates the database with 13 students, 13 subjects, and 3 consecutive examinations (Midterm 1, Midterm 2, Final Exam) with realistic performance variations.")
        if st.button("🌱 Populate Sample Test Data", type="primary", use_container_width=True):
            res = seed_database(verbose=False)
            st.success(f"Seeded {res['students']} students, {res['subjects']} subjects, and {res['marks']} marks!")
            refresh_db()
            st.rerun()

    with db_col2:
        st.subheader("⚠️ Database Reset & Danger Zone")
        st.caption("Permanently clears all database records and reinitializes empty SQLite tables.")
        confirm_reset = st.checkbox("I confirm that I want to completely erase the database.")
        if st.button("🚨 Reset Database to Empty", disabled=not confirm_reset, type="secondary", use_container_width=True):
            reset_database()
            st.success("Database has been reset to an empty state.")
            refresh_db()
            st.rerun()

        st.markdown("<br/>", unsafe_allow_html=True)
        st.subheader("ℹ️ Technology Stack & Architecture")
        st.markdown("""
        - **Backend:** Python 3.14
        - **Frontend:** Streamlit 1.67.0
        - **Database:** SQLite 3 (ACID compliant, relational schema)
        - **Analytics Engine:** Pandas 3.1.1 & NumPy 2.5.4
        - **Visualizations:** Matplotlib 3.11.2 (Agg headless renderer)
        - **PDF Generation:** ReportLab 5.1.0 (Platypus flowables & tables)
        """)
