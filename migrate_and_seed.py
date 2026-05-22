# migrate_and_seed.py
import sqlite3
import shutil
import os

DB_NAME = "abc_learning_center.db"
BACKUP_NAME = "abc_learning_center_backup.db"

def run_migration():
    print("=== ABC Learning Center Database Migration & Seeder ===")
    
    # 1. Create a safety backup
    if os.path.exists(DB_NAME):
        print(f"📦 Creating database backup: '{BACKUP_NAME}'...")
        shutil.copyfile(DB_NAME, BACKUP_NAME)
        print("✓ Backup created successfully.")
    else:
        print("❌ Error: 'abc_learning_center.db' not found!")
        return

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = OFF") # Disable foreign keys temporarily for restructure
    cursor = conn.cursor()

    try:
        # 2. Upgrade STUDENT table
        print("\n🔧 Upgrading 'STUDENT' table...")
        cursor.execute("PRAGMA table_info(STUDENT)")
        columns = [row[1] for row in cursor.fetchall()]
        if "levelType" not in columns:
            cursor.execute("ALTER TABLE STUDENT ADD COLUMN levelType TEXT")
            print("✓ Added 'levelType' column to STUDENT table.")
        else:
            print("• 'levelType' column already exists in STUDENT.")

        # 3. Recreate SUBJECT table to support new schema and clean curriculum
        print("\n🔧 Upgrading 'SUBJECT' table...")
        # Check if subject table structure matches the new schema
        cursor.execute("PRAGMA table_info(SUBJECT)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # We always drop and recreate the SUBJECT table to ensure a clean, updated curriculum
        cursor.execute("DROP TABLE IF EXISTS SUBJECT")
        cursor.execute('''
        CREATE TABLE SUBJECT (
            subjectID INTEGER PRIMARY KEY AUTOINCREMENT,
            subjectName TEXT NOT NULL,
            description TEXT,
            gradeLevel TEXT NOT NULL,
            strand TEXT,
            semester INTEGER,
            subjectType TEXT,
            termType TEXT,
            isActive INTEGER DEFAULT 1
        )''')
        print("✓ Recreated 'SUBJECT' table.")

        # 4. Recreate GRADE table to support 'quarter' and UNIQUE constraint
        print("\n🔧 Upgrading 'GRADE' table...")
        cursor.execute("DROP TABLE IF EXISTS GRADE")
        cursor.execute('''
        CREATE TABLE GRADE (
            gradeID INTEGER PRIMARY KEY AUTOINCREMENT,
            detailID INTEGER NOT NULL,
            tutorID INTEGER NOT NULL,
            quarter TEXT NOT NULL,
            gradeValue REAL NOT NULL,
            dateRecorded DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (detailID) REFERENCES DETAIL(detailID) ON DELETE CASCADE,
            FOREIGN KEY (tutorID) REFERENCES TUTOR(tutorID),
            UNIQUE(detailID, quarter) ON CONFLICT REPLACE
        )''')
        print("✓ Recreated 'GRADE' table with quarter tracking and unique constraints.")

        # 5. Seed subjects
        print("\n🌱 Seeding new subjects curriculum...")
        seed_subjects(cursor)

        conn.commit()
        print("\n🎉 Database migration and seeding successfully completed!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {e}")
        print("Database rolled back to original state.")
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


def seed_subjects(cursor):
    # Elementary: Grades 1 to 6
    # 7 subjects for the whole year (no strand, semester=None, subjectType=None)
    for g in range(1, 7):
        grade_str = f"Grade {g}"
        elem_subjects = [
            ("Mathematics", "Elementary Mathematics"),
            ("Science", "General Science"),
            ("English", "English Language Arts"),
            ("Filipino", "Wika at Panitikan"),
            ("Araling Panlipunan", "Social Studies / History"),
            ("MAPEH", "Music, Arts, Physical Education, and Health"),
            ("ESP", "Edukasyon sa Pagpapakatao")
        ]
        for name, desc in elem_subjects:
            cursor.execute("""
                INSERT INTO SUBJECT (subjectName, description, gradeLevel, strand, semester, subjectType, termType)
                VALUES (?, ?, ?, NULL, NULL, NULL, 'Quarter')
            """, (name, desc, grade_str))
            
    # High School: Grades 7 to 10
    # 9 subjects for the whole year
    for g in range(7, 11):
        grade_str = f"Grade {g}"
        hs_subjects = [
            ("Mathematics", "High School Mathematics"),
            ("English", "High School English"),
            ("Science", "General Science and Applied Technology"),
            ("Filipino", "Panitikan at Retorika"),
            ("Araling Panlipunan", "Kasaysayan at Lipunan"),
            ("MAPEH", "Music, Arts, Physical Education, and Health"),
            ("ESP", "Edukasyon sa Pagpapakatao"),
            ("TLE", "Technology and Livelihood Education"),
            ("Computer Education", "Introduction to Information and Communications Technology")
        ]
        for name, desc in hs_subjects:
            cursor.execute("""
                INSERT INTO SUBJECT (subjectName, description, gradeLevel, strand, semester, subjectType, termType)
                VALUES (?, ?, ?, NULL, NULL, NULL, 'Quarter')
            """, (name, desc, grade_str))

    # Senior High School: Grades 11 and 12
    # Strands: STEM, ABM, HUMSS
    # 6 subjects per semester per strand (4 major, 2 minor)
    shs_data = {
        "Grade 11": {
            "STEM": {
                1: {
                    "Major": [
                        ("Pre-Calculus", "Introductory calculus concepts and advanced algebra"),
                        ("General Chemistry 1", "Basic chemistry principles, atoms, and reactions"),
                        ("Earth Science", "Earth processes and planetary science"),
                        ("General Mathematics", "Core mathematical operations, functions, and models")
                    ],
                    "Minor": [
                        ("Oral Communication", "Public speaking and communicative strategies"),
                        ("Physical Education and Health 1", "Foundational physical fitness and wellness activities")
                    ]
                },
                2: {
                    "Major": [
                        ("Basic Calculus", "Limits, derivatives, integration, and applications"),
                        ("General Chemistry 2", "Advanced chemistry: thermodynamics and electrochemistry"),
                        ("Disaster Readiness and Risk Reduction", "Disaster management and geological hazards"),
                        ("Statistics and Probability", "Data analysis, distribution, and hypothesis testing")
                    ],
                    "Minor": [
                        ("Reading and Writing", "Critical reading and academic writing skills"),
                        ("Personal Development", "Self-exploration, mental health, and career preparation")
                    ]
                }
            },
            "ABM": {
                1: {
                    "Major": [
                        ("Organization and Management", "Business management principles and structures"),
                        ("Business Mathematics", "Financial math, interests, markups, and markdowns"),
                        ("Fundamentals of Accountancy, Business, and Management 1", "Basic accounting principles, journal, and ledger"),
                        ("General Mathematics", "Core mathematical operations, functions, and models")
                    ],
                    "Minor": [
                        ("Oral Communication", "Public speaking and communicative strategies"),
                        ("Physical Education and Health 1", "Foundational physical fitness and wellness activities")
                    ]
                },
                2: {
                    "Major": [
                        ("Business Ethics and Social Responsibility", "Ethics in business and corporate responsibility"),
                        ("Fundamentals of Accountancy, Business, and Management 2", "Financial statement analysis and accounting cycles"),
                        ("Applied Economics", "Economic theories, supply, demand, and markets"),
                        ("Statistics and Probability", "Data analysis, distribution, and hypothesis testing")
                    ],
                    "Minor": [
                        ("Reading and Writing", "Critical reading and academic writing skills"),
                        ("Personal Development", "Self-exploration, mental health, and career preparation")
                    ]
                }
            },
            "HUMSS": {
                1: {
                    "Major": [
                        ("Disciplines and Ideas in the Social Sciences", "Foundational theories and thinkers in social sciences"),
                        ("Creative Writing", "Fiction, poetry, drama composition techniques"),
                        ("Introduction to World Religions and Belief Systems", "Comparative study of major world religions"),
                        ("General Mathematics", "Core mathematical operations, functions, and models")
                    ],
                    "Minor": [
                        ("Oral Communication", "Public speaking and communicative strategies"),
                        ("Physical Education and Health 1", "Foundational physical fitness and wellness activities")
                    ]
                },
                2: {
                    "Major": [
                        ("Disciplines and Ideas in the Applied Social Sciences", "Counseling, social work, and communication"),
                        ("Philippine Politics and Governance", "Structure and history of Philippine government"),
                        ("Creative Nonfiction", "Literary journalism and essay writing"),
                        ("Statistics and Probability", "Data analysis, distribution, and hypothesis testing")
                    ],
                    "Minor": [
                        ("Reading and Writing", "Critical reading and academic writing skills"),
                        ("Personal Development", "Self-exploration, mental health, and career preparation")
                    ]
                }
            }
        },
        "Grade 12": {
            "STEM": {
                1: {
                    "Major": [
                        ("General Biology 1", "Cell biology, bioenergetics, genetics"),
                        ("General Physics 1", "Mechanics, thermodynamics, and waves"),
                        ("Practical Research 1", "Qualitative research methodologies"),
                        ("General Biology 2", "Systematics, anatomy, physiology, evolution")
                    ],
                    "Minor": [
                        ("Media and Information Literacy", "Responsible use of media and online resources"),
                        ("Introduction to the Philosophy of the Human Person", "Philosophical reflection on human existence")
                    ]
                },
                2: {
                    "Major": [
                        ("General Physics 2", "Electricity, magnetism, optics, modern physics"),
                        ("Research or Capstone Project", "Scientific research implementation and defense"),
                        ("Entrepreneurship", "Business plan development and marketing"),
                        ("Work Immersion", "Hands-on experience in a professional laboratory/tech environment")
                    ],
                    "Minor": [
                        ("Contemporary Philippine Arts from the Regions", "Regional art forms, artists, and critiques"),
                        ("Physical Education and Health 2", "Advanced sports, recreation, and health practices")
                    ]
                }
            },
            "ABM": {
                1: {
                    "Major": [
                        ("Business Finance", "Financial planning, investments, capital management"),
                        ("Principles of Marketing", "Consumer behavior, product, price, place, promotion"),
                        ("Applied Economics", "Economic theories, supply, demand, and markets"),
                        ("Practical Research 1", "Qualitative research methodologies")
                    ],
                    "Minor": [
                        ("Media and Information Literacy", "Responsible use of media and online resources"),
                        ("Introduction to the Philosophy of the Human Person", "Philosophical reflection on human existence")
                    ]
                },
                2: {
                    "Major": [
                        ("Business Finance 2", "Corporate finance and accounting systems"),
                        ("Entrepreneurship", "Business plan development and marketing"),
                        ("Practical Research 2", "Quantitative research methodologies"),
                        ("Work Immersion", "Hands-on experience in a business environment")
                    ],
                    "Minor": [
                        ("Contemporary Philippine Arts from the Regions", "Regional art forms, artists, and critiques"),
                        ("Physical Education and Health 2", "Advanced sports, recreation, and health practices")
                    ]
                }
            },
            "HUMSS": {
                1: {
                    "Major": [
                        ("Community Engagement, Solidarity, and Citizenship", "Social justice, community action, field immersion"),
                        ("Trends, Networks, and Critical Thinking in the 21st Century Culture", "Analyzing social patterns, technology, and global networks"),
                        ("Philippine Politics and Governance", "Structure and history of Philippine government"),
                        ("Practical Research 1", "Qualitative research methodologies")
                    ],
                    "Minor": [
                        ("Media and Information Literacy", "Responsible use of media and online resources"),
                        ("Introduction to the Philosophy of the Human Person", "Philosophical reflection on human existence")
                    ]
                },
                2: {
                    "Major": [
                        ("Creative Nonfiction", "Literary journalism and essay writing"),
                        ("Entrepreneurship", "Business plan development and marketing"),
                        ("Practical Research 2", "Quantitative research methodologies"),
                        ("Work Immersion", "Hands-on experience in a civic/community organization")
                    ],
                    "Minor": [
                        ("Contemporary Philippine Arts from the Regions", "Regional art forms, artists, and critiques"),
                        ("Physical Education and Health 2", "Advanced sports, recreation, and health practices")
                    ]
                }
            }
        }
    }

    for grade_lvl, strand_dict in shs_data.items():
        for strand, sem_dict in strand_dict.items():
            for sem, type_dict in sem_dict.items():
                for sub_type, sub_list in type_dict.items():
                    for name, desc in sub_list:
                        cursor.execute("""
                            INSERT INTO SUBJECT (subjectName, description, gradeLevel, strand, semester, subjectType, termType)
                            VALUES (?, ?, ?, ?, ?, ?, 'Semester')
                        """, (name, desc, grade_lvl, strand, sem, sub_type))

    print(f"✓ Seeded subjects successfully!")

if __name__ == "__main__":
    run_migration()
