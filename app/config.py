from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "HisabPro"
    DEBUG: bool = True
    
    # Database
    # Default to local SQLite for dev. In prod, this will be overridden by env var.
    DATABASE_URL: str = "sqlite+aiosqlite:///./sales_manager.db"
    
    # Security
    # Default secret for dev only. MUST override in prod.
    SECRET_KEY: str = "dev_secret_key_change_me_in_prod_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Payment Guard
    # Set to True in Prod to enforce payment check
    PAYMENT_REQUIRED: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
