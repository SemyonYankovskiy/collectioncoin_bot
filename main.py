import logging
import os
import emoji

from aiogram.dispatcher.filters import Command
from aiogram.types import InputFile
from threading import Thread

from gather import gather_manager
from site_calc import (
    authorize,
    AuthFail,
    get_graph,
    download,
    file_opener,
    more_info,
    countries,
    strana,
    func_swap
)


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


class DeleteForm(StatesGroup):
    confirm_delete = State()  # состояние для ввода имени пользователя
    confirm_delete2 = State()


@dp.message_handler(commands=["start"])
async def hello_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(emoji.emojize(":robot:"))
    await message.answer(f"Здарова, {message.from_user.full_name}")
    await message.answer("⬇️ Доступные команды")


@dp.message_handler(commands=["help"])
async def ua_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(
        "💬 Этот бот берет данные из вашего аккаунта на сайте Ucoin \n/profile, для этого необходимо "
        "зарегистрироваться в"
        "боте /reg \n \n💬 После регистрации бот будет каждый день собирать данные о вашей коллекции,списке обмена\n"
        "/swap_list, "
        "считать суммарную стоимость монет /summ, показывать количество монет по странам /countries,  "
        "а также строить график изменения стоимости монет за последний месяц /grafik\n \n"
        "💬 Вы можете удалить свои данные из бота /delete. При удалении данных стираются также значения стоимости "
        "монет,"
        "график обнуляется \n \n"
        "💬 Если у вас есть монеты, стоимость которых не нужно учитывать, выберите (на сайте Ucoin) для монеты желтую "
        "метку (см.рис. ниже)"
    )

    photo = InputFile("help.png")
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)
    await message.answer("⚙️ Поддержка @M0IIC")
    await message.answer("⬇️ Доступные команды")


@dp.message_handler(commands=["reg"])
async def reg_welcome(message: types.Message):
    if User.get(tg_id=message.from_user.id) is None:
        await message.reply(
            "Фиксирую. Вводи email \n________________________ \nИли жми /EXIT"
        )
        await message.answer(emoji.emojize(":monkey_face:"))
        await Form.email.set()
        return

    await message.reply("Ты уже регистрировался")

    return


# Создаем обработчик сообщений в состоянии name
@dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    # Обработка кнопки EXIT
    if message.text.lower() == "/exit":
        await state.finish()  # Завершаем текущий state
        await message.answer("⬇️ Доступные команды")
        return

    if User.check_email(email=message.text) is None:
        # Получаем имя пользователя из сообщения и сохраняем его во временном хранилище
        await state.update_data(user_Email=message.text)

        # Отправляем сообщение и переводим пользователя в состояние password
        await message.answer(
            f"Теперь введи свой пароль \n________________________ \nИли жми /EXIT"
        )
        await message.answer(emoji.emojize("\U0001F648"))
        await Form.next()
    else:
        await state.finish()  # Завершаем текущий state
        await message.answer("Почта ворованная, пёс")
        return


# Создаем обработчик сообщений в состоянии password
@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    # Получаем пароль пользователя из сообщения и сохраняем его во временном хранилище

    # Обработка кнопки EXIT
    if message.text.lower() == "/exit":
        await state.finish()  # Завершаем текущий state
        await message.answer("⬇️ Доступные команды")
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
        DataCoin.init_new_user(message.from_user.id, total, user_coin_id)

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
    user = User(message.from_user.id, user_email, user_password)
    user.save()
    # await message.answer(emoji.emojize(":handshake:"))
    await message.answer("Регистрация успешна\n" "Данные добавлены в базу")

    await state.finish()


@dp.message_handler(commands=["summ"])
async def summ(message: types.Message):
    if User.get(tg_id=message.from_user.id) is None:
        await message.answer("Доступно после регистрации в боте")
        return

    coin_st = DataCoin.get_for_user(message.from_user.id)
    lot, count = more_info(f"{coin_st[-1][4]}_.xlsx")
    # await message.answer(f"Стоимость всех монет {coin_st[-1][3]} руб.")
    await message.answer(emoji.emojize(":coin:"))
    await message.answer(
        f"Количество монет {lot} \n"
        f"Количество стран {count} \n"
        f"Общая стоимость {coin_st[-1][3]} руб."
    )


@dp.message_handler(commands=["countries"])
async def countries1(message: types.Message):
    if User.get(tg_id=message.from_user.id) is None:
        await message.answer("Доступно после регистрации в боте")
        return
    coin_st = DataCoin.get_for_user(message.from_user.id)
    strani = countries(f"{coin_st[-1][4]}_.xlsx")
    await message.answer("Кол-во монет | Страна")
    await message.answer(strani)


@dp.message_handler(
    Command(
        [
            "Australia",
            "Austria",
            "Azerbaijan",
            "Albania",
            "Algeria",
            "American_Samoa",
            "Anguilla",
            "Angola",
            "Andorra",
            "Antarctica",
            "Antigua_and_Barbuda",
            "Argentina",
            "Armenia",
            "Aruba",
            "Afghanistan",
            "Bahamas",
            "Bangladesh",
            "Barbados",
            "Bahrain",
            "Belarus",
            "Belize",
            "Belgium",
            "Benin",
            "Bermuda",
            "Bulgaria",
            "Bolivia",
            "Bonaire",
            "Bosnia_and_Herzegovina",
            "Botswana",
            "Brazil",
            "British Indian Ocean Territory",
            "Brunei",
            "Burkina_Faso",
            "Burundi",
            "Bhutan",
            "Vanuatu",
            "Hungary",
            "Venezuela",
            "Virgin Islands_British",
            "Virgin_Islands",
            "Vietnam",
            "Gabon",
            "Haiti",
            "Guyana",
            "Gambia",
            "Ghana",
            "Guadeloupe",
            "Guatemala",
            "Guinea",
            "Guinea_Bissau",
            "Germany",
            "Guernsey",
            "Gibraltar",
            "Honduras",
            "Hong_Kong",
            "Grenada",
            "Greenland",
            "Greece",
            "Georgia",
            "Guam",
            "Denmark",
            "Jersey",
            "Djibouti",
            "Dominica",
            "Dominican_Republic",
            "Egypt",
            "Zambia",
            "Western_Sahara",
            "Zimbabwe",
            "Israel",
            "India",
            "Indonesia",
            "Jordan",
            "Iraq",
            "Iran",
            "Ireland",
            "Iceland",
            "Spain",
            "Italy",
            "Yemen",
            "Cape Verde",
            "Kazakhstan",
            "Cambodia",
            "Cameroon",
            "Canada",
            "Qatar",
            "Kenya",
            "Cyprus",
            "Kyrgyzstan",
            "Kiribati",
            "China",
            "Cocos (Keeling) Islands",
            "Colombia",
            "Comoros",
            "Congo",
            "Congo_democratic",
            "KNDR",
            "Korea",
            "Costa_Rica",
            "Cote_dIvoire",
            "Cuba",
            "Kuwait",
            "Curacao",
            "LaoS",
            "Latvia",
            "Lesotho",
            "Lebanon",
            "Libya",
            "Liberia",
            "Liechtenstein",
            "Lithuania",
            "Luxembourg",
            "Mauritius",
            "Mauritania",
            "Madagascar",
            "Mayotte",
            "Macao",
            "Malawi",
            "Malaysia",
            "Mali",
            "United States Minor Outlying Islands",
            "Maldives",
            "Malta",
            "Morocco",
            "Martinique",
            "Marshall Islands",
            "Mexico",
            "Micronesia",
            "Mozambique",
            "Moldova",
            "Monaco",
            "Mongolia",
            "Montserrat",
            "Burma",
            "Namibia",
            "Nauru",
            "Nepal",
            "Niger",
            "Nigeria",
            "Netherlands",
            "Nicaragua",
            "Niue",
            "New_Zealand",
            "New_Caledonia",
            "Norway",
            "United_Arab_Emirates",
            "Oman",
            "Bouvet_Island",
            "Isle_of_Man",
            "Norfolk_Island",
            "Christmas_Island",
            "Heard_Island_and_McDonald_Islands",
            "Cayman_Islands",
            "Cook_Islands",
            "Turks_and_Caicos_Islands",
            "Pakistan",
            "Palau",
            "Palestinian",
            "Panama",
            "Vatican",
            "Papua_New_Guinea",
            "Paraguay",
            "Peru",
            "Pitcairn",
            "Poland",
            "Portugal",
            "Puerto_Rico",
            "Macedonia",
            "Reunion",
            "Russia",
            "Rwanda",
            "Romania",
            "Samoa",
            "San_Marino",
            "Sao_Tome_and_Principe",
            "Saudi_Arabia",
            "Saint Helena, Ascension And Tristan Da Cunha",
            "Northern_Mariana_Islands",
            "Saint_Barthelemy",
            "Saint_Martin",
            "Senegal",
            "Saint_Vincent_and_the_Grenadines",
            "Saint_Kitts_and_Nevis",
            "Saint_Lucia",
            "Saint_Pierre_and_Miquelon",
            "Serbia",
            "Seychelles",
            "Singapore",
            "Sint_Maarten",
            "Syrian",
            "Slovakia",
            "Slovenia",
            "GB",
            "USA",
            "Solomon_Islands",
            "Somalia",
            "Sudan",
            "Suriname",
            "Sierra Leone",
            "Tajikistan",
            "Thailand",
            "Taiwan",
            "Tanzania",
            "Timor-Leste",
            "Togo",
            "Tokelau",
            "Tonga",
            "Trinidad_and_Tobago",
            "Tuvalu",
            "Tunisia",
            "Turkmenistan",
            "Turkey",
            "Uganda",
            "Uzbekistan",
            "Ukraine",
            "Wallis_and_Futuna",
            "Uruguay",
            "Faroe_Islands",
            "Fiji",
            "Philippines",
            "Finland",
            "Falkland_Islands",
            "France",
            "French_Guiana",
            "French_Polynesia",
            "French_Southern_Territories",
            "Croatia",
            "CAR",
            "Chad",
            "Montenegro",
            "Czech",
            "Chile",
            "Switzerland",
            "Sweden",
            "Svalbard",
            "Sri_Lanka",
            "Ecuador",
            "Equatorial_Guinea",
            "Aland_Islands",
            "El_Salvador",
            "Eritrea",
            "Eswatini",
            "Estonia",
            "Ethiopia",
            "South_Africa",
            "South Georgia and the South Sandwich Islands",
            "South_Ossetia",
            "South_Sudan",
            "Jamaica",
            "Japan",
            "Caribean",
            "GDR",
            "Nazi",
            "Afrika",
            "Crimea",
            "Nid_Antilla",
            "Russian_Empire",
            "USSR",
            "France_Afar",
            "Chehoclovakia",
            "Jyugoslavia",
        ]
    )
)
async def countries2(message: types.Message):
    if User.get(tg_id=message.from_user.id) is None:
        await message.answer("Доступно после регистрации в боте")
        return
    coin_st = DataCoin.get_for_user(message.from_user.id)

    australia = strana(f"{coin_st[-1][4]}_.xlsx", message.text)
    # array = [[" " if x is None else x for x in row] for row in australia]
    array_str = "\n\n".join(["  ".join(map(str, row)) for row in australia])
    # array_str = "\n\n".join(["  ".join(["{:<8}".format(element) for element in row]) for row in array])

    # Replace None with space using list comprehension

    if len(array_str) > 4096:
        for x in range(0, len(array_str), 4007):
            await message.answer(array_str[x: x + 4007])
    else:
        await message.answer(array_str)


@dp.message_handler(commands=["swap_list"])
async def swap(message: types.Message):
    if User.get(tg_id=message.from_user.id) is None:
        await message.answer("Доступно после регистрации в боте")
        return
    coin_st = DataCoin.get_for_user(message.from_user.id)
    swap_list = func_swap(f"{coin_st[-1][4]}_SWAP.xlsx")
    array_str = "\n\n".join(["  ".join(map(str, row)) for row in swap_list])
    if len(array_str) > 4096:
        for x in range(0, len(array_str), 4045):
            await message.answer(array_str[x: x + 4045])
    else:
        await message.answer(array_str)



@dp.message_handler(commands=["profile"])
async def profile(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    coin_st = DataCoin.get_for_user(message.from_user.id)

    await message.answer(
        f'<a href="https://ru.ucoin.net/uid{coin_st[-1][4]}?v=home">Я ссылка, ЖМИ!</a>',
        parse_mode="HTML",
    )


@dp.message_handler(commands=["grafik"])
async def grafik(message: types.Message):
    if User.get(tg_id=message.from_user.id) is None:
        await message.answer("Доступно после регистрации в боте")
        return
    graph_name = get_graph(message.from_user.id)
    photo = InputFile(graph_name)
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)
    os.remove(graph_name)


@dp.message_handler(commands=["delete"])
async def delete1(message: types.Message):
    if User.get(tg_id=message.from_user.id) is None:
        await message.answer("Доступно после регистрации в боте")
        return
    await DeleteForm.confirm_delete.set()
    await message.answer("Точно удалить? \nпиши   да   или   нет")


@dp.message_handler(state=DeleteForm.confirm_delete)
async def delete2(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        await DeleteForm.confirm_delete2.set()
        await message.answer("Последний раз спрашиваю \nпиши   да   или   нет")
    else:
        await message.answer("Ну и всё, больше так не делай")

        await state.finish()  # Завершаем текущий state


@dp.message_handler(state=DeleteForm.confirm_delete2)
async def delete2(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        User.delete(tg_id=message.from_user.id)
        DataCoin.delete_user_data(tg_id=message.from_user.id)
        await message.answer(
            "Данные удалены из базы данных бота \n↓↓↓ Доступные команды"
        )

    else:
        await message.answer("Ну и нахуй ты мне мозгу ебешь, кожаный мешок")

    await state.finish()  # Завершаем текущий state


@dp.message_handler()
async def unknown(message: types.Message):
    await message.answer("Сложно непонятно говоришь")
    await message.answer("⬇️ Доступные команды")


# Запускаем бота
if __name__ == "__main__":
    task = Thread(target=gather_manager, daemon=True, name="Собираем данные")
    task.start()

    executor.start_polling(dp, skip_updates=True)
