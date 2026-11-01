import streamlit as st
from dotenv import load_dotenv
import os, httpx, sys
from pathlib import Path
import pandas as pd
import polars as pl
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "api"))
os.chdir(ROOT_DIR / "api")
from api.repositories.analytics_repository import AnalyticsRepository
import plotly.express as px

st.set_page_config(
    page_title="Budget monitoring",
    page_icon="💰",
    layout="wide"
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


monthly_expenses = AnalyticsRepository.get_monthly_expenses_by_category()
monthly_summary = AnalyticsRepository.get_monthly_summary()

st.write(monthly_summary)
kpis = monthly_summary.select(
    pl.col("depenses").sum().alias("total_expenses"),
    pl.col("revenus").sum().alias("total_income"),
    pl.col("depenses").mean().alias("average_expenses")
).row(0, named=True)


total_expenses = kpis["total_expenses"]
total_income = kpis["total_income"]
balance = total_income - total_expenses
average_expenses = kpis["average_expenses"]

st.subheader("Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Dépenses totales",
    f"{total_expenses:,.2f} €"
)

col2.metric(
    "Revenus totaux",
    f"{total_income:,.2f} €"
)

col3.metric(
    "Solde net",
    f"{balance:,.2f} €"
)

col4.metric(
    "Dépenses moyennes / mois",
    f"{average_expenses:,.2f} €"
)

st.divider()
