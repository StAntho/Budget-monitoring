import streamlit as st
import polars as pl


def render_filters(df: pl.DataFrame) -> pl.DataFrame:

    st.sidebar.header("Filtres")

    if df.is_empty():
        return df

    df = df.filter(
        pl.col("date_valeur").is_not_null()
    )

    if df.is_empty():
        st.warning("Aucune date valide dans les transactions.")
        return df

    min_date = df["date_valeur"].min()
    max_date = df["date_valeur"].max()

    if min_date is None or max_date is None:
        st.warning("Impossible de déterminer la période disponible.")
        return df

    min_date = df["date_valeur"].min()
    max_date = df["date_valeur"].max()

    selected_dates = st.sidebar.date_input(
        "Période",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    persons = sorted(
        df["personne"].unique().to_list()
    )

    selected_persons = st.sidebar.multiselect(
        "Personnes",
        options=persons,
        default=persons
    )

    categories = sorted(
        df["categorie"].unique().to_list()
    )

    selected_categories = st.sidebar.multiselect(
        "Catégories",
        options=categories,
        default=categories
    )

    transaction_types = sorted(
        df["type"].unique().to_list()
    )

    selected_types = st.sidebar.multiselect(
        "Type de transaction",
        options=transaction_types,
        default=transaction_types
    )

    filtered_df = df.filter(
        pl.col("personne").is_in(selected_persons)
        & pl.col("categorie").is_in(selected_categories)
        & pl.col("type").is_in(selected_types)
    )

    if len(selected_dates) == 2:

        start_date, end_date = selected_dates

        filtered_df = filtered_df.filter(
            pl.col("date_valeur").is_between(
                start_date,
                end_date,
                closed="both"
            )
        )

    return filtered_df