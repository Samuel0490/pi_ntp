import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

URL = "http://localhost:8080/api/users/status/ACTIVE"

def get_active_users():
    try:
        response = requests.get(URL)
        response.raise_for_status()  # valida errores HTTP
        return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

df = get_active_users()

st.title("Usuarios Activos - Dashboard")

if not df.empty:
    st.subheader("Tabla de usuarios activos")
    st.dataframe(df)

    if "age" in df.columns and "name" in df.columns:
        st.subheader("Distribución de edades")
        fig, ax = plt.subplots()
        df["age"].hist(bins=10, ax=ax)
        ax.set_xlabel("Edad")
        ax.set_ylabel("Cantidad de usuarios")
        st.pyplot(fig)

        st.subheader("Filtrar usuarios por rango de edad")
        min_edad = int(df["age"].min())
        max_edad = int(df["age"].max())
        rango = st.slider("Selecciona rango de edad", min_edad, max_edad, (min_edad, max_edad))
        filtrados = df[(df["age"] >= rango[0]) & (df["age"] <= rango[1])]
        st.write(f"Usuarios encontrados: {len(filtrados)}")
        st.dataframe(filtrados)

        st.subheader("Gráfico de usuarios filtrados por edad")
        fig2, ax2 = plt.subplots()
        filtrados["age"].hist(bins=10, ax=ax2, color="orange")
        ax2.set_xlabel("Edad")
        ax2.set_ylabel("Cantidad")
        st.pyplot(fig2)
    else:
        st.warning("La API no devuelve columna 'edad' o 'nombre'.")
else:
    st.warning("No se encontraron usuarios activos.")
