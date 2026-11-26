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


def render_expenses_by_category(df: pl.DataFrame):
    data = (
        df.filter(pl.col("type") == "Dépense")
        .group_by("categorie")
        .agg(
            pl.col("montant_euros").sum().alias("depenses")
        )
        .sort("depenses", descending=True)
    )

    fig = px.pie(
        data,
        names="categorie",
        values="depenses",
        hole=0.5,
        title="Répartition des dépenses par catégorie"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def render_monthly_category(df: pl.DataFrame):
    data = (
        df.filter(pl.col("type") == "Dépense")
        .group_by([
            pl.col("date_valeur").dt.truncate("1mo").alias("mois"),
            "categorie"
        ])
        .agg(
            pl.col("montant_euros").sum().alias("depenses")
        )
        .sort("mois")
    )

    fig = px.bar(
        data,
        x="mois",
        y="depenses",
        color="categorie",
        barmode="stack",
        title="Dépenses mensuelles par catégorie"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def render_expenses_by_person(df: pl.DataFrame):
    data = (
        df.filter(pl.col("type") == "Dépense")
        .group_by("personne")
        .agg(
            pl.col("montant_euros").sum().alias("depenses")
        )
        .sort("depenses", descending=True)
    )

    fig = px.bar(
        data,
        x="personne",
        y="depenses",
        color="personne",
        title="Dépenses par personne"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def render_person_category_heatmap(df: pl.DataFrame):
    data = (
        df.filter(pl.col("type") == "Dépense")
        .group_by(["personne", "categorie"])
        .agg(
            pl.col("montant_euros").sum().alias("depenses")
        )
    )

    fig = px.density_heatmap(
        data,
        x="categorie",
        y="personne",
        z="depenses",
        histfunc="sum",
        color_continuous_scale="Blues",
        title="Répartition des dépenses par personne et catégorie"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )