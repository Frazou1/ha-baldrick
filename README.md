# Baldrick (iLightThat) for Home Assistant

[English](#english) · [Français](#français)

---

## English

Custom HACS integration to control an iLightThat [Baldrick8](https://www.baldrickboard.com/) board from Home Assistant, locally, without FPP or xLights.

### Features

| Entity | Description |
|---|---|
| `light.<board>` | On/off, RGB colour, brightness, effects (the board's test patterns: `rainbow`, `hodgson`, `model_colours`, `full_white`, …) |
| `sensor.<board>_temperature` | Board temperature (diagnostic) |

The device page also shows the model, firmware version and a link to the board's web interface.

### How it works

The integration uses the HTTP API of the board's web interface ("turnip" firmware):

- `GET /system_state`: state, polled every 10 s
- `GET /turnip_test_ui/patterns`: list of effects
- `POST /turnip_test/test_config`: turns the light on through the board's **test mode** (`choose` pattern for a solid colour)

> ⚠️ Test mode overrides data coming from xLights/FPP (DDP, E1.31, Art-Net). Turn the light off in HA to hand control back to the show.
>
> The ports affected are the ones set in the board's *Test* tab (default: all configured pixel ports).

### Installation

#### HACS (recommended)

1. HACS → ⋮ menu → **Custom repositories**
2. URL: `https://github.com/Frazou1/ha-baldrick`, category **Integration**
3. Install **Baldrick (iLightThat)**, then restart Home Assistant

#### Manual

Copy `custom_components/baldrick` into Home Assistant's `config/custom_components/` folder, then restart.

### Configuration

**Settings → Devices & services → Add integration → Baldrick (iLightThat)**, then enter the board's IP address (e.g. `192.168.2.171`).

The board is identified by its MAC address: if its IP changes, adding it again simply updates the address.

> 💡 The board uses DHCP by default. Reserve a fixed IP for it in your router.

### Troubleshooting

"Unable to reach the board's web interface": check that `http://<board IP>` opens in a browser from the same network as Home Assistant. The exact cause is written to the HA logs (search for "Baldrick").

### Tested with

- Baldrick 8 Port v1.1, firmware v3.8.8

---

## Français

Intégration personnalisée (HACS) pour piloter une carte [Baldrick8](https://www.baldrickboard.com/) d'iLightThat depuis Home Assistant, en local, sans FPP ni xLights.

### Fonctions

| Entité | Description |
|---|---|
| `light.<carte>` | On/off, couleur RGB, luminosité, effets (motifs de test de la carte : `rainbow`, `hodgson`, `model_colours`, `full_white`, …) |
| `sensor.<carte>_temperature` | Température de la carte (diagnostic) |

L'appareil affiche aussi le modèle, la version du firmware et un lien vers l'interface web de la carte.

### Fonctionnement

L'intégration utilise l'API HTTP de l'interface web de la carte (firmware « turnip ») :

- `GET /system_state` : état, interrogé toutes les 10 s
- `GET /turnip_test_ui/patterns` : liste des effets
- `POST /turnip_test/test_config` : allume la lumière via le **mode test** de la carte (motif `choose` pour une couleur unie)

> ⚠️ Le mode test prend le dessus sur les données reçues de xLights/FPP (DDP, E1.31, Art-Net). Éteins la lumière dans HA pour rendre la main au show.
>
> Les ports pris en compte sont ceux réglés dans l'onglet *Test* de la carte (par défaut : tous les ports pixel configurés).

### Installation

#### HACS (recommandé)

1. HACS → menu ⋮ → **Dépôts personnalisés**
2. URL : `https://github.com/Frazou1/ha-baldrick`, catégorie **Intégration**
3. Installer **Baldrick (iLightThat)**, puis redémarrer Home Assistant

#### Manuelle

Copier `custom_components/baldrick` dans le dossier `config/custom_components/` de Home Assistant, puis redémarrer.

### Configuration

**Paramètres → Appareils et services → Ajouter une intégration → Baldrick (iLightThat)**, puis entrer l'adresse IP de la carte (ex. `192.168.2.171`).

La carte est identifiée par son adresse MAC : si son IP change, refaire l'ajout met simplement l'adresse à jour.

> 💡 La carte est en DHCP par défaut. Réserve-lui une IP fixe dans ton routeur.

### Dépannage

« Impossible de joindre l'interface web de la carte » : vérifier que `http://<IP de la carte>` s'ouvre dans un navigateur, depuis le même réseau que Home Assistant. La cause exacte est inscrite dans les journaux de HA (chercher « Baldrick »).

### Testé avec

- Baldrick 8 Port v1.1, firmware v3.8.8
