
# Kafka et traitement en temps réel — Expert

## Mise en contexte : concevoir un flux fiable, pas simplement déplacer des messages

Une plateforme numérique produit une suite continue d'événements : inscription créée, paiement confirmé, progression d'un apprenant, modification d'un cours, alerte de sécurité ou mesure de télémétrie. Chaque service peut enregistrer ces événements dans sa propre base, mais plusieurs autres composants ont besoin de les consommer : moteurs d'indicateurs, alertes opérationnelles, recommandations, détection d'anomalies ou systèmes analytiques. Une intégration par appels synchrones directs entre tous les services crée rapidement des dépendances difficiles à maintenir. Une architecture orientée événements découple les producteurs des consommateurs, tout en imposant de nouvelles responsabilités de conception.

Apache Kafka est une plateforme distribuée de journaux d'événements. Les producteurs publient des records dans des topics ; les brokers stockent et servent ces records ; les consommateurs lisent les partitions en suivant leur position, matérialisée par un offset. Un topic peut être lu par plusieurs groupes indépendants, ce qui permet à plusieurs systèmes d'exploiter le même flux à des rythmes différents. Kafka n'est pas une simple file où chaque message disparaît une fois consommé : la rétention conserve les événements selon une politique de temps ou de taille, et la compaction peut retenir les dernières valeurs par clé.

Dans ce cours, nous utiliserons SkillMarket, plateforme fictive de formation. Chaque inscription, progression, paiement et certification peut produire un événement qui alimente les systèmes de reporting, de notification et de détection d'anomalies. Notre objectif est de faire évoluer un flux d'événements vers une architecture de production : clés cohérentes, partitions équilibrées, schémas versionnés, sécurité, contrôle de la rétention, reprise après panne, idempotence, transactions et observabilité.

## 1. Objectifs et prérequis

À la fin du cours, vous devrez être capable de :

- expliquer l'architecture d'un cluster Kafka et le rôle des brokers, topics, partitions, leaders, réplicas et contrôleurs ;
- dimensionner les partitions à partir du débit, du parallélisme, de l'ordre métier et de la croissance ;
- choisir une clé de partitionnement garantissant l'ordre utile sans concentrer tout le trafic sur une seule partition ;
- configurer producteurs, accusés de réception, idempotence et compression selon le contrat de fiabilité ;
- gérer groupes de consommateurs, offsets, rebalance et retards ;
- différencier rétention temporelle, rétention de taille et compaction du journal ;
- versionner les schémas et traiter les données incompatibles ou malformées ;
- expliquer les sémantiques at-most-once, at-least-once et exactly-once en distinguant les étapes couvertes ;
- concevoir une écriture idempotente vers une base ou un autre système ;
- utiliser les concepts de Kafka Streams et de traitement temporel, notamment fenêtres et événements tardifs ;
- surveiller le consumer lag, la capacité, les erreurs, les sous-répliques et le retard de bout en bout ;
- sécuriser les identités, les ACL, les flux réseau, les secrets et les données personnelles ;
- préparer un runbook de reprise, de relecture, de migration de topic et de gestion d'incident.

Ce cours suppose une compréhension des événements métier, de SQL, des transactions, des files de messages et des concepts de stockage distribué. Les exemples utilisent des noms de configuration courants de Kafka et des fragments Java/Python génériques, mais les options exactes varient selon le client, la version et la distribution. Vérifiez toujours la documentation correspondant à votre environnement avant un déploiement.

## 2. Le modèle mental de Kafka

### 2.1 Topic et record

Un topic est un flux nommé de records. Un record contient généralement une clé, une valeur, des en-têtes et un timestamp. La clé permet souvent de regrouper des événements ayant le même propriétaire métier ; la valeur porte le contenu de l'événement. La clé peut être absente, mais ce choix affecte la distribution et l'ordre. Les en-têtes transportent des métadonnées, par exemple un identifiant de corrélation ou une version, sans être un substitut à un schéma de valeur clairement défini.

Un événement utile décrit un fait qui s'est produit : inscription créée, paiement capturé, certification délivrée. Il se distingue d'une commande qui demande à un système de faire quelque chose. La distinction influence le nommage, la sémantique et les conséquences d'une relecture. Une commande peut échouer ou être refusée ; un événement publié doit représenter une transition qui a réellement été validée par son propriétaire.

Exemple d'événement de formation, illustré en JSON :

~~~json
{
  "event_id": "evt-01J9A8K5",
  "event_type": "enrollment.created",
  "event_version": 1,
  "occurred_at": "2026-10-28T08:42:11Z",
  "learner_id": "learner-42",
  "course_id": "data-streaming-expert",
  "channel": "web",
  "correlation_id": "req-7bc91"
}
~~~

L'identifiant d'événement permet au consommateur de détecter des doublons au niveau applicatif. Le type d'événement est un nom stable ; la version explicite le contrat de valeur. L'heure d'occurrence n'est pas nécessairement identique à l'heure d'ingestion : un client peut être hors ligne, une source peut reprendre des événements ou une livraison peut arriver en retard. Les deux temps peuvent être conservés lorsque l'analyse temporelle l'exige.

### 2.2 Partition : unité d'ordre et de parallélisme

Un topic est réparti en partitions. Chaque partition est un journal ordonné de records auquel des offsets sont attribués. Kafka garantit un ordre dans une partition, pas un ordre total automatique entre toutes les partitions d'un topic. La partition est également une unité de parallélisme pour les consommateurs : dans un groupe, une partition est assignée à un seul membre actif à un moment donné.

~~~mermaid
flowchart TD
    P["Producteur : événement"] --> T["Topic enrollment-events"]
    T --> A["Partition 0 : offsets 0, 1, 2…"]
    T --> B["Partition 1 : offsets 0, 1, 2…"]
    T --> C["Partition 2 : offsets 0, 1, 2…"]
    A --> C1["Consommateur groupe A"]
    B --> C2["Consommateur groupe A"]
    C --> C3["Consommateur groupe A"]
    T --> D["Groupe B : lecture indépendante"]
~~~

Les offsets sont des positions dans le journal d'une partition, pas des numéros métier universels ni des compteurs globaux pour le topic. Après une compaction ou une rétention, un offset peut ne plus correspondre à un record encore conservé ; l'offset reste cependant un repère logique de progression. Ne construisez pas des règles métier à partir d'une supposition selon laquelle les offsets de différentes partitions peuvent être comparés comme une séquence unique.

Le nombre de partitions détermine la granularité du parallélisme et affecte la distribution, les fichiers de journal, les réassignations, le nombre de tâches et les coûts de métadonnées. Trop peu de partitions peuvent limiter le débit consommateur ; trop de partitions accroissent les coûts de gestion et rendent certaines opérations plus lourdes. Il faut dimensionner en fonction d'un débit mesuré, d'une marge de croissance et des garanties d'ordre métier.

### 2.3 Brokers, leader et réplicas

Les brokers hébergent les partitions. Dans un modèle de réplication, chaque partition a un leader et des réplicas. Le leader traite les lectures et écritures selon la configuration, tandis que les réplicas recopient le journal. Le facteur de réplication exprime le nombre de copies configurées, mais il ne suffit pas à prouver qu'une écriture est durable dans tous les scénarios : il faut tenir compte de l'état des réplicas, de la politique d'acquittement et de la réplication considérée comme synchronisée.

~~~mermaid
flowchart LR
    PR["Producteur"] --> L["Broker A : leader partition 0"]
    L --> R1["Broker B : réplique"]
    L --> R2["Broker C : réplique"]
    C["Consommateur"] --> L
    L --> M["Journal de partition"]
~~~

Le terme ISR, pour In-Sync Replicas, désigne l'ensemble des réplicas considérés comme synchronisés selon les règles du cluster et le paramétrage en vigueur. Les garanties d'acquittement, par exemple acks=all côté producteur, doivent être comprises avec les paramètres de réplication et de nombre minimal de réplicas synchronisés. Une configuration incohérente peut produire soit une disponibilité trop faible, soit un risque de perte plus important que prévu. Les noms exacts et comportements de configuration doivent être vérifiés par version.

Kafka a progressivement fait évoluer son architecture de contrôleur et ses modes de gestion des métadonnées. Selon les versions, l'environnement peut s'appuyer sur ZooKeeper ou sur le mode KRaft. Une documentation de production doit annoncer la version, le mode de métadonnées, la stratégie d'identifiants, le plan de migration et les contrôles de santé. Ne mélangez pas les procédures de versions différentes.

## 3. Concevoir les topics et la clé de partitionnement

### 3.1 Un topic par contrat de flux

Les topics devraient représenter un domaine ou un contrat de données identifiable : `enrollment-events`, `payment-events`, `course-catalog-changes` ou `learner-progress-events`. Un seul topic géant mélangeant des événements sans relation impose aux consommateurs de filtrer davantage, complique la gouvernance et rend difficile la définition d'une politique de rétention. À l'inverse, un topic par type de message minuscule peut augmenter la complexité d'administration et le nombre de partitions.

La décision prend en compte le rythme de publication, les consommateurs, les droits d'accès, la rétention, la taille des records, le schéma et l'évolution attendue. Un topic doit avoir un propriétaire, une finalité, une classification de données, une équipe de support et une procédure de changement. La documentation du topic ne remplace pas le schéma versionné du record.

### 3.2 Choisir une clé métier

Une clé de partitionnement pertinente permet de préserver l'ordre des événements pour une entité. Pour les transitions d'une inscription, la clé peut être l'identifiant d'inscription. Pour la progression d'un apprenant, l'identifiant apprenant peut être préférable si le traitement doit observer les transitions dans leur ordre pour un même apprenant. Le choix n'est pas neutre : un identifiant de cours peut concentrer une forte activité sur un cours très populaire, tandis qu'un identifiant d'inscription peut répartir le trafic plus uniformément.

~~~mermaid
flowchart TD
    A["Quel ordre le métier exige-t-il ?"] --> B{"Entité ordonnée"}
    B -->|"Une inscription"| C["enrollment_id comme clé"]
    B -->|"Progression d'un apprenant"| D["learner_id comme clé"]
    B -->|"État d'un compte"| E["account_id comme clé"]
    C --> F["Tester le débit par clé"]
    D --> F
    E --> F
    F --> G["Valider ordre, skew et parallélisme"]
~~~

Il faut tester la distribution des clés avec un jeu de données réaliste. Une clé nulle ou constante peut envoyer tous les records vers la même partition selon le partitionneur utilisé. Une clé à très forte cardinalité peut être bien distribuée mais ne garantit pas l'ordre entre entités liées. Si le besoin métier nécessite un ordre global, les partitions parallèles ne fournissent pas automatiquement cette garantie ; un topic à une seule partition peut offrir un ordre total, au prix d'une limite importante de parallélisme.

### 3.3 Ajouter des partitions en production

Augmenter le nombre de partitions peut accroître le parallélisme, mais ce n'est pas une opération sans conséquences. Avec un partitionneur par défaut, le mapping de certaines clés peut changer lorsque le nombre de partitions augmente ; des événements d'une même clé peuvent alors être répartis différemment dans le topic au fil du changement, et l'ordre logique attendu peut devenir complexe. Les consumers et les outils d'exploitation doivent aussi gérer le nombre et la distribution mis à jour.

Avant d'augmenter la partition count, mesurez le goulot d'étranglement : producteur, réseau, broker, nombre de partitions, consommateurs, traitement aval ou base cible. Préparez une procédure de changement, les métriques de référence, une stratégie d'ordre, les changements de capacité et un plan de rollback réaliste. Le rollback d'une configuration de partitionnement n'est pas toujours un simple retour du nombre précédent ; la migration peut exiger un nouveau topic et un basculement des producteurs.

### 3.4 Rétention par durée, taille et compaction

Kafka conserve les records selon une politique de rétention, souvent temporelle, fondée sur la taille, ou une combinaison de règles. La rétention détermine combien de temps les consommateurs peuvent revenir en arrière et combien de données doivent être stockées. Elle constitue un contrat de reprise : si un consommateur est arrêté plus longtemps que la fenêtre disponible, il peut perdre la possibilité de relire l'historique directement depuis le topic.

La compaction est différente. Sur un topic compacté, Kafka vise à conserver au moins la dernière valeur par clé dans la partie compactée du journal, tout en préservant l'ordre des records conservés et leurs offsets. La compaction convient aux flux d'état, aux changements d'une entité ou au rechargement d'un cache, tandis qu'une rétention temporelle convient souvent aux événements où chaque occurrence possède sa propre valeur historique. Un tombstone, c'est-à-dire une valeur nulle avec clé dans le contexte de compaction, peut représenter une suppression logique ; la durée de conservation des tombstones et les délais de compaction doivent être compris.

Ne choisissez pas la compaction en supposant qu'elle conserve chaque événement. Les mises à jour anciennes pour une clé peuvent disparaître à terme ; la compaction n'est donc pas l'outil approprié si chaque changement constitue un événement auditable qui doit être préservé. De la même façon, une rétention temporelle ne constitue pas un archivage permanent. Si la donnée doit être conservée au-delà de la rétention Kafka, un pipeline d'archivage et une politique de restauration sont nécessaires.

## 4. Producteurs : débit, fiabilité et schéma

### 4.1 Choisir le mode d'acquittement

Le producteur peut attendre différentes garanties d'acquittement. Un mode sans attente d'acquittement minimise parfois la latence, mais rend plus difficile la connaissance du succès réel. Un acquittement du leader seul peut avoir un compromis distinct d'un acquittement par l'ensemble des réplicas synchronisés. Le choix exact dépend du cas métier, des paramètres brokers et du niveau de perte acceptable.

La fiabilité ne se limite pas à une option. La réplication, le facteur de réplication, le nombre minimum de réplicas synchronisés, les délais de confirmation, la politique de retry et le comportement du producteur en cas de timeout forment un ensemble. Si le producteur réessaie après un timeout, il ne sait pas nécessairement si la première tentative a été enregistrée. L'idempotence du producteur réduit certaines duplications provoquées par les retries du protocole, mais elle ne déduplique pas forcément deux événements métier identiques créés séparément par l'application.

~~~text
producer:
  acks: all
  enable.idempotence: true
  compression.type: zstd
  delivery.timeout.ms: 120000
  request.timeout.ms: 30000
~~~

Ce fragment de configuration est illustratif. Les valeurs de délai doivent s'accorder avec le délai de livraison, les retries, la latence réseau et les paramètres de brokers. Un timeout très court peut déclencher des erreurs inutiles pendant une pointe ; un timeout trop long peut masquer une dégradation et accumuler des requêtes en attente. Le type de compression doit être choisi par des tests de CPU, de latence, de ratio et de compatibilité.

### 4.2 Idempotence du producteur et identifiant métier

L'idempotence du producteur protège contre certaines duplications à l'intérieur du protocole de publication, dans les conditions et la portée prises en charge par la version. Elle n'empêche pas une application de créer deux fois le même événement suite à un double clic, une reprise de transaction ou une commande rejouée. Un identifiant d'événement stable et des règles du domaine demeurent nécessaires.

Pour les événements issus d'une base transactionnelle, le motif outbox transactionnel peut résoudre l'incohérence « base mise à jour mais message non publié ». Le service écrit la modification métier et une ligne d'outbox dans la même transaction de sa base ; un relay publie ensuite les événements et marque leur état. Le relay peut republier une entrée après une panne, donc le consommateur doit toujours tolérer les doublons ou participer à un mécanisme de déduplication. Le motif élimine une catégorie de perte silencieuse sans rendre tous les systèmes distribués magiquement atomiques.

~~~mermaid
sequenceDiagram
    participant A as Service métier
    participant DB as Base transactionnelle
    participant O as Outbox relay
    participant K as Kafka
    A->>DB: Écrire la commande et l'événement outbox
    DB-->>A: Commit atomique
    O->>DB: Lire les événements non publiés
    O->>K: Publier avec event_id stable
    K-->>O: Accusé de publication
    O->>DB: Marquer publié
~~~

La ligne outbox peut être relue si l'application ou le relay échoue après la publication mais avant la mise à jour du statut. Il faut utiliser une identité stable, un état de traitement traçable et une stratégie de nettoyage/rétention des entrées publiées. Le relay doit aussi appliquer une limite de lot et une politique de reprise, afin qu'une entrée empoisonnée ou un broker inaccessible ne bloque pas tout le flux indéfiniment.

### 4.3 Sérialisation et contrat de données

Les événements peuvent être sérialisés en JSON, Avro, Protobuf ou un autre format. JSON est facile à lire, mais sa validation et son évolution doivent être contrôlées. Des formats schématisés avec un registry et des règles de compatibilité peuvent réduire les incompatibilités accidentelles. La décision doit prendre en compte les langages clients, les besoins de lecture, les performances, la gouvernance et les garanties d'évolution.

Un schéma n'est pas simplement une liste de champs. Il définit les types, les champs obligatoires, les valeurs possibles, le sens des timestamps, les unités, les identifiants, les règles de compatibilité et parfois la sémantique de null. Une donnée monétaire doit préciser la devise et la représentation décimale. Un champ appelé status doit préciser son domaine et sa transition, sinon chaque consommateur peut implémenter ses propres règles.

Les changements additifs ne sont pas automatiquement compatibles si un champ devient obligatoire, si une valeur enum nouvelle n'est pas tolérée ou si un consommateur plus ancien ne sait pas ignorer les champs inconnus. Définissez une politique : compatibilité backward, forward ou full, avec une stratégie de déploiement du producteur et des consommateurs. Testez les schémas contre les versions prises en charge avant de publier de nouveaux événements.

### 4.4 Gestion des erreurs de production

Le producteur doit distinguer les erreurs temporaires, les erreurs de configuration et les données non valides. Une file de retry non bornée peut accumuler des événements et faire exploser la mémoire ; une suppression immédiate de toute erreur peut perdre des messages. Il faut définir un délai maximal de livraison, une limite de mémoire, la surveillance des records en attente, une politique de persistance locale si le client la fournit, et le comportement attendu lorsque le délai expire.

Les journaux ne doivent pas contenir en clair des données de carte, secrets ou attributs personnels inutiles. Les événements en échec peuvent contenir des données sensibles ; le diagnostic doit donc afficher identifiants, taille, catégorie d'erreur et métadonnées suffisantes sans exposer le payload complet par défaut.

## 5. Consommateurs, groupes et offsets

### 5.1 Groupe de consommateurs

Un consumer group représente une identité de traitement logique. Plusieurs instances du même groupe se partagent les partitions du topic, ce qui permet d'augmenter le parallélisme et de continuer à traiter après la disparition d'un membre. Des groupes différents lisent indépendamment le même topic, par exemple un groupe de reporting, un groupe de notifications et un groupe de détection de fraude.

~~~mermaid
flowchart TD
    K["Topic avec 6 partitions"] --> P0["P0"]
    K --> P1["P1"]
    K --> P2["P2"]
    K --> P3["P3"]
    K --> P4["P4"]
    K --> P5["P5"]
    P0 --> A["Groupe reporting : instance A"]
    P1 --> A
    P2 --> B["Groupe reporting : instance B"]
    P3 --> B
    P4 --> C["Groupe reporting : instance C"]
    P5 --> C
    K --> N["Groupe notifications indépendant"]
~~~

Au sein d'un groupe, le nombre de consommateurs actifs qui peuvent lire les partitions en parallèle est borné par le nombre de partitions assignées. Ajouter des consommateurs au-delà du nombre de partitions peut laisser des membres inactifs. Si une application a besoin de plus de concurrence, il faut aussi examiner la taille des messages, le temps de traitement et la possibilité de redéfinir le partitionnement sans dégrader l'ordre métier.

### 5.2 Offsets et commit

L'offset représente la position de lecture du consommateur dans une partition. Un consommateur peut avancer, se réinitialiser et relire des données tant que la rétention le permet. Le commit d'un offset enregistre la progression que le groupe pourra reprendre. Le moment du commit détermine une partie du risque de perte ou de redélivrance.

Si le consommateur commit l'offset avant la fin du traitement métier et échoue ensuite, le message peut ne pas être retraité alors que ses effets ne sont pas complets : cela donne un risque de perte logique. S'il réalise l'effet métier, puis échoue avant le commit, le message sera relu et l'effet peut se répéter. C'est pourquoi la plupart des traitements qui privilégient la sûreté combinent un commit après la réussite du travail avec une destination idempotente.

~~~mermaid
sequenceDiagram
    participant C as Consumer
    participant K as Kafka
    participant DB as Base cible
    C->>K: Lire record offset 42
    K-->>C: Record
    C->>DB: Appliquer l'effet métier
    DB-->>C: Succès
    C->>K: Commit offset suivant
    K-->>C: Progression enregistrée
~~~

Le commit d'un offset n'est pas une transaction distribuée avec n'importe quelle base de données. Une écriture réussie en base et un commit Kafka peuvent ne pas être atomiques si aucun mécanisme spécialisé ne les coordonne. Dans le scénario ci-dessus, l'échec après l'écriture et avant le commit peut provoquer une nouvelle livraison. La base cible doit donc utiliser une clé de déduplication, un upsert ou une transaction locale qui garantit qu'un même event_id n'applique pas deux fois l'effet métier.

### 5.3 Auto-commit ou commit contrôlé

L'auto-commit facilite le code, mais peut enregistrer la progression à un moment qui ne correspond pas à la fin du traitement, surtout lorsque l'application traite des lots ou effectue des appels métier lents. Le commit manuel permet de placer le point de progression au moment voulu, mais exige de gérer les échecs, les tâches parallèles, les offsets maximaux terminés et les rebalances.

Si plusieurs records sont traités en parallèle dans une même partition, les offsets ne doivent pas être commités au-delà d'un record dont le traitement est encore en attente. Sinon un arrêt peut faire perdre des effets. Des implémentations avancées maintiennent un ensemble de séquences terminées et ne confirment que le plus grand offset contigu. Pour une première architecture, un traitement séquentiel par partition peut simplifier les garanties, au prix de certains compromis de débit.

### 5.4 Rebalance et coopération entre membres

Un rebalance réattribue les partitions quand les membres d'un groupe changent ou que la stratégie d'assignation l'exige. Pendant cette période, un consommateur peut suspendre son traitement ou abandonner des partitions. Les longs traitements bloquants, les pauses mal gérées, des timeouts inadaptés et des déploiements simultanés peuvent provoquer des rebalances fréquents.

La gestion d'un rebalance doit interrompre proprement le travail sur les partitions perdues, terminer ou annuler les traitements en cours selon le contrat, commit les offsets sûrs, libérer les ressources et reprendre avec les nouvelles partitions. Un rebalance fréquent n'est pas seulement une question de performance : il peut être le symptôme d'un consommateur trop lent, d'une dépendance externe en panne ou d'une stratégie de déploiement.

## 6. Les sémantiques de livraison, du producteur au résultat métier

### 6.1 At-most-once

At-most-once cherche à éviter les doublons et accepte qu'un événement puisse être perdu. Par exemple, un consommateur peut enregistrer sa progression avant de terminer un traitement, ou un producteur peut choisir de ne pas attendre des accusés de réception. Cette sémantique peut être acceptable pour certains échantillonnages ou métriques non critiques, mais elle ne convient pas automatiquement aux paiements, factures ou transitions de droits.

### 6.2 At-least-once

At-least-once cherche à ne pas perdre les messages et accepte leur redélivrance. Le consommateur réalise l'effet métier puis commit l'offset ; si le processus s'arrête entre les deux étapes, le record est relu. C'est une stratégie courante, à condition que le traitement soit idempotent ou qu'une déduplication garantisse l'unicité de l'effet.

### 6.3 Exactly-once dans une portée précise

Kafka prend en charge l'idempotence du producteur et les transactions qui peuvent atomiquement publier plusieurs records et mettre à jour des offsets consommés, dans les workflows compatibles. Cette garantie ne signifie pas qu'un appel vers un système externe arbitraire ou un e-mail ne se produira jamais deux fois. Il faut définir la frontière transactionnelle et vérifier les capacités du sink.

~~~mermaid
flowchart TD
    A["Record lu"] --> B["Transformation"]
    B --> C{"Destination et offset coordonnés ?"}
    C -->|Oui, mécanisme compatible| D["Transaction / commit atomique"]
    C -->|Non| E["Traitement idempotent et déduplication"]
    D --> F["Résultat cohérent dans la portée promise"]
    E --> G["Doublon neutralisé au niveau métier"]
~~~

Le vocabulaire « exactement une fois » doit toujours être accompagné d'une définition de périmètre : entre producteur et log, dans le flux de transformation, entre offsets et records produits, dans la base cible ou pour l'effet métier complet. Un système peut avoir un producteur idempotent et un consommateur at-least-once ; la livraison globale n'est pas automatiquement exactly-once.

### 6.4 Transactions Kafka

Un producteur transactionnel peut publier un lot atomique de records et, dans le modèle de traitement consommer-transformer-produire, inclure la progression de lecture dans la transaction. Le consommateur peut être configuré avec un niveau d'isolation adapté pour ne lire que les transactions validées. Les IDs transactionnels doivent être gérés pour éviter que deux instances concurrentes utilisent le même identifiant logique sans coordination.

L'emploi de transactions ajoute un coût et des prérequis opérationnels : timeout de transaction, état des transactions, compatibilité des brokers et clients, rebalances et traitement des erreurs. Les transactions Kafka ne couvrent pas automatiquement des écritures arbitraires vers une base SQL. Lorsque le sink n'est pas transactionnellement intégré, l'idempotence métier et la réconciliation restent indispensables.

## 7. Architecture d'un consommateur robuste

Un consommateur de production doit vérifier le schéma, valider les champs essentiels, traiter les erreurs fonctionnelles, enregistrer des métriques et avancer sa progression au bon moment. Le chemin d'erreur doit faire une distinction entre un record temporairement impossible à traiter, un événement invalide, une panne transitoire de la base cible et une erreur de code. Une politique uniforme « retry pour toujours » provoque des blocages ; une politique uniforme « ignorer toute erreur » crée une perte silencieuse.

~~~mermaid
flowchart TD
    A["Lire record"] --> B["Désérialiser / valider schéma"]
    B -->|valide| C["Contrôle métier"]
    B -->|invalide| D["DLQ avec métadonnées"]
    C -->|transitoire| E["Retry borné / backoff"]
    C -->|définitif| D
    C -->|valide| F["Écriture idempotente"]
    E -->|échec épuisé| D
    F --> G["Commit offset sûr"]
    D --> H["Alerte et procédure de correction"]
~~~

Une dead-letter queue ou DLQ est un topic de quarantaine pour les records qui ne peuvent pas être traités normalement. Elle doit conserver l'origine, le topic/partition/offset source, la version du schéma, le motif de rejet et l'identifiant de corrélation, en limitant les données sensibles. Une DLQ n'est pas un cimetière : elle nécessite des alertes, un propriétaire, un délai de traitement et une procédure de relecture après correction.

Le retry doit être borné et compatible avec l'ordre de la partition. Si un événement doit être traité avant les suivants pour la même entité, sauter immédiatement un record en erreur peut violer l'invariant métier. Dans ce cas, il faut décider si la partition s'arrête, si l'événement est mis en quarantaine avec une compensation ou si l'ordre métier accepte un traitement ultérieur. Ne laissez pas une DLQ silencieuse masquer la perte d'une transition critique.

## 8. Fenêtres temporelles, événements tardifs et Kafka Streams

Kafka est un journal d'événements ; les agrégations de fenêtres sont généralement réalisées par le consommateur ou un moteur de traitement comme Kafka Streams, Flink ou Spark Structured Streaming. Kafka Streams permet de construire des topologies d'applications, des opérations d'état, des jointures et des fenêtres, en utilisant des topics comme source et destination. Le choix du moteur dépend du modèle d'état, de la latence, des connecteurs, des opérations et des compétences de l'équipe.

### 8.1 Event time, processing time et ingestion time

Event time correspond à l'heure métier indiquée par l'événement. Processing time correspond au moment où le système traite le record. Ingestion time désigne l'heure à laquelle l'événement a été intégré ou horodaté dans l'infrastructure selon la définition utilisée. Ces temps peuvent différer significativement en cas de latence réseau, d'appareil hors ligne ou de reprise d'une source.

Pour mesurer la progression d'apprentissage par heure réelle de l'événement, event time est généralement important. Pour dimensionner la charge du service ou mesurer le retard de pipeline, processing time et ingestion time peuvent également être nécessaires. Le modèle doit conserver suffisamment de métadonnées pour expliquer cette différence.

### 8.2 Fenêtres tumbling, hopping et session

Une fenêtre tumbling est une fenêtre fixe non chevauchante, par exemple chaque intervalle de cinq minutes. Une fenêtre hopping avance par un pas déterminé et peut se chevaucher. Une fenêtre de session regroupe des événements proches dans le temps selon une période d'inactivité. Chaque modèle possède une signification métier distincte ; une fenêtre qui se chevauche ne doit pas être additionnée comme si les groupes étaient disjoints.

~~~mermaid
flowchart LR
    A["Événements horodatés"] --> B["Fenêtres temporelles"]
    B --> C["Tumbling : fixes sans chevauchement"]
    B --> D["Hopping : chevauchement possible"]
    B --> E["Session : activité séparée par inactivité"]
    C --> F["Agrégation et état"]
    D --> F
    E --> F
~~~

Le watermark ou seuil d'acceptation du retard définit comment le système traite les événements arrivés après la fenêtre attendue. Les événements tardifs peuvent modifier le résultat, être ignorés après un seuil, ou être redirigés vers une correction batch. La règle doit refléter le coût du maintien d'état, le retard observé et l'exigence d'exactitude métier.

### 8.3 État et restauration

Une agrégation continue maintient souvent un état : nombre de vues par cours et fenêtre, total de paiements par compte, ou dernière progression connue d'un apprenant. Cet état doit être stocké selon les garanties du moteur et restauré au redémarrage. L'effacement ou l'incompatibilité de l'état lors d'une mise à jour peut empêcher la reprise ou modifier le résultat. La procédure de déploiement doit préciser la compatibilité des stores, les migrations d'état, la rétention et les exigences de sauvegarde.

Une application stateful doit mesurer la taille de l'état, la fréquence des mises à jour, le coût des checkpoints et le retard de traitement. Un état par clé non borné, comme toutes les sessions sans expiration, peut croître sans limite. Il faut définir une fenêtre ou politique de purge quand le métier le permet et tester le comportement sur des cardinalités réalistes.

## 9. Contrats de données, compatibilité et évolution des topics

L'évolution du schéma est l'un des risques majeurs des systèmes orientés événements : un producteur évolue souvent avant qu'il soit certain que tous les consommateurs ont été mis à jour. Une stratégie de compatibilité définit quels changements sont tolérés et dans quel ordre ils sont déployés. Ajouter un champ facultatif peut être compatible avec certains consommateurs ; changer le type d'un champ ou la sémantique d'un statut peut casser un traitement même si le JSON se parse toujours.

Chaque événement doit avoir un propriétaire, une version, un sens métier, une date d'occurrence, une clé stable, des règles de confidentialité et une politique de rétention. Un schéma registry peut centraliser la validation et la compatibilité pour les formats pris en charge. Les équipes doivent aussi décider comment traiter les champs inconnus, les valeurs enum nouvelles, les données nulles et les évolutions des timestamps.

### 9.1 Changement incompatible

Si une modification casse le contrat, une option est de publier une version d'événement ou un nouveau topic, puis de migrer progressivement les consommateurs. Une autre consiste à réaliser un déploiement compatible en plusieurs étapes : consommateurs tolérants d'abord, producteurs ensuite, suppression des anciennes formes enfin. La décision dépend du nombre de consommateurs, des contraintes d'exploitation et du degré d'incompatibilité.

Ne renommez pas un champ ou ne changez pas sa sémantique au seul motif que cela rend le code producteur plus simple. Les consommateurs peuvent dépendre de ce champ sans que l'équipe productrice le sache. La découverte des abonnés, les tests de compatibilité et les responsabilités d'approbation font partie du cycle de vie du schéma.

### 9.2 Enveloppe d'événement commune

Une enveloppe commune peut contenir l'identifiant d'événement, le type, la version du schéma, l'heure d'occurrence, l'heure de publication, l'identité du producteur et les champs de corrélation. Les données métier restent propres à chaque événement. Cette enveloppe facilite les logs, la traçabilité et les mécanismes génériques sans forcer tous les événements à partager un schéma métier unique.

L'enveloppe doit rester stable et minimaliste. Copier toutes les données de l'acteur ou toutes les données de la commande dans chaque record peut exposer des informations personnelles et augmenter le coût de stockage. Une référence métier peut être préférable si le consommateur a besoin d'un état courant, mais elle modifie aussi les garanties de lecture historique.

## 10. Rétention, compaction et archivage

La rétention Kafka contrôle la durée de disponibilité des segments du journal. Les paramètres liés au temps et à la taille doivent être basés sur le volume de production, la durée maximale de panne des consommateurs et les coûts de stockage. Une rétention insuffisante peut empêcher un consommateur en retard de rattraper l'historique ; une rétention excessive augmente le coût et peut laisser des données sensibles disponibles plus longtemps que nécessaire.

La compaction retient les valeurs les plus récentes par clé dans la partie compactée d'un topic et peut permettre la reconstruction d'un état. Elle ne constitue pas l'outil approprié pour conserver chaque modification comme un journal d'audit exhaustif. Les tombstones peuvent être retirés après un délai de conservation configuré ; les consommateurs très en retard doivent en tenir compte avant de prétendre reconstruire entièrement une vue.

~~~mermaid
flowchart TD
    A["Topic Kafka"] --> B{"Politique de rétention"}
    B --> C["Delete : durée ou taille"]
    B --> D["Compact : dernière valeur par clé"]
    C --> E["Flux d'événements historiques limités"]
    D --> F["Reconstruction d'état par clé"]
    E --> G["Archivage externe si conservation longue"]
    F --> H["Snapshot ou bootstrap de consommateurs"]
~~~

Si l'entreprise doit conserver les événements au-delà de la rétention Kafka, créez un pipeline d'archivage vers une plateforme adaptée avec des contrôles d'intégrité et une politique de rétention. Un export doit garder les métadonnées nécessaires pour interpréter les records : identifiants, partition, offset, timestamps et version de schéma. L'archive ne remplace pas l'exploitation du topic, mais fournit une conservation distincte.

La taille des segments, le débit d'écriture, les replicas, la compaction et les consommateurs en retard influencent la capacité disque. Surveillez le taux de remplissage et prévoyez une marge de croissance et de panne. Une alerte « disque à 95 % » est souvent trop tardive si un producteur continue de remplir les partitions à un débit élevé ; le seuil doit tenir compte du temps requis pour agir.

## 11. Performance et dimensionnement

La performance dépend du débit des producteurs, de la taille des records, de la compression, du nombre de partitions, du nombre et du rythme des consommateurs, du stockage et du réseau. Mesurez séparément records par seconde, octets par seconde, latence d'accusé de réception, latence de traitement et retard consommateur. Le débit moyen ne permet pas de voir les pointes, les records volumineux ni une partition chaude.

La compression peut réduire le réseau et l'espace stocké, mais utilise du CPU. Batch.size et linger.ms du producteur peuvent regrouper des records, en échange d'une latence potentiellement supérieure. Le réglage de la taille de lot, du nombre de requêtes simultanées et des buffers doit être réalisé à partir d'un test représentatif. Les valeurs optimales varient selon la distribution des clés et la taille des payloads.

### 11.1 Consumer lag

Le consumer lag mesure la différence entre la position disponible dans le log et la position de progression du groupe, selon les outils et définitions utilisés. Il peut être élevé parce que le consommateur est trop lent, que des partitions ont une clé déséquilibrée, que la base cible est lente, que le groupe rebalance souvent ou que la source reçoit un pic. Une hausse temporaire ne prouve pas nécessairement une panne ; la durée, la pente et la capacité de rattrapage sont importantes.

~~~mermaid
flowchart TD
    A["Lag augmente"] --> B["Débit producteur versus consommateur"]
    B --> C{"Consommateur assez rapide ?"}
    C -->|Non| D["Mesurer temps de traitement"]
    D --> E["Base aval / API / calcul"]
    C -->|Oui| F["Vérifier rebalance et erreurs"]
    E --> G["Corriger le goulot"]
    F --> G
    G --> H["Vérifier retour du lag à la cible"]
~~~

Si le consommateur ne peut traiter que 80 000 records par seconde alors que le producteur en publie 100 000, le retard augmente continuellement. Augmenter le nombre de membres du groupe peut aider uniquement si des partitions et des ressources sont disponibles, et si l'application peut paralléliser le traitement sans casser l'ordre. Sinon, il faut optimiser le traitement ou revoir l'architecture.

### 11.2 Capacité et tolérance aux pannes

Le dimensionnement du stockage doit inclure les octets de données, la réplication, l'overhead, les indices et les marges opérationnelles. Une estimation simple du volume retenu multiplie le débit moyen en octets par la durée de rétention, puis applique une marge pour les pointes et l'overhead, en tenant compte de la stratégie de compression. Cette estimation doit être validée par des mesures de cluster réel ; un facteur de réplication trois n'implique pas que les trois copies puissent être ignorées dans l'estimation disque.

Le dimensionnement des partitions tient compte du débit maximal par partition et du parallélisme souhaité. Il faut considérer la capacité de chaque broker, la répartition des leaders, les transferts lors d'une panne et les opérations de rebalancement. Un cluster à capacité moyenne suffisante peut échouer si un broker tombe et que la charge restante dépasse la capacité des autres brokers.

## 12. Sécurité et confidentialité

Kafka est une plateforme centrale dans l'architecture : un topic mal protégé peut divulguer des données ou permettre à un producteur d'injecter des événements faux. La sécurité doit couvrir réseau, authentification, autorisation, chiffrement, gestion des secrets, logs et classification des données. Le fait qu'un topic ne soit pas exposé aux utilisateurs finaux ne le rend pas automatiquement sûr.

Appliquez une identité distincte à chaque service, des ACL minimales pour publier et consommer uniquement les topics requis, et des règles dédiées à l'administration. Activez TLS pour les liaisons qui le requièrent et adoptez le mécanisme d'authentification disponible dans la distribution, par exemple SASL selon l'environnement. Les configurations et procédures doivent être testées avec les vrais comptes de service, pas uniquement avec une identité d'administrateur.

Les données personnelles doivent être minimisées. Une clé de partition n'est pas le meilleur endroit pour un numéro de téléphone, un e-mail ou une donnée secrète. Les noms de clés et les logs peuvent être exportés vers des outils de monitoring. Une DLQ peut contenir le payload complet d'un événement invalide ; protégez sa visibilité et définissez sa rétention. Le masquage de log doit préserver l'identifiant de corrélation tout en évitant de copier des secrets et les données de paiement.

Des droits producteurs trop larges peuvent permettre à un service de falsifier un événement d'un autre domaine. Des droits de consommation trop larges peuvent fournir un accès indirect à des données sensibles. Utilisez des noms de service explicites et documentez les dépendances. Les changements de permissions sont des changements de sécurité et doivent avoir une procédure d'approbation, de test et d'audit.

## 13. Observabilité et runbooks

Une plateforme Kafka doit être observable du producteur au consommateur. Les métriques utiles comprennent le débit, les erreurs de production, les délais d'accusé de réception, la disponibilité des brokers, l'état des réplicas, les partitions sous-répliquées ou sans leader, l'utilisation disque, le consumer lag, les rebalances, la durée des traitements et les taux de DLQ. Les métriques métier, comme les événements reçus par minute et les certificats produits, permettent de détecter des pannes silencieuses.

~~~mermaid
flowchart TD
    A["Alerte de flux"] --> B{"Quel signal ?"}
    B --> C["Producer errors / latency"]
    B --> D["Broker / réplication / disque"]
    B --> E["Consumer lag / rebalances"]
    B --> F["DLQ / qualité métier"]
    C --> G["Localiser le premier point en échec"]
    D --> G
    E --> G
    F --> G
    G --> H["Réparer, rejouer et réconcilier"]
~~~

Les alertes devraient correspondre à une conséquence exploitable. Une hausse du lag peut être un avertissement ; un lag qui dépasse la fenêtre de fraîcheur métier est un incident. Une partition sous-répliquée peut être critique si elle réduit la tolérance à une panne supplémentaire. Les seuils varient selon la rétention et le SLO, mais doivent être documentés et testés.

### 13.1 Runbook : consommateur bloqué

1. Confirmer le groupe, les partitions concernées et l'évolution du lag.
2. Vérifier la santé du broker, la connectivité et les erreurs du client.
3. Examiner les logs pour trouver des records mal formés, des timeouts aval ou une erreur qui empêche de progresser.
4. Mesurer la durée de traitement et contrôler si une seule partition ou clé concentre le travail.
5. Choisir une réparation sûre : corriger le service, limiter le débit, reprocesser une plage, ou isoler un événement conformément à la politique.
6. Vérifier que les offsets sont cohérents, que les effets métier ne sont pas doublés et que la DLQ est suivie.
7. Documenter la cause, la durée, la quantité de records affectés et les actions de prévention.

### 13.2 Runbook : broker perdu ou disque saturé

Évaluez d'abord la disponibilité des leaders et la santé des réplicas. Ne supprimez pas les journaux arbitrairement pour libérer de l'espace : cela peut détruire la possibilité de rattrapage des groupes. Vérifiez le débit de remplissage, la rétention, la réplication, l'espace restant sur chacun des volumes et les limites du fournisseur. Une rétention d'urgence peut être une décision de perte de données et doit passer par une évaluation explicite du contrat métier.

Lors d'une perte de broker, surveillez les élections de leaders, le déplacement de charge, la disponibilité des partitions et la vitesse de récupération. Une réplique non synchronisée peut rendre la récupération plus délicate, selon les garanties de l'écriture. Après le retour à l'état normal, vérifiez que les partitions sont répliquées selon l'objectif et que le débit/lag s'est stabilisé ; ne concluez pas l'incident au seul redémarrage du processus.

### 13.3 Relecture et réparation des données

Kafka permet souvent de relire des records tant qu'ils sont conservés. Mais relire directement un groupe de production depuis une position ancienne peut répéter des effets métier. La méthode la plus sûre peut être un groupe de reconstruction distinct, une destination temporaire, un topic de replay contrôlé ou une reconstruction de table par snapshot. Définissez une plage d'offsets ou de timestamps, un identifiant de campagne de relecture, un mécanisme d'isolation et une méthode de rapprochement des résultats.

La relecture doit prendre en compte la compaction et la rétention. Si des records ont été supprimés par la rétention, Kafka ne peut pas les fournir. Si la compaction a supprimé des versions anciennes d'une clé, elle peut fournir un état final, mais pas un historique complet. L'archive externe doit être utilisée si l'historique intégral est nécessaire et a été conservé.

## 14. Atelier pratique : flux d'événements SkillMarket

L'atelier ci-dessous décrit une architecture locale de test. Les noms de conteneurs, commandes et versions doivent correspondre à l'environnement retenu. Pour une expérimentation, utilisez une instance isolée et des données synthétiques, jamais un topic critique de production.

### Étape A — Définir le contrat d'événement

~~~json
{
  "event_id": "evt-000042",
  "event_type": "progress.updated",
  "event_version": 1,
  "occurred_at": "2026-10-28T09:10:00Z",
  "learner_id": "learner-42",
  "course_id": "data-streaming-expert",
  "progress_percent": 65,
  "correlation_id": "lab-run-01"
}
~~~

Le contrat doit spécifier que progress_percent est un entier de 0 à 100, que learner_id et course_id sont stables, que event_id identifie une occurrence unique et que occurred_at représente l'heure métier. Le producteur doit refuser ou corriger les données invalides avant de publier. Le consommateur doit encore valider, car les messages peuvent provenir d'une ancienne version ou d'un autre producteur.

### Étape B — Définir le topic et la stratégie

Créez en environnement de test un topic dédié aux événements de progression, avec un nombre de partitions choisi pour l'exercice, un facteur de réplication compatible avec le cluster disponible et une rétention courte. Pour l'ordre de progression par apprenant, évaluez learner_id comme clé. Vérifiez ensuite la distribution des clés et demandez-vous si un seul apprenant très actif pourrait dominer une partition.

Une configuration de test n'est pas une recommandation de production. Le facteur de réplication doit être compatible avec le nombre de brokers et les objectifs de tolérance à la panne. Ne réduisez pas la sécurité en production pour faire fonctionner un exemple local ; adaptez l'environnement de test à une configuration sécurisée ou documentez précisément les différences.

### Étape C — Consommateur idempotent

Le pseudocode suivant illustre l'ordre logique du traitement, indépendamment d'un client Python ou Java spécifique :

~~~text
pour chaque record reçu :
    valider le schéma
    vérifier event_id
    commencer une transaction locale dans la base cible
    si event_id n'est pas déjà traité :
        mettre à jour la progression de l'apprenant
        enregistrer event_id dans une table d'événements traités
    valider la transaction locale
    commiter l'offset Kafka après que le traitement est confirmé
~~~

La table d'événements traités et la mise à jour métier doivent être dans la même transaction de la base cible, avec une contrainte d'unicité sur event_id. Ainsi, un record relu après un crash peut être détecté sans répéter la modification. La transaction locale et le commit Kafka restent deux opérations séparées, mais l'idempotence neutralise la redélivrance dans ce modèle. Pour un moteur ou un sink qui fournit une autre garantie, utilisez son mécanisme transactionnel documenté.

### Étape D — Tester les défaillances

Effectuez au minimum quatre tests :
- interrompre le consommateur avant l'écriture métier ;
- interrompre le consommateur après l'écriture métier mais avant le commit de l'offset ;
- publier deux fois le même event_id ;
- arrêter temporairement la base cible et observer le retry, le lag et la reprise.

Pour chaque test, comparez les records reçus, les offsets commités, les lignes métier, les entrées de déduplication, les erreurs et la latence. Un test « le processus redémarre » est insuffisant : le résultat métier doit être prouvé sans perte ni double effet.

### Étape E — Relecture contrôlée

Créez un groupe de test séparé et relisez les messages selon une stratégie de reset d'offset explicitement configurée. Écrivez vers une sortie temporaire, puis comparez les totaux et les événements uniques au résultat attendu. Ne lancez pas une relecture depuis le début sur un groupe de production dont les consommateurs déclenchent des paiements, envoient des notifications ou modifient des droits sans un plan de prévention des effets répétés.

## 15. Douze exercices corrigés

### Exercice 1 — Ordre entre partitions

Un flux compte douze partitions. L'équipe affirme qu'un événement dans la partition 4 sera toujours traité après tous ceux de la partition 3. Est-ce correct ?

**Correction :** Non. Kafka maintient l'ordre dans une partition, pas un ordre total entre partitions. Si un ordre est nécessaire pour une entité, choisissez une clé qui envoie ses événements vers la même partition, et concevez le traitement pour préserver cet ordre.

### Exercice 2 — Choix de la clé

La progression doit être ordonnée par apprenant, mais la clé du topic est course_id. Quel problème peut se produire ?

**Correction :** Les événements d'un même apprenant peuvent être répartis entre plusieurs partitions s'ils concernent plusieurs cours, ce qui supprime l'ordre global de cet apprenant. Une clé learner_id correspond mieux à cet invariant, sous réserve de vérifier le skew et le volume par apprenant.

### Exercice 3 — Commit trop tôt

Un consommateur commit l'offset dès qu'il reçoit un message, puis écrit la base de données. Le processus tombe avant l'écriture. Quel est le risque ?

**Correction :** Kafka peut reprendre après l'offset déjà commité et ne pas redélivrer le message ; l'effet métier sera absent. Pour un traitement fiable, commit après la réussite du traitement, ou utilisez un mécanisme transactionnel adapté à la source et au sink.

### Exercice 4 — Écriture réussie mais commit absent

Une base cible a enregistré un événement, puis le consommateur s'arrête avant le commit de l'offset. Que faut-il éviter ?

**Correction :** La relivraison peut provoquer un second effet. Une clé event_id stable, une contrainte d'unicité et une transaction locale qui combine déduplication et mise à jour métier permettent de rendre la répétition sans danger.

### Exercice 5 — Idempotence producteur

L'équipe active l'idempotence du producteur mais l'application peut créer deux événements différents pour un même paiement après un retry métier. Est-ce suffisant ?

**Correction :** Non. L'idempotence du protocole limite certains doublons introduits par les retries du producteur, mais elle ne remplace pas l'identité métier. L'application doit utiliser un identifiant stable de transaction ou d'événement et éviter de recréer un nouvel événement pour la même opération métier.

### Exercice 6 — Retention ou compaction

Le topic contient toutes les transitions de statut d'une certification, et un audit exige chaque changement historique. Quelle politique doit-on examiner ?

**Correction :** Une politique de rétention adaptée à la durée d'audit ou un archivage durable doit préserver les transitions. La compaction par clé peut supprimer les valeurs intermédiaires en ne conservant que l'état final et ne convient donc pas à l'historique exhaustif.

### Exercice 7 — Consumer lag

Le lag grimpe continuellement même lorsque tous les membres du groupe sont actifs. Quelle première mesure est pertinente ?

**Correction :** Comparer le débit produit et consommé, mesurer la durée par record et par partition, puis examiner les appels au sink, le skew, les rebalances et les erreurs. Ajouter des consommateurs n'aide que si les partitions et la capacité permettent un parallélisme supplémentaire.

### Exercice 8 — Rebalance fréquent

Un groupe rebalance chaque minute et les membres traitent parfois des appels longs vers une API. Quelle piste faut-il examiner ?

**Correction :** Vérifier les délais de polling/session, les traitements bloquants, les pauses entre polls, la santé du membre et la configuration du client. Le traitement long doit être organisé pour respecter le protocole du consommateur et éviter de perdre l'assignation ou de provoquer des rebalances permanents.

### Exercice 9 — Événement tardif

Une progression horodatée 10:00 arrive à 10:18, alors que la fenêtre de dix minutes a été fermée à 10:15. Quelle décision doit être prise ?

**Correction :** Elle dépend du contrat métier et du moteur : accepter et corriger la fenêtre, ignorer après un watermark, ou envoyer l'événement vers une voie de réconciliation. Le choix doit être explicite, mesurer le retard et garantir la cohérence des agrégats.

### Exercice 10 — DLQ

Un consommateur envoie chaque record en échec à un topic DLQ mais ne surveille jamais ce topic. Pourquoi est-ce dangereux ?

**Correction :** Des données peuvent s'accumuler sans correction, dissimulant une perte fonctionnelle ou une incompatibilité de schéma. La DLQ doit avoir un propriétaire, des alertes, un motif de rejet, une politique de conservation et un processus de réparation et de relecture.

### Exercice 11 — Exactement une fois

Un flux Spark ou Kafka publie un résultat dans Kafka puis envoie un e-mail. Peut-on conclure que l'e-mail sera envoyé exactement une seule fois grâce à la transaction Kafka ?

**Correction :** Non. La transaction Kafka ne coordonne pas automatiquement un appel externe comme l'e-mail. Il faut une stratégie dédiée, par exemple une outbox, un service d'envoi idempotent ou une clé de déduplication côté service d'e-mail.

### Exercice 12 — Partitionnement insuffisant

Un topic a deux partitions et les consommateurs sont huit, mais seules deux instances travaillent. Que faut-il comprendre ?

**Correction :** Le parallélisme utile dans le groupe est limité par les partitions assignables. Ajouter des membres ne crée pas de nouvelles partitions. Il faut vérifier si davantage de partitions est possible sans casser l'ordre, si le throughput nécessite ce changement et comment migrer les clés de façon sûre.

## 16. Défi final corrigé : un pipeline de progression fiable

### Énoncé

SkillMarket souhaite alimenter en quasi temps réel un tableau de progression, envoyer des alertes lorsqu'un apprenant atteint un seuil et conserver un historique des événements pour corriger les calculs après une panne. Plusieurs consommateurs lisent le même flux : un service de reporting, un service de notification et un système d'audit. Des événements peuvent être répétés, arriver en retard ou être temporairement impossibles à traiter.

### Architecture proposée

**Producteur.** Le service métier enregistre les transitions et utilise un outbox transactionnel si la publication doit être liée à une mise à jour en base. Chaque événement possède un event_id stable, un type, une version de schéma, une date d'occurrence, une clé métier et un identifiant de corrélation. Les records sont validés avant publication et la stratégie d'acquittement est adaptée à la criticité du flux.

**Topics et clés.** Un topic de progression utilise une clé learner_id si l'ordre des événements d'un apprenant constitue l'invariant principal. Un topic de notifications peut être alimenté par un consommateur dédié afin de ne pas lier sa disponibilité au service de reporting. Les partitions sont dimensionnées selon débit, skew, parallélisme, croissance et rétention. Les droits et les propriétaires sont distincts par domaine.

**Consommation.** Le reporting et l'audit utilisent des groupes indépendants. Le traitement métier est idempotent par event_id. L'offset est avancé après le résultat sûr, ou un mécanisme transactionnel documenté garantit l'association entre offset et sortie Kafka lorsque cela s'applique. Les appels externes non transactionnels, comme les e-mails, nécessitent un mécanisme de déduplication ou une outbox.

**Temps métier.** Le système distingue occurred_at, ingestion time et processing time. Les agrégats par fenêtre acceptent les retards conformément à une règle de watermark. Les événements tardifs sont conservés pour réconciliation si leur impact métier l'exige. Les sorties indiquent leur fraîcheur et le retard réel du flux.

**Panne.** Un consommateur bloqué déclenche une alerte sur lag et durée de traitement. Les erreurs temporaires subissent un retry borné avec backoff ; les erreurs de contrat vont dans une DLQ sécurisée. La reprise enregistre les offsets et les IDs de corrélation. Après correction, un groupe de replay ou un chemin de reconstruction compare les résultats avant d'être promu.

**Rétention.** La rétention du topic couvre la durée maximale de panne et de reprise admissible, avec marge pour les pointes. L'audit à long terme est archivé séparément si nécessaire. La politique de compaction n'est activée que sur un flux d'état où conserver la dernière valeur par clé répond au besoin ; elle n'est pas appliquée par défaut à l'historique complet des transitions.

**Sécurité.** Chaque producteur et consommateur utilise une identité de service et des ACL minimales. Les flux sont chiffrés selon les exigences de l'environnement, les secrets sont stockés hors du code et les données personnelles sont réduites au strict nécessaire. Les topics d'erreurs et d'audit bénéficient d'une classification et d'une politique de conservation adaptées.

**Validation.** Le test de charge reproduit le débit de pointe et les tailles de records réalistes. Les tests de panne interrompent le producteur après l'envoi, le consommateur après écriture métier et avant commit, la base cible pendant une pointe et une partition pendant l'exploitation. Le résultat attendu comprend absence de perte dans le contrat retenu, effets métier idempotents, lag rattrapé, DLQ traitée et audit reconstitué.

## 17. Checklist de révision

- [ ] Je peux expliquer topic, partition, record, offset, leader, réplique et ISR.
- [ ] Je choisis une clé de partitionnement qui respecte les invariants d'ordre.
- [ ] Je dimensionne les partitions en tenant compte du débit et du skew.
- [ ] Je comprends la différence entre idempotence producteur et idempotence métier.
- [ ] Je sais placer le commit d'offset après un effet sûr et traiter les rebalances.
- [ ] Je distingue rétention temporelle, rétention par taille, compaction et archivage.
- [ ] Je sais expliquer les portées et limites d'exactly-once.
- [ ] Je conçois retries bornés, DLQ, déduplication et relecture.
- [ ] Je différencie event time, processing time, ingestion time et watermark.
- [ ] Je définis la compatibilité du schéma et la procédure de migration.
- [ ] Je surveille débit, erreurs, réplicas, disque, lag et fraîcheur métier.
- [ ] Je peux exécuter un plan de panne et prouver que le résultat métier reste correct.

## 18. Documentation officielle

Les paramètres et garanties peuvent changer avec la version et le client. Vérifiez les pages correspondant à la version déployée et les contrats exacts des connecteurs.

- Apache Kafka, documentation et concepts : https://kafka.apache.org/documentation/
- Apache Kafka, design et sémantiques de livraison : https://kafka.apache.org/documentation/#design
- Apache Kafka, configuration producteur : https://kafka.apache.org/documentation/#producerconfigs
- Apache Kafka, configuration consommateur : https://kafka.apache.org/documentation/#consumerconfigs
- Apache Kafka, configuration broker : https://kafka.apache.org/documentation/#brokerconfigs
- Apache Kafka, topics et opérations administratives : https://kafka.apache.org/documentation/#basic_ops
- Apache Kafka Streams, documentation : https://kafka.apache.org/documentation/streams/
- Apache Kafka, compaction de log : https://kafka.apache.org/documentation/#compaction
- Apache Kafka, Connect : https://kafka.apache.org/documentation/#connect

Une architecture événementielle experte n'est pas celle qui active le plus de paramètres de fiabilité. C'est celle qui relie chaque garantie à un invariant métier, mesure la capacité réelle, limite les effets de panne et dispose d'une procédure de reprise démontrable. Les événements, les offsets, les transactions, l'archivage et la qualité doivent former un contrat cohérent de bout en bout.
