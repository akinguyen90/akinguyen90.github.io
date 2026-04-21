#!/usr/bin/env python3
"""Fetch current weather for major Vietnamese cities from Open-Meteo.

Writes the result to data/weather.json. Run by .github/workflows/weather.yml
once per hour.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CITIES = [
    {"name": "Hanoi",            "name_ja": "ハノイ",     "lat": 21.0285, "lon": 105.8542},
    {"name": "Ho Chi Minh City", "name_ja": "ホーチミン", "lat": 10.8231, "lon": 106.6297},
    {"name": "Da Nang",          "name_ja": "ダナン",     "lat": 16.0544, "lon": 108.2022},
    {"name": "Hue",              "name_ja": "フエ",       "lat": 16.4637, "lon": 107.5909},
    {"name": "Hai Phong",        "name_ja": "ハイフォン", "lat": 20.8449, "lon": 106.6881},
    {"name": "Can Tho",          "name_ja": "カントー",   "lat": 10.0452, "lon": 105.7469},
    {"name": "Nha Trang",        "name_ja": "ニャチャン", "lat": 12.2388, "lon": 109.1968},
    {"name": "Da Lat",           "name_ja": "ダラット",   "lat": 11.9404, "lon": 108.4583},
]

API_BASE = "https://api.open-meteo.com/v1/forecast"
CURRENT_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "weather_code",
    "wind_speed_10m",
    "is_day",
]


def fetch_city(city: dict) -> dict:
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "current": ",".join(CURRENT_FIELDS),
        "timezone": "Asia/Ho_Chi_Minh",
        "wind_speed_unit": "kmh",
    }
    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "akinguyen90.github.io weather updater"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)

    c = data["current"]
    return {
        "name": city["name"],
        "name_ja": city["name_ja"],
        "lat": city["lat"],
        "lon": city["lon"],
        "temperature": c["temperature_2m"],
        "apparent_temperature": c["apparent_temperature"],
        "humidity": c["relative_humidity_2m"],
        "wind_speed": c["wind_speed_10m"],
        "weather_code": c["weather_code"],
        "is_day": c["is_day"],
        "local_time": c["time"],
    }


def main() -> int:
    results = []
    errors = 0
    for city in CITIES:
        try:
            results.append(fetch_city(city))
            print(f"OK   {city['name']}")
        except Exception as e:
            errors += 1
            print(f"FAIL {city['name']}: {e}", file=sys.stderr)
            results.append({
                "name": city["name"],
                "name_ja": city["name_ja"],
                "lat": city["lat"],
                "lon": city["lon"],
                "error": str(e),
            })

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "https://open-meteo.com/",
        "cities": results,
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "weather.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(results)} cities, {errors} errors)")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
