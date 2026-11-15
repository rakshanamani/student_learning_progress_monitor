"""
Performance Visualization Module using Matplotlib.
Generates clean, professional charts for the Streamlit dashboard and PDF reports.
"""

import io
import os
import tempfile
from typing import List, Dict, Any, Optional

# Set temporary config dir for matplotlib to avoid permission warnings on Windows
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_cache"))

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend safe for web apps and multi-threading
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# Set global clean typography and styles
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "axes.labelweight": "medium",
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.autolayout": True,
})


def plot_subject_performance_bar(subjects: List[Dict[str, Any]], title: str = "Subject-Wise Academic Performance") -> plt.Figure:
    """
    Renders a vertical bar chart of subject scores with a 40% passing benchmark line
    and color-coded bars indicating performance tier.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)

    if not subjects:
        ax.text(0.5, 0.5, "No subject data available", ha="center", va="center", color="#6B7280", fontsize=12)
        ax.set_axis_off()
        return fig

    labels = [s.get("subject_name", s.get("subject_code", "")) for s in subjects]
    # Truncate long subject names for readable axis
    short_labels = [label[:18] + "..." if len(label) > 18 else label for label in labels]
    percentages = [float(s.get("percentage", 0.0)) for s in subjects]

    # Color mapping: Red for <40%, Amber for 40-59%, Blue for 60-74%, Green for >=75%
    colors = []
    for p in percentages:
        if p < 40.0:
            colors.append("#EF4444")  # Red: Weak
        elif p < 60.0:
            colors.append("#F59E0B")  # Amber: Pass/Average
        elif p < 75.0:
            colors.append("#3B82F6")  # Blue: Good
        else:
            colors.append("#10B981")  # Emerald: Distinction

    bars = ax.bar(range(len(short_labels)), percentages, color=colors, width=0.55, edgecolor="#1F2937", linewidth=0.8, zorder=3)

    # 40% Passing Threshold Line
    ax.axhline(y=40.0, color="#DC2626", linestyle="--", linewidth=1.5, zorder=4, label="Passing Mark (40%)")

    # Add data labels on top of bars
    for bar, pct in zip(bars, percentages):
        yval = bar.get_height()
        ax.annotate(
            f"{pct:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, yval),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#1F2937"
        )

    ax.set_xticks(range(len(short_labels)))
    ax.set_xticklabels(short_labels, rotation=20, ha="right")
    ax.set_ylim(0, max(105, max(percentages) + 12 if percentages else 100))
    ax.set_ylabel("Marks / Percentage (%)")
    ax.set_title(title, pad=12)
    ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", frameon=True, facecolor="#F9FAFB", edgecolor="#E5E7EB")

    # Clean borders
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    return fig


def plot_progress_trend(exam_history: List[Dict[str, Any]], student_name: str = "Student") -> plt.Figure:
    """
    Renders an exam-over-exam progress trendline showing trajectory across multiple examinations.
    """
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=100)

    if not exam_history or len(exam_history) == 0:
        ax.text(0.5, 0.5, "No multi-exam history available", ha="center", va="center", color="#6B7280", fontsize=12)
        ax.set_axis_off()
        return fig

    exam_names = [e["exam_name"] for e in exam_history]
    percentages = [float(e["percentage"]) for e in exam_history]
    x_indices = list(range(len(exam_names)))

    # Determine trend color
    if len(percentages) > 1:
        delta = percentages[-1] - percentages[0]
        line_color = "#10B981" if delta > 0 else ("#EF4444" if delta < 0 else "#3B82F6")
    else:
        line_color = "#3B82F6"

    # Line plot with markers
    ax.plot(x_indices, percentages, color=line_color, marker="o", markersize=8, linewidth=2.5,
            label=f"Overall % ({student_name})", zorder=4)

    # Shaded fill under line
    ax.fill_between(x_indices, percentages, alpha=0.15, color=line_color, zorder=2)

    # 40% Pass threshold
    ax.axhline(y=40.0, color="#DC2626", linestyle="--", linewidth=1.2, alpha=0.8, label="Pass Mark (40%)", zorder=3)

    # Annotate points with values and delta badges
    for i, (x, y) in enumerate(zip(x_indices, percentages)):
        annotation_text = f"{y:.1f}%"
        if i > 0:
            diff = y - percentages[i-1]
            sign = "+" if diff >= 0 else ""
            annotation_text += f"\n({sign}{diff:.1f}%)"
            
        ax.annotate(
            annotation_text,
            xy=(x, y),
            xytext=(0, 10 if y < 90 else -25),
            textcoords="offset points",
            ha="center", va="center",
            fontsize=9,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#D1D5DB", alpha=0.9),
            zorder=5
        )

    ax.set_xticks(x_indices)
    ax.set_xticklabels(exam_names, rotation=10, ha="right")
    ax.set_ylim(max(0, min(percentages) - 15), min(105, max(percentages) + 15))
    ax.set_ylabel("Overall Percentage (%)")
    ax.set_title(f"Academic Progress Trajectory - {student_name}", pad=14)
    ax.grid(True, linestyle=":", alpha=0.5, zorder=1)
    ax.legend(loc="lower right", frameon=True, facecolor="#F9FAFB")

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    return fig


def plot_grade_distribution_donut(grade_counts: Dict[str, int], title: str = "Batch Grade Distribution") -> plt.Figure:
    """
    Renders an elegant donut chart of grade distributions.
    """
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)

    # Filter out grades with 0 count for a clean donut
    filtered = {g: count for g, count in grade_counts.items() if count > 0}

    if not filtered:
        ax.text(0.5, 0.5, "No grade records to display", ha="center", va="center", color="#6B7280", fontsize=12)
        ax.set_axis_off()
        return fig

    labels = list(filtered.keys())
    sizes = list(filtered.values())

    palette_map = {
        "A+": "#10B981",
        "A":  "#34D399",
        "B":  "#3B82F6",
        "C":  "#6366F1",
        "D":  "#F59E0B",
        "E":  "#FB923C",
        "F":  "#EF4444"
    }
    colors = [palette_map.get(lbl, "#9CA3AF") for lbl in labels]

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        pctdistance=0.75,
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.42, edgecolor="#FFFFFF", linewidth=2)
    )

    for at in autotexts:
        at.set_fontsize(8.5)
        at.set_fontweight("bold")
        at.set_color("#1F2937")

    # Center circle for donut aesthetic
    ax.set_title(title, pad=15)
    ax.axis("equal")

    return fig


def plot_subject_class_comparison(subject_stats_df: pd.DataFrame) -> plt.Figure:
    """
    Renders a multi-bar chart comparing class average, highest, and lowest score per subject.
    """
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=100)

    if subject_stats_df.empty:
        ax.text(0.5, 0.5, "No subject statistics available", ha="center", va="center", color="#6B7280", fontsize=12)
        ax.set_axis_off()
        return fig

    subjects = subject_stats_df["subject_name"].apply(lambda s: s[:16] + ".." if len(s) > 16 else s).tolist()
    x = np.arange(len(subjects))
    width = 0.25

    avg_vals = subject_stats_df["average_percentage"].tolist()
    max_vals = subject_stats_df["max_percentage"].tolist()
    min_vals = subject_stats_df["min_percentage"].tolist()

    rects1 = ax.bar(x - width, min_vals, width, label="Lowest %", color="#EF4444", alpha=0.85)
    rects2 = ax.bar(x, avg_vals, width, label="Class Average %", color="#3B82F6")
    rects3 = ax.bar(x + width, max_vals, width, label="Highest %", color="#10B981", alpha=0.85)

    ax.axhline(y=40.0, color="#DC2626", linestyle=":", linewidth=1.2, label="Pass Mark (40%)")

    ax.set_ylabel("Percentage (%)")
    ax.set_title("Subject Benchmark Comparison (Min / Avg / Max)", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(subjects, rotation=15, ha="right")
    ax.set_ylim(0, 110)
    ax.legend(loc="upper right", frameon=True, facecolor="#F9FAFB")
    ax.grid(axis="y", linestyle=":", alpha=0.5)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    return fig


def fig_to_image_bytes(fig: plt.Figure) -> io.BytesIO:
    """
    Exports a Matplotlib figure as a PNG byte buffer for ReportLab PDF insertion or web downloads.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=180)
    buf.seek(0)
    plt.close(fig)
    return buf
