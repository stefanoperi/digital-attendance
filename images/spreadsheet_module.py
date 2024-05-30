import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading

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

    def create_layout(self):
        layout = ["Nombre", "DNI", "Presente"]
        cell_range = "A1:C1"

        # Obtener la lista de celdas en el rango especificado
        cell_list = self.worksheet.range(cell_range)

        # Iterar sobre las palabras en el diseño y asignarlas a las celdas correspondientes
        self.worksheet.insert_row(layout, 1)

        # Aplicar cambios a las celdas
        self.worksheet.update_cells(cell_list)

        # Aplicar bordes al rango de celdas
        self.worksheet.format(cell_range, {
            'borders': {
                'top': {'style': 'SOLID'},
                'bottom': {'style': 'SOLID'},
                'left': {'style': 'SOLID'},
                'right': {'style': 'SOLID'},
            }
        })

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
        # Eliminar sublistas vacias
        student_list = [sublist for sublist in student_list if sublist and any(sublist)]

        # Eliminar el primer elemento si la lista no está vacía
        if student_list:
            student_list.pop(0)

        # Ordenar la lista alfabéticamente por el primer carácter del nombre        
        student_list.sort(key=lambda x: x[0].lower())

    def add_student(self, student):

        student_list = self.read_values()
    
        # Verificar si el estudiante ya existe
        if student_list:
            for sublist in student_list:
                if len(sublist) >= 2 and student.full_name == sublist[0] and student.student_id == sublist[1]:
                    return False

        # Agregar el nuevo estudiante a la lista
        student_list.append([student.full_name, student.student_id])

        # Ordenar y limpiar lista
        student_list = self.clean_sort(student_list)

        print(student_list)
        # Limpiar el contenido actual de la hoja de cálculo
        self.worksheet.clear()
        #self.create_layout()
        
        # Escribir los datos ordenados en la hoja de cálculo
        for row, values in enumerate(student_list, start=2):
            self.worksheet.insert_row(values, row)
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

        for row, sublist in enumerate(student_list, start=2):
            if person_found["name"] == sublist[0] and person_found["id"] == sublist[1]:
                if sublist[3]:  # Si ya está marcado
                    return 0
                else:
                    # Agregar en la columna C de la fila donde está el estudiante escrito, la hora en la que se confirmó la presencia
                    self.worksheet.update_cell(row, 3, time_found)
                    return 1

        print(f"La persona encontrada no pertenece al curso {self.grade_selected}")
