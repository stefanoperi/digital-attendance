import sqlite3
import numpy as np
class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None 
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS encodings (
                                id INTEGER PRIMARY KEY,
                                username TEXT NOT NULL,
                                encoding TEXT NOT NULL
                            )''')
        self.connection.commit()

    def insert_encoding(self, username, encoding):
        self.cursor.execute("INSERT INTO encodings (username, encoding) VALUES (?, ?)", (username, encoding))
        self.connection.commit()
    
    def mix_encodings(self, new_encodings):
        # Selecciona todos los nombres de usuario y codificaciones de la tabla 'encodings'
        self.cursor.execute("SELECT username, encoding FROM encodings")
        rows = self.cursor.fetchall()

        mixed_encodings = new_encodings
        for row in rows:
            username = row[0]
            encoding_bytes = row[1] 

            # Convierte  los bytes a un arreglo de NumPy para compatibilidad
            encoding = np.frombuffer(encoding_bytes, dtype=np.float64)  

            # Si el nombre de usuario ya está en las codificaciones mixtas, agrega la nueva codificación
            if username in new_encodings:
                mixed_encodings[username].append(encoding)

            # Si el nombre de usuario no está en las codificaciones mixtas, crea una nueva entrada
            else:
                mixed_encodings[username] = [encoding]
        return mixed_encodings
    
    def close(self):
        self.connection.close()
