from typing import Any

from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings

from src.constants import Environment


class Config(BaseSettings):
    ENVIRONMENT: Environment = Environment.LOCAL
    JWT_SECRET: str
    JWT_ALG: str

    DATABASE_URL: PostgresDsn

    APP_VERSION: int = 1


settings = Config()  #  pyright: ignore[reportCallIssue]

app_configs: dict[str, Any] = {"title": "Breadfund API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v/{settings.APP_VERSION}"

# hide docs prod
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
