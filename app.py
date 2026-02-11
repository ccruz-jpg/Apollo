import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Apollo Contacts Explorer", layout="wide")

st.title("Apollo Contacts Explorer")

# ---------- API KEY ----------

try:
    APOLLO_API_KEY = "0fl3eqL2h102aiuGCleiPw"
except:
    st.error("API key no encontrada en Streamlit Secrets")
    st.stop()

# ---------- SIDEBAR FILTROS ----------

with st.sidebar:

    st.header("Filtros")

    keyword = st.text_input("Keywords")

    titles = st.text_input(
        "Cargos (separados por coma)",
        placeholder="ceo, founder"
    )

    company = st.text_input("Empresa")

    city = st.text_input("Ciudad")
    country = st.text_input("País")

    verified_email = st.checkbox("Solo emails verificados")
    has_phone = st.checkbox("Solo con teléfono")

    max_pages = st.slider(
        "Páginas a cargar (100 contactos por página)",
        1,
        50,
        5
    )

    search_button = st.button("Buscar contactos")

# ---------- CONSTRUCCIÓN PAYLOAD ----------

def build_payload(page):

    payload = {
        "page": page,
        "per_page": 100,
        "q_keywords": keyword,
        "organization_name": company,
        "city": city,
        "country": country,
    }

    if titles:
        payload["person_titles"] = [
            t.strip() for t in titles.split(",")
        ]

    if verified_email:
        payload["contact_email_status"] = ["verified"]

    return {k: v for k, v in payload.items() if v}

# ---------- API CALL ----------

def fetch_page(page):

    url = "https://api.apollo.io/v1/contacts/search"

    headers = {
        "X-Api-Key": APOLLO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = build_payload(page)

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        st.error(f"Error API: {response.text}")
        return []

    data = response.json()
    contacts = data.get("contacts", [])

    if has_phone:
        contacts = [
            c for c in contacts if c.get("phone_number")
        ]

    return contacts

# ---------- BÚSQUEDA ----------

def search_contacts():

    all_rows = []

    progress = st.progress(0)
    status = st.empty()

    for page in range(1, max_pages + 1):

        status.text(f"Cargando página {page}/{max_pages}")

        contacts = fetch_page(page)

        if not contacts:
            status.text("No hay más resultados disponibles")
            break

        for c in contacts:

            all_rows.append({
                "Nombre": c.get("name"),
                "Empresa": c.get("organization_name"),
                "Email": c.get("email"),
                "Teléfono": c.get("phone_number"),
                "Ciudad": c.get("city"),
                "País": c.get("country"),
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
        st.warning("No se encontraron contactos")
    else:
        st.success(f"{len(df)} contactos encontrados")

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Descargar CSV",
            csv,
            "apollo_contacts.csv",
            "text/csv"
        )
