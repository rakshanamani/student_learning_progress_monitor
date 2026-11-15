# 🎓 Student Learning Progress Monitor

An enterprise-grade, Python-based academic record management, learning analytics, progress tracking, and automated PDF reporting application built with **Streamlit**, **SQLite**, **Pandas**, **Matplotlib**, and **ReportLab**.

---

## 🌟 Key Features & Modules

### 1. 📊 Interactive Dashboard & Overview
- **Executive KPIs:** Real-time summary cards for Total Students, Cohort Average Percentage, Pass Rate (%), and At-Risk Student Counts.
- **Visual Analytics:**
  - **Grade Distribution Donut Chart:** Visual breakdown across grades (`A+`, `A`, `B`, `C`, `D`, `E`, `F`).
  - **Subject Benchmark Comparison Bar Chart:** Class-level comparison of Minimum, Average, and Maximum scores per subject.
- **Cohort Filter:** Instantly filter dashboard insights by Department, Semester, and Examination cycle.
- **Subject-Wise Summary Table:** Enrolled student count, passing rates, and count of weak students per subject.

### 2. 👨‍🎓 Student Management System
- **View & Filter:** Searchable, interactive roster filterable by Department and Semester, with instant CSV export.
- **Add New Student:** Form validation for Student ID, Full Name, Department, Semester, Email, and Contact.
- **Update Student:** Edit existing student details with pre-populated fields and immediate database updates.
- **Delete Student:** Permanent record removal with safety confirmation and cascading deletion of associated marks.

### 3. 📝 Academic Records (Marks Entry)
- **Single Student Marks Entry:** Select student and exam to load their department-specific subjects and enter/update marks out of 100.
- **Class Batch Marks Entry:** Enter marks for an entire class cohort simultaneously for a specific subject and exam.
- **Marks Directory:** Filter, inspect, and delete individual marks records.
- **Exam & Subject Management:** Define new examination cycles (Midterm 1, Midterm 2, Final Exam) and add subjects with credit allocations.

### 4. 📈 Individual Performance Analysis
- **Comprehensive Scorecard:** Total marks obtained, overall weighted percentage, awarded letter grade, and passing status.
- **Class Benchmark Delta:** Computes deviation from the class mean (e.g. `+12.4% above average`).
- **Subject-Wise Breakdown:** Color-coded status badges, credits, and grades.
- **Matplotlib Benchmark Chart:** Vertical bar chart highlighting student scores against the **40% Passing Benchmark line**.
- **Strengths & Weaknesses:** Automated recognition of distinctions (≥ 75%) and remedial areas (< 40%).

### 5. ⚠️ Weak Subject Identification & Early Intervention
- **Automated Detection:** Immediately identifies all subjects where a student scored below the 40% threshold.
- **Pedagogical Recommendation Engine:** Context-aware remedial action plans tailored to the subject domain:
  - *Mathematics / Calculus:* Problem derivation drills, step-by-step problem sets, tutorial sessions.
  - *Programming / DSA:* Hands-on coding exercises, algorithm trace dry-runs, code reviews.
  - *Database / SQL:* Relational schema normalization, live SQL query practice.
  - *Systems / Networks:* Concept mind-mapping, protocol flowcharts, past-paper analysis.
- **Remedial Export:** One-click CSV export of all at-risk students for academic counseling teams.

### 6. 🚀 Multi-Exam Academic Progress Tracking
- **Cross-Examination Comparison:** Evaluates student trajectory across multiple examination cycles (e.g. *Midterm 1* ➔ *Midterm 2* ➔ *Semester End Exam*).
- **Trajectory Classification:** Automatically flags trends such as *Substantial Academic Improvement*, *Stable Performance*, or *Severe Performance Decline*.
- **Visual Progress Trendline:** Matplotlib line chart with shaded confidence region, data callouts, and exam-over-exam percentage change badges.
- **Subject Evolution Matrix:** Tabular comparison of each subject across all exams.

### 7. 📄 Individual Downloadable Progress Reports (PDF)
- **ReportLab PDF Engine:** Generates official, publication-quality academic progress reports.
- **Embedded Visualization:** Renders and embeds a crisp Matplotlib performance bar chart directly inside the PDF document.
- **Comprehensive Content:**
  - Formal Institutional Branding Header (customizable in UI).
  - Student Profile & Metadata Table.
  - Executive Scorecard & Academic Standing.
  - Detailed Subject-Wise Marks & Grades Table.
  - Identified Strengths and Commendations.
  - Weak Subjects Warning Box with Diagnostic Action Plan.
  - Multi-Exam Progress Comparison Table (when multi-exam history exists).
  - Formal Signature Block (Class Advisor, Head of Department, Parent).
- **Direct Download:** One-click download button in the web interface.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Language** | Python 3.10+ / 3.14 | Core business logic, data models, and services |
| **Frontend Framework** | Streamlit | Modern, reactive web interface with custom styling |
| **Database** | SQLite 3 | Embedded ACID-compliant relational storage (`progress_monitor.db`) |
| **Data Analytics** | Pandas & NumPy | Academic aggregation, statistics, and cohort metrics |
| **Visualizations** | Matplotlib | Professional charts with 40% passing benchmark annotations |
| **PDF Reporting** | ReportLab | Flowable Platypus PDF document generation with embedded charts |

---

## 📂 Project Structure

```
student_learning_progress_monitor/
│
├── app.py                  # Main Streamlit web application & UI modules
├── database.py             # SQLite schema, connection pool, and CRUD queries
├── seed_data.py            # Pre-configured realistic academic test dataset
├── analytics.py            # Grading scale, statistical metrics & recommendation engine
├── visualizations.py       # Matplotlib charting engine (bar, trendline, donut, benchmarks)
├── report_generator.py     # ReportLab PDF report builder with embedded charts
├── test_app.py             # Automated end-to-end test suite
├── requirements.txt        # Python package dependencies
├── progress_monitor.db     # SQLite database (auto-created and seeded)
└── README.md               # Project documentation & setup instructions
```

---

## 🚀 Windows Terminal Execution Instructions

### 1. Open Terminal
Open **PowerShell** or **Command Prompt (CMD)**.

### 2. Navigate to Project Directory
```powershell
cd C:\Users\raksh\.gemini\antigravity\scratch\student_learning_progress_monitor
```

### 3. Install Required Dependencies
Run the following command to install the required libraries:
```powershell
python -m pip install -r requirements.txt
```
*(Packages: `streamlit`, `pandas`, `matplotlib`, `reportlab`)*

### 4. (Optional) Run Automated Verification Tests
Run the standalone verification test suite to confirm database CRUD, analytics, charts, and PDF generation:
```powershell
python test_app.py
```

### 5. Launch the Streamlit Web Application
Run the Streamlit application:
```powershell
python -m streamlit run app.py
```

Upon executing this command, Streamlit will display:
```
  Local URL: http://localhost:8501
  Network URL: http://...
```
Open your web browser at **`http://localhost:8501`** to interact with the application.

---

## 🧪 Sample Test Data Guide

The application comes pre-seeded with **13 realistic student profiles** across 3 departments (*Computer Science*, *Electronics*, *Mechanical*) and **3 examination cycles** (*Midterm 1*, *Midterm 2*, *Semester End Exam*).

| Student ID | Student Name | Department | Key Scenario to Test |
| :--- | :--- | :--- | :--- |
| **`CS202401`** | Aarav Sharma | Computer Science | **Consistent Top Scorer:** Aggregate 89-95%, all grades `A+`/`A`, zero weak subjects. |
| **`CS202402`** | Priya Patel | Computer Science | **Remarkable Improvement:** Progresses from 58.0% ➔ 72.8% ➔ 85.4% (+27.4% delta). Perfect for **Progress Tracking**. |
| **`CS202403`** | Rohan Verma | Computer Science | **Weak Subject in Math:** Scored 32% in Midterm 1 & 36% in Midterm 2 in Discrete Math. Triggers **Weak Subject Advisor** and **PDF Report**. |
| **`CS202405`** | Vikram Singh | Computer Science | **Declining Student:** Drops from 75.4% ➔ 57.8% ➔ 44.4% (-31.0% delta) with fails in OS & Networks. |
| **`CS202407`** | Kabir Mehta | Computer Science | **Persistent Weakness:** Scored <40% across all exams in Data Structures. |
| **`EC202402`** | Tanvi Deshmukh | Electronics | **Analog Electronics Remedial:** Scored 35% in Analog Circuits with automated remedial advice. |
| **`ME202401`** | Rahul Chawla | Mechanical | **Thermodynamics Remedial:** Scored 33% in Thermodynamics. |

---

## 📄 Generating PDF Reports
1. In the sidebar, select **📄 Individual Progress Reports**.
2. Select any student (e.g. **`CS202403 - Rohan Verma`** or **`CS202402 - Priya Patel`**).
3. Select an examination cycle (e.g. **`Midterm Examination 1`**).
4. Review the on-screen live scorecard preview.
5. Click **🖨️ Generate Official PDF Progress Report**.
6. Click the generated **📥 Download Progress_Report_...pdf** button to save the complete official academic report.
