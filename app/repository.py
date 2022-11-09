import datetime
from typing import Optional

import structlog
from aioredis import Redis
from pydantic import BaseModel

from abstract import IDiscordClient
from model import User
from model.channel import Channel

logger = structlog.get_logger()


def _get_timestamp() -> int:
    return int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())


class UserState(BaseModel):
    username: str
    id: int

    def to_model(self) -> User:
        return User(id=self.id, username=self.username)

    @classmethod
    def from_model(cls, model: User) -> "UserState":
        return cls(id=model.id, username=model.username)


class ChannelState(BaseModel):
    id: int
    ts: int
    users: list[UserState]

    def to_model(self) -> Channel:
        return Channel(id=self.id, users=[s.to_model() for s in self.users])

    @classmethod
    def from_model(cls, model: Channel) -> "ChannelState":
        return cls(
            id=model.id,
            ts=_get_timestamp(),
            users=[UserState.from_model(user) for user in model.users],
        )


class Repository:
    CHANNEL_KEY_PREFIX = "channel_v2_{channel_id}"
    STATE_LIFETIME = 60 * 60  # 1 hour

    def __init__(self, redis_client: Redis, discord_client: Optional[IDiscordClient] = None) -> None:
        self.redis_client = redis_client
        self.discord_client = discord_client

    def set_discord_client(self, discord_client: IDiscordClient) -> None:
        self.discord_client = discord_client

    async def save(self, channel: Channel) -> None:
        state = ChannelState.from_model(channel)
        key = self._prepare_channel_key(channel.id)
        await self.redis_client.set(key, state.json())

    async def get(self, channel_id: int) -> Optional[Channel]:
        assert self.discord_client

        users = self.discord_client.get_channel_members(channel_id)
        if users is None:
            logger.debug("cannot get channel users", channel_id=channel_id)
            return None

        previous_state = await self._load_previous_state(channel_id)
        channel = Channel(id=channel_id, users=users, previous_state=previous_state)
        logger.debug("loaded channel", channel=channel)
        return channel

    async def _load_previous_state(self, channel_id: int) -> Optional[Channel]:
        channel_key = self._prepare_channel_key(channel_id)
        data = await self.redis_client.get(channel_key)
        if data is None:
            logger.debug("no previous state", channel_id=channel_id)
            return None

        state = ChannelState.parse_raw(data)
        if _get_timestamp() - state.ts > self.STATE_LIFETIME:
            logger.debug("previous state outdated", channel_id=channel_id)
            return None

        return state.to_model()

    def _prepare_channel_key(self, channel_id) -> str:
        return self.CHANNEL_KEY_PREFIX.format(channel_id=channel_id)
