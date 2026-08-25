# Agent Tools - Functions the agent can call

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.realtime_traffic import get_area_traffic, get_congestion_level
from core.traffic_predictor import classify_area_type, predict_score_at_hour
from core.llm_analysis import analyse_traffic_with_llm
from core.data_collection import collect_city_data

# Global city cache (shared with main.py)
CITY_CACHE = {}


class AgentTools:
    """Tools available to the agent for decision-making."""

    @staticmethod
    def get_current_traffic(areas: List[Dict]) -> Dict:
        """
        Get current traffic for multiple areas.
        
        Input: [{"area_name": "Hinjewadi", "lat": 18.591, "lon": 73.738}, ...]
        Output: {
            "status": "ok",
            "timestamp": "2024-01-15 14:35:22",
            "areas": [
                {
                    "area_name": "Hinjewadi",
                    "congestion_score": 8.7,
                    "congestion_level": "CRITICAL",
                    "current_speed": 18,
                    "free_flow_speed": 55,
                    "confidence": 0.95
                }
            ]
        }
        """
        try:
            traffic_data = []
            for area in areas:
                try:
                    traffic = get_area_traffic(
                        area.get("area_name", "Unknown"),
                        area.get("lat", 0),
                        area.get("lon", 0)
                    )
                    traffic_data.append(traffic)
                except Exception as e:
                    print(f"[tools] Error fetching traffic for {area.get('area_name')}: {e}")
            
            return {
                "status": "ok",
                "timestamp": str(datetime.now()),
                "areas": traffic_data,
                "count": len(traffic_data)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @staticmethod
    def get_critical_areas(current_traffic: Dict) -> List[Dict]:
        """
        Filter and return only critical congestion areas.
        
        Input: result from get_current_traffic()
        Output: [{"area_name": "Hinjewadi", "congestion_score": 8.7, ...}]
        """
        critical = []
        for area in current_traffic.get("areas", []):
            if area.get("congestion_level") == "CRITICAL":
                critical.append(area)
        return sorted(critical, key=lambda x: x.get("congestion_score", 0), reverse=True)

    @staticmethod
    def detect_anomaly(area_data: Dict, historical_avg: Optional[float] = None) -> Dict:
        """
        Detect if current traffic is anomalous.
        
        Returns:
        {
            "is_anomaly": True/False,
            "severity": "CRITICAL" / "HIGH" / "MODERATE" / "LOW",
            "deviation": 2.1,  # Score points above normal
            "confidence": 0.87,
            "reasoning": "..."
        }
        """
        current_score = area_data.get("congestion_score", 0)
        area_name = area_data.get("area_name", "Unknown")
        area_type = classify_area_type(area_name)
        
        # Estimate normal score for this time
        hour = datetime.now().hour
        is_weekend = datetime.now().weekday() >= 5
        expected_score = predict_score_at_hour(area_type, hour, is_weekend)
        
        # Use provided historical average if available
        if historical_avg is not None:
            expected_score = historical_avg
        
        deviation = current_score - expected_score
        is_anomaly = deviation > 2.0  # More than 2 points above normal
        
        return {
            "area_name": area_name,
            "is_anomaly": is_anomaly,
            "current_score": current_score,
            "expected_score": expected_score,
            "deviation": round(deviation, 2),
            "severity": get_congestion_level(current_score),
            "confidence": 0.75 + (min(abs(deviation), 5) * 0.05),  # Increase confidence with larger deviation
            "reasoning": f"Current score {current_score} vs expected {expected_score} for {area_type} area at {hour}:00"
        }

    @staticmethod
    def predict_congestion_trend(area_name: str, area_type: str, 
                                 current_score: float) -> Dict:
        """
        Predict congestion trend for next 1-3 hours.
        
        Returns:
        {
            "area_name": "Hinjewadi",
            "trend": "WORSENING" / "STABLE" / "IMPROVING",
            "predictions": [
                {"hour": "15:00", "score": 8.9, "level": "CRITICAL"},
                {"hour": "16:00", "score": 7.5, "level": "HIGH"},
                {"hour": "17:00", "score": 9.2, "level": "CRITICAL"}
            ],
            "confidence": 0.82
        }
        """
        hour = datetime.now().hour
        is_weekend = datetime.now().weekday() >= 5
        
        predictions = []
        for offset in range(1, 4):  # Next 3 hours
            future_hour = (hour + offset) % 24
            predicted_score = predict_score_at_hour(area_type, future_hour, is_weekend)
            predictions.append({
                "hour": f"{future_hour}:00",
                "score": predicted_score,
                "level": get_congestion_level(predicted_score)
            })
        
        # Determine trend
        if predictions[-1]["score"] > current_score + 1:
            trend = "WORSENING"
        elif predictions[-1]["score"] < current_score - 1:
            trend = "IMPROVING"
        else:
            trend = "STABLE"
        
        return {
            "area_name": area_name,
            "trend": trend,
            "current_score": current_score,
            "predictions": predictions,
            "confidence": 0.78
        }

    @staticmethod
    def analyze_root_cause(area_data: Dict, area_type: str, 
                          city_wide_context: Optional[Dict] = None) -> Dict:
        """
        Analyze possible root causes for congestion.
        
        Returns:
        {
            "area_name": "Hinjewadi",
            "probable_causes": [
                {"cause": "Peak-hour IT hub traffic", "confidence": 0.92, "evidence": [...]},
                {"cause": "Road bottleneck capacity limit", "confidence": 0.78, "evidence": [...]}
            ],
            "top_cause": "Peak-hour IT hub traffic",
            "reasoning": "..."
        }
        """
        area_name = area_data.get("area_name", "Unknown")
        congestion_score = area_data.get("congestion_score", 0)
        current_speed = area_data.get("current_speed", 0)
        free_flow_speed = area_data.get("free_flow_speed", 1)
        
        hour = datetime.now().hour
        is_weekend = datetime.now().weekday() >= 5
        
        causes = []
        
        # Check 1: Peak hour
        if (7 <= hour < 10) or (17 <= hour < 21):
            causes.append({
                "cause": "Peak-hour commute traffic",
                "confidence": 0.88,
                "evidence": [
                    f"Current time: {hour}:00 (known peak hours)",
                    f"Congestion score: {congestion_score}/10"
                ]
            })
        
        # Check 2: Area type specific
        if area_type == "IT_HUB":
            causes.append({
                "cause": f"High-traffic IT hub zone ({area_name})",
                "confidence": 0.85,
                "evidence": [
                    f"Area type: {area_type}",
                    "IT hubs experience heavy weekday morning/evening traffic"
                ]
            })
        elif area_type == "MARKET":
            causes.append({
                "cause": f"Market area with heavy foot/vehicle traffic",
                "confidence": 0.80,
                "evidence": [
                    f"Area type: {area_type}",
                    "Market areas have consistently high traffic 10am-9pm"
                ]
            })
        
        # Check 3: Speed degradation
        if free_flow_speed > 0:
            speed_ratio = current_speed / free_flow_speed
            if speed_ratio < 0.4:
                causes.append({
                    "cause": "Severe speed degradation - possible accident/bottleneck",
                    "confidence": 0.75,
                    "evidence": [
                        f"Current speed: {current_speed} km/h",
                        f"Free flow speed: {free_flow_speed} km/h",
                        f"Speed ratio: {speed_ratio:.2%} (normal: 60%+)"
                    ]
                })
        
        # Check 4: Weekend patterns
        if is_weekend and area_type == "MARKET":
            causes.append({
                "cause": "Weekend shopping/leisure traffic in market area",
                "confidence": 0.82,
                "evidence": ["Weekend day detected", f"Area type: {area_type}"]
            })
        
        # Sort by confidence
        causes = sorted(causes, key=lambda x: x["confidence"], reverse=True)
        top_cause = causes[0]["cause"] if causes else "Unknown cause"
        
        return {
            "area_name": area_name,
            "probable_causes": causes,
            "top_cause": top_cause,
            "reasoning": f"Analysis based on time ({hour}:00), area type ({area_type}), and traffic patterns"
        }

    @staticmethod
    def propose_interventions(area_data: Dict, root_cause: str, 
                             predicted_trend: str) -> Dict:
        """
        Propose possible interventions.
        
        Returns:
        {
            "area_name": "Hinjewadi",
            "interventions": [
                {
                    "action": "SIGNAL_TIMING_ADJUSTMENT",
                    "description": "Increase green time on main arterial",
                    "expected_impact": "15-20% congestion reduction",
                    "risk": "LOW",
                    "implementation_time": "Immediate",
                    "requires_approval": True
                },
                {...}
            ]
        }
        """
        area_name = area_data.get("area_name", "Unknown")
        congestion_score = area_data.get("congestion_score", 0)
        
        interventions = []
        
        # Intervention 1: Signal timing
        if congestion_score >= 7:
            interventions.append({
                "action": "SIGNAL_TIMING_ADJUSTMENT",
                "description": "Adaptive signal timing - increase green time on congested arterials",
                "expected_impact": f"{min(20, 5 + congestion_score)}% congestion reduction",
                "risk": "LOW",
                "implementation_time": "1-2 minutes",
                "requires_approval": True,
                "confidence": 0.85
            })
        
        # Intervention 2: Route diversion
        if "peak" in root_cause.lower() or "bottleneck" in root_cause.lower():
            interventions.append({
                "action": "ROUTE_DIVERSION",
                "description": "Alert drivers to use alternate routes via ring roads",
                "expected_impact": "10-15% congestion reduction",
                "risk": "LOW",
                "implementation_time": "Immediate (alerts only)",
                "requires_approval": False,
                "confidence": 0.78
            })
        
        # Intervention 3: Traffic alerts
        if congestion_score >= 8:
            interventions.append({
                "action": "CRITICAL_TRAFFIC_ALERT",
                "description": "Broadcast critical traffic warning to commuters",
                "expected_impact": "5-10% congestion reduction (behavior change)",
                "risk": "VERY LOW",
                "implementation_time": "Immediate",
                "requires_approval": False,
                "confidence": 0.72
            })
        
        # Intervention 4: Public transport
        interventions.append({
            "action": "BOOST_PUBLIC_TRANSIT",
            "description": "Increase bus/metro frequency on high-volume routes",
            "expected_impact": "8-12% congestion reduction (medium-term)",
            "risk": "LOW",
            "implementation_time": "15-30 minutes",
            "requires_approval": True,
            "confidence": 0.75
        })
        
        # Intervention 5: Incident escalation
        if predicted_trend == "WORSENING" and congestion_score >= 8:
            interventions.append({
                "action": "ESCALATE_TO_AUTHORITY",
                "description": "Notify traffic management authority for manual intervention",
                "expected_impact": "Variable",
                "risk": "LOW",
                "implementation_time": "Immediate notification",
                "requires_approval": False,
                "confidence": 0.80
            })
        
        return {
            "area_name": area_name,
            "intervention_count": len(interventions),
            "interventions": interventions
        }

    @staticmethod
    def simulate_action(action: Dict, before_state: Dict) -> Dict:
        """
        Simulate the effect of an action without executing it.
        
        Input:
        {
            "action": "SIGNAL_TIMING_ADJUSTMENT",
            "area_name": "Hinjewadi",
            "description": "..."
        }
        
        Returns simulated after-state
        """
        action_type = action.get("action", "UNKNOWN")
        congestion_before = before_state.get("congestion_score", 0)
        
        # Simulate impact
        if action_type == "SIGNAL_TIMING_ADJUSTMENT":
            reduction = min(25, 5 + congestion_before * 1.5)  # 5-25% reduction
            congestion_after = max(0, congestion_before - (congestion_before * reduction / 100))
        elif action_type == "ROUTE_DIVERSION":
            reduction = min(15, 10 + congestion_before)
            congestion_after = max(0, congestion_before - (congestion_before * reduction / 100))
        elif action_type == "CRITICAL_TRAFFIC_ALERT":
            reduction = min(10, 3 + congestion_before * 0.5)
            congestion_after = max(0, congestion_before - (congestion_before * reduction / 100))
        else:
            congestion_after = congestion_before
            reduction = 0
        
        improvement = round((congestion_before - congestion_after) / max(congestion_before, 1) * 100, 1)
        
        return {
            "action": action_type,
            "congestion_before": congestion_before,
            "congestion_after": round(congestion_after, 1),
            "expected_improvement": f"{improvement}%",
            "simulation_status": "SUCCESS"
        }

    @staticmethod
    def get_city_context(city_name: str, city_traffic: Dict) -> Dict:
        """Get city-wide context for decision making."""
        return {
            "city": city_name,
            "overall_score": city_traffic.get("overall_score", 0),
            "overall_level": city_traffic.get("overall_level", "UNKNOWN"),
            "total_areas": len(city_traffic.get("areas", [])),
            "critical_count": len([a for a in city_traffic.get("areas", []) 
                                  if a.get("congestion_level") == "CRITICAL"]),
            "high_count": len([a for a in city_traffic.get("areas", []) 
                             if a.get("congestion_level") == "HIGH"]),
            "timestamp": str(datetime.now())
        }
