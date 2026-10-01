from pydantic_settings import BaseSettings, SettingsConfigDict


# Settings class to hold application configuration
class Settings(BaseSettings):
    database_url: str
    test_database_url: str
    jwt_secret_key: str
    allowed_origins: str = ""

    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding="utf-8",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]
    

settings = Settings()


