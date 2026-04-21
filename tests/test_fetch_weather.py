"""Tests for scripts/fetch_weather.py."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_weather as fw  # noqa: E402


MOCK_CURRENT = {
    "current": {
        "time": "2026-04-21T17:30",
        "temperature_2m": 29.3,
        "relative_humidity_2m": 77,
        "apparent_temperature": 33.5,
        "weather_code": 3,
        "wind_speed_10m": 16.8,
        "is_day": 1,
    }
}


class FakeResponse:
    """Minimal stand-in for the context manager urlopen returns."""

    def __init__(self, payload):
        self._bytes = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self._bytes


class FetchCityTests(unittest.TestCase):
    def setUp(self):
        self.city = {"name": "Hanoi", "name_ja": "ハノイ", "lat": 21.0, "lon": 105.8}

    def test_parses_response_into_expected_shape(self):
        with patch("urllib.request.urlopen", return_value=FakeResponse(MOCK_CURRENT)):
            result = fw.fetch_city(self.city)

        self.assertEqual(result["name"], "Hanoi")
        self.assertEqual(result["name_ja"], "ハノイ")
        self.assertEqual(result["lat"], 21.0)
        self.assertEqual(result["lon"], 105.8)
        self.assertEqual(result["temperature"], 29.3)
        self.assertEqual(result["apparent_temperature"], 33.5)
        self.assertEqual(result["humidity"], 77)
        self.assertEqual(result["wind_speed"], 16.8)
        self.assertEqual(result["weather_code"], 3)
        self.assertEqual(result["is_day"], 1)
        self.assertEqual(result["local_time"], "2026-04-21T17:30")

    def test_hits_open_meteo_with_requested_params(self):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            captured["timeout"] = timeout
            return FakeResponse(MOCK_CURRENT)

        with patch("urllib.request.urlopen", fake_urlopen):
            fw.fetch_city(self.city)

        url = captured["url"]
        self.assertIn("api.open-meteo.com/v1/forecast", url)
        self.assertIn("latitude=21.0", url)
        self.assertIn("longitude=105.8", url)
        self.assertIn("temperature_2m", url)
        self.assertIn("weather_code", url)
        self.assertIn("timezone=Asia%2FHo_Chi_Minh", url)
        self.assertEqual(captured["timeout"], 30)

    def test_propagates_http_errors(self):
        def boom(req, timeout):
            raise RuntimeError("network down")

        with patch("urllib.request.urlopen", boom):
            with self.assertRaises(RuntimeError):
                fw.fetch_city(self.city)


class CitiesConstantTests(unittest.TestCase):
    def test_all_cities_have_required_fields(self):
        required = {"name", "name_ja", "lat", "lon"}
        for city in fw.CITIES:
            missing = required - city.keys()
            self.assertFalse(missing, f"{city.get('name')} missing {missing}")

    def test_coordinates_within_vietnam_bounding_box(self):
        # Vietnam: roughly 8°–24°N, 102°–110°E
        for city in fw.CITIES:
            self.assertTrue(8 <= city["lat"] <= 24, f"{city['name']} lat out of range")
            self.assertTrue(102 <= city["lon"] <= 110, f"{city['name']} lon out of range")

    def test_city_names_are_unique(self):
        names = [c["name"] for c in fw.CITIES]
        self.assertEqual(len(names), len(set(names)))

    def test_expected_major_cities_present(self):
        names = {c["name"] for c in fw.CITIES}
        for required in ("Hanoi", "Ho Chi Minh City", "Da Nang"):
            self.assertIn(required, names)


class MainTests(unittest.TestCase):
    def test_writes_output_file_with_all_cities(self):
        tmp_cities = [
            {"name": "A", "name_ja": "A都市", "lat": 10.0, "lon": 106.0},
            {"name": "B", "name_ja": "B都市", "lat": 11.0, "lon": 107.0},
        ]
        tmp_out = ROOT / "data" / "weather.test.json"
        try:
            with patch("urllib.request.urlopen", return_value=FakeResponse(MOCK_CURRENT)):
                with patch.object(fw, "CITIES", tmp_cities):
                    rc = fw.main(out_path=tmp_out)
            self.assertEqual(rc, 0)
            payload = json.loads(tmp_out.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["cities"]), 2)
            self.assertIn("updated_at", payload)
            self.assertEqual(payload["cities"][0]["name"], "A")
        finally:
            tmp_out.unlink(missing_ok=True)

    def test_partial_failure_records_error_and_returns_nonzero(self):
        calls = {"n": 0}

        def flaky(req, timeout):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("upstream 503")
            return FakeResponse(MOCK_CURRENT)

        tmp_cities = [
            {"name": "A", "name_ja": "A", "lat": 10.0, "lon": 106.0},
            {"name": "B", "name_ja": "B", "lat": 11.0, "lon": 107.0},
        ]
        tmp_out = ROOT / "data" / "weather.test.json"
        try:
            with patch("urllib.request.urlopen", flaky):
                with patch.object(fw, "CITIES", tmp_cities):
                    rc = fw.main(out_path=tmp_out)
            self.assertEqual(rc, 1)
            payload = json.loads(tmp_out.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["cities"]), 2)
            self.assertIn("error", payload["cities"][0])
            self.assertNotIn("error", payload["cities"][1])
        finally:
            tmp_out.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
