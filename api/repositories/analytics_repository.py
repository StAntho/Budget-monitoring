from database.connection import get_connection
import polars as pl

class AnalyticsRepository:

    def get_monthly_expenses_by_category():
        with get_connection() as conect:
            result = conect.execute("""
                SELECT
                    DATE_TRUNC('month', date_valeur) AS mois,
                    categorie,
                    CAST(
                        SUM(COALESCE(debit_cents, 0))
                        AS DECIMAL(18, 2)
                    ) / 100 AS depenses_euros
                FROM transactions
                GROUP BY
                    mois,
                    categorie
                ORDER BY
                    mois,
                    categorie
            """)

            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()

            return pl.DataFrame(
                rows,
                schema=columns,
                orient="row"
            )


    def get_monthly_summary() -> pl.DataFrame:
        with get_connection() as conect:

            df = conect.execute("""
                SELECT
                    DATE_TRUNC('month', date_valeur) AS mois,
                    SUM(COALESCE(debit_cents, 0)) / 100.0
                        AS depenses,
                    SUM(COALESCE(credit_cents, 0)) / 100.0
                        AS revenus
                FROM transactions
                GROUP BY mois
                ORDER BY mois
            """)
            
            columns = [desc[0] for desc in df.description]
            rows = df.fetchall()

            return pl.DataFrame(
                rows,
                schema=columns,
                orient="row"
            )