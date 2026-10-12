import os
import csv
import ssl
import smtplib
from datetime import datetime
from email.message import EmailMessage

import cv2
import numpy as np
import face_recognition
from dotenv import load_dotenv

load_dotenv()

IMAGES_PATH = "Images"
STUDENTS_CSV = "students.csv"
ATTENDANCE_CSV = "attendance.csv"

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")


def load_student_emails():
    """Map child name -> parent email, from students.csv."""
    emails = {}
    with open(STUDENTS_CSV, "r", newline="") as f:
        for row in csv.DictReader(f):
            emails[row["Name"].strip().upper()] = row["ParentEmail"].strip()
    return emails


def load_known_faces():
    """Load each reference photo in Images/ and compute its face encoding."""
    names = []
    encodings = []
    for filename in os.listdir(IMAGES_PATH):
        img = cv2.imread(os.path.join(IMAGES_PATH, filename))
        if img is None:
            continue
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        found = face_recognition.face_encodings(img_rgb)
        if not found:
            print(f"Warning: no face detected in {filename}, skipping.")
            continue
        encodings.append(found[0])
        names.append(os.path.splitext(filename)[0].upper())
    return names, encodings


def already_marked_today(name):
    today = datetime.now().strftime("%Y-%m-%d")
    with open(ATTENDANCE_CSV, "r", newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0] == name and row[1] == today:
                return True
    return False


def mark_attendance(name):
    now = datetime.now()
    with open(ATTENDANCE_CSV, "a", newline="") as f:
        csv.writer(f).writerow([name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])


def send_arrival_email(parent_email, child_name):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("EMAIL_SENDER / EMAIL_PASSWORD not set in .env — skipping email.")
        return

    em = EmailMessage()
    em["From"] = EMAIL_SENDER
    em["To"] = parent_email
    em["Subject"] = f"{child_name.title()} has arrived home safely"
    em.set_content(
        f"Hi,\n\n{child_name.title()} was detected arriving home at "
        f"{datetime.now().strftime('%H:%M:%S')}.\n\n- AI-Enabled Attendance System"
    )

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(em)
        print(f"Notification email sent to {parent_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def main():
    student_emails = load_student_emails()
    known_names, known_encodings = load_known_faces()
    print(f"Loaded {len(known_names)} registered student(s): {known_names}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")

    print("Press 'q' to quit.")
    while True:
        success, frame = cap.read()
        if not success:
            break

        small_frame = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        for encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            if not known_encodings:
                continue

            distances = face_recognition.face_distance(known_encodings, encoding)
            best_match = int(np.argmin(distances))
            matches = face_recognition.compare_faces(known_encodings, encoding)

            if matches[best_match]:
                name = known_names[best_match]

                top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                if not already_marked_today(name):
                    mark_attendance(name)
                    parent_email = student_emails.get(name)
                    if parent_email:
                        send_arrival_email(parent_email, name)
                    else:
                        print(f"No parent email found for {name} in students.csv")

        cv2.imshow("Webcam", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
