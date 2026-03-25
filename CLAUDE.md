# COT Explorer — Markedspuls

Trading dashboard: CFTC COT data + FRED macro + SMC analysis + signal push.
Pure Python 3 (stdlib only), vanilla JS frontend, GitHub Pages deployment.

## Build & Test

```bash
pytest -v               # Run 43 tests
ruff check .            # Lint Python files
ruff format .           # Format Python files
python3 fetch_all.py    # Run full analysis pipeline
bash update.sh          # Run complete update + git push
bash update.sh --dry-run  # Run pipeline without git push
```

## Architecture

### Data Pipeline (update.sh orchestrates in order)

1. `fetch_calendar.py` — ForexFactory economic calendar -> `data/calendar/`
2. `fetch_cot.py` — CFTC COT reports (TFF, Legacy, Disaggregated, Supplemental) -> `data/`
3. `build_combined.py` — Merge + deduplicate COT datasets -> `data/combined/`
4. `fetch_fundamentals.py` — FRED API macro indicators -> `data/fundamentals/`
5. `fetch_all.py` — Core orchestrator: prices, SMC zones, confluence scoring -> `data/macro/latest.json`
6. `push_signals.py` — Push top setups to Telegram/Discord/Flask
7. `update.sh` — Orchestrates all above + git push (gated on zero failures)

### Module Structure (extracted from fetch_all.py monolith)

```
config.py          <- (none)          Constants, instruments, API keys, mapping dicts
indicators.py      <- (none)          ATR, EMA, session status, timeframe conversion
levels.py          <- indicators      Support/resistance detection, merging, formatting
price_fetchers.py  <- config          Yahoo, Twelvedata, Stooq, Finnhub, FRED fetchers
trade_setup.py     <- levels          Level-to-level trade setup with structural SL
sentiment.py       <- config, price_fetchers  Fear&Greed, news, macro indicators
scoring.py         <- (none)          12-point confluence scoring
macro_output.py    <- sentiment       Dollar Smile, VIX regime, final JSON assembly
fetch_all.py       <- all + smc       Orchestrator (461 lines)
```

### Frontend

- `index.html` (105 lines) — HTML structure only
- `css/dashboard.css` (168 lines) — Dark theme styles
- `js/dashboard.js` (555 lines) — Charts, panels, data loading
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

Crontab runs `update.sh` 4x daily (07:45, 12:30, 14:15, 17:15 CET) on weekdays.

## File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `fetch_all.py` | 461 | Orchestrator (imports 8 modules) |
| `config.py` | 110 | Instruments, API keys, mapping dicts |
| `price_fetchers.py` | 174 | Yahoo/Twelvedata/Stooq/Finnhub/FRED fetchers |
| `trade_setup.py` | 174 | Level-to-level trade setup generator |
| `sentiment.py` | 168 | Fear&Greed, news, macro indicators, conflicts |
| `levels.py` | 165 | Support/resistance detection and merging |
| `indicators.py` | 76 | ATR, EMA, session status |
| `scoring.py` | 60 | 12-point confluence scoring |
| `macro_output.py` | 87 | Dollar Smile, VIX regime, JSON assembly |
| `fetch_fundamentals.py` | 357 | FRED macro data orchestrator |
| `indicator_scoring.py` | 329 | FRED indicator scoring functions |
| `fred_client.py` | 37 | FRED API client |
| `smc.py` | 285 | Smart Money Concepts (Pine Script port) |
| `fetch_cot.py` | 248 | CFTC COT data fetcher |
| `push_signals.py` | 188 | Signal push (Telegram/Discord/Flask) |
| `build_timeseries.py` | 158 | COT time series builder for charts |
| `fetch_prices.py` | 108 | Standalone price checker (diagnostic) |
| `build_price_history.py` | 90 | Historical price data builder |
| `fetch_calendar.py` | 65 | ForexFactory calendar scraper |
| `build_combined.py` | 63 | COT dataset merger/deduplicator |
| `update.sh` | 68 | Pipeline orchestrator + git push |
| `index.html` | 105 | HTML structure (CSS/JS extracted) |
| `css/dashboard.css` | 168 | Dashboard styles (dark theme) |
| `js/dashboard.js` | 555 | Dashboard logic (charts, panels) |

## Key Conventions

- **Pure stdlib** — No pip dependencies in main scripts (only `urllib`, `json`, `os`, `pathlib`, `csv`, `zipfile`)
- **Norwegian labels** — Most code comments, variable names, and UI text are in Norwegian
- **Logging** — All scripts use `logging` module (not `print()`), except smc.py
- **Data dir is large** — `data/` is ~270MB, git-tracked for GitHub Pages
- **`scalp_edge/`** — Empty Flask stub for signal server (not active)

## Rules

- Read before edit — always read a file before modifying it
- No secrets — never commit .env or API keys
- Stage by name — `git add file.py`, never `git add .`
- 3-strike errors — diagnose, alternative, then stop and ask
- Commit with `-m` — HEREDOC hangs on Windows/MSYS
- Python style — snake_case everywhere, ruff formatting, PEP 8
- Design gate — changes touching 3+ files require the design-first skill
- Test after change — run `pytest -v` after every code modification
- Max 500 lines per file — split if exceeding
