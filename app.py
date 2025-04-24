import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from scipy.stats import shapiro, normaltest, anderson
import matplotlib.pyplot as plt
import seaborn as sns

from PIL import Image
import pandas as pd

# Configuración de la app
st.set_page_config(page_title="App con Mapas", layout="wide")

# Menú lateral
with st.sidebar:
    selected = option_menu("Menú", ["Inicio", "Mapa", "Dashboard"],
        icons=["house", "geo-alt", "bar-chart"], menu_icon="cast", default_index=0)

# Página de inicio con contexto
if selected == "Inicio":
    st.title("Diagnóstico Exploratorio Sobre Ventas de Gas Natural Vehicular en Colombia")
    # Imagen alusiva
    imagen = Image.open("gas_pic.jpg")
    st.image(imagen, caption="Paneles solares en Colombia", use_container_width=True)
    st.caption("Imagen tomada de [El Colombiano](https://www.elcolombiano.com/negocios/como-afecta-a-los-carros-la-suspension-de-gas-natural-vehicular-FG25457507)")

    st.markdown(
        """

Este análisis se basa en el conjunto de datos públicos “Consulta Ventas de Gas Natural Comprimido Vehicular (GNCV)”, publicado por el Ministerio de Minas y Energía a través del portal de Datos Abiertos. Esta base proporciona información detallada sobre la comercialización de GNCV en estaciones de servicio del país, con el fin de hacer seguimiento al consumo y distribución de este combustible limpio en el sector transporte.

El objetivo principal es entender cómo se comportan las ventas de GNCV a lo largo del tiempo y en diferentes regiones del país, con el propósito de contribuir a la toma de decisiones energéticas y de movilidad sostenible.

 **¿Qué hay en este conjunto de datos?**
Este estudio incluye las siguientes variables:

- FECHA_VENTA: Fecha exacta de la transacción (año, mes, día).

- AÑO, MES, DIA: Descomposición de la fecha para análisis temporal.

- CODIGO_MUNICIPIO_DANE: Código único de identificación del municipio.

- DEPARTAMENTO, MUNICIPIO: Ubicación geográfica de la estación de servicio.

- LATITUD, LONGITUD: Coordenadas de localización para análisis espacial.

- TIPO_AGENTE: Generalmente “Estación de servicio de GNCV”.

-  TIPO_DE_COMBUSTIBLE: Tipo de combustible vendido, en este caso, GNV (Gas Natural Vehicular).

- EDS_ACTIVAS: Número de estaciones de servicio activas que reportan ventas.

- NUMERO_DE_VENTAS: Total de transacciones de venta realizadas.

- VEHICULOS_ATENDIDOS: Cantidad de vehículos que fueron abastecidos.

- CANTIDAD_VOLUMEN_SUMINISTRADO: Volumen total de gas suministrado (en metros cúbicos).
        """
    )


    # Imagen alusiva
    imagen = Image.open("gas_pic.jpg")
    st.image(imagen, caption="Paneles solares en Colombia", use_container_width=True)
    st.caption("Imagen tomada de [El Colombiano](https://www.elcolombiano.com/negocios/como-afecta-a-los-carros-la-suspension-de-gas-natural-vehicular-FG25457507)")

    # Carga rápida del CSV y resumen
    df = pd.read_csv("consulta_ventas_gas_natural.csv")
    df["FECHA_VENTA"] = pd.to_datetime(df["FECHA_VENTA"])
    df["DEPARTAMENTO"] = df["DEPARTAMENTO"].str.upper()
    df["ANIO_VENTA"] = df["FECHA_VENTA"].dt.year
    df["NOMBRE_MES"] = df["FECHA_VENTA"].dt.month_name(locale="es")
    orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    df["NOMBRE_MES"] = pd.Categorical(df["NOMBRE_MES"], categories=orden_meses, ordered=True)

    st.subheader("Resumen de la base de datos")
    st.dataframe(df.head())

    numeric_cols = ['EDS_ACTIVAS', 'NUMERO_DE_VENTAS', 'VEHICULOS_ATENDIDOS', 'CANTIDAD_VOLUMEN_SUMINISTRADO']

    st.markdown(
        f"""
        - Total de registros: **{len(df)}**
        - Dimensiones: **{df.shape[0]} filas x {df.shape[1]} columnas**
        - Tipo de datos: **{df.dtypes.to_dict()}**
        - Departamentos incluidos: **{df['DEPARTAMENTO'].nunique()}**
        - Valores nulos: **{df.isnull().sum().sum()}**
        ---
        """
    )

    st.markdown("### Estadísticas descriptivas variables numéricas:")
    for col in numeric_cols:
        stats = df[col].describe()
        st.markdown(
            f"""- **{col}**  
            Media: **{stats['mean']:.2f}**, Mediana: **{df[col].median():.2f}**, Desv. estándar: **{stats['std']:.2f}**,  
            Mínimo: **{stats['min']}**, Máximo: **{stats['max']}**,  
            Valores únicos: **{df[col].nunique()}**  
            """
        )

    st.markdown("### Estadísticas descriptivas variables categóricas:")
    categorical_cols = df.select_dtypes(include='object').columns
    for col in categorical_cols:
        st.markdown(
                f"""- **{col}**  
                Valores únicos: **{df[col].nunique()}**  
                Más frecuente: **{df[col].mode()[0]}**  
                """
        )

    st.subheader("Pruebas de normalidad")

    resultados = []

    for col in numeric_cols:
        data = df[col]

        if len(data) > 5000:
            sample = data.sample(5000, random_state=42)
            shapiro_stat, shapiro_p = shapiro(sample)
        else:
            shapiro_stat, shapiro_p = shapiro(data)

        dagostino_stat, dagostino_p = normaltest(data)

        # Anderson- Darling
        anderson_result = anderson(data)
        ad_stat = anderson_result.statistic
        ad_crit_5 = anderson_result.critical_values[2]
        ad_conclusion = "No normal" if ad_stat > ad_crit_5 else "Normal"

        resultados.append({
            "Variable": col,
            "Shapiro-Wilk p-value": round(shapiro_p, 6),
            "D’Agostino p-value": round(dagostino_p, 6),
            "Anderson-Darling stat": round(ad_stat, 4),
            "Anderson critical 5%": round(ad_crit_5, 4),
            "Conclusión Anderson (5%)": ad_conclusion
        })

    tabla_normalidad = pd.DataFrame(resultados)
    print("\nResultados de la prueba de normalidad:\n")
    tabla_normalidad
    
    st.markdown(
    """
    Según las pruebas de normalidad aplicadas, ninguna de las variables numéricas sigue una distribución normal (todas tienen valores-p < 0.05 o estadísticos superiores al valor crítico del 5%)
    """
    )

    st.subheader("Outliers, inliers and extreme values")
    
    df_flags = df.copy()

    # Clasificar cada observación
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_outlier = Q1 - 1.5 * IQR
        upper_outlier = Q3 + 1.5 * IQR
        lower_extreme = Q1 - 3 * IQR
        upper_extreme = Q3 + 3 * IQR

        def classify(x):
            if x < lower_extreme or x > upper_extreme:
                return "extreme"
            elif x < lower_outlier or x > upper_outlier:
                return "outlier"
            else:
                return "inlier"

        # Crear nueva columna con clasificación
        df_flags[f"{col}_categoria"] = df[col].apply(classify)

    # Mostrar resumen de conteo por categoría y variable
    resumen = {}
    for col in numeric_cols:
        counts = df_flags[f"{col}_categoria"].value_counts()
        resumen[col] = {
            "inliers": counts.get("inlier", 0),
            "outliers": counts.get("outlier", 0),
            "extremos": counts.get("extreme", 0),
            "total": len(df)
        }

    resumen_df = pd.DataFrame(resumen).T
    resumen_df["% inliers"] = (resumen_df["inliers"] / resumen_df["total"] * 100).round(2)
    resumen_df["% outliers"] = (resumen_df["outliers"] / resumen_df["total"] * 100).round(2)
    resumen_df["% extremos"] = (resumen_df["extremos"] / resumen_df["total"] * 100).round(2)

    # Mostrar la tabla resumen
    print("\nResumen por variable:")
    resumen_df.drop(columns="total")

    st.subheader("Evolución mensual de ventas de GNCV en los 6 departamentos con mayor actividad")

    df['FECHA_VENTA'] = pd.to_datetime(df['FECHA_VENTA'])

    ventas_por_region_tiempo = df.groupby([pd.Grouper(key='FECHA_VENTA', freq='M'), 'DEPARTAMENTO'])['NUMERO_DE_VENTAS'].sum().reset_index()

    top_departamentos = ventas_por_region_tiempo.groupby('DEPARTAMENTO')['NUMERO_DE_VENTAS'].sum().nlargest(6).index

    ventas_top = ventas_por_region_tiempo[ventas_por_region_tiempo['DEPARTAMENTO'].isin(top_departamentos)]

    plt.figure(figsize=(12, 6))
    for depto in top_departamentos:
        datos = ventas_top[ventas_top['DEPARTAMENTO'] == depto]
        plt.plot(datos['FECHA_VENTA'], datos['NUMERO_DE_VENTAS'], label=depto)

    plt.title("Evolución de ventas de GNCV por región (Top 6 departamentos)")
    plt.xlabel("Fecha")
    plt.ylabel("Número de ventas")
    plt.legend(title="Departamento")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    st.markdown(
    """
    Bogotá D.C. lidera consistentemente las ventas de GNCV, con un crecimiento sostenido a lo largo del tiempo, seguido por Valle del Cauca, Atlántico y Meta. La tendencia ascendente sugiere una expansión progresiva en el uso de este combustible, lo que respalda políticas de movilidad sostenible. También se observan variaciones estacionales y picos abruptos que podrían estar asociados a factores económicos, normativos o logísticos. Esta información es valiosa para planificar la expansión de infraestructura y estrategias de transición energética.)
    """
    )

    st.subheader("Distribuciones")

    sns.set(style="whitegrid")

    # Gráficos tipo boxplot
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))

    sns.boxplot(data=df, x='ANIO_VENTA', y='CANTIDAD_VOLUMEN_SUMINISTRADO', ax=axs[0, 0])
    axs[0, 0].set_title("Distribución del Volumen Suministrado por Año")

    # Boxplot 2: Volumen suministrado por mes
    sns.boxplot(data=df, x='MES_VENTA', y='CANTIDAD_VOLUMEN_SUMINISTRADO', ax=axs[0, 1])
    axs[0, 1].set_title("Distribución del Volumen Suministrado por Mes")

    # Boxplot 3: Volumen suministrado por número de EDS activas
    sns.boxplot(data=df, x='EDS_ACTIVAS', y='CANTIDAD_VOLUMEN_SUMINISTRADO', ax=axs[1, 0])
    axs[1, 0].set_title("Volumen Suministrado según EDS Activas")
    axs[1, 0].tick_params(labelrotation=90)

    # Boxplot 4: Volumen suministrado por departamento (solo top 8)
    top_departamentos = df['DEPARTAMENTO'].value_counts().head(8).index
    sns.boxplot(data=df[df['DEPARTAMENTO'].isin(top_departamentos)], 
                x='DEPARTAMENTO', y='CANTIDAD_VOLUMEN_SUMINISTRADO', ax=axs[1, 1])
    axs[1, 1].set_title("Volumen Suministrado por Departamento (Top 8)")
    axs[1, 1].tick_params(labelrotation=45)

    plt.tight_layout()
    plt.show()

    st.markdown(
    """
    - Por Año: Se observa una ligera tendencia creciente en los volúmenes suministrados con el tiempo, aunque con cierta variabilidad en 2023 y 2024, lo que podría indicar un aumento en la demanda o mejoras en la infraestructura de distribución.

    - Por Mes: Hay mayor variabilidad en algunos meses como enero y marzo. Estos picos pueden estar relacionados con factores estacionales, vacaciones o ciclos económicos que afectan el consumo de gas.

    - Por EDS activas: A medida que aumenta el número de estaciones de servicio activas (EDS), también lo hace el volumen suministrado, aunque con mayor dispersión, lo que sugiere que la eficiencia o demanda puede variar entre estaciones.

    - Por Departamento (Top 8): Algunos departamentos como TOLIMA y CUNDINAMARCA muestran volúmenes más altos y mayor dispersión, lo que puede reflejar diferencias en infraestructura, consumo vehicular o políticas regionales de energía.
    """
    )

    st.markdown(
    """ 
Aunque el gráfico conjunto de cajas y bigotes sugiere que algunas variables como NUMERO_DE_VENTAS están cerca de cero, esto se debe a la diferencia de escalas entre variables
    """
    )
    








    st.info("Utiliza el menú de la izquierda para acceder al **Mapa Interactivo** y al **Dashboard de análisis**.")

elif selected == "Mapa":
    st.switch_page("pages/1_Mapa.py")
elif selected == "Dashboard":
    st.switch_page("pages/2_Dashboard.py")
