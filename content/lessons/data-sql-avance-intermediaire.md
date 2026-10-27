# Sous-requêtes, CTE et routines SQL — Intermédiaire

> **Mise en contexte.** Les requêtes SQL deviennent difficiles à maintenir lorsqu’elles mélangent plusieurs agrégations, des filtres dépendants, des calculs temporels et des règles métier. Les sous-requêtes, les expressions de table communes et les fonctions de fenêtre permettent de structurer cette complexité, mais elles ne dispensent pas de raisonner sur les cardinalités, les valeurs NULL, les doublons, les performances et les droits d’exécution. Une requête correcte doit exprimer la règle voulue, produire le bon résultat sur les cas limites et rester compréhensible pour la prochaine personne qui devra l’exploiter.

## Objectifs pédagogiques

À la fin du cours, vous saurez choisir entre sous-requête, jointure, CTE et fonction de fenêtre, expliquer les différences entre EXISTS et IN dans des cas courants, écrire des requêtes corrélées sans ignorer leur coût potentiel, structurer une requête à plusieurs étapes, utiliser les fonctions de fenêtre pour classer ou comparer des lignes, et comprendre quand une routine stockée apporte une valeur opérationnelle.

Vous devrez également pouvoir tester les règles de nullité, de cardinalité et de répétition, examiner un plan d’exécution, choisir une stratégie de pagination, protéger les routines avec des droits adaptés et documenter les différences entre les syntaxes de PostgreSQL et MySQL. Les exemples restent centrés sur les concepts portables ; certaines syntaxes et options sont propres à un moteur.

Le niveau intermédiaire suppose que vous maîtrisez les opérations courantes SELECT, JOIN, WHERE, GROUP BY et les contraintes relationnelles. Ce cours ne vise pas à mémoriser toutes les constructions du standard SQL. Il vise à savoir décomposer une règle complexe, choisir la construction adaptée et prouver que le résultat correspond au contrat métier.

## Prérequis et données d’essai

Les exemples utilisent trois tables conceptuelles :

~~~sql
CREATE TABLE customers (
  customer_id BIGINT PRIMARY KEY,
  customer_name VARCHAR(120) NOT NULL,
  region_code VARCHAR(20)
);

CREATE TABLE orders (
  order_id BIGINT PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
  order_date DATE NOT NULL,
  status VARCHAR(20) NOT NULL,
  total_amount DECIMAL(12,2) NOT NULL
);

CREATE TABLE order_items (
  order_id BIGINT NOT NULL REFERENCES orders(order_id),
  line_number INTEGER NOT NULL,
  product_code VARCHAR(50) NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
  PRIMARY KEY (order_id, line_number)
);
~~~

Créez des données synthétiques couvrant plusieurs clients, plusieurs commandes par client, des clients sans commande, des montants égaux et des dates identiques. Ajoutez aussi un cas de montant nul uniquement si le modèle autorise explicitement cette valeur. Ces cas sont plus utiles qu’un grand jeu aléatoire lorsque l’objectif est de comprendre la sémantique d’une requête.

Avant chaque exemple, formulez la question métier en une phrase. Ensuite, précisez le résultat attendu, notamment le niveau de détail : une ligne par client, une ligne par commande ou une ligne par article. De nombreuses erreurs SQL ne sont pas des erreurs de syntaxe ; ce sont des requêtes qui produisent un résultat plausible au mauvais niveau de détail.

## 1. Sous-requête : une requête dans une requête

Une sous-requête peut servir à produire une valeur, une liste de valeurs, une relation temporaire logique ou un test d’existence. La position de la sous-requête dans l’instruction détermine une partie de son contrat.

### 1.1 Sous-requête scalaire

Une sous-requête scalaire doit produire au plus une valeur dans le contexte où elle est utilisée. Exemple : obtenir les commandes qui dépassent le montant moyen des commandes :

~~~sql
SELECT order_id, customer_id, total_amount
FROM orders
WHERE total_amount > (
  SELECT AVG(total_amount)
  FROM orders
);
~~~

AVG retourne une valeur agrégée sur l’ensemble considéré. Le résultat est une comparaison avec une référence calculée. Le contrat doit être clair : moyenne de toutes les commandes, moyenne par région, moyenne du dernier trimestre ou moyenne des seules commandes validées ? Le choix du périmètre change le sens métier.

Une sous-requête scalaire qui renvoie plusieurs lignes peut faire échouer l’exécution. Si la règle suppose une seule ligne, rendez cette unicité explicite avec une contrainte ou un agrégat adapté. Ajouter arbitrairement LIMIT 1 pour masquer une ambiguïté peut rendre la requête techniquement exécutable tout en conservant une règle incorrecte.

### 1.2 Sous-requête comme source de données

Une sous-requête dans FROM peut construire une relation intermédiaire :

~~~sql
SELECT customer_id, order_count, total_spend
FROM (
  SELECT customer_id,
         COUNT(*) AS order_count,
         SUM(total_amount) AS total_spend
  FROM orders
  WHERE status = 'completed'
  GROUP BY customer_id
) AS customer_summary
WHERE order_count >= 3;
~~~

Cette forme rend visible la séparation entre agrégation et filtrage des agrégats. Selon le moteur, le planificateur peut transformer ou intégrer la sous-requête. N’imaginez pas qu’un bloc écrit entre parenthèses sera nécessairement matérialisé dans une table temporaire.

### 1.3 Sous-requête corrélée

Une sous-requête corrélée référence la ligne de la requête externe. Exemple : récupérer les clients ayant au moins une commande terminée :

~~~sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
WHERE EXISTS (
  SELECT 1
  FROM orders AS o
  WHERE o.customer_id = c.customer_id
    AND o.status = 'completed'
);
~~~

La sous-requête dépend du client courant. Logiquement, le test répond à la question « existe-t-il une ligne qui satisfait la condition ? ». Le moteur peut optimiser ce motif, mais il faut quand même regarder le plan lorsque la table est grande. Un index sur la clé de relation et les critères fréquents peut aider, sans être garanti optimal pour tous les volumes.

### 1.4 EXISTS et NOT EXISTS

EXISTS indique si la sous-requête renvoie au moins une ligne. Le contenu de SELECT n’est généralement pas utilisé pour la valeur logique ; SELECT 1 rend donc l’intention explicite.

Pour trouver les clients sans commande :

~~~sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
WHERE NOT EXISTS (
  SELECT 1
  FROM orders AS o
  WHERE o.customer_id = c.customer_id
);
~~~

Le test utilise la relation réellement définie entre les lignes. Il évite de produire un doublon de client lorsque plusieurs commandes satisfont la condition. Une jointure peut aussi convenir, mais elle doit préserver le niveau de détail et gérer correctement les cas sans correspondance.

### 1.5 IN, NOT IN et valeurs NULL

IN teste l’appartenance à un ensemble. Pour des valeurs non nulles, il est souvent facile à comprendre :

~~~sql
SELECT order_id, customer_id
FROM orders
WHERE customer_id IN (
  SELECT customer_id
  FROM customers
  WHERE region_code = 'LITTORAL'
);
~~~

Le comportement de NOT IN peut surprendre si la sous-requête contient NULL. Dans la logique SQL à trois valeurs, une comparaison avec NULL n’est ni vraie ni fausse au sens booléen classique : elle est inconnue. Une condition inconnue n’est pas retenue par WHERE. Pour exprimer « aucune ligne liée ne satisfait ce critère », NOT EXISTS est souvent une construction plus robuste, mais la relation à tester doit être écrite précisément.

Ne changez pas une construction uniquement sur une règle simpliste comme « EXISTS est toujours plus rapide ». Le plan dépend du moteur, des statistiques, de la sélectivité, des index et de la distribution des données. Le choix initial doit privilégier la sémantique correcte et la clarté ; la performance se mesure ensuite.

## 2. CTE : nommer les étapes d’une requête

Une expression de table commune, écrite avec WITH, donne un nom à une relation utilisée dans une requête. Elle facilite les requêtes qui doivent être comprises comme une suite d’étapes logiques.

~~~sql
WITH completed_orders AS (
  SELECT order_id, customer_id, total_amount
  FROM orders
  WHERE status = 'completed'
),
customer_totals AS (
  SELECT customer_id,
         COUNT(*) AS order_count,
         SUM(total_amount) AS total_spend
  FROM completed_orders
  GROUP BY customer_id
)
SELECT customer_id, order_count, total_spend
FROM customer_totals
WHERE total_spend >= 100000;
~~~

Cette structure sépare les commandes admissibles, l’agrégation client et le filtre final. Le résultat est plus facile à contrôler que la répétition du même sous-ensemble dans plusieurs endroits. Chaque étape peut être examinée isolément pendant l’analyse, ce qui réduit les erreurs de périmètre.

### 2.1 CTE et lisibilité

Une CTE ne doit pas être un nom compliqué ajouté à chaque opération triviale. La valeur vient de la séparation des règles. Les noms doivent décrire un ensemble ou un calcul, comme paid_orders, monthly_totals ou ranked_customers. Évitez names comme temp1, data2 ou final_final qui cachent l’intention.

Définissez pour chaque étape le niveau de détail. completed_orders contient une ligne par commande ; customer_totals contient une ligne par client présent dans l’ensemble ; la requête finale conserve ce niveau de détail. Si une étape joint des articles, elle peut multiplier les commandes par le nombre de lignes d’article. La somme doit alors être calculée au bon niveau afin de ne pas compter plusieurs fois le montant d’une commande.

### 2.2 CTE matérialisées ou intégrées

Le comportement d’une CTE dépend de la version et du moteur. Certains moteurs peuvent intégrer la CTE dans le plan global ; d’autres constructions ou options peuvent demander ou produire une matérialisation. Matérialiser une étape peut éviter un calcul répété, mais peut aussi créer un ensemble intermédiaire coûteux. L’intégration permet l’optimisation globale mais peut rendre les étapes moins évidentes dans le plan.

N’utilisez pas MATERIALIZED ou NOT MATERIALIZED comme une incantation. Vérifiez la documentation de la version et mesurez le plan avec des données représentatives. La stratégie retenue doit être justifiée par une observation : temps total, lignes lues, mémoire consommée, écritures temporaires ou réduction du travail répété.

### 2.3 CTE récursives

Une CTE récursive peut parcourir des structures hiérarchiques, par exemple une arborescence d’unités. Dans une forme générale, elle définit une partie initiale, puis une partie qui s’appuie sur les résultats déjà construits :

~~~sql
WITH RECURSIVE hierarchy AS (
  SELECT unit_id, parent_unit_id, unit_name, 0 AS depth
  FROM organization_units
  WHERE parent_unit_id IS NULL
  UNION ALL
  SELECT child.unit_id, child.parent_unit_id,
         child.unit_name, parent.depth + 1
  FROM organization_units AS child
  JOIN hierarchy AS parent
    ON child.parent_unit_id = parent.unit_id
)
SELECT unit_id, parent_unit_id, unit_name, depth
FROM hierarchy
ORDER BY depth, unit_id;
~~~

La partie initiale donne les racines et la partie récursive ajoute leurs enfants. Il faut définir le comportement en présence d’une référence circulaire, d’une hiérarchie très profonde ou d’un grand nombre d’enfants. Une vraie modélisation doit empêcher les cycles ou disposer d’une détection explicite. Un parcours récursif sans stratégie de cycle peut augmenter fortement le travail ou ne pas se terminer selon le moteur.

## 3. Fonctions de fenêtre : calculer sans réduire les lignes

GROUP BY produit généralement une ligne par groupe. Une fonction de fenêtre ajoute un calcul à chaque ligne tout en gardant les lignes du jeu de résultat. Cette propriété est essentielle pour classer les commandes, calculer des cumuls ou comparer une ligne à la précédente.

### 3.1 Classement

~~~sql
SELECT order_id, customer_id, total_amount,
       ROW_NUMBER() OVER (
         PARTITION BY customer_id
         ORDER BY total_amount DESC, order_id
       ) AS customer_rank
FROM orders;
~~~

PARTITION BY définit le groupe indépendant pour chaque client. ORDER BY définit l’ordre dans le groupe. L’identifiant de commande sert de critère secondaire afin de rendre l’ordre déterministe lorsque plusieurs montants sont égaux.

ROW_NUMBER attribue un rang distinct à chaque ligne. RANK et DENSE_RANK traitent les égalités différemment : RANK laisse des trous après une égalité, DENSE_RANK n’en laisse pas. Le choix dépend de la règle métier. Dire « top trois commandes par client » peut signifier trois lignes maximum ou toutes les commandes partageant un rang dans les trois premières positions. Il faut décider avant d’écrire la requête.

### 3.2 Comparer à la ligne précédente

~~~sql
SELECT customer_id, order_id, order_date, total_amount,
       LAG(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS previous_amount
FROM orders;
~~~

LAG permet d’accéder à une valeur précédente dans le cadre défini. LEAD permet d’accéder à une valeur suivante. Ce motif peut détecter des variations de montant, des écarts de temps ou des changements d’état. Il ne remplace pas une règle de validation ; il fournit le calcul nécessaire pour analyser le jeu de données.

### 3.3 Cumuls et cadre de fenêtre

~~~sql
SELECT customer_id, order_date, order_id, total_amount,
       SUM(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM orders;
~~~

Un cumul suppose un ordre significatif. Si deux commandes portent la même date, le tri secondaire rend le cumul reproductible. Les frames de fenêtre peuvent être basées sur ROWS ou RANGE et leur sémantique dépend de la construction utilisée. Vérifiez la documentation du moteur lorsque les égalités ou les valeurs de tri ont une signification particulière.

### 3.4 Fenêtres et déduplication

Une stratégie fréquente consiste à classer les versions d’un enregistrement, puis à garder la plus récente :

~~~sql
WITH versions AS (
  SELECT record_key, updated_at, source_version, payload,
         ROW_NUMBER() OVER (
           PARTITION BY record_key
           ORDER BY updated_at DESC, source_version DESC
         ) AS version_rank
  FROM inbound_records
)
SELECT record_key, updated_at, source_version, payload
FROM versions
WHERE version_rank = 1;
~~~

Avant de supprimer les autres lignes, définissez comment départager deux versions identiques, quelle source est prioritaire et ce que signifie « plus récente ». L’horodatage seul ne garantit pas l’ordre causal, surtout lorsque plusieurs systèmes alimentent la même table. Une règle explicite rend le résultat contrôlable.

## 4. Jointure, agrégation et pièges de cardinalité

Une requête peut être syntaxiquement correcte mais produire une somme erronée en multipliant les lignes. Supposons une commande de 100 avec trois articles. Une jointure de la commande à ses articles produit trois lignes qui peuvent toutes contenir le montant 100 de la commande. SUM(order_total) après cette jointure vaut alors 300, pas 100.

L’approche correcte consiste à décider du niveau de détail de chaque étape. Si l’objectif est la somme des commandes par client, agrégez la table orders avant de joindre aux articles, ou calculez les montants au niveau des lignes avec une règle précise. N’utilisez pas DISTINCT comme pansement général : il peut supprimer des lignes légitimes et masque le défaut de cardinalité.

Les tests doivent inclure des clients avec zéro commande, plusieurs commandes, des montants égaux et des commandes comportant plusieurs lignes. Comparez les résultats à un calcul manuel sur un jeu réduit. Un résultat inattendu doit déclencher une inspection du nombre de lignes après chaque étape.

## 5. Routines stockées : quand les utiliser

Une routine stockée encapsule une logique qui s’exécute dans le moteur. Elle peut être utile pour centraliser une opération transactionnelle, exposer une interface contrôlée, éviter de dupliquer une règle ou réduire certains échanges réseau. Elle n’est pas automatiquement meilleure qu’un service applicatif.

### 5.1 Fonction et procédure

Les distinctions précises entre fonction et procédure dépendent du moteur. Une fonction peut renvoyer une valeur ou une relation et être utilisée dans une requête selon la syntaxe du produit. Une procédure est généralement invoquée comme une opération. PostgreSQL et MySQL ont des règles spécifiques concernant les transactions, les retours et les options disponibles. Ne transférez pas mécaniquement une routine d’un moteur à l’autre.

Avant de créer une routine, posez quatre questions :
1. La logique doit-elle réellement être centralisée dans le moteur ?
2. Quel contrat d’entrée et de sortie doit être stable ?
3. Quels privilèges la routine doit-elle utiliser ?
4. Comment la versionner, tester, déployer et retirer ?

La logique stockée devient un composant logiciel à part entière. Elle doit avoir des tests, une revue, une version et une stratégie de déploiement.

### 5.2 Paramètres et SQL dynamique

Le SQL construit par concaténation avec des données externes peut conduire à une injection SQL. Utilisez les mécanismes de paramètres fournis par le moteur et le pilote. Si un nom de table ou de colonne ne peut pas être passé comme valeur paramétrée, il doit être choisi parmi une liste autorisée et cité avec la méthode spécifique du moteur. Ne considérez pas le remplacement de quotes comme une stratégie complète de sécurisation.

Une routine qui utilise les droits de son propriétaire peut avoir un périmètre supérieur à celui de l’appelant. Selon le moteur, il faut décider explicitement du mode de sécurité, contrôler les chemins de résolution des objets et limiter les droits d’exécution. Une routine privilégiée doit être considérée comme une frontière de sécurité.

### 5.3 Idempotence et transactions

Une opération est idempotente lorsque sa répétition avec les mêmes paramètres ne produit pas un effet supplémentaire non désiré. Cela compte dans les appels réseau, les traitements relancés après timeout et les tâches qui peuvent être exécutées deux fois.

Par exemple, « ajouter 10 au stock » n’est pas idempotent si une reprise répète la commande. « Appliquer l’événement d’entrée identifié par event_id une seule fois » peut être rendu idempotent à l’aide d’une contrainte d’unicité et d’une transaction. L’identifiant d’événement, la règle de déduplication et les retours d’erreur font partie du contrat métier.

## 6. Performance des sous-requêtes et CTE

La lisibilité est importante, mais une requête claire doit encore être évaluée à l’échelle. Les points à examiner comprennent le nombre de lignes examinées, les index choisis, les estimations de cardinalité, les tris, les tables temporaires, le nombre de répétitions d’une sous-requête et la quantité de données renvoyée au client.

### 6.1 EXPLAIN et EXPLAIN ANALYZE

PostgreSQL fournit EXPLAIN pour afficher le plan prévu et EXPLAIN ANALYZE pour exécuter la requête et comparer les estimations aux mesures. Les options disponibles varient selon la version. EXPLAIN ANALYZE exécute réellement l’instruction : une requête SELECT peut consommer des ressources ; une instruction d’écriture modifie potentiellement des données si elle n’est pas exécutée dans un cadre sûr. Utilisez un environnement de test et lisez la documentation avant d’ajouter des options.

Un plan d’exécution n’est pas seulement un arbre à regarder. Il faut comparer les lignes estimées et réellement obtenues, les opérations coûteuses, la présence d’un tri, les accès répétitifs, les lectures et les temps associés aux nœuds. Les chiffres ne s’interprètent pas toujours en les additionnant, car certaines durées peuvent inclure le travail des sous-nœuds.

### 6.2 Index et sélectivité

Un index peut accélérer une recherche, une jointure ou un tri, mais il a un coût de stockage et de mise à jour. Si la condition renvoie une grande partie de la table, le planificateur peut préférer une lecture séquentielle. C’est souvent raisonnable ; forcer un index n’est pas nécessairement une amélioration.

Un index composite doit tenir compte des colonnes filtrées, des opérateurs et du modèle de requête. Un index adapté à une recherche par customer_id puis order_date ne répond pas forcément aussi efficacement à une requête qui ne filtre que order_date. L’ordre des colonnes et la capacité à exploiter un préfixe sont des caractéristiques propres à la structure de l’index et au moteur.

### 6.3 Pagination stable

OFFSET/LIMIT peut être acceptable pour des petits résultats, mais un OFFSET élevé peut obliger le moteur à parcourir les lignes ignorées. Une pagination basée sur une clé de continuation peut mieux s’adapter aux jeux volumineux. L’ordre doit être déterministe, avec une clé qui départage les égalités. Si les données changent pendant la pagination, il faut aussi définir si le client accepte de voir un état vivant ou exige une vue cohérente.

## 7. Qualité des résultats et tests SQL

Une requête complexe doit être testée comme du code. Établissez des données minimales permettant de distinguer les cas normaux et les limites. Vérifiez le nombre de lignes, les doublons, les valeurs NULL, les égalités, les absences de correspondance et les cas d’ordre non déterminé.

### 7.1 Tests de contrat

Chaque requête importante doit répondre à ces questions :
- Quel est le niveau de détail attendu ?
- Quelle clé rend chaque ligne unique ?
- Les égalités produisent-elles un seul résultat ou plusieurs ?
- Que se passe-t-il lorsque la sous-requête ne renvoie aucune ligne ?
- Que signifie NULL dans cette règle ?
- L’ordre est-il garanti ?
- Les données concurrentes peuvent-elles changer le résultat entre deux opérations ?

Un test basé uniquement sur un grand ensemble de données peut passer par hasard. Un petit jeu discriminant fournit souvent une preuve plus claire. Il faut néanmoins compléter les tests unitaires par une charge plus réaliste pour la performance.

### 7.2 Comparaison indépendante

Pour valider une requête d’agrégation, préparez une petite table de référence avec un calcul manuel ou une logique indépendante. Si le SQL et le calcul de référence utilisent exactement le même raisonnement erroné, le test ne détectera rien. Une deuxième méthode de calcul, même peu performante, peut être utile sur un petit jeu.

## 8. Atelier pratique guidé : analyser des clients et leurs commandes

### But

Produire trois rapports avec le niveau de détail correct :
1. les clients ayant au moins trois commandes terminées ;
2. la commande la plus élevée par client ;
3. un cumul chronologique par client.

### Étapes

Commencez par charger des données synthétiques et vérifier les contraintes. Écrivez un rapport avec EXISTS, puis un rapport de classement avec ROW_NUMBER. Définissez un tri secondaire pour les montants égaux. Ajoutez le cumul par date et identifiant de commande.

~~~sql
WITH completed AS (
  SELECT order_id, customer_id, order_date, total_amount
  FROM orders
  WHERE status = 'completed'
),
customer_counts AS (
  SELECT customer_id, COUNT(*) AS order_count
  FROM completed
  GROUP BY customer_id
)
SELECT customer_id, order_count
FROM customer_counts
WHERE order_count >= 3;
~~~

~~~sql
WITH ranked_orders AS (
  SELECT order_id, customer_id, total_amount,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY total_amount DESC, order_id
         ) AS rn
  FROM orders
  WHERE status = 'completed'
)
SELECT order_id, customer_id, total_amount
FROM ranked_orders
WHERE rn = 1;
~~~

Ajoutez un client sans commande, deux commandes de même montant et une commande annulée. Vérifiez que la requête n’inclut pas une commande non terminée si la règle métier l’exclut. Vérifiez aussi que le plus grand montant produit exactement une ligne par client dans le cas ROW_NUMBER.

### Critères d’acceptation

- La granularité de chaque sortie est décrite.
- Les résultats sur le jeu réduit ont été vérifiés indépendamment.
- Les égalités sont traitées explicitement.
- Les conditions sur NULL sont documentées.
- La requête est lisible et ses étapes sont nommées par leur fonction.
- Le plan d’exécution a été examiné pour le jeu de test et ses limites sont consignées.

## 9. Étude de cas détaillée : le chiffre d’affaires est multiplié

### Situation

Un tableau de bord présente le chiffre d’affaires par client. Après l’ajout d’un JOIN vers order_items, le total double ou triple sans erreur SQL.

### Analyse

La requête part de orders, dont le montant total est stocké une fois par commande. La jointure vers order_items ajoute une ligne pour chaque article. Une commande comportant trois articles apparaît donc trois fois, et le montant total est répété sur chaque ligne. SUM appliqué au montant de la commande après cette jointure additionne le même montant plusieurs fois.

### Correction

Si le contrat métier exige le total des commandes, calculez d’abord l’ensemble au niveau commande, puis agrégez par client. Si le rapport exige un chiffre d’affaires par produit, utilisez au contraire le prix de chaque ligne d’article selon les règles de remise, de taxe et d’annulation. Les deux indicateurs peuvent avoir des noms proches mais ne représentent pas le même calcul.

### Preuve

Créez une commande de 100 avec trois lignes d’article. La somme du montant commande doit être 100 dans le rapport client. La somme des lignes d’article doit être égale au total attendu selon le modèle, par exemple 100 si les valeurs ont été choisies pour correspondre à ce total. Le test doit échouer avec l’ancienne requête et passer avec la correction. Conservez ce test dans la suite de non-régression.

## 10. Exercices corrigés

### Exercice 1 — Clients sans commande

**Énoncé.** Vous devez lister les clients qui n’ont aucune commande. Un collègue propose une jointure externe suivie d’un test sur une colonne de commande. Que faut-il vérifier ?

**Correction.** Le test doit utiliser une colonne non nullable de la relation liée, souvent la clé primaire. NOT EXISTS peut exprimer directement l’absence d’une commande. Vérifiez aussi les filtres sur les commandes : si vous ne cherchez que les commandes terminées, un client ayant une commande annulée peut être considéré comme sans commande terminée. La définition doit être explicite.

### Exercice 2 — Différence entre RANK et ROW_NUMBER

**Énoncé.** Un client a trois commandes avec montants 100, 100 et 80. Vous devez afficher toutes les commandes appartenant au rang commercial numéro un, puis afficher exactement une ligne.

**Correction.** RANK peut attribuer le rang 1 aux deux commandes de 100 ; filtrer sur rank = 1 conserve donc les deux. ROW_NUMBER attribue un numéro différent à chaque ligne ; il faut un critère de tri secondaire déterministe pour choisir exactement une ligne. Le bon choix dépend du contrat du rapport.

### Exercice 3 — CTE matérialisée

**Énoncé.** Une CTE améliore la lisibilité mais une requête devient lente lorsque le jeu de données grandit. Faut-il toujours forcer sa matérialisation ?

**Correction.** Non. Il faut examiner le plan du moteur, l’intégration de la CTE, le volume intermédiaire et la répétition du calcul. Une matérialisation peut réduire les recalculs mais aussi créer un grand ensemble temporaire ou empêcher des optimisations globales. Mesurez les deux variantes dans un environnement représentatif.

### Exercice 4 — Sous-requête avec NOT IN

**Énoncé.** Une requête avec NOT IN ne renvoie aucune ligne lorsqu’un résultat était attendu. La sous-requête peut-elle être responsable ?

**Correction.** Oui, si l’ensemble produit par la sous-requête contient NULL. La logique SQL à trois valeurs peut rendre la condition inconnue. Vérifiez les colonnes et la possibilité de NULL ; NOT EXISTS avec une relation corrélée peut mieux exprimer l’intention. Ajoutez un test qui reproduit ce cas.

### Exercice 5 — SQL dynamique

**Énoncé.** Une routine construit une requête en concaténant un filtre transmis par le client.

**Correction.** Séparez la structure SQL des valeurs. Utilisez des paramètres pour les valeurs et une liste blanche pour les noms d’objets qui ne peuvent pas être paramétrés. Vérifiez les droits de la routine et ajoutez un test négatif avec une entrée hostile. Ne vous contentez pas de supprimer quelques caractères spéciaux.

### Exercice 6 — Résultat non déterministe

**Énoncé.** Deux exécutions du rapport ne renvoient pas la même « première commande » pour certains clients.

**Correction.** La requête utilise probablement un ordre incomplet, par exemple ORDER BY order_date lorsque plusieurs commandes ont la même date. Ajoutez une clé secondaire unique pour rendre le résultat stable. Si la règle demande une égalité, utilisez plutôt une fonction de classement qui conserve les égalités selon le contrat voulu.

## 11. Défi final corrigé : établir un rapport commercial fiable

### Énoncé

Le métier demande un tableau avec une ligne par client actif, son nombre de commandes terminées, son montant total, sa commande la plus élevée, la date de cette commande et le cumul de ses commandes dans l’ordre chronologique. Le système doit conserver les clients sans commande terminée.

### Correction proposée

Définissez d’abord les résultats intermédiaires : commandes admissibles, agrégation par client, classement des commandes et cumul chronologique. La liste initiale de clients doit rester la relation de départ pour ne pas éliminer les clients sans commande. Les jointures vers les agrégats doivent être externes lorsque l’absence de commandes est valide.

~~~sql
WITH completed AS (
  SELECT order_id, customer_id, order_date, total_amount
  FROM orders
  WHERE status = 'completed'
),
customer_totals AS (
  SELECT customer_id,
         COUNT(*) AS order_count,
         SUM(total_amount) AS total_spend
  FROM completed
  GROUP BY customer_id
),
ranked AS (
  SELECT order_id, customer_id, order_date, total_amount,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY total_amount DESC, order_date DESC, order_id DESC
         ) AS amount_rank,
         SUM(total_amount) OVER (
           PARTITION BY customer_id
           ORDER BY order_date, order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) AS running_total
  FROM completed
)
SELECT c.customer_id, c.customer_name,
       COALESCE(t.order_count, 0) AS order_count,
       COALESCE(t.total_spend, 0) AS total_spend,
       r.order_id AS largest_order_id,
       r.order_date AS largest_order_date,
       r.total_amount AS largest_order_amount
FROM customers AS c
LEFT JOIN customer_totals AS t
  ON t.customer_id = c.customer_id
LEFT JOIN ranked AS r
  ON r.customer_id = c.customer_id
 AND r.amount_rank = 1;
~~~

La version finale n’affiche pas le cumul par commande car le résultat exige une ligne par client. Le cumul est un résultat à granularité commande ; il doit être livré dans un rapport distinct ou agrégé selon une règle métier explicite. C’est une leçon importante : demander des indicateurs à des niveaux de détail différents dans un seul tableau peut rendre la sortie ambiguë. Le DBA doit faire clarifier le contrat au lieu d’inventer un résultat.

### Vérifications finales

- Le nombre de lignes correspond au nombre de clients admissibles.
- Les clients sans commande terminée restent présents.
- Le nombre et le total sont calculés avant les jointures qui multiplient les lignes.
- Les égalités de montant sont départagées de manière stable.
- Les états de commande inclus sont explicitement définis.
- Le SQL a des paramètres adaptés et des privilèges limités.
- Le plan d’exécution est mesuré sur un volume représentatif.
- Les résultats sont comparés à un petit calcul de référence.

## 12. Revue, mesure et dossier de preuve

Une requête complexe ne doit pas être acceptée uniquement parce qu’elle renvoie le résultat attendu sur un exemple. Lors d’une revue technique, le lecteur doit pouvoir reconstruire la règle métier, comprendre les étapes intermédiaires et identifier les cas qui n’ont pas été testés. Préparez un dossier de preuve proportionné au risque : requête versionnée, jeux d’essai, nombre de lignes attendu, résultat observé, plan d’exécution, version du moteur et limites connues.

Pour chaque modification, conservez l’ancienne version ou une référence Git, l’hypothèse de départ, la mesure de référence et la raison du changement. Un gain de performance mesuré sur un jeu de dix lignes ne prouve rien pour une table de dix millions de lignes. Inversement, un test de performance volumineux ne prouve pas que le traitement des valeurs NULL est correct. Les tests fonctionnels et les mesures de performance répondent à des questions différentes.

Une revue de qualité peut suivre cette séquence :
1. Vérifier le contrat de sortie et la granularité.
2. Confirmer que les filtres sont appliqués au bon endroit.
3. Examiner le traitement des doublons et des valeurs inconnues.
4. Vérifier l’ordre et le départage des égalités.
5. Analyser les droits, les paramètres et le risque d’injection.
6. Comparer les plans et les mesures sur des volumes connus.
7. Décider des conditions de déploiement et du retour arrière.

Ce dossier facilite aussi le transfert de compétences. Un autre développeur peut modifier la requête sans repartir de zéro et un DBA peut distinguer une régression SQL d’un changement de données ou de configuration. Les preuves doivent rester accessibles sans exposer d’identifiants ou de données personnelles.

## Fiche de vérification

Avant de livrer une requête complexe, confirmez :
- la granularité de chaque étape ;
- les conditions de nullité et d’absence de correspondance ;
- la sémantique des égalités et de l’ordre ;
- le coût des jointures, tris et calculs répétés ;
- la compatibilité de la syntaxe avec le moteur et sa version ;
- la sécurité des paramètres et des routines ;
- la reproductibilité des tests et la conservation des résultats attendus.

## Glossaire

**Sous-requête corrélée** : requête interne qui référence une valeur de la requête externe.

**CTE** : expression de table commune définie avec WITH pour nommer une relation logique intermédiaire.

**Fonction de fenêtre** : fonction qui calcule un résultat sur un ensemble de lignes liées sans les regrouper en une seule ligne.

**Cardinalité** : nombre de lignes d’un ensemble ou de résultats attendus d’une relation.

**Sémantique NULL** : règles SQL permettant de représenter une valeur inconnue ou absente, avec une logique qui ne se réduit pas à vrai ou faux.

**Idempotence** : propriété permettant de répéter une opération sans produire un effet additionnel non désiré.

**Plan d’exécution** : stratégie choisie par le moteur pour exécuter une requête.

**SARGable** : condition de recherche formulée de façon à permettre au moteur d’utiliser efficacement un index dans les cas où l’index est pertinent.
