import sqlite3
from datetime import datetime, date, timedelta
from typing import List

from .database import Database


class DataCoin:
    def __init__(self, telegram_id, totla_sum, user_coin_id, datetime_=datetime.now(), id_=None):
        self.id = id_
        self.telegram_id = telegram_id
        self.totla_sum = totla_sum
        self.datetime = datetime_
        self.user_coin_id = user_coin_id

    def save(self):
        db = Database()

        try:
            db.cursor.execute(
                f"DELETE FROM graph_data WHERE tg_id='{self.telegram_id}' "
                f"and datetime='{self.datetime.strftime('%Y.%m.%d')}'"
            )
            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, user_coin_id,totla_sum) "
                f"VALUES ('{self.telegram_id}', '{self.datetime.strftime('%Y.%m.%d')}', "
                f"'{self.user_coin_id}', '{self.totla_sum}')"
            )
            db.conn.commit()
            print(f"{self.user_coin_id} added successfully!")
        except sqlite3.IntegrityError:
            print(f"Already exists in the database.")

    @staticmethod
    def init_new_user(tg_id: int, totla_sum: float, user_coin_id):
        db = Database()
        query = ""
        day_increment = date.today()
        for _ in range(30):
            query += (
                f"({tg_id}, '{day_increment.strftime('%Y.%m.%d')}', {totla_sum}, {user_coin_id}),"
            )
            day_increment -= timedelta(days=1)

        try:
            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, totla_sum, user_coin_id) "
                f"VALUES {query[0:-1]}"
            )
            db.conn.commit()
            print(f"INIT_NEW_USER___all days added successfully!")
        except sqlite3.IntegrityError:
            print(f"Already exists in the database.")

    @staticmethod
    def get_for_user(tg_id) -> List["DataCoin"]:
        db = Database()
        db.cursor.execute(f"SELECT * FROM graph_data WHERE tg_id='{tg_id}' ORDER BY datetime DESC")
        data_coins = []
        for sublist in db.cursor.fetchall():
            data_coins.append(
                DataCoin(
                    id_=sublist[0],
                    telegram_id=sublist[1],
                    datetime_=sublist[2],
                    totla_sum=sublist[3],
                    user_coin_id=sublist[4],
                )
            )
        return data_coins

    @staticmethod
    def delete_user_data(tg_id):
        db = Database()
        db.cursor.execute(f"DELETE FROM graph_data WHERE tg_id='{tg_id}'")
        db.conn.commit()
        print(f"User {tg_id} removed successfully!")
