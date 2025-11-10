from typing import List, Dict, Set

def inclusion_exclusion_total(zones: Dict[str, Set[str]]) -> Dict[str, int]:
    """
    zones: mapping zone_name -> set(resource_ids) assigned to that zone
    Returns mapping zone_name -> true resource count after accounting overlaps
    (here returns counts per zone using inclusion/exclusion across pairwise overlaps).
    For simplicity we compute:
      true_count(zone) = |zone_set| - sum(|zone ∩ other|) + sum(|zone ∩ other ∩ other2|) ...
    Limited to up to triple intersections for speed; extend as needed.
    """
    from itertools import combinations
    result = {}
    names = list(zones.keys())
    for i, name in enumerate(names):
        base = zones[name]
        total = len(base)
        # subtract pairwise overlaps
        for j in range(len(names)):
            if j == i:
                continue
            inter = base & zones[names[j]]
            total -= len(inter)
        # add back triple overlaps
        for a, b in combinations([n for n in names if n != name], 2):
            inter = base & zones[a] & zones[b]
            total += len(inter)
        result[name] = max(0, total)
    return result
