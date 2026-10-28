# Kafka et traitement en temps réel — Expert

> **Mise en contexte.** Skill-Tree doit réagir à un grand nombre d’événements : une tentative d’examen est terminée, une progression est validée, un certificat est généré, une page de cours est consultée ou un paiement est confirmé. Les équipes veulent produire des tableaux de bord quasi temps réel, mettre à jour des systèmes secondaires et détecter des anomalies sans obliger chaque application à appeler directement toutes les autres. Apache Kafka peut organiser ces événements comme un journal distribué durable. Mais il ne transforme pas automatiquement un traitement en système fiable : les clés, les partitions, les offsets, les schémas, les reprises et les effets secondaires doivent être conçus explicitement.

## Objectifs et prérequis

Ce cours traite du modèle de journal distribué Kafka, des brokers, topics, partitions et répliques, des producteurs, des consommateurs et groupes de consommateurs, de la gestion des offsets, de la sémantique de livraison, de l’ordre par clé, de la rétention, de la compaction, de la compatibilité des schémas, du traitement événementiel et de l’observabilité. Vous apprendrez à distinguer le stockage de messages du calcul de flux, à raisonner sur le lag, à concevoir un consommateur rejouable et à choisir les garanties appropriées en fonction de la valeur métier des événements.

Le cours suppose une connaissance des files de messages, des API, des transactions, des formats de données et de la programmation événementielle. Les commandes Kafka indiquées sont des exemples pour un environnement de laboratoire; les chemins, options, noms de scripts et modes d’authentification varient selon la distribution. N’exécutez pas de commande de suppression ou de réinitialisation d’offset sur un cluster partagé sans confirmation du périmètre et sans plan de retour.

## 1. Event streaming : le changement de modèle

Un événement représente un fait qui s’est produit : une tentative est terminée, une inscription est confirmée, un paiement a été accepté ou un cours est publié. Un événement devrait être nommé au passé lorsque c’est un fait accompli; une commande, elle, demande à un système d’effectuer une action. Confondre commande et événement peut créer des doubles exécutions ou un historique qui prétend qu’une action a réussi alors qu’elle n’a été que demandée.

Une architecture synchrone relie directement les services. Lorsqu’un service A doit prévenir B, C et D, il peut les appeler à la suite. Cette approche est simple dans certains contextes, mais elle lie la disponibilité et la latence du producteur à ses dépendances. Le streaming permet au producteur de publier un événement dans un journal partagé; plusieurs consommateurs le lisent selon leur cadence et leur propre progression. Cela réduit certains couplages temporels, mais déplace la complexité vers les retards, l’idempotence, les erreurs et la cohérence éventuelle.

Un journal d’événements conserve les enregistrements dans un ordre par partition. Les consommateurs peuvent lire les données à leur rythme et, si la rétention le permet, rejouer un historique. Cette capacité est différente d’une file traditionnelle dans laquelle les messages sont souvent retirés de la file une fois traités. Kafka conserve généralement les enregistrements selon une politique de rétention ou de compaction, et les offsets des consommateurs indiquent leur position plutôt que de supprimer automatiquement le message après chaque lecture.

Les événements sont utiles pour alimenter plusieurs vues : un service de progression, un tableau de bord, un détecteur d’anomalies et un entrepôt analytique peuvent consommer le même topic. Cependant, chacun doit avoir une finalité et une stratégie d’erreur. Si un consommateur est lent, son retard peut augmenter sans bloquer tous les autres. Si un événement est invalide, la stratégie de mise en quarantaine doit empêcher qu’une seule ligne mal formée provoque une boucle d’échec infinie.

## 2. Brokers, topics et partitions

Kafka organise les événements dans des topics, eux-mêmes découpés en partitions. Une partition est un journal ordonné. Chaque enregistrement dans une partition possède un offset qui permet d’identifier sa position. Le cluster répartit les partitions sur plusieurs brokers afin de distribuer le stockage et la charge. Les répliques peuvent protéger contre la perte d’un broker, selon le facteur de réplication, l’état des répliques et la configuration de production.

L’ordre total n’est garanti qu’à l’intérieur d’une partition, pas automatiquement entre toutes les partitions d’un topic. Si les événements liés à un même apprenant doivent être traités dans l’ordre, il est fréquent d’utiliser un identifiant d’apprenant comme clé, afin que ces événements soient affectés à la même partition. Il faut toutefois vérifier les règles de partitionnement, l’évolution du nombre de partitions et les besoins de répartition de charge. Une clé très populaire peut concentrer une grande partie du trafic sur une partition.

La clé n’est pas un champ décoratif. Elle exprime la dimension autour de laquelle l’ordre ou la localité est important. Une clé de cours peut rassembler les mises à jour de contenu d’un cours; une clé d’apprenant peut ordonner les événements du compte. Une clé vide ou une distribution aléatoire peut aider la répartition, mais ne garantit pas le traitement ordonné de toutes les mises à jour d’un même objet.

Le nombre de partitions influence le parallélisme maximum de certains groupes de consommateurs, la distribution du stockage et le coût de métadonnées. Augmenter les partitions après le déploiement peut changer la distribution des clés et compliquer l’ordre historique. Il ne faut pas augmenter ce nombre uniquement pour corriger un lag sans déterminer si les consommateurs, les brokers, le réseau ou la logique de traitement constituent le goulot d’étranglement.

~~~mermaid
flowchart LR
    P[Producteurs] --> T[Topic événements]
    T --> B1[Partition 0]
    T --> B2[Partition 1]
    T --> B3[Partition 2]
    B1 --> C1[Consommateur A]
    B2 --> C2[Consommateur B]
    B3 --> C3[Consommateur C]
    C1 --> S[Services et stockage]
    C2 --> S
    C3 --> S
~~~

La réplication doit être configurée avec une tolérance à la panne définie. Le facteur de réplication seul ne suffit pas; le choix du nombre de répliques synchronisées requis pour confirmer une écriture, le placement dans les domaines de panne et la politique d’élection influencent la garantie. Les valeurs exactes doivent être choisies en fonction de la topologie réelle, de la criticité des données et des recommandations de la version déployée.

## 3. Producteur : clés, confirmations et idempotence

Le producteur sérialise l’événement, choisit un topic et une clé, puis envoie l’enregistrement au cluster. Un événement devrait posséder un identifiant stable, un type, un timestamp métier, un identifiant de corrélation et une version de schéma lorsqu’ils sont nécessaires. Les données sensibles doivent être minimisées avant publication; un topic d’événements ne doit pas devenir un canal où toute l’application copie arbitrairement des informations personnelles.

Le niveau d’accusé de réception détermine quand le producteur considère l’écriture confirmée. Les configurations qui attendent un accusé du leader seulement n’offrent pas les mêmes garanties qu’une configuration qui attend les répliques synchronisées requises. Si le producteur reçoit un timeout, il peut être impossible de savoir immédiatement si le message a été écrit mais que la réponse s’est perdue. Une nouvelle tentative peut alors produire un doublon, sauf mécanisme de déduplication ou de production idempotente pris en charge.

L’idempotence du producteur Kafka aide à éviter certains doublons dus aux retries dans le protocole producteur. Elle ne rend pas automatiquement idempotente toute l’application. Si le service métier traite deux fois une même demande et crée deux événements possédant des identifiants différents, Kafka ne peut pas déterminer que ces événements représentent le même fait. Le producteur doit définir un contrat d’événement et l’application doit gérer les clés de déduplication lorsque le domaine l’exige.

Les confirmations doivent être choisies selon la valeur de l’événement. Un compteur temporaire de consultation n’a pas les mêmes exigences qu’un résultat de certification ou une opération financière. Les paramètres de durabilité, la disponibilité du cluster, le délai de confirmation et la capacité de réessai font partie d’un contrat de service. Les équipes doivent tester les pannes de broker et de réseau pour comprendre les limites réellement observées.

Une erreur de sérialisation ou de validation doit être traitée avant publication. Le producteur doit éviter de réessayer indéfiniment une donnée définitivement invalide. Une politique peut envoyer l’événement vers une file de rejet ou un stockage d’échec, mais cette voie doit préserver le contexte nécessaire à la correction et protéger les données sensibles. Le nombre d’événements rejetés et leur âge doivent être supervisés.

## 4. Consommateurs, groupes et offsets

Un consommateur lit les partitions à partir d’une position. Les groupes de consommateurs permettent de répartir les partitions entre plusieurs membres; dans un groupe, chaque partition est généralement assignée à un seul membre à la fois. Le parallélisme d’un groupe est borné par le nombre de partitions affectées et les autres contraintes d’exécution. Ajouter des consommateurs au-delà du nombre de partitions peut n’apporter aucun gain pour ce topic.

L’offset indique la position du consommateur dans une partition. Le commit d’offset indique où le traitement considère sa progression validée, mais il ne garantit pas à lui seul que l’effet métier est durable. Si le consommateur commit l’offset avant d’écrire le résultat, une panne entre les deux étapes peut faire perdre l’effet attendu lors du redémarrage. S’il écrit le résultat puis échoue avant le commit, l’événement peut être relu et le résultat appliqué une seconde fois. L’ordre des opérations et la stratégie de déduplication sont essentiels.

Les commits automatiques simplifient certains scénarios, mais peuvent être inadéquats pour des traitements où il faut coordonner l’écriture du résultat et l’avancement de l’offset. Une stratégie manuelle donne un contrôle plus explicite, mais demande une logique de commit correcte, des tests des interruptions et une gestion des erreurs. Le consommateur doit décider quoi faire d’un événement invalide, d’une erreur temporaire de stockage, d’une erreur métier permanente ou d’une panne après écriture.

Lorsqu’un membre quitte le groupe ou qu’un nouveau consommateur arrive, des partitions peuvent être réassignées. Les tâches en cours doivent être gérées proprement; la logique ne doit pas supposer qu’un consommateur garde une partition indéfiniment. Une réassignation trop fréquente peut ralentir le traitement et augmenter le risque d’événements relus. Les heartbeats, les timeouts, la durée de traitement et les paramètres de poll doivent être adaptés au profil du job.

## 5. At-most-once, at-least-once et exactly-once

La sémantique at-most-once privilégie l’absence de doublons et accepte un risque de perte si l’offset est avancé avant la réussite du traitement. La sémantique at-least-once privilégie le fait de ne pas perdre un événement traité par erreur, mais peut entraîner des doublons lors des retries ou après une panne. Exactly-once cherche à garantir que le résultat logique est appliqué une seule fois dans le périmètre couvert par la transaction et les mécanismes utilisés.

Il faut éviter d’utiliser ces termes sans préciser le périmètre. Le broker peut fournir des primitives transactionnelles et des mécanismes de producteur idempotent; le traitement de flux peut coordonner les offsets consommés et les sorties Kafka dans une transaction. Mais si le consommateur écrit dans une base externe, envoie un courriel ou appelle une API qui n’est pas incluse dans cette transaction, exactement-une-fois n’est pas automatiquement assuré pour cet effet externe.

Une approche courante pour les bases externes utilise une table d’idempotence ou une clé unique d’événement. Dans la même transaction de base, le service enregistre l’identifiant de l’événement traité et la modification métier. Si l’événement est rejoué, la contrainte de déduplication empêche la seconde application. Le design doit protéger contre la course entre deux workers qui traiteraient le même événement et considérer la rétention des clés de déduplication.

L’outbox transactionnelle aide à publier des événements de manière fiable depuis une base relationnelle. Le service valide la modification métier et un enregistrement d’outbox dans une même transaction; un processus lit ensuite l’outbox et publie les événements. Il peut republier après un timeout, donc l’identifiant d’événement et le consommateur idempotent restent nécessaires. Le modèle résout un problème spécifique de cohérence entre transaction de base et publication; il ne supprime pas tous les doublons.

Les tests doivent simuler une panne après la modification métier, avant la publication, après l’envoi au broker, avant le commit de l’offset et après l’écriture de la sortie. Ils doivent vérifier l’état final, le nombre de lignes et les événements manquants ou doublonnés. Une garantie qui n’a jamais été testée est souvent seulement une hypothèse de conception.

## 6. Rétention, compaction et reconstruction d’état

La rétention par durée ou taille conserve un historique limité. Elle convient lorsque les consommateurs doivent pouvoir rejouer pendant une fenêtre définie, mais qu’un stockage illimité serait inutile ou coûteux. La durée de rétention doit dépasser les délais plausibles de panne et de reprise, en tenant compte du volume et de la capacité. Une panne longue peut rendre un consumer incapable de rattraper un historique déjà supprimé.

La compaction de log conserve généralement la dernière valeur connue pour une clé selon la politique du topic, plutôt qu’un historique complet de chaque mise à jour. Elle peut convenir à la reconstruction d’un état courant ou à la distribution de configurations. Elle ne remplace pas l’historique événementiel si l’analyste a besoin de chaque changement. La sémantique des clés, les tombstones de suppression et la durée de rétention doivent être comprises.

La compaction n’est pas nécessairement instantanée. Des segments peuvent être nettoyés en arrière-plan selon les paramètres et la charge. Une application qui dépend de l’absence immédiate d’une ancienne valeur doit comprendre ce comportement. Les topics compactés ne doivent pas être utilisés comme un journal d’audit complet sans une politique supplémentaire.

La capacité doit être estimée à partir du débit d’événements, de la taille moyenne des messages, du nombre de répliques, de la rétention, de la compression et de la distribution par partition. Les événements compressés dans le réseau et sur disque peuvent consommer un volume différent de celui de leur structure logique. Surveillez le disque, le temps de remplissage, la taille par partition et les taux de production et consommation.

## 7. Contrats d’événements et compatibilité de schéma

Un événement est une API de données. Les producteurs et consommateurs peuvent être déployés à des moments différents, et un consommateur peut conserver un ancien code pendant que le producteur évolue. Les champs, types, noms, sémantique et valeurs doivent donc évoluer avec une politique de compatibilité explicite. Les formats JSON, Avro, Protobuf ou d’autres formats peuvent être utilisés, mais le mécanisme de validation et l’outil de gestion de schéma doivent être choisis consciemment.

Ajouter un champ facultatif est souvent plus facile qu’en supprimer un qui est utilisé. Changer le sens d’un champ tout en gardant son nom peut être plus dangereux qu’un changement visible de nom. Si score signifiait la note sur 100 et commence à représenter une note pondérée sur 1, les consommateurs continueraient à parser un nombre valide mais produiraient des résultats erronés. La compatibilité syntaxique ne garantit pas la compatibilité métier.

Les schémas doivent décrire la sémantique des timestamps, unités et identifiants. Un timestamp d’événement peut représenter le temps métier à la source, l’heure d’écriture dans Kafka ou l’heure de consommation. Ces valeurs servent à des calculs différents. Les noms doivent être explicites, par exemple event_time, published_at ou processed_at, et les équipes doivent documenter la convention de fuseau.

Les champs personnels ou secrets ne doivent pas être ajoutés à un événement par défaut. Les topics peuvent avoir plusieurs consommateurs, dont certains moins privilégiés que la source. Les données qui ne sont pas nécessaires à tous les consommateurs devraient être séparées ou protégées avec des contrôles d’accès appropriés. Les événements sont souvent conservés et rejoués, ce qui prolonge la portée d’une erreur de confidentialité.

## 8. Event time, fenêtres et retards

Le traitement de flux doit distinguer le temps où un événement s’est produit, le temps où il est arrivé au processeur et le temps où il a été traité. En batch, on peut souvent supposer que l’ensemble des données d’une période est arrivé. En streaming, des événements peuvent être retardés, réordonnés, rejoués ou arriver après qu’une fenêtre a déjà publié un résultat provisoire.

L’event time utilise l’horodatage métier de l’événement. Le processing time correspond au moment où le moteur traite l’enregistrement. Pour un tableau de bord qui calcule les inscriptions par minute, le choix modifie le résultat lorsqu’un événement se présente tardivement. Le processing time est pratique pour certaines alertes opérationnelles, mais l’event time est souvent plus adapté aux analyses historiques des faits.

Une fenêtre fixe de cinq minutes peut calculer un agrégat par intervalle. Des fenêtres glissantes se chevauchent; les sessions peuvent se terminer après un intervalle d’inactivité. Chaque modèle a une sémantique différente. Le choix doit refléter la question métier et être testé avec un événement au bord de la fenêtre, un timestamp manquant et un événement retardé.

Les watermarks bornent le temps pendant lequel le moteur conserve des états en attendant des données tardives. Ils équilibrent la mémoire et la correction tardive. Un watermark ne signifie pas que tous les événements plus anciens seront forcément supprimés de la source ou ignorés dans tous les moteurs de la même manière; le comportement précis dépend de l’implémentation et de l’opération. Les sorties et mises à jour tardives doivent être documentées.

~~~mermaid
flowchart LR
    A[Événements en retard variable] --> B[Tri logique par event time]
    B --> C[Fenêtres temporelles]
    C --> D[Watermark]
    D --> E[Résultats provisoires ou finaux]
    E --> F[Tableau de bord]
    G[Mesure du retard] --> D
~~~

Un tableau de bord quasi temps réel doit afficher sa fraîcheur et éventuellement indiquer que les périodes récentes peuvent encore changer. Si le métier exige une clôture exacte d’une période, le système doit définir la règle d’attente des données tardives et la façon de réviser les résultats. La simplicité de l’interface dépend d’un contrat clair côté traitement.

## 9. Kafka Streams, Spark Structured Streaming et consommateurs simples

Kafka assure le transport et la conservation des événements; il ne définit pas à lui seul le calcul d’agrégats, de jointures ou de fenêtres. Un consommateur simple peut traiter chaque événement et effectuer une mise à jour ponctuelle. Kafka Streams fournit des primitives de traitement de flux avec état et une intégration au modèle Kafka. Spark Structured Streaming fournit une API de traitement structuré de flux basée sur les DataFrames et SQL, généralement utilisée pour des traitements distribués plus larges et des sources variées.

Le choix dépend du type de traitement. Une validation légère et la mise à jour d’un état par clé peuvent s’adapter à un service de consommation ou Kafka Streams. Une analyse qui combine plusieurs sources, réalise de gros agrégats ou écrit dans un lakehouse peut être mieux adaptée à un moteur analytique de flux. La latence, la disponibilité, l’état, les connecteurs, les compétences et la façon de déployer comptent davantage que le nom du framework.

Le traitement avec état doit définir comment cet état est conservé, restauré, expiré et réconcilié. Un compteur par cours peut croître sans limite si les clés historiques ne sont jamais supprimées. Une fenêtre temporelle doit gérer l’événement tardif. Une jointure de deux flux doit connaître la durée pendant laquelle des événements peuvent encore se rencontrer. L’état distribué est une ressource qui demande une politique de cycle de vie.

Le streaming ne supprime pas l’ETL. Il change la cadence, ajoute la gestion des événements tardifs et impose une coordination plus stricte entre progrès du flux et sortie. Des traitements par micro-lots peuvent avoir une latence suffisante pour le besoin métier tout en simplifiant les reprises. Il faut mesurer la fraîcheur demandée par les utilisateurs plutôt que viser une latence milliseconde sans justification.

## 10. Observabilité : lag, erreurs et débit

Le consumer lag représente un retard entre la fin du journal disponible et la position du consommateur, mais le détail du calcul dépend de l’outil. Un lag qui augmente signifie que le consommateur ne traite pas le rythme d’arrivée, ou qu’un événement bloque un traitement. Il faut regarder le lag par partition, sa tendance, le débit du producteur et du consommateur, les erreurs, le temps par message et la dépendance de sortie.

Un lag global moyen peut masquer une partition bloquée. Si une clé très populaire se trouve sur une partition, le débit de cette partition peut déterminer la latence de tout le groupe. Mesurez la distribution par partition et la durée des tâches. Ajouter des consommateurs ne peut pas nécessairement paralléliser une partition unique et ne corrige pas un stockage externe lent.

Les erreurs de désérialisation, les schémas inattendus, les exceptions métier et les erreurs temporaires de stockage doivent être distingués. Les erreurs temporaires peuvent être réessayées avec un délai et une limite. Les erreurs permanentes nécessitent un rejet contrôlé ou une intervention. Une boucle infinie qui reprend le même événement invalide peut bloquer la partition et augmenter le lag de manière importante.

Les métriques comprennent le débit, les latences de publication et de consommation, les commits d’offset, le nombre de rebalance, le taux d’erreurs, l’âge de l’événement le plus ancien, le temps de rattrapage, le disque des brokers et l’état des répliques. Les logs devraient inclure un identifiant de corrélation et une clé d’événement lorsque cela est permis, sans exposer les payloads sensibles. Le runbook doit expliquer comment distinguer une panne broker, un consommateur ralenti et un événement empoisonné.

## 11. Sécurité, gouvernance et multi-tenant

La sécurité d’un cluster Kafka comprend l’authentification, l’autorisation par topic et groupe, le chiffrement en transit, le contrôle des opérations d’administration, la rotation des secrets et la surveillance. Un producteur ne devrait pas nécessairement pouvoir lire tous les topics; un consommateur ne devrait pas pouvoir publier des messages ni modifier des configurations. Les ACL et mécanismes équivalents doivent suivre le moindre privilège.

La séparation des environnements évite qu’un test de développement écrive dans la production. Les noms de topics doivent indiquer le domaine et l’environnement, mais le nom ne remplace pas l’isolation des permissions. Une identité de service est associée à un propriétaire, une finalité, une politique de rotation et une date de revue. Les secrets ne doivent pas être intégrés aux scripts, aux images de conteneur ou aux logs.

Les données d’événement peuvent inclure des identifiants d’apprenants, des traces de comportement ou des résultats d’examen. Il faut minimiser les champs, définir leur rétention et limiter l’accès aux topics contenant des informations personnelles. Le fait qu’un événement soit technique ne rend pas ses données non sensibles. Les copies répliquées, les archives et les outils de rejeu doivent suivre la même classification.

La gouvernance des topics comprend une description, un propriétaire, un schéma, une fréquence attendue, une taille de message, une politique de rétention, la liste des consommateurs et le contrat d’évolution. Sans catalogue, des consommateurs peuvent dépendre d’un topic qui est supprimé ou modifié sans coordination. Les changements à fort impact doivent être annoncés, testés et déployés de façon compatible.

## 12. Atelier pratique : créer un topic de laboratoire

Dans un cluster local ou dédié, créez un topic portant un nom de laboratoire et une configuration de partitionnement adaptée au test. Les scripts CLI peuvent porter un suffixe ou un emplacement différent selon la distribution Kafka. Vérifiez l’aide locale et l’environnement avant exécution.

~~~bash
kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --topic skilltree.lab.attempts \
  --partitions 3 --replication-factor 1

kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe --topic skilltree.lab.attempts
~~~

Un facteur de réplication égal à un peut convenir à un cluster local à un broker, mais il ne protège pas contre la perte de ce broker. Ne transposez pas cette configuration à une production. L’environnement de test doit isoler les données et le cluster ne doit contenir aucun topic métier critique.

Publiez quelques événements synthétiques avec une clé stable et des champs nommés clairement. Consommez-les depuis le début du journal dans un groupe de test. Vérifiez les clés, les offsets, l’ordre dans une partition et la façon dont plusieurs consommateurs d’un même groupe se partagent les partitions. Créez ensuite un second groupe de test pour observer qu’un autre groupe peut lire le même historique indépendamment.

Testez une erreur de traitement en faisant échouer volontairement la validation d’un événement synthétique. Vérifiez que l’erreur est visible, que le message n’est pas ignoré silencieusement et que la stratégie d’échec n’empêche pas de traiter les autres événements. Ajoutez une logique de déduplication basée sur un identifiant d’événement stable, puis rejouez le même événement et confirmez que l’effet métier reste unique.

## 13. Exercices corrigés

### Exercice 1 — L’ordre global

Un topic possède six partitions. L’application veut garantir que tous les événements de tous les apprenants sont traités strictement dans l’ordre global.

**Correction.** L’ordre Kafka est garanti par partition, pas automatiquement entre les partitions. Une seule partition pourrait donner un ordre total dans ce topic, mais réduirait le parallélisme et ne règle pas toutes les questions d’ordre entre producteurs. Si l’ordre n’est nécessaire que par apprenant, utilisez une clé d’apprenant stable et garantissez la cohérence de la stratégie de partitionnement.

### Exercice 2 — Offset commité avant l’écriture

Un consommateur avance l’offset puis écrit le résultat en base; il tombe juste avant l’écriture.

**Correction.** L’événement peut ne plus être relu alors que le résultat métier n’a pas été écrit. Le traitement a un risque de perte. La stratégie doit coordonner l’effet durable et l’avancement de l’offset, ou utiliser une transaction et des mécanismes adaptés. Une table de déduplication ne corrige pas à elle seule l’ordre d’opérations si l’offset est confirmé trop tôt.

### Exercice 3 — Un seul message bloque le groupe

Le lag monte parce qu’un événement contient un champ de type inattendu.

**Correction.** Identifiez si l’erreur est permanente et prévoyez une mise en quarantaine avec l’identifiant et le contexte utiles. Ne réessayez pas sans fin un événement qui ne pourra pas être parsé. La politique doit préserver la trace, alerter un propriétaire et permettre au flux de continuer selon la sémantique métier.

### Exercice 4 — Exactly-once vers une API externe

L’équipe active les transactions Kafka et affirme que les notifications SMS seront envoyées exactement une fois.

**Correction.** La transaction Kafka ne couvre pas automatiquement l’API SMS. Une panne après l’envoi mais avant la confirmation ou le commit peut conduire à une répétition. Il faut une clé d’idempotence ou un mécanisme de déduplication côté service externe, et préciser le périmètre réel de la garantie.

### Exercice 5 — Réduire le lag

Le groupe accuse 10 millions de messages de retard sur une seule partition, tandis que les autres partitions sont presque à jour.

**Correction.** Examinez la clé populaire, le coût du traitement et l’état du consommateur affecté. Ajouter des consommateurs ne divise pas automatiquement le travail d’une partition unique. Il peut être nécessaire de repenser la clé, de découper l’agrégation ou d’améliorer le traitement. Une migration de partitionnement doit préserver les règles d’ordre pertinentes.

## 14. Défi final : pipeline d’événements de résultat

Concevez un flux pour les événements attempt.completed qui alimentent un tableau de bord par cours, un service de certification et un entrepôt analytique. Un événement peut être livré plus d’une fois, arriver tardivement ou être mal formé. Les résultats de certification ne doivent pas être créés deux fois et le dashboard doit afficher sa fraîcheur.

### Correction attendue

1. **Contrat d’événement.** Définir event_id, learner_id, course_id, attempt_id, score, event_time et schema_version. Documenter les valeurs autorisées, l’unicité, l’heure métier et les champs personnels nécessaires. Valider le schéma avant publication.

2. **Partitionnement.** Choisir une clé cohérente avec le besoin d’ordre. Si l’ordre par apprenant est important, utiliser une clé stable d’apprenant. Mesurer la distribution pour éviter un hotspot. Le nombre de partitions doit permettre le débit attendu et correspondre à la capacité du groupe de consommateurs.

3. **Producteur.** Configurer les confirmations et retries selon la durabilité requise, utiliser les mécanismes d’idempotence supportés et un outbox fiable si la source est une base relationnelle. Enregistrer l’identifiant d’événement avec la transaction métier.

4. **Consommateur de certification.** Utiliser une contrainte ou une clé d’idempotence sur attempt_id/event_id, valider le score et enregistrer le résultat de façon transactionnelle. Ne pas affirmer que Kafka garantit un appel externe unique sans mécanisme dans le système externe.

5. **Consommateur analytique.** Agréger par event_time avec une règle de retard, une fenêtre et un watermark adaptés. Écrire des données de sortie versionnées, mesurer la fraîcheur et contrôler les doublons. Réconcilier les événements tardifs.

6. **Erreurs et reprise.** Séparer erreurs temporaires et permanentes. Quarantainer les événements mal formés, préserver le contexte nécessaire et alerter un propriétaire. Tester les crashes aux frontières de commit, l’indisponibilité du stockage et la réexécution du même identifiant.

7. **Observabilité et sécurité.** Mesurer le lag par partition, le débit, le temps de traitement, le taux de rejet et la dernière publication. Contrôler les ACL, le chiffrement, la rétention et les champs personnels. Documenter les propriétaires de topic et les consommateurs.

## 15. Stratégie de migration et de reprise d’un flux

Un flux vivant finit par changer : les clés peuvent évoluer, un schéma peut être remplacé, le nombre de partitions peut augmenter ou un consommateur peut être réécrit. La migration doit éviter la perte d’événements et les doubles effets pendant que deux versions coexistent. Commencez par spécifier la garantie recherchée, le point de reprise et l’identité des événements, puis testez la procédure sur un topic et des consommateurs synthétiques.

Pour un changement de schéma incompatible, une stratégie souvent plus sûre consiste à publier un champ nouveau ou un topic versionné, déployer les consommateurs capables de lire l’ancienne et la nouvelle forme, puis basculer les producteurs. Quand les consommateurs ont été migrés et le retard rattrapé, l’ancienne version peut être dépréciée. La stratégie exacte dépend des outils de schéma et du fait que les événements historiques seront relus.

L’augmentation du nombre de partitions demande une vigilance particulière si l’ordre par clé est important. Le mapping clé-partition peut changer, et des événements anciens et nouveaux d’une clé peuvent alors se trouver dans des partitions différentes. Selon le besoin, il peut être préférable de migrer vers un nouveau topic, de coordonner un cutover et de garantir une frontière de séquence, au lieu de supposer que l’ordre reste globalement identique.

Un consommateur de remplacement peut devoir restaurer son état à partir des événements ou d’un snapshot d’état. Le snapshot doit être lié à un offset cohérent; sinon, certains événements seront appliqués deux fois ou ignorés. La procédure doit documenter les offsets inclus dans le snapshot, la version du schéma, la clé de partition et la compatibilité des versions. La restauration doit être exercée comme une opération planifiée.

La reprise d’un flux se mesure en temps et en retard. Le système doit savoir à quel débit il peut rattraper une interruption tout en traitant les nouveaux messages. Une capacité de traitement juste égale au débit entrant ne permet pas de résorber le lag; il faut une marge. Pour une panne de deux heures, calculez le temps de rattrapage avec les ressources disponibles, en tenant compte du stockage de sortie et des éventuelles opérations de compaction.

## 16. Glossaire opérationnel et checklist

**Topic** : flux nommé d’enregistrements. **Partition** : journal ordonné d’un topic. **Offset** : position d’un enregistrement dans sa partition. **Broker** : serveur qui stocke et sert les partitions. **Consumer group** : groupe de consommateurs qui se répartissent les partitions. **Lag** : retard du consommateur par rapport à la fin du journal. **Idempotence** : propriété selon laquelle le rejeu d’une opération ne produit pas un second effet logique. **Outbox** : enregistrement de publication durable écrit dans la même transaction que la modification métier. **Watermark** : frontière temporelle utilisée par certains moteurs de flux pour limiter l’état conservé en attente de données tardives. **Compaction** : politique qui conserve les valeurs considérées comme pertinentes selon la clé, au lieu de garder nécessairement tous les changements.

Avant d’exploiter un topic, vérifiez son propriétaire, sa description, son schéma, sa clé, le nombre de partitions, le facteur de réplication, la politique de rétention, les permissions, le débit prévu et la capacité de rattrapage. Les consommateurs doivent avoir un groupe documenté, un mécanisme de commit adapté, une stratégie de retry, un traitement des événements invalides et un indicateur de lag. Les modifications de schéma et de partitionnement doivent avoir une procédure de migration.

Les garanties doivent être décrites sans ambiguïté. Dites si la livraison est au moins une fois, si la déduplication existe, si l’ordre est requis par clé, si le résultat externe est idempotent et si le rejeu est autorisé. Une architecture événementielle devient maintenable quand les producteurs savent ce qu’ils publient, les consommateurs savent ce qu’ils garantissent et l’équipe peut diagnostiquer les écarts avec des mesures.

## Ressources officielles

- Apache Kafka, documentation : https://kafka.apache.org/documentation/
- Apache Kafka, conception : https://kafka.apache.org/documentation/#design
- Apache Kafka, producteurs : https://kafka.apache.org/documentation/#producerconfigs
- Apache Kafka, consommateurs : https://kafka.apache.org/documentation/#consumerconfigs
- Apache Kafka, Kafka Streams : https://kafka.apache.org/documentation/streams/
- Apache Spark, Structured Streaming : https://spark.apache.org/docs/latest/streaming/index.html

Les paramètres exacts doivent être validés dans la version Kafka et les bibliothèques utilisées. Les garanties dépendent également des systèmes extérieurs; testez les pannes aux frontières entre journal, base et services externes plutôt que de considérer la configuration broker comme une preuve suffisante.
