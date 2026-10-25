
# Serverless — Niveau Expert
## Architecture événementielle, résilience, sécurité, orchestration et optimisation à grande échelle

**Fichier :** `cloud-serverless-expert.md`  
**Niveau :** Expert  
**Domaine :** Cloud computing, architectures distribuées, DevOps, SRE, cybersécurité et ingénierie logicielle  
**Approche :** Multi-cloud et indépendante du fournisseur, avec exemples AWS, Azure et Google Cloud

## 1. Présentation du cours

Le serverless est un modèle d'exécution dans lequel le fournisseur cloud prend en charge une grande partie du provisionnement et de la gestion de l'infrastructure sous-jacente. Cela ne signifie pas qu'il n'existe plus de serveurs : leur exploitation est principalement abstraite du point de vue de l'équipe applicative.

À un niveau expert, le principal défi n'est pas de créer une fonction cloud. Il consiste à concevoir un système distribué dont les composants peuvent évoluer indépendamment, échanger des événements de manière fiable, résister aux erreurs, protéger les données, respecter les objectifs de service et maintenir un coût prévisible.

Ce cours approfondit les compromis architecturaux, les modes de défaillance, les mécanismes de contrôle et les méthodes de validation nécessaires à une plateforme serverless de production.

### 1.1 Compétences visées

À la fin du cours, l'apprenant doit pouvoir :

- distinguer les différents modèles d'exécution serverless ;
- concevoir une architecture événementielle faiblement couplée ;
- définir des contrats d'événements versionnés ;
- garantir l'idempotence des traitements ;
- gérer les tentatives, les délais d'expiration et les files de messages morts ;
- construire des workflows distribués avec compensation ;
- choisir entre fonctions, conteneurs serverless et services managés ;
- concevoir les limites de concurrence et la protection des dépendances ;
- appliquer une stratégie d'identité et de gestion des secrets ;
- sécuriser une API et une chaîne de livraison ;
- mesurer la fiabilité avec des SLI, des SLO et des budgets d'erreur ;
- diagnostiquer les problèmes de latence, de saturation et de cohérence ;
- tester les défaillances et préparer la reprise ;
- maîtriser les coûts à l'échelle d'une plateforme ;
- défendre une architecture à partir de ses exigences et de ses risques.

## 2. Prérequis

Il est recommandé de maîtriser :

- les bases du cloud et des services managés ;
- HTTP, REST, DNS, TLS et les principes TCP/IP ;
- JSON, API et authentification ;
- les bases de Linux et de Git ;
- un langage backend, par exemple Python, JavaScript/TypeScript, Java, C# ou Go ;
- les notions de base de données relationnelle et NoSQL ;
- les concepts de CI/CD et d'Infrastructure as Code ;
- les notions d'identité, de permissions et de journalisation.

Commandes de vérification possibles :

```bash
git --version
python --version
node --version
docker --version
terraform version
```

Ces commandes sont indicatives : tous les outils ne sont pas requis pour chaque parcours et certains environnements ne les installent pas par défaut.

## 3. Fondamentaux avancés du serverless

### 3.1 Les principales catégories

Le terme serverless regroupe plusieurs modèles complémentaires.

| Catégorie | Fonction principale | Exemple de service |
|---|---|---|
| Fonctions managées | Exécuter une unité de code déclenchée par un événement | AWS Lambda, Azure Functions, Cloud Run functions |
| Conteneurs serverless | Exécuter un conteneur sans gérer directement un cluster de serveurs | Cloud Run, Azure Container Apps, AWS App Runner selon le besoin |
| API managées | Exposer et contrôler des API | Amazon API Gateway, Azure API Management, API Gateway sur Google Cloud |
| Messagerie | Découpler les producteurs et les consommateurs | Amazon SQS/SNS, Azure Service Bus, Google Cloud Pub/Sub |
| Événements | Distribuer les événements entre services | Amazon EventBridge, Azure Event Grid, Google Cloud Eventarc |
| Orchestration | Coordonner plusieurs étapes | AWS Step Functions, Azure Durable Functions, Google Cloud Workflows |
| Données managées | Stocker les données sans administrer directement le moteur sous-jacent | DynamoDB, Azure Cosmos DB, Firestore |
| Traitement analytique | Exécuter des traitements de données managés | BigQuery et services analytiques adaptés |

Les services cités ne sont pas parfaitement équivalents. Le choix doit prendre en compte les fonctions disponibles, les limites, les garanties de livraison, les régions prises en charge, les quotas et le modèle de facturation.

### 3.2 Modèle de responsabilité partagée

```text
Responsabilité du fournisseur cloud
|
+-- Infrastructure physique
+-- Couche d'abstraction du service
+-- Provisionnement de la capacité managée
+-- Maintenance de la plateforme selon le service
+-- Disponibilité des composants gérés selon le contrat
|
Responsabilité du client
|
+-- Code et dépendances
+-- Identités et permissions
+-- Protection des données
+-- Configuration des services
+-- Validation des entrées
+-- Gestion des erreurs métier
+-- Tests et déploiements
+-- Observabilité
+-- Objectifs de service
+-- Coûts et quotas
+-- Plan de reprise
```

La répartition exacte des responsabilités dépend du service. Un conteneur serverless, une fonction managée et une base de données managée ne présentent pas les mêmes obligations opérationnelles.

### 3.3 Les quatre grandes propriétés du modèle

**Élasticité :** la capacité peut augmenter ou diminuer en fonction de la charge.

**Abstraction de l'infrastructure :** l'équipe gère moins directement les serveurs et le système d'exploitation.

**Facturation liée à l'usage :** une partie importante du coût dépend des requêtes, du temps d'exécution, de la mémoire, des ressources provisionnées ou des opérations.

**Composition de services :** l'application s'appuie sur plusieurs composants spécialisés au lieu d'un serveur unique.

Ces propriétés ne sont pas gratuites. Elles peuvent introduire des démarrages à froid, des limites de durée, des contraintes de concurrence, des dépendances aux services managés et des coûts de communication entre composants.

## 4. Architectures synchrones et asynchrones

### 4.1 Architecture synchrone

Dans une architecture synchrone, le client attend la réponse d'un composant avant de poursuivre.

```text
Client
  |
  | Requête HTTP
  v
API
  |
  | Appel
  v
Fonction serverless
  |
  | Requête
  v
Base de données
  |
  | Résultat
  v
Fonction
  |
  v
API
  |
  v
Client
```

Avantages :
- parcours facile à comprendre ;
- réponse immédiate ;
- adaptée aux lectures et aux opérations rapides.

Risques :
- propagation de la latence ;
- dépendances disponibles simultanément ;
- accumulation de délais d'attente ;
- saturation des pools de connexions ;
- couplage temporel entre les composants.

### 4.2 Architecture asynchrone

Le producteur publie un message et n'attend pas nécessairement le traitement complet.

```text
Client
  |
  v
API
  |
  v
File ou bus d'événements
  |
  +------------------+
  |                  |
  v                  v
Consommateur A   Consommateur B
  |                  |
  v                  v
Base de données   Notification
```

Avantages :
- découplage temporel ;
- capacité à absorber des pointes de charge ;
- reprise plus facile de certains traitements ;
- consommateurs indépendants.

Risques :
- délais de traitement variables ;
- doublons ;
- ordre des événements ;
- messages qui échouent durablement ;
- complexité du suivi de bout en bout ;
- cohérence éventuellement différée.

### 4.3 Choisir le bon modèle

Utilisez le modèle synchrone lorsque le client a réellement besoin d'un résultat immédiat et que le traitement peut être borné.

Utilisez le modèle asynchrone lorsque le travail peut être accepté puis traité ultérieurement, lorsqu'il faut absorber une pointe de charge ou lorsque plusieurs consommateurs doivent réagir indépendamment.

Une architecture peut combiner les deux :

```text
Client
  |
  v
API
  |
  +-- Validation rapide
  |
  +-- Enregistrement de la demande
  |
  +-- Publication d'un événement
             |
             v
        Traitement asynchrone
             |
             v
        Mise à jour du statut
             |
             v
        Notification du résultat
```

L'API peut répondre `202 Accepted` si la demande a été acceptée pour un traitement ultérieur. Cette réponse ne signifie pas que le traitement métier est terminé.

## 5. Architecture événementielle experte

### 5.1 Producteurs, événements et consommateurs

Un événement décrit généralement un fait qui s'est produit. Une commande, en revanche, exprime généralement une intention d'effectuer une action.

Exemples :

- événement : `OrderCreated` ;
- commande : `CreateOrder` ;
- événement : `PaymentAuthorized` ;
- commande : `AuthorizePayment`.

La distinction aide à définir les responsabilités et les contrats.

```text
Commande
   |
   v
Service métier
   |
   v
Événement publié
   |
   +--------+---------+
   |        |         |
   v        v         v
Facturation Stockage Notification
```

Un événement publié ne doit pas être confondu avec la preuve que tous les consommateurs l'ont traité.

### 5.2 Contrat d'événement

Un contrat d'événement doit définir :
- un identifiant unique ;
- un type ;
- une version de schéma ;
- une date d'émission ;
- le producteur ;
- le contexte métier ;
- la structure des données ;
- les règles de compatibilité ;
- la sensibilité des données ;
- les exigences de rétention.

Exemple de contrat JSON :

```json
{
  "id": "evt-2026-000001",
  "type": "com.example.orders.created",
  "version": "1.0",
  "source": "order-service",
  "time": "2026-10-25T10:00:00Z",
  "data": {
    "orderId": "ord-12345",
    "customerId": "cus-987",
    "amount": 149.90,
    "currency": "EUR"
  }
}
```

Les identifiants de cet exemple sont fictifs. En production, les règles de validation doivent être explicites, notamment pour la devise, le montant, les données personnelles et la compatibilité du schéma.

### 5.3 Versionnement des contrats

Une évolution additive peut être compatible si les consommateurs tolèrent les champs supplémentaires et si les nouveaux champs sont optionnels ou disposent de valeurs par défaut appropriées.

Une modification du sens d'un champ ou la suppression d'un champ utilisé peut casser des consommateurs existants.

Principes :
1. versionner les contrats ;
2. documenter les changements ;
3. tester la compatibilité ;
4. déployer les consommateurs capables de lire le nouveau format ;
5. publier les nouveaux événements ;
6. retirer les anciens formats après une période contrôlée.

Ne supposez jamais que tous les consommateurs se mettent à jour en même temps.

### 5.4 Event sourcing et événements d'intégration

Il faut distinguer deux usages.

**Événements d'intégration :** messages publiés pour informer d'autres composants d'un fait métier.

**Event sourcing :** approche dans laquelle les événements constituent la source de vérité pour reconstruire l'état d'un agrégat ou d'une entité métier.

Publier des événements ne signifie pas que l'application utilise l'event sourcing. Cette dernière approche exige une conception plus poussée du modèle d'état, des projections, des versions, de la reconstruction et de la conservation.

## 6. Livraison des événements : garanties et limites

### 6.1 At-most-once, at-least-once et exactly-once

**At-most-once :** un événement peut être perdu, mais il n'est pas volontairement livré plusieurs fois dans le modèle considéré.

**At-least-once :** le système retente la livraison et peut transmettre plusieurs fois le même événement.

**Exactly-once :** une garantie d'exécution unique dans un périmètre et sous des conditions définis par le service.

La terminologie dépend du service et de la frontière considérée. Une garantie de traitement exactement une fois dans un système de messagerie ne garantit pas nécessairement une seule exécution de l'effet métier externe, par exemple un paiement auprès d'un prestataire tiers.

### 6.2 Le problème des doublons

Scénario :

```text
1. Consommateur reçoit l'événement
2. Il effectue l'opération métier
3. Il échoue avant d'accuser réception
4. Le message est relivré
5. Le consommateur recommence l'opération
```

Si l'opération est un débit financier, le client risque d'être débité deux fois.

La solution générale consiste à concevoir un traitement idempotent.

### 6.3 Idempotence

Une opération est idempotente lorsque sa répétition avec la même clé logique ne produit pas plusieurs effets métier.

Exemple :

```text
Événement : evt-123
        |
        v
Vérifier le registre des événements traités
        |
        +-- Déjà traité
        |       |
        |       v
        |    Ne pas répéter l'effet métier
        |
        +-- Pas encore traité
                |
                v
          Exécuter l'opération
                |
                v
          Enregistrer le résultat
```

La vérification et l'enregistrement doivent être conçus pour résister aux exécutions concurrentes. Une simple vérification suivie d'une insertion sans contrainte d'unicité peut laisser passer deux exécutions simultanées.

### 6.4 Exemple d'idempotence avec une base SQL

Schéma conceptuel :

```sql
CREATE TABLE processed_events (
    event_id VARCHAR(200) PRIMARY KEY,
    processed_at TIMESTAMP NOT NULL
);
```

L'identifiant doit être stable entre les tentatives. Une nouvelle clé aléatoire générée à chaque invocation ne permettrait pas de reconnaître un doublon.

Pseudocode transactionnel :

```text
BEGIN TRANSACTION

Tenter d'enregistrer event_id
avec une contrainte d'unicité

Si event_id existe déjà :
    ne pas répéter l'effet métier
Sinon :
    effectuer la modification métier
    enregistrer le résultat

COMMIT
```

Si le registre d'idempotence et la modification métier sont stockés dans la même base relationnelle, ils peuvent généralement être protégés par une transaction commune.

Si l'effet métier est externe à cette base, la transaction SQL ne suffit pas. Il faut utiliser une clé d'idempotence reconnue par le fournisseur externe, un mécanisme de compensation ou une stratégie de réconciliation.

### 6.5 Durée de conservation des clés

Le registre d'idempotence doit conserver les clés assez longtemps pour couvrir la période pendant laquelle des doublons peuvent être livrés ou rejoués.

Une suppression trop rapide des clés peut permettre à un ancien événement d'être exécuté à nouveau. Une conservation illimitée peut entraîner une croissance importante de la base.

La durée doit être choisie à partir des garanties du système source, de la politique de rejeu et des exigences métier.

## 7. Fiabilité des files et des consommateurs

### 7.1 File de messages et backpressure

Une file peut absorber temporairement une charge supérieure à la capacité des consommateurs.

```text
Producteurs rapides
        |
        v
     File de messages
        |
        v
Consommateurs à capacité limitée
        |
        v
Services en aval
```

Si les producteurs continuent à publier plus vite que les consommateurs ne traitent les messages, la file grandit. Le système doit détecter cette accumulation avant qu'elle n'entraîne des retards inacceptables.

### 7.2 Backpressure

La backpressure consiste à contrôler la charge en amont lorsque le système en aval atteint sa capacité.

Mécanismes possibles :
- limiter la concurrence ;
- ralentir les producteurs ;
- ajuster le débit de consommation ;
- utiliser une file durable ;
- appliquer des quotas ;
- rejeter explicitement certaines requêtes ;
- prioriser les traitements critiques.

La mise à l'échelle automatique seule ne résout pas le problème si la base de données, le service externe ou le quota reste le goulot d'étranglement.

### 7.3 Tentatives et backoff exponentiel

Une stratégie de nouvelle tentative peut augmenter progressivement le délai entre les tentatives.

Exemple conceptuel :

```text
Tentative 1 -> délai court
Tentative 2 -> délai plus long
Tentative 3 -> délai encore plus long
Tentative 4 -> délai plafonné
```

Une stratégie réaliste peut appliquer une formule de type :

\[
d_n = \min(d_{\max}, d_0 \times 2^n) + J
\]

où :
- \(d_0\) est le délai initial ;
- \(d_{\max}\) est le délai maximal ;
- \(J\) est une variation aléatoire appelée jitter.

Le jitter réduit le risque que de nombreux consommateurs retentent simultanément après une panne commune.

Cette formule est un modèle conceptuel : le comportement exact doit correspondre à la politique réellement configurée sur le service de messagerie.

### 7.4 Erreurs transitoires et permanentes

| Type d'erreur | Exemple | Stratégie |
|---|---|---|
| Transitoire | Timeout réseau temporaire | Nouvelle tentative contrôlée |
| Surcharge | Quota ou limitation de débit | Backoff et réduction de charge |
| Donnée invalide | Champ obligatoire absent | Rejet contrôlé et quarantaine |
| Permission incorrecte | Rôle IAM manquant | Correction de configuration, pas de retry infini |
| Incompatibilité de schéma | Champ inattendu | Diagnostic et correction du contrat |
| Dépendance indisponible durablement | Service externe en panne | Circuit breaker, file et reprise contrôlée |

Les tentatives automatiques ne doivent pas servir à masquer une erreur permanente.

### 7.5 Dead-letter queue

Une dead-letter queue (DLQ) reçoit les messages qui ont dépassé la politique de traitement ou de nouvelle tentative définie.

```text
File principale
      |
      v
Consommateur
      |
      +-- Succès
      |     |
      |     v
      |   Accusé de traitement
      |
      +-- Échec temporaire
      |     |
      |     v
      |   Nouvelle tentative
      |
      +-- Échecs persistants
            |
            v
      File de messages morts
            |
            v
      Investigation et correction
            |
            v
      Rejeu contrôlé si autorisé
```

Une DLQ n'est pas une solution complète à elle seule. Il faut définir un propriétaire, des alertes, une durée de conservation, un format de diagnostic et une procédure de rejeu.

### 7.6 Rejeu des messages

Avant de rejouer un message :
1. identifier la cause de l'échec ;
2. vérifier que la cause a été corrigée ;
3. vérifier l'idempotence ;
4. évaluer l'effet d'un traitement tardif ;
5. décider si le message doit être rejeté, corrigé ou rejoué ;
6. limiter le débit de rejeu ;
7. observer les effets sur les dépendances ;
8. consigner le résultat.

Le rejeu massif d'une DLQ peut provoquer une nouvelle panne si la cause initiale était une saturation.

## 8. Pattern Transactional Outbox

### 8.1 Le problème de la double écriture

Supposons qu'un service enregistre une commande dans une base SQL, puis publie un événement dans une file.

```text
Enregistrer la commande
        |
        v
Publier OrderCreated
```

Si l'enregistrement SQL réussit mais que la publication échoue, la commande existe sans événement correspondant.

Si l'événement est publié avant l'échec de la transaction SQL, les consommateurs peuvent agir sur une commande qui n'existe finalement pas.

### 8.2 Solution par outbox

Le pattern Transactional Outbox enregistre la donnée métier et l'événement à publier dans la même transaction de base de données.

```text
Transaction SQL
|
+-- INSERT commande
|
+-- INSERT événement dans outbox
|
+-- COMMIT
       |
       v
Relais outbox
       |
       v
Bus ou file de messages
       |
       v
Consommateurs
```

La transaction garantit que la commande et l'enregistrement outbox sont validés ensemble dans la même base.

Le relais peut être :
- un processus qui interroge périodiquement la table ;
- un mécanisme de capture des changements de données ;
- un composant spécialisé compatible avec la base.

Le relais peut publier le même événement plusieurs fois si la publication réussit mais que la confirmation de traitement n'est pas enregistrée. Les consommateurs doivent donc rester idempotents.

### 8.3 Exemple de table outbox

```sql
CREATE TABLE outbox (
    event_id VARCHAR(200) PRIMARY KEY,
    aggregate_id VARCHAR(200) NOT NULL,
    event_type VARCHAR(200) NOT NULL,
    payload TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    published_at TIMESTAMP NULL
);
```

Ce schéma est volontairement générique. Le type exact des colonnes, la gestion des statuts, les index et la stratégie de verrouillage doivent être adaptés au moteur SQL.

## 9. Workflows distribués et pattern Saga

### 9.1 Pourquoi orchestrer ?

Un processus métier peut nécessiter plusieurs services.

Exemple de commande e-commerce :

```text
Commande
   |
   v
Réserver le stock
   |
   v
Autoriser le paiement
   |
   v
Créer l'expédition
   |
   v
Confirmer la commande
```

Si une étape échoue, il faut décider quelles opérations peuvent être annulées ou compensées.

### 9.2 Saga

Une Saga décompose une transaction métier distribuée en plusieurs étapes locales, chacune ayant éventuellement une action de compensation.

```text
Étape 1 : réserver le stock
       |
       v
Étape 2 : autoriser le paiement
       |
       v
Étape 3 : créer l'expédition
       |
       +-- Succès -> terminer
       |
       +-- Échec
              |
              v
       Compenser les étapes applicables
```

Exemples de compensations :
- libérer le stock réservé ;
- annuler une autorisation de paiement ;
- demander l'annulation d'une expédition si elle n'est pas déjà partie.

Une compensation n'est pas toujours l'inverse parfait de l'opération. Un remboursement, par exemple, est une nouvelle opération métier qui peut elle-même échouer.

### 9.3 Orchestration et chorégraphie

**Orchestration :** un composant coordonne les étapes et les transitions.

**Chorégraphie :** les services réagissent aux événements et coordonnent le processus sans orchestrateur central unique.

| Critère | Orchestration | Chorégraphie |
|---|---|---|
| Visibilité du processus | Généralement centralisée | Répartie entre services |
| Couplage | Couplage à l'orchestrateur | Couplage aux contrats d'événements |
| Diagnostic | État du workflow plus explicite | Corrélation interservices nécessaire |
| Évolution | Workflow central à maintenir | Contrats et comportements distribués à maintenir |
| Usage typique | Processus long avec étapes définies | Écosystème d'événements indépendants |

Les deux modèles peuvent coexister. Le choix dépend du besoin de suivi, du nombre d'étapes, des règles métier et des capacités de la plateforme.

### 9.4 Machine à états

Un workflow doit définir explicitement :
- les états ;
- les transitions autorisées ;
- les conditions ;
- les délais ;
- les tentatives ;
- les compensations ;
- les sorties finales ;
- les mécanismes de reprise.

Exemple :

```text
RECEIVED
   |
   v
STOCK_RESERVED
   |
   v
PAYMENT_AUTHORIZED
   |
   v
SHIPPING_CREATED
   |
   v
COMPLETED

Depuis chaque état :
- succès -> état suivant
- erreur transitoire -> retry borné
- erreur permanente -> échec contrôlé
- échec après effet partiel -> compensation
```

L'état du workflow doit être persistant si le processus peut dépasser la durée d'une seule invocation serverless.

## 10. Limites de durée et traitements longs

Une fonction serverless est généralement soumise à une limite de durée d'exécution définie par le service et sa configuration.

Un traitement long ne doit pas être découpé artificiellement en une seule fonction qui risque de dépasser cette limite.

Approches possibles :
- fractionner le traitement en tâches idempotentes ;
- enregistrer un état de progression ;
- orchestrer plusieurs étapes ;
- placer les tâches dans une file durable ;
- stocker les résultats intermédiaires ;
- reprendre à partir du dernier point validé.

```text
Demande longue
      |
      v
Orchestrateur
      |
      +-- Étape 1 -> état enregistré
      |
      +-- Étape 2 -> état enregistré
      |
      +-- Étape 3 -> état enregistré
      |
      v
Résultat final
```

Un workflow durable ne garantit pas que chaque étape ne sera exécutée qu'une fois. Les opérations externes doivent rester protégées contre les répétitions.

## 11. Choisir entre fonctions, conteneurs serverless et plateformes Kubernetes

### 11.1 Fonctions managées

Adaptées à :
- des événements ciblés ;
- des tâches de traitement courtes ;
- des intégrations simples ;
- des déclenchements par événements ;
- des tâches périodiques compatibles avec les limites du service.

Points d'attention :
- modèle d'exécution et de démarrage ;
- limites de durée ;
- concurrence ;
- dépendances ;
- format des événements ;
- comportement de retry.

### 11.2 Conteneurs serverless

Adaptés à :
- des API web ;
- des services HTTP ;
- des applications existantes conteneurisées ;
- des services nécessitant un runtime ou des bibliothèques particulières ;
- des applications dont la logique n'est pas naturellement une fonction événementielle.

Points d'attention :
- port d'écoute ;
- ressources CPU et mémoire ;
- concurrence par instance ;
- démarrage ;
- réseau ;
- identité d'exécution ;
- limites de mise à l'échelle.

### 11.3 Kubernetes

Kubernetes peut être pertinent lorsque l'application nécessite :
- un contrôle important de l'orchestration ;
- des primitives Kubernetes spécifiques ;
- un écosystème d'opérateurs ou de contrôleurs ;
- des politiques réseau et d'exécution particulières ;
- une portabilité ou une standardisation qui justifie sa complexité.

Il ne faut pas choisir Kubernetes uniquement parce que l'application utilise des conteneurs. Un service serverless peut réduire la charge opérationnelle lorsque ses limites correspondent aux besoins.

### 11.4 Matrice de décision

| Question | Fonction | Conteneur serverless | Kubernetes |
|---|---|---|---|
| Unité de code ciblée | Très adaptée | Possible | Possible |
| API HTTP persistante | Selon le service | Très adaptée | Très adaptée |
| Besoin de contrôle du cluster | Faible | Limité | Élevé |
| Charge opérationnelle | Généralement faible | Généralement faible à modérée | Plus importante |
| Runtime personnalisé | Selon le service | Souvent adapté | Adapté |
| Orchestration complexe | Avec un orchestrateur | Avec un orchestrateur | Selon l'architecture |
| Contrôle fin des workloads | Limité | Partiel | Plus important |

La matrice est indicative : les services évoluent et les capacités exactes doivent être vérifiées dans la documentation du fournisseur retenu.

## 12. Performance, concurrence et démarrages à froid

### 12.1 Démarrage à froid

Un démarrage à froid peut se produire lorsqu'une plateforme doit préparer un environnement d'exécution avant de traiter une requête.

Causes possibles :
- création ou allocation d'une instance ;
- chargement du runtime ;
- chargement des dépendances ;
- initialisation de clients ;
- accès à des configurations ou secrets ;
- établissement de connexions.

```text
Requête
   |
   v
Instance disponible ?
   |
   +-- Oui -> traitement
   |
   +-- Non
         |
         v
   Initialisation
         |
         v
   Chargement de l'application
         |
         v
   Traitement
```

### 12.2 Réduire la latence de démarrage

- limiter les dépendances inutiles ;
- réduire le travail effectué au chargement ;
- éviter de télécharger de gros artefacts au démarrage ;
- réutiliser les clients et connexions lorsque le runtime le permet ;
- mesurer la durée d'initialisation ;
- choisir un runtime approprié ;
- ajuster la mémoire et les ressources ;
- envisager des instances minimales lorsque le service le permet et que le coût est justifié.

Une optimisation doit être mesurée sur des démarrages réels. La réutilisation d'un environnement d'exécution ne doit jamais être supposée permanente.

### 12.3 Concurrence

La concurrence indique combien de requêtes ou de tâches peuvent être traitées simultanément par une instance ou un consommateur selon le modèle d'exécution.

Une concurrence trop faible peut entraîner une croissance de la file et augmenter la latence.

Une concurrence trop élevée peut provoquer :
- épuisement des connexions à la base ;
- saturation CPU ;
- consommation mémoire excessive ;
- limitation de débit par les dépendances ;
- hausse du taux d'erreur.

### 12.4 Capacité des dépendances

Supposons que chaque instance ouvre jusqu'à \(C\) connexions à la base et que \(N\) instances puissent fonctionner simultanément.

Une borne simplifiée du nombre de connexions est :

\[
K_{\max} \approx N \times C
\]

Si 40 instances peuvent ouvrir chacune 15 connexions, la charge potentielle atteint environ 600 connexions. Ce calcul ne remplace pas une mesure réelle, mais met en évidence le risque de multiplication des connexions.

La capacité du système doit être évaluée de bout en bout, et non uniquement à partir de la capacité d'exécution serverless.

## 13. Protection des dépendances : timeouts, circuit breakers et bulkheads

### 13.1 Timeouts

Chaque appel externe doit avoir un délai d'attente adapté.

Sans timeout explicite, une fonction peut immobiliser des ressources en attendant une dépendance qui ne répond pas.

La durée totale d'une requête doit être cohérente avec :
- le délai client ;
- le délai de la passerelle ;
- le délai de la fonction ;
- les délais des dépendances ;
- le temps nécessaire pour produire une réponse.

Une chaîne d'appels ne doit pas laisser chaque composant attendre plus longtemps que le budget global disponible.

### 13.2 Circuit breaker

Le circuit breaker protège une dépendance qui échoue de manière répétée.

```text
État CLOSED
  |
  | Échecs au-dessus du seuil
  v
État OPEN
  |
  | Refus temporaire des appels
  |
  | Après une période de repos
  v
État HALF-OPEN
  |
  +-- Test réussi -> CLOSED
  |
  +-- Test échoué -> OPEN
```

Le circuit breaker évite de continuer à envoyer un volume important d'appels à un service en difficulté.

Les seuils, la durée d'ouverture et les tests doivent être adaptés au comportement de la dépendance. Un circuit breaker mal configuré peut lui-même provoquer des interruptions inutiles.

### 13.3 Bulkhead

Le pattern bulkhead isole des ressources ou des charges pour qu'un problème dans un composant n'épuise pas toutes les capacités du système.

Exemples :
- files séparées pour des priorités différentes ;
- limites de concurrence distinctes ;
- pools de connexions isolés ;
- quotas par type de traitement ;
- services critiques séparés des traitements non prioritaires.

### 13.4 Budget de latence

Une requête de bout en bout dispose d'un budget de latence.

```text
Budget global
|
+-- Authentification
+-- API Gateway
+-- Fonction A
+-- Base de données
+-- Service externe
+-- Sérialisation et réponse
```

Les budgets doivent être mesurés. Si chaque dépendance consomme presque tout le délai disponible, la requête complète dépassera le seuil attendu.

## 14. Sécurité serverless

### 14.1 Identité et permissions

Chaque composant doit avoir une identité distincte lorsque cela est nécessaire pour limiter les privilèges.

```text
Fonction de commande
  -> accès à la table des commandes

Fonction de notification
  -> accès au service de notification

Pipeline de déploiement
  -> permissions de déploiement limitées

Administrateur
  -> accès privilégié contrôlé
```

Évitez de donner à toutes les fonctions un rôle administrateur général. Une compromission doit avoir un rayon d'impact aussi limité que possible.

### 14.2 Authentification des appels internes

Le fait qu'un endpoint ne soit pas affiché publiquement ne signifie pas qu'il est sécurisé.

Pour chaque appel interne :
- authentifier le principal ;
- autoriser l'opération ;
- vérifier la destination ;
- utiliser TLS lorsque nécessaire ;
- limiter les permissions ;
- journaliser les opérations sensibles ;
- éviter les secrets statiques lorsque des identités managées sont disponibles.

### 14.3 Gestion des secrets

Les secrets ne doivent pas être codés en dur dans le code source, les images, les fichiers de configuration partagés ou les journaux.

Utilisez un gestionnaire de secrets compatible avec le fournisseur, tel que AWS Secrets Manager, Azure Key Vault ou Google Cloud Secret Manager.

```text
Fonction
   |
   | Identité d'exécution
   v
Gestionnaire de secrets
   |
   | Permission ciblée
   v
Secret nécessaire
```

Il faut également :
- définir les règles de rotation ;
- restreindre les permissions de lecture ;
- éviter les lectures inutiles à chaque requête ;
- gérer les versions ;
- surveiller les accès ;
- prévoir la révocation ;
- éviter d'écrire le secret dans les logs.

La mise en cache d'un secret peut améliorer les performances, mais doit être conçue en tenant compte de la rotation et de la révocation.

### 14.4 Validation des entrées

Une fonction exposée doit considérer toute entrée externe comme non fiable.

Contrôles :
- schéma JSON ;
- taille maximale ;
- types et formats ;
- valeurs autorisées ;
- authentification ;
- autorisation métier ;
- limites de débit ;
- protection contre les injections ;
- validation des URL et des destinations réseau lorsque l'application effectue des appels sortants.

Ne faites pas confiance à un identifiant fourni par le client pour déterminer automatiquement les droits sur une ressource.

### 14.5 SSRF et appels sortants

Une fonction qui accepte une URL et effectue une requête peut être vulnérable aux attaques de type SSRF (Server-Side Request Forgery).

Mesures :
- limiter les destinations autorisées ;
- refuser les plages réseau sensibles ;
- éviter de suivre aveuglément les redirections ;
- contrôler la résolution DNS lorsque c'est pertinent ;
- limiter les protocoles ;
- appliquer des restrictions réseau ;
- fixer un timeout et une taille de réponse maximale.

La validation syntaxique d'une URL ne suffit pas à empêcher toutes les formes de SSRF.

### 14.6 Sécurité des événements

Un événement peut provenir d'un producteur compromis ou contenir des données malveillantes.

Les consommateurs doivent :
- valider le contrat ;
- vérifier l'origine lorsque le modèle de sécurité le permet ;
- limiter les tailles ;
- contrôler les permissions du producteur ;
- éviter de faire confiance aux champs de contexte ;
- appliquer l'idempotence ;
- journaliser les rejets sans exposer les données sensibles.

## 15. Réseau et accès aux données privées

Les fonctions et conteneurs serverless peuvent nécessiter un accès à des ressources privées : base de données, API interne, services réseau ou système hérité.

La conception doit distinguer :
- l'accès entrant ;
- l'accès sortant ;
- la résolution DNS ;
- l'authentification applicative ;
- les règles réseau ;
- les chemins privés ;
- les contraintes du service managé.

```text
Fonction serverless
       |
       v
Connectivité réseau configurée
       |
       +-- DNS
       |
       +-- Règles réseau
       |
       +-- Routage
       |
       v
Base de données privée
```

Une connectivité réseau ne donne pas automatiquement l'autorisation d'accéder aux données. Les règles réseau, les identités et les permissions de la base doivent être vérifiées séparément.

## 16. Observabilité et diagnostic

### 16.1 Logs structurés

Un log structuré facilite le filtrage, l'agrégation et la corrélation.

Exemple :

```json
{
  "timestamp": "2026-10-25T10:00:00Z",
  "level": "INFO",
  "service": "order-worker",
  "event_id": "evt-123",
  "correlation_id": "corr-456",
  "operation": "process_order",
  "duration_ms": 84,
  "result": "success"
}
```

N'enregistrez pas les mots de passe, jetons d'accès, secrets ou données personnelles non nécessaires.

### 16.2 Identifiants de corrélation

Un système distribué doit relier les événements et les appels d'un même parcours.

```text
Requête initiale
  correlation_id = corr-456
       |
       v
API
       |
       v
File de messages
       |
       v
Fonction de traitement
       |
       v
Base de données
```

L'identifiant de corrélation ne remplace pas un identifiant d'événement. Le premier relie plusieurs opérations ; le second identifie un événement précis.

### 16.3 Les quatre signaux

Les quatre signaux classiques sont :
- latence ;
- trafic ;
- erreurs ;
- saturation.

Pour les systèmes événementiels, il faut aussi suivre :
- la profondeur de la file ;
- l'âge du message le plus ancien ;
- le débit de consommation ;
- le taux de tentatives ;
- le nombre de messages en DLQ ;
- le délai entre publication et traitement ;
- les échecs de workflow ;
- le taux de doublons détectés.

### 16.4 Traces distribuées

Les traces permettent de visualiser les appels et le temps passé dans les différents composants.

```text
Trace : traitement d'une commande

API                  12 ms
  |
  +-- Validation      3 ms
  |
  +-- Publication     5 ms
  |
  +-- Réponse         4 ms

Worker              140 ms
  |
  +-- Lecture DB     25 ms
  |
  +-- Paiement       95 ms
  |
  +-- Mise à jour    20 ms
```

Les valeurs sont illustratives. La durée de l'API et celle du worker ne doivent pas être additionnées automatiquement comme si le client attendait le worker dans un parcours asynchrone.

### 16.5 Alertes opérationnelles

Exemples d'alertes utiles :
- l'âge du message le plus ancien dépasse le seuil ;
- le taux d'erreur augmente fortement ;
- le nombre de messages en DLQ progresse ;
- la latence dépasse le SLO ;
- le nombre d'instances ou la concurrence atteint une limite ;
- les quotas sont proches de la saturation ;
- une dépendance échoue régulièrement ;
- les coûts augmentent anormalement.

Chaque alerte doit préciser une action attendue, un propriétaire et un runbook.

## 17. SRE et objectifs de service

### 17.1 SLI et SLO

Un SLI est une mesure de service. Un SLO est un objectif défini pour cette mesure.

Pour un traitement asynchrone, les SLI possibles comprennent :
- la proportion d'événements traités avec succès ;
- la proportion d'événements traités avant une échéance ;
- la latence entre publication et traitement ;
- la proportion de workflows terminés ;
- le nombre de doublons produisant un effet métier ;
- la durée d'indisponibilité d'un service.

Un SLO pertinent doit correspondre à l'expérience ou au besoin métier. Un worker qui fonctionne sans exception peut malgré tout être en retard de plusieurs heures sur sa file.

### 17.2 Budget d'erreur

Si un SLO exige un taux de succès de 99,9 %, la fraction d'échec autorisée est de 0,1 % sur la période considérée.

Pour un service mesuré par requêtes :

\[
B = N \times (1 - SLO)
\]

où :
- \(B\) est le budget d'erreur en nombre de requêtes ;
- \(N\) est le nombre de requêtes éligibles ;
- \(SLO\) est exprimé sous forme décimale.

Pour 100 000 requêtes et un SLO de 99,9 %, le budget théorique est de 100 requêtes en erreur, si la définition du SLI correspond bien à cette mesure.

### 17.3 Fiabilité des traitements asynchrones

Un système de traitement asynchrone doit définir des objectifs de délai. Exemple :
- 99 % des messages traités en moins de 60 secondes ;
- 99,9 % des workflows terminés avec succès sur la période ;
- aucune perte non détectée d'un événement métier critique.

Ces objectifs doivent être compatibles avec le débit, la capacité et les garanties réelles des services choisis.

## 18. Tests avancés

### 18.1 Tests unitaires

Tester :
- les validations ;
- les règles métier ;
- les transformations ;
- les erreurs attendues ;
- les comportements d'idempotence ;
- les calculs ;
- les transitions d'état.

Les tests unitaires doivent rester rapides et indépendants des services cloud réels autant que possible.

### 18.2 Tests de contrat

Les tests de contrat vérifient la compatibilité entre producteurs et consommateurs.

Ils doivent couvrir :
- les champs obligatoires ;
- les types ;
- les valeurs autorisées ;
- les champs inconnus ;
- les versions ;
- les erreurs de validation ;
- les données minimales et maximales.

### 18.3 Tests d'intégration

Ils vérifient le comportement avec les services réels ou des environnements de test représentatifs :
- files ;
- bases de données ;
- API ;
- gestionnaire de secrets ;
- authentification ;
- orchestration.

Les émulateurs peuvent accélérer certains tests, mais ils ne reproduisent pas toujours les quotas, les délais, les permissions et les comportements exacts du service managé.

### 18.4 Tests de charge

Tester plusieurs profils :
- charge normale ;
- pointe courte ;
- montée progressive ;
- charge prolongée ;
- pic de messages après une panne ;
- retour de la dépendance après une interruption.

Mesurer la latence, les erreurs, la profondeur de file, le coût et la capacité de récupération.

### 18.5 Tests de chaos

Un exercice de chaos peut simuler :
- une dépendance lente ;
- une réponse en erreur ;
- une interruption réseau ;
- une limitation de débit ;
- un consommateur indisponible ;
- un déploiement défectueux ;
- un rejeu de messages ;
- une augmentation brutale du trafic.

Il faut définir un périmètre, des garde-fous, un plan d'arrêt et des critères de réussite. Ne lancez pas un test destructif dans un environnement de production sans autorisation et préparation adaptées.

## 19. CI/CD et Infrastructure as Code

### 19.1 Pipeline de livraison

```text
Commit
  |
  v
Lint et tests unitaires
  |
  v
Tests de contrat
  |
  v
Analyse de sécurité
  |
  v
Construction de l'artefact
  |
  v
Publication de l'artefact
  |
  v
Déploiement en test
  |
  v
Tests d'intégration
  |
  v
Validation et approbation
  |
  v
Déploiement progressif
  |
  v
Surveillance et retour arrière
```

### 19.2 Séparer les identités

Le pipeline doit utiliser une identité différente de celle du service en exécution lorsque cela permet de limiter les privilèges.

- L'identité de construction crée et publie des artefacts.
- L'identité de déploiement applique des changements dans l'environnement cible.
- L'identité d'exécution accède aux données nécessaires au traitement.
- L'identité d'observabilité consulte les informations utiles à l'exploitation.

Les rôles doivent être définis selon les capacités réellement nécessaires.

### 19.3 Déploiement progressif

Une stratégie progressive peut envoyer une petite fraction du trafic vers la nouvelle version, puis augmenter progressivement la part après validation.

```text
Version stable A : 100 %
        |
        v
Version A : 90 %   Version B : 10 %
        |
        v
Vérification des métriques
        |
        +-- Dégradation -> retour à A
        |
        +-- Résultats satisfaisants
                    |
                    v
Version A : 50 %   Version B : 50 %
                    |
                    v
             Validation finale
```

Les pourcentages sont illustratifs. Les mécanismes de répartition du trafic diffèrent selon les plateformes et les types de déclencheurs.

Un retour arrière applicatif ne suffit pas si la nouvelle version a déjà effectué des changements de données irréversibles.

### 19.4 Infrastructure as Code

L'Infrastructure as Code doit décrire :
- les fonctions et services ;
- les déclencheurs ;
- les files et topics ;
- les permissions ;
- les paramètres de mise à l'échelle ;
- les alertes ;
- les secrets référencés ;
- les politiques de rétention ;
- les destinations de DLQ ;
- les paramètres de réseau.

Les secrets eux-mêmes ne doivent pas être inscrits en clair dans le dépôt.

Les plans doivent être examinés avant application. La destruction de ressources doit être contrôlée et ne doit pas supprimer par erreur les données persistantes.

## 20. Coûts et FinOps serverless

### 20.1 Le piège du « paiement à l'usage »

Le serverless peut réduire le coût d'une charge variable, mais il ne garantit pas un coût inférieur dans tous les scénarios.

Les coûts peuvent provenir :
- du nombre d'invocations ;
- de la durée d'exécution ;
- de la mémoire et des ressources allouées ;
- des instances minimales ;
- du stockage ;
- des opérations de stockage ;
- des messages ;
- des transferts réseau ;
- des logs et traces ;
- des bases de données ;
- des workflows ;
- des services tiers ;
- des nouvelles tentatives.

### 20.2 Modèle de coût conceptuel

Pour une fonction dont le coût dépend des invocations et de la durée, un modèle simplifié est :

\[
C \approx N \times (C_{\text{appel}} + T \times R)
\]

où :
- \(N\) représente le nombre d'invocations ;
- \(C_{\text{appel}}\) représente le coût unitaire d'invocation ;
- \(T\) représente la durée facturée ;
- \(R\) représente le coût de calcul par unité de temps.

Ce modèle omet les paliers gratuits, les allocations de ressources, les coûts réseau, les logs, les bases de données et les spécificités tarifaires. Il sert à comprendre les facteurs, pas à produire un devis.

### 20.3 Coût des retries

Une dépendance instable peut augmenter fortement le nombre d'exécutions.

```text
1 000 événements
      |
      v
Traitement initial
      |
      +-- Succès : 900
      |
      +-- Échec : 100
                |
                v
          Nouvelle tentative
                |
                +-- Succès : 60
                |
                +-- Nouvel échec : 40
```

Les tentatives supplémentaires peuvent augmenter le coût et la charge des dépendances. Il faut donc suivre le taux de retry et le nombre d'exécutions par événement.

### 20.4 Réduire le coût

- limiter les invocations inutiles ;
- filtrer les événements non pertinents ;
- traiter les messages par lots lorsque le service et le traitement le permettent ;
- ajuster la mémoire et la concurrence ;
- éviter les appels externes redondants ;
- mettre en cache les données non sensibles lorsque cela est approprié ;
- limiter la verbosité des logs sans perdre les informations nécessaires ;
- éviter les boucles de retry ;
- maîtriser les ressources minimales toujours actives ;
- analyser les transferts de données ;
- attribuer les coûts aux services et équipes.

L'optimisation doit préserver les SLO et la sécurité. Réduire la mémoire ou la concurrence peut augmenter la durée d'exécution et finalement accroître le coût total.

## 21. Portabilité multi-cloud et risque de dépendance

### 21.1 Portabilité réelle

Le code peut être portable tout en dépendant fortement des services natifs :
- modèle de déclenchement ;
- format d'événement ;
- système d'identité ;
- API de stockage ;
- orchestration ;
- politique de retry ;
- observabilité ;
- gestion des secrets.

Une fonction qui utilise directement plusieurs API spécifiques à un fournisseur n'est pas automatiquement portable parce qu'elle est écrite en Python.

### 21.2 Stratégie de portabilité raisonnable

Séparer :
- le cœur métier ;
- les adaptateurs vers les services cloud ;
- les contrats d'événements ;
- les interfaces de stockage ;
- la configuration ;
- les mécanismes de déploiement.

```text
Cœur métier
    |
    +-- Adaptateur AWS
    |
    +-- Adaptateur Azure
    |
    +-- Adaptateur Google Cloud
```

Cette séparation peut améliorer la testabilité et réduire certains coûts de migration. Elle ajoute toutefois des abstractions et des tests supplémentaires.

### 21.3 Quand éviter l'abstraction multi-cloud

Une abstraction générique peut être contre-productive si elle masque des différences importantes de cohérence, de sécurité, de livraison ou de facturation.

Le multi-cloud doit répondre à un besoin concret : exigences réglementaires, résilience indépendante, présence géographique ou stratégie d'entreprise. Il ne faut pas ajouter une deuxième plateforme uniquement pour obtenir une portabilité théorique.

## 22. Exemple d'application : traitement de commandes

### 22.1 Besoin métier

Une application reçoit des commandes, vérifie leur validité, réserve le stock, autorise le paiement et notifie le client.

Le système doit :
- absorber des pointes de trafic ;
- éviter les doubles commandes ;
- gérer les erreurs de paiement ;
- reprendre les traitements interrompus ;
- suivre le statut de chaque commande ;
- limiter les accès aux données ;
- fournir des indicateurs opérationnels.

### 22.2 Architecture

```text
Client
  |
  v
API Gateway ou point d'entrée
  |
  v
Service de commande
  |
  +-- Validation
  |
  +-- Enregistrement commande + outbox
             |
             v
       Relais outbox
             |
             v
       Bus d'événements
             |
             v
       Orchestrateur de workflow
             |
             +-- Réserver le stock
             |
             +-- Autoriser le paiement
             |
             +-- Créer l'expédition
             |
             +-- Confirmer la commande
             |
             +-- Envoyer une notification

Transversal :
- Registre d'idempotence
- Journaux structurés
- Traces distribuées
- Alertes
- DLQ
- Gestion des secrets
- Contrôle des coûts
```

### 22.3 Flux nominal

1. Le client envoie une demande.
2. L'API authentifie et valide la requête.
3. Le service enregistre la commande et l'événement outbox dans une transaction.
4. Le relais publie l'événement.
5. L'orchestrateur démarre le workflow.
6. Le stock est réservé.
7. Le paiement est autorisé.
8. L'expédition est créée.
9. La commande passe à l'état confirmé.
10. Le client est notifié.

### 22.4 Flux d'échec

Si le paiement échoue après la réservation du stock :

```text
Commande créée
      |
      v
Stock réservé
      |
      v
Paiement refusé
      |
      v
Workflow en échec métier
      |
      v
Libération du stock
      |
      v
Commande marquée comme refusée
      |
      v
Notification du client
```

La libération du stock est une compensation. Elle doit elle-même être idempotente et observable.

### 22.5 Invariants métier

Les invariants sont les règles qui doivent rester vraies même en cas de retry ou de panne.

Exemples :
- une commande possède un identifiant métier stable ;
- une commande ne doit pas déclencher plusieurs débits non autorisés ;
- le stock réservé ne peut pas dépasser les règles d'inventaire ;
- une commande ne passe pas à `COMPLETED` avant la réussite des étapes obligatoires ;
- chaque workflow peut être diagnostiqué à partir de son identifiant de corrélation.

Les invariants doivent être implémentés dans les contrôles métier et les mécanismes de stockage, pas uniquement dans le diagramme d'architecture.

## 23. Travaux pratiques

### TP 1 — Concevoir un consommateur idempotent

**Objectif :** traiter un événement plusieurs fois sans répéter l'effet métier.

Travail :
1. définir un schéma d'événement ;
2. choisir une clé d'idempotence ;
3. créer un registre des événements traités ;
4. définir une transaction ;
5. simuler deux livraisons du même événement ;
6. simuler deux traitements concurrents ;
7. vérifier que l'effet métier n'est appliqué qu'une fois ;
8. tester la conservation des clés.

**Livrable :** schéma de données, code ou pseudocode, tests et analyse des limites.

### TP 2 — Construire une file avec DLQ

**Objectif :** traiter les événements et isoler les échecs persistants.

Étapes :
1. créer une file principale ;
2. créer une file de messages morts ;
3. configurer une politique de retry ;
4. déployer un consommateur ;
5. provoquer un échec transitoire ;
6. provoquer une erreur permanente ;
7. vérifier le comportement des tentatives ;
8. observer le transfert vers la DLQ ;
9. corriger la cause ;
10. rejouer un message de façon contrôlée.

**Critères de réussite :**
- les messages réussis ne sont pas inutilement retraités ;
- les erreurs permanentes ne provoquent pas une boucle infinie ;
- les messages en DLQ sont visibles et diagnostiquables ;
- le rejeu respecte l'idempotence.

Les commandes exactes dépendent du fournisseur et du service de messagerie choisis.

### TP 3 — Concevoir un workflow Saga

**Objectif :** modéliser une commande qui réserve du stock, autorise un paiement et crée une expédition.

Étapes :
1. dessiner les états ;
2. définir les transitions ;
3. identifier les erreurs temporaires et permanentes ;
4. définir les retries ;
5. définir les compensations ;
6. définir les délais ;
7. persister l'état du workflow ;
8. tester chaque point de défaillance ;
9. vérifier les effets métier après compensation.

**Livrable :** diagramme d'états, tableau des erreurs, procédures de reprise et tests.

### TP 4 — Mesurer la performance

**Objectif :** identifier les limites de concurrence et de capacité.

Étapes :
1. établir une charge de référence ;
2. mesurer la latence ;
3. augmenter progressivement le débit ;
4. suivre les erreurs et les timeouts ;
5. surveiller les connexions à la base ;
6. observer la profondeur de file ;
7. identifier le goulot d'étranglement ;
8. ajuster un paramètre à la fois ;
9. comparer les résultats ;
10. calculer le coût approximatif par traitement.

**Livrable :** rapport avant/après, mesures et recommandations.

### TP 5 — Concevoir l'observabilité

**Objectif :** relier les logs et métriques d'un workflow.

Étapes :
1. définir un identifiant de corrélation ;
2. définir les événements de journalisation ;
3. inclure les identifiants métier nécessaires ;
4. éviter les données sensibles ;
5. définir les métriques de succès et d'échec ;
6. créer des alertes sur l'âge des messages ;
7. suivre les DLQ ;
8. rédiger un runbook ;
9. simuler un incident ;
10. vérifier que le diagnostic peut être réalisé sans accéder aux données sensibles.

## 24. Exercices corrigés

### Exercice 1 — Doublons

**Question :** pourquoi une fonction déclenchée par un événement doit-elle souvent être idempotente ?

**Correction :** certains systèmes peuvent livrer plusieurs fois le même événement, notamment après un échec ou l'absence d'accusé de réception. L'idempotence empêche de répéter les effets métier indésirables. Le mécanisme doit couvrir les accès concurrents et les opérations externes.

### Exercice 2 — Transaction Outbox

**Question :** quel problème résout le pattern Outbox ?

**Correction :** il évite l'incohérence entre l'enregistrement métier dans une base et l'intention de publier un événement en enregistrant les deux dans une transaction commune. Le relais peut encore publier plusieurs fois, d'où la nécessité de consommateurs idempotents.

### Exercice 3 — DLQ

**Question :** pourquoi ne faut-il pas rejouer immédiatement tous les messages d'une DLQ ?

**Correction :** la cause peut toujours être présente. Un rejeu massif peut saturer les dépendances, reproduire les erreurs ou répéter des effets métier. Il faut corriger la cause, vérifier l'idempotence et limiter le débit.

### Exercice 4 — Concurrence

**Question :** une fonction peut-elle être mise à l'échelle sans limite parce que la plateforme est serverless ?

**Correction :** non. Les services imposent des quotas et des limites. Les bases de données, API externes et services en aval ont également une capacité limitée. La mise à l'échelle doit être contrôlée de bout en bout.

### Exercice 5 — Saga

**Question :** pourquoi une compensation n'est-elle pas toujours l'inverse exact de l'action initiale ?

**Correction :** certaines opérations externes sont irréversibles ou ont déjà produit des effets. Un remboursement, une annulation d'expédition ou une libération de stock est une nouvelle opération métier qui peut échouer et doit être suivie.

### Exercice 6 — SLO asynchrone

**Question :** pourquoi mesurer uniquement le taux d'erreur d'un consommateur est-il insuffisant ?

**Correction :** le consommateur peut réussir toutes ses exécutions tout en étant trop lent pour absorber le débit entrant. Il faut aussi surveiller l'âge des messages, la profondeur de file et le délai entre publication et traitement.

### Exercice 7 — Coût

**Question :** pourquoi un service serverless peut-il devenir coûteux malgré un faible coût unitaire par invocation ?

**Correction :** le nombre d'invocations, les retries, les logs, les transferts réseau, les appels aux bases et les traitements redondants peuvent multiplier le coût total. L'analyse doit porter sur le parcours complet.

### Exercice 8 — Portabilité

**Question :** une fonction écrite en Python est-elle automatiquement portable entre AWS, Azure et Google Cloud ?

**Correction :** non. Le langage peut être portable, mais les déclencheurs, identités, événements, API, limites et mécanismes de déploiement diffèrent. La portabilité nécessite des interfaces explicites et des tests adaptés.

## 25. Projet final corrigé — Plateforme de traitement de commandes serverless

### 25.1 Objectif

Concevoir une plateforme serverless capable d'accepter des commandes, de les traiter de façon asynchrone et de gérer les erreurs sans créer de doublons métier.

Le système doit disposer :
- d'une API sécurisée ;
- d'un mécanisme de messagerie ;
- d'un consommateur idempotent ;
- d'un stockage d'état ;
- d'un workflow ;
- d'une stratégie de retry ;
- d'une DLQ ;
- d'une observabilité de bout en bout ;
- d'une procédure de reprise ;
- d'une stratégie de coût.

### 25.2 Architecture cible

```text
                          Client
                            |
                            v
                  API Gateway / API
                            |
                            v
                    Service de commande
                            |
                            v
                  Base transactionnelle
                    |               |
                    |               +-- Outbox
                    |
                    v
               État commande
                            |
                            v
                      Relais Outbox
                            |
                            v
                    Bus / file durable
                            |
                            v
                      Orchestrateur
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
         Service stock  Service paiement  Service livraison
             |              |              |
             +--------------+--------------+
                            |
                            v
                    État final commande
                            |
                            v
                     Notification client

Éléments transverses :
- IAM
- Secrets
- Idempotence
- Logs et traces
- Métriques et alertes
- DLQ
- CI/CD
- Infrastructure as Code
- Budgets
```

### 25.3 Étape 1 — Définir les contrats

Définir les événements :
- `OrderCreated` ;
- `StockReserved` ;
- `PaymentAuthorized` ;
- `ShipmentCreated` ;
- `OrderCompleted` ;
- `OrderRejected`.

Pour chaque événement, définir :
- un identifiant ;
- une version ;
- une source ;
- une date ;
- un identifiant de commande ;
- les données nécessaires ;
- les règles de validation ;
- la politique de conservation.

Ne transmettez pas les données de paiement sensibles dans des événements généraux si elles ne sont pas nécessaires au traitement.

### 25.4 Étape 2 — Garantir l'idempotence

Chaque opération critique doit utiliser une clé stable.

Exemples :
- réservation de stock : clé fondée sur la commande et l'opération ;
- autorisation de paiement : clé d'idempotence reconnue par le fournisseur de paiement ;
- création d'expédition : identifiant de commande ou de demande stable.

Les contraintes d'unicité et les transactions doivent protéger les effets locaux. Pour les opérations externes, utiliser les mécanismes fournis par le service externe lorsqu'ils existent, puis prévoir une procédure de réconciliation.

### 25.5 Étape 3 — Implémenter l'Outbox

Dans une transaction de création de commande :
1. valider les données ;
2. insérer la commande ;
3. insérer l'événement dans l'outbox ;
4. valider la transaction.

Le relais publie ensuite les événements non publiés. Il doit gérer les interruptions, les tentatives et les publications potentiellement répétées.

### 25.6 Étape 4 — Définir la Saga

États possibles :

```text
RECEIVED
   |
   v
VALIDATED
   |
   v
STOCK_RESERVED
   |
   v
PAYMENT_AUTHORIZED
   |
   v
SHIPMENT_CREATED
   |
   v
COMPLETED
```

États d'échec possibles :

```text
VALIDATION_FAILED
STOCK_REJECTED
PAYMENT_REJECTED
SHIPPING_FAILED
COMPENSATION_REQUIRED
COMPENSATION_FAILED
MANUAL_REVIEW
```

Les états d'échec doivent être explicites. Une commande ne doit pas rester indéfiniment dans un état intermédiaire sans alerte ni procédure de reprise.

### 25.7 Étape 5 — Définir les politiques de retry

Pour chaque étape, préciser :
- les erreurs qui peuvent être retentées ;
- les erreurs permanentes ;
- le nombre ou la durée maximale de tentatives ;
- le backoff ;
- les timeouts ;
- la DLQ éventuelle ;
- les conditions de compensation ;
- les procédures de reprise manuelle.

Les paramètres exacts doivent être adaptés au fournisseur et au service de messagerie choisis.

### 25.8 Étape 6 — Définir la sécurité

Mettre en place :
- une authentification du client ;
- une autorisation métier ;
- des identités séparées pour les composants ;
- des permissions minimales ;
- un gestionnaire de secrets ;
- des accès réseau limités ;
- une validation des événements ;
- une journalisation sans secrets ;
- des limites de débit ;
- une procédure de révocation.

### 25.9 Étape 7 — Définir l'observabilité

Créer des indicateurs :
- commandes reçues ;
- commandes terminées ;
- commandes rejetées ;
- taux d'échec du paiement ;
- délai de traitement ;
- âge du message le plus ancien ;
- nombre de retries ;
- nombre de messages en DLQ ;
- workflows bloqués ;
- coût par commande.

Chaque alerte doit avoir un propriétaire et un runbook. Les seuils doivent être établis à partir des objectifs métier et des mesures de référence.

### 25.10 Étape 8 — Tester les défaillances

Simuler :
- la répétition du même événement ;
- un timeout du fournisseur de paiement ;
- une panne temporaire de la base ;
- une erreur permanente de schéma ;
- un consommateur indisponible ;
- une DLQ qui se remplit ;
- un workflow interrompu après la réservation du stock ;
- une compensation qui échoue ;
- un pic de commandes ;
- une indisponibilité prolongée d'une dépendance.

Pour chaque scénario, vérifier l'état métier final, les journaux, les alertes et les possibilités de reprise.

### 25.11 Étape 9 — Valider les coûts

Estimer :
- les invocations ;
- les durées d'exécution ;
- les messages ;
- le stockage ;
- les opérations de base de données ;
- les transferts réseau ;
- les logs et traces ;
- les workflows ;
- les tentatives ;
- les ressources toujours actives.

Comparer le coût par commande réussie et non uniquement le coût par invocation.

### 25.12 Critères d'acceptation

Le projet est validé si :
- une commande peut être acceptée puis suivie ;
- les doublons ne provoquent pas plusieurs effets métier ;
- les erreurs transitoires sont retentées de manière bornée ;
- les erreurs permanentes sont isolées ;
- les compensations sont idempotentes ;
- les workflows peuvent être diagnostiqués ;
- les permissions sont limitées ;
- les secrets ne sont pas exposés ;
- les métriques mesurent les objectifs métier ;
- le rejeu est contrôlé ;
- le coût peut être estimé et surveillé.

## 26. Checklist de maîtrise experte

- [ ] Je sais choisir entre fonctions, conteneurs serverless et Kubernetes.
- [ ] Je sais concevoir une architecture synchrone et asynchrone.
- [ ] Je sais définir un contrat d'événement versionné.
- [ ] Je comprends les garanties de livraison et leurs limites.
- [ ] Je sais concevoir un traitement idempotent.
- [ ] Je comprends le pattern Transactional Outbox.
- [ ] Je sais concevoir des retries avec backoff et jitter.
- [ ] Je sais utiliser une DLQ et organiser le rejeu.
- [ ] Je sais concevoir une Saga et ses compensations.
- [ ] Je sais contrôler la concurrence et la capacité des dépendances.
- [ ] Je comprends les timeouts, circuit breakers et bulkheads.
- [ ] Je sais sécuriser les identités, les secrets et les événements.
- [ ] Je sais corréler les logs, les métriques et les traces.
- [ ] Je sais définir des SLI, SLO et budgets d'erreur.
- [ ] Je sais concevoir des tests de charge et de défaillance.
- [ ] Je sais sécuriser une chaîne CI/CD.
- [ ] Je sais estimer le coût d'un parcours complet.
- [ ] Je sais expliquer les compromis de portabilité multi-cloud.
- [ ] Je sais concevoir une procédure de reprise vérifiable.

## 27. Glossaire

- **Backpressure :** mécanisme de régulation de charge lorsque le système en aval est saturé.
- **Bulkhead :** isolation des ressources pour limiter la propagation des défaillances.
- **Circuit breaker :** mécanisme qui interrompt temporairement les appels vers une dépendance défaillante.
- **DLQ :** file de messages morts contenant les messages qui n'ont pas été traités selon la politique définie.
- **Event-driven architecture :** architecture dans laquelle les composants communiquent notamment par événements.
- **Event sourcing :** modèle dans lequel les événements constituent la source de vérité de l'état.
- **Idempotence :** propriété qui empêche la répétition d'une opération de produire des effets métier supplémentaires.
- **Jitter :** variation aléatoire ajoutée aux délais de retry.
- **Outbox :** table ou registre transactionnel contenant les événements à publier.
- **Retry :** nouvelle tentative de traitement après un échec.
- **Saga :** coordination d'une transaction métier distribuée par étapes locales et compensations.
- **Serverless :** modèle d'exécution qui abstrait une grande partie de la gestion de l'infrastructure.
- **SLO :** objectif de niveau de service.
- **SLI :** indicateur mesuré de niveau de service.
- **Toil :** travail opérationnel répétitif et automatisable.
- **Workflow durable :** orchestration dont l'état et la progression sont conservés pour permettre la reprise.

## 28. Documentation officielle

### Architecture générale

- Google Cloud — Serverless : https://cloud.google.com/discover/what-is-serverless-architecture
- AWS Serverless : https://aws.amazon.com/serverless/
- Azure Functions : https://learn.microsoft.com/azure/azure-functions/
- Azure Reliability : https://learn.microsoft.com/azure/reliability/

### AWS

- AWS Lambda — bonnes pratiques : https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
- AWS Lambda — gestion des erreurs : https://docs.aws.amazon.com/lambda/latest/dg/invocation-retries.html
- Amazon SQS : https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html
- AWS Step Functions : https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html
- AWS Serverless Application Model : https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html

### Microsoft Azure

- Azure Functions : https://learn.microsoft.com/azure/azure-functions/
- Azure Durable Functions : https://learn.microsoft.com/azure/azure-functions/durable/
- Azure Service Bus : https://learn.microsoft.com/azure/service-bus-messaging/
- Azure Event Grid : https://learn.microsoft.com/azure/event-grid/

### Google Cloud

- Cloud Run : https://cloud.google.com/run/docs
- Cloud Run functions : https://cloud.google.com/run/docs/functions
- Eventarc : https://cloud.google.com/eventarc/docs
- Pub/Sub : https://cloud.google.com/pubsub/docs
- Workflows : https://cloud.google.com/workflows/docs
- Cloud Logging : https://cloud.google.com/logging/docs
- Cloud Monitoring : https://cloud.google.com/monitoring/docs

### Pratiques d'architecture

- Google Cloud Architecture Framework : https://cloud.google.com/architecture/framework
- Google SRE : https://sre.google/
- Serverless Framework : https://www.serverless.com/framework/docs/

Les limites, options de retry, durées d'exécution, quotas et garanties varient selon les services et leurs versions. Avant un déploiement de production, vérifier les paramètres dans la documentation du fournisseur choisi.

## 29. Conclusion

La maîtrise experte du serverless repose sur cinq axes complémentaires :

1. **Architecture :** décomposer le système en composants cohérents, indépendants et adaptés aux besoins métier.
2. **Fiabilité :** anticiper les doublons, les retries, les files en retard, les pannes et les compensations.
3. **Sécurité :** contrôler les identités, les permissions, les secrets, les événements et les dépendances.
4. **Exploitation :** rendre les traitements observables, mesurables et récupérables.
5. **Économie :** maîtriser le coût du parcours complet plutôt que celui d'une seule fonction.

Le serverless ne supprime pas la complexité des systèmes distribués. Il déplace une partie de cette complexité vers la conception des contrats, la coordination des événements, la gestion des erreurs, les limites de capacité et les garanties métier.

Un système serverless expert n'est donc pas simplement un ensemble de fonctions qui s'exécutent automatiquement. C'est une architecture dont les comportements en cas de succès, d'échec, de surcharge, de duplication et de reprise sont explicitement conçus et testés.
