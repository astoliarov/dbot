import aiohttp
import structlog
import tenacity
from sentry_sdk import capture_exception

logger = structlog.getLogger()


class WebhooksTransport:
    def __init__(self) -> None:
        timeout = aiohttp.ClientTimeout(total=15.0, connect=5.0, sock_connect=5.0, sock_read=5.0)
        self.session = aiohttp.ClientSession(timeout=timeout)

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
            raise

        # do not retry on >400 status from target
        try:
            response.raise_for_status()
        except Exception as e:
            capture_exception(e)
            logger.info(e)

    async def call(self, link: str) -> None:
        try:
            await self._call(link=link)
        except Exception as e:
            logger.info(e)
