from __future__ import annotations

from typing import Any
import unicodedata

# Curated fallback for common Indonesian locations. Open-Meteo remains the
# primary geocoding provider; this list guarantees that autocomplete remains
# usable when that provider is temporarily unavailable.
LOCATIONS: tuple[dict[str, Any], ...] = (
    {"name":"Jakarta","admin1":"DKI Jakarta","latitude":-6.2088,"longitude":106.8456,"elevation":8},
    {"name":"Bandung","admin1":"Jawa Barat","latitude":-6.9175,"longitude":107.6191,"elevation":768},
    {"name":"Bogor","admin1":"Jawa Barat","latitude":-6.5971,"longitude":106.8060,"elevation":265},
    {"name":"Bekasi","admin1":"Jawa Barat","latitude":-6.2383,"longitude":106.9756,"elevation":19},
    {"name":"Depok","admin1":"Jawa Barat","latitude":-6.4025,"longitude":106.7942,"elevation":95},
    {"name":"Tangerang","admin1":"Banten","latitude":-6.1783,"longitude":106.6319,"elevation":14},
    {"name":"Tangerang Selatan","admin1":"Banten","latitude":-6.2889,"longitude":106.7181,"elevation":39},
    {"name":"Serang","admin1":"Banten","latitude":-6.1200,"longitude":106.1503,"elevation":39},
    {"name":"Cilegon","admin1":"Banten","latitude":-6.0025,"longitude":106.0111,"elevation":12},
    {"name":"Cirebon","admin1":"Jawa Barat","latitude":-6.7320,"longitude":108.5523,"elevation":5},
    {"name":"Sukabumi","admin1":"Jawa Barat","latitude":-6.9277,"longitude":106.9299,"elevation":584},
    {"name":"Tasikmalaya","admin1":"Jawa Barat","latitude":-7.3506,"longitude":108.2172,"elevation":351},
    {"name":"Semarang","admin1":"Jawa Tengah","latitude":-6.9667,"longitude":110.4167,"elevation":8},
    {"name":"Surakarta","admin1":"Jawa Tengah","latitude":-7.5755,"longitude":110.8243,"elevation":93},
    {"name":"Yogyakarta","admin1":"DI Yogyakarta","latitude":-7.7956,"longitude":110.3695,"elevation":113},
    {"name":"Magelang","admin1":"Jawa Tengah","latitude":-7.4706,"longitude":110.2177,"elevation":380},
    {"name":"Purwokerto","admin1":"Jawa Tengah","latitude":-7.4243,"longitude":109.2396,"elevation":75},
    {"name":"Tegal","admin1":"Jawa Tengah","latitude":-6.8797,"longitude":109.1256,"elevation":4},
    {"name":"Pekalongan","admin1":"Jawa Tengah","latitude":-6.8886,"longitude":109.6753,"elevation":4},
    {"name":"Surabaya","admin1":"Jawa Timur","latitude":-7.2575,"longitude":112.7521,"elevation":5},
    {"name":"Malang","admin1":"Jawa Timur","latitude":-7.9666,"longitude":112.6326,"elevation":506},
    {"name":"Batu","admin1":"Jawa Timur","latitude":-7.8671,"longitude":112.5239,"elevation":871},
    {"name":"Kediri","admin1":"Jawa Timur","latitude":-7.8480,"longitude":112.0178,"elevation":67},
    {"name":"Madiun","admin1":"Jawa Timur","latitude":-7.6298,"longitude":111.5239,"elevation":63},
    {"name":"Jember","admin1":"Jawa Timur","latitude":-8.1737,"longitude":113.7006,"elevation":89},
    {"name":"Banyuwangi","admin1":"Jawa Timur","latitude":-8.2192,"longitude":114.3691,"elevation":25},
    {"name":"Denpasar","admin1":"Bali","latitude":-8.6705,"longitude":115.2126,"elevation":4},
    {"name":"Mataram","admin1":"Nusa Tenggara Barat","latitude":-8.5833,"longitude":116.1167,"elevation":26},
    {"name":"Kupang","admin1":"Nusa Tenggara Timur","latitude":-10.1772,"longitude":123.6070,"elevation":62},
    {"name":"Medan","admin1":"Sumatera Utara","latitude":3.5952,"longitude":98.6722,"elevation":21},
    {"name":"Binjai","admin1":"Sumatera Utara","latitude":3.6001,"longitude":98.4854,"elevation":28},
    {"name":"Pematangsiantar","admin1":"Sumatera Utara","latitude":2.9595,"longitude":99.0687,"elevation":400},
    {"name":"Padang","admin1":"Sumatera Barat","latitude":-0.9471,"longitude":100.4172,"elevation":8},
    {"name":"Bukittinggi","admin1":"Sumatera Barat","latitude":-0.3056,"longitude":100.3692,"elevation":930},
    {"name":"Pekanbaru","admin1":"Riau","latitude":0.5071,"longitude":101.4478,"elevation":12},
    {"name":"Batam","admin1":"Kepulauan Riau","latitude":1.0456,"longitude":104.0305,"elevation":14},
    {"name":"Palembang","admin1":"Sumatera Selatan","latitude":-2.9909,"longitude":104.7566,"elevation":8},
    {"name":"Bandar Lampung","admin1":"Lampung","latitude":-5.3971,"longitude":105.2668,"elevation":93},
    {"name":"Banda Aceh","admin1":"Aceh","latitude":5.5483,"longitude":95.3238,"elevation":2},
    {"name":"Jambi","admin1":"Jambi","latitude":-1.6101,"longitude":103.6131,"elevation":16},
    {"name":"Bengkulu","admin1":"Bengkulu","latitude":-3.8004,"longitude":102.2655,"elevation":7},
    {"name":"Pontianak","admin1":"Kalimantan Barat","latitude":-0.0263,"longitude":109.3425,"elevation":3},
    {"name":"Banjarmasin","admin1":"Kalimantan Selatan","latitude":-3.3186,"longitude":114.5944,"elevation":1},
    {"name":"Palangka Raya","admin1":"Kalimantan Tengah","latitude":-2.2161,"longitude":113.9137,"elevation":25},
    {"name":"Samarinda","admin1":"Kalimantan Timur","latitude":-0.5022,"longitude":117.1536,"elevation":8},
    {"name":"Balikpapan","admin1":"Kalimantan Timur","latitude":-1.2379,"longitude":116.8529,"elevation":10},
    {"name":"Makassar","admin1":"Sulawesi Selatan","latitude":-5.1477,"longitude":119.4327,"elevation":8},
    {"name":"Manado","admin1":"Sulawesi Utara","latitude":1.4748,"longitude":124.8421,"elevation":5},
    {"name":"Palu","admin1":"Sulawesi Tengah","latitude":-0.9003,"longitude":119.8780,"elevation":14},
    {"name":"Kendari","admin1":"Sulawesi Tenggara","latitude":-3.9985,"longitude":122.5120,"elevation":5},
    {"name":"Gorontalo","admin1":"Gorontalo","latitude":0.5435,"longitude":123.0568,"elevation":9},
    {"name":"Ambon","admin1":"Maluku","latitude":-3.6954,"longitude":128.1814,"elevation":3},
    {"name":"Jayapura","admin1":"Papua","latitude":-2.5916,"longitude":140.6690,"elevation":9},
)


def _normalise(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return " ".join(value.lower().split())


def search_local_locations(query: str, limit: int = 10) -> list[dict[str, Any]]:
    needle = _normalise(query)
    if len(needle) < 2:
        return []
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for item in LOCATIONS:
        haystack = _normalise(f"{item['name']} {item['admin1']}")
        if needle not in haystack:
            continue
        score = 0 if _normalise(item["name"]).startswith(needle) else 1
        result = {
            "id": f"local-{_normalise(item['name']).replace(' ', '-')}",
            "name": item["name"],
            "admin1": item["admin1"],
            "admin2": None,
            "display_name": f"{item['name']}, {item['admin1']}",
            "latitude": item["latitude"],
            "longitude": item["longitude"],
            "elevation": item["elevation"],
            "country_code": "ID",
            "source": "curated_indonesia_fallback",
        }
        scored.append((score, item["name"], result))
    return [item for _, _, item in sorted(scored)[:limit]]
