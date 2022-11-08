from dataclasses import dataclass


@dataclass
class ChannelConfig:
    channel_id: int
    user_activity_postbacks: list[str]
    channel_activity_postbacks: list[str]


@dataclass
class ChannelsConfig:
    channels: list[ChannelConfig]
