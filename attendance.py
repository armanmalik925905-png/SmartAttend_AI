import cv2
import numpy as np
import os
import sqlite3
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")
FACES_DIR = os.path.join(BASE_DIR, "faces")


def mark_attendance(college_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM students WHERE college_id = ?",
        (college_id,)
    )

    student = cursor.fetchone()

    if not student:
        conn.close()
        return False, "Student not found"

    name = student[0]

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            college_id TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            attendance_time TEXT NOT NULL
        )
    """)

    cursor.execute("""
        SELECT id FROM attendance
        WHERE college_id = ?
        AND attendance_date = ?
    """, (college_id, today))

    already_marked = cursor.fetchone()

    if already_marked:
        conn.close()
        return False, "Attendance already marked today"

    cursor.execute("""
        INSERT INTO attendance
        (name, college_id, attendance_date, attendance_time)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        college_id,
        today,
        current_time
    ))

    conn.commit()
    conn.close()

    return True, f"Attendance marked: {name}"


def run_camera():

    # Load registered face images
    images = []
    college_ids = []

    for filename in os.listdir(FACES_DIR):

        if filename.lower().endswith((".jpg", ".jpeg", ".png")):

            path = os.path.join(FACES_DIR, filename)

            img = cv2.imread(path)

            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                images.append(gray)

                college_id = filename.rsplit("_", 1)[0]
                college_ids.append(college_id)

    if len(images) == 0:
        print("No registered faces found!")
        return

    print("Registered face images:", len(images))

    # Face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    labels = np.arange(len(images))

    recognizer.train(images, labels)

    # Haar Cascade
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Camera
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Camera open nahi ho raha!")
        return

    print("\nCamera started!")
    print("Face camera ke saamne rakho.")
    print("Q dabakar camera band kar sakte ho.")

    attendance_done = False

    while True:

        ret, frame = camera.read()

        if not ret:
            print("Camera frame nahi mil raha!")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5
        )

        for (x, y, w, h) in faces:

            face = gray[y:y+h, x:x+w]

            label, confidence = recognizer.predict(face)

            if confidence < 70:

                college_id = college_ids[label]

                if not attendance_done:

                    success, message = mark_attendance(college_id)

                    print(message)

                    attendance_done = True

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x+w, y+h),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    "Attendance Marked",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        cv2.imshow("Smart Attendance Camera", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_camera()