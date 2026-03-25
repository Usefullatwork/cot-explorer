"""Tester for scoring.py — karakter, tidshorisont og posisjonsstorrelse."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scoring import compute_score


def _make_score(**overrides):
    """Hjelpefunksjon: alle False/20 som standard, override etter behov."""
    defaults = dict(
        above_sma=False, chg20_confirms=False, cot_confirms=False,
        cot_strong=False, at_level_now=False, htf_level_nearby=False,
        trend_aligned=False, no_event_risk=False, news_confirms_dir=False,
        fund_confirms=False, bos_confirms=False, smc_struct_confirms=False,
        sesjon_aktiv=False, vix_price=20.0,
    )
    defaults.update(overrides)
    return compute_score(**defaults)


def test_grade_c_when_all_false():
    details, score, max_score, grade, color, tf, pos = _make_score()
    assert score == 0
    assert grade == "C"
    assert max_score == 12


def test_grade_a_plus_when_all_true():
    all_true = {k: True for k in [
        "above_sma", "chg20_confirms", "cot_confirms", "cot_strong",
        "at_level_now", "htf_level_nearby", "trend_aligned", "no_event_risk",
        "news_confirms_dir", "fund_confirms", "bos_confirms", "smc_struct_confirms",
    ]}
    details, score, max_score, grade, color, tf, pos = _make_score(**all_true)
    assert score == 12
    assert grade == "A+"
    assert color == "bull"


def test_grade_thresholds():
    _, s9, _, g9, _, _, _ = _make_score(
        above_sma=True, chg20_confirms=True, cot_confirms=True,
        cot_strong=True, at_level_now=True, htf_level_nearby=True,
        trend_aligned=True, no_event_risk=True, news_confirms_dir=True,
    )
    assert s9 == 9
    assert g9 == "A"

    _, s6, _, g6, _, _, _ = _make_score(
        above_sma=True, chg20_confirms=True, cot_confirms=True,
        cot_strong=True, at_level_now=True, htf_level_nearby=True,
    )
    assert s6 == 6
    assert g6 == "B"


def test_timeframe_makro():
    _, _, _, _, _, tf, _ = _make_score(
        above_sma=True, chg20_confirms=True, cot_confirms=True,
        cot_strong=True, at_level_now=True, htf_level_nearby=True,
        trend_aligned=True, no_event_risk=True,
    )
    assert tf == "MAKRO"


def test_timeframe_scalp():
    _, _, _, _, _, tf, _ = _make_score(
        above_sma=True, at_level_now=True, sesjon_aktiv=True,
    )
    # score=1 (above_sma) + at_level_now needs score>=2
    assert tf in ("SCALP", "WATCHLIST")


def test_pos_size_full():
    _, _, _, _, _, _, pos = _make_score(vix_price=15)
    assert pos == "Full"


def test_pos_size_halv():
    _, _, _, _, _, _, pos = _make_score(vix_price=25)
    assert pos == "Halv"


def test_pos_size_kvart():
    _, _, _, _, _, _, pos = _make_score(vix_price=35)
    assert pos == "Kvart"
