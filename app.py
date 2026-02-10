import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Apollo Contacts Export", layout="wide")

st.title("Apollo → Exportación Masiva de Contactos")

APOLLO_API_KEY = "0fl3eqL2h102aiuGCleiPw"


def fetch_page(page):

    url = "https://api.apollo.io/v1/contacts/search"

    headers = {
        "X-Api-Key": APOLLO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "page": page,
        "per_page": 100
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        st.error(f"Error API: {response.text}")
        return []

    data = response.json()
    return data.get("contacts", [])


def export_contacts(max_pages):

    all_rows = []

    progress = st.progress(0)
    status = st.empty()

    for page in range(1, max_pages + 1):

        status.text(f"Descargando página {page}/{max_pages}...")

        contacts = fetch_page(page)

        if not contacts:
            status.text("No hay más contactos.")
            break

        for c in contacts:
            all_rows.append({
                "Nombre": c.get("name"),
                "Empresa": c.get("organization_name"),
                "Email": c.get("email"),
                "Cargo": c.get("title"),
                "LinkedIn": c.get("linkedin_url")
            })

        progress.progress(page / max_pages)

        time.sleep(0.5)

    return pd.DataFrame(all_rows)


max_pages = st.slider(
    "Número de páginas a exportar (100 contactos por página)",
    min_value=1,
    max_value=100,
    value=10
)

estimated = max_pages * 100
st.info(f"Estimado: ~{estimated} contactos")

if st.button("Exportar contactos"):

    with st.spinner("Exportando contactos..."):

        df = export_contacts(max_pages)

    if df.empty:
        st.warning("No se encontraron contactos")
    else:
        st.success(f"Exportados {len(df)} contactos")

        st.dataframe(df, use_container_width=True)

        excel_file = "apollo_contacts_export.xlsx"
        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as f:
            st.download_button(
                "Descargar Excel",
                f,
                file_name=excel_file
            )
