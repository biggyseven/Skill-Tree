# Automatisation réseau — Niveau expert

## Conformité, tests avancés, déploiements contrôlés et intégration CI/CD


# PRÉSENTATION DU COURS

Ce cours constitue le troisième et dernier niveau du parcours d'automatisation réseau.

Au niveau débutant, l'apprenant a construit un inventaire JSON et appris à vérifier les données avant toute opération.

Au niveau intermédiaire, il a réutilisé ce projet pour préparer des connexions SSH, collecter des informations, sauvegarder les configurations, comparer des fichiers, journaliser les opérations et produire des rapports.

Au niveau expert, le projet `automation-lab` évolue vers une architecture capable de comparer un état réseau observé à un état attendu, d'évaluer la conformité, de tester des changements et de contrôler leur déploiement.

L'objectif n'est plus simplement d'exécuter des commandes sur plusieurs équipements. Il s'agit de concevoir un processus dans lequel chaque changement possède un objectif, des préconditions, des contrôles, des critères d'acceptation et une stratégie de traitement des échecs.

**Principe fondamental : une automatisation experte ne se contente pas d'exécuter une action. Elle doit pouvoir démontrer ce qu'elle a contrôlé, ce qu'elle a modifié et si le résultat obtenu correspond à celui qui était attendu.**

## Positionnement dans le parcours

```text
========================================================
NIVEAU 1 — DÉBUTANT
automation-debutant.md
========================================================

Comprendre l'automatisation
        |
        v
Apprendre Python et JSON
        |
        v
Construire un inventaire
        |
        v
Valider les données
        |
        v
Créer le projet automation-lab
        |
        v
========================================================
NIVEAU 2 — INTERMÉDIAIRE
automation-intermediaire.md
========================================================

Réutiliser l'inventaire
        |
        v
Préparer les connexions SSH
        |
        v
Collecter des informations
        |
        v
Automatiser les sauvegardes
        |
        v
Comparer les configurations
        |
        v
Journaliser les résultats
        |
        v
========================================================
NIVEAU 3 — EXPERT
automation-expert.md
========================================================

Définir un état attendu
        |
        v
Évaluer la conformité
        |
        v
Tester le code et les règles
        |
        v
Préparer un plan de changement
        |
        v
Valider les préconditions
        |
        v
Déployer progressivement
        |
        v
Vérifier le résultat réel
        |
        v
Gérer les échecs et le retour arrière
        |
        v
Intégrer le processus à une chaîne CI/CD
```

Les trois cours forment une progression continue. Il ne faut pas repartir de zéro au niveau expert : l'inventaire, les fonctions de validation, les collectes, les sauvegardes et les tests du niveau précédent servent de fondation.


# OBJECTIFS PÉDAGOGIQUES

À la fin de ce cours, l'apprenant doit pouvoir :

1. Concevoir une architecture d'automatisation réseau maintenable.
2. Définir un état réseau attendu dans des données structurées.
3. Normaliser les données collectées depuis plusieurs équipements.
4. Détecter les écarts entre l'état attendu et l'état observé.
5. Distinguer conformité, disponibilité et réussite d'une opération.
6. Construire des tests unitaires, d'intégration et de bout en bout.
7. Préparer des plans de changement vérifiables.
8. Contrôler les préconditions d'un déploiement.
9. Mettre en place des déploiements progressifs et des mécanismes d'arrêt.
10. Comprendre les limites du retour arrière automatique.
11. Produire des rapports de conformité et de déploiement.
12. Versionner le code, les règles et les changements.
13. Organiser une chaîne d'intégration continue.
14. Protéger les secrets et limiter les autorisations.
15. Construire un processus reproductible et auditable.

## Prérequis

L'apprenant doit maîtriser les éléments des niveaux précédents :

- Python : fonctions, exceptions, modules, fichiers et structures de données.
- JSON et validation d'inventaires.
- Connexions SSH et bibliothèques d'automatisation.
- Collecte d'informations multi-équipements.
- Sauvegardes et comparaison de fichiers.
- Journalisation et gestion des erreurs.
- Tests hors ligne.
- Commandes de diagnostic réseau.
- Principes de sécurité et de moindre privilège.
- Utilisation élémentaire de Git.

Il est également recommandé de connaître les notions de configuration attendue, de dérive de configuration, de tests de conformité et de déploiement logiciel.

## Règles de sécurité du cours

Les exemples de ce document utilisent des données fictives et des équipements de laboratoire.

Les opérations de modification sont présentées dans une approche contrôlée. Elles ne doivent être exécutées que sur des équipements autorisés, après vérification des préconditions et validation du mécanisme de reprise.

Une simulation réussie n'est pas une preuve que la même opération fonctionnera sans risque en production.


# PARTIE 1 — FAIRE ÉVOLUER L'ARCHITECTURE DU PROJET

## 1. Rappel du projet existant

Le projet des niveaux précédents possède déjà des composants essentiels :

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
|   +-- common.py
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
|   +-- config_A.cfg
|   +-- config_B.cfg
|
+-- reports/
|
+-- backups/
|
+-- logs/
|
+-- tests/
```

Cette structure permet de collecter et de comparer des informations.

Elle ne décrit cependant pas encore formellement la configuration que le réseau doit respecter.

Par exemple, si un commutateur contient trois VLAN, le programme peut relever leur présence et les comparer à une sauvegarde précédente. Il ne sait pas nécessairement si ces trois VLAN sont autorisés.

Pour effectuer ce contrôle, il faut définir un état attendu.

## 2. Architecture cible du niveau expert

```text
+----------------------------------------------------+
|                    ADMINISTRATEUR                  |
|              Définit les objectifs                 |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                      INVENTAIRE                    |
|           Cibles autorisées et plateformes         |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                    ÉTAT ATTENDU                    |
|           Règles et propriétés à respecter         |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                    COLLECTE RÉSEAU                 |
|        Données structurées et état observé         |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                  MOTEUR DE CONFORMITÉ              |
|         Comparaison et classification des écarts   |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                   RAPPORT DE CONTRÔLE              |
|          Conforme, non conforme ou inconnu         |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                   PLAN DE CHANGEMENT               |
|          Différences prévues et préconditions      |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                 APPROBATION ET GARDES              |
|     Autorisations, sauvegarde, fenêtre, périmètre  |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                  DÉPLOIEMENT CONTRÔLÉ               |
|       Progressif, vérifié et journalisé            |
+----------------------------+-----------------------+
                             |
                             v
+----------------------------------------------------+
|                 VALIDATION APRÈS CHANGEMENT        |
|          Résultat réel et décision finale          |
+----------------------------------------------------+
```

Cette architecture sépare la description de l'état souhaité, l'observation du réseau, l'analyse et l'exécution des changements.

Cette séparation est importante : une règle de conformité ne devrait pas être modifiée simplement parce que l'équipement observé ne la respecte pas.

## 3. Faire évoluer l'arborescence

Le projet peut maintenant adopter la structure suivante :

```text
automation-lab/
|
+-- README.md
|
+-- requirements.txt
|
+-- inventory/
|   |
|   +-- devices.json
|
+-- data/
|   |
|   +-- expected_state.json
|   |
|   +-- observed_state.json
|   |
|   +-- config_A.cfg
|   |
|   +-- config_B.cfg
|
+-- scripts/
|   |
|   +-- common.py
|   |
|   +-- collect_readonly.py
|   |
|   +-- backup_configs.py
|   |
|   +-- compare_configs.py
|   |
|   +-- compliance_check.py
|   |
|   +-- deployment_plan.py
|   |
|   +-- deployment_verify.py
|
+-- change-plans/
|   |
|   +-- CHG-DEMO-001.json
|
+-- reports/
|   |
|   +-- compliance/
|   |
|   +-- deployments/
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
|   |
|   +-- test_compliance.py
|   |
|   +-- test_deployment_plan.py
|   |
|   +-- test_observed_state.py
|
+-- .github/
    |
    +-- workflows/
        |
        +-- quality.yml
```

Les fichiers de cette arborescence seront créés au fil du cours. Le schéma représente l'organisation cible du projet, et non un répertoire déjà généré.


# PARTIE 2 — COMPRENDRE L'ÉTAT ATTENDU

## 4. Qu'est-ce qu'un état attendu ?

L'état attendu décrit les propriétés qu'un équipement doit présenter selon une politique définie.

Il ne s'agit pas nécessairement de recopier toute sa configuration. Il est souvent préférable de déclarer uniquement les propriétés réellement importantes pour le contrôle envisagé.

Pour un commutateur, l'état attendu peut notamment décrire :

- Le nom logique.
- Les VLAN obligatoires.
- Les VLAN autorisés.
- Certaines interfaces.
- Leur état administratif.
- Une description attendue.
- Les paramètres dont la conformité est essentielle.

Pour un routeur, les règles pourraient concerner les interfaces, des préfixes de routage, certains voisins ou des paramètres de sécurité.

Les données exactes dépendent de la politique de l'organisation.

## 5. Différence entre état attendu et état observé

L'état attendu représente la règle.

L'état observé représente les données réellement collectées.

```text
ÉTAT ATTENDU
SW1 doit posséder les VLAN 10 et 20.
L'interface Gi0/1 doit être active administrativement.
Sa description doit être UPLINK-CORE.
        |
        |
        v
    COMPARAISON
        ^
        |
        |
ÉTAT OBSERVÉ
SW1 possède les VLAN 10 et 20.
Gi0/1 est active administrativement.
Sa description est UPLINK-CORE.
        |
        v
RÉSULTAT
Les propriétés contrôlées sont conformes.
```

Dans cet exemple, le contrôle ne vérifie que les propriétés déclarées. Il ne prouve pas que l'ensemble de la configuration du commutateur est correct.

## 6. Pourquoi ne pas comparer uniquement les configurations textuelles ?

La comparaison textuelle est utile, mais elle possède des limites.

Deux configurations peuvent produire des textes différents tout en représentant le même état utile au contrôle.

À l'inverse, deux fichiers visuellement proches peuvent représenter des différences importantes.

Une approche experte distingue donc :

1. La comparaison textuelle des fichiers.
2. La comparaison des données structurées.
3. La validation de règles métier.
4. L'analyse de l'impact d'un changement.

```text
CONFIGURATION BRUTE
        |
        v
Collecte et interprétation
        |
        v
DONNÉES STRUCTURÉES
        |
        v
ÉTAT OBSERVÉ NORMALISÉ
        |
        v
RÈGLES DE CONFORMITÉ
        |
        v
ÉCARTS CLASSÉS
        |
        v
DÉCISION DOCUMENTÉE
```

L'interprétation d'une configuration dépend de la plateforme et de ses fonctionnalités. Il ne faut pas inventer une normalisation qui ignorerait des paramètres importants.

Une collecte structurée fournie directement par une API ou un pilote adapté peut être préférable à l'analyse de texte libre, lorsque la plateforme le permet.


# PARTIE 3 — DÉFINIR UNE POLITIQUE DE CONFORMITÉ

## 7. Créer `expected_state.json`

Créez le fichier :

`data/expected_state.json`

```json
{
  "schema_version": 1,
  "devices": {
    "SW1": {
      "hostname": "SW1",
      "required_vlans": [10, 20],
      "allowed_vlans": [10, 20, 99],
      "interfaces": {
        "GigabitEthernet0/1": {
          "admin_status": "up",
          "description": "UPLINK-CORE"
        }
      }
    },
    "SW2": {
      "hostname": "SW2",
      "required_vlans": [10, 20],
      "allowed_vlans": [10, 20, 99],
      "interfaces": {
        "GigabitEthernet0/1": {
          "admin_status": "up",
          "description": "UPLINK-CORE"
        }
      }
    }
  }
}
```

Les noms d'interfaces et les propriétés sont des données fictives de laboratoire.

### Signification des propriétés

| Propriété | Signification |
|---|---|
| `schema_version` | Version du format des règles |
| `devices` | Équipements auxquels les règles s'appliquent |
| `hostname` | Nom attendu |
| `required_vlans` | VLAN qui doivent obligatoirement exister |
| `allowed_vlans` | VLAN autorisés dans le périmètre du contrôle |
| `interfaces` | Interfaces dont certaines propriétés doivent être vérifiées |
| `admin_status` | État administratif attendu |
| `description` | Description attendue |

La liste `allowed_vlans` ne signifie pas qu'il faut supprimer automatiquement tous les autres VLAN. Elle indique uniquement que la politique de cet exemple considère les VLAN non déclarés comme des écarts à examiner.

La décision de suppression exige des contrôles supplémentaires.

## 8. Créer un état observé fictif

Créez :

`data/observed_state.json`

```json
{
  "schema_version": 1,
  "devices": {
    "SW1": {
      "hostname": "SW1",
      "vlans": [10, 20, 99],
      "interfaces": {
        "GigabitEthernet0/1": {
          "admin_status": "up",
          "description": "UPLINK-CORE"
        }
      }
    },
    "SW2": {
      "hostname": "SW2",
      "vlans": [10],
      "interfaces": {
        "GigabitEthernet0/1": {
          "admin_status": "down",
          "description": "UPLINK-CORE"
        }
      }
    }
  }
}
```

Ces données sont fictives. Elles servent à tester le moteur de conformité sans dépendre d'une connexion réseau.

Dans cet exemple :

- SW1 doit être conforme aux propriétés contrôlées.
- SW2 ne respecte pas plusieurs règles.

Le moteur devra identifier les différences sans modifier les données.

## 9. Schéma de décision

```text
             ÉTAT ATTENDU
                  |
                  v
             RÈGLES DÉFINIES
                  |
                  v
              ÉTAT OBSERVÉ
                  |
                  v
              COMPARAISON
                  |
          +-------+--------+
          |                |
          v                v
    Règles respectées   Écart détecté
          |                |
          v                v
      Conforme       Classification
                           |
                           v
                    Rapport d'écart
                           |
                           v
                    Analyse humaine
```

Le contrôle doit également distinguer les informations absentes des informations qui prouvent qu'une règle n'est pas respectée.

Par exemple, si l'état d'une interface est inconnu, le programme ne doit pas automatiquement conclure que l'interface est arrêtée.

Il doit présenter un résultat de contrôle incomplet.


# PARTIE 4 — CONSTRUIRE LE MOTEUR DE CONFORMITÉ

## 10. Préparer les catégories de résultats

Un moteur de conformité peut produire plusieurs catégories.

**Conforme :** les règles évaluées sont respectées.

**Non conforme :** une ou plusieurs règles sont explicitement violées.

**Inconnu :** les données disponibles ne permettent pas de conclure.

**Erreur d'exécution :** le fichier, le traitement ou une dépendance n'a pas pu être utilisé correctement.

Ces catégories doivent rester distinctes.

```text
CONTRÔLE
   |
   v
Données exploitables ?
   |
   +---- NON -----------------> INCONNU ou ERREUR
   |
   v
Règles évaluées
   |
   +---- Toutes respectées ---> CONFORME
   |
   +---- Écart établi --------> NON CONFORME
   |
   +---- Information absente -> INCONNU
```

Une collecte manquante ne doit jamais être considérée comme une conformité réussie.

## 11. Créer `compliance_check.py`

Créez :

`scripts/compliance_check.py`

```python
import json

from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

EXPECTED_PATH = ROOT_DIR / "data" / "expected_state.json"
OBSERVED_PATH = ROOT_DIR / "data" / "observed_state.json"

REPORT_DIR = ROOT_DIR / "reports" / "compliance"


def load_json(path: Path) -> dict:
    """Lit un document JSON et vérifie sa racine."""

    if not path.is_file():
        raise FileNotFoundError(
            f"Fichier introuvable : {path}"
        )

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON invalide dans {path.name} : {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"La racine de {path.name} doit être un objet."
        )

    return data


def add_finding(findings, device, rule, status, message):
    """Ajoute un résultat de contrôle normalisé."""

    findings.append({
        "device": device,
        "rule": rule,
        "status": status,
        "message": message,
    })


def evaluate_device(name, expected, observed):
    """Compare un équipement à ses règles attendues."""

    findings = []

    if not isinstance(expected, dict):
        add_finding(
            findings,
            name,
            "expected_state",
            "unknown",
            "Les règles attendues sont invalides."
        )
        return findings

    if not isinstance(observed, dict):
        add_finding(
            findings,
            name,
            "observed_state",
            "unknown",
            "L'état observé est absent ou invalide."
        )
        return findings

    # Vérification du nom logique.
    expected_hostname = expected.get("hostname")
    observed_hostname = observed.get("hostname")

    if observed_hostname is None:
        add_finding(
            findings,
            name,
            "hostname",
            "unknown",
            "Le nom observé est absent."
        )
    elif observed_hostname != expected_hostname:
        add_finding(
            findings,
            name,
            "hostname",
            "non_compliant",
            f"Nom attendu : {expected_hostname}; "
            f"nom observé : {observed_hostname}."
        )
    else:
        add_finding(
            findings,
            name,
            "hostname",
            "compliant",
            "Nom conforme."
        )

    # Vérification des VLAN.
    observed_vlans = observed.get("vlans")

    if not isinstance(observed_vlans, list):
        add_finding(
            findings,
            name,
            "vlans",
            "unknown",
            "La liste des VLAN observés est absente ou invalide."
        )
    else:
        observed_set = set(observed_vlans)

        required_vlans = expected.get("required_vlans", [])

        if not isinstance(required_vlans, list):
            add_finding(
                findings,
                name,
                "required_vlans",
                "unknown",
                "La règle required_vlans est invalide."
            )
        else:
            missing_vlans = sorted(
                set(required_vlans) - observed_set
            )

            if missing_vlans:
                add_finding(
                    findings,
                    name,
                    "required_vlans",
                    "non_compliant",
                    f"VLAN obligatoires absents : {missing_vlans}."
                )
            else:
                add_finding(
                    findings,
                    name,
                    "required_vlans",
                    "compliant",
                    "Tous les VLAN obligatoires sont présents."
                )

        allowed_vlans = expected.get("allowed_vlans")

        if allowed_vlans is not None:
            if not isinstance(allowed_vlans, list):
                add_finding(
                    findings,
                    name,
                    "allowed_vlans",
                    "unknown",
                    "La règle allowed_vlans est invalide."
                )
            else:
                unexpected = sorted(
                    observed_set - set(allowed_vlans)
                )

                if unexpected:
                    add_finding(
                        findings,
                        name,
                        "allowed_vlans",
                        "non_compliant",
                        f"VLAN non déclarés comme autorisés : "
                        f"{unexpected}."
                    )
                else:
                    add_finding(
                        findings,
                        name,
                        "allowed_vlans",
                        "compliant",
                        "Tous les VLAN observés sont autorisés."
                    )

    # Vérification des interfaces déclarées dans les règles.
    expected_interfaces = expected.get("interfaces", {})
    observed_interfaces = observed.get("interfaces", {})

    if not isinstance(expected_interfaces, dict):
        add_finding(
            findings,
            name,
            "interfaces",
            "unknown",
            "Les règles d'interfaces sont invalides."
        )
        return findings

    if not isinstance(observed_interfaces, dict):
        add_finding(
            findings,
            name,
            "interfaces",
            "unknown",
            "Les interfaces observées sont absentes ou invalides."
        )
        return findings

    for interface_name, expected_properties in expected_interfaces.items():
        if interface_name not in observed_interfaces:
            add_finding(
                findings,
                name,
                f"interface:{interface_name}",
                "unknown",
                "L'interface n'a pas été observée."
            )
            continue

        observed_properties = observed_interfaces[interface_name]

        if not isinstance(expected_properties, dict):
            add_finding(
                findings,
                name,
                f"interface:{interface_name}",
                "unknown",
                "Les règles de l'interface sont invalides."
            )
            continue

        if not isinstance(observed_properties, dict):
            add_finding(
                findings,
                name,
                f"interface:{interface_name}",
                "unknown",
                "Les propriétés observées sont invalides."
            )
            continue

        for property_name, expected_value in expected_properties.items():
            observed_value = observed_properties.get(property_name)

            rule_name = (
                f"interface:{interface_name}:{property_name}"
            )

            if observed_value is None:
                add_finding(
                    findings,
                    name,
                    rule_name,
                    "unknown",
                    "La propriété observée est absente."
                )
            elif observed_value != expected_value:
                add_finding(
                    findings,
                    name,
                    rule_name,
                    "non_compliant",
                    f"Attendu : {expected_value}; "
                    f"observé : {observed_value}."
                )
            else:
                add_finding(
                    findings,
                    name,
                    rule_name,
                    "compliant",
                    "Propriété conforme."
                )

    return findings


def evaluate_compliance(expected_document, observed_document):
    """Évalue la conformité de tous les équipements déclarés."""

    if expected_document.get("schema_version") != 1:
        raise ValueError(
            "Version du schéma attendu non prise en charge."
        )

    if observed_document.get("schema_version") != 1:
        raise ValueError(
            "Version du schéma observé non prise en charge."
        )

    expected_devices = expected_document.get("devices")
    observed_devices = observed_document.get("devices")

    if not isinstance(expected_devices, dict):
        raise ValueError(
            "Le document attendu doit contenir un objet devices."
        )

    if not isinstance(observed_devices, dict):
        raise ValueError(
            "Le document observé doit contenir un objet devices."
        )

    all_findings = []

    for name, expected in expected_devices.items():
        observed = observed_devices.get(name)

        if observed is None:
            all_findings.append({
                "device": name,
                "rule": "device",
                "status": "unknown",
                "message": "Aucun état observé disponible.",
            })
            continue

        all_findings.extend(
            evaluate_device(name, expected, observed)
        )

    statuses = [
        finding["status"]
        for finding in all_findings
    ]

    if "non_compliant" in statuses:
        overall_status = "non_compliant"
    elif "unknown" in statuses:
        overall_status = "incomplete"
    else:
        overall_status = "compliant"

    return {
        "status": overall_status,
        "total_checks": len(all_findings),
        "compliant": statuses.count("compliant"),
        "non_compliant": statuses.count("non_compliant"),
        "unknown": statuses.count("unknown"),
        "findings": all_findings,
    }


def main():
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    expected = load_json(EXPECTED_PATH)
    observed = load_json(OBSERVED_PATH)

    result = evaluate_compliance(
        expected,
        observed
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    result["created_at_utc"] = timestamp

    report_path = (
        REPORT_DIR
        / f"compliance_{timestamp}.json"
    )

    report_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"Statut global : {result['status']}")
    print(f"Contrôles : {result['total_checks']}")
    print(f"Conformes : {result['compliant']}")
    print(f"Non conformes : {result['non_compliant']}")
    print(f"Inconnus : {result['unknown']}")
    print(f"Rapport : {report_path}")

    if result["status"] == "non_compliant":
        raise SystemExit(2)

    if result["status"] == "incomplete":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
```

## 12. Exécuter le contrôle

Depuis la racine de `automation-lab` :

```bash
python scripts/compliance_check.py
```

Avec les données fictives fournies, le résultat global doit être non conforme, car SW2 ne respecte pas plusieurs propriétés.

Le programme doit produire un rapport dans :

```text
reports/compliance/
```

## 13. Interpréter le résultat

Le programme distingue les résultats conformes, les violations explicites et les informations inconnues.

Une propriété absente ne reçoit pas automatiquement le statut non conforme. Elle reçoit `unknown`, car le programme n'a pas suffisamment d'informations pour décider.

Une violation explicitement constatée produit `non_compliant`.

Cette distinction est importante dans un système automatisé : une absence de données ne doit pas être présentée comme une preuve de conformité ou comme une preuve certaine de violation.

### Exemple de rapport synthétique

```text
Contrôle de conformité
=====================

SW1
    hostname                  : conforme
    VLAN obligatoires         : conforme
    VLAN autorisés            : conforme
    interface Gi0/1 admin     : conforme
    interface Gi0/1 description : conforme

SW2
    hostname                  : conforme
    VLAN obligatoires         : non conforme
    interface Gi0/1 admin     : non conforme

Résultat global : NON CONFORME
```

Les noms d'interfaces sont abrégés ici pour faciliter la lecture. Le rapport JSON conserve les identifiants de règles produits par le script.

### Limites du moteur

Ce programme constitue un moteur pédagogique de base. Il ne valide pas automatiquement la totalité d'un réseau réel.

Il ne vérifie pas, entre autres :

- La qualité du collecteur qui a produit l'état observé.
- L'exactitude de chaque donnée.
- L'existence des équipements non déclarés dans l'inventaire attendu.
- Les dépendances entre interfaces et VLAN.
- Le comportement du réseau en situation réelle.
- La conformité de fonctions qui ne sont pas présentes dans les règles.

Un contrôle de conformité n'est fiable que si les données et les règles utilisées sont elles-mêmes correctement conçues.


# PARTIE 5 — NORMALISER LES DONNÉES COLLECTÉES

## 14. Pourquoi normaliser ?

Différents équipements peuvent représenter une même propriété de manière différente.

Un constructeur peut renvoyer un état d'interface sous la forme `up`, tandis qu'un autre emploie une structure ou une valeur différente.

Le moteur de conformité ne devrait pas devoir connaître tous les détails des réponses brutes de tous les constructeurs.

Il est préférable de séparer :

1. La collecte.
2. L'interprétation des réponses.
3. La normalisation.
4. La validation de conformité.

```text
ROUTEUR A                 COMMUTATEUR B
    |                          |
    v                          v
Réponse brute A            Réponse brute B
    |                          |
    v                          v
Adaptateur A                Adaptateur B
    |                          |
    +-------------+------------+
                  |
                  v
          FORMAT NORMALISÉ
                  |
                  v
          MOTEUR DE CONFORMITÉ
                  |
                  v
          RAPPORT UNIFIÉ
```

Les adaptateurs doivent tenir compte des particularités de chaque plateforme. Une valeur ne doit pas être normalisée uniquement parce qu'elle ressemble à une valeur connue.

## 15. Séparer le collecteur et le moteur de conformité

Le collecteur est responsable de la récupération des données.

Le moteur de conformité est responsable de l'application des règles.

```text
COLLECTEUR
    |
    +---- Se connecte à la cible
    |
    +---- Récupère les informations
    |
    +---- Interprète les réponses
    |
    +---- Produit l'état observé
                |
                v
          ÉTAT OBSERVÉ JSON
                |
                v
       MOTEUR DE CONFORMITÉ
                |
                +---- Charge les règles
                |
                +---- Évalue les propriétés
                |
                +---- Classe les écarts
                |
                v
             RAPPORT
```

Cette séparation permet de tester les règles sans effectuer de connexion réseau.

Elle permet également de remplacer un collecteur sans réécrire intégralement la logique de conformité.

## 16. Éviter de confondre données observées et données souhaitées

L'état attendu doit provenir de règles contrôlées et versionnées.

L'état observé doit provenir des collectes réellement effectuées.

Le moteur doit utiliser ces deux sources distinctes.

Si un programme remplace automatiquement une règle attendue par la valeur observée dès qu'un écart apparaît, il peut faire disparaître la notion même de conformité.

Les règles attendues doivent être modifiées selon une procédure explicite et traçable.


# PARTIE 6 — MESURER LA DÉRIVE DE CONFIGURATION

## 17. Qu'est-ce que la dérive ?

La dérive correspond à une différence entre l'état actuellement observé et l'état qui devait être maintenu.

Elle peut provenir de plusieurs causes :

- Une modification manuelle.
- Un changement automatisé précédent.
- Une erreur de configuration.
- Un équipement remplacé.
- Une règle attendue devenue obsolète.
- Une collecte incomplète.
- Un changement temporaire ou planifié.

La détection d'une dérive ne permet pas à elle seule d'en déterminer la cause.

### Schéma — évolution de la dérive

```text
ÉTAT ATTENDU À T0
        |
        v
Collecte initiale
        |
        v
ÉTAT CONFORME
        |
        | Changements au cours du temps
        v
Nouvelle collecte à T1
        |
        v
COMPARAISON
        |
        +---- Aucun écart
        |         |
        |         v
        |     Toujours conforme
        |
        +---- Écart détecté
                  |
                  v
              DÉRIVE
                  |
                  v
          Analyse de la cause
                  |
                  v
         Décision et remédiation
```

## 18. Détecter n'est pas corriger

Un système peut détecter une dérive sans corriger automatiquement l'équipement.

La correction automatique présente des risques si les règles sont incomplètes ou si le changement a des dépendances non modélisées.

Une approche progressive distingue :

- La détection.
- L'analyse.
- La proposition de correction.
- L'approbation.
- L'exécution.
- La vérification après changement.

Le mode de fonctionnement initial recommandé pour un projet expert est la génération d'un rapport et d'un plan, sans appliquer de correction automatique.

## 19. Définir les niveaux de sévérité

Toutes les différences n'ont pas les mêmes conséquences.

Une politique peut classer les écarts en différentes catégories :

| Niveau | Exemple conceptuel | Traitement |
|---|---|---|
| Information | Modification de description sans impact identifié | Documenter |
| Faible | Paramètre secondaire qui diffère de la règle | Examiner |
| Élevé | VLAN obligatoire absent | Investigation prioritaire |
| Critique | Propriété de sécurité essentielle incorrecte | Suspendre le déploiement concerné |

La sévérité doit être définie par les responsables techniques et de sécurité de l'organisation.

Le script présenté précédemment classe les résultats en conforme, non conforme et inconnu. Pour une application réelle, il peut être complété par une propriété `severity` définie dans les règles.


# PARTIE 7 — TESTER LE MOTEUR DE CONFORMITÉ

## 20. Pourquoi les tests sont essentiels

Un moteur de conformité peut produire des conclusions incorrectes si ses règles sont mal implémentées.

Une mauvaise comparaison peut déclarer conforme un équipement qui ne l'est pas.

À l'inverse, un contrôle trop strict peut générer un grand nombre d'alertes inutiles.

Les tests permettent de vérifier le comportement du programme sur différents scénarios.

## 21. Les familles de tests

### Tests unitaires

Ils testent une fonction isolée, par exemple le contrôle des VLAN.

### Tests d'intégration

Ils vérifient que plusieurs composants fonctionnent ensemble, par exemple la lecture des fichiers et l'évaluation complète.

### Tests de bout en bout

Ils vérifient le processus global à partir d'un inventaire et d'un ensemble de données jusqu'à la production du rapport.

### Tests de non-régression

Ils confirment qu'une modification du code n'introduit pas une erreur dans une fonctionnalité qui fonctionnait auparavant.

```text
                 CODE PYTHON
                     |
                     v
                TESTS UNITAIRES
                     |
                     v
              TESTS D'INTÉGRATION
                     |
                     v
               TESTS COMPLETS
                     |
                     v
            TESTS DE NON-RÉGRESSION
                     |
                     v
                RÉSULTATS VALIDÉS
```

## 22. Utiliser `unittest` pour tester les règles

Le module `unittest` appartient à la bibliothèque standard de Python.

Créez :

`tests/test_compliance.py`

```python
import unittest

from scripts.compliance_check import evaluate_compliance


class ComplianceTests(unittest.TestCase):

    def setUp(self):
        self.expected = {
            "schema_version": 1,
            "devices": {
                "SW1": {
                    "hostname": "SW1",
                    "required_vlans": [10, 20],
                    "allowed_vlans": [10, 20, 99],
                    "interfaces": {
                        "Gi0/1": {
                            "admin_status": "up",
                            "description": "UPLINK-CORE",
                        }
                    },
                }
            },
        }

        self.observed = {
            "schema_version": 1,
            "devices": {
                "SW1": {
                    "hostname": "SW1",
                    "vlans": [10, 20],
                    "interfaces": {
                        "Gi0/1": {
                            "admin_status": "up",
                            "description": "UPLINK-CORE",
                        }
                    },
                }
            },
        }

    def test_compliant_device(self):
        result = evaluate_compliance(
            self.expected,
            self.observed,
        )

        self.assertEqual(
            result["status"],
            "compliant",
        )

    def test_missing_required_vlan(self):
        self.observed["devices"]["SW1"]["vlans"] = [10]

        result = evaluate_compliance(
            self.expected,
            self.observed,
        )

        self.assertEqual(
            result["status"],
            "non_compliant",
        )

    def test_wrong_interface_state(self):
        self.observed["devices"]["SW1"]["interfaces"]["Gi0/1"][
            "admin_status"
        ] = "down"

        result = evaluate_compliance(
            self.expected,
            self.observed,
        )

        self.assertEqual(
            result["status"],
            "non_compliant",
        )

    def test_missing_observed_device(self):
        self.observed["devices"] = {}

        result = evaluate_compliance(
            self.expected,
            self.observed,
        )

        self.assertEqual(
            result["status"],
            "incomplete",
        )

    def test_unknown_interface_property(self):
        del self.observed["devices"]["SW1"]["interfaces"]["Gi0/1"][
            "description"
        ]

        result = evaluate_compliance(
            self.expected,
            self.observed,
        )

        self.assertEqual(
            result["status"],
            "incomplete",
        )


if __name__ == "__main__":
    unittest.main()
```

Le test importe le moteur de conformité depuis le répertoire `scripts`.

Pour que cet import fonctionne comme un paquet Python, créez un fichier vide :

`scripts/__init__.py`

Exécutez ensuite les tests depuis la racine du projet :

```bash
python -m unittest discover -s tests
```

Les tests utilisent des objets Python fictifs. Ils n'établissent aucune connexion réseau.

## 23. Interpréter les tests

Un test réussi indique que le programme s'est comporté comme attendu pour le cas testé.

Il ne prouve pas que toutes les situations possibles sont correctement gérées.

Par exemple, les tests précédents vérifient quelques propriétés des VLAN et des interfaces. Ils ne prouvent pas que le collecteur réseau produit toujours des données exactes ni que le réseau fonctionnerait correctement après un changement.

Un programme expert doit disposer de tests suffisamment variés pour couvrir les règles importantes et les erreurs connues.

## 24. Éviter les tests trop dépendants de données réelles

Un test ne devrait pas nécessiter systématiquement une connexion SSH à un équipement physique.

Une grande partie de la logique peut être vérifiée avec des objets simulés ou des fichiers temporaires.

Les tests de connexion réelle doivent être regroupés dans une catégorie séparée, exécutée uniquement lorsque le laboratoire est disponible.

Cette distinction rend les tests plus reproductibles et réduit le risque d'effets indésirables.


# PARTIE 8 — CONCEVOIR UN PLAN DE CHANGEMENT

## 25. Pourquoi formaliser les changements ?

Un changement de configuration peut avoir des effets qui dépassent l'équipement ciblé.

Modifier un VLAN, une interface, une route ou une politique d'accès peut affecter d'autres équipements et services.

Un plan de changement formalise les informations nécessaires à la décision.

Il doit notamment préciser :

- L'identifiant du changement.
- L'objectif.
- Les cibles concernées.
- L'état initial.
- L'état final attendu.
- Les préconditions.
- Le plan de validation.
- Les risques.
- La fenêtre d'exécution.
- La stratégie de retour arrière.
- L'autorité d'approbation.

Le plan doit rester distinct du code qui exécute les opérations.

## 26. Exemple de plan de changement

Créez :

`change-plans/CHG-DEMO-001.json`

```json
{
  "change_id": "CHG-DEMO-001",
  "description": "Exemple pédagogique de modification contrôlée",
  "environment": "lab",
  "targets": [
    "SW1"
  ],
  "mode": "plan_only",
  "approved": false,
  "preconditions": {
    "inventory_valid": true,
    "backup_available": true,
    "lab_environment_confirmed": true,
    "maintenance_window_confirmed": false
  },
  "validation": {
    "required_checks": [
      "connectivity",
      "configuration_state",
      "post_change_compliance"
    ]
  },
  "rollback": {
    "backup_required": true,
    "procedure_documented": false,
    "tested": false
  }
}
```

Ce plan ne déclenche aucun changement.

Il sert de démonstration d'un document de préparation. La valeur `approved: false` interdit tout déploiement dans le processus que nous allons construire.

La présence d'une valeur `true` dans le fichier ne constitue pas une preuve indépendante que le contrôle correspondant a réellement été effectué.

Un système réel doit distinguer les déclarations du demandeur des preuves produites par les contrôles.

## 27. Schéma d'un changement contrôlé

```text
DEMANDE DE CHANGEMENT
         |
         v
Définition de l'objectif
         |
         v
Liste des équipements
         |
         v
Analyse des dépendances
         |
         v
Préconditions
         |
         v
Sauvegarde et plan de retour arrière
         |
         v
Validation technique
         |
         v
Approbation requise
         |
         v
Fenêtre autorisée
         |
         v
Exécution progressive
         |
         v
Tests après changement
         |
         +--------------------------+
         |                          |
         v                          v
Résultat acceptable          Résultat non acceptable
         |                          |
         v                          v
Clôture et preuve            Arrêt et procédure
de validation                de reprise autorisée
```

Le retour arrière n'est pas une opération universelle. Certains changements sont réversibles, d'autres non, et certains exigent une procédure spécifique.

La procédure doit être adaptée à chaque type de changement.


# PARTIE 9 — AJOUTER DES GARDES AU DÉPLOIEMENT

## 28. Les préconditions

Une précondition est une condition qui doit être satisfaite avant l'exécution d'une opération.

Exemples :

- Le projet est sur une version approuvée.
- L'inventaire est valide.
- Les équipements ciblés sont autorisés.
- La sauvegarde préalable existe et a été vérifiée.
- Les données initiales ont été collectées.
- Les dépendances critiques sont disponibles.
- La fenêtre de changement est ouverte.
- L'approbation requise est valide.
- Une procédure de reprise est définie lorsque le changement l'exige.

Une précondition ne doit pas être considérée comme satisfaite simplement parce qu'une valeur a été ajoutée manuellement dans un JSON.

Les contrôles doivent être vérifiables et indépendants autant que possible.

## 29. Exécution en mode plan

Un mode plan présente ce que le programme prévoit de faire sans appliquer le changement.

Il permet notamment de vérifier :

- Les cibles.
- Les fichiers utilisés.
- Les règles applicables.
- Le périmètre du changement.
- Les préconditions.
- Les différences envisagées.

```text
PLAN DE CHANGEMENT
        |
        v
Validation du plan
        |
        v
Préparation des opérations
        |
        v
Affichage des différences
        |
        v
Rapport de préconditions
        |
        v
Aucune modification
        |
        v
Décision de validation
```

Le mode plan doit être le comportement par défaut des scripts qui envisagent des changements.

Dans une architecture robuste, la fonction qui produit un plan devrait être distincte de celle qui applique effectivement une modification.

## 30. Créer un validateur de plan

Créez :

`scripts/deployment_plan.py`

```python
import json

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

PLAN_PATH = (
    ROOT_DIR
    / "change-plans"
    / "CHG-DEMO-001.json"
)

ALLOWED_ENVIRONMENTS = {
    "lab",
}


def load_plan(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(
            f"Plan introuvable : {path}"
        )

    try:
        plan = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Plan JSON invalide : {exc}"
        ) from exc

    if not isinstance(plan, dict):
        raise ValueError(
            "La racine du plan doit être un objet."
        )

    return plan


def validate_plan(plan: dict) -> list[str]:
    """Retourne les problèmes qui empêchent d'autoriser le plan."""

    problems = []

    required_fields = {
        "change_id",
        "description",
        "environment",
        "targets",
        "mode",
        "approved",
        "preconditions",
        "validation",
        "rollback",
    }

    missing = required_fields - plan.keys()

    if missing:
        problems.append(
            f"Champs manquants : {sorted(missing)}"
        )
        return problems

    if not isinstance(plan["change_id"], str) or not plan["change_id"].strip():
        problems.append("Identifiant de changement invalide.")

    if plan["environment"] not in ALLOWED_ENVIRONMENTS:
        problems.append(
            "Environnement non autorisé par ce programme."
        )

    targets = plan["targets"]

    if not isinstance(targets, list) or not targets:
        problems.append(
            "La liste des cibles est vide ou invalide."
        )
    elif any(
        not isinstance(target, str) or not target.strip()
        for target in targets
    ):
        problems.append(
            "Une cible est vide ou invalide."
        )
    elif len(targets) != len(set(targets)):
        problems.append(
            "La liste des cibles contient des doublons."
        )

    if plan["mode"] != "plan_only":
        problems.append(
            "Ce validateur n'autorise que le mode plan_only."
        )

    if plan["approved"] is not False:
        problems.append(
            "Le plan doit rester explicitement non exécuté."
        )

    preconditions = plan["preconditions"]

    if not isinstance(preconditions, dict):
        problems.append(
            "Les préconditions sont invalides."
        )
    else:
        required_preconditions = {
            "inventory_valid",
            "backup_available",
            "lab_environment_confirmed",
            "maintenance_window_confirmed",
        }

        missing_preconditions = (
            required_preconditions - preconditions.keys()
        )

        if missing_preconditions:
            problems.append(
                "Préconditions manquantes : "
                f"{sorted(missing_preconditions)}"
            )

    validation = plan["validation"]

    if (
        not isinstance(validation, dict)
        or not isinstance(
            validation.get("required_checks"),
            list
        )
        or not validation["required_checks"]
    ):
        problems.append(
            "Le plan de validation est absent ou invalide."
        )

    rollback = plan["rollback"]

    if not isinstance(rollback, dict):
        problems.append(
            "Les informations de retour arrière sont invalides."
        )
    else:
        if rollback.get("backup_required") is not True:
            problems.append(
                "Une sauvegarde préalable est obligatoire."
            )

    return problems


def main():
    plan = load_plan(PLAN_PATH)
    problems = validate_plan(plan)

    print(f"Changement : {plan.get('change_id', 'inconnu')}")
    print(f"Environnement : {plan.get('environment', 'inconnu')}")
    print(f"Mode : {plan.get('mode', 'inconnu')}")
    print()

    if problems:
        print("Plan non validé :")

        for problem in problems:
            print(f"- {problem}")

        raise SystemExit(2)

    print("Structure du plan valide.")
    print("Mode plan uniquement.")
    print("Aucune modification réseau n'a été exécutée.")


if __name__ == "__main__":
    main()
```

## 31. Exécuter le validateur

Depuis la racine du projet :

```bash
python scripts/deployment_plan.py
```

Avec le plan de démonstration, le programme doit confirmer que la structure est acceptable pour un mode plan uniquement.

Il ne doit pas lancer de connexion de modification.

### Limite importante

Le programme vérifie la structure des déclarations. Il ne prouve pas que la sauvegarde existe réellement, que la fenêtre de maintenance est ouverte ou que l'approbation a été accordée.

Ces propriétés exigent des contrôles externes ou des preuves vérifiables.

Le mode plan est un mécanisme de transparence, pas un mécanisme suffisant de sécurité à lui seul.


# PARTIE 10 — APPROBATION ET GESTION DU CHANGEMENT

## 32. Pourquoi une approbation indépendante ?

Une automatisation peut être techniquement correcte tout en appliquant une modification qui n'est pas autorisée au moment prévu.

L'approbation permet de vérifier que le changement est justifié, que son périmètre est connu et que les conditions nécessaires sont réunies.

Pour les opérations critiques, il est préférable que la personne qui demande le changement ne soit pas la seule à pouvoir l'autoriser.

La politique exacte dépend de l'organisation.

## 33. Chaîne de validation

```text
CODE MODIFIÉ
      |
      v
Tests unitaires
      |
      v
Tests d'intégration
      |
      v
Revue du code
      |
      v
Validation du plan
      |
      v
Revue de sécurité
      |
      v
Approbation du changement
      |
      v
Vérification des préconditions
      |
      v
Déploiement autorisé
```

Les étapes de revue et d'approbation ne devraient pas être supprimées simplement pour accélérer l'exécution.

## 34. Séparer les preuves des déclarations

Un système peut enregistrer différents éléments :

- L'identité de la personne qui a demandé le changement.
- L'identité du réviseur.
- La version du code.
- La version des règles.
- Le rapport de préconditions.
- La date d'approbation.
- Les résultats des tests.
- Les résultats du déploiement.

Ces éléments permettent de reconstruire l'historique.

Ils ne doivent pas être modifiables librement après coup sans trace. Les politiques de conservation et d'intégrité doivent être adaptées aux besoins d'audit.


# PARTIE 11 — DÉPLOYER PROGRESSIVEMENT

## 35. Pourquoi ne pas modifier tous les équipements à la fois ?

Une modification peut être correcte sur un équipement et provoquer un problème ailleurs en raison d'une différence de topologie, de rôle ou de configuration.

Un déploiement progressif limite le périmètre affecté tant que les contrôles ne sont pas terminés.

```text
ENSEMBLE DES CIBLES
        |
        v
Sélection d'un premier équipement
        |
        v
Application du changement autorisé
        |
        v
Contrôles après changement
        |
        +--------------------------+
        |                          |
        v                          v
Résultat acceptable          Échec ou doute
        |                          |
        v                          v
Poursuivre vers la            Arrêter le processus
prochaine cible               selon la politique
        |
        v
Déploiement progressif
```

Un déploiement progressif n'est pas simplement une boucle qui s'arrête après une exception. Il doit définir les critères de succès, le périmètre et le comportement en cas d'échec.

## 36. Définir les critères d'arrêt

Le déploiement doit s'arrêter lorsque des conditions importantes ne sont plus satisfaites.

Exemples :

- La sauvegarde préalable est absente.
- La cible ne correspond pas à l'inventaire approuvé.
- Une dépendance essentielle est indisponible.
- Un contrôle de précondition échoue.
- Le résultat après changement ne respecte pas les critères d'acceptation.
- La méthode de reprise ne peut pas être utilisée.
- Le changement dépasse le périmètre autorisé.

Les conditions d'arrêt doivent être écrites et testées avant le déploiement.

## 37. Ne pas confondre reprise et retour arrière

Lorsqu'une opération échoue, plusieurs stratégies sont possibles :

- Arrêter les changements restants.
- Réessayer une opération idempotente si les conditions le permettent.
- Restaurer un état précédent.
- Utiliser un mécanisme de retour arrière natif.
- Faire intervenir un administrateur.
- Maintenir l'équipement dans un état sûr et documenter l'incident.

Le choix dépend du type de changement.

Une reprise ne doit jamais consister à répéter automatiquement une séquence potentiellement destructive sans vérifier l'état obtenu.


# PARTIE 12 — COMPRENDRE L'IDEMPOTENCE

## 38. Définition

Une opération est idempotente lorsqu'une répétition dans les mêmes conditions n'entraîne pas de changement supplémentaire après que l'état visé a été atteint.

Exemple conceptuel :

Un système doit s'assurer qu'un VLAN existe.

Si le programme vérifie d'abord son état et ne le crée que lorsqu'il manque, les exécutions suivantes peuvent ne produire aucun changement supplémentaire.

À l'inverse, une action qui ajoute systématiquement une entrée ou qui effectue une opération à chaque exécution peut avoir des effets cumulatifs.

L'idempotence dépend de la définition exacte de l'opération.

## 39. Schéma — opération idempotente

```text
ÉTAT INITIAL
VLAN 10 absent
        |
        v
Exécution du traitement
        |
        v
VLAN 10 créé
        |
        v
Deuxième exécution
        |
        v
Le programme constate que VLAN 10 existe
        |
        v
Aucun changement supplémentaire
```

## 40. Pourquoi l'idempotence ne suffit-elle pas ?

Même une opération idempotente peut être appliquée au mauvais équipement ou à la mauvaise valeur.

Une opération qui rend un paramètre identique à l'état attendu peut encore interrompre un service si la valeur attendue est erronée.

L'idempotence réduit certains risques de répétition, mais elle ne remplace ni les contrôles de périmètre, ni les tests, ni l'approbation.


# PARTIE 13 — UTILISER NAPALM POUR PRÉPARER DES CHANGEMENTS

## 41. Le principe d'une configuration candidate

Certains outils permettent de préparer une configuration candidate, de comparer les changements et de les appliquer après validation.

NAPALM expose notamment des méthodes de préparation et de comparaison de configurations. Les fonctions disponibles dépendent du pilote et de la plateforme.

Le principe général est le suivant :

```text
CONFIGURATION ACTUELLE
        |
        v
Préparer une configuration candidate
        |
        v
Comparer candidate et état actuel
        |
        v
Examiner le résultat
        |
        +--------------------------+
        |                          |
        v                          v
Changement rejeté            Changement approuvé
        |                          |
        v                          v
Abandonner la candidate      Appliquer selon le pilote
                                   |
                                   v
                          Vérifier le résultat
                                   |
                                   v
                          Confirmer ou reprendre
```

La notion de candidate ne garantit pas que tous les pilotes possèdent les mêmes capacités de validation ou de retour arrière.

Il faut vérifier les fonctionnalités et les limites de la plateforme avant toute utilisation opérationnelle.

## 42. Exemple de préparation d'une candidate

Le code suivant est un exemple pédagogique illustrant la séquence générale. Il ne constitue pas un outil de déploiement universel et ne doit pas être utilisé directement en production sans adaptation, essais et validation du pilote.

```python
def prepare_candidate(device, configuration):
    """
    Exemple conceptuel de préparation d'une configuration candidate.

    La connexion, le pilote et la validation des droits
    doivent être adaptés à la plateforme réelle.
    """

    device.open()

    try:
        device.load_merge_candidate(
            config=configuration
        )

        difference = device.compare_config()

        print("Différences proposées :")
        print(difference)

        # Le cours expert commence en mode plan.
        # Aucune validation ne doit être assimilée
        # automatiquement à une autorisation de commit.

        return {
            "candidate_prepared": True,
            "difference": difference,
            "committed": False,
        }

    finally:
        device.close()
```

Ce code illustre la préparation et la comparaison, mais ne constitue pas un déploiement complet.

Une application réelle doit notamment traiter les exceptions, abandonner proprement une candidate lorsqu'elle n'est pas retenue et vérifier si la plateforme prend en charge toutes les opérations nécessaires.

## 43. Commit confirmé et retour arrière

Certains pilotes et systèmes prennent en charge un mécanisme de confirmation de commit avec expiration. Le principe est de permettre un retour à l'état précédent si le changement n'est pas confirmé dans le délai prévu.

Ce mécanisme n'est pas universel.

Avant de le retenir, il faut vérifier :

- La prise en charge effective par le pilote.
- Le comportement en cas de perte de connexion.
- Le délai de retour arrière.
- La persistance de l'état précédent.
- Le comportement si l'équipement redémarre.
- La disponibilité d'une procédure de reprise indépendante.

Une implémentation qui appelle simplement une méthode de commit ne prouve pas qu'un retour arrière automatique existe.

Le code opérationnel doit se conformer aux capacités documentées du pilote utilisé.

## 44. Séquence de déploiement à retenir

```text
1. Valider le plan
        |
        v
2. Vérifier les cibles
        |
        v
3. Vérifier la sauvegarde
        |
        v
4. Préparer la candidate
        |
        v
5. Calculer la différence
        |
        v
6. Faire approuver le changement
        |
        v
7. Vérifier les conditions de déploiement
        |
        v
8. Appliquer avec le mécanisme de sécurité approprié
        |
        v
9. Collecter le nouvel état
        |
        v
10. Vérifier la conformité
        |
        +------------------------+
        |                        |
        v                        v
   Conforme                 Non conforme
        |                        |
        v                        v
Confirmer et documenter   Arrêter et appliquer
                          la procédure de reprise
```

La séquence est générale. Les opérations précises doivent être adaptées au système et au pilote.


# PARTIE 14 — VALIDATION APRÈS CHANGEMENT

## 45. Pourquoi vérifier après le déploiement ?

Une opération peut s'exécuter sans erreur tout en ne produisant pas le résultat attendu.

Le changement peut être appliqué partiellement, être interprété différemment par l'équipement ou avoir un effet sur d'autres composants.

Une validation après changement doit donc examiner l'état réel.

Elle peut comprendre :

- La présence des propriétés attendues.
- L'état des interfaces concernées.
- La disponibilité des services.
- La cohérence de la configuration.
- Les tests de connectivité prévus.
- La conformité globale après le changement.

Les contrôles doivent correspondre au risque du changement.

## 46. Schéma — validation avant et après

```text
                AVANT CHANGEMENT
                       |
                       v
              Collecte de référence
                       |
                       v
              Vérification initiale
                       |
                       v
              Sauvegarde contrôlée
                       |
                       v
              Approbation et plan
                       |
                       v
                CHANGEMENT
                       |
                       v
                APRÈS CHANGEMENT
                       |
                       v
                Nouvelle collecte
                       |
                       v
              Contrôle de conformité
                       |
              +--------+--------+
              |                 |
              v                 v
       Résultat conforme   Écart détecté
              |                 |
              v                 v
        Clôture contrôlée   Arrêt, analyse
                            et reprise prévue
```

## 47. Ne pas se limiter au statut de commande

La réussite technique d'une commande et la réussite du changement ne sont pas équivalentes.

Par exemple, une commande peut être acceptée par l'équipement alors que le service attendu ne fonctionne plus.

Une validation experte doit combiner plusieurs formes de preuve lorsque cela est pertinent :

- État de configuration.
- État opérationnel.
- Tests de connectivité.
- Résultats d'applications ou de services.
- Journaux et événements.
- Contrôles indépendants.

Le niveau de vérification dépend du changement et de son impact potentiel.


# PARTIE 15 — ORGANISER LES DONNÉES DE DÉPLOIEMENT

## 48. Structure d'un rapport de déploiement

Un rapport de déploiement doit permettre de reconstruire le déroulement de l'opération.

Il devrait notamment préciser :

- L'identifiant du changement.
- La version du code.
- La version des règles.
- Les cibles prévues.
- Les cibles réellement traitées.
- Les sauvegardes utilisées.
- Les contrôles préalables.
- Le statut de chaque étape.
- Les contrôles après changement.
- Les échecs et décisions prises.
- La conclusion finale.

### Exemple de structure

```json
{
  "change_id": "CHG-DEMO-001",
  "mode": "plan_only",
  "status": "not_deployed",
  "targets": [
    {
      "device": "SW1",
      "status": "not_deployed",
      "reason": "Mode plan uniquement"
    }
  ],
  "checks": {
    "inventory": "not_run",
    "backup": "not_run",
    "preconditions": "not_run",
    "post_change_compliance": "not_run"
  }
}
```

Il s'agit d'un exemple fictif.

Il distingue explicitement une opération non exécutée d'une opération réussie. Cette distinction évite de présenter des tests qui n'ont pas eu lieu comme s'ils étaient concluants.

## 49. Statuts recommandés

Un système de rapport peut employer les statuts suivants :

| Statut | Signification |
|---|---|
| `passed` | Le contrôle a été exécuté et a réussi |
| `failed` | Le contrôle a été exécuté et a échoué |
| `unknown` | Les informations disponibles ne permettent pas de conclure |
| `not_run` | Le contrôle n'a pas été exécuté |
| `skipped` | Le contrôle a été ignoré selon une règle explicite |
| `blocked` | Une condition empêche la poursuite |
| `rolled_back` | Une procédure de retour arrière a été exécutée et son statut doit être confirmé |

Ces valeurs doivent être utilisées de manière cohérente dans les rapports.

`rolled_back` ne doit pas être interprété comme une preuve que le réseau est revenu à son état initial. Le résultat réel doit être vérifié.


# PARTIE 16 — INTRODUIRE CI/CD

## 50. Qu'est-ce que CI/CD ?

CI/CD désigne un ensemble de pratiques visant à automatiser les étapes de construction, de test, de validation et, selon la politique, de déploiement.

Dans un projet d'automatisation réseau, l'intégration continue peut vérifier :

- La syntaxe du code.
- Les règles de qualité.
- Le fonctionnement des tests unitaires.
- La validité des fichiers JSON.
- La cohérence des changements.
- L'absence de certaines erreurs connues.

Le déploiement continu ou la livraison contrôlée peut ensuite intégrer des étapes d'approbation et des gardes adaptés à l'environnement.

**CI/CD ne signifie pas que chaque modification de code doit être envoyée automatiquement sur le réseau de production.**

## 51. Architecture d'une chaîne CI/CD réseau

```text
              MODIFICATION DU CODE
                       |
                       v
                  COMMIT GIT
                       |
                       v
                ANALYSE DU CODE
                       |
                       v
                  TESTS UNITAIRES
                       |
                       v
             VALIDATION DES DONNÉES
                       |
                       v
              TESTS D'INTÉGRATION
                       |
                       v
                 REVUE DU CODE
                       |
                       v
               PLAN DE CHANGEMENT
                       |
                       v
              APPROBATION EXPLICITE
                       |
                       v
                 PRÉCONDITIONS
                       |
                       v
               DÉPLOIEMENT CONTRÔLÉ
                       |
                       v
                TESTS POST-DÉPLOIEMENT
                       |
              +--------+--------+
              |                 |
              v                 v
           Succès              Échec
              |                 |
              v                 v
        Rapport final       Arrêt et procédure
        et traçabilité      de reprise adaptée
```

Une chaîne bien conçue doit aussi gérer les secrets, les permissions, les versions des dépendances et les restrictions propres à chaque environnement.


# PARTIE 17 — VERSIONNER LE PROJET AVEC GIT

## 52. Pourquoi utiliser Git ?

Git permet de suivre les modifications du code et des fichiers versionnés.

Il facilite :

- L'historique du projet.
- La revue des changements.
- La comparaison des versions.
- La collaboration.
- La préparation des versions approuvées.
- La possibilité d'identifier l'origine d'une modification.

Dans un projet d'automatisation, il est important de versionner les règles et les scripts de manière contrôlée.

Les sauvegardes de production, les secrets et les données sensibles ne doivent pas être ajoutés automatiquement au dépôt.

## 53. Exemple d'organisation des versions

```text
VERSION 1
Inventaire et validation
        |
        v
VERSION 2
Collecte et sauvegardes
        |
        v
VERSION 3
Moteur de conformité
        |
        v
VERSION 4
Planification des changements
        |
        v
VERSION 5
Tests et validation CI
        |
        v
VERSION 6
Déploiements contrôlés
```

Chaque étape doit conserver un état testable du projet.

Un historique de versions n'est utile que si les changements restent compréhensibles et si les procédures de revue sont réellement utilisées.

## 54. Exemple de cycle de développement

```text
Branche de travail
       |
       v
Écriture du code
       |
       v
Tests locaux
       |
       v
Commit
       |
       v
Pull request
       |
       v
Tests automatiques
       |
       v
Revue par une autre personne
       |
       v
Fusion approuvée
       |
       v
Version préparée
```

Ce cycle permet de détecter les problèmes avant de rendre une modification disponible pour un déploiement.


# PARTIE 18 — CONFIGURER UNE INTÉGRATION CONTINUE

## 55. Préparer les dépendances

Le fichier `requirements.txt` doit contenir les dépendances adaptées au projet.

Pour la partie conformité, le code présenté ici utilise principalement la bibliothèque standard de Python.

Si les tests utilisent `pytest`, ajoutez cette dépendance à l'environnement de développement selon la version choisie et la politique de gestion des dépendances.

Il convient de fixer et de vérifier les versions utilisées dans un projet réel.

## 56. Créer un workflow de tests

Créez le fichier :

`.github/workflows/quality.yml`

```yaml
name: automation-lab-quality

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

permissions:
  contents: read

jobs:
  tests:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout du code
        uses: actions/checkout@v4

      - name: Installer Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Installer les dépendances de test
        run: |
          python -m pip install --upgrade pip
          python -m pip install pytest

      - name: Vérifier les tests de conformité
        run: |
          python -m unittest discover -s tests
```

Ce workflow illustre une intégration continue de base.

Les versions des actions et de Python sont des choix d'exemple à vérifier et à maintenir selon la politique actuelle du projet.

Le workflow exécute les tests du dépôt. Il ne se connecte pas aux équipements et ne déploie aucune configuration.

Si le projet ajoute des tests qui nécessitent Netmiko ou d'autres dépendances, ces bibliothèques devront être installées dans le workflow.

## 57. Pourquoi ne pas mettre directement les identifiants du réseau dans le workflow ?

Un système CI peut exécuter du code à la suite d'un changement de dépôt.

Si ce code accède automatiquement à des identifiants réseau étendus, une erreur ou une modification non approuvée peut avoir un impact important.

La chaîne doit donc utiliser des permissions minimales, des secrets protégés et des restrictions d'environnement adaptées.

Les tests unitaires et les tests de conformité utilisant des données fictives doivent rester indépendants des secrets de production.

## 58. Séparer test et déploiement

```text
WORKFLOW DE TEST
        |
        +---- Analyse du code
        |
        +---- Tests unitaires
        |
        +---- Validation JSON
        |
        +---- Vérification du plan
        |
        v
    Rapport de qualité


WORKFLOW DE DÉPLOIEMENT
        |
        +---- Version approuvée
        |
        +---- Environnement protégé
        |
        +---- Secrets limités
        |
        +---- Préconditions vérifiées
        |
        +---- Approbation
        |
        +---- Déploiement progressif
        |
        v
    Rapport de déploiement
```

La réussite d'un workflow de test ne doit pas déclencher automatiquement un changement de configuration sans les autorisations et les contrôles prévus.


# PARTIE 19 — SÉCURITÉ DE LA CHAÎNE D'AUTOMATISATION

## 59. Le code CI/CD possède des capacités d'action

Une chaîne d'automatisation peut disposer d'accès réseau, d'identifiants et de droits de modification.

Elle doit donc être protégée comme un système d'administration.

Les contrôles importants comprennent :

- La limitation des permissions du dépôt.
- La revue du code.
- La restriction des branches autorisées à déployer.
- La protection des secrets.
- La restriction de l'accès réseau.
- La séparation des environnements.
- La validation des dépendances.
- La traçabilité des exécutions.
- L'approbation des déploiements sensibles.

## 60. Séparer les environnements

Un projet peut distinguer au minimum :

- Le développement.
- Le laboratoire.
- La préproduction.
- La production.

Ces environnements ne doivent pas partager automatiquement les mêmes autorisations.

```text
DÉVELOPPEMENT
      |
      v
Tests sur données fictives
      |
      v
LABORATOIRE
      |
      v
Tests techniques
      |
      v
PRÉPRODUCTION
      |
      v
Validation opérationnelle
      |
      v
PRODUCTION
      |
      v
Déploiement soumis aux contrôles
et autorisations requis
```

Chaque transition doit s'appuyer sur des critères définis et des preuves suffisantes.

## 61. Protéger les secrets

Une chaîne CI/CD ne doit pas afficher les secrets dans ses journaux.

Les droits d'accès aux secrets doivent être limités à la tâche qui en a besoin.

Lorsqu'une plateforme permet de retarder l'accès aux secrets jusqu'à l'approbation d'un environnement protégé, cette fonctionnalité peut aider à séparer les tests des déploiements.

Cela ne dispense pas de contrôler le code exécuté et les autorisations associées aux runners.

Les mécanismes précis dépendent de la plateforme CI/CD et de sa configuration.


# PARTIE 20 — OBSERVABILITÉ ET AUDIT

## 62. Pourquoi l'observabilité est-elle nécessaire ?

Un programme expert doit pouvoir expliquer l'exécution de ses opérations.

Les journaux, les rapports et les mesures permettent de comprendre le déroulement d'un traitement et de détecter des problèmes récurrents.

Les éléments intéressants peuvent comprendre :

- Le nombre d'équipements traités.
- Le taux de réussite.
- Le nombre d'équipements non conformes.
- Le nombre de données inconnues.
- La durée des collectes.
- Les erreurs de communication.
- Les déploiements interrompus.
- Les résultats des validations après changement.

Une mesure doit avoir une définition stable. Par exemple, un équipement non collecté ne doit pas être compté comme conforme.

## 63. Séparer les événements, les mesures et les rapports

```text
EXÉCUTION
    |
    +---- Événements
    |        |
    |        +---- Connexion
    |        +---- Commande
    |        +---- Sauvegarde
    |        +---- Erreur
    |
    +---- Mesures
    |        |
    |        +---- Durée
    |        +---- Réussites
    |        +---- Échecs
    |
    +---- Rapport
             |
             +---- Résultat global
             +---- Écarts
             +---- Preuves
             +---- Décision
```

Les événements aident au diagnostic.

Les mesures permettent de suivre l'évolution du service d'automatisation.

Le rapport relie les résultats à l'objectif et au périmètre de l'opération.

## 64. Conserver une identité de version

Un rapport devrait pouvoir être associé à une version précise du code et des règles.

Il est utile d'enregistrer des informations comme :

- L'identifiant du changement.
- Le commit Git.
- La version du schéma.
- La version des règles.
- La date de collecte.
- La liste des équipements concernés.
- Le statut final.

Ces données aident à expliquer pourquoi deux exécutions peuvent produire des résultats différents.

## 65. Attention aux informations sensibles

L'audit ne justifie pas de conserver toutes les données sans distinction.

Les journaux ne doivent pas contenir les mots de passe, les jetons ou des contenus sensibles qui ne sont pas nécessaires.

Les configurations, les rapports et les historiques doivent être soumis à des contrôles d'accès et à une politique de conservation appropriée.


# PARTIE 21 — INCIDENTS ET RETOUR ARRIÈRE

## 66. Pourquoi une stratégie de reprise est-elle nécessaire ?

Un changement peut échouer même après des tests réussis.

Le problème peut provenir d'une différence de plateforme, d'une condition opérationnelle inattendue, d'une dépendance oubliée ou d'un défaut de la procédure.

La stratégie de reprise doit être préparée avant l'exécution.

Elle doit indiquer :

- Les conditions qui déclenchent l'arrêt.
- Les actions encore autorisées après l'échec.
- Les possibilités de restauration.
- Les responsables à contacter.
- Les vérifications à effectuer.
- Les preuves à conserver.
- Les critères de clôture de l'incident.

## 67. Schéma — procédure en cas d'échec

```text
CHANGEMENT EN COURS
        |
        v
Contrôles après changement
        |
        v
Résultat acceptable ?
       / \
     OUI  NON
      |    |
      v    v
  Clôture  Arrêter les changements
           restants
              |
              v
       Préserver les preuves
              |
              v
       Identifier le périmètre
              |
              v
       Évaluer l'état réel
              |
              v
       La reprise est-elle autorisée
       et techniquement possible ?
              |
          +---+---+
          |       |
          v       v
         OUI      NON
          |        |
          v        v
     Appliquer   Intervention
     la procédure adaptée et contrôlée
          |
          v
    Nouvelle validation
          |
          v
     Rapport final
```

L'échec d'une opération ne justifie pas l'exécution aveugle d'une autre commande.

La reprise doit s'appuyer sur l'état effectivement observé et sur une procédure adaptée au changement.

## 68. Un retour arrière peut-il échouer ?

Oui.

La sauvegarde peut être incomplète, l'ancienne configuration peut dépendre d'un service qui n'existe plus ou la procédure de restauration peut ne pas fonctionner comme prévu.

Le retour arrière doit donc être testé autant que possible, dans un environnement approprié.

Il ne faut jamais affirmer qu'un système est revenu à son état précédent sans effectuer les vérifications nécessaires.

## 69. Définir des critères de clôture

Une opération ne doit pas être considérée comme terminée uniquement parce que le programme s'est arrêté.

La clôture doit vérifier :

- L'état final observé.
- La conformité aux règles pertinentes.
- La santé des services concernés.
- La présence des rapports.
- Le statut des éventuelles reprises.
- La documentation des écarts restants.
- L'identité de la version exécutée.

Un rapport final peut conclure que l'opération a échoué ou demeure partiellement validée. Il vaut mieux une conclusion exacte qu'un statut de réussite artificiel.


# PARTIE 22 — PROJET FINAL INTÉGRÉ

## 70. Mission du projet

Faire évoluer `automation-lab` en un projet capable de :

1. Lire et valider l'inventaire.
2. Collecter des informations dans un laboratoire autorisé.
3. Produire un état observé normalisé.
4. Charger les règles attendues.
5. Évaluer la conformité.
6. Produire un rapport.
7. Préparer un plan de changement sans l'exécuter.
8. Vérifier les préconditions du plan.
9. Exécuter des tests hors ligne.
10. Exposer les étapes de validation dans une chaîne CI.
11. Documenter le processus de reprise.
12. Conserver la traçabilité des exécutions.

La mission consiste d'abord à produire un système de validation fiable. La mise en œuvre de changements réels constitue une étape séparée qui exige des tests spécifiques au matériel et au contexte.

## 71. Architecture du projet final

```text
                INVENTAIRE VALIDÉ
                        |
                        v
                COLLECTE AUTORISÉE
                        |
                        v
                ÉTAT OBSERVÉ JSON
                        |
                        v
                CONTRÔLE DE CONFORMITÉ
                        |
                        v
                  RAPPORT INITIAL
                        |
                        v
                 PLAN DE CHANGEMENT
                        |
                        v
                 REVUE ET APPROBATION
                        |
                        v
                GARDES DE DÉPLOIEMENT
                        |
                        v
               CHANGEMENT AUTORISÉ
                        |
                        v
                 NOUVELLE COLLECTE
                        |
                        v
                VALIDATION FINALE
                        |
                 +------+------+
                 |             |
                 v             v
              Succès          Échec
                 |             |
                 v             v
             Clôture        Arrêt et reprise
             contrôlée      selon la procédure
```

## 72. Étapes de réalisation

### Étape 1 — Stabiliser le code

Vérifiez que le projet possède une structure cohérente et que les dépendances sont documentées.

Conservez les fonctions de collecte et les scripts de sauvegarde du niveau intermédiaire, en identifiant clairement les limites et les dépendances par plateforme.

### Étape 2 — Construire l'état attendu

Créez `expected_state.json` avec des règles contrôlées pour les équipements du laboratoire.

Chaque règle doit être suffisamment précise pour que son résultat puisse être évalué sans ambiguïté.

### Étape 3 — Produire un état observé

Utilisez des données fictives pour tester le moteur de conformité avant de le relier à une collecte réelle.

Ensuite, adaptez le collecteur de laboratoire pour produire exactement le même format normalisé.

### Étape 4 — Tester les règles

Ajoutez des tests pour les situations suivantes :

- Équipement conforme.
- VLAN obligatoire absent.
- Interface absente.
- Propriété incorrecte.
- Collecte manquante.
- Données mal formées.
- Fichier attendu invalide.
- Version de schéma non prise en charge.

### Étape 5 — Préparer les plans

Chaque plan doit disposer d'un identifiant, d'un périmètre explicite, de préconditions, de critères d'acceptation et d'une stratégie de reprise adaptée.

Les premiers plans doivent rester en mode plan uniquement.

### Étape 6 — Préparer la chaîne CI

La chaîne CI doit exécuter les tests indépendants du réseau et vérifier les fichiers versionnés.

Elle ne doit pas nécessiter les secrets de production pour effectuer les tests de base.

### Étape 7 — Tester le cycle complet en laboratoire

Lorsque le projet est stable, un cycle de test autorisé peut comprendre :

1. Une collecte initiale.
2. Une sauvegarde.
3. Une évaluation de conformité.
4. La préparation d'un plan.
5. Une revue du changement.
6. Une application contrôlée dans le laboratoire.
7. Une nouvelle collecte.
8. Une validation de l'état final.
9. La production du rapport.
10. La vérification de la procédure de reprise.

### Étape 8 — Documenter les limites

Le README doit expliquer les plateformes prises en charge, les commandes utilisées, les limites des collecteurs et les préconditions de sécurité.

Une fonctionnalité qui n'a pas été testée sur une plateforme ne doit pas être présentée comme universellement compatible.


# PARTIE 23 — EXERCICES ET CORRECTIONS

## 73. Exercice 1 — État attendu

**Question :** pourquoi faut-il définir un état attendu distinct de l'état observé ?

### Correction

L'état attendu exprime la règle que le réseau doit respecter.

L'état observé décrit ce que la collecte a réellement trouvé.

Si ces deux notions sont mélangées, une modification non autorisée pourrait conduire à modifier la règle pour qu'elle corresponde au mauvais état.

La séparation permet de détecter la dérive et d'établir une décision contrôlée.

## 74. Exercice 2 — Résultat inconnu

**Question :** la collecte d'une interface échoue. Peut-on déclarer l'interface conforme parce qu'aucun problème n'a été détecté ?

### Correction

Non.

L'absence d'un résultat ne prouve pas la conformité.

Le contrôle doit être considéré comme inconnu ou incomplet jusqu'à ce qu'une collecte fiable fournisse les informations nécessaires.

## 75. Exercice 3 — VLAN supplémentaire

**Question :** un équipement possède un VLAN non déclaré dans la liste des VLAN autorisés. Que doit faire le moteur de conformité ?

### Correction

Il doit signaler l'écart selon la politique définie.

Il ne doit pas supprimer automatiquement le VLAN sans évaluer les dépendances, les autorisations et les conséquences.

La remédiation est une action distincte du diagnostic.

## 76. Exercice 4 — Idempotence

**Question :** une opération est idempotente. Est-il possible de l'exécuter sans contrôle sur tous les équipements de production ?

### Correction

Non.

L'idempotence concerne les effets de répétition dans des conditions données. Elle ne garantit pas que la cible est correcte, que les règles attendues sont valides ou que l'opération est autorisée.

Les contrôles de périmètre, les préconditions et les validations restent nécessaires.

## 77. Exercice 5 — Tests

**Question :** tous les tests unitaires réussissent. Peut-on conclure que le déploiement en production est sans risque ?

### Correction

Non.

Les tests unitaires vérifient des fonctions dans des conditions déterminées.

Ils ne prouvent pas que toutes les interactions avec les équipements, les services et les dépendances sont correctes.

Il faut également réaliser les tests d'intégration, les vérifications de préconditions et les validations adaptées au changement.

## 78. Exercice 6 — Retour arrière

**Question :** le programme indique que la restauration a été exécutée. Peut-on conclure que le réseau a retrouvé son état initial ?

### Correction

Non.

Il faut collecter l'état réel, vérifier les propriétés attendues et contrôler les services concernés.

Le statut de l'opération de restauration et l'état final du réseau doivent être documentés séparément.

## 79. Exercice 7 — CI/CD

**Question :** pourquoi les tests automatiques ne doivent-ils pas avoir besoin de secrets de production ?

### Correction

Les tests unitaires et les validations sur données fictives doivent pouvoir fonctionner sans accès aux équipements réels.

Réduire l'accès aux secrets diminue le risque qu'une modification non approuvée ou un code défectueux puisse interagir avec le réseau de production.

Les opérations réellement autorisées à accéder à un environnement protégé doivent disposer uniquement des permissions nécessaires.

## 80. Exercice 8 — Plan de changement

**Question :** le plan de changement indique `approved: true`. Cette valeur suffit-elle à autoriser une modification ?

### Correction

Non.

Une valeur présente dans un fichier n'est qu'une déclaration.

L'autorisation doit être confirmée par un mécanisme approprié et reliée à une identité, une version de plan et un périmètre précis.

Il faut également vérifier les préconditions avant d'exécuter le changement.

## 81. Exercice 9 — Échec partiel

**Question :** une opération réussit sur le premier équipement et échoue sur le deuxième. Quelle doit être la décision ?

### Correction

La décision dépend du plan de déploiement.

Pour une collecte indépendante, le système peut continuer à collecter les autres cibles tout en enregistrant l'échec.

Pour un déploiement de configuration, il peut être nécessaire d'arrêter les cibles suivantes, d'évaluer l'état atteint et de déclencher la procédure de reprise prévue.

La politique doit être définie avant l'exécution.

## 82. Exercice 10 — Projet expert

**Question :** quelles preuves faut-il conserver pour démontrer qu'un changement a été correctement contrôlé ?

### Correction indicative

Il faut conserver les éléments adaptés au type de changement :

- L'identifiant du changement.
- La version du code et des règles.
- L'identité de l'approbation.
- L'inventaire et le périmètre validés.
- Les résultats des préconditions.
- La sauvegarde initiale.
- Le plan et les différences proposés.
- Les résultats de l'exécution.
- Les contrôles après changement.
- Les erreurs et décisions de reprise.
- Le rapport final.

Les données sensibles doivent être protégées et les preuves conservées selon la politique de l'organisation.


# PARTIE 24 — ERREURS FRÉQUENTES AU NIVEAU EXPERT

## 83. Modifier les règles pour supprimer un écart

Un écart ne doit pas être effacé simplement en modifiant la politique attendue pour qu'elle corresponde à l'état observé.

La règle ne doit être changée que si la modification est justifiée, revue et approuvée.

## 84. Traiter une donnée inconnue comme une réussite

Une collecte manquante ou incomplète ne prouve pas qu'un équipement est conforme.

Le moteur doit conserver un statut inconnu et appliquer les critères d'arrêt définis pour le changement.

## 85. Considérer le mode plan comme une garantie

Un plan peut être erroné ou incomplet.

Il doit être contrôlé, comparé à l'inventaire approuvé et examiné avant de devenir une opération autorisée.

## 86. Confondre déploiement réussi et service disponible

Une commande peut être acceptée sans que le service réseau fonctionne correctement.

La validation après changement doit correspondre aux objectifs opérationnels du système.

## 87. Déployer partout dès le premier essai

Un premier changement sur toutes les cibles augmente le périmètre d'impact potentiel.

Un déploiement progressif et des critères d'arrêt permettent de réduire ce risque lorsque l'architecture le permet.

## 88. Supposer qu'une restauration fonctionnera

Une sauvegarde existe, mais elle peut être incomplète ou difficile à restaurer.

La procédure de reprise doit être documentée et testée dans des conditions adaptées.

## 89. Donner des droits de production à tous les tests

Les tests hors ligne ne doivent pas disposer d'identifiants de production inutiles.

Il faut séparer les permissions de test, de laboratoire et de déploiement.

## 90. Négliger les preuves

Un statut `success` isolé est insuffisant pour démontrer la qualité d'une opération complexe.

Le rapport doit permettre de comprendre les vérifications réalisées et le résultat réellement observé.


# PARTIE 25 — GLOSSAIRE EXPERT

**État attendu :** représentation des propriétés que le réseau doit respecter selon une politique définie.

**État observé :** données décrivant l'état réellement collecté.

**Conformité :** degré de respect des règles définies.

**Dérive de configuration :** différence entre l'état observé et l'état attendu.

**Normalisation :** transformation des données de différentes sources vers une représentation commune et documentée.

**Faux positif :** problème signalé alors que la situation est acceptable selon la règle applicable.

**Faux négatif :** problème réel qui n'est pas signalé par le contrôle.

**Idempotence :** propriété d'une opération qui, répétée dans les mêmes conditions, ne produit pas de changement supplémentaire lorsque l'état cible est atteint.

**Précondition :** condition qui doit être satisfaite avant qu'une opération soit autorisée.

**Plan de changement :** document décrivant l'objectif, le périmètre, les contrôles, les risques et le traitement des échecs d'une modification.

**Mode plan :** mode qui prépare ou présente une opération sans appliquer le changement réseau.

**Configuration candidate :** configuration préparée pour être examinée avant son application lorsque la plateforme prend en charge ce mécanisme.

**Déploiement progressif :** application d'un changement par étapes avec contrôles entre les étapes.

**Retour arrière :** procédure visant à revenir vers un état précédent après un changement, lorsque cela est techniquement possible.

**CI/CD :** pratiques et mécanismes permettant d'automatiser l'intégration, les tests, la validation et éventuellement le déploiement.

**Test unitaire :** test portant sur une fonction ou une unité de code isolée.

**Test d'intégration :** test vérifiant le fonctionnement de plusieurs composants associés.

**Test de bout en bout :** test couvrant le déroulement d'un processus complet.

**Traçabilité :** capacité à retrouver les événements, les versions, les décisions et les résultats associés à une opération.

**Observabilité :** capacité à comprendre le fonctionnement d'un système à partir des événements, des mesures et des résultats disponibles.


# PARTIE 26 — ÉVALUATION FINALE

## 91. Questions théoriques

L'apprenant doit pouvoir répondre aux questions suivantes sans consulter le cours.

1. Quelle est la différence entre l'état attendu et l'état observé ?
2. Pourquoi faut-il normaliser les données collectées ?
3. Pourquoi un moteur de conformité doit-il distinguer un écart d'une information inconnue ?
4. Comment éviter qu'une collecte incomplète soit déclarée conforme ?
5. Qu'est-ce qu'une dérive de configuration ?
6. Pourquoi la détection d'une dérive ne justifie-t-elle pas automatiquement une correction ?
7. À quoi servent les tests unitaires ?
8. Quelle est la différence entre test unitaire, test d'intégration et test de bout en bout ?
9. Pourquoi définir des préconditions de déploiement ?
10. Quel est l'intérêt du mode plan ?
11. Pourquoi une approbation indépendante peut-elle être importante ?
12. Quelle est la différence entre idempotence et sécurité d'une opération ?
13. Pourquoi déployer progressivement ?
14. Quelles sont les limites du retour arrière ?
15. Pourquoi faut-il vérifier l'état réel après un changement ?
16. Quels éléments doivent être présents dans un rapport de déploiement ?
17. Quel est le rôle de Git dans le projet ?
18. Comment la chaîne CI/CD peut-elle contribuer à la fiabilité ?
19. Pourquoi les secrets doivent-ils être séparés des données de test ?
20. Quelles preuves permettent d'établir qu'une opération a été contrôlée correctement ?

## 92. Mise en pratique finale

Le projet doit démontrer les capacités suivantes :

- Charger et valider un inventaire.
- Produire un état observé normalisé.
- Charger les règles attendues.
- Vérifier la conformité sur des données fictives.
- Signaler les violations et les données inconnues.
- Générer un rapport JSON.
- Tester la conformité avec plusieurs scénarios.
- Préparer un plan de changement sans l'exécuter.
- Contrôler les préconditions du plan.
- Exécuter les tests automatiquement dans une chaîne CI.
- Décrire la procédure de reprise.
- Documenter les limitations des collecteurs et des plateformes.

Les opérations modifiant réellement la configuration exigent une phase de validation indépendante dans un environnement approprié.

## 93. Critères de maîtrise

Le niveau expert est acquis lorsque l'apprenant peut :

- Expliquer l'architecture générale du projet.
- Distinguer les responsabilités du collecteur et du moteur de conformité.
- Construire des règles contrôlables.
- Tester les règles et les erreurs.
- Préparer un changement documenté.
- Vérifier le périmètre et les préconditions.
- Décrire un déploiement progressif.
- Vérifier le résultat après changement.
- Identifier les limites d'une stratégie de retour arrière.
- Organiser une chaîne CI/CD adaptée au risque.
- Maintenir la traçabilité des opérations.
- Expliquer précisément ce qui a été vérifié et ce qui ne l'a pas été.

La maîtrise ne consiste pas à posséder un script capable d'envoyer des commandes. Elle consiste à savoir construire un processus dont le comportement et les limites sont clairement définis.


# PARTIE 27 — RÉFÉRENCES TECHNIQUES

Les documentations officielles suivantes permettent d'approfondir les concepts présentés dans le cours :

- **Ansible — Automatisation réseau :**  
  https://docs.ansible.com/projects/ansible/latest/network/getting_started/

- **Ansible — Particularités de l'automatisation réseau :**  
  https://docs.ansible.com/projects/ansible/latest/network/getting_started/network_differences.html

- **NAPALM — API et gestion des configurations candidates :**  
  https://napalm.readthedocs.io/en/latest/base.html

- **NAPALM — Exemple de préparation et de comparaison d'une configuration :**  
  https://napalm.readthedocs.io/en/stable/tutorials/changing_the_config.html

- **pytest — Premiers tests automatisés :**  
  https://docs.pytest.org/en/stable/getting-started.html

- **pytest — Simulation de fonctions et d'environnements :**  
  https://docs.pytest.org/en/stable/how-to/monkeypatch.html

- **GitHub Actions — Concepts des workflows :**  
  https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows

- **GitHub Actions — Environnements et protections de déploiement :**  
  https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments

Les fonctions disponibles, les versions et les mécanismes de sécurité doivent être vérifiés dans la documentation correspondant aux versions effectivement installées. La compatibilité varie selon les pilotes, les équipements et les politiques de déploiement.


# CONCLUSION GÉNÉRALE

Le niveau expert transforme le projet `automation-lab` en une base pour une automatisation réseau gouvernée.

Au niveau débutant, l'apprenant a appris à structurer et à valider les données.

Au niveau intermédiaire, il a ajouté les connexions, la collecte, les sauvegardes, les comparaisons et la gestion des erreurs.

Au niveau expert, il définit un état attendu, évalue la conformité, teste les règles, prépare les changements et organise leur validation.

Le point essentiel est de distinguer plusieurs opérations qui ne sont pas équivalentes : observer un état, déclarer une différence, évaluer la conformité, décider d'une correction, exécuter un changement et vérifier son résultat.

Une chaîne CI/CD peut contribuer à rendre ces opérations plus reproductibles. Elle ne dispense ni d'une politique de sécurité, ni d'une approbation adaptée, ni des contrôles après changement.

Un processus expert doit aussi savoir s'arrêter. Lorsque les données sont incomplètes, qu'une précondition échoue ou qu'un résultat ne peut pas être vérifié, il doit présenter cette situation clairement au lieu de produire artificiellement un statut de réussite.

**Principe final : observer avec fiabilité, comparer avec une règle connue, préparer avant d'agir, déployer selon un périmètre autorisé, vérifier l'état réel et documenter les résultats comme les échecs.**