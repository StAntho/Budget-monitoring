import streamlit as st
import os, httpx, sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "api"))
from api.repositories.analytics_repository import AnalyticsRepository
import plotly.express as px
from dashboard_filters import render_filters
from dashboard_data import *
from dashboard_kpis import *
from dashboard_charts import *

st.set_page_config(
    page_title="Budget monitoring",
    page_icon="💰",
    layout="wide"
)

st.title("BM - Dashboard test")
st.caption("Vue globale de votre situation financière")

transactions = AnalyticsRepository.get_all_transactions()


df = load_dashboard_data()
if df.is_empty():

    st.info(
        "Aucune transaction disponible. "
        "Importez un relevé bancaire pour afficher vos statistiques."
    )

    st.stop()

df = get_dashboard_data(df)

filtered_df = render_filters(df)
if filtered_df.is_empty():
    st.warning(
        "Aucune transaction ne correspond aux filtres sélectionnés."
    )

    st.stop()

st.caption(
    f"{filtered_df.height:,} transactions correspondant aux filtres."
)


kpis = calculate_kpis(filtered_df)
render_kpis(kpis)
st.divider()


st.subheader("Évolution financière")
col1, col2 = st.columns(2)
with col1:
    render_monthly_expenses(filtered_df)
with col2:
    render_income_vs_expenses(filtered_df)
st.divider()


st.subheader("Analyse des dépenses")
col1, col2 = st.columns(2)
with col1:
    render_expenses_by_category(filtered_df)
with col2:
    render_expenses_by_person(filtered_df)
render_monthly_category(filtered_df)
st.divider()


st.subheader("Analyse par personne et catégorie")
render_person_category_heatmap(filtered_df)
st.divider()

st.subheader("Détail des transactions")
st.dataframe(
    filtered_df.sort("date_valeur", descending=True),
    use_container_width=True,
    hide_index=True
)