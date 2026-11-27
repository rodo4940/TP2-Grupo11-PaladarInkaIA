from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.domain.routes import router as business_router
from app.domain.billing_ai import router as billing_ai_router
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(business_router)
api_router.include_router(billing_ai_router)

from app.domain.reconciliation import router as reconciliation_router
api_router.include_router(reconciliation_router)

from app.domain.fiscal_demo import router as fiscal_demo_router
api_router.include_router(fiscal_demo_router)

from app.domain.trained_forecast_api import router as trained_forecast_router
api_router.include_router(trained_forecast_router)
