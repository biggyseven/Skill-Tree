# Indexation et plans d'exécution — Intermédiaire

> **Mise en contexte.** Le catalogue de Skill-Tree est devenu plus volumineux. Les pages qui listaient quelques cours et inscriptions étaient rapides pendant le développement, mais les rapports prennent maintenant plusieurs secondes, certaines requêtes consomment beaucoup de mémoire et une pointe de connexions ralentit toute l'application. Un développeur propose d'ajouter un index sur presque toutes les colonnes. Un autre conseille d'augmenter la mémoire du serveur sans diagnostic. Le DBA, lui, commence par poser une question mesurable : quelle requête est lente, sur quelles données, dans quelles conditions, et où son temps est-il dépensé ? Ce cours apprend à lire les plans d'exécution, choisir les index à partir des prédicats et de la sélectivité, interpréter les estimations du moteur et valider une optimisation sans dégrader les écritures.

## 1. Objectifs pédagogiques

Ce cours prolonge les sous-requêtes, les CTE et les procédures stockées. Vous connaissez maintenant les formes SQL qui expriment un besoin métier ; vous allez apprendre comment le SGBD décide d'exécuter ces requêtes et comment mesurer le résultat. L'objectif n'est pas de mémoriser une règle simpliste telle que « un index rend tout plus rapide ». Un index est une structure supplémentaire, avec un coût de stockage et de maintenance. Il est utile pour certains motifs d'accès, mais peut être ignoré par l'optimiseur ou ralentir les insertions, mises à jour et suppressions.

À la fin de la leçon, vous devrez être capable de :

- expliquer la différence entre une requête SQL logique et son plan d'exécution physique ;
- distinguer coût estimé, temps réellement observé, nombre de lignes estimé et nombre de lignes réel ;
- lire les opérations courantes d'un plan : parcours de table, parcours d'index, recherche par clé, jointure, tri et agrégation ;
- comprendre comment un index B-tree, un index composite et d'autres familles d'index peuvent aider une requête ;
- choisir l'ordre des colonnes d'un index composite en fonction des filtres, des jointures et du tri ;
- reconnaître les limites liées à la sélectivité, à la cardinalité et aux statistiques ;
- repérer les prédicats qui empêchent ou réduisent l'utilisation d'un index ;
- différencier l'indexation d'accès, l'indexation pour l'intégrité et les index redondants ;
- interpréter les plans d'exécution sous PostgreSQL et MySQL, en tenant compte des différences de syntaxe et de sortie ;
- mesurer les performances dans des conditions reproductibles ;
- optimiser une requête sans changer son résultat fonctionnel ;
- documenter l'impact d'un index sur le stockage et les écritures ;
- savoir quand l'index n'est pas la cause principale, par exemple en cas d'attente sur un verrou, de saturation du stockage ou d'un pool de connexions mal dimensionné.

Le contenu se concentre sur les index relationnels et les plans d'exécution de PostgreSQL et MySQL. Les moteurs ont des méthodes d'accès et des stratégies d'optimisation propres. Les exemples SQL sont pédagogiques ; leur disponibilité exacte et le détail de leur plan doivent être contrôlés dans la version réellement utilisée.

## 2. Environnement de laboratoire et modèle de travail

Pour examiner l'indexation, une table de trois lignes est généralement insuffisante. Avec peu de données, un parcours complet de table est souvent moins coûteux qu'un index, même si cet index sera utile dans un environnement plus volumineux. Nous allons donc travailler avec un modèle représentatif et raisonner sur la distribution des données. En production, une mesure sur un petit échantillon ne permet pas de garantir les performances à grande échelle.

Nous réutilisons un modèle de formation contenant apprenants, cours et inscriptions. Le principe essentiel est de définir une charge de travail : les requêtes importantes, leur fréquence, les filtres, les jointures, le tri, le nombre de lignes renvoyées et les objectifs de latence. L'indexation doit répondre à cette charge, pas à la simple existence de colonnes.

### 2.1 Modèle relationnel illustratif

~~~sql
CREATE TABLE apprenants (
    apprenant_id INTEGER PRIMARY KEY,
    nom_apprenant VARCHAR(120) NOT NULL,
    email_apprenant VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE cours (
    cours_id INTEGER PRIMARY KEY,
    titre_cours VARCHAR(160) NOT NULL,
    categorie VARCHAR(80) NOT NULL,
    actif BOOLEAN NOT NULL,
    date_publication DATE
);

CREATE TABLE inscriptions (
    apprenant_id INTEGER NOT NULL,
    cours_id INTEGER NOT NULL,
    date_inscription DATE NOT NULL,
    score DECIMAL(5,2),
    statut VARCHAR(20) NOT NULL,
    PRIMARY KEY (apprenant_id, cours_id),
    FOREIGN KEY (apprenant_id) REFERENCES apprenants(apprenant_id),
    FOREIGN KEY (cours_id) REFERENCES cours(cours_id),
    CHECK (score IS NULL OR (score >= 0 AND score <= 100))
);
~~~

Les types booléens et les détails de création peuvent varier selon les moteurs, mais la structure illustre les questions de requêtage. Dans une application réelle, les colonnes de statut peuvent être soumises à des contraintes supplémentaires, et la clé composée est valable uniquement si une seule inscription par apprenant et par cours est autorisée.

### 2.2 Définir des requêtes représentatives

Avant de créer un index, notez les requêtes utilisées par l'application. Par exemple :

1. chercher un apprenant à partir de son adresse électronique ;
2. lister les inscriptions d'un apprenant, triées par date ;
3. trouver les inscriptions d'un cours pour une période ;
4. filtrer les cours actifs d'une catégorie ;
5. produire le nombre d'inscriptions par cours ;
6. afficher les résultats supérieurs à un seuil pour un cours donné.

Les clés primaires et contraintes d'unicité donnent déjà souvent des index utiles au moteur. La question suivante est de savoir quelles autres structures accélèrent une requête importante sans alourdir inutilement les opérations d'écriture.

~~~mermaid
flowchart TD
    A["Charge de travail réelle"] --> B["Requêtes fréquentes et critiques"]
    B --> C["Mesurer et lire le plan"]
    C --> D["Formuler une hypothèse"]
    D --> E["Créer ou modifier un index ciblé"]
    E --> F["Mesurer de nouveau"]
    F --> G{"Gain utile sans régression ?"}
    G -- "Non" --> H["Revoir ou retirer le changement"]
    G -- "Oui" --> I["Documenter et surveiller"]
~~~

### 2.3 Conditions de test reproductibles

Consignez le moteur, la version, la configuration pertinente, le volume et la distribution des données, les paramètres des requêtes et l'heure du test. Faites la distinction entre une première exécution et des exécutions ultérieures qui peuvent bénéficier du cache. Si plusieurs sessions écrivent ou exécutent d'autres requêtes en même temps, la charge concurrente influence aussi les résultats.

Ne désactivez pas les protections de production, ne videz pas un cache partagé et ne lancez pas de requêtes coûteuses dans un service réel sans autorisation. Les mesures d'exécution réelle, les tests d'index et les opérations qui consomment beaucoup de ressources doivent être réalisés dans un environnement contrôlé autant que possible.

## 3. Comment le SGBD choisit-il un plan ?

Une requête SQL indique le résultat voulu, et non toujours l'ordre physique exact des opérations. L'optimiseur explore des alternatives possibles et choisit un plan selon ses estimations de coûts. Pour une requête qui filtre un cours puis rejoint ses inscriptions, le moteur peut commencer par le cours et rechercher les inscriptions correspondantes, ou parcourir un ensemble de lignes puis appliquer des filtres. Le choix dépend des statistiques, des index disponibles, de la taille des tables et des coûts estimés.

~~~mermaid
flowchart TD
    A["Instruction SQL"] --> B["Analyse syntaxique et validation"]
    B --> C["Réécriture et transformations possibles"]
    C --> D["Statistiques et estimations"]
    D --> E["Comparaison des plans candidats"]
    E --> F["Plan retenu"]
    F --> G["Exécution et accès aux données"]
    G --> H["Résultat observé"]
~~~

Le plan choisi n'est pas nécessairement intuitif à la lecture du SQL. Une jointure écrite en premier dans le texte n'est pas toujours exécutée en premier. Un index qui semble intéressant peut être moins efficace qu'un parcours plus large, par exemple si le filtre conserve une grande partie de la table. L'optimiseur raisonne sur le coût total estimé, et sa décision dépend en partie de la qualité de ses informations sur les données.

### 3.1 Coût estimé et temps réel

Un coût affiché par EXPLAIN est une estimation interne au moteur, pas un nombre de millisecondes directement comparables entre systèmes. PostgreSQL, par exemple, affiche des coûts dans des unités relatives fondées sur ses paramètres de coût ; MySQL présente les informations sous une autre forme, parfois avec des colonnes explicatives sur l'accès. Ne comparez pas directement un coût PostgreSQL et un coût MySQL comme s'il s'agissait d'une mesure temporelle commune.

Lorsque l'outil fournit des mesures d'exécution réelle, comparez notamment le nombre de lignes estimé au nombre de lignes observé, le temps passé dans les étapes, les boucles, les accès aux blocs ou les lectures, selon la sortie disponible. Un grand écart entre l'estimation et le réel peut indiquer des statistiques insuffisantes, une distribution inhabituelle ou une dépendance entre colonnes que le modèle statistique décrit mal.

Le temps total inclut parfois les attentes : accès au stockage, verrou, connexion, ressource CPU ou réseau. Un plan ne montre pas toujours toutes les causes de latence. Les métriques du serveur et de l'application doivent compléter l'analyse lorsque le plan seul ne suffit pas.

### 3.2 Opérations courantes d'un plan

- **Parcours séquentiel de table** : le moteur lit la table ou un large ensemble de ses pages. Ce n'est pas automatiquement mauvais ; il peut être efficace pour une table petite ou un filtre peu sélectif.
- **Parcours d'index** : le moteur utilise une structure d'index pour identifier des lignes ou des plages de clés.
- **Recherche par clé** : le moteur accède à une ligne en utilisant une clé très restrictive, selon le moteur et le type d'index.
- **Nested loop** : une opération de jointure parcourt un côté et recherche les correspondances dans l'autre. Elle peut être efficace si l'entrée externe est petite et que l'accès interne est bon.
- **Hash join** : le moteur construit une structure de hachage sur un côté puis recherche les correspondances. Il peut être efficace pour de grandes jointures, mais consomme des ressources mémoire et peut impliquer des opérations temporaires.
- **Merge join** : les entrées sont exploitées dans un ordre compatible, souvent après un tri ou grâce à un accès ordonné.
- **Sort** : les lignes sont triées selon un ordre demandé ou requis par une étape.
- **Aggregate** : le moteur calcule des sommes, comptes, moyennes ou autres agrégations.
- **Filter** : les lignes qui ne satisfont pas une condition sont écartées à une étape du plan.

Les intitulés exacts varient et toutes ces opérations ne figurent pas dans chaque plan. L'important est de relier les étapes à la requête et au nombre de lignes qu'elles consomment et produisent.

## 4. À quoi sert un index ?

Un index est une structure supplémentaire qui aide le moteur à retrouver certaines lignes sans examiner systématiquement toute la table. Un index peut aussi fournir un ordre utile ou couvrir les colonnes nécessaires à une requête selon le moteur. L'index le plus adapté dépend de l'opérateur de comparaison, de la distribution des valeurs, de la fréquence des accès et des coûts de maintenance.

Une analogie consiste à comparer une table volumineuse à un livre et l'index à un index alphabétique : au lieu de parcourir toutes les pages, on utilise une structure permettant d'atteindre une zone pertinente. Mais cette analogie a des limites. Une base de données doit maintenir l'index lors des insertions et des changements, coordonner l'accès concurrent, et parfois lire les pages de données même après avoir trouvé l'entrée dans l'index.

### 4.1 B-tree

Les index de type B-tree sont couramment utilisés pour l'égalité, les plages de valeurs et certains tris. Par exemple, un index sur date_inscription peut aider une requête qui cherche une période. Il peut également être utile lorsqu'une requête trie sur cette colonne dans un ordre compatible et que le moteur estime que parcourir l'index est moins coûteux.

PostgreSQL utilise B-tree comme type d'index par défaut. MySQL/InnoDB utilise des index B-tree pour de nombreux cas d'usage de ses index secondaires et de sa clé primaire. Les détails internes diffèrent : ne supposez pas que les coûts, le stockage, les accès à la ligne et l'utilisation des index sont identiques.

### 4.2 Hash et autres familles d'index

Certains moteurs offrent des index de hachage ou des structures spécialisées pour certains types de données. Les index hash conviennent principalement aux recherches d'égalité dans les moteurs et configurations qui les prennent en charge ; ils ne remplacent pas un B-tree lorsqu'il faut parcourir une plage ordonnée. PostgreSQL offre plusieurs types d'index, notamment B-tree, Hash, GiST, SP-GiST, GIN et BRIN. MySQL propose différentes capacités selon le moteur de stockage et les types d'index pris en charge.

Les index spécialisés doivent être choisis en fonction de l'opérateur réellement exécuté. Un index adapté à un texte intégral ou à une donnée géospatiale n'est pas automatiquement meilleur pour une comparaison numérique ordinaire. La documentation du moteur doit confirmer les types disponibles, les opérateurs pris en charge et les limites de chaque structure.

### 4.3 Index et intégrité

Une clé primaire ou une contrainte UNIQUE est généralement soutenue par une structure d'index ou un mécanisme équivalent qui permet au moteur de vérifier l'unicité. Cet index peut aussi accélérer certaines recherches. Les index de clés étrangères ne sont pas automatiquement créés de la même façon dans tous les moteurs : PostgreSQL ne crée pas automatiquement un index sur toutes les colonnes référençantes d'une clé étrangère, alors que les comportements et exigences d'InnoDB diffèrent pour les index des colonnes enfants. Vérifiez les règles du moteur cible.

Ne créez pas un doublon d'index sans examiner ceux déjà produits par les clés primaires et les contraintes UNIQUE. Un index additionnel qui couvre exactement la même clé et le même ordre peut apporter peu de bénéfice et augmenter le coût d'écriture et le stockage.

~~~mermaid
flowchart TD
    A["Prédicat WHERE"] --> B["Estimer les lignes candidates"]
    B --> C{"Proportion de lignes retenues"}
    C -- "Très faible" --> D["Index potentiellement utile"]
    C -- "Très élevée" --> E["Parcours large parfois moins coûteux"]
    D --> F["Vérifier les accès aux lignes"]
    E --> F
    F --> G["Confirmer avec EXPLAIN et mesures"]
~~~

## 5. Sélectivité et cardinalité

La sélectivité exprime dans quelle mesure un prédicat réduit l'ensemble de lignes candidates. Un filtre qui conserve une seule ligne sur un million est très sélectif. Un filtre qui conserve presque toutes les lignes est peu sélectif. Le terme cardinalité peut avoir plusieurs usages dans les discussions sur les bases ; pour le plan d'exécution, il désigne notamment l'estimation du nombre de lignes à une étape donnée. Il faut être précis dans son contexte.

Supposons une table de plusieurs millions d'inscriptions. Rechercher un email unique par une contrainte UNIQUE est un cas très sélectif. Filtrer sur un statut qui vaut « actif » pour 95 % des lignes peut ne pas réduire assez les données pour justifier un accès par index seul. Le moteur peut préférer parcourir une grande partie de la table.

Le raisonnement dépend également du coût de retrouver les lignes de données après le parcours de l'index. Si le moteur doit lire des pages dispersées pour beaucoup de résultats, les accès peuvent devenir coûteux. Un index peut identifier des entrées efficacement tout en nécessitant de nombreuses lectures supplémentaires des lignes correspondantes.

### 5.1 Distribution uniforme et distribution asymétrique

Une colonne peut posséder beaucoup de valeurs distinctes mais une distribution très déséquilibrée. Par exemple, 90 % des inscriptions peuvent avoir le statut « actif », tandis que 10 % seulement sont « annulé ». Un index sur statut ne présente pas nécessairement le même intérêt pour les deux prédicats. L'optimiseur s'appuie sur des statistiques pour estimer les fréquences, selon ce qu'il sait de la distribution.

Si les statistiques ne reflètent pas la réalité, le moteur peut estimer une faible proportion de lignes alors que le filtre en retourne la majorité, ou inversement. L'écart peut influencer le choix de l'index, de la jointure et des opérations intermédiaires. Pour diagnostiquer, comparez estimations et lignes réelles lorsqu'elles sont disponibles, vérifiez la date et la mise à jour des statistiques et examinez les valeurs fréquentes.

### 5.2 Pourquoi le plus grand nombre de valeurs distinctes n'est pas la seule règle

Une colonne à nombreuses valeurs distinctes peut être utile pour un index, mais cela ne suffit pas. La requête peut ne jamais filtrer sur cette colonne, utiliser une fonction qui rend l'index peu applicable, ou renvoyer une grosse proportion de table. À l'inverse, une colonne avec moins de valeurs peut parfois être utile en combinaison avec une autre colonne dans un index composite, ou lorsque les requêtes utilisent un sous-ensemble précis des données.

Ne partez donc pas d'une règle telle que « indexer toutes les colonnes uniques » ou « ne jamais indexer une colonne à faible cardinalité ». Recueillez les requêtes, les distributions, les volumes et les plans. L'objectif est d'optimiser la charge globale.

## 6. Créer un index simple et tester son effet

Un index secondaire peut être créé avec CREATE INDEX. Exemple :

~~~sql
CREATE INDEX idx_inscriptions_date
ON inscriptions(date_inscription);
~~~

La requête suivante est candidate à l'utilisation de cet index :

~~~sql
SELECT apprenant_id, cours_id, date_inscription, score
FROM inscriptions
WHERE date_inscription >= DATE '2026-09-01'
  AND date_inscription < DATE '2026-10-01'
ORDER BY date_inscription;
~~~

Une plage de dates peut être adaptée à un index B-tree sur date_inscription. Néanmoins, l'optimiseur peut choisir un autre plan si la période couvre une grande part des données, si la table est petite ou si les statistiques indiquent que le parcours de table coûte moins cher. L'existence de l'index ne garantit pas son utilisation.

### 6.1 Mesurer avant et après

Une méthode de comparaison efficace :
1. sauvegarder la requête exacte et les paramètres ;
2. mesurer le plan et le temps avant l'index ;
3. créer l'index dans le laboratoire ;
4. actualiser les statistiques si la démarche du moteur le nécessite ;
5. mesurer la même requête dans des conditions comparables ;
6. comparer le résultat, le plan, les lignes traitées, les lectures disponibles et la latence ;
7. observer le coût de création et l'effet sur les écritures ;
8. décider de conserver l'index, de le modifier ou de le retirer.

Un test avant/après doit éviter de confondre les gains de l'index avec les effets du cache, de la charge concurrente ou de la distribution de données. Répétez les mesures et consignez les limites. Ne créez pas puis ne supprimez pas un index sur la production pour essayer une idée sans revue ni plan d'opération.

### 6.2 Parcours d'index et accès à la ligne

Dans de nombreux cas, l'index contient les clés et des références permettant de retrouver les lignes. Le moteur peut donc effectuer une recherche dans l'index puis accéder à la table pour obtenir les colonnes restantes. Si beaucoup de lignes correspondent et que les lignes sont dispersées sur les pages, le coût des accès à la table peut être important.

Certains moteurs peuvent satisfaire une requête directement à partir de l'index lorsque les colonnes nécessaires y sont disponibles et que les conditions de visibilité ou de stockage le permettent. Les index couvrants seront examinés plus loin. Un plan qui utilise un index n'est donc pas automatiquement optimal : il faut étudier aussi les accès qui suivent.

## 7. Index composites : plusieurs colonnes dans une même structure

Un index composite porte sur plusieurs colonnes dans un ordre défini. Il peut être utile aux requêtes qui filtrent ou trient sur une combinaison de ces colonnes. L'ordre des colonnes est crucial : un index sur (apprenant_id, date_inscription) n'est pas équivalent à un index sur (date_inscription, apprenant_id).

Supposons que l'application affiche l'historique d'un apprenant, trié par date :

~~~sql
SELECT cours_id, date_inscription, score
FROM inscriptions
WHERE apprenant_id = 10
ORDER BY date_inscription DESC;
~~~

Un index sur (apprenant_id, date_inscription) peut aider le moteur à localiser les inscriptions de l'apprenant et fournir un ordre compatible avec la date, selon le moteur, le sens de parcours et les autres colonnes de la requête.

### 7.1 Le principe du préfixe gauche

Pour de nombreux index composites B-tree, l'ordre des colonnes détermine les prédicats que l'index peut exploiter efficacement. Un index sur (apprenant_id, date_inscription) est généralement bien adapté aux conditions qui commencent par apprenant_id, éventuellement suivies d'une plage sur date_inscription. Il n'est pas équivalent à un index sur date_inscription seul pour les requêtes qui filtrent uniquement sur la date.

~~~mermaid
flowchart TD
    A["Index composite (apprenant_id, date_inscription)"] --> B["Filtre apprenant_id"]
    B --> C["Puis date_inscription"]
    A --> D["Filtre date_inscription seule"]
    D --> E["Le préfixe attendu manque"]
    E --> F["Index éventuellement peu utile pour ce prédicat"]
~~~

Le principe du préfixe gauche est une règle utile pour comprendre les index composites B-tree dans de nombreux scénarios ; les moteurs et leurs versions peuvent posséder des optimisations spécifiques. Ne l'appliquez pas comme une loi universelle à tous les types d'index. Vérifiez le plan réel.

### 7.2 Choisir l'ordre des colonnes

Imaginez ces deux requêtes :
- afficher les inscriptions d'un apprenant, triées par date ;
- afficher toutes les inscriptions comprises dans une période, quel que soit l'apprenant.

L'index (apprenant_id, date_inscription) semble pertinent pour la première. L'index (date_inscription, apprenant_id) pourrait mieux convenir à la seconde. Il ne faut pas créer automatiquement les deux : mesurez les deux usages, leur fréquence et le coût de maintenance associé. Des index composites supplémentaires augmentent la taille et le coût des insertions et mises à jour.

Une méthode pratique consiste à commencer par les conditions d'égalité les plus structurantes, puis à examiner les prédicats de plage et les besoins d'ordre. Cette méthode n'est qu'un point de départ : la distribution réelle, l'ordre de tri, les colonnes retournées et le plan global peuvent justifier un autre choix.

### 7.3 Index composites et contraintes

Une clé primaire composite fournit souvent un index dont les colonnes sont ordonnées selon la définition de la clé. Il peut soutenir certaines requêtes ; toutefois, l'ordre de la clé détermine les accès possibles. Dans notre modèle, PRIMARY KEY (apprenant_id, cours_id) aide naturellement les recherches qui commencent par apprenant_id, mais une requête filtrant uniquement sur cours_id peut nécessiter un index distinct pour être efficace.

Avant d'ajouter un index, examinez les structures existantes. Un index avec les mêmes colonnes principales dans le même ordre peut être redondant, sauf si des différences de colonnes incluses, de condition, de type ou d'option lui donnent un rôle distinct.

## 8. Index couvrants et colonnes retournées

Un index couvrant contient les données nécessaires pour répondre à une requête donnée sans devoir accéder systématiquement à la table de base, sous réserve des mécanismes du moteur. Les détails diffèrent : PostgreSQL permet des colonnes INCLUDE dans certains index B-tree, tandis que MySQL/InnoDB peut répondre à certaines requêtes à partir des informations conservées dans l'index secondaire ou primaire.

Exemple de requête :

~~~sql
SELECT score
FROM inscriptions
WHERE apprenant_id = 10
  AND cours_id = 100;
~~~

La clé primaire (apprenant_id, cours_id) identifie déjà la ligne. Selon le moteur et l'organisation du stockage, la requête peut lire les valeurs nécessaires par le chemin d'accès fourni par la clé primaire. Ajouter un index identique serait redondant. Il faut examiner les index existants avant de créer une structure supplémentaire.

Si un écran lit fréquemment date_inscription et score par apprenant, un index composite peut éventuellement couvrir ces colonnes, mais il faut évaluer la taille accrue et le coût des mises à jour de score. Un index trop large peut consommer beaucoup d'espace et amplifier les écritures. Un index couvrant répond à un motif de requête précis ; ce n'est pas une raison pour copier toute la ligne dans un index.

La clé primaire (apprenant_id, cours_id) permet de retrouver l'inscription, mais elle ne contient pas score. PostgreSQL devra normalement accéder à la ligne de table pour lire score si cette colonne n'est pas incluse dans l'index ; InnoDB organise la table selon sa clé primaire, ce qui donne un comportement différent pour l'accès aux autres colonnes. Ce contraste illustre pourquoi le plan et les propriétés du moteur doivent être vérifiés plutôt que transposés mécaniquement d'un SGBD à l'autre.

Exemple propre à PostgreSQL :

~~~sql
CREATE INDEX idx_inscriptions_apprenant_date
ON inscriptions (apprenant_id, date_inscription DESC)
INCLUDE (score, cours_id);
~~~

Cette syntaxe est spécifique à PostgreSQL et aux types d'index qui prennent en charge INCLUDE. Pour MySQL, la stratégie d'index couvrant doit se construire selon les règles d'InnoDB et la définition de l'index, sans recopier cette syntaxe. Les colonnes incluses et leur stockage doivent être évalués avec le plan et la taille réelle.

## 9. Index partiels et index fonctionnels : différences de moteur

Un index partiel indexe seulement les lignes qui satisfont une condition, lorsqu'un moteur prend en charge cette capacité. Il peut réduire la taille d'un index si les requêtes portent régulièrement sur un sous-ensemble stable. PostgreSQL prend en charge les index partiels. Les possibilités de MySQL diffèrent ; des colonnes générées, expressions indexées ou autres modèles peuvent être adaptés à certains cas, mais ils ne sont pas équivalents à toutes les formes d'index partiel.

Exemple PostgreSQL : créer un index sur les inscriptions qui n'ont pas encore de score.

~~~sql
CREATE INDEX idx_inscriptions_sans_score
ON inscriptions (date_inscription)
WHERE score IS NULL;
~~~

Cette structure est spécifique à PostgreSQL. Elle ne sera utile que pour les requêtes dont le prédicat est compatible avec la condition de l'index, et si le gain mesuré justifie le coût. Le moteur doit pouvoir prouver que la requête peut utiliser ce sous-ensemble. Un index partiel n'est pas une simple façon de déclarer une règle métier ; il ne remplace pas CHECK, NOT NULL ou les contraintes référentielles.

### 9.1 Index sur expression

Une requête qui applique une fonction à une colonne peut rendre un index ordinaire moins directement applicable. Par exemple :

~~~sql
SELECT apprenant_id
FROM apprenants
WHERE LOWER(email_apprenant) = LOWER('AMINA@example.test');
~~~

Un index ordinaire sur email_apprenant n'est pas nécessairement suffisant pour optimiser la comparaison telle qu'elle est écrite. PostgreSQL propose des index sur expression, par exemple :

~~~sql
CREATE INDEX idx_apprenants_email_lower
ON apprenants (LOWER(email_apprenant));
~~~

MySQL permet également certains usages d'expressions indexées selon la version, ou l'utilisation de colonnes générées indexées. La syntaxe et les restrictions ne sont pas identiques. Vérifiez aussi les règles de collation et de casse : le besoin peut être mieux traité au niveau du type, de la collation ou d'une contrainte d'unicité adaptée que par une expression ajoutée à chaque requête.

### 9.2 Prédicats SARGables

Une condition est souvent dite *SARGable* lorsqu'elle peut être transformée en une recherche efficace sur une structure d'index. Les prédicats qui appliquent des transformations aux colonnes, les conversions implicites ou les motifs qui commencent par un joker peuvent limiter l'accès direct par index, selon le moteur et le type d'index.

Moins adapté à un index simple sur date_inscription :

~~~sql
SELECT *
FROM inscriptions
WHERE EXTRACT(YEAR FROM date_inscription) = 2026;
~~~

Une forme de plage est souvent plus favorable à un index B-tree sur la date :

~~~sql
SELECT apprenant_id, cours_id, date_inscription
FROM inscriptions
WHERE date_inscription >= DATE '2026-01-01'
  AND date_inscription < DATE '2027-01-01';
~~~

La transformation doit préserver la sémantique : les bornes sont choisies pour inclure toutes les dates de l'année 2026 sans dépendre d'une fonction appliquée à chaque ligne. Les types, le fuseau horaire et le besoin métier doivent être pris en compte si la colonne représente un instant avec une heure plutôt qu'une date pure.

## 10. Lire EXPLAIN sous PostgreSQL et MySQL

EXPLAIN permet d'examiner la stratégie que le moteur prévoit pour une requête. Le format diffère entre PostgreSQL et MySQL. Il faut apprendre à lire le plan et chercher des preuves pertinentes, plutôt que de mémoriser qu'une étiquette est bonne ou mauvaise.

### 10.1 PostgreSQL : EXPLAIN

~~~sql
EXPLAIN
SELECT i.apprenant_id, i.cours_id, i.date_inscription
FROM inscriptions AS i
WHERE i.apprenant_id = 10
ORDER BY i.date_inscription DESC;
~~~

La sortie PostgreSQL peut exposer des nœuds comme Seq Scan, Index Scan, Bitmap Index Scan, Bitmap Heap Scan, Sort, Hash Join, Nested Loop ou Aggregate. Le plan comprend des estimations de coûts et de cardinalité. Le détail change avec la version, les options et les propriétés de la requête.

Pour examiner le comportement réel, PostgreSQL propose EXPLAIN ANALYZE. Cette option exécute effectivement la requête, mesure des durées et fournit les lignes observées. Elle doit être utilisée avec soin : une requête de lecture peut être lourde, et une instruction modifiant les données a des effets réels si elle est exécutée. Testez dans un laboratoire et assurez-vous de comprendre l'effet exact de l'instruction.

~~~sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT i.apprenant_id, i.cours_id, i.date_inscription
FROM inscriptions AS i
WHERE i.apprenant_id = 10
ORDER BY i.date_inscription DESC;
~~~

BUFFERS ajoute des informations sur les blocs selon les capacités du moteur et les options utilisées. Les chiffres doivent être interprétés dans leur contexte ; ils ne correspondent pas toujours directement à des lectures physiques de disque. Les caches du système et du moteur influencent les mesures.

### 10.2 MySQL : EXPLAIN

~~~sql
EXPLAIN
SELECT i.apprenant_id, i.cours_id, i.date_inscription
FROM inscriptions AS i
WHERE i.apprenant_id = 10
ORDER BY i.date_inscription DESC;
~~~

Selon la version de MySQL et le format, la sortie peut inclure la table, le type d'accès, les index possibles, l'index choisi, les clés utilisées, les lignes estimées et des informations supplémentaires. EXPLAIN FORMAT=JSON peut fournir une représentation structurée qui détaille davantage le plan.

~~~sql
EXPLAIN FORMAT=JSON
SELECT i.apprenant_id, i.cours_id, i.date_inscription
FROM inscriptions AS i
WHERE i.apprenant_id = 10
ORDER BY i.date_inscription DESC;
~~~

MySQL dispose aussi d'EXPLAIN ANALYZE dans les versions qui le prennent en charge ; cette variante exécute l'instruction analysée et fournit des mesures réelles. Vérifiez la version, les limitations de syntaxe et les effets de l'instruction avant utilisation. N'appliquez pas EXPLAIN ANALYZE à une modification de données sans un cadre transactionnel et une stratégie de sécurité pleinement compris.

### 10.3 Que chercher en premier ?

1. Le nombre de lignes estimé paraît-il cohérent avec le volume et les filtres ?
2. La méthode d'accès correspond-elle au type de prédicat et à sa sélectivité ?
3. Le moteur doit-il trier les lignes, et ce tri est-il attendu ?
4. Une jointure produit-elle bien le nombre de lignes prévu ?
5. Existe-t-il un écart important entre estimation et exécution réelle ?
6. Les étapes coûteuses sont-elles celles qui dominent la mesure ?
7. Les données viennent-elles du cache ou le stockage constitue-t-il un facteur ?
8. La requête attend-elle un verrou ou une connexion en dehors du coût visible du plan ?

Un plan ne se lit pas en cherchant simplement le mot « index ». Un parcours de table peut être le bon choix. Un index peut être utilisé pour obtenir une quantité énorme de lignes de façon coûteuse. Le but est de comprendre si la stratégie est adaptée au volume, à la distribution et à la question.

## 11. Statistiques et estimations de cardinalité

Le moteur utilise les statistiques pour estimer combien de lignes satisferont un prédicat, quels couples de valeurs sont courants et comment les données sont distribuées. Les statistiques ne constituent pas une copie complète de la table ; ce sont des informations résumées qui servent à la planification.

Des données importées en grand nombre, une forte évolution de la distribution ou un statut devenu dominant peuvent rendre les estimations moins représentatives. Selon le moteur et les réglages, il peut être nécessaire d'actualiser les statistiques ou de modifier leur niveau de détail. Il faut consulter les procédures du moteur avant d'appliquer une opération de maintenance.

### 11.1 Écart estimé/réel

Si un plan estime dix lignes mais en traite un million, le planificateur a pu choisir une stratégie adaptée à une petite quantité de données, mais mauvaise pour le volume réel. Il faut examiner la cause de l'estimation : statistiques obsolètes, prédicat complexe, corrélation entre colonnes ou hypothèse de distribution inexacte. La correction peut relever des statistiques, de la formulation de la requête ou du modèle, et pas uniquement de l'index.

Les prédicats sur deux colonnes ne sont pas toujours indépendants. Par exemple, un cours particulier pourrait avoir principalement le statut « actif », tandis que les autres cours ont un autre statut. Estimer la probabilité de deux conditions en multipliant leurs fréquences indépendantes peut donner un résultat imprécis si les colonnes sont corrélées. Certains moteurs disposent de statistiques étendues ou de mécanismes qui peuvent améliorer des estimations particulières ; leur usage et leur portée dépendent de la version.

### 11.2 Actualiser les statistiques : procédure prudente

Un DBA ne devrait pas exécuter aveuglément une maintenance lourde pour chaque requête lente. Commencez par identifier les indicateurs, examiner le plan et déterminer si les statistiques sont probablement impliquées. Les commandes et la charge d'actualisation dépendent du moteur et de l'objet. En environnement de laboratoire, vous pouvez comparer le plan avant et après une actualisation appropriée si les données ont changé ; notez la différence observée.

L'actualisation des statistiques n'ajoute pas un index et ne garantit pas un plan plus rapide. Elle donne au planificateur des informations actualisées. Le plan peut s'améliorer, rester similaire ou changer vers une autre stratégie. Vérifiez le résultat fonctionnel et la performance après l'opération.

## 12. Jointures et index

Les jointures sont une source fréquente de travail dans les requêtes analytiques. Un index sur les colonnes de liaison peut aider certains plans, mais la stratégie de jointure et les tailles relatives des tables comptent également.

Considérons :

~~~sql
SELECT a.nom_apprenant, i.cours_id, i.score
FROM apprenants AS a
JOIN inscriptions AS i
  ON i.apprenant_id = a.apprenant_id
WHERE a.apprenant_id = 10;
~~~

L'identifiant d'apprenant est une clé primaire dans APPRENANTS, et le préfixe apprenant_id de la clé composée d'INSCRIPTIONS peut soutenir l'accès aux inscriptions. Ajouter un nouvel index sur le même préfixe peut être redondant. Avant de créer un index, examinez la clé primaire et les index existants.

Autre exemple : obtenir les inscriptions du cours 100 :

~~~sql
SELECT apprenant_id, date_inscription, score
FROM inscriptions
WHERE cours_id = 100;
~~~

La clé primaire composée (apprenant_id, cours_id) commence par apprenant_id, pas par cours_id. Selon le moteur, elle peut ne pas être adaptée à un accès rapide lorsque seul cours_id est filtré. Un index sur cours_id peut être utile si cette requête est fréquente et suffisamment sélective. La décision doit être validée avec le plan.

### 12.1 Nested loop, hash join et merge join

Le choix de la jointure dépend de la quantité de lignes, de l'ordre des données, des index et des statistiques. Un nested loop peut être très efficace lorsque le côté externe est petit et que le côté interne dispose d'un accès rapide. Une hash join peut être adaptée à de grandes relations, si les ressources mémoire et les données s'y prêtent. Une merge join peut tirer avantage d'entrées ordonnées.

Il n'existe pas de stratégie de jointure qui soit toujours la meilleure. Si le plan montre un grand nombre de boucles, examinez combien de lignes passent par la boucle et combien de lignes chaque recherche renvoie. Si un tri ou une table temporaire apparaît, déterminez si l'opération est nécessaire à l'ordre demandé et si son coût est raisonnable.

### 12.2 Préserver la sémantique pendant l'optimisation

La réécriture d'une requête doit conserver son résultat, y compris les cas limites. Remplacer un LEFT JOIN par un INNER JOIN peut exclure les cours sans inscription. Déplacer un prédicat de WHERE vers ON peut modifier la conservation des lignes. Remplacer COUNT(*) par COUNT(colonne) peut changer le comptage des valeurs NULL. Avant de comparer la performance, construisez des tests qui détectent ces différences.

~~~mermaid
flowchart LR
    A["Ajouter un index"] --> B["Peut accélérer certaines lectures"]
    A --> C["Consomme du stockage"]
    A --> D["Augmente la maintenance des écritures"]
    B --> E["Comparer le gain et le coût global"]
    C --> E
    D --> E
~~~

## 13. Index et coût des écritures

Un index améliore potentiellement certains accès en lecture, mais le SGBD doit le maintenir quand une ligne est insérée, supprimée ou modifiée sur les colonnes indexées. Chaque index consomme aussi de l'espace, peut augmenter les écritures de journaux et de sauvegardes, et peut influencer le cache. Des index en trop peuvent ainsi dégrader le débit global.

Pour une table très fréquemment mise à jour, le coût d'un index sur une colonne qui change à chaque requête peut être important. Si la colonne n'est jamais utilisée pour filtrer, joindre ou trier une requête utile, l'index peut constituer un coût sans bénéfice significatif. À l'inverse, un index critique pour une requête de connexion ou une recherche métier peut être indispensable.

### 13.1 Coût de création et de reconstruction

Créer un index sur une grande table peut consommer de la CPU, de la mémoire et du stockage temporaire, et peut influencer les autres opérations. Les possibilités d'indexation en ligne ou concurrente diffèrent selon le moteur et la commande. PostgreSQL propose notamment CREATE INDEX CONCURRENTLY avec des contraintes particulières, tandis que MySQL/InnoDB possède ses propres algorithmes et options d'opérations en ligne. Ne présumez pas que la commande ou le niveau de blocage est identique.

Avant de déployer un index sur une grosse table, estimez la durée, la place libre, l'impact sur les écritures, les verrous, la réplication et les fenêtres de maintenance. Testez sur un volume réaliste et vérifiez les options de la version ciblée. Un index techniquement correct peut être opérationnellement risqué si sa création épuise le stockage ou dégrade les performances pendant la fenêtre critique.

### 13.2 Index inutilisés ou redondants

Un index qui n'a enregistré aucune utilisation sur la période observée n'est pas nécessairement inutile : la fenêtre peut ne pas inclure le traitement mensuel, la métrique peut avoir été réinitialisée ou la requête peut être rare mais critique. Vérifiez la période, le trafic, les dépendances et les besoins de reprise avant de supprimer un index.

Les index dupliqués ou fortement chevauchants méritent aussi une revue. Deux index peuvent sembler similaires mais différer par leur ordre des colonnes, leur condition, leurs colonnes incluses ou leur type. Documentez leur rôle. La suppression peut libérer de l'espace et réduire le coût d'écriture, mais elle doit être accompagnée d'une mesure et d'une stratégie de retour appropriée.

## 14. Cas où l'index n'est pas la solution

Une requête lente n'est pas toujours un problème de manque d'index. Les causes peuvent inclure :
- une transaction qui bloque les opérations concurrentes ;
- une saturation CPU ou stockage ;
- un pool de connexions épuisé ;
- un grand volume de lignes réellement nécessaire ;
- un transfert réseau important vers le client ;
- une agrégation ou un tri coûteux ;
- un plan choisi à partir d'estimations peu fiables ;
- des opérations répétées par le code applicatif, comme un problème N+1 ;
- des requêtes qui retournent trop de colonnes ou trop de lignes ;
- une mauvaise pagination ou un ordre non déterministe.

Une approche saine examine les signaux de bout en bout. Si l'application passe son temps à attendre un emplacement dans le pool, l'ajout d'un index n'améliore pas directement cette file d'attente. Si une requête doit réellement compter des centaines de millions de lignes, un index ne fera pas disparaître tout le coût du calcul. Si le résultat retourne des milliers de lignes inutilisées par l'écran, réduire la quantité de données demandées peut être plus efficace que d'ajouter de la structure.

~~~mermaid
flowchart TD
    A["Requête lente"] --> B["Plan et latence mesurés"]
    B --> C{"Cause dominante ?"}
    C -- "Accès aux lignes" --> D["Examiner index et sélectivité"]
    C -- "Estimation erronée" --> E["Examiner statistiques et prédicats"]
    C -- "Verrous / attentes" --> F["Diagnostiquer concurrence"]
    C -- "CPU / tri / agrégat" --> G["Réduire travail ou revoir calcul"]
    C -- "Pool / réseau" --> H["Examiner application et connexions"]
    D --> I["Tester une seule hypothèse"]
    E --> I
    F --> I
    G --> I
    H --> I
~~~

## 15. Atelier pratique : diagnostiquer trois requêtes

### Mission

Vous êtes chargé de diagnostiquer les performances de trois écrans de Skill-Tree : recherche d'un apprenant par email, historique d'un apprenant et listing des inscriptions par cours. L'objectif est de formuler une hypothèse et de la vérifier dans un environnement isolé, pas de créer plusieurs index au hasard.

### Étape 1 — Documenter la charge

Pour chaque requête, notez sa fréquence, la latence cible, le nombre de lignes attendu, les filtres, la jointure, le tri et les colonnes utilisées. Indiquez quelles contraintes et quels index existent déjà. Le test doit être exécuté sur un volume représentatif ou avec une explication des limites de l'échantillon.

### Étape 2 — Recherche d'apprenant par email

~~~sql
SELECT apprenant_id, nom_apprenant
FROM apprenants
WHERE email_apprenant = 'amina@example.test';
~~~

La colonne email_apprenant est UNIQUE dans le schéma pédagogique, ce qui fournit normalement une structure de recherche adaptée à l'unicité. Vérifiez le plan et les contraintes existantes avant de créer un autre index. Si l'écran recherche avec une casse normalisée, examinez la collation ou une solution d'indexation sur expression adaptée à la règle métier.

### Étape 3 — Historique d'un apprenant

~~~sql
SELECT cours_id, date_inscription, score
FROM inscriptions
WHERE apprenant_id = 10
ORDER BY date_inscription DESC;
~~~

La clé primaire composée commence par apprenant_id et peut aider ce filtre. L'ordre demandé porte sur date_inscription, qui n'est pas la deuxième colonne de la clé primaire dans le modèle initial, car celle-ci est cours_id. Si le besoin est fréquent, un index composite (apprenant_id, date_inscription) peut valoir une mesure. Vérifiez le tri dans le plan, la taille de l'index et l'effet sur les écritures. Une colonne ajoutée à INCLUDE peut couvrir davantage de données dans PostgreSQL, mais le choix exact dépend du moteur.

### Étape 4 — Inscriptions par cours

~~~sql
SELECT apprenant_id, date_inscription, score
FROM inscriptions
WHERE cours_id = 100
ORDER BY date_inscription DESC;
~~~

La clé primaire ne commence pas par cours_id ; elle ne fournit donc pas forcément l'accès le plus efficace pour ce prédicat seul. Un index sur (cours_id, date_inscription) pourrait soutenir le filtre et l'ordre. Mesurez cette hypothèse, car l'intérêt dépend de la fréquence et de la proportion de lignes renvoyées. Si le cours contient presque toutes les inscriptions, le moteur peut choisir un parcours plus large.

### Étape 5 — Lire les plans

Exécutez EXPLAIN sur chaque requête. Utilisez EXPLAIN ANALYZE ou EXPLAIN ANALYZE dans les versions qui le prennent en charge uniquement dans le laboratoire et après avoir compris que l'instruction sera réellement exécutée. Notez les méthodes d'accès, les estimations, le nombre de lignes, les tris et les boucles. Interprétez le plan selon les informations disponibles dans le moteur.

### Étape 6 — Tester une modification

Ne créez qu'un index à la fois. Relancez exactement les mêmes requêtes et comparez les sorties, les plans et les temps sous des conditions similaires. Testez aussi une insertion et une mise à jour sur les colonnes concernées pour observer les coûts d'écriture. Si le test n'est pas représentatif, consignez cette limite au lieu de promettre un gain de production.

### Étape 7 — Décider et documenter

Pour chaque index envisagé, consignez son nom, les colonnes et leur ordre, les requêtes ciblées, les preuves du gain, les coûts estimés, les risques de création et le plan de retrait si nécessaire. Si l'index n'apporte aucun gain, documentez pourquoi il n'est pas conservé. Le résultat professionnel est une décision justifiée, pas une collection de structures.

## 16. Méthode de diagnostic de performance

Une méthode cohérente évite de mélanger les symptômes et les causes :

1. confirmer le symptôme côté utilisateur et côté base ;
2. sélectionner une requête représentative ;
3. capturer paramètres, volume, plan et latence ;
4. vérifier la sémantique et la granularité du résultat ;
5. comparer les estimations au réel quand c'est disponible ;
6. identifier l'étape dominante, y compris les attentes hors du plan ;
7. formuler une seule hypothèse de correction ;
8. mesurer la requête originale et la variante ;
9. vérifier les cas limites et les effets sur les écritures ;
10. documenter le résultat et surveiller après déploiement.

Il faut aussi tenir compte du phénomène de régression. Une modification qui améliore une requête peut en dégrader d'autres, notamment si elle change l'ordre de colonnes d'un index, augmente la charge d'écriture ou modifie les statistiques. La décision se fait à l'échelle de la charge globale du service, et non uniquement sur le scénario de laboratoire qui a motivé le changement.

## 17. Exercices d'application avec corrigés

### Exercice 1 — Index sur l'email

Une application recherche fréquemment un apprenant par email, et la colonne est déclarée UNIQUE. Faut-il ajouter un deuxième index identique ?

**Corrigé.** Généralement non sans preuve d'un besoin distinct. La contrainte UNIQUE est normalement soutenue par un index ou un mécanisme équivalent qui permet la recherche et vérifie l'unicité. Vérifiez la structure existante et le plan avant d'ajouter un index redondant.

### Exercice 2 — Filtre par date

Une requête cherche toutes les inscriptions du mois de septembre et un index B-tree existe sur date_inscription. Pourquoi l'index peut-il ne pas être utilisé ?

**Corrigé.** Si la plage couvre une proportion importante des données, le parcours de table peut coûter moins cher que des recherches d'index suivies de nombreux accès aux lignes. La table peut aussi être petite ou les statistiques peuvent favoriser un autre plan. L'utilisation doit être vérifiée par EXPLAIN et sur les données réelles.

### Exercice 3 — Ordre d'un index composite

Une requête filtre par apprenant_id puis trie par date_inscription. Entre les index (apprenant_id, date_inscription) et (date_inscription, apprenant_id), lequel mérite d'être testé en premier ?

**Corrigé.** L'index (apprenant_id, date_inscription) correspond directement au filtre d'égalité par apprenant puis à l'ordre par date. Il mérite donc d'être testé en premier, sous réserve du moteur, du sens de tri, des colonnes retournées et de la charge observée. La mesure doit confirmer l'utilité.

### Exercice 4 — Préfixe gauche

Un index B-tree composite porte sur (apprenant_id, date_inscription). Une requête filtre uniquement par date_inscription. Peut-on supposer que l'index sera aussi adapté qu'un index commençant par date_inscription ?

**Corrigé.** Non. Pour de nombreux index B-tree, l'ordre des colonnes conditionne l'utilisation du préfixe. L'index composite est surtout organisé pour les recherches qui commencent par apprenant_id. Examinez le plan et évaluez un index distinct uniquement si la charge le justifie.

### Exercice 5 — Fonction appliquée à une colonne

La requête utilise WHERE EXTRACT(YEAR FROM date_inscription) = 2026. Comment peut-on souvent la rendre plus favorable à un index simple de date ?

**Corrigé.** Remplacer le prédicat par une plage explicite, par exemple date_inscription >= DATE '2026-01-01' AND date_inscription < DATE '2027-01-01', si cette transformation conserve la sémantique métier. Une autre option peut être un index sur expression lorsque le moteur le prend en charge et que le besoin le justifie.

### Exercice 6 — Index qui accélère SELECT mais ralentit les écritures

Pourquoi faut-il mesurer autre chose que la latence de la requête qui a motivé l'index ?

**Corrigé.** Le moteur doit maintenir l'index pour les insertions, suppressions et modifications. Il ajoute du stockage et peut augmenter l'écriture des journaux et l'occupation du cache. Il faut considérer le débit global et le profil de lecture/écriture, pas uniquement une requête sélectionnée.

### Exercice 7 — Estimation incorrecte

Le plan estime qu'une condition renvoie 20 lignes, mais elle en retourne réellement 200 000. Quelles pistes examinez-vous ?

**Corrigé.** Examinez l'actualisation et le niveau des statistiques, la distribution des valeurs, les valeurs fréquentes, les corrélations entre prédicats et la façon dont la requête est formulée. L'écart peut amener à choisir une stratégie de jointure ou d'accès mal adaptée. Mesurez à nouveau après la correction candidate.

### Exercice 8 — Scan séquentiel

EXPLAIN affiche un parcours séquentiel. Est-ce automatiquement une mauvaise nouvelle ?

**Corrigé.** Non. Le parcours séquentiel peut être optimal pour une petite table ou un prédicat qui sélectionne une grande part des données. Il faut comparer le coût, la sélectivité, les lignes produites et l'objectif de la requête avant de décider qu'un index est nécessaire.

### Exercice 9 — Index couvrant

Une requête lit plusieurs colonnes et utilise un index sur la seule colonne filtrée. Pourquoi peut-elle encore accéder à la table ?

**Corrigé.** L'index peut identifier les lignes sans contenir toutes les valeurs nécessaires au résultat. Le moteur doit alors accéder aux lignes de base pour lire les colonnes absentes de l'index. Un index couvrant peut aider, mais il faut mesurer son coût en espace et en écritures et tenir compte des différences entre moteurs.

### Exercice 10 — EXPLAIN et EXPLAIN ANALYZE

Quelle différence essentielle devez-vous retenir ?

**Corrigé.** EXPLAIN présente un plan estimé selon le moteur et ses options. EXPLAIN ANALYZE exécute réellement l'instruction dans les moteurs et versions qui proposent cette option, puis ajoute des mesures observées. Cette exécution peut consommer des ressources et, pour une instruction de modification, avoir des effets réels ; elle doit être utilisée en toute connaissance de cause.

### Exercice 11 — Mauvaise latence malgré un bon plan

Une requête paraît raisonnable dans le plan, mais la latence de l'application est élevée. Que faut-il examiner en plus ?

**Corrigé.** Examinez les attentes sur les verrous, le pool de connexions, le réseau, le transfert de gros résultats, la saturation CPU ou disque et les autres requêtes concurrentes. La latence de bout en bout ne se limite pas aux coûts visibles dans le plan SQL.

### Exercice 12 — Retirer un index inutilisé

Un tableau de bord montre qu'un index a été peu utilisé. Pouvez-vous le supprimer immédiatement ?

**Corrigé.** Non. Vérifiez que la période comprend les traitements rares, que les compteurs n'ont pas été réinitialisés, que l'index n'est pas requis pour une contrainte ou un besoin critique et que ses utilisateurs ont été recensés. Préparez une décision mesurée et une procédure de retour si la suppression révèle une régression.

## 18. Défi final corrigé — optimiser un écran d'historique

### Mission

Un écran de Skill-Tree doit afficher l'historique des inscriptions d'un apprenant, trié par date décroissante. Un second écran liste les inscriptions d'un cours dans une période. Les deux écrans ralentissent avec le volume. Votre mission est de proposer et tester une stratégie d'indexation sans créer de structure inutile.

### Étape A — Formuler les deux requêtes

Historique d'un apprenant :

~~~sql
SELECT cours_id, date_inscription, score
FROM inscriptions
WHERE apprenant_id = 10
ORDER BY date_inscription DESC;
~~~

Inscriptions d'un cours dans une période :

~~~sql
SELECT apprenant_id, date_inscription, score
FROM inscriptions
WHERE cours_id = 100
  AND date_inscription >= DATE '2026-09-01'
  AND date_inscription < DATE '2026-10-01'
ORDER BY date_inscription DESC;
~~~

La première requête filtre par apprenant et demande un ordre par date. La seconde filtre par cours et date. Elles possèdent des motifs d'accès distincts ; un seul index n'est pas nécessairement optimal pour les deux.

### Étape B — Examiner les structures existantes

Inspectez la clé primaire (apprenant_id, cours_id) et les index existants. Vérifiez quels prédicats ils peuvent soutenir. Déterminez si un index commence par la colonne de filtre des deux requêtes. Notez également les contraintes de clés étrangères et les éventuels index générés par les contraintes du moteur.

### Étape C — Formuler des hypothèses

Pour l'écran historique, testez l'hypothèse d'un index composite commençant par apprenant_id puis date_inscription. Pour la liste par cours, testez l'hypothèse d'un index commençant par cours_id et date_inscription. Ces structures sont des candidates, pas une recommandation inconditionnelle ; leur utilité dépend du volume, de la distribution, de la fréquence des requêtes et du coût d'écriture.

Exemple de DDL pour un laboratoire compatible avec les fonctionnalités principales :

~~~sql
CREATE INDEX idx_inscriptions_apprenant_date
ON inscriptions (apprenant_id, date_inscription);
~~~

~~~sql
CREATE INDEX idx_inscriptions_cours_date
ON inscriptions (cours_id, date_inscription);
~~~

L'ordre de tri exact et la syntaxe des options peuvent être adaptés au moteur. Ne créez pas les deux index dans la production simplement parce que deux requêtes existent : mesurez les gains, la taille, la fréquence et l'impact sur le débit d'écriture avant de choisir.

### Étape D — Mesurer avant et après

Exécutez EXPLAIN avant la création, puis après. Dans le laboratoire seulement, utilisez les options de mesure réelle disponibles sur le moteur cible. Comparez le résultat SQL et les plans, ainsi que les temps sur plusieurs exécutions. Notez les écarts entre lignes estimées et réelles, les tris, les accès par index et les accès aux pages de table.

### Étape E — Tester l'effet sur les écritures

Ajoutez une inscription fictive et modifiez un score. Vérifiez la cohérence et observez le comportement général, sachant que le laboratoire ne suffit pas à mesurer la charge de production. Notez que les nouveaux index augmentent les opérations de maintenance. Estimez leur espace nécessaire avec les outils du moteur et la taille des données représentatives.

### Étape F — Décider

Conservez uniquement les index dont le gain est mesuré et utile à la charge globale. Si un index n'améliore pas le résultat ou crée un coût injustifié, retirez-le du plan de conception. Pour un déploiement sur une grosse table, préparez une migration, estimez la durée et l'espace, consultez les options de création en ligne ou concurrente disponibles et surveillez le service pendant l'opération.

### Corrigé de référence

Le bon corrigé n'est pas « toujours créer deux index ». Il consiste à observer le plan réel, comprendre la structure des clés existantes, tester les candidats, comparer les résultats et les mesures, puis expliquer la décision. Si le volume de données est trop petit pour différencier les plans, le compte rendu doit indiquer cette limite et prévoir un test représentatif avant une décision de production.

Un index peut être conservé parce qu'il améliore une requête fréquente à latence critique, même s'il ajoute un coût d'écriture raisonnable. Il peut être rejeté si la requête est rare, si le gain est insignifiant ou si une structure existante fournit déjà l'accès voulu. Toute décision est documentée avec le motif, les preuves et les risques.

## 19. Checklist de validation

- Les requêtes lentes ont été identifiées avec leurs paramètres et leur fréquence.
- Le volume et la distribution des données de test sont documentés.
- Le moteur, la version et les structures d'index existantes sont connus.
- Les plans ont été examinés avant toute modification.
- Les estimations de lignes ont été comparées aux valeurs observées lorsque possible.
- Les prédicats et l'ordre des colonnes d'index sont cohérents avec les requêtes.
- Les index de clé primaire et UNIQUE ont été pris en compte avant d'ajouter un index.
- Les index composites ont été évalués selon leur ordre des colonnes et la charge réelle.
- Les possibilités d'index couvrant, partiel et fonctionnel ont été traitées comme spécifiques au moteur.
- Les coûts de stockage et d'écriture sont considérés.
- Les mesures avant/après sont reproductibles.
- Les résultats fonctionnels et les cas limites restent corrects.
- Les opérations coûteuses et les changements d'index sont préparés avec un plan de déploiement.
- Les causes non liées aux index, comme les verrous, le réseau et le pool, ont été examinées.
- Les décisions et limites du test sont documentées.
- Les performances sont surveillées après déploiement.

## 20. Synthèse finale

L'indexation est une décision fondée sur une charge de travail. Le plan d'exécution montre comment le moteur envisage d'obtenir le résultat : méthodes d'accès, jointures, tris, agrégations et estimations de cardinalité. Un parcours de table n'est pas automatiquement mauvais, et un accès par index n'est pas automatiquement rapide. Le bon plan dépend du volume, de la sélectivité, de la distribution, des statistiques, des pages à lire et des opérations suivantes.

Les index B-tree sont courants pour les égalités, les plages et certains ordres. Les index composites peuvent aider plusieurs prédicats, mais leur ordre est déterminant. Les index couvrants, partiels ou sur expression dépendent des capacités du moteur et de la requête. Les index apportent des coûts de stockage et de maintenance ; un index redondant ou peu utile peut dégrader les écritures sans amélioration suffisante des lectures.

EXPLAIN fournit une vision du plan estimé et les options de mesure réelle permettent, quand elles sont disponibles, d'examiner le nombre de lignes et le temps observés. Les variantes qui exécutent réellement une instruction doivent être utilisées avec prudence. Une mesure doit être reproductible, accompagnée de son contexte et complétée par les métriques d'application et du serveur si le problème est lié aux attentes, au stockage, aux connexions ou au réseau.

La méthode est la même pour les requêtes complexes : identifier le besoin et la granularité, observer la requête et le plan, formuler une hypothèse, tester une seule modification, préserver le résultat fonctionnel et mesurer son coût global. On n'optimise pas en ajoutant le maximum d'index, mais en choisissant les structures qui améliorent les besoins importants tout en préservant l'intégrité et la capacité d'écriture.

## Références techniques

Consultez la documentation correspondant à la version réellement utilisée, car les options et les méthodes d'accès évoluent.

- PostgreSQL, introduction aux index : https://www.postgresql.org/docs/current/indexes-intro.html
- PostgreSQL, types d'index : https://www.postgresql.org/docs/current/indexes-types.html
- PostgreSQL, index multicolonnes : https://www.postgresql.org/docs/current/indexes-multicolumn.html
- PostgreSQL, index sur expression : https://www.postgresql.org/docs/current/indexes-expressional.html
- PostgreSQL, EXPLAIN : https://www.postgresql.org/docs/current/using-explain.html
- PostgreSQL, statistiques du planificateur : https://www.postgresql.org/docs/current/planner-stats.html
- MySQL 8.4, optimisation des index : https://dev.mysql.com/doc/refman/8.4/en/optimization-indexes.html
- MySQL 8.4, EXPLAIN : https://dev.mysql.com/doc/refman/8.4/en/explain.html
- MySQL 8.4, index composites et ordre des colonnes : https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html

Les scripts sont pédagogiques. Vérifiez la syntaxe, le coût des opérations et les comportements précis du moteur cible avant de modifier un schéma en production.
