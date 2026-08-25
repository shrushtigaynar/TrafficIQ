# TrafficIQ Agent - Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Prerequisites
- ✅ Backend running: `uvicorn main:app --reload`
- ✅ Frontend open: `frontend/index.html`
- ✅ API keys configured in `.env`

---

## Demo Scenario: Autonomous Traffic Management in Pune

### Step 1: Open Dashboard
```
Navigate to: c:\Users\HP\OneDrive\Desktop\SmartCity planner\smart-city\frontend\index.html
```

### Step 2: Analyze City Traffic
```
1. Type "Pune" in the city name field
2. Click "Analyse" button
3. Wait 5-10 seconds for analysis to complete
```

### Step 3: Activate Agent Panel
```
1. Look for 🤖 button in top navigation (next to theme button)
2. Click the 🤖 agent button
3. Agent panel slides open from right side
```

### Step 4: Run Agent Analysis
```
The agent will automatically perform:
- Observe: Fetch current traffic for all 20 Pune areas
- Analyze: Detect critical congestion areas
- Reason: Analyze root causes (peak hour, area type, patterns)
- Predict: Forecast trends for next 3 hours
- Plan: Select best intervention option
- Propose: Show human-approachable recommendation
```

### Step 5: Review Proposal
The panel will display:

```
🚨 PROBLEM DETECTED
Location: [Area Name]
Congestion: 8.7/10 (CRITICAL)
Speed: 18 km/h / 55 km/h

🔍 ROOT CAUSE
Probable: Peak-hour IT hub traffic
Confidence: 87%
Evidence:
  • Speed decreased 61%
  • Traffic volume increased 42%
  • Time: 14:00 (known peak)

📊 PREDICTIONS (Next 3 Hours)
15:00 → 8.9/10 (CRITICAL) 📈
16:00 → 7.5/10 (HIGH)
17:00 → 9.2/10 (CRITICAL) 📈

💡 RECOMMENDED ACTION
Signal Timing Adjustment
→ Increase green time on arterial roads
→ Expected improvement: 18%
→ Risk: LOW
→ Time: 1-2 minutes
```

### Step 6: Make Decision
```
Two options:
[ ✓ APPROVE ]  - Execute simulation + measure results
[ ✕ REJECT ]   - Agent re-plans alternative approaches
```

### Step 7: See Results
If approved, agent shows:
```
Before: 8.7/10
After: 6.2/10
Improvement: 28.7% ✓ SUCCESSFUL
```

---

## 📡 Endpoint Quick Reference

### Run Agent Analysis
```bash
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{"city_name":"Pune"}'
```

### Approve Action
```bash
curl -X POST http://localhost:8000/api/actions/approve \
  -H "Content-Type: application/json" \
  -d '{"action_id":"action_1","approved":true}'
```

### Get Agent Status
```bash
curl http://localhost:8000/api/agent/status
```

### View All Actions
```bash
curl http://localhost:8000/api/actions
```

### View Agent Memory
```bash
curl http://localhost:8000/api/agent/memory | python -m json.tool
```

---

## 🎯 What Makes This "Agentic"

✅ **Autonomous Observation**
   - Continuously monitors traffic
   - Triggers analysis without user prompt
   - Detects anomalies automatically

✅ **Structured Reasoning**
   - Follows formal decision loop
   - Each step has observable output
   - Confidence scoring at each phase

✅ **Planning & Action**
   - Evaluates multiple options
   - Selects best intervention
   - Proposes with evidence

✅ **Human-in-Loop Safety**
   - All high-impact decisions require approval
   - Transparent reasoning shown
   - Never acts without permission

✅ **Feedback & Learning**
   - Measures actual outcomes
   - Compares to predictions
   - Stores in memory for future

---

## 🔍 Understanding the UI

### Agent Panel Components

**1. Status Indicator (Top)**
- 🟢 Green pulse = Agent ready
- 🔴 Red = Monitoring
- 🟡 Yellow = Processing

**2. Problem Card** (Red/Orange)
- Shows critical area detected
- Congestion score
- Speed comparison

**3. Root Cause Card** (Orange/Yellow)
- Most likely cause
- Confidence percentage
- Supporting evidence

**4. Prediction Section**
- 📈 Trend direction
- Next 3 hours forecast
- Severity levels

**5. Action Card** (Blue)
- Recommended intervention
- Impact percentage
- Risk assessment

**6. Approval Buttons**
- Approve (Green)
- Reject (Red)

**7. Results Section** (Green)
- Before/after comparison
- Improvement percentage
- Success/Failure status

**8. Activity Log** (Bottom)
- Timestamped events
- Phase indicators
- Real-time updates

---

## 💡 Pro Tips

### Tip 1: Peak Hours
Run agent during 7-10am or 5-9pm for dramatic congestion scenarios.

### Tip 2: Multiple Scenarios
- **Pune**: IT hub patterns (Hinjewadi shows critical congestion)
- **Mumbai**: Mixed traffic (Andheri, Bandra congestion)
- **Delhi**: Commute traffic (Connaught Place, Gurugram)
- **Bangalore**: IT hub (Whitefield, Electronic City)

### Tip 3: Watch the Activity Log
The timestamped log shows each decision step:
```
14:15:22 OBSERVE: Monitoring traffic
14:15:25 ANALYZE: Anomaly detected  
14:15:30 REASON: Root cause analysis
14:15:33 PREDICT: Trend forecasting
14:15:35 PLAN: Intervention selection
14:15:36 APPROVAL: Awaiting human decision
```

### Tip 4: Check Memory
After approving actions, visit:
```
http://localhost:8000/api/agent/memory
```
To see recorded actions and outcomes.

### Tip 5: Observe Confidence
Notice how confidence changes based on:
- Time of day
- Area type
- Speed degradation
- Historical patterns

---

## 🐛 Troubleshooting

**Q: Agent panel not opening?**
A: Click the 🤖 button in top navigation (next to theme button)

**Q: Analysis taking too long?**
A: API calls to TomTom/Groq take time. Wait 10-30 seconds.

**Q: No recommendation showing?**
A: Check if backend is running. If no critical areas, agent shows "monitoring" state.

**Q: Can't see activity log?**
A: Scroll down in agent panel to see log section.

**Q: Errors about missing API keys?**
A: Ensure .env file has TOMTOM_API_KEY, GROQ_API_KEY, STADIA_MAPS_API_KEY

---

## 📊 Expected Outputs

### Best Case Scenario
```
Location: Hinjewadi
Congestion: 8.7 → 6.2 (28.7% improvement)
Time: 5 seconds analysis + 2 seconds simulation
Status: ✓ SUCCESSFUL
```

### Graceful Fallback
If Groq API unavailable:
- Root cause analysis uses rule-based fallback
- Recommendations still generated
- System remains functional

If TomTom API unavailable:
- Uses time-based fallback predictions
- Pattern matching still works
- Dashboard shows "time-estimated" data

---

## 🎓 Learning Outcomes

After this demo, you'll understand:

1. **Autonomous Agents** - How agents operate independently
2. **Decision Loops** - OBSERVE → REASON → PLAN → ACT → EVALUATE
3. **Tool Use** - How agents leverage external systems
4. **Human-in-Loop** - Why approval gates matter
5. **Confidence Scoring** - Measuring decision quality
6. **Feedback Loops** - How agents learn from outcomes
7. **Real-Time Systems** - Combining APIs with AI
8. **Safety Design** - Preventing uncontrolled autonomous systems

---

## 🎉 Next Steps (For Production)

1. **Real Actionability**
   - Connect to actual traffic signal systems
   - Implement real route diversion via apps
   - Send alerts to traffic authorities

2. **Enhanced Learning**
   - Use machine learning to improve predictions
   - Build models from historical outcome data
   - Personalize interventions per location

3. **Multi-Agent Coordination**
   - Separate agents for different cities
   - Agents communicate during congestion spillover
   - Coordinated intervention planning

4. **Advanced Reasoning**
   - Natural language explanation generation
   - Causal reasoning for deeper analysis
   - What-if scenario simulation

5. **Integration**
   - Integrate with Google Maps/Waze for alerts
   - Connect to public transit systems
   - Coordinate with police/traffic authorities

---

## 📞 Support

**Documentation:** See `AGENT_IMPLEMENTATION.md`

**API Docs:** http://localhost:8000/docs (Swagger)

**Issues:** Check browser console for errors

**Logs:** Check terminal where uvicorn is running

---

**Ready? Start the demo now!** 🚦🤖
