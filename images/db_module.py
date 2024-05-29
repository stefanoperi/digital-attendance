
import sqlite3
import copy
import threading
import numpy as np
import time

class DatabaseManager:

    _instance = None
    _instance_lock = threading.Lock()

    # Método especial __new__ para crear la instancia única
    def __new__(cls, *args, **kwargs):
        # Adquirir el lock para garantizar que la creación de la instancia sea segura para subprocesos
        with cls._instance_lock:
            # Verificamos si la instancia aún no existe
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
        # Selecciona todos los nombres de usuario y codificaciones de la tabla 'encodings'
        self.cursor.execute("SELECT student_id, encoding FROM encodings")
        rows = self.cursor.fetchall()

        mixed_encodings = copy.deepcopy(new_encodings)
        for row in rows:
            student_id = row[0]
            encoding_bytes = row[1] 

            # Convierte  los bytes a un arreglo de NumPy para compatibilidad
            encoding = np.frombuffer(encoding_bytes, dtype=np.float64)  

            # Si el nombre de usuario ya está en las codificaciones mixtas, agrega la nueva codificación
            if student_id in mixed_encodings:
                mixed_encodings[student_id].append(encoding)

            # Si el nombre de usuario no está en las codificaciones mixtas, crea una nueva entrada
            else:
                mixed_encodings[student_id] = [encoding]
        return mixed_encodings
    
    def close(self):
        self.connection.close()
