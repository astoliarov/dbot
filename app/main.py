import asyncio

import aiohttp
import sentry_sdk
import structlog
from connectors.transport import WebhooksTransport, initialize_session

import app.dscrd
from app.channel_config.loader import JSONLoader
from app.config import config_instance
from app.connectors.webhooks import WebhookService
from app.logs import initialize_logs
from app.monitoring import HealthChecksIOMonitoring
from app.repository import Repository, open_redis
from app.services import ActivityProcessingService

logger = structlog.getLogger()


class DBot:
    def __init__(self):
        self.client: app.dscrd.DiscordClient | None = None
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
        self.client = app.dscrd.DiscordClient(processing_service, check_interval=10)

    async def run_async(self):
        await self.initialize()
        await self.client.run_async(config_instance.discord_token)

    def run(self):
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    dbot = DBot()
    dbot.run()
