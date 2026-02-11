import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Apollo Advanced Filters", layout="wide")

st.title("Apollo → Filtros Avanzados")

APOLLO_API_KEY = "0fl3eqL2h102aiuGCleiPw"

# ---------- SIDEBAR FILTROS ----------

with st.sidebar:

    st.header("Filtros estilo Apollo")

    keyword = st.text_input("Keywords")

    titles = st.text_input(
        "Cargos (separados por coma)",
        placeholder="ceo, founder"
    )

    company = st.text_input("Empresa")

    city = st.text_input("Ciudad")
    country = st.text_input("País")

    company_size = st.selectbox(
        "Tamaño empresa",
        ["", "1-10", "11-50", "51-200", "201-500", "500+"]
    )

    industry = st.text_input("Industria")

    verified_email = st.checkbox("Solo emails verificados")
    has_phone = st.checkbox("Solo contactos con teléfono")

    max_pages = st.slider("Páginas", 1, 50, 5)

    search_button = st.button("Buscar")


# ---------- API ----------

def build_payload(page):

    payload = {
        "page": page,
        "per_page": 100,
        "q_keywords": keyword,
        "organization_name": company,
        "city": city,
        "country": country,
        "industry": industry,
    }

    if titles:
        payload["person_titles"] = [
            t.strip() for t in titles.split(",")
        ]

    if company_size:
        payload["organization_num_employees_ranges"] = [
            company_size
        ]

    if verified_email:
        payload["contact_email_status"] = ["verified"]

    # limpiar vacíos
    return {k: v for k, v in payload.items() if v}


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

    # filtro local de teléfono
    if has_phone:
        contacts = [
            c for c in contacts if c.get("phone_number")
        ]

    return contacts


def search_contacts():

    all_rows = []

    progress = st.progress(0)
    status = st.empty()

    for page in range(1, max_pages + 1):

        status.text(f"Página {page}/{max_pages}")

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
                "País": c.get("country"),
                "Cargo": c.get("title"),
                "Industria": c.get("organization_industry"),
                "LinkedIn": c.get("linkedin_url")
            })

        progress.progress(page / max_pages)

        time.sleep(0.5)

    return pd.DataFrame(all_rows)


# ---------- EJECUCIÓN ----------

if search_button:

    with st.spinner("Buscando..."):
        df = search_contacts()

    if df.empty:
        st.warning("Sin resultados")
    else:
        st.success(f"{len(df)} contactos")

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Descargar CSV",
            csv,
            "apollo_results.csv",
            "text/csv"
        )
