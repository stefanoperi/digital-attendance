import kivy
import os
import shutil 

from image_handling import face_utils as utils
from database import db_module 
from spreadsheet import spreadsheet_module 
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager

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
   
class LoadingScreen(BoxLayout):
    def __init__(self, transition_callback, **kwargs):
        super().__init__(**kwargs)  # Load base class (BoxLayout)
        self.transition = transition_callback

        # Set orientation and padding for the layout
        self.orientation = 'vertical'
        self.padding = [50]

        # Create and add the label
        self.label = Label(text='Digital Attendance System', font_size=30)
        self.add_widget(self.label)
        Clock.schedule_once(lambda instance: self.transition('main') , 3)

class MainScreen(BoxLayout):
    def __init__(self, transition_callback, **kwargs):
        super().__init__(**kwargs) 
        self.transition = transition_callback

        self.orientation = 'vertical'
        self.padding = [50]

        # Create and add a button to the main screen
        self.button = Button(text='Start', font_size=20, size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=lambda instance: self.transition('running'))
        self.add_widget(self.button)

        self.button = Button(text='Add new photos', font_size=20, size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=lambda instance: self.transition('capturer'))
        self.add_widget(self.button)
    

class CapturerScreen(BoxLayout):
    def __init__(self, transition_callback, **kwargs):
        super().__init__(**kwargs) 

    ...

class DemoScreen(BoxLayout): #Sin excel jodiendo
    ...

class PromptScreen(BoxLayout):
    # Tiene que ser configurable para tres posibles pantallas
    ...
    
class RunningScreen(BoxLayout):
    ...

class DigitalAttendanceApp(App):
    def build(self):
        # Create the screen manager
        self.sm = ScreenManager()

        # Create the loading screen and add it to the ScreenManager
        loading_screen = Screen(name='loading')
        loading_screen.add_widget(LoadingScreen(transition_callback=self.transition_to))
        self.sm.add_widget(loading_screen)

        # Create the main screen and add it to the ScreenManager
        main_screen = Screen(name='main')
        main_screen.add_widget(MainScreen(transition_callback=self.transition_to))
        self.sm.add_widget(main_screen)

        capturer_screen = Screen(name='capturer')
        capturer_screen.add_widget(CapturerScreen(transition_callback=self.transition_to))
        self.sm.add_widget(capturer_screen)


        # Set the initial screen to the loading screen
        self.sm.current = 'loading'        
        
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