# coding: utf-8
import asyncio
from datetime import datetime

import aioredis

import dscrd

from checker import VoiceChannelChecker
from dao import ChannelInfoDAO
from models import ChannelInfo


async def init():
    redis = await aioredis.create_redis_pool('redis://localhost')
    return redis

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    redis = loop.run_until_complete(init())
    dao = ChannelInfoDAO(redis)

    checker = VoiceChannelChecker(dao)
    client = dscrd.DiscordClient(checker, loop=loop)
    client.run('NzQwMDk2Mzk2MzUwMTkzNzA0.XykCew.sViApzplL772x-kTHpWbAwSXrdU')

    # '740097329318854660'  # channel
    # '740097329318854656'  # guild
