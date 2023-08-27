from unittest import mock

import pytest

from dbot.connectors.webhooks import WebhookService
from dbot.model import ChannelConfig
from dbot.model.channel import Channel
from dbot.model.notifications import Notification
from dbot.monitoring import HealthChecksIOMonitoring
from dbot.repository import Repository
from dbot.services import ActivityProcessingService


@pytest.fixture
def repository():
    return mock.AsyncMock(spec=Repository)


@pytest.fixture
def monitoring():
    return mock.AsyncMock(spec=HealthChecksIOMonitoring)


@pytest.fixture
def webhooks_service():
    webhooks_service = mock.AsyncMock(spec=WebhookService)
    webhooks_service.send = mock.AsyncMock()

    return webhooks_service


@pytest.fixture
def service(repository, webhooks_service, monitoring):
    return ActivityProcessingService(
        repository=repository,
        webhooks_service=webhooks_service,
        channel_configs=[],
        monitoring=monitoring,
    )


class TestCaseService:
    async def test__process__no_errors__notification_send(self, service, repository, webhooks_service):
        configs = [
            ChannelConfig(channel_id=1, new_user_webhooks=[], users_leave_webhooks=[], users_connected_webhooks=[])
        ]
        service.channel_configs = configs

        notification = Notification()
        channel = mock.Mock(spec=Channel)
        channel.generate_notifications.return_value = [notification]

        repository.get.return_value = channel

        await service.process()

        webhooks_service.send.assert_called_once_with(notification)
