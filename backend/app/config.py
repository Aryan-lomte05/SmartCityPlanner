from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()
