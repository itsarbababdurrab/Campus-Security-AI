import cv2
import dlib
import Taking_Images_For_DataSet
import Face_Detection
import Face_Recognition
import Known_Face_Actions
import Connection_to_DB


# Load face detector, shape predictor, and face recognition model
detector = dlib.get_frontal_face_detector()  # Initialize d-lib's frontal face detector to detect faces in images.
predictor = dlib.shape_predictor(r'C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\DataModels\shape_predictor_68_face_landmarks.dat')  # This function loads a pre-trained model that can detect facial landmarks (specific key points on the face such as the eyes, nose, mouth, etc.) in a face detected in an image.
face_rec_model = dlib.face_recognition_model_v1(r'C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\DataModels\dlib_face_recognition_resnet_model_v1.dat')   # This function loads a pre-trained deep learning model that computes 128-dimensional face encodings, which are numerical representations of facial features used for recognizing or comparing faces.


def main():
    known_faces_dir = r"C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\CustomDataset\Known Faces"  # Path to the directory with known faces.
    result = Taking_Images_For_DataSet.asking_new_entry_to_dataset()
    if result:
        Taking_Images_For_DataSet.make_new_dataset()

    renew = Taking_Images_For_DataSet.ask_renew_dataset()
    known_names, known_encodings = Face_Detection.load_known_faces(known_faces_dir, renew=renew)  # Load known faces and their encodings.

    # global cap  # Make cap global, so it can be accessed in recognize_faces
    cap = cv2.VideoCapture(0)  # Open the default webcam (0 usually refers to the built-in webcam).

    while True:  # Start an infinite loop to continuously capture frames from the webcam.
        ret, frame = cap.read()  # Capture a frame from the webcam.
        if not ret:  # Check if the frame was successfully captured.
            print("Failed to grab frame")  # Print an error message if the frame could not be captured.
            break  # Exit the loop.

        faces, names = Face_Recognition.recognize_faces(frame, known_names, known_encodings, cap)  # Recognize faces in the captured frame.

        Known_Face_Actions.draw_results(frame, faces, names)  # Draw the results (bounding boxes and names) on the frame.

        cv2.imshow("Recognition", frame)  # Display the image with the results in a window.

        key = cv2.waitKey(1)

        if key == 27:
            print("Exiting...")
            break
        elif key == ord('r'):  # 'r' key to review data
            pass

    cap.release()  # Release the webcam.
    cv2.destroyAllWindows()  # Close all OpenCV windows.


if __name__ == "__main__":
    main()  # Execute the main function if the script is run directly.
    Connection_to_DB.create_gui()
