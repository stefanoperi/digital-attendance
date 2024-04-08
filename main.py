import cv2
import os
import face_recognition
from images import face_utils as utils


# Leyendo video
def main(): 

    if not os.path.exists("images/faces"):
            os.makedirs("images/faces")
            print("Nueva carpeta: faces")

    answer = input("Quieres agregar nuevas fotos? [si/no] ").lower()
    face_manager = utils.FaceManager()
    if answer == "si":
        capturer = utils.PhotoCapturer()
        new_photos = capturer.capture_photo()

        if new_photos:
            username = input("Escribe el nombre de la persona capturada para crearle un directorio: ").capitalize()
            face_manager.save_faces(username, new_photos)


    elif answer != "no":
        raise ValueError("Respuesta Invalida")
     
    faces_path = "images/faces"
    encodings_dict = face_manager.encode_faces(faces_path)

    face_detector = utils.FaceDetector()
    face_detector.live_comparison(encodings_dict)

if __name__ == "__main__":
    main()


