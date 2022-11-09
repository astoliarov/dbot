from unittest import mock
from unittest.mock import patch

import pytest
from aioredis import Redis

from dscrd import DiscordClient
from model import User
from model.channel import Channel
from repository import Repository


@pytest.fixture
def redis_client():
    redis = mock.AsyncMock(spec=Redis)
    redis.set = mock.AsyncMock()
    return redis


@pytest.fixture
def discord_client():
    return mock.AsyncMock(spec=DiscordClient)


@pytest.fixture
def repository(redis_client, discord_client):
    return Repository(redis_client=redis_client, discord_client=discord_client)


class TestCaseRepository:
    async def test__save__state_and_key_passed_correctly(self, repository, redis_client):
        user = User(
            id=2,
            username="test",
        )
        channel = Channel(users=[user], id=1)

        with patch("repository._get_timestamp") as timestamp_mock:
            timestamp_mock.return_value = 100
            await repository.save(channel)

        redis_client.set.assert_called_once_with(
            "channel_v2_1", '{"id": 1, "ts": 100, "users": [{"username": "test", "id": 2}]}'
        )

    async def test__get__previous_state_and_users_exists__channel_built(self, repository, redis_client, discord_client):
        previous_state = '{"id": 1, "ts": 100, "users": [{"username": "test", "id": 2}]}'
        redis_client.get = mock.AsyncMock(return_value=previous_state)
        discord_client.get_channel_members = mock.Mock(return_value=[])

        with patch("repository._get_timestamp") as timestamp_mock:
            timestamp_mock.return_value = 100
            channel = await repository.get(1)

        assert channel == Channel(id=1, users=[], previous_state=Channel(id=1, users=[User(username="test", id=2)]))

    async def test__get__previous_state_outdated_and_users_exists__channel_built(
        self, repository, redis_client, discord_client
    ):
        previous_state = '{"id": 1, "ts": 100, "users": [{"username": "test", "id": 2}]}'
        redis_client.get = mock.AsyncMock(return_value=previous_state)
        discord_client.get_channel_members = mock.Mock(return_value=[])

        with patch("repository._get_timestamp") as timestamp_mock:
            timestamp_mock.return_value = 10000
            channel = await repository.get(1)

        assert channel == Channel(id=1, users=[], previous_state=None)

    async def test__get__previous_state_none_and_users_exists__channel_built(
        self, repository, redis_client, discord_client
    ):
        redis_client.get = mock.AsyncMock(return_value=None)
        discord_client.get_channel_members = mock.Mock(return_value=[])

        with patch("repository._get_timestamp") as timestamp_mock:
            timestamp_mock.return_value = 100
            channel = await repository.get(1)

        assert channel == Channel(id=1, users=[], previous_state=None)

    async def test__get__previous_state_and_no_users__channel_is_none(self, repository, redis_client, discord_client):
        previous_state = '{"id": 1, "ts": 100, "users": [{"username": "test", "id": 2}]}'
        redis_client.get = mock.AsyncMock(return_value=previous_state)
        discord_client.get_channel_members = mock.Mock(return_value=None)

        with patch("repository._get_timestamp") as timestamp_mock:
            timestamp_mock.return_value = 100
            channel = await repository.get(1)

        assert channel is None
