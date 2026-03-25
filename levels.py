#!/usr/bin/env python3
"""Niv\u00e5deteksjon — st\u00f8tte/motstand, vekting og sammensl\u00e5ing."""
from indicators import get_pdh_pdl_pdc, get_pwh_pwl


def find_intraday_levels(rows_15m, n=3):
    """
    Finner st\u00f8tte/motstand fra 15m candles.
    Bruker bare siste 2 dagers data (ca 200 candles).
    n=3: minst 3 candles p\u00e5 hver side for \u00e5 bekrefte niv\u00e5.
    """
    rows = rows_15m[-200:] if len(rows_15m) > 200 else rows_15m
    curr = rows[-1][2]
    res, sup = [], []
    for i in range(n, len(rows) - n):
        if rows[i][0] == max(r[0] for r in rows[i - n:i + n + 1]):
            res.append(rows[i][0])
        if rows[i][1] == min(r[1] for r in rows[i - n:i + n + 1]):
            sup.append(rows[i][1])
    r_filt = sorted(
        list(dict.fromkeys([round(r, 5) for r in res if r > curr])),
        key=lambda x: abs(x - curr),
    )[:4]
    s_filt = sorted(
        list(dict.fromkeys([round(s, 5) for s in sup if s < curr])),
        key=lambda x: abs(x - curr),
    )[:4]
    return r_filt, s_filt


def find_swing_levels(rows, n=5):
    """Daglige/4H niv\u00e5er for kontekst."""
    curr = rows[-1][2]
    res, sup = [], []
    for i in range(n, len(rows) - n):
        if rows[i][0] == max(r[0] for r in rows[i - n:i + n + 1]):
            res.append(rows[i][0])
        if rows[i][1] == min(r[1] for r in rows[i - n:i + n + 1]):
            sup.append(rows[i][1])
    r_filt = sorted(
        list(dict.fromkeys([round(r, 5) for r in res if r > curr])),
        key=lambda x: abs(x - curr),
    )[:3]
    s_filt = sorted(
        list(dict.fromkeys([round(s, 5) for s in sup if s < curr])),
        key=lambda x: abs(x - curr),
    )[:3]
    return r_filt, s_filt


def is_at_level(curr, level, atr_15m, weight=1):
    """
    Hard sjekk: pris M\u00c5 v\u00e6re innen tight\u00d7ATR(15m) fra niv\u00e5.
    HTF-niv\u00e5er (weight>=3) f\u00e5r litt mer toleranse.
    """
    tight = 0.30 if weight <= 1 else (0.35 if weight == 2 else 0.45)
    return abs(curr - level) <= atr_15m * tight


def merge_tagged_levels(tagged, curr, atr, max_n=6):
    """
    Sl\u00e5r sammen niv\u00e5er innen 0.5\u00d7ATR av hverandre.
    Beholder det med h\u00f8yest weight (tidsvindus-styrke).
    Sorterer etter n\u00e6rhet til n\u00e5pris.
    """
    if not tagged:
        return []
    atr_buf = (atr or 0) * 0.5
    merged = []
    for lvl in sorted(tagged, key=lambda x: abs(x["price"] - curr)):
        absorbed = False
        for m in merged:
            if atr_buf > 0 and abs(lvl["price"] - m["price"]) < atr_buf:
                if lvl["weight"] > m["weight"]:
                    m["price"] = lvl["price"]
                    m["source"] = lvl["source"]
                    m["weight"] = lvl["weight"]
                    for k in ("zone_top", "zone_bottom"):
                        if k in lvl:
                            m[k] = lvl[k]
                        else:
                            m.pop(k, None)
                absorbed = True
                break
        if not absorbed:
            merged.append(dict(lvl))
    return sorted(merged, key=lambda x: abs(x["price"] - curr))[:max_n]


def fmt_level(tagged, typ, atr, curr):
    """Formatterer niv\u00e5er for JSON-output."""
    out = []
    for i, l in enumerate(tagged[:5]):
        lr = round(l["price"], 5 if l["price"] < 100 else 2)
        out.append({
            "name": l.get("source", f"{typ}{i + 1}"),
            "level": lr,
            "weight": l.get("weight", 1),
            "dist_atr": round(abs(l["price"] - curr) / (atr or 1), 1),
        })
    return out


def build_tagged_levels(daily, h4, rows_15m, smc_15m, smc_1h, smc_4h,
                        curr, atr_15m, atr_d):
    """Bygger tagget niv\u00e5-hierarki med tidsvindus-vekting (1-5)."""
    pdh, pdl, pdc = get_pdh_pdl_pdc(daily)
    pwh, pwl = get_pwh_pwl(daily)

    raw_res, raw_sup = [], []

    if pwh and pwh > curr:
        raw_res.append({"price": pwh, "source": "PWH", "weight": 5})
    if pwl and pwl < curr:
        raw_sup.append({"price": pwl, "source": "PWL", "weight": 5})
    if pdh and pdh > curr:
        raw_res.append({"price": pdh, "source": "PDH", "weight": 4})
    if pdl and pdl < curr:
        raw_sup.append({"price": pdl, "source": "PDL", "weight": 4})
    if pdc:
        if pdc > curr:
            raw_res.append({"price": pdc, "source": "PDC", "weight": 3})
        elif pdc < curr:
            raw_sup.append({"price": pdc, "source": "PDC", "weight": 3})

    res_d, sup_d = find_swing_levels(daily)
    for r in res_d:
        if r > curr:
            raw_res.append({"price": r, "source": "D1", "weight": 3})
    for s in sup_d:
        if s < curr:
            raw_sup.append({"price": s, "source": "D1", "weight": 3})

    res_4h, sup_4h = find_swing_levels(h4, n=3) if len(h4) >= 10 else ([], [])
    for r in res_4h:
        if r > curr:
            raw_res.append({"price": r, "source": "4H", "weight": 2})
    for s in sup_4h:
        if s < curr:
            raw_sup.append({"price": s, "source": "4H", "weight": 2})

    for smc_data, src, w in [(smc_1h, "SMC1H", 3), (smc_4h, "SMC4H", 2),
                              (smc_15m, "SMC15m", 1)]:
        if smc_data:
            for z in smc_data.get("supply_zones", []):
                if z["poi"] > curr:
                    raw_res.append({"price": z["poi"], "source": src, "weight": w,
                                    "zone_top": z["top"], "zone_bottom": z["bottom"]})
            for z in smc_data.get("demand_zones", []):
                if z["poi"] < curr:
                    raw_sup.append({"price": z["poi"], "source": src, "weight": w,
                                    "zone_top": z["top"], "zone_bottom": z["bottom"]})

    res_15m, sup_15m = find_intraday_levels(rows_15m) if rows_15m else ([], [])
    for r in res_15m:
        if r > curr:
            raw_res.append({"price": r, "source": "15m", "weight": 1})
    for s in sup_15m:
        if s < curr:
            raw_sup.append({"price": s, "source": "15m", "weight": 1})

    atr_for_merge = atr_15m if atr_15m else (atr_d * 0.4 if atr_d else None)
    tagged_res = merge_tagged_levels(raw_res, curr, atr_for_merge)
    tagged_sup = merge_tagged_levels(raw_sup, curr, atr_for_merge)
    return tagged_res, tagged_sup, atr_for_merge
