import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# ======================================================
# CONFIGURACIÓN
# ======================================================

st.set_page_config(page_title="Apollo API Console", layout="wide")

APOLLO_API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": APOLLO_API_KEY
}

BASE_URL = "https://api.apollo.io/v1"

# ======================================================
# FUNCIÓN GENÉRICA
# ======================================================

def ejecutar_post(endpoint, payload):

    url = f"{BASE_URL}/{endpoint}"
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code != 200:
        st.error(response.text)
        return None

    return response.json()

# ======================================================
# INTERFAZ
# ======================================================

st.title("🚀 Apollo API - Consola Completa")

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

    cargos = st.text_input("Cargos (coma)")
    industrias = st.text_input("Industrias (coma)")
    ubicaciones = st.text_input("Ubicaciones (coma)")
    email = st.text_input("Email")
    dominio = st.text_input("Dominio")
    paginas = st.number_input("Páginas (solo búsqueda)", 1, 20, 1)

    ejecutar = st.form_submit_button("Ejecutar")

# ======================================================
# LÓGICA
# ======================================================

if ejecutar:

    payload = {}
    endpoint = ""

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
        endpoint = "people/enrich"
        payload = {"email": email}

    elif metodo == "Enriquecer Empresa":
        endpoint = "organizations/enrich"
        payload = {"domain": dominio}

    elif metodo == "Match Persona por Email":
        endpoint = "people/match"
        payload = {"email": email}

    elif metodo == "Match Empresa por Dominio":
        endpoint = "organizations/match"
        payload = {"domain": dominio}

    if not endpoint:
        st.warning("Método no válido.")
        st.stop()

    with st.spinner("Consultando Apollo..."):
        resultado = ejecutar_post(endpoint, payload)

    if not resultado:
        st.stop()

    df = pd.json_normalize(resultado)

    st.success("Consulta completada.")
    st.dataframe(df, use_container_width=True)

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        "📥 Descargar Excel",
        data=buffer,
        file_name="apollo_resultado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
