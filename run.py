import asyncio
from aiogram import executor
from handlers.admin import send_to_all_users
from settngs import dp
from core.gather import gather_manager
import handlers  # инициализация хэндлеров
from core.notifications.task import notifications_checker


async def on_startup(dp):
    await send_to_all_users()

#
# # Запускаем бота
# if __name__ == "__main__":
#     task = Thread(target=gather_manager, daemon=True, name="Собираем данные")
#     task.start()
#
#     print("\nImport: ", handlers)
#
#     loop = asyncio.get_event_loop()
#     # loop.run_until_complete(gather_manager())
#     # loop.create_task(new_notifications_checker())
#     loop.run_until_complete(on_startup(dp))
#
#     executor.start_polling(dp, skip_updates=True)


async def main():
    await asyncio.gather(
        on_startup(dp),
        gather_manager(),
        #notifications_checker()
    )

if __name__ == "__main__":
    print("\nImport: ", handlers)
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)
