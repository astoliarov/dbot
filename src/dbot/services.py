import structlog

from dbot.connectors.router import NotificationRouter
from dbot.dscrd.abstract import IDiscordClient
from dbot.infrastructure.monitoring import IMonitoring
from dbot.repository import Repository

logger = structlog.getLogger()


class ActivityProcessingService:
    def __init__(
        self,
        repository: Repository,
        router: NotificationRouter,
        channels: set[int],
        monitoring: IMonitoring | None,
    ) -> None:
        self.repository = repository
        self.router = router
        self.channels = channels
        self.monitoring = monitoring

    def register_client(self, discord_client: IDiscordClient) -> None:
        self.repository.set_discord_client(discord_client)

    async def on_proces_finish(self) -> None:
        if self.monitoring:
            await self.monitoring.on_job_executed_successfully()

    async def process(self) -> None:
        logger.info("starting channels processing")
        for channel_id in self.channels:
            await self._process_chanel(channel_id)

        await self.on_proces_finish()
        logger.info("finished channels processing")

    async def _process_chanel(self, channel_id: int) -> None:
        logger.debug("started channel processing", channel_id=channel_id)

        channel = await self.repository.get(channel_id)
        if channel is None:
            return

        notifications = channel.generate_notifications()

        await self.router.send(notifications)

        await self.repository.save(channel)
