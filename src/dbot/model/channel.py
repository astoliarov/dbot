import typing
from dataclasses import dataclass

import structlog

from dbot.model.notifications import (
    NewUserInChannelNotification,
    Notification,
    UserLeftChannelNotification,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)
from dbot.model.user import User

logger = structlog.get_logger(__name__)


@dataclass
class Channel:
    id: int
    users: list[User]
    previous_state: typing.Optional["Channel"] = None

    def generate_notifications(self) -> list[Notification]:
        notifications = self._get_user_notifications()
        notifications.extend(self._get_chanel_notifications())
        return notifications

    def _get_user_notifications(self) -> list[Notification]:
        notifications: list[Notification] = []

        if self.previous_state is None:
            return []

        old_users = {user.id: user for user in self.previous_state.users}
        new_users = {user.id: user for user in self.users}

        for user_id, user in new_users.items():
            old_user = old_users.get(user_id)
            if not old_user:
                notifications.append(NewUserInChannelNotification(user=user, channel_id=self.id))
                logger.info("NewUserInChannelNotification.generated", old_users=old_users, new_users=new_users)

        for user_id, user in old_users.items():
            if user_id not in new_users:
                notifications.append(UserLeftChannelNotification(user=user, channel_id=self.id))
                logger.info("UserLeftChannelNotification.generated", old_users=old_users, new_users=new_users)

        return notifications

    def _get_chanel_notifications(self) -> list[Notification]:
        notifications: list[Notification] = []

        if self.previous_state is None:
            return []

        if not self.previous_state.users and self.users:
            notifications.append(UsersConnectedToChannelNotification(users=self.users, channel_id=self.id))
            logger.info(
                "UsersConnectedToChannelNotification.generated",
                old_users=self.previous_state.users,
                new_users=self.users,
            )

        if self.previous_state.users and not self.users:
            notifications.append(UsersLeftChannelNotification(channel_id=self.id))
            logger.info(
                "UsersLeftChannelNotification.generated", old_users=self.previous_state.users, new_users=self.users
            )

        return notifications
