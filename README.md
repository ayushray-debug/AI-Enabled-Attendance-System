# AI-Enabled Attendance System

A facial-recognition attendance system that detects a registered child via webcam,
logs their arrival time, and emails their specific parent a "safely arrived" notification.

## 1. Problem Statement

Current transportation systems lack an efficient means of notifying parents of their
child's safe arrival home from school. Manual methods of confirming child safety
post-school hours are unreliable and prone to human error.

## 2. Users / Stakeholders

- Parents seeking reassurance of their child's safety.
- Developers creating the facial attendance system.
- Schools or organizations implementing the technology.

## 3. Objectives

- Provide parents with real-time notifications upon their child's arrival.
- Enhance child safety and provide peace of mind to parents.

## 4. Features

- Facial recognition for accurate child identification.
- Automatic email notification to the *correct* parent the moment their child is detected.
- CSV-based attendance log (one entry per child per day).
- Simple file-based setup — no database required.

## 5. AI Used

- Computer vision (face detection + face encoding) via the `face_recognition` library
  (built on dlib's HOG/CNN face detector and a ResNet-based encoding model).
- Nearest-neighbor face-distance matching for identification.

## 6. Data Used

- Facial reference images of registered children (`Images/` folder, one clear photo per child).
- A simple roster (`students.csv`) mapping each child's name to their parent's email.

## 7. Solution

- Register each child by placing one clear, front-facing photo in `Images/`,
  named after the child (e.g. `Riya.jpg`).
- Add a row to `students.csv` mapping that same name to the parent's email address.
- Run `main.py`, which opens the webcam, detects faces frame-by-frame, and matches
  them against the registered encodings.
- On a first-time match for the day, the system logs the entry in `attendance.csv`
  and emails that child's parent — not a fixed, shared inbox.
- Credentials are kept out of source code (via a `.env` file) so they're never
  hardcoded or accidentally shared.

## 8. SDGs Involved

- **SDG 3** (Good Health and Well-being) — enhances child safety.
- **SDG 4** (Quality Education) — supports secure school-to-home transitions.

## 9. Future Scope

- Geolocation tracking for in-transit updates.
- Integration with smart home systems (e.g. unlock door / notify arrival).
- SMS/WhatsApp notifications in addition to email.
- Admin dashboard for managing registered students without editing files directly.

---

## Project Structure

```
AI-Enabled Attendance System/
├── Images/              # One reference photo per child (filename = child's name)
├── students.csv         # Name -> ParentEmail mapping
├── attendance.csv       # Auto-generated attendance log (Name, Date, Time)
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── .env.example         # Template for email credentials (copy to .env)
└── .gitignore
```

## Setup

### 1. Install dependencies

`face_recognition` depends on `dlib`, which needs CMake and a C++ compiler to
build from source on Windows (`pip install dlib` will fail without one). Two
options:

- **Install a C++ compiler**: install "Desktop development with C++" via the
  Visual Studio Build Tools installer, then `pip install dlib`.
- **Use a precompiled wheel** (what this project was tested with): grab a
  Windows wheel matching your Python version (e.g. `dlib-19.24.1-cp311-cp311-win_amd64.whl`
  for Python 3.11) and `pip install path\to\that\wheel.whl`. Only do this with
  a wheel source you trust, since it's a compiled binary.

Then:

```bash
pip install -r requirements.txt
```

**Note:** `requirements.txt` pins `numpy<2`. Some older precompiled `dlib`
wheels were built against NumPy 1.x and raise
`RuntimeError: Unsupported image type, must be 8bit gray or RGB image` under
NumPy 2.x due to an ABI mismatch — downgrading NumPy fixes it.

### 2. Add student photos

Drop one clear, front-facing photo per child into `Images/`, named after the
child, e.g.:

```
Images/Riya.jpg
Images/Aman.png
```

### 3. Fill in `students.csv`

```
Name,ParentEmail
Riya,riya.parent@example.com
Aman,aman.parent@example.com
```

Names must match the image filenames (case-insensitive).

### 4. Configure email credentials

Copy `.env.example` to `.env` and fill in a **Gmail App Password** (not your
normal password — generate one at https://myaccount.google.com/apppasswords,
requires 2FA enabled on the sending account):

```
EMAIL_SENDER=your-school-system@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
```

### 5. Run

```bash
python main.py
```

Press **q** with the webcam window focused to quit.

## Notes / Limitations (intentional, since this is a school project)

- Single local webcam only — no multi-camera or CCTV integration.
- One attendance entry per child per calendar day (re-detecting the same child
  later the same day won't re-trigger an email).
- No login/admin UI — registration is done by editing `Images/` and `students.csv` directly.
- Recognition accuracy depends on lighting and photo quality; this is a proof of
  concept, not a production-grade security system.
