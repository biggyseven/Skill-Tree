# CI/CD avec GitHub Actions et GitLab CI

## 1. Objectifs du cours

Ce cours prolonge les bases de l’intégration continue et du déploiement continu pour apprendre à concevoir, optimiser, sécuriser et maintenir des pipelines professionnels avec GitHub Actions et GitLab CI.

À la fin de ce niveau, l’apprenant doit être capable de :

- Construire un pipeline composé de plusieurs jobs et étapes.
- Organiser les dépendances entre jobs et exécuter certaines tâches en parallèle.
- Distinguer le cache, les artefacts et les images de conteneurs.
- Gérer les conditions d’exécution selon les branches, les merge requests, les pull requests et les tags.
- Exécuter une matrice de tests sur plusieurs versions d’un langage.
- Publier les rapports de tests et récupérer les livrables produits.
- Construire et publier une image Docker de façon automatisée.
- Préparer un déploiement en staging et en production.
- Gérer les secrets, les permissions et les environnements protégés.
- Réduire le temps d’exécution et les duplications de pipelines.
- Diagnostiquer les échecs de jobs, les problèmes de cache et les erreurs de déploiement.
- Adapter une stratégie CI/CD à une application réelle.

Les deux plateformes partagent les mêmes principes d’ingénierie, mais leur syntaxe diffère. Ce cours présente les concepts, puis les illustre avec les deux outils.

## 2. Rappel : du code au déploiement

Une pipeline CI/CD automatise une succession de contrôles et d'opérations. Elle démarre généralement après une modification du dépôt, mais peut également être déclenchée manuellement, à intervalles réguliers ou à la création d'un tag.

### 2.1 Schéma général

```text
                    DÉVELOPPEUR
                         |
                    git push
                         |
                         v
                 +----------------+
                 | Déclencheur CI |
                 +----------------+
                         |
                         v
                 +----------------+
                 | Vérifications  |
                 | lint / format  |
                 +----------------+
                         |
                         v
                 +----------------+
                 | Tests unitaires|
                 +----------------+
                         |
                         v
                 +----------------+
                 | Build / paquet |
                 +----------------+
                         |
                         v
                 +----------------+
                 | Tests intégrés |
                 +----------------+
                         |
                         v
                 +----------------+
                 | Publication    |
                 | image / paquet |
                 +----------------+
                         |
                         v
                 +----------------+
                 | Déploiement    |
                 | staging        |
                 +----------------+
                         |
                         v
                 +----------------+
                 | Validation     |
                 | et approbation |
                 +----------------+
                         |
                         v
                 +----------------+
                 | Production     |
                 +----------------+
```

Toutes les pipelines n'ont pas besoin de toutes ces étapes. Un projet de bibliothèque Python peut se limiter aux tests et à la publication d'un paquet. Une application conteneurisée peut aussi construire une image Docker et la déployer sur Kubernetes.

La règle fondamentale est de faire échouer la pipeline dès qu'un contrôle essentiel échoue. Un code qui ne passe pas les tests ne doit pas atteindre la production.

### 2.2 Intégration continue, livraison continue et déploiement continu

**Intégration continue (CI)** : chaque modification est vérifiée régulièrement par des contrôles automatisés.

**Livraison continue (Continuous Delivery)** : les versions qui passent les contrôles sont préparées pour être déployées. Une validation humaine ou une opération explicite peut encore être requise.

**Déploiement continu (Continuous Deployment)** : les modifications conformes aux règles du projet sont automatiquement déployées en production, sans approbation manuelle systématique.

Ces pratiques ne sont pas équivalentes. Automatiser le build ne signifie pas que le déploiement en production doit être automatique.

## 3. GitHub Actions et GitLab CI : les différences essentielles

### 3.1 Comparaison du vocabulaire

| Concept | GitHub Actions | GitLab CI |
|---|---|---|
| Fichier principal | `.github/workflows/ci.yml` | `.gitlab-ci.yml` |
| Pipeline | Workflow exécuté pour un événement | Pipeline |
| Unité d'exécution | Job | Job |
| Machine d'exécution | Runner | Runner |
| Étapes d'un job | `steps` | `script`, `before_script`, `after_script` |
| Dépendance entre jobs | `needs` | `needs` |
| Conditions | `if`, filtres d'événements | `rules`, `workflow: rules` |
| Cache | `actions/cache` ou cache intégré d'une action | `cache` |
| Transfert de fichiers | Artifacts Actions | `artifacts` |
| Secrets | Secrets du dépôt, de l'organisation ou de l'environnement | Variables protégées ou fournisseurs externes de secrets |
| Environnement | `environment` | `environment` |
| Matrice | `strategy.matrix` | `parallel:matrix` |
| Réutilisation | Workflows réutilisables, actions composites | `include`, `extends`, composants CI/CD |
| Registre Docker | GitHub Container Registry ou autre registre | GitLab Container Registry ou autre registre |

Un **runner** est la machine ou l'environnement qui exécute les commandes de la pipeline.

Un job peut s'exécuter dans un conteneur, sur une machine virtuelle gérée par la plateforme ou sur un runner autohébergé. Les capacités disponibles dépendent de cette configuration.

### 3.2 Les fichiers n'ont pas le même format d'exécution

Dans GitHub Actions :

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v7

      - name: Exécuter les tests
        run: python -m pytest
```

Dans GitLab CI :

```yaml
test:
  image: python:3.12-slim
  script:
    - python -m pip install -r requirements.txt
    - python -m pytest
```

Dans le premier exemple, `uses` appelle une action réutilisable et `run` exécute des commandes. Dans le second, le job choisit une image d'exécution et lance les commandes de `script`.

Les versions d'actions et les images utilisées doivent être maintenues. Avant de reprendre un exemple, il faut vérifier sa compatibilité avec les runners et les politiques de sécurité du projet.

## 4. Concevoir un pipeline avant d'écrire le YAML

Une pipeline lisible commence par une définition claire des objectifs.

Questions à se poser :

1. Quels événements déclenchent les contrôles ?
2. Quels contrôles sont obligatoires avant d'accepter une modification ?
3. Quels jobs peuvent être exécutés en parallèle ?
4. Quels fichiers doivent être transmis d'un job à un autre ?
5. Quels livrables doivent être conservés ?
6. Quelles opérations nécessitent des secrets ?
7. Quelles opérations sont autorisées uniquement sur la branche principale ou un tag ?
8. Quelles opérations nécessitent une approbation humaine ?

Un mauvais pipeline peut être fonctionnel tout en étant lent, coûteux ou dangereux. Par exemple, une pipeline qui déploie toute branche poussée vers un serveur de production confond contrôle du code et autorisation de livraison.

### 4.1 Définir des objectifs de qualité

Exemple de politique :

| Contrôle | Pull request / merge request | Branche principale | Tag de version |
|---|---|---|---|
| Formatage et lint | Oui | Oui | Oui |
| Tests unitaires | Oui | Oui | Oui |
| Tests intégrés | Oui | Oui | Oui |
| Construction | Oui | Oui | Oui |
| Publication de l'image | Non obligatoire | Oui | Oui |
| Déploiement staging | Selon politique | Oui | Selon politique |
| Déploiement production | Non | Selon politique | Selon politique |

Cette table est un exemple de décision d'équipe. Elle doit être adaptée au coût des tests, au niveau de risque et à la méthode de livraison.

## 5. Comprendre les jobs, les étapes et les dépendances

### 5.1 Le modèle séquentiel

Dans un pipeline simple, les opérations sont regroupées dans plusieurs étapes :

```text
ÉTAPE 1 : Vérifications
    |
    +---- lint
    |
    +---- format-check
              |
              v
ÉTAPE 2 : Tests
    |
    +---- tests-unitaires
    |
    +---- tests-intégration
              |
              v
ÉTAPE 3 : Build
              |
              v
ÉTAPE 4 : Publication
              |
              v
ÉTAPE 5 : Déploiement
```

Les tests unitaires et les tests d'intégration n'ont pas nécessairement besoin de s'exécuter l'un après l'autre. Lorsqu'ils sont indépendants, ils peuvent être lancés simultanément.

### 5.2 Construire un graphe de dépendances

La bonne approche consiste à décrire quelles tâches attendent réellement quelles autres tâches.

```text
                   +--------+
                   |  lint  |
                   +--------+
                       |
                       | peut être indépendant
                       |
             +---------+---------+
             |                   |
             v                   v
       +-----------+       +-------------+
       | Unit tests|       | Type checking|
       +-----------+       +-------------+
             |                   |
             +---------+---------+
                       |
                       v
                 +-----------+
                 |  Package  |
                 +-----------+
                       |
                       v
                 +-----------+
                 |  Publish  |
                 +-----------+
```

Il ne faut pas ajouter une dépendance uniquement parce que deux jobs sont placés dans des étapes successives.

### 5.3 GitHub Actions : dépendance avec `needs`

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Analyse statique"

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Tests unitaires"

  package:
    runs-on: ubuntu-latest
    needs:
      - lint
      - unit-tests
    steps:
      - run: echo "Construction du paquet"
```

`package` démarre uniquement lorsque `lint` et `unit-tests` ont réussi. Les deux premiers jobs peuvent s'exécuter en parallèle.

### 5.4 GitLab CI : dépendance avec `needs`

```yaml
stages:
  - validate
  - package

lint:
  stage: validate
  script:
    - echo "Analyse statique"

unit-tests:
  stage: validate
  script:
    - echo "Tests unitaires"

package:
  stage: package
  needs:
    - lint
    - unit-tests
  script:
    - echo "Construction du paquet"
```

Sans `needs`, les jobs s'exécutent en respectant l'ordre des étapes. Avec `needs`, un job peut démarrer dès que ses dépendances précises sont satisfaites, sans attendre tous les jobs de toutes les étapes précédentes.

Il faut éviter de créer des graphes inutilement complexes : une pipeline difficile à comprendre devient également difficile à dépanner.

## 6. Conditions d'exécution et événements

Une pipeline doit savoir quand lancer un job. Les tests d'une pull request, la publication d'une version et le déploiement de production n'ont pas besoin de s'exécuter dans les mêmes conditions.

### 6.1 Les événements habituels

| Événement | Usage |
|---|---|
| Push sur une branche | Vérifier les nouvelles modifications |
| Pull request | Valider une proposition de modification sur GitHub |
| Merge request | Valider une proposition de modification sur GitLab |
| Push d'un tag | Construire et publier une version |
| Exécution manuelle | Lancer une tâche explicitement |
| Planification | Audit, scan ou maintenance périodique |
| Pipeline parent ou amont | Orchestrer plusieurs projets ou sous-pipelines |

### 6.2 GitHub Actions : filtrer les événements

```yaml
name: CI

on:
  push:
    branches:
      - main
      - "feature/**"
  pull_request:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - run: echo "Vérifications"
```

Le filtre `branches` de `pull_request` s'applique à la branche cible de la pull request. Les motifs doivent être choisis avec attention pour éviter d'exécuter des workflows inutiles ou d'oublier des branches importantes.

### 6.3 GitLab CI : utiliser `workflow: rules`

`workflow: rules` contrôle la création de la pipeline elle-même. Les `rules` définies dans un job déterminent si ce job est inclus.

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'
    - when: never

stages:
  - test

test:
  stage: test
  script:
    - echo "Vérifications"
```

Avec cette configuration, la pipeline est créée pour les événements indiqués. Les autres événements ne sont pas autorisés par cette règle globale.

Les pipelines de merge request doivent être correctement configurées pour le dépôt et sa méthode de travail. La disponibilité de certaines fonctionnalités dépend des paramètres du projet et de l'instance GitLab.

### 6.4 Éviter les pipelines en double dans GitLab

Une configuration de `rules` trop générale peut déclencher une pipeline de branche et une pipeline de merge request pour un même push.

Exemple à éviter :

```yaml
test:
  script:
    - python -m pytest
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - when: always
```

La dernière règle peut aussi autoriser le job dans une pipeline de push. Si le projet reçoit les deux types de pipeline, des exécutions supplémentaires peuvent apparaître.

Une bonne stratégie commence par `workflow: rules`, puis définit les conditions des jobs. Évitez de mélanger sans raison les anciennes règles `only/except` et les nouvelles `rules`.

## 7. Variables, secrets et configuration

Les variables permettent de différencier les environnements sans dupliquer les fichiers de pipeline.

Exemples de configuration non sensible :

```text
APP_ENV=staging
LOG_LEVEL=info
IMAGE_NAME=mon-application
```

Exemples de données sensibles :

```text
DEPLOY_TOKEN
API_SECRET
REGISTRY_PASSWORD
PRIVATE_KEY
```

Un secret n'est pas une simple variable de configuration. Sa confidentialité, sa durée de validité, ses permissions et les jobs autorisés à le lire doivent être maîtrisés.

### 7.1 Variables d'environnement dans GitHub Actions

```yaml
jobs:
  inspect:
    runs-on: ubuntu-latest
    env:
      APP_ENV: staging
      LOG_LEVEL: info
    steps:
      - name: Afficher la configuration non sensible
        run: |
          echo "Environnement : $APP_ENV"
          echo "Niveau de journalisation : $LOG_LEVEL"
```

Une variable définie au niveau du workflow est disponible dans tous ses jobs. Au niveau du job, elle s'applique à ce job ; au niveau d'une étape, elle est limitée à cette étape.

Pour lire un secret configuré dans les paramètres du dépôt ou de l'environnement :

```yaml
- name: Appeler le script de déploiement
  env:
    DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
  run: ./scripts/deploy.sh
```

Ne placez pas directement la valeur réelle du secret dans le YAML. Évitez également de l'afficher avec `echo`, de l'ajouter à des arguments visibles dans les journaux ou de l'inclure dans un artefact.

### 7.2 Variables CI/CD dans GitLab

Les variables peuvent être déclarées dans les paramètres CI/CD du projet ou du groupe, ou définies dans le fichier YAML pour les valeurs non sensibles.

```yaml
deploy-staging:
  stage: deploy
  variables:
    APP_ENV: "staging"
  script:
    - test -n "$DEPLOY_TOKEN"
    - ./scripts/deploy.sh
```

La variable `DEPLOY_TOKEN` doit être configurée séparément dans les paramètres CI/CD, avec un type, une portée, une protection et une politique de masquage appropriés.

Le masquage d'une variable ne constitue pas une protection absolue. Un script compromis pourrait transmettre un secret à une destination externe ou tenter de le transformer avant de l'afficher.

### 7.3 Règles de sécurité des secrets

- Limiter les secrets aux jobs qui en ont réellement besoin.
- Ne pas accorder de secrets de production à un job de tests sans nécessité.
- Ne jamais versionner un fichier `.env` de production.
- Utiliser des secrets distincts pour staging et production.
- Restreindre les branches et les environnements de déploiement.
- Faire tourner les secrets lorsqu'un accès non autorisé est suspecté.
- Préférer des identités temporaires par OIDC lorsqu'un fournisseur le permet.
- Ne pas exécuter du code non fiable avec des permissions élevées.

Les contributions provenant de forks ne disposent généralement pas des mêmes secrets que les workflows de confiance. Cette restriction est importante : elle empêche une modification extérieure de récupérer directement les identifiants de déploiement.

## 8. Permissions minimales et durcissement

Chaque job doit recevoir uniquement les permissions dont il a besoin.

### 8.1 Permissions de `GITHUB_TOKEN`

Un workflow GitHub Actions ne doit pas hériter inutilement de permissions d'écriture.

```yaml
permissions:
  contents: read
```

Cette déclaration limite les permissions du jeton intégré. Si un job doit publier un paquet ou écrire dans un registre, accordez-lui les permissions supplémentaires requises au niveau approprié.

Par exemple, pour publier une image dans GitHub Container Registry, le job peut avoir besoin de :

```yaml
permissions:
  contents: read
  packages: write
```

Ne donnez pas `write-all` par commodité. Un job qui ne fait que lancer des tests n'a généralement pas besoin de modifier les branches, les releases ou les paquets.

### 8.2 Actions tierces

Les actions tierces sont du code exécuté dans votre workflow. Une action malveillante ou compromise peut lire les fichiers accessibles au job, utiliser ses permissions et éventuellement exposer ses secrets.

Bonnes pratiques :

- Privilégier les actions officielles et les dépendances nécessaires.
- Examiner leur code, leur maintenance et les permissions demandées.
- Épingler les actions sensibles à un SHA de commit complet vérifié lorsque la politique du projet le permet.
- Automatiser les mises à jour des dépendances et les examiner avant de les accepter.
- Séparer les jobs de publication des jobs exécutant du code externe.
- Ne jamais utiliser une pull request non fiable comme prétexte pour déclencher un job privilégié.

La syntaxe `@v7` est pratique dans les exemples, mais pointe sur un tag de version. L'épinglage à un SHA complet permet de mieux contrôler la révision effectivement exécutée ; il faut néanmoins conserver une procédure de mise à jour afin de recevoir les correctifs.

### 8.3 Éviter les injections de commandes

Ne concaténez pas directement une entrée non fiable dans une commande shell.

Exemple risqué dans GitHub Actions :

```yaml
- name: Recherche risquée
  run: echo "${{ github.event.pull_request.title }}"
```

Un titre de pull request est une donnée contrôlée par un utilisateur. L'interpolation directe d'une donnée non fiable dans un script shell peut provoquer une injection de commandes.

Il est plus prudent de transférer la valeur dans une variable d'environnement, puis de la traiter comme une donnée :

```yaml
- name: Traiter le titre
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: |
    printf '%s\n' "$PR_TITLE"
```

Cette technique réduit le risque d'interpolation dans le script, mais ne dispense pas de validation lorsqu'une donnée est utilisée comme argument d'une commande.

## 9. Cache et artefacts : deux mécanismes différents

Les termes cache et artefact sont souvent confondus. Cette confusion crée des pipelines fragiles.

### 9.1 Le cache

Le cache sert à réutiliser des données calculées ou téléchargées, généralement pour accélérer une exécution future.

Exemples :

- Cache du gestionnaire de paquets.
- Cache des dépendances Python ou Node.js.
- Cache de compilation.

Un cache peut être absent, expirer ou être remplacé. Le pipeline doit donc rester correct lorsqu'il n'existe pas.

### 9.2 Les artefacts

Les artefacts sont des fichiers produits par un job que l'on souhaite conserver ou transmettre à un autre job.

Exemples :

- Rapport de tests.
- Rapport de couverture.
- Binaire compilé.
- Paquet prêt à publier.
- Fichiers de documentation générés.

```text
                   JOB BUILD
                       |
                       v
               application.tar.gz
                       |
                 [ARTIFACT]
                       |
                       v
                  JOB DEPLOY
                       |
                       v
                Environnement cible
```

Le job de déploiement doit utiliser le livrable produit et validé par la pipeline, plutôt que de reconstruire silencieusement un artefact différent.

### 9.3 Cache dans GitHub Actions

Pour un projet Python, `actions/setup-python` peut gérer le cache des dépendances.

```yaml
steps:
  - uses: actions/checkout@v7

  - uses: actions/setup-python@v7
    with:
      python-version: "3.12"
      cache: pip
      cache-dependency-path: requirements.txt

  - run: python -m pip install -r requirements.txt
```

La clé de cache dépend notamment des fichiers indiqués. Lorsque les dépendances changent, le cache pertinent peut être renouvelé.

Un cache n'est pas une source fiable pour un livrable de production. Il sert à réduire le travail répété, pas à remplacer la construction et la validation du produit.

### 9.4 Artefacts dans GitHub Actions

```yaml
- name: Générer le rapport
  run: python -m pytest --junitxml=test-results.xml

- name: Conserver le rapport
  if: always()
  uses: actions/upload-artifact@v7
  with:
    name: rapports-tests
    path: test-results.xml
    if-no-files-found: warn
    retention-days: 7
```

`if: always()` permet de tenter l'envoi du rapport même si une étape précédente a échoué. Cela suppose que le fichier ait été créé ; `if-no-files-found: warn` évite de transformer automatiquement l'absence de fichier en échec supplémentaire.

### 9.5 Cache et artefacts dans GitLab CI

```yaml
default:
  image: python:3.12-slim

cache:
  key:
    files:
      - requirements.txt
  paths:
    - .cache/pip/

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

test:
  stage: test
  script:
    - python -m pip install -r requirements.txt
    - python -m pytest --junitxml=test-results.xml
  artifacts:
    when: always
    paths:
      - test-results.xml
    reports:
      junit: test-results.xml
    expire_in: 7 days
```

Ici :

- `cache` accélère le téléchargement des dépendances.
- `artifacts:paths` conserve un fichier produit.
- `artifacts:reports:junit` permet à GitLab d'interpréter le rapport de tests.
- `expire_in` limite la durée de conservation configurée pour l'artefact, sous réserve des règles de conservation de la plateforme.

Lorsque `needs` est employé, seuls les artefacts des jobs explicitement concernés sont normalement récupérés par le job dépendant. Il faut donc définir précisément les besoins de transfert.

## 10. Matrices de tests

Une matrice permet d'exécuter le même job avec plusieurs versions de langage, plusieurs systèmes ou différentes configurations.

### 10.1 Pourquoi une matrice ?

Une application Python peut fonctionner avec Python 3.11, mais échouer avec Python 3.13 à cause d'une dépendance ou d'une différence de compatibilité.

Sans matrice, l'équipe devrait écrire un job pour chaque version. Avec une matrice, une seule définition produit plusieurs exécutions.

### 10.2 Matrice GitHub Actions

```yaml
name: Tests multi-versions

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version:
          - "3.11"
          - "3.12"
          - "3.13"

    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: requirements.txt

      - name: Installer les dépendances
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt

      - name: Exécuter les tests
        run: python -m pytest
```

La matrice crée trois exécutions indépendantes du job. `fail-fast: false` évite d'annuler automatiquement les autres variantes dès qu'une version échoue.

Les versions doivent correspondre aux versions réellement prises en charge par le projet et par ses dépendances.

### 10.3 Matrice GitLab CI

```yaml
stages:
  - test

test-python:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION:
          - "3.11"
          - "3.12"
          - "3.13"
  image: python:${PYTHON_VERSION}-slim
  script:
    - python --version
    - python -m pip install -r requirements.txt
    - python -m pytest
```

GitLab crée plusieurs jobs à partir des valeurs de la matrice. Les runners doivent pouvoir télécharger les images correspondantes.

Une matrice améliore la couverture de compatibilité, mais elle augmente aussi la consommation de ressources. Il est possible de réserver une matrice complète à la branche principale et d'exécuter un sous-ensemble plus rapide sur chaque modification, selon le niveau de risque accepté.

## 11. Exemple pratique : application Python

Nous allons créer une petite application Flask, la tester automatiquement puis préparer la construction d'une image conteneurisée.

### 11.1 Structure du projet

```text
mon-api/
├── app.py
├── requirements.txt
├── requirements-dev.txt
├── test_app.py
├── Dockerfile
├── .dockerignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── scripts/
│   └── deploy.sh
└── .gitlab-ci.yml
```

Le projet utilise les mêmes sources avec les deux plateformes. Les fichiers de configuration CI sont spécifiques à chacune.

### 11.2 Fichier `requirements.txt`

```text
Flask>=3.0,<4.0
```

Pour une application de production, les dépendances doivent être choisies, vérifiées puis verrouillées selon une stratégie reproductible. Les plages de versions ci-dessus sont utilisées pour la simplicité pédagogique.

### 11.3 Fichier `requirements-dev.txt`

```text
-r requirements.txt
pytest>=8.0,<10.0
```

### 11.4 Fichier `app.py`

```python
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/")
def index():
    return jsonify(message="API disponible"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

Cet exemple est destiné à l'apprentissage des pipelines. Le serveur de développement intégré de Flask ne doit pas être utilisé comme serveur de production.

### 11.5 Fichier `test_app.py`

```python
from app import app


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_index_endpoint():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "API disponible"
```

Les tests vérifient les réponses HTTP de l'application sans devoir démarrer un serveur réseau externe.

### 11.6 Vérification locale avant CI

Depuis le dossier du projet :

```bash
python -m venv .venv
```

Activation sous Linux :

```bash
source .venv/bin/activate
```

Activation sous PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installation et tests :

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

Si les tests échouent localement, il faut corriger l'application avant de chercher un problème dans GitHub Actions ou GitLab CI.

## 12. Pipeline GitHub Actions complète pour les tests

Créer `.github/workflows/ci.yml`.

```yaml
name: CI Python

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Vérification de la syntaxe et du style
    runs-on: ubuntu-latest

    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v7

      - name: Installer Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements-dev.txt

      - name: Installer les outils
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements-dev.txt
          python -m pip install ruff

      - name: Vérifier le style
        run: ruff check .

      - name: Vérifier la syntaxe et le formatage
        run: python -m compileall -q .

  tests:
    name: Tests Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    needs: lint

    strategy:
      fail-fast: false
      matrix:
        python-version:
          - "3.11"
          - "3.12"
          - "3.13"

    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v7

      - name: Installer Python
        uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: requirements-dev.txt

      - name: Installer les dépendances
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements-dev.txt

      - name: Lancer les tests
        run: python -m pytest -v --junitxml=test-results.xml

      - name: Archiver le rapport de tests
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: test-results-python-${{ matrix.python-version }}
          path: test-results.xml
          if-no-files-found: warn
          retention-days: 7
```

### 12.1 Explication des éléments

`name` donne un nom lisible au workflow.

`on` indique les événements qui le déclenchent. Ici, il s'exécute sur un push vers `main`, sur une pull request ciblant `main` ou manuellement.

`permissions: contents: read` limite les permissions du jeton intégré nécessaires à la lecture du dépôt.

`concurrency` regroupe les exécutions qui partagent la même clé. `cancel-in-progress: true` annule une exécution antérieure du même groupe qui est encore en cours. Cela convient aux tests de branches, mais cette annulation ne doit pas être appliquée sans réflexion à un déploiement de production.

Le job `lint` analyse le style et la syntaxe. Le job `tests` dépend de `lint` et exécute les tests dans une matrice de versions Python.

Les rapports JUnit sont téléversés comme artefacts. Le nom inclut la version Python pour éviter une collision entre les variantes.

### 12.2 Limite de cette pipeline

Le job de tests dépend explicitement de `lint`. Si la matrice contient plusieurs versions et que le lint est suffisamment indépendant des tests, une équipe peut choisir de faire fonctionner les contrôles en parallèle pour réduire la durée totale.

En revanche, ne retirez pas une dépendance simplement pour accélérer l'exécution si un job a besoin d'un résultat généré par un autre.

## 13. Pipeline GitLab CI complète pour les tests

Créer `.gitlab-ci.yml` à la racine.

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'
    - when: never

stages:
  - validate
  - test

default:
  image: python:3.12-slim
  interruptible: true

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  PYTHONDONTWRITEBYTECODE: "1"
  PYTHONUNBUFFERED: "1"

cache:
  key:
    files:
      - requirements-dev.txt
  paths:
    - .cache/pip/

lint:
  stage: validate
  script:
    - python -m pip install --upgrade pip
    - python -m pip install -r requirements-dev.txt
    - python -m pip install ruff
    - ruff check .
    - python -m compileall -q .

tests:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION:
          - "3.11"
          - "3.12"
          - "3.13"
  image: python:${PYTHON_VERSION}-slim
  script:
    - python --version
    - python -m pip install --upgrade pip
    - python -m pip install -r requirements-dev.txt
    - python -m pytest -v --junitxml=test-results.xml
  artifacts:
    when: always
    paths:
      - test-results.xml
    reports:
      junit: test-results.xml
    expire_in: 7 days
```

### 13.1 Points importants

La section `workflow: rules` limite les types de pipeline créés. Elle évite de considérer systématiquement tout événement comme admissible.

`stages` organise les grandes étapes. Les jobs d'une même étape peuvent fonctionner en parallèle. La matrice crée plusieurs variantes du job `tests`.

`default` fournit des paramètres partagés aux jobs qui ne les remplacent pas. `interruptible: true` indique qu'une exécution de ce job peut être interrompue lorsqu'une pipeline devient redondante selon le comportement configuré. Ne l'appliquez pas aux opérations non idempotentes ou aux déploiements qui ne doivent pas être interrompus.

Le rapport JUnit est à la fois conservé dans les artefacts et interprété par GitLab.

### 13.2 Compatibilité des images Python

La matrice doit utiliser des images publiées et réellement disponibles. Une version de Python absente du registre provoquera un échec avant l'exécution des commandes.

Pour les environnements d'entreprise, on peut maintenir des images internes contrôlées afin de centraliser les correctifs, les outils et les certificats nécessaires.

## 14. Réduire le temps d'exécution

Une pipeline trop lente retarde le retour des développeurs et peut encourager à contourner les contrôles.

Il ne faut toutefois pas sacrifier la qualité des vérifications pour gagner quelques secondes.

### 14.1 Identifier les coûts

Mesurer au minimum :

- La durée totale de pipeline.
- La durée de chaque job.
- Le temps d'installation des dépendances.
- Le temps de construction des images.
- Le temps d'attente d'un runner.
- Le taux d'échec des tests.
- Le nombre d'exécutions annulées.
- Les jobs qui se répètent inutilement.

### 14.2 Pratiques d'optimisation

**Paralléliser les jobs indépendants.** Ne faites pas attendre les tests d'intégration la fin d'une analyse qui ne génère aucun fichier nécessaire à leur exécution.

**Utiliser le cache à bon escient.** Mettez en cache les données coûteuses à télécharger ou à recalculer. Ne traitez pas le cache comme un livrable garanti.

**Réduire les installations répétitives.** Regroupez les installations nécessaires dans une image CI contrôlée lorsque cela apporte un gain significatif.

**Éviter les scans redondants.** Placez chaque analyse au niveau où son résultat est le plus utile, sans éliminer les contrôles essentiels.

**Ne pas construire la même chose plusieurs fois sans nécessité.** Lorsque c'est possible, testez et publiez le même artefact validé.

**Adapter les matrices.** Une matrice complète peut être réservée aux branches de référence ou aux versions majeures ; une matrice plus courte peut être utilisée pour le retour rapide.

### 14.3 Pipeline séquentielle contre pipeline parallèle

Supposons les durées suivantes :

| Job | Durée |
|---|---:|
| Lint | 2 minutes |
| Tests unitaires | 5 minutes |
| Tests d'intégration | 8 minutes |
| Build | 4 minutes |

Dans un pipeline entièrement séquentiel, la somme théorique est de 19 minutes.

Si les trois premiers jobs sont réellement indépendants et se déroulent en parallèle, leur phase peut durer environ 8 minutes, puis le build peut prendre 4 minutes. La durée théorique devient environ 12 minutes, hors attente des runners, téléchargements, préparation des environnements et transferts.

Ce calcul est une approximation. Le parallélisme n'apporte aucun gain si les tâches partagent des ressources rares ou si leurs dépendances imposent encore une exécution séquentielle.

## 15. Construire une image Docker en CI

Les étapes de tests d'une application et de construction d'une image doivent être cohérentes. Une image qui n'est jamais testée peut contenir des fichiers manquants, des dépendances absentes ou une configuration incorrecte.

### 15.1 Dockerfile pédagogique

Créer `Dockerfile` :

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
```

Ce Dockerfile démontre le processus de construction, mais il reste volontairement minimal. Pour une utilisation en production, il faut notamment sélectionner une stratégie de serveur WSGI adaptée, exécuter le processus sous un utilisateur non privilégié, limiter la surface de l'image et contrôler les versions de dépendances.

### 15.2 `.dockerignore`

```text
.git
.venv
__pycache__
.pytest_cache
*.pyc
.env
test-results.xml
```

Le fichier `.dockerignore` évite d'envoyer inutilement certains fichiers au contexte de construction. Il contribue également à éviter qu'un fichier local sensible soit inclus accidentellement dans une image.

### 15.3 Construire localement

```bash
docker build -t mon-api:local .
docker run --rm -p 8000:8000 mon-api:local
```

Tester l'application :

```bash
curl http://localhost:8000/health
```

Réponse attendue :

```json
{"status":"ok"}
```

Si la construction échoue localement, corrigez d'abord le Dockerfile et le contexte. Une pipeline CI ne peut pas compenser un processus de construction invalide.

## 16. GitHub Actions : publier une image sur GHCR

GitHub Container Registry (GHCR) permet d'héberger les images d'un projet. La pipeline doit construire une image, lui attribuer un tag non ambigu, puis la publier lorsque les contrôles sont réussis.

Exemple de workflow de publication à placer dans `.github/workflows/publish-image.yml` :

```yaml
name: Publier l'image Docker

on:
  push:
    branches:
      - main
    tags:
      - "v*"

permissions:
  contents: read
  packages: write

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v7

      - name: Préparer Buildx
        uses: docker/setup-buildx-action@v4

      - name: Connexion à GHCR
        uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Construire et publier
        uses: docker/build-push-action@v7
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
```

Avant d'utiliser cet exemple :

- Vérifiez les versions actuelles des actions Docker et leur compatibilité avec vos runners.
- Vérifiez que le dépôt et le registre autorisent la publication.
- Contrôlez la visibilité et les permissions du paquet.
- Placez les contrôles de code nécessaires avant la publication.
- Ajoutez les métadonnées de provenance et un SBOM selon les exigences de votre chaîne de livraison.

L'exemple illustre les commandes de publication, mais il doit être intégré à la pipeline de tests réelle du projet. Une pipeline de publication ne devrait pas publier une image si les tests obligatoires ont échoué.

### 16.1 Pourquoi utiliser le SHA dans le tag ?

Une image étiquetée avec le SHA d'un commit est plus facile à relier à la modification qui l'a produite :

```text
ghcr.io/organisation/mon-api:8f73c2...
```

Un tag tel que `latest` est mutable : il peut désigner différentes images selon le moment. Il est donc moins adapté à l'identification précise d'un artefact de production.

La stratégie recommandée consiste à publier un tag unique lié à une révision et, si nécessaire, à lui associer des tags supplémentaires correspondant aux conventions de release.

## 17. GitLab CI : construire et publier une image

GitLab propose un registre de conteneurs intégré au projet. La publication exige une authentification et un runner correctement configuré.

### 17.1 Exemple avec Docker-in-Docker

L'exemple suivant suppose un runner autorisé à utiliser Docker-in-Docker (DinD). La configuration du runner doit être compatible avec cette approche, notamment sur les exigences de privilèges et de TLS. Ne copiez pas cette configuration dans un runner de production sans examiner son modèle de sécurité.

```yaml
stages:
  - test
  - image

variables:
  IMAGE_TAG: "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"

build-image:
  stage: image
  image: docker:27-cli
  services:
    - name: docker:27-dind
      alias: docker
  variables:
    DOCKER_HOST: "tcp://docker:2376"
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login "$CI_REGISTRY" -u "$CI_REGISTRY_USER" --password-stdin
  script:
    - docker build --pull -t "$IMAGE_TAG" .
    - docker push "$IMAGE_TAG"
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'
```

Ce job est un exemple de publication, à combiner avec les jobs de tests de la section précédente.

Dans un dépôt réel, vérifiez la compatibilité des tags d'images Docker avec le runner et adaptez la configuration du service DinD. Les versions indiquées ici sont des exemples de référence ; sélectionnez et maintenez les versions approuvées par votre projet.

### 17.2 Pourquoi ne pas publier à chaque événement ?

Les branches de travail produisent souvent des versions temporaires. Les publier dans un registre partagé peut multiplier les images inutiles et rendre ambiguë la version stable.

Une politique de publication peut être :

- Sur pull request ou merge request : construire et tester sans publier de version de production.
- Sur branche principale : publier une image identifiée par le SHA du commit.
- Sur tag de release : publier ou promouvoir une version correspondant à la release.
- Sur demande de déploiement : déployer une image déjà construite et vérifiée.

### 17.3 Attention à l'image de déploiement

Un job de déploiement doit pointer vers l'image précise attendue :

```text
registry.exemple.net/organisation/mon-api:8f73c2...
```

Évitez de déployer simplement `latest` sans mécanisme fiable permettant de connaître l'image effectivement utilisée.

Pour renforcer la reproductibilité, on peut utiliser le digest d'image, par exemple :

```text
registry.exemple.net/organisation/mon-api@sha256:...
```

Le digest identifie le contenu de l'image. Le tag est plus facile à lire, mais peut être déplacé vers une autre image.

## 18. Environnements staging et production

Un environnement représente une cible de livraison : développement, test, staging ou production.

Le pipeline doit différencier la construction d'un artefact et l'autorisation de le déployer sur un environnement critique.

### 18.1 Déploiement avec GitHub Actions

Exemple de job de déploiement, à intégrer à un workflow qui a déjà construit et validé l'artefact :

```yaml
deploy-staging:
  runs-on: ubuntu-latest
  needs:
    - tests
  environment:
    name: staging
  steps:
    - name: Récupérer le dépôt
      uses: actions/checkout@v7

    - name: Déployer sur staging
      env:
        DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
      run: |
        test -n "$DEPLOY_TOKEN"
        ./scripts/deploy.sh staging
```

Le dépôt doit contenir le script `scripts/deploy.sh`. Le mécanisme réel de déploiement dépend de l'environnement : SSH, API d'hébergeur, orchestrateur Kubernetes ou autre plateforme.

Il ne suffit pas de déclarer `environment: staging` pour créer automatiquement une infrastructure ou effectuer un déploiement fonctionnel.

### 18.2 Déploiement avec GitLab CI

```yaml
deploy-staging:
  stage: deploy
  environment:
    name: staging
  script:
    - test -n "$DEPLOY_TOKEN"
    - ./scripts/deploy.sh staging
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
```

Ce job doit être placé dans une pipeline contenant une étape `deploy` et disposer du script ainsi que des variables nécessaires.

Le déclenchement manuel crée une décision explicite avant le déploiement. Des protections supplémentaires peuvent être configurées dans les paramètres de l'environnement GitLab.

### 18.3 Protéger la production

Pour la production :

- Restreindre les branches ou tags autorisés.
- Séparer les secrets de production des secrets de tests.
- Exiger les approbations appropriées lorsque cela est nécessaire.
- Limiter les utilisateurs autorisés à déployer.
- Journaliser la version déployée et le résultat de l'opération.
- Préparer une procédure de retour à une version connue.
- S'assurer que les déploiements concurrents ne créent pas de versions incohérentes.

Les règles exactes d'approbation et les niveaux d'accès disponibles peuvent dépendre de l'édition et de la configuration de la plateforme.

## 19. Stratégies de déploiement

Le choix de la stratégie dépend de l'architecture, du trafic, de la tolérance aux interruptions et de la capacité à revenir rapidement à une version précédente.

### 19.1 Déploiement direct

La nouvelle version remplace la précédente.

```text
AVANT
Utilisateurs ---> Application v1

DÉPLOIEMENT

APRÈS
Utilisateurs ---> Application v2
```

Cette méthode est simple, mais peut provoquer une interruption si le remplacement exige un arrêt complet.

### 19.2 Rolling update

Les instances sont remplacées progressivement.

```text
Temps T0 : v1  v1  v1  v1
Temps T1 : v2  v1  v1  v1
Temps T2 : v2  v2  v1  v1
Temps T3 : v2  v2  v2  v1
Temps T4 : v2  v2  v2  v2
```

Cette stratégie est fréquente avec Kubernetes. Elle exige notamment une gestion correcte des sondes de santé, des capacités disponibles et de la compatibilité entre les versions qui coexistent temporairement.

### 19.3 Blue-green

Deux environnements existent : l'environnement actif et le nouvel environnement.

```text
                   +---------------+
Utilisateurs ----> | Routage actif |
                   +---------------+
                      |        |
                    Bleu      Vert
                    v1        v2
                   actif     préparé
```

Le routage est basculé lorsque le nouvel environnement a été validé. La stratégie facilite certains retours arrière, mais demande des ressources supplémentaires et une gestion rigoureuse des données persistantes.

### 19.4 Canary

La nouvelle version reçoit initialement une fraction du trafic :

```text
Trafic total : 100 %
     |
     +---- 95 % ----> Version stable
     |
     +----- 5 % ----> Nouvelle version
```

Si les indicateurs restent bons, le trafic peut être progressivement augmenté. Sinon, il peut être ramené vers la version stable.

Une pipeline CI/CD peut appeler un mécanisme de déploiement canary, mais les règles de routage, les métriques et les décisions d'augmentation du trafic doivent être prévues dans l'infrastructure.

## 20. Déploiement Kubernetes depuis une pipeline

Une application Kubernetes se déploie souvent en mettant à jour l'image d'un Deployment. La pipeline CI/CD ne doit pas recevoir automatiquement des privilèges d'administrateur du cluster.

### 20.1 Exemple de commande

Pour un cluster déjà accessible avec une identité autorisée :

```bash
kubectl set image deployment/mon-api \
  mon-api=ghcr.io/organisation/mon-api:8f73c2

kubectl rollout status deployment/mon-api --timeout=120s
```

La commande `kubectl set image` met à jour le conteneur correspondant dans le Deployment. `kubectl rollout status` attend l'état de progression du déploiement, dans la limite du délai donné.

Ces commandes supposent que :

- Le contexte Kubernetes est correctement configuré.
- L'identité utilisée a les autorisations nécessaires.
- Le nom du Deployment et celui du conteneur correspondent.
- L'image est accessible depuis le cluster.
- Les politiques de sécurité et les contrôles du cluster autorisent l'opération.

Une erreur de permission ou un échec de rollout doit provoquer un échec visible de la pipeline.

### 20.2 Ne pas stocker un kubeconfig administrateur dans le dépôt

Évitez de versionner des fichiers de configuration Kubernetes contenant des identifiants ou certificats privés.

Solutions possibles :

- Identité dédiée et à privilèges limités.
- Authentification temporaire par OIDC lorsqu'elle est supportée et correctement configurée.
- Secrets de déploiement séparés du code source.
- Accès limités à un namespace ou à des ressources précises lorsque c'est compatible avec l'architecture.
- Runner de déploiement isolé pour les environnements sensibles.

Un job qui ne doit mettre à jour qu'un Deployment ne devrait pas pouvoir supprimer n'importe quel objet du cluster.

## 21. OIDC : réduire les secrets de longue durée

OpenID Connect (OIDC) permet à une pipeline d'obtenir une identité fédérée auprès d'un fournisseur compatible. Le fournisseur peut alors délivrer un jeton temporaire, selon les conditions et permissions configurées.

### 21.1 Modèle traditionnel

```text
Pipeline CI
    |
    | secret permanent
    v
Fournisseur cloud
    |
    v
Ressources cloud
```

Un secret permanent doit être protégé, renouvelé et révoqué lorsqu'il n'est plus fiable.

### 21.2 Modèle fédéré OIDC

```text
Pipeline CI
    |
    | jeton d'identité
    v
Fournisseur d'identité
    |
    | vérification de l'émetteur,
    | de l'audience et des conditions
    v
Jeton temporaire
    |
    v
Ressources autorisées
```

L'utilisation d'OIDC ne rend pas la pipeline automatiquement sûre. Le fournisseur doit faire confiance au bon émetteur, vérifier le bon contexte et limiter les ressources autorisées. Une mauvaise règle de confiance peut accorder un accès trop large.

### 21.3 GitHub Actions

Un job utilisant OIDC doit disposer de la permission `id-token: write` pour demander un jeton d'identité :

```yaml
permissions:
  contents: read
  id-token: write
```

Cette permission autorise la demande du jeton ; elle ne donne pas en soi un accès complet au fournisseur cloud. L'accès final dépend de la configuration de fédération et des permissions attribuées par ce fournisseur.

Exemple de principe : un rôle cloud est autorisé uniquement pour un dépôt précis, une branche de confiance ou un environnement de déploiement protégé. La syntaxe d'authentification varie selon le fournisseur utilisé.

### 21.4 GitLab CI

GitLab CI permet de déclarer des ID tokens dans un job :

```yaml
deploy-cloud:
  stage: deploy
  id_tokens:
    CLOUD_ID_TOKEN:
      aud: https://cloud.exemple.net
  script:
    - test -n "$CLOUD_ID_TOKEN"
    - ./scripts/authenticate-and-deploy.sh
```

Ce code illustre la déclaration du jeton, pas une authentification cloud complète. Le script doit utiliser le jeton selon le protocole documenté par le fournisseur ciblé. La valeur d'audience doit correspondre à la configuration de confiance.

La capacité à utiliser un fournisseur de secrets externe peut dépendre de l'édition de GitLab et de l'intégration choisie. Les ID tokens eux-mêmes sont également utilisables pour les fournisseurs qui prennent en charge la fédération OIDC.

## 22. Réutiliser et factoriser la configuration

Les pipelines longues finissent souvent par dupliquer les mêmes commandes et les mêmes règles.

La factorisation réduit le nombre de modifications nécessaires et limite les différences involontaires entre projets.

### 22.1 Workflow réutilisable dans GitHub Actions

Un workflow peut être déclaré comme réutilisable avec `workflow_call`. Un autre workflow peut alors l'appeler avec `uses`.

Exemple simplifié :

```yaml
name: Workflow de test réutilisable

on:
  workflow_call:
    inputs:
      python-version:
        required: false
        type: string
        default: "3.12"

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
        with:
          python-version: ${{ inputs.python-version }}

      - run: python -m pip install -r requirements-dev.txt
      - run: python -m pytest
```

Un workflow appelant peut s'appuyer sur ce contrat :

```yaml
name: CI projet

on:
  pull_request:

jobs:
  tests:
    uses: ./.github/workflows/test-reusable.yml
    with:
      python-version: "3.12"
```

Le workflow appelé doit être stocké à l'emplacement attendu. Les permissions et les secrets transmis doivent respecter le principe du moindre privilège.

### 22.2 Factorisation dans GitLab CI avec `extends`

GitLab permet de définir un modèle puis de le réutiliser avec `extends` :

```yaml
.python-job:
  image: python:3.12-slim
  before_script:
    - python -m pip install --upgrade pip
    - python -m pip install -r requirements-dev.txt

lint:
  extends: .python-job
  stage: validate
  script:
    - python -m compileall -q .
    - ruff check .

tests:
  extends: .python-job
  stage: test
  script:
    - python -m pytest
```

Les clés héritées et les clés redéfinies se combinent selon les règles de fusion de GitLab. Il faut toujours examiner la configuration finale si plusieurs modèles sont imbriqués.

### 22.3 Quand factoriser ?

Factorisez lorsqu'une logique est réellement commune. N'essayez pas de rendre toutes les pipelines identiques si les applications ont des exigences différentes.

Une abstraction trop générique peut cacher le comportement réel d'un job et rendre les incidents plus difficiles à diagnostiquer.

## 23. Séparer les pipelines dans un monorepo

Un monorepo contient plusieurs composants, par exemple :

```text
plateforme/
├── frontend/
├── api/
├── worker/
├── infrastructure/
└── docs/
```

Modifier la documentation ne devrait généralement pas reconstruire et publier tous les services applicatifs.

### 23.1 GitHub Actions : chemins concernés

```yaml
on:
  push:
    branches:
      - main
    paths:
      - "api/**"
      - "Dockerfile"
      - "requirements*.txt"
  pull_request:
    paths:
      - "api/**"
      - "Dockerfile"
      - "requirements*.txt"
```

Ce filtre réduit les exécutions lorsque seuls les chemins indiqués sont concernés. Une configuration réelle doit aussi vérifier la couverture des fichiers communs : scripts partagés, configuration de build ou dépendances centrales.

Attention : dans des pipelines complexes, des filtres de chemins peuvent modifier les événements qui déclenchent le workflow. Il faut éviter de bloquer par erreur un contrôle obligatoire.

### 23.2 GitLab CI : `rules: changes`

```yaml
test-api:
  stage: test
  script:
    - cd api
    - python -m pip install -r requirements-dev.txt
    - python -m pytest
  rules:
    - changes:
        - api/**/*
        - requirements*.txt
        - Dockerfile
```

Les conditions `changes` peuvent être combinées avec d'autres règles pour tenir compte de la branche ou du type de pipeline.

Dans un monorepo, documentez les dépendances entre composants. Une modification dans une bibliothèque partagée peut imposer de tester plusieurs services même si leurs répertoires n'ont pas changé directement.

## 24. Sécurité de la chaîne d'approvisionnement logicielle

La sécurité CI/CD ne se limite pas au stockage des secrets. Il faut également savoir quel code a été construit, avec quelles dépendances et par quelle pipeline.

### 24.1 Principes essentiels

- Utiliser des images de base maintenues et mettre en place des mises à jour régulières.
- Analyser les dépendances et les images pour détecter les vulnérabilités.
- Restreindre les permissions d'écriture des jobs.
- Éviter de construire et publier des artefacts depuis des sources non fiables.
- Épingler les actions critiques à des révisions vérifiées lorsque la politique du projet l'exige.
- Produire un inventaire logiciel (SBOM) si nécessaire.
- Conserver une traçabilité entre le commit, l'image et le déploiement.
- S'assurer que les runners autohébergés sont isolés et maintenus.

### 24.2 SBOM et provenance

Un SBOM (Software Bill of Materials) est un inventaire des composants logiciels d'un artefact. Il aide à déterminer si une dépendance vulnérable est présente.

La provenance décrit des informations sur la construction, notamment la source et le processus ayant produit un artefact, selon le format et les attestations générés.

```text
Commit source
    |
    v
Dépendances contrôlées
    |
    v
Build CI
    |
    +----> Tests
    |
    +----> SBOM
    |
    +----> Attestation de provenance
    |
    v
Image publiée
    |
    v
Déploiement traçable
```

Un SBOM ne prouve pas à lui seul qu'un artefact est sûr. Il donne une visibilité sur ses composants. Une attestation ne remplace pas non plus la vérification de l'identité du producteur et des règles de confiance.

### 24.3 Construire une image puis la promouvoir

Une pratique robuste consiste à construire une image une fois, à la tester, à la publier sous un identifiant unique, puis à promouvoir cette même image vers staging et production.

```text
Commit A
   |
   v
Build image I
   |
   v
Tests sur I
   |
   v
Publication de I
   |
   +------> Staging
   |
   +------> Validation
   |
   +------> Production
```

Cette approche évite que la production reçoive une image différente de celle qui a été testée en staging. La promotion peut être identifiée par tag et idéalement contrôlée par digest.

## 25. Contrôler la qualité avant publication

Il est fréquent d'ajouter plusieurs catégories de contrôles au pipeline :

| Contrôle | Objectif |
|---|---|
| Lint | Détecter les erreurs de style ou certains défauts |
| Tests unitaires | Vérifier de petites unités de comportement |
| Tests d'intégration | Vérifier les interactions entre composants |
| Analyse de types | Détecter certains problèmes statiques |
| Analyse de dépendances | Identifier les dépendances à risque |
| Scan de conteneur | Inspecter les composants d'une image |
| Vérification du Dockerfile | Repérer les mauvaises pratiques de construction |
| Test de santé | Vérifier qu'un service démarre et répond |
| Smoke test après déploiement | Confirmer que les fonctionnalités critiques restent accessibles |

Tous les contrôles ne doivent pas avoir exactement la même règle d'échec. Certaines alertes peuvent être informatives ; les contrôles de sécurité critiques et les tests obligatoires doivent bloquer la publication selon la politique de l'équipe.

N'utilisez pas une règle permissive comme `continue-on-error` ou `allow_failure` pour masquer régulièrement un contrôle qui devrait empêcher la livraison.

## 26. Dépannage : erreurs fréquentes

### 26.1 Le job ne démarre pas

Causes possibles :

- Le workflow n'est pas déclenché par l'événement attendu.
- Les filtres de branche ou de chemins excluent l'exécution.
- Les `rules` GitLab n'incluent pas le job.
- Aucun runner compatible n'est disponible.
- Le fichier de pipeline contient une erreur YAML ou une configuration invalide.

Méthode :

1. Identifier l'événement reçu.
2. Vérifier les filtres et les règles.
3. Valider la syntaxe.
4. Vérifier l'état et les capacités des runners.
5. Examiner le journal d'exécution.

### 26.2 `ModuleNotFoundError` en Python

Causes possibles :

- Les dépendances n'ont pas été installées.
- Le job utilise le mauvais environnement Python.
- Le fichier `requirements-dev.txt` n'est pas présent dans la branche.
- Une dépendance n'est pas déclarée.
- Le répertoire de travail est incorrect.

Vérifier :

```bash
python --version
python -m pip --version
python -m pip install -r requirements-dev.txt
python -m pip list
```

Utilisez `python -m pip` afin de relier explicitement le gestionnaire de paquets à l'interpréteur choisi.

### 26.3 Les tests passent localement mais échouent en CI

Causes possibles :

- Versions différentes de Python.
- Variables d'environnement manquantes.
- Dépendance sur un fichier non versionné.
- Dépendance au fuseau horaire ou à la locale.
- Test dépendant de l'ordre d'exécution.
- Ressources externes indisponibles.
- Sensibilité à la casse du système de fichiers.

Une CI fiable doit détecter les défauts, mais elle ne doit pas dépendre d'une configuration personnelle non documentée.

### 26.4 Le cache semble ignoré

Causes possibles :

- Les fichiers dont dépend la clé ont changé.
- Le chemin de cache est incorrect.
- Le job s'exécute sur un runner sans cache partagé.
- La clé varie entre les exécutions.
- L'archive n'est pas restaurée ou sauvegardée comme prévu.

Le cache peut être absent sans que le pipeline soit incorrect. Vérifiez d'abord la reproductibilité du job sans cache, puis optimisez le mécanisme.

### 26.5 Un job GitLab ne récupère pas les fichiers précédents

Les fichiers du système de fichiers d'un job ne doivent pas être supposés présents dans un job exécuté séparément.

Solutions possibles :

- Déclarer et conserver des artefacts.
- Configurer explicitement leur transfert avec `needs`.
- Construire à nouveau le résultat si cela est moins coûteux et plus fiable.
- Utiliser un registre pour partager des images ou des paquets versionnés.

Ne confondez pas la conservation d'un fichier dans un job et le partage de ce fichier entre tous les runners.

### 26.6 La publication de l'image échoue

Vérifier :

- Les permissions de publication.
- L'adresse du registre.
- Le nom du dépôt et le tag.
- Les identifiants utilisés pour la connexion.
- Les limites de stockage et la politique de rétention.
- La disponibilité du daemon ou du builder.
- Les paramètres réseau du runner.
- La capacité du compte ou du jeton à écrire dans le registre.

Ne résolvez pas un problème de permissions en donnant des droits d'administrateur à toute la pipeline.

### 26.7 Le déploiement réussit, mais l'application est indisponible

Un code de sortie réussi peut uniquement signifier que la commande de déploiement s'est terminée. Il ne garantit pas que le service fonctionne correctement pour les utilisateurs.

Prévoir une vérification après déploiement :

```bash
curl --fail --silent --show-error \
  https://staging.exemple.net/health
```

Cette commande n'est pertinente que si l'URL et l'endpoint existent dans l'environnement ciblé. En cas d'échec, collecter les journaux et l'état du déploiement avant de décider d'un retour arrière.

## 27. Exercice guidé : créer un pipeline de bout en bout

### Objectif

Créer un pipeline de tests sur plusieurs versions de Python, puis ajouter une étape de publication d'image Docker sur la branche principale.

### Étape 1 : initialiser le dépôt

Créer les fichiers de l'application des sections précédentes, puis vérifier les tests localement.

```bash
git init
git add .
git commit -m "Initialiser l'API et ses tests"
```

Créer ensuite un dépôt distant et pousser le code sur la branche principale.

### Étape 2 : configurer les tests

Choisir GitHub Actions ou GitLab CI, puis créer le fichier de pipeline correspondant aux exemples.

Vérifier que :
- Le pipeline démarre sur une pull request ou une merge request.
- Les tests s'exécutent sur les versions de Python prévues.
- Un rapport est produit même si les tests échouent après le démarrage du framework de tests.
- Un échec de test rend la pipeline rouge.

### Étape 3 : ajouter la construction Docker

Créer le Dockerfile, puis exécuter localement :

```bash
docker build -t mon-api:local .
docker run --rm -p 8000:8000 mon-api:local
```

Vérifier le endpoint de santé, puis arrêter le conteneur.

### Étape 4 : publier sur la branche principale

Configurer l'accès au registre et intégrer un job de publication.

La publication doit être bloquée si les contrôles obligatoires ont échoué. Le tag de l'image doit permettre d'identifier le commit source.

### Étape 5 : préparer staging

Créer l'environnement staging et configurer le secret de déploiement dans les paramètres de la plateforme.

Créer le script de déploiement correspondant à l'infrastructure réelle. Ne placez pas de mots de passe ou de clés privées dans le dépôt.

### Étape 6 : tester les échecs

Provoquer volontairement plusieurs erreurs contrôlées :

- Ajouter un test qui échoue.
- Modifier une dépendance nécessaire.
- Introduire une erreur dans le Dockerfile.
- Retirer temporairement une variable non sensible de test.
- Désactiver l'accès au registre dans un environnement d'essai.

Pour chaque erreur, noter à quel job la pipeline s'arrête et vérifier que les étapes de publication ou de déploiement ne s'exécutent pas indûment.

### Critères de réussite

Le projet est réussi lorsque :

- Les modifications sont testées automatiquement.
- Les échecs sont visibles et bloquent les étapes dépendantes.
- Les rapports sont conservés.
- L'image publiée correspond au commit attendu.
- L'accès au registre repose sur des identifiants protégés.
- Le déploiement staging utilise l'image validée.
- La procédure de diagnostic est documentée.

## 28. Exercices d'application

### Exercice 1 : dépendances entre jobs

Un pipeline comprend `lint`, `unit-tests`, `integration-tests` et `package`. Le job `package` n'utilise les résultats que des tests unitaires et des tests d'intégration. Les trois premiers jobs peuvent être indépendants.

**Questions :**

1. Quels jobs peuvent s'exécuter en parallèle ?
2. Quelles dépendances faut-il ajouter à `package` ?
3. Pourquoi ne faut-il pas faire dépendre `integration-tests` de `lint` si aucun résultat de lint n'est utilisé ?

### Exercice 2 : cache ou artefact ?

Classer les éléments suivants :

- Dépendances téléchargées par pip.
- Rapport JUnit.
- Image Docker validée.
- Binaire généré par le build.
- Fichiers temporaires servant à accélérer un compilateur.

**Question complémentaire :** lesquels doivent pouvoir être reconstruits et lesquels doivent être explicitement versionnés ou transférés pour garantir la reproductibilité d'un déploiement ?

### Exercice 3 : règles GitLab

Une pipeline se déclenche à la fois sur push et sur merge request. Un développeur constate deux pipelines à chaque push sur une branche disposant d'une merge request ouverte.

**Travail :**

1. Examiner `workflow: rules`.
2. Examiner les règles de chaque job.
3. Définir les événements réellement nécessaires.
4. Réduire les exécutions en double sans éliminer les contrôles de merge request.

### Exercice 4 : stratégie de publication

Une équipe utilise `latest` pour ses environnements staging et production. Après un incident, elle n'arrive pas à identifier l'image exacte qui avait été déployée.

Proposer une stratégie comprenant :

- Des tags immuablement identifiables par commit ou release.
- Une méthode de promotion entre environnements.
- Une procédure de retour à la version précédente.
- La conservation des informations permettant d'identifier l'image déployée.

### Exercice 5 : sécurité

Un développeur propose de donner `write-all` au `GITHUB_TOKEN` et de rendre tous les secrets accessibles au job de test afin de « régler les problèmes de permissions ».

Expliquer les risques, puis définir une stratégie de moindre privilège.

## 29. Corrigés des exercices

### Corrigé 1

`lint`, `unit-tests` et `integration-tests` peuvent fonctionner en parallèle si aucun de ces jobs ne dépend d'un résultat produit par un autre. `package` dépend des tests unitaires et des tests d'intégration, puisque ces deux validations doivent être réussies avant la construction du paquet.

Le lint peut être une condition obligatoire de la pipeline sans être nécessairement une dépendance de données de chacun des tests. La distinction entre dépendance de résultat et politique générale de qualité permet de concevoir un graphe efficace.

### Corrigé 2

Le cache est approprié aux dépendances téléchargées et aux fichiers temporaires destinés à accélérer un calcul. Les rapports JUnit et les binaires produits sont des artefacts lorsqu'ils doivent être conservés ou transmis.

Une image Docker validée doit être publiée ou conservée dans un registre sous une référence précise si elle doit être promue vers d'autres environnements. Il ne faut pas compter sur un cache local de runner pour un déploiement reproductible.

### Corrigé 3

La solution consiste à définir une politique de création de pipeline explicite avec `workflow: rules`, puis des règles de job cohérentes. On peut, par exemple, autoriser les pipelines de merge request et les pipelines de branche principale tout en évitant une pipeline de branche redondante lorsque la branche fait déjà l'objet d'une merge request.

Le choix exact dépend du mode de travail de l'équipe, mais les règles doivent être testées sur les événements push, merge request, tag et exécution planifiée.

### Corrigé 4

Chaque build doit recevoir un identifiant unique lié au commit, ou être publié selon une convention de release. L'image validée doit être promue entre les environnements sans reconstruction non contrôlée.

Le registre doit conserver les images nécessaires au retour arrière, et les journaux de déploiement doivent enregistrer l'identifiant ou le digest effectivement déployé.

### Corrigé 5

`write-all` autorise des opérations d'écriture qui ne sont pas nécessaires à un job de tests et augmente l'impact possible d'une compromission. Le job pourrait modifier le dépôt ou les artefacts selon les permissions accordées.

La stratégie correcte consiste à définir des permissions de lecture au niveau général et à accorder des permissions d'écriture uniquement aux jobs qui publient effectivement un artefact. Les secrets de production ne doivent être accessibles qu'aux jobs de déploiement de confiance. Les contributions non fiables doivent être exécutées sans privilèges de production.

## 30. Projet final : pipeline CI/CD professionnelle

### Contexte

Une équipe maintient une API utilisée par plusieurs services internes. Elle souhaite automatiser les tests, publier des conteneurs et déployer une version validée sur staging avant sa mise en production.

### Exigences fonctionnelles

La pipeline doit :

1. Exécuter le lint et les tests unitaires.
2. Tester au moins deux versions de Python.
3. Générer un rapport de tests exploitable.
4. Construire une image Docker.
5. Publier l'image uniquement après les validations requises.
6. Étiqueter l'image avec une référence unique liée au commit.
7. Autoriser le déploiement de staging à partir d'une version validée.
8. Protéger le déploiement de production par une règle de branche, de tag ou d'approbation adaptée.
9. Enregistrer la version déployée et vérifier la santé du service.
10. Documenter la procédure de retour arrière.

### Livrables

- Fichier `.github/workflows/ci.yml` ou `.gitlab-ci.yml`.
- `Dockerfile` et `.dockerignore`.
- Tests automatisés.
- Configuration des environnements.
- Script de déploiement adapté à l'infrastructure.
- Documentation de dépannage.
- Tableau des permissions requises par job.

### Critères d'évaluation

| Critère | Pondération |
|---|---:|
| Validité et lisibilité du pipeline | 20 % |
| Qualité des tests et des rapports | 20 % |
| Gestion des dépendances et des artefacts | 10 % |
| Construction et traçabilité de l'image | 15 % |
| Sécurité des secrets et permissions | 15 % |
| Stratégie de déploiement et retour arrière | 10 % |
| Diagnostic et documentation | 10 % |

Une pipeline qui fonctionne uniquement dans le cas nominal, mais publie malgré des tests échoués, ne peut pas être considérée comme terminée.

## 31. Checklist de mise en production

### Qualité

- [ ] Les tests obligatoires s'exécutent automatiquement.
- [ ] Les contrôles de style ou de qualité sont définis.
- [ ] Les rapports de tests sont accessibles.
- [ ] Les dépendances utilisées sont documentées et maintenues.
- [ ] Les jobs indépendants sont parallélisés sans créer de dépendances artificielles.

### Fiabilité

- [ ] Les échecs bloquent les étapes qui en dépendent.
- [ ] Les artefacts utiles sont conservés suffisamment longtemps.
- [ ] Les caches sont facultatifs pour la correction du pipeline.
- [ ] Le build est reproductible autant que raisonnablement possible.
- [ ] Le pipeline ne publie pas une image différente de celle qui a été testée.

### Sécurité

- [ ] Les permissions sont minimales.
- [ ] Les secrets ne figurent pas dans le dépôt.
- [ ] Les secrets de production sont réservés aux jobs de confiance.
- [ ] Les actions et dépendances tierces sont surveillées.
- [ ] Les runners sont maintenus et isolés.
- [ ] Les publications et déploiements sont limités aux branches ou tags autorisés.
- [ ] Les identifiants de déploiement ont une portée limitée et une procédure de révocation.
- [ ] La provenance et les composants des artefacts sont vérifiés selon les exigences du projet.

### Exploitation

- [ ] Le pipeline fournit des journaux compréhensibles.
- [ ] Les durées de jobs sont mesurées.
- [ ] Les exécutions redondantes sont limitées.
- [ ] La version déployée peut être identifiée.
- [ ] Une procédure de retour arrière est disponible.
- [ ] L'état du service est contrôlé après déploiement.

## 32. Glossaire

**Artefact** : fichier produit par un job et conservé ou transféré vers une autre étape.

**Build** : processus de construction d'un livrable à partir du code source et de ses dépendances.

**Cache** : données réutilisées pour accélérer une exécution ultérieure, sans constituer nécessairement un livrable fiable.

**CD** : livraison continue ou déploiement continu, selon le niveau d'automatisation visé.

**CI** : intégration continue, pratique consistant à vérifier régulièrement les modifications par des contrôles automatisés.

**DAG** : graphe orienté sans cycle. Il représente les dépendances entre jobs.

**Digest** : identifiant cryptographique associé au contenu d'une image ou d'un artefact.

**Environnement** : cible de déploiement telle que staging ou production.

**GHCR** : GitHub Container Registry, registre de conteneurs associé à GitHub.

**GitHub Actions** : système d'automatisation de workflows intégré à GitHub.

**GitLab CI** : système de pipelines et de jobs intégré à GitLab.

**Job** : unité d'exécution d'un pipeline.

**Merge request** : proposition de fusion d'une branche dans GitLab.

**OIDC** : protocole d'identité fédérée permettant notamment l'obtention de jetons temporaires auprès de fournisseurs compatibles.

**Pull request** : proposition de modification et de fusion sur GitHub.

**Runner** : machine ou environnement qui exécute les jobs.

**SBOM** : inventaire des composants logiciels d'un produit.

**Secret** : donnée sensible utilisée pour l'authentification ou l'accès à une ressource.

**Staging** : environnement de préproduction dans lequel une version est validée avant production.

**Workflow** : définition des événements, jobs et règles d'exécution dans GitHub Actions.

## 33. Références officielles

### GitHub Actions

- Documentation générale : https://docs.github.com/en/actions
- Syntaxe des workflows : https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
- Utiliser les artefacts : https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts
- Mise en cache des dépendances : https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
- Sécurité de GitHub Actions : https://docs.github.com/en/actions/security-for-github-actions
- Renforcement de la sécurité des déploiements : https://docs.github.com/en/actions/how-tos/secure-your-work/security-hardening-your-deployments
- Environnements de déploiement : https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments
- Workflows réutilisables : https://docs.github.com/en/actions/sharing-automations/reusing-workflows
- Authentification OIDC auprès des fournisseurs cloud : https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-cloud-providers

### GitLab CI/CD

- Documentation CI/CD : https://docs.gitlab.com/ci/
- Référence YAML : https://docs.gitlab.com/ci/yaml/
- Dépendances entre jobs : https://docs.gitlab.com/ci/yaml/needs/
- Conditions d'exécution des jobs : https://docs.gitlab.com/ci/jobs/job_rules/
- Cache : https://docs.gitlab.com/ci/caching/
- Artefacts : https://docs.gitlab.com/ci/jobs/job_artifacts/
- Secrets externes : https://docs.gitlab.com/ci/secrets/
- Authentification OIDC avec ID tokens : https://docs.gitlab.com/ci/secrets/id_token_authentication/
- Registre de conteneurs : https://docs.gitlab.com/user/packages/container_registry/
- Construction et publication d'images : https://docs.gitlab.com/user/packages/container_registry/build_and_push_images/
- Sécurité des déploiements : https://docs.gitlab.com/ci/environments/deployment_safety/

### Docker et chaîne d'approvisionnement

- Docker Build avec GitHub Actions : https://docs.docker.com/build/ci/github-actions/
- Bonnes pratiques de construction : https://docs.docker.com/build/building/best-practices/
- Attestations de build : https://docs.docker.com/build/metadata/attestations/

Ces références doivent être consultées avant d'adopter une syntaxe ou une action dans un pipeline de production. Les plateformes évoluent : les versions d'actions, les fonctionnalités disponibles et certaines règles de sécurité peuvent changer.