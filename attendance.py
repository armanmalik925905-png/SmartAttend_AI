import cv2
import numpy as np
import os
import sqlite3
from datetime import datetime

# -----------------------------
# DATABASE ATTENDANCE FUNCTION
# -----------------------------
def mark_attendance(college_id):

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM students WHERE college_id = ?",
        (college_id,)
    )

    student = cursor.fetchone()

    if not student:
        print("Student not found!")
        connection.close()
        return

    name = student[0]

    current_date = datetime.now().strftime("%Y-%m-%d")
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

    # Same student ko same day baar-baar mark na karne ke liye
    cursor.execute("""
        SELECT id FROM attendance
        WHERE college_id = ? AND attendance_date = ?
    """, (college_id, current_date))

    already_marked = cursor.fetchone()

    if already_marked:
        print("\nAttendance already marked today! ⚠️")
        print("Name:", name)
        print("College ID:", college_id)
        connection.close()
        return

    cursor.execute("""
        INSERT INTO attendance
        (name, college_id, attendance_date, attendance_time)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        college_id,
        current_date,
        current_time
    ))

    connection.commit()
    connection.close()

    print("\nAttendance marked successfully! ✅")
    print("Name:", name)
    print("College ID:", college_id)
    print("Date:", current_date)
    print("Time:", current_time)


# -----------------------------
# LOAD REGISTERED FACE IMAGES
# -----------------------------

faces_path = "faces"

if not os.path.exists(faces_path):
    print("faces folder nahi mila!")
    exit()

images = []
labels = []

for filename in os.listdir(faces_path):

    if filename.lower().endswith(".jpg"):

        try:
            college_id = filename.rsplit("_", 1)[0]

            image_path = os.path.join(faces_path, filename)

            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

            if image is not None:
                images.append(image)
                labels.append(college_id)

        except Exception:
            pass


if len(images) == 0:
    print("Koi registered face image nahi mili!")
    exit()


print("Registered face images:", len(images))


# -----------------------------
# CREATE FACE RECOGNIZER
# -----------------------------

recognizer = cv2.face.LBPHFaceRecognizer_create()

# College IDs ko numeric labels me convert karna
unique_ids = list(set(labels))

id_to_label = {}

for index, college_id in enumerate(unique_ids):
    id_to_label[index] = college_id

numeric_labels = [
    unique_ids.index(college_id)
    for college_id in labels
]

recognizer.train(images, np.array(numeric_labels, dtype=np.int32))


# -----------------------------
# FACE DETECTOR
# -----------------------------

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


# -----------------------------
# START CAMERA
# -----------------------------

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Camera open nahi hua!")
    exit()

print("\nCamera started!")
print("Face camera ke saamne rakho.")
print("Q dabakar camera band kar sakte ho.")


attendance_done = False

while True:

    ret, frame = camera.read()

    if not ret:
        print("Camera frame nahi mila!")
        break

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    detected_faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(100, 100)
    )

    for (x, y, w, h) in detected_faces:

        face = gray[y:y+h, x:x+w]

        label, confidence = recognizer.predict(face)

        # LBPH me lower confidence = better match
        if confidence < 70:

            college_id = id_to_label[label]

            connection = sqlite3.connect("students.db")
            cursor = connection.cursor()

            cursor.execute(
                "SELECT name FROM students WHERE college_id = ?",
                (college_id,)
            )

            student = cursor.fetchone()
            connection.close()

            if student:

                name = student[0]

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x+w, y+h),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    name,
                    (x, y-30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    "Face Recognized",
                    (x, y-5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                if not attendance_done:

                    mark_attendance(college_id)

                    attendance_done = True

        else:

            cv2.rectangle(
                frame,
                (x, y),
                (x+w, y+h),
                (0, 0, 255),
                2
            )

            cv2.putText(
                frame,
                "Unknown Face",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

    cv2.imshow(
        "Smart Attendance - Face Recognition",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()