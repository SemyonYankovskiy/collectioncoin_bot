import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Optional

from .database import db_connection as db


class DataCoin:
    def __init__(self, telegram_id, totla_sum, datetime_=datetime.now(), id_=None):
        self.id = id_
        self.telegram_id = telegram_id
        self.totla_sum = totla_sum
        self.datetime = datetime_

    def save(self):
        try:
            db.cursor.execute(
                f"DELETE FROM graph_data WHERE tg_id='{self.telegram_id}' "
                f"and datetime='{self.datetime.strftime('%Y.%m.%d')}'"
            )
            print(datetime.now())
            print("Удаление из базы данных")
            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, totla_sum) "
                f"VALUES ('{self.telegram_id}', '{self.datetime.strftime('%Y.%m.%d')}', '{self.totla_sum}')"
            )
            db.conn.commit()
            print(datetime.now())
            print(f"Обновление базы стоимости")
            print(f"Данные для {self.telegram_id} добавлены успешно!")
        except sqlite3.IntegrityError:
            print(f"Already exists in the database.")

    @staticmethod
    def init_new_user(tg_id: int, totla_sum: float):
        query = ""
        day_increment = date.today()
        query += f"({tg_id}, '{day_increment.strftime('%Y.%m.%d')}', {totla_sum}),"

        try:
            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, totla_sum) "
                f"VALUES {query[0:-1]}"
            )
            db.conn.commit()
            print(f"INIT_NEW_USER___all days added successfully!")
        except sqlite3.IntegrityError:
            print(f"Already exists in the database.")

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
                )
            )
        return data_coins

    @staticmethod
    def delete_user_data(tg_id):
        db.cursor.execute(f"DELETE FROM graph_data WHERE tg_id='{tg_id}'")
        db.conn.commit()
        print(f"User {tg_id} removed successfully!")
