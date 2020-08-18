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
