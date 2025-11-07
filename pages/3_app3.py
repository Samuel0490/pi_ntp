import streamlit as st
import pandas as pd
from google import genai
# Importamos el DF completo de Diagnósticos como fallback
from inicio import df_diagnosticos as df_completo 
from pathlib import Path

st.set_page_config(page_title="🤖 Asistente Gemini", layout="wide")

st.title("💬 Asistente de Análisis de Diagnósticos (Gemini)")
st.markdown("Esta herramienta utiliza IA para responder preguntas sobre los datos filtrados en la página **2 - Dashboard CIE-10**.")
st.divider()

# ----------------------------------------------------------------------
# --- Lógica de Acceso a Datos ---
# ----------------------------------------------------------------------

# Intentamos usar el DataFrame filtrado de la página 2
df_contexto = st.session_state.get('df_filtrado_app2', pd.DataFrame())

if df_contexto.empty:
    # Si no hay filtros o el DF filtrado es igual al completo, usamos el completo
    df_contexto = df_completo
    if df_contexto.empty:
        st.error("No hay datos disponibles para el análisis. Asegúrate de que el archivo CSV se haya cargado correctamente.")
        st.stop()
    st.warning(f"⚠️ Analizando **{len(df_contexto)}** registros sin filtros. ¡Ve a la Página 2 para aplicar filtros primero!")
else:
    st.info(f"✅ Analizando **{len(df_contexto)}** registros filtrados desde el Dashboard.")


# ----------------------------------------------------------------------
# --- ASISTENTE CONVERSACIONAL (RAG) ---
# ----------------------------------------------------------------------

# 1. Inicializar el cliente Gemini
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("❌ Error de configuración: La clave 'GEMINI_API_KEY' no está configurada en .streamlit/secrets.toml")
    st.stop()
except Exception as e:
    st.error(f"❌ Error al inicializar el cliente Gemini: {e}")
    st.stop()


# 2. Preparar los datos como contexto (usando el df_contexto)
@st.cache_data(ttl=600) 
def get_dataframe_context(df_to_analyze):
    """Convierte un subconjunto del DataFrame a texto (Markdown) para el LLM."""
    if df_to_analyze.empty:
        return "No hay datos disponibles para este análisis."

    # Limitamos a 50 filas y solo 10 columnas para no sobrecargar el modelo
    df_sample = df_to_analyze.head(50).iloc[:, :10] 
    
    context_str = "Los datos de diagnósticos CIE-10 filtrados son (primeras 50 filas y 10 columnas):\n"
    context_str += df_sample.to_markdown(index=False)
    
    context_str += "\n\nColumnas disponibles: " + ", ".join(df_to_analyze.columns.tolist())
    context_str += f"\nTotal de filas a analizar: {len(df_to_analyze)}"
    
    return context_str

data_context = get_dataframe_context(df_contexto)


# 3. Inicializar el historial de chat de Streamlit
# Usamos un key único para el chat de esta página
if "messages_diagnosticos" not in st.session_state:
    st.session_state["messages_diagnosticos"] = [
        {"role": "assistant", "content": "Hola, soy el Asistente de Diagnósticos. Pregúntame sobre los diagnósticos CIE-10 filtrados. Por ejemplo: ¿Cuál es la Unidad Funcional con más atenciones de Cólera?"}
    ]

# 4. Mostrar el historial
for msg in st.session_state["messages_diagnosticos"]:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. Capturar la nueva entrada del usuario
if prompt := st.chat_input("Haz una pregunta sobre los datos filtrados..."):
    
    st.session_state["messages_diagnosticos"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Definir el mensaje del sistema (prompt de ingeniería)
    system_prompt = (
        "Eres un asistente de análisis de datos profesional experto en diagnósticos médicos CIE-10. Responde a la pregunta del usuario utilizando exclusivamente "
        "la información y el contexto del DataFrame de diagnósticos que se te proporciona. "
        "Tu respuesta debe ser clara, concisa, en español, y solo usar los datos del contexto. "
        "Si la pregunta no se puede responder, responde educadamente que la información no está disponible."
        f"\n\nCONTEXTO DEL DATAFRAME:\n{data_context}"
    )

    # Configurar y llamar a la API de Gemini
    try:
        with st.spinner("Analizando los datos con Gemini..."):
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[system_prompt, f"Pregunta del usuario: {prompt}"],
            )
            
            assistant_response = response.text
            st.session_state["messages_diagnosticos"].append({"role": "assistant", "content": assistant_response})
            st.chat_message("assistant").write(assistant_response)

    except Exception as e:
        error_msg = f"Lo siento, hubo un error al consultar a Gemini: {e}"
        st.session_state["messages_diagnosticos"].append({"role": "assistant", "content": error_msg})
        st.chat_message("assistant").write(error_msg)