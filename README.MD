# Digital Attendance System
#### Description: 
This project is a digital attendance system that uses face recognition technology to make the process of taking attendance more efficient. It consists of several components that work together to capture photos, detect faces, encode facial data, and update attendance records in a Google Sheet. The main goal is to simplify and automate the attendance tracking process in educational enviroments.

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

## Installation Instructions

Follow these steps to set up the project:

1. **Activate a virtual environment using Python 3.11**:
   ```bash
   # Replace "venv" with your preferred virtual environment name
   python3.11 -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate.bat  # Windows

2. **Install requirements.txt**: 
   ```bash
   pip install -r requirements.txt

3. **Install face-recognition WITHOUT dependencies**:
    ```bash
    pip install --no-deps face-recognition

4. **Get credentials for Google Sheets**:
   - Follow these steps to enable the Google Sheets API for your project and obtain credentials:
     1. Create a spreadsheet.
     2. Enable Google Drive & Sheets API.
     3. Create a service account.
     4. Save the credentials JSON file in the spreadsheet folder of the project.

   - Or watch the specified minutes of this tutorial:
     1. [Video tutorial](https://www.youtube.com/watch?v=wrR0YLzh4DQ&t=305s) [00:00 - 05:43] for a detailed walkthrough of the process.
     2. After following the instructions in the video, download the credentials file provided by Google.
     3. Save the credentials JSON file in the spreadsheet folder of the project.


5. **RENAME the credentials file to credentials.json**:

    After obtaining the credentials file from Google, rename it to credentials.json and place it in the spreadsheet folder of the  project.


6. **Create worksheets**:
   - Name and create new worksheets in the spreadsheet for each course you'll be using for attendance tracking.

     To create a new worksheet in Google Sheets:
     1. Open your spreadsheet.
     2. Click on the "+" button at the bottom left corner of the window to add a new sheet.
     3. Double-click on the new sheet tab to rename it, and give it a name corresponding to the course it represents.

   - Each worksheet will serve as a separate attendance log for a specific course, making it easier to organize and manage attendance data.

## Design Choices
1. **Singleton Pattern for GoogleSheetManager and DatabaseManager**: Ensures that there is only one instance of both classes, which helps manage resources efficiently when interacting with the Google Sheets API as well as with the database.
2. **Thread Safety**: The `GoogleSheetManager` and `DatabaseManager` classes use threading locks to prevent concurrent access issues, ensuring thread safety.
3. **Database Usage**: SQLite is used for storing face encodings, which allows for efficient retrieval and comparison during the face recognition process. Without this database, faces would need to be encoded each time the program is used, which would be less efficient
4. **Face Recognition Library**: The project utilizes the `face_recognition` library, which is a simple and powerful library for face recognition in Python. This library tends to be more compatible and performs better on Linux systems, resulting in improved performance on those platforms.
5. **Real-time Face Detection**: The `FaceDetector` class employs OpenCV for real-time face detection and tracking, providing immediate feedback during the attendance process.

## How It Works

1. **Setup**:
    - Ensure that necessary directories and database tables are created.
    - Connect to the Google Sheets API and check for the existence of "credentials.json".
    - Prompt the user to select the grade for which attendance is to be taken.

2. **Capturing Photos (Optional)**:
    - Optionally, the user can choose to capture new photos. Captured photos are saved and encoded.
    - The system checks for existing students and avoids duplications.

3. **Face Detection and Recognition**:
    - During live attendance, the system uses a webcam to capture frames and detect faces in real-time.
    - Detected faces are compared against the stored encodings to identify students.

4. **Updating Records**:
    - Once a student is recognized, their attendance is recorded in the Google Sheet, along with the exact time of recognition.

5. **Saving Encodings (Optional)**:
    - After demonstrating how the program works with the newly captured photos (if any), the user can choose whether to save the new encodings to the database.



## Future Enhancements
- **Improved Error Handling**: Implement comprehensive error handling to manage potential issues with database connections, file operations, and API interactions.
- **Scalability**: Enhance the system to handle larger datasets and multiple classes simultaneously.
- **User Interface**: Develop a graphical user interface to improve user experience and make the system more accessible to non-technical users.

By automating attendance with face recognition, this project aims to save time, reduce manual errors, and provide a seamless experience for educators and students alike.