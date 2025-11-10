# backend/app/models/models.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class IncidentModel(BaseModel):
    """Incident/emergency event model"""
    id: str
    lat: float
    lon: float
    type: str
    severity: Optional[int] = 1

class UnitModel(BaseModel):
    """Emergency response unit model"""
    id: str
    lat: float
    lon: float
    type: str
    available: bool = True
    capacity: Optional[int] = 1

class PlanRequest(BaseModel):
    """Request model for planning endpoint"""
    incidents: List[IncidentModel]
    units: List[UnitModel]

class PlanResponse(BaseModel):
    """Enhanced response model with full route details"""
    assignments: Dict[str, str]
    suggestions: Dict[str, Any]
    route_details: Optional[Dict[str, Any]] = {}
    unassigned_incidents: Optional[List[str]] = []
