import json
from unittest import mock

import pytest
import redis

from dbot.connectors.rqueue.connector import RedisConnector
from dbot.model import User
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
def connector(client):
    return RedisConnector(client, TEST_QUEUE_NAME)


async def test__send__new_user_in_channel(connector):
    notification = NewUserInChannelNotification(
        user=User(username="test", id=1),
        channel_id=1,
    )

    await connector.send(notification)

    connector.client.lpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"new_user","data":{"username":"test","id":1}}',
    )


async def test__send__users_connected_to_channel(connector):
    notification = UsersConnectedToChannelNotification(
        users=[
            User(username="test1", id=1),
            User(username="test2", id=2),
        ],
        channel_id=1,
    )

    await connector.send(notification)

    connector.client.lpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"users_connected","data":{"usernames":["test1","test2"],"id":1}}',
    )


async def test__send__users_left_channel(connector):
    notification = UsersLeftChannelNotification(
        channel_id=1,
    )

    await connector.send(notification)

    connector.client.lpush.assert_called_once_with(
        TEST_QUEUE_NAME,
        '{"version":1,"type":"users_left","data":{"id":1}}',
    )
