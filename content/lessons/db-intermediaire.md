# Administration de bases de données

## 1. Introduction à l'administration des bases de données

Administrer une base de données ne consiste pas uniquement à créer des tables et à exécuter des requêtes SQL. Il faut aussi garantir que le service fonctionne correctement, que les données sont protégées, que les utilisateurs disposent des bons privilèges et que les informations peuvent être restaurées après un incident.

Dans une infrastructure informatique, la base de données constitue souvent un composant critique. Une indisponibilité peut interrompre les commandes d'une boutique, les opérations d'une application métier ou l'accès aux informations d'un système d'entreprise.

L'administrateur de bases de données, souvent appelé DBA (*Database Administrator*), organise l'exploitation du SGBD, contrôle son état, planifie la maintenance et prépare les procédures de récupération.

Ce cours utilise PostgreSQL comme environnement principal. Les commandes sont principalement adaptées à Debian et Ubuntu. Les concepts fondamentaux peuvent être réutilisés avec d'autres systèmes, mais leurs outils et certaines instructions diffèrent.

### 1.1 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

- distinguer l'administration d'une base de données de la programmation SQL ;
- gérer le cycle de vie du service PostgreSQL sous Linux ;
- identifier les fichiers de configuration réellement utilisés ;
- créer des rôles et appliquer le principe du moindre privilège ;
- configurer l'authentification locale et distante ;
- comprendre les paramètres importants du serveur ;
- surveiller les connexions, transactions et erreurs ;
- identifier les requêtes lentes et les blocages ;
- comprendre l'autovacuum, `VACUUM` et `ANALYZE` ;
- créer et maintenir des index de manière prudente ;
- sauvegarder une base et vérifier sa restauration ;
- élaborer une politique de sauvegarde adaptée aux objectifs métier ;
- comprendre les journaux WAL et la récupération à un instant donné ;
- identifier les risques liés aux modifications de schéma ;
- comprendre les principes de la réplication PostgreSQL ;
- préparer un plan de maintenance et une procédure de reprise après incident.

### 1.2 Prérequis

Vous devez connaître les bases de SQL étudiées au niveau débutant :

- création de tables ;
- insertion et lecture de données ;
- clés primaires et étrangères ;
- contraintes ;
- jointures ;
- transactions ;
- types de données.

Vous devez également maîtriser les bases du terminal Linux, notamment :

```bash
ls
cat
grep
ps
ss
systemctl
journalctl
sudo
```

### 1.3 Environnement de formation recommandé

Utilisez une machine virtuelle ou une machine de laboratoire qui ne contient pas de données importantes.

Architecture de référence :

```text
+--------------------------------------------------------+
| SERVEUR LINUX                                          |
|                                                        |
|  +--------------------------------------------------+  |
|  | PostgreSQL                                      |  |
|  |                                                  |  |
|  | - Processus serveur                              |  |
|  | - Bases de données                               |  |
|  | - Rôles et privilèges                            |  |
|  | - Journaux                                       |  |
|  | - Fichiers WAL                                   |  |
|  +----------------------+---------------------------+  |
|                         |                              |
|          +--------------+--------------+               |
|          |                             |               |
|          v                             v               |
|   +-------------+              +-------------+         |
|   | Application |              | Outils DBA  |         |
|   | Web / SQL   |              | psql, pg_dump|        |
|   +-------------+              +-------------+         |
+--------------------------------------------------------+
```

Dans un environnement de production, les sauvegardes doivent être conservées séparément de la machine de base de données. Une copie située uniquement sur le même disque ne protège pas contre une panne de ce disque.

### 1.4 Les responsabilités d'un administrateur

Les principales responsabilités d'exploitation peuvent être regroupées ainsi :

| Domaine | Responsabilité |
|---|---|
| Disponibilité | Vérifier et maintenir le service opérationnel |
| Sécurité | Contrôler les accès et protéger les secrets |
| Maintenance | Gérer les statistiques, l'espace et les index |
| Performance | Identifier les requêtes coûteuses et les limitations |
| Sauvegarde | Produire des copies récupérables |
| Restauration | Vérifier la récupération des données |
| Capacité | Anticiper les besoins de stockage et de ressources |
| Continuité | Préparer les procédures en cas de panne |
| Traçabilité | Conserver les journaux et les informations d'exploitation |


## 2. Comprendre l'architecture de PostgreSQL

### 2.1 Le serveur et ses bases

PostgreSQL fonctionne comme un service qui accepte les connexions, authentifie les clients et exécute leurs requêtes.

Un même serveur PostgreSQL peut gérer plusieurs bases de données.

```text
INSTANCE POSTGRESQL
|
+-- Base postgres
|
+-- Base boutique_sql
|
+-- Base gestion_stock
|
+-- Base supervision
|
+-- Rôles globaux
|
+-- Paramètres du serveur
```

Les rôles sont définis au niveau de l'instance. Les objets comme les tables, vues et fonctions appartiennent à une base et sont organisés notamment dans des schémas.

Les bases d'une même instance partagent plusieurs ressources : mémoire partagée, processus serveur, paramètres globaux et capacité de stockage du système sous-jacent.

Une séparation entre plusieurs bases ne remplace donc pas complètement une séparation entre plusieurs instances ou entre plusieurs machines.

### 2.2 Le rôle des processus

PostgreSQL utilise une architecture multiprocessus.

Représentation simplifiée :

```text
                    CLIENTS
                       |
                       v
              +------------------+
              | Point d'entrée   |
              | PostgreSQL       |
              +---------+--------+
                        |
            +-----------+-----------+
            |           |           |
            v           v           v
        Processus   Processus   Processus
        backend 1   backend 2   backend 3
            |           |           |
            +-----------+-----------+
                        |
                        v
              Mémoire partagée
              et stockage de la base
```

Cette représentation ne montre pas tous les processus internes. PostgreSQL possède notamment des processus chargés de la maintenance et de la gestion des journaux.

Chaque connexion cliente peut être associée à un processus backend côté serveur selon l'architecture classique de PostgreSQL. Cela explique pourquoi un nombre excessif de connexions peut augmenter la consommation de ressources.

### 2.3 Les principaux composants

| Composant | Fonction générale |
|---|---|
| `postgres` | Processus principal du serveur |
| Backend | Processus qui traite une session cliente |
| `shared_buffers` | Mémoire partagée utilisée pour mettre en cache des pages de la base |
| WAL | Journal des modifications nécessaires notamment à la récupération |
| Checkpointer | Contribue à la gestion des points de contrôle |
| Autovacuum | Automatise certaines opérations de maintenance |
| Fichiers de données | Contiennent les structures persistantes |
| Journaux serveur | Permettent de diagnostiquer le fonctionnement et les erreurs |

Il est important de distinguer les journaux applicatifs des journaux internes de PostgreSQL.

Les journaux serveur contiennent les informations du SGBD. Les journaux d'une application peuvent compléter ces informations, par exemple en enregistrant l'identifiant d'une requête métier.

### 2.4 Le cycle d'une requête SQL

```text
Application
    |
    | Connexion
    v
Authentification PostgreSQL
    |
    v
Réception de la requête SQL
    |
    v
Analyse et planification
    |
    v
Exécution de la requête
    |
    +---- Lecture / modification des données
    |
    +---- Utilisation éventuelle des index
    |
    +---- Enregistrement des modifications dans le WAL
    |
    v
Réponse au client
```

Ce schéma est simplifié. L'ordre précis de certaines opérations dépend du type de requête, des transactions et des mécanismes internes.

Une administration efficace exige de comprendre l'ensemble du cycle, et pas seulement le texte SQL envoyé par le client.


## 3. Gérer le service PostgreSQL sous Linux

### 3.1 Vérifier l'état du service

Sur Debian ou Ubuntu :

```bash
sudo systemctl status postgresql
```

Cette commande permet notamment de vérifier si le service est actif et d'obtenir des informations sur son état.

Sur certaines installations Debian, `postgresql` agit comme un service de gestion de plusieurs clusters PostgreSQL. Le statut de cette unité ne constitue donc pas toujours une vérification suffisante de chaque instance.

Sur une installation qui expose directement une unité pour une instance, le nom de cette unité peut être différent.

### 3.2 Démarrer PostgreSQL

```bash
sudo systemctl start postgresql
```

Cette commande démarre le service si nécessaire.

### 3.3 Arrêter PostgreSQL

```bash
sudo systemctl stop postgresql
```

L'arrêt du service interrompt les connexions qui en dépendent. Sur un serveur utilisé par une application, cela peut provoquer une indisponibilité.

Ne réalisez cette opération que lorsque l'arrêt est autorisé et que les conséquences sont comprises.

### 3.4 Redémarrer PostgreSQL

```bash
sudo systemctl restart postgresql
```

Un redémarrage réinitialise le service. Il peut être nécessaire lorsque certains paramètres qui nécessitent un redémarrage ont été modifiés.

Dans un environnement de production, un redémarrage doit être planifié, documenté et accompagné d'une stratégie de vérification.

### 3.5 Recharger la configuration

```bash
sudo systemctl reload postgresql
```

Le rechargement demande au service de relire les paramètres qui prennent en charge cette opération.

Tous les paramètres ne sont pas modifiables par simple rechargement. Certains nécessitent un redémarrage complet.

Il est donc nécessaire de vérifier la nature du paramètre concerné avant de décider d'un rechargement ou d'un redémarrage.

### 3.6 Examiner les journaux du service

```bash
sudo journalctl -u postgresql -n 100
```

Cette commande affiche les dernières entrées du journal systemd associées à l'unité.

Pour suivre les nouvelles entrées :

```bash
sudo journalctl -u postgresql -f
```

Quittez le suivi avec `Ctrl+C`.

PostgreSQL peut également écrire dans des fichiers journaux configurés spécifiquement. Le journal systemd et les journaux du SGBD ne contiennent pas nécessairement les mêmes informations.

### 3.7 Identifier les clusters Debian

Sur une installation Debian qui utilise les outils de gestion des clusters PostgreSQL :

```bash
pg_lsclusters
```

Cette commande permet notamment de voir les clusters, leurs versions, leurs ports et leurs états.

La commande peut ne pas être disponible sur toutes les distributions.

Si plusieurs clusters sont présents, les commandes de service, les fichiers de configuration et les opérations d'administration doivent cibler le bon cluster.

### 3.8 Identifier les versions

Depuis le terminal :

```bash
psql --version
```

Cette commande affiche la version du client `psql`.

Depuis une connexion SQL :

```sql
SELECT version();
```

Cette requête affiche la version du serveur PostgreSQL auquel la session est connectée.

Les deux versions peuvent différer.

**Bonne pratique :** avant de modifier une configuration ou d'appliquer une commande d'administration, identifiez la version réelle du serveur.


## 4. Identifier les fichiers de configuration

### 4.1 Pourquoi ne pas deviner les chemins ?

Les chemins de configuration peuvent différer selon :

- la distribution Linux ;
- la version PostgreSQL ;
- le mode d'installation ;
- le nombre de clusters ;
- les options de compilation ;
- le système de gestion du service.

Il vaut mieux demander au serveur quels fichiers il utilise que supposer que la configuration se trouve dans un répertoire donné.

### 4.2 Connexion d'administration locale

Sur Debian ou Ubuntu, si l'authentification locale le permet :

```bash
sudo -u postgres psql
```

Puis :

```sql
SHOW config_file;
SHOW hba_file;
SHOW data_directory;
SHOW port;
SHOW listen_addresses;
```

Ces commandes affichent notamment :

- le chemin du fichier principal de configuration ;
- le chemin du fichier des règles d'authentification ;
- le répertoire des données ;
- le port d'écoute ;
- les adresses d'écoute configurées.

### 4.3 Le fichier postgresql.conf

Le fichier `postgresql.conf` contient les paramètres de fonctionnement du serveur.

Ils peuvent concerner :

- les connexions ;
- la mémoire ;
- les journaux ;
- les checkpoints ;
- les statistiques ;
- le comportement du planificateur ;
- le WAL ;
- l'authentification TLS.

Tous les paramètres n'ont pas les mêmes conditions d'application. Certains sont modifiables à chaud, d'autres nécessitent un redémarrage.

### 4.4 Le fichier pg_hba.conf

Le fichier `pg_hba.conf` définit les règles d'authentification des clients.

Il précise notamment :

- le type de connexion ;
- la base ou le type de connexion demandé ;
- le rôle demandé ;
- l'adresse source concernée ;
- la méthode d'authentification.

Les règles sont évaluées dans l'ordre. La première règle correspondant à la connexion est utilisée.

Une règle plus restrictive placée après une règle plus générale peut ne jamais être examinée si cette dernière correspond déjà à la connexion.

### 4.5 Le fichier postgresql.auto.conf

PostgreSQL peut stocker certains paramètres définis par `ALTER SYSTEM` dans un fichier `postgresql.auto.conf`.

Ce mécanisme doit être utilisé avec discernement. Il est préférable de savoir précisément quel paramètre est modifié et comment il sera maintenu dans la configuration d'exploitation.

Pour examiner les paramètres et leurs sources :

```sql
SELECT
    name,
    setting,
    source,
    context,
    pending_restart
FROM pg_settings
ORDER BY name;
```

`pending_restart` permet notamment d'identifier les paramètres dont la nouvelle valeur nécessite un redémarrage pour être appliquée.

### 4.6 Vérifier les règles de pg_hba.conf

PostgreSQL expose une vue permettant de diagnostiquer les problèmes dans le fichier des règles d'authentification.

```sql
SELECT *
FROM pg_hba_file_rules
WHERE error IS NOT NULL;
```

Cette vérification est utile après une modification du fichier.

Un résultat vide signifie qu'aucune erreur n'a été détectée dans les lignes analysées par cette vue. Cela ne prouve pas que la politique d'accès est correcte : il faut encore vérifier que les règles correspondent à l'intention de sécurité.


## 5. Administrer les rôles et les privilèges

La gestion des rôles est l'un des aspects fondamentaux de l'administration PostgreSQL.

Il faut séparer les comptes d'administration, les comptes applicatifs et les comptes de lecture utilisés pour les rapports.

### 5.1 Comprendre un rôle

Un rôle PostgreSQL peut :

- se connecter au serveur, si le privilège `LOGIN` lui est accordé ;
- posséder une base, une table ou un autre objet ;
- lire des données ;
- modifier des données ;
- créer certains objets ;
- transmettre certains privilèges à d'autres rôles.

Un rôle ne correspond pas nécessairement à une personne. Il peut aussi représenter une application ou un groupe de permissions.

### 5.2 Créer un rôle de lecture

Dans une session disposant des privilèges administratifs :

```sql
CREATE ROLE boutique_lecture LOGIN;
```

Ce rôle peut s'authentifier, mais il ne dispose pas automatiquement de tous les droits sur les bases et les tables.

### 5.3 Définir un mot de passe

Dans `psql`, vous pouvez utiliser :

```text
\password boutique_lecture
```

Le client demande alors le mot de passe sans obliger à écrire directement le secret dans une instruction SQL visible.

Pour les scripts automatisés, utilisez un mécanisme de gestion des secrets adapté à votre environnement et évitez de laisser les mots de passe dans l'historique du terminal, dans des fichiers de configuration non protégés ou dans les dépôts de code.

### 5.4 Créer un rôle applicatif

Pour une application qui doit lire et écrire des données, vous pouvez créer un autre rôle :

```sql
CREATE ROLE boutique_app LOGIN;
```

Attribuez-lui ensuite uniquement les droits nécessaires.

Il ne doit pas recevoir le statut superutilisateur simplement pour résoudre une erreur de privilèges.

### 5.5 Comprendre les privilèges disponibles

Selon l'objet, les droits PostgreSQL peuvent inclure notamment :

| Privilège | Fonction |
|---|---|
| `CONNECT` | Autorise la connexion à une base |
| `USAGE` | Permet notamment d'utiliser un schéma selon les règles applicables |
| `SELECT` | Autorise la lecture de données |
| `INSERT` | Autorise l'insertion de lignes |
| `UPDATE` | Autorise la modification de données |
| `DELETE` | Autorise la suppression de lignes |
| `CREATE` | Autorise certaines créations d'objets selon l'objet ciblé |
| `EXECUTE` | Autorise l'exécution d'une fonction ou procédure compatible |
| `TRUNCATE` | Autorise la suppression rapide de toutes les lignes d'une table |

Les privilèges doivent être accordés au bon niveau : base, schéma, table, séquence, fonction ou autre objet.

### 5.6 Accorder l'accès à une base

```sql
GRANT CONNECT ON DATABASE boutique_sql
TO boutique_app;
```

Ce privilège autorise la connexion à la base, sous réserve des autres règles applicables.

Il ne donne pas automatiquement les droits de lecture et d'écriture sur toutes ses tables.

### 5.7 Accorder l'accès au schéma

Dans la base concernée :

```sql
GRANT USAGE ON SCHEMA public
TO boutique_app;
```

Le privilège `USAGE` sur le schéma permet notamment au rôle de référencer les objets de ce schéma lorsque les autres privilèges nécessaires sont disponibles.

### 5.8 Autoriser la lecture

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA public
TO boutique_lecture;
```

Cette instruction accorde un droit de lecture sur les tables existantes du schéma.

Pour que le rôle puisse utiliser ces tables, il lui faut également l'accès approprié à la base et au schéma.

### 5.9 Accorder des droits d'écriture

```sql
GRANT INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO boutique_app;
```

Cette commande accorde les droits indiqués sur les tables existantes du schéma.

Elle ne doit être utilisée que si l'application a réellement besoin de ces opérations.

### 5.10 Retirer un privilège

```sql
REVOKE DELETE
ON ALL TABLES IN SCHEMA public
FROM boutique_app;
```

Cette instruction retire le privilège `DELETE` accordé directement au rôle sur les tables concernées.

Il faut également examiner les privilèges hérités par l'appartenance à d'autres rôles et les éventuels privilèges accordés par d'autres chemins.

### 5.11 Vérifier les rôles

Dans `psql` :

```text
\du
```

Pour examiner les privilèges d'une table :

```text
\dp clients
```

Pour consulter les propriétés de connexion d'un rôle :

```sql
SELECT
    rolname,
    rolcanlogin,
    rolsuper,
    rolcreatedb,
    rolcreaterole,
    rolreplication
FROM pg_roles
ORDER BY rolname;
```

Une gestion rigoureuse des rôles doit être documentée afin de savoir à quelles fonctions correspondent les privilèges accordés.


## 6. Gérer les privilèges par défaut

Un piège fréquent consiste à accorder des privilèges sur les tables existantes, puis à oublier que les nouvelles tables créées plus tard n'héritent pas automatiquement de ces mêmes droits.

### 6.1 Pourquoi les privilèges par défaut sont-ils importants ?

Considérons le scénario suivant :

```text
Jour 1
  |
  +-- Création de la table clients
  |
  +-- GRANT SELECT à boutique_lecture
  |
Jour 10
  |
  +-- Création de la table factures
  |
  +-- Le rôle de lecture ne possède pas
      nécessairement le droit attendu
```

Les privilèges par défaut permettent de définir les droits à appliquer aux objets futurs, pour un rôle créateur donné.

### 6.2 Configurer les privilèges par défaut

Exemple :

```sql
ALTER DEFAULT PRIVILEGES
FOR ROLE boutique_owner
IN SCHEMA public
GRANT SELECT ON TABLES TO boutique_lecture;
```

Cette instruction s'applique aux nouveaux objets correspondant au périmètre configuré et créés par le rôle `boutique_owner`.

Elle ne modifie pas les privilèges des tables existantes.

### 6.3 Comprendre le rôle créateur

Si les tables sont créées par un autre rôle, par exemple `postgres`, la règle définie pour `boutique_owner` ne s'applique pas automatiquement.

C'est pourquoi il est souvent préférable de séparer :

- le rôle propriétaire des objets ;
- les rôles applicatifs ;
- les rôles de lecture ;
- les rôles d'administration.

Exemple conceptuel :

```text
                  boutique_owner
                         |
                         | Crée les objets
                         v
                Tables et séquences
                         |
                 +-------+-------+
                 |               |
                 v               v
           boutique_app    boutique_lecture
           Lecture/écriture  Lecture seule
```

Cette séparation facilite l'administration et limite les privilèges inutiles.

### 6.4 Vérifier les privilèges effectifs

Ne supposez pas qu'un seul `GRANT` décrit tous les droits effectifs d'un rôle.

Il faut aussi examiner :

- l'appartenance à d'autres rôles ;
- l'héritage des privilèges ;
- les privilèges sur les schémas ;
- les privilèges sur les séquences ;
- les propriétaires des objets ;
- les règles de sécurité au niveau des lignes, lorsqu'elles existent.


## 7. Configurer l'authentification et l'accès réseau

### 7.1 Écoute locale et écoute réseau

Par défaut, PostgreSQL peut être configuré pour accepter seulement les connexions locales.

Le paramètre `listen_addresses` définit les adresses d'écoute TCP/IP.

Exemple :

```conf
listen_addresses = 'localhost'
```

Cette configuration limite l'écoute TCP aux interfaces locales couvertes par `localhost`.

Pour un serveur ayant une adresse privée précise, on peut envisager une configuration de la forme :

```conf
listen_addresses = '127.0.0.1,192.168.10.20'
```

L'adresse `192.168.10.20` est un exemple à remplacer par l'adresse réelle de l'interface du serveur.

Une modification de `listen_addresses` nécessite un redémarrage de PostgreSQL.

N'utilisez pas `listen_addresses = '*'` par réflexe : cela peut exposer le service sur toutes les interfaces disponibles.

### 7.2 Comprendre pg_hba.conf

Le fichier `pg_hba.conf` contrôle l'authentification des clients.

Exemple de règle locale :

```conf
local   all   postgres   peer
```

Cette règle illustre une authentification locale par pair pour le rôle `postgres`, courante sur certaines installations Debian.

Exemple de règle réseau avec mot de passe :

```conf
host    boutique_sql   boutique_app   192.168.10.0/24   scram-sha-256
```

Cette règle concerne les connexions réseau vers la base `boutique_sql`, demandées par `boutique_app` depuis la plage IPv4 indiquée.

La plage est un exemple et doit être remplacée par un réseau réellement autorisé.

`SCRAM-SHA-256` est une méthode d'authentification par mot de passe prise en charge par les versions modernes de PostgreSQL et les clients compatibles.

### 7.3 Ordre des règles

PostgreSQL utilise la première règle de `pg_hba.conf` qui correspond à la connexion. Si l'authentification échoue, il ne continue pas automatiquement vers une règle suivante.

L'ordre est donc important.

Exemple de logique :

```text
Connexion entrante
       |
       v
Première règle correspondante
       |
       v
Méthode d'authentification
       |
       +-- Réussite : connexion établie
       |
       +-- Échec : connexion refusée
```

Une règle permissive placée en premier peut autoriser des connexions qui devaient être limitées par une règle plus restrictive.

### 7.4 Recharger les règles

Après une modification de `pg_hba.conf`, demandez à PostgreSQL de recharger sa configuration si le fichier et le paramètre en question le permettent :

```sql
SELECT pg_reload_conf();
```

Cette fonction demande un rechargement de la configuration. La valeur retournée indique si la demande a pu être lancée, pas si toutes les règles ont le comportement de sécurité attendu.

Vérifiez également le journal du serveur et la vue `pg_hba_file_rules`.

### 7.5 Tester une connexion distante

Depuis une machine client autorisée :

```bash
psql -h 192.168.10.20 -p 5432 -U boutique_app -d boutique_sql
```

Remplacez l'adresse par celle du serveur réel.

Si la connexion échoue, vérifiez notamment :

1. que PostgreSQL écoute sur l'adresse attendue ;
2. que le port est correct ;
3. que la route réseau est disponible ;
4. que les règles du pare-feu autorisent la connexion ;
5. que `pg_hba.conf` contient une règle appropriée ;
6. que le rôle existe ;
7. que l'authentification du rôle est correcte.

### 7.6 Sécurité réseau

Ne rendez pas PostgreSQL accessible à l'ensemble d'Internet sans une architecture de sécurité explicitement conçue pour cet objectif.

Privilégiez notamment :

- les réseaux privés ;
- les règles de pare-feu restrictives ;
- les rôles à privilèges limités ;
- une authentification moderne ;
- le chiffrement TLS sur les réseaux non fiables ;
- la protection des mots de passe et des clés ;
- la surveillance des connexions.

La restriction d'adresse et l'authentification sont complémentaires : aucune ne remplace l'autre.


## 8. Sécuriser les connexions et les secrets

### 8.1 Principe du moindre privilège

Un rôle applicatif n'a généralement pas besoin de :

- créer ou supprimer des bases ;
- modifier les rôles d'administration ;
- changer la configuration générale du serveur ;
- accéder à toutes les tables ;
- devenir superutilisateur.

Un rôle doit recevoir seulement les droits nécessaires à sa mission.

### 8.2 Séparer les responsabilités

Une organisation possible :

```text
postgres
   |
   +-- Administration de l'instance

boutique_owner
   |
   +-- Propriété des objets applicatifs

boutique_app
   |
   +-- Opérations nécessaires à l'application

boutique_lecture
   |
   +-- Rapports et consultations

boutique_sauvegarde
   |
   +-- Droits spécifiques selon la stratégie de sauvegarde
```

Les droits exacts des rôles de sauvegarde dépendent des méthodes et des outils utilisés. Ne leur attribuez pas automatiquement les privilèges superutilisateur.

### 8.3 Utilisateurs inactifs

Lorsqu'une application n'utilise plus un rôle, il est important de vérifier si celui-ci dispose encore d'un accès.

L'administrateur peut désactiver la possibilité de connexion :

```sql
ALTER ROLE boutique_app NOLOGIN;
```

Cette commande interdit les nouvelles connexions par ce rôle. Elle ne termine pas automatiquement toutes ses sessions déjà ouvertes.

Pour rétablir l'accès :

```sql
ALTER ROLE boutique_app LOGIN;
```

Ces commandes doivent être intégrées à une procédure d'administration claire, en tenant compte des dépendances de l'application.

### 8.4 Protéger les secrets

Évitez de stocker les mots de passe dans :

- les dépôts Git ;
- les scripts publics ;
- les fichiers de configuration lisibles par tous ;
- les journaux ;
- les historiques shell ;
- les captures d'écran partagées.

Utilisez un mécanisme de gestion des secrets adapté à l'organisation et limitez l'accès aux fichiers qui les contiennent.

### 8.5 Contrôler les privilèges de propriété

Le propriétaire d'un objet dispose de droits particuliers sur cet objet.

Accorder un droit de lecture n'est donc pas équivalent à transférer la propriété.

Une séparation efficace entre propriétaires et utilisateurs applicatifs permet de contrôler plus clairement qui peut modifier le schéma et qui peut manipuler les données.


## 9. Paramètres de configuration importants

### 9.1 Connexions simultanées

Le paramètre :

```conf
max_connections = 100
```

représente une valeur illustrative.

`max_connections` limite le nombre de connexions simultanées au serveur. Augmenter ce paramètre peut augmenter la consommation de ressources, puisque PostgreSQL dimensionne certaines structures en fonction de cette limite.

Il ne faut pas augmenter cette valeur simplement parce que l'application indique qu'elle manque de connexions.

Il faut comprendre :

- le nombre de connexions réellement utilisées ;
- le nombre de connexions inactives ;
- la concurrence des requêtes ;
- les limites de mémoire ;
- le comportement du pool de connexions applicatif.

### 9.2 Gestion des connexions avec un pool

Une application qui ouvre une nouvelle connexion pour chaque opération peut produire un nombre important de connexions simultanées.

Un pool de connexions peut permettre de réutiliser un ensemble de connexions au lieu d'en créer continuellement de nouvelles.

```text
Applications
    |
    | Requêtes
    v
Pool de connexions
    |
    | Nombre contrôlé de connexions
    v
PostgreSQL
```

Un pool externe tel que PgBouncer peut être utile dans certaines architectures.

Cependant, le dimensionnement du pool doit tenir compte de la concurrence réelle, des transactions longues et de la capacité du serveur.

Un pool trop grand peut simplement déplacer la surcharge vers PostgreSQL.

### 9.3 Mémoire partagée

Le paramètre :

```conf
shared_buffers = 256MB
```

est un exemple de valeur et non une recommandation universelle.

`shared_buffers` contrôle la quantité de mémoire partagée utilisée par PostgreSQL pour mettre en cache des pages de données.

La valeur appropriée dépend de la mémoire disponible, du système d'exploitation, de l'application et du volume de données actif.

### 9.4 Mémoire de tri et de hachage

Le paramètre :

```conf
work_mem = 4MB
```

est également une valeur illustrative.

`work_mem` influence la mémoire pouvant être utilisée par certaines opérations comme les tris et les tables de hachage avant de recourir éventuellement à des fichiers temporaires.

La consommation totale peut dépasser largement la valeur de `work_mem`, car plusieurs opérations et plusieurs sessions peuvent en utiliser simultanément.

Une augmentation de ce paramètre peut améliorer certaines requêtes, mais elle peut aussi augmenter fortement la consommation mémoire sous forte concurrence.

### 9.5 Cache du système d'exploitation

Le cache de fichiers Linux joue également un rôle important.

PostgreSQL ne s'appuie pas uniquement sur sa propre mémoire partagée. Le système d'exploitation conserve lui aussi des données en mémoire et peut servir certains accès sans relire physiquement le stockage.

Il faut donc analyser le comportement global de la mémoire, pas uniquement la valeur de `shared_buffers`.

### 9.6 Déterminer les paramètres réellement actifs

```sql
SELECT
    name,
    setting,
    unit,
    source,
    context,
    pending_restart
FROM pg_settings
WHERE name IN (
    'max_connections',
    'shared_buffers',
    'work_mem',
    'maintenance_work_mem',
    'effective_cache_size',
    'listen_addresses',
    'port'
)
ORDER BY name;
```

Cette requête permet de comparer les valeurs actives, leur source et certaines informations relatives à leur modification.

`effective_cache_size` est une estimation destinée au planificateur de requêtes. Elle n'alloue pas directement une quantité de mémoire au serveur.

### 9.7 Modifier un paramètre avec discernement

PostgreSQL permet de modifier certains paramètres au moyen de commandes SQL comme `ALTER SYSTEM`.

Exemple de consultation :

```sql
SHOW work_mem;
```

Une modification via `ALTER SYSTEM` s'écrit notamment :

```sql
ALTER SYSTEM SET work_mem = '8MB';
```

Cette commande modifie la configuration persistante gérée par PostgreSQL. La nouvelle valeur n'est pas nécessairement appliquée immédiatement à toutes les sessions ou tous les paramètres, et certaines modifications nécessitent un redémarrage.

**Ne modifiez pas `work_mem`, `shared_buffers` ou `max_connections` sans mesurer le besoin et calculer les effets possibles sur la mémoire et la concurrence.**

En production, documentez les changements, vérifiez les paramètres actifs et prévoyez un retour arrière.


## 10. Surveiller les connexions et les requêtes actives

La vue système `pg_stat_activity` fournit des informations sur les processus et sessions associés à l'instance.

### 10.1 Compter les connexions

```sql
SELECT COUNT(*) AS nombre_connexions
FROM pg_stat_activity;
```

Cette requête compte les sessions visibles dans la vue selon les permissions du rôle connecté.

### 10.2 Compter les connexions par base

```sql
SELECT
    datname,
    COUNT(*) AS nombre_connexions
FROM pg_stat_activity
GROUP BY datname
ORDER BY nombre_connexions DESC;
```

Cette requête permet d'identifier les bases qui possèdent le plus de sessions.

Certaines lignes peuvent correspondre à des processus internes ou à des sessions sans base associée.

### 10.3 Compter les connexions par état

```sql
SELECT
    state,
    COUNT(*) AS nombre
FROM pg_stat_activity
GROUP BY state
ORDER BY nombre DESC;
```

Les états courants peuvent inclure :

- `active` ;
- `idle` ;
- `idle in transaction` ;
- des situations où l'état n'est pas renseigné de la même manière.

Une session `idle` n'est pas automatiquement anormale. Elle peut appartenir à un pool de connexions qui conserve une connexion prête à être réutilisée.

Les sessions `idle in transaction` doivent recevoir une attention particulière lorsqu'elles restent ouvertes longtemps.

### 10.4 Afficher les requêtes actives

```sql
SELECT
    pid,
    usename,
    datname,
    application_name,
    client_addr,
    state,
    wait_event_type,
    wait_event,
    query_start,
    now() - query_start AS duree_requete,
    LEFT(query, 200) AS extrait_requete
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;
```

Cette requête aide à examiner les sessions actives.

Elle doit être interprétée avec attention :

- certaines requêtes actives sont normales ;
- les statistiques peuvent ne pas être instantanées pour tous les compteurs ;
- les détails visibles dépendent des privilèges ;
- une session peut attendre une ressource sans consommer beaucoup de CPU.

### 10.5 Détecter les transactions ouvertes depuis longtemps

```sql
SELECT
    pid,
    usename,
    datname,
    state,
    xact_start,
    now() - xact_start AS duree_transaction,
    application_name,
    LEFT(query, 200) AS extrait_requete
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start;
```

Les transactions très longues peuvent retenir des verrous et empêcher certaines opérations de maintenance de progresser correctement.

Elles peuvent aussi retarder la récupération de certaines versions de lignes qui ne sont plus utiles aux autres transactions.

Il faut identifier l'application ou la session responsable avant d'intervenir.


## 11. Comprendre les verrous et les blocages

Les verrous protègent la cohérence des accès concurrents.

Une transaction peut avoir besoin d'un verrou détenu par une autre transaction. Elle doit alors attendre que le verrou soit libéré, selon les règles d'isolation et de verrouillage applicables.

### 11.1 Exemple de situation de blocage

```text
SESSION A                         SESSION B
---------                         ---------
BEGIN;                            BEGIN;

UPDATE clients                    UPDATE clients
SET ville = ...                   SET ville = ...
WHERE id = 1;                     WHERE id = 1;

Verrou détenu                     Attend le verrou
       |                                 |
       +--------------+------------------+
                      |
                      v
           SESSION B attend la fin
           de la transaction A
```

La session B peut attendre jusqu'à ce que la session A valide ou annule sa transaction, ou jusqu'à ce qu'un délai ou une autre condition provoque une erreur.

### 11.2 Identifier les sessions bloquées

```sql
SELECT
    pid,
    usename,
    datname,
    state,
    wait_event_type,
    wait_event,
    pg_blocking_pids(pid) AS bloqueurs,
    LEFT(query, 200) AS extrait_requete
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```

Cette requête est utile pour identifier les processus qui attendent un autre processus.

Une session peut être bloquée par plusieurs processus, selon la situation.

### 11.3 Afficher les relations entre bloqueurs et bloqués

```sql
SELECT
    bloque.pid AS pid_bloque,
    bloque.usename AS utilisateur_bloque,
    bloque.wait_event_type,
    bloque.wait_event,
    bloque.query AS requete_bloquee,
    bloqueur.pid AS pid_bloqueur,
    bloqueur.usename AS utilisateur_bloqueur,
    bloqueur.query AS requete_bloqueuse
FROM pg_stat_activity AS bloque
CROSS JOIN LATERAL unnest(pg_blocking_pids(bloque.pid)) AS b(pid)
JOIN pg_stat_activity AS bloqueur
    ON bloqueur.pid = b.pid;
```

Cette requête permet d'examiner certaines relations de blocage.

Elle constitue un outil de diagnostic, pas une décision automatique de terminer des processus.

### 11.4 Annuler une requête

PostgreSQL propose une fonction permettant de demander l'annulation de la requête en cours d'un processus :

```sql
SELECT pg_cancel_backend(12345);
```

`12345` est un exemple de PID à remplacer par celui de la session identifiée.

Cette opération ne doit pas être effectuée aveuglément. Il faut comprendre quelle application est concernée et quelles conséquences l'annulation peut avoir.

### 11.5 Terminer une session

PostgreSQL propose également :

```sql
SELECT pg_terminate_backend(12345);
```

Cette opération demande la terminaison de la session correspondant au PID indiqué, sous réserve des autorisations applicables.

La session peut perdre sa transaction en cours. L'application concernée peut recevoir une erreur, et certaines opérations métier peuvent devoir être reprises.

**Règle d'administration :** identifiez d'abord le PID, le rôle, la base, la requête, la durée et l'application responsable. L'annulation ou la terminaison doit être une décision consciente.


## 12. Les transactions longues et leurs conséquences

Une transaction ouverte longtemps peut affecter plusieurs aspects de PostgreSQL.

### 12.1 Rétention des versions de lignes

PostgreSQL utilise un mécanisme multiversion appelé MVCC. Plusieurs versions d'une ligne peuvent être nécessaires pour assurer la visibilité correcte des données entre les transactions.

Lorsqu'une transaction reste ouverte, certaines anciennes versions peuvent devoir être conservées plus longtemps.

```text
Modification de ligne
        |
        v
Ancienne version de la ligne
        |
        +---- Nécessaire à une transaction encore active
        |
        v
Récupération différée lors de la maintenance
```

Une accumulation de versions inutiles peut augmenter l'espace consommé et les coûts de traitement.

### 12.2 Transactions inactives mais ouvertes

Une session `idle in transaction` peut conserver une transaction ouverte alors qu'elle n'exécute actuellement aucune requête.

Cela peut se produire lorsqu'une application commence une transaction puis attend une action externe avant de la terminer.

Les conséquences dépendent de la durée et du contenu de la transaction.

### 12.3 Diagnostic

```sql
SELECT
    pid,
    usename,
    application_name,
    state,
    xact_start,
    now() - xact_start AS age_transaction,
    query_start,
    LEFT(query, 200) AS derniere_requete
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY xact_start;
```

Si des sessions restent longtemps dans cet état, examinez le code applicatif et le comportement du pool de connexions.

### 12.4 Prévention

Les applications doivent :

- terminer rapidement les transactions ;
- éviter d'attendre une interaction utilisateur à l'intérieur d'une transaction ;
- valider ou annuler les opérations même lorsqu'une erreur survient ;
- gérer correctement les connexions réutilisées ;
- surveiller les transactions laissées ouvertes.

Le réglage de délais comme `idle_in_transaction_session_timeout` peut contribuer à limiter certaines situations, mais il doit être testé soigneusement. Terminer automatiquement une session peut entraîner une erreur applicative ou l'annulation d'un travail en cours.


## 13. Maintenance des tables : VACUUM et ANALYZE

### 13.1 Pourquoi PostgreSQL nécessite-t-il une maintenance ?

Dans PostgreSQL, une opération `UPDATE` ou `DELETE` ne signifie pas que l'ancienne version de la ligne disparaît instantanément du fichier de données.

Les mécanismes MVCC nécessitent de conserver certaines versions tant qu'elles peuvent être utiles à des transactions.

Le système doit ensuite récupérer ou réutiliser l'espace associé aux versions qui ne sont plus nécessaires.

C'est l'une des raisons pour lesquelles `VACUUM` et l'autovacuum sont essentiels à l'exploitation de PostgreSQL.

### 13.2 VACUUM

La commande :

```sql
VACUUM;
```

effectue des opérations de nettoyage sur les tables de la base pour lesquelles le rôle dispose des droits nécessaires.

La forme habituelle de `VACUUM` permet notamment de récupérer de l'espace réutilisable à l'intérieur des tables.

Elle ne réduit pas nécessairement la taille physique des fichiers visibles par le système d'exploitation.

### 13.3 VACUUM ANALYZE

```sql
VACUUM (ANALYZE, VERBOSE);
```

Cette forme effectue le nettoyage et met à jour des statistiques utilisées par le planificateur de requêtes.

`VERBOSE` demande l'affichage d'informations supplémentaires sur l'opération.

La mise à jour des statistiques est importante, car un planificateur qui dispose de statistiques dépassées peut choisir un plan d'exécution inadapté.

### 13.4 ANALYZE

La commande :

```sql
ANALYZE;
```

collecte des statistiques sur les données.

Ces statistiques aident PostgreSQL à estimer le nombre de lignes concernées par les conditions, la distribution des valeurs et le coût de différentes stratégies d'exécution.

Une commande ciblée peut être utilisée :

```sql
ANALYZE public.clients;
```

Cette opération ne supprime pas les versions de lignes mortes. Elle sert principalement à actualiser les informations statistiques.

### 13.5 VACUUM FULL

La commande :

```sql
VACUUM FULL;
```

réécrit les données des tables concernées afin de récupérer davantage d'espace physique dans certains scénarios.

Elle nécessite un verrou plus fort sur les tables traitées et peut bloquer les opérations concurrentes qui doivent accéder à ces tables.

Elle peut également nécessiter de l'espace disque supplémentaire pendant l'opération.

**N'utilisez pas `VACUUM FULL` comme réflexe d'entretien quotidien.** Évaluez son intérêt, l'espace disponible, les verrous et l'impact sur la disponibilité avant d'y recourir.

### 13.6 L'autovacuum

PostgreSQL possède un mécanisme d'autovacuum qui automatise certaines opérations de nettoyage et de collecte de statistiques.

Il joue un rôle essentiel dans le fonctionnement normal d'une instance.

```text
Modifications des tables
          |
          v
Accumulation de versions de lignes
          |
          v
Seuils et conditions d'autovacuum
          |
          v
VACUUM et/ou ANALYZE automatiques
          |
          v
Maintenance régulière
```

L'autovacuum ne doit pas être désactivé globalement sans une stratégie de maintenance adaptée.

### 13.7 Surveiller l'autovacuum

```sql
SELECT
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC NULLS LAST;
```

Les nombres fournis sont des estimations statistiques. Ils ne doivent pas être considérés comme un comptage exact de chaque ligne.

Une table avec beaucoup de versions mortes estimées mérite une investigation, mais il faut également considérer son activité, les transactions longues et la fréquence de maintenance.

### 13.8 Quand lancer une maintenance manuelle ?

Une opération manuelle peut être utile après :

- une charge exceptionnelle de mises à jour ;
- une modification massive de données ;
- une importation importante ;
- une suppression de nombreuses lignes ;
- l'observation de statistiques obsolètes ;
- un besoin opérationnel précis.

La décision doit s'appuyer sur la situation de la table, l'activité, les ressources disponibles et les objectifs d'exploitation.


## 14. Surveiller le stockage et la taille des bases

### 14.1 Taille d'une base de données

PostgreSQL fournit la fonction `pg_database_size`.

```sql
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS taille
FROM pg_database
ORDER BY pg_database_size(datname) DESC;
```

Cette requête permet de repérer les bases les plus volumineuses.

### 14.2 Taille d'une table

```sql
SELECT
    pg_size_pretty(pg_relation_size('public.clients')) AS taille_table;
```

Cette fonction mesure la relation principale désignée. Elle n'inclut pas nécessairement tous les éléments associés, comme les index et certaines structures de stockage auxiliaires.

### 14.3 Taille totale d'une table avec ses index

```sql
SELECT
    pg_size_pretty(pg_total_relation_size('public.clients')) AS taille_totale;
```

Cette mesure inclut la relation et les éléments associés pris en compte par la fonction, notamment ses index et son stockage auxiliaire.

### 14.4 Classement des tables les plus volumineuses

```sql
SELECT
    schemaname,
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) AS taille_totale
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;
```

Cette requête peut aider à identifier les objets qui contribuent le plus au stockage.

### 14.5 Vérifier l'espace disque du serveur

Depuis Linux :

```bash
df -h
```

Pour examiner la taille des répertoires :

```bash
du -sh /var/lib/postgresql 2>/dev/null
```

Le chemin `/var/lib/postgresql` est courant sur Debian et Ubuntu, mais le répertoire de données réel peut être différent. Utilisez `SHOW data_directory;` pour l'identifier.

Il faut surveiller l'espace libre du volume qui héberge réellement les données, ainsi que les journaux et les fichiers temporaires.

### 14.6 Pourquoi l'espace disque est-il critique ?

Si le volume de données se remplit, PostgreSQL peut rencontrer des erreurs d'écriture et l'application peut devenir indisponible.

L'espace nécessaire au WAL, aux fichiers temporaires, aux sauvegardes et aux opérations de maintenance doit également être pris en compte.

La stratégie doit inclure des alertes avant d'atteindre une situation critique.


## 15. Index : maintenance et opérations prudentes

### 15.1 Créer un index

```sql
CREATE INDEX idx_commandes_client_id
ON public.commandes(client_id);
```

Cet index peut améliorer certaines recherches de commandes par client et certaines jointures.

Il doit être justifié par les requêtes réelles et par des mesures.

### 15.2 Créer un index concurrent

Pour limiter certains blocages des écritures pendant la création d'un index sur une table utilisée par une application, PostgreSQL propose `CREATE INDEX CONCURRENTLY`.

```sql
CREATE INDEX CONCURRENTLY idx_clients_ville
ON public.clients(ville);
```

Cette commande est utile dans certains contextes de production, mais elle comporte des contraintes et peut prendre plus longtemps que la création classique.

Elle ne peut notamment pas être exécutée dans un bloc de transaction explicite comme une opération SQL ordinaire.

Il faut vérifier les conditions et les éventuelles restrictions avant de l'employer dans un script de déploiement.

### 15.3 Pourquoi ne pas indexer toutes les colonnes ?

Chaque index consomme du stockage et doit être maintenu lorsque les données changent.

Un index inutile peut donc augmenter le coût d'insertion, de modification et de suppression.

Le choix des index repose sur :

- les requêtes fréquentes ;
- les conditions de filtrage ;
- les jointures ;
- les tris ;
- les volumes de données ;
- les sélectivités ;
- le plan d'exécution ;
- le temps mesuré avant et après.

### 15.4 Examiner les index inutilisés

```sql
SELECT
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

Les statistiques d'utilisation sont utiles, mais un nombre de scans faible ne prouve pas automatiquement qu'un index est inutile. Il peut servir à des opérations rares mais importantes.

Les compteurs peuvent aussi être réinitialisés lors de certains événements.

Ne supprimez pas un index uniquement parce que `idx_scan` vaut zéro dans un instantané isolé.

### 15.5 Reconstruire un index

PostgreSQL propose notamment :

```sql
REINDEX INDEX CONCURRENTLY public.idx_clients_ville;
```

Cette opération reconstruit l'index en limitant certains blocages des opérations concurrentes.

Elle n'est pas gratuite et comporte des contraintes. Elle doit être envisagée après un diagnostic, par exemple lorsqu'un index est suspecté d'être corrompu ou qu'une reconstruction est justifiée par l'état observé.

Il ne faut pas reconstruire systématiquement tous les index sans raison.


## 16. Diagnostiquer les requêtes lentes

Une requête lente peut provenir :

- d'un accès à trop de lignes ;
- d'un index absent ou inadapté ;
- d'une jointure coûteuse ;
- d'un tri important ;
- d'une estimation incorrecte du nombre de lignes ;
- d'un verrou ;
- d'une attente liée au stockage ;
- d'une concurrence élevée ;
- d'une dépendance applicative lente.

### 16.1 Utiliser EXPLAIN

```sql
EXPLAIN
SELECT *
FROM public.commandes
WHERE client_id = 1;
```

`EXPLAIN` affiche le plan d'exécution choisi par PostgreSQL pour la requête.

Le plan permet notamment de voir :

- la stratégie de lecture des tables ;
- l'utilisation éventuelle d'un index ;
- les opérations de jointure ;
- les estimations du nombre de lignes ;
- les coûts estimés.

### 16.2 Utiliser EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM public.commandes
WHERE client_id = 1;
```

Cette forme exécute réellement la requête et fournit des mesures observées, ainsi que des informations sur les accès aux buffers lorsque disponibles.

Attention : `EXPLAIN ANALYZE` exécute l'instruction analysée. Pour une requête de modification, cela peut modifier les données. Ne l'utilisez pas aveuglément sur des opérations destructrices.

### 16.3 Comprendre le parcours séquentiel

Un plan contenant `Seq Scan` indique que PostgreSQL parcourt les lignes de la table selon une stratégie de parcours séquentiel.

Ce n'est pas automatiquement une erreur.

Pour une petite table ou une requête qui doit lire une grande proportion des lignes, un parcours séquentiel peut être plus efficace qu'un accès par index.

### 16.4 Comprendre un parcours par index

Un plan contenant `Index Scan` ou une stratégie d'accès indexée indique que le planificateur utilise un index pour trouver des données.

Un index ne garantit pas un temps faible : si la requête nécessite de nombreuses lignes ou des lectures dispersées, l'accès peut rester coûteux.

### 16.5 Comparer les estimations et les résultats

Examinez les lignes estimées et les lignes observées :

```text
Index Scan
  estimated rows=10
  actual rows=5000
```

Cet exemple est purement illustratif.

Un écart important peut indiquer que les statistiques ne reflètent pas correctement la distribution des données ou que la requête possède un comportement particulier.

Une opération `ANALYZE` peut être pertinente, mais elle ne résout pas tous les problèmes de planification.

### 16.6 Ordre de travail recommandé

```text
Identifier la requête
        |
        v
Mesurer sa durée
        |
        v
Examiner EXPLAIN
        |
        v
Comparer les estimations
        |
        v
Examiner EXPLAIN ANALYZE
        |
        v
Identifier le coût dominant
        |
        v
Tester une amélioration
        |
        v
Comparer les résultats
```


## 17. Sauvegarde : définir une stratégie

Une stratégie de sauvegarde doit répondre à deux questions fondamentales :

1. Quelle quantité de données peut-on se permettre de perdre ?
2. Combien de temps peut-on se permettre de rester indisponible ?

### 17.1 RPO et RTO

**RPO — Recovery Point Objective**

Le RPO représente la perte maximale de données acceptable, exprimée en temps.

Un RPO de quinze minutes signifie, dans le modèle d'exigence considéré, que l'on cherche à limiter la perte de données à l'équivalent d'au plus quinze minutes de changements.

**RTO — Recovery Time Objective**

Le RTO représente la durée maximale visée pour restaurer un service après un incident.

Un RTO d'une heure signifie que l'organisation vise un retour au service en une heure ou moins.

Ces objectifs doivent être réalistes et testés.

### 17.2 Schéma d'une stratégie de sauvegarde

```text
Base PostgreSQL
       |
       +------------------------+
       |                        |
       v                        v
Sauvegardes logiques      Sauvegarde physique
       |                        |
       v                        v
Archive de données        Copie du cluster
       |                        |
       +-----------+------------+
                   |
                   v
            Stockage séparé
                   |
                   v
          Tests de restauration
```

La stratégie exacte dépend du RPO, du RTO, de la taille des données, du trafic et du budget.

### 17.3 Trois approches de sauvegarde PostgreSQL

Les approches principales comprennent :

- les sauvegardes logiques, par exemple avec `pg_dump` ;
- les sauvegardes physiques ;
- les sauvegardes physiques combinées à un archivage continu des WAL.

Ces méthodes ne répondent pas exactement aux mêmes besoins. Elles ont des contraintes distinctes de taille, de restauration, de portabilité et de granularité de récupération.

### 17.4 Sauvegardes logiques avec pg_dump

```bash
pg_dump -Fc -d boutique_sql -f boutique_sql.dump
```

Cette commande crée une archive logique au format personnalisé.

Il faut disposer des droits nécessaires pour se connecter à la base et lire les objets concernés.

Dans une installation utilisant l'authentification locale par pair, on peut exécuter l'outil sous le compte système `postgres` lorsque cela correspond à l'architecture :

```bash
sudo -u postgres pg_dump -Fc boutique_sql -f /tmp/boutique_sql.dump
```

Le fichier est un exemple de chemin de formation. En production, les sauvegardes doivent être écrites dans un emplacement protégé, avec une politique de rotation et de transfert appropriée.

### 17.5 Sauvegarder les objets globaux

Les sauvegardes d'une base avec `pg_dump` ne couvrent pas à elles seules tous les objets globaux de l'instance, tels que les rôles.

Une sauvegarde séparée des objets globaux peut être obtenue avec :

```bash
sudo -u postgres pg_dumpall --globals-only \
  > /tmp/postgres_globals.sql
```

La redirection est exécutée par le shell de l'utilisateur qui lance la commande, et les permissions du fichier doivent être contrôlées.

Cette sauvegarde peut contenir des informations sensibles relatives aux rôles. Elle doit être protégée.

### 17.6 Vérifier le fichier de sauvegarde

```bash
ls -lh /tmp/boutique_sql.dump
```

Pour examiner le contenu de l'archive :

```bash
pg_restore --list /tmp/boutique_sql.dump
```

Ces contrôles permettent de repérer certains problèmes, mais ils ne prouvent pas à eux seuls que toutes les données seront restaurées correctement.

Seul un test de restauration dans un environnement contrôlé permet de vérifier la capacité de récupération de façon plus complète.


## 18. Restaurer une sauvegarde PostgreSQL

### 18.1 Restaurer dans une base de test

Il est préférable de restaurer une sauvegarde dans une nouvelle base plutôt que d'écraser immédiatement une base existante.

Créez la base de test :

```bash
sudo -u postgres createdb boutique_sql_restore_test
```

Puis restaurez l'archive :

```bash
sudo -u postgres pg_restore \
  -d boutique_sql_restore_test \
  /tmp/boutique_sql.dump
```

Les permissions nécessaires doivent être disponibles. Les propriétaires et les rôles de destination doivent être compatibles avec la stratégie de restauration.

### 18.2 Vérifier les tables

```bash
sudo -u postgres psql -d boutique_sql_restore_test
```

Puis :

```text
\dt
```

Examinez la structure de quelques tables et les contraintes.

### 18.3 Vérifier le contenu

```sql
SELECT COUNT(*) FROM public.clients;
SELECT COUNT(*) FROM public.produits;
SELECT COUNT(*) FROM public.commandes;
SELECT COUNT(*) FROM public.lignes_commande;
```

Les nombres de lignes sont des indicateurs de contrôle, mais ils ne suffisent pas à démontrer que toutes les données, contraintes, fonctions et relations ont été restaurées correctement.

### 18.4 Vérifier l'application

Pour une restauration destinée à reprendre un service, il faut aussi tester les requêtes métier et les dépendances applicatives.

Une restauration peut être techniquement réussie tout en rencontrant des problèmes de privilèges, de versions d'extension ou de configuration de l'application.

### 18.5 Restaurer des propriétaires et des privilèges

Une archive peut contenir des instructions qui attribuent des objets à des rôles présents sur le système d'origine.

Lors d'une restauration dans un environnement différent, les rôles peuvent être absents ou les privilèges peuvent différer.

Il faut choisir explicitement si l'objectif est :

- de reproduire l'environnement d'origine ;
- de restaurer les données dans une nouvelle structure ;
- de remplacer la propriété ou les privilèges selon un modèle prévu.

Ne contournez pas un échec en donnant le statut superutilisateur à tous les rôles.


## 19. Restaurations et reprise après incident

### 19.1 Une sauvegarde n'est pas une stratégie complète

Une sauvegarde peut être inutilisable si :

- le fichier est corrompu ;
- la clé de déchiffrement est perdue ;
- les rôles nécessaires n'existent plus ;
- la version logicielle n'est pas compatible avec la procédure ;
- le stockage de sauvegarde est indisponible ;
- la procédure de restauration n'est pas documentée.

Une stratégie robuste doit aussi prévoir des tests réguliers et des contrôles d'intégrité.

### 19.2 Règle de séparation

Évitez de placer toutes les sauvegardes sur le même volume que les données principales.

Si le disque est perdu ou si une erreur administrative détruit les données locales, les sauvegardes peuvent être perdues simultanément.

Une stratégie appropriée peut combiner plusieurs emplacements de stockage et une copie qui n'est pas directement modifiable par le compte qui administre la base.

### 19.3 Préparer la procédure de reprise

Une procédure de reprise doit décrire :

1. comment détecter et qualifier l'incident ;
2. comment empêcher d'aggraver la perte de données ;
3. quelle sauvegarde sélectionner ;
4. comment restaurer les objets et les données ;
5. comment vérifier l'intégrité ;
6. comment rétablir les accès ;
7. comment valider l'application ;
8. comment remettre le service à disposition ;
9. comment documenter l'incident et ses causes.

Le DBA doit également savoir qui est autorisé à approuver une restauration et quelles données peuvent être perdues selon le point de récupération retenu.


## 20. WAL et récupération à un instant donné

### 20.1 Qu'est-ce que le WAL ?

WAL signifie *Write-Ahead Logging*.

PostgreSQL enregistre des informations de modification dans le journal WAL. Ce mécanisme est central pour la récupération après une panne et pour plusieurs architectures de sauvegarde et de réplication.

Schéma simplifié :

```text
Transaction
     |
     v
Modifications SQL
     |
     v
Enregistrement des informations WAL
     |
     v
Validation de la transaction
     |
     v
Les données sont récupérables selon
les garanties du serveur
```

Le WAL ne remplace pas une sauvegarde complète. Il complète d'autres mécanismes de persistance et de récupération.

### 20.2 Que signifie PITR ?

PITR signifie *Point-In-Time Recovery*, ou récupération à un instant donné.

Cette stratégie permet, lorsque l'architecture de sauvegarde et d'archivage est correctement configurée, de restaurer une base dans un état correspondant à un point temporel cible.

Elle peut être utile lorsqu'une suppression accidentelle ou une modification erronée a été validée.

### 20.3 Principe de la récupération

```text
Sauvegarde de base
       |
       v
Archivage continu des WAL
       |
       +---- WAL suivants
       |
       v
Restauration de la sauvegarde
       |
       v
Rejeu des WAL disponibles
       |
       v
Point de récupération demandé
```

Il faut disposer d'une sauvegarde de base appropriée et des journaux WAL nécessaires pour atteindre le point de récupération souhaité.

Une simple archive produite par `pg_dump` ne constitue pas à elle seule une configuration PITR.

### 20.4 Pourquoi l'archivage doit être surveillé

L'archivage WAL peut échouer à cause :

- d'un stockage plein ;
- d'un défaut de réseau ;
- de permissions incorrectes ;
- d'une destination indisponible ;
- d'une erreur de commande d'archivage.

Une accumulation de journaux non archivés peut consommer beaucoup d'espace disque et affecter la disponibilité.

La configuration de l'archivage et sa surveillance doivent être considérées comme des éléments de l'exploitation.

### 20.5 Documents à consulter

La mise en place complète d'une stratégie PITR nécessite une configuration spécifique et des tests de restauration. Elle dépasse une simple commande `pg_dump`.

Avant de la déployer, consultez la documentation PostgreSQL sur la sauvegarde physique, l'archivage continu et la récupération à un instant donné.


## 21. Réplication : principes d'administration

La réplication consiste à maintenir une ou plusieurs copies des données d'un serveur vers d'autres instances.

Elle peut servir à améliorer la disponibilité, faciliter certaines opérations de reprise ou répartir des lectures lorsque l'application et l'architecture le permettent.

### 21.1 Architecture primaire et secondaire

```text
                APPLICATIONS
                      |
                      v
              +---------------+
              | PRIMAIRE      |
              | PostgreSQL    |
              +-------+-------+
                      |
                      | WAL
                      v
              +---------------+
              | SECONDAIRE    |
              | Standby       |
              +---------------+
```

Le primaire accepte les écritures dans une architecture classique de réplication physique.

Le serveur secondaire reçoit et rejoue les informations WAL, ce qui lui permet de suivre l'état du primaire.

### 21.2 Réplication asynchrone

En réplication asynchrone, le primaire peut valider une transaction sans attendre que le serveur secondaire confirme que cette transaction est durablement reçue.

Cette approche réduit certains délais de validation, mais implique qu'une partie récente des transactions peut ne pas avoir atteint le secondaire au moment d'une panne.

Le retard de réplication doit donc être surveillé en fonction du RPO visé.

### 21.3 Réplication synchrone

En réplication synchrone, le primaire peut attendre une confirmation du ou des serveurs requis par la politique de réplication avant de confirmer certaines transactions.

Cela peut réduire le risque de perte de données reconnues comme validées selon les garanties configurées, mais peut augmenter la latence et dépendre de la disponibilité des secondaires requis.

La configuration doit être conçue en tenant compte du nombre de réplicas, des conditions de panne et du comportement attendu du service.

### 21.4 Réplication et sauvegarde

La réplication ne remplace pas une stratégie de sauvegarde.

Si une suppression ou une modification erronée est exécutée sur le primaire, elle peut également être répliquée sur le secondaire.

```text
Erreur de suppression sur le primaire
                  |
                  v
             WAL propagé
                  |
                  v
        Suppression sur le secondaire
```

Il faut conserver des sauvegardes récupérables indépendamment du mécanisme de réplication.

### 21.5 Supervision de la réplication

Sur le primaire, une vue utile est :

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

Les informations de retard peuvent être nulles ou avoir un sens différent selon l'état de la connexion et les informations disponibles.

Elles doivent être interprétées avec les métriques WAL et l'état réel des serveurs.

### 21.6 Conditions préalables

Une configuration de réplication physique nécessite notamment :

- des paramètres adaptés sur le primaire ;
- une connexion réseau autorisée ;
- un rôle de réplication correctement configuré ;
- des règles d'authentification spécifiques ;
- une copie de base cohérente sur le secondaire ;
- des paramètres de connexion et de récupération ;
- une procédure de promotion et de retour au service documentée.

Un serveur standby peut nécessiter une reconstruction ou une resynchronisation après certains incidents.

La mise en production d'une architecture de réplication exige des tests de panne, pas seulement la vérification qu'une connexion de réplication existe.


## 22. Planifier les opérations de maintenance

L'administration régulière doit suivre un programme adapté au service.

### 22.1 Contrôles quotidiens

Les contrôles quotidiens peuvent inclure :

- état des services ;
- erreurs récentes ;
- espace disque disponible ;
- taux d'échec des sauvegardes ;
- connexions et requêtes bloquées ;
- retard de réplication lorsqu'il existe ;
- alertes importantes de supervision.

### 22.2 Contrôles périodiques

Selon le système, les contrôles périodiques peuvent comprendre :

- vérification des restaurations de sauvegarde ;
- évolution de la taille des bases ;
- examen des requêtes lentes ;
- analyse des index ;
- examen des statistiques d'utilisation ;
- examen des transactions longues ;
- vérification des rôles et privilèges ;
- revue des paramètres de configuration.

### 22.3 Contrôles avant un changement important

Avant une modification de schéma, une mise à jour logicielle ou un changement de configuration :

1. vérifier l'environnement ciblé ;
2. lire les dépendances ;
3. vérifier les sauvegardes disponibles ;
4. estimer l'impact sur les verrous et les écritures ;
5. tester la modification ;
6. prévoir le retour arrière ;
7. planifier la fenêtre de déploiement si nécessaire ;
8. vérifier le service après l'opération.

Les modifications de schéma sur de grandes tables peuvent avoir un impact important sur les applications et ne doivent pas être assimilées à des opérations de laboratoire.


## 23. Automatiser sans perdre le contrôle

Les scripts permettent de rendre les contrôles répétables et de limiter les opérations manuelles.

Un script d'administration devrait :

- vérifier ses prérequis ;
- cibler explicitement l'instance et la base ;
- vérifier les codes de retour ;
- enregistrer les résultats nécessaires ;
- échouer clairement en cas de problème ;
- éviter les secrets en clair ;
- ne pas supprimer ou modifier des données sans validation prévue.

### 23.1 Exemple de contrôle SQL

Créez un fichier `controle_base.sql` :

```sql
SELECT current_database() AS base_courante;
SELECT current_user AS role_courant;
SELECT now() AS heure_controle;

SELECT
    datname,
    numbackends,
    deadlocks,
    conflicts
FROM pg_stat_database
WHERE datname = current_database();
```

Cette série de requêtes fournit quelques informations de diagnostic. Ce n'est pas un système de supervision complet.

### 23.2 Exécuter le contrôle

```bash
psql -X -v ON_ERROR_STOP=1 \
  -d boutique_sql \
  -f controle_base.sql
```

`-X` évite le chargement des fichiers de démarrage personnels de `psql`.

`ON_ERROR_STOP=1` demande au client de s'arrêter lorsqu'une erreur SQL se produit dans le fichier.

L'authentification doit être configurée pour que cette commande puisse se connecter au serveur. Ne contournez pas les règles d'accès en utilisant systématiquement un superutilisateur.

### 23.3 Planifier un contrôle

Un mécanisme de planification comme `cron` ou un service systemd temporisé peut exécuter certains contrôles périodiques.

Cependant, un simple script qui s'exécute sans produire d'alerte en cas d'échec n'apporte qu'une valeur limitée.

L'automatisation doit inclure des contrôles de résultat, la collecte des logs et une stratégie d'alerte.


## 24. Mise à jour et montée de version

Les mises à jour sont importantes pour la sécurité et la stabilité, mais elles doivent être distinguées selon leur nature.

### 24.1 Mises à jour mineures

Les mises à jour au sein d'une même version majeure corrigent notamment des défauts et des problèmes de sécurité.

Elles doivent être appliquées selon la politique de maintenance de l'organisation, avec une préparation adaptée à la criticité du service.

Même une mise à jour qui ne nécessite pas une migration des données peut demander un redémarrage du service ou une intervention planifiée.

### 24.2 Mises à niveau majeures

Une mise à niveau de version majeure doit être planifiée différemment.

Elle peut nécessiter :

- une sauvegarde complète ;
- une vérification de compatibilité ;
- la validation des extensions ;
- un examen des changements de paramètres ;
- une stratégie de migration ;
- une restauration de test ;
- une fenêtre de maintenance ;
- un plan de retour arrière.

Ne supposez pas qu'il suffit d'installer un nouveau paquet puis de redémarrer le service.

### 24.3 Méthodes de migration

Selon le besoin, la migration peut notamment reposer sur :

- une sauvegarde logique et une restauration ;
- l'outil `pg_upgrade` ;
- une stratégie utilisant la réplication et une bascule organisée ;
- un processus spécifique prévu par l'infrastructure.

Chaque méthode a ses contraintes de durée d'indisponibilité, de capacité, de compatibilité et de récupération.

### 24.4 Préparer un changement de version

Avant toute migration :

1. identifier les versions du client et du serveur ;
2. examiner les extensions installées ;
3. établir une sauvegarde restaurable ;
4. tester la migration dans un environnement comparable ;
5. mesurer la durée ;
6. valider les fonctions métier ;
7. documenter les opérations et le retour arrière.

La durée prévue doit provenir de tests ou d'une estimation fondée sur la taille réelle et la complexité de la base.


## 25. Diagnostic des problèmes courants

### 25.1 PostgreSQL ne démarre pas

Commencez par :

```bash
sudo systemctl status postgresql
```

Puis :

```bash
sudo journalctl -u postgresql -n 100
```

Examinez les journaux PostgreSQL configurés, car le journal systemd peut ne pas contenir toute l'information.

Causes possibles :

- syntaxe invalide d'un paramètre ;
- port déjà occupé ;
- permissions incorrectes ;
- stockage indisponible ;
- espace disque insuffisant ;
- cluster différent de celui attendu ;
- fichiers de récupération ou d'état nécessitant une analyse spécifique.

Ne supprimez pas des fichiers dans le répertoire de données pour tenter de forcer le démarrage. Certaines opérations peuvent provoquer une perte de données.

### 25.2 Connexion refusée

Contrôlez :

```bash
sudo ss -lntp | grep ':5432'
```

Puis vérifiez :

```sql
SHOW listen_addresses;
SHOW port;
```

Si l'application est distante, contrôlez également l'adresse IP, le routage, le pare-feu et les règles d'authentification.

### 25.3 Authentification refusée

Vérifiez :

- que le rôle existe ;
- qu'il dispose du droit `LOGIN` ;
- qu'une règle `pg_hba.conf` correspond à la connexion ;
- que la méthode d'authentification est compatible ;
- que le secret utilisé est correct ;
- que le client tente de se connecter à la base attendue.

Un message d'authentification refusée ne doit pas être résolu en ouvrant l'accès à tout le réseau.

### 25.4 Base en lecture seule

Une base en lecture seule peut être associée à une configuration particulière, à un serveur standby ou à une transaction dont les contraintes empêchent la modification.

Examinez notamment :

```sql
SELECT
    pg_is_in_recovery() AS en_recuperation;
```

Un résultat vrai indique que le serveur est en mode de récupération, comme un standby physique.

Ne tentez pas de transformer un standby en primaire sans avoir vérifié l'architecture de réplication et la procédure de bascule.

### 25.5 Espace disque presque plein

Depuis Linux :

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

Il faut déterminer si l'espace est consommé par les données, les index, les WAL, les journaux, les sauvegardes ou d'autres fichiers du système.

Ne supprimez pas manuellement des fichiers WAL ou des fichiers internes PostgreSQL pour libérer de l'espace. Une telle action peut compromettre la récupération et l'intégrité du serveur.

### 25.6 Requêtes qui semblent bloquées

Consultez les requêtes actives et les bloqueurs à l'aide des vues `pg_stat_activity` et des fonctions de diagnostic présentées plus haut.

Un processus qui attend peut dépendre d'un verrou, d'une ressource réseau ou d'une autre opération.

Il faut identifier la cause avant d'annuler ou de terminer une session.

### 25.7 Sauvegarde qui échoue

Contrôlez :

- le code de retour de la commande ;
- la connectivité et l'authentification ;
- les privilèges nécessaires ;
- l'espace disque disponible ;
- les permissions sur le fichier de sortie ;
- les logs et messages du programme ;
- la taille et l'intégrité apparente de l'archive.

Ne considérez jamais une sauvegarde comme réussie simplement parce qu'un fichier portant le nom attendu existe.


## 26. Travaux pratiques guidés avec corrigés

Les exercices doivent être effectués sur une base de formation.

### TP 1 — Identifier les paramètres du serveur

**Objectif :** identifier les fichiers de configuration et les caractéristiques actives.

Connectez-vous :

```bash
sudo -u postgres psql -d boutique_sql
```

Exécutez :

```sql
SHOW config_file;
SHOW hba_file;
SHOW data_directory;
SHOW port;
SHOW listen_addresses;
```

Puis :

```sql
SELECT
    name,
    setting,
    source,
    context,
    pending_restart
FROM pg_settings
WHERE name IN (
    'max_connections',
    'shared_buffers',
    'work_mem',
    'listen_addresses',
    'port'
);
```

**Corrigé :**

Les premières requêtes affichent les chemins et paramètres actifs. La seconde donne des détails sur plusieurs valeurs et indique si un redémarrage est en attente pour certains changements.

### TP 2 — Créer un rôle de lecture

**Objectif :** accorder des privilèges limités.

Dans la base `boutique_sql`, avec un rôle d'administration approprié :

```sql
CREATE ROLE boutique_lecture LOGIN;
GRANT CONNECT ON DATABASE boutique_sql TO boutique_lecture;
GRANT USAGE ON SCHEMA public TO boutique_lecture;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO boutique_lecture;
```

Définissez un mot de passe adapté en utilisant une méthode sûre pour votre environnement.

Vérifiez que le rôle peut consulter les données attendues, mais qu'une tentative de modification échoue si aucun privilège de modification ne lui a été accordé.

**Corrigé :**

Le rôle dispose de l'accès à la base, de l'utilisation du schéma public et de droits de lecture sur les tables existantes concernées. Les privilèges futurs doivent être gérés séparément avec les privilèges par défaut adaptés au rôle créateur des objets.

### TP 3 — Examiner les connexions

```sql
SELECT
    usename,
    datname,
    state,
    COUNT(*) AS nombre
FROM pg_stat_activity
GROUP BY usename, datname, state
ORDER BY nombre DESC;
```

**Corrigé :**

La requête regroupe les sessions visibles par rôle, base et état. Une valeur élevée de sessions inactives peut être normale pour une application qui utilise un pool de connexions. Il faut examiner l'utilisation réelle avant de conclure à une anomalie.

### TP 4 — Détecter une transaction ouverte

Ouvrez deux sessions SQL pour le laboratoire.

Dans la première :

```sql
BEGIN;

UPDATE clients
SET ville = 'Laboratoire'
WHERE id = 1;
```

Ne validez pas encore la transaction.

Dans la seconde, examinez les sessions :

```sql
SELECT
    pid,
    usename,
    state,
    xact_start,
    now() - xact_start AS age_transaction,
    LEFT(query, 150) AS requete
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start;
```

Vous devriez pouvoir observer la transaction encore ouverte dans la première session si les droits et la visibilité permettent de la consulter.

Dans la première session, terminez ensuite l'opération :

```sql
ROLLBACK;
```

**Corrigé :**

Le `ROLLBACK` annule la modification non validée de cette transaction. L'exercice montre aussi qu'une transaction peut rester ouverte entre deux requêtes.

### TP 5 — Examiner un plan de requête

```sql
EXPLAIN
SELECT *
FROM commandes
WHERE client_id = 1;
```

Puis :

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM commandes
WHERE client_id = 1;
```

**Corrigé :**

La première instruction présente le plan estimé. La seconde exécute la requête et fournit des informations mesurées. Sur une table minuscule, un parcours séquentiel peut être parfaitement normal.

### TP 6 — Observer la maintenance

```sql
SELECT
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC NULLS LAST;
```

Puis, dans un environnement de formation :

```sql
VACUUM (ANALYZE, VERBOSE) public.clients;
```

**Corrigé :**

La première requête expose des statistiques de table. La seconde réalise une maintenance et une collecte de statistiques sur `clients`. La commande `VACUUM` ne doit pas être exécutée à l'intérieur d'un bloc de transaction explicite.

### TP 7 — Sauvegarder puis restaurer

Sauvegardez la base :

```bash
sudo -u postgres pg_dump -Fc boutique_sql -f /tmp/boutique_sql.dump
```

Créez une base de test :

```bash
sudo -u postgres createdb boutique_sql_restore_test
```

Restaurez l'archive :

```bash
sudo -u postgres pg_restore \
  -d boutique_sql_restore_test \
  /tmp/boutique_sql.dump
```

Vérifiez le résultat :

```bash
sudo -u postgres psql -d boutique_sql_restore_test \
  -c "SELECT COUNT(*) FROM clients;"
```

**Corrigé :**

La sauvegarde et la restauration doivent s'achever sans erreur, et les vérifications métier doivent correspondre aux données attendues.

Une commande qui termine sans message d'erreur ne suffit pas à démontrer la capacité de reprise. Il faut contrôler les objets, les privilèges et les données importantes.

### TP 8 — Vérifier le rôle des index

Créez un index de laboratoire :

```sql
CREATE INDEX idx_commandes_client_id
ON public.commandes(client_id);
```

Examinez la requête :

```sql
EXPLAIN
SELECT *
FROM commandes
WHERE client_id = 1;
```

**Corrigé :**

L'index existe, mais PostgreSQL peut toujours choisir un parcours séquentiel si la table est petite ou si ce choix est estimé moins coûteux. La simple présence d'un index ne garantit pas qu'il sera utilisé.

### TP 9 — Examiner l'espace disque

```bash
df -h
```

Puis :

```sql
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS taille
FROM pg_database
ORDER BY pg_database_size(datname) DESC;
```

**Corrigé :**

La commande Linux mesure l'espace des systèmes de fichiers. La requête PostgreSQL mesure la taille des bases de données. Ces mesures sont complémentaires et ne décrivent pas exactement le même périmètre.

### TP 10 — Préparer une fiche d'incident

Simulez un problème dans le laboratoire, par exemple un rôle sans privilège de lecture ou une connexion dirigée vers une base inexistante.

Documentez :

- le symptôme ;
- le message d'erreur ;
- la première commande de diagnostic ;
- la cause identifiée ;
- la correction minimale ;
- le test effectué après correction.

**Corrigé :**

Une bonne fiche d'incident décrit la cause réelle, la procédure de correction et la vérification du retour au fonctionnement normal. Elle ne se limite pas à la commande qui a finalement supprimé le symptôme.


## 27. Défi final : administrer une base dans des conditions proches de l'exploitation

### Objectif

Mettre en place une petite procédure d'administration complète pour la base `boutique_sql`.

### Cahier des charges

La procédure doit couvrir :

- l'identification de la version et des fichiers de configuration ;
- l'état du service PostgreSQL ;
- la gestion des rôles ;
- la vérification des privilèges ;
- la surveillance des connexions ;
- l'identification d'une transaction longue ;
- l'examen des statistiques de maintenance ;
- la mesure de la taille de la base ;
- la sauvegarde et la restauration de test ;
- la documentation d'une anomalie.

### Étape A — Inspection

Exécutez :

```sql
SELECT version();
SHOW config_file;
SHOW hba_file;
SHOW data_directory;
SHOW port;
```

Enregistrez les résultats utiles dans une fiche d'administration, en évitant de publier des informations sensibles.

### Étape B — Sécurité

Vérifiez les rôles :

```text
\du
```

Identifiez le rôle utilisé par l'application et contrôlez ses privilèges.

Confirmez que l'application n'utilise pas un superutilisateur pour ses opérations ordinaires.

### Étape C — Surveillance

Exécutez :

```sql
SELECT
    datname,
    numbackends,
    deadlocks,
    conflicts
FROM pg_stat_database;
```

Puis examinez les requêtes actives et les transactions longues.

### Étape D — Maintenance

Examinez les statistiques des tables et les dates d'autovacuum.

Identifiez une table de formation et examinez son plan d'exécution pour une requête connue.

### Étape E — Sauvegarde et restauration

Créez une sauvegarde de la base, restaurez-la dans un nouvel environnement de test et vérifiez les éléments importants.

### Étape F — Rapport final

Produisez un rapport contenant :

1. la version du serveur ;
2. l'état du service ;
3. les rôles et privilèges importants ;
4. les paramètres de connexion pertinents ;
5. les observations sur les sessions et transactions ;
6. les mesures de stockage ;
7. le résultat de la sauvegarde et de la restauration ;
8. les anomalies découvertes ;
9. les actions correctives ;
10. les points à surveiller lors de la prochaine maintenance.

### Critères de réussite

Le défi est réussi si les contrôles sont reproductibles, si les changements de sécurité sont vérifiés, si une sauvegarde est restaurable et si les anomalies sont documentées avec une cause et une correction explicites.


## 28. Checklist d'administration quotidienne

### Service

- [ ] Le service PostgreSQL est opérationnel.
- [ ] La bonne instance ou le bon cluster est ciblé.
- [ ] Les journaux ne révèlent pas d'erreur critique.
- [ ] Les ports et interfaces d'écoute correspondent à l'architecture prévue.

### Sécurité

- [ ] Les rôles utilisent les privilèges nécessaires uniquement.
- [ ] Aucun rôle applicatif ne dispose de privilèges superutilisateur sans justification.
- [ ] Les accès réseau correspondent aux règles attendues.
- [ ] Les secrets et fichiers sensibles sont protégés.
- [ ] Les rôles inutilisés sont examinés.

### Performance

- [ ] Les connexions sont surveillées.
- [ ] Les transactions longues sont examinées.
- [ ] Les requêtes lentes peuvent être identifiées.
- [ ] Les blocages et verrous anormaux sont analysés.
- [ ] Les statistiques des tables sont examinées périodiquement.

### Stockage

- [ ] L'espace disque est suffisant.
- [ ] La taille des bases est surveillée.
- [ ] La croissance du WAL est suivie si nécessaire.
- [ ] Les fichiers de sauvegarde ne remplissent pas le volume des données.

### Sauvegarde et reprise

- [ ] Les sauvegardes récentes ont été vérifiées.
- [ ] Les erreurs de sauvegarde génèrent une alerte.
- [ ] Les fichiers sont protégés et conservés selon la politique.
- [ ] Une restauration de test a été effectuée périodiquement.
- [ ] Les objectifs RPO et RTO sont documentés.
- [ ] La procédure de reprise est connue.

### Maintenance

- [ ] L'autovacuum fonctionne selon les besoins.
- [ ] Les statistiques sont actualisées lorsque cela est nécessaire.
- [ ] Les index sont évalués sur la base de mesures.
- [ ] Les mises à jour suivent une procédure contrôlée.
- [ ] Les modifications importantes ont un plan de retour arrière.


## 29. Glossaire

**Autovacuum** : mécanisme PostgreSQL qui automatise certaines opérations de nettoyage et de mise à jour des statistiques.

**Backend** : processus associé à une session cliente et chargé de traiter ses requêtes dans l'architecture PostgreSQL classique.

**DBA** : administrateur de bases de données.

**Cluster PostgreSQL** : instance organisée autour d'un répertoire de données et de ses configurations, pouvant héberger plusieurs bases dans le sens PostgreSQL du terme.

**EXPLAIN** : instruction permettant d'afficher un plan d'exécution estimé.

**EXPLAIN ANALYZE** : variante qui exécute réellement la requête et fournit des mesures observées.

**Index** : structure auxiliaire destinée à accélérer certains accès aux données.

**MVCC** : mécanisme de concurrence multi-version utilisé pour gérer la visibilité des versions de lignes.

**pg_dump** : outil de sauvegarde logique d'une base PostgreSQL.

**pg_restore** : outil de restauration des archives produites dans certains formats par `pg_dump`.

**pg_hba.conf** : fichier PostgreSQL qui définit les règles d'authentification des clients.

**PITR** : récupération d'une base à un instant donné, lorsque les sauvegardes et journaux nécessaires sont disponibles.

**RPO** : objectif concernant la perte maximale de données acceptable.

**RTO** : objectif concernant le délai maximal visé pour rétablir un service.

**Rôle PostgreSQL** : identité de la base qui peut posséder des objets, recevoir des privilèges et, si elle dispose de `LOGIN`, s'authentifier.

**Transaction** : ensemble d'opérations soumises à un mécanisme de validation et d'annulation.

**VACUUM** : commande qui récupère de l'espace réutilisable et participe à la maintenance des tables.

**WAL** : journal des modifications utilisé notamment pour la récupération et la réplication.

**Verrou** : mécanisme qui coordonne les opérations concurrentes afin de préserver les règles de cohérence.

**Réplication** : propagation des modifications d'une instance vers une ou plusieurs copies.

**Sauvegarde logique** : représentation exportée des objets et données d'une base, destinée à la restauration ou à la migration.

**Sauvegarde physique** : copie adaptée des structures physiques d'un cluster ou des fichiers nécessaires à sa restauration.


## 30. Documentation officielle

Les paramètres et commandes peuvent différer selon la version du serveur. Consultez la documentation correspondant à la version réellement installée.

### PostgreSQL

- Documentation générale :  
  https://www.postgresql.org/docs/current/

- Administration du serveur :  
  https://www.postgresql.org/docs/current/admin.html

- Configuration et paramètres :  
  https://www.postgresql.org/docs/current/runtime-config.html

- Connexions et authentification :  
  https://www.postgresql.org/docs/current/client-authentication.html

- Fichier pg_hba.conf :  
  https://www.postgresql.org/docs/current/auth-pg-hba-conf.html

- Rôles et privilèges :  
  https://www.postgresql.org/docs/current/user-manag.html

- Surveillance et statistiques :  
  https://www.postgresql.org/docs/current/monitoring.html

- VACUUM :  
  https://www.postgresql.org/docs/current/sql-vacuum.html

- Sauvegarde et restauration :  
  https://www.postgresql.org/docs/current/backup.html

- Archivage continu et PITR :  
  https://www.postgresql.org/docs/current/continuous-archiving.html

- Réplication et serveurs standby :  
  https://www.postgresql.org/docs/current/warm-standby.html

- EXPLAIN :  
  https://www.postgresql.org/docs/current/sql-explain.html

- CREATE INDEX :  
  https://www.postgresql.org/docs/current/sql-createindex.html

- REINDEX :  
  https://www.postgresql.org/docs/current/sql-reindex.html

### Linux et Debian

- systemd :  
  https://www.freedesktop.org/software/systemd/man/

- Documentation Debian :  
  https://www.debian.org/doc/

- Documentation Ubuntu Server :  
  https://documentation.ubuntu.com/server/


## Conclusion générale

L'administration d'une base de données repose sur une combinaison de sécurité, de maintenance, de surveillance, de gestion des performances et de préparation à la récupération.

Un DBA doit savoir diagnostiquer une connexion refusée, identifier les transactions longues, examiner le stockage, comprendre l'autovacuum, contrôler les privilèges et restaurer des données dans un environnement maîtrisé.

Les commandes d'administration ne doivent pas être exécutées de manière mécanique. Une opération comme la suppression d'une session, une reconstruction d'index, une modification des connexions ou un changement d'authentification peut avoir des conséquences sur l'application et sur la disponibilité du service.

Le parcours recommandé est le suivant :

```text
Identifier l'instance PostgreSQL
             |
             v
Comprendre les fichiers de configuration
             |
             v
Gérer les rôles et les privilèges
             |
             v
Sécuriser les connexions
             |
             v
Surveiller les sessions et les verrous
             |
             v
Maintenir les tables et les index
             |
             v
Mesurer la taille et les performances
             |
             v
Sauvegarder et tester la restauration
             |
             v
Préparer la reprise après incident
             |
             v
Automatiser et documenter l'exploitation
```

La compétence essentielle consiste à maintenir une base de données fiable et récupérable, tout en sachant expliquer les décisions prises et vérifier leurs effets. C'est cette démarche qui prépare au niveau expert, consacré notamment à l'optimisation avancée des requêtes, à la haute disponibilité, à la réplication opérationnelle et à la gestion des bases à grande échelle.