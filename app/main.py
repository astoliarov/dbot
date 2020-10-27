import asyncio

import aioredis

import config
import dscrd
from channel_config.loader import JSONLoader
from services import ActivityProcessingService
from dao import ChannelInfoDAO
from sender import CallbackService


async def init(redis_url):
    redis = await aioredis.create_redis_pool(redis_url, timeout=10)
    return redis

if __name__ == '__main__':
    loader = JSONLoader()
    channel_config = loader.from_file(config.CHANNEL_CONFIG_PATH)

    loop = asyncio.get_event_loop()

    redis = loop.run_until_complete(init(config.REDIS_URL))
    dao = ChannelInfoDAO(redis)

    sender = CallbackService(channel_config.channels)

    processing_service = ActivityProcessingService(dao, sender, channel_config.channels)
    client = dscrd.DiscordClient(processing_service, loop=loop, check_interval=10)

    client.run(config.DISCORD_TOKEN)

    # '740097329318854660'  # channel
    # '740097329318854656'  # guild
