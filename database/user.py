import sqlite3
from datetime import datetime
from typing import Optional

from .database import db_connection as db, user_default_color_schema


class User:
    def __init__(
        self,
        telegram_id,
        email,
        password,
        user_coin_id=None,
        new_messages=None,
        new_swap=None,
        map_color_schema=None,
    ):
        self.telegram_id = telegram_id
        self.email = email
        self.password = password
        self.user_coin_id = user_coin_id
        self.new_messages = new_messages
        self.new_swap = new_swap
        self.map_color_schema = map_color_schema or user_default_color_schema

    def save(self):
        try:
            db.cursor.execute(
                f"""INSERT INTO users 
                    (
                        tg_id, email, password, user_coin_id, new_messages, new_swap, map_color_schema
                    ) 
                    VALUES 
                    (
                        '{self.telegram_id}', '{self.email}', '{self.password}', '{self.user_coin_id}',
                        {self.new_messages or 0}, {self.new_swap or 0}, '{self.map_color_schema}'
                    )"""
            )
            db.conn.commit()
            print(datetime.now(),"| ", f"User {self.email} added successfully!")
        except sqlite3.IntegrityError:
            print(datetime.now(),"| ", f"User {self.email} UPDATE in the database.")
            db.cursor.execute(
                f"""UPDATE users SET 
                    ( 
                      email, password, user_coin_id, new_messages, new_swap, map_color_schema 
                    ) = 
                    (
                      '{self.email}', '{self.password}', '{self.user_coin_id}', {self.new_messages},
                       {self.new_swap}, '{self.map_color_schema}'
                    )
                      WHERE tg_id = {self.telegram_id};"""
            )
            db.conn.commit()

    @staticmethod
    def get(tg_id) -> Optional["User"]:
        db.cursor.execute(f"SELECT * FROM users WHERE tg_id='{tg_id}'")
        user_data = db.cursor.fetchone()

        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def has_user_with_email(email) -> bool:
        db.cursor.execute(f"SELECT * FROM users WHERE email='{email}'")
        user_data = db.cursor.fetchone()

        if user_data:
            return True
        return False

    @staticmethod
    def get_all():
        db.cursor.execute(f"SELECT * FROM users")
        all_users_data = db.cursor.fetchall()

        return [User(*user) for user in all_users_data]

    @staticmethod
    def delete(tg_id):
        db.cursor.execute(f"DELETE FROM users WHERE tg_id='{tg_id}'")
        db.conn.commit()
        print(datetime.now(),"| ", f"User {tg_id} removed successfully!")
