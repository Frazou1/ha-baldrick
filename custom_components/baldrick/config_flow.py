"""Configuration via l'UI / UI config flow."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BaldrickApi, BaldrickError
from .const import DOMAIN


class BaldrickConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            api = BaldrickApi(async_get_clientsession(self.hass), host)
            try:
                state = await api.async_get_state()
            except BaldrickError:
                errors["base"] = "cannot_connect"
            else:
                # board_id = adresse MAC, stable même si l'IP change
                # board_id = MAC address, stable even if the IP changes
                await self.async_set_unique_id(state["board_id"])
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=state.get("board_model", f"Baldrick {host}"),
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )
