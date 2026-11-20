from database.connection import get_connection
import polars as pl

class AnalyticsRepository:

    @staticmethod
    def get_data_connection():

        with get_connection() as connect:

            table = connect.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = 'transactions'
            """).fetchone()[0]

            if not table:
                return {
                    "total": 0,
                    "dates_valides": 0,
                    "debits": 0,
                    "credits": 0,
                    "categories": 0,
                    "personnes": 0
                }

            result = connect.execute("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(date_valeur) AS dates_valides,
                    COUNT(debit_cents) AS debits,
                    COUNT(credit_cents) AS credits,
                    COUNT(categorie) AS categories,
                    COUNT(who) AS personnes
                FROM transactions
            """).fetchone()

            return {
                "total": result[0],
                "dates_valides": result[1],
                "debits": result[2],
                "credits": result[3],
                "categories": result[4],
                "personnes": result[5]
            }

    @staticmethod
    def get_all_transactions() -> pl.DataFrame:
        connection = AnalyticsRepository.get_data_connection()

        query = """
            SELECT
                date_valeur AS date,
                who,
                categorie,
                debit_cents AS debit,
                credit_cents AS credit,
            FROM transactions
        """

        return pl.read_database(
            query=query,
            connection=connection["connection"]
        )

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


    def get_expenses_by_person_and_category() -> pl.DataFrame:
        with get_connection() as connect:

            query = """
                SELECT
                    COALESCE(who, 'Non renseigné') AS personne,
                    COALESCE(categorie, 'Non catégorisé') AS categorie,
                    SUM(debit_cents) / 100.0 AS depenses_euros,
                    COUNT(*) AS nombre_transactions
                FROM transactions
                WHERE debit_cents > 0
                GROUP BY
                    who,
                    categorie
                ORDER BY
                    personne,
                    depenses_euros DESC
            """

            return connect.sql(query).pl()
