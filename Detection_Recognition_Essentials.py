import os
import cv2
import Main
import pickle


def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert the image to grayscale as the face detector works on grayscale images.
    faces = Main.detector(gray)  # Detect faces in the grayscale image.
    return faces  # Return the detected face bounding boxes.


def get_landmarks(image, faces):
    landmarks = []  # Initialize a list to store facial landmarks.
    for face in faces:  # Iterate through each detected face.
        shape = Main.predictor(image, face)  # Predict facial landmarks for the detected face.
        landmarks.append(shape)  # Append the landmarks to the list.
    return landmarks  # Return the list of facial landmarks.


def get_face_encodings(image, landmarks):
    encodings = []  # Initialize a list to store face encodings.
    for landmark in landmarks:  # Iterate through each set of facial landmarks.
        encoding = Main.face_rec_model.compute_face_descriptor(image, landmark)  # Compute the face encoding from the landmarks.
        encodings.append(encoding)  # Append the encoding to the list.
    return encodings  # Return the list of face encodings.


def load_encodings(filename='known_faces.pkl'):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return [], []
