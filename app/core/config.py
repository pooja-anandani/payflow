from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    algorithm: str
    app_name: str
    app_version: str
    debug: bool
    redis_url: str
    kafka_bootstrap_servers: str
    kafka_payment_topic: str

    class Config:
        env_file = ".env"


settings = Settings()
