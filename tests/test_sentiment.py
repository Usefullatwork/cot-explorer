"""Tester for sentiment.py — konflikter og bin\u00e6r risiko."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sentiment import detect_conflict


def test_detect_conflict_vix_dxy():
    conflicts = detect_conflict(vix=30, dxy_5d=-2, fg=None, cot_usd=0)
    assert any("VIX" in c for c in conflicts)


def test_detect_conflict_fear_dxy():
    fg = {"score": 20}
    conflicts = detect_conflict(vix=15, dxy_5d=-2, fg=fg, cot_usd=0)
    assert any("frykt" in c for c in conflicts)


def test_detect_conflict_greed_vix():
    fg = {"score": 75}
    conflicts = detect_conflict(vix=25, dxy_5d=0, fg=fg, cot_usd=0)
    assert any("VIX" in c for c in conflicts)


def test_detect_conflict_hy_stress():
    conflicts = detect_conflict(vix=15, dxy_5d=0, fg=None, cot_usd=0,
                                hy_stress=True)
    assert any("HY" in c for c in conflicts)


def test_detect_conflict_yield_curve():
    conflicts = detect_conflict(vix=15, dxy_5d=0, fg=None, cot_usd=0,
                                yield_curve=-0.5)
    assert any("Rentekurve" in c for c in conflicts)


def test_detect_conflict_no_conflicts():
    conflicts = detect_conflict(vix=15, dxy_5d=1, fg={"score": 50}, cot_usd=0)
    assert conflicts == []


def test_detect_conflict_news_vs_vix():
    news = {"label": "risk_on"}
    conflicts = detect_conflict(vix=30, dxy_5d=0, fg=None, cot_usd=0,
                                news_sent=news)
    assert any("Nyheter" in c for c in conflicts)
