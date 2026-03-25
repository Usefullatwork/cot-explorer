#!/usr/bin/env python3
"""Makro-output — bygger endelig JSON-dictionary med Dollar Smile og VIX-regime."""
from datetime import datetime, timezone

from sentiment import detect_conflict


def build_macro_output(prices, levels, cot_data, fg, news_sentiment,
                       calendar_events, macro_ind):
    """Bygger det endelige makro-dictionaryet."""
    vix_price = (prices.get("VIX") or {}).get("price", 20)
    dxy_5d = (prices.get("DXY") or {}).get("chg5d", 0)
    brent_p = (prices.get("Brent") or {}).get("price", 80)
    cot_dxy = cot_data.get("usd index", {})
    cot_dxy_net = ((cot_dxy.get("spekulanter") or {}).get("net", 0) or 0)

    hyg = macro_ind.get("HYG") or {}
    hy_chg5d = hyg.get("chg5d", 0)
    hy_stress = hy_chg5d < -1.5

    tip = macro_ind.get("TIP") or {}
    tip_trend_5d = tip.get("chg5d", 0)

    tnx = macro_ind.get("TNX") or {}
    irx = macro_ind.get("IRX") or {}
    yield_10y = tnx.get("price")
    yield_3m = irx.get("price")
    yield_curve = round(yield_10y - yield_3m, 2) if (yield_10y and yield_3m) else None

    copper = macro_ind.get("Copper") or {}
    copper_5d = copper.get("chg5d", 0)
    eem = macro_ind.get("EEM") or {}
    em_5d = eem.get("chg5d", 0)

    conflicts = detect_conflict(vix_price, dxy_5d, fg, cot_dxy_net,
                                hy_stress, yield_curve, news_sentiment)

    risk_off_signals = sum([vix_price > 25, hy_stress,
                            (yield_curve or 0) < -0.3,
                            (fg["score"] if fg else 50) < 35])
    if conflicts:
        smile_pos, usd_bias, usd_color, smile_desc = (
            "konflikt", "UKLAR", "warn",
            "Motstridende signaler: " + " | ".join(conflicts[:2]))
    elif vix_price > 30 or risk_off_signals >= 2:
        smile_pos, usd_bias, usd_color, smile_desc = (
            "venstre", "STERKT", "bull", "Risk-off \u2013 USD trygg havn")
    elif vix_price < 18 and brent_p < 85 and not hy_stress:
        smile_pos, usd_bias, usd_color, smile_desc = (
            "midten", "SVAKT", "bear", "Goldilocks \u2013 svak USD")
    else:
        smile_pos, usd_bias, usd_color, smile_desc = (
            "hoyre", "MODERAT", "bull", "Vekst/inflasjon driver USD")

    if vix_price > 30:
        vix_regime = {"value": vix_price, "label": "Ekstrem frykt \u2013 KVART st\u00f8rrelse",
                      "color": "bear", "regime": "extreme"}
    elif vix_price > 20:
        vix_regime = {"value": vix_price, "label": "Forh\u00f8yet \u2013 HALV st\u00f8rrelse",
                      "color": "warn", "regime": "elevated"}
    else:
        vix_regime = {"value": vix_price, "label": "Normalt \u2013 full st\u00f8rrelse",
                      "color": "bull", "regime": "normal"}

    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "cot_date": max((d.get("date", "") for d in cot_data.values() if d.get("date")),
                        default="ukjent"),
        "prices": prices,
        "vix_regime": vix_regime,
        "sentiment": {"fear_greed": fg, "news": news_sentiment, "conflicts": conflicts},
        "dollar_smile": {
            "position": smile_pos, "usd_bias": usd_bias,
            "usd_color": usd_color, "desc": smile_desc,
            "conflicts": conflicts,
            "inputs": {
                "vix": vix_price, "hy_stress": hy_stress, "hy_chg5d": hy_chg5d,
                "brent": brent_p, "tip_trend_5d": tip_trend_5d,
                "dxy_trend_5d": dxy_5d, "yield_curve": yield_curve,
                "yield_10y": yield_10y, "yield_3m": yield_3m,
                "copper_5d": copper_5d, "em_5d": em_5d,
            },
        },
        "macro_indicators": macro_ind,
        "trading_levels": levels,
        "calendar": calendar_events,
    }
