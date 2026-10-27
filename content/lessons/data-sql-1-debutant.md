# Requêtes SQL de base (SELECT, INSERT) — Débutant

> **Mise en contexte.** Vous venez de découvrir les tables, les identifiants, les clés étrangères et les contraintes. Il est maintenant temps d'interroger une base et d'y ajouter des données. Imaginez une boutique qui souhaite connaître ses produits disponibles, retrouver les commandes d'un client et enregistrer une nouvelle commande. Ces besoins semblent simples, mais une requête mal filtrée peut retourner beaucoup trop de lignes, une insertion incomplète peut créer des données ambiguës, et une chaîne concaténée dans une requête peut ouvrir une faille d'injection SQL. Apprendre SQL consiste donc à exprimer une intention avec précision, à respecter le contrat du schéma et à vérifier ce que le moteur a réellement fait.

## 1. Objectifs pédagogiques

À la fin de ce cours, vous devrez savoir lire et écrire des requêtes SQL simples sans les considérer comme des formules à copier aveuglément. Vous apprendrez à choisir les colonnes utiles avec \`SELECT\`, à lire les données depuis une table avec \`FROM\`, à filtrer les lignes avec \`WHERE\`, à combiner des conditions, à trier les résultats, à limiter leur nombre et à reconnaître le rôle de \`DISTINCT\`. Vous saurez aussi insérer une ligne avec \`INSERT\`, insérer plusieurs lignes, omettre une colonne qui dispose d'une valeur par défaut, comprendre les contraintes qui peuvent rejeter une insertion et vérifier l'état obtenu.

Une bonne requête satisfait plusieurs critères. Elle répond à une question métier définie ; elle cible la bonne table ; elle sélectionne les colonnes nécessaires ; elle filtre exactement les lignes recherchées ; elle respecte les types et les règles du schéma ; elle évite d'exposer des données qui ne sont pas nécessaires ; elle est suffisamment claire pour être relue ; et son résultat peut être vérifié. Pour une insertion, on ajoute la justesse des valeurs, la gestion des erreurs et, lorsque plusieurs opérations sont liées, la cohérence transactionnelle.

Ce cours se concentre sur \`SELECT\` et \`INSERT\`. Il n'a pas pour objectif de couvrir entièrement les jointures, les agrégations complexes, les sous-requêtes, les transactions avancées ou l'optimisation des plans d'exécution. Ces sujets viendront ensuite. Nous allons tout de même évoquer certains concepts pour vous apprendre à reconnaître ce qui relève de ce premier niveau et ce qui demande une étude plus approfondie.

Les objectifs sont opérationnels :

- traduire une question simple en une requête lisible ;
- sélectionner des colonnes explicites plutôt que dépendre systématiquement de \`SELECT *\` ;
- distinguer les filtres, le tri et la limitation du nombre de lignes ;
- comprendre les conditions qui impliquent \`NULL\` ;
- utiliser les paramètres pour séparer le code SQL des valeurs fournies ;
- ajouter des lignes en indiquant explicitement les colonnes ;
- anticiper les erreurs de clé primaire, clé étrangère, contrainte et type ;
- vérifier les résultats avant de considérer une opération terminée ;
- utiliser un environnement de test et ne jamais exécuter un essai destructif sur une base réelle sans procédure approuvée.

## 2. Prérequis et environnement

Le prérequis du parcours est **data-bases-debutant — Concepts des bases de données relationnelles**. Vous devez comprendre les tables, les lignes, les colonnes, les clés primaires, les clés étrangères et l'intérêt des contraintes. Si la notion de clé étrangère reste floue, revoyez la leçon précédente avant de poursuivre : les exemples d'insertion s'appuient directement sur l'intégrité référentielle.

Vous pouvez pratiquer avec SQLite, PostgreSQL ou MySQL. Pour un premier essai, SQLite est pratique parce qu'une base peut être enregistrée dans un fichier local. PostgreSQL et MySQL utilisent souvent un processus serveur et demandent de connaître l'adresse, le port, le compte et la base auxquels on se connecte. Les moteurs partagent de nombreux principes SQL, mais ils diffèrent sur certaines syntaxes, types, valeurs par défaut, mécanismes d'identification et options. Ne supposez jamais qu'un script spécifique à un moteur est automatiquement portable.

Avant de commencer, notez le nom de l'environnement, le moteur et sa version, le compte utilisé, le nom de la base et la manière de réinitialiser les données de test. Utilisez uniquement des données fictives. Évitez de mettre des secrets dans le code ou les captures, et ne copiez pas un exemple sur une base de production sans examen.

Dans ce cours, nous utilisons une petite base de boutique. Elle comprend les tables suivantes :

- \`clients\` : un enregistrement par client ;
- \`produits\` : un enregistrement par produit du catalogue ;
- \`commandes\` : un enregistrement par commande ;
- \`lignes_commande\` : les produits, quantités et prix appliqués à chaque commande.

Le schéma a été conçu dans le cours précédent. Pour permettre à chacun de répéter les exemples, voici une version synthétique de sa structure :

~~~mermaid
erDiagram
    CLIENTS ||--o{ COMMANDES : "passe"
    COMMANDES ||--|{ LIGNES_COMMANDE : "contient"
    PRODUITS ||--o{ LIGNES_COMMANDE : "est vendu dans"
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

Le diagramme montre les relations logiques, pas l'ordre physique dans lequel les lignes sont stockées. Le symbole PK indique une clé primaire et FK une clé étrangère. Pour ce cours, nous lirons surtout une table à la fois. Les jointures entre ces tables seront détaillées plus tard.

## 3. Comment lire une requête SQL

SQL est un langage déclaratif : on décrit le résultat que l'on souhaite, et le SGBD décide comment exécuter la requête. Une requête peut être écrite sur plusieurs lignes pour la rendre plus claire. Les espaces et retours à la ligne ne changent généralement pas le sens, mais une mise en forme cohérente aide à repérer les filtres manquants et à relire le code. Dans beaucoup d'interfaces, le point-virgule termine une instruction ; certains outils permettent d'exécuter une sélection sans le point-virgule final, mais il est utile de garder une convention régulière.

Une première requête :

~~~sql
SELECT nom, email
FROM clients;
~~~

Elle demande les colonnes \`nom\` et \`email\` depuis la table \`clients\`. Elle ne modifie pas les données. La base renvoie un jeu de résultats composé de zéro ou plusieurs lignes, chacune contenant ces deux colonnes.

~~~mermaid
flowchart TD
    Q["Question : quels noms et courriels ?"] --> S["SELECT nom, email"]
    S --> F["FROM clients"]
    F --> R["Le SGBD lit les lignes candidates"]
    R --> O["Le résultat contient nom et email"]
~~~

Il est utile de lire la requête dans l'ordre de la question : « sélectionner les noms et courriels depuis les clients ». Lorsqu'une requête grandit, la clause \`WHERE\` limite les lignes et \`ORDER BY\` spécifie leur ordre. Le texte d'une instruction SQL n'est pas une phrase française ; les clauses ont une syntaxe précise. Mais formuler d'abord l'intention dans un langage naturel aide à détecter ce qui manque.

Une requête peut retourner zéro ligne sans être en erreur. Par exemple, si aucun produit ne porte le nom recherché, une requête filtrée peut réussir et produire un résultat vide. Il faut distinguer l'échec technique d'une requête valide dont le jeu de résultats est vide. Selon le contexte, les deux états n'appellent pas la même réponse : le code doit éventuellement afficher « aucun résultat » plutôt qu'un message d'échec.

## 4. SELECT : choisir les colonnes utiles

### 4.1 La forme élémentaire

La forme la plus simple consiste à écrire les colonnes voulues après \`SELECT\`, puis la table après \`FROM\`.

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits;
~~~

Cette requête retourne chaque ligne visible de \`produits\`, mais seulement les trois colonnes demandées. Si la table contient des milliers de produits, la sortie peut être longue. Le fait de sélectionner trois colonnes ne limite pas le nombre de lignes ; c'est le rôle du filtrage et, le cas échéant, de la limitation.

Utilisez de préférence les noms de colonnes. Les noms doivent correspondre à ceux du schéma effectif. Certains moteurs sont sensibles aux règles de casse ou aux guillemets utilisés dans les noms d'objets. Évitez les noms ambigus comme \`value\`, \`data\` ou \`status\` lorsqu'ils ne décrivent pas suffisamment le sens. Dans un projet, les conventions de nommage doivent être cohérentes et documentées.

### 4.2 Pourquoi éviter \`SELECT *\` par défaut

L'astérisque signifie « toutes les colonnes de la source ». C'est pratique pour une exploration ponctuelle :

~~~sql
SELECT *
FROM produits;
~~~

Mais cela ne doit pas devenir le réflexe universel dans le code applicatif. Une nouvelle colonne peut être ajoutée plus tard et être renvoyée à toutes les applications qui utilisent l'astérisque. Le résultat peut devenir plus volumineux, exposer des informations non nécessaires ou perturber un traitement qui attendait une structure précise. En sélectionnant les colonnes explicites, vous rendez le contrat de sortie plus stable.

Il existe des cas où l'astérisque est acceptable : inspection manuelle dans un environnement de développement, exploration contrôlée d'une petite table ou test ciblé où toutes les colonnes sont précisément ce que l'on veut observer. Pour une API, un rapport récurrent ou un traitement de données, privilégiez une liste explicite.

La question à poser n'est pas « comment afficher toute la table ? » mais « quelles données sont nécessaires à cette opération ? ». La réponse permet de réduire les transferts, d'améliorer la clarté et parfois de limiter les risques de divulgation.

### 4.3 Renommer les colonnes de sortie avec AS

Un alias donne un nom à une colonne du résultat. Il ne renomme pas la colonne dans la table.

~~~sql
SELECT
    nom AS nom_produit,
    prix_catalogue AS prix_actuel
FROM produits;
~~~

L'alias est utile dans un rapport ou une interface qui attend une étiquette lisible. Il est aussi pratique lorsqu'une expression calcule une valeur :

~~~sql
SELECT
    nom,
    prix_catalogue * 1.20 AS prix_avec_taxe_indicatif
FROM produits;
~~~

L'expression ci-dessus illustre un calcul, mais elle ne constitue pas une règle complète de taxation. Le taux, la devise, l'arrondi, le pays, les exceptions et la date de validité ne sont pas définis. Ne réutilisez jamais cet exemple comme un calcul fiscal de production sans modèle métier spécifique.

L'alias peut être utilisé par certaines clauses selon le moteur, mais il ne faut pas présumer que chaque dialecte l'autorise partout. Pour des requêtes de débutant, le plus sûr est d'utiliser un alias pour nommer le résultat et de répéter une expression simple si nécessaire, plutôt que dépendre d'une particularité non vérifiée.

### 4.4 Valeurs littérales et expressions simples

Une requête peut renvoyer une expression calculée sans modifier la table :

~~~sql
SELECT
    produit_id,
    nom,
    prix_catalogue,
    prix_catalogue * 2 AS prix_double
FROM produits;
~~~

Les valeurs littérales sont aussi utiles pour tester une expression :

~~~sql
SELECT 2 + 3 AS resultat;
~~~

La possibilité de faire un calcul ne signifie pas que chaque calcul doit être effectué au niveau SQL. Un calcul métier peut être exécuté dans la base ou dans l'application selon les besoins, le volume, la cohérence et les responsabilités. La décision doit être consciente. Si le calcul est utilisé pour filtrer ou classer beaucoup de lignes, le lieu de calcul peut avoir des conséquences sur le volume de données transférées et le plan d'exécution. L'optimisation sera étudiée plus tard.

### 4.5 DISTINCT : retirer les doublons du résultat

Par défaut, une requête peut retourner plusieurs lignes identiques dans les colonnes sélectionnées. \`DISTINCT\` élimine les doublons de la sortie :

~~~sql
SELECT DISTINCT statut
FROM commandes;
~~~

Cette requête donne les valeurs différentes de \`statut\` observées dans les commandes. Elle ne modifie pas les données. Elle ne prouve pas non plus que la liste des valeurs autorisées est correcte : si le schéma accepte par erreur « expédié », « expediee », « envoyé » et « done », DISTINCT affichera ces variantes.

DISTINCT s'applique à l'ensemble des expressions sélectionnées. Par exemple, sélectionner statut et date_commande retourne des combinaisons distinctes statut-date, pas seulement les statuts uniques. Il faut choisir les colonnes selon la question précise.

N'utilisez pas DISTINCT pour masquer une jointure erronée ou une duplication inattendue des données. Dans le cours présent, nous ne détaillons pas les jointures, mais retenez le principe : si des doublons apparaissent là où ils ne devraient pas exister, identifiez la source avant de les supprimer visuellement. DISTINCT peut rendre un rapport plus clair, tout en dissimulant un problème de modèle ou de requête.

## 5. FROM : indiquer la source des données

La clause \`FROM\` indique d'où proviennent les lignes candidates : une table, une vue ou une autre source supportée par le moteur. Dans les exemples du niveau débutant, il s'agit d'une table existante.

~~~sql
SELECT nom, prix_catalogue
FROM produits;
~~~

Le nom de la table doit correspondre au schéma choisi. La requête échoue si la table n'existe pas ou si le compte n'a pas le droit d'y accéder. Une erreur de permission ne signifie pas toujours que la table a disparu. Avant de modifier le schéma, vérifiez la base, le schéma logique et le compte utilisés.

Lorsque plusieurs tables sont mentionnées dans FROM, il faut comprendre comment leurs lignes se combinent. Sans relation de jointure adaptée, les résultats peuvent se multiplier en produit cartésien. Les jointures feront l'objet d'un cours spécifique. Pour l'instant, utilisez une seule table à la fois, ou soyez certain de comprendre le rôle de chaque source.

Une table logique n'est pas nécessairement un fichier portant le même nom. Le SGBD peut répartir les données et leurs métadonnées dans plusieurs structures internes. Ne tentez pas de manipuler les fichiers physiques directement comme si l'on pouvait modifier une ligne de table en éditant un fichier texte.

## 6. WHERE : choisir les lignes qui répondent à la question

### 6.1 Le filtrage de base

\`WHERE\` indique une condition que les lignes doivent satisfaire pour apparaître dans le résultat. Par exemple :

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
WHERE prix_catalogue >= 20;
~~~

Cette requête ne renvoie que les produits dont le prix est supérieur ou égal à 20. Elle ne modifie pas la table. La condition porte sur chaque ligne candidate ; les lignes dont la condition est fausse ou inconnue ne sont pas retenues.

La formulation métier devrait précéder l'écriture. « Afficher les produits dont le prix est au moins 20 » peut se traduire par \`WHERE prix_catalogue >= 20\`. « Afficher les produits dont le prix est exactement 20 » devient \`WHERE prix_catalogue = 20\`. Les symboles ne sont pas interchangeables : \`>\` exclut l'égalité, tandis que \`>=\` l'inclut.

### 6.2 Opérateurs de comparaison

Les opérateurs que vous rencontrerez souvent sont :

| Opérateur | Signification | Exemple |
|---|---|---|
| \`=\` | égal à | \`statut = 'confirmee'\` |
| \`<>\` | différent de | \`statut <> 'annulee'\` |
| \`!=\` | différent de, pris en charge par de nombreux moteurs | préférez \`<>\` pour une forme standard |
| \`>\` | strictement supérieur | \`prix_catalogue > 50\` |
| \`>=\` | supérieur ou égal | \`quantite >= 2\` |
| \`<\` | strictement inférieur | \`prix_catalogue < 100\` |
| \`<=\` | inférieur ou égal | \`quantite <= 10\` |

Pour les valeurs textuelles, la comparaison dépend des règles de collation et de la configuration du moteur. Ne présumez pas que « A » et « a » seront considérés comme égaux partout. Si la recherche doit être insensible à la casse, choisissez une stratégie cohérente avec le SGBD et la langue, puis testez les accents et les caractères pertinents.

Les comparaisons de dates doivent également tenir compte du type réel. Une date est différente d'un horodatage, qui peut inclure une heure et un fuseau. Pour chercher les commandes d'une journée dans une colonne horodatée, une plage semi-ouverte est souvent plus sûre qu'une égalité avec une date, mais sa syntaxe et les conversions doivent être comprises pour le moteur.

### 6.3 Combiner AND et OR

\`AND\` exige que toutes les conditions réunies soient vraies. \`OR\` autorise qu'au moins une condition soit vraie. Les parenthèses clarifient les conditions combinées et évitent les erreurs de priorité.

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
WHERE prix_catalogue >= 10
  AND prix_catalogue <= 30;
~~~

Cette requête retourne les produits dont le prix est compris entre 10 et 30, bornes incluses.

Comparez avec :

~~~sql
SELECT commande_id, statut
FROM commandes
WHERE statut = 'brouillon'
   OR statut = 'confirmee'
  AND client_id = 1;
~~~

Dans les expressions SQL courantes, \`AND\` est évalué avant \`OR\`. Cette requête peut donc être comprise comme : statut brouillon, quel que soit le client, ou statut confirmée pour le client 1. Ce n'est probablement pas ce que voulait exprimer une personne qui entendait « les commandes brouillon ou confirmées du client 1 ».

La version plus claire est :

~~~sql
SELECT commande_id, statut
FROM commandes
WHERE client_id = 1
  AND (statut = 'brouillon' OR statut = 'confirmee');
~~~

Règle pratique : dès qu'une condition contient à la fois AND et OR, placez des parenthèses explicites autour des groupes qui correspondent à la logique métier. Cela rend l'intention visible lors d'une revue de code et réduit le risque d'erreur.

### 6.4 IN : tester plusieurs valeurs

\`IN\` permet de comparer une valeur à une liste :

~~~sql
SELECT commande_id, statut
FROM commandes
WHERE statut IN ('brouillon', 'confirmee');
~~~

Cette requête est souvent plus lisible qu'une série de conditions reliées par OR. Si la liste devient très longue ou est construite à partir d'une autre table, une approche plus structurée peut être préférable, mais elle dépasse le périmètre de ce cours.

Attention à la valeur NULL dans une liste IN ou NOT IN. Les règles de logique à trois valeurs peuvent rendre le résultat surprenant si la liste contient NULL. Pour un débutant, ne construisez pas de filtre NOT IN à partir d'une liste dont les valeurs ne sont pas maîtrisées. Vérifiez explicitement la présence de valeurs inconnues et privilégiez une logique dont la sémantique est claire.

### 6.5 BETWEEN : une plage inclusive

\`BETWEEN\` permet d'exprimer une plage avec ses bornes :

~~~sql
SELECT nom, prix_catalogue
FROM produits
WHERE prix_catalogue BETWEEN 10 AND 30;
~~~

La condition équivaut à une comparaison inclusive des deux bornes. Cela signifie que 10 et 30 sont également acceptés. Si votre règle métier veut exclure une borne, écrivez des comparaisons explicites. Pour une colonne de dates ou d'horodatages, vérifiez attentivement si la borne haute doit être incluse ; une période « du lundi au mardi » ne signifie pas toujours la même chose qu'un intervalle numérique inclusif.

### 6.6 LIKE : rechercher un motif textuel

\`LIKE\` sert à rechercher un motif. Le caractère \`%\` représente zéro ou plusieurs caractères et \`_\` représente un caractère, selon les règles SQL usuelles :

~~~sql
SELECT client_id, nom, email
FROM clients
WHERE nom LIKE 'A%';
~~~

Cette requête recherche les noms qui commencent par la lettre A, suivie de zéro ou plusieurs caractères. Elle ne signifie pas forcément « tous les noms dont la première lettre est A quelle que soit la casse », car le comportement de casse dépend du moteur et de la collation.

Autres exemples :

~~~sql
SELECT nom
FROM produits
WHERE nom LIKE '%clavier%';

SELECT nom
FROM produits
WHERE nom LIKE 'Souris_';
~~~

Le premier motif trouve « clavier » à n'importe quelle position, et le second correspond à « Souris » suivi d'un seul caractère. Le soulignement n'est pas un simple caractère décoratif dans un motif LIKE. Si vous devez rechercher un pourcentage ou un soulignement littéral, étudiez la syntaxe ESCAPE et les règles du moteur.

Un motif qui commence par \`%\` peut empêcher certains index ordinaires de servir efficacement, selon l'indexation et le moteur. Ce n'est pas une raison de bannir la recherche de sous-chaîne, mais il faut reconnaître qu'une requête fonctionnelle n'est pas nécessairement optimisée à grande échelle.

### 6.7 NULL : utiliser IS NULL

NULL représente l'absence d'une valeur connue ou enregistrée, selon le contrat de la colonne. Il ne doit pas être comparé comme un nombre ordinaire.

Incorrect pour rechercher les courriels absents :

~~~sql
SELECT client_id, nom
FROM clients
WHERE email = NULL;
~~~

Forme correcte :

~~~sql
SELECT client_id, nom
FROM clients
WHERE email IS NULL;
~~~

Et pour les valeurs connues :

~~~sql
SELECT client_id, nom
FROM clients
WHERE email IS NOT NULL;
~~~

La différence vient de la logique SQL à trois valeurs. Comparer quelque chose à NULL ne produit généralement pas TRUE, même lorsque la valeur testée est elle-même NULL ; le résultat de la comparaison est inconnu. Dans une clause WHERE, seules les lignes pour lesquelles la condition est vraie sont retenues. Cette règle est une source classique de bugs.

Si la colonne email a été définie NOT NULL, le filtre IS NULL ne devrait retourner aucune ligne dans un état conforme. Cela peut être utile pour tester la structure, mais ne remplace pas la vérification de la contrainte réelle et des éventuels chemins de migration.

## 7. Trier et limiter le résultat

### 7.1 ORDER BY : un ordre explicite

Sans \`ORDER BY\`, le SGBD ne garantit pas un ordre stable. Les lignes peuvent sembler arriver dans l'ordre des identifiants pendant un test, puis changer après la création d'un index, une migration, une mise à jour ou un changement de plan d'exécution.

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
ORDER BY prix_catalogue ASC, nom ASC;
~~~

ASC signifie ordre croissant. DESC signifie ordre décroissant. Vous pouvez trier par plusieurs colonnes : la première définit l'ordre principal ; la suivante départage les lignes qui ont la même valeur pour la première, et ainsi de suite.

~~~sql
SELECT commande_id, date_commande, statut
FROM commandes
ORDER BY date_commande DESC, commande_id DESC;
~~~

La seconde colonne sert de départage si plusieurs commandes ont la même date. Pour obtenir des résultats reproductibles, ajoutez souvent un identifiant unique comme dernier critère de tri. Le type du champ, la collation et la gestion des valeurs NULL peuvent influencer le détail du tri ; consultez le moteur si l'ordre exact est important.

### 7.2 LIMIT, FETCH et portabilité

Beaucoup de moteurs proposent \`LIMIT\` pour limiter le nombre de lignes renvoyées. Par exemple :

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
ORDER BY prix_catalogue DESC, produit_id ASC
LIMIT 5;
~~~

Cette requête renvoie au plus cinq lignes, dans l'ordre demandé. La syntaxe de limitation varie selon les moteurs : PostgreSQL et SQLite acceptent LIMIT, MySQL l'utilise aussi, tandis que d'autres interfaces peuvent privilégier FETCH FIRST. Ne mélangez pas les syntaxes sans vérifier le moteur cible.

LIMIT sans tri stable peut produire un sous-ensemble imprévisible. Si dix lignes partagent le même prix et que vous n'avez pas de critère de départage, il n'existe pas nécessairement un résultat unique pour les cinq premières. La règle est particulièrement importante lorsqu'une interface utilise une pagination.

L'OFFSET permet de sauter un nombre de lignes avant de retourner la suite, mais les grandes valeurs d'OFFSET peuvent devenir coûteuses et les modifications concurrentes peuvent provoquer des doublons ou des omissions entre deux pages. La pagination par clé ou curseur est un sujet d'optimisation ultérieur. Pour l'instant, retenez que l'ordre doit être déterministe et que la pagination doit être conçue selon les volumes et la fréquence des modifications.

### 7.3 La forme complète d'une requête simple

Une requête peut réunir plusieurs clauses :

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
WHERE prix_catalogue >= 10
  AND prix_catalogue < 100
ORDER BY prix_catalogue DESC, produit_id ASC
LIMIT 20;
~~~

La question métier est : « montrer au maximum vingt produits dont le prix est au moins 10 et strictement inférieur à 100, du plus cher au moins cher ». Réécrivez toujours la question en mots avant de modifier une requête importante. Le filtrage répond à « quelles lignes ? », le SELECT à « quelles colonnes ? », ORDER BY à « dans quel ordre ? » et LIMIT à « combien au maximum ? ».

~~~mermaid
flowchart TD
    A["Question métier"] --> B["Identifier la table source"]
    B --> C["Choisir les colonnes SELECT"]
    C --> D["Définir les conditions WHERE"]
    D --> E["Préciser l'ordre ORDER BY"]
    E --> F["Limiter les lignes si besoin"]
    F --> G["Exécuter puis vérifier les résultats"]
~~~

N'écrivez pas une clause LIMIT simplement pour cacher un jeu de données trop grand sans comprendre sa taille. Pour une inspection, limiter les lignes est souvent une bonne pratique. Pour un traitement métier qui doit inclure tous les résultats, une limite arbitraire peut produire un rapport incomplet.

## 8. Lire les résultats comme un contrat

Exécuter une requête est seulement une étape. Il faut ensuite vérifier que le résultat correspond à la question. Une requête qui retourne des lignes peut être fausse si elle a omis un filtre. Une requête qui retourne zéro ligne peut être correcte si aucun enregistrement ne correspond. Une requête peut également afficher les bonnes valeurs mais dans un ordre non garanti, ce qui est problématique pour une pagination ou un test automatisé.

Avant d'exécuter une requête, notez ce que vous attendez : quelles colonnes, quelles valeurs possibles, combien de lignes environ et quelles exclusions. Après l'exécution, comparez les observations avec cette attente. Si le nombre de lignes est étonnant, ne le corrigez pas manuellement : cherchez la cause, par exemple une condition manquante ou une hypothèse incorrecte sur les données.

Un jeu de résultats doit être lu dans son contexte. Une colonne \`prix_catalogue\` ne dit pas à elle seule dans quelle devise le montant est exprimé. Une colonne \`date_commande\` ne dit pas si l'heure a été conservée. Un champ \`statut\` peut représenter un vocabulaire technique ou une étape métier. Les requêtes ne peuvent pas compenser des conventions non documentées ; elles les rendent parfois plus visibles.

Pour une tâche récurrente, conservez une requête versionnée avec un exemple de résultat attendu ou un test vérifiable. Ne stockez pas les données sensibles dans un exemple pédagogique. Un bon test peut vérifier une propriété, comme « le produit le plus cher apparaît en premier » ou « tous les statuts retournés sont dans la liste autorisée », sans nécessiter une copie de toutes les données de production.

## 9. INSERT : ajouter des données sans ambiguïté

### 9.1 Pourquoi nommer les colonnes

\`INSERT\` ajoute une ou plusieurs lignes à une table. La forme recommandée précise la liste des colonnes cibles et associe une valeur à chaque colonne dans le même ordre.

~~~sql
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES (30, 'Écran', 149.90);
~~~

La commande demande d'ajouter un produit avec l'identifiant 30, le nom Écran et le prix catalogue 149,90. Si la table possède d'autres colonnes, elles doivent être compatibles avec les règles de la table : valeur par défaut, autorisation de NULL ou génération automatique. Si une colonne obligatoire n'a ni valeur fournie ni valeur par défaut, l'insertion peut être refusée.

Nommer les colonnes rend la commande plus résistante aux changements du schéma. Une insertion positionnelle sans liste de colonnes dépend de l'ordre complet des colonnes de la table et devient fragile si le modèle évolue. En code applicatif, listez explicitement les colonnes que vous avez l'intention de fournir.

Une erreur fréquente est de donner trois valeurs pour deux colonnes, ou d'associer le nom au champ du prix par mauvais ordre. Les colonnes et valeurs doivent se correspondre une à une. La meilleure défense est une mise en forme sur plusieurs lignes, des noms explicites et un petit test avant d'utiliser une insertion dans un traitement plus important.

### 9.2 Insérer plusieurs lignes en une instruction

De nombreux moteurs prennent en charge plusieurs groupes de valeurs dans un même INSERT :

~~~sql
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES
    (31, 'Webcam', 39.90),
    (32, 'Casque', 59.00),
    (33, 'Support écran', 22.50);
~~~

Cette écriture est compacte et permet au moteur de traiter plusieurs lignes dans une instruction. La prise en charge et les limites exactes sont spécifiques au moteur et à sa version. Pour les données volumineuses, les imports en lot ou les outils d'importation peuvent être plus adaptés qu'une énorme instruction littérale.

Si une valeur viole une contrainte, le comportement global dépend des garanties du moteur et du mode d'insertion utilisés. Ne supposez pas que toutes les bases réagiront exactement de la même manière à une erreur au milieu d'un lot. Vérifiez le comportement documenté, testez sur une base isolée et décidez comment enregistrer ou reprendre le lot en cas d'échec.

Les inserts multiples ne doivent pas être utilisés pour contourner un problème de qualité. Si une ligne comporte un identifiant existant ou une clé étrangère invalide, il faut comprendre le défaut. Une importation doit rapporter quelles lignes ont été acceptées, quelles lignes ont été rejetées et comment reprendre le traitement sans doublonner les données déjà chargées.

### 9.3 Omettre une colonne et utiliser DEFAULT

Supposons que le schéma gère une colonne date_creation par défaut. Il est possible d'omettre cette colonne afin que le moteur applique la valeur par défaut définie :

~~~sql
INSERT INTO clients (client_id, nom, email)
VALUES (3, 'Nadia Fotsing', 'nadia@example.test');
~~~

Cette requête ne fournit pas de date_creation. Elle ne fonctionnera ainsi que si la définition du schéma rend cette omission valide. Une colonne NOT NULL sans valeur par défaut peut provoquer un rejet. Une colonne auto-générée peut suivre une règle spéciale. Le comportement doit être vérifié dans le schéma effectif.

La valeur DEFAULT signifie « applique la valeur par défaut déclarée », pas « invente une valeur qui semble appropriée ». Une valeur par défaut doit correspondre au besoin métier. Par exemple, un statut initial peut être \`brouillon\` si c'est la règle du système, mais il serait risqué de définir automatiquement toutes les commandes comme payées.

Évitez de coder en dur une date ou un statut seulement parce que l'exemple a fonctionné une fois. Vérifiez si la valeur appartient au schéma ou à la règle de création. Les migrations peuvent modifier les valeurs par défaut ; un script d'insertion robuste doit connaître le contrat dont il dépend.

### 9.4 NULL dans une insertion

NULL peut représenter une valeur absente lorsque la colonne l'autorise et que ce sens est approprié :

~~~sql
INSERT INTO clients (client_id, nom, email)
VALUES (4, 'Yann Mbarga', NULL);
~~~

Cette insertion échouera si email est NOT NULL, comme dans le schéma d'exemple du cours précédent. Cet échec est normal : le modèle demande un courriel. Ne retirez pas la contrainte uniquement pour faire fonctionner une donnée de laboratoire ; modifiez le modèle seulement si la règle métier confirme que l'information peut être absente.

Si l'absence est autorisée, elle doit avoir un sens. Il peut s'agir d'une donnée inconnue, non fournie ou non applicable. Ce sont des états métier différents. Si l'application doit distinguer ces cas, un statut explicite peut être préférable à une seule valeur NULL. Le modèle doit éviter les interprétations ambiguës.

NULL n'est pas identique à la chaîne vide. Une insertion de \`''\` stocke une chaîne de longueur zéro si le type l'accepte. Elle ne signifie pas automatiquement « inconnue ». Si l'application accepte une chaîne vide pour un email, cela peut être une erreur de validation même si la colonne est techniquement textuelle. La base peut imposer NOT NULL, mais une règle plus précise peut demander une contrainte complémentaire et une validation applicative.

### 9.5 Identifiants générés automatiquement

Beaucoup de tables utilisent un identifiant généré automatiquement. Les syntaxes varient : PostgreSQL propose notamment les colonnes identity, MySQL possède AUTO_INCREMENT, et SQLite a ses propres règles pour INTEGER PRIMARY KEY et les mécanismes de génération associés. La forme exacte doit être choisie dans la documentation du moteur.

Le principe est qu'on peut omettre la colonne générée si le schéma est configuré pour la produire automatiquement. Ne créez pas une identité à la main dans une base où le compteur ou la séquence est géré par le SGBD, sauf si vous comprenez l'effet de la valeur manuelle sur les insertions suivantes.

Il faut également distinguer l'identifiant technique généré du code métier que l'utilisateur voit. Un numéro d'identification technique peut être stable sans être séquentiel sans interruption, public ou significatif. Les applications ne doivent pas utiliser l'identifiant comme preuve d'autorisation : connaître un identifiant ne doit pas donner le droit d'accéder à un enregistrement.

### 9.6 INSERT et les contraintes

Une insertion doit respecter les règles du schéma. Les principaux rejets que vous rencontrerez sont :

- **Clé primaire dupliquée** : l'identifiant existe déjà.
- **Violation de clé étrangère** : la ligne référence un parent inexistant.
- **Violation NOT NULL** : une valeur obligatoire est absente.
- **Violation UNIQUE** : la combinaison doit être unique et ne l'est pas.
- **Violation CHECK** : la valeur ne respecte pas une règle, par exemple une quantité positive.
- **Type ou format incorrect** : le moteur ne peut pas convertir la valeur comme attendu.
- **Permission insuffisante** : le compte n'a pas le droit d'insérer dans la table.

L'erreur est une information. Elle indique souvent que l'opération n'est pas compatible avec le modèle ou les droits. N'ajoutez pas automatiquement des privilèges administrateur, ne désactivez pas les contraintes et ne changez pas les types à l'aveugle. Vérifiez quelle précondition a échoué, puis corrigez la cause.

Lorsqu'un insert est rejeté, le programme doit gérer le rejet. Dans une application, cela peut signifier afficher un message compréhensible, journaliser un identifiant de corrélation sans exposer de données sensibles et laisser l'opérateur corriger la saisie. Le détail technique de l'erreur ne doit pas nécessairement être affiché à l'utilisateur final, surtout s'il révèle des noms internes ou des données.

~~~mermaid
flowchart TD
    A["Préparer les colonnes et valeurs"] --> B["Exécuter INSERT"]
    B --> C{"Le SGBD accepte-t-il l'opération ?"}
    C -->|Oui| D["Vérifier la ligne créée"]
    C -->|Non| E["Identifier la contrainte ou la cause"]
    E --> F["Corriger la donnée ou la logique"]
    F --> G["Rejouer un test isolé"]
    D --> H["Confirmer les postconditions"]
~~~

## 10. Les valeurs paramétrées et la sécurité SQL

### 10.1 Ne pas construire une requête en concaténant des entrées

Une application peut vouloir rechercher un produit dont le nom est fourni par une personne. Il serait dangereux de concaténer directement la valeur dans la chaîne SQL :

~~~python
# Exemple à ne pas utiliser avec une entrée externe.
sql = "SELECT produit_id, nom FROM produits WHERE nom = '" + user_input + "'"
~~~

Si user_input contient des caractères qui modifient la syntaxe SQL, la requête ne représente plus uniquement la recherche voulue. Cela peut provoquer des erreurs, contourner un filtre ou, dans des cas plus graves, permettre une injection SQL. Le problème est une confusion entre le code SQL et les données qui lui sont fournies.

La solution habituelle est d'utiliser des paramètres liés, via l'interface de la bibliothèque ou du pilote. Le moteur reçoit la structure de la requête et les valeurs selon le protocole prévu, au lieu de traiter une chaîne entièrement reconstruite.

~~~python
# Exemple avec le module sqlite3 de Python.
cursor.execute(
    "SELECT produit_id, nom FROM produits WHERE nom = ?",
    (user_input,)
)
rows = cursor.fetchall()
~~~

Ici, le point d'interrogation est un paramètre du pilote SQLite utilisé en Python. Ce n'est pas une syntaxe universelle à copier dans tous les pilotes. Certains pilotes PostgreSQL ou MySQL utilisent par exemple un marqueur \`%s\` ou une forme nommée. Consultez la documentation de la bibliothèque réellement utilisée : ne remplacez pas les marqueurs à la main et ne supposez pas que le format est identique partout.

Un paramètre peut représenter une valeur, pas un nom de table ou une direction de tri dans toutes les interfaces. Si le programme doit choisir une colonne de tri, utilisez une liste blanche de noms connus et construisez la partie identifiant à partir de cette liste contrôlée ; ne placez pas directement un texte libre provenant de l'utilisateur dans la syntaxe SQL.

### 10.2 Paramètres et insertion

Le même principe vaut pour INSERT :

~~~python
# Exemple sqlite3 : chaque valeur est transmise séparément.
cursor.execute(
    "INSERT INTO produits (produit_id, nom, prix_catalogue) VALUES (?, ?, ?)",
    (34, product_name, product_price)
)
~~~

Cette méthode évite de placer la valeur directement dans la chaîne SQL. Elle améliore la sécurité, réduit les erreurs de guillemets et permet au pilote de transmettre les valeurs avec le type attendu. Le code doit toujours valider les règles métier : utiliser les paramètres ne garantit pas qu'un prix est positif ou que le produit est autorisé. La sécurité contre l'injection et la validation métier sont deux protections complémentaires.

Ne confondez pas paramétrage et chiffrement. Les paramètres protègent la séparation entre code et valeurs pour la requête ; ils ne remplacent ni le chiffrement du réseau, ni la gestion des secrets, ni les droits minimum, ni la politique de journalisation.

### 10.3 Quand une liste de valeurs est nécessaire

Certaines requêtes filtrent un ensemble de valeurs. Évitez de construire une liste de valeurs en concaténant arbitrairement les entrées d'une personne. La manière de lier une collection dépend de l'API du pilote ; certains permettent de développer une liste de paramètres, d'autres disposent de types tableaux ou d'autres mécanismes. L'implémentation doit suivre la documentation du driver et conserver des paramètres sûrs.

Pour une première pratique, utilisez une liste écrite explicitement dans la requête pédagogique, comme \`IN ('brouillon', 'confirmee')\`, et apprenez séparément comment votre pilote gère une liste fournie par l'application. Il est plus sûr de comprendre un mécanisme avant de créer soi-même une chaîne SQL dynamique.

## 11. SELECT et INSERT dans une application réelle

Dans un système réel, une requête est rarement seule. Une API reçoit une demande, authentifie l'utilisateur, vérifie l'autorisation, valide les paramètres, interroge la base, transforme le résultat en réponse et journalise ce qui est nécessaire. Chacune de ces étapes doit conserver une responsabilité claire.

Pour lire un produit, la requête SELECT peut être correcte et l'autorisation quand même insuffisante. Le fait que l'identifiant du produit soit connu n'autorise pas nécessairement l'accès à toutes ses données. Une application doit déterminer quelles colonnes peuvent être retournées au demandeur, quels filtres sont obligatoires et quelles données doivent rester internes.

Pour ajouter un produit, INSERT doit être précédé de contrôles adaptés à la fonctionnalité : nom non vide, prix au format attendu, compte autorisé à créer le produit et règles de visibilité. Les contraintes de la base protègent les invariants communs, tandis que l'application présente une explication utile en cas de rejet. Il ne faut pas dupliquer de façon contradictoire la logique partout, mais choisir où chaque règle doit être garantie.

La sécurité ne consiste pas seulement à empêcher une injection SQL. Le compte utilisé par l'application doit avoir le minimum de privilèges nécessaires. Un compte de lecture devrait disposer uniquement des droits de lecture requis. Une fonctionnalité de création n'a pas besoin d'un compte administrateur de base. Les erreurs techniques ne doivent pas révéler des secrets, et les paramètres sensibles ne doivent pas apparaître dans les logs.

Les journaux doivent être utiles sans devenir une nouvelle source de fuite. Il peut être important de consigner un horodatage, le type d'opération, un identifiant de corrélation et un état de succès ou d'échec. Il n'est pas nécessaire de consigner un mot de passe ou l'intégralité d'un enregistrement personnel pour prouver qu'une requête a été exécutée.

## 12. Vérifier une requête avant de la mettre à disposition

Une requête manuelle peut être acceptable pour une exploration, mais une requête qui alimente une API ou un rapport régulier doit être vérifiée de façon répétable. La vérification doit inclure le résultat, les limites, les erreurs et le périmètre des données.

Pour SELECT, écrivez d'abord le contrat de sortie : colonnes attendues, filtre, ordre et nombre de lignes éventuel. Créez un petit jeu de données synthétiques dont vous connaissez les résultats. Testez le cas normal, un cas sans résultat, une valeur frontière et un cas où une condition doit exclure une ligne. Si l'ordre compte, ajoutez ORDER BY et un critère de départage stable.

Pour INSERT, précisez les colonnes, vérifiez toutes les valeurs obligatoires et identifiez les contraintes susceptibles de rejeter l'opération. Testez une insertion valide, un doublon, une référence absente, une valeur hors limites et une donnée facultative manquante lorsque ce cas est permis. Vérifiez ensuite que les lignes sont bien présentes et que les compteurs ou identifiants produits sont cohérents.

La validation ne doit pas dépendre d'une capture d'écran isolée. Consignez la commande, l'environnement, les données de test, le résultat attendu et le résultat obtenu. Une personne différente doit pouvoir rejouer le test sur une base de laboratoire et arriver à la même conclusion dans le contexte documenté.

~~~mermaid
flowchart TD
    A["Définir le résultat attendu"] --> B["Créer un petit jeu de test"]
    B --> C["Tester le cas normal"]
    C --> D["Tester une frontière et un rejet"]
    D --> E["Comparer résultat observé et attendu"]
    E --> F{"Contrat respecté ?"}
    F -->|Oui| G["Documenter et versionner"]
    F -->|Non| H["Isoler la cause"]
    H --> B
~~~

## 13. Atelier pratique guidé : un catalogue de produits

L'atelier utilise la table \`produits\` suivante :

~~~sql
CREATE TABLE produits (
    produit_id INTEGER PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    prix_catalogue DECIMAL(10,2) NOT NULL CHECK (prix_catalogue >= 0)
);
~~~

Vérifiez la syntaxe sur le moteur choisi. La déclaration du type, la prise en charge de CHECK et les détails des identifiants peuvent différer. Pour éviter une confusion avec la génération automatique, nous saisissons explicitement les identifiants de laboratoire.

### Étape 1 — Ajouter le jeu initial

~~~sql
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES
    (101, 'Clavier', 25.00),
    (102, 'Souris', 12.50),
    (103, 'Écran', 149.90),
    (104, 'Adaptateur USB', 8.75),
    (105, 'Casque', 59.00);
~~~

Si le script est exécuté une deuxième fois sans réinitialiser les données, les clés primaires existantes peuvent être refusées. C'est un résultat normal. Ne supprimez pas les contraintes pour rendre le script réexécutable. Dans un cours de débutant, la procédure de remise à zéro doit être contrôlée et explicitement limitée à la base de laboratoire.

### Étape 2 — Lire toutes les lignes utiles

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
ORDER BY produit_id ASC;
~~~

Le résultat attendu comprend les cinq produits triés par identifiant croissant. Confirmez les colonnes, le nombre de lignes et les valeurs. Si le résultat ne contient que trois lignes, recherchez l'erreur de chargement ; ne supposez pas que la requête SELECT les a supprimées, puisqu'elle ne modifie pas la table.

### Étape 3 — Filtrer par prix

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
WHERE prix_catalogue < 30
ORDER BY prix_catalogue ASC, produit_id ASC;
~~~

Résultat attendu : Adaptateur USB, Souris et Clavier, dans l'ordre du prix croissant. Vérifiez que l'écran à 149,90 et le casque à 59,00 ne sont pas retournés. Un test doit vérifier les lignes attendues mais aussi s'assurer que des lignes qui ne correspondent pas n'apparaissent pas.

### Étape 4 — Rechercher un nom

~~~sql
SELECT produit_id, nom
FROM produits
WHERE nom LIKE '%USB%';
~~~

Le résultat attendu contient Adaptateur USB, sous réserve des règles de casse et de collation du moteur. Si la recherche doit être insensible à la casse, confirmez le comportement sur le SGBD choisi avant de déployer une solution.

### Étape 5 — Ajouter un nouveau produit

~~~sql
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES (106, 'Station d’accueil', 89.90);
~~~

Puis vérifiez l'insertion :

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
WHERE produit_id = 106;
~~~

Le contrôle consiste à confirmer qu'une seule ligne correspond à l'identifiant 106 et que ses colonnes contiennent les valeurs attendues. Le code de retour de l'INSERT et l'inspection de la ligne sont deux preuves complémentaires.

### Étape 6 — Provoquer des rejets contrôlés

Testez séparément ces cas dans le laboratoire :

~~~sql
-- Doit échouer : quantité ou prix négatif selon la règle CHECK
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES (107, 'Produit invalide', -1.00);

-- Doit échouer : clé primaire déjà utilisée si 106 existe.
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES (106, 'Identifiant dupliqué', 10.00);

-- Doit échouer : nom obligatoire absent.
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES (108, NULL, 12.00);
~~~

Le texte de commentaire indique ce qui est attendu dans ce schéma. Si le moteur accepte une valeur qui devrait être refusée, vérifiez que la bonne base a été utilisée et que la contrainte figure dans le schéma effectif. Certaines différences de moteur ou de mode de configuration peuvent expliquer un comportement divergent. L'objectif du test est de révéler un écart, pas de prétendre que le script est forcément correct.

N'exécutez pas tous les tests à l'aveugle dans une seule séquence si votre client SQL s'arrête au premier échec ou si les transactions sont laissées ouvertes après une erreur. Exécutez chaque test séparément et notez son résultat. Réinitialisez le laboratoire uniquement à l'aide d'une procédure connue. Sur une base réelle, toute insertion de test doit être autorisée et encadrée.

### Critères d'acceptation

Vous avez réussi si vous pouvez expliquer chaque clause, reproduire les cinq premières insertions, retrouver un produit par son identifiant, trier les prix, filtrer un sous-ensemble, ajouter une nouvelle ligne et démontrer les trois rejets prévus. Vous devez également expliquer les limites du test et indiquer quel moteur et quelle version ont été utilisés.

## 14. Bonnes pratiques de mise en forme SQL

La lisibilité est un élément de fiabilité. Une requête courte peut tenir sur une ligne, mais dès qu'elle possède plusieurs conditions, répartissez les clauses. Une clause WHERE isolée est plus facile à vérifier qu'un filtre noyé dans une ligne très longue. Les alias doivent être clairs et les noms doivent révéler le sens des champs.

~~~sql
SELECT
    produit_id,
    nom,
    prix_catalogue
FROM produits
WHERE prix_catalogue >= 10
  AND prix_catalogue < 100
ORDER BY prix_catalogue DESC, produit_id ASC
LIMIT 20;
~~~

Une convention courante met les mots-clés SQL en majuscules et les identifiants en minuscules. Ce choix est stylistique, mais la cohérence aide à lire le code. N'introduisez pas de guillemets autour des identifiants sans raison, car leur signification diffère selon le moteur. Évitez également les noms réservés comme nom de table ou colonne ; choisir un nom approprié réduit le besoin de contournements spécifiques.

Les commentaires doivent expliquer une décision non évidente, une restriction importante ou un risque. Un commentaire qui répète littéralement la requête ajoute peu de valeur. Au contraire, « le tri utilise produit_id comme critère de départage afin que le résultat paginé soit stable » explique une décision qui ne se déduit pas immédiatement du code.

Ne modifiez pas une requête correcte pour qu'elle soit simplement plus compacte. Le plus petit nombre de caractères n'est pas un objectif de qualité. Préférez une forme qui peut être vérifiée et discutée en revue de code, surtout pour les opérations qui alimentent un rapport ou une application.

## 15. Erreurs fréquentes et méthode de résolution

### Erreur : la table est introuvable

Vérifiez le nom exact, la base sélectionnée, le schéma logique si le moteur en utilise un, la casse et les droits. Une table peut exister dans une autre base ou un autre schéma. Ne créez pas une nouvelle table immédiatement : vous pourriez masquer une erreur de connexion ou travailler sur une structure qui n'est pas celle de l'application.

### Erreur : une colonne est ambiguë ou introuvable

Vérifiez les noms de colonnes et le contexte. Dans une requête simple avec une seule table, le problème est souvent une faute de frappe ou un schéma différent. Les requêtes multi-tables nécessitent parfois de préfixer les colonnes par un alias. Les jointures et leurs règles seront étudiées plus tard.

### Erreur : trop de lignes sont retournées

Vérifiez que le filtre WHERE est présent et que ses conditions expriment exactement la question. Regardez particulièrement les conditions combinant AND et OR. Utilisez des parenthèses pour rendre la logique explicite et contrôlez un petit ensemble d'exemples connus.

### Erreur : aucune ligne n'est retournée

Une requête peut réussir avec un résultat vide. Vérifiez la valeur recherchée, ses espaces, sa casse, les bornes, le type et le contexte. Confirmez que l'enregistrement existe dans la même base. Ne changez pas automatiquement l'opérateur ou ne retirez pas un filtre de sécurité pour obtenir une ligne.

### Erreur : INSERT est refusé

Identifiez la contrainte ou le type mentionné par le moteur. Vérifiez les colonnes obligatoires, les valeurs par défaut, les identifiants, les références et les droits. Évitez d'accorder tous les privilèges ou de désactiver les contraintes. Une insertion refusée peut indiquer que la base protège correctement la qualité des données.

### Erreur : les résultats changent d'ordre

Ajoutez ORDER BY et un critère de départage stable. L'ordre apparent du stockage physique n'est pas un contrat SQL. Si la requête limite les résultats ou alimente une pagination, un tri déterministe est particulièrement important.

### Erreur : le code semble fonctionner avec des valeurs simples mais échoue avec certains noms

Vérifiez les guillemets, les encodages et le paramétrage. Ne construisez pas le code SQL en concaténant des entrées externes. Utilisez les paramètres liés du pilote et testez des valeurs avec apostrophes, accents et caractères spéciaux dans l'environnement de test.

### Erreur : la commande a réussi mais le résultat n'est pas celui attendu

Un code de retour favorable indique que l'opération a été exécutée selon les règles du moteur ; il ne prouve pas que l'intention métier était correcte. Vérifiez le résultat de manière indépendante, comparez les préconditions et postconditions, puis ajoutez un test qui reproduira l'erreur. La correction se termine lorsque la cause est comprise et que la non-régression est prouvée.

## 16. Exercices avec corrigés détaillés

### Exercice 1 — Sélectionner les colonnes

Vous devez afficher uniquement le nom et le prix des produits. Écrivez une requête et expliquez pourquoi \`SELECT *\` est moins précis pour cette tâche.

**Corrigé :**

~~~sql
SELECT nom, prix_catalogue
FROM produits;
~~~

Les colonnes explicites représentent le contrat de sortie. Si une nouvelle colonne confidentielle ou simplement volumineuse est ajoutée à la table, elle ne sera pas automatiquement exposée par cette requête. Elle est également plus facile à relire et plus stable pour un appelant qui attend deux champs.

### Exercice 2 — Filtrer avec une borne incluse

Afficher les produits dont le prix est supérieur ou égal à 20.

**Corrigé :**

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
WHERE prix_catalogue >= 20
ORDER BY prix_catalogue ASC, produit_id ASC;
~~~

L'opérateur >= inclut la valeur 20. Le tri donne une sortie reproductible et le deuxième critère départage les produits ayant le même prix.

### Exercice 3 — Comprendre AND et OR

On veut voir les commandes du client 1 dont le statut est brouillon ou confirmée. Écrivez la condition sans ambiguïté.

**Corrigé :**

~~~sql
SELECT commande_id, statut
FROM commandes
WHERE client_id = 1
  AND (statut = 'brouillon' OR statut = 'confirmee')
ORDER BY commande_id ASC;
~~~

Les parenthèses font apparaître que les deux valeurs de statut sont évaluées pour le client 1 uniquement. Sans parenthèses, la priorité de AND et OR pourrait laisser passer toutes les commandes brouillon de tous les clients.

### Exercice 4 — Chercher l'absence d'information

Trouver les clients pour lesquels aucune adresse électronique n'est enregistrée, dans un schéma où email accepte NULL.

**Corrigé :**

~~~sql
SELECT client_id, nom
FROM clients
WHERE email IS NULL;
~~~

Il ne faut pas écrire email = NULL, car une comparaison SQL avec NULL produit un résultat inconnu plutôt qu'un vrai test d'absence. Vérifiez également que le modèle autorise vraiment NULL ; si email est NOT NULL, le résultat devrait être vide dans un état conforme.

### Exercice 5 — Trier et limiter

Afficher les cinq produits les plus chers en imposant un ordre stable.

**Corrigé :**

~~~sql
SELECT produit_id, nom, prix_catalogue
FROM produits
ORDER BY prix_catalogue DESC, produit_id ASC
LIMIT 5;
~~~

Le prix décroissant met les articles les plus chers en premier. L'identifiant croissant départage les produits au même prix. LIMIT limite le résultat ; il ne remplace ni le filtre ni le tri.

### Exercice 6 — Insérer une ligne

Ajouter un produit avec l'identifiant 150, le nom « Dock USB-C » et le prix 79,90.

**Corrigé :**

~~~sql
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES (150, 'Dock USB-C', 79.90);
~~~

Les colonnes sont explicites et les valeurs apparaissent dans le même ordre. L'insertion ne doit être exécutée que dans une base où l'identifiant 150 n'est pas déjà utilisé. Après l'opération, une requête SELECT ciblée doit confirmer l'état réel.

### Exercice 7 — Diagnostiquer une clé dupliquée

Le SGBD refuse l'insertion de l'identifiant 150. Quelles sont les premières vérifications utiles ?

**Corrigé :** vérifiez si un produit 150 existe déjà, si vous êtes connecté à la bonne base et si la stratégie d'identifiants est manuelle ou automatique. Ne supprimez pas l'ancien produit pour libérer l'identifiant sans comprendre ses dépendances. Si l'identifiant est généré par le SGBD, utilisez la méthode appropriée au moteur et au schéma plutôt que de gérer arbitrairement le compteur.

### Exercice 8 — Protéger une valeur utilisateur

Une application reçoit le nom du produit à rechercher. Pourquoi est-il dangereux de concaténer directement ce nom dans une chaîne SQL ?

**Corrigé :** les caractères fournis peuvent modifier la structure de la requête et provoquer une injection SQL. Utilisez les paramètres liés de la bibliothèque choisie. Les marqueurs varient selon les pilotes ; suivez leur documentation. La requête paramétrée protège la séparation code/données, mais la validation métier, les permissions minimales et les contrôles de sortie restent nécessaires.

### Exercice 9 — Insérer avec une contrainte

Le prix doit être positif ou nul. Le script accepte un prix négatif. Donnez une démarche de diagnostic sans désactiver le contrôle.

**Corrigé :** vérifiez la base visée, le schéma réel, la présence de CHECK, la version du moteur et sa configuration. Testez sur un environnement isolé une valeur négative et une valeur autorisée. Si la contrainte manque, corrigez le schéma et vérifiez les données existantes avant de déployer. Ne contournez pas le rejet en donnant au compte applicatif des droits supplémentaires.

### Exercice 10 — Une requête renvoie zéro ligne

Une recherche par nom ne renvoie rien, mais une personne pense que le produit existe. Que faut-il vérifier avant de retirer le filtre ?

**Corrigé :** vérifiez le nom réellement stocké, les espaces, les accents, la casse et la collation, la base ou le schéma utilisés, ainsi que la condition complète. Recherchez d'abord un cas discriminant et plus large dans un environnement autorisé. Ne retirez pas un filtre d'accès ou de sécurité simplement pour forcer un résultat.

### Exercice 11 — Valeurs multiples

Vous voulez ajouter trois produits avec un seul INSERT. Quelle forme pouvez-vous utiliser et quel contrôle reste indispensable ?

**Corrigé :**

~~~sql
INSERT INTO produits (produit_id, nom, prix_catalogue)
VALUES
    (151, 'Câble réseau', 4.50),
    (152, 'Adaptateur HDMI', 9.90),
    (153, 'Tapis souris', 6.25);
~~~

La forme multi-lignes est prise en charge par de nombreux moteurs, mais les limites et comportements doivent être vérifiés. Il faut s'assurer que les identifiants sont libres et que chaque ligne respecte les contraintes. Après l'exécution, confirmez le nombre et les valeurs enregistrées ; si le lot échoue, consultez les garanties du moteur avant de supposer que tout ou rien a été inséré.

### Exercice 12 — Concevoir un test de non-régression

Une requête de catalogue a été corrigée après avoir retourné trop de lignes. Que devrait contenir le test de non-régression ?

**Corrigé :** définissez un petit jeu synthétique avec des lignes qui doivent être incluses et exclues, précisez les colonnes et l'ordre attendus, vérifiez les bornes et les combinaisons AND/OR, puis comparez le résultat. Le test doit exposer le défaut d'origine et prouver qu'il ne revient pas. Conservez l'environnement, la version et les attentes, sans enregistrer de données sensibles.

## 17. Défi final corrigé — mini-catalogue de formation

### Mission

Construisez une table de formations avec un identifiant, un titre, un niveau et un statut de publication. Vous devez ajouter plusieurs formations fictives, afficher uniquement le titre et le niveau des formations publiées, rechercher les titres contenant « SQL », trier les formations par titre et limiter l'affichage à quelques lignes. Enfin, vous devez démontrer qu'un statut inconnu est refusé par le schéma et expliquer comment le code de l'application doit paramétrer une valeur de recherche.

### Étape A — Définir la structure et les règles

Les règles retenues pour ce défi sont : l'identifiant est unique ; le titre est obligatoire ; le niveau appartient à la liste débutant, intermédiaire ou expert ; le statut appartient à la liste brouillon, publié ou archivé. Cette liste d'états sert à illustrer une contrainte, et n'est pas une prescription pour chaque application de formation.

~~~mermaid
erDiagram
    FORMATIONS {
        int formation_id PK
        string titre
        string niveau
        string statut
    }
~~~

### Étape B — Créer la table

~~~sql
CREATE TABLE formations (
    formation_id INTEGER PRIMARY KEY,
    titre VARCHAR(160) NOT NULL,
    niveau VARCHAR(20) NOT NULL
        CHECK (niveau IN ('debutant', 'intermediaire', 'expert')),
    statut VARCHAR(20) NOT NULL
        CHECK (statut IN ('brouillon', 'publie', 'archive'))
);
~~~

Vérifiez la syntaxe et la prise en charge de CHECK dans le moteur choisi. Le schéma définit les valeurs admises mais ne gère pas un historique de publication. Si vous devez savoir qui a publié une formation et quand, il faudra ajouter des métadonnées et une stratégie d'audit.

### Étape C — Insérer un jeu fictif

~~~sql
INSERT INTO formations (formation_id, titre, niveau, statut)
VALUES
    (1, 'Bases relationnelles', 'debutant', 'publie'),
    (2, 'SQL : SELECT et INSERT', 'debutant', 'publie'),
    (3, 'Jointures SQL', 'debutant', 'brouillon'),
    (4, 'Optimisation SQL', 'intermediaire', 'archive'),
    (5, 'Architecture de données', 'expert', 'publie');
~~~

Cette instruction insère cinq lignes. Si elle est exécutée à nouveau, la clé primaire peut être dupliquée. Dans un exercice réinitialisable, définissez une procédure claire de remise à zéro. Ne réalisez pas cette réinitialisation sur des données réelles.

### Étape D — Afficher les formations publiées

~~~sql
SELECT formation_id, titre, niveau
FROM formations
WHERE statut = 'publie'
ORDER BY titre ASC, formation_id ASC
LIMIT 10;
~~~

Le résultat doit contenir les trois formations publiées, triées par titre. La limite 10 n'empêche pas le SGBD d'en retourner trois seulement. Si la table reçoit davantage de données, la requête continue à respecter le maximum prévu.

### Étape E — Rechercher les titres SQL

~~~sql
SELECT formation_id, titre, niveau
FROM formations
WHERE titre LIKE '%SQL%'
  AND statut = 'publie'
ORDER BY titre ASC, formation_id ASC;
~~~

Selon le moteur et sa collation, la casse du motif peut influer sur les résultats. Le test doit donc inclure la convention attendue, par exemple rechercher aussi les variantes de casse si c'est une exigence métier.

### Étape F — Tester la contrainte

~~~sql
-- Doit être rejeté, car « avance » ne figure pas dans les niveaux autorisés.
INSERT INTO formations (formation_id, titre, niveau, statut)
VALUES (6, 'Formation invalide', 'avance', 'publie');
~~~

Si l'opération est acceptée, examinez la définition effective de la table et la configuration du moteur. Le test ne doit pas être ignoré au motif que l'application affiche déjà une liste de choix. La contrainte du schéma et l'interface servent des objectifs complémentaires.

### Étape G — Corrigé de la conception et critères de réussite

La structure convient à un petit catalogue si les quatre attributs suffisent au besoin. L'identifiant est la clé primaire ; le titre et le niveau sont obligatoires ; le statut est limité à un vocabulaire contrôlé. La requête de lecture sélectionne uniquement les colonnes utiles et filtre les formations publiées. Le tri est explicite et stable. Le test négatif prouve que la contrainte de niveau est appliquée.

La solution n'est pas encore une plateforme de formation complète. Elle ne décrit ni les auteurs, ni les versions de cours, ni les inscriptions, ni les permissions, ni l'historique des changements de statut. Il ne faut pas ajouter ces éléments sans règle métier. Le bon modèle est celui qui couvre explicitement le besoin actuel et permet une évolution maîtrisée.

Le défi est terminé lorsque vous pouvez exécuter les opérations, expliquer leurs clauses, vérifier les résultats et montrer le rejet attendu. Une capture de l'écran ne suffit pas à elle seule : gardez les scripts, le moteur utilisé, les données de test et les observations.

## 18. Parcours pratique du débutant

Pour consolider les concepts, répartissez l'apprentissage en plusieurs petites séances.

**Séance 1 — Lire.** Prenez une table fictive et écrivez cinq SELECT dont le nombre de colonnes est de plus en plus précis. Avant chaque requête, écrivez en français les colonnes nécessaires et la table qui les contient. Comparez ensuite le résultat attendu et les colonnes effectivement retournées.

**Séance 2 — Filtrer.** Écrivez des filtres avec égalité, comparaison numérique, IN, BETWEEN et LIKE. Ajoutez ensuite des cas limites pour tester les bornes. Pour chaque condition, consignez un exemple qui doit être accepté et un exemple qui doit être exclu.

**Séance 3 — Trier et limiter.** Réalisez plusieurs tris sur une table contenant des valeurs répétées. Vérifiez comment un deuxième critère de tri départage les lignes. Comparez un résultat avec ORDER BY et un résultat sans ORDER BY sans considérer l'ordre accidentel comme une garantie.

**Séance 4 — Insérer.** Ajoutez des lignes avec des colonnes explicites. Testez un insert simple puis plusieurs lignes. Vérifiez les contraintes et notez les erreurs. Apprenez à identifier la cause du rejet sans supprimer les protections.

**Séance 5 — Paramétrer.** Écrivez un petit programme qui effectue une recherche avec un paramètre lié. Testez un texte qui comporte une apostrophe et des caractères spéciaux. Vérifiez que la donnée est traitée comme une valeur, non comme du code SQL.

**Séance 6 — Tester et documenter.** Créez un script reproductible, décrivez le jeu d'essai, notez le moteur et sa version, vérifiez le résultat attendu, et consignez les écarts. Une autre personne doit pouvoir reproduire votre test sans accès aux données de production.

Le but de ce parcours n'est pas d'atteindre une vitesse maximale de saisie. Le but est d'acquérir des réflexes : lire avant d'écrire, préciser les colonnes, comprendre les conditions, paramétrer les valeurs, tester les contraintes et vérifier les postconditions. Ces réflexes sont utiles pour toutes les requêtes futures.

## 19. Checklist de maîtrise

Avant de considérer le cours terminé, assurez-vous de pouvoir cocher chaque point sans consulter la solution :

- Je peux expliquer la différence entre une requête de lecture SELECT et une insertion INSERT.
- Je sais choisir explicitement les colonnes et expliquer pourquoi SELECT * n'est pas toujours souhaitable.
- Je sais écrire un filtre WHERE avec des comparaisons et vérifier les bornes.
- Je sais grouper des conditions avec AND, OR et des parenthèses.
- Je sais utiliser IN, BETWEEN et LIKE sur un petit jeu de données.
- Je sais pourquoi NULL se teste avec IS NULL et non avec = NULL.
- Je sais trier un résultat et rendre son ordre stable avec un critère de départage.
- Je sais limiter un résultat et expliquer pourquoi LIMIT sans ordre explicite peut être imprévisible.
- Je sais ajouter une ligne et plusieurs lignes en nommant les colonnes.
- Je comprends le rôle des valeurs par défaut, des identifiants générés et de NULL.
- Je sais expliquer les causes courantes de rejet d'un INSERT.
- Je sais utiliser les paramètres liés d'un pilote au lieu de concaténer les valeurs externes.
- Je sais écrire des tests négatifs qui prouvent que les contraintes fonctionnent.
- Je sais documenter le moteur, sa version, les attentes et les résultats observés.
- Je sais distinguer une requête techniquement réussie d'un résultat métier correct.

Si un point n'est pas maîtrisé, répétez l'exercice correspondant avec un jeu de données plus petit. Il est préférable d'expliquer correctement cinq lignes que de manipuler mille lignes sans comprendre les conditions.

## 20. Synthèse finale

SELECT décrit les colonnes à retourner et, avec FROM, la table d'où proviennent les lignes. WHERE limite le résultat aux lignes qui satisfont les conditions. AND, OR et les parenthèses expriment une logique. IN teste plusieurs valeurs ; BETWEEN représente une plage inclusive ; LIKE recherche un motif textuel ; IS NULL et IS NOT NULL testent l'absence. ORDER BY spécifie l'ordre, et LIMIT ou une syntaxe correspondante limite le nombre de lignes. Sans ordre explicite, la base ne promet pas un résultat trié.

INSERT ajoute une ligne ou plusieurs lignes. Il faut indiquer explicitement les colonnes et aligner les valeurs. Les colonnes omises doivent être permises par le schéma, parce qu'une valeur par défaut existe, que NULL est autorisé ou qu'une génération est définie. Les contraintes peuvent refuser un insert lorsque la clé est dupliquée, qu'une référence est absente, qu'une valeur obligatoire manque ou qu'une règle CHECK est violée.

Dans une application, les valeurs externes doivent être transmises avec les paramètres liés du pilote, pas concaténées dans le texte SQL. Le paramétrage évite l'injection dans les valeurs, mais ne remplace pas l'autorisation, la validation métier, les contraintes ou la gestion des secrets. Pour lire comme pour écrire, il faut vérifier le résultat réel, tester les limites et documenter les hypothèses.

Une requête peut être syntaxiquement correcte et répondre à la mauvaise question. La bonne pratique commence par un contrat clair, un jeu de test connu, des conditions relisibles et une vérification après exécution. Ces habitudes constituent la base du travail SQL professionnel.

## Références techniques

Les références ci-dessous permettent de vérifier le comportement et les différences entre les moteurs. Consultez la documentation correspondant à la version réellement installée avant de généraliser une syntaxe ou un comportement.

- PostgreSQL 18, SELECT : https://www.postgresql.org/docs/18/sql-select.html
- PostgreSQL 18, INSERT : https://www.postgresql.org/docs/18/sql-insert.html
- PostgreSQL 18, fonctions et opérateurs de comparaison : https://www.postgresql.org/docs/18/functions-comparison.html
- MySQL 8.4, SELECT : https://dev.mysql.com/doc/refman/8.4/en/select.html
- MySQL 8.4, INSERT : https://dev.mysql.com/doc/refman/8.4/en/insert.html
- SQLite, SELECT : https://www.sqlite.org/lang_select.html
- SQLite, INSERT : https://www.sqlite.org/lang_insert.html
- SQLite, paramètres des requêtes préparées : https://www.sqlite.org/c3ref/bind_blob.html

Une documentation officielle décrit ce que garantit le moteur ; elle ne définit pas les règles métier de votre application. Les décisions de filtrage, d'autorisation, de conservation et de vérification doivent rester explicites dans le projet.
