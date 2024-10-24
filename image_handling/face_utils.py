import cv2
import os
import face_recognition
from spreadsheet import spreadsheet_module
from database import db_module 
import numpy as np
import time
import datetime
import logging
from kivy.graphics.texture import Texture
import random

db_directory = "database"
db_file = "encodings.db"
db_path = os.path.join(db_directory, db_file)

os.makedirs(db_directory, exist_ok=True)

db_manager = db_module.DatabaseManager(db_path)
db_manager.connect()
db_manager.connect()

sheet_manager = spreadsheet_module.GoogleSheetManager('Toma de Asistencia') # Open by the name of the google spreadsheet

def kivy_to_cv2(kivy_camera):
    # Ensure texture is valid and retrieve pixel data
    if kivy_camera.texture:
        frame_data = kivy_camera.texture.pixels
        if isinstance(frame_data, memoryview):
            frame_data = bytes(frame_data)
    else:
        raise ValueError("No valid texture found in the Kivy camera object.")

    # Convert frame data to numpy array
    buf1 = np.frombuffer(frame_data, dtype=np.uint8)

    # Reshape to image form (height, width, 4 channels)
    frame = np.reshape(buf1, (kivy_camera.texture.height, kivy_camera.texture.width, 4))  
    
    # Convert from RGBA to BGR (format used by OpenCV)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
    return frame


class FaceDetector:
    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier("./classifiers/frontalface_classifier.xml")
        self.confirmation_threshold = 15  # Number of consecutive detections required to confirm presence
        self.confirmed_person_id = None
        self.consecutive_detections = 0


    def detect_faces(self, image):
        # Detects faces in an image and returns the coordinates of the rectangles enclosing them
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_classifier.detectMultiScale(gray_image, 1.2, 5)
        return faces
    
    def live_comparison(self, encodings_list, kivy_camera):

        # Convert kivy camera into compatible cv2 format
        frame = kivy_to_cv2(kivy_camera)
    
        unknown = "Unknown"
        person_found = {"name": unknown, "id": unknown, "grade": unknown} 
        if frame is not None: 
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.flip(frame, 1)

            # Detect faces in frame
            faces = self.detect_faces(frame)
            
            # Process each face found
            for (x, y, w, h) in faces:
                face = frame[y:y + h, x:x + w]  # Extract face region
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)  
        
                try:
                    # Encode face found
                    found_encoding = face_recognition.face_encodings(face, known_face_locations=[(0, w, h, 0)])[0]

                    # Identify person based on the encoding found
                    person_found, color = self.identify_person(encodings_list, found_encoding, person_found)
                    self.draw_info(frame, x, y, w, h, person_found, color)
                    
                    # Confirm presence in Excel spreadsheet
                    self.confirm_presence(person_found)
                except IndexError:
                    continue  
                
            # Course selected
            text = f"Course of attendance: {sheet_manager.grade_selected}"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
            x = frame.shape[1] - text_width - 10 
            y = text_height + 10  
            cv2.rectangle(frame, (x - 5, y - text_height - 5), (x + text_width + 5, y + 5), (0, 0, 0), cv2.FILLED)
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

            # Convert CV2 modified image to a Kivy texture
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
            frame = cv2.flip(frame, 0)  
            buf = frame.tobytes()  
            
            # Create Kivy texture with image data
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            return image_texture, person_found, self.consecutive_detections, self.confirmation_threshold


    def identify_person(self, encodings_list, actual_encoding, person_found):
        """ Compare detected face encodings with the list of encodings for each person in the database """
        color = (0, 0, 250) 
        
        # Iterate over the list of tuples (student_id, encoding)
        for student_id, encoding in encodings_list:
            encoding = np.fromstring(encoding, dtype=np.float64) # Convert to numpy array
            result = face_recognition.compare_faces([encoding], actual_encoding)
            if True in result:
                person_found["id"] = student_id
                result = db_manager.cursor.execute(
                    "SELECT student_id, full_name, grade FROM encodings WHERE student_id = ?", 
                    (person_found["id"],)
                ).fetchone()
                if result:
                    person_found["name"] = result[1]
                    person_found["grade"] = result[2]
                    color = (125, 220, 0)  # Green
                
        return person_found, color

    
    def draw_info(self, frame, x, y, w, h, person_found, color):
        cv2.rectangle(frame, (x, y + h), (x + w, y + h + 50), color, -1)  # Bottom rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)  # Face rectangle

        # Draw the name and ID
        cv2.putText(frame, person_found["name"], (x, y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)  # Name
        cv2.putText(frame, f"ID: {person_found['id']}", (x, y + h + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)  # ID
    
 
    def confirm_presence(self, person_found):
        if self.confirmed_person_id == person_found["id"]:
            self.consecutive_detections += 1
        else:
            self.confirmed_person_id = person_found["id"]
            self.consecutive_detections = 1
        
        if self.consecutive_detections >= self.confirmation_threshold:
            time_found = datetime.datetime.now()
            sheet_manager.register_presence(person_found, time_found)
            self.consecutive_detections = 0

         

class PhotoCapturer:
    def __init__(self):
        self.face_detector = FaceDetector()

    def capture_photo(self, kivy_camera, photo_count):
        
        # Convert kivy camera into compatible cv2 format
        frame = kivy_to_cv2(kivy_camera)
    
        # Capture photos from the camera with face detector display

        self.photo_count = photo_count
        self.photo_threshold = 250
        self.brightness = None
        self.brightness_threshold = 100
        face_detected = False

        frame = cv2.resize(frame, (640, 480))  
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.brightness = cv2.mean(gray_frame)[0]
        faces = self.face_detector.detect_faces(frame)
        
        for (x, y, w, h) in faces:
            self.draw_info(frame, x, y, w, h) 
            face_detected = True

        # Convert CV2 modified image to a Kivy texture
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
        frame = cv2.flip(frame, 0)  
        buf = frame.tobytes()  

        # Create Kivy texture with image data
        image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

        thresholds = {
            "photo": self.photo_threshold, 
            "brightness": self.brightness_threshold}
      
        return image_texture, self.brightness, face_detected, thresholds
   
    def draw_info(self, frame, x, y, w, h):
        # Round the brightness value
        self.brightness = round(self.brightness)
        
        # Define the texts to be displayed
        brightness_fraction = f"Brightness: {self.brightness} / {self.brightness_threshold}"
        photo_text = f"Photos taken: {self.photo_count} / {self.photo_threshold}"
        
        # Determine text color based on brightness threshold
        if self.brightness >= self.brightness_threshold:
            text_color = (0, 255, 0)  # Green
        else:
            text_color = (0, 0, 255)  # Red
        
        # Calculate text size and positions
        brightness_text_size, _ = cv2.getTextSize(brightness_fraction, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        photo_text_size, _ = cv2.getTextSize(photo_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        
        # Define padding
        padding = 5

        # Compute the rectangle size
        rect_width = max(brightness_text_size[0], photo_text_size[0]) + 2 * padding
        rect_height = brightness_text_size[1] + photo_text_size[1] + 3 * padding
        
        # Position the rectangle and texts
        text_x = frame.shape[1] - rect_width - padding
        text_y = padding + brightness_text_size[1] + padding
        
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Draw background rectangle for text
        cv2.rectangle(frame, 
                    (text_x - padding, text_y - padding), 
                    (text_x + rect_width, text_y + rect_height), 
                    (0, 0, 0), 
                    cv2.FILLED)
        
        # Overlay the texts on top of the rectangle
        cv2.putText(frame, brightness_fraction, (text_x, text_y + brightness_text_size[1] - padding), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2, cv2.LINE_AA)
        cv2.putText(frame, photo_text, (text_x, text_y + brightness_text_size[1] + padding + photo_text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)



class FaceManager:
    # Class to manage and save face images in folders
    def __init__(self):
        self.face_detector = FaceDetector()
        self.faces_folder = "image_handling/faces"
        

    def save_faces(self, student, images_folder, student_faces_path):    
        # Save face images in a folder assigned to the captured user    
        success = False
        
        try:
            if not os.path.exists(student_faces_path):
                os.makedirs(student_faces_path)
                logging.info(f"New folder created: {student.full_name}")
            else:
                logging.info(f"A directory with the name {student.full_name} already exists")
                
            count = len(os.listdir(student_faces_path)) + 1

            # Iterate over images and save the face section of each one
            for image_filename in os.listdir(images_folder):
                image_path = os.path.join(images_folder, image_filename)
                image = cv2.imread(image_path)
            
                if image is None:
                    logging.warning(f"Failed to load image: {image_path}")
                    continue

                face_detected = self.face_detector.detect_faces(image)
                for (x, y ,w , h) in face_detected:
                    face_area = image[y:y + h, x:x + w]
                    cv2.imwrite(os.path.join(student_faces_path, f"{student.full_name}_{count}.jpg"), face_area)
                    count += 1
                    logging.info("Face image saved")

            # Remove residual raw images
            for file in os.listdir(images_folder):
                os.remove(os.path.join(images_folder, file))

            logging.info("All face images were saved")
            success = True

            return success
                    
        except Exception as e:
            print(f"Error saving images: {e}")
    
    def encode_faces(self, faces_path, student):
        encodings_dict = {}
        count = 0
        # Iterate over each user's folder
        for user_folder in os.listdir(faces_path):
            user_faces_path = os.path.join(faces_path, user_folder)

            # List to store all face encodings of the current person
            person_encodings = []
            
            # Encode each image
            for user_faces in os.listdir(user_faces_path):
                image_path = os.path.join(user_faces_path, user_faces)
                image = cv2.imread(image_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Change color format to RGB 
        
                f_coding = face_recognition.face_encodings(image, known_face_locations = [(0, 150, 150, 0)])[0]
                person_encodings.append(f_coding)
                logging.info(f"Face encoded number: {count}")
                count += 1
                
            # Add the person's face encodings list to the dictionary
            if person_encodings:
                encodings_dict[student.student_id] = person_encodings
        
        return encodings_dict
    
