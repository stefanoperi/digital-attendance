# Automated Attendance System with Face Recognition
#### Video Demo: [URL HERE]
#### Description:

## Overview
This project is an Automated Attendance System that leverages face recognition technology to streamline the process of taking attendance. It consists of several components that work together to capture photos, detect faces, encode facial data, and update attendance records in a Google Sheet. The primary aim is to simplify and automate the attendance tracking process in educational settings.

## Components
The project comprises the following main files:

1. **main.py**:
    - **Functionality**: This is the entry point of the application. It handles the setup and initialization of necessary components like creating directories for storing face images, managing database connections, and interfacing with the Google Sheets API.
    - **Key Functions**:
        - `main()`: Orchestrates the workflow of the application including capturing photos, encoding faces, and updating the database and Google Sheets.
        - `get_valid_input(options, prompt)`: Validates user inputs against a list of options.
        - `delete_faces_folder(student, face_manager)`: Deletes folders containing old face images for a student.

2. **face_utils.py**:
    - **Functionality**: Contains utilities for face detection, photo capturing, and face encoding.
    - **Classes**:
        - `FaceDetector`: Detects faces in images and performs live face comparison to identify individuals.
        - `PhotoCapturer`: Captures photos using the webcam and detects faces in real-time.
        - `FaceManager`: Manages face images, saves them in directories, and encodes them for face recognition.

3. **db_module.py**:
    - **Functionality**: Manages the database operations required to store and retrieve face encodings.
    - **Key Functions**:
        - `DatabaseManager.connect()`: Establishes a connection to the SQLite database.
        - `DatabaseManager.create_table()`: Creates the necessary table for storing face encodings.
        - `DatabaseManager.insert_encoding(student, encoding)`: Inserts a new face encoding into the database.
        - `DatabaseManager.mix_encodings(student_encodings)`: Prepares face encodings for live comparison.

4. **spreadsheet_module.py** (Code provided in the chat):
    - **Functionality**: Manages interactions with Google Sheets including reading, writing, and updating attendance records.
    - **Classes**:
        - `GoogleSheetManager`: Implements singleton pattern to manage Google Sheets API interactions.
        - `select_grade(grade)`: Selects the worksheet corresponding to a particular grade.
        - `read_values()`: Reads all values from the selected worksheet.
        - `read_worksheet_names()`: Fetches the names of all worksheets (courses).
        - `clean_sort(student_list)`: Cleans and sorts the list of students.
        - `add_student(student)`: Adds a new student to the worksheet and updates the list.
        - `register_presence(person_found, time_found)`: Records the presence of a student at a particular time.

## Design Choices
1. **Singleton Pattern for GoogleSheetManager**: Ensures that there is only one instance of the `GoogleSheetManager` class, which helps manage resources efficiently when interacting with the Google Sheets API.
2. **Thread Safety**: The `GoogleSheetManager` class uses threading locks to prevent concurrent access issues, ensuring thread safety.
3. **Database Usage**: SQLite is used for storing face encodings, which allows for efficient retrieval and comparison during the face recognition process.
4. **Face Recognition Library**: The project utilizes the `face_recognition` library, which is a simple and powerful library for face recognition in Python.
5. **Real-time Face Detection**: The `FaceDetector` class employs OpenCV for real-time face detection and tracking, providing immediate feedback during the attendance process.

## How It Works
1. **Setup**:
    - The application starts by ensuring that necessary directories and database tables are created.
    - It connects to the Google Sheets API and prompts the user to select the grade for which attendance is to be taken.

2. **Capturing Photos**:
    - The user is prompted to capture new photos. The captured photos are saved and encoded.
    - The system checks for existing students and avoids duplications.

3. **Face Detection and Recognition**:
    - During live attendance, the system uses a webcam to capture frames and detect faces in real-time.
    - Detected faces are compared against the stored encodings to identify students.

4. **Updating Records**:
    - Once a student is recognized, their attendance is recorded in the Google Sheet, with the exact time of recognition.

## Future Enhancements
- **Improved Error Handling**: Implement comprehensive error handling to manage potential issues with database connections, file operations, and API interactions.
- **Scalability**: Enhance the system to handle larger datasets and multiple classes simultaneously.
- **User Interface**: Develop a graphical user interface to improve user experience and make the system more accessible to non-technical users.

By automating attendance with face recognition, this project aims to save time, reduce manual errors, and provide a seamless experience for educators and students alike.