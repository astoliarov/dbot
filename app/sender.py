import typing
from enum import Enum
from functools import singledispatchmethod
from urllib.parse import quote_plus

import aiohttp
import structlog
from jinja2 import Template
from sentry_sdk import capture_exception

from model import (
    ChannelConfig,
    NewUserInChannelNotification,
    UsersConnectedToChannelNotification,
)
from model.notifications import Notification, UsersLeftChannelNotification

logger = structlog.getLogger()


class NotificationTypesEnum(Enum):
    NEW_USER = "new_user"
    USERS_CONNECTED = "users_connected"
    USERS_LEAVE = "users_leave"


class CallbackService:
    def __init__(self, channels_config: list[ChannelConfig]):
        self.session = aiohttp.ClientSession()
        self.channels_templates = {
            config.channel_id: self._init_channel_templates(config) for config in channels_config
        }

    def _init_channel_templates(self, channel_config: ChannelConfig) -> typing.Dict[str, list[Template]]:
        return {
            "new_user_webhooks": [Template(template_str) for template_str in channel_config.new_user_webhooks],
            "users_connected_webhook": [
                Template(template_str) for template_str in channel_config.users_connected_webhook
            ],
            "users_leave_webhook": [Template(template_str) for template_str in channel_config.users_leave_webhook],
        }

    @singledispatchmethod
    async def send(self, notification: Notification) -> None:
        raise NotImplementedError()

    @send.register
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
            await self._make_call(link)

    @send.register
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

        for template in templates["users_connected_webhook"]:
            link = template.render(**data)
            await self._make_call(link)

    @send.register
    async def _(self, notification: UsersLeftChannelNotification) -> None:

        data = {
            "id": notification.channel_id,
            "type": NotificationTypesEnum.USERS_LEAVE.value,
        }
        templates = self.channels_templates.get(notification.channel_id)
        if not templates:
            return

        for template in templates["users_leave_webhook"]:
            link = template.render(**data)
            await self._make_call(link)

    async def _make_call(self, link: str) -> None:
        try:
            await self.session.get(link, allow_redirects=True)
        except Exception as e:
            capture_exception(e)
            logger.info(e)
