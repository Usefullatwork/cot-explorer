"""Delte test-fixtures for COT Explorer."""
import pytest


@pytest.fixture
def sample_daily_rows():
    """250 daglige (h, l, c) tupler med realistiske EUR/USD-verdier."""
    import random
    random.seed(42)
    rows = []
    base = 1.0800
    for i in range(250):
        c = base + random.uniform(-0.0050, 0.0050)
        h = c + random.uniform(0.0005, 0.0030)
        l = c - random.uniform(0.0005, 0.0030)
        rows.append((round(h, 5), round(l, 5), round(c, 5)))
        base = c
    return rows


@pytest.fixture
def sample_15m_rows():
    """500 15-minutt (h, l, c) tupler med tettere range."""
    import random
    random.seed(43)
    rows = []
    base = 1.0850
    for i in range(500):
        c = base + random.uniform(-0.0008, 0.0008)
        h = c + random.uniform(0.0001, 0.0005)
        l = c - random.uniform(0.0001, 0.0005)
        rows.append((round(h, 5), round(l, 5), round(c, 5)))
        base = c
    return rows


@pytest.fixture
def sample_1h_rows():
    """200 1-times (h, l, c) tupler."""
    import random
    random.seed(44)
    rows = []
    base = 1.0820
    for i in range(200):
        c = base + random.uniform(-0.0015, 0.0015)
        h = c + random.uniform(0.0002, 0.0010)
        l = c - random.uniform(0.0002, 0.0010)
        rows.append((round(h, 5), round(l, 5), round(c, 5)))
        base = c
    return rows


@pytest.fixture
def sample_cot_data():
    """Dict matching data/combined/latest.json-struktur."""
    return {
        "euro fx": {
            "market": "Euro FX",
            "date": "2026-03-18",
            "report": "TFF",
            "open_interest": 500000,
            "spekulanter": {"long": 180000, "short": 120000, "net": 60000},
            "change_spec_net": 5000,
        },
        "gold": {
            "market": "Gold",
            "date": "2026-03-18",
            "report": "TFF",
            "open_interest": 400000,
            "spekulanter": {"long": 250000, "short": 100000, "net": 150000},
            "change_spec_net": -3000,
        },
    }


@pytest.fixture
def sample_calendar_events():
    """Liste av kalender-events med impact, hours_away, berorte."""
    return [
        {"title": "Non-Farm Payrolls", "impact": "High", "hours_away": 2,
         "cet": "14:30", "country": "USD", "berorte": ["EURUSD", "GBPUSD", "Gold", "DXY"]},
        {"title": "ECB Rate Decision", "impact": "High", "hours_away": 6,
         "cet": "13:45", "country": "EUR", "berorte": ["EURUSD"]},
        {"title": "UK Retail Sales", "impact": "Medium", "hours_away": 1,
         "cet": "08:00", "country": "GBP", "berorte": ["GBPUSD"]},
    ]
