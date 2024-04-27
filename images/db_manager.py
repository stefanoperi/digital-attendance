import sqlite3
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

    def close(self):
        self.connection.close()
