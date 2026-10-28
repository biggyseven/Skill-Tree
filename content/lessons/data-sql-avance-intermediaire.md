# Sous-requêtes, CTE, Procédures stockées — Intermédiaire

> **Mise en contexte.** L'application de formation Skill-Tree conserve les apprenants, les cours, les inscriptions et les résultats d'évaluation. Les premières requêtes SQL répondaient aux besoins courants, mais de nouveaux rapports demandent désormais des comparaisons avec une moyenne globale, des listes d'éléments sans activité, des classements et des parcours de prérequis. Plusieurs requêtes contiennent les mêmes calculs, certaines sont devenues difficiles à relire et des traitements sont copiés dans plusieurs endpoints de l'application. Pour garder des résultats cohérents, vous devez savoir composer des sous-requêtes, structurer des étapes avec des CTE et décider quand une procédure stockée est pertinente. Le but n'est pas de rendre le SQL plus complexe : il est de rendre le raisonnement explicite, testable et maintenable.

## 1. Objectifs pédagogiques

Ce cours prolonge les jointures, les agrégations, la normalisation et les travaux pratiques sur PostgreSQL et MySQL. Une sous-requête est une requête intégrée à une autre instruction. Une CTE (*Common Table Expression*) permet de nommer un résultat intermédiaire à l'intérieur d'une instruction avec WITH. Une procédure stockée est un objet exécutable enregistré dans la base, qui regroupe une logique procédurale autour d'opérations SQL.

À l'issue de cette leçon, vous devrez savoir :

- distinguer une sous-requête scalaire, une sous-requête de table et une sous-requête corrélée ;
- utiliser IN, EXISTS, NOT EXISTS, ANY et ALL lorsque leur sémantique correspond au besoin ;
- comprendre le comportement des sous-requêtes lorsqu'elles renvoient zéro, une ou plusieurs lignes ;
- éviter les pièges courants de NULL, de NOT IN et des comparaisons ;
- nommer des étapes SQL avec une CTE pour rendre une requête lisible ;
- composer plusieurs CTE en respectant leurs dépendances ;
- construire et limiter une CTE récursive pour parcourir une hiérarchie ;
- comprendre la différence entre une CTE, une table temporaire, une vue et une procédure stockée ;
- concevoir une procédure avec paramètres, contrôles, gestion d'erreur et droits adaptés ;
- distinguer les procédures et fonctions dans PostgreSQL et MySQL ;
- tester la logique SQL sur plusieurs cas, y compris les cas limites ;
- examiner la performance avec EXPLAIN, les statistiques et un jeu de données représentatif ;
- savoir quand garder la logique dans une requête ou dans l'application plutôt que d'ajouter une procédure.

La leçon emploie un mini-modèle de formation. Les exemples SQL courants sont volontairement proches des syntaxes prises en charge par les deux moteurs, mais les procédures stockées, les blocs de code, certaines fonctions et les options d'optimisation sont spécifiques au SGBD. Ne copiez pas un exemple PostgreSQL dans MySQL, ou l'inverse, sans adaptation et validation dans un environnement de laboratoire.

## 2. Jeu de données et hypothèses métier

Nous utilisons quatre tables : apprenants, cours, inscriptions et formateurs. Le modèle est volontairement proche des cours précédents.

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
    FOREIGN KEY (formateur_id) REFERENCES formateurs(formateur_id)
);

CREATE TABLE inscriptions (
    apprenant_id INTEGER NOT NULL,
    cours_id INTEGER NOT NULL,
    date_inscription DATE NOT NULL,
    score DECIMAL(5,2),
    PRIMARY KEY (apprenant_id, cours_id),
    FOREIGN KEY (apprenant_id) REFERENCES apprenants(apprenant_id),
    FOREIGN KEY (cours_id) REFERENCES cours(cours_id),
    CHECK (score IS NULL OR (score >= 0 AND score <= 100))
);
~~~

Dans cette version du modèle, un apprenant ne peut être inscrit qu'une seule fois à un cours. Le score est NULL avant l'évaluation ou compris entre zéro et cent. Chaque cours possède un formateur responsable unique. Ces hypothèses déterminent les clés et les résultats attendus ; si l'application autorise plusieurs sessions, plusieurs tentatives ou plusieurs formateurs par cours, il faut adapter le modèle avant de réutiliser les requêtes.

Un jeu d'essai simple :

~~~sql
INSERT INTO formateurs (formateur_id, nom_formateur) VALUES
    (7, 'Jules'),
    (8, 'Nadege'),
    (9, 'Ariane');

INSERT INTO apprenants (apprenant_id, nom_apprenant, email_apprenant) VALUES
    (10, 'Amina', 'amina@example.test'),
    (11, 'Samuel', 'samuel@example.test'),
    (12, 'Nadia', 'nadia@example.test'),
    (13, 'Mariam', 'mariam@example.test');

INSERT INTO cours (cours_id, titre_cours, formateur_id) VALUES
    (100, 'SQL debutant', 7),
    (200, 'Modelisation', 8),
    (300, 'Administration PostgreSQL', 9),
    (400, 'Bases avancees', 7);

INSERT INTO inscriptions (apprenant_id, cours_id, date_inscription, score) VALUES
    (10, 100, '2026-09-01', 82),
    (11, 100, '2026-09-02', 75),
    (12, 100, '2026-09-06', NULL),
    (10, 200, '2026-09-05', 91),
    (11, 200, '2026-09-08', 68),
    (13, 200, '2026-09-09', 87),
    (10, 400, '2026-09-12', 96);
~~~

Le cours 300 n'a aucune inscription. Mariam n'est inscrite qu'à Modélisation. Nadia possède une inscription sans score. Ces cas sont utiles pour valider les requêtes portant sur les absences, les NULL et les cours sans activité. Un jeu de test qui ne contient que des cas habituels ne révèle pas toujours les erreurs de logique.

## 3. Sous-requêtes : une requête à l'intérieur d'une autre

Une sous-requête est une instruction SQL intégrée dans une autre requête. Elle peut se trouver dans SELECT, FROM, WHERE ou HAVING selon sa forme et le moteur. Elle peut retourner une valeur unique, un ensemble de valeurs ou un ensemble de lignes et de colonnes. La position de la sous-requête indique souvent comment le résultat est consommé.

Les sous-requêtes sont puissantes parce qu'elles permettent de formuler un besoin en plusieurs niveaux. Par exemple, pour trouver les inscriptions dont le score est supérieur à la moyenne de toutes les notes connues, il faut calculer une moyenne puis la comparer aux inscriptions.

~~~sql
SELECT apprenant_id, cours_id, score
FROM inscriptions
WHERE score > (
    SELECT AVG(score)
    FROM inscriptions
);
~~~

La sous-requête calcule une valeur moyenne. La requête principale compare ensuite chaque score à cette valeur. Les valeurs NULL sont ignorées par AVG ; elles ne passent pas non plus la condition score > moyenne. Si la table ne contient aucun score connu, AVG renvoie NULL et la comparaison ne sera pas vraie pour les lignes. Le résultat doit donc être interprété selon les données présentes.

### 3.1 Sous-requête scalaire

Une sous-requête scalaire est utilisée dans un contexte qui attend une seule valeur. Elle doit renvoyer au plus une ligne et une colonne. Si elle renvoie une ligne avec une valeur NULL, la valeur obtenue est NULL ; si elle renvoie zéro ligne, le résultat est également traité comme une valeur absente dans les contextes appropriés. Si elle renvoie plusieurs lignes dans un contexte scalaire, le moteur renvoie normalement une erreur.

Exemple : chercher la moyenne des scores pour un cours donné et l'afficher à côté de chaque inscription de ce cours.

~~~sql
SELECT
    i.apprenant_id,
    i.cours_id,
    i.score,
    (
        SELECT AVG(i2.score)
        FROM inscriptions AS i2
        WHERE i2.cours_id = i.cours_id
    ) AS moyenne_du_cours
FROM inscriptions AS i
WHERE i.cours_id = 100;
~~~

La sous-requête utilise la valeur cours_id de la ligne externe. Elle calcule la moyenne du cours correspondant. C'est une sous-requête corrélée, car elle fait référence à une colonne de la requête principale.

### 3.2 Garantir un résultat scalaire

N'utilisez pas arbitrairement LIMIT 1 pour masquer une sous-requête qui renvoie plusieurs lignes. Le risque est de sélectionner une valeur arbitraire et de cacher un problème de modèle. Si plusieurs résultats sont possibles, décidez s'il faut agréger, imposer une règle d'unicité, utiliser IN/EXISTS ou ordonner explicitement pour sélectionner le premier élément selon un critère métier.

Par exemple, si vous voulez le score maximum d'un cours, exprimez l'intention par MAX(score), plutôt que d'écrire une sous-requête qui choisit une ligne sans règle claire :

~~~sql
SELECT
    c.cours_id,
    c.titre_cours,
    (
        SELECT MAX(i.score)
        FROM inscriptions AS i
        WHERE i.cours_id = c.cours_id
    ) AS meilleur_score
FROM cours AS c;
~~~

Le résultat est NULL pour un cours sans score connu. Cette valeur doit être interprétée comme « pas de score disponible », pas comme un score de zéro.

### 3.3 Sous-requête dans FROM

Une sous-requête utilisée comme source de lignes dans FROM est souvent appelée table dérivée. Elle doit recevoir un alias dans les moteurs courants concernés par ce cours. Son intérêt est de résumer un ensemble avant de le joindre à d'autres données.

~~~sql
SELECT
    c.cours_id,
    c.titre_cours,
    stats.nombre_inscriptions,
    stats.moyenne_score
FROM cours AS c
LEFT JOIN (
    SELECT
        cours_id,
        COUNT(*) AS nombre_inscriptions,
        AVG(score) AS moyenne_score
    FROM inscriptions
    GROUP BY cours_id
) AS stats
    ON stats.cours_id = c.cours_id
ORDER BY c.cours_id;
~~~

La table dérivée produit une ligne par cours qui possède au moins une inscription. LEFT JOIN conserve aussi les cours sans inscription. Pour le cours 300, stats.nombre_inscriptions et stats.moyenne_score sont NULL, car aucune ligne d'agrégat ne correspond. Si l'affichage doit montrer zéro inscription, on peut utiliser COALESCE(stats.nombre_inscriptions, 0). Il ne faut pas nécessairement remplacer la moyenne NULL par zéro : cela donnerait un sens mathématique incorrect.

### 3.4 Sous-requête dans HAVING

Une sous-requête peut aussi comparer un groupe à une valeur calculée sur d'autres groupes. Pour garder les cours dont le nombre d'inscriptions est supérieur au nombre moyen d'inscriptions par cours parmi les cours ayant au moins une inscription :

~~~sql
SELECT cours_id, COUNT(*) AS nombre_inscriptions
FROM inscriptions
GROUP BY cours_id
HAVING COUNT(*) > (
    SELECT AVG(nombre)
    FROM (
        SELECT COUNT(*) AS nombre
        FROM inscriptions
        GROUP BY cours_id
    ) AS compteurs
);
~~~

Il faut lire cette requête de l'intérieur vers l'extérieur. La table dérivée calcule d'abord un nombre par cours. La sous-requête scalaire calcule ensuite la moyenne de ces nombres. Enfin, la requête principale compare le compte de chaque cours à cette moyenne. Les cours sans inscription ne sont pas inclus dans cette moyenne parce que la première agrégation part d'INSCRIPTIONS ; si la question métier voulait les traiter comme zéro, le calcul devrait partir de COURS avec une jointure externe.

## 4. IN, EXISTS, ANY et ALL

Les opérateurs d'ensemble permettent d'exprimer des comparaisons par rapport à plusieurs valeurs sans devoir écrire un ensemble de OR à la main. Il faut choisir l'opérateur selon la question métier.

### 4.1 IN : appartenir à une liste ou à un résultat

Pour trouver les apprenants qui sont inscrits à au moins un cours enseigné par Jules :

~~~sql
SELECT apprenant_id, nom_apprenant
FROM apprenants
WHERE apprenant_id IN (
    SELECT i.apprenant_id
    FROM inscriptions AS i
    JOIN cours AS c ON c.cours_id = i.cours_id
    JOIN formateurs AS f ON f.formateur_id = c.formateur_id
    WHERE f.nom_formateur = 'Jules'
)
ORDER BY apprenant_id;
~~~

IN renvoie vrai lorsque la valeur recherchée correspond à l'une des valeurs du résultat. Il évite de reproduire toute la relation dans une longue liste de conditions. Cette sous-requête peut renvoyer plusieurs lignes, contrairement à une sous-requête scalaire.

### 4.2 NOT IN et le piège de NULL

NOT IN mérite une attention particulière. Si la liste de comparaison contient NULL et qu'aucune correspondance n'est trouvée, le résultat de NOT IN peut devenir UNKNOWN plutôt que TRUE. Une clause WHERE ne conserve que les expressions vraies ; le résultat peut donc être vide ou incomplet alors que la requête semble logique.

Exemple conceptuel à éviter si la colonne peut contenir NULL :

~~~sql
SELECT apprenant_id
FROM inscriptions
WHERE apprenant_id NOT IN (
    SELECT apprenant_id
    FROM autre_source
);
~~~

Si autre_source.apprenant_id contient une valeur NULL, l'effet de NOT IN peut être inattendu. Il faut comprendre la possibilité de NULL et choisir une expression qui correspond au besoin. Pour tester l'absence de correspondance, NOT EXISTS est souvent plus robuste, car il vérifie l'existence de lignes liées plutôt que de comparer une valeur à une liste potentiellement contaminée par NULL.

### 4.3 EXISTS : une ligne correspondante existe-t-elle ?

Pour obtenir les apprenants ayant au moins une inscription, utilisez EXISTS :

~~~sql
SELECT a.apprenant_id, a.nom_apprenant
FROM apprenants AS a
WHERE EXISTS (
    SELECT 1
    FROM inscriptions AS i
    WHERE i.apprenant_id = a.apprenant_id
)
ORDER BY a.apprenant_id;
~~~

EXISTS porte sur l'existence d'au moins une ligne. Le contenu du SELECT interne importe peu pour le test logique ; SELECT 1 est une convention de lecture courante. Le moteur peut arrêter la recherche dès qu'il a établi qu'une correspondance existe, selon son plan.

Pour trouver les apprenants qui n'ont encore aucune inscription :

~~~sql
SELECT a.apprenant_id, a.nom_apprenant
FROM apprenants AS a
WHERE NOT EXISTS (
    SELECT 1
    FROM inscriptions AS i
    WHERE i.apprenant_id = a.apprenant_id
)
ORDER BY a.apprenant_id;
~~~

Avec les données du laboratoire, Mariam peut apparaître dans la première requête puisqu'elle a une inscription à Modélisation ; pour tester NOT EXISTS, utilisez un apprenant ajouté sans inscription. Le cours 300 sert à vérifier la même logique côté cours.

### 4.4 ANY et ALL

ANY et ALL servent à comparer une expression à un ensemble de valeurs. La syntaxe exacte est à vérifier dans la documentation du moteur, mais le sens conceptuel est le suivant :
- comparaison avec ANY : la condition doit être vraie pour au moins une valeur ;
- comparaison avec ALL : la condition doit être vraie pour toutes les valeurs du résultat.

Exemple : retrouver les scores supérieurs à au moins un score du cours 200 :

~~~sql
SELECT apprenant_id, cours_id, score
FROM inscriptions
WHERE score > ANY (
    SELECT score
    FROM inscriptions
    WHERE cours_id = 200
      AND score IS NOT NULL
);
~~~

Pour exiger un score supérieur à tous les scores connus du cours 200 :

~~~sql
SELECT apprenant_id, cours_id, score
FROM inscriptions
WHERE score > ALL (
    SELECT score
    FROM inscriptions
    WHERE cours_id = 200
      AND score IS NOT NULL
);
~~~

Ces opérations sont sensibles aux NULL et à la cardinalité de l'ensemble. Les filtrer explicitement rend l'intention plus lisible lorsque la question concerne uniquement les scores connus. Si la sous-requête ALL renvoie zéro ligne, la condition est vraie de manière vacuement vraie selon la logique SQL des quantificateurs ; ce comportement peut surprendre et doit être pris en compte si l'ensemble peut être vide. Ne choisissez ANY ou ALL que si la formulation métier correspond réellement à « au moins une » ou « toutes ».

## 5. Sous-requêtes corrélées

Une sous-requête corrélée utilise une valeur de la requête externe. Elle est pratique pour exprimer un calcul par ligne, mais peut être moins lisible ou plus coûteuse selon le moteur et le volume des données. Il est faux d'affirmer qu'une sous-requête corrélée est toujours exécutée exactement une fois par ligne : l'optimiseur peut transformer la requête, la décorréler ou utiliser une stratégie différente. Il faut donc raisonner sur la sémantique et mesurer le plan réel.

### 5.1 Score supérieur à la moyenne du cours

~~~sql
SELECT
    i.apprenant_id,
    i.cours_id,
    i.score
FROM inscriptions AS i
WHERE i.score > (
    SELECT AVG(i2.score)
    FROM inscriptions AS i2
    WHERE i2.cours_id = i.cours_id
);
~~~

La requête compare chaque score à la moyenne des scores connus de son cours. Le filtre i2.cours_id = i.cours_id relie la sous-requête à la ligne extérieure. Sans ce filtre, chaque ligne serait comparée à la moyenne générale, ce qui répondrait à une autre question.

### 5.2 La plus récente inscription par apprenant

Dans le modèle courant, un apprenant ne peut avoir qu'une seule inscription à un cours, mais il peut avoir plusieurs cours. Nous pouvons trouver la date la plus récente par apprenant :

~~~sql
SELECT i.apprenant_id, i.cours_id, i.date_inscription
FROM inscriptions AS i
WHERE i.date_inscription = (
    SELECT MAX(i2.date_inscription)
    FROM inscriptions AS i2
    WHERE i2.apprenant_id = i.apprenant_id
);
~~~

Si un apprenant possède plusieurs inscriptions à la même date maximale, plusieurs lignes seront retournées. Ce comportement est souvent correct : toutes les lignes sont ex aequo. Si une seule ligne doit être sélectionnée, il faut choisir un second critère stable, par exemple un identifiant d'inscription ou un cours_id selon la règle métier, puis appliquer une fonction de classement ou un filtre déterministe.

### 5.3 Vérifier la granularité

Une sous-requête corrélée doit être évaluée avec la granularité de l'objet externe. La question « apprenants dont le score dépasse la moyenne du cours » n'est pas équivalente à « cours dont la moyenne dépasse une moyenne générale ». L'une compare les lignes d'inscription ; l'autre compare les agrégats des cours.

Avant d'écrire la requête, formulez une phrase : « une ligne de résultat représente… ». Ensuite, indiquez la clé de cette unité et décrivez comment les calculs internes sont reliés à elle. Cette discipline prévient de nombreux bugs d'agrégation et de sous-requêtes.

## 6. Common Table Expressions : structurer une requête avec WITH

Une CTE, ou expression de table commune, est un résultat nommé à l'intérieur d'une instruction. Elle commence généralement par WITH et peut être référencée dans la requête qui suit. Sa portée est limitée à cette instruction ; elle ne crée pas une table permanente et ne persiste pas après la fin de la requête.

Les CTE aident à donner des noms aux étapes d'un raisonnement. Plutôt que d'imbriquer plusieurs niveaux de parenthèses, vous pouvez préparer d'abord les scores connus, calculer ensuite les moyennes par cours et enfin joindre les résultats.

~~~sql
WITH scores_connus AS (
    SELECT apprenant_id, cours_id, score
    FROM inscriptions
    WHERE score IS NOT NULL
),
moyennes_cours AS (
    SELECT
        cours_id,
        AVG(score) AS moyenne_score,
        COUNT(*) AS nombre_scores
    FROM scores_connus
    GROUP BY cours_id
)
SELECT
    c.cours_id,
    c.titre_cours,
    m.moyenne_score,
    m.nombre_scores
FROM cours AS c
LEFT JOIN moyennes_cours AS m
    ON m.cours_id = c.cours_id
ORDER BY c.cours_id;
~~~

La première CTE nomme les lignes d'inscription possédant un score. La seconde agrège ces lignes par cours. La requête finale rattache les agrégats au catalogue, ce qui garde aussi les cours sans score. Cette structure permet au lecteur de comprendre le calcul par étapes.

### 6.1 Plusieurs CTE dépendantes

Une instruction WITH peut définir plusieurs CTE séparées par des virgules. Une CTE peut s'appuyer sur une CTE définie avant elle dans la même clause. Les noms doivent être distincts, et les dépendances doivent être organisées de façon cohérente.

~~~sql
WITH inscriptions_par_cours AS (
    SELECT cours_id, COUNT(*) AS nb_inscriptions
    FROM inscriptions
    GROUP BY cours_id
),
scores_par_cours AS (
    SELECT cours_id, AVG(score) AS moyenne_score
    FROM inscriptions
    GROUP BY cours_id
),
catalogue AS (
    SELECT
        c.cours_id,
        c.titre_cours,
        COALESCE(i.nb_inscriptions, 0) AS nb_inscriptions,
        s.moyenne_score
    FROM cours AS c
    LEFT JOIN inscriptions_par_cours AS i
      ON i.cours_id = c.cours_id
    LEFT JOIN scores_par_cours AS s
      ON s.cours_id = c.cours_id
)
SELECT *
FROM catalogue
WHERE nb_inscriptions >= 1
ORDER BY nb_inscriptions DESC, cours_id;
~~~

La CTE catalogue rassemble les informations nécessaires à l'affichage ; la requête finale applique le filtre et le tri. Dans les scripts de production, une liste explicite de colonnes est généralement préférable à SELECT * afin de rendre le contrat de sortie visible.

### 6.2 CTE ou table dérivée ?

Une table dérivée se trouve dans FROM et peut être utilisée pour nommer un sous-résultat local. Une CTE nomme le résultat au début de l'instruction. Les deux constructions peuvent parfois être substituables. Une CTE peut être référencée plusieurs fois dans la même instruction et peut être récursive, ce qu'une table dérivée classique ne fournit pas de la même manière.

Choisissez la construction la plus lisible, pas celle qui paraît la plus avancée. Une sous-requête courte avec une seule utilisation peut être plus simple. Une série de calculs métier en plusieurs étapes se prête souvent aux CTE parce que chaque étape a un nom et une responsabilité.

### 6.3 CTE n'est pas forcément plus rapide

Une CTE est d'abord un outil de structuration. Le moteur peut l'intégrer dans le plan global ou la traiter comme un résultat matérialisé, selon le SGBD, la version, la requête et les options. PostgreSQL a notamment des règles d'optimisation et des options de matérialisation pour certaines CTE non récursives ; MySQL possède également des stratégies d'optimisation et de matérialisation pour les CTE et les tables dérivées. Ces détails changent le plan et doivent être vérifiés dans la documentation de la version employée.

N'ajoutez pas une CTE en supposant automatiquement que la requête sera plus rapide. Si la performance importe, comparez les plans et les mesures, tout en vérifiant que le résultat est identique. La lisibilité est déjà une raison valable d'utiliser une CTE, même si le plan final reste proche de celui d'une requête imbriquée équivalente.

## 7. CTE récursives : parcourir une hiérarchie

Une CTE récursive permet de construire un ensemble en partant d'un cas initial puis en ajoutant des lignes reliées à celles déjà trouvées. Elle est utile pour les arbres et hiérarchies : organigrammes, catégories imbriquées, composants de produit ou graphe de prérequis de cours. Elle doit comporter un point de départ et une règle d'extension qui finit par s'arrêter.

Supposons une table de catégories :

~~~sql
CREATE TABLE categories (
    categorie_id INTEGER PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES categories(categorie_id)
);
~~~

Les lignes racines ont parent_id NULL. Une catégorie peut avoir plusieurs enfants, mais un seul parent dans ce modèle arborescent simple. Ce modèle ne représente pas tous les graphes possibles ; il est choisi pour démontrer la récursion.

Données illustratives :

~~~sql
INSERT INTO categories (categorie_id, nom, parent_id) VALUES
    (1, 'Data', NULL),
    (2, 'SQL', 1),
    (3, 'Modelisation', 1),
    (4, 'SQL avance', 2),
    (5, 'Administration', 1),
    (6, 'Sauvegarde', 5);
~~~

Pour parcourir tous les descendants de Data, utilisez une CTE récursive :

~~~sql
WITH RECURSIVE arbre AS (
    SELECT categorie_id, nom, parent_id, 0 AS niveau
    FROM categories
    WHERE categorie_id = 1

    UNION ALL

    SELECT c.categorie_id, c.nom, c.parent_id, a.niveau + 1
    FROM categories AS c
    JOIN arbre AS a
      ON c.parent_id = a.categorie_id
)
SELECT categorie_id, nom, parent_id, niveau
FROM arbre
ORDER BY niveau, categorie_id;
~~~

La partie initiale sélectionne la catégorie racine au niveau zéro. La partie récursive joint les enfants de chaque catégorie déjà trouvée et augmente le niveau. L'évaluation continue jusqu'à ce qu'aucune nouvelle ligne ne soit produite ou qu'une limite du moteur soit atteinte. Le résultat doit inclure Data elle-même ainsi que ses descendants.

### 7.1 Structure d'une récursion

~~~mermaid
flowchart TD
    A["Ancre : sélectionner la racine"] --> B["Jeu courant"]
    B --> C["Trouver les enfants reliés au jeu courant"]
    C --> D{"Nouvelles lignes ?"}
    D -- "Oui" --> B
    D -- "Non" --> E["Résultat complet"]
~~~

Le point de départ et la partie récursive doivent produire des colonnes compatibles en nombre et en types. UNION ALL conserve les lignes des étapes. Le moteur évalue le travail de façon itérative dans de nombreuses implémentations, même si le SQL est écrit de manière récursive. La récursion est un mécanisme de requête, pas une fonction qui s'appelle nécessairement elle-même comme un programme traditionnel.

### 7.2 Prévenir les cycles

Un graphe peut contenir un cycle si les contraintes métier ne garantissent pas une structure d'arbre. Par exemple, A peut être parent de B et B parent de A si l'application ne valide pas ces règles. Une requête récursive peut alors continuer à revisiter des nœuds jusqu'à l'atteinte d'une limite ou d'une erreur. Il faut concevoir la requête et le modèle pour empêcher ou détecter les cycles.

Des stratégies comprennent une limite de profondeur, une liste des identifiants déjà visités ou une syntaxe de détection de cycle spécifique au moteur lorsque celle-ci est disponible. Une limite de profondeur est une mesure de protection, mais elle ne prouve pas que le graphe est correct : elle peut simplement tronquer un parcours. La validation du modèle doit rester séparée de la protection contre une requête incontrôlée.

~~~sql
WITH RECURSIVE arbre AS (
    SELECT categorie_id, nom, parent_id, 0 AS niveau
    FROM categories
    WHERE categorie_id = 1

    UNION ALL

    SELECT c.categorie_id, c.nom, c.parent_id, a.niveau + 1
    FROM categories AS c
    JOIN arbre AS a
      ON c.parent_id = a.categorie_id
    WHERE a.niveau < 10
)
SELECT *
FROM arbre
ORDER BY niveau, categorie_id;
~~~

La limite à dix niveaux protège ce parcours pédagogique contre un arbre anormalement profond. Dans un système réel, choisissez une borne cohérente avec le domaine et surveillez si elle est atteinte. MySQL expose des limites de récursion configurables, tandis que PostgreSQL propose d'autres mécanismes et options suivant la version ; vérifiez la documentation du moteur concerné.

### 7.3 Pré-requis de cours et graphes

Les prérequis de formation peuvent former un graphe orienté. Si chaque cours possède au maximum un prérequis, une simple hiérarchie peut suffire. Si un cours peut avoir plusieurs prérequis, le modèle devient un graphe dirigé et la récursion doit tenir compte des chemins et des cycles. Une boucle de prérequis, telle que A exige B et B exige A, rendrait le parcours impossible à terminer logiquement pour un débutant qui doit commencer par l'un des deux.

La vérification d'un graphe de prérequis doit donc examiner les cycles, les racines accessibles et les identifiants manquants. La CTE peut aider à explorer le graphe, mais elle ne remplace pas la validation des règles lors de l'ajout d'une dépendance. La détection des cycles doit être testée sur des cas où un cycle est intentionnellement introduit dans un laboratoire isolé.

## 8. Sous-requêtes et CTE pour les opérations de modification

Les sous-requêtes et les CTE ne servent pas uniquement à SELECT. Selon le moteur et la syntaxe, elles peuvent participer à INSERT, UPDATE ou DELETE. Toute modification doit être préparée avec un périmètre explicite, un test sur les lignes ciblées et une vérification après écriture.

### 8.1 UPDATE à partir d'une agrégation

Supposons une table de synthèse de cours et un besoin de calculer le nombre d'inscriptions. Une méthode consiste à utiliser une CTE puis à joindre ce résultat à la table cible. La syntaxe exacte d'UPDATE avec FROM ou JOIN diffère selon le moteur ; il est préférable de conserver deux variantes explicites plutôt que prétendre avoir un script identique.

Exemple PostgreSQL :

~~~sql
WITH comptes AS (
    SELECT cours_id, COUNT(*) AS nb
    FROM inscriptions
    GROUP BY cours_id
)
UPDATE cours_resume AS r
SET nombre_inscriptions = comptes.nb
FROM comptes
WHERE comptes.cours_id = r.cours_id;
~~~

Exemple MySQL :

~~~sql
UPDATE cours_resume AS r
JOIN (
    SELECT cours_id, COUNT(*) AS nb
    FROM inscriptions
    GROUP BY cours_id
) AS comptes
  ON comptes.cours_id = r.cours_id
SET r.nombre_inscriptions = comptes.nb;
~~~

Ces variantes ne sont valables que si cours_resume existe et possède les colonnes indiquées. Elles illustrent les divergences de syntaxe ; elles ne font pas partie du schéma initial. Les tables de synthèse doivent être justifiées par un besoin, avoir une source de vérité et une stratégie de rafraîchissement claire.

### 8.2 DELETE basé sur NOT EXISTS

Supposons qu'une table de travail contienne des éléments importés et qu'on souhaite retirer de cette table de travail les références qui n'existent plus dans le catalogue. On peut utiliser NOT EXISTS :

~~~sql
DELETE FROM import_cours AS ic
WHERE NOT EXISTS (
    SELECT 1
    FROM cours AS c
    WHERE c.cours_id = ic.cours_id
);
~~~

Avant cette suppression, lancez un SELECT qui reprend la même condition et inspectez toutes les lignes ciblées. Dans une application réelle, il est possible qu'une référence absente soit précisément une anomalie qu'il faut conserver pour audit, mettre en quarantaine ou corriger plutôt que supprimer. Le choix doit être métier et documenté. Ne lancez pas une commande destructive sur une table de production sans contrôle, sauvegarde et validation.

### 8.3 CTE de modification et atomicité

PostgreSQL permet certaines formes de CTE qui exécutent une instruction de modification et exposent les lignes modifiées au reste de la requête via RETURNING. Ce comportement est une fonctionnalité du moteur et ne doit pas être supposé identique dans MySQL. Les modifications liées doivent aussi respecter les contraintes transactionnelles. Lorsque la portabilité compte, choisissez une conception explicite qui sépare les variantes et les tests plutôt que de masquer les différences.

## 9. Procédures stockées : principe et cas d'usage

Une procédure stockée est une routine enregistrée dans le SGBD et appelée explicitement. Elle peut prendre des paramètres, exécuter plusieurs instructions, appliquer des conditions, effectuer des contrôles et gérer certaines erreurs. Elle convient notamment à une opération transactionnelle réutilisée par plusieurs clients ou à une routine administrative encadrée.

Les procédures ne sont pas une réponse automatique à tout SQL répétitif. Il faut tenir compte de la maintenance, de la portabilité, du contrôle de version, des droits, des tests, de la visibilité de la logique et de la façon dont l'application gère les transactions. Une requête simple peut rester dans le code applicatif. Une procédure est plus intéressante quand elle exprime une opération de données cohérente, possède un contrat clair et peut être gérée avec les mêmes pratiques d'ingénierie que le reste du système.

### 9.1 Procédure, fonction, vue et CTE : différences

- **Sous-requête** : un bloc SQL imbriqué dans une instruction.
- **CTE** : un résultat nommé utilisable pendant une seule instruction.
- **Vue** : une définition de requête enregistrée sous un nom, généralement interrogée comme une relation ; son comportement précis dépend du moteur et du type de vue.
- **Table temporaire** : une table créée pour un usage temporaire selon une portée définie ; elle stocke des lignes au lieu de simplement nommer une étape logique de requête.
- **Fonction** : une routine pouvant être appelée dans une expression ou une requête et qui renvoie une valeur ou un ensemble selon sa définition.
- **Procédure stockée** : une routine appelée en tant qu'action, généralement avec CALL dans PostgreSQL et MySQL, capable d'organiser un processus avec paramètres et instructions.

Une procédure peut être le bon endroit pour appliquer un changement atomique et partagé par différents clients. Elle ne doit pas être créée simplement parce qu'un SELECT parait long. Une longue requête de lecture peut être rendue plus lisible avec des CTE sans pour autant devenir une routine.

### 9.2 Contrat d'une procédure

Avant de rédiger une procédure, spécifiez :
- son objectif et les données qu'elle modifie ;
- les paramètres d'entrée et de sortie ;
- les préconditions ;
- les contrôles métier et les contraintes qui protègent les données ;
- la sémantique transactionnelle ;
- les erreurs possibles et leur contrat de retour ;
- les droits nécessaires à l'appel ;
- les tests qui prouvent le succès et le rejet des cas invalides.

La procédure ne doit pas s'appuyer sur un nom d'utilisateur ou une valeur implicite sans le documenter. Les paramètres doivent être typés et validés selon les règles métier. Si la procédure dépend de l'heure, d'un contexte de session ou d'une configuration, notez-le et testez cette dépendance.

## 10. Exemple PostgreSQL : créer une procédure

PostgreSQL permet de définir une procédure avec CREATE PROCEDURE. Les procédures PL/pgSQL utilisent un bloc avec DECLARE facultatif, BEGIN et END, entouré d'un délimiteur de corps. Dans cet exemple, on crée une procédure qui inscrit un apprenant à un cours si les références existent et que le modèle n'interdit pas l'opération.

~~~sql
CREATE OR REPLACE PROCEDURE inscrire_apprenant(
    p_apprenant_id INTEGER,
    p_cours_id INTEGER,
    p_date_inscription DATE
)
LANGUAGE plpgsql
AS $proc$
BEGIN
    IF p_date_inscription IS NULL THEN
        RAISE EXCEPTION 'La date d inscription est obligatoire';
    END IF;

    INSERT INTO inscriptions (
        apprenant_id,
        cours_id,
        date_inscription,
        score
    )
    VALUES (
        p_apprenant_id,
        p_cours_id,
        p_date_inscription,
        NULL
    );
END;
$proc$;
~~~

L'appel se fait par CALL :

~~~sql
CALL inscrire_apprenant(13, 100, DATE '2026-10-01');
~~~

Avec les données du laboratoire, cette insertion doit réussir si le couple (13, 100) n'existe pas déjà. Si l'apprenant ou le cours n'existe pas, la clé étrangère doit rejeter l'opération. Si le couple existe, la clé primaire composée doit empêcher une deuxième inscription. Le code de la procédure n'a pas besoin de reproduire toutes les contraintes : le schéma reste une seconde ligne de défense.

Cet exemple est volontairement simple. Dans un système réel, les appels, les erreurs et la transaction doivent être gérés dans le contrat applicatif. En PostgreSQL, une procédure appelée dans un bloc de transaction explicite ne peut pas toujours exécuter des commandes de contrôle transactionnel ; les possibilités sont soumises aux règles de CALL et au contexte d'appel. Ne placez pas COMMIT ou ROLLBACK dans une routine sans avoir vérifié les conditions exactes de la documentation.

### 10.1 Renvoyer une valeur ou un état

Une procédure peut utiliser des paramètres de sortie selon les fonctionnalités du moteur, mais les usages et les conventions diffèrent. Pour un simple résultat calculé dans une expression, une fonction peut être plus naturelle. Une procédure appelée par une application pourrait, selon le pilote, communiquer le succès via le résultat de l'appel, une exception ou un paramètre OUT. Le contrat doit être précis pour que le client sache distinguer un succès, un rejet métier et une erreur technique.

### 10.2 Gestion des erreurs en PostgreSQL

PL/pgSQL permet un bloc EXCEPTION pour traiter certaines erreurs. Exemple pédagogique de gestion d'un doublon :

~~~sql
CREATE OR REPLACE PROCEDURE inscrire_apprenant_controle(
    p_apprenant_id INTEGER,
    p_cours_id INTEGER,
    p_date_inscription DATE
)
LANGUAGE plpgsql
AS $proc$
BEGIN
    INSERT INTO inscriptions (
        apprenant_id, cours_id, date_inscription, score
    )
    VALUES (
        p_apprenant_id, p_cours_id, p_date_inscription, NULL
    );

EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Une inscription existe deja pour ce couple';
END;
$proc$;
~~~

L'exemple montre que l'erreur est transformée en un message métier plus compréhensible. Dans une application de production, il faut soigneusement distinguer les violations d'unicité, de clé étrangère, les entrées invalides et les pannes techniques. Ne traduisez pas toutes les erreurs en « impossible de faire l'opération » sans conserver des informations diagnostiques suffisantes dans des journaux protégés.

Un gestionnaire d'exception peut modifier les frontières transactionnelles internes en PL/pgSQL ; ses effets exacts doivent être compris et testés. L'instruction doit rester cohérente même si la procédure échoue, et l'application doit savoir si elle peut réessayer ou si la requête est devenue invalide.

## 11. Exemple MySQL : procédure stockée avec paramètres

MySQL utilise une syntaxe différente pour les routines stockées. Dans un client interactif comme le client mysql, la commande DELIMITER change le séparateur utilisé par le client pour reconnaître la fin de la définition. DELIMITER n'est pas une instruction SQL envoyée au serveur ; elle est une commande du client.

~~~sql
DELIMITER //

CREATE PROCEDURE inscrire_apprenant(
    IN p_apprenant_id INTEGER,
    IN p_cours_id INTEGER,
    IN p_date_inscription DATE
)
BEGIN
    IF p_date_inscription IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La date d inscription est obligatoire';
    END IF;

    INSERT INTO inscriptions (
        apprenant_id,
        cours_id,
        date_inscription,
        score
    )
    VALUES (
        p_apprenant_id,
        p_cours_id,
        p_date_inscription,
        NULL
    );
END//

DELIMITER ;
~~~

Appel :

~~~sql
CALL inscrire_apprenant(13, 100, '2026-10-01');
~~~

Les paramètres IN indiquent les valeurs transmises à la procédure. MySQL prend également en charge les paramètres OUT et INOUT avec leurs règles propres. La déclaration des paramètres, les blocs, les gestionnaires d'erreur et les instructions de routine ne sont pas interchangeables avec PL/pgSQL. Testez cette procédure sur une instance MySQL 8.4 ou la version réellement ciblée.

La procédure doit respecter les mêmes contraintes de données que l'exemple PostgreSQL. Si l'inscription est dupliquée, la clé primaire doit rejeter l'opération ; si la référence n'existe pas, la clé étrangère doit la rejeter. Les contraintes de la table restent importantes même lorsque l'application utilise des routines stockées.

## 12. Paramètres, SQL dynamique et sécurité

Les paramètres de procédure doivent être utilisés comme des valeurs et non transformés en morceaux de code SQL. Le même principe de sécurité que pour les requêtes applicatives s'applique : une valeur externe ne doit pas être concaténée directement dans une instruction dynamique sans traitement adapté.

Un SQL dynamique peut être nécessaire lorsque le nom de l'objet ou une partie de la structure varie selon le besoin. Ce cas est plus délicat que le passage d'une simple valeur. Les marqueurs de paramètres peuvent protéger les valeurs, mais ils ne représentent généralement pas des noms de tables ou de colonnes. Il faut alors utiliser une liste blanche de noms autorisés, une validation stricte et les mécanismes de préparation adaptés au moteur.

La routine doit également être appelée avec des permissions appropriées. Dans un environnement où les procédures s'exécutent avec des droits différents de ceux de l'appelant, les options de sécurité du moteur doivent être examinées avec soin. N'utilisez pas un privilège élevé pour contourner un modèle d'accès mal défini. Vérifiez l'identité effective, les schémas accessibles et les objets que la routine peut lire ou modifier.

Les erreurs retournées aux utilisateurs ne devraient pas révéler des secrets, des noms de serveurs internes ou des détails sensibles. À l'inverse, les logs internes doivent conserver assez d'information pour diagnostiquer le problème. Une séparation entre message utilisateur et détail technique est souvent nécessaire.

## 13. Transactions et responsabilités d'une procédure

Une procédure stockée doit définir si elle participe à la transaction initiée par l'appelant ou si son architecture autorise certaines actions de transaction propres au moteur. Ce point est crucial quand l'opération inclut plusieurs insertions ou modifications qui doivent être réalisées ensemble.

Dans une application, le modèle courant est que le code appelant ouvre la transaction, invoque les opérations et valide ou annule selon le résultat. Cela rend la frontière transactionnelle visible côté applicatif, mais il existe d'autres architectures. Le choix dépend du besoin de réutilisation, des droits et des contraintes du moteur. Le contrat doit préciser qui possède la responsabilité de COMMIT et ROLLBACK.

PostgreSQL permet certaines opérations de contrôle transactionnel dans les procédures sous des conditions précises, notamment liées à l'appel au niveau supérieur et à l'absence d'un bloc de transaction englobant. Les fonctions ne disposent pas des mêmes possibilités. MySQL possède ses propres règles de procédures et de transactions, ainsi que des interactions avec certaines instructions DDL. Il ne faut donc jamais supposer qu'une routine peut valider ou annuler indépendamment son appel dans tous les contextes.

Un modèle de procédure de transfert de crédits, de commande ou de réservation doit inclure les contrôles de solde ou de disponibilité, éviter les courses concurrentes et garantir l'intégrité en cas d'erreur. Les exemples pédagogiques de ce cours ne constituent pas une implémentation complète d'un système de paiement. Pour une opération sensible, il faut une revue spécifique du verrouillage, de l'isolation, de l'idempotence, des erreurs et de la récupération.

## 14. Fonctions, procédures et vues : choisir la bonne abstraction

Une vue peut encapsuler une requête de lecture répétitive et présenter un contrat stable aux utilisateurs. Elle est adaptée lorsqu'on souhaite nommer et partager une projection relationnelle. Une CTE convient à une étape de calcul limitée à une instruction. Une fonction est pertinente lorsqu'on veut calculer ou retourner une valeur dans le cadre d'une expression ou d'un appel adapté au moteur. Une procédure convient à une action composée de plusieurs étapes.

Choisir une procédure pour chaque requête peut rendre l'application plus difficile à comprendre, particulièrement si la logique est répartie entre le code applicatif et la base sans séparation claire. À l'inverse, copier une logique métier critique dans cinq services augmente le risque que chaque service se comporte différemment. Le bon choix dépend des consommateurs, des responsabilités et du besoin de cohérence.

Avant de déplacer une logique dans le SGBD, demandez-vous :
- plusieurs clients doivent-ils exécuter exactement le même processus ?
- ce processus a-t-il un contrat de données stable ?
- nécessite-t-il des accès atomiques à plusieurs objets ?
- les tests, la revue et le déploiement des routines sont-ils gérés dans le dépôt et la CI ?
- l'équipe sait-elle diagnostiquer le comportement de la routine ?
- le couplage à un moteur spécifique est-il accepté ?
- la logique est-elle mieux exprimée en SQL ou requiert-elle un workflow applicatif complexe ?

Une procédure ne doit pas remplacer la séparation des responsabilités. L'application reste responsable du parcours utilisateur, du contexte de requête et de la gestion du retour ; la base protège l'intégrité des données et peut encapsuler les opérations qui ont intérêt à être communes.

## 15. Performance des sous-requêtes et des CTE

La lisibilité est un critère majeur, mais les requêtes doivent aussi respecter les objectifs de performance. Une sous-requête corrélée n'est pas intrinsèquement mauvaise ; une CTE n'est pas intrinsèquement rapide ; une jointure n'est pas toujours meilleure que EXISTS. Les optimisateurs modernes transforment de nombreux motifs SQL. Le résultat dépend de la version du moteur, des statistiques, de la taille des relations, des index, de la sélectivité et du plan choisi.

### 15.1 Comparer EXISTS et JOIN

Pour lister les cours qui possèdent au moins une inscription, EXISTS est une expression directe du besoin :

~~~sql
SELECT c.cours_id, c.titre_cours
FROM cours AS c
WHERE EXISTS (
    SELECT 1
    FROM inscriptions AS i
    WHERE i.cours_id = c.cours_id
);
~~~

Une jointure suivie de DISTINCT peut aussi donner les cours inscrits :

~~~sql
SELECT DISTINCT c.cours_id, c.titre_cours
FROM cours AS c
JOIN inscriptions AS i
  ON i.cours_id = c.cours_id;
~~~

Les résultats peuvent être équivalents sur ce besoin, mais la jointure génère conceptuellement une ligne par correspondance avant la déduplication. EXISTS exprime plus directement un test d'existence. Selon les données et l'optimiseur, les deux plans peuvent néanmoins être proches. Choisissez d'abord la forme qui correspond au sens du besoin, puis mesurez si nécessaire.

### 15.2 Sous-requête corrélée ou agrégation jointe

Pour comparer chaque score à la moyenne de son cours, on peut utiliser une sous-requête corrélée ou calculer la moyenne dans une CTE puis joindre cette moyenne à la table d'inscriptions.

Version corrélée :

~~~sql
SELECT i.apprenant_id, i.cours_id, i.score
FROM inscriptions AS i
WHERE i.score > (
    SELECT AVG(i2.score)
    FROM inscriptions AS i2
    WHERE i2.cours_id = i.cours_id
);
~~~

Version avec CTE :

~~~sql
WITH moyennes AS (
    SELECT cours_id, AVG(score) AS moyenne_score
    FROM inscriptions
    GROUP BY cours_id
)
SELECT i.apprenant_id, i.cours_id, i.score
FROM inscriptions AS i
JOIN moyennes AS m
  ON m.cours_id = i.cours_id
WHERE i.score > m.moyenne_score;
~~~

Les deux requêtes répondent au même besoin si les hypothèses et le traitement de NULL sont identiques. La CTE rend l'étape d'agrégation visible et peut faciliter sa réutilisation. La sous-requête peut être optimisée efficacement. Comparez les résultats et les plans sur un jeu de données représentatif avant de choisir selon la performance.

### 15.3 Index, statistiques et sélectivité

Un index sur inscriptions(cours_id) peut être utile aux requêtes qui filtrent ou joignent fréquemment sur cours_id. La clé primaire composée (apprenant_id, cours_id) possède un ordre de colonnes ; selon le moteur, cet index n'est pas nécessairement équivalent à un index commençant par cours_id. L'utilité d'un index doit donc être évaluée pour les prédicats réellement employés.

Les index coûtent de l'espace et ralentissent certaines écritures puisqu'ils doivent être maintenus. Les statistiques renseignent l'optimiseur sur les valeurs et la distribution. Une modification massive de données peut nécessiter une mise à jour des statistiques selon les mécanismes du moteur. N'ajoutez pas plusieurs index proches sans mesure et sans comprendre leurs interactions.

### 15.4 Protocole de comparaison

Quand vous comparez deux versions d'une requête :
1. validez qu'elles retournent le même résultat pour des cas ordinaires et limites ;
2. utilisez des données représentatives et notez le volume ;
3. exécutez les requêtes plusieurs fois dans des conditions comparables ;
4. consignez la latence et le plan d'exécution ;
5. vérifiez les lectures, les tris, la cardinalité et les attentes lorsque ces informations sont disponibles ;
6. évaluez l'impact des index et la charge concurrente ;
7. conservez la version qui est la plus claire et respecte les objectifs avec un coût global acceptable.

Ne tirez pas de conclusion universelle à partir d'un seul test en mémoire sur quelques lignes. Une différence insignifiante dans un environnement minuscule peut disparaître ou s'inverser sur une charge réelle.

## 16. Atelier pratique complet : tableau de bord des cours

### Mission

Vous devez produire une requête qui retourne, pour chaque cours, son titre, le nombre d'inscriptions, le nombre de scores connus, la moyenne et le meilleur score. Vous devez ensuite isoler les cours sans inscription, les apprenants au-dessus de la moyenne de leur cours et la hiérarchie des catégories. Enfin, vous créez une procédure d'inscription adaptée à PostgreSQL ou à MySQL.

### Étape 1 — Calculer les indicateurs par cours avec une CTE

~~~sql
WITH statistiques AS (
    SELECT
        cours_id,
        COUNT(*) AS nombre_inscriptions,
        COUNT(score) AS nombre_scores_connus,
        AVG(score) AS moyenne_score,
        MAX(score) AS meilleur_score
    FROM inscriptions
    GROUP BY cours_id
)
SELECT
    c.cours_id,
    c.titre_cours,
    COALESCE(s.nombre_inscriptions, 0) AS nombre_inscriptions,
    COALESCE(s.nombre_scores_connus, 0) AS nombre_scores_connus,
    s.moyenne_score,
    s.meilleur_score
FROM cours AS c
LEFT JOIN statistiques AS s
    ON s.cours_id = c.cours_id
ORDER BY c.cours_id;
~~~

La CTE produit des indicateurs seulement pour les cours qui ont des inscriptions. La jointure externe garde le catalogue complet. COALESCE transforme les compteurs absents en zéro, mais laisse la moyenne et le meilleur score à NULL lorsqu'aucun score ne peut être calculé. Cela respecte la différence entre « aucun résultat » et un résultat numériquement égal à zéro.

### Étape 2 — Retrouver les cours sans inscription

~~~sql
SELECT c.cours_id, c.titre_cours
FROM cours AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM inscriptions AS i
    WHERE i.cours_id = c.cours_id
)
ORDER BY c.cours_id;
~~~

Dans le jeu de données de l'atelier, cette requête doit retourner le cours 300. Si elle ne renvoie rien, inspectez le jeu de test : il est possible que le cours ait été inscrit lors d'une séance précédente. Le résultat dépend de l'état réel et non de la seule intention du cours.

### Étape 3 — Comparer chaque score à la moyenne du cours

~~~sql
WITH moyennes AS (
    SELECT cours_id, AVG(score) AS moyenne_score
    FROM inscriptions
    GROUP BY cours_id
)
SELECT
    a.nom_apprenant,
    c.titre_cours,
    i.score,
    m.moyenne_score
FROM inscriptions AS i
JOIN apprenants AS a
  ON a.apprenant_id = i.apprenant_id
JOIN cours AS c
  ON c.cours_id = i.cours_id
JOIN moyennes AS m
  ON m.cours_id = i.cours_id
WHERE i.score IS NOT NULL
  AND i.score > m.moyenne_score
ORDER BY c.cours_id, i.score DESC;
~~~

Le filtre score IS NOT NULL rend le traitement des notes explicite. Le cours sans score ne possède aucune moyenne exploitable et n'apparaît pas dans la CTE des moyennes, ce qui correspond au besoin de comparer uniquement les cours évalués.

### Étape 4 — Parcourir une hiérarchie de catégories

Créez les catégories de la section 7 puis exécutez la CTE récursive. Vérifiez le niveau de chaque catégorie : Data doit être au niveau zéro, SQL, Modélisation et Administration au niveau un, et SQL avancé et Sauvegarde au niveau deux.

Ajoutez une catégorie enfant pour confirmer que la requête l'inclut sans modifier le SQL. Dans un second jeu de test isolé, essayez d'introduire un cycle uniquement si le schéma et la stratégie de test le permettent, et démontrez comment la limite ou la détection de cycle empêche une exploration non contrôlée.

### Étape 5 — Créer puis appeler une procédure

Choisissez une seule variante du code de procédure de la section 10 ou 11, selon le moteur de votre laboratoire. Exécutez la définition, appelez-la avec un couple valide, puis essayez un couple inexistant et un couple déjà présent. Le premier cas doit réussir et les cas invalides doivent être refusés par les contraintes ou les validations appropriées.

N'exécutez pas les deux variantes dans la même base en espérant qu'elles soient portables. Les syntaxes sont différentes. Enregistrez le moteur et la version, car les comportements peuvent dépendre du moteur, du pilote et du contexte de transaction.

### Étape 6 — Vérifier la procédure

Après l'appel valide, relisez la ligne dans INSCRIPTIONS et confirmez les valeurs attendues. Après chaque appel qui échoue, vérifiez que l'état de la base est resté cohérent et déterminez si la transaction appelante nécessite un rollback. Testez également la manière dont l'application reçoit l'erreur et la façon dont le détail technique est journalisé sans exposer d'information sensible.

### Étape 7 — Mesurer

Comparez la requête du tableau de bord à une version contenant une sous-requête corrélée pour un même indicateur. Vérifiez l'équivalence des résultats, examinez EXPLAIN, puis consignez les hypothèses et mesures. Le petit jeu de données ne permet pas à lui seul de conclure sur la performance de production ; le but de ce premier test est d'apprendre la méthode d'observation.

~~~mermaid
flowchart TD
    A["Données et règles métier"] --> B["Calculs par cours avec CTE"]
    B --> C["Contrôle des cours sans activité"]
    C --> D["Comparaison des scores"]
    D --> E["Exploration récursive"]
    E --> F["Routine stockée")
    F --> G["Tests positifs et négatifs"]
    G --> H["Mesures et compte rendu"]
~~~

### Livrables de l'atelier

Le livrable doit contenir les scripts dans l'ordre d'exécution, les résultats attendus pour les données de laboratoire, les tests négatifs et leur résultat, la variante de procédure correspondant au moteur, les plans d'exécution observés et une brève conclusion sur la lisibilité et la performance. Ne joignez pas de mots de passe, de valeurs sensibles ni de captures issues d'une base de production.

## 17. Erreurs fréquentes et méthodes de diagnostic

### 17.1 La sous-requête renvoie plusieurs lignes

Une comparaison scalaire attend une valeur unique. Si le sous-SELECT renvoie plusieurs lignes, demandez-vous si la logique est incorrecte ou si l'opérateur doit être différent. Si la question demande une appartenance, utilisez IN ou EXISTS. Si elle demande une valeur de synthèse, utilisez un agrégat approprié. Si elle suppose une unicité métier, définissez et faites respecter la contrainte correspondante.

### 17.2 Résultat inattendu avec NOT IN

Vérifiez si la sous-requête contient NULL. Si l'objectif est l'absence de correspondance avec une relation, envisagez NOT EXISTS et reliez explicitement les clés. Testez un cas où la source contient un NULL et un cas où la source est vide ; ces exemples révèlent rapidement les différences de sémantique.

### 17.3 CTE récursive sans fin

Vérifiez la condition qui sélectionne les enfants, le point de départ, les relations du graphe et la présence de cycles. Ajoutez une protection de profondeur adaptée au domaine ou une détection explicite de cycles, puis testez le cas dans un laboratoire isolé. Une limite ne remplace pas la correction du modèle.

### 17.4 Procédure créée mais appel rejeté

Vérifiez le schéma ou la base dans laquelle la procédure est enregistrée, le nom exact, les types et le nombre de paramètres, les droits EXECUTE ou équivalents et la syntaxe de l'appel. Dans MySQL, souvenez-vous que DELIMITER est une commande du client pour définir la routine, pas une instruction envoyée telle quelle au serveur. Dans PostgreSQL, distinguez une procédure appelée par CALL d'une fonction appelée dans une expression ou avec SELECT.

### 17.5 Une CTE est lente

Ne supposez pas que le mot WITH est la cause. Examinez le plan, le nombre de références à la CTE, la sélectivité des filtres et les index. Selon le moteur et la version, le calcul peut être intégré au plan ou matérialisé. Testez une forme équivalente et comparez à données égales. La clarté reste une raison de garder une CTE lorsque la performance satisfait les objectifs.

## 18. Exercices d'application avec corrigés

### Exercice 1 — Scores supérieurs à la moyenne générale

Écrivez une requête qui retourne les inscriptions dont le score est supérieur à la moyenne des scores connus.

**Corrigé :**

~~~sql
SELECT apprenant_id, cours_id, score
FROM inscriptions
WHERE score > (
    SELECT AVG(score)
    FROM inscriptions
);
~~~

AVG ignore NULL. La comparaison ne garde que les lignes dont score est connu et supérieur à la moyenne. Si aucun score n'est connu, AVG renvoie NULL et aucun score ne satisfait la comparaison.

### Exercice 2 — Cours sans inscription

Écrivez une requête qui trouve les cours qui n'apparaissent pas dans INSCRIPTIONS.

**Corrigé :**

~~~sql
SELECT c.cours_id, c.titre_cours
FROM cours AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM inscriptions AS i
    WHERE i.cours_id = c.cours_id
);
~~~

NOT EXISTS exprime le test d'absence d'une ligne correspondante. Cette forme évite le piège classique de NOT IN lorsqu'une valeur NULL apparaît dans la liste comparée.

### Exercice 3 — Pourquoi la sous-requête scalaire échoue-t-elle ?

Une requête compare cours_id à une sous-requête qui sélectionne tous les cours. Elle provoque une erreur de sous-requête multi-lignes. Que faut-il faire ?

**Corrigé.** Il faut choisir l'opérateur correspondant au besoin. Pour tester l'appartenance, utiliser IN ; pour l'existence d'une ligne qui remplit une condition, utiliser EXISTS ; pour produire un unique nombre, utiliser un agrégat comme COUNT ou MAX. Ne masquer pas le défaut en ajoutant LIMIT 1 sans règle de sélection.

### Exercice 4 — Trouver les apprenants ayant une inscription

Écrivez la requête avec EXISTS, sans joindre directement INSCRIPTIONS dans la requête principale.

**Corrigé :**

~~~sql
SELECT a.apprenant_id, a.nom_apprenant
FROM apprenants AS a
WHERE EXISTS (
    SELECT 1
    FROM inscriptions AS i
    WHERE i.apprenant_id = a.apprenant_id
);
~~~

La requête retourne une ligne par apprenant parce que la requête principale lit APPRENANTS. Plusieurs inscriptions ne multiplient pas la ligne externe. C'est une raison fréquente de préférer EXISTS à une jointure suivie de DISTINCT.

### Exercice 5 — Construire deux étapes avec CTE

Créez une CTE qui calcule le nombre d'inscriptions par cours et affiche les cours qui ont au moins deux inscriptions.

**Corrigé :**

~~~sql
WITH comptes AS (
    SELECT cours_id, COUNT(*) AS nombre
    FROM inscriptions
    GROUP BY cours_id
)
SELECT cours_id, nombre
FROM comptes
WHERE nombre >= 2
ORDER BY cours_id;
~~~

La CTE nomme le résultat intermédiaire et la requête extérieure filtre le groupe déjà agrégé. Cette structure peut être plus claire que d'imbriquer le même calcul dans plusieurs endroits.

### Exercice 6 — Score comparé à la moyenne du cours

Expliquez pourquoi cette requête est corrélée et ce qu'il se passe si le filtre sur cours_id est retiré :

~~~sql
SELECT i.apprenant_id, i.cours_id, i.score
FROM inscriptions AS i
WHERE i.score > (
    SELECT AVG(i2.score)
    FROM inscriptions AS i2
    WHERE i2.cours_id = i.cours_id
);
~~~

**Corrigé.** La sous-requête fait référence à i.cours_id, attribut de la requête externe. Elle calcule une moyenne différente pour chaque cours. Sans la condition de corrélation, elle calcule la moyenne générale et compare chaque score à cette moyenne, ce qui répond à une autre question.

### Exercice 7 — Récursion et terminaison

Dans une CTE récursive qui parcourt une hiérarchie, pourquoi doit-on contrôler les cycles et la condition d'arrêt ?

**Corrigé.** Si chaque étape retrouve au moins une ligne déjà visitée et qu'aucune condition n'arrête le parcours, la récursion peut continuer jusqu'à une limite ou une erreur. Il faut garantir une structure acyclique ou détecter les cycles, définir le point de départ et vérifier que la règle d'extension se termine.

### Exercice 8 — Procédure ou CTE ?

Vous devez uniquement calculer la moyenne des scores par cours dans une seule requête de rapport. Faut-il créer une procédure stockée ?

**Corrigé.** Pas nécessairement. Une CTE peut nommer l'étape d'agrégation et garder le calcul dans une instruction lisible. Une procédure apporte un avantage quand une opération partagée, avec paramètres et plusieurs étapes ou contrôles, mérite un contrat d'exécution réutilisable. La complexité supplémentaire doit être justifiée.

### Exercice 9 — PostgreSQL et MySQL

Pourquoi les définitions de procédures présentées dans ce cours ne sont-elles pas interchangeables ?

**Corrigé.** PostgreSQL utilise notamment PL/pgSQL avec un corps délimité et des mécanismes d'exception propres à son langage. MySQL utilise sa syntaxe de routine, ses paramètres IN/OUT/INOUT, ses gestionnaires et le délimiteur de client pour écrire plusieurs instructions. La logique métier peut être semblable, mais la définition et plusieurs comportements sont spécifiques au moteur.

### Exercice 10 — Pourquoi une CTE n'est-elle pas toujours plus rapide ?

**Corrigé.** Une CTE apporte un nom et une structure logique, mais le moteur décide du plan et peut intégrer ou matérialiser le résultat selon les règles propres au SGBD. Les statistiques, les index, le nombre de références et la sélectivité comptent. Il faut mesurer avec EXPLAIN et comparer les résultats fonctionnels avant de retenir une optimisation.

### Exercice 11 — Prévenir une procédure dangereuse

Une procédure reçoit une valeur de filtre et la concatène dans une chaîne SQL dynamique. Quel risque et quelle mesure recommandez-vous ?

**Corrigé.** La concaténation peut permettre à une entrée de modifier la commande et d'introduire une injection SQL. Utilisez les paramètres de routine ou de requête pour les valeurs ; si un identifiant d'objet doit varier, choisissez-le dans une liste blanche et appliquez les mécanismes sécurisés de préparation propres au moteur. Limitez aussi les privilèges de la routine et journalisez les erreurs sans exposer de secrets.

### Exercice 12 — Mesurer correctement une optimisation

Vous avez remplacé une sous-requête par une CTE et constaté un temps plus faible sur une seule exécution. Est-ce suffisant pour conclure ?

**Corrigé.** Non. Comparez les résultats et les cas limites, utilisez une charge représentative, répétez les mesures dans des conditions comparables et inspectez les plans. Un seul essai peut être influencé par le cache ou la charge concurrente. Vérifiez la performance globale et la lisibilité du code avant de retenir le changement.

## 19. Défi final corrigé — construire un rapport analytique et une routine sûre

### Mission

Vous devez produire un mini-module de données qui fournit un rapport de synthèse par cours, détecte les cours sans inscription, trouve les scores supérieurs à la moyenne de leur cours et permet d'enregistrer une inscription par une procédure stockée. Le module doit préciser son moteur, les hypothèses, les préconditions et les tests.

### Étape A — Rapport avec CTE

~~~sql
WITH statistiques AS (
    SELECT
        cours_id,
        COUNT(*) AS nombre_inscriptions,
        COUNT(score) AS nombre_scores_connus,
        AVG(score) AS moyenne_score,
        MAX(score) AS meilleur_score
    FROM inscriptions
    GROUP BY cours_id
)
SELECT
    c.cours_id,
    c.titre_cours,
    COALESCE(s.nombre_inscriptions, 0) AS nombre_inscriptions,
    COALESCE(s.nombre_scores_connus, 0) AS nombre_scores_connus,
    s.moyenne_score,
    s.meilleur_score
FROM cours AS c
LEFT JOIN statistiques AS s
  ON s.cours_id = c.cours_id
ORDER BY c.cours_id;
~~~

**Correction attendue :** le rapport comprend tout le catalogue. Un cours sans inscription possède des compteurs affichés à zéro et une moyenne NULL. Un cours avec des inscriptions mais sans score connu possède un nombre de scores égal à zéro et une moyenne NULL. Les NULL ne doivent pas être confondus avec zéro.

### Étape B — Scores au-dessus de la moyenne par cours

~~~sql
WITH moyennes AS (
    SELECT cours_id, AVG(score) AS moyenne_score
    FROM inscriptions
    GROUP BY cours_id
)
SELECT
    a.nom_apprenant,
    c.titre_cours,
    i.score,
    m.moyenne_score
FROM inscriptions AS i
JOIN apprenants AS a
  ON a.apprenant_id = i.apprenant_id
JOIN cours AS c
  ON c.cours_id = i.cours_id
JOIN moyennes AS m
  ON m.cours_id = i.cours_id
WHERE i.score IS NOT NULL
  AND i.score > m.moyenne_score
ORDER BY c.cours_id, i.score DESC;
~~~

**Correction attendue :** chaque ligne représente une inscription avec un score supérieur à la moyenne de son cours. La CTE calcule les moyennes une fois dans l'expression logique, puis la requête les relie aux inscriptions. Le plan réel peut être transformé par l'optimiseur ; la syntaxe n'impose pas une stratégie physique particulière.

### Étape C — Choisir une procédure et documenter les différences

Implémentez une seule variante pour le moteur du laboratoire : PostgreSQL avec PL/pgSQL, ou MySQL avec CREATE PROCEDURE. Les paramètres d'entrée doivent être typés ; la procédure insère une inscription et laisse les contraintes de clé étrangère et de clé primaire protéger les références et l'unicité. Documentez qui démarre et termine la transaction et comment le client reçoit une erreur.

N'accordez pas de droits élevés pour rendre l'appel fonctionnel. L'utilisateur ou le rôle de l'application doit avoir le droit d'exécuter la routine et les permissions nécessaires selon le modèle choisi, mais pas devenir administrateur global par défaut. Les détails de sécurité des routines diffèrent entre moteurs et doivent être revus sur la version ciblée.

### Étape D — Matrice de tests

| Scénario | Résultat attendu |
|---|---|
| Appel avec apprenant et cours existants, couple inédit | Inscription ajoutée |
| Appel avec apprenant inexistant | Rejet par clé étrangère ou contrôle prévu |
| Appel avec cours inexistant | Rejet par clé étrangère ou contrôle prévu |
| Appel avec couple déjà inscrit | Rejet par clé primaire |
| Date absente si elle est interdite par le contrat | Rejet explicite |
| Erreur pendant une transaction enveloppante | État final cohérent après la gestion d'erreur |
| Appel sans droit d'exécution | Refus contrôlé, sans élévation silencieuse |
| Valeur hostile dans un paramètre texte | Traitée comme une donnée, jamais concaténée comme code SQL |

### Étape E — Vérifier la performance et la maintenabilité

Consignez le plan de requête, les données utilisées, le temps d'exécution mesuré et les limites du test. Comparez uniquement des variantes qui calculent le même résultat. Vérifiez aussi les plans lorsque les tables deviennent plus volumineuses, ou simulez une charge réaliste dans un environnement contrôlé. Ne prétendez pas avoir prouvé la performance de production sur sept lignes d'essai.

### Critères de réussite

Le défi est réussi si le rapport respecte la granularité choisie, les résultats sur les cas limites sont compris, la procédure fonctionne uniquement sur le moteur prévu, les erreurs sont traitées selon un contrat clair, les droits sont limités et les mesures sont reproductibles. Le livrable doit inclure les scripts, les résultats attendus, les tests négatifs et les références de version.

## 20. Checklist de maîtrise

- La sous-requête est choisie selon le nombre de valeurs et de lignes qu'elle peut renvoyer.
- Les comparaisons scalaires ne sont pas utilisées quand plusieurs lignes sont possibles.
- IN, EXISTS, NOT EXISTS, ANY et ALL reflètent l'intention métier.
- Les effets des NULL et de NOT IN ont été testés.
- La corrélation de chaque sous-requête est claire.
- La granularité du résultat est définie avant l'écriture.
- Les CTE ont des noms descriptifs et des responsabilités distinctes.
- Les dépendances entre CTE sont organisées sans référence ambiguë.
- La récursion possède un point de départ et une terminaison sûre.
- Les cycles éventuels sont contrôlés lorsque la structure n'est pas strictement arborescente.
- La matérialisation et le plan des CTE ne sont pas supposés universels.
- Les procédures ont un contrat, des paramètres typés et des erreurs explicites.
- La syntaxe du moteur et de sa version a été vérifiée.
- Les droits d'exécution et le contexte de sécurité sont contrôlés.
- Les limites transactionnelles sont documentées.
- Les valeurs externes ne sont pas concaténées arbitrairement dans du SQL dynamique.
- Les tests couvrent réussite, doublons, références manquantes, NULL et absence de lignes.
- Les performances sont mesurées sur des données représentatives.
- Les scripts et le résultat sont versionnés et reproductibles.

## 21. Synthèse finale

Les sous-requêtes permettent de comparer des lignes à une valeur calculée, à une liste ou à un résultat relationnel. Leur forme doit correspondre au besoin : une sous-requête scalaire doit produire au plus une valeur ; IN teste l'appartenance ; EXISTS et NOT EXISTS examinent l'existence ou l'absence d'une correspondance ; ANY et ALL expriment des comparaisons avec un ensemble. Les NULL, les sous-requêtes vides et les cardinalités doivent être testés explicitement.

Les CTE nomment des étapes de calcul au sein d'une instruction. Elles rendent souvent les requêtes analytiques plus faciles à lire et permettent des constructions récursives pour les hiérarchies et certains graphes. Elles ne sont pas automatiquement persistantes ni toujours plus rapides : le moteur choisit le plan d'exécution selon sa version, ses statistiques et ses règles d'optimisation.

Les procédures stockées regroupent une action exécutable avec paramètres et logique de contrôle. Elles peuvent centraliser un processus de données partagé, mais ajoutent un contrat, des besoins de test, des droits et un couplage au moteur. PostgreSQL et MySQL ont des syntaxes et comportements propres pour les procédures, la gestion d'erreur, les transactions et certaines fonctionnalités de modification.

La méthode professionnelle reste constante : écrire les hypothèses, garder la granularité visible, contrôler les cas limites, mesurer au lieu de deviner, limiter les droits et vérifier les postconditions. Les requêtes les plus maintenables ne sont pas nécessairement les plus courtes : elles sont celles dont le sens et les garanties peuvent être compris, testés et exploités par une autre personne.

## Références techniques

Les syntaxes et comportements peuvent varier selon les versions. Consultez les références correspondant au moteur qui exécute réellement vos scripts.

- PostgreSQL, WITH et requêtes récursives : https://www.postgresql.org/docs/current/queries-with.html
- PostgreSQL, CREATE PROCEDURE : https://www.postgresql.org/docs/current/sql-createprocedure.html
- PostgreSQL, CALL : https://www.postgresql.org/docs/current/sql-call.html
- PostgreSQL, gestion des transactions dans PL/pgSQL : https://www.postgresql.org/docs/current/plpgsql-transactions.html
- MySQL 8.4, CTE et requêtes récursives : https://dev.mysql.com/doc/refman/8.4/en/with.html
- MySQL 8.4, syntaxe des routines stockées : https://dev.mysql.com/doc/refman/8.4/en/stored-routines-syntax.html
- MySQL 8.4, CREATE PROCEDURE et CREATE FUNCTION : https://dev.mysql.com/doc/refman/8.4/en/create-procedure.html

Tous les scripts sont pédagogiques et doivent être exécutés dans un environnement de laboratoire. Avant un déploiement réel, examinez les privilèges, la taille des données, le comportement transactionnel, la syntaxe exacte de la version et la stratégie de migration.
