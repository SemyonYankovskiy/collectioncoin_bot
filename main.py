import os
import logging
from threading import Thread

import emoji
from aiogram.dispatcher.filters import Command
from aiogram.types import InputFile
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from core.gather import gather_manager
from core.site_calc import (
    authorize,
    AuthFail,
    get_graph,
    download,
    file_opener,
    more_info,
    countries,
    strana,
    func_swap,
    euro,
    refresh,
)
from core.map import WorldMap
from core.types import MessageWithUser
from database import db_connection, User, DataCoin
from helpers.handler_decorators import check_and_set_user
from helpers.comands import countries_cmd
from helpers.limiter import rate_limit


API_TOKEN = os.getenv("TG_TOKEN")

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
    print("Directory already exist")


# Создаем класс состояний для конечного автомата
class Form(StatesGroup):
    email = State()  # состояние для ввода имени пользователя
    password = State()  # состояние для ввода пароля


class DeleteForm(StatesGroup):
    confirm_delete = State()  # 1 состояние для удаления данных из бота
    confirm_delete2 = State()  # 2 состояние для удаления данных из бота


@dp.message_handler(commands=["start"])
async def hello_welcome(message: MessageWithUser):
    await message.answer(emoji.emojize(":robot:"))
    await message.answer(f"Здарова, {message.from_user.full_name}")
    await message.answer("⬇️ Доступные команды")


# Временная функция принудительного обновления
@dp.message_handler(commands=["refresh"])
@check_and_set_user
@rate_limit(600)
async def refresh_data(message: MessageWithUser):
    await bot.send_chat_action(chat_id=message.from_id, action="find_location")

    refresh(message.from_user.id)
    await message.answer("База данных успешно обновлена")


@dp.message_handler(commands=["help"])
async def ua_welcome(message: MessageWithUser):
    await message.answer(
        "💬 Этот бот берет данные из вашего аккаунта на сайте Ucoin \n/profile, для этого необходимо "
        "зарегистрироваться в "
        "боте /reg \n \n💬 После регистрации бот будет каждый день собирать данные о вашей коллекции,списке обмена\n"
        "/swap_list, "
        "считать суммарную стоимость монет /summ, показывать количество монет по странам /countries,"
        " рисовать карту мира /map "
        "а также строить график изменения стоимости монет за последний месяц /grafik\n \n"
        "💬 Вы можете удалить свои данные из бота /delete. При удалении данных стираются также значения стоимости "
        "монет,"
        "график обнуляется \n \n"
        "💬 Если у вас есть монеты, стоимость которых не нужно учитывать, выберите (на сайте Ucoin) для монеты желтую "
        "метку (см.рис. ниже)"
    )
    await bot.send_photo(chat_id=message.from_user.id, photo=InputFile("img/help.png"))
    await message.answer("⚙️ Поддержка @M0IIC")
    await message.answer("⬇️ Доступные команды")


@dp.message_handler(commands=["reg"])
async def reg_welcome(message: MessageWithUser):
    # Проверка пользователя в БД, чтобы исключить регистрацию с 1 аккаунта телеграм, если всё ок, устанавливаем
    # конечный автомат в состояние email чтобы попасть в функцию process_email
    if User.get(tg_id=message.from_user.id) is None:
        await message.reply("Фиксирую. Вводи email \n________________________ \nИли жми /EXIT")
        await message.answer(emoji.emojize(":monkey_face:"))
        await Form.email.set()
        return
    else:
        await message.reply("Ты уже регистрировался")
        return


# Создаем обработчик сообщений в состоянии email
@dp.message_handler(state=Form.email)
async def process_email(message: MessageWithUser, state: FSMContext):
    # Обработка кнопки EXIT
    if message.text.lower() == "/exit":
        await state.finish()  # Завершаем текущий state
        await message.answer("⬇️ Доступные команды")
        return
    # Проверка пользователя в БД, чтобы исключить регистрацию такой же почты, если совпадения нет, то переводим
    # конечный автомат в следующее состояние password
    if User.has_user_with_email(email=message.text):
        await state.finish()  # Сбрасываем состояние конечного автомата
        await message.answer("Почта ворованная, пёс")
    else:
        # Получаем имя пользователя из сообщения и сохраняем его во временном хранилище
        await state.update_data(user_Email=message.text)
        # Отправляем сообщение и переводим пользователя в состояние password
        await message.answer(f"Теперь введи свой пароль \n________________________ \nИли жми /EXIT")
        await message.answer(emoji.emojize("\U0001F648"))
        await Form.next()


# Создаем обработчик сообщений в состоянии password
@dp.message_handler(state=Form.password)
async def process_password(message: MessageWithUser, state: FSMContext):
    # Обработка кнопки EXIT
    if message.text.lower() == "/exit":
        await state.finish()  # Завершаем текущий state
        await message.answer("⬇️ Доступные команды")
        return

    # Получаем пароль пользователя из сообщения и сохраняем его во временном хранилище
    await state.update_data(user_password=message.text)

    # Получаем данные из хранилища и формируем ответ
    temp = await state.get_data()
    user_email = temp.get("user_Email")
    user_password = temp.get("user_password")

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
            f"Неправильный email или пароль \n"
            f"\nВведи правильный email \n________________________ \nИли жми /EXIT"
        )

        return  # Выходим из данной функции

    # Если данные были верные, то записываем в базу пользователя
    user = User(
        telegram_id=message.from_user.id,
        email=user_email,
        password=user_password,
        user_coin_id=user_coin_id,
    )
    user.save()

    await bot.delete_message(message.from_user.id, message.message_id)

    await message.answer("Регистрация успешна\n" "Данные добавлены в базу")
    # сбрасываем состояние автомата
    await state.finish()


@dp.message_handler(commands=["summ"])
@check_and_set_user
async def summ(message: MessageWithUser):
    coin_st = DataCoin.get_for_user(message.from_user.id)
    # обращаемся к функции more info, передаем в эту функциию значение переменной (значение из 4 столбца массива)
    lot, count = more_info(f"./users_files/{message.user.user_coin_id}_.xlsx")

    await message.answer(emoji.emojize(":coin:"))
    await message.answer(
        f"Количество монет {lot} \n"
        f"Количество стран {count} \n"
        f"Общая стоимость {coin_st[-1].totla_sum} руб."
    )


@dp.message_handler(commands=["countries"])
@check_and_set_user
async def output_counties(message: MessageWithUser):
    # обращаемся к функции countries, передаем в эту функциию значение переменной coin_st(значение из 4 столбца массива)
    # функция возвращает массив strani
    strani = countries(f"./users_files/{message.user.user_coin_id}_.xlsx")

    # Условие построчного переноса, при превышении длинны сообщения более 4096 символов
    data_length = 0
    output = ""
    # Записываем элементы массива как строку
    for flag, count, name, cmd in strani:
        part = f"{flag} {count:<5}{name}\n           /{cmd}\n"
        # определяем длинну строки
        part_len = len(part)
        # суммируем длинны всех строк
        data_length += part_len
        # при превышении длинны всех строк больше чем 4096 символов
        if data_length > 4096:
            await message.answer(output)  # Отправляем пользователю output, на данный момент
            output = part
            data_length = part_len
        else:
            output += part
    await message.answer(output)


async def vyvod_monet(message: MessageWithUser, input_list):
    data_length = 0
    output = ""
    for flag, nominal, year, cena, md, name in input_list:
        part = f"{flag} {nominal} {year} {cena} {md} {name}\n\n"
        part_len = len(part)
        data_length += part_len
        if data_length > 4096:
            await message.answer(output)  # Отправляем пользователю output.
            output = part
            data_length = part_len
        else:
            output += part
    await message.answer(output)


@dp.message_handler(commands=["europe"])
@check_and_set_user
async def output_eurocoin(message: MessageWithUser):
    euro1 = euro(f"./users_files/{message.user.user_coin_id}_.xlsx")
    await vyvod_monet(message, euro1)


@dp.message_handler(Command(countries_cmd))
@check_and_set_user
async def output_coin(message: MessageWithUser):
    strani = strana(f"./users_files/{message.user.user_coin_id}_.xlsx", message.text)
    await vyvod_monet(message, strani)


@dp.message_handler(commands=["swap_list"])
@check_and_set_user
async def swap(message: MessageWithUser):
    swap_list = func_swap(f"./users_files/{message.user.user_coin_id}_SWAP.xlsx")
    data_length = 0
    output = ""

    for flag, nominal, year, cena, count, md, name, comment in swap_list:
        part = f"{flag} {nominal} {year} {cena} {count} {md} {name} {comment} \n\n"
        part_len = len(part)
        data_length += part_len
        if data_length > 4096:
            await message.answer(output)  # Отправляем пользователю output.
            output = part
            data_length = part_len
        else:
            output += part
    if not output:
        await message.answer("Список обмена пуст")
    else:
        await message.answer(output)


@dp.message_handler(commands=["profile"])
@check_and_set_user
async def profile(message: MessageWithUser):
    user = User.get(message.from_user.id)
    message_status = f"✉️" if user.new_messages == 0 else f"📩"
    swap_status = f"❕" if user.new_swap == 0 else f"❗️"
    await message.answer(
        f'<a href="https://ru.ucoin.net/uid{message.user.user_coin_id}?v=home">👤 Профиль</a>\n'
        f"{message_status} Новые сообщения {user.new_messages} \n{swap_status} Предложения обмена {user.new_swap}",
        parse_mode="HTML",
    )


@dp.message_handler(commands=["grafik"])
@check_and_set_user
async def grafik(message: MessageWithUser):
    await bot.send_chat_action(chat_id=message.from_id, action="upload_photo")

    graph_name = get_graph(message.from_user.id)
    photo = InputFile(graph_name)
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)
    os.remove(graph_name)


def get_maps_keyboards(current_location: str):
    world_locations = [
        ("Мир", "World"),
        ("Европа", "Europe"),
        ("Ц.Америка", "North_America"),
        ("Ю.Америка", "South_America"),
        ("Азия", "Asia"),
        ("Африка", "Africa"),
        ("Острова Азии", "Asian_Islands"),
    ]
    keyboard = []

    for name, callback_data in world_locations:
        if callback_data != current_location:
            keyboard.append(InlineKeyboardButton(name, callback_data=callback_data))

    return InlineKeyboardMarkup().add(*keyboard)


async def get_user_map(location: str, user: User, delete_last_message_id=None):
    await bot.send_chat_action(chat_id=user.telegram_id, action="upload_photo")

    world_map = WorldMap(user_coin_id=user.user_coin_id)
    map_name = world_map.create_map(location=location)

    keyboard = get_maps_keyboards(current_location=location)

    map_img = InputFile(map_name)

    if delete_last_message_id:
        await bot.delete_message(chat_id=user.telegram_id, message_id=delete_last_message_id)
    await bot.send_photo(chat_id=user.telegram_id, photo=map_img, reply_markup=keyboard)
    os.remove(map_name)


@dp.message_handler(commands=["map"])
@check_and_set_user
async def maps(message: MessageWithUser):
    location = "World"
    await get_user_map(location, message.user)


@dp.callback_query_handler(
    lambda c: c.data == "World"
    or c.data == "Europe"
    or c.data == "North_America"
    or c.data == "South_America"
    or c.data == "Asia"
    or c.data == "Africa"
    or c.data == "Asian_Islands"
)
@check_and_set_user
async def process_callback_button1(callback_query: types.CallbackQuery):
    location = callback_query.data
    user = User.get(tg_id=callback_query.from_user.id)
    await get_user_map(location, user, delete_last_message_id=callback_query.message.message_id)


@dp.message_handler(commands=["delete"])
@check_and_set_user
async def delete1(message: MessageWithUser):
    await DeleteForm.confirm_delete.set()
    await message.answer(
        "При удалении данных стираются также значения стоимости монет, график обнуляется"
    )
    await message.answer("Точно удалить? \nпиши   да   или   нет")


@dp.message_handler(state=DeleteForm.confirm_delete)
@check_and_set_user
async def delete2(message: MessageWithUser, state: FSMContext):
    if message.text.lower() == "да":
        await DeleteForm.confirm_delete2.set()
        await message.answer("Последний раз спрашиваю \nпиши   да   или   нет")

    else:
        await message.answer("Ну и всё, больше так не делай")

        await state.finish()  # Завершаем текущий state


@dp.message_handler(state=DeleteForm.confirm_delete2)
@check_and_set_user
async def delete2(message: MessageWithUser, state: FSMContext):
    if message.text.lower() == "да":
        User.delete(tg_id=message.from_user.id)
        DataCoin.delete_user_data(tg_id=message.from_user.id)
        await message.answer("Данные удалены из базы данных бота \n↓↓↓ Доступные команды")

    else:
        await message.answer("Ну и нахуй ты мне мозгу ебешь, кожаный мешок")

    await state.finish()  # Завершаем текущий state


@dp.message_handler(commands=["all"])
@check_and_set_user
async def all_(message: MessageWithUser):
    await refresh_data(message)
    await profile(message)
    await summ(message)
    await grafik(message)
    await maps(message)


@dp.message_handler()
async def unknown(message: MessageWithUser):
    await message.answer("Сложно непонятно говоришь")
    await message.answer("⬇️ Доступные команды")


# Запускаем бота
if __name__ == "__main__":
    task = Thread(target=gather_manager, daemon=True, name="Собираем данные")
    task.start()

    executor.start_polling(dp, skip_updates=True)
