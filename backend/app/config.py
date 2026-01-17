from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    GA4_PROPERTY_ID: str
    GA4_CREDENTIALS_JSON: str = "./credentials.json"
    GEMINI_API_KEY: str
    DEEPSEEK_API_KEY: str
    ADMIN_SECRET: str
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
