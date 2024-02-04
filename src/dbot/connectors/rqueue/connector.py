import asyncio
import datetime
import inspect
from collections import defaultdict
from functools import singledispatchmethod
from typing import Any

import redis
from pydantic import BaseModel

from dbot.connectors.abstract import IConnector, NotificationTypesEnum
from dbot.infrastructure.monitoring import Monitoring
from dbot.model import MonitorConfig
from dbot.model.notifications import (
    NewUserInChannelNotification,
    Notification,
    UserLeftChannelNotification,
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
    def __init__(self, client: redis.asyncio.Redis, config: MonitorConfig, monitoring: Monitoring) -> None:
        self.client = client
        self.config = config
        self.monitoring = monitoring

        self.channel_queue_map: dict[int, list[str]] = self._prepare_queues_for_channels(config)

    def _prepare_queues_for_channels(self, config: MonitorConfig) -> dict[int, list[str]]:
        channel_queue_map = defaultdict(list)

        for channel in config.channels:
            if channel.redis_queues is None:
                continue

            for target in channel.redis_queues:
                channel_queue_map[channel.channel_id].append(target.queue)

        return channel_queue_map

    def _get_queue(self, channel_id: int) -> list[str] | None:
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
            "id": notification.user.id,
            "username": notification.user.username,
        }
        await self._send(notification.channel_id, data, NotificationTypesEnum.NEW_USER, 1)

    @_send_one.register
    async def _(self, notification: UserLeftChannelNotification) -> None:
        data = {
            "id": notification.user.id,
            "username": notification.user.username,
        }
        await self._send(notification.channel_id, data, NotificationTypesEnum.USER_LEFT, 1)

    @_send_one.register
    async def _(self, notification: UsersConnectedToChannelNotification) -> None:
        data = {
            "usernames": [user.username for user in notification.users],
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                }
                for user in notification.users
            ],
        }
        await self._send(notification.channel_id, data, NotificationTypesEnum.USERS_CONNECTED, 1)

    @_send_one.register
    async def _(self, notification: UsersLeftChannelNotification) -> None:
        data: dict[Any, Any] = {}
        await self._send(notification.channel_id, data, NotificationTypesEnum.USERS_LEFT, 1)

    async def _send(self, channel_id: int, data: dict[str, Any], _type: NotificationTypesEnum, version: int) -> None:
        queues = self._get_queue(channel_id)
        if not queues:
            return

        happened_at = datetime.datetime.now(tz=datetime.timezone.utc)
        message = Message(version=version, type=_type, data=data, happened_at=happened_at, channel_id=channel_id)
        raw = message.model_dump_json()

        futures = []
        for queue in queues:
            future = self.client.rpush(queue, raw)

            if not inspect.isawaitable(future):
                raise TypeError(f"Expected awaitable, got {type(future)}")

            futures.append(future)

        await asyncio.gather(*futures)

        await self.monitoring.fire_redis_events_count()
