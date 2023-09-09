from unittest import mock

import pytest

from dbot.connectors.router import NotificationRouter
from dbot.infrastructure.monitoring import HealthChecksIOMonitoring
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
def router():
    connector = mock.AsyncMock(spec=NotificationRouter)
    connector.send = mock.AsyncMock()

    return connector


@pytest.fixture
def service(repository, router, monitoring):
    return ActivityProcessingService(
        repository=repository,
        router=router,
        channels=set(),
        monitoring=monitoring,
    )


class TestCaseService:
    async def test__process__no_errors__notification_send(self, service, repository, router):
        service.channels = {1}

        notification = Notification(channel_id=1)
        channel = mock.Mock(spec=Channel)
        channel.generate_notifications.return_value = [notification]

        repository.get.return_value = channel

        await service.process()

        router.send.assert_called_once_with([notification])
