import abc
import time

import structlog

from dbot.connectors.abstract import IConnector
from dbot.infrastructure.monitoring import Monitoring
from dbot.model.config import (
    ChannelMonitorConfig,
    MonitorConfig,
    Target,
    TargetTypeEnum,
)
from dbot.model.notifications import Notification

logger = structlog.getLogger()


class INotificationRouter(abc.ABC):
    @abc.abstractmethod
    async def send(self, notifications: list[Notification]) -> None:
        ...


class NotificationRouter(INotificationRouter):
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


class NotificationRouterInstrumentation(INotificationRouter):
    def __init__(self, router: NotificationRouter, monitoring: Monitoring) -> None:
        self._router = router
        self._monitoring = monitoring

    async def send(self, notifications: list[Notification]) -> None:
        logger.debug("notifications.sending", notifications=notifications)
        start = time.monotonic()

        await self._router.send(notifications)

        send_time = time.monotonic() - start
        logger.debug("notifications.sent", notifications=notifications, processing_time=send_time)

        if not notifications:
            return

        channel_id = notifications[0].channel_id
        await self._monitoring.fire_notifications_processing(channel_id, send_time)
        await self._monitoring.fire_notifications_count(channel_id, len(notifications))
