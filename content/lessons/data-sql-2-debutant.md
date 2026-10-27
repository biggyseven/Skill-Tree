# Jointures et agrégations SQL — Débutant

> **Mise en contexte.** Une boutique possède une table de clients, une table de commandes et une table de produits. Une personne demande « quelles commandes a passées chaque client ? », puis « combien chaque client a-t-il dépensé ? », puis « quels clients n'ont encore jamais commandé ? ». Une seule table ne contient pas forcément toutes les informations nécessaires. Il faut relier les tables, puis regrouper les lignes pour calculer des résultats. Ces opérations paraissent simples jusqu'au moment où un rapport compte deux fois une commande, exclut silencieusement les clients sans activité ou confond le nombre de commandes avec le nombre de lignes de commande. Ce cours apprend à obtenir des résultats justes, à comprendre la granularité des lignes et à vérifier ce que les calculs signifient réellement.

## 1. Objectifs pédagogiques

Les cours précédents ont présenté les tables, les clés, les relations, les requêtes de lecture, les filtres, l'ordre et les insertions. Nous allons maintenant exploiter les relations afin de répondre à des questions qui portent sur plusieurs tables ou sur plusieurs enregistrements à la fois.

Une jointure permet de combiner des lignes provenant de différentes sources selon une condition de correspondance. Une agrégation transforme plusieurs lignes en une valeur calculée, ou en une valeur par groupe. Ces opérations sont fondamentales pour produire des rapports, des tableaux de bord, des exports et des indicateurs métier. Elles exigent surtout de comprendre ce que représente une ligne à chaque étape de la requête.

À la fin de ce cours, vous devez être capable de distinguer INNER JOIN et LEFT JOIN, relier deux tables au moyen de clés compatibles, utiliser des alias pour rendre une requête lisible, reconnaître une relation plusieurs-à-plusieurs, compter les enregistrements correctement, calculer SUM, AVG, MIN et MAX, construire une clause GROUP BY, distinguer WHERE de HAVING, comprendre le traitement des NULL par les agrégats, détecter les erreurs dues au double comptage et vérifier un rapport à l'aide d'un petit jeu de données de référence.

La compétence visée ne consiste pas seulement à savoir taper JOIN ou GROUP BY. Vous devez pouvoir expliquer pourquoi une ligne apparaît dans le résultat, pourquoi une autre n'y apparaît pas, à quel niveau le résultat est détaillé et quelle unité est comptée ou additionnée. Si une requête annonce 500 commandes alors que l'application n'en contient que 300, le bon réflexe n'est pas d'ajouter DISTINCT au hasard : il faut analyser la relation, la granularité et les conditions de regroupement.

Les objectifs opérationnels sont les suivants :

- exprimer une relation entre deux tables avec une condition de jointure ;
- choisir INNER JOIN ou LEFT JOIN selon la question métier ;
- distinguer le rôle de ON de celui de WHERE, en particulier avec les jointures externes ;
- relier plusieurs tables sans produire une multiplication non intentionnelle des lignes ;
- comprendre ce qui change lorsqu'une relation plusieurs-à-plusieurs est traversée ;
- choisir COUNT(*), COUNT(colonne) et COUNT(DISTINCT expression) selon l'objet compté ;
- calculer des sommes, moyennes, minimums et maximums ;
- grouper les données au niveau métier voulu ;
- filtrer les lignes avant agrégation et les groupes après agrégation ;
- vérifier les résultats sur un exemple calculable à la main ;
- éviter les rapports trompeurs causés par NULL, les doublons, les montants répétés ou une mauvaise granularité.

## 2. Prérequis et environnement

Le prérequis du parcours est **data-modelisation-debutant — Modélisation et diagrammes (MCD/MLD)**. Vous devez comprendre les clés primaires et étrangères, les cardinalités, les tables associatives et les champs pouvant être absents. Si vous ne savez pas pourquoi une ligne de commande référence à la fois une commande et un produit, relisez la leçon de modélisation avant de poursuivre : cette relation sera au centre des exemples.

Les exemples utilisent une boutique fictive avec les tables suivantes :

- \`clients\` : identité d'un client ;
- \`commandes\` : une ligne par commande ;
- \`produits\` : catalogue de produits ;
- \`lignes_commande\` : une ligne par produit et commande, avec quantité et prix appliqué ;
- \`paiements\` : exemple complémentaire pour distinguer commande et paiement lorsque nécessaire.

Ces noms sont illustratifs. Le schéma réel d'un projet peut utiliser des conventions différentes. Vérifiez toujours les noms de tables, les colonnes, les types et les contraintes de la base sur laquelle vous travaillez.

~~~mermaid
erDiagram
    CLIENTS ||--o{ COMMANDES : "passe"
    COMMANDES ||--|{ LIGNES_COMMANDE : "contient"
    PRODUITS ||--o{ LIGNES_COMMANDE : "apparait dans"
    COMMANDES ||--o{ PAIEMENTS : "peut recevoir"
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
    LIGNES_COMMANDE {
        int commande_id PK, FK
        int produit_id PK, FK
        int quantite
        decimal prix_unitaire
    }
    PRODUITS {
        int produit_id PK
        string nom
        decimal prix_catalogue
    }
    PAIEMENTS {
        int paiement_id PK
        int commande_id FK
        decimal montant
        string statut
    }
~~~

Le diagramme montre les liens logiques. Il ne garantit pas à lui seul les comportements d'une requête : les jointures dépendent des colonnes utilisées dans ON et des filtres appliqués ensuite. Pour apprendre efficacement, nous allons d'abord relier deux tables, puis introduire les agrégats, et enfin combiner les deux en restant attentifs aux duplications.

Utilisez une base de laboratoire avec des données synthétiques. Les exemples de rapports financiers sont pédagogiques et ne définissent ni une règle comptable, ni une politique de remboursement, ni une méthode de reconnaissance du chiffre d'affaires. Dans une application réelle, ces règles doivent être confirmées avec le métier.

## 3. Comprendre la granularité avant d'écrire JOIN

La granularité répond à une question essentielle : **que représente une ligne dans cette table ou dans ce résultat ?** Dans \`clients\`, une ligne représente un client. Dans \`commandes\`, une ligne représente une commande. Dans \`lignes_commande\`, une ligne représente un produit inclus dans une commande, avec sa quantité et son prix appliqué. Ces tables ne possèdent donc pas la même granularité.

Exemple :

| client_id | nom |
|---:|---|
| 1 | Amina |
| 2 | Samuel |
| 3 | Nadia |

Table \`commandes\` :

| commande_id | client_id | date_commande |
|---:|---:|---|
| 100 | 1 | 2026-10-20 |
| 101 | 1 | 2026-10-21 |
| 102 | 2 | 2026-10-22 |

Amina possède deux commandes, Samuel une, et Nadia aucune. Si l'on associe clients et commandes, le résultat comporte trois lignes, pas trois clients distincts : Amina y apparaît deux fois. Cette répétition n'est pas une erreur de jointure ; elle reflète la relation un-à-plusieurs. Elle devient un problème seulement si le rapport voulait compter les clients et utilise le nombre de lignes du résultat sans tenir compte des répétitions.

~~~mermaid
flowchart LR
    A["CLIENT Amina"] --> C100["Commande 100"]
    A --> C101["Commande 101"]
    S["CLIENT Samuel"] --> C102["Commande 102"]
    N["CLIENT Nadia"] -. "aucune commande" .-> N
~~~

Le principe à retenir : une relation un-à-plusieurs produit généralement plusieurs lignes de résultat pour l'élément du côté « un ». Lorsqu'une ligne parent est reliée à trois lignes enfants, elle apparaît trois fois dans une jointure qui renvoie les détails. On ne doit pas confondre la répétition de la valeur parent avec un doublon erroné dans la table source.

Avant de joindre ou d'agréger, écrivez une phrase : « une ligne du résultat représente… ». Par exemple :
- une ligne représente un couple client-commande ;
- une ligne représente un produit d'une commande ;
- une ligne représente un client avec le nombre de commandes ;
- une ligne représente un statut de commande ;
- une ligne représente une commande avec son total calculé.

Si vous ne pouvez pas compléter cette phrase, la requête risque de combiner des niveaux différents. La granularité est la boussole qui permet de choisir la bonne clé de jointure et le bon GROUP BY.

## 4. INNER JOIN : ne conserver que les correspondances

La jointure interne, écrite \`INNER JOIN\` ou simplement \`JOIN\`, combine les lignes pour lesquelles la condition ON correspond. Dans une relation client-commandes, seuls les clients ayant au moins une commande apparaissent dans le résultat. Les clients sans commande sont exclus.

~~~sql
SELECT
    clients.client_id,
    clients.nom,
    commandes.commande_id,
    commandes.date_commande
FROM clients
INNER JOIN commandes
    ON commandes.client_id = clients.client_id;
~~~

La condition ON indique comment relier les lignes : commandes.client_id doit correspondre à clients.client_id. Il s'agit normalement d'une clé étrangère vers la clé primaire, selon le schéma présenté. La jointure n'ajoute pas une relation permanente à la base ; elle construit un résultat à partir des lignes existantes.

Le résultat de l'exemple est :

| client_id | nom | commande_id | date_commande |
|---:|---|---:|---|
| 1 | Amina | 100 | 2026-10-20 |
| 1 | Amina | 101 | 2026-10-21 |
| 2 | Samuel | 102 | 2026-10-22 |

Nadia n'apparaît pas parce qu'elle n'a aucune commande correspondante. Amina apparaît deux fois parce qu'elle a deux commandes. Si l'objectif est de lister les commandes, c'est exactement ce que l'on veut. Si l'objectif est de compter les clients ayant commandé, il faudra adapter la requête ou utiliser un agrégat qui tient compte de l'identité client.

### 4.1 Pourquoi la condition ON est indispensable

Si l'on combine deux tables sans la condition appropriée, chaque ligne de la première peut être associée à chaque ligne de la seconde. Le résultat est appelé produit cartésien. Avec 100 clients et 1 000 commandes, ce type de combinaison peut produire jusqu'à 100 000 paires avant les autres filtres. Cela peut être voulu dans certains calculs, mais c'est rarement ce qu'on souhaite pour relier un client à ses commandes.

~~~sql
-- À éviter pour relier les commandes à leurs clients :
SELECT clients.nom, commandes.commande_id
FROM clients
CROSS JOIN commandes;
~~~

CROSS JOIN exprime explicitement un produit cartésien. Il n'est pas intrinsèquement mauvais, mais la plupart des rapports client-commandes doivent relier les tables via une clé compatible. Une requête comportant plusieurs tables doit indiquer clairement chaque relation attendue.

### 4.2 Utiliser des alias pour rendre la requête lisible

Lorsqu'une requête contient plusieurs tables, les noms complets peuvent devenir longs. Un alias donne un nom court à une table dans la requête :

~~~sql
SELECT
    c.client_id,
    c.nom,
    co.commande_id,
    co.date_commande
FROM clients AS c
INNER JOIN commandes AS co
    ON co.client_id = c.client_id;
~~~

Ici, c représente clients et co représente commandes. Les alias ne changent ni les données, ni les noms du schéma ; ils rendent simplement les références plus concises. Choisissez des alias compréhensibles, surtout pour une requête partagée avec une équipe. Les alias obscurs comme a, b, x, y deviennent pénibles lorsque la requête possède cinq tables.

Il est préférable de qualifier les colonnes lorsque plusieurs tables possèdent le même nom, comme client_id, id ou statut. Une référence non qualifiée peut être ambiguë et provoquer une erreur, ou devenir difficile à comprendre lors d'une évolution du schéma.

### 4.3 Relier trois tables

Une requête peut suivre plusieurs relations successives :

~~~sql
SELECT
    c.nom AS client,
    co.commande_id,
    p.nom AS produit,
    lc.quantite,
    lc.prix_unitaire
FROM clients AS c
INNER JOIN commandes AS co
    ON co.client_id = c.client_id
INNER JOIN lignes_commande AS lc
    ON lc.commande_id = co.commande_id
INNER JOIN produits AS p
    ON p.produit_id = lc.produit_id
ORDER BY co.commande_id, p.nom;
~~~

Cette requête retourne le détail des produits commandés, avec le nom du client et l'identifiant de la commande. La granularité est désormais une ligne par ligne de commande, et non une ligne par commande. Une commande contenant trois produits apparaîtra trois fois. C'est attendu pour un détail, mais il faut faire attention si l'on ajoute ensuite un total de commande, un paiement ou une autre relation plusieurs-à-plusieurs.

La jointure entre commandes et lignes_commande suit la clé étrangère commande_id. Celle entre lignes_commande et produits suit produit_id. Si l'une des relations est manquante ou incorrecte, le résultat peut omettre des lignes ou associer des données qui n'ont pas de sens.

## 5. LEFT JOIN : conserver les lignes de gauche même sans correspondance

La jointure externe gauche, \`LEFT JOIN\`, conserve toutes les lignes de la table située à gauche. Lorsqu'aucune ligne de droite ne correspond, les colonnes de droite valent NULL dans le résultat.

~~~sql
SELECT
    c.client_id,
    c.nom,
    co.commande_id
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
ORDER BY c.client_id, co.commande_id;
~~~

Le résultat comprend Amina avec ses deux commandes, Samuel avec la commande 102, et Nadia avec une valeur NULL pour commande_id. Nadia est conservée malgré l'absence de commande. C'est l'intérêt de LEFT JOIN.

~~~mermaid
flowchart TD
    A["Toutes les lignes de gauche : clients"] --> B{"Commande correspondante ?"}
    B -->|Oui| C["Associer les données client et commande"]
    B -->|Non| D["Conserver le client et compléter la partie commande par NULL"]
    C --> E["Résultat LEFT JOIN"]
    D --> E
~~~

Le choix entre INNER JOIN et LEFT JOIN doit découler de la question. « Liste toutes les commandes avec le client associé » peut utiliser INNER JOIN si toute commande possède obligatoirement un client valide. « Liste tous les clients, même ceux qui n'ont pas commandé » nécessite LEFT JOIN. Si vous utilisez INNER JOIN dans la seconde question, vous excluez les clients sans commande et le rapport est incomplet.

### 5.1 Trouver les clients sans commande

LEFT JOIN permet de chercher les lignes sans correspondance en filtrant sur une colonne de droite qui doit être non nulle lorsqu'une ligne correspond :

~~~sql
SELECT
    c.client_id,
    c.nom
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
WHERE co.commande_id IS NULL;
~~~

Résultat attendu : Nadia, dans le jeu de données précédent. Le filtre porte ici sur l'identifiant de commande. Si commande_id est la clé primaire, il ne peut pas être NULL pour une véritable ligne de commande ; NULL dans le résultat de LEFT JOIN indique donc l'absence de correspondance.

Ne filtrez pas automatiquement sur une colonne facultative de la table de droite. Si une commande correspondante existe mais que son commentaire est NULL, tester commentaire IS NULL pourrait la confondre avec une absence de commande. Choisissez une colonne de droite qui est obligatoirement renseignée lorsqu'une ligne existe, généralement sa clé primaire.

### 5.2 Le piège classique : WHERE sur la table de droite

Considérez cette requête :

~~~sql
SELECT c.client_id, c.nom, co.commande_id
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
WHERE co.statut = 'confirmee';
~~~

Même si la requête utilise LEFT JOIN, elle élimine les clients sans commande. Pour Nadia, co.statut vaut NULL dans le résultat ; la condition co.statut = 'confirmee' n'est pas vraie, donc Nadia est exclue. Pour obtenir tous les clients en conservant uniquement les commandes confirmées associées, il est souvent préférable de placer le filtre de statut dans ON :

~~~sql
SELECT c.client_id, c.nom, co.commande_id
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
   AND co.statut = 'confirmee';
~~~

La différence est essentielle : dans la première version, le filtre WHERE s'applique au résultat après la jointure et élimine les lignes où le statut est absent. Dans la seconde, la condition fait partie de la recherche d'une commande correspondante ; chaque client reste présent, même s'il n'a aucune commande confirmée.

Il ne faut pas appliquer cette règle mécaniquement à toutes les requêtes. La bonne place du filtre dépend de ce qu'on veut conserver. Demandez-vous : « est-ce que je veux exclure les lignes de gauche qui n'ont pas de correspondance répondant à ce critère, ou veux-je conserver toutes les lignes de gauche et seulement restreindre les correspondances de droite ? » Cette formulation clarifie souvent le choix entre WHERE et ON.

## 6. Relier les tables sur la bonne clé

Une jointure est logique lorsque les colonnes de comparaison représentent la même relation. La convention de nommage aide, mais la structure et le sens métier doivent être confirmés. Joindre clients.client_id à commandes.commande_id est généralement une erreur, même si les deux colonnes sont des entiers : elles identifient des objets différents.

La condition correcte d'une jointure doit préserver le sens des identifiants. Une clé étrangère dans la table enfant référence normalement la clé primaire ou une clé unique de la table parente. Lorsqu'une relation passe par une table associative, il faut suivre les références successivement plutôt que contourner le modèle.

Par exemple, produits et commandes ne sont pas directement reliés dans notre modèle ; la relation est matérialisée par lignes_commande. Pour obtenir les produits de chaque commande, la requête traverse commandes → lignes_commande → produits. Ne joignez pas commandes à produits avec une condition arbitraire sur le nom du produit ou le prix, car ces valeurs peuvent changer ou être répétées.

Les types de données doivent être compatibles. Des colonnes portant des identifiants sous forme texte d'un côté et entier de l'autre peuvent entraîner conversions, erreurs ou comportements spécifiques au moteur. Corrigez le modèle ou les données plutôt que d'introduire des conversions improvisées dans chaque requête.

Si les colonnes de clé ne sont pas uniques du côté attendu, une jointure peut produire davantage de lignes que prévu. Une clé primaire est unique ; mais une colonne appelée code ou référence peut contenir des doublons si aucune contrainte ne l'interdit. Avant de vous appuyer sur une relation supposée un-à-un, vérifiez l'unicité qui justifie cette hypothèse.

## 7. FULL JOIN, RIGHT JOIN et autres variantes

Le niveau débutant doit surtout maîtriser INNER JOIN et LEFT JOIN. D'autres variantes existent :

- **RIGHT JOIN** conserve toutes les lignes de la table de droite et complète la partie gauche par NULL lorsqu'il n'existe pas de correspondance. On peut souvent réécrire la requête en inversant les tables puis en utilisant LEFT JOIN, ce qui rend la lecture plus simple.
- **FULL OUTER JOIN** conserve les lignes des deux côtés, même lorsqu'elles n'ont pas de correspondance. Les colonnes de l'autre côté valent alors NULL.
- **CROSS JOIN** produit les combinaisons de chaque ligne de gauche avec chaque ligne de droite.
- **Self join** relie une table à elle-même, par exemple pour associer un employé à son responsable lorsque les deux sont enregistrés dans la même table.

La prise en charge et la syntaxe de FULL OUTER JOIN varient selon les moteurs. Vérifiez la documentation de la version utilisée. Le but du cours n'est pas de choisir la jointure la plus exotique, mais de sélectionner celle qui exprime exactement les lignes que vous souhaitez conserver.

### Exemple de self join

Une table employés peut posséder une colonne responsable_id qui référence l'identifiant d'un autre employé. Pour afficher le nom de chaque employé et le nom de son responsable, on peut joindre la table à elle-même avec deux alias. Une jointure externe est utile si certains employés n'ont pas de responsable déclaré, par exemple le directeur.

~~~sql
SELECT
    e.nom AS employe,
    r.nom AS responsable
FROM employes AS e
LEFT JOIN employes AS r
    ON r.employe_id = e.responsable_id
ORDER BY e.nom;
~~~

Les alias e et r distinguent deux rôles joués par la même table. Cette technique sera utile dans d'autres domaines : catégories parent-enfant, comptes liés, hiérarchies d'organisation ou références entre objets.

## 8. Agrégats : résumer plusieurs lignes

Une fonction d'agrégation calcule une valeur à partir d'un ensemble de lignes. Les plus courantes sont :

- \`COUNT\` : compter des lignes ou des valeurs non NULL ;
- \`SUM\` : additionner les valeurs d'une expression numérique ;
- \`AVG\` : calculer la moyenne arithmétique des valeurs non NULL ;
- \`MIN\` : trouver la plus petite valeur ;
- \`MAX\` : trouver la plus grande valeur.

~~~sql
SELECT
    COUNT(*) AS nombre_lignes,
    MIN(prix_catalogue) AS prix_minimum,
    MAX(prix_catalogue) AS prix_maximum,
    AVG(prix_catalogue) AS prix_moyen,
    SUM(prix_catalogue) AS somme_des_prix
FROM produits;
~~~

Sans GROUP BY, cette requête produit habituellement une ligne de résultats qui résume toutes les lignes candidates de produits. Les fonctions ne changent pas la table. Elles calculent des valeurs dérivées du jeu de données.

Les fonctions d'agrégation ne donnent du sens qu'en rapport avec le domaine. La moyenne du prix catalogue de chaque produit n'est pas la dépense moyenne d'un client. La somme des prix catalogue n'est pas le chiffre d'affaires, puisque les quantités vendues et les prix historiques de vente ne sont pas pris en compte. Le calcul peut être syntaxiquement valide et répondre à une question différente de celle souhaitée.

### 8.1 COUNT(*) : compter les lignes

\`COUNT(*)\` compte les lignes du jeu de résultats, y compris lorsqu'une ou plusieurs colonnes contiennent NULL. Il ne compte pas seulement les lignes où toutes les colonnes sont remplies.

~~~sql
SELECT COUNT(*) AS nombre_de_produits
FROM produits;
~~~

Cette requête retourne le nombre de lignes présentes dans produits, après les éventuelles conditions WHERE. Elle ne compte pas les catégories uniques ni le nombre de commandes ; il faut choisir la table correspondant à l'objet métier compté.

### 8.2 COUNT(colonne) : compter les valeurs connues

\`COUNT(colonne)\` compte les lignes où l'expression donnée n'est pas NULL. C'est différent de COUNT(*) si la colonne peut être absente :

~~~sql
SELECT
    COUNT(*) AS total_clients,
    COUNT(email) AS clients_avec_email
FROM clients;
~~~

Si email est défini NOT NULL, les deux valeurs seront normalement égales dans un état conforme. Si email accepte NULL, elles peuvent différer. COUNT(email) ne compte pas les chaînes vides : une chaîne vide est une valeur textuelle non NULL. C'est une distinction importante lorsqu'une application accepte une entrée vide au lieu d'une absence réelle.

### 8.3 COUNT(DISTINCT expression) : compter les valeurs uniques

Si un client peut passer plusieurs commandes, compter les lignes de la jointure client-commandes donne le nombre de commandes, pas le nombre de clients. Pour compter les clients distincts ayant passé une commande :

~~~sql
SELECT COUNT(DISTINCT client_id) AS clients_ayant_commande
FROM commandes;
~~~

COUNT(DISTINCT client_id) compte les valeurs uniques non NULL de client_id. Avec une clé étrangère obligatoire, chaque commande doit normalement référencer un client et cette valeur ne devrait pas être NULL. Dans un rapport général, la signification exacte de la colonne et de son caractère facultatif doit être vérifiée.

DISTINCT ne doit pas être utilisé comme un correctif universel. Il répond à la question « combien de valeurs distinctes ? ». Il ne répond pas à la question « pourquoi des lignes se sont-elles multipliées ? ». Si le détail d'une jointure doit produire une ligne par commande, mais produit plusieurs lignes par commande, investiguez la condition de jointure et les relations de données.

## 9. GROUP BY : produire un résultat par groupe

GROUP BY rassemble les lignes qui partagent la même valeur pour une ou plusieurs expressions, puis calcule des agrégats pour chaque groupe. Sans GROUP BY, un agrégat résume l'ensemble du jeu. Avec GROUP BY client_id, il calcule un résultat par client présent dans les lignes candidates.

~~~sql
SELECT
    client_id,
    COUNT(*) AS nombre_commandes
FROM commandes
GROUP BY client_id
ORDER BY client_id;
~~~

La granularité du résultat est une ligne par client_id ayant au moins une ligne dans commandes. Les clients sans commande n'apparaissent pas ici, car la requête part de commandes. Pour obtenir un résultat pour tous les clients, y compris ceux sans commande, il faudra partir de clients et utiliser LEFT JOIN, puis choisir soigneusement l'expression comptée.

### 9.1 Grouper plusieurs expressions

~~~sql
SELECT
    client_id,
    statut,
    COUNT(*) AS nombre
FROM commandes
GROUP BY client_id, statut
ORDER BY client_id, statut;
~~~

Cette requête produit une ligne par combinaison client-statut. Un même client peut apparaître plusieurs fois si ses commandes possèdent plusieurs statuts. Ce n'est pas une erreur : la granularité est le couple (client_id, statut). Si l'objectif était une ligne par client, le statut doit être traité autrement, par exemple avec une autre règle d'agrégation ou une logique métier spécifique.

Un bon test consiste à écrire : « une ligne du résultat représente un groupe défini par … ». Si vous dites « une ligne représente un client et son statut de commande », votre GROUP BY doit refléter ces deux dimensions ou calculer un seul statut selon une règle explicite.

### 9.2 Les colonnes dans SELECT doivent respecter le regroupement

Une requête comme celle-ci est problématique dans un modèle SQL standard :

~~~sql
SELECT client_id, statut, COUNT(*)
FROM commandes
GROUP BY client_id;
~~~

Quel statut faut-il afficher si le client possède une commande brouillon et une autre confirmée ? La requête ne définit pas ce choix. Certains moteurs et modes SQL refusent la requête ; des configurations plus permissives peuvent renvoyer une valeur qui ne représente pas une règle fiable.

Les colonnes sélectionnées doivent généralement être :
- incluses dans GROUP BY ;
- utilisées dans une fonction d'agrégation ;
- ou déterminées par une dépendance fonctionnelle reconnue par le moteur et conforme aux règles applicables.

Pour apprendre, gardez une règle simple : si une colonne doit apparaître telle quelle dans SELECT, mettez-la dans GROUP BY, sauf si vous savez expliquer la règle et le comportement du moteur. Ne choisissez pas arbitrairement MAX(statut) ou MIN(statut) pour faire disparaître une erreur : cela ajoute une logique qui peut ne pas avoir de sens métier.

### 9.3 Agréger après filtrage

WHERE sélectionne les lignes candidates avant le regroupement. Par exemple :

~~~sql
SELECT
    client_id,
    COUNT(*) AS commandes_confirmees
FROM commandes
WHERE statut = 'confirmee'
GROUP BY client_id;
~~~

Seules les commandes confirmées entrent dans les groupes. La fonction COUNT compte les lignes restantes par client. Ce n'est pas la même chose que compter toutes les commandes et ensuite éliminer des groupes selon un total.

L'ordre logique de traitement aide à comprendre la requête : FROM et JOIN construisent les lignes candidates, WHERE filtre ces lignes, GROUP BY crée les groupes, les fonctions d'agrégation calculent les valeurs, HAVING filtre les groupes, puis SELECT et ORDER BY définissent la sortie selon les règles du moteur. La syntaxe s'écrit dans un ordre qui n'est pas exactement cet ordre conceptuel ; apprendre la séquence logique réduit les confusions.

~~~mermaid
flowchart TD
    A["FROM et JOIN : construire les lignes"] --> B["WHERE : filtrer les lignes"]
    B --> C["GROUP BY : créer les groupes"]
    C --> D["Calcul des agrégats"]
    D --> E["HAVING : filtrer les groupes"]
    E --> F["SELECT : construire le résultat"]
    F --> G["ORDER BY : ordonner la sortie"]
~~~

## 10. HAVING : filtrer les groupes après agrégation

HAVING permet de garder les groupes qui satisfont une condition portant généralement sur un agrégat. Exemple : les clients qui ont passé au moins deux commandes.

~~~sql
SELECT
    client_id,
    COUNT(*) AS nombre_commandes
FROM commandes
GROUP BY client_id
HAVING COUNT(*) >= 2
ORDER BY nombre_commandes DESC, client_id ASC;
~~~

La différence avec WHERE est fondamentale. WHERE écarte les lignes avant la création des groupes. HAVING écarte les groupes après le calcul des agrégats. On ne peut pas remplacer systématiquement l'un par l'autre.

Exemple : « parmi les commandes confirmées, trouver les clients qui ont au moins trois commandes confirmées ». On filtre d'abord les commandes avec WHERE, puis on regroupe par client et l'on retient les groupes avec HAVING :

~~~sql
SELECT
    client_id,
    COUNT(*) AS commandes_confirmees
FROM commandes
WHERE statut = 'confirmee'
GROUP BY client_id
HAVING COUNT(*) >= 3;
~~~

Autre question : « trouver les clients qui ont au moins trois commandes quel que soit leur statut ». Ici, on retire le filtre statut du WHERE :

~~~sql
SELECT
    client_id,
    COUNT(*) AS nombre_commandes
FROM commandes
GROUP BY client_id
HAVING COUNT(*) >= 3;
~~~

Ces deux requêtes répondent à des règles métier différentes. Une requête correcte doit refléter le périmètre exact de l'indicateur, notamment les statuts inclus et les dates retenues.

### 10.1 Peut-on utiliser un alias dans HAVING ?

Certains moteurs autorisent l'utilisation d'un alias d'agrégat dans HAVING, d'autres possèdent des restrictions ou des différences de comportement. La forme la plus portable et la plus claire pour le débutant consiste à répéter l'expression :

~~~sql
SELECT client_id, COUNT(*) AS nombre_commandes
FROM commandes
GROUP BY client_id
HAVING COUNT(*) >= 2;
~~~

Si votre SGBD prend en charge une variante, vérifiez-la dans sa documentation. Ne supposez pas qu'une requête acceptée dans un moteur fonctionnera de la même manière dans un autre.

## 11. Les agrégats les plus courants en détail

### 11.1 COUNT

COUNT compte les lignes ou les valeurs non NULL selon la forme utilisée. Il est souvent employé pour mesurer le nombre de commandes, produits, clients actifs ou lignes de détail. Il faut choisir l'unité à compter.

- COUNT(*) compte les lignes dans le groupe.
- COUNT(colonne) compte les valeurs non NULL de l'expression.
- COUNT(DISTINCT colonne) compte les valeurs distinctes non NULL.

Un rapport « nombre de commandes par client » doit compter commande_id dans la granularité commande, pas les lignes de commande qui détaillent les produits. Lorsqu'on joint commandes à lignes_commande, une commande avec quatre produits apparaîtra quatre fois. COUNT(*) dans ce résultat comptera les lignes de produits, pas les commandes. COUNT(DISTINCT commande_id) peut compter les commandes distinctes, mais la solution la plus sûre reste d'examiner la granularité et d'écrire une requête qui correspond au besoin.

### 11.2 SUM

SUM additionne les valeurs numériques non NULL de l'expression. Un calcul de total de ligne peut être quantity * unit_price. Un total de commande correspond ensuite à la somme de ces valeurs par commande :

~~~sql
SELECT
    commande_id,
    SUM(quantite * prix_unitaire) AS total_lignes
FROM lignes_commande
GROUP BY commande_id
ORDER BY commande_id;
~~~

La requête calcule le total brut des lignes selon les prix stockés et les quantités. Elle ne prend pas en compte les remises au niveau de commande, les frais de livraison, les taxes, les remboursements ou une politique comptable particulière. Le nom total_lignes évite de prétendre que le calcul représente nécessairement le montant final facturé.

Quand un groupe ne contient aucune valeur non NULL, le comportement de SUM peut produire NULL plutôt que zéro. Une commande sans ligne n'apparaît pas dans cette requête, parce que la source est lignes_commande. Si le rapport doit afficher zéro pour les commandes sans ligne, il faut partir des commandes et effectuer un LEFT JOIN avant d'agréger, avec une gestion explicite du résultat NULL selon le besoin.

### 11.3 AVG

AVG calcule la moyenne des valeurs non NULL. Une moyenne peut être trompeuse si l'on ne précise pas son unité. La moyenne des prix de catalogue donne le prix moyen par ligne de produit. La moyenne des montants de commande donne un montant moyen par commande si chaque commande n'est représentée qu'une fois dans l'agrégat.

Évitez de calculer AVG sur des lignes multipliées par une jointure sans connaître l'effet de pondération. Une commande avec cinq lignes de produits apparaissant cinq fois ne doit pas peser cinq fois plus qu'une commande avec une seule ligne si vous souhaitez la moyenne par commande.

La moyenne arithmétique ne reflète pas nécessairement le comportement d'un utilisateur typique, ni un indicateur financier pondéré. Avant de publier une moyenne, définissez l'ensemble des valeurs incluses, le traitement des valeurs absentes et l'unité de chaque observation.

### 11.4 MIN et MAX

MIN et MAX renvoient respectivement la plus petite et la plus grande valeur non NULL selon les règles de comparaison applicables. Ils peuvent servir à trouver la date de première commande, la date de dernière commande ou les valeurs extrêmes d'un prix. Pour les textes, le résultat dépend des règles de tri et de collation ; il ne signifie pas « première valeur dans le temps » sauf si la colonne représente une date correctement.

~~~sql
SELECT
    MIN(date_commande) AS premiere_commande,
    MAX(date_commande) AS derniere_commande
FROM commandes;
~~~

Cette requête décrit les dates minimale et maximale parmi les commandes présentes. Elle ne garantit pas l'existence d'un historique complet : si certaines commandes ont été archivées dans une autre table ou si les données sont incomplètes, les résultats ne représentent que les lignes actuellement consultées.

### 11.5 Les agrégats et NULL

Les agrégats ignorent généralement les valeurs NULL des expressions qu'ils traitent, tandis que COUNT(*) compte les lignes. Par exemple, AVG(note) calcule la moyenne des notes renseignées et non la moyenne incluant artificiellement des zéros pour les notes absentes. Si NULL signifie « examen pas encore passé », remplacer la valeur par zéro modifierait la signification de l'indicateur.

Un rapport doit différencier « zéro vente » de « aucune donnée disponible ». La fonction COALESCE peut remplacer un NULL par une valeur explicitement choisie, mais il faut connaître la sémantique du champ avant de le faire. Zéro peut être un résultat réel, alors que NULL peut signifier que le total n'est pas défini ou qu'aucune ligne n'a contribué au calcul.

## 12. LEFT JOIN et agrégations : compter aussi les absences

Supposons que l'on veuille afficher **tous les clients et le nombre de commandes de chacun, y compris zéro**. La requête suivante part de clients et utilise LEFT JOIN :

~~~sql
SELECT
    c.client_id,
    c.nom,
    COUNT(co.commande_id) AS nombre_commandes
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
GROUP BY c.client_id, c.nom
ORDER BY c.client_id;
~~~

Pourquoi COUNT(co.commande_id) plutôt que COUNT(*) ? Pour un client sans commande, LEFT JOIN produit tout de même une ligne de résultat, avec les colonnes de commandes à NULL. COUNT(*) compterait cette ligne artificielle comme une ligne, et Nadia aurait alors le compte 1. COUNT(co.commande_id) ignore le NULL de la colonne de droite et donne zéro, à condition que commande_id soit non NULL pour chaque véritable commande.

C'est l'un des pièges les plus importants du cours. Une jointure externe conserve une ligne parent même sans enfant ; COUNT(*) compte toutes les lignes du jeu de jointure ; COUNT(colonne_enfant) ne compte que les valeurs non NULL. Le choix doit correspondre à ce que l'on compte.

~~~mermaid
flowchart TD
    A["CLIENT Nadia"] --> B["LEFT JOIN sans commande"]
    B --> C["Résultat provisoire : client_id = 3, commande_id = NULL"]
    C --> D["COUNT(*) = 1"]
    C --> E["COUNT(commande_id) = 0"]
    E --> F["Nombre réel de commandes : zéro"]
~~~

Le résultat est une ligne par client, car le GROUP BY contient l'identité et le nom du client. Si la clé primaire rend le nom fonctionnellement déterminé, certains moteurs SQL autorisent des variantes de GROUP BY, mais la forme qui cite les deux colonnes est plus claire et largement comprise. En cas d'évolution du modèle, vérifiez les règles du moteur et les dépendances fonctionnelles éventuelles.

### 12.1 Filtrer les enfants sans perdre les parents

On veut compter toutes les commandes confirmées par client, tout en conservant les clients qui n'en ont aucune. La bonne approche place le statut dans la condition de jointure :

~~~sql
SELECT
    c.client_id,
    c.nom,
    COUNT(co.commande_id) AS commandes_confirmees
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
   AND co.statut = 'confirmee'
GROUP BY c.client_id, c.nom
ORDER BY c.client_id;
~~~

Cette requête conserve chaque client, puis associe uniquement les commandes confirmées. Si Nadia n'en a aucune, elle reçoit un compte de zéro. Si l'on déplaçait co.statut = 'confirmee' dans WHERE, on éliminerait les lignes sans correspondance et on perdrait les clients à zéro.

La même idée s'applique aux factures payées, aux réservations actives, aux appareils remontant des alertes ou aux employés possédant des tickets ouverts. Si le rapport doit inclure tous les objets d'une population de référence, partez de cette population et utilisez LEFT JOIN avec des filtres placés au bon endroit.

## 13. Le danger du double comptage lors de plusieurs jointures

Une des erreurs de reporting les plus difficiles à détecter vient de la multiplication des lignes. Imaginez qu'une commande 100 possède trois lignes de produits et deux paiements. Si la requête joint les commandes aux lignes de commande et aux paiements dans une même relation plate, le résultat peut comporter trois fois deux, soit six lignes, pour cette commande : chaque ligne de produit est combinée avec chaque paiement.

Si vous additionnez le montant des lignes ou le montant des paiements sur ce résultat, vous pouvez compter chaque fait plusieurs fois. Les valeurs affichées dans les colonnes semblent plausibles, mais les agrégats deviennent faux.

~~~mermaid
flowchart TD
    C["Commande 100"] --> L1["Ligne produit A"]
    C --> L2["Ligne produit B"]
    C --> L3["Ligne produit C"]
    C --> P1["Paiement 1"]
    C --> P2["Paiement 2"]
    L1 -. "jointure plate" .-> P1
    L1 -. "jointure plate" .-> P2
    L2 -. "jointure plate" .-> P1
    L2 -. "jointure plate" .-> P2
    L3 -. "jointure plate" .-> P1
    L3 -. "jointure plate" .-> P2
~~~

Le dessin montre l'effet multiplicatif. La table source a trois lignes de commande et deux paiements, mais le produit combiné possède six combinaisons. SUM(ligne_total) dans ce résultat ajouterait chaque ligne deux fois. SUM(paiement.montant) ajouterait chaque paiement trois fois.

La correction ne consiste pas forcément à appliquer SUM(DISTINCT montant). Deux paiements légitimes peuvent avoir le même montant, et deux lignes de produits peuvent aussi avoir la même valeur. DISTINCT sur le montant fusionnerait alors des faits différents. Il faut agréger chaque ensemble à sa granularité avant de réunir les résultats, ou construire des sous-requêtes/CTE qui seront étudiées plus tard. Pour le niveau débutant, on peut résoudre le cas en effectuant un agrégat par commande séparément puis en reliant les résultats.

Exemple : d'abord calculer le total de lignes par commande :

~~~sql
SELECT
    commande_id,
    SUM(quantite * prix_unitaire) AS total_lignes
FROM lignes_commande
GROUP BY commande_id;
~~~

Puis calculer le total des paiements par commande séparément :

~~~sql
SELECT
    commande_id,
    SUM(montant) AS total_paye
FROM paiements
WHERE statut = 'accepte'
GROUP BY commande_id;
~~~

Ces deux résultats possèdent une ligne par commande, donc leur combinaison peut être plus sûre si chaque agrégat garantit cette granularité. Une requête complète pourrait utiliser des sous-requêtes ou des CTE pour joindre les deux totaux. Ces constructions feront l'objet d'un cours avancé ; l'idée à retenir maintenant est qu'on ne doit pas additionner des faits provenant de plusieurs relations multiples après les avoir multipliés.

### 13.1 Comment détecter le double comptage ?

Avant d'ajouter un agrégat, comptez les lignes avant et après chaque jointure. Choisissez une commande connue et inspectez chaque détail. Si une commande avec trois produits et deux paiements apparaît six fois, vous avez identifié la multiplication. Comparez ensuite la somme attendue calculée à la main avec le résultat de la requête.

Ne concluez pas que toute répétition de commande_id est erronée. Une requête de détail peut légitimement répéter l'identifiant commande pour chaque produit. Le problème survient lorsqu'on additionne une valeur au niveau commande autant de fois qu'elle est répétée au niveau ligne. Toujours demander à quel niveau appartient la mesure calculée.

## 14. CASE : classer les données avant de les agréger

CASE permet de calculer une catégorie ou une valeur selon des conditions. Il est utile pour créer des groupes de prix, compter des statuts ou comparer plusieurs catégories dans un même résultat.

~~~sql
SELECT
    CASE
        WHEN prix_catalogue < 20 THEN 'economique'
        WHEN prix_catalogue < 100 THEN 'intermediaire'
        ELSE 'premium'
    END AS categorie_prix,
    COUNT(*) AS nombre_produits
FROM produits
GROUP BY
    CASE
        WHEN prix_catalogue < 20 THEN 'economique'
        WHEN prix_catalogue < 100 THEN 'intermediaire'
        ELSE 'premium'
    END
ORDER BY categorie_prix;
~~~

Cette requête illustre le regroupement selon une expression. Les bornes doivent correspondre à la règle métier ; la catégorie « premium » inclut toutes les valeurs supérieures ou égales à 100, et les prix NULL peuvent suivre une branche ELSE si le schéma les autorise. Un modèle plus clair peut ajouter une branche WHEN prix_catalogue IS NULL pour distinguer l'absence d'information.

Selon le moteur, on peut parfois grouper par alias ou position, mais il ne faut pas dépendre de ces formes sans les vérifier. Pour le débutant, répéter l'expression rend le lien entre SELECT et GROUP BY explicite. Dans une requête plus complexe, une sous-requête ou une CTE peut éviter de répéter la logique ; ce sera un sujet ultérieur.

## 15. Exemple de bout en bout : total par commande

Nous voulons calculer le montant des lignes pour chaque commande. Le jeu synthétique suivant rend le résultat vérifiable à la main.

\`lignes_commande\` :

| commande_id | produit_id | quantite | prix_unitaire |
|---:|---:|---:|---:|
| 100 | 10 | 2 | 25.00 |
| 100 | 20 | 1 | 12.50 |
| 101 | 20 | 3 | 12.50 |
| 102 | 30 | 1 | 149.90 |

Le total de la commande 100 est 2 × 25,00 + 1 × 12,50 = 62,50. Celui de la commande 101 est 3 × 12,50 = 37,50. Celui de la commande 102 est 149,90.

~~~sql
SELECT
    commande_id,
    SUM(quantite * prix_unitaire) AS total_lignes
FROM lignes_commande
GROUP BY commande_id
ORDER BY commande_id;
~~~

Résultat attendu :

| commande_id | total_lignes |
|---:|---:|
| 100 | 62.50 |
| 101 | 37.50 |
| 102 | 149.90 |

Le résultat possède une ligne par commande ayant au moins une ligne de détail. Une commande qui n'a aucune ligne n'apparaît pas. Si le système permet des commandes brouillon sans détail, un rapport qui doit les afficher toutes utilisera une approche différente.

Pour afficher toutes les commandes y compris celles sans ligne, partez de commandes et effectuez un LEFT JOIN sur lignes_commande. La somme peut être NULL si aucune ligne ne correspond. COALESCE peut alors être utilisé pour afficher zéro, à condition que le sens métier du rapport soit bien « aucun détail équivaut à total de lignes égal à zéro », et non « montant inconnu ».

~~~sql
SELECT
    co.commande_id,
    COALESCE(SUM(lc.quantite * lc.prix_unitaire), 0) AS total_lignes
FROM commandes AS co
LEFT JOIN lignes_commande AS lc
    ON lc.commande_id = co.commande_id
GROUP BY co.commande_id
ORDER BY co.commande_id;
~~~

Ce cas illustre une distinction importante : le choix de la table de départ définit en partie la population du rapport. L'agrégation n'ajoute pas spontanément les entités absentes de la table source. Si l'on veut montrer tous les clients ou toutes les commandes, il faut partir de cette population de référence.

## 16. Atelier pratique guidé : rapports de boutique

L'atelier combine les jointures et les agrégations sur une boutique fictive. Travaillez avec un schéma de laboratoire que vous pouvez réinitialiser. Les types et l'identité des clés doivent être adaptés au moteur installé. Les données sont synthétiques et n'appartiennent à aucun client réel.

### Étape 1 — Préparer les tables et les données

Utilisez les tables clients, commandes, produits et lignes_commande telles qu'elles ont été présentées dans les cours précédents. Pour vérifier les résultats de manière déterministe, voici un jeu de données minimal conceptuel :

**Clients**

| client_id | nom |
|---:|---|
| 1 | Amina |
| 2 | Samuel |
| 3 | Nadia |
| 4 | David |

**Commandes**

| commande_id | client_id | statut |
|---:|---:|---|
| 100 | 1 | confirmee |
| 101 | 1 | brouillon |
| 102 | 2 | confirmee |

**Lignes de commande**

| commande_id | produit_id | quantite | prix_unitaire |
|---:|---:|---:|---:|
| 100 | 10 | 2 | 25.00 |
| 100 | 20 | 1 | 12.50 |
| 101 | 20 | 3 | 12.50 |
| 102 | 30 | 1 | 149.90 |

**Produits**

| produit_id | nom |
|---:|---|
| 10 | Clavier |
| 20 | Souris |
| 30 | Écran |

Avec ces données, Amina possède deux commandes, Samuel une, Nadia et David aucune. La commande 100 contient deux lignes, la commande 101 une ligne et la commande 102 une ligne.

### Étape 2 — Afficher les commandes avec leur client

~~~sql
SELECT
    co.commande_id,
    c.nom AS client,
    co.statut
FROM commandes AS co
INNER JOIN clients AS c
    ON c.client_id = co.client_id
ORDER BY co.commande_id;
~~~

Vous devez obtenir trois lignes, une par commande. Les clients sans commande n'apparaissent pas, ce qui correspond à l'objet du rapport : ici on liste les commandes existantes.

### Étape 3 — Afficher tous les clients et leur nombre de commandes

~~~sql
SELECT
    c.client_id,
    c.nom,
    COUNT(co.commande_id) AS nombre_commandes
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
GROUP BY c.client_id, c.nom
ORDER BY c.client_id;
~~~

Résultat attendu :

| client_id | nom | nombre_commandes |
|---:|---|---:|
| 1 | Amina | 2 |
| 2 | Samuel | 1 |
| 3 | Nadia | 0 |
| 4 | David | 0 |

Si Nadia ou David reçoit le nombre 1, examinez l'utilisation de COUNT(*) et la nature de la ligne créée par LEFT JOIN. Si ces clients disparaissent, vérifiez si la requête utilise INNER JOIN ou un filtre WHERE sur la table de droite.

### Étape 4 — Calculer le total de chaque commande

~~~sql
SELECT
    commande_id,
    SUM(quantite * prix_unitaire) AS total_lignes
FROM lignes_commande
GROUP BY commande_id
ORDER BY commande_id;
~~~

Résultat attendu : commande 100 = 62,50 ; commande 101 = 37,50 ; commande 102 = 149,90. Faites le calcul à la main avant d'exécuter la requête. Si le résultat diffère, vérifiez les quantités, les prix, les lignes en double et le type de données.

### Étape 5 — Trouver les clients possédant au moins deux commandes

~~~sql
SELECT
    c.client_id,
    c.nom,
    COUNT(co.commande_id) AS nombre_commandes
FROM clients AS c
INNER JOIN commandes AS co
    ON co.client_id = c.client_id
GROUP BY c.client_id, c.nom
HAVING COUNT(co.commande_id) >= 2
ORDER BY nombre_commandes DESC, c.client_id ASC;
~~~

Résultat attendu : Amina. WHERE ne peut pas remplacer HAVING pour filtrer directement sur le total calculé avec COUNT dans cette requête. Les lignes doivent d'abord être regroupées avant que le critère de groupe ne soit appliqué.

### Étape 6 — Afficher tous les clients et compter uniquement les commandes confirmées

~~~sql
SELECT
    c.client_id,
    c.nom,
    COUNT(co.commande_id) AS commandes_confirmees
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
   AND co.statut = 'confirmee'
GROUP BY c.client_id, c.nom
ORDER BY c.client_id;
~~~

Résultat attendu : Amina = 1, Samuel = 1, Nadia = 0, David = 0. Si le filtre statut est placé dans WHERE, Nadia et David peuvent être exclus. C'est une bonne expérience pour comprendre la différence entre les conditions de jointure et les filtres appliqués au résultat.

### Étape 7 — Critères d'acceptation

L'atelier est terminé si vous obtenez trois commandes dans le détail, quatre clients dans le rapport client avec comptage, les totaux corrects par commande et seulement Amina dans le groupe des clients possédant au moins deux commandes. Vous devez également pouvoir expliquer pourquoi la requête qui affiche tous les clients utilise LEFT JOIN et COUNT(co.commande_id), et pourquoi le statut des commandes confirmées est placé dans ON.

Documentez le moteur, la version, les données utilisées, les requêtes et les résultats observés. Ne réinitialisez que la base de laboratoire. Si une requête donne un résultat inattendu, réduisez le jeu de données puis identifiez la première jointure ou agrégation à laquelle les lignes deviennent différentes de ce qui était prévu.

## 17. Exercices avec corrigés détaillés

### Exercice 1 — Distinguer INNER JOIN et LEFT JOIN

Une école veut afficher tous les apprenants, même ceux qui ne sont encore inscrits à aucun cours. Quelle jointure est la plus appropriée entre apprenants et inscriptions ?

**Corrigé.** LEFT JOIN, en partant de apprenants. INNER JOIN ne conserve que les apprenants ayant une inscription correspondante. Le choix dépend de la population attendue : un rapport d'inscriptions peut ne montrer que les inscriptions ; un annuaire complet des apprenants doit conserver les personnes à zéro inscription.

### Exercice 2 — Compter les commandes ou les lignes de commande

Un rapport joint commandes et lignes_commande, puis utilise COUNT(*). Pourquoi le chiffre obtenu peut-il être supérieur au nombre réel de commandes ?

**Corrigé.** Une commande peut avoir plusieurs lignes de détail. La jointure renvoie une ligne par combinaison commande-ligne, donc COUNT(*) mesure le nombre de lignes de commande, pas le nombre de commandes. On peut compter COUNT(DISTINCT co.commande_id) si la question est le nombre de commandes distinctes, ou écrire l'agrégation au niveau commande sans traverser inutilement les détails.

### Exercice 3 — Trouver les clients sans commande

Écrivez une requête qui renvoie les identifiants et noms des clients sans aucune commande.

**Corrigé.**

~~~sql
SELECT c.client_id, c.nom
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
WHERE co.commande_id IS NULL
ORDER BY c.client_id;
~~~

commande_id est la clé primaire d'une vraie commande et doit être non NULL. Quand la jointure ne trouve aucune commande, cette colonne est NULL dans le résultat. Évitez de filtrer sur une colonne nullable qui pourrait être NULL dans une commande existante.

### Exercice 4 — Compter les clients ayant commandé

Quelle expression convient pour compter les clients distincts ayant passé au moins une commande ?

**Corrigé.**

~~~sql
SELECT COUNT(DISTINCT client_id) AS nombre_clients
FROM commandes;
~~~

COUNT(DISTINCT client_id) compte les identifiants client distincts présents dans les commandes. COUNT(*) compterait les commandes. Les deux indicateurs sont différents lorsqu'un client peut passer plusieurs commandes.

### Exercice 5 — Calculer un total de lignes

Une commande comporte trois unités à 8,50 chacune et une unité à 12,00. Quelle expression permet d'obtenir son total de lignes ?

**Corrigé.** Le calcul est 3 × 8,50 + 1 × 12,00 = 37,50. Si toutes les lignes sont dans lignes_commande et si la commande_id filtre ce groupe, l'agrégat peut être écrit :

~~~sql
SELECT SUM(quantite * prix_unitaire) AS total_lignes
FROM lignes_commande
WHERE commande_id = 500;
~~~

La requête retourne le total de lignes enregistrées pour la commande 500. Les taxes, remises, frais et remboursements ne sont pas inclus sauf s'ils sont représentés dans le modèle.

### Exercice 6 — WHERE ou HAVING ?

On veut trouver les clients qui possèdent au moins trois commandes confirmées. Où placer le filtre sur le statut et où placer le seuil du nombre de commandes ?

**Corrigé.**

~~~sql
SELECT client_id, COUNT(*) AS commandes_confirmees
FROM commandes
WHERE statut = 'confirmee'
GROUP BY client_id
HAVING COUNT(*) >= 3;
~~~

WHERE retire les commandes non confirmées avant regroupement. HAVING filtre les groupes en fonction du total calculé. Cette requête ne compte que les commandes confirmées.

### Exercice 7 — Pourquoi LEFT JOIN ne conserve-t-il plus tous les clients ?

Une requête utilise LEFT JOIN commandes mais place \`WHERE commandes.statut = 'confirmee'\`. Les clients sans commande disparaissent. Expliquez le comportement et proposez une correction si l'on veut garder tous les clients.

**Corrigé.** Les lignes sans correspondance ont NULL dans commandes.statut ; le filtre WHERE n'est pas vrai pour ces lignes et les élimine. Si le but est de conserver tous les clients et seulement joindre les commandes confirmées, le filtre doit être placé dans ON :

~~~sql
SELECT c.client_id, c.nom, co.commande_id
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
   AND co.statut = 'confirmee';
~~~

### Exercice 8 — Interpréter COUNT(*), COUNT(colonne) et COUNT(DISTINCT)

Sur un LEFT JOIN, un client sans commande a une ligne de résultat où commande_id vaut NULL. Que retournent les trois formes au niveau global du rapport si elles sont évaluées sur la ligne artificielle du client sans commande ?

**Corrigé.** COUNT(*) compte cette ligne de résultat et ajoute 1 au total ; COUNT(commande_id) ignore la valeur NULL et ajoute 0 ; COUNT(DISTINCT commande_id) ne compte aucune commande distincte sur cette ligne. La forme exacte doit toujours être choisie selon l'objet métier compté.

### Exercice 9 — Détecter la multiplication des lignes

Une commande contient deux lignes de produits et trois paiements. Une jointure directe commande-lignes-paiements produit six lignes pour cette commande. Quel risque existe si l'on additionne le montant des produits dans ce résultat ?

**Corrigé.** Chaque ligne de produit apparaît une fois par paiement, donc son montant est répété trois fois. La somme des lignes est multipliée par trois. Il faut agréger les lignes et les paiements séparément à la granularité commande avant de les combiner, ou choisir une autre stratégie de requête. SUM(DISTINCT montant) n'est pas une correction sûre, puisque deux faits légitimes peuvent posséder le même montant.

### Exercice 10 — Comprendre AVG après une jointure

Une commande avec cinq lignes de produits apparaît cinq fois dans une jointure. Vous calculez AVG(total_commande) à partir de ce résultat. Pourquoi le résultat peut-il être biaisé ?

**Corrigé.** Le total de la commande est répété cinq fois, alors qu'une commande avec une seule ligne ne l'est qu'une fois. Les commandes sont donc pondérées selon leur nombre de lignes de détail. Pour obtenir la moyenne par commande, calculez d'abord un total par commande puis faites la moyenne sur ce résultat de granularité commande.

### Exercice 11 — Groupement par plusieurs colonnes

Écrivez une requête qui compte les commandes par client et par statut. Expliquez pourquoi un client peut apparaître plusieurs fois.

**Corrigé.**

~~~sql
SELECT client_id, statut, COUNT(*) AS nombre
FROM commandes
GROUP BY client_id, statut
ORDER BY client_id, statut;
~~~

Une ligne correspond à une combinaison client-statut. Un client qui a des commandes brouillon et confirmées apparaît une fois par statut présent. Ce comportement est attendu et différent d'un rapport qui exige une seule ligne par client.

### Exercice 12 — Un agrégat vide ou NULL

Vous calculez SUM(montant) sur une sélection qui ne contient aucune ligne ou dont toutes les valeurs de montant sont NULL. Pourquoi ne faut-il pas toujours conclure que le total vaut zéro ?

**Corrigé.** Selon les fonctions et le moteur, SUM peut produire NULL lorsqu'aucune valeur n'est disponible à additionner. Zéro est une valeur réelle, alors que NULL peut signifier qu'aucune contribution n'est connue ou qu'aucune ligne ne correspond. COALESCE peut fournir zéro si la règle métier définit explicitement l'absence de lignes comme un total nul.

## 18. Défi final corrigé — construire un rapport commercial fiable

### Mission

Une boutique souhaite un rapport qui affiche tous les clients, le nombre de commandes confirmées de chaque client et le total des lignes de leurs commandes confirmées. Les clients sans commande confirmée doivent apparaître avec un nombre égal à zéro et un total égal à zéro si aucune ligne ne contribue au rapport. Vous devez éviter de compter deux fois une commande et expliquer vos choix.

### Étape A — Définir la granularité

La sortie demandée est une ligne par client. Le nombre de commandes compte les identifiants de commande, pas les lignes de produits. Le total est la somme des quantités multipliées par les prix unitaires des lignes qui appartiennent à des commandes confirmées. Ce total de lignes n'inclut pas les frais, taxes, remises ou remboursements qui ne sont pas présents dans le modèle.

Écrivez les hypothèses :
- une commande possède un identifiant unique ;
- les lignes d'une commande sont reliées via commande_id ;
- les prix appliqués et quantités sont présents sur les lignes ;
- la requête considère uniquement le statut confirmé ;
- tous les clients doivent être conservés ;
- les clients sans commande confirmée doivent afficher zéro si le contrat du rapport le définit ainsi.

### Étape B — Calculer les totaux par commande séparément

Un premier calcul donne une ligne par commande confirmée :

~~~sql
SELECT
    co.commande_id,
    co.client_id,
    SUM(lc.quantite * lc.prix_unitaire) AS total_lignes
FROM commandes AS co
INNER JOIN lignes_commande AS lc
    ON lc.commande_id = co.commande_id
WHERE co.statut = 'confirmee'
GROUP BY co.commande_id, co.client_id;
~~~

Cette étape produit un total par commande qui possède des lignes. Si des commandes confirmées sans ligne sont autorisées, il faut décider si elles ont un total de zéro, si elles sont invalides ou si elles doivent être exclues. Le modèle doit exprimer cette règle plutôt que de la supposer.

### Étape C — Méthode complète recommandée

Dans une requête complète, un agrégat par commande peut être construit dans une sous-requête ou une CTE puis relié aux clients. Les sous-requêtes et CTE seront détaillées dans un cours ultérieur ; l'exemple suivant les présente brièvement pour montrer la logique de granularité.

~~~sql
WITH commandes_confirmees AS (
    SELECT
        commande_id,
        client_id
    FROM commandes
    WHERE statut = 'confirmee'
),
totaux_par_commande AS (
    SELECT
        commande_id,
        SUM(quantite * prix_unitaire) AS total_lignes
    FROM lignes_commande
    GROUP BY commande_id
),
synthese_client AS (
    SELECT
        cc.client_id,
        COUNT(*) AS nombre_commandes_confirmees,
        SUM(COALESCE(tc.total_lignes, 0)) AS total_lignes_confirmees
    FROM commandes_confirmees AS cc
    LEFT JOIN totaux_par_commande AS tc
        ON tc.commande_id = cc.commande_id
    GROUP BY cc.client_id
)
SELECT
    c.client_id,
    c.nom,
    COALESCE(sc.nombre_commandes_confirmees, 0) AS nombre_commandes_confirmees,
    COALESCE(sc.total_lignes_confirmees, 0) AS total_lignes_confirmees
FROM clients AS c
LEFT JOIN synthese_client AS sc
    ON sc.client_id = c.client_id
ORDER BY c.client_id;
~~~

La première partie sélectionne les commandes confirmées. La deuxième agrège les lignes au niveau commande. La troisième combine chaque commande confirmée à un total déjà consolidé, puis calcule les indicateurs au niveau client. Enfin, l'agrégat par client est joint à tous les clients, ce qui conserve ceux qui n'ont aucune commande confirmée.

Ce modèle évite la multiplication entre plusieurs tables enfants, parce que les lignes de commande sont d'abord résumées à une ligne par commande. Il utilise COUNT(*) à un niveau où chaque ligne correspond bien à une commande confirmée. Si des commandes sans ligne doivent être considérées invalides, le comportement du total zéro doit être accompagné d'une validation du métier ; le SQL ci-dessus considère ce cas comme total de lignes égal à zéro.

Les CTE sont disponibles dans les versions modernes de nombreux moteurs, mais la syntaxe précise et leurs possibilités dépendent du SGBD. Consultez la documentation de la version utilisée. L'objectif du défi est surtout de comprendre la séparation des granularités avant de réunir des résultats.

### Étape D — Vérifier avec un jeu minimal

Prenez un client Amina avec deux commandes confirmées : une commande dont les lignes valent 62,50 et une autre dont les lignes valent 37,50. Son nombre de commandes confirmées est 2 et son total de lignes est 100,00. Un client Nadia sans commande confirmée doit apparaître avec 0 et 0,00 si le contrat du rapport l'exige.

Vérifiez séparément :
- le nombre de commandes confirmées dans la table source ;
- le total de lignes calculé pour chaque commande ;
- le total obtenu par client ;
- la présence des clients à zéro ;
- l'absence de multiplication quand une commande a plusieurs lignes ;
- l'exclusion des commandes qui ne sont pas confirmées.

Si un résultat diffère, ne changez pas immédiatement la requête en ajoutant DISTINCT. Reproduisez le cas avec une commande et deux lignes, puis avec deux commandes et plusieurs lignes. Le jeu minimal réduit le nombre de causes possibles.

### Étape E — Corrigé et critères d'acceptation

La solution est acceptée si la sortie contient exactement une ligne par client, si le nombre de commandes compte les commandes confirmées uniques, si le total correspond à la somme des lignes retenues, si les clients sans commande restent visibles et si la requête ne multiplie pas un total de commande par le nombre de lignes. Vous devez pouvoir expliquer la granularité de chaque CTE et la raison pour laquelle les agrégations sont séparées.

Le rapport n'est pas un état comptable complet. Il ne traite ni de taxes, ni de remboursements, ni de commandes annulées, ni de règlements partiels ou multiples, sauf si des règles complémentaires sont ajoutées. Documentez ces limites avant de réutiliser un indicateur dans un tableau de bord officiel.

## 19. Méthode de diagnostic d'un résultat inattendu

Une jointure incorrecte produit souvent trop de lignes ; une jointure trop restrictive en produit trop peu. Un agrégat peut être techniquement valide mais calculer la mauvaise unité. Pour diagnostiquer, procédez par étapes :

1. Écrivez la question métier en une phrase testable.
2. Décrivez la granularité attendue de chaque ligne du résultat.
3. Comptez les lignes de chaque table source dans un jeu de test connu.
4. Exécutez la jointure seule, sans agrégat, en sélectionnant les identifiants des deux côtés.
5. Repérez la première relation où une ligne se multiplie ou disparaît.
6. Ajoutez les filtres un par un et vérifiez quelles lignes ils excluent.
7. Ajoutez l'agrégat seulement lorsque la granularité est comprise.
8. Vérifiez COUNT(*) par comparaison avec COUNT(DISTINCT clé) lorsque cela a du sens.
9. Comparez les totaux à un calcul manuel sur quelques enregistrements.
10. Documentez la correction et ajoutez un test de non-régression.

Les tests manuels ne remplacent pas les contrôles automatiques, mais ils rendent le diagnostic plus rapide. Choisissez des identifiants concrets, par exemple une commande avec deux lignes et une autre avec une seule. Les valeurs simples permettent de calculer le résultat attendu sans outil. Ensuite, le même scénario peut être conservé dans un test automatisé.

Ne faites pas confiance à un total seulement parce qu'il semble plausible. Une somme deux fois trop élevée peut ressembler à une augmentation normale. Un nombre de clients peut être égal au nombre de commandes par hasard. Pour chaque indicateur important, définissez l'objet compté, les statuts inclus, la période, le traitement des absences et les règles de duplication.

## 20. Bonnes pratiques de lisibilité et de maintenance

Une requête de rapport doit être facile à relire par une autre personne. Utilisez des alias explicites, écrivez chaque jointure sur ses propres lignes, indentez les conditions ON et WHERE, et nommez les agrégats avec un sens métier. Évitez les abréviations non expliquées lorsque plusieurs tables sont impliquées.

~~~sql
SELECT
    c.client_id,
    c.nom,
    COUNT(co.commande_id) AS nombre_commandes
FROM clients AS c
LEFT JOIN commandes AS co
    ON co.client_id = c.client_id
GROUP BY
    c.client_id,
    c.nom
ORDER BY
    c.client_id;
~~~

La mise en forme rend visibles les responsabilités : SELECT définit les colonnes, FROM la population principale, LEFT JOIN la relation et la préservation des clients, GROUP BY la granularité, ORDER BY l'ordre. La requête est plus facile à faire évoluer et à discuter lors d'une revue.

Les noms d'indicateurs doivent être honnêtes. \`total_lignes\` ne doit pas être appelé \`chiffre_affaires\` si les règles de chiffre d'affaires ne sont pas couvertes. \`nombre_commandes\` ne doit pas compter les lignes de détail. \`clients_actifs\` doit correspondre à une définition explicite de l'activité. Les alias font partie du contrat de sortie et influencent l'interprétation de l'indicateur.

Une requête partagée par plusieurs systèmes devrait être accompagnée d'une description des colonnes retournées, de leur unité et des filtres utilisés. Les définitions d'indicateurs dans une équipe doivent être cohérentes ; sinon, deux tableaux de bord peuvent afficher des chiffres différents tout en étant techniquement valides.

Les performances seront étudiées dans un cours dédié. Néanmoins, la clarté aide aussi l'optimisation : des clés compatibles, des conditions de jointure correctes et des agrégats au bon niveau sont souvent plus faciles à analyser qu'une seule requête confuse. Ne remplacez pas une logique métier lisible par une astuce de performance sans mesurer et vérifier le résultat.

## 21. Parcours pratique de consolidation

**Séance 1 — Relier deux tables.** Dessinez la relation client-commandes et écrivez une jointure interne. Ajoutez un client sans commande et observez sa disparition. Remplacez par LEFT JOIN et expliquez la différence.

**Séance 2 — Trouver les absences.** Cherchez les clients sans commande en filtrant sur la clé primaire de droite avec IS NULL. Essayez ensuite volontairement de filtrer sur une colonne facultative pour comprendre pourquoi le choix de la colonne testée compte.

**Séance 3 — Compter.** Comparez COUNT(*), COUNT(commandes.commande_id) et COUNT(DISTINCT commandes.commande_id) dans des jeux de données qui contiennent une relation un-à-plusieurs. Décrivez l'objet compté dans chaque cas.

**Séance 4 — Grouper.** Calculez le nombre de commandes par client puis par client et statut. Écrivez une phrase décrivant la granularité de chaque sortie. Comparez les nombres de lignes et expliquez pourquoi un client peut apparaître plusieurs fois.

**Séance 5 — Totaux.** Calculez les montants de ligne puis un total par commande. Faites le calcul à la main pour au moins deux commandes. Vérifiez si une commande sans détail doit être exclue ou affichée avec un total nul selon le besoin.

**Séance 6 — Détecter la multiplication.** Créez une commande avec deux lignes et trois paiements fictifs. Joignez les trois tables et comptez les lignes. Calculez les sommes séparément, puis démontrez comment la somme d'une table enfant peut être répétée par la jointure.

**Séance 7 — Vérifier.** Transformez les résultats attendus en tests reproductibles. Documentez les tables, les données synthétiques, le moteur et les valeurs attendues. Une autre personne doit pouvoir rejouer le test sans utiliser des données réelles.

L'objectif est d'acquérir les réflexes d'analyse : comprendre les relations, choisir une jointure selon la population attendue, définir la granularité, agréger au bon niveau et vérifier les indicateurs. La syntaxe devient plus naturelle lorsque vous savez expliquer chaque étape.

## 22. Checklist de maîtrise

Avant de poursuivre le parcours, assurez-vous de pouvoir expliquer et démontrer les points suivants :

- Je sais ce que représente une ligne dans chaque table et dans le résultat.
- Je sais écrire une INNER JOIN au moyen d'une clé de relation pertinente.
- Je sais utiliser LEFT JOIN pour conserver la population de gauche, même sans correspondance.
- Je sais rechercher les parents sans enfant à l'aide d'un test IS NULL sur une clé de droite non nullable.
- Je comprends pourquoi un filtre WHERE sur la table de droite peut éliminer des lignes conservées par LEFT JOIN.
- Je sais placer une condition dans ON lorsqu'elle doit restreindre les correspondances sans exclure les lignes de gauche.
- Je sais expliquer la différence entre COUNT(*), COUNT(colonne) et COUNT(DISTINCT expression).
- Je sais écrire un GROUP BY et décrire la granularité de son résultat.
- Je sais expliquer la différence entre WHERE et HAVING.
- Je sais calculer SUM, AVG, MIN et MAX et préciser l'unité correspondante.
- Je sais pourquoi les fonctions d'agrégation ignorent généralement NULL pour l'expression qu'elles calculent.
- Je sais détecter le double comptage provoqué par la combinaison de plusieurs relations un-à-plusieurs.
- Je sais pourquoi SUM(DISTINCT montant) n'est pas une correction universelle du double comptage.
- Je sais contrôler une requête par un jeu de données simple et calculable manuellement.
- Je sais définir les limites d'un indicateur avant de le publier dans un rapport.

Si une notion reste fragile, reprenez le tableau de données minimal et prédisez chaque ligne avant d'exécuter la requête. L'exercice est particulièrement utile pour comprendre les jointures externes et le double comptage.

## 23. Synthèse finale

Les jointures relient les lignes de différentes tables selon une condition. INNER JOIN ne conserve que les correspondances. LEFT JOIN conserve toutes les lignes de gauche et complète les colonnes de droite par NULL lorsqu'aucune correspondance n'existe. Le choix de la jointure doit découler de la population que le rapport doit conserver. ON définit la correspondance ; WHERE filtre le résultat obtenu. Avec LEFT JOIN, déplacer un filtre de WHERE vers ON peut changer profondément les lignes conservées.

Une jointure ne transforme pas deux tables en une table ayant automatiquement une ligne par entité métier. Dans une relation un-à-plusieurs, la ligne parent peut être répétée pour chaque ligne enfant. Cette répétition est normale dans un détail, mais elle peut fausser un agrégat si l'on ne tient pas compte de la granularité. La jointure de plusieurs tables enfants peut produire un produit de leurs multiplicités et compter plusieurs fois les mêmes faits.

COUNT(*) compte les lignes du résultat ; COUNT(colonne) compte les valeurs non NULL de l'expression ; COUNT(DISTINCT expression) compte les valeurs distinctes non NULL. SUM additionne, AVG calcule une moyenne, MIN et MAX trouvent des extrêmes. GROUP BY crée un résultat par groupe ; WHERE filtre les lignes avant l'agrégation et HAVING filtre les groupes après agrégation. Les NULL, les lignes absentes et les règles métier doivent être compris avant de publier un total ou un indicateur.

La qualité d'une requête se juge à la fois sur sa syntaxe, son sens et ses preuves. Définissez la granularité attendue, vérifiez les relations, comparez un petit jeu de données à un calcul manuel et ajoutez des tests qui empêchent le défaut de revenir. C'est ce raisonnement qui permet de produire des rapports SQL fiables.

## Références techniques

Les liens officiels ci-dessous permettent de vérifier la syntaxe et les différences propres aux moteurs. Consultez la documentation correspondant à la version réellement utilisée.

- PostgreSQL 18, expressions de jointure : https://www.postgresql.org/docs/18/queries-table-expressions.html
- PostgreSQL 18, fonctions d'agrégation : https://www.postgresql.org/docs/18/functions-aggregate.html
- PostgreSQL 18, expressions conditionnelles : https://www.postgresql.org/docs/18/functions-conditional.html
- MySQL 8.4, syntaxe JOIN : https://dev.mysql.com/doc/refman/8.4/en/join.html
- MySQL 8.4, fonctions d'agrégation : https://dev.mysql.com/doc/refman/8.4/en/aggregate-functions.html
- SQLite, SELECT et clauses de jointure : https://www.sqlite.org/lang_select.html
- SQLite, fonctions d'agrégation : https://www.sqlite.org/lang_aggfunc.html

La documentation décrit le comportement du moteur, mais elle ne définit pas les règles commerciales de la boutique. Avant de produire un indicateur, confirmez les statuts inclus, la période, les unités, le traitement des remboursements et la signification des absences avec les responsables du processus.
