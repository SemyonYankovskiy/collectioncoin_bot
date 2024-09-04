from datetime import datetime

from aiogram.dispatcher.filters import Command, Text

from core.name_transformer import transformer
from core.site_calc import countries, strana, func_swap, euro
from helpers.types import MessageWithUser
from handlers.services import send_message_to_user
from helpers.comands import countries_cmd
from helpers.handler_decorators import check_and_set_user
from settngs import dp


@dp.message_handler(Text(equals="Страны"))
@dp.message_handler(commands=["countries"])
@check_and_set_user
async def output_counties(message: MessageWithUser):
    print(datetime.now(), "| ", message.from_user.id, 'commands=["countries"]')

    # обращаемся к функции countries, передаем в эту функциию значение переменной coin_st(значение из 4 столбца массива)
    # функция возвращает массив strani

    try:
        strani = countries(f"./users_files/{message.user.user_coin_id}_.xlsx")
    except Exception as e:
        await send_message_to_user(726837488, f"У пользователя возникла ошибка {e}, в функции вывода стран")
        await message.answer(f"Ой! Обновите базу данных вручную \n/refresh")
        return
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


@check_and_set_user
async def vyvod_monet(message: MessageWithUser, input_list):
    data_length = 0
    output = ""
    output_with_header = ""

    string_without_first_char = message.text[1:]
    text2 = transformer.get_country_rus_name(string_without_first_char)

    for country_name, flag, nominal, year, cena, md, name_for_output, pokupka, kommentariy in input_list:
        # Формирование строки с @pic как кодированного текста
        name = name_for_output
        if name_for_output != "":
            name = f"\n{name_for_output}"
        if md != "":
            md = f"\n{md}"
        if pokupka != "":
            pokupka = f"\n{pokupka}"
        if kommentariy != "":
            kommentariy = f"\n{kommentariy}"

        if message.user.show_pictures == True:
            if name_for_output != "":
                pic_line = f"@pic {country_name} {nominal} {name_for_output}"
            else:
                pic_line = f"@pic {country_name} {nominal} {year}"
            part = f"{flag} {nominal} {year} {cena} {md} {name} {pokupka} {kommentariy}\n`{pic_line}`\n\n"
        else:
            part = f"{flag} {nominal} {year} {cena} {md} {name} {pokupka} {kommentariy}\n\n"

        part_len = len(part)
        data_length += part_len

        if data_length > 4012:
            if "🇪🇺" in flag:
                flag = "🇪🇺"
                text2 = "Евросоюз"
            output_with_header = f"{flag}  {text2}\n----------------------------------------\n" + output
            await send_message_to_user(message.from_user.id, output_with_header)  # Отправляем пользователю output.
            output = part
            data_length = part_len
        else:
            if "🇪🇺" in flag:
                flag = "🇪🇺"
                text2 = "Евросоюз"
            output += part
            output_with_header = f"{flag}  {text2}\n----------------------------------------\n" + output

    await send_message_to_user(message.from_user.id, output_with_header, parse_mode="MARKDOWN")


@dp.message_handler(commands=["europe"])
@check_and_set_user
async def output_eurocoin(message: MessageWithUser):
    print(datetime.now(), "| ", message.from_user.id, 'commands=["europe"]')
    try:
        euro1 = euro(f"./users_files/{message.user.user_coin_id}_.xlsx")
        await vyvod_monet(message, euro1)
    except Exception as e:
        await send_message_to_user(726837488, f"У пользователя возникла ошибка {e}, в функции (output eurocoin)")
        await message.answer(f"Ой! Обновите базу данных вручную \n/refresh")


@dp.message_handler(Command(countries_cmd))
@check_and_set_user
async def output_coin(message: MessageWithUser):
    strani = strana(f"./users_files/{message.user.user_coin_id}_.xlsx", message.text)
    await vyvod_monet(message, strani)


@dp.message_handler(commands=["swap_list"])
@check_and_set_user
async def swap(message: MessageWithUser):
    print(datetime.now(), "| ", message.from_user.id, 'commands=["swap_list"]')

    try:
        swap_list = func_swap(f"./users_files/{message.user.user_coin_id}_SWAP.xlsx")
    except Exception as e:
        await send_message_to_user(726837488, f"У пользователя возникла ошибка {e}, в функции swap")
        await message.answer(f"Ой! Обновите базу данных вручную \n/refresh")
        return

    output = ""
    max_length = 4096

    for country, coins in swap_list.items():
        flag = transformer.get_country_code(country)
        country_header = f"\n{flag} {country}\n--------------------------\n"
        country_data = country_header

        for coin in coins:
            part = f"{flag} {coin[1]} {coin[2]} {coin[3]} {coin[4]} {coin[5]} {coin[6]} {coin[7]}\n\n"
            country_data += part

        if len(output) + len(country_data) > max_length:

            await message.answer(output)  # Send the current accumulated output.
            output = country_data  # Start new output with the current country's data.
        else:
            output += country_data

    if not output:
        await message.answer("Список обмена пуст")
    else:
        await message.answer(output)
