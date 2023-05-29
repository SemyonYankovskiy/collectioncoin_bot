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
    mydict = dt.set_index(0)[1].to_dict()  # setting first column as index and second column as values

    # создание датафрейма для построения карты
    data = [
        [line[1], transformer.get_country_eng_valid_name(line[2])]
        for line in countries(f"./users_files/{user_coin_id}_.xlsx")
    ]
    df = pd.DataFrame(data, columns=["count", "eng_name"])



    # для закрашивания разных территорий, принадлежащих 1 стране
    if df[df['eng_name'] == 'Greenland'].empty and df[df['eng_name'] == 'Greenland'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Greenland'].empty:
            df.loc[len(df.index)] = [0, "Greenland"]
        if df[df['eng_name'] == 'Denmark'].empty:
            df.loc[len(df.index)] = [0, "Denmark"]
        df.loc[df["eng_name"] == "Greenland", "count"] += df.loc[df["eng_name"] == "Denmark", "count"].values[0]

    if df[df['eng_name'] == 'Germany'].empty and df[df['eng_name'] == 'GDR'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Germany'].empty:
            df.loc[len(df.index)] = [0, "Germany"]
        if df[df['eng_name'] == 'GDR'].empty:
            df.loc[len(df.index)] = [0, "GDR"]
        df.loc[df["eng_name"] == "Germany", "count"] += df.loc[df["eng_name"] == "GDR", "count"].values[0]
    if df[df['eng_name'] == 'Germany'].empty and df[df['eng_name'] == 'Nazi'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Germany'].empty:
            df.loc[len(df.index)] = [0, "Germany"]
        if df[df['eng_name'] == 'Nazi'].empty:
            df.loc[len(df.index)] = [0, "Nazi"]
        df.loc[df["eng_name"] == "Germany", "count"] += df.loc[df["eng_name"] == "Nazi", "count"].values[0]
    if df[df['eng_name'] == 'Germany'].empty and df[df['eng_name'] == 'FRG'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Germany'].empty:
            df.loc[len(df.index)] = [0, "Germany"]
        if df[df['eng_name'] == 'FRG'].empty:
            df.loc[len(df.index)] = [0, "FRG"]
        df.loc[df["eng_name"] == "Germany", "count"] += df.loc[df["eng_name"] == "FRG", "count"].values[0]

    # для закрашивания разных территорий, принадлежащих 1 стране
    if df[df['eng_name'] == 'Djibouti'].empty and df[df['eng_name'] == 'France_Afar'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Djibouti'].empty:
            df.loc[len(df.index)] = [0, "Djibouti"]
        if df[df['eng_name'] == 'France_Afar'].empty:
            df.loc[len(df.index)] = [0, "France_Afar"]
        df.loc[df["eng_name"] == "Djibouti", "count"] += df.loc[df["eng_name"] == "France_Afar", "count"].values[0]

    # Бенин, Буркина-Фасо, Кот-д'Ивуар, Гвинея-Бисау, Мали, Нигер, Сенегал, Того.
    # Для закрашивания разных территорий, принадлежащих 1 стране
    if df[df['eng_name'] == 'Afrika'].empty and df[df['eng_name'] == 'Benin'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Afrika'].empty:
            df.loc[len(df.index)] = [0, "Afrika"]
        if df[df['eng_name'] == 'Benin'].empty:
            df.loc[len(df.index)] = [0, "Benin"]
        df.loc[df["eng_name"] == "Benin", "count"] += df.loc[df["eng_name"] == "Afrika", "count"].values[0]
    if df[df['eng_name'] == 'Burkina Faso'].empty and df[df['eng_name'] == 'Afrika'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Afrika'].empty:
            df.loc[len(df.index)] = [0, "Afrika"]
        if df[df['eng_name'] == 'Burkina Faso'].empty:
            df.loc[len(df.index)] = [0, "Burkina Faso"]
        df.loc[df["eng_name"] == "Burkina Faso", "count"] += df.loc[df["eng_name"] == "Afrika", "count"].values[0]
    if df[df['eng_name'] == "Côte d'Ivoire"].empty and df[df['eng_name'] == 'Afrika'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Afrika'].empty:
            df.loc[len(df.index)] = [0, "Afrika"]
        if df[df['eng_name'] == "Côte d'Ivoire"].empty:
            df.loc[len(df.index)] = [0, "Côte d'Ivoire"]
        df.loc[df["eng_name"] == "Côte d'Ivoire", "count"] += df.loc[df["eng_name"] == "Afrika", "count"].values[0]
    if df[df['eng_name'] == 'Guinea-Bissau'].empty and df[df['eng_name'] == 'Afrika'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Afrika'].empty:
            df.loc[len(df.index)] = [0, "Afrika"]
        if df[df['eng_name'] == 'Guinea-Bissau'].empty:
            df.loc[len(df.index)] = [0, "Guinea-Bissau"]
        df.loc[df["eng_name"] == "Guinea-Bissau", "count"] += df.loc[df["eng_name"] == "Afrika", "count"].values[0]
    if df[df['eng_name'] == 'Mali'].empty and df[df['eng_name'] == 'Afrika'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Afrika'].empty:
            df.loc[len(df.index)] = [0, "Afrika"]
        if df[df['eng_name'] == 'Mali'].empty:
            df.loc[len(df.index)] = [0, "Mali"]
        df.loc[df["eng_name"] == "Mali", "count"] += df.loc[df["eng_name"] == "Afrika", "count"].values[0]
    if df[df['eng_name'] == 'Niger'].empty and df[df['eng_name'] == 'Afrika'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Afrika'].empty:
            df.loc[len(df.index)] = [0, "Afrika"]
        if df[df['eng_name'] == 'Niger'].empty:
            df.loc[len(df.index)] = [0, "Niger"]
        df.loc[df["eng_name"] == "Niger", "count"] += df.loc[df["eng_name"] == "Afrika", "count"].values[0]
    if df[df['eng_name'] == 'Senegal'].empty and df[df['eng_name'] == 'Afrika'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Afrika'].empty:
            df.loc[len(df.index)] = [0, "Afrika"]
        if df[df['eng_name'] == 'Senegal'].empty:
            df.loc[len(df.index)] = [0, "Senegal"]
        df.loc[df["eng_name"] == "Senegal", "count"] += df.loc[df["eng_name"] == "Afrika", "count"].values[0]
    if df[df['eng_name'] == 'Togo'].empty and df[df['eng_name'] == 'Afrika'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Afrika'].empty:
            df.loc[len(df.index)] = [0, "Afrika"]
        if df[df['eng_name'] == 'Togo'].empty:
            df.loc[len(df.index)] = [0, "Togo"]
        df.loc[df["eng_name"] == "Togo", "count"] += df.loc[df["eng_name"] == "Afrika", "count"].values[0]

    if df[df['eng_name'] == 'N. Cyprus'].empty and df[df['eng_name'] == 'Cyprus'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Cyprus'].empty:
            df.loc[len(df.index)] = [0, "Cyprus"]
        if df[df['eng_name'] == 'N. Cyprus'].empty:
            df.loc[len(df.index)] = [0, "N. Cyprus"]
        df.loc[len(df.index)] = [0, "Cyprus"]
        df.loc[len(df.index)] = [0, "N. Cyprus"]
        df.loc[df["eng_name"] == "N. Cyprus", "count"] += df.loc[df["eng_name"] == "Cyprus", "count"].values[0]

    # Босния и Герцеговина, Хорватия, Македония, Черногория, Сербия и Словения.
    if df[df['eng_name'] == 'Kosovo'].empty and df[df['eng_name'] == 'Serbia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Kosovo'].empty:
            df.loc[len(df.index)] = [0, "Kosovo"]
        if df[df['eng_name'] == 'Serbia'].empty:
            df.loc[len(df.index)] = [0, "Serbia"]
        df.loc[df["eng_name"] == "Kosovo", "count"] = df.loc[df["eng_name"] == "Serbia", "count"].values[0]

    if df[df['eng_name'] == 'Bosnia and Herz.'].empty and df[df['eng_name'] == 'Jyugoslavia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Jyugoslavia'].empty:
            df.loc[len(df.index)] = [0, "Jyugoslavia"]
        if df[df['eng_name'] == 'Bosnia and Herz.'].empty:
            df.loc[len(df.index)] = [0, "Bosnia and Herz."]
        df.loc[df["eng_name"] == "Bosnia and Herz.", "count"] += df.loc[df["eng_name"] == "Jyugoslavia", "count"].values[0]
    if df[df['eng_name'] == 'Croatia'].empty and df[df['eng_name'] == 'Jyugoslavia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Jyugoslavia'].empty:
            df.loc[len(df.index)] = [0, "Jyugoslavia"]
        if df[df['eng_name'] == 'Croatia'].empty:
            df.loc[len(df.index)] = [0, "Croatia"]
        df.loc[df["eng_name"] == "Croatia", "count"] += df.loc[df["eng_name"] == "Jyugoslavia", "count"].values[0]
    if df[df['eng_name'] == "North Macedonia"].empty and df[df['eng_name'] == 'Jyugoslavia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Jyugoslavia'].empty:
            df.loc[len(df.index)] = [0, "Jyugoslavia"]
        if df[df['eng_name'] == 'North Macedonia'].empty:
            df.loc[len(df.index)] = [0, "North Macedonia"]
        df.loc[df["eng_name"] == "North Macedonia", "count"] += df.loc[df["eng_name"] == "Jyugoslavia", "count"].values[0]
    if df[df['eng_name'] == 'Montenegro'].empty and df[df['eng_name'] == 'Jyugoslavia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Jyugoslavia'].empty:
            df.loc[len(df.index)] = [0, "Jyugoslavia"]
        if df[df['eng_name'] == 'Montenegro'].empty:
            df.loc[len(df.index)] = [0, "Montenegro"]
        df.loc[df["eng_name"] == "Montenegro", "count"] += df.loc[df["eng_name"] == "Jyugoslavia", "count"].values[0]
    if df[df['eng_name'] == 'Serbia'].empty and df[df['eng_name'] == 'Jyugoslavia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Jyugoslavia'].empty:
            df.loc[len(df.index)] = [0, "Jyugoslavia"]
        if df[df['eng_name'] == 'Serbia'].empty:
            df.loc[len(df.index)] = [0, "Serbia"]
        df.loc[df["eng_name"] == "Serbia", "count"] += df.loc[df["eng_name"] == "Jyugoslavia", "count"].values[0]
    if df[df['eng_name'] == 'Slovenia'].empty and df[df['eng_name'] == 'Jyugoslavia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Jyugoslavia'].empty:
            df.loc[len(df.index)] = [0, "Jyugoslavia"]
        if df[df['eng_name'] == 'Slovenia'].empty:
            df.loc[len(df.index)] = [0, "Slovenia"]
        df.loc[df["eng_name"] == "Slovenia", "count"] += df.loc[df["eng_name"] == "Jyugoslavia", "count"].values[0]
    if df[df['eng_name'] == 'Kosovo'].empty and df[df['eng_name'] == 'Jyugoslavia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Jyugoslavia'].empty:
            df.loc[len(df.index)] = [0, "Jyugoslavia"]
        if df[df['eng_name'] == 'Kosovo'].empty:
            df.loc[len(df.index)] = [0, "Kosovo"]
        df.loc[df["eng_name"] == "Kosovo", "count"] += df.loc[df["eng_name"] == "Jyugoslavia", "count"].values[0]



    if df[df['eng_name'] == 'Czechia'].empty and df[df['eng_name'] == 'Chehoclovakia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Chehoclovakia'].empty:
            df.loc[len(df.index)] = [0, "Chehoclovakia"]
        if df[df['eng_name'] == 'Czechia'].empty:
            df.loc[len(df.index)] = [0, "Czechia"]
        df.loc[df["eng_name"] == "Czechia", "count"] += df.loc[df["eng_name"] == "Chehoclovakia", "count"].values[0]
    if df[df['eng_name'] == 'Slovakia'].empty and df[df['eng_name'] == 'Chehoclovakia'].empty:
        pass
    else:
        if df[df['eng_name'] == 'Chehoclovakia'].empty:
            df.loc[len(df.index)] = [0, "Chehoclovakia"]
        if df[df['eng_name'] == 'Slovakia'].empty:
            df.loc[len(df.index)] = [0, "Slovakia"]
        df.loc[df["eng_name"] == "Slovakia", "count"] += df.loc[df["eng_name"] == "Chehoclovakia", "count"].values[0]




    # Костыль, чтобы закрашивание было более контрастным (не работает с колорбаром)
    df = df[df['count'] != 0]
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
        facecolor=plt.cm.Greys(0.2),
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
        cmap="YlGn", #YlGn RdYlGn_r
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

    img_res = img.crop((left, top, right, bottom))
    img_res.save(image_name)
    return image_name
