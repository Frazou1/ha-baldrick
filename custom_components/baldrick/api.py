"""Client HTTP de l'interface web Baldrick (firmware "turnip").

HTTP client for the Baldrick web interface ("turnip" firmware).

Points d'accès utilisés / Endpoints used:
  GET  /system_state                -> état de la carte, mode test, température
  GET  /turnip_test_ui/patterns     -> motifs de test disponibles / available test patterns
  POST /turnip_test/test_config     -> active/désactive le mode test / toggles test mode (JSON)
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import aiohttp

TIMEOUT = 10


class BaldrickError(Exception):
    """Carte injoignable ou réponse invalide / Board unreachable or bad response."""


class BaldrickApi:
    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        self._session = session
        self._base = f"http://{host}"

    async def _request(self, method: str, path: str, payload: dict | None = None) -> Any:
        try:
            async with asyncio.timeout(TIMEOUT):
                resp = await self._session.request(
                    method,
                    f"{self._base}/{path}",
                    data=json.dumps(payload) if payload is not None else None,
                )
                resp.raise_for_status()
                if method == "GET":
                    # La carte ne renvoie pas toujours application/json
                    # The board does not always send application/json
                    return json.loads(await resp.text())
                return None
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise BaldrickError(f"{method} {path}: {err}") from err

    async def async_get_state(self) -> dict[str, Any]:
        return await self._request("GET", "system_state")

    async def async_get_pixel_patterns(self) -> list[str]:
        data = await self._request("GET", "turnip_test_ui/patterns")
        return [p["name"] for p in data.get("patterns", []) if p.get("port_type") == "pixel"]

    async def async_set_test(self, settings: dict[str, Any]) -> None:
        """Envoie une config de mode test (champs partiels acceptés).

        Send a test-mode config (partial fields accepted).
        """
        await self._request("POST", "turnip_test/test_config", settings)
