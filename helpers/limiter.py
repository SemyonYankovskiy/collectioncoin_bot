import time
from functools import wraps


# Создаем класс для хранения и изменения времени последнего вызова handler для каждого пользователя
class LastCall:
    # Инициализируем словарь для хранения времени
    def __init__(self, interval):
        self.data = {}
        self.interval = interval

    # Создаем метод для получения времени по идентификатору пользователя
    def get(self, user_id):
        return self.data.get(user_id) or 0

    # Создаем метод для обновления времени по идентификатору пользователя
    def update(self, user_id):
        self.data[user_id] = time.time()

    def can_execute(self, user_id) -> bool:
        delta = time.time() - self.get(user_id)

        # Проверяем, меньше ли разница интервала
        if delta < self.interval:
            return False
        return True

    def times_left(self, user_id) -> int:
        return round(self.interval - (time.time() - self.get(user_id)))


def rate_limit(interval: int):

    last_call = LastCall(interval)

    def decorator(handler):
        @wraps(handler)
        async def wrapper(message, *args, **kwargs):

            # Получаем идентификатор пользователя из сообщения
            user_id = message.from_user.id

            # Если пользователь может вызвать этот handler
            if last_call.can_execute(user_id):
                last_call.update(user_id)
                return await handler(message, *args, *kwargs)

            else:
                seconds = last_call.times_left(user_id)
                await message.answer(
                    f"Вы можете вызвать эту команду только раз в {last_call.interval//60} минут. \n"
                    f"Подождите еще {seconds//60}:{seconds % 60}."
                )

        return wrapper

    return decorator
