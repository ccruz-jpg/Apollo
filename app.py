
import streamlit as st
import requests
import pandas as pd
import time

st.title("Apollo → Exportación Masiva (1000+ Leads)")

APOLLO_API_KEY = "0fl3eqL2h102aiuGCleiPw"

def fetch_page(query, page):
    url = "https://api.apollo.io/v1/mixed_people/search"

    payload = {
        "api_key": APOLLO_API_KEY,
        "q_keywords": query,
        "page": page
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        st.error(f"Error API: {response.text}")
        return []

    data = response.json()
    return data.get("people", [])


def export_massive(query, max_pages):
    all_rows = []

    progress = st.progress(0)
    status = st.empty()

    for page in range(1, max_pages + 1):
        status.text(f"Descargando página {page}/{max_pages}...")

        people = fetch_page(query, page)

        if not people:
            break

        for p in people:
            all_rows.append({
                "Nombre": p.get("name"),
                "Empresa": p.get("organization", {}).get("name"),
                "Email": p.get("email"),
                "Cargo": p.get("title"),
                "LinkedIn": p.get("linkedin_url")
            })

        progress.progress(page / max_pages)

        # Evitar rate limits
        time.sleep(1)

    return pd.DataFrame(all_rows)


query = st.text_input("Palabras clave de búsqueda (ej: security founder bogota)")

max_pages = st.slider(
    "Número de páginas a exportar (≈25 leads por página)",
    min_value=1,
    max_value=50,
    value=10
)

estimated = max_pages * 25
st.info(f"Estimado: ~{estimated} leads")

if st.button("Exportar masivo"):

    if not query:
        st.warning("Introduce una búsqueda")
    else:
        with st.spinner("Exportando leads..."):
            df = export_massive(query, max_pages)

        if df.empty:
            st.warning("No se encontraron resultados")
        else:
            st.success(f"Exportados {len(df)} leads")

            st.dataframe(df)

            excel_file = "apollo_massive_export.xlsx"
            df.to_excel(excel_file, index=False)

            with open(excel_file, "rb") as f:
                st.download_button(
                    "Descargar Excel",
                    f,
                    file_name=excel_file
                )
