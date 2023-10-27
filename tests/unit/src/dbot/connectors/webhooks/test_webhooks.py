from unittest.mock import Mock

import pytest

from dbot.connectors.webhooks.transport import WebhooksTransport
from dbot.connectors.webhooks.webhooks import WebhooksConnector
from dbot.model import MonitorConfig, NewUserInChannelNotification, User
from dbot.model.config import ChannelMonitorConfig, WebhooksTargetConfig
from dbot.model.notifications import (
    UserLeftChannelNotification,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)

WIREMOCK_HOST = "http://localhost:8080"


@pytest.fixture
async def config() -> MonitorConfig:
    return MonitorConfig(
        channels=[
            ChannelMonitorConfig(
                channel_id=1,
                webhooks=WebhooksTargetConfig(
                    new_user_webhooks=[
                        "http://localhost:8080/webhook-target?"
                        "channel_id={{id}}&event={{type}}&un={{username}}&uid={{user_id}}",
                    ],
                    users_connected_webhooks=[
                        "http://localhost:8080/webhook-target?"
                        "channel_id={{id}}&event={{type}}&usernames={{usernames_safe}}",
                    ],
                    user_left_webhooks=[
                        "http://localhost:8080/webhook-target?"
                        "channel_id={{id}}&event={{type}}&un={{username}}&uid={{user_id}}",
                    ],
                    users_left_webhooks=[
                        "http://localhost:8080/webhook-target?channel_id={{id}}&event={{type}}",
                    ],
                ),
                redis=None,
            )
        ]
    )


@pytest.fixture
async def transport():
    return Mock(spec=WebhooksTransport)


@pytest.fixture
async def connector(transport, config):
    return WebhooksConnector(transport, config)


class TestCaseWebhooksConnector:
    async def test__send__new_user(self, connector, transport):
        notification = NewUserInChannelNotification(
            channel_id=1,
            user=User(
                username="user1",
                id=11,
            ),
        )

        correct_webhook_path = (
            f"http://localhost:8080/webhook-target?channel_id={notification.channel_id}"
            f"&event=new_user&un={notification.user.username}&uid={notification.user.id}"
        )

        await connector.send([notification])

        transport.call.assert_called_once_with(correct_webhook_path)

    async def test__send__user_left_channel(self, transport, connector):
        notification = UserLeftChannelNotification(
            channel_id=1,
            user=User(
                username="user1",
                id=11,
            ),
        )

        correct_webhook_path = (
            f"http://localhost:8080/webhook-target?channel_id={notification.channel_id}"
            f"&event=user_left&un={notification.user.username}&uid={notification.user.id}"
        )

        await connector.send([notification])

        transport.call.assert_called_once_with(correct_webhook_path)

    async def test__send__users_connected_to_channel(self, transport, connector):
        notification = UsersConnectedToChannelNotification(
            channel_id=1, users=[User(username="user1", id=11), User(username="user2", id=12)]
        )

        correct_webhook_path = (
            f"http://localhost:8080/webhook-target?channel_id={notification.channel_id}"
            f"&event=users_connected&usernames=user1%2Cuser2"
        )

        await connector.send([notification])

        transport.call.assert_called_once_with(correct_webhook_path)

    async def test__send__users_left_channel(self, transport, connector):
        notification = UsersLeftChannelNotification(
            channel_id=1,
        )

        correct_webhook_path = (
            f"http://localhost:8080/webhook-target?channel_id={notification.channel_id}" f"&event=users_left"
        )

        await connector.send([notification])

        transport.call.assert_called_once_with(correct_webhook_path)
