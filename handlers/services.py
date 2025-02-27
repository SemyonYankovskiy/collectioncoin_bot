import asyncio
from datetime import datetime
from aiogram.utils import exceptions
import emoji
from core.site_calc import more_info, authorize, parsing, download, file_opener
from helpers.types import MessageWithUser
from database import DataCoin, User
from handlers.map import save_user_map
from helpers.handler_decorators import check_and_set_user
from helpers.limiter import rate_limit
from settngs import dp, bot


@dp.message_handler(commands=["refresh"])
@check_and_set_user
@rate_limit(600)
async def refresh_data(message: MessageWithUser):
    print(datetime.now(), "| USER:", message.from_user.id, 'commands=["refresh"]')

    """Функция принудительного обновления"""

    await bot.send_chat_action(chat_id=message.from_id, action="upload_document")

    user = User.get(message.from_user.id)
    # user_coin_id, session = authorize(user.email, user.password)
    # parsing(session, user, user_coin_id)
    # file_name = download(user_coin_id, session)
    file_name = f"./users_files/32693_.xlsx"
    total, total_count = file_opener(file_name)
    DataCoin(user.telegram_id, total, total_count).save()
    print(datetime.now(), "| ", f"Скачиваем карты для {user.user_name}")
    await message.answer("Я не завис, скачиваю карты")
    save_user_map(user)

    await message.answer("База данных успешно обновлена")


# Вспомогательная функция для безопасной отправки сообщения
async def send_message_to_user(user_id: int, text: str, disable_notification: bool = False, parse_mode="MARKDOWN") -> bool:
    user = User.get(user_id)
    try:
        await bot.send_message(user_id, text, parse_mode, disable_notification=disable_notification, )
    except exceptions.BotBlocked:
        print(datetime.now(), "| ", f"Пользователь [{user.email}] заблокировал бота")
    except exceptions.ChatNotFound:
        print(datetime.now(), "| ", f"Неверный ID пользователя [{user.email}]")
    except exceptions.RetryAfter as e:
        print(datetime.now(), "| ", f"Превышен лимит отправки сообщений для [{user.email}]. Жди {e.timeout} сек.")
        await asyncio.sleep(e.timeout)
        return await send_message_to_user(user_id, text)
    except exceptions.UserDeactivated:
        print(datetime.now(), "| ", f"Пользователь [{user.email}] деактивирован")
    except exceptions.TelegramAPIError:
        print(datetime.now(), "| ", f"Не удалось отправить сообщение пользователю [{user.email}]")
    else:
        print(datetime.now(), "| ", f"Сообщение успешно отправлено пользователю [{user.email}]")
        return True
    return False


@dp.message_handler(commands=["summ"])
@check_and_set_user
async def summ(message: MessageWithUser):

    await message.answer(emoji.emojize(":coin:"))
    await _summ(message)


@check_and_set_user
async def _summ(message: MessageWithUser):
    print(datetime.now(), "| USER:", message.from_user.id, 'commands=["summ"]')

    coin_st = DataCoin.get_for_user(message.from_user.id, limit=1)
    # обращаемся к функции more info, передаем в эту функциию значение переменной (значение из 4 столбца массива)
    try:
        lot, count, sold = more_info(f"./users_files/{message.user.user_coin_id}_.xlsx")

        await message.answer(
            f"🪙 Количество монет {lot} \n"
            f"🌐 Количество стран {count} \n\n"
            f"💶 Общая стоимость {coin_st[0].totla_sum} руб. \n\n"
            f"💵 Потрачено {sold} руб. "
        )
    except Exception:
        await message.answer(f"Ой! Обновите базу данных вручную \n/refresh")
