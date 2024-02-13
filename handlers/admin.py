import asyncio
from datetime import datetime
from core.types import MessageWithUser
from handlers import profile
from handlers.graph import grafik
from handlers.services import _summ, send_message_to_user
from helpers.handler_decorators import check_and_set_user
from settngs import dp
from database import User


@dp.message_handler(commands=["all"])
@check_and_set_user
async def all_(message: MessageWithUser):
    print(datetime.now(), "| ",  message.from_user.id, 'commands=["all"]')
    # await refresh_data(message)
    await profile(message)
    await _summ(message)
    await grafik(message)


async def send_to_all_users(message_text="Бот был перезагружен, обновите данные \n /refresh"):
    # Получаем список всех пользователей из базы данных
    users_list = User.get_all()

    # Отправляем сообщение каждому пользователю
    for user in users_list:
        await send_message_to_user(user.telegram_id, message_text)
        await asyncio.sleep(0.1)
