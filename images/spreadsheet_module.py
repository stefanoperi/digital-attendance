import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
from datetime import datetime

class GoogleSheetManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, spreadsheet_name, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(GoogleSheetManager, cls).__new__(cls)
                cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self, spreadsheet_name):
        if self.__initialized:
            return
        self.__initialized = True

        # Definir el alcance de acceso
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

        # Cargar las credenciales desde el archivo JSON
        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

        # Autenticar con Google Sheets API
        gc = gspread.authorize(credentials)

        # Abrir la hoja de cálculo por su nombre
        self.spreadsheet = gc.open(spreadsheet_name)
    
    def select_grade(self, grade):
        self.grade_selected = grade
        self.worksheet = self.spreadsheet.worksheet(grade)

    def read_values(self):
        # Obtener todos los valores de la hoja de cálculo (Estudiantes del curso)
        values = self.worksheet.get_all_values()
        return values
    
    def read_worksheet_names(self):
        # Obtener nombres de hojas de calculo (Nombre de cada curso)
        worksheet_names = []
        for worksheet in self.spreadsheet.worksheets():
            worksheet_names.append(worksheet.title)
        return worksheet_names
    
    def clean_sort(self, student_list):
        if len(student_list) > 1:
            # Eliminar sublistas vacias
            student_list = [sublist for sublist in student_list if sublist and any(sublist)]
            
            # Mantener la primera sublista intacta y ordenar el resto
            header = student_list[0]
            data = student_list[1:]

            student_list = [header] + data

            # Ordenar la lista alfabéticamente por el primer carácter del nombre        
            data.sort(key=lambda x: x[0].lower())

            return student_list

    def add_student(self, student):
        student_list = self.read_values()

        # Asegurar que la primera sublista tenga al menos 3 elementos
        if len(student_list[0]) < 3:
            student_list[0].extend([""] * (3 - len(student_list[0])))

        student_list[0][0] = "Estudiante"
        student_list[0][1] = "DNI"
        student_list[0][2] = "Presencia"

        # Verificar si el estudiante ya existe
        if student_list:
            for sublist in student_list:
                if len(sublist) >= 2 and student.full_name == sublist[0] and student.student_id == sublist[1]:
                    return False

        # Agregar el nuevo estudiante a la lista
        student_list.append([student.full_name, student.student_id])

        # Ordenar y limpiar lista
        student_list = self.clean_sort(student_list)

        # Limpiar el contenido actual de la hoja de cálculo
        self.worksheet.clear()
       
        # Escribir los datos ordenados en la hoja de cálculo
        for row, values in enumerate(student_list, start=1):
            self.worksheet.insert_row(values, row) """ USAR UPDATE CELL EN VEZ DE INSERT ROW """
            cell_range = f"A{row}:C{row}"
        
            # Verificar si las celdas están vacías antes de aplicar el formato
            cell_values = self.worksheet.get_values(cell_range)
            if any(cell_values[0]):  # Verificar si hay algún valor en las celdas de la fila
                self.worksheet.format(cell_range, {
                    'borders': {
                        'top': {
                            'style': 'SOLID'
                        },
                        'bottom': {
                            'style': 'SOLID'
                        },
                        'left': {
                            'style': 'SOLID'
                        },
                        'right': {
                            'style': 'SOLID',
                        }
                    }
                })

          
        return True
    def register_presence(self, person_found, time_found):
        student_list = self.clean_sort(self.read_values())
        if student_list == None:
            print("Aun no hay ningun alumno inscripto en el curso")
            return
        
        # Convertir time_found a string si es un objeto datetime
        if isinstance(time_found, datetime):
            time_found = time_found.strftime('%Y-%m-%d %H:%M:%S')

        for row, sublist in enumerate(student_list, start=1):
            if person_found["name"] == sublist[0] and person_found["id"] == sublist[1]:
                if sublist[2]:  # Si ya habia sido marcado
                    print(f"La presencia de {person_found['name']} ya habia sido confirmada")
                    return 1
                else:
                    # Agregar en la columna C de la fila donde está el estudiante escrito, el momento en el que se confirmó la presencia
                    self.worksheet.update_cell(row, 3, time_found)
                    print(f"La presencia de {person_found['name']} ha sido confirmada.")
                    return 0

        print(f"La persona encontrada no pertenece al curso {self.grade_selected}")
        return -1
