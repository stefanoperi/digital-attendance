import os
import shutil 
from images import face_utils as utils
from images import db_module 
from images import spreadsheet_module

def main(): 

    if not os.path.exists("images/faces"):
            os.makedirs("images/faces")
            print("Nueva carpeta: faces")
    

    face_manager = utils.FaceManager()
    faces_path = "images/faces"
    
    db_manager = db_module.DatabaseManager("encodings.db")
    db_manager.connect()
  
    student_encodings = {} 
    new_photos = None
    student = None
    
    
    sheet_manager = spreadsheet_module.GoogleSheetManager('Toma de Asistencia')
    worksheet_names = sheet_manager.read_worksheet_names() # Obtener nombre de cursos
    
    # Preguntar por grado con el cual trabajar
    grade = get_valid_input(worksheet_names, "Escribe el grado al que se le tomara asistencia (Ej: 6to A): ") 
    sheet_manager.select_grade(grade) 
    print(f"Informacion de {grade}: {sheet_manager.read_values()}")
    

    answer = None
    while True:
        answer = input("Quieres agregar nuevas fotos? [si/no] ").lower()

        if answer == "si":
            capturer = utils.PhotoCapturer()
            new_photos = capturer.capture_photo()

            if new_photos:
               full_name = input("Escribe el nombre completo de la persona capturada: ").strip().title()
               student_id = input("Escribe el numero de DNI de la persona capturada: ")
               student_grade = get_valid_input(worksheet_names, "Escribe el grado de la persona capturada (Ej: 6to A): ") 

               student = Student(student_id=student_id, full_name=full_name, grade=student_grade)
               # Asegurar de borrar fotos restantes antes de añadir nuevas
               delete_faces_folder(student, face_manager)

               face_manager.save_faces(student, new_photos)
               student_encodings = face_manager.encode_faces(faces_path)
            break

        elif answer == "no":
            break
    
    db_manager.create_table()
    mixed_encodings = db_manager.mix_encodings(student_encodings)
    
    face_detector = utils.FaceDetector()
    face_detector.live_comparison(mixed_encodings)
    # Guarda los datos del estudiante en la base de datos para un rendimiento mas eficiente
    answer = None
   
    if student_encodings:
        while True:
            answer = input("¿Desea guardar los datos de la persona en la base de datos? [si/no]: ").lower()
            
            if answer == "si":
                db_manager.create_table()

                # Insertar encodings e informacion en la base de datos
                for person, encodings in student_encodings.items():
                    print(f"Nombre: {person}, Encoding: {encodings}")
                    for encoding in encodings:
                        db_manager.insert_encoding(student, encoding.tobytes())

                db_manager.close()
                print("Datos guardados exitosamente en la base de datos.")

                sheet_manager.add_student(student)
                break

            elif answer == "no":
                break
        
        delete_faces_folder(student, face_manager)
 
    
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
            print(f"La opción '{user_input}' no es válida. Por favor, intenta nuevamente.")

def delete_faces_folder(student, face_manager):
   try:
        shutil.rmtree(f"{face_manager.faces_folder}/{str(student.full_name)}")
   except FileNotFoundError as e:
        print(f"No hay fotos sobrantes que borrar :)")
   except OSError as e:
        raise OSError(f"Error al eliminar la carpeta: {e}")
        

if __name__ == "__main__":
    main()


