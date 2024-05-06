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
    
    def select_grade(self, worksheet_index):
        self.worksheet = self.spreadsheet.get_worksheet(worksheet_index)

    def read_values(self):
        # Obtener todos los valores de la hoja de cálculo
        values = self.worksheet.get_all_values()
        return values
    
    def read_worksheet_names(self):
        # Obtener nombres de hojas de calculo (Nombre de cada curso)
        worksheet_names = []
        for worksheet in self.spreadsheet.worksheets():
            worksheet_names.append(worksheet.title)
        return worksheet_names

    def write_words(self, words):
        last_row = len(self.worksheet.get_all_values()) + 1

        # Escribir una palabra por fila
        for row, word in enumerate(words, start=last_row):
            self.worksheet.update_cell(row, 1, word)