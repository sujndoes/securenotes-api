from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
class Settings(BaseSettings):
	secret_key: str = Field(min_length=32)
	database_url: str = "sqlite:///./securenotes.db"
	access_token_expire_minutes: int = 15
	environment: str = "production"
	
	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()	
