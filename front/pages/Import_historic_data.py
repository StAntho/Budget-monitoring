import streamlit as st
from dotenv import load_dotenv
import os, httpx
from uploading_file import *

st.set_page_config(
    page_title="Budget monitoring",
    page_icon="💰",
)

st.title("BM - Historic Data importation")

# === API ===
load_dotenv()
API_URL = os.getenv("STREAMLIT_URL_API")

st.markdown("---")

st.markdown("#### Choose your historic file")
uploaded_file = st.file_uploader("Ajouter un nouveau Document au VectorStore", type=["csv", "xlsx", "json", "pdf"])

if uploaded_file:
    file_type = detect_file_type(uploaded_file)
    st.write(f"Type détecté : **{file_type}**")

    if file_type == "csv" or file_type == "xlsx":
        nb_line_rm = st.number_input('Lignes à laquelle commencer', min_value=0, step=1, value=0)
        nb_col_rm = st.number_input('Nombre de colonnes à supprimer', min_value=0, step=1, value=0)
        df = load_file(uploaded_file, file_type)
        df = df.iloc[nb_line_rm:, nb_col_rm:]
        if df.iloc[0].notna().all():
            df.columns = df.iloc[0]
            df = df.iloc[1:, :]
            st.write(df.columns)
            # df.columns.name = None
            df = df.rename_axis(None, axis=1)

        if df is not None:
            st.success("Fichier chargé avec succès")
            st.dataframe(df)

            if st.button("Envoyer"):
                df = df.where(df.notna(), None)
                df = df.fillna("")
                payload = {
                    "data": df.to_dict(orient="records")
                }

                response = httpx.post(
                    f"{API_URL}import_doc/process",
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 422:
                    st.error("Erreur de validation API")
                    st.json(response.json())
                    st.stop()

                if response.status_code >= 400:
                    st.error(f"API error {response.status_code}")
                    st.code(response.text)
                    st.stop()

                response.raise_for_status()

                result = response.json()
                st.write(result)

st.markdown("---")

collections = httpx.get(
    f"{API_URL}import_doc/get_datas_vs",
    timeout=30.0,
)
collections = collections.json()
collections = [c["name"] for c in collections["collections"]]


st.markdown("#### Search for document")
collection = st.selectbox("Selectionner la collection", options=collections)
query = st.text_input("Chercher un doc dans la base vectorielle")

if query is not None and st.button("Rechercher"):
    payload = {
        "collection": collection,
        "query": query
    }
    retrieves = httpx.post(
        f"{API_URL}import_doc/request_vs",
        json=payload,
        timeout=30.0,
    )

    if retrieves.status_code != 200:
        st.error(
            f"Erreur API {retrieves.status_code}: "
            f"{retrieves.text}"
        )
        st.stop()

    st.write(retrieves)

    # st.write(result_retrieve)
    retrieves.raise_for_status()

    # result_retreive = retrieves.json()
    st.write(retrieves.status_code)
    st.write(retrieves.text)