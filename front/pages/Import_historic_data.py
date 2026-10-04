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

            dataset = []
            for i, (_, row) in enumerate(df.iterrows()):
                row_dict = {}
                for col in df.columns:
                    row_dict[col] = row.get(col)
                dataset.append(row_dict)
            # dataset = df.to_dict(orient="records")
            st.write(dataset)

st.markdown("---")