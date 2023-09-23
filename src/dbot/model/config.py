from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TargetTypeEnum(Enum):
    WEBHOOKS = "webhooks"
    REDIS = "redis"


@dataclass
class WebhooksTargetConfig:
    new_user_webhooks: list[str]
    users_connected_webhooks: list[str]
    user_left_webhooks: list[str]
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
    webhooks: Optional[WebhooksTargetConfig]
    redis: Optional[RedisTargetConfig]

    @property
    def targets(self) -> list[Target]:
        return [target for target in (self.webhooks, self.redis) if target]


@dataclass
class MonitorConfig:
    channels: list[ChannelMonitorConfig]

    @property
    def channels_ids(self) -> set[int]:
        return {channel.channel_id for channel in self.channels}
