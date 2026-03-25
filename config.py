#!/usr/bin/env python3
"""Konfigurasjon for COT Explorer — instrumenter, API-nøkler og datakildekart."""
import os
from pathlib import Path

BASE = Path(__file__).parent / "data"
OUT = BASE / "macro" / "latest.json"

TWELVEDATA_API_KEY = os.environ.get("TWELVEDATA_API_KEY", "")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")

INSTRUMENTS = [
    {"key": "EURUSD", "navn": "EUR/USD", "symbol": "EURUSD=X", "label": "Valuta", "kat": "valuta", "klasse": "A", "session": "London 08:00\u201312:00 CET"},
    {"key": "USDJPY", "navn": "USD/JPY", "symbol": "JPY=X", "label": "Valuta", "kat": "valuta", "klasse": "A", "session": "London 08:00\u201312:00 CET"},
    {"key": "GBPUSD", "navn": "GBP/USD", "symbol": "GBPUSD=X", "label": "Valuta", "kat": "valuta", "klasse": "A", "session": "London 08:00\u201312:00 CET"},
    {"key": "AUDUSD", "navn": "AUD/USD", "symbol": "AUDUSD=X", "label": "Valuta", "kat": "valuta", "klasse": "A", "session": "London 08:00\u201312:00 CET"},
    {"key": "Gold", "navn": "Gull", "symbol": "GC=F", "label": "R\u00e5vare", "kat": "ravarer", "klasse": "B", "session": "London Fix 10:30 / NY Fix 15:00 CET"},
    {"key": "Silver", "navn": "S\u00f8lv", "symbol": "SI=F", "label": "R\u00e5vare", "kat": "ravarer", "klasse": "B", "session": "London Fix 10:30 / NY Fix 15:00 CET"},
    {"key": "Brent", "navn": "Brent", "symbol": "BZ=F", "label": "R\u00e5vare", "kat": "ravarer", "klasse": "B", "session": "London Fix 10:30 / NY Fix 15:00 CET"},
    {"key": "WTI", "navn": "WTI", "symbol": "CL=F", "label": "R\u00e5vare", "kat": "ravarer", "klasse": "B", "session": "London Fix 10:30 / NY Fix 15:00 CET"},
    {"key": "SPX", "navn": "S&P 500", "symbol": "^GSPC", "label": "Aksjer", "kat": "aksjer", "klasse": "C", "session": "NY Open 14:30\u201317:00 CET"},
    {"key": "NAS100", "navn": "Nasdaq", "symbol": "^NDX", "label": "Aksjer", "kat": "aksjer", "klasse": "C", "session": "NY Open 14:30\u201317:00 CET"},
    {"key": "VIX", "navn": "VIX", "symbol": "^VIX", "label": "Vol", "kat": "aksjer", "klasse": "C", "session": "NY Open 14:30\u201317:00 CET"},
    {"key": "DXY", "navn": "DXY", "symbol": "DX-Y.NYB", "label": "Valuta", "kat": "valuta", "klasse": "A", "session": "London 08:00\u201312:00 CET"},
]

# Kun symboler bekreftet tilgjengelig p\u00e5 Twelvedata gratis-plan
TD_FREE_SYMBOLS = {"EURUSD=X", "JPY=X", "GBPUSD=X", "AUDUSD=X", "GC=F",
                   "HYG", "TIP", "EEM"}

TWELVEDATA_MAP = {
    "EURUSD=X": "EUR/USD",
    "JPY=X": "USD/JPY",
    "GBPUSD=X": "GBP/USD",
    "AUDUSD=X": "AUD/USD",
    "GC=F": "XAU/USD",
    "HYG": "HYG",
    "TIP": "TIP",
    "EEM": "EEM",
}

TD_INTERVAL = {"1d": "1day", "15m": "15min", "60m": "1h"}
TD_SIZE = {"1y": 365, "5d": 500, "60d": 500, "30d": 35}

# Stooq-symboler (ingen API-n\u00f8kkel, n\u00e6r sanntid i markedstid)
STOOQ_MAP = {
    "EURUSD=X": "eurusd",
    "JPY=X": "usdjpy",
    "GBPUSD=X": "gbpusd",
    "AUDUSD=X": "audusd",
    "GC=F": "xauusd",
    "SI=F": "xagusd",
    "BZ=F": "co.f",
    "CL=F": "cl.f",
    "^GSPC": "^spx",
    "^NDX": "^ndx",
    "^VIX": "^vix",
    "DX-Y.NYB": "dxy.f",
    "HG=F": "hg.f",
    "HYG": "hyg.us",
    "TIP": "tip.us",
    "EEM": "eem.us",
}
STOOQ_DAYS = {"1y": 400, "30d": 35, "5d": 7}

# Finnhub sanntidspriser for indekser og r\u00e5varer
FINNHUB_QUOTE_MAP = {
    "^GSPC": "^GSPC",
    "^NDX": "^NDX",
    "^VIX": "^VIX",
    "SI=F": "SI1!",
    "BZ=F": "UKOIL",
    "CL=F": "USOIL",
    "HG=F": "HG1!",
}

# Nyhetssentiment: hvilken retning bekrefter risk_on / risk_off per instrument
NEWS_CONFIRMS_MAP = {
    "SPX": ("bull", "bear"),
    "NAS100": ("bull", "bear"),
    "Gold": ("bear", "bull"),
    "Silver": ("bear", "bull"),
    "EURUSD": ("bull", "bear"),
    "GBPUSD": ("bull", "bear"),
    "AUDUSD": ("bull", "bear"),
    "USDJPY": ("bull", "bear"),
    "DXY": ("bear", "bull"),
    "Brent": (None, None),
    "WTI": (None, None),
    "VIX": ("bear", "bull"),
}

COT_MAP = {
    "EURUSD": "euro fx",
    "USDJPY": "japanese yen",
    "GBPUSD": "british pound",
    "Gold": "gold",
    "Silver": "silver",
    "Brent": "crude oil, light sweet",
    "WTI": "crude oil, light sweet",
    "SPX": "s&p 500 consolidated",
    "NAS100": "nasdaq mini",
    "DXY": "usd index",
}

# Rate-limit konstanter
TWELVEDATA_RATE_LIMIT_SECONDS = 8

# ATR-toleranse for is_at_level
ATR_TIGHT_MULTIPLIERS = {1: 0.30, 2: 0.35, 3: 0.45}
