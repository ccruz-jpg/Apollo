import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(page_title="Apollo API Explorer", layout="wide")

API_KEY = st.secrets["KqTN83fY1U5Ic4O4-FhRzQ"]

HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

# =====================================================
# FUNCIÓN GENERICA PARA LLAMAR ENDPOINT
# =====================================================

def llamar_endpoint(endpoint, payload):

    url = f"https://api.apollo.io{endpoint}"

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code != 200:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

    return response.json()


# =====================================================
# UI
# =====================================================

st.title("🚀 Apollo API Explorer")

with st.sidebar:

    st.header("Configuración")

    endpoint = st.selectbox(
        "Selecciona el endpoint",
        [
            "/v1/mixed_people/search",
            "/v1/organizations/search",
            "/v1/people/bulk_match",
            "/v1/organizations/enrich"
        ]
    )

# =====================================================
# FORMULARIO DINÁMICO SEGÚN ENDPOINT
# =====================================================

st.subheader(f"Endpoint seleccionado: {endpoint}")

payload = {}

if endpoint == "/v1/mixed_people/search":

    cargos = st.text_input("Cargos (coma)")
    empresa = st.text_input("Empresa (coma)")
    ubicacion = st.text_input("Ubicación (coma)")
    pagina = st.number_input("Página", 1, 20, 1)

    if st.button("Ejecutar búsqueda"):

        payload = {
            "page": pagina,
            "per_page": 50,
            "person_titles": [c.strip() for c in cargos.split(",")] if cargos else [],
            "organization_names": [e.strip() for e in empresa.split(",")] if empresa else [],
            "person_locations": [u.strip() for u in ubicacion.split(",")] if ubicacion else []
        }

        data = llamar_endpoint(endpoint, payload)

elif endpoint == "/v1/organizations/search":

    nombre_empresa = st.text_input("Nombre de empresa (coma)")
    industria = st.text_input("Industria (coma)")
    pagina = st.number_input("Página", 1, 20, 1)

    if st.button("Ejecutar búsqueda"):

        payload = {
            "page": pagina,
            "per_page": 50,
            "organization_names": [n.strip() for n in nombre_empresa.split(",")] if nombre_empresa else [],
            "organization_industries": [i.strip() for i in industria.split(",")] if industria else []
        }

        data = llamar_endpoint(endpoint, payload)

elif endpoint == "/v1/people/bulk_match":

    email = st.text_input("Email de la persona")

    if st.button("Enriquecer persona"):

        payload = {
            "details": [
                {
                    "email": email
                }
            ]
        }

        data = llamar_endpoint(endpoint, payload)

elif endpoint == "/v1/organizations/enrich":

    dominio = st.text_input("Dominio (ej: empresa.com)")

    if st.button("Enriquecer empresa"):

        payload = {
            "domain": dominio
        }

        data = llamar_endpoint(endpoint, payload)

# =====================================================
# MOSTRAR RESULTADOS
# =====================================================

if "data" in locals() and data:

    st.success("Respuesta recibida correctamente")

    if isinstance(data, dict):

        # Intentar normalizar si viene lista dentro
        if "people" in data:
            df = pd.json_normalize(data["people"])
        elif "organizations" in data:
            df = pd.json_normalize(data["organizations"])
        else:
            df = pd.json_normalize(data)

        st.dataframe(df, use_container_width=True)

        # Exportar
        archivo = BytesIO()
        df.to_excel(archivo, index=False)
        archivo.seek(0)

        st.download_button(
            "Descargar resultado en Excel",
            data=archivo,
            file_name="resultado_apollo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
