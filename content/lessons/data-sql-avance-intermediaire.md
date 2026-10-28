# Sous-requêtes, CTE, Procédures stockées — Intermédiaire

> **Mise en contexte.** La plateforme d’apprentissage possède maintenant des centaines de milliers d’inscriptions, d’évaluations et d’activités. Les requêtes simples suffisent à afficher une liste, mais les besoins métier deviennent plus complexes : chercher les apprenants qui n’ont jamais passé de quiz, comparer les meilleurs résultats de chaque cours, calculer des tendances par mois, reconstruire une chaîne de prérequis, ou effectuer une opération métier en plusieurs étapes. Le défi n’est pas d’écrire la requête la plus sophistiquée. Il faut choisir la forme la plus claire, préserver le sens en présence de valeurs NULL, maîtriser le coût d’exécution et placer les règles d’intégrité au bon endroit.

## Objectifs et parcours pratique

Ce cours suppose que vous connaissez SELECT, les jointures, GROUP BY, les agrégats, les contraintes et les transactions de base. À l’issue du parcours, vous saurez distinguer une sous-requête scalaire, une sous-requête relationnelle et une sous-requête corrélée; choisir entre EXISTS, IN, NOT EXISTS et les jointures; organiser une requête avec une expression de table commune (CTE); parcourir un graphe avec une CTE récursive; utiliser les fonctions de fenêtre sans perdre le détail des lignes; et choisir quand une règle appartient à une procédure stockée plutôt qu’au code applicatif.

Les exemples sont principalement écrits pour PostgreSQL. Les concepts SQL sont souvent transférables à MySQL, mais la syntaxe de création des procédures, les types de paramètres, la gestion des transactions, les extensions et les possibilités d’optimisation varient. Chaque exemple doit être exécuté sur une base de laboratoire avant d’être intégré à une application. Il est important de séparer la syntaxe portable des particularités d’un moteur.

Le fil rouge est une plateforme de formation. Elle contient des apprenants, des cours, des inscriptions, des quiz et des tentatives. Les données utilisées sont synthétiques. Les noms et résultats ne représentent personne de réel. Les exercices de modification sont conçus pour une base dédiée, et non pour une production.

## 1. Pourquoi les requêtes avancées doivent conserver un sens précis

Une requête SQL décrit un résultat attendu, pas nécessairement l’ordre procédural exact dans lequel un programme devrait parcourir les lignes. Le moteur peut transformer la requête, réordonner des jointures, intégrer une sous-requête ou choisir un autre chemin d’accès si les règles relationnelles lui permettent de préserver la sémantique. Cette liberté rend SQL puissant; elle oblige aussi le développeur à exprimer le résultat avec précision.

Les requêtes deviennent difficiles lorsque plusieurs relations doivent être comparées, lorsque l’absence de données est significative, ou lorsque l’on doit calculer un classement sans supprimer le détail des lignes. Une sous-requête peut exprimer une condition d’existence, une comparaison à un agrégat ou une table intermédiaire. Une CTE peut nommer une étape logique. Une fenêtre analytique peut enrichir chaque ligne avec un total ou un rang. Une procédure stockée peut centraliser une opération transactionnelle lorsqu’un tel emplacement est justifié.

La première règle est de définir le résultat avant d’écrire la syntaxe. Par exemple, « apprenants sans tentative » n’est pas la même chose que « apprenants dont toutes les tentatives sont échouées ». La première recherche l’absence de ligne associée. La seconde exige au moins une tentative et vérifie leurs résultats. Si aucune tentative n’existe, une moyenne est NULL, pas zéro; assimiler ces deux valeurs peut changer le sens métier.

La deuxième règle est de préciser le grain du résultat. Une ligne par apprenant? Une ligne par couple apprenant-cours? Une ligne par tentative? Beaucoup d’erreurs de comptage proviennent d’une jointure qui multiplie les lignes avant un agrégat. Une requête peut retourner un résultat plausible tout en comptant deux fois les tentatives ou les inscriptions.

La troisième règle est d’anticiper les cas limites : absence de lignes, doublons, valeurs NULL, égalités de score, fuseaux horaires, données incohérentes et valeurs invalides. Les cas limites ne sont pas des détails à traiter après le déploiement; ils font partie de la définition du résultat.

## 2. Sous-requête scalaire

Une sous-requête scalaire renvoie une seule valeur : une seule colonne et au plus une ligne. Elle est utile quand une valeur calculée complète le contexte d’une requête. Dans PostgreSQL, si une telle sous-requête renvoie plusieurs lignes, une erreur est produite. Si elle ne renvoie aucune ligne, la valeur résultante est NULL. Cette distinction doit être comprise avant d’utiliser une sous-requête pour une règle métier.

Exemple : afficher chaque cours avec le nombre d’inscriptions.

~~~sql
SELECT
    c.id,
    c.titre,
    (
        SELECT count(*)
        FROM inscriptions i
        WHERE i.cours_id = c.id
    ) AS nombre_inscriptions
FROM cours c
ORDER BY c.titre;
~~~

La sous-requête est corrélée parce qu’elle utilise l’identifiant de la ligne courante de cours. Cela ne signifie pas automatiquement que le moteur exécute un scan complet séparé pour chaque cours. Le planificateur peut transformer certaines formes, et les index ainsi que les statistiques influencent le plan choisi. Il faut analyser le plan réel lorsque la volumétrie devient importante.

Une alternative est l’agrégat avec jointure :

~~~sql
SELECT
    c.id,
    c.titre,
    count(i.id) AS nombre_inscriptions
FROM cours c
LEFT JOIN inscriptions i ON i.cours_id = c.id
GROUP BY c.id, c.titre
ORDER BY c.titre;
~~~

Les deux formes peuvent être adaptées au même besoin, mais il ne faut pas supposer qu’elles ont toujours le même coût ou le même sens. Une jointure à plusieurs tables de détail peut multiplier les lignes et fausser un COUNT. Une sous-requête scalaire bien ciblée peut parfois éviter cette multiplication; un agrégat global peut être plus efficace lorsque beaucoup de lignes sont concernées. Comparez les plans et gardez la forme la plus explicite.

## 3. Sous-requêtes relationnelles, IN et EXISTS

Une sous-requête relationnelle renvoie un ensemble de lignes. IN teste si une valeur correspond à l’un des éléments de cet ensemble. EXISTS vérifie si au moins une ligne satisfait une condition. EXISTS exprime clairement une question d’existence; il n’a pas besoin de retourner une valeur utile dans la sous-requête.

Pour rechercher les apprenants ayant au moins une inscription :

~~~sql
SELECT a.id, a.email
FROM apprenants a
WHERE EXISTS (
    SELECT 1
    FROM inscriptions i
    WHERE i.apprenant_id = a.id
);
~~~

Pour trouver ceux qui n’ont aucune inscription, utilisez NOT EXISTS :

~~~sql
SELECT a.id, a.email
FROM apprenants a
WHERE NOT EXISTS (
    SELECT 1
    FROM inscriptions i
    WHERE i.apprenant_id = a.id
);
~~~

Le raisonnement est direct : pour chaque apprenant, il suffit de savoir si une ligne associée existe. Le moteur peut s’arrêter dès qu’il trouve une correspondance lorsque le plan le permet. Un index sur inscriptions(apprenant_id) peut aider, mais il doit être évalué sur les requêtes réelles.

NOT IN mérite une attention particulière en présence de NULL. Si la sous-requête contient NULL et qu’aucune égalité n’est vraie, le résultat peut être UNKNOWN plutôt que TRUE. Une condition WHERE conserve uniquement les lignes où la condition est TRUE. Cela surprend souvent lorsqu’un NOT IN semble omettre toutes les lignes.

~~~sql
-- Forme potentiellement piégeuse si inscriptions.apprenant_id peut contenir NULL.
SELECT a.id
FROM apprenants a
WHERE a.id NOT IN (
    SELECT i.apprenant_id
    FROM inscriptions i
);
~~~

Une solution robuste consiste souvent à utiliser NOT EXISTS, qui exprime l’absence de correspondance indépendamment de cette ambiguïté :

~~~sql
SELECT a.id
FROM apprenants a
WHERE NOT EXISTS (
    SELECT 1
    FROM inscriptions i
    WHERE i.apprenant_id = a.id
);
~~~

La correction ne signifie pas que NOT IN est toujours mauvais; c’est le comportement des valeurs NULL qui impose de raisonner sur les contraintes et les données. Si la colonne est garantie NOT NULL, la forme NOT IN peut avoir un comportement simple. Il est cependant souvent plus lisible de dire précisément quelle correspondance doit être absente.

## 4. Sous-requêtes corrélées et anti-jointures

Une sous-requête corrélée fait référence à la ligne de la requête extérieure. Elle peut exprimer une règle fine, comme la sélection de la dernière tentative par apprenant ou le test de l’existence d’un résultat supérieur à un seuil. Le risque n’est pas la corrélation elle-même, mais l’ignorance de la cardinalité, des valeurs NULL et du plan choisi.

Exemple : afficher les tentatives dont le score est supérieur à la moyenne globale des scores disponibles.

~~~sql
SELECT t.id, t.apprenant_id, t.score
FROM tentatives_quiz t
WHERE t.score > (
    SELECT avg(t2.score)
    FROM tentatives_quiz t2
    WHERE t2.score IS NOT NULL
);
~~~

La moyenne globale est une valeur scalaire qui ne dépend pas de la ligne extérieure. Certains moteurs calculent ou mettent en cache cette sous-requête; dans tous les cas, si la requête devient complexe, mesurez son plan. Une requête corrélée plus complexe peut être coûteuse lorsqu’elle se répète sur beaucoup de lignes, surtout si elle ne dispose d’aucun index adapté.

Les anti-jointures recherchent une absence de correspondance. Elles peuvent s’écrire avec NOT EXISTS ou avec LEFT JOIN suivi d’un test IS NULL sur une colonne non nullable de la relation droite. La première forme est souvent plus facile à lire et moins sensible aux erreurs de projection.

~~~sql
SELECT a.id, a.email
FROM apprenants a
LEFT JOIN inscriptions i ON i.apprenant_id = a.id
WHERE i.id IS NULL;
~~~

Cette version est valide si i.id ne peut pas être NULL lorsqu’une ligne d’inscription existe, ce qui est le cas d’une clé primaire. Attention au filtre appliqué sur la table droite : placer une condition dans WHERE plutôt que dans ON peut transformer une jointure externe en comportement proche d’une jointure interne. Il faut comprendre si l’on veut éliminer les apprenants sans inscription ou seulement ceux dont une inscription répond à un critère.

## 5. Tables dérivées et LATERAL

Une table dérivée est une sous-requête placée dans FROM. Elle transforme une étape de calcul en relation nommée localement. Elle est utile pour agréger des lignes avant de les joindre à une autre relation. Cette organisation clarifie le grain et évite certains doubles comptages.

~~~sql
SELECT
    a.id,
    a.email,
    resume.nombre_tentatives,
    resume.meilleur_score
FROM apprenants a
LEFT JOIN (
    SELECT
        t.apprenant_id,
        count(*) AS nombre_tentatives,
        max(t.score) AS meilleur_score
    FROM tentatives_quiz t
    GROUP BY t.apprenant_id
) AS resume ON resume.apprenant_id = a.id
ORDER BY a.id;
~~~

L’agrégat réduit d’abord les tentatives à une ligne par apprenant. En le joignant aux apprenants, la requête conserve un grain clair. Une jointure brute entre apprenants, inscriptions et tentatives pourrait produire plusieurs lignes par apprenant avant le COUNT, en combinant toutes les inscriptions avec toutes les tentatives.

LATERAL, pris en charge par PostgreSQL et dans des formes similaires par d’autres moteurs, permet à une sous-requête du FROM de référencer les éléments précédents de ce même FROM. Cela sert notamment à sélectionner quelques lignes dépendantes de chaque parent. Exemple, récupérer les trois dernières tentatives par apprenant :

~~~sql
SELECT a.id, a.email, t.id AS tentative_id, t.score, t.commencee_le
FROM apprenants a
LEFT JOIN LATERAL (
    SELECT t.id, t.score, t.commencee_le
    FROM tentatives_quiz t
    WHERE t.apprenant_id = a.id
    ORDER BY t.commencee_le DESC, t.id DESC
    LIMIT 3
) t ON true
ORDER BY a.id, t.commencee_le DESC;
~~~

Cette forme est expressive, mais sa performance dépend du nombre de parents, des index et de la sélectivité. Un index combinant apprenant_id et commencee_le peut être pertinent, mais un index doit correspondre à la requête réellement mesurée. Dans certains scénarios, une fonction de fenêtre est une autre solution. La lisibilité et la capacité de test doivent guider le choix avant l’optimisation.

## 6. CTE : nommer les étapes d’une requête

Une expression de table commune, souvent appelée CTE, est définie au moyen de WITH. Elle permet de donner un nom à une relation intermédiaire, puis de la réutiliser dans la requête principale. Une CTE est particulièrement utile lorsqu’une requête contient plusieurs étapes métier : sélectionner les tentatives valides, calculer une moyenne par cours, classer les résultats et extraire les cours qui ont besoin d’une intervention.

~~~sql
WITH tentatives_valides AS (
    SELECT apprenant_id, cours_id, score
    FROM tentatives_quiz
    WHERE terminee_le IS NOT NULL
      AND score IS NOT NULL
),
moyennes_par_cours AS (
    SELECT cours_id, avg(score) AS moyenne
    FROM tentatives_valides
    GROUP BY cours_id
)
SELECT c.id, c.titre, m.moyenne
FROM cours c
JOIN moyennes_par_cours m ON m.cours_id = c.id
WHERE m.moyenne < 70
ORDER BY m.moyenne;
~~~

La CTE ne doit pas être utilisée seulement pour donner à une requête un aspect sophistiqué. Son intérêt est de mettre en évidence une étape nommée, d’éviter les répétitions et d’aider à raisonner sur le grain des données. Une CTE non récursive ne constitue pas systématiquement une table temporaire matérialisée. Le moteur peut l’intégrer au plan ou lui donner un traitement spécifique selon la version, le nombre de références et les options utilisées.

PostgreSQL permet notamment de demander MATERIALIZED ou NOT MATERIALIZED pour certaines CTE non récursives. Une matérialisation peut éviter de recalculer une étape chère si elle est réutilisée, mais elle peut aussi empêcher certaines optimisations poussées à travers cette étape. NOT MATERIALIZED peut permettre des optimisations supplémentaires dans les contextes appropriés, mais ne doit pas être appliqué sans comprendre les effets. Les comportements ont évolué entre versions; consultez la documentation actuelle de votre moteur.

Les CTE sont aussi disponibles pour les instructions de modification dans les moteurs qui les prennent en charge, avec des différences de syntaxe et de garanties. Une requête qui utilise une CTE pour mettre à jour des lignes doit préciser quelles lignes seront changées, vérifier le nombre de lignes touchées et tenir compte de la concurrence. Le fait que le SQL soit organisé en plusieurs étapes ne remplace pas la transaction ni la validation des règles métier.

## 7. CTE récursive : parcourir un graphe

Une CTE récursive sert à exprimer un calcul répétitif sur un ensemble qui s’élargit étape après étape. Parmi les usages typiques figurent les arbres hiérarchiques, les chaînes de prérequis, les catégories imbriquées et les relations parent-enfant. Dans PostgreSQL, WITH RECURSIVE définit une partie initiale, appelée terme d’ancrage, puis une partie récursive qui se réfère à l’ensemble produit précédemment.

Considérons une table prerequis(cours_id, prerequis_id). On peut parcourir les prérequis directs puis leurs propres prérequis. Une requête peut inclure la profondeur et un chemin pour aider à comprendre les résultats :

~~~sql
WITH RECURSIVE parcours AS (
    SELECT
        p.cours_id AS cours_depart,
        p.prerequis_id AS cours_courant,
        1 AS profondeur,
        ARRAY[p.cours_id, p.prerequis_id] AS chemin
    FROM prerequis p
    WHERE p.cours_id = 900

    UNION ALL

    SELECT
        parcours.cours_depart,
        p.prerequis_id,
        parcours.profondeur + 1,
        parcours.chemin || p.prerequis_id
    FROM parcours
    JOIN prerequis p ON p.cours_id = parcours.cours_courant
    WHERE NOT p.prerequis_id = ANY(parcours.chemin)
)
SELECT cours_depart, cours_courant, profondeur, chemin
FROM parcours
ORDER BY profondeur, cours_courant;
~~~

Cette version est propre à PostgreSQL, notamment à cause du type tableau. Sur d’autres moteurs, le chemin peut être stocké dans une représentation textuelle ou au moyen d’un type spécifique. Le contrôle de chemin cherche à empêcher de revisiter un nœud déjà présent dans le chemin courant, ce qui aide à éviter une boucle infinie si les données contiennent un cycle. Il faut néanmoins tester les profondeurs et les cas limites.

Les CTE récursives peuvent consommer beaucoup de ressources lorsque le graphe est grand ou très connecté. Un bon schéma doit contrôler l’intégrité des relations et prévoir des limites quand la profondeur est bornée par la règle métier. Certaines structures hiérarchiques se prêtent mieux à des modèles spécialisés, à des tables de fermeture ou à des chemins matérialisés pour certains types d’accès. Il n’existe pas de forme universellement meilleure.

Le diagramme montre la progression conceptuelle :

~~~mermaid
flowchart TD
    A[Terme d'ancrage] --> B[Ensemble courant]
    B --> C[Étape récursive]
    C --> D{Nouvelles lignes ?}
    D -- Oui --> B
    D -- Non --> E[Résultat final]
    F[Contrôle de cycles] --> C
    G[Limite de profondeur] --> C
~~~

Avant d’exécuter une exploration récursive sur un graphe métier, définissez son objectif, le point de départ, la règle d’arrêt, le traitement des cycles et le volume maximal attendu. Testez avec un arbre simple, un nœud sans enfant, plusieurs niveaux, un nœud partagé et un graphe contenant volontairement un cycle. Ces données de test aident à prouver que la requête termine et renvoie exactement le résultat attendu.

## 8. Fonctions de fenêtre : analyser sans perdre les lignes

Une fonction de fenêtre effectue un calcul sur un ensemble de lignes associées, sans réduire le résultat à une ligne par groupe comme le fait habituellement GROUP BY. La clause OVER définit la fenêtre; PARTITION BY délimite les groupes; ORDER BY précise un ordre pour les calculs qui en dépendent. Les fonctions de fenêtre sont essentielles pour les classements, les totaux cumulés, les comparaisons aux lignes précédentes et le repérage des dernières activités.

Pour classer les tentatives par cours en conservant les lignes :

~~~sql
SELECT
    t.cours_id,
    t.apprenant_id,
    t.score,
    rank() OVER (
        PARTITION BY t.cours_id
        ORDER BY t.score DESC
    ) AS rang
FROM tentatives_quiz t
WHERE t.score IS NOT NULL;
~~~

RANK attribue le même rang aux ex æquo et saute des positions après un groupe d’égalité. DENSE_RANK conserve un rang compact. ROW_NUMBER attribue un numéro unique à chaque ligne, même si le score est identique; pour un résultat déterministe, ajoutez un critère de départage comme l’identifiant. Le choix dépend du sens métier : « rang partagé » et « position unique pour sélectionner une ligne » ne sont pas le même besoin.

Pour comparer chaque score au score précédent d’un même apprenant et cours, LAG peut fournir une valeur d’une ligne antérieure :

~~~sql
SELECT
    apprenant_id,
    cours_id,
    commencee_le,
    score,
    lag(score) OVER (
        PARTITION BY apprenant_id, cours_id
        ORDER BY commencee_le, id
    ) AS score_precedent
FROM tentatives_quiz
WHERE score IS NOT NULL;
~~~

Un ordre stable est essentiel. Si deux tentatives ont le même horodatage et que l’ordre n’est pas départagé, la valeur précédente peut être ambiguë. La fenêtre ne remplace pas les contraintes de données; elle utilise les données disponibles pour produire le calcul demandé.

Les cadres de fenêtre influencent également le résultat. Les fonctions comme SUM peuvent calculer un total cumulatif en fonction de l’ordre et du cadre. Une déclaration explicite ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW aide à rendre l’intention claire. Les règles par défaut concernant les pairs d’ordre peuvent surprendre lorsqu’il existe des valeurs égales. Lorsqu’un total doit être cumulatif par ligne, indiquez le cadre voulu et ajoutez un ordre déterministe.

~~~sql
SELECT
    cours_id,
    commencee_le,
    score,
    sum(score) OVER (
        PARTITION BY cours_id
        ORDER BY commencee_le, id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS total_cumulatif
FROM tentatives_quiz;
~~~

Un autre usage important est de sélectionner la dernière tentative pour chaque couple apprenant-cours. Une CTE avec ROW_NUMBER permet de classer puis filtrer les lignes :

~~~sql
WITH classees AS (
    SELECT
        t.*,
        row_number() OVER (
            PARTITION BY apprenant_id, cours_id
            ORDER BY commencee_le DESC, id DESC
        ) AS numero
    FROM tentatives_quiz t
)
SELECT *
FROM classees
WHERE numero = 1;
~~~

Cette forme est plus générale qu’une simple agrégation MAX(date), car elle permet de récupérer toutes les colonnes de la ligne gagnante de façon déterministe. Une agrégation seule peut trouver le dernier horodatage mais ne sait pas toujours quelle ligne contient les autres valeurs à afficher.

## 9. Fonctions et procédures stockées : choisir le bon emplacement

Une fonction ou une procédure stockée est du code exécuté par le moteur de base de données. Les fonctions peuvent retourner une valeur ou un ensemble selon leur définition. Les procédures sont conçues pour effectuer une opération appelée explicitement et, selon le moteur, peuvent avoir des possibilités spécifiques de contrôle transactionnel. La terminologie et les possibilités varient entre PostgreSQL, MySQL et d’autres SGBD; il ne faut pas traiter les mécanismes comme interchangeables.

Placer une règle dans le SGBD peut être utile lorsqu’elle doit être partagée par plusieurs applications, lorsqu’elle combine des opérations qui doivent être atomiques, ou lorsqu’un contrôle doit être appliqué près des données. Cela peut aussi créer un couplage fort avec le moteur, rendre les tests plus difficiles et disperser la logique métier entre l’application et la base. Il faut décider selon la propriété recherchée, pas sur une préférence dogmatique.

Une bonne candidate est une opération transactionnelle concise, clairement définie et liée à l’intégrité des données. Une mauvaise candidate peut être une procédure gigantesque qui orchestre des appels HTTP, envoie des courriels, exécute des règles commerciales changeant souvent ou cache des effets secondaires difficiles à tester. La frontière dépend de l’architecture, mais doit être documentée.

Exemple PostgreSQL : une fonction de lecture qui calcule le meilleur score d’un apprenant dans un cours.

~~~sql
CREATE OR REPLACE FUNCTION meilleur_score(
    p_apprenant_id BIGINT,
    p_cours_id BIGINT
)
RETURNS NUMERIC
LANGUAGE SQL
STABLE
AS $fonction$
    SELECT max(score)
    FROM tentatives_quiz
    WHERE apprenant_id = p_apprenant_id
      AND cours_id = p_cours_id
      AND score IS NOT NULL;
$fonction$;
~~~

STABLE est une caractéristique déclarative indiquant que, dans le contexte d’une instruction, la fonction ne modifie pas la base et renvoie une valeur stable pour les mêmes arguments et les mêmes données visibles. Le mot-clé ne rend pas une fonction stable par magie : son usage doit correspondre au comportement réel. Une fonction qui exécute une écriture ou dépend de l’horloge ne doit pas être étiquetée de façon incorrecte.

Une procédure PostgreSQL se définit avec CREATE PROCEDURE et s’invoque avec CALL; une fonction s’invoque normalement dans une expression ou une requête. La gestion des transactions à l’intérieur des procédures est soumise à des règles de contexte et diffère des fonctions. En MySQL, les syntaxes des paramètres et des procédures ont leurs spécificités. Consultez les guides officiels de votre version, puis encapsulez l’exemple dans une migration versionnée et un test automatisé.

~~~sql
-- Exemple d'invocation d'une procédure déjà définie.
CALL actualiser_resume_cours(900);
~~~

Cet exemple suppose qu’une procédure actualiser_resume_cours existe et accepte le paramètre indiqué. Ne le copiez pas en production en croyant qu’il s’agit d’une commande intégrée à PostgreSQL. L’objectif est de montrer la syntaxe d’appel; la définition réelle doit être écrite, revue, testée et incluse dans les migrations du projet.

## 10. Exceptions, idempotence et sécurité du code stocké

Les erreurs doivent être traitées sans masquer les anomalies. Une procédure qui intercepte toutes les exceptions puis retourne un succès fictif rend le diagnostic difficile et peut corrompre les données métier. Il vaut mieux attraper les erreurs pour lesquelles une réponse précise est prévue, transformer les exceptions attendues en résultat documenté et laisser remonter les problèmes inattendus afin que la transaction échoue clairement.

L’idempotence signifie qu’une opération répétée produit le même état final que sa première exécution, pour les mêmes paramètres et le même contexte. Une opération d’importation ou une tâche périodique devrait souvent pouvoir être rejouée après un timeout sans créer de doublon. On peut utiliser une clé de déduplication, une contrainte unique, une table de suivi des lots et une transaction. Une fonction stockée n’est pas idempotente par défaut; cette propriété doit être pensée et testée.

Les procédures stockées doivent suivre le moindre privilège. Si une procédure s’exécute avec les droits de son propriétaire, elle peut devenir un point de passage privilégié. Dans PostgreSQL, les fonctions SECURITY DEFINER exigent une prudence particulière : vérifier l’identité qui appelle, limiter les droits du propriétaire, contrôler la recherche des objets via search_path et éviter les constructions SQL dynamiques vulnérables. L’exécution de SQL dynamique doit privilégier des paramètres pour les valeurs, une liste blanche pour les noms d’objets et une validation forte des entrées.

Ne concaténez pas une chaîne fournie par l’utilisateur directement dans le texte SQL. Les paramètres protègent les valeurs, mais ne peuvent généralement pas remplacer arbitrairement un nom de table ou une colonne. Pour ces cas, utilisez une correspondance explicite entre une option autorisée et un identifiant connu. Le code stocké mérite une revue de sécurité et un test de permissions au même titre que le code applicatif.

## 11. SQL préparé, paramètres et requêtes dynamiques

Les instructions préparées séparent la structure SQL des valeurs de données. Elles réduisent le risque d’injection SQL et peuvent être réutilisées. Leur intérêt n’est pas uniquement la performance : elles imposent au programme de traiter les valeurs comme des valeurs, et non comme une partie du langage SQL.

~~~sql
SELECT id, titre
FROM cours
WHERE categorie = $1
  AND publie = $2
ORDER BY titre;
~~~

Dans cet exemple de syntaxe de requête préparée côté PostgreSQL, $1 et $2 sont des paramètres. Une bibliothèque applicative fournit les valeurs séparément au lieu de les concaténer. La syntaxe d’appel exacte dépend du pilote. Dans les procédures stockées, EXECUTE avec USING ou les mécanismes correspondants peuvent fournir des paramètres pour du SQL dynamique.

Il existe une différence entre paramétrer une valeur et choisir un identifiant dynamique. On peut préparer une requête qui compare categorie à une valeur; on ne peut pas remplacer de manière universelle un nom de colonne par un paramètre ordinaire. Si une interface permet à l’utilisateur de choisir un ordre de tri, construisez le choix à partir d’une liste blanche telle que titre, date de création ou niveau, puis ajoutez un sens ASC/DESC validé. N’insérez jamais une expression de tri arbitraire fournie par une entrée non fiable.

Le SQL dynamique peut être légitime pour des outils d’administration, des rapports paramétrables ou des opérations sur plusieurs tables connues. Il doit cependant conserver une séparation stricte entre la structure autorisée et les données fournies. La journalisation devrait indiquer l’opération et un identifiant de corrélation, sans publier des secrets ni des informations personnelles inutiles.

## 12. Atelier : créer des analyses reproductibles

Créez une base de test ou utilisez un schéma jetable. Voici un modèle minimal qui permet d’expérimenter les sous-requêtes, les fenêtres et les agrégats.

~~~sql
CREATE TABLE apprenants (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE cours (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    titre TEXT NOT NULL
);

CREATE TABLE tentatives_quiz (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    apprenant_id BIGINT NOT NULL REFERENCES apprenants(id),
    cours_id BIGINT NOT NULL REFERENCES cours(id),
    score NUMERIC(5,2),
    commencee_le TIMESTAMPTZ NOT NULL DEFAULT now(),
    terminee_le TIMESTAMPTZ
);
~~~

Insérez plusieurs apprenants, au moins trois cours, des tentatives réussies et échouées, une valeur de score NULL et un apprenant sans tentative. Il faut volontairement inclure des ex æquo et plusieurs tentatives pour un même couple apprenant-cours. Ces éléments permettent de vérifier les limites de IN, NOT EXISTS, MAX, AVG et RANK.

Réalisez ensuite les tâches suivantes dans cet ordre :
1. Affichez les apprenants sans tentative avec NOT EXISTS.
2. Calculez le nombre de tentatives et la moyenne par cours.
3. Affichez chaque tentative avec la moyenne de son cours à l’aide d’une fonction de fenêtre.
4. Sélectionnez la dernière tentative par apprenant et cours.
5. Calculez le classement par cours et expliquez le comportement des ex æquo.
6. Parcourez la relation de prérequis d’un cours avec une CTE récursive.
7. Comparez les plans de deux formes logiquement équivalentes lorsque le volume le justifie.
8. Créez une fonction de lecture, testez-la avec un cours sans tentative et observez que la valeur renvoyée peut être NULL.

Après chaque requête, vérifiez le grain du résultat. Comptez manuellement les lignes attendues sur un très petit jeu de données. Puis vérifiez que les valeurs NULL, les doublons et les absences de lignes sont traités comme prévu. Il est plus facile de détecter une erreur sur neuf lignes choisies que sur un rapport de plusieurs millions de lignes.

## 13. Modèle de test et cas limites

Les tests doivent vérifier plus que l’exécution sans erreur. Pour une sous-requête scalaire, créez un cas avec aucune correspondance puis un cas avec plusieurs correspondances si la contrainte ne garantit pas l’unicité. Pour NOT IN, insérez volontairement un NULL dans un jeu de test correspondant à une colonne nullable et comparez le résultat à NOT EXISTS. Pour les fonctions de fenêtre, incluez des scores identiques et deux tentatives ayant le même horodatage.

Les procédures doivent être testées avec des paramètres valides, des paramètres absents, des identifiants inexistants, des droits insuffisants et une erreur provoquée en milieu d’opération. Vérifiez l’état final après l’échec : une procédure qui laisse une moitié de l’opération validée ne respecte peut-être pas la garantie attendue. Les tests doivent couvrir la transaction complète, et non seulement une réponse de fonction.

Les valeurs de date et heure doivent utiliser le type qui correspond à la sémantique. Si l’application stocke des instants globaux, utilisez un type avec fuseau et une convention documentée. Les calculs de jours locaux, les horaires d’été et les dates sans heure peuvent nécessiter des traitements distincts. Une fonction de fenêtre triée par date ne résout pas à elle seule les ambiguïtés entre lignes égales.

## 14. Exercices corrigés

### Exercice 1 — Apprenants sans quiz

Écrivez une requête qui affiche les apprenants n’ayant terminé aucun quiz. Une ligne de tentative peut exister sans valeur terminee_le.

**Correction :**

~~~sql
SELECT a.id, a.email
FROM apprenants a
WHERE NOT EXISTS (
    SELECT 1
    FROM tentatives_quiz t
    WHERE t.apprenant_id = a.id
      AND t.terminee_le IS NOT NULL
);
~~~

La requête cherche l’absence de tentative terminée, pas forcément l’absence de toute tentative. Si l’objectif métier était « aucun historique, même inachevé », il faudrait retirer la condition terminee_le. Cette distinction doit apparaître dans les noms de rapport et les tests.

### Exercice 2 — Dernier score

Affichez la dernière tentative de chaque apprenant pour chaque cours. En cas d’égalité d’horodatage, choisissez l’identifiant le plus grand.

**Correction :**

~~~sql
WITH classes AS (
    SELECT
        t.*,
        row_number() OVER (
            PARTITION BY apprenant_id, cours_id
            ORDER BY commencee_le DESC, id DESC
        ) AS rn
    FROM tentatives_quiz t
)
SELECT id, apprenant_id, cours_id, score, commencee_le
FROM classes
WHERE rn = 1;
~~~

ROW_NUMBER garantit une seule ligne gagnante par groupe grâce à l’ordre de départage. Il ne suffit pas de calculer MAX(commencee_le), car cette valeur ne désigne pas à elle seule les autres colonnes de la ligne.

### Exercice 3 — Moyenne par cours sans double comptage

Un rapport joint tentatives, inscriptions et cours, puis calcule AVG(score). Pourquoi la moyenne peut-elle être fausse?

**Correction.** Si une tentative est combinée avec plusieurs lignes d’inscription ou une autre relation de détail, elle peut être répétée dans l’ensemble intermédiaire. Selon la jointure, des scores identiques sont comptés plusieurs fois. Il faut définir le grain voulu et pré-agréger les relations à la granularité appropriée. Une CTE avec une ligne par cours ou par tentative peut clarifier le calcul. Vérifiez le nombre de lignes avant et après chaque jointure.

### Exercice 4 — Fonction ou procédure?

Une opération doit enregistrer une tentative, vérifier les règles, mettre à jour un agrégat et retourner un identifiant. Doit-elle nécessairement être une procédure stockée?

**Correction.** Non. Il faut comparer le besoin de transaction atomique, le nombre de clients qui partagent cette règle, les pratiques de migration, la facilité de test, les dépendances au moteur et les exigences de sécurité. Une opération stockée peut être appropriée si plusieurs applications doivent utiliser la même transaction; une transaction applicative peut aussi convenir si le service contrôle clairement tous les accès. Le choix doit être documenté et testé.

### Exercice 5 — Pourquoi NOT IN ne retourne rien?

Une requête NOT IN sur une sous-requête vide fonctionne, mais après l’ajout d’une ligne avec clé NULL le rapport ne retourne plus les résultats attendus.

**Correction.** La comparaison avec un ensemble qui contient NULL peut produire UNKNOWN. WHERE élimine les lignes dont la condition est UNKNOWN. Réécrivez la logique avec NOT EXISTS ou garantissez, par une contrainte et un contrat de données, que la colonne n’est jamais NULL. Testez les deux cas de façon explicite.

## 15. Défi final : un rapport de progression complet

Vous devez créer un rapport comportant une ligne par apprenant et cours où au moins une tentative terminée existe. Il faut exposer le nombre de tentatives terminées, le meilleur score, le score de la dernière tentative, le rang du meilleur score dans le cours et une indication si le meilleur score atteint 80. Les ex æquo doivent conserver un rang partagé. Les tentatives inachevées ne doivent pas compter dans les indicateurs.

### Correction proposée

~~~sql
WITH terminees AS (
    SELECT
        t.id,
        t.apprenant_id,
        t.cours_id,
        t.score,
        t.terminee_le,
        row_number() OVER (
            PARTITION BY t.apprenant_id, t.cours_id
            ORDER BY t.terminee_le DESC, t.id DESC
        ) AS dernier_numero
    FROM tentatives_quiz t
    WHERE t.terminee_le IS NOT NULL
),
resume AS (
    SELECT
        apprenant_id,
        cours_id,
        count(*) AS nombre_tentatives_terminees,
        max(score) AS meilleur_score
    FROM terminees
    GROUP BY apprenant_id, cours_id
),
dernier AS (
    SELECT apprenant_id, cours_id, score AS score_dernier
    FROM terminees
    WHERE dernier_numero = 1
),
classement AS (
    SELECT
        cours_id,
        apprenant_id,
        meilleur_score,
        rank() OVER (
            PARTITION BY cours_id
            ORDER BY meilleur_score DESC NULLS LAST
        ) AS rang_meilleur_score
    FROM resume
)
SELECT
    r.apprenant_id,
    r.cours_id,
    r.nombre_tentatives_terminees,
    r.meilleur_score,
    d.score_dernier,
    c.rang_meilleur_score,
    CASE
        WHEN r.meilleur_score >= 80 THEN true
        ELSE false
    END AS seuil_atteint
FROM resume r
JOIN dernier d
  ON d.apprenant_id = r.apprenant_id
 AND d.cours_id = r.cours_id
JOIN classement c
  ON c.apprenant_id = r.apprenant_id
 AND c.cours_id = r.cours_id
ORDER BY r.cours_id, c.rang_meilleur_score, r.apprenant_id;
~~~

La correction matérialise trois décisions séparées : le filtre des tentatives terminées, l’agrégation au niveau apprenant-cours et le classement au niveau cours. Le classement du meilleur score est calculé après l’agrégat, ce qui évite de classer chaque tentative séparément. Le score NULL est conservé dans les nombres de tentatives terminées mais max ignore les NULL; si cette situation ne doit jamais exister, l’application doit la rejeter ou le rapport doit signaler explicitement les données manquantes. Les tests doivent vérifier une ligne avec score NULL, un cours avec un seul apprenant, un ex æquo et un apprenant possédant une tentative inachevée uniquement.

## 16. Liste de vérification et synthèse

Avant de publier une requête avancée, documentez le résultat attendu, le grain, le traitement des NULL, les règles d’ordre et les cas sans correspondance. Pour une CTE récursive, définissez le terme d’ancrage, l’arrêt et la gestion des cycles. Pour une fonction ou une procédure, clarifiez les droits, les effets secondaires, les erreurs, l’idempotence et le contrat de transaction. Pour les requêtes volumineuses, lisez le plan réel sur un environnement représentatif.

Les sous-requêtes scalaires sont utiles pour une valeur unique; EXISTS et NOT EXISTS expriment les conditions d’existence; les tables dérivées et CTE nomment des relations intermédiaires; les CTE récursives explorent des structures hiérarchiques; les fonctions de fenêtre calculent classement et tendances sans réduire les lignes. Les procédures stockées centralisent parfois des opérations, mais elles ajoutent aussi un couplage et un périmètre de sécurité spécifique. SQL avancé est donc autant une question de sémantique que de syntaxe.

## Ressources officielles

- PostgreSQL, expressions de table communes : https://www.postgresql.org/docs/current/queries-with.html
- PostgreSQL, fonctions de fenêtre : https://www.postgresql.org/docs/current/tutorial-window.html
- PostgreSQL, fonctions SQL et procédures : https://www.postgresql.org/docs/current/xfunc.html
- PostgreSQL, CALL : https://www.postgresql.org/docs/current/sql-call.html
- MySQL, sous-requêtes : https://dev.mysql.com/doc/refman/8.4/en/subqueries.html
- MySQL, fonctions de fenêtre : https://dev.mysql.com/doc/refman/8.4/en/window-functions.html

Vérifiez les différences de syntaxe, de transaction et de planification dans la version utilisée. Une requête lisible, testée sur des cas limites et mesurée dans son contexte est préférable à une requête plus compacte mais ambiguë.
