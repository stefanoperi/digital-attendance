import kivy
import os
import shutil
import cv2
import face_recognition
import sys
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
from kivy.uix.textinput import TextInput

class Student:
    def __init__(self):
        self.student_id = None
        self.full_name = None
        self.grade = None
        self.encodings = None
        
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
        self.last_registered_student = Student()

        self.capturer = utils.PhotoCapturer()
          
        self.sheet_manager = spreadsheet_module.GoogleSheetManager("Toma de Asistencia") # Open by the google spreadsheet's name
        self.worksheet_names = self.sheet_manager.read_worksheet_names() # Get course names

class MainScreen(BoxLayout):
    def __init__(self, transition_callback, resources, **kwargs):
        super().__init__(**kwargs)
        
        self.transition = transition_callback
        self.resources = resources
        self.selected_course = None  
        self.orientation = 'horizontal'  
        self.face_detector = utils.FaceDetector()
        self.update_event = None

        self.setup_ui()
        self.setup_camera_layout()
        self.setup_info_layout()
       
    def setup_ui(self):
        self.setup_dropdown() 
        self.setup_buttons()  

    def setup_dropdown(self):
        self.dropdown = DropDown()
        for course_name in self.resources.worksheet_names:
            self.add_dropdown_item(course_name)

        self.dropdown_button = Button(text='Course', size_hint=(None, None), size=(200, 44))
        self.dropdown_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=self.on_course_select)
    
    def add_dropdown_item(self, course_name):
        btn = Button(text=course_name, size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
        self.dropdown.add_widget(btn)  

    def setup_buttons(self):
        self.photo_button = Button(text='Add new photos', font_size=20)
        self.photo_button.bind(on_press=self.on_photos_select)

        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.button_layout.add_widget(self.dropdown_button)  
        self.button_layout.add_widget(self.photo_button)  
        
    def setup_camera_layout(self):
        self.camera_layout = BoxLayout(orientation='vertical', size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.camera_placeholder = Label(text='Initializing camera...')
        self.camera_layout.add_widget(self.camera_placeholder)
        self.initialize_camera()

        self.prompt_label = Label(text='Please select the course for attendance', font_size=20, size_hint=(1, 0.1))
        self.camera_layout.add_widget(self.prompt_label)
        self.camera_layout.add_widget(self.button_layout)
        self.add_widget(self.camera_layout)

    def initialize_camera(self):
        camera_index = 0
        while camera_index < 5:
            try:
                self.camera = Camera(index=camera_index, play=True, size_hint=(1, 1))
                self.camera_placeholder.parent.add_widget(self.camera)
                self.camera_placeholder.parent.remove_widget(self.camera_placeholder)
                return
            except Exception as e:
                self.camera_placeholder.text = f"Failed to initialize camera at index {camera_index}: {e}"
                camera_index += 1
        
        self.camera_placeholder.text = 'Camera initialization failed for all indices'

    def setup_info_layout(self):
        info_layout = BoxLayout(orientation='vertical', padding=[10], size_hint=(0.3, 1))
        self.info_label = Label(text='Student Info', font_size=20)
        info_layout.add_widget(self.info_label)
        self.add_widget(info_layout)

    def update(self, dt):
        image_texture = self.face_detector.live_comparison(self.resources.student_encodings, self.resources.last_registered_student, self.camera)
        self.camera.texture = image_texture

    def on_course_select(self, instance, value):
        if self.update_event is not None:
            self.update_event.cancel()
        
        self.selected_course = value  
        setattr(self.dropdown_button, 'text', value)
        self.resources.sheet_manager.select_grade(self.selected_course)
        self.prompt_label.opacity = 0
        
        if self.selected_course is not None:
            self.update_event = Clock.schedule_interval(self.update, 1/30)

    def on_photos_select(self, instance):
        self.clear_widgets()
        self.stop_update()
        self.add_widget(self.camera_layout)
        self.add_widget(self.CapturerScreen(self))

    def stop_update(self):
        if self.update_event is not None:
            self.update_event.cancel()
            self.update_event = None

    class CapturerScreen(BoxLayout):
        def __init__(self, main_screen, **kwargs):
            super().__init__(**kwargs)
            self.main_screen = main_screen
            self.change_previous_layout()
            self.setup_forms()
            
        def change_previous_layout(self):
            # Remove unnecesary widgets from previous layout
            self.main_screen.camera_layout.remove_widget(self.main_screen.button_layout)
            self.main_screen.camera_layout.remove_widget(self.main_screen.prompt_label)
      
        def setup_forms(self):
            input_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            # Name input
            self.name_input = TextInput(hint_text='Name')
            input_layout.add_widget(Label(text='Name'))
            input_layout.add_widget(self.name_input)
            
            # Last name input
            self.lastname_input = TextInput(hint_text='Last Name')
            input_layout.add_widget(Label(text='Last Name'))
            input_layout.add_widget(self.lastname_input)
            
            # ID input (only numbers)
            self.id_input = TextInput(hint_text='ID', input_filter='int')
            input_layout.add_widget(Label(text='ID'))
            input_layout.add_widget(self.id_input) 
                
            # Action buttons
            action_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
            
            self.save_button = Button(text='Save', size_hint_x=0.2, width=50)
            self.save_button.bind(on_press=self.save_action)
            action_layout.add_widget(self.save_button)

            self.cancel_button = Button(text='Cancel', size_hint_x=0.2, width=50)
            self.cancel_button.bind(on_press=self.cancel_action)
            action_layout.add_widget(self.cancel_button)
            
            # Add the input layout and action buttons to the main layout
            input_layout.add_widget(action_layout)
            self.main_screen.camera_layout.add_widget(input_layout)
        
        def save_action(self, instance):
            # Handle the save action here
            name = self.name_input.text
            lastname = self.lastname_input.text
            student_id = self.id_input.text
            print(f"Saved: Name={name}, Last Name={lastname}, ID={student_id}")
            # Additional save logic goes here

        def cancel_action(self, instance):
            # Handle the cancel action here
            print("Cancelled")
            # Additional cancel logic goes here
        
    

class CapturerScreen(BoxLayout):
    def __init__(self, transition_callback, resources, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize with transition callback and resources
        self.transition = transition_callback
        self.resources = resources
        self.selected_course = None  
        self.orientation = 'vertical'  
        self.face_detector = utils.FaceDetector()
        self.update_event = None

    def on_enter(self, *args):
        # Set up specific layouts and components when entering the screen
        self.setup_ui()
       
    def setup_ui(self):
        self.setup_camera_layout()
        self.setup_forms()

    def setup_forms(self):
        input_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Name input
        self.name_input = TextInput(hint_text='Name')
        input_layout.add_widget(Label(text='Name'))
        input_layout.add_widget(self.name_input)
        
        # Last name input
        self.lastname_input = TextInput(hint_text='Last Name')
        input_layout.add_widget(Label(text='Last Name'))
        input_layout.add_widget(self.lastname_input)
        
        # ID input (only numbers)
        self.id_input = TextInput(hint_text='ID', input_filter='int')
        input_layout.add_widget(Label(text='ID'))
        input_layout.add_widget(self.id_input)

        self.add_widget(input_layout)
    
    def setup_camera_layout(self):
        camera_layout = BoxLayout(orientation='vertical', size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.camera_placeholder = Label(text='Initializing camera...')
        camera_layout.add_widget(self.camera_placeholder)
        self.add_widget(camera_layout)

        # Schedule camera initialization with a delay
        Clock.schedule_once(self.initialize_camera, 10.0)
    
    def initialize_camera(self, dt):
     
        camera_index = 0
        while camera_index < 5:  # Try up to 5 different indices
            try:
                self.camera = Camera(index=camera_index, play=True, size_hint=(1, 1))
                self.camera_placeholder.parent.add_widget(self.camera)
                self.camera_placeholder.parent.remove_widget(self.camera_placeholder)
                return  # Exit if successful
            except Exception as e:
                self.camera_placeholder.text = f"Failed to initialize camera at index {camera_index}: {e}"
                camera_index += 1
        
        # If no camera could be initialized, show an error message
        self.camera_placeholder.text = 'Camera initialization failed for all indices'

    def update(self, dt):
        # Method to update the camera display
        image_texture = self.face_detector.live_comparison(self.resources.student_encodings, self.resources.last_registered_student, self.camera)
        self.camera.texture = image_texture  # Update camera texture with live comparison result

    def stop_update(self):
        # Method to stop the update schedule
        if self.update_event is not None:
            self.update_event.cancel()
            self.update_event = None


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
        
        # Create the capturer screen and add it to the ScreenManager
        capturer_screen = Screen(name='capturer')
        capturer_screen_instance = CapturerScreen(transition_callback=self.transition_to, resources=resources)
        capturer_screen.add_widget(capturer_screen_instance)
        self.sm.add_widget(capturer_screen)

        # Bind on_enter method of capturer_screen_instance to the on_enter event
        capturer_screen.bind(on_enter=capturer_screen_instance.on_enter)

        # Set the initial screen to the loading screen
        self.sm.current = 'main'

        return self.sm

    def transition_to(self, screen_name, *args):
        self.sm.current = screen_name


if __name__ == '__main__':
    DigitalAttendanceApp().run()