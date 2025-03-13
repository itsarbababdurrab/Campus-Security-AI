from scipy.spatial import distance  # Import the distance function from scipy to calculate Euclidean distances between face encodings.
import time
import Connection_to_DB
import Detection_Recognition_Essentials
import cv2
import Unknown_Face_Actions
import Known_Face_Actions
import datetime


# global cap  # Make cap global, so it can be accessed in recognize_faces
def recognize_faces(image, known_names, known_encodings, cap,  tolerance=0.5):
    faces = Detection_Recognition_Essentials.detect_faces(image)  # Detect faces in the new image.
    landmarks = Detection_Recognition_Essentials.get_landmarks(image, faces)  # Get facial landmarks for the detected faces.
    encodings = Detection_Recognition_Essentials.get_face_encodings(image, landmarks)  # Compute face encodings for the landmarks.

    recognized_names = []  # Initialize a list to store recognized names.

    for encoding in encodings:  # Iterate through each face encoding.
        matches = []  # Initialize a list to store distances between the face encoding and known encodings.

        for known_encoding in known_encodings:  # Iterate through each known face encoding.
            dist = distance.euclidean(known_encoding, encoding)  # Compute the Euclidean distance between the known encoding and the current encoding.
            matches.append(dist)  # Append the distance to the list.

        best_match_index = min(range(len(matches)), key=matches.__getitem__)  # Find the index of the smallest distance.

        if matches[best_match_index] < tolerance:  # Check if the smallest distance is within the tolerance.
            name = known_names[best_match_index]  # Get the name corresponding to the best match.
            Known_Face_Actions.current_time()
            Connection_to_DB.insert_recognition(name, datetime.datetime.now())

        else:
            name = "Unknown"  # Label as "Unknown" if no match is within the tolerance.
            start_time = time.time()
            while time.time() - start_time < 0.1:  # 0.1-second delay
                ret, frame = cap.read()  # Capture a new frame from the webcam
                cv2.imshow("Recognition", frame)  # Continue showing the live feed
                cv2.waitKey(1)  # Necessary to update the frame
                cv2.destroyAllWindows()
        if name == "Unknown":
            Unknown_Face_Actions.alarm_on_unknown_face()
            Unknown_Face_Actions.save_unknown_image(image, time.localtime())

        recognized_names.append(name)  # Append the recognized name to the list.

    return faces, recognized_names  # Return the detected faces and recognized names.
