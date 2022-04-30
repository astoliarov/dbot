# coding: utf-8

from config import env

from .base import *

DISCORD_TOKEN = env.str(f"{ENV_PREFIX}_DISCORD_TOKEN", "")  # type: ignore
REDIS_URL = env.str(f"{ENV_PREFIX}_REDIS_URL", "")  # type: ignore

CHANNEL_CONFIG_PATH = env.str(f"{ENV_PREFIX}_CHANNEL_CONFIG_PATH", "./channel_config/config.json")  # type: ignore
SENTRY_DSN = env.str(f"{ENV_PREFIX}_SENTRY_DSN", "")  # type: ignore

logging_level = env.str(f"{ENV_PREFIX}_LOGGING_LEVEL", "INFO")  # type: ignore
if logging_level not in ("INFO", "DEBUG"):
    logging_level = "INFO"

HEALTHCHECKSIO_WEBHOOK = env.str(f"{ENV_PREFIX}_HEALTHCHECKSIO_WEBHOOK", "")

config = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
        }
    },
    "loggers": {
        "debug": {
            "level": logging_level,
            "handlers": [
                "console",
            ],
        },
    },
}
logging_config.dictConfig(config)
