import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def client_with_ready_db(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    def fake_db():
        yield object()

    monkeypatch.setattr("app.api.v1.endpoints.health.is_database_ready", lambda db: True)
    app.dependency_overrides[get_db] = fake_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
