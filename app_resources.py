
import os
import shutil
import numpy as np
import logging

from image_handling import face_utils as utils
from database import db_module 
from spreadsheet import spreadsheet_module 
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.text import Label as CoreLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class AppResources():
    def __init__(self, **kwargs):
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
     
        self.capturer = utils.PhotoCapturer()
        self.show_popup = show_popup

        self.sheet_manager = spreadsheet_module.GoogleSheetManager("Toma de Asistencia") # Open by the google spreadsheet's name
        self.worksheet_names = self.sheet_manager.read_worksheet_names() # Get course names


def show_popup(message, type="Error", auto_dismis=True, add_yes_no_buttons=False):
    # Calculate the size of the text
    label = CoreLabel(text=message, font_size=20)
    label.refresh()
    text_width, text_height = label.texture.size
    
    # Add some padding
    padding = 20
    popup_width = text_width + padding * 4
    popup_height = text_height + padding * 4
    
    # Create a layout to hold the message and optionally buttons
    layout = BoxLayout(orientation='vertical', padding=padding, spacing=padding)
    
    # Create a label with the message and add it to the layout
    message_label = Label(text=message, size_hint=(None, None), size=(text_width, text_height))
    layout.add_widget(message_label)
    
    # Optionally add Yes-No buttons
    if add_yes_no_buttons:
        buttons_layout = BoxLayout(spacing=10, size_hint=(None, None), height=50)
        yes_button = Button(text="Yes", size_hint=(1, 1))
        no_button = Button(text="No", size_hint=(1, 1))
        
        # Add buttons to the buttons_layout
        buttons_layout.add_widget(yes_button)
        buttons_layout.add_widget(no_button)
        
        # Add the buttons layout to the main layout
        layout.add_widget(buttons_layout)
        
        # Adjust popup height to accommodate the buttons
        popup_height += 50 + padding
    
    # Create the popup with the layout as content
    popup = Popup(title=type,
                  content=layout,
                  auto_dismiss=auto_dismis,
                  size_hint=(None, None),
                  size=(popup_width, popup_height))
    
    # Open the popup
    popup.open()
    return popup

