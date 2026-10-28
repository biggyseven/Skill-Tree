# Pipelines de données complexes — Expert

> **Mise en contexte.** Skill-Tree reçoit des données depuis sa base relationnelle, des événements Kafka, des fichiers déposés par des partenaires, des API externes et des exports historiques. Les sources n’ont ni les mêmes schémas ni les mêmes rythmes. Certaines livrent un fichier complet une fois par jour, d’autres envoient des événements quelques secondes après l’action, et d’autres corrigent tardivement les valeurs déjà publiées. L’enjeu est de construire des pipelines capables d’ingérer, valider, transformer et publier les données sans perdre d’événements, créer des doublons ou exposer un résultat partiel comme s’il était complet.

## Objectifs et prérequis

Ce cours approfondit les architectures d’ingestion, les chargements batch et incrémentaux, les API et fichiers, les mécanismes de capture de changements (CDC), les points de reprise, l’idempotence, la gestion d’erreurs, les données tardives, l’évolution de schéma, les backfills, la déduplication et l’orchestration. Vous apprendrez à choisir une stratégie selon les sources, à définir un contrat d’ingestion, à construire un traitement rejouable, à séparer données brutes et données validées, et à surveiller la fraîcheur, les rejets et le coût.

Le cours suppose que vous maîtrisez les bases des bases de données, SQL, les APIs, les fichiers structurés et les principes des systèmes distribués. Les exemples utilisent Python, SQL et des commandes shell génériques; ils doivent être adaptés aux bibliothèques, moteurs et plateformes de l’environnement réel. Les commandes qui déplacent, écrasent ou suppriment des fichiers doivent être exécutées dans un laboratoire d’abord. Un pipeline de production doit aussi définir les responsabilités, le traitement des secrets et les règles de rétention.

## 1. Cartographier les sources et le besoin d’ingestion

Avant d’écrire un job, inventoriez chaque source. Documentez son propriétaire, sa finalité, son schéma, sa clé, son mode d’accès, sa fréquence de changement, son volume, son mécanisme d’authentification, ses limites de débit, sa politique de suppression et le niveau de fraîcheur attendu. Une API qui limite les requêtes à quelques centaines par minute n’impose pas le même design qu’un flux CDC avec un débit élevé, ni qu’un dépôt de fichiers qui publie un lot complet à heure fixe.

La méthode d’ingestion doit correspondre au contrat de source. Un chargement batch peut être le meilleur choix lorsque la source publie un fichier complet de façon quotidienne. Une extraction incrémentale basée sur un timestamp peut fonctionner si la source garantit un champ de mise à jour fiable et une stratégie de suppression. CDC peut être nécessaire quand la fenêtre de perte tolérée est faible ou que les requêtes d’extraction lourdes perturbent la base transactionnelle. Une consommation d’événements peut être appropriée lorsque la source fournit déjà un journal durable.

Il faut identifier le point de vérité. Une base relationnelle peut posséder la valeur courante d’une inscription, tandis qu’un topic d’événements conserve chaque transition d’état. Un export mensuel peut être une photographie prise à un instant donné, pas un historique complet. L’ingestion doit savoir si elle reçoit des événements, des états courants ou des snapshots. Sans cette distinction, le pipeline peut additionner des états répétés comme s’il s’agissait de nouvelles opérations.

La fréquence doit être justifiée par le besoin métier. Un dashboard actualisé toutes les nuits ne requiert pas nécessairement une infrastructure de streaming. À l’inverse, un contrôle de sécurité qui détecte des comportements suspects peut avoir besoin d’une latence bien plus faible. Comparez l’impact d’un retard, le coût de calcul, le coût de lecture de la source et la complexité d’exploitation. Une architecture plus rapide n’est pas automatiquement meilleure si elle multiplie les points de panne et n’améliore aucun usage réel.

Une fiche de source devrait documenter au minimum : propriétaire, dataset, clé, format, codage, volume typique, pic, cadence, règle de suppression, schéma, authentification, limite de débit, SLA de disponibilité, délai de récupération et contact d’incident. Cette fiche doit être maintenue avec le pipeline, car la source peut changer de version, d’URL, de pagination ou de fournisseur. L’absence de propriétaire est un risque opérationnel : personne ne saura confirmer si une valeur a changé légitimement.

## 2. Architecture de référence et frontières de publication

Une chaîne d’ingestion comporte généralement acquisition, mise en zone brute, validation technique, normalisation, déduplication, enrichissement, contrôle qualité et publication. Chaque étape doit avoir une entrée et une sortie déterminées. La zone brute préserve l’information reçue et son contexte de capture; la zone nettoyée exprime le schéma canonique; la zone de consommation contient des modèles adaptés à l’usage. Une publication ne doit pas devenir visible avant que les conditions minimales de complétude soient vérifiées.

~~~mermaid
flowchart LR
    A[API, bases, fichiers, Kafka] --> B[Acquisition]
    B --> C[Zone brute avec identifiant de lot]
    C --> D[Validation et normalisation]
    D --> E[Déduplication et enrichissement]
    E --> F[Contrôles de qualité]
    F -->|Validé| G[Zone publiée]
    F -->|Écart| H[Quarantaine]
    H --> I[Correction et rejeu]
    I --> D
    J[Orchestration et point de reprise] --> B
    J --> D
    J --> G
~~~

La zone brute ne doit pas simplement être un dossier « temporaire ». Elle conserve assez de contexte pour permettre une réexécution : source, timestamp de capture, identifiant de lot, version de schéma et éventuellement checksum. Elle doit aussi avoir une rétention et un contrôle d’accès, parce que des données brutes peuvent contenir des informations personnelles, des valeurs invalides ou des champs qui seront supprimés des modèles de consommation.

La zone de publication est une frontière de confiance. Les consommateurs doivent pouvoir identifier la dernière version complète et savoir si le flux est à jour. Une table peut être physiquement présente mais pas encore validée; un fichier peut avoir été écrit par une tâche avant que toutes les autres ne terminent. Publiez avec un identifiant de version, un manifeste, un état de lot ou un mécanisme transactionnel adapté au stockage. Ne laissez pas les clients déduire la complétude à partir de la seule présence d’un répertoire.

Le pipeline doit définir ce qui se passe si l’étape d’acquisition réussit, mais la validation échoue; si les données sont écrites, mais que le curseur ne peut pas être mis à jour; ou si la publication réussit mais que la notification échoue. Un workflow robuste sépare les états « reçu », « validé », « transformé », « publié » et « notifié ». Il peut ensuite reprendre à la bonne frontière au lieu de refaire tout le travail ou de déclarer le lot réussi prématurément.

## 3. Chargement batch : fichiers, snapshots et manifests

Un batch regroupe un ensemble de données associé à une période logique ou une exécution. Il peut s’agir d’un fichier CSV, d’un objet JSON, d’un export Parquet ou d’un dump fourni par un partenaire. L’ingestion doit connaître la convention de nommage, la taille attendue, la structure, le jeu de caractères, les règles d’échappement et le signal qui indique que le lot est complet.

Un fichier publié dans un répertoire peut être partiellement écrit. Le pipeline doit éviter de le lire avant la fin du transfert. Des solutions comprennent un fichier temporaire suivi d’un renommage atomique dans les environnements qui le supportent, un manifeste de livraison, un marqueur de fin ou un protocole de dépôt documenté. Sur le stockage objet, les garanties et opérations diffèrent d’un système POSIX : vérifiez le mécanisme approprié plutôt que de supposer que le renommage a la même sémantique.

Le manifeste associe un batch_id à des fichiers attendus, leurs tailles, éventuellement des checksums et la période couverte. Il permet de détecter un fichier manquant, inattendu ou répété. Le checksum aide à détecter certaines altérations, mais ne prouve pas que le contenu est métier correct. Il faut compléter le contrôle technique par des validations du schéma, des clés, des volumes et de la cohérence.

Le traitement batch doit aussi gérer les fichiers tardifs. Si un partenaire redépose un fichier corrigé pour une période déjà publiée, le pipeline doit savoir s’il remplace le précédent, si les nouvelles lignes complètent le lot ou si le fichier représente une version additive. La date du fichier ne suffit pas toujours à décider. Un identifiant de version et une règle de correction rendent le comportement reproductible.

Ne supprimez pas la preuve brute après la publication avant d’avoir établi la rétention et les besoins de correction. Si un indicateur est erroné, l’équipe peut avoir besoin de reconstruire la transformation à partir de la source originale. L’espace de stockage doit donc être estimé en intégrant les versions de fichiers, les rejets et la période de reprise. Une stratégie de nettoyage est indispensable, mais elle doit suivre la politique et l’état des lots.

## 4. Ingestion d’API : pagination, limites et reprise

Une API d’ingestion exige de comprendre l’authentification, la pagination, le filtrage, les limites de débit et la sémantique des champs. Une réponse contenant 100 lignes peut être une page parmi 50, et l’absence d’erreur HTTP ne prouve pas que toutes les pages ont été lues. Le client doit suivre le curseur ou le lien next selon le contrat, vérifier la fin de pagination et enregistrer la progression.

Les limites de débit doivent être respectées. En cas de réponse 429 ou d’erreur temporaire, un délai de retry avec backoff et jitter peut éviter d’aggraver la saturation. Une stratégie de retry doit être bornée et distinguer les erreurs transitoires des erreurs permanentes. Un HTTP 401 peut indiquer un secret expiré; réessayer cent fois le même secret n’améliore pas la situation et ajoute du bruit aux logs.

Les API paginées peuvent changer pendant l’extraction. Si un nouvel enregistrement apparaît en tête de liste pendant que les pages sont lues, un offset numérique peut causer un doublon ou un saut. Un curseur stable, un timestamp de snapshot ou un mécanisme d’export cohérent est préférable lorsque la source le propose. Si elle ne le propose pas, documentez les limites et prévoyez une fenêtre de chevauchement ainsi qu’une déduplication.

~~~python
import time
import random
import requests

def fetch_page(url, token, params=None, max_attempts=5):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    for attempt in range(max_attempts):
        response = requests.get(url, headers=headers, params=params, timeout=(5, 30))
        if response.status_code == 429 or 500 <= response.status_code < 600:
            if attempt == max_attempts - 1:
                response.raise_for_status()
            retry_after = response.headers.get("Retry-After")
            wait = float(retry_after) if retry_after and retry_after.isdigit() else min(30, 2 ** attempt)
            time.sleep(wait + random.uniform(0, 0.5))
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Aucune réponse exploitable après les tentatives prévues")
~~~

Cet exemple illustre une stratégie de base et doit être adapté au contrat de l’API : certaines sources exposent un champ de délai avec une unité spécifique, un format de pagination ou une politique d’authentification différente. Un token ne doit jamais être affiché en logs. L’ingestion doit enregistrer la page ou le curseur, le nombre d’objets reçus et le timestamp de collecte, pas les secrets ou un payload sensible complet.

L’ingestion doit utiliser un mécanisme de reprise. Enregistrer le curseur après une seule page peut être sûr si cette page a été écrite de façon durable et dédupliquée. Avancer le curseur avant l’écriture peut perdre les données; l’avancer après l’écriture sans déduplication peut faire répéter les données. Une table de suivi de lots ou un checkpoint doit donc être coordonné avec l’écriture ou conçu pour tolérer les reprises.

## 5. Chargements incrémentaux et points de reprise

Un chargement incrémental ne récupère que les changements depuis une position connue. Ce point peut être une date de mise à jour, une clé monotone, un numéro de séquence, un offset d’événement ou un token de reprise fourni par la source. La fiabilité dépend du contrat de ce curseur : peut-il être réutilisé? est-il stable après un changement de schéma? peut-il représenter plusieurs modifications avec la même valeur? inclut-il les suppressions?

Un filtre WHERE updated_at > last_timestamp peut manquer des changements si plusieurs lignes partagent la même date et que la limite est mise à jour au mauvais moment. Une approche de chevauchement lit quelques minutes avant la dernière position puis déduplique avec une clé stable. Une autre utilise un couple timestamp et identifiant. La meilleure approche est celle qui respecte la sémantique de la source et est validée par des tests d’interruption et de mise à jour concurrente.

Le curseur doit être enregistré après que les données correspondantes ont été acceptées par la destination. Si le lot contient des rejets, il faut décider si le curseur peut avancer : souvent il peut avancer si les rejets sont conservés dans une quarantaine durable et que le lot est marqué comme ayant des erreurs, mais il ne doit pas oublier les enregistrements. L’état de progression doit représenter exactement ce qui a été pris en charge, pas seulement la dernière requête réussie.

Une reprise idempotente peut être réalisée avec une clé stable et un UPSERT, un MERGE, une contrainte unique ou une table de staging. Si le même lot est traité deux fois, l’état final devrait être identique, sauf si le contrat prévoit une nouvelle version. Évitez un append aveugle qui double les données à chaque reprise. Le mécanisme exact dépend du stockage, mais les tests doivent prouver le comportement.

Les points de reprise doivent être protégés et versionnés. Si un checkpoint est effacé, le pipeline peut repartir de zéro, reprendre trop loin ou perdre sa relation avec les sorties déjà publiées. Un changement majeur du modèle peut nécessiter de recréer un point de reprise, mais cette action doit être accompagnée d’un plan de backfill, de déduplication et de comparaison de résultats.

## 6. CDC : capturer les changements transactionnels

Change Data Capture capture les changements d’une source, souvent à partir de journaux transactionnels ou d’un mécanisme natif. Le CDC peut limiter les extractions lourdes et réduire la latence. Il faut toutefois comprendre son ordre, ses garanties, le format des événements, la gestion des suppressions, les mises à jour de schéma et la manière dont le point de lecture est conservé. Un connecteur qui tombe pendant un long intervalle doit pouvoir reprendre sans sauter d’événements, selon le contrat du système.

Les événements CDC peuvent représenter une insertion, une mise à jour ou une suppression. Une mise à jour peut inclure seulement les champs modifiés ou l’image complète, selon le système et sa configuration. Le consommateur doit comprendre la différence entre un événement de changement et une ligne d’état courant. Appliquer des événements dans le mauvais ordre peut faire revenir une valeur à un état ancien si les positions ou versions ne sont pas prises en compte.

Une capture de suppression est essentielle pour synchroniser un modèle courant. Si le pipeline extrait seulement les lignes qui existent à la source, il ne sait pas qu’une ligne a disparu. Un tombstone, un journal de changement ou une réconciliation par snapshot peut signaler cette suppression. Le stockage analytique doit décider si la ligne est supprimée, marquée inactive ou conservée dans l’histoire selon la sémantique métier.

Le CDC peut avoir un retard important. Mesurez la position de source, la position traitée et l’heure de dernière publication. Un connecteur peut être connecté mais bloqué sur une erreur de schéma ou limité par la capacité de destination. Le statut « running » ne prouve pas que toutes les données progressent. Les alertes doivent suivre le retard et la capacité de rattrapage.

Le changement de schéma est une responsabilité partagée. Si la source supprime une colonne dont un consommateur dépend, le flux peut échouer ou produire une forme inattendue. Une procédure devrait capturer les changements de DDL, tester leur compatibilité, déployer les consommateurs et conserver une période de transition. Les transformations doivent être capables de signaler les champs inconnus et absents; il ne faut pas convertir silencieusement une rupture de contrat en NULL.

## 7. Déduplication et idempotence

La déduplication dépend du grain et de l’identité métier. Deux événements identiques en contenu peuvent représenter deux opérations légitimes; deux événements avec des timestamps différents peuvent être des doublons d’une même opération après un retry. La clé de déduplication doit venir du contrat : event_id, attempt_id et version, identifiant de transaction ou combinaison stable explicitement définie.

Il faut distinguer déduplication d’événement et réconciliation d’état. Un flux d’événements peut avoir besoin de conserver chaque occurrence et d’éviter uniquement les duplications techniques. Un modèle d’état courant peut appliquer le dernier changement par clé. Dans ce second cas, il faut un ordre ou une version de source suffisamment fiable pour choisir la valeur la plus récente. Utiliser simplement l’heure d’arrivée peut être incorrect lorsque les événements sont retardés.

L’idempotence assure qu’un même lot ou événement peut être rejoué sans produire de doublon logique. Elle peut s’appuyer sur une contrainte unique dans la destination, un MERGE sur une clé, une table des événements consommés et une transaction, ou une stratégie de fichiers et de manifests versionnés. L’idempotence doit être testée sur une panne simulée entre l’écriture des données et la mise à jour du checkpoint.

Un pipeline ne doit pas supposer que les retries ne seront jamais répétés. Les systèmes distribués peuvent perdre une réponse après une opération réussie. L’appelant réessaie alors, même si la première opération a été appliquée. Une API externe peut exiger une clé d’idempotence distincte. Le contrat doit détailler quelles opérations sont réessayables, quelles erreurs sont définitives et comment un traitement manuel évite de dupliquer des effets externes.

La déduplication peut elle-même être coûteuse. Une recherche de doublons dans plusieurs milliards de lignes demande un partitionnement ou une stratégie de fenêtre adaptée. Si la source possède une clé stable, il est préférable de l’exploiter au fil de l’ingestion plutôt que de reparcourir périodiquement tout l’historique. Si la clé est absente, il faut définir les limites du rapprochement et la manière de traiter les collisions.

## 8. Gestion des erreurs, quarantaines et rejeu

Une donnée mal formée doit être traitée selon une stratégie explicite. La rejeter sans trace fait perdre l’information; interrompre tout le flux peut bloquer les données valides; la convertir arbitrairement en une valeur par défaut peut contaminer les indicateurs. Une zone de quarantaine conserve la donnée ou une représentation protégée, la raison du rejet, la source, le lot, la version de schéma et le contexte nécessaire à la correction.

La quarantaine doit rester sécurisée. Les payloads peuvent contenir des secrets ou des données personnelles. Il faut limiter l’accès, masquer les champs inutiles et définir une durée de rétention. Les logs ne doivent pas copier intégralement des événements sensibles simplement parce qu’ils sont invalides. L’équipe doit pouvoir diagnostiquer la cause sans augmenter le risque d’exposition.

Chaque catégorie d’erreur doit avoir une politique. Une panne réseau temporaire peut être réessayée avec backoff; une erreur d’authentification nécessite une correction des secrets; un schéma inconnu peut bloquer un lot jusqu’à l’approbation; une ligne avec une clé étrangère inconnue peut être mise en attente; un enregistrement définitivement invalide peut être rejeté après validation de sa sémantique. Les tentatives doivent être bornées et les erreurs critiques doivent déclencher une alerte.

Le rejeu est une opération contrôlée, non un simple relancement de job. Identifiez le périmètre, la version de transformation, la source originale, les effets déjà appliqués et la cible. Assurez-vous que les clés d’idempotence empêchent les doublons, ou écrivez dans une table de staging avant de remplacer une partition. Si les indicateurs officiels sont publiés pendant le backfill, prévoyez un point de bascule pour éviter que les utilisateurs voient un mélange de versions.

Un rapport de rejeu doit indiquer l’identifiant de l’incident, la période, les entrées, les sorties, les lignes ajoutées, modifiées et rejetées, les contrôles réalisés et la date de publication. Une fois le résultat validé, documentez la cause et ajoutez un test qui détecte le problème à l’avenir. La résolution n’est pas achevée tant que la même erreur peut se reproduire sans alerte.

## 9. Orchestration et dépendances entre tâches

L’orchestrateur planifie les jobs, gère les dépendances, les paramètres, les fenêtres, les retries et les alertes. Il doit représenter la date logique du traitement et la version de code, pas seulement l’heure d’exécution. Un job du 1er octobre relancé le 10 octobre doit reconstruire la même période logique ou documenter explicitement pourquoi il utilise les données actuelles.

~~~mermaid
flowchart TD
    A[Détecter une livraison] --> B[Valider le manifeste]
    B --> C[Ingestion brute]
    C --> D[Contrôle du schéma]
    D --> E[Normaliser et dédupliquer]
    E --> F[Contrôles qualité]
    F -->|Succès| G[Publier version]
    F -->|Échec critique| H[Quarantaine et alerte]
    H --> I[Corriger la source ou la règle]
    I --> E
    G --> J[Notifier et enregistrer le lot]
~~~

Les dépendances doivent porter sur des états explicites. Une tâche ne doit pas commencer parce que le job précédent a simplement lancé un processus; elle doit commencer lorsque sa sortie requise est durable et validée. Si plusieurs sources alimentent une table, l’orchestrateur doit vérifier que toutes les sources attendues sont arrivées ou publier un statut partiel autorisé. L’absence d’une source peut être un retard ou un changement de contrat, ce qui exige une décision.

Les retries doivent être ciblés. Une tâche qui échoue sur une erreur de validation ne gagnera rien à être répétée sans changement. Une tâche qui échoue pour un timeout temporaire peut être relancée. Les politiques doivent distinguer retry, reprise au checkpoint et backfill. Les logs doivent relier les tentatives au même identifiant de lot afin de suivre la chronologie et éviter la confusion entre exécutions.

Un pipeline complexe gagne à être découpé en étapes testables : extraction, validation, transformation, publication et notification. Il faut éviter les tâches gigantesques qui combinent appels externes, dédupe et écriture métier sans points de reprise. Le découpage ne doit cependant pas multiplier inutilement les écritures intermédiaires. L’architecture doit équilibrer la reprise, la performance, la visibilité et le coût.

## 10. Backfill et corrections historiques

Un backfill recalculé sur une période historique est nécessaire lorsqu’une source corrige des valeurs, une règle de transformation change ou un incident a affecté les données. Il peut traiter un grand volume tout en coexistant avec les écritures courantes. La stratégie doit définir le périmètre de date, la version de code, la source utilisée, le mécanisme de déduplication et la manière de publier un résultat cohérent.

Avant le backfill, prenez une mesure de référence : nombres de lignes, sommes, distributions, taux et version courante. Écrivez le résultat du backfill dans une zone isolée ou une table temporaire, puis comparez-le aux données existantes. Si la transformation corrige une règle métier, certains changements sont attendus; ils doivent être expliqués et validés, pas annulés simplement parce que les nombres diffèrent.

Les partitions temporelles peuvent faciliter un backfill ciblé. Si la table est partitionnée par date de l’événement, le traitement peut recalculer uniquement les partitions touchées. Cependant, un événement modifié peut changer de date ou d’identité, auquel cas une simple réécriture d’une seule partition peut laisser une ancienne ligne dans l’autre. Il faut traiter à la fois la clé et l’ancienne position. Le modèle doit définir comment gérer les changements de partition.

La publication d’un backfill peut être progressive si les consommateurs savent quelles périodes sont corrigées. Pour un indicateur officiel, il faut éviter de présenter un mélange de versions sans l’indiquer. Une méthode consiste à construire une nouvelle table ou un nouveau snapshot, valider les résultats, puis basculer la référence vers la version complète. La capacité à revenir à la version antérieure doit être testée et conservée pendant la fenêtre convenue.

Le backfill doit être rejouable. La même exécution avec les mêmes entrées et le même code doit produire un résultat cohérent, sauf s’il dépend de sources qui ont changé. Enregistrez l’identifiant de lot, le commit, les versions de schéma, les paramètres et les snapshots sources. Cela permet d’expliquer un écart et de reconstruire un traitement si nécessaire.

## 11. Évolution de schéma et compatibilité

Les schémas changent au fil du développement. Un producteur ajoute un champ, renomme une colonne, change un type ou modifie une énumération de valeurs. Le pipeline doit détecter le changement et en évaluer la compatibilité. Une simple acceptation automatique de tout champ nouveau peut rendre le système plus flexible, mais aussi masquer une rupture de sens.

Les changements additifs sont souvent plus simples lorsqu’un champ reste facultatif pour les anciens consommateurs. Les changements de suppression ou de type nécessitent une transition. Une stratégie courante consiste à déployer un lecteur capable de lire les deux formes, déployer le producteur de nouvelle forme, backfiller les historiques, puis retirer l’ancienne forme après vérification des usages. La compatibilité doit être évaluée pour tous les consommateurs, pas seulement le pipeline qui reçoit la source.

Les valeurs inconnues doivent avoir une politique. Si un nouveau statut arrive, le consommateur peut le rejeter, le conserver dans une zone brute ou l’associer à une catégorie « inconnu » selon le contrat. La conversion en « succès » ou « échec » par défaut peut fausser les résultats. L’équipe doit être alertée, comprendre le sens du nouveau statut et versionner la règle si nécessaire.

Les migrations de schéma doivent être testées sur des échantillons anciens et nouveaux, avec plusieurs versions de lecteur. Les tests incluent les champs manquants, les valeurs nulles, les types incompatibles et les grands volumes. Il faut également vérifier la performance : un nouveau champ peut déclencher une transformation coûteuse ou invalider une optimisation d’index et de partitionnement.

## 12. Observabilité : fraîcheur, volume, qualité et coût

La supervision d’un pipeline doit mesurer plus que son statut de processus. Elle doit observer le volume lu, écrit, rejeté, dédupliqué, le temps par étape, le dernier timestamp source, le dernier timestamp traité, la dernière publication complète, le retard, le coût et le taux de reprise. Ces métriques permettent de distinguer une source silencieuse d’un job bloqué ou d’un retard de publication.

La fraîcheur peut se mesurer par la différence entre event_time ou source_updated_at et le moment où le résultat est publié. Il faut s’assurer que les horloges et fuseaux sont compris. Les données peuvent arriver avec plusieurs heures de retard tout en étant correctement traitées; le rapport doit distinguer le retard de source et le temps de calcul.

Le nombre de lignes rejetées doit être vu dans son contexte. Une hausse d’un rejet pour un champ facultatif n’est pas équivalente à une hausse des résultats d’examen sans clé de cours. Les règles doivent classifier les erreurs et produire une alerte adaptée à leur criticité. Les tableaux de bord devraient montrer le nombre et le ratio de rejets, ainsi que l’âge du plus ancien enregistrement en quarantaine.

La supervision doit suivre le coût : requêtes API, octets transférés, volume d’écriture, fichiers créés, CPU et mémoire, temps de stockage, nombre de retries et durée de backfill. Un job peut techniquement réussir tout en consommant dix fois plus de ressources après un changement de schéma. Les seuils de coût doivent déclencher une enquête et aider à identifier les régressions.

Un runbook accompagne les alertes. Il décrit le symptôme, les métriques à regarder, les tests non destructifs, la personne à prévenir et les opérations qui nécessitent une autorisation. Les interventions doivent être journalisées. Une alerte sans propriétaire et sans procédure devient un bruit que l’équipe finit par ignorer.

## 13. Atelier pratique : ingestion idempotente

Créez une table de suivi des lots et une table de destination dans un environnement de laboratoire. Un lot possède un batch_id, la source et un état. Les lignes de destination utilisent un identifiant métier unique. Le but est de démontrer qu’un même lot peut être relancé sans dupliquer les données.

~~~sql
CREATE TABLE ingestion_batches (
    batch_id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    status TEXT NOT NULL,
    rows_received INTEGER NOT NULL DEFAULT 0,
    rows_rejected INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ
);

CREATE TABLE incoming_attempts (
    attempt_id TEXT PRIMARY KEY,
    learner_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    score NUMERIC(5,2),
    source_updated_at TIMESTAMPTZ NOT NULL,
    batch_id TEXT NOT NULL REFERENCES ingestion_batches(batch_id)
);
~~~

Insérez un lot de laboratoire, puis trois tentatives synthétiques. Relancez le même fichier avec l’une des mêmes tentatives et vérifiez que l’identifiant primaire empêche le doublon. Dans un vrai pipeline, il faudrait déterminer si la ligne répétée est strictement identique, si elle met à jour une version précédente ou si elle entre en conflit. La contrainte détecte la collision, mais le traitement de résolution appartient au contrat métier.

Simulez ensuite une erreur après l’écriture des lignes mais avant la mise à jour du statut du lot. Redémarrez le traitement avec le même batch_id. Le pipeline doit constater les lignes déjà écrites et terminer le lot de façon cohérente, ou les remplacer via une procédure idempotente. Ajoutez une règle de validation pour les scores, placez une ligne invalide en quarantaine et assurez-vous que rows_rejected est mis à jour.

Enfin, construisez un rapport de lot qui affiche le nombre reçu, accepté, rejeté, le nombre de clés distinctes et l’état de publication. N’autorisez pas le statut publié si les contrôles requis ne sont pas terminés. Si une stratégie autorise une publication partielle, l’état et les limites doivent être exposés au consommateur.

## 14. Exercices corrigés

### Exercice 1 — API paginée

L’API renvoie 100 enregistrements par page. Le job a réussi mais n’a importé que 100 lignes alors que la source compte plusieurs milliers de lignes.

**Correction.** Vérifiez la logique de pagination, le curseur suivant, la condition d’arrêt et les erreurs de page. Le statut HTTP 200 de la première requête ne garantit pas la complétude de l’extraction. Ajoutez un compteur des pages, le nombre d’objets reçus et un test avec plusieurs pages. Enregistrez le point de reprise seulement après l’écriture de la page et son contrôle.

### Exercice 2 — Doublons après un retry

Une tâche a écrit les lignes, puis perdu la connexion avant de recevoir la confirmation. Elle a relancé tout le lot et doublé les enregistrements.

**Correction.** La destination doit avoir un mécanisme idempotent : clé unique stable, UPSERT/MERGE ou publication versionnée. Le retry doit utiliser le même batch_id et la même clé de source. Testez explicitement la panne entre écriture et confirmation. Le code ne doit pas considérer un timeout comme la preuve que l’opération n’a pas eu lieu.

### Exercice 3 — Suppression non détectée

Un chargement incrémental utilise updated_at et ne récupère que les lignes présentes. Les lignes supprimées à la source restent dans le modèle cible.

**Correction.** Un filtre sur les lignes courantes ne révèle pas une suppression physique. Utilisez CDC, des tombstones, une table de suppressions ou une comparaison de snapshots selon la source. Définissez si la suppression doit retirer la ligne, la désactiver ou conserver l’historique. Testez ce chemin dans un environnement de laboratoire.

### Exercice 4 — Événement en retard

Un résultat d’examen arrive deux jours après la date de l’événement et modifie l’indicateur du mois précédent.

**Correction.** Le pipeline doit distinguer event_time et processing_time, accepter les événements tardifs selon la règle du contrat et recalculer la période affectée. Les tableaux de bord doivent indiquer la fraîcheur et les corrections tardives. Un watermark ou une fermeture de période doit être choisi selon le besoin métier, pas par défaut technique.

### Exercice 5 — Schéma source modifié

Le fournisseur remplace le champ status par state et ajoute une nouvelle valeur « pending_review ».

**Correction.** Conservez la donnée brute, détectez le changement de schéma, évaluez la sémantique et mettez à jour le mapping après validation. Le nouveau statut ne doit pas être converti silencieusement en réussite ou échec. Déployez un consommateur compatible, testez l’historique et documentez la version de contrat.

## 15. Défi final : ingestion multi-source de progression

Concevez une chaîne qui reçoit les inscriptions depuis PostgreSQL via CDC, les tentatives d’examen depuis Kafka et un fichier de certificats fourni chaque nuit par un partenaire. Le dashboard est actualisé chaque heure. Les événements peuvent être doublonnés, les fichiers peuvent arriver tardivement et les certificats peuvent être corrigés.

### Correction attendue

1. **Contrats.** Définir l’identifiant stable, le grain, le schéma, la sémantique du temps et la règle de suppression pour chacune des sources. Documenter la cadence, les propriétaires, les limites et la politique d’évolution.

2. **Acquisition.** CDC pour les changements relationnels, consommation par offset pour les tentatives Kafka et ingestion du manifeste du fichier partenaire. Chaque source conserve un point de reprise spécifique et un identifiant de lot.

3. **Zone brute.** Écrire les données reçues avec source, horodatage de capture, version du schéma, checksum du fichier si applicable et identifiant de lot. Contrôler les accès et la rétention.

4. **Normalisation.** Convertir les types, normaliser les horodatages et les statuts, traiter les suppressions et résoudre les clés. Les champs inconnus doivent être détectés. Les transformations doivent être versionnées.

5. **Déduplication.** Utiliser l’identifiant de tentative ou de certificat défini par le producteur. La même livraison doit être rejouable sans créer une seconde ligne logique. Pour les corrections, conserver la règle de version ou l’historique approprié.

6. **Qualité.** Vérifier les clés, les références, la complétude, les valeurs de score, la cohérence des périodes, la présence du manifeste et le rapprochement des volumes. Rejeter ou mettre en quarantaine les lignes invalides sans les perdre.

7. **Publication.** Publier une version seulement après les contrôles. Indiquer la fraîcheur de chaque source et le statut de complétude. Ne pas prétendre que l’ensemble est complet si le fichier de certificats attendu n’est pas arrivé, sauf politique explicite de publication partielle.

8. **Reprise.** Tester une panne après écriture, un offset non commité, un fichier tardif, un doublon, une suppression et un changement de schéma. Mesurer le temps de rattrapage et vérifier l’absence de pertes et de duplications.

9. **Gouvernance.** Attribuer les propriétaires, protéger les secrets, classifier les données personnelles, définir la rétention et relier le dashboard au lignage des trois sources. Les changements contractuels doivent être annoncés aux consommateurs.

## 16. Checklist et synthèse

Un pipeline d’ingestion fiable sait ce qu’il reçoit, ce qu’une ligne signifie, comment détecter une livraison complète, comment enregistrer un point de reprise, comment traiter les doublons et comment décider qu’une version est publiée. Il préserve la provenance, sépare données brutes et données validées, rend les erreurs observables et possède un mécanisme de rejeu. La source ne doit pas être surchargée par une extraction mal planifiée, et ses limites de débit doivent être respectées.

L’idempotence, la gestion des erreurs, le backfill et l’évolution de schéma sont des propriétés centrales. Les retries peuvent répéter des opérations; les API peuvent changer; les événements peuvent arriver tard; les suppressions ne sont pas visibles dans toutes les stratégies d’extraction. Chaque comportement doit avoir une règle testée. Une exécution sans exception ne prouve pas que les données sont complètes, correctes ou publiées au bon point.

Avant la mise en production, testez les échecs entre toutes les frontières importantes : acquisition et écriture brute, écriture et checkpoint, transformation et validation, validation et publication, publication et notification. Mesurez volume, retards, rejets, coûts et temps de reprise. Attribuez un propriétaire à chaque source, contrat et pipeline. Le système sera plus facile à exploiter si ses états sont explicites et les reprises reproductibles.

## Ressources officielles

- Apache Kafka, documentation : https://kafka.apache.org/documentation/
- PostgreSQL, réplication logique : https://www.postgresql.org/docs/current/logical-replication.html
- Apache Airflow, concepts : https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/
- Apache Spark, Structured Streaming : https://spark.apache.org/docs/latest/streaming/index.html
- OpenLineage, spécification : https://openlineage.io/docs/
- Great Expectations, validations de données : https://docs.greatexpectations.io/

Chaque connecteur et moteur présente des particularités de reprise, d’ordre et d’idempotence. Validez les exemples dans la version et la plateforme utilisées, et formalisez ce qu’une réussite d’ingestion garantit aux consommateurs.
