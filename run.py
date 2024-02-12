import asyncio
from threading import Thread

from aiogram import executor

from handlers.admin import send_to_all_users
from settngs import dp
from core.gather import gather_manager
import handlers  # инициализация хэндлеров
from core.notifications.task import new_notifications_checker

async def on_startup(dp):
    await send_to_all_users()

# Запускаем бота
if __name__ == "__main__":
    task = Thread(target=gather_manager, daemon=True, name="Собираем данные")
    task.start()

    print("\nImport: ", handlers)

    loop = asyncio.get_event_loop()

    # loop.create_task(new_notifications_checker())
    loop.run_until_complete(on_startup(dp))

    executor.start_polling(dp, skip_updates=True)
