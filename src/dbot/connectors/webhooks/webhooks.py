import asyncio
import typing
from functools import singledispatchmethod
from urllib.parse import quote_plus

import structlog
from jinja2 import Template

from dbot.connectors.abstract import IConnector, NotificationTypesEnum
from dbot.connectors.webhooks.transport import WebhooksTransport
from dbot.model import (
    ChannelConfig,
    NewUserInChannelNotification,
    UsersConnectedToChannelNotification,
)
from dbot.model.notifications import Notification, UsersLeftChannelNotification

logger = structlog.getLogger()


class WebhookService(IConnector):
    def __init__(self, channels_config: list[ChannelConfig], transport: WebhooksTransport):
        self.transport = transport
        self.channels_templates = {
            config.channel_id: self._init_channel_templates(config) for config in channels_config
        }

    def _init_channel_templates(self, channel_config: ChannelConfig) -> typing.Dict[str, list[Template]]:
        return {
            "new_user_webhooks": [Template(template_str) for template_str in channel_config.new_user_webhooks],
            "users_connected_webhooks": [
                Template(template_str) for template_str in channel_config.users_connected_webhooks
            ],
            "users_leave_webhooks": [Template(template_str) for template_str in channel_config.users_leave_webhooks],
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
            "id": notification.user.id,
            "type": NotificationTypesEnum.NEW_USER.value,
        }
        templates = self.channels_templates.get(notification.channel_id)
        if not templates:
            return

        for template in templates["new_user_webhooks"]:
            link = template.render(**data)
            await self.transport.call(link)

    @_send_one.register
    async def _(self, notification: UsersConnectedToChannelNotification) -> None:
        usernames = [user.username for user in notification.users]
        usernames_safe = quote_plus(",".join(usernames))

        data = {
            "usernames_safe": usernames_safe,
            "id": notification.channel_id,
            "type": NotificationTypesEnum.USERS_CONNECTED.value,
        }
        templates = self.channels_templates.get(notification.channel_id)
        if not templates:
            return

        for template in templates["users_connected_webhooks"]:
            link = template.render(**data)
            await self.transport.call(link)

    @_send_one.register
    async def _(self, notification: UsersLeftChannelNotification) -> None:
        data = {
            "id": notification.channel_id,
            "type": NotificationTypesEnum.USERS_LEAVE.value,
        }
        templates = self.channels_templates.get(notification.channel_id)
        if not templates:
            return

        for template in templates["users_leave_webhooks"]:
            link = template.render(**data)
            await self.transport.call(link)
