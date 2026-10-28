
# Data Lakes et Lakehouse — Expert

## Mise en contexte : du stockage massif à un produit de données gouverné

Une entreprise moderne peut produire des journaux applicatifs, des événements Kafka, des exports SQL, des fichiers de télémétrie, des images, des résultats de modèles et des données de partenaires. Les formats et fréquences varient, tandis que les usages vont du traitement batch aux tableaux de bord, de l'exploration scientifique à l'entraînement de modèles. Conserver chaque type de données dans un système transactionnel unique est rarement optimal. C'est l'une des raisons pour lesquelles les architectures de données ont adopté les Data Lakes, puis les architectures Lakehouse.

Un Data Lake est une plateforme de stockage capable de conserver de grandes quantités de données, souvent dans un stockage objet et dans des formats variés. Il sépare relativement le stockage du calcul : les données sont conservées dans un emplacement partagé, tandis que différents moteurs peuvent les lire et les transformer selon les permissions disponibles. Cette flexibilité permet de conserver une copie brute avant de définir toutes les analyses, mais elle crée un risque de « marécage de données » : fichiers sans propriétaire, schémas inconnus, doublons, dates non documentées, droits trop larges et tables impossibles à reconstruire.

Un Lakehouse cherche à conserver la flexibilité et l'économie d'un lac tout en apportant des capacités de gestion de tables analytiques : transactions, snapshots cohérents, évolution contrôlée du schéma, gestion des fichiers, métadonnées, opérations d'upsert et parfois time travel. Des formats de tables ouverts comme Apache Iceberg, Delta Lake et Apache Hudi répondent à des besoins proches mais n'ont pas des APIs ni des garanties identiques. Ils s'appuient généralement sur des fichiers de données et des métadonnées, avec des mécanismes permettant au moteur de connaître l'état logique de la table.

Dans ce cours, nous concevrons une architecture pour SkillMarket, plateforme de formation qui collecte des inscriptions, des paiements, des événements de progression et des journaux de sécurité. Nous devons conserver les données sources, les préparer, rendre certains jeux de données réutilisables par Spark et les outils SQL, appliquer les contrôles d'accès et permettre la reprise d'un traitement. L'objectif n'est pas de choisir un produit à la mode, mais de savoir quelles garanties sont nécessaires et comment les tester.

## 1. Objectifs et prérequis

À la fin du cours, vous devrez savoir :

- distinguer Data Lake, Data Warehouse, Data Mart et Lakehouse ;
- concevoir des zones d'atterrissage, brutes, préparées et publiées sans confondre stockage et qualité ;
- comprendre la différence entre stockage objet, système de fichiers distribué, catalogue et moteur de calcul ;
- choisir entre CSV, JSON, Avro, Parquet et ORC selon les cas d'usage ;
- concevoir un schéma de données versionné et contrôler les changements ;
- expliquer les rôles des formats de tables Apache Iceberg, Delta Lake et Apache Hudi ;
- comprendre snapshots, métadonnées, fichiers de manifeste ou de log et publication atomique ;
- utiliser des opérations incrémentales, upserts, compaction et time travel selon les capacités de la table ;
- maîtriser les risques des petits fichiers, du partitionnement inadéquat et des écritures concurrentes ;
- structurer des traitements batch et streaming sur les mêmes jeux de données ;
- gouverner le catalogue, le lignage, la qualité, la confidentialité et la rétention ;
- diagnostiquer les coûts, les lectures excessives, les conflits de commit et les jeux de données orphelins ;
- définir une stratégie de sauvegarde, de restauration, de rejeu et de validation après incident.

Ce cours suppose de maîtriser SQL, les bases du traitement distribué, Spark, Kafka et les principes ETL/ELT. Il s'adresse à un niveau expert : nous examinons autant les contraintes d'exploitation que les modèles. Les exemples sont illustratifs et les syntaxes exactes dépendent du format de table, du moteur, du catalogue et de leurs versions.

## 2. Data Lake, entrepôt et Lakehouse : séparer les responsabilités

### 2.1 Data Lake

Le Data Lake conserve des objets dans un stockage adapté aux gros volumes : fichiers de données, journaux, exports, images, modèles ou archives. Le schéma peut être imposé à l'écriture, au moment de la transformation ou lorsqu'un moteur lit les données. Cette flexibilité facilite l'ingestion de sources hétérogènes, mais n'est utile que si l'organisation sait identifier les données, comprendre leurs schémas et gérer leurs droits.

La notion de « données brutes » ne doit pas être interprétée comme une autorisation de stocker n'importe quoi sans contrôle. L'ingestion doit encore appliquer les exigences de sécurité, la minimisation, les limites de taille, l'authentification et la validation structurelle. Certaines données sensibles doivent être exclues ou transformées avant d'atteindre la zone de stockage commune.

### 2.2 Data Warehouse

Un Data Warehouse propose un modèle analytique intégré, avec des définitions de faits, dimensions, mesures et indicateurs. Il est généralement optimisé pour les requêtes analytiques et l'usage partagé par des analystes. Un Lakehouse peut héberger des modèles de type entrepôt, mais les deux termes ne sont pas interchangeables : le premier insiste sur les capacités de données en lac avec gestion de tables, tandis que le second décrit une plateforme intégrée de données analytiques.

### 2.3 Lakehouse

Le Lakehouse combine une couche de stockage, des fichiers analytiques et un format de table qui gère l'état logique de la table. Le format de table maintient les métadonnées qui indiquent quels fichiers constituent un snapshot cohérent, plutôt que de considérer simplement « tous les fichiers présents sous ce chemin » comme la table.

~~~mermaid
flowchart TD
    A["Sources : bases, API, Kafka, fichiers"] --> B["Stockage objet"]
    B --> C["Zone brute : données reçues"]
    C --> D["Zone préparée : qualité et standardisation"]
    D --> E["Tables Lakehouse avec métadonnées"]
    E --> F["Spark / SQL / BI / ML"]
    E --> G["Catalogage et gouvernance"]
    G --> H["Permissions, lignage et qualité"]
~~~

Le schéma représente des responsabilités logiques. Dans une implémentation, la zone brute et les tables gouvernées peuvent utiliser des buckets distincts, des préfixes, des catalogues séparés ou des politiques de sécurité différentes. L'existence d'une couche Lakehouse ne signifie pas que toutes les données doivent passer par une seule table transactionnelle.

## 3. Stockage objet : architecture et contraintes

### 3.1 Objet, clé et métadonnées

Un stockage objet expose des objets identifiés par des clés dans des buckets ou conteneurs. Un objet est généralement composé d'un contenu et de métadonnées. Il ne possède pas exactement le comportement d'un disque POSIX : la sémantique des opérations, les latences, la gestion des versions et les garanties de cohérence dépendent du service. Les moteurs analytiques interagissent avec ces objets via des connecteurs et des APIs de stockage.

Les préfixes peuvent organiser les objets par domaine et date, mais ne doivent pas devenir un labyrinthe de répertoires reflétant tous les champs métier. Une bonne organisation facilite la séparation des responsabilités et les politiques d'accès. La structure logique d'une table transactionnelle est, elle, définie par les métadonnées du format de table et le catalogue, pas uniquement par la convention de nommage des fichiers.

### 3.2 Pourquoi le stockage est séparé du calcul

Avec le stockage et le calcul séparés, plusieurs moteurs peuvent partager des données. On peut augmenter les ressources de Spark pour une transformation lourde puis les réduire, tout en conservant les fichiers. Cela améliore la flexibilité et peut maîtriser les coûts, mais exige des politiques d'accès, de concurrence et de nettoyage des fichiers.

Une lecture analytique peut être limitée par le stockage réseau, le débit des requêtes objet, le nombre de fichiers, la compression ou le calcul des métadonnées. Un stockage peu coûteux n'assure donc pas à lui seul des performances acceptables. Mesurez le temps passé à découvrir les fichiers, les données transférées, les lectures inutiles et les opérations de commit.

### 3.3 Écritures concurrentes et opérations atomiques

Ne supposez pas qu'une écriture objet équivaut à une transaction sur un ensemble de fichiers. Écrire dix nouveaux fichiers puis échouer avant d'enregistrer leur métadonnée peut laisser des objets inutilisés. Remplacer plusieurs objets séparément peut exposer un mélange d'anciennes et de nouvelles données aux lecteurs. Les formats de table ajoutent des métadonnées et un protocole de commit afin de présenter une vue logique cohérente, selon leur modèle de concurrence et le catalogue utilisé.

Dans le Lakehouse, la question est donc moins « le fichier existe-t-il ? » que « est-il référencé par le snapshot publié de la table ? ». Les processus ne doivent jamais identifier les lignes d'une table en listant arbitrairement tous les fichiers qui semblent correspondre au format. Utilisez le moteur et le catalogue compatibles pour effectuer les lectures et écritures.

## 4. Zones du Lake : atterrissage, brut, préparé et publié

Les noms Bronze, Silver et Gold sont des conventions répandues, pas une norme universelle. Il faut définir les responsabilités et les règles d'accès de chaque zone plutôt que s'en tenir aux couleurs.

- **Atterrissage** : reçoit un fichier ou événement et les métadonnées de son arrivée. Il faut savoir identifier le lot, la source et le résultat de validation.
- **Bronze / brut** : conserve une représentation de la donnée reçue, dans les limites de sécurité et de conservation autorisées, pour audit ou rejeu.
- **Silver / préparé** : standardise types, identifiants, horodatages, doublons et contrôles de qualité.
- **Gold / publié** : expose des tables ou vues métier stables, adaptées aux indicateurs, analyses et consommateurs officiels.

~~~mermaid
flowchart LR
    A["Ingestion"] --> B["Atterrissage"]
    B --> C["Bronze : brut gouverné"]
    C --> D["Silver : validé et harmonisé"]
    D --> E["Gold : modèles métier"]
    D --> Q["Quarantaine avec motifs"]
    Q --> R["Correction puis rejeu"]
    R --> D
~~~

La donnée peut être refusée à n'importe quelle étape. Une erreur de format, une absence d'identifiant ou un montant impossible doit être mesuré et expliqué. La quarantaine nécessite un propriétaire, une politique de rétention et un processus de correction. Une zone brute ne doit pas devenir une excuse pour conserver indéfiniment tout payload contenant des secrets ou des données personnelles.

### 4.1 Conservation de la provenance

Chaque ingestion devrait préserver un identifiant de source, l'heure de réception, le nom de fichier ou le topic/partition/offset pertinent, la version de schéma, l'identifiant de lot et, si nécessaire, une empreinte permettant de détecter un fichier répété. Pour les transformations, enregistrez la version du code ou du modèle, la période source, les métriques et l'état du lot.

La provenance est essentielle pour répondre à des questions opérationnelles : pourquoi un chiffre a-t-il changé ? Quel fichier a introduit cette valeur ? Quel lot a été rejeté ? Peut-on recalculer la période ? Sans provenance, l'équipe ne peut souvent que supprimer et recharger au hasard, avec un risque de doublon et un coût opérationnel élevé.

### 4.2 Publication des données

L'écriture d'une table préparée et la décision de la rendre visible aux consommateurs doivent être distinguées. Un pipeline peut charger une table de travail, contrôler sa structure, ses volumes, ses clés et ses mesures, puis publier un snapshot ou une nouvelle version. Si les contrôles échouent, la version précédente doit rester disponible ou le dataset doit être explicitement marqué indisponible, selon le contrat métier.

L'heure de publication et l'heure de dernière donnée doivent être affichées ou exposées aux consommateurs. Un modèle publié à 06 h avec les événements reçus jusqu'à 03 h ne doit pas être présenté comme intégrant les données de 05 h. La fraîcheur fait partie de la qualité d'un produit de données.

## 5. Formats de données et schéma

### 5.1 CSV et JSON

CSV est portable et inspectable, mais il faut définir les séparateurs, l'encodage, les guillemets, les valeurs nulles, les formats de date, le séparateur décimal et les types. Une colonne qui contient des identifiants avec des zéros initiaux peut être corrompue si elle est interprétée comme un nombre. Une date locale sans fuseau horaire peut être interprétée différemment par les systèmes.

JSON gère les structures imbriquées et est pratique pour les événements, mais les noms de champs répétés et le parsing peuvent représenter un coût. Une collection de fichiers JSON peut également contenir des variantes de schéma. Le format ne remplace pas le contrat de données ni la validation.

### 5.2 Avro, Parquet et ORC

Avro est un format binaire orienté lignes qui utilise un schéma et convient souvent aux échanges d'enregistrements et aux événements. Parquet et ORC sont des formats colonne conçus pour les analyses : un moteur peut souvent lire uniquement les colonnes demandées, compresser les valeurs de manière efficace et utiliser des statistiques pour ignorer des blocs qui ne correspondent pas aux filtres.

~~~mermaid
flowchart TD
    A["Forme des données et requêtes"] --> B{"Usage dominant"}
    B --> C["Événements et échanges"]
    B --> D["Analytique colonne"]
    B --> E["Export portable / inspection"]
    C --> F["Avro ou schéma événementiel équivalent"]
    D --> G["Parquet ou ORC"]
    E --> H["CSV ou JSON avec contrat strict"]
    F --> I["Tests de compatibilité"]
    G --> J["Compression, stats, pruning"]
    H --> K["Validation des types et encodages"]
~~~

Le format colonne n'élimine pas le besoin de compaction, de partitionnement ni de validation. Des millions de petits fichiers Parquet peuvent être plus coûteux à lire qu'un nombre raisonnable de fichiers plus grands. Les gains de projection et de compression varient aussi selon la distribution des valeurs et le moteur utilisé.

### 5.3 Schema-on-read et schema-on-write

Le schema-on-read interprète la structure à la lecture ; il offre de la flexibilité, mais reporte une partie de la validation aux consommateurs. Le schema-on-write valide la structure avant publication ou écriture dans la table de destination. Dans les architectures gouvernées, ces approches peuvent coexister : la zone brute conserve le payload autorisé, puis les tables préparées imposent les types et invariants attendus.

Une inférence automatique peut être utile lors de l'exploration, mais risquée pour les pipelines durables. Le même champ peut être déduit comme entier dans un lot puis chaîne dans un autre. Un schéma explicite, un versionnement et des tests de compatibilité rendent le comportement prévisible. Les évolutions incompatibles doivent faire l'objet d'une migration planifiée, et non être tolérées implicitement jusqu'à ce qu'un rapport échoue.

### 5.4 Évolution et validation du schéma

Une nouvelle colonne facultative est parfois compatible ; changer le type d'une colonne, renommer un champ obligatoire ou modifier son sens ne l'est pas nécessairement. Définissez les règles de compatibilité du producteur et du consommateur, la valeur par défaut, la gestion des nulls, les conversions autorisées et la procédure de migration des données déjà stockées.

Un pipeline doit distinguer les champs inconnus, les champs obligatoires manquants, les conversions impossibles et les valeurs hors domaine. Les règles peuvent conduire à rejeter le lot, mettre certaines lignes en quarantaine ou accepter un résultat partiel avec alerte. La politique doit être explicite. La tolérance automatique d'un moteur n'est pas une preuve que la donnée reste sémantiquement correcte.

## 6. Pourquoi les fichiers seuls ne suffisent pas

Un dossier contenant des fichiers Parquet n'offre pas automatiquement les fonctions attendues d'une table analytique transactionnelle. Il n'existe pas nécessairement de snapshot atomique commun à tous les fichiers, de version connue de l'état publié, de mécanisme de conflit entre writers ni de contrat d'upsert. Si un job remplace des fichiers tandis qu'un autre les lit, la vue obtenue dépend du moteur de stockage et des opérations employées.

Un format de table Lakehouse conserve des métadonnées qui décrivent l'ensemble logique des fichiers actifs et l'historique des versions publiées. Il peut fournir des commits optimistes, snapshots, évolution de schéma et opérations de maintenance. Les capacités ne sont pas identiques entre produits, moteurs et versions ; vérifiez chaque garantie dans la documentation technique et effectuez un test de concurrence sur l'environnement cible.

~~~mermaid
flowchart TD
    A["Fichiers Parquet isolés"] --> B["Listing manuel du dossier"]
    B --> C["Risque de lecture d'un état partiel"]
    D["Format de table"] --> E["Catalogue et métadonnées"]
    E --> F["Snapshot publié"]
    F --> G["Ensemble cohérent de fichiers actifs"]
    G --> H["Lecture / écriture par moteur compatible"]
~~~

La couche de table n'est pas un remplacement du stockage sous-jacent. Les données restent dans des fichiers, et les métadonnées définissent comment ils sont interprétés comme une table. Si l'on supprime manuellement des fichiers actifs, la table peut devenir illisible ; si l'on conserve indéfiniment les fichiers orphelins, les coûts augmentent. La maintenance doit être exécutée via les mécanismes du format, pas par une suppression arbitraire de préfixes.

## 7. Les formats de tables Lakehouse

### 7.1 Apache Iceberg

Apache Iceberg définit un format de table analytique ouvert avec métadonnées et snapshots. La table conserve des métadonnées versionnées qui décrivent l'état publié, les fichiers de données et les statistiques utiles. Les snapshots permettent de représenter des états cohérents au fil des commits. Iceberg a des mécanismes pour faire évoluer le schéma et la disposition de partitionnement sans obliger nécessairement les consommateurs à connaître les chemins de tous les fichiers.

Les capacités et opérations exactes dépendent du moteur, du catalogue et de la version : Spark, Trino, Flink ou d'autres moteurs peuvent proposer des prises en charge différentes. Vérifiez les opérations de lecture, écriture, merge, time travel, maintenance et sécurité avant de supposer qu'elles se comportent de façon identique entre connecteurs. L'ouverture du format ne rend pas tous les environnements d'exécution interchangeables.

### 7.2 Delta Lake

Delta Lake ajoute une couche transactionnelle au-dessus de fichiers de données grâce à un journal de transaction et aux métadonnées de la table. Il permet des opérations de mutation et de gestion de snapshots selon les fonctions et versions prises en charge. Les opérations telles que MERGE, l'évolution de schéma, le time travel ou certaines optimisations dépendent de la configuration et de la plateforme utilisées ; vérifiez la matrice de compatibilité plutôt que de supposer qu'un SQL fonctionne de manière identique partout.

### 7.3 Apache Hudi

Apache Hudi est un format de table et une couche de gestion des données qui met l'accent sur l'ingestion incrémentale, l'upsert, le suivi des changements et des modes d'écriture conçus pour certains profils batch et streaming. Ses tables peuvent utiliser des stratégies de stockage distinctes et les compromis entre opérations de lecture et d'écriture diffèrent selon le mode et les réglages. Comme les autres formats, son fonctionnement dépend de la version, du moteur et du déploiement.

### 7.4 Comparer par les besoins

| Question d'architecture | Ce qu'il faut vérifier |
|---|---|
| Plusieurs moteurs doivent-ils lire et écrire ? | Compatibilité des connecteurs, catalogue, fonctions et versions |
| Les mises à jour de lignes sont-elles fréquentes ? | Upsert/MERGE, indexation des fichiers, coût de maintenance |
| Les données arrivent-elles en flux continu ? | Support streaming, commits, checkpoints et latence |
| Faut-il retrouver un état passé ? | Snapshots, time travel, rétention des métadonnées et des fichiers |
| La table change-t-elle souvent de schéma ? | Règles de compatibilité et migration |
| Le stockage objet est-il partagé entre régions ? | Cohérence, catalogue, sécurité, latence et reprise |
| Les coûts de lecture sont-ils dominants ? | Pruning, statistiques, compaction et formats de fichiers |
| Plusieurs writers peuvent-ils écrire simultanément ? | Isolation des commits, conflits, retries et limites du catalogue |

Il n'existe pas de gagnant universel. Si le besoin principal est de publier de grands datasets append-only lus par Spark, un format analytique avec une stratégie simple peut suffire. Si les mises à jour incrémentales, le time travel et l'accès de plusieurs moteurs sont essentiels, un format de table géré devient plus important. Le choix doit s'appuyer sur une matrice d'exigences et un test représentatif de l'application.

## 8. Snapshots, commits et concurrence

### 8.1 Commit atomique au niveau logique

Un commit de table ne consiste pas nécessairement à modifier en place tous les fichiers de données. Le moteur écrit de nouveaux fichiers, construit les métadonnées de la prochaine version et publie un nouveau snapshot selon le protocole du format et du catalogue. Les lecteurs peuvent alors continuer à utiliser un snapshot cohérent tandis que les nouvelles lectures choisissent l'état publié le plus récent.

~~~mermaid
sequenceDiagram
    participant W as Writer
    participant S as Stockage objet
    participant C as Catalogue / métadonnées
    participant R as Reader
    W->>S: Écrire nouveaux fichiers
    W->>C: Préparer métadonnées du snapshot
    W->>C: Tenter publication du commit
    alt Commit accepté
        C-->>W: Nouveau snapshot publié
        R->>C: Lire le snapshot courant
        C-->>R: Référence snapshot cohérent
        R->>S: Lire les fichiers référencés
    else Conflit de commit
        C-->>W: Conflit / commit refusé
        W->>W: Recalculer ou réessayer selon le cas
    end
~~~

Ce diagramme illustre une logique générale, non le protocole exact d'un produit. Un conflit ne doit pas être ignoré ou résolu en écrasant aveuglément le snapshot publié par un autre writer. Il faut comprendre quelles données ont changé, si les opérations peuvent être rejouées et si la transformation reste correcte après relecture du nouvel état.

### 8.2 Concurrence optimiste

De nombreux formats et catalogues s'appuient sur des mécanismes de concurrence optimiste : un writer prépare ses changements et vérifie qu'il peut publier un nouveau snapshot sans écraser un état incompatible. Si un autre writer a commité dans l'intervalle, le premier peut devoir relire les métadonnées, recalculer ses changements ou signaler un conflit. Les opérations append-only et les mises à jour ciblées ne présentent pas nécessairement le même risque.

Une application doit distinguer un conflit de commit temporaire d'une incompatibilité métier. Un retry aveugle peut réappliquer des ajouts en double, écraser un changement récent ou créer un résultat différent sans le signaler. Rendez les opérations idempotentes, définissez les clés d'identité et vérifiez les garanties du mécanisme de commit.

### 8.3 Time travel et snapshots historiques

Le time travel permet de lire une version antérieure de la table lorsqu'elle est conservée par le format, la configuration et le catalogue. C'est utile pour déboguer un changement, comparer un rapport avant/après ou restaurer un snapshot après une erreur logique. Mais un snapshot ancien n'est pas nécessairement conservé indéfiniment : la rétention des snapshots et le nettoyage des fichiers anciens peuvent rendre une version historique inaccessible.

Le time travel n'est pas une sauvegarde hors site. Si le stockage est supprimé, si les métadonnées sont corrompues ou si le compte d'exploitation peut supprimer toutes les versions, les mécanismes de versionnage peuvent disparaître avec la table. Les besoins de restauration après perte du compte, du bucket ou de la région demandent des copies et un plan de reprise distincts.

## 9. Upsert, MERGE et ingestion incrémentale

Un Lakehouse doit souvent intégrer des changements : mise à jour d'un profil, correction d'un paiement, suppression d'un enregistrement ou arrivée d'un événement tardif. L'append-only suffit pour des journaux immuables, mais une table de dimension ou un état courant peut nécessiter un upsert. La syntaxe et les garanties de MERGE varient selon le moteur et le format de table.

Exemple conceptuel de logique de MERGE SQL, à adapter au moteur choisi :

~~~sql
MERGE INTO gold.learner_progress AS target
USING staging.learner_progress_changes AS source
ON target.event_id = source.event_id
WHEN MATCHED THEN UPDATE SET
    target.progress_percent = source.progress_percent,
    target.updated_at = source.updated_at
WHEN NOT MATCHED THEN INSERT (
    event_id, learner_id, course_id, progress_percent, updated_at
) VALUES (
    source.event_id, source.learner_id, source.course_id,
    source.progress_percent, source.updated_at
);
~~~

L'exemple utilise event_id comme clé, mais la bonne clé dépend de la sémantique de la table. Si chaque progression est un événement immuable, il est préférable d'empiler les événements avec un identifiant unique. Si la table représente l'état courant, la clé peut être l'apprenant et le cours, avec une règle qui ne laisse pas un événement plus ancien écraser une progression plus récente. La sémantique doit précéder l'instruction SQL.

Il faut également dédupliquer la source du MERGE. Si deux lignes de staging correspondent à la même clé cible, le résultat peut être ambigu ou refusé par le moteur. Le pipeline doit ordonner ou agréger les changements selon une règle déterministe, par exemple la version source, l'horodatage métier et une clé d'événement. Les timestamps seuls peuvent ne pas suffire en cas d'égalité ou d'horloge incohérente.

### 9.1 Suppressions et tombstones

Les suppressions nécessitent un contrat explicite : suppression physique, suppression logique, marqueur de tombstone ou événement de retrait. Une table courante peut effacer une ligne lors d'un traitement, tandis qu'un dataset d'audit peut conserver l'événement de suppression. Les formats de table ne déterminent pas à eux seuls la politique de conservation métier.

Pour respecter une suppression, il faut examiner les copies dans toutes les couches, les agrégats, les snapshots, les métadonnées et les sauvegardes selon les obligations applicables. La suppression de la ligne dans le snapshot courant ne signifie pas que son contenu a disparu immédiatement de tous les fichiers physiques. La maintenance peut retirer les fichiers devenus inutiles plus tard, sous réserve des règles de rétention et de concurrence.

## 10. Partitionnement, pruning et petits fichiers

### 10.1 Partitionnement adapté aux filtres

Les tables de grande taille sont souvent partitionnées par une colonne de temps ou de domaine. Le partition pruning évite de lire des partitions qui ne peuvent pas répondre à une requête. Un partitionnement pertinent est choisi à partir du workload, des volumes et de la fréquence des opérations de maintenance. Il ne faut pas partitionner par défaut sur des identifiants très nombreux, qui peuvent créer un excès de partitions et de petits fichiers.

Exemple conceptuel de layout :

~~~text
silver/events/event_date=2026-10-26/
silver/events/event_date=2026-10-27/
silver/events/event_date=2026-10-28/
gold/enrollment_metrics/event_month=2026-09/
gold/enrollment_metrics/event_month=2026-10/
~~~

Ce layout illustre une organisation plausible, mais les formats de table modernes peuvent gérer le partitionnement au moyen de métadonnées et de transformations plutôt qu'en exposant exactement chaque répertoire comme clé logique. N'ajoutez pas une colonne de partition uniquement parce qu'elle existe dans les données ; vérifiez que les requêtes filtrent effectivement dessus et que sa cardinalité est adaptée.

### 10.2 Les petits fichiers

Les traitements fréquents et hautement parallèles écrivent parfois beaucoup de petits fichiers. Chaque fichier ajoute des coûts d'ouverture, de listing, de métadonnées et de planification. Les tables peuvent alors se dégrader même si le nombre total d'octets reste modéré. Une stratégie de compaction rassemble des fichiers en unités de taille mieux adaptée, mais son coût de calcul et le volume de données réécrites doivent être pris en compte.

Le seuil de taille cible dépend du moteur, du format, du stockage, du type de requête et du nombre de lecteurs. Il ne faut pas appliquer un chiffre arbitraire sans mesurer. Une compaction trop fréquente peut provoquer un coût d'écriture et des conflits ; une compaction trop rare laisse les petites lectures se multiplier. Les tâches de maintenance doivent avoir une fenêtre, un budget et des métriques.

### 10.3 Nettoyage des fichiers orphelins

Un fichier peut être écrit dans le stockage sans être référencé par un snapshot publié, par exemple après l'échec d'un commit. Les fichiers orphelins consomment de l'espace, mais les supprimer sans respecter le protocole du format peut détruire une donnée encore utilisée. Utilisez les commandes de maintenance prévues par le format ou le moteur, avec des délais qui tiennent compte des writers en cours et des snapshots anciens.

Les opérations de nettoyage doivent être planifiées, observées et testées en présence d'écritures concurrentes. Évitez un job générique qui supprime tout objet plus ancien qu'une date sans comprendre les métadonnées de la table. La sécurité du nettoyage fait partie de la cohérence du Lakehouse.

## 11. Catalogue, métadonnées et interopérabilité

Le catalogue donne un nom stable aux datasets, décrit leurs schémas et connecte les moteurs aux métadonnées de table. Il peut aussi centraliser des permissions, des propriétaires et des commentaires selon la plateforme. Le catalogue ne doit pas être considéré comme une simple liste d'objets : il participe à la découverte, à l'accès et à la manière dont une table est interprétée par différents moteurs.

Des moteurs différents ne prennent pas nécessairement en charge toutes les capacités d'un format de la même manière. Une lecture peut fonctionner alors que les upserts, changements de schéma, time travel ou transactions concurrentes ne sont pas supportés dans cette version de connecteur. Une architecture multi-moteur doit définir une matrice officielle de compatibilité et tester la lecture et l'écriture par chaque moteur autorisé.

Les tables ne doivent pas être créées en parallèle avec des métadonnées indépendantes pointant vers le même dossier, à moins que la méthode de partage soit précisément prise en charge par les outils. Plusieurs catalogues qui ne coordonnent pas la publication peuvent exposer des états incohérents. Standardisez le chemin de création des tables, le catalogue, les propriétaires et la procédure de changement.

### 11.1 Découverte et contrat de données

Une entrée de catalogue devrait documenter le sens métier, la source, le propriétaire, la fraîcheur, la classification, le grain, la clé de déduplication, les champs sensibles, la politique de rétention et les règles de qualité. Les commentaires de colonnes peuvent expliquer une mesure, mais ils ne remplacent pas un contrat de données versionné et testé.

Le lignage doit permettre de retrouver les sources d'une table publiée et, idéalement, les versions de code, les lots et les transformations impliqués. Les métadonnées peuvent être collectées automatiquement ou enregistrées par l'orchestrateur. Dans les deux cas, il faut traiter les changements de noms, les tables renommées, les migrations et les suppressions afin de ne pas laisser des références obsolètes.

## 12. Batch et streaming sur les mêmes tables

Le Lakehouse peut réunir des traitements périodiques et des ingestions à faible latence. Cela ne signifie pas que tous les workloads doivent écrire dans la même table simultanément. Les écritures concurrentes doivent respecter le protocole du format, le catalogue et le modèle de commit. Si un job batch réécrit une partition pendant qu'un flux réalise des upserts, le risque de conflit et de résultat imprévu doit être étudié.

~~~mermaid
flowchart LR
    K["Kafka / CDC"] --> S["Stream processor"]
    F["Fichiers / exports batch"] --> B["Batch processor"]
    S --> R["Zone d'atterrissage"]
    B --> R
    R --> V["Validation et déduplication"]
    V --> T["Table Lakehouse"]
    T --> M["Datamart / SQL / ML"]
    V --> Q["Quarantaine"]
~~~

Un choix robuste peut consister à écrire le flux dans une table d'événements append-only puis à construire une table d'état courant avec des tâches séparées. Cela simplifie parfois la conservation de l'historique et permet le rejeu. Il faut néanmoins surveiller le délai du traitement d'état et définir le comportement en cas d'événement tardif ou dupliqué.

Si le batch et le streaming emploient des règles métier différentes, leurs tables vont diverger même si elles sont stockées dans le même format. Partagez les définitions sémantiques, les contrats et les tests, puis utilisez une réconciliation périodique pour vérifier que les agrégats correspondent à la source attendue.

### 12.1 Idempotence et livraison

L'idempotence reste importante dans un Lakehouse. Un flux peut rejouer des offsets, un fichier peut arriver deux fois, un job peut échouer après l'écriture et avant le checkpoint, ou le catalogue peut refuser un commit déjà préparé. Les clés d'événement, les identifiants de lot, les contraintes de destination et les opérations de merge doivent être conçus ensemble pour éviter les doubles effets.

Ne supposez pas que le format de table rend automatiquement exactement une fois l'ensemble du pipeline. Le format peut assurer un commit cohérent d'une table, tandis que la source, l'orchestrateur et la destination externe peuvent avoir des garanties distinctes. Définissez la frontière transactionnelle et prouver comment la reprise fonctionne.

## 13. Qualité des données, tests et publication

La qualité doit être mesurée avant qu'une table Gold devienne visible. Les tests peuvent contrôler le schéma, la présence des champs obligatoires, l'unicité des clés, les références, les plages de valeurs, les volumes, les totaux et la fraîcheur. Des règles telles que « progression entre 0 et 100 » sont faciles à exprimer, alors que « revenu net » dépend d'une définition métier des remboursements, devises et taxes.

~~~sql
SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT event_id) AS unique_events,
    SUM(CASE WHEN learner_id IS NULL THEN 1 ELSE 0 END) AS missing_learner,
    SUM(CASE WHEN progress_percent < 0 OR progress_percent > 100 THEN 1 ELSE 0 END) AS invalid_progress
FROM silver.progress_events;
~~~

Cette requête illustre des contrôles possibles. La sémantique des champs, la gestion de la valeur nulle et la définition de l'événement unique doivent être établies avec les propriétaires du domaine. Un taux de rejet non nul n'est pas nécessairement critique, mais il doit être visible, justifié et soumis à un seuil.

### 13.1 Quarantaine et reprise

La quarantaine conserve les enregistrements rejetés avec leur origine et le motif. Les données doivent pouvoir être corrigées et rejouées sans créer de doublons. Définissez un délai de résolution et un propriétaire. Les événements qui contiennent des données sensibles doivent être masqués ou conservés avec des droits plus restreints que la table publiée.

Un lot doit être marqué « publié » après les contrôles et le commit réussi. Si le traitement échoue entre le chargement physique et la publication, les consommateurs doivent continuer d'utiliser le snapshot valide précédent ou voir une erreur explicite selon le contrat. Ne laissez pas une zone en cours de reconstruction se confondre avec une table publiée.

### 13.2 Réconciliation des résultats

Comparez les volumes sources, les volumes chargés, les lignes rejetées et les doublons retirés. Pour les mesures importantes, comparez les agrégats par période, catégories et statuts, plutôt qu'un seul total. Un total identique peut cacher une perte et un doublon qui se compensent. La réconciliation doit aussi inclure les valeurs manquantes, les dates tardives et les modifications de dimensions.

Les tests de publication doivent contrôler que le schéma exposé correspond à la version approuvée, que le snapshot est disponible pour les moteurs autorisés et que les consommateurs lisent la bonne version. Après une maintenance ou une migration de format, répétez les tests de lecture, les upserts requis et la procédure de time travel.

## 14. Sécurité, confidentialité et cycle de vie

Un Lakehouse est souvent un point d'agrégation de données venant de plusieurs domaines ; il peut donc concentrer les risques de confidentialité. Les permissions doivent s'appliquer au stockage, au catalogue, aux tables et aux outils. Un analyste autorisé à voir une table Gold n'a pas automatiquement besoin d'accéder aux objets bruts, aux fichiers rejetés ou aux snapshots qui conservent des données personnelles historiques.

La minimisation doit intervenir dès la conception : n'ingérez que les données nécessaires à une finalité reconnue, retirez ou transformez les attributs inutiles et documentez les champs sensibles. La pseudonymisation peut permettre certains rapprochements mais ne garantit pas l'anonymat. Les identifiants de corrélation, les clés de partition et les logs peuvent aussi permettre une réidentification s'ils sont mal conçus.

Le chiffrement au repos et en transit, la gestion des clés, les identités de service et l'audit des accès doivent être intégrés au cycle de vie. Protégez les credentials des moteurs et les comptes qui peuvent supprimer le stockage ou les métadonnées. Les logs, fichiers temporaires et quarantaines sont des zones de données à part entière ; ils doivent avoir les mêmes précautions que les tables si les payloads sont sensibles.

La politique de rétention doit préciser les durées par couche et par catégorie. Les données brutes peuvent être conservées assez longtemps pour l'audit ou le rejeu, mais pas nécessairement aussi longtemps que des agrégats anonymisés. Les suppressions réglementaires peuvent concerner les tables actuelles, snapshots, fichiers obsolètes, exports et sauvegardes selon la politique applicable. La capacité à retirer une donnée doit être conçue et testée, pas supposée à partir d'un DELETE SQL seul.

## 15. Sauvegarde, restauration et reprise après sinistre

Le versionnage d'une table et son time travel facilitent les corrections logiques, mais une restauration après perte de stockage, suppression du bucket ou compromission des comptes requiert des copies indépendantes. Le plan de sauvegarde doit inclure les données, les métadonnées de table, le catalogue, les schémas, les configurations, les secrets via leur système dédié et les dépendances nécessaires à la lecture.

Une stratégie peut combiner snapshots cohérents des tables, copie des fichiers nécessaires, protection du catalogue et rétention hors du domaine de panne. Elle doit préciser comment retrouver la liste des tables, reconstruire les métadonnées, rétablir les accès et valider les relations entre snapshots et fichiers. Une sauvegarde qui copie les fichiers visibles pendant une écriture concurrente sans protocole peut être incomplète.

~~~mermaid
flowchart TD
    A["Incident : table indisponible"] --> B["Geler les écritures ou isoler le périmètre"]
    B --> C["Identifier snapshot et métadonnées sains"]
    C --> D{"Données et catalogue disponibles ?"}
    D -->|Oui| E["Restaurer / pointer vers snapshot validé"]
    D -->|Non| F["Restaurer copie indépendante et métadonnées"]
    E --> G["Vérifier schéma, fichiers, droits et compteurs"]
    F --> G
    G --> H["Réconcilier avec sources"]
    H --> I["Publier et surveiller"]
~~~

Le runbook doit distinguer une erreur logique d'une panne physique. Une erreur logique peut permettre de revenir à un snapshot précédent, tandis qu'une perte de données ou de métadonnées peut imposer une restauration depuis une copie indépendante. Dans les deux cas, identifiez les consommateurs, la fenêtre de données concernée, les commits en cours et les effets qui doivent être rejoués.

Mesurez le RPO et le RTO en pratique. Le RPO indique la perte maximale de données admissible, et le RTO le délai cible de rétablissement du service. Ils doivent refléter le type de table : une table de cache reconstructible a un objectif différent d'une table financière servant d'audit. Un exercice de restauration périodique doit vérifier la cohérence, le temps de reprise et la capacité des utilisateurs à accéder de nouveau aux données.

## 16. Performance, coûts et exploitation

Séparer stockage et calcul ne supprime pas les coûts : il les rend parfois plus visibles. Les coûts comprennent la capacité objet, les requêtes de stockage, les transferts réseau, les ressources de calcul, les snapshots historiques, les petits fichiers, la compaction, les extractions répétées et la rétention. Plusieurs moteurs lisant les mêmes données peuvent économiser une duplication, mais une mauvaise organisation peut conduire chaque requête à scanner des téraoctets.

Mesurez les bytes lus, la durée d'énumération des fichiers, la sélectivité des filtres, les partitions prunées, la taille moyenne des fichiers, le volume de shuffle, le nombre de snapshots et la fréquence de maintenance. Comparez les résultats à la charge métier et à la fraîcheur attendue. Une optimisation de coût qui rend les données indisponibles au mauvais moment n'est pas un succès.

### 16.1 Maintenance régulière

Les opérations de maintenance peuvent inclure compactage, purge des snapshots anciens, nettoyage de fichiers orphelins, mise à jour des statistiques et réorganisation du layout selon les fonctions disponibles. Il faut définir les seuils de déclenchement, le budget, les fenêtres, les dépendances et l'impact sur les writers. Un job de maintenance doit être relançable et supervisé comme tout autre pipeline.

### 16.2 Coût de la relecture

Une relecture de tout l'historique peut être nécessaire après une erreur de transformation ou une évolution de schéma. Le coût peut être important, surtout si l'historique est massif ou stocké dans une classe de stockage plus lente. Maintenez des métriques de provenance et des modèles déterministes pour pouvoir recalculer la période ou la partition concernée lorsque les règles métier le permettent.

Un rejeu partiel exige de connaître les dépendances : si la table Gold dépend de plusieurs tables Silver, recalculer une seule partition de Gold peut être incorrect si une dimension ou une source connexe a changé. Les métadonnées de lot, les snapshots de référence et les versions de code permettent d'établir un périmètre de reprise précis.

## 17. Atelier pratique : une table Lakehouse pour les progressions

Cet atelier est illustratif et doit être exécuté dans un environnement isolé avec le moteur et le format de table effectivement installés. Les exemples SQL s'approchent d'un dialecte analytique, mais la syntaxe de création, de merge et de time travel varie selon Iceberg, Delta Lake, Hudi et le moteur utilisé.

### Étape A — Définir le contrat

La table de progression courante est identifiée par le couple learner_id, course_id. Elle contient progress_percent, source_updated_at et ingestion_batch. Le contrat précise que la progression est comprise entre 0 et 100 et que la version source la plus récente prévaut. Si l'on veut conserver toutes les transitions, une table append-only d'événements distincte est nécessaire.

~~~sql
CREATE TABLE silver.learner_progress (
    learner_id VARCHAR,
    course_id VARCHAR,
    progress_percent INTEGER,
    source_updated_at TIMESTAMP,
    ingestion_batch VARCHAR
);
~~~

L'exemple de DDL est générique ; la commande correcte pour une table Lakehouse doit préciser le format, le catalogue, l'emplacement ou les options appropriées à la plateforme. Ne créez pas cette table en pointant deux catalogues indépendants sur le même chemin sans vérifier leur support de concurrence.

### Étape B — Valider les changements

Avant d'appliquer les mises à jour, dédupliquez la zone staging selon la clé métier et la version source. Un enregistrement sans identifiant ou avec une progression hors domaine doit être mis en quarantaine. La politique de résolution de la dernière version doit être déterministe lorsque plusieurs événements ont un même timestamp.

~~~sql
SELECT *
FROM staging.learner_progress_changes
WHERE learner_id IS NULL
   OR course_id IS NULL
   OR progress_percent < 0
   OR progress_percent > 100;
~~~

Cette requête ne vérifie que quelques règles. Il faut également vérifier les timestamps, les duplications, les identifiants inconnus, les valeurs nulles et la compatibilité du schéma. Le pipeline doit enregistrer les volumes rejetés et faire échouer la publication si les seuils critiques sont dépassés.

### Étape C — Appliquer un upsert

~~~sql
MERGE INTO silver.learner_progress AS target
USING staging.latest_progress_changes AS source
ON target.learner_id = source.learner_id
AND target.course_id = source.course_id
WHEN MATCHED THEN UPDATE SET
    progress_percent = source.progress_percent,
    source_updated_at = source.source_updated_at,
    ingestion_batch = source.ingestion_batch
WHEN NOT MATCHED THEN INSERT (
    learner_id, course_id, progress_percent, source_updated_at, ingestion_batch
) VALUES (
    source.learner_id, source.course_id, source.progress_percent,
    source.source_updated_at, source.ingestion_batch
);
~~~

La table latest_progress_changes doit contenir au maximum une ligne par couple apprenant-cours. Le merge n'est correct que si la source a déjà été dédupliquée selon une règle déterministe et que le moteur/format prend en charge l'opération avec les garanties souhaitées. Il faut tester le comportement lors de commits concurrents et de retries.

Pour gérer les événements tardifs, ne laissez pas une version plus ancienne écraser une version plus récente. Une condition sur les versions ou timestamps peut être nécessaire, avec une politique définie quand les horloges sont incohérentes. Si la vérité métier dépend d'une séquence source plutôt que d'un timestamp, utilisez cette séquence.

### Étape D — Contrôler puis publier

Après le merge, vérifiez l'unicité du couple clé, la plage des valeurs, la fraîcheur maximale de source et le nombre de lignes modifiées. Comparez les totaux avant/après et confirmez que le snapshot publié est celui validé. Si une anomalie critique est détectée, gardez la version précédente disponible et consignez le lot en échec.

Un test sérieux inclut un doublon d'entrée, une source sans changement, une mise à jour tardive, une panne pendant le commit, deux writers concurrents et une restauration d'un snapshot précédent. Ces tests montrent si le contrat tient au-delà du chemin nominal.

## 18. Douze exercices corrigés

### Exercice 1 — Différencier Data Lake et Lakehouse

Pourquoi le simple fait d'enregistrer des fichiers Parquet dans un bucket ne garantit-il pas les fonctionnalités d'un Lakehouse ?

**Correction :** Les fichiers seuls ne définissent pas nécessairement un snapshot cohérent, un protocole de commit, un historique des versions, une gestion des conflits ou des opérations d'upsert. Une couche de format de table conserve des métadonnées et des règles qui décrivent l'état logique de la table.

### Exercice 2 — Choisir la zone

Une source envoie un fichier avec des champs inattendus et des valeurs invalides. Que doit faire le pipeline avant publication ?

**Correction :** Le pipeline doit valider la structure, préserver la provenance autorisée, identifier les erreurs et isoler les lignes rejetées avec un motif. Les données ne doivent pas être publiées comme une table Silver/Gold fiable avant les contrôles. La politique de conservation du fichier brut doit respecter la sécurité et la rétention.

### Exercice 3 — Format de fichier

Une requête analytique lit seulement trois colonnes d'un dataset très large. Pourquoi Parquet ou ORC peut-il être utile ?

**Correction :** Les formats colonne permettent au moteur de ne lire que les colonnes nécessaires et de bénéficier de compression et statistiques selon le moteur. Le gain dépend du layout, des filtres, du nombre de fichiers et de la prise en charge effective.

### Exercice 4 — Schema-on-read

Que risque une architecture qui utilise uniquement l'inférence automatique de schéma sur chaque lot JSON ?

**Correction :** Un champ peut être inféré avec des types différents selon les valeurs présentes dans chaque lot. Cette variation rend les transformations non déterministes et peut provoquer des erreurs ou des conversions silencieuses. Un schéma explicite et versionné, des règles de compatibilité et des tests rendent le contrat stable.

### Exercice 5 — Choisir un format de table

L'application doit réaliser des upserts fréquents et lire un historique de snapshots. Quels critères faut-il examiner avant de choisir Iceberg, Delta Lake ou Hudi ?

**Correction :** Examinez les garanties de commit et de concurrence, les opérations de merge, le time travel, la prise en charge des moteurs et du catalogue, les capacités streaming, la maintenance, les migrations et le coût. Le choix doit être vérifié sur les versions exactes et un workload représentatif, pas sur une comparaison marketing générique.

### Exercice 6 — Conflit de commit

Deux writers mettent à jour la même table. Le deuxième reçoit un conflit de commit. Pourquoi ne doit-il pas simplement ignorer l'erreur ?

**Correction :** Un autre writer a pu modifier l'état depuis que le deuxième a préparé son snapshot. Ignorer le conflit peut perdre des changements ou produire une vue incohérente. Le système doit relire les métadonnées, évaluer si l'opération est rejouable et utiliser une stratégie de retry ou de résolution adaptée au format.

### Exercice 7 — Petits fichiers

Un pipeline écrit des milliers de petits fichiers à chaque minute. Quel problème cela peut-il provoquer et quelle solution examiner ?

**Correction :** Le nombre de fichiers augmente les coûts d'ouverture, de listing et de planification et peut dégrader les scans. Il faut mesurer la distribution des tailles, réviser le parallélisme d'écriture, regrouper les données et planifier une compaction avec des seuils basés sur l'usage.

### Exercice 8 — Partitionnement

Une table est partitionnée par user_id, qui possède des centaines de millions de valeurs. Pourquoi cela peut-il être un mauvais choix ?

**Correction :** Le partitionnement à très forte cardinalité peut créer trop de partitions et de petits fichiers, et augmenter le coût de métadonnées. Le partitionnement doit être choisi à partir des filtres analytiques, du volume par valeur, des opérations de maintenance et des capacités du format.

### Exercice 9 — Compaction et historique

Pourquoi la compaction physique ne doit-elle pas être confondue avec la suppression historique d'une table ?

**Correction :** La compaction réécrit les fichiers selon le protocole de la table pour améliorer le layout, tandis que le retrait d'anciens snapshots ou des fichiers obsolètes répond à une autre politique. Une maintenance incorrecte peut détruire des fichiers encore référencés par une version active ou nécessaire au time travel.

### Exercice 10 — Upsert idempotent

Un job échoue après avoir écrit la table et avant de confirmer le succès à l'orchestrateur. Que doit garantir la relance ?

**Correction :** Le rejeu ne doit pas créer de doublons ni appliquer deux fois les mêmes changements. Il faut une clé stable, une déduplication déterministe, un identifiant de lot et une opération idempotente ou un protocole de publication qui permette de vérifier si le commit a déjà réussi.

### Exercice 11 — Time travel et sauvegarde

Pourquoi un snapshot antérieur ne suffit-il pas pour répondre à une perte complète du bucket ?

**Correction :** Le snapshot dépend des métadonnées et des fichiers de données conservés dans le stockage. Si le bucket ou ses identifiants de gestion disparaissent, les versions historiques peuvent être perdues avec les données. Une sauvegarde indépendante, incluant métadonnées et procédure de restauration, reste nécessaire.

### Exercice 12 — Gouvernance multi-moteur

Spark lit une table Iceberg, mais un autre moteur ne supporte pas une opération de merge ou une évolution de schéma. Que faut-il faire avant de partager la table officiellement ?

**Correction :** Construire et maintenir une matrice de compatibilité par moteur et version, tester les opérations requises, fixer un catalogue commun et documenter les limites de lecture/écriture. L'ouverture du format ne garantit pas que chaque connecteur supporte chaque fonctionnalité.

## 19. Défi final corrigé : Lakehouse pour SkillMarket

### Énoncé

SkillMarket reçoit des événements Kafka, des exports transactionnels et des fichiers de partenaires. Il faut préserver la provenance, produire des tables analytiques utilisées par Spark et un moteur SQL, corriger les événements en retard, tenir un historique de versions, limiter l'accès aux données personnelles et restaurer le service après une erreur de publication.

### Correction proposée

**Architecture.** Utiliser une zone d'atterrissage pour recevoir les fichiers et événements avec identifiants de lot, timestamps et métadonnées de source. Conserver une zone brute gouvernée pour permettre le rejeu dans les limites de la politique de données. Transformer ensuite les données dans une zone préparée avec validation de schéma, normalisation des types, déduplication et quarantaine. Les tables publiées exposent des modèles métier et un contrat de fraîcheur.

**Format.** Choisir le format de fichier selon le type de données : un format événementiel schématisé pour l'échange, Parquet ou ORC pour l'analytique colonne. Utiliser un format de table tel qu'Iceberg, Delta Lake ou Hudi selon le besoin d'interopérabilité, de merge, de streaming, de snapshots et de compatibilité des moteurs. Tester la version et le catalogue réellement utilisés.

**Clés et idempotence.** Définir une identité stable des événements et des lots. Dédupliquer les changements avant merge et choisir si chaque table représente un journal d'événements ou l'état courant. Un événement tardif ne doit pas écraser arbitrairement une version plus récente. Les opérations de retry doivent être idempotentes ou vérifiables après un commit dont la réponse a été perdue.

**Concurrence.** Désigner les producteurs de chaque table et les règles de commit. Un job de maintenance ne doit pas supprimer les fichiers nécessaires à un writer ou à un snapshot actif. Les conflits de commit sont suivis, analysés et réessayés seulement lorsque la logique peut être recalculée sans effet double. Le catalogue ne doit pas être contourné par une écriture de fichiers manuelle dans le dossier d'une table.

**Qualité.** Avant publication, contrôler schéma, clés, références, plages de valeurs, duplications, volumes, fraîcheur et réconciliation avec les sources. Les anomalies ont un seuil et une décision explicites : bloquer, mettre en quarantaine ou publier avec avertissement si le métier l'autorise. La table publiée expose la version et l'heure de dernière donnée.

**Sécurité.** Séparer les droits sur les données brutes et les tables publiées. Employer des identités de service, des permissions minimales, le chiffrement adapté et un catalogue gouverné. Les champs personnels inutiles sont retirés ou transformés dès une étape autorisée. Les journaux, snapshots et quarantaines sont couverts par une politique de conservation.

**Performance.** Mesurer bytes lus, pruning, tailles de fichiers, petits fichiers, shuffle, temps de compaction, nombre de snapshots et coûts des requêtes. Choisir les partitions en fonction des filtres fréquents et de la cardinalité. Les opérations de maintenance ont des seuils, une fenêtre et un budget. Les grands recalculs sont planifiés avec une capacité suffisante pour les reprises.

**Reprise.** Garder des copies indépendantes du domaine de panne, protéger le catalogue et documenter les dépendances. Lors d'une erreur logique, identifier le snapshot correct et comparer les résultats avant publication. Lors d'une perte de stockage, restaurer les fichiers et les métadonnées depuis une copie fiable. Vérifier les droits, les schémas, les volumes, les références et les agrégats avant de rouvrir les consommateurs.

**Tests.** Simuler des doublons, des événements tardifs, deux writers concurrents, un échec de commit, un nettoyage de fichiers, une évolution de schéma, une disparition de catalogue et une restauration. Valider la cohérence finale, l'absence de doublons, la traçabilité et le temps de reprise. Une architecture n'est approuvée que lorsque ces tests sont reproductibles.

## 20. Checklist de révision

- [ ] Je distingue Data Lake, Data Warehouse et Lakehouse.
- [ ] Je sais définir les responsabilités des zones brute, préparée et publiée.
- [ ] Je conserve la provenance, le schéma, le lot et les erreurs.
- [ ] Je choisis le format de fichier en fonction du workload.
- [ ] Je sais expliquer pourquoi un dossier Parquet n'est pas automatiquement une table transactionnelle.
- [ ] Je comprends le rôle du catalogue, des métadonnées et du snapshot courant.
- [ ] Je compare les formats de table par les garanties, moteurs, opérations et coût.
- [ ] Je maîtrise l'impact des commits concurrents, upserts, replays et petits fichiers.
- [ ] Je définis une stratégie de partitionnement et de compaction mesurable.
- [ ] Je publie uniquement après les contrôles de qualité et de réconciliation.
- [ ] Je protège données brutes, snapshots, logs, quarantaine et sauvegardes.
- [ ] Je distingue time travel et sauvegarde indépendante.
- [ ] Je peux démontrer une restauration et un rejeu sans doublons.

## 21. Documentation officielle

Les fonctions exactes varient selon les versions, les moteurs et les catalogues. Vérifiez la matrice de compatibilité et les limites documentées avant de concevoir une dépendance de production.

- Apache Iceberg, documentation : https://iceberg.apache.org/docs/latest/
- Apache Iceberg, évolution de schéma : https://iceberg.apache.org/docs/latest/evolution/
- Apache Iceberg, maintenance et procédures : https://iceberg.apache.org/docs/latest/maintenance/
- Delta Lake, documentation : https://docs.delta.io/latest/
- Delta Lake, concurrency control : https://docs.delta.io/latest/concurrency-control.html
- Delta Lake, schema evolution : https://docs.delta.io/latest/delta-batch.html#schema-validation
- Apache Hudi, documentation : https://hudi.apache.org/docs/overview/
- Apache Hudi, concepts de tables : https://hudi.apache.org/docs/table_types/
- Apache Parquet, documentation : https://parquet.apache.org/docs/
- Apache ORC, documentation : https://orc.apache.org/docs/
- Apache Spark SQL, guide de programmation : https://spark.apache.org/docs/latest/sql-programming-guide.html

La maîtrise experte du Lakehouse repose sur des garanties explicites plutôt que sur une simple accumulation de fichiers. Le format, le catalogue, le moteur, les clés métier, la gouvernance et les procédures d'exploitation doivent former un contrat cohérent. Une table utile est une table dont le contenu est explicable, le changement contrôlé, la lecture reproductible et la restauration démontrable.
