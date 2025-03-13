import cv2
from playsound import playsound


def save_unknown_image(image, datetime):
    file_path = rf"C:\Users\User\PycharmProjects\AI-Based_Campus_Security_System_D-lib\UnKnown_Faces\UK_face_{datetime}.jpg"
    cv2.imwrite(file_path, image)
    print(f"Image of unknown face saved as {file_path}")


def alarm_on_unknown_face():
    playsound('Alarm Sound/chin_tapak_dum_dum.mp3')
