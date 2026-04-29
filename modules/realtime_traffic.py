# Realtime traffic module - TomTom API + time-based fallback

import os
import time
import random
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "")
TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

COLOR_MAP = {"CRITICAL": "red", "HIGH": "orange", "MODERATE": "yellow", "LOW": "green"}


# ── 1. GET CONGESTION LEVEL ───────────────────────────────────────────────────
def get_congestion_level(score: float) -> str:
    if score > 7:   return "CRITICAL"
    if score >= 4:  return "HIGH"
    if score >= 2:  return "MODERATE"
    return "LOW"


# ── 2. GET AREA TRAFFIC ───────────────────────────────────────────────────────
def get_area_traffic(area_name: str, lat: float, lon: float) -> dict:
    if TOMTOM_API_KEY and TOMTOM_API_KEY != "your_key_here":
        try:
            import requests
            params = {"point": f"{lat},{lon}", "key": TOMTOM_API_KEY, "unit": "KMPH"}
            r = requests.get(TOMTOM_URL, params=params, timeout=10)
            if r.status_code == 200:
                fd        = r.json().get("flowSegmentData", {})
                current   = fd.get("currentSpeed", 0)
                free_flow = fd.get("freeFlowSpeed", 1)
                ratio     = current / max(free_flow, 1)
                score     = round((1 - ratio) * 10)
                score     = max(0, min(10, score))
                level     = get_congestion_level(score)

                print(f"[tomtom] {area_name}: current={current}, free={free_flow}, ratio={ratio:.2f}, score={score}")

                # If TomTom says score=0 but it's peak hours, the road data may be
                # from a low-traffic segment — override with time-based estimate
                hour = datetime.now().hour
                is_peak = (7 <= hour < 10) or (17 <= hour < 21)
                if score == 0 and is_peak:
                    fallback = time_based_fallback(area_name, lat, lon)
                    print(f"[tomtom] {area_name}: peak hour override → score={fallback['congestion_score']}")
                    fallback["source"]         = "tomtom_peak_override"
                    fallback["current_speed"]  = current
                    fallback["free_flow_speed"] = free_flow
                    return fallback

                return {
                    "area_name":        area_name,
                    "lat":              lat,
                    "lon":              lon,
                    "current_speed":    current,
                    "free_flow_speed":  free_flow,
                    "congestion_score": score,
                    "congestion_level": level,
                    "confidence":       fd.get("confidence", 1.0),
                    "color":            COLOR_MAP[level],
                    "source":           "tomtom",
                }
        except Exception as e:
            print(f"[traffic] TomTom failed for {area_name}: {e}")

    return time_based_fallback(area_name, lat, lon)


# ── 3. TIME-BASED FALLBACK ────────────────────────────────────────────────────
def time_based_fallback(area_name: str, lat: float = 0.0, lon: float = 0.0) -> dict:
    hour = datetime.now().hour
    if 0 <= hour < 7:
        base = random.randint(1, 2)
    elif 7 <= hour < 10:
        base = random.randint(7, 9)
    elif 10 <= hour < 17:
        base = random.randint(4, 6)
    elif 17 <= hour < 21:
        base = random.randint(7, 9)
    else:  # 21-24
        base = random.randint(2, 3)

    score = max(0, min(10, base + random.choice([-1, 0, 1])))
    level = get_congestion_level(score)
    return {
        "area_name":        area_name,
        "lat":              lat,
        "lon":              lon,
        "current_speed":    max(5, round(60 * (1 - score / 10))),
        "free_flow_speed":  60,
        "congestion_score": score,
        "congestion_level": level,
        "confidence":       0.7,
        "color":            COLOR_MAP[level],
        "source":           "fallback",
    }


# ── 4. GET CITY TRAFFIC ───────────────────────────────────────────────────────
def get_city_traffic(areas_list: list) -> list:
    results = []
    for area in areas_list:
        name = area.get("name", "Unknown")
        lat  = area.get("lat", 0.0)
        lon  = area.get("lon", 0.0)
        print(f"[traffic] Fetching {name}...")
        try:
            result = get_area_traffic(name, lat, lon)
            results.append(result)
        except Exception as e:
            print(f"[traffic] Error for {name}: {e}")
        time.sleep(0.3)
    return results


# ── 5. GET WORST AREAS ────────────────────────────────────────────────────────
def get_worst_areas(city_traffic_data: list, top_n: int = 5) -> list:
    return sorted(city_traffic_data, key=lambda x: x.get("congestion_score", 0), reverse=True)[:top_n]


# ── 6. GET BEST AREAS ─────────────────────────────────────────────────────────
def get_best_areas(city_traffic_data: list, top_n: int = 5) -> list:
    return sorted(city_traffic_data, key=lambda x: x.get("congestion_score", 0))[:top_n]


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_areas = [
        {"name": "Hinjewadi",    "lat": 18.591, "lon": 73.738},
        {"name": "Shivajinagar", "lat": 18.530, "lon": 73.847},
        {"name": "Hadapsar",     "lat": 18.506, "lon": 73.928},
        {"name": "Baner",        "lat": 18.559, "lon": 73.787},
        {"name": "Kothrud",      "lat": 18.508, "lon": 73.806},
    ]

    print("Testing realtime_traffic.py with 5 Pune areas...\n")
    results = get_city_traffic(test_areas)

    print("\n--- Results ---")
    for r in results:
        print(f"  {r['area_name']:20s}  score={r['congestion_score']}  level={r['congestion_level']:10s}  source={r['source']}")

    print("\n--- Worst 3 ---")
    for r in get_worst_areas(results, 3):
        print(f"  {r['area_name']:20s}  score={r['congestion_score']}  {r['congestion_level']}")

    print("\n--- Best 3 ---")
    for r in get_best_areas(results, 3):
        print(f"  {r['area_name']:20s}  score={r['congestion_score']}  {r['congestion_level']}")
