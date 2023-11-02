import contextlib
import time
import typing

import structlog

from dbot.connectors.router import NotificationRouter
from dbot.dscrd.abstract import IDiscordClient
from dbot.infrastructure.monitoring import IMonitoring
from dbot.repository import Repository

logger = structlog.getLogger()


class ActivityProcessingServiceInstrumentation:
    def __init__(self, monitoring: IMonitoring) -> None:
        self._monitoring = monitoring

    @contextlib.asynccontextmanager
    async def channel_processing(self, channel_id: int) -> typing.AsyncIterator[None]:
        start = time.monotonic()
        logger.debug("channel_processing.started", channel_id=channel_id)

        yield

        processing_time = time.monotonic() - start
        logger.debug("channel_processing.finished", channel_id=channel_id, processing_time=processing_time)
        await self._monitoring.fire_channel_processing(channel_id, processing_time)

    @contextlib.asynccontextmanager
    async def channels_processing(self, channels: set[int]) -> typing.AsyncIterator[None]:
        start = time.monotonic()
        logger.info("channels_processing.started", ids=channels)

        yield

        processing_time = time.monotonic() - start
        logger.info("channels_processing.finished", ids=channels, processing_time=processing_time)

        await self._monitoring.on_job_executed_successfully()
        await self._monitoring.fire_channels_processing(processing_time)


class ActivityProcessingService:
    def __init__(
        self,
        repository: Repository,
        router: NotificationRouter,
        channels: set[int],
        monitoring: IMonitoring,
    ) -> None:
        self.repository = repository
        self.router = router
        self.channels = channels
        self.instrumentation = ActivityProcessingServiceInstrumentation(monitoring)

    def register_client(self, discord_client: IDiscordClient) -> None:
        self.repository.set_discord_client(discord_client)

    async def process(self) -> None:
        async with self.instrumentation.channels_processing(self.channels):
            for channel_id in self.channels:
                await self._process_chanel(channel_id)

    async def _process_chanel(self, channel_id: int) -> None:
        async with self.instrumentation.channel_processing(channel_id):
            channel = await self.repository.get(channel_id)
            if channel is None:
                return

            notifications = channel.generate_notifications()

            await self.router.send(notifications)

            await self.repository.save(channel)
