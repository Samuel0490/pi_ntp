import streamlit as st
import pandas as pd
from pathlib import Path

# La ruta del archivo de Diagnósticos CIE-10
# ASUMIMOS: El archivo está en 'dataframe/enfermedades.csv'
FILE_PATH = Path("dataframe") / "enfermedades.csv"

@st.cache_data
def cargar_datos_diagnosticos():
    """Carga, limpia y prepara el DataFrame de diagnósticos CIE-10."""
    
    try:
        # Usamos coma como separador y la codificación por defecto
        df = pd.read_csv(FILE_PATH, sep=',', encoding='utf-8')
    except FileNotFoundError:
        st.error(f"Error: El archivo CSV no se encontró en la ruta '{FILE_PATH}'. Asegúrate de que el archivo 'enfermedades.csv' esté en la carpeta 'dataframe'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return pd.DataFrame()

    # --- Limpieza y preparación de datos ---

    # 1. Limpiar y estandarizar los nombres de columna
    df.columns = [col.strip().upper().replace('"', '') for col in df.columns]

    # 2. Limpiar la columna AÑO REPORTADO (eliminar coma y convertir a string)
    if "AÑO REPORTADO" in df.columns:
        df["AÑO REPORTADO"] = df["AÑO REPORTADO"].astype(str).str.replace('"', '').str.replace(",", "").str.strip()
    
    # 3. Limpiar y convertir EDAD DE ATENCION
    if "EDAD DE ATENCION (AÑOS)" in df.columns:
        df["EDAD DE ATENCION (AÑOS)"] = pd.to_numeric(
            df["EDAD DE ATENCION (AÑOS)"].astype(str).str.replace('"', '').str.strip(), 
            errors="coerce"
        )
    
    return df

# Carga la data una sola vez y la guarda globalmente
df_diagnosticos = cargar_datos_diagnosticos()