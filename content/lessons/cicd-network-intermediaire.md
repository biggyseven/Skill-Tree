
# CI/CD et Git pour le réseau — Niveau intermédiaire

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** maîtriser les dépôts, commits, branches, diff et pipelines simples présentés dans le cours débutant.  
> **Objectif :** construire une chaîne CI plus fiable, tester les données et les configurations réseau, et préparer des déploiements gouvernés sans exposer prématurément les équipements de production.


## Sommaire

1. Contexte et objectifs
2. Architecture du dépôt réseau
3. Gestion des branches et qualité des changements
4. Validation des inventaires YAML
5. Tests automatisés et analyse statique
6. Pipeline CI intermédiaire
7. Production de rapports et d'artefacts
8. Préparation d'un déploiement contrôlé
9. Sécurité de la chaîne CI/CD
10. Vérification avant et après changement
11. Atelier pratique complet
12. Dépannage
13. Évaluation corrigée
14. Préparation du niveau expert


# 1. Contexte et objectifs

## 1.1 De la gestion des fichiers à la validation automatisée

Au niveau débutant, nous avons appris à enregistrer les configurations dans Git, à travailler sur une branche et à lancer des contrôles élémentaires.

À ce stade, une CI peut vérifier qu'un fichier existe. Mais cela ne permet pas de savoir si l'inventaire contient tous les champs nécessaires, si les noms sont cohérents ou si des paramètres interdits sont présents.

Le niveau intermédiaire introduit une approche plus rigoureuse :

- définir des règles de données explicites ;
- automatiser les validations ;
- exécuter des tests reproductibles ;
- conserver les rapports des contrôles ;
- bloquer la fusion lorsqu'un contrôle obligatoire échoue ;
- séparer les tests de la préparation du déploiement ;
- organiser les permissions et les approbations.

Le but n'est pas simplement d'avoir un pipeline vert. Le but est de pouvoir expliquer précisément **ce qui a été testé, ce que le résultat prouve et ce qu'il ne prouve pas**.

## 1.2 Objectifs pédagogiques

À la fin du cours, vous serez capable de :

1. structurer un dépôt réseau maintenable ;
2. définir des règles de validation pour un inventaire ;
3. écrire un programme de validation en Python ;
4. utiliser des tests automatiques pour détecter des incohérences ;
5. déclencher une CI sur les pull requests et sur la branche principale ;
6. enregistrer et consulter un rapport de test ;
7. distinguer validation statique, test en laboratoire et vérification opérationnelle ;
8. préparer des étapes d'approbation avant un déploiement ;
9. limiter les permissions et l'exposition des secrets ;
10. documenter des critères d'acceptation et une procédure de retour arrière.

## 1.3 Prérequis pratiques

Git doit être installé et fonctionnel. Vous devez aussi disposer de Python 3.11 ou d'une version compatible avec les dépendances choisies.

Dans un terminal, vérifiez les outils :

```bash
git --version
python --version
```

Sur certains systèmes, la commande Python est :

```bash
python3 --version
```

Tous les exercices de validation ci-dessous peuvent être exécutés localement avant d'être intégrés à la CI.


# 2. Architecture du dépôt réseau

Une structure claire aide à séparer les données, les programmes et les résultats des tests.

```text
cicd-network/
├── .github/
│   └── workflows/
│       └── validate.yml
├── configs/
│   └── reference/
│       └── SW-ACCESS-01.cfg
├── inventory/
│   └── devices.yml
├── schemas/
│   └── inventory.schema.json
├── src/
│   └── validate_inventory.py
├── tests/
│   └── test_inventory.py
├── reports/
├── requirements.txt
├── .gitignore
└── README.md
```

Les dossiers `reports/` et `configs/` ne doivent pas être remplis indistinctement de fichiers temporaires. Les rapports produits localement et les véritables rapports de pipeline peuvent avoir des politiques de conservation différentes.

## 2.1 Rôle des principaux dossiers

| Élément | Fonction |
|---|---|
| `configs/` | Configurations de référence ou modèles approuvés |
| `inventory/` | Inventaire structuré des équipements |
| `schemas/` | Structure et contraintes des données attendues |
| `src/` | Programmes de validation |
| `tests/` | Tests automatiques des validateurs |
| `.github/workflows/` | Définition des workflows GitHub Actions |
| `reports/` | Rapports de contrôle générés |
| `requirements.txt` | Dépendances Python nécessaires |

L'inventaire ne doit pas devenir un endroit où l'on stocke les mots de passe. Il décrit les équipements et leurs propriétés non secrètes ; les identifiants, lorsqu'ils sont nécessaires, relèvent d'un système de secrets.

## 2.2 Exemple d'inventaire

Dans `inventory/devices.yml` :

```yaml
devices:
  - name: SW-ACCESS-01
    platform: cisco_ios
    role: access
    management_address: 192.0.2.11
    site: DOUALA-LAB

  - name: RTR-EDGE-01
    platform: cisco_ios
    role: edge
    management_address: 192.0.2.1
    site: DOUALA-LAB
```

Les adresses `192.0.2.0/24` sont réservées à la documentation. Elles servent ici d'exemples ; remplacez-les par les valeurs de votre laboratoire si vous exécutez des contrôles de connectivité.


# 3. Gestion des branches et qualité des changements

## 3.1 Un workflow Git reproductible

Une modification suit généralement les étapes suivantes :

1. créer une branche ;
2. modifier les fichiers ;
3. examiner le diff ;
4. exécuter les validations locales ;
5. commiter et publier la branche ;
6. ouvrir une pull request ;
7. examiner le résultat de la CI ;
8. demander une revue ;
9. fusionner lorsque les conditions requises sont remplies.

Commandes principales :

```bash
git switch -c feature/validation-inventaire
git status
git diff
```

Après la modification :

```bash
git add inventory/devices.yml src/ tests/
git diff --cached
git commit -m "Ajoute la validation de l'inventaire réseau"
git push -u origin feature/validation-inventaire
```

La dernière commande suppose qu'un dépôt distant nommé `origin` est configuré.

## 3.2 Schéma du cycle de validation

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="380" viewBox="0 0 1000 380" role="img" aria-labelledby="mid-git-title mid-git-desc">
  <title id="mid-git-title">Workflow Git et CI intermédiaire</title>
  <desc id="mid-git-desc">Une branche de travail passe par les tests locaux, une pull request, la CI et la revue, puis la fusion. Si les contrôles échouent, le changement revient en correction. Les animations concernent uniquement les tirets des lignes orientées.</desc>
  <defs>
    <marker id="mid-git-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .mg-box{fill:#16263b;stroke:#60a5fa;stroke-width:2}
      .mg-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .mg-fail{fill:#3b201f;stroke:#fb7185;stroke-width:2}
      .mg-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .mg-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .mg-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#mid-git-arrow);animation:mg-dash 1.8s linear infinite}
      .mg-error{fill:none;stroke:#fb7185;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#mid-git-arrow);animation:mg-dash 1.8s linear infinite}
      @keyframes mg-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="378" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">UN CHANGEMENT N'EST INTÉGRÉ QU'APRÈS LES CONTRÔLES</text>
  <rect class="mg-box" x="25" y="75" width="170" height="75" rx="10"/>
  <text class="mg-title" x="110" y="104" text-anchor="middle">Branche</text>
  <text class="mg-text" x="110" y="126" text-anchor="middle">Code et données</text>
  <rect class="mg-box" x="225" y="75" width="170" height="75" rx="10"/>
  <text class="mg-title" x="310" y="104" text-anchor="middle">Tests locaux</text>
  <text class="mg-text" x="310" y="126" text-anchor="middle">Vérifier avant push</text>
  <rect class="mg-box" x="425" y="75" width="170" height="75" rx="10"/>
  <text class="mg-title" x="510" y="104" text-anchor="middle">Pull request</text>
  <text class="mg-text" x="510" y="126" text-anchor="middle">Diff proposé</text>
  <rect class="mg-box" x="625" y="75" width="170" height="75" rx="10"/>
  <text class="mg-title" x="710" y="104" text-anchor="middle">CI automatique</text>
  <text class="mg-text" x="710" y="126" text-anchor="middle">Validation et tests</text>
  <rect class="mg-ok" x="825" y="75" width="150" height="75" rx="10"/>
  <text class="mg-title" x="900" y="104" text-anchor="middle">Fusion</text>
  <text class="mg-text" x="900" y="126" text-anchor="middle">Après approbation</text>
  <path class="mg-flow" d="M195 112 H218"/>
  <path class="mg-flow" d="M395 112 H418"/>
  <path class="mg-flow" d="M595 112 H618"/>
  <path class="mg-flow" d="M795 112 H818"/>
  <rect class="mg-fail" x="260" y="235" width="480" height="65" rx="10"/>
  <text class="mg-title" x="500" y="261" text-anchor="middle">Échec d'un contrôle obligatoire</text>
  <text class="mg-text" x="500" y="282" text-anchor="middle">Corriger, relancer les tests et examiner le nouveau diff</text>
  <path class="mg-error" d="M710 150 V200 H650 V228"/>
  <path class="mg-error" d="M260 268 H120 V190 H110 V157"/>
  <text class="mg-text" x="500" y="340" text-anchor="middle">La CI fournit une décision technique selon les règles configurées.</text>
  <text class="mg-text" x="500" y="359" text-anchor="middle">La revue et les protections du dépôt déterminent si la fusion est autorisée.</text>
</svg>

## 3.3 Protéger la branche principale

Configurez la protection de `main` sur votre plateforme pour exiger, selon les capacités disponibles :

- des contrôles CI réussis ;
- une revue par une personne autorisée ;
- des conversations de revue résolues ;
- l'absence de fusion directe non autorisée.

La configuration se fait dans les paramètres du dépôt. La syntaxe YAML de la CI ne suffit pas à imposer toutes ces protections.

## 3.4 Règles de qualité

Un changement doit avoir une intention identifiable. Évitez les commits qui mêlent le renommage de dizaines de fichiers, une modification de VLAN et une refonte de script sans justification.

Un petit changement est plus facile à relire, tester et annuler.


# 4. Validation des inventaires YAML

Une CI intermédiaire doit examiner les données, et pas uniquement vérifier que le fichier existe.

Nous allons utiliser Python et PyYAML pour lire le YAML, vérifier les champs obligatoires, contrôler les noms d'équipements et vérifier la forme des adresses IP.

## 4.1 Installer les dépendances

Dans `requirements.txt` :

```text
PyYAML==6.0.3
```

Installez la dépendance dans un environnement virtuel :

```bash
python -m venv .venv
```

Activation sous Linux ou macOS :

```bash
source .venv/bin/activate
```

Activation sous PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Puis :

```bash
python -m pip install -r requirements.txt
```

Le numéro de version est fixé pour rendre l'exercice reproductible. Dans un environnement professionnel, vérifiez la compatibilité, tenez les dépendances à jour et utilisez la politique de versions de votre organisation.

## 4.2 Écrire le validateur

Créez `src/validate_inventory.py` :

```python
#!/usr/bin/env python3
"""Validation élémentaire d'un inventaire d'équipements réseau."""

from __future__ import annotations

import ipaddress
import sys
from pathlib import Path
from typing import Any

import yaml


ALLOWED_ROLES = {"access", "distribution", "core", "edge", "firewall"}
REQUIRED_FIELDS = {
    "name",
    "platform",
    "role",
    "management_address",
    "site",
}


def validate_inventory(path: Path) -> list[str]:
    errors: list[str] = []

    try:
        with path.open("r", encoding="utf-8") as stream:
            data: Any = yaml.safe_load(stream)
    except FileNotFoundError:
        return [f"Fichier introuvable : {path}"]
    except yaml.YAMLError as exc:
        return [f"YAML invalide : {exc}"]
    except OSError as exc:
        return [f"Impossible de lire le fichier : {exc}"]

    if not isinstance(data, dict):
        return ["La racine du document doit être un objet YAML."]

    devices = data.get("devices")
    if not isinstance(devices, list) or not devices:
        return ["Le champ 'devices' doit être une liste non vide."]

    seen_names: set[str] = set()

    for index, device in enumerate(devices, start=1):
        prefix = f"Équipement #{index}"

        if not isinstance(device, dict):
            errors.append(f"{prefix} : chaque élément doit être un objet.")
            continue

        missing = REQUIRED_FIELDS - device.keys()
        if missing:
            errors.append(
                f"{prefix} : champs manquants : {', '.join(sorted(missing))}"
            )
            continue

        name = device["name"]
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix} : le nom doit être une chaîne non vide.")
        elif name in seen_names:
            errors.append(f"{prefix} : nom dupliqué : {name}")
        else:
            seen_names.add(name)

        platform = device["platform"]
        if not isinstance(platform, str) or not platform.strip():
            errors.append(f"{prefix} : plateforme absente ou invalide.")

        role = device["role"]
        if role not in ALLOWED_ROLES:
            errors.append(
                f"{prefix} : rôle {role!r} non autorisé. "
                f"Valeurs acceptées : {', '.join(sorted(ALLOWED_ROLES))}"
            )

        site = device["site"]
        if not isinstance(site, str) or not site.strip():
            errors.append(f"{prefix} : le site doit être renseigné.")

        address = device["management_address"]
        if not isinstance(address, str):
            errors.append(f"{prefix} : l'adresse de gestion doit être une chaîne.")
        else:
            try:
                ipaddress.ip_address(address)
            except ValueError:
                errors.append(
                    f"{prefix} : adresse IP invalide : {address!r}"
                )

    return errors


def main() -> int:
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path("inventory/devices.yml")
    )

    errors = validate_inventory(path)

    if errors:
        print("ÉCHEC — inventaire invalide")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"SUCCÈS — inventaire valide : {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 4.3 Comprendre le validateur

Le programme effectue plusieurs contrôles :

- le fichier existe et peut être lu ;
- le contenu est du YAML valide ;
- le champ `devices` est une liste non vide ;
- chaque équipement est un objet ;
- les champs requis sont présents ;
- les noms d'équipements ne sont pas dupliqués ;
- le rôle appartient à un ensemble autorisé ;
- les adresses peuvent être analysées comme des adresses IP.

Le programme renvoie un code de sortie non nul lorsqu'il détecte une erreur. C'est important : la CI doit savoir qu'elle doit échouer, au lieu de simplement afficher un message d'avertissement.

Ce validateur ne prouve pas que l'adresse IP est joignable, qu'elle correspond à l'équipement attendu ou que la topologie est correcte. Ces vérifications nécessitent d'autres règles et éventuellement des tests distincts.

## 4.4 Exécuter le validateur

```bash
python src/validate_inventory.py
```

Résultat attendu pour l'inventaire fourni :

```text
SUCCÈS — inventaire valide : inventory/devices.yml
```

Pour tester volontairement un échec, dupliquez le nom d'un équipement ou modifiez une adresse IP en une chaîne invalide. Le programme doit alors afficher les problèmes et terminer avec un code d'échec.


# 5. Tests automatisés et analyse statique

Un validateur lui-même doit être testé. Sinon, il est possible qu'une erreur dans son code laisse passer un inventaire incorrect ou rejette des données valides.

## 5.1 Pourquoi tester le validateur ?

Il faut vérifier le comportement en cas de données valides, mais aussi face à des erreurs courantes :

- YAML mal formé ;
- champs obligatoires absents ;
- noms dupliqués ;
- rôles inconnus ;
- adresses IP invalides ;
- fichier introuvable.

Ces tests évaluent les règles du programme sans se connecter aux équipements réseau.

## 5.2 Ajouter des tests avec `unittest`

Créez `tests/test_inventory.py` :

```python
import tempfile
import unittest
from pathlib import Path

from src.validate_inventory import validate_inventory


VALID_YAML = """
devices:
  - name: SW-ACCESS-01
    platform: cisco_ios
    role: access
    management_address: 192.0.2.11
    site: DOUALA-LAB
"""


class InventoryValidationTests(unittest.TestCase):
    def write_temp_file(self, content: str) -> Path:
        temp = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".yml",
            delete=False,
        )
        with temp:
            temp.write(content)
        return Path(temp.name)

    def test_valid_inventory(self) -> None:
        path = self.write_temp_file(VALID_YAML)
        try:
            self.assertEqual(validate_inventory(path), [])
        finally:
            path.unlink(missing_ok=True)

    def test_invalid_ip_is_rejected(self) -> None:
        content = VALID_YAML.replace(
            "192.0.2.11", "not-an-ip"
        )
        path = self.write_temp_file(content)
        try:
            errors = validate_inventory(path)
            self.assertTrue(any("adresse IP invalide" in e for e in errors))
        finally:
            path.unlink(missing_ok=True)

    def test_duplicate_names_are_rejected(self) -> None:
        duplicate_yaml = VALID_YAML + VALID_YAML.split("devices:\n", 1)[1]
        path = self.write_temp_file(duplicate_yaml)
        try:
            errors = validate_inventory(path)
            self.assertTrue(any("nom dupliqué" in e for e in errors))
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
```

Pour que Python importe les modules depuis les dossiers, créez aussi un fichier vide `src/__init__.py`.

La construction du cas de test des noms dupliqués est volontairement simple et pédagogique. Dans une base de tests plus importante, préférez une fonction dédiée qui construit des inventaires de test lisibles plutôt que de manipuler des chaînes YAML à l'aveugle.

Lancez les tests :

```bash
python -m unittest discover -s tests -v
```

Les tests doivent tous réussir. Si l'un d'eux échoue, examinez le détail affiché avant de modifier les règles du validateur.

## 5.3 Différence entre un test unitaire et un test réseau

Un test unitaire vérifie une petite unité de code ou de logique de validation.

Un test réseau peut vérifier un comportement plus large, par exemple une connectivité entre deux réseaux dans un laboratoire virtuel. Il doit définir un environnement, une topologie, des préconditions et des résultats attendus.

Un test unitaire réussi ne démontre pas le bon fonctionnement de toute l'infrastructure.


# 6. Pipeline CI intermédiaire

Nous allons maintenant automatiser :

1. l'installation de Python ;
2. l'installation des dépendances ;
3. la validation de l'inventaire ;
4. l'exécution des tests ;
5. la publication d'un rapport.

## 6.1 Préparer le rapport

Créez le dossier `reports/`. Le workflow produira un rapport texte indiquant que les contrôles de base ont été exécutés. Le rapport peut être conservé comme artefact du pipeline ; il ne doit pas contenir de secrets ni de données sensibles inutiles.

Ajoutez `reports/local/` et les fichiers temporaires au `.gitignore` si vous ne souhaitez pas versionner les sorties locales :

```gitignore
.venv/
__pycache__/
*.pyc
reports/local/
.env
.env.*
*.key
*.pem
secrets/
credentials/
```

## 6.2 Créer le workflow

Créez `.github/workflows/validate.yml` :

```yaml
name: Network repository validation

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Validate inventory
        run: |
          python src/validate_inventory.py

      - name: Run unit tests
        run: |
          python -m unittest discover -s tests -v

      - name: Create validation report
        if: always()
        run: |
          mkdir -p reports
          {
            echo "Validation du dépôt réseau"
            echo "Commit : $GITHUB_SHA"
            echo "Workflow : $GITHUB_WORKFLOW"
            echo "Run : $GITHUB_RUN_ID"
            echo "Consulter les étapes du job pour le détail des tests."
          } > reports/validation-report.txt

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: network-validation-report
          path: reports/validation-report.txt
          if-no-files-found: error
          retention-days: 14
```

Les références de versions des actions sont des choix de démonstration à vérifier et à maintenir selon les politiques de sécurité du dépôt. Les versions de `actions/checkout` et `actions/setup-python` évoluent ; consultez leurs dépôts officiels avant un usage professionnel.

Références :

- https://github.com/actions/checkout/releases
- https://github.com/actions/setup-python/releases
- https://github.com/actions/upload-artifact

## 6.3 Comment interpréter le résultat ?

Le job est réussi uniquement si l'inventaire et les tests passent. Un échec de validation doit empêcher de considérer le changement comme accepté.

L'étape de génération de rapport utilise `if: always()` afin de produire un rapport même si un contrôle précédent échoue, lorsque les conditions d'exécution le permettent. Le rapport donne des informations d'identification du run, mais les détails des échecs restent visibles dans les étapes correspondantes.

Le rapport n'est pas une preuve de validation fonctionnelle de l'équipement. Il faut lire les résultats réels des tests.

## 6.4 Schéma du pipeline intermédiaire

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390" role="img" aria-labelledby="mid-pipe-title mid-pipe-desc">
  <title id="mid-pipe-title">Pipeline CI intermédiaire</title>
  <desc id="mid-pipe-desc">Le dépôt passe au contrôle des données, puis aux tests unitaires et à la génération d'un rapport. La revue décide ensuite si la fusion est autorisée. Un échec renvoie la modification à l'étape de correction. Les flèches animées utilisent des tirets et aucune boule mobile.</desc>
  <defs>
    <marker id="mid-pipe-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .mp-box{fill:#172033;stroke:#38bdf8;stroke-width:2}
      .mp-approved{fill:#123126;stroke:#4ade80;stroke-width:2}
      .mp-error{fill:#3b201f;stroke:#fb7185;stroke-width:2}
      .mp-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .mp-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .mp-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#mid-pipe-arrow);animation:mp-dash 1.8s linear infinite}
      .mp-retry{fill:none;stroke:#fb7185;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#mid-pipe-arrow);animation:mp-dash 1.8s linear infinite}
      @keyframes mp-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="33" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DES DONNÉES AUX RÉSULTATS MESURABLES</text>
  <rect class="mp-box" x="25" y="72" width="170" height="78" rx="10"/>
  <text class="mp-title" x="110" y="100" text-anchor="middle">1. Dépôt Git</text>
  <text class="mp-text" x="110" y="124" text-anchor="middle">Pull request</text>
  <rect class="mp-box" x="225" y="72" width="170" height="78" rx="10"/>
  <text class="mp-title" x="310" y="100" text-anchor="middle">2. YAML</text>
  <text class="mp-text" x="310" y="124" text-anchor="middle">Structure et champs</text>
  <rect class="mp-box" x="425" y="72" width="170" height="78" rx="10"/>
  <text class="mp-title" x="510" y="100" text-anchor="middle">3. Tests</text>
  <text class="mp-text" x="510" y="124" text-anchor="middle">Règles et cas négatifs</text>
  <rect class="mp-box" x="625" y="72" width="170" height="78" rx="10"/>
  <text class="mp-title" x="710" y="100" text-anchor="middle">4. Rapport</text>
  <text class="mp-text" x="710" y="124" text-anchor="middle">Artefact de run</text>
  <rect class="mp-approved" x="825" y="72" width="150" height="78" rx="10"/>
  <text class="mp-title" x="900" y="100" text-anchor="middle">5. Revue</text>
  <text class="mp-text" x="900" y="124" text-anchor="middle">Décision de fusion</text>
  <path class="mp-flow" d="M195 111 H218"/>
  <path class="mp-flow" d="M395 111 H418"/>
  <path class="mp-flow" d="M595 111 H618"/>
  <path class="mp-flow" d="M795 111 H818"/>
  <rect class="mp-error" x="265" y="232" width="470" height="64" rx="10"/>
  <text class="mp-title" x="500" y="258" text-anchor="middle">Contrôle en échec</text>
  <text class="mp-text" x="500" y="279" text-anchor="middle">Corriger les données ou le code, puis relancer</text>
  <path class="mp-retry" d="M310 150 V197 H345 V225"/>
  <path class="mp-retry" d="M265 264 H120 V193 H110 V157"/>
  <text class="mp-text" x="500" y="333" text-anchor="middle">Les tests valident les règles implémentées.</text>
  <text class="mp-text" x="500" y="353" text-anchor="middle">Ils ne prouvent pas à eux seuls le comportement en production.</text>
</svg>


# 7. Production de rapports et d'artefacts

## 7.1 Qu'est-ce qu'un artefact ?

Un artefact est un fichier produit par un job et rendu disponible après son exécution, par exemple :

- un rapport de test ;
- un résultat d'analyse ;
- un inventaire rendu ;
- une configuration candidate ;
- un journal d'exécution nettoyé des données sensibles.

Un artefact n'est pas automatiquement digne de confiance parce qu'il a été produit par un pipeline. Il faut connaître son origine, le commit source, la version des outils et les contrôles réellement exécutés.

## 7.2 Que faut-il conserver ?

Pour un changement réseau, il est utile de conserver :

- l'identifiant du commit ;
- la date et le résultat des contrôles ;
- les versions des outils utilisés ;
- les avertissements et erreurs ;
- le rapport de tests ;
- les validations et décisions prévues par le processus.

Ne conservez pas inutilement des mots de passe, des clés privées, des configurations contenant des secrets ou des journaux complets de sessions.

## 7.3 Traçabilité et reproductibilité

Le même commit doit idéalement donner des résultats comparables lorsque les conditions sont identiques. Pour améliorer la reproductibilité :

- fixez les versions des dépendances ;
- consignez la version du validateur ;
- versionnez les règles de validation ;
- séparez les données d'entrée des rapports ;
- évitez les dépendances implicites à la machine locale ;
- documentez les paramètres nécessaires aux tests.


# 8. Préparation d'un déploiement contrôlé

Le niveau intermédiaire ne consiste pas à donner immédiatement au pipeline des identifiants administrateur. Il s'agit de séparer les contrôles de la préparation du déploiement.

## 8.1 Séparer les environnements

Une organisation peut utiliser plusieurs environnements logiques :

| Environnement | Usage |
|---|---|
| Développement | Expérimentation sur les fichiers et validateurs |
| Laboratoire | Test du comportement sur une topologie isolée |
| Préproduction | Vérification sur un environnement représentatif |
| Production | Réseau opérationnel de l'organisation |

Tous les projets ne disposent pas d'un environnement de préproduction. Lorsqu'il manque, cette limite doit être explicitement compensée par des contrôles adaptés et une analyse du risque.

## 8.2 Précontrôles et post-contrôles

Un précontrôle vérifie l'état initial avant un changement. Selon les outils et les permissions, il peut vérifier l'accessibilité, l'identité de l'équipement, l'état des interfaces ou des routes attendues.

Un post-contrôle vérifie si le résultat prévu a été obtenu. Il ne doit pas se limiter à vérifier qu'une commande de configuration a renvoyé une réponse positive.

Exemples de critères :

- l'interface attendue est opérationnelle ;
- le VLAN demandé existe ;
- une route attendue est présente ;
- le service de gestion reste accessible ;
- les tests de connectivité critiques réussissent ;
- aucun indicateur de santé défini n'est passé à un état interdit.

Les contrôles doivent être adaptés à l'équipement, au protocole et au besoin métier. Ils doivent avoir des résultats attendus explicites.

## 8.3 Condition d'arrêt

Le processus doit s'arrêter lorsqu'un critère obligatoire échoue. Un pipeline ne doit pas poursuivre mécaniquement le déploiement sur d'autres équipements après la détection d'un échec critique.

L'ordre opérationnel, le nombre d'équipements traités simultanément, les délais d'attente et les conditions d'arrêt doivent faire partie de la conception du changement.


# 9. Sécurité de la chaîne CI/CD

## 9.1 Principe du moindre privilège

Une étape de validation de fichiers n'a généralement besoin que d'un accès en lecture au dépôt. Elle ne devrait pas recevoir de clés SSH ou de mots de passe permettant de modifier les équipements.

Les permissions doivent être accordées au job qui en a réellement besoin et limitées au périmètre requis.

## 9.2 Protéger les secrets

N'insérez jamais de secret en clair dans un fichier versionné, une ligne de commande conservée dans un journal ou un rapport d'artefact.

Si des secrets sont nécessaires à une étape opérationnelle :

- utilisez un gestionnaire de secrets approuvé ;
- limitez leur accès à l'environnement ciblé ;
- séparez les secrets de test et de production ;
- évitez de rendre les secrets disponibles aux workflows non fiables ;
- faites tourner tout secret qui a été exposé ;
- vérifiez que les messages d'erreur ne révèlent pas leur contenu.

## 9.3 Distinguer les événements de confiance

Une pull request provenant d'un contributeur externe ne doit pas automatiquement recevoir les secrets et permissions du dépôt cible. Un pipeline doit éviter d'exécuter du code non fiable avec des privilèges élevés.

Pour les workflows de production, utilisez des environnements protégés, des permissions minimales et une revue adaptée. Consultez la documentation de sécurité de la plateforme choisie.

Référence GitHub Actions : https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions

## 9.4 Dépendances des actions

Une action tierce exécutée dans la CI fait partie de la chaîne logicielle. Les versions doivent être surveillées et mises à jour. Dans les contextes de risque élevé, l'équipe peut exiger des références immuables par SHA de commit plutôt qu'un simple tag de version.

L'utilisation de versions récentes n'élimine pas tous les risques ; la provenance, les permissions et le contexte d'exécution restent importants.


# 10. Vérification avant et après changement

## 10.1 Définir des critères d'acceptation

Un plan de changement ne doit pas seulement dire « appliquer la configuration ». Il doit préciser le résultat fonctionnel à obtenir et les conditions qui obligent à arrêter.

Exemple :

**Changement :** ajouter un VLAN de laboratoire sur un commutateur d'accès.

**Préconditions :**

- équipement identifié et joignable ;
- sauvegarde ou version de référence disponible ;
- identifiant VLAN autorisé ;
- ports et trunks concernés documentés ;
- fenêtre de changement approuvée.

**Résultats attendus :**

- VLAN présent ;
- ports affectés conformément au plan ;
- connectivité des services existants maintenue ;
- absence d'alarme critique nouvelle ;
- accès de gestion toujours opérationnel.

**Critères d'arrêt :**

- équipement inattendu ;
- état initial différent de la précondition ;
- perte de connectivité critique ;
- tests obligatoires en échec ;
- durée dépassant le seuil défini.

Ces valeurs et conditions sont des exemples. Le plan réel doit être validé par les responsables de l'infrastructure.

## 10.2 Schéma de passage du test à l'opérationnel

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-labelledby="gate-title gate-desc">
  <title id="gate-title">Passage contrôlé du test au changement opérationnel</title>
  <desc id="gate-desc">Le résultat CI conduit à un examen humain, puis à une décision d'approbation. Le déploiement limité n'est autorisé que si les préconditions sont satisfaites. Les vérifications déterminent la clôture ou le déclenchement d'un retour arrière.</desc>
  <defs>
    <marker id="gate-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .gt-box{fill:#16263b;stroke:#60a5fa;stroke-width:2}
      .gt-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .gt-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .gt-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .gt-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .gt-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#gate-arrow);animation:gt-dash 1.8s linear infinite}
      @keyframes gt-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="348" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="24" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">LA CI PRÉPARE LA DÉCISION, ELLE NE REMPLACE PAS LA GOUVERNANCE</text>
  <rect class="gt-box" x="25" y="75" width="190" height="80" rx="10"/>
  <text class="gt-title" x="120" y="105" text-anchor="middle">Résultats CI</text>
  <text class="gt-text" x="120" y="129" text-anchor="middle">Rapports et tests</text>
  <rect class="gt-gate" x="260" y="75" width="190" height="80" rx="10"/>
  <text class="gt-title" x="355" y="105" text-anchor="middle">Approbation</text>
  <text class="gt-text" x="355" y="129" text-anchor="middle">Autorité désignée</text>
  <rect class="gt-box" x="495" y="75" width="190" height="80" rx="10"/>
  <text class="gt-title" x="590" y="105" text-anchor="middle">Déploiement limité</text>
  <text class="gt-text" x="590" y="129" text-anchor="middle">Périmètre planifié</text>
  <rect class="gt-ok" x="730" y="75" width="205" height="80" rx="10"/>
  <text class="gt-title" x="832" y="105" text-anchor="middle">Post-contrôles</text>
  <text class="gt-text" x="832" y="129" text-anchor="middle">Résultat mesuré</text>
  <path class="gt-flow" d="M215 115 H252"/>
  <path class="gt-flow" d="M450 115 H487"/>
  <path class="gt-flow" d="M685 115 H722"/>
  <rect class="gt-box" x="220" y="230" width="520" height="65" rx="10"/>
  <text class="gt-title" x="480" y="256" text-anchor="middle">Si une précondition ou un test critique échoue</text>
  <text class="gt-text" x="480" y="278" text-anchor="middle">Arrêter la progression, diagnostiquer et exécuter le plan prévu</text>
  <path class="gt-flow" d="M832 155 V195 H740 V222"/>
  <text class="gt-text" x="480" y="322" text-anchor="middle">Ne passez à l'étape suivante que si ses conditions d'entrée sont satisfaites.</text>
</svg>

## 10.3 Retour arrière

Le retour arrière doit utiliser une procédure connue et adaptée au changement : restauration d'une configuration, suppression d'un objet, rétablissement d'une route ou autre action contrôlée.

Il doit indiquer :

- les critères qui le déclenchent ;
- l'action à effectuer ;
- les personnes responsables ;
- les commandes ou procédures autorisées ;
- le résultat attendu ;
- les tests confirmant le rétablissement.

Ne supposez jamais que remettre un fichier Git à sa version précédente remet automatiquement l'équipement dans cet état.


# 11. Atelier pratique complet

## Situation

Une équipe veut ajouter un VLAN de laboratoire et renforcer sa validation CI. Vous devez prouver que l'inventaire peut être validé et que les règles rejettent des données incorrectes, sans déployer de configuration.

## Étape A — Vérifier la structure

Vérifiez que les fichiers suivants existent :

```text
inventory/devices.yml
src/validate_inventory.py
src/__init__.py
tests/test_inventory.py
requirements.txt
.github/workflows/validate.yml
```

## Étape B — Exécuter la validation

```bash
python src/validate_inventory.py
```

Le résultat attendu pour des données conformes est un message de réussite et un code de sortie égal à zéro.

## Étape C — Exécuter les tests

```bash
python -m unittest discover -s tests -v
```

Tous les tests doivent passer. Si ce n'est pas le cas, examinez le message détaillé et vérifiez si l'erreur provient des données, du validateur ou du test.

## Étape D — Introduire une erreur contrôlée

Sur votre copie de laboratoire, modifiez temporairement une adresse IP valide en `not-an-ip`.

Relancez :

```bash
python src/validate_inventory.py
```

Le validateur doit signaler l'adresse et échouer. Restaurez ensuite la valeur correcte.

## Étape E — Créer une branche

```bash
git switch -c feature/test-validation-inventaire
git status
git diff
```

Vérifiez que vous êtes dans la bonne branche et que seuls les fichiers prévus sont modifiés.

## Étape F — Commiter et publier

```bash
git add src tests inventory requirements.txt .github/workflows/validate.yml
git diff --cached
git commit -m "Ajoute la validation automatique de l'inventaire"
git push -u origin feature/test-validation-inventaire
```

## Étape G — Vérifier le pipeline

Ouvrez la pull request. Examinez les résultats de validation et de tests. Si un contrôle échoue, corrigez le problème puis relancez la CI.

La fusion doit rester soumise aux protections configurées dans le dépôt.

**Résultat attendu de l'atelier :** un changement versionné, des règles testées, une CI reproductible et des résultats consultables. Aucun déploiement réseau n'est nécessaire pour démontrer cette réussite.


# 12. Dépannage

## 12.1 Le validateur indique qu'une adresse IP est incorrecte

Vérifiez la valeur, les espaces et le type du champ dans le YAML. Une adresse doit être donnée dans un format que la bibliothèque Python `ipaddress` peut analyser.

## 12.2 La CI ne trouve pas le module `src.validate_inventory`

Vérifiez que `src/__init__.py` existe, que le fichier porte le bon nom et que le job exécute les commandes depuis la racine du dépôt.

## 12.3 Les tests réussissent localement mais échouent dans la CI

Vérifiez la version de Python, les dépendances, les chemins, la casse des noms de fichiers et la reproductibilité de l'environnement. Un dépôt exécuté sur un système sensible à la casse peut se comporter différemment d'un poste Windows.

## 12.4 Le rapport existe même si le pipeline échoue

C'est attendu lorsque la génération du rapport utilise `if: always()`. Examinez les étapes précédentes pour identifier le contrôle défaillant. Un artefact présent ne signifie pas que tous les contrôles ont réussi.

## 12.5 Le YAML est syntaxiquement valide mais l'inventaire est incorrect

Un parseur YAML vérifie seulement la structure du document. Les règles métier — noms uniques, rôles autorisés, champs obligatoires et contraintes d'adressage — doivent être testées séparément.


# 13. Évaluation corrigée

## Questions

1. Pourquoi la validation des données est-elle plus utile qu'un simple contrôle d'existence de fichier ?
2. Pourquoi tester un validateur ?
3. Quelle est la différence entre un test unitaire et un test réseau ?
4. Pourquoi un code de sortie non nul est-il important dans un pipeline ?
5. Que représente un artefact de CI ?
6. Pourquoi faut-il limiter les permissions d'un job qui ne fait que lire des fichiers ?
7. Qu'est-ce qu'un post-contrôle ?
8. Pourquoi une CI ne doit-elle pas forcément déployer automatiquement ?
9. Pourquoi un rapport peut-il exister même si le job échoue ?
10. Quel est le rôle d'une protection de branche ?

## Corrigé

1. Elle détecte les valeurs incorrectes, les champs manquants et les incohérences que la simple présence du fichier ne révèle pas.
2. Pour vérifier que ses règles détectent les erreurs prévues et acceptent les cas valides.
3. Le test unitaire vérifie une petite logique de programme. Le test réseau vérifie un comportement sur une topologie ou des équipements.
4. Il permet au système CI de distinguer un contrôle réussi d'un contrôle en échec.
5. C'est un fichier produit par le pipeline, par exemple un rapport de validation.
6. Parce que chaque permission supplémentaire augmente les possibilités d'action en cas d'erreur ou de compromission.
7. C'est une vérification exécutée après le changement afin de confirmer le résultat opérationnel attendu.
8. Certains changements sont risqués, nécessitent une fenêtre définie et exigent une approbation humaine.
9. Une étape de génération de rapport peut être configurée pour s'exécuter même si une étape précédente échoue.
10. Elle peut imposer des contrôles réussis, une revue et d'autres règles avant d'autoriser les changements sur la branche principale.


# 14. Préparation du niveau expert

Le niveau expert ira au-delà de la validation des fichiers et des tests unitaires. Il portera notamment sur :

- les déploiements progressifs et par lots ;
- les contrôles d'état avant, pendant et après déploiement ;
- les politiques d'approbation et de séparation des responsabilités ;
- la sécurisation avancée des identités et des secrets ;
- l'idempotence et la gestion de l'état attendu ;
- les tests de bout en bout et les tests de résilience ;
- la gestion des changements partiels et les mécanismes d'arrêt ;
- la traçabilité et la mesure de la fiabilité du pipeline ;
- les stratégies de restauration et de récupération ;
- la gouvernance des changements sur un parc réseau étendu.

**Le niveau intermédiaire transforme le dépôt Git en une base testable. Le niveau expert transforme cette base en un processus de changement gouverné, observable et résilient.**


## Références officielles

- Documentation Git : https://git-scm.com/doc
- GitHub Actions : https://docs.github.com/actions
- Sécurisation des workflows : https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- Action Checkout : https://github.com/actions/checkout
- Action Setup Python : https://github.com/actions/setup-python
- Action Upload Artifact : https://github.com/actions/upload-artifact
- PyYAML : https://pyyaml.org/wiki/PyYAMLDocumentation
- Python `unittest` : https://docs.python.org/3/library/unittest.html

**Fichier :** `cicd-network-intermediaire.md`  
**Niveau :** Intermédiaire  
**Fin du cours**
