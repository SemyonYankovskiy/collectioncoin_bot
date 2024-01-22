import asyncio
from datetime import datetime
import random

import requests

from database import User
from handlers.services import send_text_to_user
from .cache import storage
from ..site_calc import authorize, parsing


async def check_user_notifications(user: User):

    print(datetime.now(),"| ", f"check user ({user.email}) notifications")

    old_messages = storage.get_data(user.telegram_id, "new_messages") or 0
    old_swap_messages = storage.get_data(user.telegram_id, "swap_messages") or 0

    if old_messages < int(user.new_messages):
        new_messages = user.new_messages #- old_messages
        await send_text_to_user(user, f"У вас ({new_messages}) новых сообщений")
        storage.set_data(user.telegram_id, "new_messages", user.new_messages)

    if old_swap_messages < int(user.new_swap):
        new_swap = user.new_swap #- old_swap_messages
        await send_text_to_user(user, f"У вас ({new_swap}) новых предложений обмена")
        storage.set_data(user.telegram_id, "swap_messages", user.new_swap)


async def new_notifications_checker():

    # Получить текущее время
    now = datetime.now()

    # Установить время для сравнения
    start_time = datetime(now.year, now.month, now.day, 10, 0)  # 10:00
    end_time = datetime(now.year, now.month, now.day, 20, 0)  # 20:00



    while True:
        users_list = User.get_all()
        for user in users_list:
            try:
                if start_time <= now <= end_time:
                    print(now, "| ", "Start notifications checker")
                    user_coin_id, session = authorize(user.email, user.password)
                    parsing(session, user, user_coin_id)
                    await check_user_notifications(user)
            except requests.exceptions.ConnectionError as e:
                await send_text_to_user(user.telegram_id, f"Снова наебнулись уведомления {e})")
            await asyncio.sleep(random.randint(60, 120))
        await asyncio.sleep(60 * 60)
