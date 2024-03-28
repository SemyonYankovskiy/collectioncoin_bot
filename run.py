import asyncio
from aiogram import executor
from handlers.admin import send_to_all_users
from handlers.services import send_message_to_user
from settngs import dp
from core.gather import gather_manager, gather_graph_data
import handlers  # инициализация хэндлеров
from core.notifications.task import notifications_checker


async def on_startup(dp):
    # print("Отправляем пользователям сообщение о перезагрузке бота")
    # await send_to_all_users()
    await send_message_to_user(726837488, "ℹ️Бот был перезагружен")
    print("Обновляем данные для пользователей после перезагрузки")
    await gather_graph_data()


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
