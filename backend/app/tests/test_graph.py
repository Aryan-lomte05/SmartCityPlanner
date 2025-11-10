from backend.app.core.graph_model import GraphModel

def test_shortest_path_simple():
    g = GraphModel()
    g.add_node("A"); g.add_node("B"); g.add_node("C")
    g.add_edge("A", "B", base_time=1.0)
    g.add_edge("B", "C", base_time=1.0)
    path = g.shortest_path("A","C")
    assert path == ["A","B","C"]
