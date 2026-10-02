from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.health import is_database_ready
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "paladar-inka-api",
    }


@router.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    if not is_database_ready(db):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unavailable",
                "database": "error",
            },
        )

    return {
        "status": "ready",
        "database": "ok",
    }
