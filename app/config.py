from enum import Enum

from pydantic import BaseSettings


class LogLevelEnum(Enum):
    CRITICAL = 'CRITICAL'
    FATAL = 'FATAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'


class Configuration(BaseSettings):
    discord_token: str
    redis_url: str
    channel_config_path: str = "./channel_config/config.json"
    sentry_dsn: str = ""
    logging_level: LogLevelEnum = LogLevelEnum.DEBUG
    healthcheckio_webhook: str = ""

    class Config:
        env_prefix = "dbot_"
        case_sensitive = False


config_instance = Configuration()
