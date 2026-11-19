# NBA Parlay EV Analyzer

Estimates the **true probability** of NBA bets and parlays, accounts for correlation between legs, and compares it to sportsbook odds to answer one question: **is this parlay worth it?**

## Roadmap
- [x] **Phase 1a** – Data pipeline: team + player game logs (2018-19 → present) in DuckDB
- [ ] **Phase 1b** – Historical odds + injury data
- [ ] **Phase 2** – Leg models (game winner/spread/total, player props as full distributions)
- [ ] **Phase 3** – Calibration (Brier, log loss, reliability curves)
- [ ] **Phase 4** – Parlay engine (Monte Carlo with correlated legs → true prob, fair odds, EV, Kelly)
- [ ] **Phase 5** – Backtest vs closing lines (CLV)
- [ ] **Phase 6** – Streamlit app

## Setup
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.pull_data      # first full pull
python -m scripts.check_data     # sanity check
```
Daily refresh: `python -m scripts.pull_data --current`

## Data
| Table | Grain |
|---|---|
| `team_game_logs` | one row per team per game |
| `games` | one row per game (home/away, score, margin, total) |
| `player_game_logs` | one row per player per game |

Source: stats.nba.com via [`nba_api`](https://github.com/swar/nba_api).
