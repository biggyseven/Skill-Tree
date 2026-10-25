# Solutions de sauvegarde d'entreprise

## Niveau intermédiaire

## 1. Présentation générale du cours

Au niveau débutant, nous avons appris à créer des archives, copier des fichiers, utiliser Restic, vérifier l'intégrité des données et restaurer une sauvegarde dans un environnement de test.

Dans une entreprise, les besoins deviennent plus complexes.

Il faut sauvegarder plusieurs dizaines ou centaines de serveurs, des machines virtuelles, des bases de données, des partages de fichiers et parfois des charges hébergées dans le cloud. Les sauvegardes doivent être planifiées, suivies, protégées et vérifiées. Les équipes doivent aussi pouvoir restaurer les données rapidement, même lorsqu'une partie de l'infrastructure est indisponible.

Une solution de sauvegarde d'entreprise ne se limite donc pas à un logiciel qui copie des fichiers. Elle repose sur une architecture, des politiques, des espaces de stockage, une gestion des identités, des mécanismes de protection, un suivi des résultats et des procédures de reprise.

Ce cours présente les principaux concepts d'une plateforme de sauvegarde centralisée et les met en pratique à travers plusieurs technologies.

Nous étudierons notamment :

- Les architectures de sauvegarde centralisées.
- Les catalogues, serveurs de gestion, proxys et dépôts de sauvegarde.
- Les sauvegardes complètes, incrémentales, synthétiques et les chaînes de restauration.
- Les solutions Veeam Backup & Replication, Proxmox Backup Server, Bareos et les solutions Microsoft.
- Les sauvegardes des machines virtuelles, des serveurs physiques et des applications.
- Les dépôts immuables et la protection contre les rançongiciels.
- Les politiques de rétention, notamment GFS.
- Les sauvegardes hors site et les copies vers le cloud.
- Le dimensionnement du stockage et du réseau.
- La supervision des tâches de sauvegarde.
- Les tests de restauration et l'organisation d'un PRA.
- L'automatisation et la standardisation des opérations.

Les exemples sont pédagogiques. Avant une mise en production, il faut vérifier les versions des logiciels, les fonctionnalités disponibles dans l'édition retenue, les prérequis matériels et les contraintes contractuelles.

## 2. Objectifs pédagogiques

À la fin de ce cours, l'apprenant doit être capable de :

1. Concevoir une architecture de sauvegarde centralisée.
2. Identifier les composants d'une solution d'entreprise.
3. Choisir une solution adaptée au type de données et d'infrastructure.
4. Construire une politique de sauvegarde par niveau de criticité.
5. Comprendre les chaînes de sauvegarde incrémentale et les sauvegardes synthétiques.
6. Définir des fenêtres de sauvegarde et des politiques de rétention.
7. Sauvegarder des machines virtuelles avec une solution compatible.
8. Comprendre les particularités des sauvegardes applicatives et des bases de données.
9. Concevoir des dépôts de sauvegarde sécurisés.
10. Mettre en place une copie indépendante et immuable.
11. Calculer la capacité de stockage et le débit nécessaires.
12. Surveiller les tâches et diagnostiquer les échecs.
13. Définir des procédures de restauration par type de sinistre.
14. Organiser des tests de restauration mesurables.
15. Préparer un plan de reprise d'activité.
16. Documenter les responsabilités de l'équipe d'exploitation.
17. Construire un projet de sauvegarde d'entreprise reproductible.

## 3. Rappel : sauvegarde, réplication, snapshot et continuité

Avant de choisir un produit, il faut distinguer les mécanismes de protection.

| Mécanisme | Objectif principal | Limite |
|---|---|---|
| Sauvegarde | Conserver des versions récupérables de données | Nécessite une politique de rétention et des tests |
| Réplication | Maintenir des copies sur un autre système | Peut reproduire une suppression ou une corruption |
| Snapshot | Capturer un état à un instant donné | Peut dépendre du stockage ou du système source |
| Haute disponibilité | Continuer ou reprendre le service après certaines pannes | Ne remplace pas l'historique des données |
| Archivage | Conserver des données sur une durée prolongée | La récupération peut être plus lente |
| Réplication hors site | Maintenir une copie sur un autre emplacement | Ne garantit pas à elle seule l'isolation contre un compte compromis |

### 3.1 Pourquoi la haute disponibilité ne suffit-elle pas ?

Prenons une base de données répliquée sur deux serveurs.

```text
              APPLICATION
                   |
                   v
             BASE PRINCIPALE
                   |
                   | Réplication
                   v
             BASE SECONDAIRE
```

Une panne du serveur principal peut permettre de continuer le service à partir de la base secondaire, selon l'architecture.

Mais supposons qu'une application supprime accidentellement une table importante et que cette opération soit répliquée. La copie secondaire peut reproduire la suppression.

Une sauvegarde versionnée conserve des états antérieurs et permet de revenir à un point précédant l'incident.

```text
Production
   |
   +------> Réplication vers le secours
   |              |
   |              v
   |         Continuité du service
   |
   +------> Sauvegardes versionnées
                  |
                  v
            Récupération historique
```

Les deux approches sont complémentaires.

### 3.2 Le périmètre de sauvegarde

Une entreprise doit définir exactement ce qu'elle protège.

Cela peut comprendre :

- Les fichiers utilisateurs.
- Les répertoires partagés.
- Les systèmes d'exploitation.
- Les configurations des serveurs.
- Les machines virtuelles.
- Les bases de données.
- Les applications.
- Les services d'identité.
- Les configurations réseau.
- Les données de collaboration.
- Les secrets et certificats nécessaires à la reprise.
- Les configurations du logiciel de sauvegarde lui-même.

Il faut aussi identifier ce qui n'est volontairement pas sauvegardé, par exemple des caches reconstructibles ou des fichiers temporaires.

Une exclusion mal définie peut toutefois entraîner la perte de données importantes.

## 4. Architecture d'une solution de sauvegarde d'entreprise

### 4.1 Les principaux composants

Une solution centralisée peut comprendre les éléments suivants.

**Serveur de gestion :** centralise la configuration des tâches, les politiques et les opérations.

**Planificateur :** détermine quand les tâches doivent s'exécuter. Il est souvent intégré au serveur de gestion.

**Agents :** logiciels installés sur certains systèmes protégés pour lire les données et participer aux opérations.

**Proxys ou data movers :** composants qui déplacent les données entre les systèmes sources et les dépôts.

**Dépôts de sauvegarde :** stockent les points de restauration.

**Catalogue ou base de données de gestion :** conserve les informations nécessaires pour retrouver les sauvegardes et organiser la restauration.

**Système de notification et de supervision :** signale les échecs, les retards et les anomalies.

**Copie secondaire :** conserve des sauvegardes dans un autre domaine de panne ou un autre emplacement.

**Interface d'administration :** permet de surveiller les tâches, examiner les résultats et lancer des restaurations.

### 4.2 Schéma d'architecture

```text
                 ADMINISTRATEURS
                        |
                        v
              CONSOLE DE GESTION
                        |
                        v
              SERVEUR DE SAUVEGARDE
              Configuration / Catalogue
                        |
             +----------+-----------+
             |                      |
             v                      v
        PROXY DE DONNEES       PLANIFICATEUR
             |
       +-----+-------------------------------+
       |                 |                   |
       v                 v                   v
 Serveur physique    Cluster VM          Serveur fichiers
       |                 |                   |
       +-----------------+-------------------+
                         |
                         v
                   DEPOT PRINCIPAL
                         |
                         v
                  COPIE SECONDAIRE
                         |
             +-----------+-----------+
             |                       |
             v                       v
       Dépôt immuable         Site distant / cloud
             |
             v
        Tests de restauration
```

Cette représentation est générique. Toutes les solutions ne possèdent pas exactement ces composants sous forme de serveurs distincts.

Par exemple, une plateforme compacte peut intégrer la gestion et les transferts dans un même service. Une plateforme à grande échelle peut utiliser plusieurs proxys, plusieurs dépôts et des copies distribuées.

### 4.3 Le plan de contrôle et le plan de données

Il est utile de séparer deux notions.

Le **plan de contrôle** gère les politiques, les identités, les plannings, le catalogue et les opérations.

Le **plan de données** transporte les fichiers ou blocs et les enregistre dans les dépôts.

Cette séparation aide à comprendre certains incidents.

Un serveur de gestion indisponible peut empêcher de lancer de nouvelles tâches sans signifier que toutes les données de sauvegarde ont disparu.

À l'inverse, une interface de gestion accessible ne garantit pas que les dépôts possèdent les données nécessaires à une restauration.

Il faut protéger les deux plans.

### 4.4 Pourquoi centraliser ?

La centralisation offre notamment :

- Une gestion cohérente des politiques.
- Une vue globale des résultats.
- Une identification des systèmes non protégés.
- Une standardisation des horaires.
- Une gestion des accès.
- Une recherche plus rapide des sauvegardes.
- Une consolidation des rapports.
- Une meilleure visibilité sur la capacité.

Mais elle concentre aussi des responsabilités. Le serveur de gestion et les comptes privilégiés doivent être protégés, et la stratégie de reprise doit permettre de récupérer les informations nécessaires à l'administration du système de sauvegarde.

## 5. Comparer les principales solutions

Il n'existe pas un seul outil qui soit idéal dans tous les environnements.

Le choix dépend des systèmes à protéger, de la virtualisation, des compétences disponibles, des contraintes de récupération, des licences, du stockage et des exigences de sécurité.

### 5.1 Tableau comparatif

| Solution | Environnements courants | Points forts | Points d'attention |
|---|---|---|---|
| Veeam Backup & Replication | Environnements virtualisés, physiques et charges prises en charge | Gestion centralisée, sauvegardes d'images, restauration et copies | Licences, compatibilité, architecture et capacités selon version |
| Proxmox Backup Server | Proxmox VE et sauvegardes prises en charge par les clients PBS | Intégration Proxmox, déduplication, vérification et synchronisation | Périmètre de protection à vérifier selon les charges |
| Bareos | Serveurs physiques et fichiers, avec plugins et extensions selon besoins | Architecture ouverte avec Director, File Daemon, Storage Daemon et catalogue | Administration et intégration qui nécessitent des compétences |
| Windows Server Backup | Scénarios de sauvegarde Windows pris en charge | Outil Microsoft intégré aux environnements compatibles | Fonctionnalités et portée plus limitées qu'une suite d'entreprise complète |
| Azure Backup | Charges prises en charge dans un environnement Microsoft Azure et hybride | Intégration avec des services Azure et fonctions de sécurité | Coûts cloud, réseau, rétention et contraintes des charges |
| Restic | Fichiers et dépôts compatibles | Sauvegardes versionnées, chiffrement, dépôt local ou distant selon backend | Orchestration centralisée à construire ou intégrer selon l'échelle |

Les fonctions précises, les plateformes prises en charge et les conditions commerciales évoluent. Il faut consulter la documentation correspondant aux versions effectivement envisagées avant de prendre une décision.

### 5.2 Veeam Backup & Replication

Veeam est utilisé notamment pour la sauvegarde de machines virtuelles et de systèmes physiques pris en charge.

Sa plateforme repose sur des tâches configurées pour définir :

- Ce qui doit être protégé.
- Quand la sauvegarde doit être exécutée.
- Où elle doit être stockée.
- Quel historique doit être conservé.
- Quelles méthodes de traitement des données sont utilisées.
- Quelles options de restauration sont disponibles.

Les fonctionnalités dépendent de la version, de la plateforme source et de l'édition ou des droits de licence disponibles.

Documentation officielle :

https://helpcenter.veeam.com/docs/vbr/userguide/about_backup.html

### 5.3 Proxmox Backup Server

Proxmox Backup Server est une solution de sauvegarde intégrée aux environnements Proxmox et conçue pour gérer des sauvegardes versionnées.

Parmi les fonctionnalités décrites dans sa documentation figurent :

- Le stockage des sauvegardes.
- La déduplication.
- La vérification d'intégrité.
- Les politiques de rétention.
- La synchronisation entre dépôts.
- La restauration.
- Le chiffrement côté client lorsqu'il est configuré.

Sa méthode de stockage réduit les transferts et la duplication de données, mais il faut encore dimensionner les dépôts, surveiller leur santé et tester les restaurations.

Documentation officielle :

https://pbs.proxmox.com/docs/

### 5.4 Bareos

Bareos est une solution de sauvegarde reposant sur plusieurs composants.

```text
                 BAREOS DIRECTOR
        Jobs / Horaires / Politiques
                       |
             +---------+---------+
             |                   |
             v                   v
       File Daemon          Storage Daemon
       sur les clients      Stockage des données
             |                   |
             v                   v
       Fichiers sources    Disques / bandes / cibles
                       |
                       v
                    CATALOGUE
```

Le Director organise les opérations, le File Daemon intervient sur les systèmes protégés, le Storage Daemon lit et écrit les données dans les cibles de sauvegarde, et le catalogue facilite la gestion et la restauration.

Les plugins et intégrations disponibles doivent être vérifiés pour chaque charge.

Documentation officielle :

https://docs.bareos.org/

### 5.5 Solutions Microsoft et cloud

Windows Server Backup et `wbadmin` permettent des opérations de sauvegarde et de restauration pour des scénarios Windows pris en charge.

Azure Backup propose des mécanismes de protection pour des charges compatibles avec le service. Les options de sécurité, d'immuabilité, de suppression réversible et d'autorisation doivent être configurées en fonction du besoin.

Documentation officielle :

https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin

https://learn.microsoft.com/en-us/azure/backup/

### 5.6 Comment choisir ?

Avant de retenir une solution, établir une matrice de sélection :

| Critère | Question à résoudre |
|---|---|
| Compatibilité | La solution prend-elle en charge les systèmes réellement utilisés ? |
| RPO/RTO | Permet-elle les fréquences et délais de récupération attendus ? |
| Restauration applicative | Peut-elle récupérer les bases ou applications de manière cohérente ? |
| Stockage | Prend-elle en charge les dépôts disponibles et la stratégie hors site ? |
| Sécurité | Offre-t-elle les protections et contrôles nécessaires ? |
| Exploitation | L'équipe sait-elle gérer les incidents et restaurations ? |
| Coût | Quel est le coût logiciel, matériel, réseau et opérationnel ? |
| Capacité | Le débit de sauvegarde et de restauration est-il suffisant ? |
| Automatisation | Les tâches, API et rapports peuvent-ils être intégrés à l'exploitation ? |
| Réversibilité | Comment récupérer les données sans dépendre uniquement de l'outil ou du prestataire ? |

Le meilleur choix n'est pas nécessairement celui qui possède le plus de fonctionnalités. Il doit répondre aux besoins essentiels avec un niveau d'exploitation réaliste pour l'organisation.

## 6. Types de sauvegardes dans les solutions d'entreprise

### 6.1 Sauvegarde complète

Une sauvegarde complète capture l'ensemble du périmètre sélectionné.

Elle facilite la compréhension et la récupération, mais peut demander plus de temps, de bande passante et d'espace.

### 6.2 Sauvegarde incrémentale

Une sauvegarde incrémentale conserve les changements selon le mécanisme de référence de l'outil.

Dans une chaîne incrémentale classique :

```text
DIMANCHE : FULL
  |
  v
LUNDI : INC-1
  |
  v
MARDI : INC-2
  |
  v
MERCREDI : INC-3
```

Pour récupérer l'état de mercredi dans ce modèle, la restauration utilise la sauvegarde complète et les incréments nécessaires.

Les systèmes modernes peuvent fonctionner différemment, notamment grâce à la déduplication, aux métadonnées et aux mécanismes de blocs.

### 6.3 Sauvegarde différentielle

Dans le modèle différentiel classique, chaque sauvegarde conserve les changements depuis la dernière complète.

```text
DIMANCHE : FULL
  |
  +------> LUNDI : DIFF-1
  |
  +------> MARDI : DIFF-2
  |
  +------> MERCREDI : DIFF-3
```

La restauration d'une date nécessite normalement la complète de référence et la différentielle correspondant à l'état recherché.

La différentielle tend à devenir plus volumineuse à mesure que le temps s'écoule depuis la dernière complète.

### 6.4 Sauvegarde synthétique complète

Une sauvegarde synthétique complète est construite à partir de données déjà présentes dans le dépôt, avec les mécanismes du logiciel de sauvegarde.

L'objectif est de créer un point de restauration complet logique sans nécessairement relire toutes les données depuis la source.

Les performances dépendent de l'organisation du dépôt, de la déduplication, des opérations de lecture et écriture et des capacités de stockage.

Il ne faut pas supposer que toute sauvegarde appelée « full » implique un transfert complet des données sources.

### 6.5 Chaînes de sauvegarde

Une chaîne représente les éléments nécessaires pour retrouver un point de restauration.

Exemple conceptuel :

```text
FULL-001
   |
   +---- INC-001
   |
   +---- INC-002
   |
   +---- INC-003
```

Si un point de restauration dépend de plusieurs éléments, il faut préserver ces dépendances selon les règles de l'outil.

Il faut donc savoir :

- Quel fichier ou bloc dépend de quelle chaîne.
- Comment l'outil gère les sauvegardes complètes et incrémentales.
- Quand une chaîne devient supprimable.
- Quelles vérifications sont prévues.
- Comment déplacer ou copier les points de restauration.

Une suppression manuelle des fichiers du dépôt peut rendre une chaîne inutilisable. Utiliser les mécanismes de rétention de la solution plutôt que supprimer arbitrairement des fichiers internes.

## 7. Comprendre les proxys, agents et transferts de données

### 7.1 Le rôle d'un proxy de sauvegarde

Dans certaines architectures, un proxy réalise le transfert de données entre l'hyperviseur ou les systèmes sources et le dépôt.

Il peut notamment contribuer à :

- Lire les données sources.
- Traiter les blocs.
- Effectuer certaines opérations de compression ou de transfert.
- Répartir la charge de sauvegarde.
- Accéder à des environnements isolés.
- Limiter la charge sur le serveur de gestion.

Le rôle exact dépend du produit et de l'architecture.

### 7.2 Exemple d'architecture virtualisée

```text
          HYPERVISEUR / CLUSTER VM
                    |
                    v
             Lecture des blocs
                    |
                    v
             PROXY DE SAUVEGARDE
                    |
             +------+------+
             |             |
             v             v
        Traitement      Transfert
             |             |
             +------+------+
                    |
                    v
             DEPOT BACKUP
```

Un proxy trop peu dimensionné peut devenir un goulot d'étranglement.

Mais ajouter des proxys ne résout pas automatiquement tous les problèmes. Le stockage, les réseaux et les limitations de la plateforme source peuvent aussi restreindre le débit.

### 7.3 Agent ou sauvegarde sans agent ?

Une sauvegarde basée sur la virtualisation peut lire les données au niveau de la plateforme de virtualisation, selon les capacités de la solution.

Un agent installé dans le système invité permet un traitement plus proche de l'OS, notamment pour certains scénarios physiques et applicatifs.

Les deux approches ont des avantages.

| Approche | Atout | Limite |
|---|---|---|
| Au niveau hyperviseur | Gestion centralisée des VM et des disques virtuels pris en charge | Les besoins de cohérence applicative doivent être traités |
| Agent dans le système | Contrôle proche de l'OS et possibilités spécifiques | Déploiement, mises à jour et gestion d'agents |
| Sauvegarde applicative | Cohérence des données métier | Dépend de l'application, du moteur et des plugins |
| Export logique | Format souvent indépendant de la disposition physique des fichiers | Peut être long pour les grands volumes et demander des ressources |

Une plateforme peut combiner ces méthodes selon les charges.

## 8. Sauvegarder des machines virtuelles

### 8.1 Pourquoi la sauvegarde d'une VM est particulière

Une machine virtuelle comprend généralement :

- Un ou plusieurs disques virtuels.
- Une configuration virtuelle.
- Des informations sur les interfaces et périphériques.
- Un système d'exploitation invité.
- Des applications et leurs données.
- Des dépendances réseau et stockage.

Sauvegarder une VM en fonctionnement nécessite de comprendre le niveau de cohérence obtenu.

Une copie de disque peut être exploitable pour démarrer un système tout en laissant certaines données applicatives incohérentes, notamment si une base de données écrit simultanément plusieurs fichiers liés.

### 8.2 Cohérence de panne et cohérence applicative

Une sauvegarde cohérente après panne, ou *crash-consistent*, représente un état similaire à celui obtenu après une interruption brutale.

Le système et ses applications peuvent avoir besoin de mécanismes de récupération à la suite de cette interruption.

Une sauvegarde cohérente au niveau applicatif cherche à coordonner les données avec le système ou l'application pour obtenir un état récupérable selon les mécanismes pris en charge.

Cela peut nécessiter des outils d'intégration applicative, des VSS writers sous Windows ou des méthodes propres au moteur.

### 8.3 Schéma de traitement d'une VM

```text
            MACHINE VIRTUELLE
                    |
                    v
        Préparation / cohérence éventuelle
                    |
                    v
         Création du point de lecture
                    |
                    v
           Lecture des données
                    |
                    v
          Compression / déduplication
                    |
                    v
            Dépôt de sauvegarde
                    |
                    v
            Vérification et suivi
```

Le mécanisme exact varie avec l'hyperviseur et le produit. Certaines solutions utilisent des snapshots temporaires ou d'autres mécanismes de suivi des changements.

Les snapshots temporaires de sauvegarde doivent être gérés par la solution prévue et ne doivent pas être confondus avec des points de restauration conservés indéfiniment sur le stockage de production.

### 8.4 Ce qu'il faut tester

Pour une VM protégée, une recette de sauvegarde peut vérifier :

1. La VM est incluse dans le job.
2. La tâche termine selon le résultat attendu.
3. Le point de restauration apparaît dans le catalogue.
4. La sauvegarde se trouve dans le dépôt prévu.
5. La configuration de la VM est récupérable.
6. Les disques nécessaires sont présents.
7. La VM peut être restaurée dans un environnement de test.
8. Le système démarre.
9. Les services applicatifs fonctionnent.
10. Les données sont cohérentes.
11. Les dépendances réseau sont documentées.

Un job vert ne prouve pas à lui seul que le service métier sera récupéré correctement.

## 9. Sauvegardes applicatives et bases de données

### 9.1 Pourquoi les applications nécessitent-elles une attention particulière ?

Les applications peuvent conserver des données dans plusieurs emplacements :

- Fichiers.
- Bases de données.
- Files de messages.
- Stockage objet.
- Journaux transactionnels.
- Configurations.
- Secrets et certificats.

Une sauvegarde de la VM ne garantit pas automatiquement que tous ces composants pourront être remis en cohérence.

### 9.2 SQL Server, PostgreSQL et autres moteurs

Chaque moteur possède ses propres mécanismes de sauvegarde.

Exemples :

- Sauvegardes intégrées de SQL Server.
- `pg_dump` et outils de sauvegarde physique PostgreSQL.
- Journaux transactionnels ou mécanismes d'archivage.
- Sauvegardes spécifiques Oracle ou autres moteurs.
- Intégration applicative fournie par la solution de sauvegarde.

Le choix doit tenir compte du RPO, du volume, de la durée de restauration et de la cohérence.

### 9.3 Exemple PostgreSQL

Une sauvegarde logique peut être créée avec `pg_dump` :

```bash
pg_dump -Fc -d NOM_DE_BASE -f sauvegarde.dump
```

Les identifiants de connexion doivent être gérés de manière sécurisée.

La restauration d'un export compatible peut être réalisée avec `pg_restore` :

```bash
pg_restore -d BASE_DE_TEST sauvegarde.dump
```

La base cible doit être préparée et les dépendances nécessaires doivent être disponibles.

Ces commandes sont des exemples d'administration PostgreSQL. Une stratégie de production peut nécessiter une sauvegarde physique, des journaux transactionnels ou une autre méthode selon le RPO et le RTO.

### 9.4 Applications transactionnelles

Pour une application critique, documenter :

- Le mécanisme de cohérence.
- La fréquence des sauvegardes.
- Le traitement des journaux transactionnels.
- Les dépendances.
- Les identifiants nécessaires.
- Les étapes de démarrage après restauration.
- La validation fonctionnelle.
- La stratégie de retour à un état antérieur.

Il faut également définir comment restaurer les différents composants dans un ordre cohérent.

## 10. Concevoir une politique de sauvegarde d'entreprise

### 10.1 Pourquoi classer les données ?

Toutes les données n'ont pas la même importance.

Un environnement de développement peut être reconstructible. Une base transactionnelle critique peut exiger une récupération beaucoup plus rapide et un point de restauration plus récent.

La politique doit être construite à partir des objectifs métier.

### 10.2 Exemple de classification

| Classe | Exemple | Fréquence indicative | Contrôle |
|---|---|---|---|
| Critique | Base transactionnelle principale | Selon RPO, avec mécanismes complémentaires si nécessaire | Vérifications régulières et restauration prioritaire |
| Haute | Application métier | Quotidienne ou adaptée au besoin | Contrôle des jobs et tests périodiques |
| Standard | Serveur de fichiers courant | Quotidienne | Vérification périodique |
| Faible | Laboratoire reconstructible | Selon la valeur des données | Contrôle simplifié |
| Archive | Données anciennes à conserver | Selon les exigences de conservation | Vérification d'intégrité et test de récupération |

Ces valeurs sont indicatives. La fréquence réelle doit être décidée selon le rythme des modifications et le coût d'une perte de données.

### 10.3 Matrice de politique

Pour chaque charge, définir :

```text
Nom du service :
Propriétaire métier :
Responsable technique :
Criticité :
Périmètre :
Méthode de sauvegarde :
Fréquence :
RPO cible :
RTO cible :
Dépôt principal :
Copie secondaire :
Rétention :
Protection immuable :
Chiffrement :
Vérification :
Test de restauration :
Procédure de reprise :
```

La matrice doit indiquer les responsabilités : équipe de sauvegarde, équipe système, propriétaire applicatif et responsable métier.

### 10.4 Éviter les politiques uniquement fondées sur le type de serveur

Deux serveurs de fichiers peuvent avoir des exigences très différentes.

L'un peut héberger des documents facilement reconstruits ; l'autre peut conserver des données juridiques ou financières critiques.

La fréquence de sauvegarde doit tenir compte de la criticité des informations, de leur rythme de modification et du coût d'une perte.

## 11. Rétention et stratégie GFS

### 11.1 Qu'est-ce que GFS ?

GFS désigne généralement une politique de conservation de type :

- Grandfather : points de restauration conservés sur une durée longue.
- Father : points de restauration intermédiaires, souvent hebdomadaires.
- Son : points de restauration fréquents, souvent quotidiens.

La nomenclature exacte dépend des pratiques de l'organisation et des possibilités de la solution.

### 11.2 Exemple de rétention GFS

```text
QUOTIDIEN
  Conserver les 14 derniers points journaliers

HEBDOMADAIRE
  Conserver 8 points hebdomadaires

MENSUEL
  Conserver 12 points mensuels

ANNUEL
  Conserver les points requis pour l'archivage
```

Ces valeurs sont illustratives. Elles ne constituent pas une obligation réglementaire ou une recommandation universelle.

### 11.3 Pourquoi conserver plusieurs horizons ?

Les incidents ne sont pas toujours détectés immédiatement.

Un fichier peut être corrompu aujourd'hui, alors que la corruption a commencé plusieurs semaines auparavant.

Une rétention uniquement quotidienne et très courte peut ne conserver aucune version antérieure à la corruption.

La politique de rétention doit donc prendre en compte le délai possible de détection et la durée pendant laquelle une donnée peut rester apparemment incorrecte.

### 11.4 Réduire la rétention avec précaution

Une politique de suppression mal conçue peut retirer un point de restauration qui semble ancien mais reste nécessaire.

Avant une modification de rétention, examiner :

- Les objectifs de récupération.
- Les chaînes dépendantes.
- Les obligations de conservation.
- Les points de restauration réellement disponibles.
- La capacité.
- Les effets sur les copies secondaires.
- Les conséquences sur le coût.

Pour les solutions qui gèrent leurs propres chaînes et métadonnées, laisser le logiciel gérer les suppressions.

## 12. Concevoir un dépôt de sauvegarde

### 12.1 Les principaux types de dépôts

Un dépôt peut être :

- Un disque local.
- Un stockage partagé.
- Un serveur de fichiers dédié.
- Un serveur Linux de sauvegarde.
- Un stockage objet compatible avec la solution.
- Une bibliothèque de bandes.
- Un dépôt cloud.
- Un dépôt spécialisé fourni par un constructeur.

Le choix dépend du débit, du volume, de la conservation, du coût et des fonctions de protection.

### 12.2 Stockage en disque

Avantages courants :

- Accès direct.
- Restauration généralement rapide.
- Administration connue des équipes.
- Capacité pouvant être étendue selon la plateforme.

Points d'attention :

- Panne de disque ou de contrôleur.
- Saturation de capacité.
- Compromission des comptes d'accès.
- Propagation de suppressions.
- Protection physique du serveur.
- Dépendance au système de fichiers.

### 12.3 Stockage objet

Le stockage objet peut être utilisé pour des copies à grande échelle ou des rétentions spécifiques.

Les caractéristiques importantes comprennent :

- Capacité.
- Coût des opérations et du stockage.
- Réplication selon le service.
- Chiffrement.
- Versionnement éventuel.
- Immutabilité lorsque disponible.
- Délais et coûts de récupération.
- Limites API.
- Dépendances réseau.

Les classes d'archivage peuvent coûter moins cher pour la conservation mais entraîner des délais ou coûts supplémentaires à la restauration.

### 12.4 Stockage sur bande

La bande peut offrir un stockage hors ligne et une conservation prolongée, selon l'architecture.

Il faut prévoir :

- Le catalogue des médias.
- Les lecteurs et bibliothèques.
- La rotation des supports.
- La gestion des erreurs.
- Le stockage physique.
- Les vérifications périodiques.
- Les procédures de restauration.
- La conservation hors site éventuelle.

La bande n'est pas automatiquement invulnérable : les procédures de transport, de stockage et de gestion des accès doivent également être maîtrisées.

### 12.5 Choisir le dépôt selon la restauration

La performance de la sauvegarde n'est qu'une partie du problème.

Il faut mesurer la capacité de restaurer lorsque plusieurs systèmes demandent simultanément de récupérer des données.

Un dépôt capable d'absorber les sauvegardes nocturnes peut ne pas fournir le débit requis lors d'un incident majeur impliquant plusieurs centaines de VM.

## 13. Protection contre les rançongiciels

### 13.1 Pourquoi les dépôts doivent-ils être protégés séparément ?

Une attaque peut chercher à supprimer ou chiffrer non seulement les données de production, mais aussi les sauvegardes.

Si les mêmes privilèges permettent de supprimer les données sources et les copies, l'attaquant peut neutraliser une grande partie du dispositif de récupération.

### 13.2 Le principe de l'immuabilité

L'immuabilité vise à empêcher la modification ou la suppression d'un point de sauvegarde pendant une période donnée, selon le mécanisme utilisé.

Exemples de mécanismes possibles :

- Dépôt Linux durci.
- Stockage objet avec verrouillage de rétention.
- Dépôt spécialisé prenant en charge l'immuabilité.
- Copies hors ligne.
- Contrôles d'accès empêchant les opérations de destruction.

L'immuabilité doit être configurée et vérifiée. Le seul fait d'utiliser un serveur Linux ou un stockage objet ne rend pas automatiquement les sauvegardes immuables.

### 13.3 Architecture de protection

```text
             ENVIRONNEMENT DE PRODUCTION
                         |
                         v
                 DEPOT PRINCIPAL
                         |
              +----------+----------+
              |                     |
              v                     v
        COPIE IMMUTABLE        COPIE HORS SITE
              |                     |
              v                     v
         Accès limité           Identités distinctes
              |                     |
              +----------+----------+
                         |
                         v
                  TESTS DE RESTAURATION
```

Il faut vérifier que les identités utilisées pour administrer la production n'ont pas, à elles seules, le pouvoir de supprimer toutes les copies protégées.

### 13.4 La règle 3-2-1-1-0

Cette règle est un aide-mémoire de bonnes pratiques :

- 3 copies des données, en comptant la production.
- 2 types de supports ou environnements différents.
- 1 copie hors site.
- 1 copie isolée ou immuable.
- 0 erreur de sauvegarde non détectée, objectif poursuivi grâce aux vérifications et aux tests.

Le dernier point n'est pas une garantie absolue. Il faut mettre en place des contrôles réguliers et corriger les anomalies identifiées.

### 13.5 Exemples de contrôles de sécurité

Une politique de sécurité devrait définir :

- Qui peut créer les sauvegardes.
- Qui peut modifier les politiques.
- Qui peut supprimer les dépôts.
- Qui peut modifier la rétention.
- Qui peut désactiver les mécanismes de protection.
- Qui peut restaurer les données.
- Comment les opérations sensibles sont journalisées.
- Comment les comptes d'urgence sont contrôlés.

Les fonctions d'immuabilité, la durée maximale de protection et les règles de suppression varient selon les solutions. Il faut consulter les caractéristiques du produit retenu avant de définir la politique.

## 14. Veeam Backup & Replication : principes d'exploitation

### 14.1 Comprendre un job

Dans Veeam Backup & Replication, un job de sauvegarde définit généralement :

- Les objets à protéger.
- Les options de traitement.
- Le calendrier.
- Le dépôt cible.
- La rétention.
- Les mécanismes de traitement et de suivi.
- Les paramètres nécessaires à la restauration.

Un job peut couvrir un ou plusieurs objets selon le type de charge et les paramètres de la solution.

Documentation officielle :

https://helpcenter.veeam.com/docs/vbr/userguide/about_backup.html

### 14.2 Chaîne de sauvegarde

Pour une machine virtuelle, une stratégie peut employer une sauvegarde complète initiale puis des incréments.

```text
POINT DE RESTAURATION INITIAL
            FULL
             |
             v
      INCREMENTAL 01
             |
             v
      INCREMENTAL 02
             |
             v
      INCREMENTAL 03
```

La manière de suivre les modifications dépend de la plateforme source et du produit. La méthode de sauvegarde, le type de disque et les options configurées peuvent influer sur les transferts.

Il faut comprendre les dépendances de la chaîne avant de déplacer ou supprimer les fichiers.

### 14.3 Backup Copy

Une tâche de copie de sauvegarde permet de conserver une copie supplémentaire des données déjà sauvegardées dans un autre emplacement.

Exemple :

```text
VM de production
      |
      v
Job de sauvegarde
      |
      v
Dépôt principal
      |
      v
Backup Copy
      |
      v
Dépôt secondaire
```

La copie secondaire doit disposer de sa propre politique de rétention et de protection.

La présence d'une copie ne signifie pas automatiquement qu'elle est indépendante : les permissions, les réseaux, le contrôle des identités et les dépendances partagés doivent être examinés.

Documentation officielle :

https://helpcenter.veeam.com/docs/vbr/userguide/backup_copy_managing_jobs.html

### 14.4 Dépôt Linux durci

Veeam documente un dépôt Linux durci destiné notamment à empêcher la modification ou la suppression des fichiers de sauvegarde pendant la période d'immuabilité configurée.

La conception repose sur des contrôles d'accès et des mécanismes spécifiques. Elle ne doit pas être réduite à la simple installation d'un partage réseau.

Documentation officielle :

https://helpcenter.veeam.com/docs/vbr/userguide/hardened_repository.html

Avant de mettre en œuvre cette architecture, vérifier les prérequis, les versions, les droits, les ports et les limitations décrits par le fournisseur.

### 14.5 Tâches de validation

Une mise en service Veeam devrait notamment confirmer :

- Les jobs configurés.
- Les machines incluses.
- Les résultats récents.
- Le dépôt utilisé.
- Les points de restauration disponibles.
- Les copies secondaires.
- Les règles de rétention.
- Les notifications.
- Les tests de restauration.

Il faut également vérifier la protection des configurations et des données nécessaires à l'administration de la solution.

## 15. Proxmox Backup Server : architecture et cycle de vie

### 15.1 Rôle de Proxmox Backup Server

Proxmox Backup Server est une solution de sauvegarde qui s'intègre notamment aux environnements Proxmox VE et propose un stockage optimisé pour des points de restauration.

Elle dispose notamment de fonctions de :

- Gestion des datastores.
- Déduplication.
- Vérification d'intégrité.
- Prune.
- Garbage collection.
- Synchronisation entre dépôts.
- Gestion de la rétention.
- Chiffrement côté client lorsque celui-ci est configuré.

La documentation officielle décrit ces mécanismes :

https://pbs.proxmox.com/docs/

### 15.2 Datastore

Un datastore désigne un espace de stockage géré par Proxmox Backup Server pour les sauvegardes.

Il doit être dimensionné en fonction :

- Du volume des données.
- Du taux de modification.
- De la rétention.
- Des opérations de maintenance.
- Des besoins de synchronisation.
- De la politique de vérification.
- Des capacités matérielles.

Un datastore proche de la saturation peut compromettre les tâches de sauvegarde ou les opérations de maintenance.

### 15.3 Déduplication

La déduplication vise à éviter de conserver inutilement plusieurs copies identiques de données, selon les mécanismes de l'outil.

Cela peut réduire la capacité et les transferts requis.

Mais le taux de déduplication dépend du contenu, du taux de modification et du format des données. Il ne faut pas dimensionner un système en supposant un taux de réduction garanti sans mesurer la charge réelle.

### 15.4 Prune et garbage collection

Dans Proxmox Backup Server, il faut distinguer les opérations de gestion de l'historique et la récupération de l'espace non référencé.

**Prune** applique une politique de rétention aux snapshots selon les règles configurées.

**Garbage collection** récupère l'espace occupé par les données qui ne sont plus référencées après la suppression ou le retrait de points de restauration.

Une suppression logique ne signifie donc pas toujours que l'espace physique est immédiatement récupéré.

### 15.5 Vérification des sauvegardes

Proxmox Backup Server prend en charge des mécanismes de vérification d'intégrité.

La planification doit permettre de contrôler régulièrement les sauvegardes, pas seulement de vérifier les nouvelles données.

Il est recommandé de combiner des vérifications régulières des nouvelles sauvegardes avec des revérifications périodiques selon les besoins, la capacité et les recommandations de la version employée.

Documentation officielle :

https://pbs.proxmox.com/docs/maintenance.html

### 15.6 Synchronisation entre serveurs

Proxmox Backup Server prend en charge la synchronisation de datastores entre serveurs, avec des tâches de synchronisation adaptées à l'architecture.

Cette possibilité permet de disposer d'une copie supplémentaire dans un autre emplacement.

Il faut cependant définir :

- La direction de synchronisation.
- L'authentification.
- Les autorisations.
- La fréquence.
- Les limites de bande passante.
- Le chiffrement.
- La rétention du datastore cible.
- La procédure de récupération après la perte du serveur principal.

Documentation officielle :

https://pbs.proxmox.com/docs/managing-remotes.html

### 15.7 Exemple de stratégie Proxmox

```text
Cluster Proxmox VE
         |
         v
Proxmox Backup Server principal
         |
         v
Snapshots / Déduplication
         |
         v
Vérifications planifiées
         |
         v
Synchronisation vers un second PBS
         |
         v
Datastore distant
         |
         v
Test de restauration de VM
```

Cette architecture est indicative. La réplication du datastore ne dispense pas de protéger les identités, les données de configuration, le matériel et les accès du serveur secondaire.

## 16. Bareos : sauvegarde centralisée de serveurs et fichiers

### 16.1 Architecture

Bareos utilise une architecture composée de plusieurs services.

```text
               BAREOS DIRECTOR
         Configuration / Planification
                       |
           +-----------+-----------+
           |                       |
           v                       v
      FILE DAEMON            STORAGE DAEMON
    Sur les systèmes        Lit et écrit les données
           |                       |
           v                       v
     Données sources       Dépôts et médias
                       |
                       v
                    CATALOGUE
```

Le catalogue facilite la recherche des données sauvegardées et la sélection des éléments à restaurer.

### 16.2 Notions de base

Un job définit une opération de sauvegarde ou de restauration.

Un schedule détermine les horaires.

Un FileSet représente le périmètre de fichiers à sauvegarder selon la configuration.

Un pool organise les volumes de sauvegarde selon les règles de gestion choisies.

Un client représente un système protégé.

Le stockage est géré par les composants et ressources configurés.

La syntaxe exacte dépend de la version Bareos et des éléments définis dans la configuration.

### 16.3 Pourquoi le catalogue est-il important ?

Le catalogue ne contient pas nécessairement l'ensemble des données sauvegardées elles-mêmes. Il permet surtout de conserver les métadonnées nécessaires à l'administration et à la recherche.

Si le catalogue est perdu, les données physiques de sauvegarde peuvent encore exister, mais il peut devenir plus difficile de retrouver et de restaurer les éléments concernés.

Il faut donc prévoir une sauvegarde du catalogue et de la configuration selon les recommandations du produit.

### 16.4 Gestion opérationnelle

Pour une plateforme Bareos, vérifier :

- L'état des jobs.
- Les erreurs des clients.
- La disponibilité du Storage Daemon.
- Les volumes de stockage.
- La sauvegarde du catalogue.
- La cohérence des politiques de rétention.
- Les droits de restauration.
- La capacité du stockage.
- Les tests de récupération.

Documentation officielle :

https://docs.bareos.org/

## 17. Sauvegardes Windows Server

### 17.1 Les options Windows

Selon le système et l'architecture, les opérations peuvent utiliser :

- Windows Server Backup.
- `wbadmin`.
- Des solutions d'entreprise compatibles.
- Des méthodes spécifiques aux applications.
- Des services de sauvegarde cloud pris en charge.

L'outil approprié dépend du type de récupération attendu : fichiers, volumes, état système, applications ou système complet.

### 17.2 Consulter les sauvegardes disponibles

Dans une console élevée, selon les droits disponibles :

```powershell
wbadmin get versions
```

La commande permet de répertorier les versions de sauvegarde récupérables à partir des emplacements appropriés.

Pour consulter les éléments d'une sauvegarde :

```powershell
wbadmin get items
```

Selon le scénario, il peut être nécessaire d'indiquer des paramètres de sélection supplémentaires.

### 17.3 État du système

Pour certaines charges Windows, la sauvegarde de l'état système est importante.

Exemple de commande :

```powershell
wbadmin start systemstatebackup -backupTarget:F:
```

Cette commande nécessite une exécution élevée et un support cible approprié. Vérifier que `F:` correspond bien à la destination attendue avant de l'exécuter.

L'état système ne remplace pas nécessairement la sauvegarde de tous les fichiers et volumes métier. Il faut examiner le périmètre protégé et les exigences de récupération.

Documentation officielle :

https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-systemstatebackup

### 17.4 Restauration

Avant toute restauration Windows, vérifier :

- La version à récupérer.
- Les données incluses.
- La destination.
- Les éventuels conflits avec les données actuelles.
- Les permissions requises.
- Les dépendances applicatives.
- Le besoin d'un environnement de récupération.
- La procédure de retour arrière.

Les commandes de récupération peuvent modifier ou remplacer les données existantes. Elles ne doivent pas être lancées en production sans vérifier précisément le périmètre et les conséquences.

Documentation officielle :

https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-recovery

## 18. Sauvegardes cloud et dépôts distants

### 18.1 Pourquoi utiliser le cloud ?

Le stockage distant permet de conserver une copie dans un autre domaine de panne.

Il peut compléter un dépôt local lorsque celui-ci n'est pas suffisant pour couvrir une perte de site, un vol ou un incident majeur.

Le cloud n'est pas automatiquement sécurisé ou immuable par nature. Il faut activer et vérifier les protections appropriées.

### 18.2 Points à examiner

Avant de choisir un service de stockage ou de sauvegarde cloud :

- Type de service pris en charge.
- Région de stockage.
- Contraintes de résidence et de confidentialité.
- Chiffrement.
- Gestion des clés.
- Versionnement.
- Immutabilité ou verrouillage.
- Suppression réversible.
- Coût du stockage.
- Coût des opérations.
- Coût de sortie des données.
- Délais de récupération.
- Débit de téléchargement.
- Limites des API.
- Droits des comptes d'administration.

### 18.3 Exemple de stratégie hybride

```text
                         PRODUCTION
                              |
                              v
                    DEPOT LOCAL RAPIDE
                              |
                              v
                      COPIE DISTANTE
                              |
                 +------------+------------+
                 |                         |
                 v                         v
            Stockage cloud           Dépôt secondaire
                 |                         |
                 +------------+------------+
                              |
                              v
                      Test de récupération
```

Le dépôt local permet de récupérer rapidement les données courantes.

La copie distante protège contre la perte du site principal, selon les caractéristiques et les dépendances du service.

Une copie cloud doit être testée en récupération, notamment si les données doivent être téléchargées au travers d'une connexion limitée.

### 18.4 Sécurité des dépôts cloud

Le modèle de protection doit vérifier :

- Les rôles d'accès.
- Les autorisations de suppression.
- La protection des clés.
- Les possibilités de verrouillage.
- Le contrôle des changements de politique.
- La journalisation des opérations d'administration.
- Les mécanismes de récupération d'un compte compromis.

Microsoft documente notamment des fonctions de sécurité pour Azure Backup.

Documentation officielle :

https://learn.microsoft.com/en-us/azure/backup/security-overview

## 19. Dimensionner le stockage de sauvegarde

Le dimensionnement doit être réalisé avant le déploiement, puis ajusté à partir des mesures réelles.

### 19.1 Données à collecter

Pour chaque charge :

- Volume initial.
- Taux de changement.
- Fréquence des sauvegardes.
- Méthode de protection.
- Taux de compression mesuré.
- Taux de déduplication mesuré.
- Rétention.
- Copies supplémentaires.
- Croissance prévue.
- Capacité de réserve.
- Besoins de restauration simultanée.

### 19.2 Exemple de calcul simplifié

Supposons :

```text
Données protégées :
2 To

Changements quotidiens :
5 % du volume initial

Rétention :
14 jours
```

Le volume quotidien modifié peut être estimé ainsi :

```text
2 To x 5 % = 0,1 To
```

Soit environ 100 Go par jour dans cette hypothèse simplifiée.

Sur quatorze jours :

```text
100 Go x 14 = 1 400 Go
```

Cette estimation représente les changements quotidiens dans un modèle simple. Elle ne constitue pas un calcul exact du stockage d'un produit de sauvegarde.

Les mécanismes de déduplication, la méthode de sauvegarde, les données supprimées, les sauvegardes complètes, la compression et les copies secondaires modifient le résultat réel.

### 19.3 Capacité brute, capacité utile et réserve

Il faut distinguer :

- La capacité brute des disques.
- La capacité utile après redondance et formatage.
- La capacité utilisée par les sauvegardes.
- La capacité qui reste libre.
- La capacité réservée à la reconstruction.
- La capacité consommée par les métadonnées et les opérations.

Ne pas dimensionner un dépôt pour qu'il atteigne 100 % d'occupation.

Le système de sauvegarde doit conserver assez de marge pour les nouvelles tâches, les opérations de maintenance et la croissance.

### 19.4 Prévoir la perte d'un composant

Un dépôt constitué de plusieurs disques doit être évalué dans le scénario de panne prévu par son architecture.

Si un disque ou un nœud tombe en panne, la capacité utile restante doit permettre de continuer à fonctionner selon les objectifs définis.

La tolérance à la panne dépend du type de RAID, du stockage distribué, de la réplication ou du mécanisme de protection choisi.

## 20. Dimensionner les fenêtres de sauvegarde

### 20.1 Estimation du temps de transfert

Supposons qu'une sauvegarde doive transférer 600 Go sur un réseau dont le débit effectif mesuré est de 100 Mo/s.

Avec une convention décimale :

```text
Volume :
600 Go = 600 000 Mo

Débit :
100 Mo/s

Temps :
600 000 / 100 = 6 000 secondes
```

Soit environ 1 heure et 40 minutes, sans compter les autres traitements.

La durée réelle dépend du nombre de fichiers, du protocole, de la compression, du chiffrement, du stockage et des traitements de vérification.

### 20.2 Temps de restauration

La restauration peut solliciter d'autres ressources que la sauvegarde.

Une récupération doit parfois relire des volumes volumineux, créer de nouveaux disques, transférer des données sur le réseau, démarrer des VM et vérifier les applications.

Il faut mesurer le temps total de reprise plutôt que le seul temps de transfert.

### 20.3 Ordonnancement

Exemple de planification :

```text
20 h 00 : fichiers partagés
21 h 00 : serveurs applicatifs
22 h 00 : bases de données
23 h 00 : machines virtuelles standard
00 h 00 : copie distante
03 h 00 : vérifications planifiées
```

Cet exemple ne doit pas être repris sans mesure.

Il faut vérifier les dépendances, les pics de charge, les fenêtres métier et les ressources partagées.

## 21. Gestion des identités et contrôle des accès

### 21.1 Pourquoi séparer les comptes ?

Une plateforme de sauvegarde peut détenir un accès très large à l'ensemble de l'infrastructure.

Si un compte compromis permet de modifier les jobs, désactiver la rétention et supprimer les dépôts, l'attaquant peut compromettre une partie importante de la capacité de reprise.

### 21.2 Modèle d'accès recommandé

Prévoir des rôles distincts selon les tâches :

- Administration de la plateforme de sauvegarde.
- Gestion des politiques.
- Opérations courantes.
- Consultation des rapports.
- Restauration de données.
- Gestion des dépôts.
- Administration du stockage immuable.
- Gestion des comptes et des secrets.

Les rôles doivent être attribués selon les responsabilités réelles.

### 21.3 Contrôles essentiels

- Comptes nominatifs pour les administrateurs.
- MFA pour les accès sensibles lorsque disponible.
- Comptes de service distincts.
- Moindre privilège.
- Journalisation des opérations critiques.
- Séparation des identités de production et de sauvegarde.
- Revue des autorisations.
- Rotation des secrets.
- Procédures d'urgence contrôlées.
- Révocation des accès inutiles.

Une architecture de sauvegarde ne doit pas être considérée comme isolée si elle dépend d'un compte administrateur de production ayant la capacité de la détruire.

## 22. Supervision des sauvegardes

Une plateforme de sauvegarde doit être supervisée comme n'importe quel service critique.

### 22.1 Indicateurs principaux

| Indicateur | Objectif |
|---|---|
| Tâches réussies | Confirmer que les sauvegardes attendues ont été réalisées |
| Tâches échouées | Détecter les erreurs |
| Âge de la dernière sauvegarde valide | Repérer les données insuffisamment récentes |
| Durée du job | Détecter les dérives de durée |
| Capacité disponible | Prévenir la saturation |
| Erreurs de vérification | Détecter les problèmes d'intégrité |
| État des copies distantes | Confirmer leur actualisation |
| État des dépôts immuables | Vérifier que la protection est active |
| Résultats des tests de restauration | Vérifier la capacité de récupération |
| État du catalogue | Vérifier que les informations nécessaires à la restauration sont disponibles |

### 22.2 Pourquoi le succès d'un job ne suffit-il pas ?

Une tâche peut réussir alors qu'une charge importante est absente de la politique.

Une sauvegarde peut également être valide au niveau des fichiers, mais insuffisante pour récupérer une application entière.

Il faut donc surveiller à la fois les résultats techniques, la couverture des données et les résultats de restauration.

### 22.3 Vérifier la couverture

Une organisation doit pouvoir identifier les systèmes qui ne sont pas protégés.

Créer un inventaire comparant :

```text
INVENTAIRE DES SERVEURS
         |
         v
SYSTEMES ATTENDUS
         |
         v
COMPARAISON AVEC LES JOBS
         |
         v
+--------+---------+
|                  |
v                  v
Protégés        Non protégés
|                  |
v                  v
Contrôler les   Corriger la
résultats       couverture
```

Cette comparaison évite de se concentrer uniquement sur les tâches existantes et de manquer un nouveau serveur jamais intégré à la sauvegarde.

### 22.4 Alertes recommandées

Exemples de conditions à surveiller :

- Échec d'une tâche critique.
- Dernier point de restauration plus ancien que le RPO cible.
- Dépôt proche de la saturation.
- Copie distante en retard.
- Erreur de vérification.
- Tâche dépassant sa fenêtre normale.
- Catalogue ou base de gestion indisponible.
- Test de restauration échoué.

Les seuils doivent être adaptés à la politique et à la criticité du service.

## 23. Vérification d'intégrité, tests et restauration

### 23.1 Trois niveaux de contrôle

| Contrôle | Résultat recherché |
|---|---|
| Vérification technique | S'assurer que les données et métadonnées répondent aux contrôles du produit |
| Test de restauration | Confirmer que les données peuvent être récupérées |
| Test applicatif | Vérifier que l'application fonctionne après récupération |

Ces contrôles se complètent.

Un dépôt peut passer un contrôle d'intégrité et contenir un jeu de sauvegarde qui ne permet pas de remettre l'application en service dans le délai demandé.

### 23.2 Restaurer un fichier

La restauration d'un fichier permet généralement de tester rapidement l'accès au dépôt et la récupération ciblée.

Le test devrait vérifier :

- Le chemin.
- Le contenu.
- La date ou version sélectionnée.
- Les permissions.
- L'intégrité.
- Le respect du délai cible.

### 23.3 Restaurer une VM

Pour une VM, vérifier :

1. L'accès au point de restauration.
2. La présence de la configuration et des disques requis.
3. La disponibilité de l'espace cible.
4. L'absence de conflit avec la VM de production.
5. Le démarrage du système.
6. Les interfaces réseau.
7. Les dépendances.
8. Le fonctionnement applicatif.
9. Les données récupérées.
10. Le délai total.

La VM restaurée doit être isolée du réseau de production lorsqu'un conflit d'adresse, un doublon d'identité ou un risque de contamination est possible.

### 23.4 Restaurer une application

Une restauration applicative doit valider plus que le démarrage du serveur.

Par exemple, pour une application Web qui utilise une base de données, vérifier :

- L'accès HTTP.
- L'authentification.
- Les opérations de lecture.
- Les opérations d'écriture en environnement de test.
- La cohérence des données.
- Les dépendances externes.
- Les certificats.
- Les tâches programmées.

Le résultat doit être validé par les propriétaires techniques ou métier selon le périmètre.

## 24. Définir un PRA à partir des sauvegardes

### 24.1 Ce qu'est un plan de reprise d'activité

Le PRA décrit comment rétablir les services après un sinistre.

Il doit préciser :

- Les services prioritaires.
- Les RPO et RTO.
- Les contacts.
- Les responsabilités.
- Les dépendances.
- Les emplacements de sauvegarde.
- L'ordre de restauration.
- Les contrôles applicatifs.
- Les conditions de retour à la normale.

### 24.2 Ordre de reprise

Certains services dépendent d'autres composants.

Exemple :

```text
1. Infrastructure réseau
          |
          v
2. Identité / DNS / services de base
          |
          v
3. Stockage et machines nécessaires
          |
          v
4. Bases de données
          |
          v
5. Services applicatifs
          |
          v
6. Frontends et accès utilisateurs
          |
          v
7. Validation métier
```

Cet ordre est un exemple. L'ordre réel dépend des dépendances du service et de la conception de l'infrastructure.

### 24.3 Réduire le temps de reprise

Pour réduire le RTO, on peut :

- Prépositionner certaines ressources.
- Préparer des réseaux de reprise.
- Automatiser la création des VM.
- Documenter les comptes et secrets.
- Tester les procédures.
- Mesurer les temps de transfert.
- Réduire les opérations manuelles.
- Prioriser les services critiques.

Il faut tenir compte du coût et de la complexité de la solution.

### 24.4 Mesurer les objectifs réels

Après un test, enregistrer les durées mesurées :

```text
Détection du sinistre       : 09:00
Décision de reprise         : 09:15
Accès aux sauvegardes       : 09:30
Fin de restauration         : 10:25
Fin des tests techniques    : 10:45
Validation métier           : 11:00
```

Dans cet exemple fictif, la reprise opérationnelle est terminée à 11 h 00. Il faut définir le point de départ et le point de fin du RTO selon les engagements retenus.

## 25. Automatiser les opérations

### 25.1 Principes

L'automatisation réduit les oublis et rend les opérations plus reproductibles.

Elle peut couvrir :

- La découverte des systèmes.
- L'ajout aux politiques.
- La création des jobs.
- La planification.
- Les contrôles de configuration.
- Les rapports.
- Les vérifications de statut.
- Les notifications.
- Les tests de restauration.

Les actions destructives, telles que la purge des sauvegardes, doivent être contrôlées et soumises à la politique appropriée.

### 25.2 Utiliser les API

Certaines solutions proposent des API qui permettent d'intégrer les opérations à un outil de gestion ou à un pipeline.

Avant d'automatiser, définir :

- L'identité utilisée.
- Les autorisations.
- Les paramètres attendus.
- Les résultats à vérifier.
- Le traitement des erreurs.
- La gestion des répétitions.
- Les journaux d'audit.
- Les changements non planifiés.

Une API qui répond avec succès ne garantit pas nécessairement que toutes les données demandées sont couvertes et récupérables.

### 25.3 Contrôle des résultats

Un workflow peut ressembler à ceci :

```text
Déclenchement
      |
      v
Vérification de la configuration
      |
      v
Exécution de la sauvegarde
      |
      v
Collecte du résultat
      |
      v
Validation des données attendues
      |
      v
Mise à jour du rapport
      |
      v
Notification si anomalie
```

La vérification doit porter sur le résultat et la couverture, pas uniquement sur l'exécution de la commande.

## 26. Journalisation et reporting

### 26.1 Pourquoi conserver des rapports ?

Les rapports de sauvegarde permettent de suivre :

- La réussite des jobs.
- Les échecs.
- Les retards.
- Le volume traité.
- Les erreurs de lecture ou d'écriture.
- La consommation de stockage.
- Les copies distantes.
- Les vérifications.
- Les restaurations testées.

Ils facilitent également les revues de capacité et les échanges avec les responsables de service.

### 26.2 Exemple de rapport quotidien

```text
RAPPORT DE SAUVEGARDE

Date :
Nombre de charges attendues :
Nombre de charges protégées :
Jobs réussis :
Jobs avec avertissement :
Jobs échoués :
Données traitées :
Capacité disponible :
Dernière copie distante valide :
Dernière vérification d'intégrité :
Restauration de test la plus récente :
Actions de suivi :
Responsable :
```

Ces informations doivent être issues des systèmes de sauvegarde et de l'inventaire. Il ne faut pas déclarer une tâche réussie sans résultat vérifiable.

### 26.3 Rapport mensuel

Un rapport mensuel peut inclure :

- Le taux de réussite.
- Les incidents récurrents.
- Les systèmes non protégés.
- Les tests de restauration.
- Les évolutions de stockage.
- Les écarts de RPO.
- Les écarts de RTO.
- Les risques de capacité.
- Les changements des politiques.
- Les actions préventives.

Les pourcentages doivent indiquer leur mode de calcul. Par exemple, un taux de réussite des jobs n'est pas identique à un taux de couverture des systèmes.

## 27. Étude de cas : plateforme de sauvegarde pour une PME

### 27.1 Contexte

Une entreprise possède :

- Six serveurs virtuels.
- Deux serveurs physiques.
- Un serveur de fichiers.
- Une base de données métier.
- Un cluster de virtualisation.
- Un emplacement distant disponible pour les copies.
- Une équipe informatique limitée.

Les données critiques doivent pouvoir être restaurées après une panne, une suppression ou un incident de sécurité.

### 27.2 Architecture proposée

```text
                 INFRASTRUCTURE ENTREPRISE
                            |
                 +----------+----------+
                 |                     |
                 v                     v
           Cluster VM            Serveurs physiques
                 |                     |
                 +----------+----------+
                            |
                            v
                PLATEFORME DE SAUVEGARDE
                            |
                            v
                   DEPOT PRINCIPAL
                            |
                 +----------+----------+
                 |                     |
                 v                     v
            DEPOT IMMUTABLE       COPIE DISTANTE
                 |                     |
                 +----------+----------+
                            |
                            v
                  TESTS DE RESTAURATION
```

### 27.3 Ce qui doit être décidé

Avant le déploiement, l'entreprise doit choisir :

- La solution de sauvegarde.
- Les composants de gestion.
- Le dépôt principal.
- La copie secondaire.
- La méthode de sauvegarde des bases.
- La rétention.
- Le chiffrement.
- Les comptes d'administration.
- Les horaires.
- La fréquence des vérifications.
- Le mode de notification.
- La procédure de reprise.
- Les responsabilités de chaque équipe.

### 27.4 Critères de validation

La solution ne sera pas considérée comme opérationnelle simplement parce que tous les jobs sont créés.

Il faudra démontrer :

1. Que tous les systèmes attendus sont couverts.
2. Que les sauvegardes se terminent.
3. Que les erreurs sont détectées.
4. Que les dépôts sont accessibles et assez grands.
5. Que les copies secondaires sont actualisées.
6. Que les accès sont sécurisés.
7. Que les restaurations fonctionnent.
8. Que les délais correspondent aux objectifs.
9. Que les procédures sont documentées.
10. Que l'équipe peut rétablir le service.

## 28. Travaux pratiques guidés

### TP 1 — Construire une matrice de sauvegarde

**Objectif :** définir des règles de protection pour plusieurs charges.

Créer une matrice contenant au moins :

- Un serveur de fichiers.
- Une VM applicative.
- Une base de données.
- Un serveur Windows.
- Un environnement de test.

Pour chaque charge, préciser :

- Le propriétaire.
- Le RPO.
- Le RTO.
- La fréquence.
- Le dépôt.
- La rétention.
- Le chiffrement.
- Le test de restauration.
- La procédure de reprise.

Livrable : un tableau de politiques documenté.

### TP 2 — Déployer un dépôt de laboratoire Proxmox Backup Server

**Objectif :** comprendre les étapes d'exploitation d'un dépôt PBS.

Dans un environnement de test compatible :

1. Préparer le serveur de sauvegarde.
2. Créer un datastore.
3. Configurer les accès.
4. Relier l'environnement source.
5. Réaliser une première sauvegarde.
6. Vérifier le snapshot.
7. Exécuter une vérification d'intégrité.
8. Créer une politique de rétention.
9. Exécuter un test de restauration.
10. Documenter les résultats.

Ne pas connecter un dépôt de laboratoire à une production sans une validation de sécurité et une revue de l'architecture.

Livrable : schéma, procédure et preuves de sauvegarde et restauration.

### TP 3 — Construire une chaîne de sauvegarde VM

**Objectif :** comprendre les points de restauration.

Sur une plateforme virtualisée de test :

1. Créer une VM avec des données non sensibles.
2. Exécuter une sauvegarde initiale.
3. Modifier un fichier de test.
4. Réaliser une nouvelle sauvegarde.
5. Vérifier les points de restauration.
6. Restaurer l'état initial dans un environnement séparé.
7. Comparer les fichiers.
8. Mesurer le temps de restauration.

Livrable : description des versions et démonstration de récupération.

### TP 4 — Tester une copie indépendante

**Objectif :** valider le fonctionnement d'une seconde copie.

1. Identifier le dépôt principal.
2. Définir une destination distincte.
3. Configurer la copie selon le produit.
4. Réaliser un transfert.
5. Vérifier la présence de la copie.
6. Vérifier les autorisations.
7. Simuler l'indisponibilité du dépôt principal dans le laboratoire.
8. Démontrer que la copie secondaire est accessible.
9. Restaurer des données de test.

Livrable : rapport de validation de la copie indépendante.

### TP 5 — Mesurer le RTO

**Objectif :** déterminer le temps réel nécessaire à la récupération.

Réaliser un test de restauration avec une chronologie mesurable.

Enregistrer :

- Début du test.
- Début de la restauration.
- Fin du transfert.
- Démarrage du système.
- Validation technique.
- Validation applicative.
- Fin du test.

Calculer la durée totale et comparer le résultat au RTO cible.

Livrable : rapport détaillé avec les écarts et les améliorations.

### TP 6 — Créer un rapport de sauvegarde

**Objectif :** organiser la supervision des jobs.

Préparer un rapport contenant :

- Les charges attendues.
- Les charges effectivement couvertes.
- Les jobs réussis ou échoués.
- Les erreurs.
- La capacité.
- Les copies secondaires.
- Les contrôles d'intégrité.
- Les tests de restauration.
- Les actions en retard.

Livrable : rapport quotidien et rapport mensuel de démonstration.

## 29. Exercices d'application avec corrections

### Exercice 1 — Capacité quotidienne

Une entreprise protège 4 To de données. Le volume quotidien modifié est estimé à 3 %.

Calculer le volume quotidien modifié dans ce modèle simplifié.

**Correction :**

```text
4 To x 3 % = 0,12 To
```

Cela représente environ 120 Go par jour avec une convention décimale simplifiée.

Le volume réellement écrit dans le dépôt dépend du logiciel, de la déduplication, de la compression et de la méthode de sauvegarde.

### Exercice 2 — Fenêtre de sauvegarde

Une sauvegarde doit transférer 300 Go. Le débit effectif mesuré est de 50 Mo/s.

Estimer la durée de transfert.

**Correction :**

```text
300 Go = 300 000 Mo

300 000 / 50 = 6 000 secondes

6 000 secondes = 1 h 40
```

Cette estimation ne comprend ni le traitement préalable, ni la validation, ni la compression, ni les autres opérations qui peuvent prolonger le job.

### Exercice 3 — RPO

Le dernier point de restauration valide date de 01 h 00. Un incident est détecté à 09 h 30. Le RPO demandé est de trois heures.

La politique respecte-t-elle l'objectif si aucun autre mécanisme de récupération n'existe ?

**Correction :**

La perte potentielle peut atteindre huit heures et trente minutes de données.

Le RPO de trois heures n'est donc pas garanti par ce seul point de restauration.

### Exercice 4 — Rétention

Une entreprise conserve sept points quotidiens. Une corruption de fichier, introduite il y a vingt jours mais détectée aujourd'hui, a été intégrée aux nouvelles sauvegardes.

La politique actuelle permet-elle forcément de retrouver la version saine ?

**Correction :**

Non. Si toutes les versions antérieures ont été supprimées selon la rétention quotidienne, la version saine peut ne plus être disponible. Une rétention plus longue ou une politique GFS peut être nécessaire pour certains types de données.

### Exercice 5 — Tâche réussie, couverture incomplète

Tous les jobs configurés sont en succès. Cependant, un nouveau serveur n'apparaît dans aucun job.

La politique peut-elle être considérée comme satisfaisante ?

**Correction :**

Non. Le taux de réussite des jobs ne prouve pas que toutes les charges requises sont protégées.

Il faut comparer l'inventaire des systèmes à la couverture réelle des politiques de sauvegarde.

### Exercice 6 — Copie secondaire

Le dépôt principal et le dépôt secondaire utilisent le même compte d'administration. Ce compte peut supprimer toutes les données des deux dépôts.

Quel risque subsiste ?

**Correction :**

Une compromission de ce compte peut permettre de supprimer les deux copies. Il faut renforcer l'isolation des identités et limiter les droits de destruction. Une copie immuable ou hors ligne peut compléter les protections.

### Exercice 7 — Sauvegarde d'une base active

Un administrateur copie les fichiers d'une base de données alors qu'elle continue à écrire des données.

Pourquoi cette méthode peut-elle poser problème ?

**Correction :**

La copie n'est pas nécessairement cohérente. Les fichiers peuvent représenter des états différents et le moteur peut nécessiter une procédure de récupération.

Il faut utiliser une méthode de sauvegarde adaptée au moteur et au niveau de cohérence attendu.

### Exercice 8 — Vérification contre restauration

Une tâche de vérification confirme que le dépôt est cohérent, mais aucune restauration n'a été testée depuis un an.

Quel contrôle manque ?

**Correction :**

Un test de restauration. Il faut confirmer la capacité à récupérer les données, à reconstruire les dépendances et à respecter les objectifs de reprise.

### Exercice 9 — Choix de solution

Une entreprise utilise déjà Proxmox VE et veut sauvegarder ses VM avec déduplication et vérification d'intégrité.

Quelle solution peut être étudiée en priorité ?

**Correction :**

Proxmox Backup Server est un candidat naturel à évaluer grâce à son intégration avec Proxmox VE. Il faut encore vérifier les exigences de sauvegarde, l'architecture, les copies distantes, le dimensionnement et les besoins de restauration.

### Exercice 10 — Calcul du RTO

Une restauration prend 90 minutes, le démarrage des systèmes 20 minutes et les tests applicatifs 35 minutes.

Quel est le délai total du scénario ?

**Correction :**

```text
90 + 20 + 35 = 145 minutes
```

Soit 2 heures et 25 minutes.

Le RTO réellement obtenu dépend de l'heure de départ et de la définition de la fin de reprise adoptée par l'organisation.

## 30. Projet de fin de niveau

### Concevoir une solution de sauvegarde d'entreprise

L'objectif est de proposer et de documenter une architecture pour une entreprise possédant :

- Un cluster de virtualisation.
- Des serveurs physiques.
- Un serveur de fichiers.
- Une base de données métier.
- Plusieurs applications.
- Un dépôt de sauvegarde local.
- Un emplacement distant pour une seconde copie.

### Livrable A — Architecture

Documenter :

- La solution choisie.
- Les composants.
- Le plan de contrôle.
- Le plan de données.
- Les proxys ou agents.
- Les dépôts.
- La copie distante.
- Les dépendances.
- Les domaines de panne.

### Livrable B — Politique de sauvegarde

Définir :

- Le périmètre.
- La fréquence.
- Le type de sauvegarde.
- La rétention.
- Le chiffrement.
- Le dépôt.
- Les identités.
- Les règles d'immuabilité.
- Les RPO et RTO.
- Les vérifications.

### Livrable C — Dimensionnement

Estimer :

- Le volume initial.
- La croissance.
- Les changements quotidiens.
- La durée des jobs.
- Le débit réseau.
- La capacité utile.
- La marge.
- Le coût du stockage hors site.
- Le débit de restauration attendu.

Séparer clairement les données mesurées des hypothèses de calcul.

### Livrable D — Automatisation et supervision

Définir :

- Les horaires.
- Les procédures de lancement.
- Les notifications.
- Les rapports.
- Le suivi de couverture.
- Les contrôles de capacité.
- Les vérifications d'intégrité.
- Les tests de restauration.

### Livrable E — Plan de reprise

Fournir :

- La liste des services prioritaires.
- L'ordre de reprise.
- Les dépendances.
- Les étapes de restauration.
- Les critères de validation.
- Les contacts et responsabilités.
- Les RPO et RTO cibles.
- Les procédures de retour à la normale.

### Livrable F — Démonstration

La démonstration doit prouver :

1. Qu'une sauvegarde fonctionne.
2. Qu'un point de restauration est disponible.
3. Qu'une copie secondaire existe.
4. Que les données peuvent être vérifiées.
5. Qu'une restauration peut être réalisée.
6. Que les données restaurées correspondent aux attentes.
7. Que le délai est mesuré.
8. Que la procédure est documentée.

Le projet ne peut pas être validé uniquement par la présence d'un dépôt contenant des fichiers. La preuve de récupération est essentielle.

## 31. Bonnes pratiques à retenir

### Architecture

- Séparer les données de production des dépôts de sauvegarde.
- Prévoir une copie indépendante.
- Identifier les points uniques de défaillance.
- Protéger la configuration et le catalogue nécessaires à la restauration.
- Dimensionner les dépôts selon les volumes mesurés.
- Vérifier les performances de récupération.

### Politiques

- Classer les données par criticité.
- Définir les RPO et RTO.
- Utiliser une rétention adaptée au délai de détection.
- Documenter le périmètre.
- Contrôler l'intégration des nouveaux systèmes.
- Séparer les sauvegardes opérationnelles de l'archivage à long terme.

### Sécurité

- Appliquer le moindre privilège.
- Séparer les identités de production et de sauvegarde.
- Protéger les clés et secrets.
- Prévoir des copies immuables ou hors ligne.
- Contrôler les droits de suppression.
- Journaliser les opérations sensibles.
- Vérifier que les protections restent actives.

### Exploitation

- Examiner les erreurs de jobs.
- Surveiller l'âge des derniers points de restauration valides.
- Contrôler la capacité des dépôts.
- Vérifier les copies secondaires.
- Tester les restaurations.
- Documenter les incidents.
- Corriger les échecs récurrents.
- Mesurer les RPO et RTO réellement obtenus.

### Amélioration continue

- Réexaminer périodiquement les politiques.
- Tester les restaurations à partir de plusieurs points.
- Contrôler les procédures de reprise.
- Ajuster la capacité à partir des mesures réelles.
- Réviser les accès.
- Valider la réversibilité.
- Conserver des preuves des tests.

## 32. Référence opérationnelle rapide

| Besoin | Outil ou mécanisme |
|---|---|
| Créer une archive de fichiers | `tar` |
| Copier et synchroniser des fichiers | `rsync` |
| Sauvegarde versionnée de fichiers | Restic ou solution équivalente |
| Sauvegarde de VM dans une plateforme compatible | Veeam, Proxmox Backup Server ou solution équivalente |
| Gestion centralisée de clients et de jobs | Solution de sauvegarde avec serveur de gestion |
| Sauvegarde de systèmes Windows pris en charge | Windows Server Backup / `wbadmin` |
| Sauvegarde de fichiers multi-plateformes | Bareos ou solution compatible |
| Vérifier un dépôt PBS | Fonction de vérification de Proxmox Backup Server |
| Appliquer la rétention PBS | Prune selon la politique retenue |
| Récupérer l'espace PBS non référencé | Garbage collection |
| Créer une copie secondaire | Backup Copy, sync job ou fonction équivalente |
| Protéger contre la suppression | Immuabilité, contrôle d'accès et copies isolées |
| Mesurer une restauration | Chronologie et rapport de test |
| Valider une application restaurée | Tests techniques et métier |

## 33. Glossaire

**Agent :** composant installé sur un système protégé pour participer aux opérations de sauvegarde ou de restauration.

**Backup Copy :** mécanisme qui crée une copie supplémentaire des sauvegardes selon une politique définie par la solution.

**Catalogue :** ensemble de métadonnées qui aide à retrouver et gérer les points de restauration.

**Chaîne de sauvegarde :** ensemble de points ou d'éléments interdépendants nécessaires à certaines restaurations.

**Déduplication :** mécanisme visant à éviter le stockage répétitif de données identiques.

**Dépôt :** emplacement géré pour stocker les sauvegardes.

**GFS :** politique de rétention organisant des points de restauration quotidiens, hebdomadaires, mensuels ou annuels selon les règles choisies.

**Garbage collection :** opération qui récupère l'espace occupé par des données qui ne sont plus référencées, selon le mécanisme du produit.

**Immuabilité :** mécanisme qui empêche la modification ou la suppression des données pendant une période définie.

**Job :** unité de configuration d'une tâche de sauvegarde, copie ou restauration, selon la solution.

**Plan de contrôle :** fonctions qui configurent, planifient et administrent les opérations.

**Plan de données :** chemin emprunté par les données lors des opérations de lecture, transfert et écriture.

**Proxy :** composant qui réalise certaines opérations de lecture, traitement ou transfert dans une architecture de sauvegarde.

**Prune :** opération qui applique des règles de rétention et retire des points de restauration qui ne doivent plus être conservés.

**RPO :** objectif de point de récupération, exprimant la perte maximale de données acceptable en temps.

**RTO :** objectif de délai de reprise, exprimant le temps cible de rétablissement du service.

**Restauration applicative :** récupération suivie d'une validation des fonctions métier concernées.

**Rétention :** règles définissant les versions conservées et la durée de conservation.

**Sauvegarde synthétique complète :** point de restauration complet construit à partir de données déjà présentes dans le dépôt, selon les mécanismes de la solution.

**Stockage objet :** modèle de stockage organisé en objets, souvent utilisé pour des volumes importants et des copies distantes.

**Vérification d'intégrité :** contrôle destiné à détecter certaines altérations ou incohérences des sauvegardes.

## 34. Documentation officielle

### Veeam

- Documentation Veeam Backup & Replication : https://helpcenter.veeam.com/docs/vbr/userguide/
- Fonctionnement des sauvegardes : https://helpcenter.veeam.com/docs/vbr/userguide/about_backup.html
- Copies de sauvegarde : https://helpcenter.veeam.com/docs/vbr/userguide/backup_copy_managing_jobs.html
- Dépôt Linux durci : https://helpcenter.veeam.com/docs/vbr/userguide/hardened_repository.html
- Immuabilité : https://helpcenter.veeam.com/docs/vbr/userguide/immutability.html

### Proxmox Backup Server

- Documentation générale : https://pbs.proxmox.com/docs/
- Documentation officielle Proxmox Backup Server : https://www.proxmox.com/en/downloads/proxmox-backup-server/documentation
- Maintenance, rétention et vérification : https://pbs.proxmox.com/docs/maintenance.html
- Gestion des serveurs distants : https://pbs.proxmox.com/docs/managing-remotes.html
- FAQ et principes de stockage : https://pbs.proxmox.com/docs/faq.html

### Bareos

- Documentation générale : https://docs.bareos.org/
- Présentation de l'architecture : https://www.bareos.com/software/

### Microsoft

- Référence `wbadmin` : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin
- Sauvegarde de l'état système : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-systemstatebackup
- Restauration : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-recovery
- Azure Backup : https://learn.microsoft.com/en-us/azure/backup/
- Sécurité d'Azure Backup : https://learn.microsoft.com/en-us/azure/backup/security-overview

### Restic et sécurité

- Documentation Restic : https://restic.readthedocs.io/
- Guide CISA contre les rançongiciels : https://www.cisa.gov/stopransomware/ransomware-guide

Les versions des produits, les fonctionnalités disponibles et les conditions de licence peuvent évoluer. Vérifier les documentations correspondant aux versions envisagées avant toute mise en production.

## 35. Conclusion du niveau intermédiaire

Une solution de sauvegarde d'entreprise doit fournir une protection cohérente de plusieurs types de charges, une gestion centralisée, une conservation adaptée, une copie indépendante, des contrôles d'intégrité et une capacité de restauration démontrée.

Veeam, Proxmox Backup Server, Bareos, les outils Microsoft et les solutions cloud répondent à des besoins différents. Le choix doit être fait selon les plateformes à protéger, le modèle d'exploitation, les objectifs métier, les ressources disponibles et les contraintes de sécurité.

La conception ne s'arrête pas à l'installation du logiciel. Elle doit intégrer la couverture des systèmes, la gestion des identités, la protection des dépôts, le suivi des jobs, les tests de restauration et la préparation à un sinistre.

Le niveau intermédiaire est atteint lorsque l'administrateur sait configurer et exploiter les sauvegardes de plusieurs charges, suivre leurs résultats, identifier les défaillances et démontrer que les données sont récupérables.

**La véritable valeur d'une plateforme de sauvegarde se mesure à sa capacité à restaurer les bonnes données, dans le bon ordre et dans le délai attendu, y compris lorsque la production ou le site principal est indisponible.**