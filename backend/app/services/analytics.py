from typing import Dict, Any
import math

class Analytics:
    def __init__(self, simulator=None):
        self.simulator = simulator

    def summary(self) -> Dict[str, Any]:
        """Summarize simulation events or logs."""
        events = []
        if self.simulator and self.simulator.state["events"]:
            events = self.simulator.state["events"]

        if not events:
            return {
                "total_assignments": 0,
                "avg_distance": 0.0,
                "unit_usage_balance": {},
                "most_active_unit": None
            }

        unit_usage = {}
        total_dist = 0.0
        total_moves = 0

        for snapshot in events:
            for e in snapshot.get("events", []):
                uid = e["unit"]
                unit_usage[uid] = unit_usage.get(uid, 0) + 1
                total_moves += 1

        if total_moves > 0:
            avg_distance = round(total_dist / total_moves, 3)
        else:
            avg_distance = 0.0

        most_active = max(unit_usage, key=unit_usage.get) if unit_usage else None

        return {
            "total_assignments": total_moves,
            "avg_distance": avg_distance,
            "unit_usage_balance": unit_usage,
            "most_active_unit": most_active,
        }
