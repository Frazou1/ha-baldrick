# Baldrick (iLightThat) pour Home Assistant / for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories/)
![Version](https://img.shields.io/badge/version-0.2.1-blue)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.11%2B-41BDF5)

[Français](#français) | [English](#english)

---

## Français

### Description

Intégration personnalisée (HACS) qui pilote une carte de contrôle de pixels **Baldrick8** d'[iLightThat](https://www.baldrickboard.com/) directement depuis Home Assistant, **en local**, sans FPP ni xLights.

Elle utilise l'API HTTP de l'interface web de la carte (firmware « turnip ») :

| Requête | Usage |
|---|---|
| `GET /system_state` | état de la carte, mode test, effet en cours, température |
| `GET /settings`, `POST /settings` | réglages complets, dont les presets CunningFX |
| `GET /turnip_test_ui/patterns` | motifs de test disponibles |
| `POST /turnip_test/test_config` | couleur unie et motifs de test (mode test de la carte) |
| `GET /turnip_fx/effects` | effets animés CunningFX disponibles |
| `POST /turnip_fx/fx_config` | lance ou arrête un preset CunningFX |

Type d'intégration : appareil, `local_polling`. Aucune dépendance Python supplémentaire.

### Fonctionnalités

- Allumer / éteindre les pixels, choisir une **couleur RGB** et une **luminosité**.
- Lancer les **effets animés CunningFX** de la carte avec la couleur choisie dans Home Assistant (changer la couleur pendant un effet garde l'effet).
- Jouer les **presets** créés dans l'interface web de la carte (onglet *CunningFX*).
- Afficher les **motifs de test** `hodgson` et `model_colours` (s'ils existent sur la carte).
- Régler la **vitesse** des effets animés (statique, lente, normale, rapide), conservée après un redémarrage de Home Assistant.
- Suivre la **température** de la carte.
- Suivre les changements faits ailleurs : un preset lancé ou une couleur choisie depuis l'interface web de la carte apparaît dans Home Assistant au prochain cycle d'interrogation.
- La carte est identifiée par son **adresse MAC** : un changement d'adresse IP ne crée pas de doublon. La fiche de l'appareil affiche le fabricant, le modèle, la version du firmware et un lien vers l'interface web.

### Prérequis

- Home Assistant **2024.11** ou plus récent (valeur de `hacs.json`).
- Une carte Baldrick8 dont l'**interface web** répond en **HTTP** (port 80, sans authentification) depuis la machine Home Assistant. Testé avec une **Baldrick 8 Port v1.1, firmware v3.8.8**; les autres firmwares n'ont pas été vérifiés.
- Le moteur d'effets **CunningFX** du firmware, pour les effets animés et les presets.
- Une **adresse IP fixe** recommandée (réservation DHCP dans le routeur) : la carte est en DHCP par défaut.

> **Important** : tant que la lumière est allumée dans Home Assistant, elle **prend le dessus** sur les données reçues de xLights / FPP (DDP, E1.31, Art-Net). Éteignez la lumière dans Home Assistant pour rendre la main au spectacle.

### Installation

#### Par HACS (recommandé)

1. Dans Home Assistant, ouvrir **HACS**.
2. Menu **⋮** (en haut à droite) → **Dépôts personnalisés**.
3. Dépôt : `https://github.com/Frazou1/ha-baldrick`, catégorie : **Intégration**, puis **Ajouter**.
4. Rechercher **Baldrick (iLightThat)** dans HACS, puis **Télécharger**.
5. **Redémarrer** Home Assistant.

#### Installation manuelle

1. Copier le dossier `custom_components/baldrick` de ce dépôt dans le dossier `config/custom_components/` de Home Assistant (créer `custom_components` s'il n'existe pas).
2. Vous devez obtenir `config/custom_components/baldrick/manifest.json`.
3. **Redémarrer** Home Assistant.

### Configuration

**Paramètres → Appareils et services → Ajouter une intégration → Baldrick (iLightThat)**.

| Champ | Obligatoire | Description |
|---|---|---|
| **Hôte** (`host`) | oui | Adresse IP ou nom d'hôte de la carte, par exemple `192.168.1.50`. Un préfixe `http://` ou `https://` et tout chemin après l'adresse (`/…`) sont retirés automatiquement. La connexion se fait toujours en `http://`. |

À la validation, l'intégration lit `/system_state` :

- si la carte ne répond pas : erreur **« Impossible de joindre l'interface web de la carte. »**;
- l'entrée porte le nom du **modèle** renvoyé par la carte (sinon `Baldrick <hôte>`);
- si cette carte (même adresse MAC) est déjà configurée, l'ajout est interrompu (**« Cette carte est déjà configurée. »**) et **l'adresse enregistrée est mise à jour** : c'est la façon de corriger l'adresse après un changement d'IP.

Il n'y a **pas d'options** après l'installation. Les ports et la cible utilisés pour la couleur unie sont ceux réglés dans l'onglet *Test* de l'interface web de la carte (par défaut : tous les ports pixel configurés).

### Entités créées

Un appareil par carte, avec trois entités. Les identifiants d'entité ci-dessous sont des exemples : ils sont dérivés du nom de l'appareil (modèle de la carte) et de la langue de Home Assistant au moment de l'ajout.

| Entité | Plateforme | Catégorie | Description |
|---|---|---|---|
| `light.<carte>` | `light` | — | Allumé/éteint, couleur RGB, luminosité, liste d'effets (voir ci-dessous). Allumée si le mode test **ou** un preset CunningFX est actif. |
| `select.<carte>_vitesse_des_effets` (`…_effect_speed` en anglais) | `select` | Configuration | Vitesse des effets animés : `static`, `slow`, `regular` (défaut), `fast`. Changer la vitesse relance l'effet lancé par Home Assistant. |
| `sensor.<carte>_temperature` | `sensor` | Diagnostic | Température de la carte en °C (première valeur renvoyée par la carte), 1 décimale. |

**Liste des effets de la lumière**, dans l'ordre :

1. `off` : couleur unie (mode test de la carte, motif « couleur choisie »).
2. Les **effets animés CunningFX** de type pixel annoncés par la carte (sur le firmware testé : Twinkle, Fader, Bounce, Colour Splash, Alternate, On/Off, Rainbow). Ils utilisent la couleur de Home Assistant; la luminosité est appliquée en assombrissant la couleur. Les autres paramètres de l'effet sont remplis automatiquement (fond noir, nombres au milieu de leur plage).
3. `Preset: <nom>` : chaque preset créé sur la carte, joué tel quel.
4. `Test: hodgson`, `Test: model_colours` : motifs de test de la carte.

Pour jouer un effet animé, l'intégration enregistre sur la carte un preset nommé **`Home Assistant`** (réécrit dans la mémoire de la carte seulement quand l'effet, la couleur, la luminosité ou la vitesse change). Ne le modifiez pas dans l'interface web; il n'apparaît pas dans la liste des presets de Home Assistant.

**Interrogation** : toutes les **10 secondes** (`/system_state` et `/settings`). La liste des effets et des motifs de test n'est lue qu'au **démarrage de l'intégration** : après une mise à jour du firmware, recharger l'intégration. Les presets, eux, sont relus à chaque cycle.

### Exemples d'utilisation

Allumer les pixels en orange avec l'effet Twinkle au coucher du soleil, puis les éteindre à 22 h :

```yaml
automation:
  - alias: "Baldrick - orange au coucher du soleil"
    triggers:
      - trigger: sun
        event: sunset
    actions:
      - action: light.turn_on
        target:
          entity_id: light.baldrick_8_port   # adapter à votre entité
        data:
          rgb_color: [255, 100, 0]
          brightness_pct: 80
          effect: Twinkle

  - alias: "Baldrick - extinction"
    triggers:
      - trigger: time
        at: "22:00:00"
    actions:
      - action: light.turn_off
        target:
          entity_id: light.baldrick_8_port
```

Jouer un preset créé sur la carte : `effect: "Preset: <nom du preset>"`. Revenir à une couleur unie : `effect: "off"`.

Carte de tableau de bord :

```yaml
type: tile
entity: light.baldrick_8_port
features:
  - type: light-brightness
```

### Dépannage

- **« Impossible de joindre l'interface web de la carte. »** : vérifier que `http://<adresse de la carte>` s'ouvre dans un navigateur depuis le même réseau que Home Assistant. La cause exacte (délai dépassé, refus de connexion, réponse non JSON…) est écrite dans le journal avec le message `Carte Baldrick injoignable / Baldrick board unreachable`.
- **Entités indisponibles** : la carte n'a pas répondu à l'interrogation (délai de 10 s par requête). Si la carte est injoignable au démarrage, Home Assistant réessaie automatiquement la configuration.
- **L'adresse IP de la carte a changé** : refaire **Ajouter une intégration** avec la nouvelle adresse; l'entrée existante est mise à jour.
- **Rien ne s'allume** : vérifier les ports cochés dans l'onglet *Test* de la carte. Si la carte ne renvoie aucun port valide (par exemple après son redémarrage), l'intégration utilise tous les ports pixel.
- **xLights / FPP ne contrôle plus les pixels** : la lumière est encore allumée dans Home Assistant; l'éteindre.
- **Erreur `Baldrick: unknown effect '…'`** : le nom d'effet passé à `light.turn_on` n'existe pas dans la liste de la lumière (les noms sont sensibles à la casse).

Journal détaillé, dans `configuration.yaml` :

```yaml
logger:
  default: warning
  logs:
    custom_components.baldrick: debug
```

### Licence

[MIT](LICENSE) © 2026 Frazou1

---

## English

### Description

Custom (HACS) integration that controls an [iLightThat](https://www.baldrickboard.com/) **Baldrick8** pixel controller directly from Home Assistant, **locally**, without FPP or xLights.

It uses the HTTP API of the board's web interface ("turnip" firmware):

| Request | Purpose |
|---|---|
| `GET /system_state` | board state, test mode, running effect, temperature |
| `GET /settings`, `POST /settings` | full settings, including CunningFX presets |
| `GET /turnip_test_ui/patterns` | available test patterns |
| `POST /turnip_test/test_config` | solid colour and test patterns (board test mode) |
| `GET /turnip_fx/effects` | available CunningFX animated effects |
| `POST /turnip_fx/fx_config` | starts or stops a CunningFX preset |

Integration type: device, `local_polling`. No extra Python dependencies.

### Features

- Turn the pixels on/off, pick an **RGB colour** and a **brightness**.
- Run the board's **CunningFX animated effects** with the colour picked in Home Assistant (changing the colour while an effect runs keeps the effect).
- Play the **presets** created in the board's web interface (*CunningFX* tab).
- Show the `hodgson` and `model_colours` **test patterns** (when the board provides them).
- Set the **speed** of animated effects (static, slow, regular, fast), kept across Home Assistant restarts.
- Monitor the board **temperature**.
- Follow changes made elsewhere: a preset started or a colour picked from the board's web interface shows up in Home Assistant on the next polling cycle.
- The board is identified by its **MAC address**: an IP address change does not create a duplicate. The device page shows the manufacturer, model, firmware version and a link to the web interface.

### Requirements

- Home Assistant **2024.11** or newer (value from `hacs.json`).
- A Baldrick8 board whose **web interface** answers over **HTTP** (port 80, no authentication) from the Home Assistant host. Tested with a **Baldrick 8 Port v1.1, firmware v3.8.8**; other firmware versions have not been verified.
- The firmware's **CunningFX** effect engine, for animated effects and presets.
- A **fixed IP address** is recommended (DHCP reservation in your router): the board uses DHCP by default.

> **Important**: while the light is on in Home Assistant, it **overrides** data coming from xLights / FPP (DDP, E1.31, Art-Net). Turn the light off in Home Assistant to hand control back to the show.

### Installation

#### With HACS (recommended)

1. In Home Assistant, open **HACS**.
2. **⋮** menu (top right) → **Custom repositories**.
3. Repository: `https://github.com/Frazou1/ha-baldrick`, type: **Integration**, then **Add**.
4. Search for **Baldrick (iLightThat)** in HACS, then **Download**.
5. **Restart** Home Assistant.

#### Manual installation

1. Copy the `custom_components/baldrick` folder of this repository into Home Assistant's `config/custom_components/` folder (create `custom_components` if needed).
2. You should end up with `config/custom_components/baldrick/manifest.json`.
3. **Restart** Home Assistant.

### Configuration

**Settings → Devices & services → Add integration → Baldrick (iLightThat)**.

| Field | Required | Description |
|---|---|---|
| **Host** (`host`) | yes | IP address or hostname of the board, e.g. `192.168.1.50`. An `http://` or `https://` prefix and any path after the address (`/…`) are stripped automatically. The connection always uses `http://`. |

On submit, the integration reads `/system_state`:

- if the board does not answer: error **"Unable to reach the board's web interface."**;
- the entry is named after the **model** reported by the board (otherwise `Baldrick <host>`);
- if this board (same MAC address) is already configured, the flow aborts (**"This board is already configured."**) and **the stored address is updated**: this is how to fix the address after an IP change.

There are **no options** after setup. The ports and target used for solid colour are the ones set in the *Test* tab of the board's web interface (default: all configured pixel ports).

### Entities

One device per board, with three entities. The entity IDs below are examples: they are derived from the device name (board model) and from Home Assistant's language when the board is added.

| Entity | Platform | Category | Description |
|---|---|---|---|
| `light.<board>` | `light` | — | On/off, RGB colour, brightness, effect list (see below). On when test mode **or** a CunningFX preset is active. |
| `select.<board>_effect_speed` | `select` | Configuration | Speed of animated effects: `static`, `slow`, `regular` (default), `fast`. Changing it restarts the effect started by Home Assistant. |
| `sensor.<board>_temperature` | `sensor` | Diagnostic | Board temperature in °C (first value reported by the board), 1 decimal. |

**Light effect list**, in order:

1. `off`: solid colour (board test mode, "picked colour" pattern).
2. The pixel **CunningFX animated effects** reported by the board (on the tested firmware: Twinkle, Fader, Bounce, Colour Splash, Alternate, On/Off, Rainbow). They use the Home Assistant colour; brightness is applied by dimming the colour. Other effect parameters are filled automatically (black background, numbers in the middle of their range).
3. `Preset: <name>`: each preset created on the board, played as is.
4. `Test: hodgson`, `Test: model_colours`: board test patterns.

To play an animated effect, the integration saves a preset named **`Home Assistant`** on the board (written to the board's memory only when the effect, colour, brightness or speed changes). Do not edit it in the web interface; it is not listed among the presets in Home Assistant.

**Polling**: every **10 seconds** (`/system_state` and `/settings`). The list of effects and test patterns is read only when the **integration starts**: reload the integration after a firmware update. Presets are re-read on every cycle.

### Usage examples

Turn the pixels orange with the Twinkle effect at sunset, then off at 10 p.m.:

```yaml
automation:
  - alias: "Baldrick - orange at sunset"
    triggers:
      - trigger: sun
        event: sunset
    actions:
      - action: light.turn_on
        target:
          entity_id: light.baldrick_8_port   # adjust to your entity
        data:
          rgb_color: [255, 100, 0]
          brightness_pct: 80
          effect: Twinkle

  - alias: "Baldrick - off"
    triggers:
      - trigger: time
        at: "22:00:00"
    actions:
      - action: light.turn_off
        target:
          entity_id: light.baldrick_8_port
```

Play a preset created on the board: `effect: "Preset: <preset name>"`. Back to a solid colour: `effect: "off"`.

Dashboard card:

```yaml
type: tile
entity: light.baldrick_8_port
features:
  - type: light-brightness
```

### Troubleshooting

- **"Unable to reach the board's web interface."**: check that `http://<board address>` opens in a browser from the same network as Home Assistant. The exact cause (timeout, connection refused, non-JSON answer…) is logged with the message `Carte Baldrick injoignable / Baldrick board unreachable`.
- **Entities unavailable**: the board did not answer polling (10 s timeout per request). If the board is unreachable at startup, Home Assistant retries the setup automatically.
- **The board's IP address changed**: run **Add integration** again with the new address; the existing entry is updated.
- **Nothing lights up**: check the ports ticked in the board's *Test* tab. If the board reports no valid port (for example after it reboots), the integration falls back to all pixel ports.
- **xLights / FPP no longer controls the pixels**: the light is still on in Home Assistant; turn it off.
- **Error `Baldrick: unknown effect '…'`**: the effect name passed to `light.turn_on` is not in the light's effect list (names are case-sensitive).

Debug logging, in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.baldrick: debug
```

### License

[MIT](LICENSE) © 2026 Frazou1
