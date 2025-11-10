from typing import Dict, Set
from itertools import product

def warshall_closure(adj: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Compute transitive closure (Warshall) on adjacency dictionary.
    adj: mapping node -> set(neighbors)
    Returns mapping node -> set(reachable nodes)
    """
    nodes = list(adj.keys())
    reach = {u: set(adj.get(u, set())) for u in nodes}
    for u in nodes:
        reach[u].add(u)
    for k in nodes:
        for i, j in product(nodes, nodes):
            if k in reach[i] and j in reach[k]:
                reach[i].add(j)
    return reach
