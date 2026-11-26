"""Configuración estricta, sin secretos reales dentro del repositorio."""
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    app_name: str = Field(default='Paladar Inka API', alias='APP_NAME')
    app_env: str = Field(default='development', alias='APP_ENV')
    debug: bool = Field(default=False, alias='DEBUG')
    api_v1_prefix: str = Field(default='/api/v1', alias='API_V1_PREFIX')
    database_host: str = Field(default='localhost', alias='DATABASE_HOST')
    database_port: int = Field(default=5432, alias='DATABASE_PORT')
    database_name: str = Field(default='paladar_inka', alias='DATABASE_NAME')
    database_user: str = Field(default='paladar_user', alias='DATABASE_USER')
    database_password: str = Field(default='change_me', alias='DATABASE_PASSWORD')
    database_url_override: str | None = Field(default=None, alias='DATABASE_URL')
    cors_origins: str = Field(default='http://localhost:5173', alias='CORS_ORIGINS')
    jwt_secret: str = Field(default='dev-only-replace-with-32-characters-secret', alias='JWT_SECRET')
    token_ttl_minutes: int = Field(default=480, ge=5, le=1440, alias='TOKEN_TTL_MINUTES')

    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, value: object) -> bool:
        if isinstance(value, bool): return value
        if isinstance(value, str):
            normalized=value.strip().lower()
            if normalized in {'1','true','yes','y','on','debug','development'}: return True
            if normalized in {'0','false','no','n','off','release','production'}: return False
        return bool(value)

    @property
    def database_url(self) -> str:
        if self.database_url_override: return self.database_url_override
        from urllib.parse import quote_plus
        return f'postgresql+psycopg://{quote_plus(self.database_user)}:{quote_plus(self.database_password)}@{self.database_host}:{self.database_port}/{self.database_name}'

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(',') if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()