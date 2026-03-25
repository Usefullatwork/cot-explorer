# COT Explorer — Markedspuls

Trading dashboard: CFTC COT data + FRED macro + SMC analysis + signal push.
Pure Python 3 (stdlib only), vanilla JS frontend, GitHub Pages deployment.

## Build & Test

```bash
pytest                  # Run tests (when tests exist)
ruff check .            # Lint Python files
ruff format .           # Format Python files
python3 fetch_all.py    # Run full analysis pipeline
bash update.sh          # Run complete update + git push
```

## Architecture

### Data Pipeline (update.sh orchestrates in order)

1. `fetch_calendar.py` — ForexFactory economic calendar → `data/calendar/`
2. `fetch_cot.py` — CFTC COT reports (TFF, Legacy, Disaggregated, Supplemental) → `data/`
3. `build_combined.py` — Merge + deduplicate COT datasets → `data/combined/`
4. `fetch_fundamentals.py` — FRED API macro indicators → `data/fundamentals/`
5. `fetch_all.py` — Core analysis engine: prices, SMC zones, confluence scoring → `data/macro/latest.json`
6. `push_signals.py` — Push top setups to Telegram/Discord/Flask
7. `update.sh` — Orchestrates all above + `git push` to GitHub Pages

### Frontend

- `index.html` (830 lines) — Single-page vanilla JS dashboard
- Reads JSON directly from `data/` directory
- No build step, no npm, no bundler, no framework

### Data Sources

| Source | Env Var | Purpose |
|--------|---------|---------|
| TwelveData | `TWELVEDATA_API_KEY` | Forex/commodity prices |
| Finnhub | `FINNHUB_API_KEY` | Real-time index/commodity quotes |
| FRED | `FRED_API_KEY` | Macro indicators (GDP, CPI, NFP) |
| Stooq | (none) | Backup daily price source |
| CFTC | (none) | COT positioning reports |
| ForexFactory | (none) | Economic calendar |

### Signal Push (all optional)

| Env Var | Purpose |
|---------|---------|
| `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID` | Telegram bot alerts |
| `DISCORD_WEBHOOK` | Discord webhook alerts |
| `SCALP_API_KEY` + `FLASK_URL` | Flask signal server |

### Scheduling

Crontab runs `update.sh` 4× daily (07:45, 12:30, 14:15, 17:15 CET) on weekdays.

## File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `fetch_all.py` | 1242 | Core analysis engine (prices, SMC, levels, scoring) |
| `index.html` | 830 | Dashboard frontend (vanilla JS, dark theme) |
| `fetch_fundamentals.py` | 520 | FRED macro data fetcher |
| `smc.py` | 285 | Smart Money Concepts (supply/demand zones, BOS) |
| `fetch_cot.py` | 248 | CFTC COT data fetcher |
| `push_signals.py` | 188 | Signal push (Telegram/Discord/Flask) |
| `build_timeseries.py` | 158 | COT time series builder for charts |
| `fetch_prices.py` | 108 | Price fetcher (TwelveData → Stooq → Yahoo fallback) |
| `build_price_history.py` | 90 | Historical price data builder |
| `fetch_calendar.py` | 65 | ForexFactory calendar scraper |
| `build_combined.py` | 63 | COT dataset merger/deduplicator |
| `update.sh` | 47 | Pipeline orchestrator + git push |

## Key Conventions

- **Pure stdlib** — No pip dependencies in main scripts (only `urllib`, `json`, `os`, `pathlib`, `csv`, `zipfile`)
- **Norwegian labels** — Most code comments, variable names, and UI text are in Norwegian
- **Data dir is large** — `data/` is ~270MB, git-tracked for GitHub Pages
- **No tests yet** — Test infrastructure (pytest) to be added
- **`scalp_edge/`** — Empty Flask stub for signal server (not active)

## Rules

- Read before edit — always read a file before modifying it
- No secrets — never commit .env or API keys
- Stage by name — `git add file.py`, never `git add .`
- 3-strike errors — diagnose, alternative, then stop and ask
- Commit with `-m` — HEREDOC hangs on Windows/MSYS
- Python style — snake_case everywhere, ruff formatting, PEP 8
- Design gate — changes touching 3+ files require the design-first skill
- Test after change — run pytest after every code modification (when tests exist)
