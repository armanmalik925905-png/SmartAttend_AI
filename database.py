import sqlite3
import os

def create_database():
    connection = sqlite3.connect(
        os.path.join(os.path.dirname(__file__), "students.db")
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            college_id TEXT UNIQUE NOT NULL,
            dob TEXT,
            gender TEXT,
            email TEXT,
            phone TEXT,
            course TEXT,
            semester TEXT,
            father_name TEXT,
            parent_phone TEXT,
            address TEXT
        )
    """)

    connection.commit()
    connection.close()

    print("Database and students table created successfully!")

create_database()