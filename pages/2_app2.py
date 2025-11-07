import streamlit as st
import pandas as pd
import plotly.express as px
# Importamos el DataFrame cargado y limpio desde el loader
from inicio import df_diagnosticos as df 

st.set_page_config(page_title="📊 Análisis Diagnósticos CIE-10", layout="wide")

# ----------------------------------------------------------------------
# --- DASHBOARD PRINCIPAL ---
# ----------------------------------------------------------------------

# Definición de nombres de columnas para evitar errores de tipeo
COL_AÑO = "AÑO REPORTADO"
COL_UNIDAD = "UNIDAD FUNCIONAL"
COL_DIAGNOSTICO = "NOMBRE DEL DIAGNOSTICO"
COL_EDAD = "EDAD DE ATENCION (AÑOS)"


# Verificación crítica de datos
if df.empty or COL_AÑO not in df.columns or COL_UNIDAD not in df.columns or COL_DIAGNOSTICO not in df.columns:
    st.error("No se pudieron cargar los datos o faltan columnas clave (AÑO REPORTADO, UNIDAD FUNCIONAL, NOMBRE DEL DIAGNOSTICO).")
    st.stop()


st.title("📈 Dashboard de Diagnósticos CIE-10")
st.markdown("Análisis interactivo de atenciones por diagnóstico, edad y unidad funcional.")

# --- Filtros ---
col1, col2 = st.columns(2)

with col1:
    # Aseguramos que los valores sean únicos antes de ordenar
    años_unicos = sorted(df[COL_AÑO].dropna().unique())
    # Usamos session_state para mantener el valor del filtro entre ejecuciones
    if 'año_sel_app2' not in st.session_state:
        st.session_state.año_sel_app2 = años_unicos[0] if años_unicos else None
    
    año_sel = st.selectbox("Selecciona el año:", años_unicos, key='año_sel_app2')

with col2:
    unidades_unicas = sorted(df[COL_UNIDAD].dropna().unique().tolist())
    if 'unidad_sel_app2' not in st.session_state:
        st.session_state.unidad_sel_app2 = "Todos"
    
    unidad_sel = st.selectbox("Selecciona unidad funcional:", ["Todos"] + unidades_unicas, key='unidad_sel_app2')

# --- Filtrar datos ---
df_filtrado = df[df[COL_AÑO] == año_sel]
if unidad_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado[COL_UNIDAD] == unidad_sel]

# 4. Guardar el DataFrame filtrado para la Página 3 (Gemini)
st.session_state['df_filtrado_app2'] = df_filtrado.copy()


# ----------------------------------------------------------------------
# --- KPIs (4 Estadísticas) ---
# ----------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_registros = len(df_filtrado)
diagnosticos_unicos = df_filtrado[COL_DIAGNOSTICO].nunique()
unidades_funcionales_unicas = df_filtrado[COL_UNIDAD].nunique()

# Nueva Estadística: Promedio de Edad
if COL_EDAD in df_filtrado.columns:
    promedio_edad = df_filtrado[COL_EDAD].mean()
    promedio_edad_str = f"{promedio_edad:.1f}" if pd.notna(promedio_edad) else "N/A"
else:
    promedio_edad_str = "N/A"


col1.metric("🧾 Total registros", total_registros)
col2.metric("💉 Diagnósticos únicos", diagnosticos_unicos)
col3.metric("🏥 Unidades funcionales", unidades_funcionales_unicas)
col4.metric("👶 Edad Promedio", promedio_edad_str, help="Promedio de edad de los pacientes atendidos (en años).") # Nuevo KPI aquí

st.divider()

# ----------------------------------------------------------------------
# --- Gráficos ---
# ----------------------------------------------------------------------
col1, col2 = st.columns(2)

# Gráfico 1: Frecuencia de diagnósticos
top_diag = df_filtrado[COL_DIAGNOSTICO].value_counts().nlargest(10)
fig1 = px.bar(
    top_diag,
    x=top_diag.values,
    y=top_diag.index,
    orientation="h",
    labels={"x": "Casos", "y": "Diagnóstico"},
    title="🔹 Top 10 diagnósticos más frecuentes",
)
col1.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Promedio de edad por diagnóstico
if COL_EDAD in df_filtrado.columns:
    edad_prom = df_filtrado.groupby(COL_DIAGNOSTICO)[COL_EDAD].mean().nlargest(10)
    fig2 = px.bar(
        edad_prom,
        x=edad_prom.values,
        y=edad_prom.index,
        orientation="h",
        labels={"x": "Edad promedio", "y": "Diagnóstico"},
        title="🔹 Edad promedio de atención (Top 10 diagnósticos)",
    )
    col2.plotly_chart(fig2, use_container_width=True)
else:
     col2.info(f"Columna '{COL_EDAD}' no encontrada o con datos nulos para el Gráfico 2.")


# --- Tabla de detalle ---
st.subheader("📋 Datos detallados")
st.dataframe(df_filtrado, use_container_width=True)