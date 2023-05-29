# # Создаем функцию, которая будет выполняться каждый день в 20:00
import time
import schedule
from database import User, DataCoin
from .site_calc import authorize, download, file_opener, parsing


class GatherFail(Exception):
    pass


def gather_graph_data(*args, **kwargs):
    users_list = User.get_all()

    for user in users_list:
        user_coin_id, session = authorize(user.email, user.password)
        file_name = download(user_coin_id, session)
        total = file_opener(file_name)
        DataCoin(user.telegram_id, total, user_coin_id).save()
        parsing(session, user, user_coin_id)


def gather_manager(*args):
    print("Start gather manager")
    schedule.every().day.at("08:00").do(gather_graph_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

