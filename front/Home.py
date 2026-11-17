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

    response.raise_for_status()
    
    data = response.json()

    if data["status"] == "already_imported":
        st.error(f"API error {data["status"]}")
        st.code(data["message"])
        st.stop()

    df = pd.DataFrame(data["final_df"])

    df = df.fillna("")

    if df is not None:
        edited_df = st.data_editor(
            df,
            width='content',
            num_rows="dynamic",
            key="data_editor"
        )

        if st.button("Enregistrer les données"):
            edited_df = pl.from_pandas(edited_df)
            edited_df = edited_df.with_columns([
                pl.col(col)
                .cast(pl.String)
                .str.replace_all(r"[\s\u00A0\u202F€]", "")
                .str.replace(",", ".")
                .cast(pl.Float64, strict=False)
                .cast(pl.Int64, strict=False)
                .alias(col)

                for col in ["debit_cents", "credit_cents"]
            ])

            payload = {
                "df": edited_df.to_dicts(),
                "file_hash": data["file_hash"],
                "filename": data["filename"]
            }

            save_df = httpx.post(
                f"{API_URL}extract_doc/validate",
                json=payload,
                timeout=600.0
            )

            if save_df.status_code == 422:
                st.error("Erreur de validation API")
                st.json(save_df.json())
                st.stop()

            if save_df.status_code >= 400:
                st.error(f"API error {save_df.status_code}")
                st.code(save_df.text)
                st.stop()

            save_df.raise_for_status()

            result = save_df.json()

            if result["status"] == "success":
                st.success("Transactions enregistrées avec succès !")
                st.write(result["validate_df"])

            elif result["status"] == "already_imported":
                st.warning("Ce fichier a déjà été importé.")
                
            else:
                st.error("Une erreur est survenue pendant la sauvegarde.")


            if result["validate_df"] is not None:
                df = pl.DataFrame(result["validate_df"])
                
                monthly_expenses = (
                    df.with_columns(
                        pl.col("date_valeur")
                        .str.to_date("%Y-%m-%d")
                        .alias("date_valeur")
                    ).with_columns(
                        pl.col("date_valeur").dt.truncate("1mo").alias("mois")
                    )
                    .group_by(["mois", "categorie"])
                    .agg(
                        (pl.col("debit_cents").fill_null(0).sum() / 100)
                        .alias("depenses_euros")
                    )
                    .sort(["mois", "categorie"])
                )

                monthly_summary = (df.with_columns(
                        pl.col("date_valeur")
                        .str.to_date("%Y-%m-%d")
                        .alias("date_valeur")
                    ).with_columns(
                        pl.col("date_valeur").dt.truncate("1mo").alias("mois")
                    )
                    .group_by("mois")
                    .agg([
                        (pl.col("debit_cents").fill_null(0).sum() / 100)
                        .alias("depenses"),

                        (pl.col("credit_cents").fill_null(0).sum() / 100)
                        .alias("revenus")
                    ])
                    .sort("mois")
                )

                kpis = monthly_summary.select([
                    pl.col("depenses").sum().alias("total_expenses"),
                    pl.col("revenus").sum().alias("total_income"),
                    pl.col("depenses").mean().alias("average_expenses")
                ]).row(0, named=True)

                total_expenses = kpis["total_expenses"] or 0
                total_income = kpis["total_income"] or 0

                balance = total_income - total_expenses
                average_expenses = kpis["average_expenses"] or 0

                st.subheader("Indicateurs clés df")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Dépenses totales", f"{total_expenses:,.2f} €")
                col2.metric("Revenus totaux", f"{total_income:,.2f} €")
                col3.metric("Solde net", f"{balance:,.2f} €")
                col4.metric("Dépenses moyennes / mois", f"{average_expenses:,.2f} €")


                def monthly_expenses_chart(df):
                    fig = px.line(
                        df.to_pandas(),
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



                def monthly_category_chart(df):
                    fig = px.bar(
                        df.to_pandas(),
                        x="mois",
                        y="depenses_euros",
                        color="categorie",
                        title="Dépenses mensuelles par catégorie",
                        barmode="stack"
                    )

                    return fig


                def income_vs_expenses_chart(df):
                    fig = px.bar(
                        df.to_pandas(),
                        x="mois",
                        y=["revenus", "depenses"],
                        barmode="group",
                        title="Comparaison revenus / dépenses"
                    )

                    return fig

                st.plotly_chart(
                    monthly_expenses_chart(monthly_summary),
                    width="stretch"
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Analyse détaillée")

                    st.plotly_chart(
                        monthly_category_chart(monthly_expenses),
                        width="stretch"
                    )

                with col2:
                    st.subheader("Revenus vs dépenses")

                    st.plotly_chart(
                        income_vs_expenses_chart(monthly_summary),
                        width="stretch"
                    )