
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from image_handling import face_utils as utils
from kivy.uix.popup import Popup

import sys
import shutil
import cv2
    
class Student:
    def __init__(self, student_id=None, full_name=None, grade=None, resources=None, ):
        self.student_id = student_id
        self.full_name = full_name
        self._grade = None  # Private attribute to store the actual grade value
        self.resources = resources
        self.grade = grade  # This will trigger the grade setter for validation

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        # Validates that the grade is within the allowed worksheet names
        if self.resources and value in self.resources.worksheet_names:
            self._grade = value
        else:     
            raise ValueError(self.resources.show_popup(f"Invalid grade '{value}'. Must be one of {self.resources.worksheet_names}."))

def delete_faces_folder(student, face_manager):
   try:
        shutil.rmtree(f"{face_manager.faces_folder}/{str(student.student_id)}")
   except FileNotFoundError as e:
        print(f"No leftover photos to delete :)")
   except OSError as e:
        raise OSError(f"Error deleting folder: {e}")


class CapturerScreen(FloatLayout):
    def __init__(self, main_screen, resources, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.photo_capturer = resources.capturer
        self.capture_pressed = False
        self.photos_exist = False
        self.resources = resources

    def on_enter(self):
        self.main_screen.camera_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.main_screen.camera_layout.size_hint = (0.9, 1)
        self.change_previous_layout()
        self.setup_components()
        self.captured_photos = []
        
        Clock.schedule_interval(self.update, 1/30)
        
    def change_previous_layout(self):
        # Remove unnecesary widgets from previous layout
        self.main_screen.camera_layout.remove_widget(self.main_screen.button_layout)
        self.main_screen.camera_layout.remove_widget(self.main_screen.prompt_label)
    
    def setup_components(self):
        input_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Capture button
        self.capture_button = Button(text='Capture', pos_hint={'center_x': 0.5}, size_hint_x=0.5, size_hint_y=1.4)
        self.capture_button.bind(on_press=self.start_capture, on_release=self.stop_capture)
        input_layout.add_widget(self.capture_button)

        # ID input (only numbers)
        self.id_input = TextInput(hint_text='ID', input_filter='int')
        input_layout.add_widget(Label(text='ID'))
        input_layout.add_widget(self.id_input) 

        # Name input
        self.name_input = TextInput(hint_text='Name')
        input_layout.add_widget(Label(text='Name'))
        input_layout.add_widget(self.name_input)
        
        # Last name input
        self.lastname_input = TextInput(hint_text='Last Name', size_hint_y=1)
        input_layout.add_widget(Label(text='Last Name'))
        input_layout.add_widget(self.lastname_input)

        # Grade input
        self.grade_input = TextInput(hint_text='Grade')
        input_layout.add_widget(Label(text=f'Grade (Available courses: {self.resources.worksheet_names}'))
        input_layout.add_widget(self.grade_input)
        
        # Action buttons
        action_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        self.save_button = Button(text='Save', size_hint_x=0.2)
        self.save_button.bind(on_press=self.save_action)
        action_layout.add_widget(self.save_button)

        self.cancel_button = Button(text='Cancel', size_hint_x=0.2)
        self.cancel_button.bind(on_press=self.cancel_action)
        action_layout.add_widget(self.cancel_button)
        
        # Add the input layout and action buttons to the main layout
        input_layout.add_widget(action_layout)
        self.main_screen.camera_layout.add_widget(input_layout)

    def start_capture(self, instance):
        self.capture_pressed = True

    def stop_capture(self, instance):
        self.capture_pressed= False

    def update(self, dt):
       image_texture, brightness, face_detected, thresholds = self.photo_capturer.capture_photo(self.main_screen.camera, self.captured_photos)
       self.main_screen.camera.texture = image_texture
       while self.capture_pressed and brightness  >=  thresholds["brightness"] and face_detected:
        if  len(self.captured_photos) >= thresholds["photo"]:
             self.photos_exist = True
             break
        
        frame = utils.kivy_to_cv2(self.main_screen.camera)
        self.captured_photos.append(frame)
         
        self.capture_pressed = False
      

    def save_action(self, instance):

        # Check that attributes are not None or empty
        try:
            if self.id_input.text and self.name_input.text and self.lastname_input.text and self.grade_input.text:
                student_registered = Student(
                student_id=self.id_input.text, 
                full_name=self.name_input.text + " " + self.lastname_input.text,
                grade=self.grade_input.text,
                resources=self.resources)
            else:
                raise ValueError(self.resources.show_popup("Please fill correctly all fields"))
        except Exception:
            return 
        print("no hay fotos")
        if self.photos_exist:
            print("hay fotos")
            for img in self.captured_photos:
                print(f"LEN: {len(self.captured_photos)}")
                cv2.imshow("ImAGE PREVIEW",img)
            # Ensure to delete remaining photos before adding new ones
          #  delete_faces_folder(student_registered, self.resources.face_manager)
            
            # opup = self.resources.show_popup("Processing information, this may take a moment. Do not close the application", "Warning")    
           # success = self.resources.face_manager.save_faces(student_registered, self.captured_photos)
            #student_encodings = self.resources.face_manager.encode_faces(self.resources.faces_path, student_registered)
            #if student_encodings:
                # popup.dismiss()
                #   self.resources.show_popup("Information processed succesfully", "Success")
        #else:
            #       self.resources.show_popup("More photos are needed to proceed")
   
        
        # Additional save logic goes here

    def cancel_action(self, instance):
        sys.exit(0)
        # Additional cancel logic goes here

 