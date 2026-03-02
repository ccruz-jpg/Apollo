import streamlit as st
import requests
import pandas as pd

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================

st.set_page_config(page_title="Consola Apollo API", layout="wide")

st.title("🚀 Consola Apollo API")

# ======================================================
# API KEY
# ======================================================

# Primero intenta leer desde Secrets (producción)
if "APOLLO_API_KEY" in st.secrets:
    API_KEY = st.secrets["KqTN83fY1U5Ic4O4-FhRzQ"]
else:
    # Si no existe, permite ingresarla manualmente (modo fallback)
    st.warning("No se encontró APOLLO_API_KEY en Secrets. Ingrésala manualmente.")
    API_KEY = st.text_input("Ingresa tu Apollo API Key", type="password")

if not API_KEY:
    st.stop()

HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

BASE_URL = "https://api.apollo.io/v1"

# ======================================================
# FUNCIÓN POST
# ======================================================

def ejecutar_post(endpoint, payload):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code != 200:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

    return response.json()

# ======================================================
# FORMULARIO
# ======================================================

with st.form("formulario_principal"):

    metodo = st.selectbox(
        "Selecciona el método",
        [
            "Buscar Personas",
            "Buscar Empresas"
        ]
    )

    cargos = st.text_input("Cargos (solo personas)")
    industrias = st.text_input("Industrias")
    ubicaciones = st.text_input("Ubicaciones")
    paginas = st.number_input("Número de páginas", 1, 20, 1)

    ejecutar = st.form_submit_button("Ejecutar consulta")

# ======================================================
# LÓGICA
# ======================================================

if ejecutar:

    endpoint = ""
    payload = {}

    if metodo == "Buscar Personas":

        endpoint = "mixed_people/search"

        payload = {
            "page": paginas,
            "per_page": 50,
            "person_titles": [c.strip() for c in cargos.split(",")] if cargos else [],
            "organization_industries": [i.strip() for i in industrias.split(",")] if industrias else [],
            "person_locations": [u.strip() for u in ubicaciones.split(",")] if ubicaciones else []
        }

    elif metodo == "Buscar Empresas":

        endpoint = "organizations/search"

        payload = {
            "page": paginas,
            "per_page": 50,
            "organization_industries": [i.strip() for i in industrias.split(",")] if industrias else [],
            "organization_locations": [u.strip() for u in ubicaciones.split(",")] if ubicaciones else []
        }

    if not endpoint:
        st.stop()

    with st.spinner("Consultando Apollo..."):
        resultado = ejecutar_post(endpoint, payload)

    if not resultado:
        st.stop()

    # Extraer correctamente la lista interna
    if metodo == "Buscar Personas":
        datos = resultado.get("people", [])
    else:
        datos = resultado.get("organizations", [])

    if not datos:
        st.warning("No se encontraron resultados.")
        st.stop()

    df = pd.json_normalize(datos)

    st.success(f"Se encontraron {len(df)} registros.")
    st.dataframe(df, use_container_width=True)

    # Exportar CSV (estable)
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Descargar CSV",
        data=csv,
        file_name="apollo_resultado.csv",
        mime="text/csv"
    )
