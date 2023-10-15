import asyncio
import traceback

import aiohttp
import structlog
import tenacity
from sentry_sdk import capture_exception

logger = structlog.getLogger()


async def initialize_session() -> aiohttp.ClientSession:
    timeout = aiohttp.ClientTimeout(total=15.0, connect=5.0, sock_connect=5.0, sock_read=5.0)
    return aiohttp.ClientSession(timeout=timeout)


class WebhooksTransport:
    def __init__(self, session: aiohttp.ClientSession, raise_errors: bool = False) -> None:
        self.session = session
        self.raise_errors = raise_errors

    @tenacity.retry(
        reraise=False,
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_random_exponential(0.5, 60.0),
    )
    async def _call(self, link: str) -> None:
        try:
            response = await self.session.get(link, allow_redirects=True)
        except Exception as e:
            capture_exception(e)
            logger.info(e)
            if self.raise_errors:
                raise

        # do not retry on >400 status from target
        try:
            response.raise_for_status()
        except Exception as e:
            capture_exception(e)
            logger.info(e)
            if self.raise_errors:
                raise

    async def call(self, link: str) -> None:
        await self._call(link=link)
