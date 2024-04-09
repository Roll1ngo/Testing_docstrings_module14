from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr


class Settings(BaseSettings):
    """
      This class represents the settings for the application.

      Attributes:
      DB_URL (str): The URL of the database.
      SECRET_KEY (str): The secret key for encryption of JWT tokens.
      ALGORITHM (str): The algorithm used for encryption of JWT tokens.
      MAIL_USERNAME (EmailStr): The username for the email service.
      MAIL_PASSWORD (str): The password for the email service.
      MAIL_FROM (str): The email address to send emails from.
      MAIL_PORT (int): The port number for the email service.
      MAIL_SERVER (str): The server address for the email service.
      REDIS_DOMAIN (str): The domain for the Redis server.
      REDIS_PORT (int): The port number for the Redis server.
      REDIS_PASSWORD (str | None): The password for the Redis server.
      CLD_NAME (str): The Cloudinary name from https://cloudinary.com/.
      CLD_API_KEY (int): The Cloudinary API key from https://cloudinary.com/.
      CLD_API_SECRET_KEY (str): The Cloudinary secret API key from https://cloudinary.com/.
      model_config (ConfigDict): A dictionary containing additional configuration options.
      """
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
