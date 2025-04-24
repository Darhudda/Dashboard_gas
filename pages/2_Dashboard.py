import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Gas", layout="wide")
st.title("Dashboard de Ventas de Gas Natural")

# Cargar datos
df = pd.read_csv("consulta_ventas_gas_natural.csv")
df["FECHA_VENTA"] = pd.to_datetime(df["FECHA_VENTA"])
df["DEPARTAMENTO"] = df["DEPARTAMENTO"].str.upper()
df["ANIO_VENTA"] = df["FECHA_VENTA"].dt.year
meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

df["NOMBRE_MES"] = df["FECHA_VENTA"].dt.month.apply(lambda x: meses_es[x - 1])

orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
               "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
df["NOMBRE_MES"] = pd.Categorical(df["NOMBRE_MES"], categories=orden_meses, ordered=True)
# Filtros
st.sidebar.header("Filtros")
anio = st.sidebar.selectbox("Selecciona el año", sorted(df["ANIO_VENTA"].unique()))
departamento = st.sidebar.selectbox("Selecciona el departamento", sorted(df["DEPARTAMENTO"].unique()))

df_anio = df[df["ANIO_VENTA"] == anio]
df_barras = df_anio[df_anio["DEPARTAMENTO"] == departamento]

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Volumen Total Suministrado (m³)", f"{df_anio['CANTIDAD_VOLUMEN_SUMINISTRADO'].sum():,.2f}")
with col2:
    st.metric("Vehículos Atendidos", f"{df_anio['VEHICULOS_ATENDIDOS'].sum():,}")
with col3:
    st.metric("Número de Ventas", f"{df_anio['NUMERO_DE_VENTAS'].sum():,}")


# Texto resumen
ventas = df_anio["NUMERO_DE_VENTAS"].sum()
volumen = df_anio["CANTIDAD_VOLUMEN_SUMINISTRADO"].sum()
st.markdown(
    f"""
    <div style='background-color:#1e1e1e; color:white; border-left:6px solid #4caf50;
        padding:15px;
        border-radius:8px;
        font-size:16px;'>
        <strong>Interpretación</strong><br>
        En {anio} se registraron <strong>{ventas:,}</strong> ventas y se suministraron <strong>{volumen:,.2f} m³</strong> de GNV.
    </div>
    """, unsafe_allow_html=True
)

# Estaciones activas
st.subheader("Promedio de Estaciones Activas por Mes")
df_eds = df_anio.groupby("NOMBRE_MES")["EDS_ACTIVAS"].mean().reset_index(name="EDS_PROM")
orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
               "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
df_eds["NOMBRE_MES"] = pd.Categorical(df_eds["NOMBRE_MES"], categories=orden_meses, ordered=True)
fig_eds = px.bar(df_eds.sort_values("NOMBRE_MES"), x="NOMBRE_MES", y="EDS_PROM",
                 title="Promedio de Estaciones Activas por Mes")
st.plotly_chart(fig_eds, use_container_width=True)

# Relación volumen-vehículos
st.subheader("Relación entre Vehículos Atendidos y Volumen")
fig_scatter = px.scatter(df_anio, x="VEHICULOS_ATENDIDOS", y="CANTIDAD_VOLUMEN_SUMINISTRADO",
                         trendline="ols", title=f"Relación entre Vehículos Atendidos y Volumen - {anio}")
st.plotly_chart(fig_scatter, use_container_width=True)

# Barras por mes
st.subheader("Número de Ventas por Mes")
df_barras_mes = df_barras.groupby("NOMBRE_MES")["NUMERO_DE_VENTAS"].sum().reset_index()
df_barras_mes["NOMBRE_MES"] = pd.Categorical(df_barras_mes["NOMBRE_MES"], categories=orden_meses, ordered=True)
fig_barras = px.bar(df_barras_mes.sort_values("NOMBRE_MES"), x="NOMBRE_MES", y="NUMERO_DE_VENTAS",
                    title=f"Número de Ventas - {departamento} - {anio}",
                    color="NUMERO_DE_VENTAS", color_continuous_scale="Plasma")
st.plotly_chart(fig_barras, use_container_width=True)

# Serie de tiempo
st.subheader("Serie de Tiempo - Volumen Mensual")
df_anio["MES"] = df_anio["FECHA_VENTA"].dt.to_period("M").dt.to_timestamp()
serie = df_anio.groupby("MES")["CANTIDAD_VOLUMEN_SUMINISTRADO"].sum().reset_index(name="VOLUMEN_TOTAL")
fig_serie = px.line(serie, x="MES", y="VOLUMEN_TOTAL", markers=True,
                    title=f"Serie de Tiempo de Volumen - {anio}")
st.plotly_chart(fig_serie, use_container_width=True)

