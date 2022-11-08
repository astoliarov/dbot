import typing

import structlog
from model import ChannelConfig
from monitoring import HealthChecksIOMonitoring
from repository import Repository
from sender import CallbackService

logger = structlog.getLogger()


class ActivityProcessingService:
    def __init__(
        self,
        repository: Repository,
        callback_service: CallbackService,
        channel_configs: list[ChannelConfig],
        monitoring: typing.Optional[HealthChecksIOMonitoring],
    ) -> None:

        self.repository = repository
        self.callback_service = callback_service
        self.channel_configs = channel_configs
        self.monitoring = monitoring

    def register_client(self, discord_client):
        self.repository.set_discord_client(discord_client)

    async def on_proces_finish(self):
        if self.monitoring:
            await self.monitoring.on_job_executed_successfully()

    async def process(self):
        logger.info("starting channels processing")
        for channel in self.channel_configs:
            await self._process_chanel(channel)

        await self.on_proces_finish()
        logger.info("finished channels processing")

    async def _process_chanel(self, config: ChannelConfig) -> None:
        logger.debug("started channel processing", channel_id=config.channel_id)

        channel = await self.repository.get(config.channel_id)
        if channel is None:
            return

        notifications = channel.generate_notifications()
        for notification in notifications:
            await self.callback_service.send(notification)

        await self.repository.save(channel)
