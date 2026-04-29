from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from modules.data_collection import collect_city_data
from modules.realtime_traffic import get_city_traffic, get_worst_areas, get_best_areas, get_area_traffic
from modules.traffic_analysis import analyse_city_traffic
from modules.traffic_predictor import get_predictions, get_city_wide_prediction
from modules.llm_analysis import analyse_traffic_with_llm

app = FastAPI(title="Traffic Intelligence System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

city_cache: dict = {}


class CityRequest(BaseModel):
    city_name: str


# ── ENDPOINT 1 — POST /analyse-city ──────────────────────────────────────────
@app.post("/analyse-city")
def analyse_city(request: CityRequest):
    city_name = request.city_name.strip()
    print(f"\n{'='*50}\n[api] Starting analysis for: {city_name}\n{'='*50}")

    # Step 1 — collect coordinates and areas
    step = "data_collection"
    try:
        print(f"[api] Step 1: Collecting city data...")
        city_data = collect_city_data(city_name)
        if city_data.get("status") == "error":
            raise ValueError(city_data.get("error", "Unknown error"))
        areas = city_data["areas"]
    except Exception as e:
        raise HTTPException(status_code=500, detail={"step": step, "error": str(e)})

    # Step 2 — live traffic for all areas
    step = "realtime_traffic"
    try:
        print(f"[api] Step 2: Fetching live traffic for {len(areas)} areas...")
        city_traffic = get_city_traffic(areas)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"step": step, "error": str(e)})

    # Step 3 — score and rank
    step = "traffic_analysis"
    try:
        print(f"[api] Step 3: Analysing city traffic...")
        analysis = analyse_city_traffic(city_name, city_traffic)
        worst_areas = analysis["worst_areas"]
        overall_score = analysis["overall_score"]
    except Exception as e:
        raise HTTPException(status_code=500, detail={"step": step, "error": str(e)})

    # Step 4 — city-wide predictions
    step = "predictions"
    try:
        print(f"[api] Step 4: Generating predictions...")
        predictions = get_city_wide_prediction(areas)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"step": step, "error": str(e)})

    # Step 5 — LLM insights
    step = "llm_analysis"
    try:
        print(f"[api] Step 5: Running AI analysis...")
        worst_summary = [
            f"{a['area_name']} {a['congestion_level']} score {a['congestion_score']}"
            for a in worst_areas
        ]
        llm_insights = analyse_traffic_with_llm(city_name, worst_summary, overall_score, predictions)
    except Exception as e:
        print(f"[api] LLM step failed ({e}), continuing without insights.")
        llm_insights = {}

    # Step 6 — cache and return
    result = {
        "city_name":    city_name,
        "coordinates":  city_data["coordinates"],
        "total_areas":  city_data["total_areas"],
        "overall_score": overall_score,
        "overall_level": analysis["overall_level"],
        "areas":         city_traffic,
        "worst_areas":   worst_areas,
        "best_areas":    analysis["best_areas"],
        "predictions":   predictions,
        "llm_insights":  llm_insights,
        "timestamp":     str(datetime.now()),
    }
    city_cache[city_name.lower()] = result
    print(f"[api] Analysis complete for {city_name}. Cached.")
    return result


# ── ENDPOINT 2 — GET /area-traffic/{city_name}/{area_name} ───────────────────
@app.get("/area-traffic/{city_name}/{area_name}")
def area_traffic(city_name: str, area_name: str):
    cached = city_cache.get(city_name.lower(), {})
    lat, lon = None, None

    # Try to find area coords from cache
    for area in cached.get("areas", []):
        if area.get("area_name", "").lower() == area_name.lower():
            lat = area.get("lat")
            lon = area.get("lon")
            break

    if lat is None:
        # Fallback coords from city coordinates
        coords = cached.get("coordinates", {})
        lat = coords.get("lat", 18.52)
        lon = coords.get("lon", 73.85)

    try:
        live    = get_area_traffic(area_name, lat, lon)
        predict = get_predictions(area_name, live.get("congestion_score", 5))
        return {
            "city_name":   city_name,
            "area_name":   area_name,
            "live_traffic": live,
            "predictions":  predict,
            "timestamp":    str(datetime.now()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ── ENDPOINT 3 — GET /city-areas/{city_name} ─────────────────────────────────
@app.get("/city-areas/{city_name}")
def city_areas(city_name: str):
    cached = city_cache.get(city_name.lower())
    if cached:
        return {
            "city_name":   city_name,
            "total_areas": cached["total_areas"],
            "areas":       cached["areas"],
            "source":      "cache",
        }
    try:
        print(f"[api] Fetching areas for {city_name} (not cached)...")
        city_data = collect_city_data(city_name)
        return {
            "city_name":   city_name,
            "total_areas": city_data["total_areas"],
            "areas":       city_data["areas"],
            "source":      "live",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ── ENDPOINT 4 — GET /health ──────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status":        "Traffic Intelligence System is running",
        "timestamp":     str(datetime.now()),
        "cached_cities": list(city_cache.keys()),
    }
