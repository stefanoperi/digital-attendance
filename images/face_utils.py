import cv2
import os
import face_recognition
import time

class FaceDetector:
    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier("classifiers/frontalface_classifier.xml")

    def detect_faces(self, image):
        # Detecta caras en una imagen y devuelve las coordenadas de los rectángulos que las encierran
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_classifier.detectMultiScale(gray_image, 1.1, 5)
        return faces
    
    def live_comparison(self, encodings_dict):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        start_time = time.time()  # Get start time
        num_frames = 0 

        while True:
            ret, frame = cap.read()
            if ret == False:
                break
            frame = cv2.flip(frame, 1)
            orig = frame.copy()
            faces = self.detect_faces(frame)

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
            num_frames += 1  # Increment frame counter
    
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            # Calculate fps
            fps = num_frames / elapsed_time
            # Display fps
            print(f"FPS: {fps:.2f}")


            k = cv2.waitKey(1) & 0xFF
            #Si toca la tecla ESC
            if k == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

class PhotoCapturer:
    def __init__(self):
        self.face_detector = FaceDetector()
        self.images_path = "images/input_images"

    def capture_photo(self):
        # Captura fotos desde la cámara con el display del detector de caras
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Error: No se pudo abrir la cámara")

        captured_photos = []
        while True:
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError("Error al capturar el frame")

            faces = self.face_detector.detect_faces(frame)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imshow("frame", frame)
          

            captured_photos.append(frame.copy())
            print("Foto tomada\n")
            
            # Si toca "ESC", cerrar 
            key = cv2.waitKey(1)
            if key == 27:  
                break

        cap.release()
        cv2.destroyAllWindows()
        return captured_photos
    


class FaceManager:
    # Clase para gestionar y guardar imágenes de caras en carpetas
    def __init__(self):
        self.face_detector = FaceDetector()
        self.faces_folder = "images/faces"

    def save_faces(self, user_folder, images):    
        # Guarda las imágenes de las caras en una carpeta asignada al usuario capturado    
        folder_path = os.path.join(self.faces_folder, user_folder)
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Nueva carpeta creada: {user_folder}")
            else:
                print(f"Ya existe un directorio con el nombre {user_folder}")
                
            count = len(os.listdir(folder_path)) + 1
            for image in images:
                face_detected = self.face_detector.detect_faces(image)
                for (x, y ,w , h) in face_detected:
                    face_area = image[y:y + h, x:x + w]
                    cv2.imwrite(os.path.join(folder_path, f"{user_folder}_{count}.jpg"), face_area)
                    count += 1
                    print("Imagen de cara guardada")
                    
        except Exception as e:
            print(f"Error al guardar las imagenes: {e}")
    
    def encode_faces(self, faces_path):
        encodings_dict = {}
        # Iterar sobre cada carpeta de los usuarios

        for user_folder in os.listdir(faces_path):
            user_faces_path = os.path.join(faces_path, user_folder)

            # Lista para almacenar todas las codificaciones faciales de la persona actual
            person_encodings = []

            for user_faces in os.listdir(user_faces_path):
                image_path = os.path.join(user_faces_path, user_faces)
                image = cv2.imread(image_path)
                # Cambiar formato de colores a RGB para face_recognition
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
                f_coding = face_recognition.face_encodings(image, known_face_locations = [(0, 150, 150, 0)])[0]
                person_encodings.append(f_coding)

            # Agregar las codificaciones faciales de la persona al diccionario
            if person_encodings:
                encodings_dict[user_folder.split(".")[0]] = person_encodings
        
        return encodings_dict
    

"""
Cambios evidentes a realizar:
    - Optimizar codigo (Probando otras librerias de deteccion)
    - Solucionar enumerado de caras guardadas
    - Agregar detector de caras de perfil
    - Agregar mas posibilidades de eleccion del usuario
"""