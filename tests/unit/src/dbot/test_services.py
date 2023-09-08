from unittest import mock

import pytest

from dbot.connectors.abstract import IConnector
from dbot.infrastructure.monitoring import HealthChecksIOMonitoring
from dbot.model import ChannelConfig
from dbot.model.channel import Channel
from dbot.model.notifications import Notification
from dbot.repository import Repository
from dbot.services import ActivityProcessingService


@pytest.fixture
def repository():
    return mock.AsyncMock(spec=Repository)


@pytest.fixture
def monitoring():
    return mock.AsyncMock(spec=HealthChecksIOMonitoring)


@pytest.fixture
def connector():
    connector = mock.AsyncMock(spec=IConnector)
    connector.send = mock.AsyncMock()

    return connector


@pytest.fixture
def service(repository, connector, monitoring):
    return ActivityProcessingService(
        repository=repository,
        connector=connector,
        channel_configs=[],
        monitoring=monitoring,
    )


class TestCaseService:
    async def test__process__no_errors__notification_send(self, service, repository, connector):
        configs = [
            ChannelConfig(channel_id=1, new_user_webhooks=[], users_leave_webhooks=[], users_connected_webhooks=[])
        ]
        service.channel_configs = configs

        notification = Notification(channel_id=1)
        channel = mock.Mock(spec=Channel)
        channel.generate_notifications.return_value = [notification]

        repository.get.return_value = channel

        await service.process()

        connector.send.assert_called_once_with([notification])
