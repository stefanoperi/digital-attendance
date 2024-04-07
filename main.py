import cv2
import os
import face_recognition
from images import face_extractor as extractor


# Leyendo video
def main(): 

    if not os.path.exists("images/faces"):
            os.makedirs("images/faces")
            print("Nueva carpeta: faces")

    answer = input("Quieres agregar nuevas fotos? [si/no] ").lower()
    if answer == "si":
        capturer = extractor.PhotoCapturer()
        new_photos = capturer.capture_photo()
        if new_photos:
            username = input("Escribe el nombre de la persona capturada para crearle un directorio: ").capitalize()

            face_manager = extractor.FaceManager()
            face_manager.save_faces(username, new_photos)

    elif answer != "no":
        raise ValueError("Respuesta Invalida")
     
    faces_path = "images/faces"
    encodings_dict = face_manager.encode_faces(faces_path)

    face_detector = extractor.FaceDetector()
   
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        frame = cv2.flip(frame, 1)
        orig = frame.copy()
        faces = face_detector.detect_faces(frame)

        for (x, y, w, h) in faces:
            #Codifica la ubicacion de la cara encontrada y la compara
            face = orig[y:y + h, x:x + w]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            actual_encoding = face_recognition.face_encodings(face, known_face_locations = [(0, w, h, 0)])[0]
            
            for key in encodings_dict.keys():
                result = face_recognition.compare_faces(encodings_dict[key], actual_encoding)
                if True in result:
                    name = key
                    color = (125, 220, 0) 
                    break
                else:
                    name = "Desconocido"
                    color = (50, 50 , 255)
            
            cv2.rectangle(frame, (x, y + h), (x + w, y + h + 30), color, -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, name, (x, y + h + 25), 2, 1, (255, 255 , 255), 2, cv2.LINE_AA)
        
        cv2.imshow("Frame", frame)

        k = cv2.waitKey(1) & 0xFF
        #Si toca la tecla ESC
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


