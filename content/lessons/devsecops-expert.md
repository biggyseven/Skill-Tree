# DevSecOps

## 1. Positionnement du niveau expert

Ce cours représente l'étape de convergence des compétences acquises dans le parcours DevOps. Il ne s'agit plus simplement d'ajouter des scanners à une pipeline : il faut concevoir un système de livraison dans lequel la sécurité est vérifiable, mesurable, automatisée et intégrée aux décisions de mise en production.

À la fin de ce niveau, il faut être capable de :

- Concevoir une stratégie DevSecOps pour une application complète.
- Intégrer les contrôles de sécurité dans GitHub Actions et GitLab CI.
- Sécuriser les dépendances, le code, les images Docker, les manifests Kubernetes et les configurations Terraform.
- Protéger les secrets, les identités et les permissions des pipelines.
- Produire et vérifier des SBOM, des signatures et des attestations de provenance.
- Définir des politiques de blocage adaptées au niveau de risque.
- Déployer progressivement des contrôles sans paralyser les équipes.
- Gérer une compromission de pipeline ou de chaîne d'approvisionnement logicielle.
- Mesurer l'efficacité des contrôles et améliorer continuellement le dispositif.

### 1.1. Continuité avec les cours précédents

Les notions suivantes sont considérées comme acquises :

| Cours antérieur | Réutilisation dans DevSecOps |
|---|---|
| Git et stratégies de branching | Protection des branches, revue de code, traçabilité des changements |
| Docker et sécurité des conteneurs | Images minimales, utilisateurs non privilégiés, réduction de la surface d'attaque |
| Kubernetes avancé et sécurité | RBAC, Pod Security Standards, NetworkPolicy, gestion des secrets |
| CI/CD avec GitHub Actions et GitLab CI | Orchestration des tests, contrôles automatiques et déploiements |
| Terraform et IaC à grande échelle | Détection des configurations dangereuses et gouvernance de l'infrastructure |
| Ansible | Configuration sécurisée et conformité des serveurs |
| SRE : SLI, SLO et gestion des incidents | Mesure de l'impact, gestion des incidents de sécurité et retour d'expérience |

L'objectif est de relier ces éléments dans une chaîne de livraison unique.

### 1.2. Architecture cible

```text
                 DEVELOPPEUR
                      |
                      v
             +------------------+
             | Code source Git  |
             | Revue + règles   |
             +------------------+
                      |
                      v
             +------------------+
             | CI : validation  |
             | Tests + SAST     |
             | Secrets + SCA    |
             +------------------+
                      |
                      v
             +------------------+
             | Build Docker     |
             | Scan image       |
             | SBOM + provenance|
             +------------------+
                      |
                      v
             +------------------+
             | Registre privé   |
             | Image immuable   |
             +------------------+
                      |
                      v
             +------------------+
             | Politique de     |
             | promotion        |
             +------------------+
                      |
                      v
             +------------------+
             | Kubernetes       |
             | Admission + RBAC |
             | NetworkPolicy    |
             +------------------+
                      |
                      v
             +------------------+
             | Observabilité    |
             | Alertes + SRE    |
             +------------------+
                      |
                      v
             +------------------+
             | Retour de sécurité|
             | Correction       |
             +------------------+
```

Chaque étape doit produire des preuves exploitables. Un contrôle qui échoue silencieusement ou dont les résultats ne sont jamais consultés apporte peu de protection.

## 2. Fondamentaux du DevSecOps

### 2.1. DevSecOps : définition

Le DevSecOps consiste à intégrer les exigences de sécurité à toutes les étapes du cycle de développement et d'exploitation.

Une démarche traditionnelle peut fonctionner ainsi :

1. L'équipe développe une application.
2. L'équipe livre l'application.
3. Une équipe de sécurité réalise un audit tardif.
4. Les vulnérabilités sont découvertes après la livraison.
5. Des corrections coûteuses doivent être réalisées dans l'urgence.

Une démarche DevSecOps déplace les contrôles vers les premières étapes, tout en conservant les validations nécessaires avant la production et pendant l'exploitation.

```text
APPROCHE TARDIVE

Développement ------> Livraison ------> Audit
                                          |
                                          v
                                    Corrections
                                    coûteuses


APPROCHE DEVSECOPS

Code --> Tests --> Scans --> Build --> Validation --> Déploiement
  ^        |         |         |           |              |
  |        +---------+---------+-----------+--------------+
  |                      Feedback continu
  +---------------- Correction et amélioration
```

### 2.2. DevSecOps ne signifie pas « tout bloquer »

Les contrôles doivent être proportionnés aux risques.

Par exemple :

- Un secret détecté dans un commit doit généralement bloquer la livraison.
- Une vulnérabilité critique exploitable dans un composant exposé sur Internet peut justifier un blocage immédiat.
- Une vulnérabilité faible sans chemin d'exploitation crédible peut être suivie et corrigée selon un délai défini.
- Un avertissement de style sans impact de sécurité ne doit pas être traité comme une compromission.

Une politique efficace distingue :

- La détection.
- La qualification du risque.
- La décision de blocage.
- La gestion des exceptions.
- La correction.
- La vérification de la correction.

### 2.3. Modèle de responsabilité partagée

| Acteur | Responsabilités principales |
|---|---|
| Développeurs | Code sûr, tests, dépendances, correction des vulnérabilités |
| Équipe plateforme | Sécurité des runners, registres, environnements et clusters |
| Équipe sécurité | Politiques, modélisation des menaces, validation et accompagnement |
| SRE / exploitation | Surveillance, réponse aux incidents, fiabilité et récupération |
| Responsables produit | Arbitrage des risques métier et des priorités |
| Équipe de gouvernance | Exigences, preuves, conformité et suivi des exceptions |

La sécurité ne doit pas reposer uniquement sur une équipe spécialisée. Les responsabilités doivent être explicites et vérifiables.

## 3. Modélisation des menaces

Avant de choisir les scanners, il faut identifier les actifs, les menaces et les chemins d'attaque.

### 3.1. Actifs à protéger

Dans une chaîne CI/CD, les actifs les plus importants sont souvent :

- Le code source.
- Les identifiants et jetons d'accès.
- Les runners et agents de build.
- Les images de conteneurs.
- Les registres d'artefacts.
- Les clés de signature.
- Les environnements de production.
- Les états Terraform.
- Les journaux de sécurité et les preuves de livraison.

### 3.2. Principales menaces

| Menace | Exemple | Protection principale |
|---|---|---|
| Vol de secrets | Jeton affiché dans un journal | Secrets gérés, masquage, rotation |
| Compromission d'une dépendance | Bibliothèque malveillante | SCA, verrouillage, provenance |
| Compromission d'une action CI | Action externe détournée | SHA immuable, audit, permissions minimales |
| Injection dans une pipeline | Entrée utilisateur interprétée comme commande | Validation des entrées, isolation des jobs |
| Build falsifié | Image construite à partir d'un code non approuvé | Provenance, signatures, contrôle de promotion |
| Mauvaise configuration IaC | Stockage public involontaire | Scans IaC, policy as code |
| Escalade dans Kubernetes | Conteneur privilégié | Pod Security Standards, RBAC, admission |
| Runner compromis | Vol de secrets ou d'artefacts | Runners éphémères et isolés |

### 3.3. Modéliser un flux de livraison

Pour chaque étape, poser cinq questions :

1. Quelle donnée entre dans cette étape ?
2. Qui contrôle cette donnée ?
3. Quelles permissions sont disponibles ?
4. Quel résultat est produit ?
5. Comment vérifier que ce résultat n'a pas été altéré ?

Exemple : un job de build reçoit du code provenant d'une branche de pull request. Il ne devrait pas recevoir automatiquement des secrets de production ni disposer de permissions permettant de modifier les déploiements.

## 4. Sécurité du code source et des dépôts Git

### 4.1. Protéger les branches importantes

Pour une branche de production :

- Exiger des revues de code.
- Exiger le succès des contrôles obligatoires.
- Interdire les modifications directes lorsque c'est possible.
- Limiter les personnes autorisées à approuver les changements sensibles.
- Protéger les fichiers de pipeline et les politiques de sécurité.
- Journaliser les changements de règles et les exceptions.

Les protections de branches doivent être accompagnées de règles sur les dépôts, les environnements et les permissions.

### 4.2. Protéger les fichiers critiques

Les fichiers suivants méritent une attention particulière :

```text
.github/workflows/
.gitlab-ci.yml
Dockerfile
compose.yaml
k8s/
helm/
terraform/
ansible/
policy/
```

Un changement de code applicatif et un changement de pipeline n'ont pas nécessairement le même niveau de risque.

Par exemple, modifier un workflow pour ajouter un accès aux secrets peut avoir des conséquences plus importantes qu'une modification de présentation sur une page Web.

### 4.3. Détection des secrets

Les secrets accidentellement committés peuvent inclure :

- Clés API.
- Jetons d'accès.
- Mots de passe.
- Clés privées.
- Identifiants de base de données.
- Clés d'accès à un fournisseur cloud.

Un outil de détection de secrets doit être exécuté en CI et, idéalement, avant le commit.

Exemple avec Gitleaks, dans un environnement où l'outil est installé :

```bash
gitleaks git .
```

La syntaxe et les options exactes dépendent de la version installée ; vérifier la documentation correspondante avant d'intégrer la commande dans une pipeline.

**Important :** supprimer un secret du dernier commit ne suffit pas toujours. Le secret peut rester présent dans l'historique Git, les journaux, les artefacts ou les caches.

En cas d'exposition :

1. Révoquer ou désactiver le secret.
2. Créer un nouveau secret si nécessaire.
3. Identifier les usages et accès suspects.
4. Supprimer les copies exposées lorsque cela est possible.
5. Réécrire l'historique uniquement si nécessaire, avec coordination.
6. Rechercher les autres secrets exposés.

La rotation du secret est prioritaire sur le nettoyage de l'historique.

## 5. Analyse de sécurité du code

### 5.1. SAST : analyse statique

Le SAST (*Static Application Security Testing*) analyse le code sans devoir exécuter l'application.

Il peut rechercher notamment :

- Injections SQL.
- Faiblesses de validation des entrées.
- Utilisation de fonctions dangereuses.
- Erreurs cryptographiques courantes.
- Exposition accidentelle d'informations.
- Certains problèmes de contrôle d'accès.

Exemples d'outils :

- Semgrep.
- CodeQL.
- SonarQube, selon les règles et éditions utilisées.
- Les analyseurs SAST disponibles dans GitLab.

Exemple illustratif avec Semgrep :

```bash
semgrep scan --config auto .
```

Le jeu de règles utilisé doit être choisi et versionné selon les langages et les exigences du projet.

Le SAST ne prouve pas que le code est sûr. Il détecte des motifs suspects et peut produire des faux positifs ou manquer des vulnérabilités.

### 5.2. DAST : tests dynamiques

Le DAST (*Dynamic Application Security Testing*) teste une application en cours d'exécution.

Il peut rechercher des problèmes comme :

- Absence de certains en-têtes de sécurité.
- Mauvaise configuration HTTP.
- Vulnérabilités Web connues.
- Comportements dangereux face à des entrées spécifiques.

Un scanner DAST doit cibler un environnement autorisé et isolé. Il ne faut pas lancer des tests agressifs contre un système tiers ou une production sans autorisation et plan de test.

### 5.3. Tests complémentaires

| Contrôle | Objet |
|---|---|
| SAST | Code source |
| DAST | Application exécutée |
| SCA | Bibliothèques et dépendances |
| Secret scanning | Secrets présents dans le dépôt |
| Fuzzing | Robustesse face à des entrées inattendues |
| Tests d'API | Contrats, autorisations et comportements |
| IaC scanning | Configurations d'infrastructure |
| Container scanning | Paquets et vulnérabilités des images |

Ces contrôles sont complémentaires : aucun outil ne couvre toutes les catégories de risque.

## 6. SCA et sécurité des dépendances

Le SCA (*Software Composition Analysis*) analyse les dépendances directes et transitives.

Une dépendance directe est déclarée par l'application. Une dépendance transitive est introduite par une autre bibliothèque.

### 6.1. Pourquoi verrouiller les dépendances ?

Un fichier de dépendances qui accepte des versions très larges peut conduire à des builds différents au fil du temps.

Le verrouillage des dépendances améliore la reproductibilité.

Exemples :

```text
Python :
requirements.txt
poetry.lock

Node.js :
package.json
package-lock.json

Java :
pom.xml
fichiers de dépendances Maven ou Gradle
```

Le fichier exact dépend du gestionnaire utilisé.

Pour Python, par exemple :

```bash
python -m pip install -r requirements.txt
```

La présence d'un fichier de verrouillage n'élimine pas les vulnérabilités. Elle permet de mieux contrôler les versions effectivement installées.

### 6.2. Politique de vulnérabilités

Une politique mature peut tenir compte de :

- La sévérité technique.
- L'exploitabilité connue.
- La présence d'un exploit public.
- L'exposition du service.
- Les privilèges du composant.
- L'existence d'une version corrigée.
- L'importance métier du système.

Exemple de matrice de décision :

| Situation | Réponse possible |
|---|---|
| Secret actif exposé | Blocage immédiat et révocation |
| Vulnérabilité critique exploitable sur un service exposé | Blocage et correction prioritaire |
| Vulnérabilité élevée sans correctif disponible | Mesures compensatoires et exception documentée |
| Vulnérabilité faible dans un composant non exposé | Suivi et correction planifiée |
| Faux positif confirmé | Exception justifiée, limitée et réévaluée |

Ne pas utiliser la sévérité seule comme unique décision de risque.

## 7. Sécurité des images Docker

Cette section réutilise le cours Docker expert. L'objectif est de transformer les bonnes pratiques du Dockerfile en règles contrôlées automatiquement.

### 7.1. Réduire la surface d'attaque

Bonnes pratiques :

- Utiliser une image de base adaptée et maintenue.
- Réduire le nombre de paquets installés.
- Utiliser un build multi-stage lorsque pertinent.
- Exécuter l'application avec un utilisateur non privilégié.
- Ne pas incorporer de secrets dans l'image.
- Éviter les outils de compilation inutiles dans l'image finale.
- Reproduire les builds et surveiller les mises à jour.
- Scanner les images avant promotion.

Exemple :

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .

USER app

CMD ["python", "app.py"]
```

Cet exemple illustre quelques principes, mais ne constitue pas à lui seul un Dockerfile de production. Il faut notamment contrôler les versions, les dépendances, les permissions et le fonctionnement réel de l'application.

### 7.2. Scanner une image

Exemple avec Trivy, installé et configuré localement :

```bash
trivy image --severity HIGH,CRITICAL mon-application:dev
```

Pour analyser les configurations IaC :

```bash
trivy config terraform/
```

Les commandes et options disponibles peuvent varier selon la version. Les résultats doivent être conservés sous forme de rapports exploitables par la CI.

### 7.3. Politique de promotion

Ne pas promouvoir une image uniquement parce que sa compilation a réussi.

```text
Image construite
      |
      v
Scan de vulnérabilités
      |
      v
Évaluation de la politique
      |
      +----> Échec : correction ou exception autorisée
      |
      v
Image approuvée
      |
      v
Publication immuable
      |
      v
Déploiement par digest
```

Il est préférable de promouvoir exactement l'image validée plutôt que de reconstruire une image différente pour chaque environnement.

## 8. Sécurité des pipelines CI/CD

La pipeline constitue une cible de grande valeur : elle peut accéder au code, aux artefacts, aux secrets et parfois à la production.

### 8.1. Principe du moindre privilège

Chaque job doit recevoir uniquement les permissions nécessaires.

Exemples :

- Un job de test n'a pas besoin d'un accès en écriture au registre.
- Un job de scan ne devrait pas avoir de jeton d'administration Kubernetes.
- Un job de déploiement ne devrait pas avoir accès à tous les environnements.
- Un job exécutant du code provenant d'une contribution externe ne devrait pas recevoir automatiquement les secrets de production.

### 8.2. Risques des actions externes

Dans GitHub Actions, une référence comme :

```yaml
uses: organisation/action@v1
```

est lisible, mais une étiquette de version peut être déplacée selon les conditions du dépôt.

Pour un workflow sensible, privilégier les références à un SHA de commit complet, après vérification de la source et de la version.

```yaml
# Exemple illustratif : remplacer le SHA par celui
# de la version réellement vérifiée de l'action.
- uses: actions/checkout@<SHA_COMPLET_VERIFIE>
```

Le texte entre chevrons est un emplacement réservé, pas une valeur valide à utiliser telle quelle dans une pipeline. Une politique de dépendances de workflow peut aussi aider à gérer les mises à jour.

### 8.3. Séparer les jobs de confiance

Un schéma recommandé :

```text
Pull request externe
        |
        v
Tests sans secrets privilégiés
        |
        v
Revue et fusion approuvées
        |
        v
Build contrôlé
        |
        v
Publication avec permissions limitées
        |
        v
Déploiement soumis à approbation
```

Ne pas exposer des secrets privilégiés à du code non approuvé. Les déclencheurs de workflow, les permissions des jetons et les environnements protégés doivent être examinés ensemble.

## 9. Exemple GitHub Actions avec contrôles de sécurité

Le workflow suivant est une base pédagogique. Il lance des tests, un scan de secrets, une analyse de code et un contrôle IaC.

Les actions sont illustrées avec des références lisibles. Pour la production, vérifier les versions et remplacer les références externes par les SHA complets approuvés par l'organisation.

Fichier : `.github/workflows/security.yml`

```yaml
name: Security checks

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  tests:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Tests
        run: |
          python -m pip install -r requirements.txt
          python -m pytest

  secret-scan:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout history
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Detect secrets
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  sast:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Static analysis
        uses: returntocorp/semgrep-action@v1

  iac-scan:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Scan Terraform configuration
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          working_directory: terraform
```

### 9.1. Limites de cet exemple

Ce workflow n'est pas une politique de production prête à déployer telle quelle.

Avant adoption :

1. Vérifier que les actions existent toujours et que leurs versions sont appropriées.
2. Épingler les actions aux SHA vérifiés.
3. Vérifier les permissions réellement demandées par chaque action.
4. Contrôler la compatibilité des outils et des paramètres.
5. Définir les seuils d'échec et les formats de rapport.
6. Ajouter les contrôles de dépendances et d'images nécessaires.
7. Isoler les jobs non fiables.
8. Définir les règles de conservation des journaux et artefacts.

Une pipeline qui lance un scanner mais ignore ses rapports ne doit pas être considérée comme sécurisée.

## 10. Exemple GitLab CI avec scans de sécurité

GitLab propose des modèles de sécurité pour différents contrôles. Les fonctions exactes et leur disponibilité dépendent de la version, de la configuration et du niveau de service utilisé.

Fichier : `.gitlab-ci.yml`

```yaml
stages:
  - test
  - security

include:
  - template: Jobs/SAST.gitlab-ci.yml
  - template: Jobs/Secret-Detection.gitlab-ci.yml
  - template: Jobs/Dependency-Scanning.v2.gitlab-ci.yml

unit-tests:
  stage: test
  image: python:3.12-slim
  script:
    - python -m pip install -r requirements.txt
    - python -m pytest
```

### 10.1. Points à vérifier

- Les modèles inclus doivent être compatibles avec la version GitLab utilisée.
- Les jobs doivent être associés à des stages existants.
- Les rapports de sécurité doivent être conservés et consultés.
- Les scans doivent couvrir les fichiers et langages réellement présents.
- Les variables de CI doivent être protégées.
- Les runners doivent être isolés et maintenus.
- Les règles de fusion doivent exiger les contrôles jugés obligatoires.

Pour une chaîne de livraison complète, ajouter les scans d'images, les scans IaC et les validations de déploiement adaptés au projet.

### 10.2. GitHub Actions ou GitLab CI ?

Les deux plateformes peuvent participer à une démarche DevSecOps.

Le choix dépend notamment :

- De l'hébergement du code.
- Des fonctions de sécurité disponibles.
- Des runners et environnements existants.
- De l'intégration au registre.
- Des contraintes de gouvernance.
- Des coûts et des compétences de l'équipe.

Il n'est pas nécessaire de faire fonctionner les deux systèmes simultanément. Une organisation peut adopter une seule plateforme, ou utiliser les deux si une architecture clairement définie le justifie.

## 11. Gestion avancée des secrets

### 11.1. Ne jamais stocker les secrets dans le dépôt

Éviter notamment :

```yaml
env:
  DATABASE_PASSWORD: "mot-de-passe-en-dur"
```

Préférer un mécanisme de gestion de secrets adapté à la plateforme.

Cependant, utiliser une variable CI ne suffit pas à sécuriser un secret : un job autorisé à le lire peut potentiellement le transmettre ailleurs.

### 11.2. Utiliser des identités temporaires

Lorsque c'est possible, privilégier des identités temporaires et fédérées plutôt que des clés statiques de longue durée.

Exemple de principe avec une plateforme cloud :

```text
Job CI approuvé
      |
      v
Identité du workflow vérifiée
      |
      v
Fédération OIDC
      |
      v
Jeton temporaire à portée limitée
      |
      v
Accès au seul service nécessaire
```

Le fournisseur cloud doit vérifier les attributs d'identité et les conditions d'accès, notamment le dépôt, la branche, l'environnement et le workflow autorisé.

La présence d'OIDC ne rend pas automatiquement un workflow sûr : un workflow compromis peut encore abuser des permissions qui lui sont accordées.

### 11.3. Rotation et traçabilité

Pour chaque secret :

- Identifier son propriétaire.
- Définir sa durée de vie.
- Restreindre les systèmes autorisés à l'utiliser.
- Éviter son affichage dans les logs.
- Contrôler ses usages.
- Prévoir sa révocation.
- Documenter la procédure de rotation.

Les secrets de production ne doivent pas être accessibles à tous les jobs de développement.

## 12. Sécurité de Terraform et de l'IaC

Cette partie réutilise le cours Terraform intermédiaire et le cours IaC à grande échelle.

### 12.1. Risques IaC

Une configuration incorrecte peut créer :

- Un stockage accessible publiquement.
- Un pare-feu trop permissif.
- Un compte disposant de privilèges excessifs.
- Un chiffrement désactivé.
- Une journalisation insuffisante.
- Des secrets intégrés aux fichiers.
- Des ressources exposées inutilement.

### 12.2. Scanner avant le plan et l'application

Une séquence de contrôle peut être :

```text
Formatage
   |
   v
Validation Terraform
   |
   v
Scan IaC
   |
   v
Plan Terraform
   |
   v
Revue des changements
   |
   v
Application autorisée
```

Exemples de commandes :

```bash
terraform fmt -check -recursive
terraform validate
trivy config terraform/
terraform plan
```

Ces commandes doivent être exécutées dans le bon contexte et avec les fournisseurs et modules nécessaires. La validation syntaxique ne prouve pas qu'une infrastructure est sûre.

### 12.3. Policy as Code

Une politique de sécurité peut interdire certaines configurations avant le déploiement.

Exemples d'outils :

- Open Policy Agent (OPA).
- Conftest.
- Checkov.
- Trivy.
- Les mécanismes de politique natifs du fournisseur cloud.

Exemple de politique conceptuelle :

```text
RÈGLE : stockage sensible

SI une ressource contient des données sensibles
ET que l'accès public est activé
ALORS refuser le changement
SAUF exception approuvée et documentée
```

Une exception doit avoir un propriétaire, une justification, une date d'expiration et des mesures compensatoires.

### 12.4. Protéger le state Terraform

Le state peut contenir des informations sensibles.

Il faut :

- Utiliser un backend distant adapté.
- Activer le contrôle d'accès.
- Activer le chiffrement approprié.
- Protéger l'historique et les sauvegardes.
- Éviter de publier le state dans les artefacts accessibles à tous.
- Limiter les permissions de lecture et d'écriture.
- Séparer les environnements et leurs états.

Le state ne doit jamais être traité comme un fichier public ordinaire.

## 13. Sécurité d'Ansible et des configurations système

Le cours Ansible intermédiaire fournit les bases de l'automatisation. Le niveau DevSecOps ajoute des contrôles de conformité.

### 13.1. Bonnes pratiques

- Utiliser Ansible Vault ou un gestionnaire de secrets approprié.
- Limiter les privilèges des comptes d'automatisation.
- Contrôler les rôles et collections externes.
- Vérifier les changements avant application.
- Versionner les playbooks.
- Tester dans un environnement non productif.
- Produire des journaux de changement.
- Éviter les commandes arbitraires sans validation.

Exemple de vérification syntaxique :

```bash
ansible-playbook --syntax-check site.yml
```

Exemple de mode de simulation lorsque le module et le playbook le permettent :

```bash
ansible-playbook --check --diff site.yml
```

Le mode `--check` n'est pas une simulation parfaite de toutes les actions. Certains modules ne prennent pas entièrement en charge ce mode.

### 13.2. Détection de dérive

Un système sécurisé ne se limite pas à une configuration correcte au moment du déploiement.

Il faut aussi détecter les modifications non autorisées intervenues ensuite.

```text
Configuration attendue
        |
        v
État réel du serveur
        |
        v
Comparaison
        |
        +----> Conforme
        |
        +----> Dérive détectée
                    |
                    v
             Analyse et correction
```

La correction automatique doit être utilisée avec prudence : une dérive peut correspondre à un incident, à un changement d'urgence légitime ou à une intervention en cours.

## 14. Sécurité Kubernetes dans la chaîne DevSecOps

Cette section s'appuie sur le cours Kubernetes avancé et sécurité.

### 14.1. Contrôler les manifests avant le déploiement

Les manifests Kubernetes doivent être analysés avant d'être appliqués au cluster.

Exemples d'outils :

- kubeconform pour la validation de schémas.
- kube-linter pour certaines bonnes pratiques.
- Checkov ou Trivy pour des contrôles de configuration.
- OPA et Gatekeeper pour des politiques d'admission.

Une séquence de livraison :

```text
Manifestes YAML / Helm
          |
          v
Validation de syntaxe
          |
          v
Scan de sécurité
          |
          v
Rendu des templates Helm
          |
          v
Contrôle des politiques
          |
          v
Déploiement dans un environnement cible
```

Les valeurs Helm doivent être évaluées après rendu : un template peut produire une configuration dangereuse même si son fichier source paraît correct.

### 14.2. Exemple de Pod sécurisé

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-secure
  labels:
    app: app-secure
spec:
  automountServiceAccountToken: false

  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    seccompProfile:
      type: RuntimeDefault

  containers:
    - name: app
      image: registry.example.com/app@sha256:REMPLACER_PAR_LE_DIGEST_REEL

      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        privileged: false
        capabilities:
          drop:
            - ALL

      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "500m"
          memory: "256Mi"
```

Le digest d'image est un emplacement réservé : il doit être remplacé par un digest réel.

Ce manifeste doit aussi être adapté à l'application. Un système de fichiers en lecture seule peut nécessiter des volumes temporaires pour certains répertoires. Les UID, les droits sur les volumes et les contraintes de sécurité doivent être testés.

### 14.3. Politiques d'admission

Les contrôles en CI peuvent être contournés si une autre identité applique directement un manifeste au cluster.

Les politiques d'admission apportent une protection supplémentaire au moment de la création ou de la modification des ressources.

Elles peuvent notamment imposer :

- L'absence de conteneurs privilégiés.
- L'utilisation d'images approuvées.
- Des limites de ressources.
- Des contextes de sécurité conformes.
- Des restrictions sur les volumes.
- Des labels ou métadonnées obligatoires.

La validation en CI et le contrôle d'admission doivent se compléter.

## 15. Sécurité de la chaîne d'approvisionnement logicielle

La chaîne d'approvisionnement comprend le code, les dépendances, les outils de build, les runners, les images et les artefacts.

Un artefact peut être vulnérable, mais il peut aussi être remplacé par un artefact qui n'a jamais été validé.

### 15.1. SBOM

Une SBOM (*Software Bill of Materials*) décrit les composants d'un logiciel.

Elle peut notamment indiquer :

- Les paquets.
- Les versions.
- Les relations entre composants.
- Des identifiants utiles pour rechercher des vulnérabilités.

Deux formats courants sont CycloneDX et SPDX.

Une SBOM facilite les analyses, mais elle n'atteste pas à elle seule que le logiciel a été construit de façon sûre.

### 15.2. Provenance

La provenance décrit des informations sur la construction d'un artefact : source, paramètres de build, environnement ou processus utilisé.

Elle permet de répondre à des questions comme :

- Quel dépôt a produit cette image ?
- Quel commit a été utilisé ?
- Quelle pipeline a exécuté le build ?
- Quels éléments permettent de vérifier le processus de construction ?

La provenance doit être vérifiée et liée à l'artefact de manière fiable. Un fichier JSON non authentifié n'est pas une preuve suffisante.

### 15.3. Signature des artefacts

La signature permet de vérifier l'origine et l'intégrité d'un artefact, à condition de faire confiance à l'identité de signature et à la politique de vérification.

Exemple conceptuel :

```text
Image construite
      |
      v
Génération de SBOM
      |
      v
Attestation de provenance
      |
      v
Signature
      |
      v
Vérification de l'identité
      |
      v
Autorisation de déploiement
```

La signature ne garantit pas l'absence de vulnérabilité. Elle aide à vérifier que l'artefact correspond à ce qui a été approuvé.

### 15.4. Promotion d'artefacts

Une bonne pratique consiste à construire une seule fois, puis à promouvoir le même artefact à travers les environnements.

```text
Commit approuvé
      |
      v
Build contrôlé
      |
      v
Image + SBOM + provenance
      |
      v
Validation de sécurité
      |
      v
Environnement de test
      |
      v
Approbation de promotion
      |
      v
Production : même digest
```

Le déploiement par digest réduit l'ambiguïté liée aux tags modifiables.

## 16. Gestion des vulnérabilités et exceptions

### 16.1. Un processus de traitement

```text
Détection
   |
   v
Qualification
   |
   v
Évaluation du risque
   |
   +----> Risque inacceptable : blocage
   |
   +----> Risque tolérable temporairement
   |             |
   |             v
   |       Exception approuvée
   |
   v
Correction
   |
   v
Nouveau scan
   |
   v
Clôture avec preuve
```

### 16.2. Informations d'une exception

Toute exception importante doit inclure :

- La vulnérabilité ou la règle concernée.
- Le système et la version affectés.
- Le propriétaire responsable.
- La justification.
- L'évaluation du risque.
- Les mesures compensatoires.
- La date d'expiration.
- La personne ayant approuvé l'exception.
- La preuve de réévaluation.

Une exception sans expiration peut devenir une dérogation permanente non maîtrisée.

### 16.3. Délais de correction

Les délais doivent être définis par la politique interne, en fonction du risque métier et de la capacité de correction.

Un exemple de politique pourrait fixer un délai court pour les vulnérabilités critiques exploitables, un délai plus long pour les vulnérabilités élevées et un suivi planifié pour les vulnérabilités faibles.

Ces délais sont des choix de gouvernance, pas des valeurs universelles.

## 17. Déploiement progressif d'une stratégie DevSecOps

L'introduction de nombreux contrôles en une seule fois peut créer une accumulation d'échecs, de faux positifs et de contournements.

### Phase 1 : visibilité

- Inventorier les dépôts, pipelines, images et environnements.
- Activer les scans en mode informatif lorsque c'est adapté.
- Mesurer les résultats.
- Identifier les faux positifs.
- Définir les propriétaires.

### Phase 2 : règles minimales obligatoires

- Bloquer les secrets actifs exposés.
- Protéger les branches importantes.
- Exiger les tests critiques.
- Limiter les permissions des workflows.
- Protéger les identifiants de production.

### Phase 3 : contrôle de la chaîne d'approvisionnement

- Scanner les dépendances et images.
- Générer des SBOM.
- Produire des preuves de provenance.
- Signer et vérifier les artefacts.
- Promouvoir des artefacts immuables.

### Phase 4 : contrôle de l'infrastructure

- Scanner Terraform et Ansible.
- Valider les manifests Kubernetes.
- Appliquer des politiques d'admission.
- Vérifier les permissions et les configurations cloud.

### Phase 5 : amélioration continue

- Mesurer les délais de correction.
- Réviser les exceptions.
- Tester la réponse aux incidents.
- Améliorer les règles à partir des incidents réels.
- Automatiser les tâches répétitives sans supprimer la responsabilité humaine.

## 18. SRE et sécurité opérationnelle

La sécurité ne s'arrête pas à la mise en production. Elle doit s'intégrer à l'observabilité et à la gestion des incidents.

### 18.1. Indicateurs pertinents

Exemples :

- Délai médian de correction des vulnérabilités critiques.
- Pourcentage d'images déployées avec provenance vérifiable.
- Pourcentage de dépôts couverts par des scans de secrets.
- Nombre de secrets actifs exposés.
- Pourcentage de workflows utilisant des permissions minimales.
- Taux de conformité des déploiements Kubernetes.
- Nombre d'exceptions arrivées à expiration.
- Temps nécessaire pour révoquer un identifiant compromis.

### 18.2. Ne pas confondre activité et efficacité

Un grand nombre de scans exécutés ne prouve pas que l'organisation est plus sûre.

Il faut mesurer le résultat :

- Les vulnérabilités importantes sont-elles corrigées ?
- Les artefacts déployés sont-ils vérifiables ?
- Les secrets sont-ils correctement limités ?
- Les incidents sont-ils détectés rapidement ?
- Les mécanismes de récupération fonctionnent-ils ?

### 18.3. Incident de sécurité et retour d'expérience

Après un incident :

1. Contenir la menace.
2. Préserver les éléments de preuve.
3. Révoquer les identifiants concernés.
4. Déterminer les artefacts et systèmes affectés.
5. Restaurer un état de confiance.
6. Identifier la cause racine.
7. Ajouter des contrôles préventifs ou détectifs.
8. Vérifier leur efficacité.

Le retour d'expérience doit produire des actions suivies et attribuées, pas uniquement un rapport.

## 19. Atelier pratique : sécuriser une application de bout en bout

### 19.1. Objectif

Créer une chaîne de livraison qui valide une application, contrôle ses dépendances, analyse son image, vérifie ses manifests et prépare un déploiement contrôlé.

### 19.2. Structure du projet

```text
application/
├── src/
├── tests/
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── terraform/
│   └── main.tf
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── .github/
│   └── workflows/
│       └── security.yml
├── .gitlab-ci.yml
└── docs/
    └── security-policy.md
```

Les deux fichiers de pipeline sont des variantes pour deux plateformes. Ils ne doivent pas nécessairement être exécutés simultanément.

### 19.3. Étape 1 : tests

Exécuter les tests de l'application avant les scans coûteux.

```bash
python -m pytest
```

Le pipeline doit échouer si un test obligatoire échoue.

### 19.4. Étape 2 : contrôle des secrets

Installer et exécuter un outil adapté :

```bash
gitleaks git .
```

Si un secret est détecté, identifier s'il est réel, révoquer tout secret exposé et analyser l'historique si nécessaire.

### 19.5. Étape 3 : contrôle du code et des dépendances

Exécuter les scanners choisis par l'organisation.

Exemple :

```bash
semgrep scan --config auto .
```

Analyser les dépendances avec un outil adapté à l'écosystème. Conserver les rapports en tant qu'artefacts de pipeline.

### 19.6. Étape 4 : contrôle IaC

```bash
terraform fmt -check -recursive
terraform validate
trivy config terraform/
```

Les commandes Terraform nécessitent un répertoire valide et les fournisseurs appropriés. Les résultats du scan doivent être évalués selon une politique explicite.

### 19.7. Étape 5 : construction et analyse de l'image

```bash
docker build -t application:local .
trivy image --severity HIGH,CRITICAL application:local
```

Dans une pipeline réelle, utiliser un nom d'image déterministe et publier les rapports. Définir clairement quels résultats empêchent la promotion.

### 19.8. Étape 6 : validation Kubernetes

```bash
kubectl apply --dry-run=client -f k8s/
```

Cette commande réalise certaines validations locales, mais elle ne remplace pas un scan de sécurité, une validation complète des schémas ou les politiques d'admission du cluster.

Analyser les manifests avec un outil de sécurité dédié et tester le déploiement dans un cluster non productif.

### 19.9. Étape 7 : promotion contrôlée

Avant de déployer :

- Vérifier les résultats obligatoires.
- Vérifier l'identité de l'artefact.
- Contrôler les attestations attendues.
- Confirmer que le digest correspond à l'image approuvée.
- Utiliser une identité de déploiement limitée.
- Exiger une approbation pour les environnements sensibles.

### 19.10. Critères de réussite

L'atelier est réussi lorsque :

- Les tests sont exécutés automatiquement.
- Les secrets sont contrôlés.
- Le code et les dépendances sont analysés.
- L'image est scannée.
- L'IaC est contrôlée.
- Les manifests Kubernetes sont validés.
- Les résultats sont conservés.
- Les règles de blocage sont documentées.
- Les secrets de production ne sont pas accessibles aux jobs non fiables.
- Le déploiement utilise l'artefact qui a été validé.

## 20. Exercice corrigé : identifier les faiblesses d'une pipeline

Considérer le workflow suivant :

```yaml
name: Deploy

on:
  pull_request:
  push:
    branches:
      - main

permissions: write-all

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main
      - run: echo "${{ secrets.PROD_TOKEN }}"
      - run: ./deploy.sh
```

### Questions

1. Pourquoi `write-all` est-il problématique ?
2. Quel est le risque d'une référence comme `@main` ?
3. Pourquoi afficher le jeton est-il dangereux ?
4. Pourquoi le job ne devrait-il pas traiter toutes les pull requests de la même manière ?
5. Comment séparer validation et déploiement ?

### Correction

**1. Permissions excessives**

Un job compromis pourrait modifier des ressources pour lesquelles il possède des permissions inutiles. Les permissions doivent être définies au minimum nécessaire, au niveau global puis au niveau de chaque job.

**2. Référence mutable**

Une branche peut changer. Il faut vérifier l'action et épingler une version approuvée à un SHA complet lorsque cela est requis par la politique de sécurité.

**3. Exposition du jeton**

Les journaux peuvent être accessibles à d'autres personnes ou conservés longtemps. Le masquage automatique n'est pas une garantie suffisante. Ne jamais afficher un secret.

**4. Code non fiable**

Une pull request externe peut modifier les scripts exécutés. Un job de validation doit être séparé du job de déploiement privilégié.

**5. Séparation des responsabilités**

```text
Pull request
    |
    v
Tests et scans sans secrets de production
    |
    v
Fusion approuvée
    |
    v
Build et vérification
    |
    v
Environnement protégé
    |
    v
Déploiement avec identité limitée
```

## 21. Projet final : plateforme DevSecOps sécurisée

### 21.1. Scénario

Une équipe exploite une API Python conteneurisée, déployée sur Kubernetes. L'infrastructure est gérée avec Terraform et la configuration de certains serveurs avec Ansible.

L'objectif est de mettre en place une chaîne de livraison avec GitHub Actions ou GitLab CI.

### 21.2. Exigences fonctionnelles

La solution doit :

1. Exécuter les tests applicatifs.
2. Détecter les secrets dans le dépôt.
3. Analyser le code.
4. Analyser les dépendances.
5. Construire une image Docker sécurisée.
6. Scanner l'image.
7. Générer une SBOM.
8. Produire des preuves de provenance lorsque l'outillage le permet.
9. Analyser les fichiers Terraform.
10. Valider les manifests Kubernetes.
11. Publier les artefacts dans un registre contrôlé.
12. Déployer en utilisant un digest immuable.
13. Restreindre les permissions des workflows.
14. Protéger les secrets et les environnements.
15. Produire des journaux et rapports exploitables.
16. Définir une procédure de réponse à une compromission.

### 21.3. Exigences de sécurité

- Aucun secret ne doit être stocké dans le dépôt.
- Les runners doivent être isolés selon leur niveau de confiance.
- Les actions et dépendances de pipeline doivent être contrôlées.
- Les images doivent être analysées avant promotion.
- Les exceptions doivent être limitées et traçables.
- Les ressources Kubernetes doivent respecter la politique de sécurité.
- Les identités de déploiement doivent être limitées.
- Les procédures de rotation et de révocation doivent être documentées.

### 21.4. Livrables attendus

```text
projet-devsecops/
├── application/
├── tests/
├── Dockerfile
├── .dockerignore
├── .github/workflows/security.yml
├── .gitlab-ci.yml
├── terraform/
├── ansible/
├── k8s/
├── policies/
├── reports/
└── docs/
    ├── threat-model.md
    ├── security-policy.md
    ├── incident-response.md
    └── exceptions.md
```

Les rapports contenant des informations sensibles ne doivent pas être publiés dans un espace accessible à tous.

### 21.5. Grille d'évaluation

| Domaine | Points |
|---|---:|
| Tests et validation du code | 10 |
| Détection des secrets | 10 |
| Analyse des dépendances et du code | 15 |
| Sécurité Docker et scan d'image | 10 |
| Contrôle Terraform et Kubernetes | 15 |
| Gestion des permissions CI/CD | 15 |
| SBOM, provenance et intégrité | 10 |
| Gestion des vulnérabilités et exceptions | 5 |
| Documentation et réponse aux incidents | 10 |
| **Total** | **100** |

Un projet n'est pas validé uniquement parce que tous les jobs sont verts. Il faut démontrer que les contrôles détectent des défauts réels, que les échecs sont traités correctement et que les artefacts livrés sont ceux qui ont été approuvés.

## 22. Erreurs fréquentes à éviter

### Erreur 1 : ajouter beaucoup de scanners sans politique

**Conséquence :** accumulation de rapports que personne ne traite.

**Correction :** définir les seuils, les propriétaires, les délais et les conditions de blocage.

### Erreur 2 : exposer les secrets à tous les jobs

**Conséquence :** une dépendance compromise ou un script malveillant peut voler les identifiants.

**Correction :** isoler les jobs, réduire les permissions et réserver les secrets aux étapes autorisées.

### Erreur 3 : faire confiance uniquement au tag d'une image

**Conséquence :** le contenu correspondant au tag peut changer.

**Correction :** utiliser des digests immuables et vérifier l'origine de l'artefact.

### Erreur 4 : scanner seulement l'application

**Conséquence :** les images, l'IaC, les manifests et la chaîne de build restent des angles morts.

**Correction :** établir une couverture de sécurité par type d'actif.

### Erreur 5 : accepter les exceptions indéfiniment

**Conséquence :** les vulnérabilités connues deviennent une dette permanente.

**Correction :** imposer une justification, un propriétaire et une expiration.

### Erreur 6 : confondre conformité et sécurité réelle

**Conséquence :** un système peut satisfaire des contrôles formels tout en restant exposé à une menace non couverte.

**Correction :** combiner politiques, tests, surveillance, exercices d'incident et analyse du risque.

## 23. Checklist de mise en production

### Dépôts et code

- [ ] Branches protégées.
- [ ] Revues de code exigées.
- [ ] Fichiers de pipeline protégés.
- [ ] Détection des secrets active.
- [ ] Dépendances maîtrisées et mises à jour.

### Pipelines

- [ ] Permissions minimales.
- [ ] Actions externes contrôlées et versions vérifiées.
- [ ] Runners isolés.
- [ ] Jobs non fiables séparés des jobs privilégiés.
- [ ] Secrets limités aux environnements nécessaires.
- [ ] Journaux et rapports protégés.

### Images et artefacts

- [ ] Images maintenues et minimales.
- [ ] Utilisateur non privilégié.
- [ ] Scan de vulnérabilités.
- [ ] SBOM générée.
- [ ] Provenance vérifiée lorsque requise.
- [ ] Artefacts identifiés par digest.
- [ ] Promotion de l'artefact approuvé.

### Infrastructure et Kubernetes

- [ ] Terraform analysé.
- [ ] State protégé.
- [ ] Playbooks Ansible vérifiés.
- [ ] Manifests Kubernetes analysés.
- [ ] RBAC limité.
- [ ] Politiques d'admission actives.
- [ ] Conteneurs non privilégiés.
- [ ] Réseau et secrets correctement configurés.

### Exploitation

- [ ] Procédure de révocation des identifiants.
- [ ] Gestion des vulnérabilités documentée.
- [ ] Exceptions suivies.
- [ ] Alertes et journaux disponibles.
- [ ] Procédure de réponse aux incidents testée.
- [ ] Retour d'expérience après incident.

## 24. Glossaire

- **DevSecOps** : intégration de la sécurité dans le développement, la livraison et l'exploitation.
- **SAST** : analyse statique du code source.
- **DAST** : tests de sécurité sur une application en cours d'exécution.
- **SCA** : analyse des composants et dépendances logicielles.
- **SBOM** : inventaire des composants logiciels.
- **Provenance** : informations attestant comment un artefact a été produit.
- **Attestation** : déclaration structurée accompagnée de mécanismes permettant d'en vérifier l'origine et l'intégrité.
- **Digest** : identifiant cryptographique du contenu d'un artefact.
- **OIDC** : protocole d'identité permettant notamment la fédération d'identités dans certains environnements CI/CD.
- **Policy as Code** : règles de gouvernance exprimées et exécutées sous forme de code.
- **Runner** : machine ou environnement exécutant les jobs d'une pipeline.
- **SLSA** : cadre de niveaux et de pratiques visant à renforcer la chaîne d'approvisionnement logicielle.
- **Faux positif** : alerte qui ne correspond pas à une vulnérabilité réelle dans le contexte analysé.
- **Vulnérabilité exploitable** : faiblesse pouvant être utilisée dans des conditions données pour produire un impact.
- **Moindre privilège** : attribution des permissions minimales nécessaires.
- **Dérive de configuration** : différence entre la configuration attendue et l'état réel.
- **Exception de sécurité** : dérogation formellement approuvée à une règle, limitée et suivie.

## 25. Références officielles

### Cadres et recommandations

- NIST — Secure Software Development Framework (SSDF) : https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP — DevSecOps Guideline : https://owasp.org/www-project-devsecops-guideline/
- SLSA — Supply-chain Levels for Software Artifacts : https://slsa.dev/

### GitHub Actions

- Sécurisation de l'utilisation des workflows : https://docs.github.com/en/actions/reference/security/secure-use
- Gestion des permissions : https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication
- Environnements et secrets : https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions

### GitLab

- Sécurité des applications : https://docs.gitlab.com/user/application_security/
- Configuration des scanners : https://docs.gitlab.com/user/application_security/detect/security_configuration/
- Détection de secrets : https://docs.gitlab.com/user/application_security/secret_detection/

### Docker et chaîne d'approvisionnement

- Bonnes pratiques de build : https://docs.docker.com/build/building/best-practices/
- Secrets de build : https://docs.docker.com/build/building/secrets/
- Attestations de build : https://docs.docker.com/build/metadata/attestations/
- Docker Scout : https://docs.docker.com/scout/

### Kubernetes

- Pod Security Standards : https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Checklist de sécurité : https://kubernetes.io/docs/concepts/security/application-security-checklist/
- NetworkPolicy : https://kubernetes.io/docs/concepts/services-networking/network-policies/

### Terraform

- Documentation officielle : https://developer.hashicorp.com/terraform/docs
- Sécurité et bonnes pratiques : https://developer.hashicorp.com/terraform/tutorials/security

## Conclusion

Le niveau expert DevSecOps consiste à passer d'une collection d'outils à un système de livraison maîtrisé.

La chaîne doit établir une continuité entre le code approuvé, les dépendances analysées, l'image construite, les preuves de provenance, l'infrastructure validée et le déploiement réellement exécuté.

La qualité de cette démarche se mesure à sa capacité à prévenir les erreurs, limiter l'impact d'une compromission, détecter les écarts, corriger les vulnérabilités et démontrer que les logiciels mis en production sont ceux qui ont été contrôlés et approuvés.