# Data Lakes et Lakehouse — Expert

> **Mise en contexte.** L’entreprise veut consolider les données transactionnelles, les événements Kafka, les journaux techniques, les fichiers de formation et les exports partenaires. Les formats et les schémas varient; certaines équipes veulent conserver les données originales pour rejouer les transformations, d’autres ont besoin de tables analytiques avec des transactions, un historique et des changements de schéma maîtrisés. Un data lake permet de centraliser des données dans un stockage peu coûteux et évolutif, tandis qu’une architecture lakehouse ajoute des capacités de gestion de tables analytiques fiables au-dessus des fichiers. La réussite exige une gouvernance, des métadonnées et une stratégie de cycle de vie, pas seulement un bucket très grand.

## Objectifs et prérequis

Ce cours approfondit les architectures de data lake et lakehouse, les zones de données, le stockage objet, les formats colonnes, les catalogues, les métadonnées, les formats de table, les snapshots, l’évolution de schéma et de partitionnement, les transactions analytiques, les pipelines batch et streaming, l’optimisation des fichiers et la gouvernance. Vous apprendrez à distinguer fichiers bruts, tables gérées et vues de consommation, à planifier les changements de schéma, à réduire les petits fichiers, à tester la reproductibilité et à gérer les politiques de rétention.

Le cours suppose une maîtrise des entrepôts de données, ETL/ELT et des traitements analytiques distribués. Les exemples évoquent Apache Iceberg et Spark, mais le lakehouse peut utiliser différentes technologies et différents catalogues. Les commandes exactes dépendent du moteur, du catalogue, du stockage objet et des connecteurs choisis. Une architecture qui fonctionne avec une version d’Iceberg et un moteur donné ne doit pas être supposée compatible avec toutes les versions.

## 1. Data lake : principe et motivations

Un data lake conserve des données dans un stockage évolutif, souvent sous forme de fichiers dans un stockage objet ou un système distribué. Il peut accueillir des données structurées, semi-structurées et non structurées, les originales et leurs transformations. Cette diversité permet de différer certaines décisions de modélisation jusqu’au moment de la consommation, souvent résumé par l’expression schema-on-read. Ce modèle peut accélérer l’arrivée de nouvelles sources, mais il ne dispense pas de contrôler les formats, les accès, les schémas et la qualité.

Un lac sans gouvernance peut devenir un « marécage de données » : fichiers sans propriétaire, duplications, noms incohérents, données personnelles non classifiées, métadonnées manquantes et modèles impossibles à reproduire. La flexibilité de stockage doit être accompagnée d’un catalogue, de conventions de nommage, d’une politique de rétention, d’un lignage et de tests. Sans ces éléments, la quantité de données augmente plus vite que la capacité à les utiliser correctement.

Il faut distinguer l’arrivée de données et leur publication. Un fichier déposé dans une zone brute ne devrait pas être automatiquement considéré comme un ensemble fiable pour l’analytique. Il peut contenir des doublons, des timestamps invalides, un schéma non reconnu ou des données incomplètes. Les consommateurs doivent pouvoir savoir quelle zone est brute, quelle zone est nettoyée et quel modèle offre un contrat de données validé.

Le stockage objet favorise la durabilité, l’évolutivité et une séparation des coûts de stockage et de calcul, mais ses opérations et latences diffèrent d’un système de fichiers local. Le calcul distribué doit gérer les listes de fichiers, les commits de données, les métadonnées et les fichiers temporaires. Les méthodes de modification de table qui sont sûres sur une base relationnelle ne se traduisent pas automatiquement en opérations atomiques sur un ensemble de fichiers.

## 2. Lakehouse : ajouter la gestion de tables

Une architecture lakehouse cherche à combiner l’évolutivité et le coût d’un stockage de type lake avec les propriétés de gestion d’un entrepôt : tables, schémas, transactions, snapshots, évolution, partitionnement, visibilité cohérente et contrôle des métadonnées. Le terme décrit une architecture et un ensemble de capacités, pas une seule implémentation. Les formats de table comme Apache Iceberg, Delta Lake ou Apache Hudi fournissent des mécanismes différents; leurs capacités et leur compatibilité doivent être comparées dans l’environnement cible.

Un format de table gère des données et des métadonnées qui indiquent quels fichiers font partie d’une version logique. Un lecteur ne doit pas simplement parcourir tous les fichiers d’un répertoire et supposer qu’ils constituent l’état courant. Les métadonnées de table déterminent l’ensemble de fichiers visible, le schéma, le partitionnement et parfois l’historique de snapshots. Les opérations de modification publient une nouvelle version des métadonnées selon le mécanisme de commit supporté.

Ce modèle évite plusieurs problèmes de fichiers bruts, mais il introduit des opérations d’administration : maintenance des snapshots, expiration de l’historique, compaction, suivi des fichiers orphelins, mise à jour du catalogue et compatibilité entre moteurs. Une table peut être correcte et lisible mais inefficace en raison de trop petits fichiers, d’une partition peu adaptée ou d’un historique qui occupe un stockage croissant. Le cycle de vie doit être défini dès la conception.

~~~mermaid
flowchart TD
    A[Sources hétérogènes] --> B[Zone brute]
    B --> C[Tables nettoyées]
    C --> D[Format de table lakehouse]
    D --> E[Snapshots et métadonnées]
    D --> F[Modèles analytiques]
    F --> G[BI, ML et applications]
    H[Catalogue et gouvernance] --> D
    I[Qualité, lignage et ACL] --> C
    I --> F
    J[Compaction et rétention] --> D
~~~

## 3. Zones bronze, silver et gold

Une organisation courante sépare les données en zones bronze, silver et gold. Bronze conserve la représentation brute ou aussi proche que possible de la source, avec le contexte de capture. Silver applique la normalisation, la validation, la déduplication et la résolution des formats. Gold contient des modèles orientés vers les usages de consommation : tables de faits, dimensions, agrégats et indicateurs. Ces noms sont des conventions; les propriétés garanties doivent être documentées plutôt que déduites de la couleur.

La zone bronze sert à rejouer les transformations, examiner les changements de source et conserver le contexte de l’arrivée. Elle doit enregistrer la source, la date de capture, l’identifiant de lot, la version de schéma et les informations de provenance nécessaires. La zone brute peut contenir des secrets ou des identifiants personnels; son accès ne doit pas être plus large que celui de la source par défaut. La rétention brute doit être liée aux usages, aux risques et aux obligations applicables.

La zone silver réduit l’ambiguïté. Les horodatages sont normalisés, les champs ont des types définis, les clés de déduplication sont documentées et les données invalides sont rejetées ou mises en quarantaine. Cette zone ne doit pas simplement supprimer les enregistrements qui ne correspondent pas au schéma. Il faut compter les rejets, expliquer leur raison et décider si la publication est bloquée, partielle ou autorisée.

La zone gold est optimisée pour les consommateurs. Elle doit posséder un grain et une définition d’indicateur clairs, une politique de fraîcheur et un propriétaire. Si plusieurs tableaux de bord recomputent la même métrique avec des filtres différents, la logique doit être centralisée et testée. Les modèles gold ne doivent pas devenir un ensemble de tables sans dictionnaire ou avec des colonnes dont le sens dépend de l’équipe qui les a créées.

Le passage d’une zone à une autre est une frontière de qualité et de responsabilité. Les tests doivent vérifier les volumes, les clés, les types, les valeurs autorisées et la fraîcheur. Une nouvelle version d’un modèle doit rester reproductible, et les utilisateurs doivent pouvoir identifier quelles tables sont recommandées, quelles sont expérimentales et quelles sont dépréciées.

## 4. Stockage objet, partitionnement et formats

Le stockage objet conserve des objets adressés par clé, avec des opérations différentes de celles d’un système de fichiers POSIX. Il est adapté à de grands volumes de fichiers et à une séparation du calcul et du stockage. Mais la liste des objets, le coût des requêtes de métadonnées, les opérations de renommage, les éventuelles cohérences de visibilité et le comportement du catalogue doivent être pris en compte par les moteurs et connecteurs.

Parquet et ORC sont des formats colonnaires fréquemment utilisés en analytique. Ils permettent de lire seulement les colonnes demandées et de bénéficier de compression et d’organisation des données par groupes. Avro et d’autres formats orientés lignes peuvent convenir à des échanges ou à des flux où la structure des enregistrements est importante. CSV et JSON sont simples pour certains usages, mais leurs types et coûts de parsing peuvent être moins adaptés aux scans analytiques massifs.

Le partitionnement organise les données en sous-ensembles, souvent par date ou domaine. Il permet de limiter la quantité lue lorsqu’une requête filtre sur la colonne de partitionnement. Une partition trop fine produit trop de petits fichiers ou de métadonnées; une partition trop large oblige à lire davantage de données. La clé doit correspondre aux requêtes, au volume et au rythme d’arrivée. Une partition par identifiant utilisateur est souvent trop cardinalisée pour de nombreuses tables analytiques.

Le partitionnement logique d’une table lakehouse et son organisation physique ne sont pas toujours identiques. Des formats modernes peuvent gérer l’évolution de la disposition physique sans imposer aux consommateurs de réécrire leurs requêtes. Le bon choix dépend du format de table, du moteur, du catalogue et de la version supportée. Les hypothèses doivent être testées sur une copie représentative avant d’appliquer une nouvelle partition en production.

Les petits fichiers constituent un problème classique. Un pipeline qui écrit un fichier par tâche, micro-batch ou clé très spécifique peut créer des centaines de milliers de fichiers. La lecture doit alors ouvrir trop d’objets et traiter trop de métadonnées. La compaction regroupe certains fichiers pour retrouver des tailles plus adaptées, mais elle consomme du calcul et doit être coordonnée avec les lecteurs et écrivains. Il faut mesurer l’efficacité de lecture et de maintenance après compaction.

## 5. Catalogue et métadonnées de table

Le catalogue décrit quelles tables existent, où se trouvent leurs métadonnées et comment les moteurs les identifient. Selon l’architecture, il peut s’agir d’un catalogue de métadonnées associé à un moteur, d’un service partagé ou d’une intégration avec un catalogue de données plus large. Un format de table, un catalogue et un moteur d’exécution sont des composants distincts même s’ils sont vendus ou déployés ensemble dans certaines plateformes.

Le catalogue doit être cohérent avec les permissions et les environnements. Deux environnements ne doivent pas modifier la même table de production par accident; les noms de base, schémas et tables doivent être explicites. La configuration du catalogue fait partie du plan de reprise : sans elle, les fichiers peuvent exister mais les moteurs ne savent pas retrouver la version logique courante de la table.

Les métadonnées comprennent le schéma, la disposition des partitions, les fichiers de données, les snapshots et éventuellement les statistiques. Elles permettent au moteur de sélectionner les fichiers correspondant à une requête. Si ces métadonnées vieillissent, s’accumulent ou sont supprimées au mauvais moment, les performances et la reprise peuvent se dégrader. Les opérations de maintenance doivent utiliser les mécanismes supportés par le format de table et le catalogue.

Le catalogue de données au sens gouvernance apporte des descriptions, propriétaires, classifications, glossaires, politiques d’accès et lignage. Il ne faut pas confondre ce catalogue métier avec le catalogue technique nécessaire à l’ouverture des tables. Les deux sont liés : le registre de gouvernance décrit le sens et le propriétaire, tandis que le catalogue technique permet au moteur de lire le bon état de la table. Une architecture complète doit maintenir les deux.

## 6. Snapshots, time travel et commits

Un snapshot représente un état logique d’une table à un point défini. Dans un format lakehouse, les métadonnées peuvent pointer vers des fichiers de données immuables; un nouveau commit publie un nouvel ensemble de métadonnées. Les snapshots facilitent la lecture cohérente d’une version, la comparaison entre états et certains usages de restauration ou de time travel selon le moteur et le format.

Le time travel permet de lire une version antérieure lorsqu’elle est encore conservée. Il peut être utile pour enquêter sur un indicateur qui a changé, comparer une transformation ou restaurer une table après un traitement incorrect. Ce mécanisme dépend de l’historique des métadonnées et des fichiers toujours présents. Expirer les snapshots ou supprimer des fichiers nécessaires réduit la durée pendant laquelle la récupération est possible.

Les commits concurrents doivent être coordonnés. Deux écrivains peuvent lire le même état initial puis tenter de publier des changements; le format et le catalogue déterminent comment une collision est détectée et quelles opérations peuvent être retentées. Une écriture réussie au niveau des fichiers n’est pas nécessairement un commit visible de la table. L’application doit respecter le protocole du format et ne pas gérer les fichiers comme si elle pouvait mettre à jour manuellement le pointeur de métadonnées.

Les snapshots peuvent augmenter l’espace occupé lorsque des fichiers sont réécrits ou lorsque l’historique est conservé longtemps. L’expiration des snapshots et le nettoyage des fichiers orphelins doivent être exécutés selon la politique de conservation. Les fichiers orphelins ne sont pas toujours des fichiers inutiles : un job encore actif ou une opération interrompue peut dépendre de fichiers qui ne sont pas encore référencés dans le catalogue courant. Utilisez les procédures du format et du moteur pour éviter une suppression prématurée.

~~~mermaid
flowchart LR
    S1[Snapshot 1] --> F1[Fichiers version initiale]
    S2[Snapshot 2] --> F2[Fichiers version suivante]
    S3[Snapshot 3] --> F3[Fichiers après mise à jour]
    S1 --> H[Historique de table]
    S2 --> H
    S3 --> H
    H --> C[Catalogue et métadonnées courantes]
~~~

## 7. Évolution de schéma et de partitionnement

Les données changent : de nouveaux champs apparaissent, des champs disparaissent, certains types deviennent plus précis et les partitions sont redessinées. Une bonne architecture de lakehouse doit traiter l’évolution comme une opération versionnée. Les lecteurs existants doivent savoir comment traiter les champs absents, et les producteurs doivent éviter les conversions silencieuses qui transforment la signification d’une colonne.

Apache Iceberg prend en charge plusieurs évolutions de schéma, y compris l’ajout, la suppression, le renommage et certains changements de type, en s’appuyant sur des identifiants de champ dans les métadonnées. Le format suit une spécification; les fonctionnalités utilisables dépendent de la version de la spécification, de la bibliothèque et du moteur qui lit ou écrit la table. Ne supposez pas qu’une modification supportée par un client sera reconnue par tous les consommateurs d’un cluster hétérogène.

L’évolution de partitionnement permet d’adapter une table quand les volumes ou les requêtes changent, sans obliger nécessairement à réécrire tous les fichiers existants. Mais les lecteurs doivent comprendre la façon dont les fichiers historiques sont organisés et le format doit correctement gérer l’union des fichiers. Un changement peut améliorer les futures écritures tout en laissant un historique hétérogène; il faut mesurer ses conséquences et planifier une réorganisation si elle est nécessaire.

Le versionnement de schéma doit être lié aux contrats des consommateurs. Une colonne ajoutée peut être facultative pour les anciens lecteurs; un renommage peut nécessiter une période de coexistence entre l’ancien et le nouveau nom; une modification de type peut impliquer un backfill. Les tests doivent inclure une version ancienne des données, une version nouvelle, les lecteurs attendus et les erreurs de conversion.

Une migration devrait commencer dans un environnement isolé, vérifier la compatibilité de chaque moteur, comparer les résultats avant/après, mesurer la charge et prévoir un retour. Un retour à l’ancienne version du code ne rétablit pas automatiquement la forme physique ou logique des fichiers. Il faut distinguer rollback applicatif, nouvelle version des métadonnées et restauration d’un snapshot.

## 8. Transactions et cohérence d’une table analytique

Un lakehouse vise souvent à fournir des écritures de table atomiques et une lecture cohérente de l’état publié. Ces garanties s’appliquent dans le périmètre du format, de son catalogue et de ses lecteurs/écrivains compatibles. Il ne faut pas conclure que toutes les opérations sur n’importe quel objet de stockage sont transactionnelles. Une écriture directe de fichiers hors du protocole peut laisser des fichiers qui ne font pas partie de la table ou produire une lecture incohérente.

Les charges peuvent être en append, overwrite, merge ou mise à jour de lignes selon les capacités du format et du moteur. Append ajoute de nouveaux enregistrements; overwrite remplace un périmètre défini; merge combine des enregistrements source et cible selon des clés. Une erreur de condition peut remplacer une table entière au lieu de la période attendue. Toute opération d’écriture doit préciser son périmètre, sa clé, les doublons possibles et le traitement des suppressions.

La concurrence entre jobs doit être gérée. Si deux pipelines écrivent dans les mêmes partitions ou les mêmes lignes, le comportement dépend du format, du moteur et de la façon dont les conflits sont résolus. Un système robuste identifie les lots, maintient une frontière de publication, retente uniquement les opérations sûres et vérifie la cohérence après commit. Les retries aveugles peuvent dupliquer les données ou refaire une opération destructive.

Le modèle transactionnel doit aussi intégrer la cohérence avec les systèmes externes. Une table lakehouse peut être mise à jour avant qu’un catalogue métier, un cache ou un rapport soit rafraîchi. La chaîne doit définir l’ordre, la version visible et les contrôles à la fin du lot. Le mot « transactionnel » ne signifie pas que toute l’architecture distribuée participe à une même transaction globale.

## 9. Batch et streaming dans un lakehouse

Les données peuvent arriver par batchs planifiés, par fichiers périodiques ou par événements. Le batch simplifie certaines opérations : un lot possède une frontière, il peut être validé puis publié. Le streaming réduit la latence, mais introduit des événements retardés, des micro-batchs, des états intermédiaires et des opérations de compaction plus fréquentes. Les deux modes peuvent coexister si les écritures vers la même table respectent les règles de concurrence et de commit.

Un événement Kafka peut être écrit vers une zone brute, puis transformé en table silver; un job périodique peut agréger les données en tables gold. Si le traitement de flux utilise un mécanisme de checkpoint, ce checkpoint doit être conservé dans un emplacement durable et isolé pour cette application. Le changement de code ou de schéma peut nécessiter un plan de migration du checkpoint; supprimer celui-ci pour contourner un problème risque de provoquer une relecture ou une perte de progression.

La déduplication des événements doit s’appuyer sur un identifiant stable ou une clé définie. La livraison répétée d’un message ne doit pas nécessairement créer deux lignes dans la table analytique. Selon le moteur, un MERGE ou une déduplication par fenêtre peut être adapté, mais la logique doit couvrir le replay et les événements tardifs. Une déduplication basée uniquement sur l’égalité du contenu peut effacer deux faits légitimes identiques.

L’écriture continue de petits lots peut créer une forte accumulation de petits fichiers et de métadonnées. La compaction doit être coordonnée avec le flux, mesurer le retard, éviter les conflits et ne pas bloquer les lecteurs critiques. Le budget de fraîcheur doit inclure la capture, la transformation, le commit, la compaction éventuelle et la publication des modèles. Une chaîne « temps réel » peut avoir plusieurs minutes de retard si le service ne surveille pas ses étapes.

## 10. Qualité, lignage et gouvernance

Les données brutes, nettoyées et publiées doivent être reliées par un lignage qui explique leur provenance et les transformations appliquées. Un analyste doit pouvoir comprendre d’où provient une colonne, quelle règle lui donne sa valeur, quelle version de code a produit le lot et quelles sources ont contribué. Le lignage est important pour l’investigation, les changements de métrique, les incidents de confidentialité et la correction d’erreurs.

La qualité s’évalue à plusieurs niveaux. À l’arrivée, vérifier le format, le schéma, la taille et la provenance. Après nettoyage, vérifier les types, valeurs autorisées, doublons et relations. Au niveau analytique, vérifier le grain, les agrégats, les périodes et le rapprochement avec la source. À la publication, vérifier la fraîcheur, la complétude du lot et l’existence d’une version validée. Chaque test doit être accompagné d’une décision si le seuil n’est pas respecté.

Les politiques d’accès doivent suivre la classification des données. L’accès brut peut être plus restreint que celui des tables agrégées. Des données personnelles peuvent être masquées, pseudonymisées ou supprimées selon les règles applicables. Les snapshots et sauvegardes historiques peuvent conserver des valeurs qui ont disparu de la table courante; la politique de rétention doit donc prendre en compte la persistance d’historique, pas seulement le dernier état visible.

Le catalogue métier doit définir les propriétaires, le sens des indicateurs, les unités, le public autorisé et le niveau de fraîcheur. La table technique sans description n’est pas un produit analytique complet. La gouvernance ne signifie pas interdire les explorations; elle doit permettre l’expérimentation dans des zones contrôlées et fournir un chemin clair pour promouvoir les datasets vers des modèles partagés et fiables.

## 11. Sécurité, coûts et cycle de vie

Un lac central peut devenir l’un des actifs les plus sensibles de l’organisation parce qu’il réunit des données provenant de nombreuses sources. Il faut contrôler l’identité, les permissions sur les objets et tables, les clés de chiffrement, les accès des moteurs de calcul, les secrets des jobs et les sorties temporaires. Une séparation de comptes et d’environnements réduit le risque qu’un pipeline expérimental écrase des données officielles.

Le chiffrement en transit et au repos doit être coordonné avec la gestion de clés et la reprise. Le contrôle d’accès doit être appliqué au niveau adapté : stockage objet, catalogue, table, rôle de moteur et couche de consommation. Les copies brutes peuvent contenir des champs que les rapports analytiques n’ont pas besoin de montrer. Limitez l’exposition au plus petit périmètre utile.

Les coûts se divisent entre stockage de données, versions historiques, fichiers temporaires, snapshots, requêtes de catalogue, calcul batch, streaming, transfert réseau et compaction. Un stockage « bon marché » peut produire des coûts élevés si les requêtes lisent toutes les partitions, si les fichiers sont trop nombreux ou si les jobs fonctionnent en permanence. Mesurez les octets scannés, la durée, les retries, les fichiers et la consommation de ressources.

La suppression des données inutiles nécessite un protocole. Un fichier peut être référencé par un snapshot historique ou en cours de lecture. Une tâche de nettoyage doit vérifier l’état de la table et utiliser les mécanismes du format pour éviter de supprimer des fichiers qui sont encore nécessaires. Une politique de conservation doit préciser la durée des snapshots, les points de reprise, les données réglementées et la procédure de purge.

## 12. Atelier : modèle lakehouse de progression

Dans un environnement de laboratoire qui dispose de Spark et d’un format de table tel qu’Iceberg, créez une table analytique. La syntaxe exacte dépend de la version et du catalogue configuré; l’objectif est de comprendre les étapes et les contrôles, pas de supposer qu’une configuration unique fonctionne partout.

~~~sql
CREATE TABLE lakehouse_lab.course_attempts (
    attempt_id STRING,
    learner_id STRING,
    course_id STRING,
    event_date DATE,
    score DOUBLE,
    finished BOOLEAN
)
USING iceberg;
~~~

Ajoutez quelques lignes synthétiques, lisez la table, puis calculez un agrégat par cours et date. Vérifiez le nombre de tentatives, le nombre d’apprenants distincts et la moyenne de score. Incluez un score manquant, un doublon volontaire et un événement retardé pour tester la logique. Utilisez un namespace de laboratoire qui ne peut pas être confondu avec la production.

Appliquez ensuite une modification de schéma compatible, comme l’ajout d’un champ source_system. Vérifiez que les anciens fichiers restent lisibles et que les valeurs manquantes ont le comportement attendu. Examinez le catalogue, l’historique de snapshots et le plan d’exécution lorsque les outils de la version le permettent. Comparez les résultats avant et après; le simple fait que la commande ALTER réussisse n’est pas un test complet.

Créez plusieurs fichiers de données ou plusieurs petits lots pour observer le coût de lecture, puis réalisez une compaction via le mécanisme supporté par le moteur ou le format. Vérifiez que les données logiques restent identiques et que le nombre de fichiers physiques évolue comme prévu. Mesurez la durée de compaction, l’espace utilisé et l’effet sur les lectures suivantes.

Enfin, restaurez ou relisez une version antérieure si l’environnement supporte le time travel. Comparez les résultats des deux snapshots et documentez la période de rétention. Ne supposez pas que l’historique restera disponible indéfiniment. La rétention est une propriété opérationnelle à définir, tester et surveiller.

## 13. Exercices corrigés

### Exercice 1 — Le lac a des fichiers, mais aucune table ne les voit

Une tâche a écrit des fichiers Parquet dans un répertoire que l’équipe considère comme une table lakehouse, mais le catalogue ne les référence pas.

**Correction.** L’écriture de fichiers ne constitue pas forcément un commit de table. Les tables lakehouse ont des métadonnées qui déterminent la version logique et les fichiers visibles. Utilisez le protocole du format et du moteur pour publier la table; n’ajoutez pas manuellement des fichiers au répertoire en supposant qu’ils seront reconnus automatiquement.

### Exercice 2 — Des centaines de milliers de petits fichiers

Les jobs produisent beaucoup de petits fichiers, et les requêtes ralentissent même si le volume des données est modeste.

**Correction.** Le coût de métadonnées, d’ouverture et de planification peut dominer. Réduisez le nombre de partitions d’écriture si c’est approprié, compactez les fichiers avec les mécanismes supportés, ajustez le partitionnement et observez la taille moyenne après compaction. Ne remplacez pas le problème par un seul gros fichier qui limiterait le parallélisme.

### Exercice 3 — Migration de schéma

Un moteur récent lit un champ renommé, mais un autre consommateur plus ancien continue à utiliser l’ancien nom.

**Correction.** La compatibilité doit être vérifiée pour tous les lecteurs et écrivains, pas seulement pour le moteur qui a exécuté la migration. Utilisez une période de transition, un champ compatible si nécessaire, un backfill et des tests sur les versions anciennes. Ne supprimez l’ancien champ qu’après avoir observé que les consommateurs dépendants ont migré.

### Exercice 4 — Snapshot supprimé

Une équipe a expiré les snapshots pour économiser l’espace et découvre ensuite qu’elle ne peut plus revenir à une version ancienne.

**Correction.** Le time travel dépend de l’historique et des fichiers conservés. La rétention doit refléter les délais de détection, les besoins d’investigation et les objectifs de reprise. Testez la restauration et établissez une politique explicite; ne supposez pas que l’existence d’un format transactionnel garantit la présence éternelle des anciens états.

### Exercice 5 — Données personnelles dans la zone brute

Une demande de suppression a été exécutée dans la table gold, mais le même identifiant reste dans la zone bronze et dans un snapshot ancien.

**Correction.** La politique doit couvrir les zones brutes, les tables transformées, les snapshots, les exports et les sauvegardes. Il faut définir la rétention, les procédures de purge ou de réapplication des suppressions après restauration, et les droits d’accès aux historiques. La suppression de la table de consommation ne suffit pas si d’autres copies demeurent accessibles.

## 14. Défi final : concevoir un lakehouse gouverné

L’organisation doit intégrer les événements Kafka, les exports des bases relationnelles et les fichiers de partenaires. Elle veut reconstruire les indicateurs des 18 derniers mois, publier des résultats chaque heure, conserver suffisamment d’historique pour investiguer les changements et permettre à plusieurs moteurs analytiques de lire les mêmes tables.

### Correction attendue

1. **Stockage et zones.** Définir une zone brute avec provenance et lot, une zone nettoyée avec schémas et validations, puis des modèles analytiques décrits. Protéger chaque zone selon la classification des données et la politique de rétention.

2. **Format et catalogue.** Choisir un format de table adapté aux moteurs, définir une version de spécification supportée, confirmer la compatibilité des lecteurs et écrivains, et gérer les métadonnées dans un catalogue partagé. Tester la lecture d’un même snapshot depuis les moteurs nécessaires.

3. **Ingestion.** Organiser le chargement initial par période, puis un flux incrémental avec un point de capture fiable. Traiter les doublons, les événements tardifs, les suppressions et les évolutions de schéma. Les lots doivent être rejouables et idempotents.

4. **Modèle analytique.** Définir les grains des tables, les dimensions, les clés, les mesures et les politiques d’évolution historique. Calculer les taux à partir de numérateurs et dénominateurs, et ne pas additionner des ratios.

5. **Publication.** Publier uniquement une version validée, conserver la version précédente tant que les contrôles échouent, exposer la fraîcheur et les limites des rapports. Utiliser les transactions de table du format au lieu d’écrire des fichiers à côté du catalogue.

6. **Maintenance.** Surveiller le nombre et la taille des fichiers, les snapshots, le retard, le coût des requêtes et la durée de compaction. Planifier l’expiration des anciens snapshots en fonction des besoins de reprise, puis tester une restauration avant de raccourcir la rétention.

7. **Gouvernance.** Définir les propriétaires, les droits, le lignage, les contrats de données et les règles de confidentialité. Relier une valeur de rapport à sa source, à la version du code et au lot de données qui l’a produite.

## 15. Contrats de données et gestion des changements

Une table lakehouse est consommée par des équipes qui ne connaissent pas forcément les détails du pipeline qui l’a produite. Un contrat doit préciser les champs, les types, le grain, la clé métier, les règles de nullabilité, la sémantique temporelle, les garanties de fraîcheur et les changements annoncés. Les noms de colonnes ne suffisent pas : une colonne montant peut désigner un montant brut, net, en monnaie locale ou dans une devise normalisée. La signification doit être explicite et versionnée.

Les changements de schéma doivent être évalués en fonction de tous les lecteurs. Ajouter une colonne peut être compatible si les anciens lecteurs l’ignorent, mais un moteur peut ne pas reconnaître la version de spécification ou le type exact. Renommer un champ peut être supporté dans les métadonnées du format tout en posant problème à un outil BI qui a figé le nom. Les tests doivent inclure la compatibilité de table et les rapports réels.

Lorsqu’un champ doit être remplacé, utilisez si nécessaire une période de double écriture ou de coexistence. Publiez le nouveau champ, alimentez-le, vérifiez son contenu, migrez les consommateurs, puis dépréciez l’ancien champ après avoir observé les accès. Ce modèle progressif évite une rupture synchronisée de toutes les équipes. Il suppose toutefois que la règle de conversion est définie et que les deux champs restent cohérents pendant la transition.

La détection d’un changement inattendu à la source doit être automatisée. Un export fournisseur peut ajouter une colonne, renommer un statut, envoyer une date au format différent ou réduire un identifiant à une longueur plus courte. Le pipeline doit signaler le changement, conserver les fichiers bruts et appliquer un choix explicite : accepter, adapter ou bloquer. Un traitement qui ignore silencieusement les nouveaux champs peut continuer à tourner tout en produisant un résultat incomplet.

Les tests doivent être exécutés avant de déclarer la nouvelle version disponible. Vérifiez les types, valeurs limites, valeurs nulles, clés, volume et résultats d’indicateurs. Un contrôle de contrat peut s’exécuter à chaque lot ou chaque livraison de code. Si le contrat est rompu, le lot doit être mis en quarantaine ou publié avec une indication explicite si cette tolérance est autorisée. La décision dépend de la criticité, mais le système ne doit pas confondre « tâche exécutée » et « données validées ».

## 16. Coût, performances et responsabilité d’exploitation

Le coût du lac dépend du stockage, des opérations de catalogue, des lectures facturées, du transfert réseau et des ressources de calcul. Un fichier compressé peut être bon marché à conserver et cher à interroger si toutes les requêtes lisent une grande partie du dataset. L’optimisation nécessite des métriques d’usage : octets scannés, files d’attente, temps de planification, taille moyenne des fichiers, nombre de fichiers, fréquence de compaction et coût par résultat livré.

La séparation du stockage et du calcul permet de dimensionner les ressources selon les besoins, mais elle signifie aussi qu’un calcul peut être lancé sans limite sur un volume massif. Les quotas, budgets, étiquettes de coût et règles de durée de vie des environnements de test aident à contenir les dépenses. Les équipes devraient connaître le coût approximatif d’un job récurrent avant d’augmenter sa fréquence ou de lui ajouter des consommateurs.

L’optimisation doit être liée aux objectifs. Pour un rapport quotidien, économiser 20 % de calcul peut être plus important que gagner dix secondes. Pour un tableau de bord interactif, la latence et le nombre d’octets lus deviennent essentiels. Les petites partitions et index de métadonnées doivent être choisis en fonction des requêtes réellement exécutées, et non uniquement du schéma abstrait.

La maintenance est une responsabilité opérationnelle : compaction, expiration des snapshots, contrôle des fichiers orphelins, rotation des clés, mise à jour des moteurs et tests de restauration. Ces tâches doivent avoir des fenêtres, des métriques de fin, un mécanisme de reprise et un propriétaire. Une tâche de nettoyage qui est planifiée mais jamais contrôlée peut supprimer des points de restauration ou accumuler des fichiers sans que l’équipe s’en rende compte.

## 17. Checklist et synthèse

Un data lake fournit une zone d’atterrissage évolutive pour des formats variés; un lakehouse ajoute la gestion de tables, de métadonnées, de snapshots et d’évolutions de schéma. Le résultat n’est fiable que si les zones ont des garanties explicites, les producteurs respectent les contrats, les consommateurs connaissent la fraîcheur et les changements sont publiés par les mécanismes du format.

Avant la mise en production, vérifiez la compatibilité des versions, les droits, le schéma, l’évolution de partitions, la politique de snapshots, les tests de reprise, la compaction, la rétention et le contrôle d’accès. Documentez qui possède chaque table, quelles transformations la construisent, quels indicateurs en dépendent et comment une anomalie sera corrigée. Un lakehouse est une plateforme de données gouvernée, pas simplement un ensemble de fichiers compressés.

Un parcours d’exploitation mature doit également permettre de répondre rapidement aux questions suivantes : quelle version a été publiée; quelles sources ont contribué à cette version; quelles transformations ont été appliquées; combien de lignes ont été rejetées; quelle période est complète; quelles données sont encore dans la rétention historique; et comment revenir à un état connu sain. Ces réponses doivent provenir de métadonnées et de rapports automatisés plutôt que de la mémoire d’une personne.

## Ressources officielles

- Apache Iceberg, documentation : https://iceberg.apache.org/docs/latest/
- Apache Iceberg, évolution de schéma et partitionnement : https://iceberg.apache.org/docs/latest/evolution/
- Apache Iceberg, spécification : https://iceberg.apache.org/spec/
- Apache Spark, guide SQL : https://spark.apache.org/docs/latest/sql-programming-guide.html
- Apache Parquet, documentation : https://parquet.apache.org/docs/
- Apache Hive, catalogue et metastore : https://hive.apache.org/

Vérifiez toujours la combinaison du format de table, du catalogue, du moteur d’exécution et de la version de bibliothèque. Une propriété supportée par un composant peut ne pas être exposée par tous les connecteurs déployés dans l’organisation.
