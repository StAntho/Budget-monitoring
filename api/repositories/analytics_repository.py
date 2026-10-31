from database.connection import get_connection
import polars as pl

class AnalyticsRepository:

    def get_monthly_expenses_by_category(self):
        with get_connection() as conect:
            result = conect.execute("""
                SELECT
                    DATE_TRUNC('month', date_valeur) AS mois,
                    categorie,
                    SUM(COALESCE(debit_cents, 0)) / 100.0
                        AS depenses_euros
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
