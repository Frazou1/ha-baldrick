# Baldrick (iLightThat) pour Home Assistant

Intégration personnalisée (HACS) pour piloter une carte **Baldrick8** d'[iLightThat](https://www.baldrickboard.com/) depuis Home Assistant, en local, sans FPP ni xLights.

*Custom HACS integration to control an iLightThat Baldrick8 board from Home Assistant, locally.*

## Fonctions

| Entité | Description |
|---|---|
| `light.<carte>` | On/off, couleur RGB, luminosité, effets (motifs de test de la carte : `rainbow`, `hodgson`, `model_colours`, `full_white`, …) |
| `sensor.<carte>_temperature` | Température de la carte (diagnostic) |

L'appareil affiche aussi le modèle, la version du firmware et un lien vers l'interface web.

## Fonctionnement

L'intégration utilise l'API HTTP de l'interface web de la carte (firmware « turnip ») :

- `GET /system_state` : état interrogé toutes les 10 s
- `GET /turnip_test_ui/patterns` : liste des effets
- `POST /turnip_test/test_config` : allume la lumière via le **mode test** de la carte (motif `choose` pour une couleur unie)

> ⚠️ Le mode test prend le dessus sur les données reçues de xLights/FPP (DDP, E1.31, Art-Net). Éteins la lumière dans HA pour rendre la main au show.
>
> Les ports pris en compte sont ceux réglés dans l'onglet *Test* de la carte (par défaut : tous les ports pixel configurés).

## Installation

### HACS (recommandé)

1. HACS → menu ⋮ → **Dépôts personnalisés**
2. URL : `https://github.com/Frazou1/ha-baldrick`, catégorie **Intégration**
3. Installer **Baldrick (iLightThat)**, puis redémarrer Home Assistant

### Manuelle

Copier `custom_components/baldrick` dans le dossier `config/custom_components/` de Home Assistant, puis redémarrer.

## Configuration

**Paramètres → Appareils et services → Ajouter une intégration → Baldrick (iLightThat)**, puis entrer l'adresse IP de la carte (ex. `192.168.2.171`).

La carte est identifiée par son adresse MAC : si son IP change, refaire l'ajout met simplement l'adresse à jour.

## Testé avec

- Baldrick 8 Port v1.1, firmware v3.8.8
