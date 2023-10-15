import pytest
from aiohttp import ClientSession
from integration.clients.wiremock import WireMockClient

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
async def wiremock():
    client = WireMockClient(WIREMOCK_HOST)
    await client.reset()
    return client


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
async def connector(config):
    transport = WebhooksTransport(ClientSession(), raise_errors=True)
    return WebhooksConnector(transport, config)


class TestCaseWebhooksConnector:
    async def test__send__new_user_no_reraise_and_error__no_error(self, wiremock, config):
        transport = WebhooksTransport(ClientSession(), raise_errors=False)
        connector = WebhooksConnector(transport, config)

        connector.transport.raise_errors = False
        notification = NewUserInChannelNotification(
            channel_id=1,
            user=User(
                username="user1",
                id=11,
            ),
        )

        await connector.send([notification])

    async def test__send__new_user_reraise_and_error__error_risen(self, wiremock, config):
        transport = WebhooksTransport(ClientSession(), raise_errors=True)
        connector = WebhooksConnector(transport, config)

        notification = NewUserInChannelNotification(
            channel_id=1,
            user=User(
                username="user1",
                id=11,
            ),
        )

        with pytest.raises(Exception):
            await connector.send([notification])

    async def test__send__new_user(self, wiremock, connector):
        notification = NewUserInChannelNotification(
            channel_id=1,
            user=User(
                username="user1",
                id=11,
            ),
        )

        correct_webhook_path = (
            f"/webhook-target?channel_id={notification.channel_id}"
            f"&event=new_user&un={notification.user.username}&uid={notification.user.id}"
        )

        await wiremock.set_stub(correct_webhook_path, {"status": "ok"}, method="GET", status=200)

        await connector.send([notification])

    async def test__send__user_left_channel(self, wiremock, connector):
        notification = UserLeftChannelNotification(
            channel_id=1,
            user=User(
                username="user1",
                id=11,
            ),
        )

        correct_webhook_path = (
            f"/webhook-target?channel_id={notification.channel_id}"
            f"&event=user_left&un={notification.user.username}&uid={notification.user.id}"
        )

        await wiremock.set_stub(correct_webhook_path, {"status": "ok"}, method="GET", status=200)

        await connector.send([notification])

    async def test__send__users_connected_to_channel(self, wiremock, connector):
        notification = UsersConnectedToChannelNotification(
            channel_id=1, users=[User(username="user1", id=11), User(username="user2", id=12)]
        )

        correct_webhook_path = (
            f"/webhook-target?channel_id={notification.channel_id}" f"&event=users_connected&usernames=user1,user2"
        )

        await wiremock.set_stub(correct_webhook_path, {"status": "ok"}, method="GET", status=200)

        await connector.send([notification])

    async def test__send__users_left_channel(self, wiremock, connector):
        notification = UsersLeftChannelNotification(
            channel_id=1,
        )

        correct_webhook_path = f"/webhook-target?channel_id={notification.channel_id}" f"&event=users_left"

        await wiremock.set_stub(correct_webhook_path, {"status": "ok"}, method="GET", status=200)

        await connector.send([notification])
