from typing import List, Dict, Any
import math

def pigeonhole_alloc(incidents: List[Dict[str, Any]], units: List[Dict[str, Any]]):
    """
    Simple allocation: distribute incidents across available units as evenly as possible.
    Returns mapping unit_id -> list of incident_ids.
    """
    available_units = [u for u in units if u.get('available', True)]
    if not available_units:
        return {}
    m = len(incidents)
    n = len(available_units)
    base = m // n
    extra = m % n  # first 'extra' units get one additional incident
    alloc = {}
    it = iter(incidents)
    for i, unit in enumerate(available_units):
        cnt = base + (1 if i < extra else 0)
        alloc[unit['id']] = [next(it)['id'] for _ in range(cnt)] if cnt > 0 else []
    return alloc
