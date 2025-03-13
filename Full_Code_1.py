import os
import cv2
import dlib
from scipy.spatial import distance
from tkinter import messagebox
from playsound import playsound
import time
import pickle
import datetime
import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import scrolledtext

# Initialize Dlib models
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r'C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\DataModels\shape_predictor_68_face_landmarks.dat')
face_rec_model = dlib.face_recognition_model_v1(r'C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\DataModels\dlib_face_recognition_resnet_model_v1.dat')

# Define camera positions on the map
camera_positions = {
    "camera_1": (100, 200),  # Example coordinates for camera 1
    "camera_2": (400, 300)   # Example coordinates for camera 2
}

# Load the map image
map_image = cv2.imread(r'C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\CampusMap.jpg')

# Database connection


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MySQL123...",
            database="ai_based_security_system"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None


def insert_recognition(name, date_time):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        check_query = """
        SELECT COUNT(*) FROM known_names
        WHERE name = %s AND date_time > NOW() - INTERVAL 5 SECOND
        """
        cursor.execute(check_query, (name, ))
        count = cursor.fetchone()[0]

        if count == 0:
            insert_query = """
            INSERT INTO known_names (name, date_time)
            VALUES (%s, %s)
            """
            cursor.execute(insert_query, (name, date_time))
            connection.commit()
            print(f"Inserted {name} at {date_time}")

        cursor.close()
        connection.close()


def review_data(text_box):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        review_query = "SELECT * FROM known_names ORDER BY date_time DESC"
        cursor.execute(review_query)
        records = cursor.fetchall()

        text_box.delete(1.0, tk.END)

        for record in records:
            text_box.insert(tk.END, f"Name: {record[1]}, Date and Time: {record[2]}\n")

        cursor.close()
        connection.close()

# GUI for reviewing logs


def create_gui():
    root = tk.Tk()
    root.title("AI-Based Multi-Camera Campus Security System")

    review_button = tk.Button(root, text="Review Data", command=lambda: review_data(text_box))
    review_button.pack(pady=10)

    text_box = scrolledtext.ScrolledText(root, width=60, height=20)
    text_box.pack(padx=10, pady=10)

    root.mainloop()

# Detection and Recognition Functions


def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    return faces


def get_landmarks(image, faces):
    landmarks = []
    for face in faces:
        shape = predictor(image, face)
        landmarks.append(shape)
    return landmarks


def get_face_encodings(image, landmarks):
    encodings = []
    for landmark in landmarks:
        encoding = face_rec_model.compute_face_descriptor(image, landmark)
        encodings.append(encoding)
    return encodings


def alarm_on_unknown_face():
    playsound('Alarm Sound/chin_tapak_dum_dum.mp3')

# Save and Load Known Encodings


def save_encodings(known_names, known_encodings, filename='known_faces.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump((known_names, known_encodings), f)


def load_encodings(filename='known_faces.pkl'):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return [], []


def save_unknown_image(image, image_count):
    file_path = rf"C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\UnKnown_Faces\UK_face_{image_count}.jpg"
    cv2.imwrite(file_path, image)
    print(f"Image of unknown face saved as {file_path}")

# Load Known Faces Dataset


def load_known_faces(known_faces_dir, save_file='known_faces.pkl', renew=False):
    if not renew:
        known_names, known_encodings = load_encodings(save_file)
        if known_names:
            print("Loaded known faces from file.")
            return known_names, known_encodings

    known_names = []
    known_encodings = []

    if not os.path.exists(known_faces_dir):
        print(f"Directory {known_faces_dir} does not exist!")
        return known_names, known_encodings

    for person_name in os.listdir(known_faces_dir):
        person_dir = os.path.join(known_faces_dir, person_name)

        if not os.path.isdir(person_dir):
            continue

        for image_name in os.listdir(person_dir):
            image_path = os.path.join(person_dir, image_name)

            image = cv2.imread(image_path)
            faces = detect_faces(image)
            landmarks = get_landmarks(image, faces)
            encodings = get_face_encodings(image, landmarks)

            for encoding in encodings:
                known_names.append(person_name)
                known_encodings.append(encoding)

    save_encodings(known_names, known_encodings)
    return known_names, known_encodings

# Draw a Line on Map


def draw_line_on_map(map_img, start_point, end_point):
    cv2.line(map_img, start_point, end_point, (0, 0, 255), 2)
    cv2.imshow("Map Tracking", map_img)
    cv2.waitKey(1)

# Recognize Faces


def recognize_faces(image, known_names, known_encodings, image_count, cap, camera_id, tolerance=0.5):
    faces = detect_faces(image)
    landmarks = get_landmarks(image, faces)
    encodings = get_face_encodings(image, landmarks)

    recognized_names = []
    for encoding in encodings:
        matches = [distance.euclidean(known_encoding, encoding) for known_encoding in known_encodings]
        best_match_index = min(range(len(matches)), key=matches.__getitem__)

        if matches[best_match_index] < tolerance:
            name = known_names[best_match_index]
            insert_recognition(name, datetime.datetime.now())

            if camera_id == "camera_1":
                print(f"{name} detected on camera 1")
            elif camera_id == "camera_2":
                print(f"{name} detected on camera 2")
                draw_line_on_map(map_image.copy(), camera_positions["camera_1"], camera_positions["camera_2"])
        else:
            name = "Unknown"
            alarm_on_unknown_face()
            save_unknown_image(image, image_count)
            image_count += 1

        recognized_names.append(name)

    return faces, recognized_names, image_count

# Draw Results on Camera Feed


def draw_results(image, faces, names):
    for (face, name) in zip(faces, names):
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

# Main Function


def main():
    image_count = 0
    known_faces_dir = r"C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\CustomDataset\Known Faces"
    renew = messagebox.askquestion("Renew Dataset", "Do you want to renew the dataset?") == 'yes'
    known_names, known_encodings = load_known_faces(known_faces_dir, renew=renew)

    cap1 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(1)

    while True:
        ret1, frame1 = cap1.read()
        if ret1:
            faces1, names1, image_count = recognize_faces(frame1, known_names, known_encodings, image_count, cap1, "camera_1")
            draw_results(frame1, faces1, names1)
            cv2.imshow("Camera 1", frame1)

        ret2, frame2 = cap2.read()
        if ret2:
            faces2, names2, image_count = recognize_faces(frame2, known_names, known_encodings, image_count, cap2, "camera_2")
            draw_results(frame2, faces2, names2)
            cv2.imshow("Camera 2", frame2)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
