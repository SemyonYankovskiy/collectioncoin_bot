import requests
import openpyxl


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

        print(resp.headers.get("Location"))
        user_coin_id = "".join(filter(str.isdigit, resp.headers.get("Location")))
        print(user_coin_id)
        return user_coin_id, session


def download(user_coin_id: str, session: requests.Session):
    # Скачиваем файл
    response = session.get(
        # URL файла, который нужно скачать
        url=f"https://ru.ucoin.net/uid{user_coin_id}?export=xls",
        headers=HEADERS,
    )

    # Имя файла, в который нужно сохранить содержимое
    file_name = f"{user_coin_id}_DATE.xlsx"
    with open(file_name, "wb") as f:
        f.write(response.content)
    return file_name


def file_opener(file_name):
    # Буква столбца, сумму которого нужно посчитать
    column = "G"

    # Открываем файл Excel с помощью openpyxl
    wb = openpyxl.load_workbook(file_name)
    ws = wb.active

    # Удаляем первую строку
    ws.delete_rows(1)

    # Находим сумму значений в заданном столбце
    total = 0
    for cell in ws[column]:
        if cell.value is not None:
            total += cell.value

    return round(total, 2)
