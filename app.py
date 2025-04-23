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

    st.subheader("¿Por qué se hace este análisis?")
    st.markdown(
    """
    En el marco de la transición energética, conocer el comportamiento de los paneles solares 
    es esencial para **tomar decisiones informadas** sobre expansión, mantenimiento y eficiencia energética. 
    Esta herramienta contribuye al análisis de la **producción solar a nivel regional**.
    """
    )

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
    
    st.info("Según las pruebas de normalidad aplicadas, ninguna de las variables numéricas sigue una distribución normal (todas tienen valores-p < 0.05 o estadísticos superiores al valor crítico del 5%).")



    st.info("Utiliza el menú de la izquierda para acceder al **Mapa Interactivo** y al **Dashboard de análisis**.")

elif selected == "Mapa":
    st.switch_page("pages/1_Mapa.py")
elif selected == "Dashboard":
    st.switch_page("pages/2_Dashboard.py")
