from datetime import datetime

import emoji

from core.site_calc import more_info, refresh
from core.types import MessageWithUser
from database import DataCoin, User
from helpers.handler_decorators import check_and_set_user
from helpers.limiter import rate_limit
from settngs import dp, bot


@dp.message_handler(commands=["refresh"])
@check_and_set_user
@rate_limit(600)
async def refresh_data(message: MessageWithUser):
    print(message.from_user.id, 'commands=["refresh"]')
    print(datetime.now())
    """Функция принудительного обновления"""

    await bot.send_chat_action(chat_id=message.from_id, action="find_location")

    refresh(message.from_user.id)
    await message.answer("База данных успешно обновлена")


async def send_text_to_user(user: User, text: str):
    await bot.send_message(user.telegram_id, text)


@dp.message_handler(commands=["summ"])
@check_and_set_user
async def summ(message: MessageWithUser):
    print(message.from_user.id, 'commands=["summ"]')
    print(datetime.now())
    coin_st = DataCoin.get_for_user(message.from_user.id, limit=1)
    # обращаемся к функции more info, передаем в эту функциию значение переменной (значение из 4 столбца массива)
    lot, count = more_info(f"./users_files/{message.user.user_coin_id}_.xlsx")

    await message.answer(emoji.emojize(":coin:"))
    await message.answer(
        f"Количество монет {lot} \n"
        f"Количество стран {count} \n"
        f"Общая стоимость {coin_st[0].totla_sum} руб."
    )
