import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetManager:
    def __init__(self, spreadsheet_name):
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
    

    def add_student(self, student):
        # Leer los valores existentes de la hoja de cálculo
        student_list = self.read_values()

        # Verificar si el estudiante ya existe
        print(f"Student list before if: {student_list}")
        if student_list:
            for sublist in student_list:
                if len(sublist) == 2 and student.full_name == sublist[0] and student.id == sublist[1]:
                    return False

        # Agregar el nuevo estudiante a la lista
        print(f"Student list before append: {student_list}")
        student_list.append([student.full_name, student.student_id])

        # Eliminar sublistas vacías (si las hay)
        student_list = [sublist for sublist in student_list if sublist]
        
        # Ordenar la lista alfabéticamente por el primer carácter del nombre        
        print(f"Student list before sort: {student_list}")
        student_list.sort(key=lambda x: x[0].lower())

        # Limpiar el contenido actual de la hoja de cálculo
        self.worksheet.clear()

        # Escribir los datos ordenados en la hoja de cálculo
        for row, values in enumerate(student_list, start=1):
            self.worksheet.insert_row(values, row)

        return True
    
def write_words(self, words):

    last_row = len(self.worksheet.get_all_values()) + 1

    # Escribir una palabra por fila
    for row, word in enumerate(words, start=last_row):
        self.worksheet.update_cell(row, 1, word)