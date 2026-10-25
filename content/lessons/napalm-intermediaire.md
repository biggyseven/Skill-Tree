# NAPALM — Niveau Intermédiaire

> **Fichier :** `napalm-intermediaire.md`  
> **Parcours :** Automatisation réseau avec NAPALM — niveau 2 sur 3  
> **Prérequis :** avoir étudié `napalm-debutant.md` et savoir exécuter un script Python qui se connecte à un équipement de laboratoire.  
> **Révision documentaire :** 23 octobre 2026. La page PyPI et les versions publiées du dépôt indiquent NAPALM 5.2.0 comme version la plus récente vérifiée à cette date. NAPALM 5.2.0 demande Python 3.10 ou plus. Vérifiez toujours l'état réel des dépendances dans votre environnement avant une installation.


## 0. La place de ce niveau dans le parcours

Ce document **ne recommence pas le niveau Débutant** et ne constitue pas une formation indépendante. Il prolonge les bases déjà acquises : création d'un environnement virtuel, installation de NAPALM et de son pilote, sélection d'un pilote avec `get_network_driver()`, ouverture et fermeture d'une session, récupération des informations de base, compréhension des getters, lecture d'un inventaire YAML, chargement d'une configuration candidate et précautions élémentaires avant un commit.

Le changement de niveau correspond à un changement de posture. Au niveau Débutant, on apprend à exécuter une opération sur un équipement. Au niveau Intermédiaire, on apprend à **industrialiser cette opération**, à traiter plusieurs équipements de façon cohérente, à vérifier la qualité des résultats, à détecter des écarts, à produire des rapports exploitables et à encadrer les changements avec une procédure de sécurité.

Au terme du niveau, vous devrez être capable de transformer quelques scripts isolés en un petit outil d'automatisation maintenable. Cet outil devra distinguer une collecte réussie d'une collecte partielle, éviter qu'une panne de connexion arrête tout le parc, conserver un historique lisible, comparer un état réel à un état attendu, et bloquer un changement tant que ses contrôles n'ont pas été effectués.

### 0.1 Ce qui est réutilisé du niveau Débutant

Vous devez déjà comprendre les éléments suivants :

- la relation entre le nom du pilote NAPALM et le système d'exploitation réseau ciblé ;
- la différence entre construire un objet `NetworkDriver` et ouvrir réellement une session ;
- le rôle de `open()`, `close()` et des getters tels que `get_facts()`, `get_interfaces()`, `get_interfaces_ip()` et `get_lldp_neighbors()` ;
- la différence entre `load_merge_candidate()` et `load_replace_candidate()` ;
- le fait qu'un chargement de configuration candidate ne doit pas être confondu avec une modification déjà appliquée ;
- l'importance de `compare_config()` avant `commit_config()` ;
- le rôle de `discard_config()` quand une candidate ne doit pas être appliquée.

Si un de ces éléments reste flou, consolidez-le dans le fichier du niveau Débutant avant de poursuivre. Un niveau intermédiaire solide dépend de fondamentaux fiables.

### 0.2 Carte de progression des trois niveaux

```text
NIVEAU 1 — DÉBUTANT
Connexion • premiers getters • inventaire simple • première candidate
        │
        ▼
NIVEAU 2 — INTERMÉDIAIRE (ce document)
Qualité des données • multi-équipements • normalisation • conformité
Diffs exploitables • tests • changements contrôlés • rapports reproductibles
        │
        ▼
NIVEAU 3 — EXPERT
Architecture de production • orchestration avancée • politiques de déploiement
Observabilité • CI/CD • gestion des risques à grande échelle • extensibilité
```

Le niveau Expert devra pouvoir reprendre les fonctions, les conventions et les résultats définis ici. Pour cela, nous allons utiliser une structure de projet stable et des contrats de données explicites plutôt que d'accumuler des scripts jetables.

### 0.3 Objectifs mesurables

À la fin de ce cours, vous saurez :

1. charger et valider un inventaire enrichi sans exposer les secrets dans le code ;
2. exécuter une collecte sur plusieurs équipements en isolant les erreurs par équipement ;
3. normaliser et sauvegarder les résultats dans des fichiers JSON horodatés ;
4. vérifier des invariants simples sur les interfaces, les versions, les voisins ou les sessions BGP lorsque le pilote le permet ;
5. utiliser les rapports de conformité NAPALM pour comparer un état observé à un état attendu ;
6. produire un rapport indiquant les équipements conformes, non conformes, injoignables ou partiellement analysés ;
7. préparer un changement, examiner son diff, appliquer un déploiement prudent et vérifier le résultat ;
8. tester les fonctions Python sans devoir se connecter à un commutateur ou à un routeur réel ;
9. diagnostiquer un échec en séparant les problèmes d'inventaire, d'authentification, de transport, de pilote, de données et de configuration.


# 1. Concevoir un outil, pas seulement un script

## 1.1 Le défaut du script monolithique

Un script court qui se connecte à un routeur, appelle `get_facts()` et affiche le résultat est utile pour apprendre. Il devient toutefois fragile dès qu'on lui ajoute plusieurs équipements, une sortie JSON, une validation d'état et une action de configuration.

Un script monolithique finit souvent par mélanger cinq responsabilités :

- la connaissance du parc et de ses adresses ;
- la gestion des identifiants et des sessions ;
- les appels NAPALM ;
- la vérification des résultats ;
- l'affichage ou l'archivage des résultats.

Quand ces responsabilités sont entremêlées, un changement dans l'inventaire peut casser la collecte, une erreur de connexion peut interrompre toute l'exécution, et une sortie conçue pour être affichée à l'écran devient difficile à réutiliser dans un autre outil.

La règle de ce niveau est simple : **séparer les responsabilités sans compliquer inutilement le projet**.

## 1.2 Architecture minimale recommandée

```text
Inventaire YAML ──► Validation de l'inventaire
                           │
                           ▼
                    Collecteur NAPALM
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
         État normalisé        Erreurs isolées
                │                     │
                └──────────┬──────────┘
                           ▼
                 Instantané JSON daté
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
        Contrôles techniques   Rapport de conformité
                │                     │
                └──────────┬──────────┘
                           ▼
                    Rapport global
```

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500" role="img" aria-labelledby="napint-arch-title napint-arch-desc" width="1000" height="500" style="max-width:100%;display:block">
  <title id="napint-arch-title">Architecture d'un collecteur NAPALM intermédiaire</title>
  <desc id="napint-arch-desc">Sur un fond bleu nuit, l'inventaire validé alimente un collecteur NAPALM. Le collecteur sépare l'état collecté des erreurs, puis alimente les instantanés, les contrôles et le rapport consolidé.</desc>
  <defs>
    <marker id="napint-arch-arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,8 L9,4 z" fill="#52d6f4"/></marker>
    <linearGradient id="napint-arch-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1424"/><stop offset="1" stop-color="#121f35"/></linearGradient>
    <linearGradient id="napint-arch-card" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#192a43"/><stop offset="1" stop-color="#122137"/></linearGradient>
  </defs>
  <rect x="0" y="0" width="1000" height="500" rx="20" fill="url(#napint-arch-bg)"/>
  <text x="34" y="38" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="22" font-weight="700" fill="#f3f7ff">Pipeline de collecte NAPALM</text>
  <text x="34" y="61" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#9eb2cc">Inventaire → collecte isolée → données historisées → contrôles → rapport</text>
  <rect x="324" y="82" width="352" height="58" rx="12" fill="url(#napint-arch-card)" stroke="#8b9cff" stroke-width="1.8"/>
  <rect x="324" y="82" width="6" height="58" rx="3" fill="#a6a6ff"/>
  <text x="500" y="105" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Inventaire YAML validé</text>
  <text x="500" y="124" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">périmètre · rôle · paramètres · secrets référencés</text>
  <path d="M500 140 V163" fill="none" stroke="#52d6f4" stroke-width="2.5" stroke-dasharray="7 7" marker-end="url(#napint-arch-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-56" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="324" y="166" width="352" height="60" rx="12" fill="url(#napint-arch-card)" stroke="#52d6f4" stroke-width="1.8"/>
  <rect x="324" y="166" width="6" height="60" rx="3" fill="#52d6f4"/>
  <text x="500" y="190" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Collecteur NAPALM</text>
  <text x="500" y="209" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">une session indépendante par équipement</text>
  <path d="M500 226 V246 H255 V267" fill="none" stroke="#52d6f4" stroke-width="2.5" stroke-dasharray="7 7" marker-end="url(#napint-arch-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-56" dur="2.8s" repeatCount="indefinite"/></path>
  <path d="M500 246 H745 V267" fill="none" stroke="#ffb86b" stroke-width="2.5" stroke-dasharray="7 7" marker-end="url(#napint-arch-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-56" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="55" y="270" width="400" height="66" rx="12" fill="#112c32" stroke="#47d7b0" stroke-width="1.8"/>
  <rect x="55" y="270" width="6" height="66" rx="3" fill="#47d7b0"/>
  <text x="255" y="295" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="16" font-weight="700" fill="#eafff8">État normalisé</text>
  <text x="255" y="316" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#a8ddd0">facts · interfaces · voisins · protocoles</text>
  <rect x="545" y="270" width="400" height="66" rx="12" fill="#33251f" stroke="#ffb86b" stroke-width="1.8"/>
  <rect x="545" y="270" width="6" height="66" rx="3" fill="#ffb86b"/>
  <text x="745" y="295" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="16" font-weight="700" fill="#fff4e8">Erreur isolée et traçable</text>
  <text x="745" y="316" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#e8c8a8">équipement · étape · catégorie · message</text>
  <path d="M255 336 V361 H500" fill="none" stroke="#47d7b0" stroke-width="2.5" stroke-dasharray="7 7"><animate attributeName="stroke-dashoffset" from="0" to="-56" dur="3.2s" repeatCount="indefinite"/></path>
  <path d="M745 336 V361 H500" fill="none" stroke="#ffb86b" stroke-width="2.5" stroke-dasharray="7 7"><animate attributeName="stroke-dashoffset" from="0" to="-56" dur="3.2s" repeatCount="indefinite"/></path>
  <path d="M500 361 V379" fill="none" stroke="#52d6f4" stroke-width="2.5" stroke-dasharray="7 7" marker-end="url(#napint-arch-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-56" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="300" y="382" width="400" height="48" rx="11" fill="url(#napint-arch-card)" stroke="#6d9eff" stroke-width="1.8"/>
  <text x="500" y="411" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#edf4ff">Instantanés versionnés + contrôles</text>
  <path d="M500 430 V449" fill="none" stroke="#52d6f4" stroke-width="2.5" stroke-dasharray="7 7" marker-end="url(#napint-arch-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-56" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="300" y="452" width="400" height="35" rx="10" fill="#18344b" stroke="#52d6f4" stroke-width="1.8"/>
  <text x="500" y="474" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3faff">Rapport global exploitable</text>
</svg>

Le schéma montre un flux d'information, pas une promesse que toute collecte réussira. Un système robuste conserve les échecs comme des résultats explicites au lieu de les masquer ou de perdre les résultats des autres appareils.

## 1.3 Arborescence du projet

Pour les exercices, créez la structure suivante :

```text
napalm-intermediaire/
├── inventory/
│   └── devices.yml
├── config/
│   └── validation.yml
├── snapshots/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── inventory.py
│   ├── collector.py
│   ├── checks.py
│   └── report.py
├── tests/
│   ├── test_inventory.py
│   └── test_checks.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Cette organisation demeure volontairement modeste. Elle est assez claire pour séparer l'inventaire, la collecte, les contrôles, les tests et les résultats. Le niveau Expert pourra ensuite introduire un orchestrateur, une base de données, une file de tâches ou une chaîne CI/CD sans devoir réécrire toute la logique métier.

Exemple de `requirements.txt` :

```text
napalm==5.2.0
PyYAML>=6.0
pytest>=8.0
```

Ces versions servent de base de laboratoire, pas de politique universelle de dépendances. Dans un projet partagé, verrouillez toutes les dépendances dans un fichier de lock généré et vérifié, validez la compatibilité avec le pilote choisi, puis déployez la même résolution de dépendances en test et en production.

Exemple de `.gitignore` :

```gitignore
.venv/
__pycache__/
.pytest_cache/
.env
snapshots/*.json
reports/*.json
reports/*.html
*.log
```

Si les snapshots doivent être suivis dans un dépôt, décidez explicitement quels champs peuvent y être conservés. Les configurations, adresses, noms internes et sorties détaillées peuvent révéler des informations sensibles. Ne versionnez pas automatiquement l'ensemble des données collectées.


# 2. Inventaire enrichi, validation et gestion des secrets

## 2.1 Pourquoi l'inventaire devient une donnée de premier ordre

Dans le niveau Débutant, un inventaire peut se limiter à une liste d'équipements et à leur pilote. À mesure que le parc grandit, cette liste doit aussi décrire l'identité logique de chaque appareil : site, rôle, environnement, criticité, groupe de déploiement et référence du secret à utiliser.

L'inventaire est une source de données opérationnelles. Une faute de frappe dans `hostname`, un pilote erroné ou une variable d'environnement inexistante peut faire échouer la collecte. Une valeur valide au niveau YAML n'est pas nécessairement une valeur valide au niveau métier ; il faut donc contrôler les deux.

## 2.2 Exemple d'inventaire

Fichier `inventory/devices.yml` :

```yaml
version: 1

defaults:
  timeout: 30
  username_env: NAPALM_USERNAME
  password_env: NAPALM_PASSWORD

devices:
  - name: core-r1
    hostname: 192.0.2.11
    driver: ios
    site: douala-dc1
    role: core-router
    environment: lab
    criticality: high
    enabled: true
    groups: [core, lab]

  - name: access-sw1
    hostname: 192.0.2.21
    driver: eos
    site: douala-office
    role: access-switch
    environment: lab
    criticality: medium
    enabled: true
    groups: [access, lab]

  - name: edge-j1
    hostname: 192.0.2.31
    driver: junos
    site: douala-dc1
    role: edge-router
    environment: lab
    criticality: high
    enabled: false
    groups: [edge, lab]
```

Les adresses `192.0.2.0/24` appartiennent au bloc réservé à la documentation. Remplacez-les par les adresses de votre réseau de laboratoire. Les noms de pilotes ne sont que des exemples : vérifiez que le pilote est installé, que le modèle et la version logicielle ciblés sont compatibles, et que les getters dont vous avez besoin sont effectivement pris en charge.

Le secret n'est pas stocké dans ce fichier. Le nom `NAPALM_USERNAME` indique où trouver l'identifiant et `NAPALM_PASSWORD` où trouver le mot de passe. Dans un environnement de production, privilégiez un gestionnaire de secrets adapté, des identifiants à privilèges minimaux, une rotation périodique et des comptes de service distincts selon l'usage.

## 2.3 Charger le YAML sans faire confiance au fichier

Avec PyYAML, utilisez `yaml.safe_load()` pour lire un fichier de données. Évitez `yaml.load()` sans chargeur sûr sur des documents non fiables.

Fichier `src/inventory.py` :

```python
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

REQUIRED_DEVICE_FIELDS = {
    "name", "hostname", "driver", "site", "role", "environment", "enabled"
}
ALLOWED_ENVIRONMENTS = {"lab", "staging", "production"}


def load_inventory(path: str | Path) -> dict[str, Any]:
    """Charge l'inventaire YAML et vérifie sa structure minimale."""
    inventory_path = Path(path)
    with inventory_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)

    if not isinstance(data, dict):
        raise ValueError("L'inventaire doit être un objet YAML au niveau racine.")

    devices = data.get("devices")
    if not isinstance(devices, list):
        raise ValueError("La clé 'devices' doit contenir une liste.")

    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("La clé 'defaults' doit être un objet YAML.")

    seen_names: set[str] = set()
    for index, device in enumerate(devices):
        prefix = f"devices[{index}]"
        if not isinstance(device, dict):
            raise ValueError(f"{prefix} doit être un objet YAML.")

        missing = REQUIRED_DEVICE_FIELDS - device.keys()
        if missing:
            raise ValueError(f"{prefix} : champs manquants : {sorted(missing)}")

        name = device["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{prefix}.name doit être une chaîne non vide.")
        if name in seen_names:
            raise ValueError(f"Nom d'équipement dupliqué : {name}")
        seen_names.add(name)

        for field in ("hostname", "driver", "site", "role", "environment"):
            if not isinstance(device[field], str) or not device[field].strip():
                raise ValueError(f"{prefix}.{field} doit être une chaîne non vide.")

        if device["environment"] not in ALLOWED_ENVIRONMENTS:
            raise ValueError(
                f"{prefix}.environment doit être l'un de {sorted(ALLOWED_ENVIRONMENTS)}"
            )

        if not isinstance(device["enabled"], bool):
            raise ValueError(f"{prefix}.enabled doit être un booléen YAML.")

        groups = device.get("groups", [])
        if not isinstance(groups, list) or not all(isinstance(g, str) for g in groups):
            raise ValueError(f"{prefix}.groups doit être une liste de chaînes.")

    return data
```

Cette validation ne teste pas encore si une adresse IP est joignable, si un pilote NAPALM existe réellement ou si les identifiants sont corrects. Ce sont des contrôles distincts. Il est préférable que chaque contrôle soit explicite et que l'erreur dise à quelle étape il s'est produit.

## 2.4 Fusionner les paramètres par défaut

Un outil de parc doit appliquer des valeurs par défaut sans écraser une valeur spécifique d'un équipement. Pour cet exercice, utilisez une fonction dédiée :

```python
from typing import Any


def effective_device_config(
    defaults: dict[str, Any], device: dict[str, Any]
) -> dict[str, Any]:
    """Renvoie la configuration effective, propre à un équipement."""
    return {**defaults, **device}
```

La syntaxe `{**defaults, **device}` signifie que les valeurs de `device` prévalent sur les valeurs de `defaults` en cas de collision. C'est généralement le comportement attendu : un équipement peut avoir un délai d'attente spécifique sans obliger à changer la valeur par défaut pour tout le parc.

Dans un projet plus large, documentez la priorité entre les valeurs globales, les groupes, le site, l'environnement et l'équipement. Une hiérarchie implicite et mal comprise est une source classique d'erreurs opérationnelles.

## 2.5 Lire les identifiants depuis l'environnement

```python
import os


def get_credentials(config: dict) -> tuple[str, str]:
    username_key = config.get("username_env", "NAPALM_USERNAME")
    password_key = config.get("password_env", "NAPALM_PASSWORD")

    username = os.getenv(username_key)
    password = os.getenv(password_key)

    missing = [
        key for key, value in ((username_key, username), (password_key, password))
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Variables d'identifiants manquantes ou vides : " + ", ".join(missing)
        )

    return username, password  # type: ignore[return-value]
```

Le commentaire de typage ne remplace pas une validation runtime ; ici, les valeurs ont été contrôlées juste avant le retour. Une variante stricte peut affecter des variables locales après validation ou définir un objet de configuration typé.

Fichier `.env.example` (exemple explicatif, non destiné à contenir de vrais secrets) :

```dotenv
NAPALM_USERNAME=compte_automatisation
NAPALM_PASSWORD=remplacer_par_un_secret_de_laboratoire
```

Ne commitez jamais un fichier `.env` contenant les secrets réels. N'imprimez pas le mot de passe, ne l'incluez pas dans les messages d'exception personnalisés et veillez à ce que les journaux n'enregistrent pas les paramètres de connexion complets.

### Exercice 2.1 — Contrôle de l'inventaire

1. Supprimez le champ `driver` d'un équipement : la validation doit échouer et nommer l'équipement ou son index.
2. Ajoutez deux équipements portant le même champ `name` : la validation doit repérer le doublon.
3. Remplacez `enabled: true` par `enabled: "true"` : la validation doit refuser la chaîne, car un booléen YAML et du texte ne sont pas équivalents.
4. Ajoutez un environnement non autorisé : la validation doit l'identifier.
5. Reprenez ensuite l'inventaire correct et confirmez qu'il est chargé.


# 3. Établir un contrat de collecte fiable

## 3.1 Une collecte doit avoir une forme connue

Une fonction de collecte doit préciser ce qu'elle garantit. Elle ne doit pas retourner tantôt une chaîne, tantôt un dictionnaire, tantôt `None` selon le type d'échec. Une structure uniforme est plus facile à journaliser, tester, sauvegarder et agréger.

Pour notre projet, chaque résultat aura les champs suivants :

```json
{
  "device": "core-r1",
  "hostname": "192.0.2.11",
  "driver": "ios",
  "status": "success",
  "started_at": "2026-10-23T10:15:00+00:00",
  "duration_seconds": 1.42,
  "data": {
    "facts": {},
    "interfaces": {},
    "interfaces_ip": {},
    "lldp_neighbors": {}
  },
  "errors": []
}
```

Les valeurs de cet exemple sont illustratives. Un résultat réel contiendra les structures fournies par le pilote. Pour un résultat en échec, `status` pourra être `error` ou `partial`, et `errors` contiendra au minimum l'étape qui a échoué et un message débarrassé de toute donnée secrète.

## 3.2 Choisir entre échec total et échec partiel

La notion d'échec partiel doit être définie, pas improvisée au moment de la panne.

- **`success`** : toutes les opérations obligatoires de la collecte ont réussi.
- **`partial`** : la session a été établie et certaines données utiles ont été obtenues, mais au moins un getter attendu a échoué ou n'est pas implémenté par ce pilote.
- **`error`** : la collecte n'a pas pu atteindre un état de résultat utile, par exemple à cause d'un échec de connexion ou d'une erreur empêchant l'initialisation.
- **`skipped`** : l'équipement a été volontairement exclu, par exemple parce que `enabled` vaut `false`.

Ces états ne doivent pas être présentés comme interchangeables. « Aucun voisin trouvé » peut être un résultat valide. « Impossible de récupérer les voisins » est un échec de collecte. « Getter non pris en charge » signifie que ce contrôle ne peut pas être affirmé pour ce pilote sans autre méthode.

## 3.3 Pourquoi ne pas supposer que tous les pilotes sont identiques

NAPALM définit une interface commune, mais la prise en charge de méthodes et de fonctionnalités dépend du pilote, de l'équipement et de sa version logicielle. Le fait que `get_bgp_neighbors_detail()` fonctionne sur un appareil ne garantit pas qu'il fonctionnera sur un autre. Un appel peut lever `NotImplementedError` ou une exception propre au pilote.

Avant d'ajouter un getter à la collecte standard, consultez la matrice de prise en charge et testez-le sur la combinaison précise pilote/modèle/version que vous exploitez. Pour les contrôles indispensables, distinguez clairement « non conforme » de « non vérifiable ».

Références techniques :

- [Documentation NAPALM — NetworkDriver](https://napalm.readthedocs.io/en/latest/base.html)
- [Documentation NAPALM — pilotes et équipements pris en charge](https://napalm.readthedocs.io/en/stable/support/)


# 4. Construire un collecteur multi-équipements

## 4.1 Règles d'implémentation

La fonction suivante introduit quelques éléments plus professionnels que le script débutant :

- chaque appel prend un objet d'équipement explicite ;
- l'horodatage est enregistré en UTC ;
- la durée utilise une horloge monotone ;
- la session est fermée par un gestionnaire de contexte ;
- les erreurs sont attachées à l'équipement concerné ;
- le reste de la collecte peut continuer même si un getter échoue ;
- les données sont organisées par nom de getter pour faciliter les contrôles ultérieurs.

**Important :** le gestionnaire de contexte est utilisable si l'objet `NetworkDriver` du pilote et de la version installés le prend en charge. Si votre combinaison de pilote ne le permet pas, remplacez-le par un `open()` puis un `close()` dans un bloc `try/finally`. La fermeture doit être exécutée autant que possible même après une exception.

## 4.2 Première version du collecteur

Fichier `src/collector.py` :

```python
from __future__ import annotations

from datetime import datetime, timezone
from time import monotonic
from typing import Any, Callable

from napalm import get_network_driver

GETTERS: dict[str, Callable[[Any], Any]] = {
    "facts": lambda device: device.get_facts(),
    "interfaces": lambda device: device.get_interfaces(),
    "interfaces_ip": lambda device: device.get_interfaces_ip(),
    "lldp_neighbors": lambda device: device.get_lldp_neighbors(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def collect_one(
    config: dict[str, Any],
    username: str,
    password: str,
) -> dict[str, Any]:
    """Collecte plusieurs getters sur un seul équipement, sans propager l'échec."""
    started_at = utc_now()
    timer_start = monotonic()
    result: dict[str, Any] = {
        "device": config["name"],
        "hostname": config["hostname"],
        "driver": config["driver"],
        "status": "error",
        "started_at": started_at,
        "duration_seconds": None,
        "data": {},
        "errors": [],
    }

    try:
        driver_factory = get_network_driver(config["driver"])
        timeout = int(config.get("timeout", 30))
        device = driver_factory(
            hostname=config["hostname"],
            username=username,
            password=password,
            timeout=timeout,
            optional_args=config.get("optional_args", {}),
        )

        # Le gestionnaire de contexte assure la fermeture si le pilote le supporte.
        with device:
            for data_key, getter in GETTERS.items():
                try:
                    result["data"][data_key] = getter(device)
                except NotImplementedError as exc:
                    result["errors"].append({
                        "stage": data_key,
                        "kind": "unsupported",
                        "message": str(exc) or "Getter non pris en charge par ce pilote.",
                    })
                except Exception as exc:
                    result["errors"].append({
                        "stage": data_key,
                        "kind": "getter_error",
                        "message": f"{type(exc).__name__}: {exc}",
                    })

        if result["errors"]:
            result["status"] = "partial" if result["data"] else "error"
        else:
            result["status"] = "success"

    except Exception as exc:
        result["errors"].append({
            "stage": "connection_or_driver_setup",
            "kind": "connection_error",
            "message": f"{type(exc).__name__}: {exc}",
        })

    finally:
        result["duration_seconds"] = round(monotonic() - timer_start, 3)

    return result
```

### Point de vigilance sur les exceptions

Ce code capture volontairement les exceptions afin de produire un résultat par appareil. Il ne signifie pas qu'il faut ignorer toutes les exceptions dans une application de production. Une exception peut indiquer un problème de code, une dépendance incompatible, une erreur de configuration ou une panne d'infrastructure. La bonne pratique consiste à conserver le type, l'étape et le contexte utile, à éviter de journaliser les secrets, et à définir les exceptions qui doivent arrêter le traitement global.

L'exemple privilégie la poursuite de la collecte pour les autres équipements. Dans une chaîne de déploiement, une erreur sur un équipement critique peut au contraire imposer l'arrêt du lot. Ce choix doit être relié à la politique de risque, pas seulement au confort de programmation.

## 4.3 Faut-il appeler tous les getters ?

Pas nécessairement. Plus une collecte est large, plus elle prend du temps, sollicite les équipements et produit des données à protéger. Dans un véritable outil, définissez plusieurs profils de collecte :

- **rapide** : identité de l'appareil, statut des interfaces et quelques contrôles de santé ;
- **standard** : inventaire, adressage, voisins et paramètres de routage utiles ;
- **audit** : collecte plus complète, détails supplémentaires et instantané de configuration, si la politique l'autorise.

Un profil d'audit ne doit pas être lancé à haute fréquence sans raison. Les getters ont des coûts différents et certains pilotes effectuent plusieurs commandes sous-jacentes. La fréquence doit donc être testée en laboratoire et dimensionnée selon les appareils et les fenêtres opérationnelles.

## 4.4 Distinguer une interface arrêtée d'une donnée absente

Considérez les états typiques de `get_interfaces()` :

```python
{
    "GigabitEthernet1": {
        "is_up": True,
        "is_enabled": True,
        "description": "Uplink vers distribution",
        "last_flapped": -1.0,
        "speed": 1000.0,
        "mtu": 1500,
        "mac_address": "00:11:22:33:44:55"
    }
}
```

Il s'agit d'un exemple de forme de données ; le résultat réel et certains champs dépendent du pilote. Il faut différencier au moins ces situations :

- l'interface existe et est opérationnelle ;
- l'interface existe mais le lien est down ;
- l'interface est administrativement désactivée ;
- le getter a réussi mais cette interface n'apparaît pas ;
- le getter lui-même a échoué ;
- la donnée n'est pas disponible ou a une valeur sentinelle pour ce pilote.

Ne transformez pas systématiquement une valeur comme `-1.0` en une date ou un compteur réel. Lisez les conventions du getter concerné et consignez la limite de la donnée.

### Exercice 4.1 — Collecter deux appareils

1. Créez un inventaire de laboratoire avec deux équipements réellement disponibles, idéalement utilisant des pilotes différents si vous pouvez le faire sans risque.
2. Exécutez `collect_one()` pour chaque équipement.
3. Ajoutez volontairement une adresse inaccessible pour le troisième cas de test.
4. Vérifiez qu'un échec de connexion produit un résultat `error` pour cet appareil mais n'efface pas les résultats valides des autres.
5. Retirez ensuite ce faux équipement de l'inventaire opérationnel.


# 5. Exécution en parallèle avec une limite de concurrence

## 5.1 Pourquoi le parallèle n'est pas automatiquement meilleur

Les sessions réseau comportent des temps d'attente. Un traitement séquentiel peut être lent lorsqu'un parc compte plusieurs dizaines d'équipements. Le parallélisme permet d'attendre plusieurs équipements en même temps, mais lancer trop de sessions simultanées peut saturer les équipements, le serveur d'automatisation, le réseau de gestion ou le service d'authentification.

La bonne approche est le **parallélisme borné** : une limite configurable, mesurée et ajustée à la capacité réelle du parc.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 430" role="img" aria-labelledby="napint-par-title napint-par-desc" width="1080" height="430" style="max-width:100%;display:block">
  <title id="napint-par-title">Collecte séquentielle comparée à une collecte parallèle bornée</title>
  <desc id="napint-par-desc">Deux panneaux contrastés expliquent la différence entre exécuter les appareils un par un et distribuer les tâches entre un nombre limité de travailleurs.</desc>
  <defs>
    <marker id="napint-par-arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,8 L9,4 z" fill="#52d6f4"/></marker>
    <linearGradient id="napint-par-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1424"/><stop offset="1" stop-color="#121f35"/></linearGradient>
  </defs>
  <rect width="1080" height="430" rx="20" fill="url(#napint-par-bg)"/>
  <text x="30" y="38" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="22" font-weight="700" fill="#f3f7ff">Deux stratégies d'exécution</text>
  <rect x="28" y="60" width="425" height="340" rx="16" fill="#101e31" stroke="#53677f" stroke-width="1.5"/>
  <rect x="473" y="60" width="579" height="340" rx="16" fill="#101e31" stroke="#52d6f4" stroke-width="1.5"/>
  <text x="240" y="91" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="17" font-weight="700" fill="#d9e5f4">Séquentiel</text>
  <text x="762" y="91" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="17" font-weight="700" fill="#a4efff">Parallèle borné</text>
  <rect x="58" y="110" width="365" height="58" rx="10" fill="#1a2c43" stroke="#6d9eff" stroke-width="1.4"/>
  <text x="240" y="133" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Équipement A</text><text x="240" y="151" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">connexion · getters · fermeture</text>
  <path d="M240 168 V184" fill="none" stroke="#52d6f4" stroke-width="2.2" stroke-dasharray="6 6" marker-end="url(#napint-par-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-48" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="58" y="187" width="365" height="58" rx="10" fill="#1a2c43" stroke="#6d9eff" stroke-width="1.4"/>
  <text x="240" y="210" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Équipement B</text><text x="240" y="228" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">démarre après la fin de A</text>
  <path d="M240 245 V261" fill="none" stroke="#52d6f4" stroke-width="2.2" stroke-dasharray="6 6" marker-end="url(#napint-par-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-48" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="58" y="264" width="365" height="58" rx="10" fill="#1a2c43" stroke="#6d9eff" stroke-width="1.4"/>
  <text x="240" y="287" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Équipement C</text><text x="240" y="305" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">simple à diagnostiquer, parfois lent</text>
  <text x="240" y="366" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#9eb2cc">1 seul traitement actif à la fois</text>
  <rect x="523" y="110" width="479" height="50" rx="10" fill="#172d43" stroke="#52d6f4" stroke-width="1.5"/>
  <text x="762" y="131" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3faff">Ordonnanceur</text><text x="762" y="148" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#a4efff">max_workers = limite explicite</text>
  <path d="M762 160 V180 H600 V197 M762 180 V197 M762 180 H924 V197" fill="none" stroke="#52d6f4" stroke-width="2.2" stroke-dasharray="6 6" marker-end="url(#napint-par-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-48" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="526" y="200" width="148" height="59" rx="10" fill="#112e32" stroke="#47d7b0" stroke-width="1.5"/>
  <text x="600" y="223" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" fill="#eafff8">Worker 1</text><text x="600" y="242" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#a8ddd0">appareil A</text>
  <rect x="688" y="200" width="148" height="59" rx="10" fill="#112e32" stroke="#47d7b0" stroke-width="1.5"/>
  <text x="762" y="223" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" fill="#eafff8">Worker 2</text><text x="762" y="242" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#a8ddd0">appareil B</text>
  <rect x="850" y="200" width="148" height="59" rx="10" fill="#112e32" stroke="#47d7b0" stroke-width="1.5"/>
  <text x="924" y="223" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" fill="#eafff8">Worker N</text><text x="924" y="242" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#a8ddd0">limite respectée</text>
  <path d="M600 259 V279 H762" fill="none" stroke="#52d6f4" stroke-width="2.2" stroke-dasharray="6 6"><animate attributeName="stroke-dashoffset" from="0" to="-48" dur="2.8s" repeatCount="indefinite"/></path>
  <path d="M924 259 V279 H762" fill="none" stroke="#52d6f4" stroke-width="2.2" stroke-dasharray="6 6"><animate attributeName="stroke-dashoffset" from="0" to="-48" dur="2.8s" repeatCount="indefinite"/></path>
  <path d="M762 259 V294" fill="none" stroke="#52d6f4" stroke-width="2.2" stroke-dasharray="6 6" marker-end="url(#napint-par-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-48" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="612" y="297" width="300" height="54" rx="10" fill="#1a2c43" stroke="#8b9cff" stroke-width="1.5"/>
  <text x="762" y="319" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Résultats agrégés</text><text x="762" y="338" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">succès · erreurs · durées par appareil</text>
  <text x="762" y="376" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#9eb2cc">Plus rapide, à condition de borner et mesurer la charge</text>
</svg>

## 5.2 Exemple avec `ThreadPoolExecutor`

Ajoutez ce code au-dessus du point d'entrée de votre programme ou dans un module dédié :

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any


def collect_many(
    devices: list[dict[str, Any]],
    username: str,
    password: str,
    max_workers: int = 4,
) -> list[dict[str, Any]]:
    """Collecte un ensemble d'équipements avec une concurrence bornée."""
    if max_workers < 1:
        raise ValueError("max_workers doit être supérieur ou égal à 1.")

    results: list[dict[str, Any]] = []
    enabled_devices = [device for device in devices if device.get("enabled", True)]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(collect_one, device, username, password): device
            for device in enabled_devices
        }

        for future in as_completed(futures):
            device_config = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                # Garde-fou : collect_one est censée capturer les erreurs usuelles.
                results.append({
                    "device": device_config.get("name", "unknown"),
                    "hostname": device_config.get("hostname"),
                    "driver": device_config.get("driver"),
                    "status": "error",
                    "data": {},
                    "errors": [{
                        "stage": "worker",
                        "kind": "unexpected_error",
                        "message": f"{type(exc).__name__}: {exc}",
                    }],
                })

    # L'ordre de fin est non déterministe : retrier pour un rapport stable.
    return sorted(results, key=lambda item: str(item.get("device", "")))
```

La limite `max_workers=4` est un point de départ d'exercice, pas un réglage universel. Mesurez le temps moyen et maximal, observez la charge, les erreurs de transport, les contrôles d'accès et le comportement de vos appareils avant d'augmenter la concurrence.

Chaque tâche construit sa propre instance `NetworkDriver`. Ne partagez pas un même objet de session entre plusieurs threads. En cas de besoin, testez aussi le comportement des bibliothèques et pilotes sous-jacents avec la version précise utilisée.

## 5.3 Distinguer débit, délai d'attente et délai total

Trois paramètres se ressemblent mais ne veulent pas dire la même chose :

- le délai d'attente passé à un pilote peut être utilisé pour certaines opérations de connexion ou de commande ;
- le délai total d'une collecte est la durée réelle de la totalité du travail ;
- la limite de concurrence est le nombre maximum d'opérations simultanées que votre ordonnanceur autorise.

Un timeout par commande n'implique pas toujours un timeout global pour une collecte comprenant plusieurs getters. Si le processus doit avoir une durée maximale stricte, définissez une politique d'exécution et d'annulation explicite, puis vérifiez que le pilote est capable d'interrompre effectivement ses opérations. L'annulation d'un `Future` ne garantit pas à elle seule qu'un appel réseau bloqué a été interrompu.

### Exercice 5.1 — Mesurer avant d'optimiser

Lancez la même collecte en mode séquentiel, puis avec `max_workers=2`, puis avec `max_workers=4`. Pour chaque essai, consignez le nombre d'équipements, la durée totale, le nombre de succès, de résultats partiels et d'erreurs. Ne comparez pas des tests réalisés dans des conditions de réseau très différentes.

Votre objectif n'est pas seulement de réduire la durée. Il faut préserver une qualité de données et un taux de réussite satisfaisants.


# 6. Normaliser et archiver les résultats

## 6.1 Pourquoi produire des instantanés

Un dictionnaire de résultat affiché dans le terminal disparaît à la fin du programme. Un instantané daté permet de retrouver ce que l'outil a observé à un moment donné, de diagnostiquer une évolution et de comparer deux exécutions.

Conservez le contexte minimal : date de collecte, version du logiciel d'automatisation, identité logique de l'équipement, statut de collecte, durée, données utiles et erreurs. Évitez de stocker plus de données que nécessaire. Les configurations complètes et les tables détaillées peuvent être sensibles et volumineuses.

## 6.2 Sauvegarde JSON robuste

```python
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any


def save_snapshot(
    results: list[dict[str, Any]],
    output_dir: str | Path = "snapshots",
) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = out_dir / f"snapshot-{timestamp}.json"

    payload = {
        "schema_version": 1,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "result_count": len(results),
        "results": results,
    }

    # allow_nan=False évite de produire des valeurs NaN/Infinity non standard.
    with output_path.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")

    return output_path
```

Il est utile d'ajouter une version du schéma (`schema_version`). Quand votre format évoluera, un lecteur pourra savoir comment interpréter un ancien fichier. Si vous renommez un champ utilisé par les rapports, vous pourrez prévoir une migration au lieu de supposer que tous les fichiers archivés correspondent au format actuel.

Attention : une valeur renvoyée par un pilote peut ne pas être directement sérialisable en JSON, selon le getter ou l'extension utilisée. Si `json.dump()` échoue, inspectez le type exact et décidez d'une conversion explicite. Évitez d'utiliser par défaut `default=str` pour tout : cela peut masquer un changement de type en transformant silencieusement des objets structurés en chaînes difficiles à traiter.

## 6.3 Créer le rapport global

```python
from collections import Counter
from typing import Any


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = Counter(str(item.get("status", "unknown")) for item in results)
    errors = []

    for item in results:
        for error in item.get("errors", []):
            errors.append({
                "device": item.get("device", "unknown"),
                "stage": error.get("stage", "unknown"),
                "kind": error.get("kind", "unknown"),
                "message": error.get("message", ""),
            })

    return {
        "device_count": len(results),
        "status_counts": dict(statuses),
        "error_count": len(errors),
        "errors": errors,
    }
```

Ce résumé évite une erreur de présentation fréquente : afficher uniquement les échecs et laisser croire que tous les appareils non mentionnés sont conformes. Un rapport doit indiquer combien d'appareils ont été attendus, combien ont été analysés, combien ont été ignorés et combien n'ont pas pu être vérifiés.

## 6.4 Pourquoi l'identité et l'horodatage doivent être explicites

Ne vous fiez pas uniquement à l'ordre des lignes ou au nom du fichier pour relier un résultat à un équipement. Incluez l'identité logique et une date de collecte dans le document. Utilisez l'UTC pour l'archivage afin d'éviter les ambiguïtés de fuseau lors de comparaisons inter-sites.

Pour un parc important, envisagez la conservation selon une politique documentée : par exemple garder les instantanés détaillés pendant une durée limitée puis ne conserver que des résumés. Adaptez cette politique aux besoins opérationnels et aux règles de sécurité applicables.


# 7. Vérifications réseau plus avancées

Cette section transforme les sorties des getters en contrôles explicites. Un getter fournit de l'information ; un contrôle interprète cette information par rapport à une règle. Ne confondez pas les deux.

## 7.1 Vérifier les interfaces selon le rôle de l'équipement

Un contrôle rigide tel que « toutes les interfaces doivent être up » est presque toujours incorrect. Sur un commutateur, de nombreux ports d'accès peuvent être volontairement inoccupés. Sur un routeur, une interface de secours ou une sous-interface désactivée peut être attendue.

La politique doit préciser les interfaces requises pour le rôle. Pour un premier contrôle, utilisez une liste d'interfaces obligatoires et vérifiez que chacune existe, est activée et que son état opérationnel correspond à l'attendu.

Exemple de données de politique :

```yaml
checks:
  core-router:
    required_interfaces:
      - GigabitEthernet0/0
      - GigabitEthernet0/1
  access-switch:
    required_interfaces:
      - Ethernet1
```

Les noms ci-dessus sont illustratifs et doivent être adaptés au format exact des interfaces de votre équipement.

Exemple de fonction :

```python
from typing import Any


def check_required_interfaces(
    interfaces: dict[str, Any],
    required_names: list[str],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    for name in required_names:
        item = interfaces.get(name)
        if item is None:
            findings.append({
                "severity": "critical",
                "check": "required_interface_exists",
                "subject": name,
                "message": "Interface obligatoire absente du résultat.",
            })
            continue

        if item.get("is_enabled") is not True:
            findings.append({
                "severity": "major",
                "check": "required_interface_enabled",
                "subject": name,
                "message": "Interface obligatoire non activée ou état inconnu.",
            })

        if item.get("is_up") is not True:
            findings.append({
                "severity": "major",
                "check": "required_interface_up",
                "subject": name,
                "message": "Interface obligatoire non opérationnelle ou état inconnu.",
            })

    return findings
```

La comparaison avec `is True` est intentionnelle. Si le champ est absent ou contient une valeur inconnue, la fonction ne l'accepte pas comme preuve de conformité. Cette politique est restrictive : selon le contexte, vous pourrez classifier l'état comme « indéterminé » plutôt que « non conforme ». En production, une structure de constat peut inclure `pass`, `fail` et `unknown` afin de distinguer clairement ces cas.

## 7.2 Utiliser les compteurs d'interface avec prudence

`get_interfaces_counters()` peut fournir des compteurs de trafic et d'erreurs, selon le pilote. Ces données sont des instantanés. Un grand compteur de paquets ou d'octets ne signifie pas automatiquement qu'une interface fonctionne mal. Les erreurs doivent être interprétées avec une fenêtre temporelle, une vitesse de lien, l'historique et les caractéristiques de la plateforme.

Pour repérer une hausse, comparez deux instantanés compatibles : même équipement, même interface, mêmes unités et timestamps connus. Calculez un delta seulement si le compteur n'a pas été remis à zéro, si l'interface n'a pas été réinitialisée et si la différence n'est pas négative de façon inexpliquée.

Pseudo-algorithme :

```text
pour chaque interface commune aux instantanés A et B :
    confirmer que les compteurs et les unités sont comparables
    si le compteur B >= compteur A :
        delta = compteur B - compteur A
    sinon :
        marquer la mesure comme ambiguë (reset, wrap ou changement d'état)
    rapporter delta et durée entre les deux collectes
```

Ne présentez pas un delta ambigu comme une mesure fiable. Cette attention à la qualité des données deviendra importante au niveau Expert, lorsque les résultats nourriront des alertes ou des décisions automatisées.

## 7.3 Vérifier les voisins LLDP

`get_lldp_neighbors()` et `get_lldp_neighbors_detail()` peuvent aider à contrôler la topologie physique. Les structures exactes et les champs disponibles dépendent du getter et du pilote. Un contrôle utile peut vérifier qu'un lien supposé entre deux équipements apparaît dans les deux directions, tout en tenant compte de différences possibles dans les noms d'interfaces.

Exemple de politique logique :

```yaml
expected_links:
  - local_device: core-r1
    local_interface: GigabitEthernet0/1
    remote_device: access-sw1
    remote_interface: Ethernet1
```

Pour chaque lien attendu, votre code devra :

1. vérifier que la collecte des deux équipements a réussi suffisamment pour permettre le contrôle ;
2. rechercher le voisin distant dans les informations LLDP du côté local ;
3. comparer les noms de système et d'interface avec une règle de normalisation explicite ;
4. qualifier le résultat comme conforme, non conforme ou impossible à vérifier ;
5. ne pas confondre une information LLDP absente avec une panne physique certaine.

L'absence de voisin LLDP peut provenir d'un protocole désactivé, d'un délai de découverte, d'une limite du pilote ou d'une politique de sécurité. Le rapport doit décrire ce qui a réellement été mesuré, pas surinterpréter le résultat.

## 7.4 Contrôler les voisins BGP

Lorsque le pilote prend en charge les getters concernés, `get_bgp_neighbors()` fournit un état agrégé des voisins BGP et `get_bgp_neighbors_detail()` des détails supplémentaires. Vérifiez la structure réelle renvoyée par votre pilote avant d'écrire des règles, car il peut exister des variations de disponibilité ou de détail.

Une politique BGP solide doit au minimum répondre aux questions suivantes :

- quels processus ou VRF BGP sont concernés ?
- quels voisins sont attendus pour cet équipement et ce rôle ?
- quels états constituent une session établie acceptable ?
- quelle est la différence entre voisin absent, état non établi et getter indisponible ?
- une collecte partielle doit-elle rendre le contrôle indéterminé ?

Évitez d'encoder le statut attendu dans le code lui-même pour chaque appareil. Placez les voisins attendus dans une politique versionnée, attachée au rôle ou à l'équipement. Cela facilite la revue des changements et les futurs tests.

## 7.5 Contrôles NTP, environnement et autres getters

NAPALM expose d'autres getters, par exemple pour l'environnement matériel, la configuration, les pairs NTP, les VLAN ou les tables ARP, selon les fonctions implémentées par le pilote. La disponibilité exacte doit être confirmée dans la documentation et dans les essais de votre plateforme.

Quelques principes :

- **NTP :** vérifier les pairs attendus ou un état de synchronisation seulement si les champs requis sont exposés et correctement interprétés par le pilote ;
- **environnement matériel :** interpréter les capteurs et seuils selon le modèle, sans présumer que toutes les plates-formes rapportent les mêmes unités ;
- **VLAN :** vérifier la présence et les propriétés attendues, tout en tenant compte des VLAN réservés ou internes à la plateforme ;
- **ARP/MAC :** contrôler le caractère plausible des entrées dans un contexte précis, plutôt que de supposer qu'une table identique est attendue partout ;
- **configuration :** utiliser la configuration comme preuve de paramètres déclarés, mais ne pas la considérer comme preuve suffisante que l'état opérationnel est correct.


# 8. Mettre en place la conformité avec NAPALM Validate

## 8.1 Configuration et état réel sont deux choses différentes

Une configuration contient ce qui est demandé ou enregistré dans l'équipement. L'état opérationnel montre ce que le système observe réellement. Les deux peuvent diverger : une interface peut être configurée mais down ; une session BGP peut être définie mais non établie ; une route attendue peut ne pas apparaître dans la table de routage.

NAPALM Validate permet de décrire un état attendu, d'interroger les getters correspondants et de produire un rapport de conformité. La syntaxe exacte et les possibilités de validation doivent être étudiées dans la version de la documentation correspondant à votre installation.

Référence officielle : [Validating deployments](https://napalm.readthedocs.io/en/latest/validate/index.html).

## 8.2 Exemple simple de fichier de validation

Créez `config/validation.yml` :

```yaml
- get_facts:
    hostname: core-r1
```

Ce cas minimal illustre la relation entre le nom du getter et une valeur attendue. Adaptez la structure aux données réellement renvoyées par le pilote de laboratoire. Selon les plateformes et la façon dont un champ est normalisé, un nom d'hôte observé peut différer du nom logique utilisé dans l'inventaire.

Pour ajouter d'autres propriétés, appuyez-vous sur les exemples officiels et validez le fichier sur votre version installée. Évitez d'inventer un schéma YAML en supposant que toute clé de getter peut être imbriquée arbitrairement.

## 8.3 Appeler le rapport de conformité

Le modèle d'appel NAPALM est le suivant :

```python
from napalm import get_network_driver


def validate_device(config: dict, username: str, password: str, validation_file: str):
    driver_factory = get_network_driver(config["driver"])
    device = driver_factory(
        hostname=config["hostname"],
        username=username,
        password=password,
        timeout=int(config.get("timeout", 30)),
        optional_args=config.get("optional_args", {}),
    )

    with device:
        report = device.compliance_report(validation_file=validation_file)
        return report
```

Le format précis de l'objet `report` dépend de l'API et de la version. Commencez par examiner le rapport en laboratoire et consultez les objets retournés par le pilote. Avant de construire un tableau de bord, mappez explicitement les champs et statuts utiles au schéma interne de votre projet.

Si le pilote ne prend pas en charge la méthode demandée ou si le fichier de validation est incorrect, le contrôle ne doit pas être classé comme conforme. Rapportez plutôt une erreur ou un statut indéterminé, avec le motif.

## 8.4 Créer un contrat de conformité compréhensible

Une bonne règle de conformité comprend :

- **un sujet précis** : un équipement, une interface, un voisin ou un paramètre ;
- **une valeur attendue** : une donnée observable et vérifiable ;
- **une méthode de collecte** : getter NAPALM ou contrôle Python ;
- **une portée** : les appareils auxquels la règle s'applique ;
- **une sévérité** : information, mineur, majeur ou critique, selon les conventions du projet ;
- **une conduite en cas d'incertitude** : échec du getter, champ absent, pilote non compatible ;
- **une justification** : pourquoi la règle est importante.

Par exemple, une session BGP qui n'est pas établie peut être critique sur un routeur de bordure mais attendue sur une plateforme de laboratoire encore en préparation. La même règle technique doit donc pouvoir être activée selon le rôle ou l'environnement.

## 8.5 Conformité et faux positifs

La validation automatisée ne dispense pas d'un modèle correct du réseau. Si le fichier d'attendu contient une erreur, l'outil peut signaler une non-conformité alors que l'équipement fonctionne comme prévu. Inversement, une règle trop permissive peut laisser passer un problème réel.

Pour réduire les faux positifs :

1. versionnez les politiques et soumettez les changements à une revue ;
2. commencez avec un nombre réduit de règles faciles à expliquer ;
3. exécutez les règles en laboratoire contre des cas positifs et négatifs ;
4. vérifiez que les getters couvrent bien les champs que la politique suppose ;
5. enregistrez le motif d'un état indéterminé ;
6. n'autorisez pas les actions destructrices uniquement sur la base d'un rapport sans revue humaine ou contrôles additionnels.

### Exercice 8.1 — Premier audit de conformité

Utilisez deux appareils de laboratoire. Définissez une règle facile à vérifier, par exemple un nom d'hôte ou une version connue. Exécutez la validation, inspectez le rapport, puis modifiez temporairement la valeur attendue pour provoquer un écart. Confirmez que votre outil distingue bien un écart réel d'un échec de collecte.


# 9. Comparer les instantanés et repérer les changements

## 9.1 Comparer des objets, pas seulement des fichiers texte

Deux fichiers JSON peuvent différer par l'ordre des clés sans représenter un changement de réseau. Pour comparer un état, chargez les documents et examinez les champs structurés.

Un diff textuel demeure utile pour les configurations, mais un diff d'état doit répondre à des questions précises : une interface est-elle passée de up à down ? un voisin attendu a-t-il disparu ? une version logicielle a-t-elle changé ? un getter a-t-il échoué dans l'une des collectes ?

## 9.2 Comparer les statuts d'interface

```python
from typing import Any


def diff_interface_state(
    before: dict[str, Any],
    after: dict[str, Any],
) -> list[dict[str, str]]:
    """Compare les champs opérationnels de deux résultats normalisés."""
    changes: list[dict[str, str]] = []
    all_names = sorted(set(before) | set(after))

    for name in all_names:
        old = before.get(name)
        new = after.get(name)

        if old is None:
            changes.append({
                "interface": name,
                "field": "presence",
                "before": "absent",
                "after": "present",
            })
            continue
        if new is None:
            changes.append({
                "interface": name,
                "field": "presence",
                "before": "present",
                "after": "absent",
            })
            continue

        for field in ("is_up", "is_enabled", "description", "speed", "mtu"):
            old_value = old.get(field)
            new_value = new.get(field)
            if old_value != new_value:
                changes.append({
                    "interface": name,
                    "field": field,
                    "before": repr(old_value),
                    "after": repr(new_value),
                })

    return changes
```

La fonction compare quelques champs seulement, pas l'intégralité des données. C'est un choix volontaire : un diff utile met en avant les propriétés importantes et évite le bruit produit par les champs volatils.

Avant de comparer deux instantanés, vérifiez qu'ils correspondent au même appareil, au même getter, à des schémas compatibles et à des collectes assez complètes. Si l'un des getters a échoué, une interface absente du résultat peut être une conséquence de la collecte partielle et non un changement du réseau.

## 9.3 Produire un journal de changements

Un événement utile pourrait prendre cette forme :

```json
{
  "event_type": "interface_state_change",
  "device": "core-r1",
  "subject": "GigabitEthernet0/1",
  "field": "is_up",
  "before": true,
  "after": false,
  "severity": "major",
  "detected_at": "2026-10-23T10:30:00+00:00",
  "evidence": "snapshots/snapshot-20261023T103000Z.json"
}
```

Un événement de ce type n'est pas une preuve absolue de cause. Il indique qu'un changement a été observé entre deux résultats exploitables. Pour déterminer pourquoi le lien est passé down, il peut être nécessaire de croiser les journaux réseau, la topologie, les changements de configuration et les événements physiques.


# 10. Préparer un changement de configuration de façon contrôlée

Cette partie est volontairement prudente. Les opérations de configuration peuvent couper la connectivité d'administration ou affecter la production. Effectuez les exercices sur un environnement isolé, des équipements de test ou un simulateur compatible. N'appliquez jamais une configuration candidate à un équipement de production uniquement parce que l'exemple de cours paraît simple.

## 10.1 Chaîne d'un changement

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 520" role="img" aria-labelledby="napint-change-title napint-change-desc" width="1080" height="520" style="max-width:100%;display:block">
  <title id="napint-change-title">Cycle de changement NAPALM avec décision explicite</title>
  <desc id="napint-change-desc">Préparer la modification, charger la candidate, examiner le diff, obtenir une décision. En cas de refus, abandonner la candidate. En cas d'approbation, appliquer le changement, vérifier l'état et confirmer ou déclencher la procédure de retour adaptée.</desc>
  <defs>
    <marker id="napint-change-arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,8 L9,4 z" fill="#52d6f4"/></marker>
    <marker id="napint-change-warn-arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,8 L9,4 z" fill="#ffb86b"/></marker>
    <linearGradient id="napint-change-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1424"/><stop offset="1" stop-color="#121f35"/></linearGradient>
  </defs>
  <rect width="1080" height="520" rx="20" fill="url(#napint-change-bg)"/>
  <text x="30" y="38" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="22" font-weight="700" fill="#f3f7ff">Cycle de changement : aucune étape ne doit être implicite</text>
  <text x="30" y="60" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#9eb2cc">La production n'est modifiée qu'après une revue humaine et des contrôles préalables.</text>
  <rect x="28" y="91" width="222" height="74" rx="12" fill="#192a43" stroke="#8b9cff" stroke-width="1.7"/>
  <text x="139" y="118" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">1 · Préparer</text><text x="139" y="139" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">cible · sauvegarde · revue</text>
  <path d="M250 128 H280" fill="none" stroke="#52d6f4" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#napint-change-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-52" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="282" y="91" width="222" height="74" rx="12" fill="#192a43" stroke="#52d6f4" stroke-width="1.7"/>
  <text x="393" y="118" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">2 · Charger candidate</text><text x="393" y="139" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">merge / replace maîtrisé</text>
  <path d="M504 128 H534" fill="none" stroke="#52d6f4" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#napint-change-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-52" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="536" y="91" width="222" height="74" rx="12" fill="#192a43" stroke="#52d6f4" stroke-width="1.7"/>
  <text x="647" y="118" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">3 · Examiner le diff</text><text x="647" y="139" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">portée · retraits · impact</text>
  <path d="M758 128 H788" fill="none" stroke="#52d6f4" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#napint-change-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-52" dur="2.8s" repeatCount="indefinite"/></path>
  <path d="M805 91 H1014 L1050 128 L1014 165 H805 L769 128 Z" fill="#33251f" stroke="#ffb86b" stroke-width="1.8"/>
  <text x="909" y="120" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#fff4e8">4 · Décision</text><text x="909" y="140" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#e8c8a8">validation explicite ?</text>
  <path d="M909 165 V200 H692 V226" fill="none" stroke="#52d6f4" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#napint-change-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-52" dur="2.8s" repeatCount="indefinite"/></path>
  <text x="821" y="192" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" fill="#a4efff">OUI</text>
  <path d="M869 165 V207 H208 V226" fill="none" stroke="#ffb86b" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#napint-change-warn-arrow)"/>
  <text x="492" y="199" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" fill="#ffcf9d">NON</text>
  <rect x="78" y="229" width="260" height="72" rx="12" fill="#33251f" stroke="#ffb86b" stroke-width="1.8"/>
  <text x="208" y="256" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#fff4e8">Abandonner la candidate</text><text x="208" y="278" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#e8c8a8">aucune application du diff</text>
  <rect x="562" y="229" width="260" height="72" rx="12" fill="#172d43" stroke="#52d6f4" stroke-width="1.8"/>
  <text x="692" y="256" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3faff">5 · Appliquer avec prudence</text><text x="692" y="278" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#a4efff">fenêtre · accès de secours</text>
  <path d="M692 301 V328" fill="none" stroke="#52d6f4" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#napint-change-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-52" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="562" y="331" width="260" height="72" rx="12" fill="#112e32" stroke="#47d7b0" stroke-width="1.8"/>
  <text x="692" y="358" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#eafff8">6 · Vérifier l'état obtenu</text><text x="692" y="380" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#a8ddd0">connectivité · règles · getters</text>
  <path d="M562 367 H522 V436 H495" fill="none" stroke="#52d6f4" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#napint-change-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-52" dur="2.8s" repeatCount="indefinite"/></path>
  <rect x="235" y="407" width="260" height="72" rx="12" fill="#192a43" stroke="#8b9cff" stroke-width="1.8"/>
  <text x="365" y="434" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">7 · Confirmer ou revenir</text><text x="365" y="456" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#bdcce1">selon résultats et capacités du pilote</text>
  <text x="30" y="498" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" fill="#9eb2cc">Attention : commit-confirm n'est pas disponible sur tous les pilotes. Prévoir un plan de retour vérifiable.</text>
</svg>

## 10.2 Merge et replace : une décision de portée

- `load_merge_candidate()` prépare l'ajout ou la fusion de lignes de configuration selon le comportement du pilote. Il ne faut pas supposer que le résultat est identique sur toutes les plateformes.
- `load_replace_candidate()` vise le remplacement de la configuration selon les mécanismes pris en charge par le pilote. Une erreur dans le fichier peut retirer des éléments qui n'étaient pas ciblés explicitement.
- `compare_config()` affiche les différences entre l'état courant et la candidate, dans les limites et le format du pilote.
- `discard_config()` abandonne la candidate qui n'est pas retenue.
- `commit_config()` applique le changement candidat.

Pour les premiers exercices intermédiaires, privilégiez des changements limités et réversibles, tels qu'une description d'interface sur une interface non critique dans un laboratoire. Ne commencez pas par remplacer une configuration entière ou modifier les paramètres d'accès à distance.

## 10.3 Exemple de préparation d'une candidate sans commit automatique

```python
from pathlib import Path
from napalm import get_network_driver


def prepare_candidate(
    config: dict,
    username: str,
    password: str,
    candidate_file: str | Path,
    mode: str = "merge",
) -> str:
    """Charge une candidate et renvoie son diff sans l'appliquer."""
    candidate_path = Path(candidate_file)
    if not candidate_path.is_file():
        raise FileNotFoundError(f"Fichier candidat introuvable : {candidate_path}")
    if mode not in {"merge", "replace"}:
        raise ValueError("mode doit valoir 'merge' ou 'replace'.")

    driver_factory = get_network_driver(config["driver"])
    device = driver_factory(
        hostname=config["hostname"],
        username=username,
        password=password,
        timeout=int(config.get("timeout", 30)),
        optional_args=config.get("optional_args", {}),
    )

    with device:
        if mode == "merge":
            device.load_merge_candidate(filename=str(candidate_path))
        else:
            device.load_replace_candidate(filename=str(candidate_path))

        try:
            diff = device.compare_config()
            return diff
        finally:
            # Cette fonction est volontairement en mode préparation seulement.
            # Elle ne commit jamais et essaie de laisser la session sans candidate.
            try:
                device.discard_config()
            except Exception:
                # Le journal appelant doit noter ce cas ; ne pas masquer un commit,
                # et ne jamais supposer que le candidat a été abandonné avec succès.
                pass
```

Le bloc `finally` ici vise un outil de démonstration qui ne fait que prévisualiser le diff. Il faut adapter le traitement pour votre pilote : `discard_config()` peut lui-même échouer, et une fermeture de session ne garantit pas que toutes les plateformes abandonnent la candidate de la même façon. Pour un workflow d'approbation réel, conservez la session ou rechargez la candidate de façon explicite après approbation, selon le comportement documenté de la plateforme. Ne prétendez jamais qu'un abandon est garanti si l'appel a échoué.

## 10.4 Un changement ne doit pas être validé par un simple clic

Avant le commit, contrôlez au minimum :

1. la cible exacte et le rôle de l'équipement ;
2. la provenance du fichier candidat et sa revue ;
3. le diff complet, y compris les lignes supprimées ;
4. la présence d'une sauvegarde et d'un moyen d'accès de secours ;
5. les préconditions techniques, telles que les voisins, la route de gestion ou l'état des interfaces ;
6. l'effet attendu après le changement ;
7. le plan de retour arrière et le responsable de la décision.

Une automatisation de qualité doit exiger une décision explicite. Le code peut proposer un diff et préparer des tests, mais il ne doit pas déduire un accord de production du seul fait que le processus s'exécute sans erreur.

## 10.5 Commit-confirm et retour arrière

Certains pilotes exposent la possibilité d'un commit avec minuterie de retour arrière, au travers de `commit_config(revert_in=...)`, `has_pending_commit()` et `confirm_commit()`. Ce mécanisme n'est pas universel. Confirmez la prise en charge, la durée acceptée et la sémantique exacte sur le matériel ciblé.

Modèle conceptuel, à réaliser uniquement dans un laboratoire compatible :

```python
# Exemple conceptuel : ne l'exécutez pas sans confirmer que le pilote
# et l'équipement prennent en charge commit-confirm et la valeur revert_in.

device.load_merge_candidate(filename="candidate.conf")
diff = device.compare_config()
print(diff)

# L'autorisation humaine et les contrôles de sécurité doivent avoir lieu ici.
# Le code de cours s'arrête volontairement avant le commit.
```

Lorsqu'un déploiement réel utilise commit-confirm, la logique attendue est la suivante : charger et inspecter, appliquer avec une minuterie de retour arrière, tester réellement la connectivité et l'état du service, puis confirmer uniquement si les tests réussissent. Si les tests échouent ou si le canal d'administration est perdu, il faut laisser le retour arrière se produire ou déclencher le mécanisme de rollback documenté. Testez ce scénario à l'avance ; un script doit savoir comment se comporter si la session expire au moment critique.

## 10.6 Déployer par petit lot, pas sur tout le parc

Un déploiement prudent peut suivre ces étapes :

1. vérifier la candidate sans changement ;
2. tester sur une plateforme de laboratoire représentative ;
3. appliquer le changement à un seul équipement canari ;
4. lancer les contrôles de post-déploiement ;
5. analyser le résultat et les métriques ;
6. continuer par petits lots si les conditions restent satisfaites ;
7. interrompre le déploiement et revenir à l'état précédent dès qu'un contrôle critique échoue.

La taille du lot dépend du risque, du rôle et de la redondance du réseau. Un canari ne doit pas être choisi uniquement parce qu'il est facile d'accès : il doit représenter suffisamment les conditions du groupe cible.


# 11. Tests automatisés sans équipement réseau

## 11.1 Pourquoi tester les fonctions indépendamment

Les tests qui se connectent à des équipements réels sont utiles pour les tests d'intégration, mais ils ne doivent pas être l'unique moyen de valider la logique Python. Un test unitaire doit pouvoir vérifier la fusion d'inventaire, la classification d'un résultat, le comportement d'un contrôle d'interface et la construction d'un rapport sans dépendre de la disponibilité d'un routeur.

La séparation entre collecte et règles de contrôle permet cette indépendance. La fonction de vérification reçoit des dictionnaires déjà collectés ; elle ne doit pas ouvrir de session NAPALM elle-même.

## 11.2 Exemple de test pour les interfaces requises

Fichier `tests/test_checks.py` :

```python
from src.checks import check_required_interfaces


def test_required_interfaces_up_returns_no_findings():
    interfaces = {
        "GigabitEthernet0/0": {"is_enabled": True, "is_up": True},
        "GigabitEthernet0/1": {"is_enabled": True, "is_up": True},
    }

    findings = check_required_interfaces(
        interfaces,
        ["GigabitEthernet0/0", "GigabitEthernet0/1"],
    )

    assert findings == []


def test_missing_required_interface_is_reported():
    interfaces = {"GigabitEthernet0/0": {"is_enabled": True, "is_up": True}}

    findings = check_required_interfaces(
        interfaces,
        ["GigabitEthernet0/0", "GigabitEthernet0/1"],
    )

    assert len(findings) == 1
    assert findings[0]["subject"] == "GigabitEthernet0/1"
    assert findings[0]["check"] == "required_interface_exists"


def test_unknown_state_is_not_silently_accepted():
    interfaces = {"GigabitEthernet0/0": {"is_enabled": None, "is_up": True}}

    findings = check_required_interfaces(interfaces, ["GigabitEthernet0/0"])

    assert any(item["check"] == "required_interface_enabled" for item in findings)
```

Pour lancer les tests :

```bash
pytest -q
```

Adaptez l'import `from src.checks` au nom réel du module dans lequel vous avez placé la fonction. Le nom de module doit rester cohérent avec votre arborescence.

## 11.3 Tester l'inventaire

Fichier `tests/test_inventory.py` :

```python
import pytest
from src.inventory import load_inventory


def test_inventory_rejects_invalid_root(tmp_path):
    inventory_file = tmp_path / "devices.yml"
    inventory_file.write_text("- not-a-dict\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_inventory(inventory_file)


def test_inventory_rejects_duplicate_names(tmp_path):
    inventory_file = tmp_path / "devices.yml"
    inventory_file.write_text(
        """
version: 1
devices:
  - name: sw1
    hostname: 192.0.2.1
    driver: eos
    site: lab
    role: access-switch
    environment: lab
    enabled: true
  - name: sw1
    hostname: 192.0.2.2
    driver: eos
    site: lab
    role: access-switch
    environment: lab
    enabled: true
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="dupliqué"):
        load_inventory(inventory_file)
```

Ces tests vérifient les validations de base. Complétez-les pour les champs manquants, les valeurs booléennes, les environnements incorrects et les formats de groupes erronés.

## 11.4 Tester le collecteur avec des doubles de test

Pour aller un cran plus loin, utilisez `unittest.mock` ou des fixtures pytest pour remplacer le pilote NAPALM par un faux objet qui retourne des données déterministes. Les tests pourront simuler : connexion réussie, erreur d'authentification, getter non implémenté, exception sur un getter, fermeture de session ou données inattendues.

L'objectif est de prouver que la logique réagit correctement à chaque situation. Ce n'est pas de prouver que le pilote vendor fonctionne réellement : cela nécessite un test d'intégration sur un environnement compatible.

La stratégie de test doit comporter trois couches :

- **tests unitaires** : règles Python et validation des données, rapides et indépendants du réseau ;
- **tests d'intégration** : compatibilité du pilote, connexion réelle en laboratoire, disponibilité des getters et comportement de configuration ;
- **tests de recette** : comportement du système complet, rapport produit, règles opérationnelles et décision humaine.


# 12. Journalisation et diagnostic reproductible

## 12.1 Utiliser `logging` plutôt que des `print()` partout

`print()` suffit à une démonstration, mais un outil de parc doit pouvoir régler le niveau de détail et conserver un historique. Le module `logging` de Python fournit des niveaux tels que `DEBUG`, `INFO`, `WARNING` et `ERROR`.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("napalm_intermediaire")


def log_result(result: dict) -> None:
    device_name = result.get("device", "unknown")
    status = result.get("status", "unknown")
    duration = result.get("duration_seconds")

    logger.info(
        "Collecte terminée device=%s status=%s duration=%s",
        device_name,
        status,
        duration,
    )

    for error in result.get("errors", []):
        logger.warning(
            "Collecte incomplète device=%s stage=%s kind=%s message=%s",
            device_name,
            error.get("stage"),
            error.get("kind"),
            error.get("message", ""),
        )
```

N'écrivez pas systématiquement les données collectées complètes dans le journal. Loguez plutôt l'identité, l'étape, le statut, la durée et une référence vers l'instantané sécurisé si une inspection détaillée est nécessaire.

## 12.2 Une taxonomie d'erreurs exploitable

Pour éviter de dépendre uniquement du texte d'une exception, normalisez les catégories :

| Catégorie | Exemples | Réaction recommandée |
|---|---|---|
| `inventory_error` | champ absent, pilote mal orthographié dans les données | corriger l'inventaire, ne pas tenter de session |
| `credential_error` | variable de secret absente, secret invalide | vérifier le mécanisme de secret et les permissions |
| `connectivity_error` | hôte injoignable, timeout de connexion | vérifier la route de gestion, l'ACL et la disponibilité |
| `authentication_error` | accès refusé | vérifier le compte et la méthode d'authentification sans exposer le secret |
| `driver_error` | dépendance absente, plateforme non compatible | confirmer la version du pilote et la matrice de prise en charge |
| `getter_unsupported` | méthode non implémentée | marquer le contrôle non vérifiable sur ce pilote |
| `getter_error` | commande sous-jacente échouée, réponse inattendue | inspecter l'erreur et reproduire en laboratoire |
| `validation_error` | format de règle incorrect, rapport invalide | corriger la politique de validation et la tester |
| `serialization_error` | valeur non JSON, données circulaires | corriger le schéma de données ou ajouter une conversion explicite |
| `configuration_error` | diff inattendu, candidate refusée | abandonner le changement tant que la cause n'est pas comprise |

Cette taxonomie est un contrat interne à votre application ; elle n'est pas une liste officielle imposée par NAPALM. Elle aide à produire des métriques cohérentes, même si les exceptions concrètes varient selon les transports et les pilotes.

## 12.3 Ordre de diagnostic

Lorsqu'une collecte échoue, procédez du plus simple au plus spécifique :

1. **Inventaire :** le bon appareil est-il ciblé ? Le champ `driver` est-il correct ?
2. **Configuration Python :** l'environnement virtuel est-il actif ? La bonne version de NAPALM est-elle installée ?
3. **Secret :** les variables existent-elles dans le processus qui exécute le script ?
4. **Réseau de gestion :** l'adresse et le port du transport attendu sont-ils joignables ?
5. **Authentification :** le compte possède-t-il les droits nécessaires ?
6. **Pilote :** le modèle, la version logicielle, le transport et les dépendances sont-ils compatibles ?
7. **Getter :** le getter est-il implémenté et renvoie-t-il la donnée attendue ?
8. **Règle :** le contrôle comprend-il réellement la structure et la sémantique de la sortie ?
9. **Persistance :** le résultat peut-il être sérialisé et écrit sans perte ?

Cette séquence évite de modifier inutilement une règle de conformité quand le vrai problème est une connexion SSH ou un pilote incompatible.


# 13. Sécurité et garde-fous opérationnels

L'automatisation donne la possibilité de reproduire rapidement une action sur de nombreux équipements. C'est sa force et son risque. Plus l'outil est capable, plus il faut limiter les privilèges, clarifier le périmètre et vérifier les résultats.

## 13.1 Gestion des accès

- Utilisez des comptes d'automatisation dédiés, avec les privilèges strictement nécessaires à la collecte ou au type de changement prévu.
- Séparez les identifiants de lecture et de modification lorsqu'une plateforme le permet.
- Ne placez pas les mots de passe dans le code, l'inventaire, les fichiers d'exemple, le dépôt Git ou les commandes visibles dans l'historique du terminal.
- Préférez des secrets injectés au moment de l'exécution, et limitez l'accès aux variables et aux journaux.
- Ne désactivez pas la vérification des clés d'hôte SSH ou la validation TLS par défaut pour « faire fonctionner » une connexion. Toute exception doit être documentée et limitée au laboratoire concerné.
- Contrôlez qui peut modifier l'inventaire, les règles de conformité et les fichiers candidats.

## 13.2 Empêcher les opérations de configuration involontaires

Pour un outil dont la fonction principale est la collecte, créez une séparation explicite entre les chemins de lecture et les chemins de modification. Par exemple, le profil `audit` ne doit pas appeler `commit_config()`.

Vous pouvez aussi ajouter un mode par défaut qui n'applique rien :

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collecteur NAPALM de laboratoire")
    parser.add_argument("--inventory", default="inventory/devices.yml")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--profile", choices=["fast", "standard", "audit"], default="standard")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Mode sans changement de configuration (comportement par défaut).",
    )
    return parser
```

Cette option `--dry-run` est illustrative et force ici le mode sans changement : une option argparse construite de cette manière n'offre pas un moyen d'activer le commit. Dans un outil de déploiement, définissez un mécanisme d'autorisation distinct, documenté et explicite, ainsi qu'une approbation appropriée. Ne confondez pas un indicateur d'affichage avec une vraie barrière de sécurité.

## 13.3 Privilège minimal et segmentation des responsabilités

Un collecteur qui a seulement besoin de lire des facts, des interfaces et des voisins ne devrait pas utiliser par défaut un compte capable de modifier toutes les configurations du réseau. À l'inverse, un composant de changement doit être limité aux utilisateurs, environnements et fenêtres dans lesquels il peut opérer.

La séparation n'est pas seulement technique : elle permet à l'équipe de sécurité, au responsable réseau et à l'opérateur de comprendre clairement qui peut lire, qui peut préparer, qui peut approuver et qui peut appliquer un changement.


# 14. Atelier intégrateur — Construire un mini-auditeur réseau

Cet atelier réunit les acquis du niveau Débutant et les nouvelles compétences intermédiaires. Le livrable est un mini-auditeur en lecture seule qui collecte les informations réseau, conserve les résultats, applique quelques contrôles, et produit un rapport global.

## 14.1 Cahier des charges

L'outil doit :

1. lire l'inventaire YAML et le valider ;
2. ignorer proprement les équipements désactivés ;
3. résoudre les identifiants depuis une source non versionnée ;
4. effectuer une collecte bornée en concurrence ;
5. isoler les erreurs par équipement ;
6. sauvegarder un instantané JSON horodaté ;
7. vérifier les interfaces obligatoires selon le rôle ;
8. vérifier un état attendu via NAPALM Validate lorsque le pilote le permet ;
9. produire un résumé par statut et par catégorie d'erreur ;
10. retourner un code de sortie non nul si une condition critique du contrôle est rencontrée, tout en conservant le rapport complet.

Le comportement exact du code de sortie doit être défini. Pour ce laboratoire, vous pouvez choisir de retourner 0 si la collecte s'est exécutée et que tous les contrôles obligatoires sont passés, 1 si au moins une règle critique échoue, et 2 si une erreur d'inventaire ou de configuration empêche l'exécution. Documentez ce contrat dans le `README.md`.

## 14.2 Exemple de point d'entrée

Ce squelette montre comment assembler les fonctions. Adaptez les imports, le chargement de secrets et les fonctions auxiliaires à la structure finale du projet :

```python
from __future__ import annotations

import os
import sys
from pathlib import Path

from src.collector import collect_many
from src.inventory import load_inventory
from src.report import save_snapshot, summarize_results


def main() -> int:
    inventory_path = Path("inventory/devices.yml")
    inventory = load_inventory(inventory_path)

    username_key = inventory.get("defaults", {}).get("username_env", "NAPALM_USERNAME")
    password_key = inventory.get("defaults", {}).get("password_env", "NAPALM_PASSWORD")
    username = os.getenv(username_key)
    password = os.getenv(password_key)
    if not username or not password:
        raise RuntimeError("Identifiants absents : vérifier la source de secrets.")

    devices = [
        {**inventory.get("defaults", {}), **device}
        for device in inventory["devices"]
        if device.get("enabled", True)
    ]

    results = collect_many(
        devices,
        username=username,
        password=password,
        max_workers=4,
    )

    snapshot_path = save_snapshot(results, "snapshots")
    summary = summarize_results(results)

    print(f"Instantané sauvegardé : {snapshot_path}")
    print(f"Équipements analysés : {summary['device_count']}")
    print(f"Statuts : {summary['status_counts']}")
    print(f"Nombre d'erreurs de collecte : {summary['error_count']}")

    # Règle de sortie minimale : une collecte partielle ou en erreur signale
    # que l'audit n'a pas pu confirmer l'état de tout le périmètre.
    if any(item.get("status") != "success" for item in results):
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERREUR FATALE : {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
```

Ce point d'entrée est une base d'intégration, pas un produit fini. Il faut y ajouter les contrôles d'interface et de conformité, la journalisation configurée, le traitement de l'état partiel et une structure de rapport adaptée. Le contrôle d'une production doit également différencier une alerte critique d'un problème de collecte et ne doit jamais traduire une absence de donnée en succès.

## 14.3 Scénarios obligatoires de recette

Exécutez ces scénarios dans cet ordre :

**Scénario A — Parc totalement joignable.** Tous les équipements de laboratoire sont accessibles. Le rapport doit contenir un résultat explicite pour chaque appareil activé, et le nombre attendu doit correspondre au nombre d'appareils traités.

**Scénario B — Un équipement indisponible.** Rendez un appareil de test inaccessible ou utilisez une cible de laboratoire inutilisée. La collecte doit produire une erreur associée à cette cible tout en préservant les résultats des autres équipements.

**Scénario C — Getter non pris en charge.** Sur un pilote de test ou un faux pilote, simulez un getter indisponible. Le rapport doit noter que le contrôle est non vérifiable, et non conclure que l'équipement est conforme.

**Scénario D — Interface requise down.** Simulez une interface requise dans un état down. Le résultat doit indiquer le nom exact de l'interface et la règle enfreinte.

**Scénario E — Donnée manquante.** Supprimez un champ dans la sortie de test. Vérifiez que l'outil ne substitue pas arbitrairement `False`, `0` ou une chaîne vide sans garder la trace de l'incertitude.

**Scénario F — Inventaire mal formé.** Supprimez un champ obligatoire et relancez l'outil. Il doit échouer avant de tenter une connexion réseau.

**Scénario G — Données non sérialisables.** Injectez une valeur de test inattendue et confirmez que l'erreur de sauvegarde est signalée précisément, sans prétendre que l'instantané existe.

**Scénario H — Comparaison de deux collectes.** Exécutez deux instantanés et introduisez une différence connue dans l'état de laboratoire. La sortie doit la décrire sans mélanger le changement réel avec l'ordre des clés JSON.

## 14.4 Critères d'acceptation

Le projet peut être considéré comme terminé lorsque :

- aucun secret réel n'est stocké dans le code ou l'inventaire ;
- l'inventaire est validé avant les connexions ;
- chaque équipement activé apparaît dans le rapport, y compris en cas d'erreur ;
- les erreurs de getter et les erreurs de session sont différenciées ;
- les données sont archivées avec un schéma et un horodatage ;
- un getter non pris en charge n'est pas présenté comme un résultat conforme ;
- les contrôles sont séparés de la logique de collecte et couverts par des tests ;
- les comparaisons indiquent les champs réellement modifiés ;
- le collecteur n'applique aucune modification de configuration ;
- la procédure a été exécutée dans un environnement de laboratoire et les limites connues sont consignées.


# 15. Travaux pratiques progressifs

## TP 1 — Inventaire fiable

**But :** construire un inventaire valide et rejeter les erreurs avant toute connexion.

**Travail demandé :** ajoutez des champs `site`, `role`, `environment`, `criticality`, `groups` et `enabled`. Implémentez les validations de type et d'unicité. Ajoutez trois tests d'erreur au minimum.

**Livrable :** `inventory/devices.yml`, `src/inventory.py`, `tests/test_inventory.py`.

**Validation :** les données invalides doivent produire un message explicite et ne déclencher aucune session réseau.

## TP 2 — Collecteur à erreurs isolées

**But :** collecter les facts, interfaces, adresses et voisins LLDP de plusieurs appareils.

**Travail demandé :** implémentez `collect_one()` puis `collect_many()`. Ajoutez une catégorisation d'erreur cohérente. Vérifiez qu'un équipement inaccessible ne fait pas perdre les autres résultats.

**Livrable :** `src/collector.py` et un exemple de rapport.

**Validation :** chaque appareil activé doit avoir un état `success`, `partial` ou `error` documenté.

## TP 3 — Stockage et synthèse

**But :** persister les résultats pour permettre une comparaison ultérieure.

**Travail demandé :** créez un instantané JSON horodaté, ajoutez `schema_version`, vérifiez la sérialisation et générez un résumé de statuts.

**Livrable :** deux instantanés de test et un court rapport de synthèse.

**Validation :** le rapport doit afficher le nombre d'équipements et le statut de chaque collecte, sans dissimuler les erreurs.

## TP 4 — Contrôles métier

**But :** définir des règles par rôle d'équipement plutôt que d'appliquer une règle universelle.

**Travail demandé :** définissez les interfaces obligatoires des rôles `core-router` et `access-switch`. Simulez une interface absente, désactivée et down. Envisagez un troisième état `unknown` pour les données non disponibles.

**Livrable :** `src/checks.py`, politiques YAML et tests unitaires.

**Validation :** chaque constat doit indiquer la règle, le sujet, la sévérité et un message compréhensible.

## TP 5 — Conformité NAPALM Validate

**But :** confronter un état attendu à la sortie d'un getter.

**Travail demandé :** préparez une règle simple sur un équipement de laboratoire, lancez `compliance_report()` et adaptez votre code au rapport réellement renvoyé par la version installée.

**Livrable :** `config/validation.yml`, extrait de rapport et note sur les limites du pilote.

**Validation :** l'exécution doit distinguer un état conforme, un état non conforme et une validation impossible.

## TP 6 — Diff opérationnel

**But :** repérer une évolution entre deux instantanés.

**Travail demandé :** comparez la présence, l'état opérationnel, l'activation et la description des interfaces. Ignorez les différences de représentation sans sens opérationnel, mais conservez une trace des champs ignorés dans la documentation.

**Livrable :** une fonction de diff et des tests positifs/négatifs.

**Validation :** les changements doivent être reproductibles et reliés aux deux instantanés comparés.

## TP 7 — Préparation d'une candidate sûre

**But :** charger et examiner une candidate sans la committer.

**Travail demandé :** créez un petit fichier de configuration adapté à une plateforme de laboratoire, affichez le diff et implémentez une voie explicite d'abandon. Le code livré dans ce TP ne doit pas appeler `commit_config()`.

**Livrable :** une fonction `prepare_candidate()` et une procédure de test.

**Validation :** aucun changement n'est appliqué ; les échecs de chargement ou d'abandon sont rapportés explicitement.

## TP 8 — Audit complet

**But :** assembler inventaire, collecte, contrôles, stockage et rapport.

**Travail demandé :** créer un point d'entrée CLI, une sortie JSON de synthèse, une journalisation et un code de sortie défini. Exécuter les huit scénarios de recette de l'atelier intégrateur.

**Livrable :** le projet complet et un `README.md` expliquant l'installation, la configuration, les commandes, les tests, les limites et les précautions opérationnelles.


# 16. Erreurs courantes du niveau Intermédiaire

## 16.1 Utiliser le même compte privilégié partout

Cela simplifie les premiers essais, mais augmente le rayon d'impact d'une fuite ou d'une erreur de code. Séparez la collecte de la modification dès que possible et appliquez le principe du moindre privilège.

## 16.2 Supposer qu'une clé de getter sera toujours présente

Un champ absent peut refléter une variation de pilote, une donnée non disponible ou un changement de schéma. Contrôlez la présence et le type des champs nécessaires à une règle, puis classez le résultat comme indéterminé lorsque l'information ne suffit pas.

## 16.3 Traiter toute exception comme un simple timeout

Une exception peut signaler une erreur d'authentification, une méthode non prise en charge, un mauvais pilote, un problème de parsing ou une panne de transport. Gardez la catégorie, le type et l'étape pour guider le diagnostic.

## 16.4 Déclarer un appareil conforme parce que la collecte n'a rien signalé

L'absence de résultat n'est pas la preuve de l'absence de problème. Un audit valable doit dire quelles règles ont été évaluées et lesquelles n'ont pas pu l'être.

## 16.5 Augmenter le parallélisme avant d'avoir mesuré

Des sessions simultanées peuvent augmenter les erreurs et la charge. Mesurez le taux de réussite, la durée et les temps d'attente avant de modifier le nombre de travailleurs.

## 16.6 Comparer des instantanés non comparables

Des pilotes différents, des collectes partielles, des dates ambiguës ou des schémas différents peuvent donner des différences trompeuses. Vérifiez les métadonnées et la couverture des getters avant de conclure à une dérive.

## 16.7 Commiter parce que le diff semble court

Un diff de quelques lignes peut couper un accès distant, modifier une route par défaut ou toucher une interface critique. L'importance d'un changement dépend de sa sémantique et du rôle de l'équipement, pas du nombre de lignes.

## 16.8 Considérer les diagrammes et les exemples comme une procédure de production

Les extraits du cours illustrent des concepts. Ils doivent être adaptés, testés et revus par rapport au pilote, au modèle, à la version logicielle et aux politiques de l'organisation. Aucune recette générique ne garantit qu'un changement est sans risque sur toutes les plates-formes.


# 17. Grille d'évaluation

Évaluez le projet sur 100 points :

| Domaine | Points | Critères |
|---|---:|---|
| Inventaire et validation | 15 | types, champs obligatoires, doublons, environnements, messages d'erreur |
| Collecte NAPALM | 15 | session maîtrisée, getters appropriés, fermeture et erreurs isolées |
| Multi-équipements | 10 | concurrence bornée, tri stable, résultats conservés par appareil |
| Stockage et qualité de données | 10 | JSON valide, horodatage UTC, version de schéma, gestion des types |
| Contrôles de conformité | 15 | règles par rôle, état inconnu distinct d'un échec, résultat expliqué |
| Comparaison d'instantanés | 10 | diff structuré, champs pertinents, couverture et dates vérifiées |
| Tests et diagnostic | 10 | tests unitaires, scénarios d'erreur, journalisation exploitable |
| Sécurité opérationnelle | 10 | secrets protégés, privilège minimal, aucune modification cachée |
| Documentation du projet | 5 | installation, usage, limites, reproduction des tests |
| **Total** | **100** | |

**Seuil recommandé :** 80/100, sans échec sur les critères de sécurité. Un outil qui collecte correctement mais expose les secrets ou présente un résultat inconnu comme conforme ne doit pas être considéré comme prêt.


# 18. Préparer le passage au niveau Expert

Le niveau Intermédiaire vous a fait passer d'une opération isolée à un outil structuré. Le niveau Expert devra approfondir l'architecture et la fiabilité à grande échelle, sans repartir de zéro.

Vous devrez réutiliser les conventions établies ici :

- l'inventaire typé, enrichi par rôle, site et environnement ;
- le format de résultat qui distingue succès, résultat partiel, erreur et exclusion ;
- la taxonomie des erreurs ;
- les fonctions pures de vérification séparées des sessions réseau ;
- les instantanés datés et versionnés ;
- les rapports de conformité qui rendent visible ce qui a été évalué et ce qui reste inconnu ;
- la politique de configuration préparée, contrôlée et appliquée avec approbation ;
- les tests unitaires et les scénarios d'intégration documentés.

Les thèmes du niveau Expert pourront ensuite inclure la gestion de lots complexes, la coordination des dépendances réseau, une stratégie de retries bornés, la planification et la reprise de tâches, l'observabilité des collectes, la gestion du cycle de vie des instantanés, la comparaison de grandes topologies, l'intégration aux pipelines CI/CD et l'application de politiques de déploiement avec approbation et rollback mesurables.

Il ne suffira pas d'écrire un script plus long. Le niveau Expert devra pouvoir expliquer comment l'outil se comporte pendant une panne partielle, comment il sait qu'une donnée est fiable, comment il empêche une action non autorisée, et comment il prouve qu'une opération a été vérifiée après son application.


# 19. Références officielles et vérifications de version

Consultez en priorité les sources officielles suivantes avant une utilisation sur vos appareils :

1. **PyPI — NAPALM :** https://pypi.org/project/napalm/ — version publiée, dépendances et version minimale de Python.
2. **Dépôt et releases NAPALM :** https://github.com/napalm-automation/napalm/releases — notes des versions et changements.
3. **API `NetworkDriver` :** https://napalm.readthedocs.io/en/latest/base.html — définition des getters et des méthodes de configuration.
4. **Matrice de prise en charge :** https://napalm.readthedocs.io/en/stable/support/ — vérifiez le pilote et les fonctionnalités dont vous avez besoin.
5. **Modification de configuration :** https://napalm.readthedocs.io/en/stable/tutorials/changing_the_config.html — exemples de merge, replace, comparaison, commit et commit-confirm.
6. **Validation des déploiements :** https://napalm.readthedocs.io/en/latest/validate/index.html — fichier d'attendu et rapport de conformité.

Les pages de documentation peuvent être publiées indépendamment des versions du paquet et certaines URLs historiques peuvent contenir des exemples plus anciens. Pour des fonctions sensibles — en particulier les changements de configuration et commit-confirm — vérifiez la documentation correspondante à votre version NAPALM et testez le comportement sur le pilote réel. La prise en charge peut différer selon les plateformes, les transports, les versions logicielles et les options du pilote.


# 20. Checklist finale avant de déclarer le niveau acquis

## Compréhension

- [ ] Je peux expliquer pourquoi le niveau Intermédiaire prolonge les bases du niveau Débutant.
- [ ] Je distingue la récupération d'une donnée de la règle qui interprète cette donnée.
- [ ] Je distingue non-conformité et impossibilité de vérifier.
- [ ] Je sais que les getters et changements disponibles peuvent varier selon le pilote.

## Inventaire et collecte

- [ ] Mon inventaire est validé avant les connexions.
- [ ] Aucun secret réel n'est stocké dans les fichiers suivis par Git.
- [ ] Chaque appareil possède son propre résultat et ses propres erreurs.
- [ ] Une panne isolée n'efface pas les résultats des appareils qui ont réussi.
- [ ] La concurrence est bornée et choisie à partir de mesures.

## Données et conformité

- [ ] Les instantanés sont horodatés et comportent une version de schéma.
- [ ] La sérialisation échoue de façon visible si une donnée n'est pas représentable.
- [ ] Les règles sont adaptées aux rôles des équipements.
- [ ] Les getters non pris en charge sont signalés comme tels.
- [ ] Les rapports rendent visibles les appareils non analysés et les contrôles indéterminés.
- [ ] Les comparaisons sont faites entre instantanés compatibles et suffisamment complets.

## Changement et sécurité

- [ ] Le collecteur de ce projet ne modifie aucune configuration.
- [ ] Je sais examiner et abandonner une candidate dans un laboratoire.
- [ ] Je n'utilise commit-confirm que si le pilote et l'équipement le prennent réellement en charge.
- [ ] Je dispose d'une sauvegarde, d'un accès de secours et d'une procédure de retour arrière pour tout changement autorisé.
- [ ] Aucun changement n'est appliqué uniquement parce que le script s'est exécuté sans erreur.

## Qualité logicielle

- [ ] Les contrôles Python importants ont des tests unitaires.
- [ ] Les scénarios d'erreur sont reproduits et documentés.
- [ ] La journalisation aide au diagnostic sans enregistrer les secrets.
- [ ] Le `README.md` explique l'installation, les paramètres, les tests, les limites et les précautions opérationnelles.


## Conclusion

Le niveau Débutant vous a appris à utiliser NAPALM sur un équipement. Le niveau Intermédiaire vous apprend à rendre cette utilisation cohérente sur plusieurs équipements, contrôlable dans le temps et sûre pour les opérations réseau.

Retenez les principes essentiels : **valider l'inventaire avant d'agir, traiter les erreurs comme des résultats à part entière, ne jamais assimiler une donnée absente à une preuve de conformité, normaliser les résultats, mesurer avant d'optimiser, séparer collecte et contrôle, et inspecter chaque changement avant de l'appliquer**.

La réussite de ce niveau se mesure à la qualité de l'outil que vous êtes capable de maintenir — pas au nombre de commandes NAPALM que vous avez mémorisées. Cet outil doit pouvoir expliquer ce qu'il a observé, ce qu'il n'a pas pu vérifier, quelle règle a échoué et pourquoi aucune action de configuration ne sera exécutée sans les contrôles requis.
