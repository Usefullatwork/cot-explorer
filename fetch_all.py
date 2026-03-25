#!/usr/bin/env python3
"""COT Explorer — hovedorkestrator for makroanalyse og handelsoppsett.

Henter priser, kj\u00f8rer SMC-analyse, scorer 12 instrumenter p\u00e5 12-punkt
konfluensskala og genererer level-til-level trade setups.
"""
import json
import logging
import os

from config import BASE, COT_MAP, INSTRUMENTS, NEWS_CONFIRMS_MAP, OUT
from indicators import calc_atr, calc_ema, get_pdh_pdl_pdc, get_pwh_pwl, get_session_status, to_4h
from levels import build_tagged_levels, fmt_level, is_at_level
from price_fetchers import fetch_prices
from scoring import compute_score
from macro_output import build_macro_output
from sentiment import fetch_fear_greed, fetch_macro_indicators, fetch_news_sentiment
from trade_setup import make_setup_l2l

try:
    from smc import run_smc
    SMC_OK = True
except ImportError:
    SMC_OK = False
    logging.getLogger(__name__).warning("SMC ikke tilgjengelig")

log = logging.getLogger(__name__)


# ── Hjelpefunksjoner ─────────────────────────────────────────


def get_binary_risk(instrument_key, calendar_events, hours=4):
    """Filtrer kalender for bin\u00e6r risiko n\u00e6r instrument."""
    risks = []
    for ev in calendar_events:
        if ev.get("impact") != "High":
            continue
        ha = ev.get("hours_away", 99)
        if ha < 0 or ha > hours:
            continue
        berorte = ev.get("berorte", [])
        if instrument_key in berorte or not berorte:
            risks.append({
                "title": ev["title"],
                "cet": ev["cet"],
                "country": ev["country"],
            })
    return risks


# ── Datalasting ──────────────────────────────────────────────


def load_fundamentals():
    fund_file = BASE / "fundamentals" / "latest.json"
    if fund_file.exists():
        try:
            with open(fund_file) as f:
                data = json.load(f)
            n = len(data.get("indicators", {}))
            log.info("Fundamentals: %d indikatorer lastet (%s USD)",
                     n, data.get("usd_fundamental", {}).get("bias", "?"))
            return data
        except Exception:
            pass
    return {}


def load_calendar():
    cal_file = BASE / "calendar" / "latest.json"
    if cal_file.exists():
        try:
            with open(cal_file) as f:
                cal_data = json.load(f)
            events = cal_data.get("events", [])
            log.info("Kalender: %d events lastet", len(events))
            return events
        except Exception:
            pass
    return []


def load_cot():
    cot_file = BASE / "combined" / "latest.json"
    data = {}
    if cot_file.exists():
        with open(cot_file) as f:
            for d in json.load(f):
                data[d["market"].lower()] = d
    return data


# ── Instrumentanalyse ────────────────────────────────────────


def analyze_instrument(inst, fund_data, calendar_events, cot_data,
                       fg, news_sentiment, prices):
    """Analyserer ett instrument og returnerer (price_entry, level_entry) eller None."""
    key = inst["key"]
    klasse = inst["klasse"]

    daily = fetch_prices(inst["symbol"], "1d", "1y")
    rows_15m = fetch_prices(inst["symbol"], "15m", "5d")
    rows_1h = fetch_prices(inst["symbol"], "60m", "60d")
    h4 = to_4h(rows_1h) if rows_1h else []

    if not daily or len(daily) < 15:
        return None

    curr = daily[-1][2]
    if rows_15m and len(rows_15m) > 0:
        curr = rows_15m[-1][2]

    atr_d = calc_atr(daily, 14)
    atr_15m = calc_atr(rows_15m, 14) if len(rows_15m) >= 15 else None
    atr_4h = calc_atr(h4, 14) if len(h4) >= 15 else None
    sma200 = sum(r[2] for r in daily[-200:]) / min(200, len(daily))

    c1 = daily[-2][2] if len(daily) >= 2 else curr
    c5 = daily[-6][2] if len(daily) >= 6 else curr
    c20 = daily[-21][2] if len(daily) >= 21 else curr
    price_entry = {
        "price": round(curr, 4 if curr < 100 else 2),
        "chg1d": round((curr / c1 - 1) * 100, 2),
        "chg5d": round((curr / c5 - 1) * 100, 2),
        "chg20d": round((curr / c20 - 1) * 100, 2),
    }

    if key == "VIX":
        return price_entry, None

    # SMC analyse
    smc_15m = _run_smc_safe(rows_15m, 5, "15m") if rows_15m and len(rows_15m) > 50 else None
    smc_1h = _run_smc_safe(rows_1h, 10, "1H") if rows_1h and len(rows_1h) > 50 else None
    smc_4h = _run_smc_safe(h4, 5, "4H") if h4 and len(h4) > 30 else None

    # Niv\u00e5er
    tagged_res, tagged_sup, atr_for_merge = build_tagged_levels(
        daily, h4, rows_15m, smc_15m, smc_1h, smc_4h, curr, atr_15m, atr_d,
    )

    # EMA9 + Regime
    closes_d = [r[2] for r in daily]
    closes_15 = [r[2] for r in rows_15m] if rows_15m else []
    ema9_d = calc_ema(closes_d, 9)
    ema9_15m = calc_ema(closes_15, 9) if closes_15 else None

    d1_bull = curr > ema9_d if ema9_d else None
    m15_bull = curr > ema9_15m if ema9_15m else None
    d1_regime = ("BULLISH" if d1_bull else "BEARISH") if d1_bull is not None else "N\u00d8YTRAL"
    m15_regime = ("BULLISH" if m15_bull else "BEARISH") if m15_bull is not None else "N\u00d8YTRAL"

    if d1_bull and m15_bull:
        align = "bull"
    elif not d1_bull and not m15_bull:
        align = "bear"
    else:
        align = "mixed"

    session_now = get_session_status()

    # COT
    cot_key = COT_MAP.get(key, "")
    cot_entry = cot_data.get(cot_key, {})
    spec_net = (cot_entry.get("spekulanter") or {}).get("net", 0) or 0
    oi = cot_entry.get("open_interest", 1) or 1
    cot_pct = spec_net / oi * 100
    cot_bias = "LONG" if cot_pct > 4 else "SHORT" if cot_pct < -4 else "N\u00d8YTRAL"
    cot_color = "bull" if cot_pct > 4 else "bear" if cot_pct < -4 else "neutral"
    _cot_chg = cot_entry.get("change_spec_net", 0) or 0
    if _cot_chg == 0:
        cot_momentum = "STABIL"
    elif (_cot_chg > 0 and spec_net >= 0) or (_cot_chg < 0 and spec_net <= 0):
        cot_momentum = "\u00d8KER"
    else:
        cot_momentum = "SNUR"

    # Score-inputs
    above_sma = curr > sma200
    chg5 = price_entry["chg5d"]
    chg20 = price_entry["chg20d"]

    at_sup = any(
        is_at_level(curr, l["price"], atr_for_merge or atr_d * 0.4, l["weight"])
        for l in tagged_sup
    ) if tagged_sup else False
    at_res = any(
        is_at_level(curr, l["price"], atr_for_merge or atr_d * 0.4, l["weight"])
        for l in tagged_res
    ) if tagged_res else False
    at_level_now = at_sup or at_res

    nearest_sup_w = tagged_sup[0]["weight"] if tagged_sup else 0
    nearest_res_w = tagged_res[0]["weight"] if tagged_res else 0
    htf_level_nearby = max(nearest_sup_w, nearest_res_w) >= 3

    sesjon_aktiv = session_now["active"]
    dir_color = ("bull" if (above_sma and chg5 > 0) else
                 "bear" if (not above_sma and chg5 < 0) else
                 ("bull" if above_sma else "bear"))
    cot_confirms = ((cot_bias == "LONG" and dir_color == "bull") or
                    (cot_bias == "SHORT" and dir_color == "bear"))
    cot_strong = abs(cot_pct) > 10
    no_event_risk = len(get_binary_risk(key, calendar_events, hours=4)) == 0

    # BOS
    bos_1h_levels = (smc_1h or {}).get("bos_levels", [])
    bos_4h_levels = (smc_4h or {}).get("bos_levels", [])
    recent_bos = sorted(bos_1h_levels + bos_4h_levels, key=lambda b: b["idx"], reverse=True)[:3]
    bos_confirms = any(
        (b["type"] == "BOS_opp" and dir_color == "bull") or
        (b["type"] == "BOS_ned" and dir_color == "bear")
        for b in recent_bos
    )

    smc_1h_structure = (smc_1h or {}).get("structure", "MIXED")
    smc_struct_confirms = (
        (dir_color == "bull" and smc_1h_structure in ("BULLISH", "BULLISH_SVAK")) or
        (dir_color == "bear" and smc_1h_structure in ("BEARISH", "BEARISH_SVAK"))
    )

    # Nyhetssentiment
    ns_label = (news_sentiment or {}).get("label", "neutral")
    nc_map = NEWS_CONFIRMS_MAP.get(key, (None, None))
    if ns_label == "risk_on" and nc_map[0]:
        news_confirms_dir = (nc_map[0] == dir_color)
    elif ns_label == "risk_off" and nc_map[1]:
        news_confirms_dir = (nc_map[1] == dir_color)
    else:
        news_confirms_dir = False
    news_headwind = False
    if ns_label == "risk_on" and nc_map[0] and nc_map[0] != dir_color:
        news_headwind = True
    elif ns_label == "risk_off" and nc_map[1] and nc_map[1] != dir_color:
        news_headwind = True

    # Fundamentals
    inst_fund = fund_data.get("instrument_scores", {}).get(key, {})
    inst_fund_score = inst_fund.get("score", 0)
    inst_fund_bias = inst_fund.get("bias", "neutral")
    fund_confirms = ((inst_fund_score > 0.3 and dir_color == "bull") or
                     (inst_fund_score < -0.3 and dir_color == "bear"))

    # Scoring
    vix_price = (prices.get("VIX") or {}).get("price", 20)
    score_details, score, max_score, grade, grade_color, timeframe_bias, pos_size = (
        compute_score(
            above_sma=above_sma,
            chg20_confirms=(chg20 > 0 if dir_color == "bull" else chg20 < 0),
            cot_confirms=cot_confirms,
            cot_strong=cot_strong,
            at_level_now=at_level_now,
            htf_level_nearby=htf_level_nearby,
            trend_aligned=(align in ("bull", "bear")),
            no_event_risk=no_event_risk,
            news_confirms_dir=news_confirms_dir,
            fund_confirms=fund_confirms,
            bos_confirms=bos_confirms,
            smc_struct_confirms=smc_struct_confirms,
            sesjon_aktiv=sesjon_aktiv,
            vix_price=vix_price,
        )
    )

    # Setups
    atr_for_setup = atr_15m if atr_15m else (atr_d * 0.4)
    setup_long = make_setup_l2l(curr, atr_for_setup, atr_d, tagged_sup, tagged_res, "long", klasse)
    setup_short = make_setup_l2l(curr, atr_for_setup, atr_d, tagged_sup, tagged_res, "short", klasse)
    for s in [setup_long, setup_short]:
        if s:
            s["session"] = inst["session"]

    # Output
    atr_s = f"{atr_15m:.5f}" if atr_15m else "N/A"
    active_setup = setup_long if dir_color == "bull" else setup_short
    t1_s = active_setup["t1"] if active_setup else None
    rr_s = active_setup["rr_t1"] if active_setup else None
    if t1_s is None:
        min_dist = (atr_15m or atr_d * 0.4) * 1.5
        cands = tagged_res if dir_color == "bull" else tagged_sup
        cands = [l for l in cands if abs(l["price"] - curr) >= min_dist]
        pot = next((l for l in cands if l["weight"] >= 2), cands[0] if cands else None)
        if pot:
            p = pot["price"]
            t1_s = f"~{round(p, 5 if p < 100 else 2)}"
        else:
            t1_s = "-"
        rr_s = "-"

    st = "\U0001f7e2" if at_level_now else "\U0001f7e1"
    dir_tag = "\u25b2" if dir_color == "bull" else "\u25bc"
    htf_tag = f"HTF:w{max(nearest_sup_w, nearest_res_w)}" if htf_level_nearby else "noHTF"
    log.info("  %s %s  %s  ATR15m=%s  %s(%d/%d) %s %s  T1:%s  R:R:%s",
             st, f"{inst['navn']:10s}", f"{curr:.5f}", atr_s,
             grade, score, max_score, dir_tag, htf_tag, t1_s, rr_s)

    pdh, pdl, pdc = get_pdh_pdl_pdc(daily)
    pwh, pwl = get_pwh_pwl(daily)

    level_entry = {
        "name": inst["navn"],
        "label": inst["label"],
        "klasse": klasse,
        "session": inst["session"],
        "class": inst["kat"][0].upper(),
        "current": round(curr, 5 if curr < 100 else 2),
        "atr14": round(atr_15m, 5) if atr_15m else None,
        "atr_15m": round(atr_15m, 5) if atr_15m else None,
        "atr_daily": round(atr_d, 5) if atr_d else None,
        "atr_4h": round(atr_4h, 5) if atr_4h else None,
        "at_level_now": at_level_now,
        "status": "aktiv" if at_level_now else "watchlist",
        "pdh": round(pdh, 5) if pdh else None,
        "pdl": round(pdl, 5) if pdl else None,
        "pdc": round(pdc, 5) if pdc else None,
        "pwh": round(pwh, 5) if pwh else None,
        "pwl": round(pwl, 5) if pwl else None,
        "ema9_d1": round(ema9_d, 5) if ema9_d else None,
        "ema9_15m": round(ema9_15m, 5) if ema9_15m else None,
        "ema9_above": curr > ema9_d if ema9_d else None,
        "d1_regime": d1_regime,
        "m15_regime": m15_regime,
        "regime_align": align,
        "session_now": session_now,
        "sma200": round(sma200, 4 if sma200 < 100 else 2),
        "sma200_pos": "over" if above_sma else "under",
        "chg5d": chg5,
        "chg20d": chg20,
        "dir_color": dir_color,
        "grade": grade,
        "grade_color": grade_color,
        "score": score,
        "score_pct": round(score / max_score * 100),
        "score_details": score_details,
        "news_headwind": news_headwind,
        "news_sentiment_label": ns_label,
        "open_interest": oi,
        "resistances": fmt_level(tagged_res, "R", atr_15m or atr_d, curr),
        "supports": fmt_level(tagged_sup, "S", atr_15m or atr_d, curr),
        "setup_long": setup_long,
        "setup_short": setup_short,
        "binary_risk": get_binary_risk(key, calendar_events),
        "smc": _smc_output(smc_15m),
        "smc_1h": _smc_output(smc_1h),
        "smc_4h": _smc_output(smc_4h),
        "dxy_conf": ("medvind" if (inst["kat"] == "valuta" and
                     (prices.get("DXY") or {}).get("chg5d", 0) < 0) else "motvind"),
        "pos_size": pos_size,
        "vix_spread_factor": 1.0 if vix_price < 20 else 1.5 if vix_price < 30 else 2.0,
        "cot": {
            "bias": cot_bias, "color": cot_color, "net": spec_net,
            "chg": cot_entry.get("change_spec_net", 0), "pct": round(abs(cot_pct), 1),
            "momentum": cot_momentum,
            "date": cot_entry.get("date", ""), "report": cot_entry.get("report", ""),
        },
        "combined_bias": "LONG" if dir_color == "bull" else "SHORT",
        "timeframe_bias": timeframe_bias,
        "sentiment": {"fear_greed": fg},
        "fundamentals": {
            "score": inst_fund_score,
            "bias": inst_fund_bias,
            "confirms": fund_confirms,
            "categories": {
                cat: fund_data.get("category_scores", {}).get(cat, {})
                for cat in ("econ_growth", "inflation", "jobs")
            },
            "indicators": fund_data.get("indicators", {}),
            "usd_bias": fund_data.get("usd_fundamental", {}).get("bias", "neutral"),
            "updated": fund_data.get("updated", ""),
        },
    }
    return price_entry, level_entry


# ── Interne hjelpere ─────────────────────────────────────────


def _run_smc_safe(rows, swing_length, label):
    if not SMC_OK:
        return None
    try:
        return run_smc(rows, swing_length=swing_length)
    except Exception as e:
        log.warning("SMC %s FEIL: %s", label, e)
        return None


def _smc_output(smc_data):
    if not smc_data:
        return {
            "structure": None, "supply_zones": [], "demand_zones": [],
            "bos_levels": [], "last_swing_high": None, "last_swing_low": None,
        }
    return {
        "structure": smc_data["structure"],
        "supply_zones": smc_data["supply_zones"],
        "demand_zones": smc_data["demand_zones"],
        "bos_levels": smc_data["bos_levels"],
        "last_swing_high": smc_data["last_swing_high"],
        "last_swing_low": smc_data["last_swing_low"],
    }


# ── Main ─────────────────────────────────────────────────────


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    os.makedirs(BASE / "macro", exist_ok=True)

    fund_data = load_fundamentals()
    calendar_events = load_calendar()
    cot_data = load_cot()

    log.info("Henter Fear & Greed...")
    fg = fetch_fear_greed()
    if fg:
        log.info("  -> %s (%s)", fg["score"], fg["rating"])

    log.info("Henter nyhetssentiment...")
    news_sentiment = fetch_news_sentiment()

    prices, levels = {}, {}
    for inst in INSTRUMENTS:
        log.info("Henter %s...", inst["navn"])
        result = analyze_instrument(inst, fund_data, calendar_events, cot_data,
                                    fg, news_sentiment, prices)
        if result is None:
            continue
        price_entry, level_entry = result
        prices[inst["key"]] = price_entry
        if level_entry is not None:
            levels[inst["key"]] = level_entry

    log.info("Henter makro-indikatorer (HYG, TIP, TNX, IRX, Kobber, EM)...")
    macro_ind = fetch_macro_indicators()
    for k, v in macro_ind.items():
        if v:
            log.info("  %s: %s  5d=%+.2f%%", k, v["price"], v["chg5d"])
        else:
            log.info("  %s: FEIL", k)

    macro = build_macro_output(prices, levels, cot_data, fg, news_sentiment,
                               calendar_events, macro_ind)

    with open(OUT, "w") as f:
        json.dump(macro, f, ensure_ascii=False, indent=2)
    log.info("OK -> %s  (%d instruments)", OUT, len(levels))
    if macro["sentiment"]["conflicts"]:
        log.info("Konflikter:")
        for c in macro["sentiment"]["conflicts"]:
            log.warning("  %s", c)


if __name__ == "__main__":
    main()
