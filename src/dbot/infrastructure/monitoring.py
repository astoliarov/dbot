from abc import abstractmethod

import aiohttp
import structlog
from aioprometheus.collectors import Counter, Summary
from aioprometheus.service import Service
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.getLogger()


class MonitoringConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="dbot_monitoring_", case_sensitive=False)

    healthchecksio_webhook: str = ""

    prometheus_metrics_enabled: bool = True
    prometheus_metrics_port: int = 3333
    prometheus_metrics_host: str = "0.0.0.0"


class IMonitoring:
    @abstractmethod
    async def start(self) -> None:
        ...

    @abstractmethod
    async def on_job_executed_successfully(self) -> None:
        ...

    @abstractmethod
    async def fire_channel_processing(self, channel_id: int, time: float) -> None:
        ...

    @abstractmethod
    async def fire_channels_processing(self, time: float) -> None:
        ...

    @abstractmethod
    async def fire_notifications_processing(self, channel_id: int, time: float) -> None:
        ...

    @abstractmethod
    async def fire_notifications_count(self, channel_id: int, count: int) -> None:
        ...


class HealthChecksIOClient:
    def __init__(self, webhook: str) -> None:
        self.webhook = webhook
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))

    async def fire(self) -> None:
        await self.session.get(self.webhook)


def initialize_monitoring() -> IMonitoring:
    monitoring_config = MonitoringConfiguration()

    health_checks_client = None
    if monitoring_config.healthchecksio_webhook:
        health_checks_client = HealthChecksIOClient(monitoring_config.healthchecksio_webhook)

    prometheus_monitoring = None
    if monitoring_config.prometheus_metrics_enabled:
        prometheus_monitoring = PrometheusMonitoring()

    return Monitoring(health_checks_client, prometheus_monitoring)


class PrometheusMonitoring:
    def __init__(self) -> None:
        self._service = Service()
        self._channel_processing_summary = Summary("channel_processing", "One channel processing time")
        self._channels_processing_summary = Summary("channels_processing", "All channels processing time")
        self._notifications_counter = Counter("notifications_count", "Notifications count")
        self._notifications_processing_summary = Summary("notifications_processing", "Notifications processing time")

    async def start(self) -> None:
        logger.info("prometheus_service.started")
        await self._service.start(port=3333)

    def fire_channel_processing(self, channel_id: int, time: float) -> None:
        self._channel_processing_summary.observe({"channel": str(channel_id)}, time)

    def fire_channels_processing(self, time: float) -> None:
        self._channels_processing_summary.observe({}, time)

    def fire_notifications_processing(self, channel_id: int, time: float) -> None:
        self._notifications_processing_summary.observe({"channel": str(channel_id)}, time)

    def fire_notifications_count(self, channel_id: int, count: int) -> None:
        self._notifications_counter.add({"channel": str(channel_id)}, count)


class Monitoring(IMonitoring):
    def __init__(
        self, health_checks_client: HealthChecksIOClient | None, prometheus_monitoring: PrometheusMonitoring | None
    ) -> None:
        self._health_checks_client = health_checks_client
        self._prometheus = prometheus_monitoring

    async def start(self) -> None:
        if self._prometheus:
            await self._prometheus.start()

    async def on_job_executed_successfully(self) -> None:
        if self._health_checks_client:
            await self._health_checks_client.fire()

    async def fire_channel_processing(self, channel_id: int, time: float) -> None:
        if self._prometheus:
            self._prometheus.fire_channel_processing(channel_id, time)

    async def fire_channels_processing(self, time: float) -> None:
        if self._prometheus:
            self._prometheus.fire_channels_processing(time)

    async def fire_notifications_processing(self, channel_id: int, time: float) -> None:
        if self._prometheus:
            self._prometheus.fire_notifications_processing(channel_id, time)

    async def fire_notifications_count(self, channel_id: int, count: int) -> None:
        if self._prometheus:
            self._prometheus.fire_notifications_count(channel_id, count)
