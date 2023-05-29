from functools import wraps
from typing import Callable

from aiogram import types

from database import User


def check_and_set_user(handler: Callable):
    @wraps(handler)
    async def wrapper(obj: types.Message, *args, **kwargs):
        user = User.get(tg_id=obj.from_user.id)
        if user is None:
            await obj.answer("Доступно после регистрации в боте")
        else:
            obj.user = user
            await handler(obj, *args, **kwargs)

    return wrapper
