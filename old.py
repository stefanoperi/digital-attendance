""" 
   
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