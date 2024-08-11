
import os
import shutil
import numpy as np

from image_handling import face_utils as utils
from database import db_module 
from spreadsheet import spreadsheet_module 

        
def get_valid_input(options, prompt):
    while True:
        user_input = input(prompt).strip()
        if user_input in options:
            return user_input
        else:
            print(f"No spreadsheet is named {user_input}. The option {user_input} is not valid,  please try again.")



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

        self.sheet_manager = spreadsheet_module.GoogleSheetManager("Toma de Asistencia") # Open by the google spreadsheet's name
        self.worksheet_names = self.sheet_manager.read_worksheet_names() # Get course names
