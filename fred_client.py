#!/usr/bin/env python3
"""
fred_client.py — Enkel wrapper for FRED API-kall.
Henter observasjoner for en gitt serie med sortering og grenseverdi.
"""
import json
import logging
import os
import urllib.request

log = logging.getLogger(__name__)

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")


def fetch_fred_api(series_id, limit=16):
    """Hent siste observasjoner fra FRED API for en gitt serie."""
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={FRED_API_KEY}"
        f"&file_type=json&sort_order=desc&limit={limit}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            d = json.loads(r.read())
        obs = []
        for o in d.get("observations", []):
            if o.get("value") not in (".", "", None):
                try:
                    obs.append((o["date"], float(o["value"])))
                except (ValueError, KeyError):
                    pass
        return list(reversed(obs))
    except Exception as e:
        log.error("FRED %s FEIL: %s", series_id, e)
        return []
