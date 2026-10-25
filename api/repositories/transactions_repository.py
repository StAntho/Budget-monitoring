from pathlib import Path

import duckdb
import polars as pl

class TransactionRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path

        database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        with duckdb.connect(str(database_path)) as connect:
            connect.execute("""
                CREATE TABLE IF NOT EXISTS imports (
                    file_hash VARCHAR PRIMARY KEY,
                    filename VARCHAR NOT NULL,
                    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connect.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    file_hash VARCHAR NOT NULL,
                    date DATE,
                    date_valeur DATE,
                    operation VARCHAR,
                    debit_cents BIGINT,
                    credit_cents BIGINT,
                    devise VARCHAR,
                    source_page INTEGER,
                    confidence DOUBLE,
                    status VARCHAR,
                    "Sous-catégorie" VARCHAR,
                    categorie VARCHAR,
                    "Sub-categorie" VARCHAR
                )
            """)

    def is_imported(self, file_hash: str) -> bool:
        with duckdb.connect(str(self.database_path)) as connect:
            result = connect.execute(
                """
                SELECT COUNT(*)
                FROM imports
                WHERE file_hash = ?
                """,
                [file_hash],
            ).fetchone()

        return result[0] > 0

    def save_import(
        self,
        file_hash: str,
        filename: str,
        dataframe: pl.DataFrame,
    ) -> bool:
        with duckdb.connect(str(self.database_path)) as connect:
            connect.execute("BEGIN TRANSACTION")

            try:
                # Enregistrement du fichier.
                inserted = connect.execute(
                    """
                    INSERT INTO imports (file_hash, filename)
                    VALUES (?, ?)
                    ON CONFLICT (file_hash) DO NOTHING
                    RETURNING file_hash
                    """,
                    [file_hash, filename],
                ).fetchone()

                # Le fichier existe déjà.
                if inserted is None:
                    connect.execute("ROLLBACK")
                    return False

                # Ajouter les données de l'import.
                connect.register("incoming_transactions", dataframe)

                connect.execute("""
                    INSERT INTO transactions (
                        file_hash,
                        date,
                        date_valeur,
                        operation,
                        debit_cents,
                        credit_cents,
                        devise,
                        source_page,
                        confidence,
                        status,
                        "Sous-catégorie",
                        categorie,
                        "Sub-categorie"
                    )
                    SELECT
                        file_hash,
                        date,
                        date_valeur,
                        operation,
                        debit_cents,
                        credit_cents,
                        devise,
                        source_page,
                        confidence,
                        status,
                        "Sous-catégorie",
                        categorie,
                        "Sub-categorie"
                    FROM incoming_transactions
                """) if "file_hash" in dataframe.columns else connect.execute("""
                    INSERT INTO transactions (
                        file_hash,
                        date,
                        date_valeur,
                        operation,
                        debit_cents,
                        credit_cents,
                        devise,
                        source_page,
                        confidence,
                        status,
                        "Sous-catégorie",
                        categorie,
                        "Sub-categorie"
                    )
                    SELECT
                        ?,
                        date,
                        date_valeur,
                        operation,
                        debit_cents,
                        credit_cents,
                        devise,
                        source_page,
                        confidence,
                        status,
                        "Sous-catégorie",
                        categorie,
                        "Sub-categorie"
                    FROM incoming_transactions
                """, [file_hash])

                connect.execute("COMMIT")
                return True

            except Exception:
                connect.execute("ROLLBACK")
                raise