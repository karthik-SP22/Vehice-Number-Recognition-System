import cv2
import easyocr
import sqlite3
from datetime import datetime



conn = sqlite3.connect("vehicle_database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicle_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_number TEXT,
    date_time TEXT
)
""")

conn.commit()

# =========================
# EASYOCR
# =========================

reader = easyocr.Reader(['en'], gpu=False)

# =========================
# WEBCAM
# =========================

cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Cannot open webcam")
    exit()

print("Press SPACE to scan")
print("Press Q to quit")

last_text = ""

# =========================
# MAIN LOOP
# =========================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Resize for speed
    frame = cv2.resize(frame, (640, 480))

    # Show camera
    cv2.imshow("Vehicle Number Plate Recognition", frame)

    key = cv2.waitKey(1)

    # =========================
    # SPACE = SCAN
    # =========================

    if key == 32:

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Increase contrast
        gray = cv2.equalizeHist(gray)

        # OCR
        results = reader.readtext(
            gray,
            detail=1,
            paragraph=False
        )

        detected_text = ""

        for result in results:

            text = result[1]
            confidence = result[2]

            if confidence > 0.25:

                detected_text += text + " "

                # Draw rectangle
                points = result[0]

                top_left = tuple(map(int, points[0]))
                bottom_right = tuple(map(int, points[2]))

                cv2.rectangle(
                    frame,
                    top_left,
                    bottom_right,
                    (0, 255, 0),
                    2
                )

        # Clean text
        detected_text = detected_text.strip()

        detected_text = "".join(
            c for c in detected_text
            if c.isalnum()
        )

        # =========================
        # SHOW RESULT
        # =========================

        if len(detected_text) >= 5:

            cv2.putText(
                frame,
                f"Plate: {detected_text}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

            print("Detected:", detected_text)

            # Save database
            if detected_text != last_text:

                current_time = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                cursor.execute("""
                INSERT INTO vehicle_data (
                    vehicle_number,
                    date_time
                )
                VALUES (?, ?)
                """, (
                    detected_text,
                    current_time
                ))

                conn.commit()

                print("Saved to Database")

                last_text = detected_text

        else:
            print("No Plate Detected")

        # Show scanned result
        cv2.imshow(
            "Vehicle Number Plate Recognition",
            frame
        )

    # =========================
    # Q = QUIT
    # =========================

    if key == ord('q'):
        break

# =========================
# RELEASE
# =========================

cap.release()
conn.close()
cv2.destroyAllWindows()