import duckdb
import pandas as pd

from src.config import DB_PATH, DATA_DIR


def connect() -> duckdb.DuckDBPyConnection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def replace_season(con, table: str, df: pd.DataFrame, season: str, season_type: str) -> int:
    """Idempotent load: delete this season/season_type, then insert fresh rows."""
    if df.empty:
        return 0
    con.register("incoming", df)
    con.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM incoming LIMIT 0")
    con.execute(f"DELETE FROM {table} WHERE season = ? AND season_type = ?", [season, season_type])
    con.execute(f"INSERT INTO {table} BY NAME SELECT * FROM incoming")
    con.unregister("incoming")
    return len(df)
