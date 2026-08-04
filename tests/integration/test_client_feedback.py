from pathlib import Path


def planner_payload():
    return {
        "location": {
            "city": "Jakarta",
            "latitude": -6.2,
            "longitude": 106.8,
            "elevation_m": 8,
        },
        "plot": {"shape": "rectangle", "length_m": 2, "width_m": 1.5, "sun_direction": "north"},
        "surface": "containers",
        "sunlight": "partial",
        "care_commitment": "regular",
        "primary_goal": "kitchen",
        "desired_crops": [],
        "excluded_crops": [],
        "vertical_allowed": True,
        "tiered_rack_allowed": True,
        "water_access": "normal",
        "child_or_pet_concerns": False,
        "container_depth_cm": 35,
        "language": "en",
    }


def test_container_specs_are_returned_and_used_in_layout(client, monkeypatch):
    async def fake_weather(*args, **kwargs):
        return {"mean_temperature_c": 28, "provider_available": True}

    monkeypatch.setattr("app.api.routes.planner.get_weather_context", fake_weather)
    response = client.post("/api/v1/planner/recommendations", json=planner_payload())
    assert response.status_code == 200, response.text
    for plan in response.json()["plans"]:
        for crop in plan["crops"]:
            assert crop["container_spec"]["recommended_diameter_cm"] >= crop["container_spec"]["minimum_diameter_cm"]
            assert crop["container_spec"]["recommended_depth_cm"] >= crop["container_spec"]["minimum_depth_cm"]
        for placement in plan["layout"]["placements"]:
            assert placement["structure_type"] in {"pot", "hanging_pot", "rack_pot"}
            assert placement["container_spec"]
            expected = placement["container_spec"]["recommended_diameter_cm"] / 100
            assert abs(placement["width_m"] - expected) < 0.001


def test_guest_diary_advice_works_without_sign_in(client):
    response = client.post(
        "/api/v1/diary/guest-advice",
        json={
            "plan_data": {
                "environment": {"seven_day_rain_mm": 55},
                "crops": [
                    {"slug": "kangkung", "name_en": "Water spinach", "name_id": "Kangkung"},
                    {"slug": "caisim", "name_en": "Choy sum", "name_id": "Caisim / sawi hijau"},
                ],
            },
            "planner_input": planner_payload(),
            "crop": {"name_en": "Water spinach", "name_id": "Kangkung"},
            "previous_entries": [],
            "growth_stage": "vegetative",
            "entry_text": "Caisimnya layu dan pot masih basah.",
            "user_question": "Apa yang perlu saya periksa?",
            "language": "id",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["provider_status"] in {"deterministic_fallback", "ai_provider"}
    assert body["detected_crop_slug"] == "caisim"
    assert "Caisim" in body["detected_crop_name"]
    assert "Kangkung" not in body["ai_response"]
    assert body["clarification_needed"] is False


def test_weather_routes_expose_location_and_live_metrics(client, monkeypatch):
    async def fake_locations(query, language):
        return [{"name": "Jakarta", "display_name": "Jakarta, DKI Jakarta", "latitude": -6.2, "longitude": 106.8}]

    async def fake_context(city, latitude, longitude, elevation_m, language):
        return {
            "provider": "open_meteo",
            "provider_available": True,
            "weather_label": "Clear sky",
            "current_temperature_c": 30,
            "humidity_percent": 72,
            "precipitation_mm": 0,
            "wind_speed_kmh": 8,
        }

    monkeypatch.setattr("app.api.routes.weather.search_locations", fake_locations)
    monkeypatch.setattr("app.api.routes.weather.get_weather_context", fake_context)
    locations = client.get("/api/v1/weather/locations?q=Jak&language=en")
    assert locations.status_code == 200
    assert locations.json()["items"][0]["display_name"].startswith("Jakarta")
    weather = client.get("/api/v1/weather/context?city=Jakarta&latitude=-6.2&longitude=106.8&language=en")
    assert weather.status_code == 200
    assert weather.json()["humidity_percent"] == 72


def test_public_navigation_hides_database_catalog():
    app_js = Path("backend/app/static/assets/app.v8.2.js").read_text()
    header_block = app_js[app_js.index("function header"):app_js.index("function landing")]
    assert 'data-view="plants"' not in header_block


def test_guest_diary_handles_two_named_crops_and_spelling_variants(client):
    response = client.post(
        "/api/v1/diary/guest-advice",
        json={
            "plan_data": {
                "environment": {},
                "crops": [
                    {"slug": "pakcoy", "name_en": "Pak choi", "name_id": "Pakcoy"},
                    {"slug": "caisim", "name_en": "Choy sum", "name_id": "Caisim / sawi hijau"},
                    {"slug": "kangkung", "name_en": "Water spinach", "name_id": "Kangkung"},
                ],
            },
            "planner_input": planner_payload(),
            "previous_entries": [],
            "growth_stage": "vegetative",
            "entry_text": "pokcoy pendek ya, caisin agak berbintik putih di ujung daun",
            "user_question": None,
            "language": "id",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert [item["slug"] for item in body["detected_crops"]] == ["pakcoy", "caisim"]
    assert body["clarification_needed"] is False
    assert "Pakcoy" in body["ai_response"]
    assert "Caisim" in body["ai_response"]
    assert "Kangkung" not in body["ai_response"]
