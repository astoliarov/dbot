from pydantic import BaseSettings


class Configuration(BaseSettings):
    discord_token: str
    redis_url: str
    channel_config_path: str = "./channel_config/config.json"
    sentry_dsn: str = ""
    logging_level: str = "DEBUG"
    healthcheckio_webhook: str = ""

    class Config:
        env_prefix = "dbot_"
        case_sensitive = False


config_instance = Configuration()
