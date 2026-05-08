# ABC Learning Center Management System

A LAN-based Desktop Management System for ABC Learning Center.  
Final Project — CCS 2501: Systems Analysis and Design & CCS 2601: Programming with Databases  
Central Philippine University | College of Computer Studies | BS Computer Science 2 | S.Y. 2025–2026

---

## About the Project

ABC Learning Center is a privately owned tutorial and review center established in 2018,
offering academic assistance to Elementary and Senior High School students
with over 300 enrollees per term.

This system was developed to replace the center's existing manual, paper-based processes
with a centralized, digitalized solution. It handles student enrollment, attendance tracking,
grade recording, payment processing, and report generation — all within a
local area network (LAN) environment.

---

## System Type

LAN-based Desktop Application — accessible only from computers within the learning center.
No internet or remote access required.

---

## System Users

| Role          | Access |
|---------------|--------|
| Admin/Staff   | Register students, process payments, manage records, generate reports |
| Tutor         | Record attendance, submit grades, view student progress |
| Student/Parent| No system access — external entities only. Admin encodes their data. |

---

## Features

### Admin/Staff Modules
- Admin Login with credential verification
- Student Registration and Enrollment in Subjects
- Payment Processing and Digital Receipt Generation
- Student Records Management
- Outstanding Balance Monitoring
- Report Generation and Printing (Attendance, Grades, Payment)

### Tutor Modules
- Tutor Login with credential verification
- Attendance Recording (Present / Absent / Late)
- Grade Submission per Subject
- Student Progress and Attendance Summary Viewing

---

## Tech Stack

| Layer          | Technology     |
|----------------|----------------|
| Language       | Python 3       |
| UI Framework   | CustomTkinter  |
| Database       | SQLite         |
| IDE            | VS Code        |
| Version Control| Git + GitHub   |

---

## Database

The system uses SQLite as its database engine — lightweight, file-based,
and requires no separate server installation.
The database consists of 11 tables:

STUDENT, PARENT, STAFF, TUTOR, ENROLLMENT, DETAIL,
SUBJECT, ATTENDANCE, GRADE, PAYMENT, RECEIPT

---
---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone git@github-yakuvv:yakuvv/ABC-Learning-Center-Management-System.git

# 2. Navigate to the project
cd ABC-Learning-Center-Management-System

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

---

## System Design

The system was designed following the full systems analysis and design process including:

- Context Diagram and Level 0 DFD (Current System)
- Proposed Data Flow Diagram (Level 1)
- Entity Relationship Diagram (Crow's Foot Notation)
- Use Case Diagram
- Class Diagram
- Sequence Diagrams (Admin/Staff and Tutor)
- Activity Diagrams (5 modules)

---

## Course

- CCS 2501 — Systems Analysis and Design
- CCS 2601 — Programming with Databases

---

## License

This project is developed for academic purposes only.  
2026 Group 1 — Central Philippine University