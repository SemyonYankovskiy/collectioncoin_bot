# # Создаем функцию, которая будет выполняться каждый день в 20:00
import asyncio
import time
from datetime import datetime

import schedule

from database import User, DataCoin
from handlers.admin import send_message_to_users_handler
from .site_calc import authorize, download, file_opener, parsing


class GatherFail(Exception):
    pass

def gather_graph_data(*args, **kwargs):
    users_list = User.get_all()
    print(datetime.now(), "| ", "Start gather update")

    for user in users_list:
        user_coin_id, session = authorize(user.email, user.password)
        parsing(session, user, user_coin_id)
        file_name = download(user_coin_id, session)
        total, total_count = file_opener(file_name)
        DataCoin(user.telegram_id, total, total_count).save()

    # if not DataCoin.check_graph_data():
    #     send_message_to_users_handler(726837488, "Нет сегодняшней записи в БД")


def gather_manager(*args):
    print(datetime.now(), "| ", "Start gather manager")
    schedule.every().day.at("09:55").do(gather_graph_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
