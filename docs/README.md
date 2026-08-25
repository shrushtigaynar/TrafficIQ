# 🚦 TrafficIQ — Real-Time Traffic Intelligence System

> Type a city. Get live traffic intelligence.

AI-powered congestion analysis, real-time interactive map, area-wise predictions, and smart routing recommendations for major Indian cities — powered by TomTom, Groq LLaMA, and OpenStreetMap.

---

## ✨ Features

- 🔴 **Live congestion data** for 20+ areas per city via TomTom Traffic Flow API
- 🗺️ **Color-coded interactive map** — Green (Free) → Yellow (Moderate) → Orange (Heavy) → Red (Critical)
- 🕐 **AI-powered time predictions** — next 1hr traffic prediction
- 📊 **Area-wise deep analysis** with congestion scores (0–10) and area-type classification (IT Hub / Market / Residential / Mixed)
- 🤖 **LLM insights via Groq LLaMA 3.1** — root causes, immediate fixes, long-term solutions, and alternate routes
- 🌙 **Dark & light mode** with CARTO tile switching
- 🔄 **Auto-refresh** every 60 seconds
- 🛡️ **Graceful fallbacks** — time-based congestion estimates when TomTom data is unavailable or unreliable during peak hours

---

## 🏙️ Supported Cities

| City | Areas Covered |
|---|---|
| **Pune** | Hinjewadi, Kothrud, Hadapsar, Baner, Wakad, Aundh, Kharadi, Viman Nagar + 12 more |
| **Mumbai** | Andheri, Bandra, Dadar, Powai, BKC, Lower Parel, Dharavi, Navi Mumbai + 12 more |
| **Delhi** | Connaught Place, Dwarka, Rohini, Saket, Gurugram, Noida Sec 18 + 14 more |
| **Bangalore** | Koramangala, Whitefield, Electronic City, Indiranagar, HSR Layout + 15 more |

> Any city can be typed — Nominatim + Overpass API will attempt to dynamically discover areas. The four cities above have hardcoded fallback area lists for reliability.

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13 · FastAPI · Uvicorn |
| **AI Analysis** | Groq API — LLaMA 3.1 8B Instant |
| **Traffic Data** | TomTom Traffic Flow API (v4) |
| **City / Area Discovery** | OpenStreetMap · Nominatim · Overpass API |
| **Map Rendering** | Leaflet.js · CARTO dark/light tiles · Stadia Maps |
| **Frontend** | HTML · CSS · Vanilla JavaScript (`app.js`) — zero build step |

---

## 📁 Project Structure

```
smart-city/
├── main.py                    # FastAPI app — all 4 endpoints
├── requirements.txt           # Python dependencies
├── .env                       # API keys (do NOT commit — add to .gitignore)
├── README.md
│
├── modules/
│   ├── data_collection.py     # Nominatim + Overpass area discovery + hardcoded fallbacks
│   ├── realtime_traffic.py    # TomTom API integration + time-based fallback scoring
│   ├── traffic_analysis.py    # Score aggregation, city-wide ranking, best/worst areas
│   ├── traffic_predictor.py   # Rule-based hourly & daily predictions by area type
│   └── llm_analysis.py        # Groq LLaMA prompt + JSON parsing + offline fallback
│
├── frontend/
│   ├── index.html             # Dashboard UI shell
│   └── app.js                 # All frontend logic — map, API calls, UI updates
│
└── data/
    └── cost_database.csv      # (Reserved for future cost estimation features)
```

---

## ⚙️ How to Run

### 1. Set up API keys

Create a `.env` file in the `smart-city/` directory:

```env
TOMTOM_API_KEY=your_tomtom_key
GROQ_API_KEY=your_groq_key
STADIA_MAPS_API_KEY=your_stadia_key
```

Get free keys from:
- **TomTom:** https://developer.tomtom.com — free tier, 2,500 requests/day
- **Groq:** https://console.groq.com — free tier, generous rate limits
- **Stadia Maps:** https://stadiamaps.com — free tier for development

> ⚠️ **Never commit your `.env` file.** Add it to `.gitignore` immediately.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the backend

```bash
uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`

### 4. Open the frontend

Open `frontend/index.html` directly in any browser. No build step, no bundler needed.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyse-city` | Full 5-step pipeline: collect → traffic → score → predict → AI insights |
| `GET` | `/area-traffic/{city}/{area}` | Live traffic + predictions for a single area |
| `GET` | `/city-areas/{city}` | List all tracked areas for a city (uses cache if available) |
| `GET` | `/health` | System status + list of currently cached cities |

**Example — analyse a city:**
```bash
curl -X POST http://localhost:8000/analyse-city \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Pune"}'
```

**Example — check one area:**
```bash
curl http://localhost:8000/area-traffic/Mumbai/Bandra
```

Interactive Swagger docs: `http://127.0.0.1:8000/docs`

---

## 🔁 Analysis Pipeline (POST /analyse-city)

```
Step 1 → Collect city coordinates + area list   (Nominatim + Overpass)
Step 2 → Fetch live traffic for all areas        (TomTom Flow API)
Step 3 → Score + rank areas                      (traffic_analysis.py)
Step 4 → Generate time-based predictions         (traffic_predictor.py)
Step 5 → Run LLM for insights                    (Groq LLaMA 3.1)
Step 6 → Cache + return full result
```

LLM failures are non-fatal — the system returns a sensible offline fallback with pre-written root causes and solutions so the dashboard always has something to display.

---

## 🧠 Prediction Engine

The predictor classifies each area into one of four types and applies time/day rules:

| Area Type | Peak Pattern |
|---|---|
| **IT Hub** | Heavy Mon–Fri 7–10 AM & 5–9 PM; quiet weekends |
| **Market** | Heavy evenings + all-day weekends |
| **Residential** | Moderate peaks morning & evening |
| **Mixed** | Blended average of Market + Residential |

Classified areas include: Hinjewadi, Whitefield, Electronic City (IT Hubs); Deccan, MG Road, Connaught Place (Markets); and several mixed zones.

---

## 🎨 Congestion Score Reference

| Score | Level | Color | Meaning |
|---|---|---|---|
| 0–2 | **FREE** | 🟢 Green | Roads flowing freely |
| 3–5 | **MODERATE** | 🟡 Yellow | Light congestion |
| 6–7 | **HIGH** | 🟠 Orange | Significant delays expected |
| 8–10 | **CRITICAL** | 🔴 Red | Severe congestion — avoid if possible |

Scores are derived from TomTom's `currentSpeed / freeFlowSpeed` ratio. During peak hours, if TomTom returns a suspiciously low score (0 on a known-busy road), the system overrides with a time-based estimate.

---

## 🔒 Security Notes

- Add `.env` to your `.gitignore` before your first commit — it contains live API keys.
- The backend uses `allow_origins=["*"]` (CORS open) which is fine for local dev but should be locked down for any deployment.
- In-memory `city_cache` resets on every server restart — no persistence layer yet.

---

## 🚧 Known Limitations

- Predictions are rule-based, not ML-trained — accuracy depends on how well an area fits its classification.
- TomTom free tier caps at 2,500 requests/day; with 20 areas per city, one full analysis costs ~20 requests.
- Area discovery via Overpass can be slow (5–15s) on first load; subsequent calls use the in-memory cache.
- The `cost_database.csv` is currently a placeholder for a planned cost estimation module.

---

## 📸 Screenshots

*(Add screenshots here)*

---

## 📄 License

MIT License — free to use, modify, and distribute.
