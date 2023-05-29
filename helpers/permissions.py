from functools import wraps
from typing import Callable

from aiogram import types

from database import User


def login_required(handler: Callable):
    @wraps(handler)
    async def wrapper(message: types.Message, *args, **kwargs):
        if User.get(tg_id=message.from_user.id) is None:
            await message.answer("Доступно после регистрации в боте")
        else:
            await handler(message, *args, **kwargs)

    return wrapper
