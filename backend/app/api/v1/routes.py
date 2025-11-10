# backend/app/api/v1/routes.py

from fastapi import APIRouter, HTTPException, Query
from backend.app.models.models import PlanRequest, PlanResponse
from backend.app.services.planner import Planner
from backend.app.services.simulator import Simulator
from backend.app.services.analytics import Analytics
from backend.app.services.exporter import Exporter
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()
planner = Planner()  # Loads mumbai_roads.geojson with 70 km/h speed
simulator = Simulator(planner)
analytics = Analytics(simulator)
exporter = Exporter()

@router.post("/plan")
def plan_deployment(req: PlanRequest):
    """
    Generate optimal deployment plan with route details.
    Features: KDTree routing, multi-criteria assignment, auto-reassignment.
    """
    try:
        logger.info(f"[API] Planning for {len(req.incidents)} incidents, {len(req.units)} units")
        plan_result = planner.plan(req.incidents, req.units)
        
        assigned = plan_result.get('suggestions', {}).get('assigned', 0)
        logger.info(f"[API] Plan complete: {assigned} incidents assigned")
        
        return plan_result
    except Exception as e:
        logger.error(f"[API] Planning error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")

@router.post("/simulate")
def run_simulation(req: PlanRequest, interval: float = Query(1.0, gt=0.1, le=5.0), 
                   steps: int = Query(10, ge=1, le=100)):
    """
    Execute simulation with interpolated position tracking.
    Features: Adaptive frame rate, synchronized multi-vehicle playback.
    """
    try:
        logger.info(f"[API] Starting simulation: interval={interval}s, steps={steps}")
        simulator.load(req.units, req.incidents)
        plan_result = planner.plan(req.incidents, req.units)
        sim_result = simulator.step_simulate_plan(plan_result, interval)
        
        simulator.state['events'].append({
            'step': steps,
            'simulation_data': sim_result
        })
        
        max_frames = sim_result.get('max_frames', 0)
        logger.info(f"[API] Simulation complete: {max_frames} frames generated")
        return {'events': simulator.state['events']}
    except Exception as e:
        logger.error(f"[API] Simulation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/congestion")
def update_congestion(updates: List[Dict]):
    """Dynamically update road segment speeds for traffic modeling."""
    try:
        updated_count = 0
        for update in updates:
            u, v = update['node_from'], update['node_to']
            new_speed = update['speed_kmph']
            planner.graph.update_edge_speed(u, v, new_speed)
            updated_count += 1
        
        return {
            'status': 'success',
            'updated_edges': updated_count
        }
    except Exception as e:
        logger.error(f"[API] Congestion update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
def get_analytics_summary():
    """Generate comprehensive analytics from simulation history."""
    try:
        return analytics.summary()
    except Exception as e:
        logger.error(f"[API] Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csv")
def export_csv():
    """Export simulation logs as downloadable CSV."""
    try:
        return exporter.export_csv()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/json")
def export_json():
    """Export simulation logs as JSON."""
    try:
        return exporter.export_json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph/stats")
def get_graph_statistics():
    """Return road network statistics and configuration."""
    try:
        bounds = planner.graph.get_subgraph_bounds()
        return {
            'total_nodes': planner.graph.G.number_of_nodes(),
            'total_edges': planner.graph.G.number_of_edges(),
            'bounds': bounds,
            'kdtree_enabled': planner.graph._kdtree is not None,
            'geojson_loaded': 'mumbai_roads.geojson',
            'emergency_speed_kmph': 70
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache")
def clear_graph_cache():
    """Force rebuild of graph cache on next load."""
    try:
        import shutil
        from pathlib import Path
        cache_dir = Path("backend/cache")
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
        return {'status': 'success', 'message': 'Graph cache cleared. Restart server to rebuild.'}
    except Exception as e:
        logger.error(f"[API] Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
