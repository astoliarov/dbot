from unittest import mock

import pytest
from model import ChannelConfig
from model.channel import Channel
from model.notifications import Notification
from monitoring import HealthChecksIOMonitoring
from repository import Repository
from sender import CallbackService
from services import ActivityProcessingService


@pytest.fixture
def repository():
    return mock.AsyncMock(spec=Repository)


@pytest.fixture
def monitoring():
    return mock.AsyncMock(spec=HealthChecksIOMonitoring)


@pytest.fixture
def callback_service():
    callback_service = mock.AsyncMock(spec=CallbackService)
    callback_service.send = mock.AsyncMock()

    return callback_service


@pytest.fixture
def service(repository, callback_service, monitoring):
    return ActivityProcessingService(
        repository=repository, callback_service=callback_service, channel_configs=[], monitoring=monitoring
    )


class TestCaseService:
    async def test__process__no_errors__notification_send(self, service, repository, callback_service):
        configs = [ChannelConfig(channel_id=1, user_activity_postbacks=[], channel_activity_postbacks=[])]
        service.channel_configs = configs

        notification = Notification()
        channel = mock.Mock(spec=Channel)
        channel.generate_notifications.return_value = [notification]

        repository.get.return_value = channel

        await service.process()

        callback_service.send.assert_called_once_with(notification)
