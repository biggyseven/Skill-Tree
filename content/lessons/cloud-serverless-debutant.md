# Architectures Serverless — Débutant

> **Mise en contexte**
>
> Imagine que tu développes une application web pour Skill-Tree. Un utilisateur s'inscrit, réalise un quiz, gagne des points d'expérience et reçoit une notification. Tu dois exécuter du code, enregistrer des résultats, exposer une API et gérer les pics de trafic.
>
> Dans une architecture classique, tu peux devoir gérer des serveurs, installer les environnements d'exécution, surveiller leur disponibilité et augmenter leur capacité lorsque le nombre d'utilisateurs augmente. Une architecture serverless te permet de déléguer une grande partie de cette gestion au fournisseur cloud.
>
> Tu restes responsable de la logique applicative, des données, de la sécurité et de la qualité de ton application. Le fournisseur prend en charge une grande partie de l'infrastructure sous-jacente.

## 1. Objectifs pédagogiques

À la fin de ce cours, tu devras être capable de :

- Expliquer le principe du serverless et comprendre pourquoi le terme ne signifie pas « sans serveurs ».
- Distinguer une fonction serverless, un service managé et une architecture complète.
- Identifier les principaux composants d'une architecture serverless.
- Comprendre les événements, les déclencheurs, les fonctions et les services de stockage.
- Différencier les traitements synchrones et asynchrones.
- Reconnaître les avantages, les limites et les risques de cette approche.
- Concevoir une architecture serverless simple pour une application web.
- Écrire et tester localement une fonction inspirée du modèle serverless.
- Appliquer les principes fondamentaux de sécurité, de fiabilité et de maîtrise des coûts.

## 2. Prérequis

Aucune expérience du serverless n'est nécessaire.

Il est cependant utile de connaître les notions suivantes :

- Une application est un ensemble de programmes qui réalisent des tâches.
- Une API permet à des applications de communiquer.
- Une base de données conserve des informations.
- Un événement correspond à un fait qui vient de se produire.
- Le cloud permet d'utiliser des ressources informatiques fournies à distance.

Un peu de Python sera utilisé dans les travaux pratiques. Les exemples seront expliqués étape par étape.

## 3. Comprendre le serverless

### 3.1. Qu'est-ce que le serverless ?

Le serverless est une approche de conception et d'hébergement dans laquelle le fournisseur cloud prend en charge une grande partie de la gestion de l'infrastructure.

Le développeur peut notamment écrire du code, le déployer, le connecter à des événements et le laisser s'exécuter lorsque cela est nécessaire.

Le fournisseur gère généralement une partie importante des opérations suivantes :

- La mise à disposition de l'environnement d'exécution.
- La gestion des machines physiques et de l'infrastructure sous-jacente.
- Une partie de la mise à l'échelle.
- La maintenance de la plateforme.
- La gestion de la capacité nécessaire à l'exécution.

Le niveau de responsabilité exact dépend du service choisi et de sa configuration.

### 3.2. Pourquoi le mot « serverless » ?

Le terme anglais *serverless* signifie littéralement « sans serveur ».

Cependant, le code s'exécute toujours sur des serveurs physiques ou virtuels. Ces serveurs ne disparaissent pas : ils sont gérés en grande partie par le fournisseur cloud et sont moins directement visibles pour le développeur.

Prenons un exemple.

Tu souhaites qu'un programme envoie un message lorsqu'un nouvel utilisateur termine son inscription.

Avec une approche traditionnelle, tu pourrais héberger un programme permanent sur une machine virtuelle et gérer son environnement.

Avec une fonction serverless, tu peux définir le comportement à exécuter lorsque l'événement « inscription terminée » se produit. La plateforme se charge alors de l'exécution selon les règles que tu as configurées.

### 3.3. Exemple concret

Une boutique en ligne reçoit des commandes.

Quand une commande est créée, plusieurs actions doivent être réalisées :

1. Vérifier les informations de la commande.
2. Enregistrer la commande.
3. Envoyer une confirmation.
4. Actualiser les statistiques de vente.

Toutes ces opérations ne nécessitent pas nécessairement un programme permanent qui attend en continu une nouvelle commande.

Une architecture serverless peut déclencher des traitements spécifiques à partir de l'événement de création de la commande.

### 3.4. Les trois notions à ne pas confondre

**Le serverless comme approche architecturale**

Il s'agit de la manière dont les différents composants d'une application sont organisés pour fonctionner à partir de services managés, d'événements et de ressources dont l'exploitation est largement déléguée au fournisseur.

**La fonction serverless**

C'est une unité de code exécutée par une plateforme lorsqu'une requête ou un événement déclenche son exécution. Ce modèle est souvent appelé *Function as a Service* (FaaS).

**Les services cloud managés**

Ce sont des services dont le fournisseur gère une partie importante de l'infrastructure et de l'exploitation. Ils peuvent servir à stocker des fichiers, conserver des données, exposer une API ou acheminer des messages.

Une architecture serverless complète utilise généralement plusieurs de ces composants ensemble.

## 4. L'évolution de l'hébergement des applications

Pour comprendre l'intérêt du serverless, comparons quatre approches.

### 4.1. Machine virtuelle : IaaS

IaaS signifie *Infrastructure as a Service*.

Le fournisseur met à disposition une infrastructure informatique. Tu disposes d'une machine virtuelle sur laquelle tu peux installer ton système d'exploitation, ton environnement logiciel et ton application.

Schéma :

```text
┌──────────────────────────────────┐
│ Application                       │
├──────────────────────────────────┤
│ Bibliothèques et runtime          │
├──────────────────────────────────┤
│ Système d'exploitation             │
├──────────────────────────────────┤
│ Machine virtuelle                  │
├──────────────────────────────────┤
│ Infrastructure du cloud            │
└──────────────────────────────────┘
```

Tu dois généralement assurer une partie importante de la configuration, de la maintenance, de la surveillance, de la capacité et des mises à jour du système.

**Exemple :** installer une application Python sur une machine virtuelle Linux et gérer son serveur web.

### 4.2. Plateforme managée : PaaS

PaaS signifie *Platform as a Service*.

Le fournisseur prend en charge davantage de composants de la plateforme. Tu te concentres plus directement sur ton application et sur son déploiement.

Le niveau de gestion du système d'exploitation, de l'environnement d'exécution et de la mise à l'échelle dépend du service choisi.

**Exemple :** héberger une application web sur une plateforme qui gère son environnement d'exécution.

### 4.3. Fonctions serverless : FaaS

FaaS signifie *Function as a Service*.

Tu déploies des unités de code appelées fonctions, associées à des déclencheurs et à des règles d'exécution.

Schéma :

```text
        Un événement se produit
                  |
                  v
       ┌─────────────────────┐
       │ Déclencheur          │
       └──────────┬──────────┘
                  |
                  v
       ┌─────────────────────┐
       │ Fonction serverless  │
       └──────────┬──────────┘
                  |
             ┌────┴────┐
             v         v
       ┌──────────┐ ┌──────────┐
       │ Base de   │ │ Service  │
       │ données   │ │ externe  │
       └──────────┘ └──────────┘
```

La plateforme gère l'environnement d'exécution et une partie importante de la mise à l'échelle. La fonction peut être exécutée à la suite d'une requête HTTP, d'un message, d'un événement de stockage ou d'une planification.

### 4.4. Conteneurs serverless

Le serverless ne se limite pas aux fonctions.

Certaines plateformes permettent également de déployer des applications complètes sous forme de conteneurs sans gérer directement les serveurs qui les hébergent.

Cette approche convient notamment à des applications web, des API ou des programmes qui doivent traiter des requêtes HTTP de manière continue, selon la configuration du service.

**À retenir :** FaaS désigne principalement l'exécution de fonctions, tandis que les plateformes de conteneurs serverless peuvent exécuter des applications plus complètes.

## 5. Les principaux composants d'une architecture serverless

Une architecture serverless se compose rarement d'une seule fonction isolée. Elle associe généralement plusieurs services spécialisés.

### 5.1. Le déclencheur : trigger

Un *trigger* est un mécanisme qui déclenche l'exécution d'une fonction.

Les déclencheurs courants comprennent :

| Type de déclencheur | Exemple |
|---|---|
| Requête HTTP | Un utilisateur demande le résultat d'un quiz. |
| Téléversement de fichier | Un utilisateur dépose une image. |
| Message | Une commande arrive dans une file d'attente. |
| Événement de base de données | Un document est créé ou modifié. |
| Planification | Une tâche doit s'exécuter chaque nuit. |
| Événement applicatif | Un utilisateur termine un cours. |

Le déclencheur détermine dans quelles circonstances le code peut être exécuté.

### 5.2. La fonction

Une fonction contient la logique métier à exécuter.

Par exemple, une fonction peut :

- Calculer la note obtenue à un quiz.
- Vérifier si une commande est valide.
- Transformer un fichier.
- Générer un rapport.
- Préparer une notification.
- Contrôler les données reçues par une API.

Une fonction doit rester suffisamment claire pour que son comportement soit compréhensible, testable et maintenable.

### 5.3. L'API Gateway

Une passerelle d'API, ou *API Gateway*, constitue un point d'entrée pour les appels d'API.

Elle peut notamment fournir des fonctions telles que :

- Le routage des requêtes vers les bons traitements.
- La gestion de l'authentification selon la configuration.
- L'application de quotas et de limites de débit.
- La validation de certaines requêtes.
- La collecte de données de surveillance.

Illustration :

```text
Navigateur
    |
    | HTTPS : GET /cours/42
    v
┌──────────────────┐
│ Passerelle d'API  │
└────────┬─────────┘
         |
         v
┌──────────────────┐
│ Fonction          │
│ get_cours         │
└────────┬─────────┘
         |
         v
┌──────────────────┐
│ Base de données   │
└──────────────────┘
```

Une passerelle d'API est fréquente dans les architectures serverless orientées API, mais tous les services n'en exigent pas une : certaines plateformes peuvent exposer directement un endpoint HTTP.

### 5.4. Le stockage de données

Une application doit conserver ses informations au-delà de l'exécution d'une fonction.

Pour cela, elle peut utiliser différents services :

- Une base de données relationnelle.
- Une base de données orientée documents.
- Un stockage d'objets pour les fichiers.
- Un service de stockage clé-valeur.
- Un service de stockage de secrets.

Le choix dépend du type de données, des contraintes de cohérence, des accès attendus et des exigences de performance.

**Principe important :** ne considère pas la mémoire d'une fonction ni son système de fichiers local temporaire comme un stockage permanent et fiable de ton application. Une instance d'exécution peut disparaître ou être remplacée. Les données importantes doivent être conservées dans un service de stockage adapté.

### 5.5. La file d'attente de messages

Une file d'attente, ou *queue*, permet de transmettre un travail à réaliser sans obliger le composant qui produit ce travail à attendre la fin du traitement.

Prenons l'exemple d'une notification.

```text
Création de commande
         |
         v
┌──────────────────┐
│ File d'attente    │
└────────┬─────────┘
         |
         v
┌──────────────────┐
│ Fonction          │
│ de notification   │
└────────┬─────────┘
         |
         v
  Service de messagerie
```

La commande peut être enregistrée rapidement. L'envoi de la notification est réalisé séparément.

Une file d'attente peut également permettre de lisser un pic de trafic lorsque beaucoup de messages arrivent en même temps.

Elle ne supprime cependant pas la nécessité de prévoir des mécanismes de reprise, de surveillance et de gestion des messages qui échouent.

### 5.6. Les services d'observabilité

Une application doit permettre de comprendre ce qu'il se passe en production.

Trois éléments sont particulièrement utiles :

**Les journaux (*logs*)** : ils enregistrent des événements, des erreurs et des informations de diagnostic.

**Les métriques** : elles indiquent, par exemple, le nombre d'invocations, la durée des traitements, le taux d'erreur et la consommation de ressources.

**Les traces distribuées** : elles permettent de suivre une requête lorsqu'elle traverse plusieurs composants.

Sans ces outils, une architecture composée de nombreuses fonctions peut devenir difficile à diagnostiquer.

### 5.7. Les services de sécurité

Une architecture serverless doit aussi gérer :

- L'identité des utilisateurs.
- Les permissions des fonctions.
- Les secrets et les clés d'accès.
- Le chiffrement des données.
- La protection des endpoints.
- La limitation des abus.
- L'audit des accès.

Le fait de déléguer l'infrastructure au fournisseur ne signifie pas que la sécurité est entièrement prise en charge automatiquement. La configuration du compte cloud, des autorisations et de l'application reste déterminante.

## 6. Comment fonctionne une fonction serverless ?

Le déroulement typique peut être décrit en six étapes.

1. Un événement ou une requête se produit.
2. La plateforme détecte le déclencheur configuré.
3. Elle met à disposition un environnement d'exécution si nécessaire.
4. Le code de la fonction s'exécute avec les paramètres reçus.
5. La fonction retourne un résultat ou réalise une action.
6. La plateforme collecte des informations d'exécution et applique ses règles de gestion.

Exemple : un utilisateur demande une note.

```text
Utilisateur
    |
    | Demande de résultat
    v
Déclencheur HTTP
    |
    v
Fonction de calcul
    |
    +----> Lecture des réponses enregistrées
    |
    +----> Calcul de la note
    |
    +----> Enregistrement du résultat
    |
    v
Réponse HTTP
    |
    v
Utilisateur
```

Ce schéma représente une architecture simplifiée. Dans une application réelle, la lecture et l'enregistrement peuvent être réalisés par des composants distincts.

### 6.1. L'événement et le contexte

Une fonction reçoit généralement des informations lui permettant de savoir pourquoi elle est appelée et quelles données elle doit traiter.

Un événement pourrait contenir :

```json
{
  "type": "quiz_termine",
  "utilisateur_id": 125,
  "quiz_id": 42,
  "score": 85
}
```

La fonction peut examiner ces données pour décider de la suite du traitement.

Dans certains environnements, le fournisseur transmet aussi un contexte d'exécution qui contient des informations supplémentaires. La forme exacte de l'événement et du contexte dépend de la plateforme et du déclencheur.

### 6.2. Une fonction doit-elle conserver son état ?

En règle générale, il faut concevoir une fonction comme un traitement qui peut être exécuté indépendamment des autres invocations.

Supposons qu'une fonction soit appelée pour traiter une commande :

```text
Invocation A : commande 1001
Invocation B : commande 1002
Invocation C : commande 1003
```

Il ne faut pas supposer que les trois invocations partageront la même mémoire, s'exécuteront sur la même instance ou seront traitées dans un ordre particulier.

L'état important doit donc être conservé dans un stockage externe adapté.

Une plateforme peut réutiliser un environnement d'exécution entre plusieurs invocations, mais cette réutilisation ne doit pas devenir une garantie applicative.

## 7. L'architecture événementielle

Le serverless est très souvent associé à une architecture événementielle, également appelée *event-driven architecture*.

Dans cette approche, les composants réagissent à des événements plutôt que de devoir constamment interroger les autres composants pour vérifier si quelque chose a changé.

### 7.1. Exemple : inscription sur Skill-Tree

Lorsqu'un utilisateur termine une inscription, l'application émet un événement.

```text
              Nouvel utilisateur
                     |
                     v
          ┌────────────────────┐
          │ Événement           │
          │ utilisateur_créé    │
          └─────────┬──────────┘
                    |
            ┌───────┼────────┐
            v       v        v
     ┌──────────┐ ┌───────┐ ┌───────────┐
     │ Profil   │ │ Email │ │ Statistiques│
     │ initial  │ │ bienvenue│ │ globales  │
     └──────────┘ └───────┘ └───────────┘
```

Plusieurs traitements peuvent réagir au même événement.

Les composants sont ainsi moins directement dépendants les uns des autres. Toutefois, l'architecture devient plus complexe à surveiller, à tester et à déboguer.

### 7.2. Couplage fort et couplage faible

Un couplage fort signifie que plusieurs composants dépendent étroitement de l'interface ou du fonctionnement interne des autres.

Par exemple, une fonction d'inscription qui appelle successivement cinq autres services de manière synchrone peut devenir très dépendante de leur disponibilité.

Un couplage plus faible peut être obtenu en transmettant un événement à un service de messagerie, puis en laissant les autres composants traiter cet événement séparément.

Cela ne signifie pas que le couplage disparaît. Les composants doivent toujours s'accorder sur le format des messages, leur signification, leur version et les règles de traitement.

### 7.3. Traitement synchrone

Un traitement est synchrone lorsque l'appelant attend une réponse avant de poursuivre son opération.

```text
Client
  |
  v
API
  |
  v
Fonction
  |
  v
Résultat
  |
  v
Réponse au client
```

Exemples :

- Calculer immédiatement le prix d'une commande.
- Retourner le contenu d'un cours.
- Vérifier les informations d'un formulaire.
- Calculer un résultat de quiz.

Le traitement synchrone est utile lorsque l'utilisateur attend directement le résultat.

### 7.4. Traitement asynchrone

Un traitement est asynchrone lorsqu'un composant peut transmettre une tâche à un autre sans attendre nécessairement la fin de cette tâche.

```text
Client
  |
  v
API
  |
  v
Enregistrement de la demande
  |
  v
File d'attente
  |
  v
Traitement en arrière-plan
  |
  v
Résultat ou notification
```

Exemples :

- Envoyer un courriel.
- Générer un rapport volumineux.
- Traiter des fichiers.
- Mettre à jour des statistiques.
- Exécuter un traitement qui peut durer plus longtemps que le délai acceptable pour une requête HTTP.

Dans une architecture asynchrone, il faut réfléchir à la manière dont l'utilisateur sera informé de la fin du travail et aux conséquences d'un échec.

## 8. Les principaux modèles d'architecture serverless

### 8.1. API serverless

Ce modèle associe généralement une API à une ou plusieurs fonctions et à des services de stockage.

```text
Navigateur ou application mobile
                 |
                 v
           Passerelle API
                 |
           ┌─────┴─────┐
           v           v
     Fonction A   Fonction B
           |           |
           v           v
     Base de données   Service externe
```

**Cas d'utilisation :** une application web qui affiche des cours, enregistre les quiz et retourne la progression de chaque utilisateur.

### 8.2. Traitement de fichiers

Une fonction est déclenchée lorsqu'un fichier est déposé dans un espace de stockage.

```text
Dépôt d'un fichier
        |
        v
Stockage d'objets
        |
        v
Événement de dépôt
        |
        v
Fonction de traitement
        |
        v
Fichier transformé
```

**Cas d'utilisation :** produire une miniature d'image, vérifier un document ou extraire des métadonnées d'un fichier.

Il faut prévoir la gestion des formats invalides, des tailles excessives, des fichiers malveillants et des échecs de traitement.

### 8.3. Architecture pilotée par une file d'attente

Une application enregistre les tâches à traiter et les transmet à une file.

```text
Application
    |
    v
File de messages
    |
    v
Fonction de traitement
    |
    v
Base de données ou service externe
```

**Cas d'utilisation :** traiter des commandes, envoyer des notifications ou exécuter des tâches qui peuvent être réparties dans le temps.

### 8.4. Traitement planifié

Une règle de planification déclenche une fonction à intervalles définis.

```text
Planificateur
      |
      | Déclenchement programmé
      v
Fonction
      |
      +----> Calcul du bilan quotidien
      |
      +----> Nettoyage des données temporaires
      |
      +----> Vérification de tâches arrivées à échéance
```

**Cas d'utilisation :** établir un bilan quotidien, nettoyer les données temporaires ou vérifier périodiquement l'état d'un processus.

Une planification doit tenir compte du fuseau horaire, des exécutions qui se chevauchent et des éventuelles relances.

## 9. Les avantages du serverless

### 9.1. Moins de gestion de l'infrastructure

Le fournisseur prend en charge une partie importante des tâches liées à l'exploitation de l'environnement d'exécution.

L'équipe peut consacrer davantage de temps aux fonctionnalités, aux tests, aux données et à l'expérience utilisateur.

### 9.2. Mise à l'échelle automatique

Les plateformes serverless peuvent ajuster automatiquement leur capacité en fonction de la charge, selon le service et la configuration.

Imaginons une application recevant un faible nombre de demandes le matin puis un nombre élevé de demandes lors de la publication d'un nouveau cours.

Une plateforme adaptée peut augmenter le nombre d'exécutions disponibles pour répondre à la demande.

Cette capacité n'est pas illimitée : des quotas, des limites de concurrence et des restrictions d'autres services peuvent s'appliquer.

### 9.3. Facturation liée à l'utilisation

De nombreux services serverless facturent une partie de leur usage en fonction de mesures telles que les invocations, la durée d'exécution ou les ressources consommées.

L'intérêt est particulièrement important pour des applications dont la charge varie fortement.

Cependant, tous les composants ne sont pas nécessairement facturés uniquement à l'invocation. Un service de stockage, une base de données, un endpoint configuré pour rester disponible ou des journaux peuvent également générer des coûts.

### 9.4. Rapidité de développement

Les fonctions peuvent être développées et testées comme de petits composants indépendants.

Cette organisation peut simplifier la création de traitements ponctuels ou événementiels.

### 9.5. Intégration avec les services cloud

Les fournisseurs mettent à disposition des mécanismes pour connecter les fonctions à des API, des files de messages, des bases de données, des espaces de stockage et des services d'identité.

Ces intégrations peuvent réduire la quantité de code nécessaire pour orchestrer les opérations.

## 10. Les limites et les difficultés du serverless

Le serverless n'est pas une solution universelle. Il déplace certaines responsabilités plutôt qu'il ne supprime tous les problèmes.

### 10.1. Le démarrage à froid

Un démarrage à froid, ou *cold start*, peut se produire lorsque la plateforme doit préparer un nouvel environnement d'exécution avant de lancer le traitement.

Ce phénomène peut ajouter un délai à la première requête traitée par cet environnement.

Sa fréquence et son impact dépendent notamment de la plateforme, du runtime, de la taille du programme, de la charge et des options de configuration.

Pour des applications très sensibles à la latence, il faut mesurer les performances réelles et choisir une configuration appropriée.

### 10.2. Les limites d'exécution

Une fonction possède des contraintes définies par le fournisseur : durée maximale, mémoire, ressources disponibles, concurrence et autres limites.

Une tâche qui dure longtemps ou qui nécessite un environnement spécifique n'est donc pas automatiquement adaptée à une fonction serverless.

Il faut choisir le bon service : fonction, tâche sur conteneur, service web, traitement par lots ou autre solution.

### 10.3. La difficulté de débogage

Dans une application traditionnelle, une grande partie du traitement peut se produire dans un seul processus.

Dans une architecture événementielle, une requête peut traverser plusieurs fonctions, files d'attente et services externes.

Une erreur peut donc se produire à différentes étapes. La surveillance, l'identifiant de corrélation et les traces distribuées deviennent importants.

### 10.4. La dépendance au fournisseur

Chaque fournisseur dispose de ses propres formats d'événements, services, interfaces de configuration et mécanismes d'autorisation.

Une application fortement intégrée à ces services peut demander un travail conséquent pour être déplacée vers un autre environnement.

Utiliser des standards, séparer la logique métier des interfaces cloud et tester les composants peut limiter certaines dépendances, sans les éliminer totalement.

### 10.5. Le risque de coûts inattendus

Une facturation liée à l'usage ne signifie pas nécessairement que l'application sera moins chère.

Un endpoint exposé publiquement, une boucle involontaire, un traitement qui relance constamment les mêmes messages ou des journaux trop volumineux peuvent augmenter les coûts.

Il faut donc surveiller les consommations, définir des alertes et limiter les usages anormaux.

### 10.6. L'importance des dépendances externes

Même si une fonction s'adapte automatiquement à la charge, une base de données ou une API externe peut ne pas suivre le même rythme.

Par exemple, dix mille invocations simultanées peuvent provoquer trop de connexions vers une base de données.

La mise à l'échelle doit être étudiée à l'échelle de l'architecture complète, et non uniquement à celle des fonctions.

## 11. Comprendre les tentatives répétées et l'idempotence

Cette notion est fondamentale dans le serverless.

Un service de messagerie peut retransmettre un message si le traitement échoue ou si sa confirmation n'est pas reçue à temps. Selon le système, un même événement peut donc être traité plus d'une fois.

Supposons qu'une fonction attribue 50 points d'expérience pour une activité terminée.

Si le même événement est traité deux fois et que la fonction ajoute simplement 50 points à chaque invocation, l'utilisateur recevra 100 points au lieu de 50.

### 11.1. Le principe d'idempotence

Une opération est idempotente lorsqu'une répétition de la même opération ne produit pas d'effet supplémentaire après que le résultat attendu a été atteint.

Pour notre exemple, au lieu d'ajouter automatiquement 50 points chaque fois qu'un événement arrive, l'application pourrait enregistrer l'identifiant unique de l'activité validée et vérifier si la récompense a déjà été attribuée.

```text
Événement : activité terminée
              |
              v
      Vérifier event_id
              |
        ┌─────┴─────┐
        |           |
    Déjà traité    Nouveau
        |           |
        v           v
   Aucun nouvel   Attribuer les
   effet métier   points une fois
                    |
                    v
             Enregistrer event_id
```

L'enregistrement de l'identifiant et l'attribution de la récompense doivent être conçus de façon à éviter les problèmes de concurrence, idéalement dans une transaction ou avec un mécanisme de déduplication fiable.

**À retenir :** ne suppose pas qu'un événement sera nécessairement livré et traité une seule fois.

## 12. Sécurité d'une architecture serverless

La sécurité doit être prise en compte dès la conception.

### 12.1. Le principe du moindre privilège

Chaque fonction doit disposer uniquement des autorisations nécessaires à son travail.

Exemple :

- Une fonction de lecture de cours reçoit une permission de lecture sur les données concernées.
- Une fonction de création de commande reçoit les permissions nécessaires à l'enregistrement des commandes.
- Une fonction de notification n'a pas besoin d'un accès administrateur à l'ensemble du compte cloud.

Des permissions trop larges augmentent l'impact potentiel d'une erreur ou d'une compromission.

### 12.2. Protéger les secrets

Les mots de passe, jetons d'API et clés privées ne doivent pas être inscrits en clair dans le code source ni publiés dans un dépôt Git.

Utilise les mécanismes de gestion des secrets adaptés à la plateforme. Les secrets doivent être accessibles uniquement aux composants autorisés et renouvelés lorsque cela est nécessaire.

### 12.3. Valider les données

Une fonction exposée par HTTP doit vérifier les données reçues.

Elle doit notamment :

- Vérifier la présence des champs obligatoires.
- Contrôler les types et les formats.
- Limiter les valeurs autorisées et les tailles.
- Rejeter les entrées invalides.
- Ne pas exposer de données confidentielles dans les messages d'erreur.

La validation des entrées ne remplace pas l'authentification, l'autorisation ni la protection contre les abus.

### 12.4. Protéger les données

Selon le service utilisé, il peut être nécessaire de configurer :

- Le chiffrement au repos.
- Le chiffrement des communications.
- Les règles d'accès au stockage.
- Les sauvegardes et la restauration.
- La conservation et la suppression des données.
- Les politiques d'audit et de journalisation.

### 12.5. Une sécurité partagée

Le fournisseur est responsable de la sécurité de l'infrastructure qu'il exploite. Le client reste responsable de nombreux éléments de sa propre solution, notamment le code, les données, les permissions et les configurations qu'il choisit.

La répartition exacte varie selon le modèle de service et le contrat cloud.

## 13. Comparaison des principales plateformes

Les trois grands environnements cloud proposent des mécanismes adaptés à la construction de solutions serverless.

| Fournisseur | Exécution de fonctions | Services complémentaires possibles |
|---|---|---|
| AWS | AWS Lambda | API Gateway, S3, SQS, EventBridge, DynamoDB |
| Microsoft Azure | Azure Functions | API Management, Blob Storage, Service Bus, Event Grid, Cosmos DB |
| Google Cloud | Cloud Run functions et Cloud Run | Cloud Storage, Pub/Sub, Eventarc, Firestore |

### 13.1. AWS

AWS Lambda permet d'exécuter du code en réponse à des événements ou à des appels d'API sans gérer directement les serveurs sous-jacents.

Exemple de chaîne :

```text
Client HTTP
    |
    v
Amazon API Gateway
    |
    v
AWS Lambda
    |
    v
Amazon DynamoDB
```

Les événements peuvent également provenir d'autres services AWS, notamment le stockage d'objets, les files d'attente ou les services de routage d'événements.

### 13.2. Microsoft Azure

Azure Functions fournit un environnement d'exécution pour des traitements événementiels et planifiés.

Exemple :

```text
Événement de stockage
        |
        v
Azure Functions
        |
        v
Stockage ou base de données
```

Azure Functions propose plusieurs options d'hébergement. Les capacités de mise à l'échelle, la disponibilité permanente et la facturation dépendent du plan choisi.

### 13.3. Google Cloud

Cloud Run functions permet de déployer des fonctions déclenchées par des requêtes HTTP ou par des événements compatibles. Cloud Run permet aussi d'exécuter des services et des tâches conteneurisés dans un environnement managé.

Exemple :

```text
Événement
    |
    v
Eventarc ou autre déclencheur
    |
    v
Cloud Run functions
    |
    v
Stockage ou service de données
```

Le choix entre fonctions et services conteneurisés dépend du type de traitement, du modèle de déploiement, des dépendances logicielles et des exigences de fonctionnement.

### 13.4. Comment choisir ?

Le bon choix ne dépend pas uniquement du nom du fournisseur.

Évalue notamment :

- Les besoins de l'application.
- Les technologies déjà utilisées.
- Les services de données nécessaires.
- Les exigences de sécurité et de conformité.
- La latence et la durée d'exécution.
- Les limites de concurrence et de capacité.
- Le coût global.
- Les compétences disponibles dans l'équipe.

Une architecture serverless correctement conçue est plus importante que le simple choix d'une fonction dans un catalogue cloud.

## 14. Concevoir une architecture serverless pour Skill-Tree

Imaginons que Skill-Tree utilise une architecture serverless pour une partie de son application pédagogique.

Les fonctionnalités demandées sont les suivantes :

1. Afficher les cours.
2. Enregistrer les résultats des quiz.
3. Attribuer des points d'expérience.
4. Envoyer une notification lorsqu'une activité est terminée.
5. Produire des statistiques quotidiennes.

Une architecture possible serait :

```text
             Navigateur Skill-Tree
                      |
                      | HTTPS
                      v
              ┌──────────────┐
              │ API Gateway   │
              └──────┬───────┘
                     |
          ┌──────────┼───────────┐
          v          v           v
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Cours    │ │ Quiz     │ │ Profil   │
    │ Function │ │ Function │ │ Function │
    └────┬─────┘ └────┬─────┘ └────┬─────┘
         |            |            |
         └────────────┼────────────┘
                      v
             ┌─────────────────┐
             │ Stockage durable │
             └─────────────────┘
```

Après un quiz validé, le traitement pourrait produire un événement :

```text
Quiz validé
    |
    v
Événement de progression
    |
    v
File d'attente ou bus d'événements
    |
    ├──> Attribution des XP
    |
    ├──> Mise à jour des statistiques
    |
    └──> Notification de l'utilisateur
```

### 14.1. Pourquoi séparer les traitements ?

Toutes les actions n'ont pas les mêmes exigences.

L'affichage d'un résultat doit généralement répondre rapidement à l'utilisateur.

L'envoi d'un courriel ou la production d'un bilan peut être traité séparément.

La séparation permet d'ajuster les composants indépendamment et de mieux isoler certains échecs.

### 14.2. Que faut-il surveiller ?

Pour cette architecture, il faudrait notamment surveiller :

- Le temps de réponse des endpoints.
- Le taux d'erreur des fonctions.
- Le nombre de messages en attente.
- Les messages qui échouent plusieurs fois.
- Les connexions et les performances de la base de données.
- Les coûts par fonctionnalité.
- Les erreurs d'autorisation.
- Les doublons lors de l'attribution des XP.

### 14.3. Faut-il migrer toute l'application ?

Non. Le serverless n'impose pas de transformer chaque composant d'une application en fonction.

Skill-Tree peut conserver une API FastAPI et une base SQLite dans un environnement adapté, puis introduire des services serverless pour des fonctions précises, des événements ou des tâches planifiées.

Une migration doit répondre à un problème concret : simplicité d'exploitation, besoin de mise à l'échelle, traitement événementiel, disponibilité ou coût global.

Une solution hybride peut être plus pertinente qu'une réécriture complète.

## 15. Parcours pratique du débutant

Ce parcours est conçu pour être suivi progressivement, sans exiger de compte cloud payant.

### Étape 1 — Comprendre le principe

Prends une fonctionnalité que tu connais : calculer le score d'un quiz.

Identifie :

- L'événement : le quiz vient d'être terminé.
- Les entrées : les réponses de l'utilisateur et les bonnes réponses.
- Le traitement : calculer le score.
- La sortie : retourner la note.
- Le stockage éventuel : enregistrer le résultat.

### Étape 2 — Écrire une fonction indépendante

Commence par une fonction Python qui reçoit des données et retourne un résultat.

À cette étape, elle n'a pas besoin d'API, de serveur ni de compte cloud.

### Étape 3 — Tester les cas normaux et les erreurs

Prévois des données valides, des données manquantes et des valeurs invalides.

### Étape 4 — Imaginer le déclencheur

Détermine comment la fonction serait appelée dans un environnement cloud : requête HTTP, événement métier, message ou planification.

### Étape 5 — Ajouter la persistance

Si le traitement doit conserver son résultat, prévois une base de données ou un stockage adapté. Ne compte pas sur la mémoire temporaire de la fonction.

### Étape 6 — Envisager le déploiement

Choisis un fournisseur et identifie son environnement d'exécution, ses permissions, son mécanisme de déclenchement et ses outils de surveillance.

Ne déploie pas une fonction simplement parce qu'elle fonctionne localement : vérifie aussi les accès, les limites, la gestion des erreurs et les coûts.

## 16. Travaux pratiques — Simuler un traitement serverless pour le Lab Workspace de Skill-Tree

### Objectif du TP

Dans Skill-Tree, un utilisateur peut réaliser un lab de réseau, configurer une topologie, vérifier sa configuration et soumettre son travail.

Lorsqu'il termine un lab, plusieurs opérations peuvent être nécessaires :

1. Enregistrer sa tentative.
2. Indiquer si le lab est réussi ou échoué.
3. Attribuer les points d'expérience (XP) si les conditions sont remplies.
4. Actualiser le total d'XP de l'utilisateur.
5. Éviter qu'un même événement attribue plusieurs fois la même récompense.
6. Préparer les traitements complémentaires, comme la mise à jour des badges ou des statistiques.

Dans une architecture traditionnelle, ces opérations peuvent être réalisées directement dans le backend FastAPI.

Dans une architecture serverless événementielle, le backend pourrait enregistrer la tentative, puis transmettre un événement à un traitement chargé de gérer les récompenses et certaines opérations secondaires.

Le but de ce TP est de comprendre ce mécanisme avec une simulation locale utilisant Python et SQLite.

**Important :** ce TP crée une petite base SQLite de démonstration distincte de `skilltree.db`. Il ne modifie pas la base réelle de Skill-Tree et ne remplace pas les endpoints existants de Lab Workspace v2.

### 16.1. Architecture du traitement

Nous allons simuler le scénario suivant :

```text
                  Utilisateur Skill-Tree
                          |
                          v
                  Lab Workspace v2
                          |
                          v
                   Soumission du lab
                          |
                          v
                  Vérification du lab
                          |
                          v
                 Enregistrement de la
                      tentative
                          |
                          v
                Événement lab.submitted
                          |
                          v
               ┌──────────────────────┐
               │ Traitement serverless │
               │                      │
               │ 1. Vérifier l'événement│
               │ 2. Détecter les doublons│
               │ 3. Vérifier la réussite│
               │ 4. Calculer les XP     │
               └───────────┬──────────┘
                           |
                 ┌─────────┴─────────┐
                 v                   v
          Historique des       Total d'XP
             tentatives        de l'utilisateur
```

Dans une véritable architecture cloud, l'événement pourrait être transmis par une file d'attente ou un bus d'événements. Ici, nous appellerons directement une fonction Python pour simuler le traitement.

Cette approche nous permet de comprendre la logique avant de configurer un fournisseur cloud.

### 16.2. Définir notre scénario Skill-Tree

Imaginons un utilisateur qui réalise le lab `ospf-3-routers`.

Le lab possède une récompense de 100 XP.

Le résultat de la vérification indique que toutes les règles obligatoires sont satisfaites.

Le backend produit un événement contenant les informations nécessaires au traitement.

Voici un exemple de cet événement :

```json
{
  "event_type": "lab.submitted",
  "event_id": "evt-001",
  "attempt_id": "attempt-001",
  "user_id": "user-42",
  "lab_id": "ospf-3-routers",
  "passed": true,
  "xp_reward": 100
}
```

Les champs ont les rôles suivants :

| Champ | Signification |
|---|---|
| `event_type` | Type d'événement déclenché. |
| `event_id` | Identifiant de l'événement transmis. |
| `attempt_id` | Identifiant stable de la tentative enregistrée. |
| `user_id` | Identifiant de l'utilisateur. |
| `lab_id` | Identifiant du lab concerné. |
| `passed` | Indique si les règles de réussite sont satisfaites. |
| `xp_reward` | Récompense prévue pour le lab. |

L'identifiant de la tentative doit rester identique lorsque le même événement est transmis de nouveau. C'est indispensable pour reconnaître une répétition.

Pour ce TP, nous appliquerons deux règles métier :

- Une tentative n'est enregistrée qu'une seule fois, même si son événement est reçu plusieurs fois.
- Un utilisateur ne reçoit la récompense d'un lab qu'une seule fois, même s'il réussit ce lab à plusieurs reprises.

Les nouvelles tentatives restent visibles dans l'historique. La récompense déjà obtenue n'est simplement pas attribuée une seconde fois.

### 16.3. Créer l'environnement de travail

Crée un dossier dédié, par exemple :

```text
skilltree-serverless-tp/
├── serverless_lab.py
└── skilltree_serverless_demo.db
```

Le fichier Python sera créé à la première étape. Le fichier SQLite sera généré automatiquement pendant l'exécution.

Vérifie que Python est disponible :

```bash
python --version
```

Le TP utilise uniquement la bibliothèque standard de Python. Il ne nécessite ni FastAPI, ni bibliothèque externe, ni compte cloud.

**Précaution :** conserve ce TP dans son propre dossier. N'utilise pas la base réelle `skilltree.db` pour les essais.

### 16.4. Créer le traitement serverless

Crée le fichier `serverless_lab.py` et copie le code ci-dessous.

```python
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


# Base isolée pour le TP.
# Ne pas remplacer ce chemin par celui de la base réelle de Skill-Tree.
DB_PATH = Path(__file__).with_name("skilltree_serverless_demo.db")


def now_utc():
    """Retourne une date UTC au format ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def init_db(db_path=DB_PATH):
    """
    Crée les tables de démonstration.

    Cette base est indépendante de la base de production Skill-Tree.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS demo_lab_attempts (
                attempt_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lab_id TEXT NOT NULL,
                passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
                xp_awarded INTEGER NOT NULL DEFAULT 0,
                processed_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS demo_lab_rewards (
                user_id TEXT NOT NULL,
                lab_id TEXT NOT NULL,
                xp_awarded INTEGER NOT NULL,
                awarded_at TEXT NOT NULL,
                PRIMARY KEY (user_id, lab_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS demo_user_stats (
                user_id TEXT PRIMARY KEY,
                xp_total INTEGER NOT NULL DEFAULT 0
                    CHECK (xp_total >= 0)
            )
        """)


def validate_event(event):
    """Vérifie la structure et les valeurs de l'événement."""

    if not isinstance(event, dict):
        raise ValueError("L'événement doit être un objet.")

    required_fields = (
        "event_type",
        "event_id",
        "attempt_id",
        "user_id",
        "lab_id",
        "passed",
        "xp_reward",
    )

    for field in required_fields:
        if field not in event:
            raise ValueError(f"Champ obligatoire manquant : {field}")

    if event["event_type"] != "lab.submitted":
        raise ValueError("Type d'événement non pris en charge.")

    for field in ("event_id", "attempt_id", "user_id", "lab_id"):
        value = event[field]

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Le champ {field} doit être une chaîne non vide."
            )

    # bool est un sous-type de int en Python.
    # On vérifie donc explicitement que passed est un booléen.
    if not isinstance(event["passed"], bool):
        raise ValueError("Le champ passed doit être un booléen.")

    xp_reward = event["xp_reward"]

    if isinstance(xp_reward, bool) or not isinstance(xp_reward, int):
        raise ValueError("La récompense XP doit être un entier.")

    if not 0 <= xp_reward <= 1000:
        raise ValueError("La récompense XP doit être comprise entre 0 et 1000.")

    return {
        "event_type": event["event_type"],
        "event_id": event["event_id"].strip(),
        "attempt_id": event["attempt_id"].strip(),
        "user_id": event["user_id"].strip(),
        "lab_id": event["lab_id"].strip(),
        "passed": event["passed"],
        "xp_reward": xp_reward,
    }


def process_lab_event(event, db_path=DB_PATH):
    """
    Simule un traitement serverless déclenché après la soumission d'un lab.

    Règles :
    - une tentative identifiée n'est enregistrée qu'une fois ;
    - une tentative échouée ne rapporte aucun XP ;
    - la récompense du lab est attribuée une seule fois par utilisateur ;
    - les modifications SQLite sont regroupées dans une transaction.
    """

    try:
        event = validate_event(event)
    except ValueError as exc:
        return {
            "status": "invalid_event",
            "message": str(exc),
            "xp_gained": 0,
        }

    conn = sqlite3.connect(db_path, timeout=10)

    try:
        conn.execute("BEGIN IMMEDIATE")

        # Une nouvelle livraison du même événement peut survenir.
        # L'identifiant stable de la tentative permet de la reconnaître.
        existing_attempt = conn.execute(
            """
            SELECT user_id, lab_id, passed, xp_awarded
            FROM demo_lab_attempts
            WHERE attempt_id = ?
            """,
            (event["attempt_id"],),
        ).fetchone()

        if existing_attempt is not None:
            conn.rollback()

            # Vérifier qu'un identifiant existant ne soit pas réutilisé
            # accidentellement pour un autre utilisateur ou un autre lab.
            same_attempt = (
                existing_attempt[0] == event["user_id"]
                and existing_attempt[1] == event["lab_id"]
                and existing_attempt[2] == int(event["passed"])
            )

            if not same_attempt:
                return {
                    "status": "id_conflict",
                    "message": (
                        "Cet identifiant de tentative existe déjà "
                        "avec d'autres données."
                    ),
                    "xp_gained": 0,
                }

            return {
                "status": "duplicate_ignored",
                "message": "Cette tentative a déjà été traitée.",
                "xp_gained": 0,
            }

        # Toute tentative nouvelle est enregistrée, même si elle échoue.
        conn.execute(
            """
            INSERT INTO demo_lab_attempts (
                attempt_id,
                user_id,
                lab_id,
                passed,
                xp_awarded,
                processed_at
            )
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (
                event["attempt_id"],
                event["user_id"],
                event["lab_id"],
                int(event["passed"]),
                now_utc(),
            ),
        )

        if not event["passed"]:
            conn.commit()

            return {
                "status": "failed",
                "message": "Tentative enregistrée sans récompense XP.",
                "xp_gained": 0,
            }

        # La réussite est enregistrée, mais vérifions si le lab
        # a déjà été récompensé pour cet utilisateur.
        existing_reward = conn.execute(
            """
            SELECT xp_awarded
            FROM demo_lab_rewards
            WHERE user_id = ? AND lab_id = ?
            """,
            (event["user_id"], event["lab_id"]),
        ).fetchone()

        if existing_reward is not None:
            conn.commit()

            return {
                "status": "already_rewarded",
                "message": "La récompense de ce lab a déjà été attribuée.",
                "xp_gained": 0,
            }

        xp = event["xp_reward"]

        # Enregistrer la récompense et actualiser les statistiques
        # dans la même transaction.
        conn.execute(
            """
            INSERT INTO demo_lab_rewards (
                user_id,
                lab_id,
                xp_awarded,
                awarded_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                event["user_id"],
                event["lab_id"],
                xp,
                now_utc(),
            ),
        )

        conn.execute(
            """
            INSERT INTO demo_user_stats (user_id, xp_total)
            VALUES (?, 0)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (event["user_id"],),
        )

        conn.execute(
            """
            UPDATE demo_user_stats
            SET xp_total = xp_total + ?
            WHERE user_id = ?
            """,
            (xp, event["user_id"]),
        )

        conn.execute(
            """
            UPDATE demo_lab_attempts
            SET xp_awarded = ?
            WHERE attempt_id = ?
            """,
            (xp, event["attempt_id"]),
        )

        conn.commit()

        return {
            "status": "rewarded",
            "message": "Lab réussi et récompense attribuée.",
            "user_id": event["user_id"],
            "lab_id": event["lab_id"],
            "xp_gained": xp,
        }

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_user_xp(user_id, db_path=DB_PATH):
    """Retourne le total d'XP enregistré pour un utilisateur."""

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT xp_total
            FROM demo_user_stats
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    return row[0] if row else 0


def print_result(title, result):
    print(f"\n--- {title} ---")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    init_db()

    first_event = {
        "event_type": "lab.submitted",
        "event_id": "evt-001",
        "attempt_id": "attempt-001",
        "user_id": "user-42",
        "lab_id": "ospf-3-routers",
        "passed": True,
        "xp_reward": 100,
    }

    # 1. Première réussite.
    result = process_lab_event(first_event)
    print_result("Première réussite", result)

    # 2. Même tentative reçue une nouvelle fois.
    # L'événement ne doit pas attribuer une deuxième récompense.
    duplicate = process_lab_event(first_event)
    print_result("Nouvelle livraison de la même tentative", duplicate)

    # 3. Nouvelle tentative, mais échec du lab.
    failed_event = {
        "event_type": "lab.submitted",
        "event_id": "evt-002",
        "attempt_id": "attempt-002",
        "user_id": "user-42",
        "lab_id": "acl-debutant",
        "passed": False,
        "xp_reward": 50,
    }

    failed_result = process_lab_event(failed_event)
    print_result("Tentative échouée", failed_result)

    # 4. Nouvelle tentative réussie sur le lab déjà récompensé.
    second_success = {
        **first_event,
        "event_id": "evt-003",
        "attempt_id": "attempt-003",
    }

    second_result = process_lab_event(second_success)
    print_result("Nouvelle réussite du même lab", second_result)

    # 5. Vérifier le total de l'utilisateur.
    print("\n--- Progression finale ---")
    print("Utilisateur : user-42")
    print("XP total :", get_user_xp("user-42"))
```

### 16.5. Exécuter le TP

Depuis le dossier du projet, lance :

```bash
python serverless_lab.py
```

Le programme doit produire des résultats similaires à ceux-ci :

```text
--- Première réussite ---
status: rewarded
message: Lab réussi et récompense attribuée.
user_id: user-42
lab_id: ospf-3-routers
xp_gained: 100

--- Nouvelle livraison de la même tentative ---
status: duplicate_ignored
message: Cette tentative a déjà été traitée.
xp_gained: 0

--- Tentative échouée ---
status: failed
message: Tentative enregistrée sans récompense XP.
xp_gained: 0

--- Nouvelle réussite du même lab ---
status: already_rewarded
message: La récompense de ce lab a déjà été attribuée.
xp_gained: 0

--- Progression finale ---
Utilisateur : user-42
XP total : 100
```

Les dates ne sont pas affichées ici, car elles sont conservées dans la base de démonstration et non dans les messages de résultat.

### 16.6. Explorer les données enregistrées

Le TP a créé trois tables.

| Table | Rôle |
|---|---|
| `demo_lab_attempts` | Conserver l'historique des tentatives traitées. |
| `demo_lab_rewards` | Garantir qu'un même utilisateur ne reçoive pas plusieurs fois la récompense d'un même lab. |
| `demo_user_stats` | Conserver le total d'XP de chaque utilisateur. |

Tu peux afficher les données enregistrées avec une petite commande Python :

```bash
python -c "import sqlite3; c=sqlite3.connect('skilltree_serverless_demo.db'); print('Tentatives :', c.execute('SELECT attempt_id, user_id, lab_id, passed, xp_awarded FROM demo_lab_attempts').fetchall()); print('Récompenses :', c.execute('SELECT user_id, lab_id, xp_awarded FROM demo_lab_rewards').fetchall()); print('Statistiques :', c.execute('SELECT user_id, xp_total FROM demo_user_stats').fetchall()); c.close()"
```

Tu devrais constater que les tentatives réussies et échouées sont conservées, mais qu'une seule récompense est enregistrée pour `user-42` et `ospf-3-routers`.

### 16.7. Comprendre les mécanismes importants

**La validation de l'événement**

La fonction contrôle les champs obligatoires et les types de données. Une fonction réellement exposée sur Internet doit effectuer ces vérifications même si le frontend valide déjà les formulaires.

**L'historique des tentatives**

Chaque tentative possède un identifiant stable. Une contrainte d'unicité empêche la même tentative d'être insérée plusieurs fois.

**L'idempotence**

Le même événement peut être reçu plusieurs fois à la suite d'une erreur réseau ou d'une nouvelle livraison par un système de messagerie. La fonction doit empêcher ces répétitions de provoquer des effets métier supplémentaires.

Le TP utilise deux protections :

- Un identifiant unique pour chaque tentative.
- Une clé composée de l'utilisateur et du lab pour la récompense.

**La transaction SQLite**

L'enregistrement de la récompense et l'actualisation du total d'XP sont réalisés dans une transaction. Cela évite de valider l'une de ces modifications sans l'autre en cas d'erreur pendant cette transaction.

**La séparation des responsabilités**

Le code distingue la validation des entrées, le traitement métier, l'accès aux données et la consultation du total d'XP. Cela facilite les tests et la future adaptation vers un environnement cloud.

### 16.8. Comment ce TP correspond-il au véritable Skill-Tree ?

Dans ton application, le Lab Workspace v2 dispose déjà d'un mécanisme de soumission. Le backend s'appuie sur des définitions de labs et conserve les tentatives dans la base SQLite.

Le scénario pédagogique est donc proche du parcours réel :

```text
Lab Workspace
      |
      v
Soumission de la configuration
      |
      v
Vérification des règles du lab
      |
      v
Enregistrement de la tentative
      |
      v
Traitement de la récompense XP
      |
      v
Mise à jour de la progression
```

Dans une architecture serverless, une évolution possible serait de séparer l'enregistrement de la tentative des traitements secondaires.

Par exemple :

```text
FastAPI
   |
   v
Vérification et soumission du lab
   |
   v
Enregistrement durable de la tentative
   |
   v
Publication fiable d'un événement
   |
   v
Traitement serverless
   |
   ├──> Attribution des XP
   ├──> Mise à jour des badges
   └──> Statistiques et notifications
```

Ce schéma présente une architecture envisageable, et non une modification déjà réalisée dans Skill-Tree.

Dans un système réel, il faudrait notamment garantir qu'une tentative validée ne soit pas enregistrée sans que son événement soit finalement publié. Une table *outbox*, une file d'attente durable ou un mécanisme équivalent peut répondre à ce besoin.

Il faudrait également choisir une base adaptée aux contraintes de concurrence et au service cloud retenu, plutôt que supposer que la base SQLite locale convient à toutes les situations.

### 16.9. Exercices d'amélioration

**Exercice A — Ajouter un utilisateur**

Crée un événement avec :

- `user_id` : `user-99`
- `lab_id` : `acl-debutant`
- `passed` : `true`
- `xp_reward` : `50`
- Un nouvel `attempt_id`

Exécute le programme et vérifie que le nouvel utilisateur possède son propre total d'XP.

**Exercice B — Tester une récompense nulle**

Modifie une copie de l'événement pour utiliser une récompense de `0`.

Le traitement doit accepter cette valeur selon les règles du TP, mais ne doit pas augmenter le total d'XP.

**Exercice C — Simuler une erreur de données**

Teste les entrées suivantes :

```python
{"passed": "oui"}
{"passed": True, "xp_reward": -5}
{"passed": True, "xp_reward": 10000}
```

Intègre chacune de ces valeurs dans un événement par ailleurs complet.

La fonction doit rejeter les données incorrectes et ne doit enregistrer ni tentative ni récompense pour les événements rejetés.

**Exercice D — Simuler plusieurs tentatives**

Enregistre deux tentatives distinctes pour le même utilisateur et le même lab :

- La première échoue.
- La seconde réussit.

Vérifie que les deux tentatives sont visibles dans l'historique et que seule la tentative réussie peut obtenir la récompense.

**Exercice E — Ajouter des badges**

Imagine qu'un badge `first_lab` soit attribué après la première réussite d'un lab.

Propose une table de démonstration pour enregistrer les badges déverrouillés. Prévoyez une contrainte d'unicité sur l'utilisateur et le badge, afin qu'un même badge ne soit pas attribué plusieurs fois.

### 16.10. Limites de la simulation

Ce programme est un exercice pédagogique, pas un composant prêt à être déployé en production.

Il ne prend notamment pas en charge :

- La vérification réelle de la configuration réseau d'un lab.
- L'authentification d'un utilisateur.
- La vérification serveur de son droit à soumettre une tentative.
- La connexion à la vraie base de données Skill-Tree.
- Les badges réels, les prérequis et les règles de déblocage des cours.
- La publication d'événements dans une file d'attente cloud.
- Les mécanismes complets de reprise, de surveillance et d'alerte.

Autre distinction importante : le programme suppose que le champ `passed` a déjà été déterminé par un composant fiable. Dans une application réelle, un utilisateur ne doit jamais pouvoir obtenir des XP simplement en envoyant lui-même `"passed": true` au serveur.

Le backend doit vérifier le résultat du lab à partir des règles de validation côté serveur, puis décider des récompenses autorisées.

**Résultat attendu :** tu sais maintenant concevoir un traitement qui réagit à la soumission d'un lab, conserve les tentatives, attribue les XP une seule fois et peut servir de base à une future architecture événementielle serverless pour Skill-Tree.


**Correction :**

Non. Les serveurs existent toujours. Le terme signifie que le fournisseur prend en charge une grande partie de leur gestion, ce qui permet au développeur de se concentrer davantage sur l'application et sur ses événements.

### Exercice 2 — Identifier les composants

Une application reçoit une image, la stocke, puis déclenche un traitement pour créer une miniature.

Identifie les trois composants principaux.

**Correction :**

- Le stockage d'objets conserve l'image.
- L'événement de stockage sert de déclencheur.
- La fonction transforme l'image et produit la miniature, qui sera ensuite enregistrée dans un stockage approprié.

La solution réelle devra aussi prévoir les permissions d'accès, le format des fichiers, la gestion des erreurs et la surveillance.

### Exercice 3 — Choisir entre synchrone et asynchrone

Une API doit calculer immédiatement le prix d'un produit et retourner le résultat à l'utilisateur.

Quel type de traitement semble le plus adapté ?

**Correction :**

Un traitement synchrone est naturel ici, car l'utilisateur attend immédiatement le prix.

À l'inverse, un envoi de courriel ou la création d'un rapport volumineux peut être effectué de manière asynchrone lorsque le besoin métier le permet.

### Exercice 4 — Comprendre les risques des événements

Une fonction attribue 20 points d'expérience chaque fois qu'elle reçoit l'événement `cours_termine`. Le même événement est transmis deux fois.

Quel problème peut se produire et comment le prévenir ?

**Correction :**

L'utilisateur peut recevoir 40 points au lieu de 20.

Il faut prévoir une stratégie d'idempotence ou de déduplication basée sur un identifiant unique de l'activité, puis s'assurer que l'attribution des points et l'enregistrement de la déduplication sont réalisés de manière cohérente.

### Exercice 5 — Réfléchir à la persistance

Une fonction conserve le score d'un quiz uniquement dans une variable en mémoire. Peut-on garantir que ce score sera disponible lors de la prochaine invocation ?

**Correction :**

Non. Une invocation ultérieure peut utiliser un autre environnement d'exécution, et l'environnement courant peut disparaître. Si le score doit être conservé, il faut le stocker dans un système de persistance adapté.

### Exercice 6 — Évaluer les coûts

Une fonction est très rarement appelée, mais elle utilise une base de données et un service de stockage configurés pour rester disponibles.

Peut-on conclure que le coût total sera presque nul simplement parce que la fonction est peu utilisée ?

**Correction :**

Non. Le coût global dépend aussi de la configuration de la base de données, du stockage, des requêtes, des journaux, du trafic réseau et des autres services utilisés. Il faut examiner la tarification de chaque composant.

## 18. Défi final — Concevoir une architecture serverless

### Situation

Skill-Tree souhaite ajouter une fonctionnalité permettant aux utilisateurs de terminer un quiz.

Quand un utilisateur valide son quiz, l'application doit :

1. Enregistrer le résultat.
2. Mettre à jour sa progression.
3. Attribuer les points d'expérience associés à l'activité.
4. Envoyer une notification.
5. Produire des statistiques quotidiennes.

Tu dois proposer une architecture serverless simple et expliquer le rôle de ses composants.

### Questions

**Question 1.** Quel composant doit recevoir la requête du navigateur ?

**Question 2.** Quel composant doit calculer le résultat du quiz ?

**Question 3.** Où faut-il conserver durablement le résultat et la progression ?

**Question 4.** Comment éviter que les points d'expérience soient attribués deux fois ?

**Question 5.** Faut-il obligatoirement attendre l'envoi de la notification avant de retourner le résultat du quiz ?

**Question 6.** Quels éléments faut-il surveiller en production ?

### Correction du défi final

#### 1. Réception de la requête

Une API Gateway ou un endpoint HTTP adapté reçoit la demande de validation du quiz.

Cette entrée doit être protégée par une authentification et des règles d'autorisation adaptées.

#### 2. Calcul du résultat

Une fonction serverless peut valider les entrées, calculer la note et déterminer si le quiz est réussi.

Elle doit vérifier les règles métier côté serveur : il ne faut pas faire confiance uniquement au résultat envoyé par le navigateur.

#### 3. Stockage durable

Le résultat, la progression et les points attribués sont enregistrés dans une base de données ou un service de données adapté.

La structure doit garantir une cohérence suffisante entre la réussite du quiz et la progression enregistrée.

#### 4. Éviter les doubles attributions

Chaque activité validée doit avoir un identifiant stable. L'application vérifie si la récompense associée a déjà été enregistrée.

Le contrôle de déduplication et l'attribution des points doivent être conçus pour rester cohérents même en cas de requêtes simultanées ou de nouvelle tentative.

#### 5. Envoyer la notification de manière asynchrone

Il n'est généralement pas nécessaire d'attendre la fin de l'envoi d'une notification pour afficher le résultat d'un quiz.

Un événement peut être transmis à une file d'attente, puis traité par une fonction distincte. Le système doit cependant prévoir les tentatives de reprise, les échecs et le suivi du statut d'envoi.

#### 6. Surveillance et sécurité

Il faut surveiller le temps de réponse, les erreurs, le nombre de traitements, la file de messages, les échecs répétés, les coûts et les accès refusés.

Les fonctions doivent disposer d'autorisations limitées à leurs besoins. Les secrets doivent être protégés, les données sensibles sécurisées et les entrées validées côté serveur.

#### Architecture proposée

```text
              Navigateur Skill-Tree
                       |
                       v
                 Endpoint HTTP
                       |
                       v
                Fonction Quiz
                       |
                       v
                 Base de données
                       |
                       v
               Événement de réussite
                       |
                       v
                 File de messages
                       |
              ┌────────┴────────┐
              v                 v
       Fonction XP        Fonction de
       idempotente         notification

       Tâche planifiée
              |
              v
       Statistiques quotidiennes
```

Ce schéma est une proposition logique : l'enregistrement du quiz et l'émission de l'événement doivent être conçus de manière fiable. Dans un système réel, un mécanisme tel qu'une table de type *outbox* peut aider à éviter qu'une transaction soit enregistrée sans que l'événement correspondant soit publié.

### Critères d'évaluation

Tu as réussi le défi si tu peux expliquer :

- Pourquoi le navigateur ne doit pas être l'autorité finale pour l'attribution des XP.
- Pourquoi la base de données doit conserver durablement les résultats.
- Pourquoi une file d'attente peut simplifier les traitements secondaires.
- Pourquoi les événements peuvent être traités plusieurs fois.
- Pourquoi la sécurité, l'observabilité et la maîtrise des coûts font partie de l'architecture.

## 19. Checklist de révision

Avant de passer au niveau intermédiaire, vérifie que tu peux cocher les points suivants.

- [ ] Je sais expliquer pourquoi serverless ne signifie pas absence de serveurs.
- [ ] Je comprends la différence entre IaaS, PaaS et FaaS.
- [ ] Je sais reconnaître une fonction, un déclencheur, une API et une file d'attente.
- [ ] Je sais distinguer un traitement synchrone d'un traitement asynchrone.
- [ ] Je comprends pourquoi une fonction ne doit pas dépendre de sa mémoire pour conserver les données importantes.
- [ ] Je sais expliquer le démarrage à froid et les contraintes d'exécution.
- [ ] Je comprends le risque de traiter plusieurs fois un même événement.
- [ ] Je sais appliquer le principe du moindre privilège.
- [ ] Je peux représenter une architecture serverless simple.
- [ ] Je sais identifier les coûts et les éléments à surveiller.

## 20. Pour aller plus loin

Pour approfondir les notions de ce cours, privilégie la documentation officielle des fournisseurs :

- **AWS Lambda :** https://docs.aws.amazon.com/lambda/latest/dg/
- **Architectures serverless sur AWS :** https://aws.amazon.com/lambda/serverless-architectures-learn-more/
- **Vue d'ensemble d'Azure Functions :** https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview
- **Bonnes pratiques d'architecture pour Azure Functions :** https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-functions
- **Présentation de Cloud Run :** https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run
- **Cloud Run functions :** https://docs.cloud.google.com/run/docs/functions/overview
- **Vue d'ensemble de l'architecture serverless sur Google Cloud :** https://cloud.google.com/discover/what-is-serverless-architecture

Les noms des services, leurs options de déploiement et leurs limites évoluent. Consulte la documentation du fournisseur choisi avant de réaliser un déploiement réel.

## Conclusion

Le serverless est une approche qui permet de construire des applications en déléguant au fournisseur cloud une grande partie de la gestion de l'infrastructure.

Son intérêt repose sur la combinaison de fonctions, de déclencheurs, de services managés et de mécanismes événementiels. Cette organisation peut faciliter la mise à l'échelle et diminuer certaines tâches d'exploitation.

Elle ne supprime toutefois ni les responsabilités de sécurité, ni les besoins de persistance, ni les contraintes de performance, ni les risques de coûts inattendus.

Le réflexe fondamental à retenir est le suivant : **concevoir chaque traitement autour de sa responsabilité, choisir le déclencheur approprié, conserver durablement les données importantes et prévoir les erreurs dès la conception.**
