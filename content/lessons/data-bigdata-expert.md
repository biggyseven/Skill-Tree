
# Architecture Hadoop et Spark — Expert

## Mise en contexte : quand une machine ne suffit plus

Une plateforme numérique peut générer des milliards d'événements : consultations de cours, paiements, journaux applicatifs, traces réseau, événements de sécurité et données de télémétrie. Une base relationnelle bien conçue peut traiter une part importante de ces données, mais certaines charges analytiques deviennent trop volumineuses, trop parallèles ou trop coûteuses pour être exécutées sur un seul serveur. L'architecture distribuée répartit alors stockage et calcul sur un ensemble de machines, tout en acceptant de nouveaux problèmes : pannes partielles, transfert réseau, déséquilibre entre tâches, réplication, cohérence des métadonnées, reprise et gouvernance.

Hadoop et Apache Spark sont deux projets historiques majeurs de l'écosystème Big Data. Hadoop apporte notamment HDFS pour le stockage distribué, YARN pour l'allocation de ressources et l'architecture MapReduce pour certains traitements batch. Spark fournit un moteur de calcul distribué polyvalent qui permet d'exprimer des transformations batch, SQL, streaming et apprentissage machine avec plusieurs API. Spark peut lire des fichiers sur HDFS, sur un stockage objet compatible ou depuis d'autres systèmes ; son adoption ne signifie donc pas que chaque déploiement doit utiliser HDFS ou YARN.

Le but de ce cours n'est pas de mémoriser une liste de composants. Il s'agit d'être capable de concevoir un pipeline, d'estimer les risques, de lire les symptômes d'un mauvais plan d'exécution et de justifier une architecture à partir des contraintes métier. Nous utiliserons un scénario fictif : SkillMarket traite des journaux d'activité et des événements de formation pour calculer des indicateurs à grande échelle, repérer des anomalies et produire des datasets gouvernés pour les analystes.

## 1. Objectifs et prérequis

À la fin de ce cours, vous devrez pouvoir :

- expliquer l'architecture Hadoop et le rôle respectif de HDFS, YARN et MapReduce ;
- distinguer stockage distribué, calcul distribué, ordonnanceur et moteur analytique ;
- choisir entre fichiers structurés, formats colonne et stockage objet selon les besoins ;
- décrire l'exécution d'une application Spark, de l'interface de soumission aux exécuteurs ;
- raisonner sur transformations, actions, DAG, partitions, shuffle et cache ;
- écrire des exemples de transformation Spark SQL et DataFrame avec une gestion correcte des types ;
- expliquer la tolérance aux pannes par lineage, recomputation, checkpoints et réplication ;
- diagnostiquer skew, petites tâches, grosses partitions, pression mémoire et shuffle coûteux ;
- définir des règles de qualité, d'idempotence, de schéma et de publication des données ;
- comparer batch, Structured Streaming et les notions de livraison exactement une fois ;
- prévoir observabilité, sécurité, contrôles d'accès, gestion des secrets et coûts ;
- proposer un runbook opérationnel et des tests de charge et de reprise.

Le cours suppose de connaître SQL, les structures de données, les principes d'ETL/ELT, les partitions de tables et les commandes de base d'un système Unix. Une première expérience avec Python ou Scala est utile. Les exemples utilisent principalement PySpark, mais les concepts s'appliquent aussi aux API Scala et SQL de Spark. Les commandes de production doivent être ajustées à la version, au cluster et au gestionnaire de ressources effectivement déployés.

## 2. Les problèmes que le calcul distribué résout — et ceux qu'il introduit

Le traitement distribué vise à répartir les données et le travail entre plusieurs nœuds. Cela augmente potentiellement la capacité totale et permet de traiter des volumes supérieurs à la mémoire ou au disque d'une seule machine. Mais cette capacité n'est pas gratuite : les données doivent être lues, déplacées, sérialisées, réparties puis parfois recombinées. Un job distribué peut être plus lent qu'un traitement local si son volume est petit, si ses tâches sont trop nombreuses ou si la plupart du travail se résume à des transferts réseau.

Un bon design distingue quatre facteurs : volume stocké, quantité de données lue, quantité de calcul effectuée et coût des échanges entre nœuds. La bonne architecture minimise le travail inutile, puis alloue suffisamment de ressources au travail utile. Ajouter des exécuteurs ne corrige pas toujours un mauvais algorithme ou un shuffle disproportionné.

~~~mermaid
flowchart TD
    A["Charge analytique"] --> B["Volume de données"]
    A --> C["Complexité du calcul"]
    A --> D["Mouvement des données"]
    B --> E["Stockage distribué"]
    C --> F["Calcul distribué"]
    D --> G["Partitionnement et réseau"]
    E --> H["Mesure globale"]
    F --> H
    G --> H
~~~

La distribution introduit aussi les pannes partielles : un nœud peut disparaître alors que les autres continuent. Un disque peut être saturé, un exécuteur peut manquer de mémoire, une tâche peut être beaucoup plus lente que les autres ou un service de métadonnées peut devenir indisponible. Les composants doivent savoir détecter les échecs, reprendre une tâche et éviter de publier un résultat incomplet.

L'expert ne promet donc jamais simplement « plus de machines, donc plus rapide ». Il définit le workload, le niveau de service, les contraintes de reprise, la qualité attendue, le coût maximal et les mesures qui prouveront que l'architecture tient ses objectifs.

## 3. Hadoop : stockage, ressources et calcul

### 3.1 HDFS, un système de fichiers distribué

HDFS, Hadoop Distributed File System, stocke de gros fichiers répartis en blocs entre des DataNodes. Le NameNode gère les métadonnées du système de fichiers : namespace, associations entre fichiers et blocs, emplacements connus et informations nécessaires à la gestion du stockage. Les DataNodes stockent les blocs et communiquent leur état. La donnée est généralement répliquée selon une politique configurée, afin de tolérer certaines défaillances de nœuds ou de disques.

~~~mermaid
flowchart TD
    C["Client HDFS"] --> N["NameNode : métadonnées"]
    C --> D1["DataNode A"]
    C --> D2["DataNode B"]
    C --> D3["DataNode C"]
    D1 --- B1["Bloc / réplique"]
    D2 --- B1
    D3 --- B2["Autre bloc / réplique"]
    N -. "emplacements des blocs" .-> C
~~~

Le client demande les emplacements des blocs au NameNode, puis lit ou écrit les données auprès des DataNodes. Le NameNode n'est donc pas un proxy de toutes les données du fichier. Cette séparation est importante pour comprendre les flux réseau et les risques de métadonnées.

HDFS est conçu pour de gros fichiers et des lectures de débit élevé, notamment en batch. Il n'est pas l'équivalent d'un système de fichiers local à faible latence, d'une base de données OLTP ou d'un stockage objet universel. Un très grand nombre de petits fichiers peut consommer une quantité disproportionnée de métadonnées et mettre le NameNode sous pression. La taille des fichiers, la stratégie de compactage et le format de stockage font partie de la conception.

La réplication protège contre certaines pannes physiques mais n'est pas une sauvegarde complète. Une suppression logique, une corruption par application ou une erreur de transformation peut toucher toutes les copies. Les politiques de sauvegarde, les snapshots et les tests de restauration doivent être conçus séparément selon les possibilités de la distribution et du stockage utilisé.

### 3.2 NameNode, haute disponibilité et exploitation

Le NameNode est un composant critique du namespace. Les distributions Hadoop modernes peuvent proposer des configurations de haute disponibilité avec plusieurs NameNodes et un mécanisme de coordination, ainsi que des mécanismes de contrôle des métadonnées et des journaux partagés. Les détails de déploiement dépendent de la distribution et de la version. Un plan de production doit préciser le quorum ou le mécanisme de coordination, la procédure de bascule, l'observabilité et les opérations de maintenance.

Une architecture haute disponibilité ne doit pas être évaluée uniquement par le nombre de processus actifs. Testez la bascule, la récupération après redémarrage, la cohérence des métadonnées, la saturation du stockage local et la procédure de retour à l'état nominal. Une instance standby qui n'a jamais été testée ne constitue pas une preuve de reprise.

Les DataNodes envoient des signaux de vie et des rapports de blocs. Le système peut détecter des répliques manquantes ou des nœuds devenus injoignables et planifier une réplication supplémentaire. Surveillez la capacité utilisée, l'espace restant par volume, la santé des disques, le nombre de blocs sous-répliqués, les erreurs de lecture et le débit des opérations. La capacité moyenne du cluster ne suffit pas : un seul disque plein ou un groupe déséquilibré peut provoquer des incidents.

### 3.3 YARN : allocation des ressources

YARN sépare l'allocation des ressources du moteur qui effectue réellement le traitement. Le ResourceManager coordonne l'allocation à l'échelle du cluster, les NodeManagers gèrent les ressources et conteneurs sur les nœuds, et chaque application dispose d'un ApplicationMaster qui coordonne son exécution selon le framework. Cette séparation permet à plusieurs moteurs compatibles de partager le cluster.

~~~mermaid
flowchart TD
    U["Utilisateur / client"] --> RM["ResourceManager"]
    RM --> Q["Ordonnanceur de ressources"]
    RM --> NM1["NodeManager A"]
    RM --> NM2["NodeManager B"]
    U --> AM["ApplicationMaster"]
    AM --> NM1
    AM --> NM2
    NM1 --> C1["Conteneur de tâche"]
    NM2 --> C2["Conteneur de tâche"]
~~~

Le diagramme est conceptuel : les détails précis du lancement dépendent du mode de soumission, du framework et de la version. Il faut distinguer conteneur, processus d'exécuteur Spark, tâche Spark et partition logique. Ces objets peuvent être liés mais ne sont pas synonymes.

La gestion des ressources doit concilier plusieurs besoins : isolation entre équipes, fair sharing ou priorités, capacité réservée, limites de mémoire, quotas et comportement d'une application qui attend des ressources. Un cluster peut sembler sous-utilisé alors qu'une queue est saturée par sa politique d'allocation. Inversement, une application qui demande trop de cœurs et de mémoire peut empêcher d'autres traitements de démarrer.

Pour les opérations, documentez les capacités, les queues, les limites par application, les identités de service, les logs et le mécanisme de terminaison. Une application abandonnée qui conserve des ressources ou une file d'attente mal dimensionnée peut dégrader la plateforme entière.

### 3.4 MapReduce : modèle batch historique

MapReduce décrit des traitements en deux phases principales. La fonction Map transforme des enregistrements en paires clé-valeur intermédiaires. La phase de shuffle et sort regroupe les données par clé. La fonction Reduce combine les valeurs associées à chaque clé afin de produire un résultat.

~~~mermaid
flowchart LR
    A["Fichiers d'entrée"] --> B["Map par partition"]
    B --> C["Paires clé-valeur"]
    C --> D["Shuffle / sort par clé"]
    D --> E["Reduce par clé"]
    E --> F["Résultat distribué"]
~~~

Pour compter les occurrences de mots, Map produit par exemple une paire mot/1 pour chaque occurrence, puis Reduce additionne les valeurs de chaque mot. Le modèle peut tolérer les pannes de tâches via des relances et tire parti du stockage distribué. Mais certaines étapes exigent des écritures intermédiaires et la matérialisation de résultats, ce qui peut devenir coûteux pour des pipelines composés de nombreuses transformations.

Spark propose un moteur plus général qui peut conserver des résultats en mémoire ou sur disque et optimiser un graphe d'opérations. Cela ne rend pas Spark systématiquement supérieur : le choix dépend des APIs, du cluster, de la tâche, des garanties et des contraintes historiques. MapReduce reste utile pour comprendre les fondamentaux du shuffle et de la distribution, même lorsqu'une application utilise surtout Spark SQL.

## 4. Stockage analytique et formats de fichiers

### 4.1 Choisir entre texte, JSON, Avro, Parquet et ORC

Le format de stockage influence le volume transféré, le coût de décodage, les capacités d'évolution du schéma et les optimisations du moteur. CSV est simple à inspecter mais représente les types de façon limitée et nécessite des règles d'échappement, de séparateur, d'encodage et de nulls très explicites. JSON gère mieux les structures imbriquées mais peut répéter les noms de champs et avoir un coût de parsing important. Avro est un format binaire orienté lignes, doté d'un schéma et souvent utile pour les échanges et événements. Parquet et ORC sont des formats colonne courants pour l'analytique.

Les formats colonne permettent de lire les colonnes nécessaires plutôt que toutes les valeurs de chaque ligne et offrent des stratégies de compression adaptées aux données. Ils peuvent aussi permettre des statistiques et du pruning au niveau des fichiers ou groupes de lignes, si le moteur les utilise. Le bénéfice dépend du type de données, de la sélectivité, de l'ordre des données et des capacités de l'outil.

~~~mermaid
flowchart TD
    A["Usage principal"] --> B{"Profil"}
    B -->|"Échange d'événements"| C["Avro ou format événementiel schématisé"]
    B -->|"Exploration simple / export"| D["CSV ou JSON sous contrat"]
    B -->|"Analytique colonne"| E["Parquet ou ORC"]
    C --> F["Versionner le schéma"]
    D --> G["Valider encodage et types"]
    E --> H["Compacter et partitionner"]
~~~

Aucun format ne répare un schéma incohérent. Si la même colonne est parfois une chaîne, parfois un entier et parfois une structure imbriquée, il faut gérer explicitement l'évolution du schéma. Si les fichiers sont trop petits, même un format colonne optimisé peut subir le coût d'une ouverture de fichier, de la planification et des métadonnées.

### 4.2 Compression et coût total

La compression réduit généralement les octets stockés et transférés mais consomme du CPU pour compresser et décompresser. Le bon codec dépend de la vitesse d'accès, du taux de compression, de la compatibilité et des fonctions de découpage des blocs. Évaluez les performances de bout en bout : un fichier plus petit ne garantit pas à lui seul un job plus rapide si la décompression devient le goulot d'étranglement.

Il faut également prendre en compte la lisibilité opérationnelle et la possibilité de récupérer une partie d'un fichier. Des formats compressés en continu peuvent limiter la lecture parallèle ou l'accès aléatoire selon le codec. Les choix doivent être testés sur un échantillon réaliste, pas décidés à partir d'une caractéristique isolée.

### 4.3 Partitionner les données

Une structure de répertoires par date ou par domaine peut réduire les données à examiner pour les requêtes qui filtrent sur ces colonnes. Le partitionnement doit être fondé sur les requêtes et la distribution réelle des données. Partitionner par un identifiant très cardinal crée souvent trop de répertoires, augmente le nombre de petits fichiers et rend l'exploitation complexe. À l'inverse, une unique partition très large peut empêcher une lecture sélective ou compliquer la rétention.

~~~text
warehouse/
  events/
    event_date=2026-10-26/
    event_date=2026-10-27/
    event_date=2026-10-28/
  enrollments/
    event_month=2026-09/
    event_month=2026-10/
~~~

Cette arborescence n'est qu'un exemple conceptuel. Le format exact et la convention de partitionnement dépendent des métadonnées et du moteur. Avec un stockage objet, évitez de supposer que renommer ou déplacer un très grand nombre de fichiers est aussi peu coûteux qu'une opération de métadonnées locale. Un mécanisme de publication de versions, un catalogue de tables ou un format transactionnel peut être requis lorsque plusieurs producteurs écrivent simultanément.

## 5. Spark : architecture d'exécution

### 5.1 Driver, cluster manager, exécuteurs et tâches

Une application Spark comprend un Driver qui construit le plan, coordonne l'application et ordonnance les tâches, ainsi que des Executors qui effectuent les calculs. Le Cluster Manager alloue les ressources. Il peut s'agir de YARN, Kubernetes, du mode standalone Spark ou d'un autre environnement compatible. Le choix du gestionnaire n'est pas l'essence de Spark : il contrôle la manière dont les ressources sont attribuées et les processus lancés.

~~~mermaid
flowchart TD
    S["spark-submit"] --> M["Gestionnaire de cluster"]
    M --> D["Driver"]
    D --> P["Plan logique et DAG"]
    D --> E1["Executor A"]
    D --> E2["Executor B"]
    E1 --> T1["Tâches sur partitions"]
    E2 --> T2["Tâches sur partitions"]
    E1 --> O["Résultats / écritures"]
    E2 --> O
~~~

Le Driver peut fonctionner sur la machine cliente ou dans le cluster selon le mode de déploiement. Si le Driver disparaît, l'application Spark standard ne continue pas nécessairement simplement parce que les exécuteurs existent. Le placement, les ressources et les règles de redémarrage doivent être adaptés à la criticité du job.

Une action sur le DataFrame déclenche l'exécution nécessaire du plan. Les transformations sont souvent paresseuses : Spark construit un graphe d'opérations plutôt que d'exécuter immédiatement chaque ligne de code. Il peut optimiser ce graphe, choisir une stratégie de jointure et planifier les échanges entre partitions.

### 5.2 RDD, DataFrame et Dataset

Les RDD représentent des collections distribuées résistantes aux pannes et permettent des transformations de plus bas niveau. Les DataFrames expriment des données structurées avec des colonnes et des types, ce qui permet au moteur d'optimiser le plan grâce aux informations de schéma. Dans PySpark, DataFrame est l'API structurée principale. Dataset typé existe particulièrement dans l'écosystème Scala/Java, mais n'a pas la même place dans toutes les APIs.

Pour la plupart des traitements analytiques structurés, commencez par DataFrame ou Spark SQL. Utilisez des RDD lorsque le niveau de contrôle ou la nature des données le justifie. Passer trop tôt à des fonctions arbitraires Python peut empêcher certaines optimisations et introduire des coûts de sérialisation.

### 5.3 Transformations et actions

Les transformations créent de nouveaux objets logiques : sélection, filtre, projection, regroupement, jointure et enrichissement. Les actions exigent un résultat ou déclenchent une matérialisation, par exemple un comptage, une écriture ou une collecte locale. Il est important de distinguer le code qui définit le plan de celui qui force l'exécution.

~~~python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("skillmarket-events-summary")
    .getOrCreate()
)

events = spark.read.parquet("s3a://analytics-lake/events/")
clean = (
    events
    .filter(F.col("event_date") >= F.lit("2026-10-01"))
    .filter(F.col("event_type").isNotNull())
    .select("event_date", "event_type", "learner_id")
)

daily = (
    clean
    .groupBy("event_date", "event_type")
    .agg(F.count("*").alias("event_count"),
         F.countDistinct("learner_id").alias("unique_learners"))
)

daily.write.mode("overwrite").parquet(
    "s3a://analytics-curated/daily-event-summary/"
)
~~~

Le chemin S3 présenté est illustratif et suppose que le connecteur, l'authentification et les permissions sont configurés. Dans une production, un overwrite vers un chemin partagé doit être encadré : la stratégie de publication dépend du format de table, de la façon dont les consommateurs lisent les données et des risques de voir un résultat partiellement reconstruit.

La collecte complète d'un gros DataFrame vers le Driver avec collect peut saturer la mémoire locale. Utilisez des agrégations distribuées, des exports, des écritures partitionnées ou une collecte limitée destinée au diagnostic. Les notebooks ne doivent pas convertir un jeu de données massif en liste locale uniquement pour voir « les premières lignes ».

### 5.4 Spark SQL et schéma explicite

La lecture de données peut inférer le schéma, mais l'inférence est coûteuse et sujette aux variations. Les pipelines importants bénéficient d'un schéma explicite, surtout lorsque les sources évoluent ou que des valeurs manquantes et types mixtes apparaissent. Il faut définir ce qui se passe quand un champ disparaît, est renommé, change de type ou reçoit une nouvelle catégorie.

~~~python
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType, DoubleType
)

event_schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("learner_id", StringType(), True),
    StructField("event_type", StringType(), False),
    StructField("event_time", TimestampType(), False),
    StructField("amount", DoubleType(), True),
])

events = (
    spark.read
    .schema(event_schema)
    .json("s3a://analytics-lake/raw/events/")
)
~~~

Pour des montants financiers, un type flottant binaire est souvent inadapté si l'on exige une arithmétique exacte à l'échelle du centime. Préférez un type décimal de précision adaptée, et définissez la devise, l'arrondi et le traitement des valeurs nulles. Le code utilise DoubleType uniquement comme exemple de type générique à remplacer quand la mesure représente de l'argent.

Les schémas doivent être versionnés. Une évolution compatible peut ajouter un champ facultatif, tandis qu'un changement de type ou de signification métier nécessite une migration et un contrat explicite. Spark peut tolérer certains changements de structure, mais la tolérance technique ne constitue pas un contrat de données valide.

## 6. Partitionnement, parallélisme et shuffle

### 6.1 Ce que représente une partition Spark

Une partition est une unité logique de données distribuée qui devient généralement l'entrée d'une tâche pour une étape donnée. Le nombre de partitions influence le parallélisme, l'overhead de planification, la taille des blocs de travail et la pression mémoire. Trop peu de partitions peuvent sous-utiliser le cluster ; trop de partitions minuscules produisent un grand nombre de tâches courtes et un coût de coordination élevé.

Le partitionnement des fichiers sur le stockage et le partitionnement interne Spark sont liés mais différents. Une table peut être partitionnée par date au niveau du stockage, tandis que Spark redistribue ses lignes selon une clé avant une agrégation. Un fichier n'est pas nécessairement égal à une tâche, car le moteur peut fractionner la lecture, combiner les fichiers ou regrouper le travail selon le format et la configuration.

### 6.2 Narrow transformations et shuffle

Certaines transformations peuvent lire une partition et produire des résultats sans échanges globaux, parfois dites narrow. D'autres, comme une agrégation par clé ou certaines jointures, nécessitent de déplacer les données afin que les valeurs liées se retrouvent ensemble. Cet échange est un shuffle ; il consomme réseau, disque, mémoire et temps de sérialisation.

~~~mermaid
flowchart LR
    A["Partitions initiales"] --> B["Filtre local"]
    B --> C["Shuffle par clé"]
    C --> D1["Partition clé 1"]
    C --> D2["Partition clé 2"]
    C --> D3["Partition clé 3"]
    D1 --> E["Agrégation"]
    D2 --> E
    D3 --> E
~~~

Le shuffle n'est pas à proscrire : un regroupement distribué en a souvent besoin. L'objectif est d'éviter les shuffles inutiles et de gérer leur taille. Filtrer tôt, sélectionner les colonnes nécessaires, choisir une clé de partitionnement pertinente, éviter des jointures trop larges et mesurer le plan peuvent réduire le coût.

### 6.3 Repartition et coalesce

Repartition redistribue les données et implique généralement un shuffle ; elle peut augmenter ou diminuer le nombre de partitions. Coalesce permet souvent de réduire le nombre de partitions avec moins de redistribution, mais peut créer un déséquilibre si la réduction est excessive. Le choix dépend de la suite du pipeline et de la taille réelle des données.

Évitez d'imposer un nombre fixe de partitions sans mesurer le volume et les ressources. Un chiffre convenable pour une journée de données peut être mauvais lors d'une pointe. Les configurations d'exécuteurs et la taille moyenne des tâches doivent être ajustées à partir des métriques, pas simplement copiées d'un autre cluster.

### 6.4 Skew : une clé domine le travail

Le skew apparaît lorsque certaines clés reçoivent beaucoup plus de données ou de travail que les autres. Les tâches ordinaires finissent rapidement, mais une ou deux tâches très lourdes prolongent le job. Ajouter des exécutants ne résout pas toujours le problème : la partition surchargée peut rester assignée à une seule tâche.

Exemples de causes : une valeur null ou inconnue extrêmement fréquente, une clé « global » appliquée à presque tous les événements, un client à très forte activité ou un join où une seule valeur se répète des millions de fois. Les remèdes comprennent le nettoyage et le traitement spécifique des clés anormales, le salting lorsque la logique le permet, la diffusion d'une dimension petite, l'adaptation des partitions et les mécanismes d'optimisation du skew supportés par le moteur.

~~~mermaid
flowchart TD
    A["Job lent"] --> B["Comparer durée et volume par tâche"]
    B --> C{"Quelques tâches extrêmes ?"}
    C -->|Oui| D["Diagnostiquer le skew de clé"]
    C -->|Non| E["Examiner IO, shuffle, mémoire et ressources"]
    D --> F["Pré-agréger, saler ou traiter une clé spéciale"]
    F --> G["Mesurer le plan modifié"]
    E --> G
~~~

Le salting ajoute un suffixe temporaire à une clé pour répartir le calcul, puis effectue une agrégation finale pour réunir les sous-résultats. Il ne convient pas à toutes les opérations et peut créer un second shuffle. Pour une jointure, il faut garder une cohérence entre les clés salées des deux côtés ou répliquer la petite dimension correctement. Une transformation qui « supprime le skew » mais change le résultat métier est évidemment inacceptable.

## 7. Optimiser les jointures et l'agrégation

Une jointure distribuée peut nécessiter un échange massif des deux côtés. Si l'une des tables est suffisamment petite pour être diffusée à chaque exécuteur, une broadcast join peut réduire le shuffle. « Petite » signifie suffisamment petite pour tenir de manière sûre en mémoire sur les exécuteurs avec la marge nécessaire ; une table de référence n'est pas automatiquement petite après avoir ajouté des colonnes ou filtré de façon inadéquate.

~~~python
from pyspark.sql import functions as F
from pyspark.sql.functions import broadcast

events_by_course = (
    events
    .groupBy("course_id")
    .agg(F.count("*").alias("event_count"))
)

course_dim = (
    spark.read.parquet("s3a://analytics-curated/dim_course/")
    .select("course_id", "category", "level")
)

result = events_by_course.join(
    broadcast(course_dim),
    on="course_id",
    how="left"
)
~~~

Le broadcast est ici une suggestion explicite, pas une commande à appliquer à toute dimension. Il faut vérifier la taille en mémoire et le plan physique. Si la dimension est plus grosse que prévu ou si plusieurs jointures font du broadcast, la mémoire des exécuteurs peut être saturée.

Les agrégations partielles peuvent réduire le volume de données avant le shuffle. Par exemple, compter localement par partition puis regrouper les sous-comptes diminue les paires transférées lorsque plusieurs occurrences de la même clé sont dans une partition. Les moteurs structurés appliquent certaines optimisations automatiquement ; examinez le plan avant d'ajouter du code qui les reproduit.

### 7.1 Examiner les plans

Spark propose l'affichage du plan logique et physique via explain. Les plans révèlent filtres, projections, jointures, scans et échanges. Le nom exact des étapes et leurs détails changent avec la version et les configurations. Il faut relier la lecture du plan aux métriques du Spark UI, notamment les bytes lus et écrits en shuffle, la durée des tâches, le spill, les GC et la taille des résultats.

~~~python
result.explain("formatted")
~~~

Ne cherchez pas seulement un mot-clé et ne supposez pas qu'un plan plus court est automatiquement meilleur. Mesurez la latence totale, la variabilité, le coût des ressources et l'exactitude des résultats sur un jeu de test. Un cache peut accélérer plusieurs actions répétées, mais peut aussi consommer la mémoire qui devrait servir au shuffle. Une amélioration sur un seul micro-benchmark peut provoquer une régression sur les autres jobs du cluster.

## 8. Mémoire, persistance et tolérance aux pannes Spark

### 8.1 Lineage et recomputation

Les transformations d'un RDD ou d'un DataFrame construisent une lignée logique, souvent appelée lineage. Si certaines partitions intermédiaires sont perdues, Spark peut parfois recalculer les données depuis leurs dépendances. Cette capacité permet la tolérance aux pannes sans répliquer systématiquement chaque résultat intermédiaire. Elle n'est cependant pas gratuite : recalculer une longue chaîne peut coûter cher, surtout si la source est lente ou si le calcul comporte des étapes lourdes.

### 8.2 Cache et persist

Cache ou persist conserve un résultat intermédiaire pour réutiliser ses partitions lors d'actions ultérieures. Le niveau exact de stockage et de tolérance dépend de l'API, de la version et de la configuration ; les données peuvent résider en mémoire ou sur disque et être recalculées si elles sont perdues. Il faut libérer la persistance après le dernier usage afin de ne pas immobiliser indéfiniment les ressources.

~~~python
prepared = (
    events
    .filter(F.col("event_type").isNotNull())
    .select("event_date", "event_type", "learner_id")
    .persist()
)

# Plusieurs actions réutilisent les partitions préparées.
daily_count = prepared.groupBy("event_date").count()
event_types = prepared.groupBy("event_type").count()

daily_count.write.mode("overwrite").parquet(
    "s3a://analytics-curated/daily-count/"
)
event_types.write.mode("overwrite").parquet(
    "s3a://analytics-curated/type-count/"
)

prepared.unpersist()
~~~

La persistance est utile lorsque le coût de recalcul évité dépasse le coût de stockage et de maintien. Mettre en cache un DataFrame utilisé une seule fois peut perdre du temps et de la mémoire. Il faut également comprendre qu'un cache Spark n'est pas une base de référence durable et ne remplace pas la persistance du dataset final.

### 8.3 Checkpoint

Un checkpoint écrit un résultat afin de couper ou de raccourcir une lignée de calcul, selon l'API et les garanties du mode choisi. Il est notamment utile dans certains traitements itératifs ou streaming avec un état géré. La configuration du répertoire, la sécurité, la rétention et la disponibilité du stockage doivent être explicites. Le checkpoint n'est pas simplement un deuxième nom pour un cache mémoire.

Une reprise fiable doit savoir d'où vient l'état sauvegardé, avec quelle version du code et quel schéma il est compatible, et si la source d'origine est toujours accessible. Lorsqu'un pipeline évolue, la compatibilité de ses checkpoints et métadonnées doit être étudiée avant un déploiement. Une relance depuis un ancien état avec une nouvelle sémantique de calcul peut produire une sortie incohérente.

## 9. Structured Streaming et traitements quasi temps réel

Spark Structured Streaming permet de représenter des traitements de flux avec l'API structurée, en s'appuyant sur un plan de calcul et un modèle de progression des données. Les sources et sinks pris en charge, la gestion de l'état, les checkpoints et les garanties dépendent de la version et du connecteur. Une architecture streaming doit préciser les offsets, la sémantique de livraison et les effets externes ; le nom « streaming » ne prouve pas à lui seul que la latence est faible ou que toutes les écritures sont exactement une fois.

~~~mermaid
flowchart LR
    K["Kafka / source d'événements"] --> S["Spark Structured Streaming"]
    S --> C["Validation et transformations"]
    C --> A["Agrégation avec état"]
    A --> O["Sink / table cible"]
    S --> CP["Checkpoint durable"]
    CP -. "offsets et état" .-> S
~~~

Une source de type Kafka peut attribuer à un événement un topic, une partition et un offset. Spark conserve des informations de progression dans son checkpoint et lit les événements selon les options du connecteur. Mais si l'écriture vers la cible n'est pas transactionnelle ou idempotente, un redémarrage peut produire des doublons ou des résultats partiels. Les garanties de bout en bout sont un contrat combinant source, moteur, sink et logique de transformation.

### 9.1 Fenêtres et événements tardifs

Une fenêtre temporelle regroupe des événements selon leur temps métier, souvent avec une durée fixe ou glissante. Un watermark permet de définir jusqu'où l'application accepte de conserver l'état pour des événements retardés, selon la sémantique du traitement. Quand l'événement arrive plus tard que la limite définie, il peut être ignoré pour certaines agrégations d'état ou traité par une autre voie. Le choix doit être aligné sur le retard réel de la source et les besoins métier.

Un watermark n'est pas une promesse universelle de purge exact à une seconde près et ne remplace pas un plan de gestion des événements tardifs. Testez les temps en désordre, les doublons, les événements sans timestamp, les retards exceptionnels et les redémarrages. Il faut également savoir distinguer event time, processing time et ingestion time.

### 9.2 Exactly-once : définition prudente

L'expression exactly-once est fréquemment employée de façon trop large. Il faut identifier ce qui est garanti : absence de traitement logique en double dans un état interne, reprise des offsets, transaction atomique avec le sink, ou résultat métier idempotent. Si un traitement envoie un e-mail ou appelle une API externe sans clé d'idempotence, le moteur ne peut pas annuler l'effet si le processus plante après l'appel mais avant d'enregistrer sa progression.

Pour les sorties vers une base, utilisez les garanties transactionnelles du sink lorsqu'elles existent ou un motif d'idempotence explicite : identifiant d'événement unique, upsert, clé de déduplication, table de suivi et règles de réconciliation. Évitez de promettre « exactement une fois » sans préciser le périmètre, les limites de la source, du moteur et de la destination.

### 9.3 Batch ou streaming ?

Le batch est simple à rejouer, facile à auditer par lot et souvent économique pour des délais de plusieurs minutes ou heures. Le streaming peut réduire la latence mais nécessite de gérer l'état, l'ordre partiel, le retard, la contre-pression, les checkpoints et la compatibilité des changements. Une architecture lambda ou kappa ne doit pas être adoptée seulement pour sa popularité ; partez du délai et de la valeur métier de l'indicateur.

Si une mesure doit être disponible en quelques minutes et que l'information tardive peut être corrigée par batch, un pipeline mixte peut être pertinent. Il faut alors éviter que le flux et le batch produisent deux définitions différentes du même indicateur. Une source sémantique commune et des mécanismes de réconciliation sont essentiels.

## 10. Petits fichiers, compaction et gouvernance de la table

Les jobs fréquents peuvent créer de nombreux petits fichiers. Les petits fichiers augmentent les coûts d'ouverture, de planification, de listes de stockage et de métadonnées. Une compaction combine des fichiers afin d'obtenir une taille plus équilibrée et de réduire l'overhead des lectures. La taille cible doit cependant être adaptée au moteur, au volume, à la concurrence et à la distribution des données ; il n'existe pas une taille universelle.

Une table partagée par plusieurs pipelines doit avoir un propriétaire, un schéma versionné, une politique de partitionnement, une convention d'évolution et une règle de publication. Les simples fichiers Parquet dans un dossier n'apportent pas automatiquement un catalogue de transactions, des mises à jour atomiques et un historique de versions. Selon la plateforme, un format de table comme Apache Iceberg, Delta Lake ou Apache Hudi peut apporter des fonctionnalités de gestion de table, mais les garanties et les compatibilités doivent être vérifiées pour les versions installées.

La table doit aussi définir comment sont traitées les écritures concurrentes et les corrections. Deux jobs qui écrivent dans le même dossier sans coordination peuvent se remplacer ou exposer un état partiel selon le mode de sortie et le stockage. Une écriture réussie du job ne signifie pas que les consommateurs voient un instantané cohérent si la publication n'est pas atomique.

## 11. Sécurité dans un environnement Big Data

La quantité de données et la distribution des fichiers élargissent la surface d'attaque. L'accès doit être géré au niveau du cluster, du stockage, du catalogue, des chemins de données, des journaux et des outils d'administration. Le fait que les processus s'exécutent sur un réseau privé ne remplace pas l'authentification et les autorisations.

Les principes importants comprennent :
- identité de service propre à chaque workload ;
- droits minimaux sur les chemins et tables utilisés ;
- chiffrement des échanges et des supports quand la plateforme l'exige ;
- stockage des secrets dans un mécanisme adapté plutôt que dans le code ou les arguments visibles ;
- audits des accès et séparation des rôles d'exploitation et d'analyse ;
- minimisation des données personnelles, politique de rétention et procédure de suppression ;
- isolation entre environnements de développement, test et production.

Dans Hadoop, les configurations d'authentification, l'intégration Kerberos, les ACL HDFS et les mécanismes d'autorisation doivent être adaptés à la distribution. Dans Spark, il faut protéger les interfaces, les logs, les fichiers de configuration et les informations d'identification utilisées pour accéder au stockage. Un accès par URL ou chemin de stockage n'est pas en soi un contrôle de sécurité ; les identités d'exécution doivent être validées.

Ne passez pas de secrets dans les arguments des commandes si l'environnement les expose aux listes de processus ou aux journaux. Évitez les accès larges qui permettent à toute l'équipe de lire des données brutes, et testez que les permissions effectives correspondent à la politique. Les données de quarantaine et les fichiers temporaires peuvent être aussi sensibles que les tables finales.

## 12. Observabilité et diagnostic en production

L'observabilité combine des métriques d'infrastructure, des métriques d'application et des métriques de données. Pour Hadoop, observez l'espace disponible, les blocs sous-répliqués, l'état du NameNode, les queues YARN, les tâches en attente, la mémoire et les logs de conteneurs. Pour Spark, observez la durée des stages et tâches, le volume de shuffle, le spill disque, les GC, les erreurs, la distribution des durées, les volumes lus et écrits et les métriques de la source.

Les métriques de données doivent inclure le nombre d'événements lus, acceptés et rejetés, le volume de doublons, les valeurs manquantes, l'heure du dernier événement, le retard des sources, l'état du watermark et la date de publication de la cible. Un job peut avoir un statut réussi tout en ne lisant aucune donnée à cause d'un filtre incorrect. Un contrôle de fraîcheur et un contrôle de volume sont aussi importants que le code retour.

~~~mermaid
flowchart TD
    A["Alerte : durée du job en hausse"] --> B["Vérifier source et volumes"]
    B --> C["Lire Spark UI : stages et tâches"]
    C --> D{"Shuffle ou skew important ?"}
    D -->|Oui| E["Examiner clés, joins et partitions"]
    D -->|Non| F["Examiner IO, mémoire, GC et ressources"]
    E --> G["Hypothèse mesurable"]
    F --> G
    G --> H["Test sur échantillon représentatif"]
    H --> I["Comparer résultat et métriques"]
    I --> J["Déployer avec seuil de retour arrière"]
~~~

### 12.1 Incident : une seule tâche reste très longtemps

Si la plupart des tâches terminent et qu'une ou quelques-unes restent actives, recherchez un déséquilibre de partition ou une clé dominante. Comparez les tailles, les temps et les octets de shuffle. Vérifiez également si la tâche restante attend un accès réseau ou effectue un traitement exceptionnel. Le bon remède peut être un salting, une pré-agrégation, un traitement dédié à une valeur spéciale ou une modification du modèle de partitionnement.

### 12.2 Incident : Out of Memory

Déterminez si la mémoire est consommée par les données de shuffle, une jointure, un broadcast, la sérialisation, les caches ou le code utilisateur. Inspectez les logs des exécuteurs, le spill, les GC et la taille des partitions. Augmenter la mémoire peut traiter un besoin réel, mais peut aussi masquer un skew ou une collecte locale inappropriée. Évaluez les ressources en tenant compte de la mémoire réservée au système et de l'overhead hors tas.

### 12.3 Incident : job réussi, sortie vide

Vérifiez les plages temporelles, le fuseau horaire, les filtres, le format du fichier, le chemin d'entrée et la progression CDC. Comparez les comptages à chaque étape et examinez les quarantaines. Un job avec zéro ligne peut être valide à certains moments ; ce comportement doit être défini. Si une sortie vide est inattendue, un contrôle de volume minimum ou une alerte de fraîcheur peut bloquer la publication.

### 12.4 Incident : doublons après redémarrage

Identifiez si les doublons viennent de la source, d'un retry, d'un sink non idempotent ou d'une publication partielle. Comparez les identifiants d'événement, les offsets, le registre de lots et les clés de sortie. Réparer les doublons après coup peut être nécessaire, mais la prévention passe par un contrat d'idempotence, une déduplication et une écriture cible contrôlée.

## 13. Atelier pratique : traiter des événements de formation

Cet atelier s'exécute dans un environnement de développement où PySpark est installé et où le chemin de données est accessible. Le chemin présenté est fictif et doit être remplacé par un dossier de test. Ne lancez pas une écriture overwrite sur un chemin partagé de production pendant l'expérimentation.

### Étape A — Charger et valider

~~~python
from pyspark.sql import functions as F

raw = spark.read.parquet("file:///tmp/skillmarket/events/")

required = ["event_id", "learner_id", "event_type", "event_time"]
missing_columns = [name for name in required if name not in raw.columns]
if missing_columns:
    raise ValueError(f"Colonnes obligatoires absentes : {missing_columns}")

valid = (
    raw
    .filter(F.col("event_id").isNotNull())
    .filter(F.col("event_type").isNotNull())
    .filter(F.col("event_time").isNotNull())
)

invalid_count = raw.count() - valid.count()
print(f"Lignes exclues par les règles de base : {invalid_count}")
~~~

Sur un volume massif, deux appels count distincts peuvent relire toute la source, à moins que le plan et le cache ne l'évitent. Pour un travail de production, pensez à mesurer les lignes et à écrire une seule fois une zone validée, ou utilisez des métriques de pipeline intégrées. Cette démonstration favorise la compréhension, mais il ne faut pas recopier aveuglément chaque action en production.

La quarantaine doit conserver les raisons de rejet plutôt que seulement un nombre. Dans un véritable pipeline, construisez un DataFrame des lignes invalides avec une colonne de motif, puis écrivez-le dans un emplacement protégé avec un identifiant de lot. Définissez qui peut consulter ce contenu et combien de temps il est conservé.

### Étape B — Dédupliquer

~~~python
from pyspark.sql.window import Window

window_by_event = (
    Window
    .partitionBy("event_id")
    .orderBy(F.col("ingested_at").desc())
)

deduplicated = (
    valid
    .withColumn("row_num", F.row_number().over(window_by_event))
    .filter(F.col("row_num") == 1)
    .drop("row_num")
)
~~~

Cette règle garde l'enregistrement ayant le timestamp d'ingestion le plus récent pour chaque event_id. Elle n'est correcte que si event_id est réellement stable et si le dernier événement est bien la version à retenir. Si deux occurrences sont des événements différents, la clé de déduplication est erronée. Si les dates d'ingestion peuvent manquer ou être identiques, définissez un second critère déterministe.

Une déduplication a une signification métier. Pour les événements financiers, il faut distinguer une répétition technique d'une correction ou d'un remboursement. Un simple dropDuplicates sur les colonnes de la ligne peut garder arbitrairement une version si les lignes diffèrent.

### Étape C — Calculer des métriques quotidiennes

~~~python
daily = (
    deduplicated
    .withColumn("event_date", F.to_date("event_time"))
    .groupBy("event_date", "event_type")
    .agg(
        F.count("*").alias("events"),
        F.countDistinct("learner_id").alias("learners")
    )
)

daily.orderBy("event_date", "event_type").show(50, truncate=False)
~~~

Un affichage limité est approprié au diagnostic. Pour un grand résultat, écrivez les données ou limitez précisément l'ensemble à un échantillon. La fonction countDistinct peut avoir un coût important selon le moteur, les cardinalités et le plan. Avant de choisir une approximation, vérifiez que l'erreur estimée est acceptable pour l'indicateur métier.

### Étape D — Inspecter le plan et publier

~~~python
daily.explain("formatted")

(
    daily
    .write
    .mode("overwrite")
    .parquet("file:///tmp/skillmarket/output/daily-events/")
)
~~~

Dans un environnement réel, utilisez une table ou un mécanisme de publication compatible avec les consommateurs, les accès concurrents et les exigences de reprise. Vérifiez la sortie avec un contrôle de schéma, de volume et de fraîcheur avant d'annoncer la réussite. Une écriture terminée n'est qu'une étape de la validation du résultat.

## 14. Douze exercices corrigés

### Exercice 1 — Différencier Hadoop et Spark

Quel rôle remplit principalement HDFS et quel rôle remplit Spark ?

**Correction :** HDFS fournit un système de fichiers distribué, alors que Spark est un moteur de calcul distribué. Spark peut lire depuis HDFS, mais aussi depuis d'autres sources compatibles. Installer Spark n'impose pas d'utiliser HDFS, et un stockage distribué ne constitue pas à lui seul un moteur de calcul.

### Exercice 2 — HDFS et petits fichiers

Un pipeline crée plusieurs millions de fichiers de quelques kilo-octets. Pourquoi cela peut-il dégrader l'exploitation HDFS ?

**Correction :** Chaque fichier demande des métadonnées et des opérations de gestion. Un nombre extrême de petits fichiers augmente la pression sur le NameNode et l'overhead de lecture et de planification. Une stratégie de compactage, un format de table adapté et une granularité de sortie mieux choisie peuvent réduire ces coûts.

### Exercice 3 — YARN et Spark

Dans une architecture Spark sur YARN, un conteneur YARN et une tâche Spark désignent-ils la même chose ?

**Correction :** Non. YARN alloue des ressources sous forme de conteneurs et coordonne l'exécution des applications. Spark répartit le travail en stages et tâches associés à ses partitions. Plusieurs tâches Spark peuvent s'exécuter dans un même exécuteur, lequel utilise les ressources qui lui ont été attribuées.

### Exercice 4 — Pourquoi le shuffle coûte-t-il cher ?

Une agrégation par clé provoque de nombreux transferts réseau. Que se passe-t-il et comment limiter le coût ?

**Correction :** Les valeurs qui doivent être regroupées par clé sont redistribuées entre les partitions. Ce shuffle consomme réseau, sérialisation, disque et mémoire. Filtrer tôt, réduire les colonnes, pré-agréger, choisir une distribution adaptée et examiner le plan peuvent réduire le volume échangé.

### Exercice 5 — Diagnostic du skew

La plupart des tâches se terminent en une minute, mais une tâche dure vingt minutes. Quelle piste doit être examinée ?

**Correction :** Un déséquilibre de partition ou une clé dominante est probable. Comparez taille, durée et volume de shuffle par tâche et examinez les valeurs de clé extrêmes. Un salting, un traitement spécialisé ou une autre stratégie de jointure peut être utile si les règles métier le permettent.

### Exercice 6 — DataFrame ou RDD

Pourquoi privilégier souvent DataFrame ou Spark SQL pour une transformation tabulaire ?

**Correction :** Ces API structurées exposent les colonnes et les types, ce qui permet au moteur d'optimiser le plan. Les RDD sont utiles pour des besoins bas niveau spécifiques, mais l'utilisation arbitraire de fonctions peut compliquer l'optimisation et ajouter des coûts de sérialisation.

### Exercice 7 — collect sur un grand volume

Un développeur ajoute collect pour convertir le résultat Spark en liste Python sur le Driver. Quel danger existe ?

**Correction :** Toutes les données collectées doivent tenir dans la mémoire du Driver et traverser le réseau. Un volume massif peut provoquer un Out of Memory et faire échouer l'application. Préférez les agrégations distribuées, les sorties partitionnées et les actions d'inspection limitées.

### Exercice 8 — Persist ou cache

Pourquoi ne faut-il pas persister chaque DataFrame automatiquement ?

**Correction :** La persistance consomme mémoire ou disque et peut concurrencer le travail principal. Elle est utile lorsque plusieurs actions réutilisent un résultat coûteux ; un résultat utilisé une seule fois peut être plus efficace sans cache. Il faut libérer les données persistées quand elles ne sont plus nécessaires.

### Exercice 9 — Reprise Structured Streaming

Un job streaming redémarre et relit certains événements. Quelle propriété doit avoir la destination pour éviter les doublons visibles ?

**Correction :** Selon la garantie du connecteur, la destination doit offrir une écriture transactionnelle compatible ou une logique idempotente, par exemple une clé d'événement stable et un upsert. La garantie exactly-once doit être précisée de bout en bout, et non déduite du seul checkpoint Spark.

### Exercice 10 — Pourquoi un watermark ?

Un agrégat streaming conserve un état par fenêtre et reçoit des événements longtemps en retard. Quel est le rôle du watermark ?

**Correction :** Le watermark exprime une limite de retard permettant au moteur de gérer la rétention de l'état et certains événements tardifs. Il doit être choisi selon le retard réel et le contrat métier. Il ne garantit pas que chaque événement très tardif soit inclus automatiquement.

### Exercice 11 — Format colonne

Une requête analytique n'utilise que trois colonnes d'une table très large. Pourquoi Parquet ou ORC peuvent-ils aider ?

**Correction :** Les formats colonne permettent souvent de ne lire que les colonnes nécessaires et de tirer parti de compression et de statistiques. Le gain dépend du format, du moteur, du partitionnement, du filtre et de la disposition des fichiers ; il doit être mesuré.

### Exercice 12 — Succès technique mais données fausses

Un job termine avec succès, mais le rapport quotidien tombe à zéro. Quels contrôles doivent intervenir ?

**Correction :** Vérifier chemins et plages temporelles, filtres, schéma, données lues à chaque étape, rejets, progression de source et volume final. Des contrôles de fraîcheur et de volume attendus doivent empêcher ou signaler la publication d'un résultat vide inattendu. Le code retour seul ne prouve pas la qualité.

## 15. Défi final corrigé : plateforme distribuée de données SkillMarket

### Énoncé

SkillMarket reçoit chaque jour des centaines de gigaoctets de journaux d'activité et de progression, ainsi qu'un flux d'événements de paiement. La plateforme doit publier des statistiques par heure, par cours et par canal, conserver des résultats auditables, accepter des événements tardifs et reprendre un traitement après une panne d'exécuteur. Les données personnelles doivent être protégées, et les utilisateurs BI doivent voir uniquement les données autorisées.

### Correction proposée

**Stockage.** Les fichiers bruts sont écrits dans une zone d'atterrissage avec identifiant de lot ou métadonnées d'événement. Le format est choisi selon le besoin : un format événementiel schématisé pour l'échange, Parquet ou un format colonne équivalent pour les datasets analytiques. Les fichiers sont partitionnés selon les filtres usuels, par exemple la date événement, mais sans créer un répertoire pour chaque identifiant à très forte cardinalité. Une politique de compaction maîtrise les petits fichiers.

**Traitement batch.** Le pipeline Spark lit un schéma explicite, filtre les colonnes utiles, valide les champs requis, normalise les timestamps et déduplique sur une clé métier stable. Les transformations structurées sont privilégiées pour laisser le moteur optimiser les plans. Les agrégations sont distribuées et les clés dominantes sont mesurées avant de décider d'une stratégie de salting ou de pré-agrégation.

**Ingestion streaming.** Pour les événements qui exigent une fraîcheur plus courte, Structured Streaming suit la progression de la source avec un checkpoint durable. L'état temporel emploie un watermark documenté. Les effets sur la destination sont rendus idempotents avec des identifiants stables ou des mécanismes transactionnels adaptés. Les événements trop tardifs sont conservés ou traités par un processus de correction si les règles métier le demandent.

**Publication.** Le job écrit dans une zone versionnée ou une table qui fournit les garanties de cohérence requises. Les consommateurs ne lisent que les lots publiés après validation. Les contrôles vérifient le schéma, le nombre d'événements, les clés, les doublons, la fraîcheur et les écarts métier. Le nom d'un chemin d'output ne suffit pas comme signal de publication.

**Ressources.** Les ressources sont allouées selon des queues ou des quotas. Les limites des exécuteurs tiennent compte de la mémoire JVM, de l'overhead et des conteneurs. Le réglage utilise les métriques de durée des tâches, du shuffle, du spill et de GC. La capacité est évaluée à partir de la charge de pointe et des reprises, pas uniquement sur la moyenne.

**Résilience.** Le pipeline est relançable par lot ou par plage de données. Chaque exécution enregistre son ID, les versions du code et du schéma, les bornes source et les statistiques. Une panne d'exécuteur déclenche le mécanisme de reprise de Spark ; un échec de publication empêche d'annoncer le lot comme disponible. Les réexécutions ne doivent pas créer de doublons.

**Sécurité.** Les rôles de stockage, du catalogue et du cluster appliquent le moindre privilège. Les identifiants sont fournis par un gestionnaire de secrets ou le mécanisme sécurisé de la plateforme. Les attributs personnels non nécessaires sont retirés ou transformés avant d'entrer dans les couches non autorisées. Les logs et quarantaines sont protégés et soumis à rétention.

**Observabilité.** Le tableau de supervision combine l'état des ressources, la durée et les erreurs des jobs, la latence du flux, la progression des offsets, les volumes chargés, les quarantaines, les contrôles de qualité et l'heure de la dernière publication. Une alerte signale non seulement l'échec du job mais aussi une absence de données inattendue ou un retard dépassant l'objectif métier.

**Tests.** Avant le déploiement, testez panne d'exécuteur, saturation mémoire, fichier manquant, doublons source, événement tardif, changement de schéma, destination indisponible et relance après succès partiel. Comparez les résultats avec un échantillon calculé indépendamment. Mesurez les temps de reprise, les volumes et la cohérence finale pour prouver que le système fonctionne sous panne.

## 16. Checklist de révision

- [ ] Je peux expliquer les rôles de HDFS, YARN, MapReduce et Spark.
- [ ] Je sais distinguer bloc HDFS, fichier, partition Spark, tâche, stage, exécuteur et conteneur.
- [ ] Je choisis un format de stockage et un partitionnement à partir des requêtes et volumes.
- [ ] Je comprends le plan logique, le DAG et les échanges de shuffle.
- [ ] Je sais identifier un skew et proposer une correction mesurable.
- [ ] Je limite les collectes locales et la persistance inutile.
- [ ] Je définis les garanties de checkpoint et d'idempotence d'un flux.
- [ ] Je distingue temps d'événement, temps de traitement et watermark.
- [ ] Je protège les données, les secrets, les checkpoints et les quarantaines.
- [ ] Je surveille les métriques du moteur et la qualité des données.
- [ ] Je rends les lots relançables sans doublons et publie seulement après contrôle.
- [ ] Je teste les pannes, le scénario de reprise et le résultat métier final.

## 17. Documentation officielle

Les versions et distributions peuvent différer ; consultez la documentation correspondant à l'environnement réellement déployé avant d'utiliser un réglage en production.

- Apache Hadoop, documentation générale : https://hadoop.apache.org/docs/stable/
- Apache Hadoop HDFS, guide de conception : https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html
- Apache Hadoop YARN, architecture : https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/YARN.html
- Apache Spark, documentation : https://spark.apache.org/docs/latest/
- Apache Spark, guide de programmation RDD : https://spark.apache.org/docs/latest/rdd-programming-guide.html
- Apache Spark SQL et DataFrames : https://spark.apache.org/docs/latest/sql-programming-guide.html
- Apache Spark, réglage de performance : https://spark.apache.org/docs/latest/sql-performance-tuning.html
- Apache Spark, Structured Streaming : https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
- Apache Parquet, documentation : https://parquet.apache.org/docs/
- Apache ORC, documentation : https://orc.apache.org/docs/

Ces références définissent les possibilités techniques des projets, mais ne déterminent pas à elles seules les politiques de production. Les valeurs de mémoire, de parallélisme, de rétention et les garanties de publication doivent être adaptées à la charge et testées sur le déploiement précis.

La maîtrise experte du Big Data se mesure à la capacité de faire des compromis explicites. Un job qui traite un volume énorme mais qui est impossible à auditer, à reprendre ou à sécuriser n'est pas une solution fiable. L'architecture doit expliquer d'où viennent les données, comment elles sont distribuées, comment le résultat reste juste malgré les pannes et comment une équipe peut diagnostiquer un incident à partir de faits mesurables.
