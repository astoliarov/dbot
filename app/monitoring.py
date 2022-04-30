import aiohttp


class HealthChecksIOMonitoring:
    def __init__(self, webhook: str) -> None:
        self.webhook = webhook
        timeout = aiohttp.ClientTimeout(total=15)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def on_job_executed_successfully(self) -> None:
        await self.session.get(self.webhook)
