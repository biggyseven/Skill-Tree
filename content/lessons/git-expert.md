# Stratégies de branching

## 1. Présentation du cours

Dans les cours précédents, vous avez appris à utiliser Git, à créer des branches, à fusionner des modifications, à effectuer des rebasages et à récupérer un historique après une erreur.

À ce stade, la question n'est plus seulement de savoir comment créer une branche ou résoudre un conflit. La véritable question devient : **comment organiser les branches pour que toute une équipe puisse développer, tester, livrer et maintenir un logiciel sans bloquer les autres contributeurs ?**

Cette organisation constitue une **stratégie de branching**, c'est-à-dire un ensemble de règles qui définissent comment les branches sont créées, nommées, mises à jour, fusionnées, protégées et supprimées pendant le cycle de vie d'un projet.

Une stratégie de branching mal adaptée peut provoquer des divergences importantes entre les branches, des conflits répétés, des corrections oubliées dans certaines versions, des déploiements difficiles à reproduire et des délais de livraison excessifs.

À l'inverse, une stratégie bien choisie facilite la collaboration, améliore la traçabilité, réduit les risques d'intégration et permet d'adapter le processus de livraison aux contraintes du produit.

Il n'existe pas une stratégie universellement idéale. Une application web déployée plusieurs fois par jour n'a pas nécessairement besoin du même modèle qu'un logiciel industriel publié deux fois par an, qu'une bibliothèque utilisée par plusieurs milliers de projets ou qu'une application conservant plusieurs versions en production.

Ce cours présente les principaux modèles de branching, leurs différences, leurs limites et les méthodes permettant de les appliquer dans un contexte professionnel.

### 1.1. Objectifs pédagogiques

À la fin de ce cours, vous devrez être capable de :

- Concevoir une stratégie de branches adaptée à un projet.
- Distinguer GitHub Flow, GitFlow, Trunk-Based Development et les variantes de GitLab Flow.
- Déterminer quand utiliser des branches de fonctionnalité, de release, de maintenance ou de correction urgente.
- Définir une politique de création et de suppression des branches.
- Choisir entre merge commit, squash merge et rebase selon les objectifs du projet.
- Organiser les revues de code et les contrôles automatiques.
- Protéger les branches principales et les branches de publication.
- Gérer les hotfixes sans perdre de corrections dans les autres versions maintenues.
- Organiser les branches de release pour plusieurs versions en production.
- Comprendre les limites des branches représentant directement les environnements.
- Intégrer les tags, les versions et les pipelines CI/CD dans le processus de branching.
- Détecter les problèmes d'une stratégie de branches devenue trop complexe.
- Faire évoluer une stratégie existante sans perturber l'ensemble de l'équipe.
- Définir des règles de contribution et des indicateurs permettant de mesurer l'efficacité du modèle choisi.

### 1.2. Prérequis

Ce cours suppose que vous connaissez déjà :

- Les commits et les références Git.
- Les branches locales et distantes.
- `git merge` et `git rebase`.
- Les conflits et leur résolution.
- `git cherry-pick`.
- Les tags.
- `git fetch`, `git pull` et `git push`.
- Les bases d'un pipeline CI/CD.
- Les principes d'une revue de code.

Les exemples utilisent les commandes Git standards et des scénarios compatibles avec des plateformes comme GitHub et GitLab.

### 1.3. Principe fondamental

Une stratégie de branching n'est pas une collection de noms de branches. C'est une politique de circulation des modifications.

Elle doit répondre à ces questions :

1. Où commence une modification ?
2. Où le travail est-il intégré ?
3. Quels contrôles sont obligatoires avant l'intégration ?
4. Quelle branche représente la version de référence ?
5. Comment préparer et identifier une version livrable ?
6. Comment corriger rapidement un défaut en production ?
7. Comment reporter une correction vers les versions encore maintenues ?
8. Qui peut fusionner ou publier une modification ?
9. Comment revenir sur une livraison défectueuse ?
10. Quelles branches doivent être conservées et lesquelles doivent être supprimées ?

Si ces questions n'ont pas de réponses explicites, les branches risquent de devenir des espaces de travail indépendants qui se désynchronisent progressivement.

## 2. Comprendre les rôles des branches

Avant d'étudier les modèles de branching, il faut distinguer les principaux rôles possibles d'une branche.

### 2.1. Branche principale

La branche principale porte généralement le nom `main`.

Dans certains dépôts anciens, elle s'appelle encore `master`.

Elle représente habituellement le point central d'intégration du projet.

Selon la stratégie adoptée, elle peut représenter :

- Le code considéré comme stable.
- La version destinée à la production.
- Le code intégré qui peut être livré à tout moment.
- Le point de départ des branches de fonctionnalité.

Dans un modèle GitFlow classique, `main` représente les versions officielles de production.

Dans un modèle de type Trunk-Based Development, la branche principale reçoit fréquemment les changements validés et reste continuellement dans un état acceptable pour une livraison.

Ces rôles ne sont donc pas strictement identiques.

### 2.2. Branche de développement

Une branche appelée `develop` existe notamment dans GitFlow.

Elle sert de branche d'intégration pour les fonctionnalités qui préparent une version future.

```text
main
 |
 | Versions de production
 |
 +----------------------------------+

develop
 |
 | Intégration du prochain ensemble
 | de fonctionnalités
 |
 +----------------------------------+
```

Cette branche n'est pas indispensable dans toutes les stratégies.

De nombreux projets utilisent uniquement `main` comme branche d'intégration et créent des branches de courte durée pour les changements.

### 2.3. Branche de fonctionnalité

Une branche de fonctionnalité isole le développement d'un changement.

Exemples :

```text
feature/authentification
feature/export-csv
feature/api-supervision
feature/cache-redis
```

Elle permet de travailler sans intégrer immédiatement le changement dans la branche principale.

Sa durée doit rester cohérente avec le modèle adopté.

Dans un flux de travail rapide, elle peut durer quelques heures ou quelques jours. Dans des modèles avec de longues phases de développement, elle peut rester ouverte beaucoup plus longtemps, au prix d'un risque accru de divergence.

### 2.4. Branche de correction

Une branche de correction sert à résoudre un défaut.

Exemples :

```text
fix/validation-ip
fix/timeout-api
fix/calcul-taxe
```

Elle se distingue éventuellement d'un hotfix par son contexte.

Une correction ordinaire peut être intégrée dans le cycle normal de développement. Un hotfix vise généralement une version de production qui nécessite une intervention urgente.

### 2.5. Branche de release

Une branche de release sert à stabiliser une version avant sa publication ou à maintenir une version préparée pour livraison.

Exemple :

```text
release/2.4.0
```

Selon la stratégie, elle peut être :

- Créée temporairement pour finaliser les tests.
- Utilisée pour les corrections de stabilisation.
- Conservée comme branche de maintenance si la version continue d'être supportée.

Il faut distinguer une branche temporaire de préparation de version d'une branche de maintenance qui reste active pendant plusieurs mois.

### 2.6. Branche de hotfix

Un hotfix est une correction urgente destinée à une version déjà publiée.

Exemple :

```text
hotfix/2.4.1
```

Dans un modèle GitFlow classique, cette branche part de `main`, puisque la correction vise une version de production.

La correction doit ensuite être propagée dans les autres lignes de développement concernées, notamment `develop` lorsqu'elle existe.

Dans d'autres stratégies, la correction peut être réalisée sur une branche de maintenance ou directement à partir de la dernière version de production.

### 2.7. Branche de maintenance

Un projet peut maintenir plusieurs versions en production.

Exemple :

```text
support/2.3
support/2.4
main
```

Chaque branche de maintenance correspond à une ligne de version ayant ses propres contraintes.

Une correction compatible avec la version 2.3 peut nécessiter une implémentation différente sur la version 2.4.

Cette situation apparaît notamment dans les bibliothèques logicielles, les logiciels installés chez des clients et les produits qui garantissent plusieurs années de support.

## 3. La stratégie de branching doit correspondre au mode de livraison

La stratégie de branches et la stratégie de livraison sont liées, mais elles ne sont pas identiques.

Le branching détermine comment les modifications évoluent dans le dépôt.

La livraison détermine comment une version est construite, validée et mise à disposition.

Une branche peut déclencher un pipeline CI, une construction d'artefact ou un déploiement, mais le nom de la branche ne suffit pas à garantir la qualité du changement.

### 3.1. Projet web à livraison fréquente

Un service web peut utiliser un modèle simple :

```text
feature/*
     |
     v
Pull request
     |
     v
Tests + revue
     |
     v
main
     |
     v
Construction et déploiement
```

Le dépôt n'a pas nécessairement besoin d'une branche `develop` ou de branches permanentes par environnement.

### 3.2. Logiciel publié selon un calendrier

Un logiciel livré à des dates planifiées peut utiliser plusieurs phases :

```text
Développement
      |
      v
Intégration des fonctionnalités
      |
      v
Branche de release
      |
      v
Stabilisation et validation
      |
      v
Publication
      |
      v
Maintenance de la version
```

Le besoin de stabilisation, de validation réglementaire ou de support de plusieurs versions peut justifier des branches supplémentaires.

### 3.3. Projet à exigences réglementaires

Un système soumis à des validations strictes peut nécessiter :

- Des approbations formelles.
- Des contrôles techniques obligatoires.
- Une traçabilité des commits.
- Des tags de publication.
- Des artefacts identifiés.
- Des validations avant déploiement.
- Une procédure documentée de correction et de retour arrière.

Cela ne signifie pas nécessairement qu'il faut multiplier les branches.

Les exigences de contrôle peuvent être mises en œuvre par les règles de revue, les contrôles CI/CD, la gestion des versions et l'approbation des déploiements, sans créer une branche permanente pour chaque étape administrative.

### 3.4. Principe de simplicité

Une branche permanente doit correspondre à une responsabilité réelle.

Si une branche existe uniquement parce que l'organisation a toujours fonctionné de cette manière, examinez si elle apporte encore une valeur mesurable.

Une stratégie simple, bien contrôlée et comprise par tous est souvent préférable à une architecture de branches compliquée dont personne ne maîtrise entièrement les règles.

## 4. Vue d'ensemble des principales stratégies

Les principaux modèles abordés dans ce cours sont :

1. GitHub Flow.
2. Trunk-Based Development.
3. GitFlow.
4. GitLab Flow et ses variantes.
5. Stratégies avec branches de release et de maintenance.
6. Stratégies utilisant une branche par environnement.

Ils ne répondent pas tous aux mêmes besoins.

### 4.1. Tableau comparatif

| Critère | GitHub Flow | Trunk-Based Development | GitFlow | Branches de release et maintenance | Branches par environnement |
|---|---|---|---|---|---|
| Branche centrale | `main` | Trunk, généralement `main` | `main` et `develop` | Trunk et branches de version | Une ou plusieurs branches représentant des environnements |
| Branches de fonctionnalité | Courtes | Très courtes ou intégration directe contrôlée | Généralement séparées de `develop` | Selon le flux choisi | Généralement présentes |
| Fréquence d'intégration | Régulière | Très fréquente | Dépend des branches et du cycle de release | Régulière, avec stabilisation des versions | Dépend du processus de promotion |
| Releases planifiées | Possibles | Possibles | Bien adaptées aux versions planifiées | Très adaptées | Possible, mais nécessite des règles strictes |
| Plusieurs versions en production | Possible avec une stratégie complémentaire | Possible avec des branches de maintenance | Possible avec support adapté | Adapté | Possible, mais ne résout pas à lui seul le support des versions |
| Complexité opérationnelle | Faible à moyenne | Moyenne sur le plan technique et organisationnel | Plus élevée | Variable | Peut devenir élevée |
| Besoin d'une CI fiable | Élevé | Très élevé | Élevé | Élevé | Très élevé |
| Cas typique | Application web ou service | Produit évoluant rapidement | Produit à releases structurées | Logiciel versionné sur la durée | Processus d'environnements très spécifique |

La bonne stratégie dépend de l'architecture du produit, du risque opérationnel, de la fréquence de livraison et de la capacité de l'équipe à automatiser les contrôles.

## 5. GitHub Flow

### 5.1. Principe

GitHub Flow est un modèle de collaboration centré sur une branche principale et des branches de courte durée.

Dans sa forme courante :

1. Le développeur part de `main`.
2. Il crée une branche pour son changement.
3. Il envoie cette branche vers le dépôt distant.
4. Il ouvre une pull request.
5. Les autres personnes examinent les changements.
6. Les contrôles automatiques sont exécutés.
7. La pull request est fusionnée lorsque les règles sont satisfaites.
8. Le système peut ensuite déployer la version selon les règles de livraison.

Représentation :

```text
                       BRANCHE PRINCIPALE
A---B---C---M---F---G-------------------------- main
         \   /
          D-E
         feature/api
```

La branche `feature/api` contient les modifications D et E.

Le commit M représente l'intégration, selon la méthode de fusion utilisée.

Les commits F et G représentent des changements ultérieurs sur `main`.

Le diagramme est conceptuel : la représentation exacte dépend de la méthode de fusion configurée sur la plateforme.

### 5.2. Créer une branche de fonctionnalité

Actualiser la branche principale locale :

```bash
git switch main
git fetch origin
git pull --ff-only origin main
```

Créer une branche :

```bash
git switch -c feature/api-supervision
```

Modifier le code, exécuter les tests, puis enregistrer les changements :

```bash
git add .
git commit -m "Ajout de l'API de supervision"
```

Avant un ajout global, vérifiez que les fichiers temporaires et secrets ne seront pas inclus.

Publier la branche :

```bash
git push -u origin feature/api-supervision
```

Une pull request peut alors être ouverte sur la plateforme.

### 5.3. Que doit contenir une pull request ?

Une pull request utile doit permettre aux personnes chargées de la revue de comprendre le changement sans reconstruire tout le contexte.

Elle devrait comporter :

- Un titre précis.
- Le besoin auquel elle répond.
- Un résumé des changements.
- Les tests exécutés.
- Les risques connus.
- Les impacts sur les configurations ou les dépendances.
- Les éléments nécessaires à une validation fonctionnelle.
- Les références aux tickets concernés si le projet en utilise.

### 5.4. Pourquoi GitHub Flow fonctionne bien pour les services web

Ce modèle limite le nombre de branches permanentes et réduit les mécanismes d'intégration.

Lorsque `main` reste dans un état livrable, l'équipe peut s'appuyer sur les contrôles automatiques pour déterminer si un changement est prêt.

Cela convient notamment aux équipes qui :

- Livrent régulièrement.
- Utilisent une revue de code.
- Disposent d'une CI fiable.
- Peuvent déployer fréquemment.
- Ne maintiennent pas de nombreuses versions historiques en parallèle.

### 5.5. Limites de GitHub Flow

Le modèle simple n'indique pas à lui seul comment gérer plusieurs versions supportées simultanément.

Si les versions 2.3 et 2.4 doivent recevoir des correctifs indépendants, il faudra ajouter une stratégie de maintenance, des tags ou des branches spécifiques.

Le modèle nécessite également que `main` reste suffisamment stable pour l'usage prévu.

Une branche principale qui accumule des fonctionnalités incomplètes et des régressions ne bénéficie pas réellement de la simplicité du modèle.

### 5.6. Règles recommandées

Pour un projet utilisant GitHub Flow :

- Interdire les modifications directes non contrôlées sur `main`.
- Exiger les checks CI nécessaires.
- Utiliser des branches de courte durée.
- Garder les pull requests suffisamment petites pour être relues.
- Supprimer les branches fusionnées lorsqu'elles ne sont plus utiles.
- Déployer depuis un commit ou un artefact identifié.
- Documenter la procédure de correction urgente.
- Éviter de faire de `main` une branche de développement instable.

GitHub Flow n'exige pas nécessairement une approbation manuelle spécifique dans tous les projets, mais les règles de protection doivent être adaptées au risque.

## 6. Trunk-Based Development

### 6.1. Principe

Trunk-Based Development consiste à intégrer fréquemment le travail dans une branche centrale, appelée *trunk*, souvent nommée `main`.

Les développeurs utilisent des changements petits et des branches de courte durée lorsqu'une isolation ou une revue le nécessite.

Le modèle cherche à limiter la divergence entre les branches.

```text
               feature A
                  |
                  v
main  A---B---C---D---E---F---G---H
                  ^       ^
                  |       |
               feature B feature C
```

Cette représentation indique que les changements des fonctionnalités sont intégrés progressivement au trunk.

Les branches courtes peuvent être utilisées pour les revues et les contrôles CI, mais elles ne doivent pas devenir des lignes de développement éloignées du trunk pendant de longues périodes.

### 6.2. Pourquoi intégrer souvent ?

Plus une branche reste séparée du trunk, plus elle risque d'accumuler des différences.

Supposons que trois développeurs travaillent séparément pendant plusieurs semaines :

```text
main:      A---B---C---D---E---F---G
                 \
feature A:        H---I---J---K
                  \
feature B:         L---M---N
                   \
feature C:          P---Q---R
```

Les trois branches peuvent avoir des dépendances différentes par rapport à la branche principale.

Au moment de leur intégration, elles risquent de rencontrer :

- Des conflits.
- Des modifications incompatibles.
- Des tests qui échouent à cause des interactions.
- Des changements qui ne sont plus adaptés à l'état actuel du projet.
- Un délai élevé entre le développement et le retour d'information.

Trunk-Based Development cherche à réduire cette divergence en intégrant les modifications régulièrement.

### 6.3. Branches de courte durée

Une branche de courte durée est créée pour une tâche clairement délimitée et est intégrée rapidement après les contrôles nécessaires.

Exemples :

```text
feature/add-export
fix/api-timeout
refactor/config-loader
```

Il ne faut pas fixer une durée arbitraire identique pour tous les projets. L'objectif est de limiter la durée pendant laquelle les changements restent isolés.

Une branche ouverte pendant quelques heures peut être trop longue si les changements sont minuscules et la CI très rapide. Une branche de plusieurs jours peut être raisonnable si une tâche nécessite plusieurs étapes de validation.

Le principal indicateur est la fréquence d'intégration et le niveau de divergence, pas seulement le nombre de jours.

### 6.4. Comment intégrer une fonctionnalité incomplète ?

Un défi fréquent consiste à travailler sur une fonctionnalité qui n'est pas encore prête à être utilisée.

La solution n'est pas nécessairement de conserver une branche séparée pendant plusieurs semaines.

Plusieurs mécanismes existent.

#### Fonctionnalité inactive par défaut

Le code peut être intégré tout en gardant la fonctionnalité désactivée.

Exemple conceptuel :

```python
def traiter_nouvelle_fonctionnalite(configuration):
    if not configuration.nouvelle_fonctionnalite_activee:
        return None

    return executer_nouvelle_fonctionnalite()
```

Le contrôle de cette fonctionnalité peut s'appuyer sur une configuration, une permission ou un mécanisme de *feature flag*.

Il faut toutefois vérifier que le code inactif ne perturbe pas le comportement existant.

#### Feature flags

Un feature flag permet de contrôler l'activation d'une fonctionnalité indépendamment de son intégration dans le code.

Les flags peuvent être contrôlés par configuration ou par un service dédié.

Ils doivent être gouvernés :

- Définir un propriétaire.
- Préciser leur valeur par défaut.
- Contrôler qui peut les modifier.
- Documenter leur rôle.
- Supprimer les flags temporaires devenus inutiles.
- Vérifier les chemins activés et désactivés.

Un feature flag n'est pas une protection absolue. Le code derrière le flag reste présent dans le produit et doit être testé.

#### Branches courtes et changements progressifs

Une fonctionnalité volumineuse peut être divisée en plusieurs changements compatibles.

Exemple :

```text
Étape 1 : ajouter les structures de données
Étape 2 : intégrer le service interne
Étape 3 : ajouter l'interface
Étape 4 : activer la fonctionnalité
```

Chaque étape doit laisser le projet dans un état techniquement acceptable.

### 6.5. Les exigences de Trunk-Based Development

Le modèle repose sur une discipline technique et collective.

Il nécessite généralement :

- Une CI rapide et fiable.
- Des tests automatiques pertinents.
- Des changements de taille maîtrisée.
- Une revue de code compatible avec une intégration fréquente.
- Des mécanismes d'activation progressive si nécessaire.
- Des règles claires pour les migrations de données et les changements incompatibles.
- Une gestion efficace des régressions.
- Une stratégie de livraison qui ne dépend pas d'une branche de développement séparée pendant de longues périodes.

### 6.6. Avantages et limites

Avantages :

- Divergence plus faible entre les branches.
- Retour d'information plus fréquent.
- Intégration plus continue.
- Historique généralement plus facile à suivre.
- Détection potentiellement plus rapide des incompatibilités.
- Bon alignement avec les pratiques CI/CD.

Limites :

- Exige une CI de qualité.
- Demande de découper correctement le travail.
- Nécessite une bonne maîtrise des fonctionnalités incomplètes.
- Peut être difficile dans des projets où l'intégration est bloquée par des validations longues et externes.
- Peut nécessiter une stratégie complémentaire pour les anciennes versions.

Le trunk-based development ne signifie pas que tout développeur doit obligatoirement pousser directement sur `main`. Des branches très courtes et des pull requests restent compatibles avec le modèle.

## 7. GitFlow

### 7.1. Principe

GitFlow est un modèle de branching qui sépare le développement courant, la préparation des releases, les corrections urgentes et les versions officielles.

Le modèle classique repose sur deux branches principales :

- `main` : versions de production.
- `develop` : intégration du travail destiné à une prochaine version.

Il utilise également plusieurs catégories de branches temporaires :

- `feature/*`
- `release/*`
- `hotfix/*`

Des branches de support peuvent être ajoutées pour maintenir d'anciennes versions.

### 7.2. Vue d'ensemble

```text
                          main
                            |
       +--------------------+------------------+
       |                    |                  |
       v                    v                  v
     v1.0.0              v1.1.0             v1.2.0
       ^                    ^                  ^
       |                    |                  |
       +----------+---------+------------------+
                  |         |
                  |         |
develop  A---B----C----D----E----F----G
              \       \          \
               \       \          \
feature/login   L---M   feature/api N---O
```

Le diagramme illustre une activité de développement alimentant des versions publiées sur `main`.

Le modèle exact dépend du cycle de release et du calendrier du projet.

### 7.3. Branche `main`

La branche `main` représente les versions officielles de production.

Les commits présents sur cette branche doivent respecter les règles établies pour le code publié.

Les versions sont généralement identifiées par des tags annotés, par exemple :

```text
v1.0.0
v1.1.0
v1.2.0
```

Les tags doivent être associés aux commits réellement publiés.

### 7.4. Branche `develop`

La branche `develop` rassemble le travail destiné à la prochaine version.

Les branches de fonctionnalité partent généralement de `develop`, puis sont fusionnées dans cette même branche lorsque le travail est terminé.

Schéma :

```text
develop A---B---C---F---G
             \   /
              D-E
             feature/login
```

Cette séparation permet de faire évoluer le prochain lot de fonctionnalités indépendamment de la version stable.

Elle impose néanmoins de maintenir deux lignes d'intégration qui doivent régulièrement être synchronisées.

### 7.5. Branches de fonctionnalité

Une branche de fonctionnalité est créée à partir de `develop`.

Exemple :

```bash
git switch develop
git pull --ff-only origin develop
git switch -c feature/gestion-utilisateurs
```

Après les modifications :

```bash
git add .
git commit -m "Ajout de la gestion des utilisateurs"
git push -u origin feature/gestion-utilisateurs
```

La fonctionnalité est ensuite intégrée dans `develop` via le processus défini par l'équipe.

La branche temporaire peut être supprimée après la fusion si elle n'est plus nécessaire.

### 7.6. Branches de release

Une branche de release est créée à partir de `develop` lorsque les fonctionnalités prévues pour la version sont suffisamment intégrées.

Exemple :

```bash
git switch develop
git switch -c release/2.4.0
```

La branche sert ensuite à finaliser la version.

Les activités possibles comprennent :

- Corrections de bugs.
- Ajustements de configuration.
- Mise à jour des numéros de version.
- Validation des dépendances.
- Exécution des tests de régression.
- Préparation de la documentation.
- Vérification de la procédure de publication.

Une branche de release ne devrait généralement pas recevoir de nouvelles fonctionnalités majeures. Les nouvelles fonctionnalités peuvent continuer sur `develop`, tandis que `release/2.4.0` est stabilisée.

### 7.7. Publier une release

Une fois la branche validée, le processus GitFlow classique intègre la version dans `main` et crée un tag de publication.

Les outils automatisent parfois une partie de ces opérations, mais leur séquence doit être documentée.

Schéma :

```text
develop
   |
   | Création de la branche
   v
release/2.4.0
   |
   | Tests et corrections
   v
Validation finale
   |
   v
Fusion dans main
   |
   v
Tag v2.4.0
   |
   v
Publication
```

Les corrections réalisées sur la branche de release doivent également être réintégrées dans `develop`, afin que la prochaine version ne perde pas ces corrections.

### 7.8. Branche de hotfix

Une branche de hotfix est créée à partir de `main` car elle vise une version de production.

Exemple :

```bash
git switch main
git switch -c hotfix/2.4.1
```

Après la correction et les tests :

```bash
git add .
git commit -m "Correction urgente de la validation des accès"
```

Dans le workflow GitFlow, le hotfix est ensuite intégré dans `main`, identifié par une nouvelle version, puis propagé dans `develop`.

Le mécanisme exact peut utiliser une fusion adaptée au modèle ou une intégration équivalente des changements. L'essentiel est que la correction soit présente dans toutes les lignes maintenues qui en ont besoin.

### 7.9. Vue simplifiée du hotfix GitFlow

```text
                 main
                  |
                v2.4.0
                  |
                  v
          hotfix/2.4.1
                  |
                  v
         Correction urgente
                  |
             +----+----+
             |         |
             v         v
           main      develop
             |
             v
           v2.4.1
```

Le schéma représente le principe de propagation de la correction, et non l'obligation d'utiliser une commande identique pour toutes les branches.

Dans un véritable dépôt, la fusion du hotfix peut nécessiter une résolution de conflit différente sur `develop`, car cette branche peut avoir évolué depuis la publication de la version 2.4.0.

### 7.10. Avantages de GitFlow

GitFlow peut être adapté lorsqu'un projet possède :

- Des releases planifiées.
- Une phase de stabilisation clairement distincte du développement courant.
- Des versions officielles identifiées.
- Des correctifs urgents sur une version stable.
- Des besoins de maintenance de plusieurs lignes.
- Un processus de publication nécessitant des validations structurées.

### 7.11. Limites de GitFlow

GitFlow crée plus de branches de longue durée qu'un flux simple centré sur `main`.

Il peut compliquer le travail lorsque les équipes souhaitent livrer très fréquemment.

Les risques comprennent :

- Divergence entre `main` et `develop`.
- Accumulation de modifications avant intégration.
- Corrections à propager vers plusieurs branches.
- Conflits lors des fusions de release.
- Confusion sur la branche qui contient la version la plus récente.
- Multiplication des processus de publication.

Pour une application web déployée plusieurs fois par jour, GitFlow peut ajouter une complexité supérieure au besoin réel.

### 7.12. GitFlow n'est pas nécessairement le choix par défaut

GitFlow est un modèle reconnu, particulièrement adapté à certains cycles de versions structurés.

Il n'est cependant pas obligatoire dans les projets professionnels ni dans les environnements CI/CD modernes.

La décision doit être fondée sur les besoins de release, le nombre de versions maintenues, les exigences d'exploitation et la capacité de l'équipe à maintenir plusieurs lignes de développement.

## 8. GitLab Flow et ses variantes

### 8.1. Comprendre le terme

GitLab Flow désigne une famille de pratiques de gestion des branches et de promotion des changements associées aux workflows de GitLab.

Selon le contexte, ces pratiques peuvent combiner :

- Une branche principale.
- Des branches de fonctionnalité.
- Des merge requests.
- Des branches de maintenance.
- Des branches de release.
- Une séparation entre développement amont et versions de production.
- Des règles de promotion d'une version entre des environnements.

Il n'existe donc pas une seule représentation de GitLab Flow qui conviendrait à tous les projets.

### 8.2. Le principe « upstream first »

Lorsqu'une correction vise une version de production mais doit aussi exister dans le développement futur, une règle utile consiste à traiter la branche principale comme la source de référence du correctif lorsque cela est possible.

Une correction peut ensuite être propagée vers les branches de maintenance concernées.

Selon l'état des versions, cela peut passer par une fusion ou par un cherry-pick.

L'objectif est de réduire le risque de divergence et d'éviter qu'une correction ne soit oubliée dans une ligne de développement.

Il faut toutefois adapter la direction de propagation si la correction doit d'abord être validée ou développée dans un contexte spécifique.

### 8.3. Exemple avec une branche de maintenance

Supposons que le projet maintienne :

```text
main
release/2.3
release/2.4
```

Un défaut affecte les versions 2.3 et 2.4.

La correction est d'abord intégrée dans la branche appropriée selon la politique du projet, puis propagée dans les autres branches concernées.

```text
                    main
                     |
                     v
             Correction commune
               /           \
              v             v
        release/2.4     release/2.3
              |             |
              v             v
       Tests de la     Tests de la
       version 2.4     version 2.3
```

Les modifications ne sont pas nécessairement identiques dans toutes les branches. Une ancienne version peut avoir une architecture différente et nécessiter une correction adaptée.

### 8.4. Quand les branches de maintenance sont utiles

Elles sont particulièrement pertinentes lorsque :

- Des clients utilisent plusieurs versions.
- Les mises à niveau ne sont pas immédiates.
- Le contrat de support impose des correctifs.
- Les dépendances diffèrent entre les versions.
- Les versions plus anciennes doivent recevoir uniquement des corrections ciblées.

### 8.5. Pourquoi ne pas conserver une branche permanente pour chaque étape administrative ?

Il peut être tentant de créer systématiquement :

```text
develop
test
uat
preprod
production
```

avec des fusions successives entre toutes les branches.

Cette approche peut être adaptée à certains processus, mais elle comporte des risques :

- Le code de `test` peut diverger de celui de `develop`.
- La branche `preprod` peut accumuler des commits absents de la branche principale.
- Il devient difficile de déterminer quel commit est réellement en production.
- Une correction peut être propagée dans un sens sans l'être dans l'autre.
- Les opérations de promotion peuvent devenir manuelles et fragiles.

Lorsqu'un seul artefact doit passer par plusieurs environnements, une solution souvent plus simple consiste à construire une version identifiée, puis à promouvoir le même artefact entre les environnements au moyen du pipeline et des règles d'approbation.

### 8.6. Quand une branche par environnement peut se justifier

Une organisation peut avoir des contraintes spécifiques qui rendent certaines branches d'environnement nécessaires, par exemple un workflow imposé ou des dépôts séparés.

Dans ce cas, il faut documenter précisément :

- La branche source de référence.
- Les règles de propagation des commits.
- Le lien entre un commit et un artefact.
- Les autorisations de promotion.
- La procédure de retour arrière.
- La manière de corriger les divergences.

Une branche d'environnement ne devrait pas devenir le seul endroit où une correction existe, sauf si cela fait explicitement partie d'une stratégie maîtrisée.

## 9. Branches de release et maintenance multi-version

### 9.1. Le problème de plusieurs versions actives

Imaginons un produit dont plusieurs versions sont en production :

```text
Client A : version 2.3
Client B : version 2.4
Nouvelle livraison : version 2.5
```

Le produit est développé sur `main`, mais les deux versions précédentes doivent continuer à recevoir certaines corrections.

Un seul historique principal ne suffit pas toujours à gérer ces obligations, notamment si les changements de code diffèrent entre versions.

### 9.2. Modèle de branches de maintenance

```text
main
 |
 +--- développement de la version 2.5
 |
 +--- tag v2.5.0

release/2.4
 |
 +--- corrections de la version 2.4
 |
 +--- tag v2.4.3

release/2.3
 |
 +--- corrections de la version 2.3
 |
 +--- tag v2.3.7
```

La branche `main` poursuit le développement de la nouvelle version.

Les branches de release conservées servent aux versions encore maintenues.

### 9.3. Déterminer quelles versions sont supportées

La politique du projet doit préciser :

- Les versions activement maintenues.
- La durée de support.
- Les types de correctifs acceptés.
- Les versions qui ne reçoivent plus de mises à jour.
- Les règles de migration.
- Les conditions de retrait d'une branche de maintenance.

Sans politique claire, les branches anciennes peuvent rester ouvertes indéfiniment et mobiliser des efforts de maintenance imprévus.

### 9.4. Propager une correction vers plusieurs versions

Une correction appliquée à une branche de maintenance ne doit pas être supposée présente automatiquement dans les autres branches.

Pour chaque branche concernée :

1. Identifier la version affectée.
2. Déterminer si le correctif y est applicable.
3. Choisir une fusion ou un cherry-pick selon le contexte.
4. Résoudre les conflits.
5. Exécuter les tests propres à cette version.
6. Publier un tag si une nouvelle version est produite.
7. Documenter les branches corrigées.

La correction doit être suivie explicitement jusqu'à ce que toutes les versions concernées soient traitées ou déclarées hors support.

## 10. Choisir la bonne méthode d'intégration

La stratégie de branching détermine les branches utilisées. La méthode de fusion détermine comment les changements sont intégrés à l'historique.

Ces décisions sont liées, mais il ne faut pas les confondre.

### 10.1. Merge commit

Un merge commit conserve les deux lignes de développement dans le graphe d'historique.

```text
A---B---C---------M
     \           /
      D---E-----F
```

Avantages :

- Le point d'intégration est visible.
- L'historique des branches est conservé.
- Il est plus facile d'identifier le groupe de changements qui constituait une fonctionnalité.
- La fusion peut être utile pour analyser le cycle d'une release.

Limites :

- Le graphe peut devenir complexe si de nombreuses branches sont fusionnées.
- Des commits de merge fréquents peuvent rendre certains affichages plus difficiles à lire.

### 10.2. Squash merge

Le squash merge regroupe généralement les changements d'une branche dans un commit d'intégration unique.

```text
A---B---C---S
```

Le graphe principal apparaît plus linéaire.

Avantages :

- Historique compact.
- Un commit de la branche représente souvent la fonctionnalité intégrée.
- Le message du commit final peut être plus compréhensible que plusieurs commits intermédiaires.

Limites :

- La chronologie des commits originaux de la branche n'apparaît pas de la même manière dans l'historique principal.
- Le suivi des relations entre les commits originaux et le commit de squash nécessite les références de la plateforme ou la documentation.
- Certaines techniques de comparaison entre branches doivent tenir compte du fait que les identifiants des commits ne sont pas conservés tels quels dans le résultat.

### 10.3. Rebase puis avance rapide

Une branche de fonctionnalité peut être rebasée sur la branche cible, puis intégrée par avance rapide.

Avant :

```text
A---B---C             main
         \
          D---E       feature
```

Après rebase :

```text
A---B---C---D'---E'   feature
```

Après avance rapide de `main` :

```text
A---B---C---D'---E'   main
```

Avantages :

- Historique linéaire.
- Pas de commit de merge nécessaire.
- Les commits individuels de la fonctionnalité restent visibles.

Limites :

- Les commits rejoués possèdent de nouveaux identifiants.
- L'opération peut nécessiter plusieurs résolutions de conflit.
- La politique doit préciser si la réécriture d'une branche publiée est autorisée.

### 10.4. Choisir une méthode cohérente

Il est utile de définir une politique commune.

Exemple :

```text
Branche de fonctionnalité
           |
           v
Pull request
           |
           v
Tests et revue
           |
           v
Squash merge vers main
           |
           v
Tag de release si nécessaire
```

Autre possibilité :

```text
Branche de fonctionnalité
           |
           v
Pull request
           |
           v
Tests et revue
           |
           v
Merge commit vers main
           |
           v
Historique avec intégrations explicites
```

Les deux politiques peuvent convenir selon le type de projet.

Évitez de mélanger plusieurs méthodes sans nécessité, au risque de produire un historique difficile à interpréter.

## 11. Convention de nommage des branches

### 11.1. Pourquoi les noms sont importants

Les noms de branches permettent aux contributeurs de repérer le type de travail et parfois sa relation avec un ticket.

Une nomenclature claire facilite :

- L'identification du sujet.
- La recherche dans les branches distantes.
- Les règles de protection.
- Les règles CI/CD.
- Les procédures de nettoyage.
- La génération de rapports.

### 11.2. Convention proposée

```text
feature/<description>
fix/<description>
hotfix/<description>
release/<version>
support/<version-majeure-mineure>
docs/<description>
refactor/<description>
test/<description>
chore/<description>
```

Exemples :

```text
feature/export-csv
feature/gestion-utilisateurs
fix/timeout-api
hotfix/2.4.1
release/2.5.0
support/2.3
docs/architecture-reseau
refactor/gestion-configuration
test/regression-authentification
chore/mise-a-jour-dependances
```

### 11.3. Ajouter un identifiant de ticket

Dans une organisation qui utilise un système de suivi des tâches :

```text
feature/NET-142-export-csv
fix/OPS-281-timeout-api
hotfix/SEC-019-validation-token
```

L'identifiant facilite la traçabilité, mais le nom doit rester lisible.

N'utilisez pas uniquement un numéro si celui-ci ne peut pas être interprété sans consulter un outil externe.

### 11.4. Éviter les noms ambigus

Évitez les noms tels que :

```text
test
new
temp
final
branch1
correction
develop2
```

Ils ne décrivent pas la responsabilité de la branche.

Les noms courts et explicites réduisent l'effort nécessaire pour comprendre le dépôt.

### 11.5. Les noms ne remplacent pas les règles

Une branche nommée `hotfix/2.4.1` ne devient pas automatiquement une correction de production.

Les contrôles doivent aussi vérifier sa base, sa destination et le processus de publication.

Le nom est une convention destinée aux personnes et aux automatismes. Il n'est pas une preuve de conformité du contenu.

## 12. Protéger les branches importantes

Une bonne stratégie ne peut pas reposer uniquement sur la bonne volonté des contributeurs. Les règles du dépôt doivent empêcher certaines opérations dangereuses.

### 12.1. Branches généralement protégées

Selon le modèle utilisé :

```text
main
develop
release/*
support/*
```

La protection doit être adaptée au rôle de chaque branche.

`main` peut exiger une revue, des tests et une validation de déploiement.

Une branche `release/*` peut exiger des approbations supplémentaires pendant la stabilisation.

Une branche de maintenance peut limiter les modifications à certaines catégories de correctifs.

### 12.2. Règles de protection recommandées

Pour une branche critique, envisagez de configurer :

- Les pull requests ou merge requests obligatoires.
- Le nombre minimal d'approbations.
- Les contrôles CI obligatoires.
- La résolution des conversations de revue avant fusion.
- Les restrictions sur les pushs directs.
- L'interdiction des pushs forcés.
- La protection contre la suppression accidentelle.
- Les règles d'approbation des propriétaires de code.
- Les contrôles de signature si le projet les exige.
- Les contrôles de déploiement avant fusion ou publication lorsque la plateforme et le processus le permettent.

Les capacités exactes dépendent de la plateforme et de son édition.

### 12.3. Exemple de règles par branche

| Branche | Push direct | Revue | Tests obligatoires | Publication |
|---|---|---|---|---|
| `main` | Restreint ou interdit | Obligatoire selon la politique | Oui | Automatique ou contrôlée |
| `develop` | Restreint selon l'équipe | Généralement requise | Oui | Préparation de version |
| `release/*` | Restreint | Selon le risque | Tests de régression | Après validation |
| `support/*` | Très restreint | Recommandée ou obligatoire | Tests adaptés à la version | Publication d'un correctif |
| `feature/*` | Autorisé aux contributeurs concernés | Via pull request | Oui avant fusion | Généralement non directement |

Ce tableau est un modèle de départ. Il doit être adapté aux responsabilités réelles du projet.

### 12.4. Exemple sur GitHub

Les règles de protection de branche GitHub peuvent imposer des approbations, des status checks, des contrôles de conversation, des signatures ou une histoire linéaire selon les capacités disponibles.

La documentation officielle est accessible ici :

https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

Pour un dépôt utilisant des contrôles CI, assurez-vous que les noms des jobs obligatoires sont stables et sans ambiguïté. Une règle qui attend un contrôle dont le nom change constamment peut bloquer les fusions.

### 12.5. Exemple sur GitLab

GitLab permet de configurer des règles de branches protégées, de gérer les permissions de push et de fusion, et de contrôler certains mécanismes d'approbation.

Documentation officielle :

https://docs.gitlab.com/user/project/repository/branches/protected/

Les règles d'approbation des merge requests sont documentées ici :

https://docs.gitlab.com/user/project/merge_requests/approvals/rules/

Il faut vérifier les capacités et les menus disponibles pour la version de GitLab utilisée.

## 13. Branching et CI/CD

Le nom d'une branche peut déclencher des actions dans un pipeline, mais ce déclenchement doit être conçu avec prudence.

### 13.1. Exemple de pipeline déclenché sur certaines branches

Un workflow GitHub Actions peut être déclenché lorsqu'un push cible `main` ou lorsqu'une pull request cible cette branche.

Exemple simplifié :

```yaml
name: CI

on:
  push:
    branches:
      - main
      - "release/**"
  pull_request:
    branches:
      - main
      - "release/**"

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Vérifier le code
        run: echo "Exécuter ici les contrôles du projet"
```

Ce fichier illustre uniquement la logique de déclenchement.

Dans un véritable projet, remplacez l'étape `echo` par des tests et des contrôles pertinents, puis vérifiez les versions des actions et leurs exigences de sécurité. Les actions critiques peuvent être épinglées à un SHA de commit complet et vérifié selon la politique du dépôt.

### 13.2. Ne pas accorder les mêmes privilèges à toutes les branches

Les pipelines d'une branche de fonctionnalité ne devraient généralement pas disposer des mêmes secrets et privilèges qu'un pipeline de publication en production.

Par exemple :

```text
feature/*
    |
    v
Tests et analyses
Aucun accès production
    |
    v
main
    |
    v
Construction et validation
    |
    v
Publication autorisée
```

Cette séparation limite les conséquences d'une modification malveillante ou d'une erreur dans une branche de travail.

Les permissions, secrets et conditions de déclenchement doivent être configurés explicitement. Le simple nom de branche ne constitue pas un mécanisme de sécurité suffisant.

### 13.3. Utiliser les conditions avec prudence

Un pipeline peut comporter des conditions différentes selon la branche, le tag ou le type d'événement.

Les risques à éviter sont notamment :

- Publier une version à partir d'une branche non validée.
- Exposer des secrets à un workflow exécutant du code non fiable.
- Autoriser un déploiement sur production à partir d'une pull request.
- Ignorer les tests obligatoires sur certaines branches.
- Déclencher deux publications concurrentes pour la même version.

### 13.4. Construire une fois, promouvoir l'artefact

Une stratégie saine consiste souvent à identifier le résultat de la construction, puis à promouvoir ce même artefact entre les environnements.

```text
Commit identifié
      |
      v
Build
      |
      v
Artefact versionné
      |
      v
Tests et validations
      |
      v
Préproduction
      |
      v
Approbation éventuelle
      |
      v
Production
```

Cela réduit le risque que la version testée soit différente de celle mise en production.

Une branche `preprod` ne devrait pas être confondue avec un artefact testé en préproduction : la branche identifie un historique, tandis que l'artefact est le résultat précis de la construction.

## 14. Gestion des hotfixes dans les différents modèles

Un incident de production peut nécessiter une correction urgente. La stratégie doit indiquer comment faire cette correction rapidement tout en protégeant les autres versions.

### 14.1. Hotfix en GitHub Flow

Dans un modèle simple :

```text
main
 |
 +--- dernière version livrée
 |
 +--- hotfix/* créé depuis main
         |
         v
      Correction
         |
         v
   Revue + tests
         |
         v
   Fusion vers main
         |
         v
  Nouvelle publication
```

La branche de hotfix est courte.

Le pipeline doit effectuer les contrôles obligatoires, même si le délai est urgent.

Si d'autres branches de maintenance existent, la correction doit ensuite être reportée vers les versions concernées.

### 14.2. Hotfix en Trunk-Based Development

Si le trunk correspond à la source de vérité pour la prochaine version, un correctif urgent peut être intégré rapidement à `main`, puis publié selon le processus habituel.

Si plusieurs versions sont en production, il faut utiliser les branches de maintenance correspondantes.

Le modèle trunk-based n'élimine donc pas les besoins de backport.

### 14.3. Hotfix en GitFlow

Une branche de hotfix part de la version de production sur `main`.

Après correction et validation, le changement est intégré dans `main`, reçoit un tag de correctif et est propagé vers `develop`.

Si des branches de release ou de support supplémentaires restent actives, il faut déterminer si elles nécessitent également la correction.

### 14.4. Scénario d'urgence

Supposons qu'une application de supervision présente une vulnérabilité permettant à un utilisateur non autorisé de consulter certaines données.

La procédure doit inclure :

1. Identifier la ou les versions affectées.
2. Choisir la branche de départ appropriée.
3. Corriger la cause.
4. Ajouter un test de régression.
5. Exécuter les contrôles de sécurité requis.
6. Faire examiner le changement selon la procédure d'urgence.
7. Créer la version corrigée.
8. Déployer selon les règles d'exploitation.
9. Vérifier le comportement après déploiement.
10. Propager la correction aux branches de maintenance concernées.
11. Documenter l'incident et les versions corrigées.

L'urgence peut justifier une procédure de revue accélérée, mais elle ne doit pas supprimer la traçabilité ni les vérifications essentielles.

## 15. Backport et forward-port

### 15.1. Backport

Un backport consiste à reporter un changement récent vers une version ou une branche plus ancienne.

Exemple :

```text
main
 |
 +--- correction ajoutée pour la version actuelle
            |
            v
       report vers
            |
            v
       support/2.3
```

Le backport est courant lorsque des branches de maintenance continuent de recevoir des correctifs.

Il peut utiliser :

```bash
git cherry-pick IDENTIFIANT_DU_COMMIT
```

ou une fusion adaptée si la politique du dépôt s'y prête.

### 15.2. Forward-port

Le forward-port consiste à reporter une correction vers une version ou une branche plus récente.

Il peut être nécessaire lorsqu'une correction a d'abord été réalisée sur une ancienne version maintenue, puis doit être intégrée dans la branche principale.

Le sens du report dépend donc du point de départ de la correction et de la ligne de version cible.

### 15.3. Pourquoi un cherry-pick n'est pas toujours suffisant

Le changement peut dépendre :

- D'un autre commit.
- D'une bibliothèque différente.
- D'une structure de code qui a évolué.
- D'un schéma de base de données.
- D'une API différente.
- D'une configuration qui n'existe plus dans l'ancienne version.

Avant de reporter un commit, il faut identifier ses dépendances.

Après le report, les tests doivent être exécutés dans la version cible.

### 15.4. Maintenir une matrice de propagation

Pour les projets ayant plusieurs branches de maintenance, il est utile de tenir un registre des corrections.

| Correction | `main` | `support/2.4` | `support/2.3` |
|---|---|---|---|
| CVE-XXXX | Corrigé | Corrigé | Non applicable |
| Bug API-142 | Corrigé | À reporter | Corrigé |
| Erreur de configuration | Corrigé | Non concerné | Corrigé |

Ce tableau est illustratif. Le suivi réel doit être relié aux commits, aux tickets et aux versions effectivement publiées.

La mention « corrigé » doit correspondre à un changement identifié et validé, pas uniquement à une action envisagée.

## 16. Contrôler la durée de vie des branches

### 16.1. Les branches temporaires doivent être supprimées

Lorsqu'une branche de fonctionnalité a été intégrée et n'est plus nécessaire, la conserver inutilement peut compliquer la liste des branches.

Lister les branches locales :

```bash
git branch
```

Lister les branches fusionnées dans `main` :

```bash
git branch --merged main
```

Cette commande affiche les branches dont les commits sont déjà accessibles depuis `main`, mais il faut examiner les résultats avant suppression.

Supprimer une branche locale terminée :

```bash
git branch -d feature/export-csv
```

Supprimer la branche distante :

```bash
git push origin --delete feature/export-csv
```

Cette dernière commande modifie le dépôt distant. Vérifiez qu'il s'agit bien de la branche souhaitée.

### 16.2. Nettoyer les références distantes obsolètes

Lorsque des branches distantes ont été supprimées, le dépôt local peut conserver des références de suivi désormais obsolètes.

Pour les nettoyer :

```bash
git fetch --prune
```

Cette commande supprime les références de suivi correspondant aux branches distantes qui n'existent plus, selon la configuration et les références récupérées.

Elle ne remplace pas la suppression des branches locales habituelles.

### 16.3. Ne pas supprimer automatiquement les branches de maintenance

Les branches de maintenance peuvent être nécessaires même lorsque leur version est ancienne.

Avant leur suppression, il faut vérifier :

- Que la version n'est plus supportée.
- Que les obligations contractuelles sont satisfaites.
- Que les derniers correctifs sont publiés.
- Que les tags et artefacts nécessaires restent accessibles.
- Que la procédure d'archivage est documentée.

La durée de vie d'une branche doit dépendre de son rôle, pas d'une règle uniforme.

## 17. Choisir une stratégie selon les caractéristiques du projet

### 17.1. Arbre de décision

```text
Le projet publie-t-il très fréquemment ?
              |
        +-----+-----+
        |           |
       OUI          NON
        |           |
        v           v
Branche centrale  Releases planifiées
avec branches     ou validations longues ?
courtes                  |
        |           +----+----+
        |           |         |
        |          OUI       NON
        |           |         |
        v           v         v
Trunk-Based      GitFlow ou   GitHub Flow
ou GitHub Flow   branches     avec maintenance
                 de release   adaptée
```

Cet arbre est une orientation initiale. Il faut également examiner le nombre de versions en production, les exigences de validation et le niveau d'automatisation.

### 17.2. Cas 1 : API SaaS déployée plusieurs fois par jour

Contexte :

- Un service central.
- Une équipe qui collabore fréquemment.
- Des tests automatisés.
- Des déploiements continus.
- Peu de versions historiques maintenues.

Approche souvent adaptée :

- Trunk-Based Development ou GitHub Flow.
- Branches courtes.
- CI obligatoire.
- `main` protégée.
- Contrôles de déploiement et récupération testée.

GitFlow peut fonctionner, mais ses branches supplémentaires peuvent ne pas apporter suffisamment de valeur.

### 17.3. Cas 2 : logiciel d'entreprise publié chaque trimestre

Contexte :

- Un calendrier de publication défini.
- Une phase de stabilisation.
- Des validations fonctionnelles.
- Une version officielle par trimestre.
- Des correctifs possibles sur la version en production.

Approches possibles :

- GitFlow.
- Branche principale avec branches temporaires de release.
- Branches de maintenance si plusieurs versions restent supportées.

Le choix dépend notamment du degré de séparation nécessaire entre la stabilisation et le développement futur.

### 17.4. Cas 3 : bibliothèque utilisée par de nombreux clients

Contexte :

- Des versions largement distribuées.
- Des clients qui ne mettent pas tous à jour en même temps.
- Un engagement de maintenance de plusieurs versions.
- Un besoin de compatibilité ascendante ou descendante.

Approche possible :

- Branche principale pour le développement futur.
- Tags de publication.
- Branches de support pour les versions maintenues.
- Processus de backport.
- Tests de compatibilité adaptés à chaque version.

### 17.5. Cas 4 : systèmes avec validation formelle

Contexte :

- Approbations techniques.
- Tests longs.
- Validation de la configuration.
- Publication à dates fixées.
- Traçabilité importante.

Le modèle doit séparer clairement la branche de développement, la version candidata à publication et les branches de maintenance requises.

Les validations peuvent être réalisées dans des environnements distincts sans nécessairement imposer une branche permanente par environnement.

### 17.6. Cas 5 : petite équipe avec peu d'automatisation

Une équipe peut préférer un workflow simple avec `main`, des branches courtes et une revue de code.

Avant d'adopter une stratégie complexe, elle devrait améliorer les fondations :

- Historique compréhensible.
- Tests reproductibles.
- README et règles de contribution.
- CI minimale.
- Contrôle des secrets.
- Processus de publication documenté.

Une stratégie avancée ne compense pas l'absence de ces fondations.

## 18. Une politique de branching opérationnelle

Cette section propose une politique adaptable à un projet professionnel.

### 18.1. Règles générales

Exemple de politique :

1. La branche `main` est la référence principale du dépôt.
2. Les changements fonctionnels sont développés sur des branches dédiées, sauf exception documentée.
3. Chaque pull request possède un objectif clairement défini.
4. Les tests et contrôles obligatoires doivent réussir avant la fusion.
5. Les branches protégées ne peuvent pas recevoir de push direct non autorisé.
6. Les branches de fonctionnalité sont supprimées après intégration si elles n'ont plus d'utilité.
7. Les releases sont identifiées par des tags.
8. Les corrections urgentes suivent un workflow documenté.
9. Les branches de maintenance restent disponibles tant que les versions correspondantes sont supportées.
10. Toute modification de la politique de branching est communiquée aux contributeurs.

### 18.2. Exemple de conventions

```text
main
feature/*
fix/*
hotfix/*
release/*
support/*
docs/*
refactor/*
```

Une équipe utilisant GitFlow peut ajouter `develop` comme branche permanente.

Une équipe utilisant Trunk-Based Development n'a généralement pas besoin d'introduire `develop` uniquement pour séparer le travail courant de la branche principale.

### 18.3. Exemple de règles de fusion

```text
feature/*
    |
    v
Pull request
    |
    +-- CI obligatoire
    |
    +-- Revue de code
    |
    +-- Conversations résolues
    |
    v
Fusion vers la branche cible
    |
    v
Suppression de la branche temporaire
```

Les règles de fusion doivent préciser la méthode choisie, par exemple squash merge ou merge commit.

### 18.4. Exemple de politique de release

Pour une version `2.5.0` :

1. Identifier le commit ou l'état validé servant de base à la release.
2. Créer une branche de release si le modèle le prévoit.
3. Exécuter les tests et les validations.
4. Corriger les défauts de stabilisation.
5. Vérifier que les corrections sont propagées vers les branches nécessaires.
6. Fusionner les modifications dans les lignes de développement concernées.
7. Créer un tag annoté.
8. Construire et publier l'artefact.
9. Enregistrer l'identifiant de l'artefact utilisé.
10. Conserver les informations nécessaires à une reprise ou à un audit.

Toutes les équipes n'ont pas besoin de conserver une branche `release/*`. Dans un service livrable depuis `main`, un tag et un processus de publication reproductible peuvent suffire.

## 19. Modèles de documents pour l'équipe

### 19.1. Modèle de description de pull request

Un modèle de pull request peut contenir :

```markdown
## Objectif

Décrire le besoin auquel ce changement répond.

## Modifications

- Changement principal
- Composants concernés
- Configuration éventuellement modifiée

## Tests

- [ ] Tests unitaires exécutés
- [ ] Tests d'intégration exécutés si nécessaires
- [ ] Contrôles statiques réussis

## Risques

Décrire les impacts possibles sur les données, la compatibilité,
la sécurité ou la production.

## Déploiement et retour arrière

Décrire les étapes particulières, si nécessaire.

## Validation

Indiquer les éléments permettant au relecteur de confirmer
que le changement répond au besoin.
```

Ce modèle aide à rendre les revues plus utiles, mais ne doit pas devenir une formalité remplie sans contenu réel.

### 19.2. Modèle de procédure de hotfix

```text
1. Décrire l'incident et la version affectée.
2. Identifier la branche de base correcte.
3. Créer la branche de hotfix ou de maintenance.
4. Implémenter le correctif minimal.
5. Ajouter un test de régression.
6. Exécuter les contrôles obligatoires.
7. Faire examiner le correctif selon la procédure d'urgence.
8. Fusionner ou intégrer le correctif.
9. Créer le tag de la nouvelle version.
10. Construire et publier l'artefact.
11. Déployer et vérifier le service.
12. Reporter la correction dans les autres branches concernées.
13. Documenter la clôture de l'incident.
```

### 19.3. Modèle de fiche de branche de release

```text
Nom de la branche :
Version prévue :
Commit de base :
Date de création :
Responsable de la release :
Critères de validation :
Tests obligatoires :
Défauts connus :
Corrections acceptées :
Procédure de publication :
Tag final :
Identifiant de l'artefact :
Date de fin de maintenance :
```

Le modèle peut être stocké dans la documentation du projet ou dans l'outil de gestion des releases.

## 20. Mesurer la qualité de la stratégie de branching

Une stratégie devrait être évaluée à partir de son fonctionnement réel, et pas uniquement de sa conformité à un modèle connu.

### 20.1. Durée de vie des branches

Une durée de vie élevée peut indiquer que les changements restent isolés trop longtemps.

Il faut examiner :

- La raison du délai.
- Les dépendances entre tâches.
- La durée des revues.
- Les blocages CI.
- La fréquence des mises à jour de branches.

Un délai élevé n'est pas toujours un problème : une branche de maintenance doit parfois exister pendant plusieurs années. Il faut distinguer les branches permanentes justifiées des branches temporaires devenues trop longues.

### 20.2. Délai avant intégration

Mesurez le temps entre la création d'une modification et son intégration dans la branche cible.

Un délai excessif peut indiquer :

- Des pull requests trop volumineuses.
- Un manque de disponibilité pour les revues.
- Des tests trop lents.
- Des dépendances organisationnelles.
- Des conflits répétés.
- Des exigences de validation mal définies.

### 20.3. Taux d'échec des fusions et des déploiements

Une fusion sans conflit peut quand même produire une régression.

Il est donc utile d'observer :

- Les pull requests qui nécessitent plusieurs cycles de correction.
- Les tests qui échouent après fusion.
- Les déploiements nécessitant un retour arrière.
- Les hotfixes qui auraient pu être évités.
- Les incidents liés à des corrections absentes d'une branche de maintenance.

### 20.4. Temps de résolution des conflits

Si les conflits sont fréquents, il faut examiner la cause :

- Branches trop longues.
- Changements trop importants.
- Plusieurs équipes modifiant les mêmes composants.
- Refactorisations massives.
- Interfaces instables.
- Absence de synchronisation régulière.

La solution ne consiste pas nécessairement à choisir une autre commande Git. Il peut être nécessaire de découper le travail, modifier les responsabilités des composants ou améliorer les tests.

### 20.5. Mesures de livraison

Les mesures de performance de livraison peuvent compléter l'analyse du branching :

- Délai de livraison des changements.
- Fréquence des déploiements.
- Taux d'échec des changements.
- Temps de récupération après un déploiement défaillant.
- Taux de retravail des déploiements.

Les indicateurs doivent servir à améliorer le système de travail, pas à classer les développeurs selon le nombre de commits.

## 21. Les erreurs de conception fréquentes

### 21.1. Garder trop de branches permanentes

Chaque branche permanente crée des obligations de synchronisation, de test et de maintenance.

Une branche doit avoir un rôle précis.

### 21.2. Intégrer trop tard les fonctionnalités

Des branches longues augmentent les risques de divergence et peuvent empêcher la détection rapide des incompatibilités.

Réduisez la taille des changements lorsque cela est possible et intégrez plus fréquemment.

### 21.3. Utiliser des branches d'environnement comme système de promotion automatique

Une branche `preprod` n'est pas une preuve que l'artefact correspondant a été validé en préproduction.

Utilisez l'identification des artefacts et la traçabilité des déploiements pour savoir quelle version est effectivement en cours d'exécution.

### 21.4. Réécrire l'historique partagé sans coordination

Un rebase ou un push forcé peut rendre les historiques des collaborateurs incompatibles.

Réservez les réécritures aux contextes autorisés et coordonnez les opérations lorsqu'une branche a déjà été publiée.

### 21.5. Propager un hotfix uniquement dans une branche

Une correction destinée à plusieurs versions doit être suivie jusqu'à ce que chaque branche concernée ait été traitée.

Une correction qui reste uniquement sur `main` peut ne jamais atteindre un produit ancien encore utilisé.

### 21.6. Mélanger les politiques de fusion sans règle

Des méthodes différentes peuvent être adaptées à certains scénarios, mais une politique sans cohérence rend l'historique plus difficile à lire.

Documentez la méthode par défaut et les exceptions.

### 21.7. Confondre branche et version publiée

Une branche est une référence mobile dans l'historique.

Une version publiée doit être identifiable de façon stable, généralement à l'aide d'un tag, d'un artefact versionné et des informations de livraison associées.

### 21.8. Déployer une branche au lieu d'un artefact contrôlé

Un nom de branche n'identifie pas nécessairement un contenu stable dans le temps.

Pour une release, utilisez un commit ou un artefact identifié, puis conservez la relation entre le commit, l'artefact et le déploiement.

## 22. Migrer d'une stratégie à une autre

Le changement de stratégie doit être planifié. Modifier les conventions de branches sans adapter les pipelines et les permissions peut bloquer les contributions ou provoquer des publications inattendues.

### 22.1. Étape 1 : inventorier les branches existantes

Lister les branches locales :

```bash
git branch
```

Lister toutes les branches connues :

```bash
git branch -a
```

Examiner les références :

```bash
git log --oneline --graph --decorate --all
```

Déterminer :

- Les branches permanentes.
- Les branches de release encore actives.
- Les versions maintenues.
- Les branches de fonctionnalité anciennes.
- Les règles de fusion.
- Les pipelines déclenchés par nom de branche.
- Les secrets ou permissions associés aux déploiements.

### 22.2. Étape 2 : comprendre les problèmes actuels

Posez-vous les questions suivantes :

- Les équipes attendent-elles longtemps avant les fusions ?
- Les branches divergent-elles souvent ?
- Les releases ont-elles besoin de longues phases de stabilisation ?
- Existe-t-il plusieurs versions en production ?
- Les corrections sont-elles propagées manuellement ?
- Les pipelines sont-ils suffisamment rapides et fiables ?
- La stratégie actuelle entraîne-t-elle des déploiements incorrects ?

Ne migrez pas vers un nouveau modèle simplement parce qu'il est populaire.

### 22.3. Étape 3 : définir le modèle cible

Écrivez les règles avant de modifier les branches.

Par exemple :

```text
main :
  Source de référence du code intégré.

feature/* :
  Branches temporaires pour les changements.

release/* :
  Créées uniquement lorsqu'une phase de stabilisation est nécessaire.

support/* :
  Conservées tant que la version correspondante est maintenue.

hotfix/* :
  Corrections urgentes depuis la version appropriée.
```

Le document doit aussi préciser les méthodes de fusion, les approbations et le processus de publication.

### 22.4. Étape 4 : mettre à jour les pipelines et les permissions

Vérifiez :

- Les filtres par branche.
- Les règles de déclenchement.
- Les autorisations des jobs.
- Les approbations obligatoires.
- Les secrets accessibles.
- Les déploiements automatisés.
- Les procédures de retour arrière.
- Les règles de conservation et de suppression des branches.

### 22.5. Étape 5 : migrer progressivement

Choisissez un projet pilote si l'organisation compte plusieurs dépôts.

Mesurez les délais et les difficultés avant et après le changement.

Documentez les problèmes rencontrés puis ajustez les règles avant de généraliser la migration.

### 22.6. Étape 6 : supprimer les anciennes branches avec prudence

Vérifiez qu'une branche n'est plus nécessaire avant de la supprimer.

Ne supprimez pas les branches qui assurent encore le support de versions publiées.

Un ancien modèle de branche peut être abandonné pour le développement courant tout en conservant certaines branches de maintenance indispensables.

## 23. Projet pratique expert : concevoir une stratégie adaptée à un produit

### 23.1. Contexte du projet

Vous êtes responsable de la gestion des versions d'une plateforme de supervision réseau.

Le système comporte :

- Une API.
- Une interface web.
- Un module de collecte de métriques.
- Des tests automatisés.
- Un pipeline CI/CD.
- Une version récente en production.
- Une ancienne version encore maintenue pour certains clients.

L'équipe publie régulièrement des améliorations, mais elle doit aussi corriger rapidement les défauts de production.

Le processus actuel est mal défini : les développeurs créent des branches avec des noms variables, certaines branches restent ouvertes très longtemps et les correctifs ne sont pas toujours propagés vers les versions anciennes.

### 23.2. Travail demandé

Concevez une stratégie de branching qui précise :

1. La branche principale de référence.
2. Le modèle choisi : GitHub Flow, Trunk-Based Development, GitFlow ou une variante justifiée.
3. Les types de branches autorisés.
4. La convention de nommage.
5. La durée de vie attendue des branches temporaires.
6. La méthode de fusion.
7. Les contrôles CI obligatoires.
8. Les règles de protection de la branche principale.
9. La procédure de préparation d'une release.
10. La procédure de hotfix.
11. Les règles de backport vers l'ancienne version.
12. La politique de tagging.
13. Le processus de suppression des branches terminées.
14. Les indicateurs permettant de mesurer l'efficacité de la stratégie.

### 23.3. Scénario A : correction urgente

Un défaut de sécurité est détecté sur la version 2.4.0.

La version 2.5 est en développement et la version 2.3 est toujours supportée.

Décrivez :

- La branche depuis laquelle créer le hotfix.
- Les tests requis.
- La méthode de publication.
- Le report du correctif vers les branches concernées.
- Les contrôles permettant de vérifier que les versions sont toutes traitées.

### 23.4. Scénario B : fonctionnalité volumineuse

Une nouvelle fonctionnalité prend plusieurs semaines et doit être développée en plusieurs étapes.

Décrivez comment éviter qu'une branche longue ne diverge excessivement.

Vous pouvez envisager :

- Un découpage progressif.
- Des branches très courtes.
- Des feature flags.
- Des interfaces compatibles entre les étapes.
- Des tests d'intégration.
- Des validations progressives.

Justifiez les choix retenus.

### 23.5. Scénario C : échec d'une release

Une release candidate passe les tests unitaires, mais échoue en préproduction.

Expliquez comment identifier le commit et l'artefact concernés, corriger le problème, relancer les contrôles et éviter de publier une version différente de celle qui a été validée.

### 23.6. Livrables attendus

Le projet doit contenir :

- Un document décrivant le modèle de branching.
- Des schémas textuels des flux de branches.
- Une politique de nommage.
- Une politique de fusion.
- Une procédure de hotfix et de backport.
- Une politique de release et de tag.
- Un exemple de règles de protection.
- Une proposition de workflow CI/CD.
- Une checklist de revue.
- Une checklist de publication.
- Un plan de mesure et d'amélioration continue.

## 24. Exercices de compréhension

### Exercice 1 : choisir un modèle

Une application SaaS est déployée plusieurs fois par jour. L'équipe dispose de tests automatisés rapides, d'une revue de code obligatoire et d'une surveillance efficace en production.

Quel modèle privilégieriez-vous entre GitFlow et un modèle centré sur `main` ? Justifiez votre réponse et précisez les conditions nécessaires.

### Exercice 2 : GitFlow et release

Dans GitFlow, pourquoi une branche `release/2.4.0` est-elle créée à partir de `develop` plutôt qu'à partir de `main` dans le modèle classique ?

Que doit-il se passer avec les corrections effectuées pendant la stabilisation ?

### Exercice 3 : propagation d'un hotfix

Une correction urgente est appliquée à `main`, puis publiée.

Le dépôt possède aussi `develop`, `support/2.3` et `support/2.4`.

Décrivez la méthode permettant de vérifier les branches auxquelles la correction doit être reportée.

### Exercice 4 : branches par environnement

Une entreprise utilise les branches `dev`, `test`, `preprod` et `prod`.

Chaque semaine, les équipes fusionnent manuellement le contenu d'une branche vers la suivante.

Identifiez quatre risques de ce modèle et proposez une solution qui permet de mieux tracer la version déployée.

### Exercice 5 : branche trop longue

Une branche de fonctionnalité est restée ouverte pendant six semaines. Elle comporte une quarantaine de commits et plusieurs conflits lors de la fusion.

Proposez une démarche technique et organisationnelle pour réduire la probabilité de reproduire cette situation.

### Exercice 6 : méthode d'intégration

Un projet exige de conserver un historique linéaire dans sa branche principale.

Quelle méthode de fusion peut être adaptée ? Quels contrôles supplémentaires faut-il effectuer avant et après l'intégration ?

### Exercice 7 : maintenance de plusieurs versions

Une bibliothèque maintient les versions 3.2 et 3.3, tandis que le développement futur se poursuit sur `main`.

Pourquoi une seule branche principale peut-elle être insuffisante pour gérer tous les correctifs ?

Décrivez les rôles possibles des branches de maintenance.

### Exercice 8 : branche et artefact

Une équipe déploie la branche `preprod` après avoir effectué quelques tests, puis déploie la même branche en production une semaine plus tard.

Pourquoi le nom de branche ne suffit-il pas à prouver que le même artefact a été testé puis publié ?

### Exercice 9 : revue et sécurité

Une pull request a été approuvée, mais un nouveau commit est ajouté après l'approbation.

Quels mécanismes peuvent empêcher la fusion de reposer sur une approbation devenue obsolète ou sur des tests exécutés sur un ancien commit ?

### Exercice 10 : mesurer une stratégie

L'équipe constate une hausse du nombre de branches et une augmentation du temps entre la création des pull requests et leur fusion.

Quelles données collecteriez-vous pour identifier les causes du problème ?

## 25. Corrigés des exercices

### Corrigé 1

Un modèle centré sur `main`, tel que GitHub Flow ou Trunk-Based Development, est souvent adapté à une application SaaS qui livre fréquemment, dispose de contrôles automatiques et peut publier des versions de manière fiable.

Le choix dépend néanmoins de la capacité de la CI, de la taille des changements, des exigences de publication et du besoin éventuel de maintenir plusieurs versions.

GitFlow pourrait convenir si le produit nécessite des releases structurées avec une séparation importante entre développement et stabilisation.

### Corrigé 2

Dans GitFlow classique, `develop` contient les fonctionnalités destinées à la prochaine version. La branche de release est créée à partir de cette intégration lorsque les fonctionnalités prévues sont prêtes.

Les corrections de stabilisation doivent être conservées dans la version publiée et réintégrées dans `develop`, afin que les défauts corrigés ne réapparaissent pas dans les futures releases.

### Corrigé 3

Il faut commencer par identifier les versions réellement affectées.

Ensuite, on vérifie le contenu de `main`, `develop` et des branches de maintenance. La correction doit être propagée vers chaque version encore concernée, par fusion ou cherry-pick selon le contexte.

Chaque branche cible doit recevoir les tests adaptés à sa version. Il faut enfin documenter les versions corrigées et les publications réalisées.

### Corrigé 4

Les principaux risques sont :

- La divergence entre les branches d'environnement.
- Les corrections présentes dans une branche mais absentes des autres.
- La difficulté à identifier le commit qui tourne réellement en production.
- La possibilité de reconstruire ou de modifier le logiciel différemment à chaque promotion.

Une approche plus traçable consiste à construire un artefact identifié, à le vérifier puis à promouvoir cet artefact entre les environnements avec un pipeline contrôlé. Les branches d'environnement ne doivent être conservées que si elles répondent à un besoin clairement justifié.

### Corrigé 5

La démarche peut inclure :

- Découper la fonctionnalité en changements plus petits.
- Intégrer plus fréquemment les changements dans la branche principale ou la branche d'intégration.
- Ajouter des tests pour détecter les incompatibilités.
- Utiliser des interfaces compatibles entre les étapes.
- Envisager des feature flags pour intégrer progressivement du code encore inactif.
- Réduire la durée des revues.
- Identifier les composants souvent modifiés simultanément.

La solution doit traiter les causes de la divergence plutôt que de simplement changer le nom de la branche.

### Corrigé 6

Une stratégie basée sur le rebase des branches de fonctionnalité, suivie d'une avance rapide lorsque cela est possible, peut répondre à l'exigence d'un historique linéaire.

Un squash merge peut également produire un historique principal linéaire selon la configuration de la plateforme.

Il faut vérifier les différences, la réussite des tests, la politique de réécriture de l'historique et les règles de protection de branche.

### Corrigé 7

Les versions 3.2 et 3.3 peuvent avoir des bases de code différentes et nécessiter des corrections distinctes.

Des branches telles que `support/3.2` et `support/3.3` permettent de maintenir chacune des versions tout en poursuivant le développement futur sur `main`.

Les corrections doivent être reportées vers chaque branche concernée et testées dans son contexte.

### Corrigé 8

Une branche est une référence vers un commit qui peut changer au fil du temps. Un déploiement correspond à un artefact précis, construit à partir d'un état de code et de dépendances.

Pour prouver que la même version a été testée puis publiée, il faut conserver l'identifiant du commit, l'identifiant de l'artefact, les résultats des contrôles et la traçabilité des déploiements.

### Corrigé 9

La plateforme peut proposer des mécanismes tels que la révocation des approbations devenues obsolètes, les contrôles de statut obligatoires, les règles d'approbation, la protection de branche et des vérifications liées au dernier commit de la pull request.

Les tests doivent porter sur le contenu effectivement fusionné, ou sur un état qui respecte la politique d'intégration définie par le projet.

### Corrigé 10

Il faut notamment mesurer :

- La durée de vie des branches.
- Le temps entre l'ouverture et la fusion des pull requests.
- Le nombre de cycles de correction.
- Le délai d'exécution de la CI.
- Le temps d'attente avant revue.
- La fréquence des conflits.
- La taille des pull requests.
- Les blocages liés aux approbations.
- Le nombre de branches obsolètes.
- Les échecs après fusion.

Ces données permettent de distinguer un problème technique d'un problème de processus ou de capacité de revue.

## 26. Checklist d'adoption d'une stratégie de branching

Avant d'adopter une stratégie sur un projet professionnel, validez les éléments suivants.

### Gouvernance

- [ ] La branche de référence est définie.
- [ ] Le rôle de chaque branche permanente est documenté.
- [ ] Les types de branches temporaires sont définis.
- [ ] La convention de nommage est connue de l'équipe.
- [ ] Les règles de suppression des branches sont documentées.

### Intégration

- [ ] La méthode de fusion par défaut est choisie.
- [ ] Les critères de revue sont définis.
- [ ] Les contrôles CI obligatoires sont identifiés.
- [ ] Les branches protégées sont configurées.
- [ ] Les permissions de push et de fusion sont adaptées.

### Releases

- [ ] La méthode de création d'une release est documentée.
- [ ] Les tags suivent une convention cohérente.
- [ ] Les artefacts publiés sont identifiables.
- [ ] Les versions maintenues sont définies.
- [ ] Le traitement des correctifs urgents est documenté.

### Sécurité

- [ ] Les secrets ne sont pas stockés dans les branches.
- [ ] Les pipelines disposent de permissions limitées.
- [ ] Les pushs forcés sur les branches critiques sont interdits ou strictement contrôlés.
- [ ] Les changements sensibles nécessitent une revue adaptée.
- [ ] Les procédures de récupération et de retour arrière sont connues.

### Amélioration continue

- [ ] La durée de vie des branches est mesurée.
- [ ] Le délai d'intégration est suivi.
- [ ] Les échecs de fusion et de déploiement sont analysés.
- [ ] Les problèmes récurrents font l'objet d'améliorations documentées.

## 27. Glossaire essentiel

**Backport :** report d'un changement vers une version ou une branche plus ancienne.

**Branche de fonctionnalité :** branche temporaire consacrée au développement d'un changement.

**Branche de maintenance :** branche utilisée pour entretenir une version du produit qui reste supportée.

**Branche de release :** branche utilisée pour stabiliser ou préparer une version avant publication.

**Branche de hotfix :** branche créée pour corriger rapidement une version en production.

**Branching :** organisation des branches et des règles de circulation des modifications dans un dépôt.

**CI :** intégration continue, pratique qui vérifie fréquemment les changements par des contrôles automatisés.

**Commit de fusion :** commit qui réunit plusieurs lignes de développement dans l'historique.

**Feature flag :** mécanisme permettant d'activer ou de désactiver une fonctionnalité indépendamment de sa présence dans le code.

**Forward-port :** report d'une correction vers une version ou une branche plus récente.

**GitFlow :** modèle de branching organisé autour de `main`, `develop` et de branches temporaires pour les fonctionnalités, releases et hotfixes.

**GitHub Flow :** modèle de collaboration centré sur des branches de courte durée, des pull requests et l'intégration dans la branche principale.

**GitLab Flow :** famille de workflows qui combine l'intégration de changements, la revue et, selon le contexte, la gestion de versions ou d'environnements.

**Hotfix :** correction urgente destinée à une version déjà publiée ou en production.

**Merge commit :** commit créé lors d'une fusion lorsque l'historique nécessite ou demande un commit de fusion.

**Pull request :** demande d'intégration de changements, accompagnée d'un processus de revue et de contrôles sur une plateforme collaborative.

**Release :** version préparée, identifiée et publiée selon le processus du projet.

**Squash merge :** méthode d'intégration regroupant plusieurs changements en un commit sur la branche cible.

**Support branch :** branche conservée pour assurer la maintenance d'une ligne de version.

**Tag :** référence identifiant un point précis de l'historique, souvent utilisé pour marquer une release.

**Trunk-Based Development :** pratique d'intégration fréquente des changements dans une branche centrale, généralement avec des branches de courte durée.

## 28. Références officielles pour approfondir

### Stratégies de branching

- GitLab Docs — Stratégies de branching : https://docs.gitlab.com/user/project/repository/branches/strategies/
- Trunk-Based Development — Documentation du modèle : https://trunkbaseddevelopment.com/
- Trunk-Based Development — Publication depuis le trunk : https://trunkbaseddevelopment.com/release-from-trunk/
- Atlassian — Trunk-Based Development : https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development
- GitFlow — Implémentation de référence du modèle : https://github.com/nvie/gitflow
- GitFlow — Présentation du workflow : https://git-flow.sh/workflows/gitflow/

### Git et méthodes de fusion

- Git — Documentation de `merge` : https://git-scm.com/docs/git-merge
- Git — Documentation de `rebase` : https://git-scm.com/docs/git-rebase
- Git — Documentation de `cherry-pick` : https://git-scm.com/docs/git-cherry-pick
- Git — Documentation de `branch` : https://git-scm.com/docs/git-branch
- Git — Documentation de `tag` : https://git-scm.com/docs/git-tag

### Protection et collaboration

- GitHub Docs — Protection des branches : https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub Docs — Configuration des règles de branche : https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule
- GitLab Docs — Branches protégées : https://docs.gitlab.com/user/project/repository/branches/protected/
- GitLab Docs — Flux de merge requests : https://docs.gitlab.com/user/project/merge_requests/authorization_for_merge_requests/
- GitLab Docs — Règles d'approbation des merge requests : https://docs.gitlab.com/user/project/merge_requests/approvals/rules/

### Versions et releases

- Semantic Versioning — Spécification officielle 2.0.0 : https://semver.org/

La documentation officielle de la plateforme utilisée doit être consultée avant de mettre en œuvre les règles exactes de protection, de fusion et de déclenchement des pipelines. Les fonctionnalités disponibles peuvent différer selon les plateformes, versions et éditions.

## 29. Synthèse du niveau expert

Une stratégie de branching définit l'organisation des modifications, leur trajectoire dans l'historique et les règles qui permettent de les intégrer en sécurité.

Les idées essentielles sont les suivantes :

**GitHub Flow** privilégie une branche principale et des branches de travail courtes. Il convient à de nombreux services qui peuvent livrer régulièrement.

**Trunk-Based Development** cherche à intégrer très fréquemment les modifications dans une branche centrale. Il dépend d'une CI fiable, de changements limités et d'une bonne maîtrise des fonctionnalités incomplètes.

**GitFlow** distingue le développement courant, les releases et les hotfixes. Il peut convenir aux produits dont les versions suivent un cycle structuré, mais sa complexité peut être excessive pour des services livrés en continu.

**GitLab Flow** regroupe plusieurs manières d'organiser l'intégration, la gestion des versions et la promotion des changements selon les besoins du projet.

**Les branches de maintenance** deviennent nécessaires lorsque plusieurs versions du produit doivent recevoir des corrections distinctes.

**Les branches d'environnement** ne doivent pas être multipliées sans raison. Lorsqu'une même version est promue entre plusieurs environnements, la traçabilité des artefacts et le contrôle des déploiements peuvent offrir une solution plus simple que des fusions permanentes entre branches.

**Les hotfixes et backports** nécessitent une politique explicite pour que les corrections atteignent toutes les versions concernées.

**Les règles de protection et les contrôles CI/CD** empêchent qu'une branche critique soit modifiée ou publiée sans les vérifications adaptées.

Enfin, la stratégie optimale n'est pas celle qui possède le plus de branches ou qui suit le modèle le plus connu. C'est celle qui réduit les frictions d'intégration tout en répondant aux contraintes réelles de livraison, de sécurité, de maintenance et de gouvernance du projet.

Une équipe efficace choisit un modèle compréhensible, définit les exceptions nécessaires, mesure les résultats et fait évoluer ses règles lorsque les besoins du produit changent.