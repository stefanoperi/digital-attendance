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

    def create_layout(self):
        layout = ["Nombre", "DNI", "Presente"]
        cell_range = "A1:C1"

        # Obtener la lista de celdas en el rango especificado
        cell_list = self.worksheet.range(cell_range)

        # Iterar sobre las palabras en el diseño y asignarlas a las celdas correspondientes
        for i, word in enumerate(layout):
            cell_list[i].value = word

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
    

    def add_student(self, student):

        student_list = self.read_values()
        self.create_layout()

        # Verificar si el estudiante ya existe
        if student_list:
            for sublist in student_list:
                if len(sublist) == 2 and student.full_name == sublist[0] and student.student_id == sublist[1]:
                    return False

        # Agregar el nuevo estudiante a la lista
        student_list.append([student.full_name, student.student_id])

        # Eliminar sublistas vacías (si las hay)
        student_list = [sublist for sublist in student_list if sublist]
        
        # Ordenar la lista alfabéticamente por el primer carácter del nombre        
        student_list.sort(key=lambda x: x[0].lower())

        # Limpiar el contenido actual de la hoja de cálculo
        self.worksheet.clear()
        
        
        # Escribir los datos ordenados en la hoja de cálculo
        for row, values in enumerate(student_list, start=2):
            self.worksheet.insert_row(values, row)

            cell_range = f"A{row}:C{row}"
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
    
    