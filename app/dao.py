import typing

import aioredis
from models import ChannelInfo
from serializers import ChannelInfoSerializer


class ChannelInfoDAO:
    CHANNEL_KEY_PREFIX = "channel_{channel_id}"

    def __init__(self, client: aioredis.Redis) -> None:
        self.client = client

    def _prepare_channel_key(self, channel_id) -> str:
        return self.CHANNEL_KEY_PREFIX.format(channel_id=channel_id)

    async def write_channel_info(self, channel_info: ChannelInfo) -> None:
        serializer = ChannelInfoSerializer.from_model(channel_info)
        key = self._prepare_channel_key(channel_info.channel_id)
        await self.client.set(key, serializer.json())

    async def get_channel_info(self, channel_id: int) -> typing.Optional[ChannelInfo]:
        key = self._prepare_channel_key(channel_id)
        data = await self.client.get(key)
        if data is None:
            return None

        serializer = ChannelInfoSerializer.parse_raw(data)
        return serializer.to_model()
