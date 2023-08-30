from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="dbot_redis_", case_sensitive=False)

    url: str


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="dbot_", case_sensitive=False)

    discord_token: str
    channel_config_path: str = "./src/dbot/channel_config/config.json"
    sentry_dsn: str = ""
    healthchecksio_webhook: str = ""


config_instance = Configuration()
redis_config_instance = RedisConfig()
