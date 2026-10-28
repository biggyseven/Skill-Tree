# Pipelines de données complexes — Expert

> **Mise en contexte.** Un pipeline de données fiable ne se résume pas à déplacer des lignes d’une base vers un entrepôt. Il doit préserver le sens des événements, résister aux interruptions, éviter les effets en double, absorber les retards, isoler les messages impossibles à traiter, permettre des reprises contrôlées et prouver ce qui a été ingéré, transformé et publié. Dans une architecture distribuée, les pannes partielles sont normales : un service peut valider une écriture alors que son client perd la réponse, un consommateur peut redémarrer avant de confirmer un offset, et un événement ancien peut arriver après une mise à jour plus récente.

Cette leçon s’adresse aux personnes qui conçoivent des flux d’ingestion avancés : chargements par lots, extraction incrémentale, Change Data Capture (CDC), événements, files de messages, traitement en streaming, orchestration et publication de données analytiques. Elle relie la fiabilité distribuée à la qualité, aux contrats, au lignage, à l’observabilité et à la gouvernance. Les exemples sont pédagogiques et doivent être adaptés au moteur, au broker, à l’orchestrateur et aux exigences de production.

L’objectif n’est pas de promettre un système qui ne tombe jamais. L’objectif est de spécifier ce qui se passe lorsqu’un composant tombe, lorsqu’un message est livré plusieurs fois, lorsque l’ordre est différent, lorsque le schéma change ou lorsque la destination refuse une écriture. Un système sérieux définit ses garanties, teste ses frontières et rend les situations ambiguës visibles.

## Objectifs pédagogiques

À la fin de cette leçon, vous serez capable de choisir entre batch, micro-batch et streaming selon la latence métier, de concevoir une ingestion incrémentale qui évite les trous de données, de définir des clés d’idempotence et des stratégies de déduplication, de gérer les offsets et checkpoints, de choisir des politiques de reprise avec backoff, d’utiliser une dead-letter queue, de traiter les événements tardifs, de gérer l’évolution des schémas, de protéger les écritures et effets secondaires, de définir un rejeu contrôlé, d’orchestrer les dépendances, de mesurer la qualité et la fraîcheur et de préparer un plan de reprise après incident.

Vous saurez différencier les garanties « au plus une fois », « au moins une fois » et « exactement une fois », expliquer pourquoi une livraison exactement une fois ne garantit pas automatiquement un effet métier exactement une fois, et concevoir des tests qui valident le comportement sous panne. La compétence avancée repose sur des frontières de cohérence clairement définies, des identifiants stables et des preuves vérifiables.

## 1. Concevoir une ingestion à partir du besoin

Avant de choisir un outil, définissez l’usage du produit de données. Un flux utilisé pour déclencher une décision antifraude en quelques secondes n’a pas les mêmes exigences qu’un rapport comptable recalculé chaque nuit. Une ingestion continue peut réduire la latence mais ajouter de la complexité d’exploitation, de la surveillance et des contraintes de rejeu. Un traitement par lot peut être plus simple, économique et reproductible si la fraîcheur demandée le permet.

Pour chaque flux, documentez la source, le volume moyen et maximal, la taille des messages, la fréquence, le débit de pointe, la latence cible, le retard accepté, les besoins d’ordre, les exigences de conservation, les consommateurs, la criticité, les données sensibles et le comportement attendu en cas d’échec. Définissez également les responsabilités du producteur, du broker, du consommateur et du propriétaire métier.

Il faut distinguer le débit moyen du pic. Un système peut absorber mille événements par seconde en moyenne mais recevoir cinquante mille événements par seconde lors d’une reprise. Il faut aussi distinguer l’heure de l’événement métier, l’heure de publication et l’heure d’ingestion. Les confondre rend les mesures de fraîcheur trompeuses.

### 1.1 Batch, micro-batch et streaming

Le batch rassemble des données sur une période et les traite en une exécution. Il convient aux clôtures périodiques, à l’historisation et aux grands recalculs. Le micro-batch traite de petits lots fréquents. Le streaming traite les événements au fil de leur arrivée et gère un état et une progression continue.

§§§mermaid
flowchart TD
    A[Besoin métier] --> B{Latence requise ?}
    B -->|Heures ou journée| C[Batch planifié]
    B -->|Minutes| D[Micro-batch ou incrémental]
    B -->|Secondes ou sous-seconde| E[Streaming événementiel]
    C --> F[Mesures de fraîcheur et rejeu]
    D --> F
    E --> G[Offsets, état, fenêtres et événements tardifs]
    G --> F
§§§

Aucune architecture n’est automatiquement meilleure. Le streaming implique la gestion des offsets, du débit, de la pression en amont, de l’ordre, des événements tardifs et des mises à jour d’état. Le batch requiert lui aussi des mécanismes de reprise, de déduplication et de validation. Le choix doit être justifié par une exigence mesurable, pas par l’effet de mode.

### 1.2 SLO de fraîcheur et disponibilité

Une cible de latence doit définir son point de départ et son point d’arrivée. « Temps réel » ne signifie rien sans mesure. Un objectif peut préciser que 99 % des événements doivent être visibles dans la table publiée en moins de deux minutes après l’événement source, ou que le lot quotidien doit être prêt avant 07 h dans le fuseau métier. Définissez le percentile, la période de mesure, les exclusions et le traitement des périodes sans activité.

L’objectif doit prendre en compte l’ensemble de la chaîne : source, transport, ingestion, transformation, stockage et consommation. Si la source est déjà en retard, une ingestion très rapide ne rend pas le produit frais. Mesurer plusieurs temps intermédiaires aide à localiser le retard. Le contrat doit définir les comportements en cas de dépassement : alerte, publication dégradée, blocage ou notification du consommateur.

## 2. Modéliser l’événement et son identité

Un événement robuste possède une sémantique claire. Il décrit quelque chose qui s’est produit, avec un identifiant stable, une version de schéma, un temps métier, une provenance et les attributs nécessaires au traitement. Une ligne d’état courant et un événement ne sont pas interchangeables : l’un décrit un état, l’autre un changement ou une occurrence.

### 2.1 Identifiant d’événement

L’identifiant doit rester stable lorsqu’un message est retransmis. Un nouvel identifiant généré à chaque tentative empêche la déduplication. Un identifiant peut provenir de la source, être déterminé par une clé métier ou être produit par le service qui enregistre l’événement. Une clé calculée à partir de plusieurs champs demande une réflexion sur l’unicité, les normalisations et les valeurs manquantes.

Un timestamp ne doit pas être utilisé seul comme identifiant unique sauf si le contrat garantit réellement cette propriété. Plusieurs événements légitimes peuvent se produire au même instant, l’horloge peut reculer et des producteurs différents peuvent avoir des précisions d’horodatage distinctes.

### 2.2 Enveloppe d’événement

Un format d’événement peut distinguer les métadonnées de transport des données métier. Exemple illustratif :

§§§json
{
  "event_id": "evt-demo-001",
  "event_type": "commande.confirmee",
  "schema_version": 2,
  "occurred_at": "2026-10-28T06:10:00Z",
  "produced_at": "2026-10-28T06:10:01Z",
  "producer": "service-commandes",
  "correlation_id": "workflow-demo-42",
  "payload": {
    "commande_id": "cmd-demo-009",
    "statut": "CONFIRMEE",
    "montant_net": 12500
  }
}
§§§

Ces valeurs sont fictives. L’horodatage de l’événement décrit l’action métier, celui de publication situe l’envoi, et l’heure d’ingestion est généralement attribuée par la plateforme. L’identifiant de corrélation relie des étapes d’un processus sans devenir nécessairement une clé de déduplication. La signification de chaque champ doit être stable et documentée.

### 2.3 Événements immuables et corrections

Dans un journal événementiel, on évite généralement de modifier silencieusement le message déjà publié. Une correction peut être représentée par un événement compensatoire ou une nouvelle version, selon le contrat métier. Les consommateurs peuvent ainsi expliquer pourquoi un solde ou un indicateur a changé après la publication initiale.

L’immutabilité ne veut pas dire conserver chaque donnée indéfiniment. Les politiques de rétention, confidentialité, suppression et archivage continuent de s’appliquer. Une conception événementielle doit prévoir comment traiter les données personnelles et les demandes d’effacement, y compris les copies dérivées et les historiques.

## 3. Sémantique de livraison

Les systèmes distribués ne peuvent pas se contenter d’un mot vague comme fiable. Il faut préciser les garanties réellement fournies par le broker, le consommateur, l’état local et la destination.

### 3.1 Au plus une fois

La livraison au plus une fois évite les duplications liées aux reprises en ne retentant pas certaines opérations. Mais un message peut être perdu lorsqu’une panne survient au mauvais moment. Cette stratégie peut convenir à une métrique non critique où une perte ponctuelle est acceptable et documentée. Elle convient mal à des écritures financières ou des actions qui ne peuvent être perdues.

### 3.2 Au moins une fois

La livraison au moins une fois retente l’opération jusqu’à obtenir une confirmation ou atteindre une condition d’échec contrôlée. Elle réduit le risque de perte mais autorise les doublons. Elle doit donc être associée à un identifiant d’événement stable et à un consommateur idempotent, ou à une stratégie de déduplication durable.

### 3.3 Exactement une fois : frontière et pièges

Le terme exactement une fois peut s’appliquer à un périmètre précis d’un moteur : par exemple, un message est traité une fois dans un état transactionnel et un offset associé est commité de manière cohérente. Il ne garantit pas que tous les effets externes sont uniques. Si le consommateur envoie un email ou appelle une API après avoir écrit l’état mais avant d’enregistrer sa progression, la reprise peut provoquer un nouvel appel.

§§§mermaid
sequenceDiagram
    participant B as Broker
    participant C as Consommateur
    participant D as Destination
    B->>C: Événement E
    C->>D: Écriture de E
    D-->>C: Écriture confirmée
    Note over C: Crash avant confirmation de l'offset
    B->>C: Livraison répétée de E
    C->>D: Nouvelle tentative
    Note over D: Idempotence nécessaire pour éviter l'effet en double
§§§

Le bon raisonnement consiste à identifier les opérations atomiques et les frontières qui ne le sont pas. Là où une transaction distribuée complète n’est pas réaliste, l’idempotence, l’outbox transactionnelle, les clés d’opération, la déduplication et la réconciliation rendent le processus fiable.

## 4. Idempotence et déduplication

Une opération est idempotente si la répéter avec la même entrée conduit au même état final que l’exécuter une fois. C’est une propriété centrale des API de paiement, des ingestions, des migrations et des tâches de reprise.

La clé d’idempotence identifie l’opération logique, et non chacune de ses tentatives. Elle peut être l’identifiant d’événement, une clé de commande ou un identifiant stable produit par le système source. Il faut définir sa portée : destination, type d’opération, tenant, période ou clé métier globale. Une clé trop large peut faire disparaître des opérations légitimes ; une clé trop étroite laisse passer les doublons.

Une table d’idempotence peut conserver l’identifiant, une empreinte du contenu, la première réception et l’état du traitement. L’enregistrement de l’identifiant et la mutation métier doivent être atomiques lorsqu’ils partagent la même base. Si le système marque un message traité avant l’écriture métier, une panne peut conduire à une perte. S’il écrit d’abord puis tombe avant de marquer le message, il peut le traiter de nouveau.

Un même identifiant associé à un contenu différent n’est pas un doublon ordinaire. Il faut détecter le conflit, le conserver dans une trace et appliquer une politique explicite : rejet, quarantaine, correction de la source ou arbitrage métier. La durée de vie de la déduplication doit couvrir la fenêtre maximale de retard et de replay, sans croître indéfiniment sans politique de rétention.

### 4.1 Exemple conceptuel de table de contrôle

§§§sql
CREATE TABLE ingestion_events (
    event_id VARCHAR(200) PRIMARY KEY,
    payload_hash VARCHAR(128) NOT NULL,
    first_seen_at TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL
);
§§§

Cette table seule ne crée pas une garantie d’idempotence. Le code de traitement doit gérer les conflits, exécuter la mutation métier dans la même transaction si possible et définir comment l’offset ou l’acquittement suit la validation durable.

## 5. Outbox transactionnelle et effets externes

Un problème fréquent apparaît lorsqu’une application écrit dans sa base puis publie un événement. Si l’écriture en base réussit mais que la publication échoue, le flux aval ne connaît pas le changement. À l’inverse, si le message part puis que la transaction métier échoue, l’événement décrit une opération qui n’a jamais été validée.

Avec une outbox transactionnelle, l’application écrit la mutation métier et un enregistrement d’outbox dans une même transaction locale. Un relais publie ensuite l’événement vers le broker. Il peut publier un événement plus d’une fois, donc les consommateurs doivent rester idempotents.

§§§mermaid
flowchart TD
    A[Commande reçue] --> B[Transaction locale]
    B --> C[Écriture de l'état métier]
    B --> D[Écriture d'un événement outbox]
    C --> E[Commit atomique]
    D --> E
    E --> F[Relais outbox]
    F --> G[Broker]
    G --> H[Consommateur idempotent]
§§§

L’outbox rend atomiques la mutation métier et l’intention de publier, pas la livraison unique à toutes les destinations. Le relais doit gérer les reprises, l’ordre si nécessaire, les erreurs permanentes, la purge des lignes publiées et la surveillance du backlog.

Pour une API externe, utilisez une clé d’idempotence si le fournisseur le permet. Conservez le résultat et l’identité de l’opération pour éviter de créer un nouveau paiement, une nouvelle facture ou un nouvel ordre lors d’une reprise. Si le fournisseur ne propose pas de garantie d’idempotence, concevez une réconciliation et une recherche d’état avant de retenter une opération ambiguë. Un timeout peut signifier que le client ignore si le serveur a déjà effectué l’action.

## 6. Chargement incrémental et CDC

Un chargement incrémental lit uniquement les données nouvelles ou modifiées depuis une position de progression. Il peut réduire les coûts et la latence par rapport à une extraction complète. La difficulté est de définir précisément ce que signifie nouveau et comment la progression se comporte face aux retards, modifications rétroactives et suppressions.

Le curseur peut être une clé croissante, un horodatage de modification, un offset, un token de page ou une position de journal transactionnel. Un timestamp seul peut poser des problèmes : plusieurs lignes ont la même valeur, les horloges peuvent différer, une modification peut être antérieure au watermark et certaines sources réécrivent des dates. Une fenêtre de recouvrement relit une période passée puis déduplique les événements par clé ; elle augmente les lectures mais peut rattraper des écritures tardives.

Le Change Data Capture capte les insertions, mises à jour et suppressions à partir d’un journal ou d’un mécanisme de changement. Il réduit les scans répétés mais exige une gestion des offsets, des snapshots initiaux, des schémas, des permissions de lecture du journal et des retards du consommateur. L’initialisation doit décrire la frontière de cohérence entre le snapshot et le journal. Sans point de cohérence, des modifications peuvent être manquées ou appliquées deux fois.

Les suppressions sont souvent invisibles dans une extraction qui ne lit que les lignes actuelles. Le CDC peut les représenter par un événement de suppression ; une ingestion par extraction doit disposer d’une autre stratégie, comme un journal de suppressions, un statut ou un rapprochement. Un tombstone doit porter un identifiant fiable et être appliqué par les consommateurs. Les événements anciens ne doivent pas ressusciter un état supprimé plus récemment sans règle explicite.

Le checkpoint enregistre jusqu’où le consommateur considère les événements traités. Un commit anticipé peut perdre une sortie après crash ; un commit tardif peut provoquer un replay. La destination doit donc être idempotente ou participer à une transaction compatible avec la source. Une procédure de reprise doit indiquer comment vérifier la progression, choisir un offset sûr et évaluer l’impact d’un rejeu.
