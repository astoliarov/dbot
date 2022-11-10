from dataclasses import dataclass


@dataclass
class ChannelConfig:
    channel_id: int
    new_user_webhooks: list[str]
    users_connected_webhook: list[str]
    users_leave_webhook: list[str]


@dataclass
class ChannelsConfig:
    channels: list[ChannelConfig]
