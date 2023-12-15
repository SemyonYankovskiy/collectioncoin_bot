import os
from datetime import datetime

from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile, InlineKeyboardButton, InlineKeyboardMarkup

from core.site_calc import get_graph
from core.types import MessageWithUser, CallbackQueryWithUser
from database import User
from helpers.handler_decorators import check_and_set_user
from settngs import dp, bot


def get_graph_keyboards(current_limit: str):
    time_limit = [
        ("Последние 2 месяца", "month:2"),
        ("Последние 6 месяцев", "month:6"),
        ("Последний год", "month:12"),
        ("Всё время", "month:all"),
        ("Последний месяц", "month:1"),
    ]
    keyboard = []

    for name, callback_data in time_limit:
        if current_limit == callback_data:
            name = f"❇️ {name}"
        keyboard.append(InlineKeyboardButton(name, callback_data=callback_data))

    return InlineKeyboardMarkup(row_width=2).add(*keyboard)


async def send_user_graph(callback_data: str, user: User):
    await bot.send_chat_action(chat_id=user.telegram_id, action="upload_photo")

    limit_str = callback_data[6:]
    if limit_str.isdigit():
        limit = int(limit_str) * 30
    else:
        limit = None

    graph_name, len_active = get_graph(user.telegram_id, limit=limit)
    keyboard = get_graph_keyboards(current_limit=callback_data)
    map_img = InputFile(graph_name)

    if limit is None or limit > len_active:
        await bot.send_photo(
            chat_id=user.telegram_id,
            photo=map_img,
            reply_markup=keyboard,
            caption=f"❕ Данные приведены за последние {len_active} {get_day_verbose_name(len_active)}",
        )
    else:
        await bot.send_photo(chat_id=user.telegram_id, photo=map_img, reply_markup=keyboard)

    os.remove(graph_name)


def get_day_verbose_name(days: int) -> str:
    if days % 10 == 1 and days % 100 != 11:
        name = "день"
    elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
        name = "дня"
    else:
        name = "дней"
    return name

@dp.message_handler(Text(equals="График"))
@dp.message_handler(commands=["grafik"])
@check_and_set_user
async def grafik(message: MessageWithUser):
    print(datetime.now(), "| ",  message.from_user.id, 'commands=["grafik"]')

    default_limit = "month:1"
    await send_user_graph(callback_data=default_limit, user=message.user)


@dp.callback_query_handler(lambda c: c.data.startswith("month:"))
@check_and_set_user
async def process_callback_graph(callback_query: CallbackQueryWithUser):
    limit = callback_query.data
    user = User.get(tg_id=callback_query.from_user.id)
    await send_user_graph(limit, user)
    # messages = await bot.history(chat_id=user.telegram_id, limit=2)
    # for callback_query in messages:
    await bot.delete_message(chat_id=user.telegram_id, message_id=callback_query.message.message_id)
