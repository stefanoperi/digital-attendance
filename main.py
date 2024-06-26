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
    def __init__(self, student_id, full_name, grade, encodings):
        self.student_id = student_id
        self.full_name = full_name
        self.grade = grade
        self.encodings = encodings
        
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
        self.db_manager.create_table()


        self.student_encodings = {}
        self.new_photos = None
        self.student = None

        self.capturer = utils.PhotoCapturer()
          
        self.sheet_manager = spreadsheet_module.GoogleSheetManager("Toma de Asistencia") # Open by the google spreadsheet's name
        self.worksheet_names = self.sheet_manager.read_worksheet_names() # Get course names


class MainScreen(BoxLayout):
    def __init__(self, transition_callback, resources, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize with transition callback and resources
        self.transition = transition_callback
        self.resources = resources
        self.selected_course = None  
        self.orientation = 'horizontal'  
        self.face_detector = utils.FaceDetector()

        # Set up the UI components during initialization
        self.setup_ui()
        
        # Set up specific layouts and components
        self.setup_camera_layout()
        self.setup_info_layout()
       
    def setup_ui(self):
        self.setup_dropdown() 
        self.setup_buttons()  

    def setup_dropdown(self):
        # Method to set up the dropdown menu
        self.dropdown = DropDown()  # Create a dropdown instance
        for course_name in self.resources.worksheet_names:
            self.add_dropdown_item(course_name)  # Add each course name as a dropdown item

        self.dropdown_button = Button(text='Course', size_hint=(None, None), size=(200, 44))
        self.dropdown_button.bind(on_release=self.dropdown.open)  # Bind button to open the dropdown
        self.dropdown.bind(on_select=self.on_course_select)  # Bind dropdown selection to handler method
    
    def add_dropdown_item(self, course_name):
        # Add each course name as a dropdown item
        btn = Button(text=course_name, size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))  # Bind button to select dropdown item
        self.dropdown.add_widget(btn)  

    def setup_buttons(self):
        # Method to set up action buttons
        self.photo_button = Button(text='Add new photos', font_size=20)
        self.photo_button.bind(on_press=lambda instance: self.transition('capturer'))  # Bind button press to transition callback    

    def setup_camera_layout(self):
        # Method to set up the camera and related UI layout
        camera_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
        self.prompt_label = Label(text='Please select the course for attendance', font_size=20)
        camera_layout.add_widget(self.prompt_label)  # Add prompt label to camera layout

        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), padding=[0, 0, 0, 100])
        button_layout.add_widget(self.dropdown_button)  
        button_layout.add_widget(self.photo_button)  
        camera_layout.add_widget(button_layout) # Add all buttons to the camera layout
        self.add_widget(camera_layout)  # Add camera layout to the main screen

    def setup_info_layout(self):
        # Method to set up information display layout
        info_layout = BoxLayout(orientation='vertical', padding=[10], size_hint=(0.3, 1))
        self.info_label = Label(text='Student Info', font_size=20)
        info_layout.add_widget(self.info_label)  # Add label for student info
        self.add_widget(info_layout)  # Add info layout to the main screen

    def update(self, dt):
        # Method to update the camera display
        image_texture = self.face_detector.live_comparison(self.resources.student_encodings, self.resources.student, self.camera)
        self.camera.texture = image_texture  # Update camera texture with live comparison result

    def on_course_select(self, instance, value):
        # Method to handle selection of a course from the dropdown
        self.selected_course = value  
        setattr(self.dropdown_button, 'text', value)  # Change original text to the selected course
    
    def run(self):
        ...
      


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