from dataclasses import dataclass
from enum import Enum


class TargetTypeEnum(Enum):
    WEBHOOKS = "webhooks"
    REDIS = "redis"


@dataclass
class WebhooksTargetConfig:
    new_user_webhooks: list[str]
    users_connected_webhooks: list[str]
    user_left_webhooks: list[str]
    users_left_webhooks: list[str]

    @property
    def type(self) -> TargetTypeEnum:
        return TargetTypeEnum.WEBHOOKS


@dataclass
class RedisTargetConfig:
    queue: str

    @property
    def type(self) -> TargetTypeEnum:
        return TargetTypeEnum.REDIS


@dataclass
class ChannelMonitorConfig:
    channel_id: int
    webhooks: WebhooksTargetConfig | None
    redis_queues: list[RedisTargetConfig] | None

    @property
    def available_target_types(self) -> list[TargetTypeEnum]:
        targets = []

        if self.webhooks:
            targets.append(TargetTypeEnum.WEBHOOKS)

        if self.redis_queues:
            targets.append(TargetTypeEnum.REDIS)

        return targets


@dataclass
class MonitorConfig:
    channels: list[ChannelMonitorConfig]

    @property
    def channels_ids(self) -> set[int]:
        return {channel.channel_id for channel in self.channels}
