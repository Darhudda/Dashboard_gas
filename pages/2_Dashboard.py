import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard de Producción Solar en Colombia")

# Cargar datos
df = pd.read_csv("energia_solar.csv")
df.columns = df.columns.str.strip()

# Filtro de departamento
departamentos = ["Todos"] + sorted(df["Departamento"].unique())
dep_seleccionado = st.selectbox("Selecciona un departamento (opcional):", departamentos)

if dep_seleccionado == "Todos":
    df_filtrado = df.copy()
else:
    df_filtrado = df[df["Departamento"] == dep_seleccionado]

# KPIs
col1, col2 = st.columns(2)
with col1:
    prod_prom = round(df_filtrado["Producción_kWh"].mean(), 2)
    st.metric("⚡ Producción promedio (kWh)", f"{prod_prom}")
with col2:
    sol_prom = round(df_filtrado["Horas_Sol_Diarias"].mean(), 2)
    st.metric("☀️ Horas de sol promedio", f"{sol_prom}")

st.markdown("---")

# Gráfico de barras: promedio por departamento (producción + horas)
st.subheader("Comparación por Departamento (Promedios)")
if dep_seleccionado == "Todos":
    resumen = df.groupby("Departamento").agg({
        "Producción_kWh": "mean",
        "Horas_Sol_Diarias": "mean"
    }).reset_index()

    fig_bar = px.bar(resumen, x="Departamento", y=["Producción_kWh", "Horas_Sol_Diarias"],
                     barmode="group", labels={"value": "Promedio", "variable": "Variable"},
                     title="Promedio de Producción y Horas de Sol por Departamento")
    st.plotly_chart(fig_bar, use_container_width=True)

# Scatter plot
st.subheader("Relación entre Horas de Sol y Producción")
fig_scatter = px.scatter(df_filtrado, x="Horas_Sol_Diarias", y="Producción_kWh",
                         color="Departamento" if dep_seleccionado == "Todos" else None,
                         title="Horas de Sol vs Producción", trendline="ols")
st.plotly_chart(fig_scatter, use_container_width=True)

# Boxplot por departamento (solo si no hay filtro)
if dep_seleccionado == "Todos":
    st.subheader("Variabilidad de Producción por Departamento (Boxplot)")
    fig_box = px.box(df, x="Departamento", y="Producción_kWh",
                     title="Distribución de Producción por Departamento")
    st.plotly_chart(fig_box, use_container_width=True)