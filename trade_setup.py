#!/usr/bin/env python3
"""Level-til-level trade setup — strukturbasert SL med R:R-krav."""
from levels import is_at_level


def make_setup_l2l(curr, atr_15m, atr_daily, sup_tagged, res_tagged,
                   direction, klasse, min_rr=1.5):
    """
    Makro level-til-level setup — strukturbasert stop loss:

    Geometri:
      LONG:  entry = st\u00f8tte/demand-sone,  SL = under sone-bunn
      SHORT: entry = motstand/supply-sone, SL = over sone-topp

    Regler:
      - SL plasseres ved STRUKTUREN, ikke mekanisk ATR fra n\u00e5pris
      - Risk = faktisk avstand entry \u2192 SL
      - T1 m\u00e5 gi R:R >= min_rr basert p\u00e5 faktisk risk
    """
    if not atr_15m or atr_15m <= 0:
        return None
    if not atr_daily or atr_daily <= 0:
        atr_daily = atr_15m * 5

    def structural_sl(entry_level, entry_obj, dir_):
        """SL ved strukturniv\u00e5 — aldri mekanisk ATR fra n\u00e5pris."""
        buf = atr_daily * 0.15
        w = entry_obj.get("weight", 1)
        if dir_ == "long":
            zone_bot = entry_obj.get("zone_bottom")
            if zone_bot and zone_bot < entry_level:
                return round(zone_bot - buf, 5)
            sl_buf = atr_daily * (0.5 if w >= 4 else 0.3)
            return round(entry_level - sl_buf, 5)
        else:
            zone_top = entry_obj.get("zone_top")
            if zone_top and zone_top > entry_level:
                return round(zone_top + buf, 5)
            sl_buf = atr_daily * (0.5 if w >= 4 else 0.3)
            return round(entry_level + sl_buf, 5)

    def best_t1(levels, entry, min_dist):
        """Beste T1: h\u00f8yest HTF-weight \u2192 n\u00e6rmest entry, minst min_dist unna."""
        cands = sorted(levels, key=lambda x: (-x["weight"], abs(x["price"] - entry)))
        for l in cands:
            p = l["price"]
            ok = (p > entry + min_dist) if direction == "long" else (p < entry - min_dist)
            if ok:
                q = "htf" if l["weight"] >= 3 else ("4h" if l["weight"] >= 2 else "weak")
                return dict(l, t1_quality=q)
        return None

    if direction == "long":
        return _build_long_setup(curr, atr_15m, atr_daily, sup_tagged, res_tagged,
                                 min_rr, structural_sl, best_t1)
    else:
        return _build_short_setup(curr, atr_15m, atr_daily, sup_tagged, res_tagged,
                                  min_rr, structural_sl, best_t1)


def _build_long_setup(curr, atr_15m, atr_daily, sup_tagged, res_tagged,
                      min_rr, structural_sl, best_t1):
    if not sup_tagged or not res_tagged:
        return None
    entry_obj = sup_tagged[0]
    entry_level = entry_obj["price"]
    entry_w = entry_obj["weight"]

    entry_dist = curr - entry_level
    max_entry_dist = atr_daily * (0.3 if entry_w <= 1 else 0.7 if entry_w == 2 else 1.0)
    if entry_dist < 0 or entry_dist > max_entry_dist:
        return None

    sl = structural_sl(entry_level, entry_obj, "long")
    risk = entry_level - sl
    if risk <= 0:
        return None
    min_t1_dist = risk * min_rr

    t1_obj = best_t1(res_tagged, entry_level, min_t1_dist)
    if t1_obj is None:
        return None
    t1 = t1_obj["price"]

    res_after = [l for l in res_tagged if l["price"] > t1]
    t2 = res_after[0]["price"] if res_after else round(t1 + risk, 5)

    rr1 = round((t1 - entry_level) / risk, 2)
    rr2 = round((t2 - entry_level) / risk, 2)

    at_level = is_at_level(curr, entry_level, atr_15m, entry_w)
    sl_src = "zone" if entry_obj.get("zone_bottom") else "struktur"
    q = t1_obj["t1_quality"]
    return {
        "entry": round(entry_level, 5),
        "entry_curr": round(curr, 5),
        "sl": sl,
        "sl_type": sl_src,
        "t1": round(t1, 5),
        "t2": round(t2, 5),
        "rr_t1": rr1, "rr_t2": rr2, "min_rr": min_rr,
        "risk_atr_d": round(risk / atr_daily, 2),
        "entry_dist_atr": round(entry_dist / atr_daily, 2),
        "entry_name": f"St\u00f8tte {round(entry_level, 5)} [{entry_obj['source']}]",
        "entry_level": round(entry_level, 5),
        "entry_weight": entry_w,
        "t1_source": t1_obj["source"],
        "t1_weight": t1_obj["weight"],
        "t1_quality": q,
        "status": "aktiv" if at_level else "watchlist",
        "note": (f"MAKRO LONG: E={round(entry_level, 4)} [{entry_obj['source']} w{entry_w}]"
                 f" SL={round(sl, 4)} ({sl_src}) \u2192 T1={round(t1, 4)}"
                 f" [{t1_obj['source']} w{t1_obj['weight']} {q}]"
                 f" R:R={rr1} | Risk={round(risk, 4)} ({round(risk / atr_daily, 2)}\u00d7ATRd)"),
        "timeframe": "D1/4H",
    }


def _build_short_setup(curr, atr_15m, atr_daily, sup_tagged, res_tagged,
                       min_rr, structural_sl, best_t1):
    if not res_tagged or not sup_tagged:
        return None
    entry_obj = res_tagged[0]
    entry_level = entry_obj["price"]
    entry_w = entry_obj["weight"]

    entry_dist = entry_level - curr
    max_entry_dist = atr_daily * (0.3 if entry_w <= 1 else 0.7 if entry_w == 2 else 1.0)
    if entry_dist < 0 or entry_dist > max_entry_dist:
        return None

    sl = structural_sl(entry_level, entry_obj, "short")
    risk = sl - entry_level
    if risk <= 0:
        return None
    min_t1_dist = risk * min_rr

    t1_obj = best_t1(sup_tagged, entry_level, min_t1_dist)
    if t1_obj is None:
        return None
    t1 = t1_obj["price"]

    sup_after = [l for l in sup_tagged if l["price"] < t1]
    t2 = sup_after[0]["price"] if sup_after else round(t1 - risk, 5)

    rr1 = round((entry_level - t1) / risk, 2)
    rr2 = round((entry_level - t2) / risk, 2)

    at_level = is_at_level(curr, entry_level, atr_15m, entry_w)
    sl_src = "zone" if entry_obj.get("zone_top") else "struktur"
    q = t1_obj["t1_quality"]
    return {
        "entry": round(entry_level, 5),
        "entry_curr": round(curr, 5),
        "sl": sl,
        "sl_type": sl_src,
        "t1": round(t1, 5),
        "t2": round(t2, 5),
        "rr_t1": rr1, "rr_t2": rr2, "min_rr": min_rr,
        "risk_atr_d": round(risk / atr_daily, 2),
        "entry_dist_atr": round(entry_dist / atr_daily, 2),
        "entry_name": f"Motstand {round(entry_level, 5)} [{entry_obj['source']}]",
        "entry_level": round(entry_level, 5),
        "entry_weight": entry_w,
        "t1_source": t1_obj["source"],
        "t1_weight": t1_obj["weight"],
        "t1_quality": q,
        "status": "aktiv" if at_level else "watchlist",
        "note": (f"MAKRO SHORT: E={round(entry_level, 4)} [{entry_obj['source']} w{entry_w}]"
                 f" SL={round(sl, 4)} ({sl_src}) \u2192 T1={round(t1, 4)}"
                 f" [{t1_obj['source']} w{t1_obj['weight']} {q}]"
                 f" R:R={rr1} | Risk={round(risk, 4)} ({round(risk / atr_daily, 2)}\u00d7ATRd)"),
        "timeframe": "D1/4H",
    }
