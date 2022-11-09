import typing
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


class CallbackService:
    def __init__(self, channels_config: list[ChannelConfig]):
        self.session = aiohttp.ClientSession()
        self.channels_templates = {
            config.channel_id: self._init_channel_templates(config) for config in channels_config
        }

    def _init_channel_templates(self, channel_config: ChannelConfig) -> typing.Dict[str, list[Template]]:
        return {
            "user_activity_postbacks": [
                Template(template_str) for template_str in channel_config.user_activity_postbacks
            ],
            "channel_activity_postbacks": [
                Template(template_str) for template_str in channel_config.channel_activity_postbacks
            ],
        }

    @singledispatchmethod
    async def send(self, notification: Notification) -> None:
        raise NotImplementedError()

    @send.register
    async def _(self, notification: NewUserInChannelNotification) -> None:
        data = {
            "username": notification.user.username,
            "id": notification.user.id,
        }
        templates = self.channels_templates.get(notification.channel_id)
        if not templates:
            return

        for template in templates["user_activity_postbacks"]:
            link = template.render(**data)
            await self._make_call(link)

    @send.register
    async def _(self, notification: UsersConnectedToChannelNotification) -> None:
        usernames = [user.username for user in notification.users]
        usernames_safe = quote_plus(",".join(usernames))

        data = {
            "usernames_safe": usernames_safe,
            "id": notification.channel_id,
        }
        templates = self.channels_templates.get(notification.channel_id)
        if not templates:
            return

        for template in templates["channel_activity_postbacks"]:
            link = template.render(**data)
            await self._make_call(link)

    @send.register
    async def _(self, notification: UsersLeftChannelNotification) -> None:
        logger.debug("received notification", notification=notification)
        ...

    async def _make_call(self, link: str) -> None:
        try:
            await self.session.get(link, allow_redirects=True)
        except Exception as e:
            capture_exception(e)
            logger.info(e)
