from typing import Optional

class Settings():
    # API Keys
    openai_api_key: str
    hyperliquid_api_key: str
    supabase_url: str
    supabase_anon_key: str
    infura_project_id: str
    covalent_api_key: Optional[str] = None
    
    # Database
    database_url: str = ""
    
    # Security
    jwt_secret_key: str
    
    # Application
    debug: bool = False
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()