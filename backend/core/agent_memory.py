# Agent Memory System - Tracks actions, outcomes, and historical incidents

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

MEMORY_FILE = "agent_memory.json"


class AgentMemory:
    """Simple JSON-based memory for tracking agent decisions and outcomes."""

    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.data = self._load()

    def _load(self) -> Dict:
        """Load memory from file or initialize empty structure."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return self._init_empty()
        return self._init_empty()

    def _init_empty(self) -> Dict:
        """Initialize empty memory structure."""
        return {
            "actions": [],
            "incidents": [],
            "learnings": [],
            "intervention_history": {},
        }

    def _save(self):
        """Save memory to file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[memory] Failed to save: {e}")

    def record_action(self, action: Dict) -> str:
        """
        Record an agent action.
        
        action = {
            "location": "Hinjewadi",
            "action_type": "SIGNAL_TIMING_ADJUSTMENT",
            "timestamp": "...",
            "congestion_before": 8.7,
            "expected_impact": "18% reduction",
            "reasoning": "...",
            "confidence": 0.84
        }
        """
        action_id = f"action_{len(self.data['actions']) + 1}"
        action["id"] = action_id
        action["recorded_at"] = str(datetime.now())
        action["status"] = "proposed"
        self.data["actions"].append(action)
        self._save()
        return action_id

    def record_incident(self, incident: Dict) -> str:
        """Record a traffic incident detected by the agent."""
        incident_id = f"incident_{len(self.data['incidents']) + 1}"
        incident["id"] = incident_id
        incident["detected_at"] = str(datetime.now())
        self.data["incidents"].append(incident)
        self._save()
        return incident_id

    def update_action_outcome(self, action_id: str, outcome: Dict):
        """
        Update action with outcome after execution.
        
        outcome = {
            "status": "SUCCESSFUL" / "INEFFECTIVE" / "PARTIAL",
            "congestion_after": 6.2,
            "improvement_percentage": 28.7,
            "execution_time": "...",
            "feedback": "..."
        }
        """
        for action in self.data["actions"]:
            if action["id"] == action_id:
                action["status"] = "completed"
                action["outcome"] = outcome
                action["outcome_recorded_at"] = str(datetime.now())
                self._save()
                return True
        return False

    def get_action_history(self, location: Optional[str] = None) -> List[Dict]:
        """Retrieve action history, optionally filtered by location."""
        if location:
            return [a for a in self.data["actions"] 
                   if a.get("location", "").lower() == location.lower()]
        return self.data["actions"]

    def get_recent_incidents(self, location: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent incidents for a location."""
        incidents = self.data["incidents"]
        if location:
            incidents = [i for i in incidents 
                        if i.get("location", "").lower() == location.lower()]
        return incidents[-limit:]

    def find_similar_past_incidents(self, location: str, area_type: str) -> List[Dict]:
        """Find similar past incidents by location or area type."""
        similar = []
        for incident in self.data["incidents"]:
            if (incident.get("location", "").lower() == location.lower() or
                incident.get("area_type", "").lower() == area_type.lower()):
                similar.append(incident)
        return similar[-5:]  # Return last 5 similar incidents

    def get_successful_interventions(self, location: Optional[str] = None) -> List[Dict]:
        """Get past successful interventions."""
        successful = [a for a in self.data["actions"]
                     if a.get("outcome", {}).get("status") == "SUCCESSFUL"]
        if location:
            successful = [a for a in successful
                         if a.get("location", "").lower() == location.lower()]
        return successful

    def record_learning(self, learning: Dict):
        """Record learned pattern or insight."""
        learning["recorded_at"] = str(datetime.now())
        self.data["learnings"].append(learning)
        self._save()

    def get_all_data(self) -> Dict:
        """Get entire memory dump (for debugging)."""
        return self.data

    def clear(self):
        """Clear all memory (for testing)."""
        self.data = self._init_empty()
        self._save()


# Global memory instance
memory = AgentMemory()
