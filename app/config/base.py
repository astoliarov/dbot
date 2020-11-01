# coding: utf-8
from logging import config as logging_config

ENV_PREFIX = "DBOT"

REDIS_URL = "redis://localhost:6379/0"
CHANNEL_CONFIG_PATH = "./channel_config/config.json"

DISCORD_TOKEN = ""
SENTRY_DSN = ""

config = {
    "version": 1,
    "formatters": {"simple": {"format": "%(asctime)s - %(name)s - %(message)s", }},
    "handlers": {"console": {"class": "logging.StreamHandler", "level": "DEBUG", "formatter": "simple"}},
    "loggers": {
        "debug": {"level": "DEBUG", "handlers": ["console", ]},
    },
}
logging_config.dictConfig(config)
