"""Configuration management for the ADCO system."""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

from .core.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    llm_provider: str = Field("openai", alias="LLM_PROVIDER")
    llm_model: str = Field("gpt-4-turbo-preview", alias="LLM_MODEL")
    
    # Database Configuration
    database_url: str = Field("sqlite:///./data/adco.db", alias="DATABASE_URL")
    
    # Vector Store Configuration
    vector_store_type: str = Field("chroma", alias="VECTOR_STORE_TYPE")
    chroma_persist_dir: str = Field("./data/chroma_db", alias="CHROMA_PERSIST_DIR")
    pinecone_api_key: Optional[str] = Field(None, alias="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(None, alias="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field("adco-regulations", alias="PINECONE_INDEX_NAME")
    
    # Application Configuration
    app_name: str = Field("ADCO Multi-Agent System", alias="APP_NAME")
    app_version: str = Field("1.0.0", alias="APP_VERSION")
    debug: bool = Field(False, alias="DEBUG")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")
    api_secret_key: str = Field("change-me-in-production", alias="API_SECRET_KEY")
    
    # Agent Configuration
    max_concurrent_agents: int = Field(5, alias="MAX_CONCURRENT_AGENTS")
    agent_timeout: int = Field(300, alias="AGENT_TIMEOUT")
    retry_attempts: int = Field(3, alias="RETRY_ATTEMPTS")
    
    # Data Source Configuration
    scan_interval: int = Field(3600, alias="SCAN_INTERVAL")
    max_scan_depth: int = Field(1000, alias="MAX_SCAN_DEPTH")
    
    # Report Configuration
    report_output_dir: str = Field("./data/reports", alias="REPORT_OUTPUT_DIR")
    report_formats: str = Field("pdf,html,json", alias="REPORT_FORMATS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config YAML file
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    
    config = {}
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
        logger.info("Configuration loaded", config_path=str(config_path))
    else:
        logger.warning("Config file not found, using defaults", config_path=str(config_path))
    
    return config


def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings instance
    """
    global _settings
    
    if _settings is None:
        _settings = Settings()
    
    return _settings


def get_config() -> Dict[str, Any]:
    """
    Get merged configuration (YAML + environment variables).
    
    Returns:
        Configuration dictionary
    """
    yaml_config = load_config()
    settings = get_settings()
    
    # Merge YAML config with settings
    config = {
        "llm": {
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "openai_api_key": settings.openai_api_key,
            "anthropic_api_key": settings.anthropic_api_key,
        },
        "database": {
            "url": settings.database_url,
        },
        "vector_store": {
            "type": settings.vector_store_type,
            "chroma_persist_dir": settings.chroma_persist_dir,
            "pinecone_api_key": settings.pinecone_api_key,
            "pinecone_environment": settings.pinecone_environment,
            "pinecone_index_name": settings.pinecone_index_name,
        },
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
            "log_level": settings.log_level,
        },
        "api": {
            "host": settings.api_host,
            "port": settings.api_port,
            "secret_key": settings.api_secret_key,
        },
        "agents": {
            "max_concurrent": settings.max_concurrent_agents,
            "timeout": settings.agent_timeout,
            "retry_attempts": settings.retry_attempts,
        },
        "scanning": {
            "interval": settings.scan_interval,
            "max_depth": settings.max_scan_depth,
        },
        "reports": {
            "output_dir": settings.report_output_dir,
            "formats": settings.report_formats.split(","),
        },
    }
    
    # Override with YAML config if present
    if yaml_config:
        for key, value in yaml_config.items():
            if key in config:
                if isinstance(value, dict):
                    config[key].update(value)
                else:
                    config[key] = value
            else:
                config[key] = value
    
    return config

