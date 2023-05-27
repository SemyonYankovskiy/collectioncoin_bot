import geopandas as gpd
import matplotlib.pyplot as plt
from PIL import Image
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
from site_calc import countries
from name_transformer import transformer
import math


def get_world_map(user_coin_id) -> str:
    """
    Создаем карту мира с кол-во монеток и возвращаем строку, где файл картинки.

    :param user_coin_id: ID на сайте монет.
    :return: Путь в виде строки изображения.
    """

    data = [
        [line[1], transformer.get_country_eng_valid_name(line[2])]
        for line in countries(f"./users_files/{user_coin_id}_.xlsx")
    ]

    df = pd.DataFrame(data, columns=["count", "eng_name"])
    # df.loc[df['count'] > 40, 'count'] = 35
    df['count'] = df['count'].apply(lambda x: x ** 0.05)

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    countries_data = gpd.read_file(
        "config/ne_110m_admin_0_countries.shp"
    )

    merged = world.merge(df, left_on="name", right_on="eng_name")

    fig, ax = plt.subplots(1, 1, figsize=(15, 6), facecolor=plt.cm.Blues(0.35), linewidth=0.15)
    countries_data.plot(ax=ax,  facecolor=plt.cm.Blues(0.15), )


    ax.set_xlim([-170, 190])
    ax.set_ylim([-60, 85])
    ax.axis("off")

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
    countries_data.plot(ax=ax, edgecolor="black", facecolor='none', linewidth=0.15)

    image_name = f"users_files/{user_coin_id}.png"

    plt.savefig(image_name, dpi=500)
    plt.clf()
    img = Image.open(image_name)
    width, height = img.size
    left = 1000
    top = 150
    right = width - 900
    bottom = height - 0

    img_res = img.crop((left, top, right, bottom))
    img_res.save(image_name)
    return image_name
