"""
Configuration - Application settings
Following Clean Architecture: Infrastructure configuration
"""

import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)


class Settings(BaseModel):
    """
    Application settings
    Single Responsibility: Centralize configuration
    """
    
    # API Settings
    api_title: str = "Invoice Agent API"
    api_version: str = "1.0.0"
    api_description: str = "Conversational AI for invoice creation"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Settings
    cors_origins: list[str] = ["*"]  # In production, specify actual origins
    cors_methods: list[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: list[str] = ["*"]
    
    # Agent Settings
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Logging Settings
    log_level: str = "INFO"
    
    @property
    def is_anthropic_configured(self) -> bool:
        """Check if Anthropic API key is configured"""
        return bool(self.anthropic_api_key and self.anthropic_api_key != "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
