from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str

    SECRET_KEY: str = 'your_secret_key' # ключ для создания JWT токенов
    ALGORITHM: str # алгоритм для создания JWT токенов


    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


    @property
    def redis_url(self) -> str:
        return (
            f'redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:'
            f'{self.REDIS_PORT}/{self.REDIS_DB}'
        )


    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY


    @property
    def algorithm(self) -> str:
        return self.ALGORITHM


settings = Settings()
