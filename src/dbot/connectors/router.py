from dbot.connectors.abstract import IConnector
from dbot.model.config import (
    ChannelMonitorConfig,
    MonitorConfig,
    Target,
    TargetTypeEnum,
)
from dbot.model.notifications import Notification


class NotificationRouter:
    def __init__(self, configs: MonitorConfig) -> None:
        self._by_channel_id: dict[int, ChannelMonitorConfig] = {
            config.channel_id: config for config in configs.channels
        }
        self._connectors: dict[TargetTypeEnum, IConnector] = {}

    def register_connector(self, route_type: TargetTypeEnum, connector: IConnector) -> None:
        self._connectors[route_type] = connector

    async def send(self, notifications: list[Notification]) -> None:
        for notification in notifications:
            config: ChannelMonitorConfig | None = self._by_channel_id.get(notification.channel_id)

            if not config:
                continue

            for target in config.targets:
                connector = self._get_connector(target)
                if not connector:
                    continue
                await connector.send([notification])

    def _get_connector(self, target: Target) -> IConnector | None:
        return self._connectors.get(target.type, None)
