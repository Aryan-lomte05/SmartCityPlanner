# # # # backend/app/services/planner.py

# # # from typing import List, Dict, Any, Optional
# # # from backend.app.core.graph_model import GraphModel
# # # from backend.app.core.lattice import Poset
# # # import logging

# # # logger = logging.getLogger(__name__)

# # # class Planner:
# # #     """
# # #     ULTIMATE GODMODE planner with:
# # #     - STRICT type matching
# # #     - Aggressive multi-assignment
# # #     - Priority-based allocation
# # #     """
    
# # #     def __init__(self, graph_geojson: str = "backend/data/mumbai_roads.geojson", 
# # #                  use_mapbox: bool = False):
# # #         self.graph = GraphModel()
# # #         try:
# # #             self.graph.load_from_geojson(graph_geojson, default_speed=70.0)
# # #             logger.info(f"[Planner] Graph loaded with 70 km/h emergency speed")
# # #         except Exception as e:
# # #             logger.error(f"Graph load failed: {e}")
        
# # #         elems = ['civilian', 'ambulance', 'fire', 'police', 'control']
# # #         lt = [('civilian', 'ambulance'), ('ambulance', 'fire'), 
# # #               ('fire', 'police'), ('police', 'control')]
# # #         self.poset = Poset(elems, lt)
# # #         self.use_mapbox = use_mapbox

# # #     def _get_field(self, obj: Any, name: str, default: Any = None) -> Any:
# # #         """Universal field accessor for both Pydantic models and dicts."""
# # #         if hasattr(obj, name):
# # #             return getattr(obj, name)
# # #         if isinstance(obj, dict):
# # #             return obj.get(name, default)
# # #         return default

# # #     def _unit_priority(self, unit_type: str) -> int:
# # #         """Higher priority = lower number (control=0 is highest)."""
# # #         order = {'control': 0, 'police': 1, 'fire': 2, 'ambulance': 3, 'civilian': 4}
# # #         return order.get(unit_type, 99)

# # #     def _incident_priority_score(self, incident: Any) -> float:
# # #         """Calculate incident urgency score (higher = more urgent)."""
# # #         severity = self._get_field(incident, 'severity', 1)
# # #         incident_type = self._get_field(incident, 'type', '').lower()
        
# # #         type_weight = {
# # #             'fire': 3.0,
# # #             'medical': 2.5,
# # #             'accident': 2.0,
# # #             'crime': 1.5,
# # #             'other': 1.0
# # #         }
        
# # #         weight = type_weight.get(incident_type, 1.0)
# # #         return severity * weight

# # #     def _get_preferred_unit_type(self, incident_type: str) -> str:
# # #         """Map incident type to preferred unit type."""
# # #         mapping = {
# # #             'fire': 'fire',
# # #             'medical': 'ambulance',
# # #             'accident': 'ambulance',
# # #             'crime': 'police',
# # #             'other': 'police'
# # #         }
# # #         return mapping.get(incident_type.lower(), 'ambulance')

# # #     def plan(self, incidents: List[Any], units: List[Any]) -> Dict[str, Any]:
# # #         """
# # #         ULTIMATE GODMODE++ planning with:
# # #         1. STRICT type matching (ambulance->medical, fire->fire, police->crime)
# # #         2. Unlimited multi-tasking (ignore capacity completely)
# # #         3. Priority-based smart allocation
# # #         """
# # #         assignments = {}
# # #         route_details = {}
# # #         unassigned_incidents = []
        
# # #         available_units = [u for u in units if self._get_field(u, 'available', True)]
        
# # #         if not available_units:
# # #             logger.warning("No available units")
# # #             return {
# # #                 'assignments': {},
# # #                 'suggestions': {'warning': 'No available units'},
# # #                 'route_details': {},
# # #                 'unassigned_incidents': [self._get_field(i, 'id') for i in incidents]
# # #             }
        
# # #         # Sort incidents by priority (highest first)
# # #         sorted_incidents = sorted(incidents, 
# # #                                  key=lambda i: self._incident_priority_score(i), 
# # #                                  reverse=True)
        
# # #         # PHASE 1: STRICT type-matching assignment
# # #         for incident in sorted_incidents:
# # #             inc_id = self._get_field(incident, 'id')
# # #             inc_lat = self._get_field(incident, 'lat')
# # #             inc_lon = self._get_field(incident, 'lon')
# # #             inc_type = self._get_field(incident, 'type', 'other')
            
# # #             inc_node = self.graph.find_nearest_node(inc_lat, inc_lon)
# # #             if inc_node is None:
# # #                 logger.warning(f"No graph node for incident {inc_id}")
# # #                 unassigned_incidents.append(inc_id)
# # #                 continue
            
# # #             preferred_unit_type = self._get_preferred_unit_type(inc_type)
            
# # #             # Filter units by STRICT type match
# # #             matching_units = [u for u in available_units 
# # #                             if self._get_field(u, 'type') == preferred_unit_type]
            
# # #             best_unit = None
# # #             best_eta = float('inf')
# # #             best_route = None
            
# # #             # Find closest matching unit (ignore capacity)
# # #             for unit in matching_units:
# # #                 unit_id = self._get_field(unit, 'id')
# # #                 unit_lat = self._get_field(unit, 'lat')
# # #                 unit_lon = self._get_field(unit, 'lon')
                
# # #                 unit_node = self.graph.find_nearest_node(unit_lat, unit_lon)
# # #                 if unit_node is None:
# # #                     continue
                
# # #                 route = self.graph.shortest_path_with_details(unit_node, inc_node)
                
# # #                 if route['path'] and route['travel_time_s'] < best_eta:
# # #                     best_eta = route['travel_time_s']
# # #                     best_unit = unit
# # #                     best_route = route
            
# # #             if best_unit:
# # #                 unit_id = self._get_field(best_unit, 'id')
# # #                 assignments[inc_id] = unit_id
# # #                 route_details[inc_id] = {
# # #                     'unit_id': unit_id,
# # #                     'unit_type': self._get_field(best_unit, 'type'),
# # #                     'distance_km': best_route['distance_km'],
# # #                     'eta_seconds': best_route['travel_time_s'],
# # #                     'eta_minutes': round(best_route['travel_time_s'] / 60, 1),
# # #                     'path': best_route['path'],
# # #                     'num_segments': best_route['num_segments'],
# # #                     'type_match': '✓'
# # #                 }
# # #                 logger.info(f"✓ Assigned {unit_id} ({preferred_unit_type}) to {inc_id} ({inc_type})")
# # #             else:
# # #                 unassigned_incidents.append(inc_id)
# # #                 logger.warning(f"No {preferred_unit_type} unit available for {inc_id}")
        
# # #         # PHASE 2: Fallback assignment for unassigned (relaxed type matching)
# # #         if unassigned_incidents:
# # #             logger.info(f"🔄 Fallback assignment for {len(unassigned_incidents)} incidents")
            
# # #             for inc_id in list(unassigned_incidents):
# # #                 incident = next((i for i in sorted_incidents 
# # #                                if self._get_field(i, 'id') == inc_id), None)
# # #                 if not incident:
# # #                     continue
                
# # #                 inc_lat = self._get_field(incident, 'lat')
# # #                 inc_lon = self._get_field(incident, 'lon')
# # #                 inc_type = self._get_field(incident, 'type', 'other')
# # #                 inc_node = self.graph.find_nearest_node(inc_lat, inc_lon)
                
# # #                 if inc_node is None:
# # #                     continue
                
# # #                 # Try ANY unit (relaxed matching)
# # #                 best_unit = None
# # #                 best_eta = float('inf')
# # #                 best_route = None
                
# # #                 for unit in available_units:
# # #                     unit_id = self._get_field(unit, 'id')
# # #                     unit_lat = self._get_field(unit, 'lat')
# # #                     unit_lon = self._get_field(unit, 'lon')
# # #                     unit_type = self._get_field(unit, 'type')
                    
# # #                     unit_node = self.graph.find_nearest_node(unit_lat, unit_lon)
# # #                     if unit_node is None:
# # #                         continue
                    
# # #                     route = self.graph.shortest_path_with_details(unit_node, inc_node)
# # #                     if route['path'] and route['travel_time_s'] < best_eta:
# # #                         best_eta = route['travel_time_s']
# # #                         best_unit = unit
# # #                         best_route = route
                
# # #                 if best_unit:
# # #                     unit_id = self._get_field(best_unit, 'id')
# # #                     unit_type = self._get_field(best_unit, 'type')
# # #                     assignments[inc_id] = unit_id
# # #                     route_details[inc_id] = {
# # #                         'unit_id': unit_id,
# # #                         'unit_type': unit_type,
# # #                         'distance_km': best_route['distance_km'],
# # #                         'eta_seconds': best_route['travel_time_s'],
# # #                         'eta_minutes': round(best_route['travel_time_s'] / 60, 1),
# # #                         'path': best_route['path'],
# # #                         'num_segments': best_route['num_segments'],
# # #                         'type_match': '⚠ Fallback'
# # #                     }
# # #                     unassigned_incidents.remove(inc_id)
# # #                     logger.info(f"⚠ Fallback: {unit_id} ({unit_type}) assigned to {inc_id} ({inc_type})")
        
# # #         # Generate suggestions
# # #         suggestions = {
# # #             'total_incidents': len(incidents),
# # #             'assigned': len(assignments),
# # #             'unassigned': len(unassigned_incidents),
# # #             'unassigned_ids': unassigned_incidents,
# # #             'avg_eta_seconds': round(sum(r['eta_seconds'] for r in route_details.values()) / max(1, len(route_details)), 2),
# # #             'max_eta_seconds': max((r['eta_seconds'] for r in route_details.values()), default=0),
# # #             'unit_utilization': f"{len(set(assignments.values()))}/{len(available_units)}",
# # #             'type_matches': sum(1 for r in route_details.values() if r.get('type_match') == '✓'),
# # #             'fallback_matches': sum(1 for r in route_details.values() if '⚠' in str(r.get('type_match', '')))
# # #         }
        
# # #         if unassigned_incidents:
# # #             suggestions['alert'] = f"⚠️ {len(unassigned_incidents)} incidents need more units"
        
# # #         return {
# # #             'assignments': assignments,
# # #             'suggestions': suggestions,
# # #             'route_details': route_details,
# # #             'unassigned_incidents': unassigned_incidents
# # #         }
# # # backend/app/services/planner.py

# # from typing import List, Dict, Any, Optional
# # from backend.app.core.graph_model import GraphModel
# # from backend.app.core.lattice import Poset
# # import logging

# # logger = logging.getLogger(__name__)

# # class Planner:
# #     """
# #     ULTIMATE GODMODE planner with strict type matching and multi-assignment.
# #     """
    
# #     def __init__(self, graph_geojson: str = "backend/data/mumbai_roads.geojson", 
# #                  use_mapbox: bool = False):
# #         self.graph = GraphModel()
# #         try:
# #             self.graph.load_from_geojson(graph_geojson, default_speed=70.0)
# #             logger.info(f"[Planner] Graph loaded with 70 km/h emergency speed")
# #         except Exception as e:
# #             logger.error(f"Graph load failed: {e}")
        
# #         elems = ['civilian', 'ambulance', 'fire', 'police', 'control']
# #         lt = [('civilian', 'ambulance'), ('ambulance', 'fire'), 
# #               ('fire', 'police'), ('police', 'control')]
# #         self.poset = Poset(elems, lt)
# #         self.use_mapbox = use_mapbox

# #     def _get_field(self, obj: Any, name: str, default: Any = None) -> Any:
# #         """Universal field accessor for both Pydantic models and dicts."""
# #         if hasattr(obj, name):
# #             return getattr(obj, name)
# #         if isinstance(obj, dict):
# #             return obj.get(name, default)
# #         return default

# #     def _unit_priority(self, unit_type: str) -> int:
# #         """Higher priority = lower number."""
# #         order = {'control': 0, 'police': 1, 'fire': 2, 'ambulance': 3, 'civilian': 4}
# #         return order.get(unit_type, 99)

# #     def _incident_priority_score(self, incident: Any) -> float:
# #         """Calculate incident urgency score."""
# #         severity = self._get_field(incident, 'severity', 1)
# #         incident_type = self._get_field(incident, 'type', '').lower()
        
# #         type_weight = {
# #             'fire': 3.0,
# #             'medical': 2.5,
# #             'accident': 2.0,
# #             'crime': 1.5,
# #             'other': 1.0
# #         }
        
# #         weight = type_weight.get(incident_type, 1.0)
# #         return severity * weight

# #     def _get_preferred_unit_type(self, incident_type: str) -> str:
# #         """Map incident type to preferred unit type."""
# #         mapping = {
# #             'fire': 'fire',
# #             'medical': 'ambulance',
# #             'accident': 'ambulance',
# #             'crime': 'police',
# #             'other': 'police'
# #         }
# #         return mapping.get(incident_type.lower(), 'ambulance')

# #     def plan(self, incidents: List[Any], units: List[Any]) -> Dict[str, Any]:
# #         """
# #         ULTIMATE GODMODE planning with strict type matching and unlimited multi-assignment.
# #         """
# #         assignments = {}
# #         route_details = {}
# #         unassigned_incidents = []
        
# #         available_units = [u for u in units if self._get_field(u, 'available', True)]
        
# #         if not available_units:
# #             logger.warning("No available units")
# #             return {
# #                 'assignments': {},
# #                 'suggestions': {'warning': 'No available units'},
# #                 'route_details': {},
# #                 'unassigned_incidents': [self._get_field(i, 'id') for i in incidents]
# #             }
        
# #         sorted_incidents = sorted(incidents, 
# #                                  key=lambda i: self._incident_priority_score(i), 
# #                                  reverse=True)
        
# #         for incident in sorted_incidents:
# #             inc_id = self._get_field(incident, 'id')
# #             inc_lat = self._get_field(incident, 'lat')
# #             inc_lon = self._get_field(incident, 'lon')
# #             inc_type = self._get_field(incident, 'type', 'other')
            
# #             inc_node = self.graph.find_nearest_node(inc_lat, inc_lon)
# #             if inc_node is None:
# #                 logger.warning(f"No graph node for incident {inc_id}")
# #                 unassigned_incidents.append(inc_id)
# #                 continue
            
# #             preferred_unit_type = self._get_preferred_unit_type(inc_type)
            
# #             matching_units = [u for u in available_units 
# #                             if self._get_field(u, 'type') == preferred_unit_type]
            
# #             best_unit = None
# #             best_eta = float('inf')
# #             best_route = None
            
# #             for unit in matching_units:
# #                 unit_id = self._get_field(unit, 'id')
# #                 unit_lat = self._get_field(unit, 'lat')
# #                 unit_lon = self._get_field(unit, 'lon')
                
# #                 unit_node = self.graph.find_nearest_node(unit_lat, unit_lon)
# #                 if unit_node is None:
# #                     continue
                
# #                 route = self.graph.shortest_path_with_details(unit_node, inc_node)
                
# #                 if route['path'] and route['travel_time_s'] < best_eta:
# #                     best_eta = route['travel_time_s']
# #                     best_unit = unit
# #                     best_route = route
            
# #             if best_unit:
# #                 unit_id = self._get_field(best_unit, 'id')
# #                 assignments[inc_id] = unit_id
# #                 route_details[inc_id] = {
# #                     'unit_id': unit_id,
# #                     'unit_type': self._get_field(best_unit, 'type'),
# #                     'distance_km': best_route['distance_km'],
# #                     'eta_seconds': best_route['travel_time_s'],
# #                     'eta_minutes': round(best_route['travel_time_s'] / 60, 1),
# #                     'path': best_route['path'],
# #                     'num_segments': best_route['num_segments'],
# #                     'type_match': '✓'
# #                 }
# #                 logger.info(f"✓ Assigned {unit_id} ({preferred_unit_type}) to {inc_id} ({inc_type})")
# #             else:
# #                 unassigned_incidents.append(inc_id)
# #                 logger.warning(f"No {preferred_unit_type} unit available for {inc_id}")
        
# #         if unassigned_incidents:
# #             logger.info(f"🔄 Fallback assignment for {len(unassigned_incidents)} incidents")
            
# #             # 🔥 FIX: Create a snapshot of unassigned list to avoid modification during iteration
# #             unassigned_snapshot = unassigned_incidents.copy()
            
# #             for inc_id in unassigned_snapshot:
# #                 incident = next((i for i in sorted_incidents 
# #                                if self._get_field(i, 'id') == inc_id), None)
# #                 if not incident:
# #                     continue
                
# #                 inc_lat = self._get_field(incident, 'lat')
# #                 inc_lon = self._get_field(incident, 'lon')
# #                 inc_type = self._get_field(incident, 'type', 'other')
# #                 inc_node = self.graph.find_nearest_node(inc_lat, inc_lon)
                
# #                 if inc_node is None:
# #                     logger.warning(f"No graph node for fallback incident {inc_id}")
# #                     continue
                
# #                 best_unit = None
# #                 best_eta = float('inf')
# #                 best_route = None
                
# #                 # Try ANY unit (relaxed matching)
# #                 for unit in available_units:
# #                     unit_id = self._get_field(unit, 'id')
# #                     unit_lat = self._get_field(unit, 'lat')
# #                     unit_lon = self._get_field(unit, 'lon')
# #                     unit_type = self._get_field(unit, 'type')
                    
# #                     unit_node = self.graph.find_nearest_node(unit_lat, unit_lon)
# #                     if unit_node is None:
# #                         continue
                    
# #                     route = self.graph.shortest_path_with_details(unit_node, inc_node)
# #                     if route['path'] and route['travel_time_s'] < best_eta:
# #                         best_eta = route['travel_time_s']
# #                         best_unit = unit
# #                         best_route = route
                
# #                 if best_unit:
# #                     unit_id = self._get_field(best_unit, 'id')
# #                     unit_type = self._get_field(best_unit, 'type')
# #                     assignments[inc_id] = unit_id
# #                     route_details[inc_id] = {
# #                         'unit_id': unit_id,
# #                         'unit_type': unit_type,
# #                         'distance_km': best_route['distance_km'],
# #                         'eta_seconds': best_route['travel_time_s'],
# #                         'eta_minutes': round(best_route['travel_time_s'] / 60, 1),
# #                         'path': best_route['path'],
# #                         'num_segments': best_route['num_segments'],
# #                         'type_match': '⚠ Fallback'
# #                     }
# #                     unassigned_incidents.remove(inc_id)
# #                     logger.info(f"⚠ Fallback: {unit_id} ({unit_type}) assigned to {inc_id} ({inc_type})")
# #                 else:
# #                     logger.error(f"❌ Could not assign any unit to {inc_id} - no path found")
        
# #         suggestions = {
# #             'total_incidents': len(incidents),
# #             'assigned': len(assignments),
# #             'unassigned': len(unassigned_incidents),
# #             'unassigned_ids': unassigned_incidents,
# #             'avg_eta_seconds': round(sum(r['eta_seconds'] for r in route_details.values()) / max(1, len(route_details)), 2),
# #             'max_eta_seconds': max((r['eta_seconds'] for r in route_details.values()), default=0),
# #             'unit_utilization': f"{len(set(assignments.values()))}/{len(available_units)}",
# #             'type_matches': sum(1 for r in route_details.values() if r.get('type_match') == '✓'),
# #             'fallback_matches': sum(1 for r in route_details.values() if '⚠' in str(r.get('type_match', '')))
# #         }
        
# #         if unassigned_incidents:
# #             suggestions['alert'] = f"⚠️ {len(unassigned_incidents)} incidents need more units"
        
# #         return {
# #             'assignments': assignments,
# #             'suggestions': suggestions,
# #             'route_details': route_details,
# #             'unassigned_incidents': unassigned_incidents
# #         }
# # backend/app/services/planner.py

# from typing import List, Dict, Any, Optional
# from backend.app.core.graph_model import GraphModel
# from backend.app.core.lattice import Poset
# import logging

# logger = logging.getLogger(__name__)

# class Planner:
#     """
#     ULTIMATE GODMODE planner with strict type matching and proper unit tracking.
#     """
    
#     def __init__(self, graph_geojson: str = "backend/data/mumbai_roads.geojson", 
#                  use_mapbox: bool = False):
#         self.graph = GraphModel()
#         try:
#             self.graph.load_from_geojson(graph_geojson, default_speed=70.0)
#             logger.info(f"[Planner] Graph loaded with 70 km/h emergency speed")
#         except Exception as e:
#             logger.error(f"Graph load failed: {e}")
        
#         elems = ['civilian', 'ambulance', 'fire', 'police', 'control']
#         lt = [('civilian', 'ambulance'), ('ambulance', 'fire'), 
#               ('fire', 'police'), ('police', 'control')]
#         self.poset = Poset(elems, lt)
#         self.use_mapbox = use_mapbox

#     def _get_field(self, obj: Any, name: str, default: Any = None) -> Any:
#         """Universal field accessor for both Pydantic models and dicts."""
#         if hasattr(obj, name):
#             return getattr(obj, name)
#         if isinstance(obj, dict):
#             return obj.get(name, default)
#         return default

#     def _unit_priority(self, unit_type: str) -> int:
#         """Higher priority = lower number."""
#         order = {'control': 0, 'police': 1, 'fire': 2, 'ambulance': 3, 'civilian': 4}
#         return order.get(unit_type, 99)

#     def _incident_priority_score(self, incident: Any) -> float:
#         """Calculate incident urgency score."""
#         severity = self._get_field(incident, 'severity', 1)
#         incident_type = self._get_field(incident, 'type', '').lower()
        
#         type_weight = {
#             'fire': 3.0,
#             'medical': 2.5,
#             'accident': 2.0,
#             'crime': 1.5,
#             'other': 1.0
#         }
        
#         weight = type_weight.get(incident_type, 1.0)
#         return severity * weight

#     def _get_preferred_unit_type(self, incident_type: str) -> str:
#         """Map incident type to preferred unit type."""
#         mapping = {
#             'fire': 'fire',
#             'medical': 'ambulance',
#             'accident': 'ambulance',
#             'crime': 'police',
#             'other': 'police'
#         }
#         return mapping.get(incident_type.lower(), 'ambulance')

#     def plan(self, incidents: List[Any], units: List[Any]) -> Dict[str, Any]:
#         """
#         🔥 FIXED: Track which units are already assigned to prevent double-assignment.
#         """
#         assignments = {}
#         route_details = {}
#         unassigned_incidents = []
#         assigned_units = set()  # 🔥 NEW: Track assigned units
        
#         available_units = [u for u in units if self._get_field(u, 'available', True)]
        
#         if not available_units:
#             logger.warning("No available units")
#             return {
#                 'assignments': {},
#                 'suggestions': {'warning': 'No available units'},
#                 'route_details': {},
#                 'unassigned_incidents': [self._get_field(i, 'id') for i in incidents]
#             }
        
#         sorted_incidents = sorted(incidents, 
#                                  key=lambda i: self._incident_priority_score(i), 
#                                  reverse=True)
        
#         # PHASE 1: STRICT type matching with unit tracking
#         for incident in sorted_incidents:
#             inc_id = self._get_field(incident, 'id')
#             inc_lat = self._get_field(incident, 'lat')
#             inc_lon = self._get_field(incident, 'lon')
#             inc_type = self._get_field(incident, 'type', 'other')
            
#             inc_node = self.graph.find_nearest_node(inc_lat, inc_lon)
#             if inc_node is None:
#                 logger.warning(f"No graph node for incident {inc_id}")
#                 unassigned_incidents.append(inc_id)
#                 continue
            
#             preferred_unit_type = self._get_preferred_unit_type(inc_type)
            
#             # 🔥 FIX: Filter out already-assigned units
#             matching_units = [u for u in available_units 
#                             if self._get_field(u, 'type') == preferred_unit_type
#                             and self._get_field(u, 'id') not in assigned_units]
            
#             best_unit = None
#             best_eta = float('inf')
#             best_route = None
            
#             for unit in matching_units:
#                 unit_id = self._get_field(unit, 'id')
#                 unit_lat = self._get_field(unit, 'lat')
#                 unit_lon = self._get_field(unit, 'lon')
                
#                 unit_node = self.graph.find_nearest_node(unit_lat, unit_lon)
#                 if unit_node is None:
#                     continue
                
#                 route = self.graph.shortest_path_with_details(unit_node, inc_node)
                
#                 if route['path'] and route['travel_time_s'] < best_eta:
#                     best_eta = route['travel_time_s']
#                     best_unit = unit
#                     best_route = route
            
#             if best_unit:
#                 unit_id = self._get_field(best_unit, 'id')
#                 assignments[inc_id] = unit_id
#                 assigned_units.add(unit_id)  # 🔥 MARK AS ASSIGNED
#                 route_details[inc_id] = {
#                     'unit_id': unit_id,
#                     'unit_type': self._get_field(best_unit, 'type'),
#                     'distance_km': best_route['distance_km'],
#                     'eta_seconds': best_route['travel_time_s'],
#                     'eta_minutes': round(best_route['travel_time_s'] / 60, 1),
#                     'path': best_route['path'],
#                     'num_segments': best_route['num_segments'],
#                     'type_match': '✓'
#                 }
#                 logger.info(f"✓ Assigned {unit_id} ({preferred_unit_type}) to {inc_id} ({inc_type})")
#             else:
#                 unassigned_incidents.append(inc_id)
#                 logger.warning(f"No {preferred_unit_type} unit available for {inc_id}")
        
#         # PHASE 2: Fallback assignment for unassigned (relaxed matching)
#         if unassigned_incidents:
#             logger.info(f"🔄 Fallback assignment for {len(unassigned_incidents)} incidents")
            
#             unassigned_snapshot = unassigned_incidents.copy()
            
#             for inc_id in unassigned_snapshot:
#                 incident = next((i for i in sorted_incidents 
#                                if self._get_field(i, 'id') == inc_id), None)
#                 if not incident:
#                     continue
                
#                 inc_lat = self._get_field(incident, 'lat')
#                 inc_lon = self._get_field(incident, 'lon')
#                 inc_type = self._get_field(incident, 'type', 'other')
#                 inc_node = self.graph.find_nearest_node(inc_lat, inc_lon)
                
#                 if inc_node is None:
#                     logger.warning(f"No graph node for fallback incident {inc_id}")
#                     continue
                
#                 best_unit = None
#                 best_eta = float('inf')
#                 best_route = None
                
#                 # 🔥 FIX: Try UNASSIGNED units only (no double-assignment)
#                 unassigned_units = [u for u in available_units 
#                                    if self._get_field(u, 'id') not in assigned_units]
                
#                 for unit in unassigned_units:
#                     unit_id = self._get_field(unit, 'id')
#                     unit_lat = self._get_field(unit, 'lat')
#                     unit_lon = self._get_field(unit, 'lon')
#                     unit_type = self._get_field(unit, 'type')
                    
#                     unit_node = self.graph.find_nearest_node(unit_lat, unit_lon)
#                     if unit_node is None:
#                         continue
                    
#                     route = self.graph.shortest_path_with_details(unit_node, inc_node)
#                     if route['path'] and route['travel_time_s'] < best_eta:
#                         best_eta = route['travel_time_s']
#                         best_unit = unit
#                         best_route = route
                
#                 if best_unit:
#                     unit_id = self._get_field(best_unit, 'id')
#                     unit_type = self._get_field(best_unit, 'type')
#                     assignments[inc_id] = unit_id
#                     assigned_units.add(unit_id)  # 🔥 MARK AS ASSIGNED
#                     route_details[inc_id] = {
#                         'unit_id': unit_id,
#                         'unit_type': unit_type,
#                         'distance_km': best_route['distance_km'],
#                         'eta_seconds': best_route['travel_time_s'],
#                         'eta_minutes': round(best_route['travel_time_s'] / 60, 1),
#                         'path': best_route['path'],
#                         'num_segments': best_route['num_segments'],
#                         'type_match': '⚠ Fallback'
#                     }
#                     unassigned_incidents.remove(inc_id)
#                     logger.info(f"⚠ Fallback: {unit_id} ({unit_type}) assigned to {inc_id} ({inc_type})")
#                 else:
#                     logger.error(f"❌ Could not assign any unit to {inc_id} - all units busy")
        
#         suggestions = {
#             'total_incidents': len(incidents),
#             'assigned': len(assignments),
#             'unassigned': len(unassigned_incidents),
#             'unassigned_ids': unassigned_incidents,
#             'avg_eta_seconds': round(sum(r['eta_seconds'] for r in route_details.values()) / max(1, len(route_details)), 2),
#             'max_eta_seconds': max((r['eta_seconds'] for r in route_details.values()), default=0),
#             'unit_utilization': f"{len(assigned_units)}/{len(available_units)}",
#             'type_matches': sum(1 for r in route_details.values() if r.get('type_match') == '✓'),
#             'fallback_matches': sum(1 for r in route_details.values() if '⚠' in str(r.get('type_match', '')))
#         }
        
#         if unassigned_incidents:
#             suggestions['alert'] = f"⚠️ {len(unassigned_incidents)} incidents need more units"
        
#         return {
#             'assignments': assignments,
#             'suggestions': suggestions,
#             'route_details': route_details,
#             'unassigned_incidents': unassigned_incidents
#         }
# backend/app/services/planner.py

from typing import List, Dict, Any, Optional
from backend.app.core.graph_model import GraphModel
from backend.app.core.lattice import Poset
import logging

logger = logging.getLogger(__name__)

class Planner:
    """
    ULTIMATE GODMODE planner with enhanced debugging.
    """
    
    def __init__(self, graph_geojson: str = "backend/data/mumbai_roads.geojson", 
                 use_mapbox: bool = False):
        self.graph = GraphModel()
        try:
            self.graph.load_from_geojson(graph_geojson, default_speed=70.0)
            logger.info(f"[Planner] Graph loaded with 70 km/h emergency speed")
        except Exception as e:
            logger.error(f"Graph load failed: {e}")
        
        elems = ['civilian', 'ambulance', 'fire', 'police', 'control']
        lt = [('civilian', 'ambulance'), ('ambulance', 'fire'), 
              ('fire', 'police'), ('police', 'control')]
        self.poset = Poset(elems, lt)
        self.use_mapbox = use_mapbox

    def _get_field(self, obj: Any, name: str, default: Any = None) -> Any:
        """Universal field accessor for both Pydantic models and dicts."""
        if hasattr(obj, name):
            return getattr(obj, name)
        if isinstance(obj, dict):
            return obj.get(name, default)
        return default

    def _unit_priority(self, unit_type: str) -> int:
        """Higher priority = lower number."""
        order = {'control': 0, 'police': 1, 'fire': 2, 'ambulance': 3, 'civilian': 4}
        return order.get(unit_type, 99)

    def _incident_priority_score(self, incident: Any) -> float:
        """Calculate incident urgency score."""
        severity = self._get_field(incident, 'severity', 1)
        incident_type = self._get_field(incident, 'type', '').lower()
        
        type_weight = {
            'fire': 3.0,
            'medical': 2.5,
            'accident': 2.0,
            'crime': 1.5,
            'other': 1.0
        }
        
        weight = type_weight.get(incident_type, 1.0)
        return severity * weight

    def _get_preferred_unit_type(self, incident_type: str) -> str:
        """Map incident type to preferred unit type."""
        mapping = {
            'fire': 'fire',
            'medical': 'ambulance',
            'accident': 'ambulance',
            'crime': 'police',
            'other': 'police'
        }
        return mapping.get(incident_type.lower(), 'ambulance')

    def plan(self, incidents: List[Any], units: List[Any]) -> Dict[str, Any]:
        """
        🔥 FIXED with enhanced debug logging to find type matching bug.
        """
        assignments = {}
        route_details = {}
        unassigned_incidents = []
        assigned_units = set()
        
        available_units = [u for u in units if self._get_field(u, 'available', True)]
        
        # 🔥 DEBUG: Log all units with their ACTUAL types
        logger.info(f"[Planner] === DEBUG: ALL UNITS ===")
        for u in available_units:
            unit_id = self._get_field(u, 'id')
            unit_type = self._get_field(u, 'type')
            logger.info(f"[Planner] Unit {unit_id}: type='{unit_type}' (repr={repr(unit_type)})")
        
        if not available_units:
            logger.warning("No available units")
            return {
                'assignments': {},
                'suggestions': {'warning': 'No available units'},
                'route_details': {},
                'unassigned_incidents': [self._get_field(i, 'id') for i in incidents]
            }
        
        sorted_incidents = sorted(incidents, 
                                 key=lambda i: self._incident_priority_score(i), 
                                 reverse=True)
        
        for incident in sorted_incidents:
            inc_id = self._get_field(incident, 'id')
            inc_lat = self._get_field(incident, 'lat')
            inc_lon = self._get_field(incident, 'lon')
            inc_type = self._get_field(incident, 'type', 'other')
            
            inc_node = self.graph.find_nearest_node(inc_lat, inc_lon)
            if inc_node is None:
                logger.warning(f"No graph node for incident {inc_id}")
                unassigned_incidents.append(inc_id)
                continue
            
            preferred_unit_type = self._get_preferred_unit_type(inc_type)
            
            # 🔥 DEBUG: Show what we're looking for
            logger.info(f"[Planner] Incident {inc_id} (type='{inc_type}') needs unit_type='{preferred_unit_type}'")
            logger.info(f"[Planner] Already assigned units: {assigned_units}")
            
            # Filter matching units with debug
            matching_units = []
            for u in available_units:
                unit_id = self._get_field(u, 'id')
                unit_type = self._get_field(u, 'type')
                
                # 🔥 DEBUG: Show comparison
                is_match = (unit_type == preferred_unit_type)
                is_available = (unit_id not in assigned_units)
                logger.info(f"[Planner]   {unit_id}: type='{unit_type}' == '{preferred_unit_type}'? {is_match}, available? {is_available}")
                
                if is_match and is_available:
                    matching_units.append(u)
            
            logger.info(f"[Planner] Found {len(matching_units)} matching units for {inc_id}")
            
            best_unit = None
            best_eta = float('inf')
            best_route = None
            
            for unit in matching_units:
                unit_id = self._get_field(unit, 'id')
                unit_lat = self._get_field(unit, 'lat')
                unit_lon = self._get_field(unit, 'lon')
                
                unit_node = self.graph.find_nearest_node(unit_lat, unit_lon)
                if unit_node is None:
                    continue
                
                route = self.graph.shortest_path_with_details(unit_node, inc_node)
                
                if route['path'] and route['travel_time_s'] < best_eta:
                    best_eta = route['travel_time_s']
                    best_unit = unit
                    best_route = route
            
            if best_unit:
                unit_id = self._get_field(best_unit, 'id')
                assignments[inc_id] = unit_id
                assigned_units.add(unit_id)
                route_details[inc_id] = {
                    'unit_id': unit_id,
                    'unit_type': self._get_field(best_unit, 'type'),
                    'distance_km': best_route['distance_km'],
                    'eta_seconds': best_route['travel_time_s'],
                    'eta_minutes': round(best_route['travel_time_s'] / 60, 1),
                    'path': best_route['path'],
                    'num_segments': best_route['num_segments'],
                    'type_match': '✓'
                }
                logger.info(f"✓ Assigned {unit_id} ({preferred_unit_type}) to {inc_id} ({inc_type})")
            else:
                unassigned_incidents.append(inc_id)
                logger.warning(f"No {preferred_unit_type} unit available for {inc_id}")
        
        if unassigned_incidents:
            logger.info(f"🔄 Fallback assignment for {len(unassigned_incidents)} incidents")
            
            unassigned_snapshot = unassigned_incidents.copy()
            
            for inc_id in unassigned_snapshot:
                incident = next((i for i in sorted_incidents 
                               if self._get_field(i, 'id') == inc_id), None)
                if not incident:
                    continue
                
                inc_lat = self._get_field(incident, 'lat')
                inc_lon = self._get_field(incident, 'lon')
                inc_type = self._get_field(incident, 'type', 'other')
                inc_node = self.graph.find_nearest_node(inc_lat, inc_lon)
                
                if inc_node is None:
                    logger.warning(f"No graph node for fallback incident {inc_id}")
                    continue
                
                best_unit = None
                best_eta = float('inf')
                best_route = None
                
                unassigned_units = [u for u in available_units 
                                   if self._get_field(u, 'id') not in assigned_units]
                
                logger.info(f"[Planner] Fallback: {len(unassigned_units)} unassigned units left")
                
                for unit in unassigned_units:
                    unit_id = self._get_field(unit, 'id')
                    unit_lat = self._get_field(unit, 'lat')
                    unit_lon = self._get_field(unit, 'lon')
                    unit_type = self._get_field(unit, 'type')
                    
                    unit_node = self.graph.find_nearest_node(unit_lat, unit_lon)
                    if unit_node is None:
                        continue
                    
                    route = self.graph.shortest_path_with_details(unit_node, inc_node)
                    if route['path'] and route['travel_time_s'] < best_eta:
                        best_eta = route['travel_time_s']
                        best_unit = unit
                        best_route = route
                
                if best_unit:
                    unit_id = self._get_field(best_unit, 'id')
                    unit_type = self._get_field(best_unit, 'type')
                    assignments[inc_id] = unit_id
                    assigned_units.add(unit_id)
                    route_details[inc_id] = {
                        'unit_id': unit_id,
                        'unit_type': unit_type,
                        'distance_km': best_route['distance_km'],
                        'eta_seconds': best_route['travel_time_s'],
                        'eta_minutes': round(best_route['travel_time_s'] / 60, 1),
                        'path': best_route['path'],
                        'num_segments': best_route['num_segments'],
                        'type_match': '⚠ Fallback'
                    }
                    unassigned_incidents.remove(inc_id)
                    logger.info(f"⚠ Fallback: {unit_id} ({unit_type}) assigned to {inc_id} ({inc_type})")
                else:
                    logger.error(f"❌ Could not assign any unit to {inc_id} - all units busy")
        
        suggestions = {
            'total_incidents': len(incidents),
            'assigned': len(assignments),
            'unassigned': len(unassigned_incidents),
            'unassigned_ids': unassigned_incidents,
            'avg_eta_seconds': round(sum(r['eta_seconds'] for r in route_details.values()) / max(1, len(route_details)), 2),
            'max_eta_seconds': max((r['eta_seconds'] for r in route_details.values()), default=0),
            'unit_utilization': f"{len(assigned_units)}/{len(available_units)}",
            'type_matches': sum(1 for r in route_details.values() if r.get('type_match') == '✓'),
            'fallback_matches': sum(1 for r in route_details.values() if '⚠' in str(r.get('type_match', '')))
        }
        
        if unassigned_incidents:
            suggestions['alert'] = f"⚠️ {len(unassigned_incidents)} incidents need more units"
        
        return {
            'assignments': assignments,
            'suggestions': suggestions,
            'route_details': route_details,
            'unassigned_incidents': unassigned_incidents
        }
