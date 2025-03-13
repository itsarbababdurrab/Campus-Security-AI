import os
import cv2
import dlib
import tkinter as tk
from tkinter import messagebox


def ask_renew_dataset():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askquestion("Renew Dataset", "Do you want to renew the dataset?")
    root.destroy()
    return result == 'yes'


def asking_new_entry_to_dataset():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askquestion("Making New Dataset", "Do you want to Add someone New to DataSet?")
    return result == "yes"


def make_new_dataset():
    # Step 1: Create a new folder for saving cropped face images
    folder_name = input("Enter the student name")
    directory = fr"C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_d-lib\CustomDataset\Known Faces\{folder_name}"
    os.makedirs(directory, exist_ok=True)

    # Step 2: Initialize the webcam
    cap = cv2.VideoCapture(0)  # 0 is usually the built-in webcam

    # Step 3: Initialize the Dlib face detector
    detector = dlib.get_frontal_face_detector()

    # Initialize a counter for the images
    image_count = 0

    print("Press 'SPACE' to capture an image and crop to the face, 'ESC' to exit.")

    while True:
        # Step 4: Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Detect faces in the frame
        faces = detector(frame, 1)

        # Draw rectangles around detected faces
        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x - 30, y - 30), (x + w + 30, y + h + 30), (0, 255, 0), 2)

        # Show the frame in a window
        cv2.imshow('Webcam', frame)

        # Step 5: Wait for key press
        key = cv2.waitKey(1)

        if key == 27:  # ESC key to exit
            print("Exiting...")
            break
        elif key == 32:  # SPACE key to capture image
            if len(faces) == 0:
                print("No face detected")
            else:
                for face in faces:
                    # Extract the coordinates of the face
                    x, y, w, h = face.left(), face.top(), face.width(), face.height()

                    # Crop the face from the image
                    cropped_face = frame[y - 30:y + h + 30, x - 30:x + w + 30]

                    # Increment the image counter
                    image_count += 1
                    file_name = f"face_{image_count}.jpg"
                    file_path = os.path.join(directory, file_name)

                    # Save the cropped face image
                    cv2.imwrite(file_path, cropped_face)
                    print(f"Cropped face saved as {file_name}")

    # Step 6: Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()

    print(f"All cropped face images saved in folder '{directory}" " ' ")
