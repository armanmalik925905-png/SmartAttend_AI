import cv2
import os
import sqlite3

os.makedirs("faces", exist_ok=True)

college_id = input("Enter existing College ID: ")

# Database me ID check karo
connection = sqlite3.connect("students.db")
cursor = connection.cursor()

cursor.execute(
    "SELECT name FROM students WHERE college_id = ?",
    (college_id,)
)

student = cursor.fetchone()
connection.close()

if not student:
    print("College ID database me nahi mili!")
    exit()

name = student[0]

print("Student found:", name)

# Camera start
camera = cv2.VideoCapture(0)

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

count = 0

print("\nCamera started!")
print("Face camera ke saamne rakho.")

while True:
    ret, frame = camera.read()

    if not ret:
        print("Camera open nahi hua!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5
    )

    for (x, y, w, h) in faces:
        count += 1

        face = gray[y:y + h, x:x + w]

        filename = f"faces/{college_id}_{count}.jpg"
        cv2.imwrite(filename, face)

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Images: {count}/10",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.imshow("Face Registration", frame)

    if cv2.waitKey(100) & 0xFF == ord("q") or count >= 10:
        break

camera.release()
cv2.destroyAllWindows()

print("\nFace registration completed! ✅")
print("Student:", name)
print("College ID:", college_id)
print("Images saved:", count)