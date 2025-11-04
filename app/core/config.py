from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # app
    port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str = "change-me-in-production"
    password_min_length: int = 8
    
    # db
    db_dsn: str = "postgres://postgres:postgres@localhost:5432/slice_db"
    
    # obs + metrics
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831
    enable_tracing: bool = True
    enable_logging: bool = True
    enable_log_file: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
