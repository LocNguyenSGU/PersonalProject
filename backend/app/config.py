from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SUPABASE_URL: str = "postgresql://localhost/test"
    SUPABASE_KEY: str = "test_key"
    GA4_PROPERTY_ID: str = "123456789"
    GA4_CREDENTIALS_JSON: str = "./credentials.json"
    GEMINI_API_KEY: str = "test_gemini_key"
    DEEPSEEK_API_KEY: str = "test_deepseek_key"
    ADMIN_SECRET: str = "test_secret_key_for_jwt"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
