# Sous-requêtes, CTE, Procédures stockées — Intermédiaire

> **Mise en contexte.** SQL ne sert pas uniquement à sélectionner des colonnes. Des analyses fiables demandent parfois des sous-requêtes, des expressions de table communes (CTE), des fonctions de fenêtre ou une logique transactionnelle réutilisable. Une requête lisible aide à contrôler le sens du résultat ; une procédure stockée peut encapsuler une opération côté serveur, mais elle ajoute des responsabilités de versionnement, de droits, de tests et de portabilité. Ce cours approfondit les constructions SQL, les compare avec des alternatives et montre comment conserver l’exactitude tout en tenant compte du coût d’exécution. Les exemples sont illustratifs et ciblent une syntaxe proche du SQL standard avec des éléments PostgreSQL identifiés comme tels ; vérifiez toujours le dialecte du moteur utilisé.

## Objectifs pédagogiques

À la fin du cours, vous pourrez choisir entre jointure et sous-requête, construire une CTE lisible, utiliser une fonction de fenêtre pour comparer ou classer des lignes, écrire une CTE récursive simple, utiliser une transaction pour protéger une opération métier, concevoir une procédure lorsque le moteur le justifie, et tester les erreurs, les valeurs NULL, les doublons et les volumes réels.

Vous devrez être capable d’expliquer le résultat, pas uniquement de produire une requête qui semble fonctionner. Toute réécriture doit préserver sémantique, cardinalité, ordre nécessaire et comportement dans les cas limites. Le plan d’exécution et les mesures restent importants : une construction plus élégante n’est pas nécessairement plus rapide.

## Prérequis et environnement

Vous devez connaître SELECT, WHERE, JOIN, GROUP BY, HAVING, INSERT, UPDATE, DELETE, clés primaires et étrangères, transactions et NULL. Préparez une base de laboratoire et un jeu synthétique qui inclut doublons, clients sans commandes, commandes répétées, montants nuls lorsque cela représente un cas métier valide et plusieurs dates identiques. Ce sont ces cas qui révèlent les différences entre une requête superficiellement correcte et une requête robuste.

Les fonctionnalités de CTE, de fonctions de fenêtre, de procédures, de paramètres, de gestion d’erreurs et de transactions varient selon le moteur et sa version. Les fragments marqués PostgreSQL ne doivent pas être copiés tels quels vers MySQL, SQL Server, Oracle ou SQLite. Notez la version de votre environnement et lisez la documentation correspondante avant d’utiliser des fonctions de production.

## 1. Pourquoi utiliser une sous-requête ?

Une sous-requête est une requête imbriquée dans une autre. Elle peut produire une valeur scalaire, une liste de valeurs, une table dérivée ou un test d’existence. Elle permet souvent d’exprimer une règle métier directement : « trouver les commandes dont le montant dépasse la moyenne » ou « sélectionner les clients qui ont au moins une commande ». Mais ses résultats dépendent du contexte et la distinction entre une sous-requête corrélée et une sous-requête indépendante est importante.

Une sous-requête indépendante ne dépend pas des valeurs de la ligne externe. Le moteur peut parfois la calculer une seule fois, la réécrire ou la transformer en une jointure. Une sous-requête corrélée référence une colonne de la requête externe ; conceptuellement, elle évalue un résultat pour chaque ligne candidate, même si l’optimiseur peut transformer l’expression. N’assumez pas qu’elle se répète physiquement dans tous les moteurs ; inspectez le plan lorsque la performance est importante.

```sql
-- Clients qui ont au moins une commande.
SELECT c.customer_id, c.display_name
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);
```

EXISTS indique que l’intérêt porte sur l’existence d’une ligne, pas sur ses colonnes. Il évite de devoir retirer des doublons produits par une jointure, lorsqu’il s’agit seulement de répondre « oui ou non ». Un index sur la colonne de relation peut aider, mais le plan dépend des données, du moteur et de la sélectivité.

### Sous-requête scalaire

Une sous-requête scalaire doit produire au plus une valeur dans le contexte qui l’utilise. Si elle renvoie plusieurs lignes, certains moteurs renvoient une erreur ; un résultat vide peut donner NULL. Il faut traiter ces conditions explicitement. Une requête qui semble correcte sur un jeu de test où il n’existe qu’une seule ligne peut échouer dès qu’une deuxième correspondance apparaît.

```sql
SELECT
    p.product_id,
    p.name,
    (SELECT MAX(o.created_at)
     FROM orders AS o
     WHERE o.product_id = p.product_id) AS last_order_at
FROM products AS p;
```

La requête exprime une valeur dérivée par produit. Pour un très grand catalogue, une agrégation puis une jointure peut parfois être plus adaptée. Comparez le plan et le nombre de lignes, et souvenez-vous que l’agrégation et la jointure doivent respecter la même sémantique si l’on compare les résultats.

## 2. IN, EXISTS, ANY et les valeurs NULL

IN compare une valeur à un ensemble. EXISTS teste si au moins une ligne existe. Les deux peuvent se ressembler mais diffèrent dans le traitement des valeurs NULL et dans certains contextes logiques. NOT IN est particulièrement piégeux : si l’ensemble contient NULL, le test peut devenir inconnu et filtrer des lignes auxquelles on s’attendait. Cette logique à trois valeurs peut surprendre même un développeur expérimenté.

```sql
-- Les clients sans commande : formulation avec NOT EXISTS.
SELECT c.customer_id
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);
```

Cette formulation exprime la non-existence d’une commande associée. Elle est généralement plus robuste que NOT IN si l’ensemble des identifiants peut contenir NULL. Néanmoins, elle exige des clés et index corrects et doit être validée dans le moteur cible. Si la colonne de relation peut être NULL, définissez le sens métier de cette absence et vérifiez l’équivalence attendue.

Un test fiable couvre : ensemble vide, ensemble contenant une valeur, ensemble contenant NULL, ligne externe avec valeur NULL et plusieurs lignes associées. Ne vous contentez pas du cas nominal. Les règles SQL, pas les suppositions de l’application, déterminent la valeur vraie, fausse ou inconnue.

## 3. CTE : organiser une requête en étapes

Une expression de table commune (CTE) est déclarée avec WITH. Elle donne un nom à un résultat intermédiaire et améliore la lisibilité. Une CTE n’est pas automatiquement une table temporaire ni une garantie de calcul unique. Selon le moteur et la version, elle peut être intégrée au plan, matérialisée ou traitée avec des règles spécifiques. Ne l’utilisez pas en supposant qu’elle accélère toute requête.

```sql
WITH customer_totals AS (
    SELECT customer_id, SUM(total) AS lifetime_total
    FROM orders
    GROUP BY customer_id
),
eligible_customers AS (
    SELECT customer_id, lifetime_total
    FROM customer_totals
    WHERE lifetime_total >= 100000
)
SELECT c.customer_id, c.display_name, e.lifetime_total
FROM eligible_customers AS e
JOIN customers AS c ON c.customer_id = e.customer_id
ORDER BY e.lifetime_total DESC;
```

Ce découpage sépare calcul d’agrégat, filtre et enrichissement descriptif. Il évite de répéter une expression complexe et fournit un point de lecture pour chaque étape. Une CTE doit cependant être nommée précisément et ne doit pas cacher une logique métier dont personne ne comprend le contrat. Les noms vagues comme `tmp`, `data` ou `result` ne rendent pas une requête plus maintenable.

Une CTE peut être utile pour définir un ensemble de lignes puis le réutiliser, mais la manière dont le moteur exécute cette structure doit être vérifiée. Si la même CTE est référencée plusieurs fois, le moteur peut choisir un plan différent selon la version. Lorsque la performance est critique, comparez le plan avant et après réécriture et mesurez sur des paramètres représentatifs.

## 4. CTE récursives : parcourir une hiérarchie

Une CTE récursive décrit un résultat initial, puis une étape qui s’applique aux résultats précédents jusqu’à ce qu’il n’y ait plus de nouvelles lignes. Elle est utile pour une hiérarchie de catégories, une structure organisationnelle ou un graphe simple. Elle doit gérer les cycles et la profondeur ; sans contrôle, un graphe cyclique peut provoquer une récursion qui ne termine pas ou produire des résultats volumineux.

```sql
WITH RECURSIVE category_tree AS (
    SELECT category_id, parent_id, name, 0 AS depth
    FROM categories
    WHERE category_id = ?

    UNION ALL

    SELECT child.category_id, child.parent_id, child.name, parent.depth + 1
    FROM categories AS child
    JOIN category_tree AS parent
      ON child.parent_id = parent.category_id
    WHERE parent.depth < 20
)
SELECT category_id, parent_id, name, depth
FROM category_tree
ORDER BY depth, category_id;
```

Cet exemple limite la profondeur, mais cela ne détecte pas automatiquement tout cycle. Pour des graphes susceptibles de contenir des cycles, gardez un chemin de visite, un ensemble de nœuds vus ou une protection spécifique au moteur. Utilisez UNION au lieu de UNION ALL seulement si la déduplication correspond à la sémantique et si son coût est acceptable. UNION ALL est souvent moins coûteux mais peut conserver des doublons ou des cycles.

Une récursion doit définir sa population initiale, la relation de progression, la condition d’arrêt, la profondeur maximale et le comportement pour un nœud inconnu. Testez un nœud sans enfant, une hiérarchie longue, une référence inexistante et un cycle si le modèle l’autorise.

## 5. Fonctions de fenêtre : calculer sur un ensemble sans supprimer les lignes

Une fonction de fenêtre calcule une valeur sur un ensemble de lignes liées à la ligne courante sans réduire le résultat à une ligne par groupe. OVER définit la fenêtre ; PARTITION BY sépare les groupes ; ORDER BY ordonne les lignes dans la fenêtre. Les fonctions courantes comprennent ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD et des agrégats exécutés en mode fenêtre.

```sql
SELECT
    customer_id,
    order_id,
    created_at,
    total,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY created_at DESC, order_id DESC
    ) AS position
FROM orders;
```

Cette requête attribue une position à chaque commande au sein du client. L’identifiant de commande sert de départage pour rendre l’ordre déterministe. Sans une clé de départage unique, plusieurs lignes peuvent partager une position ambiguë pour des dates identiques. ROW_NUMBER, RANK et DENSE_RANK ont des règles différentes pour les égalités : choisissez selon la question métier.

### Comparer avec la ligne précédente

```sql
SELECT
    account_id,
    event_time,
    balance,
    LAG(balance) OVER (
        PARTITION BY account_id
        ORDER BY event_time, event_id
    ) AS prior_balance
FROM balance_events;
```

LAG permet de calculer une différence ou de détecter une anomalie entre deux événements successifs. La première ligne de chaque partition n’a pas de ligne précédente et renvoie normalement NULL, sauf valeur par défaut prévue par la fonction. Une valeur NULL peut signifier « pas de précédent » ou une donnée inconnue ; ne confondez pas ces situations.

Les fonctions de fenêtre sont souvent plus lisibles qu’une auto-jointure répétée. Elles peuvent cependant exiger tri et mémoire. Regardez le plan, les index possibles et le volume de chaque partition.

## 6. Agrégation et fenêtrage ne sont pas équivalents

GROUP BY réduit les lignes : une sortie par groupe selon les expressions choisies. Les fonctions de fenêtre laissent les lignes individuelles tout en calculant un résumé pour leur partition. Si l’écran doit afficher chaque commande avec le total cumulé du client, une fonction de fenêtre convient mieux que l’agrégation seule. Si l’on veut uniquement le total par client, GROUP BY est plus direct.

```sql
SELECT
    customer_id,
    created_at,
    order_id,
    total,
    SUM(total) OVER (
        PARTITION BY customer_id
        ORDER BY created_at, order_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM orders;
```

Le cadre de fenêtre explicite définit ici un cumul depuis le début de la partition jusqu’à la ligne courante. Les valeurs égales d’ORDER BY et le cadre par défaut peuvent changer le résultat entre constructions ou moteurs. Définissez le cadre, la clé de tri et le comportement des NULL explicitement lorsque le calcul est critique.

## 7. Transactions : rendre une suite d’opérations cohérente

Une transaction regroupe des modifications qui doivent être validées ou annulées ensemble. BEGIN, COMMIT et ROLLBACK sont familiers dans de nombreux moteurs, mais l’autocommit et la syntaxe peuvent varier. Une transaction longue conserve parfois des verrous et ressources ; elle doit donc être aussi courte que possible tout en couvrant la règle métier.

```sql
BEGIN;

UPDATE inventory
SET available = available - 1
WHERE sku = ?
  AND available > 0;

-- L'application doit vérifier le nombre de lignes modifiées.
-- Si aucune ligne n'est modifiée, la réservation ne doit pas être confirmée.

INSERT INTO order_line (order_id, sku, quantity)
VALUES (?, ?, 1);

COMMIT;
```

Le fragment est un schéma pédagogique, pas un code prêt à copier. Pour une application réelle, les erreurs doivent déclencher un rollback, le résultat de l’UPDATE doit être vérifié et l’INSERT doit échouer proprement si une contrainte est violée. Vérifiez la quantité conditionnelle, l’isolation, l’ordre des opérations et la possibilité de rejeu. Une application ne doit pas faire COMMIT lorsque la réservation de stock n’a pas réussi.

Les erreurs de concurrence peuvent exiger une nouvelle tentative transactionnelle. Une reprise doit être bornée et la transaction doit pouvoir être rejouée sans dupliquer un paiement ou une commande. Utilisez une clé d’idempotence métier lorsque l’opération peut être répétée par un client après un timeout. Le timeout ne prouve pas que la transaction n’a pas été validée ; il peut seulement signifier que la réponse s’est perdue.

## 8. Procédures stockées et fonctions côté serveur

Une procédure stockée encapsule une suite d’instructions côté serveur. Elle peut rapprocher traitement et données, réduire les allers-retours réseau et centraliser un contrat de mise à jour. Une fonction peut également produire une valeur ou un ensemble selon le moteur. Les langages, possibilités de transaction, règles d’erreur, droits d’exécution et outils de déploiement diffèrent ; vérifiez le système cible.

Les avantages ne sont pas automatiques. Une logique stockée peut rendre le code plus difficile à versionner, tester localement ou déplacer entre moteurs. Elle peut masquer des requêtes lourdes et créer une frontière de sécurité insuffisante si les droits du propriétaire ou de l’appelant ne sont pas compris. Gardez une séparation claire entre logique métier, requêtes et orchestration selon les besoins de l’application.

Exemple conceptuel PostgreSQL :

```sql
CREATE OR REPLACE FUNCTION demo_total_for_customer(p_customer_id INTEGER)
RETURNS NUMERIC
LANGUAGE SQL
AS $$
    SELECT COALESCE(SUM(total), 0)
    FROM orders
    WHERE customer_id = p_customer_id;
$$;
```

La fonction retourne une valeur agrégée pour le client. COALESCE convertit l’absence de commandes en zéro : ce choix n’est correct que si le contrat métier considère « aucune commande » comme un total nul. Si l’absence signifie « inconnue », cette conversion inventerait une information. L’exemple illustre pourquoi il faut écrire la règle métier avant la requête.

Lorsqu’une logique côté serveur est requise, versionnez sa définition, automatisez son déploiement et testez la compatibilité avec les versions précédentes. Définissez les droits d’exécution, la stratégie de migration et la façon d’observer les erreurs. Le nom et le contrat de la procédure devraient être plus stables que ses détails internes.

## 9. Paramètres et sécurité des requêtes

Les valeurs fournies par un utilisateur ne doivent pas être concaténées dans la chaîne SQL. Les requêtes paramétrées séparent le code des données et sont une protection majeure contre l’injection SQL. Les paramètres ne peuvent toutefois pas toujours représenter un nom de table, de colonne ou un mot-clé de tri : pour ces parties dynamiques, utilisez une liste blanche de valeurs validées et contrôlez l’autorisation.

```python
# Exemple Python conceptuel avec un pilote DB-API :
cursor.execute(
    "SELECT order_id, total FROM orders WHERE customer_id = %s",
    (customer_id,),
)
```

Le marqueur varie selon le pilote ; vérifiez la documentation de l’API utilisée. Le principe est de fournir les données séparément, sans fabriquer la requête par concaténation. Les paramètres protègent aussi les valeurs contenant apostrophes ou caractères spéciaux.

Ne divulguez pas les erreurs SQL brutes à un utilisateur final si elles révèlent noms de tables, versions, données ou requêtes internes. Journalisez suffisamment d’informations techniques pour le diagnostic, mais masquez les secrets et données sensibles. Les paramètres préparés ne remplacent ni les droits minimaux, ni la validation métier, ni les protections contre une requête coûteuse volontaire.

## 10. Gestion des erreurs et idempotence

Une opération peut échouer avant de démarrer, pendant l’exécution ou après que le serveur a validé la transaction mais avant que le client ne reçoive la réponse. Cette dernière situation est source de doublons : le client réessaie en pensant que la demande a échoué, alors que la première écriture est déjà validée.

Pour les opérations non idempotentes, définissez une clé ou un identifiant de requête unique et une contrainte qui empêche un double traitement. Le serveur doit stocker ou retrouver le résultat correspondant et renvoyer une réponse cohérente lors d’une répétition. Ne supposez pas qu’un timeout annule automatiquement la transaction. La stratégie doit être adaptée au moteur, à l’application et au flux métier.

La logique d’erreur doit distinguer violation de contrainte, absence de ligne, conflit concurrent, timeout, perte de connexion et erreur inattendue. Les reprises automatiques sont adaptées à certains conflits transitoires, mais pas à une erreur de syntaxe ou à une donnée invalide. Les tentatives doivent avoir une limite, un délai et un journal de décision.

## 11. Lisibilité et maintenance des requêtes

Une requête est un artefact logiciel. Elle doit être lisible, testée et versionnée comme du code : nommer les CTE par leur rôle, qualifier les colonnes ambiguës, expliciter les clés de tri, réduire les conversions implicites et éviter les conditions métier dupliquées. Les commentaires expliquent une règle non évidente, pas chaque mot-clé SQL.

Ne confondez pas lisibilité et multiplication des niveaux. Une CTE pour chaque expression simple peut rendre la requête plus difficile à suivre. À l’inverse, une requête monolithique avec de nombreuses sous-requêtes imbriquées et noms d’alias opaques augmente le risque d’erreur. Choisissez une structure qui rend visibles les étapes et les invariants.

La revue doit poser plusieurs questions : le résultat est-il exact en présence de doublons ? Quelle est la sémantique des NULL ? La requête est-elle stable sans ordre explicite ? Le nombre de lignes peut-il exploser ? Les paramètres sont-ils protégés ? L’opération est-elle transactionnelle ? Les index et le plan correspondent-ils au volume réel ? Les permissions sont-elles suffisantes mais non excessives ?

## 12. Atelier pratique guidé : analyser l’activité des clients

### Scénario

Un commerce souhaite afficher pour chaque client le nombre de commandes, la date de la commande la plus récente et le classement des commandes par montant. Vous devez produire une requête lisible, puis comparer sous-requête, CTE, agrégation et fonction de fenêtre.

### Étape A — Préparer les données

Créez les tables customers et orders et insérez un client sans commande, un client avec une commande, un client avec plusieurs commandes et deux commandes du même montant. Ajoutez aussi deux commandes avec le même horodatage. Ce jeu révèle la différence entre COUNT, COUNT(colonne), LEFT JOIN et INNER JOIN, ainsi que la nécessité d’un départage stable.

### Étape B — Calculer les totaux par client

```sql
WITH totals AS (
    SELECT customer_id,
           COUNT(*) AS order_count,
           SUM(total) AS total_spend,
           MAX(created_at) AS latest_order_at
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_id,
       c.display_name,
       COALESCE(t.order_count, 0) AS order_count,
       t.total_spend,
       t.latest_order_at
FROM customers AS c
LEFT JOIN totals AS t
  ON t.customer_id = c.customer_id
ORDER BY c.customer_id;
```

Le LEFT JOIN conserve les clients sans commande. Le COUNT est calculé dans la CTE afin de ne pas compter artificiellement une ligne de gauche introduite par la jointure. Le comportement de SUM pour une population vide reste NULL dans plusieurs moteurs ; le convertir en zéro dépend de la règle métier. Dans un rapport financier, « aucun mouvement » et « total inconnu » ne sont pas toujours équivalents.

### Étape C — Classer les commandes

```sql
SELECT customer_id, order_id, total,
       ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY total DESC, order_id
       ) AS position_by_total
FROM orders;
```

Le départage par identifiant rend la position déterministe pour les montants égaux. Si le métier veut que des montants identiques partagent le même rang, utilisez RANK ou DENSE_RANK en comprenant la différence. Vérifiez la sortie avec deux montants égaux et une commande sans montant seulement si ce cas est autorisé.

### Étape D — Encapsuler une mise à jour métier

Créez une transaction qui vérifie une réservation, met à jour le stock et écrit une ligne de commande. Ajoutez un test où le stock est épuisé et un test où une contrainte d’écriture échoue. Vérifiez qu’aucune réservation partielle ne reste. Si le moteur permet une procédure stockée, créez une version de laboratoire qui suit la même règle et comparez les droits nécessaires.

### Étape E — Comparer les plans

Mesurez la requête sur plusieurs tailles de jeu. Comparez le résultat et le plan, pas uniquement la syntaxe. Une CTE ne garantit pas une optimisation automatique ; le moteur peut avoir choisi le même plan après réécriture. Documentez les mesures, leur variance et les cas limites.

### Critères d’acceptation

Le résultat inclut tous les clients, y compris sans commande ; les totaux et rangs sont corrects ; l’ordre est stable ; une panne ou un échec de contrainte n’entraîne pas de modification partielle ; et les paramètres utilisateurs sont séparés du SQL. Le compte-rendu documente moteur, version, requêtes, tests et risques.

## 13. Étude de cas : les commandes doublent après un timeout

### Situation

Un client clique sur « payer ». L’application envoie la commande au serveur ; une latence réseau empêche la réponse d’arriver à temps. Le client répète la demande et deux commandes sont créées.

### Causes possibles

Le système peut ne pas avoir d’identifiant de requête idempotent, la contrainte métier peut manquer, l’application peut traiter la commande sans transaction ou le timeout peut masquer un commit déjà réussi. Un verrou seul ne garantit pas une opération unique après la disparition du client. Il faut comprendre où le commit intervient et comment la répétition est détectée.

### Correction

Utilisez un identifiant unique de demande ou une clé d’idempotence, stockez le résultat et imposez une contrainte appropriée. Lorsqu’une demande identique revient, renvoyez le résultat déjà associé au lieu d’effectuer un second paiement. La transaction doit contenir les changements locaux qui doivent rester cohérents. Les interactions avec un fournisseur externe peuvent demander un état intermédiaire et une réconciliation ; une transaction SQL ne rend pas atomique un système extérieur.

### Prévention et preuve

Ajoutez un test qui envoie deux demandes identiques et vérifie une seule commande métier. Testez aussi un timeout après validation et une répétition après redémarrage du processus. Mesurez le nombre de tentatives, les doublons empêchés et les erreurs. La correction n’est complète que si elle résiste aux scénarios concurrents et après reprise.

## 14. Exercices avec corrigés

### Exercice 1 — Pourquoi NOT IN peut-il surprendre quand la sous-requête renvoie NULL ?

**Correction.** La logique SQL inclut UNKNOWN. Si l’ensemble contient NULL, la comparaison peut devenir inconnue plutôt que vraie ou fausse et une condition WHERE ne conserve pas cette ligne. NOT EXISTS décrit souvent plus clairement l’absence, mais il faut vérifier les clés et la sémantique des NULL.

### Exercice 2 — Pourquoi une CTE n’est-elle pas automatiquement plus rapide ?

**Correction.** Une CTE est une structure de requête et un outil de lisibilité. Selon le moteur et la version, elle peut être intégrée au plan ou matérialisée. La performance dépend de l’optimiseur, des statistiques, des index, du volume et du nombre de références. Comparez les plans et les temps réels.

### Exercice 3 — Quelle différence entre RANK et ROW_NUMBER ?

**Correction.** ROW_NUMBER attribue une position unique selon l’ordre défini. RANK partage le rang entre valeurs à égalité puis laisse un saut dans les rangs suivants ; DENSE_RANK partage le rang sans saut. Le choix dépend du sens du classement. Ajoutez un départage si un ordre unique est exigé.

### Exercice 4 — Une transaction a expiré côté client. Peut-on conclure qu’elle a été annulée ?

**Correction.** Non. Le serveur peut avoir validé la transaction avant que la réponse soit perdue. Il faut utiliser un identifiant idempotent ou rechercher le résultat avec une clé métier fiable avant de réessayer. La stratégie doit tenir compte du moteur et de l’application.

### Exercice 5 — Quand une procédure stockée peut-elle être pertinente ?

**Correction.** Elle peut encapsuler une opération critique, réduire les allers-retours et concentrer les permissions côté serveur. Mais son langage, ses droits, son déploiement et sa portabilité ajoutent de la complexité. Elle doit être versionnée, testée, observée et justifiée par le besoin.

### Exercice 6 — Pourquoi un LEFT JOIN est-il nécessaire pour afficher les clients sans commande ?

**Correction.** INNER JOIN élimine les clients sans correspondance. LEFT JOIN conserve les lignes de la table de gauche et remplit les colonnes manquantes du côté droit par NULL. Les agrégats et COUNT doivent être construits de manière à ne pas compter artificiellement la ligne conservée.

## 15. Défi final : produire un rapport SQL fiable

Vous devez produire un rapport client qui affiche les clients, leur total d’achats, leur dernière commande et leur rang parmi les clients selon le total. Le rapport doit préserver les clients sans commande et rester correct en présence de montants identiques et d’horodatages identiques.

### Corrigé attendu

Commencez par définir le sens du total d’un client sans commande. Si zéro est bien la valeur prévue, convertissez explicitement le NULL issu de l’absence de groupe ; sinon conservez la distinction entre absence et inconnu. Agrégez les commandes par client dans une CTE, joignez ce résultat à la population des clients avec LEFT JOIN, puis appliquez une fonction de fenêtre sur l’ensemble agrégé pour créer le classement. Définissez si l’égalité des totaux doit partager un rang et ajoutez un identifiant en départage lorsque l’ordre de sortie doit être stable.

Vérifiez que les commandes associées à un client inconnu sont interdites ou gérées selon les règles du schéma. Préparez des tests avec client sans commande, total nul, plusieurs commandes, valeurs égales et données manquantes. Contrôlez le plan, les index et les mesures sur des volumes réels. N’optimisez pas seulement à partir d’un jeu de dix lignes.

Pour l’opération de paiement distincte, utilisez une transaction et une stratégie d’idempotence. Le rapport de classement n’a pas besoin de verrouiller les commandes en écriture ; ne mélangez pas une requête de reporting avec une transaction de modification de longue durée. Attribuez les responsabilités et documentez les attentes de fraîcheur.

La remise finale contient requêtes, résultats attendus, tests négatifs, plan d’exécution, moteur/version et limites. Une requête correcte est un contrat reproductible : un autre développeur doit pouvoir comprendre les règles et vérifier les cas limites sans se fier à l’auteur.

## 16. Checklist avant publication d’une requête

- [ ] Le résultat attendu est décrit en termes métier.
- [ ] Les valeurs NULL et les ensembles vides ont un comportement défini.
- [ ] Les doublons et les cardinalités des jointures sont contrôlés.
- [ ] Les ordres et classements sont déterministes quand nécessaire.
- [ ] Les paramètres utilisateurs sont liés, pas concaténés.
- [ ] Les opérations multi-étapes sont transactionnelles au bon périmètre.
- [ ] Les reprises sont bornées et l’idempotence est définie.
- [ ] Le dialecte et la version du moteur sont documentés.
- [ ] Les plans et mesures utilisent un jeu représentatif.
- [ ] Les droits d’exécution sont minimaux.
- [ ] Les erreurs fournissent une information utile sans divulguer de secret.
- [ ] Les tests de non-régression couvrent les cas limites.

## Conclusion

Les sous-requêtes, CTE, fonctions de fenêtre et procédures étendent l’expression de SQL, mais imposent une responsabilité supplémentaire de compréhension et de vérification. Une requête doit préserver la sémantique avec doublons, NULL et données concurrentes. Une transaction doit protéger une règle métier, et une reprise doit tenir compte du fait qu’un timeout n’annule pas nécessairement une écriture. La meilleure construction est celle dont le contrat est clair, les résultats prouvés, le plan compris et l’exploitation documentée.


## Complément avancé : revue de cas limites et déploiement progressif

### Vérifier l’équivalence entre deux formulations

Une réécriture SQL doit être testée sur des cas qui distinguent les sémantiques. Par exemple, remplacer une sous-requête par une jointure peut multiplier des lignes si plusieurs correspondances existent ; ajouter DISTINCT peut ensuite masquer l’erreur et ajouter un tri ou une déduplication coûteuse. Comparer seulement le nombre total de lignes n’est pas suffisant : comparez les clés et les valeurs avec une méthode qui détecte une ligne manquante, une ligne supplémentaire et une valeur différente. Conservez un jeu réduit qui a déjà provoqué une divergence.

Pour un filtre anti-jointure, comparez NOT EXISTS, LEFT JOIN avec test IS NULL et les contraintes réelles. Ces formes peuvent être équivalentes sous certaines conditions, mais une expression de test sur une colonne nullable du côté droit peut confondre « aucune ligne » et « ligne présente avec valeur NULL ». Appuyez le test sur une clé non nulle et documentez l’invariant.

### Comprendre l’ordre logique et l’ordre d’exécution

L’ordre logique d’une requête explique comment les clauses définissent le résultat ; il ne détermine pas nécessairement l’ordre physique d’exécution. Le moteur peut déplacer des filtres, réordonner des jointures, intégrer des CTE ou choisir un index. Il ne doit pas changer la sémantique, mais les hypothèses reposant sur un ordre de traitement implicite sont fragiles. Utilisez ORDER BY pour exiger un ordre, une transaction pour définir un périmètre cohérent et les outils d’analyse pour étudier le plan.

Une CTE récursive doit être contrôlée par un invariant de progression. Dans une hiérarchie, l’identifiant parent-enfant doit être indexé si le volume l’exige, la profondeur doit être bornée si le domaine peut contenir des erreurs et le compte-rendu doit identifier la façon dont les cycles sont détectés. Une récursion valide sur une petite structure peut devenir très coûteuse si le degré de branchement augmente.

### Procédures, rôles et migration

Une procédure stockée doit avoir une interface stable : paramètres, format de sortie, erreurs attendues et droits. Préférez des comptes séparés pour exécuter une opération sensible. Réfléchissez au modèle de sécurité du moteur : exécution avec droits de l’appelant et exécution avec droits du propriétaire ne se comportent pas identiquement. Les conventions de sécurité doivent être revues pour chaque moteur, et les procédures ne doivent pas contourner les contrôles de l’application sans justification.

Le changement de procédure fait partie d’un déploiement. Une nouvelle version de l’application peut appeler la nouvelle signature alors qu’une ancienne instance demeure active. Il peut être nécessaire d’ajouter une nouvelle procédure, de déployer les consommateurs, de vérifier l’usage, puis de retirer l’ancienne signature. Documentez les points de compatibilité, les dépendances et le retour arrière. Une migration de définition n’est pas forcément réversible si elle modifie les données.

### Évaluer la charge et le risque

Un rapport d’analyse peut avoir un coût élevé pendant les heures de pointe. Planifiez les tests, définissez un timeout, limitez la quantité de données et surveillez mémoire et espace temporaire. Une fonction de fenêtre sur une vaste population peut nécessiter un tri important ; une CTE récursive peut exploser le nombre de lignes ; une procédure peut tenir une transaction ouverte plus longtemps que prévu. Les mécanismes côté serveur peuvent économiser des allers-retours, mais ils ne font pas disparaître les coûts d’algorithme.

Pour conclure, distinguez quatre preuves : le résultat est exact, le plan correspond à une hypothèse comprise, la durée atteint la cible sur une charge représentative, et les droits respectent le périmètre attendu. Si l’une de ces preuves manque, notez le risque restant plutôt que de déclarer la requête « optimisée » par intuition.