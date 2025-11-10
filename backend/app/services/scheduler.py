from typing import List, Dict, Any
import time
def schedule_tasks(plan: Dict[str, List[str]]):
    """
    Simple scheduler: converts plan (unit->incident list) into a list of timed tasks.
    This is a placeholder for richer priority/time-window scheduling.
    """
    timeline = []
    now = time.time()
    for unit_id, incs in plan.items():
        start = now
        for inc in incs:
            timeline.append({"unit": unit_id, "incident": inc, "start": start, "estimated_duration": 300})
            start += 300
    return timeline
