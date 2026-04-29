# Traffic LLM analysis module

import os
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

MODEL = "llama-3.1-8b-instant"

FALLBACK = {
    "root_causes": [
        "High vehicle density during peak hours",
        "Inadequate public transport coverage",
        "Poor signal timing optimization",
    ],
    "immediate_solutions": [
        {"solution": "Adaptive traffic signal timing",              "impact": "HIGH",   "cost": "LOW"},
        {"solution": "Dedicated bus lanes on arterial roads",       "impact": "HIGH",   "cost": "MEDIUM"},
        {"solution": "Odd-even vehicle scheme during peak hours",   "impact": "MEDIUM", "cost": "LOW"},
    ],
    "long_term_solutions": [
        {"solution": "Metro rail network expansion",                "impact": "VERY HIGH", "cost": "HIGH"},
        {"solution": "Ring road development to bypass city center", "impact": "HIGH",      "cost": "HIGH"},
        {"solution": "Smart parking management system",             "impact": "MEDIUM",    "cost": "MEDIUM"},
    ],
    "travel_advice": "Avoid peak hours 8am-10am and 5pm-8pm. Use public transport where possible.",
    "best_alternate_routes": [
        "Use ring road to bypass congested city center",
        "Metro and bus combo for IT hub commuters",
    ],
    "improvement_potential": "30 percent reduction possible with signal optimization",
}


def analyse_traffic_with_llm(city_name: str, worst_areas: list,
                              city_score: float, predictions: dict) -> dict:
    print(f"[llm] Analysing traffic for {city_name}...")

    if not GROQ_AVAILABLE:
        print("[llm] groq library not installed. Using fallback.")
        return FALLBACK.copy()

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        print("[llm] GROQ_API_KEY not set. Using fallback.")
        return FALLBACK.copy()

    prompt = f"""You are an expert urban traffic analyst for Indian cities.
Analyse the following traffic data for {city_name}.

City overall congestion score: {city_score}/10
Top 5 most congested areas: {worst_areas}
City wide predictions: {predictions}

Respond ONLY in valid JSON with no extra text, no markdown, no backticks — just pure JSON like this:
{{
  "root_causes": ["cause1", "cause2", "cause3"],
  "immediate_solutions": [
    {{"solution": "string", "impact": "HIGH/MEDIUM/LOW", "cost": "HIGH/MEDIUM/LOW"}},
    {{"solution": "string", "impact": "string", "cost": "string"}},
    {{"solution": "string", "impact": "string", "cost": "string"}}
  ],
  "long_term_solutions": [
    {{"solution": "string", "impact": "string", "cost": "string"}},
    {{"solution": "string", "impact": "string", "cost": "string"}},
    {{"solution": "string", "impact": "string", "cost": "string"}}
  ],
  "travel_advice": "single practical string for commuters",
  "best_alternate_routes": ["route suggestion 1", "route suggestion 2"],
  "improvement_potential": "string like 35 percent reduction possible"
}}"""

    try:
        client   = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()

        # Strip accidental markdown fences
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        result = json.loads(raw)
        print("[llm] Analysis complete.")
        return result

    except json.JSONDecodeError as e:
        print(f"[llm] JSON parse error: {e}. Using fallback.")
    except Exception as e:
        print(f"[llm] API error: {e}. Using fallback.")

    return FALLBACK.copy()


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = analyse_traffic_with_llm(
        city_name   = "Pune",
        worst_areas = ["Hinjewadi HIGH score 8", "Hadapsar HIGH score 7"],
        city_score  = 6.5,
        predictions = {"most_congested_tomorrow": ["Hinjewadi", "Hadapsar"]},
    )
    print(json.dumps(result, indent=2))
