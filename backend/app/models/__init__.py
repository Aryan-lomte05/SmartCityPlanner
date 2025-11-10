from pydantic import BaseModel
from typing import Optional

class IncidentModel(BaseModel):
    id: str
    lat: float
    lon: float
    type: str
    severity: int = 1
    timestamp: Optional[float] = None

class UnitModel(BaseModel):
    id: str
    type: str
    lat: float
    lon: float
    available: bool = True
