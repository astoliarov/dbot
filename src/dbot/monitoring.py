import aiohttp


class HealthChecksIOMonitoring:
    def __init__(self, webhook: str) -> None:
        self.webhook = webhook
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))

    async def on_job_executed_successfully(self) -> None:
        await self.session.get(self.webhook)
