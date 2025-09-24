import os
from datetime import timedelta
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

#Lee .env y carga configuraciones de entorno
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Backend Campaigns")
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    DB_POSTGRESQL_URL: str = os.getenv("DB_POSTGRESQL_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-change-me")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    ACCESS_TTL = timedelta(minutes=int(os.getenv("ACCESS_TTL_MIN", "30")))
    REFRESH_TTL = timedelta(days=int(os.getenv("REFRESH_TTL_DAYS", "15")))
    JWT_ISS: str = os.getenv("JWT_ISS", "bk-robot")
    JWT_AUD: str = os.getenv("JWT_AUD", "bk-robot-clients")

@lru_cache
def get_settings() -> Settings:
    return Settings()