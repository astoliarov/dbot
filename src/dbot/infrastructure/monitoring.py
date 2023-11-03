import aiohttp
import structlog
from aioprometheus.collectors import REGISTRY, Counter, Summary
from aioprometheus.service import Service
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.getLogger()


class MonitoringConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="dbot_monitoring_", case_sensitive=False)

    healthchecksio_webhook: str = ""

    prometheus_metrics_enabled: bool = True
    prometheus_metrics_port: int = 3333
    prometheus_metrics_host: str = "0.0.0.0"


class HealthChecksIOClient:
    def __init__(self, webhook: str) -> None:
        self.webhook = webhook
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))

    async def fire(self) -> None:
        await self.session.get(self.webhook)


class PrometheusMonitoring:
    def __init__(self, enabled: bool, host: str = "0.0.0.0", port: int = 3333) -> None:
        self._enabled = enabled
        self._port = port
        self._host = host

        self._service = Service()
        self._channel_processing_summary = Summary("channel_processing", "One channel processing time")
        self._channels_processing_summary = Summary("channels_processing", "All channels processing time")
        self._notifications_counter = Counter("notifications", "Notifications count")
        self._notifications_processing_summary = Summary("notifications_processing", "Notifications processing time")
        self._webhooks_count = Counter("webhooks", "Webhooks count")
        self._redis_events_count = Counter("redis_events", "Webhooks count")

    async def start(self) -> None:
        if self._enabled:
            await self._service.start(port=self._port, addr=self._host)
            logger.info("prometheus_service.started", port=self._port, host=self._host)
        else:
            logger.info("prometheus_service.disabled")

    @staticmethod
    def clear() -> None:
        REGISTRY.clear()  # type: ignore

    def fire_channel_processing(self, channel_id: int, time: float) -> None:
        self._channel_processing_summary.observe({"channel": str(channel_id)}, time)

    def fire_channels_processing(self, time: float) -> None:
        self._channels_processing_summary.observe({}, time)

    def fire_notifications_processing(self, channel_id: int, time: float) -> None:
        self._notifications_processing_summary.observe({"channel": str(channel_id)}, time)

    def fire_notifications_count(self, channel_id: int, count: int) -> None:
        self._notifications_counter.add({"channel": str(channel_id)}, count)

    def fire_webhooks_count(self) -> None:
        self._webhooks_count.add({}, 1)

    def fire_redis_events_count(self) -> None:
        self._redis_events_count.add({}, 1)


class Monitoring:
    def __init__(
        self, health_checks_client: HealthChecksIOClient | None, prometheus_monitoring: PrometheusMonitoring
    ) -> None:
        self._health_checks_client = health_checks_client
        self._prometheus = prometheus_monitoring

    async def start(self) -> None:
        await self._prometheus.start()

    async def on_job_executed_successfully(self) -> None:
        if self._health_checks_client:
            await self._health_checks_client.fire()

    async def fire_channel_processing(self, channel_id: int, time: float) -> None:
        self._prometheus.fire_channel_processing(channel_id, time)

    async def fire_channels_processing(self, time: float) -> None:
        self._prometheus.fire_channels_processing(time)

    async def fire_notifications_processing(self, channel_id: int, time: float) -> None:
        self._prometheus.fire_notifications_processing(channel_id, time)

    async def fire_notifications_count(self, channel_id: int, count: int) -> None:
        self._prometheus.fire_notifications_count(channel_id, count)

    async def fire_webhooks_count(self) -> None:
        self._prometheus.fire_webhooks_count()

    async def fire_redis_events_count(self) -> None:
        self._prometheus.fire_redis_events_count()


def initialize_monitoring() -> Monitoring:
    monitoring_config = MonitoringConfiguration()

    health_checks_client = None
    if monitoring_config.healthchecksio_webhook:
        health_checks_client = HealthChecksIOClient(monitoring_config.healthchecksio_webhook)

    prometheus_monitoring = PrometheusMonitoring(
        enabled=monitoring_config.prometheus_metrics_enabled,
        port=monitoring_config.prometheus_metrics_port,
        host=monitoring_config.prometheus_metrics_host,
    )

    return Monitoring(health_checks_client, prometheus_monitoring)
