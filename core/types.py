from aiogram.types import Message

from database import User


class MessageWithUser(Message):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user: User = User(telegram_id=self.from_user.id, email="", password="")
