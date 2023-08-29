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


def initialize_monitoring() -> IMonitoring | None:
    monitoring_config = MonitoringConfiguration()

    if not monitoring_config.healthchecksio_webhook:
        return None

    return HealthChecksIOMonitoring(monitoring_config.healthchecksio_webhook)


class HealthChecksIOMonitoring(IMonitoring):
    def __init__(self, webhook: str) -> None:
        self.webhook = webhook
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))

    async def on_job_executed_successfully(self) -> None:
        await self.session.get(self.webhook)
