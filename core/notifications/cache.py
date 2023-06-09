from typing import Any


class MemoryStorage:
    def __init__(self):
        self._data: dict[int, dict[str, Any]] = {}

    def set_data(self, user_id: int, key: str, data: Any):
        self._resolve_user_storage(user_id)
        self._data[user_id][key] = data

    def get_data(self, user_id: int, key: str) -> Any:
        self._resolve_user_storage(user_id)
        return self._data[user_id].get(key)

    def remove_data(self, user_id: int, key: str) -> Any:
        self._resolve_user_storage(user_id)
        if self._data[user_id].get(key):
            del self._data[user_id][key]

    def _resolve_user_storage(self, user_id: int):
        self._data.setdefault(user_id, {})


storage = MemoryStorage()
