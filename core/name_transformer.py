import pandas as pd


class Transformer:
    ru_to_short_eng_file_path = "./config/RutoEng.xlsx"
    ru_to_code_file_path = "./config/RutoCode.xlsx"
    ru_to_valid_eng_file_path = "./config/RutoValidEng.xlsx"
    eng_to_rus_map_file_path = "./config/EngmaptoRu.xlsx"

    def __init__(self):
        # Короткие названия стран на англ, для команд бота
        df = pd.read_excel(self.ru_to_short_eng_file_path, header=None)  # assuming no header
        self.short_eng_names = df.set_index(0)[1].to_dict()

        # Коды стран для флагов
        df = pd.read_excel(self.ru_to_code_file_path, header=None)  # assuming no header
        self.countries_codes = df.set_index(0)[1].to_dict()

        # Правильные названия стран на англ, для карты
        df = pd.read_excel(self.ru_to_valid_eng_file_path, header=None)  # assuming no header
        self.valid_eng_names = df.set_index(0)[1].to_dict()

        # Переводит названия стран для карты
        df = pd.read_excel(self.eng_to_rus_map_file_path, header=None)
        self.eng_to_rus_map_names = df.set_index(0)[1].to_dict()

    def get_country_eng_short_name(self, country_name: str):
        return self.short_eng_names.get(country_name, "")

    def get_country_code(self, country_name: str):
        return self.countries_codes.get(country_name, "")

    def get_country_eng_valid_name(self, country_name: str):
        return self.valid_eng_names.get(country_name, "")

    def get_rus_country_name(self, country_name: str):
        return self.eng_to_rus_map_names.get(country_name, "")


transformer = Transformer()
