"""Punto de entrada de FastAPI. Migraciones se ejecutan por Alembic antes del servidor."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.domain import models  # noqa: F401 - registra metadata de SQLAlchemy

settings = get_settings()
app = FastAPI(title=settings.app_name, version='1.0.0', debug=settings.debug)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True,
                   allow_methods=['GET','POST','PUT','PATCH','OPTIONS'], allow_headers=['Authorization','Content-Type'])
app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.middleware('http')
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    return response