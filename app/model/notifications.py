from dataclasses import dataclass

from model.user import User


@dataclass
class Notification:
    pass


@dataclass
class UserNotification(Notification):
    user: User
    channel_id: int


@dataclass
class ChannelActivityNotification(Notification):
    channel_id: int
    users: list[User]
