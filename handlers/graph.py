import os

from aiogram.types import InputFile

from core.site_calc import get_graph
from core.types import MessageWithUser
from helpers.handler_decorators import check_and_set_user
from settngs import dp, bot


@dp.message_handler(commands=["grafik"])
@check_and_set_user
async def grafik(message: MessageWithUser):
    await bot.send_chat_action(chat_id=message.from_id, action="upload_photo")

    graph_name = get_graph(message.from_user.id)
    photo = InputFile(graph_name)
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)
    os.remove(graph_name)
