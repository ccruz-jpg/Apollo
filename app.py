
import streamlit as st
import requests
import pandas as pd
import os

st.title("Apollo → Excel Export Tool")

APOLLO_API_KEY = st.secrets.get("APOLLO_API_KEY")

def fetch_apollo_data(query):
    url = "https://api.apollo.io/v1/mixed_people/search"

    payload = {
        "api_key": APOLLO_API_KEY,
        "q_keywords": query
    }

    response = requests.post(url, json=payload)
    data = response.json()

    people = data.get("people", [])

    rows = []

    for p in people:
        rows.append({
            "Nombre": p.get("name"),
            "Empresa": p.get("organization", {}).get("name"),
            "Email": p.get("email"),
            "Cargo": p.get("title"),
            "LinkedIn": p.get("linkedin_url")
        })

    return pd.DataFrame(rows)

query = st.text_input("Pega la URL o palabras clave de búsqueda")

if st.button("Exportar"):
    with st.spinner("Consultando Apollo..."):
        df = fetch_apollo_data(query)

        if df.empty:
            st.warning("No se encontraron resultados")
        else:
            st.dataframe(df)

            excel_file = "apollo_export.xlsx"
            df.to_excel(excel_file, index=False)

            with open(excel_file, "rb") as f:
                st.download_button(
                    "Descargar Excel",
                    f,
                    file_name=excel_file
                )

            st.success("Exportación lista")
