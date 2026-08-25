# Agent Orchestrator - Main coordination of agent loop

import json
from datetime import datetime
from typing import Dict, List, Optional

from modules.agent_tools import AgentTools
from modules.agent_memory import memory
from modules.traffic_analysis import analyse_city_traffic


class TrafficIQAgent:
    """Main orchestrator for the TrafficIQ autonomous agent."""

    def __init__(self, city_name: str):
        self.city_name = city_name
        self.tools = AgentTools()
        self.state = {
            "phase": "initialization",
            "city": city_name,
            "timestamp": str(datetime.now()),
            "steps": []
        }

    def _log_step(self, phase: str, description: str, data: Optional[Dict] = None):
        """Log a step in the agent reasoning process."""
        step = {
            "phase": phase,
            "time": str(datetime.now()),
            "description": description,
            "data": data or {}
        }
        self.state["steps"].append(step)
        print(f"[agent] {phase.upper()}: {description}")

    def run(self, city_traffic_data: Dict) -> Dict:
        """
        Execute complete agent loop:
        OBSERVE → ANALYZE → REASON → PLAN → REQUEST APPROVAL → RETURN PROPOSAL
        
        The actual ACT phase happens after human approval via a separate call.
        """
        self.state["phase"] = "observe"
        
        # ── STEP 1: OBSERVE ──────────────────────────────────────────────────────
        self._log_step("observe", "Monitoring traffic conditions")
        current_traffic = self.tools.get_current_traffic(city_traffic_data.get("areas", []))
        critical_areas = self.tools.get_critical_areas(current_traffic)
        
        self._log_step("observe", f"Detected {len(critical_areas)} critical areas", 
                      {"critical_areas": [a.get("area_name") for a in critical_areas]})
        
        if not critical_areas:
            self._log_step("observe", "No critical congestion detected. Continuing monitoring.")
            return {
                "status": "monitoring",
                "message": "All areas operating normally",
                "recommended_action": "CONTINUE_MONITORING",
                "requires_approval": False,
                "steps": self.state["steps"]
            }
        
        # ── STEP 2: ANALYZE (Anomaly Detection) ──────────────────────────────────
        self.state["phase"] = "analyze"
        self._log_step("analyze", f"Analyzing {len(critical_areas)} critical areas for anomalies")
        
        anomalies = []
        for area in critical_areas[:3]:  # Focus on top 3
            anomaly = self.tools.detect_anomaly(area)
            if anomaly["is_anomaly"]:
                anomalies.append(anomaly)
                self._log_step("analyze", 
                             f"Anomaly detected in {area.get('area_name')}: deviation +{anomaly['deviation']} points",
                             anomaly)
        
        if not anomalies:
            self._log_step("analyze", "No anomalies detected. Congestion is expected for this time.")
            anomalies = [self.tools.detect_anomaly(critical_areas[0])]
        
        primary_anomaly = anomalies[0]
        problem_area = primary_anomaly["area_name"]
        
        # ── STEP 3: REASON (Root Cause Analysis) ──────────────────────────────────
        self.state["phase"] = "reason"
        self._log_step("reason", f"Investigating root causes for {problem_area}")
        
        area_data = next((a for a in critical_areas if a.get("area_name") == problem_area), None)
        if not area_data:
            return {
                "status": "error",
                "message": f"Could not find area data for {problem_area}",
                "steps": self.state["steps"]
            }
        
        area_type = self._classify_area(problem_area)
        root_cause = self.tools.analyze_root_cause(area_data, area_type, city_traffic_data)
        
        self._log_step("reason", 
                      f"Probable cause: {root_cause['top_cause']} (confidence: {root_cause['probable_causes'][0]['confidence']:.0%})",
                      {"top_cause": root_cause["top_cause"], 
                       "causes": root_cause["probable_causes"]})
        
        # ── STEP 4: PREDICT ──────────────────────────────────────────────────────
        self.state["phase"] = "predict"
        self._log_step("predict", f"Predicting congestion trend for {problem_area}")
        
        trend = self.tools.predict_congestion_trend(
            problem_area, 
            area_type,
            area_data.get("congestion_score", 0)
        )
        
        self._log_step("predict", 
                      f"Trend: {trend['trend']} - {trend['predictions'][-1]['level']} in 3 hours",
                      {"trend": trend["trend"], "predictions": trend["predictions"]})
        
        # ── STEP 5: PLAN (Decision Making) ──────────────────────────────────────
        self.state["phase"] = "plan"
        self._log_step("plan", "Evaluating possible interventions")
        
        intervention_options = self.tools.propose_interventions(
            area_data,
            root_cause["top_cause"],
            trend["trend"]
        )
        
        # Select best intervention
        best_action = self._select_best_action(
            intervention_options["interventions"],
            area_data.get("congestion_score", 0),
            trend["trend"]
        )
        
        self._log_step("plan", 
                      f"Selected intervention: {best_action['action']}",
                      best_action)
        
        # Simulate the action
        self.state["phase"] = "simulate"
        self._log_step("simulate", f"Simulating impact of {best_action['action']}")
        
        simulation = self.tools.simulate_action(best_action, area_data)
        self._log_step("simulate", 
                      f"Simulated improvement: {simulation['expected_improvement']}",
                      simulation)
        
        # ── STEP 6: PREPARE FOR APPROVAL ────────────────────────────────────────
        self.state["phase"] = "approval_pending"
        action_id = memory.record_action({
            "location": problem_area,
            "action_type": best_action["action"],
            "description": best_action.get("description", ""),
            "congestion_before": area_data.get("congestion_score", 0),
            "expected_impact": simulation["expected_improvement"],
            "reasoning": root_cause["top_cause"],
            "confidence": root_cause["probable_causes"][0]["confidence"]
        })
        
        return {
            "status": "approval_required",
            "action_id": action_id,
            "location": problem_area,
            "problem": {
                "congestion_score": area_data.get("congestion_score", 0),
                "congestion_level": area_data.get("congestion_level", "UNKNOWN"),
                "speed": area_data.get("current_speed", 0),
                "free_flow_speed": area_data.get("free_flow_speed", 0)
            },
            "root_cause": {
                "cause": root_cause["top_cause"],
                "confidence": root_cause["probable_causes"][0]["confidence"],
                "evidence": root_cause["probable_causes"][0]["evidence"]
            },
            "trend": {
                "direction": trend["trend"],
                "predictions": trend["predictions"]
            },
            "recommended_action": {
                "action": best_action["action"],
                "description": best_action.get("description", ""),
                "expected_impact": simulation["expected_improvement"],
                "risk": best_action.get("risk", "UNKNOWN"),
                "implementation_time": best_action.get("implementation_time", "Unknown")
            },
            "requires_approval": best_action.get("requires_approval", True),
            "steps": self.state["steps"]
        }

    def execute_approved_action(self, action_id: str, approve: bool) -> Dict:
        """
        Execute an approved action and monitor results.
        This is called after human approval.
        """
        action_history = memory.get_action_history()
        action = next((a for a in action_history if a["id"] == action_id), None)
        
        if not action:
            return {"status": "error", "message": f"Action {action_id} not found"}
        
        if not approve:
            memory.update_action_outcome(action_id, {
                "status": "REJECTED",
                "feedback": "Human rejected the proposed intervention"
            })
            return {
                "status": "rejected",
                "action_id": action_id,
                "message": "Action was rejected by human operator"
            }
        
        # Execute simulated action
        congestion_before = action.get("congestion_before", 0)
        impact_percent = float(action.get("expected_impact", "0").replace("%", ""))
        congestion_after = congestion_before * (1 - impact_percent / 100)
        
        # Record outcome
        improvement = round((congestion_before - congestion_after) / max(congestion_before, 1) * 100, 1)
        
        memory.update_action_outcome(action_id, {
            "status": "SUCCESSFUL",
            "congestion_before": congestion_before,
            "congestion_after": round(congestion_after, 1),
            "improvement_percentage": improvement,
            "execution_time": str(datetime.now()),
            "feedback": "Simulated action completed successfully"
        })
        
        return {
            "status": "executed",
            "action_id": action_id,
            "result": {
                "congestion_before": congestion_before,
                "congestion_after": round(congestion_after, 1),
                "improvement_percentage": improvement,
                "message": f"Action {action.get('action_type')} executed. Congestion reduced by {improvement}%"
            }
        }

    def _classify_area(self, area_name: str) -> str:
        """Classify area type for reasoning."""
        from modules.traffic_predictor import classify_area_type
        return classify_area_type(area_name)

    def _select_best_action(self, interventions: List[Dict], 
                           congestion_score: float, trend: str) -> Dict:
        """
        Select the best intervention from options using simple heuristics.
        
        Scoring:
        - Higher confidence: +points
        - Lower risk: +points
        - Matches trend: +points
        - Requires approval: consider impact
        """
        if not interventions:
            return {
                "action": "CONTINUE_MONITORING",
                "description": "Continue monitoring situation",
                "expected_impact": "0%",
                "risk": "NONE"
            }
        
        for intervention in interventions:
            score = intervention.get("confidence", 0.5)
            
            # Bonus for low risk
            if intervention.get("risk", "").upper() in ["LOW", "VERY LOW"]:
                score += 0.15
            
            # Bonus if it addresses worsening trend
            if trend == "WORSENING" and "SIGNAL" in intervention.get("action", ""):
                score += 0.10
            
            intervention["selection_score"] = score
        
        # Sort by score and return top
        best = sorted(interventions, key=lambda x: x.get("selection_score", 0), reverse=True)[0]
        return best

    def get_state(self) -> Dict:
        """Return current agent state for UI."""
        return self.state
