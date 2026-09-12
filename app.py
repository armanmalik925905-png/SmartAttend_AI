from flask import Flask, request, redirect, render_template, render_template_string
from flask import Flask, render_template
import sqlite3
import os
import threading
from attendance import run_camera
import numpy as np
from datetime import datetime

app = Flask(__name__)


def add_student(name, college_id, dob, gender, email, phone,
                course, semester, father_name, parent_phone, address):

    connection = sqlite3.connect(
    os.path.join(os.path.dirname(__file__), "students.db")
    )
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO students
            (name, college_id, dob, gender, email, phone,
             course, semester, father_name, parent_phone, address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            college_id,
            dob,
            gender,
            email,
            phone,
            course,
            semester,
            father_name,
            parent_phone,
            address
        ))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


@app.route("/")
def home():
    return render_template("index.html")
@app.route("/start-camera")
def start_camera():

    camera_thread = threading.Thread(
        target=run_camera,
        daemon=True
    )

    camera_thread.start()

    return redirect("/admin")

@app.route("/admin")
def admin():



    connection = sqlite3.connect(
        os.path.join(os.path.dirname(__file__), "students.db")
    )
    cursor = connection.cursor()

    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Present Today
    cursor.execute("""
        SELECT COUNT(DISTINCT college_id)
        FROM attendance
        WHERE date(attendance_date) = date('now', 'localtime')
    """)
    present_today = cursor.fetchone()[0]

    # Absent Today
    absent_today = total_students - present_today

    # Attendance Percentage
    if total_students > 0:
        attendance_percentage = round(
            (present_today / total_students) * 100, 1
        )
    else:
        attendance_percentage = 0
        # Recent Attendance
    cursor.execute("""
        SELECT
            a.college_id,
            s.name,
            a.attendance_date,
            a.attendance_time,
            'Present'
             
        FROM attendance a
        JOIN students s
            ON a.college_id = s.college_id
        ORDER BY a.attendance_date DESC, a.attendance_time DESC
        LIMIT 10
    """)

    recent_attendance = cursor.fetchall()

    connection.close()

    # Admin HTML read karo
    file_path = os.path.join(
        os.path.dirname(__file__), "admin.html"
    )

    with open(file_path, "r", encoding="utf-8") as file:
        html = file.read()

    return render_template_string(
        html,
        recent_attendance=recent_attendance,
        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        attendance_percentage=attendance_percentage
    )

@app.route("/student")
def student():
    return render_template("studentR.html")

    file_path = os.path.join(os.path.dirname(__file__), "studentR.html")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

@app.route("/students")
def students_list():
    return render_template("studentR.html")

    connection = sqlite3.connect(
        os.path.join(os.path.dirname(__file__), "students.db")
    )
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, college_id, dob, gender,
               email, phone, course, semester
        FROM students
        ORDER BY id DESC
    """)

    students = cursor.fetchall()
    connection.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student List</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                padding: 30px;
            }

            h1 {
                text-align: center;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                margin-top: 25px;
            }

            th, td {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }

            th {
                background: #222;
                color: white;
            }

            tr:hover {
                background: #f1f1f1;
            }
        </style>
    </head>

    <body>

        <h1>Registered Students</h1>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>College ID</th>
                    <th>DOB</th>
                    <th>Gender</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Course</th>
                    <th>Semester</th>
                </tr>
            </thead>

            <tbody>

                {% for student in students %}
                <tr>
                    <td>{{ student[0] }}</td>
                    <td>{{ student[1] }}</td>
                    <td>{{ student[2] }}</td>
                    <td>{{ student[3] }}</td>
                    <td>{{ student[4] }}</td>
                    <td>{{ student[5] }}</td>
                    <td>{{ student[6] }}</td>
                    <td>{{ student[7] }}</td>
                    <td>{{ student[8] }}</td>
                </tr>
                {% endfor %}

            </tbody>
        </table>

    </body>
    </html>
    """

    return render_template_string(html, students=students)

@app.route("/attendance")
def attendance_report():
    return render_template("Attendance.html")

    selected_date = request.args.get("date")

    connection = sqlite3.connect(
    os.path.join(os.path.dirname(__file__), "students.db")
    )
    cursor = connection.cursor()

    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Attendance records
    if selected_date:
        cursor.execute("""
            SELECT name, college_id, attendance_date, attendance_time
            FROM attendance
            WHERE date(attendance_date) = ?
            ORDER BY id DESC
        """, (selected_date,))
    else:
        cursor.execute("""
            SELECT name, college_id, attendance_date, attendance_time
            FROM attendance
            ORDER BY id DESC
        """)

    records = cursor.fetchall()

    # Present students
    if selected_date:
        cursor.execute("""
            SELECT COUNT(DISTINCT college_id)
            FROM attendance
            WHERE date(attendance_date) = ?
        """, (selected_date,))
    else:
        cursor.execute("""
            SELECT COUNT(DISTINCT college_id)
            FROM attendance
        """)

    present = cursor.fetchone()[0]

    absent = total_students - present

    if total_students > 0:
        attendance_rate = round((present / total_students) * 100, 1)
    else:
        attendance_rate = 0

    connection.close()

    with open("Attendance.html", "r", encoding="utf-8") as file:
        html = file.read()

    return render_template_string(
        html,
        records=records,
        total_students=total_students,
        present=present,
        absent=absent,
        attendance_rate=attendance_rate,
        selected_date=selected_date
    )

    records = cursor.fetchall()

    connection.close()

    with open("Attendance.html", "r", encoding="utf-8") as file:
        html = file.read()

    return render_template_string(
        html,
        records=records,
        total_students=total_students,
        present=present,
        absent=absent,
        attendance_rate=attendance_rate
    )
@app.route("/teacher")
def teacher():
    return render_template("teacher.html")

@app.route("/settings")
def settings():
    return render_template("setting.html")

@app.route("/logout")
def logout():
    return render_template("logout.html")

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    college_id = request.form["college_id"]
    dob = request.form.get("dob")
    gender = request.form.get("gender")
    email = request.form.get("email")
    phone = request.form.get("phone")
    course = request.form.get("course")
    semester = request.form.get("semester")
    father_name = request.form.get("father_name")
    parent_phone = request.form.get("parent_phone")
    address = request.form.get("address")

    success = add_student(
        name,
        college_id,
        dob,
        gender,
        email,
        phone,
        course,
        semester,
        father_name,
        parent_phone,
        address
    )

    if success:
        return """
        <h1>Student Registered Successfully! ✅</h1>
        <p>Student Name: {}</p>
        <p>Student ID: {}</p>
        <br>
        <a href="/student">Register Another Student</a>
        """.format(name, college_id)

    else:
        return """
        <h1>Registration Failed ❌</h1>
        <p>Ye Student ID already registered hai.</p>
        <br>
        <a href="/student">Go Back</a>
        """


if __name__ == "__main__":
    app.run(debug=True)
        
            
