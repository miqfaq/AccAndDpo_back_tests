from authx import AuthX, AuthXConfig, TokenPayload
from authx.exceptions import JWTDecodeError
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    DATABASE_URL: str
    DEEPSEEK_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",       
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings() # pyright: ignore[reportCallIssue]


config = AuthXConfig()
config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_COOKIE_CSRF_PROTECT = False #debug
config.JWT_COOKIE_SECURE = False


security = AuthX(config=config)

