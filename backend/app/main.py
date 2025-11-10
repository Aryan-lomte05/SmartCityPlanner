from fastapi import FastAPI
from backend.app.api.v1.routes import router as v1_router
from backend.app.config import settings

app = FastAPI(
    title="SmartCity Emergency Backend",
    version="0.1",
    description="Graph–Lattice Framework for Smart City Emergency Response Optimization"
)

app.include_router(v1_router, prefix="/api/v1")
