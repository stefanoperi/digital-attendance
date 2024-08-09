
from image_handling import face_utils as utils
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from capturer_sc import CapturerScreen
from kivy.uix.floatlayout import FloatLayout

class MainScreen(FloatLayout):
    def __init__(self, transition_callback, resources, **kwargs):
        super().__init__(**kwargs)
        
        self.transition = transition_callback
        self.resources = resources
        self.selected_course = None  
        self.orientation = 'horizontal'  
        self.face_detector = utils.FaceDetector()
        self.update_event = None
        self.camera_availability = False

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
        self.camera_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 0.9), pos_hint={'center_x': 0.4, 'center_y': 0.5})
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
        self.info_layout = BoxLayout(orientation='vertical', padding=[5],  size_hint=(0.3, 1), pos_hint={'right': 1})
        self.add_widget(self.info_layout)

    def update(self, dt):
        image_texture, person_found, consecutive_detections, confirmation_threshold  = self.face_detector.live_comparison(self.resources.student_encodings, self.camera)
        self.camera.texture = image_texture
        # AUTOMATIZAR ESTO CON UN FOR LOOP
        self.info_layout.clear_widgets()
        if person_found != None:
            self.info_layout.add_widget(Label(text=f'ID: {person_found["id"]} ', font_size=20))
            self.info_layout.add_widget(Label(text=f'Name: {person_found["name"]} ', font_size=20))
            self.info_layout.add_widget(Label(text=f'Grade: {person_found["grade"]} ', font_size=20))
            self.info_layout.add_widget(Label(text=f"{consecutive_detections} / {confirmation_threshold}", font_size=25))

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
        capturer_screen = CapturerScreen(self, resources=self.resources)
        self.add_widget(capturer_screen)
        capturer_screen.on_enter()

    def stop_update(self):
        if self.update_event is not None:
            self.update_event.cancel()
            self.update_event = None

