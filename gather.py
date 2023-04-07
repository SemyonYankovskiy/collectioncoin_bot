# # Создаем функцию, которая будет выполняться каждый день в 20:00
import time
import schedule

from site_calc import authorize, download, file_opener


def gather_graph_data(*args, **kwargs):
    print("Работает")


def gather_manager(*args):
    print("Start")
    schedule.every().day.at("18:00").do(gather_graph_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
