from unittest import mock

import freezegun
import pytest

from dbot.connectors.rqueue.connector import RedisConnector
from dbot.infrastructure.monitoring import Monitoring
from dbot.model import MonitorConfig, User
from dbot.model.config import ChannelMonitorConfig, RedisTargetConfig
from dbot.model.notifications import (
    NewUserInChannelNotification,
    UserLeftChannelNotification,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)

TEST_QUEUE_NAME = "test_queue"


@pytest.fixture
def client():
    return mock.AsyncMock()


@pytest.fixture
async def monitoring():
    return mock.AsyncMock(spec=Monitoring)


@pytest.fixture
def time_freeze():
    with freezegun.freeze_time("2023-10-10T10:10:10"):
        yield


@pytest.fixture
def connector(client, monitoring):
    return RedisConnector(
        client,
        MonitorConfig(
            channels=[
                ChannelMonitorConfig(
                    channel_id=1,
                    redis=RedisTargetConfig(
                        queue=TEST_QUEUE_NAME,
                    ),
                    webhooks=None,
                )
            ]
        ),
        monitoring,
    )


async def test__send__new_user_in_channel(connector, time_freeze):
    notification = NewUserInChannelNotification(
        user=User(username="test", id=1),
        channel_id=1,
    )

    await connector.send([notification])

    connector.client.rpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"new_user","data":{"id":1,"username":"test"},"channel_id":1,"happened_at":"2023-10-10T10:10:10Z"}',
    )


async def test__send__users_connected_to_channel(connector, time_freeze):
    notification = UsersConnectedToChannelNotification(
        users=[
            User(username="test1", id=1),
            User(username="test2", id=2),
        ],
        channel_id=1,
    )

    await connector.send([notification])

    connector.client.rpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"users_connected","data":{"usernames":["test1","test2"],"users":[{"id":1,"username":"test1"},{"id":2,"username":"test2"}]},'
        '"channel_id":1,"happened_at":"2023-10-10T10:10:10Z"}',
    )


async def test__send__users_left_channel(connector, time_freeze):
    notification = UsersLeftChannelNotification(
        channel_id=1,
    )

    await connector.send([notification])

    connector.client.rpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"users_left","data":{},"channel_id":1,"happened_at":"2023-10-10T10:10:10Z"}',
    )


async def test__send__user_left_channel(connector, time_freeze):
    notification = UserLeftChannelNotification(channel_id=1, user=User(username="test_user", id=1))

    await connector.send([notification])

    connector.client.rpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"user_left","data":{"id":1,"username":"test_user"},"channel_id":1,"happened_at":"2023-10-10T10:10:10Z"}',
    )
