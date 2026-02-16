import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Apollo Contact Finder", layout="wide")
st.title("Apollo Contact Finder")

APOLLO_API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

# ------------------ FILTROS ------------------

with st.sidebar:

    st.header("Filtros")

    keywords = st.text_input("Texto libre (nombre, empresa, cargo)")
    titles = st.text_input("Cargos (coma): CEO, Founder")
    cities = st.text_input("Ciudades (coma): Bogota, Funza")
    company_contains = st.text_input("Empresa contiene")
    only_email = st.checkbox("Solo con email")
    only_phone = st.checkbox("Solo con teléfono")

    pages = st.slider("Páginas", 1, 50, 5)

    run = st.button("Buscar")

# ------------------ API ------------------

def fetch_page(page):

    url = "https://api.apollo.io/v1/contacts/search"

    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "page": page,
        "per_page": 100
    }

    r = requests.post(url, json=payload, headers=headers)

    if r.status_code != 200:
        st.error(r.text)
        return []

    return r.json().get("contacts", [])

# ------------------ FILTRADO LOCAL ------------------

def match(contact):

    text = " ".join([
        str(contact.get("name","")),
        str(contact.get("title","")),
        str(contact.get("organization_name","")),
        str(contact.get("city",""))
    ]).lower()

    if keywords and keywords.lower() not in text:
        return False

    if titles:
        valid = [t.strip().lower() for t in titles.split(",")]
        if not any(t in text for t in valid):
            return False

    if cities:
        valid = [c.strip().lower() for c in cities.split(",")]
        if not any(c in text for c in valid):
            return False

    if company_contains:
        if company_contains.lower() not in str(contact.get("organization_name","")).lower():
            return False

    if only_email and not contact.get("email"):
        return False

    if only_phone and not contact.get("phone_number"):
        return False

    return True

# ------------------ BUSQUEDA ------------------

def search():

    rows = []
    progress = st.progress(0)

    for page in range(1, pages+1):

        contacts = fetch_page(page)

        if not contacts:
            break

        for c in contacts:
            if match(c):
                rows.append({
                    "Nombre": c.get("name"),
                    "Cargo": c.get("title"),
                    "Empresa": c.get("organization_name"),
                    "Ciudad": c.get("city"),
                    "Email": c.get("email"),
                    "Teléfono": c.get("phone_number"),
                    "LinkedIn": c.get("linkedin_url")
                })

        progress.progress(page/pages)
        time.sleep(0.4)

    return pd.DataFrame(rows)

# ------------------ UI ------------------

if run:

    with st.spinner("Buscando..."):
        df = search()

    st.success(f"{len(df)} resultados")

    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.download_button(
            "Descargar CSV",
            df.to_csv(index=False).encode(),
            "contacts.csv"
        )
