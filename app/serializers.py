from models import ChannelConfig, ChannelInfo, ChannelsConfig, UserActivityInfo
from pydantic import BaseModel


class UserActivityInfoSerializer(BaseModel):
    id: int
    last_seen_timestamp: int

    def to_model(self) -> UserActivityInfo:
        return UserActivityInfo(id=self.id, last_seen_timestamp=self.last_seen_timestamp)

    @classmethod
    def from_model(cls, model: UserActivityInfo) -> "UserActivityInfoSerializer":
        return cls(
            id=model.id,
            last_seen_timestamp=model.last_seen_timestamp,
        )


class ChannelInfoSerializer(BaseModel):
    channel_id: int
    timestamp: int
    activities: list[UserActivityInfoSerializer]

    def to_model(self) -> ChannelInfo:
        return ChannelInfo(
            channel_id=self.channel_id, timestamp=self.timestamp, activities=[i.to_model() for i in self.activities]
        )

    @classmethod
    def from_model(cls, model: ChannelInfo) -> "ChannelInfoSerializer":
        return cls(
            channel_id=model.channel_id,
            timestamp=model.timestamp,
            activities=[UserActivityInfoSerializer.from_model(i) for i in model.activities],
        )


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
