from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.domain.routes import router as business_router
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(business_router)