"""Pull NBA team + player game logs into DuckDB.

Usage:
    python -m scripts.pull_data              # all seasons (first run, ~5 min)
    python -m scripts.pull_data --current    # current season only (daily refresh)
    python -m scripts.pull_data --seasons 2024-25 2025-26
"""
import argparse

from src.config import ALL_SEASONS, SEASON_TYPES
from src.db import connect, replace_season
from src.ingest import build_games, fetch_player_logs, fetch_team_logs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--current", action="store_true", help="only the current season")
    p.add_argument("--seasons", nargs="+", help='e.g. 2024-25 2025-26')
    args = p.parse_args()

    seasons = [ALL_SEASONS[-1]] if args.current else (args.seasons or ALL_SEASONS)
    con = connect()

    for season in seasons:
        for st in SEASON_TYPES:
            print(f"{season} {st}")
            team = fetch_team_logs(season, st)
            if team.empty:
                print("  (no games yet)")
                continue
            n_t = replace_season(con, "team_game_logs", team, season, st)
            n_g = replace_season(con, "games", build_games(team), season, st)
            n_p = replace_season(con, "player_game_logs", fetch_player_logs(season, st), season, st)
            print(f"  team rows {n_t:,} | games {n_g:,} | player rows {n_p:,}")

    con.close()
    print("Done.")


if __name__ == "__main__":
    main()
