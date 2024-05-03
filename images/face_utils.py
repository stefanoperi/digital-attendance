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
   
        start_time = time.time()  # Empieza a tomar el tiempo
        num_frames = 0 

        while True:
            success, frame = cap.read()
            frame = cv2.resize(frame, (640, 480))  
            if success == False:
                break
            frame = cv2.flip(frame, 1)
            orig = frame.copy()
            faces = self.detect_faces(frame)

            for (x, y, w, h) in faces:
                # Codifica la ubicacion de la cara detectada en tiempo real
                face = orig[y:y + h, x:x + w]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB) 
                actual_encoding = face_recognition.face_encodings(face, known_face_locations = [(0, w, h, 0)])[0] 
                
                name = "Desconocido"
                color = (50, 50 , 255)
                
                # Compara codificaciones de cara detectada con la lista de codificaciones por cada persona en la base de datos
                for key in encodings_dict:
                    result = face_recognition.compare_faces(encodings_dict[key], actual_encoding)
                    if True in result:
                        name = key
                        color = (125, 220, 0) 
                        break

                cv2.rectangle(frame, (x, y + h), (x + w, y + h + 30), color, -1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, name, (x, y + h + 25), 2, 1, (255, 255 , 255), 2, cv2.LINE_AA)
            
            cv2.imshow("Frame", frame)
    
            elapsed_time = time.time() - start_time
            fps = num_frames / elapsed_time  # Calcula FPS
            print(f"FPS: {fps:.2f}")

            num_frames += 1  

            k = cv2.waitKey(1) & 0xFF
            #Si toca la tecla ESC
            if k == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

class PhotoCapturer:
    def __init__(self):
        self.face_detector = FaceDetector()

    def capture_photo(self):
        # Captura fotos desde la cámara con el display del detector de caras
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Error: No se pudo abrir la cámara")

        captured_photos = []
        photo_count = 0
        while True:
            success, frame = cap.read()
            frame = cv2.resize(frame, (640, 480))  
            if not success:
                raise RuntimeError("Error al capturar el frame")

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = cv2.mean(gray_frame)[0]
            faces = self.face_detector.detect_faces(frame)
          
            for (x, y, w, h) in faces:
                cv2.rectangle(frame,(x, y), (x+w, y+h), (0, 255, 0), 2)
                key = cv2.waitKey(1)
                if brightness >= 120 and key == 32: # Si toca "SPACE BAR" e Iluminacion >= 100
                    captured_photos.append(frame.copy())
                    photo_count += 1
                    print("Foto tomada\n")
                print(f"Iluminacion: {brightness:.2f} / 120 \n")

            cv2.imshow("frame", frame)
          
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

        # Path de la carpeta donde se guardarán las imágenes de caras del usuario
        folder_path = os.path.join(self.faces_folder, user_folder)
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Nueva carpeta creada: {user_folder}")
            else:
                print(f"Ya existe un directorio con el nombre {user_folder}")
                
            count = len(os.listdir(folder_path)) + 1
            # Itera sobre imagenes y guarda la seccion de la cara de cada una
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
        count = 0
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
                print(f"Cara codificada numero: {count}")
                count += 1
                

            # Agregar la lista de codificaciones faciales de la persona al diccionario
            if person_encodings:
                encodings_dict[user_folder.split(".")[0]] = person_encodings
        
        return encodings_dict
    

"""
Cambios evidentes a realizar:
    - Agregar las graphics de la asistencia digital 
    - Esperar X cantidad de segundos y ahi enviar una orden la google sheets
        para confirmar que la persona detectada sea esa 
    - Agregar la parte de la asistencia digital con gspread
 
    - Acelerar gpu con OpenCl
    - Comentar mejor el codigo :)
    - Agregar detector de caras de perfil

"""

"""
Notas:
    Usar gspread implicara tener WiFi a la hora de presentar el proyecto
    La precision de la deteccion efectivamente mejora al haber mas fotos de cada persona
    La bajada de fps radica sobre todo en tener q codificar y comparar en tiempo real las caras entrantes

"""