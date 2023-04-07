import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()

    @staticmethod
    def create_tables():
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users
                            (tg_id INTEGER PRIMARY KEY NOT NULL,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL);"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS graph_data
                            (tg_id INTEGER PRIMARY KEY NOT NULL,
                            datetime REAL NOT NULL,
                            totla_sum REAL NOT NULL);"""
        )
        conn.commit()


class User:
    def __init__(self, telegram_id, email, password):
        self.telegram_id = telegram_id
        self.email = email
        self.password = password

    def save(self):
        db = Database()
        try:
            db.cursor.execute(
                f"INSERT INTO users (tg_id, email, password) "
                f"VALUES ('{self.telegram_id}', '{self.email}', '{self.password}')"
            )
            db.conn.commit()
            print(f"User {self.email} added successfully!")
        except sqlite3.IntegrityError:
            print(f"User {self.email} already exists in the database.")

    @staticmethod
    def get(tg_id):
        db = Database()
        db.cursor.execute(f"SELECT * FROM users WHERE tg_id='{tg_id}'")
        user_data = db.cursor.fetchone()

        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def delete(tg_id):
        db = Database()
        db.cursor.execute(f"DELETE FROM users WHERE tg_id='{tg_id}'")
        db.conn.commit()
        print(f"User {tg_id} removed successfully!")
