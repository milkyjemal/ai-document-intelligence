from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.extractions import router as extractions_router

app = FastAPI(title="AI Document Extraction API", version="0.1.0")

app.include_router(health_router)
app.include_router(extractions_router)
