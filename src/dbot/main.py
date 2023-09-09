import asyncio

import aiohttp
import sentry_sdk
import structlog

from dbot.config_loader.loader import JSONLoader
from dbot.connectors.router import NotificationRouter
from dbot.connectors.webhooks.transport import WebhooksTransport, initialize_session
from dbot.connectors.webhooks.webhooks import WebhooksConnector
from dbot.dscrd.client import DiscordClient
from dbot.infrastructure.config import config_instance, redis_config_instance
from dbot.infrastructure.logs import initialize_logs
from dbot.infrastructure.monitoring import initialize_monitoring
from dbot.model.config import TargetTypeEnum
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
        monitor_config = loader.from_file(config_instance.channel_config_path)

        self.session = await initialize_session()
        transport = WebhooksTransport(self.session)
        webhooks_connector = WebhooksConnector(monitor_config, transport)

        router = NotificationRouter(monitor_config)
        router.register_connector(TargetTypeEnum.WEBHOOKS, webhooks_connector)

        processing_service = ActivityProcessingService(
            repository=repository,
            router=router,
            channels=monitor_config.channels_ids,
            monitoring=monitoring,
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
