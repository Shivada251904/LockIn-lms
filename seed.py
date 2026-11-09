import os
from datetime import datetime, timedelta, timezone
from lms_app import build_app
from lms_app.models import User, Course, Enrollment, Assignment, Submission, db
from lms_app.extensions import bcrypt

def seed_database():
    print(" Initialising High-Density Database Seeding Procedure...")
    
    db_path = os.path.join("instance", "lockin-lms.db")
    if os.path.exists(db_path):
        try:
            db.session.remove()
            db.drop_all()
            print(" Cleared legacy SQLite database tables cleanly.")
        except Exception as e:
            print(f" Table reset checkpoint note: {e}")

    db.create_all()

    hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")

    teachers = [
        User(name="Prof. Eleanor Vance", email="vance@lockin.edu", password_hash=hashed_pw, role="teacher"),
        User(name="Dr. Marcus Brody", email="brody@lockin.edu", password_hash=hashed_pw, role="teacher"),
        User(name="Dr. Sarah Jenkins", email="jenkins@lockin.edu", password_hash=hashed_pw, role="teacher")
    ]
    
    students = [
        User(name="Alex Mercer", email="student@lockin.edu", password_hash=hashed_pw, role="student"),
        User(name="Sam Wilson", email="sam@lockin.edu", password_hash=hashed_pw, role="student"),
        User(name="Chloe Fraser", email="chloe@lockin.edu", password_hash=hashed_pw, role="student")
    ]

    db.session.add_all(teachers + students)
    db.session.commit()

    courses = [

        Course(title="Intro to Cyber Security & Isolation Frameworks", description="Foundations of system architecture, security primitives, and automated sandbox container testing metrics.", teacher_id=teachers[0].id),
        Course(title="Human-Computer Interaction & Desktop Containers", description="Evaluating frontend focus tracking telemetry, full-screen event state tracking, and secure web engine wrappers.", teacher_id=teachers[0].id),
        
        Course(title="Advanced Relational Databases & SQL Optimization", description="Deep-dive schema constraints, nested optimization loops, multi-table index structures, and ACID transactional pipelines.", teacher_id=teachers[1].id),
        Course(title="Data Mining and Machine Learning Essentials", description="Introduction to algorithmic mathematical constructs, clustering pipelines, predictive models, and pattern extraction architectures.", teacher_id=teachers[1].id),
        
        Course(title="Discrete Mathematics & Physical Structures", description="Combinatorics, graph algorithms, predicate calculus, and mathematical proof structures foundational to computer science.", teacher_id=teachers[2].id),
        Course(title="Ethics in the Digital Age & Artificial Intelligence", description="Analysing data ownership paradigms, computational neutrality, algorithm biases, and legal frameworks governing autonomous software systems.", teacher_id=teachers[2].id)
    ]
    
    db.session.add_all(courses)
    db.session.commit()

    enrolments = [
        Enrollment(student_id=students[0].id, course_id=courses[0].id),
        Enrollment(student_id=students[0].id, course_id=courses[1].id),
        Enrollment(student_id=students[0].id, course_id=courses[2].id),
        Enrollment(student_id=students[0].id, course_id=courses[4].id),
        Enrollment(student_id=students[0].id, course_id=courses[0].id),
        Enrollment(student_id=students[1].id, course_id=courses[2].id),
        Enrollment(student_id=students[2].id, course_id=courses[3].id)
    ]
    db.session.add_all(enrolments)
    db.session.commit()

    # Sample Assignment Variations
    assignments = [
        Assignment(course_id=courses[0].id, title="Weekly Lab: Networking Architecture Analysis", description="Review routing table topologies. Provide a 300-word documentation outlining how packets traverse cross-origin spaces safely.", due_date=datetime.now(timezone.utc) + timedelta(days=7)),
        Assignment(course_id=courses[0].id, title="Final Assessment: Systems Security Lockdown Exam", description="EXAM RULES: You are locked into a secure browser monitoring session. Leaving fullscreen mode or shifting window cursor focus generates infractions. 3 violations auto-terminates your paper.", due_date=datetime.now(timezone.utc) + timedelta(hours=2)),
        Assignment(course_id=courses[2].id, title="Database Challenge: Normalisation Strategy", description="Execute complete 3NF normalization transformations over an un-indexed flat tabular spreadsheet structure.", due_date=datetime.now(timezone.utc) + timedelta(days=4)),
        Assignment(course_id=courses[4].id, title="Problem Set 1: Graph Theory Proofs", description="Submit formalized documentation detailing node traversal solutions using Euler paths vs Hamiltonian cycles.", due_date=datetime.now(timezone.utc) + timedelta(days=3))
    ]
    db.session.add_all(assignments)
    db.session.commit()

    print("\n High-Density Seeding Operations Completed! Multiple courses deployed successfully.")

if __name__ == "__main__":
    app = build_app()
    with app.app_context():
        seed_database()

