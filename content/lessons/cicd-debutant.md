# Principes DevOps et cycle CI/CD

## 1. Présentation du cours

Le développement logiciel ne consiste pas uniquement à écrire du code. Une application doit être conçue, développée, testée, livrée, déployée, surveillée et maintenue dans le temps.

Dans une organisation traditionnelle, ces activités peuvent être réparties entre plusieurs équipes qui travaillent séparément. Les développeurs produisent le code, une équipe de test vérifie son fonctionnement et les administrateurs systèmes se chargent ensuite de son déploiement. Lorsque la communication est insuffisante, cette séparation peut provoquer des retards, des erreurs de configuration et des incidents en production.

**DevOps** propose une approche fondée sur la collaboration, l'automatisation, le partage des responsabilités et l'amélioration continue. Le cycle **CI/CD** constitue l'une des pratiques techniques qui facilitent cette approche : il permet d'automatiser une partie des étapes qui transforment une modification de code en une version testée et, selon les règles définies, déployable ou effectivement déployée.

Ce premier cours présente les fondations de DevOps et de CI/CD. Il prépare aux cours suivants, dans lesquels les pipelines, les outils d'automatisation, les artefacts, les environnements, la sécurité et les déploiements seront étudiés plus en profondeur.

### 1.1. Objectifs pédagogiques

À la fin de ce cours, vous devrez savoir :

- Définir DevOps et expliquer ses principaux objectifs.
- Distinguer la culture DevOps des outils qui peuvent la soutenir.
- Expliquer les notions d'intégration continue, de livraison continue et de déploiement continu.
- Décrire le cycle de vie d'une application moderne.
- Comprendre le rôle de Git, des tests automatisés et des pipelines.
- Identifier les principaux composants d'un pipeline CI/CD.
- Lire un fichier de pipeline simple.
- Comprendre les raisons pour lesquelles un pipeline réussit ou échoue.
- Appliquer quelques règles élémentaires de sécurité et de qualité.
- Construire un premier pipeline de tests avec GitHub Actions.

### 1.2. Prérequis

Il est recommandé de connaître quelques notions élémentaires :

- Les fichiers et les répertoires.
- Les commandes de base du terminal.
- Le rôle général d'une application.
- La différence entre un ordinateur local et un serveur.

Une connaissance préalable de Git ou de Python est utile, mais les exemples sont expliqués progressivement.

### 1.3. Environnement pédagogique

Le laboratoire pratique utilisera :

- Python pour illustrer un petit programme.
- Git pour suivre les modifications du code.
- GitHub pour héberger un dépôt de démonstration.
- GitHub Actions pour exécuter automatiquement les vérifications.

Les principes étudiés restent applicables à d'autres langages et plateformes, notamment Java, JavaScript, Go, .NET, GitLab CI/CD, Jenkins et Azure Pipelines.

## 2. Comprendre DevOps

### 2.1. Que signifie DevOps ?

Le terme DevOps est formé à partir de deux mots :

- **Dev**, pour Development : développement des applications.
- **Ops**, pour Operations : exploitation et fonctionnement opérationnel des applications et des systèmes.

DevOps cherche à rapprocher les personnes, les processus et les outils impliqués dans la création et l'exploitation d'un service numérique.

L'objectif n'est pas simplement de développer plus rapidement. Il s'agit de fournir de la valeur aux utilisateurs de manière plus fiable, plus fréquente et plus sécurisée.

Une équipe DevOps cherche notamment à :

- Réduire le délai entre une idée et sa mise à disposition.
- Détecter les défauts avant qu'ils affectent les utilisateurs.
- Rendre les opérations répétitives plus prévisibles grâce à l'automatisation.
- Réduire les erreurs humaines dans les procédures techniques.
- Faciliter le retour arrière en cas de problème.
- Mesurer le fonctionnement réel du service.
- Apprendre des incidents et améliorer les procédures.

### 2.2. DevOps n'est pas uniquement un outil

Git, Jenkins, GitHub Actions, Docker, Kubernetes et Ansible sont des outils qui peuvent participer à une démarche DevOps.

Cependant, installer ces outils ne suffit pas à adopter DevOps.

Une organisation peut posséder un système d'intégration continue sophistiqué tout en conservant des équipes cloisonnées, des procédures incompréhensibles et des mises en production très risquées.

À l'inverse, une petite équipe peut adopter les principes DevOps avec un dépôt Git, des tests automatisés, une documentation claire et une procédure de déploiement reproductible.

La démarche repose sur trois dimensions complémentaires.

| Dimension | Signification | Exemple |
|---|---|---|
| Personnes | Collaboration et responsabilité partagée | Les développeurs et les administrateurs analysent ensemble un incident. |
| Processus | Étapes explicites et reproductibles | Chaque modification doit être examinée et testée. |
| Technologie | Outils qui facilitent le travail | Un pipeline lance automatiquement les tests à chaque modification. |

La technologie facilite le travail, mais elle ne remplace ni la communication ni la réflexion collective.

### 2.3. Exemple d'une organisation sans approche DevOps

Imaginons une entreprise qui développe une application de gestion des commandes.

Le processus de livraison est le suivant :

1. Les développeurs écrivent du code pendant plusieurs semaines.
2. Ils transmettent manuellement une archive à l'équipe de test.
3. L'équipe de test découvre des erreurs et renvoie le code.
4. Les développeurs corrigent les erreurs.
5. Une nouvelle archive est préparée.
6. L'équipe système configure manuellement le serveur.
7. Le déploiement échoue à cause d'une différence entre les environnements.
8. Les équipes doivent rechercher les causes du problème pendant plusieurs heures.

Représentation simplifiée :

```text
Développement
     |
     v
Archive créée manuellement
     |
     v
Tests tardifs
     |
     v
Corrections répétées
     |
     v
Configuration manuelle
     |
     v
Déploiement risqué
     |
     v
Recherche des erreurs
```

Les difficultés principales sont les suivantes :

- Les erreurs sont détectées tardivement.
- Les modifications sont regroupées en lots trop importants.
- Les équipes échangent tardivement les informations.
- Les opérations manuelles sont difficiles à reproduire.
- Les résultats des tests peuvent dépendre de l'environnement utilisé.
- La responsabilité du fonctionnement global n'est pas clairement partagée.

Ce processus n'est pas nécessairement condamné à échouer, mais il présente davantage de sources de retard et de risques.

### 2.4. Exemple d'une organisation utilisant les principes DevOps

Avec une démarche DevOps, les développeurs et les équipes opérationnelles collaborent dès le début.

Les changements sont plus petits, leur historique est conservé dans Git et les vérifications sont automatisées.

```text
Besoin utilisateur
       |
       v
Planification partagée
       |
       v
Modification du code
       |
       v
Commit et dépôt Git
       |
       v
Pipeline automatisé
       |
       +-------------------------+
       |                         |
       v                         v
  Vérifications OK          Échec détecté
       |                         |
       v                         v
Version candidate           Analyse et correction
       |                         |
       v                         |
Déploiement contrôlé <-----------+
       |
       v
Surveillance du service
       |
       v
Retour d'expérience
```

L'équipe peut alors identifier plus rapidement les défauts, comprendre ce qui a changé et limiter l'impact d'une livraison défectueuse.

**Point essentiel :** DevOps vise à améliorer l'ensemble du flux de travail, depuis la compréhension du besoin jusqu'à l'exploitation du service.

## 3. Les principes fondamentaux de DevOps

### 3.1. La collaboration

Les équipes ne doivent pas travailler comme des services indépendants qui se transmettent un produit sans partager les informations nécessaires.

Les développeurs doivent comprendre les contraintes d'exploitation. Les administrateurs systèmes doivent comprendre les objectifs de l'application. Les personnes chargées de la sécurité doivent intervenir suffisamment tôt pour que leurs exigences soient prises en compte dès la conception.

La collaboration peut prendre plusieurs formes :

- Revues de code.
- Documentation partagée.
- Responsabilités clairement définies.
- Procédures d'incident communes.
- Réunions de retour d'expérience.
- Tableaux de suivi des tâches et des défauts.

Une bonne collaboration signifie également qu'un incident n'est pas automatiquement considéré comme la faute d'une personne. L'équipe recherche les causes techniques et organisationnelles qui ont permis au problème de se produire.

### 3.2. L'automatisation

Une opération répétée manuellement peut être longue, oublier certaines étapes ou produire des résultats différents selon la personne qui l'exécute.

L'automatisation permet de rendre ces opérations cohérentes.

Exemples :

| Opération | Sans automatisation | Avec automatisation |
|---|---|---|
| Tester le code | Lancer les tests manuellement | Le pipeline lance les tests à chaque modification. |
| Vérifier le formatage | Examiner les fichiers un par un | Un outil contrôle automatiquement les règles. |
| Construire un paquet | Suivre une procédure manuelle | Un script génère un artefact reproductible. |
| Déployer une version | Copier des fichiers sur un serveur | Un processus contrôlé déploie la version approuvée. |
| Surveiller un service | Consulter les journaux de temps en temps | Des métriques et des alertes signalent les anomalies. |

L'automatisation n'est pas synonyme d'absence de contrôle. Certaines opérations doivent rester conditionnées à une validation humaine, notamment lorsque leur impact est important.

Par ailleurs, automatiser une mauvaise procédure ne la rend pas bonne. Il faut d'abord comprendre et simplifier le processus, puis automatiser les étapes pertinentes.

### 3.3. L'amélioration continue

Un processus DevOps doit évoluer à partir des résultats réellement observés.

Après un incident, l'équipe peut examiner les questions suivantes :

- Pourquoi le défaut n'a-t-il pas été détecté avant le déploiement ?
- Le test nécessaire existe-t-il ?
- La procédure de restauration a-t-elle fonctionné ?
- Les alertes étaient-elles suffisamment pertinentes ?
- Une documentation manquait-elle ?
- Comment réduire le risque lors d'une prochaine livraison ?

L'objectif est de corriger le problème et de réduire les chances qu'il se reproduise.

### 3.4. Les changements de petite taille

Des changements fréquents et limités sont généralement plus faciles à examiner et à tester que des modifications volumineuses regroupées pendant plusieurs semaines.

Considérons deux situations.

**Situation A : gros changement**

Une équipe modifie 40 fichiers, ajoute une fonctionnalité importante et change plusieurs composants en même temps. Un test échoue. L'analyse doit examiner un grand nombre de possibilités.

**Situation B : petits changements**

L'équipe ajoute d'abord une fonction limitée, la teste, puis poursuit avec la modification suivante. Lorsqu'un test échoue, le nombre de causes possibles est plus réduit.

De petits changements ne garantissent pas l'absence de défauts. Ils permettent toutefois de mieux isoler les problèmes et de réduire l'ampleur d'un retour arrière.

### 3.5. Le partage des responsabilités

Chaque personne doit contribuer à la qualité du service, dans les limites de son rôle et de ses compétences.

Le développeur ne doit pas considérer son travail comme terminé uniquement parce que son programme fonctionne sur son ordinateur.

De même, l'équipe d'exploitation ne devrait pas découvrir au dernier moment des exigences techniques inconnues des développeurs.

La responsabilité collective implique notamment :

- De documenter les décisions importantes.
- De communiquer les risques.
- De tester les procédures.
- De conserver les informations utiles aux interventions.
- De mesurer la qualité du service après sa mise en production.

### 3.6. Les retours rapides

Plus un défaut est détecté tôt, plus il est généralement facile de le localiser et de le corriger.

Un test lancé immédiatement après une modification fournit un retour rapide au développeur.

Un défaut découvert plusieurs semaines après son introduction peut être plus difficile à analyser : la personne qui a écrit le code a pu changer de tâche, et d'autres modifications peuvent avoir masqué son origine.

Les pipelines CI/CD permettent d'obtenir des retours techniques réguliers et visibles par toute l'équipe.

## 4. Comprendre le cycle de vie d'une application

Le développement et l'exploitation peuvent être représentés sous la forme de plusieurs étapes liées entre elles.

### 4.1. Les grandes phases

```text
+-------------+
|   PLANIFIER |
+-------------+
       |
       v
+-------------+
| DÉVELOPPER  |
+-------------+
       |
       v
+-------------+
|   VÉRIFIER  |
+-------------+
       |
       v
+-------------+
|   CONSTRUIRE|
+-------------+
       |
       v
+-------------+
|   LIVRER    |
+-------------+
       |
       v
+-------------+
|   DÉPLOYER  |
+-------------+
       |
       v
+-------------+
|  EXPLOITER  |
+-------------+
       |
       v
+-------------+
|  SURVEILLER |
+-------------+
       |
       v
  RETOUR VERS
  LA PLANIFICATION
```

Dans la pratique, certaines étapes sont exécutées en parallèle ou se chevauchent. Le schéma représente les grandes responsabilités, pas une règle imposant qu'elles soient toujours strictement séquentielles.

### 4.2. Planifier

La planification définit ce que l'équipe doit réaliser et pourquoi.

Elle peut inclure :

- Les besoins des utilisateurs.
- Les fonctionnalités à développer.
- Les corrections à apporter.
- Les exigences de sécurité.
- Les contraintes de performance.
- Les critères permettant d'accepter une livraison.

Exemple : l'équipe doit ajouter une fonctionnalité qui calcule automatiquement le montant total d'une commande.

Un critère d'acceptation pourrait être :

> Pour une commande dont les articles coûtent respectivement 5 000 FCFA et 3 000 FCFA, le montant total doit être égal à 8 000 FCFA.

Un critère clair aide à concevoir les tests qui vérifieront la fonctionnalité.

### 4.3. Développer

Les développeurs implémentent la fonctionnalité dans un environnement de travail.

Ils peuvent créer une branche Git, modifier les fichiers, exécuter les tests localement et soumettre ensuite leurs changements pour examen.

Le développement inclut aussi la lecture du code existant, la correction des défauts et la documentation.

### 4.4. Vérifier

Cette phase sert à déterminer si les changements satisfont les exigences définies.

Elle peut comprendre :

- Des tests unitaires.
- Des tests d'intégration.
- Des contrôles de style.
- Des analyses statiques.
- Des contrôles de dépendances.
- Des vérifications de sécurité.
- Des tests fonctionnels.

Un contrôle échoué doit empêcher la progression lorsque celui-ci est défini comme obligatoire.

### 4.5. Construire

La construction transforme le code source et ses dépendances en un élément utilisable pour les étapes suivantes.

Selon le projet, il peut s'agir de :

- Fichiers compilés.
- Une archive.
- Un paquet logiciel.
- Un paquet installable.
- Une image de conteneur.
- Un ensemble de fichiers statiques.
- Une application empaquetée pour la distribution.

Le résultat est souvent appelé **artefact de build** ou **artefact de construction**.

Un projet Python très simple peut être exécuté sans construire d'archive. À l'inverse, une application Java ou une image Docker nécessite généralement une étape de construction explicite.

### 4.6. Livrer

La livraison consiste à rendre une version testée disponible pour un processus de déploiement.

L'artefact peut être placé dans un registre de paquets, un registre de conteneurs ou un dépôt prévu à cet effet.

À ce stade, une version peut être prête à être déployée sans être immédiatement mise à disposition des utilisateurs.

### 4.7. Déployer

Le déploiement installe ou active une version dans un environnement donné.

Les environnements peuvent inclure :

- **Développement** : travail quotidien des développeurs.
- **Test** : vérification du fonctionnement.
- **Préproduction** : validation dans des conditions proches de la production.
- **Production** : environnement qui sert les utilisateurs réels.

Chaque environnement doit être configuré de façon cohérente avec sa fonction.

Un déploiement doit aussi prévoir les aspects pratiques : configuration, accès, dépendances, vérifications après installation et stratégie de retour arrière.

### 4.8. Exploiter et surveiller

Après le déploiement, le service doit être maintenu en fonctionnement.

L'équipe surveille notamment :

- La disponibilité.
- Les erreurs.
- Les temps de réponse.
- L'utilisation du processeur et de la mémoire.
- Les journaux de l'application.
- Les indicateurs métier utiles.

La surveillance permet de détecter des problèmes que les tests effectués avant le déploiement ne peuvent pas nécessairement reproduire.

### 4.9. Apprendre

Les résultats de l'exploitation retournent vers les équipes de développement et de planification.

Un problème observé en production peut entraîner une correction du code, un nouveau test, une adaptation de la configuration ou une amélioration du processus de livraison.

DevOps repose donc sur une boucle d'apprentissage, et non sur une chaîne qui s'arrête au déploiement.

## 5. Comprendre CI, CD et CI/CD

Les termes CI/CD sont souvent utilisés ensemble, mais ils désignent des pratiques distinctes.

### 5.1. CI : Continuous Integration

L'intégration continue consiste à intégrer fréquemment les modifications de code et à automatiser des vérifications sur ces changements.

Le but est d'identifier tôt les problèmes d'intégration.

Un processus CI typique comprend les éléments suivants :

1. Un développeur modifie le code.
2. Il enregistre ses changements dans Git.
3. Il envoie les modifications vers un dépôt partagé.
4. Un pipeline est déclenché.
5. Le code est analysé et testé.
6. Le résultat est affiché.

Exemple :

```text
Modification du code
        |
        v
Commit Git
        |
        v
Push vers le dépôt
        |
        v
Déclenchement CI
        |
        v
Installation de l'environnement
        |
        v
Contrôles et tests
        |
   +----+----+
   |         |
   v         v
 SUCCÈS     ÉCHEC
   |         |
   v         v
Résultat    Rapport d'erreur
visible     à analyser
```

La CI ne garantit pas l'absence de défauts. Elle fournit des contrôles réguliers et reproductibles.

Un pipeline qui ne lance aucun test pertinent ou qui ignore systématiquement ses erreurs ne constitue pas une intégration continue efficace simplement parce qu'il se déclenche automatiquement.

### 5.2. CD : Continuous Delivery

Dans ce cours, **Continuous Delivery** désigne la livraison continue.

Le logiciel est construit et vérifié régulièrement de manière à obtenir une version prête à être déployée.

Le déploiement en production peut nécessiter une décision ou une approbation humaine.

Exemple :

```text
Code
 |
 v
Tests automatisés
 |
 v
Construction
 |
 v
Vérifications supplémentaires
 |
 v
Artefact prêt
 |
 v
Approbation de la livraison
 |
 v
Déploiement en production
```

Une entreprise peut donc livrer un logiciel de manière continue sans déployer automatiquement chaque changement en production.

### 5.3. CD : Continuous Deployment

**Continuous Deployment** désigne le déploiement continu.

Dans cette pratique, les modifications qui passent avec succès les contrôles obligatoires peuvent être déployées automatiquement en production, sans approbation manuelle individuelle de chaque version.

Cela suppose des contrôles de qualité adaptés, une stratégie de déploiement fiable, une surveillance opérationnelle et une possibilité de récupération en cas de problème.

Le déploiement continu n'est pas approprié à tous les systèmes ni à toutes les organisations. Certains environnements imposent des validations humaines, réglementaires ou opérationnelles.

### 5.4. Comparaison des trois pratiques

| Pratique | Objectif principal | Mise en production automatique ? |
|---|---|---|
| CI | Intégrer et vérifier fréquemment les changements. | Non, pas par définition. |
| Continuous Delivery | Garder une version testée prête à être déployée. | Pas nécessairement. Une approbation peut être requise. |
| Continuous Deployment | Déployer automatiquement les changements qui satisfont les contrôles. | Oui, selon les règles du pipeline. |

Attention : la lettre CD peut donc désigner **Continuous Delivery** ou **Continuous Deployment**. Il est important de préciser le sens lorsque l'on décrit une architecture.

### 5.5. Exemple concret de différence

Une équipe modifie le texte d'un bouton sur son site web.

Avec CI :

- Le code est envoyé vers le dépôt.
- Les tests s'exécutent.
- Le résultat confirme que les vérifications ont réussi.

Avec Continuous Delivery :

- Les tests réussissent.
- Une version est construite.
- L'artefact est disponible.
- Une personne autorisée valide la mise en production.

Avec Continuous Deployment :

- Les tests réussissent.
- La version est construite.
- Les vérifications requises sont satisfaites.
- Le pipeline déploie automatiquement la version en production.

La différence porte principalement sur le niveau d'automatisation du processus de livraison et de déploiement.

## 6. Le pipeline CI/CD

### 6.1. Définition

Un **pipeline CI/CD** est un ensemble organisé d'étapes automatisées qui vérifient, construisent, livrent et éventuellement déploient un logiciel.

Le pipeline décrit le processus à exécuter. Un moteur d'automatisation l'interprète et lance les tâches correspondantes sur une ou plusieurs machines d'exécution.

Un pipeline peut être déclenché par différents événements :

- Un push vers un dépôt Git.
- L'ouverture ou la mise à jour d'une pull request.
- La création d'une version ou d'un tag.
- Une exécution manuelle.
- Une planification.
- Un événement venant d'un autre système.

La nature du déclencheur détermine quand et dans quel contexte les tâches seront exécutées.

### 6.2. Les composants d'un pipeline

| Composant | Rôle | Exemple |
|---|---|---|
| Déclencheur | Détermine quand le pipeline démarre. | Push sur la branche principale. |
| Runner | Machine ou environnement qui exécute un travail. | Machine Linux hébergée par un fournisseur CI. |
| Job | Ensemble de tâches exécutées dans un contexte donné. | Job de tests unitaires. |
| Étape | Action réalisée dans un job. | Installer les dépendances. |
| Stage | Regroupement logique de jobs dans certains moteurs CI. | Test ou déploiement. |
| Artefact | Résultat conservé pour une utilisation ultérieure. | Archive construite. |
| Cache | Données réutilisables pour accélérer une exécution. | Cache de dépendances. |
| Variable | Valeur configurable accessible au pipeline. | Nom de l'environnement cible. |
| Secret | Information sensible utilisée de manière contrôlée. | Jeton d'authentification. |
| Environnement | Cible ou contexte dans lequel une version est livrée. | Préproduction ou production. |

Les outils ne reprennent pas tous exactement la même terminologie.

Par exemple, un job représente un ensemble d'étapes dans GitHub Actions. GitLab CI/CD utilise également des jobs et des stages, avec ses propres règles de configuration.

### 6.3. Stage, job et step : ne pas les confondre

Dans une configuration CI/CD, ces termes représentent des niveaux d'organisation différents, même si leur usage exact dépend de l'outil.

Considérons un pipeline composé de trois phases logiques.

```text
PIPELINE
   |
   +-- STAGE : verification
   |       |
   |       +-- JOB : controle_syntaxe
   |       |
   |       +-- JOB : tests_unitaires
   |
   +-- STAGE : construction
   |       |
   |       +-- JOB : creer_artefact
   |
   +-- STAGE : livraison
           |
           +-- JOB : publier_version
```

Dans une configuration qui utilise des stages séquentiels, l'échec d'un stage peut empêcher le démarrage des stages suivants.

En revanche, plusieurs jobs indépendants d'un même stage peuvent parfois s'exécuter en parallèle.

À l'intérieur d'un job, les steps sont généralement exécutés dans l'ordre défini.

### 6.4. Déroulement illustré d'un pipeline

```text
ÉVÉNEMENT : push Git
          |
          v
+------------------------+
| 1. Récupérer le code   |
+------------------------+
          |
          v
+------------------------+
| 2. Préparer Python     |
+------------------------+
          |
          v
+------------------------+
| 3. Vérifier la syntaxe |
+------------------------+
          |
          v
+------------------------+
| 4. Exécuter les tests  |
+------------------------+
          |
          v
     Tous réussis ?
       /       \
     NON        OUI
      |          |
      v          v
  Pipeline    Version validée
   en échec      pour cette étape
```

Une exécution en échec est utile si elle fournit des informations qui permettent d'identifier et de corriger le problème.

Le but n'est pas d'obtenir artificiellement un statut vert. Le but est de disposer d'un signal fiable sur la qualité du changement.

## 7. Le rôle de Git dans CI/CD

### 7.1. Pourquoi utiliser un contrôle de version ?

Git est un système de gestion de versions distribué.

Il conserve l'historique des modifications du code et aide plusieurs personnes à travailler sur un même projet.

Git permet notamment de :

- Conserver des commits décrivant les changements.
- Créer des branches pour séparer les travaux.
- Comparer des versions.
- Examiner les différences avant de les intégrer.
- Revenir à un état antérieur du dépôt.
- Collaborer à travers un dépôt partagé.

Git n'est pas, à lui seul, un moteur CI/CD. Il fournit toutefois des événements et des informations sur les changements que les outils CI/CD peuvent utiliser.

### 7.2. Commandes Git élémentaires

Vérifier si Git est installé :

```bash
git --version
```

Créer un répertoire et initialiser un dépôt :

```bash
mkdir mon-projet-cicd
cd mon-projet-cicd
git init
```

Consulter l'état du dépôt :

```bash
git status
```

Ajouter les fichiers à la prochaine validation :

```bash
git add .
```

Créer un commit :

```bash
git commit -m "Ajout de la première version"
```

Afficher l'historique :

```bash
git log --oneline
```

Renommer la branche courante en `main` :

```bash
git branch -M main
```

Ces commandes peuvent être utilisées pour préparer un projet local. Pour déclencher un pipeline hébergé, il faut ensuite envoyer le dépôt vers une plateforme distante et configurer le pipeline.

### 7.3. Le cycle d'une modification

```text
Fichiers de travail
       |
       v
Modification du code
       |
       v
git add
       |
       v
Zone de préparation
       |
       v
git commit
       |
       v
Historique local
       |
       v
git push
       |
       v
Dépôt distant
       |
       v
Pipeline CI/CD
```

Quelques distinctions importantes :

- `git add` prépare les modifications à enregistrer.
- `git commit` crée une nouvelle entrée dans l'historique local.
- `git push` envoie les commits vers un dépôt distant.
- Un dépôt distant peut déclencher le pipeline en fonction de l'événement et des règles configurées.

Le commit est donc différent du push. Créer un commit local ne signifie pas nécessairement qu'un pipeline hébergé sera lancé immédiatement.

### 7.4. Pourquoi les branches et les pull requests sont utiles

Une branche permet de développer une modification sans la fusionner immédiatement dans la branche principale.

Une pull request, aussi appelée merge request sur certaines plateformes, permet de proposer cette modification pour examen.

L'équipe peut alors :

- Lire le code.
- Discuter des changements.
- Demander des corrections.
- Vérifier le statut du pipeline.
- Exiger la réussite des contrôles avant la fusion.

Exemple de cycle :

```text
Branche main
     |
     v
Création d'une branche feature
     |
     v
Modifications
     |
     v
Push de la branche feature
     |
     v
Ouverture d'une pull request
     |
     v
Tests automatiques
     |
     v
Revue du code
     |
     v
Fusion si les règles sont satisfaites
```

La réussite des tests et l'approbation humaine répondent à des questions complémentaires. Les tests vérifient certains comportements techniques ; la revue permet aussi d'évaluer la lisibilité, la pertinence et les conséquences d'une modification.

## 8. Les tests automatisés dans CI/CD

### 8.1. Pourquoi automatiser les tests ?

Un test automatisé exécute des vérifications dont le résultat peut être déterminé sans intervention manuelle à chaque exécution.

Il peut vérifier, par exemple, qu'une fonction retourne le bon résultat ou qu'une API respecte un contrat attendu.

Les tests peuvent être réexécutés chaque fois que le code change.

Cela évite de dépendre uniquement de vérifications manuelles ponctuelles.

### 8.2. Les tests unitaires

Les tests unitaires vérifient le comportement d'une petite unité de code, souvent une fonction ou une méthode.

Exemple :

```python
def additionner(a, b):
    return a + b
```

Test correspondant :

```python
assert additionner(2, 3) == 5
```

Si la fonction retourne 6 au lieu de 5, le test échoue.

Ce type de test est généralement rapide et facile à exécuter dans un pipeline.

### 8.3. Les tests d'intégration

Les tests d'intégration vérifient que plusieurs composants fonctionnent correctement ensemble.

Par exemple, un test peut vérifier que :

- Une application se connecte à une base de données.
- Une requête est correctement exécutée.
- Le résultat est transformé comme prévu.
- La réponse produite correspond au contrat attendu.

Les tests d'intégration nécessitent parfois une base de données, un service externe ou une configuration spécifique.

### 8.4. Les tests fonctionnels

Les tests fonctionnels vérifient qu'une fonctionnalité répond à un besoin défini.

Exemple : lors de la création d'une commande, le montant total doit correspondre à la somme des articles et aux règles tarifaires applicables.

Ces tests peuvent être réalisés au niveau d'une API, d'un service ou d'une interface utilisateur.

### 8.5. Les analyses statiques et contrôles de style

Certains contrôles analysent le code sans exécuter l'application.

Ils peuvent rechercher :

- Des erreurs de syntaxe.
- Des constructions problématiques.
- Des violations de règles de style.
- Des problèmes susceptibles de créer des défauts.
- Certaines vulnérabilités connues.

Ces outils complètent les tests dynamiques. Aucun de ces mécanismes ne permet à lui seul de garantir qu'un programme est exempt de défauts.

### 8.6. La pyramide des tests

On représente souvent la stratégie de test sous la forme d'une pyramide.

```text
                 /\
                /  \
               / E2E\
              /------\
             /        \
            / Intégra- \
           /   tion     \
          /--------------\
         /                \
        /  Tests unitaires \
       /____________________\
```

En règle générale :

- Les tests unitaires sont nombreux et rapides.
- Les tests d'intégration vérifient les interactions entre composants.
- Les tests de bout en bout, ou E2E, couvrent des parcours complets, mais sont souvent plus lents et plus coûteux à maintenir.

Cette représentation est un guide de conception, pas une règle mathématique universelle. La répartition appropriée dépend de l'application.

### 8.7. Que faire quand un test échoue ?

Lorsqu'un test échoue, il ne faut pas automatiquement le supprimer ni le désactiver.

La démarche recommandée est la suivante :

1. Lire le message d'erreur.
2. Identifier le test qui a échoué.
3. Déterminer si l'erreur vient du code, du test ou de l'environnement.
4. Reproduire le problème localement si possible.
5. Corriger la cause.
6. Relancer les contrôles.
7. Ajouter un test supplémentaire si le défaut révèle un cas oublié.

Un test qui échoue de manière intermittente, sans changement fonctionnel identifiable, est parfois appelé un **test flaky**. Il faut rechercher sa cause plutôt que d'ignorer systématiquement ses échecs.

## 9. Les environnements et les versions livrables

### 9.1. Pourquoi plusieurs environnements ?

Les applications ne sont généralement pas développées et validées directement dans l'environnement de production.

On distingue habituellement plusieurs contextes.

| Environnement | Usage principal |
|---|---|
| Développement | Créer et modifier l'application. |
| Test | Exécuter les vérifications techniques et fonctionnelles. |
| Préproduction | Valider une version dans des conditions proches de la production. |
| Production | Fournir le service aux utilisateurs. |

Ces environnements peuvent avoir des tailles ou des configurations différentes.

Il est donc important d'identifier les écarts susceptibles de modifier le comportement de l'application.

### 9.2. L'artefact

Un artefact est un résultat identifiable produit par le processus de construction ou de publication.

Exemples :

- Une archive d'application.
- Un paquet Python.
- Un exécutable.
- Un fichier compilé.
- Une image Docker publiée dans un registre.
- Un paquet destiné à l'installation sur un serveur.

Un artefact ne doit pas être confondu avec le code source. Il s'agit d'un résultat produit à partir du code et des éléments nécessaires à sa construction.

### 9.3. Construire une fois, promouvoir plusieurs fois

Une bonne pratique consiste, lorsque l'architecture le permet, à construire un artefact identifié puis à promouvoir ce même artefact de l'environnement de test vers la préproduction et ensuite vers la production.

```text
Code versionné
      |
      v
Construction
      |
      v
Artefact identifié
      |
      v
Tests sur l'artefact
      |
      v
Déploiement en test
      |
      v
Validation en préproduction
      |
      v
Déploiement en production
```

Cela permet de réduire le risque de déployer en production un paquet différent de celui qui a été testé.

Cette pratique nécessite une gestion correcte de la configuration : les paramètres propres à chaque environnement doivent être injectés de façon contrôlée, sans modifier arbitrairement le contenu de l'artefact.

## 10. Une introduction aux stratégies de déploiement

Le cours débutant n'aborde pas en profondeur les déploiements avancés, mais il est utile d'en connaître les principes.

### 10.1. Déploiement direct

La nouvelle version remplace l'ancienne version sur l'environnement cible.

Cette méthode peut être simple, mais elle doit être accompagnée de vérifications et d'une stratégie de récupération adaptée.

### 10.2. Déploiement progressif

La nouvelle version est mise à disposition progressivement.

Une équipe peut commencer sur une partie des instances ou des utilisateurs, vérifier les indicateurs, puis augmenter la portée du déploiement.

Cette approche limite l'exposition initiale, à condition que le système soit conçu pour supporter cette transition.

### 10.3. Blue/Green

Deux environnements équivalents sont préparés :

- L'environnement Blue, qui sert actuellement les utilisateurs.
- L'environnement Green, qui reçoit la nouvelle version.

Après validation de Green, le trafic peut être basculé vers ce nouvel environnement.

```text
                 TRAFIC UTILISATEURS
                         |
                         v
                    +---------+
                    | Routage |
                    +---------+
                      /     \
                     /       \
                    v         v
             +----------+  +----------+
             |   BLUE   |  |  GREEN   |
             | Ancienne |  | Nouvelle |
             | version  |  | version  |
             +----------+  +----------+
```

Le retour vers l'ancien environnement dépend notamment de la compatibilité des données, des changements de schéma et de la configuration.

### 10.4. Canary

Une petite partie du trafic est dirigée vers la nouvelle version avant un déploiement plus large.

Les métriques, les erreurs et les retours utilisateurs sont examinés pour déterminer si la progression peut continuer.

Blue/Green et Canary sont deux stratégies distinctes. Elles nécessitent un système de routage, des contrôles opérationnels et une planification appropriée.

### 10.5. Retour arrière

Le retour arrière, ou rollback, permet de revenir à une version antérieure ou à un état opérationnel connu.

Il doit être envisagé avant la mise en production. Une simple restauration des fichiers n'est pas toujours suffisante, notamment si la nouvelle version modifie les données ou les schémas de base de données.

Un déploiement peut être automatisé sans qu'un retour arrière soit automatiquement sûr. La procédure de récupération doit être conçue et testée séparément.

## 11. Les fondations de la sécurité dans CI/CD

La rapidité ne doit pas se faire au détriment de la sécurité.

Un pipeline peut accéder au code source, à des paquets, à des environnements et parfois à des systèmes de production. Il doit donc être protégé au même titre que les autres éléments de l'infrastructure.

### 11.1. Ne pas placer les secrets dans le code

Un secret peut être :

- Un mot de passe.
- Une clé privée.
- Un jeton d'accès.
- Une clé d'API.
- Un identifiant d'accès à un registre.
- Un identifiant d'accès à un environnement de production.

Un secret ne doit pas être placé en clair dans le dépôt Git.

Exemple à éviter :

```python
MOT_DE_PASSE_BASE = "MotDePasseSuperSecret123"
```

Même si le code est destiné à un environnement de test, cette pratique est dangereuse. Les dépôts sont copiés, partagés, sauvegardés et parfois rendus publics.

Le pipeline doit utiliser un mécanisme adapté de stockage et d'injection des secrets.

Si un secret est accidentellement publié, le supprimer du fichier ne suffit pas toujours. Il faut généralement le révoquer ou le renouveler, puis traiter les éventuelles copies conservées dans l'historique.

### 11.2. Appliquer le principe du moindre privilège

Un pipeline ne devrait disposer que des autorisations nécessaires à son travail.

Par exemple :

- Un job de tests n'a généralement pas besoin d'un accès administrateur à la production.
- Un job qui lit le code n'a pas besoin de pouvoir supprimer tous les dépôts.
- Une tâche de publication doit disposer de droits limités à l'opération concernée.

Des autorisations trop larges augmentent les conséquences possibles en cas d'erreur ou de compromission.

### 11.3. Protéger les branches et les livraisons

Les règles de protection peuvent empêcher une fusion tant que les contrôles requis ne sont pas réussis.

Elles peuvent aussi exiger une revue de code ou une approbation.

Pour les environnements sensibles, des protections supplémentaires peuvent être mises en place :

- Autorisation explicite du déploiement.
- Séparation entre les droits de test et de production.
- Journalisation des opérations.
- Restrictions sur les branches et les personnes autorisées.
- Vérification des dépendances et des actions externes utilisées par le pipeline.

### 11.4. Comprendre les dépendances externes

Un pipeline utilise souvent des bibliothèques, des images de base et des actions réutilisables.

Une dépendance compromise ou modifiée de manière inattendue peut introduire un risque.

Les bonnes pratiques comprennent notamment :

- Utiliser des dépendances provenant de sources fiables.
- Examiner les mises à jour importantes.
- Conserver un inventaire des composants lorsque cela est approprié.
- Appliquer des contrôles de vulnérabilités.
- Épingler les dépendances critiques selon les règles de la plateforme.
- Maintenir les composants et outils de construction à jour.

### 11.5. Le rôle de DevSecOps

DevSecOps étend les principes de collaboration et d'automatisation de DevOps aux activités de sécurité.

La sécurité est prise en compte lors de la conception, du développement, des tests, de la livraison et de l'exploitation.

Elle ne doit pas être limitée à une vérification finale effectuée après que toutes les décisions techniques ont déjà été prises.

## 12. Mesurer l'efficacité du processus

Un pipeline qui s'exécute très rapidement n'est pas nécessairement un bon pipeline. Il faut également savoir s'il aide l'équipe à fournir des changements fiables et à récupérer rapidement en cas de problème.

Les mesures doivent servir à identifier les blocages et à guider l'amélioration collective.

### 12.1. Le délai de livraison d'un changement

Il mesure le temps nécessaire pour faire passer un changement du point de départ défini par la méthode de mesure jusqu'à sa mise en production.

Il ne faut pas confondre ce délai avec le temps effectivement passé à écrire le code.

Un changement peut être terminé techniquement, mais rester bloqué pendant plusieurs jours en attente de revue, de test ou d'autorisation.

### 12.2. La fréquence des déploiements

Elle indique à quelle fréquence une application ou un service est déployé.

La fréquence doit être interprétée avec le contexte du système et de l'organisation.

Un grand nombre de déploiements n'est pas automatiquement synonyme de qualité si ceux-ci provoquent de nombreux incidents.

### 12.3. Le taux d'échec des changements

Cette mesure s'intéresse à la proportion des déploiements qui provoquent des problèmes nécessitant une intervention, par exemple une correction urgente ou un retour arrière.

Elle aide à comprendre la stabilité des livraisons.

### 12.4. Le temps de récupération après un déploiement défaillant

Cette mesure s'intéresse au temps nécessaire pour récupérer après un déploiement qui a provoqué un problème.

Une équipe doit non seulement réduire les risques d'échec, mais également améliorer sa capacité à limiter les conséquences lorsqu'un échec survient.

### 12.5. Le taux de retravail lié aux déploiements

Le retravail peut notamment correspondre à des déploiements imprévus réalisés pour corriger un problème visible par les utilisateurs.

Cette mesure permet de comprendre la charge imprévue provoquée par des problèmes de livraison.

Les définitions précises et les conventions de calcul doivent être fixées avant de comparer des résultats.

### 12.6. Les mesures DORA

Les recherches DORA utilisent cinq mesures principales de performance de livraison logicielle :

| Mesure | Question à laquelle elle répond |
|---|---|
| Délai de livraison des changements | Combien de temps faut-il pour livrer un changement en production ? |
| Fréquence des déploiements | À quelle fréquence le service est-il déployé ? |
| Temps de récupération après un déploiement défaillant | Combien de temps faut-il pour récupérer après ce type d'échec ? |
| Taux d'échec des changements | Quelle proportion des déploiements provoque un échec nécessitant une intervention ? |
| Taux de retravail des déploiements | Quelle part des déploiements correspond à du travail imprévu destiné à corriger des problèmes ? |

Ces mesures permettent d'observer le débit de livraison et l'instabilité du processus.

Il ne faut pas utiliser une mesure isolée pour établir un classement simpliste des personnes ou des équipes. Les résultats doivent être interprétés selon la nature du service, les contraintes et les tendances observées.

## 13. Laboratoire pratique : créer son premier pipeline CI

Cette partie met en œuvre un petit projet Python. Le pipeline vérifiera la syntaxe et exécutera des tests unitaires à chaque push sur la branche `main`, ainsi qu'à chaque pull request ciblant cette branche.

Ce premier laboratoire est volontairement limité : il met en place une intégration continue et ne déploie pas l'application en production.

### 13.1. Préparer le projet

Créer cette structure de répertoires et de fichiers :

```text
mon-projet-cicd/
|
+-- app.py
|
+-- tests/
|   |
|   +-- test_app.py
|
+-- .github/
    |
    +-- workflows/
        |
        +-- ci.yml
```

Le dossier `.github/workflows/` est l'emplacement où GitHub Actions recherche les fichiers définissant les workflows d'un dépôt.

### 13.2. Créer le programme

Dans `app.py`, ajouter le contenu suivant :

```python
def additionner(a, b):
    """Retourne la somme de deux nombres."""
    return a + b


def diviser(a, b):
    """Divise a par b et refuse une division par zéro."""
    if b == 0:
        raise ValueError("Le diviseur ne peut pas être zéro.")

    return a / b
```

Ce programme contient deux fonctions :

- `additionner` retourne la somme de deux valeurs.
- `diviser` retourne le quotient de deux valeurs et lève une exception si le diviseur est nul.

Le cas de division par zéro est intentionnellement traité. Un logiciel doit définir un comportement approprié pour les situations invalides, et pas uniquement pour les cas habituels.

### 13.3. Créer les tests unitaires

Dans `tests/test_app.py`, écrire :

```python
import unittest

from app import additionner, diviser


class TestApplication(unittest.TestCase):

    def test_additionner_deux_entiers(self):
        self.assertEqual(additionner(2, 3), 5)

    def test_additionner_valeurs_negatives(self):
        self.assertEqual(additionner(-2, -3), -5)

    def test_diviser_deux_nombres(self):
        self.assertEqual(diviser(10, 2), 5)

    def test_diviser_par_zero(self):
        with self.assertRaises(ValueError):
            diviser(10, 0)


if __name__ == "__main__":
    unittest.main()
```

Le framework `unittest` est fourni avec Python. Aucun paquet externe n'est nécessaire pour exécuter ces tests.

Le fichier vérifie quatre situations :

1. L'addition de deux entiers positifs.
2. L'addition de deux entiers négatifs.
3. Une division normale.
4. Le refus d'une division par zéro.

### 13.4. Tester localement avant le pipeline

Ouvrir un terminal dans le répertoire `mon-projet-cicd`.

Vérifier Python :

```bash
python --version
```

Sur certains systèmes, l'exécutable s'appelle `python3` :

```bash
python3 --version
```

Exécuter les tests :

```bash
python -m unittest discover -s tests -v
```

Ou, si nécessaire :

```bash
python3 -m unittest discover -s tests -v
```

Le résultat doit indiquer que les quatre tests ont réussi.

Le nombre exact de messages affichés peut varier selon la version de Python, mais la dernière ligne doit signaler une exécution réussie des tests.

Si une erreur apparaît, ne passez pas directement au pipeline. Corrigez d'abord les problèmes locaux, puis relancez les tests.

### 13.5. Créer le workflow GitHub Actions

Créer le fichier `.github/workflows/ci.yml` avec le contenu suivant :

```yaml
name: CI Python

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
    name: Vérifications Python
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v7

      - name: Installer Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Vérifier la syntaxe Python
        run: python -m compileall -q app.py tests

      - name: Exécuter les tests unitaires
        run: python -m unittest discover -s tests -v
```

Ce fichier définit un workflow simple.

Les références d'actions sont celles utilisées dans cet exemple. Dans un projet réel, il faut vérifier leurs versions, suivre les recommandations de sécurité de la plateforme et, lorsqu'il convient de garantir une référence immuable, épingler les actions à un SHA de commit complet et vérifié.

### 13.6. Comprendre chaque partie du workflow

**Nom du workflow**

```yaml
name: CI Python
```

Ce nom permet d'identifier le workflow dans l'interface de GitHub.

**Déclencheurs**

```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
```

Le pipeline se déclenche lorsqu'un push cible la branche `main` et lorsqu'une pull request cible cette même branche.

Ces règles déterminent le moment où le workflow doit être exécuté. Elles ne signifient pas que toute modification locale déclenche immédiatement le pipeline : les événements doivent parvenir à GitHub.

**Autorisations**

```yaml
permissions:
  contents: read
```

Cette configuration limite les autorisations explicites du jeton fourni au workflow pour l'accès au contenu du dépôt.

Elle illustre le principe du moindre privilège. Si le pipeline doit plus tard publier une version ou modifier un autre système, les autorisations requises devront être évaluées et ajoutées de manière ciblée.

**Job et runner**

```yaml
jobs:
  tests:
    name: Vérifications Python
    runs-on: ubuntu-latest
```

Le workflow possède un job nommé `tests`.

`runs-on` indique l'environnement de calcul utilisé pour l'exécution. Ici, il s'agit d'un runner Linux hébergé, désigné par `ubuntu-latest`.

**Récupération du dépôt**

```yaml
- name: Récupérer le dépôt
  uses: actions/checkout@v7
```

Cette action permet au job de récupérer le code du dépôt afin que les commandes suivantes puissent accéder aux fichiers du projet.

**Installation de Python**

```yaml
- name: Installer Python
  uses: actions/setup-python@v7
  with:
    python-version: "3.12"
```

Le job configure la version de Python utilisée pour les étapes suivantes.

Fixer la version de l'interpréteur permet d'obtenir un environnement de test plus prévisible. Il faut choisir une version réellement compatible avec le projet.

**Vérification de la syntaxe**

```yaml
- name: Vérifier la syntaxe Python
  run: python -m compileall -q app.py tests
```

Cette commande vérifie que les fichiers Python concernés peuvent être compilés en bytecode. Elle peut détecter des erreurs de syntaxe, mais ne prouve pas que le programme est fonctionnel.

**Exécution des tests**

```yaml
- name: Exécuter les tests unitaires
  run: python -m unittest discover -s tests -v
```

Cette étape exécute les tests unitaires.

Si une assertion échoue ou qu'une exception inattendue survient, la commande retourne normalement un code de sortie non nul. GitHub Actions marque alors l'étape en échec et, par défaut, ne poursuit pas les étapes suivantes du job.

### 13.7. Préparer le dépôt Git

Si le projet n'est pas encore un dépôt Git :

```bash
git init
git branch -M main
git add app.py tests/test_app.py .github/workflows/ci.yml
git commit -m "Création du premier pipeline CI"
```

Créer ensuite un dépôt distant sur GitHub, puis associer ce dépôt local à l'adresse fournie par la plateforme.

Exemple de commande, à adapter à l'adresse réelle de votre dépôt :

```bash
git remote add origin https://github.com/UTILISATEUR/mon-projet-cicd.git
```

Envoyer les changements :

```bash
git push -u origin main
```

Les droits d'accès et l'authentification doivent être configurés correctement. Ne placez pas de mot de passe ou de jeton d'accès directement dans les commandes ou les fichiers du projet.

Si vous travaillez sur un dépôt déjà initialisé et associé à GitHub, ne répétez pas les étapes de création. Ajoutez simplement les nouveaux fichiers, créez un commit puis poussez-le.

### 13.8. Observer l'exécution

Après le push :

1. Ouvrir le dépôt sur GitHub.
2. Accéder à l'onglet **Actions**.
3. Sélectionner le workflow `CI Python`.
4. Ouvrir l'exécution correspondant au push.
5. Examiner le job `Vérifications Python`.
6. Consulter les détails de chaque étape.

Lorsque toutes les vérifications réussissent, l'exécution doit apparaître comme réussie.

Si le workflow n'apparaît pas, vérifier notamment :

- Que le fichier se trouve exactement dans `.github/workflows/ci.yml`.
- Que la branche ciblée correspond à `main`.
- Que le fichier YAML respecte l'indentation attendue.
- Que le dépôt autorise l'exécution des workflows concernés.
- Que le push a effectivement été envoyé au dépôt distant.

### 13.9. Provoquer volontairement un échec

Pour comprendre le fonctionnement du pipeline, modifier temporairement la fonction `additionner` :

```python
def additionner(a, b):
    return a - b
```

Relancer les tests en local.

Le test qui vérifie que `additionner(2, 3)` retourne `5` doit maintenant échouer.

Envoyer cette modification vers le dépôt si vous souhaitez observer l'échec dans GitHub Actions.

Le pipeline doit signaler l'échec du test. Ce résultat est attendu : il montre que le contrôle détecte un comportement incorrect.

Remettre ensuite la fonction dans son état correct :

```python
def additionner(a, b):
    return a + b
```

Relancer les tests, créer un nouveau commit puis envoyer la correction.

Le pipeline devrait à nouveau réussir.

**Ce que l'exercice démontre :** un pipeline utile n'est pas un mécanisme destiné à afficher une réussite à chaque exécution. C'est un système de contrôle qui doit distinguer les modifications conformes des modifications qui nécessitent une correction.

## 14. Les erreurs fréquentes lors des premiers projets CI/CD

### 14.1. Confondre un commit et un déploiement

Un commit conserve une modification dans l'historique Git.

Il ne signifie pas que l'application a été testée, livrée ou déployée.

Ces opérations peuvent être déclenchées à la suite d'un commit ou d'un push, mais chacune reste une étape distincte.

### 14.2. Déployer directement chaque modification en production

L'automatisation du déploiement ne garantit pas que le déploiement soit sûr.

Il faut tenir compte des tests, des autorisations, de l'impact des changements, des procédures de récupération et de la surveillance.

Un système d'apprentissage peut utiliser un environnement de test pour s'exercer. Un système qui sert de vrais utilisateurs doit avoir des contrôles adaptés à son niveau de risque.

### 14.3. Ne jamais tester localement

Le pipeline est utile, mais il ne devrait pas être le seul endroit où les développeurs exécutent les tests.

Les vérifications locales accélèrent le retour d'information et évitent de pousser des erreurs simples qui auraient pu être détectées avant l'envoi.

### 14.4. Stocker des secrets dans le dépôt

Les secrets ne doivent pas être intégrés au code source ni affichés dans les journaux des jobs.

Leur exposition peut permettre un accès non autorisé aux ressources visées, même si le dépôt est ensuite rendu privé ou si le fichier contenant le secret est supprimé.

### 14.5. Ignorer un test en échec

Désactiver un test pour faire disparaître une erreur peut masquer un défaut réel.

Il faut déterminer si l'échec vient du produit, du test ou de l'environnement, puis traiter la cause.

### 14.6. Ne jamais vérifier le comportement en production

Une application peut passer ses tests et rencontrer malgré tout des problèmes réels.

Le comportement opérationnel dépend aussi de la configuration, des données, des dépendances et de la charge.

Les métriques, les journaux, les alertes et les procédures de récupération complètent donc le pipeline.

### 14.7. Considérer les outils comme une solution complète

Un outil ne remplace pas la définition des règles de livraison.

Le pipeline doit répondre à des questions concrètes :

- Quels changements doivent déclencher les tests ?
- Quels contrôles sont obligatoires ?
- Quel résultat permet de poursuivre ?
- Qui peut autoriser une livraison sensible ?
- Où les artefacts sont-ils conservés ?
- Comment récupérer après un déploiement défectueux ?

Sans réponses claires, les automatisations risquent d'être incohérentes ou difficiles à maintenir.

## 15. Bonnes pratiques à retenir

Pour un projet débutant, appliquer progressivement les règles suivantes.

### Pratique 1 : conserver un historique compréhensible

Utiliser des messages de commit qui décrivent les changements.

Exemple :

```bash
git commit -m "Ajout des tests de division"
```

Un bon historique facilite les revues, les comparaisons et les analyses de problèmes.

### Pratique 2 : intégrer régulièrement les modifications

Éviter d'attendre trop longtemps avant de partager les changements.

Les petites modifications sont généralement plus simples à examiner et à tester.

### Pratique 3 : automatiser les contrôles importants

Commencer par les tests qui apportent une réelle valeur au projet.

Il est préférable d'avoir quelques tests fiables plutôt qu'un grand nombre de tests peu pertinents dont les résultats sont ignorés.

### Pratique 4 : rendre les échecs visibles

Conserver les journaux nécessaires à l'analyse et rendre le statut du pipeline visible aux personnes concernées.

Un échec doit déclencher une investigation appropriée, pas être masqué par une configuration qui le transforme systématiquement en succès.

### Pratique 5 : limiter les autorisations

Les jobs doivent avoir les droits nécessaires, mais pas davantage.

Séparer autant que possible les tâches de test des opérations qui modifient des environnements sensibles.

### Pratique 6 : contrôler les dépendances

Les dépendances sont une partie du logiciel livré.

Il faut savoir lesquelles sont utilisées, comment elles sont mises à jour et comment leurs vulnérabilités sont traitées.

### Pratique 7 : préparer les déploiements avant de les automatiser

Un processus doit être compréhensible, testé et documenté avant de devenir une opération automatique à fort impact.

Commencer par un environnement de test est souvent une manière adaptée d'apprendre.

### Pratique 8 : mesurer et améliorer le processus

Observer les temps d'attente, les échecs de tests, la fréquence des livraisons et les incidents.

Utiliser ces informations pour améliorer le processus collectif plutôt que pour sanctionner arbitrairement des personnes.

## 16. Exercices de compréhension

### Exercice 1 : distinguer DevOps d'un outil

Une entreprise installe GitHub Actions. Les développeurs continuent toutefois à transmettre manuellement les archives aux administrateurs et les équipes ne partagent pas les informations sur les incidents.

**Question :** peut-on considérer que l'entreprise a pleinement adopté DevOps ?

### Exercice 2 : identifier CI, Continuous Delivery et Continuous Deployment

Associer chaque scénario à la pratique correspondante.

A. Chaque push déclenche les tests et affiche les résultats.

B. Chaque modification validée produit un artefact prêt à être déployé, mais la mise en production nécessite une approbation.

C. Chaque modification qui passe les contrôles obligatoires est automatiquement déployée en production.

### Exercice 3 : repérer les composants d'un pipeline

Considérons le processus suivant :

```text
Push Git
  |
  v
Runner Linux
  |
  v
Installation de Python
  |
  v
Exécution des tests
  |
  v
Rapport de résultats
```

Identifier :

1. Le déclencheur.
2. Le runner.
3. Une étape.
4. Le contrôle qui détermine si les tests ont réussi.

### Exercice 4 : analyser un échec

Un développeur modifie une fonction. Le pipeline échoue ensuite sur un test qui réussissait auparavant.

Citer au moins quatre vérifications à réaliser avant de décider de modifier ou de supprimer le test.

### Exercice 5 : sécuriser un pipeline

Une équipe place un jeton d'accès à la production dans un fichier `config.py`, puis envoie ce fichier dans un dépôt partagé.

Identifier le risque et expliquer la première mesure de sécurité à prendre si le jeton a été exposé.

### Exercice 6 : comprendre les environnements

Une nouvelle version fonctionne sur l'ordinateur du développeur, mais échoue en préproduction à cause d'une variable de configuration manquante.

Expliquer pourquoi cette situation ne signifie pas nécessairement que le code applicatif est incorrect et proposer une amélioration du processus.

### Exercice 7 : les mesures de livraison

Deux équipes déploient chacune dix fois par semaine.

L'équipe A subit régulièrement des incidents nécessitant des corrections urgentes. L'équipe B connaît moins d'échecs et récupère plus rapidement lorsqu'un problème se produit.

Pourquoi la fréquence seule ne suffit-elle pas à comparer la performance de livraison de ces équipes ?

## 17. Corrigés des exercices

### Corrigé 1

Non. L'entreprise a adopté un outil d'automatisation, mais cela ne prouve pas qu'elle a transformé ses pratiques de collaboration.

Elle doit aussi améliorer le partage des responsabilités, l'automatisation du processus de livraison, la circulation de l'information et l'apprentissage collectif après les incidents.

### Corrigé 2

- A : intégration continue, ou CI.
- B : livraison continue, ou Continuous Delivery.
- C : déploiement continu, ou Continuous Deployment.

Dans B, une version peut être prête sans être automatiquement mise en production.

Dans C, le déploiement en production est une conséquence automatique de la réussite des contrôles définis.

### Corrigé 3

1. Le déclencheur est le push Git.
2. Le runner est l'environnement Linux qui exécute le job.
3. L'installation de Python est une étape du job.
4. Le résultat de la commande de tests détermine si ce contrôle a réussi. Dans un pipeline classique, une commande qui retourne un code d'échec fait échouer l'étape.

### Corrigé 4

Il faut notamment :

- Lire le message d'erreur et identifier le test concerné.
- Examiner les modifications introduites depuis la dernière réussite.
- Reproduire l'échec localement.
- Vérifier si le résultat attendu est toujours conforme à la spécification.
- Examiner les éventuelles différences d'environnement.
- Déterminer si le test est incorrect ou si le code a introduit une régression.

Supprimer un test uniquement parce qu'il échoue empêcherait de détecter certains défauts.

### Corrigé 5

Le jeton peut être récupéré par des personnes ayant accès au dépôt ou à ses copies.

Il faut révoquer ou renouveler le jeton exposé, puis examiner les accès et les opérations potentiellement réalisés avec celui-ci. Le secret doit ensuite être stocké dans un mécanisme adapté, avec des droits limités et sans être écrit en clair dans le code.

### Corrigé 6

Les environnements peuvent différer par leurs variables, leurs dépendances et leurs paramètres.

L'équipe devrait documenter les variables requises, vérifier leur présence dans les environnements concernés et automatiser autant que possible la validation de la configuration. Les valeurs sensibles doivent être fournies par un mécanisme sécurisé.

### Corrigé 7

La fréquence décrit une partie du débit de livraison, mais pas la stabilité ni le coût des échecs.

Il faut également examiner le taux d'échec des changements, le temps de récupération et le retravail causé par les incidents. Deux équipes qui déploient aussi souvent peuvent avoir des résultats opérationnels très différents.

## 18. Projet de fin de niveau : automatiser la validation d'une petite application

### 18.1. Objectif

Mettre en place un dépôt Git contenant une petite application Python et un pipeline CI capable de contrôler la syntaxe et d'exécuter des tests unitaires automatiquement.

Le projet doit démontrer que vous comprenez le cycle de base entre la modification du code, le dépôt Git, le pipeline et la correction d'un défaut.

### 18.2. Travail demandé

Réaliser les tâches suivantes :

1. Créer un dépôt Git pour le projet.
2. Écrire deux fonctions Python : une addition et une division.
3. Écrire au moins quatre tests unitaires.
4. Exécuter les tests sur l'environnement local.
5. Créer un workflow GitHub Actions.
6. Configurer le workflow pour se lancer sur les événements prévus.
7. Envoyer le projet vers le dépôt distant.
8. Vérifier l'exécution du workflow.
9. Provoquer un échec volontaire.
10. Corriger le défaut et observer une exécution réussie.

### 18.3. Critères de réussite

Le projet est considéré comme réussi lorsque :

- L'historique Git contient les modifications du projet.
- Les fonctions répondent aux cas prévus.
- Les tests sont exécutables localement.
- Le workflow se trouve dans le répertoire attendu.
- Le pipeline se déclenche lors des événements configurés.
- L'échec d'un test provoque l'échec du job.
- Une correction du code permet aux tests de réussir.
- Aucun secret sensible n'est enregistré dans le dépôt.
- Les étapes de mise en place sont documentées.

### 18.4. Améliorations facultatives

Une fois le projet fonctionnel, il est possible de :

- Ajouter des tests pour les nombres décimaux.
- Vérifier le comportement lorsque les arguments sont invalides.
- Ajouter un contrôle de style.
- Ajouter une matrice de tests sur plusieurs versions de Python compatibles.
- Conserver un rapport de test comme artefact du pipeline.
- Créer une branche de fonctionnalité et une pull request.
- Ajouter une étape de construction d'un paquet.
- Publier un artefact vers un registre de test.
- Ajouter des vérifications de dépendances dans une évolution ultérieure.

Chaque amélioration doit répondre à un besoin précis. L'objectif n'est pas de complexifier le pipeline sans raison, mais de renforcer progressivement la qualité et la reproductibilité du processus.

## 19. Glossaire essentiel

**Agile :** approche de développement privilégiant l'adaptation, la collaboration et les retours réguliers.

**Artefact :** résultat produit par une étape de construction ou de publication, utilisable par les étapes suivantes.

**Branche :** ligne de développement distincte dans un dépôt Git.

**Build :** opération qui construit un résultat logiciel à partir du code et de ses dépendances.

**CI :** Continuous Integration, ou intégration continue.

**CD :** Continuous Delivery ou Continuous Deployment, selon le contexte.

**Commit :** enregistrement d'un ensemble de changements dans l'historique Git.

**Déploiement :** opération qui installe ou active une version dans un environnement cible.

**DevOps :** approche favorisant la collaboration, l'automatisation, le partage des responsabilités et l'amélioration continue sur le cycle de vie logiciel.

**DevSecOps :** intégration continue des préoccupations de sécurité dans les pratiques DevOps.

**Environnement :** contexte d'exécution et de configuration d'une application, par exemple le développement, le test ou la production.

**Intégration :** assemblage et vérification de modifications ou de composants logiciels.

**Job :** ensemble de tâches exécutées dans un contexte d'exécution défini par l'outil CI/CD.

**Pipeline :** processus organisé d'étapes automatisées de vérification, de construction, de livraison ou de déploiement.

**Préproduction :** environnement de validation précédant généralement la production.

**Production :** environnement qui fournit le service aux utilisateurs réels.

**Pull request :** demande d'intégration de modifications permettant notamment la revue et les contrôles automatisés.

**Rollback :** retour vers une version ou un état antérieur après un problème.

**Runner :** environnement de calcul qui exécute les travaux du pipeline.

**Stage :** regroupement logique de jobs dans les outils CI/CD qui utilisent cette notion.

**Test unitaire :** test portant sur une petite unité de code.

**Workflow :** ensemble de règles et de travaux automatisés déclenchés par certains événements, notamment dans GitHub Actions.

## 20. Références officielles pour aller plus loin

Les ressources suivantes permettent d'approfondir les concepts présentés dans ce cours.

### DevOps et cycle de vie logiciel

- Microsoft Learn — Présentation de DevOps : https://learn.microsoft.com/en-us/devops/what-is-devops
- Microsoft Learn — Centre de ressources DevOps : https://learn.microsoft.com/en-us/devops/
- Microsoft Learn — Formation d'introduction à DevOps : https://learn.microsoft.com/en-us/training/modules/discover-devops/

### GitHub Actions et pipelines

- GitHub Docs — Comprendre GitHub Actions : https://docs.github.com/en/actions/get-started/understanding-github-actions
- GitHub Docs — Présentation des workflows : https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows
- GitHub Docs — Documentation générale de GitHub Actions : https://docs.github.com/en/actions
- GitHub Docs — Sécurité de GitHub Actions : https://docs.github.com/en/actions/how-tos/secure-your-work

### GitLab CI/CD

- GitLab Docs — Présentation des pipelines CI/CD : https://docs.gitlab.com/ci/pipelines/

### Mesure et amélioration continue

- DORA — Mesures de performance de livraison logicielle : https://dora.dev/guides/dora-metrics/
- DORA — Capacité de livraison continue : https://dora.dev/capabilities/continuous-delivery/

### Python et tests

- Documentation Python — Module `unittest` : https://docs.python.org/3/library/unittest.html
- Documentation Python — `compileall` : https://docs.python.org/3/library/compileall.html

Les documentations officielles constituent les références à consulter lorsque la syntaxe, les fonctions ou les versions des outils évoluent.

## 21. Synthèse du niveau débutant

Les notions fondamentales à retenir sont les suivantes.

**DevOps** est une démarche de travail qui rapproche le développement et l'exploitation. Elle s'appuie sur la collaboration, l'automatisation, les retours rapides, la mesure et l'amélioration continue.

**CI/CD** regroupe des pratiques d'automatisation de la livraison logicielle. La CI permet d'intégrer et de vérifier fréquemment les changements. La livraison continue maintient des versions testées prêtes à être déployées. Le déploiement continu automatise également leur mise en production lorsque les contrôles définis sont satisfaits.

**Git** assure le suivi des modifications et fournit l'historique nécessaire au travail collaboratif. Le dépôt distant permet aux outils CI/CD de réagir aux événements configurés.

**Le pipeline** organise et exécute des contrôles reproductibles. Il comporte des déclencheurs, des jobs, des étapes et parfois des stages, ainsi que des résultats qui peuvent être transmis aux étapes suivantes.

**Les tests automatisés** réduisent le risque de réintroduire des défauts et fournissent des résultats réguliers. Ils doivent être pertinents, fiables et exécutés dans des conditions adaptées.

**La sécurité** doit être intégrée dès le départ : secrets protégés, droits limités, dépendances contrôlées et déploiements encadrés.

Enfin, **un pipeline réussi n'est pas une garantie absolue de qualité**. Il prouve uniquement que les contrôles exécutés ont satisfait leurs règles. La qualité réelle dépend aussi de la pertinence des tests, de la conception du logiciel, de la sécurité, de l'exploitation et des retours des utilisateurs.

La prochaine étape de cette progression consistera à approfondir la conception de pipelines CI/CD, la définition de jobs et de stages, les artefacts, les conditions d'exécution et l'organisation des workflows dans un projet plus complet.