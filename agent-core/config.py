"""
HyperOS Configuration Management
Centralized configuration with validation using Pydantic
"""

import os
from typing import Optional, Literal
from pathlib import Path
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All settings have sensible defaults for development.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ==========================================================================
    # API Keys
    # ==========================================================================
    
    gemini_api_key: str = Field(
        ...,  # Required
        min_length=20,
        description="Google Gemini API key"
    )
    
    # ==========================================================================
    # Agent Configuration
    # ==========================================================================
    
    max_steps: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum steps per task"
    )
    
    step_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Delay between steps in seconds"
    )
    
    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model to use"
    )
    
    # ==========================================================================
    # Server Configuration
    # ==========================================================================
    
    host: str = Field(
        default="127.0.0.1",
        description="Server host"
    )
    
    port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Server port"
    )
    
    # ==========================================================================
    # Security Configuration
    # ==========================================================================
    
    enable_audit_log: bool = Field(
        default=True,
        description="Enable action audit logging"
    )
    
    rate_limit_requests: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max requests per rate limit window"
    )
    
    rate_limit_window: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Rate limit window in seconds"
    )
    
    enable_coordinate_safety: bool = Field(
        default=True,
        description="Enable safe coordinate validation"
    )
    
    # ==========================================================================
    # Logging Configuration
    # ==========================================================================
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    log_file: Optional[str] = Field(
        default="logs/hyperos.log",
        description="Log file path (None to disable file logging)"
    )
    
    log_max_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max log file size in MB before rotation"
    )
    
    log_backup_count: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of log backups to keep"
    )
    
    # ==========================================================================
    # Environment
    # ==========================================================================
    
    environment: Literal["development", "production", "testing"] = Field(
        default="development",
        description="Application environment"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # ==========================================================================
    # Validators
    # ==========================================================================
    
    @field_validator("gemini_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if v == "your_gemini_api_key_here":
            raise ValueError(
                "Please set a valid GEMINI_API_KEY in your .env file. "
                "Get one at: https://makersuite.google.com/app/apikey"
            )
        if not v.startswith("AI"):
            # Gemini keys typically start with "AI"
            pass  # Just a warning, not blocking
        return v
    
    @field_validator("log_file")
    @classmethod
    def validate_log_file(cls, v: Optional[str]) -> Optional[str]:
        if v:
            log_path = Path(v)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    # ==========================================================================
    # Properties
    # ==========================================================================
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def cors_origins(self) -> list:
        """Get CORS origins based on environment"""
        if self.is_development:
            return [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        return [
            "file://",  # Electron in production
        ]


class DevelopmentSettings(Settings):
    """Development-specific settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    environment: Literal["development", "production", "testing"] = "development"
    debug: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"


class ProductionSettings(Settings):
    """Production-specific settings with stricter defaults"""
    
    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8"
    )
    
    environment: Literal["development", "production", "testing"] = "production"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    enable_audit_log: bool = True


class TestingSettings(Settings):
    """Testing-specific settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8"
    )
    
    environment: Literal["development", "production", "testing"] = "testing"
    debug: bool = True
    enable_audit_log: bool = False
    gemini_api_key: str = "test_key_for_testing_only_12345"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance based on environment.
    
    Returns:
        Settings instance appropriate for the current environment
    """
    env = os.getenv("HYPEROS_ENV", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


def validate_environment() -> tuple[bool, list[str]]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        example_file = Path(".env.example")
        if example_file.exists():
            errors.append(
                "No .env file found. Copy .env.example to .env and configure it."
            )
        else:
            errors.append("No .env file found. Create one with GEMINI_API_KEY.")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        errors.append("GEMINI_API_KEY is not set in environment or .env file")
    elif api_key == "your_gemini_api_key_here":
        errors.append(
            "GEMINI_API_KEY is still set to placeholder value. "
            "Get a real key at: https://makersuite.google.com/app/apikey"
        )
    elif len(api_key) < 20:
        errors.append("GEMINI_API_KEY appears to be invalid (too short)")
    
    return len(errors) == 0, errors


# Export settings instance
settings = get_settings()
