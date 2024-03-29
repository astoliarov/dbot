import json

import freezegun
import pytest
import redis

from dbot.connectors.rqueue.connector import RedisConnector
from dbot.infrastructure.config import redis_config_instance
from dbot.infrastructure.monitoring import Monitoring, PrometheusMonitoring
from dbot.model import (
    MonitorConfig,
    NewUserInChannelNotification,
    User,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)
from dbot.model.config import ChannelMonitorConfig, RedisTargetConfig
from dbot.model.notifications import UserLeftChannelNotification
from dbot.repository import open_redis


@pytest.fixture()
async def client() -> redis.Redis:
    return await open_redis(redis_config_instance.url)


@pytest.fixture
async def monitoring() -> Monitoring:
    PrometheusMonitoring.clear()

    prometheus_monitoring = PrometheusMonitoring(True)
    return Monitoring(None, prometheus_monitoring)


@pytest.fixture()
async def connector(client, monitoring):
    return RedisConnector(
        client,
        MonitorConfig(
            channels=[
                ChannelMonitorConfig(
                    channel_id=1,
                    redis_queues=[
                        RedisTargetConfig(
                            queue="test_queue",
                        )
                    ],
                    webhooks=None,
                )
            ]
        ),
        monitoring,
    )


@pytest.fixture
def time_freeze():
    with freezegun.freeze_time("2023-10-10T10:10:10"):
        yield


class TestCaseCommon:
    async def test__send__called_twice__twice_sent_to_redis(self, connector, client, time_freeze):
        await connector.send(
            [
                NewUserInChannelNotification(user=User(id=1, username="test_user"), channel_id=1),
                NewUserInChannelNotification(user=User(id=2, username="test_user_2"), channel_id=1),
            ]
        )

        raw_message_1 = await client.lpop("test_queue")
        raw_message_2 = await client.lpop("test_queue")

        assert json.loads(raw_message_1.decode("utf-8")) == {
            "data": {"id": 1, "username": "test_user"},
            "type": "new_user",
            "version": 1,
            "channel_id": 1,
            "happened_at": "2023-10-10T10:10:10Z",
        }

        assert json.loads(raw_message_2.decode("utf-8")) == {
            "data": {"id": 2, "username": "test_user_2"},
            "type": "new_user",
            "version": 1,
            "channel_id": 1,
            "happened_at": "2023-10-10T10:10:10Z",
        }


class TestCaseSendDifferentTypes:
    async def test__send__new_user__sent_to_redis(self, connector, client, time_freeze):
        await connector.send([NewUserInChannelNotification(user=User(id=1, username="test_user"), channel_id=1)])

        raw_data = await client.lpop("test_queue")

        data = json.loads(raw_data.decode("utf-8"))

        assert data == {
            "data": {"id": 1, "username": "test_user"},
            "type": "new_user",
            "version": 1,
            "channel_id": 1,
            "happened_at": "2023-10-10T10:10:10Z",
        }

    async def test__send__users_connected_to_channel__sent_to_redis(self, connector, client, time_freeze):
        await connector.send(
            [UsersConnectedToChannelNotification(users=[User(id=1, username="test_user")], channel_id=1)]
        )

        raw_data = await client.lpop("test_queue")

        data = json.loads(raw_data.decode("utf-8"))

        assert data == {
            "data": {
                "users": [
                    {
                        "id": 1,
                        "username": "test_user",
                    }
                ],
                "usernames": ["test_user"],
            },
            "channel_id": 1,
            "type": "users_connected",
            "version": 1,
            "happened_at": "2023-10-10T10:10:10Z",
        }

    async def test__send__users_left_channel__sent_to_redis(self, connector, client, time_freeze):
        await connector.send([UsersLeftChannelNotification(channel_id=1)])

        raw_data = await client.lpop("test_queue")

        data = json.loads(raw_data.decode("utf-8"))

        assert data == {
            "data": {},
            "channel_id": 1,
            "type": "users_left",
            "version": 1,
            "happened_at": "2023-10-10T10:10:10Z",
        }

    async def test__send__user_left_channel__sent_to_redis(self, connector, client, time_freeze):
        await connector.send([UserLeftChannelNotification(channel_id=1, user=User(id=1, username="test_user"))])

        raw_data = await client.lpop("test_queue")

        data = json.loads(raw_data.decode("utf-8"))

        assert data == {
            "data": {
                "id": 1,
                "username": "test_user",
            },
            "channel_id": 1,
            "type": "user_left",
            "version": 1,
            "happened_at": "2023-10-10T10:10:10Z",
        }
