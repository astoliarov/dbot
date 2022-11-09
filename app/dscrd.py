import asyncio
import typing

import discord
import structlog

from abstract import IDiscordClient
from model import User
from services import ActivityProcessingService

logger = structlog.get_logger()


class DiscordClient(discord.Client, IDiscordClient):
    def __init__(self, processing_service: ActivityProcessingService, check_interval: int, *args, **kwargs):

        intents = discord.Intents.all()
        kwargs["intents"] = intents

        super().__init__(*args, **kwargs)

        self.processing_service = processing_service
        self.processing_service.register_client(self)
        self.check_interval = check_interval

        self.bg_task = self.loop.create_task(self.background_worker())

    async def background_worker(self):
        logger.info("starting background task")
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                await self.processing_service.process()
            except Exception as e:
                logger.error(e)
            await asyncio.sleep(self.check_interval)  # task runs every 60 seconds

    def get_channel_members(self, channel_id: int) -> typing.Optional[list[User]]:
        channel = self.get_channel(channel_id)
        if channel is None:
            return None

        return [User(id=member.id, username=member.name) for member in channel.members]
