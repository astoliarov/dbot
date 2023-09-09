import json
from unittest import mock

import freezegun
import pytest
import redis

from dbot.connectors.rqueue.connector import RedisConnector
from dbot.model import MonitorConfig, User
from dbot.model.config import ChannelMonitorConfig, RedisTargetConfig
from dbot.model.notifications import (
    NewUserInChannelNotification,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)

TEST_QUEUE_NAME = "test_queue"


@pytest.fixture
def client():
    return mock.AsyncMock()


@pytest.fixture
def time_freeze():
    with freezegun.freeze_time("2023-10-10T10:10:10"):
        yield


@pytest.fixture
def connector(client):
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
    )


async def test__send__new_user_in_channel(connector, time_freeze):
    notification = NewUserInChannelNotification(
        user=User(username="test", id=1),
        channel_id=1,
    )

    await connector.send([notification])

    connector.client.lpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"new_user","data":{"username":"test","id":1},' '"happened_at":"2023-10-10T10:10:10Z"}',
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

    connector.client.lpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"users_connected","data":{"usernames":["test1","test2"],"id":1},'
        '"happened_at":"2023-10-10T10:10:10Z"}',
    )


async def test__send__users_left_channel(connector, time_freeze):
    notification = UsersLeftChannelNotification(
        channel_id=1,
    )

    await connector.send([notification])

    connector.client.lpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"users_leave","data":{"id":1},' '"happened_at":"2023-10-10T10:10:10Z"}',
    )
