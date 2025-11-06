import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Gemini & Enfermedades", page_icon="✨", layout="wide")

archivo_csv = 'dataframe/enfermedades.csv'
try:
    df = pd.read_csv(archivo_csv, encoding='utf-8')
except FileNotFoundError:
    st.error(f"No se encontró el archivo '{archivo_csv}' en la carpeta actual.")
    st.stop()

df.columns = [col.strip().upper() for col in df.columns]
df = df.rename(columns={
    'CIDIGO CIE-10': 'CIE10',
    'NOMBRE DEL DIAGNOSTICO': 'DIAGNOSTICO',
    'UNIDAD FUNCIONAL': 'UNIDAD',
    'DESTINO AL EGRESO': 'DESTINO',
    'EDAD DE ATENCION (AÑOS)': 'EDAD',
    'AÑO REPORTADO': 'ANIO'
})

st.title("✨ Gemini sobre Enfermedades")

api_key = st.sidebar.text_input("API Key Gemini", type="password")
max_mostrar = st.sidebar.slider("Filas que verá Gemini:", 10, min(200, len(df)), 50)
pregunta = st.text_area("Pregunta a Gemini sobre el dataframe:", value="¿Cuáles son los diagnósticos más comunes en menores de 18 años?")

if st.button("Enviar a Gemini"):
    if not api_key:
        st.error("Falta API Key")
        st.stop()
    contexto = df.head(max_mostrar).to_markdown(index=False)
    prompt = (
        "Eres un asistente experto en análisis de datos médicos. "
        f"Tienes las primeras {max_mostrar} filas del dataframe 'enfermedades', columnas {list(df.columns)}.\n\n"
        f"{contexto}\n\n"
        f"Pregunta: {pregunta}"
    )
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        st.success("Respuesta Gemini:")
        st.markdown(response.text)
    except Exception as e:
        st.error(f"Error con Gemini: {str(e)}")

if st.checkbox("Mostrar DataFrame completo"):
    st.dataframe(df, use_container_width=True)
