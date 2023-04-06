import sqlite3


class User:
    def __init__(self, telegram_id, email, password):
        self.telegram_id = telegram_id
        self.email = email
        self.password = password


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS users
                            (tg_id INTEGER PRIMARY KEY NOT NULL,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL);"""
                    )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS graph_data
                            (tg_id INTEGER PRIMARY KEY NOT NULL,
                            datetime REAL NOT NULL,
                            totla_sum REAL NOT NULL);"""
        )
        self.conn.commit()

    def add_user(self, user):
        try:
            self.cursor.execute(
                f"INSERT INTO users (tg_id, email, password) VALUES ('{user.telegram_id}', '{user.email}', '{user.password}')"
            )
            self.conn.commit()
            print(f"User {user.email} added successfully!")
        except sqlite3.IntegrityError:
            print(f"User {user.email} already exists in the database.")

    def get_user(self, tg_id):
        self.cursor.execute(f"SELECT * FROM users WHERE tg_id='{tg_id}'")
        user_data = self.cursor.fetchone()

        if user_data:
            return User(*user_data)
        return None

    def delete_user(self, tg_id):
        self.cursor.execute(f"DELETE FROM users WHERE tg_id='{tg_id}'")
        self.conn.commit()
