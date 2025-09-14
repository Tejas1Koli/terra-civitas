"""
Entrypoint for FastAPI app.
"""
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from .routers import health, predict, streams, alerts, models

app = FastAPI(title="Sentinel-Crime API")

# Routers
app.include_router(health.router)
app.include_router(models.router)
app.include_router(predict.router)
app.include_router(streams.router)
app.include_router(alerts.router)

# Metrics
Instrumentator().instrument(app).expose(app)
