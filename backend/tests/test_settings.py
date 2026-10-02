from app.core.config import Settings


def test_debug_accepts_true_aliases() -> None:
    settings = Settings(DEBUG="development")

    assert settings.debug is True


def test_debug_accepts_false_aliases() -> None:
    settings = Settings(DEBUG="production")

    assert settings.debug is False


def test_database_url_uses_configured_values() -> None:
    settings = Settings(
        DATABASE_HOST="db.internal",
        DATABASE_PORT=5433,
        DATABASE_NAME="paladar_test",
        DATABASE_USER="tester",
        DATABASE_PASSWORD="secret",
    )

    assert (
        settings.database_url
        == "postgresql+psycopg://tester:secret@db.internal:5433/paladar_test"
    )


def test_cors_origin_list_normalizes_comma_separated_values() -> None:
    settings = Settings(
        CORS_ORIGINS="http://localhost:5173, https://example.test ,"
    )

    assert settings.cors_origin_list == [
        "http://localhost:5173",
        "https://example.test",
    ]
