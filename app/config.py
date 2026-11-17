from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	secret_key: str
	database_url: str = "sqlite:///./securenotes.db"
	access_token_expire_minutes: int = 15
	
	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()	
