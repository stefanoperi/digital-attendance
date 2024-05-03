import cv2
import os
import face_recognition 
import numpy as np
import shutil 

from images import face_utils as utils
from images import db_manager as db_module


def main(): 

    if not os.path.exists("images/faces"):
            os.makedirs("images/faces")
            print("Nueva carpeta: faces")

    face_manager = utils.FaceManager()
    faces_path = "images/faces"
    
    db_manager = db_module.DatabaseManager("encodings.db")
    db_manager.connect()
  
    new_encodings = {} 
    new_photos = {}

    answer = None
    while answer != "no":
        answer = input("Quieres agregar nuevas fotos? [si/no] ").lower()

        if answer == "si":
            capturer = utils.PhotoCapturer()
            new_photos = capturer.capture_photo()

            if new_photos:
                username = input("Escribe el nombre de la persona capturada para crearle un directorio: ").capitalize()
                face_manager.save_faces(username, new_photos)
                new_encodings = face_manager.encode_faces(faces_path)
            break
    
    db_manager.create_table()
    mixed_encodings = db_manager.mix_encodings(new_encodings)
    face_detector = utils.FaceDetector()
    face_detector.live_comparison(mixed_encodings)
 

    # Guarda las codificaciones en la base de datos para un rendimiento mas eficiente
    answer = None
    if new_photos:
        while answer != "no":
            answer = input("¿Desea guardar las codificaciones en la base de datos? [si/no]: ").lower()
            
            if answer == "si":
                db_manager.create_table()

                # Insertar encodings en la base de datos
                for username, encodings in new_encodings.items():
                    for encoding in encodings:
                        db_manager.insert_encoding(username, encoding.tobytes())

                db_manager.close()
                print("Encodings guardados exitosamente en la base de datos.")
                break

        try: 
            shutil.rmtree(f"{face_manager.faces_folder}/{str(username)}")
            return
        except OSError as e:
            print(f"Error al eliminar la carpeta: {e}")
    

    

if __name__ == "__main__":
    main()


