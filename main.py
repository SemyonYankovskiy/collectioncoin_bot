import logging
from site_calc import authorize, file_opener

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import Database, User

API_TOKEN = "6101263183:AAGuzsxAGNO1PlgxaKKI31NIg_I6kXIxzYo"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database()


# Создаем класс состояний для конечного автомата
class Form(StatesGroup):
    email = State()  # состояние для ввода имени пользователя
    password = State()  # состояние для ввода пароля


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Здарова заебал. Вводи email ")
    await Form.email.set()


# Создаем обработчик сообщений в состоянии name
@dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения и сохраняем его во временном хранилище
    await state.update_data(user_Email=message.text)

    # Отправляем сообщение и переводим пользователя в состояние password
    await message.answer(f"Теперь введи свой пароль.")
    await Form.next()


# Создаем обработчик сообщений в состоянии password
@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    # Получаем пароль пользователя из сообщения и сохраняем его во временном хранилище
    await state.update_data(user_password=message.text)

    # Получаем данные из хранилища и формируем ответ
    hueta = await state.get_data()
    user_email = hueta.get("user_Email")
    user_password = hueta.get("user_password")
    answer = f"Спасибо за регистрацию,теперь введи CVV код."

    # БД

    user1 = User(message.from_user.id, user_email, user_password)
    db.add_user(user1)

    # Отправляем ответ и сбрасываем состояние пользователя
    await message.answer(answer)
    await state.finish()


@dp.message_handler(commands=["summ"])
async def summ(message: types.Message):
    tg_user: User = db.get_user(message.from_user.id)
    if tg_user is None:
        await message.answer(f"ты еблан {message.from_user.full_name}")
        return
    file_name = authorize(tg_user.email, tg_user.password)
    total = file_opener(file_name)

    await message.answer(total)

@dp.message_handler(commands=["delete"])
async def delete(message: types.Message):
    db.delete_user(message.from_user.id)
    await message.answer('уволен')

# Запускаем бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
