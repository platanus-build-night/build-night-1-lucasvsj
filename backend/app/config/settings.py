from pydantic_settings import BaseSettings
from pydantic.networks import AnyUrl
from sqlalchemy.orm import declarative_base

import os

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Games Search API"
    DATABASE_URL: str = DATABASE_URL
    SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
Base = declarative_base()