from threading import Thread

from aiogram import executor

from settngs import dp
from core.gather import gather_manager
import handlers  # инициализация хэндлеров


# Запускаем бота
if __name__ == "__main__":
    task = Thread(target=gather_manager, daemon=True, name="Собираем данные")
    task.start()
    print("\nImport: ", handlers)
    executor.start_polling(dp, skip_updates=True)
