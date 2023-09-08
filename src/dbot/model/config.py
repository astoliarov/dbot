from dataclasses import dataclass
from enum import Enum


@dataclass
class ChannelConfig:
    channel_id: int
    new_user_webhooks: list[str]
    users_connected_webhooks: list[str]
    users_leave_webhooks: list[str]


@dataclass
class ChannelsConfig:
    channels: list[ChannelConfig]


class TargetTypeEnum(Enum):
    WEBHOOKS = "webhooks"
    REDIS = "redis"


@dataclass
class WebhooksTargetConfig:
    new_user_webhooks: list[str]
    users_connected_webhooks: list[str]
    users_leave_webhooks: list[str]

    @property
    def type(self) -> TargetTypeEnum:
        return TargetTypeEnum.WEBHOOKS


@dataclass
class RedisTargetConfig:
    queue: str

    @property
    def type(self) -> TargetTypeEnum:
        return TargetTypeEnum.REDIS


Target = RedisTargetConfig | WebhooksTargetConfig


@dataclass
class ChannelMonitorConfig:
    channel_id: int
    targets: list[Target]


@dataclass
class MonitorConfig:
    channels: list[ChannelMonitorConfig]
