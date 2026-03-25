#!/usr/bin/env python3
"""Sentiment — Fear & Greed, nyhetssentiment, makroindikatorer og konflikter."""
import json
import logging
import re
import urllib.request

from config import NEWS_CONFIRMS_MAP
from price_fetchers import fetch_fred, fetch_prices, fetch_yahoo

log = logging.getLogger(__name__)


def fetch_fear_greed():
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://edition.cnn.com/markets/fear-and-greed",
            "Origin": "https://edition.cnn.com",
        })
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
        return {
            "score": round(d["fear_and_greed"]["score"], 1),
            "rating": d["fear_and_greed"]["rating"],
        }
    except Exception as e:
        log.error("Fear&Greed FEIL: %s", e)
        return None


def fetch_news_sentiment():
    """Henter RSS-nyheter (Google News + BBC), scorer risk-on/risk-off n\u00f8kkelord."""
    RISK_ON = [
        "peace", "ceasefire", "deal", "agreement", "truce", "treaty",
        "stimulus", "rate cut", "rate cuts", "recovery", "trade deal",
        "tariff pause", "tariff reduction", "tariff removed", "de-escalation",
        "deescalation", "accord", "optimism", "soft landing", "talks progress",
        "diplomatic", "breakthrough", "resolved", "lifted sanctions",
    ]
    RISK_OFF = [
        "war", "attack", "invasion", "escalation", "sanctions", "default",
        "crisis", "collapse", "recession", "military strike", "nuclear",
        "terror", "conflict", "threatens", "tariff hike", "new tariffs",
        "imposed tariffs", "sell-off", "selloff", "bank run", "debt crisis",
        "banking crisis", "crash", "downgrade", "emergency", "missile",
    ]
    feeds = [
        "https://news.google.com/rss/search?q=economy+markets+geopolitics&hl=en-US&gl=US&ceid=US:en",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ]
    headlines = []
    for url in feeds:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=7) as r:
                txt = r.read().decode("utf-8", errors="replace")
            titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", txt)
            if not titles:
                titles = re.findall(r"<title>(.*?)</title>", txt)
            headlines.extend(titles[1:16])
        except Exception as e:
            log.warning("Nyheter FEIL (%s): %s", url[:45], e)
    if not headlines:
        return None
    ro_count = roff_count = 0
    drivers = []
    for h in headlines:
        hl = h.lower()
        ro = sum(1 for w in RISK_ON if w in hl)
        roff = sum(1 for w in RISK_OFF if w in hl)
        if ro > roff:
            ro_count += 1
            drivers.append({"headline": h[:90], "type": "risk_on"})
        elif roff > ro:
            roff_count += 1
            drivers.append({"headline": h[:90], "type": "risk_off"})
    total = ro_count + roff_count
    if total == 0:
        label, net = "neutral", 0.0
    else:
        net = round((ro_count - roff_count) / total, 2)
        label = "risk_on" if net >= 0.3 else "risk_off" if net <= -0.3 else "neutral"
    log.info("Nyhetssentiment: %s (score=%+.2f, ro=%d, roff=%d, n=%d)",
             label, net, ro_count, roff_count, len(headlines))
    return {
        "score": net,
        "label": label,
        "top_headlines": headlines[:5],
        "key_drivers": drivers[:6],
        "ro_count": ro_count,
        "roff_count": roff_count,
        "headlines_n": len(headlines),
    }


# Makroindikatorer — privat for dette modulet
MACRO_SYMBOLS = {
    "HYG": "HYG",
    "TIP": "TIP",
    "TNX": "^TNX",
    "IRX": "^IRX",
    "Copper": "HG=F",
    "EEM": "EEM",
}


def fetch_macro_indicators():
    """Henter tilleggsindikatorer for makrobilde."""
    out = {}

    log.info("FRED: henter renter...")
    for key, series in [("TNX", "DGS10"), ("IRX", "DTB3")]:
        val = fetch_fred(series)
        if val:
            out[key] = {"price": round(val, 3), "chg1d": 0, "chg5d": 0}
            log.info("  %s (%s): %.3f%%", key, series, val)
        else:
            daily = fetch_yahoo(MACRO_SYMBOLS[key], "1d", "30d")
            if daily and len(daily) >= 2:
                curr = daily[-1][2]
                c5 = daily[-6][2] if len(daily) >= 6 else curr
                out[key] = {"price": round(curr, 3), "chg1d": 0,
                            "chg5d": round((curr / c5 - 1) * 100, 2)}
            else:
                out[key] = None

    for key in ["HYG", "TIP", "Copper", "EEM"]:
        sym = MACRO_SYMBOLS[key]
        daily = fetch_prices(sym, "1d", "30d")
        if not daily or len(daily) < 6:
            out[key] = None
            continue
        curr = daily[-1][2]
        c5 = daily[-6][2] if len(daily) >= 6 else curr
        c1 = daily[-2][2] if len(daily) >= 2 else curr
        out[key] = {
            "price": round(curr, 4 if curr < 10 else 2),
            "chg1d": round((curr / c1 - 1) * 100, 2),
            "chg5d": round((curr / c5 - 1) * 100, 2),
        }
    return out


def detect_conflict(vix, dxy_5d, fg, cot_usd, hy_stress=False,
                    yield_curve=None, news_sent=None):
    conflicts = []
    if vix > 25 and dxy_5d < 0:
        conflicts.append("VIX>25 men DXY faller \u2013 risk-off uten USD-ettersp\u00f8rsel")
    if fg and fg["score"] < 30 and dxy_5d < 0:
        conflicts.append("Ekstrem frykt men USD svekkes \u2013 unormalt")
    if fg and fg["score"] > 70 and vix > 22:
        conflicts.append("Gr\u00e5dighet men VIX forh\u00f8yet \u2013 divergens")
    if cot_usd and cot_usd > 0 and dxy_5d < -1:
        conflicts.append("COT long USD men pris faller \u2013 divergens")
    if hy_stress and vix < 20:
        conflicts.append("HY-spreader \u00f8ker men VIX lav \u2013 skjult kredittrisiko")
    if yield_curve is not None and yield_curve < -0.3:
        conflicts.append(f"Rentekurve invertert ({yield_curve:+.2f}%) \u2013 resesjonsrisiko")
    if news_sent and news_sent.get("label") == "risk_on" and vix > 25:
        conflicts.append("Nyheter risk-on men VIX forh\u00f8yet \u2013 sentimentskifte p\u00e5g\u00e5r")
    if news_sent and news_sent.get("label") == "risk_off" and fg and fg["score"] > 60:
        conflicts.append("Nyheter risk-off men Fear&Greed viser gr\u00e5dighet \u2013 divergens")
    if news_sent and news_sent.get("label") == "risk_on" and fg and fg["score"] < 25:
        conflicts.append("Nyheter risk-on men ekstrem frykt i markedet \u2013 potensiell bunnstemning")
    return conflicts
