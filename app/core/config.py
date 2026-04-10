from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):

    PROJECT_NAME: str = "Zhagaram Showroom Management"

    # ✅ Must come from ENV in production
    DATABASE_URL: str

    # ✅ Change this (important)
    JWT_SECRET_KEY: str = Field(default="change-this-in-production")

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
