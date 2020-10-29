# coding: utf-8
import typing
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
    activities: typing.List[UserActivityInfo]


@dataclass
class Notification:
    user: User


@dataclass
class ChannelActivityNotification:
    channel_id: int
    users: typing.List[User]


@dataclass
class ChannelConfig:
    channel_id: int
    user_activity_postbacks: typing.List[str]
    channel_activity_postbacks: typing.List[str]


@dataclass
class ChannelsConfig:
    channels: typing.List[ChannelConfig]
