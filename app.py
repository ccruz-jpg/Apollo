import streamlit as st
import requests
import pandas as pd

# ======================================================
# CONFIG
# ======================================================

st.set_page_config(page_title="Apollo API Console Pro", layout="wide")

API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

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
# UI
# ======================================================

st.title("🚀 Apollo API Console - Versión Completa")

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

    st.markdown("## 🔎 Filtros de búsqueda")

    # PERSONAS
    cargos = st.text_input("Cargos (CEO, Marketing Manager)")
    empresas = st.text_input("Empresas (Google, Amazon)")
    industrias = st.text_input("Industrias (Software, Fintech)")
    ubicaciones = st.text_input("Ubicaciones (United States, Spain)")
    seniority = st.text_input("Seniority (owner, director, manager)")
    departamentos = st.text_input("Departamentos (marketing, sales)")

    # EMPRESAS
    tamaño_min = st.number_input("Empleados mínimo", 0, 1000000, 0)
    tamaño_max = st.number_input("Empleados máximo", 0, 1000000, 0)

    # ENRIQUECIMIENTO / MATCH
    email = st.text_input("Email")
    dominio = st.text_input("Dominio empresa (ej: empresa.com)")

    paginas = st.number_input("Número de páginas (búsquedas)", 1, 20, 1)

    ejecutar = st.form_submit_button("Ejecutar consulta")

# ======================================================
# LÓGICA
# ======================================================

if ejecutar:

    endpoint = ""
    payload = {}

    # ==============================
    # BUSCAR PERSONAS
    # ==============================

    if metodo == "Buscar Personas":

        endpoint = "mixed_people/search"

        payload = {
            "page": 1,
            "per_page": 50,
            "person_titles": [x.strip() for x in cargos.split(",")] if cargos else [],
            "organization_names": [x.strip() for x in empresas.split(",")] if empresas else [],
            "organization_industries": [x.strip() for x in industrias.split(",")] if industrias else [],
            "person_locations": [x.strip() for x in ubicaciones.split(",")] if ubicaciones else [],
            "person_seniorities": [x.strip() for x in seniority.split(",")] if seniority else [],
            "person_departments": [x.strip() for x in departamentos.split(",")] if departamentos else []
        }

    # ==============================
    # BUSCAR EMPRESAS
    # ==============================

    elif metodo == "Buscar Empresas":

        endpoint = "organizations/search"

        payload = {
            "page": 1,
            "per_page": 50,
            "organization_names": [x.strip() for x in empresas.split(",")] if empresas else [],
            "organization_industries": [x.strip() for x in industrias.split(",")] if industrias else [],
            "organization_locations": [x.strip() for x in ubicaciones.split(",")] if ubicaciones else [],
            "employee_count_range": {
                "min": tamaño_min if tamaño_min > 0 else None,
                "max": tamaño_max if tamaño_max > 0 else None
            }
        }

    # ==============================
    # ENRIQUECER PERSONA
    # ==============================

    elif metodo == "Enriquecer Persona":

        if not email:
            st.warning("Debes ingresar un email.")
            st.stop()

        endpoint = "people/enrich"
        payload = {"email": email}

    # ==============================
    # ENRIQUECER EMPRESA
    # ==============================

    elif metodo == "Enriquecer Empresa":

        if not dominio:
            st.warning("Debes ingresar un dominio.")
            st.stop()

        endpoint = "organizations/enrich"
        payload = {"domain": dominio}

    # ==============================
    # MATCH PERSONA
    # ==============================

    elif metodo == "Match Persona por Email":

        if not email:
            st.warning("Debes ingresar un email.")
            st.stop()

        endpoint = "people/match"
        payload = {"email": email}

    # ==============================
    # MATCH EMPRESA
    # ==============================

    elif metodo == "Match Empresa por Dominio":

        if not dominio:
            st.warning("Debes ingresar un dominio.")
            st.stop()

        endpoint = "organizations/match"
        payload = {"domain": dominio}

    if not endpoint:
        st.error("Método inválido.")
        st.stop()

    # ==============================
    # EJECUCIÓN CON PAGINACIÓN
    # ==============================

    resultados_totales = []

    with st.spinner("Consultando Apollo..."):

        if "search" in endpoint:

            for p in range(1, paginas + 1):
                payload["page"] = p
                resultado = ejecutar_post(endpoint, payload)

                if not resultado:
                    break

                if "people" in resultado:
                    resultados_totales.extend(resultado["people"])
                elif "organizations" in resultado:
                    resultados_totales.extend(resultado["organizations"])

        else:
            resultado = ejecutar_post(endpoint, payload)
            if resultado:
                resultados_totales.append(resultado)

    if not resultados_totales:
        st.warning("Sin resultados.")
        st.stop()

    df = pd.json_normalize(resultados_totales)

    st.success(f"Consulta completada. {len(df)} registros obtenidos.")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Descargar CSV",
        data=csv,
        file_name="apollo_resultado.csv",
        mime="text/csv"
    )
