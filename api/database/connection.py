import duckdb

DB_PATH = "data/budget.duckdb"

def get_connection():
    return duckdb.connect(DB_PATH)