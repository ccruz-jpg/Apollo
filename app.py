import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# =========================================================
# CONFIGURACIÓN INICIAL
# =========================================================

st.set_page_config(
    page_title="Extractor de Leads - Apollo",
    layout="wide"
)

APOLLO_API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

# =========================================================
# FUNCIÓN PARA CONSULTAR APOLLO
# =========================================================

@st.cache_data(show_spinner=False)
def buscar_en_apollo(cargos, industrias, ubicaciones, total_paginas):

    url = "https://api.apollo.io/v1/mixed_people/search"

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }

    todos_los_resultados = []

    for pagina in range(1, total_paginas + 1):

        payload = {
            "page": pagina,
            "per_page": 50,
            "person_titles": cargos,
            "organization_industries": industrias,
            "person_locations": ubicaciones
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            st.error(f"Error en página {pagina}: {response.text}")
            break

        data = response.json()
        personas = data.get("people", [])

        if not personas:
            break

        todos_los_resultados.extend(personas)

    return todos_los_resultados


# =========================================================
# INTERFAZ
# =========================================================

st.title("🚀 Extractor de Leads desde Apollo")
st.markdown("Consulta Apollo usando filtros personalizados y descarga los resultados en Excel.")

with st.sidebar:

    st.header("🔎 Filtros de búsqueda")

    cargos = st.text_input("Cargos (separados por coma)", placeholder="Ej: CEO, Marketing Manager")
    industrias = st.text_input("Industrias (separadas por coma)", placeholder="Ej: Software, Fintech")
    ubicaciones = st.text_input("Ubicaciones (separadas por coma)", placeholder="Ej: United States, Spain")
    total_paginas = st.number_input("Número de páginas a consultar", min_value=1, max_value=20, value=1)

# =========================================================
# BOTÓN DE BÚSQUEDA
# =========================================================

if st.button("🔍 Buscar leads"):

    if not cargos:
        st.warning("Debes ingresar al menos un cargo.")
        st.stop()

    with st.spinner("Consultando Apollo..."):

        resultados = buscar_en_apollo(
            [c.strip() for c in cargos.split(",")],
            [i.strip() for i in industrias.split(",")] if industrias else [],
            [u.strip() for u in ubicaciones.split(",")] if ubicaciones else [],
            total_paginas
        )

        if not resultados:
            st.warning("No se encontraron resultados con esos filtros.")
            st.stop()

        df = pd.json_normalize(resultados)

        st.success(f"Se encontraron {len(df)} leads.")
        st.dataframe(df, use_container_width=True)

        # =====================================================
        # EXPORTAR A EXCEL
        # =====================================================

        archivo_excel = BytesIO()
        df.to_excel(archivo_excel, index=False)
        archivo_excel.seek(0)

        st.download_button(
            label="📥 Descargar resultados en Excel",
            data=archivo_excel,
            file_name="leads_apollo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
