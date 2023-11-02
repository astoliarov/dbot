from abc import abstractmethod

import aiohttp
from pydantic_settings import BaseSettings, SettingsConfigDict


class MonitoringConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="dbot_monitoring_", case_sensitive=False)

    healthchecksio_webhook: str = ""


class IMonitoring:
    @abstractmethod
    async def on_job_executed_successfully(self) -> None:
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

    return Monitoring(health_checks_client)


class Monitoring(IMonitoring):
    def __init__(self, health_checks_client: HealthChecksIOClient | None) -> None:
        self._health_checks_client = health_checks_client

    async def on_job_executed_successfully(self) -> None:
        if self._health_checks_client:
            await self._health_checks_client.fire()
