from dataclasses import dataclass

from dbot.model.user import User


@dataclass
class Notification:
    channel_id: int


@dataclass
class NewUserInChannelNotification(Notification):
    user: User


@dataclass
class UsersConnectedToChannelNotification(Notification):
    users: list[User]


@dataclass
class UsersLeftChannelNotification(Notification):
    ...
