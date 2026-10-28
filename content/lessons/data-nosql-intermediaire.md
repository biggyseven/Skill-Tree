# Introduction à MongoDB et Redis — Intermédiaire

> **Mise en contexte.** La plateforme de formation commence à traiter des données de nature très différente. Les informations de compte, les inscriptions et les résultats d’examen demandent des contraintes fortes et des transactions structurées; des événements de consultation arrivent en continu; le tableau de bord doit retrouver rapidement des compteurs temporaires et l’état d’une session. L’équipe envisage MongoDB pour certains documents flexibles et Redis pour certaines lectures rapides. Le choix ne doit pas être « NoSQL est plus rapide que SQL ». Il doit partir des modèles d’accès, des exigences de cohérence, de la durabilité, de la volumétrie et des compétences d’exploitation.

## Objectifs pédagogiques et parcours pratique

Ce cours introduit les bases documentaires de MongoDB et le magasin en mémoire Redis. Vous apprendrez à expliquer la différence entre documents, collections, clés-valeurs et structures de données en mémoire; choisir entre intégration d’objets et références; utiliser les opérations CRUD, les agrégations et les index MongoDB; comprendre les usages de chaînes, listes, ensembles, ensembles triés, hachages et expirations Redis; distinguer un cache d’une source de vérité; et évaluer les compromis de persistance, réplication, transaction et disponibilité.

Ce parcours vient après les bases relationnelles et les opérations SQL courantes. Il s’agit d’étendre votre vocabulaire de modélisation, pas de remplacer systématiquement les données relationnelles. Les exemples utilisent mongosh pour MongoDB et redis-cli pour Redis. Les commandes exactes dépendent de la version et de la configuration; les exemples utilisent des données synthétiques et doivent être exécutés dans un environnement de laboratoire.

## 1. Pourquoi les familles NoSQL existent

NoSQL n’est pas un modèle unique. Le terme regroupe plusieurs familles conçues pour des besoins différents : bases documentaires, magasins clé-valeur, magasins de colonnes larges, bases orientées graphe et moteurs spécialisés. Elles ne garantissent pas toutes les mêmes opérations, le même ordre, les mêmes transactions ou les mêmes mécanismes d’indexation. Il faut regarder les propriétés de chaque produit avant de choisir une architecture.

Une base relationnelle permet d’exprimer un modèle structuré par des relations, des contraintes et des requêtes combinant les données. Une base documentaire conserve des documents contenant des champs et des objets imbriqués, souvent avec une flexibilité de structure. Cela peut réduire la nécessité d’effectuer certaines jointures lorsque les données sont lues ensemble. En contrepartie, une modification qui touche les mêmes informations copiées dans plusieurs documents peut exiger une mise à jour coordonnée, ou accepter une certaine duplication.

Un magasin clé-valeur associe une clé à une valeur ou à une structure accessible principalement par cette clé. Redis offre plusieurs structures de données et opérations atomiques adaptées aux compteurs, files, ensembles, classement et cache. Il n’est pas identique à un cache RAM trivial : il a des mécanismes de persistance, de réplication et de gestion de mémoire, mais ces mécanismes doivent être configurés et compris. Une structure en mémoire ne garantit pas automatiquement qu’aucune donnée ne sera perdue en cas de panne.

Le choix d’un stockage doit partir des invariants. Un résultat d’examen qui doit rester lié à un apprenant et être unique peut bénéficier fortement d’un modèle relationnel. Un document de configuration extensible, lu en entier et dont les champs varient raisonnablement, peut être adapté à un modèle documentaire. Un compteur de requêtes temporaires ou un cache de résultat calculé peut être adapté à Redis si la perte ou la reconstruction est correctement gérée.

Le diagramme suivant donne une orientation conceptuelle, pas une règle absolue :

~~~mermaid
flowchart TD
    A[Besoin métier et accès] --> B{Nature dominante ?}
    B -->|Relations et contraintes| C[SGBD relationnel]
    B -->|Documents lus ensemble| D[Base documentaire]
    B -->|Accès par clé et structures rapides| E[Magasin clé-valeur]
    B -->|Connexions et parcours de relations| F[Base graphe]
    C --> G[Mesurer cohérence et transactions]
    D --> G
    E --> G
    F --> G
    G --> H[Valider charge, coûts et récupération]
~~~

Il est courant de combiner plusieurs modèles dans une architecture polyglotte, mais chaque système ajoute des copies, des flux, des opérations de sauvegarde, des mécanismes de sécurité et une charge d’exploitation. Ne déployez pas une deuxième base simplement parce qu’elle semble intéressante. Justifiez son rôle, ses données propriétaires, sa source de vérité et la façon dont les systèmes se synchronisent.

## 2. MongoDB : documents, collections et schémas

MongoDB stocke des documents BSON dans des collections. BSON est une représentation binaire qui étend les types JSON courants avec des types supplémentaires. Un document possède des champs; un champ peut contenir une valeur, un tableau ou un sous-document. Les documents d’une collection ne sont pas obligés d’avoir exactement les mêmes champs, mais une application robuste établit tout de même des conventions de structure, de validation, de noms et de version.

Exemple de document de configuration de cours :

~~~javascript
{
  _id: ObjectId(),
  title: "Routage IP avancé",
  level: "intermediaire",
  published: true,
  objectives: [
    "Lire une table de routage",
    "Diagnostiquer un défaut de passerelle"
  ],
  estimatedMinutes: 90,
  owner: {
    team: "networking",
    revision: 4
  }
}
~~~

La flexibilité du document ne signifie pas l’absence de schéma. Le schéma est souvent exprimé par l’application et par les règles de validation du serveur. Sans conventions, la collection peut contenir des valeurs dont le type varie entre documents, des champs manquants, des noms alternatifs pour une même propriété et des références qui ne correspondent plus à un document existant. Les consommateurs doivent alors gérer davantage de cas imprévus.

Un schéma de document doit représenter une unité de lecture et de mise à jour cohérente. Si l’interface affiche toujours le titre, le niveau et les objectifs ensemble, les conserver dans le document du cours est naturel. Si le document contient une liste de milliers d’événements qui s’allonge indéfiniment, l’intégration de tous ces événements peut agrandir sans limite la lecture et la mise à jour. Une collection distincte est souvent plus adaptée lorsque les éléments ont une durée de vie, un volume ou un accès indépendant.

Le modèle documentaire utilise fréquemment une certaine dénormalisation. Le titre du cours peut être copié dans un document d’historique pour permettre de lire l’historique même si le titre change. Cette copie doit avoir une sémantique claire : est-ce le titre au moment de l’inscription ou le titre actuel ? S’il s’agit d’un instantané historique, elle ne doit pas être mise à jour comme si elle était une référence courante. Une bonne dénormalisation exprime une règle métier; une copie accidentelle crée une incohérence.

MongoDB permet des règles de validation côté serveur. Elles servent à imposer certains types, champs requis et domaines de valeurs. Elles ne remplacent pas tous les tests de l’application, mais évitent que des scripts ou des clients non conformes écrivent silencieusement des documents invalides. Les validations doivent évoluer avec le schéma, et l’équipe doit décider comment les documents historiques sont traités pendant une migration.

## 3. Intégrer ou référencer des données

L’intégration, ou embedding, consiste à placer des données reliées dans un même document. Elle peut réduire les requêtes nécessaires à une lecture et permettre de mettre à jour un ensemble lié de façon atomique au niveau du document. Elle est particulièrement utile lorsque les données enfants sont limitées, lues avec le parent et ont un cycle de vie commun.

La référence conserve un identifiant vers un autre document. Elle convient lorsque les relations sont nombreuses, partagées entre parents, volumineuses ou mises à jour indépendamment. MongoDB ne transforme pas automatiquement toute référence en jointure relationnelle au moment de la lecture; il faut effectuer des requêtes supplémentaires ou utiliser les capacités d’agrégation appropriées. Le choix déplace donc une partie du travail vers le modèle d’accès.

Exemple : un cours contient un petit ensemble d’objectifs. Les intégrer permet de charger le cours avec ses objectifs dans une seule lecture. En revanche, les tentatives de quiz peuvent se compter par milliers et être consultées séparément par date, statut ou apprenant. Les placer toutes dans le document cours ferait croître celui-ci sans limite et compliquerait les accès ciblés.

Les références exigent une stratégie pour les documents orphelins. Un identifiant peut pointer vers un document supprimé, car une référence logique n’impose pas nécessairement une contrainte de clé étrangère comme dans un SGBD relationnel. Il faut définir qui possède la relation, comment une suppression est traitée et quels contrôles détectent les références cassées. Un script de nettoyage doit être testé et surveillé.

Les transactions multi-documents sont possibles dans les déploiements MongoDB qui satisfont les préconditions requises, notamment les environnements répliqués ou shardés supportés, mais elles ne sont pas gratuites. La documentation met en garde sur leur coût possible. Avant d’utiliser une transaction, comparez le modèle des documents, l’ordre de lecture et les exigences de cohérence. Parfois, une intégration qui regroupe les données atomiquement est plus simple; parfois, la référence et une transaction explicitement nécessaire sont le bon choix.

## 4. CRUD MongoDB et filtres précis

Les opérations CRUD désignent Create, Read, Update et Delete. mongosh permet de travailler directement avec les collections. Un document peut être inséré avec insertOne; plusieurs documents avec insertMany. La réussite d’une insertion ne prouve pas que la structure convient à toutes les requêtes futures. Le modèle doit être validé avec un jeu de données couvrant les cas habituels et les cas limites.

~~~javascript
db.courses.insertOne({
  title: "Routage IP avancé",
  level: "intermediaire",
  published: true,
  estimatedMinutes: 90
});
~~~

Pour lire les cours publiés d’un certain niveau :

~~~javascript
db.courses.find(
  { level: "intermediaire", published: true },
  { title: 1, level: 1, estimatedMinutes: 1 }
).sort({ title: 1 }).limit(20);
~~~

La projection réduit les champs retournés. Il est préférable de ne récupérer que ce dont l’application a besoin, surtout lorsque les documents comportent des tableaux ou des sous-documents volumineux. Le tri peut demander un index; il faut évaluer le plan et la cardinalité avant de supposer qu’une lecture est rapide.

Une mise à jour ciblée doit utiliser un filtre suffisamment précis. updateOne modifie un document correspondant, updateMany plusieurs documents. Si la condition est trop large ou mal formée, une mise à jour peut toucher bien plus de documents que prévu. Avant toute mise à jour de masse, lancez d’abord la requête de lecture correspondante, comptez les documents ciblés, sauvegardez si nécessaire et exécutez dans une base de test. Utilisez $set pour modifier des champs spécifiques au lieu de remplacer par accident l’ensemble du document.

~~~javascript
db.courses.updateOne(
  { title: "Routage IP avancé" },
  { $set: { published: false } }
);
~~~

La suppression est encore plus risquée. deleteOne supprime un document correspondant et deleteMany tous les documents qui satisfont le filtre. Une condition vide peut supprimer toute une collection. L’accès de production doit appliquer le moindre privilège et les outils d’administration doivent confirmer le nombre de documents visés avant une action destructive. Une suppression logique par statut peut être utile pour certaines fonctions, mais elle ne remplace pas une politique d’archivage et d’effacement.

Les mises à jour concurrentes doivent également être pensées. Un document peut changer entre une lecture et une mise à jour. Si la modification dépend d’un état préalable, encodez la condition dans le filtre pour que la modification ne s’applique que si l’état attendu est encore vrai. Le serveur renvoie un résultat qui indique combien de documents ont correspondu et ont été modifiés. L’application doit vérifier ces valeurs et traiter le cas où une opération n’a plus d’effet.

## 5. Agrégation, pipelines et résultats

Le pipeline d’agrégation MongoDB transforme des documents en une suite d’étapes. $match filtre, $project choisit ou calcule des champs, $group agrège, $sort ordonne, $unwind déplie certains tableaux et $lookup rapproche des documents de collections liées. L’ordre des étapes a un sens et influence souvent le coût. Un $match tôt dans le pipeline peut réduire le nombre de documents transmis aux étapes suivantes.

~~~javascript
db.attempts.aggregate([
  { $match: { finished: true, score: { $ne: null } } },
  {
    $group: {
      _id: "$courseId",
      count: { $sum: 1 },
      averageScore: { $avg: "$score" },
      bestScore: { $max: "$score" }
    }
  },
  { $sort: { averageScore: -1 } }
]);
~~~

Ce pipeline suppose que les champs existent et que les types sont cohérents. Si score contient des chaînes dans certains documents, le résultat peut différer du sens métier attendu ou devenir difficile à interpréter. Une validation de schéma et un contrôle de qualité des données réduisent ce risque. La définition du filtre doit aussi clarifier si les tentatives inachevées et les scores absents sont exclus, comptés ou présentés séparément.

Les opérations d’agrégation peuvent être coûteuses si elles analysent une très grande collection, construisent de gros groupes ou trient un grand volume de documents. Les index peuvent aider certains filtres initiaux, mais toutes les étapes ne bénéficient pas d’un index. Il faut examiner explain avec les statistiques d’exécution pour identifier la quantité de documents examinés, la partie qui réduit le volume et les étapes qui consomment la mémoire.

$lookup peut représenter une association entre collections, mais une succession de jointures peut cacher un modèle peu adapté aux accès les plus fréquents. Il n’est pas nécessaire de dénormaliser chaque relation; il faut mesurer la fréquence, le volume et le besoin de fraîcheur. Une table de lecture pré-calculée peut être un choix, à condition de gérer la mise à jour, la cohérence et la réconciliation.

## 6. Index MongoDB et plan de requête

MongoDB utilise des index pour accélérer les lectures qui correspondent à la structure de l’index. Les index courants incluent les index à champ unique et composites. L’ordre des champs d’un index composé compte pour les filtres et le tri. Une bonne pratique est de commencer par les requêtes réellement observées, puis de choisir un index qui aide les champs filtrés et ordonnés en tenant compte de l’ordre, de la sélectivité et du volume de résultats.

~~~javascript
db.attempts.createIndex({
  learnerId: 1,
  startedAt: -1
});
~~~

Cet index est un candidat si le parcours demande les dernières tentatives d’un apprenant. Il n’assure pas que toutes les colonnes retournées proviennent de l’index, et chaque modification concernée doit maintenir celui-ci. Les index consomment de la mémoire et du stockage; trop d’index peuvent pénaliser l’écriture et augmenter les coûts de maintenance.

La méthode explain permet de comprendre comment une requête est exécutée. Avec executionStats, l’analyse expose des statistiques réelles comme les documents examinés et retournés selon le plan et la version. Une requête peut être lente parce qu’elle examine beaucoup de documents pour en retourner quelques-uns, parce qu’elle trie un résultat large, ou parce qu’elle renvoie elle-même un grand volume. Dans ce dernier cas, l’optimisation peut demander une projection, une pagination ou un autre modèle d’accès, pas uniquement un index.

~~~javascript
db.attempts.find({
  learnerId: 105
}).sort({
  startedAt: -1
}).limit(20).explain("executionStats");
~~~

Après la création d’un index, refaites l’analyse avec les mêmes filtres et le même profil de données. Comparez les documents examinés, la durée observée, le plan et le coût d’écriture. Testez les valeurs fréquentes et rares. N’imposez pas une structure d’index parce qu’une requête est lente sur quelques documents; le planificateur a besoin de données représentatives.

Les index uniques peuvent protéger l’unicité d’une clé logique. Ils doivent être soigneusement définis si certains documents ne comportent pas le champ ou si la valeur est nullable. Un index unique peut refuser une migration si les données existantes contiennent des doublons. Avant la création, analysez la qualité des données, corrigez les doublons de façon contrôlée et prévoyez la gestion des nouvelles écritures pendant la migration.

## 7. Transactions, réplication et sharding MongoDB

MongoDB offre des garanties atomiques au niveau du document; les transactions multi-documents sont disponibles dans les configurations prises en charge. L’application doit choisir le niveau de cohérence qui correspond au besoin. Si les données d’un cours sont regroupées dans un document, une mise à jour de ce document peut être atomique. Si une opération doit modifier plusieurs documents liés, une transaction peut être nécessaire, mais peut avoir un coût supplémentaire.

La réplication maintient des copies des données et favorise la disponibilité. Elle ne supprime pas le besoin de sauvegarde ni les problèmes de corruption logique. Selon le mécanisme et les options de lecture, des clients peuvent observer un retard de propagation sur certaines répliques. Les garanties de cohérence doivent être définies dans l’application et les configurations de lecture/écriture choisies conformément à la version et au niveau de criticité des données.

Le sharding répartit les données sur plusieurs partitions pour augmenter la capacité de stockage ou de traitement. La clé de sharding est une décision structurante : elle influence la distribution, les requêtes ciblées, les hotspots et les opérations multi-shards. Une mauvaise clé peut concentrer la charge sur une partie du cluster et annuler les bénéfices de la distribution. Le sharding augmente aussi la complexité opérationnelle et la nécessité d’observer la répartition des données, les migrations et les performances par shard.

N’adoptez pas le sharding avant d’avoir mesuré le besoin. Vérifiez le modèle documentaire, les index, la sélectivité, le volume des résultats et les limites d’un nœud. Une architecture distribuée n’est pas automatiquement plus rapide pour une petite base, et la latence réseau entre composants peut augmenter le coût de certaines opérations. Le passage à une architecture distribuée doit être justifié par un objectif mesurable.

## 8. Redis : clés et structures de données

Redis associe des clés à des valeurs et structures en mémoire. Il ne se limite pas à des chaînes. Selon le besoin, une application peut utiliser des chaînes pour une valeur simple, des hachages pour des champs, des listes pour un ordre, des ensembles pour des valeurs uniques, des ensembles triés pour un classement, des bitmaps pour certains états compacts et d’autres structures disponibles dans la version utilisée. Le choix de structure affecte les opérations, le coût mémoire et les garanties possibles.

Une clé doit avoir une convention de nommage qui permet d’identifier son propriétaire, sa finalité et son environnement. Par exemple, skilltree:course:900:summary peut désigner un résumé mis en cache. Un préfixe ne constitue pas une isolation de sécurité : les autorisations et les ACL doivent empêcher les clients d’accéder à des clés qu’ils ne devraient pas utiliser. Dans les environnements partagés, les collisions de noms et les suppressions larges peuvent provoquer des incidents.

~~~text
SET skilltree:course:900:title "Routage IP avancé"
GET skilltree:course:900:title
HSET skilltree:learner:105 name "Amina" level "intermediaire"
HGETALL skilltree:learner:105
SADD skilltree:course:900:learners 105 106 107
SISMEMBER skilltree:course:900:learners 105
ZADD skilltree:leaderboard 850 "learner:105"
ZRANGE skilltree:leaderboard 0 9 REV WITHSCORES
~~~

Ces commandes illustrent des structures différentes; elles ne constituent pas le schéma universel à adopter. Les chaînes, hachages, ensembles et ensembles triés ont des opérations et des coûts distincts. Il faut vérifier la signification exacte des commandes et des options sur la version déployée. Un classement peut avoir besoin d’un ordre déterministe, de scores liés et d’une politique de mise à jour lorsque le score change.

Les clés de cache doivent avoir une politique d’expiration lorsque leurs valeurs peuvent devenir obsolètes. Sans TTL, un cache peut croître indéfiniment. Avec un TTL trop court, le système subit une forte pression de recalcul et des tempêtes de cache. Avec un TTL trop long, l’interface peut présenter une valeur périmée. Définissez la fraîcheur métier et choisissez une stratégie de rafraîchissement adaptée.

## 9. Redis comme cache : source de vérité et invalidation

Un cache réduit le coût de calcul ou de lecture en conservant temporairement une copie d’une valeur. La source de vérité reste normalement dans un système durable, par exemple une base relationnelle. L’application doit pouvoir reconstruire le cache après une perte, une expiration ou un déploiement. Si une valeur représente une donnée irremplaçable et qu’elle n’existe que dans un cache volatile sans mécanisme de persistance adapté, l’architecture est risquée.

Le modèle cache-aside est courant : l’application essaie d’abord de lire le cache; en cas d’absence, elle lit la base primaire, calcule la réponse, puis écrit la valeur dans Redis avec une expiration. Lors d’une modification, l’application invalide la clé ou met à jour la valeur selon une stratégie claire. La course entre écriture en base, invalidation et lecture doit être étudiée : une ancienne requête peut réinscrire une valeur périmée dans le cache après l’invalidation.

~~~mermaid
sequenceDiagram
    participant U as Utilisateur
    participant A as Application
    participant R as Redis
    participant DB as Base durable
    U->>A: Demande le résumé
    A->>R: Lire la clé
    alt Cache trouvé
        R-->>A: Valeur en cache
    else Cache absent
        R-->>A: Valeur absente
        A->>DB: Lire la source de vérité
        DB-->>A: Données actuelles
        A->>R: Enregistrer avec TTL
    end
    A-->>U: Réponse
~~~

Les problèmes fréquents comprennent les tempêtes de cache au redémarrage, le cache stampede lorsqu’un grand nombre de requêtes recalculent la même clé expirée, les valeurs périmées et la consommation mémoire. Des mécanismes de verrouillage temporaire, de rafraîchissement anticipé ou de regroupement des calculs peuvent aider, mais doivent être justifiés par des mesures. Un verrou dans Redis a ses propres questions de durée, de renouvellement et de libération; il ne doit pas être considéré comme une garantie magique.

L’invalidation doit suivre la sémantique des données. Une modification du titre du cours exige peut-être d’invalider le résumé de cours et le résultat de recherche, mais pas le cache d’une ressource indépendante. Les clés doivent être recensées et les dépendances documentées. Un cache non observable devient une source de bugs difficiles à reproduire. Suivez les hits, misses, expirations, erreurs, latence, mémoire et taux de recalcul.

## 10. Persistance, réplication et mémoire Redis

Redis peut être configuré avec différents mécanismes de persistance. RDB produit des instantanés à certains moments; AOF enregistre les écritures selon sa politique de synchronisation. Le choix implique un compromis entre perte potentielle en cas de panne, coût d’écriture, taille des fichiers et temps de récupération. Désactiver toute persistance peut être acceptable pour un cache entièrement reconstructible, mais pas pour une fonction métier qui dépend uniquement de ces données.

La présence d’un fichier de persistance ne suffit pas à prouver la possibilité de reprise. Il faut vérifier que la configuration est active, que les fichiers sont disponibles, que les copies sont protégées et qu’une restauration a été testée. La persistance Redis n’est pas forcément une sauvegarde indépendante; si les fichiers se trouvent sur le même disque et sous le même compte que l’instance, certains scénarios de perte ou d’attaque touchent les deux.

La réplication Redis permet de maintenir des copies, mais la réplication peut être asynchrone. Les écritures reconnues par un primaire ne sont donc pas automatiquement une garantie qu’aucune donnée ne sera perdue en cas de perte immédiate du primaire. Le niveau de durabilité nécessaire dépend de l’usage. Pour un cache reconstructible, cette limite peut être acceptable; pour un état irremplaçable, elle exige un autre design ou une configuration plus stricte.

La mémoire est une ressource critique. Lorsque Redis atteint sa limite de mémoire, la politique configurée peut refuser des écritures ou évincer certaines clés. Une politique d’éviction conçue pour un cache n’est pas forcément compatible avec une base utilisée comme source de vérité. Surveillez l’utilisation mémoire, les expirations, l’éviction, les plus grosses clés, la fragmentation et le taux de commandes. N’utilisez pas une politique d’éviction globale sans comprendre quelles données peuvent être supprimées.

## 11. Cohérence entre MongoDB, Redis et la base relationnelle

Lorsqu’un système utilise plusieurs stockages, l’équipe doit définir le propriétaire de chaque donnée. Si PostgreSQL est la source de vérité des inscriptions, Redis peut stocker un décompte temporaire, et MongoDB un document de contenu. Une modification d’inscription doit mettre à jour PostgreSQL de manière fiable; le cache peut être invalidé ou recalculé. Il faut éviter que deux systèmes soient modifiés indépendamment sans mécanisme de synchronisation, car une panne entre les étapes laissera un état divergent.

Un modèle d’événements peut aider lorsque plusieurs systèmes doivent se synchroniser. L’application valide d’abord l’opération métier dans la base propriétaire puis publie un événement de façon fiable, par exemple avec une table d’outbox transactionnelle. Un consommateur met à jour les vues secondaires et peut être rejoué en cas d’échec. Les consommateurs doivent être idempotents, parce qu’un événement peut être livré plus d’une fois selon la technologie et la stratégie de reprise.

L’invalidation du cache peut être envoyée après le commit. Mais si le processus tombe entre le commit SQL et l’invalidation Redis, une ancienne valeur demeure. Un système plus robuste peut utiliser une outbox, une notification fiable ou un TTL qui borne la durée d’obsolescence. Le choix dépend du besoin de fraîcheur. Un badge de popularité peut tolérer quelques secondes; une validation de paiement ou de certification a besoin de garanties différentes.

Il faut également empêcher la fuite de données entre utilisateurs ou environnements. Les clés de cache et documents doivent intégrer les dimensions nécessaires, par exemple le tenant, la version de contenu ou la langue. Un cache dont la clé ignore le périmètre de sécurité peut retourner des données d’un autre utilisateur même si la base source protège correctement les accès. La sécurité doit être examinée dans les chemins de lecture secondaires, pas seulement dans la base principale.

## 12. Laboratoire MongoDB

Dans un environnement local ou de test, connectez-vous à mongosh sur une instance que vous contrôlez. Créez une base de laboratoire et ajoutez des documents synthétiques.

~~~javascript
use skilltree_lab

db.courses.insertMany([
  {
    title: "Routage IP",
    level: "debutant",
    published: true,
    tags: ["network", "routing"]
  },
  {
    title: "BGP",
    level: "expert",
    published: true,
    tags: ["network", "routing"]
  },
  {
    title: "Introduction aux bases",
    level: "debutant",
    published: false,
    tags: ["data"]
  }
]);
~~~

Effectuez plusieurs recherches : tous les cours publiés, les cours d’un niveau donné, les cours ayant une étiquette particulière et les vingt cours les plus récents si la date est ajoutée au modèle. Examinez les documents renvoyés et vérifiez si la projection évite de transmettre les champs inutiles. Ajoutez ensuite un index qui correspond à une requête fréquente et comparez explain avant et après.

Créez des tentatives séparées plutôt que d’imbriquer un historique non borné dans chaque cours. Construisez une agrégation qui calcule le nombre et le meilleur score par cours. Ajoutez des documents avec score absent ou de type inattendu pour observer l’effet, puis corrigez le modèle avec des validations. Répétez l’agrégation après le nettoyage.

Pratiquez les opérations destructives seulement sur les données jetables. Avant un updateMany ou un deleteMany, exécutez le filtre en find, comptez les documents correspondants et vérifiez qu’ils sont les bons. Cette discipline simule la procédure de changement opérationnel et évite les incidents liés aux filtres trop larges.

## 13. Laboratoire Redis

Connectez-vous à une instance de test de Redis avec redis-cli. Vérifiez l’identité de l’environnement et ne réutilisez pas un serveur qui contient des données d’un autre projet. Les exemples suivants créent des clés préfixées par skilltree:lab pour limiter le risque de collision.

~~~text
SET skilltree:lab:course:900:summary "120 inscriptions"
EXPIRE skilltree:lab:course:900:summary 300
TTL skilltree:lab:course:900:summary
GET skilltree:lab:course:900:summary
DEL skilltree:lab:course:900:summary
~~~

Observez comment le TTL diminue et ce que renvoie GET après l’expiration. L’expiration est une propriété du cache, pas une politique de sauvegarde. Ajoutez un hachage pour un profil synthétique et un ensemble pour des identifiants uniques. Vérifiez les opérations de lecture, de mise à jour et d’appartenance. Pour un classement, testez un ensemble trié avec plusieurs valeurs et des ex æquo, puis définissez comment le rang doit être présenté à l’utilisateur.

Examinez les commandes d’information autorisées sur votre environnement, l’usage mémoire, le taux de clés expirées et l’état de la persistance. En production, certaines commandes d’administration sont restreintes ou peuvent produire des informations sensibles. Utilisez le compte et les commandes adaptés, et ne lancez pas une commande de nettoyage globale dans un environnement partagé.

Pour simuler une panne de cache, supprimez une clé de résumé et vérifiez que l’application peut reconstruire la valeur depuis la source de vérité. Le test doit confirmer l’exactitude du résultat reconstruit et observer le temps supplémentaire. Si la valeur ne peut pas être reconstruite, demandez-vous si elle doit réellement vivre uniquement dans Redis ou si un stockage durable et une sauvegarde sont nécessaires.

## 14. Exercices corrigés

### Exercice 1 — Embedding ou référence?

Un cours possède cinq objectifs et 500 000 tentatives. Les objectifs sont lus avec le cours; les tentatives sont filtrées par apprenant et date.

**Correction.** Les objectifs sont de bons candidats à l’intégration car ils sont peu nombreux et partagent le cycle de vie du cours. L’historique des tentatives devrait généralement être séparé, car il est volumineux et lu par d’autres critères. Le choix doit inclure la taille des documents, le nombre de requêtes et les besoins de modification.

### Exercice 2 — MongoDB ne possède pas de clé étrangère classique

Un document d’inscription référence un cours supprimé.

**Correction.** Définissez le traitement du cours supprimé, puis ajoutez des validations applicatives et des contrôles périodiques des références. Selon les règles métier, il peut être interdit de supprimer un cours avec des inscriptions, ou les inscriptions peuvent garder un instantané de l’information historique. Les suppressions doivent suivre la politique et les cas orphelins doivent être détectés.

### Exercice 3 — Cache périmé

Après avoir modifié un cours en base relationnelle, Redis continue d’afficher l’ancien titre.

**Correction.** L’écriture en base et l’invalidation ne sont probablement pas coordonnées de façon fiable. Définissez la source de vérité, invalidez ou mettez à jour la clé après commit et prévoyez le cas de panne entre les deux opérations. Un mécanisme d’événement fiable ou un TTL borné peut aider. Ajoutez un test qui simule l’interruption au moment critique.

### Exercice 4 — Redis sans persistance

L’équipe stocke exclusivement dans Redis les résultats définitifs d’examen et désactive la persistance pour gagner de la vitesse.

**Correction.** La décision met les résultats en risque de perte et ne convient pas à des données irremplaçables sans autre mécanisme durable. Redis peut être utilisé pour l’accès rapide, mais la source de vérité doit offrir les garanties approuvées. Il faut définir un stockage durable, un chemin de reprise et un test de restauration avant le déploiement.

### Exercice 5 — Index MongoDB

Une requête filtre par learnerId et trie par startedAt, mais examine un très grand nombre de documents.

**Correction.** Examinez explain("executionStats"), la sélectivité, la projection et le nombre de résultats. Un index composite commençant par learnerId et intégrant startedAt peut être candidat, mais doit être mesuré sur les valeurs fréquentes et rares. Vérifiez le coût d’écriture et la possibilité que la requête retourne elle-même trop de lignes.

## 15. Défi final : architecture polyglotte contrôlée

Proposez une architecture pour la plateforme de formation qui utilise PostgreSQL pour les inscriptions et les résultats, MongoDB pour les documents de contenu flexibles et Redis pour des résumés temporaires. Un titre de cours peut changer. Les inscriptions doivent rester cohérentes. Le tableau de bord doit être rapide, et la perte de Redis ne doit pas faire perdre de données métier.

### Correction attendue

1. **Source de vérité.** PostgreSQL possède les identités, inscriptions, résultats et règles relationnelles. MongoDB possède les documents de contenu si ce domaine bénéficie réellement de sa flexibilité. Les décisions de propriété et les identifiants de relation sont documentés. Les synchronisations ne doivent pas créer deux propriétaires concurrents pour la même donnée.

2. **MongoDB.** Définir un schéma logique, une politique de validation et des index correspondant aux accès fréquents. Intégrer les champs du document de cours souvent lus ensemble, mais garder séparées les collections historiques non bornées. Contrôler les références et la version du document.

3. **Redis.** Utiliser des clés dédiées par domaine, définir une expiration et une stratégie d’invalidation après les changements validés. Les résumés doivent pouvoir être reconstruits à partir de la source de vérité. Surveiller hits, misses, mémoire, éviction, latence et taux de recalcul.

4. **Cohérence.** Publier un événement fiable après les transactions métier ou employer un mécanisme de synchronisation documenté. Les consommateurs doivent être idempotents. Prévoir l’échec partiel, le rattrapage et les doublons. Définir la tolérance à l’obsolescence par donnée.

5. **Sécurité et reprise.** Appliquer le moindre privilège, les secrets, la segmentation réseau, les sauvegardes, la rotation des clés et les tests de restauration adaptés à chaque moteur. Un cache reconstructible peut avoir une politique différente, mais les données métier durables doivent répondre à des objectifs explicites.

6. **Mesure.** Tester le p95 de lecture, la charge d’écriture, le comportement lors de la perte de Redis et le rattrapage des événements. Comparer la complexité opérationnelle à une solution relationnelle plus simple. Conserver cette architecture uniquement si les bénéfices sont mesurés et valent les coûts de maintenance supplémentaires.

## 16. Checklist et synthèse

Avant d’ajouter un stockage, définissez la source de vérité, les invariants, le profil de requête, les règles de transaction, la durabilité, les objectifs de disponibilité, les procédures de sauvegarde et les compétences nécessaires. Pour MongoDB, réfléchissez au grain du document, à l’intégration ou aux références, aux index, à la validation, aux opérations CRUD, aux agrégations et aux transactions. Pour Redis, définissez les structures, le cycle de vie des clés, l’expiration, l’invalidation, la mémoire, la persistance et la possibilité de reconstruire les valeurs.

NoSQL ne supprime pas la modélisation : il change les structures et certains compromis. Une base documentaire n’est pas un JSON sans règles; Redis n’est pas une source durable par défaut; un cache doit être observable et reconstructible; la réplication n’élimine pas le besoin de sauvegarde; l’architecture polyglotte exige une propriété claire des données et un mécanisme de synchronisation fiable.

## Ressources officielles

- MongoDB, modélisation des données : https://www.mongodb.com/docs/manual/data-modeling/
- MongoDB, opérations CRUD : https://www.mongodb.com/docs/manual/crud/
- MongoDB, index : https://www.mongodb.com/docs/manual/indexes/
- MongoDB, transactions et cohérence : https://www.mongodb.com/docs/manual/core/transactions/
- Redis, structures de données : https://redis.io/docs/latest/develop/data-types/
- Redis, persistance : https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
- Redis, documentation de référence des commandes : https://redis.io/docs/latest/commands/

Les mécanismes de disponibilité, de transaction et de persistance doivent être vérifiés dans la version et la configuration exactes. Les noms des produits ne garantissent pas à eux seuls une propriété de cohérence ou de reprise.
