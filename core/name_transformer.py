import pandas as pd


class Transformer:
    ru_to_short_eng_file_path = "./config/RutoEng.xlsx"
    ru_to_code_file_path = "./config/RutoCode.xlsx"
    ru_to_valid_eng_file_path = "./config/RutoValidEng.xlsx"
    eng_to_rus_map_file_path = "./config/EngmaptoRu.xlsx"
    coin_difference_file_path = "./config/diff.xlsx"


    def __init__(self):
        # Короткие названия стран на англ, для команд бота
        df = pd.read_excel(self.ru_to_short_eng_file_path, header=None)  # assuming no header
        self._short_eng_names = df.set_index(0)[1].to_dict()

        # Разновидности монет
        df = pd.read_excel(self.coin_difference_file_path, header=None)  # assuming no header
        self._coin_difference = df.set_index(0)[1].to_dict()

        self._rus_names = dict((value, key) for key, value in self._short_eng_names.items())

        # Коды стран для флагов
        df = pd.read_excel(self.ru_to_code_file_path, header=None)  # assuming no header
        self._countries_codes = df.set_index(0)[1].to_dict()

        # Правильные названия стран на англ, для карты
        df = pd.read_excel(self.ru_to_valid_eng_file_path, header=None)  # assuming no header
        self._valid_eng_names = df.set_index(0)[1].to_dict()

        # Переводит названия стран для карты
        df = pd.read_excel(self.eng_to_rus_map_file_path, header=None)
        self._eng_to_rus_map_names = df.set_index(0)[1].to_dict()

    # def get_rus_from_code(self, country_code: str):
    #     for key, value in self._countries_codes.items():
    #         if value == country_code:
    #             return key
    #         elif "🇪🇺" in country_code:
    #             return "Евросоюз"
    #     return ""

    def get_country_eng_short_name(self, country_name: str):
        return self._short_eng_names.get(country_name, "")

    def get_coin_difference(self, country_name: str):
        return self._coin_difference.get(country_name, "")

    def get_country_code(self, country_name: str):
        return self._countries_codes.get(country_name, "")

    def get_country_eng_valid_name(self, country_name: str):
        return self._valid_eng_names.get(country_name, "")

    def get_rus_country_name_on_map(self, country_name: str):
        return self._eng_to_rus_map_names.get(country_name, "")

    def get_country_rus_name(self, country_name: str):
        return self._rus_names.get(country_name, "")

    def get_eng_from_code(self, country_code: str):
        return self._short_eng_names.get(country_code, "")


transformer = Transformer()
