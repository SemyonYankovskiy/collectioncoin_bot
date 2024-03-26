import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

from .name_transformer import transformer
from .site_calc import countries


class WorldMap:
    map_projection = "EPSG:3857"
    color_bar_style = "YlGn"  # `YlGn`, `RdYlGn_r`

    # "Страна_0_которая_будет_отображаться_на_карте":
    # ["Страна_1_которая_добавляет_своё_значение_стране_0", "Страна_2_которая_добавляет_своё_значение_стране_0"],

    countries_alias = {
        "Germany": ["GDR", "Nazi", "FRG"],
        "Greenland": ["Denmark"],
        "Djibouti": ["France_Afar"],
        "Benin": ["Afrika"],
        "Burkina Faso": ["Afrika"],
        "Côte d'Ivoire": ["Afrika"],
        "Guinea-Bissau": ["Afrika"],
        "Mali": ["Afrika"],
        "Niger": ["Afrika"],
        "Senegal": ["Afrika"],
        "Togo": ["Afrika"],
        "N. Cyprus": ["Cyprus"],
        "Kosovo": ["Serbia", "Jyugoslavia"],
        "Bosnia and Herz.": ["Jyugoslavia"],
        "Croatia": ["Jyugoslavia"],
        "North Macedonia": ["Jyugoslavia"],
        "Montenegro": ["Jyugoslavia"],
        "Serbia": ["Jyugoslavia"],
        "Slovenia": ["Jyugoslavia"],
        "Czechia": ["Chehoclovakia"],
        "Slovakia": ["Chehoclovakia"],
        "Fr. S. Antarctic Lands": ["France"],
        "Yemen": ["N.Yemen", "N.Arabia"],
        "Somalia": ["Somaliland"],
        "Gabon": ["Centr_Afrika"],
        "Cameroon": ["Centr_Afrika"],
        "Central African Rep.": ["Centr_Afrika"],
        "Chad": ["Centr_Afrika"],
        "Eq. Guinea": ["Centr_Afrika"],
        "Kenya": ["Britan_Afrika"],
    }

    def __init__(self, user_coin_id: int):
        self.user_coin_id = user_coin_id

        self.df: pd.DataFrame = self._get_countries_and_coin_counts()

        self.need_to_add_counties_names_on_map = False
        self._color_schema = "YlGn"

    def set_color_schema(self, name: str):
        if name in [
            "Greys",
            "Purples",
            "Blues",
            "Greens",
            "Oranges",
            "Reds",
            "YlOrBr",
            "YlOrRd",
            "OrRd",
            "PuRd",
            "RdPu",
            "BuPu",
            "GnBu",
            "PuBu",
            "YlGnBu",
            "PuBuGn",
            "BuGn",
            "YlGn",
        ]:
            self._color_schema = name

    def create_map(self, location: str):
        self._unity_all_countries_aliases()
        self._format_coin_counts()

        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres")).to_crs(
            self.map_projection
        )
        countries_data = gpd.read_file("./config/ne_110m_admin_0_countries.shp").to_crs(
            self.map_projection
        )

        merged = world.merge(self.df, left_on="name", right_on="eng_name")

        fig, ax = self._create_plot()

        countries_data.plot(
            ax=ax,
            facecolor=plt.cm.Greys(0.2),
        )

        self._set_axis_crop(location=location, axis=ax)

        ax.axis("off")

        if self.need_to_add_counties_names_on_map:
            self._add_counties_names_on_map(world=world, axis=ax)

        merged.plot(
            column="count",
            cmap=self._color_schema,
            ax=ax,
            legend=False,
        )
        countries_data.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.15)

        image_name = self._create_map_image()

        plt.clf()

        return image_name

    def _set_axis_crop(self, location: str, axis):
        """
        Изменяет масштаб карты согласно переданной локации.
        :param location: Название локации.
        :param axis: Оси
        """

        if location == "World":
            axis.set_xlim([-2 * 10**7, 2 * 10**7])
            axis.set_ylim([-0.8 * 10**7, 1.9 * 10**7])
        elif location == "Europe":
            axis.set_xlim([-0.42 * 10**7, 0.6 * 10**7])
            axis.set_ylim([0.36 * 10**7, 1.01 * 10**7])
            self.need_to_add_counties_names_on_map = True
        elif location == "South_America":
            axis.set_xlim([-1 * 10**7, -0.4 * 10**7])
            axis.set_ylim([-0.8 * 10**7, 0.2 * 10**7])
            self.need_to_add_counties_names_on_map = True
        elif location == "North_America":
            axis.set_xlim([-1.3 * 10**7, -0.5 * 10**7])
            axis.set_ylim([0 * 10**7, 0.4 * 10**7])
            self.need_to_add_counties_names_on_map = True
        elif location == "Asia":
            axis.set_xlim([0.31 * 10**7, 1.31 * 10**7])
            axis.set_ylim([0.06 * 10**7, 0.68 * 10**7])
            self.need_to_add_counties_names_on_map = True
        elif location == "Africa":
            axis.set_xlim([-0.3 * 10**7, 0.7 * 10**7])
            axis.set_ylim([-0.42 * 10**7, 0.46 * 10**7])
            self.need_to_add_counties_names_on_map = True
        elif location == "Asian_Islands":
            axis.set_xlim([0.6 * 10**7, 2.3 * 10**7])
            axis.set_ylim([-0.6 * 10**7, 0.6 * 10**7])
            self.need_to_add_counties_names_on_map = True

    @staticmethod
    def _add_counties_names_on_map(world, axis):
        """
        Подписывает названия стран на карте.
        """
        for idx, row in world.iterrows():
            axis.annotate(
                text=transformer.get_rus_country_name_on_map(row["name"]),
                xy=row["geometry"].centroid.coords[0],
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=3,
            )

    @staticmethod
    def _create_plot() -> tuple:
        """
        Создаем график.
        """

        return plt.subplots(
            1,
            1,
            figsize=(9, 4.5),
            facecolor=plt.cm.Blues(0.35),
            linewidth=0.15,
            edgecolor="black",
        )

    def _create_map_image(self) -> str:
        """
        Создает изображение карты.
        :return: Путь к изображению.
        """
        image_name = f"users_files/{self.user_coin_id}.png"
        plt.savefig(image_name, dpi=500)

        # Обрезаем картинку.
        img = Image.open(image_name)
        width, height = img.size
        left = 1000
        top = 270
        right = width - 885
        bottom = height - 220

        img_res = img.crop((left, top, right, bottom))
        img_res.save(image_name)
        return image_name

    def _format_coin_counts(self):
        """
        Видоизменяет кол-во монет для стран, чтобы кривая изменения кол-ва была `x ^ 0.05`.
        """
        # Костыль, чтобы закрашивание было более контрастным (не работает с колорбаром)
        self.df["count"] = self.df["count"].apply(lambda x: x**0.05)

    def _get_countries_and_coin_counts(self) -> pd.DataFrame:
        """
        Возвращает `DataFrame` стран и кол-ва монет.
        """
        data = [
            [line[1], transformer.get_country_eng_valid_name(line[2])]
            for line in countries(f"./users_files/{self.user_coin_id}_.xlsx")
        ]
        return pd.DataFrame(data, columns=["count", "eng_name"])

    def _unity_all_countries_aliases(self):
        """
        Объединяет количество монет в странах в соответствии со словарем 'countries_alias'
        """
        for country, aliases in self.countries_alias.items():
            alias_coin_counts = 0
            for alias in aliases:
                if self._has_country(alias):
                    alias_coin_counts += self._get_country_coin_count(alias)
            if alias_coin_counts:
                self._add_to_country_coin_count(country, alias_coin_counts)

    def _add_to_country_coin_count(self, country_name: str, count: int) -> None:
        if self._has_country(country_name):
            self.df.loc[self.df["eng_name"] == country_name, "count"] += count
        else:
            self.df.loc[len(self.df.index)] = [
                count,
                country_name,
            ]

    def _has_country(self, country_name: str) -> bool:
        return not self.df[self.df["eng_name"] == country_name].empty

    def _get_country_coin_count(self, country_name: str) -> int:
        data = self.df[self.df["eng_name"] == country_name]["count"].values[0]
        return data
