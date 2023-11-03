import asyncio
import typing
from enum import Enum
from functools import singledispatchmethod
from urllib.parse import quote_plus

import structlog
from jinja2 import Template

from dbot.connectors.abstract import IConnector, NotificationTypesEnum
from dbot.connectors.webhooks.transport import WebhooksTransport
from dbot.infrastructure.monitoring import Monitoring
from dbot.model import NewUserInChannelNotification, UsersConnectedToChannelNotification
from dbot.model.config import ChannelMonitorConfig, MonitorConfig
from dbot.model.notifications import (
    Notification,
    UserLeftChannelNotification,
    UsersLeftChannelNotification,
)

logger = structlog.getLogger()


class TemplatesEnum(Enum):
    NEW_USER = "new_user_webhooks"
    USERS_CONNECTED = "users_connected_webhooks"
    USERS_LEFT = "users_left_webhooks"
    USER_LEFT = "user_left_webhooks"


class WebhooksConnector(IConnector):
    def __init__(
        self,
        transport: WebhooksTransport,
        config: MonitorConfig,
        monitoring: Monitoring,
    ):
        self.transport = transport
        self.monitoring = monitoring
        self.channels_templates = {
            config.channel_id: self._init_channel_templates(config) for config in config.channels
        }

    def _init_channel_templates(
        self, channel_config: ChannelMonitorConfig
    ) -> typing.Dict[TemplatesEnum, list[Template]]:
        if channel_config.webhooks is None:
            return {}

        webhooks_target = channel_config.webhooks

        return {
            TemplatesEnum.NEW_USER: [Template(template_str) for template_str in webhooks_target.new_user_webhooks],
            TemplatesEnum.USERS_CONNECTED: [
                Template(template_str) for template_str in webhooks_target.users_connected_webhooks
            ],
            TemplatesEnum.USERS_LEFT: [Template(template_str) for template_str in webhooks_target.users_left_webhooks],
            TemplatesEnum.USER_LEFT: [Template(template_str) for template_str in webhooks_target.user_left_webhooks],
        }

    async def send(self, notifications: list[Notification]) -> None:
        tasks = [asyncio.create_task(self._send_one(notification)) for notification in notifications]
        await asyncio.gather(*tasks)

    @singledispatchmethod
    async def _send_one(self, notification: Notification) -> None:
        raise NotImplementedError()

    @_send_one.register
    async def _(self, notification: NewUserInChannelNotification) -> None:
        data = {
            "username": notification.user.username,
            "id": notification.channel_id,
            "user_id": notification.user.id,
            "type": NotificationTypesEnum.NEW_USER.value,
        }
        await self._execute_send(data, notification.channel_id, TemplatesEnum.NEW_USER)

    @_send_one.register
    async def _(self, notification: UserLeftChannelNotification) -> None:
        data = {
            "username": notification.user.username,
            "id": notification.channel_id,
            "user_id": notification.user.id,
            "type": NotificationTypesEnum.USER_LEFT.value,
        }
        await self._execute_send(data, notification.channel_id, TemplatesEnum.USER_LEFT)

    @_send_one.register
    async def _(self, notification: UsersConnectedToChannelNotification) -> None:
        usernames = [user.username for user in notification.users]
        usernames_safe = quote_plus(",".join(usernames))

        data = {
            "usernames_safe": usernames_safe,
            "id": notification.channel_id,
            "type": NotificationTypesEnum.USERS_CONNECTED.value,
        }
        await self._execute_send(data, notification.channel_id, TemplatesEnum.USERS_CONNECTED)

    @_send_one.register
    async def _(self, notification: UsersLeftChannelNotification) -> None:
        data = {
            "id": notification.channel_id,
            "type": NotificationTypesEnum.USERS_LEFT.value,
        }
        await self._execute_send(data, notification.channel_id, TemplatesEnum.USERS_LEFT)

    async def _execute_send(self, data: dict[str, typing.Any], channel_id: int, template_type: TemplatesEnum) -> None:
        templates = self.channels_templates.get(channel_id)
        if not templates:
            return

        for template in templates[template_type]:
            link = template.render(**data)
            await self.transport.call(link)
            await self.monitoring.fire_webhooks_count()
