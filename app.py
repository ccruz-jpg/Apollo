import streamlit as st
import requests
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Apollo Extractor", layout="wide")

APOLLO_API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

# ==================================================
# FUNCIÓN CONSULTA APOLLO
# ==================================================

@st.cache_data(show_spinner=False)
def search_apollo(job_titles, industries, locations, total_pages):

    url = "https://api.apollo.io/v1/mixed_people/search"
    all_people = []

    for page in range(1, total_pages + 1):

        payload = {
            "api_key": APOLLO_API_KEY,
            "page": page,
            "person_titles": job_titles,
            "organization_industries": industries,
            "person_locations": locations
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            st.error(f"Error en página {page}: {response.text}")
            break

        data = response.json()
        people = data.get("people", [])

        if not people:
            break

        all_people.extend(people)

    return all_people


# ==================================================
# UI
# ==================================================

st.title("🚀 Apollo Lead Extractor")
st.markdown("Consulta Apollo y descarga los resultados en Excel.")

with st.sidebar:
    st.header("Filtros")

    job_titles = st.text_input("Job Titles (separados por coma)")
    industries = st.text_input("Industrias (coma)")
    locations = st.text_input("Ubicaciones (coma)")
    pages = st.number_input("Número de páginas", min_value=1, max_value=20, value=1)

if st.button("Buscar en Apollo"):

    if not job_titles:
        st.warning("Debes ingresar al menos un Job Title")
        st.stop()

    with st.spinner("Consultando Apollo..."):

        results = search_apollo(
            [x.strip() for x in job_titles.split(",")],
            [x.strip() for x in industries.split(",")] if industries else [],
            [x.strip() for x in locations.split(",")] if locations else [],
            pages
        )

        if not results:
            st.warning("No se encontraron resultados.")
            st.stop()

        df = pd.json_normalize(results)

        st.success(f"Se encontraron {len(df)} leads.")
        st.dataframe(df, use_container_width=True)

        # Exportar a Excel
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Descargar Excel",
            data=output,
            file_name="apollo_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
