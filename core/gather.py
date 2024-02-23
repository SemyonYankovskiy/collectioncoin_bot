# # Создаем функцию, которая будет выполняться каждый день в 20:00
import asyncio
from datetime import datetime
import schedule
from database import User, DataCoin
from handlers.services import send_message_to_user
from .site_calc import authorize, download, file_opener, parsing


class GatherFail(Exception):
    pass


async def gather_graph_data():
    users_list = User.get_all()
    print(datetime.now(), "| ", "Start gather update")

    check = "Заебало, не работает"

    for i in range(3):
        print(f"{i+1} check")
        for user in users_list:
            # user_coin_id, session = authorize(user.email, user.password)
            # parsing(session, user, user_coin_id)
            # file_name = download(user_coin_id, session)
            # total, total_count = file_opener(file_name)
            # DataCoin(user.telegram_id, total, total_count).save()
            # await asyncio.sleep(60)
            print(f"do something for {user}")

        check = DataCoin.check_graph_data()

        if check == "Для всех пользователей запись в БД сегодня существует":
            break
        await asyncio.sleep(5 if i == 0 else 10)  # задержка 5 минут первый раз, затем 10 минут

    else:
        await send_message_to_user(726837488, f"❌ Нет данных\n{check}")


async def gather_manager():
    print(datetime.now(), "| ", "Start gather manager")
    schedule.every().day.at("12:52").do(lambda: asyncio.create_task(gather_graph_data()))
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
