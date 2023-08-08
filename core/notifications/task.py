import asyncio

from database import User
from handlers.services import send_text_to_user
from .cache import storage
from ..site_calc import authorize, parsing


async def check_user_notifications(user: User):
    print(f"check user ({user.email}) notifications")

    old_messages = storage.get_data(user.telegram_id, "new_messages") or 0
    old_swap_messages = storage.get_data(user.telegram_id, "swap_messages") or 0

    if old_messages < user.new_messages:
        new_messages = user.new_messages - old_messages
        await send_text_to_user(user, f"У вас ({new_messages}) новых сообщений")
        storage.set_data(user.telegram_id, "new_messages", user.new_messages)

    if old_swap_messages < user.new_swap:
        new_swap = user.new_swap - old_swap_messages
        await send_text_to_user(user, f"У вас ({new_swap}) новых предложений обмена")
        storage.set_data(user.telegram_id, "swap_messages", user.new_swap)


async def new_notifications_checker():
    print("Start notifications checker")
    while True:
        users_list = User.get_all()
        for user in users_list:
            user_coin_id, session = authorize(user.email, user.password)
            parsing(session, user, user_coin_id)
            await check_user_notifications(user)

        await asyncio.sleep(60 * 10)
