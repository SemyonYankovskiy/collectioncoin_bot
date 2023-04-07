import logging
import os
from aiogram.types import InputFile

from threading import Thread

from gather import gather_manager
from site_calc import authorize, AuthFail, get_graph, download, file_opener


from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import Database, User, DataCoin

API_TOKEN = "6101263183:AAGuzsxAGNO1PlgxaKKI31NIg_I6kXIxzYo"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

Database.create_tables()


# Создаем класс состояний для конечного автомата
class Form(StatesGroup):
    email = State()  # состояние для ввода имени пользователя
    password = State()  # состояние для ввода пароля


@dp.message_handler(commands=["start"])
async def hello_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(
        f"Здарова заебал, {message.from_user.full_name} \n↓↓↓ Чекай доступные команды"
    )


@dp.message_handler(commands=["ua"])
async def ua_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(
        f"Мужики не шмаляйте я кабан! \n \n"
        f"⠀⠀⠀⠀⠀⠀⠀⣴⣶⣦⣤⣴⣶⣶⣿⣿⣿⣿⣷⣶⣦⣤⣄⣀⡀⠀⠀⠀⣀⡀ "
        f"⠀⠀⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⡋⠀⠀ "
        f"⠀⠀⣠⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀ "
        f"⠙⠟⠛⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀ "
        f"⠀⠀⠀⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⡀ "
        f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⣶⡿⢿⡿⠿⠿⠂⠀⠉⠉⠉⠀⣀⣿⡿⠟⠛⠿⠻⠇ "
        f"⠀⠀⠀⠀⠀⠀⠀⢀⣰⠟⠀⠀⠈⠛⠳⠀⠀⠀⠀⠀⢠⡾⠋⠀⠀⠀⠀"
    )


@dp.message_handler(commands=["reg"])
async def reg_welcome(message: types.Message):
    if User.get(tg_id=message.from_user.id) is None:
        await message.reply(
            "Фиксирую. Вводи email \n________________________ \nИли жми /EXIT"
        )
        await Form.email.set()
        return

    await message.reply("Ты уже регистрировался")
    await message.answer(f"↓↓↓ Чекай доступные команды")
    return


# Создаем обработчик сообщений в состоянии name
@dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    # Обработка кнопки EXIT
    if message.text.lower() == "/exit":
        await state.finish()  # Завершаем текущий state
        await message.answer(f"↓↓↓ Чекай доступные команды")
        return

    # Получаем имя пользователя из сообщения и сохраняем его во временном хранилище
    await state.update_data(user_Email=message.text)

    # Отправляем сообщение и переводим пользователя в состояние password
    await message.answer(
        f"Теперь введи свой пароль \n________________________ \nИли жми /EXIT"
    )

    await Form.next()


# Создаем обработчик сообщений в состоянии password
@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    # Получаем пароль пользователя из сообщения и сохраняем его во временном хранилище

    # Обработка кнопки EXIT
    if message.text.lower() == "/exit":
        await state.finish()  # Завершаем текущий state
        await message.answer(f"↓↓↓ Чекай доступные команды")
        return

    await state.update_data(user_password=message.text)

    # Получаем данные из хранилища и формируем ответ
    hueta = await state.get_data()
    user_email = hueta.get("user_Email")
    user_password = hueta.get("user_password")

    try:
        # Пытаемся по введенным данным от пользователя зайти на сайт
        user_coin_id, session = authorize(user_email, user_password)
        file_name = download(user_coin_id, session)
        total = file_opener(file_name)
        DataCoin.init_new_user(message.from_user.id, total)



    # Перехватываем ошибку
    except AuthFail:
        # Если данные неверные, то просим его ввести их снова
        await Form.email.set()  # Заново будем запрашивать email
        await message.answer(
            f"Ты чё бухой блять? \nИди нахуй, {message.from_user.full_name} "
            f"\nЯ жду от тебя нормальный email \n________________________ \nИли жми /EXIT"
        )

        return  # Выходим из данной функции

    # Если данные были верные, то записываем в базу пользователя
    user = User(message.from_user.id, user_email, user_password)
    user.save()

    await message.answer(
        "Спасибо за регистрацию, ищи себя в прошмандовках севтелекома."
    )

    await message.answer(f"↓↓↓ Чекай доступные команды")
    await state.finish()


@dp.message_handler(commands=["summ"])
async def summ(message: types.Message):
    coin_st = DataCoin.get_for_user(message.from_user.id)
    await message.answer(f"Стоимость всех монет {coin_st[-1][3]}")


@dp.message_handler(commands=["grafik"])
async def grafik(message: types.Message):
    graph_name = get_graph(message.from_user.id)
    photo = InputFile(graph_name)
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)
    os.remove(graph_name)

@dp.message_handler(commands=["delete"])
async def delete(message: types.Message):
    User.delete(tg_id=message.from_user.id)
    await message.answer("уволен \n↓↓↓ Чекай доступные команды")


# Запускаем бота
if __name__ == "__main__":
    task = Thread(target=gather_manager, daemon=True, name="Собираем данные")
    task.start()

    executor.start_polling(dp, skip_updates=True)
