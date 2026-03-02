import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json
import tempfile

st.set_page_config(page_title="Apollo Extractor", layout="wide")

APOLLO_API_KEY = "KqTN83fY1U5Ic4O4-FhRzQ"

# ==================================================
# APOLLO SEARCH
# ==================================================

@st.cache_data(show_spinner=False)
def search_apollo(job_titles, industries, locations, total_pages):

    url = "https://api.apollo.io/v1/mixed_people/search"
    all_people = []

    for page in range(1, total_pages + 1):

        payload = {
            "api_key": APOLLO_API_KEY,
            "page": page,
            "person_titles": job_titles,
            "organization_industries": industries,
            "person_locations": locations
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            st.error(response.text)
            break

        data = response.json()
        people = data.get("people", [])

        if not people:
            break

        all_people.extend(people)

    return all_people


# ==================================================
# DRIVE UPLOAD (PYDRIVE2)
# ==================================================

def upload_to_drive(file_bytes, filename):

    service_account_info = st.secrets["gcp_service_account"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(json.dumps(service_account_info).encode())
        tmp_path = tmp.name

    gauth = GoogleAuth()
    gauth.settings['client_config_file'] = tmp_path
    gauth.ServiceAuth()

    drive = GoogleDrive(gauth)

    file_drive = drive.CreateFile({"title": filename})
    file_drive.content = file_bytes.read()
    file_drive.Upload()

    return file_drive['alternateLink']


# ==================================================
# UI
# ==================================================

st.title("Apollo Lead Extractor")

with st.sidebar:
    job_titles = st.text_input("Job Titles (coma)")
    industries = st.text_input("Industrias (coma)")
    locations = st.text_input("Ubicaciones (coma)")
    pages = st.number_input("Páginas", 1, 20, 1)

if st.button("Buscar"):

    results = search_apollo(
        [x.strip() for x in job_titles.split(",")],
        [x.strip() for x in industries.split(",")] if industries else [],
        [x.strip() for x in locations.split(",")] if locations else [],
        pages
    )

    if not results:
        st.warning("Sin resultados")
        st.stop()

    df = pd.json_normalize(results)

    st.dataframe(df, use_container_width=True)

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Descargar Excel",
            data=output,
            file_name="apollo_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col2:
        if st.button("Subir a Drive"):
            link = upload_to_drive(output, "apollo_results.xlsx")
            st.success(f"Archivo subido: {link}")
