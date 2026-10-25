# Haute Disponibilité des Bases de Données

## 1. Introduction à la haute disponibilité

Une base de données peut fonctionner correctement pendant des mois, puis subir une panne matérielle, une erreur de configuration, une saturation du stockage ou une défaillance réseau. Lorsque les applications dépendent directement de cette base, l'incident peut interrompre une partie importante du système d'information.

La haute disponibilité, généralement abrégée **HA** pour *High Availability*, vise à maintenir un service accessible malgré certaines défaillances.

Dans une architecture PostgreSQL, elle repose sur plusieurs mécanismes complémentaires :

- la réplication des données entre plusieurs serveurs ;
- la détection des pannes ;
- la désignation d'un serveur primaire ;
- le basculement vers un serveur de secours ;
- la prévention de plusieurs primaires actifs simultanément ;
- la redirection des connexions applicatives ;
- la sauvegarde et la récupération des données ;
- la surveillance de l'ensemble de l'infrastructure.

La présence de deux serveurs PostgreSQL ne suffit pas à garantir une haute disponibilité. Il faut aussi organiser la coordination, la prise de décision, le basculement, les connexions clientes et la récupération après incident.

### 1.1 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

- distinguer haute disponibilité, réplication, sauvegarde et reprise après sinistre ;
- définir des objectifs RPO et RTO ;
- concevoir une architecture PostgreSQL primaire-secondaires ;
- comprendre les mécanismes WAL et la réplication physique ;
- différencier réplication synchrone et asynchrone ;
- initialiser un serveur secondaire avec `pg_basebackup` ;
- contrôler le retard de réplication ;
- comprendre les risques liés aux replication slots ;
- expliquer le rôle de Patroni et d'un système de consensus comme etcd ;
- prévenir le scénario de *split-brain* ;
- configurer HAProxy pour diriger les connexions vers le primaire ;
- comprendre la promotion d'un secondaire ;
- réintégrer un ancien primaire après un basculement ;
- utiliser `pg_rewind` lorsque ses conditions sont réunies ;
- organiser les sauvegardes avec archivage WAL et restauration PITR ;
- superviser la réplication, le stockage et les erreurs ;
- réaliser des simulations de panne contrôlées ;
- préparer un plan de reprise et un retour à l'état nominal.

### 1.2 Prérequis

Ce cours prolonge les connaissances acquises sur l'administration des bases de données :

- gestion des rôles et privilèges PostgreSQL ;
- configuration de `postgresql.conf` et `pg_hba.conf` ;
- surveillance avec `pg_stat_activity` ;
- sauvegardes avec `pg_dump` et `pg_restore` ;
- utilisation de `systemctl`, `journalctl` et `ss` ;
- diagnostic des erreurs réseau ;
- compréhension des transactions et du WAL.

Le SGBD principal est PostgreSQL. Patroni et HAProxy sont utilisés comme exemples d'outils d'orchestration et de routage.

Les configurations présentées sont des modèles pédagogiques. Les chemins, les versions et certains paramètres doivent être adaptés à la distribution, à la version PostgreSQL et à l'environnement réel avant toute mise en production.


## 2. Définir correctement les objectifs de disponibilité

### 2.1 Qu'est-ce que la disponibilité ?

La disponibilité représente la capacité d'un service à fonctionner et à répondre aux demandes dans des conditions acceptables.

On peut la représenter de manière simplifiée :

```text
Temps observé
     |
     +---- Service fonctionnel
     |
     +---- Service indisponible
```

Une base peut être indisponible à la suite :

- d'une panne matérielle ;
- d'un arrêt du processus PostgreSQL ;
- d'un problème du système d'exploitation ;
- d'un incident réseau ;
- d'une saturation du stockage ;
- d'une erreur humaine ;
- d'une corruption de données ;
- d'un défaut dans le mécanisme de basculement.

Chaque cause demande une réponse différente.

### 2.2 Disponibilité théorique

Un objectif de disponibilité est parfois exprimé sous forme de pourcentage.

| Disponibilité visée | Indisponibilité théorique approximative sur une année de 365 jours |
|---|---:|
| 99 % | 3 jours, 15 heures et 36 minutes |
| 99,9 % | 8 heures, 45 minutes et 36 secondes |
| 99,95 % | 4 heures, 22 minutes et 48 secondes |
| 99,99 % | 52 minutes et 34 secondes environ |
| 99,999 % | 5 minutes et 15 secondes environ |

Ces valeurs représentent une disponibilité théorique sur la période considérée. Elles ne comprennent pas automatiquement les exclusions liées à une politique de maintenance, aux mesures retenues pour calculer la disponibilité ou à un accord de service particulier.

Une architecture ne doit pas être qualifiée de « cinq neuf » uniquement parce qu'elle possède plusieurs serveurs.

### 2.3 Le RPO : perte de données acceptable

Le **RPO** (*Recovery Point Objective*) représente le point maximal de perte de données acceptable, exprimé dans le temps.

Exemple :

```text
Dernière transaction enregistrée
             |
             v
T0 ------------------------ T1
             |
             +-- Panne
```

Si des transactions ont été validées sur le primaire mais n'ont pas été reçues ou rendues récupérables sur le secondaire, elles peuvent être perdues lors d'un basculement, selon le mécanisme de réplication et l'état exact des serveurs.

Un RPO de zéro signifie qu'aucune perte de transaction validée n'est acceptable dans les conditions couvertes par la conception et les garanties retenues. Cet objectif nécessite une architecture adaptée ; il ne peut pas être déduit du simple fait qu'un secondaire existe.

### 2.4 Le RTO : durée de rétablissement acceptable

Le **RTO** (*Recovery Time Objective*) représente la durée maximale visée pour remettre le service à disposition après une panne.

Exemple :

```text
Panne du primaire
       |
       v
Détection
       |
       v
Décision de basculement
       |
       v
Promotion du secondaire
       |
       v
Redirection des connexions
       |
       v
Validation applicative
       |
       v
Service rétabli
```

Le RTO dépend notamment du délai de détection, de la décision du gestionnaire de cluster, de la promotion, du routage et de la reconnexion des applications.

Une promotion rapide ne garantit pas un rétablissement rapide si l'application continue d'utiliser une ancienne adresse ou si son pool de connexions ne récupère pas correctement.

### 2.5 Exemple d'objectifs métier

Une application pourrait définir les exigences suivantes :

| Indicateur | Objectif d'exemple |
|---|---|
| RPO | Au plus 5 secondes de données perdues dans le scénario de panne défini |
| RTO | Retour du service en moins de 60 secondes |
| Réplication | Retard surveillé et alerté |
| Sauvegardes | Sauvegardes régulières dans un dépôt indépendant |
| Restauration | Procédure testée périodiquement |

Ces valeurs sont illustratives. Les objectifs réels doivent être définis par les responsables métier et vérifiés par des tests.


## 3. Haute disponibilité, réplication et sauvegarde

Ces trois notions sont complémentaires, mais elles ne répondent pas au même besoin.

### 3.1 La haute disponibilité

La haute disponibilité cherche à maintenir le service en fonctionnement lorsqu'un composant tombe en panne.

```text
          Application
               |
               v
       Point d'accès SQL
               |
          +----+----+
          |         |
          v         v
       Primaire   Secondaire
          |
          +-- Réplication
```

Lorsqu'un primaire devient indisponible, un système de gestion de cluster peut sélectionner un secondaire éligible et le promouvoir.

### 3.2 La réplication

La réplication maintient une autre instance à jour en lui transmettant les modifications du primaire.

Elle peut permettre un basculement plus rapide qu'une restauration complète, mais son résultat dépend du retard, du mode de réplication et de l'état du serveur secondaire.

### 3.3 La sauvegarde

Une sauvegarde permet de récupérer les données à partir d'une copie conservée séparément.

Elle est particulièrement importante lorsqu'une erreur logique se propage à toutes les instances répliquées.

Exemple :

```text
Une commande DELETE erronée est validée
                    |
                    v
          Réplication des changements
                    |
          +---------+---------+
          |                   |
          v                   v
       Primaire           Secondaire
       Données             Données
       supprimées          supprimées
```

Le secondaire n'est pas une sauvegarde indépendante : il reproduit normalement les changements du primaire.

### 3.4 La reprise après sinistre

La reprise après sinistre (*Disaster Recovery*) concerne un incident majeur : perte d'un site, destruction d'une infrastructure ou impossibilité de retrouver le service dans son environnement initial.

Elle peut nécessiter :

- des sauvegardes dans une autre zone ;
- un dépôt WAL distant ;
- des serveurs situés sur un autre site ;
- des procédures de reconstruction ;
- une procédure d'activation du site de secours ;
- une stratégie de retour au site principal.

### 3.5 Tableau comparatif

| Mécanisme | Objectif principal | Limite importante |
|---|---|---|
| Réplication | Maintenir une autre instance à jour | Peut reproduire une erreur logique |
| Basculement automatique | Réduire le temps d'indisponibilité | Doit empêcher deux primaires actifs |
| Sauvegarde logique | Exporter les objets et données | Restauration parfois longue |
| Sauvegarde physique | Préserver une copie exploitable du cluster | Nécessite une méthode de restauration adaptée |
| Archivage WAL | Permettre la relecture des changements | Dépend de la continuité et de la disponibilité des journaux |
| PITR | Restaurer à un point temporel choisi | Nécessite une sauvegarde de base et les WAL nécessaires |

**Règle fondamentale :** la réplication améliore certaines formes de disponibilité ; la sauvegarde protège contre d'autres catégories de perte de données. Une architecture fiable a généralement besoin des deux.


## 4. Concevoir une architecture PostgreSQL haute disponibilité

### 4.1 Architecture minimale primaire-secondaire

```text
                   APPLICATION
                        |
                        v
               +------------------+
               | Point d'accès SQL|
               +--------+---------+
                        |
                        v
                +---------------+
                | PostgreSQL    |
                | Primaire      |
                +-------+-------+
                        |
                        | WAL
                        v
                +---------------+
                | PostgreSQL    |
                | Secondaire    |
                +---------------+
```

Le primaire accepte les écritures. Le secondaire reçoit et rejoue les informations nécessaires pour maintenir une copie de la base.

Dans une configuration de réplication physique en lecture seule, le secondaire peut éventuellement répondre à des requêtes de lecture lorsqu'il est en mode *hot standby*.

### 4.2 Pourquoi deux serveurs ne suffisent-ils pas toujours ?

Un cluster constitué d'un primaire et d'un secondaire peut fournir une copie de secours. Il doit cependant déterminer si le primaire est réellement en panne ou seulement isolé du reste du réseau.

Considérons la situation suivante :

```text
         PRIMAIRE                     SECONDAIRE
      10.10.0.11                    10.10.0.12
            |                            |
            |         Réseau              |
            +------------X---------------+
                         |
                  Rupture de lien
```

Le secondaire peut constater qu'il ne reçoit plus les WAL. Pourtant, le primaire peut toujours fonctionner et accepter des écritures sur son propre réseau.

Si le secondaire se promeut sans empêcher l'ancien primaire d'écrire, deux instances peuvent accepter des modifications indépendantes.

C'est le problème de *split-brain*.

### 4.3 Architecture avec gestionnaire de cluster

Une architecture automatique ajoute un mécanisme de coordination :

```text
                 +----------------------+
                 | Système de consensus |
                 | DCS : etcd, etc.     |
                 +----------+-----------+
                            |
                   Coordination et état
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          +-------------+       +-------------+
          | Patroni 1   |       | Patroni 2   |
          | PostgreSQL  |       | PostgreSQL  |
          | Primaire    |       | Secondaire  |
          +------+------+       +------+------+
                 |                     |
                 +---------------------+
                         WAL
```

Le gestionnaire de cluster observe les états des instances et participe à la coordination de l'élection du primaire.

Un DCS (*Distributed Configuration Store*) comme etcd, Consul ou ZooKeeper peut stocker l'information de coordination suivant la solution utilisée.

Le DCS ne remplace pas les données PostgreSQL : il sert à la coordination et à la prise de décision.

### 4.4 Architecture de référence recommandée

Pour une architecture PostgreSQL gérée par Patroni, on peut retenir l'organisation conceptuelle suivante :

```text
                 CLIENTS / APPLICATIONS
                           |
                           v
                  +-------------------+
                  | HAProxy ou VIP    |
                  | Point d'accès SQL |
                  +---------+---------+
                            |
                      Port PostgreSQL
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
       +-----------+  +-----------+  +-----------+
       | PG Node 1 |  | PG Node 2 |  | PG Node 3 |
       | Patroni   |  | Patroni   |  | Patroni   |
       +-----+-----+  +-----+-----+  +-----+-----+
             |              |              |
             +--------------+--------------+
                            |
                            v
                 +---------------------+
                 | DCS                 |
                 | Quorum / État       |
                 +---------------------+

                 +---------------------+
                 | Dépôt de sauvegarde |
                 | Indépendant         |
                 +---------------------+
```

Cette architecture est un exemple de référence. Elle doit être adaptée aux domaines de panne, aux besoins de sécurité, au réseau et aux ressources de l'organisation.

Pour une disponibilité réelle, évitez de placer tous les composants critiques sur un même hôte physique. Trois machines virtuelles hébergées sur un seul serveur physique ne protègent pas contre la perte de cet hôte.


## 5. Comprendre le WAL et la réplication physique

### 5.1 Le rôle du WAL

WAL signifie *Write-Ahead Logging*.

PostgreSQL enregistre les informations de modification dans un journal avant que les pages de données correspondantes n'aient nécessairement été écrites dans leur emplacement final.

Ce mécanisme permet notamment la récupération après une panne et l'application des changements sur un serveur secondaire.

```text
Transaction
     |
     v
Modification logique
     |
     v
Enregistrement WAL
     |
     v
Validation selon les garanties configurées
     |
     v
Écriture des données au fil des opérations
```

Le WAL est un élément central de la durabilité PostgreSQL. Il ne constitue pas à lui seul une sauvegarde autonome de toutes les données.

### 5.2 Comment le secondaire reçoit-il les changements ?

En réplication physique, le secondaire reçoit les informations WAL du primaire, puis les rejoue pour reproduire l'état des données.

```text
                 PRIMAIRE
                    |
                    | Produit les enregistrements WAL
                    v
               WAL courant
                    |
                    | Streaming de réplication
                    v
                SECONDAIRE
                    |
                    | Rejeu du WAL
                    v
             État répliqué
```

La réplication physique porte sur la structure du cluster PostgreSQL, et non simplement sur les résultats de requêtes SQL individuelles.

Elle exige des versions et une configuration compatibles, ainsi qu'une procédure adaptée à l'initialisation et à la reconstruction des secondaires.

### 5.3 Réplication par fichiers et streaming

Deux mécanismes courants sont :

- le transfert de segments WAL archivés ;
- le streaming des enregistrements WAL au fil de leur production.

Le streaming permet généralement au secondaire de suivre plus rapidement le primaire qu'un transfert qui attend l'achèvement de segments de journal.

L'archivage WAL reste utile pour la récupération et peut compléter la réplication en direct.

### 5.4 Pourquoi la version du serveur est importante

Les procédures de réplication dépendent de la version PostgreSQL.

Pour les versions modernes, notamment PostgreSQL 12 et suivantes, la configuration d'un standby utilise notamment le fichier `standby.signal` et les paramètres habituels du serveur. L'ancien fichier `recovery.conf` n'est plus le mécanisme de configuration à utiliser.

Vérifiez toujours la documentation correspondant à la version réelle de PostgreSQL.


## 6. Réplication asynchrone et synchrone

Le choix entre la réplication asynchrone et synchrone influence directement le compromis entre durabilité, latence et disponibilité.

### 6.1 Réplication asynchrone

Dans une réplication asynchrone, le primaire peut valider une transaction sans attendre que le secondaire confirme la réception ou la durabilité de son WAL, selon le niveau de synchronisation configuré.

```text
Application
    |
    | Écriture
    v
Primaire
    |
    | Commit confirmé au client
    |
    +---------> WAL transmis ensuite au secondaire
```

Avantages :

- faible impact du réseau de réplication sur la validation des transactions dans le cas courant ;
- fonctionnement adapté aux réseaux où la latence varie ;
- possibilité de poursuivre les écritures lorsque le secondaire est temporairement inaccessible, sous les conditions de la configuration.

Limite :

- si le primaire tombe avant que certaines modifications soient reçues ou rendues durables sur le secondaire choisi pour le basculement, des transactions validées peuvent être perdues.

### 6.2 Réplication synchrone

La réplication synchrone peut obliger le primaire à attendre une confirmation d'un ou plusieurs secondaires avant de confirmer certaines validations de transactions.

```text
Application
    |
    | Écriture
    v
Primaire
    |
    | WAL envoyé
    v
Secondaire
    |
    | Confirmation selon le niveau choisi
    v
Primaire
    |
    | Validation confirmée au client
```

Avantages :

- meilleure durabilité à l'égard de certains scénarios de panne du primaire ;
- possibilité de réduire fortement le risque de perdre une transaction confirmée lors d'une promotion convenablement effectuée.

Limites :

- hausse possible de la latence des écritures ;
- dépendance à l'état des secondaires requis ;
- possibilité que les validations attendent si aucun secondaire synchrone admissible ne répond.

### 6.3 Les différents niveaux de confirmation

PostgreSQL expose le paramètre `synchronous_commit`, qui permet de choisir la condition de confirmation requise.

| Valeur | Principe général |
|---|---|
| `off` | N'attend pas la confirmation locale habituelle du WAL avant de signaler la validation ; des transactions récemment déclarées validées peuvent être perdues lors d'une panne système |
| `local` | Attend le flush local du WAL, sans attendre la confirmation distante |
| `remote_write` | Attend l'écriture du WAL sur le système d'exploitation du secondaire selon la configuration synchrone, sans garantir que les données ont été durablement flushées sur son stockage |
| `on` | Attend le flush distant du WAL sur le secondaire synchrone retenu, en plus des garanties locales |
| `remote_apply` | Attend que le secondaire synchrone ait appliqué la transaction et rende ses effets visibles dans son contexte de lecture |

Les garanties exactes dépendent de la méthode de réplication, du stockage, du rôle des secondaires et du mécanisme de basculement.

### 6.4 Réplication synchrone avec une seule cible

Le paramètre `synchronous_standby_names` définit les secondaires susceptibles de répondre au mécanisme de réplication synchrone.

Exemple conceptuel :

```conf
synchronous_standby_names = 'FIRST 1 (pg_standby_1, pg_standby_2)'
```

Dans cette configuration, un secondaire disponible et admissible peut être choisi selon la priorité définie.

Pour les transactions exigeant le niveau de confirmation synchrone, l'absence de secondaire admissible peut bloquer les validations concernées, selon les paramètres de session et les règles du gestionnaire de cluster.

### 6.5 Réplication synchrone avec quorum

PostgreSQL permet également d'utiliser une politique de quorum.

Exemple :

```conf
synchronous_standby_names = 'ANY 1 (pg_standby_1, pg_standby_2, pg_standby_3)'
```

Cette configuration demande une confirmation d'au moins un des secondaires admissibles du groupe, selon le mécanisme défini.

Le choix du quorum doit être cohérent avec l'objectif de durabilité, la topologie réseau et les scénarios de panne à tolérer.

### 6.6 Comment choisir ?

| Critère | Asynchrone | Synchrone |
|---|---|---|
| Latence d'écriture | Généralement plus faible | Peut être plus élevée |
| Risque de perte lors d'un basculement | Dépend du retard | Peut être fortement réduit avec la bonne configuration |
| Dépendance au réseau secondaire | Moins forte pour la validation ordinaire | Peut bloquer les validations exigeant une confirmation |
| Tolérance à un secondaire indisponible | Souvent meilleure pour continuer à écrire | Dépend du mode synchrone et du gestionnaire |
| Cas d'utilisation | Charges sensibles à la latence, pertes limitées acceptables | Données pour lesquelles la durabilité renforcée est prioritaire |

La réplication synchrone ne supprime pas le besoin de sauvegardes, de contrôle du split-brain et de tests de panne. Elle ne rend pas non plus toutes les opérations applicatives idempotentes.


## 7. Les principaux risques d'une architecture HA

### 7.1 Le split-brain

Le split-brain est l'un des risques les plus importants.

Il apparaît lorsque deux instances peuvent agir comme primaires et accepter des écritures indépendantes.

```text
                    Ancien primaire
                         |
                         | Réseau partitionné
                         X
                         |
                    Secondaire promu
                         |
                         v
               Deux branches de données
```

Les changements effectués sur les deux branches peuvent diverger. Les réconcilier n'est pas une simple opération de copie.

Une architecture HA doit éviter de promouvoir un serveur si l'ancien primaire peut continuer à écrire dans des conditions concurrentes non contrôlées.

### 7.2 Le fencing

Le *fencing*, ou isolation forcée du nœud, vise à garantir qu'un ancien primaire ne peut plus accepter des écritures lorsqu'un nouveau primaire est activé.

Les mécanismes possibles dépendent de l'infrastructure :

- arrêt ou extinction forcée du nœud ;
- isolation par la couche de virtualisation ;
- contrôle de l'alimentation ;
- mécanisme de watchdog ;
- contrôle réseau suffisamment robuste ;
- mécanisme de gestion du cluster qui assure l'exclusion d'un ancien leader.

Un simple échec de ping ne prouve pas que l'ancien primaire est arrêté.

### 7.3 Le quorum

Le quorum correspond à la majorité nécessaire à la prise de certaines décisions dans un système de consensus.

Pour un cluster etcd, il est courant d'utiliser trois ou cinq membres afin de tolérer certaines défaillances tout en conservant une majorité.

Un ensemble de trois membres peut normalement continuer à former un quorum après la perte d'un membre ; un ensemble de deux membres ne peut pas continuer à obtenir la majorité après la perte d'un membre.

Le quorum du DCS ne garantit pas à lui seul l'intégrité de toutes les écritures PostgreSQL. Il fait partie de la coordination et doit être associé au mécanisme d'exclusion de l'ancien primaire.

### 7.4 Un point d'entrée unique

Un cluster PostgreSQL peut disposer de plusieurs nœuds de données et rester dépendant d'un unique HAProxy.

```text
Application
     |
     v
 HAProxy unique  <--- Panne possible
     |
     +----> PostgreSQL 1
     |
     +----> PostgreSQL 2
     |
     +----> PostgreSQL 3
```

Le répartiteur devient alors un point de défaillance unique.

Pour une architecture réellement disponible, il faut aussi redonder le point d'accès : deux répartiteurs, un service réseau redondant, une adresse virtuelle ou un autre mécanisme adapté.

### 7.5 Les dépendances externes

Une base peut rester disponible alors que l'application ne peut plus l'utiliser en raison :

- d'une résolution DNS défaillante ;
- d'un certificat expiré ;
- d'un pool de connexions bloqué ;
- d'une règle de pare-feu incorrecte ;
- d'un défaut de routage ;
- d'un mécanisme de supervision en panne.

Il faut donc tester le service depuis le chemin réel des applications, et pas seulement depuis une session locale sur le serveur.


## 8. Gestionnaire de cluster : comprendre Patroni

Patroni est un outil d'orchestration de la haute disponibilité PostgreSQL. Il gère l'état des instances et coordonne leur comportement avec un système de configuration distribuée, généralement appelé DCS.

Il ne remplace pas PostgreSQL. Il automatise une partie des mécanismes nécessaires pour gérer un cluster de bases.

### 8.1 Rôle de Patroni

Patroni peut notamment :

- initialiser un cluster ;
- superviser le rôle des nœuds ;
- organiser l'élection du primaire ;
- gérer la configuration de réplication ;
- procéder à un basculement selon les règles retenues ;
- tenter de réintégrer un ancien primaire comme secondaire ;
- fournir une API permettant de connaître l'état des instances.

### 8.2 Architecture conceptuelle

```text
            +---------------------------+
            | DCS                       |
            | etcd / Consul / ZooKeeper |
            +-------------+-------------+
                          |
                          | État et coordination
           +--------------+--------------+
           |                             |
           v                             v
   +---------------+             +---------------+
   | Patroni A     |             | Patroni B     |
   | PostgreSQL A  |             | PostgreSQL B  |
   +-------+-------+             +-------+-------+
           |                             |
           +--------------- WAL ---------+
```

Le DCS sert notamment à déterminer quel nœud détient l'état de leader. Patroni utilise ces informations et les contrôles disponibles pour gérer PostgreSQL.

### 8.3 Le DCS doit être dimensionné séparément

Un DCS à trois membres peut tolérer la perte d'un membre tout en maintenant la majorité, si les autres composants et les conditions réseau sont corrects.

Il est préférable que les membres du DCS soient répartis sur des domaines de panne indépendants, lorsque l'infrastructure le permet.

Trois processus etcd installés sur le même hôte physique ne fournissent pas la même résilience que trois membres répartis sur des hôtes réellement indépendants.

### 8.4 Nombre de nœuds PostgreSQL

Une architecture composée d'un primaire et d'un secondaire peut fonctionner avec Patroni.

Toutefois, lorsqu'un seul secondaire existe, un basculement réussi laisse temporairement le cluster sans copie secondaire tant que l'ancien primaire n'a pas été réintégré ou qu'un autre secondaire n'a pas été créé.

Trois nœuds PostgreSQL peuvent améliorer cette situation en conservant une copie secondaire disponible dans davantage de scénarios.

Cela ne rend pas le système invulnérable : il faut aussi considérer les domaines de panne, le stockage, le réseau et la capacité réelle de chaque nœud.


## 9. Architecture de référence avec Patroni

L'architecture utilisée dans la suite du cours est illustrée par le schéma suivant.

```text
                   APPLICATIONS
                        |
                        v
                +------------------+
                | HAProxy          |
                | Port SQL logique |
                +--------+---------+
                         |
                Vérification du leader
                         |
           +-------------+-------------+
           |             |             |
           v             v             v
       +-------+     +-------+     +-------+
       | PG 1  |     | PG 2  |     | PG 3  |
       | HA    |     | HA    |     | HA    |
       +---+---+     +---+---+     +---+---+
           |             |             |
           +-------------+-------------+
                         |
                         v
                +------------------+
                | etcd             |
                | 3 membres        |
                +------------------+

                +------------------+
                | Dépôt de backup  |
                | Distant          |
                +------------------+
```

Dans cet exemple :

- PostgreSQL stocke et traite les données ;
- Patroni coordonne le rôle de chaque instance ;
- etcd fournit le mécanisme de coordination ;
- HAProxy fournit un point d'accès aux applications ;
- le dépôt de sauvegarde conserve des copies indépendantes.

Les composants de coordination et de sauvegarde sont des éléments critiques. Ils doivent être supervisés eux aussi.


## 10. Préparer les serveurs PostgreSQL

### 10.1 Exemple de topologie

Nous utiliserons des adresses privées fictives pour illustrer les flux.

| Composant | Adresse d'exemple | Port principal |
|---|---|---:|
| PostgreSQL 1 | `10.10.0.11` | 5432 |
| PostgreSQL 2 | `10.10.0.12` | 5432 |
| PostgreSQL 3 | `10.10.0.13` | 5432 |
| etcd 1 | `10.10.0.21` | 2379 |
| etcd 2 | `10.10.0.22` | 2379 |
| etcd 3 | `10.10.0.23` | 2379 |
| HAProxy | `10.10.0.31` | 5000 |

Les adresses sont des exemples de réseau privé. Elles doivent être adaptées à votre réseau et ne doivent pas être copiées aveuglément.

Le port 5000 sera utilisé dans l'exemple pour l'accès applicatif au primaire.

### 10.2 Préparer les systèmes

Les serveurs doivent disposer :

- d'une version PostgreSQL compatible ;
- d'une configuration de fuseau horaire cohérente ;
- d'une synchronisation temporelle fiable ;
- d'un stockage dimensionné ;
- d'une connectivité réseau entre les composants autorisés ;
- de règles de pare-feu cohérentes ;
- d'un mécanisme de gestion des secrets.

Utilisez des procédures reproductibles pour installer les paquets et configurer les services.

### 10.3 Vérifier la connectivité

Depuis une machine de laboratoire autorisée :

```bash
ping -c 3 10.10.0.11
```

Cette commande vérifie si des réponses ICMP sont reçues. Elle ne prouve pas que PostgreSQL accepte des connexions.

Pour contrôler un port TCP, si `nc` est disponible :

```bash
nc -vz 10.10.0.11 5432
```

La connectivité TCP n'assure pas que l'authentification PostgreSQL réussira.

Un diagnostic doit donc distinguer la connectivité réseau, l'écoute du service et l'authentification SQL.


## 11. Initialiser une réplication physique PostgreSQL

Cette section décrit le principe d'une réplication physique manuelle. Elle permet de comprendre ce que l'orchestrateur automatise ensuite.

Les manipulations doivent être réalisées sur des machines de laboratoire ou sur des instances de test. N'écrasez pas le répertoire de données d'un serveur existant.

### 11.1 Configurer le primaire

Dans `postgresql.conf`, le primaire doit disposer des paramètres nécessaires à la réplication physique.

Exemple de paramètres :

```conf
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
```

`wal_level = replica` fournit les informations WAL nécessaires à la réplication physique.

`max_wal_senders` détermine combien de processus émetteurs WAL peuvent être utilisés simultanément.

`max_replication_slots` détermine le nombre maximal de replication slots.

Les valeurs proposées sont illustratives. Elles doivent tenir compte du nombre de secondaires, des besoins de sauvegarde et des connexions de réplication.

Certains paramètres demandent un redémarrage après modification.

### 11.2 Créer un rôle de réplication

Sur le primaire :

```sql
CREATE ROLE replicator LOGIN REPLICATION;
```

Définissez un secret approprié pour ce rôle, au moyen d'une procédure sécurisée telle que `\password replicator` dans `psql`.

N'enregistrez pas le mot de passe en clair dans un dépôt de code, un fichier lisible par tous ou une commande partagée.

Le rôle de réplication doit disposer des seuls privilèges nécessaires à la fonction prévue.

### 11.3 Autoriser le secondaire

Dans `pg_hba.conf` sur le primaire, ajoutez une règle qui autorise le serveur secondaire concerné.

Exemple :

```conf
host    replication    replicator    10.10.0.12/32    scram-sha-256
```

Cette règle concerne une connexion de réplication depuis l'adresse source indiquée, avec le rôle défini.

Répétez avec une règle adaptée pour chaque secondaire autorisé.

Ne remplacez pas cette règle par une autorisation générale à toutes les adresses si le serveur ne doit être accessible que depuis des hôtes connus.

### 11.4 Vérifier les règles et la configuration

Depuis une session d'administration :

```sql
SHOW listen_addresses;
SHOW port;
SHOW hba_file;
SHOW config_file;
```

Vérifiez aussi les erreurs de lecture des règles :

```sql
SELECT *
FROM pg_hba_file_rules
WHERE error IS NOT NULL;
```

Après une modification de `pg_hba.conf`, demandez le rechargement nécessaire et vérifiez les logs. Une modification de `listen_addresses`, en revanche, demande un redémarrage.

### 11.5 Préparer un emplacement sûr pour le mot de passe

Sur le secondaire, le compte système qui exécute `pg_basebackup` ou le processus PostgreSQL doit pouvoir s'authentifier auprès du primaire.

Un fichier de mots de passe `.pgpass` peut être utilisé lorsque ce mécanisme convient à l'environnement. Il doit être accessible uniquement au compte prévu.

Exemple de format, sans secret réel :

```text
10.10.0.11:5432:replication:replicator:REMPLACER_PAR_UN_SECRET
```

Protégez le fichier :

```bash
chmod 600 ~/.pgpass
```

Le chemin du fichier doit correspondre à l'utilisateur qui exécute la commande. Les permissions appropriées sont importantes pour que le client l'accepte.

### 11.6 Créer une réplication de base

Sur un secondaire disposant d'un répertoire de données vide et prévu pour cette instance, utilisez `pg_basebackup`.

Exemple conceptuel :

```bash
pg_basebackup \
  -h 10.10.0.11 \
  -p 5432 \
  -U replicator \
  -D /chemin/vers/le/repertoire_de_donnees \
  -Fp \
  -Xs \
  -P \
  -R \
  -C \
  -S standby1_slot
```

Cette commande est un modèle. Le répertoire cible doit être vide, approprié à la version installée et accessible au compte système PostgreSQL. Ne l'exécutez pas sur le répertoire de données d'une instance en fonctionnement.

Les options utilisées sont :

- `-h` : hôte du primaire ;
- `-p` : port PostgreSQL ;
- `-U` : rôle utilisé pour la réplication ;
- `-D` : répertoire de destination ;
- `-Fp` : format de copie en arborescence ;
- `-Xs` : transfert du WAL nécessaire via le streaming pendant la sauvegarde ;
- `-P` : affichage de la progression ;
- `-R` : création de la configuration nécessaire pour démarrer comme standby ;
- `-C` : création du replication slot lorsqu'il n'existe pas ;
- `-S` : nom du replication slot utilisé.

Le primaire doit disposer des paramètres et privilèges nécessaires à cette opération, et la version des outils doit être compatible.

### 11.7 Démarrer le secondaire

La manière de démarrer l'instance dépend de la distribution et de sa gestion des clusters.

Sur une installation Debian utilisant les outils de gestion des clusters, il faut éviter de démarrer une deuxième instance sur les mêmes chemins de données et le même port.

Après démarrage du secondaire, contrôlez son état :

```sql
SELECT pg_is_in_recovery();
```

Un résultat `true` indique que le serveur est en mode de récupération, ce qui est normal pour un standby physique.

### 11.8 Comprendre les fichiers de configuration du standby

Dans les versions modernes de PostgreSQL, un fichier `standby.signal` signale le démarrage en mode standby.

La connexion au primaire est configurée notamment avec `primary_conninfo`. Un slot peut être indiqué au moyen de `primary_slot_name`.

`pg_basebackup -R` prépare normalement les éléments de configuration associés, mais il faut vérifier le résultat au lieu de supposer que tous les chemins et paramètres sont corrects.


## 12. Vérifier la réplication physique

### 12.1 Contrôle sur le primaire

Sur le primaire :

```sql
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;
```

Cette vue permet notamment d'identifier les secondaires connectés et d'observer leur état de réplication.

Les colonnes de retard temporel peuvent être nulles selon l'état de la connexion et le trafic récent. Il faut interpréter les métriques dans leur contexte.

### 12.2 Contrôle sur le secondaire

Sur le secondaire :

```sql
SELECT
    pg_is_in_recovery() AS est_standby,
    pg_last_wal_receive_lsn() AS dernier_wal_recu,
    pg_last_wal_replay_lsn() AS dernier_wal_rejoue,
    pg_last_xact_replay_timestamp() AS derniere_transaction_rejouee;
```

Ces fonctions donnent des informations relatives à la réception et au rejeu du WAL.

Une absence de transaction récente ne signifie pas nécessairement un problème si le primaire ne reçoit aucune écriture.

### 12.3 Mesurer un retard en octets

Sur le primaire :

```sql
SELECT
    application_name,
    state,
    pg_size_pretty(
        pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)
    ) AS retard_approximatif
FROM pg_stat_replication;
```

Cette mesure compare le LSN WAL courant du primaire avec celui que le secondaire a rejoué.

Elle constitue un indicateur de retard, mais ne fournit pas directement une mesure de la perte de données en secondes.

### 12.4 Retard en temps et retard en octets

Le retard peut être exprimé :

- en octets de WAL non encore rejoués ;
- en position logique de WAL ;
- au moyen d'indicateurs temporels ;
- par l'observation du délai de visibilité de certaines transactions.

Il n'existe pas de conversion universelle entre un nombre fixe d'octets et un temps de retard : cela dépend du débit de génération du WAL et du rythme de rejeu.

### 12.5 Contrôler les slots de réplication

Sur le primaire :

```sql
SELECT
    slot_name,
    slot_type,
    active,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;
```

La disponibilité des colonnes et leur pertinence dépendent notamment du type de slot.

Pour la réplication physique, `restart_lsn` est particulièrement utile pour comprendre la position à partir de laquelle des journaux peuvent être nécessaires.

### 12.6 Risque des replication slots

Un replication slot peut empêcher PostgreSQL de supprimer certains segments WAL tant qu'ils peuvent être nécessaires au client associé.

C'est utile pour éviter qu'un secondaire retardé perde des journaux indispensables.

Mais si le client reste longtemps déconnecté, le volume de WAL conservé peut augmenter et remplir le disque.

```text
Secondaire déconnecté
          |
          v
Slot retient des WAL
          |
          v
Accumulation dans pg_wal
          |
          v
Risque de saturation du stockage
```

Il faut surveiller les slots inactifs, le retard et l'espace disponible. `max_slot_wal_keep_size` peut servir à limiter certaines rétentions, mais son emploi doit être cohérent avec la stratégie de récupération et de resynchronisation.

Ne supprimez pas un replication slot sans comprendre quelle instance ou quel consommateur en dépend.


## 13. Contrôler la durabilité et le retard de réplication

### 13.1 Une réplication connectée n'est pas nécessairement à jour

Un secondaire peut être connecté sans avoir encore rejoué tout le WAL reçu.

Il est donc important de distinguer :

- la connexion au primaire ;
- la réception des données ;
- le flush sur le stockage ;
- le rejeu des WAL ;
- la visibilité des changements sur le secondaire.

Ces états peuvent différer dans le temps.

### 13.2 Suivre le retard selon le besoin métier

Pour une application de reporting, un léger retard peut être acceptable.

Pour une application qui lit immédiatement une écriture qu'elle vient d'effectuer, un retard peut provoquer une incohérence observable si la lecture est dirigée vers un secondaire asynchrone.

Les applications doivent tenir compte des garanties de cohérence du système.

### 13.3 Exemple de problème de lecture après écriture

```text
Client
  |
  | INSERT d'une commande
  v
Primaire
  |
  | Commit confirmé
  |
  | Réplication encore en cours
  v
Secondaire
  |
  | SELECT immédiat
  v
Commande temporairement absente
```

Ce comportement peut se produire avec une réplication asynchrone.

Pour certains parcours applicatifs, il faut diriger les lectures consécutives à une écriture vers le primaire, utiliser une stratégie de synchronisation ou concevoir une attente cohérente avec les garanties requises.

### 13.4 Ne pas confondre synchronisation et basculement

Le fait qu'une réplication soit synchrone peut améliorer certaines garanties de durabilité, mais le système doit quand même :

- empêcher les primaires concurrents ;
- déterminer un candidat de promotion valide ;
- orienter les nouvelles connexions ;
- reconnecter les clients ;
- traiter les requêtes interrompues ;
- restaurer la redondance après l'incident.


## 14. Le basculement : failover et switchover

### 14.1 Failover

Le *failover* est un basculement non planifié, généralement provoqué par une panne ou une situation qui rend le primaire inutilisable.

```text
                    AVANT
                 +----------+
                 | Primaire |
                 +----+-----+
                      |
                      v
                 +----------+
                 | Secondaire
                 +----------+

                    PANNE
                      |
                      v

                    APRÈS
                 +----------+
                 | Ancien   |
                 | primaire |
                 | isolé    |
                 +----------+

                 +----------+
                 | Nouveau  |
                 | primaire |
                 +----------+
```

La chronologie exacte dépend de la solution de gestion du cluster.

### 14.2 Switchover

Le *switchover* est un changement de rôle planifié.

Il peut être utilisé pour :

- effectuer une maintenance ;
- déplacer le primaire vers une autre machine ;
- rééquilibrer l'infrastructure ;
- préparer une mise à jour ;
- tester la procédure de basculement.

Un switchover correctement préparé permet généralement de vérifier que les composants savent changer de rôle sans dépendre d'une panne imprévisible.

### 14.3 Différence essentielle

| Critère | Failover | Switchover |
|---|---|---|
| Déclenchement | Panne ou situation imprévue | Décision planifiée |
| Préparation du transfert | Parfois limitée | Généralement organisée |
| Risque de perte selon le mode asynchrone | Peut être significatif | Peut être réduit par la préparation et la synchronisation |
| Objectif | Restaurer le service | Changer de rôle de manière contrôlée |

Un switchover doit être préparé et exécuté selon la procédure de la solution HA utilisée.

### 14.4 Les étapes générales d'un basculement

```text
1. Détection de l'incident
             |
             v
2. Vérification des conditions de promotion
             |
             v
3. Décision coordonnée du cluster
             |
             v
4. Exclusion de l'ancien primaire
             |
             v
5. Promotion du secondaire
             |
             v
6. Mise à jour du point d'accès SQL
             |
             v
7. Reconnexion des applications
             |
             v
8. Vérification des opérations métier
             |
             v
9. Réintégration ou reconstruction
   de l'ancien primaire
```

L'ancien primaire ne doit pas être autorisé à poursuivre des écritures concurrentes non contrôlées.


## 15. Le risque de split-brain : prévention et récupération

### 15.1 Scénario dangereux

Supposons que le primaire soit isolé du réseau de coordination, mais continue de fonctionner localement.

Le secondaire voit une perte de communication et souhaite devenir primaire.

```text
      Réseau A                      Réseau B
   +-------------+              +-------------+
   | Ancien P    |       X      | Secondaire  |
   | Peut écrire |              | Promu       |
   +-------------+              +-------------+
```

Si chacun accepte des écritures, les historiques des deux instances divergent.

La réplication physique normale ne fournit pas un mécanisme automatique de fusion de deux branches d'écritures indépendantes.

### 15.2 Les mécanismes de prévention

La conception doit inclure :

- un mécanisme de consensus ;
- un contrôle du droit d'être leader ;
- des délais cohérents ;
- une stratégie de fencing ;
- un mécanisme empêchant l'ancien primaire de continuer à accepter les écritures ;
- des procédures de bascule testées ;
- une politique de retour de l'ancien primaire.

### 15.3 Le rôle du watchdog

Dans certaines architectures Patroni, un watchdog peut renforcer la protection en déclenchant une action de sécurité lorsque le nœud ne peut plus respecter les conditions de leadership prévues.

Ce mécanisme dépend du matériel, du système d'exploitation, de la configuration et de la solution installée.

Un watchdog ne doit pas être considéré comme activé ou fonctionnel simplement parce que Patroni est installé. Il faut vérifier la configuration et tester le comportement dans un environnement sûr.

### 15.4 Règle opérationnelle

Ne lancez pas la promotion manuelle d'un secondaire simplement parce que le primaire ne répond plus depuis votre poste.

Avant une décision manuelle, il faut établir avec des moyens fiables que l'ancien primaire ne peut plus accepter de nouvelles écritures ou utiliser un mécanisme d'exclusion prévu et correctement configuré.

Une erreur dans cette étape peut créer une divergence de données bien plus difficile à résoudre que la panne initiale.


## 16. Patroni : configuration conceptuelle

La configuration exacte de Patroni dépend de la méthode d'installation, du DCS, des identifiants et des chemins du système.

L'exemple suivant présente les principales catégories de paramètres, sans constituer un fichier complet à copier directement dans une infrastructure réelle.

```yaml
scope: pg-ha
namespace: /service/
name: pg1

restapi:
  listen: 10.10.0.11:8008
  connect_address: 10.10.0.11:8008

etcd3:
  hosts:
    - 10.10.0.21:2379
    - 10.10.0.22:2379
    - 10.10.0.23:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576

    postgresql:
      use_pg_rewind: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        max_wal_senders: 10
        max_replication_slots: 10

postgresql:
  listen: 10.10.0.11:5432
  connect_address: 10.10.0.11:5432
  data_dir: /chemin/du/repertoire/de/donnees

  authentication:
    superuser:
      username: postgres
      password: A_REMPLACER
    replication:
      username: replicator
      password: A_REMPLACER
```

### 16.1 Explication des paramètres

`scope` identifie le cluster Patroni.

`namespace` définit l'espace de noms utilisé dans le DCS.

`name` identifie le nœud Patroni.

`restapi` configure l'interface de contrôle Patroni.

`etcd3` indique les membres du système de coordination utilisé dans cet exemple.

`ttl`, `loop_wait` et `retry_timeout` interviennent dans les temporisations de gestion du leadership et de la coordination.

`maximum_lag_on_failover` définit une limite de retard utilisée dans certaines décisions de basculement asynchrone. Il ne faut pas interpréter ce paramètre comme une garantie absolue de perte maximale de données dans tous les scénarios.

`use_pg_rewind` demande à Patroni d'utiliser `pg_rewind` lorsque les conditions de la procédure de réintégration le permettent.

`data_dir` identifie le répertoire de données utilisé par l'instance gérée.

Les noms, chemins et paramètres doivent correspondre à la version Patroni et à l'installation PostgreSQL.

### 16.2 Pourquoi les paramètres varient-ils d'un nœud à l'autre ?

Le `name`, les adresses d'écoute et les adresses de connexion doivent être adaptés à chaque machine.

Le rôle courant de primaire ou de secondaire est géré dynamiquement par Patroni. Il ne faut pas coder arbitrairement le même rôle statique dans tous les fichiers comme si le rôle ne devait jamais changer.

### 16.3 Sécurité des fichiers Patroni

Les fichiers de configuration peuvent contenir des secrets de connexion.

Il faut :

- limiter leur lecture au compte de service autorisé ;
- éviter de déposer les secrets dans un dépôt public ;
- protéger l'accès à l'API de contrôle ;
- utiliser TLS et une authentification appropriée pour les interfaces exposées sur un réseau non fiable ;
- vérifier les règles du pare-feu ;
- ne pas publier l'API Patroni à tous les clients Internet.

### 16.4 Initialisation de l'infrastructure

Avant le démarrage d'un cluster Patroni, il faut notamment :

1. préparer les serveurs et leurs répertoires ;
2. installer des versions compatibles de PostgreSQL et Patroni ;
3. configurer le DCS ;
4. sécuriser les connexions ;
5. préparer le stockage ;
6. définir les paramètres du cluster ;
7. valider les fichiers de configuration ;
8. démarrer le premier nœud selon la procédure d'initialisation ;
9. ajouter les autres nœuds ;
10. vérifier leur état avant d'exposer l'application.

Une mauvaise configuration au démarrage peut initialiser le mauvais nœud ou le mauvais répertoire. L'état existant du système doit donc être vérifié avant toute opération d'initialisation.


## 17. Observer l'état du cluster Patroni

### 17.1 Utiliser patronictl

`patronictl` est un outil de gestion de clusters Patroni.

Suivant l'installation, la configuration et la disponibilité des informations dans le DCS :

```bash
patronictl -c /chemin/vers/patroni.yml list
```

Cette commande permet d'afficher les informations sur les membres, leurs rôles et leur état.

Le chemin fourni est un exemple.

### 17.2 Ce qu'il faut contrôler

Un contrôle utile doit notamment vérifier :

- quel nœud est primaire ;
- quels nœuds sont secondaires ;
- si les instances sont accessibles ;
- si les connexions de réplication sont actives ;
- si le DCS fonctionne ;
- si un nœud est en retard ;
- si un candidat peut être promu selon les règles du cluster.

Un simple état `running` ne démontre pas que le cluster est prêt à basculer sans perte ou sans interruption significative.

### 17.3 API REST de Patroni

Patroni expose une API REST dont les endpoints peuvent fournir des informations sur le rôle et l'état d'une instance.

Par exemple, le endpoint :

```text
/primary
```

peut servir au contrôle de l'état primaire et de son statut de leader selon la configuration Patroni.

Une requête de test pourrait prendre cette forme :

```bash
curl -i http://10.10.0.11:8008/primary
```

L'adresse et le port sont des exemples.

L'API doit être accessible uniquement depuis les systèmes autorisés. Un endpoint utilisé pour la supervision ne doit pas être exposé sans nécessité.


## 18. HAProxy : diriger les connexions vers le primaire

Une application a besoin d'un point d'accès stable. Elle ne devrait pas avoir à décider elle-même lequel des serveurs PostgreSQL est actuellement primaire.

HAProxy peut utiliser les informations d'état fournies par Patroni pour sélectionner le bon nœud.

### 18.1 Architecture

```text
APPLICATION
    |
    | Connexion SQL
    v
+----------------------+
| HAProxy              |
| Point d'accès SQL    |
+----------+-----------+
           |
           | Vérification du rôle
           |
   +-------+-------+-------+
   |               |       |
   v               v       v
+------+         +------+ +------+
| PG 1 |         | PG 2 | | PG 3 |
| P?   |         | R?   | | R?   |
+------+         +------+ +------+

P? = rôle primaire possible selon l'état
R? = rôle secondaire possible selon l'état
```

L'objectif est de choisir le primaire courant pour l'accès en écriture.

### 18.2 Exemple conceptuel de configuration HAProxy

L'exemple suivant est un modèle de backend PostgreSQL utilisant le endpoint Patroni comme contrôle d'état.

```haproxy
frontend postgres_rw
    bind *:5000
    mode tcp
    default_backend postgres_primary

backend postgres_primary
    mode tcp

    option httpchk GET /primary
    http-check expect status 200

    default-server inter 2s fall 3 rise 2

    server pg1 10.10.0.11:5432 check port 8008
    server pg2 10.10.0.12:5432 check port 8008
    server pg3 10.10.0.13:5432 check port 8008
```

Cette configuration illustre le principe : le trafic SQL est dirigé vers le serveur qui est considéré comme primaire par les vérifications de Patroni.

Les adresses sont des exemples. La configuration complète doit respecter la syntaxe de la version HAProxy utilisée, l'interface de contrôle Patroni et les règles réseau autorisées.

### 18.3 Pourquoi le contrôle doit-il vérifier le rôle ?

Un simple contrôle TCP sur le port 5432 peut indiquer que PostgreSQL accepte une connexion, y compris lorsque l'instance est un secondaire.

Ce contrôle ne suffit donc pas à sélectionner le primaire destiné aux écritures.

Un contrôle fondé sur le rôle permet de distinguer les instances qui sont joignables de celles qui sont effectivement admissibles pour l'accès en écriture.

### 18.4 Valider la configuration

Avant de recharger HAProxy :

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg
```

Puis appliquez la configuration selon le mécanisme de gestion du service prévu par la distribution.

Il faut également superviser HAProxy, ses contrôles de santé et les journaux des connexions.

### 18.5 Redonder le point d'accès

Un HAProxy unique peut devenir un point de défaillance.

Dans une infrastructure exigeant une disponibilité élevée, une stratégie courante est d'avoir plusieurs instances HAProxy derrière un point d'accès réseau redondant, une adresse virtuelle ou un service de répartition externe.

Une adresse virtuelle et Keepalived peuvent contribuer à fournir un point d'accès stable dans certains environnements, mais ils ne remplacent ni le gestionnaire de cluster PostgreSQL ni les contrôles de fencing.


## 19. Séparer les connexions en lecture et en écriture

Certaines applications peuvent envoyer les écritures au primaire et certaines lectures à des secondaires.

Cette stratégie doit être conçue en fonction des besoins de cohérence.

### 19.1 Principe

```text
               APPLICATION
                    |
           +--------+--------+
           |                 |
           v                 v
     Connexions RW      Connexions RO
           |                 |
           v                 v
       Primaire         Secondaires
           |                 |
           +------ WAL ------+
```

### 19.2 Endpoint de lecture

HAProxy peut utiliser un endpoint de santé qui identifie les réplicas admissibles pour la lecture, par exemple `/replica`, selon la configuration Patroni.

Un backend de lecture doit être configuré séparément et testé avec des requêtes réellement accessibles en lecture.

Les secondaires peuvent avoir un retard de réplication. Une lecture effectuée immédiatement après une écriture peut donc ne pas voir la dernière modification.

### 19.3 Cohérence après écriture

Lorsqu'un utilisateur crée une commande, il peut attendre de la retrouver immédiatement dans l'écran suivant.

Si la première requête est envoyée au primaire puis que la lecture est immédiatement dirigée vers un secondaire asynchrone, la commande peut ne pas encore y être visible.

Les solutions possibles dépendent de l'application :

- diriger certaines lectures vers le primaire ;
- utiliser une règle de routage fondée sur le parcours de la requête ;
- mettre en place un mécanisme de synchronisation approprié ;
- accepter explicitement une cohérence éventuellement différée.

La répartition des lectures ne doit pas être ajoutée sans examiner ces conséquences.

### 19.4 Attention aux sessions SQL

Une connexion déjà ouverte vers un serveur qui change de rôle ne se transforme pas automatiquement en connexion fonctionnelle vers le nouveau primaire.

Les applications et leurs pools de connexions doivent savoir gérer les erreurs et reconnecter les clients.

Le routage des nouvelles connexions et la récupération des connexions existantes sont deux aspects différents du basculement.


## 20. Gérer les pools de connexions avec PgBouncer

Les connexions PostgreSQL consomment des ressources. Lorsque de nombreuses applications ouvrent simultanément des sessions, il peut être utile d'interposer un pool de connexions.

PgBouncer est un outil couramment utilisé à cette fin.

### 20.1 Architecture

```text
APPLICATIONS
     |
     v
+------------------+
| PgBouncer        |
| Pool de sessions |
+--------+---------+
         |
         v
+------------------+
| HAProxy          |
| Routage vers P   |
+--------+---------+
         |
         v
   PostgreSQL
```

L'ordre exact des composants dépend de l'architecture. Dans certaines installations, le routage du rôle et le pooling sont organisés différemment.

### 20.2 Les modes de pooling

PgBouncer propose notamment plusieurs modes de pooling, dont :

- session ;
- transaction ;
- statement.

Ils ne sont pas interchangeables.

Le pooling par transaction permet de réutiliser une connexion serveur après la fin d'une transaction, mais certaines fonctionnalités dépendantes de l'état de session doivent alors être examinées avec attention.

Le mode adapté dépend des exigences de l'application et de sa façon d'utiliser PostgreSQL.

### 20.3 Connexions et basculement

Lorsqu'un primaire tombe, les connexions PostgreSQL qui lui étaient associées peuvent être interrompues.

Le pool doit traiter ces erreurs, abandonner ou recréer les connexions selon son mode de fonctionnement et la stratégie prévue.

PgBouncer n'est pas, à lui seul, un gestionnaire de basculement PostgreSQL. Il doit être associé à un point d'accès ou à un mécanisme de découverte du primaire qui reste correct après une promotion.

### 20.4 Risques à examiner

Avant l'utilisation en production, vérifiez :

- le comportement des transactions ;
- les requêtes préparées ;
- les paramètres de session ;
- les limites de pool ;
- la gestion des délais ;
- les erreurs lors d'une coupure ;
- la capacité de reconnexion après basculement.

Un pool mal dimensionné peut devenir un nouveau goulot d'étranglement.


## 21. Le basculement contrôlé avec PostgreSQL

Cette section explique le principe de la promotion d'un secondaire sans Patroni. Dans une architecture gérée par Patroni, il faut normalement utiliser les mécanismes Patroni prévus pour l'administration du cluster plutôt que lancer directement des opérations PostgreSQL qui contournent sa coordination.

### 21.1 Promotion d'un standby

PostgreSQL propose notamment la fonction :

```sql
SELECT pg_promote();
```

Elle permet de demander la promotion d'un serveur en récupération vers un rôle primaire.

Elle ne doit pas être invoquée simplement parce qu'un primaire ne répond plus à une tentative de connexion.

Avant une promotion manuelle, il faut notamment :

1. vérifier l'état des nœuds ;
2. s'assurer que le primaire précédent est réellement empêché d'écrire ;
3. identifier le secondaire admissible ;
4. évaluer le retard de réplication ;
5. documenter la décision ;
6. prévoir la mise à jour du point d'accès.

### 21.2 Promotion et cohérence

Un secondaire peut avoir reçu et rejoué une partie du WAL, mais ne pas être parfaitement à jour.

Dans un modèle asynchrone, la promotion d'un secondaire peut donc entraîner une perte de transactions qui n'ont jamais atteint ce secondaire.

Un basculement doit prendre en compte l'objectif de durabilité défini pour l'application.

### 21.3 Vérifier le nouveau primaire

Après une promotion manuelle contrôlée :

```sql
SELECT pg_is_in_recovery();
```

Un résultat `false` indique que le serveur n'est plus en mode de récupération.

Il faut ensuite vérifier que le service est accessible, que les connexions sont rétablies et que les opérations métier répondent correctement.

### 21.4 Pourquoi ne pas réactiver immédiatement l'ancien primaire ?

L'ancien primaire peut conserver un historique de WAL différent de celui du nouveau primaire.

Le démarrer simplement en espérant qu'il se synchronise n'est pas une procédure de réintégration sûre.

Il faut vérifier son état, son historique de timeline et la procédure nécessaire pour le faire rejoindre le cluster au bon rôle.


## 22. Réintégrer un ancien primaire avec pg_rewind

### 22.1 Pourquoi une réintégration est-elle nécessaire ?

Après une promotion, les historiques du serveur promu et de l'ancien primaire peuvent diverger.

La réplication physique ne permet pas de fusionner automatiquement deux branches d'écriture.

Une solution consiste à réinitialiser l'ancien primaire à partir d'une copie cohérente. Dans certaines situations, `pg_rewind` peut rapprocher un cluster qui a divergé du nouveau primaire.

### 22.2 Conditions d'utilisation

`pg_rewind` n'est pas une commande universelle de réparation.

Son utilisation dépend notamment :

- de la version PostgreSQL ;
- de l'état du cluster cible ;
- de la possibilité de déterminer les blocs modifiés depuis la divergence ;
- des prérequis de configuration, comme les sommes de contrôle des pages ou `wal_log_hints` selon le cas ;
- de la disponibilité des WAL nécessaires ;
- des conditions de cohérence et de compatibilité entre les clusters.

Les conditions exactes doivent être vérifiées dans la documentation de la version installée.

### 22.3 Exemple conceptuel

```text
Ancien primaire
      |
      | Historique initial commun
      |
      +-------------------+
      |                   |
      v                   v
 Nouveau primaire     Ancien primaire
      |                   |
      v                   v
 Nouvelles écritures  Anciennes écritures
      |                   |
      +----- Divergence --+
                 |
                 v
       Réintégration contrôlée
                 |
                 v
        pg_rewind ou reconstruction
                 |
                 v
       Ancien nœud redevenu standby
```

### 22.4 Prudence avec les données divergentes

Les écritures apparues uniquement sur l'ancien primaire peuvent ne pas être présentes dans l'historique retenu après le basculement.

Elles ne doivent pas être écrasées sans analyse lorsque leur valeur métier doit être conservée.

Si la divergence ne peut pas être traitée correctement avec `pg_rewind`, il peut être nécessaire de reconstruire le secondaire à partir du nouveau primaire et de traiter séparément les données qui doivent être récupérées.

### 22.5 Règle avec Patroni

Lorsque Patroni gère le cluster, utilisez sa procédure de réintégration et ses contrôles d'état.

Ne contournez pas arbitrairement son mécanisme de gestion du rôle en lançant des commandes de promotion ou de réinitialisation sans vérifier les conséquences sur le DCS et sur l'état de l'instance.


## 23. Sauvegardes physiques et pgBackRest

La haute disponibilité doit être complétée par une stratégie de sauvegarde indépendante.

pgBackRest est un outil de sauvegarde et de restauration PostgreSQL qui peut gérer notamment des sauvegardes complètes, différentielles ou incrémentales selon la configuration.

Il peut également s'intégrer à l'archivage WAL pour des stratégies de récupération plus avancées.

### 23.1 Architecture recommandée

```text
                   PostgreSQL
                       |
                       | Sauvegardes et WAL
                       v
               +------------------+
               | pgBackRest       |
               +---------+--------+
                         |
                         v
               +------------------+
               | Dépôt distant    |
               | Protégé           |
               +---------+--------+
                         |
                         v
                 Restauration test
```

Le dépôt doit être indépendant du volume principal de PostgreSQL.

Un dépôt distant, un stockage objet ou un autre stockage séparé peut être utilisé selon les exigences de l'organisation.

### 23.2 Pourquoi stocker les sauvegardes ailleurs ?

Si le primaire et ses sauvegardes sont sur le même disque, une panne de ce disque peut supprimer les deux.

Pour les systèmes sensibles, il faut également protéger les sauvegardes contre les erreurs administratives, la suppression accidentelle et les accès non autorisés.

### 23.3 Configurer l'archivage WAL

Dans une configuration utilisant pgBackRest, un modèle de paramètres peut être :

```conf
archive_mode = on
archive_command = 'pgbackrest --stanza=prod archive-push %p'
```

Cet exemple ne fonctionne que si pgBackRest est réellement installé et configuré avec une stanza et un dépôt adaptés.

L'activation de `archive_mode` nécessite un redémarrage de PostgreSQL. Vérifiez la documentation et la configuration de votre version avant de modifier le service.

### 23.4 Vérifier l'archivage

Dans PostgreSQL :

```sql
SELECT
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count,
    last_failed_wal,
    last_failed_time
FROM pg_stat_archiver;
```

Cette vue fournit des indicateurs utiles sur l'archivage.

Un nombre élevé d'échecs ou une date d'archivage qui ne progresse pas alors que le WAL est généré mérite une investigation.

Une absence d'archivage récent n'est pas nécessairement une erreur si aucun nouveau segment n'a été archivé récemment, mais il faut la mettre en relation avec le trafic, les journaux et l'état de la configuration.

### 23.5 Créer une sauvegarde

Avec pgBackRest, une opération de sauvegarde suit la configuration préalable du dépôt et de la stanza.

Exemple de commande :

```bash
sudo -u postgres pgbackrest --stanza=prod backup
```

Le nom `prod` est un exemple. La commande exige une configuration existante et valide.

### 23.6 Contrôler l'état du dépôt

```bash
sudo -u postgres pgbackrest --stanza=prod info
```

Cette commande permet d'examiner les sauvegardes et les informations de dépôt disponibles selon la configuration.

La présence d'une archive ne remplace pas un test de restauration.


## 24. PITR : restauration à un point dans le temps

### 24.1 Pourquoi le PITR est-il nécessaire ?

Une réplication protège contre certaines pannes de serveur, mais elle peut transmettre une modification erronée.

Une restauration PITR permet, avec les sauvegardes et WAL nécessaires, de récupérer une base à un point précis avant une erreur.

Exemple :

```text
08:00  Sauvegarde cohérente
08:10  Transactions normales
08:20  Suppression accidentelle validée
08:25  Incident détecté

Objectif :
Restaurer un environnement à un point
avant la suppression accidentelle.
```

### 24.2 Éléments nécessaires

Une stratégie PITR nécessite notamment :

- une sauvegarde physique de base compatible ;
- les WAL nécessaires depuis cette sauvegarde jusqu'au point souhaité ;
- une configuration de récupération correcte ;
- de l'espace de stockage suffisant ;
- une procédure de validation de l'état restauré.

### 24.3 Pourquoi tester la restauration ?

Une sauvegarde peut sembler correcte mais être inutilisable à cause de :

- WAL manquants ;
- erreurs de stockage ;
- fichiers corrompus ;
- privilèges incorrects ;
- mauvaise configuration de récupération ;
- incompatibilité de versions ou d'extensions ;
- procédure de restauration incomplète.

Une restauration de test doit vérifier la cohérence des données et les opérations métier importantes.

### 24.4 Ne pas confondre restauration et basculement

Le basculement cherche à reprendre le service à partir d'un secondaire existant.

Le PITR cherche à restaurer un état antérieur à partir d'une sauvegarde et des journaux nécessaires.

Le premier répond généralement à une panne d'instance. Le second est notamment utile pour récupérer après une erreur logique ou certains incidents majeurs.


## 25. Supervision d'un cluster PostgreSQL HA

Une architecture haute disponibilité nécessite une supervision de plusieurs couches.

### 25.1 État du primaire et des secondaires

Sur le primaire, la vue `pg_stat_replication` permet d'examiner les connexions de réplication.

Sur les secondaires, les fonctions liées au WAL permettent d'observer la réception, le rejeu et l'état de récupération.

Il faut également connaître le résultat des contrôles du gestionnaire de cluster.

### 25.2 Surveillance de la capacité

Les métriques importantes comprennent :

- CPU ;
- mémoire disponible ;
- pression mémoire ;
- espace disque ;
- débit I/O ;
- débit de génération WAL ;
- taille de `pg_wal` ;
- nombre de connexions ;
- requêtes lentes ;
- transactions longues ;
- taux d'erreur ;
- retard de réplication.

Une surveillance de la seule disponibilité TCP n'est pas suffisante.

### 25.3 Surveiller les connexions

```sql
SELECT
    datname,
    state,
    COUNT(*) AS nombre
FROM pg_stat_activity
GROUP BY datname, state
ORDER BY nombre DESC;
```

Cette requête permet de repérer la répartition des sessions par base et état.

Un grand nombre de connexions inactives peut être normal dans certains environnements. Il faut comparer les valeurs observées aux limites et au comportement de l'application.

### 25.4 Surveiller les verrous

```sql
SELECT
    pid,
    usename,
    datname,
    wait_event_type,
    wait_event,
    pg_blocking_pids(pid) AS bloqueurs,
    LEFT(query, 150) AS extrait_requete
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```

Cette requête aide à identifier les sessions bloquées.

Les blocages doivent être analysés avant de terminer des sessions. Une transaction interrompue peut provoquer une erreur applicative et annuler des opérations.

### 25.5 Surveiller l'espace disque

```bash
df -h
```

Dans PostgreSQL :

```sql
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS taille
FROM pg_database
ORDER BY pg_database_size(datname) DESC;
```

Le système doit être surveillé pour l'espace restant sur les volumes qui hébergent les données, les WAL, les journaux et les sauvegardes.

### 25.6 Surveiller les erreurs d'archivage

```sql
SELECT
    archived_count,
    failed_count,
    last_archived_time,
    last_failed_time
FROM pg_stat_archiver;
```

L'absence de progression ou des échecs répétés doivent déclencher une vérification de l'archivage, du stockage et des permissions.

### 25.7 Alertes essentielles

Les alertes devraient notamment couvrir :

- primaire absent ou état de cluster incohérent ;
- secondaire déconnecté ;
- retard de réplication supérieur au seuil prévu ;
- absence de quorum DCS ;
- échecs d'archivage WAL ;
- dépôt de sauvegarde indisponible ;
- espace disque critique ;
- croissance anormale des WAL retenus ;
- hausse des transactions longues ;
- échec d'une sauvegarde planifiée ;
- échec d'un test de restauration.

Les seuils doivent être définis à partir des objectifs opérationnels et des mesures réelles.


## 26. Préparer un basculement contrôlé

Un basculement ne doit pas être traité comme une opération improvisée.

### 26.1 Préparer le test

Avant un test, documentez :

- le nœud primaire ;
- les nœuds secondaires ;
- l'état du DCS ;
- le niveau de réplication ;
- le point d'accès SQL ;
- les applications connectées ;
- la procédure de retour à l'état nominal.

Utilisez un environnement de formation qui ne porte pas de données critiques.

### 26.2 Vérifier l'état initial

Examinez l'état du cluster :

```bash
patronictl -c /chemin/vers/patroni.yml list
```

Vérifiez aussi l'état PostgreSQL, les journaux, le retard de réplication et les contrôles de santé.

Ne lancez pas une simulation de panne si le cluster est déjà dégradé.

### 26.3 Effectuer un switchover avec Patroni

Pour un changement de rôle planifié, utilisez la commande de switchover prise en charge par votre version Patroni.

La commande exacte et ses options doivent être vérifiées dans la documentation installée et dans l'aide de l'outil.

Un switchover doit être exécuté uniquement après vérification de l'état des nœuds et des conséquences attendues. Il ne faut pas combiner une expérimentation d'administration et des modifications non documentées sur le DCS.

### 26.4 Contrôler après le switchover

Vérifiez :

1. le nouveau rôle de chaque nœud ;
2. l'état de réplication ;
3. les contrôles HAProxy ;
4. la connexion d'une application ;
5. une lecture de données ;
6. une opération d'écriture de test appropriée ;
7. les journaux et les erreurs ;
8. le retour de la redondance.

L'objectif est de confirmer le bon fonctionnement de toute la chaîne, et pas uniquement que la promotion SQL a réussi.


## 27. Tester une panne et valider le failover

### 27.1 Test contrôlé dans un laboratoire

Un test de panne doit simuler un scénario défini et prévoir une procédure de récupération.

Exemples de scénarios :

- arrêt contrôlé du processus PostgreSQL du primaire ;
- perte de communication entre un nœud et le DCS ;
- arrêt d'un secondaire ;
- indisponibilité temporaire de HAProxy ;
- panne d'accès au dépôt de sauvegarde ;
- manque d'espace disque simulé dans un environnement dédié.

Ne provoquez pas ces incidents sur une infrastructure de production sans plan de test approuvé.

### 27.2 Chronologie du test

```text
T0 : état nominal vérifié
 |
 v
T1 : incident simulé
 |
 v
T2 : incident détecté
 |
 v
T3 : décision de basculement
 |
 v
T4 : nouveau primaire disponible
 |
 v
T5 : point d'accès mis à jour
 |
 v
T6 : application rétablie
 |
 v
T7 : redondance restaurée
```

Enregistrez les heures réelles observées. Elles permettront de mesurer les composantes du RTO.

### 27.3 Mesurer le temps d'indisponibilité

Pour un test contrôlé, mesurez le temps qui sépare :

- le début de l'incident ;
- la première connexion réussie au nouveau primaire ;
- la première opération métier réussie ;
- le retour à une situation redondante.

Ces durées sont différentes.

Un service peut répondre avant que tous les secondaires aient retrouvé un retard acceptable.

### 27.4 Vérifier les données après le basculement

Comparez les opérations de test attendues, les enregistrements importants et l'état du nouveau primaire.

Si le mode de réplication est asynchrone, il faut analyser la possibilité de transactions validées qui n'auraient pas atteint le secondaire promu.

Un test de basculement ne doit pas conclure à une absence de perte simplement parce que quelques enregistrements de test sont encore présents.

### 27.5 Documenter le résultat

Un rapport de test doit inclure :

- le scénario ;
- le nœud touché ;
- l'état initial ;
- les horodatages ;
- le RTO observé ;
- le retard de réplication au moment de la panne ;
- le comportement du point d'accès ;
- les erreurs de l'application ;
- la perte éventuelle de données ;
- le temps de retour à la redondance ;
- les écarts par rapport aux objectifs.


## 28. Réintégrer le cluster après un incident

### 28.1 Pourquoi le retour à la normale est important

Après un basculement, le service peut fonctionner sur le nouveau primaire, mais l'ancienne architecture n'est pas forcément entièrement rétablie.

Il peut rester :

- un ancien primaire arrêté ;
- un secondaire en retard ;
- un slot qui retient des WAL ;
- un nœud dont l'état est inconnu ;
- une configuration de routage à contrôler ;
- une sauvegarde ou un archivage en échec.

### 28.2 Exemple de retour à la normale

```text
Avant la panne :
Primaire A + Secondaires B et C

Après basculement :
Primaire B + Secondaire C + Ancien primaire A isolé

Après réintégration :
Primaire B + Secondaires A et C
```

Ce schéma représente le résultat souhaité, pas une garantie que la réintégration sera automatique ou immédiate.

### 28.3 Vérification avant réintégration

Avant de redémarrer ou de réutiliser l'ancien primaire :

- vérifiez qu'il ne peut plus accepter d'écritures indépendantes ;
- vérifiez le rôle courant du cluster ;
- examinez les historiques et le retard ;
- choisissez la méthode de réintégration documentée ;
- contrôlez la place disponible ;
- vérifiez l'authentification et les paramètres de réplication.

### 28.4 Ne pas réintégrer deux primaires

Deux instances issues de branches divergentes ne doivent pas être mises en service comme si elles étaient déjà synchronisées.

La réintégration doit permettre à l'ancien primaire de rejoindre le nouveau primaire dans un rôle de secondaire, après une reconstruction ou un repositionnement approprié de ses données.


## 29. Haute disponibilité sur plusieurs sites

### 29.1 Pourquoi la géographie compte

Deux serveurs placés dans la même salle peuvent partager les mêmes risques :

- alimentation électrique ;
- climatisation ;
- switch réseau ;
- stockage partagé ;
- panne de l'hôte physique ;
- incident dans le bâtiment.

Répartir les serveurs dans plusieurs domaines de panne peut améliorer la résilience, mais ajoute également des contraintes de latence et de réseau.

### 29.2 Architecture multi-site

```text
                 SITE A
            +----------------+
            | PostgreSQL P   |
            | Patroni         |
            +-------+--------+
                    |
                    | Réplication
                    |
            +-------v--------+
            | SITE B         |
            | PostgreSQL S   |
            | Patroni        |
            +----------------+

       DCS réparti sur des domaines
       de panne indépendants
```

Ce schéma est conceptuel. Dans une architecture multi-site réelle, le placement des membres du DCS, du stockage, des serveurs PostgreSQL et du point d'accès doit être conçu ensemble.

### 29.3 Latence réseau

La réplication synchrone ajoute une dépendance à la latence du réseau entre le primaire et les secondaires synchrones.

Si un secondaire synchrone est situé dans une zone géographiquement éloignée, les validations d'écriture peuvent être sensiblement retardées.

Il faut mesurer le temps aller-retour, le débit WAL et le comportement lors de la perte d'un site.

### 29.4 Perte d'un site

Une perte de communication avec un site ne prouve pas que les serveurs de ce site sont arrêtés.

Un site peut continuer de fonctionner localement tout en étant isolé.

La promotion du site distant doit donc s'appuyer sur un mécanisme de coordination et de fencing qui évite un double primaire.

### 29.5 Retour d'un site isolé

Lorsqu'un ancien site redevient accessible, il ne faut pas supposer que son ancien primaire peut simplement reprendre les écritures.

L'instance doit être réintégrée selon la procédure prévue, et il peut être nécessaire de la reconstruire comme secondaire à partir du primaire actuel.


## 30. Plan de maintenance d'un cluster HA

### 30.1 Contrôles quotidiens

Un contrôle quotidien peut vérifier :

- l'état du primaire ;
- l'état des secondaires ;
- la santé du DCS ;
- le retard de réplication ;
- l'espace disque ;
- le statut de l'archivage WAL ;
- les journaux d'erreurs ;
- les sauvegardes récentes ;
- le fonctionnement des contrôles HAProxy.

### 30.2 Contrôles hebdomadaires

Selon les besoins, les contrôles hebdomadaires peuvent comprendre :

- le contrôle des transactions longues ;
- l'examen des connexions et blocages ;
- la tendance de croissance des bases ;
- le retard de réplication aux heures de pointe ;
- le volume des WAL retenus ;
- les anomalies de maintenance ;
- la vérification des rôles et privilèges.

### 30.3 Contrôles périodiques

Des opérations périodiques peuvent porter sur :

- la restauration complète d'une sauvegarde dans un environnement de test ;
- le test de switchover ;
- le test de failover selon la politique d'exploitation ;
- la procédure de réintégration d'un nœud ;
- les mises à jour logicielles ;
- la vérification des procédures de reprise ;
- la révision des objectifs RPO et RTO.

### 30.4 Les mises à jour

Une mise à jour PostgreSQL ou Patroni peut modifier le comportement de certaines fonctionnalités, les paramètres disponibles ou les procédures d'exploitation.

Avant un changement important :

1. identifier les versions installées ;
2. lire les notes de version ;
3. vérifier les compatibilités ;
4. effectuer un test de mise à jour ;
5. vérifier les sauvegardes ;
6. tester la réplication ;
7. préparer le retour arrière ;
8. mettre à jour la documentation d'exploitation.

Les mises à niveau majeures PostgreSQL exigent notamment une stratégie de migration appropriée. Une mise à niveau des paquets ne doit pas être assimilée à une migration complète de cluster.


## 31. Préparer un plan de reprise après incident

Une procédure de reprise doit définir à l'avance qui fait quoi, dans quel ordre et selon quels contrôles.

### 31.1 Classification des incidents

| Incident | Réponse initiale |
|---|---|
| Panne du primaire | Vérifier l'état, la coordination et le candidat à la promotion |
| Retard élevé d'un secondaire | Identifier la cause réseau, la charge ou le retard de rejeu |
| Perte du DCS | Vérifier le quorum et les conditions de sécurité avant toute action |
| Saturation du disque | Identifier les fichiers responsables et protéger les journaux nécessaires |
| Échec d'archivage WAL | Examiner la destination, les permissions et les files d'archivage |
| Erreur logique de données | Évaluer la restauration PITR et les besoins de récupération |
| Perte complète du site | Activer la procédure de reprise multi-site prévue |
| Ancien primaire divergent | Isoler l'instance et préparer sa réintégration contrôlée |

### 31.2 Ordre des opérations

```text
1. Détecter et qualifier l'incident
                 |
                 v
2. Protéger l'état restant
                 |
                 v
3. Identifier le primaire effectif
                 |
                 v
4. Évaluer le retard et le risque de perte
                 |
                 v
5. Choisir failover ou restauration
                 |
                 v
6. Rétablir le point d'accès
                 |
                 v
7. Tester les opérations métier
                 |
                 v
8. Restaurer la redondance
                 |
                 v
9. Documenter et corriger les causes
```

### 31.3 Une reprise doit être validée par l'application

Un état SQL accessible ne suffit pas.

Il faut aussi vérifier les opérations métier importantes, les écritures, les lectures, les connexions, les erreurs et les dépendances.

Dans un système de commandes, par exemple, la récupération peut nécessiter une vérification des dernières transactions, des statuts et de l'intégrité des enregistrements associés.


## 32. Travaux pratiques guidés

Les exercices suivants sont conçus pour un laboratoire. Utilisez des machines de test et des données non critiques.

Le modèle d'environnement comprend, selon les exercices :

- deux serveurs PostgreSQL ;
- un réseau privé ;
- un client SQL ;
- une sauvegarde indépendante.

Les exercices utilisant Patroni, un DCS et HAProxy exigent une installation préalablement configurée selon la documentation des composants.

### TP 1 — Identifier les rôles PostgreSQL

Sur le serveur de laboratoire :

```bash
sudo -u postgres psql
```

Puis :

```sql
SELECT
    current_database(),
    current_user,
    version();
```

Ensuite :

```sql
SELECT pg_is_in_recovery();
```

**Objectif :** apprendre à identifier le serveur courant et son état de récupération.

**Résultat attendu :** le serveur primaire renvoie normalement `false`, tandis qu'un secondaire physique en récupération renvoie normalement `true`.

### TP 2 — Vérifier les connexions de réplication

Sur le primaire :

```sql
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;
```

**Objectif :** repérer les secondaires connectés et examiner leur état.

**Résultat attendu :** les informations de réplication correspondent aux nœuds réellement connectés. Dans une architecture sans réplica connecté, aucune ligne correspondant à un secondaire actif ne sera nécessairement affichée.

### TP 3 — Examiner le retard

Sur le primaire :

```sql
SELECT
    application_name,
    state,
    pg_size_pretty(
        pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)
    ) AS retard_approx
FROM pg_stat_replication;
```

**Objectif :** comprendre le retard en position WAL.

**Résultat attendu :** les valeurs donnent une estimation de la distance entre le WAL courant et le WAL rejoué sur le secondaire.

Interprétez le résultat avec les métriques temporelles et l'activité du serveur. Une distance faible ne prouve pas à elle seule qu'il n'y aura aucune perte en cas de basculement.

### TP 4 — Vérifier le rôle du serveur

Sur chaque nœud PostgreSQL :

```sql
SELECT
    inet_server_addr(),
    inet_server_port(),
    pg_is_in_recovery();
```

**Objectif :** vérifier l'adresse, le port et l'état de récupération du serveur.

**Résultat attendu :** les nœuds montrent des adresses différentes et leur état correspond à leur rôle effectif.

### TP 5 — Examiner l'état Patroni

Sur l'environnement Patroni :

```bash
patronictl -c /chemin/vers/patroni.yml list
```

**Objectif :** identifier le leader et les secondaires.

**Résultat attendu :** le nœud primaire est clairement identifié et les secondaires affichent leur état de suivi. Un nœud déconnecté ou en retard doit faire l'objet d'une investigation.

### TP 6 — Vérifier le contrôle HAProxy

Testez la configuration avant application :

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg
```

Vérifiez ensuite l'accès SQL via le point d'entrée prévu :

```bash
psql -h ADRESSE_HAPROXY -p 5000 -U boutique_app -d boutique_sql
```

Remplacez les paramètres par ceux de votre laboratoire.

**Objectif :** vérifier que les connexions applicatives utilisent l'entrée prévue plutôt qu'une adresse de nœud codée en dur.

### TP 7 — Simuler un switchover

Dans un laboratoire opérationnel Patroni :

1. vérifier que tous les nœuds sont en état nominal ;
2. enregistrer le nœud primaire actuel ;
3. vérifier que le secondaire candidat est à jour selon les critères définis ;
4. effectuer un switchover planifié avec la procédure de la version installée ;
5. observer le nouveau primaire ;
6. tester une connexion via HAProxy ;
7. vérifier la réplication ;
8. vérifier que le cluster possède de nouveau une redondance.

**Objectif :** valider le changement planifié de rôle.

Ne lancez pas de commandes de promotion manuelle en parallèle du switchover Patroni.

### TP 8 — Tester une perte de connexion applicative

Utilisez une application de test qui se connecte au point d'accès SQL HAProxy.

Effectuez un switchover dans le cadre du TP précédent, puis observez :

- les connexions interrompues ;
- le comportement du pool applicatif ;
- les nouvelles connexions ;
- les erreurs SQL ;
- le délai de reprise.

**Objectif :** distinguer le changement de rôle PostgreSQL de la reconnexion des clients.

### TP 9 — Tester une sauvegarde

Si pgBackRest est configuré :

```bash
sudo -u postgres pgbackrest --stanza=prod info
```

Puis, selon la procédure de laboratoire :

```bash
sudo -u postgres pgbackrest --stanza=prod backup
```

**Objectif :** confirmer que le dépôt est accessible et qu'une sauvegarde est produite selon la configuration prévue.

Ne lancez pas cette commande si la stanza et le dépôt ne sont pas configurés.

### TP 10 — Restaurer dans un environnement isolé

Utilisez la procédure de restauration adaptée à l'outil de sauvegarde et à la version PostgreSQL.

Restaurez sur un répertoire de données et une instance de test distincts du cluster actif.

Vérifiez ensuite :

- le démarrage du serveur restauré ;
- la cohérence des bases ;
- les objets attendus ;
- les données métier ;
- les privilèges ;
- les conditions de récupération.

**Objectif :** prouver que la sauvegarde peut être utilisée, au lieu de simplement vérifier que des fichiers existent.

### TP 11 — Surveiller le WAL

Examinez :

```sql
SELECT
    slot_name,
    slot_type,
    active,
    restart_lsn
FROM pg_replication_slots;
```

Puis :

```sql
SELECT
    archived_count,
    failed_count,
    last_archived_time,
    last_failed_time
FROM pg_stat_archiver;
```

**Objectif :** identifier les slots inactifs et les éventuels problèmes d'archivage.

Ne supprimez aucun slot pendant l'exercice tant que son utilisation et ses dépendances n'ont pas été comprises.

### TP 12 — Rédiger le rapport du test

Consignez les résultats dans un rapport comprenant :

- la topologie ;
- le nœud initialement primaire ;
- les états observés avant le test ;
- les heures de début et de fin ;
- les erreurs rencontrées ;
- le temps de basculement ;
- l'état du point d'accès SQL ;
- le résultat du contrôle des données ;
- le temps de retour à la redondance ;
- les améliorations à effectuer.

**Objectif :** faire du test de basculement une opération mesurable, reproductible et exploitable.


## 33. Défi final : construire une architecture HA documentée

### Objectif

Concevoir et valider une architecture PostgreSQL capable de tolérer certaines pannes sans perdre le contrôle de l'état des données.

### Cahier des charges

L'architecture doit comprendre :

- au moins un primaire PostgreSQL ;
- un ou plusieurs secondaires ;
- une réplication configurée ;
- un gestionnaire de cluster ou une procédure de failover documentée ;
- un point d'accès applicatif stable ;
- une stratégie de sauvegarde indépendante ;
- un mécanisme de surveillance ;
- une procédure de réintégration ;
- un plan de reprise après incident.

### Étape A — Définir les objectifs

Définissez :

- le RPO ;
- le RTO ;
- le nombre de nœuds ;
- le mode de réplication ;
- les domaines de panne ;
- la politique de lecture et d'écriture ;
- les exigences de sauvegarde ;
- les critères de basculement.

### Étape B — Décrire l'architecture

Votre schéma doit montrer :

```text
Applications
     |
     v
Point d'accès SQL
     |
     +--------> Primaire PostgreSQL
     |
     +--------> Secondaires PostgreSQL

DCS / Coordination
Sauvegardes indépendantes
Supervision et alertes
Réseau et sécurité
```

### Étape C — Décrire un basculement

Documentez un scénario de panne du primaire.

Précisez comment le système :

1. détecte la panne ;
2. empêche l'ancien primaire de continuer à écrire ;
3. choisit un candidat ;
4. promeut le secondaire ;
5. met à jour le point d'accès ;
6. permet aux applications de se reconnecter ;
7. contrôle les données après l'incident ;
8. rétablit la redondance.

### Étape D — Décrire une restauration

Documentez la manière dont l'équipe récupère les données après une erreur logique ou une perte plus importante de l'infrastructure.

Cette procédure doit être distincte de la simple promotion d'un secondaire.

### Étape E — Tester

Effectuez un test contrôlé dans le laboratoire.

Mesurez le temps d'interruption et comparez le résultat avec les objectifs préalablement définis.

### Critères de réussite

Le défi est réussi si :

- le rôle primaire est identifiable ;
- les secondaires reçoivent et rejouent le WAL ;
- le point d'accès cible correctement le primaire ;
- une panne de test est traitée par la procédure prévue ;
- les applications peuvent se reconnecter ;
- les données ont été vérifiées ;
- la sauvegarde est restaurable ;
- la réintégration du nœud est documentée ;
- le risque de split-brain est explicitement traité ;
- les résultats sont mesurés et consignés.

Une architecture ne doit pas être déclarée hautement disponible uniquement parce qu'un basculement a fonctionné une fois. La répétabilité des tests et la cohérence des données sont essentielles.


## 34. Erreurs critiques à éviter

### 34.1 Promouvoir un secondaire sans isoler l'ancien primaire

Cette erreur peut provoquer un split-brain et des historiques de données divergents.

Un contrôle réseau ou un ping en échec ne suffit pas à prouver que l'ancien primaire ne peut plus écrire.

### 34.2 Utiliser la réplication comme unique protection

Une suppression accidentelle, une corruption logique ou une modification erronée peut se propager à tous les secondaires.

Conservez des sauvegardes récupérables séparément.

### 34.3 Confondre rôle de leader et disponibilité de l'application

Un leader peut être fonctionnel alors qu'HAProxy, le réseau ou les applications ne peuvent pas l'atteindre.

Testez le chemin réel utilisé par les clients.

### 34.4 Oublier le point d'accès

Un cluster PostgreSQL disponible peut rester inaccessible si le répartiteur ou l'adresse utilisée par les clients est indisponible.

La redondance doit s'étendre aux composants critiques de l'architecture.

### 34.5 Accumuler des WAL sans surveillance

Un replication slot ou un défaut d'archivage mal géré peut consommer beaucoup d'espace disque.

Surveillez les volumes, les slots, les erreurs et les retards.

### 34.6 Oublier le coût de la réplication synchrone

Une réplication synchrone peut augmenter la latence ou bloquer certaines validations si les secondaires requis ne sont plus disponibles.

Choisissez le mode en fonction des garanties métier et du réseau réel.

### 34.7 Réintégrer l'ancien primaire sans contrôler sa divergence

Un ancien primaire ne doit pas simplement être démarré comme s'il avait le même historique que le nouveau.

Utilisez une procédure compatible avec Patroni ou une méthode documentée de reconstruction ou de repositionnement.

### 34.8 Ne jamais tester les sauvegardes

Un fichier présent sur le disque ne prouve pas qu'une restauration réussira.

Testez périodiquement une restauration complète ou le scénario de restauration approprié.

### 34.9 Déployer sans supervision

Un cluster peut être dégradé sans que les applications cessent immédiatement de fonctionner.

Les alertes doivent également suivre la réplication, l'archivage WAL, le DCS, le stockage et la capacité.

### 34.10 Considérer le basculement comme une opération sans interruption

Les connexions existantes peuvent être coupées. Des requêtes peuvent échouer et des transactions peuvent nécessiter un traitement applicatif spécifique.

La haute disponibilité réduit le risque et le temps d'interruption selon la conception ; elle n'élimine pas tous les incidents.


## 35. Checklist d'exploitation

### Réplication

- [ ] Le primaire courant est identifiable.
- [ ] Les secondaires sont connectés.
- [ ] L'état de réception et de rejeu du WAL est contrôlé.
- [ ] Le retard est mesuré et alerté.
- [ ] Les replication slots sont surveillés.
- [ ] L'espace disque permet de conserver le WAL nécessaire.

### Gestion du cluster

- [ ] Le DCS fonctionne correctement.
- [ ] Les conditions d'élection du leader sont comprises.
- [ ] Le risque de split-brain est traité.
- [ ] Les mécanismes de fencing sont validés.
- [ ] Le comportement lors de la perte du réseau a été examiné.
- [ ] Les procédures Patroni sont documentées.

### Point d'accès

- [ ] HAProxy ou le point d'accès est disponible.
- [ ] Les contrôles de santé identifient le primaire.
- [ ] Le point d'accès est lui-même redondé lorsque nécessaire.
- [ ] Les applications peuvent se reconnecter après un changement de rôle.
- [ ] Les lectures sur les secondaires respectent les exigences de cohérence.

### Sauvegardes

- [ ] Les sauvegardes sont indépendantes du stockage principal.
- [ ] L'archivage WAL est fonctionnel lorsqu'il est utilisé.
- [ ] Les erreurs d'archivage sont surveillées.
- [ ] Les sauvegardes disposent d'une politique de rétention.
- [ ] Les restaurations sont testées.
- [ ] Le RPO et le RTO sont documentés.

### Maintenance

- [ ] Les mises à jour sont préparées et testées.
- [ ] Les versions des composants sont connues.
- [ ] L'état du stockage est surveillé.
- [ ] Les procédures de switchover sont maîtrisées.
- [ ] La réintégration d'un ancien primaire est documentée.
- [ ] Les résultats des incidents et tests sont conservés.


## 36. Fiche de révision rapide

### Vérifier le rôle PostgreSQL

```sql
SELECT pg_is_in_recovery();
```

### Examiner la réplication sur le primaire

```sql
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;
```

### Observer la réception et le rejeu sur le secondaire

```sql
SELECT
    pg_last_wal_receive_lsn(),
    pg_last_wal_replay_lsn(),
    pg_last_xact_replay_timestamp();
```

### Examiner les slots

```sql
SELECT
    slot_name,
    slot_type,
    active,
    restart_lsn
FROM pg_replication_slots;
```

### Vérifier l'archivage WAL

```sql
SELECT
    archived_count,
    failed_count,
    last_archived_time,
    last_failed_time
FROM pg_stat_archiver;
```

### Examiner les connexions

```sql
SELECT
    datname,
    state,
    COUNT(*)
FROM pg_stat_activity
GROUP BY datname, state;
```

### Examiner les journaux

```bash
sudo journalctl -u postgresql -n 100
```

```bash
sudo journalctl -u haproxy -n 100
```

### Contrôler Patroni

```bash
patronictl -c /chemin/vers/patroni.yml list
```

### Vérifier HAProxy

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg
```

### Contrôler les sauvegardes avec pgBackRest

```bash
sudo -u postgres pgbackrest --stanza=prod info
```

Ces commandes doivent être adaptées au service, au chemin de configuration et aux noms de bases réellement utilisés.


## 37. Glossaire

**Basculement (*failover*)** : changement vers un serveur de secours à la suite d'une panne ou d'une situation imprévue.

**DCS** : système de stockage distribué utilisé par un gestionnaire de cluster pour la coordination et l'état du cluster.

**Fencing** : mécanisme qui empêche un ancien primaire ou un nœud isolé de continuer à participer de manière dangereuse aux écritures.

**HA** : haute disponibilité, *High Availability*.

**HAProxy** : répartiteur de charge pouvant servir de point d'accès réseau pour les connexions PostgreSQL.

**Leader** : nœud désigné comme détenteur du rôle principal par le système de coordination.

**PITR** : récupération à un instant donné à partir d'une sauvegarde et des journaux nécessaires.

**Primaire** : instance PostgreSQL qui accepte normalement les écritures dans une architecture de réplication physique classique.

**Réplication asynchrone** : mécanisme dans lequel le primaire n'attend pas systématiquement une confirmation distante avant de confirmer une transaction.

**Réplication synchrone** : mécanisme qui peut imposer une confirmation distante pour les transactions concernées.

**Replication slot** : objet PostgreSQL qui permet notamment de retenir les WAL nécessaires à un consommateur de réplication ou de décodage logique.

**RPO** : objectif de perte de données maximale acceptable.

**RTO** : objectif de délai maximal de rétablissement du service.

**Secondaire (*standby*)** : instance qui reçoit et rejoue les modifications du primaire dans une architecture de réplication.

**Split-brain** : situation dans laquelle plusieurs instances peuvent accepter des écritures indépendantes pour un même service logique.

**Switchover** : changement de rôle planifié entre le primaire et un secondaire.

**WAL** : journal des modifications PostgreSQL, utilisé notamment pour la récupération et la réplication.

**Watchdog** : mécanisme de surveillance qui peut déclencher une action de sécurité lorsqu'un nœud ne respecte plus certaines conditions de fonctionnement.

**pg_rewind** : outil permettant, lorsque ses conditions sont réunies, de réaligner un cluster PostgreSQL ayant divergé avec un autre historique.

**Patroni** : solution de gestion de cluster qui automatise des mécanismes de haute disponibilité PostgreSQL.

**Quorum** : majorité nécessaire à certaines décisions de coordination distribuée.


## 38. Documentation officielle

Les configurations et comportements dépendent des versions utilisées. Avant un déploiement, consultez la documentation correspondant exactement aux versions installées.

### PostgreSQL

- Haute disponibilité, équilibrage de charge et réplication :  
  https://www.postgresql.org/docs/current/high-availability.html

- Serveurs secondaires et streaming replication :  
  https://www.postgresql.org/docs/current/warm-standby.html

- Paramètres de réplication :  
  https://www.postgresql.org/docs/current/runtime-config-replication.html

- Réplication synchrone :  
  https://www.postgresql.org/docs/current/warm-standby.html

- Sauvegarde et restauration :  
  https://www.postgresql.org/docs/current/backup.html

- Archivage continu et récupération PITR :  
  https://www.postgresql.org/docs/current/continuous-archiving.html

- pg_basebackup :  
  https://www.postgresql.org/docs/current/app-pgbasebackup.html

- pg_rewind :  
  https://www.postgresql.org/docs/current/app-pgrewind.html

- pg_stat_replication :  
  https://www.postgresql.org/docs/current/monitoring-stats.html

### Patroni

- Documentation générale :  
  https://patroni.readthedocs.io/en/latest/

- Introduction et architecture :  
  https://patroni.readthedocs.io/en/latest/README.html

- Haute disponibilité multi-site :  
  https://patroni.readthedocs.io/en/latest/ha_multi_dc.html

- Watchdog et prévention du split-brain :  
  https://patroni.readthedocs.io/en/latest/watchdog.html

### HAProxy

- Documentation des contrôles de santé :  
  https://www.haproxy.com/documentation/haproxy-configuration-tutorials/reliability/health-checks/

- Manuel de configuration :  
  https://docs.haproxy.org/

### pgBackRest

- Guide utilisateur :  
  https://pgbackrest.org/user-guide.html

- Référence de configuration :  
  https://pgbackrest.org/configuration.html


## Conclusion générale

La haute disponibilité des bases de données nécessite bien davantage que la création d'une copie secondaire.

Une architecture PostgreSQL fiable doit coordonner la réplication, la désignation du primaire, l'exclusion des anciens leaders, le routage des connexions, la gestion des transactions interrompues et la récupération des données.

Les sauvegardes indépendantes restent indispensables, car les erreurs logiques peuvent se propager aux secondaires. De même, la réplication synchrone ne dispense pas de la prévention du split-brain, des tests de restauration ou de la supervision.

Le parcours recommandé est le suivant :

```text
Définir les objectifs RPO et RTO
              |
              v
Concevoir les domaines de panne
              |
              v
Configurer la réplication
              |
              v
Coordonner les rôles avec Patroni et le DCS
              |
              v
Diriger les connexions avec HAProxy
              |
              v
Protéger contre le split-brain
              |
              v
Sauvegarder et archiver le WAL
              |
              v
Superviser et tester les pannes
              |
              v
Valider la restauration et la réintégration
```

**Le principe fondamental de la haute disponibilité est de privilégier la cohérence des données avant la rapidité du basculement.** Un système qui redémarre très vite mais accepte des écritures concurrentes sur deux primaires peut provoquer une perte de données bien plus grave que l'indisponibilité initiale.

La maîtrise de ces mécanismes constitue une base solide pour l'exploitation de clusters PostgreSQL résilients, la reprise après sinistre et l'administration de bases de données critiques.