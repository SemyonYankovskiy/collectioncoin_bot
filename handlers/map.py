import os

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
    print(current_location)
    for name, callback_data in world_locations:
        if current_location == callback_data:
            name = f"❇️ {name}"
        keyboard.append(InlineKeyboardButton(name, callback_data=callback_data))
    return InlineKeyboardMarkup().add(*keyboard)


async def send_user_map(location: str, user: User):
    await bot.send_chat_action(chat_id=user.telegram_id, action="upload_photo")

    world_map = WorldMap(user_coin_id=user.user_coin_id)
    map_name = world_map.create_map(location=location)

    keyboard = get_maps_keyboards(current_location=f"map:{location}")

    map_img = InputFile(map_name)

    await bot.send_photo(chat_id=user.telegram_id, photo=map_img, reply_markup=keyboard)
    os.remove(map_name)


@dp.message_handler(commands=["map"])
@check_and_set_user
async def maps(message: MessageWithUser):
    location = "World"
    await send_user_map(location, message.user)


@dp.callback_query_handler(lambda c: c.data.startswith("map:"))
@check_and_set_user
async def process_callback_map(callback_query: CallbackQueryWithUser):
    location = callback_query.data[4:]
    user = User.get(tg_id=callback_query.from_user.id)
    await send_user_map(location, user)
    await bot.delete_message(chat_id=user.telegram_id, message_id=callback_query.message.message_id)
