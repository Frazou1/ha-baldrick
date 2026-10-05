"""Constantes de l'intégration Baldrick / Baldrick integration constants."""

from datetime import timedelta

DOMAIN = "baldrick"

SCAN_INTERVAL = timedelta(seconds=10)

# Mode test : motif « couleur choisie » et motifs exposés comme effets « Test: … »
# Test mode: "picked colour" pattern and patterns exposed as "Test: …" effects
PATTERN_CHOOSE = "choose"
TEST_EFFECT_PATTERNS = ("hodgson", "model_colours")

DEFAULT_TEST_PORTS = "all_pixel"
DEFAULT_TEST_TARGET = "configured"

# Preset CunningFX géré par Home Assistant (réécrit à chaque changement d'effet/couleur)
# CunningFX preset managed by Home Assistant (rewritten on each effect/colour change)
HA_JOB = "Home Assistant"

PRESET_PREFIX = "Preset: "
TEST_PREFIX = "Test: "

FX_SPEEDS = ["static", "slow", "regular", "fast"]
DEFAULT_FX_SPEED = "regular"
