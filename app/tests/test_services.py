import datetime

import pytest
from models import ChannelInfo, User, UserActivityInfo
from services import ActivityProcessingService


@pytest.fixture
def service(mocker):
    channel_info_dao_mock = mocker.MagicMock()
    callback_service_mock = mocker.MagicMock()
    channel_configs_mock = mocker.MagicMock()

    service = ActivityProcessingService(
        channel_info_dao=channel_info_dao_mock,
        callback_service=callback_service_mock,
        channel_configs=channel_configs_mock,
    )

    return service


def test__ActivityProcessingService_process_channel__no_activity_and_user__new_notification_for_user(
    mocker, service
):
    user_1 = User(id=1, username="1")
    users = [user_1]

    activity = []

    notifications = service._get_user_activity_notifications(
        users=users, activity_info=activity
    )

    assert len(notifications) == 1
    assert notifications[0].user == user_1


def test__ActivityProcessingService_process_channel__no_activities_and_users__new_notification_for_users(
    mocker, service
):
    users = [User(id=1, username="1"), User(id=2, username="2")]

    activity = []

    notifications = service._get_user_activity_notifications(
        users=users, activity_info=activity
    )

    assert len(notifications) == 2


def test__ActivityProcessingService_process_channel__fresh_activity_and_user__no_new_notifaction(
    mocker, service
):
    users = [
        User(id=1, username="1"),
    ]

    dt = datetime.datetime.now()

    activity = [UserActivityInfo(id=1, last_seen_timestamp=int(dt.timestamp()))]

    notifications = service._get_user_activity_notifications(
        users=users, activity_info=activity
    )

    assert len(notifications) == 0


def test__ActivityProcessingService_get_user_activity_notifications__outdated_activity_and_user__new_notification(
    mocker, service
):
    user_1 = User(id=1, username="1")
    users = [user_1]
    dt = datetime.datetime.now() - datetime.timedelta(
        minutes=service.ACTIVITY_LIFETIME + 5
    )
    activity = [UserActivityInfo(id=1, last_seen_timestamp=int(dt.timestamp()))]

    notifications = service._get_user_activity_notifications(
        users=users, activity_info=activity
    )

    assert len(notifications) == 1
    assert notifications[0].user == user_1


def test__ActivityProcessingService_get_channel_new_activity_notifications__no_old_channel_info__no_channel_notification(
    mocker, service
):
    user_1 = User(id=1, username="1")
    users = [user_1]

    notification = service._get_channel_new_activity_notifications(
        users=users, channel_info=None
    )

    assert notification is None


def test__ActivityProcessingService_get_channel_new_activity_notifications__old_channel_info_outdated__no_channel_notification(
    mocker, service
):
    processing_timestamp = int(datetime.datetime.now().timestamp())
    service._get_processing_timestamp = mocker.MagicMock()
    service._get_processing_timestamp.return_value = processing_timestamp

    user_1 = User(id=1, username="1")
    users = [user_1]
    channel_info_timestamp = int(
        (datetime.datetime.now() - datetime.timedelta(hours=5)).timestamp()
    )
    channel_info = ChannelInfo(
        timestamp=channel_info_timestamp, activities=[], channel_id=1
    )

    notification = service._get_channel_new_activity_notifications(
        users=users, channel_info=channel_info
    )

    assert notification is None


def test__ActivityProcessingService_get_channel_new_activity_notifications__old_channel_info_contains_activity__no_channel_notification(
    mocker, service
):
    processing_timestamp = int(datetime.datetime.now().timestamp())
    service._get_processing_timestamp = mocker.MagicMock()
    service._get_processing_timestamp.return_value = processing_timestamp

    user_1 = User(id=1, username="1")
    users = [user_1]
    channel_info_timestamp = int(
        (datetime.datetime.now() - datetime.timedelta(minutes=5)).timestamp()
    )
    channel_info = ChannelInfo(
        timestamp=channel_info_timestamp,
        activities=[UserActivityInfo(id=1, last_seen_timestamp=channel_info_timestamp)],
        channel_id=1,
    )

    notification = service._get_channel_new_activity_notifications(
        users=users, channel_info=channel_info
    )

    assert notification is None


def test__ActivityProcessingService_get_channel_new_activity_notifications__old_channel_info_dont_have_activity_and_no_users__no_channel_notification(
    mocker, service
):
    processing_timestamp = int(datetime.datetime.now().timestamp())
    service._get_processing_timestamp = mocker.MagicMock()
    service._get_processing_timestamp.return_value = processing_timestamp

    users = []
    channel_info_timestamp = int(
        (datetime.datetime.now() - datetime.timedelta(minutes=5)).timestamp()
    )
    channel_info = ChannelInfo(
        timestamp=channel_info_timestamp,
        activities=[UserActivityInfo(id=1, last_seen_timestamp=channel_info_timestamp)],
        channel_id=1,
    )

    notification = service._get_channel_new_activity_notifications(
        users=users, channel_info=channel_info
    )

    assert notification is None


def test__ActivityProcessingService_get_channel_new_activity_notifications__old_channel_info_dont_have_activity_and_users__channel_notification(
    mocker, service
):
    processing_timestamp = int(datetime.datetime.now().timestamp())
    service._get_processing_timestamp = mocker.MagicMock()
    service._get_processing_timestamp.return_value = processing_timestamp

    users = [User(id=1, username="1")]
    channel_info_timestamp = int(
        (datetime.datetime.now() - datetime.timedelta(minutes=5)).timestamp()
    )
    channel_info = ChannelInfo(
        timestamp=channel_info_timestamp, activities=[], channel_id=1
    )

    notification = service._get_channel_new_activity_notifications(
        users=users, channel_info=channel_info
    )

    assert notification.channel_id == channel_info.channel_id
    assert notification.users == users
