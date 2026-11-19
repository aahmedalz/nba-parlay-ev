import time

import pandas as pd
from nba_api.stats.endpoints import playergamelogs, teamgamelogs

from src.config import MAX_RETRIES, REQUEST_DELAY, REQUEST_TIMEOUT


def _call(endpoint_cls, **kwargs) -> pd.DataFrame:
    """Call an nba_api endpoint with retries + exponential backoff."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = endpoint_cls(timeout=REQUEST_TIMEOUT, **kwargs).get_data_frames()[0]
            time.sleep(REQUEST_DELAY)
            return df
        except Exception as e:
            wait = REQUEST_DELAY * 2 ** attempt
            print(f"  ! {endpoint_cls.__name__} failed ({e.__class__.__name__}), retry {attempt}/{MAX_RETRIES} in {wait:.0f}s")
            time.sleep(wait)
    raise RuntimeError(f"{endpoint_cls.__name__} failed after {MAX_RETRIES} retries: {kwargs}")


def _clean(df: pd.DataFrame, season: str, season_type: str) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    # drop nba_api's rank columns (e.g. pts_rank) - not needed
    df = df[[c for c in df.columns if not c.endswith("_rank")]]
    df["game_date"] = pd.to_datetime(df["game_date"]).dt.date
    df["season"] = season
    df["season_type"] = season_type
    df["is_home"] = df["matchup"].str.contains(" vs. ")
    return df


def fetch_player_logs(season: str, season_type: str) -> pd.DataFrame:
    df = _call(playergamelogs.PlayerGameLogs, season_nullable=season, season_type_nullable=season_type)
    return _clean(df, season, season_type) if not df.empty else df


def fetch_team_logs(season: str, season_type: str) -> pd.DataFrame:
    df = _call(teamgamelogs.TeamGameLogs, season_nullable=season, season_type_nullable=season_type)
    return _clean(df, season, season_type) if not df.empty else df


def build_games(team_logs: pd.DataFrame) -> pd.DataFrame:
    """One row per game: home vs away, final score, margin, total."""
    if team_logs.empty:
        return pd.DataFrame()
    cols = ["game_id", "game_date", "season", "season_type", "team_id", "team_abbreviation", "pts"]
    home = team_logs[team_logs["is_home"]][cols]
    away = team_logs[~team_logs["is_home"]][["game_id", "team_id", "team_abbreviation", "pts"]]
    g = home.merge(away, on="game_id", suffixes=("_home", "_away"))
    g = g.rename(columns={
        "team_id_home": "home_team_id", "team_abbreviation_home": "home_team", "pts_home": "home_pts",
        "team_id_away": "away_team_id", "team_abbreviation_away": "away_team", "pts_away": "away_pts",
    })
    g["home_margin"] = g["home_pts"] - g["away_pts"]
    g["total_pts"] = g["home_pts"] + g["away_pts"]
    g["home_win"] = g["home_margin"] > 0
    return g.sort_values(["game_date", "game_id"]).reset_index(drop=True)
