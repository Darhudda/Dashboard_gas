import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium import Choropleth

st.set_page_config(page_title="Mapa", layout="wide")
st.title("Mapa Interactivo - Volumen Promedio por Departamento")

# Cargar datos
df = pd.read_csv("consulta_ventas_gas_natural.csv")
df["FECHA_VENTA"] = pd.to_datetime(df["FECHA_VENTA"])
df["ANIO_VENTA"] = df["FECHA_VENTA"].dt.year
df.columns = df.columns.str.strip()

# Cargar mapa GeoJSON de Colombia
colombia_geo = gpd.read_file("https://raw.githubusercontent.com/lihkir/Uninorte/main/AppliedStatisticMS/DataVisualizationRPython/Lectures/Python/PythonDataSets/Colombia.geo.json")

# Filtro por año
anios = sorted(df["ANIO_VENTA"].unique())
anio_seleccionado = st.selectbox("Selecciona un año", anios)

# Agrupación por departamento y año
mapa_data = df[df["ANIO_VENTA"] == anio_seleccionado].groupby("DEPARTAMENTO").agg(
    CANTIDAD_PROMEDIO=pd.NamedAgg(column="CANTIDAD_VOLUMEN_SUMINISTRADO", aggfunc="mean")
).reset_index()

# Unir datos al shapefile
colombia_geo_merged = colombia_geo.merge(mapa_data, left_on="NOMBRE_DPT", right_on="DEPARTAMENTO", how="left")
colombia_geo_merged["CANTIDAD_PROMEDIO"] = colombia_geo_merged["CANTIDAD_PROMEDIO"].fillna(0)

# Centrado del mapa
centro = [4.5709, -74.2973]
m = folium.Map(location=centro, zoom_start=5.2)

# Capa de coropletas
Choropleth(
    geo_data=colombia_geo_merged.__geo_interface__,
    data=colombia_geo_merged,
    columns=["NOMBRE_DPT", "CANTIDAD_PROMEDIO"],
    key_on="feature.properties.NOMBRE_DPT",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Volumen Promedio (m³)"
).add_to(m)

# Agregar etiquetas
for _, row in colombia_geo_merged.iterrows():
    if row["CANTIDAD_PROMEDIO"] > 0:
        folium.Marker(
            location=[row["geometry"].centroid.y, row["geometry"].centroid.x],
            icon=None,
            popup=f"{row['NOMBRE_DPT']}: {round(row['CANTIDAD_PROMEDIO'], 2)} m³"
        ).add_to(m)

st_data = st_folium(m, width=1000, height=550)