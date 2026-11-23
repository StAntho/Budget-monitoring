import polars as pl
import streamlit as st


def calculate_kpis(df: pl.DataFrame) -> dict:
    if df.is_empty():
        return {
            "revenus": 0,
            "depenses": 0,
            "solde": 0,
            "taux_epargne": 0,
            "nb_transactions": 0,
            "depense_moyenne": 0,
            "depenses_mensuelles": 0
        }

    kpis = df.select(
        pl.col("montant_euros")
        .filter(pl.col("type") == "Revenu")
        .sum()
        .alias("revenus"),

        pl.col("montant_euros")
        .filter(pl.col("type") == "Dépense")
        .sum()
        .alias("depenses"),

        pl.col("montant_euros")
        .filter(pl.col("type") == "Dépense")
        .mean()
        .alias("depense_moyenne"),

        pl.len().alias("nb_transactions")
    ).row(0, named=True)

    revenus = kpis["revenus"] or 0
    depenses = kpis["depenses"] or 0

    solde = revenus - depenses

    taux_epargne = (
        solde / revenus * 100
        if revenus > 0 else 0
    )

    monthly = (
        df.filter(pl.col("type") == "Dépense")
        .group_by(pl.col("date_valeur").dt.truncate("1mo"))
        .agg(pl.col("montant_euros").sum())
    )

    depenses_mensuelles = (
        monthly["montant_euros"].mean()
        if not monthly.is_empty()
        else 0
    )

    return {
        "revenus": revenus,
        "depenses": depenses,
        "solde": solde,
        "taux_epargne": taux_epargne,
        "nb_transactions": kpis["nb_transactions"],
        "depense_moyenne": kpis["depense_moyenne"] or 0,
        "depenses_mensuelles": depenses_mensuelles
    }


def format_euros(value):
    return f"{value:,.2f} €".replace(
        ",", " "
    ).replace(".", ",")


def render_kpis(kpis: dict):
    st.subheader("Indicateurs clés")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Revenus",
        format_euros(kpis["revenus"])
    )

    col2.metric(
        "Dépenses",
        format_euros(kpis["depenses"])
    )

    col3.metric(
        "Solde net",
        format_euros(kpis["solde"])
    )

    col4.metric(
        "Taux d'épargne",
        f'{kpis["taux_epargne"]:.1f} %'
    )

    col5, col6, col7 = st.columns(3)

    col5.metric(
        "Dépenses moyennes / mois",
        format_euros(kpis["depenses_mensuelles"])
    )

    col6.metric(
        "Dépense moyenne / transaction",
        format_euros(kpis["depense_moyenne"])
    )

    col7.metric(
        "Nombre de transactions",
        kpis["nb_transactions"]
    )