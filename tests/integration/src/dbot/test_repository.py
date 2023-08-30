import json

import pytest
import redis

from dbot.connectors.rqueue.connector import RedisConnector
from dbot.infrastructure.config import redis_config_instance
from dbot.model import (
    NewUserInChannelNotification,
    User,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)
from dbot.repository import open_redis


@pytest.fixture()
async def client() -> redis.Redis:
    return await open_redis(redis_config_instance.url)


@pytest.fixture()
async def connector(client):
    return RedisConnector(client, "test_queue")


class TestCaseCommon:
    async def test__send__called_twice__twice_sent_to_redis(self, connector, client):
        await connector.send(NewUserInChannelNotification(User(id=1, username="test_user"), 1))
        await connector.send(NewUserInChannelNotification(User(id=2, username="test_user_2"), 1))

        raw_message_1 = await client.rpop("test_queue")
        raw_message_2 = await client.rpop("test_queue")

        assert json.loads(raw_message_1.decode("utf-8")) == {
            "data": {"id": 1, "username": "test_user"},
            "type": "new_user",
            "version": 1,
        }

        assert json.loads(raw_message_2.decode("utf-8")) == {
            "data": {"id": 2, "username": "test_user_2"},
            "type": "new_user",
            "version": 1,
        }


class TestCaseSendDifferentTypes:
    async def test__send__new_user__sent_to_redis(self, connector, client):
        await connector.send(NewUserInChannelNotification(User(id=1, username="test_user"), 1))

        raw_data = await client.rpop("test_queue")

        data = json.loads(raw_data.decode("utf-8"))

        assert data == {"data": {"id": 1, "username": "test_user"}, "type": "new_user", "version": 1}

    async def test__send__users_connected_to_channel__sent_to_redis(self, connector, client):
        await connector.send(
            UsersConnectedToChannelNotification(users=[User(id=1, username="test_user")], channel_id=1)
        )

        raw_data = await client.rpop("test_queue")

        data = json.loads(raw_data.decode("utf-8"))

        assert data == {"data": {"id": 1, "usernames": ["test_user"]}, "type": "users_connected", "version": 1}

    async def test__send__users_left_channel__sent_to_redis(self, connector, client):
        await connector.send(UsersLeftChannelNotification(channel_id=1))

        raw_data = await client.rpop("test_queue")

        data = json.loads(raw_data.decode("utf-8"))

        assert data == {"data": {"id": 1}, "type": "users_left", "version": 1}
