from backend.app.services.planner import Planner

def test_planner_assigns():
    planner = Planner()
    incidents = [
        {'id':'i1','lat':0,'lon':0,'type':'medical'},
        {'id':'i2','lat':10,'lon':10,'type':'fire'}
    ]
    units = [
        {'id':'u1','lat':0.1,'lon':0.2,'type':'ambulance','available':True},
        {'id':'u2','lat':10.1,'lon':10.1,'type':'fire','available':True}
    ]
    out = planner.plan(incidents, units)
    assert 'assignments' in out
    # each unit assigned nearest incident
    assert out['assignments']['u1'] == ['i1']
    assert out['assignments']['u2'] == ['i2']
