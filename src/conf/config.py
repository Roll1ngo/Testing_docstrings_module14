from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://username:password@host:port/database_name"

    SECRET_KEY: str = "key for encryption JWT token"
    ALGORITHM: str = "algorithm for encryption JWT "

    MAIL_USERNAME: EmailStr = "email@service.com"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: str = "mail_from"
    MAIL_PORT: int = 1111
    MAIL_SERVER: str = 1111

    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None

    CLD_NAME: str = "Cloudinary name from https://cloudinary.com/"
    CLD_API_KEY: int
    CLD_API_SECRET_KEY: str = "Cloudinary secret_api_key from https://cloudinary.com/"

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")


config = Settings()
