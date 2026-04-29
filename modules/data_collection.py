# Traffic data collection module

import time
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
HEADERS_NOM = {"User-Agent": "TrafficIQ/1.0"}
HEADERS_OVP = {
    "User-Agent": "TrafficIQ/1.0",
    "Content-Type": "application/x-www-form-urlencoded",
}

# ── HARDCODED FALLBACK AREAS ──────────────────────────────────────────────────
FALLBACK = {
    "pune": [
        ("Hinjewadi",18.591,73.738),("Shivajinagar",18.530,73.847),
        ("Hadapsar",18.506,73.928),("Kothrud",18.508,73.806),
        ("Baner",18.559,73.787),("Wakad",18.598,73.762),
        ("Deccan",18.516,73.838),("Pimpri",18.627,73.801),
        ("Chinchwad",18.644,73.795),("Magarpatta",18.511,73.931),
        ("Viman Nagar",18.567,73.915),("Kalyani Nagar",18.548,73.901),
        ("Aundh",18.558,73.808),("Kharadi",18.551,73.943),
        ("Swargate",18.502,73.858),("Camp",18.519,73.877),
        ("Yerawada",18.545,73.886),("Katraj",18.460,73.862),
        ("Kondhwa",18.470,73.888),("Bavdhan",18.526,73.772),
    ],
    "mumbai": [
        ("Andheri",19.119,72.847),("Bandra",19.054,72.840),
        ("Dadar",19.018,72.843),("Borivali",19.228,72.857),
        ("Kurla",19.072,72.879),("Powai",19.117,72.906),
        ("Thane",19.197,72.961),("Malad",19.187,72.849),
        ("Goregaon",19.162,72.849),("Juhu",19.098,72.827),
        ("Worli",19.013,72.818),("Colaba",18.906,72.814),
        ("Mulund",19.176,72.956),("Vikhroli",19.104,72.924),
        ("BKC",19.051,72.865),("Chembur",19.052,72.900),
        ("Navi Mumbai",19.033,73.029),("Dharavi",19.038,72.855),
        ("Lower Parel",18.994,72.830),("Versova",19.131,72.812),
    ],
    "delhi": [
        ("Connaught Place",28.634,77.220),("Karol Bagh",28.651,77.190),
        ("Lajpat Nagar",28.565,77.243),("Rohini",28.738,77.068),
        ("Dwarka",28.593,77.046),("Saket",28.524,77.214),
        ("Noida Sec 18",28.570,77.322),("Gurugram",28.459,77.026),
        ("Janakpuri",28.621,77.084),("Pitampura",28.701,77.131),
        ("Greater Kailash",28.539,77.237),("Vasant Kunj",28.520,77.157),
        ("Nehru Place",28.550,77.251),("Mayur Vihar",28.607,77.295),
        ("Laxmi Nagar",28.632,77.276),("Preet Vihar",28.643,77.292),
        ("Sarita Vihar",28.541,77.283),("Shahdara",28.672,77.289),
        ("Rajouri Garden",28.645,77.120),("CP Extension",28.638,77.228),
    ],
    "bangalore": [
        ("Koramangala",12.934,77.627),("Whitefield",12.969,77.750),
        ("Electronic City",12.839,77.677),("Indiranagar",12.978,77.641),
        ("Jayanagar",12.925,77.583),("HSR Layout",12.911,77.636),
        ("Marathahalli",12.956,77.701),("BTM Layout",12.916,77.620),
        ("Malleshwaram",13.003,77.565),("Bannerghatta",12.863,77.597),
        ("JP Nagar",12.900,77.583),("Hebbal",13.036,77.597),
        ("Yeshwanthpur",13.021,77.539),("Rajajinagar",12.991,77.553),
        ("Bellandur",12.926,77.677),("Sarjapur",12.869,77.697),
        ("Banashankari",12.925,77.547),("Cunningham Road",12.991,77.594),
        ("Ulsoor",12.977,77.622),("Nagarbhavi",12.952,77.508),
    ],
}


# ── 1. GET CITY COORDINATES ───────────────────────────────────────────────────
def get_city_coordinates(city_name: str) -> dict | None:
    print(f"[coords] Fetching coordinates for {city_name}...")
    try:
        params = {"q": f"{city_name}, India", "format": "json", "limit": 1}
        r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS_NOM, timeout=15)
        r.raise_for_status()
        results = r.json()
        if results:
            result = {
                "city_name":    city_name,
                "lat":          float(results[0]["lat"]),
                "lon":          float(results[0]["lon"]),
                "display_name": results[0].get("display_name", city_name),
            }
            print(f"[coords] Found: {result['lat']}, {result['lon']}")
            return result
        print(f"[coords] No results found for {city_name}.")
    except Exception as e:
        print(f"[coords] Failed: {e}")
    return None


# ── 2. GET CITY AREAS ─────────────────────────────────────────────────────────
def get_city_areas(city_name: str, lat: float, lon: float) -> list:
    print(f"[areas] Fetching areas for {city_name}...")
    query = (
        f'[out:json][timeout:30];'
        f'area["name"="{city_name}"]["place"~"city|town"]->.searchArea;'
        f'(node["place"~"suburb|neighbourhood|quarter|village"](area.searchArea););'
        f'out center 40;'
    )

    for url in OVERPASS_URLS:
        try:
            print(f"[areas] Trying {url}...")
            r = requests.post(url, data=query, headers=HEADERS_OVP, timeout=35)
            r.raise_for_status()
            elements = r.json().get("elements", [])
            areas = []
            for el in elements:
                name = el.get("tags", {}).get("name", "").strip()
                if not name:
                    continue
                areas.append({
                    "name":    name,
                    "lat":     el.get("lat", lat),
                    "lon":     el.get("lon", lon),
                    "area_id": name.lower().replace(" ", "_"),
                })
            if areas:
                areas.sort(key=lambda x: x["name"])
                print(f"[areas] Found {len(areas)} areas via Overpass.")
                return areas[:40]
            print(f"[areas] Overpass returned empty from {url}.")
        except Exception as e:
            print(f"[areas] {url} failed: {e}")

    print(f"[areas] All Overpass endpoints failed. Using hardcoded fallback.")
    return _fallback_areas(city_name)


def _fallback_areas(city_name: str) -> list:
    key = city_name.lower()
    entries = FALLBACK.get(key, [])
    if not entries:
        print(f"[areas] No fallback for {city_name}. Returning empty list.")
        return []
    areas = [
        {"name": name, "lat": lat, "lon": lon,
         "area_id": name.lower().replace(" ", "_")}
        for name, lat, lon in entries
    ]
    print(f"[areas] Using {len(areas)} hardcoded fallback areas for {city_name}.")
    return areas


# ── 3. COLLECT CITY DATA ──────────────────────────────────────────────────────
def collect_city_data(city_name: str) -> dict:
    print(f"\n{'='*50}")
    print(f"Collecting data for: {city_name}")
    print(f"{'='*50}")

    # Step 1 — coordinates
    coords = get_city_coordinates(city_name)
    if not coords:
        return {"city_name": city_name, "status": "error", "error": "Could not fetch coordinates"}

    time.sleep(1)

    # Step 2 — areas
    areas = get_city_areas(city_name, coords["lat"], coords["lon"])

    # Step 3 — return combined result
    result = {
        "city_name":   city_name,
        "coordinates": {"lat": coords["lat"], "lon": coords["lon"]},
        "areas":       areas,
        "total_areas": len(areas),
        "status":      "success",
    }
    print(f"\n[done] {len(areas)} areas collected for {city_name}.")
    return result


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = collect_city_data("Pune")
    print(f"\nTotal areas found: {data['total_areas']}")
    print("\nAll areas:")
    for a in data.get("areas", []):
        print(f"  {a['name']:25s}  lat={a['lat']}  lon={a['lon']}")
