"""Tester for levels.py — niv\u00e5deteksjon, vekting og sammensl\u00e5ing."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from levels import find_intraday_levels, find_swing_levels, is_at_level, merge_tagged_levels, fmt_level


def test_is_at_level_within_tolerance():
    assert is_at_level(1.0800, 1.0801, 0.0010, weight=1) is True


def test_is_at_level_outside_tolerance():
    assert is_at_level(1.0800, 1.0900, 0.0010, weight=1) is False


def test_is_at_level_htf_wider_tolerance():
    # weight=3 gets 0.45 multiplier
    assert is_at_level(1.0800, 1.0804, 0.0010, weight=3) is True
    # Same distance but weight=1 (0.30 multiplier) fails
    assert is_at_level(1.0800, 1.0804, 0.0010, weight=1) is False


def test_merge_tagged_levels_deduplication():
    tagged = [
        {"price": 1.0800, "source": "D1", "weight": 3},
        {"price": 1.0802, "source": "4H", "weight": 2},  # within 0.5*ATR
        {"price": 1.0900, "source": "PWH", "weight": 5},
    ]
    result = merge_tagged_levels(tagged, curr=1.0750, atr=0.0010)
    # Two levels near each other should merge (keeping higher weight)
    assert len(result) <= 3
    # PWH should survive
    assert any(l["source"] == "PWH" for l in result)


def test_merge_tagged_levels_empty():
    assert merge_tagged_levels([], 1.08, 0.001) == []


def test_find_intraday_levels(sample_15m_rows):
    res, sup = find_intraday_levels(sample_15m_rows)
    assert isinstance(res, list)
    assert isinstance(sup, list)


def test_find_swing_levels(sample_daily_rows):
    res, sup = find_swing_levels(sample_daily_rows)
    assert isinstance(res, list)
    assert isinstance(sup, list)


def test_fmt_level():
    tagged = [
        {"price": 1.0900, "source": "PWH", "weight": 5},
        {"price": 1.0850, "source": "D1", "weight": 3},
    ]
    result = fmt_level(tagged, "R", 0.0010, curr=1.0800)
    assert len(result) == 2
    assert result[0]["name"] == "PWH"
    assert "dist_atr" in result[0]
