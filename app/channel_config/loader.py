import structlog
from model import ChannelConfig, ChannelsConfig
from pydantic import BaseModel

logger = structlog.get_logger()


class ChannelConfigSerializer(BaseModel):
    channel_id: int
    user_activity_postbacks: list[str]
    channel_activity_postbacks: list[str]

    def to_model(self) -> ChannelConfig:
        return ChannelConfig(
            channel_id=self.channel_id,
            user_activity_postbacks=self.user_activity_postbacks,
            channel_activity_postbacks=self.channel_activity_postbacks,
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
