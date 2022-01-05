# coding: utf-8

from config import env

from .base import *

DISCORD_TOKEN = env.str(f"{ENV_PREFIX}_DISCORD_TOKEN", "")  # type: ignore
REDIS_URL = env.str(f"{ENV_PREFIX}_REDIS_URL", "")  # type: ignore

CHANNEL_CONFIG_PATH = env.str(f"{ENV_PREFIX}_CHANNEL_CONFIG_PATH", "./channel_config/config.json")  # type: ignore
SENTRY_DSN = env.str(f"{ENV_PREFIX}_SENTRY_DSN", "")  # type: ignore
