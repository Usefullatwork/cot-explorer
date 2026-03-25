"""Tester for indicators.py — ATR, EMA, tidsrammekonvertering."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from indicators import calc_atr, calc_ema, to_4h, get_pdh_pdl_pdc, get_pwh_pwl, get_session_status


def test_calc_atr_basic(sample_daily_rows):
    result = calc_atr(sample_daily_rows, 14)
    assert result is not None
    assert result > 0


def test_calc_atr_insufficient_data():
    rows = [(1.10, 1.09, 1.095)] * 5
    assert calc_atr(rows, 14) is None


def test_calc_ema_basic():
    closes = [1.08, 1.09, 1.10, 1.11, 1.10, 1.09, 1.08, 1.09, 1.10, 1.11, 1.12]
    result = calc_ema(closes, 9)
    assert result is not None
    assert 1.08 < result < 1.12


def test_calc_ema_insufficient_data():
    closes = [1.08, 1.09, 1.10]
    assert calc_ema(closes, 9) is None


def test_to_4h_groups_correctly(sample_1h_rows):
    h4 = to_4h(sample_1h_rows)
    assert len(h4) == len(sample_1h_rows) // 4
    for h, l, c in h4:
        assert h >= c
        assert l <= c


def test_get_pdh_pdl_pdc(sample_daily_rows):
    pdh, pdl, pdc = get_pdh_pdl_pdc(sample_daily_rows)
    assert pdh is not None
    assert pdl is not None
    assert pdc is not None
    assert pdh >= pdl


def test_get_pdh_pdl_pdc_insufficient():
    assert get_pdh_pdl_pdc([(1.10, 1.09, 1.095)]) == (None, None, None)


def test_get_pwh_pwl(sample_daily_rows):
    pwh, pwl = get_pwh_pwl(sample_daily_rows)
    assert pwh is not None
    assert pwl is not None
    assert pwh >= pwl


def test_get_session_status_returns_dict():
    result = get_session_status()
    assert "active" in result
    assert "label" in result
    assert "cet_hour" in result
    assert isinstance(result["active"], bool)
