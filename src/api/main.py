# src/api/main.py
# this file sets up the FastAPI application and includes the API routers


# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from .endpoints import vessel_history
from .endpoints.ports import router as ports_router
from .endpoints.vessels import router as vessels_router
from src.api.endpoints import dashboard
from .endpoints.port_areas import router as port_areas_router
from src.api.endpoints import traffic_routes
from .endpoints import dashboard_liverpool
from src.api.endpoints import area_traffic
from .endpoints import vessel_popup
from src.api.endpoints.traffic_insights import router as traffic_insights_router

app = FastAPI()

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ports_router, prefix="/api/ports", tags=["ports"])
app.include_router(vessels_router, prefix="/api/vessels", tags=["vessels"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(vessel_history.router, prefix="/api/vessel_history", tags=["vessel_history"])
app.include_router(port_areas_router, prefix="/api/port_areas", tags=["port_areas"])
app.include_router(traffic_routes.router, prefix="/api", tags=["traffic"])
app.include_router(dashboard_liverpool.router, prefix="/api/liverpool", tags=["liverpool"])
app.include_router(area_traffic.router, prefix="/api/area-traffic", tags=["liverpool-areas"])
app.include_router(vessel_popup.router, prefix="/api/vessel-popup", tags=["vessel-popup"])
app.include_router(traffic_insights_router, prefix="/api/traffic-insights", tags=["traffic-insights"])