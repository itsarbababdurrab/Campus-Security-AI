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


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r'C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\DataModels\shape_predictor_68_face_landmarks.dat')
face_rec_model = dlib.face_recognition_model_v1(r'C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\DataModels\dlib_face_recognition_resnet_model_v1.dat')


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MySQL123...",
            database="ai_based_security_system")
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

        print("Reviewing data from database:")
        for record in records:
            text_box.insert(tk.END, f"Name: {record[1]}, Date and Time: {record[2]}\n")

        cursor.close()
        connection.close()


def create_gui():
    root = tk.Tk()
    root.title("AI-Based Multi-Camera Campus Security System")

    review_button = tk.Button(root, text="Review Data", command=lambda: review_data(text_box))
    review_button.pack(pady=10)

    text_box = scrolledtext.ScrolledText(root, width=60, height=20)
    text_box.pack(padx=10, pady=10)

    root.mainloop()


def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    print(faces)
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


def save_encodings(known_names, known_encodings, filename='known_faces.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump((known_names, known_encodings), f)


def load_encodings(filename='known_faces.pkl'):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return [], []


def current_time():
    current_time_stamp = datetime.datetime.now().replace(microsecond=0)
    print("Current Date and Time:", current_time_stamp)


def save_unknown_image(image, image_count):
    file_path = rf"C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\UnKnown_Faces\UK_face_{image_count}.jpg"
    cv2.imwrite(file_path, image)
    print(f"Image of unknown face saved as {file_path}")


def load_known_faces(known_faces_dir, save_file='known_faces.pkl', renew=False):
    if not renew:
        known_names, known_encodings = load_encodings(save_file)
        if known_names:
            print("Loaded known faces from file.")
            return known_names, known_encodings

    print("load_known_faces from Images")
    known_names = []
    known_encodings = []

    if not os.path.exists(known_faces_dir):
        print(f"Directory {known_faces_dir} does not exist!")
        return known_names, known_encodings

    print(f"Loading faces from directory: {known_faces_dir}")

    for person_name in os.listdir(known_faces_dir):
        person_dir = os.path.join(known_faces_dir, person_name)
        print(f"Processing directory: {person_dir}")

        if not os.path.isdir(person_dir):
            print(f"{person_dir} is not a directory!")
            continue

        for image_name in os.listdir(person_dir):
            image_path = os.path.join(person_dir, image_name)
            print(f"Loading image: {image_path}")

            image = cv2.imread(image_path)
            faces = detect_faces(image)
            landmarks = get_landmarks(image, faces)
            encodings = get_face_encodings(image, landmarks)

            for encoding in encodings:
                known_names.append(person_name)
                known_encodings.append(encoding)

    save_encodings(known_names, known_encodings)
    return known_names, known_encodings


def recognize_faces(image, known_names, known_encodings, image_count, cap, tolerance=0.5):
    faces = detect_faces(image)
    landmarks = get_landmarks(image, faces)
    encodings = get_face_encodings(image, landmarks)

    recognized_names = []

    for encoding in encodings:
        matches = []

        for known_encoding in known_encodings:
            dist = distance.euclidean(known_encoding, encoding)
            matches.append(dist)

        best_match_index = min(range(len(matches)), key=matches.__getitem__)

        if matches[best_match_index] < tolerance:
            name = known_names[best_match_index]
            current_time()

            insert_recognition(name, datetime.datetime.now())

        else:
            name = "Unknown"
            start_time = time.time()
            while time.time() - start_time < 0.1:
                ret, frame = cap.read()
                cv2.imshow("Recognition", frame)
                cv2.waitKey(1)
        if name == "Unknown":
            alarm_on_unknown_face()
            save_unknown_image(image, image_count)
            image_count += 1

        recognized_names.append(name)

    return faces, recognized_names, image_count


def draw_results(image, faces, names):
    for (face, name) in zip(faces, names):
        x, y, w, h = face.left(), face.top(), face.width(), face.height()

        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)


def ask_renew_dataset():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askquestion("Renew Dataset", "Do you want to renew the dataset?")
    root.destroy()
    return result == 'yes'


def main():
    image_count = 0
    known_faces_dir = r"C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\CustomDataset\Known Faces"
    renew = ask_renew_dataset()
    known_names, known_encodings = load_known_faces(known_faces_dir, renew=renew)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        faces, names, image_count = recognize_faces(frame, known_names, known_encodings, image_count, cap)

        draw_results(frame, faces, names)

        cv2.imshow("Recognition", frame)

        key = cv2.waitKey(1)

        if key == 27:
            print("Exiting...")
            break
        elif key == ord('r'):
            review_data(None)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    create_gui()
