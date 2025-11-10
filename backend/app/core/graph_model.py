# backend/app/core/graph_model.py

import json
import math
import pickle
import networkx as nx
from typing import Tuple, List, Dict, Any, Optional
from scipy.spatial import KDTree
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Calculate haversine distance between two (lat, lon) points in km."""
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    R = 6371.0
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*(math.sin(dlon/2)**2)
    return 2 * R * math.asin(math.sqrt(h))


class GraphModel:
    """
    HIGH-PERFORMANCE road network graph with KDTree spatial indexing,
    persistent caching, and optimized Dijkstra routing.
    """
    
    def __init__(self):
        self.G = nx.DiGraph()
        self._node_index = {}  # (lat, lon) -> node_id
        self._coords = {}      # node_id -> (lat, lon)
        self._kdtree: Optional[KDTree] = None
        self._coord_to_node: List[int] = []
        self._cache_dir = Path("backend/cache")
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, geojson_path: str) -> Path:
        """Generate cache filename based on source GeoJSON."""
        cache_name = Path(geojson_path).stem + "_graph.pkl"
        return self._cache_dir / cache_name

    def _add_coord_node(self, coord: Tuple[float, float]) -> int:
        """Add coordinate with 6-decimal precision deduplication."""
        key = (round(coord[0], 6), round(coord[1], 6))
        if key in self._node_index:
            return self._node_index[key]
        nid = len(self._node_index) + 1
        self._node_index[key] = nid
        self._coords[nid] = key
        self.G.add_node(nid, lat=key[0], lon=key[1])
        return nid

    def _build_kdtree(self):
        """Build KDTree for O(log n) nearest-node queries."""
        coords_list = []
        node_ids = []
        for nid in sorted(self._coords.keys()):
            lat, lon = self._coords[nid]
            coords_list.append([lat, lon])
            node_ids.append(nid)
        self._kdtree = KDTree(coords_list)
        self._coord_to_node = node_ids
        logger.info(f"[GraphModel] KDTree built with {len(node_ids)} nodes")

    def save_cache(self, cache_path: Path):
        """Persist graph to disk for instant loading."""
        cache_data = {
            'G': self.G,
            'node_index': self._node_index,
            'coords': self._coords,
            'coord_to_node': self._coord_to_node
        }
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"[GraphModel] Cache saved to {cache_path}")

    def load_cache(self, cache_path: Path) -> bool:
        """Load pre-built graph from cache."""
        if not cache_path.exists():
            return False
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            self.G = cache_data['G']
            self._node_index = cache_data['node_index']
            self._coords = cache_data['coords']
            self._coord_to_node = cache_data['coord_to_node']
            self._kdtree = KDTree([[self._coords[nid][0], self._coords[nid][1]] 
                                   for nid in self._coord_to_node])
            logger.info(f"[GraphModel] Loaded from cache: {self.G.number_of_nodes()} nodes, "
                       f"{self.G.number_of_edges()} edges")
            return True
        except Exception as e:
            logger.error(f"[GraphModel] Cache load failed: {e}")
            return False

    def load_from_geojson(self, path: str, default_speed: float = 70.0, force_rebuild: bool = False):
        """
        Load road network from GeoJSON with intelligent caching.
        🔥 EMERGENCY VEHICLE SPEED: Default 70 km/h for realistic ETAs
        
        Args:
            path: Path to GeoJSON file
            default_speed: Default speed in km/h (70 km/h for emergency vehicles)
            force_rebuild: Skip cache and rebuild from scratch
        """
        cache_path = self._cache_path(path)
        
        if not force_rebuild and self.load_cache(cache_path):
            return
        
        logger.info(f"[GraphModel] Building graph from {path} with {default_speed} km/h emergency speed...")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        features = data.get('features', [])
        edges_added = 0
        
        for feat in features:
            geom = feat.get('geometry', {})
            if geom.get('type') != 'LineString':
                continue
            
            coords = geom.get('coordinates', [])
            if len(coords) < 2:
                continue
            
            props = feat.get('properties', {})
            speed_kmph = props.get('maxspeed', default_speed)
            if isinstance(speed_kmph, str):
                try:
                    speed_kmph = float(speed_kmph)
                except:
                    speed_kmph = default_speed
            
            # Clamp speeds for realism (20-100 km/h)
            speed_kmph = min(max(speed_kmph, 20.0), 100.0)
            
            # Build directed edges between consecutive coordinates
            for i in range(len(coords) - 1):
                lon1, lat1 = coords[i]
                lon2, lat2 = coords[i + 1]
                
                u = self._add_coord_node((lat1, lon1))
                v = self._add_coord_node((lat2, lon2))
                
                dist_km = haversine_km((lat1, lon1), (lat2, lon2))
                travel_time = (dist_km / speed_kmph) * 3600.0  # seconds
                
                self.G.add_edge(u, v, weight=travel_time, distance_km=dist_km, 
                               speed_kmph=speed_kmph)
                edges_added += 1
        
        logger.info(f"[GraphModel] Loaded {self.G.number_of_nodes()} nodes, "
                   f"{edges_added} directed edges with emergency vehicle speeds")
        
        self._build_kdtree()
        self.save_cache(cache_path)

    def find_nearest_node(self, lat: float, lon: float) -> Optional[int]:
        """Ultra-fast KDTree-based nearest neighbor lookup."""
        if self._kdtree is None or not self._coord_to_node:
            return None
        distance, index = self._kdtree.query([lat, lon], k=1)
        return self._coord_to_node[index]

    def shortest_path_with_details(self, start_node: int, end_node: int) -> Dict[str, Any]:
        """
        Compute shortest path with comprehensive metrics.
        Returns: {
            'path': [(lat, lon), ...],
            'node_ids': [node1, node2, ...],
            'distance_km': float,
            'travel_time_s': float,
            'num_segments': int
        }
        """
        try:
            path_nodes = nx.shortest_path(self.G, start_node, end_node, weight='weight')
            path_coords = [self._coords[nid] for nid in path_nodes]
            
            total_distance = 0.0
            total_time = 0.0
            
            for i in range(len(path_nodes) - 1):
                u, v = path_nodes[i], path_nodes[i + 1]
                edge_data = self.G[u][v]
                total_distance += edge_data.get('distance_km', 0.0)
                total_time += edge_data.get('weight', 0.0)
            
            return {
                'path': path_coords,
                'node_ids': path_nodes,
                'distance_km': round(total_distance, 3),
                'travel_time_s': round(total_time, 2),
                'num_segments': len(path_nodes) - 1
            }
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {
                'path': [],
                'node_ids': [],
                'distance_km': 0.0,
                'travel_time_s': 0.0,
                'num_segments': 0
            }

    def update_edge_speed(self, u: int, v: int, new_speed_kmph: float):
        """Dynamically update edge speed for congestion modeling."""
        if self.G.has_edge(u, v):
            dist_km = self.G[u][v]['distance_km']
            new_travel_time = (dist_km / new_speed_kmph) * 3600.0
            self.G[u][v]['weight'] = new_travel_time
            self.G[u][v]['speed_kmph'] = new_speed_kmph

    def get_subgraph_bounds(self) -> Dict[str, float]:
        """Get bounding box for map centering."""
        if not self._coords:
            return {'min_lat': 0, 'max_lat': 0, 'min_lon': 0, 'max_lon': 0}
        
        lats = [coord[0] for coord in self._coords.values()]
        lons = [coord[1] for coord in self._coords.values()]
        
        return {
            'min_lat': min(lats),
            'max_lat': max(lats),
            'min_lon': min(lons),
            'max_lon': max(lons),
            'center_lat': sum(lats) / len(lats),
            'center_lon': sum(lons) / len(lons)
        }
