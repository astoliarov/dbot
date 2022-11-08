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
