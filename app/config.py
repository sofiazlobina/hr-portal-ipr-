from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[1] / '.env',
                                     env_file_encoding='utf-8')
    DATABASE_URL: str
    SECRET_KEY: str = 'your-secret-key-change-this-in-production'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()


def get_settings():
    return settings
