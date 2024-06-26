import sqlite3
import copy
import threading
import numpy as np
import time

class DatabaseManager:

    _instance = None
    _instance_lock = threading.Lock()

    # Special __new__ method to create the unique instance
    def __new__(cls, *args, **kwargs):
        # Acquire the lock to ensure thread-safe instance creation
        with cls._instance_lock:
            # Check if the instance does not already exist
            if not cls._instance:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance.__initialized = False
        return cls._instance


    def __init__(self, db_name):
   
        if self.__initialized:
            return
        self.__initialized = True

        self.db_name = db_name
        self.connection = None 
        self.cursor = None
        self.lock = threading.Lock()
        
    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS encodings (
                                id INTEGER PRIMARY KEY,
                                student_id TEXT NOT NULL, 
                                full_name TEXT NOT NULL,
                                grade TEXT NOT NULL,
                                encoding TEXT NOT NULL
                            )''')
        self.connection.commit()

    def insert_encoding(self, student, encodings):
        with self.lock:
            retry_attempts = 5
            for attempt in range(retry_attempts):
                try:
                    self.cursor.execute("INSERT INTO encodings (student_id, full_name, grade, encoding) VALUES (?, ?, ?, ?)",
                                        (student.student_id, student.full_name, student.grade, encodings))
                    self.connection.commit()
                    break
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e):
                        if attempt < retry_attempts - 1:
                            time.sleep(1)
                        else:
                            raise
                    else:
                        raise
    
    def mix_encodings(self, new_encodings):
        # Select all user names and encodings from the 'encodings' table
        self.cursor.execute("SELECT student_id, encoding FROM encodings")
        rows = self.cursor.fetchall()

        mixed_encodings = copy.deepcopy(new_encodings)
        for row in rows:
            student_id = row[0]
            encoding_bytes = row[1] 

            # Convert the bytes to a NumPy array for compatibility
            encoding = np.frombuffer(encoding_bytes, dtype=np.float64)  

            # If the user id is already in the mixed encodings, add the new encoding
            if student_id in mixed_encodings:
                mixed_encodings[student_id].append(encoding)

            # If the user id is not in the mixed encodings, create a new entry
            else:
                mixed_encodings[student_id] = [encoding]
        return mixed_encodings
    
    def close(self):
        self.connection.close()
