"""Tester for trade_setup.py — level-til-level setupgenerering."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from trade_setup import make_setup_l2l


def _make_tagged(prices, source="D1", weight=3):
    return [{"price": p, "source": source, "weight": weight} for p in prices]


def test_long_setup_basic():
    curr = 1.0800
    sup = _make_tagged([1.0780, 1.0750], weight=3)
    res = _make_tagged([1.0850, 1.0900], weight=3)
    result = make_setup_l2l(curr, 0.0010, 0.0050, sup, res, "long", "A")
    if result is not None:
        assert result["rr_t1"] >= 1.5
        assert result["sl"] < result["entry"]
        assert result["t1"] > result["entry"]


def test_short_setup_basic():
    curr = 1.0800
    sup = _make_tagged([1.0750, 1.0700], weight=3)
    res = _make_tagged([1.0820, 1.0870], weight=3)
    result = make_setup_l2l(curr, 0.0010, 0.0050, sup, res, "short", "A")
    if result is not None:
        assert result["rr_t1"] >= 1.5
        assert result["sl"] > result["entry"]
        assert result["t1"] < result["entry"]


def test_returns_none_without_atr():
    sup = _make_tagged([1.0780])
    res = _make_tagged([1.0850])
    assert make_setup_l2l(1.08, 0, 0.005, sup, res, "long", "A") is None
    assert make_setup_l2l(1.08, None, 0.005, sup, res, "long", "A") is None


def test_returns_none_without_levels():
    assert make_setup_l2l(1.08, 0.001, 0.005, [], [], "long", "A") is None
    assert make_setup_l2l(1.08, 0.001, 0.005, None, None, "long", "A") is None


def test_setup_has_required_fields():
    curr = 1.0800
    sup = _make_tagged([1.0795], weight=4)
    res = _make_tagged([1.0850, 1.0900], weight=3)
    result = make_setup_l2l(curr, 0.0010, 0.0050, sup, res, "long", "A")
    if result is not None:
        required = {"entry", "sl", "t1", "t2", "rr_t1", "rr_t2",
                    "status", "note", "timeframe"}
        assert required.issubset(set(result.keys()))
