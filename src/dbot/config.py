from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevelEnum(Enum):
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="dbot_", case_sensitive=False)

    discord_token: str
    redis_url: str
    channel_config_path: str = "./src/dbot/channel_config/config.json"
    sentry_dsn: str = ""
    logging_level: LogLevelEnum = LogLevelEnum.DEBUG
    healthchecksio_webhook: str = ""


config_instance = Configuration()
