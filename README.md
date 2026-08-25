# TrafficIQ Agent

Autonomous AI operations agent for real-time urban traffic management.

TrafficIQ combines live TomTom traffic data, OpenStreetMap area discovery, rule-based predictions, and Groq LLaMA analysis to identify congestion, explain likely causes, forecast trends, and recommend interventions with human approval.

## Features

- Live congestion data for 20+ areas per city via TomTom Traffic Flow API
- Color-coded interactive Leaflet map
- Area-level congestion scores and traffic predictions
- Root-cause analysis and intervention recommendations
- Autonomous agent loop: OBSERVE, ANALYZE, REASON, PREDICT, PLAN, SIMULATE
- Human-in-the-loop approval before simulated actions
- JSON-based action memory and outcome tracking
- Dark and light themes with graceful API fallbacks

## Supported Cities

Pune, Mumbai, Delhi, and Bangalore have fallback area lists. Other cities can be entered and are discovered through Nominatim and Overpass when available.

## Project Structure

```text
smart-city/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── requirements.txt           # Python dependencies
│   ├── config/
│   │   ├── settings.py            # Application configuration
│   │   └── .env                   # Local secrets, never commit
│   ├── core/
│   │   ├── agent_orchestrator.py  # Agent decision loop
│   │   ├── agent_tools.py         # Agent analysis tools
│   │   ├── agent_memory.py        # Action memory and outcomes
│   │   ├── data_collection.py     # City and area discovery
│   │   ├── realtime_traffic.py    # TomTom integration
│   │   ├── traffic_analysis.py    # Traffic metrics
│   │   ├── traffic_predictor.py   # Time-based predictions
│   │   └── llm_analysis.py        # Groq integration
│   ├── utils/                     # Helpers and logging
│   └── tests/                     # Backend tests
├── frontend/
│   ├── public/
│   │   ├── index.html             # Dashboard page
│   │   └── app.js                 # Main dashboard logic
│   ├── src/
│   │   ├── agent-panel.js         # Agent panel behavior
│   │   └── agent-panel.css        # Agent panel styles
│   └── assets/data/
│       └── cost_database.csv
├── docs/                          # Architecture and usage guides
├── logs/                          # Runtime logs
├── SETUP.md
└── README.md
```

## Setup

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/config/.env`:

```env
TOMTOM_API_KEY=your_tomtom_key
GROQ_API_KEY=your_groq_key
STADIA_MAPS_API_KEY=your_stadia_key
```

Never commit `.env` or expose API keys publicly.

## Run the Backend

From the project root:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

If `backend/main.py` uses top-level imports such as `from modules...`, run from inside `backend` instead:

```powershell
cd backend
python main.py
```

API documentation is available at `http://localhost:8000/docs`.

## Run the Frontend

Open `frontend/public/index.html` directly, or serve it with a local HTTP server:

```powershell
cd frontend/public
python -m http.server 8080
```

Open `http://localhost:8080` in a browser while the backend is running.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyse-city` | Run the traffic analysis pipeline |
| `GET` | `/area-traffic/{city}/{area}` | Get traffic for one area |
| `GET` | `/city-areas/{city}` | List tracked city areas |
| `GET` | `/health` | Check backend health |
| `POST` | `/api/agent/run` | Run the autonomous agent |
| `POST` | `/api/actions/approve` | Approve or reject an action |
| `GET` | `/api/actions` | View action history |
| `GET` | `/api/actions/{action_id}` | View one action |
| `GET` | `/api/agent/memory` | View agent memory |
| `GET` | `/api/agent/status` | Check agent readiness |

Example:

```powershell
$body = @{ city_name = "Pune" } | ConvertTo-Json
Invoke-RestMethod http://localhost:8000/api/agent/run `
  -Method Post -ContentType "application/json" -Body $body
```

## Testing

From the project root:

```powershell
python -m pytest backend/tests
```

## Documentation

- [SETUP.md](SETUP.md) - Installation and configuration
- [docs/QUICK_START.md](docs/QUICK_START.md) - Demo walkthrough
- [docs/AGENT_IMPLEMENTATION.md](docs/AGENT_IMPLEMENTATION.md) - Agent architecture
- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - Folder details

## Security Notes

- Keep `backend/config/.env` private.
- Lock down CORS before production deployment.
- The current action system simulates interventions; it does not control physical traffic infrastructure.

## License

MIT License.
