import asyncio
import socket
from datetime import datetime
import random
import aiohttp
import requests

from database import User
from handlers.services import send_message_to_user
from .cache import storage
from ..site_calc import authorize, parsing


async def check_user_notifications(user: User):

    print(datetime.now(), "| ", f"check user ({user.email}) notifications")

    old_messages = storage.get_data(user.telegram_id, "new_messages") or 0
    old_swap_messages = storage.get_data(user.telegram_id, "swap_messages") or 0

    if old_messages < int(user.new_messages):
        new_messages = user.new_messages  # - old_messages
        message_m = f"У вас ({new_messages}) новых сообщений"
        await send_message_to_user(user.telegram_id, message_m)
        print(datetime.now(), "| ", f"Пользователю {user.email} отправлено сообщение {message_m}")
        storage.set_data(user.telegram_id, "new_messages", user.new_messages)
    else:
        print(datetime.now(), "| ", f"У Пользователя {user.email} нет новых сообщений")

    if old_swap_messages < int(user.new_swap):
        new_swap = user.new_swap  # - old_swap_messages
        message_s = f"У вас ({new_swap}) новых предложений обмена"
        await send_message_to_user(user.telegram_id, message_s)
        print(datetime.now(), "| ", f"Пользователю {user.email} отправлено сообщение {message_s}")
        storage.set_data(user.telegram_id, "swap_messages", user.new_swap)
    else:
        print(datetime.now(), "| ", f"У Пользователя {user.email} нет новых обменов")


async def new_notifications_checker():

    # Получить текущее время
    now = datetime.now()

    # Установить время для сравнения
    start_time = datetime(now.year, now.month, now.day, 10, 0)  # 10:00
    end_time = datetime(now.year, now.month, now.day, 20, 0)  # 20:00

    users_list = User.get_all()
    for user in users_list:
        try:
            if start_time <= now <= end_time:
                print(now, "| ", "Start notifications checker")
                user_coin_id, session = authorize(user.email, user.password)
                parsing(session, user, user_coin_id)
                await check_user_notifications(user)
        except requests.exceptions.ConnectionError as e:
            await send_message_to_user(726837488, f"Снова наебнулись уведомления {e})")
        await asyncio.sleep(random.randint(60, 180))


async def notifications_checker():
    while True:
        try:
            await new_notifications_checker()

        except (asyncio.exceptions.TimeoutError, aiohttp.ClientOSError, socket.gaierror) as e:
            # Обработка исключений, таких как тайм-ауты или ошибки сети
            await send_message_to_user(726837488, f"Снова наебнулись уведомления {e})")
            print(f"Произошла ошибка: {e}")
            # Повторная попытка выполнения функции через некоторое время
            await asyncio.sleep(5)  # Подождать 5 секунд перед повторной попыткой
            await new_notifications_checker()
        await asyncio.sleep(60 * 10)  # Время между проверками новых сообщений, в т.ч. парсинга, шоб не ддосить сайт
