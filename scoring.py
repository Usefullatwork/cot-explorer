#!/usr/bin/env python3
"""Konfluens-scoring — 12-punkt vurdering med tidshorisonts-klassifisering."""


def compute_score(above_sma, chg20_confirms, cot_confirms, cot_strong,
                  at_level_now, htf_level_nearby, trend_aligned,
                  no_event_risk, news_confirms_dir, fund_confirms,
                  bos_confirms, smc_struct_confirms,
                  sesjon_aktiv, vix_price):
    """
    Beregner konfluens-score fra 12 boolske kriterier.

    Returnerer (score_details, score, grade, grade_color, timeframe_bias, pos_size).
    """
    score_details = [
        {"kryss": "Over SMA200 (D1 trend)", "verdi": above_sma},
        {"kryss": "Momentum 20d bekrefter", "verdi": chg20_confirms},
        {"kryss": "COT bekrefter retning", "verdi": cot_confirms},
        {"kryss": "COT sterk posisjonering (>10%)", "verdi": cot_strong},
        {"kryss": "Pris VED HTF-niv\u00e5 n\u00e5", "verdi": at_level_now},
        {"kryss": "HTF-niv\u00e5 D1/Ukentlig", "verdi": htf_level_nearby},
        {"kryss": "D1 + 4H trend kongruent", "verdi": trend_aligned},
        {"kryss": "Ingen event-risiko (4t)", "verdi": no_event_risk},
        {"kryss": "Nyhetssentiment bekrefter", "verdi": news_confirms_dir},
        {"kryss": "Fundamental bekrefter", "verdi": fund_confirms},
        {"kryss": "BOS 1H/4H bekrefter retning", "verdi": bos_confirms},
        {"kryss": "SMC 1H struktur bekrefter", "verdi": smc_struct_confirms},
    ]
    score = sum(1 for s in score_details if s["verdi"])
    max_score = len(score_details)

    # Karakter
    if score >= 11:
        grade, grade_color = "A+", "bull"
    elif score >= 9:
        grade, grade_color = "A", "warn"
    elif score >= 6:
        grade, grade_color = "B", "bear"
    else:
        grade, grade_color = "C", "bear"

    # Tidshorisont
    if score >= 6 and cot_confirms and htf_level_nearby:
        timeframe_bias = "MAKRO"
    elif score >= 4 and htf_level_nearby:
        timeframe_bias = "SWING"
    elif score >= 2 and at_level_now and sesjon_aktiv:
        timeframe_bias = "SCALP"
    else:
        timeframe_bias = "WATCHLIST"

    # Posisjonsstorrelse basert p\u00e5 VIX
    if vix_price < 20:
        pos_size = "Full"
    elif vix_price < 30:
        pos_size = "Halv"
    else:
        pos_size = "Kvart"

    return score_details, score, max_score, grade, grade_color, timeframe_bias, pos_size
