"""Autenticación JWT y autorización de roles, validada en servidor."""
from datetime import datetime, timedelta, timezone
from typing import Callable
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import get_db
from app.domain.models import User

_hasher = PasswordHasher()
_bearer = HTTPBearer(auto_error=False)

def hash_password(value: str) -> str:
    return _hasher.hash(value)

def verify_password(value: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, value)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False

def issue_token(user: User) -> str:
    s = get_settings()
    secret = s.jwt_secret
    if not secret or (s.app_env == 'production' and (len(secret) < 32 or secret.startswith('dev-only'))):
        raise RuntimeError('Configure un JWT_SECRET seguro (mínimo 32 caracteres en producción)')
    now = datetime.now(timezone.utc)
    claims = {'sub': str(user.id), 'iss': 'paladar-inka-api', 'aud': 'paladar-inka-ui', 'iat': now, 'exp': now + timedelta(minutes=s.token_ttl_minutes)}
    return jwt.encode(claims, secret, algorithm='HS256')

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Autenticación requerida', headers={'WWW-Authenticate':'Bearer'})
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret, algorithms=['HS256'], audience='paladar-inka-ui', issuer='paladar-inka-api')
        uid = int(payload['sub'])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Token inválido o vencido', headers={'WWW-Authenticate':'Bearer'})
    user = db.get(User, uid)
    if user is None or not user.active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Cuenta no disponible')
    return user

def require_roles(*roles: str) -> Callable:
    def gate(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, 'Rol sin permiso para esta operación')
        return user
    return gate