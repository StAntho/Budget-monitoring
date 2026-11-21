import streamlit as st
import polars as pl
from api.repositories.analytics_repository import AnalyticsRepository


@st.cache_data(ttl=300, show_spinner="Chargement des transactions...")
def load_dashboard_data() -> pl.DataFrame:
    df = AnalyticsRepository.get_all_transactions()

    if df.is_empty():
        return df

    df = df.with_columns(
        pl.col("date_valeur").cast(pl.Date),
        pl.col("who").fill_null("Non renseigné"),
        pl.col("categorie").fill_null("Non catégorisé"),
        (pl.col("debit_cents") / 100).alias("debit_euros"),
        (pl.col("credit_cents") / 100).alias("credit_euros"),
    )

    df = df.with_columns(
        pl.when(pl.col("credit_cents") > 0).then(pl.lit("Revenu")).when(pl.col("debit_cents") > 0).then(pl.lit("Dépense")).otherwise(pl.lit("Inconnu")).alias("type"),
    )

    df = df.with_columns(
        pl.when(pl.col("type") == "Revenu").then(pl.col("credit_euros")).when(pl.col("type") == "Dépense").then(pl.col("debit_euros")).otherwise(0).alias("montant_euros")
    )

    df = df.rename({"who": "personne"})
    
    return df


def get_dashboard_data(df: pl.DataFrame) -> pl.DataFrame:

    if df.is_empty():
        return df

    return df.with_columns(
        pl.col("date_valeur").dt.strftime("%Y-%m").alias("mois")
    )