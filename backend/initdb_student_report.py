import sqlite3


def get_db_connection():
    conn = sqlite3.connect('student_projects.db')
    conn.row_factory = sqlite3.Row  # This allows dictionary-like access to rows
    return conn

# Create a SQLite database and tables if they don't exist
def init_db():
    conn = sqlite3.connect('student_projects.db')
    cursor = conn.cursor()

    # Create the ProjectData table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProjectData (
        Student_ID TEXT,
        Project_ID TEXT,
        Project_Name TEXT,
        Milestone_Name TEXT,
        Milestone_Status TEXT,
        Overall_Status TEXT,
        Overall_Completion_Percentage INTEGER,
        Update_Date TEXT,
        Time_Spent INTEGER,
        Uploaded_Files INTEGER,
        Next_Deadline TEXT
    )
    ''')

    # Create the FilePaths table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FilePaths (
        Project_ID TEXT,
        pdf TEXT,
        csv TEXT,
        other TEXT
    )
    ''')

    # Create the Milestones table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Milestones (
        Project_ID TEXT,
        name TEXT,
        status TEXT,
        completionDate TEXT
    )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
init_db()


import random
from datetime import datetime, timedelta

# Mock data for 10 students and 3 projects
students = [
    ("ST101", "John Doe"), ("ST102", "Jane Smith"), ("ST103", "Alice Brown"), ("ST104", "Bob White"),
    ("ST105", "Charlie Black"), ("ST106", "Dana Blue"), ("ST107", "Evan Gray"), ("ST108", "Fay Green"),
    ("ST109", "George Yellow"), ("ST110", "Hannah Orange")
]

projects = [
    ("P001", "AI Healthcare Analysis"), 
    ("P002", "Smart City Traffic Management"), 
    ("P003", "E-Commerce Recommendation System")
]

# Milestones for each project
milestones = {
    "P001": ["Data Collection", "Model Development", "Model Training", "Testing", "Deployment"],
    "P002": ["Requirement Gathering", "Design Architecture", "Simulation Setup", "Data Analysis", "Report Submission"],
    "P003": ["Market Research", "Product Design", "Prototype Development", "User Testing", "Launch"]
}

def random_status():
    return random.choice(["On Track", "Delayed", "At Risk"])

def random_milestone_status():
    return random.choice(["Not Started", "In Progress", "Completed"])

def random_percentage():
    return random.randint(0, 100)

def random_time_spent():
    return random.randint(10, 100)

def random_uploaded_files():
    return random.randint(1, 10)

def random_date(start_date):
    return (start_date + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")

def insert_mock_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get today's date for Update_Date and Next_Deadline generation
    today = datetime.now()

    # Insert projects and their milestones first
    for project in projects:
        project_id = project[0]
        project_name = project[1]

        # Insert file paths
        cursor.execute('''
            INSERT INTO FilePaths (Project_ID, pdf, csv, other) 
            VALUES (?, ?, ?, ?)''',
            (project_id, f"/path/to/{project_id}_report.pdf", f"/path/to/{project_id}_data.csv", f"/path/to/{project_id}_notes.txt"))

        # Insert milestones for each project
        for milestone_name in milestones[project_id]:
            cursor.execute('''
                INSERT INTO Milestones (Project_ID, name, status, completionDate)
                VALUES (?, ?, ?, ?)''',
                (project_id, milestone_name, random_milestone_status(), random_date(today)))

    # Now insert student project data
    for student in students:
        student_id = student[0]

        for project in projects:
            project_id = project[0]
            project_name = project[1]

            # Insert project data for the student
            cursor.execute('''
                INSERT INTO ProjectData (Student_ID, Project_ID, Project_Name, Milestone_Name, Milestone_Status,
                Overall_Status, Overall_Completion_Percentage, Update_Date, Time_Spent, Uploaded_Files, Next_Deadline)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (student_id, project_id, project_name, "Overall Project", random_status(), random_status(), random_percentage(),
                random_date(today), random_time_spent(), random_uploaded_files(), random_date(today)))

    conn.commit()
    conn.close()

# Call the function to insert the mock data
insert_mock_data()