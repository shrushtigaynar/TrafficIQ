# 🚦 TrafficIQ — Real-Time Traffic Intelligence System

## Overview

Type a city. Get live traffic intelligence.

AI-powered congestion analysis, real-time map, area-wise predictions and smart recommendations for Pune, Mumbai, Delhi and Bangalore.

---

## Features

- 🔴 Live traffic congestion data for 20+ city areas
- 🗺️ Color-coded interactive map (Green=Free, Orange=Heavy, Red=Critical)
- 🕐 AI-powered predictions for next 1hr, 3hr and tomorrow
- 📊 Area-wise deep analysis with congestion score (0–10)
- 🤖 Smart route recommendations powered by Groq LLaMA AI
- 🌙 Dark and light mode support
- 🔄 Auto-refresh every 60 seconds

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13 + FastAPI + Uvicorn |
| AI Analysis | Groq API (LLaMA 3.1 8B Instant) |
| Traffic Data | TomTom Traffic Flow API |
| Map | Leaflet.js + CARTO dark/light tiles |
| City Data | OpenStreetMap + Nominatim + Overpass API |
| Frontend | Pure HTML + CSS + JavaScript (no frameworks) |

---

## Supported Cities

| City | Areas |
|---|---|
| Pune | Hinjewadi, Kothrud, Hadapsar, Baner, Wakad + 15 more |
| Mumbai | Andheri, Bandra, Dadar, Powai, BKC + 15 more |
| Delhi | Connaught Place, Dwarka, Rohini, Saket + 16 more |
| Bangalore | Koramangala, Whitefield, Electronic City + 17 more |

---

## Project Structure

```
smart-city/
├── main.py                    # FastAPI app + all endpoints
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not committed)
├── README.md
├── modules/
│   ├── data_collection.py     # Nominatim + Overpass city/area data
│   ├── realtime_traffic.py    # TomTom API + time-based fallback
│   ├── traffic_analysis.py    # Score aggregation + ranking
│   ├── traffic_predictor.py   # Rule-based hourly predictions
│   ├── llm_analysis.py        # Groq LLaMA AI insights
│   └── traffic_analysis.py    # City-wide analysis
├── frontend/
│   └── index.html             # Single-file dashboard (HTML+CSS+JS)
└── data/
    └── cost_database.csv
```

---

## How to Run

**1. Add API keys to `.env` file**
```
TOMTOM_API_KEY=your_tomtom_key
GROQ_API_KEY=your_groq_key
```

Get free keys:
- TomTom: https://developer.tomtom.com (free tier — 2,500 requests/day)
- Groq: https://console.groq.com (free tier)

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Start backend server**
```bash
uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000`

**4. Open frontend**

Open `frontend/index.html` directly in any browser. No build step needed.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyse-city` | Full city traffic analysis pipeline |
| GET | `/area-traffic/{city}/{area}` | Live traffic + predictions for one area |
| GET | `/city-areas/{city}` | All areas list for a city |
| GET | `/health` | System status + cached cities |

**Example request:**
```bash
curl -X POST http://localhost:8000/analyse-city \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Pune"}'
```

Interactive API docs available at `http://127.0.0.1:8000/docs`

---

## Congestion Score Reference

| Score | Level | Color | Meaning |
|---|---|---|---|
| 0–2 | FREE | 🟢 Green | Roads flowing freely |
| 3–5 | MODERATE | 🟡 Yellow | Light congestion |
| 6–7 | HEAVY | 🟠 Orange | Significant delays |
| 8–10 | CRITICAL | 🔴 Red | Severe congestion |

---

## Screenshots

*(Add screenshots here)*

---

## License

MIT License
