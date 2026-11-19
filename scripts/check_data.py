"""Sanity-check the database after a pull."""
from src.db import connect

con = connect()

print("\nGames per season:")
print(con.sql("""
    SELECT season, season_type, COUNT(*) AS games,
           ROUND(AVG(total_pts), 1) AS avg_total,
           ROUND(AVG(home_win::INT), 3) AS home_win_pct
    FROM games GROUP BY ALL ORDER BY season, season_type
""").df().to_string(index=False))

print("\nTop scorers, current season:")
print(con.sql("""
    SELECT player_name, team_abbreviation AS team, COUNT(*) AS gp,
           ROUND(AVG(pts), 1) AS ppg,
           ROUND(AVG((pts >= 30)::INT), 3) AS pct_30plus
    FROM player_game_logs
    WHERE season = (SELECT MAX(season) FROM player_game_logs) AND season_type = 'Regular Season'
    GROUP BY ALL HAVING gp >= 5 ORDER BY ppg DESC LIMIT 15
""").df().to_string(index=False))
