# coding: utf-8
import asyncio

import discord
import typing

from models import User
from checker import VoiceChannelChecker


class DiscordClient(discord.Client):

    def __init__(self, checker: VoiceChannelChecker, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.checker = checker
        self.checker.register_client(self)

        self.bg_task = self.loop.create_task(self.my_background_task())

    async def my_background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await self.checker.process()
            await asyncio.sleep(10)  # task runs every 60 seconds

    def get_channel_members(self, channel_id: int) -> typing.List[User]:
        channel = self.get_channel(channel_id)

        users = []
        for member in channel.members:
            users.append(User(id=member.id, username=member.name))

        return users
