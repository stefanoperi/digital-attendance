import kivy
import os
import shutil
import cv2
import face_recognition
import numpy as np

from image_handling import face_utils as utils
from database import db_module 
from spreadsheet import spreadsheet_module 

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown

class Student:
    def __init__(self, student_id, full_name, grade):
        self.student_id = student_id
        self.full_name = full_name
        self.grade = grade

def get_valid_input(options, prompt):
    while True:
        user_input = input(prompt).strip()
        if user_input in options:
            return user_input
        else:
            print(f"No spreadsheet is named {user_input}. The option {user_input} is not valid,  please try again.")

def delete_faces_folder(student, face_manager):
   try:
        shutil.rmtree(f"{face_manager.faces_folder}/{str(student.full_name)}")
   except FileNotFoundError as e:
        print(f"No leftover photos to delete :)")
   except OSError as e:
        raise OSError(f"Error deleting folder: {e}")

class AppResources:
    def __init__(self):
        if not os.path.exists("image_handling/faces"):
            os.makedirs("image_handling/faces")
            print("New folder: faces")

        self.face_manager = utils.FaceManager()
        self.faces_path = "image_handling/faces"

        db_directory = "database"
        db_file = "encodings.db"
        db_path = os.path.join(db_directory, db_file)

        os.makedirs(db_directory, exist_ok=True)

        self.db_manager = db_module.DatabaseManager(db_path)
        self.db_manager.connect()

        self.student_encodings = {}
        self.new_photos = None
        self.student = None

        self.capturer = utils.PhotoCapturer()
          
        self.sheet_manager = spreadsheet_module.GoogleSheetManager("Toma de Asistencia") # Open by the google spreadsheet's name
        self.worksheet_names = self.sheet_manager.read_worksheet_names() # Get course names


class MainScreen(BoxLayout):
    def __init__(self, transition_callback, resources, **kwargs):
        super().__init__(**kwargs)
        self.transition = transition_callback
        self.resources = resources

        self.orientation = 'horizontal'
    
        # Camera layout
        camera_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
        
        self.prompt_label = Label(text='Please select the course for attendance', font_size=20)
        camera_layout.add_widget(self.prompt_label)
        
        # Add buttons at the bottom of the camera
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), padding=[0,0,0,100])
        
      # Create the dropdown and its button
        self.dropdown = DropDown()
        for course_name in self.resources.worksheet_names:
            btn = Button(text=course_name, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)

        self.dropdown_button = Button(text='Course', size_hint=(None, None), size=(200, 44))
        self.dropdown_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.dropdown_button, 'text', x))
        
        button_layout.add_widget(self.dropdown_button)
        
        self.photo_button = Button(text='Add new photos', font_size=20)
        self.photo_button.bind(on_press=lambda instance: self.transition('capturer'))
        button_layout.add_widget(self.photo_button)
        
        # Add Camera widget
        #self.camera = Camera(play=True)
        #self.camera.size_hint = (1, 0.85)
        #camera_layout.add_widget(self.camera)

        camera_layout.add_widget(button_layout)
        
        # Add camera layout to the main layout
        self.add_widget(camera_layout)

        # Info layout
        info_layout = BoxLayout(orientation='vertical', padding=[10], size_hint=(0.3, 1))
        
        self.info_label = Label(text='Student Info', font_size=20)
        info_layout.add_widget(self.info_label)
        
        # Add more widgets to info_layout as needed, e.g., text inputs, additional labels, etc.
        
        self.add_widget(info_layout)

        # Initialize face detector
        self.face_detector = utils.FaceDetector()
        
        # Schedule the update method 30 times a second
        #Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        image_texture = self.face_detector.live_comparison(self.resources.student_encodings, self.resources.student, self.camera)
        self.camera.texture = image_texture

class DigitalAttendanceApp(App):
    def build(self):
        # Create the resources object
        resources = AppResources()

        # Create the screen manager
        self.sm = ScreenManager()
   
        # Create the main screen and add it to the ScreenManager
        main_screen = Screen(name='main')
        main_screen.add_widget(MainScreen(transition_callback=self.transition_to, resources=resources))
        self.sm.add_widget(main_screen)

        # Set the initial screen to the loading screen
        self.sm.current = 'main'

        return self.sm

    def transition_to(self, screen_name, *args):
        self.sm.current = screen_name


if __name__ == '__main__':
    
    DigitalAttendanceApp().run()


    

""" 
   

def main(): 

    if not os.path.exists("image_handling/faces"):
            os.makedirs("image_handling/faces")
            print("New folder: faces")
    

    face_manager = utils.FaceManager()
    faces_path = "image_handling/faces"
    
    db_directory = "database"
    db_file = "encodings.db"
    db_path = os.path.join(db_directory, db_file)

    os.makedirs(db_directory, exist_ok=True)

    db_manager = db_module.DatabaseManager(db_path)
    db_manager.connect()

    student_encodings = {} 
    new_photos = None
    student = None
    
    
    sheet_manager = spreadsheet_module.GoogleSheetManager("Toma de Asistencia") # Open by the google spreadsheet's name
    worksheet_names = sheet_manager.read_worksheet_names() # Get course names
    
    # Ask for the grade to work with
    if worksheet_names:
        grade = get_valid_input(worksheet_names, f"Enter the grade for attendance (Available options: {worksheet_names}) ") 
        sheet_manager.select_grade(grade)
        print(f"Information of {grade}: {sheet_manager.read_values()}")
    else:
        raise ValueError("No courses are currently available")
    

    answer = None
    while True:
        answer = input("Do you want to add new photos? [yes/no] ").lower()

        if answer == "yes":
            capturer = utils.PhotoCapturer()
            new_photos = capturer.capture_photo()

            if new_photos:
               full_name = input("Enter the full name of the captured person: ").strip().title()
               student_id = input("Enter the ID number of the captured person: ")
               student_grade = get_valid_input(worksheet_names, f"Enter the grade of the captured person (Available options: {worksheet_names}) ") 

               student = Student(student_id=student_id, full_name=full_name, grade=student_grade)
               # Ensure to delete remaining photos before adding new ones
               delete_faces_folder(student, face_manager)

               face_manager.save_faces(student, new_photos)
               student_encodings = face_manager.encode_faces(faces_path, student)
               break
            else:
                raise ValueError("No new photos have been taken")
                
            

        elif answer == "no":
            break
    
    db_manager.create_table()
    mixed_encodings = db_manager.mix_encodings(student_encodings)
    
    face_detector = utils.FaceDetector()
    face_detector.live_comparison(mixed_encodings, student)
    answer = None
   
    # Save student data in the database for more efficient performance
    if student_encodings:
        while True:
            answer = input("Do you want to save the person's data in the database? [yes/no]: ").lower()
            
            if answer == "yes":
                db_manager.create_table()

                # Insert encodings and information into the database
                for student_id, encodings in student_encodings.items():
                    for encoding in encodings:
                        db_manager.insert_encoding(student, encoding.tobytes())

                db_manager.close()
                print("Data successfully saved to the database.")

                sheet_manager.add_student(student)
                break

            elif answer == "no":
                break
        
        delete_faces_folder(student, face_manager)

if __name__ == "__main__":
    main()"""