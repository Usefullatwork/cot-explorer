#!/usr/bin/env python3
"""Tekniske indikatorer — ATR, EMA, tidsrammekonvertering og sesjonsstatus."""
from datetime import datetime, timezone


def calc_atr(rows, n=14):
    """Beregner Average True Range over n perioder."""
    if len(rows) < n + 1:
        return None
    trs = [
        max(rows[i][0] - rows[i][1],
            abs(rows[i][0] - rows[i - 1][2]),
            abs(rows[i][1] - rows[i - 1][2]))
        for i in range(1, len(rows))
    ]
    return sum(trs[-n:]) / n


def calc_ema(closes, n=9):
    """Beregner Exponential Moving Average over n perioder."""
    if len(closes) < n + 1:
        return None
    k = 2 / (n + 1)
    ema = sum(closes[:n]) / n
    for c in closes[n:]:
        ema = c * k + ema * (1 - k)
    return ema


def to_4h(rows_1h):
    """Konverterer 1H candles til 4H ved \u00e5 gruppere 4 og 4."""
    out = []
    for i in range(0, len(rows_1h) - 3, 4):
        grp = rows_1h[i:i + 4]
        h = max(r[0] for r in grp)
        l = min(r[1] for r in grp)
        c = grp[-1][2]
        out.append((h, l, c))
    return out


def get_pdh_pdl_pdc(daily):
    """Returnerer Previous Day High, Low, Close."""
    if len(daily) < 2:
        return None, None, None
    return daily[-2][0], daily[-2][1], daily[-2][2]


def get_pwh_pwl(daily):
    """Returnerer Previous Week High og Low (siste 5 handelsdager)."""
    if len(daily) < 10:
        return None, None
    week = daily[-8:-1]
    return max(r[0] for r in week), min(r[1] for r in week)


def get_session_status():
    """Returnerer aktiv handelssesjon basert p\u00e5 CET-tid."""
    h = datetime.now(timezone.utc).hour
    m = datetime.now(timezone.utc).minute
    cet = (h * 60 + m + 60) % (24 * 60)  # UTC+1
    ch = cet // 60
    sessions = []
    if 7 * 60 <= cet < 12 * 60:
        sessions.append("London")
    if 13 * 60 <= cet < 17 * 60:
        sessions.append("NY Overlap")
    if 8 * 60 <= cet < 12 * 60:
        sessions.append("London Fix")
    if not sessions:
        sessions.append("Off-session")
    return {
        "active": any(s != "Off-session" for s in sessions),
        "label": " / ".join(sessions),
        "cet_hour": ch,
    }
