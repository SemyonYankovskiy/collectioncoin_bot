import os

from aiogram.types import InputFile, InlineKeyboardButton, InlineKeyboardMarkup

from core.site_calc import get_graph
from core.types import MessageWithUser, CallbackQueryWithUser
from database import User
from helpers.handler_decorators import check_and_set_user
from settngs import dp, bot


def get_graph_keyboards(current_limit: str):
    time_limit = [
        ("Последний месяц", "month:1"),
        ("Послдение 2 месяца", "month:2"),
        ("Последние 6 месяцев", "month:6"),
        ("Последний год", "month:12"),
        ("Всё время", "month:all"),
    ]
    keyboard = []

    for name, callback_data in time_limit:
        if callback_data != current_limit:
            keyboard.append(InlineKeyboardButton(name, callback_data=callback_data))

    return InlineKeyboardMarkup(row_width=2).add(*keyboard)


async def send_user_graph(callback_data: str, user: User):
    await bot.send_chat_action(chat_id=user.telegram_id, action="upload_photo")

    limit_str = callback_data[6:]
    if limit_str.isdigit():
        limit = int(limit_str) * 30
    else:
        limit = None

    graph_name = get_graph(user.telegram_id, limit=limit)

    keyboard = get_graph_keyboards(current_limit=callback_data)

    map_img = InputFile(graph_name)

    await bot.send_photo(chat_id=user.telegram_id, photo=map_img, reply_markup=keyboard)
    os.remove(graph_name)


@dp.message_handler(commands=["grafik"])
@check_and_set_user
async def grafik(message: MessageWithUser):
    default_limit = "month:1"
    await send_user_graph(callback_data=default_limit, user=message.user)


@dp.callback_query_handler(lambda c: c.data.startswith("month:"))
@check_and_set_user
async def process_callback_graph(callback_query: CallbackQueryWithUser):
    limit = callback_query.data
    user = User.get(tg_id=callback_query.from_user.id)
    await send_user_graph(limit, user)
    await bot.delete_message(chat_id=user.telegram_id, message_id=callback_query.message.message_id)
