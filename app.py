import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Apollo Console", layout="wide")
st.title("🚀 Apollo Console")

API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

BASE_URL = "https://api.apollo.io/v1"

def buscar_empresas(industria, ubicacion, paginas):

    endpoint = "organizations/search"
    url = f"{BASE_URL}/{endpoint}"

    resultados_totales = []

    for pagina in range(1, paginas + 1):

        payload = {
            "page": pagina,
            "per_page": 50,
            "organization_industries": [industria] if industria else [],
            "organization_locations": [ubicacion] if ubicacion else []
        }

        response = requests.post(url, json=payload, headers=HEADERS)

        if response.status_code != 200:
            st.error(response.text)
            return None

        data = response.json()
        organizaciones = data.get("organizations", [])

        if not organizaciones:
            break

        resultados_totales.extend(organizaciones)

    return resultados_totales


with st.form("form"):

    industria = st.text_input("Industria")
    ubicacion = st.text_input("Ubicación")
    paginas = st.number_input("Número de páginas", 1, 10, 2)

    ejecutar = st.form_submit_button("Buscar")

if ejecutar:

    with st.spinner("Consultando Apollo..."):

        datos = buscar_empresas(industria, ubicacion, paginas)

    if not datos:
        st.warning("No se encontraron resultados.")
        st.stop()

    df = pd.json_normalize(datos)

    # Eliminar duplicados por ID
    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"])

    st.success(f"Se encontraron {len(df)} empresas únicas.")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Descargar CSV",
        data=csv,
        file_name="empresas_apollo.csv",
        mime="text/csv"
    )
