# Architecture Hadoop et Spark — Expert

> **Mise en contexte.** La plateforme de formation collecte des événements de navigation, des tentatives d’évaluation, des journaux d’accès et des traces de traitement. L’historique atteint plusieurs téraoctets et des analyses récurrentes dépassent la capacité d’une seule machine. L’équipe explore Hadoop et Spark pour stocker et traiter de gros volumes distribués. Le défi n’est pas d’ajouter un cluster pour donner une impression de puissance : il faut choisir une architecture en fonction de la taille des données, des transformations, des exigences de reprise, des formats, de la latence et des coûts d’exploitation.

## Objectifs pédagogiques et prérequis

Ce cours approfondit HDFS, YARN, MapReduce, les briques de l’écosystème Hadoop, l’architecture d’exécution Spark, les DataFrames, les plans logiques et physiques, les partitions, les shuffles, la persistance, la tolérance aux pannes, les formats de fichiers et les stratégies de performance. Vous apprendrez à distinguer les responsabilités de stockage et de calcul, expliquer le rôle du NameNode et des DataNodes, comprendre le rôle du ResourceManager et des NodeManagers, et décrire le parcours d’un job Spark du programme utilisateur aux tâches exécutées sur les workers.

Le cours suppose une maîtrise de SQL, de la programmation de base, des systèmes d’exploitation, du réseau et des principes de bases de données. Les exemples utilisent Python avec l’API PySpark, mais les concepts s’appliquent aussi aux interfaces Spark SQL et Scala. Les commandes de cluster sont des modèles : chemins, identités, paramètres et modes de déploiement doivent être adaptés à la distribution Hadoop/Spark et à la plateforme cible. Le traitement distribué implique des coûts de réseau et d’ordonnancement que ne montrent pas les tests sur une petite machine.

## 1. Ce que change le traitement distribué

Un traitement distribué découpe le travail sur plusieurs ressources. Il peut augmenter la capacité de stockage et le débit en répartissant données et calculs, mais il introduit des problèmes que le programme local ne rencontre pas de la même manière : partitionnement, transport réseau, exécution en parallèle, contention de ressources, reprise de tâches, déséquilibre de charge et cohérence de sortie. Le temps total dépend de la quantité de données, du nombre de partitions, du coût des opérations et de la disponibilité des nœuds.

La loi d’Amdahl rappelle qu’une partie séquentielle limite le gain d’un calcul parallélisé. Si une étape doit trier globalement les données ou regrouper toutes les valeurs sous une même clé, elle peut devenir un goulot d’étranglement même si les étapes précédentes sont distribuées. Ajouter plus de workers peut ne pas améliorer un job dominé par des accès disque, une mauvaise partition ou un shuffle disproportionné.

La distribution doit aussi répondre au modèle de défaillance. Un worker peut tomber pendant l’exécution; un fichier peut être inaccessible; le réseau peut être momentanément saturé; une tâche peut échouer sur une valeur particulière. L’architecture doit savoir relancer du travail sans dupliquer des effets externes, perdre des lignes ou publier un résultat partiel comme complet. Les mécanismes de tolérance du framework doivent être compris, pas supposés.

Un système distribué n’est pas automatiquement plus rapide pour un petit jeu de données. L’initialisation d’un job, la planification des tâches, la lecture de métadonnées et le transfert entre nœuds ajoutent un coût fixe. Il est courant d’utiliser un processus local pour valider le code et le schéma, puis un cluster pour les données représentatives. Il faut conserver une méthode de comparaison qui distingue le gain dû au parallélisme du coût opérationnel de l’infrastructure.

## 2. Les briques Hadoop : HDFS, YARN et MapReduce

Hadoop est une famille de composants, pas une seule base de données. HDFS est un système de fichiers distribué conçu pour stocker de gros fichiers en blocs et les répartir sur des DataNodes. Le NameNode gère les métadonnées du système de fichiers et la localisation des blocs; les DataNodes stockent et servent les blocs. La réplication des blocs apporte une tolérance à certaines pannes de nœud. Le niveau de réplication et le placement des blocs doivent être adaptés aux objectifs de disponibilité et de capacité.

HDFS est bien adapté à de gros fichiers accessibles par des traitements de type batch et à un débit élevé. Il n’est pas destiné à servir chaque petit fichier comme une base transactionnelle à faible latence. Un nombre énorme de petits fichiers peut mettre la pression sur les métadonnées et le NameNode. Lorsque les pipelines produisent des milliers de petits fichiers par partition, il faut souvent compacter les sorties et choisir des tailles de fichiers raisonnables.

MapReduce fournit un modèle de traitement distribué en phases de map et reduce. La phase map transforme des enregistrements en paires clé-valeur intermédiaires; le framework regroupe ou trie par clé, puis la phase reduce traite les valeurs d’une même clé. Le modèle est robuste pour de nombreux batchs, mais les écritures de résultats intermédiaires sur disque et les frontières de phases peuvent rendre certains algorithmes coûteux.

YARN gère l’allocation des ressources et l’ordonnancement d’applications. Le ResourceManager coordonne les ressources du cluster; les NodeManagers gèrent les ressources et conteneurs sur les machines. Un ApplicationMaster est associé à une application et interagit avec YARN pour demander les ressources et piloter l’exécution selon le framework. Il faut distinguer ce plan de contrôle des processus qui réalisent effectivement le calcul.

~~~mermaid
flowchart TD
    U[Utilisateur soumet un job] --> RM[ResourceManager]
    RM --> AM[ApplicationMaster]
    AM --> NM1[NodeManager A]
    AM --> NM2[NodeManager B]
    NM1 --> T1[Conteneurs de tâches]
    NM2 --> T2[Conteneurs de tâches]
    T1 --> HDFS[HDFS]
    T2 --> HDFS
    NN[NameNode et métadonnées] --> HDFS
~~~

HDFS et YARN résolvent des problèmes complémentaires : HDFS fournit un stockage distribué, tandis que YARN gère des ressources de calcul partagées. Un cluster Hadoop peut accueillir des moteurs autres que MapReduce lorsque ceux-ci intègrent les mécanismes YARN appropriés. De même, Spark peut fonctionner sans HDFS et ne dépend pas obligatoirement de Hadoop; il peut utiliser d’autres systèmes de fichiers et gestionnaires de cluster selon le déploiement.

## 3. HDFS : blocs, réplication et opérations

Un fichier HDFS est découpé en blocs. Les blocs sont répartis sur plusieurs DataNodes, et le NameNode garde les métadonnées qui décrivent où ils se trouvent. La taille des blocs influence l’équilibre entre les métadonnées, le parallélisme et l’efficacité des lectures. Une taille élevée réduit le nombre de blocs pour de gros fichiers; une taille trop élevée peut réduire le parallélisme sur des fichiers modestes. Les décisions doivent s’appuyer sur le type de données et les tâches qui les traitent.

La réplication protège contre la perte de certains DataNodes en conservant plusieurs copies des blocs. Le facteur de réplication est un compromis de stockage, disponibilité et coût réseau. Il ne protège pas contre toute suppression logique ou toute corruption appliquée à toutes les copies. Les politiques de placement cherchent à répartir les copies entre des domaines de panne, mais la configuration réelle doit être vérifiée dans le cluster.

Les commandes HDFS sont distinctes des commandes du système de fichiers local. Par exemple, hdfs dfs -ls liste un chemin HDFS et hdfs dfs -put transfère un fichier local vers HDFS. Le chemin source et le chemin cible doivent être identifiés clairement. Une commande de suppression telle que hdfs dfs -rm modifie le système de fichiers distribué et ne doit pas être utilisée sans vérifier le chemin et la politique de rétention.

~~~bash
hdfs dfs -mkdir -p /data/skilltree/events
hdfs dfs -put events-2026-10-28.jsonl /data/skilltree/events/
hdfs dfs -ls /data/skilltree/events
hdfs dfs -du -h /data/skilltree/events
~~~

Ces commandes supposent que le client est configuré pour le cluster souhaité et que l’utilisateur a les permissions nécessaires. Le nom de fichier en entrée doit exister localement; un transfert réussi doit être suivi d’une vérification de la présence, de la taille, du nombre de lignes si pertinent et de l’identité du fichier. Les commandes de production doivent être exécutées dans le bon environnement, sans supposer que le répertoire local et le chemin HDFS sont interchangeables.

Les fichiers de données doivent être organisés selon les accès. Un partitionnement par date peut simplifier les extractions d’une période et réduire les données lues par le moteur. Cependant, trop de partitions fines créent trop de chemins et de petits fichiers. Le schéma de répertoires doit correspondre aux requêtes habituelles et être accompagné d’une politique de compaction et de rétention.

## 4. MapReduce et le coût du shuffle

Une opération MapReduce peut lire des enregistrements, produire des clés intermédiaires et regrouper toutes les valeurs d’une même clé pour les reducers. Cette phase implique souvent un shuffle, c’est-à-dire le transfert et le regroupement de données entre nœuds. Le shuffle peut dominer le job en réseau, disque et mémoire. Une clé très fréquente peut créer un reducer qui reçoit une quantité disproportionnée de données, un phénomène appelé skew ou déséquilibre de clé.

L’agrégation locale peut réduire le volume transmis. Si chaque mapper calcule un sous-total local pour une clé, il transmet moins d’enregistrements au reduce. Cette optimisation n’est pas applicable à toutes les opérations : une opération qui ne peut pas être résumée de manière associative et commutative ne peut pas forcément être partiellement agrégée. Comprendre la mathématique de l’opération est aussi important que comprendre le framework.

Le nombre de reducers affecte le parallélisme et le volume de données traité par tâche. Trop peu de reducers crée des tâches longues; trop de reducers crée du travail de planification et de nombreux fichiers. Le choix doit être fondé sur le volume, le débit du cluster et les limites de ressources. Un nombre de reducers constant pour toutes les tailles de données peut être inefficace.

Les fichiers temporaires et résultats intermédiaires consomment du disque et du réseau. Un job qui réussit avec des données petites peut échouer en grande taille faute d’espace, de mémoire ou de capacité de sortie. Le monitoring doit inclure les durées par phase, le nombre d’enregistrements, les erreurs, le taux de reprise, les entrées/sorties et les tâches les plus lentes. Le meilleur diagnostic compare la distribution des tâches, pas seulement la durée totale.

## 5. Spark : moteur d’exécution et modèle de programmation

Apache Spark fournit un moteur de calcul distribué adapté aux transformations batch, SQL, au machine learning et au traitement structuré de flux selon les composants utilisés. Spark se distingue notamment par son moteur d’exécution optimisé et sa capacité à réutiliser des données en mémoire lorsque le plan s’y prête. Il n’est pas une base de données à part entière; il lit et écrit des données dans des systèmes de stockage tels que HDFS, le stockage objet ou d’autres sources supportées.

Un programme Spark utilise un driver qui construit et coordonne l’exécution, puis des executors qui exécutent des tâches et peuvent conserver des données en cache ou en mémoire selon le plan. Le driver traduit le programme en un graphe de dépendances et planifie des stages et tâches. Les workers exécutent les partitions de données. Le nombre d’executors, les cores, la mémoire, le partitionnement et le gestionnaire de cluster déterminent une partie de la capacité.

~~~mermaid
flowchart TD
    A[Application PySpark] --> B[Driver]
    B --> C[Plan logique]
    C --> D[Optimisation du plan]
    D --> E[Plan physique et DAG]
    E --> F[Découpage en stages]
    F --> G[Tâches par partition]
    G --> H[Executors]
    H --> I[Lecture et écriture du stockage]
    H --> J[Cache et mémoire d'exécution]
~~~

L’API DataFrame décrit une table distribuée avec colonnes typées ou inférées, transformations déclaratives et opérations d’agrégation. Spark SQL peut optimiser des expressions pour créer un plan physique. L’API RDD existe et reste utile dans certains contextes, mais les DataFrames et SQL sont souvent préférables pour des données structurées car le moteur possède davantage d’informations pour optimiser le calcul.

Une transformation est souvent paresseuse : elle décrit une opération sans la lancer immédiatement. Une action, telle qu’un count, une écriture ou collect, déclenche l’exécution. Cette évaluation paresseuse permet au moteur d’optimiser une chaîne, mais peut surprendre si le programme répète plusieurs actions qui recalculent le même DAG. Il faut observer les actions et mettre en cache les données réutilisées uniquement lorsque le coût et la mémoire le justifient.

## 6. DataFrames, transformations et actions PySpark

Les opérations typiques comprennent read pour lire une source, select pour projeter des colonnes, filter/where pour filtrer, groupBy pour grouper, join pour combiner, repartition pour redistribuer, cache/persist pour conserver des données réutilisées et write pour publier les résultats. Le programme doit savoir quel format il lit, quel schéma est attendu, quelles colonnes sont utilisées et comment les erreurs de parsing sont traitées.

~~~python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("skilltree-course-attempts")
    .getOrCreate()
)

attempts = (
    spark.read
    .option("header", True)
    .schema("""
        attempt_id STRING,
        learner_id STRING,
        course_id STRING,
        score DOUBLE,
        finished BOOLEAN,
        event_time TIMESTAMP
    """)
    .csv("hdfs:///data/skilltree/attempts/")
)

finished = attempts.filter(
    F.col("finished") == F.lit(True)
)

summary = (
    finished
    .groupBy("course_id")
    .agg(
        F.count("*").alias("attempt_count"),
        F.avg("score").alias("average_score"),
        F.max("score").alias("best_score")
    )
)

summary.write.mode("overwrite").parquet(
    "hdfs:///warehouse/skilltree/course_summary/"
)
~~~

L’exemple illustre une chaîne batch, mais doit être adapté à la source réelle. Les chemins HDFS ne sont accessibles que depuis un environnement configuré. Le schéma doit correspondre aux données; la façon dont Spark parse les valeurs booléennes, timestamps et nombres dépend du format et des options. Un mode overwrite peut remplacer une sortie existante et doit être utilisé sur une cible dont le comportement est contrôlé. En production, une sortie versionnée, un chemin de lot ou une table gérée peut être plus approprié.

L’action collect ramène les lignes au driver et doit être évitée sur un jeu de données volumineux. Une conversion vers une liste Python peut épuiser la mémoire du driver. show limite généralement l’affichage à un petit échantillon, mais les opérations qui collectent toutes les données doivent être soigneusement contrôlées. Utilisez count, limit et des échantillons représentatifs pour valider la structure, sans confondre ces actions de test avec un benchmark de production.

Le schéma explicite est préférable lorsque les types et contrats sont connus. L’inférence peut être coûteuse et produire des types inattendus, notamment lorsque les données sont hétérogènes ou lorsqu’un fichier est vide. Les erreurs de parsing doivent être observées, comptabilisées et traitées selon une politique. Les lignes rejetées ne doivent pas disparaître sans trace, surtout lorsque les indicateurs en aval sont utilisés pour des décisions.

## 7. Plans Spark, stages et transformations larges

Spark construit des plans logiques et physiques à partir des transformations. La projection et les filtres peuvent être poussés vers la source lorsque le connecteur et le format le permettent. Le moteur peut choisir des stratégies de jointure, des échanges de données et des opérations de tri. L’inspection du plan aide à comprendre quelles colonnes sont lues, où les données sont réparties, quels échanges sont nécessaires et quelle opération génère le plus de travail.

Les transformations étroites peuvent traiter une partition de sortie à partir d’une partition d’entrée, sans redistribution complète entre workers. Les transformations larges impliquent souvent un shuffle et des dépendances entre nombreuses partitions, par exemple groupBy, certaines jointures ou un repartition. Elles sont coûteuses parce qu’elles déplacent des données entre exécutants, écrivent des fichiers intermédiaires et nécessitent de coordonner les résultats.

Un shuffle n’est pas un défaut : il est nécessaire pour agréger ou combiner des clés présentes sur différents workers. L’objectif est de limiter les shuffles inutiles et de réduire le volume transféré. Filtrer tôt, sélectionner uniquement les colonnes nécessaires et utiliser une stratégie de jointure adaptée peut faire une différence considérable. Repartitionner sans compréhension peut au contraire forcer une redistribution plus coûteuse.

~~~python
summary.explain(mode="formatted")
~~~

La sortie précise dépend de la version de Spark et du contexte d’exécution. Regardez les opérateurs d’échange, la stratégie de jointure, les filtres et projections, ainsi que les estimations ou statistiques disponibles. Le plan logique seul ne révèle pas tous les problèmes d’une exécution réelle; il faut également examiner l’interface de supervision, les tâches, les temps de shuffle, le spill disque, les erreurs et la distribution de durée par tâche.

Une jointure peut utiliser un broadcast join lorsque l’une des relations est suffisamment petite et que les conditions le permettent. Une diffusion excessive peut épuiser la mémoire des executors. Une jointure entre deux relations volumineuses peut nécessiter un shuffle partitionné. Le choix dépend du volume, du format, des filtres et du nombre de clés. Il faut mesurer avec les données réelles avant d’imposer une stratégie.

## 8. Partitions, skew et équilibrage

Une partition est une unité de travail qui peut être traitée en parallèle. Trop peu de partitions peut sous-utiliser le cluster; trop de partitions crée un coût de planification, d’ouverture de fichiers et d’ordonnancement. La taille raisonnable dépend du moteur, du format, du volume, de la mémoire par tâche et de la charge. Il n’existe pas un seul nombre de partitions optimal pour tous les jobs.

Le skew apparaît lorsque certaines partitions ou clés contiennent beaucoup plus de données ou de travail que les autres. Le job peut avoir presque toutes les tâches terminées alors qu’une tâche reste pendant longtemps; cette dernière peut dominer la durée totale. Ajouter des executors ne résout pas nécessairement une clé extrêmement fréquente, car la clé peut encore être affectée à un seul groupe logique.

Les techniques pour réduire le skew incluent un partitionnement approprié, une agrégation locale, le salting contrôlé de certaines clés, l’activation de mécanismes adaptatifs supportés par la version ou la réécriture de l’algorithme. Le salting répartit temporairement une clé populaire entre plusieurs clés artificielles, puis agrège les sous-résultats. Cette technique exige de comprendre l’opération; elle ne s’applique pas uniformément à chaque métrique, particulièrement pour les opérations non associatives.

Les partitions de sortie influencent aussi le nombre de fichiers. Une écriture parpartition peut produire beaucoup de petits fichiers si la cardinalité de la clé est grande. À l’inverse, coalesce trop agressif peut créer quelques fichiers gigantesques et réduire le débit. Le nombre et la taille des fichiers doivent être observés en relation avec les requêtes suivantes, la compaction et le système de stockage.

## 9. Cache, persistance et mémoire

Le cache Spark peut être utile lorsque le même DataFrame est utilisé plusieurs fois et que son recalcul serait coûteux. Le cache occupe des ressources et peut entraîner l’éviction d’autres données; si un DataFrame n’est utilisé qu’une fois, sa mise en cache peut être inutile. La décision doit mesurer le coût de reconstruction, la mémoire, le disque local et les autres jobs qui partagent le cluster.

Les données mises en cache doivent être libérées lorsque la phase de calcul est terminée. Un cache oublié peut réduire la mémoire disponible et rendre d’autres tâches plus lentes. Une application qui conserve plusieurs DataFrames intermédiaires sans nécessité peut provoquer une pression de mémoire ou du spill disque. L’interface de supervision montre généralement les données cachées et leur occupation.

Le stockage en mémoire n’est pas nécessairement durable au sens métier. Si un executor tombe, les partitions perdues peuvent être recalculées à partir du lineage ou relues depuis la source, selon le type de transformation. Cela n’est possible que si les données sources et le graphe de dépendances restent disponibles. Spark ne remplace pas une sauvegarde durable de la source et ne doit pas être utilisé comme l’unique stockage de résultats irremplaçables.

Le spill disque survient lorsque certaines opérations dépassent la mémoire disponible et doivent s’appuyer sur le stockage local. Cela peut éviter l’échec mais augmenter la durée. Une hausse du spill peut venir d’une agrégation ou jointure trop large, d’un déséquilibre ou d’un partage de ressources. Ajouter de la mémoire peut aider, mais filtrer plus tôt, réduire la largeur des données et corriger une stratégie de jointure peut produire un meilleur gain à moindre coût.

## 10. Formats analytiques : Parquet, ORC et fichiers de lignes

Le choix du format influe sur le stockage et l’exécution. CSV est lisible et souvent utilisé pour des échanges, mais il ne conserve pas naturellement tous les types, les métadonnées de schéma ou les possibilités de lecture sélective de colonnes. JSON est flexible mais peut coûter davantage à parser. Parquet et ORC sont des formats colonnaires courants pour les données analytiques; ils permettent une lecture de colonnes sélectionnées et des mécanismes de compression adaptés à de nombreuses charges.

Un format colonne peut réduire les E/S lorsqu’une requête utilise peu de colonnes sur un large jeu de données. Il ne garantit pas que chaque requête sera rapide : le partitionnement, l’organisation des fichiers, les statistiques, les filtres et le volume des lignes comptent. Des milliers de très petits fichiers peuvent annuler certains bénéfices du format et ralentir la découverte des métadonnées.

Le partitionnement par date est utile lorsque les requêtes filtrent fréquemment une période. Mais une partition par identifiant d’apprenant peut produire un nombre énorme de répertoires et de fichiers. Choisissez les colonnes de partitionnement en fonction des filtres courants, de la cardinalité, de la taille des lots et des formats de stockage. Le partitionnement ne remplace pas les index ou métadonnées de chaque moteur.

L’organisation d’un entrepôt utilise souvent des zones brutes, nettoyées et prêtes à l’analyse. Ces noms — bronze, silver, gold — sont des conventions de conception, pas des garanties de qualité. Il faut définir ce que chaque zone garantit : originalité de la source, normalisation, déduplication, règles d’intégrité, grain, fraîcheur et compatibilité de schéma. Sans ce contrat, les utilisateurs choisissent une table au hasard et obtiennent des chiffres divergents.

## 11. Tolérance aux pannes et sortie sûre

Spark et Hadoop peuvent relancer des tâches lorsqu’un worker ou une tâche échoue, mais le code utilisateur peut encore créer des effets non idempotents. Une tâche qui envoie un courriel ou appelle un endpoint externe ne doit pas supposer qu’elle ne sera exécutée qu’une seule fois. Un retry peut répéter l’appel. Les jobs analytiques devraient généralement écrire vers une cible contrôlée, avec identifiant de lot, staging et publication validée plutôt que d’effectuer directement des effets métier externes.

La sortie doit être atomique du point de vue du consommateur ou publier un état qui indique son niveau de complétude. Selon le stockage et le connecteur, l’écriture peut produire plusieurs fichiers; il faut distinguer les données temporaires de la version publiée. Un consommateur ne doit pas lire un répertoire à moitié écrit et croire qu’il s’agit du nouveau rapport complet.

Le partitionnement de sortie et le nombre de fichiers doivent être calculés avant la publication. Une tâche échouée peut laisser des fichiers temporaires ou un état de transaction qui nécessite un nettoyage supporté. Ne supprimez pas manuellement des répertoires du stockage partagé tant que vous ne savez pas s’ils appartiennent à un job actif. Utilisez le mécanisme de commit et les outils du connecteur qui correspondent au format.

La reprise doit enregistrer l’identifiant du batch, la source et son point de capture, la version de code et de schéma, le volume lu, le volume écrit et les contrôles effectués. Si la relance produit un autre résultat pour les mêmes entrées, recherchez une dépendance à l’heure courante, à un ordre instable, à des données sources modifiées ou à une fonction non déterministe. L’idempotence et la reproductibilité rendent les incidents plus simples à traiter.

## 12. Atelier pratique : résumé de cours avec PySpark

Sur un environnement local compatible Spark ou un cluster de laboratoire, préparez un jeu synthétique de tentatives. Le but est de tester le pipeline et le plan, pas de mesurer la capacité maximale d’un cluster local.

~~~python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("skilltree-lab-summary")
    .master("local[*]")
    .getOrCreate()
)

rows = [
    ("a1", "course-1", 80.0, True),
    ("a2", "course-1", 70.0, True),
    ("a1", "course-2", 91.0, True),
    ("a3", "course-1", None, False),
]

attempts = spark.createDataFrame(
    rows,
    ["learner_id", "course_id", "score", "finished"]
)

finished = attempts.filter(F.col("finished"))
summary = (
    finished
    .groupBy("course_id")
    .agg(
        F.count("*").alias("attempt_count"),
        F.countDistinct("learner_id").alias("learner_count"),
        F.avg("score").alias("average_score"),
        F.max("score").alias("best_score")
    )
)

summary.orderBy("course_id").show(truncate=False)
summary.explain(mode="formatted")
~~~

Le résultat doit montrer une ligne par cours avec au moins une tentative terminée. Comparez attempt_count et learner_count lorsque le même apprenant réalise plusieurs tentatives. Observez le traitement du score NULL. L’exercice doit inclure des cas qui peuvent invalider des hypothèses, pas seulement des données propres qui rendent toutes les formes de requêtes équivalentes.

Ensuite, écrivez le résultat en Parquet dans un répertoire de laboratoire, puis relisez-le et vérifiez que les types et les valeurs sont conservés. Ne réutilisez pas une sortie de production. Comparez le nombre de fichiers et le temps de lecture sur un jeu plus grand, et observez l’impact d’un partitionnement par date. Évitez de conclure sur la performance avec un petit tableau en mémoire.

## 13. Exécution et diagnostic du cluster

Avant de lancer un job, vérifiez le gestionnaire de cluster, la version du runtime, les bibliothèques, les droits de lecture, les paramètres de ressources et les chemins de sortie. Le job doit être associé à un nom et à un identifiant qui permettent de le retrouver dans l’interface de supervision. Les logs driver et executor doivent être disponibles pour l’équipe responsable.

Une exécution lente peut provenir du parsing, de la lecture, d’un shuffle, d’un skew, de la mémoire, du spill disque, d’une cible d’écriture lente ou d’une concurrence avec d’autres applications. Mesurez la durée par stage, le nombre de tâches, les distributions, la quantité de données lues et écrites, la taille des sorties et les erreurs. Si quelques tâches sont beaucoup plus lentes que les autres, examinez les clés et les partitions concernées.

Il faut aussi distinguer la saturation permanente d’un pic temporaire. Un cluster partagé peut ralentir parce qu’une autre application consomme les ressources. Une tâche peut rester en attente faute de cœurs ou de mémoire même si son propre plan est raisonnable. L’ordonnancement, les quotas et les priorités sont des paramètres opérationnels; l’équipe de données doit pouvoir identifier qui utilise le cluster et selon quelles limites.

Le dimensionnement doit considérer le coût total. Un cluster trop grand peut traiter un job plus vite mais rester inutilisé la plupart du temps. Un cluster partagé peut être plus économique mais plus sensible à la contention. La meilleure solution est celle qui respecte le niveau de service avec un coût et une charge opérationnelle acceptables, pas celle qui utilise le plus de machines.

## 14. Exercices corrigés

### Exercice 1 — Spark nécessite-t-il Hadoop?

Une équipe veut utiliser Spark mais ne souhaite pas déployer HDFS. Est-ce possible?

**Correction.** Oui. Spark peut s’exécuter sans Hadoop et utiliser d’autres systèmes de fichiers ou stockages compatibles, ainsi que différents gestionnaires de cluster. Hadoop et Spark sont liés dans de nombreux déploiements, mais ils ne sont pas le même composant et Spark ne nécessite pas obligatoirement HDFS. Le choix du stockage et du gestionnaire doit être explicite.

### Exercice 2 — Un seul reducer est lent

La plupart des tâches terminent en dix secondes, mais une tâche de réduction prend dix minutes.

**Correction.** Inspectez la distribution des clés, les volumes par partition, les données envoyées lors du shuffle et les valeurs populaires. Le problème peut être un skew ou un reducer qui reçoit la majorité des données. Envisagez agrégation locale, salting si l’opération le permet, adaptation du partitionnement ou réécriture du traitement. Ajouter des workers sans changer la distribution peut ne rien résoudre.

### Exercice 3 — Collect provoque une panne

Un script appelle collect sur un DataFrame de plusieurs dizaines de millions de lignes et le driver manque de mémoire.

**Correction.** collect ramène l’ensemble des lignes au processus driver. Pour un grand résultat, il faut garder le calcul distribué et écrire une sortie dans un stockage durable ou limiter l’échantillon. Les actions locales de collecte sont adaptées aux petits résultats ou aux tests, pas aux grands jeux de données.

### Exercice 4 — Trop de petits fichiers

Un job écrit 200 000 fichiers d’une taille minuscule.

**Correction.** Examinez le partitionnement de sortie, la cardinalité des clés et la façon dont le job découpe les partitions. Choisissez un nombre de partitions adapté, regroupez les résultats lorsque cela est sûr et prévoyez une compaction. N’effectuez pas un coalesce aveugle qui créerait quelques fichiers gigantesques ou une tâche unique qui deviendrait un goulot.

### Exercice 5 — Pourquoi cacher un DataFrame?

Une même transformation coûteuse est utilisée par trois actions successives.

**Correction.** Le moteur peut recalculer le DAG pour plusieurs actions. Mettre en cache le résultat peut éviter certains recalculs, à condition que le DataFrame soit réellement réutilisé et que la mémoire disponible soit suffisante. Mesurez le coût de recalcul, l’occupation de cache, les évictions et la durée globale, puis libérez les données persistées lorsque la phase est terminée.

## 15. Défi final : pipeline analytique de plusieurs téraoctets

Vous devez agréger quotidiennement plusieurs téraoctets de tentatives et d’événements. Le rapport comporte un nombre de tentatives terminées, un nombre d’apprenants uniques et une moyenne de score par cours et par jour. Certains cours possèdent beaucoup plus d’événements que d’autres. Le résultat ne doit pas être publié s’il est incomplet et doit pouvoir être rejoué après un échec.

### Correction attendue

1. **Source et format.** Choisir un stockage adapté aux gros fichiers et une convention de partitionnement par date qui correspond aux requêtes temporelles. Utiliser un format structuré et compressé comme Parquet lorsque le moteur et les consommateurs le supportent. Contrôler le schéma, les événements invalides et la politique de rétention.

2. **Plan Spark.** Lire seulement les colonnes utiles, filtrer les événements terminés et la période avant les transformations larges, puis agréger au grain cours-jour. Examiner le plan et les échanges de données. Si les clés sont déséquilibrées, mesurer le skew et utiliser une stratégie spécifique.

3. **Déduplication.** Utiliser un identifiant d’événement stable ou une clé de source. Documenter si des événements dupliqués peuvent arriver. Appliquer une déduplication avant de calculer les indicateurs, sans supprimer des événements légitimes qui se ressemblent.

4. **Calculs.** Compter les événements et les apprenants uniques séparément; calculer la moyenne du score en traitant les valeurs absentes selon un contrat explicite. Ne pas faire la moyenne des moyennes journalières pour obtenir une moyenne globale sans pondération appropriée.

5. **Publication.** Écrire dans une zone de lot identifiée, exécuter des contrôles de qualité et publier un pointeur ou une table de version seulement lorsque les contrôles réussissent. Le consommateur doit lire une version complète. La relance du même batch ne doit pas doubler les faits.

6. **Surveillance.** Mesurer le retard, les lignes sources, les rejets, le volume écrit, la durée par stage, le shuffle, le spill, les erreurs et les tâches lentes. Alertes et runbooks doivent avoir un propriétaire.

7. **Coût.** Tester plusieurs tailles de cluster et de partitions avec un jeu représentatif. Comparer le délai de fin, les E/S, les ressources et les coûts. Choisir le plus petit profil qui respecte le niveau de service avec une marge raisonnable.

## 16. Checklist et synthèse

Hadoop fournit des composants distincts de stockage et de gestion des ressources; HDFS gère des fichiers distribués, YARN alloue les ressources et MapReduce offre un modèle batch par phases. Spark propose un moteur de calcul qui construit et exécute un graphe de dépendances, avec DataFrames et SQL souvent adaptés aux données structurées. Le plan, le partitionnement, le shuffle, le cache, les formats et les sorties déterminent une grande part de la performance.

Un job fiable doit être reproductible, observable, tolérant aux échecs et prudent avec les effets externes. La taille du cluster ne corrige pas automatiquement un skew, une requête qui lit trop de colonnes ou une sortie qui crée des milliers de petits fichiers. La conception de données doit correspondre aux usages; les mesures et contrôles de qualité doivent précéder la publication. Le traitement distribué réussit lorsque les résultats sont exacts, répétables et livrés avec une latence et un coût maîtrisés.

## Ressources officielles

- Apache Hadoop, HDFS : https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html
- Apache Hadoop, architecture YARN : https://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/YARN.html
- Apache Hadoop, tutoriel MapReduce : https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html
- Apache Spark, documentation générale : https://spark.apache.org/docs/latest/
- Apache Spark, guide SQL : https://spark.apache.org/docs/latest/sql-programming-guide.html
- Apache Spark, réglage de performance : https://spark.apache.org/docs/latest/sql-performance-tuning.html
- Apache Spark, Structured Streaming : https://spark.apache.org/docs/latest/streaming/index.html

Les composants et paramètres exacts changent entre distributions et versions. Validez les commandes, le gestionnaire de cluster, les permissions et les mécanismes de sortie dans l’environnement cible avant toute exploitation.
