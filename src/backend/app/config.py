"""
Application configuration management.
"""
import os
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field
from enum import Enum


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(default="sqlite+aiosqlite:///./strategy_system.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)
    pool_timeout: int = Field(default=30)
    
    class Config:
        env_prefix = "DB_"


class AuthConfig(BaseSettings):
    """Authentication configuration."""
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    
    class Config:
        env_prefix = "AUTH_"


class APIConfig(BaseSettings):
    """API configuration."""
    title: str = Field(default="Wafer Sampling Strategy System")
    description: str = Field(default="API for managing wafer sampling strategies")
    version: str = Field(default="1.0.0")
    docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")
    openapi_url: str = Field(default="/openapi.json")
    
    # CORS settings
    allow_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])
    allow_credentials: bool = Field(default=True)
    allow_methods: List[str] = Field(default=["*"])
    allow_headers: List[str] = Field(default=["*"])
    
    class Config:
        env_prefix = "API_"


class PluginConfig(BaseSettings):
    """Plugin system configuration."""
    plugin_directories: List[str] = Field(default=[])
    auto_discover_plugins: bool = Field(default=True)
    plugin_timeout: int = Field(default=30)  # seconds
    max_plugin_memory: int = Field(default=100)  # MB
    
    class Config:
        env_prefix = "PLUGIN_"


class StorageConfig(BaseSettings):
    """File storage configuration."""
    strategy_storage_path: str = Field(default="./data/strategies")
    simulation_cache_path: str = Field(default="./data/cache")
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    allowed_file_types: List[str] = Field(default=[".yaml", ".yml", ".json", ".xlsx"])
    
    class Config:
        env_prefix = "STORAGE_"


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: Optional[str] = Field(default=None)
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    backup_count: int = Field(default=5)
    
    class Config:
        env_prefix = "LOG_"


class MonitoringConfig(BaseSettings):
    """Monitoring and metrics configuration."""
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=8001)
    health_check_interval: int = Field(default=30)  # seconds
    enable_tracing: bool = Field(default=False)
    jaeger_endpoint: Optional[str] = Field(default=None)
    
    class Config:
        env_prefix = "MONITORING_"


class VendorConfig(BaseSettings):
    """Vendor integration configuration."""
    asml_config: Dict[str, Any] = Field(default_factory=dict)
    kla_config: Dict[str, Any] = Field(default_factory=dict)
    default_timeout: int = Field(default=30)  # seconds
    retry_attempts: int = Field(default=3)
    
    class Config:
        env_prefix = "VENDOR_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=True)
    
    # Host and port
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    vendors: VendorConfig = Field(default_factory=VendorConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING
    
    def get_database_url(self) -> str:
        """Get database URL with environment-specific overrides."""
        if self.is_testing:
            return "sqlite+aiosqlite:///./test.db"
        return self.database.url
    
    def setup_logging(self):
        """Setup application logging."""
        import logging
        import logging.handlers
        
        # Set log level
        level = getattr(logging, self.logging.level.upper(), logging.INFO)
        logging.basicConfig(level=level, format=self.logging.format)
        
        # Setup file logging if configured
        if self.logging.file_path:
            os.makedirs(os.path.dirname(self.logging.file_path), exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                self.logging.file_path,
                maxBytes=self.logging.max_file_size,
                backupCount=self.logging.backup_count
            )
            file_handler.setFormatter(logging.Formatter(self.logging.format))
            logging.getLogger().addHandler(file_handler)
    
    def create_directories(self):
        """Create necessary directories."""
        directories = [
            self.storage.strategy_storage_path,
            self.storage.simulation_cache_path,
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Global settings instance
settings = Settings()

# Setup on import
settings.setup_logging()
settings.create_directories()