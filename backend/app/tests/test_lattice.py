from backend.app.core.lattice import Poset

def test_poset_basic():
    elems = ['civilian','ambulance','fire']
    lt = [('civilian','ambulance'), ('ambulance','fire')]
    p = Poset(elems, lt)
    assert p.is_less_or_equal('civilian','fire') is True
    assert p.is_less_or_equal('fire','civilian') is False
