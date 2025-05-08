import folium
import json
import pandas as pd
import sqlite3

conn = sqlite3.connect("..\stats_big.db")

# Load the 'income_paris' table into a DataFrame
income_df = pd.read_sql_query("SELECT * FROM income_paris;", conn)

# Load GeoJSON
with open(r"..\data\iris.geojson", "r", encoding="utf-8") as response:
    iris_geo = json.load(response)

# column in geo_json match dataframe
income_df = income_df.rename(columns={"IRIS": "code_iris"})

# Convert code_iris to string (to ensure match)
income_df["code_iris"] = income_df["code_iris"].astype(str)

# Create a lookup dict from the DataFrame
income_lookup = income_df.set_index("code_iris").to_dict(orient="index")


for feature in iris_geo["features"]:
    iris_code = feature["properties"].get("code_iris")
    if iris_code in income_lookup:
        for key, value in income_lookup[iris_code].items():
            feature["properties"][key] = value


with open("iris_income.geojson", "w", encoding="utf-8") as f:
    json.dump(iris_geo, f)

# Load IRIS boundaries with income data (merged into the GeoJSON properties)
with open("iris_income.geojson", "r", encoding="utf-8") as f:
    iris_data = json.load(f)

# Load green spaces GeoJSON
with open(r"..\data\plan-de-voirie-emprises-espaces-verts.geojson", "r", encoding="utf-8") as f:
    green_data = json.load(f)

m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# map with choropleth
folium.Choropleth(
    geo_data=iris_data,
    data=income_df,  # a DataFrame with columns: 'IRIS', 'value'
    columns=["code_iris", "DISP_MED21"],
    key_on="feature.properties.code_iris",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Income"
).add_to(m)


# layer greenspaces over top
folium.GeoJson(
    green_data,
    name="Green Spaces",
    style_function=lambda x: {
        "fillColor": "green",
        "color": "darkgreen",
        "weight": 1,
        "fillOpacity": 0.5
    }
).add_to(m)


folium.LayerControl().add_to(m)
m.save("map.html")