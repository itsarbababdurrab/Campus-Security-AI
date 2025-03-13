import os  # Import the OS module for interacting with the operating system, like handling file paths and directories.
import cv2  # Import OpenCV for image processing and computer vision tasks.
import Known_Face_Actions
import Detection_Recognition_Essentials


def load_known_faces(known_faces_dir, save_file='known_faces.pkl', renew=False):
    if not renew:
        known_names, known_encodings = Detection_Recognition_Essentials.load_encodings(save_file)
        if known_names:  # If encodings are already loaded, skip processing
            print("Loaded known faces from file.")
            return known_names, known_encodings

    print("load_known_faces from Images")  # Print a message indicating the function has been called.
    known_names = []  # List to store the names of known individuals.
    known_encodings = []  # List to store the face encodings of known individuals.

    if not os.path.exists(known_faces_dir):  # Check if the directory containing known faces does not exist.
        print(f"Directory {known_faces_dir} does not exist!")  # Print an error message.
        return known_names, known_encodings  # Return empty lists if the directory does not exist.

    print(f"Loading faces from directory: {known_faces_dir}")  # Print the directory being processed.

    for person_name in os.listdir(known_faces_dir):  # Iterate through each person's directory in the known faces' directory.
        person_dir = os.path.join(known_faces_dir, person_name)  # Construct the full path to the person's directory.
        print(f"Processing directory: {person_dir}")  # Print the directory being processed.

        if not os.path.isdir(person_dir):  # isdir() method is used to check whether a given path exists.
            print(f"{person_dir} is not a directory!")  # Print an error message.
            continue  # Skip to the next iteration.

        for image_name in os.listdir(person_dir):  # Iterate through each image file in the person's directory.
            image_path = os.path.join(person_dir, image_name)  # Construct the full path to the image file.
            print(f"Loading image: {image_path}")  # Print the image being loaded.

            image = cv2.imread(image_path)  # Read the image from the file.
            faces = Detection_Recognition_Essentials.detect_faces(image)  # Detect faces in the image.
            landmarks = Detection_Recognition_Essentials.get_landmarks(image, faces)  # Get facial landmarks for the detected faces.
            encodings = Detection_Recognition_Essentials.get_face_encodings(image, landmarks)  # Compute face encodings for the landmarks.

            for encoding in encodings:  # Iterate through each face encoding.
                known_names.append(person_name)  # Store the person's name.
                known_encodings.append(encoding)  # Store the corresponding face encoding.

    Known_Face_Actions.save_encodings(known_names, known_encodings)  # Save encodings to file
    return known_names, known_encodings  # Return the lists of known names and encodings.
