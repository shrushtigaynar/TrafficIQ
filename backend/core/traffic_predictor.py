# Traffic prediction module - rule-based

from datetime import datetime, timedelta

IT_HUBS  = {"hinjewadi","whitefield","electronic city","magarpatta","kharadi",
            "viman nagar","cybercity","cyber city"}
MARKETS  = {"deccan","camp","swargate","laxmi road","mg road","lajpat nagar",
            "karol bagh","connaught place","dadar","bandra"}
MIXED    = {"yerawada","katraj","hadapsar"}

REASONS = {
    "IT_HUB":      "IT hub area — heavy weekday morning and evening traffic",
    "MARKET":      "Market area — heavy evening and weekend traffic",
    "RESIDENTIAL": "Residential area — peak during morning and evening commute",
    "MIXED":       "Mixed zone — moderate traffic throughout the day",
}


# ── 1. CLASSIFY AREA TYPE ─────────────────────────────────────────────────────
def classify_area_type(area_name: str) -> str:
    key = area_name.lower().strip()
    if key in IT_HUBS:  return "IT_HUB"
    if key in MARKETS:  return "MARKET"
    if key in MIXED:    return "MIXED"
    return "RESIDENTIAL"


# ── 2. PREDICT SCORE AT HOUR ──────────────────────────────────────────────────
def predict_score_at_hour(area_type: str, target_hour: int, is_weekend: bool) -> int:
    h = target_hour % 24

    if area_type == "IT_HUB":
        if is_weekend:
            return 3
        if 7 <= h < 10:  return 9
        if 10 <= h < 17: return 5
        if 17 <= h < 21: return 8
        return 2

    if area_type == "MARKET":
        if is_weekend:
            return 9 if 10 <= h < 21 else 3
        if 7 <= h < 10:  return 6
        if 10 <= h < 20: return 7
        if 20 <= h < 22: return 8
        return 2

    if area_type == "RESIDENTIAL":
        if is_weekend:
            return 5 if 10 <= h < 20 else 2
        if 7 <= h < 10:  return 7
        if 10 <= h < 17: return 4
        if 17 <= h < 21: return 7
        return 2

    if area_type == "MIXED":
        r = predict_score_at_hour("RESIDENTIAL", h, is_weekend)
        m = predict_score_at_hour("MARKET",      h, is_weekend)
        return round((r + m) / 2)

    return 5


# ── HELPERS ───────────────────────────────────────────────────────────────────
def _level(score: int) -> str:
    if score > 7:  return "CRITICAL"
    if score >= 4: return "HIGH"
    if score >= 2: return "MODERATE"
    return "LOW"

def _slot(score: int) -> dict:
    return {"score": score, "level": _level(score)}

def _fmt_hour(h: int) -> str:
    h = h % 24
    suffix = "AM" if h < 12 else "PM"
    display = h if h <= 12 else h - 12
    display = 12 if display == 0 else display
    return f"{display}:00 {suffix}"


# ── 3. GET PREDICTIONS ────────────────────────────────────────────────────────
def get_predictions(area_name: str, current_score: int = 5) -> dict:
    now         = datetime.now()
    cur_hour    = now.hour
    is_weekend  = now.weekday() >= 5
    tmr_weekend = (now + timedelta(days=1)).weekday() >= 5

    area_type = classify_area_type(area_name)

    # Predicted slots
    cur   = predict_score_at_hour(area_type, cur_hour,     is_weekend)
    n1    = predict_score_at_hour(area_type, cur_hour + 1, is_weekend)
    n3    = predict_score_at_hour(area_type, cur_hour + 3, is_weekend)
    tmr_m = predict_score_at_hour(area_type, 8,            tmr_weekend)
    tmr_e = predict_score_at_hour(area_type, 18,           tmr_weekend)

    # Best / worst hour today
    today_scores = [(h, predict_score_at_hour(area_type, h, is_weekend)) for h in range(24)]
    best_hour  = min(today_scores, key=lambda x: x[1])[0]
    worst_hour = max(today_scores, key=lambda x: x[1])[0]

    return {
        "area_name":            area_name,
        "area_type":            area_type,
        "current":              _slot(cur),
        "next_1hr":             _slot(n1),
        "next_3hr":             _slot(n3),
        "tomorrow_morning":     _slot(tmr_m),
        "tomorrow_evening":     _slot(tmr_e),
        "best_time_to_travel":  _fmt_hour(best_hour),
        "worst_time_to_travel": _fmt_hour(worst_hour),
        "prediction_reason":    REASONS[area_type],
    }


# ── 4. CITY-WIDE PREDICTION ───────────────────────────────────────────────────
def get_city_wide_prediction(areas_list: list) -> dict:
    predictions = []
    for area in areas_list:
        name = area.get("name", area) if isinstance(area, dict) else area
        try:
            predictions.append(get_predictions(name, current_score=5))
        except Exception as e:
            print(f"[predictor] Error for {name}: {e}")

    sorted_by_morning = sorted(predictions, key=lambda x: x["tomorrow_morning"]["score"], reverse=True)

    return {
        "most_congested_tomorrow":  sorted_by_morning[:5],
        "least_congested_tomorrow": sorted_by_morning[-5:],
    }


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for area in ["Hinjewadi", "Kothrud"]:
        p = get_predictions(area)
        print(f"\n{'='*45}")
        print(f"  {p['area_name']}  [{p['area_type']}]")
        print(f"{'='*45}")
        print(f"  Current          : {p['current']['score']}  {p['current']['level']}")
        print(f"  Next 1 hour      : {p['next_1hr']['score']}  {p['next_1hr']['level']}")
        print(f"  Next 3 hours     : {p['next_3hr']['score']}  {p['next_3hr']['level']}")
        print(f"  Tomorrow morning : {p['tomorrow_morning']['score']}  {p['tomorrow_morning']['level']}")
        print(f"  Tomorrow evening : {p['tomorrow_evening']['score']}  {p['tomorrow_evening']['level']}")
        print(f"  Best time        : {p['best_time_to_travel']}")
        print(f"  Worst time       : {p['worst_time_to_travel']}")
        print(f"  Reason           : {p['prediction_reason']}")
