from dataclasses import dataclass

from app.model.user import User


@dataclass
class Notification:
    pass


@dataclass
class NewUserInChannelNotification(Notification):
    user: User
    channel_id: int


@dataclass
class UsersConnectedToChannelNotification(Notification):
    channel_id: int
    users: list[User]


@dataclass
class UsersLeftChannelNotification(Notification):
    channel_id: int
