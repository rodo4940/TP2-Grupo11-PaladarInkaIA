from fastapi.testclient import TestClient
import pytest

from app.db.health import is_database_ready
from app.db.session import SessionLocal


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "paladar-inka-api",
    }


def test_ready_returns_ok_when_database_is_available(client_with_ready_db: TestClient) -> None:
    response = client_with_ready_db.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ok",
    }


def test_ready_returns_ok_with_real_database_when_available(client: TestClient) -> None:
    db = SessionLocal()
    try:
        if not is_database_ready(db):
            pytest.skip("PostgreSQL is not available in this test environment")
    finally:
        db.close()

    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ok",
    }
