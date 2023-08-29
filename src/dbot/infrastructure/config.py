from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="dbot_", case_sensitive=False)

    discord_token: str
    redis_url: str
    channel_config_path: str = "./src/dbot/channel_config/config.json"
    sentry_dsn: str = ""
    healthchecksio_webhook: str = ""


config_instance = Configuration()
