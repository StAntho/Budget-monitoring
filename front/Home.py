import streamlit as st
from dotenv import load_dotenv
import os, httpx
import pandas as pd

st.set_page_config(
    page_title="Budget monitoring",
    page_icon="💰",
)

st.title("BM - Data extraction")


# === API ===
load_dotenv()
API_URL = os.getenv("STREAMLIT_URL_API")

st.markdown("#### Choose a file or folder")
choice_type = st.radio(
    "What's type of download",
    ("Files", "Directory"),
    index=0,
    horizontal=True
)

mapping = {
    "Files": True,
    "Directory": "directory",
}

download_type = mapping.get(choice_type)

uploaded_files = st.file_uploader(
    f"Choose a {choice_type}", 
    accept_multiple_files=download_type,
    type="pdf"
)

if uploaded_files:
    st.write(f"Found {len(uploaded_files)} files in the folder:")
    for file in uploaded_files:
        st.write(file.name)

    files = [
        ("pdf_files", (f.name, f.getvalue(), f.type))
        for f in uploaded_files
    ]

    response = httpx.post(
        f"{API_URL}extract_doc/extract",
        files=files,
        timeout=600.0
    )

    st.write(response)
    response.raise_for_status()
    
    data = response.json()
    df = pd.DataFrame(data["final_df"])

    df = df.fillna("")

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )