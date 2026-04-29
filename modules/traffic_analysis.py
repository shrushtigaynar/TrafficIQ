# Traffic analysis module

from modules.realtime_traffic import get_worst_areas, get_best_areas, get_congestion_level


def analyse_city_traffic(city_name: str, city_traffic: list) -> dict:
    """Score and rank city traffic data."""
    if not city_traffic:
        return {"city_name": city_name, "overall_score": 0, "worst_areas": [], "best_areas": []}

    scores = [a.get("congestion_score", 0) for a in city_traffic]
    overall = round(sum(scores) / len(scores), 1)

    worst = get_worst_areas(city_traffic, 5)
    best  = get_best_areas(city_traffic, 5)

    return {
        "city_name":     city_name,
        "overall_score": overall,
        "overall_level": get_congestion_level(overall),
        "total_areas":   len(city_traffic),
        "worst_areas":   worst,
        "best_areas":    best,
    }
