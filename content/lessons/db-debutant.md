# Bases de données relationnelles et langage SQL

## 1. Introduction aux bases de données

Une base de données permet de stocker, organiser, rechercher et modifier des informations de manière structurée.

On retrouve des bases de données dans presque tous les domaines informatiques :

- les applications Web ;
- les boutiques en ligne ;
- les banques ;
- les systèmes de gestion des utilisateurs ;
- les applications mobiles ;
- les systèmes de réservation ;
- les outils de gestion des stocks ;
- les plateformes de supervision ;
- les applications d'entreprise.

Une application Web, par exemple, peut utiliser une base de données pour mémoriser ses utilisateurs, leurs commandes, les produits disponibles et les paiements enregistrés.

### 1.1 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

- expliquer ce qu'est une base de données relationnelle ;
- distinguer une base de données, un serveur de bases de données et un langage SQL ;
- comprendre les tables, colonnes, lignes et relations ;
- installer et utiliser PostgreSQL sous Linux ;
- créer une base de données et des tables ;
- choisir des types de données adaptés ;
- comprendre les clés primaires et étrangères ;
- ajouter des contraintes d'intégrité ;
- insérer, lire, modifier et supprimer des données ;
- utiliser `SELECT`, `WHERE`, `ORDER BY` et `LIMIT` ;
- comprendre les valeurs `NULL` ;
- utiliser les fonctions d'agrégation et `GROUP BY` ;
- relier plusieurs tables avec `JOIN` ;
- effectuer des opérations simples à l'intérieur d'une transaction ;
- comprendre le rôle élémentaire des index ;
- créer un utilisateur de base de données avec des privilèges limités ;
- effectuer une sauvegarde et comprendre le principe de restauration ;
- diagnostiquer les erreurs SQL les plus fréquentes.

### 1.2 Prérequis

Vous devez connaître les bases de l'utilisation d'un ordinateur et d'un terminal.

Les notions suivantes sont utiles, mais elles seront réexpliquées lorsque nécessaire :

- fichiers et répertoires sous Linux ;
- commandes élémentaires du terminal ;
- droits administratifs avec `sudo` ;
- notions d'adresse IP, de port et de service ;
- fonctionnement général d'une application Web.

Aucune expérience préalable en programmation SQL n'est nécessaire.


## 2. Comprendre l'architecture d'une base de données

### 2.1 Qu'est-ce qu'une donnée ?

Une donnée est une information que l'on peut représenter et exploiter.

Exemples :

```text
Nom : Amina
Ville : Douala
Âge : 24
Prix : 15.50
Date : 2026-10-24
```

Ces valeurs n'ont pas toutes la même nature.

- `Amina` représente du texte.
- `Douala` représente du texte.
- `24` représente un nombre entier.
- `15.50` représente un nombre décimal.
- `2026-10-24` représente une date.

Une base de données peut stocker ces informations en leur associant des types et des règles.

### 2.2 Qu'est-ce qu'une base de données ?

Une base de données est un ensemble structuré d'informations persistantes.

Une base de données relationnelle organise généralement les informations dans des tables qui peuvent être reliées entre elles.

Exemple :

```text
BASE DE DONNÉES : boutique_sql
|
+-- clients
|
+-- produits
|
+-- commandes
|
+-- lignes_commande
```

Chaque table stocke un type d'information ou un ensemble d'informations ayant une structure définie.

### 2.3 Qu'est-ce qu'un SGBD ?

Un SGBD, ou système de gestion de base de données, est un logiciel qui permet de créer, stocker, interroger et administrer des bases de données.

Exemples :

- PostgreSQL ;
- MySQL ;
- MariaDB ;
- SQLite ;
- Microsoft SQL Server ;
- Oracle Database.

Le SGBD gère notamment les requêtes, les données, les contraintes, les droits d'accès et les mécanismes de transactions.

### 2.4 Qu'est-ce que SQL ?

SQL signifie *Structured Query Language*, ou langage de requête structuré.

SQL permet notamment de :

- créer des tables ;
- insérer des données ;
- rechercher des informations ;
- modifier des lignes ;
- supprimer des données ;
- définir des relations ;
- gérer des transactions ;
- accorder certains droits aux utilisateurs.

SQL est un langage déclaratif : on décrit généralement le résultat recherché plutôt que les étapes exactes que le moteur doit exécuter pour l'obtenir.

Exemple :

```sql
SELECT nom
FROM clients
WHERE ville = 'Douala';
```

Cette requête demande les noms des clients dont la ville est Douala.

Le moteur de base de données détermine comment exécuter cette demande.

### 2.5 Distinguer les composants

```text
+--------------------------------+
| Application                    |
| Site Web, script, logiciel     |
+---------------+----------------+
                |
                | Envoie une requête SQL
                v
+--------------------------------+
| SGBD                           |
| PostgreSQL, MySQL, etc.        |
+---------------+----------------+
                |
                | Lit ou modifie les données
                v
+--------------------------------+
| Stockage de la base de données |
| Tables, index, journaux        |
+--------------------------------+
```

SQL est le langage utilisé pour décrire les opérations. PostgreSQL ou MySQL est le logiciel qui les exécute.

### 2.6 Comparaison rapide des SGBD

| SGBD | Caractéristique générale | Utilisation courante |
|---|---|---|
| PostgreSQL | SGBD relationnel riche en fonctionnalités | Applications Web, systèmes d'entreprise, analyse |
| MySQL | SGBD relationnel largement utilisé dans le Web | Sites, applications et plateformes Web |
| MariaDB | SGBD relationnel issu de l'écosystème MySQL | Applications Web et systèmes d'entreprise |
| SQLite | Base embarquée généralement stockée dans un fichier | Applications locales, prototypes et petits outils |

Les quatre systèmes utilisent SQL, mais leurs syntaxes et leurs fonctionnalités ne sont pas strictement identiques.

**Dans ce cours, les exemples utilisent principalement PostgreSQL.** Les différences importantes avec MySQL et SQLite seront signalées.


## 3. Comprendre les tables relationnelles

### 3.1 Une table

Une table organise les données en colonnes et en lignes.

Exemple de table `clients` :

| id | nom | email | ville |
|---:|---|---|---|
| 1 | Amina Diallo | amina@example.test | Douala |
| 2 | Paul Martin | paul@example.test | Yaoundé |
| 3 | Sara Nguema | sara@example.test | Douala |

Une table possède généralement :

- un nom ;
- des colonnes ;
- des types de données ;
- des règles de validation ;
- des lignes contenant les valeurs.

### 3.2 Les colonnes

Une colonne définit un attribut d'une entité.

Dans la table `clients` :

```text
id      -> identifiant du client
nom     -> nom du client
email   -> adresse électronique
ville   -> ville de résidence
```

Chaque colonne possède un type de données adapté à l'information qu'elle doit contenir.

### 3.3 Les lignes

Une ligne représente un enregistrement.

Dans la table `clients`, une ligne correspond à un client.

```text
id | nom          | email
---+--------------+-----------------------
1  | Amina Diallo | amina@example.test
2  | Paul Martin  | paul@example.test
3  | Sara Nguema  | sara@example.test
```

Chaque ligne peut être identifiée par une clé primaire.

### 3.4 Le schéma d'une table

Le schéma décrit la structure de la table.

Par exemple :

```text
Table : clients

id             BIGINT
nom            VARCHAR(100)
email          VARCHAR(255)
ville          VARCHAR(100)
date_creation  TIMESTAMPTZ
```

Le schéma définit la structure attendue. Les lignes contiennent les données réelles.

### 3.5 Pourquoi ne pas tout stocker dans une seule table ?

Imaginez une boutique qui stocke tous les clients, produits, commandes et détails des commandes dans une seule grande table.

```text
nom_client | email | produit | prix | date_commande
```

Cette organisation devient problématique lorsque :

- un client passe plusieurs commandes ;
- une commande contient plusieurs produits ;
- un produit apparaît dans plusieurs commandes ;
- l'adresse électronique d'un client change ;
- le prix actuel d'un produit évolue.

La duplication des données risque de provoquer des incohérences.

Les bases relationnelles permettent de répartir ces informations dans plusieurs tables, puis de les relier avec des clés.


## 4. Comprendre les relations entre les tables

Nous utiliserons une boutique en ligne comme fil conducteur.

Son modèle comprend quatre tables :

- `clients` ;
- `produits` ;
- `commandes` ;
- `lignes_commande`.

### 4.1 Diagramme relationnel

```text
+---------------------+
| CLIENTS             |
+---------------------+
| id (PK)             |
| nom                 |
| email               |
| ville               |
+----------+----------+
           |
           | Un client peut passer plusieurs commandes
           |
           v
+---------------------+
| COMMANDES           |
+---------------------+
| id (PK)             |
| client_id (FK)      |
| date_commande       |
| statut              |
+----------+----------+
           |
           | Une commande possède plusieurs lignes
           |
           v
+---------------------+
| LIGNES_COMMANDE     |
+---------------------+
| id (PK)             |
| commande_id (FK)    |
| produit_id (FK)     |
| quantite            |
| prix_unitaire       |
+----------+----------+
           |
           | Chaque ligne référence un produit
           |
           v
+---------------------+
| PRODUITS            |
+---------------------+
| id (PK)             |
| nom                 |
| prix                |
| stock               |
+---------------------+
```

`PK` signifie *Primary Key*, ou clé primaire.

`FK` signifie *Foreign Key*, ou clé étrangère.

### 4.2 Relation un-à-plusieurs

Un client peut passer plusieurs commandes, mais chaque commande appartient ici à un seul client.

```text
CLIENT 1
   |
   +---- COMMANDE 1
   |
   +---- COMMANDE 2
   |
   +---- COMMANDE 3
```

Cette relation est dite un-à-plusieurs.

Elle est représentée par une clé étrangère dans la table `commandes`.

### 4.3 Relation plusieurs-à-plusieurs

Une commande peut contenir plusieurs produits et un produit peut apparaître dans plusieurs commandes.

```text
COMMANDE A -------- PRODUIT X
     |                  |
     |                  |
     +-------------- PRODUIT Y
                        |
COMMANDE B -------------+
```

Pour représenter cette relation, on utilise une table intermédiaire : `lignes_commande`.

Cette table contient notamment :

- l'identifiant de la commande ;
- l'identifiant du produit ;
- la quantité commandée ;
- le prix unitaire appliqué lors de la commande.

Le prix historique est important : si le prix actuel du produit change, il faut pouvoir conserver le prix utilisé pour une commande déjà passée.

### 4.4 Pourquoi les relations sont-elles utiles ?

Les relations permettent de :

- réduire les duplications inutiles ;
- conserver la cohérence des informations ;
- représenter les règles métier ;
- relier plusieurs tables dans une requête ;
- empêcher certaines données orphelines.

Elles constituent une caractéristique centrale des bases de données relationnelles.


## 5. Préparer l'environnement PostgreSQL

### 5.1 Installer PostgreSQL sous Debian ou Ubuntu

Dans un environnement de formation :

```bash
sudo apt update
sudo apt install postgresql postgresql-client
```

Le premier paquet fournit le serveur PostgreSQL et le second les outils clients.

Vérifiez le service :

```bash
sudo systemctl status postgresql
```

Démarrez-le et activez son lancement automatique si nécessaire :

```bash
sudo systemctl enable --now postgresql
```

Vérifiez la version du client :

```bash
psql --version
```

La version du client peut différer de celle du serveur. Pour connaître les versions installées et les instances actives, consultez les outils de la distribution.

### 5.2 Se connecter à PostgreSQL

Sur une installation Debian ou Ubuntu courante, le compte système `postgres` est généralement associé à l'administration initiale de PostgreSQL.

La commande suivante permet d'ouvrir une session SQL avec le rôle de base de données `postgres` :

```bash
sudo -u postgres psql
```

Vous devriez obtenir une invite similaire à :

```text
postgres=#
```

Le format exact de l'invite peut varier.

Pour quitter `psql` :

```text
\q
```

La commande `\q` est une commande du client `psql`, pas une instruction SQL standard.

### 5.3 Distinguer le compte système et le rôle SQL

Il faut distinguer deux notions :

- un compte système Linux, qui permet notamment de lancer des processus ;
- un rôle PostgreSQL, qui définit une identité dans le SGBD.

La commande :

```bash
sudo -u postgres psql
```

utilise le compte système `postgres` pour exécuter le client `psql`. Selon la configuration locale, l'authentification PostgreSQL utilise ensuite un mécanisme tel que l'authentification locale par pair.

Un rôle SQL n'est pas automatiquement un compte Linux et inversement.

### 5.4 Commandes utiles de `psql`

Dans le client PostgreSQL :

```text
\l
```

Affiche les bases de données accessibles au rôle connecté.

```text
\du
```

Affiche les rôles PostgreSQL.

```text
\dt
```

Affiche les tables visibles dans le schéma courant.

```text
\d clients
```

Affiche la structure d'une table appelée `clients`.

```text
\conninfo
```

Affiche des informations relatives à la connexion actuelle.

```text
\q
```

Quitte le client.

Ces commandes sont spécifiques à `psql`. Elles ne doivent pas être envoyées telles quelles depuis un client SQL qui ne les prend pas en charge.


## 6. Créer une base de données de formation

Nous allons utiliser une base de données nommée `boutique_sql`.

Depuis la session d'administration PostgreSQL :

```sql
CREATE DATABASE boutique_sql;
```

Puis quittez le client :

```text
\q
```

Reconnectez-vous à la nouvelle base :

```bash
sudo -u postgres psql -d boutique_sql
```

Vous pouvez maintenant exécuter les instructions SQL de la suite du cours dans cette base.

### 6.1 Vérifier la connexion

```sql
SELECT current_database();
```

Cette requête renvoie le nom de la base de données courante.

Pour connaître le rôle connecté :

```sql
SELECT current_user;
```

Ces requêtes utilisent des fonctions intégrées à PostgreSQL.

### 6.2 Attention aux bases de production

Les manipulations de ce cours doivent se faire dans une base de formation.

Ne créez pas, ne supprimez pas et ne modifiez pas de tables de production sans comprendre l'effet de l'opération, les droits requis, la stratégie de sauvegarde et les conséquences pour l'application.


## 7. Les grandes catégories d'instructions SQL

SQL comprend plusieurs catégories d'instructions.

### 7.1 DDL — Définition des structures

DDL signifie *Data Definition Language*.

Ces instructions définissent ou modifient les structures de la base.

| Instruction | Rôle |
|---|---|
| `CREATE` | Créer un objet |
| `ALTER` | Modifier la structure d'un objet |
| `DROP` | Supprimer un objet |

Exemples :

```sql
CREATE TABLE exemple (
    id INTEGER PRIMARY KEY,
    nom VARCHAR(100)
);
```

```sql
ALTER TABLE exemple
ADD COLUMN ville VARCHAR(100);
```

`DROP TABLE` supprime une table et sa structure. Cette opération doit être utilisée avec prudence.

### 7.2 DML — Manipulation des données

DML signifie *Data Manipulation Language*.

Les instructions courantes comprennent :

| Instruction | Rôle |
|---|---|
| `INSERT` | Ajouter des lignes |
| `UPDATE` | Modifier des lignes |
| `DELETE` | Supprimer des lignes |

Exemple :

```sql
INSERT INTO exemple (id, nom)
VALUES (1, 'Amina');
```

### 7.3 Requêtes de lecture

L'instruction `SELECT` permet de lire et d'analyser des données.

```sql
SELECT nom
FROM exemple;
```

Elle permet aussi d'effectuer des calculs, des regroupements et des jointures.

### 7.4 TCL — Contrôle des transactions

TCL signifie *Transaction Control Language*.

Les instructions courantes sont :

- `BEGIN` ;
- `COMMIT` ;
- `ROLLBACK` ;
- `SAVEPOINT`.

Elles permettent de gérer un ensemble d'opérations qui doivent être validées ou annulées ensemble.

### 7.5 DCL — Contrôle des privilèges

DCL signifie *Data Control Language* dans les classifications pédagogiques courantes.

Exemples :

- `GRANT` : accorder des privilèges ;
- `REVOKE` : retirer des privilèges.

La sécurité des bases dépend aussi de la configuration du serveur, de l'authentification, du réseau et de la gestion des secrets.


## 8. Créer les tables

Nous allons définir les quatre tables du modèle de boutique.

### 8.1 Table `clients`

```sql
CREATE TABLE clients (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    ville VARCHAR(100),
    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### Explication

`BIGINT` représente un entier de grande capacité.

`GENERATED BY DEFAULT AS IDENTITY` demande à PostgreSQL de générer automatiquement une valeur lorsqu'aucun identifiant n'est fourni.

`PRIMARY KEY` définit la clé primaire de la table.

`VARCHAR(100)` définit une chaîne de texte dont la longueur maximale déclarée est de 100 caractères.

`NOT NULL` interdit à la colonne de contenir la valeur SQL `NULL`.

`UNIQUE` empêche plusieurs lignes d'avoir la même valeur dans cette colonne, dans les conditions applicables aux valeurs non nulles.

`TIMESTAMPTZ` représente une date et une heure avec gestion du contexte de fuseau horaire selon le fonctionnement de PostgreSQL.

`DEFAULT CURRENT_TIMESTAMP` fournit une valeur par défaut lorsque la colonne n'est pas renseignée lors de l'insertion.

### 8.2 Table `produits`

```sql
CREATE TABLE produits (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    prix NUMERIC(10, 2) NOT NULL CHECK (prix >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    actif BOOLEAN NOT NULL DEFAULT TRUE
);
```

`NUMERIC(10, 2)` permet de stocker un nombre décimal avec une précision définie, adaptée ici à des montants.

Pour les montants financiers, un type décimal exact comme `NUMERIC` est généralement préférable à un type à virgule flottante.

`CHECK (prix >= 0)` interdit les prix négatifs.

`DEFAULT 0` définit une valeur par défaut si aucun stock n'est fourni.

`BOOLEAN` représente une valeur logique, habituellement `TRUE` ou `FALSE`.

### 8.3 Table `commandes`

```sql
CREATE TABLE commandes (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    client_id BIGINT NOT NULL REFERENCES clients(id),
    date_commande TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(20) NOT NULL
        CHECK (statut IN (
            'en_attente',
            'payee',
            'expediee',
            'annulee'
        ))
);
```

La colonne `client_id` est une clé étrangère vers `clients(id)`.

Cette relation interdit normalement d'enregistrer une commande qui référence un client inexistant.

La contrainte `CHECK` limite les valeurs autorisées pour le statut.

### 8.4 Table `lignes_commande`

```sql
CREATE TABLE lignes_commande (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    commande_id BIGINT NOT NULL
        REFERENCES commandes(id) ON DELETE CASCADE,
    produit_id BIGINT NOT NULL
        REFERENCES produits(id),
    quantite INTEGER NOT NULL CHECK (quantite > 0),
    prix_unitaire NUMERIC(10, 2) NOT NULL
        CHECK (prix_unitaire >= 0),
    UNIQUE (commande_id, produit_id)
);
```

Cette table relie les commandes aux produits.

`quantite` doit être strictement positive.

`prix_unitaire` conserve le prix utilisé pour cette ligne de commande. Il ne dépend pas automatiquement du prix actuel enregistré dans `produits`.

La contrainte `UNIQUE (commande_id, produit_id)` interdit deux lignes distinctes portant la même paire commande-produit. Si l'application doit autoriser plusieurs lignes pour un même produit dans une commande, cette règle devra être adaptée.

`ON DELETE CASCADE` signifie que la suppression d'une commande supprime également les lignes qui lui sont associées. Cette règle est une décision de conception et doit être choisie consciemment.

### 8.5 Comprendre les relations finales

```text
clients
  |
  | id
  |<---------------- client_id
  |
commandes
  |
  | id
  |<---------------- commande_id
  |
lignes_commande
  |
  | produit_id
  v
produits
```

Les clés étrangères assurent la cohérence des références entre les tables.

### 8.6 Vérifier les tables

Dans `psql` :

```text
\dt
```

Puis :

```text
\d clients
\d produits
\d commandes
\d lignes_commande
```

Vous pouvez aussi utiliser les vues du catalogue PostgreSQL pour examiner les informations sur les tables.


## 9. Les types de données importants

Le choix du type d'une colonne influence sa validité, son stockage et les opérations autorisées.

| Type PostgreSQL | Utilisation habituelle |
|---|---|
| `SMALLINT` | Petit entier |
| `INTEGER` | Entier courant |
| `BIGINT` | Entier de grande capacité |
| `NUMERIC(p, s)` | Nombre décimal avec précision définie |
| `REAL` | Nombre à virgule flottante de précision limitée |
| `DOUBLE PRECISION` | Nombre à virgule flottante de précision supérieure à `REAL` |
| `VARCHAR(n)` | Texte de longueur maximale déclarée |
| `TEXT` | Texte sans longueur maximale déclarée dans le type |
| `BOOLEAN` | Valeur logique |
| `DATE` | Date |
| `TIME` | Heure |
| `TIMESTAMP` | Date et heure sans fuseau horaire |
| `TIMESTAMPTZ` | Date et heure avec sémantique de fuseau horaire |
| `UUID` | Identifiant universel |
| `JSONB` | Données JSON stockées sous une forme binaire optimisée par PostgreSQL |

### 9.1 Entiers

Utilisez un type entier lorsque la valeur doit représenter un nombre sans partie décimale.

Exemples :

- un nombre de commandes ;
- un stock d'articles entiers ;
- un identifiant interne.

Un identifiant ne doit pas être confondu avec une valeur métier qui pourrait avoir des zéros initiaux.

Par exemple, un code postal ou un numéro de téléphone est généralement représenté sous forme de texte, car les opérations arithmétiques ne constituent pas son objectif principal.

### 9.2 Nombres décimaux

Pour un prix :

```sql
prix NUMERIC(10, 2)
```

Cette définition convient à de nombreux montants exprimés avec deux décimales.

Le choix de la précision doit correspondre aux besoins de l'application, aux règles métier et à la devise considérée.

### 9.3 Texte

Pour stocker un nom :

```sql
nom VARCHAR(100) NOT NULL
```

Pour un texte long :

```sql
description TEXT
```

Dans PostgreSQL, `TEXT` est un type courant pour les textes de longueur variable.

### 9.4 Dates et heures

Une date sans heure :

```sql
date_naissance DATE
```

Une date et une heure :

```sql
date_creation TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
```

Lorsqu'une application fonctionne sur plusieurs fuseaux horaires, le choix du type et les règles de conversion doivent être cohérents.

Il est souvent préférable d'enregistrer des instants avec une sémantique de fuseau horaire, puis de gérer leur présentation selon la zone souhaitée.

### 9.5 Différences avec MySQL et SQLite

Les types et les fonctions ne sont pas strictement identiques selon les SGBD.

Par exemple :

- PostgreSQL utilise fréquemment `GENERATED ... AS IDENTITY` pour les identifiants générés ;
- MySQL utilise couramment `AUTO_INCREMENT` ;
- SQLite utilise souvent `INTEGER PRIMARY KEY` pour un identifiant correspondant au mécanisme de rowid ;
- PostgreSQL propose un type `BOOLEAN` natif ;
- SQLite possède un modèle de typage différent, même si les colonnes peuvent être déclarées avec des types familiers.

Ne supposez pas que tous les scripts SQL peuvent être exécutés sans modification sur tous les SGBD.


## 10. Insérer les premières données avec INSERT

### 10.1 Insérer un client

```sql
INSERT INTO clients (nom, email, ville)
VALUES ('Amina Diallo', 'amina@example.test', 'Douala');
```

Les colonnes sont indiquées explicitement dans la liste après le nom de la table.

La valeur de `id` est générée automatiquement.

### 10.2 Insérer plusieurs clients

```sql
INSERT INTO clients (nom, email, ville)
VALUES
    ('Paul Martin', 'paul@example.test', 'Yaoundé'),
    ('Sara Nguema', 'sara@example.test', 'Douala');
```

Une seule instruction peut insérer plusieurs lignes.

### 10.3 Insérer des produits

```sql
INSERT INTO produits (nom, prix, stock, actif)
VALUES
    ('Clavier USB', 15.00, 40, TRUE),
    ('Souris sans fil', 25.50, 30, TRUE),
    ('Écran 24 pouces', 149.90, 12, TRUE),
    ('Câble HDMI', 9.99, 60, TRUE),
    ('Casque audio', 45.00, 20, TRUE);
```

### 10.4 Obtenir un identifiant généré

PostgreSQL permet de récupérer l'identifiant créé grâce à `RETURNING`.

```sql
INSERT INTO clients (nom, email, ville)
VALUES ('Nora Essomba', 'nora@example.test', 'Garoua')
RETURNING id;
```

Cette méthode est préférable à l'hypothèse qu'un nouvel identifiant aura toujours une valeur précise.

### 10.5 Pourquoi nommer les colonnes ?

Cette écriture :

```sql
INSERT INTO clients (nom, email, ville)
VALUES ('Amina Diallo', 'amina@example.test', 'Douala');
```

est préférable à une insertion où l'on dépend de l'ordre de toutes les colonnes.

Elle rend la requête plus lisible et plus résistante à certaines évolutions du schéma.

### 10.6 Les erreurs fréquentes

Cette insertion est incorrecte :

```sql
INSERT INTO clients (nom, email)
VALUES ('Amina Diallo');
```

Le nombre de valeurs ne correspond pas au nombre de colonnes indiqué.

Cette insertion est également incorrecte si un autre client possède déjà le même email :

```sql
INSERT INTO clients (nom, email, ville)
VALUES ('Autre Client', 'amina@example.test', 'Limbé');
```

La contrainte `UNIQUE` empêche la duplication de l'adresse électronique.


## 11. Lire les données avec SELECT

### 11.1 Lire toutes les colonnes

```sql
SELECT *
FROM clients;
```

`*` signifie toutes les colonnes de la table.

C'est utile pour explorer une petite table de formation, mais il est souvent préférable de nommer explicitement les colonnes dans les requêtes applicatives.

### 11.2 Sélectionner certaines colonnes

```sql
SELECT nom, email
FROM clients;
```

Le résultat ne contient que les colonnes demandées.

### 11.3 Renommer une colonne dans le résultat

```sql
SELECT
    nom AS nom_client,
    email AS adresse_email
FROM clients;
```

`AS` permet de donner un alias à une colonne ou à une expression.

L'alias ne modifie pas le nom réel de la colonne dans la table.

### 11.4 Créer une expression calculée

```sql
SELECT
    nom,
    prix,
    prix * 1.10 AS prix_avec_majoration
FROM produits;
```

Le résultat contient une nouvelle valeur calculée à partir de `prix`.

Cette expression n'enregistre pas un nouveau prix dans la table.

### 11.5 Éviter les résultats inutiles

Si vous n'avez besoin que du nom et du prix des produits :

```sql
SELECT nom, prix
FROM produits;
```

il n'est pas nécessaire de demander toutes les colonnes avec `SELECT *`.

Cela améliore la lisibilité et peut réduire la quantité de données transférées vers l'application.


## 12. Filtrer les données avec WHERE

La clause `WHERE` limite les lignes qui correspondent à une condition.

### 12.1 Égalité

```sql
SELECT *
FROM clients
WHERE ville = 'Douala';
```

Seuls les clients dont la ville correspond à la valeur recherchée sont renvoyés.

### 12.2 Comparaisons numériques

```sql
SELECT nom, prix
FROM produits
WHERE prix > 30;
```

Les opérateurs courants sont :

| Opérateur | Signification |
|---|---|
| `=` | Égal à |
| `<>` | Différent de |
| `!=` | Différent de, pris en charge par plusieurs SGBD |
| `>` | Supérieur à |
| `<` | Inférieur à |
| `>=` | Supérieur ou égal |
| `<=` | Inférieur ou égal |

Pour les exercices du cours, préférez `<>` pour exprimer une différence dans un SQL largement portable.

### 12.3 Combiner plusieurs conditions avec AND

```sql
SELECT nom, prix, stock
FROM produits
WHERE prix < 100
  AND stock > 0;
```

La ligne doit satisfaire les deux conditions.

### 12.4 Combiner des conditions avec OR

```sql
SELECT nom, prix
FROM produits
WHERE prix < 10
   OR prix > 100;
```

Une ligne est retenue lorsque l'une des conditions est vraie.

### 12.5 Utiliser les parenthèses

```sql
SELECT *
FROM produits
WHERE (prix < 20 OR prix > 100)
  AND actif = TRUE;
```

Les parenthèses rendent explicite le regroupement des conditions.

Elles évitent les erreurs d'interprétation lorsque `AND` et `OR` sont combinés.

### 12.6 Rechercher une valeur parmi plusieurs

```sql
SELECT *
FROM clients
WHERE ville IN ('Douala', 'Yaoundé');
```

`IN` est pratique pour rechercher plusieurs valeurs possibles d'une même colonne.

### 12.7 Rechercher une plage

```sql
SELECT nom, prix
FROM produits
WHERE prix BETWEEN 10 AND 50;
```

`BETWEEN` inclut les deux bornes.

Dans cet exemple, un prix de 10 ou de 50 satisfait la condition.

### 12.8 Rechercher un texte avec LIKE

```sql
SELECT *
FROM clients
WHERE nom LIKE 'A%';
```

Dans PostgreSQL, `%` représente une suite de zéro ou plusieurs caractères.

`_` représente un seul caractère.

Exemple :

```sql
SELECT *
FROM produits
WHERE nom LIKE '%USB%';
```

Cette recherche sélectionne les noms qui contiennent le texte `USB`, avec une sensibilité à la casse dans le comportement habituel de `LIKE`.

PostgreSQL propose également `ILIKE` pour les recherches textuelles sans distinction de casse.

```sql
SELECT *
FROM produits
WHERE nom ILIKE '%usb%';
```

`ILIKE` est spécifique à PostgreSQL et n'est pas une construction SQL universelle.


## 13. Trier et limiter les résultats

### 13.1 Trier avec ORDER BY

```sql
SELECT nom, prix
FROM produits
ORDER BY prix ASC;
```

`ASC` signifie ordre croissant.

Pour un ordre décroissant :

```sql
SELECT nom, prix
FROM produits
ORDER BY prix DESC;
```

### 13.2 Trier avec plusieurs critères

```sql
SELECT nom, ville
FROM clients
ORDER BY ville ASC, nom ASC;
```

Le résultat est d'abord trié par ville, puis par nom pour les lignes ayant la même ville.

### 13.3 Limiter le nombre de lignes

```sql
SELECT *
FROM produits
ORDER BY prix DESC
LIMIT 3;
```

Cette requête renvoie au maximum trois lignes.

Le tri est important si vous souhaitez obtenir les trois produits les plus chers. Sans `ORDER BY`, l'ordre des lignes n'est pas garanti.

### 13.4 Paginer les résultats

```sql
SELECT id, nom, email
FROM clients
ORDER BY id
LIMIT 10 OFFSET 20;
```

Cette requête ignore les vingt premières lignes du résultat trié et renvoie les dix suivantes au maximum.

`OFFSET` peut devenir coûteux lorsque la position demandée est très élevée. Pour de grandes tables, une pagination fondée sur une clé stable peut être plus efficace.


## 14. Comprendre NULL

`NULL` représente une valeur absente, inconnue ou non renseignée selon le contexte.

Il ne signifie pas :

- le nombre zéro ;
- une chaîne vide ;
- la valeur booléenne `FALSE`.

### 14.1 Rechercher les valeurs absentes

Incorrect :

```sql
SELECT *
FROM clients
WHERE ville = NULL;
```

Correct :

```sql
SELECT *
FROM clients
WHERE ville IS NULL;
```

Pour rechercher les valeurs présentes :

```sql
SELECT *
FROM clients
WHERE ville IS NOT NULL;
```

### 14.2 Pourquoi l'égalité ne fonctionne-t-elle pas normalement avec NULL ?

SQL utilise une logique qui tient compte d'une valeur inconnue.

Une comparaison comme :

```sql
ville = NULL
```

ne produit pas une vérité ordinaire utilisable comme condition vraie. Il faut utiliser `IS NULL` ou `IS NOT NULL`.

### 14.3 Combiner NULL et les conditions

Une condition qui dépend d'une valeur absente peut produire un résultat inconnu.

C'est pourquoi il faut examiner explicitement les valeurs nulles lorsque le comportement attendu en dépend.

### 14.4 COALESCE

La fonction `COALESCE` renvoie la première expression non nulle.

```sql
SELECT
    nom,
    COALESCE(ville, 'Ville inconnue') AS ville_affichee
FROM clients;
```

Cette fonction permet de fournir une valeur de remplacement dans le résultat.

Elle ne modifie pas la valeur enregistrée dans la table.


## 15. Modifier les données avec UPDATE

La commande `UPDATE` permet de modifier des lignes existantes.

### 15.1 Modifier un prix

```sql
UPDATE produits
SET prix = 17.50
WHERE nom = 'Clavier USB';
```

Cette instruction modifie le prix du produit dont le nom correspond à la condition.

### 15.2 Modifier plusieurs colonnes

```sql
UPDATE produits
SET prix = 27.00,
    stock = 25
WHERE nom = 'Souris sans fil';
```

Plusieurs colonnes peuvent être mises à jour dans la même instruction.

### 15.3 Le danger d'un UPDATE sans WHERE

Cette instruction :

```sql
UPDATE produits
SET prix = 0;
```

modifie le prix de toutes les lignes de la table.

Il ne faut l'exécuter que lorsque ce comportement est réellement souhaité et qu'il a été vérifié.

Avant un changement important, examinez les lignes concernées.

```sql
SELECT id, nom, prix
FROM produits
WHERE nom = 'Clavier USB';
```

Vous pouvez ensuite appliquer la modification et contrôler le résultat.

### 15.4 Mise à jour calculée

```sql
UPDATE produits
SET prix = prix * 1.05
WHERE actif = TRUE;
```

Cette instruction augmente les prix de 5 % pour tous les produits actifs.

Elle est présentée comme un exemple pédagogique. Ne l'exécutez pas dans une base réelle sans vérifier que vous voulez réellement appliquer cette modification à toutes les lignes concernées.


## 16. Supprimer des données avec DELETE

### 16.1 Supprimer une ligne déterminée

```sql
DELETE FROM clients
WHERE email = 'nora@example.test';
```

Cette instruction supprime les lignes qui correspondent à la condition.

Si une clé étrangère interdit la suppression d'un client encore référencé par des commandes, la suppression échouera tant que ces dépendances ne sont pas traitées.

### 16.2 Vérifier avant de supprimer

Avant un `DELETE`, exécutez une requête de lecture utilisant la même condition :

```sql
SELECT *
FROM clients
WHERE email = 'nora@example.test';
```

Vérifiez que les lignes affichées sont bien celles qui doivent être supprimées.

### 16.3 Le danger de DELETE sans WHERE

```sql
DELETE FROM produits;
```

Cette instruction supprime toutes les lignes de la table `produits`.

La structure de la table reste présente, mais ses données sont supprimées.

Une suppression en masse doit être considérée comme une opération à risque. Les droits, la transaction, les sauvegardes et les conséquences sur les tables liées doivent être compris.

### 16.4 DROP TABLE n'est pas DELETE

`DELETE` supprime des lignes.

`DROP TABLE` supprime la table elle-même et sa définition.

```sql
DROP TABLE exemple;
```

Cette instruction est dangereuse si la table contient des données utiles. Elle est présentée uniquement pour comprendre la différence.


## 17. Agrégations et statistiques

Les fonctions d'agrégation calculent un résultat à partir de plusieurs lignes.

| Fonction | Rôle |
|---|---|
| `COUNT` | Compter les lignes ou valeurs non nulles |
| `SUM` | Additionner des valeurs |
| `AVG` | Calculer une moyenne |
| `MIN` | Trouver la valeur minimale |
| `MAX` | Trouver la valeur maximale |

### 17.1 Compter les clients

```sql
SELECT COUNT(*) AS nombre_clients
FROM clients;
```

`COUNT(*)` compte les lignes retournées par la table ou le groupe.

### 17.2 Compter les produits actifs

```sql
SELECT COUNT(*) AS nombre_produits_actifs
FROM produits
WHERE actif = TRUE;
```

### 17.3 Calculer le prix moyen

```sql
SELECT AVG(prix) AS prix_moyen
FROM produits
WHERE actif = TRUE;
```

### 17.4 Trouver le prix minimum et maximum

```sql
SELECT
    MIN(prix) AS prix_minimum,
    MAX(prix) AS prix_maximum
FROM produits;
```

### 17.5 Additionner les quantités disponibles

```sql
SELECT SUM(stock) AS stock_total
FROM produits;
```

`SUM` ignore les valeurs nulles. Dans notre table, la colonne `stock` est déclarée `NOT NULL`.


## 18. Regrouper les données avec GROUP BY

`GROUP BY` permet de calculer des agrégats séparément pour chaque groupe.

### 18.1 Compter les clients par ville

```sql
SELECT
    ville,
    COUNT(*) AS nombre_clients
FROM clients
GROUP BY ville
ORDER BY nombre_clients DESC;
```

Chaque ville forme un groupe et possède son propre nombre de clients.

### 18.2 Calculer la valeur totale du stock

```sql
SELECT
    actif,
    SUM(stock) AS total_stock
FROM produits
GROUP BY actif;
```

Cette requête compare les quantités de stock des produits actifs et inactifs.

### 18.3 Filtrer les groupes avec HAVING

`WHERE` filtre les lignes avant le regroupement.

`HAVING` filtre les groupes après leur formation.

Exemple :

```sql
SELECT
    ville,
    COUNT(*) AS nombre_clients
FROM clients
GROUP BY ville
HAVING COUNT(*) >= 2;
```

Cette requête affiche uniquement les villes qui possèdent au moins deux clients.

### 18.4 Différence entre WHERE et HAVING

```text
Lignes de la table
       |
       v
WHERE : filtre les lignes
       |
       v
GROUP BY : forme les groupes
       |
       v
HAVING : filtre les groupes
       |
       v
Résultat
```

Exemple :

```sql
SELECT
    ville,
    COUNT(*) AS nombre_clients
FROM clients
WHERE ville IS NOT NULL
GROUP BY ville
HAVING COUNT(*) >= 2;
```

Les clients dont la ville n'est pas renseignée sont exclus avant le regroupement. La condition `HAVING` conserve ensuite les groupes ayant au moins deux clients.


## 19. Relier plusieurs tables avec JOIN

Les jointures permettent d'associer des données de plusieurs tables en utilisant une relation.

### 19.1 INNER JOIN

`INNER JOIN` conserve les lignes pour lesquelles la condition de jointure trouve une correspondance.

Exemple :

```sql
SELECT
    commandes.id AS commande_id,
    clients.nom AS nom_client,
    commandes.date_commande,
    commandes.statut
FROM commandes
INNER JOIN clients
    ON commandes.client_id = clients.id;
```

Cette requête affiche les commandes avec le nom du client associé.

### 19.2 Diagramme de jointure

```text
+------------------+        +------------------+
| clients          |        | commandes        |
+------------------+        +------------------+
| id               |<-------| client_id        |
| nom              |        | id               |
| email            |        | statut           |
+------------------+        +------------------+
            |
            | JOIN sur clients.id = commandes.client_id
            v
      Résultat combiné
```

Le résultat peut contenir des colonnes provenant des deux tables.

### 19.3 LEFT JOIN

`LEFT JOIN` conserve toutes les lignes de la table située à gauche, même si aucune correspondance n'existe dans la table de droite.

Exemple :

```sql
SELECT
    clients.nom,
    commandes.id AS commande_id
FROM clients
LEFT JOIN commandes
    ON commandes.client_id = clients.id
ORDER BY clients.nom;
```

Un client sans commande apparaît quand même. Les colonnes issues de `commandes` valent alors `NULL`.

### 19.4 Trouver les clients sans commande

```sql
SELECT
    clients.id,
    clients.nom
FROM clients
LEFT JOIN commandes
    ON commandes.client_id = clients.id
WHERE commandes.id IS NULL;
```

Cette requête identifie les clients qui n'ont aucune commande correspondante.

### 19.5 Relier trois tables

```sql
SELECT
    clients.nom,
    commandes.id AS commande_id,
    produits.nom AS produit,
    lignes_commande.quantite,
    lignes_commande.prix_unitaire
FROM clients
INNER JOIN commandes
    ON commandes.client_id = clients.id
INNER JOIN lignes_commande
    ON lignes_commande.commande_id = commandes.id
INNER JOIN produits
    ON produits.id = lignes_commande.produit_id
ORDER BY commandes.id, produits.nom;
```

Cette requête relie les clients, les commandes, les lignes de commande et les produits.

Elle permet de retrouver le détail des produits commandés par chaque client.

### 19.6 Attention aux duplications de lignes

Lorsqu'une commande contient plusieurs produits, le résultat comporte plusieurs lignes pour cette commande.

Ce comportement est normal : la requête représente ici les lignes de détail, pas une ligne par commande.

Il faut choisir le niveau de détail attendu avant d'écrire une requête.


## 20. Comprendre les clés primaires et étrangères

### 20.1 Clé primaire

Une clé primaire identifie chaque ligne d'une table.

Exemple :

```sql
id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY
```

Une clé primaire doit être unique et ne peut pas être nulle.

### 20.2 Clé étrangère

Une clé étrangère référence une clé primaire ou une autre contrainte d'unicité compatible dans une table liée.

Exemple :

```sql
client_id BIGINT NOT NULL REFERENCES clients(id)
```

Cette règle empêche de référencer un client inexistant.

### 20.3 Unicité

Une contrainte `UNIQUE` empêche certaines duplications.

Exemple :

```sql
email VARCHAR(255) UNIQUE
```

La manière de traiter les valeurs nulles sous une contrainte d'unicité peut dépendre du SGBD et de la forme exacte de la contrainte. Dans notre table, `email` possède également `NOT NULL`.

### 20.4 Clés composées

Une contrainte peut porter sur plusieurs colonnes :

```sql
UNIQUE (commande_id, produit_id)
```

La paire formée par `commande_id` et `produit_id` doit être unique.

Cela permet de représenter une règle métier qui porte sur plusieurs valeurs simultanément.

### 20.5 Pourquoi ces contraintes sont-elles importantes ?

Les contraintes ne sont pas uniquement destinées à aider l'application. Elles font appliquer certaines règles directement par le SGBD.

Elles évitent qu'une donnée incorrecte soit introduite par un autre script, une autre application ou une opération administrative, sous réserve des privilèges et des mécanismes employés.


## 21. Intégrité des données : NOT NULL, DEFAULT et CHECK

### 21.1 NOT NULL

```sql
nom VARCHAR(100) NOT NULL
```

Cette contrainte exige que la colonne soit renseignée.

### 21.2 DEFAULT

```sql
stock INTEGER NOT NULL DEFAULT 0
```

Lorsque l'insertion ne fournit pas de valeur pour `stock`, PostgreSQL utilise zéro.

`DEFAULT` ne remplace pas automatiquement une valeur explicitement fournie par `NULL`. Si la colonne est `NOT NULL`, une insertion explicite de `NULL` échouera.

### 21.3 CHECK

```sql
prix NUMERIC(10, 2) CHECK (prix >= 0)
```

La contrainte interdit les valeurs négatives.

Les contraintes `CHECK` doivent être conçues avec attention, car leur comportement doit être cohérent avec les règles métier. Dans SQL, une expression de contrainte qui évalue à `UNKNOWN` en raison d'une valeur nulle n'est pas automatiquement équivalente à `FALSE`. Utilisez `NOT NULL` en complément lorsqu'une valeur doit obligatoirement être présente.

### 21.4 UNIQUE

```sql
email VARCHAR(255) UNIQUE NOT NULL
```

Cette définition interdit les emails dupliqués et les valeurs absentes.

### 21.5 Ajouter une contrainte à une table existante

Exemple :

```sql
ALTER TABLE produits
ADD CONSTRAINT prix_non_negatif
CHECK (prix >= 0);
```

Si des données existantes violent la règle, l'ajout peut échouer. Avant une modification de schéma, examinez les données concernées et préparez une stratégie de correction.


## 22. Normalisation : organiser correctement les données

La normalisation consiste à structurer les données afin de limiter les duplications inutiles et les anomalies de mise à jour.

### 22.1 Exemple non normalisé

Supposons une table contenant :

```text
commande_id | nom_client | email_client | produits
```

Une seule cellule pourrait contenir plusieurs produits :

```text
101 | Amina | amina@example.test | Clavier, Souris, Écran
```

Cette structure complique les recherches, les mises à jour et les calculs.

### 22.2 Première forme normale

Dans une organisation conforme à la première forme normale, les colonnes contiennent des valeurs individuelles selon le modèle prévu.

Il est préférable de représenter les lignes de commande séparément :

```text
commande_id | produit_id | quantite
------------+------------+---------
101         | 1          | 2
101         | 2          | 1
101         | 3          | 1
```

Chaque ligne décrit un élément de la commande.

### 22.3 Réduire la duplication

Au lieu de répéter l'email du client pour chaque commande :

```text
clients
   |
   +--- id, nom, email
          |
          v
commandes
   |
   +--- id, client_id, date
```

La table `commandes` référence le client grâce à `client_id`.

Le nom et l'email sont stockés dans la table `clients`, puis récupérés par une jointure quand cela est nécessaire.

### 22.4 Pourquoi conserver le prix historique dans la commande ?

Le prix d'un produit peut changer dans le temps.

La table `produits` contient son prix actuel.

La table `lignes_commande` contient le prix appliqué au moment de la commande.

Ces deux valeurs répondent à deux questions différentes :

- combien coûte le produit actuellement ?
- à quel prix cette ligne a-t-elle été commandée ?

La normalisation n'interdit pas toute duplication. Une donnée historique ou une valeur calculée conservée peut être justifiée lorsqu'elle répond à une exigence métier clairement définie.


## 23. Créer et utiliser un index

Un index est une structure qui permet au moteur de retrouver certaines lignes plus efficacement.

Sans index adapté, le moteur peut devoir parcourir une grande partie de la table pour répondre à une requête.

### 23.1 Exemple conceptuel

```text
TABLE clients
+
| id | nom | email |
+----+-----+-------+
| 1  | ... | ...   |
| 2  | ... | ...   |
| 3  | ... | ...   |
|... | ... | ...   |

Sans index adapté :
Parcours possible d'un grand nombre de lignes

Avec index approprié :
Recherche potentiellement plus directe
```

Le choix de l'accès réel appartient à l'optimiseur de requêtes, qui tient compte de la table, des statistiques et de la condition.

### 23.2 Créer un index

```sql
CREATE INDEX idx_clients_ville
ON clients(ville);
```

Cet index peut aider certaines requêtes filtrant ou triant les données selon `ville`.

Il n'est pas garanti que toutes les requêtes utilisant `ville` soient plus rapides. Pour une très petite table ou une condition peu sélective, un parcours de table peut être préférable.

### 23.3 Index sur une clé étrangère

PostgreSQL crée automatiquement un index pour la clé primaire et pour les contraintes `UNIQUE`, selon leur définition.

En revanche, la création d'une clé étrangère ne crée pas automatiquement un index sur les colonnes référençantes de la table enfant.

Pour notre modèle, un index peut être utile sur `commandes.client_id` :

```sql
CREATE INDEX idx_commandes_client_id
ON commandes(client_id);
```

Cet index peut aider les recherches de commandes par client et certaines opérations de jointure.

### 23.4 Le coût des index

Les index consomment du stockage et doivent être maintenus lors des opérations d'insertion, de modification et de suppression.

Créer un index sur chaque colonne n'est pas une bonne pratique.

Le choix doit se faire à partir des requêtes réelles, des mesures et des besoins de performance.


## 24. Transactions : regrouper plusieurs opérations

Une transaction permet d'exécuter plusieurs opérations comme une unité logique.

Les propriétés ACID sont souvent utilisées pour présenter les garanties d'une transaction :

- **Atomicité** : les opérations de la transaction sont validées ensemble ou annulées ensemble ;
- **Cohérence** : la transaction doit préserver les contraintes et règles applicables ;
- **Isolation** : les transactions concurrentes doivent respecter le niveau d'isolation configuré ;
- **Durabilité** : après validation, les changements validés doivent persister selon les garanties du système.

Les garanties exactes dépendent du SGBD, de sa configuration et de la nature des opérations.

### 24.1 Commencer une transaction

```sql
BEGIN;
```

Les instructions SQL suivantes appartiennent à cette transaction jusqu'à sa validation ou son annulation.

### 24.2 Valider une transaction

```sql
COMMIT;
```

`COMMIT` valide les changements de la transaction.

### 24.3 Annuler une transaction

```sql
ROLLBACK;
```

`ROLLBACK` annule les changements non validés de la transaction en cours.

### 24.4 Exemple de transaction

Supposons que vous souhaitiez diminuer le stock d'un produit après une commande.

```sql
BEGIN;

UPDATE produits
SET stock = stock - 2
WHERE id = 1
  AND stock >= 2;

COMMIT;
```

Cette requête présente le principe, mais une application réelle doit vérifier que la mise à jour a modifié exactement le nombre de lignes attendu avant de valider toute l'opération.

Une simple condition `WHERE` peut ne modifier aucune ligne si le stock est insuffisant ou si le produit n'existe pas.

### 24.5 Exemple plus prudent

```sql
BEGIN;

UPDATE produits
SET stock = stock - 2
WHERE id = 1
  AND stock >= 2
RETURNING id, stock;
```

Examinez le résultat :

- si une ligne est renvoyée, la mise à jour a été appliquée à un produit correspondant ;
- si aucune ligne n'est renvoyée, il faut examiner la situation et annuler ou traiter l'échec.

Pour annuler :

```sql
ROLLBACK;
```

Pour valider, seulement si toutes les étapes attendues sont réussies :

```sql
COMMIT;
```

Dans une application, ces contrôles doivent être intégrés au traitement. La requête `RETURNING` permet ici d'illustrer la vérification du changement.

### 24.6 Pourquoi les transactions sont-elles essentielles ?

Elles sont utilisées dans de nombreux scénarios :

- transfert d'argent ;
- traitement de commandes ;
- réservation de ressources ;
- mise à jour cohérente de plusieurs tables ;
- création d'un enregistrement avec ses détails associés.

Une transaction doit toutefois rester suffisamment courte. Des transactions ouvertes trop longtemps peuvent bloquer des opérations, conserver des ressources et compliquer l'administration.


## 25. Sécurité SQL : utilisateurs et privilèges

Une base de données ne doit pas être administrée avec un compte superutilisateur par toutes les applications.

Il est préférable de créer des rôles avec des droits limités aux opérations nécessaires.

### 25.1 Créer un rôle applicatif

Depuis une session disposant des privilèges administratifs PostgreSQL :

```sql
CREATE ROLE boutique_app
LOGIN
PASSWORD 'RemplacerParUnSecretLongEtUnique';
```

Ce secret est illustratif et ne doit pas être utilisé tel quel sur un système réel.

Dans une installation de production, utilisez un mécanisme adapté pour générer, conserver et faire tourner les secrets. Évitez de les intégrer dans des dépôts, des scripts partagés ou des journaux.

### 25.2 Accorder l'accès à la base

```sql
GRANT CONNECT ON DATABASE boutique_sql TO boutique_app;
```

Ce privilège permet au rôle de se connecter à la base, sous réserve des autres règles de connexion et d'authentification.

Il ne donne pas automatiquement accès à toutes les tables.

### 25.3 Accorder l'accès au schéma

Dans la base `boutique_sql` :

```sql
GRANT USAGE ON SCHEMA public TO boutique_app;
```

`USAGE` sur un schéma permet notamment de référencer les objets pour lesquels le rôle dispose par ailleurs des droits nécessaires.

### 25.4 Accorder des droits de lecture

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA public
TO boutique_app;
```

Cette instruction accorde les droits de lecture sur les tables existantes dans ce schéma.

Elle ne règle pas automatiquement les droits des futures tables créées par d'autres rôles.

### 25.5 Accorder les droits d'écriture nécessaires

Pour une application qui doit manipuler les données :

```sql
GRANT INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO boutique_app;
```

Ces privilèges doivent correspondre au besoin réel de l'application.

Une application qui ne doit que consulter des rapports ne devrait pas recevoir automatiquement des droits `INSERT`, `UPDATE` et `DELETE`.

### 25.6 Séquences PostgreSQL

Les colonnes `IDENTITY` utilisent un mécanisme interne de génération de valeurs.

Dans les cas où des droits sur les séquences sont nécessaires, ils doivent être gérés selon le mécanisme de génération et les privilèges de la base.

Pour les tables déjà existantes qui utilisent des séquences classiques, des privilèges sur les séquences peuvent être requis.

Ne contournez pas un problème de privilèges en accordant un statut superutilisateur à l'application.

### 25.7 SQL et injection

Une injection SQL survient notamment lorsqu'une application construit une requête en incorporant directement des données non fiables dans le texte SQL.

Exemple conceptuel à éviter :

```text
"SELECT * FROM clients WHERE email = '" + email_saisi + "'"
```

Si l'application assemble du SQL à partir de valeurs non fiables sans échappement ou paramétrage approprié, la requête peut être altérée.

La solution courante consiste à utiliser des requêtes paramétrées dans le langage de programmation et le pilote de base de données.

Exemple conceptuel avec un paramètre :

```sql
SELECT *
FROM clients
WHERE email = $1;
```

La syntaxe de liaison des paramètres dépend du pilote et de l'interface utilisés.

Le point essentiel est de transmettre la valeur comme un paramètre de données, et non de la concaténer comme du texte SQL.


## 26. Sauvegarde et restauration : premières notions

Une base de données contient souvent des informations dont la perte serait coûteuse.

Une stratégie de sauvegarde doit préciser :

- quelles bases et quels objets doivent être sauvegardés ;
- à quelle fréquence ;
- où les copies seront conservées ;
- qui peut y accéder ;
- combien de temps elles sont conservées ;
- comment elles seront restaurées ;
- comment l'intégrité des restaurations sera vérifiée.

Une sauvegarde non testée ne garantit pas que la restauration fonctionnera au moment nécessaire.

### 26.1 Sauvegarder une base PostgreSQL avec pg_dump

Depuis le terminal, pour une installation locale qui utilise le compte système `postgres` :

```bash
sudo -u postgres pg_dump -Fc boutique_sql > boutique_sql.dump
```

L'option `-Fc` demande un format d'archive personnalisé adapté à `pg_restore`.

Le fichier `boutique_sql.dump` sera créé dans le répertoire courant, avec les permissions liées à l'utilisateur exécutant la commande et aux règles du système.

Choisissez un répertoire approprié et protégez le fichier de sauvegarde.

### 26.2 Vérifier que le fichier existe

```bash
ls -lh boutique_sql.dump
```

Cette vérification confirme l'existence et la taille du fichier, mais ne prouve pas à elle seule que toutes les données pourront être restaurées.

### 26.3 Restaurer dans une autre base

Créez d'abord une base de test :

```bash
sudo -u postgres createdb boutique_sql_test
```

Puis restaurez l'archive :

```bash
sudo -u postgres pg_restore \
  -d boutique_sql_test \
  boutique_sql.dump
```

Examinez les messages de restauration et vérifiez ensuite les tables et les données.

### 26.4 Vérification

Connectez-vous à la base restaurée :

```bash
sudo -u postgres psql -d boutique_sql_test
```

Puis :

```sql
SELECT COUNT(*) FROM clients;
```

Comparez les résultats avec la base d'origine.

Une restauration complète nécessite davantage de vérifications que le simple comptage de lignes. Les objets, contraintes, séquences, privilèges et dépendances doivent être examinés selon les besoins du système.

### 26.5 Protéger les sauvegardes

Les sauvegardes doivent être accessibles uniquement aux personnes et systèmes autorisés.

Elles peuvent contenir des données personnelles, des données financières ou des informations confidentielles.

Prévoyez également une protection contre la suppression accidentelle ou la compromission simultanée de la base et de ses sauvegardes.


## 27. Afficher le détail d'une commande

Les concepts étudiés peuvent être combinés pour produire une requête métier.

Le détail d'une commande peut inclure :

- l'identifiant de la commande ;
- le nom du client ;
- le nom du produit ;
- la quantité commandée ;
- le prix historique appliqué ;
- le montant de la ligne.

Exemple :

```sql
SELECT
    commandes.id AS commande_id,
    clients.nom AS client,
    produits.nom AS produit,
    lignes_commande.quantite,
    lignes_commande.prix_unitaire,
    lignes_commande.quantite * lignes_commande.prix_unitaire
        AS montant_ligne
FROM commandes
INNER JOIN clients
    ON clients.id = commandes.client_id
INNER JOIN lignes_commande
    ON lignes_commande.commande_id = commandes.id
INNER JOIN produits
    ON produits.id = lignes_commande.produit_id
ORDER BY commandes.id, produits.nom;
```

Cette requête combine les relations, les jointures et les expressions calculées.

Le montant de la ligne est calculé à partir de la quantité et du prix historique.

### 27.1 Calculer le montant total par commande

```sql
SELECT
    commandes.id AS commande_id,
    clients.nom AS client,
    SUM(
        lignes_commande.quantite * lignes_commande.prix_unitaire
    ) AS montant_total
FROM commandes
INNER JOIN clients
    ON clients.id = commandes.client_id
INNER JOIN lignes_commande
    ON lignes_commande.commande_id = commandes.id
GROUP BY commandes.id, clients.nom
ORDER BY commandes.id;
```

La clause `GROUP BY` permet ici d'obtenir une ligne par commande.

### 27.2 Calculer le montant total par client

```sql
SELECT
    clients.id,
    clients.nom,
    SUM(
        lignes_commande.quantite * lignes_commande.prix_unitaire
    ) AS montant_total
FROM clients
INNER JOIN commandes
    ON commandes.client_id = clients.id
INNER JOIN lignes_commande
    ON lignes_commande.commande_id = commandes.id
GROUP BY clients.id, clients.nom
ORDER BY montant_total DESC;
```

Cette requête ne renvoie que les clients associés à des lignes de commande.

Pour inclure également les clients sans commande, il faut adapter les jointures et le traitement des valeurs `NULL`.


## 28. Travaux pratiques guidés

### TP 1 — Vérifier la base et ses tables

**Objectif :** vérifier que le modèle a été créé correctement.

Dans le terminal :

```bash
sudo -u postgres psql -d boutique_sql
```

Dans `psql` :

```text
\dt
```

Inspectez chaque table :

```text
\d clients
\d produits
\d commandes
\d lignes_commande
```

**Résultat attendu :** les quatre tables apparaissent avec leurs colonnes et leurs contraintes.

### TP 2 — Insérer des clients

Exécutez :

```sql
INSERT INTO clients (nom, email, ville)
VALUES
    ('Amina Diallo', 'amina@example.test', 'Douala'),
    ('Paul Martin', 'paul@example.test', 'Yaoundé'),
    ('Sara Nguema', 'sara@example.test', 'Douala');
```

Vérifiez :

```sql
SELECT id, nom, email, ville
FROM clients
ORDER BY id;
```

Si les clients ont déjà été insérés, ne répétez pas aveuglément cette étape : la contrainte d'unicité sur `email` empêchera les duplications.

### TP 3 — Insérer les produits

Exécutez :

```sql
INSERT INTO produits (nom, prix, stock, actif)
VALUES
    ('Clavier USB', 15.00, 40, TRUE),
    ('Souris sans fil', 25.50, 30, TRUE),
    ('Écran 24 pouces', 149.90, 12, TRUE),
    ('Câble HDMI', 9.99, 60, TRUE),
    ('Casque audio', 45.00, 20, TRUE);
```

Vérifiez :

```sql
SELECT id, nom, prix, stock, actif
FROM produits
ORDER BY id;
```

### TP 4 — Créer des commandes

Dans une base de formation fraîchement créée, les trois clients et les cinq produits ajoutés dans les exercices précédents auront normalement des identifiants générés à partir de 1.

Pour éviter de dépendre de cet ordre dans une application réelle, on devrait plutôt récupérer les identifiants générés ou les sélectionner au moyen de critères uniques. Ici, nous utilisons les identifiants issus de ce laboratoire neuf.

```sql
INSERT INTO commandes (client_id, statut)
VALUES
    (1, 'payee'),
    (1, 'expediee'),
    (2, 'en_attente');
```

Insérez ensuite les lignes de commande :

```sql
INSERT INTO lignes_commande (
    commande_id,
    produit_id,
    quantite,
    prix_unitaire
)
VALUES
    (1, 1, 2, 15.00),
    (1, 2, 1, 25.50),
    (2, 3, 1, 149.90),
    (3, 2, 2, 25.50),
    (3, 4, 1, 9.99);
```

Vérifiez :

```sql
SELECT *
FROM commandes
ORDER BY id;
```

Puis :

```sql
SELECT *
FROM lignes_commande
ORDER BY id;
```

### TP 5 — Rechercher les produits en stock

```sql
SELECT nom, prix, stock
FROM produits
WHERE stock > 0
ORDER BY stock DESC;
```

Comparez le nombre de lignes renvoyées avec celui de la table `produits`.

### TP 6 — Calculer la valeur théorique du stock

```sql
SELECT
    SUM(prix * stock) AS valeur_theorique_stock
FROM produits;
```

Cette valeur représente la somme des prix actuels multipliés par les quantités présentes.

Elle ne doit pas être automatiquement assimilée à la valeur comptable du stock, qui peut dépendre d'autres règles de valorisation.

### TP 7 — Afficher les commandes avec leurs clients

```sql
SELECT
    commandes.id,
    clients.nom,
    commandes.date_commande,
    commandes.statut
FROM commandes
INNER JOIN clients
    ON clients.id = commandes.client_id
ORDER BY commandes.id;
```

Identifiez le client associé à chaque commande.

### TP 8 — Calculer le montant des commandes

```sql
SELECT
    commande_id,
    SUM(quantite * prix_unitaire) AS montant_total
FROM lignes_commande
GROUP BY commande_id
ORDER BY commande_id;
```

Vérifiez manuellement le montant de chaque commande à partir des quantités et des prix unitaires.

### TP 9 — Tester une contrainte

Essayez l'insertion suivante :

```sql
INSERT INTO produits (nom, prix, stock, actif)
VALUES ('Produit invalide', -5, 10, TRUE);
```

Le SGBD doit refuser l'insertion en raison de la contrainte sur `prix`.

L'objectif est de comprendre que la validation des données peut être faite directement au niveau du schéma SQL.

### TP 10 — Effectuer une transaction de test

Commencez :

```sql
BEGIN;
```

Insérez un client de test :

```sql
INSERT INTO clients (nom, email, ville)
VALUES ('Client temporaire', 'temporaire@example.test', 'Douala');
```

Vérifiez sa présence dans la transaction :

```sql
SELECT *
FROM clients
WHERE email = 'temporaire@example.test';
```

Annulez :

```sql
ROLLBACK;
```

Vérifiez que le client n'existe plus :

```sql
SELECT *
FROM clients
WHERE email = 'temporaire@example.test';
```

Le résultat doit être vide si l'insertion n'avait pas été validée par une autre transaction et que l'annulation a été correctement exécutée.


## 29. Exercices de compréhension avec corrigés

### Exercice 1 — Définition d'une base de données

**Question :** quelle est la différence entre une base de données et un SGBD ?

**Corrigé :**

La base de données est l'ensemble structuré des informations stockées. Le SGBD est le logiciel qui gère ces données, les requêtes, les contraintes et l'accès des utilisateurs.

### Exercice 2 — SELECT

**Question :** comment afficher uniquement les noms des clients ?

**Corrigé :**

```sql
SELECT nom
FROM clients;
```

### Exercice 3 — Filtrage

**Question :** comment rechercher les produits dont le prix est supérieur à 50 ?

**Corrigé :**

```sql
SELECT nom, prix
FROM produits
WHERE prix > 50;
```

### Exercice 4 — Tri

**Question :** comment afficher les produits du plus cher au moins cher ?

**Corrigé :**

```sql
SELECT nom, prix
FROM produits
ORDER BY prix DESC;
```

### Exercice 5 — Clé primaire

**Question :** quel est le rôle d'une clé primaire ?

**Corrigé :**

Elle identifie chaque ligne de manière unique et ne permet pas les valeurs nulles.

### Exercice 6 — Clé étrangère

**Question :** pourquoi la colonne `client_id` de `commandes` est-elle une clé étrangère ?

**Corrigé :**

Elle référence un client existant dans la table `clients`, ce qui permet au SGBD de contrôler la cohérence de cette relation.

### Exercice 7 — Valeurs NULL

**Question :** comment rechercher les clients dont la ville n'est pas renseignée ?

**Corrigé :**

```sql
SELECT *
FROM clients
WHERE ville IS NULL;
```

### Exercice 8 — Agrégation

**Question :** comment compter le nombre de produits ?

**Corrigé :**

```sql
SELECT COUNT(*) AS nombre_produits
FROM produits;
```

### Exercice 9 — Jointure

**Question :** comment afficher l'identifiant de chaque commande et le nom de son client ?

**Corrigé :**

```sql
SELECT
    commandes.id,
    clients.nom
FROM commandes
INNER JOIN clients
    ON clients.id = commandes.client_id;
```

### Exercice 10 — Sécurité

**Question :** pourquoi ne faut-il pas utiliser un compte superutilisateur PostgreSQL pour toute application ?

**Corrigé :**

Un compte superutilisateur possède des privilèges très étendus. Une application compromise ou mal programmée pourrait effectuer des opérations dangereuses. Il faut accorder seulement les privilèges nécessaires à son fonctionnement.

### Exercice 11 — Transactions

**Question :** quelle est la différence entre `COMMIT` et `ROLLBACK` ?

**Corrigé :**

`COMMIT` valide les changements de la transaction. `ROLLBACK` annule les changements non validés de la transaction en cours.

### Exercice 12 — Index

**Question :** un index rend-il toutes les requêtes plus rapides ?

**Corrigé :**

Non. Un index peut améliorer certains accès, mais il consomme du stockage et doit être maintenu lors des modifications. Le choix de l'index dépend des requêtes et des données.


## 30. Défi final : créer et interroger une mini-base de boutique

### Objectif

Construire une base de données relationnelle simple et être capable d'effectuer les principales opérations SQL.

### Cahier des charges

La base doit contenir :

```text
clients
produits
commandes
lignes_commande
```

Elle doit respecter les règles suivantes :

- chaque client possède un identifiant ;
- chaque email de client doit être unique ;
- chaque produit possède un prix non négatif ;
- le stock d'un produit ne peut pas être négatif ;
- chaque commande référence un client existant ;
- chaque ligne de commande référence une commande et un produit existants ;
- chaque ligne possède une quantité positive ;
- le prix unitaire de la ligne est conservé historiquement.

### Étape A — Créer le modèle

Créez les quatre tables avec les contraintes expliquées dans le cours.

Vérifiez les relations avec les commandes `\d` de PostgreSQL.

### Étape B — Ajouter les données

Ajoutez au moins trois clients, cinq produits et trois commandes.

Ajoutez plusieurs lignes de commande afin de pouvoir tester les jointures et les agrégations.

### Étape C — Écrire les requêtes

Réalisez les opérations suivantes :

1. afficher les clients de Douala ;
2. afficher les produits classés du plus cher au moins cher ;
3. afficher les produits dont le stock dépasse 20 unités ;
4. compter les clients ;
5. calculer le prix moyen des produits ;
6. afficher les commandes avec le nom du client ;
7. calculer le montant de chaque commande ;
8. calculer le montant total par client ;
9. trouver les clients sans commande ;
10. vérifier que les contraintes refusent un prix négatif.

### Étape D — Tester une transaction

Créez un client de test dans une transaction, contrôlez sa présence, puis annulez l'opération.

Vérifiez que ce client n'apparaît plus après le `ROLLBACK`.

### Étape E — Sauvegarder la base

Utilisez `pg_dump` pour créer une archive, restaurez-la dans une nouvelle base et vérifiez les données.

### Critères de réussite

Le défi est réussi lorsque :

- les quatre tables sont correctement créées ;
- les relations sont définies ;
- les contraintes empêchent les données incohérentes prévues ;
- les requêtes de lecture donnent les résultats attendus ;
- les jointures relient correctement les clients, les commandes et les produits ;
- les agrégations produisent des montants cohérents ;
- la transaction peut être annulée ;
- la sauvegarde et la restauration ont été testées.


## 31. Fiche de révision rapide

### Créer une table

```sql
CREATE TABLE exemple (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);
```

### Insérer une ligne

```sql
INSERT INTO exemple (nom)
VALUES ('Amina');
```

### Lire des données

```sql
SELECT *
FROM exemple;
```

### Filtrer

```sql
SELECT *
FROM exemple
WHERE nom = 'Amina';
```

### Trier

```sql
SELECT *
FROM exemple
ORDER BY nom ASC;
```

### Limiter les résultats

```sql
SELECT *
FROM exemple
ORDER BY id
LIMIT 10;
```

### Modifier une ligne

```sql
UPDATE exemple
SET nom = 'Amina Diallo'
WHERE id = 1;
```

### Supprimer une ligne

```sql
DELETE FROM exemple
WHERE id = 1;
```

Toujours vérifier la condition avant d'exécuter un `UPDATE` ou un `DELETE` important.

### Compter les lignes

```sql
SELECT COUNT(*)
FROM exemple;
```

### Regrouper des données

```sql
SELECT ville, COUNT(*)
FROM clients
GROUP BY ville;
```

### Relier des tables

```sql
SELECT clients.nom, commandes.id
FROM clients
INNER JOIN commandes
    ON commandes.client_id = clients.id;
```

### Transaction

```sql
BEGIN;

-- Opérations SQL à effectuer

COMMIT;
```

Pour annuler au lieu de valider :

```sql
ROLLBACK;
```

### Vérification de la base

Dans `psql` :

```text
\l
\dt
\d clients
\du
\conninfo
\q
```

### Sauvegarde PostgreSQL

```bash
sudo -u postgres pg_dump -Fc boutique_sql > boutique_sql.dump
```


## 32. Glossaire

**Base de données** : ensemble structuré d'informations stockées pour être consultées et modifiées.

**Clé étrangère** : colonne ou ensemble de colonnes qui référence une clé compatible d'une autre table ou de la même table.

**Clé primaire** : clé qui identifie de manière unique chaque ligne.

**Colonne** : attribut défini dans la structure d'une table.

**Contrainte** : règle imposée aux données, par exemple une valeur obligatoire ou une valeur unique.

**DDL** : catégorie d'instructions SQL qui définissent les structures de la base.

**DML** : catégorie d'instructions SQL qui manipulent les données.

**DCL** : catégorie d'instructions liées au contrôle des privilèges.

**Index** : structure permettant d'accélérer certains accès aux données.

**INNER JOIN** : jointure qui ne conserve que les lignes possédant une correspondance selon la condition de jointure.

**LEFT JOIN** : jointure qui conserve toutes les lignes de la table de gauche, avec des valeurs nulles pour les colonnes de droite en l'absence de correspondance.

**Ligne** : enregistrement d'une table.

**NULL** : valeur SQL représentant une donnée absente, inconnue ou non renseignée selon le contexte.

**Normalisation** : organisation du modèle de données visant notamment à limiter les duplications et les anomalies de mise à jour.

**PostgreSQL** : système de gestion de base de données relationnelle.

**SGBD** : logiciel qui gère une base de données.

**SQL** : langage permettant de définir, interroger et manipuler des données dans les systèmes de bases de données qui le prennent en charge.

**Table** : structure qui organise des données en lignes et colonnes.

**Transaction** : ensemble d'opérations traitées selon des règles de validation et d'annulation.

**Type de données** : définition de la nature des valeurs qu'une colonne ou une expression peut contenir.

**UNIQUE** : contrainte qui interdit certaines duplications de valeurs.

**WHERE** : clause qui filtre les lignes selon une condition.


## 33. Documentation officielle

Les documentations suivantes permettent d'approfondir les concepts et de vérifier les particularités de chaque SGBD.

### PostgreSQL

- Tutoriel officiel :  
  https://www.postgresql.org/docs/current/tutorial.html

- Documentation de référence :  
  https://www.postgresql.org/docs/current/

- Le langage SQL :  
  https://www.postgresql.org/docs/current/sql.html

- Création de tables :  
  https://www.postgresql.org/docs/current/ddl-basics.html

- Contraintes :  
  https://www.postgresql.org/docs/current/ddl-constraints.html

- Transactions :  
  https://www.postgresql.org/docs/current/tutorial-transactions.html

- Index :  
  https://www.postgresql.org/docs/current/indexes.html

- Sauvegarde et restauration :  
  https://www.postgresql.org/docs/current/backup.html

### MySQL

- Manuel de référence MySQL :  
  https://dev.mysql.com/doc/refman/8.4/en/

- Instructions SQL :  
  https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html

### SQLite

- Documentation générale :  
  https://www.sqlite.org/docs.html

- Langage SQL pris en charge par SQLite :  
  https://www.sqlite.org/lang.html

- Fonctionnement de SQLite :  
  https://www.sqlite.org/howitworks.html


## Conclusion

Vous disposez désormais des bases nécessaires pour comprendre et utiliser SQL dans un système de bases de données relationnelles.

La maîtrise de SQL ne consiste pas seulement à mémoriser `SELECT`, `INSERT`, `UPDATE` et `DELETE`. Elle repose aussi sur la compréhension du modèle relationnel, des contraintes, des relations entre les tables, des transactions et des droits d'accès.

Le parcours recommandé est le suivant :

```text
Comprendre les bases de données
             |
             v
Créer une base et des tables
             |
             v
Définir les types et les contraintes
             |
             v
Insérer et rechercher des données
             |
             v
Modifier et supprimer des données
             |
             v
Relier les tables avec JOIN
             |
             v
Calculer des statistiques
             |
             v
Comprendre les transactions
             |
             v
Gérer les utilisateurs et les privilèges
             |
             v
Sauvegarder et restaurer
```

Ces compétences forment une base solide avant d'aborder les requêtes SQL avancées, les index et l'optimisation des requêtes, les vues, les fonctions, les procédures, la réplication et l'administration avancée des bases de données.