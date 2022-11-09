import asyncio

import aioredis
import sentry_sdk
import structlog
from aioredis import Redis

import dscrd
from channel_config.loader import JSONLoader
from config import config_instance
from logs import initialize_logs
from monitoring import HealthChecksIOMonitoring
from repository import Repository
from sender import CallbackService
from services import ActivityProcessingService

logger = structlog.getLogger()


async def init(redis_url: str) -> Redis:
    return await aioredis.from_url(redis_url, socket_timeout=10)


if __name__ == "__main__":
    initialize_logs(config_instance.logging_level)

    if config_instance.sentry_dsn:
        sentry_sdk.init(config_instance.sentry_dsn)

    if config_instance.healthcheckio_webhook:
        healthchecks_io_monitoring = HealthChecksIOMonitoring(webhook=config_instance.healthchecksio_webhook)
    else:
        healthchecks_io_monitoring = None

    loader = JSONLoader()
    channel_config = loader.from_file(config_instance.channel_config_path)

    loop = asyncio.get_event_loop()

    redis = loop.run_until_complete(init(config_instance.redis_url))
    repository = Repository(redis_client=redis)

    sender = CallbackService(channel_config.channels)

    processing_service = ActivityProcessingService(
        repository,
        sender,
        channel_config.channels,
        healthchecks_io_monitoring,
    )
    client = dscrd.DiscordClient(processing_service, loop=loop, check_interval=10)

    client.run(config_instance.discord_token)
