import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_icon="🩺", layout="wide")

# == Carga de datos ==
archivo_csv = 'dataframe/enfermedades.csv'  # Cambia al nombre real de tu archivo
try:
    df = pd.read_csv(archivo_csv, encoding='utf-8')
except FileNotFoundError:
    st.error(f"No se encontró el archivo '{archivo_csv}' en la carpeta actual.")
    st.stop()

# == Limpieza de columnas ==
df.columns = [col.strip().upper() for col in df.columns]
df = df.rename(columns={
    'CIDIGO CIE-10': 'CIE10',
    'NOMBRE DEL DIAGNOSTICO': 'DIAGNOSTICO',
    'UNIDAD FUNCIONAL': 'UNIDAD',
    'DESTINO AL EGRESO': 'DESTINO',
    'EDAD DE ATENCION (AÑOS)': 'EDAD',
    'AÑO REPORTADO': 'ANIO'
})

# == Conversión de datos ==
df['EDAD'] = pd.to_numeric(df['EDAD'], errors='coerce')
df['ANIO'] = df['ANIO'].astype(str).str.replace(',', '').astype(int)

# == Sidebar de filtros ==
st.sidebar.title("🔎 Filtros de Enfermedades")
anios = sorted(df['ANIO'].unique())
anio_sel = st.sidebar.multiselect('Año reportado:', options=anios, default=anios)
unidad_sel = st.sidebar.multiselect('Unidad funcional:', options=sorted(df['UNIDAD'].unique()), default=sorted(df['UNIDAD'].unique()))
destino_sel = st.sidebar.multiselect('Destino al egreso:', options=sorted(df['DESTINO'].unique()), default=sorted(df['DESTINO'].unique()))
diagnostico_buscar = st.sidebar.text_input("Buscar diagnóstico (palabra clave):")
edad_min, edad_max = int(df['EDAD'].min()), int(df['EDAD'].max())
rango_edad = st.sidebar.slider('Rango de edad:', min_value=edad_min, max_value=edad_max, value=(edad_min, edad_max))

# == Aplicar filtros ==
df_filtrado = df[
    df['ANIO'].isin(anio_sel) &
    df['UNIDAD'].isin(unidad_sel) &
    df['DESTINO'].isin(destino_sel) &
    df['EDAD'].between(rango_edad[0], rango_edad[1])
]

if diagnostico_buscar:
    df_filtrado = df_filtrado[
        df_filtrado['DIAGNOSTICO'].str.contains(diagnostico_buscar, case=False, na=False) |
        df_filtrado['CIE10'].str.contains(diagnostico_buscar, case=False, na=False)
    ]

# == Título y datos ==
st.markdown("""
<div style="background: linear-gradient(90deg, #155799, #159957); 
            padding:10px; border-radius:10px; text-align:center;">
    <h1 style="color:white;">🩺 Dashboard de Enfermedades (Diagnósticos)</h1>
</div>
""", unsafe_allow_html=True)

st.markdown(f"**Total registros filtrados:** {len(df_filtrado)}")

st.markdown("<h2 style='text-align:center;'>📋 Datos Filtrados</h2>", unsafe_allow_html=True)
st.dataframe(df_filtrado[['CIE10', 'DIAGNOSTICO', 'UNIDAD', 'DESTINO', 'EDAD', 'ANIO']], use_container_width=True)

if not df_filtrado.empty:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>📈 Visualizaciones</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Diagnósticos más frecuentes
    top_diag = df_filtrado['DIAGNOSTICO'].value_counts().nlargest(10).reset_index()
    top_diag.columns = ['DIAGNOSTICO', 'REGISTROS']
    fig1 = px.bar(top_diag, x='DIAGNOSTICO', y='REGISTROS', title="Top 10 Diagnósticos", labels={'REGISTROS':'Nº de casos'})
    col1.plotly_chart(fig1, use_container_width=True)

    # Distribución por unidad funcional
    unidad_counts = df_filtrado['UNIDAD'].value_counts().reset_index()
    unidad_counts.columns = ['UNIDAD', 'REGISTROS']
    fig2 = px.bar(unidad_counts, x='UNIDAD', y='REGISTROS', title="Distribución por Unidad Funcional", labels={'REGISTROS':'Nº de casos'})
    col2.plotly_chart(fig2, use_container_width=True)

    # Distribución por destino
    destino_counts = df_filtrado['DESTINO'].value_counts().reset_index()
    destino_counts.columns = ['DESTINO', 'REGISTROS']
    fig3 = px.pie(destino_counts, names='DESTINO', values='REGISTROS', title="Destino al egreso", hole=0.3)
    col1.plotly_chart(fig3, use_container_width=True)

    # Histograma de edad
    fig4 = px.histogram(df_filtrado, x='EDAD', nbins=20, title="Distribución de edades", labels={'EDAD':'Edad'})
    col2.plotly_chart(fig4, use_container_width=True)

    # Tendencia anual
    st.divider()
    tendencia = df_filtrado.groupby('ANIO').size().reset_index(name='CASOS')
    fig5 = px.line(tendencia, x='ANIO', y='CASOS', title="Casos por Año reportado", markers=True, labels={'ANIO':'Año', 'CASOS':'Nº de casos'})
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("No hay datos que cumplan con los filtros seleccionados.")
