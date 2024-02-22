import sqlite3
from datetime import datetime, date
from typing import List, Optional

from .database import db_connection as db


class DataCoin:
    def __init__(self, telegram_id, totla_sum, totla_count, datetime_=None, id_=None):
        self.id = id_
        self.telegram_id = telegram_id
        self.totla_sum = totla_sum
        self.totla_count = totla_count
        self.datetime = datetime.now() if datetime_ is None else datetime_

    def save(self):
        try:
            print(datetime.now(), "| ", "Удаление из базы данных")
            db.cursor.execute(
                f"DELETE FROM graph_data WHERE tg_id='{self.telegram_id}' "
                f"and datetime='{self.datetime.strftime('%Y.%m.%d')}'"
            )

            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, totla_sum, totla_count) "
                f"VALUES ('{self.telegram_id}', "
                f"'{self.datetime.strftime('%Y.%m.%d')}', "
                f"'{self.totla_sum}', '{self.totla_count}')"
            )
            db.conn.commit()

            print(datetime.now(), "| ", "Обновление базы стоимости")
            print(
                datetime.now(),
                "| ",
                f"Данные для {self.telegram_id} добавлены успешно!",
            )
        except sqlite3.IntegrityError:
            print(datetime.now(), "| ", "Already exists in the database.")

    @staticmethod
    def init_new_user(tg_id: int, totla_sum: float, totla_count: int):
        query = ""
        day_increment = date.today()
        query += f"({tg_id}, '{day_increment.strftime('%Y.%m.%d')}', {totla_sum}, {totla_count})"

        try:
            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, totla_sum, totla_count) "
                f"VALUES {query[0:-1]})"
            )
            db.conn.commit()
            print(datetime.now(), "| ", "INIT_NEW_USER___all days added successfully!")
        except sqlite3.IntegrityError:
            print(datetime.now(), "| ", "Already exists in the database.")

    @staticmethod
    def get_for_user(tg_id, limit: Optional[int]) -> List["DataCoin"]:
        limit_str = f"LIMIT {limit}" if limit else ""

        db.cursor.execute(
            f"SELECT * FROM graph_data WHERE tg_id='{tg_id}' ORDER BY datetime DESC {limit_str}"
        )
        data_coins = []
        for sublist in db.cursor.fetchall():
            data_coins.append(
                DataCoin(
                    id_=sublist[0],
                    telegram_id=sublist[1],
                    datetime_=sublist[2],
                    totla_sum=sublist[3],
                    totla_count=sublist[4],
                )
            )
        return data_coins

    @staticmethod
    def delete_user_data(tg_id):
        db.cursor.execute(f"DELETE FROM graph_data WHERE tg_id='{tg_id}'")
        db.conn.commit()
        print(datetime.now(), "| ", f"User {tg_id} removed successfully!")

    @staticmethod
    def check_graph_data():
        # Получение текущей даты и времени
        now = datetime.now()

        # Преобразование в строку с нужным форматом
        formatted_date_now = now.strftime('%Y.%m.%d')

        # Получение всех пользователей из базы данных
        query_users = "SELECT DISTINCT tg_id FROM graph_data"
        db.cursor.execute(query_users)
        users = db.cursor.fetchall()

        res = ""

        for user in users:
            user_id = user[0]
            query = f"SELECT EXISTS (SELECT 1 FROM graph_data WHERE datetime = '{formatted_date_now}' AND tg_id = '{user_id}')"
            db.cursor.execute(query)
            result = db.cursor.fetchone()[0]

            if not result:
                res += f"Запись для пользователя `{user_id}` сегодня отсутствует\n"
        if res != "":
            return res
        return "Для всех пользователей запись в БД сегодня существует"
