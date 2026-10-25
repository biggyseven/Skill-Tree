# Automatisation réseau — Niveau intermédiaire

## Connexions multi-équipements, collecte, sauvegardes et contrôle des résultats


## Présentation du cours

Ce cours constitue la deuxième étape du parcours d'automatisation réseau.

Au niveau débutant, l'apprenant a découvert les principes de l'automatisation, les bases de Python, le format JSON, la construction d'un inventaire et la validation des données avant toute opération réseau.

Il a également construit un premier projet appelé `automation-lab`.

Le niveau intermédiaire reprend ce projet et lui ajoute des fonctionnalités concrètes. Le programme ne se contente plus de vérifier un fichier : il apprend à communiquer avec des équipements de laboratoire, à collecter des informations, à enregistrer les résultats, à effectuer des sauvegardes et à détecter des différences entre deux états.

L'objectif n'est pas encore de déployer automatiquement des changements complexes. Il est d'apprendre à construire une automatisation réseau contrôlée, reproductible et capable de signaler correctement ses erreurs.

### Positionnement dans le parcours

```text
========================================================
NIVEAU DÉBUTANT
automation-debutant.md
========================================================

  Python
     |
     v
  JSON et inventaire
     |
     v
  Validation des données
     |
     v
  Principes SSH et sécurité
     |
     v
  Projet automation-lab
     |
     v
========================================================
NIVEAU INTERMÉDIAIRE
automation-intermediaire.md
========================================================

  Réutiliser le projet existant
     |
     v
  Préparer les connexions SSH
     |
     v
  Collecter des informations
     |
     v
  Traiter plusieurs équipements
     |
     v
  Enregistrer les résultats
     |
     v
  Sauvegarder des configurations
     |
     v
  Comparer les états
     |
     v
  Produire des rapports fiables
     |
     v
========================================================
NIVEAU EXPERT
automation-expert.md
========================================================

  Définir un état attendu
     |
     v
  Contrôler la conformité
     |
     v
  Automatiser les tests
     |
     v
  Valider les changements
     |
     v
  Contrôler les déploiements
     |
     v
  Prévoir les reprises
     |
     v
  Intégrer le projet à une chaîne CI/CD
```

**Règle pédagogique :** ce cours ne doit pas être étudié comme un projet totalement indépendant. Il prolonge les notions et les fichiers du cours débutant. Le cours expert reprendra à son tour le projet enrichi dans ce niveau intermédiaire.


# OBJECTIFS PÉDAGOGIQUES

À la fin du cours, l'apprenant doit être capable de :

1. Réutiliser un inventaire JSON pour préparer une automatisation multi-équipements.
2. Sélectionner uniquement les équipements appartenant à un environnement autorisé.
3. Préparer un environnement Python avec un environnement virtuel.
4. Utiliser une bibliothèque adaptée à la plateforme réseau.
5. Comprendre les étapes d'une connexion SSH automatisée.
6. Gérer les identifiants sans les enregistrer dans le code.
7. Exécuter des commandes réseau en lecture seule.
8. Enregistrer les résultats dans des fichiers structurés.
9. Traiter les erreurs rencontrées pendant les connexions.
10. Produire des sauvegardes de configuration distinctes et datées.
11. Comparer deux sauvegardes et interpréter les différences.
12. Construire des rapports distinguant les réussites, les échecs et les opérations non exécutées.
13. Tester les fonctions importantes sans dépendre systématiquement d'un équipement réel.
14. Préparer le projet pour les mécanismes avancés du niveau expert.

## Prérequis

L'apprenant doit avoir terminé le cours débutant ou maîtriser les notions équivalentes :

- Syntaxe Python élémentaire.
- Variables, listes, dictionnaires et fonctions.
- Lecture d'un fichier JSON.
- Validation d'un inventaire.
- Organisation d'un projet.
- Notions d'adressage IP.
- Commandes réseau de vérification.
- Principes de base de SSH.
- Gestion des erreurs.

Il est également recommandé de savoir se connecter manuellement à un équipement de laboratoire et d'exécuter des commandes de lecture.

## Matériel pédagogique

Les exemples supposent la présence de Python 3 et d'un laboratoire réseau accessible.

Le laboratoire peut être constitué d'équipements physiques, de machines virtuelles ou d'un environnement d'émulation adapté.

Les adresses d'exemple utilisées dans ce cours appartiennent à une plage réservée à la documentation. Elles ne représentent pas des équipements réellement accessibles.

**Aucune commande de modification de configuration n'est nécessaire pour suivre les premiers exercices.** La collecte et la sauvegarde doivent d'abord être validées en lecture seule.


# PARTIE 1 — REPRENDRE LE PROJET DÉBUTANT

## 1. Rappel des acquis

Le cours débutant a introduit le projet `automation-lab`.

L'inventaire décrit les équipements à traiter. Le programme Python vérifie ensuite les données avant d'envisager une connexion.

Exemple de structure :

```text
automation-lab/
|
+-- README.md
|
+-- inventory/
|   |
|   +-- devices.json
|
+-- scripts/
|   |
|   +-- read_inventory.py
|   |
|   +-- inventory_check.py
|
+-- data/
|
+-- reports/
|
+-- backups/
|
+-- tests/
```

Au niveau débutant, le programme validait les données, mais ne communiquait pas avec les équipements.

Le niveau intermédiaire va conserver cette architecture et lui ajouter des composants spécialisés.

## 2. Architecture cible du niveau intermédiaire

```text
+--------------------------------------------------+
|                  ADMINISTRATEUR                  |
|          Définit les objectifs et les règles     |
+---------------------------+----------------------+
                            |
                            v
+--------------------------------------------------+
|                    INVENTAIRE                    |
|           Nom, adresse, rôle, plateforme          |
+---------------------------+----------------------+
                            |
                            v
+--------------------------------------------------+
|                VALIDATION PYTHON                 |
|        Structure, champs, environnement          |
+---------------------------+----------------------+
                            |
                            v
+--------------------------------------------------+
|               MOTEUR D'AUTOMATISATION            |
|     Connexion, collecte, sauvegarde, erreurs     |
+---------------------------+----------------------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
        +---------+    +---------+    +---------+
        | ROUTEUR |    | SWITCH  |    | SWITCH  |
        |   R1    |    |  SW1    |    |  SW2    |
        +----+----+    +----+----+    +----+----+
             |              |              |
             +--------------+--------------+
                            |
                            v
+--------------------------------------------------+
|              RÉSULTATS ET SAUVEGARDES             |
|          JSON, configuration, journaux            |
+---------------------------+----------------------+
                            |
                            v
+--------------------------------------------------+
|                 CONTRÔLE FINAL                   |
|        Différences, erreurs, rapport              |
+--------------------------------------------------+
```

Cette architecture sépare plusieurs responsabilités :

- L'inventaire indique les cibles prévues.
- La validation décide si les données peuvent être utilisées.
- Le moteur d'automatisation exécute les opérations permises.
- Les équipements répondent aux commandes.
- Les résultats sont enregistrés et contrôlés.

Cette séparation deviendra encore plus importante au niveau expert.

## 3. Faire évoluer l'arborescence

L'arborescence précédente sera conservée.

Voici la version enrichie :

```text
automation-lab/
|
+-- README.md
|
+-- inventory/
|   |
|   +-- devices.json
|
+-- scripts/
|   |
|   +-- read_inventory.py
|   |
|   +-- inventory_check.py
|   |
|   +-- collect_readonly.py
|   |
|   +-- backup_configs.py
|   |
|   +-- compare_configs.py
|
+-- data/
|   |
|   +-- sample_devices.json
|
+-- reports/
|   |
|   +-- collecte_YYYYMMDD_HHMMSS.json
|   |
|   +-- rapport_YYYYMMDD_HHMMSS.json
|
+-- backups/
|   |
|   +-- R1/
|   |
|   +-- SW1/
|   |
|   +-- SW2/
|
+-- logs/
|   |
|   +-- automation.log
|
+-- tests/
    |
    +-- test_inventory.py
    |
    +-- README.md
```

Les noms comportant `YYYYMMDD_HHMMSS` représentent une convention illustrative de date et d'heure. Les scripts produiront de véritables horodatages.

Les fichiers indiqués dans cette arborescence correspondent aux éléments à construire progressivement. Ils ne sont pas tous créés automatiquement par le simple fait de reproduire le schéma.


# PARTIE 2 — PRÉPARER L'ENVIRONNEMENT PYTHON

## 4. Pourquoi utiliser un environnement virtuel ?

Un projet Python peut dépendre de plusieurs bibliothèques.

Installer toutes les bibliothèques dans l'environnement global de l'ordinateur peut créer des conflits entre différents projets.

Un environnement virtuel isole les dépendances d'un projet et facilite la reproduction de son environnement.

```text
ORDINATEUR D'ADMINISTRATION
           |
           v
      Python 3
           |
           v
+--------------------------+
| automation-lab           |
|                          |
| Environnement virtuel    |
|                          |
| Bibliothèques du projet  |
| Scripts et tests         |
+--------------------------+
```

L'environnement virtuel ne constitue pas une frontière de sécurité contre une action malveillante. Il sert principalement à isoler les dépendances Python.

## 5. Créer l'environnement virtuel

Placez-vous dans la racine du projet :

```bash
cd automation-lab
```

Sous Linux ou macOS :

```bash
python3 -m venv .venv
```

Sous Windows :

```powershell
py -m venv .venv
```

### Activation sous Linux ou macOS

```bash
source .venv/bin/activate
```

### Activation sous Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Vérifier Python

```bash
python --version
```

Dans un environnement virtuel activé, la commande `python` devrait utiliser l'interpréteur associé à l'environnement.

Si la commande `python` n'est pas disponible, adaptez les commandes à l'installation du système.

## 6. Installer Netmiko

Dans ce cours, Netmiko servira d'exemple de bibliothèque pour les connexions SSH à des équipements réseau.

Installez la bibliothèque :

```bash
python -m pip install netmiko
```

Vérifiez sa présence :

```bash
python -m pip show netmiko
```

Le programme devra également pouvoir communiquer avec les équipements concernés par le réseau prévu dans le laboratoire.

L'installation d'une bibliothèque ne prouve pas que les équipements sont joignables ni qu'ils sont compatibles avec la plateforme choisie.

### Schéma — préparation avant connexion

```text
Python disponible ?
        |
        v
Environnement virtuel créé ?
        |
        v
Dépendance installée ?
        |
        v
Inventaire validé ?
        |
        v
Laboratoire accessible ?
        |
        v
Identité SSH vérifiable ?
        |
        v
AUTOMATISATION PRÊTE
```

Si une seule des étapes nécessaires échoue, il faut résoudre le problème avant de poursuivre.

## 7. Conserver une trace des dépendances

Pour enregistrer les bibliothèques installées dans l'environnement de travail :

```bash
python -m pip freeze > requirements.txt
```

Le fichier `requirements.txt` permet de conserver un relevé des dépendances de l'environnement.

Dans un projet destiné à être partagé ou déployé, il convient aussi de définir et de tester une stratégie de versions compatibles. Le simple enregistrement de toutes les bibliothèques présentes sur une machine ne garantit pas un environnement reproductible dans toutes les circonstances.

Le dossier `.venv/` ne doit généralement pas être ajouté au dépôt Git.


# PARTIE 3 — ADAPTER L'INVENTAIRE AUX CONNEXIONS

## 8. Réutiliser le JSON du niveau débutant

Le fichier `inventory/devices.json` contient toujours les informations de base :

```json
[
  {
    "name": "R1",
    "host": "192.0.2.11",
    "platform": "ios",
    "role": "router",
    "environment": "lab"
  },
  {
    "name": "SW1",
    "host": "192.0.2.21",
    "platform": "ios",
    "role": "switch",
    "environment": "lab"
  },
  {
    "name": "SW2",
    "host": "192.0.2.22",
    "platform": "ios",
    "role": "switch",
    "environment": "lab"
  }
]
```

Les noms, les adresses, les rôles et les environnements servent à identifier les cibles.

Une propriété supplémentaire sera utilisée par les scripts : `platform`.

Ce champ décrit ici la plateforme de manière logique. Le programme devra associer cette valeur au type de périphérique attendu par la bibliothèque employée.

Dans cet exemple, la valeur `ios` sera associée au type Netmiko `cisco_ios`.

Cette correspondance ne signifie pas que tous les équipements Cisco utilisent nécessairement la même plateforme ou le même type de connexion.

## 9. Comprendre la correspondance des plateformes

Toutes les bibliothèques d'automatisation n'utilisent pas les mêmes noms de plateformes.

L'inventaire doit donc rester compréhensible et le programme doit convertir les valeurs vers le format attendu par la bibliothèque choisie.

```text
INVENTAIRE
    |
    v
platform = "ios"
    |
    v
TABLE DE CORRESPONDANCE
    |
    v
type Netmiko = "cisco_ios"
    |
    v
Paramètres de connexion
    |
    v
Connexion adaptée à la plateforme
```

On évite ainsi de mélanger les informations métier du projet avec les conventions propres à une bibliothèque.

## 10. Définir les règles de ciblage

Un script ne doit pas nécessairement traiter tous les équipements présents dans un inventaire.

Il peut, par exemple, être limité aux équipements déclarés dans l'environnement `lab`.

```text
INVENTAIRE
    |
    +---- R1 / lab
    |
    +---- SW1 / lab
    |
    +---- SW2 / lab
    |
    +---- FW1 / production
             |
             v
       FILTRE ENVIRONNEMENT
             |
             v
       Autoriser uniquement lab
             |
       +-----+-----+
       |     |     |
       v     v     v
       R1   SW1   SW2

       FW1 : EXCLU
```

Le filtrage constitue une protection supplémentaire, mais il ne remplace pas une validation indépendante des cibles autorisées.

Les exemples de ce cours refuseront de traiter un équipement d'un environnement différent de `lab`.


# PARTIE 4 — SÉCURISER LES CONNEXIONS

## 11. Comprendre les informations nécessaires

Pour ouvrir une connexion SSH, un programme doit généralement connaître :

- L'adresse de destination.
- Le type de plateforme.
- Le nom d'utilisateur ou le mécanisme d'authentification.
- Le moyen de vérifier l'identité du serveur.
- Les délais d'attente applicables.
- Les paramètres nécessaires à la plateforme.

Les mots de passe et autres secrets ne doivent pas être enregistrés dans l'inventaire.

### Schéma — séparation des responsabilités

```text
+-----------------------------+
| INVENTAIRE                  |
| Nom, IP, rôle, plateforme   |
+---------------+-------------+
                |
                v
+-----------------------------+
| CONFIGURATION DU PROGRAMME  |
| Délais, commandes permises  |
+---------------+-------------+
                |
                v
+-----------------------------+
| GESTION DES IDENTIFIANTS    |
| Authentification contrôlée  |
+---------------+-------------+
                |
                v
+-----------------------------+
| VÉRIFICATION SSH            |
| Identité de la cible        |
+---------------+-------------+
                |
                v
       CONNEXION AUTORISÉE
```

## 12. Utiliser des variables d'environnement

Pour un laboratoire simple, les exemples peuvent lire les identifiants dans des variables d'environnement préparées avant le lancement.

Cette solution réduit le risque d'inscrire des secrets dans le code, mais elle ne constitue pas à elle seule une plateforme complète de gestion des secrets.

Sous Linux ou macOS :

```bash
export AUTOMATION_USERNAME="labuser"
export AUTOMATION_PASSWORD="mot-de-passe-du-laboratoire"
```

Sous Windows PowerShell :

```powershell
$env:AUTOMATION_USERNAME = "labuser"
$env:AUTOMATION_PASSWORD = "mot-de-passe-du-laboratoire"
```

Ces valeurs sont des exemples. Le mot de passe doit être remplacé par un identifiant réellement prévu pour le laboratoire.

Évitez de saisir des secrets dans des scripts partagés, des captures d'écran ou des journaux de terminal qui seront conservés.

Dans un environnement professionnel, un coffre de secrets ou le mécanisme de gestion des identifiants de la plateforme d'automatisation est souvent préférable.

## 13. Vérifier l'identité de l'équipement

SSH ne doit pas être utilisé en supprimant arbitrairement les contrôles d'identité du serveur.

Une connexion peut être chiffrée tout en étant dirigée vers une cible qui n'est pas celle attendue. La vérification de la clé d'hôte contribue à confirmer l'identité du serveur distant.

Lorsque la politique du laboratoire s'appuie sur le fichier de clés d'hôtes connu du client SSH, ce fichier doit être préparé et tenu à jour selon une procédure fiable.

Une clé inconnue ou modifiée doit être vérifiée, et non acceptée automatiquement pour faire disparaître un avertissement.

### Schéma — contrôle avant connexion

```text
Demande de connexion
         |
         v
Adresse de destination
         |
         v
Vérification de la clé d'hôte
         |
         +--------------------+
         |                    |
         v                    v
Clé vérifiée             Clé inconnue
         |                    |
         v                    v
Poursuivre selon         Suspendre la connexion
la politique             et vérifier l'identité
         |
         v
Authentification
         |
         v
Contrôle des autorisations
         |
         v
Opération permise
```

Les paramètres précis de vérification dépendent du client SSH, de la bibliothèque et de la politique utilisée dans le laboratoire.

**Règle du cours :** ne pas contourner automatiquement la vérification d'identité SSH.

## 14. Limiter les privilèges

Un compte destiné à la collecte d'informations ne doit pas disposer de droits de modification simplement parce qu'ils sont faciles à obtenir.

Le compte doit être configuré pour autoriser les opérations nécessaires à la mission.

```text
OBJECTIF
   |
   v
Collecter l'état des équipements
   |
   v
Commandes de lecture nécessaires
   |
   v
Définir les droits correspondants
   |
   v
Tester avec le compte du laboratoire
   |
   v
Vérifier que les actions non autorisées
restent impossibles
```

Les droits exacts dépendent du système réseau et de son modèle d'autorisation.

Une automatisation en lecture seule peut nécessiter certains droits élevés pour consulter une configuration complète, mais elle ne doit pas recevoir automatiquement des privilèges de modification si ceux-ci ne sont pas requis.


# PARTIE 5 — CONSTRUIRE UN MODULE COMMUN

## 15. Pourquoi partager les fonctions ?

Le projet va comporter plusieurs scripts :

- Un script de collecte.
- Un script de sauvegarde.
- Un script de comparaison.

Si chaque script réécrit sa propre logique de lecture JSON et de vérification des identifiants, le code devient redondant.

Une modification peut être appliquée à un script et oubliée dans un autre.

Il est donc préférable de regrouper les fonctions partagées dans un module commun.

```text
                  automation-lab
                         |
                         v
                +-----------------+
                | common.py       |
                |                 |
                | Lire inventaire |
                | Valider données |
                | Charger secrets |
                | Préparer cible   |
                +--------+--------+
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
       collect_      backup_      compare_
       readonly.py   configs.py   configs.py
             |           |
             v           v
       Résultats     Sauvegardes
             |           |
             +-----+-----+
                   |
                   v
                Rapports
```

## 16. Créer le module `common.py`

Créez le fichier :

`scripts/common.py`

Contenu :

```python
import json
import ipaddress
import os

from pathlib import Path
from netmiko import ConnectHandler


ROOT_DIR = Path(__file__).resolve().parent.parent

INVENTORY_PATH = ROOT_DIR / "inventory" / "devices.json"
REPORTS_DIR = ROOT_DIR / "reports"
BACKUPS_DIR = ROOT_DIR / "backups"
LOGS_DIR = ROOT_DIR / "logs"

REQUIRED_FIELDS = {
    "name",
    "host",
    "platform",
    "role",
    "environment",
}

PLATFORM_MAP = {
    "ios": "cisco_ios",
}

ALLOWED_ENVIRONMENTS = {
    "lab",
}


def load_inventory():
    """Charge l'inventaire et valide ses données principales."""

    if not INVENTORY_PATH.is_file():
        raise FileNotFoundError(
            f"Inventaire introuvable : {INVENTORY_PATH}"
        )

    try:
        with INVENTORY_PATH.open(
            "r",
            encoding="utf-8"
        ) as file:
            devices = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON invalide : {exc}"
        ) from exc

    if not isinstance(devices, list):
        raise ValueError(
            "L'inventaire doit être une liste JSON."
        )

    if not devices:
        raise ValueError(
            "L'inventaire est vide."
        )

    seen_names = set()

    for index, device in enumerate(devices, start=1):
        if not isinstance(device, dict):
            raise ValueError(
                f"Entrée {index} : un objet est attendu."
            )

        missing = REQUIRED_FIELDS - device.keys()

        if missing:
            raise ValueError(
                f"Entrée {index} : champs manquants : "
                f"{', '.join(sorted(missing))}"
            )

        for field in REQUIRED_FIELDS:
            value = device[field]

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Entrée {index} : champ invalide : {field}"
                )

        name = device["name"]
        host = device["host"]

        if name in seen_names:
            raise ValueError(
                f"Nom dupliqué : {name}"
            )

        seen_names.add(name)

        try:
            ipaddress.ip_address(host)
        except ValueError as exc:
            raise ValueError(
                f"{name} : adresse IP invalide : {host}"
            ) from exc

        if device["environment"] not in ALLOWED_ENVIRONMENTS:
            raise ValueError(
                f"{name} : environnement non autorisé : "
                f"{device['environment']}"
            )

        if device["platform"] not in PLATFORM_MAP:
            raise ValueError(
                f"{name} : plateforme non prise en charge : "
                f"{device['platform']}"
            )

    return devices


def load_credentials():
    """Lit les identifiants depuis l'environnement d'exécution."""

    username = os.environ.get("AUTOMATION_USERNAME")
    password = os.environ.get("AUTOMATION_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Définissez AUTOMATION_USERNAME et "
            "AUTOMATION_PASSWORD avant de lancer le script."
        )

    return username, password


def build_connection_parameters(device, username, password):
    """Prépare les paramètres de connexion d'une cible validée."""

    if device["environment"] not in ALLOWED_ENVIRONMENTS:
        raise ValueError(
            f"Cible interdite : {device['name']}"
        )

    device_type = PLATFORM_MAP[device["platform"]]

    return {
        "device_type": device_type,
        "host": device["host"],
        "username": username,
        "password": password,
        "port": 22,
        "conn_timeout": 10,
        "auth_timeout": 10,
        "banner_timeout": 15,
        "fast_cli": False,
        "ssh_strict": True,
        "system_host_keys": True,
    }


def ensure_output_directories():
    """Crée les répertoires de sortie nécessaires."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def open_device_connection(device, username, password):
    """Ouvre une connexion selon les paramètres validés."""

    parameters = build_connection_parameters(
        device,
        username,
        password
    )

    return ConnectHandler(**parameters)
```

### Explications importantes

La constante `ROOT_DIR` permet de retrouver la racine du projet sans dépendre du répertoire courant du terminal.

Les chemins des inventaires, des sauvegardes et des rapports sont ainsi construits à partir de cette racine.

La fonction `load_inventory()` lit et valide les données.

La fonction `load_credentials()` récupère les identifiants nécessaires.

La fonction `build_connection_parameters()` associe l'inventaire à la plateforme attendue par Netmiko.

La fonction `open_device_connection()` utilise ensuite les paramètres pour ouvrir la session.

### À propos de la vérification SSH

Le code active une politique stricte de vérification des clés d'hôte au moyen des paramètres de Netmiko. Le laboratoire doit donc préparer les clés de confiance nécessaires avant la connexion.

Les paramètres précis peuvent dépendre de la version de la bibliothèque et de l'environnement SSH. Il faut vérifier leur prise en charge dans la version installée et tester la configuration de confiance en laboratoire.

Le code ne doit pas être modifié pour désactiver la validation uniquement parce qu'une clé est inconnue.

### À propos des plateformes

Le dictionnaire `PLATFORM_MAP` ne contient qu'une correspondance d'exemple.

Pour intégrer un autre type de plateforme, il faut :

1. Vérifier que Netmiko prend en charge l'équipement.
2. Choisir le type de périphérique approprié.
3. Vérifier les commandes de lecture disponibles.
4. Tester la connexion et les réponses.
5. Confirmer que les paramètres de sécurité sont respectés.


# PARTIE 6 — COLLECTER DES INFORMATIONS EN LECTURE SEULE

## 17. Pourquoi commencer par la collecte ?

La collecte permet d'automatiser la récupération d'informations sans chercher à modifier l'équipement.

Elle sert notamment à :

- Vérifier les versions logicielles.
- Examiner les interfaces.
- Relever certaines informations opérationnelles.
- Constituer un état initial.
- Préparer des rapports.
- Disposer de données de référence.

Elle est particulièrement utile pour apprendre les connexions multi-équipements.

## 18. Cycle de collecte

```text
           LANCEMENT DU SCRIPT
                    |
                    v
           Charger l'inventaire
                    |
                    v
             Valider les cibles
                    |
                    v
          Charger les identifiants
                    |
                    v
             Parcourir les cibles
                    |
                    v
          Vérifier l'environnement
                    |
                    v
             Ouvrir la session SSH
                    |
                    v
         Exécuter les commandes autorisées
                    |
                    v
            Lire les réponses
                    |
                    v
          Enregistrer les résultats
                    |
                    v
          Fermer la session proprement
                    |
                    v
            Produire le rapport
```

Les opérations doivent rester séparées : une erreur de connexion ne doit pas être présentée comme une collecte réussie.

## 19. Créer `collect_readonly.py`

Créez :

`scripts/collect_readonly.py`

Contenu :

```python
import json
import logging

from datetime import datetime, timezone

from common import (
    REPORTS_DIR,
    ensure_output_directories,
    load_credentials,
    load_inventory,
    open_device_connection,
)


COMMANDS = {
    "show_version": "show version",
    "show_interfaces_summary": "show ip interface brief",
}


def configure_logging():
    """Configure les journaux du projet."""

    ensure_output_directories()

    log_file = (
        REPORTS_DIR.parent
        / "logs"
        / "automation.log"
    )

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        encoding="utf-8",
    )


def collect_from_device(device, username, password):
    """Collecte des informations de lecture sur un équipement."""

    device_result = {
        "device": device["name"],
        "host": device["host"],
        "environment": device["environment"],
        "status": "failed",
        "commands": {},
        "error": None,
    }

    connection = None

    try:
        logging.info(
            "Connexion en cours vers %s",
            device["name"]
        )

        connection = open_device_connection(
            device,
            username,
            password
        )

        device_result["status"] = "connected"

        for label, command in COMMANDS.items():
            logging.info(
                "%s : commande de lecture : %s",
                device["name"],
                label
            )

            output = connection.send_command(
                command,
                read_timeout=30
            )

            device_result["commands"][label] = {
                "command": command,
                "output": output,
                "status": "success",
            }

        device_result["status"] = "success"

        logging.info(
            "Collecte réussie sur %s",
            device["name"]
        )

    except Exception as exc:
        device_result["status"] = "failed"

        # Le message ne doit jamais inclure de mot de passe.
        device_result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

        logging.exception(
            "Échec de la collecte sur %s",
            device["name"]
        )

    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception:
                logging.exception(
                    "Échec de fermeture de session sur %s",
                    device["name"]
                )

    return device_result


def main():
    configure_logging()

    try:
        devices = load_inventory()
        username, password = load_credentials()

    except Exception as exc:
        logging.exception(
            "Impossible de préparer la collecte"
        )

        print(f"Erreur de préparation : {exc}")
        raise SystemExit(1) from exc

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    report_path = (
        REPORTS_DIR
        / f"collecte_{timestamp}.json"
    )

    results = []

    for device in devices:
        result = collect_from_device(
            device,
            username,
            password
        )

        results.append(result)

        print(
            f"{device['name']:5} : "
            f"{result['status']}"
        )

    successful = sum(
        result["status"] == "success"
        for result in results
    )

    failed = len(results) - successful

    report = {
        "created_at_utc": timestamp,
        "operation": "read_only_collection",
        "total_devices": len(devices),
        "successful": successful,
        "failed": failed,
        "results": results,
    }

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print()
    print(f"Équipements traités : {len(devices)}")
    print(f"Réussites : {successful}")
    print(f"Échecs : {failed}")
    print(f"Rapport : {report_path}")

    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
```

### Comprendre le fonctionnement

Le script commence par charger et valider l'inventaire.

Il récupère ensuite les identifiants depuis l'environnement d'exécution et traite les équipements un par un.

Pour chaque équipement, il :

1. Prépare les informations de connexion.
2. Ouvre une session.
3. Exécute les commandes de lecture configurées.
4. Enregistre les réponses.
5. Ferme la session.
6. Signale une erreur si une opération échoue.

Le rapport est enregistré au format JSON.

Les commandes utilisées sont des commandes de lecture adaptées à l'exemple de plateforme Cisco IOS. Elles ne doivent pas être supposées compatibles avec tous les systèmes réseau.

Il faut vérifier la disponibilité des commandes sur le laboratoire utilisé et ajuster la liste selon la plateforme.

### Limite importante

Le script considère ici la collecte comme réussie lorsque toutes les commandes de lecture ont été exécutées sans exception.

Cela ne garantit pas que le contenu est complet ou qu'il satisfait une exigence de conformité. Ces contrôles feront partie des améliorations du projet.


# PARTIE 7 — EXÉCUTER ET CONTRÔLER LA COLLECTE

## 20. Préparer le laboratoire

Avant de lancer le script, vérifiez les points suivants :

- Les équipements appartiennent au laboratoire.
- L'inventaire est correct.
- Les plateformes sont prises en charge.
- Le routage entre le poste et les équipements fonctionne.
- SSH est accessible.
- Les clés d'hôte sont vérifiées selon la politique prévue.
- Les identifiants fonctionnent.
- Le compte dispose des droits nécessaires aux commandes.
- Les répertoires de sortie sont accessibles.

### Schéma — vérifications préalables

```text
Inventaire valide ?
        |
        v
Équipements autorisés ?
        |
        v
Réseau accessible ?
        |
        v
Clés SSH vérifiées ?
        |
        v
Authentification fonctionnelle ?
        |
        v
Droits suffisants en lecture ?
        |
        v
Répertoires de sortie accessibles ?
        |
        v
Collecte prête
```

Une adresse IP correctement formatée ne prouve pas qu'elle est joignable.

Une connexion SSH réussie ne prouve pas non plus que toutes les commandes sont autorisées.

Ces éléments doivent être testés séparément.

## 21. Exécuter le script

Depuis la racine du projet :

```bash
python scripts/collect_readonly.py
```

Si l'environnement est correctement préparé, le programme affiche un résultat semblable à celui-ci :

```text
R1    : success
SW1   : success
SW2   : success

Équipements traités : 3
Réussites : 3
Échecs : 0
Rapport : .../reports/collecte_20261024_080000.json
```

Cet exemple est illustratif. Les noms de fichiers et les statuts réels dépendent de l'exécution.

Si un équipement est inaccessible, il doit apparaître comme échec dans le rapport. Le programme ne doit pas inventer une réponse ni déclarer une commande exécutée lorsqu'elle ne l'a pas été.

## 22. Comprendre le rapport JSON

Le rapport contient les informations nécessaires pour distinguer les équipements réussis des équipements en échec.

Exemple simplifié :

```json
{
  "created_at_utc": "20261024_080000",
  "operation": "read_only_collection",
  "total_devices": 2,
  "successful": 1,
  "failed": 1,
  "results": [
    {
      "device": "R1",
      "host": "192.0.2.11",
      "environment": "lab",
      "status": "success",
      "commands": {
        "show_version": {
          "command": "show version",
          "output": "Résultat fictif de laboratoire",
          "status": "success"
        }
      },
      "error": null
    },
    {
      "device": "SW1",
      "host": "192.0.2.21",
      "environment": "lab",
      "status": "failed",
      "commands": {},
      "error": "Erreur de connexion illustrative"
    }
  ]
}
```

Ce JSON montre la structure possible d'un rapport, pas la sortie d'une connexion réelle.

### Pourquoi conserver les résultats dans un format structuré ?

Un rapport structuré permet à un autre programme d'exploiter les données sans avoir à analyser manuellement un texte libre.

Par exemple, un futur script pourra :

- Compter les échecs.
- Extraire les versions logicielles.
- Regrouper les résultats par rôle.
- Comparer les informations d'une exécution à la suivante.
- Identifier les équipements qui n'ont pas répondu.


# PARTIE 8 — GÉRER LES ÉCHECS DE CONNEXION

## 23. Les causes possibles d'un échec

Une connexion peut échouer pour plusieurs raisons :

- L'équipement est hors ligne.
- L'adresse est incorrecte.
- Le port SSH est inaccessible.
- La clé d'hôte n'est pas reconnue.
- L'authentification est refusée.
- Le compte est verrouillé.
- Les délais d'attente sont dépassés.
- L'équipement n'est pas compatible avec le type de plateforme choisi.
- Une commande est indisponible ou non autorisée.

Il est important de ne pas traiter tous ces événements comme un seul problème générique dans la logique de l'application.

## 24. Schéma — cycle d'erreur

```text
Connexion vers SW1
        |
        v
Connexion établie ?
      /      \
    OUI      NON
     |        |
     v        v
Commande   Identifier
autorisée  la cause possible
     |        |
     v        v
Réponse    Journaliser
reçue ?    l'échec
  /   \       |
OUI   NON     v
 |     |   Continuer selon
 v     v   la politique
Enre-  Signaler
gistrer l'erreur
     |
     v
Rapport final
```

Le traitement exact dépend du type d'erreur.

Une erreur de clé d'hôte doit mener à une vérification de l'identité de la cible, pas à une désactivation automatique des contrôles.

Une erreur de privilège doit conduire à la vérification des autorisations, plutôt qu'à une attribution aveugle de privilèges supplémentaires.

## 25. Pourquoi continuer sur les autres équipements ?

Supposons que le programme doive traiter dix équipements.

Si le quatrième est inaccessible, les neuf autres ne sont pas nécessairement en panne.

Une politique raisonnable pour une collecte indépendante consiste à :

1. Enregistrer l'échec du quatrième équipement.
2. Fermer toute session partiellement ouverte.
3. Continuer selon la politique prévue.
4. Produire un rapport global.
5. Retourner un code de sortie indiquant qu'au moins une opération a échoué.

Cette stratégie est adaptée à de nombreuses collectes, mais elle ne doit pas être appliquée aveuglément à toutes les opérations.

Pour un déploiement dépendant d'une étape précédente, il peut être nécessaire d'arrêter complètement le traitement.

### Différence entre les codes de sortie

Le script précédent utilise :

- `0` lorsque tous les équipements sont traités sans échec.
- `1` lorsqu'une erreur empêche la préparation générale du programme.
- `2` lorsque le rapport a été produit mais qu'au moins un équipement a échoué.

Ces conventions permettent à un outil externe de distinguer certains résultats.

Elles doivent rester cohérentes dans les différents scripts du projet.


# PARTIE 9 — AUTOMATISER LES SAUVEGARDES

## 26. Pourquoi automatiser les sauvegardes ?

Une sauvegarde permet de conserver une représentation de la configuration à un moment déterminé.

Elle peut être utile pour :

- Conserver un historique.
- Comprendre un changement.
- Préparer une intervention.
- Comparer plusieurs états.
- Faciliter certaines procédures de reprise.
- Documenter une configuration.

Une sauvegarde n'est utile que si elle est correctement collectée, identifiable, protégée et suffisamment complète pour l'objectif prévu.

Une sauvegarde enregistrée ne constitue pas automatiquement une garantie de restauration. Il faut vérifier sa qualité et, dans les environnements concernés, tester les procédures de restauration.

## 27. Organisation des fichiers de sauvegarde

Chaque équipement doit disposer d'un emplacement identifiable.

```text
automation-lab/
|
+-- backups/
    |
    +-- R1/
    |   |
    |   +-- running_20261024_080000.cfg
    |   +-- running_20261025_080000.cfg
    |
    +-- SW1/
    |   |
    |   +-- running_20261024_080000.cfg
    |
    +-- SW2/
        |
        +-- running_20261024_080000.cfg
```

Les noms de fichiers présentés sont illustratifs.

La convention de nommage doit permettre d'identifier au minimum :

- L'équipement.
- La nature du fichier.
- La date et l'heure de collecte.

Il faut éviter les noms identiques qui provoquent l'écrasement accidentel d'une sauvegarde précédente.

## 28. Architecture d'une sauvegarde automatisée

```text
Inventaire validé
        |
        v
Sélection des équipements autorisés
        |
        v
Connexion SSH
        |
        v
Collecte de la configuration
        |
        v
Vérification du résultat
        |
        v
Création du répertoire de l'équipement
        |
        v
Écriture du fichier daté
        |
        v
Vérification de l'écriture
        |
        v
Journalisation
        |
        v
Rapport global
```

La sauvegarde ne doit être déclarée réussie que si les contrôles définis par le projet sont satisfaits.

L'absence d'exception lors de l'écriture d'un fichier n'est pas toujours suffisante. Il faut également vérifier que le contenu correspond au résultat obtenu et que le fichier est exploitable.

## 29. Préparer le répertoire de sortie

Le module `common.py` définit déjà le chemin du répertoire `backups`.

La fonction suivante permet de construire les chemins des équipements :

```python
from pathlib import Path

from common import BACKUPS_DIR


def prepare_device_backup_directory(device_name: str) -> Path:
    directory = BACKUPS_DIR / device_name
    directory.mkdir(parents=True, exist_ok=True)
    return directory
```

Cette fonction suppose que `device_name` a été validé dans l'inventaire.

Dans un projet de plus grande taille, la validation des noms de fichiers doit également interdire les chemins inattendus et les caractères non souhaités.

## 30. Créer `backup_configs.py`

Le script suivant collecte la configuration courante de chaque cible autorisée et l'enregistre dans un fichier daté.

Il est prévu pour le laboratoire Cisco IOS de l'exemple.

Créez :

`scripts/backup_configs.py`

Contenu :

```python
import json
import logging

from datetime import datetime, timezone

from common import (
    BACKUPS_DIR,
    REPORTS_DIR,
    ensure_output_directories,
    load_credentials,
    load_inventory,
    open_device_connection,
)


BACKUP_COMMAND = "show running-config"


def configure_logging():
    ensure_output_directories()

    log_file = (
        REPORTS_DIR.parent
        / "logs"
        / "automation.log"
    )

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        encoding="utf-8",
    )


def backup_device(device, username, password, timestamp):
    result = {
        "device": device["name"],
        "host": device["host"],
        "status": "failed",
        "file": None,
        "error": None,
    }

    connection = None

    try:
        logging.info(
            "Connexion pour la sauvegarde de %s",
            device["name"]
        )

        connection = open_device_connection(
            device,
            username,
            password
        )

        output = connection.send_command(
            BACKUP_COMMAND,
            read_timeout=60
        )

        if not isinstance(output, str) or not output.strip():
            raise RuntimeError(
                "La commande n'a renvoyé aucun contenu exploitable."
            )

        device_dir = BACKUPS_DIR / device["name"]

        device_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        destination = device_dir / (
            f"running_{timestamp}.cfg"
        )

        if destination.exists():
            raise FileExistsError(
                f"La sauvegarde existe déjà : {destination}"
            )

        destination.write_text(
            output.rstrip() + "\n",
            encoding="utf-8"
        )

        saved_content = destination.read_text(
            encoding="utf-8"
        )

        if not saved_content.strip():
            raise RuntimeError(
                "Le fichier écrit est vide."
            )

        result["status"] = "success"
        result["file"] = str(destination)

        logging.info(
            "Sauvegarde réussie pour %s",
            device["name"]
        )

    except Exception as exc:
        result["status"] = "failed"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

        logging.exception(
            "Échec de sauvegarde sur %s",
            device["name"]
        )

    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception:
                logging.exception(
                    "Échec de fermeture de session sur %s",
                    device["name"]
                )

    return result


def main():
    configure_logging()

    try:
        devices = load_inventory()
        username, password = load_credentials()

    except Exception as exc:
        logging.exception(
            "Préparation impossible"
        )

        print(f"Erreur de préparation : {exc}")
        raise SystemExit(1) from exc

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    results = []

    for device in devices:
        result = backup_device(
            device,
            username,
            password,
            timestamp
        )

        results.append(result)

        print(
            f"{device['name']:5} : "
            f"{result['status']}"
        )

    successful = sum(
        result["status"] == "success"
        for result in results
    )

    failed = len(results) - successful

    report = {
        "created_at_utc": timestamp,
        "operation": "configuration_backup",
        "total_devices": len(devices),
        "successful": successful,
        "failed": failed,
        "results": results,
    }

    report_path = (
        REPORTS_DIR
        / f"rapport_sauvegarde_{timestamp}.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print()
    print(f"Sauvegardes réussies : {successful}")
    print(f"Échecs : {failed}")
    print(f"Rapport : {report_path}")

    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
```

### Comprendre les précautions

Le script crée des fichiers nommés à partir de la date et de l'heure.

Avant d'écrire le fichier, il vérifie qu'un fichier de même nom n'existe pas déjà. Cela réduit le risque d'écraser une sauvegarde antérieure dans une même période de nommage.

Le script refuse de considérer un résultat vide comme une sauvegarde réussie.

Il conserve aussi le statut de chaque équipement et produit un rapport global.

### Attention à `show running-config`

La commande utilisée est adaptée à l'exemple Cisco IOS, mais son accessibilité dépend des autorisations du compte et de la configuration de l'équipement.

Si le compte n'a pas le droit de lire la configuration complète, la collecte doit échouer clairement. Il ne faut pas contourner cette restriction en augmentant automatiquement les privilèges.

La configuration peut contenir des informations sensibles. Les répertoires de sauvegarde doivent donc être protégés par des permissions et des règles de conservation adaptées.

**Une sauvegarde de configuration n'est pas un fichier anodin : il faut la traiter comme une donnée potentiellement sensible.**


# PARTIE 10 — COMPRENDRE LES LIMITES D'UNE SAUVEGARDE

## 31. Une sauvegarde est-elle toujours complète ?

Pas nécessairement.

Un fichier peut être présent sans contenir la configuration complète attendue.

Il peut être tronqué, partiellement collecté ou incomplet en raison d'une erreur de communication.

Le script de sauvegarde de base vérifie que le résultat n'est pas vide et que le fichier est lisible. Ces contrôles restent limités.

Dans un environnement professionnel, des vérifications supplémentaires peuvent être nécessaires :

- Présence d'éléments attendus.
- Longueur minimale adaptée à l'équipement.
- Correspondance avec la commande et la cible.
- Contrôle d'intégrité.
- Vérification de l'horodatage.
- Validation de la politique de conservation.

Il ne faut pas imposer une longueur minimale identique à toutes les plateformes. Les configurations ont des tailles différentes et leur contenu dépend des fonctions activées.

## 32. Séparer sauvegarde et restauration

Une sauvegarde permet de conserver un état. La restauration est une opération distincte qui peut modifier le système.

```text
SAUVEGARDE
    |
    v
Collecter et conserver un état
    |
    v
Vérifier le fichier
    |
    v
Protéger et organiser le stockage


RESTAURATION
    |
    v
Identifier l'incident et l'état visé
    |
    v
Valider la sauvegarde utilisable
    |
    v
Évaluer les impacts
    |
    v
Préparer une procédure autorisée
    |
    v
Effectuer les contrôles requis
    |
    v
Restaurer selon la procédure
    |
    v
Vérifier le fonctionnement après restauration
```

La collecte automatique des configurations ne doit pas être confondue avec une capacité de retour arrière déjà opérationnelle.

La restauration devra faire l'objet de tests distincts et d'une procédure appropriée.


# PARTIE 11 — COMPARER DEUX SAUVEGARDES

## 33. Pourquoi comparer les configurations ?

Après une période d'exploitation, une équipe peut vouloir savoir ce qui a changé sur un équipement.

Une comparaison permet d'identifier les lignes ajoutées, supprimées ou modifiées entre deux fichiers.

Elle constitue une première étape pour analyser les modifications.

Cependant, une différence textuelle ne correspond pas automatiquement à une anomalie fonctionnelle.

Une ligne peut avoir changé pour une raison légitime. Certaines informations générées dynamiquement peuvent varier sans changement important de la configuration désirée.

## 34. Schéma — cycle de comparaison

```text
SAUVEGARDE A
Configuration à T0
       |
       +----------------------+
                              |
                              v
                         COMPARAISON
                              ^
                              |
       +----------------------+
       |
SAUVEGARDE B
Configuration à T1
       |
       v
Liste des différences
       |
       v
Analyse du contexte
       |
       +-----------------------+
       |                       |
       v                       v
Changement attendu       Changement à examiner
       |                       |
       v                       v
Documenter le résultat  Vérification technique
```

## 35. Utiliser `difflib`

Python propose le module standard `difflib`, qui permet de comparer des séquences de texte sans installer de bibliothèque supplémentaire.

Une comparaison unifiée peut afficher :

- Les lignes supprimées.
- Les lignes ajoutées.
- Le contexte autour des différences.

Exemple :

```text
Ligne précédente :
 switchport access vlan 10

Ligne actuelle :
 switchport access vlan 20
```

La comparaison indiquera qu'une valeur a changé.

Elle ne peut pas déterminer seule si le VLAN 20 est autorisé par la politique réseau.

## 36. Créer `compare_configs.py`

Créez :

`scripts/compare_configs.py`

Contenu :

```python
import difflib
import sys

from pathlib import Path


def read_configuration(path: Path) -> list[str]:
    """Lit un fichier de configuration en conservant ses lignes."""

    if not path.is_file():
        raise FileNotFoundError(
            f"Fichier introuvable : {path}"
        )

    return path.read_text(
        encoding="utf-8"
    ).splitlines(keepends=True)


def compare_files(old_path: Path, new_path: Path) -> str:
    """Construit une comparaison unifiée de deux fichiers."""

    old_lines = read_configuration(old_path)
    new_lines = read_configuration(new_path)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=str(old_path),
        tofile=str(new_path),
        n=3,
    )

    return "".join(diff)


def main():
    if len(sys.argv) != 3:
        print(
            "Usage : python scripts/compare_configs.py "
            "ANCIEN_FICHIER NOUVEAU_FICHIER"
        )
        raise SystemExit(1)

    old_path = Path(sys.argv[1])
    new_path = Path(sys.argv[2])

    try:
        difference = compare_files(
            old_path,
            new_path
        )

    except (OSError, UnicodeError) as exc:
        print(f"Erreur de lecture : {exc}")
        raise SystemExit(1) from exc

    if difference:
        print(difference)
        raise SystemExit(2)

    print("Aucune différence textuelle détectée.")


if __name__ == "__main__":
    main()
```

### Comment utiliser le programme

Exemple :

```bash
python scripts/compare_configs.py \
  backups/SW1/running_20261024_080000.cfg \
  backups/SW1/running_20261025_080000.cfg
```

Sous Windows PowerShell, la commande peut être saisie sur une seule ligne :

```powershell
python scripts/compare_configs.py backups/SW1/running_20261024_080000.cfg backups/SW1/running_20261025_080000.cfg
```

Les deux fichiers doivent correspondre au même équipement ou à des objets explicitement comparables.

Les chemins d'exemple doivent être remplacés par les fichiers présents dans le laboratoire.

### Codes de sortie

Le script utilise les codes suivants :

- `0` : aucune différence textuelle détectée.
- `1` : problème d'utilisation ou de lecture.
- `2` : différences détectées.

Un code de sortie `2` ne signifie pas nécessairement que la configuration est incorrecte. Il indique que les fichiers ne sont pas identiques du point de vue de la comparaison textuelle.


# PARTIE 12 — INTERPRÉTER LES DIFFÉRENCES

## 37. Lire une comparaison unifiée

Exemple de comparaison :

```diff
--- sauvegarde_A.cfg
+++ sauvegarde_B.cfg
@@
 interface GigabitEthernet0/1
- description LIAISON-UTILISATEURS
- switchport access vlan 10
+ description LIAISON-IMPRIMANTES
+ switchport access vlan 20
  spanning-tree portfast
```

Dans cet exemple :

- Le symbole `-` indique une ligne présente dans le fichier précédent.
- Le symbole `+` indique une ligne présente dans le nouveau fichier.
- Les lignes sans préfixe de changement sont du contexte.

Les descriptions et les affectations de VLAN semblent avoir changé.

La comparaison ne précise pas si le changement était prévu. L'administrateur doit vérifier le contexte avant de conclure.

## 38. Trois niveaux d'analyse

Une approche prudente distingue trois niveaux.

### Niveau 1 — Différence textuelle

Le programme indique quelles lignes ont changé.

### Niveau 2 — Interprétation technique

L'administrateur détermine ce que représentent les lignes concernées.

### Niveau 3 — Analyse de conformité

Les différences sont évaluées par rapport à une politique, un état attendu ou une modification planifiée.

```text
COMPARAISON TEXTUELLE
        |
        v
Liste des différences
        |
        v
INTERPRÉTATION TECHNIQUE
        |
        v
Comprendre l'effet du changement
        |
        v
CONTRÔLE DE CONFORMITÉ
        |
        v
Comparer avec la règle attendue
        |
        v
Conclusion documentée
```

Le niveau intermédiaire réalise principalement les deux premiers niveaux.

Le niveau expert introduira des contrôles plus structurés de conformité.


# PARTIE 13 — AMÉLIORER LE SUIVI DES EXÉCUTIONS

## 39. Pourquoi journaliser ?

Les messages affichés à l'écran disparaissent souvent lorsque le terminal est fermé.

Un journal permet de conserver des événements pour analyser les exécutions passées.

Il peut servir à répondre à ces questions :

- Quand le script a-t-il été exécuté ?
- Quel équipement a été traité ?
- Quelle opération était en cours ?
- Une erreur est-elle survenue ?
- Le fichier a-t-il été écrit ?
- Quel était le résultat global ?

Les journaux ne doivent pas contenir de mots de passe, de jetons d'accès ou d'autres informations qui ne sont pas nécessaires au diagnostic.

## 40. Différence entre rapport et journal

Le journal conserve des événements pendant l'exécution.

Le rapport résume le résultat de l'opération.

```text
EXÉCUTION
   |
   +---- Événement de connexion
   |
   +---- Événement de commande
   |
   +---- Événement de sauvegarde
   |
   +---- Événement d'erreur
   |
   v
JOURNAL D'EXÉCUTION


FIN DE L'EXÉCUTION
   |
   v
Récapitulatif par équipement
   |
   +---- Nombre de réussites
   |
   +---- Nombre d'échecs
   |
   +---- Emplacements des résultats
   |
   v
RAPPORT FINAL
```

Les deux mécanismes sont complémentaires.

Le rapport donne une vue synthétique du résultat.

Le journal fournit davantage de contexte pour examiner une exécution.

## 41. Comprendre les niveaux de journalisation

Le module standard `logging` propose plusieurs niveaux courants.

| Niveau | Utilisation générale |
|---|---|
| `DEBUG` | Informations détaillées utiles au diagnostic |
| `INFO` | Événements normaux de l'exécution |
| `WARNING` | Situation inhabituelle qui mérite une attention |
| `ERROR` | Opération ayant échoué |
| `CRITICAL` | Problème grave pouvant empêcher le fonctionnement |

Le niveau de détail doit être adapté au besoin.

Des journaux trop pauvres compliquent le diagnostic. Des journaux trop détaillés augmentent le volume de données et peuvent exposer des informations sensibles si le contenu n'est pas contrôlé.


# PARTIE 14 — TESTER LE PROJET

## 42. Pourquoi tester avant une exécution réelle ?

Un programme qui fonctionne une fois peut échouer lorsque les données changent.

Par exemple :

- L'inventaire peut être vide.
- Un champ peut manquer.
- Un nom peut être dupliqué.
- Un équipement peut être inaccessible.
- Un fichier de sauvegarde peut être absent.
- Deux fichiers peuvent être identiques.
- Les données d'une commande peuvent être vides.

Les tests permettent de vérifier que le programme répond correctement aux situations prévues.

## 43. Les différents types de tests

### Tests unitaires

Ils vérifient le comportement d'une fonction isolée.

Exemple : vérifier qu'une fonction refuse un inventaire contenant un nom dupliqué.

### Tests d'intégration

Ils vérifient le fonctionnement de plusieurs composants associés.

Exemple : charger un inventaire réel de test, préparer une connexion et récupérer une réponse d'un équipement de laboratoire.

### Tests de bout en bout

Ils vérifient le déroulement de l'ensemble du processus.

Exemple : lancer le programme de collecte, vérifier les résultats et contrôler le rapport final.

```text
             CODE
              |
              v
        TESTS UNITAIRES
              |
              v
      TESTS D'INTÉGRATION
              |
              v
       TESTS DE BOUT EN BOUT
              |
              v
       VALIDATION DU RÉSULTAT
              |
              v
        EXÉCUTION AUTORISÉE
```

Il n'est pas nécessaire d'utiliser un équipement physique pour chaque test unitaire.

Certaines parties du projet peuvent être testées avec des fichiers temporaires et des données fictives.

## 44. Préparer les tests de comparaison

Créez deux fichiers de test.

`data/config_A.cfg` :

```text
hostname SW1
vlan 10
name USERS
interface GigabitEthernet0/1
switchport access vlan 10
```

`data/config_B.cfg` :

```text
hostname SW1
vlan 10
name USERS
vlan 20
name PRINTERS
interface GigabitEthernet0/1
switchport access vlan 10
```

Les fichiers sont volontairement simplifiés.

Exécutez :

```bash
python scripts/compare_configs.py data/config_A.cfg data/config_B.cfg
```

Le résultat doit signaler des différences.

Exécutez ensuite :

```bash
python scripts/compare_configs.py data/config_A.cfg data/config_A.cfg
```

Le programme doit indiquer qu'aucune différence textuelle n'a été détectée.

Ces tests ne nécessitent aucune connexion réseau.

## 45. Préparer des tests pour les inventaires

Les fonctions de validation peuvent être testées sans contacter les équipements.

Les cas à couvrir comprennent :

- Un inventaire valide.
- Une liste vide.
- Un objet qui n'est pas un dictionnaire.
- Un champ manquant.
- Un nom dupliqué.
- Une adresse IP invalide.
- Un environnement interdit.
- Une plateforme non prise en charge.

L'objectif est de vérifier les contrôles du programme, pas seulement sa réussite dans le cas normal.

## 46. Comprendre les faux positifs et les faux négatifs

Dans un contrôle automatisé, une conclusion incorrecte peut prendre plusieurs formes.

**Faux positif :** le programme signale un problème alors que le résultat est acceptable.

**Faux négatif :** le programme ne signale pas un problème réel.

Exemple :

Un programme vérifie qu'une sauvegarde n'est pas vide et conclut qu'elle est correcte.

Si le fichier contient uniquement un message d'erreur renvoyé par un équipement, le programme peut considérer à tort la sauvegarde comme valide.

La présence de données ne suffit donc pas toujours. Le programme doit aussi vérifier que les données correspondent au type de résultat attendu.

Ces notions deviendront essentielles au niveau expert.


# PARTIE 15 — UN PROJET DE VALIDATION HORS LIGNE

## 47. Mission

Avant d'utiliser les connexions réelles, il faut pouvoir tester les fonctions indépendantes du réseau.

Le projet de validation hors ligne doit démontrer que :

1. L'inventaire est correctement lu.
2. Les données incorrectes sont refusées.
3. Deux fichiers de configuration peuvent être comparés.
4. Les erreurs de lecture sont traitées.
5. Le programme ne dépend pas de la disponibilité des équipements pour ces tests.

## 48. Construire un test simple

Créez :

`tests/test_compare_configs.py`

```python
import tempfile
import unittest

from pathlib import Path
from difflib import unified_diff


def compare_text(old_text: str, new_text: str) -> str:
    return "".join(
        unified_diff(
            old_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile="ancien",
            tofile="nouveau",
        )
    )


class CompareConfigTests(unittest.TestCase):

    def test_identical_files_have_no_difference(self):
        text = "hostname SW1\nvlan 10\n"

        result = compare_text(text, text)

        self.assertEqual(result, "")

    def test_different_files_produce_difference(self):
        old = "hostname SW1\nvlan 10\n"
        new = "hostname SW1\nvlan 20\n"

        result = compare_text(old, new)

        self.assertIn("-vlan 10", result)
        self.assertIn("+vlan 20", result)

    def test_empty_text_is_supported(self):
        result = compare_text("", "")

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
```

Lancez :

```bash
python -m unittest discover -s tests
```

Les tests portent sur la logique de comparaison.

Ils ne valident pas les connexions SSH, les autorisations ou la qualité des sauvegardes réelles.

## 49. Pourquoi tester hors ligne ?

Les tests hors ligne sont généralement plus rapides et plus faciles à reproduire.

Ils permettent de détecter les erreurs de programmation avant d'ajouter les difficultés du réseau.

Une erreur dans une fonction de comparaison peut être corrigée sans toucher à un routeur ou à un commutateur.

```text
MODIFICATION DU CODE
        |
        v
TESTS HORS LIGNE
        |
        +---- Échec
        |       |
        |       v
        |   Corriger le code
        |       |
        |       +----> Recommencer les tests
        |
        +---- Réussite
                |
                v
       TESTS EN LABORATOIRE
                |
                v
       Vérification des résultats
```

La réussite des tests hors ligne n'autorise pas à elle seule une opération sur la production.


# PARTIE 16 — SÉCURITÉ ET QUALITÉ DES DONNÉES

## 50. Les sauvegardes sont sensibles

Une configuration réseau peut contenir ou révéler des informations telles que :

- Des adresses internes.
- Des règles de filtrage.
- Des noms de systèmes.
- Des détails de routage.
- Des paramètres d'accès.
- Des éléments sensibles propres à certaines plateformes.

Les fichiers de sauvegarde doivent être protégés en fonction de leur contenu.

Les permissions du système de fichiers, les sauvegardes du poste, le stockage distant et les droits de consultation doivent être pris en compte.

## 51. Contrôler les permissions

Les permissions exactes dépendent du système d'exploitation et de l'organisation.

Sous Linux ou macOS, des permissions restreintes peuvent être configurées sur les dossiers qui contiennent des données sensibles.

Exemple de commande, à adapter au compte et au contexte :

```bash
chmod 700 backups
```

Cette commande restreint l'accès au propriétaire du répertoire dans les systèmes compatibles avec ce modèle de permissions.

Elle ne garantit pas à elle seule la protection contre tous les accès : les comptes administrateurs, les sauvegardes externes et les mécanismes de stockage doivent aussi être considérés.

Sous Windows, il faut utiliser les mécanismes de contrôle d'accès appropriés.

## 52. Éviter de publier les données sensibles

Le dépôt Git ne doit pas contenir automatiquement les sauvegardes et les identifiants.

Un fichier `.gitignore` peut empêcher l'ajout accidentel de certains éléments.

Exemple :

```gitignore
.venv/
__pycache__/
*.pyc

backups/
logs/
reports/

.env
```

Cette liste est un point de départ.

Il faut vérifier les règles du dépôt et contrôler les fichiers réellement suivis par Git. Le `.gitignore` n'enlève pas un fichier déjà suivi et ne remplace pas la gestion des secrets.

## 53. Respecter le périmètre autorisé

Une automatisation doit traiter uniquement les équipements pour lesquels les opérations sont autorisées.

Une bonne conception combine plusieurs protections :

- Un inventaire explicite.
- Une validation des données.
- Un filtrage par environnement.
- Des droits réseau limités.
- Un compte adapté à l'opération.
- Une liste de commandes autorisées.
- Des journaux et des rapports.

Aucun contrôle isolé n'est suffisant dans toutes les situations.


# PARTIE 17 — EXERCICES CORRIGÉS

## 54. Exercice 1 — Préparation de l'environnement

**Question :** pourquoi utiliser un environnement virtuel Python ?

### Correction

L'environnement virtuel permet d'isoler les bibliothèques d'un projet et de réduire les conflits avec d'autres applications Python.

Il facilite également la reproduction de l'environnement de travail.

Il ne remplace pas les contrôles de sécurité et ne doit pas être considéré comme une isolation complète du système.

## 55. Exercice 2 — Inventaire

**Question :** l'inventaire contient un équipement dont le champ `environment` vaut `production`. Le programme du cours est limité à `lab`. Que doit-il faire ?

### Correction

Il doit refuser cette cible.

Le filtrage doit intervenir avant toute tentative de connexion.

Il ne faut pas simplement ignorer silencieusement l'environnement, car le rapport devrait permettre de savoir pourquoi la cible n'a pas été traitée.

Pour ce cours, la fonction de validation refuse les environnements qui ne figurent pas dans l'ensemble autorisé.

## 56. Exercice 3 — Équipement inaccessible

**Question :** trois équipements sont présents dans l'inventaire. La connexion au deuxième échoue. Comment le rapport doit-il représenter l'exécution ?

### Correction

Le rapport doit conserver un résultat distinct pour chaque équipement.

Le premier peut être indiqué comme réussi, le deuxième comme échoué et le troisième comme réussi si sa collecte aboutit.

Le rapport global doit indiquer le nombre de réussites et d'échecs.

Il ne doit pas présenter l'ensemble du traitement comme réussi si une opération obligatoire a échoué.

## 57. Exercice 4 — Commande non autorisée

**Question :** la connexion fonctionne mais la commande de lecture complète de configuration est refusée. Faut-il automatiquement accorder des privilèges supplémentaires au compte ?

### Correction

Non.

Il faut vérifier la mission, les droits nécessaires et les règles de l'environnement.

Si l'opération est autorisée, les autorisations doivent être ajustées selon la procédure prévue. Sinon, le programme doit signaler l'échec.

Une automatisation ne doit pas contourner une restriction d'accès simplement pour terminer son traitement.

## 58. Exercice 5 — Sauvegarde vide

**Question :** le programme crée un fichier de sauvegarde, mais le fichier est vide. Peut-il déclarer la sauvegarde réussie ?

### Correction

Non.

Le programme doit considérer que le résultat n'est pas exploitable et enregistrer l'échec.

Il devra également conserver suffisamment d'informations pour comprendre si l'erreur provient de la commande, de la connexion ou de l'écriture du fichier.

Une validation plus avancée peut contrôler la présence d'éléments attendus selon la plateforme.

## 59. Exercice 6 — Comparaison

**Question :** une comparaison signale qu'une interface possède une description différente. Peut-on déclarer automatiquement une anomalie ?

### Correction

Pas uniquement à partir de la différence.

La nouvelle description peut correspondre à un changement approuvé. Il faut comparer les données avec l'historique et les changements attendus.

La différence doit être documentée puis interprétée dans son contexte.

## 60. Exercice 7 — Fichier de sauvegarde

**Question :** deux sauvegardes portent le même nom. Quel risque existe-t-il ?

### Correction

La deuxième écriture peut remplacer la première et faire perdre un état précédent.

Une convention de nommage datée, le contrôle de l'existence du fichier et une politique de conservation permettent de limiter ce risque.

Il faut aussi prendre en compte les exécutions simultanées et les risques de collision lorsque plusieurs processus peuvent produire des fichiers au même moment.

## 61. Exercice 8 — Test hors ligne

**Question :** pourquoi est-il utile de tester la comparaison de configurations sans se connecter à un équipement ?

### Correction

Les données fictives permettent de tester la logique indépendamment du réseau.

On peut vérifier le comportement face à des fichiers identiques, différents ou absents sans dépendre des accès SSH.

Les tests hors ligne ne remplacent pas les tests en laboratoire, mais ils constituent une première étape utile.

## 62. Exercice 9 — Journalisation

**Question :** un journal enregistre les mots de passe utilisés pendant une connexion. Est-ce acceptable ?

### Correction

Non.

Les secrets doivent être exclus des journaux. Il faut journaliser des événements utiles au diagnostic, sans divulguer les informations d'authentification.

Si un secret a été exposé, il faut appliquer la procédure de sécurité correspondante, notamment sa révocation ou son remplacement lorsque cela est nécessaire.

## 63. Exercice 10 — Préparer le niveau expert

**Question :** un programme récupère une configuration et compare deux fichiers. Que lui manque-t-il pour contrôler la conformité ?

### Correction indicative

Il faut notamment :

- Définir un état attendu ou des règles de conformité.
- Identifier les éléments réellement contrôlés.
- Traiter les différences selon leur importance.
- Distinguer les écarts acceptables des écarts interdits.
- Définir des critères de réussite.
- Produire des résultats vérifiables.
- Tester les contrôles afin de limiter les faux positifs et les faux négatifs.
- Prévoir une validation appropriée avant les éventuels changements.

Ces fonctions seront développées au niveau expert.


# PARTIE 18 — ERREURS FRÉQUENTES

## 64. Utiliser le même type de connexion pour tous les équipements

Les plateformes peuvent avoir des particularités différentes.

**Bonne pratique :** employer une correspondance explicite entre la plateforme de l'inventaire et le type pris en charge par la bibliothèque, puis tester chaque type dans le laboratoire.

## 65. Confondre connexion réussie et collecte réussie

La connexion SSH peut être établie alors qu'une commande échoue ou renvoie un résultat incomplet.

**Bonne pratique :** suivre séparément le statut de connexion, celui des commandes et celui de la collecte globale.

## 66. Ignorer les résultats partiels

Une collecte peut réussir sur certains équipements et échouer sur d'autres.

**Bonne pratique :** enregistrer un statut par cible et produire un rapport global qui indique clairement les résultats partiels.

## 67. Écraser une sauvegarde antérieure

Un nom de fichier fixe peut provoquer un écrasement lors d'une nouvelle exécution.

**Bonne pratique :** employer des noms datés, vérifier l'existence des fichiers et prévoir une politique de conservation.

## 68. Considérer toute différence comme une anomalie

Une différence de texte n'exprime pas automatiquement un problème fonctionnel.

**Bonne pratique :** comparer les fichiers, examiner le contexte et confronter les différences à un état attendu ou à une modification planifiée.

## 69. Accorder des droits excessifs au compte d'automatisation

Une tâche de lecture ne nécessite pas systématiquement les mêmes permissions qu'une opération de configuration.

**Bonne pratique :** appliquer le principe du moindre privilège et ajuster les autorisations uniquement en fonction des besoins vérifiés.

## 70. Négliger les tests

Un programme peut fonctionner avec un inventaire valide mais échouer avec une entrée différente.

**Bonne pratique :** tester les cas normaux, les entrées invalides, les erreurs de connexion et les résultats incomplets.

## 71. Exposer les données de configuration

Une sauvegarde peut révéler des informations sensibles.

**Bonne pratique :** limiter l'accès aux fichiers, protéger les journaux et exclure les données sensibles des dépôts partagés lorsque cela est nécessaire.


# PARTIE 19 — ÉVALUATION DE FIN DE NIVEAU

## 72. Questions théoriques

L'apprenant doit pouvoir répondre aux questions suivantes sans consulter le cours.

1. Quel est le rôle du module `common.py` ?
2. Pourquoi faut-il séparer l'inventaire de la gestion des identifiants ?
3. Pourquoi la plateforme déclarée dans l'inventaire doit-elle être associée à un type de connexion approprié ?
4. Comment limiter une automatisation à l'environnement de laboratoire ?
5. Pourquoi les clés d'hôte SSH doivent-elles être vérifiées ?
6. Pourquoi une connexion réussie ne garantit-elle pas une collecte réussie ?
7. Quels éléments doit contenir un rapport multi-équipements ?
8. Comment prévenir l'écrasement d'une sauvegarde ?
9. Pourquoi les configurations sauvegardées doivent-elles être protégées ?
10. Quelle différence existe entre journalisation et rapport ?
11. Comment fonctionne une comparaison textuelle ?
12. Pourquoi une différence ne prouve-t-elle pas qu'il existe une anomalie ?
13. Quelle différence existe entre un test unitaire et un test d'intégration ?
14. Pourquoi les tests hors ligne sont-ils utiles ?
15. Pourquoi une sauvegarde n'est-elle pas équivalente à une procédure de restauration ?
16. Pourquoi ne faut-il pas augmenter automatiquement les privilèges lorsqu'une commande est refusée ?
17. Quels sont les principaux risques d'une collecte multi-équipements ?
18. Quels contrôles supplémentaires pourraient permettre de vérifier la conformité d'un réseau ?

## 73. Mise en pratique finale

Réalisez les tâches suivantes dans le projet `automation-lab` :

1. Préparer un environnement virtuel Python.
2. Installer Netmiko.
3. Conserver l'inventaire du niveau débutant.
4. Ajouter le module `common.py`.
5. Configurer l'authentification du laboratoire sans stocker de secret dans le code.
6. Préparer la vérification des clés d'hôte SSH.
7. Lancer les tests de comparaison hors ligne.
8. Exécuter une collecte en lecture seule sur les équipements autorisés.
9. Générer un rapport JSON.
10. Sauvegarder les configurations dans des fichiers séparés et datés.
11. Comparer deux sauvegardes d'un même équipement.
12. Tester un échec de connexion dans un environnement contrôlé.
13. Vérifier que les échecs apparaissent dans les rapports.
14. Vérifier que les journaux ne contiennent pas de secrets.
15. Mettre à jour le README pour expliquer les fonctionnalités ajoutées.

Les tests de connexion réelle doivent être réalisés uniquement dans un laboratoire autorisé, avec des équipements compatibles et des droits adaptés.

## 74. Critères de maîtrise

Le niveau intermédiaire est considéré comme acquis lorsque l'apprenant sait :

- Réutiliser le projet débutant.
- Construire une connexion adaptée à la plateforme.
- Collecter des informations en lecture seule.
- Traiter plusieurs équipements sans confondre les résultats.
- Gérer les erreurs et produire un rapport.
- Organiser des sauvegardes datées.
- Comparer deux états textuels.
- Protéger les fichiers produits.
- Tester les fonctions hors ligne.
- Expliquer les limites des vérifications réalisées.

La qualité d'une automatisation ne se mesure pas seulement au nombre d'équipements traités. Elle se mesure aussi à la fiabilité des résultats, à la visibilité des erreurs et à la maîtrise du périmètre d'exécution.


# PARTIE 20 — TRANSITION VERS LE NIVEAU EXPERT

## 75. Ce qui est maintenant acquis

Le projet `automation-lab` dispose désormais d'une structure permettant de :

- Lire un inventaire.
- Vérifier les propriétés des équipements.
- Préparer les connexions.
- Réaliser une collecte en lecture seule.
- Enregistrer des résultats dans des fichiers structurés.
- Produire des sauvegardes de configuration.
- Comparer des sauvegardes.
- Journaliser les opérations.
- Distinguer les réussites et les échecs.
- Exécuter des tests indépendamment du réseau.

Le projet reste volontairement limité.

Il sait collecter et comparer des informations, mais il ne possède pas encore toutes les fonctions nécessaires pour décider automatiquement si le réseau respecte une politique donnée.

Il ne devrait pas non plus déployer automatiquement des changements sans tests, règles de conformité et mécanismes de contrôle supplémentaires.

## 76. Schéma de la progression

```text
==========================================================
DÉBUTANT — BASES DU PROJET
==========================================================

Inventaire JSON
      |
      v
Validation des données
      |
      v
Principes de sécurité
      |
      v
Projet automation-lab
      |
      v
==========================================================
INTERMÉDIAIRE — AUTOMATISATION OPÉRATIONNELLE
==========================================================

Réutiliser l'inventaire
      |
      v
Connexion SSH contrôlée
      |
      v
Collecte multi-équipements
      |
      v
Sauvegardes datées
      |
      v
Comparaison des fichiers
      |
      v
Rapports et journaux
      |
      v
Tests hors ligne et en laboratoire
      |
      v
==========================================================
EXPERT — CONTRÔLE ET GOUVERNANCE
==========================================================

Définition d'un état attendu
      |
      v
Contrôles de conformité
      |
      v
Validation des résultats
      |
      v
Tests avant changement
      |
      v
Déploiement progressif et contrôlé
      |
      v
Vérification après changement
      |
      v
Stratégie de retour arrière
      |
      v
Intégration CI/CD et traçabilité
```

## 77. Contenu attendu du cours expert

Le cours expert devra approfondir les notions suivantes.

### État attendu et conformité

- Décrire l'état cible d'un équipement.
- Représenter les règles réseau dans des données structurées.
- Comparer les règles attendues avec les informations observées.
- Détecter et classer les écarts.
- Éviter les faux positifs et les faux négatifs.

### Tests et validation

- Tester les règles avant de modifier un équipement.
- Vérifier les préconditions d'une opération.
- Valider le résultat après un changement.
- Définir des critères d'acceptation.
- Produire des preuves et des rapports reproductibles.

### Déploiements contrôlés

- Définir un périmètre de déploiement.
- Évaluer les dépendances entre équipements.
- Prévoir des étapes de validation.
- Gérer les échecs partiels.
- Définir une stratégie de reprise adaptée.
- Éviter les modifications non autorisées.

### Intégration CI/CD

- Versionner le code.
- Exécuter des tests automatiques.
- Vérifier les changements avant leur déploiement.
- Contrôler les autorisations.
- Enregistrer les résultats.
- Organiser les validations humaines nécessaires.

Le cours expert devra réutiliser le projet existant et enrichir ses fonctions. Il ne devra pas repartir d'une application totalement différente.


# CONCLUSION GÉNÉRALE

Le niveau intermédiaire marque le passage entre la préparation d'une automatisation et son utilisation opérationnelle dans un laboratoire réseau.

L'apprenant a conservé l'inventaire du cours débutant et a appris à préparer les connexions SSH, collecter des informations, gérer les résultats et conserver des sauvegardes.

Il a également découvert la comparaison textuelle, la journalisation, la gestion des erreurs et les tests hors ligne.

Ces opérations sont essentielles pour construire une automatisation fiable. Elles permettent de connaître l'état des équipements, de conserver des traces et d'identifier les différences entre plusieurs observations.

Elles ne suffisent cependant pas à garantir la conformité du réseau ni la sécurité d'un changement automatisé.

Le niveau expert ajoutera donc les contrôles de conformité, la définition d'un état attendu, les tests avant et après changement, les déploiements progressifs et l'intégration dans une chaîne CI/CD.

**Principe final : collecter correctement, sauvegarder de manière fiable, comparer avec méthode, comprendre les écarts et ne déployer des changements que dans un processus testé, autorisé et contrôlé.**