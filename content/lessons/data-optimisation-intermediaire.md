# Indexation et plans d'exécution — Intermédiaire

> **Mise en contexte.** Le tableau de bord d’une plateforme de formation est lent alors que le serveur ne semble pas à court de mémoire. Une page qui liste les cours répond en 80 millisecondes dans l’environnement de test mais met quatre secondes en production. Une autre requête est rapide lorsqu’elle filtre un petit groupe d’apprenants, puis s’effondre lorsque le filtre couvre une grande partie de la table. Les index ont été ajoutés au fil des demandes, certains ne sont probablement jamais utilisés, et personne ne connaît leur coût d’écriture. Pour améliorer la performance, il faut examiner le plan réellement choisi, les statistiques, la sélectivité, la cardinalité, le volume de lignes et le profil de charge — pas empiler des index au hasard.

## Objectifs et parcours pratique

Vous allez apprendre à lire un plan d’exécution, distinguer estimation et mesure, reconnaître les scans, comprendre les jointures, évaluer la sélectivité d’un prédicat, choisir un type d’index adapté, raisonner sur un index composite, identifier une mauvaise estimation et bâtir une mesure reproductible. Vous apprendrez aussi quand ne pas créer d’index : sur une petite table, une colonne peu sélective, une colonne mise à jour constamment ou une requête rarement exécutée, le coût supplémentaire peut être supérieur au gain.

Les exemples utilisent PostgreSQL et mentionnent MySQL. Les syntaxes et les options de diagnostic diffèrent entre les moteurs et entre versions. Ne copiez jamais une conclusion issue d’un plan sur une autre base sans comparer la taille des tables, les statistiques, le volume renvoyé, les index disponibles, la charge, le matériel et les paramètres. Le même SQL peut produire un autre plan et être plus rapide ou plus lent selon le contexte.

Le fil rouge est un catalogue de cours, des inscriptions et des tentatives. L’objectif est de réduire la latence des parcours d’apprentissage sans sacrifier la cohérence des données ni dégrader les écritures. Les requêtes et données de laboratoire sont synthétiques et ne ciblent aucune production.

## 1. La performance est une mesure contextualisée

Une requête lente n’est pas un diagnostic. La durée totale peut contenir l’attente d’une connexion, l’attente d’un verrou, la planification, l’exécution, la lecture du stockage, le transfert réseau, la sérialisation des résultats et le traitement client. Ajouter un index agit principalement sur les chemins d’accès et parfois sur les opérations nécessaires, mais il ne résout pas automatiquement les autres causes.

La première étape est de définir l’objectif avec une mesure observable : par exemple, le 95e percentile de latence doit être inférieur à 300 ms pour une recherche qui retourne au maximum 50 cours. Cette spécification associe une requête, une population de données, un volume de sortie et un percentile. Dire « la requête doit être rapide » ne permet ni de comparer deux versions, ni de décider si le résultat est atteint.

Les percentiles comptent parce qu’une moyenne peut masquer des cas très lents. Si 99 % des requêtes répondent en 50 ms et 1 % en 5 s, la moyenne peut sembler correcte tandis qu’un groupe d’utilisateurs ressent de longues attentes. Mesurez les distributions, le nombre de requêtes, les erreurs et la charge. Une amélioration de la moyenne qui dégrade la queue de latence peut être un mauvais compromis.

Un test de performance exige un jeu de données représentatif. Tester sur 100 lignes ne prouve pas que l’index sera efficace sur 100 millions de lignes. Les distributions comptent : une colonne de statut avec deux valeurs, une date répartie sur plusieurs années, un identifiant presque unique et une catégorie très déséquilibrée n’offrent pas la même sélectivité. Il faut aussi mesurer avec des valeurs « populaires » et « rares » lorsqu’elles produisent des plans différents.

Un index est une structure auxiliaire qui accélère certains accès en échange d’espace et de travail lors des écritures. Il peut accélérer WHERE, certaines jointures, ORDER BY ou des agrégations, mais seulement si sa forme et le plan du moteur correspondent à la requête. Le coût n’est pas uniquement sa taille : il comprend les insertions, les suppressions, les mises à jour, la maintenance, la sauvegarde, le cache et parfois le verrouillage pendant sa création ou sa reconstruction.

## 2. Le planificateur et le plan d’exécution

Le planificateur estime les coûts possibles et sélectionne un plan. Le plan décrit les opérations choisies : lecture séquentielle, lecture d’index, accès à la table, jointure par boucles imbriquées, jointure par hachage, tri, agrégation ou autre opération selon le moteur. Les nombres de coût sont des unités internes relatives; ils ne représentent pas directement des millisecondes. Leur intérêt est de comparer des alternatives sous les hypothèses du modèle de coût.

PostgreSQL fournit EXPLAIN pour afficher le plan estimé. EXPLAIN ANALYZE exécute réellement la requête et rapporte des mesures observées; il doit donc être utilisé en connaissance de cause. Pour une instruction SELECT, l’effet principal est la lecture et le travail exécuté. Pour INSERT, UPDATE ou DELETE, l’instruction est réellement exécutée : encapsulez-la dans une transaction de test et annulez lorsque cela est approprié, en gardant à l’esprit que certains effets externes ou appels de fonctions ne sont pas annulés comme un simple changement de ligne.

~~~sql
EXPLAIN
SELECT id, titre
FROM cours
WHERE categorie = 'reseaux'
ORDER BY titre;
~~~

Une version plus détaillée pour un environnement contrôlé :

~~~sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, titre
FROM cours
WHERE categorie = 'reseaux'
ORDER BY titre;
~~~

BUFFERS aide à observer les accès aux blocs et à distinguer ce qui a été trouvé en cache de certaines lectures. Les mesures dépendent de l’état du cache et de la charge concurrente; deux exécutions à la suite ne sont pas nécessairement comparables à deux exécutions après redémarrage. Le temps d’exécution rapporté par PostgreSQL n’inclut pas toute la chaîne côté client, par exemple le temps d’affichage de milliers de lignes.

Un plan doit être lu du bas vers le haut pour comprendre d’où proviennent les lignes, puis de haut en bas pour suivre les opérations qui les combinent. Les nœuds enfants produisent des données pour le parent. Il faut regarder les estimations de lignes, les lignes réellement traitées, le nombre de boucles, les temps observés, les blocs lus et les opérations de tri ou de hachage. Une grosse différence entre lignes estimées et observées est un signal important : le planificateur peut choisir une mauvaise stratégie parce que ses hypothèses sont éloignées des données.

~~~mermaid
flowchart TD
    A[SQL et paramètres] --> B[Statistiques]
    B --> C[Plans candidats]
    C --> D[Estimation des coûts]
    D --> E[Plan retenu]
    E --> F[Exécution]
    F --> G[Mesures réelles]
    G --> H{Écart avec les estimations ?}
    H -- Important --> I[Revoir statistiques et hypothèses]
    H -- Faible --> J[Évaluer les ressources dominantes]
    I --> B
~~~

Ne forcez pas immédiatement le moteur à utiliser un index parce que le plan montre un scan séquentiel. Si la requête lit 70 % d’une table, un scan séquentiel peut être plus économique qu’une lecture d’index suivie de nombreux accès dispersés aux pages. L’objectif n’est pas de faire apparaître le mot Index Scan partout; c’est de réduire le coût réel du service tout en maintenant un comportement stable.

## 3. Lecture séquentielle, index et sélectivité

Un scan séquentiel lit les pages d’une table. Il est souvent adapté quand une grande fraction des lignes doit être lue, quand la table est petite ou quand les données nécessaires sont déjà largement dans le cache. Un scan d’index peut trouver un petit ensemble de clés, mais le moteur peut ensuite devoir consulter les pages de la table pour récupérer les colonnes. Si les lignes sélectionnées sont dispersées sur beaucoup de pages, le coût de ces consultations peut être élevé.

La sélectivité exprime la part des lignes correspondant à un prédicat. Une condition qui renvoie 20 lignes sur 10 millions est très sélective; une condition qui renvoie 8 millions de lignes sur 10 millions ne l’est pas. La cardinalité représente souvent le nombre de lignes estimées ou observées à un stade du plan. Ces idées sont liées mais ne doivent pas être confondues : le nombre de valeurs distinctes, la fréquence de certaines valeurs et la proportion de résultats influencent le coût.

Une colonne presque unique, telle qu’un identifiant, peut être un excellent filtre. Une colonne contenant seulement deux statuts équilibrés peut être moins utile seule pour une requête qui demande la moitié de la table. Cela ne veut pas dire qu’il ne faut jamais indexer un statut : si une valeur rare correspond à une petite part de la table, si un index partiel est possible ou si l’ordre de colonnes d’un index composite aide la requête, l’index peut devenir utile. La décision demande un plan et des mesures.

Un index n’a pas pour but de « réduire le nombre de lignes de la table ». Il organise l’accès à certaines clés, et le planificateur doit estimer si cet accès sera moins coûteux que les alternatives. Si une requête retourne de nombreuses colonnes, un index qui ne contient que la clé de recherche ne fournit peut-être pas les données requises. Des accès à la table sont encore nécessaires, sauf si les conditions permettant un accès couvert sont satisfaites.

## 4. Index B-tree, composite, partiel et couvrant

Le B-tree est le type d’index courant pour les comparaisons d’égalité, les plages ordonnées et de nombreux tris. Il peut aider des prédicats comme id = 42, commencee_le >= une date, ou des recherches qui combinent plusieurs conditions. Le moteur choisit les détails internes de la structure. Un index doit être construit sur les colonnes utilisées par les requêtes réelles, et sa pertinence se vérifie par le plan d’exécution et la charge globale.

Un index composite contient plusieurs colonnes. L’ordre est important. Sur un index (apprenant_id, commencee_le), les recherches par apprenant_id et celles qui filtrent un apprenant puis ordonnent par date peuvent être adaptées; la recherche seulement par commencee_le n’exploite généralement pas le préfixe de la même façon. Cette règle générale dépend du moteur et ne doit pas remplacer la lecture de sa documentation, mais elle explique pourquoi l’ordre choisi doit refléter les filtres et l’ordre de tri les plus importants.

~~~sql
CREATE INDEX idx_tentatives_apprenant_date
ON tentatives_quiz (apprenant_id, commencee_le DESC);
~~~

Cet index peut aider une requête qui sélectionne les dernières tentatives d’un apprenant. Il n’est pas gratuitement bénéfique : chaque insertion de tentative doit également maintenir la structure, la taille du stockage augmente, et la présence d’un index supplémentaire peut augmenter le coût des sauvegardes et ralentir les changements sur les colonnes couvertes.

Un index partiel est défini sur un sous-ensemble de lignes conforme à un prédicat, dans les moteurs qui le prennent en charge. Il peut être intéressant lorsque le système consulte très fréquemment une portion réduite de la table, par exemple les tâches non terminées. Dans PostgreSQL :

~~~sql
CREATE INDEX idx_tentatives_inachevees
ON tentatives_quiz (apprenant_id, commencee_le)
WHERE terminee_le IS NULL;
~~~

Le moteur n’utilise cet index que si la requête peut être démontrée compatible avec le prédicat de l’index et si le plan estime cet accès avantageux. Une requête équivalente sur le plan logique peut ne pas correspondre exactement au prédicat ou dépendre de paramètres qui empêchent certaines preuves au moment de planifier. Ne créez pas un index partiel sans identifier les requêtes qui doivent l’utiliser.

Un index couvrant contient ou permet d’obtenir toutes les colonnes nécessaires à une requête donnée sans revisiter la table pour chaque ligne, selon les capacités du moteur et l’état des pages. PostgreSQL permet d’ajouter des colonnes de payload à un index avec INCLUDE. Ces colonnes ne sont pas des clés de recherche de la même façon que les colonnes principales. Les index couvrants peuvent accélérer des lectures précises, mais ils occupent de l’espace et peuvent rendre les mises à jour plus coûteuses.

~~~sql
CREATE INDEX idx_cours_categorie_titre
ON cours (categorie, titre)
INCLUDE (niveau, publie);
~~~

L’index peut être adapté à une liste de cours filtrée par catégorie et triée par titre qui affiche le niveau et le statut de publication. La possibilité réelle d’un index-only scan dépend toutefois de la visibilité des pages et d’autres détails internes. La création de l’index ne garantit pas à elle seule le plan ni le gain.

## 5. Index de fonctions et expressions

Certaines requêtes appliquent une fonction à une colonne dans la condition. Selon le moteur et l’expression, un index ordinaire sur la colonne peut ne pas être directement utilisable. Par exemple, chercher LOWER(email) = une valeur normalisée peut nécessiter un index sur cette expression, ou une stratégie de normalisation au moment de l’écriture.

~~~sql
CREATE INDEX idx_apprenants_email_lower
ON apprenants (lower(email));
~~~

La requête doit utiliser une expression compatible avec l’index pour que le planificateur puisse envisager cet accès. Une autre approche consiste à stocker une valeur normalisée dans une colonne dédiée, avec une contrainte qui empêche la divergence. Le choix dépend de la sémantique métier : normaliser une adresse e-mail de manière trop agressive peut être incorrect dans certains contextes, tandis qu’une politique de comparaison insensible à la casse peut être nécessaire pour l’application.

Les prédicats qui convertissent des dates en chaînes ou entourent une colonne d’une fonction peuvent également rendre le filtrage moins efficace. Au lieu de convertir chaque date pour comparer un mois, privilégiez parfois une plage temporelle explicite. La forme doit préserver le fuseau horaire et la sémantique de la période.

~~~sql
-- Forme souvent plus exploitable par un index sur cree_le :
SELECT id, email
FROM apprenants
WHERE cree_le >= TIMESTAMPTZ '2026-01-01 00:00:00+00'
  AND cree_le <  TIMESTAMPTZ '2026-02-01 00:00:00+00';
~~~

Cette requête définit un intervalle semi-ouvert, inclusif au début et exclusif à la fin. Elle évite les ambiguïtés dues à la précision de stockage pour le dernier instant de la période. Les bornes en UTC sont appropriées uniquement si la période métier est définie en UTC; si elle correspond à un mois local, calculez les bornes avec le fuseau de référence puis utilisez les instants correspondants.

## 6. Jointures et stratégies d’exécution

Les moteurs relationnels utilisent plusieurs stratégies pour joindre les relations. Une boucle imbriquée peut être efficace lorsque l’ensemble extérieur est petit et que l’ensemble intérieur est accessible par un index. Une jointure par hachage peut être adaptée à deux ensembles plus importants dont une relation peut servir à construire une table de hachage en mémoire ou sur disque. Une jointure par fusion peut être intéressante lorsque les données sont déjà ordonnées ou qu’un tri est rentable. Les noms et détails exacts varient selon le moteur.

Le choix dépend du nombre de lignes estimées. Si le planificateur croit que le côté extérieur ne contient que quelques lignes alors qu’il en contient plusieurs millions, une boucle imbriquée avec des accès répétés peut devenir coûteuse. La cause profonde peut être une statistique obsolète, une corrélation entre colonnes ou un filtre dont la sélectivité est mal estimée. Ajouter un index au hasard ne corrige pas nécessairement la mauvaise estimation.

Un exemple de jointure entre cours et inscriptions :

~~~sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.id, c.titre, count(i.id) AS nombre
FROM cours c
JOIN inscriptions i ON i.cours_id = c.id
WHERE c.publie = true
GROUP BY c.id, c.titre
ORDER BY nombre DESC;
~~~

Le plan réel doit montrer combien de cours passent le filtre, combien de lignes d’inscription sont examinées, la méthode de jointure, le coût de l’agrégat et le tri. Si le résultat final ne contient que 15 cours mais que le plan examine des millions de lignes, le coût provient peut-être du volume nécessaire pour calculer l’agrégat. Un index ne peut pas éliminer tout travail logique lorsque le résultat exige d’inspecter une grande part des données; des agrégats pré-calculés ou une autre stratégie peuvent être pertinents.

Ne transformez pas toutes les jointures en sous-requêtes ou l’inverse à partir d’une règle universelle. Un optimiseur moderne peut transformer plusieurs formes équivalentes, mais les CTE, les fonctions, les limites de lignes, les opérations DISTINCT et la dépendance entre expressions peuvent limiter les transformations. Le bon choix s’appuie sur la clarté de la requête, le plan observé et des mesures répétables.

## 7. Statistiques et estimation des cardinalités

Le planificateur a besoin de statistiques sur la distribution des valeurs, le nombre de valeurs distinctes, les fréquences les plus courantes et la distribution des données. PostgreSQL recueille des statistiques via ANALYZE, souvent exécuté par autovacuum selon sa configuration. MySQL dispose de ses propres mécanismes d’estimation et d’actualisation. Si les données changent rapidement ou si la distribution est fortement déséquilibrée, les statistiques peuvent ne plus représenter la réalité de la charge.

Après un chargement important, une migration qui change la distribution ou un changement de profil de données, vérifiez si les statistiques sont adaptées. Dans PostgreSQL :

~~~sql
ANALYZE cours;
ANALYZE inscriptions;
ANALYZE tentatives_quiz;
~~~

ANALYZE collecte des statistiques; ce n’est pas une promesse que chaque plan sera optimal. Si une condition dépend fortement de plusieurs colonnes corrélées, des statistiques indépendantes peuvent conduire à une estimation incorrecte. PostgreSQL prend en charge des statistiques étendues pour certains cas; d’autres moteurs ont leurs propres outils. La configuration doit être envisagée seulement après avoir identifié l’écart entre estimations et lignes réelles.

Une erreur d’estimation peut provenir de données très déséquilibrées. Imaginez que 95 % des cours sont privés et seulement 5 % sont publics, alors que la requête demande les cours publics. Si le moteur suppose une distribution uniforme ou ne dispose pas de statistiques récentes, il peut évaluer la mauvaise proportion de résultats et choisir un plan inadapté. Une colonne booléenne n’est pas automatiquement inutile à indexer : la fréquence de chaque valeur et la requête précise déterminent l’intérêt.

Les paramètres de requête peuvent aussi produire des profils différents. Une recherche sur un apprenant ayant deux tentatives n’a pas la même sélectivité que celle d’un compte de service avec plusieurs centaines de milliers de lignes. Les plans préparés, les paramètres et les stratégies du moteur peuvent influencer la stabilité. Mesurez les cas rares et fréquents, notamment si une même requête sert à la fois l’interface individuelle et des tâches de masse.

## 8. Tri, LIMIT et pagination

ORDER BY peut exiger un tri si aucun chemin d’accès ne fournit un ordre utile. Si la requête renvoie seulement les premières lignes, un index qui correspond au filtre et à l’ordre peut permettre de s’arrêter plus tôt. Mais un index sur une colonne de tri ne résout pas toutes les formes de filtrage. L’ordre composite doit correspondre au modèle d’accès et à la direction de tri.

~~~sql
SELECT id, titre, cree_le
FROM cours
WHERE categorie = 'reseaux'
ORDER BY cree_le DESC, id DESC
LIMIT 20;
~~~

Un index sur (categorie, cree_le DESC, id DESC) peut être un candidat, mais la mesure décide. Il faut également vérifier l’ordre exact, les filtres éventuels et la part de lignes qui satisfont la condition. Si la catégorie sélectionne presque toute la table, un autre plan peut rester plus efficace.

La pagination par offset devient coûteuse lorsque l’offset est très grand car le moteur peut devoir parcourir et ignorer de nombreuses lignes avant de renvoyer la page demandée. La pagination par curseur, ou keyset pagination, utilise la dernière clé déjà reçue pour demander les éléments suivants.

~~~sql
SELECT id, titre, cree_le
FROM cours
WHERE categorie = 'reseaux'
  AND (cree_le, id) < (TIMESTAMPTZ '2026-03-01 09:00:00+00', 5000)
ORDER BY cree_le DESC, id DESC
LIMIT 20;
~~~

Cette forme suppose un ordre descendant cohérent et une clé de départ qui correspond à la dernière ligne observée. La syntaxe de comparaison sur les lignes dépend du moteur, et il faut adapter les valeurs de curseur. Le curseur doit être stable, précis et suffisamment unique pour éviter les doublons ou les lignes oubliées entre les pages. Si les données changent pendant la pagination, définissez également le comportement attendu.

## 9. Pourquoi trop d’index peut ralentir le système

Chaque index doit être maintenu lors des modifications des colonnes ou des lignes qu’il couvre. Une insertion peut modifier plusieurs structures; une mise à jour peut provoquer des écritures supplémentaires; une suppression modifie aussi les index. Plus il existe de structures, plus il faut de stockage, de cache et de maintenance. Un index rarement utilisé peut donc avoir un coût permanent sans bénéfice observable.

Avant de supprimer un index, vérifiez son rôle dans les contraintes, les clés étrangères, les requêtes peu fréquentes mais critiques, les jobs mensuels et les chemins d’accès qui ne sont pas visibles pendant une petite fenêtre d’observation. Un index peut être utile à une contrainte UNIQUE ou à l’application d’une clé primaire même si l’on ne le voit pas dans un tableau de bord de lectures. La suppression doit passer par une revue, un test et une procédure de retour.

Les index redondants sont fréquents. Par exemple, un index sur (apprenant_id, commencee_le) peut rendre un autre index sur apprenant_id en partie redondant dans certains cas, mais leur utilité exacte dépend du moteur, des contraintes, de la taille et des requêtes. Ne supprimez pas systématiquement l’index court : il peut être plus petit et moins coûteux pour des accès ciblés. Mesurez et vérifiez.

La maintenance des index varie aussi. Les mises à jour peuvent générer des versions de lignes anciennes, de la fragmentation ou des coûts de nettoyage. PostgreSQL utilise notamment VACUUM pour le nettoyage des tuples morts et le maintien de la visibilité; certaines opérations de maintenance peuvent être nécessaires pour garder les statistiques, l’espace et les performances dans un état acceptable. N’exécutez pas les commandes de maintenance à l’aveugle : consultez les métriques, la documentation et les contraintes de production.

## 10. Mesurer proprement avant et après

Un bon benchmark reproduit un cas représentatif. Fixez la version du schéma, les données, les paramètres, la concurrence, l’état du cache autant que possible, le volume retourné et la configuration. Répétez les mesures. Notez médiane et percentiles, pas seulement une exécution isolée. Une requête peut être rapide la première fois sur un jeu de données minuscule, mais devenir plus lente au moment d’un pic de charge ou lorsque le cache est froid.

Les tests doivent inclure le coût d’écriture. Ajouter un index peut réduire la durée de lecture d’une liste de cours, mais augmenter le temps d’insertion, la taille de la sauvegarde et la latence d’un backfill. Mesurez la charge globale de l’application, pas seulement le SQL qui a motivé l’index. Un changement qui accélère une requête rarement exécutée de 40 ms à 10 ms mais ralentit toutes les insertions de 20 % peut être un mauvais compromis.

La comparaison avant/après doit utiliser la même requête et des paramètres comparables. Conservez le plan, les statistiques utiles et la version du moteur. Évitez les affirmations telles que « le nouvel index a rendu la base trois fois plus rapide » si le test ne mesure qu’un appel isolé. Précisez la portée : p95 de la route, temps de la requête, nombre de résultats, taux de cache ou débit total.

Une amélioration peut aussi provenir de la réduction des données transférées. Remplacer SELECT * par une liste de colonnes pertinentes réduit parfois la lecture, la sérialisation et la taille de la réponse. Limiter le résultat, éviter des calculs répétitifs et supprimer les appels SQL en N+1 peut apporter plus qu’un index. Le plan doit être interprété avec le profil du flux complet.

## 11. Atelier : construire un cas d’indexation

Créez une base de laboratoire et un jeu de données suffisamment grand pour observer plusieurs plans. Cette boucle de génération est adaptée à PostgreSQL et doit être exécutée uniquement dans une base dédiée.

~~~sql
CREATE TABLE cours (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    titre TEXT NOT NULL,
    categorie TEXT NOT NULL,
    publie BOOLEAN NOT NULL DEFAULT false,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO cours (titre, categorie, publie, cree_le)
SELECT
    'Cours ' || n,
    CASE
        WHEN n % 20 = 0 THEN 'securite'
        WHEN n % 5 = 0 THEN 'cloud'
        ELSE 'reseaux'
    END,
    (n % 4 <> 0),
    TIMESTAMPTZ '2024-01-01 00:00:00+00'
        + n * INTERVAL '1 minute'
FROM generate_series(1, 300000) AS n;

ANALYZE cours;
~~~

La distribution est volontairement déséquilibrée : certaines catégories sont beaucoup plus fréquentes que d’autres. Testez :

~~~sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, titre
FROM cours
WHERE categorie = 'securite'
ORDER BY cree_le DESC
LIMIT 30;
~~~

Créez un index candidat :

~~~sql
CREATE INDEX idx_cours_categorie_date
ON cours (categorie, cree_le DESC, id DESC);
ANALYZE cours;
~~~

Relancez exactement la même requête et comparez les plans, les lignes et les buffers. Si l’index n’est pas choisi, n’en concluez pas immédiatement qu’il est inutile : examinez la sélectivité, les colonnes projetées, les statistiques et le coût estimé. Vérifiez si la requête triée bénéficie de l’ordre et si l’accès à la table reste requis. Mesurez aussi une requête qui sélectionne la catégorie majoritaire et une insertion en lot pour observer le compromis.

Ajoutez ensuite un filtre de statut et comparez un index composite et un index partiel si la version le permet. Ne gardez pas toutes les variantes à la fin du laboratoire. Notez quelle requête chaque index sert, les résultats mesurés et le coût d’écriture observé. Un catalogue de nombreux index candidats n’est pas une stratégie de production.

## 12. Repérer les anti-patterns de requêtes

Le premier anti-pattern est le SELECT * dans un flux où seules quelques colonnes sont utiles. Il augmente le transfert et peut rendre impossible un accès couvrant ciblé. Le second est la pagination par grand OFFSET sur une liste qui grossit. Le troisième est le N+1, où le code exécute une requête pour récupérer une liste puis une autre pour chaque élément. Le quatrième est la conversion de colonnes dans le filtre sans tenir compte de l’index disponible. Le cinquième est l’agrégation répétée de données historiques à chaque affichage alors qu’un résumé validé pourrait être calculé selon une stratégie explicite.

Une requête N+1 peut être difficile à remarquer si la liste est courte en test. Pour 20 cours, cela fait une requête initiale et 20 requêtes de détail; pour 500 cours, le temps réseau et le coût de planification peuvent devenir dominants. Une jointure, un chargement en lot ou une API de lecture adaptée peut réduire le nombre d’allers-retours. Cela ne signifie pas que tout doit être joint dans une seule requête géante : la taille du résultat et les relations à plusieurs valeurs doivent être prises en compte.

Le problème du tri répété apparaît lorsqu’une application récupère beaucoup de lignes et les trie ensuite en mémoire alors que le serveur pourrait réduire le résultat avec une clause ORDER BY et LIMIT. À l’inverse, un grand tri SQL peut être cher si le résultat contient des millions de lignes. Identifiez quelle partie de la relation doit être triée et combien de lignes doivent être renvoyées.

Les requêtes ad hoc sont utiles, mais un système de reporting peut avoir besoin d’un modèle de lecture séparé, d’une table d’agrégats ou d’une tâche de calcul planifiée. Ces solutions déplacent la complexité vers la fraîcheur, la synchronisation et la cohérence. Un résumé pré-calculé doit avoir un propriétaire, une fréquence de rafraîchissement, une gestion des échecs et un indicateur de date de mise à jour afin que l’interface ne présente pas des données périmées comme parfaitement courantes.

## 13. Concurrence, verrous et performance perçue

Un plan efficace peut tout de même être lent si la requête attend un verrou. Les mesures doivent distinguer le temps passé à exécuter les nœuds du plan et les attentes liées à la concurrence. Si une requête est bloquée par une transaction longue, ajouter un index ne libérera pas nécessairement le verrou. Il faut alors identifier la transaction bloquante et comprendre pourquoi elle garde la ressource.

Les index peuvent parfois réduire la durée de certaines recherches ou le nombre de lignes touchées, et donc limiter l’intervalle de verrouillage. Mais les index peuvent aussi introduire du travail lors de l’écriture, une création concurrente peut consommer des ressources, et une mauvaise requête peut continuer à verrouiller une grande portion des données. La performance sous concurrence doit être testée avec un volume et un profil d’accès représentatifs.

Les index sur les clés étrangères doivent être réfléchis en fonction du moteur et des opérations. Une clé étrangère garantit l’intégrité, mais certains moteurs ne créent pas automatiquement un index sur la colonne enfant. Lorsqu’on supprime ou met à jour un parent, le moteur doit vérifier les relations associées; un index sur la clé étrangère enfant peut éviter une recherche coûteuse. Cela reste à vérifier en regard du schéma, du nombre de lignes et des contraintes réelles.

Les migrations d’index sur une table active peuvent bloquer les écritures ou consommer beaucoup de CPU, mémoire et stockage. PostgreSQL propose certaines formes de création concurrente, avec des restrictions et une procédure de traitement de l’échec; il faut lire la documentation de la version employée. Les opérations concurrentes ne sont pas une permission d’ignorer l’observabilité : elles peuvent échouer ou nécessiter un nettoyage si elles sont interrompues.

## 14. Exercices corrigés

### Exercice 1 — La lecture séquentielle est-elle toujours mauvaise?

Le plan affiche Seq Scan sur une table de 800 lignes. L’équipe demande un index.

**Correction.** Un scan séquentiel sur une petite table peut être optimal. L’index exige une structure supplémentaire et peut demander de consulter ensuite les pages de la table. Si la requête lit une grande proportion de lignes, le coût de l’index peut dépasser celui du scan. Il faut comparer les mesures et la charge, pas chercher à éliminer tous les scans séquentiels.

### Exercice 2 — Index composite

La requête filtre par apprenant_id, trie par commencee_le décroissante et affiche score. Quel index tester?

**Correction.** Commencez par un index dont les colonnes principales correspondent au filtre et à l’ordre, par exemple (apprenant_id, commencee_le DESC), puis observez le plan. Dans PostgreSQL, un ajout de score en INCLUDE peut être candidat si la requête est fréquente et si la réduction d’accès à la table vaut l’espace et le coût d’écriture. Il faut aussi confirmer les besoins en cas de valeurs de date égales et mesurer les insertions.

### Exercice 3 — Index inutilisé

Les statistiques indiquent qu’un index n’a presque jamais été utilisé pendant une journée.

**Correction.** Ne le supprimez pas immédiatement. Vérifiez la durée d’observation, les tâches de nuit, les rapports mensuels, les contraintes qu’il supporte, les requêtes qui peuvent l’utiliser et la date de la dernière réinitialisation des statistiques. S’il reste candidat à suppression, testez le plan de requêtes critiques sans lui et préparez un retour arrière.

### Exercice 4 — Estimation incorrecte

Le plan prévoit 100 lignes mais en traite 900 000. Quelles pistes vérifier?

**Correction.** Vérifiez les statistiques, la distribution des valeurs, la fraîcheur après un chargement, les corrélations entre colonnes, les paramètres et les expressions dans le filtre. Examinez à quel nœud l’écart commence, car une mauvaise estimation en bas du plan peut entraîner de mauvais choix de jointure ou de tri plus haut. Une fois la cause identifiée, mettez à jour les statistiques ou ajustez le modèle de données et retestez. Forcer le plan peut masquer le problème et devenir fragile lorsque les données changent.

### Exercice 5 — La requête accélère mais l’application ralentit

Après un index, le rapport passe de 4 s à 0,6 s, mais la saisie de tentatives est plus lente.

**Correction.** Le gain local peut être compensé par le coût de maintenance ajouté à chaque écriture, une hausse de contention ou une pression supplémentaire sur le cache et les E/S. Mesurez le profil complet, le taux d’écriture, les latences et les coûts de stockage. Vérifiez si le rapport doit réellement tourner aussi fréquemment, s’il peut utiliser un résumé ou une réplique, ou si une autre structure d’index est plus adaptée.

## 15. Défi final : accélérer un catalogue sans faire régresser les écritures

Le tableau de bord exécute trois opérations : lister 20 cours publics d’une catégorie triés par date, montrer les dernières tentatives de l’apprenant courant et afficher un décompte d’inscriptions par cours. L’équipe exige un p95 sous 250 ms pour les deux premières opérations, et une insertion de tentative ne doit pas régresser de plus de 10 %. Décrivez votre démarche de mesure et une proposition d’indexation initiale.

### Correction attendue

1. **Mesure.** Capturer la requête complète, ses paramètres, son plan, le nombre de lignes et le volume de sortie. Mesurer le p50/p95, la latence du pool, les attentes et la performance sous charge. Inclure des catégories fréquentes et rares, ainsi que les apprenants avec peu et beaucoup de tentatives.

2. **Catalogue.** Pour la requête qui filtre categorie et publie, puis ordonne par date et id avec LIMIT, tester un index composite aligné sur les prédicats et l’ordre. La liste de colonnes et la sélection réelle doivent être limitées. Comparer le gain et la maintenance lors des écritures de cours. Si les cours publics sont très nombreux ou très rares, mesurer les deux profils.

3. **Tentatives.** Tester un index qui commence par apprenant_id et permet de récupérer les dernières dates. Mesurer un index couvrant seulement si les colonnes projetées et la fréquence justifient le coût. Préciser un ordre de départage stable et vérifier que les requêtes utilisent la même convention.

4. **Décompte.** Déterminer si l’agrégat doit être exact et à jour à chaque appel. Si la table est petite ou le nombre de rapports faible, un calcul en ligne peut suffire. Si le volume est important, examiner un résumé actualisé ou une tâche planifiée, en documentant la fraîcheur des résultats et le comportement en cas d’échec.

5. **Validation.** Déployer les index sur un environnement représentatif, observer la durée de création et l’espace, puis tester sous charge. Comparer le plan, le p95, le débit d’insertion et les erreurs avant/après. Garder uniquement les structures apportant un bénéfice global mesuré. Préparer une procédure de suppression et de retour avant de modifier la production.

## 16. Checklist de diagnostic et synthèse

Avant de créer un index, identifiez une requête observée, ses paramètres, son volume de résultat, sa fréquence et son niveau de service. Capturez un plan, examinez les estimations et les lignes réelles, puis testez une hypothèse à la fois. Après un changement, refaites les mêmes mesures et observez les opérations d’écriture. N’ajoutez pas un index simplement parce qu’une colonne apparaît dans WHERE : la sélectivité, l’ordre, les autres index, la distribution et le coût de maintenance déterminent la valeur réelle.

Si les performances restent mauvaises, recherchez d’abord l’étage dominant : attente de connexion, verrouillage, CPU, E/S, tri, agrégat, résultat volumineux ou client. Actualisez les statistiques si nécessaire, corrigez les requêtes qui traitent trop de lignes, réduisez le nombre d’allers-retours, puis envisagez des résumés ou une architecture de lecture différente. L’indexation est un outil puissant, mais seulement une pièce de la stratégie de performance.

## Ressources officielles

- PostgreSQL, utilisation d’EXPLAIN : https://www.postgresql.org/docs/current/using-explain.html
- PostgreSQL, types d’index : https://www.postgresql.org/docs/current/indexes-types.html
- PostgreSQL, index multicolonnes : https://www.postgresql.org/docs/current/indexes-multicolumn.html
- PostgreSQL, index partiels : https://www.postgresql.org/docs/current/indexes-partial.html
- PostgreSQL, examen de l’usage des index : https://www.postgresql.org/docs/current/indexes-examine.html
- MySQL, EXPLAIN : https://dev.mysql.com/doc/refman/8.4/en/explain.html

La performance devient reproductible lorsque l’équipe mesure le comportement réel, formule une hypothèse, change une seule variable importante, compare les résultats et documente les limites du test. Le planificateur n’est pas un adversaire à forcer; il prend des décisions à partir d’un modèle, et le DBA l’aide à disposer de bonnes statistiques, d’un schéma adapté et d’un accès réellement utile.
