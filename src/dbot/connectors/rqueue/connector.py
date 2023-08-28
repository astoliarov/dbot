import inspect
from enum import Enum
from functools import singledispatchmethod
from typing import Any

import redis
from pydantic import BaseModel

from dbot.connectors.abstract import IConnector
from dbot.model.notifications import (
    NewUserInChannelNotification,
    Notification,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)


class NotificationTypesEnum(str, Enum):
    NEW_USER = "new_user"
    USERS_CONNECTED = "users_connected"
    USERS_LEFT = "users_left"


class Message(BaseModel):
    version: int
    type: NotificationTypesEnum
    data: dict[str, Any]


class RedisConnector(IConnector):
    def __init__(self, client: redis.asyncio.Redis, queue_name: str) -> None:
        self.client = client
        self.queue_name = queue_name

    async def _send(self, data: dict[str, Any], _type: NotificationTypesEnum, version: int) -> None:
        message = Message(version=version, type=_type, data=data)
        raw = message.model_dump_json()

        future = self.client.lpush(self.queue_name, raw)

        if not inspect.isawaitable(future):
            raise TypeError("Expected awaitable, got %r" % type(future))

        await future

    @singledispatchmethod
    async def send(self, notification: Notification) -> None:
        raise NotImplementedError()

    @send.register
    async def _(self, notification: NewUserInChannelNotification) -> None:
        data = {
            "username": notification.user.username,
            "id": notification.user.id,
        }
        await self._send(data, NotificationTypesEnum.NEW_USER, 1)

    @send.register
    async def _(self, notification: UsersConnectedToChannelNotification) -> None:
        data = {
            "usernames": [user.username for user in notification.users],
            "id": notification.channel_id,
        }
        await self._send(data, NotificationTypesEnum.USERS_CONNECTED, 1)

    @send.register
    async def _(self, notification: UsersLeftChannelNotification) -> None:
        data = {
            "id": notification.channel_id,
        }
        await self._send(data, NotificationTypesEnum.USERS_LEFT, 1)
