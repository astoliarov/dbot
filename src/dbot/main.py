import asyncio

import aiohttp
import sentry_sdk
import structlog

from dbot.channel_config import new_loader
from dbot.channel_config.loader import JSONLoader
from dbot.connectors.webhooks.transport import WebhooksTransport, initialize_session
from dbot.connectors.webhooks.webhooks import WebhookService
from dbot.dscrd.client import DiscordClient
from dbot.infrastructure.config import config_instance, redis_config_instance
from dbot.infrastructure.logs import initialize_logs
from dbot.infrastructure.monitoring import initialize_monitoring
from dbot.repository import Repository, open_redis
from dbot.services import ActivityProcessingService

logger = structlog.getLogger()


class DBot:
    def __init__(self) -> None:
        self.client: DiscordClient | None = None
        self.session: aiohttp.ClientSession | None = None

    async def initialize(self) -> None:
        initialize_logs()

        if config_instance.sentry_dsn:
            sentry_sdk.init(config_instance.sentry_dsn)

        monitoring = initialize_monitoring()

        redis_client = await open_redis(redis_config_instance.url)
        repository = Repository(redis_client=redis_client)

        loader = JSONLoader()
        channel_config = loader.from_file(config_instance.channel_config_path)

        _loader = new_loader.JSONLoader()
        _channel_config = _loader.from_file("./src/dbot/channel_config/new_config.json")

        self.session = await initialize_session()
        transport = WebhooksTransport(self.session)
        webhooks_service = WebhookService(channel_config.channels, transport)

        processing_service = ActivityProcessingService(
            repository,
            webhooks_service,
            channel_config.channels,
            monitoring,
        )
        self.client = DiscordClient(processing_service, check_interval=10)

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
