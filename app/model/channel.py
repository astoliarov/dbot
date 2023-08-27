from dataclasses import dataclass
from typing import Optional

from app.model.notifications import (
    NewUserInChannelNotification,
    Notification,
    UsersConnectedToChannelNotification,
    UsersLeftChannelNotification,
)
from app.model.user import User


@dataclass
class Channel:
    id: int
    users: list[User]
    previous_state: Optional["Channel"] = None

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

        return notifications

    def _get_chanel_notifications(self) -> list[Notification]:
        notifications: list[Notification] = []

        if self.previous_state is None:
            return []

        if not self.previous_state.users and self.users:
            notifications.append(UsersConnectedToChannelNotification(users=self.users, channel_id=self.id))

        if self.previous_state.users and not self.users:
            notifications.append(UsersLeftChannelNotification(channel_id=self.id))

        return notifications
