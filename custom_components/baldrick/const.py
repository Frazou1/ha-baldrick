"""Constantes de l'intégration Baldrick / Baldrick integration constants."""

from datetime import timedelta

DOMAIN = "baldrick"

SCAN_INTERVAL = timedelta(seconds=10)

# Motif "couleur choisie" du mode test, et motifs à ne pas exposer comme effets
# Test-mode "picked colour" pattern, and patterns not exposed as effects
PATTERN_CHOOSE = "choose"
PATTERN_OFF = "off"
HIDDEN_PATTERNS = {PATTERN_OFF, PATTERN_CHOOSE}

DEFAULT_TEST_PORTS = "all_pixel"
DEFAULT_TEST_TARGET = "configured"
