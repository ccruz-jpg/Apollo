import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Apollo Mixed Search", layout="wide")
st.title("Apollo Global Leads Search")

APOLLO_API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

# ----------- FILTROS -----------

with st.sidebar:

    st.header("Filtros")

    titles = st.text_input("Cargos (comma separated)", "founder,ceo")
    location = st.text_input("Ubicación", "Bogota, Colombia")
    keyword = st.text_input("Keyword empresa", "security")
    employees = st.selectbox("Tamaño empresa", ["0,10","11,50","51,200","201,500","500,1000"])
    verified_email = st.checkbox("Solo emails verificados", True)

    max_pages = st.slider("Páginas", 1, 20, 3)

    run = st.button("Buscar leads")


# ----------- REQUEST -----------

def fetch_page(page):

    url = "https://api.apollo.io/v1/mixed_people/search"

    headers = {
        "X-Api-Key": APOLLO_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "page": page,
        "person_titles": [t.strip() for t in titles.split(",")],
        "person_locations": [location],
        "organization_num_employees_ranges": [employees],
        "q_organization_keyword_tags": [keyword],
    }

    if verified_email:
        payload["contact_email_status"] = ["verified"]

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        st.error(response.text)
        return []

    return response.json().get("people", [])


# ----------- LOOP -----------

def search():

    results = []
    progress = st.progress(0)

    for page in range(1, max_pages+1):

        people = fetch_page(page)

        if not people:
            break

        for p in people:
            results.append({
                "Nombre": p.get("name"),
                "Cargo": p.get("title"),
                "Empresa": p.get("organization", {}).get("name"),
                "Ciudad": p.get("city"),
                "Email": p.get("email"),
                "LinkedIn": p.get("linkedin_url")
            })

        progress.progress(page/max_pages)
        time.sleep(1)

    return pd.DataFrame(results)


# ----------- UI -----------

if run:

    with st.spinner("Buscando en Apollo..."):
        df = search()

    if df.empty:
        st.warning("Sin resultados (probablemente falta permiso API)")
    else:
        st.success(f"{len(df)} leads encontrados")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode()
        st.download_button("Descargar CSV", csv, "apollo_leads.csv")
