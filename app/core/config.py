"""Application configuration settings"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # API Settings
    app_name: str = "AI Assistant Chat System"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM Settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_model: str = "gpt-4o-mini"
    
    # Chat Settings
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # CORS Settings - Handle as string then convert to list
    cors_origins: Optional[str] = None
    
    # Supabase Settings
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert cors_origins string to list"""
        if self.cors_origins:
            return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
        # Default to allow common local dev ports and Vercel domain
        return [
            "http://localhost:3000", 
            "http://localhost:8080",
            "https://portfolio-smoky-iota-20ecu1z2nu.vercel.app"
        ]


# Global settings instance
settings = Settings() 