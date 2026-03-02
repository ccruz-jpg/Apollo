import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# =============================
# CONFIG
# =============================

APOLLO_API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

# =============================
# FUNCION CONSULTA APOLLO
# =============================

def search_apollo(job_titles, industries, locations, page=1):

    url = "https://api.apollo.io/v1/mixed_people/search"

    payload = {
        "api_key": APOLLO_API_KEY,
        "page": page,
        "person_titles": job_titles,
        "organization_industries": industries,
        "person_locations": locations
    }

    response = requests.post(url, json=payload)
    return response.json()


# =============================
# GOOGLE DRIVE UPLOAD
# =============================

def upload_to_drive(file_bytes, filename):

    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )

    service = build("drive", "v3", credentials=credentials)

    file_metadata = {
        "name": filename
    }

    media = MediaIoBaseUpload(file_bytes,
                               mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return file.get("id")


# =============================
# STREAMLIT UI
# =============================

st.title("Apollo Lead Extractor")

with st.sidebar:
    st.header("Filtros")

    job_titles = st.text_input("Job Titles (separados por coma)")
    industries = st.text_input("Industrias (coma)")
    locations = st.text_input("Ubicaciones (coma)")
    page = st.number_input("Página", min_value=1, value=1)

if st.button("Buscar en Apollo"):

    with st.spinner("Consultando Apollo..."):

        data = search_apollo(
            job_titles.split(","),
            industries.split(","),
            locations.split(","),
            page
        )

        people = data.get("people", [])

        if not people:
            st.warning("No se encontraron resultados")
        else:
            df = pd.json_normalize(people)

            st.success(f"{len(df)} resultados encontrados")
            st.dataframe(df)

            # =====================
            # EXPORTAR A EXCEL
            # =====================

            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)

            st.download_button(
                label="Descargar Excel",
                data=output,
                file_name="apollo_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # =====================
            # SUBIR A DRIVE
            # =====================

            if st.button("Subir a Google Drive"):
                file_id = upload_to_drive(output, "apollo_results.xlsx")
                st.success(f"Archivo subido. ID: {file_id}")
