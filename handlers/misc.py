from datetime import datetime

import emoji
from aiogram import types
from aiogram.types import InputFile

from core.types import MessageWithUser
from settngs import dp, bot


@dp.message_handler(commands=["start"])
async def hello_welcome(message: MessageWithUser):
    print(datetime.now(),"| ",  message.from_user.id, 'commands=["start"]')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Страны", "Карта"]
    keyboard.add(*buttons)
    button_1 = types.KeyboardButton(text="График")
    keyboard.add(button_1)
    await message.answer(emoji.emojize(":robot:"))
    await message.answer(f"Здарова, {message.from_user.full_name}", reply_markup=keyboard)
    await message.answer("⬇️ Доступные команды")


@dp.message_handler(commands=["help"])
async def ua_welcome(message: MessageWithUser):
    print(datetime.now(),"| ",  message.from_user.id, 'commands=["help"]')

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


@dp.message_handler()
async def unknown(message: MessageWithUser):
    await message.answer("Сложно непонятно говоришь")
    await message.answer("⬇️ Доступные команды")
