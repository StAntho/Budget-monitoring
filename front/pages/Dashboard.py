import streamlit as st
from dotenv import load_dotenv
import os, httpx, sys
from pathlib import Path
import pandas as pd
import polars as pl
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "api"))
from api.repositories.analytics_repository import AnalyticsRepository
import plotly.express as px

st.set_page_config(
    page_title="Budget monitoring",
    page_icon="💰",
    layout="wide"
)

st.title("BM - Dashboard")

get_connection = AnalyticsRepository.get_data_connection()
if get_connection["total"] == 0:

    st.info(
        "Aucune transaction disponible. "
        "Importez un relevé bancaire pour afficher vos statistiques."
    )

else:
    monthly_expenses = AnalyticsRepository.get_monthly_expenses_by_category()
    monthly_summary = AnalyticsRepository.get_monthly_summary()
    expenses_by_person_per_category = AnalyticsRepository.get_expenses_by_person_and_category()

    st.write(expenses_by_person_per_category)
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

    def format_euros(cents: int) -> str:
        euros = cents / 100
        return f"{euros:,.2f} €".replace(",", " ").replace(".", ",")


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



    col1, col2 = st.columns(2)


    with col1:

        def monthly_expenses_chart(df):
            fig = px.line(
                df,
                x="mois",
                y="depenses",
                markers=True,
                title="Évolution des dépenses mensuelles"
            )

            fig.update_layout(
                yaxis_title="Dépenses (€)",
                xaxis_title="Mois",
                template="plotly_white"
            )

            return fig


        st.plotly_chart(
            monthly_expenses_chart(monthly_summary),
            width='content',
        )

    with col2:
        def expenses_by_category_chart(df):
            fig = px.pie(
                df,
                names="categorie",
                values="depenses_euros",
                title="Répartition des dépenses par catégorie",
                hole=0.45
            )
            return fig

        st.plotly_chart(
            expenses_by_category_chart(
                monthly_expenses.group_by("categorie").agg(
                    pl.col("depenses_euros").sum()
                )
            ),
            width='content',
        )
    # with col2:

    #     st.plotly_chart(
    #         expenses_by_category_chart(category_data),
    #         use_container_width=True
    #     )


    st.subheader("Analyse détaillée")

    def monthly_category_chart(df):

        fig = px.bar(
            df,
            x="mois",
            y="depenses_euros",
            color="categorie",
            title="Dépenses mensuelles par catégorie",
            barmode="stack"
        )

        return fig

    st.plotly_chart(
        monthly_category_chart(monthly_expenses),
        width='content',
    )


    st.divider()



    st.subheader("Revenus vs dépenses")

    def income_vs_expenses_chart(df):

        fig = px.bar(
            df,
            x="mois",
            y=["revenus", "depenses"],
            barmode="group",
            title="Comparaison revenus / dépenses"
        )

        return fig

    st.plotly_chart(
        income_vs_expenses_chart(monthly_summary),
        width='content',
    )



    st.subheader("Données mensuelles")

    st.dataframe(
        monthly_summary,
        width='content',
    )