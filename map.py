import geopandas as gpd
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
from site_calc import countries
from name_transformer import transformer


def get_world_map(user_coin_id, location) -> str:
    """
    Создаем карту мира с кол-во монеток и возвращаем строку, где файл картинки.

    :param user_coin_id: ID на сайте монет.
    :return: Путь в виде строки изображения.
    """
    dt = pd.read_excel("./config/EngmaptoRu.xlsx", header=None)  # assuming no header
    mydict = dt.set_index(0)[
        1
    ].to_dict()  # setting first column as index and second column as values

    # создание датафрейма для построения карты
    data = [
        [line[1], transformer.get_country_eng_valid_name(line[2])]
        for line in countries(f"./users_files/{user_coin_id}_.xlsx")
    ]
    df = pd.DataFrame(data, columns=["count", "eng_name"])

    # для закрашивания разных территорий, принадлежащих 1 стране
    df.loc[len(df.index)] = [0, "Greenland"]
    df.loc[df["eng_name"] == "Greenland", "count"] += df.loc[
        df["eng_name"] == "Denmark", "count"
    ].values[0]

    # Костыль, чтобы закрашивание было более контрастным (не работает с колорбаром)
    df["count"] = df["count"].apply(lambda x: x**0.05)

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres")).to_crs(
        "EPSG:3857"
    )
    countries_data = gpd.read_file("config/ne_110m_admin_0_countries.shp").to_crs(
        "EPSG:3857"
    )

    merged = world.merge(df, left_on="name", right_on="eng_name")

    fig, ax = plt.subplots(
        1,
        1,
        figsize=(9, 4.5),
        facecolor=plt.cm.Blues(0.35),
        linewidth=0.15,
        edgecolor="black",
    )
    countries_data.plot(
        ax=ax,
        facecolor=plt.cm.Blues(0.1),
    )
    country_name = False
    if location == "World":
        ax.set_xlim([-2 * 10**7, 2 * 10**7])
        ax.set_ylim([-0.8 * 10**7, 1.9 * 10**7])

    elif location == "Europe":
        ax.set_xlim([-0.42 * 10**7, 0.6 * 10**7])
        ax.set_ylim([0.36 * 10**7, 1.01 * 10**7])
        country_name = True
    elif location == "South_America":
        ax.set_xlim([-1 * 10**7, -0.4 * 10**7])
        ax.set_ylim([-0.8 * 10**7, 0.2 * 10**7])
        country_name = True
    elif location == "North_America":
        ax.set_xlim([-1.3 * 10**7, -0.5 * 10**7])
        ax.set_ylim([0 * 10**7, 0.4 * 10**7])
        country_name = True
    elif location == "Asia":
        ax.set_xlim([0.35 * 10**7, 1.35 * 10**7])
        ax.set_ylim([0.06 * 10**7, 0.68 * 10**7])
        country_name = True
    elif location == "Afrika":
        ax.set_xlim([-0.3 * 10**7, 0.7 * 10**7])
        ax.set_ylim([-0.42 * 10**7, 0.46 * 10**7])
        country_name = True
    elif location == "Asian_Islands":
        ax.set_xlim([0.8 * 10**7, 2.5 * 10**7])
        ax.set_ylim([-0.6 * 10**7, 0.6 * 10**7])
        country_name = True

    ax.axis("off")

    # ax.grid('on')
    if country_name is True:
        for idx, row in world.iterrows():
            ax.annotate(
                text=mydict[row["name"]],
                xy=row["geometry"].centroid.coords[0],
                horizontalalignment="center",
                verticalalignment="bottom",
                fontsize=3,
            )

    # ниже колорбар
    # divider = make_axes_locatable(ax)
    # cax = divider.append_axes(
    #      "bottom",
    #      size="1%",
    #      pad=0.2,
    #  )
    merged.plot(
        column="count",
        cmap="YlGn",
        ax=ax,
        legend=False,
        #    cax=cax,
        #    legend_kwds={"orientation": "horizontal"},
    )
    countries_data.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.15)

    image_name = f"users_files/{user_coin_id}.png"

    plt.savefig(image_name, dpi=500)
    plt.clf()
    img = Image.open(image_name)
    width, height = img.size
    left = 1000
    top = 270
    right = width - 885
    bottom = height - 220

    # if location == "World":
    #     left = 1000
    #     top = 270
    #     right = width - 885
    #     bottom = height - 220
    # elif location == "Europe":
    #     ax.set_xlim([-2 * 10**7, 2 * 10**7])
    #     ax.set_ylim([-0.8 * 10**7, 1.9 * 10**7])
    # elif location == "South_America":
    #     ax.set_xlim([-2 * 10**7, 2 * 10**7])
    #     ax.set_ylim([-0.8 * 10**7, 1.9 * 10**7])
    # elif location == "North_America":
    #     ax.set_xlim([-2 * 10**7, 2 * 10**7])
    #     ax.set_ylim([-0.8 * 10**7, 1.9 * 10**7])
    # elif location == "Asia":
    #     ax.set_xlim([-2 * 10**7, 2 * 10**7])
    #     ax.set_ylim([-0.8 * 10**7, 1.9 * 10**7])
    # elif location == "Afrika":
    #     ax.set_xlim([-2 * 10**7, 2 * 10**7])
    #     ax.set_ylim([-0.8 * 10**7, 1.9 * 10**7])
    # elif location == "Asian_Islands":
    #     ax.set_xlim([-2 * 10**7, 2 * 10**7])
    #     ax.set_ylim([-0.8 * 10**7, 1.9 * 10**7])

    img_res = img.crop((left, top, right, bottom))
    img_res.save(image_name)
    return image_name
