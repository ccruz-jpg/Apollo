import streamlit as st
import requests
import pandas as pd

# ======================================================
# CONFIGURACIÓN
# ======================================================

st.set_page_config(page_title="Apollo API Console", layout="wide")

if "APOLLO_API_KEY" not in st.secrets:
    st.error("No se encontró APOLLO_API_KEY en los Secrets de Streamlit Cloud.")
    st.stop()

API_KEY = st.secrets["KqTN83fY1U5Ic4O4-FhRzQ"]

HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

BASE_URL = "https://api.apollo.io/v1"

# ======================================================
# FUNCIÓN GENÉRICA POST
# ======================================================

def ejecutar_post(endpoint, payload):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code != 200:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

    return response.json()

# ======================================================
# INTERFAZ
# ======================================================

st.title("🚀 Consola Completa Apollo API")
st.markdown("Ejecuta cualquier método principal de Apollo y descarga el resultado.")

with st.form("formulario_principal"):

    metodo = st.selectbox(
        "Selecciona el método",
        [
            "Buscar Personas",
            "Buscar Empresas",
            "Enriquecer Persona",
            "Enriquecer Empresa",
            "Match Persona por Email",
            "Match Empresa por Dominio"
        ]
    )

    st.markdown("### Parámetros")

    cargos = st.text_input("Cargos (separados por coma)")
    industrias = st.text_input("Industrias (separadas por coma)")
    ubicaciones = st.text_input("Ubicaciones (separadas por coma)")
    email = st.text_input("Email")
    dominio = st.text_input("Dominio (ej: empresa.com)")
    paginas = st.number_input("Número de páginas (solo búsqueda)", 1, 20, 1)

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

    elif metodo == "Enriquecer Persona":
        if not email:
            st.warning("Debes ingresar un email.")
            st.stop()
        endpoint = "people/enrich"
        payload = {"email": email}

    elif metodo == "Enriquecer Empresa":
        if not dominio:
            st.warning("Debes ingresar un dominio.")
            st.stop()
        endpoint = "organizations/enrich"
        payload = {"domain": dominio}

    elif metodo == "Match Persona por Email":
        if not email:
            st.warning("Debes ingresar un email.")
            st.stop()
        endpoint = "people/match"
        payload = {"email": email}

    elif metodo == "Match Empresa por Dominio":
        if not dominio:
            st.warning("Debes ingresar un dominio.")
            st.stop()
        endpoint = "organizations/match"
        payload = {"domain": dominio}

    if not endpoint:
        st.error("Método no válido.")
        st.stop()

    with st.spinner("Consultando Apollo..."):
        resultado = ejecutar_post(endpoint, payload)

    if not resultado:
        st.stop()

    df = pd.json_normalize(resultado)

    st.success("Consulta completada.")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Descargar CSV",
        data=csv,
        file_name="apollo_resultado.csv",
        mime="text/csv"
    )
