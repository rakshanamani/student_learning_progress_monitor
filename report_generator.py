"""
PDF Progress Report Generator using ReportLab.
Produces comprehensive, publication-quality academic progress reports with
student profiles, subject marks, grades, embedded matplotlib charts, weak subject alerts,
pedagogical improvement plans, and formal signature blocks.
"""

import io
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)

from analytics import evaluate_student_exam_performance, track_student_progress
from visualizations import plot_subject_performance_bar, fig_to_image_bytes


def generate_student_pdf_report(
    student_eval: Dict[str, Any],
    progress_tracking: Optional[Dict[str, Any]] = None,
    institution_name: str = "NATIONAL INSTITUTE OF HIGHER EDUCATION",
    department_label: str = "Office of Academic Evaluation & Progress Monitoring"
) -> io.BytesIO:
    """
    Builds a professional multi-section PDF progress report and returns a BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "InstTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1  # Center
    )
    subtitle_style = ParagraphStyle(
        "InstSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4B5563"),
        alignment=1
    )
    doc_heading = ParagraphStyle(
        "DocHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#111827"),
        alignment=1
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1E3A8A")
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1F2937")
    )
    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#111827")
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1F2937")
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#111827")
    )
    alert_text = ParagraphStyle(
        "AlertText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#7F1D1D")
    )

    # 1. INSTITUTION HEADER BAR
    story.append(Paragraph(institution_name, title_style))
    story.append(Paragraph(department_label, subtitle_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("OFFICIAL STUDENT ACADEMIC PROGRESS REPORT", doc_heading))
    story.append(Spacer(1, 8))

    # 2. STUDENT PROFILE & EXAMINATION METADATA
    report_date = datetime.now().strftime("%B %d, %Y")
    profile_data = [
        [
            Paragraph("<b>Student ID:</b>", body_style),
            Paragraph(student_eval.get("student_id", "N/A"), body_bold),
            Paragraph("<b>Examination:</b>", body_style),
            Paragraph(student_eval.get("exam_name", "N/A"), body_bold),
        ],
        [
            Paragraph("<b>Student Name:</b>", body_style),
            Paragraph(student_eval.get("student_name", "N/A"), body_bold),
            Paragraph("<b>Academic Year:</b>", body_style),
            Paragraph(student_eval.get("academic_year", "N/A"), body_bold),
        ],
        [
            Paragraph("<b>Department:</b>", body_style),
            Paragraph(student_eval.get("department", "N/A"), body_bold),
            Paragraph("<b>Semester:</b>", body_style),
            Paragraph(f"Semester {student_eval.get('semester', 'N/A')}", body_bold),
        ],
        [
            Paragraph("<b>Email:</b>", body_style),
            Paragraph(student_eval.get("email", "Not provided"), body_style),
            Paragraph("<b>Report Generated:</b>", body_style),
            Paragraph(report_date, body_style),
        ]
    ]

    profile_table = Table(profile_data, colWidths=[1.1*inch, 2.3*inch, 1.3*inch, 2.3*inch])
    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 10))

    # 3. EXECUTIVE PERFORMANCE SCORECARD
    total_obt = student_eval.get("total_obtained", 0)
    total_max = student_eval.get("total_max", 0)
    ovr_pct = student_eval.get("overall_percentage", 0)
    ovr_grade = student_eval.get("overall_grade", "N/A")
    standing = student_eval.get("standing", "N/A")
    passed_cnt = student_eval.get("passed_subject_count", 0)
    failed_cnt = student_eval.get("failed_subject_count", 0)

    scorecard_data = [
        [
            Paragraph("<b>Total Score</b>", subtitle_style),
            Paragraph("<b>Aggregate %</b>", subtitle_style),
            Paragraph("<b>Final Grade</b>", subtitle_style),
            Paragraph("<b>Passed / Total</b>", subtitle_style),
            Paragraph("<b>Academic Standing</b>", subtitle_style),
        ],
        [
            Paragraph(f"<b>{total_obt:.1f} / {total_max:.0f}</b>", doc_heading),
            Paragraph(f"<b>{ovr_pct:.1f}%</b>", doc_heading),
            Paragraph(f"<b>{ovr_grade}</b>", doc_heading),
            Paragraph(f"<b>{passed_cnt} / {passed_cnt + failed_cnt}</b>", doc_heading),
            Paragraph(f"<b>{standing}</b>", body_bold),
        ]
    ]

    # Color background depending on fail count
    sc_bg = colors.HexColor("#EFF6FF") if failed_cnt == 0 else colors.HexColor("#FEF2F2")
    sc_border = colors.HexColor("#3B82F6") if failed_cnt == 0 else colors.HexColor("#EF4444")

    scorecard_table = Table(scorecard_data, colWidths=[1.3*inch, 1.3*inch, 1.1*inch, 1.3*inch, 2.0*inch])
    scorecard_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), sc_bg),
        ("BOX", (0, 0), (-1, -1), 1, sc_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(scorecard_table)
    story.append(Spacer(1, 10))

    # 4. DETAILED SUBJECT-WISE PERFORMANCE TABLE
    story.append(Paragraph("1. Subject-Wise Performance Breakdown", section_heading))
    story.append(Spacer(1, 4))

    table_headers = [
        Paragraph("<b>Code</b>", table_cell_bold),
        Paragraph("<b>Subject Name</b>", table_cell_bold),
        Paragraph("<b>Credits</b>", table_cell_bold),
        Paragraph("<b>Max Marks</b>", table_cell_bold),
        Paragraph("<b>Obtained</b>", table_cell_bold),
        Paragraph("<b>Percentage</b>", table_cell_bold),
        Paragraph("<b>Grade</b>", table_cell_bold),
        Paragraph("<b>Status</b>", table_cell_bold),
    ]
    marks_table_rows = [table_headers]

    for s in student_eval.get("subjects", []):
        is_weak = s.get("is_weak", False)
        status_text = "PASS" if not is_weak else "FAIL / WEAK"
        status_color = "#10B981" if not is_weak else "#DC2626"

        row = [
            Paragraph(s.get("subject_code", ""), table_cell),
            Paragraph(s.get("subject_name", ""), table_cell),
            Paragraph(str(s.get("credits", 3)), table_cell),
            Paragraph(f"{s.get('max_marks', 100):.0f}", table_cell),
            Paragraph(f"{s.get('marks_obtained', 0):.1f}", table_cell_bold),
            Paragraph(f"{s.get('percentage', 0):.1f}%", table_cell_bold),
            Paragraph(s.get("grade", "N/A"), table_cell_bold),
            Paragraph(f"<font color='{status_color}'><b>{status_text}</b></font>", table_cell),
        ]
        marks_table_rows.append(row)

    marks_table = Table(
        marks_table_rows,
        colWidths=[0.8*inch, 2.3*inch, 0.6*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.9*inch]
    )
    marks_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ]))
    # Highlight header text white
    for col_idx in range(len(table_headers)):
        marks_table.setStyle(TableStyle([
            ("TEXTCOLOR", (col_idx, 0), (col_idx, 0), colors.white)
        ]))
    story.append(marks_table)
    story.append(Spacer(1, 8))

    # 5. EMBEDDED VISUALIZATION CHART
    try:
        fig = plot_subject_performance_bar(
            student_eval.get("subjects", []),
            title=f"Performance by Subject - {student_eval.get('exam_name', '')}"
        )
        img_buf = fig_to_image_bytes(fig)
        img = Image(img_buf, width=6.8*inch, height=2.4*inch)
        story.append(KeepTogether([
            Paragraph("2. Performance Visualization Chart", section_heading),
            Spacer(1, 4),
            img,
            Spacer(1, 8)
        ]))
    except Exception as e:
        story.append(Paragraph(f"<i>(Chart rendering skipped: {str(e)})</i>", body_style))

    # 6. IDENTIFIED WEAK SUBJECTS & PEDAGOGICAL RECOMMENDATIONS
    weak_subs = student_eval.get("weak_subjects", [])
    if weak_subs:
        weak_content = [
            Paragraph("3. Identified Weak Subjects (< 40%) & Action Plan for Improvement", section_heading),
            Spacer(1, 4)
        ]
        
        weak_table_rows = [
            [
                Paragraph("<b>Subject</b>", table_cell_bold),
                Paragraph("<b>Score</b>", table_cell_bold),
                Paragraph("<b>Targeted Improvement Recommendation & Diagnostic Advice</b>", table_cell_bold)
            ]
        ]
        for w in weak_subs:
            weak_table_rows.append([
                Paragraph(f"<b>{w['subject_name']}</b><br/>({w['subject_code']})", table_cell),
                Paragraph(f"<font color='#DC2626'><b>{w['percentage']:.1f}%</b></font><br/>({w['marks']})", table_cell),
                Paragraph(w["recommendation"], alert_text)
            ])

        weak_table = Table(weak_table_rows, colWidths=[1.8*inch, 0.9*inch, 4.3*inch])
        weak_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FEE2E2")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFF5F5")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#EF4444")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FCA5A5")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        weak_content.append(weak_table)
        weak_content.append(Spacer(1, 8))
        story.append(KeepTogether(weak_content))
    else:
        strong_subs = student_eval.get("strong_subjects", [])
        praise_text = "<b>Commendation:</b> The student has passed all registered subjects successfully with zero weak areas detected."
        if strong_subs:
            praise_text += f" Exceptional mastery demonstrated in: <i>{', '.join([s['subject_name'] for s in strong_subs])}</i>."
        story.append(KeepTogether([
            Paragraph("3. Academic Strengths & Commendations", section_heading),
            Spacer(1, 4),
            Table(
                [[Paragraph(praise_text, body_style)]],
                colWidths=[7.0*inch],
                style=[
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#10B981")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            ),
            Spacer(1, 8)
        ]))

    # 7. MULTI-EXAM PROGRESS COMPARISON (If available)
    if progress_tracking and progress_tracking.get("has_data") and len(progress_tracking.get("exam_history", [])) > 1:
        prog_rows = [
            [
                Paragraph("<b>Examination</b>", table_cell_bold),
                Paragraph("<b>Total Score</b>", table_cell_bold),
                Paragraph("<b>Percentage</b>", table_cell_bold),
                Paragraph("<b>Grade</b>", table_cell_bold),
                Paragraph("<b>Delta (Change)</b>", table_cell_bold),
                Paragraph("<b>Weak Subjects</b>", table_cell_bold),
            ]
        ]
        for eh in progress_tracking.get("exam_history", []):
            d_val = eh.get("delta_from_previous", 0.0)
            sign = "+" if d_val > 0 else ""
            delta_color = "#10B981" if d_val > 0 else ("#EF4444" if d_val < 0 else "#6B7280")
            delta_str = f"<font color='{delta_color}'><b>{sign}{d_val:.1f}%</b></font>" if eh != progress_tracking["exam_history"][0] else "<i>Baseline</i>"

            prog_rows.append([
                Paragraph(eh.get("exam_name", ""), table_cell),
                Paragraph(f"{eh.get('total_obtained', 0):.0f} / {eh.get('total_max', 0):.0f}", table_cell),
                Paragraph(f"<b>{eh.get('percentage', 0):.1f}%</b>", table_cell_bold),
                Paragraph(eh.get("grade", "N/A"), table_cell_bold),
                Paragraph(delta_str, table_cell),
                Paragraph(str(eh.get("weak_count", 0)), table_cell),
            ])

        prog_table = Table(prog_rows, colWidths=[2.2*inch, 1.2*inch, 1.0*inch, 0.8*inch, 1.0*inch, 0.8*inch])
        prog_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ]))

        traj_label = progress_tracking.get("trajectory_label", "")
        traj_color = progress_tracking.get("trajectory_color", "#1E3A8A")

        story.append(KeepTogether([
            Paragraph("4. Academic Progress Trajectory Across Examinations", section_heading),
            Spacer(1, 3),
            Paragraph(f"<b>Trajectory Assessment:</b> <font color='{traj_color}'>{traj_label}</font>", body_style),
            Spacer(1, 3),
            prog_table,
            Spacer(1, 8)
        ]))

    # 8. SIGNATURE & VERIFICATION BLOCK
    sig_data = [
        [
            Paragraph("<b>Class Advisor / Mentor</b><br/><br/><br/>___________________________<br/>Signature & Date", body_style),
            Paragraph("<b>Academic Dean / HoD</b><br/><br/><br/>___________________________<br/>Signature & Seal", body_style),
            Paragraph("<b>Parent / Student Acknowledgement</b><br/><br/><br/>___________________________<br/>Signature & Date", body_style),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[2.3*inch, 2.3*inch, 2.4*inch])
    sig_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    story.append(KeepTogether([
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#94A3B8"), spaceBefore=2, spaceAfter=6),
        sig_table,
        Spacer(1, 4),
        Paragraph("<font color='#6B7280' size='7'>This academic report is computer-generated by the Student Learning Progress Monitor. Any unauthorized alterations render it invalid.</font>", subtitle_style)
    ]))

    # Build the document
    doc.build(story)
    buffer.seek(0)
    return buffer
