
# Introduction à MongoDB et Redis — Intermédiaire

## Mise en contexte

Une application de formation, une boutique en ligne, une API de réservation ou une plateforme de supervision manipule plusieurs catégories de données. Certaines représentent des objets métier riches, dont les champs évoluent avec le temps. D'autres sont des valeurs à lire ou à mettre à jour avec une latence très faible : session, compteur, cache, verrou applicatif ou classement. Vouloir faire entrer tous ces besoins dans un seul modèle de stockage peut simplifier artificiellement le schéma, mais compliquer l'exploitation et dégrader les performances.

MongoDB et Redis appartiennent au vaste ensemble des technologies NoSQL, sans pour autant fournir le même modèle. MongoDB est principalement une base documentaire : elle conserve des documents BSON dans des collections, propose des requêtes riches, des index, un pipeline d'agrégation et des garanties transactionnelles. Redis est un serveur de structures de données en mémoire accessible par protocole réseau. Il expose notamment des chaînes, des hachages, des listes, des ensembles, des ensembles triés et des flux. Il est utile pour les accès à faible latence, les compteurs, les classements, les sessions, les files simples et les caches. Redis peut également persister ses données, être répliqué et servir à d'autres usages ; il ne faut donc pas le réduire à une simple table de cache.

Le terme NoSQL ne signifie pas « sans structure », « sans contraintes », ni « sans transactions ». Il désigne des modèles qui ne reposent pas tous sur la représentation relationnelle classique en tables et jointures. Chaque technologie possède ses compromis concernant la forme des données, les requêtes, la cohérence, la distribution, la durabilité et l'exploitation.

L'objectif de ce cours est de concevoir une solution, et pas seulement de mémoriser des commandes. Nous suivrons SkillMarket, une application fictive qui gère des parcours de formation, des catalogues, des sessions utilisateur et des classements d'activité. MongoDB conservera les objets métier qui profitent du modèle documentaire ; Redis accélérera les lectures et réalisera quelques opérations éphémères et atomiques. Le choix reste une hypothèse à vérifier par des mesures, pas une règle universelle.

## 1. Objectifs et prérequis

À la fin du cours, vous devrez savoir comparer une base relationnelle, une base documentaire et un serveur de structures en mémoire ; identifier ce qui doit être embarqué dans un document MongoDB et ce qui mérite une collection séparée ; écrire des opérations CRUD, des filtres, une agrégation et des index cohérents avec les requêtes ; connaître les limites des schémas flexibles et mettre en place une validation ; choisir entre les types de données Redis ; manipuler expiration, compteur, pipeline et transaction sans confondre atomicité et durabilité ; expliquer réplication, persistance, disponibilité et sauvegarde ; éviter les incohérences d'un cache ; diagnostiquer une requête lente, une clé évincée ou une restauration non testée ; enfin, présenter une architecture hybride avec une source de vérité clairement définie.

Ce cours suppose une familiarité avec les tables SQL, les clés primaires, les jointures, les transactions, les index et les notions RPO/RTO. Les concepts sont repris lorsque cela aide à comparer les modèles, mais le parcours part du principe que vous savez déjà interroger une base relationnelle et lire un schéma simple.

## 2. Panorama des modèles NoSQL

### 2.1 Les grandes familles

Une base documentaire expose des objets semi-structurés ; une base clé-valeur associe une clé à une valeur ou à une structure ; une base orientée colonnes privilégie certains accès analytiques ou distribués ; une base orientée graphe représente explicitement sommets et relations. Ces familles ne sont pas des frontières absolues : des produits peuvent combiner plusieurs fonctionnalités.

~~~mermaid
flowchart TD
    A["Besoin de persistance"] --> B["Relationnel"]
    A --> C["NoSQL et modèles spécialisés"]
    B --> D["Tables, contraintes, jointures"]
    C --> E["Documents"]
    C --> F["Clé-valeur / structures"]
    C --> G["Colonnes distribuées"]
    C --> H["Graphe"]
    E --> I["MongoDB"]
    F --> J["Redis"]
~~~

Le modèle relationnel reste un excellent choix lorsque les relations et contraintes intertables sont centrales, que les requêtes sont variées et que la cohérence transactionnelle est déterminante. MongoDB peut convenir à un domaine composé d'objets consultés ensemble, avec des structures imbriquées et des évolutions de champs. Redis est adapté aux opérations sur des données ou structures ciblées, avec des accès fréquents et rapides. Il peut aussi tenir un rôle durable, mais la décision doit s'appuyer sur une configuration de persistance, une politique de sauvegarde et des tests de reprise.

La bonne question n'est pas « quelle base est la meilleure ? », mais « quel modèle rend les opérations réelles simples, sûres, mesurables et économiquement soutenables ? ».

| Dimension | Relationnel | MongoDB | Redis |
|---|---|---|---|
| Modèle | Tables et relations | Documents BSON et collections | Structures adressées par clés |
| Requêtes | SQL, jointures et agrégations | Filtres, projections, pipeline | Commandes ciblées par structure |
| Relations | Clés étrangères selon le SGBD | Références ou documents embarqués | Généralement encodées dans les clés ou structures |
| Atomicité | Selon la transaction et le SGBD | Au niveau d'un document ; transactions multi-documents possibles | Commandes individuelles atomiques ; transactions et scripts selon le besoin |
| Usage fréquent | Système transactionnel général | Catalogue, profil, contenu, événements documentaires | Cache, session, compteur, classement, flux |
| Risque typique | Jointures et schéma mal conçus | Documents trop gros, duplication non maîtrisée | Pression mémoire, expiration mal pensée, confusion cache/source |

Ce tableau donne des repères, pas un classement. La performance dépend du volume, des index, de la cardinalité, de la concurrence, du réseau, des réglages et du profil des opérations.

### 2.2 Pourquoi combiner plusieurs modèles ?

Supposons que SkillMarket affiche une fiche de cours, compte des vues, maintienne une session de connexion et présente les dix participants les plus actifs. MongoDB peut conserver le contenu pédagogique et les documents d'inscription. Redis peut garder une copie temporaire des fiches les plus lues, compter des événements et ordonner un classement. Une architecture hybride peut réduire la charge de la base de référence, mais elle introduit un deuxième système à superviser et une question importante : comment corriger ou invalider les copies lorsque la donnée source change ?

~~~mermaid
flowchart LR
    U["Navigateur"] --> API["API métier"]
    API --> M["MongoDB : données de référence"]
    API --> R["Redis : cache et compteurs"]
    API --> Q["Journal / traitement asynchrone"]
    M --> B["Sauvegardes et restauration"]
    R --> P["Persistance et politique de reprise"]
    API -. "cache miss" .-> M
    M -. "invalidation après écriture" .-> R
~~~

L'application doit définir le comportement attendu en cas d'indisponibilité de Redis. Pour un cache, il peut être acceptable de continuer à lire la base principale, si elle possède la capacité nécessaire. Pour une session ou un mécanisme d'anti-abus, la réponse peut être différente. Chaque usage doit avoir un mode de repli documenté et testé.

## 3. MongoDB : le modèle documentaire

### 3.1 Base, collection et document

MongoDB organise les données dans des bases, des collections et des documents. Un document BSON est une structure composée de champs et de valeurs. Il ressemble à un objet JSON, mais BSON prend en charge des types supplémentaires, notamment certains types numériques et les dates. Une collection regroupe des documents du même domaine, sans imposer par défaut un schéma strictement identique à chaque document.

~~~javascript
{
  _id: ObjectId("65f000000000000000000001"),
  slug: "mongodb-modelisation",
  title: "Modéliser avec MongoDB",
  level: "intermediaire",
  durationMinutes: 75,
  tags: ["nosql", "documents", "index"],
  author: {
    id: "trainer-42",
    displayName: "Nadia"
  },
  published: true,
  updatedAt: ISODate("2026-10-28T09:00:00Z")
}
~~~

Les valeurs d'identifiant et de date ci-dessus sont des exemples de shell MongoDB. Un document est une unité structurée, pas une ligne avec des colonnes immuables. Cette souplesse est un avantage si elle reflète le domaine ; elle devient un risque si chaque service emploie un nom de champ ou un type différent sans contrôle.

Une collection peut contenir des documents ayant certains champs facultatifs. Par exemple, un cours en brouillon peut ne pas avoir de date de publication. Il reste souhaitable de définir les invariants : le slug doit être une chaîne non vide, la durée doit être positive, le niveau doit appartenir à un ensemble défini et un cours publié doit répondre aux exigences de contenu. Les invariants importants doivent être contrôlés dans le code métier et, lorsque cela convient, par une validation côté base.

### 3.2 Embarquer ou référencer ?

Un modèle documentaire ne consiste pas à imbriquer tout le domaine dans un document géant. L'embarquement convient lorsque les sous-objets appartiennent étroitement au parent, sont généralement lus ensemble et ont une croissance bornée. Une référence convient lorsqu'une entité est partagée entre de nombreux parents, évolue indépendamment, ou peut croître sans limite prévisible.

Un modèle simple de cours peut embarquer un auteur résumé et quelques étiquettes. Les inscriptions, en revanche, peuvent former une collection séparée parce qu'elles sont nombreuses, consultées par apprenant et susceptibles d'augmenter continuellement.

~~~mermaid
flowchart TD
    A["Fiche de cours"] --> B["Métadonnées"]
    A --> C["Auteur embarqué"]
    A --> D["Étiquettes embarquées"]
    A --> E["Inscriptions séparées"]
    E --> F["Collection inscriptions"]
    F --> G["Référence vers apprenant"]
~~~

La représentation exacte dépend des accès. Si la majorité des écrans charge la fiche avec l'auteur et les étiquettes, les embarquer peut réduire les allers-retours. Si les inscriptions doivent être filtrées par apprenant, période et statut, une collection dédiée avec des index adaptés peut être préférable. La dénormalisation est acceptable lorsqu'elle est intentionnelle : il faut décider quelle copie fait autorité et comment les changements se propagent.

Pour décider, écrivez d'abord les principales lectures et écritures. Demandez-vous quelle entité est consultée seule, quelle entité grandit, quels éléments sont partagés entre parents et quelle duplication serait acceptable. Un tableau non borné crée des documents plus volumineux et peut concentrer les mises à jour sur un même document. Des documents de taille raisonnable et une croissance maîtrisée simplifient la maintenance. Quand deux objets doivent être mis à jour indépendamment, des documents distincts rendent parfois le domaine plus clair.

### 3.3 Exemple CRUD avec mongosh

Les commandes suivantes se lancent dans le shell MongoDB, dans une base de test. Elles ne sont pas des requêtes SQL.

~~~javascript
use skillmarket

db.courses.insertOne({
  slug: "mongodb-modelisation",
  title: "Modéliser avec MongoDB",
  level: "intermediaire",
  durationMinutes: 75,
  tags: ["nosql", "documents"],
  published: true,
  updatedAt: new Date()
})

db.courses.find(
  { level: "intermediaire", published: true },
  { title: 1, slug: 1, durationMinutes: 1, _id: 0 }
).sort({ title: 1 }).limit(20)

db.courses.updateOne(
  { slug: "mongodb-modelisation" },
  { $set: { durationMinutes: 80, updatedAt: new Date() } }
)

db.courses.deleteOne({ slug: "cours-de-test-temporaire" })
~~~

insertOne insère un document. find filtre les documents et la projection sélectionne les champs à retourner. Le fait d'indiquer _id: 0 masque l'identifiant dans le résultat. sort organise les résultats avant la limite. updateOne modifie au plus un document correspondant ; $set ne remplace que les champs nommés. deleteOne supprime au plus un document correspondant.

En environnement réel, vérifiez le filtre, les droits, les valeurs concernées et le nombre de documents modifiés. Une suppression non bornée ou une mise à jour dépourvue de filtre peut provoquer un incident. Les scripts d'administration doivent afficher ce qu'ils vont changer, employer un environnement de test lorsque possible et disposer d'une stratégie de restauration.

### 3.4 Filtres et opérateurs

MongoDB propose une riche syntaxe de filtres. Les opérateurs usuels comprennent $gt, $gte, $lt, $lte, $in, $exists, $and, $or et $regex. Pour une recherche simple sur une catégorie et un intervalle de durée :

~~~javascript
db.courses.find({
  level: { $in: ["debutant", "intermediaire"] },
  durationMinutes: { $gte: 30, $lte: 90 },
  published: true
})
~~~

Il faut réfléchir aux types BSON. Une durée stockée comme chaîne n'est pas équivalente à une durée numérique. Des dates stockées de façon incohérente conduisent à des comparaisons inattendues. Ne laissez pas un schéma flexible devenir un schéma imprévisible.

L'opérateur $exists indique si un champ est présent ; il ne garantit pas que sa valeur soit utile ni du type attendu. Un champ peut exister avec la valeur null. Les opérateurs de comparaison avec des données absentes ou nulles exigent donc une connaissance précise du jeu de données. Les recherches textuelles fondées sur des expressions régulières peuvent être coûteuses selon le motif et les index disponibles. Une requête n'est pas optimisée par le seul fait qu'elle est concise.

### 3.5 Validation de schéma

La flexibilité n'exclut pas une validation de schéma. Une collection stabilisée gagne à préciser les types et règles qui doivent rester vrais. Exemple illustratif avec JSON Schema dans MongoDB :

~~~javascript
db.createCollection("coursesValidated", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["slug", "title", "level", "durationMinutes", "published"],
      properties: {
        slug: { bsonType: "string", minLength: 1 },
        title: { bsonType: "string", minLength: 1 },
        level: { enum: ["debutant", "intermediaire", "expert"] },
        durationMinutes: {
          bsonType: ["int", "long", "double"],
          minimum: 1
        },
        published: { bsonType: "bool" },
        tags: { bsonType: "array", items: { bsonType: "string" } }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})
~~~

Le validateur empêche certains documents de s'écarter des règles. Il ne remplace pas toutes les validations métier : une contrainte qui implique plusieurs collections ou un service externe peut nécessiter un contrôle applicatif ou une transaction. La validation doit être déployée en tenant compte des données déjà présentes. Avant de rendre une règle stricte, inventoriez les documents existants, corrigez les données invalides et prévoyez un changement progressif.

Documentez les raisons d'un champ facultatif plutôt que d'accepter des valeurs disparates. Lorsqu'une nouvelle version de l'application ajoute un champ, lisez les anciennes valeurs avec une stratégie de compatibilité claire : valeur par défaut, migration progressive ou lecture qui sait traiter les deux formes pendant une période limitée.

## 4. Agrégations MongoDB

Le pipeline d'agrégation enchaîne des étapes serveur. Le principe est de filtrer tôt, de ne transporter que les champs nécessaires, puis de grouper, calculer, trier et limiter le résultat attendu. Cela évite de récupérer des centaines de milliers de documents pour effectuer les mêmes calculs dans la mémoire du service web.

~~~javascript
db.courses.aggregate([
  { $match: { published: true } },
  {
    $group: {
      _id: "$level",
      nombreCours: { $sum: 1 },
      dureeMoyenne: { $avg: "$durationMinutes" }
    }
  },
  { $sort: { nombreCours: -1, _id: 1 } },
  {
    $project: {
      _id: 0,
      niveau: "$_id",
      nombreCours: 1,
      dureeMoyenne: { $round: ["$dureeMoyenne", 1] }
    }
  }
])
~~~

~~~mermaid
flowchart LR
    A["Collection courses"] --> B["$match : filtrer"]
    B --> C["$group : agréger"]
    C --> D["$sort : ordonner"]
    D --> E["$project : présenter"]
    E --> F["Résultat synthétique"]
~~~

Une étape $match placée tôt réduit potentiellement les documents à traiter et peut bénéficier d'un index. $group calcule le nombre et la moyenne dans l'exemple. $project façonne le résultat final. Les pipelines peuvent aussi comporter $unwind pour déplier un tableau, $lookup pour rapprocher des collections, $set pour créer des champs, et $facet pour produire plusieurs sous-résultats. Ces possibilités ne suppriment pas les principes de modélisation : une agrégation complexe exécutée à chaque requête peut indiquer qu'un autre modèle ou une donnée pré-calculée serait plus adapté.

Quand un pipeline inclut $lookup, examinez les deux côtés de la jointure, les types de clés et les index. Si la collection jointe est énorme et que l'étape répète une recherche coûteuse, il peut être nécessaire de revoir le pipeline, de filtrer auparavant ou de modifier le modèle. Ne remplacez pas chaque jointure SQL par un $lookup sans mesurer le résultat.

Une agrégation doit aussi être validée sur des données représentatives. Testez les champs absents, les tableaux vides, les valeurs nulles et les documents très volumineux. Vérifiez que le calcul compte bien les entités attendues : après $unwind, un cours comportant trois étiquettes peut apparaître trois fois, ce qui change le sens d'un comptage.

## 5. Index MongoDB

Un index permet au moteur de retrouver certaines entrées sans parcourir tous les documents. En contrepartie, chaque index occupe de l'espace, doit être maintenu lors des écritures et ajoute des coûts de mémoire et d'exploitation. L'objectif est d'indexer les requêtes réellement importantes.

~~~javascript
db.courses.createIndex({ slug: 1 }, { unique: true })
db.courses.createIndex({ published: 1, level: 1, updatedAt: -1 })
db.courses.createIndex({ tags: 1 })
~~~

Le premier index exprime l'unicité du slug. Le second peut aider une requête qui filtre par état et niveau puis trie par mise à jour, selon le profil réel. Le troisième est un exemple d'index multikey sur un tableau. Les index composés sont sensibles à l'ordre des champs, aux filtres, aux tris et à la sélectivité. Ne copiez pas arbitrairement un ordre proposé par un exemple : mesurez et vérifiez.

Un index unique peut échouer lors de sa création si les données existantes violent déjà l'unicité. Avant son déploiement, détectez les doublons et décidez comment les corriger. Une contrainte unique a un sens métier ; elle ne doit pas être ajoutée sans réflexion sur les valeurs nulles et manquantes.

explain executionStats permet d'examiner le plan et des métriques d'exécution. On peut rechercher notamment un balayage de collection (COLLSCAN), l'utilisation d'un index (IXSCAN), le nombre de documents examinés et le nombre de résultats produits. Un balayage complet n'est pas forcément un défaut : une petite collection ou une requête qui doit retourner presque tous les documents peut être servie efficacement sans index spécialisé. La décision doit s'appuyer sur le coût, la fréquence et la latence observée.

~~~javascript
db.courses.find({
  published: true,
  level: "intermediaire"
}).explain("executionStats")
~~~

Le diagnostic suit un ordre discipliné : reproduire la requête avec un volume représentatif, observer les statistiques, formuler une hypothèse, créer ou modifier un index dans un environnement contrôlé, comparer les mesures, puis documenter le gain et le coût d'écriture. Accumuler des index par réflexe peut rendre le système plus lent et plus complexe.

## 6. Relations, transactions et cohérence MongoDB

Une opération de lecture ou d'écriture sur un document est atomique. Cette propriété est importante lorsque des champs liés doivent rester cohérents ensemble. Par exemple, si un document contient un état et un compteur, une opération unique modifiant les deux champs peut éviter un état intermédiaire visible au niveau du document.

Les opérations multi-documents sont un sujet différent. MongoDB prend en charge les transactions multi-documents dans des déploiements compatibles, mais une transaction augmente le coût et ne doit pas compenser une modélisation négligée. Pour un processus de commande, déterminez quelles invariants traversent réellement plusieurs documents et si les données peuvent être modélisées pour que la mise à jour principale reste dans un seul document.

~~~mermaid
sequenceDiagram
    participant A as Application
    participant M as MongoDB
    A->>M: Démarrer la transaction
    A->>M: Mettre à jour document A
    A->>M: Insérer document B
    alt Toutes les règles sont satisfaites
        A->>M: Commit
        M-->>A: Succès
    else Une étape échoue
        A->>M: Abort
        M-->>A: Aucun changement partiel validé
    end
~~~

La réussite dépend aussi des paramètres de lecture et d'écriture, du déploiement et du traitement des erreurs. Le code doit gérer les annulations, les conflits transitoires et les reprises conformément à l'API du pilote utilisé. Évitez d'effectuer dans une transaction des appels réseau longs vers un service externe : la transaction de base ne peut pas annuler un paiement envoyé à une passerelle externe. Les architectures distribuées utilisent souvent une saga, une boîte d'envoi transactionnelle ou des mécanismes de compensation.

La cohérence ne se résume pas à « réplicas présents ». La lecture depuis un secondaire, les garanties d'acquittement, les délais de réplication et les paramètres de lecture influencent ce qu'un client observe. Pour les décisions financières ou sensibles, il faut définir précisément la garantie nécessaire, la tolérance à la latence et le comportement attendu lors d'une panne. Validez le comportement avec le pilote et le déploiement exacts utilisés en production.

## 7. Redis : clés et structures de données

### 7.1 Une clé n'est pas un schéma métier complet

Redis adresse les valeurs par des clés. La structure de la valeur doit correspondre à l'opération attendue. Une chaîne convient à une valeur simple, un hachage à un petit objet composé de champs, une liste à une séquence, un ensemble à des éléments uniques, un ensemble trié à des éléments ordonnés par score et un flux à une suite d'événements. D'autres types existent selon les versions et les modules déployés.

~~~mermaid
flowchart TD
    A["Besoin applicatif"] --> B{"Quelle opération domine ?"}
    B -->|"Valeur simple ou compteur"| C["STRING"]
    B -->|"Champs d'un objet"| D["HASH"]
    B -->|"File / séquence"| E["LIST"]
    B -->|"Membres uniques"| F["SET"]
    B -->|"Classement par score"| G["SORTED SET"]
    B -->|"Journal d'événements"| H["STREAM"]
~~~

Les types ne sont pas interchangeables. Une liste ne fournit pas automatiquement les mêmes garanties de recherche qu'un ensemble. Un ensemble trié n'est pas un remplacement universel d'une base de classement complexe. Les structures intégrées permettent d'exécuter certaines opérations côté Redis, limitant les données transférées au client.

### 7.2 Préfixes de clés et conventions

Une convention de nommage est utile dans une application partagée. Exemples : `skillmarket:cache:course:mongodb-modelisation`, `skillmarket:session:abc123`, `skillmarket:course:views:mongodb-modelisation` et `skillmarket:leaderboard:weekly`. Les préfixes facilitent le diagnostic, mais ils ne remplacent pas les ACL, les namespaces ni des limites de responsabilité.

Évitez d'inclure des données personnelles en clair dans les clés, de concaténer sans encodage des éléments contrôlés par l'utilisateur ou d'utiliser un format impossible à faire évoluer. Définissez les règles de TTL, le propriétaire de chaque famille de clés, la taille attendue, le besoin de persistance et le comportement lors de l'expiration. Les outils d'exploitation doivent savoir quelles clés appartiennent au cache, aux sessions et à des données plus durables.

### 7.3 Chaînes et compteurs atomiques

~~~redis
SET skillmarket:course:views:mongodb-modelisation 0
INCR skillmarket:course:views:mongodb-modelisation
GET skillmarket:course:views:mongodb-modelisation
EXPIRE skillmarket:temporary-counter 300
TTL skillmarket:temporary-counter
~~~

INCR met à jour atomiquement une valeur entière stockée sous forme de chaîne Redis. C'est utile pour les compteurs, sous réserve de définir leur signification : compteur de vues approximatif, événements confirmés, quotas par fenêtre ou statistiques à exporter. Un compteur en Redis peut disparaître après expiration, éviction, panne ou restauration. Si ce compteur fait autorité pour une facture ou une obligation réglementaire, le design doit être différent ou garantir sa durabilité de manière documentée.

L'exemple d'expiration suppose que la clé temporaire a été créée auparavant. TTL retourne le temps restant selon les conventions de Redis, dont une valeur particulière si la clé n'existe pas ou si aucune expiration n'est définie. Contrôlez le résultat au lieu de supposer qu'une expiration a été correctement posée.

### 7.4 Hachages, listes et ensembles

Un hachage peut représenter les champs simples d'une session ou d'un profil :

~~~redis
HSET skillmarket:session:abc123 userId 42 role learner lastSeen 2026-10-28T09:30:00Z
HGET skillmarket:session:abc123 userId
HGETALL skillmarket:session:abc123
EXPIRE skillmarket:session:abc123 1800
~~~

Les sessions méritent une attention de sécurité particulière : leur expiration est une décision métier, pas un nettoyage cosmétique. Une session de privilège élevé peut avoir une durée différente, être invalidée après un changement de mot de passe ou être liée à un appareil. Les identifiants de session doivent être imprévisibles et les commandes ne doivent pas exposer les secrets dans les journaux.

Les listes permettent des opérations en tête et en queue, par exemple dans certaines files de travail :

~~~redis
LPUSH skillmarket:notifications learner:42:course-published
RPOP skillmarket:notifications
LLEN skillmarket:notifications
~~~

Ce petit exemple illustre une séquence élémentaire, mais une application de production doit évaluer la récupération après panne, l'accusé de traitement, la visibilité des messages, la livraison multiple et la supervision de la profondeur. Selon les exigences, Redis Streams, une file spécialisée ou un broker de messages peut être plus adapté. Une file qui supprime définitivement un message au moment de sa lecture peut entraîner une perte si le processus s'arrête avant d'avoir terminé le traitement.

Un ensemble garantit l'unicité des membres, ce qui convient par exemple pour les identifiants des apprenants qui ont aimé un cours :

~~~redis
SADD skillmarket:course:liked-by:mongodb-modelisation learner:42 learner:57
SISMEMBER skillmarket:course:liked-by:mongodb-modelisation learner:42
SCARD skillmarket:course:liked-by:mongodb-modelisation
SREM skillmarket:course:liked-by:mongodb-modelisation learner:57
~~~

Le choix d'un ensemble n'évite pas la question du stockage durable. Si cette liste d'appréciations est une donnée métier indispensable, il faut décider si Redis est la source d'autorité, s'il s'agit d'une vue recalculable ou s'il faut enregistrer l'événement dans un stockage durable avant d'actualiser l'ensemble.

### 7.5 Ensembles triés pour les classements

Un ensemble trié associe un score à chaque membre unique. Il permet de classer les membres selon leur score et d'obtenir des plages ordonnées. Exemple :

~~~redis
ZADD skillmarket:leaderboard:weekly 125 learner:42 98 learner:57 151 learner:19
ZREVRANGE skillmarket:leaderboard:weekly 0 9 WITHSCORES
ZINCRBY skillmarket:leaderboard:weekly 10 learner:57
ZREVRANK skillmarket:leaderboard:weekly learner:57
~~~

Les scores représentent ici des points de formation. Définissez les règles des égalités : est-ce que deux apprenants à égalité doivent partager le rang, ou est-ce qu'un second critère de tri départage les résultats ? Les commandes de classement ne remplacent pas les règles métier. Elles matérialisent un algorithme qui doit être explicite, testable et cohérent avec le système de points.

Un classement hebdomadaire doit disposer d'un mécanisme de rotation ou d'une clé datée et d'une politique de rétention. Sans cela, la plateforme peut conserver des périodes anciennes sans raison et consommer inutilement la mémoire.

## 8. Expiration, TTL et conception du cache

La durée de vie d'une clé Redis peut être définie en secondes ou millisecondes. Elle peut être inspectée et renouvelée. L'expiration est adaptée aux sessions, aux données de cache, aux jetons temporaires ou aux verrous de courte durée selon leur protocole. Mais une TTL n'est pas une stratégie d'invalidation complète : un contenu de cours qui change peut rester présent jusqu'à expiration, à moins que l'application ne l'invalide ou le versionne.

~~~mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant R as Redis
    participant M as MongoDB
    C->>A: Lire un cours
    A->>R: GET cache du cours
    alt Cache hit
        R-->>A: Document sérialisé
    else Cache miss
        R-->>A: Clé absente
        A->>M: Lire la version de référence
        M-->>A: Document actuel
        A->>R: SET avec TTL
    end
    A-->>C: Réponse du cours
~~~

La stratégie cache-aside laisse l'application consulter le cache puis la source en cas d'absence. Elle est simple, mais elle oblige à traiter les courses entre lecture et écriture. Imaginez qu'une requête lise l'ancien document de MongoDB pendant qu'une autre le met à jour et invalide Redis. Si la première écrit ensuite son ancien résultat dans le cache, une valeur obsolète revient. Les remèdes dépendent du besoin : versionnement, invalidation plus robuste, verrouillage limité, mise en cache de versions, TTL courte ou stratégie événementielle.

La TTL doit être fondée sur une règle de fraîcheur. Elle n'est pas automatiquement égale à la durée de session ni au délai maximal de cohérence acceptable. Pour un catalogue éditorial, une minute ou plusieurs minutes peut être convenable selon le besoin. Pour un prix ou un statut d'autorisation, il peut être dangereux d'utiliser le même modèle. Les données d'autorisation ne doivent pas rester obsolètes après une révocation si le risque est élevé.

Il faut aussi prévenir le cache stampede, phénomène durant lequel de nombreux clients demandent simultanément une donnée expirée et déclenchent chacun une lecture coûteuse de la source. Des mécanismes de verrouillage à courte durée, des TTL avec légère dispersion, du préchauffage, du rafraîchissement anticipé ou une limitation des requêtes peuvent réduire le risque. Leur coût et leur comportement en cas de panne doivent être testés.

### 8.1 Invalidation après une modification

Une politique courante consiste à enregistrer la mise à jour dans la source d'autorité, puis à supprimer la clé de cache correspondante. Une suppression n'est pas une preuve d'invalidation globale si plusieurs versions ou clés dérivées existent. Maintenez une cartographie documentée entre entité métier et clés de cache. Si une écriture réussit dans MongoDB mais que la suppression Redis échoue, l'application doit avoir une réponse définie : journaliser, réessayer, publier un événement durable ou accepter une courte période d'obsolescence explicitement approuvée.

Ne faites pas de Redis l'unique copie d'une donnée critique en supposant que le serveur ne redémarrera jamais. Il peut être configuré sans persistance pour un cache récupérable, mais ce choix doit être réservé aux données reconstructibles. Si Redis contient des états qu'il est impossible de reconstruire, étudiez la persistance, la réplication, les sauvegardes, les copies hors machine et les essais de restauration. Une réplication seule n'est pas une sauvegarde, puisqu'une erreur de suppression peut se propager.

## 9. Atomicité et transactions Redis

Chaque commande Redis individuelle possède des garanties d'atomicité selon l'opération. Cependant, une suite de commandes exécutées par un client n'est pas automatiquement indivisible. Les transactions Redis regroupent des commandes avec MULTI et EXEC ; WATCH permet un modèle optimiste où l'exécution est annulée si une clé surveillée change avant l'exécution.

~~~redis
WATCH skillmarket:inventory:course-42
GET skillmarket:inventory:course-42
MULTI
DECR skillmarket:inventory:course-42
EXEC
~~~

Ce fragment montre l'idée de base et non une implémentation complète de vente. Le client doit analyser le résultat de EXEC, gérer une transaction annulée et réessayer de manière bornée si la clé a changé. Il doit également vérifier que la quantité ne devient pas négative. Un simple DECR sans condition ne suffit pas à faire respecter cette règle.

Les transactions Redis ne sont pas identiques aux transactions SQL avec des instructions conditionnelles complexes, contraintes intertables et annulation générale de tous les effets applicatifs. Redis ne fournit pas un rollback arbitraire de chaque commande déjà exécutée comme certains développeurs l'imaginent. Selon le besoin, un script Lua peut réaliser une séquence atomique sur le serveur, mais il doit rester court, borné et testé pour éviter de monopoliser le serveur.

Pour un verrou distribué, un exemple naïf tel que définir une clé puis la supprimer plus tard est dangereux : le bail peut expirer puis être repris par un autre client, tandis que l'ancien propriétaire supprime le verrou du nouveau. Un schéma plus sûr utilise une valeur de jeton unique et une suppression conditionnelle, avec une durée adaptée et une analyse des garanties nécessaires. Dans des opérations critiques, un verrou Redis ne doit pas être considéré comme une solution magique à la coordination distribuée. Évaluez les partitions réseau, la suspension des processus et le risque qu'un propriétaire ancien continue son travail après expiration.

Pour diminuer l'attente réseau, Redis supporte le pipelining : le client envoie plusieurs commandes avant de lire l'ensemble des réponses. Le pipeline peut réduire les allers-retours, mais il ne transforme pas par lui-même les commandes en une opération atomique. Il faut distinguer pipeline, transaction et script côté serveur.

## 10. Persistance et durabilité de Redis

Redis conserve un jeu de données en mémoire et propose plusieurs options de persistance. Les snapshots RDB créent des instantanés. L'append-only file (AOF) journalise les opérations d'écriture afin de reconstruire l'état. Il est possible de configurer les deux mécanismes ou, dans des scénarios de cache récupérable, de désactiver la persistance. Le choix dépend du niveau de perte admissible, du temps de redémarrage, de la charge d'écriture et de la capacité disque.

~~~mermaid
flowchart TD
    A["Écritures Redis"] --> B["Jeu de données en mémoire"]
    B --> C["RDB : instantané périodique"]
    B --> D["AOF : journal des écritures"]
    C --> E["Fichier de snapshot"]
    D --> F["Rejeu du journal au redémarrage"]
    E --> G["Reprise après incident"]
    F --> G
    G --> H["Validation applicative"]
~~~

RDB peut donner un fichier compact utile pour un instantané et certaines sauvegardes, mais une panne entre deux snapshots peut faire perdre les écritures depuis le dernier instantané. AOF fournit une autre relation entre durabilité et performance, réglable selon la fréquence de synchronisation sur disque. Avec une politique de synchronisation toutes les secondes, la perte potentielle est distincte d'une politique de synchronisation à chaque écriture, qui peut être plus coûteuse. La performance réelle doit être mesurée et les garanties de configuration comprises, pas supposées.

La persistance Redis n'équivaut pas à une stratégie complète de sauvegarde. Il faut conserver des copies séparées de la machine, gérer la rétention, chiffrer les sauvegardes selon le risque, contrôler leur intégrité et tester une restauration sur un environnement de remplacement. Une sauvegarde n'est utile que si elle peut être restaurée dans un délai compatible avec les besoins de l'entreprise.

Redis fournit notamment INFO persistence pour inspecter des indicateurs de persistance. En opération, surveillez l'état des snapshots et réécritures AOF, les erreurs d'E/S, l'espace disque et les temps de fork qui peuvent affecter la latence. Toute modification des options de durabilité est un changement d'architecture, pas une simple optimisation cosmétique.

Les points à documenter sont : quelles données sont perdues si Redis est vidé, comment les reconstruire, quelle est la tolérance de perte, où sont les sauvegardes, qui peut les lire, quand la dernière restauration a été testée, et quel est le runbook en cas de corruption. Pour le cache d'un catalogue MongoDB, le vidage peut être acceptable si la source reste disponible et peut absorber le trafic. Pour des événements qui représentent des paiements ou des états irremplaçables, le raisonnement est entièrement différent.

## 11. Réplication, Sentinel, Cluster et disponibilité

La réplication Redis suit un modèle leader-réplique. Les répliques reçoivent les effets des écritures du leader. Elle peut améliorer la disponibilité et répartir certaines lectures, mais la réplication est généralement asynchrone : une écriture acquittée par le leader peut ne pas être immédiatement visible sur une réplique ou peut être perdue dans certains scénarios de bascule. Répliquer les données ne dispense pas de gérer les sauvegardes.

Sentinel peut surveiller un déploiement et participer à l'identification d'une nouvelle instance principale lors d'une panne. Redis Cluster partitionne l'espace de clés entre plusieurs nœuds et apporte une architecture distribuée, au prix de contraintes supplémentaires sur les clés multi-objets et les opérations. Le choix entre instance simple, réplication avec Sentinel et Cluster doit découler des besoins de capacité, du domaine de panne, de la topologie et des compétences d'exploitation.

~~~mermaid
flowchart TD
    C["Clients"] --> S["Service de découverte / Sentinel"]
    S --> P["Principal Redis"]
    P --> R1["Réplique A"]
    P --> R2["Réplique B"]
    P --> W["Écritures"]
    R1 --> L["Lectures possibles selon la politique"]
    R2 --> L
    P --> D["Persistance configurée"]
    R1 --> B["Sauvegardes selon le plan"]
~~~

Ce diagramme est conceptuel. Sentinel n'est pas un proxy qui reçoit nécessairement toutes les commandes, et une topologie réelle peut être différente. L'application ou l'environnement client doit découvrir le bon principal, se reconnecter et gérer des erreurs temporaires. Lors d'une bascule, des commandes peuvent échouer pendant un intervalle ; le code doit avoir une stratégie de reconnexion bornée et ne pas répéter aveuglément des écritures non idempotentes.

Une architecture de haute disponibilité doit être testée avec de vraies pannes : arrêt d'un nœud, perte de réseau entre segments, redémarrage, saturation mémoire, indisponibilité d'un stockage et bascule. Vérifiez le temps de récupération, les erreurs visibles par le client, la perte de données, la remise en service des répliques et l'exactitude des clés après reprise. Une architecture qui semble redondante sur un schéma n'est pas validée pour autant.

Dans MongoDB, la haute disponibilité s'appuie notamment sur les replica sets, avec un primaire et des secondaires. Dans Redis, les mécanismes sont différents et n'offrent pas automatiquement les mêmes garanties transactionnelles. Ne supposez jamais que deux produits répliqués se comportent de la même façon : comprenez le mode d'acquittement et le scénario de bascule propre à chacun.

## 12. Sécurité : protection en profondeur

Les bases ne doivent pas être exposées directement à Internet sans besoin et conception de sécurité le justifiant. Placez les services sur des réseaux privés, limitez les ports, authentifiez les clients, imposez le principe du moindre privilège, chiffrez les flux et protégez les secrets. Les utilisateurs applicatifs ne doivent pas disposer d'un rôle administrateur global uniquement parce que cela rend le développement plus simple.

Pour MongoDB, définissez des utilisateurs et rôles adaptés à la base et aux collections nécessaires. Activez les options de transport sécurisé, gérez les certificats, contrôlez les journaux et envisagez la validation de schéma. Les filtres doivent être construits à partir de valeurs validées et non par concaténation de fragments fournis par l'utilisateur. Les secrets d'accès ne doivent pas être commités dans Git ni exposés dans les messages d'erreur.

Pour Redis, utilisez l'authentification et les ACL selon l'environnement, limitez les commandes et les clés auxquelles chaque service peut accéder, et restreignez le trafic réseau. Le fait que Redis ait historiquement été utilisé dans des réseaux privés ne justifie pas une exposition anonyme. Si plusieurs applications partagent une même instance, des utilisateurs et permissions distincts réduisent le risque qu'un composant affecte les données de l'autre.

La protection des données en transit n'est qu'une couche. Il faut aussi gérer les sauvegardes, journaux, exports de diagnostic, snapshots, métriques et environnements de test. Les données de production copiées dans un environnement de développement peuvent contenir des identifiants ou des informations personnelles. Préférez des données synthétiques ou anonymisées lorsque cela répond au besoin. Définissez la durée de conservation et les personnes qui peuvent accéder aux données sensibles.

MongoDB et Redis ne corrigent pas une faille d'autorisation dans l'application. Une clé Redis imprévisible est utile, mais n'est pas un substitut à l'authentification et au contrôle d'accès. Un identifiant de document difficile à deviner ne remplace pas la vérification que l'utilisateur est autorisé à le consulter. Les contrôles de sécurité doivent être effectués côté serveur.

## 13. Observabilité et diagnostic

La supervision doit associer métriques, journaux structurés, traces et indicateurs métier. Pour MongoDB, surveillez la latence des requêtes, le nombre de documents examinés, les taux d'utilisation des index, la mémoire, les connexions, le journal et l'état du replica set. Pour Redis, surveillez la mémoire utilisée, les clés évincées, les expirations, les connexions, la latence, les commandes lentes, le taux de cache hit et l'état de persistance et de réplication.

Un cache hit ratio faible n'indique pas toujours un défaut : il peut s'agir d'un cache récent, d'un accès peu répétitif ou d'une clé mal conçue. Un hit ratio élevé n'assure pas non plus la fraîcheur ni la justesse. Il faut comparer le coût des misses, la latence de la source, la consommation mémoire et les taux d'erreur pour décider si le cache contribue réellement au service.

~~~mermaid
flowchart TD
    A["Alerte : latence API élevée"] --> B["Séparer API, réseau et bases"]
    B --> C["MongoDB : explain et profiler contrôlé"]
    B --> D["Redis : latence, mémoire, eviction"]
    C --> E["Comparer requête et index"]
    D --> F["Comparer hit ratio, TTL et commandes"]
    E --> G["Hypothèse documentée"]
    F --> G
    G --> H["Test ciblé et mesure avant/après"]
    H --> I["Déploiement surveillé ou retour arrière"]
~~~

N'activez pas un profilage détaillé durablement sans en connaître le coût et le contenu potentiel. Les journaux peuvent contenir des valeurs sensibles ; appliquez une politique de masquage et de rétention. Un diagnostic efficace commence par l'observation de symptômes concrets et une hypothèse falsifiable. Modifier simultanément les index, la taille du cache, la configuration mémoire et les clients ne permet pas d'identifier la cause d'une amélioration ou d'une régression.

### 13.1 Incidents typiques

**Latence MongoDB élevée.** Mesurez les requêtes les plus lentes, regardez les plans d'exécution, examinez la sélectivité des index, la taille des documents et les volumes retournés. Vérifiez également si les clients lancent trop de requêtes séquentielles. Un index supplémentaire est une hypothèse à tester, pas une réponse automatique.

**Redis manque de mémoire.** Déterminez si les clés doivent être conservées ou si certaines peuvent être évincées. Vérifiez les valeurs volumineuses, les clés sans TTL, les structures qui grandissent sans limite et le nombre de clients. Une politique LRU/LFU n'est pas équivalente à une rétention métier ; elle peut retirer une clé valide selon la stratégie d'éviction. Si toutes les clés sont indispensables, augmenter seulement la limite sans résoudre la croissance ne fait que repousser le problème.

**Cache incohérent.** Déterminez la source d'autorité, la dernière modification, la durée de cache, le mécanisme d'invalidation et les clés dérivées. Testez si deux opérations concurrentes peuvent réintroduire une valeur obsolète après invalidation. Tracez les versions ou dates de modification lorsque c'est pertinent.

**Bascule ou redémarrage.** Vérifiez le quorum et le mécanisme de haute disponibilité, les journaux, les répliques, la durabilité configurée et les erreurs côté client. Ne supposez pas qu'un processus vivant est un service disponible. Après le retour, validez le contenu, les connexions et les fonctions métier avant de déclarer l'incident terminé.

## 14. Architecture de référence pour SkillMarket

Une architecture possible conserve dans MongoDB les cours, profils publics et documents de progression qui nécessitent des requêtes documentaires. Redis stocke des copies sérialisées temporaires de fiches populaires, les sessions et certains compteurs d'activité. Les événements significatifs peuvent être enregistrés dans une source durable ou publiés par un mécanisme d'événements avec confirmation de traitement, puis utilisés pour recalculer les agrégats Redis.

~~~mermaid
flowchart LR
    U["Web / mobile"] --> API["API métier"]
    API --> AUTH["Service de session"]
    AUTH --> R["Redis"]
    API --> M["MongoDB"]
    API --> E["Événements durables"]
    E --> W["Worker"]
    W --> R
    W --> A["Agrégats et classements"]
    M --> BK["Sauvegarde isolée"]
    R --> RK["RDB / AOF selon le besoin"]
~~~

Cette proposition décrit des responsabilités, pas une infrastructure prête à déployer. Le choix exact du mécanisme événementiel, la stratégie de persistance, le service managé ou autogéré et les objectifs de disponibilité dépendront du volume et des compétences d'exploitation.

### 14.1 Décider des sources de vérité

Chaque attribut métier doit avoir une source d'autorité identifiable. Le titre d'un cours peut être défini dans MongoDB et copié dans Redis à des fins de cache. Le cache ne devient pas la source du titre. Si une clé de cache est perdue, elle doit être recréée depuis la source ; si une copie obsolète est détectée, elle doit être invalidée ou remplacée. Les points du classement peuvent être recalculés à partir d'événements durables, ou Redis peut être choisi comme stockage opérationnel avec une politique de persistance et de récupération approuvée. Cette décision doit être explicite.

L'application doit aussi se comporter correctement lorsque l'une des deux bases est indisponible. Si Redis est indisponible, la stratégie de repli ne doit pas envoyer immédiatement un million de requêtes à MongoDB. Il peut être nécessaire de limiter le trafic, d'utiliser une réponse dégradée, de désactiver temporairement certaines fonctions non essentielles et d'activer des protections contre les pointes. Inversement, si MongoDB est indisponible, Redis peut servir certaines valeurs de cache existantes, mais il ne faut pas prétendre que ces valeurs sont forcément à jour ni permettre des modifications métier incohérentes.

### 14.2 Écrire les contrats opérationnels

Pour chaque famille de clés Redis, documentez : propriétaire, type, schéma, politique TTL, taille attendue, origine, sensibilité, mécanisme d'invalidation, comportement à l'indisponibilité et possibilité de reconstruction. Pour chaque collection MongoDB, documentez les champs obligatoires, l'unicité, les requêtes principales, les index, la croissance, la politique d'archivage et le plan de migration.

Un contrat opérationnel est utile pendant une panne. Par exemple : « la clé cours est un cache dérivable d'un document MongoDB ; elle a une TTL de cinq minutes ; elle est invalidée après modification ; en cas d'indisponibilité Redis, les endpoints critiques continuent sur MongoDB avec une limitation de concurrence ». Un tel contrat permet de discuter la latence, la fraîcheur et la capacité sans ambiguïté.

## 15. Atelier pratique guidé

L'atelier s'exécute dans un environnement de développement jetable. N'utilisez pas une instance de production. Il met en place un exemple minimal, puis demande d'observer et d'expliquer les résultats.

### Étape A — Préparer la collection MongoDB

~~~javascript
use skillmarket_lab

db.courses.insertMany([
  {
    slug: "sql-joins",
    title: "Jointures SQL",
    level: "debutant",
    durationMinutes: 50,
    tags: ["sql", "relations"],
    published: true,
    updatedAt: new Date()
  },
  {
    slug: "mongo-indexes",
    title: "Index MongoDB",
    level: "intermediaire",
    durationMinutes: 70,
    tags: ["nosql", "performance"],
    published: true,
    updatedAt: new Date()
  },
  {
    slug: "redis-cache",
    title: "Cache Redis",
    level: "intermediaire",
    durationMinutes: 45,
    tags: ["nosql", "cache"],
    published: false,
    updatedAt: new Date()
  }
])
~~~

Inspectez ensuite le jeu de données :

~~~javascript
db.courses.find({ published: true }).sort({ title: 1 })
db.courses.countDocuments({ level: "intermediaire" })
db.courses.createIndex({ published: 1, level: 1, title: 1 })
db.courses.find({ published: true, level: "intermediaire" }).explain("executionStats")
~~~

Avant de réexécuter insertMany, souvenez-vous que la première opération insérera des documents supplémentaires ou échouera en cas de conflit lié à une contrainte unique. Un script d'atelier doit prévoir s'il est idempotent ou s'il commence par nettoyer son espace de test. Dans un vrai environnement, n'ajoutez pas un nettoyage global sans vérifier la base ciblée.

### Étape B — Agréger les durées par niveau

~~~javascript
db.courses.aggregate([
  { $match: { published: true } },
  {
    $group: {
      _id: "$level",
      count: { $sum: 1 },
      averageMinutes: { $avg: "$durationMinutes" }
    }
  },
  { $sort: { count: -1, _id: 1 } }
])
~~~

Expliquez pourquoi le document du cours Redis non publié n'est pas comptabilisé. Ajoutez un quatrième document, testez les résultats, puis utilisez $project pour choisir les champs renvoyés.

### Étape C — Créer un cache Redis

~~~redis
SET skillmarket:cache:course:mongo-indexes "{\\"slug\\":\\"mongo-indexes\\",\\"title\\":\\"Index MongoDB\\"}" EX 300
GET skillmarket:cache:course:mongo-indexes
TTL skillmarket:cache:course:mongo-indexes
DEL skillmarket:cache:course:mongo-indexes
GET skillmarket:cache:course:mongo-indexes
~~~

Cette représentation illustre une chaîne qui contient du JSON sérialisé. En application réelle, utilisez un sérialiseur approprié et traitez les erreurs de parsing, les encodages, la version du cache et les champs sensibles. La commande EX associe une expiration à la clé dès sa création. DEL supprime la clé ; la prochaine lecture de l'application doit recharger la source si la clé est de type cache-aside.

### Étape D — Mesurer un classement

~~~redis
ZADD skillmarket:leaderboard:lab 20 learner:alice 35 learner:bob 29 learner:carol
ZREVRANGE skillmarket:leaderboard:lab 0 -1 WITHSCORES
ZINCRBY skillmarket:leaderboard:lab 10 learner:alice
ZREVRANGE skillmarket:leaderboard:lab 0 -1 WITHSCORES
~~~

Faites varier les scores, observez l'ordre et réfléchissez aux égalités. Ajoutez une politique pour le classement hebdomadaire : clés datées, expiration après une durée définie et origine des points. N'oubliez pas que cette démonstration n'est pas un système anti-fraude : elle suppose que la logique d'attribution des points a déjà validé les événements.

### Étape E — Décrire le mode dégradé

Pour les trois fonctions du laboratoire, répondez aux questions suivantes : que se passe-t-il si MongoDB n'est pas joignable ? Si Redis est indisponible ? Si Redis redémarre avec un jeu vide ? Si l'invalidation du cache échoue après une mise à jour ? Si un client répète une requête après un timeout dont l'issue est inconnue ? Les réponses doivent être écrites dans un mini-runbook, pas laissées à l'intuition du développeur de garde.

## 16. Douze exercices corrigés

### Exercice 1 — Choisir la technologie

Un catalogue contient des descriptions longues, des listes d'étiquettes et des champs qui évoluent. Les utilisateurs consultent souvent une fiche complète. Quel modèle mérite d'être évalué en premier ?

**Correction :** MongoDB est un candidat naturel pour une représentation documentaire, car les champs imbriqués peuvent être lus ensemble et évoluer avec une validation appropriée. Le relationnel peut rester pertinent selon les relations et exigences. La décision doit être confirmée par les requêtes, la cohérence attendue, le coût opérationnel et la mesure des performances.

### Exercice 2 — Éviter une liste infinie embarquée

Vous envisagez d'ajouter chaque tentative d'apprenant dans un tableau du document de cours. Pourquoi est-ce risqué ?

**Correction :** Le tableau peut croître sans limite, augmenter la taille du document, rendre chaque écriture plus coûteuse et créer une forte contention autour d'un même document. Une collection séparée avec index adaptés aux consultations par apprenant ou cours sera souvent plus évolutive. Embarquer convient surtout à des sous-objets bornés et généralement lus avec le parent.

### Exercice 3 — Ajouter une validation

La durée d'un cours ne doit jamais être négative ou nulle et doit être numérique. Où définir les règles ?

**Correction :** Dans le modèle applicatif et, en complément, avec un validateur MongoDB qui exige un type numérique approprié et une valeur minimale de 1. Il faut migrer les documents existants avant d'activer une règle stricte. La validation de schéma ne vérifie pas nécessairement les contraintes métier qui dépendent d'autres collections.

### Exercice 4 — Interpréter une requête lente

Une requête MongoDB fait un balayage complet sur une collection énorme alors qu'elle retourne quelques documents. Quelle est la démarche ?

**Correction :** Inspecter explain avec les statistiques d'exécution, confirmer les filtres et le tri réels, étudier la sélectivité et envisager un index pertinent. Tester le plan avant et après sur un volume représentatif. Ne pas créer un index sans considérer le coût d'écriture et la fréquence de la requête.

### Exercice 5 — Comprendre unwind

Une agrégation déplie les étiquettes d'un cours avec trois tags, puis compte les documents. Pourquoi peut-elle compter ce cours trois fois ?

**Correction :** L'étape unwind produit une ligne de pipeline par élément de tableau. Le document source est donc représenté par trois documents de pipeline. Si le but est de compter les cours uniques, il faut grouper de nouveau par identifiant de cours ou réaliser le calcul avant l'expansion selon la logique recherchée.

### Exercice 6 — Choisir un type Redis

Vous devez vérifier rapidement si un apprenant a aimé un cours, sans doublons. Quel type choisir ?

**Correction :** Un ensemble SET est approprié, car chaque membre est unique et SISMEMBER permet de vérifier la présence. Mais si cette action doit être conservée durablement et être auditable, il faut décider si Redis est la source d'autorité ou si l'événement doit être enregistré dans une base durable.

### Exercice 7 — TTL d'une session

Une session Redis ne possède plus de TTL à cause d'une erreur de code. Quel est le risque ?

**Correction :** La session peut demeurer plus longtemps que prévu, augmentant le risque d'accès après la durée de vie attendue et consommant la mémoire. Le code doit définir l'expiration lors de la création ou du renouvellement, et la supervision peut détecter les clés de session sans durée de vie. Une politique de sécurité doit aussi révoquer les sessions lors d'événements sensibles.

### Exercice 8 — Distinguer pipeline et transaction

Un développeur envoie dix commandes Redis avec pipeline et affirme qu'aucun client ne peut intervenir entre elles. Est-ce vrai ?

**Correction :** Non. Le pipeline réduit surtout le nombre d'allers-retours réseau ; il ne garantit pas par lui-même l'atomicité du groupe. Utilisez une transaction ou un script adapté si l'ordre atomique entre commandes est nécessaire, et traitez les résultats et conflits comme le contrat l'exige.

### Exercice 9 — Invalidation du cache

MongoDB a enregistré un nouveau titre de cours, mais Redis sert l'ancien titre. Donnez deux mécanismes à examiner.

**Correction :** Vérifier que l'invalidation ou la mise à jour de clé est appelée après la modification source, et examiner les courses entre une lecture ancienne et une invalidation qui peut être suivie d'une réécriture obsolète. Versionnement de cache, événement durable, réessai d'invalidation, TTL maîtrisée et tests concurrents sont des pistes, selon le niveau de fraîcheur exigé.

### Exercice 10 — RDB ou AOF

Une application peut tolérer quelques minutes de perte de données dérivables. Une autre ne tolère qu'une très faible perte et requiert une reprise contrôlée. Peut-on appliquer la même configuration sans étude ?

**Correction :** Non. RDB fournit un instantané pouvant omettre les écritures postérieures au snapshot. AOF enregistre les opérations d'écriture et permet de régler la politique de synchronisation. La stratégie doit être choisie selon la perte admissible, la latence, la taille, le stockage, les tests de reprise et la politique de sauvegarde externe.

### Exercice 11 — Comprendre la réplication

Un responsable pense que trois répliques Redis rendent les sauvegardes inutiles. Quelle est l'erreur ?

**Correction :** La réplication améliore surtout la disponibilité et la copie de données entre instances. Une suppression ou corruption logique peut se répliquer. Elle ne remplace pas des sauvegardes isolées et testées. Il faut combiner des mécanismes de haute disponibilité avec des sauvegardes et des exercices de restauration.

### Exercice 12 — Définir un mode dégradé

Redis tombe en panne et l'API envoie immédiatement toutes les lectures du cache vers MongoDB. Que risque-t-elle ?

**Correction :** Une surcharge en cascade peut saturer MongoDB, augmenter les latences et provoquer une panne générale. Il faut une stratégie de repli contrôlée : limite de concurrence, circuit breaker, réponses dégradées si acceptable, mise en cache locale limitée ou désactivation temporaire de fonctions non essentielles. Cette stratégie doit préserver les règles d'autorisation et de fraîcheur.

## 17. Défi final corrigé : catalogue de cours et classement hebdomadaire

### Contexte

Vous devez concevoir une version minimale de SkillMarket. MongoDB conserve les cours de référence. Redis sert de cache pour les fiches populaires et tient un classement hebdomadaire. La plateforme doit supporter les mises à jour de cours, les expirations, une panne Redis et une remise en service. Les points du classement ne doivent pas être attribués à partir de paramètres arbitraires fournis par un client non fiable.

### Livrable attendu

Rédigez un document d'architecture comprenant les collections et champs principaux, les index, la validation, les clés Redis, les TTL, la source d'autorité, les règles d'invalidation, la politique de persistance, le plan de sauvegarde et le mode dégradé. Ajoutez trois requêtes MongoDB, une agrégation, au moins quatre commandes Redis et un plan de test d'incident.

### Correction proposée

**MongoDB.** Une collection courses contient slug, title, level, durationMinutes, tags, published et updatedAt. L'identifiant stable de l'application peut être le slug, mais il doit être unique. La validation impose les types attendus, les niveaux autorisés et une durée positive. L'index unique sur slug protège l'invariant d'identification. Un index composé ne sera ajouté qu'après analyse des filtres réellement utilisés par les écrans, par exemple état de publication, niveau et tri par date. Une collection dédiée d'inscriptions évite une liste infinie dans chaque cours.

**Cache.** Une clé telle que skillmarket:cache:course:slug:v1 contient une représentation sérialisée de la fiche. Le suffixe de version facilite une évolution du format ; la TTL est choisie selon la fraîcheur admissible. La lecture passe par Redis puis MongoDB en cas de miss. Une mise à jour réussie dans MongoDB déclenche l'invalidation des clés correspondantes. Le système doit traiter l'échec d'invalidation par réessai et surveillance, et éviter qu'une requête commencée avant la mise à jour réinjecte une valeur ancienne.

**Classement.** Une clé datée par semaine est un ensemble trié. Le service valide les événements de points et ne permet pas au navigateur d'écrire directement des scores arbitraires. Une période datée simplifie l'analyse et la rétention. Si les scores sont dérivables, ils peuvent être reconstruits depuis un journal d'événements durable. Si le jeu Redis fait autorité sur le score, la persistance et les garanties de reprise devront être considérablement plus strictes et testées.

**Dégradation.** Si Redis est en panne, l'API limite la concurrence vers MongoDB et peut dégrader les fonctions de classement. La logique d'autorisation doit continuer de respecter la source fiable ; une clé de session absente ne doit pas automatiquement être interprétée comme une session valide. Si MongoDB est indisponible, certaines fiches déjà en cache peuvent être servies uniquement si leurs règles de fraîcheur autorisent cette dégradation. Les écritures métier doivent échouer explicitement ou entrer dans une file durable avec des garanties documentées ; elles ne doivent pas être confirmées à tort.

**Reprise.** Le runbook identifie les responsables, les signaux de diagnostic, la bascule, les tests de lecture et écriture, la vérification des clés, la validation des données, le contrôle du cache et le retour à un état stable. Les sauvegardes sont stockées séparément des instances qui les produisent. Un exercice périodique mesure effectivement le RPO et le RTO au lieu de les supposer.

**Mesures.** La validation comprend le taux de cache hit, la latence p95/p99 de lecture, le coût des misses, le nombre de documents MongoDB examinés, les évictions Redis, la mémoire, la durée de la restauration et le nombre d'erreurs de reconnexion. Le test de charge couvre des expirations simultanées, les invalidations et une panne temporaire. La décision finale d'architecture doit reposer sur ces résultats.

## 18. Checklist de révision

- [ ] Je sais expliquer pourquoi MongoDB et Redis ne sont pas interchangeables.
- [ ] Je sais décider quels champs doivent être embarqués dans un document et quand utiliser des références.
- [ ] Je peux écrire une requête CRUD, appliquer une validation et construire une agrégation.
- [ ] Je sais lire un explain et relier un index à un profil de requête réel.
- [ ] Je distingue atomicité d'un document et transaction multi-documents.
- [ ] Je sélectionne une structure Redis en fonction des opérations requises.
- [ ] Je définis la TTL, l'invalidation et le traitement d'un cache périmé.
- [ ] Je distingue commande atomique, pipeline, transaction et script.
- [ ] Je comprends les compromis RDB/AOF et les risques de réplication asynchrone.
- [ ] Je peux décrire une procédure de restauration et le mode dégradé de l'application.
- [ ] Je sécurise les réseaux, identifiants, ACL, sauvegardes et données de diagnostic.
- [ ] Je mesure les performances et valide le changement avec un test reproductible.

## 19. Références officielles

- MongoDB Manual, modélisation et bonnes pratiques : https://www.mongodb.com/docs/manual/data-modeling/best-practices/
- MongoDB Manual, validation de schéma : https://www.mongodb.com/docs/manual/core/schema-validation/
- MongoDB Manual, index : https://www.mongodb.com/docs/manual/indexes/
- MongoDB Manual, agrégation : https://www.mongodb.com/docs/manual/aggregation/
- MongoDB Manual, transactions : https://www.mongodb.com/docs/manual/core/transactions/
- MongoDB Manual, replica sets : https://www.mongodb.com/docs/manual/replication/
- Redis documentation, types de données : https://redis.io/docs/latest/develop/data-types/
- Redis documentation, expiration des clés : https://redis.io/docs/latest/develop/use/keyspace/
- Redis documentation, persistance : https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
- Redis documentation, réplication : https://redis.io/docs/latest/operate/oss_and_stack/management/replication/
- Redis documentation, ACL : https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/

Pour approfondir, choisissez un scénario métier et écrivez les requêtes les plus fréquentes avant de choisir un schéma. Construisez ensuite un jeu de données synthétique représentatif, mesurez les opérations, testez une panne et démontrez une restauration. Le niveau intermédiaire se manifeste moins par le nombre de commandes mémorisées que par la capacité à expliquer les compromis, à documenter les invariants et à prouver que le système fonctionne dans les conditions qui comptent.
