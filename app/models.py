from dataclasses import dataclass


@dataclass
class User:
    username: str
    id: int


@dataclass
class UserActivityInfo:
    id: int
    last_seen_timestamp: int


@dataclass
class ChannelInfo:
    channel_id: int
    timestamp: int
    activities: list[UserActivityInfo]


@dataclass
class Notification:
    user: User


@dataclass
class ChannelActivityNotification:
    channel_id: int
    users: list[User]


@dataclass
class ChannelConfig:
    channel_id: int
    user_activity_postbacks: list[str]
    channel_activity_postbacks: list[str]


@dataclass
class ChannelsConfig:
    channels: list[ChannelConfig]
