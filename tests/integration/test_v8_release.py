from pathlib import Path

import httpx
import pytest

from app.weather.client import search_locations


def _payload(surface: str = "mixed"):
    return {
        "location": {"city": "Jakarta", "latitude": -6.2, "longitude": 106.8, "elevation_m": 8},
        "plot": {"shape": "rectangle", "length_m": 4, "width_m": 3, "sun_direction": "north"},
        "surface": surface,
        "sunlight": "full",
        "care_commitment": "regular",
        "primary_goal": "kitchen",
        "desired_crops": [],
        "excluded_crops": [],
        "vertical_allowed": True,
        "tiered_rack_allowed": True,
        "water_access": "normal",
        "child_or_pet_concerns": False,
        "container_depth_cm": 45,
        "language": "en",
    }


def test_build_endpoint_and_versioned_browser_assets(client):
    build = client.get("/api/v1/build")
    assert build.status_code == 200
    assert build.json()["build"] == "8.2.0"
    index = client.get("/")
    assert index.status_code == 200
    assert "app.v8.2.js" in index.text
    assert "styles.v8.2.css" in index.text
    assert index.headers["x-groe-build"] == "8.2.0"
    assert "no-store" in index.headers["cache-control"]


@pytest.mark.asyncio
async def test_location_search_keeps_working_when_provider_fails(monkeypatch):
    class FailingClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return False
        async def get(self, *args, **kwargs): raise httpx.ConnectError("offline")

    monkeypatch.setattr("app.weather.client.httpx.AsyncClient", lambda *args, **kwargs: FailingClient())
    items = await search_locations("Jak", "en")
    assert items
    assert items[0]["name"] == "Jakarta"
    assert items[0]["source"] == "curated_indonesia_fallback"
    assert isinstance(items[0]["latitude"], float)


def test_mixed_surface_returns_soil_and_container_footprints(client, monkeypatch):
    async def fake_weather(*args, **kwargs):
        return {"mean_temperature_c": 28, "provider_available": True}
    monkeypatch.setattr("app.api.routes.planner.get_weather_context", fake_weather)
    response = client.post("/api/v1/planner/recommendations", json=_payload("mixed"))
    assert response.status_code == 200, response.text
    shapes = {placement["shape"] for plan in response.json()["plans"] for placement in plan["layout"]["placements"]}
    assert "soil" in shapes
    assert "container" in shapes


def test_static_ui_contains_all_client_feedback_components():
    js = Path("backend/app/static/assets/app.v8.2.js").read_text()
    css = Path("backend/app/static/assets/styles.v8.2.css").read_text()
    assert 'request("/plants?page_size=50")' not in js
    assert 'data-view="plants"' not in js
    assert "Use my current location" in js
    assert "Refresh" in js
    assert "Plant key" in js
    assert "Hanging pot" in js
    assert "Plant stand / rack" in js
    assert "Trellis" in js
    assert ".legend-hanging" in css
    assert ".legend-rack" in css
    assert ".legend-trellis" in css
    assert "Pot sizes included in the space calculation" in js
    assert "recommendation-plant-card" in js
    assert "No sign-in needed for testing" in js
    assert "Guest beta" in js
    assert "LOCAL_GARDENS_KEY" in js
    assert "data-action=\"open-auth\"" not in js[js.index("function header"):js.index("function landing")]
    assert "Beta build" in js
    assert ".crop-map-key" in css
    assert ".pot-summary" in css


def test_v82_static_map_has_external_sun_compass_and_explicit_assignments():
    js = Path("backend/app/static/assets/app.v8.2.js").read_text()
    css = Path("backend/app/static/assets/styles.v8.2.css").read_text()
    assert "Strongest light:" in js
    assert "Cahaya terkuat:" in js
    assert 'class="compass"' in js
    assert "Vertical placement assignments" in js
    assert "Rack Tier" in js
    assert "detected_crops" in js
    assert ".vertical-assignment-summary" in css
    assert ".detected-crop-list" in css
