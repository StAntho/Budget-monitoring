import polars as pl
import plotly.express as px
import streamlit as st


def get_monthly_summary(df: pl.DataFrame):
    return (
        df.group_by(pl.col("date_valeur").dt.truncate("1mo"))
        .agg([
            pl.col("montant_euros")
            .filter(pl.col("type") == "Revenu")
            .sum()
            .alias("revenus"),

            pl.col("montant_euros")
            .filter(pl.col("type") == "Dépense")
            .sum()
            .alias("depenses")
        ])
        .sort("date_valeur")
        .rename({"date_valeur": "mois"})
    )


def render_monthly_expenses(df: pl.DataFrame):
    monthly = get_monthly_summary(df)

    fig = px.line(
        monthly,
        x="mois",
        y="depenses",
        markers=True,
        title="Évolution des dépenses mensuelles"
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Dépenses (€)",
        xaxis_title="Mois"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def render_income_vs_expenses(df: pl.DataFrame):
    monthly = get_monthly_summary(df)

    fig = px.bar(
        monthly,
        x="mois",
        y=["revenus", "depenses"],
        barmode="group",
        title="Revenus vs dépenses"
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Montant (€)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
