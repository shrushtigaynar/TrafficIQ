# Setup & Installation Guide

## 📦 Installation Steps

### 1. Prerequisites
- Python 3.8+
- Node.js/npm (optional, for frontend tooling)
- Git
- pip (Python package manager)

### 2. Backend Setup

#### Step 1: Navigate to backend directory
```bash
cd backend
```

#### Step 2: Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure environment variables
```bash
# Copy example env file
cp config/.env.example config/.env

# Edit config/.env with your API keys
# TOMTOM_API_KEY=your_key
# GROQ_API_KEY=your_key
# STADIA_MAPS_API_KEY=your_key
```

#### Step 5: Run backend
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### 3. Frontend Setup

#### Step 1: Open in browser
```bash
# Direct file URL
file:///path/to/frontend/public/index.html
```

Or use a local HTTP server:
```bash
cd frontend/public
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

---

## 🔧 Configuration

### Backend Configuration (`backend/config/settings.py`)

**Environment Variables:**
```
ENVIRONMENT=development          # development/production/testing
TOMTOM_API_KEY=xxxxx             # TomTom traffic API key
GROQ_API_KEY=xxxxx               # Groq LLM API key
STADIA_MAPS_API_KEY=xxxxx        # Stadia Maps API key
AGENT_MAX_AREAS=20               # Max areas to analyze
AGENT_TIMEOUT=60                 # Agent timeout in seconds
```

### Frontend Configuration (`frontend/public/app.js`)

**API Base URL:**
```javascript
const API_BASE = 'http://localhost:8000'
```

---

## 🚀 Running the Application

### Full Stack Start

#### Terminal 1: Backend
```bash
cd backend
python main.py
# Backend running on http://localhost:8000
```

#### Terminal 2: Frontend
```bash
cd frontend/public
python -m http.server 8080
# Frontend running on http://localhost:8080
```

#### Access Dashboard
Open browser: `http://localhost:8080/index.html`

Or use file URL: `file:///path/to/frontend/public/index.html`

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Test Specific Endpoint
```bash
# Test agent status
curl http://localhost:8000/api/agent/status

# Test agent analysis
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Pune"}'
```

---

## 📋 API Documentation

### Access Swagger UI
```
http://localhost:8000/docs
```

### Access ReDoc
```
http://localhost:8000/redoc
```

---

## 📁 Project Structure

```
smart-city/
├── backend/              # FastAPI server
├── frontend/             # Web dashboard
├── docs/                 # Documentation
├── logs/                 # Application logs
└── README.md             # This file
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Backend (change port in main.py)
# Frontend (change port in http.server command)
```

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### API Keys Not Working
1. Check `.env` file exists in `backend/config/`
2. Verify API keys are correct
3. Ensure no spaces around `=` sign

### Frontend Not Loading
1. Check browser console for errors
2. Verify API_BASE URL is correct
3. Check backend is running on correct port

---

## 📚 Documentation

- **Project Structure:** See `docs/PROJECT_STRUCTURE.md`
- **Agent Architecture:** See `docs/AGENT_IMPLEMENTATION.md`
- **Quick Start:** See `docs/QUICK_START.md`
- **Main README:** See `docs/README.md`

---

## 🔄 Development Tips

### Auto-reload Backend
```bash
# FastAPI with uvicorn (in main.py)
# Uses --reload flag automatically
```

### Debug Mode
```python
# In backend/main.py
app = FastAPI(debug=True)
```

### View Logs
```bash
# Backend logs
tail -f logs/backend.log

# Agent logs
tail -f logs/agent.log
```

---

## 🚢 Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t trafficiq .

# Run Docker container
docker run -p 8000:8000 trafficiq
```

See `docker-compose.yml` for multi-container setup.

---

## 📞 Support

- Check browser console for JavaScript errors
- Check terminal for Python errors
- Review logs in `logs/` directory
- Check API responses in Swagger UI

---

**Last Updated:** 2026-08-25
**Version:** 2.0.0
