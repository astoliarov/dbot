import asyncio
import logging

import aioredis
import config
import dscrd
import sentry_sdk
from channel_config.loader import JSONLoader
from dao import ChannelInfoDAO
from monitoring import HealthChecksIOMonitoring
from sender import CallbackService
from services import ActivityProcessingService

logger = logging.getLogger("debug")


async def init(redis_url):
    redis = await aioredis.create_redis_pool(redis_url, timeout=10)
    return redis


if __name__ == "__main__":
    if config.SENTRY_DSN:
        sentry_sdk.init(config.SENTRY_DSN)

    if config.HEALTHCHECKSIO_WEBHOOK:
        healthchecks_io_monitoring = HealthChecksIOMonitoring(webhook=config.HEALTHCHECKSIO_WEBHOOK)
    else:
        healthchecks_io_monitoring = None

    loader = JSONLoader()
    channel_config = loader.from_file(config.CHANNEL_CONFIG_PATH)
    logger.debug(channel_config)

    loop = asyncio.get_event_loop()

    redis = loop.run_until_complete(init(config.REDIS_URL))
    dao = ChannelInfoDAO(redis)

    sender = CallbackService(channel_config.channels)

    processing_service = ActivityProcessingService(
        dao,
        sender,
        channel_config.channels,
        healthchecks_io_monitoring,
    )
    client = dscrd.DiscordClient(processing_service, loop=loop, check_interval=10)

    client.run(config.DISCORD_TOKEN)
