import os
from datetime import datetime

from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile, InlineKeyboardButton, InlineKeyboardMarkup

from core.map import WorldMap
from core.types import MessageWithUser, CallbackQueryWithUser
from database import User
from helpers.handler_decorators import check_and_set_user
from settngs import dp, bot


def get_maps_keyboards(current_location: str):
    world_locations = [
        ("Европа", "map:Europe"),
        ("Ц.Америка", "map:North_America"),
        ("Ю.Америка", "map:South_America"),
        ("Азия", "map:Asia"),
        ("Африка", "map:Africa"),
        ("Острова Азии", "map:Asian_Islands"),
        ("Мир", "map:World"),
    ]
    keyboard = []
    print(datetime.now(), "| ", current_location)
    for name, callback_data in world_locations:
        if current_location == callback_data:
            name = f"❇️ {name}"
        keyboard.append(InlineKeyboardButton(name, callback_data=callback_data))
    return InlineKeyboardMarkup().add(*keyboard)


async def send_user_map(location: str, user: User):
    await bot.send_chat_action(chat_id=user.telegram_id, action="find_location")

    keyboard = get_maps_keyboards(current_location=f"map:{location}")

    map_img = InputFile(f"./users_files/{user.user_coin_id}_{location}.png")

    await bot.send_photo(chat_id=user.telegram_id, photo=map_img, reply_markup=keyboard)


def save_user_map(user: User):
    location = ["World", "Asian_Islands", "Africa", "Asia", "South_America", "North_America", "Europe"]
    try:
        for item in location:
            world_map = WorldMap(user_coin_id=user.user_coin_id)
            world_map.set_color_schema(user.map_color_schema)
            world_map.create_map(location=item)

    except Exception as e:
        print(f"Ой! Скачивание карты сломалось\n {e}")

# @dp.message_handler(commands=["save"])
# @check_and_set_user
# async def save_(message: MessageWithUser):
#     try:
#         save_user_map(message.user)
#         await message.answer(f"Done")
#     except Exception as e:
#         await message.answer(f"Ой!\n{e}")


@dp.message_handler(Text(equals="Карта"))
@dp.message_handler(commands=["map"])
@check_and_set_user
async def maps(message: MessageWithUser):
    print(datetime.now(), "| ", message.from_user.id, 'commands=["map"]')
    try:
        location = "World"
        await send_user_map(location, message.user)
    except Exception as e:
        await message.answer(f"Ой! Обновите базу данных вручную \n/refresh\n {e}")




@dp.callback_query_handler(lambda c: c.data.startswith("map:"))
@check_and_set_user
async def process_callback_map(callback_query: CallbackQueryWithUser):
    location = callback_query.data[4:]
    user = User.get(tg_id=callback_query.from_user.id)
    await send_user_map(location, user)
    await bot.delete_message(chat_id=user.telegram_id, message_id=callback_query.message.message_id)


def get_choose_color_map_scheme_keyboard():
    schemas = [
        "Greys",
        "Purples",
        "Blues",
        "Greens",
        "Oranges",
        "Reds",
        "YlOrBr",
        "YlOrRd",
        "OrRd",
        "PuRd",
        "RdPu",
        "BuPu",
        "GnBu",
        "PuBu",
        "YlGnBu",
        "PuBuGn",
        "BuGn",
        "YlGn",
    ]
    keyboard = []

    for schema_name in schemas:
        keyboard.append(
            InlineKeyboardButton(schema_name, callback_data=f"set_color_map_scheme:{schema_name}")
        )
    return InlineKeyboardMarkup(row_width=5).add(*keyboard)


@dp.callback_query_handler(lambda c: c.data == "choose_color_map_scheme")
@check_and_set_user
async def choose_color_map_scheme(callback_query: CallbackQueryWithUser):
    map_img = InputFile("img/color_map_scheme.png")
    keyboard = get_choose_color_map_scheme_keyboard()
    await bot.send_photo(
        chat_id=callback_query.user.telegram_id, photo=map_img, reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: c.data.startswith("set_color_map_scheme:"))
@check_and_set_user
async def set_color_map_scheme(callback_query: CallbackQueryWithUser):
    color_name = callback_query.data.split(":")[-1]
    callback_query.user.map_color_schema = color_name
    callback_query.user.save()
    # await callback_query.answer("Готово, чекай карту!", show_alert=True)
    await callback_query.message.answer("Сохранено! Изменения вступят в силу после обновления данных")
