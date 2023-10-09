import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from database import db_connection


API_TOKEN = "6180484344:AAGyBQJEtOZ1ZRU4GrRj08olO6oynDnAfD0"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Создаем таблицы в базе данных
db_connection.create_tables()

path = os.path.join(os.getcwd(), "users_files")
try:
    os.mkdir(path)
    print("Directory created successfully")
except OSError as error:
    print("Check user_files directory - Done")
