import datetime
import pickle
import cv2


def current_time():
    current_time_stamp = datetime.datetime.now().replace(microsecond=0)
    print("Current Date and Time:", current_time_stamp)


def save_encodings(known_names, known_encodings, filename='known_faces.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump((known_names, known_encodings), f)


def draw_results(image, faces, names):
    for (face, name) in zip(faces, names):  # Iterate through each face and its recognized name.
        x, y, w, h = face.left(), face.top(), face.width(), face.height()  # Get coordinates of the face bounding box.

        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw a green rectangle around the face.
        cv2.putText(image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)    # Label the face with the recognized name.
