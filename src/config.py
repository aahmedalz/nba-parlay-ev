from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "nba.duckdb"

# Seasons to pull (NBA format "YYYY-YY")
FIRST_SEASON = 2018
CURRENT_SEASON = 2026  # 2026-27 season


def season_str(start_year: int) -> str:
    return f"{start_year}-{str(start_year + 1)[-2:]}"


ALL_SEASONS = [season_str(y) for y in range(FIRST_SEASON, CURRENT_SEASON + 1)]
SEASON_TYPES = ["Regular Season", "Playoffs"]

# Seconds to wait between NBA API calls (stats.nba.com rate-limits hard)
REQUEST_DELAY = 1.5
REQUEST_TIMEOUT = 60
MAX_RETRIES = 4
