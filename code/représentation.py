import folium
import json
import pandas as pd
import sqlite3
import geopandas as gpd

conn = sqlite3.connect("..\stats_big.db")

espaces_verts_gdf = gpd.read_file("../data/plan-de-voirie-emprises-espaces-verts.geojson")
geo_gdf = gpd.read_file("../data/iris.geojson")
df_revenu = pd.read_sql_query("SELECT * FROM income_paris;", conn)

# renommer et trouver le correspondant à chaque clé
df_revenu  = df_revenu.rename(columns={"IRIS": "code_iris"})
df_revenu["code_iris"] = df_revenu["code_iris"].astype(str)
geo_gdf["code_iris"] = geo_gdf["code_iris"].astype(str)

# fusionner !
fusionner_gdf = geo_gdf.merge(df_revenu, on="code_iris")

# charger le GeoJSON avec des espaces verts
with open(r"..\data\plan-de-voirie-emprises-espaces-verts.geojson", "r", encoding="utf-8") as f:
    data_espaces_verts = json.load(f)

# utiliser la meme carte
iris_gdf = fusionner_gdf.to_crs(epsg=3857)
vert_gdf = espaces_verts_gdf.to_crs(epsg=3857)

# trouver la distance
iris_gdf["centroid"] = iris_gdf.geometry.centroid

def min_distance_a_espace_vert(centroid, polygons_verts):
    return polygons_verts.distance(centroid).min()

iris_gdf["dist_to_green"] = iris_gdf["centroid"].apply(lambda c: round(min_distance_a_espace_vert(c, vert_gdf.geometry),2))
iris_gdf = iris_gdf.drop(columns=["centroid"])
iris_gdf.to_file("../data/iris_avec_distances_vertes.geojson", driver="GeoJSON")
iris_gdf[["nom_iris", "code_iris", "DISP_MED21", "dist_to_green"]].to_csv("../data/iris_revenu_distance.csv", index=False)

with open("../data/iris_avec_distances_vertes.geojson", "r", encoding="utf-8") as f:
    data_iris_avec_distances_vertes = json.load(f)


m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# créer une carte avec choropleth
folium.Choropleth(
    geo_data=fusionner_gdf,
    name="Médiane du revenu disponible par unité de consommation (en euros)",
    data=df_revenu,
    columns=["code_iris", "DISP_MED21"],
    key_on="feature.properties.code_iris",
    scope='europe',
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    highlight=True,
    legend_name="Médiane du revenu disponible"
).add_to(m)


# superposer les espaces verts
folium.GeoJson(
    data_espaces_verts,
    name="Emprises Espaces Verts",
    style_function=lambda x: {
        "fillColor": "green",
        "color": "darkgreen",
        "weight": 1,
        "fillOpacity": 0.5
    }
).add_to(m)


## ajouter les étiquettes
style_function = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
IrisNom = folium.features.GeoJson(
    iris_gdf,
    style_function=style_function, 
    control=False,
    tooltip=folium.features.GeoJsonTooltip(
        fields=['nom_iris'
                ,'code_iris'
                ,'DISP_MED21'
                ,'dist_to_green'
               ],
        aliases=["Nom d'IRIS: "
                ,"Code d'IRIS: "
                ,'Médiane du revenu disponible: '
                ,"Distance jusqu'à l'espace vert le plus proche"
                 ],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
    )
)
# ajouter les étiquettes à la carte
m.add_child(IrisNom)
m.keep_in_front(IrisNom)
folium.LayerControl().add_to(m)

folium.LayerControl().add_to(m)
# sauver la carte
m.save("carte_interactive.html")
