import gspread
import threading
import os
import time
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from gspread.exceptions import APIError


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

        # Define the scope of access
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

        # Load credentials from the JSON file
        credentials_path = os.path.join("spreadsheet", "credentials.json")
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        except FileNotFoundError as e:
            raise(f"Error: {e}. No credentials found for the Google Sheet connection at '{credentials_path}'")

        # Authenticate with Google Sheets API
        gc = gspread.authorize(credentials)

        # Open the spreadsheet by its name
        self.spreadsheet = gc.open(spreadsheet_name)
        self.cached_data = None 
        self.last_fetch_time = 0 # Time from last request 
        self.cache_duration = 60  # Time in seconds to keep the data in the cache
        self.retry_delay = 5  
    
    def select_grade(self, grade):
        self.grade_selected = grade
        self.worksheet = self.spreadsheet.worksheet(grade)

    def read_values(self):
        current_time = time.time()
        if self.cached_data is None or (current_time - self.last_fetch_time > self.cache_duration):
            while True:
                try:
                    self.cached_data = self.worksheet.get_all_values()
                    self.last_fetch_time = current_time
                    break
                except APIError as e:
                    if 'quota' in str(e).lower():
                        print("Cuota superada, esperando para reintentar...")
                        time.sleep(self.retry_delay)
                    else:
                        raise e
                    
        return self.cached_data
    def read_worksheet_names(self):
        # Get worksheet names (Name of each course)
        worksheet_names = []
        for worksheet in self.spreadsheet.worksheets():
            worksheet_names.append(worksheet.title)
        return sorted(worksheet_names)
    
    def clean_sort(self, student_list):
        if len(student_list) > 1:
            # Remove empty sublists
            student_list = [sublist for sublist in student_list if sublist and any(sublist)]
            
            # Keep the first sublist intact and sort the rest
            header = student_list[0]
            data = student_list[1:]


            # Sort the list alphabetically by the first character of the name        
            data.sort(key=lambda x: x[0].lower())
            student_list = [header] + data

            return student_list

    def add_student(self, student):
        student_list = self.read_values()

        # Ensure the first sublist has at least 3 elements
        if len(student_list[0]) < 3:
            student_list[0].extend([""] * (3 - len(student_list[0])))

        student_list[0][0] = "Student"
        student_list[0][1] = "ID"
        student_list[0][2] = "Presence"

        # Check if the student already exists
        if student_list:
            for sublist in student_list:
                if len(sublist) >= 2 and student.full_name == sublist[0] and student.student_id == sublist[1]:
                    return False

        # Add the new student to the list
        student_list.append([student.full_name, student.student_id])

        # Sort and clean list
        student_list = self.clean_sort(student_list)

        # Clear the current content of the spreadsheet
        self.worksheet.clear()
       
        # Write the sorted data to the spreadsheet
        for row_idx, values in enumerate(student_list, start=1):
            for col_idx, value in enumerate(values, start=1):
                self.worksheet.update_cell(row_idx, col_idx, value)

            cell_range = f"A{row_idx}:C{row_idx}"

            # Check if the cells are empty before applying formatting
            cell_values = self.worksheet.get_values(cell_range)
            if any(cell_values[0]):  # Check if there is any value in the row cells
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
        if student_list is None:
            print("There are no students enrolled in the course yet")
            return
        
        # Convert time_found to string if it is a datetime object
        if isinstance(time_found, datetime):
            time_found = time_found.strftime('%Y-%m-%d %H:%M:%S')

        for row, sublist in enumerate(student_list, start=1):
            if person_found["name"] == sublist[0] and person_found["id"] == sublist[1]:
                if sublist[2]:  # If already marked
                    print(f"Presence of {person_found['name']} has already been confirmed")
                    return 
                else:
                    # Add the time of presence confirmation in column C of the row where the student is written
                    self.worksheet.update_cell(row, 3, time_found)
                    print(f"Presence of {person_found['name']} has been confirmed. ")         
                    return

        print(f"The person found does not belong to the course {self.grade_selected} ")
        return 
