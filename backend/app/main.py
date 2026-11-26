"""Punto de entrada de FastAPI. Migraciones se ejecutan por Alembic antes del servidor."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.domain import models  # noqa: F401 - registra metadata de SQLAlchemy

settings = get_settings()
if settings.app_env == 'production':
    if settings.debug:
        raise RuntimeError('DEBUG debe estar desactivado en producción')
    if (len(settings.jwt_secret) < 32 or settings.jwt_secret.startswith('dev-only')
            or any(word in settings.jwt_secret.upper() for word in ['REEMPLAZAR', 'GENERAR_', 'PLACEHOLDER', 'CAMBIAR'])):
        raise RuntimeError('JWT_SECRET inseguro: configure un valor aleatorio fuera del repositorio')
    if settings.database_password in {'change_me','CHANGE_LOCAL_POSTGRES_PASSWORD',''} or any(word in settings.database_password.upper() for word in ['GENERAR_', 'PLACEHOLDER', 'CAMBIAR']):
        raise RuntimeError('Configure una contraseña de PostgreSQL segura')
    if '*' in settings.cors_origin_list:
        raise RuntimeError('CORS_ORIGINS no puede contener comodines en producción')
app = FastAPI(title=settings.app_name, version='1.1.0', debug=settings.debug,
              docs_url=None if settings.app_env=='production' else '/docs',
              redoc_url=None if settings.app_env=='production' else '/redoc',
              openapi_url=None if settings.app_env=='production' else '/openapi.json')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True,
                   allow_methods=['GET','POST','PUT','PATCH','OPTIONS'], allow_headers=['Authorization','Content-Type'])
app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.middleware('http')
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
    if request.url.path.startswith('/api/v1/auth'):
        response.headers['Cache-Control']='no-store'
    return response