from __future__ import annotations

CITY_CLIMATE = {
    "jakarta": {"mean_temperature_c":29.0,"humidity_percent":78,"climate_label":"hot_lowland","confidence":"fallback"},
    "surabaya": {"mean_temperature_c":30.0,"humidity_percent":72,"climate_label":"hot_lowland","confidence":"fallback"},
    "bandung": {"mean_temperature_c":23.5,"humidity_percent":80,"climate_label":"cool_highland","confidence":"fallback"},
    "malang": {"mean_temperature_c":24.0,"humidity_percent":79,"climate_label":"cool_highland","confidence":"fallback"},
    "bogor": {"mean_temperature_c":26.0,"humidity_percent":84,"climate_label":"wet_lowland","confidence":"fallback"},
    "denpasar": {"mean_temperature_c":28.5,"humidity_percent":76,"climate_label":"hot_lowland","confidence":"fallback"},
    "yogyakarta": {"mean_temperature_c":27.5,"humidity_percent":78,"climate_label":"warm_lowland","confidence":"fallback"},
    "medan": {"mean_temperature_c":27.5,"humidity_percent":82,"climate_label":"humid_lowland","confidence":"fallback"},
    "makassar": {"mean_temperature_c":29.0,"humidity_percent":74,"climate_label":"hot_lowland","confidence":"fallback"},
}

def fallback_climate(city: str, elevation_m: float | None = None) -> dict:
    key=city.lower().split(",")[0].strip()
    if key in CITY_CLIMATE: return dict(CITY_CLIMATE[key])
    if elevation_m is not None and elevation_m>700:
        return {"mean_temperature_c":23.0,"humidity_percent":78,"climate_label":"estimated_highland","confidence":"reduced"}
    return {"mean_temperature_c":28.0,"humidity_percent":78,"climate_label":"estimated_indonesian_lowland","confidence":"reduced"}
