from typing import Optional

import structlog
from model import ChannelConfig, ChannelsConfig
from pydantic import BaseModel

logger = structlog.get_logger()


class ChannelConfigSerializer(BaseModel):
    channel_id: int
    new_user_webhooks: list[str]
    users_connected_webhooks: list[str]
    users_leave_webhooks: Optional[list[str]]

    def to_model(self) -> ChannelConfig:
        return ChannelConfig(
            channel_id=self.channel_id,
            new_user_webhooks=self.new_user_webhooks,
            users_connected_webhooks=self.users_connected_webhooks,
            users_leave_webhooks=self.users_leave_webhooks or [],
        )


class ConfigSerializer(BaseModel):
    channels: list[ChannelConfigSerializer]

    def to_model(self):
        return ChannelsConfig(channels=[c.to_model() for c in self.channels])


class JSONLoader:
    def from_file(self, path: str) -> ChannelsConfig:
        with open(path, "r") as f:
            raw = f.read()

        serializer = ConfigSerializer.parse_raw(raw)

        config = serializer.to_model()
        logger.debug("loaded config", config=config)

        return serializer.to_model()
