#!/usr/bin/env python3
"""
fetch_fundamentals.py — Henter fundamental makrodata fra FRED og scorer ±2 per indikator.
Lagrer til data/fundamentals/latest.json.

Kategorier (EdgeFinder-stil):
  - Economic Growth: GDP QoQ, Retail Sales MoM, UoM Consumer Confidence
  - Inflation:       CPI YoY, PPI YoY, PCE YoY, Fed Funds Rate
  - Jobs Market:     NFP, Unemployment Rate, Initial Claims, ADP, JOLTS

PMI hentes utelukkende fra ForexFactory-kalenderen (ISM-serier er ikke
tilgjengelige som FRED-serie; de må kjøpes direkte fra ISM).

Vekting for høy-sannsynlighets-setups:
  - Innenfor kategori: vektes per indikator (NFP/Claims/CPI/PCE veier tyngst)
  - Mellom kategorier: inflation 0.40 · jobs 0.35 · growth 0.25 (for FX/metaller)
  - Konsensus-multiplikator: ×1.4 når inflasjon+jobs peker SAMME vei,
    ×0.7 når de peker MOT hverandre → demper mixet signal
"""
import json
import logging
import os
import time
from datetime import datetime, timezone

from fred_client import fetch_fred_api
from indicator_scoring import compute_indicator, consensus_multiplier, score_indicator

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

BASE = os.path.expanduser("~/cot-explorer/data")
OUT = os.path.join(BASE, "fundamentals", "latest.json")
os.makedirs(os.path.join(BASE, "fundamentals"), exist_ok=True)

# ── FRED-serier ───────────────────────────────────────────────────────────────
# Merk: NAPM og NMFCI (ISM PMI) gir 400-feil — ISM selger dataene, de er ikke
# gratis på FRED. PMI håndteres i try_calendar_pmi() under.
# ADPMNUSNERNSA er allerede en månedlig ENDRINGSSERIE (ikke nivåserie),
# så type = "level" — ikke "mom_abs" (som ville gitt andre derivat).

FRED_SERIES = {
    # Economic Growth & Consumer Strength
    "GDP": {"id": "A191RL1Q225SBEA", "type": "level", "label": "GDP Growth QoQ (%)"},
    "Retail": {"id": "RSAFS", "type": "mom", "label": "Retail Sales MoM (%)"},
    "ConConf": {"id": "UMCSENT", "type": "level", "label": "UoM Consumer Sentiment"},
    # Inflation
    "CPI": {"id": "CPIAUCSL", "type": "yoy", "label": "CPI YoY (%)"},
    "PPI": {"id": "PPIACO", "type": "yoy", "label": "PPI YoY (%)"},
    "PCE": {"id": "PCEPI", "type": "yoy", "label": "PCE YoY (%)"},
    "IntRate": {"id": "FEDFUNDS", "type": "level", "label": "Fed Funds Rate (%)"},
    # Jobs Market
    "NFP": {"id": "PAYEMS", "type": "mom_abs", "label": "NFP Endring (k)"},
    "Unemp": {"id": "UNRATE", "type": "level", "label": "Arbeidsledighet (%)"},
    "Claims": {"id": "ICSA", "type": "level", "label": "Init. Krav (k)"},
    # ADP: allerede en endringsserie → type="level" (raw = månedlig endring i tusen)
    "ADP": {"id": "ADPMNUSNERNSA", "type": "level", "label": "ADP Endring (k)"},
    "JOLTS": {"id": "JTSJOL", "type": "level", "label": "JOLTS Stillinger (k)"},
}

# Vekter per indikator (innenfor kategori) — høyere = viktigere markedsbeveger
INDICATOR_WEIGHTS = {
    # Growth (sum = 4)
    "GDP": 1.0,
    "mPMI": 2.0,  # fra kalender
    "sPMI": 2.0,  # fra kalender
    "Retail": 1.5,
    "ConConf": 1.5,
    # Inflation (sum = 6.5)
    "CPI": 2.0,
    "PPI": 1.0,
    "PCE": 2.0,
    "IntRate": 1.5,
    # Jobs (sum = 7)
    "NFP": 2.0,
    "Unemp": 1.5,
    "Claims": 1.5,
    "ADP": 1.0,
    "JOLTS": 1.0,
}

CATEGORIES = {
    "econ_growth": ["GDP", "mPMI", "sPMI", "Retail", "ConConf"],
    "inflation": ["CPI", "PPI", "PCE", "IntRate"],
    "jobs": ["NFP", "Unemp", "Claims", "ADP", "JOLTS"],
}

# Kategori-vekter per instrumenttype
CAT_WEIGHTS_FX = {"econ_growth": 0.25, "inflation": 0.40, "jobs": 0.35}
CAT_WEIGHTS_EQ = {
    "econ_growth": 0.50,
    "inflation": 0.10,
    "jobs": 0.40,
}  # aksjer/råolje

INSTRUMENT_USD_DIR = {
    "EURUSD": -1,
    "GBPUSD": -1,
    "AUDUSD": -1,
    "USDJPY": +1,
    "DXY": +1,
    "Gold": -1,
    "Silver": -1,
    "SPX": +1,
    "NAS100": +1,
    "Brent": +1,
    "WTI": +1,
}

EQ_INSTRUMENTS = {"SPX", "NAS100", "Brent", "WTI"}


# ── PMI fra ForexFactory-kalenderen ──────────────────────────────────────────
def try_calendar_pmi():
    """
    Leter etter ISM Manufacturing og Services PMI-releaser med faktiske verdier
    i ForexFactory-kalenderen. Returnerer {key: {actual, forecast, score}}.
    """
    cal_path = os.path.join(BASE, "calendar", "latest.json")
    if not os.path.exists(cal_path):
        return {}
    try:
        with open(cal_path) as f:
            cal = json.load(f)
    except Exception:
        return {}

    pmi_map = {}
    for ev in cal.get("events", []):
        if ev.get("country") != "USD":
            continue
        title = ev.get("title", "").lower()
        actual = ev.get("actual", "")
        if not actual:
            continue
        try:
            act_val = float(str(actual).replace("%", "").strip())
        except (ValueError, AttributeError):
            continue
        try:
            fore_val = (
                float(str(ev.get("forecast", "")).replace("%", "").strip())
                if ev.get("forecast")
                else None
            )
        except (ValueError, AttributeError):
            fore_val = None
        try:
            prev_val = (
                float(str(ev.get("previous", "")).replace("%", "").strip())
                if ev.get("previous")
                else None
            )
        except (ValueError, AttributeError):
            prev_val = None

        # Score: kombiner nivå og surprise
        base_score = score_indicator("mPMI", act_val, prev_val)
        if fore_val is not None:
            diff = act_val - fore_val
            surprise = (
                2
                if diff > 1
                else 1
                if diff > 0
                else -2
                if diff < -1
                else -1
                if diff < 0
                else 0
            )
        else:
            surprise = 0
        final_score = max(-2, min(2, base_score + surprise))

        entry = {
            "actual": act_val,
            "forecast": fore_val,
            "previous": prev_val,
            "surprise": surprise,
            "score": final_score,
        }
        if "ism manufacturing" in title or (
            "manufacturing pmi" in title and "flash" not in title
        ):
            pmi_map["mPMI"] = entry
        elif (
            "ism services" in title
            or ("services pmi" in title and "flash" not in title)
            or "non-manufacturing" in title
        ):
            pmi_map["sPMI"] = entry

    return pmi_map


# ── Vektet kategori-gjennomsnitt ──────────────────────────────────────────────
def weighted_cat_avg(cat_keys, indicators):
    """Vektet gjennomsnitt av indikator-scorer innenfor en kategori."""
    total_score = 0.0
    total_w = 0.0
    for k in cat_keys:
        if k in indicators:
            w = INDICATOR_WEIGHTS.get(k, 1.0)
            total_score += indicators[k]["score"] * w
            total_w += w
    return round(total_score / total_w, 3) if total_w > 0 else 0.0


# ══ HOVEDLOGIKK ══════════════════════════════════════════════════════════════
log.info("=== fetch_fundamentals.py ===")

indicators = {}

# 1. Hent FRED-data
for key, cfg in FRED_SERIES.items():
    log.info("Henter %s (%s)...", key, cfg["id"])
    limit = 16 if cfg["type"] == "yoy" else 6
    obs = fetch_fred_api(cfg["id"], limit=limit)
    result = compute_indicator(key, cfg, obs)
    if result:
        indicators[key] = result
        log.info(
            "    → %s (%-5s)  score=%+d",
            result["current"],
            result["trend"],
            result["score"],
        )
    else:
        log.warning("    → FEIL eller for få datapunkter")
    time.sleep(0.15)

# 2. Supplement PMI fra kalender
cal_pmi = try_calendar_pmi()
for k, pmi in cal_pmi.items():
    indicators[k] = {
        "key": k,
        "label": "ISM Manufacturing PMI" if k == "mPMI" else "ISM Services NMI",
        "current": pmi["actual"],
        "previous": pmi.get("previous"),
        "forecast": pmi.get("forecast"),
        "surprise": pmi.get("surprise", 0),
        "score": pmi["score"],
        "trend": "ukjent",
        "kilde": "kalender",
    }
    log.info(
        "Kalender %s: actual=%s  forecast=%s  score=%+d",
        k,
        pmi["actual"],
        pmi.get("forecast"),
        pmi["score"],
    )

# 3. Beregn vektede kategori-gjennomsnitt
cat_avgs = {}
category_scores = {}
for cat, keys in CATEGORIES.items():
    avg = weighted_cat_avg(keys, indicators)
    count = sum(1 for k in keys if k in indicators)
    cat_avgs[cat] = avg
    category_scores[cat] = {
        "score": round(
            sum(indicators[k]["score"] for k in keys if k in indicators), 2
        ),
        "avg": avg,
        "count": count,
        "bias": "bullish" if avg >= 0.4 else "bearish" if avg <= -0.4 else "neutral",
        "keys": keys,
    }

# 4. Konsensus-multiplikator
multiplier = consensus_multiplier(cat_avgs)

# 5. USD-samlet score (vektet, med konsensus)
usd_raw = (
    cat_avgs.get("econ_growth", 0) * CAT_WEIGHTS_FX["econ_growth"]
    + cat_avgs.get("inflation", 0) * CAT_WEIGHTS_FX["inflation"]
    + cat_avgs.get("jobs", 0) * CAT_WEIGHTS_FX["jobs"]
)
usd_score = round(usd_raw * multiplier, 3)

if usd_score > 0.7:
    usd_bias = "strong_bullish"
elif usd_score > 0.25:
    usd_bias = "bullish"
elif usd_score < -0.7:
    usd_bias = "strong_bearish"
elif usd_score < -0.25:
    usd_bias = "bearish"
else:
    usd_bias = "neutral"

# 6. Instrument-scorer
instrument_scores = {}
for inst_key, direction in INSTRUMENT_USD_DIR.items():
    if inst_key in EQ_INSTRUMENTS:
        cat_w = CAT_WEIGHTS_EQ
    else:
        cat_w = CAT_WEIGHTS_FX

    raw = (
        cat_avgs.get("econ_growth", 0) * cat_w["econ_growth"]
        + cat_avgs.get("inflation", 0) * cat_w["inflation"]
        + cat_avgs.get("jobs", 0) * cat_w["jobs"]
    )
    raw_with_consensus = raw * multiplier * direction
    score_inst = round(max(-2.0, min(2.0, raw_with_consensus)), 2)

    if score_inst > 0.7:
        bias = "strong_bullish"
    elif score_inst > 0.25:
        bias = "bullish"
    elif score_inst < -0.7:
        bias = "strong_bearish"
    elif score_inst < -0.25:
        bias = "bearish"
    else:
        bias = "neutral"

    instrument_scores[inst_key] = {
        "score": score_inst,
        "bias": bias,
        "direction": direction,
    }

# 7. Lagre
output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "consensus_multi": multiplier,
    "usd_fundamental": {
        "score": usd_score,
        "bias": usd_bias,
        "n": len(indicators),
    },
    "category_scores": category_scores,
    "indicators": indicators,
    "instrument_scores": instrument_scores,
}
with open(OUT, "w") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# 8. Utskrift
log.info("Lagret → %s", OUT)
log.info("Konsensus-multiplikator: ×%s", multiplier)
log.info("USD fundamental: %s  (score=%+.3f)", usd_bias.upper(), usd_score)
for cat, cs in category_scores.items():
    log.info("  %-14s: %-14s  (vektet avg=%+.2f)", cat, cs["bias"], cs["avg"])
log.info("Instrument-prediksjon:")
for k, v in instrument_scores.items():
    bar = "▲" if "bullish" in v["bias"] else "▼" if "bearish" in v["bias"] else "─"
    bb = "!" if "strong" in v["bias"] else " "
    log.info("  %s%s %-8s: %+.2f  %s", bar, bb, k, v["score"], v["bias"])
