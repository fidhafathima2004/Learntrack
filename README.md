# 🎓 LearnTrack — Smart Syllabus Tracker & Study Assistant

**LearnTrack** is an intelligent academic tracking web application developed with Django. It bridges the gap between static course syllabi and active student preparation by automatically parsing uploaded syllabus PDFs, structuring them into modules and topics, generating tailored day-by-day study schedules, and providing interactive MCQ quizzes with automated progress scoring.

---

## 🌟 Key Features

- **Automated Syllabus Extraction**: Upload syllabus documents in PDF format; LearnTrack utilizes `PyMuPDF` (`fitz`) and regex engines to parse modules, headings, and topic lists automatically.
- **Dynamic Study Planner**: Students can input target exam dates and daily study hours; the system computes a balanced study schedule covering all modules before the exam.
- **Interactive MCQ Assessment**: Module-specific multiple-choice quizzes with instant auto-grading, tracking pass/fail status and progress metrics.
- **Dual Role Dashboards**:
  - **Student Dashboard**: Real-time study schedule timeline, pending modules, quiz scores, and course completion status.
  - **Admin Dashboard**: Comprehensive analytics on total syllabi uploaded, active modules, question banks, and registered students.
- **Responsive UI/UX**: Custom responsive design system featuring sleek glassmorphic components, status badges, and smooth interactive elements.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python / [Django](https://www.djangoproject.com/)
- **PDF Processing**: [PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/)
- **Database**: SQLite3
- **Frontend**: HTML5, Modern CSS3 (Glassmorphism & Flex/Grid), Vanilla JavaScript
- **Version Control**: Git & GitHub

---

## 📂 Project Structure

```text
learntrack/
├── core/                       # Main application logic
│   ├── migrations/             # Database migration files
│   ├── admin.py                # Django admin registration
│   ├── apps.py                 # App configuration
│   ├── models.py               # Syllabus, Module, StudyPlan, MCQ, ModuleProgress
│   ├── tests.py                # Unit test suites
│   ├── urls.py                 # Core routing endpoints
│   └── views.py                # Auth, PDF parsing, dashboard, and quiz logic
├── learntrack/                 # Project configuration directory
│   ├── asgi.py
│   ├── settings.py             # Settings, static/media configuration
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py
├── static/                     # Static assets
│   ├── style.css               # Design system and layout styles
│   └── script.js               # Client-side scripts
├── templates/                  # Frontend templates
│   ├── base.html               # Base layout with navbar
│   ├── login.html              # User login
│   ├── register.html           # User registration
│   ├── dashboard.html          # Student dashboard & schedule
│   ├── admin_dashboard.html    # Admin analytics dashboard
│   ├── upload_syllabus.html    # Syllabus PDF upload
│   ├── syllabus.html           # Module and topic breakdown
│   ├── create_study_plan.html  # Exam date & hours configuration
│   ├── add_mcq.html            # Teacher question creation
│   └── question_bank.html      # Question repository
├── uploads/                    # Uploaded syllabus files
├── db.sqlite3                  # Application database
├── manage.py                   # Django CLI utility
├── requirements.txt            # Dependency list
└── README.md                   # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python installed (Python 3.10+ recommended).

### 2. Installation

Clone the repository and navigate to the project root:
```bash
git clone https://github.com/<username>/learntrack.git
cd learntrack
```

Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Setup & Run
Apply migrations:
```bash
python manage.py migrate
```

Run the development server:
```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 👤 Author
- **Fidha Fathima** — [fidhafathimapp13@gmail.com](mailto:fidhafathimapp13@gmail.com)
