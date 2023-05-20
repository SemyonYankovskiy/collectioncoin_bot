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
                            password TEXT NOT NULL,
                            new_messages INTEGER DEFAULT NULL,
                            new_swap INTEGER DEFAULT NULL);"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS graph_data
                            (id INTEGER PRIMARY KEY NOT NULL,
                            tg_id INTEGER NOT NULL,
                            datetime TEXT NOT NULL,
                            totla_sum REAL NOT NULL,
                            user_coin_id TEXT NOT NULL);"""
        )
        conn.commit()


class DataCoin:
    def __init__(self, telegram_id, totla_sum, user_coin_id, datetime_=datetime.now()):
        self.telegram_id = telegram_id
        self.totla_sum = totla_sum
        self.datetime = datetime_
        self.user_coin_id = user_coin_id

    def save(self):
        db = Database()

        try:
            db.cursor.execute(f"DELETE FROM graph_data WHERE tg_id='{self.telegram_id}' and datetime='{self.datetime.strftime('%Y.%m.%d')}'")
            db.cursor.execute(
                f"INSERT INTO graph_data (tg_id, datetime, user_coin_id,totla_sum) "
                f"VALUES ('{self.telegram_id}', '{self.datetime.strftime('%Y.%m.%d')}', "
                f"'{self.user_coin_id}', '{self.totla_sum}')"
            )
            db.conn.commit()
            print(f"{self.user_coin_id} added successfully!")
        except sqlite3.IntegrityError:
            print(f"Already exists in the database.")

    def debug(self):
        db = Database()
        db.cursor.execute("SELECT tg_id, COUNT(*) FROM graph_data GROUP BY tg_id")
        # Для каждого пользователя в результате запроса
        for row in db.cursor:
            print("Количество строк")
            print(row)
            if row[1] < 30:


                date1 = date.today()
                print(date1)

                db.cursor.execute(
                    f"SELECT datetime FROM graph_data ORDER BY datetime DESC LIMIT 1;"
                )
                date2 = db.cursor.fetchone()
                date21 = date2[0]
                date22 = datetime.strptime(date21, "%Y.%m.%d")
                date23 = date22.date()
                print(date23)

                delta = date1 - date23
                #
                print(delta.days)

                query = ""
                day_increment = date.today()
                for _ in range(delta.days):
                    query += f"({self.telegram_id}, '{day_increment.strftime('%Y.%m.%d')}', {self.totla_sum}, {self.user_coin_id}),"
                    day_increment -= timedelta(days=1)

                try:
                    db.cursor.execute(
                        f"INSERT INTO graph_data (tg_id, datetime, totla_sum, user_coin_id) "
                        f"VALUES {query[0:-1]}"
                    )
                    db.conn.commit()
                except sqlite3.IntegrityError:
                    print(f"ГРОБ ГРОБ КЛАДБИЩЕ МОГИЛА СМЕРТЬ ГАВНО")
            else:
                continue

    @staticmethod
    def init_new_user(tg_id: int, totla_sum: float, user_coin_id):
        db = Database()
        query = ""
        day_increment = date.today()
        for _ in range(30):
            query += f"({tg_id}, '{day_increment.strftime('%Y.%m.%d')}', {totla_sum}, {user_coin_id}),"
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
        # db.cursor.execute("SELECT tg_id, COUNT(*) FROM graph_data GROUP BY tg_id")
        # # Для каждого пользователя в результате запроса
        # for row in db.cursor:
        #     if row[1] >= 30:
        #         raise DBFail("Больше 30 значений")
        #     else:
        #         continue

    @staticmethod
    def delete_user_data(tg_id):
        db = Database()
        db.cursor.execute(f"DELETE FROM graph_data WHERE tg_id='{tg_id}'")
        db.conn.commit()
        print(f"User {tg_id} removed successfully!")


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
                f"VALUES ('{self.telegram_id}', '{self.email}', '{self.password}', {self.new_messages or 0}, {self.new_swap or 0})"
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
    def get(tg_id):
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

