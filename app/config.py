from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite+pysqlite:///./inpi-dev.db'
    app_env: str = 'dev'
    source_stale_days: int = 14

settings = Settings()
