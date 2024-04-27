import cv2
import os
import face_recognition 
from images import face_utils as utils
from images import db_manager as db_manager_module


def main(): 

    if not os.path.exists("images/faces"):
            os.makedirs("images/faces")
            print("Nueva carpeta: faces")

    face_manager = utils.FaceManager()
    answer = None

    while answer != "no":
        answer = input("Quieres agregar nuevas fotos? [si/no] ").lower()

        if answer == "si":
            capturer = utils.PhotoCapturer()
            new_photos = capturer.capture_photo()
            if new_photos:
                username = input("Escribe el nombre de la persona capturada para crearle un directorio: ").capitalize()
                face_manager.save_faces(username, new_photos)
            break
     
    faces_path = "images/faces"
    encodings_dict = face_manager.encode_faces(faces_path)

    face_detector = utils.FaceDetector()
    face_detector.live_comparison(encodings_dict)

    # Guarda las codificaciones en la base de datos para un rendimiento mas eficiente
    answer = None
    while answer != "no":
        answer = input("¿Desea guardar las codificaciones en la base de datos? [si/no]: ").lower()
        
        if answer == "si":
            db_manager = db_manager_module.DatabaseManager("encodings.db")
            db_manager.connect()
            db_manager.create_table()

            # Insertar encodings en la base de datos
            for username, encodings in encodings_dict.items():
                for encoding in encodings:
                    db_manager.insert_encoding(username, str(encoding.tolist()))

            db_manager.close()
            print("Encodings guardados exitosamente en la base de datos.")
            break

    

if __name__ == "__main__":
    main()


