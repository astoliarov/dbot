import datetime
import inspect
from functools import singledispatchmethod
from typing import Any

import redis
from pydantic import BaseModel

from dbot.connectors.abstract import IConnector, NotificationTypesEnum
from dbot.model import MonitorConfig
from dbot.model.notifications import (
    NewUserInChannelNotification,
    Notification,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)


class Message(BaseModel):
    version: int
    type: NotificationTypesEnum
    data: dict[str, Any]
    channel_id: int
    happened_at: datetime.datetime


class RedisConnector(IConnector):
    def __init__(self, client: redis.asyncio.Redis, config: MonitorConfig) -> None:
        self.client = client
        self.config = config

        self.channel_queue_map = self._prepare_queues_for_channels(config)

    def _prepare_queues_for_channels(self, config: MonitorConfig) -> dict[int, str]:
        channel_queue_map = {}

        for channel in config.channels:
            if channel.redis is None:
                continue

            channel_queue_map[channel.channel_id] = channel.redis.queue

        return channel_queue_map

    def _get_queue(self, channel_id: int) -> str | None:
        return self.channel_queue_map.get(channel_id)

    async def send(self, notifications: list[Notification]) -> None:
        for notification in notifications:
            await self._send_one(notification)

    @singledispatchmethod
    async def _send_one(self, notification: Notification) -> None:
        raise NotImplementedError()

    @_send_one.register
    async def _(self, notification: NewUserInChannelNotification) -> None:
        data = {
            "username": notification.user.username,
        }
        await self._send(notification.channel_id, data, NotificationTypesEnum.NEW_USER, 1)

    @_send_one.register
    async def _(self, notification: UsersConnectedToChannelNotification) -> None:
        data = {
            "usernames": [user.username for user in notification.users],
        }
        await self._send(notification.channel_id, data, NotificationTypesEnum.USERS_CONNECTED, 1)

    @_send_one.register
    async def _(self, notification: UsersLeftChannelNotification) -> None:
        data = {}
        await self._send(notification.channel_id, data, NotificationTypesEnum.USERS_LEAVE, 1)

    async def _send(self, channel_id: int, data: dict[str, Any], _type: NotificationTypesEnum, version: int) -> None:
        queue = self._get_queue(channel_id)
        if not queue:
            return

        happened_at = datetime.datetime.now(tz=datetime.timezone.utc)
        message = Message(version=version, type=_type, data=data, happened_at=happened_at, channel_id=channel_id)
        raw = message.model_dump_json()

        future = self.client.rpush(queue, raw)

        if not inspect.isawaitable(future):
            raise TypeError("Expected awaitable, got %r" % type(future))

        await future
