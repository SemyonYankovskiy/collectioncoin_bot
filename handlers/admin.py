from datetime import datetime

from core.types import MessageWithUser
from handlers import profile
from handlers.graph import grafik
from handlers.map import maps
from handlers.services import refresh_data, summ
from helpers.handler_decorators import check_and_set_user
from settngs import dp


@dp.message_handler(commands=["all"])
@check_and_set_user
async def all_(message: MessageWithUser):
    print(message.from_user.id, 'commands=["all"]')
    print(datetime.now())
    await refresh_data(message)
    await profile(message)
    await summ(message)
    await grafik(message)
    await maps(message)
