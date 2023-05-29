import sqlite3
from typing import Optional

from .database import Database


class User:
    def __init__(self, telegram_id, email, password, new_messages=None, new_swap=None):
        self.telegram_id = telegram_id
        self.email = email
        self.password = password
        self.new_messages = new_messages
        self.new_swap = new_swap

    def save(self):
        db = Database()
        try:
            db.cursor.execute(
                f"INSERT INTO users (tg_id, email, password, new_messages, new_swap ) "
                f"VALUES ('{self.telegram_id}', '{self.email}', '{self.password}', {self.new_messages or 0},"
                f" {self.new_swap or 0})"
            )
            db.conn.commit()
            print(f"User {self.email} added successfully!")
        except sqlite3.IntegrityError:
            print(f"User {self.email} UPDATE in the database.")
            db.cursor.execute(
                f"UPDATE  users SET (email, password, new_messages, new_swap )= "
                f"('{self.email}', '{self.password}', {self.new_messages}, {self.new_swap})"
                f"WHERE tg_id = {self.telegram_id} ;"
            )
            db.conn.commit()

    @staticmethod
    def get(tg_id) -> Optional["User"]:
        db = Database()
        db.cursor.execute(f"SELECT * FROM users WHERE tg_id='{tg_id}'")
        user_data = db.cursor.fetchone()

        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def check_email(email):
        db = Database()
        db.cursor.execute(f"SELECT * FROM users WHERE email='{email}'")
        user_data = db.cursor.fetchone()

        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def get_all():
        db = Database()
        db.cursor.execute(f"SELECT * FROM users")
        all_users_data = db.cursor.fetchall()

        return [User(*user) for user in all_users_data]

    @staticmethod
    def delete(tg_id):
        db = Database()
        db.cursor.execute(f"DELETE FROM users WHERE tg_id='{tg_id}'")
        db.conn.commit()
        print(f"User {tg_id} removed successfully!")
