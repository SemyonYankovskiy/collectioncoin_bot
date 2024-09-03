import random
import re
from datetime import datetime

import emoji
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageToDeleteNotFound
from bs4 import BeautifulSoup

from core.site_calc import authorize, AuthFail, download, file_opener, parsing
from core.types import MessageWithUser
from database import User, DataCoin
from helpers.handler_decorators import check_and_set_user
from settngs import dp, bot


def get_user_profile_keyboard():
    keyboard = InlineKeyboardMarkup()

    # Первая кнопка для изменения цветовой схемы
    button_color_scheme = InlineKeyboardButton(
        "Изменить цветовую схему для карты",
        callback_data="choose_color_map_scheme"
    )

    # Вторая кнопка, при нажатии на которую будет отображаться уведомление
    button_notify = InlineKeyboardButton(
        "Показ изображений вкл|выкл",
        callback_data="show_pictures"
    )

    # Добавляем кнопки в клавиатуру
    keyboard.add(button_color_scheme)
    keyboard.add(button_notify)

    return keyboard



@dp.message_handler(commands=["profile"])
@check_and_set_user
async def profile(message: MessageWithUser):
    print(datetime.now(), "| ", message.from_user.id, 'commands=["profile"]')

    user = User.get(message.from_user.id)
    message_status = f"✉️" if user.new_messages == 0 else f"📩"
    swap_status = f"❕" if user.new_swap == 0 else f"❗️"
    last_refresh = user.last_refresh

    # user_coin_id, session = authorize(user.email, user.password)
    # parsing(session, user, user_coin_id)

    keyboard = get_user_profile_keyboard()
    await message.answer(
        f'<a href="https://ru.ucoin.net/uid{message.user.user_coin_id}?v=home">👤 Профиль</a>\n'
        f"{message_status} Новые сообщения {user.new_messages} \n{swap_status} Предложения обмена {user.new_swap}"
        f"\n🕓 Последнее обновление: {last_refresh}"
        f"\n_____________________________\n📨 Обновить: /whats_new",
        parse_mode="HTML",
        reply_markup=keyboard,
    )

@dp.message_handler(commands=["whats_new"])
@check_and_set_user
async def whats_new(message: MessageWithUser):
    print(datetime.now(), "| ", message.from_user.id, 'commands=["whats_new"]')

    user = User.get(message.from_user.id)
    user_coin_id, session = authorize(user.email, user.password)
    parsing(session, user, user_coin_id)

    # Удаляем предпоследнее сообщение
    chat_id = message.chat.id
    message_id = message.message_id

    try:
        # Удаляем сообщение с id на единицу меньше текущего
        await bot.delete_message(chat_id, message_id - 1)
        await bot.delete_message(chat_id, message_id)
    except MessageToDeleteNotFound:
        pass  # Сообщение уже удалено или не существует

    await profile(message)

# Создаем класс состояний для конечного автомата
class Form(StatesGroup):
    email = State()  # состояние для ввода имени пользователя
    password = State()  # состояние для ввода пароля


@dp.message_handler(commands=["reg"])
async def reg_welcome(message: MessageWithUser):
    print(datetime.now(), "| ",  message.from_user.id, 'commands=["reg"]')
    # Проверка пользователя в БД, чтобы исключить регистрацию с 1 аккаунта телеграм, если всё ок, устанавливаем
    # конечный автомат в состояние email, чтобы попасть в функцию process_email
    if User.get(tg_id=message.from_user.id) is None:
        await message.answer("Фиксирую. Вводи email \n________________________ \nИли жми /EXIT")
        await message.answer(emoji.emojize(":monkey_face:"))
        await Form.email.set()
        return
    else:
        await message.answer("Ты уже регистрировался")
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

        HEADERS = [
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.43 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 OPR/106.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.43 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 OPR/106.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.43 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 OPR/106.0.0.0",
        ]

        response = session.get(
            url=f"https://ru.ucoin.net/uid{user_coin_id}?v=home",
            headers={"user-agent": random.choice(HEADERS)},
        )
        if response.status_code != 200:
            raise AuthFail(f"Получили ответ от сервера {response.status_code}")
    # Перехватываем ошибку
    except AuthFail as e:
        # Если данные неверные, то просим его ввести их снова
        await Form.email.set()  # Заново будем запрашивать email
        await message.answer(
            f"Ошибка {e} \n"
            f"Возможно неправильный email или пароль \n")
        await message.answer(
            f"Повторная попытка регистрации \n"
            f"\nВведите email \n________________________ \nИли нажмите /EXIT"
        )
        return
    else:
        # если всё ок - собираем данные
        file_name = download(user_coin_id, session)
        total, total_count = file_opener(file_name)
        DataCoin.init_new_user(message.from_user.id, total, total_count)

        soup = BeautifulSoup(response.content, "html.parser")
        name = str(soup.find_all("div", {"class": "name-block"}))
        pattern = r'<h1 class="wrap left">(.*?)</h1>'
        user_name = str(re.search(pattern, name).group(1))
        user_name = user_name.replace(' ', '_')

    # Если данные были верные, то записываем в базу пользователя
    user = User(
        telegram_id=message.from_user.id,
        email=user_email,
        password=user_password,
        user_coin_id=user_coin_id,
        user_name=user_name,
    )
    user.save()

    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer("Регистрация успешна\n" "Данные добавлены в базу")
    # сбрасываем состояние автомата
    await state.finish()


class DeleteForm(StatesGroup):
    confirm_delete = State()  # 1 состояние для удаления данных из бота
    confirm_delete2 = State()  # 2 состояние для удаления данных из бота


@dp.message_handler(commands=["delete"])
@check_and_set_user
async def delete1(message: MessageWithUser):
    print(datetime.now(), "| ",  message.from_user.id, 'commands=["delete"]')

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
async def delete3(message: MessageWithUser, state: FSMContext):
    if message.text.lower() == "да":
        User.delete(tg_id=message.from_user.id)
        DataCoin.delete_user_data(tg_id=message.from_user.id)
        await message.answer("Данные удалены из базы данных бота \n↓↓↓ Доступные команды")

    else:
        await message.answer("Ну и нахуй ты мне мозгу ебешь, кожаный мешок")

    await state.finish()  # Завершаем текущий state
