"""
Configuration management for SmartCharge AI Backend
Loads environment variables and provides typed configuration objects
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # IBM Bob API Configuration
    ibm_bob_api_key: str = Field(..., env="IBM_BOB_API_KEY")
    ibm_bob_api_url: str = Field(
        default="https://api.watsonx.ai/v1/bob",
        env="IBM_BOB_API_URL"
    )
    ibm_bob_project_id: Optional[str] = Field(default=None, env="IBM_BOB_PROJECT_ID")
    ibm_bob_model_id: str = Field(
        default="ibm/granite-13b-chat-v2",
        env="IBM_BOB_MODEL_ID"
    )
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Configuration (optional for demo)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    redis_cache_ttl: int = Field(default=300, env="REDIS_CACHE_TTL")
    redis_enabled: bool = Field(default=True, env="REDIS_ENABLED")
    
    # Application Settings
    app_name: str = Field(default="SmartCharge AI", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=1440, env="JWT_EXPIRATION_MINUTES")
    
    # CORS Settings
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # API Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Telemetry Settings
    telemetry_interval_seconds: int = Field(default=5, env="TELEMETRY_INTERVAL_SECONDS")
    telemetry_batch_size: int = Field(default=100, env="TELEMETRY_BATCH_SIZE")
    
    # Charging Modes
    fast_charge_power_kw: float = Field(default=11.0, env="FAST_CHARGE_POWER_KW")
    eco_mode_power_kw: float = Field(default=3.5, env="ECO_MODE_POWER_KW")
    pause_power_kw: float = Field(default=0.0, env="PAUSE_POWER_KW")
    
    # Decision Engine Settings
    decision_confidence_threshold: float = Field(
        default=0.7,
        env="DECISION_CONFIDENCE_THRESHOLD"
    )
    max_decision_retries: int = Field(default=3, env="MAX_DECISION_RETRIES")
    decision_timeout_seconds: int = Field(default=10, env="DECISION_TIMEOUT_SECONDS")
    
    # WebSocket Settings
    ws_heartbeat_interval: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    ws_max_connections: int = Field(default=1000, env="WS_MAX_CONNECTIONS")
    
    # Monitoring & Logging
    sentry_dsn: str = Field(default="", env="SENTRY_DSN")
    datadog_api_key: str = Field(default="", env="DATADOG_API_KEY")
    log_file_path: str = Field(default="logs/smartcharge.log", env="LOG_FILE_PATH")
    log_rotation_size_mb: int = Field(default=100, env="LOG_ROTATION_SIZE_MB")
    log_retention_days: int = Field(default=30, env="LOG_RETENTION_DAYS")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins into a list"""
        if isinstance(v, list):
            return ",".join(v)
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the expected values"""
        valid_envs = ["development", "staging", "production"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v_lower
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Helper functions
def get_database_url() -> str:
    """Get the database URL for SQLAlchemy"""
    return settings.database_url


def get_redis_url() -> Optional[str]:
    """Get the Redis URL (returns None if Redis is disabled)"""
    if not settings.redis_enabled or not settings.redis_url:
        return None
    return settings.redis_url


def is_redis_enabled() -> bool:
    """Check if Redis caching is enabled"""
    return settings.redis_enabled and bool(settings.redis_url)


def is_production() -> bool:
    """Check if running in production environment"""
    return settings.environment == "production"


def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return settings.debug


def get_cors_origins() -> List[str]:
    """Get list of allowed CORS origins"""
    if isinstance(settings.cors_origins, list):
        return settings.cors_origins
    return [origin.strip() for origin in settings.cors_origins.split(",")]


# IBM Bob specific helpers
def get_bob_headers() -> dict:
    """Get headers for IBM Bob API requests"""
    return {
        "Authorization": f"Bearer {settings.ibm_bob_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def get_bob_api_endpoint(path: str = "") -> str:
    """Construct full IBM Bob API endpoint URL"""
    base_url = settings.ibm_bob_api_url.rstrip("/")
    if path:
        path = path.lstrip("/")
        return f"{base_url}/{path}"
    return base_url


# Charging mode configuration
CHARGING_MODES = {
    "FAST_CHARGE": {
        "power_kw": settings.fast_charge_power_kw,
        "description": "Maximum charging speed using available power",
        "priority": 1
    },
    "ECO_MODE": {
        "power_kw": settings.eco_mode_power_kw,
        "description": "Balanced charging optimizing for renewable energy",
        "priority": 2
    },
    "PAUSED": {
        "power_kw": settings.pause_power_kw,
        "description": "Charging paused to avoid peak pricing or grid strain",
        "priority": 3
    }
}


def get_charging_mode_config(mode: str) -> dict:
    """Get configuration for a specific charging mode"""
    return CHARGING_MODES.get(mode.upper(), CHARGING_MODES["ECO_MODE"])

# Made with Bob
