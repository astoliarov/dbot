import json
from typing import Any

from aiohttp import ClientSession


class WireMockClient:
    def __init__(self, host: str) -> None:
        self.host = host
        self.session = ClientSession()

    async def set_stub(self, path: str, body: dict[str, Any], method: str = "GET", status: int = 200) -> None:
        assert method in ["POST", "GET", "PUT", "DELETE", "PATCH"]

        body = {
            "request": {"method": method, "url": path},
            "response": {"body": json.dumps(body), "headers": {"Content-Type": "application/json"}, "status": status},
        }

        response = await self.session.post(f"{self.host}/__admin/mappings", json=body)
        assert response.status == 201

    async def reset(self) -> None:
        response = await self.session.post(f"{self.host}/__admin/mappings/reset")

        assert response.status == 200
