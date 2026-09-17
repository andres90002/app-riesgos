import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configura el diseño de la página
st.set_page_config(page_title="Panel Gerencial ForjaHierro G&G", layout="wide")

st.title("Panel Gerencial - ForjaHierro G&G - Versión 2.0")

# Conexión a la base de datos y lectura de la tabla
DATABASE = 'riesgos_forjahierro.db'
@st.cache_data
def cargar_datos():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM incidentes", conn)
    conn.close()
    return df

df = cargar_datos()

# Cálculo de métricas
total_incidentes = len(df)
incidentes_nivel_5 = (df['nivel_riesgo'] == 5).sum()
paradas_requeridas = (df['requiere_parada_planta'] == 1).sum()  # 1 es True en SQLite

# Mostrar métricas
col1, col2, col3 = st.columns(3)
col1.metric("Total de incidentes", total_incidentes)
col2.metric("Incidentes con nivel de riesgo 5", incidentes_nivel_5)
col3.metric("Paradas de planta requeridas", paradas_requeridas)

# Gráfico de barras por área de taller
conteo_area = df['area_taller'].value_counts().reset_index()
conteo_area.columns = ['area_taller', 'cantidad_incidentes']

fig = px.bar(
    conteo_area,
    x='area_taller',
    y='cantidad_incidentes',
    labels={'area_taller': 'Área del Taller', 'cantidad_incidentes': 'Cantidad de Incidentes'},
    title='Incidentes por Área de Taller',
    color='cantidad_incidentes',
    color_continuous_scale='OrRd'
)
st.plotly_chart(fig, use_container_width=True)

# Tabla de datos crudos
st.subheader("Datos Crudos de Incidentes")
st.dataframe(df)