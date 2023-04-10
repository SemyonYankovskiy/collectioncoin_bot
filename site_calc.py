import os
import requests
import openpyxl
import matplotlib.pyplot as plt
from database import DataCoin
import pandas as pd


# класс ошибок
class AuthFail(Exception):
    pass


HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.0.2246 Yowser/2.5 Safari/537.36 "
}


def authorize(username, password):
    # Создаем сессию для сохранения куки
    with requests.Session() as session:
        # Авторизуемся на сайте
        resp = session.post(
            "https://ru.ucoin.net/login",
            data={"email": username, "passwd": password, "remember": 1},
            headers=HEADERS,
            allow_redirects=False,
        )
        if resp.status_code != 302:
            raise AuthFail("неверные данные авторизации")
        # print(resp.headers.get("Location"))
        user_coin_id = "".join(filter(str.isdigit, resp.headers.get("Location")))
        print(user_coin_id, "Connected")
        return user_coin_id, session


def get_graph(telegram_id):
    graph_coin_data = DataCoin.get_for_user(telegram_id)
    print(len(graph_coin_data))

    graph_date = []
    graph_sum = []
    step = -7

    for sublist in graph_coin_data:
        graph_date.append(sublist[2])
        graph_sum.append(sublist[3])

    plt.clf()
    plt.plot(graph_date, graph_sum, marker="o", markersize=4)
    plt.xticks(graph_date[::step], graph_date[::step])

    plt.title("Стоимость коллекции, руб")

    #  Прежде чем рисовать вспомогательные линии
    #  необходимо включить второстепенные деления
    #  осей:
    plt.minorticks_on()

    #  Определяем внешний вид линий основной сетки:
    plt.grid(which="major")

    #  Определяем внешний вид линий вспомогательной
    #  сетки:
    plt.grid(
        # axis="y",
        which="minor",
        linestyle=":",
    )

    plt.savefig(f"{telegram_id}_plot.png")
    return f"{telegram_id}_plot.png"


def download(user_coin_id: str, session: requests.Session):
    # Скачиваем файл
    response = session.get(
        # URL файла, который нужно скачать
        url=f"https://ru.ucoin.net/uid{user_coin_id}?export=xls",
        headers=HEADERS,
    )

    # Имя файла, в который нужно сохранить содержимое
    file_name = f"{user_coin_id}_.xlsx"
    os.remove(file_name)
    with open(file_name, "wb") as f:
        f.write(response.content)
    return file_name


def more_info(file_name):
    df = pd.read_excel(file_name)
    countryroad = df[df.columns[0]].unique()  # эта переменная считает кол-во стран

    return len(df), len(countryroad)


def countries(file_name):
    #df = pd.read_excel('RutoEng.xlsx', header=None)  # assuming no header
    #mydict = df.set_index(0)[1].to_dict()  # setting first column as index and second column as values
    df = pd.read_excel("RutoCode.xlsx", header=None)  # assuming no header
    mydict1 = df.set_index(0)[1].to_dict()
    df = pd.read_excel(file_name)
    result = ""
    grouped = df.groupby("Страна").size()
    for country, count in grouped.items():
        result += f"{mydict1[country]}      {str(count):<5}       {country}\n"

    return result


def file_opener(file_name):
    # Буква столбца, сумму которого нужно посчитать
    column = "G"

    # Открываем файл Excel с помощью openpyxl
    wb = openpyxl.load_workbook(file_name)
    ws = wb.active

    # Удаляем первую строку
    # ws.delete_rows(1)

    # Находим сумму значений в заданном столбце

    # Инициализируем переменную для хранения суммы
    total = 0

    # Проходимся по строкам и суммируем значения в столбце G
    for row in ws.iter_rows(min_row=2, max_col=9):
        # print(row[6].value)
        if not row[6].value:
            continue

        if row[8].value != "Метка 13":
            total += row[6].value

    # Выводим результат
    # print("Сумма значений в столбце G:", total)
    # os.remove(file_name)
    # total = 0
    # for cell in ws[column]:
    #     if cell.value is not None:
    #         total += cell.value

    return round(total, 2)
