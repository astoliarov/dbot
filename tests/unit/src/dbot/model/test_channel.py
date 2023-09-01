from dbot.model import (
    NewUserInChannelNotification,
    User,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)
from dbot.model.channel import Channel


class TestCaseChannel:
    def test__generate_notifications__no_previous_state__no_notifications(self):
        user = User(username="test", id=1)

        channel = Channel(id=1, users=[user], previous_state=None)

        notifications = channel.generate_notifications()

        assert notifications == []

    def test__generate_notifications__new_user_in_channel__notifications_correct(self):
        user = User(username="test", id=1)

        previous_channel_state = Channel(users=[], id=1)

        channel = Channel(id=1, users=[user], previous_state=previous_channel_state)

        notifications = channel.generate_notifications()

        assert notifications == [
            NewUserInChannelNotification(user=user, channel_id=channel.id),
            UsersConnectedToChannelNotification(users=channel.users, channel_id=channel.id),
        ]

    def test__generate_notifications__new_user_connected_to_channel_with_users__notifications_correct(
        self,
    ):
        user = User(username="test", id=1)
        user_2 = User(username="test_2", id=2)

        previous_channel_state = Channel(users=[user], id=1)

        channel = Channel(id=1, users=[user, user_2], previous_state=previous_channel_state)

        notifications = channel.generate_notifications()

        assert notifications == [
            NewUserInChannelNotification(user=user_2, channel_id=channel.id),
        ]

    def test__generate_notifications__users_left_channel__notifications_correct(self):
        user = User(username="test", id=1)

        previous_channel_state = Channel(users=[user], id=1)

        channel = Channel(id=1, users=[], previous_state=previous_channel_state)

        notifications = channel.generate_notifications()

        assert notifications == [
            UsersLeftChannelNotification(channel_id=channel.id),
        ]
