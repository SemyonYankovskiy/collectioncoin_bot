# # Создаем функцию, которая будет выполняться каждый день в 20:00
import asyncio
import random
from datetime import datetime
import schedule
from requests import RequestException

from database import User, DataCoin
from handlers.services import send_message_to_user
from .site_calc import authorize, download, file_opener, parsing


class GatherFail(Exception):
    pass


async def gather_graph_data():
    users_list = User.get_all()
    print(datetime.now(), "| ", "Запуск обновления данных")
    check = "AAA CYKA"
    for i in range(3):
        print(datetime.now(), "| ", "Пробуем спарсить и скачать нужные данные, " f"{i + 1} попытка")
        retry_for_users = []  # список пользователей, для которых нужно повторно выполнить операции
        all_data_exist = True  # флаг для проверки наличия данных у всех пользователей
        for user in users_list:
            try:
                user_coin_id, session = authorize(user.email, user.password)
            except RequestException as e:
                print("Error", e)
            else:
                parsing(session, user, user_coin_id)
                file_name = download(user_coin_id, session)
                total, total_count = file_opener(file_name)
                DataCoin(user.telegram_id, total, total_count).save()

                await asyncio.sleep(random.randint(30, 60))

            check = DataCoin.check_graph_data(user.telegram_id)
            if check != "Для всех пользователей запись в БД сегодня существует":
                all_data_exist = False
                retry_for_users.append(user)

        if all_data_exist:
            print(datetime.now(), "| ", check)
            await send_message_to_user(726837488, f"️✅ {check}")
            break

        # повторно выполняем операции только для пользователей, у которых нет данных
        users_list = retry_for_users
        # await asyncio.sleep(5*60 if i == 0 else 10*60)  # задержка 5 мин первый раз, затем 10 мин
        await asyncio.sleep(5*60)  # задержка 5 мин
    else:
        print(datetime.now(), "| ", check)
        await send_message_to_user(726837488, f"❌ Нет данных\n{check}")


async def gather_manager():
    print(datetime.now(), "| ", "Start gather manager")
    schedule.every().day.at("07:00").do(lambda: asyncio.create_task(gather_graph_data()))
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
