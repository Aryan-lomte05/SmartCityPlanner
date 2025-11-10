# # backend/app/services/simulator.py

# from typing import List, Dict, Any
# import math
# import logging
# from backend.app.core.graph_model import haversine_km

# logger = logging.getLogger(__name__)

# class Simulator:
#     """
#     GODMODE++ emergency response simulator with:
#     - Smooth interpolation along real road paths
#     - Synchronized multi-unit playback
#     - Adaptive frame rate for fast animation
#     - Pydantic model compatibility
#     """
    
#     def __init__(self, planner):
#         self.planner = planner
#         self.running = False
#         self.state = {"units": [], "incidents": [], "events": []}

#     def _get_field(self, obj: Any, name: str, default: Any = None) -> Any:
#         """Universal field accessor for Pydantic models and dicts."""
#         if hasattr(obj, name):
#             return getattr(obj, name)
#         if isinstance(obj, dict):
#             return obj.get(name, default)
#         return default

#     def load(self, units: List[Any], incidents: List[Any]):
#         """Initialize simulation state."""
#         self.state['units'] = units
#         self.state['incidents'] = incidents
#         self.state['events'] = []

#     def _interpolate_along_path(self, path: List[tuple], total_time: float, 
#                                 step_time: float) -> List[Dict]:
#         """
#         Generate smooth position interpolation along road path.
#         Returns list of {lat, lon, progress, remaining_time} dicts.
#         """
#         if not path or total_time <= 0:
#             return []
        
#         # Calculate cumulative distances
#         cumulative_dist = [0.0]
#         for i in range(1, len(path)):
#             dist = haversine_km(path[i-1], path[i])
#             cumulative_dist.append(cumulative_dist[-1] + dist)
        
#         total_dist = cumulative_dist[-1]
#         if total_dist == 0:
#             return [{'lat': path[0][0], 'lon': path[0][1], 'progress': 100, 'remaining_time': 0}]
        
#         # Generate interpolated positions
#         positions = []
#         elapsed = 0.0
        
#         while elapsed <= total_time:
#             progress_ratio = elapsed / total_time
#             target_dist = progress_ratio * total_dist
            
#             # Find segment containing target distance
#             for i in range(1, len(cumulative_dist)):
#                 if cumulative_dist[i] >= target_dist:
#                     segment_start_dist = cumulative_dist[i-1]
#                     segment_end_dist = cumulative_dist[i]
#                     segment_progress = (target_dist - segment_start_dist) / max(0.001, segment_end_dist - segment_start_dist)
                    
#                     lat1, lon1 = path[i-1]
#                     lat2, lon2 = path[i]
                    
#                     interp_lat = lat1 + (lat2 - lat1) * segment_progress
#                     interp_lon = lon1 + (lon2 - lon1) * segment_progress
                    
#                     positions.append({
#                         'lat': round(interp_lat, 6),
#                         'lon': round(interp_lon, 6),
#                         'progress': round(progress_ratio * 100, 1),
#                         'remaining_time': round(total_time - elapsed, 1)
#                     })
#                     break
            
#             elapsed += step_time
        
#         # Ensure final position
#         if positions and positions[-1]['progress'] < 100:
#             positions.append({
#                 'lat': path[-1][0],
#                 'lon': path[-1][1],
#                 'progress': 100,
#                 'remaining_time': 0
#             })
        
#         return positions

#     def step_simulate_plan(self, plan_result: Dict, interval: float = 1.0) -> Dict:
#         """
#         Generate complete timeline for ALL units with synchronized playback.
#         🔥 ADAPTIVE FRAME RATE: Uses smart interval to limit max frames to 60-120 per route.
#         """
#         route_details = plan_result.get('route_details', {})
        
#         if not route_details:
#             return {'timeline': [], 'max_frames': 0}
        
#         timeline = []
        
#         for inc_id, details in route_details.items():
#             unit_id = details['unit_id']
#             unit_type = details['unit_type']
#             path = details['path']
#             eta_s = details['eta_seconds']
#             distance_km = details['distance_km']
            
#             if not path:
#                 continue
            
#             # 🔥 ADAPTIVE INTERVAL: Limit frames to 60-120 for smooth but fast playback
#             adaptive_interval = max(5.0, eta_s / 80.0)  # Target ~80 frames per route
            
#             positions = self._interpolate_along_path(path, eta_s, adaptive_interval)
            
#             timeline.append({
#                 'unit_id': unit_id,
#                 'unit_type': unit_type,
#                 'incident_id': inc_id,
#                 'total_eta_seconds': eta_s,
#                 'total_distance_km': distance_km,
#                 'start_pos': {'lat': path[0][0], 'lon': path[0][1]},
#                 'end_pos': {'lat': path[-1][0], 'lon': path[-1][1]},
#                 'positions': positions,
#                 'path': path,
#                 'total_frames': len(positions)
#             })
        
#         max_frames = max(len(t['positions']) for t in timeline) if timeline else 0
        
#         logger.info(f"[Simulator] Generated {max_frames} max frames for {len(timeline)} units")
        
#         return {
#             'timeline': timeline,
#             'max_frames': max_frames,
#             'total_units': len(timeline),
#             'interval_seconds': adaptive_interval
#         }

#     def run(self, interval: float = 1.0, steps: int = 10) -> List[Dict]:
#         """Legacy run method for backward compatibility."""
#         if not self.state['units'] or not self.state['incidents']:
#             logger.warning("Simulator state not loaded")
#             return []
        
#         plan_result = self.planner.plan(self.state['incidents'], self.state['units'])
#         sim_result = self.step_simulate_plan(plan_result, interval)
        
#         self.state['events'].append({
#             'step': steps,
#             'simulation_data': sim_result
#         })
        
#         return self.state['events']
# backend/app/services/simulator.py

from typing import List, Dict, Any
import math
import logging
from backend.app.core.graph_model import haversine_km

logger = logging.getLogger(__name__)

class Simulator:
    """
    GODMODE simulator with adaptive frame rate and smooth interpolation.
    """
    
    def __init__(self, planner):
        self.planner = planner
        self.running = False
        self.state = {"units": [], "incidents": [], "events": []}

    def _get_field(self, obj: Any, name: str, default: Any = None) -> Any:
        """Universal field accessor for Pydantic models and dicts."""
        if hasattr(obj, name):
            return getattr(obj, name)
        if isinstance(obj, dict):
            return obj.get(name, default)
        return default

    def load(self, units: List[Any], incidents: List[Any]):
        """Initialize simulation state."""
        self.state['units'] = units
        self.state['incidents'] = incidents
        self.state['events'] = []

    def _interpolate_along_path(self, path: List[tuple], total_time: float, 
                                step_time: float) -> List[Dict]:
        """
        Generate smooth position interpolation along road path.
        """
        if not path or total_time <= 0:
            return []
        
        cumulative_dist = [0.0]
        for i in range(1, len(path)):
            dist = haversine_km(path[i-1], path[i])
            cumulative_dist.append(cumulative_dist[-1] + dist)
        
        total_dist = cumulative_dist[-1]
        if total_dist == 0:
            return [{'lat': path[0][0], 'lon': path[0][1], 'progress': 100, 'remaining_time': 0}]
        
        positions = []
        elapsed = 0.0
        
        while elapsed <= total_time:
            progress_ratio = elapsed / total_time
            target_dist = progress_ratio * total_dist
            
            for i in range(1, len(cumulative_dist)):
                if cumulative_dist[i] >= target_dist:
                    segment_start_dist = cumulative_dist[i-1]
                    segment_end_dist = cumulative_dist[i]
                    segment_progress = (target_dist - segment_start_dist) / max(0.001, segment_end_dist - segment_start_dist)
                    
                    lat1, lon1 = path[i-1]
                    lat2, lon2 = path[i]
                    
                    interp_lat = lat1 + (lat2 - lat1) * segment_progress
                    interp_lon = lon1 + (lon2 - lon1) * segment_progress
                    
                    positions.append({
                        'lat': round(interp_lat, 6),
                        'lon': round(interp_lon, 6),
                        'progress': round(progress_ratio * 100, 1),
                        'remaining_time': round(total_time - elapsed, 1)
                    })
                    break
            
            elapsed += step_time
        
        if positions and positions[-1]['progress'] < 100:
            positions.append({
                'lat': path[-1][0],
                'lon': path[-1][1],
                'progress': 100,
                'remaining_time': 0
            })
        
        return positions

    def step_simulate_plan(self, plan_result: Dict, interval: float = 1.0) -> Dict:
        """
        Generate complete timeline with adaptive frame rate.
        🔥 FIX: Create separate timeline entry for EVERY incident assignment.
        """
        route_details = plan_result.get('route_details', {})
        
        if not route_details:
            return {'timeline': [], 'max_frames': 0}
        
        timeline = []
        
        # 🔥 FIX: Iterate through ALL route_details entries (including duplicate units)
        for inc_id, details in route_details.items():
            unit_id = details['unit_id']
            unit_type = details['unit_type']
            path = details['path']
            eta_s = details['eta_seconds']
            distance_km = details['distance_km']
            
            if not path:
                logger.warning(f"[Simulator] No path for incident {inc_id}")
                continue
            
            # Adaptive interval: limit frames to ~80 per route
            adaptive_interval = max(5.0, eta_s / 80.0)
            
            positions = self._interpolate_along_path(path, eta_s, adaptive_interval)
            
            # 🔥 FIX: Use UNIQUE KEY combining unit_id and incident_id
            timeline_entry = {
                'unit_id': unit_id,
                'unit_type': unit_type,
                'incident_id': inc_id,
                'assignment_key': f"{unit_id}→{inc_id}",  # Unique identifier
                'total_eta_seconds': eta_s,
                'total_distance_km': distance_km,
                'start_pos': {'lat': path[0][0], 'lon': path[0][1]},
                'end_pos': {'lat': path[-1][0], 'lon': path[-1][1]},
                'positions': positions,
                'path': path,
                'total_frames': len(positions)
            }
            
            timeline.append(timeline_entry)
            logger.info(f"[Simulator] Generated {len(positions)} frames for {unit_id} → {inc_id}")
        
        max_frames = max(len(t['positions']) for t in timeline) if timeline else 0
        
        logger.info(f"[Simulator] Generated {max_frames} max frames for {len(timeline)} assignments")
        
        return {
            'timeline': timeline,
            'max_frames': max_frames,
            'total_units': len(set(t['unit_id'] for t in timeline)),  # Count unique units
            'total_assignments': len(timeline),  # Total assignments
            'interval_seconds': adaptive_interval if timeline else 0
        }

    def run(self, interval: float = 1.0, steps: int = 10) -> List[Dict]:
        """Legacy run method for backward compatibility."""
        if not self.state['units'] or not self.state['incidents']:
            logger.warning("Simulator state not loaded")
            return []
        
        plan_result = self.planner.plan(self.state['incidents'], self.state['units'])
        sim_result = self.step_simulate_plan(plan_result, interval)
        
        self.state['events'].append({
            'step': steps,
            'simulation_data': sim_result
        })
        
        return self.state['events']
