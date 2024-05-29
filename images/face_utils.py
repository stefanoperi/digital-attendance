import cv2
import os
import face_recognition
from images import spreadsheet_module
from images import db_module 
import time

db_manager = db_module.DatabaseManager("encodings.db")
db_manager.connect()
class FaceDetector:
    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier("./classifiers/frontalface_classifier.xml")
        self.confirmation_threshold = 5  # Número de detecciones consecutivas requeridas para confirmar la presencia
        self.confirmed_person_id = None
        self.consecutive_detections = 0

    def detect_faces(self, image):
        # Detecta caras en una imagen y devuelve las coordenadas de los rectángulos que las encierran
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_classifier.detectMultiScale(gray_image, 1.2, 5)
        return faces
    
    def live_comparison(self, encodings_dict, student):
        cap = cv2.VideoCapture(0)
        # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
   
        start_time = time.time()  # Empieza a tomar el tiempo
        num_frames = 0 

        while True:
            success, frame = cap.read()
            if not success or frame is None:
                print("No se pudo leer la camara")
                continue

            frame = cv2.resize(frame, (640, 480))  
            frame = cv2.flip(frame, 1)
            orig = frame.copy()
            faces = self.detect_faces(frame)

            for (x, y, w, h) in faces:
                # Codifica la ubicacion de la cara detectada en tiempo real
                face = orig[y:y + h, x:x + w]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB) 
                actual_encoding = face_recognition.face_encodings(face, known_face_locations = [(0, w, h, 0)])[0] 
                
                person_found, color = self.identify_person(encodings_dict, actual_encoding, student)
                self.draw_info(frame, x, y, w, h, person_found, color)

                self.confirm_presence(person_found)
      
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

    def identify_person(self, encodings_dict, actual_encoding, student):
        unknown = "Desconocido"
        person_found = {"name": unknown, "id": unknown}
        color = (0, 0, 250)  # Rojo
        
        # Compara codificaciones de cara detectada con la lista de codificaciones por cada persona en la base de datos
        for key in encodings_dict:
            result = face_recognition.compare_faces(encodings_dict[key], actual_encoding)
            if True in result:
                person_found["id"] = key
                color = (125, 220, 0)
                break

        # Encontrar el nombre de la persona encontrada
        if student and person_found["id"] == student.student_id:  # Si coincide con el ultimo estudiante capturado
            person_found["name"] = student.full_name
        else:
            db_manager.cursor.execute("SELECT student_id FROM encodings WHERE student_id = ?", (person_found["id"],))
            result = db_manager.cursor.fetchone()
            
            if result: # Si el DNI encontrado esta en la base de datos
                db_manager.cursor.execute("SELECT full_name FROM encodings WHERE student_id = ?", (person_found["id"],))
                name_result = db_manager.cursor.fetchone()
                person_found["name"] = name_result[0] if name_result else unknown  # Si el nombre fue encontrado

            else: # Si el DNI NO fue encontrado
                person_found["name"] = unknown

        return person_found, color
    
    def draw_info(self, frame, x, y, w, h, person_found, color):
        cv2.rectangle(frame, (x, y + h), (x + w, y + h + 50), color, -1)  # Rectángulo inferior
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)  # Rectángulo de la cara

        # Dibujar el nombre y el DNI
        cv2.putText(frame, person_found["name"], (x, y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)  # Nombre
        cv2.putText(frame, f"ID: {person_found['id']}", (x, y + h + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)  # DNI
    
    def confirm_presence(self, person_found):
        if self.confirmed_person_id == person_found["id"]:
            self.consecutive_detections += 1
        else:
            self.confirmed_person_id = person_found["id"]
            self.consecutive_detections = 1
        
        if self.consecutive_detections >= self.confirmation_threshold:
            print(f"La presencia de {person_found['name']} ha sido confirmada.")

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
                print(f"Iluminacion: {brightness:.2f}  / 120 \n")

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

    def save_faces(self, student, images):    
        # Guarda las imágenes de las caras en una carpeta asignada al usuario capturado    

        # Path de la carpeta donde se guardarán las imágenes de caras del usuario
        folder_path = os.path.join(self.faces_folder, student.full_name)
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Nueva carpeta creada: {student.full_name}")
            else:
                print(f"Ya existe un directorio con el nombre {student.full_name}")
                
            count = len(os.listdir(folder_path)) + 1
            # Itera sobre imagenes y guarda la seccion de la cara de cada una
            for image in images:
                face_detected = self.face_detector.detect_faces(image)
                for (x, y ,w , h) in face_detected:
                    face_area = image[y:y + h, x:x + w]
                    cv2.imwrite(os.path.join(folder_path, f"{student.full_name}_{count}.jpg"), face_area)
                    count += 1
                    print("Imagen de cara guardada")
                    
        except Exception as e:
            print(f"Error al guardar las imagenes: {e}")
    
    def encode_faces(self, faces_path, student):
        encodings_dict = {}
        # Iterar sobre cada carpeta de los usuarios
        count = 0
        for user_folder in os.listdir(faces_path):
            user_faces_path = os.path.join(faces_path, user_folder)

            # Lista para almacenar todas las codificaciones faciales de la persona actual
            person_encodings = []
            
            # Codificar cada imagen
            for user_faces in os.listdir(user_faces_path):
                image_path = os.path.join(user_faces_path, user_faces)
                image = cv2.imread(image_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # Cambiar formato de colores a RGB 
        
                f_coding = face_recognition.face_encodings(image, known_face_locations = [(0, 150, 150, 0)])[0]
                person_encodings.append(f_coding)
                print(f"Cara codificada numero: {count}")
                count += 1
                

            # Agregar la lista de codificaciones faciales de la persona al diccionario
            if person_encodings:
                encodings_dict[student.student_id] = person_encodings
        
        return encodings_dict
    

"""
Cambios evidentes a realizar:
    - Descentralizar el main.py
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