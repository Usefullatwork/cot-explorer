"""Tester for config.py — datastruktur-validering."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import INSTRUMENTS, COT_MAP, STOOQ_MAP, NEWS_CONFIRMS_MAP


def test_instruments_have_required_keys():
    required = {"key", "navn", "symbol", "label", "kat", "klasse", "session"}
    for inst in INSTRUMENTS:
        missing = required - set(inst.keys())
        assert not missing, f"{inst['key']} mangler: {missing}"


def test_instruments_count():
    assert len(INSTRUMENTS) == 12


def test_cot_map_covers_tradeable():
    tradeable = {i["key"] for i in INSTRUMENTS if i["key"] not in ("VIX", "AUDUSD")}
    for key in tradeable:
        assert key in COT_MAP, f"{key} mangler i COT_MAP"


def test_stooq_map_covers_symbols():
    symbols = {i["symbol"] for i in INSTRUMENTS}
    for sym in symbols:
        assert sym in STOOQ_MAP, f"{sym} mangler i STOOQ_MAP"


def test_news_confirms_map_covers_instruments():
    for inst in INSTRUMENTS:
        assert inst["key"] in NEWS_CONFIRMS_MAP, f"{inst['key']} mangler i NEWS_CONFIRMS_MAP"


def test_klasse_values():
    valid = {"A", "B", "C"}
    for inst in INSTRUMENTS:
        assert inst["klasse"] in valid, f"{inst['key']} har ugyldig klasse: {inst['klasse']}"
