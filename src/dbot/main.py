import asyncio

import aiohttp
import sentry_sdk
import structlog

import dbot.dscrd
from dbot.channel_config.loader import JSONLoader
from dbot.config import config_instance
from dbot.connectors.transport import WebhooksTransport, initialize_session
from dbot.connectors.webhooks import WebhookService
from dbot.logs import initialize_logs
from dbot.monitoring import HealthChecksIOMonitoring
from dbot.repository import Repository, open_redis
from dbot.services import ActivityProcessingService

logger = structlog.getLogger()


class DBot:
    def __init__(self) -> None:
        self.client: dbot.dscrd.DiscordClient | None = None
        self.session: aiohttp.ClientSession | None = None

    async def initialize(self) -> None:
        initialize_logs(config_instance.logging_level)

        if config_instance.sentry_dsn:
            sentry_sdk.init(config_instance.sentry_dsn)

        if config_instance.healthchecksio_webhook:
            healthchecks_io_monitoring = HealthChecksIOMonitoring(webhook=config_instance.healthchecksio_webhook)
        else:
            healthchecks_io_monitoring = None

        loader = JSONLoader()
        channel_config = loader.from_file(config_instance.channel_config_path)

        redis_client = await open_redis(config_instance.redis_url)
        repository = Repository(redis_client=redis_client)

        self.session = await initialize_session()
        transport = WebhooksTransport(self.session)
        webhooks_service = WebhookService(channel_config.channels, transport)

        processing_service = ActivityProcessingService(
            repository,
            webhooks_service,
            channel_config.channels,
            healthchecks_io_monitoring,
        )
        self.client = dbot.dscrd.DiscordClient(processing_service, check_interval=10)

    async def run_async(self) -> None:
        await self.initialize()

        if self.client is None:
            raise RuntimeError("Client is not initialized")

        await self.client.run_async(config_instance.discord_token)

    def run(self) -> None:
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    instance = DBot()
    instance.run()
