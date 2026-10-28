# Entrepôt de données et ETL — Intermédiaire

> **Mise en contexte.** La direction de Skill-Tree veut savoir quels cours améliorent le plus la réussite, quels apprenants abandonnent le parcours et combien de temps sépare l’inscription de la certification. La base transactionnelle sait répondre à certaines questions, mais les analyses historiques y provoquent des requêtes lourdes, le modèle applicatif est organisé pour gérer le quotidien et les données arrivent de plusieurs systèmes avec des formats différents. Il faut maintenant construire une chaîne analytique qui transforme des événements opérationnels en indicateurs fiables, sans confondre les données de production avec un modèle d’analyse.

## Objectifs pédagogiques

À la fin de ce cours, vous saurez distinguer une base transactionnelle d’un entrepôt analytique, définir le grain d’une table de faits, concevoir des dimensions, comprendre les schémas en étoile et en flocon, comparer ETL et ELT, concevoir un chargement initial et des chargements incrémentaux, gérer les dimensions à évolution lente, appliquer des contrôles de qualité et rendre les traitements rejouables. Vous devrez aussi pouvoir expliquer pourquoi une moyenne peut être fausse si l’événement compté est mal défini, et comment tester qu’une chaîne analytique est complète.

Le fil rouge utilise des données de plateforme de formation : cours, apprenants, inscriptions, tentatives d’examen, résultats, certificats et sessions d’apprentissage. L’objectif est de produire des analyses fiables sans faire porter toutes les requêtes historiques sur la base transactionnelle. Les exemples SQL sont proches de PostgreSQL, mais les principes de modélisation sont transférables à de nombreux entrepôts. Les outils de transformation changent selon l’organisation et ne doivent pas être considérés comme obligatoires.

## 1. OLTP et OLAP répondent à des besoins différents

Les systèmes OLTP, pour Online Transaction Processing, gèrent des opérations fréquentes, courtes et précises : créer une inscription, enregistrer un résultat, modifier un profil ou attribuer un certificat. Leur modèle cherche à préserver les règles d’intégrité, réduire les anomalies de mise à jour et répondre aux lectures et écritures opérationnelles. La charge peut être caractérisée par une forte concurrence, de petites transactions et une tolérance faible aux erreurs de cohérence.

Les systèmes OLAP, pour Online Analytical Processing, répondent à des questions d’analyse : évolution du taux de réussite, répartition des activités par domaine, comparaison entre cohortes et tendance sur plusieurs années. Une seule requête peut parcourir un grand nombre de lignes, regrouper des données et calculer des indicateurs historiques. L’architecture analytique optimise souvent les scans, l’agrégation, le stockage en colonnes ou la parallélisation, plutôt que l’insertion d’une opération transactionnelle isolée.

Les deux mondes ne sont pas nécessairement deux produits totalement séparés. Un petit projet peut commencer avec une base et un ensemble de vues ou de tables résumées. Lorsque la volumétrie et la concurrence augmentent, il devient utile de séparer les environnements ou d’utiliser une plateforme analytique spécialisée. La décision doit partir du volume, de la fraîcheur attendue, du coût, des besoins de sécurité et de l’impact sur l’application.

Une requête analytique ne doit pas être déplacée mécaniquement vers un entrepôt sans examiner la qualité de ses données. Si les événements d’origine sont incomplets, si les horodatages n’utilisent pas la même convention, si un utilisateur possède plusieurs identifiants ou si le statut de réussite change sans historique, le résultat de l’analyse sera biaisé. Le premier travail d’un entrepôt consiste à expliciter la sémantique des événements et à documenter les transformations appliquées.

## 2. Architecture analytique de bout en bout

Une architecture analytique comprend les sources, l’extraction ou la capture des changements, une zone d’atterrissage, les transformations, les modèles d’analyse, les contrôles, la publication et la consommation par les outils de reporting. Chaque zone répond à une responsabilité distincte. La zone d’atterrissage conserve souvent une copie aussi proche que possible de la source; la zone transformée normalise les types, noms et clés; les modèles de consommation présentent des mesures et dimensions documentées.

~~~mermaid
flowchart LR
    A[Applications et bases OLTP] --> B[Extraction ou CDC]
    B --> C[Zone brute]
    C --> D[Nettoyage et standardisation]
    D --> E[Modèle analytique]
    E --> F[Qualité et rapprochement]
    F --> G[Mart et indicateurs]
    G --> H[BI et analyses]
    I[Catalogue et lignage] --> C
    I --> D
    I --> E
    J[Orchestration et alertes] --> B
    J --> D
    J --> G
~~~

Une chaîne n’est pas fiable seulement parce que chaque tâche est verte. Il faut vérifier qu’un lot complet a été traité, que les lignes attendues ont été lues, que les rejets sont visibles, que les transformations ont la bonne version et que les données publiées respectent les invariants. Si la source est inaccessible pendant une heure, l’orchestrateur doit indiquer si le lot est retardé, s’il peut être relancé et si le tableau de bord doit signaler un retard de fraîcheur.

La zone brute est utile pour réexécuter une transformation sans relire la source opérationnelle, et pour comparer les données originales aux données nettoyées. Elle doit cependant avoir une politique de rétention, d’accès, de chiffrement et de suppression. Une copie brute peut contenir toutes les données personnelles de la source; elle ne doit pas devenir un espace librement accessible au seul motif qu’elle est temporaire.

Les transformations doivent être ordonnées en fonction de leurs dépendances. Une dimension cours peut devoir être mise à jour avant de charger des faits qui la référencent. Une tâche de synthèse peut attendre la fin de tous les lots de la période. L’orchestration doit décrire ces dépendances, les délais, les conditions de reprise et les règles de publication afin d’éviter que les utilisateurs consultent un indicateur construit sur des tables partiellement mises à jour.

## 3. Définir le grain avant la table de faits

Le grain définit exactement ce que représente une ligne d’une table. C’est l’une des décisions les plus importantes d’un entrepôt. Une ligne peut représenter une inscription à un cours, une tentative d’examen, un événement de lecture, une journée d’activité par apprenant ou un total mensuel par cours. Tant que le grain n’est pas explicite, les mesures et les jointures peuvent devenir ambiguës.

Supposons une table de faits qui contient une ligne par tentative d’examen terminée. Elle peut enregistrer une clé de tentative, la clé de l’apprenant, la clé du cours, la date de l’évaluation, le score et un indicateur de réussite. Un nombre de lignes équivaut alors au nombre de tentatives terminées, pas au nombre d’apprenants uniques ni au nombre de certifications. Une personne peut effectuer plusieurs tentatives sur le même cours; compter les lignes comme des apprenants conduirait à surestimer le public.

Un autre fait peut représenter une inscription. Il a un grain différent et peut être associé à zéro, une ou plusieurs tentatives. Les joindre directement avant agrégation peut multiplier les lignes. Pour calculer la meilleure tentative par inscription, il faut définir si une tentative est choisie, si l’on calcule un maximum ou si toutes les tentatives doivent être comptées. Les requêtes analytiques doivent refléter les règles métier, pas seulement la structure des clés.

Une table de faits doit donc documenter son grain dans son nom, sa description et ses tests. Les métriques doivent être nommées de façon explicite : nombre de tentatives, nombre d’apprenants distincts, taux de réussite des tentatives ou taux de cours terminés. Deux indicateurs qui semblent voisins peuvent avoir des dénominateurs différents et produire des conclusions différentes. La documentation doit préciser les filtres inclus, les données exclues, les périodes et la manière de traiter les résultats manquants.

## 4. Schéma en étoile et dimensions

Un schéma en étoile place une table de faits au centre et la relie à des dimensions descriptives. Les dimensions permettent de filtrer et regrouper les faits selon les cours, les apprenants, les dates, les niveaux, les domaines ou les cohortes. Elles sont souvent dénormalisées pour faciliter la consommation analytique. Un schéma en flocon normalise davantage certains niveaux de dimension, ce qui peut réduire les duplications mais rendre les requêtes plus complexes.

~~~mermaid
flowchart TD
    F[FactTentatives] --> D1[DimApprenant]
    F --> D2[DimCours]
    F --> D3[DimDate]
    F --> D4[DimCohorte]
    F --> M1[Score et nombre de tentatives]
    D1 --> Q[Rapports par public]
    D2 --> Q2[Rapports par domaine]
    D3 --> Q3[Rapports temporels]
~~~

Une dimension cours peut contenir une clé de dimension, l’identifiant opérationnel du cours, son titre, son domaine, son niveau et une catégorie de publication. La clé de dimension peut être une clé substitut indépendante de l’identifiant source. Cela permet de suivre certaines évolutions et de distinguer les versions successives d’une entité si la règle métier le demande. L’identifiant source reste utile pour le rapprochement et le lignage.

Une dimension date est souvent un calendrier préconstruit avec année, trimestre, mois, semaine, jour ouvré, jour férié éventuel et autres attributs nécessaires. Elle évite que chaque rapport réimplémente les mêmes règles temporelles. Les périodes financières, fuseaux horaires, années fiscales et semaines ISO doivent être définis explicitement. Un simple DATE_TRUNC n’exprime pas nécessairement le calendrier métier d’une entreprise.

Les faits contiennent des clés vers les dimensions et des mesures quantitatives. Certaines valeurs sont additives — par exemple le nombre de tentatives — d’autres sont semi-additives — par exemple un solde observé à un instant — et d’autres ne s’additionnent pas du tout, comme un ratio déjà calculé. Il est dangereux d’additionner des taux pour obtenir un taux global. Le taux global doit être recalculé à partir de son numérateur et de son dénominateur agrégés.

## 5. Modèle de fait exemple en SQL

La table ci-dessous illustre une clé substitut de dimension, une clé source et des attributs descriptifs. Dans un véritable projet, le type des clés, la politique d’identifiants et les dates de validité doivent être adaptés à l’entrepôt et aux sources.

~~~sql
CREATE TABLE dim_cours (
    cours_sk BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cours_source_id BIGINT NOT NULL,
    titre TEXT NOT NULL,
    domaine TEXT NOT NULL,
    niveau TEXT NOT NULL,
    date_debut_validite DATE NOT NULL,
    date_fin_validite DATE,
    version_courante BOOLEAN NOT NULL DEFAULT true
);
~~~

Une table de faits avec un grain d’une ligne par tentative terminée pourrait ressembler à ceci :

~~~sql
CREATE TABLE fact_tentatives (
    tentative_source_id BIGINT NOT NULL,
    apprenant_sk BIGINT NOT NULL,
    cours_sk BIGINT NOT NULL REFERENCES dim_cours(cours_sk),
    date_sk INTEGER NOT NULL,
    score NUMERIC(5,2),
    tentative_reussie BOOLEAN NOT NULL,
    nombre_tentatives INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (tentative_source_id)
);
~~~

Le modèle est volontairement minimal et ne couvre pas toutes les contraintes de production, comme la dimension date, la gestion des doublons de source, les dates de chargement, la provenance ou les contrôles de plage. Il permet néanmoins d’illustrer la différence entre une mesure et un attribut de dimension. Un vrai modèle devrait aussi indiquer l’heure de chargement, la version du lot et éventuellement une clé de source plus complexe.

Les clés de dimension doivent être résolues au chargement. Si un fait arrive alors que la dimension associée n’est pas encore présente, il faut choisir une stratégie : rejeter le fait, le placer en attente, créer un membre inconnu ou utiliser une clé à statut temporaire. La stratégie doit être documentée, puis les faits doivent être réconciliés lorsque la dimension apparaît. Ignorer silencieusement la ligne crée un biais.

## 6. ETL et ELT

ETL signifie Extract, Transform, Load : les données sont extraites, transformées puis chargées dans la cible. Historiquement, ce modèle permettait de nettoyer et normaliser les données avant de les insérer dans un entrepôt. ELT signifie Extract, Load, Transform : les données sont d’abord chargées dans la plateforme cible, puis transformées à l’aide de ses capacités de calcul. Les deux approches existent aujourd’hui; le choix dépend du système source, du stockage, du moteur de transformation, de la sécurité et de l’usage de la zone brute.

ETL peut être adapté lorsque la donnée doit être filtrée ou masquée avant l’arrivée dans l’entrepôt, lorsque le traitement doit fonctionner sur une plateforme distincte ou lorsque les étapes de nettoyage sont intégrées à un outil existant. ELT convient lorsque la plateforme de destination offre de bonnes capacités de transformation, que les données brutes peuvent être stockées de façon contrôlée et que les équipes veulent versionner les transformations près des modèles analytiques.

Le principe important est de traiter les transformations comme du code de production. Les règles doivent être versionnées, relues, testées et déployées par étapes. Les transformations manuelles exécutées dans un éditeur BI deviennent difficiles à reproduire. Le modèle analytique doit être reconstruit à partir de la zone de données et de la version de code enregistrée, avec un historique qui permet d’expliquer pourquoi une valeur a changé.

Une chaîne bien conçue distingue extraction, nettoyage, normalisation, déduplication, résolution des dimensions, calcul des faits, contrôles de qualité et publication. Chaque étape a des entrées et sorties définies. Les lots doivent être identifiables et idempotents. Une étape qui échoue ne doit pas publier de manière silencieuse un résultat partiel; le système doit soit reprendre le lot, soit le marquer comme incomplet, soit publier un état de fraîcheur explicite.

## 7. Chargement initial et incrémental

Un chargement initial copie l’historique requis dans la cible. Il peut être coûteux et créer une fenêtre où la source continue à changer. Il faut donc définir un point de cohérence, un volume cible, le traitement des écritures qui surviennent pendant la copie et la procédure de rapprochement. Un chargement qui copie d’abord les cours puis les tentatives sans contrôler les changements peut créer des références manquantes ou des doublons.

Le chargement incrémental traite uniquement les nouveaux éléments ou les changements depuis le dernier point de capture. Il nécessite un mécanisme fiable pour identifier les changements : colonne de mise à jour, numéro de séquence, journal de modifications, CDC ou flux d’événements. Une colonne updated_at peut être insuffisante si des mises à jour partagent le même timestamp, si une transaction est retardée ou si une suppression ne laisse pas de ligne à détecter. Le mécanisme de capture doit garantir que les changements sont observables.

Un curseur de traitement peut être un identifiant monotone, une position dans un journal ou un couple timestamp plus identifiant. Le traitement doit enregistrer la position seulement après que les données sont durables et que les contrôles ont réussi. Si le curseur avance trop tôt, une panne peut faire perdre des données. S’il avance trop tard sans déduplication, un rejeu peut créer des doublons. L’idempotence permet de reprendre sans changer le résultat final.

La capture des suppressions doit être planifiée. Une extraction qui ne récupère que les lignes présentes dans la source ne saura pas qu’une ligne a été supprimée, à moins qu’elle utilise un mécanisme de tombstone, un journal ou une comparaison de snapshots. Le modèle analytique doit savoir comment gérer la suppression : retirer une ligne, conserver un historique, marquer une dimension comme inactive ou préserver une valeur historique selon la règle métier.

## 8. CDC, latence et fraîcheur

Change Data Capture (CDC) consiste à capturer les changements réalisés sur une source, souvent à partir des journaux de transaction ou d’un mécanisme spécifique au moteur. CDC peut réduire la nécessité d’interroger la source avec des requêtes périodiques lourdes et améliorer la fraîcheur des modèles. Mais il ajoute un flux qui doit être surveillé, rejoué et réconcilié.

Une chaîne CDC doit définir la garantie de livraison, l’ordre des événements, les doublons possibles, les suppressions, les changements de schéma et les points de reprise. Les événements peuvent arriver plus d’une fois; le consommateur doit pouvoir les traiter de façon idempotente. L’ordre global n’est pas toujours garanti dans un pipeline distribué; il faut savoir si la règle métier a besoin de l’ordre par clé, par table ou par transaction.

La fraîcheur doit être mesurée. Le timestamp du dernier événement source, le timestamp de traitement et le timestamp de publication permettent de calculer le retard. Un dashboard peut afficher un résultat correct mais vieux de deux heures; c’est une forme de défaut si l’utilisateur pense consulter des données immédiates. Un indicateur de dernière mise à jour aide à rendre la limite visible.

Un pipeline temps réel n’est pas toujours nécessaire. Si une direction consulte des indicateurs une fois par jour, un traitement quotidien robuste peut être plus simple et moins coûteux qu’une chaîne d’événements en continu. La cadence doit être décidée à partir du besoin métier et non de la tendance technologique. Les exigences plus strictes doivent apporter une valeur mesurable.

## 9. Dimensions à évolution lente

Les dimensions à évolution lente, souvent appelées Slowly Changing Dimensions, décrivent comment représenter les changements d’attributs dans le temps. Si le titre d’un cours change, l’analyse historique doit parfois utiliser le titre actuel, parfois le titre tel qu’il était au moment de la tentative. Ces deux lectures ne sont pas équivalentes.

La stratégie Type 1 remplace la valeur existante sans conserver l’historique. Elle est utile lorsque la correction doit écraser une valeur erronée ou que l’ancien attribut n’est plus nécessaire. La stratégie Type 2 crée une nouvelle version de dimension avec des dates de validité ou un indicateur courant; les faits historiques peuvent alors référencer la version qui s’appliquait à leur période. Il existe d’autres variantes, mais ces deux idées montrent le choix principal entre correction immédiate et historique.

~~~mermaid
flowchart LR
    A[Cours version 1] -->|Titre initial valable du 1er janvier au 14 mai| B[Faits historiques]
    C[Changement du titre le 15 mai] --> D[Nouvelle version de dimension]
    D -->|Titre actuel à partir du 15 mai| E[Faits récents]
~~~

Un membre de dimension Type 2 peut comporter cours_source_id, cours_sk, titre, date_debut_validite, date_fin_validite et version_courante. Lors d’un changement suivi historiquement, la ligne courante est fermée et une nouvelle ligne est créée. Les faits doivent résoudre la bonne version selon la date métier définie. Une erreur de bornes — par exemple deux versions courantes qui se chevauchent — peut affecter les rapports de façon subtile.

Toutes les colonnes ne nécessitent pas une histoire Type 2. Une correction de typographie peut être un Type 1; un changement de domaine qui modifie l’interprétation historique peut justifier un Type 2. La règle doit être définie attribut par attribut et expliquée dans le catalogue analytique. Si le rapport peut accepter une catégorisation actuelle, documentez-le plutôt que de stocker inutilement toutes les versions.

## 10. Qualité et rapprochement des données

La qualité des données doit être mesurée avec des tests précis. La complétude vérifie que les champs requis sont présents; l’unicité vérifie les doublons; la validité examine les domaines de valeurs; la cohérence vérifie les relations entre champs et tables; la fraîcheur mesure le retard; le rapprochement compare les nombres et montants entre source et cible. Une règle de qualité doit indiquer le périmètre, le seuil, le propriétaire et la réaction lorsqu’elle échoue.

Un test simple peut vérifier qu’aucune tentative terminée ne référence un cours absent. Un autre peut comparer le nombre de tentatives terminées source avec le nombre de faits chargés pour la même période. Ces contrôles doivent être calculés dans un périmètre cohérent, prendre en compte les retards de CDC et distinguer un écart attendu d’une corruption. Un contrôle global sur un pipeline en retard produira des faux positifs s’il ignore la frontière de chargement.

~~~sql
SELECT f.tentative_source_id
FROM fact_tentatives f
LEFT JOIN dim_cours c ON c.cours_sk = f.cours_sk
WHERE c.cours_sk IS NULL;
~~~

Le résultat devrait être vide si la dimension résolue est obligatoire et que le chargement est complet. Si les lignes inconnues sont admises, la règle doit les vérifier séparément. Un test peut aussi détecter plusieurs versions courantes du même identifiant de source :

~~~sql
SELECT cours_source_id, count(*) AS versions_courantes
FROM dim_cours
WHERE version_courante = true
GROUP BY cours_source_id
HAVING count(*) > 1;
~~~

Le contrôle de qualité n’est pas seulement un rapport d’erreurs. Il faut décider si le lot est bloqué, mis en quarantaine, chargé avec une anomalie identifiée ou publié partiellement avec une alerte. La décision doit dépendre de la criticité de l’indicateur. Un défaut mineur de format de description et une clé étrangère manquante sur des résultats d’examen ne devraient pas avoir la même politique.

## 11. Orchestration, reprise et idempotence

L’orchestrateur déclenche les étapes dans l’ordre, garde les états, gère les dépendances, les fenêtres horaires, les reprises et les alertes. Un pipeline périodique doit connaître la date logique du lot, et pas seulement l’heure de la machine au lancement. Les traitements retardés doivent pouvoir être rejoués pour une période antérieure sans créer une nouvelle série de doublons.

Une opération idempotente produit le même état final lorsqu’elle est exécutée plusieurs fois avec les mêmes entrées. Dans un entrepôt, on peut utiliser un identifiant de lot, un MERGE ou UPSERT selon le moteur, une clé naturelle stable, une table de suivi ou un chargement en zone temporaire puis une promotion atomique. Le mécanisme exact dépend du moteur, mais le contrat de reprise doit être explicite.

Évitez de marquer un lot comme « réussi » avant que les faits aient été chargés et vérifiés. Si une tâche plante après le commit de données mais avant l’écriture du statut, la prochaine exécution doit détecter les données déjà chargées. Si le statut est enregistré avant le commit, une erreur peut empêcher le traitement de se terminer tout en faisant croire au pipeline qu’il n’y a plus rien à faire. Les données et l’état du lot doivent être coordonnés.

Un modèle robuste peut charger dans une zone temporaire identifiée par batch_id, effectuer les contrôles de qualité, puis appliquer les changements à la cible dans une étape transactionnelle lorsque le moteur et le volume le permettent. Pour de gros volumes ou un stockage distribué, la publication peut utiliser des fichiers immuables et un catalogue de versions. Quel que soit le mécanisme, le consommateur doit savoir quelle version est publiée et comment revenir à la version précédente.

La supervision doit présenter la durée par étape, le nombre de lignes lues, rejetées et écrites, le retard de la source, les tentatives de reprise, les erreurs et la dernière période publiée. Les alertes doivent être reliées à un propriétaire. Une tâche qui échoue tous les jours depuis une semaine sans conséquence visible dans l’application reste une dette de fiabilité.

## 12. Atelier : modèle analytique de tentatives

Créez un schéma de laboratoire comprenant une dimension cours, une dimension date et une table de faits avec un grain explicitement décrit. Chargez d’abord quelques cours et dates synthétiques; puis insérez des tentatives avec plusieurs scores par apprenant et cours. Calculez des indicateurs en vérifiant le dénominateur et le numérateur.

~~~sql
CREATE TABLE fact_tentatives_lab (
    tentative_id BIGINT PRIMARY KEY,
    apprenant_id BIGINT NOT NULL,
    cours_id BIGINT NOT NULL,
    date_tentative DATE NOT NULL,
    score NUMERIC(5,2),
    terminee BOOLEAN NOT NULL
);
~~~

Le premier rapport calcule la moyenne et le nombre de tentatives terminées par cours :

~~~sql
SELECT
    cours_id,
    count(*) FILTER (WHERE terminee) AS tentatives_terminees,
    count(DISTINCT apprenant_id) FILTER (WHERE terminee) AS apprenants_avec_tentative,
    avg(score) FILTER (WHERE terminee AND score IS NOT NULL) AS moyenne_score
FROM fact_tentatives_lab
GROUP BY cours_id;
~~~

Dans un moteur qui ne supporte pas la clause FILTER pour les agrégats, la même logique peut être écrite avec CASE. La sémantique doit être gardée identique. Vérifiez que le nombre de tentatives n’est pas confondu avec le nombre de personnes et que les scores NULL ne sont pas transformés en zéro sans justification.

Ajoutez ensuite une dimension cours de type 2. Simulez le changement de titre d’un cours à une date donnée. Insérez des faits avant et après la date, puis écrivez deux rapports : l’un qui utilise la version historique, l’autre qui rassemble les faits sous le titre courant. Expliquez pourquoi les résultats diffèrent. Vérifiez qu’une seule version de dimension est courante et que les périodes ne se chevauchent pas.

## 13. Exercices corrigés

### Exercice 1 — Grain ambigu

Une table contient une ligne par inscription, et une autre une ligne par tentative. Le rapport joint les deux puis compte les inscriptions. Quelle erreur peut se produire?

**Correction.** Une inscription liée à plusieurs tentatives apparaît plusieurs fois après la jointure. COUNT(*) comptera ces répétitions et surestimera les inscriptions. Il faut définir le grain du rapport, compter une clé distincte ou pré-agréger les tentatives au grain de l’inscription avant la jointure. Le choix doit correspondre à la mesure recherchée et être testé avec une inscription ayant plusieurs tentatives.

### Exercice 2 — Changement de titre

Le titre d’un cours est corrigé pour une faute de frappe. Faut-il une dimension Type 2?

**Correction.** Pas nécessairement. Si l’objectif est de corriger l’historique sans conserver la faute, une mise à jour Type 1 peut convenir. Si le changement représente une évolution métier que les rapports historiques doivent distinguer, Type 2 est plus approprié. La décision dépend de la sémantique, pas du simple fait que la valeur a changé.

### Exercice 3 — Pipeline relancé

Un job charge des faits puis échoue avant de mettre à jour son curseur. À la reprise, les mêmes événements sont relus.

**Correction.** Le chargement doit être idempotent. Utilisez un identifiant d’événement ou une clé stable, une contrainte, un UPSERT ou une table de staging et une étape de publication contrôlée. Le curseur doit avancer uniquement lorsque les données sont durables et validées. Les doublons doivent être détectés et la reprise testée par une panne simulée.

### Exercice 4 — Source et cible divergent

Le nombre de lignes source est supérieur à celui de la cible. Peut-on conclure que le chargement est incorrect?

**Correction.** Pas sans connaître la frontière du lot, les filtres, les suppressions, les rejets et les délais de fraîcheur. Comparez le même périmètre logique, la même période et la même version de source. Analysez les lignes rejetées et les clés non résolues. Si le pipeline est incomplet, ne publiez pas l’état comme complet sans un indicateur de fraîcheur.

### Exercice 5 — Le taux moyen

Un rapport calcule la moyenne des taux de réussite mensuels pour obtenir le taux annuel.

**Correction.** Une moyenne non pondérée des taux mensuels peut être fausse si le nombre de tentatives diffère par mois. Le taux annuel doit être recalculé en additionnant les tentatives réussies puis en divisant par le nombre total de tentatives selon la définition convenue. Une mesure de taux ne doit pas être traitée comme une mesure additive.

## 14. Défi final : chaîne analytique de progression

Construisez une proposition de chaîne qui alimente chaque matin un tableau de bord de taux de réussite par cours et par mois. Les sources contiennent des tentatives, des cours et des inscriptions. Le titre de cours peut changer, des doublons peuvent arriver après une reprise, et un lot doit être rejouable. Le rapport doit distinguer les tentatives terminées et les apprenants uniques.

### Correction attendue

1. **Contrat des sources.** Définir l’identifiant stable d’une tentative, les champs requis, la sémantique du statut terminé, la définition du score et le fuseau de date qui détermine le mois. Documenter les suppressions, mises à jour et délais attendus.

2. **Zone brute.** Charger une copie identifiable des données par lot et source. Garder les données originales sous une politique de sécurité et de rétention. Enregistrer le point de reprise pour éviter de perdre les modifications.

3. **Nettoyage.** Normaliser les types et timestamps, détecter les identifiants manquants, isoler les doublons et vérifier que les tentatives référencent des cours valides. Ne supprimez pas silencieusement les lignes invalides; comptez-les et expliquez leur traitement.

4. **Dimensions.** Maintenir une dimension cours avec une politique explicite de changement historique, une dimension date et les clés nécessaires. Résoudre chaque tentative vers la bonne version de dimension selon la règle historique définie.

5. **Faits.** Utiliser un grain d’une ligne par tentative terminée. Dédupliquer par identifiant de source, conserver le numéro de lot, le score et les clés de dimension. Le nombre de tentatives, le nombre d’apprenants uniques et le taux sont calculés séparément.

6. **Publication.** Calculer le numérateur et le dénominateur de la période, puis construire le taux. N’afficher que le dernier lot validé, avec un timestamp de fraîcheur. Si un contrôle de qualité critique échoue, conserver la version précédente ou publier un état explicitement incomplet.

7. **Reprise et tests.** Relancer le même lot deux fois et vérifier qu’il ne double pas les faits. Injecter une référence inconnue, un doublon et une modification tardive. Mesurer les lignes lues, rejetées et chargées, puis documenter les résultats.

## 15. Contrats de données et évolution de schéma

Un contrat de données explicite ce que le producteur garantit à ses consommateurs : nom et signification des champs, types, valeurs autorisées, clé d’unicité, règles de nullabilité, sémantique temporelle, fréquence de mise à jour et procédure de changement. Sans contrat, une application peut renommer une colonne ou modifier un statut sans comprendre qu’un tableau de bord historique en dépend. Le contrat transforme une hypothèse implicite en dépendance visible.

Un changement de schéma peut être additif ou incompatible. Ajouter un champ nullable avec une signification documentée est souvent plus simple qu’en retirer un utilisé par plusieurs modèles. Renommer une valeur de statut peut être incompatible même si le type ne change pas. Il faut examiner les consommateurs, versionner les modèles, ajouter les nouveaux attributs de manière compatible, migrer les transformations, comparer les résultats, puis retirer l’ancien champ après une période clairement définie.

Lorsqu’une source envoie des événements, la version de schéma devrait être connue ou inférable de manière fiable. Si le producteur et le consommateur évoluent à des moments différents, il faut gérer la coexistence de versions. Le consommateur peut accepter plusieurs variantes temporaires, mais cette compatibilité doit être testée et bornée dans le temps pour éviter une collection de branches historiques impossibles à maintenir.

Les règles de qualité font partie du contrat. Si score doit être un nombre compris entre zéro et cent, le consommateur doit distinguer un score hors plage d’une absence de score. Si un événement terminé nécessite une date de fin, les lignes qui ne possèdent pas cette date doivent être mises en attente, rejetées ou traitées selon une règle précise. Convertir tous les scores invalides en zéro crée un résultat apparemment complet mais faux.

## 16. Définir des indicateurs interprétables

Un indicateur analytique doit être défini avec un nom, une formule, un grain, un filtre, un fuseau de référence, une source et un propriétaire. Le taux de réussite peut se définir comme le nombre de tentatives terminées avec réussite divisé par le nombre de tentatives terminées éligibles. Il faut décider si les tentatives annulées sont exclues, si les tests pratiques sont comptés comme des examens, et si le même apprenant peut contribuer plusieurs fois.

Le nombre d’apprenants actifs peut signifier au moins une connexion pendant une période, au moins une leçon terminée ou une action qualifiée dans un système. Des définitions différentes peuvent produire des nombres différents, tous valides pour leur contexte. L’entrepôt doit documenter ces définitions et éviter que chaque rapport calcule sa propre version. Un dictionnaire d’indicateurs est aussi important qu’un dictionnaire de tables.

La validation d’un indicateur nécessite un petit ensemble de données dont le résultat attendu peut être calculé à la main. Incluez un utilisateur avec plusieurs tentatives, un cours sans activité, un score manquant, une tentative en cours et un changement de titre. Le test sert à vérifier que la formule respecte le métier et ne change pas accidentellement quand l’implémentation évolue.

Un indicateur n’est pas interprétable si sa fraîcheur ou son taux de complétude est inconnu. Affichez la période couverte, la date de mise à jour et les éventuelles limitations. En cas de retard d’ingestion, il faut éviter que les utilisateurs comparent une journée incomplète à des journées terminées sans signaler l’écart. La qualité de présentation fait partie de la qualité des données.

## 17. Checklist et synthèse

Le modèle analytique devient fiable lorsque chaque table possède un grain explicite, chaque mesure une définition et chaque transformation un contrat. L’architecture doit tracer les données depuis la source jusqu’au rapport, gérer les mises à jour et les suppressions, permettre les reprises, tester la qualité et indiquer la fraîcheur des indicateurs. Les clés, les dates et les valeurs historiques doivent avoir une sémantique claire.

Un entrepôt n’est pas simplement une copie de la base transactionnelle. Il organise les données autour des usages analytiques, stabilise les définitions et permet de comparer des périodes. ETL et ELT sont des choix de placement des transformations; le plus important est la reproductibilité, l’idempotence, les contrôles, la sécurité et la capacité d’expliquer le résultat publié.

Avant de déclarer une chaîne prête, vérifiez que le chargement initial a un point de cohérence, que l’incrémental détecte aussi les suppressions, que les reprises ne dupliquent pas les faits, que le schéma de dimension conserve l’histoire prévue, que les données invalides sont observables, que les indicateurs ont une définition documentée et que les lots incomplets ne remplacent pas un état publié sain. Identifiez les propriétaires de la source, de la transformation, du modèle et du rapport. Une chaîne sans propriétaire aura tendance à accumuler des règles inexpliquées et des écarts difficiles à corriger.

## Ressources pour approfondir

- PostgreSQL, fonctions d’agrégat : https://www.postgresql.org/docs/current/functions-aggregate.html
- PostgreSQL, requêtes avec WITH : https://www.postgresql.org/docs/current/queries-with.html
- Microsoft Learn, architecture de données : https://learn.microsoft.com/en-us/azure/architecture/data-guide/
- Google Cloud, architecture de données : https://cloud.google.com/architecture
- Apache Airflow, concepts d’orchestration : https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/

Les termes ETL, ELT, CDC, dimension Type 2 et grain sont utiles, mais ne remplacent pas une définition métier spécifique. La chaîne doit être évaluée sur ses données et les indicateurs que les utilisateurs consomment réellement.
