from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.site_calc import get_top_10_coin
from core.types import MessageWithUser, CallbackQueryWithUser
from helpers.handler_decorators import check_and_set_user

from settngs import dp, bot


def _get_top10_keyboards(active_mode: str):
    keyboard = []
    mode_of_top = [
        ("Цена ⬆️", "expensive_value"),
        ("Цена ⬇️", "cheap_value"),
        ("Дата добавления ⬆️", "last_append"),
        ("Дата добавления ⬇️", "first_append"),
        ("Год ⬆️", "novelty"),
        ("Год ⬇️", "old"),
    ]
    for name, callback_data in mode_of_top:
        if callback_data == active_mode:
            name = f"❇️ {name}"
        keyboard.append(InlineKeyboardButton(name, callback_data=callback_data))

    return InlineKeyboardMarkup(row_width=2).add(*keyboard)


def _get_top10_message_text(user_coin_id, mode: str):
    top_coin = get_top_10_coin(f"./users_files/{user_coin_id}_.xlsx", mode=mode)
    output = ""
    for flag, nominal, year, cena, md, name, comment in top_coin:
        output += f"{flag} {nominal} {year} {cena} {md} {name} {comment} \n\n"
    return output


@dp.message_handler(commands=["top"])
@check_and_set_user
async def top10_default(message: MessageWithUser):
    default_mode = "old"
    output = _get_top10_message_text(message.user.user_coin_id, mode=default_mode)
    keyboards = _get_top10_keyboards(active_mode=default_mode)
    await message.answer(output, reply_markup=keyboards)


@dp.callback_query_handler(
    lambda c: c.data
    in ["expensive_value", "cheap_value", "last_append", "first_append", "novelty", "old"]
)
@check_and_set_user
async def top10_by_sort(callback_query: CallbackQueryWithUser):
    mode = callback_query.data
    keyboards = _get_top10_keyboards(active_mode=mode)
    output = _get_top10_message_text(callback_query.user.user_coin_id, mode=mode)

    await callback_query.message.answer(output, reply_markup=keyboards)
    await bot.delete_message(
        chat_id=callback_query.user.telegram_id, message_id=callback_query.message.message_id
    )
