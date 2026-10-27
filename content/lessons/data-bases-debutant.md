# Concepts des bases de données relationnelles — Débutant

> **Mise en contexte.** Imaginez une plateforme de formation qui doit mémoriser des apprenants, des cours, des inscriptions et des résultats de quiz. Au début, un tableur unique semble suffisant. Quelques mois plus tard, une personne apparaît sous deux orthographes, un résultat n'a plus d'apprenant identifiable, le nom d'un cours est modifié dans certains fichiers mais pas dans d'autres, et deux personnes réservent la dernière place disponible au même instant. Le problème ne se résout pas en ajoutant davantage de colonnes : il faut représenter les faits, les relations et les règles de cohérence de façon explicite. C'est précisément le rôle d'une base de données relationnelle bien conçue.

## Introduction : pourquoi apprendre les bases avant SQL

Une base de données est un ensemble organisé de données que l'on veut conserver, retrouver, faire évoluer et partager de manière contrôlée. Une base de données relationnelle représente une grande partie de ces informations sous forme de relations, généralement matérialisées par des tables. Chaque table décrit une catégorie de faits ; chaque ligne représente un fait particulier ; chaque colonne exprime une propriété de ce fait. Des clés et des contraintes permettent de relier ces faits sans que leur cohérence repose uniquement sur la discipline des personnes qui les saisissent.

Le mot « relationnel » ne signifie pas simplement que plusieurs tables sont reliées par des flèches. Il désigne un modèle de données fondé sur des relations, avec des règles concernant les valeurs, les lignes et les opérations. Le modèle relationnel permet de décrire les informations indépendamment de l'application qui les utilise. Un site web, un outil mobile, une tâche automatique et une interface d'administration peuvent donc interroger la même source de vérité, chacun avec ses propres droits.

Le but de ce premier cours n'est pas de mémoriser des dizaines de commandes SQL. Il est d'apprendre à raisonner sur les données avant de les manipuler. Dans les cours suivants, vous étudierez plus précisément les requêtes SQL, la modélisation, les jointures, la normalisation et les opérations pratiques. Ici, vous devez d'abord comprendre pourquoi une table existe, comment reconnaître une identité stable, comment une relation exprime une règle métier et pourquoi le moteur doit protéger les données contre des incohérences.

Le fil conducteur sera une petite boutique en ligne. Elle possède des clients, des commandes, des produits et des lignes de commande. Ce cas est volontairement concret : il permet de distinguer le client qui passe commande, la commande qui est créée à une date donnée, le produit qui peut être vendu plusieurs fois et la ligne qui mémorise une quantité et un prix au moment de l'achat. Les mêmes principes s'appliquent à une école, une bibliothèque, une clinique, une entreprise de télécommunications ou un système de gestion de réseau.

À la fin du cours, vous devez pouvoir expliquer avec vos propres mots ce qu'est une base de données relationnelle, distinguer la base du logiciel qui la gère, lire un petit schéma, identifier une clé primaire et une clé étrangère, reconnaître les relations un-à-un, un-à-plusieurs et plusieurs-à-plusieurs, comprendre l'utilité des contraintes, différencier zéro, chaîne vide et valeur inconnue, expliquer l'objectif d'une transaction et réaliser un petit atelier reproductible. Vous devrez également savoir repérer les erreurs de conception les plus courantes et justifier une correction.

## 1. Prérequis, vocabulaire et environnement de travail

Aucune expérience préalable en administration de bases de données n'est nécessaire. Il est utile de savoir ce qu'est un fichier, ce qu'est une application et pourquoi des informations doivent survivre à la fermeture d'un programme. Une connaissance du principe « une donnée a un sens et un format » suffit pour commencer.

Quelques mots seront employés régulièrement :

- **Donnée** : valeur enregistrée, par exemple le prix d'un article ou la date de création d'une commande.
- **Information** : interprétation utile d'une ou plusieurs données dans un contexte. Le nombre 42 est une donnée ; « 42 articles disponibles » est une information si son unité et sa source sont connues.
- **Base de données** : ensemble organisé de données et de structures associées.
- **SGBD** : système de gestion de base de données, c'est-à-dire le logiciel qui reçoit les requêtes, applique les règles, contrôle les accès, gère les transactions et organise le stockage.
- **Schéma** : description structurée des objets de la base, notamment les tables, colonnes, types, contraintes et relations.
- **Requête** : instruction adressée au SGBD pour lire ou modifier les données, ou pour décrire la structure.
- **Métadonnées** : informations qui décrivent les données, comme le type d'une colonne, sa contrainte ou la date de création d'une table.
- **Intégrité** : propriété qui garantit que les données respectent les règles définies et restent cohérentes entre elles.

Pour la pratique, vous pouvez utiliser SQLite, PostgreSQL ou MySQL. SQLite est pratique pour une première expérience locale, car une base peut être conservée dans un fichier et ne nécessite pas de serveur séparé. PostgreSQL et MySQL sont fréquents dans les applications multi-utilisateurs et les environnements de production. Ils ont des différences de syntaxe, de types, de gestion des identifiants et de configuration ; il ne faut donc pas supposer qu'une commande fonctionnera exactement de la même manière partout.

Avant tout exercice, isolez le laboratoire des données réelles. Travaillez avec des informations fictives, gardez une copie du script et vérifiez la cible avant une opération destructive. Ne placez jamais de mot de passe, de clé d'API ou de secret dans le script de cours, les captures d'écran ou les journaux. Un environnement d'apprentissage doit pouvoir être réinitialisé sans mettre une organisation en danger.

## 2. Base, SGBD, serveur et application : quatre notions différentes

Une erreur fréquente consiste à employer les expressions « base de données » et « serveur de base de données » comme si elles désignaient le même objet. Elles sont liées, mais différentes.

La base est l'ensemble logique des données et de leur structure. Le SGBD est le logiciel qui gère ces données. Dans certaines installations, un processus serveur reçoit les connexions des applications. Dans d'autres, comme SQLite, l'application utilise une bibliothèque qui lit et écrit directement un fichier de base. L'application métier est un quatrième élément : elle présente des écrans, valide des formulaires, applique une partie des règles métier et envoie des opérations au SGBD.

~~~mermaid
flowchart LR
    U[Utilisateur] --> A[Application]
    A -->|requête contrôlée| S[SGBD]
    S --> R[Schéma et règles]
    S --> D[(Données persistantes)]
    S --> L[Journaux et mécanismes de reprise]
    D --> S
    S -->|résultat ou erreur| A
    A --> U
~~~

Ce schéma représente une architecture courante. Il ne signifie pas que chaque base possède un service serveur distinct : avec SQLite, la zone SGBD correspond à la bibliothèque utilisée par l'application. Le point important est la séparation des responsabilités. L'application ne doit pas être considérée comme la seule gardienne de l'intégrité. Si une règle doit être vraie pour toutes les opérations, il est souvent préférable de la représenter dans la base elle-même.

Prenons une règle simple : une quantité commandée doit toujours être supérieure à zéro. Un formulaire peut refuser la valeur zéro, mais un script d'import, une autre application ou une requête exécutée par un administrateur pourrait contourner ce formulaire. Une contrainte dans la base peut fournir une protection commune. L'application conserve un rôle important pour expliquer l'erreur à l'utilisateur, mais elle n'est plus l'unique barrière.

La base n'est pas non plus un simple fichier texte. Selon le SGBD, les données peuvent être réparties dans des pages, des fichiers, des journaux, des index et des structures de contrôle. Le logiciel gère ces éléments pour fournir un comportement cohérent. Il est rarement nécessaire de modifier directement ces fichiers internes. La voie normale passe par les commandes et interfaces prévues par le SGBD.

Une application peut être arrêtée alors que la base reste disponible. Une base peut exister sans interface graphique. Plusieurs applications peuvent partager les mêmes données si les droits, les connexions et les règles le permettent. À l'inverse, une application peut utiliser plusieurs bases pour des besoins différents. Ces distinctions sont utiles lors d'un incident : un écran vide n'implique pas automatiquement que les données ont disparu ; il peut s'agir d'une erreur réseau, d'un problème d'authentification, d'une requête incorrecte ou d'un défaut dans le code de présentation.

## 3. Pourquoi ne pas tout conserver dans un seul tableur ?

Un tableur est utile pour calculer, explorer un jeu de données limité ou partager une analyse ponctuelle. Le problème apparaît lorsqu'il devient, sans conception préalable, le système central d'une activité. Les mêmes faits sont alors souvent copiés dans plusieurs feuilles ou fichiers. Les règles restent implicites et les modifications concurrentes sont difficiles à coordonner.

Imaginons une feuille contenant les colonnes suivantes : identifiant client, nom du client, courriel, numéro de commande, date de commande, identifiant produit, nom du produit, quantité et prix. Une commande avec trois produits doit occuper trois lignes. Le nom et le courriel du client sont alors répétés trois fois. Chaque nouvelle commande répète à son tour les coordonnées. Une correction du courriel exige de modifier toutes les lignes qui le contiennent. Si une seule ligne est oubliée, l'organisation possède désormais deux versions contradictoires du même fait.

Ce phénomène produit trois catégories de problèmes, souvent appelées anomalies :

1. **Anomalie de mise à jour** : un fait est copié à plusieurs endroits et toutes les copies ne sont pas modifiées.
2. **Anomalie d'insertion** : il devient difficile d'enregistrer un fait tant qu'un autre fait n'existe pas, même s'ils sont conceptuellement indépendants.
3. **Anomalie de suppression** : retirer un enregistrement peut effacer involontairement la seule copie d'une information qui devait être conservée.

Ces anomalies sont des indices de conception, pas une condamnation automatique des tableurs. Pour une analyse ponctuelle, un tableau peut être suffisant. Pour un système partagé qui conserve des faits évolutifs, une base relationnelle permet de séparer les entités, de relier leurs identifiants et de faire appliquer les règles de façon systématique.

Il faut également éviter l'idée inverse : une base de données ne corrige pas par magie un mauvais modèle. Si les colonnes ont un sens flou, si les identifiants sont instables ou si les règles métier ne sont pas comprises, le SGBD peut conserver des informations incohérentes de façon parfaitement durable. La qualité dépend à la fois du modèle, des contraintes, des procédures d'exploitation et de la qualité des données reçues.

## 4. Tables, lignes, colonnes et domaines de valeurs

Une table représente une catégorie de faits. Dans notre boutique, une table CLIENTS décrit les clients, une table PRODUITS décrit les produits commercialisables, une table COMMANDES décrit les commandes et une table LIGNES_COMMANDE décrit les produits et quantités associés à chaque commande.

Une ligne représente un enregistrement particulier. Par exemple, une ligne de CLIENTS correspond à un client déterminé. Une colonne représente une propriété de ce type d'enregistrement, comme le nom ou l'adresse électronique. Chaque colonne possède une définition de type et peut être soumise à des contraintes.

Un type n'est pas une décoration. Il indique quelles valeurs sont acceptables et quelles opérations ont un sens. Une date ne devrait pas être stockée arbitrairement comme un texte dont le format varie selon la personne qui saisit l'information. Une quantité doit être représentée comme une valeur numérique adaptée, et un montant doit éviter les approximations propres à certains formats flottants binaires lorsqu'une précision décimale exacte est attendue.

Quelques types rencontrés fréquemment :

| Besoin | Famille de type habituelle | Point d'attention |
|---|---|---|
| Identifiant entier | entier | gérer l'unicité et la génération |
| Nom ou intitulé | texte à longueur variable | préciser longueur raisonnable et règles de saisie |
| Date | type date | ne pas confondre date civile et instant horodaté |
| Instant d'événement | horodatage | préciser le fuseau horaire et la convention |
| Quantité entière | entier | imposer une borne cohérente |
| Montant | décimal exact | préciser la devise et l'échelle |
| État limité | texte avec contrainte, référence ou enum selon le moteur | éviter les valeurs arbitraires |
| Information facultative | type approprié acceptant éventuellement NULL | définir ce que signifie l'absence |

Les moteurs n'ont pas tous le même système de types. SQLite, par exemple, utilise une approche de typage différente de celle de PostgreSQL ; MySQL possède ses propres choix de types et modes de configuration. Pour les concepts, retenez la règle générale ; pour la syntaxe et les limites exactes, consultez la documentation du moteur et de sa version.

Une colonne doit également avoir un sens métier stable. Si une colonne nommée prix contient parfois des euros, parfois des dollars et parfois des centimes, son nom ne suffit pas à la rendre compréhensible. Si une colonne état accepte les valeurs « nouveau », « neuf », « fresh », « 1 », « ok » et « normal », les traitements deviendront fragiles. Il faut convenir d'un vocabulaire contrôlé, documenter la signification des valeurs et appliquer ce contrat.

Les colonnes ne doivent pas représenter plusieurs faits différents à la fois. Un champ « adresse complète » peut être utile pour un affichage simple, mais si l'application doit rechercher séparément la ville, le pays et le code postal, des attributs distincts peuvent être nécessaires. Cela ne signifie pas qu'il faut découper chaque phrase en dizaines de colonnes : la bonne granularité dépend des usages, des règles et des exigences d'évolution.

## 5. Le schéma relationnel : séparer les faits tout en conservant les liens

Le schéma relationnel décrit les tables et la manière dont elles se relient. Il aide à répondre à plusieurs questions : quelles entités existent ? quels attributs décrivent chacune d'elles ? quel identifiant désigne une ligne sans ambiguïté ? comment un fait peut-il faire référence à un autre ? quelles valeurs sont obligatoires ? quelles règles doivent être vérifiées par la base ?

Pour notre boutique, le modèle de départ peut comprendre quatre tables :

- CLIENTS : une ligne par client.
- COMMANDES : une ligne par commande, rattachée au client qui l'a passée.
- PRODUITS : une ligne par produit dans le catalogue.
- LIGNES_COMMANDE : une ligne par produit présent dans une commande, avec la quantité et le prix appliqué au moment de la vente.

~~~mermaid
erDiagram
    CLIENTS ||--o{ COMMANDES : "passe"
    COMMANDES ||--|{ LIGNES_COMMANDE : "contient"
    PRODUITS ||--o{ LIGNES_COMMANDE : "apparait dans"
    CLIENTS {
        int client_id PK
        string nom
        string email
    }
    COMMANDES {
        int commande_id PK
        int client_id FK
        date date_commande
        string statut
    }
    PRODUITS {
        int produit_id PK
        string nom
        decimal prix_catalogue
    }
    LIGNES_COMMANDE {
        int commande_id PK, FK
        int produit_id PK, FK
        int quantite
        decimal prix_unitaire
    }
~~~

Ce diagramme est une représentation logique. Il ne décrit pas la disposition physique des pages sur le disque et ne précise pas tous les détails d'indexation. La notation exacte d'un outil peut varier ; ici, PK signifie clé primaire et FK clé étrangère.

La table LIGNES_COMMANDE est indispensable. Une commande peut inclure plusieurs produits, et un produit peut apparaître dans plusieurs commandes. Cette situation est une relation plusieurs-à-plusieurs. Dans un modèle relationnel classique, on la représente au moyen d'une table intermédiaire qui porte les deux références et les propriétés spécifiques à la relation, comme la quantité vendue et le prix appliqué. Répéter « produit 8, produit 15, produit 42 » dans des colonnes d'une table COMMANDES rendrait la structure rigide et limiterait les requêtes possibles.

Pourquoi enregistrer le prix unitaire dans LIGNES_COMMANDE si PRODUITS possède déjà un prix catalogue ? Parce que le prix catalogue peut changer, alors que le montant d'une vente passée doit refléter les conditions au moment de cette vente. Si un produit coûtait 25,00 au moment de la commande, une modification du prix catalogue à 27,00 ne devrait pas réécrire silencieusement l'historique de la vente. Le champ prix_unitaire de la ligne est un fait historique distinct du prix courant du produit.

Ce principe ne justifie pas la duplication de toutes les informations. La copie du prix de vente est volontaire, limitée et liée à un événement métier. Le nom du client, lui, n'a pas besoin d'être recopié dans chaque ligne de commande pour identifier le client : la commande porte une référence vers CLIENTS. Il faut toujours demander pourquoi une valeur est conservée à plusieurs endroits et quelle règle garantit que les copies ne se contredisent pas.

## 6. Identifiants et clés : donner une identité stable aux lignes

Une ligne doit pouvoir être distinguée des autres. La clé primaire est la colonne, ou le groupe de colonnes, retenu comme identifiant principal d'une table. Elle doit être unique et non nulle. Elle permet notamment de cibler une ligne lors d'une modification, de faire référence à cette ligne depuis une autre table et de reconnaître le même enregistrement au cours du temps.

Pour CLIENTS, on peut choisir client_id. Pour PRODUITS, produit_id. Pour COMMANDES, commande_id. Une clé composée est possible lorsque plusieurs colonnes forment ensemble l'identité voulue. Par exemple, dans LIGNES_COMMANDE, le couple commande_id et produit_id peut identifier une ligne si le modèle décide qu'un produit ne peut apparaître qu'une seule fois dans une commande. Si le même produit peut être réparti entre plusieurs lignes pour des raisons commerciales, il faudra choisir une autre règle d'identité, comme un numéro de ligne en plus du numéro de commande.

Une clé dite naturelle provient du domaine métier : numéro national de référence, code produit ou identifiant métier défini par l'organisation. Une clé dite technique ou surrogate est créée principalement pour identifier l'enregistrement dans le système, sans signification métier directe. Les deux approches ont des usages. Une clé naturelle peut déjà exister et posséder une sémantique claire, mais elle peut changer, avoir une longueur importante ou être sensible. Une clé technique est généralement stable et simple à référencer, mais ne remplace pas les règles d'unicité du domaine métier.

Par exemple, un identifiant numérique client peut servir de clé primaire, tandis que le courriel reste soumis à une contrainte d'unicité si le métier exige qu'un courriel ne soit rattaché qu'à un seul compte actif. Il faut toutefois vérifier la règle réelle : certaines applications autorisent plusieurs personnes à partager une adresse, les courriels peuvent changer et l'identité d'une personne ne devrait pas toujours être déduite d'une adresse électronique.

Une clé primaire composée n'est pas inférieure par nature à une clé simple. Elle exprime simplement qu'il faut plusieurs valeurs pour identifier l'enregistrement. Un exemple courant est une table d'association entre étudiant et cours, où le couple (etudiant_id, cours_id) interdit deux inscriptions identiques au même cours. Si l'inscription possède une histoire propre, un statut, une date ou des tentatives multiples, le modèle peut avoir besoin d'un identifiant supplémentaire et d'une contrainte unique appropriée.

~~~mermaid
flowchart TD
    A["Choisir un identifiant"] --> B{"Existe-t-il une clé métier stable ?"}
    B -->|Oui, et sa stabilité est démontrée| C["Évaluer son usage comme clé"]
    B -->|Non ou risque de changement| D["Envisager une clé technique"]
    C --> E["Ajouter les contraintes utiles"]
    D --> E
    E --> F["Tester doublons, valeurs nulles et références"]
~~~

Ne choisissez pas un identifiant uniquement parce qu'il « semble unique » dans les dix lignes de test. Vérifiez si cette propriété sera vraie dans le temps et dans tous les canaux de création. Un prénom, un nom complet ou une date de naissance ne forme généralement pas un identifiant fiable. Deux personnes peuvent partager ces valeurs. Un numéro de téléphone ou une adresse peut changer. Même un code venant d'un système extérieur doit être accompagné d'une règle explicite et d'une stratégie en cas de collision.

## 7. Clé étrangère : rendre une relation vérifiable

Une clé étrangère est une colonne, ou un groupe de colonnes, qui fait référence à une clé candidate d'une autre table, souvent la clé primaire. Elle exprime qu'une valeur doit correspondre à un enregistrement parent existant, selon les règles de la contrainte. Elle rend possible l'intégrité référentielle : la base protège la cohérence des liens au lieu de s'en remettre à une vérification ponctuelle dans chaque application.

Dans notre boutique, COMMANDES.client_id fait référence à CLIENTS.client_id. Une commande ne doit pas désigner un client inexistant. LIGNES_COMMANDE.commande_id fait référence à une commande existante et LIGNES_COMMANDE.produit_id à un produit existant. La relation ne garantit pas que le produit est disponible en stock ou que le client a le droit d'acheter : ces règles métier sont distinctes. Elle garantit que la référence ne pointe pas vers une identité absente.

~~~mermaid
flowchart LR
    C["CLIENTS<br/>client_id = 17"] -->|référence valide| O["COMMANDES<br/>client_id = 17"]
    O --> L["LIGNES_COMMANDE"]
    P["PRODUITS<br/>produit_id = 42"] --> L
    X["Commande avec client_id = 999"] -. "rejetée si client 999 absent" .-> C
~~~

Une clé étrangère n'est pas simplement une convention de nommage. Le fait qu'une colonne s'appelle client_id ne suffit pas à créer une règle. La contrainte doit être déclarée dans le schéma et activée selon les modalités du moteur. Les applications doivent également gérer le rejet d'une opération qui violerait cette contrainte.

La suppression d'un enregistrement parent demande une décision particulière. Si un client possède des commandes historiques, faut-il autoriser la suppression du client ? Faut-il bloquer cette suppression, anonymiser le client, conserver un compte désactivé ou appliquer une autre politique légale et métier ? L'option CASCADE peut transmettre une suppression aux lignes dépendantes ; elle ne doit pas être utilisée machinalement. Une commande ou une facture peut devoir être conservée pour audit, comptabilité ou obligation réglementaire. La politique de suppression doit être décidée avant la mise en production.

De façon générale, les actions possibles comprennent le blocage, la cascade et, selon le moteur et le modèle, la mise à NULL de la référence. Les détails exacts et les noms d'options varient. SET NULL suppose notamment que la colonne accepte NULL, et son sens métier doit rester cohérent. Pour un débutant, le réflexe le plus sûr est de commencer par une politique restrictive et de concevoir explicitement le comportement de suppression plutôt que de choisir CASCADE par facilité.

Les clés étrangères ne remplacent pas une stratégie de sauvegarde. Elles protègent certaines incohérences lors des opérations normales, mais ne garantissent pas la disponibilité du service, la validité commerciale de chaque donnée ni la récupération après une panne. Elles peuvent aussi ne pas empêcher une corruption externe du fichier ou une mauvaise procédure d'administration. Les garanties sont puissantes mais limitées à leur rôle.

## 8. Les principales cardinalités

La cardinalité indique combien d'enregistrements d'un côté peuvent correspondre à ceux de l'autre. Il est important de l'exprimer dans les deux sens : « un client peut passer plusieurs commandes » n'implique pas que « une commande peut appartenir à plusieurs clients ».

### Relation un-à-un

Dans une relation un-à-un, chaque enregistrement d'une entité est lié à au plus un enregistrement d'une autre entité, et inversement selon la règle métier. Par exemple, un équipement peut avoir une fiche d'inventaire détaillée unique séparée pour des raisons de permissions ou de cycle de vie. Il faut toutefois se demander si deux tables sont vraiment nécessaires : si les données ont toujours la même durée de vie et les mêmes droits d'accès, une seule table peut être plus simple.

Pour réaliser une relation un-à-un, une clé étrangère avec contrainte UNIQUE peut limiter à une seule ligne enfant par parent. Une relation « un-à-un » n'est pas créée uniquement par deux colonnes qui se ressemblent.

### Relation un-à-plusieurs

Dans une relation un-à-plusieurs, un enregistrement parent peut être associé à plusieurs enfants, tandis que chaque enfant est associé à un parent déterminé. Un client peut passer plusieurs commandes, mais chaque commande doit être rattachée à un seul client. La clé étrangère se trouve généralement dans la table du côté « plusieurs », ici COMMANDES.

### Relation plusieurs-à-plusieurs

Dans une relation plusieurs-à-plusieurs, plusieurs éléments d'un côté peuvent être associés à plusieurs éléments de l'autre. Une commande contient plusieurs produits et un même produit peut apparaître dans plusieurs commandes. On ajoute une table d'association qui porte les références et les attributs propres à la relation.

~~~mermaid
flowchart TB
    subgraph Parent
      C1["Client A"]
      C2["Client B"]
    end
    subgraph Child
      O1["Commande 100"]
      O2["Commande 101"]
      O3["Commande 102"]
    end
    C1 --> O1
    C1 --> O2
    C2 --> O3
~~~

Pour vérifier une cardinalité, décrivez une règle dans un langage naturel qui ne laisse aucune ambiguïté. « Un client peut posséder plusieurs commandes » est une règle ; « une commande peut avoir zéro ou plusieurs lignes » est une autre. La présence d'une ligne de commande peut être obligatoire dans une commande validée, mais pas forcément dans une commande en brouillon. Cette différence révèle qu'une cardinalité peut dépendre de l'état métier. Le simple diagramme doit alors être complété par des règles de transition ou des validations supplémentaires.

Ne confondez pas la cardinalité et la quantité métier. Une commande peut avoir plusieurs lignes ; une ligne peut avoir une quantité de 1, 2 ou 50 unités. Le nombre de lignes et le nombre d'unités commandées ne sont pas la même chose. De même, un produit peut être présent dans de nombreuses commandes sans que cela indique le nombre d'articles actuellement disponibles en stock.

## 9. Contraintes : transformer les règles en protections durables

Une contrainte est une règle déclarée dans la base et vérifiée par le SGBD lors des opérations concernées. Elle documente le modèle et empêche certaines valeurs invalides d'être enregistrées. Une conception robuste cherche à mettre chaque règle au bon endroit : l'interface aide la personne, l'application explique le comportement et la base protège la cohérence des données partagées.

Les contraintes courantes sont :

- **PRIMARY KEY** : identifie les lignes et impose unicité et absence de NULL pour la clé.
- **FOREIGN KEY** : vérifie une référence entre tables.
- **NOT NULL** : interdit l'absence de valeur pour une colonne.
- **UNIQUE** : interdit les doublons dans la combinaison de colonnes ciblée, selon le comportement du moteur concernant NULL.
- **CHECK** : contrôle une condition sur les valeurs d'une ligne.
- **DEFAULT** : fournit une valeur par défaut lorsque l'insertion omet la colonne, selon la syntaxe et les règles du moteur. Une valeur par défaut n'est pas en soi une validation de toutes les valeurs possibles.

Exemples de règles métier : une quantité commandée doit être strictement positive ; un prix ne doit pas être négatif ; le statut d'une commande doit appartenir à une liste connue ; un identifiant de client doit référencer un client existant. Le modèle doit distinguer les invariants stables des décisions qui dépendent de processus plus complexes.

~~~sql
CREATE TABLE produits (
    produit_id INTEGER PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    prix_catalogue DECIMAL(10,2) NOT NULL CHECK (prix_catalogue >= 0),
    actif VARCHAR(3) NOT NULL CHECK (actif IN ('oui', 'non'))
);
~~~

Cet exemple illustre plusieurs principes, mais n'est pas un modèle universel de type portable à tous les moteurs. La prise en charge, l'application stricte des contraintes, les types et les règles de conversion peuvent différer. Il faut valider le script sur le SGBD réellement utilisé. Une bonne contrainte est écrite pour refléter une règle métier comprise, pas simplement parce qu'une syntaxe est disponible.

Une contrainte doit être suffisamment précise pour être utile et suffisamment juste pour ne pas bloquer des données légitimes. Par exemple, interdire les prix négatifs est souvent logique pour un produit standard, mais les montants négatifs peuvent être valides dans une table d'écritures comptables qui représente des crédits et débits selon une convention différente. La bonne règle dépend du sens de la colonne, de l'unité et du processus.

Une autre erreur consiste à transformer une hypothèse temporaire en invariant permanent. Supposons que les clients résident uniquement dans un pays lors du premier déploiement. Une contrainte qui accepte uniquement ce pays pourrait bloquer l'expansion prévue vers d'autres marchés. Les règles doivent être établies avec le métier et versionnées comme du code. Elles ne sont ni arbitraires ni immuables ; elles doivent évoluer par des migrations contrôlées.

Enfin, distinguez « valeur techniquement valide » et « fait métier vrai ». La base peut vérifier qu'un courriel respecte une longueur ou qu'un statut appartient à une liste. Elle ne peut pas déduire automatiquement que le courriel appartient réellement à la bonne personne. Elle peut imposer qu'une quantité soit positive, mais la disponibilité du stock au moment exact de l'achat demande une opération cohérente et éventuellement une gestion de concurrence. Toute protection a un périmètre à définir.

## 10. NULL, zéro, chaîne vide et absence d'information

Les débutants pensent parfois que NULL équivaut à zéro, à une chaîne vide ou à une valeur « non applicable ». Ce n'est pas le cas. NULL représente l'absence d'une valeur connue ou enregistrée, selon le contrat de la colonne. Cette absence peut signifier que l'information n'a pas encore été fournie, qu'elle est inconnue ou que le modèle a explicitement choisi de ne pas la renseigner. Le sens exact doit être documenté.

Zéro est une valeur numérique. Une chaîne vide est une valeur textuelle de longueur nulle. « Inconnu » peut être une absence de valeur, mais un statut explicite peut parfois être nécessaire pour distinguer « non demandé », « refusé », « en attente de confirmation » et « connu ». Ne multipliez pas les valeurs codées sans raison : « N/A », « aucun », « inconnu », « -1 » et « 0 » ne doivent pas servir de substituts improvisés à NULL.

SQL utilise une logique à trois valeurs dans de nombreuses expressions : une comparaison avec NULL n'est pas vraie ou fausse de la même manière qu'une comparaison classique. Elle peut produire UNKNOWN, souvent traduit par inconnu. On utilise généralement IS NULL et IS NOT NULL pour tester l'absence. Le comportement détaillé des fonctions, des contraintes et de UNIQUE concernant NULL doit être vérifié dans le moteur concerné.

Prenons un exemple : date_retour dans une table de prêts. Si le prêt n'est pas encore terminé, date_retour peut être NULL. La valeur NULL ne signifie pas que le prêt a été rendu à minuit ou à une date zéro ; elle signifie qu'aucune date de retour n'est enregistrée. La règle « un prêt actif n'a pas encore de date de retour » peut être liée au statut du prêt et mérite une définition explicite.

Une colonne obligatoire et une valeur inconnue ne sont pas toujours compatibles. Si un enregistrement ne peut pas être créé sans pays de résidence, la colonne peut être NOT NULL. Si l'information est facultative, NULL peut être permis. Mais si l'organisation a besoin de distinguer l'absence temporaire d'une réponse négative, un statut dédié peut rendre la donnée plus explicite. Le bon choix dépend des questions qu'on devra poser sur les données.

## 11. Transactions et cohérence des opérations

Une transaction regroupe une suite d'opérations qui doivent être traitées comme une unité cohérente. Imaginez une commande : il faut créer l'entête de commande, ajouter ses lignes, mettre à jour la réservation ou le stock, puis confirmer l'opération. Si une étape échoue après que les premières ont été enregistrées, le système risque de conserver un état partiel qui ne correspond à aucun état métier valide.

Le modèle ACID résume quatre propriétés classiquement recherchées dans une transaction :

- **Atomicité** : la transaction est appliquée comme un tout ou annulée comme un tout, dans les limites des garanties du moteur et de ses opérations.
- **Cohérence** : les transactions doivent préserver les invariants définis par le modèle et les règles de l'application.
- **Isolation** : les transactions concurrentes ne doivent pas produire d'interférences interdites par le niveau d'isolation et les garanties du SGBD.
- **Durabilité** : après une validation confirmée, les changements doivent survivre aux défaillances couvertes par les garanties de durabilité du système.

~~~mermaid
flowchart TD
    A[Début de la transaction] --> B[Créer la commande]
    B --> C[Ajouter les lignes]
    C --> D[Vérifier et réserver le stock]
    D --> E{Toutes les étapes réussissent ?}
    E -->|Oui| F[COMMIT : valider]
    E -->|Non| G[ROLLBACK : annuler]
    F --> H[État cohérent confirmé]
    G --> I[Repartir de l'état précédent]
~~~

Dans cet exemple, COMMIT demande au SGBD de confirmer la transaction ; ROLLBACK demande son annulation avant validation. Les interfaces et les comportements exacts varient, et certaines opérations DDL ou opérations administratives peuvent se comporter différemment selon le moteur. Il ne faut pas supposer qu'un seul bloc de code forme une transaction correctement gérée sans comprendre les règles de la connexion utilisée.

L'atomicité ne signifie pas que toute l'activité d'une entreprise est automatiquement couverte par une unique transaction. Si une application appelle un prestataire de paiement externe, envoie un courriel et écrit dans une base, ces actions n'appartiennent pas nécessairement au même mécanisme transactionnel. Des stratégies applicatives supplémentaires peuvent être nécessaires pour gérer les échecs partiels, les répétitions et la réconciliation.

L'isolation mérite également une compréhension pratique. Deux clients peuvent tenter de commander la dernière unité d'un produit. Si le système lit simplement le stock disponible puis le décrémente plus tard, les deux opérations pourraient croire que la dernière unité leur est accessible. Le système doit organiser la vérification et la modification de manière sûre, en utilisant les garanties de concurrence adaptées. Les mécanismes exacts varient selon le SGBD, le niveau d'isolation et la manière dont les requêtes sont écrites.

La durabilité n'est pas l'équivalent d'une stratégie de sauvegarde complète. Elle concerne la persistance des changements confirmés face aux défaillances couvertes par le moteur et sa configuration. Les sauvegardes, les tests de restauration, la réplication, la surveillance du stockage et les procédures de reprise restent nécessaires. Une sauvegarde dont personne n'a jamais testé la restauration n'apporte pas une preuve suffisante de capacité de reprise.

## 12. Modèle conceptuel, logique et physique

Il est utile de distinguer trois vues du même système.

Le **modèle conceptuel** exprime les concepts du métier sans imposer de détail de stockage. Il décrit par exemple qu'un client passe des commandes et qu'une commande contient des produits. Il sert à vérifier le sens avec les personnes qui comprennent le processus.

Le **modèle logique relationnel** précise les tables, attributs, clés et relations. Il transforme les entités et liens en structures pouvant être traduites en SQL. À ce stade, on s'intéresse à la cohérence de la représentation, aux identifiants et aux règles.

Le **modèle physique** tient compte du SGBD choisi et des décisions de réalisation : types précis, index, partitionnement éventuel, organisation du stockage, paramètres, stratégie de sauvegarde et contraintes propres au moteur. Il répond aussi aux exigences de performance, de disponibilité et d'exploitation.

~~~mermaid
flowchart TB
    A["Besoin métier<br/>Qui fait quoi, quand, pourquoi ?"] --> B["Modèle conceptuel<br/>Entités et associations"]
    B --> C["Modèle logique<br/>Tables, colonnes, clés, contraintes"]
    C --> D["Modèle physique<br/>Types du moteur, index, stockage"]
    D --> E["Implémentation et tests"]
    E --> F["Surveillance, retours et évolution"]
    F -. "révision contrôlée" .-> B
~~~

Ces étapes ne doivent pas devenir un processus rigide où le modèle n'est jamais ajusté. Le modèle est une hypothèse structurée qui doit être confrontée aux usages réels, aux règles de conservation et aux scénarios de défaillance. Une découverte peut conduire à modifier une association ou à ajouter un attribut. Toute modification doit néanmoins être évaluée, testée et déployée de manière contrôlée.

Ne commencez pas par optimiser une table qui n'a pas encore de sens métier clair. À l'inverse, ne considérez pas que la conception logique suffit lorsque le système doit gérer des millions de lignes, des accès concurrents ou une disponibilité exigeante. La conception et l'exploitation sont liées, mais il est plus simple de distinguer les questions de sens, d'intégrité et de performance avant de les réunir dans une solution finale.

## 13. Sources de vérité, qualité et sécurité

Une source de vérité est le système ou l'enregistrement retenu comme référence pour un fait donné. Si le prix courant d'un produit est maintenu dans la base du catalogue, une copie dans un fichier CSV exporté n'est généralement qu'un instantané. Une application peut utiliser un cache pour accélérer ses lectures, mais il faut décider quand ce cache est rafraîchi et comment réagir lorsqu'il devient obsolète.

Il faut toutefois éviter de désigner une seule base comme source de vérité universelle lorsque plusieurs domaines métier ont leur propre responsabilité. Un outil de facturation peut être la référence pour le statut d'une facture, tandis qu'un système de catalogue est la référence pour la description actuelle d'un produit. La frontière doit être documentée, sinon des systèmes différents peuvent tenter de modifier les mêmes faits sans stratégie commune.

La qualité des données commence avant l'insertion. Les données importées d'un fichier externe peuvent comporter des doublons, des dates incohérentes, des espaces superflus, des valeurs mal encodées ou des identifiants qui ne correspondent plus à la source. Une base peut rejeter certaines anomalies si des contraintes sont en place, mais il faut aussi planifier la détection, le nettoyage et la correction des données existantes. Désactiver les contraintes pour que l'import passe n'est pas une solution durable.

La sécurité doit être conçue dès le départ. Les comptes applicatifs ne doivent pas utiliser systématiquement un compte administrateur. Les droits doivent être limités aux opérations nécessaires ; les secrets doivent être conservés dans un mécanisme adapté ; les connexions doivent être protégées selon le contexte ; les exports doivent être contrôlés ; les traces ne doivent pas exposer inutilement des données personnelles. Une base relationnelle ne rend pas automatiquement les données privées ou conformes aux règles applicables.

Il faut aussi minimiser les données collectées. Si une fonctionnalité n'a pas besoin de la date de naissance complète, la conserver sans nécessité peut augmenter le risque. Une base bien structurée n'est pas seulement une base où les requêtes sont correctes : c'est aussi une base dont les données sont pertinentes, l'accès justifié, la conservation définie et la suppression traitée de manière appropriée.

## 14. Les erreurs de conception à reconnaître tôt

**Utiliser un nom comme identifiant.** Deux personnes ou deux produits peuvent porter le même nom. Un nom peut changer. Il est rarement une clé primaire fiable à lui seul. Choisissez une identité stable et déclarez les contraintes métier supplémentaires nécessaires.

**Mettre plusieurs valeurs dans une seule colonne.** Une colonne contenant « 12,15,19 » pour représenter plusieurs produits devient difficile à interroger, contrôler et modifier. Une table de relation est généralement plus adaptée lorsqu'un fait peut avoir plusieurs occurrences.

**Créer une colonne par occurrence possible.** Les colonnes produit_1, produit_2 et produit_3 limitent artificiellement le nombre de produits par commande et imposent des requêtes complexes. La table LIGNES_COMMANDE permet de représenter un nombre variable de produits avec la même structure.

**Copier les détails courants partout.** Répéter le nom du produit dans chaque commande risque de créer des versions contradictoires. Certaines valeurs historiques doivent être conservées volontairement, comme le prix appliqué au moment d'une vente ; les autres copies demandent une justification.

**Ne pas représenter les références.** Si une commande contient le nombre 45 dans une colonne client_id sans clé étrangère, rien ne garantit qu'un client 45 existe. Une référence déclarée permet au SGBD d'appliquer cette règle.

**Confondre valeur absente et zéro.** Un stock inconnu n'est pas nécessairement un stock égal à zéro. Utiliser -1, une chaîne vide ou un mot arbitraire comme valeur de remplacement peut rendre les calculs et rapports erronés.

**Accepter toutes les valeurs dans une colonne de statut.** Les variantes « envoyé », « expédié », « ship », « 2 » et « done » compliquent les traitements. Définissez les valeurs possibles et le sens de chacune d'elles.

**Supposer qu'une contrainte corrige des données anciennes.** Ajouter une règle peut échouer si les données existantes la violent. Il faut détecter les incohérences, décider d'une correction et planifier la migration avant le déploiement.

**Supprimer une ligne sans comprendre ses dépendances.** Une suppression peut être interdite par une clé étrangère ou se propager si une cascade a été déclarée. Le comportement doit être décidé et testé, notamment pour les données historiques.

**Tester uniquement le scénario idéal.** Une table peut sembler correcte avec trois enregistrements propres, puis révéler des défauts lorsqu'on tente un doublon, une valeur nulle, une référence inexistante ou deux mises à jour concurrentes. Testez les limites et les scénarios de rejet.

## 15. Atelier pratique guidé : construire le modèle d'une petite boutique

L'objectif de l'atelier est de créer une base simple qui représente des clients, des commandes, des produits et des lignes de commande. Vous allez pratiquer la lecture d'un schéma, créer quelques tables, insérer des données synthétiques, observer des relations et vérifier certaines règles. Cet atelier introduit seulement les commandes nécessaires à la démonstration ; les requêtes SQL seront étudiées plus en détail dans les modules suivants.

### Étape 1 : définir les règles métier avant les tables

Notez les règles suivantes avant de commencer :

1. Chaque client possède un identifiant stable.
2. Une commande appartient à un seul client.
3. Un client peut passer plusieurs commandes.
4. Chaque produit possède un identifiant et un prix catalogue courant.
5. Une commande contient une ou plusieurs lignes lorsqu'elle est confirmée.
6. Chaque ligne fait référence à une commande et à un produit existants.
7. La quantité d'une ligne doit être strictement positive.
8. Le prix unitaire enregistré sur la ligne correspond au prix appliqué lors de la vente, pas forcément au prix catalogue actuel.
9. Une commande historique ne doit pas être effacée automatiquement simplement parce qu'un compte client est désactivé.
10. Les valeurs de test sont fictives et ne sont pas issues d'une clientèle réelle.

Ces règles orientent les choix de schéma. Si une règle n'est pas claire, revenez au besoin métier plutôt que d'inventer une interprétation au moment de coder.

### Étape 2 : créer les tables

L'exemple suivant utilise une syntaxe courante que vous devez tester avec le moteur choisi. Les types d'identifiant automatique et certaines contraintes nécessitent une adaptation selon SQLite, PostgreSQL ou MySQL. Le cours privilégie des identifiants fournis explicitement dans les données de laboratoire afin de ne pas masquer les différences entre les moteurs.

~~~sql
CREATE TABLE clients (
    client_id INTEGER PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE produits (
    produit_id INTEGER PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    prix_catalogue DECIMAL(10,2) NOT NULL CHECK (prix_catalogue >= 0)
);

CREATE TABLE commandes (
    commande_id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    date_commande DATE NOT NULL,
    statut VARCHAR(20) NOT NULL
        CHECK (statut IN ('brouillon', 'confirmee', 'expediee', 'annulee')),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE lignes_commande (
    commande_id INTEGER NOT NULL,
    produit_id INTEGER NOT NULL,
    quantite INTEGER NOT NULL CHECK (quantite > 0),
    prix_unitaire DECIMAL(10,2) NOT NULL CHECK (prix_unitaire >= 0),
    PRIMARY KEY (commande_id, produit_id),
    FOREIGN KEY (commande_id) REFERENCES commandes(commande_id),
    FOREIGN KEY (produit_id) REFERENCES produits(produit_id)
);
~~~

Le schéma choisit une clé composée pour les lignes : une commande ne peut contenir qu'une ligne par produit. Si le métier exige plusieurs lignes identiques, ce choix doit être modifié. On pourrait ajouter un numéro de ligne et utiliser la combinaison commande_id, numero_ligne comme clé primaire, tout en décidant si une contrainte séparée doit interdire la répétition d'un produit dans la même commande. Le schéma n'est pas une simple recette : chaque choix correspond à une règle explicite.

Sur certains moteurs, une clé étrangère nécessite une configuration ou une vérification d'activation. Il faut s'assurer que les contraintes sont réellement actives dans l'environnement. SQLite, notamment, possède des particularités de configuration pour les clés étrangères. Dans un environnement de production, la vérification de la configuration fait partie de la mise en service ; il ne suffit pas que le script contienne une déclaration.

### Étape 3 : charger un petit jeu de données fictives

Le but est de créer deux clients, deux produits, deux commandes et quelques lignes. Utilisez des valeurs courtes pour faciliter l'inspection. Si vous réexécutez le script, des erreurs de clé primaire peuvent apparaître parce que les identifiants existent déjà. Dans ce cas, réinitialisez uniquement la base de laboratoire ou adaptez le script de manière explicite ; ne supprimez pas de données de production pour faire disparaître l'erreur.

~~~sql
INSERT INTO clients (client_id, nom, email)
VALUES
    (1, 'Amina Njoya', 'amina@example.test'),
    (2, 'Samuel Talla', 'samuel@example.test');

INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES
    (10, 'Clavier', 25.00),
    (20, 'Souris', 12.50);

INSERT INTO commandes (commande_id, client_id, date_commande, statut)
VALUES
    (100, 1, '2026-10-20', 'confirmee'),
    (101, 2, '2026-10-21', 'brouillon');

INSERT INTO lignes_commande
    (commande_id, produit_id, quantite, prix_unitaire)
VALUES
    (100, 10, 2, 25.00),
    (100, 20, 1, 12.50),
    (101, 20, 3, 12.50);
~~~

La date est une donnée de test. Le format accepté et sa conversion peuvent varier selon le moteur et le type. Utilisez le format attendu par la documentation du SGBD sélectionné.

### Étape 4 : observer les résultats et vérifier les règles

La manière la plus simple d'inspecter une table consiste à demander quelques lignes. Les commandes de lecture détaillées seront approfondies dans le cours SQL de base, mais une sélection simple aide à vérifier que la structure et les données correspondent à votre intention.

~~~sql
SELECT * FROM clients;
SELECT * FROM commandes;
SELECT * FROM lignes_commande;
~~~

Vous devez pouvoir répondre à ces questions à partir du modèle et des données :

- Le client 1 a-t-il deux commandes ou une seule ?
- La commande 100 contient-elle un ou plusieurs produits ?
- Le produit 20 apparaît-il dans plusieurs commandes ?
- Où est conservé le prix appliqué à une vente ?
- Quelle table relie la commande au produit ?
- Quel identifiant est unique pour une ligne de commande selon le modèle actuel ?

Ne déduisez pas les réponses d'une capture d'écran seule. Vérifiez les valeurs réellement retournées par la base et comparez-les aux règles définies avant la création du schéma.

### Étape 5 : effectuer des tests négatifs contrôlés

Un test négatif vérifie que le système refuse une opération invalide. Dans un environnement isolé, essayez séparément ces opérations :

~~~sql
-- Doit être rejeté : une quantité nulle.
INSERT INTO lignes_commande
    (commande_id, produit_id, quantite, prix_unitaire)
VALUES (100, 10, 0, 25.00);

-- Doit être rejeté : la commande 9999 n'existe pas.
INSERT INTO lignes_commande
    (commande_id, produit_id, quantite, prix_unitaire)
VALUES (9999, 20, 1, 12.50);

-- Doit être rejeté : le client 9999 n'existe pas.
INSERT INTO commandes (commande_id, client_id, date_commande, statut)
VALUES (999, 9999, '2026-10-22', 'brouillon');

-- Doit être rejeté : valeur de statut non autorisée.
INSERT INTO commandes (commande_id, client_id, date_commande, statut)
VALUES (1000, 1, '2026-10-22', 'peut-etre');
~~~

Chaque test doit échouer pour une raison attendue. Si une opération invalide est acceptée, ne concluez pas immédiatement que le modèle est mauvais : vérifiez d'abord que le script a été exécuté contre la bonne base, que la contrainte a réellement été créée et que le moteur l'applique. Une contrainte présente dans un fichier de migration mais absente du schéma effectif ne protège rien.

Si plusieurs essais utilisent des identifiants qui viennent d'être créés, des erreurs supplémentaires peuvent masquer l'objectif du test. Réinitialisez la base de laboratoire entre les groupes de tests ou choisissez des identifiants qui ne se chevauchent pas. Consignez la commande, le résultat attendu, le résultat réel et la conclusion. Une pratique reproductible permet de distinguer une vraie validation d'une simple impression.

### Étape 6 : documenter les limites de la solution

Le modèle est suffisant pour démontrer les relations mais n'est pas encore une solution complète de commerce électronique. Il ne gère pas le stock, les paiements, les adresses de livraison, la TVA, les remboursements, les retours, les commandes multi-devises ou la possibilité de plusieurs lignes identiques. Il ne faut pas ajouter ces fonctionnalités au hasard : chacune demande une règle métier et des tests dédiés.

Le schéma ne dit pas non plus qui a le droit de lire les coordonnées d'un client. Les permissions, les journaux d'audit, la sauvegarde, la reprise après incident et la surveillance sont des sujets complémentaires. À mesure que le système grandit, le modèle logique sera relié aux besoins d'exploitation et de sécurité.

### Critères d'acceptation de l'atelier

L'atelier est réussi si les quatre tables sont créées sans erreur, si les enregistrements de test sont visibles, si les références relient les commandes aux bons clients et les lignes aux commandes et produits, et si les tests négatifs échouent pour les raisons attendues. Vous devez également expliquer pourquoi la clé composée de LIGNES_COMMANDE correspond au choix de ne conserver qu'une ligne par produit et par commande.

Documentez les différences observées entre les moteurs, notamment le type d'identifiant, l'activation des clés étrangères et le comportement des contraintes. Si une syntaxe doit être adaptée, notez la version et le changement. Le résultat attendu n'est pas de prétendre que tous les moteurs sont identiques, mais de comprendre quels principes restent communs et quels détails doivent être vérifiés.

## 16. Étude de cas : une commande devient incohérente après un changement de prix

Une boutique enregistre le prix actuel dans PRODUITS et le copie dans chaque ligne de commande au moment de la vente. Le responsable modifie le prix catalogue de la souris de 12,50 à 14,00. Lors d'une vérification ultérieure, une commande ancienne affiche toujours 12,50. Une personne signale un écart et propose de mettre toutes les lignes de commande à jour avec le nouveau prix.

Avant de modifier les données, posez trois questions : quelle valeur représente le prix courant ? quelle valeur représente le prix effectivement appliqué à une vente passée ? quelle source doit être utilisée pour recalculer une commande historique ? Si le prix de la ligne est une photographie du prix appliqué lors de la vente, le mettre à jour globalement détruirait une information historique correcte. La duplication est intentionnelle parce que le prix de vente est un fait distinct.

En revanche, si la ligne est censée pointer vers une offre tarifaire courante plutôt que conserver le prix au moment de la vente, le modèle doit représenter cette règle différemment. La base ne peut pas deviner la sémantique métier à partir du nom d'une colonne. Le propriétaire du processus doit préciser le contrat avant que l'on corrige les données.

La bonne méthode consiste à isoler quelques commandes connues, comparer la ligne de vente avec le prix catalogue actuel et retrouver la règle applicable à la date de vente. Ensuite, on documente le diagnostic, on met à jour seulement les enregistrements qui sont réellement erronés et on ajoute un test de non-régression. L'objectif n'est pas d'obtenir des nombres identiques partout, mais de préserver le sens de chaque donnée.

Une autre variante de l'incident concerne le stock. Deux commandes sont confirmées pour la dernière unité disponible parce que le contrôle de stock et la réservation ne sont pas coordonnés. Une vérification isolée de la valeur courante n'est pas suffisante. Le traitement doit être conçu pour que la lecture, la décision et la réservation respectent les garanties de concurrence nécessaires. Les transactions sont une partie de la solution, mais la méthode exacte dépend du moteur, des requêtes et du modèle du stock.

## 17. Méthode de diagnostic quand une donnée paraît fausse

Lorsqu'un résultat semble incohérent, évitez de commencer par exécuter une correction destructive. Décrivez d'abord le symptôme avec une valeur concrète et une règle attendue. « Le rapport est faux » est trop vague ; « la commande 100 affiche un prix actuel de catalogue au lieu du prix enregistré lors de la vente » est testable.

Procédez ensuite de manière structurée :

1. **Confirmer la cible.** Vérifier le nom de la base, l'environnement, le compte et la version du schéma. Les erreurs d'environnement peuvent faire croire que les données ont disparu.
2. **Reproduire le problème.** Choisir un identifiant ou un petit jeu d'exemples qui expose le comportement sans mettre en danger les utilisateurs.
3. **Distinguer les couches.** Vérifier si la valeur est incorrecte dans la base, transformée par une requête, mise en cache, ou simplement mal affichée.
4. **Lire les règles.** Examiner les contraintes, les références et les hypothèses du modèle. Une requête correcte ne peut pas réparer une sémantique ambiguë.
5. **Tester les frontières.** Essayer le cas normal, un cas absent, un doublon, une valeur limite et, si pertinent, deux opérations concurrentes.
6. **Préserver les preuves.** Conserver les requêtes, les résultats, l'heure, la version et le contexte autorisé sans exposer de secrets ni de données personnelles inutiles.
7. **Corriger avec contrôle.** Proposer une modification limitée, la tester sur une copie et définir le moyen de retour arrière.
8. **Vérifier après correction.** Rejouer le test initial, les tests de non-régression et les contrôles d'intégrité concernés.

Une méthode de diagnostic n'est pas une liste cérémonielle. Chaque étape réduit une catégorie d'incertitude. Confirmer la cible évite de modifier la mauvaise base ; reproduire le cas permet à une autre personne de vérifier la conclusion ; distinguer les couches empêche de traiter un problème d'affichage par une mise à jour SQL ; contrôler les résultats après correction démontre que le changement a produit l'effet souhaité.

## 18. Exercices d'application avec corrigés

### Exercice 1 — Tableur ou base relationnelle ?

Une petite association conserve dans un seul tableur le nom des membres, les événements auxquels ils participent et les paiements effectués. Le nom complet est recopié pour chaque événement. Une personne change de nom et plusieurs lignes ne sont pas mises à jour. Quel problème observez-vous et quelle amélioration proposeriez-vous ?

**Corrigé.** Le même fait — l'identité d'un membre — est dupliqué dans plusieurs lignes, ce qui crée une anomalie de mise à jour. Il est préférable de séparer une table MEMBRES d'une table EVENEMENTS et d'une table de participation ou d'inscription reliant un membre à un événement. Les paiements méritent une structure propre si plusieurs paiements sont possibles pour une participation. Chaque entité a un identifiant stable, et les références sont protégées par des clés étrangères. Cela ne signifie pas qu'une base relationnelle est obligatoire pour tout petit fichier ; le besoin de cohérence partagée, le volume, les droits d'accès et les opérations concurrentes motivent le choix.

### Exercice 2 — Choisir une clé primaire

Vous devez identifier un produit. Les choix sont son nom, son prix actuel, son code produit interne ou un identifiant numérique généré. Le nom et le prix peuvent changer et plusieurs produits peuvent avoir le même nom. Quelle conception est raisonnable ?

**Corrigé.** Un identifiant stable peut être la clé primaire, tandis que le code produit interne peut être UNIQUE si le métier garantit son unicité et sa stabilité. Le nom et le prix ne sont pas de bons identifiants : ils changent et ne sont pas nécessairement uniques. Une clé technique est pratique, mais elle ne dispense pas d'imposer l'unicité d'un code métier lorsqu'elle est requise.

### Exercice 3 — Trouver la bonne relation

Chaque commande peut contenir plusieurs produits. Le même produit peut être acheté par des milliers de clients. Pourquoi ne pas ajouter les colonnes produit_1, produit_2, produit_3 dans COMMANDES ?

**Corrigé.** Le nombre de colonnes imposerait une limite artificielle et rendrait difficile l'ajout de nouveaux produits, la validation des quantités et l'analyse des ventes. Il faut créer LIGNES_COMMANDE qui relie une commande à un produit et contient quantité et prix appliqué. Cette table représente la relation plusieurs-à-plusieurs entre COMMANDES et PRODUITS. Une clé composée ou un numéro de ligne permet d'identifier chaque ligne selon les règles du métier.

### Exercice 4 — Clé étrangère

Une commande contient client_id = 501, mais aucune ligne du tableau CLIENTS ne possède client_id = 501. Que garantit une clé étrangère et que ne garantit-elle pas ?

**Corrigé.** Une clé étrangère active interdit normalement de créer ou conserver une référence qui ne correspond pas à un enregistrement parent valide, selon les règles du moteur. Elle garantit la cohérence de la référence, pas que le client a l'autorisation commerciale de commander, qu'il a payé ou qu'il est encore actif. Ces règles supplémentaires nécessitent des validations adaptées.

### Exercice 5 — NULL ou zéro ?

Une table de prêts possède la colonne date_retour. Un livre est encore emprunté. Faut-il enregistrer la date du jour, la date zéro, une chaîne vide ou NULL ?

**Corrigé.** NULL est souvent approprié si la règle indique qu'aucune date de retour n'a encore été enregistrée. La date du jour inventerait un retour, la date zéro ne représente pas un fait valide et une chaîne vide confond la donnée avec du texte. Le modèle doit préciser le sens de NULL et éventuellement relier cette absence à l'état du prêt.

### Exercice 6 — Contrainte adaptée

Une ligne de commande doit avoir une quantité strictement positive. Où placer la règle ? Suffit-il de désactiver le bouton d'envoi si la quantité est zéro ?

**Corrigé.** La vérification côté interface améliore l'expérience, mais elle ne protège pas les autres applications, scripts ou imports. Une contrainte CHECK (quantite > 0), avec NOT NULL, exprime la règle dans le schéma. Il faut adapter la syntaxe au moteur choisi et tester que les contraintes sont effectivement actives. Si une quantité zéro possède un sens métier exceptionnel, cette exception doit être modélisée explicitement.

### Exercice 7 — Comprendre une transaction

Une opération crée l'entête d'une commande puis ajoute deux lignes. La deuxième insertion échoue. Pourquoi une transaction est-elle utile ?

**Corrigé.** Sans transaction gérée correctement, l'entête et la première ligne pourraient rester enregistrés alors que la commande est incomplète. Une transaction permet de valider l'ensemble si toutes les étapes réussissent ou d'annuler les modifications concernées en cas d'échec, dans les limites du mécanisme transactionnel. Les effets externes comme un courriel ou un paiement hors base demandent une stratégie complémentaire.

### Exercice 8 — Préserver l'historique

Le prix courant d'un produit passe de 25 à 28. Un responsable veut mettre à jour tous les prix des anciennes lignes de commande pour qu'ils correspondent au catalogue. Quelle question faut-il poser avant d'agir ?

**Corrigé.** Il faut déterminer si la ligne conserve le prix effectivement appliqué à la transaction ou si elle représente une référence dynamique au prix courant. Pour une vente historique, le prix appliqué est généralement un fait daté qui ne doit pas changer automatiquement. Une mise à jour générale peut détruire la trace commerciale. Il faut confirmer la règle, isoler les cas réellement incorrects et tester la correction avant de modifier les données.

### Exercice 9 — Suppression d'un parent

Vous voulez supprimer un client qui possède encore des commandes. Pourquoi ne pas déclarer systématiquement ON DELETE CASCADE sur la clé étrangère ?

**Corrigé.** Une suppression en cascade pourrait effacer les commandes et leurs lignes associées, ce qui détruirait des informations historiques potentiellement nécessaires. La politique devrait tenir compte de la conservation, de l'audit, de la facturation, des règles de confidentialité et du cycle de vie du compte. Selon le besoin, le système peut bloquer la suppression, désactiver le client ou appliquer une procédure d'anonymisation contrôlée.

### Exercice 10 — Diagnostiquer une contrainte qui semble ignorée

Un script SQL accepte une quantité zéro alors que le schéma devait la refuser. Donnez une démarche de diagnostic.

**Corrigé.** Vérifier d'abord que le script se connecte à la bonne base et que la table inspectée est celle utilisée par l'application. Examiner le schéma effectif plutôt que le fichier théorique. Confirmer que la contrainte a bien été créée et qu'elle est appliquée par la configuration du moteur. Reproduire le test dans un environnement isolé, puis consulter la documentation de la version installée. Enfin, corriger la cause, vérifier les données déjà enregistrées et relancer le test négatif. Ne pas masquer le problème en supprimant simplement le test.

## 19. Défi final corrigé : concevoir une base d'inventaire de formation

### Mission

Vous devez modéliser un petit système qui suit des apprenants, des modules de formation et les inscriptions. Un apprenant peut suivre plusieurs modules. Un module peut être suivi par plusieurs apprenants. Une inscription possède une date, un statut et éventuellement une date d'achèvement. Deux inscriptions identiques pour le même apprenant et le même module ne doivent pas être créées accidentellement. Vous devez concevoir les principales tables, choisir les clés, protéger les références et expliquer les limites de la solution.

### Étape A — Extraire les entités et les règles

Les entités sont APPRENANTS et MODULES. INSCRIPTIONS représente la relation entre elles et porte ses propres attributs : date_inscription, statut et date_achevement. La relation apprenant-module est plusieurs-à-plusieurs ; INSCRIPTIONS la transforme en deux relations un-à-plusieurs. L'identifiant d'une inscription peut être une clé technique, tandis qu'une contrainte UNIQUE sur (apprenant_id, module_id) empêche les doublons si une seule inscription est autorisée par apprenant et module.

Avant de figer cette contrainte, vérifiez si le métier autorise une réinscription après abandon, une seconde tentative ou plusieurs sessions du même module. Si oui, la clé métier doit inclure un identifiant de session ou un numéro de tentative. Le modèle ci-dessous suppose volontairement une seule inscription par apprenant et module ; toute autre règle impose une modification explicite.

### Étape B — Schéma proposé

~~~mermaid
erDiagram
    APPRENANTS ||--o{ INSCRIPTIONS : "s'inscrit"
    MODULES ||--o{ INSCRIPTIONS : "est suivi via"
    APPRENANTS {
        int apprenant_id PK
        string nom
        string email UK
    }
    MODULES {
        int module_id PK
        string titre
        string niveau
    }
    INSCRIPTIONS {
        int inscription_id PK
        int apprenant_id FK
        int module_id FK
        date date_inscription
        string statut
        date date_achevement
    }
~~~

### Étape C — Exemple de définition

~~~sql
CREATE TABLE apprenants (
    apprenant_id INTEGER PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE modules (
    module_id INTEGER PRIMARY KEY,
    titre VARCHAR(160) NOT NULL,
    niveau VARCHAR(20) NOT NULL
        CHECK (niveau IN ('debutant', 'intermediaire', 'expert'))
);

CREATE TABLE inscriptions (
    inscription_id INTEGER PRIMARY KEY,
    apprenant_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    date_inscription DATE NOT NULL,
    statut VARCHAR(20) NOT NULL
        CHECK (statut IN ('inscrit', 'en_cours', 'termine', 'abandonne')),
    date_achevement DATE,
    UNIQUE (apprenant_id, module_id),
    FOREIGN KEY (apprenant_id) REFERENCES apprenants(apprenant_id),
    FOREIGN KEY (module_id) REFERENCES modules(module_id),
    CHECK (date_achevement IS NULL OR date_achevement >= date_inscription)
);
~~~

Ce schéma constitue un point de départ. La contrainte vérifie que la date d'achèvement n'est pas antérieure à la date d'inscription, mais elle ne garantit pas que statut = termine lorsque date_achevement est renseignée. Il faudrait décider si cette règle est nécessaire et comment traiter une réouverture ou une correction d'inscription. Une règle entre plusieurs colonnes peut être ajoutée si elle reflète réellement le domaine et si le moteur la supporte comme prévu.

Le modèle ne conserve pas encore l'historique des changements de statut. Si l'organisation doit prouver qu'une inscription est passée de inscrit à en_cours puis à termine, une table d'événements ou un journal d'audit peut être nécessaire. Le statut courant et la chronologie des événements ne sont pas la même information.

### Étape D — Tests d'acceptation

Le schéma est accepté si un apprenant et un module peuvent être créés, si une inscription valide peut être ajoutée, si une inscription vers un apprenant inexistant est rejetée et si un doublon apprenant-module est bloqué. Une valeur de statut inconnue doit échouer. La date d'achèvement antérieure à la date d'inscription doit être rejetée. Testez également une inscription sans date d'achèvement pour confirmer que la valeur facultative se comporte comme prévu.

Un test d'acceptation doit être formulé avant le test réel : « lorsque j'insère une inscription dont apprenant_id ne correspond à aucune ligne, le moteur refuse l'opération ». Le résultat observé doit être archivé avec la version du moteur, la commande testée et le message d'erreur sans secret. Si le test échoue, le travail n'est pas terminé : il faut identifier pourquoi l'invariant n'est pas appliqué.

### Étape E — Expliquer les décisions

Vous devez pouvoir justifier chaque table, chacune des clés, la contrainte UNIQUE, les valeurs de statut, le choix de permettre une date d'achèvement absente et la relation entre les inscriptions et leurs parents. Vous devez aussi exposer les hypothèses non couvertes, comme les réinscriptions, les sessions multiples, le journal d'audit, les permissions et la sauvegarde.

Le défi est réussi lorsque vous ne vous contentez pas d'obtenir un script qui s'exécute. Vous savez relier une règle métier à une structure, prévoir un cas invalide, montrer que la base le refuse et documenter ce qui reste hors périmètre. La compétence fondamentale d'une personne qui travaille avec des bases de données est cette capacité à passer du besoin aux règles vérifiables, et non la simple mémorisation de mots-clés.

## 20. Parcours pratique du débutant : transformer les concepts en réflexes

Consacrez plusieurs courtes séances plutôt qu'une seule lecture rapide. Durant la première séance, relisez le scénario de la boutique et dessinez les tables avec leurs identifiants. Durant la deuxième, expliquez chaque relation à voix haute et inventez un exemple valide et un exemple invalide. Durant la troisième, exécutez le script de création dans un environnement isolé puis inspectez le schéma effectif. Durant la quatrième, exécutez les tests négatifs un par un et décrivez la raison de chaque rejet. Durant la cinquième, modifiez une hypothèse du métier — autoriser plusieurs lignes du même produit, par exemple — et identifiez les parties du modèle qui doivent évoluer.

Tenez un carnet technique très simple. Pour chaque essai, consignez l'objectif, la règle testée, la commande, le résultat attendu, le résultat observé, le moteur et sa version. Le carnet ne doit contenir ni identifiants personnels réels, ni mot de passe, ni secret. Cette pratique aide à distinguer ce que vous avez supposé de ce que vous avez effectivement prouvé.

Quand une erreur survient, ne cherchez pas uniquement la ligne à copier depuis Internet. Reformulez l'erreur : s'agit-il d'une clé dupliquée, d'une référence absente, d'une valeur interdite, d'un type incompatible, d'une syntaxe différente ou d'un problème de connexion ? Ensuite, construisez un test minimal qui isole cette cause. Une erreur comprise devient une compétence réutilisable.

Pour réviser, choisissez une table de votre choix et répondez à six questions : quel fait représente-t-elle ? quelle ligne constitue un enregistrement ? quelles colonnes décrivent le fait ? comment est-il identifié ? quelles valeurs sont obligatoires ? quelles autres tables peuvent le référencer ? Si vous ne pouvez pas répondre sans ambiguïté, revenez au modèle plutôt que de commencer l'écriture de requêtes.

## 21. Checklist de mise en œuvre

Avant de considérer une première conception comme prête pour une suite de travail, vérifiez les points suivants :

- Chaque table représente un concept ou un ensemble de faits clairement défini.
- Les colonnes ont un sens précis, un type approprié et une unité connue si nécessaire.
- Chaque table possède une stratégie d'identification et une clé primaire adaptée.
- Les clés étrangères représentent les relations prévues et sont effectivement appliquées par le moteur.
- Les contraintes NOT NULL, UNIQUE et CHECK traduisent des règles métier confirmées.
- Les valeurs absentes ont un sens documenté ; NULL n'est pas utilisé comme substitut improvisé à zéro.
- Les cardinalités un-à-un, un-à-plusieurs et plusieurs-à-plusieurs sont comprises et justifiées.
- Les données historiques sont distinguées des valeurs courantes lorsque leur sens diffère.
- Le traitement des suppressions et modifications parentales est explicite.
- Les tests comprennent des cas valides et des cas invalides.
- Le script et les tests sont reproductibles dans un environnement isolé.
- Les comptes disposent des privilèges nécessaires, et pas automatiquement de privilèges administrateur.
- La configuration, la version du moteur et les différences de dialecte sont documentées.
- Les sauvegardes, restaurations, journaux et procédures de reprise seront traités avant la production.
- Les données collectées sont nécessaires et leur cycle de vie est défini.

Cette checklist ne remplace pas une revue technique, mais elle réduit les omissions évidentes. Dans un projet réel, faites relire le modèle par les personnes responsables du métier, du développement et de l'exploitation. Une base doit fonctionner aujourd'hui, mais elle doit aussi rester compréhensible et maintenable lors des évolutions futures.

## 22. Synthèse : ce qu'il faut retenir

Une base relationnelle représente les faits à l'aide de tables, de lignes et de colonnes. Le SGBD applique les règles déclarées et gère les accès, transactions et mécanismes de stockage. L'application offre une expérience à l'utilisateur mais ne devrait pas être la seule responsable de l'intégrité des données.

Les clés donnent une identité aux enregistrements. La clé primaire doit identifier une ligne sans ambiguïté ; la clé étrangère vérifie une référence entre tables. Les contraintes permettent d'interdire certaines valeurs ou certains états incohérents. Les cardinalités décrivent les relations et aident à choisir les tables et les références. Les relations plusieurs-à-plusieurs sont habituellement représentées au moyen d'une table d'association qui peut porter les propriétés du lien.

Il faut distinguer la valeur courante d'un fait de sa valeur historique, comme le prix du catalogue de celui d'une vente passée. NULL ne signifie pas zéro. Une transaction protège un ensemble cohérent d'opérations dans les limites du mécanisme transactionnel. Une bonne conception n'évite pas tous les incidents : elle rend les règles explicites, détecte certains problèmes tôt et facilite le diagnostic.

Le modèle conceptuel clarifie le besoin ; le modèle logique structure les tables et les relations ; le modèle physique tient compte du SGBD et de l'exploitation. Ces vues se complètent. La qualité exige également de la sécurité, une gestion de la concurrence, des sauvegardes testées, un contrôle des accès et une stratégie d'évolution.

Le meilleur test de compréhension consiste à expliquer pourquoi le modèle est ainsi conçu, puis à montrer qu'il accepte un cas valide et refuse un cas invalide. Si vous savez faire cela, vous disposez des fondations nécessaires pour apprendre les premières requêtes SQL sans les réduire à une suite de commandes à mémoriser.

## Références techniques

Les références ci-dessous complètent le cours et permettent de vérifier les différences propres aux moteurs. Consultez la documentation correspondant à la version réellement installée avant de généraliser une syntaxe ou une garantie.

- PostgreSQL 18, tutoriel officiel : https://www.postgresql.org/docs/18/tutorial.html
- PostgreSQL 18, contraintes de données : https://www.postgresql.org/docs/18/ddl-constraints.html
- MySQL 8.4, présentation d'InnoDB et de ses fonctions : https://dev.mysql.com/doc/refman/8.4/en/innodb-introduction.html
- MySQL 8.4, contraintes de clés étrangères : https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html
- MySQL 8.4, modèle de transactions InnoDB : https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-model.html
- SQLite, création des tables et contraintes : https://www.sqlite.org/lang_createtable.html

La documentation constructeur décrit la syntaxe et les garanties de son moteur ; les règles métier restent à définir dans le contexte de l'application. Une commande acceptée par un moteur ne doit pas être présumée portable à tous les autres.
