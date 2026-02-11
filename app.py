import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Apollo Filtros", layout="wide")

st.title("Apollo → Búsqueda con Filtros")

APOLLO_API_KEY = "0fl3eqL2h102aiuGCleiPw"


# ---------- FORMULARIO DE FILTROS ----------

with st.sidebar:

    st.header("Filtros")

    keyword = st.text_input("Keyword / Nombre")
    company = st.text_input("Empresa")
    title = st.text_input("Cargo")
    city = st.text_input("Ciudad")
    email = st.text_input("Email")

    max_pages = st.slider(
        "Número de páginas",
        min_value=1,
        max_value=50,
        value=5
    )

    search_button = st.button("Buscar contactos")


# ---------- API ----------

def fetch_page(page):

    url = "https://api.apollo.io/v1/contacts/search"

    headers = {
        "X-Api-Key": APOLLO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "page": page,
        "per_page": 100,
        "q_keywords": keyword,
        "organization_name": company,
        "person_titles": [title] if title else None,
        "city": city,
        "email": email
    }

    # limpiar campos vacíos
    payload = {k: v for k, v in payload.items() if v}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        st.error(f"Error API: {response.text}")
        return []

    data = response.json()
    return data.get("contacts", [])


def search_contacts():

    all_rows = []

    progress = st.progress(0)
    status = st.empty()

    for page in range(1, max_pages + 1):

        status.text(f"Descargando página {page}/{max_pages}...")

        contacts = fetch_page(page)

        if not contacts:
            break

        for c in contacts:

            all_rows.append({
                "Nombre": c.get("name"),
                "Empresa": c.get("organization_name"),
                "Email": c.get("email"),
                "Teléfono": c.get("phone_number"),
                "Ciudad": c.get("city"),
                "Cargo": c.get("title"),
                "LinkedIn": c.get("linkedin_url")
            })

        progress.progress(page / max_pages)

        time.sleep(0.5)

    return pd.DataFrame(all_rows)


# ---------- EJECUCIÓN ----------

if search_button:

    with st.spinner("Buscando contactos..."):
        df = search_contacts()

    if df.empty:
        st.warning("No se encontraron resultados")
    else:
        st.success(f"{len(df)} contactos encontrados")

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Descargar CSV",
            csv,
            "apollo_resultados.csv",
            "text/csv"
        )
