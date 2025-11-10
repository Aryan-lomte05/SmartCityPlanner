from typing import Dict, List, Any

class Poset:
    """
    Minimal poset/lattice utilities — represent as adjacency for cover relations.
    We assume a finite set of elements with partial order given via 'less_than' pairs.
    """
    def __init__(self, elements: List[str], less_than_pairs: List[tuple]):
        self.elements = elements
        self.less_than = {e: set() for e in elements}
        for a, b in less_than_pairs:
            # a < b
            self.less_than[a].add(b)

    def is_less_or_equal(self, a: str, b: str) -> bool:
        # simple DFS
        visited = set()
        stack = [a]
        while stack:
            cur = stack.pop()
            if cur == b:
                return True
            for nxt in self.less_than.get(cur, []):
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)
        return False

    def upper_bounds(self, subset: List[str]) -> List[str]:
        return [e for e in self.elements if all(self.is_less_or_equal(x, e) for x in subset)]

    def least_upper_bound(self, subset: List[str]) -> str:
        ubs = self.upper_bounds(subset)
        # pick minimal among ubs (heuristic: element with smallest count of upper relations)
        if not ubs:
            return None
        ubs.sort(key=lambda e: len(self.less_than.get(e, set())))
        return ubs[0]
