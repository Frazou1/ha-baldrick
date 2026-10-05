"""Interrogation de la carte et commandes de lumière / Board polling and light commands.

La carte a deux sources de lumière exclusives :
The board has two mutually exclusive light sources:
  - le mode test (couleur unie, motifs de test) / test mode (solid colour, test patterns)
  - CunningFX (effets animés, presets) / CunningFX (animated effects, presets)
Elle refuse de lancer un effet tant que le mode test est actif : on coupe toujours l'autre source.
It refuses to start an effect while test mode is active: we always stop the other source.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BaldrickApi, BaldrickError
from .const import (
    DEFAULT_FX_SPEED,
    DEFAULT_TEST_PORTS,
    DEFAULT_TEST_TARGET,
    DOMAIN,
    HA_JOB,
    PATTERN_CHOOSE,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

BLACK = 0x000000


def _valid_ports(ports: str | None) -> str:
    """Garde la sélection de ports de la carte seulement si elle est valide.

    Keep the board's port selection only when it is valid ("all_pixel" or "1,3,").
    Après un redémarrage la carte peut renvoyer « | » (aucun port) : rien ne s'allumerait.
    After a reboot the board may report "|" (no port): nothing would light up.
    """
    if ports and re.fullmatch(r"all_\w+|(\d+,)+", ports):
        return ports
    return DEFAULT_TEST_PORTS


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def build_effect(effect: dict[str, Any], colour: int, speed: str) -> dict[str, Any]:
    """Construit un effet CunningFX à partir de la couleur choisie dans HA.

    Build a CunningFX effect from the colour picked in HA. Arguments are filled
    generically from the board's effect description:
      COLOUR "bg" -> noir / black ; 1er COLOUR -> couleur HA ; COLOUR suivants -> noir
      COLOUR_ARRAY -> [couleur HA, noir, blanc…] selon min_cols / per min_cols
      NUMBER -> milieu de la plage / middle of the range
    """
    result: dict[str, Any] = {
        "effect_name": effect["name"],
        "location": "ALL:",
        "speed": speed,
        "reverse": False,
    }
    colour_used = False
    for arg in effect.get("args", []):
        kind, name = arg.get("type"), arg["name"]
        if kind == "COLOUR":
            if name == "bg" or colour_used:
                result[name] = BLACK
            else:
                result[name] = colour
                colour_used = True
        elif kind == "COLOUR_ARRAY":
            palette = [colour, BLACK, 0xFFFFFF, BLACK, 0xFFFFFF]
            result[name] = palette[: max(1, arg.get("min_cols") or 1)]
            colour_used = True
        elif kind == "NUMBER":
            result[name] = (int(arg.get("min", 0)) + int(arg.get("max", 100))) // 2
    return result


class BaldrickCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: BaldrickApi) -> None:
        super().__init__(
            hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=SCAN_INTERVAL
        )
        self.api = api
        self.pixel_patterns: list[str] = []
        self.fx_effects: dict[str, dict[str, Any]] = {}  # display_name -> description
        self.presets: list[str] = []
        self._lock = asyncio.Lock()
        self._saved_job: dict[str, Any] | None = None

        # État choisi dans HA / State chosen in HA
        self.rgb: tuple[int, int, int] = (255, 255, 255)
        self.brightness: int = 255  # 0-255
        self.fx_speed: str = DEFAULT_FX_SPEED
        self.ha_effect: str | None = None  # effet CunningFX lancé par HA / effect started by HA

    async def _async_setup(self) -> None:
        try:
            self.pixel_patterns = await self.api.async_get_pixel_patterns()
            effects = await self.api.async_get_fx_effects()
        except BaldrickError as err:
            raise UpdateFailed(str(err)) from err
        self.fx_effects = {e.get("display_name") or e["name"]: e for e in effects}

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            state = await self.api.async_get_state()
            settings = await self.api.async_get_settings()
        except BaldrickError as err:
            raise UpdateFailed(str(err)) from err

        jobs = settings.get("cunningfx", {}).get("jobs", [])
        self.presets = [j["name"] for j in jobs if j.get("name") != HA_JOB]
        # Suit les changements faits depuis l'interface web de la carte
        # Follow changes made from the board's web interface
        if state.get("test_mode_active") and state.get("test_pattern") == PATTERN_CHOOSE:
            if colour := state.get("test_fixed_colours"):
                self.rgb = _hex_to_rgb(colour)
            if pct := state.get("test_brightness"):
                self.brightness = round(pct * 255 / 100)
        if not state.get("fx_state") or state.get("fx_active") != HA_JOB:
            self.ha_effect = None
        elif self.ha_effect is None:
            # Effet HA déjà en cours (ex. après un redémarrage de HA) : on le retrouve dans le preset
            # HA effect already running (e.g. after an HA restart): recover it from the preset
            for job in jobs:
                if job.get("name") == HA_JOB and job.get("effects"):
                    self._saved_job = job
                    name = job["effects"][0].get("effect_name")
                    self.ha_effect = next(
                        (d for d, e in self.fx_effects.items() if e["name"] == name), None
                    )
        return state

    # ----- Commandes / Commands -----

    async def async_set_solid(self, pattern: str = PATTERN_CHOOSE) -> None:
        """Couleur unie (ou motif de test) via le mode test / Solid colour (or test pattern) via test mode."""
        async with self._lock:
            if (await self.api.async_get_state()).get("fx_state"):
                await self.api.async_set_fx("")
            r, g, b = self.rgb
            await self.api.async_set_test(
                {
                    "test_mode_active": True,
                    "test_pattern": pattern,
                    "test_brightness": max(1, round(self.brightness * 100 / 255)),
                    "test_colour_picked_r": r,
                    "test_colour_picked_g": g,
                    "test_colour_picked_b": b,
                    "test_dmx_preset": self.data.get("test_dmx_preset", 0),
                    "test_ports": _valid_ports(self.data.get("test_ports")),
                    "test_target": self.data.get("test_target") or DEFAULT_TEST_TARGET,
                }
            )
            self.ha_effect = None
        await self.async_request_refresh()

    async def async_run_effect(self, name: str) -> None:
        """Lance un effet CunningFX avec la couleur HA / Run a CunningFX effect with the HA colour."""
        # La luminosité HA est appliquée en assombrissant la couleur
        # HA brightness is applied by dimming the colour
        scale = self.brightness / 255
        r, g, b = (round(c * scale) for c in self.rgb)
        job = {
            "name": HA_JOB,
            "effects": [build_effect(self.fx_effects[name], (r << 16) | (g << 8) | b, self.fx_speed)],
        }
        async with self._lock:
            # On n'écrit les réglages (mémoire flash) que si le preset HA a changé
            # Only write settings (flash memory) when the HA preset changed
            if job != self._saved_job:
                settings = await self.api.async_get_settings()
                fx = settings.setdefault("cunningfx", {})
                fx["jobs"] = [j for j in fx.get("jobs", []) if j.get("name") != HA_JOB] + [job]
                await self.api.async_save_settings(settings)
                self._saved_job = job
            await self._start_job(HA_JOB)
            self.ha_effect = name
        await self.async_request_refresh()

    async def async_run_preset(self, preset: str) -> None:
        """Lance un preset créé sur la carte / Run a preset created on the board."""
        async with self._lock:
            await self._start_job(preset)
            self.ha_effect = None
        await self.async_request_refresh()

    async def _start_job(self, job: str) -> None:
        state = await self.api.async_get_state()
        if state.get("test_mode_active"):
            await self.api.async_set_test({"test_mode_active": False})
        if state.get("fx_state"):
            # fx_config agit comme une bascule : relancer le preset en cours l'arrêterait
            # fx_config is a toggle: restarting the running preset would stop it
            await self.api.async_set_fx("")
        await self.api.async_set_fx(job)

    async def async_turn_off(self) -> None:
        async with self._lock:
            if (await self.api.async_get_state()).get("fx_state"):
                await self.api.async_set_fx("")
            await self.api.async_set_test({"test_mode_active": False})
            self.ha_effect = None
        await self.async_request_refresh()
