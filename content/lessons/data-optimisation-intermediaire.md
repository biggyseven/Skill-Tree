# Indexation et plans d’exécution — Intermédiaire

> **Mise en contexte.** Une requête SQL lente n’est pas automatiquement une requête qui manque d’index. Elle peut lire trop de lignes, utiliser des statistiques dépassées, transférer trop de données, effectuer un tri coûteux, attendre un verrou ou répéter la même opération. L’optimisation efficace commence par une mesure reproductible, puis relie le résultat observé au plan d’exécution, à la distribution des données et au contrat de la requête. Ajouter un index sans comprendre le goulot d’étranglement peut augmenter le coût des écritures sans réduire la latence.

## Objectifs d’apprentissage

À la fin du cours, vous devrez pouvoir lire la structure d’un plan, différencier une lecture séquentielle et un accès par index, interpréter les cardinalités estimées et observées, reconnaître les tris et agrégations coûteux, proposer un index qui correspond à un motif de requête, comprendre le coût de maintenance d’un index, et comparer des variantes à l’aide de mesures réelles. Vous saurez aussi préparer une expérience de performance, éviter les faux gains issus d’un cache déjà chaud, décider quand un index est inutile et rédiger une recommandation justifiée.

Ce cours suppose que vous connaissez les tables relationnelles, les clés et les requêtes SELECT. Il ne prétend pas remplacer les manuels propres à PostgreSQL, MySQL ou à votre fournisseur. Les noms d’opérations, les statistiques, les méthodes d’indexation et les options de mesure évoluent selon le moteur et sa version. Les commandes de laboratoire doivent être vérifiées dans la documentation de l’environnement utilisé.

## Prérequis et environnement de test

Utilisez une base isolée contenant une table suffisamment volumineuse pour rendre visible la différence entre plusieurs stratégies. Quelques dizaines de lignes démontrent la syntaxe, mais ne permettent pas de tirer des conclusions solides sur la performance. Pour un exercice intermédiaire, plusieurs centaines de milliers de lignes synthétiques peuvent être utiles, à condition de garder un contrôle sur la durée et la charge.

Enregistrez la version du moteur, la définition de la table, les index existants, les statistiques, le jeu de données et la requête exacte. Conservez le même contrat fonctionnel entre les variantes. Si une réécriture retourne moins de lignes, elle n’est pas plus rapide de manière valable : elle calcule autre chose.

Utilisez des données synthétiques, sans informations personnelles. Ne lancez pas un test de charge ou un EXPLAIN ANALYZE coûteux sur la production sans autorisation, créneau et garde-fous. Une expérience doit avoir un objectif, une hypothèse, une mesure initiale, un changement unique et un critère de succès.

## 1. Coût logique et coût réel

Le moteur ne compte pas uniquement les lignes retournées. Il peut devoir lire des pages, parcourir des index, vérifier des conditions, joindre plusieurs relations, trier, agréger, matérialiser des résultats intermédiaires et transférer les lignes au client. Le temps total perçu peut également inclure le réseau et le traitement par l’application.

Une requête qui retourne cent lignes peut lire dix millions de lignes si son filtre est mal sélectif ou si aucun chemin d’accès efficace n’est disponible. À l’inverse, une requête qui retourne beaucoup de lignes peut légitimement utiliser une lecture séquentielle parce que parcourir une grande partie de la table coûte moins cher que multiplier les accès à l’index puis à la table.

La première étape consiste à comprendre le volume traité, pas seulement le nombre de résultats. Il faut aussi savoir si la latence vient du moteur, du pool de connexions ou du transfert. Mesurer le temps entre l’appel applicatif et le retour SQL, puis comparer au temps serveur lorsqu’il est disponible, aide à isoler le coût.

### 1.1 Latence, débit et variance

La latence mesure le temps pris par une opération. Le débit mesure le nombre d’opérations traitées par unité de temps. Un traitement peut augmenter son débit en exécutant plus de requêtes en parallèle tout en augmentant le temps d’attente de certaines requêtes. Il faut donc choisir la métrique en fonction de l’objectif utilisateur.

Mesurez la médiane et les percentiles pertinents, pas seulement la moyenne. Si 95 % des requêtes prennent 50 millisecondes et que 5 % prennent plusieurs secondes, la moyenne ne suffit pas à décrire l’expérience. La distribution de latence doit être associée à la fréquence, à l’impact et à la fenêtre de mesure.

### 1.2 Construire une référence

Avant toute optimisation, collectez :
- la requête exacte et ses paramètres ;
- le temps d’exécution sur plusieurs essais ;
- le nombre de lignes retournées ;
- les estimations et lignes observées ;
- les lectures logiques et physiques lorsqu’elles sont mesurables ;
- les opérations de tri, de jointure et de lecture ;
- le profil de charge et l’état du cache ;
- la version du moteur et les index disponibles.

Une mesure unique est fragile. La première exécution peut inclure des lectures physiques qui ne se répètent pas ensuite. Les écritures de données et les statistiques peuvent également varier entre deux essais. La méthode de test doit préciser si elle vise un cache froid, un cache chaud ou une situation mixte.

## 2. Lire un plan d’exécution

Le plan décrit la stratégie choisie par le moteur. Dans PostgreSQL, EXPLAIN présente le plan prévu et EXPLAIN ANALYZE exécute la requête tout en affichant des mesures. Les outils MySQL et d’autres moteurs ont leurs propres formats. Le principe est identique : identifier les opérateurs, examiner leurs entrées et sorties et vérifier si les estimations correspondent à la réalité.

### 2.1 Exemple de parcours

Une requête comme :

~~~sql
SELECT order_id, total_amount
FROM orders
WHERE customer_id = 42
ORDER BY order_date DESC;
~~~

peut nécessiter une lecture séquentielle suivie d’un tri, un accès par index sur customer_id avec un tri séparé, ou un parcours par index adapté au filtre et à l’ordre. Le meilleur choix dépend du nombre de commandes du client, de la taille totale de la table, de la forme des index et de la distribution des valeurs.

Le planificateur estime le coût de chaque stratégie. Ces estimations dépendent des statistiques et de ses hypothèses. Un plan avec un coût estimé supérieur n’est pas une mesure de durée en millisecondes ; le coût est une unité interne servant à comparer les stratégies.

### 2.2 Lire les estimations et les lignes observées

L’écart entre lignes estimées et lignes réelles constitue un indice important. Si le plan attend dix lignes mais en lit cent mille, les statistiques ou les hypothèses de distribution peuvent être insuffisantes. Le planificateur peut alors choisir une mauvaise stratégie de jointure ou un mauvais chemin d’accès.

Une estimation erronée n’implique pas toujours qu’il faut ajouter un index. Il faut examiner les statistiques, les corrélations entre colonnes, les valeurs très fréquentes et les filtres. Les mécanismes de statistiques étendues, les histogrammes et les estimations multicolonnes diffèrent selon les moteurs. Une correction doit correspondre à la capacité réelle du produit utilisé.

### 2.3 Ne pas additionner aveuglément les durées

Les durées ou coûts des nœuds d’un plan peuvent être imbriqués. Le temps d’un parent comprend une partie du travail réalisé par ses enfants. Additionner tous les temps d’un plan peut compter plusieurs fois le même travail. L’analyse doit examiner les opérateurs qui produisent beaucoup de lignes, les accès répétés et les étapes qui consomment des ressources.

### 2.4 EXPLAIN ANALYZE avec prudence

EXPLAIN ANALYZE exécute l’instruction mesurée. Une lecture peut mobiliser une grande quantité de CPU ou d’entrées-sorties. Une écriture peut modifier les données. Utilisez un environnement de test, une transaction annulable lorsque c’est adapté et un volume contrôlé. Le rollback ne protège pas de tous les coûts opérationnels : une requête a pu consommer des ressources, remplir des journaux ou provoquer des verrous pendant son exécution.

## 3. Lecture séquentielle et accès par index

Une lecture séquentielle parcourt une partie ou la totalité des pages de table. Elle peut être optimale quand une forte proportion des lignes doit être lue ou lorsque la table est petite. Un index fournit une structure de recherche qui permet de trouver certaines lignes sans parcourir toute la table, mais il doit lui-même être parcouru et peut conduire à des accès supplémentaires aux pages de données.

Le mot « séquentiel » ne signifie pas « mauvais ». Une lecture séquentielle d’une petite table de référence est souvent une bonne décision. L’index n’est pas une promesse de performance. Un index non sélectif, mal ordonné ou inutilisé peut occuper de l’espace et ralentir les écritures sans améliorer les requêtes importantes.

### 3.1 Sélectivité

La sélectivité décrit la fraction des données qui satisfait une condition. Une valeur unique dans une colonne presque unique peut être très sélective. Une condition sur une colonne où la moitié des lignes partage la même valeur est beaucoup moins sélective. Le type d’index, les statistiques et le stockage influencent néanmoins la décision.

Pour décider si l’index est utile, mesurez la proportion de lignes attendues et la fréquence de la requête. Une recherche qui retourne 30 % de la table peut être légitimement exécutée par lecture séquentielle sur certains moteurs. Le seuil n’est pas universel : il dépend de la taille des lignes, de l’état du cache, du coût du stockage et du modèle de charge.

### 3.2 Index B-tree

Les index B-tree conviennent à de nombreux motifs d’égalité et de plage, comme l’identifiant d’un client, les dates ou les montants. Ils peuvent parfois fournir des lignes dans l’ordre attendu et éviter un tri explicite. Les détails de tri, de nullité et de couverture dépendent du moteur.

Un index ne remplace pas les contraintes d’intégrité. Une clé primaire ou une contrainte UNIQUE apporte une garantie de données ; un index créé pour accélérer un rapport répond principalement à un besoin d’accès. Les deux usages peuvent s’appuyer sur des structures d’index, mais leur rôle logique diffère.

### 3.3 Index composite

Considérons les requêtes fréquentes :

~~~sql
SELECT order_id, order_date, total_amount
FROM orders
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 20;
~~~

Un index composite sur customer_id puis order_date peut mieux correspondre à ce motif qu’un index indépendant sur chaque colonne. Il faut cependant vérifier si le moteur peut exploiter l’ordre inverse, si des colonnes additionnelles sont nécessaires et si le bénéfice justifie la taille et le coût de maintenance.

La règle dite du préfixe ne doit pas devenir une incantation. L’ordre des colonnes est lié aux conditions de recherche, aux comparaisons, à la plage, à l’ordre et au moteur. Un index conçu pour customer_id suivi de order_date ne répond pas nécessairement aussi efficacement à une requête qui ne filtre que sur order_date.

### 3.4 Index partiel, expression et couverture

Certains moteurs permettent des index limités à un sous-ensemble de lignes, des index sur une expression ou des stratégies de couverture. Ils peuvent être utiles pour des requêtes très ciblées, mais ajoutent des conditions de compatibilité et de maintenance. Vérifiez la version, la syntaxe et la façon dont le planificateur reconnaît le prédicat de la requête.

Un index partiel réservé aux commandes terminées peut réduire l’espace utilisé si cette partie est petite et si le rapport filtre systématiquement le même statut. Si la requête ne contient pas un prédicat compatible, le planificateur peut ne pas pouvoir utiliser cet index. Les index d’expression nécessitent aussi que les expressions de requête correspondent aux règles reconnues par le moteur.

## 4. Statistiques et cardinalités

Le planificateur utilise des statistiques pour estimer le nombre de lignes. Ces statistiques peuvent devenir obsolètes lorsque la table évolue fortement, après un import massif, une suppression importante ou un changement inhabituel de distribution. Les opérations d’actualisation des statistiques ont un nom et un comportement propres au moteur.

La bonne démarche est de comparer la taille réelle, le volume de modifications récentes et les estimations du plan. Ne lancez pas aveuglément toutes les commandes de maintenance sur une grande production : l’opération peut consommer des ressources ou appliquer des effets qui doivent être coordonnés. Définissez les conditions et le créneau adaptés au moteur.

Une distribution très asymétrique est un cas difficile. Par exemple, une région peut contenir 70 % des commandes alors que plusieurs autres régions ne représentent chacune que quelques pourcents. Une estimation uniforme peut conduire à choisir une stratégie inadéquate pour certaines valeurs. Les histogrammes et statistiques de valeurs fréquentes aident, mais il faut vérifier la façon dont le moteur modélise les corrélations entre plusieurs colonnes.

## 5. Optimiser les jointures

Les stratégies de jointure comprennent notamment des méthodes par boucles imbriquées, par hachage et par fusion, selon le moteur. Aucune n’est toujours meilleure. Une boucle imbriquée peut être efficace si l’ensemble extérieur est petit et si l’accès intérieur est rapide. Un hachage peut convenir à des ensembles plus larges. Une fusion peut tirer parti d’un ordre déjà disponible ou d’un tri.

### 5.1 Boucles imbriquées

Une boucle imbriquée traite les lignes d’un ensemble et recherche les correspondances dans l’autre. Elle peut être très efficace pour quelques clients auxquels on associe quelques commandes avec un index adapté. Elle peut devenir coûteuse si l’ensemble extérieur est énorme et si chaque itération déclenche un accès cher.

### 5.2 Jointure par hachage

Une jointure par hachage construit une structure de recherche à partir d’un ensemble et l’utilise pour faire correspondre l’autre. Elle consomme de la mémoire. Si les données dépassent la mémoire disponible, des opérations temporaires peuvent apparaître. Une hausse du volume ou de la concurrence peut donc modifier le comportement, même si la requête ne change pas.

### 5.3 Jointure par fusion

Une jointure par fusion utilise l’ordre des clés de jointure. Si les entrées sont déjà ordonnées, elle peut éviter certains coûts ; sinon, le tri préalable peut être important. L’ordre qui convient à une jointure peut différer de celui d’un rapport final. Il faut regarder le plan complet plutôt que juger un opérateur en isolation.

### 5.4 Réduire les lignes avant la jointure

Si un rapport ne nécessite que les commandes terminées d’un trimestre, appliquez ce filtre dans la logique qui produit l’ensemble de commandes avant de joindre des relations volumineuses, lorsque le contrat SQL le permet. Le planificateur peut souvent pousser des prédicats, mais une expression complexe ou une fonction peut limiter cette optimisation. La vérification se fait dans le plan, pas seulement à partir de l’apparence du SQL.

## 6. Agrégation, tri et tables temporaires

GROUP BY, DISTINCT, ORDER BY et certaines fonctions de fenêtre peuvent nécessiter un tri ou une structure de hachage. Le coût dépend du volume, du nombre de groupes, de la taille des lignes et de la mémoire disponible. Si la mémoire ne suffit pas, le moteur peut utiliser des fichiers temporaires, ce qui peut allonger le traitement.

Un tri peut aussi être évitable lorsque les données sont disponibles dans un ordre compatible via un index. Mais un index qui élimine un tri pour une requête peut ralentir les écritures et occuper beaucoup d’espace. Il faut comparer le coût global et non optimiser un seul opérateur au détriment des autres charges.

Le DISTINCT global doit attirer l’attention lorsqu’il est ajouté pour « corriger » des doublons inattendus. Les doublons peuvent provenir d’une jointure au mauvais niveau de détail, d’une relation plusieurs-à-plusieurs ou d’une contrainte absente. DISTINCT peut être exactement la règle demandée, mais il ne doit pas servir à dissimuler une erreur de modèle.

## 7. Fonctions et filtres non sargables

Une condition peut empêcher l’utilisation efficace d’un index si elle applique une transformation à la colonne d’une manière que le moteur ne peut pas exploiter. Par exemple, appliquer une fonction à la date peut empêcher certains accès par plage selon le moteur et les index disponibles.

Au lieu de filtrer par l’année extraite de chaque date, il peut être plus efficace d’utiliser une plage explicite couvrant l’année. La règle doit prendre en compte le type, le fuseau horaire si applicable et la précision des valeurs. Ne réécrivez pas une condition sans vérifier qu’elle conserve le même résultat aux bornes.

Les conversions implicites peuvent également changer le plan ou l’égalité. Comparez les types des colonnes et des paramètres, vérifiez la syntaxe et évitez de compter sur des conversions automatiques peu documentées. Un paramètre typé correctement peut être aussi important qu’un index.

## 8. Mesurer une optimisation correctement

Une expérience doit modifier une seule variable à la fois. Si vous ajoutez un index, réécrivez la requête, changez les statistiques et augmentez la mémoire simultanément, vous ne saurez pas quelle modification a fourni le gain ou introduit une régression.

Procédez ainsi :
1. figez la requête et le jeu de données de référence ;
2. mesurez plusieurs exécutions dans un état défini ;
3. enregistrez le plan et les métriques pertinentes ;
4. appliquez une seule modification ;
5. répétez les mesures dans des conditions comparables ;
6. validez la correction fonctionnelle ;
7. mesurez l’impact sur les autres opérations qui utilisent la même table ;
8. rédigez une décision.

Les résultats doivent distinguer le cache froid et le cache chaud si les deux situations existent en production. Ne videz pas le cache de production pour créer un test. Utilisez une base isolée et un protocole qui reproduit le profil de charge.

### 8.1 Tester sous concurrence

Une requête peut être rapide seule et lente lorsque vingt autres requêtes consomment les mêmes ressources. L’optimisation se juge donc sur un scénario représentatif avec un nombre raisonnable de clients, une distribution réaliste des paramètres et une durée suffisante pour observer les pointes.

Gardez un œil sur les taux d’erreur et les attentes. Un débit plus élevé accompagné de davantage de timeouts n’est pas une amélioration sans réserve. Les limites du pool de connexions, les verrous et la mémoire par requête peuvent devenir les nouvelles contraintes.

### 8.2 Gain relatif et gain absolu

Passer de 10 secondes à 5 secondes représente une réduction de 50 %, mais l’opération prend encore 5 secondes. Passer de 20 millisecondes à 10 millisecondes représente aussi 50 %, mais le bénéfice utilisateur peut différer. Priorisez en fonction de la fréquence, de l’impact, des objectifs de latence et du coût de changement.

Une requête rarement exécutée mais très longue peut bloquer un traitement de clôture. Une requête courte exécutée très souvent peut dominer la consommation globale. Le classement des priorités doit utiliser les durées cumulées, la fréquence et les conséquences métier.

## 9. Quand ne pas ajouter un index

Un index supplémentaire peut être inutile lorsque la table est petite, quand le filtre renvoie une grande fraction des lignes, lorsque la requête ne correspond pas à l’ordre de colonnes, lorsque l’index dupliqué existe déjà ou lorsque le principal coût est ailleurs. Chaque index augmente l’espace, les opérations de maintenance et souvent le coût des INSERT, UPDATE et DELETE.

Un index redondant n’est pas toujours évident. Deux index qui semblent similaires peuvent différer sur l’ordre, les colonnes incluses ou les conditions. Il faut inspecter les définitions exactes et les usages mesurés avant de supprimer. Dans certains moteurs, les statistiques d’usage peuvent être réinitialisées ou ne représenter que la période depuis le dernier démarrage ; elles doivent être interprétées avec prudence.

Avant de retirer un index, vérifiez les contraintes, les requêtes rares mais critiques, les traitements de nuit, les besoins de tri et les chemins de récupération. Déployez une suppression avec une procédure de restauration de l’index lorsque le risque l’exige. Une baisse de coût d’écriture peut être annulée par une régression sur une requête essentielle.

## 10. Atelier pratique guidé : optimiser une recherche de commandes

### But

Comparer trois stratégies pour obtenir les vingt dernières commandes d’un client : sans index adapté, avec un index simple et avec un index composite.

### Préparation

Créez un jeu synthétique de commandes réparties entre plusieurs milliers de clients. Assurez-vous qu’un client possède à la fois peu et beaucoup de commandes. Chargez assez de lignes pour rendre les plans visibles, puis actualisez les statistiques avec la méthode adaptée au moteur.

Exécutez :

~~~sql
SELECT order_id, order_date, total_amount
FROM orders
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 20;
~~~

Enregistrez le plan et plusieurs temps d’exécution. Créez ensuite un index sur customer_id, puis comparez. Enfin, essayez un index composite sur customer_id et order_date, si la syntaxe et les options du moteur le permettent. Vérifiez le contenu des résultats après chaque variante : les mêmes vingt lignes doivent être retournées avec le même ordre et la même règle d’égalité.

### Analyse

Relevez si le plan utilise un parcours séquentiel, un accès par index, un tri ou un autre opérateur. Comparez les lignes estimées et observées. Consignez l’effet sur l’INSERT et l’UPDATE de quelques milliers de lignes, puisque chaque index supplémentaire doit être maintenu.

### Critères d’acceptation

- La requête retourne exactement le même résultat fonctionnel.
- La mesure distingue plusieurs exécutions et l’état du cache.
- Les plans sont sauvegardés.
- Les coûts de mise à jour et l’espace sont considérés.
- La décision explique pourquoi l’index apporte ou non une valeur.
- Un autre apprenant peut répéter l’essai.

## 11. Étude de cas : rapport lent après une croissance de volume

### Situation

Un rapport de commandes prenait 700 millisecondes avec le volume de test et dépasse désormais 8 secondes. Le SQL n’a pas changé. Le nombre de lignes a fortement augmenté et une nouvelle région représente une large part des données.

### Diagnostic

L’équipe compare les plans historiques et actuels. Elle remarque que l’estimation du nombre de lignes filtrées est très éloignée de la réalité. Le plan choisit une stratégie de jointure coûteuse et trie un résultat intermédiaire volumineux. Le diagnostic inclut les statistiques, la distribution des valeurs, l’ordre des jointures, les index, les lectures et les fichiers temporaires.

### Correction

Les statistiques sont actualisées selon une procédure adaptée et le plan est re-mesuré. La requête est également reformulée pour filtrer tôt les commandes du périmètre requis, sans supprimer les lignes métier attendues. Un index composite est testé seulement après avoir vérifié qu’il répond au motif de filtre et d’ordre. L’équipe rejette une proposition d’ajouter trois index redondants parce que les tests ne montrent aucun bénéfice complémentaire.

### Preuve

Le résultat est comparé à un calcul de référence et le plan doit montrer que les estimations et le volume traité sont plus cohérents. Le test de charge mesure la latence et les erreurs. Les écritures sont également observées pour détecter le coût de maintenance introduit par l’index. La correction est validée sur plusieurs valeurs de région, notamment celle qui représente la plus forte proportion de données.

## 12. Exercices corrigés

### Exercice 1 — Lecture séquentielle

**Énoncé.** Le plan effectue une lecture séquentielle sur une table de quelques centaines de lignes malgré un index sur la colonne filtrée. Est-ce forcément un défaut ?

**Correction.** Non. Le coût de lire toute la petite table peut être inférieur à celui de parcourir l’index et de récupérer les lignes correspondantes. Vérifiez la sélectivité, la taille, les estimations et le résultat mesuré. L’existence d’un index ne signifie pas qu’il doit être utilisé.

### Exercice 2 — Estimation erronée

**Énoncé.** Le plan estime que dix lignes seront retournées mais observe 100 000 lignes. Quel est le premier axe d’investigation ?

**Correction.** Examinez la distribution des données, les statistiques, la corrélation entre filtres et les paramètres de la requête. Une estimation fausse peut conduire à une mauvaise stratégie de jointure. Ajouter un index sans corriger l’estimation ou comprendre le volume peut ne pas résoudre la cause.

### Exercice 3 — Index composite

**Énoncé.** Un rapport filtre par customer_id et trie par order_date. Quel est l’intérêt possible d’un index composite ?

**Correction.** Un index dont l’ordre est compatible avec le filtre et le tri peut réduire le nombre de lignes parcourues et parfois éviter un tri séparé. Il faut tester le plan, la sélectivité, la taille et le coût des mises à jour ; aucun index n’est garanti utile pour tous les profils.

### Exercice 4 — Index et écritures

**Énoncé.** Après l’ajout de quatre index, les rapports sont un peu plus rapides mais les imports ralentissent fortement.

**Correction.** Chaque index supplémentaire doit être maintenu lors des insertions et des mises à jour. Mesurez leur bénéfice par usage et retirez les structures redondantes uniquement après avoir vérifié les contraintes et les requêtes rares. L’optimisation est un compromis entre lectures, écritures et stockage.

### Exercice 5 — EXPLAIN ANALYZE sur production

**Énoncé.** Un développeur veut lancer immédiatement une analyse complète sur une table critique pour confirmer une hypothèse.

**Correction.** Préparez une expérience contrôlée, vérifiez le coût potentiel et privilégiez un environnement représentatif. Une analyse qui exécute la requête peut consommer les mêmes ressources que la charge de production. Toute action en production exige autorisation et garde-fous.

### Exercice 6 — Variance de latence

**Énoncé.** Le temps moyen a baissé, mais le percentile élevé s’est dégradé.

**Correction.** Examinez la distribution et le profil concurrent. Un changement peut améliorer les requêtes fréquentes tout en pénalisant les valeurs rares ou les périodes de pointe. Il faut relier la latence à la sélectivité, à la concurrence et aux objectifs de service.

## 13. Défi final corrigé : justifier un index en production

### Énoncé

Un endpoint fournit les commandes récentes d’un client. Il est exécuté 20 000 fois par heure et sa latence au percentile 95 dépasse 400 millisecondes. L’équipe propose un index composite. Préparez une décision technique.

### Correction attendue

**1. Définir la cible.** Mesurez le percentile visé, le taux d’erreur, la fréquence, les paramètres, le volume et le comportement sous concurrence. Définissez l’objectif attendu, par exemple réduire la latence au percentile 95 sans détériorer les écritures critiques.

**2. Vérifier l’exécution.** Collectez le plan et les temps, identifiez les lignes estimées et réellement parcourues, le tri et les autres opérations coûteuses. Établissez si le temps est consommé dans le moteur ou avant/après l’exécution.

**3. Formuler l’index.** Choisissez les colonnes à partir du filtre, de l’ordre, des opérateurs et des distributions. Vérifiez l’existence d’index similaires. Décrivez pourquoi l’ordre proposé répond au motif réel.

**4. Tester la fonctionnalité.** Comparez les résultats exacts avant et après, y compris les commandes à montants égaux, les dates identiques et les clients qui ont peu de commandes. L’index ne doit changer ni le contrat de sortie ni le choix des lignes.

**5. Mesurer les effets.** Répétez les essais avec plusieurs paramètres et sous concurrence. Mesurez la taille de l’index, les écritures et le comportement des autres requêtes importantes. Gardez des conditions de test comparables.

**6. Décider.** Conservez l’index uniquement si la preuve montre un bénéfice correspondant à l’objectif et un coût acceptable. Documentez les limites, l’effet observé et la manière de revenir à l’état antérieur.

**7. Déployer prudemment.** Vérifiez la méthode de création adaptée à la version et au contexte. Surveillez la charge, les verrous, la latence et les erreurs. Prévoyez des critères d’arrêt et une méthode de retrait ou de restauration.

La décision finale doit contenir les mesures de référence, les plans, le résultat fonctionnel et le coût secondaire. Un index est justifié par une preuve, pas par son apparente sophistication.

## 14. Gestion du cycle de vie d’un index

Créer un index est une modification de schéma qui doit être gérée comme un changement logiciel. Avant la création, recherchez les index existants, leurs définitions exactes et leurs usages connus. Après la création, surveillez la requête ciblée, mais aussi les écritures, l’espace et les autres requêtes qui utilisent la même relation. Un index peut améliorer un chemin et rendre un autre chemin moins favorable s’il modifie le choix du planificateur.

La suppression mérite le même soin. Un index apparemment inutilisé peut servir à un traitement mensuel ou à un scénario de reprise rarement exécuté. Les statistiques d’usage dépendent de la période observée et des redémarrages du serveur. Faites correspondre la fenêtre de collecte aux cycles d’activité réels. Si possible, utilisez un environnement de préproduction pour comparer les plans avant de supprimer une structure.

Préparez un changement réversible : définition de l’index, commande adaptée au moteur, durée estimée, éventuels verrous, surveillance et critères d’arrêt. La restauration d’un index peut être possible mais prend du temps et consomme des ressources ; cette réalité doit être incluse dans le plan. Une suppression ne doit pas se faire au milieu d’un incident sans compréhension de ses conséquences.

Après le déploiement, conservez un court dossier : objectif, référence avant changement, définition, résultat de performance, coût d’écriture, taille et décision. Si le gain disparaît avec une croissance du volume ou une évolution de distribution, le dossier aide à comprendre pourquoi. La maintenance est continue : elle ne se résume pas à créer le plus grand nombre d’index possible.

### Procédure d’arrêt d’une expérimentation

Définissez à l’avance les signaux qui vous feront interrompre l’essai : augmentation nette des erreurs, ralentissement des transactions non ciblées, saturation du stockage temporaire, hausse des verrous ou dépassement d’un budget de charge. L’arrêt doit lui-même être sûr et documenté. Si un test est exécuté en concurrence, terminez les clients de test et vérifiez que les transactions temporaires ont été clôturées. Ne laissez pas une expérimentation abandonnée continuer à consommer des ressources.

Une comparaison est recevable lorsque les deux variantes ont été exécutées sur le même jeu et des paramètres comparables, que le résultat fonctionnel est identique et que les effets secondaires sont consignés. Si les mesures varient beaucoup entre les essais, augmentez le nombre d’observations ou cherchez la source de la variance avant de conclure. La bonne décision peut être de ne pas modifier le schéma si la preuve est insuffisante.

## Fiche de vérification

- La requête et les paramètres sont reproductibles.
- Le plan est analysé avec les estimations et les mesures réelles.
- La sélectivité est comprise.
- Les index existants ont été examinés.
- Les coûts de stockage et d’écriture sont évalués.
- Le résultat métier est identique avant et après.
- Les mesures représentent le profil réel de charge.
- Les conditions de déploiement et de retour arrière sont documentées.

## Glossaire

**Planificateur** : composant qui choisit une stratégie d’exécution SQL.

**Cardinalité** : nombre de lignes estimées ou produites par une étape.

**Sélectivité** : part des lignes qui satisfait une condition.

**Index composite** : index dont les clés suivent un ordre de plusieurs colonnes.

**Lecture séquentielle** : parcours d’une suite de pages de table plutôt qu’une recherche ciblée via index.

**Plan d’exécution** : représentation des opérateurs et du chemin choisi pour exécuter la requête.

**SARGable** : condition formulée de façon à pouvoir exploiter efficacement un index quand c’est pertinent.

**Latence** : temps nécessaire à une opération.

**Débit** : nombre d’opérations traitées par unité de temps.

**Cardinalité estimée** : nombre de lignes que le planificateur prévoit de traiter.

**Cardinalité observée** : nombre de lignes réellement traitées pendant l’exécution mesurée.
