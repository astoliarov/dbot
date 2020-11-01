# coding: utf-8
import dataclasses
import json
import typing

import aioredis
from models import ChannelInfo, UserActivityInfo
from serializers import ChannelInfoSchema


class RedisJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class ChannelInfoDAO:
    CHANNEL_KEY_PREFIX = "channel_{channel_id}"

    def __init__(self, client: aioredis.Redis) -> None:
        self.client = client

    def _prepare_channel_key(self, channel_id) -> str:
        return self.CHANNEL_KEY_PREFIX.format(channel_id=channel_id)

    async def write_channel_info(self, channel_info: ChannelInfo) -> None:
        schema = ChannelInfoSchema()
        serialized = schema.dumps(channel_info)

        key = self._prepare_channel_key(channel_info.channel_id)
        await self.client.set(key, serialized)

    async def get_channel_info(self, channel_id: int) -> typing.Optional[ChannelInfo]:
        key = self._prepare_channel_key(channel_id)
        data = await self.client.get(key)
        if data is None:
            return None

        schema = ChannelInfoSchema()

        loaded = schema.loads(data)
        activities = [UserActivityInfo(**activity) for activity in loaded["activities"]]

        return ChannelInfo(
            channel_id=loaded["channel_id"],
            timestamp=loaded["timestamp"],
            activities=activities,
        )
