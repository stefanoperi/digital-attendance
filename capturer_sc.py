
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout

class CapturerScreen(FloatLayout):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
    
    def on_enter(self):
        self.main_screen.camera_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.main_screen.camera_layout.size_hint = (0.9, 1)
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