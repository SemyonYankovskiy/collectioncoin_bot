import sqlite3
from datetime import datetime, date, timedelta


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
                            (id INTEGER PRIMARY KEY NOT NULL,
                            tg_id INTEGER NOT NULL,
                            datetime TEXT NOT NULL,
                            totla_sum REAL NOT NULL);"""
        )
        conn.commit()


class DataCoin:
    def __init__(self, telegram_id, totla_sum, datetime_=datetime.now()):
        self.telegram_id = telegram_id
        self.totla_sum = totla_sum
        self.datetime = datetime_

    def save(self):
        db = Database()
        try:
            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, totla_sum) "
                f"VALUES ('{self.telegram_id}', '{self.datetime.strftime('%Y.%m.%d')}', '{self.totla_sum}')"
            )
            db.conn.commit()
            print(f"{self.totla_sum} added successfully!")
        except sqlite3.IntegrityError:
            print(f"Already exists in the database.")

    @staticmethod
    def init_new_user(tg_id: int, totla_sum: float):
        db = Database()
        query = ""
        day_increment = date.today()
        for _ in range(30):
            query += f"({tg_id}, '{day_increment.strftime('%Y.%m.%d')}', {totla_sum}),"
            day_increment -= timedelta(days=1)

        try:
            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, totla_sum) "
                f"VALUES {query[0:-1]}"
            )
            db.conn.commit()
            print(f"all days added successfully!")
        except sqlite3.IntegrityError:
            print(f"Already exists in the database.")

    @staticmethod
    def get_for_user(tg_id):
        db = Database()
        db.cursor.execute(
            f"SELECT * FROM graph_data WHERE tg_id='{tg_id}' ORDER BY datetime"
        )
        coin_data = db.cursor.fetchall()
        # print(coin_data)
        return coin_data

    @staticmethod
    def clear_old_data():
        db = Database()
        # Вычисляем дату 30 дней назад
        thirty_days_ago = date.today() - timedelta(days=30)

        # Удаляем данные старше 30 дней
        db.cursor.execute(
            f"DELETE FROM graph_data WHERE datetime <= '{thirty_days_ago.strftime('%Y.%m.%d')}'"
        )
        db.conn.commit()

    @staticmethod
    def delete_user_data(tg_id):
        db = Database()
        db.cursor.execute(f"DELETE FROM graph_data WHERE tg_id='{tg_id}'")
        db.conn.commit()
        print(f"User {tg_id} removed successfully!")

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
