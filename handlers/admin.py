import asyncio
import sqlite3
from datetime import datetime

from aiogram.utils import exceptions

from core.types import MessageWithUser
from database import User
from handlers import profile
from handlers.graph import grafik
from handlers.services import refresh_data, summ, _summ
from helpers.handler_decorators import check_and_set_user
from settngs import dp, bot
from database import DataCoin, User
from aiogram import types



@dp.message_handler(commands=["all"])
@check_and_set_user
async def all_(message: MessageWithUser):
    print(datetime.now(),"| ",  message.from_user.id, 'commands=["all"]')
    # await refresh_data(message)
    await profile(message)
    await _summ(message)
    await grafik(message)





async def send_to_all_users(message_text= "Бот был перезагружен, обновите данные \n /refresh"):
    # Получаем список всех пользователей из базы данных
    users_list = User.get_all()


    # Отправляем сообщение каждому пользователю
    for user in users_list:
        print(user.telegram_id)
        await send_message_to_users_handler(user.telegram_id, message_text)
        await asyncio.sleep(0.1)


# Вспомогательная функция для безопасной отправки сообщения
async def send_message_to_users_handler(user_id: int, text: str, disable_notification: bool = False) -> bool:
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        print(f"Пользователь [ID:{user_id}] заблокировал бота")
    except exceptions.ChatNotFound:
        print(f"Неверный ID пользователя [ID:{user_id}]")
    except exceptions.RetryAfter as e:
        print(f"Превышен лимит отправки сообщений для [ID:{user_id}]. Подождите {e.timeout} секунд.")
        await asyncio.sleep(e.timeout)
        return await send_message_to_users_handler(user_id, text)
    except exceptions.UserDeactivated:
        print(f"Пользователь [ID:{user_id}] деактивирован")
    except exceptions.TelegramAPIError:
        print(f"Не удалось отправить сообщение пользователю [ID:{user_id}]")
    else:
        print(f"Сообщение успешно отправлено пользователю [ID:{user_id}]")
        return True
    return False

