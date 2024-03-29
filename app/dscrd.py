# coding: utf-8
import asyncio
import typing

import discord
from models import User
from services import ActivityProcessingService


class DiscordClient(discord.Client):
    def __init__(self, processing_service: ActivityProcessingService, check_interval: int, *args, **kwargs):

        intents = discord.Intents.all()
        kwargs["intents"] = intents

        super().__init__(*args, **kwargs)

        self.processing_service = processing_service
        self.processing_service.register_client(self)
        self.check_interval = check_interval

        self.bg_task = self.loop.create_task(self.my_background_task())

    async def my_background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await self.processing_service.process()
            await asyncio.sleep(self.check_interval)  # task runs every 60 seconds

    def get_channel_members(self, channel_id: int) -> typing.List[User]:
        channel = self.get_channel(channel_id)

        users = []
        for member in channel.members:
            users.append(User(id=member.id, username=member.name))

        return users
