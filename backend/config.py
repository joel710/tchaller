"""
Configuration centralisée pour l'application Tcha-llé
"""
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "Tcha-llé Ultra Polyvalent"
    app_version: str = "2.0.0"
    app_description: str = "Plateforme ultra polyvalente pour découvrir toutes les activités locales"
    debug: bool = False
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tchaller")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS - Ultra permissif pour le développement
    cors_origins: List[str] = ["*"]  # Accepte toutes les origines
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]  # Toutes les méthodes
    cors_allow_headers: List[str] = ["*"]  # Tous les headers
    
    # External Services
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Search Engine
    search_radius_default: int = 5000  # 5km par défaut
    search_limit_default: int = 10
    search_radius_max: int = 50000  # 50km maximum
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Cache
    cache_ttl: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale des paramètres
settings = Settings()