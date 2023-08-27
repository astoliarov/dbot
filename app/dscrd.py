import asyncio
import typing

import discord
import structlog

from app.abstract import IDiscordClient
from app.model import User
from app.services import ActivityProcessingService

logger = structlog.get_logger()


class DiscordClient(discord.Client, IDiscordClient):
    def __init__(
        self,
        processing_service: ActivityProcessingService,
        check_interval: int,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:

        intents = discord.Intents.all()
        kwargs["intents"] = intents

        super().__init__(*args, **kwargs)

        self.processing_service = processing_service
        self.processing_service.register_client(self)
        self.check_interval = check_interval

    async def on_ready(self) -> None:
        self.loop.create_task(self.background_worker())

    async def background_worker(self) -> None:
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

        if isinstance(channel, (discord.ForumChannel, discord.CategoryChannel, discord.abc.PrivateChannel)):
            return []

        users: list[User] = []

        for member in channel.members:
            if isinstance(member, discord.ThreadMember):
                username = "unknown"
            else:
                username = member.name

            users.append(User(id=member.id, username=username))

        return users

    async def run_async(
        self,
        token: str,
        *,
        reconnect: bool = True,
    ) -> None:
        async with self:
            await self.start(token, reconnect=reconnect)
