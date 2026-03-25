#!/usr/bin/env python3
"""Priskilder — Twelvedata, Stooq, Yahoo, Finnhub og FRED med fallback-kjede."""
import json
import logging
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from config import (
    FINNHUB_API_KEY,
    FINNHUB_QUOTE_MAP,
    STOOQ_DAYS,
    STOOQ_MAP,
    TD_FREE_SYMBOLS,
    TD_INTERVAL,
    TD_SIZE,
    TWELVEDATA_API_KEY,
    TWELVEDATA_MAP,
    TWELVEDATA_RATE_LIMIT_SECONDS,
)

log = logging.getLogger(__name__)


def fetch_yahoo(symbol, interval="1d", range_="1y"):
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{urllib.parse.quote(symbol)}?interval={interval}&range={range_}"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        res = d["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        rows = [
            (h, l, c)
            for h, l, c in zip(q.get("high", []), q.get("low", []), q.get("close", []))
            if h and l and c
        ]
        return rows
    except Exception as e:
        log.error("FEIL %s (%s): %s", symbol, interval, e)
        return []


def fetch_twelvedata(symbol, interval="1d", outputsize=365):
    """Henter OHLC fra Twelvedata. Returnerer [(h,l,c), ...] eldst\u2192nyest."""
    if not TWELVEDATA_API_KEY or symbol not in TD_FREE_SYMBOLS:
        return []
    td_sym = TWELVEDATA_MAP.get(symbol, symbol)
    td_int = TD_INTERVAL.get(interval, interval)
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={urllib.parse.quote(td_sym)}"
        f"&interval={td_int}&outputsize={outputsize}"
        f"&apikey={TWELVEDATA_API_KEY}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            d = json.loads(r.read())
        if d.get("status") == "error":
            log.warning("TD %s: %s", td_sym, d.get("message", "ukjent feil"))
            return []
        rows = []
        for v in reversed(d.get("values", [])):
            try:
                rows.append((float(v["high"]), float(v["low"]), float(v["close"])))
            except (ValueError, KeyError):
                continue
        time.sleep(TWELVEDATA_RATE_LIMIT_SECONDS)
        return rows
    except Exception as e:
        log.error("TD FEIL %s (%s): %s", td_sym, interval, e)
        return []


def fetch_stooq(symbol, range_="1y"):
    """Henter daglig OHLC fra Stooq (ingen API-n\u00f8kkel, n\u00e6r sanntid).
    Returnerer [(h,l,c), ...] eldst\u2192nyest, eller [] ved feil."""
    stooq_sym = STOOQ_MAP.get(symbol)
    if not stooq_sym:
        return []
    days = STOOQ_DAYS.get(range_, 400)
    d2 = datetime.now(timezone.utc).strftime("%Y%m%d")
    d1 = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y%m%d")
    url = f"https://stooq.com/q/d/l/?s={stooq_sym}&i=d&d1={d1}&d2={d2}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read().decode(errors="replace")
        lines = text.strip().split("\n")
        rows = []
        for line in lines[1:]:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            try:
                h, l, c = float(parts[2]), float(parts[3]), float(parts[4])
                if h and l and c:
                    rows.append((h, l, c))
            except (ValueError, KeyError):
                continue
        return rows
    except Exception as e:
        log.error("Stooq FEIL %s: %s", stooq_sym, e)
        return []


def fetch_finnhub_quote(symbol):
    """Henter sanntidspris (h,l,c) fra Finnhub for indekser og r\u00e5varer."""
    if not FINNHUB_API_KEY:
        return None
    fh_sym = FINNHUB_QUOTE_MAP.get(symbol)
    if not fh_sym:
        return None
    url = (
        f"https://finnhub.io/api/v1/quote"
        f"?symbol={urllib.parse.quote(fh_sym)}&token={FINNHUB_API_KEY}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
        c, h, l = d.get("c", 0), d.get("h", 0), d.get("l", 0)
        if c and h and l:
            return (h, l, c)
        return None
    except Exception as e:
        log.error("FH FEIL %s: %s", fh_sym, e)
        return None


def fetch_fred(series_id):
    """Henter siste daglige verdi fra FRED (Federal Reserve)."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            lines = r.read().decode().strip().split("\n")
        for line in reversed(lines[1:]):
            parts = line.strip().split(",")
            if len(parts) == 2 and parts[1] not in (".", ""):
                return float(parts[1])
        return None
    except Exception as e:
        log.error("FRED %s FEIL: %s", series_id, e)
        return None


def fetch_prices(symbol, interval, range_or_size):
    """Prioritet: Twelvedata (forex/gull) \u2192 Stooq (daglig) \u2192 Yahoo.
    Oppdaterer siste bar med Finnhub sanntidspris hvis tilgjengelig."""
    if TWELVEDATA_API_KEY and symbol in TD_FREE_SYMBOLS:
        rows = fetch_twelvedata(symbol, interval, TD_SIZE.get(range_or_size, 365))
        if rows:
            if interval == "1d":
                qt = fetch_finnhub_quote(symbol)
                if qt:
                    rows[-1] = qt
            return rows
    if interval == "1d":
        rows = fetch_stooq(symbol, range_or_size)
        if rows:
            qt = fetch_finnhub_quote(symbol)
            if qt:
                rows[-1] = qt
            return rows
    return fetch_yahoo(symbol, interval, range_or_size)
