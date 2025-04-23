import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Mapa", layout="wide")
st.title("Mapa Interactivo de Producción Solar")

# Cargar datos
df = pd.read_csv("energia_solar.csv")
df["Latitud"] = df["Latitud"].astype(float)
df["Longitud"] = df["Longitud"].astype(float)
df.columns = df.columns.str.strip()

# Filtro por departamento
departamentos = df["Departamento"].unique().tolist()
departamento_seleccionado = st.selectbox("Selecciona un departamento", ["Todos"] + departamentos)

# Filtrar el dataframe
if departamento_seleccionado != "Todos":
    df_filtrado = df[df["Departamento"] == departamento_seleccionado]
else:
    df_filtrado = df

# Centro del mapa calculado dinámicamente
centro_lat = df_filtrado["Latitud"].mean()
centro_lon = df_filtrado["Longitud"].mean()

# Crear mapa
m = folium.Map(location=[centro_lat, centro_lon], zoom_start=6)

# Verificar que el nombre de columnas no tenga espacios
df.columns = df.columns.str.strip()


# Marcadores dinámicos
if departamento_seleccionado == "Todos":
    # Agrupar por departamento (mostrar un punto promedio por depto)
    resumen = df.groupby("Departamento").agg({
        "Latitud": "mean",
        "Longitud": "mean",
        "Producción_kWh": "mean",
        "Horas_Sol_Diarias": "mean"
    }).reset_index()

    for _, row in resumen.iterrows():
        folium.CircleMarker(
            location=[row["Latitud"], row["Longitud"]],
            radius=8,
            color="green",
            fill=True,
            fill_opacity=0.7,
            popup=(f"<b>{row['Departamento']}</b><br>"
                   f"Prom. Producción: {round(row['Producción_kWh'], 2)} kWh<br>"
                   f"Prom. Sol: {round(row['Horas_Sol_Diarias'], 2)} hrs"),
            tooltip=row["Departamento"]
        ).add_to(m)
else:
    # Mostrar solo un marcador promedio del departamento seleccionado
    df_depto = df[df["Departamento"] == departamento_seleccionado]
    lat_mean = df_depto["Latitud"].mean()
    lon_mean = df_depto["Longitud"].mean()
    prod_mean = df_depto["Producción_kWh"].mean()
    sol_mean = df_depto["Horas_Sol_Diarias"].mean()

    folium.CircleMarker(
        location=[lat_mean, lon_mean],
        radius=10,
        color="blue",
        fill=True,
        fill_opacity=0.7,
        popup=(f"<b>{departamento_seleccionado}</b><br>"
               f"Prom. Producción: {round(prod_mean, 2)} kWh<br>"
               f"Prom. Sol: {round(sol_mean, 2)} hrs"),
        tooltip=departamento_seleccionado
    ).add_to(m)


# Mostrar mapa
st_data = st_folium(m, width=800, height=500)

# Texto debajo del mapa (resumen del departamento)
st.markdown("---")
if departamento_seleccionado != "Todos":
    prod_prom = round(df_filtrado["Producción_kWh"].mean(), 2)
    sol_prom = round(df_filtrado["Horas_Sol_Diarias"].mean(), 2)
    num_paneles = len(df_filtrado)

    st.subheader(f"Datos generales para {departamento_seleccionado}")
    st.markdown(
        f"""
        - Número de paneles registrados: **{num_paneles}**  
        - Producción promedio: **{prod_prom} kWh**  
        - Horas de sol promedio: **{sol_prom} hrs**
        """
    )

    st.subheader("Paneles solares registrados")
    for _, row in df_filtrado.iterrows():
        st.markdown(
            f"""
            <div style="background-color:#1e1e1e;padding:10px;border-radius:8px;margin-bottom:10px;border:1px solid #444;">
                <b>{row['Panel_ID']}</b><br>
                Producción: {row['Producción_kWh']} kWh<br>
                Horas de sol: {row['Horas_Sol_Diarias']} hrs
            </div>
            """, unsafe_allow_html=True
        )
else:
    st.info("Selecciona un departamento en el menú para ver estadísticas detalladas debajo del mapa.")