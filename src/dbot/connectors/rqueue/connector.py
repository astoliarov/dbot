import datetime
import inspect
from functools import singledispatchmethod
from typing import Any

import redis
from pydantic import BaseModel

from dbot.connectors.abstract import IConnector, NotificationTypesEnum
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
    happened_at: datetime.datetime


class RedisConnector(IConnector):
    def __init__(self, client: redis.asyncio.Redis, queue_name: str) -> None:
        self.client = client
        self.queue_name = queue_name

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
            "id": notification.user.id,
        }
        await self._send(data, NotificationTypesEnum.NEW_USER, 1)

    @_send_one.register
    async def _(self, notification: UsersConnectedToChannelNotification) -> None:
        data = {
            "usernames": [user.username for user in notification.users],
            "id": notification.channel_id,
        }
        await self._send(data, NotificationTypesEnum.USERS_CONNECTED, 1)

    @_send_one.register
    async def _(self, notification: UsersLeftChannelNotification) -> None:
        data = {
            "id": notification.channel_id,
        }
        await self._send(data, NotificationTypesEnum.USERS_LEAVE, 1)

    async def _send(self, data: dict[str, Any], _type: NotificationTypesEnum, version: int) -> None:
        happened_at = datetime.datetime.now(tz=datetime.timezone.utc)
        message = Message(version=version, type=_type, data=data, happened_at=happened_at)
        raw = message.model_dump_json()

        future = self.client.lpush(self.queue_name, raw)

        if not inspect.isawaitable(future):
            raise TypeError("Expected awaitable, got %r" % type(future))

        await future
