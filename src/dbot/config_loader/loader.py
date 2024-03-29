import structlog
from pydantic import BaseModel

from dbot.model.config import (
    ChannelMonitorConfig,
    MonitorConfig,
    RedisTargetConfig,
    WebhooksTargetConfig,
)

logger = structlog.get_logger()


class WebhooksTargetConfigSerializer(BaseModel):
    new_user_webhooks: list[str] | None = None
    users_connected_webhooks: list[str] | None = None
    users_left_webhooks: list[str] | None = None
    user_left_webhooks: list[str] | None = None

    def to_model(self) -> WebhooksTargetConfig:
        return WebhooksTargetConfig(
            new_user_webhooks=self.new_user_webhooks or [],
            users_connected_webhooks=self.users_connected_webhooks or [],
            users_left_webhooks=self.users_left_webhooks or [],
            user_left_webhooks=self.user_left_webhooks or [],
        )


class RedisTargetConfigSerializer(BaseModel):
    queue: str

    def to_model(self) -> RedisTargetConfig:
        return RedisTargetConfig(
            queue=self.queue,
        )


class ChannelMonitorConfigSerializer(BaseModel):
    channel_id: int
    webhooks: WebhooksTargetConfigSerializer | None = None
    redis_queues: list[RedisTargetConfigSerializer] | None = None

    def to_model(self) -> ChannelMonitorConfig:
        return ChannelMonitorConfig(
            channel_id=self.channel_id,
            webhooks=self.webhooks.to_model() if self.webhooks else None,
            redis_queues=[item.to_model() for item in self.redis_queues] if self.redis_queues else [],
        )


class MonitorConfigSerializer(BaseModel):
    channels: list[ChannelMonitorConfigSerializer]

    def to_model(self) -> MonitorConfig:
        return MonitorConfig(channels=[c.to_model() for c in self.channels])


class JSONLoader:
    def from_string(self, raw: str) -> MonitorConfig:
        serializer = MonitorConfigSerializer.model_validate_json(raw)

        config = serializer.to_model()
        logger.debug("config.loaded", config=config)

        return serializer.to_model()

    def from_file(self, path: str) -> MonitorConfig:
        with open(path, "r") as f:
            raw = f.read()

        return self.from_string(raw)
