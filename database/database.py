import sqlite3

user_default_color_schema = "YlGn"


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("./db/users.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute(
            f"""CREATE TABLE IF NOT  EXISTS users
                            (tg_id INTEGER PRIMARY KEY NOT NULL,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL,
                            user_coin_id TEXT DEFAULT NULL,
                            new_messages INTEGER DEFAULT NULL,
                            new_swap INTEGER DEFAULT NULL,
                            user_name TEXT DEFAULT NULL,
                            map_color_schema VARCHAR(50) DEFAULT '{user_default_color_schema}',
                            last_refresh TEXT DEFAULT NULL);"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS graph_data
                            (id INTEGER PRIMARY KEY NOT NULL,
                            tg_id INTEGER NOT NULL,
                            datetime TEXT NOT NULL,
                            totla_sum REAL NOT NULL,
                            totla_count INTEGER NOT NULL);"""
        )
        self.conn.commit()


db_connection = Database()
