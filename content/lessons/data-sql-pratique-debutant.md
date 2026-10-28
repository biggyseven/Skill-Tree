# Travaux pratiques (MySQL/PostgreSQL) — Débutant

> **Mise en contexte.** Vous rejoignez une petite équipe qui développe une application de formation. Les apprenants peuvent consulter des cours, s'inscrire et obtenir un résultat à une évaluation. La conception relationnelle et la normalisation sont déjà étudiées ; l'objectif est maintenant d'apprendre à mettre ce modèle en pratique dans un vrai SGBD. Vous allez préparer un environnement isolé, créer le schéma, charger un jeu de données synthétiques, exécuter des requêtes lisibles, vérifier les contraintes, maîtriser les transactions et documenter les résultats. Dans un laboratoire professionnel, une commande qui « semble fonctionner » ne suffit pas : il faut connaître la base ciblée, les préconditions, les effets produits et la façon de revenir à un état propre.

## 1. Objectifs pédagogiques

Ce cours est un atelier guidé de mise en pratique SQL. Il consolide la lecture des tables, les clés, les jointures et la normalisation en les appliquant dans PostgreSQL ou MySQL. Les deux moteurs parlent SQL, mais ne sont pas identiques : leurs types, outils en ligne de commande, paramètres de configuration, gestion des identifiants et certains comportements transactionnels diffèrent. L'objectif n'est donc pas de mémoriser une syntaxe qui serait universelle, mais de séparer le SQL commun des détails propres au moteur choisi.

À la fin du parcours, vous devrez pouvoir :

- distinguer un serveur de base de données, une base, un schéma et une table ;
- utiliser un environnement de développement isolé avec des données fictives ;
- vous connecter au bon serveur et confirmer l'identité de la base cible ;
- créer un schéma relationnel avec clés primaires, clés étrangères, contraintes d'unicité et contraintes de domaine ;
- insérer et modifier des données de façon contrôlée ;
- exécuter des SELECT, filtres, tris, agrégations et jointures ;
- comprendre les différences courantes entre PostgreSQL et MySQL ;
- utiliser une transaction pour regrouper des modifications qui doivent réussir ensemble ;
- diagnostiquer une erreur en lisant le message, en vérifiant les hypothèses et en réduisant le cas ;
- organiser le SQL dans des fichiers reproductibles et versionnés ;
- tester le résultat réel plutôt que de se fier uniquement au code de retour ;
- produire un compte rendu minimal permettant à une autre personne de reproduire l'atelier.

Ce cours vise le niveau débutant, mais ne vous demande pas de traiter SQL comme une suite de commandes isolées. Une bonne pratique de laboratoire combine un objectif, une hypothèse, une commande, un résultat attendu et un contrôle. Lorsque le résultat diffère, vous cherchez la cause avant de recommencer au hasard.

## 2. Préparer un laboratoire sûr et reproductible

### 2.1 Pourquoi isoler l'environnement ?

Une requête SQL peut modifier ou supprimer des données. Une commande exécutée sur la mauvaise base peut donc avoir un effet très différent de celui attendu. Les premières manipulations doivent se dérouler sur une base locale, un conteneur jetable ou un serveur de développement explicitement identifié. Évitez d'utiliser une base de production comme terrain d'essai, même pour une simple insertion.

Avant l'atelier, établissez une règle claire : toutes les données seront fictives, le laboratoire pourra être réinitialisé, et aucun compte ne disposera de droits excessifs. Les scripts ne doivent pas inclure de mot de passe personnel, de jeton ou de donnée réelle sensible. Les captures et journaux que vous partagez doivent masquer les secrets et les informations qui permettraient d'identifier des personnes.

Documentez quatre éléments :
1. le moteur et sa version ;
2. le nom de la base utilisée pour l'exercice ;
3. le compte de connexion et ses privilèges ;
4. la procédure qui remet le laboratoire à zéro.

Un laboratoire fiable n'est pas seulement une machine sur laquelle SQL s'exécute. C'est une expérience que l'on peut refaire, contrôler et expliquer.

### 2.2 Architecture de travail

~~~mermaid
flowchart TD
    A["Apprenant ou développeur"] --> B["Client SQL / terminal"]
    B --> C["Serveur PostgreSQL ou MySQL"]
    C --> D["Base de laboratoire"]
    D --> E["Schéma et tables"]
    E --> F["Données fictives"]
    F --> G["Requêtes et assertions"]
    G --> H["Compte rendu reproductible"]
~~~

Le client SQL envoie une instruction au serveur. Le serveur l'analyse, vérifie les droits, applique les règles du moteur et renvoie un résultat ou une erreur. La base est l'espace dans lequel les objets et les données sont stockés. PostgreSQL possède des schémas à l'intérieur d'une base, alors que dans MySQL le mot schema est souvent synonyme de database dans l'usage courant. Cette différence de vocabulaire compte lorsque vous lisez une documentation ou un outil d'administration.

### 2.3 Deux façons d'exécuter SQL

Vous pouvez utiliser un terminal interactif ou un client graphique. Le terminal facilite la reproduction d'une séquence et l'automatisation ; un client graphique aide à explorer les tables, les types et les résultats. Les deux peuvent être utiles. Quel que soit l'outil, assurez-vous de voir le serveur, la base et le compte actifs avant une commande qui change des données.

Pour PostgreSQL, le client usuel est psql. Une forme de connexion fréquente est :

~~~bash
psql -h localhost -p 5432 -U lab_user -d skilltree_lab
~~~

Pour MySQL, le client usuel est mysql :

~~~bash
mysql -h 127.0.0.1 -P 3306 -u lab_user -p skilltree_lab
~~~

Ces exemples supposent que le serveur écoute sur l'adresse et le port correspondants, que la base existe et que le compte est autorisé. Le mot de passe n'est pas écrit dans la commande MySQL ; l'option -p provoque une demande interactive. Ne copiez pas un mot de passe directement dans l'historique du terminal. Dans un outil ou une application, privilégiez un mécanisme de secrets adapté à votre environnement.

Les commandes de connexion dépendent du système et de l'installation. Si le client n'est pas installé, identifiez d'abord la méthode prévue par votre équipe ou votre environnement de formation. Ne téléchargez pas un exécutable inconnu au hasard pour résoudre un problème de connexion.

### 2.4 Confirmer la cible

Dans PostgreSQL, vous pouvez examiner la base et la session avec :

~~~sql
SELECT current_database(), current_user, version();
~~~

Dans MySQL, utilisez par exemple :

~~~sql
SELECT DATABASE(), CURRENT_USER(), VERSION();
~~~

Interprétez les résultats avant de poursuivre. Une connexion réussie ne signifie pas que vous êtes dans la bonne base ou avec le compte adapté. Un compte d'administration peut se connecter correctement, mais il possède probablement davantage de privilèges que nécessaire pour un laboratoire d'application.

Dans psql, la commande méta \conninfo affiche des informations de connexion. Dans le client MySQL, la commande STATUS fournit des renseignements sur la session. Ces commandes sont propres aux clients et ne font pas partie du SQL portable. Distinguez les commandes du client des instructions envoyées au serveur.

## 3. Comprendre le modèle avant d'écrire les scripts

Le laboratoire utilise quatre entités : APPRENANTS, FORMATEURS, COURS et INSCRIPTIONS. Chaque table représente un type de fait. Un apprenant peut suivre plusieurs cours et un cours peut accueillir plusieurs apprenants ; la table INSCRIPTIONS représente cette association et porte la date d'inscription et le score.

Les règles de l'atelier sont les suivantes :

- apprenant_id identifie un apprenant ;
- formateur_id identifie un formateur ;
- cours_id identifie un cours ;
- dans cette première version, chaque cours possède un formateur responsable unique ;
- un apprenant ne peut avoir qu'une seule inscription par cours dans le périmètre du laboratoire ;
- le score est absent avant l'évaluation ou compris entre 0 et 100 ;
- une inscription référence toujours un apprenant et un cours existants.

Ces règles sont volontairement simples, mais elles ont des conséquences sur les clés. La clé primaire d'INSCRIPTIONS sera composée de apprenant_id et cours_id. Si le métier autorise plusieurs sessions ou tentatives pour le même cours, cette clé doit changer. Une hypothèse de modèle n'est pas une vérité universelle : elle doit être documentée et révisée lorsque le besoin métier change.

~~~mermaid
erDiagram
    APPRENANTS ||--o{ INSCRIPTIONS : "s'inscrit"
    COURS ||--o{ INSCRIPTIONS : "accueille"
    FORMATEURS ||--o{ COURS : "responsable"
    APPRENANTS {
        int apprenant_id PK
        string nom_apprenant
        string email_apprenant UK
    }
    FORMATEURS {
        int formateur_id PK
        string nom_formateur
    }
    COURS {
        int cours_id PK
        string titre_cours
        int formateur_id FK
    }
    INSCRIPTIONS {
        int apprenant_id PK, FK
        int cours_id PK, FK
        date date_inscription
        decimal score
    }
~~~

La modélisation et la normalisation ont déjà montré pourquoi le nom d'un apprenant n'est pas recopié dans chaque inscription. Cette séparation est pratique : si l'adresse email change, une seule ligne est mise à jour. Les clés étrangères assurent que les références pointent vers des lignes existantes. Les contraintes de domaine limitent certaines valeurs invalides, comme un score négatif.

## 4. Créer la base et préparer les scripts

### 4.1 Créer la base de laboratoire

La création de la base dépend des permissions et de l'installation. Un administrateur ou un compte habilité peut exécuter une instruction telle que :

~~~sql
CREATE DATABASE skilltree_lab;
~~~

Connectez-vous ensuite à cette base avec le client approprié. La manière de basculer de base diffère selon le moteur : PostgreSQL utilise généralement une nouvelle connexion ou la commande méta de psql \c ; le client MySQL propose USE skilltree_lab. Ces commandes de client ne sont pas toutes portables.

Dans PostgreSQL, vous pouvez isoler les objets avec un schéma nommé lab :

~~~sql
CREATE SCHEMA IF NOT EXISTS lab;
~~~

Dans le reste de cet atelier, les exemples n'utilisent pas systématiquement le préfixe lab afin de conserver une syntaxe commune simple. Vous pouvez les exécuter dans une base dédiée, ou ajouter le schéma et les qualifications nécessaires dans PostgreSQL. Si plusieurs applications partagent une base, le choix du schéma et les privilèges doivent être établis explicitement.

### 4.2 Organiser les fichiers

Un laboratoire doit éviter que l'intégralité du SQL soit conservée uniquement dans l'historique du terminal. Créez par exemple cette structure dans votre répertoire de travail :

~~~text
sql-lab/
  README.md
  migrations/
    001_create_schema.sql
  seeds/
    002_seed_data.sql
  queries/
    003_basic_queries.sql
  tests/
    004_integrity_checks.sql
  notes/
    results.md
~~~

Le fichier README doit mentionner le moteur et la version testés, la procédure de connexion, l'ordre d'exécution et la manière de réinitialiser l'environnement. Les scripts servent de journal de décisions et permettent de reproduire le résultat sur une autre machine.

Dans un projet réel, les migrations sont généralement gérées par un outil ou une convention d'équipe. Le numéro de migration indique l'ordre et permet de comprendre comment la structure a évolué. Évitez de réécrire silencieusement une migration déjà appliquée sur des environnements partagés ; préparez une nouvelle migration qui modifie le schéma, et planifiez comment traiter les données existantes.

### 4.3 Bien distinguer script initial et migration

Un script initial peut créer toutes les tables pour un laboratoire jetable. Une migration d'application doit gérer un changement de structure sur une base qui possède déjà des données. Le second problème est plus délicat : il faut considérer l'ordre des opérations, la compatibilité avec la version de l'application, les contraintes et la possibilité de revenir en arrière.

~~~mermaid
flowchart TD
    A["Définir le modèle et les hypothèses"] --> B["Écrire migration versionnée"]
    B --> C["L'exécuter sur base jetable"]
    C --> D["Contrôler tables, clés et données"]
    D --> E{"Tests conformes ?"}
    E -- "Non" --> F["Corriger ou écrire migration suivante"]
    F --> C
    E -- "Oui" --> G["Revue et plan de déploiement"]
    G --> H["Appliquer sur l'environnement cible selon la procédure"]
~~~

Les instructions DDL comme CREATE TABLE sont gérées transactionnellement différemment selon les moteurs et les opérations. PostgreSQL permet de nombreuses opérations DDL dans une transaction ; MySQL exécute fréquemment certaines instructions DDL avec un commit implicite. Pour des migrations de production, vérifiez le comportement exact de la version et de l'instruction, plutôt que de supposer que ROLLBACK annulera toujours une modification de schéma.

## 5. Créer les tables et les contraintes

Le script ci-dessous reste volontairement proche du SQL commun. Les colonnes d'identifiant utilisent INTEGER et reçoivent des valeurs explicites dans l'atelier ; cela évite de commencer par les différences entre mécanismes d'auto-incrémentation. Dans une application réelle, vous choisirez une stratégie d'identifiant et des types adaptés au moteur.

~~~sql
CREATE TABLE formateurs (
    formateur_id INTEGER PRIMARY KEY,
    nom_formateur VARCHAR(120) NOT NULL
);

CREATE TABLE apprenants (
    apprenant_id INTEGER PRIMARY KEY,
    nom_apprenant VARCHAR(120) NOT NULL,
    email_apprenant VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE cours (
    cours_id INTEGER PRIMARY KEY,
    titre_cours VARCHAR(160) NOT NULL,
    formateur_id INTEGER NOT NULL,
    FOREIGN KEY (formateur_id)
        REFERENCES formateurs(formateur_id)
);

CREATE TABLE inscriptions (
    apprenant_id INTEGER NOT NULL,
    cours_id INTEGER NOT NULL,
    date_inscription DATE NOT NULL,
    score DECIMAL(5,2),
    PRIMARY KEY (apprenant_id, cours_id),
    FOREIGN KEY (apprenant_id)
        REFERENCES apprenants(apprenant_id),
    FOREIGN KEY (cours_id)
        REFERENCES cours(cours_id),
    CHECK (score IS NULL OR (score >= 0 AND score <= 100))
);
~~~

Ce script exprime plusieurs règles. PRIMARY KEY identifie les lignes et ne permet pas que sa clé soit dupliquée. NOT NULL indique qu'une valeur doit être présente. UNIQUE protège une règle d'unicité pour l'email dans ce modèle. Les clés étrangères empêchent qu'un cours fasse référence à un formateur absent ou qu'une inscription référence un apprenant ou un cours absent. CHECK exprime la plage des scores.

Une contrainte valide uniquement la règle qu'on lui a demandé d'appliquer. CHECK sur score n'assure pas qu'un apprenant a réellement passé l'évaluation. La clé étrangère ne garantit pas que le cours est encore ouvert aux inscriptions. Ces règles plus riches nécessitent un modèle complémentaire, une logique applicative ou une stratégie transactionnelle adaptée.

### 5.1 Identifier les dépendances et l'ordre de création

Une table qui contient une clé étrangère dépend de la table référencée. Ici, FORMATEURS et APPRENANTS peuvent être créées avant les tables qui les référencent ; COURS référence FORMATEURS et INSCRIPTIONS référence APPRENANTS et COURS. Si l'ordre est incorrect, la création de la contrainte peut échouer parce que la cible n'existe pas encore.

La même dépendance apparaît lors du chargement initial : insérez d'abord les formateurs et les apprenants, puis les cours, puis les inscriptions. Cette séquence respecte les références et rend les erreurs plus faciles à diagnostiquer.

### 5.2 Différences de moteur à connaître

- **PostgreSQL :** les schémas organisent les objets à l'intérieur d'une base. Les mécanismes d'identifiants automatiques incluent notamment IDENTITY. La documentation décrit les types, contraintes et fonctionnalités du moteur.
- **MySQL :** les objets sont généralement organisés dans une base, et le type entier peut utiliser AUTO_INCREMENT. Pour bénéficier des clés étrangères InnoDB, assurez-vous d'utiliser un moteur de stockage qui les prend en charge ; InnoDB est le choix habituel.
- Les mots réservés, la sensibilité à la casse des noms selon le système, les types disponibles et les options DDL peuvent varier. La bonne pratique est de tester sur le moteur visé.

Le script d'atelier ne crée pas automatiquement les identifiants. Cette simplicité est intentionnelle : elle permet d'observer les relations avant d'ajouter les facilités de génération. Ne mélangez pas les problèmes de génération d'identifiants et les questions de clés sans comprendre la règle de l'application.

## 6. Charger les données d'essai

Le jeu d'essai doit couvrir plusieurs cas, pas uniquement une seule ligne qui prouve que la commande fonctionne. Nous utiliserons des données fictives : trois apprenants, deux formateurs, deux cours et quatre inscriptions.

~~~sql
INSERT INTO apprenants
    (apprenant_id, nom_apprenant, email_apprenant)
VALUES
    (10, 'Amina', 'amina@example.test'),
    (11, 'Samuel', 'samuel@example.test'),
    (12, 'Nadia', 'nadia@example.test');

INSERT INTO formateurs (formateur_id, nom_formateur)
VALUES
    (7, 'Jules'),
    (8, 'Nadège');

INSERT INTO cours (cours_id, titre_cours, formateur_id)
VALUES
    (100, 'SQL débutant', 7),
    (200, 'Modélisation', 8);

INSERT INTO inscriptions
    (apprenant_id, cours_id, date_inscription, score)
VALUES
    (10, 100, '2026-09-01', 82),
    (11, 100, '2026-09-02', 75),
    (10, 200, '2026-09-05', 91),
    (12, 100, '2026-09-06', NULL);
~~~

La date est écrite au format ISO année-mois-jour, couramment reconnu pour les littéraux de date dans ces moteurs. La ligne de Nadia n'a pas encore de score ; NULL représente l'absence de valeur connue ou applicable selon la règle choisie, ce qui n'est pas la même chose que zéro. Ne remplacez pas automatiquement les valeurs inconnues par zéro : cela fausserait les moyennes et l'interprétation métier.

### 6.1 Vérifier les volumes après insertion

~~~sql
SELECT COUNT(*) AS nombre_apprenants FROM apprenants;
SELECT COUNT(*) AS nombre_formateurs FROM formateurs;
SELECT COUNT(*) AS nombre_cours FROM cours;
SELECT COUNT(*) AS nombre_inscriptions FROM inscriptions;
~~~

Les résultats attendus pour le jeu initial sont respectivement 3, 2, 2 et 4. Ce sont des assertions simples, mais elles ne prouvent pas tout : quatre inscriptions pourraient être présentes tout en reliant les mauvais apprenants aux mauvais cours. Les vérifications suivantes examinent la qualité des références et des valeurs.

### 6.2 Remarquer l'ordre des insertions

Si vous essayez d'insérer une inscription avant le cours correspondant, la clé étrangère doit rejeter l'opération. Ce rejet n'est pas un échec de l'atelier : c'est la preuve que la contrainte protège le modèle. De même, une tentative de dupliquer un email déjà utilisé doit échouer parce que UNIQUE protège cette règle du jeu.

Lorsqu'une insertion multi-lignes échoue, le comportement détaillé peut dépendre du moteur, du type d'instruction et du mode transactionnel. Ne supposez pas qu'aucune ligne n'a été ajoutée ou que toutes les lignes ont été ajoutées sans vérifier la transaction et le résultat réellement observé. Après une erreur, examinez l'état avant de relancer le script.

## 7. Lire et filtrer les données

La commande SELECT sert à demander les colonnes et les lignes utiles. Pour commencer, choisissez explicitement les colonnes dont vous avez besoin :

~~~sql
SELECT apprenant_id, nom_apprenant, email_apprenant
FROM apprenants
ORDER BY apprenant_id;
~~~

Évitez d'utiliser SELECT * dans les scripts d'application qui dépendent d'un ordre de colonnes stable. L'astérisque est commode pour une exploration rapide, mais la structure d'une table peut évoluer. Les requêtes explicites indiquent les données attendues et rendent plus visibles les changements de contrat.

### 7.1 Filtres WHERE

~~~sql
SELECT apprenant_id, nom_apprenant
FROM apprenants
WHERE nom_apprenant = 'Amina';
~~~

Une condition WHERE élimine les lignes qui ne satisfont pas la condition. Les opérateurs usuels incluent =, <>, <, <=, >, >=, AND, OR et NOT. Utilisez des parenthèses lorsque la priorité des opérateurs risque d'être ambiguë :

~~~sql
SELECT cours_id, titre_cours
FROM cours
WHERE cours_id = 100 OR (cours_id = 200 AND titre_cours = 'Modélisation');
~~~

Sans parenthèses, la priorité de AND par rapport à OR peut donner un résultat différent de l'intention. Les conditions doivent refléter clairement le besoin.

Pour rechercher une plage, utilisez BETWEEN lorsque ses bornes inclusives correspondent au sens voulu :

~~~sql
SELECT apprenant_id, cours_id, score
FROM inscriptions
WHERE score BETWEEN 75 AND 90;
~~~

BETWEEN comprend la borne inférieure et la borne supérieure. Les lignes avec score NULL ne satisfont pas cette condition ; NULL doit être traité par les opérateurs dédiés.

### 7.2 NULL et les valeurs manquantes

Pour identifier les inscriptions sans score :

~~~sql
SELECT apprenant_id, cours_id
FROM inscriptions
WHERE score IS NULL;
~~~

Pour les scores déjà disponibles :

~~~sql
SELECT apprenant_id, cours_id, score
FROM inscriptions
WHERE score IS NOT NULL;
~~~

La comparaison score = NULL n'est pas l'équivalent d'IS NULL dans le modèle SQL habituel. Les expressions impliquant NULL peuvent produire UNKNOWN, qui ne passe pas le filtre WHERE. Il faut bien distinguer un score égal à zéro d'un score absent, un email vide d'un email NULL et une valeur inconnue d'une valeur qui n'existe pas par définition.

### 7.3 Trier et limiter les résultats

~~~sql
SELECT apprenant_id, cours_id, score
FROM inscriptions
ORDER BY score DESC, apprenant_id ASC;
~~~

L'ordre ne doit pas être supposé si ORDER BY n'est pas écrit. Pour limiter le nombre de lignes, LIMIT est disponible dans PostgreSQL et MySQL :

~~~sql
SELECT cours_id, titre_cours
FROM cours
ORDER BY cours_id
LIMIT 5;
~~~

Un tri stable nécessite un ordre qui distingue les lignes si vous devez paginer de façon reproductible. Trier uniquement sur une valeur répétée peut produire un ordre variable entre lignes ayant la même valeur. Une clé unique peut compléter le tri.

### 7.4 Éviter les constructions fragiles

Une recherche par préfixe peut utiliser LIKE :

~~~sql
SELECT apprenant_id, nom_apprenant
FROM apprenants
WHERE nom_apprenant LIKE 'A%';
~~~

Le pourcentage correspond à zéro ou plusieurs caractères ; le soulignement correspond à un caractère dans les motifs LIKE usuels. La sensibilité à la casse dépend du moteur, de la collation et des expressions utilisées. Ne présumez pas que la même recherche se comportera de la même façon avec toutes les configurations.

Pour compter des valeurs distinctes, utilisez COUNT(DISTINCT colonne) lorsque c'est bien la question posée. Évitez de transformer implicitement la logique métier dans une requête juste pour obtenir un nombre qui paraît plausible.

## 8. Insérer, modifier et supprimer sans danger

### 8.1 INSERT

Une insertion doit préciser les colonnes de destination :

~~~sql
INSERT INTO apprenants
    (apprenant_id, nom_apprenant, email_apprenant)
VALUES
    (13, 'Mariam', 'mariam@example.test');
~~~

Cette écriture résiste mieux à l'ajout de colonnes optionnelles qu'une insertion sans liste de colonnes. Les valeurs doivent respecter les types, les contraintes NOT NULL, UNIQUE et les éventuelles clés étrangères. Les instructions préparées doivent être privilégiées dans le code applicatif pour éviter l'injection SQL.

### 8.2 UPDATE : vérifier le périmètre

Une modification sans clause WHERE peut modifier toutes les lignes de la table. La requête suivante change le nom de l'apprenant 13 :

~~~sql
UPDATE apprenants
SET nom_apprenant = 'Mariam N.'
WHERE apprenant_id = 13;
~~~

Avant une opération qui peut toucher beaucoup de lignes, exécutez un SELECT utilisant exactement la même condition. Vérifiez les identifiants et le nombre de lignes ciblées. En environnement de travail, des mécanismes de revue ou de confirmation peuvent être nécessaires pour les opérations sensibles.

### 8.3 DELETE : savoir ce qui sera supprimé

~~~sql
DELETE FROM apprenants
WHERE apprenant_id = 13;
~~~

Cet exemple peut échouer si l'apprenant est référencé par une inscription, car la clé étrangère protège l'intégrité. Ce comportement est généralement souhaitable : il évite de laisser une inscription orpheline. Selon la règle métier, on peut supprimer explicitement les inscriptions associées dans une transaction, archiver l'apprenant ou utiliser une action référentielle bien étudiée. Ne choisissez pas ON DELETE CASCADE automatiquement, car il peut entraîner la suppression en chaîne de données dont le cycle de vie est différent.

Pour supprimer des données, écrivez d'abord le SELECT qui montre les lignes visées. Vérifiez le résultat. Ensuite seulement, exécutez la modification dans le bon environnement. Si les opérations doivent être atomiques, utilisez une transaction et validez les postconditions avant le COMMIT.

## 9. Jointures : relier les faits

La normalisation place les données dans plusieurs tables. Les jointures permettent de reconstituer la vue nécessaire à une question métier. Pour afficher le nom des apprenants avec le titre des cours auxquels ils sont inscrits :

~~~sql
SELECT
    a.nom_apprenant,
    c.titre_cours,
    i.date_inscription,
    i.score
FROM inscriptions AS i
INNER JOIN apprenants AS a
    ON a.apprenant_id = i.apprenant_id
INNER JOIN cours AS c
    ON c.cours_id = i.cours_id
ORDER BY a.nom_apprenant, c.titre_cours;
~~~

Chaque relation possède un rôle clair. Les alias a, c et i rendent la requête moins répétitive, à condition d'être cohérents. La condition ON relie les clés correspondantes. Une omission ou un mauvais prédicat de jointure peut fabriquer un produit cartésien, c'est-à-dire une combinaison de chaque ligne d'une table avec chaque ligne de l'autre.

### 9.1 INNER JOIN et LEFT JOIN

INNER JOIN renvoie les lignes qui ont une correspondance entre les relations jointes. LEFT JOIN conserve toutes les lignes de la table de gauche et remplit par NULL les colonnes de droite lorsqu'aucune correspondance n'existe.

Pour afficher tous les cours, y compris ceux qui ne possèdent aucune inscription :

~~~sql
SELECT
    c.cours_id,
    c.titre_cours,
    i.apprenant_id
FROM cours AS c
LEFT JOIN inscriptions AS i
    ON i.cours_id = c.cours_id
ORDER BY c.cours_id, i.apprenant_id;
~~~

Un cours sans inscription reste visible dans le résultat. Si une condition sur la table de droite est ajoutée au WHERE, il faut vérifier qu'elle ne supprime pas les lignes NULL que LEFT JOIN devait conserver. Les conditions liées à la correspondance peuvent parfois être placées dans ON ; la décision dépend de la question.

### 9.2 Vérifier la cardinalité du résultat

Une jointure peut augmenter le nombre de lignes si une relation de droite contient plusieurs correspondances. C'est souvent le comportement attendu, pas une duplication anormale. Lorsque vous joignez plusieurs relations un-à-plusieurs, les lignes peuvent se multiplier et modifier un total si l'agrégat est placé au mauvais niveau.

Avant de calculer un total, posez trois questions :
1. quelle est la granularité de départ : une ligne par inscription, par cours ou par apprenant ?
2. quelle cardinalité la jointure produit-elle ?
3. l'agrégat compte-t-il le fait que vous souhaitez mesurer, ou plusieurs représentations du même fait ?

Un bon SQL débute par la définition de l'unité métier que représente chaque ligne.

## 10. Agréger et produire des rapports

Les fonctions d'agrégation résument un ensemble de lignes. COUNT compte, SUM additionne, AVG calcule une moyenne, MIN et MAX trouvent les extrêmes. Les valeurs NULL sont généralement ignorées par les agrégats qui opèrent sur une expression, tandis que COUNT(*) compte les lignes.

~~~sql
SELECT
    cours_id,
    COUNT(*) AS nombre_inscriptions,
    COUNT(score) AS nombre_scores_connus,
    AVG(score) AS moyenne_score
FROM inscriptions
GROUP BY cours_id
ORDER BY cours_id;
~~~

COUNT(*) compte toutes les inscriptions par cours. COUNT(score) compte celles dont le score est non NULL. La moyenne est calculée sur les scores connus. Une distinction entre nombre d'inscriptions et nombre d'évaluations terminées est importante : les deux nombres ne répondent pas à la même question métier.

Pour ne conserver que les cours ayant au moins deux inscriptions :

~~~sql
SELECT cours_id, COUNT(*) AS nombre_inscriptions
FROM inscriptions
GROUP BY cours_id
HAVING COUNT(*) >= 2;
~~~

WHERE filtre les lignes avant l'agrégation ; HAVING filtre les groupes après leur formation. Utilisez HAVING pour les conditions qui portent sur le résultat agrégé.

### 10.1 Contrôler les résultats d'agrégation

Si vous combinez plusieurs tables avant un SUM, vérifiez que la jointure ne multiplie pas les faits qui doivent être additionnés. Par exemple, joindre les inscriptions à une table de commentaires où plusieurs commentaires existent par inscription peut répéter le score. Un SUM(score) après cette jointure risque de surcompter.

Une stratégie utile consiste à agréger chaque fait au niveau correct avant de joindre les résultats, ou à utiliser une sous-requête qui produit une ligne par entité. La solution exacte dépend du modèle et du besoin ; la leçon essentielle est de tester la granularité, pas seulement de vérifier qu'une requête renvoie une valeur.

## 11. Transactions : regrouper des opérations cohérentes

Une transaction permet de traiter un ensemble d'opérations comme une unité logique. Les propriétés ACID — atomicité, cohérence, isolation et durabilité — décrivent des garanties essentielles des systèmes transactionnels, mais le niveau exact d'isolation et certaines options dépendent du moteur et de la configuration.

La séquence habituelle est :

~~~sql
BEGIN;

UPDATE inscriptions
SET score = 84
WHERE apprenant_id = 10
  AND cours_id = 100;

SELECT apprenant_id, cours_id, score
FROM inscriptions
WHERE apprenant_id = 10
  AND cours_id = 100;

COMMIT;
~~~

Dans cet exemple, on lit le résultat avant validation. Dans un atelier, on peut remplacer COMMIT par ROLLBACK pour annuler les modifications non validées lorsque le moteur et le contexte s'y prêtent. Ne confondez pas le rollback d'une transaction avec une restauration de sauvegarde : ce sont des mécanismes différents, et toutes les opérations DDL ne sont pas annulables de la même manière sur tous les moteurs.

### 11.1 La transaction et l'ordre des opérations

Supposons qu'un paiement et une inscription doivent être enregistrés ensemble. Si une étape réussit et l'autre échoue, le système pourrait se retrouver dans un état incohérent si les opérations ne sont pas correctement regroupées. La transaction sert à préserver l'unité logique, accompagnée de contraintes et de contrôles applicatifs.

~~~mermaid
sequenceDiagram
    participant App as Application
    participant DB as Base de données
    App->>DB: BEGIN
    App->>DB: Insérer la première donnée
    App->>DB: Insérer la seconde donnée
    DB-->>App: Résultat et contrôles
    alt Toutes les étapes sont valides
        App->>DB: COMMIT
        DB-->>App: Transaction validée
    else Une étape échoue
        App->>DB: ROLLBACK
        DB-->>App: Modifications non validées annulées
    end
~~~

Une transaction ne dispense pas de gérer les erreurs. Dans le code applicatif, si une instruction échoue, la transaction doit être annulée ou remise dans un état correct avant de continuer, selon le moteur et le pilote utilisés. Il faut aussi éviter de garder une transaction ouverte pendant une interaction utilisateur longue : cela peut retenir des verrous et gêner les autres sessions.

### 11.2 SAVEPOINT

Un point de sauvegarde transactionnel permet de revenir à une étape intermédiaire dans une transaction qui se poursuit. Son utilité dépend de la logique de récupération. Par exemple :

~~~sql
BEGIN;
UPDATE inscriptions
SET score = 84
WHERE apprenant_id = 10 AND cours_id = 100;

SAVEPOINT apres_score;

UPDATE inscriptions
SET score = 120
WHERE apprenant_id = 11 AND cours_id = 100;
-- La contrainte CHECK peut rejeter la seconde opération.

ROLLBACK TO SAVEPOINT apres_score;
COMMIT;
~~~

Les détails du comportement après erreur diffèrent entre moteurs et pilotes, en particulier pour l'état de la transaction. En PostgreSQL, une erreur d'instruction place normalement la transaction dans un état où il faut la faire revenir à un état valide avant de poursuivre, par exemple via un point de sauvegarde adapté. Testez cette séquence dans le moteur cible et consultez sa documentation. Le principe est de prévoir comment une opération partiellement réussie sera gérée, pas de supposer que le serveur s'en sortira automatiquement.

## 12. Tests d'intégrité : prouver que le schéma protège les règles

Une base de données robuste doit être testée par des cas valides et invalides. Les tests négatifs sont essentiels : la contrainte doit rejeter ce qui viole la règle. Un test qui ne fait qu'insérer une ligne normale prouve peu de choses.

### 12.1 Tester une clé étrangère

L'insertion suivante doit être refusée si aucun apprenant 999 n'existe :

~~~sql
INSERT INTO inscriptions
    (apprenant_id, cours_id, date_inscription, score)
VALUES
    (999, 100, '2026-09-10', 50);
~~~

Ne désactivez pas la contrainte pour faire passer le test. Le rejet constitue le résultat attendu. Vérifiez l'état après l'erreur afin de confirmer qu'aucune donnée indésirable n'a été conservée.

### 12.2 Tester la clé composée

~~~sql
INSERT INTO inscriptions
    (apprenant_id, cours_id, date_inscription, score)
VALUES
    (10, 100, '2026-09-11', 77);
~~~

Cette opération doit être refusée car le couple (10, 100) existe déjà dans le jeu initial. Si le besoin métier change pour autoriser plusieurs tentatives ou sessions, ce rejet ne sera plus une exigence correcte ; on modifiera le modèle et la clé.

### 12.3 Tester la plage de valeurs

~~~sql
INSERT INTO inscriptions
    (apprenant_id, cours_id, date_inscription, score)
VALUES
    (11, 200, '2026-09-11', 150);
~~~

La note 150 viole CHECK. La contrainte protège le domaine tel qu'il est défini dans le modèle. En revanche, le test ne garantit pas que la note de chaque cours suit la même échelle dans un autre contexte ; si certaines évaluations sont notées sur 20 et d'autres sur 100, le modèle doit le préciser.

### 12.4 Tester l'unicité de l'email

~~~sql
INSERT INTO apprenants
    (apprenant_id, nom_apprenant, email_apprenant)
VALUES
    (14, 'Autre Amina', 'amina@example.test');
~~~

L'email du jeu initial est déjà utilisé. L'insertion devrait être rejetée. La contrainte UNIQUE formalise l'hypothèse qu'un email ne peut être associé qu'à un apprenant dans cette application. Ce choix doit correspondre à la règle métier ; dans un système qui autorise une adresse partagée par plusieurs personnes, il faut le revoir.

### 12.5 Créer une petite matrice de tests

| Règle | Cas valide | Cas invalide attendu |
|---|---|---|
| Clé primaire | Identifiant nouveau | Identifiant déjà présent |
| Clé étrangère | Référence existante | Référence absente |
| UNIQUE | Email différent | Email déjà présent |
| CHECK sur score | Score entre 0 et 100 ou NULL | Score inférieur à 0 ou supérieur à 100 |
| Clé d'inscription | Couple inédit | Couple déjà enregistré |
| NOT NULL | Valeur présente | Valeur obligatoire absente |

La matrice sert de contrat de vérification. Pour chaque cas, notez la commande, le résultat attendu, le résultat observé et l'état réel des données après le test. Un message d'erreur seul ne prouve pas l'état final si plusieurs instructions ou une transaction sont impliquées.

## 13. Paramètres et prévention des injections SQL

Dans une application, ne construisez pas une requête en concaténant directement une valeur fournie par l'utilisateur. Une entrée qui contient des caractères SQL peut modifier le sens de la requête si elle est insérée comme texte brut. Utilisez les paramètres du pilote ou les requêtes préparées, avec un mécanisme adapté à la bibliothèque.

Exemple conceptuel en Python : le texte SQL utilise un marqueur de paramètre défini par le pilote ; la valeur est transmise séparément comme donnée. La syntaxe exacte des marqueurs varie selon le pilote.

~~~python
# Exemple pédagogique avec un pilote dont le marqueur est %s.
sql = "SELECT apprenant_id, nom_apprenant FROM apprenants WHERE email_apprenant = %s"
cursor.execute(sql, (email_recherche,))
rows = cursor.fetchall()
~~~

Le paramètre email_recherche est transmis séparément. Ne remplacez pas ce mécanisme par une interpolation de chaîne. Le code doit aussi gérer les erreurs, fermer les curseurs et les connexions proprement et appliquer un compte de base doté uniquement des droits nécessaires.

Les paramètres ne peuvent généralement pas représenter n'importe quel nom de table ou de colonne. Si l'utilisateur peut choisir un ordre de tri, utilisez une liste blanche de colonnes valides plutôt que d'insérer un nom arbitraire dans le SQL. La prévention des injections repose sur une combinaison de requêtes paramétrées, validation du besoin, droits minimums et tests.

## 14. PostgreSQL et MySQL : choisir le bon vocabulaire

Le SQL commun facilite l'apprentissage, mais chaque moteur possède ses caractéristiques. Un laboratoire visant les deux moteurs doit distinguer :
- la syntaxe standard ou largement commune ;
- les fonctionnalités propres au moteur ;
- les outils de ligne de commande ;
- les types et mécanismes de génération des identifiants ;
- le comportement transactionnel et les opérations DDL ;
- les options de stockage, de collation et de contraintes.

### 14.1 Identifiants générés automatiquement

PostgreSQL propose notamment les colonnes IDENTITY. Exemple :

~~~sql
CREATE TABLE exemple_postgres (
    id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    libelle VARCHAR(100) NOT NULL
);
~~~

MySQL utilise couramment AUTO_INCREMENT :

~~~sql
CREATE TABLE exemple_mysql (
    id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    libelle VARCHAR(100) NOT NULL
);
~~~

Ces deux scripts sont spécifiques à leur moteur et ne doivent pas être exécutés tels quels sur l'autre sans adaptation. Ils illustrent le concept, pas une syntaxe commune portable. Pour l'atelier commun, des identifiants explicites sont utilisés afin d'éviter cette divergence.

### 14.2 Types et dates

Les types de date, de temps, de texte numérique et les conversions doivent être choisis en fonction du besoin. Le type DATE représente une date sans heure. Les instants, fuseaux horaires et dates métier ne doivent pas être confondus. Pour les montants financiers, un type décimal exact est généralement préférable à un flottant binaire. Pour les scores, le modèle utilise DECIMAL(5,2), mais la précision doit correspondre à la règle métier.

Les types ne remplacent pas les validations. Une colonne VARCHAR(120) limite la longueur selon les règles du moteur, mais ne garantit pas la qualité du nom. Une date valide n'est pas nécessairement une date cohérente avec le processus métier. Le schéma doit exprimer ce qui peut être garanti, puis l'application doit gérer les règles contextuelles supplémentaires.

### 14.3 Transactions et DDL

Dans les deux moteurs, les transactions jouent un rôle majeur pour les modifications de données. Toutefois, certaines opérations de définition du schéma et certaines options ne se comportent pas de manière identique. MySQL exécute souvent les instructions DDL avec un commit implicite ; PostgreSQL permet d'en inclure de nombreuses dans une transaction. Vérifiez le comportement de l'instruction exacte dans la version utilisée avant de compter sur un ROLLBACK pour annuler une migration.

### 14.4 Fonctions et différences mineures

Certaines fonctions, concaténations, conversions, options de pagination, collations et fonctions JSON diffèrent. Quand une requête doit fonctionner sur plusieurs moteurs, utilisez le sous-ensemble commun lorsque c'est possible et automatisez les tests sur chacun. Si une fonctionnalité spécifique est nécessaire, isolez-la et documentez le dialecte correspondant. « SQL fonctionne » n'est pas suffisamment précis pour garantir la portabilité d'une application.

## 15. Diagnostic : une méthode au lieu de commandes au hasard

Une erreur SQL peut venir d'une faute de syntaxe, d'une table absente, d'un droit insuffisant, d'une contrainte, d'une connexion incorrecte, d'une transaction déjà en échec, d'un type incompatible ou d'une hypothèse de données invalide. La méthode la plus efficace consiste à lire l'erreur, la reproduire avec un cas réduit et comparer l'état réel à l'état attendu.

~~~mermaid
flowchart TD
    A["Erreur ou résultat inattendu"] --> B["Lire le message complet"]
    B --> C["Confirmer moteur, version, base et compte"]
    C --> D["Vérifier tables, colonnes, droits et contraintes"]
    D --> E["Réduire la requête et les données"]
    E --> F["Reproduire dans le laboratoire isolé"]
    F --> G{"Cause identifiée ?"}
    G -- "Non" --> H["Formuler une hypothèse et ajouter un test ciblé"]
    H --> E
    G -- "Oui" --> I["Corriger et exécuter les tests de régression"]
    I --> J["Documenter cause, correctif et résultat"]
~~~

### 15.1 Relation ou colonne introuvable

Vérifiez d'abord la connexion et le nom exact de la table. Dans PostgreSQL, la résolution dépend du schéma et du search_path ; dans MySQL, la base sélectionnée joue un rôle visible. Vérifiez les noms de colonnes, les guillemets et la casse utilisée. N'effectuez pas immédiatement une modification de schéma pour corriger une simple erreur de contexte.

### 15.2 Violation de clé étrangère

Un rejet de clé étrangère peut signifier que la ligne référencée n'existe pas, que l'ordre d'insertion est incorrect, ou qu'une suppression est bloquée parce qu'une ligne enfant référence encore la ligne parente. Vérifiez la valeur de référence et l'ordre des opérations. Ne désactivez pas les contrôles sans plan clair de validation et de réparation ; cela pourrait introduire des liens orphelins.

### 15.3 Violation de contrainte UNIQUE

Une contrainte UNIQUE révèle que la valeur ou la combinaison existe déjà selon la règle de l'index. Cherchez la ligne existante et déterminez si le comportement voulu est de rejeter le doublon, de mettre à jour la ligne existante ou de créer une nouvelle occurrence sous un nouvel identifiant métier. Les stratégies d'upsert sont spécifiques dans leurs détails ; apprenez-les après avoir défini la règle métier.

### 15.4 Résultat vide ou nombre inattendu de lignes

Un SELECT renvoyant zéro ligne ne prouve pas que la table est vide. La condition WHERE peut être trop stricte, la valeur peut contenir un espace ou différer par sa casse, ou la connexion viser une autre base. Retirez temporairement une condition à la fois dans un laboratoire pour isoler le filtre, puis remettez-la lorsque son effet est compris.

Une jointure qui renvoie trop de lignes doit être examinée sous l'angle de la cardinalité. Il peut s'agir d'un prédicat de jointure manquant ou d'une relation un-à-plusieurs tout à fait légitime. Comptez les entités distinctes et comparez le résultat avec la granularité attendue avant de conclure que des doublons sont stockés.

### 15.5 Permissions insuffisantes

Un refus d'accès peut indiquer que le compte ne possède pas le privilège requis. N'utilisez pas immédiatement un compte superutilisateur ou root : vérifiez quel privilège manque et accordez seulement ce qui est nécessaire dans un environnement contrôlé. Le principe du moindre privilège limite l'impact d'une erreur ou d'un compte compromis.

## 16. Examiner une requête et ses performances de base

La première démarche d'optimisation est de formuler une question mesurable et de connaître le volume de données. Une requête rapide sur quatre lignes de laboratoire ne prouve pas qu'elle restera rapide sur plusieurs millions. À l'inverse, une requête qui semble longue ne doit pas être réécrite avant d'avoir observé son comportement.

EXPLAIN permet d'examiner le plan prévu par le moteur. Exemple PostgreSQL :

~~~sql
EXPLAIN
SELECT a.nom_apprenant, c.titre_cours
FROM inscriptions AS i
JOIN apprenants AS a ON a.apprenant_id = i.apprenant_id
JOIN cours AS c ON c.cours_id = i.cours_id
WHERE i.cours_id = 100;
~~~

Exemple MySQL :

~~~sql
EXPLAIN
SELECT a.nom_apprenant, c.titre_cours
FROM inscriptions AS i
JOIN apprenants AS a ON a.apprenant_id = i.apprenant_id
JOIN cours AS c ON c.cours_id = i.cours_id
WHERE i.cours_id = 100;
~~~

Les formes de sortie et les options d'EXPLAIN diffèrent selon le moteur. Des variantes peuvent exécuter réellement la requête et exposer des données ou consommer des ressources ; n'utilisez ces variantes qu'en comprenant leur effet et dans un environnement adapté.

Un index peut accélérer certaines recherches, mais il occupe de l'espace et augmente le coût d'écriture. Les clés primaires et uniques sont souvent accompagnées d'index, mais l'indexation complémentaire doit être justifiée par les requêtes fréquentes et le plan observé. Ne créez pas un index sur chaque colonne automatiquement.

## 17. Atelier complet : laboratoire SQL de la boutique pédagogique

### Mission

Vous êtes responsable d'un mini-laboratoire qui conserve les apprenants, les formateurs, les cours et les inscriptions. Vous devez construire la base, charger des données, répondre à des questions métier, tester les contraintes et produire une trace reproductible.

### Étape 1 — Préconditions

Avant d'exécuter le script, vérifiez que :
- vous êtes connecté à la base de laboratoire ;
- le compte ne dispose pas de droits de production ;
- les tables de l'atelier sont absentes ou l'environnement a été réinitialisé ;
- les données utilisées sont fictives ;
- les commandes de création et de chargement sont enregistrées dans des fichiers versionnés.

Si l'environnement contient déjà des tables avec ces noms, ne lancez pas aveuglément un script destructif. Examinez le schéma et décidez si vous devez utiliser une base jetable distincte. Dans un projet réel, la migration doit être revue, pas improvisée.

### Étape 2 — Créer le schéma

Exécutez le script de création de la section 5. Contrôlez ensuite la liste des tables depuis votre client SQL ou votre outil d'administration. Vérifiez les colonnes, les types et les contraintes ; ne vous contentez pas de constater que le client n'a pas affiché d'erreur.

### Étape 3 — Charger les données

Exécutez les insertions de la section 6 dans l'ordre prévu. Lancez les quatre COUNT et comparez les résultats aux volumes attendus. Si un résultat diffère, vérifiez l'état avant de réexécuter le script, car les clés uniques peuvent maintenant rejeter certaines lignes déjà présentes.

### Étape 4 — Répondre à des questions métier

**Question A : quels sont les apprenants inscrits ?**

~~~sql
SELECT DISTINCT a.apprenant_id, a.nom_apprenant
FROM apprenants AS a
JOIN inscriptions AS i
  ON i.apprenant_id = a.apprenant_id
ORDER BY a.apprenant_id;
~~~

DISTINCT peut être utile si la requête produit plusieurs inscriptions par apprenant et que la question porte sur la liste des personnes. Pour le jeu initial, Amina apparaît dans deux cours ; la sortie doit pourtant la présenter une seule fois.

**Question B : combien d'inscriptions et de scores connus par cours ?**

~~~sql
SELECT
    c.cours_id,
    c.titre_cours,
    COUNT(i.apprenant_id) AS nb_inscriptions,
    COUNT(i.score) AS nb_scores_connus
FROM cours AS c
LEFT JOIN inscriptions AS i
    ON i.cours_id = c.cours_id
GROUP BY c.cours_id, c.titre_cours
ORDER BY c.cours_id;
~~~

LEFT JOIN permet d'inclure un cours qui n'aurait aucune inscription. COUNT(i.apprenant_id) compte les lignes correspondantes non NULL, tandis que COUNT(i.score) compte les évaluations disposant d'un score. Pour les données initiales, SQL débutant compte trois inscriptions mais seulement deux scores connus ; Modélisation compte une inscription et un score connu.

**Question C : quels apprenants n'ont pas encore de score ?**

~~~sql
SELECT
    a.apprenant_id,
    a.nom_apprenant,
    c.titre_cours
FROM inscriptions AS i
JOIN apprenants AS a
    ON a.apprenant_id = i.apprenant_id
JOIN cours AS c
    ON c.cours_id = i.cours_id
WHERE i.score IS NULL;
~~~

Le jeu initial devrait retourner Nadia avec SQL débutant. La requête exprime l'absence de score, pas un score égal à zéro. Écrivez cette différence dans le compte rendu afin qu'elle reste comprise par une personne qui reprendra le laboratoire.

**Question D : quelle est la moyenne des scores connus par cours ?**

~~~sql
SELECT
    c.cours_id,
    c.titre_cours,
    AVG(i.score) AS moyenne_scores
FROM cours AS c
LEFT JOIN inscriptions AS i
    ON i.cours_id = c.cours_id
GROUP BY c.cours_id, c.titre_cours
ORDER BY c.cours_id;
~~~

AVG ignore les valeurs NULL. Si aucun score n'est connu pour un cours, la moyenne est NULL, ce qui signifie qu'il n'y a pas de moyenne calculable dans le jeu actuel. Ne transformez pas automatiquement ce résultat en zéro sans décision métier explicite.

### Étape 5 — Exécuter les tests négatifs

Testez la clé étrangère, la clé composée, la contrainte CHECK et UNIQUE sur l'email. Pour chaque cas invalide, notez l'erreur attendue et vérifiez que l'état final n'inclut pas la ligne rejetée. Si vous avez modifié le jeu de données avant le test, adaptez les identifiants afin de conserver un cas discriminant.

### Étape 6 — Tester une transaction

~~~sql
BEGIN;
UPDATE inscriptions
SET score = 84
WHERE apprenant_id = 10 AND cours_id = 100;

SELECT score
FROM inscriptions
WHERE apprenant_id = 10 AND cours_id = 100;

ROLLBACK;
~~~

Après le ROLLBACK, relisez la ligne et vérifiez qu'elle a retrouvé son score initial de 82, si aucune autre transaction n'a changé cette donnée entre-temps. Dans un laboratoire isolé, cette vérification est simple ; dans un environnement partagé, les interactions concurrentes rendent le contexte plus complexe.

### Étape 7 — Consigner le résultat

Dans notes/results.md, consignez le moteur et sa version, les commandes exécutées, les nombres de lignes attendus et obtenus, les tests négatifs et leur résultat, l'écart éventuel entre la sortie attendue et observée, ainsi que les limites de l'essai. Ne publiez pas de secrets ou de valeurs issues de données de production. Un compte rendu utile permet de reproduire et de comprendre, pas uniquement de montrer une capture d'écran.

~~~mermaid
flowchart LR
    A["Préparer la base isolée"] --> B["Créer tables et contraintes"]
    B --> C["Charger des données fictives"]
    C --> D["Exécuter requêtes métier"]
    D --> E["Tester cas valides et invalides"]
    E --> F["Tester transaction et rollback"]
    F --> G["Documenter les preuves"]
~~~

## 18. Automatiser les contrôles de laboratoire

Un contrôle répétable est préférable à une inspection manuelle seule. Par exemple, un script de vérification peut exécuter des SELECT qui détectent les références manquantes ou les valeurs hors domaine. Si les clés étrangères sont activées et fiables, certaines anomalies doivent déjà être impossibles ; les contrôles restent utiles lors d'une migration de données, d'une importation ou d'une opération historique.

Exemple de requête diagnostique pour détecter des inscriptions orphelines dans une ancienne table importée sans contrainte :

~~~sql
SELECT i.apprenant_id, i.cours_id
FROM inscriptions AS i
LEFT JOIN apprenants AS a
  ON a.apprenant_id = i.apprenant_id
LEFT JOIN cours AS c
  ON c.cours_id = i.cours_id
WHERE a.apprenant_id IS NULL
   OR c.cours_id IS NULL;
~~~

Dans le schéma de laboratoire normal, cette requête devrait renvoyer zéro ligne. Sur un jeu importé, des résultats indiqueraient des références à réparer avant d'ajouter les contraintes. N'effacez pas les lignes automatiquement sans connaître l'origine de la corruption ; il faut identifier les faits manquants et définir une politique de correction.

Une assertion peut aussi comparer un résultat agrégé à une attente documentée, par exemple le nombre de lignes de chaque table après chargement. Les tests peuvent être exécutés dans la CI, mais un test qui ne vérifie qu'un code retour reste faible. Vérifiez les résultats, les invariants et les cas négatifs.

## 19. Qualité des scripts et collaboration

Les scripts SQL devraient être lisibles et organisés autour d'une intention : création du schéma, chargement de données, requêtes d'analyse, tests, migration. Des commentaires courts expliquent les hypothèses métier ou les choix qui ne sont pas évidents. Évitez les commentaires qui se contentent de répéter chaque mot de la commande.

Une convention de nommage cohérente aide à réduire les erreurs. Par exemple, les identifiants suivent le même suffixe _id ; les noms de tables sont cohérents en singulier ou en pluriel ; les unités sont explicites lorsque les valeurs peuvent être interprétées de plusieurs façons. La convention exacte importe moins que sa cohérence documentée.

Lors d'une revue, un pair doit pouvoir répondre à ces questions :
- quelle règle métier chaque contrainte protège-t-elle ?
- les scripts peuvent-ils être exécutés dans l'ordre indiqué ?
- le laboratoire peut-il être recommencé sans collision ou perte imprévue ?
- les données d'essai couvrent-elles les cas limites pertinents ?
- les requêtes ont-elles une granularité et un résultat attendu clairement définis ?
- les commandes destructives sont-elles isolées et expliquées ?
- les différences PostgreSQL/MySQL sont-elles identifiées ?
- le compte utilisé possède-t-il seulement les privilèges nécessaires ?

Versionnez les scripts, pas les secrets. Ne stockez pas un fichier de configuration contenant le mot de passe réel dans le dépôt. Un exemple de configuration peut documenter les noms de variables attendus tout en laissant leurs valeurs sensibles dans un gestionnaire de secrets ou un mécanisme local non versionné.

## 20. Sécurité, sauvegarde et limites du laboratoire

Un laboratoire n'est pas un système de production. Il utilise des données synthétiques et un périmètre limité, mais les pratiques de sécurité doivent tout de même être appliquées. Utilisez un compte non administrateur pour les opérations normales, limitez l'écoute réseau si le service n'a pas besoin d'être accessible, protégez les identifiants, maintenez les composants à jour et ne partagez pas les journaux sans examiner les données qu'ils contiennent.

La sauvegarde ne se résume pas à copier un fichier ou à lancer une commande une seule fois. Une stratégie professionnelle définit la fréquence, la rétention, les responsabilités, la protection des sauvegardes et la procédure de restauration. Une sauvegarde dont la restauration n'a jamais été testée ne constitue pas une preuve suffisante de capacité de reprise.

Pour les données réelles, examinez les exigences de conservation, la confidentialité et les contrôles d'accès. Le présent atelier ne doit pas être utilisé comme modèle exhaustif de sécurité, de conformité ou de haute disponibilité. Il fournit une base de pratique SQL ; l'exploitation réelle nécessite un plan adapté au service, à ses utilisateurs et à son niveau de criticité.

## 21. Exercices d'application avec corrigés

### Exercice 1 — Connexion réussie, mauvaise base

Vous êtes connecté sans erreur, mais la table apprenants est introuvable. Quelle est la première vérification ?

**Corrigé.** Confirmez le serveur, le compte et la base active avec les fonctions propres au moteur, puis inspectez les schémas ou objets visibles. Une connexion réussie ne garantit pas la bonne base. Ne créez pas immédiatement une table homonyme qui pourrait masquer une mauvaise configuration.

### Exercice 2 — L'ordre d'insertion

Vous devez charger une inscription qui référence l'apprenant 10 et le cours 100. Dans quel ordre les lignes parentes doivent-elles être disponibles ?

**Corrigé.** L'apprenant doit déjà exister dans APPRENANTS et le cours doit déjà exister dans COURS ; le cours lui-même doit référencer un formateur valide. Créez et chargez donc les formateurs et apprenants, puis les cours, puis les inscriptions.

### Exercice 3 — Différence entre COUNT(*) et COUNT(score)

Le cours 100 a trois inscriptions, dont une avec score NULL. Quelles valeurs les deux fonctions renvoient-elles ?

**Corrigé.** COUNT(*) renvoie 3 car il compte toutes les lignes du groupe. COUNT(score) renvoie 2 car il compte les valeurs non NULL de score. Les deux nombres sont corrects, mais ils mesurent des choses différentes.

### Exercice 4 — Erreur de clé étrangère

Une inscription avec cours_id = 999 est rejetée. Donnez deux hypothèses à vérifier avant de modifier la contrainte.

**Corrigé.** Vérifiez si le cours 999 existe dans la base cible et si la commande a été exécutée dans l'ordre prévu. Il est aussi possible d'être connecté à la mauvaise base ou d'utiliser un identifiant différent de celui attendu. La suppression de la contrainte ne devrait pas être une première réponse.

### Exercice 5 — Pourquoi l'UPDATE doit-il être contrôlé ?

Vous exécutez UPDATE apprenants SET nom_apprenant = 'Inconnu'. Quel risque si WHERE est absent ?

**Corrigé.** Toutes les lignes peuvent être modifiées. Prévisualisez les lignes ciblées avec un SELECT, ajoutez une condition précise, vérifiez le nombre d'occurrences et exécutez l'opération sur l'environnement correct. Une transaction peut aider à revenir sur la modification si elle n'est pas encore validée et que le contexte le permet.

### Exercice 6 — NULL et zéro

Une inscription n'a pas encore de note. Pourquoi ne pas insérer zéro pour éviter les NULL ?

**Corrigé.** Zéro est une valeur connue qui peut représenter un résultat réel ; NULL indique l'absence de score selon la règle choisie. Remplacer les deux par la même valeur fausse les moyennes et brouille la différence entre « non évalué » et « score nul ».

### Exercice 7 — LEFT JOIN filtré

Vous souhaitez lister tous les cours, y compris ceux sans inscription, mais vous ajoutez WHERE i.score >= 80 après un LEFT JOIN. Pourquoi le résultat peut-il ne plus montrer les cours sans inscription ?

**Corrigé.** Pour les cours sans correspondance, i.score est NULL et la condition WHERE n'est pas vraie ; ces lignes sont donc filtrées. Il faut revoir la question et l'emplacement du filtre, parfois dans ON, afin de préserver les lignes de gauche voulues.

### Exercice 8 — Transaction et rollback

Vous mettez score à 84 entre BEGIN et ROLLBACK. Que devez-vous vérifier ensuite ?

**Corrigé.** Relisez la ligne en ciblant le même apprenant et le même cours ; le score doit avoir retrouvé sa valeur précédente si aucune autre transaction n'a modifié ce fait. Le message ROLLBACK seul n'est pas la preuve de la postcondition métier.

### Exercice 9 — Pourquoi paramétrer une requête ?

Une application construit SELECT ... WHERE email = 'valeur entrée par l'utilisateur' par concaténation. Quel est le risque et la correction ?

**Corrigé.** L'entrée peut contenir des caractères qui changent le sens du SQL et conduire à une injection. Utilisez les paramètres du pilote, transmettez la valeur séparément et donnez au compte de l'application les privilèges minimums nécessaires.

### Exercice 10 — Requête de performance

Une requête est rapide avec quatre inscriptions. Peut-on conclure qu'elle sera rapide avec un million de lignes ?

**Corrigé.** Non. Le jeu de test est trop petit pour tirer une conclusion fiable. Mesurez avec une charge représentative, examinez le plan avec EXPLAIN, considérez les index et la sélectivité, et vérifiez la performance sur le moteur et les données visés avant de changer la conception.

### Exercice 11 — Différences entre moteurs

Vous utilisez AUTO_INCREMENT dans le script et tentez de l'exécuter dans PostgreSQL. Quelle leçon faut-il retenir ?

**Corrigé.** La génération automatique d'identifiants est spécifique au moteur. PostgreSQL propose notamment IDENTITY ; MySQL utilise couramment AUTO_INCREMENT. Il faut soit écrire des variantes distinctes documentées, soit utiliser un mécanisme d'abstraction adapté au projet. Le script commun du laboratoire utilise des identifiants explicites pour éviter cette divergence initiale.

### Exercice 12 — Script rejoué

Un fichier INSERT échoue parce qu'un email existe déjà. Pourquoi est-ce dangereux de relancer plusieurs fois un script sans vérifier l'état ?

**Corrigé.** Les premières instructions peuvent avoir réussi avant l'erreur ou les données peuvent déjà être présentes d'un essai précédent. Avant de relancer, inspectez les lignes, le nombre d'opérations effectuées et l'état transactionnel. Un script de laboratoire doit déclarer s'il suppose une base vide, s'il réinitialise l'environnement ou s'il gère explicitement les données déjà présentes.

## 22. Défi final corrigé — construire un mini-laboratoire reproductible

### Mission

Vous devez livrer un mini-laboratoire qui permet à un pair de créer le schéma, charger les données, produire un rapport, tester les contraintes et vérifier une transaction. Le laboratoire doit fonctionner sur un moteur choisi parmi PostgreSQL et MySQL, et les différences propres à ce moteur doivent être notées.

### Étape A — Définir les préconditions

- Une base dédiée et isolée est disponible.
- Le compte de laboratoire possède les privilèges nécessaires aux exercices, mais pas un rôle d'administration global.
- Le moteur et sa version sont consignés.
- Le jeu est fictif et peut être recréé.
- Les scripts sont versionnés dans l'ordre d'exécution.

### Étape B — Créer les tables

Utilisez le schéma des sections 5 et 6. Respectez l'ordre de dépendance : FORMATEURS et APPRENANTS d'abord, ensuite COURS, enfin INSCRIPTIONS. Vérifiez que les quatre tables et leurs contraintes existent bien avant d'insérer les données.

### Étape C — Charger et vérifier le jeu de base

Insérez les trois apprenants, les deux formateurs, les deux cours et les quatre inscriptions. Les volumes attendus sont :
- 3 apprenants ;
- 2 formateurs ;
- 2 cours ;
- 4 inscriptions.

Si les volumes diffèrent, ne poursuivez pas avec des résultats qui reposeraient sur un état inconnu. Identifiez la cause, réinitialisez le laboratoire selon la procédure, puis répétez le chargement.

### Étape D — Produire le rapport

~~~sql
SELECT
    c.cours_id,
    c.titre_cours,
    COUNT(i.apprenant_id) AS nombre_inscriptions,
    COUNT(i.score) AS nombre_scores,
    AVG(i.score) AS moyenne_scores
FROM cours AS c
LEFT JOIN inscriptions AS i
    ON i.cours_id = c.cours_id
GROUP BY c.cours_id, c.titre_cours
ORDER BY c.cours_id;
~~~

Le rapport doit montrer trois inscriptions et deux scores connus pour SQL débutant, et une inscription et un score connu pour Modélisation. Les moyennes sont calculées sur les scores non NULL. Si les valeurs ne correspondent pas, inspectez les données avant de modifier le SQL.

### Étape E — Exécuter les tests négatifs

Vérifiez qu'une clé étrangère invalide, un couple d'inscription dupliqué, un score supérieur à 100 et un email dupliqué sont refusés. Capturez ou consignez les messages utiles sans enregistrer de secret. Vérifiez ensuite que les lignes rejetées n'ont pas été conservées.

### Étape F — Prouver le rollback

Mettez temporairement le score d'Amina pour SQL débutant à 84 dans une transaction, relisez la valeur, puis annulez. Vérifiez que le score revient à 82. Inscrivez dans le compte rendu les commandes et la postcondition observée.

### Étape G — Documenter le travail

Le README du laboratoire doit spécifier le moteur et la version, les préconditions, l'ordre des fichiers, la façon de se connecter, les requêtes à exécuter, les volumes attendus, les tests négatifs et le mécanisme de réinitialisation. Notez les divergences entre moteurs et les limites du scénario, notamment l'hypothèse d'une seule inscription par couple apprenant-cours.

### Critères de réussite

Le défi est réussi lorsque le laboratoire est reproductible par une autre personne, que les résultats attendus correspondent à l'état réel et que les contraintes rejettent les exemples invalides. Le rendu ne se limite pas à un fichier SQL : il inclut un environnement documenté, des données de test, des vérifications et une explication de ce qui est garanti et de ce qui ne l'est pas.

## 23. Checklist de fin de laboratoire

- Le moteur et sa version sont consignés.
- La base cible et le compte actif ont été vérifiés avant les modifications.
- Les scripts sont séparés et versionnés.
- Le schéma reflète les règles métier et les clés attendues.
- Les clés étrangères, contraintes UNIQUE, NOT NULL et CHECK ont été testées.
- Les données d'essai sont fictives et couvrent plusieurs cas.
- Les requêtes utilisent des colonnes explicites et des conditions lisibles.
- Les jointures respectent la granularité attendue.
- Les agrégations distinguent les lignes de toutes les valeurs non NULL.
- Les UPDATE et DELETE sont contrôlés par une condition vérifiée.
- Les transactions et le rollback ont été contrôlés par une postcondition.
- Les requêtes applicatives utilisent des paramètres au lieu d'une concaténation non sûre.
- Les différences PostgreSQL/MySQL sont notées.
- Les résultats et les anomalies sont documentés.
- La procédure de réinitialisation ne touche pas à des données réelles.
- Aucune clé, aucun mot de passe ou secret n'a été ajouté au dépôt.

## 24. Synthèse

Un bon laboratoire SQL est isolé, documenté et reproductible. Il commence par vérifier le moteur, la version, la base et le compte, puis crée le schéma en respectant les dépendances entre les tables. Il charge des données synthétiques, exécute des requêtes liées à des questions métier, teste les contraintes positives et négatives et contrôle les transactions par des résultats observés.

PostgreSQL et MySQL partagent une large base de SQL, mais certains outils, mécanismes d'identifiants, types et comportements DDL diffèrent. La portabilité exige donc de distinguer le SQL commun des extensions du moteur. Les scripts doivent être testés sur les versions réellement utilisées, et la documentation consultée doit correspondre à ces versions.

Les contraintes de base protègent les identifiants, les références, l'unicité et certaines plages de valeur. Elles doivent être complétées par les règles applicatives, les transactions, les tests, les permissions minimales, les sauvegardes et les procédures opérationnelles. En production, une migration ne se résume pas à exécuter CREATE TABLE : elle doit préserver les données existantes, être testée, être observable et posséder une stratégie de retour adaptée au moteur.

La compétence la plus importante est la méthode : poser une question, formuler une hypothèse, écrire une commande, prévoir le résultat, l'exécuter dans un environnement sûr et contrôler l'état réellement obtenu. Lorsqu'un résultat surprend, lisez l'erreur, réduisez le cas, vérifiez le contexte et testez une hypothèse. Cette discipline transforme des commandes SQL isolées en travail d'ingénierie fiable.

## Références techniques

- PostgreSQL, documentation officielle : https://www.postgresql.org/docs/current/
- PostgreSQL, contraintes de définition des données : https://www.postgresql.org/docs/current/ddl-constraints.html
- PostgreSQL, transactions : https://www.postgresql.org/docs/current/tutorial-transactions.html
- MySQL 8.4, référence officielle : https://dev.mysql.com/doc/refman/8.4/en/
- MySQL 8.4, contraintes de clés étrangères InnoDB : https://dev.mysql.com/doc/refman/8.4/en/innodb-foreign-key-constraints.html
- MySQL 8.4, transactions et contrôle de la concurrence : https://dev.mysql.com/doc/refman/8.4/en/commit.html
- OWASP, prévention des injections SQL : https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

Référez-vous à la documentation correspondant au moteur et à la version de votre environnement. Les scripts sont un support pédagogique à valider dans le laboratoire, et non un plan de migration prêt à exécuter en production.
