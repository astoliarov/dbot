import asyncio

import aioredis
import structlog

import dscrd
import sentry_sdk
from channel_config.loader import JSONLoader
from config import config_instance
from dao import ChannelInfoDAO
from logs import initialize_logs
from monitoring import HealthChecksIOMonitoring
from sender import CallbackService
from services import ActivityProcessingService

logger = structlog.getLogger()


async def init(redis_url):
    redis = await aioredis.from_url(redis_url, socket_timeout=10)
    return redis


if __name__ == "__main__":
    initialize_logs(config_instance.logging_level)

    if config_instance.sentry_dsn:
        sentry_sdk.init(config_instance.sentry_dsn)

    if config_instance.healthcheckio_webhook:
        healthchecks_io_monitoring = HealthChecksIOMonitoring(webhook=config_instance.healthcheckio_webhook)
    else:
        healthchecks_io_monitoring = None

    loader = JSONLoader()
    channel_config = loader.from_file(config_instance.channel_config_path)
    logger.debug(channel_config)

    loop = asyncio.get_event_loop()

    redis = loop.run_until_complete(init(config_instance.redis_url))
    dao = ChannelInfoDAO(redis)

    sender = CallbackService(channel_config.channels)

    processing_service = ActivityProcessingService(
        dao,
        sender,
        channel_config.channels,
        healthchecks_io_monitoring,
    )
    client = dscrd.DiscordClient(processing_service, loop=loop, check_interval=10)

    client.run(config_instance.discord_token)
