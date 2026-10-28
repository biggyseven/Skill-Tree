
# Entrepôt de données et ETL — Intermédiaire

## Mise en contexte : transformer des données de production en décisions fiables

Une application métier enregistre des commandes, des inscriptions, des paiements, des connexions et des changements de statut. Ces données sont indispensables à son fonctionnement quotidien, mais elles ne répondent pas toujours directement aux questions des responsables : quels cours améliorent le plus la réussite des apprenants ? Quel canal d'acquisition produit des inscriptions qui aboutissent réellement à une certification ? Comment l'activité a-t-elle évolué au cours des douze derniers mois ? Dans quelle région se trouvait un client au moment d'un achat, même s'il a déménagé depuis ?

Interroger directement les bases transactionnelles pour répondre à toutes ces questions peut être risqué. Les requêtes analytiques parcourent parfois de grandes périodes, rapprochent plusieurs domaines et calculent des agrégats coûteux. Elles entrent alors en concurrence avec les écritures qui font fonctionner le service. De plus, les systèmes sources ont souvent été conçus pour les besoins des applications opérationnelles : une structure efficace pour enregistrer une commande n'est pas nécessairement la structure la plus compréhensible pour analyser plusieurs années de ventes.

Un entrepôt de données, ou data warehouse, organise les données issues de plusieurs sources pour permettre l'analyse historique, la production d'indicateurs et l'exploration de tendances. Les pipelines ETL et ELT extraient, transforment et chargent ces données. Ces mots décrivent une démarche, pas simplement un outil : il faut comprendre d'où viennent les données, quelles transformations elles subissent, quelles règles assurent leur qualité et comment prouver qu'un lot a été traité correctement.

Dans ce cours, nous utiliserons un exemple fictif, SkillMarket, plateforme de formation disposant d'une base applicative, d'un outil de paiement et d'une solution de suivi d'apprentissage. Nous construirons un entrepôt qui permet de mesurer les ventes, les inscriptions, la progression et les certifications. Le point central sera la traçabilité : un tableau de bord fiable doit pouvoir expliquer comment ses chiffres ont été produits.

## 1. Objectifs et prérequis

À l'issue du cours, vous devrez savoir distinguer OLTP et OLAP, définir le grain d'une table de faits, reconnaître faits et dimensions, concevoir un schéma en étoile, comprendre les clés de substitution et les dimensions à évolution lente, comparer ETL et ELT, concevoir des chargements initiaux et incrémentaux, expliquer CDC et watermark, rendre un pipeline relançable, traiter doublons et événements tardifs, écrire des contrôles de qualité, orchestrer les dépendances, mesurer fraîcheur et volumes, et décrire une reprise après échec.

Le cours suppose la maîtrise des requêtes SQL de base, des jointures, des agrégations, des index et des concepts de transaction. Une première connaissance de la modélisation relationnelle et des sauvegardes est utile. Vous n'avez pas besoin d'avoir déjà exploité un entrepôt en production ; les exemples vont du schéma conceptuel jusqu'au runbook d'exploitation.

## 2. OLTP, OLAP et rôle d'un entrepôt

### 2.1 Deux usages différents

OLTP signifie Online Transaction Processing. Il s'agit des traitements opérationnels : créer une inscription, enregistrer un paiement, modifier un profil ou confirmer une livraison. Ces opérations sont souvent courtes, fréquentes et ciblées, et doivent respecter les contraintes du domaine.

OLAP signifie Online Analytical Processing. Il s'agit de travaux d'analyse : agréger les inscriptions par mois, comparer le taux d'achèvement par catégorie, étudier les revenus par zone ou mesurer la rétention d'un cohort. Les requêtes analytiques lisent souvent de grands volumes, regroupent les données et croisent plusieurs perspectives.

~~~mermaid
flowchart LR
    A["Applications OLTP"] --> B["Extraction / réplication des changements"]
    B --> C["Zone de préparation"]
    C --> D["Nettoyage et transformations"]
    D --> E["Entrepôt analytique"]
    E --> F["Datamarts / modèle sémantique"]
    F --> G["Tableaux de bord et analystes"]
    A -. "charge analytique évitée" .-> G
~~~

La séparation ne signifie pas qu'une base opérationnelle ne peut jamais produire un rapport ni qu'un entrepôt ne peut pas être interrogé en SQL. La distinction porte sur les objectifs de conception, la charge, la granularité, la rétention et les garanties. L'entrepôt peut recevoir des données périodiquement, via CDC, ou avec une combinaison des deux. Il faut choisir une architecture proportionnée au délai métier attendu.

### 2.2 Pourquoi ne pas simplement joindre directement toutes les sources ?

Les sources peuvent être réparties entre plusieurs bases, API ou fichiers. Elles emploient parfois des identifiants différents et peuvent définir différemment des termes tels que « client actif », « revenu » ou « cours terminé ». Une extraction vers une zone commune permet de résoudre les différences, de contrôler les types et de conserver un historique de traitement.

Le reporting direct peut être pertinent pour un besoin limité, un petit volume ou un outil de consultation simple. Il devient problématique lorsque chaque rapport réimplémente ses propres règles, que les requêtes lourdes ralentissent les applications ou que l'historique a disparu de la source opérationnelle. Un entrepôt n'est pas une solution automatique : il ajoute de l'infrastructure, des transformations, des coûts de calcul et une obligation d'expliquer la provenance des indicateurs.

### 2.3 Les couches logiques d'une plateforme analytique

- **Source opérationnelle** : système où les événements métier sont produits.
- **Zone d'atterrissage ou staging** : copie des données reçues, souvent proche de leur format source.
- **Entrepôt intégré** : modèle nettoyé, historisé et cohérent entre les domaines.
- **Datamart** : sous-ensemble organisé pour une fonction analytique, comme ventes ou formation.
- **Modèle sémantique** : couche qui expose des noms, définitions et métriques compréhensibles pour les utilisateurs.
- **Orchestration** : mécanisme qui déclenche les tâches, exprime leurs dépendances et gère leur état.

Ces couches peuvent être logiques plutôt que physiques. Une petite équipe peut utiliser quelques schémas dans une seule base, tandis qu'une organisation plus grande peut employer un stockage objet, un moteur distribué et un entrepôt cloud. L'architecture doit garder les responsabilités intelligibles, même si elle ne multiplie pas les composants.

## 3. ETL et ELT

### 3.1 ETL : extraire, transformer puis charger

Dans une architecture ETL classique, la donnée est extraite des sources, transformée dans un processus intermédiaire, puis chargée dans la cible. La transformation peut inclure le nettoyage, le rapprochement des référentiels, la conversion des unités, le masquage de données, la déduplication et la création d'indicateurs dérivés.

~~~mermaid
flowchart LR
    S["Sources"] --> E["Extract"]
    E --> T["Transform"]
    T --> L["Load"]
    L --> W["Entrepôt prêt pour analyse"]
~~~

L'ETL convient notamment lorsque les données doivent être filtrées, masquées ou transformées avant d'entrer dans la cible. Il peut aussi être choisi pour utiliser des ressources de calcul spécifiques ou garantir une structure précise avant le chargement. Son coût est que le moteur de transformation intermédiaire devient une partie importante de l'architecture.

### 3.2 ELT : extraire, charger puis transformer

En ELT, les données brutes ou légèrement préparées sont chargées dans la plateforme cible, puis transformées avec ses propres capacités de calcul, souvent en SQL. Cette approche exploite la puissance du moteur analytique et peut faciliter la traçabilité entre la donnée reçue et les modèles produits. Elle ne signifie pas qu'il faut charger sans contrôle toute donnée sensible : le filtrage à la source et la protection des données restent nécessaires.

~~~mermaid
flowchart LR
    S["Sources"] --> E["Extract"]
    E --> L["Load en zone brute"]
    L --> T["Transformations dans la plateforme"]
    T --> W["Modèles analytiques"]
~~~

ETL et ELT ne sont pas des philosophies mutuellement exclusives. Dans un même système, on peut masquer des champs avant la zone de stockage, charger ensuite une copie brute gouvernée, puis effectuer les transformations dimensionnelles dans le moteur SQL. Le choix doit prendre en compte les coûts de calcul, la capacité de la cible, la sécurité, la gouvernance, les besoins de reprise et les compétences disponibles.

### 3.3 Extraction par lot ou capture des changements

Une extraction par lot lit des données à un horaire déterminé : toutes les nuits, toutes les heures, ou à une autre fréquence. Le chargement incrémental utilise un critère pour ne récupérer que les lignes ou événements nouveaux ou modifiés. Le Change Data Capture, ou CDC, capture les changements observés par un mécanisme dédié, souvent lié au journal de transactions ou à un flux d'événements de la source.

Un chargement incrémental fondé sur un champ de modification peut être simple, mais il exige une convention fiable. Si un système ne renseigne pas sa date de modification lors de chaque changement, des données seront omises. Si les horloges sont incohérentes, la fenêtre peut être mal calculée. Un CDC peut fournir une séquence plus fine, mais augmente les exigences de configuration, de suivi des offsets, de gestion des suppressions et d'exploitation.

## 4. Concevoir un schéma dimensionnel

### 4.1 Commencer par les questions métier

Le modèle dimensionnel cherche à rendre les analyses compréhensibles. Une table de faits conserve des événements ou mesures à un grain défini. Les dimensions apportent le contexte descriptif permettant d'agréger les faits : date, cours, apprenant, canal, région, offre ou statut.

Pour SkillMarket, imaginons que la direction souhaite répondre à ces questions : combien d'inscriptions ont été créées par mois et par catégorie de cours ? Quel revenu net a été attribué à chaque canal ? Quel pourcentage des inscriptions aboutit à une certification dans les trente jours ? Le modèle doit être construit à partir de questions de ce type, pas à partir d'une traduction mécanique de toutes les tables opérationnelles.

### 4.2 Le grain : la décision la plus importante

Le grain précise ce qu'une ligne de la table de faits représente. Par exemple : « une ligne par inscription créée » ou « une ligne par événement de paiement ». Ce choix fixe le sens des mesures et les clés nécessaires. Mélanger plusieurs grains dans une seule table peut provoquer des doubles comptages et rendre les indicateurs impossibles à interpréter.

Avant de créer la table, écrivez la phrase qui définit chaque ligne. Ensuite, identifiez les dimensions applicables à ce grain et les mesures numériques disponibles. Si l'on mélange l'inscription et les paiements, une inscription payée en trois fois peut produire trois lignes ; compter les inscriptions par nombre de lignes donnerait alors un résultat faux sans déduplication explicite.

~~~mermaid
flowchart TD
    A["Question métier"] --> B["Définir le grain"]
    B --> C["Lister les dimensions"]
    C --> D["Identifier les mesures"]
    D --> E["Définir les clés et contraintes"]
    E --> F["Écrire les requêtes cibles"]
    F --> G["Valider avec les utilisateurs"]
~~~

### 4.3 Faits, dimensions et mesures

Une table de faits d'inscription peut enregistrer le nombre d'inscriptions, les montants facturés et les durées calculées au moment d'une analyse. Une dimension Cours peut décrire le titre, la catégorie et le niveau. Une dimension Date apporte jour, semaine, mois, trimestre et année. Une dimension Canal peut contenir la source d'acquisition.

Les mesures ne sont pas toutes additives. Le nombre d'inscriptions et les montants peuvent être additionnés sur plusieurs dimensions si les règles métier sont correctes. Un taux ou un pourcentage doit généralement être recalculé à partir de son numérateur et de son dénominateur, plutôt que d'être additionné. Un solde de fin de mois, lui, ne s'additionne pas nécessairement sur les jours. Le modèle doit signaler ces différences pour éviter des tableaux de bord trompeurs.

### 4.4 Schéma en étoile

~~~mermaid
erDiagram
    DIM_DATE ||--o{ FACT_INSCRIPTION : date_creation
    DIM_COURSE ||--o{ FACT_INSCRIPTION : cours
    DIM_LEARNER ||--o{ FACT_INSCRIPTION : apprenant
    DIM_CHANNEL ||--o{ FACT_INSCRIPTION : acquisition
    DIM_STATUS ||--o{ FACT_INSCRIPTION : statut
    DIM_DATE {
        int date_key
        date calendar_date
        int month_number
        int year_number
    }
    DIM_COURSE {
        int course_key
        string course_id
        string title
        string category
        string level
    }
    FACT_INSCRIPTION {
        int date_key
        int course_key
        int learner_key
        int channel_key
        int status_key
        int inscription_count
        decimal amount
    }
~~~

Le schéma en étoile place la table de faits au centre et les dimensions autour. Il peut rendre les requêtes analytiques plus lisibles et favoriser les outils de BI. Il ne s'agit pas de répéter toutes les colonnes du système opérationnel : le but est d'exposer les attributs et mesures requis pour analyser le métier.

Un schéma en flocon normalise davantage certaines dimensions en sous-tables. Il peut réduire la duplication, mais ajoute des jointures et peut être plus complexe pour les utilisateurs. Une étoile est souvent un bon point de départ, sans être une règle immuable. Les performances dépendent du moteur analytique, des volumes et des requêtes.

### 4.5 Dimensions conformes

Si le département ventes et le département formation utilisent des définitions différentes d'un apprenant ou d'un cours, leurs indicateurs ne pourront pas être comparés facilement. Une dimension conforme fournit une définition partagée entre plusieurs tables de faits ou datamarts. Il faut convenir de la sémantique des attributs, de l'identifiant métier et des règles de dédoublonnage.

Une dimension commune ne signifie pas que chaque équipe doit voir toutes les données. La gouvernance et la sécurité déterminent les attributs exposés. Les identifiants de rapprochement peuvent être conservés dans une couche contrôlée, tandis que le modèle analytique destiné aux utilisateurs utilise des clés techniques et des catégories autorisées.

## 5. Clés naturelles, clés de substitution et intégration

Les systèmes sources ont leurs propres identifiants : numéro client dans une application, identifiant utilisateur dans une autre, identifiant du fournisseur tiers dans une API. Une clé naturelle représente une entité du domaine, tandis qu'une clé de substitution est une clé technique attribuée dans le modèle analytique. La clé technique protège l'entrepôt contre certaines modifications des systèmes sources et permet de distinguer les différentes versions historiques d'une même entité métier.

Exemple : un apprenant a pour identifiant source `learner-42`. La dimension d'apprenant attribue la clé de substitution `learner_key = 1058`. La table de faits référence 1058, et la clé naturelle permet au processus de chargement de retrouver l'entité. Si l'apprenant change de région et que cette dimension conserve l'historique, une nouvelle version reçoit une nouvelle clé de substitution.

Un rapprochement entre sources doit également traiter les cas où deux identifiants représentent le même acteur, ou où un acteur n'a pas encore été décrit dans la dimension. Une ligne inconnue à clé de substitution réservée peut permettre de charger un fait sans perdre sa trace, à condition de signaler l'anomalie et de corriger le rapprochement ensuite. L'usage de cette ligne ne doit pas masquer une grande proportion de références manquantes.

## 6. Gestion des changements : dimensions à évolution lente

Les Slowly Changing Dimensions, ou SCD, traitent les changements d'attributs descriptifs au cours du temps. La méthode dépend de la question analytique. Si l'on veut seulement disposer du nom actuel corrigé, l'écrasement peut suffire. Si l'on veut savoir dans quelle région un apprenant se trouvait lorsqu'il a acheté une formation, il faut conserver l'historique.

### 6.1 Type 1 : écraser la valeur

Le type 1 met à jour la ligne existante, sans conserver l'ancienne valeur dans la dimension. Il convient aux corrections de fautes ou aux attributs pour lesquels l'historique n'a aucun intérêt analytique. Son avantage est la simplicité ; sa limite est que les rapports historiques reflètent alors le nouvel attribut.

### 6.2 Type 2 : créer une version

Le type 2 clôt l'ancienne version et insère une nouvelle ligne avec une clé de substitution distincte, une date de début de validité, une date de fin et un indicateur de ligne courante. Les faits historiques conservent la clé de la version qui était valide au moment du fait, ce qui permet de restituer le contexte temporel.

~~~mermaid
flowchart LR
    A["Apprenant : Région Nord"] --> B["Version 1 valide jusqu'au 31/03"]
    B --> C["Changement de région"]
    C --> D["Version 2 : Région Centre depuis le 01/04"]
    D --> E["Nouveaux faits pointent vers version 2"]
    B --> F["Faits historiques gardent version 1"]
~~~

Une structure illustrative peut contenir `learner_key`, `learner_id`, `region`, `valid_from`, `valid_to` et `is_current`. Une convention de validité doit être définie, par exemple intervalles semi-ouverts : la date de début est incluse et la date de fin exclue. Cette règle évite qu'une date de transition appartienne à deux versions. L'entrepôt doit empêcher plusieurs versions courantes pour la même clé naturelle, sauf si le modèle métier le permet explicitement.

### 6.3 Type 3 et stratégies hybrides

Le type 3 conserve un historique limité, souvent la valeur actuelle et une valeur précédente. Il est moins général et ne remplace pas une histoire complète lorsque le nombre de changements peut être important. Des modèles peuvent combiner des stratégies : type 1 pour corriger un libellé erroné, type 2 pour les changements de région influençant les analyses. Les règles doivent être décidées par attribut, et non seulement par table.

## 7. Conception SQL illustrative

Les exemples suivants utilisent une syntaxe proche de PostgreSQL. Les types précis et les fonctions de génération de clés peuvent varier selon le SGBD.

~~~sql
CREATE TABLE dim_course (
    course_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id VARCHAR(100) NOT NULL,
    title VARCHAR(300) NOT NULL,
    category VARCHAR(100),
    level VARCHAR(30),
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE UNIQUE INDEX uq_dim_course_current
ON dim_course(course_id)
WHERE is_current = TRUE;

CREATE TABLE fact_enrollment (
    enrollment_id VARCHAR(100) NOT NULL,
    enrollment_date_key INTEGER NOT NULL,
    course_key BIGINT NOT NULL REFERENCES dim_course(course_key),
    learner_key BIGINT NOT NULL,
    channel_key INTEGER NOT NULL,
    enrollment_count INTEGER NOT NULL DEFAULT 1,
    paid_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    source_updated_at TIMESTAMP,
    batch_id VARCHAR(100) NOT NULL,
    PRIMARY KEY (enrollment_id, batch_id)
);
~~~

La table de dimension utilise une clé technique générée et un identifiant métier provenant de la source. L'index partiel vise à garantir une seule version courante par cours dans PostgreSQL. Cette DDL doit être adaptée aux règles exactes du projet ; la clé primaire de faits illustrée par enrollment_id et batch_id sert d'exemple d'audit de chargement, mais une production doit choisir une stratégie d'identité métier et de déduplication explicitement vérifiée.

Un entrepôt peut retenir un fait par inscription, ou au contraire un fait par événement métier comme un paiement. Si la facturation peut comporter plusieurs tentatives, remboursements et paiements partiels, la table de paiements doit utiliser son propre grain. Ne dupliquez pas les montants de paiement dans chaque ligne d'inscription sans un schéma qui garantit le sens des sommes.

## 8. De l'extraction à une zone de staging fiable

La zone de staging reçoit la donnée dans un format proche de la source, en gardant suffisamment de métadonnées pour retracer son origine. Il est utile d'enregistrer le nom logique de la source, la date d'extraction, l'identifiant du lot, la version du schéma, la date de modification source et un identifiant d'événement ou de fichier. Ces attributs permettent de comprendre si une donnée est ancienne, répétée ou issue d'un nouveau format.

Un chargement robuste ne se résume pas à lancer un SELECT puis un INSERT. Il doit gérer les données incomplètes, les conversions impossibles, les changements de schéma, les doublons, la coupure réseau, les fichiers partiels et les reprises. Une zone de staging peut être temporaire avec rétention courte, ou persistante pour permettre le rejeu et l'audit. Le choix dépend du volume et des obligations.

~~~mermaid
flowchart TD
    S["Sources : SQL, API, fichiers"] --> L["Zone d'atterrissage"]
    L --> V["Validation structurelle"]
    V -->|valide| C["Nettoyage et standardisation"]
    V -->|invalide| Q["Quarantaine + raison"]
    C --> D["Déduplication et rapprochement"]
    D --> T["Tables de dimensions"]
    T --> F["Tables de faits"]
    F --> R["Contrôles de réconciliation"]
    R --> P["Publication du lot"]
~~~

La quarantaine évite qu'une ligne invalide interrompe nécessairement toute la chaîne, mais elle exige une politique claire. Certaines erreurs sont bloquantes parce qu'elles invalident un total financier ; d'autres peuvent être mises à l'écart si les règles métier acceptent un résultat partiel visible avec une alerte. Il ne faut jamais cacher silencieusement les erreurs en éliminant des lignes.

## 9. Chargement complet, incrémental, watermark et CDC

### 9.1 Chargement complet

Un chargement complet relit un ensemble entier puis remplace ou reconstruit la cible. Il peut être raisonnable pour de petites dimensions, des référentiels stables ou des tables de taille modeste. Sur de gros volumes, il augmente la durée, le coût réseau et la charge des sources. Le processus doit aussi choisir comment publier le résultat : remplacer une table en une étape, charger une table temporaire puis basculer, ou utiliser une transaction et des mécanismes adaptés au moteur.

### 9.2 Incrément basé sur un watermark

Un watermark peut être un timestamp updated_at, une séquence croissante ou une position d'événement. Le pipeline mémorise la dernière frontière traitée et charge les changements au-delà de cette frontière. Une stratégie robuste prend une borne supérieure au début du lot, traite jusqu'à cette borne, valide le lot, puis avance le watermark seulement après la réussite complète.

~~~mermaid
sequenceDiagram
    participant O as Orchestrateur
    participant S as Source
    participant W as Entrepôt
    O->>S: Lire borne haute H
    O->>S: Extraire watermark précédent < timestamp <= H
    S-->>O: Lignes du lot
    O->>W: Charger staging
    O->>W: Transformer et contrôler
    alt Lot valide et publié
        O->>W: Enregistrer H comme nouveau watermark
    else Échec
        O->>W: Conserver l'ancien watermark
    end
~~~

La règle d'intervalle doit être stable, par exemple strictement supérieur à l'ancien watermark et inférieur ou égal à la borne haute. Si plusieurs lignes ont exactement le même timestamp, un watermark composé avec un identifiant stable ou un chevauchement suivi d'une déduplication peut être nécessaire. Une fenêtre de recouvrement permet de récupérer des modifications arrivées tardivement si la source autorise des mises à jour rétroactives, mais elle ne doit pas être confondue avec une garantie parfaite. Le choix dépend du contrat de la source.

### 9.3 Le problème des suppressions

Une requête fondée sur updated_at ne détecte pas nécessairement les lignes supprimées, car la ligne n'existe plus dans la source. Il faut alors un marqueur de suppression, un journal CDC, un tombstone, une comparaison de snapshots ou une autre convention explicite. Les suppressions logiques peuvent être plus simples à charger, mais leur signification doit être partagée entre producteur et consommateur.

### 9.4 CDC et positions de journal

Le CDC transmet les changements d'une source sous forme d'événements : insertion, mise à jour, suppression, avec des métadonnées de position ou de transaction selon le système. Il permet une latence plus faible qu'un batch périodique et peut mieux représenter les suppressions. Il exige cependant le suivi des offsets, la gestion des changements de schéma, la rétention des journaux sources et les règles de reprise après interruption.

Un événement CDC peut être reçu plusieurs fois, notamment lors d'une reprise. Le consommateur doit être idempotent ou disposer d'une déduplication fiable. Il faut aussi comprendre le contrat d'ordre des événements : l'ordre global entre partitions ou sources différentes peut ne pas être garanti. Le consommateur doit appliquer un événement dans le contexte de sa clé et de sa version, au lieu de supposer que tous les événements du domaine arrivent dans un ordre total.

## 10. Idempotence, déduplication et transactions de chargement

Un pipeline est idempotent lorsqu'une relance pour les mêmes données et la même période ne crée pas de doublons ni de résultats différents non attendus. Cette propriété est fondamentale parce que les échecs peuvent se produire après une insertion mais avant que l'orchestrateur reçoive la confirmation. Le système ne sait alors pas toujours si l'étape a été exécutée ; réessayer doit être sans danger.

Les moyens d'obtenir l'idempotence incluent une clé métier stable, des contraintes d'unicité, un MERGE ou upsert, un identifiant de lot, une table de contrôle des lots, une partition reconstruite de manière déterministe et un traitement des événements déjà appliqués. La méthode appropriée dépend du SGBD et du type de données. Un MERGE doit être analysé attentivement : plusieurs lignes source qui correspondent à la même ligne cible peuvent rendre l'opération ambiguë ou provoquer une erreur selon le moteur.

~~~mermaid
flowchart TD
    A["Début du lot batch-2026-10-28"] --> B["Vérifier le registre de lots"]
    B --> C{"Lot déjà publié ?"}
    C -->|Oui| D["Terminer sans réinsérer"]
    C -->|Non| E["Charger staging avec batch_id"]
    E --> F["Dédupliquer selon la clé métier"]
    F --> G["Appliquer dimensions et faits"]
    G --> H["Contrôles de qualité"]
    H --> I{"Contrôles valides ?"}
    I -->|Oui| J["Publier et marquer réussi"]
    I -->|Non| K["Mettre en quarantaine / échec"]
~~~

Le registre de lots doit contenir un identifiant de lot, le périmètre traité, les bornes ou offsets, l'heure de début et de fin, le nombre de lignes, les erreurs et l'état final. Les identifiants de lot permettent de retrouver l'origine d'un résultat et facilitent les réparations. Le registre ne remplace pas les contraintes de données, mais il rend le processus explicable.

Un lot ne doit pas marquer son watermark comme réussi avant d'avoir rendu la cible cohérente. Si les tables de faits et les métadonnées de contrôle sont mises à jour en plusieurs étapes, l'orchestrateur doit savoir quelle étape peut être relancée indépendamment. Selon le moteur, une transaction peut regrouper les opérations ; sinon, une stratégie de table de travail et de publication atomique ou une logique de compensation peut s'avérer nécessaire.

## 11. Qualité des données : contrôles avant de publier

La qualité n'est pas une étape décorative. Un pipeline peut s'exécuter sans erreur technique et produire de mauvais indicateurs : doublons, montants négatifs inattendus, dates décalées, dimensions orphelines, lignes manquantes ou règles métier contradictoires. Il faut traduire les exigences en contrôles automatisés et décider ce qui bloque le lot.

### 11.1 Dimensions de qualité utiles

- **Complétude** : les champs requis sont-ils présents ?
- **Validité** : les valeurs respectent-elles leur type et leur domaine ?
- **Unicité** : une entité ou un événement apparaît-il plus d'une fois ?
- **Cohérence** : les relations et les règles métier sont-elles respectées ?
- **Exactitude** : les données reflètent-elles la réalité de la source ?
- **Fraîcheur** : le pipeline a-t-il chargé les données dans le délai prévu ?
- **Unicité de sémantique** : le même indicateur signifie-t-il la même chose entre rapports ?

Ces dimensions se recoupent sans être équivalentes. Une adresse peut être valide au regard du format et pourtant erronée. Une donnée peut être exacte à l'extraction mais obsolète au moment du tableau de bord. Un contrôle automatisé peut détecter certaines anomalies, mais pas définir seul la vérité métier.

### 11.2 Réconciliation des volumes et montants

Après extraction, comparez les nombres de lignes lus, rejetés, dédupliqués et chargés. Pour un domaine financier, rapprochez aussi les montants totaux, le nombre de transactions, les remboursements et les monnaies. Un total identique n'est pas une preuve suffisante : une valeur manquante et un doublon de même montant peuvent se compenser. Les contrôles doivent donc inclure la granularité et la répartition, pas seulement un total général.

~~~sql
SELECT
    batch_id,
    COUNT(*) AS row_count,
    COUNT(DISTINCT enrollment_id) AS unique_enrollments,
    SUM(paid_amount) AS total_paid,
    SUM(CASE WHEN paid_amount < 0 THEN 1 ELSE 0 END) AS negative_amount_rows
FROM staging_enrollments
GROUP BY batch_id;
~~~

Cette requête illustre des indicateurs de contrôle. Elle doit être adaptée au fait que les remboursements peuvent légitimement être négatifs dans certains modèles : la règle ne doit pas rejeter une valeur simplement parce qu'elle paraît inhabituelle. Toute anomalie nécessite une définition métier et une décision documentée.

### 11.3 Contrôles de relations

Une table de faits qui référence une dimension absente peut être rejetée, mise en attente ou associée à un membre inconnu selon la politique de l'organisation. Il est dangereux de supprimer silencieusement les faits orphelins : le rapport présentera alors une baisse artificielle. Un contrôle de références peut identifier les anomalies avant la publication.

~~~sql
SELECT f.course_id, COUNT(*) AS orphan_facts
FROM staging_fact_enrollment AS f
LEFT JOIN dim_course AS d
  ON d.course_id = f.course_id AND d.is_current = TRUE
WHERE d.course_key IS NULL
GROUP BY f.course_id;
~~~

Dans un modèle SCD de type 2, la résolution de clé ne peut pas simplement joindre la version courante à tous les faits historiques. Il faut rechercher la version valide à la date métier du fait, selon les intervalles de validité convenus. La jointure temporelle doit être testée avec les dates exactes de transition, les valeurs tardives et les cas où la dimension est arrivée après le fait.

### 11.4 Quarantaine et contrat de données

Un contrat de données décrit le schéma attendu, les propriétaires, les règles de compatibilité, la fréquence, la fraîcheur attendue et le traitement des changements. Il peut être exprimé comme documentation, tests exécutables, schéma versionné ou ensemble de validations. Il est utile lorsque les équipes productrices et consommatrices ne sont pas les mêmes.

La quarantaine conserve les enregistrements qui n'ont pas passé des contrôles, avec la raison, la source et l'identifiant de lot. Une bonne quarantaine permet de réparer puis rejouer les lignes ; elle ne doit pas devenir une décharge sans propriétaire. Définissez un délai de résolution, un responsable, des alertes sur les volumes et une procédure de suppression sécurisée si les données contiennent des informations personnelles.

## 12. Orchestration, dépendances et reprise

Un orchestrateur décrit les tâches, leur ordre, les horaires, les retries, les délais et les alertes. Le workflow doit être représenté comme un graphe de dépendances. Par exemple, l'extraction ne démarre pas si la source est indisponible ; le chargement des faits attend que les dimensions nécessaires soient prêtes ; la publication des rapports attend les contrôles qualité.

~~~mermaid
flowchart TD
    A["Vérifier sources"] --> B["Extraire / CDC"]
    B --> C["Staging"]
    C --> D["Contrôles structurels"]
    D --> E["Construire dimensions"]
    E --> F["Construire faits"]
    F --> G["Réconciliation"]
    G --> H["Actualiser modèle sémantique"]
    H --> I["Notifier succès"]
    D -->|échec critique| X["Quarantaine + alerte"]
    G -->|écart critique| X
~~~

La répétition automatique doit être conçue, pas activée sans réfléchir. Une tâche peut être réessayée si elle échoue pour une panne temporaire, mais un retry sans limite peut masquer un défaut permanent. Définissez un nombre maximal de tentatives, un délai progressif, un jitter, des timeouts et une procédure d'escalade. Un échec de validation des données n'est pas nécessairement résolu en répétant à l'identique la même extraction.

Les graphes d'orchestration doivent prendre en compte les dépendances de données, pas seulement le calendrier. Un tableau de bord mensuel doit dépendre du lot qui a réellement traité la période, pas du simple passage de minuit. Les reprises manuelles doivent permettre de relancer une période, un lot ou une tâche précise en conservant le contexte. La procédure doit empêcher deux exécutions concurrentes de modifier sans coordination le même watermark ou la même partition.

L'observabilité inclut l'identifiant de run, l'identifiant de lot, les bornes de données, la durée de chaque tâche, le nombre de lignes, les erreurs et l'état de publication. Un statut « vert » du planificateur ne prouve pas la qualité des chiffres ; les métriques de données sont aussi importantes que les métriques d'infrastructure.

## 13. Traitements tardifs, corrections et données historiques

Une donnée peut arriver longtemps après l'événement qu'elle décrit. Un paiement peut être confirmé après sa création, une certification peut être reçue plus tard par un système de reporting ou un fichier journalier peut arriver après une interruption. L'entrepôt doit distinguer la date de l'événement, la date de réception, la date de traitement et la période analytique à laquelle il appartient.

Pour une table de faits, on peut utiliser la date métier comme dimension de date tout en conservant les timestamps de réception et de chargement pour la traçabilité. Un événement tardif peut modifier une partition historique et nécessite de recalculer certains agrégats dérivés. Une architecture qui n'accepte que les événements du jour doit documenter ce compromis et prévoir un mécanisme de correction.

Les corrections rétroactives peuvent être traitées par une mise à jour idempotente du fait, une compensation ou une nouvelle version selon le domaine. Pour des données financières, il peut être préférable de préserver les mouvements de correction plutôt que de remplacer invisiblement l'historique. Pour une statistique de fréquentation, recalculer une fenêtre récente peut suffire. Il n'existe pas une règle unique ; il faut arbitrer entre auditabilité, simplicité, stockage, précision historique et coût de recalcul.

Le modèle dimensionnel de type 2 conserve l'évolution des attributs descriptifs, tandis que les faits tardifs demandent une résolution de dimension adaptée à la date d'occurrence. Si un événement arrive avant que sa dimension soit connue, le pipeline peut créer un membre provisoire, mettre le fait en attente ou le charger avec une clé « inconnu » puis corriger la référence. Chaque option doit être documentée et testée.

## 14. Performance, partitionnement et coûts

Les problèmes de performance doivent être diagnostiqués à partir du profil des requêtes et des volumes. Les dimensions doivent permettre des jointures efficaces ; les tables de faits peuvent être partitionnées selon la date ou un autre critère si le moteur et les requêtes en tirent bénéfice. Une partition par mois peut simplifier la suppression de données expirées ou la reconstruction d'une période, mais elle ne remplace pas un index ou un modèle adapté et ne garantit pas automatiquement l'accélération.

La compression, le format colonne, les statistiques, les agrégations pré-calculées et l'élagage de partitions sont des leviers possibles dans les plateformes qui les prennent en charge. Leurs effets doivent être vérifiés dans les plans et métriques du moteur réel. Sur une petite table, une sophistication de partitionnement peut augmenter la complexité sans bénéfice visible.

Le coût de l'entrepôt est souvent influencé par le volume scanné, les fenêtres de calcul, la duplication, la durée de rétention, les environnements de test et les jobs qui tournent sans valeur métier. Surveiller les ressources ne signifie pas supprimer des données historiques nécessaires. Il faut définir une politique de rétention par catégorie, distinguer les données brutes des données agrégées et conserver la capacité de reconstituer les indicateurs lorsque cela est requis.

### 14.1 Les agrégats pré-calculés

Un agrégat peut accélérer un tableau de bord fréquemment consulté. Mais l'agrégat doit avoir un contrat de fraîcheur et une méthode de reconstruction. S'il est calculé une fois par jour, les utilisateurs ne doivent pas le confondre avec une mesure temps réel. Si les faits tardifs changent une période historique, le processus doit recalculer les agrégats concernés ou expliquer qu'ils sont approximatifs.

Les vues matérialisées et tables d'agrégats sont des optimisations utiles lorsqu'elles s'appuient sur une définition stable. N'implémentez pas chaque graphique comme une table différente sans gouvernance, sinon plusieurs calculs du même indicateur peuvent diverger. Centralisez les définitions métier importantes et ajoutez des tests de cohérence entre modèle détaillé et agrégat.

## 15. Sécurité, confidentialité et gouvernance

Un entrepôt réunit souvent des données provenant de plusieurs systèmes, ce qui en fait une cible intéressante et une source de risque. Les copies analytiques peuvent survivre plus longtemps que les données opérationnelles et rendre accessibles des informations à des personnes qui n'en ont pas besoin. Appliquez le moindre privilège, contrôlez les accès aux zones brutes et aux vues métier, chiffrez les flux et les sauvegardes, et évitez les secrets dans le code.

La minimisation exige d'importer uniquement les champs nécessaires à une finalité déclarée. Les données personnelles qui ne servent pas à l'analyse doivent être exclues ou transformées selon les règles de l'organisation. Le masquage, la pseudonymisation et l'anonymisation ne sont pas synonymes ; une donnée pseudonymisée peut encore être réidentifiable si une table de correspondance existe ou si les attributs permettent une corrélation.

La traçabilité permet de répondre à des questions d'audit : d'où vient ce champ, quelle transformation lui a été appliquée, quelle version du pipeline a produit ce lot, qui a approuvé le modèle, et quelle période de source est couverte ? Le lignage peut être suivi au niveau des tables, colonnes, transformations et exécutions. Sa valeur dépend de la précision et de la mise à jour des métadonnées.

Les règles de rétention doivent être exécutables. Si un identifiant n'est plus nécessaire, il faut savoir dans quelles zones, snapshots, agrégats et sauvegardes il subsiste. Les obligations de suppression ou de restriction peuvent avoir des implications complexes pour les historiques analytiques ; les décisions doivent être validées avec les responsables compétents et inscrites dans le design, plutôt que découvertes lors d'un incident.

## 16. Mini-projet : construire un entrepôt d'inscriptions

### 16.1 Hypothèses et grain

Le projet utilise une base opérationnelle avec les inscriptions, les cours, les apprenants et les paiements. La table de faits principale aura une ligne par inscription créée. Les paiements resteront dans un fait séparé, car une inscription peut être remboursée ou payée en plusieurs échéances. Les questions de direction porteront sur le nombre d'inscriptions, le revenu reconnu, le taux d'achèvement et les variations par catégorie ou canal.

### 16.2 Tables cibles illustratives

~~~sql
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    calendar_date DATE NOT NULL UNIQUE,
    day_number INTEGER NOT NULL,
    month_number INTEGER NOT NULL,
    quarter_number INTEGER NOT NULL,
    year_number INTEGER NOT NULL
);

CREATE TABLE dim_channel (
    channel_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    channel_code VARCHAR(100) NOT NULL UNIQUE,
    channel_name VARCHAR(200) NOT NULL
);

CREATE TABLE fact_enrollment (
    enrollment_id VARCHAR(100) PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    course_key BIGINT NOT NULL,
    learner_key BIGINT NOT NULL,
    channel_key BIGINT NOT NULL REFERENCES dim_channel(channel_key),
    enrollment_count INTEGER NOT NULL DEFAULT 1,
    batch_id VARCHAR(100) NOT NULL,
    source_updated_at TIMESTAMP,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
~~~

La clé de cours et la clé d'apprenant doivent être résolues depuis les dimensions correspondantes avant le chargement du fait. Pour rendre l'exemple concret, le prochain bloc illustre un contrôle d'intégrité, mais il ne remplace pas une convention de gestion des membres inconnus. Les clés externes des dimensions doivent être adaptées à la stratégie adoptée pour les entités à évolution lente.

~~~sql
SELECT COUNT(*) AS rows_without_course
FROM staging_enrollment AS s
LEFT JOIN dim_course AS d
  ON d.course_id = s.course_id AND d.is_current = TRUE
WHERE d.course_key IS NULL;
~~~

Si le résultat n'est pas nul, le pipeline décide si le lot échoue, si les lignes passent en quarantaine ou si un membre provisoire est créé. La décision dépend de la criticité de la dimension. Charger silencieusement une clé incorrecte compromet les agrégats ultérieurs.

### 16.3 Transformation des faits

~~~sql
INSERT INTO fact_enrollment (
    enrollment_id,
    date_key,
    course_key,
    learner_key,
    channel_key,
    enrollment_count,
    batch_id,
    source_updated_at
)
SELECT
    s.enrollment_id,
    dd.date_key,
    dc.course_key,
    dl.learner_key,
    ch.channel_key,
    1,
    s.batch_id,
    s.source_updated_at
FROM staging_enrollment AS s
JOIN dim_date AS dd
  ON dd.calendar_date = CAST(s.created_at AS DATE)
JOIN dim_course AS dc
  ON dc.course_id = s.course_id AND dc.is_current = TRUE
JOIN dim_learner AS dl
  ON dl.learner_id = s.learner_id AND dl.is_current = TRUE
JOIN dim_channel AS ch
  ON ch.channel_code = s.channel_code
WHERE s.batch_id = :batch_id;
~~~

Ce SQL est une base d'apprentissage, pas un script de production prêt à exécuter. Il suppose notamment que les dimensions de cours et d'apprenant utilisent une stratégie de version courante. Si l'analyse doit préserver l'attribut exact de la dimension à la date d'inscription, remplacez la sélection de version courante par une jointure temporelle SCD adaptée. Le traitement d'une ligne source orpheline doit être explicite, sans que la jointure interne ne la fasse disparaître silencieusement.

Avant de généraliser la logique, vérifiez la clé de déduplication, la date métier, les fuseaux horaires, les types monétaires, les remboursements et les corrections tardives. Une seule opération SQL propre en apparence peut néanmoins calculer un chiffre faux si le grain du modèle ou les règles d'affectation ne sont pas correctement définis.

### 16.4 Réconciliation de fin de lot

À la fin du chargement, comparez le nombre de lignes sources, le nombre de lignes acceptées, la quarantaine, les doublons retirés et le nombre de faits insérés ou mis à jour. Le registre de lots doit expliquer chaque écart. Si un lot est publié avec des anomalies autorisées, elles doivent être visibles dans son état et dans les tableaux de bord opérationnels. Un tableau de bord analytique ne doit pas masquer la fraîcheur et la qualité du dernier chargement.

### 16.5 Tests de reprise

Testez au moins ces scénarios : source indisponible avant extraction, interruption pendant le chargement, même fichier livré deux fois, changement de schéma, données tardives, dimension absente, partition déjà chargée, erreur pendant la publication des agrégats et reprise après un lot rejeté. Pour chaque scénario, consignez l'état avant, l'action de reprise, les lignes finales, les métriques attendues et la preuve que les faits ne sont ni perdus ni doublés.

## 17. Douze exercices corrigés

### Exercice 1 — OLTP ou OLAP ?

Le service d'inscription doit enregistrer immédiatement une nouvelle inscription, tandis que la direction souhaite agréger trois années d'activité par mois, catégorie et canal. Pourquoi pourrait-on séparer ces traitements ?

**Correction :** L'opération d'inscription est transactionnelle et doit respecter la latence du service. L'analyse historique est plus lourde et peut parcourir beaucoup de données. Un entrepôt permet de dédier un modèle et des ressources à l'analyse, de préserver l'historique et de limiter la concurrence avec le système opérationnel.

### Exercice 2 — Choix ETL ou ELT

Une règle de sécurité interdit de charger certains identifiants personnels dans la plateforme analytique. Peut-on charger la totalité du contenu puis masquer les champs plus tard sans autre réflexion ?

**Correction :** Non. La protection doit intervenir avant l'entrée dans la zone qui n'est pas autorisée à recevoir les identifiants. Un pipeline peut effectuer une extraction filtrée ou une transformation avant chargement, puis utiliser ELT pour les transformations analytiques non sensibles. La politique doit couvrir logs, rejets et fichiers intermédiaires.

### Exercice 3 — Définir le grain

Une table contient une ligne par inscription, mais un rapport joint aussi chaque paiement. Une inscription peut avoir trois paiements. Quel danger apparaît ?

**Correction :** La jointure peut produire trois lignes pour une inscription, multipliant le compte d'inscriptions et les mesures répétées. Il faut définir séparément le grain du fait d'inscription et celui du fait de paiement, puis agréger au niveau nécessaire avec des clés et mesures non ambiguës.

### Exercice 4 — Fait ou dimension

Dans un rapport, la catégorie du cours sert à filtrer et regrouper, tandis que le nombre d'inscriptions est calculé. Où placer ces informations ?

**Correction :** La catégorie est un attribut descriptif d'une dimension de cours ; le nombre d'inscriptions est une mesure ou un fait selon le grain défini. Il est important que les dimensions aient des clés stables et que les mesures soient calculées à partir des événements attendus.

### Exercice 5 — Type 1 ou Type 2

Un apprenant change de région et l'entreprise veut savoir dans quelle région les inscriptions historiques ont été réalisées. Quelle stratégie SCD convient généralement ?

**Correction :** Le Type 2, car il crée une nouvelle version de la dimension et conserve les intervalles de validité. Les faits historiques peuvent référencer la version correspondant à la date de l'inscription. Un simple écrasement de la région actuelle modifierait le contexte des analyses passées.

### Exercice 6 — Watermark

Un pipeline mémorise la date de dernière modification la plus récente puis avance le watermark avant de charger les faits. Que se passe-t-il si le chargement échoue ensuite ?

**Correction :** La prochaine exécution peut ignorer les données comprises entre l'ancien et le nouveau watermark. Le watermark doit être avancé uniquement après le chargement, les contrôles et la publication réussis, ou le processus doit disposer d'une procédure fiable de rollback et de rejeu.

### Exercice 7 — Événement CDC en double

Une interruption oblige le consommateur CDC à reprendre à un offset plus ancien et à recevoir à nouveau quelques événements. Quelle qualité doit avoir le consommateur ?

**Correction :** Il doit être idempotent ou dédupliquer les événements grâce à un identifiant stable et à une stratégie de version/ordre. La répétition d'un événement ne doit pas doubler un paiement ni créer une deuxième inscription analytique. Le traitement de l'offset doit suivre le contrat exact du connecteur.

### Exercice 8 — Réconciliation

Le nombre total de lignes en staging est égal au nombre de lignes chargées. Est-ce suffisant pour conclure que le lot est juste ?

**Correction :** Non. Des doublons et des lignes manquantes peuvent se compenser. Il faut également contrôler l'unicité des clés métier, les orphelins, les totaux par catégories pertinentes, les montants, les dates, les quarantaines et les règles métier. La qualité ne se résume pas à un total.

### Exercice 9 — Retry après erreur

Une tâche d'orchestration a expiré après l'insertion des faits, mais avant de confirmer son succès. Pourquoi une relance naïve est-elle risquée ?

**Correction :** Les mêmes faits peuvent être insérés une seconde fois ou des agrégats peuvent être doublés. Le pipeline doit être idempotent, utiliser une clé métier et un registre de lots, et reprendre depuis une étape dont les effets sont vérifiables. Le succès doit être publié de manière contrôlée.

### Exercice 10 — Donnée tardive

Une inscription d'avril arrive au début de mai. Comment concevoir le pipeline pour éviter de l'affecter à mai uniquement parce qu'elle a été reçue en mai ?

**Correction :** Séparer la date de l'événement et la date de réception/chargement. La dimension de date du fait utilise la date métier d'avril si telle est la règle, tandis que les métadonnées de chargement conservent la date de traitement en mai. Les agrégats d'avril doivent être recalculés ou corrigés.

### Exercice 11 — Référence dimensionnelle absente

Un fait référence un cours inconnu à la date du chargement. Quelle approche peut être adoptée ?

**Correction :** Selon les règles, échouer le lot, placer la ligne en quarantaine, créer un membre inconnu avec traçabilité ou créer un membre provisoire qui sera complété par la suite. La décision et la réparation doivent être explicites. Une jointure interne qui élimine silencieusement le fait est dangereuse.

### Exercice 12 — Fraîcheur et SLA

Le tableau de bord affiche des données jusqu'à 03 h, mais les utilisateurs pensent voir les chiffres en temps réel. Quelle amélioration est prioritaire ?

**Correction :** Définir et afficher la fraîcheur réelle, préciser l'objectif métier, mesurer le retard du pipeline, mettre en place une alerte et décider si l'architecture doit passer à un batch plus fréquent ou au CDC. Il faut aligner promesse, calendrier, orchestration et indicateurs, plutôt que d'appeler automatiquement le système « temps réel ».

## 18. Défi final corrigé : un pipeline analytique fiable

### Énoncé

SkillMarket veut publier chaque matin un tableau de bord qui mesure les inscriptions, les revenus nets, les cours terminés et la conversion par canal. Les données proviennent de la base d'inscription, du prestataire de paiement et d'une API d'apprentissage. Une livraison de fichier peut être retardée, un même événement peut arriver plusieurs fois et les métadonnées d'un cours peuvent changer.

### Proposition de correction

**Modèle métier.** Définir séparément un fait d'inscription, un fait de paiement et un fait de progression. Un grain explicite évite que chaque paiement supplémentaire multiplie le nombre d'inscriptions. Des dimensions conformes de date, cours, apprenant et canal permettent des analyses croisées cohérentes. Les montants doivent distinguer paiements, remboursements, taxes et devise selon les règles financières.

**Ingestion.** Pour les tables SQL, un watermark ou CDC peut être choisi selon les capacités de la source. Pour l'API, enregistrer les fenêtres interrogées, les identifiants d'événements et les pages récupérées. Pour les fichiers, attendre une indication fiable de livraison complète, valider le format et calculer une empreinte de fichier. Conserver des métadonnées de source, d'extraction et de lot pour le diagnostic.

**Transformation.** Normaliser les dates, devises, états et identifiants dans la zone de staging. Dédupliquer les événements avec une clé stable. Résoudre les clés de dimension et appliquer l'historique Type 2 lorsqu'un changement doit être visible dans l'analyse passée. Rejeter ou mettre en quarantaine les données invalides selon une règle explicitement approuvée.

**Publication.** Charger les dimensions puis les faits, exécuter les contrôles de réconciliation, comparer volumes et montants par périmètre, puis ne publier l'état du lot qu'après réussite. Le watermark ne progresse qu'après cette publication. Les vues analytiques s'appuient sur des définitions partagées et identifient leur fraîcheur.

**Exploitation.** L'orchestrateur exprime les dépendances, les timeouts, les retries bornés et les alertes. Les erreurs transitoires sont réessayées ; les erreurs de contrat et de qualité sont signalées aux propriétaires de données. Les lots sont relançables et ne doivent pas créer de doublons. Le runbook indique comment reprendre un fichier retardé, réparer une dimension inconnue et recalculer une période historique.

**Validation.** Exécuter un test normal, un test de livraison dupliquée, un test d'événement tardif, un test de dimension Type 2 et un test de panne après chargement mais avant la mise à jour du watermark. Vérifier que les résultats finaux restent cohérents après une relance. Mesurer le délai d'arrivée, les lignes traitées, les rejets, la latence, les écarts de réconciliation et la fraîcheur publiée.

**Gouvernance.** Définir les propriétaires des indicateurs, les autorisations de chaque couche, les données personnelles nécessaires, les règles de conservation et le lignage de bout en bout. Un indicateur de revenus doit avoir une définition officielle, une monnaie de référence et une politique pour les remboursements et corrections. Une autre équipe ne doit pas réimplémenter cet indicateur avec une définition concurrente sans décision documentée.

## 19. Checklist de révision

- [ ] Je distingue OLTP, OLAP, zone de staging, entrepôt, datamart et modèle sémantique.
- [ ] Je sais expliquer les différences entre ETL, ELT, batch et CDC.
- [ ] Je définis le grain avant de créer une table de faits.
- [ ] Je distingue les mesures des attributs de dimension.
- [ ] Je sais quand une dimension Type 1 ou Type 2 convient.
- [ ] Je peux concevoir un watermark avec une borne haute et une publication sûre.
- [ ] Je prends en charge les suppressions, événements tardifs et doublons.
- [ ] Je sais pourquoi l'idempotence est nécessaire lors des retries.
- [ ] Je définis les contrôles de qualité et les seuils bloquants.
- [ ] Je peux expliquer la dépendance entre tâches d'orchestration.
- [ ] Je sais réconcilier les nombres de lignes et les mesures métier.
- [ ] Je connais les enjeux de sécurité, de rétention et de lignage.
- [ ] Je dispose d'un plan de reprise et de tests reproductibles.
- [ ] Je peux démontrer que le modèle analytique répond aux questions métier sans double comptage.

## 20. Références officielles et documentation

- Microsoft Learn, aperçu de la modélisation dimensionnelle : https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-overview
- Microsoft Learn, tables de dimensions et historique SCD : https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables
- Microsoft Learn, chargement des tables d'un modèle dimensionnel : https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-load-tables
- Apache Airflow, concepts et architecture d'orchestration : https://airflow.apache.org/docs/apache-airflow/stable/concepts/
- Apache Airflow, DAGs, tâches et dépendances : https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html
- Google Cloud, aperçu des schémas et transferts de données : https://cloud.google.com/bigquery/docs/migration/schema-data-overview
- Google Cloud, schémas de tables et types de colonnes : https://cloud.google.com/bigquery/docs/schemas

Les principes de ce cours peuvent être appliqués dans PostgreSQL, SQL Server, BigQuery, Snowflake, Redshift ou d'autres plateformes, mais les syntaxes, transactions, coûts et comportements opérationnels ne sont pas identiques. Consultez la documentation correspondant à la technologie déployée et testez les exemples dans un environnement isolé.

Le niveau intermédiaire consiste à rendre les données analytiques fiables au fil des changements et des incidents. Un entrepôt bien conçu n'est pas seulement une collection de tables de reporting : c'est un produit de données dont le grain, la provenance, les règles métier, les tests, la fraîcheur et les responsabilités sont documentés. Sa qualité se démontre par des chiffres réconciliés et une reprise maîtrisée, pas uniquement par une tâche planifiée qui se termine sans erreur.
