# Windows Server Expert : Failover Clustering et Hyper-V
## Cours expert — Haute disponibilité, virtualisation, stockage, migration et reprise après sinistre

## 1. Présentation du cours

### 1.1 Objectif général

Les niveaux précédents t'ont permis d'apprendre à installer Windows Server, à administrer Active Directory, à gérer les GPO et à automatiser des tâches de gestion de parc.

Ce niveau expert change d'échelle : il s'agit désormais de concevoir et d'exploiter une infrastructure capable de continuer à fournir des services malgré la panne d'un serveur, de déplacer des machines virtuelles pendant la maintenance, de protéger les données et de préparer une reprise après sinistre.

Les deux technologies centrales sont :

- **Windows Server Failover Clustering (WSFC)** : mécanisme de haute disponibilité qui coordonne plusieurs serveurs, appelés nœuds, pour maintenir les rôles et services pris en charge.
- **Hyper-V** : hyperviseur de Microsoft permettant d'exécuter plusieurs machines virtuelles sur un même serveur physique.

Associées, ces technologies peuvent fournir une plateforme de virtualisation hautement disponible.

Cependant, elles ne constituent pas à elles seules une solution de sauvegarde complète, ne suppriment pas tous les points uniques de défaillance et ne garantissent pas une absence absolue d'interruption.

La compétence experte consiste donc à comprendre les mécanismes, connaître leurs limites, concevoir l'architecture appropriée et vérifier son comportement en cas d'incident réel ou simulé.

### 1.2 Compétences visées

À la fin du cours, tu devras être capable de :

- Concevoir une architecture Hyper-V adaptée aux besoins de disponibilité.
- Dimensionner les ressources CPU, mémoire, stockage et réseau des hôtes.
- Distinguer haute disponibilité, migration à chaud, réplication et sauvegarde.
- Installer et préparer un cluster de basculement.
- Valider la compatibilité matérielle et logicielle des nœuds.
- Configurer et contrôler le quorum.
- Comprendre les rôles des réseaux du cluster.
- Utiliser le stockage partagé et les volumes partagés de cluster.
- Comprendre les principes de Storage Spaces Direct.
- Créer des commutateurs virtuels Hyper-V adaptés à l'infrastructure.
- Configurer une machine virtuelle pour une utilisation en cluster.
- Réaliser une migration à chaud.
- Organiser une maintenance coordonnée des nœuds.
- Mettre en œuvre une stratégie de mise à jour avec Cluster-Aware Updating.
- Concevoir une solution de reprise après sinistre avec Hyper-V Replica.
- Construire un plan de sauvegarde cohérent pour les machines virtuelles.
- Détecter les principaux problèmes de quorum, de stockage, de réseau et d'authentification.
- Collecter des informations de diagnostic avec PowerShell.
- Rédiger des procédures de maintenance, de basculement et de restauration.

### 1.3 Prérequis techniques

Ce cours suppose que tu maîtrises déjà :

- L'installation et l'administration de Windows Server.
- Active Directory et les comptes ordinateurs.
- DNS, DHCP, sous-réseaux, passerelles et routage.
- Les groupes de sécurité et les permissions.
- PowerShell et les modules d'administration Windows.
- Les notions de stockage, de systèmes de fichiers et de sauvegarde.
- L'administration des serveurs à distance.

Il est particulièrement utile d'avoir déjà manipulé Hyper-V sur un serveur de laboratoire.

### 1.4 Versions et limites de compatibilité

Les exemples se basent principalement sur Windows Server 2022 et Windows Server 2025, en signalant les considérations importantes pour les versions prises en charge.

Tous les environnements ne possèdent pas exactement les mêmes fonctionnalités. Les capacités disponibles peuvent dépendre :

- De la version de Windows Server.
- De l'édition et des droits de licence.
- Du matériel certifié et de ses pilotes.
- Des cartes réseau et des capacités de commutation.
- Du type de stockage.
- Des mises à jour appliquées.
- Des services et rôles installés.
- De l'architecture du cluster.

Une commande PowerShell correcte ne rend pas automatiquement une architecture prise en charge. Il faut valider le matériel, les versions, le réseau, le stockage et les conditions de support avant de construire une plateforme de production.

## 2. Comprendre la haute disponibilité

### 2.1 Le problème du serveur unique

Imaginons une entreprise qui héberge toutes ses applications sur un seul serveur physique.

```text
                     UTILISATEURS
                          |
                          v
                  +---------------+
                  | Serveur HV01  |
                  |               |
                  | Hyper-V       |
                  | Application   |
                  | Base de données
                  +---------------+
```

Si le serveur tombe en panne, l'ensemble des services hébergés devient potentiellement indisponible.

Les causes peuvent être nombreuses :

- Défaillance de la carte mère.
- Problème d'alimentation.
- Panne de mémoire.
- Défaillance du système d'exploitation.
- Défaillance d'un contrôleur de stockage.
- Erreur lors d'une mise à jour.
- Incident réseau.
- Erreur humaine.
- Corruption d'un composant logiciel.

Même si les machines virtuelles sont correctement sauvegardées, il faut disposer d'un serveur de remplacement et restaurer les services avant de retrouver un fonctionnement normal.

### 2.2 Introduire un deuxième hôte

Une première amélioration consiste à disposer de deux serveurs Hyper-V.

```text
                    UTILISATEURS
                         |
                   Réseau de production
                         |
              +----------+----------+
              |                     |
              v                     v
        +-----------+         +-----------+
        |   HV01    |         |   HV02    |
        | Hyper-V   |         | Hyper-V   |
        +-----------+         +-----------+
              |                     |
              +----------+----------+
                         |
                  Stockage partagé
```

Disposer de deux serveurs ne suffit toutefois pas à assurer un basculement automatique.

Il faut notamment :

- Un mécanisme de coordination.
- Un stockage accessible par le nœud qui reprendra la charge, selon le modèle retenu.
- Une configuration réseau appropriée.
- Des rôles pris en charge par le cluster.
- Une stratégie de quorum.
- Une méthode de détection et de gestion des pannes.
- Des procédures de maintenance et de reprise.

C'est le rôle de Windows Server Failover Clustering.

### 2.3 Que signifie un basculement ?

Un cluster de basculement regroupe plusieurs serveurs indépendants qui coordonnent l'exécution de rôles ou de services.

Chaque serveur membre est appelé un **nœud**.

Lorsqu'un nœud ou un rôle tombe en panne, le cluster peut transférer la responsabilité du rôle vers un autre nœud disponible.

```text
AVANT LA PANNE

HV01 : EN SERVICE
  |
  +-- VM-APP01 : active
  +-- VM-DB01  : active

HV02 : EN SERVICE
  |
  +-- VM-WEB01 : active


PANNE DE HV01

HV01 : INDISPONIBLE
  |
  +-- VM-APP01 : interruption détectée
  +-- VM-DB01  : interruption détectée


APRÈS LE BASCULEMENT

HV02 : EN SERVICE
  |
  +-- VM-WEB01 : continue
  +-- VM-APP01 : redémarrée selon le scénario
  +-- VM-DB01  : redémarrée selon le scénario
```

Dans un cluster Hyper-V classique, les machines virtuelles affectées par la panne peuvent devoir être redémarrées sur un autre nœud.

Il ne faut pas confondre ce mécanisme avec une migration à chaud, qui déplace une machine virtuelle en fonctionnement entre deux hôtes sans interruption normalement perceptible.

### 2.4 Haute disponibilité et tolérance aux pannes

La **haute disponibilité** vise à limiter la durée pendant laquelle un service est indisponible.

La **tolérance aux pannes**, au sens strict, vise à maintenir le service sans interruption malgré une panne.

Un cluster Hyper-V peut fortement améliorer la disponibilité, mais un basculement classique après la perte brutale d'un nœud implique généralement une interruption et un redémarrage de la machine virtuelle.

Le résultat dépend également de l'application hébergée.

Une application qui récupère correctement après un redémarrage ne présente pas nécessairement le même niveau de disponibilité qu'une application conçue pour fonctionner sur plusieurs instances indépendantes.

### 2.5 Les quatre notions à ne jamais confondre

| Mécanisme | Objectif | Exemple |
|---|---|---|
| Haute disponibilité | Limiter l'indisponibilité après un incident local | Redémarrer une VM sur un autre nœud |
| Migration à chaud | Déplacer une VM en fonctionnement pour une opération planifiée | Vider HV01 avant sa maintenance |
| Réplication | Maintenir une copie des données et de l'état d'une VM sur un autre hôte ou site | Hyper-V Replica |
| Sauvegarde | Conserver des points de restauration récupérables | Restaurer une VM supprimée ou corrompue |

Une infrastructure résiliente peut combiner ces quatre mécanismes, car ils couvrent des risques différents.

## 3. RTO, RPO et objectifs de disponibilité

### 3.1 Le RTO

Le **Recovery Time Objective**, ou RTO, définit le délai maximal ciblé pour rétablir un service après une interruption.

Exemple :

Une application de gestion interne doit être rétablie dans les quinze minutes suivant une panne.

Le RTO cible est de quinze minutes.

Pour vérifier que cet objectif est réaliste, il faut prendre en compte le temps de détection, le basculement, le démarrage du système, la récupération de l'application et les contrôles fonctionnels.

### 3.2 Le RPO

Le **Recovery Point Objective**, ou RPO, définit la quantité de données qu'une organisation accepte de perdre, exprimée en durée.

Exemple :

Une base de données dont le RPO est de cinq minutes doit pouvoir être récupérée avec un décalage maximal ciblé de cinq minutes par rapport au moment de la panne.

Le RPO réel dépend de la technologie de réplication ou de sauvegarde utilisée, de la fréquence des opérations et de leur bon fonctionnement.

### 3.3 Exemple de besoins

| Service | RTO cible | RPO cible |
|---|---:|---:|
| Application métier interne | 15 minutes | 5 minutes |
| Portail Web secondaire | 30 minutes | 15 minutes |
| Serveur de fichiers non critique | 4 heures | 1 heure |
| Environnement de test | 1 jour | 1 jour |

Ces valeurs sont des exemples. Elles doivent provenir d'une analyse métier, d'une estimation des pertes et d'une validation technique.

### 3.4 Pourquoi le RTO et le RPO changent la conception

Un objectif de reprise de quelques minutes n'entraîne pas les mêmes choix qu'une reprise possible le lendemain.

Il peut nécessiter :

- Des hôtes de réserve.
- Du stockage répliqué.
- Des équipements réseau redondants.
- Une procédure de basculement documentée.
- Des sauvegardes fréquentes.
- Des tests réguliers de restauration.
- Une supervision centralisée.
- Une équipe capable d'intervenir rapidement.

Il ne suffit pas d'installer un cluster pour atteindre automatiquement les objectifs de disponibilité définis par le métier.

## 4. Architecture Hyper-V

### 4.1 Le rôle de l'hyperviseur

Hyper-V est l'hyperviseur de Microsoft pour les systèmes Windows Server et certaines éditions clientes de Windows.

Sur un hôte Windows Server, Hyper-V permet de créer et d'exécuter plusieurs machines virtuelles partageant les ressources matérielles de la machine physique.

```text
                  SERVEUR PHYSIQUE
         +--------------------------------+
         | CPU / RAM / Cartes réseau      |
         | Contrôleurs et stockage        |
         +--------------------------------+
                         |
                         v
                  HYPER-V
         +--------------------------------+
         | Commutateurs virtuels          |
         | Planification CPU              |
         | Mémoire virtuelle              |
         | Disques virtuels               |
         +--------------------------------+
               |          |          |
               v          v          v
          +---------+ +---------+ +---------+
          | VM-APP01| | VM-DB01 | | VM-WEB01|
          | Windows | | Windows | | Linux   |
          | Server  | | Server  | |         |
          +---------+ +---------+ +---------+
```

L'hôte gère les ressources physiques. Les machines virtuelles disposent d'un matériel virtuel présenté par Hyper-V.

### 4.2 Les générations de machines virtuelles

Hyper-V distingue principalement deux générations de machines virtuelles.

**Génération 1**

Elle utilise une architecture matérielle virtuelle plus ancienne et permet de prendre en charge certains systèmes ou scénarios historiques.

**Génération 2**

Elle utilise un firmware UEFI virtuel et offre des fonctionnalités modernes adaptées aux systèmes pris en charge.

Le choix doit être effectué lors de la création de la machine virtuelle, en fonction des exigences du système invité et de la solution de démarrage envisagée.

Il ne faut pas choisir une génération au hasard : le changement ultérieur n'est pas une simple modification de paramètre.

### 4.3 Les composants d'une machine virtuelle

Une machine virtuelle comprend notamment :

- Sa configuration.
- Ses processeurs virtuels.
- Sa mémoire.
- Ses interfaces réseau.
- Ses disques virtuels.
- Ses paramètres de démarrage.
- Ses points de contrôle éventuels.
- Ses périphériques virtuels.
- Ses paramètres de sécurité.

Schéma conceptuel :

```text
VM-APP01
|
+-- Configuration de la VM
|
+-- vCPU : 4
|
+-- RAM : 8 Go
|
+-- vNIC : vSwitch-Production
|
+-- Disque système : APP01-OS.vhdx
|
+-- Disque données : APP01-DATA.vhdx
|
+-- Système invité : Windows Server
```

Les ressources présentées dans cet exemple sont fictives. Les besoins réels dépendent de l'application.

### 4.4 Mémoire fixe et mémoire dynamique

Hyper-V peut utiliser une mémoire configurée de manière statique ou dynamique, selon le système invité et le scénario.

La mémoire fixe apporte un comportement relativement prévisible : une quantité définie de mémoire est attribuée à la VM.

La mémoire dynamique permet à Hyper-V d'adapter l'attribution de mémoire dans les limites configurées.

Cependant, elle ne crée pas de mémoire physique supplémentaire.

Sur un serveur fortement chargé, une configuration trop généreuse peut dégrader les performances de plusieurs machines virtuelles.

Pour les applications sensibles à la latence, les bases de données ou les logiciels ayant des exigences spécifiques, il faut valider le comportement réel avant d'activer la mémoire dynamique.

### 4.5 Processeurs virtuels

Le nombre de processeurs virtuels doit être dimensionné selon la charge de travail.

Attribuer systématiquement un grand nombre de vCPU à toutes les VM n'est pas une méthode de dimensionnement valable.

Un excès de vCPU peut compliquer la planification CPU sans améliorer les performances de l'application.

Il faut prendre en compte :

- Le nombre de cœurs physiques.
- La charge moyenne et maximale.
- La concurrence entre les machines virtuelles.
- Les exigences de l'application.
- Les pics de charge.
- La capacité restante en cas de panne d'un nœud.

Le dimensionnement doit être vérifié à l'aide de mesures et non uniquement par intuition.

### 4.6 Configuration et disques virtuels

Le format VHDX est couramment utilisé pour les disques virtuels Hyper-V.

Un disque virtuel à taille fixe réserve sa capacité au stockage selon le fonctionnement du format.

Un disque à expansion dynamique utilise initialement moins d'espace physique et croît lorsque les données sont ajoutées.

Cela implique une différence importante de gestion de capacité.

Un disque virtuel dynamique de 2 To dont seulement 100 Go sont occupés ne garantit pas que 2 To de stockage physique soient disponibles. Il faut surveiller l'espace réel sur le volume qui héberge le fichier.

### 4.7 Un fichier VHDX n'est pas une sauvegarde

Copier un fichier VHDX pendant que sa machine virtuelle est en cours d'utilisation ne constitue pas à lui seul une sauvegarde fiable.

Il faut tenir compte de l'état d'écriture, de la configuration de la VM et de la cohérence de l'application.

Pour protéger les machines virtuelles, privilégie une solution de sauvegarde compatible avec Hyper-V et capable de gérer les points de restauration, la cohérence applicative et les scénarios de restauration.

## 5. Architectures de haute disponibilité Hyper-V

### 5.1 Cluster avec stockage partagé

L'architecture traditionnelle utilise plusieurs nœuds Hyper-V accédant à un stockage commun.

```text
              +-----------------------+
              | Cluster WSFC          |
              | CL-HV                 |
              +-----------------------+
                  |               |
                  v               v
             +--------+      +--------+
             |  HV01  |      |  HV02  |
             +--------+      +--------+
                  |               |
                  +-------+-------+
                          |
                          v
                 +----------------+
                 | Stockage partagé|
                 | SAN / iSCSI / FC|
                 +----------------+
                          |
                          v
                    Volumes CSV
                          |
                          v
                 Fichiers des VM
```

Le stockage partagé peut être fourni par une infrastructure SAN ou une architecture adaptée au cluster.

Les nœuds ne doivent pas seulement voir le même stockage : ils doivent pouvoir l'utiliser dans une configuration supportée, avec les pilotes et la configuration appropriés.

### 5.2 Architecture hyperconvergée

Une autre approche consiste à combiner les capacités de calcul et de stockage dans les mêmes serveurs.

Storage Spaces Direct peut agréger des disques internes de plusieurs nœuds afin de fournir un stockage résilient défini par logiciel.

```text
              CLUSTER HYPERCONVERGÉ
              +-------------------+
              |        HV01       |
              | Hyper-V + Disques |
              +-------------------+
                      ||
                Réseau de stockage
                à haut débit
                      ||
              +-------------------+
              |        HV02       |
              | Hyper-V + Disques |
              +-------------------+
```

Ce modèle ne doit pas être confondu avec un cluster utilisant un SAN partagé traditionnel.

Les exigences matérielles, réseau et de stockage sont différentes.

### 5.3 Comparaison des architectures

| Critère | Stockage partagé | Storage Spaces Direct |
|---|---|---|
| Stockage | Fourni par une infrastructure commune | Agrégé à partir des disques locaux de plusieurs nœuds |
| Dépendance principale | Baie, chemins de stockage et réseau associé | Nœuds, disques locaux et réseau inter-nœuds |
| Gestion | Dépend du SAN et du cluster | Dépend du cluster et du stockage défini par logiciel |
| Coûts | Dépend de la baie, de la connectivité et du support | Dépend des serveurs, disques, réseaux et exigences de validation |
| Disponibilité | Dépend de la redondance complète du chemin de stockage | Dépend de la résilience des données et de la santé du cluster |
| Déploiement | Nécessite une configuration cohérente du stockage partagé | Nécessite une architecture S2D correctement conçue |

Le choix doit être motivé par les besoins, les compétences disponibles, les coûts, les performances, la résilience et les exigences de support.

### 5.4 Stockage local sans mécanisme de partage ou de réplication

Deux serveurs Hyper-V séparés disposant chacun de leurs propres disques ne forment pas automatiquement un cluster capable de redémarrer leurs VM respectives.

Si une VM doit être transférée vers un autre hôte après une panne, son stockage et sa configuration doivent être accessibles au nœud cible.

Cela peut être obtenu par un stockage partagé compatible, un stockage défini par logiciel ou d'autres mécanismes de déplacement ou de réplication selon le scénario.

Le choix d'un cluster doit donc commencer par une analyse complète du stockage, et non uniquement par l'achat d'un deuxième serveur.

## 6. Dimensionnement d'un cluster Hyper-V

### 6.1 La règle N+1

Un principe de dimensionnement fréquent est la capacité N+1.

Cela signifie que la capacité du parc est suffisante pour supporter la charge prévue après la perte d'un nœud.

Exemple : deux nœuds dont la capacité combinée permet d'héberger les VM en fonctionnement normal, mais dont aucun n'est capable d'assumer seul la charge après une panne, ne satisfont pas un objectif de reprise intégrale sur un seul nœud.

Pour deux nœuds, la situation est particulièrement simple à comprendre :

```text
État normal
HV01 : 10 VM
HV02 : 10 VM

Panne de HV01
HV02 doit être capable de reprendre les VM
de HV01 tout en maintenant les VM déjà présentes.
```

Il faut prévoir la capacité CPU, mémoire, stockage et réseau requise par la charge après basculement.

### 6.2 Calculer la mémoire nécessaire

Supposons que les VM suivantes soient prévues sur un cluster à deux nœuds :

| Groupe | Mémoire attribuée |
|---|---:|
| VM de production critiques | 36 Go |
| VM de production secondaires | 24 Go |
| Services d'infrastructure | 12 Go |
| Total attribué aux VM | 72 Go |

Il faudra ajouter la mémoire nécessaire à Windows Server, Hyper-V, aux processus d'administration et aux marges d'exploitation.

La réserve ne doit pas être choisie arbitrairement. Elle doit être estimée à partir de mesures et de recommandations adaptées au matériel et aux charges de travail.

Si un nœud ne dispose pas de suffisamment de mémoire pour accueillir toutes les VM critiques après une panne, le cluster ne pourra pas garantir le comportement prévu pour ces VM.

### 6.3 Réserve CPU

Le calcul CPU doit considérer la charge réelle et les périodes de pointe.

Une moyenne d'utilisation très faible peut masquer des pics importants.

Il faut examiner :

- Le temps CPU consommé.
- La pression de planification.
- Le nombre de vCPU configurés.
- Les pics de traitement.
- Les dépendances entre applications.
- La capacité disponible après perte d'un nœud.

La surallocation des vCPU n'est pas nécessairement mauvaise, mais elle doit être évaluée en fonction des besoins et des mesures de l'infrastructure.

### 6.4 Dimensionnement du réseau

Une infrastructure de virtualisation utilise plusieurs catégories de trafic :

- Administration.
- Trafic des machines virtuelles.
- Communication interne du cluster.
- Migration à chaud.
- Stockage.
- Réplication.
- Sauvegarde.

Ces flux ne demandent pas tous la même bande passante ni la même latence.

La conception doit définir quels flux sont séparés physiquement, lesquels utilisent des VLAN distincts et quelles garanties de bande passante ou de priorité sont nécessaires.

Des VLAN distincts ne remplacent pas automatiquement toutes les garanties qu'apporterait une séparation physique.

## 7. Préparer les nœuds du cluster

### 7.1 Exemple d'infrastructure de laboratoire

Nous utiliserons les paramètres suivants :

| Élément | Valeur pédagogique |
|---|---|
| Domaine | `ad.lab.test` |
| Nœud 1 | `HV01.ad.lab.test` |
| Nœud 2 | `HV02.ad.lab.test` |
| Nom du cluster | `CL-HV` |
| Adresse du cluster | `192.168.20.50` |
| Réseau d'administration | `192.168.20.0/24` |
| Réseau de stockage | `192.168.30.0/24` |
| Réseau de migration | `192.168.40.0/24` |
| Partage témoin éventuel | `\\FSW01\CL-HV-Witness` |
| Stockage partagé | Volumes CSV selon le laboratoire |

Ces adresses servent uniquement d'exemple. Dans une infrastructure de production, il faut vérifier les routes, la disponibilité des adresses, le DNS, les VLAN et les dépendances réseau.

### 7.2 Exigences générales

Avant de créer le cluster, vérifie :

1. Que les serveurs utilisent des versions de Windows Server compatibles entre elles.
2. Que les pilotes et firmwares sont adaptés.
3. Que les nœuds disposent de la configuration réseau prévue.
4. Que les noms des serveurs sont correctement résolus.
5. Que les comptes et permissions Active Directory sont préparés.
6. Que la configuration du stockage est supportée.
7. Que la connectivité entre les nœuds fonctionne.
8. Que les mises à jour et la configuration de sécurité sont cohérentes.
9. Que les interfaces réseau sont identifiées sans ambiguïté.
10. Que les éventuelles dépendances de virtualisation sont vérifiées.

Un cluster ne doit pas être construit en supposant que deux serveurs de modèles différents sont nécessairement interchangeables.

### 7.3 Vérifier les noms et la connectivité

Sur les deux nœuds :

```powershell
hostname
```

Vérifier la résolution DNS :

```powershell
Resolve-DnsName HV01.ad.lab.test
Resolve-DnsName HV02.ad.lab.test
```

Vérifier l'adresse IP :

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
    Select-Object InterfaceAlias,
                  IPAddress,
                  PrefixLength
```

Inspecter les interfaces :

```powershell
Get-NetAdapter |
    Select-Object Name,
                  InterfaceDescription,
                  Status,
                  LinkSpeed
```

Vérifie également l'absence d'adresses IP en double, la configuration des passerelles et les règles de pare-feu.

Une réponse positive à `ping` ne garantit pas que tous les flux de cluster ou de stockage fonctionnent.

### 7.4 Installer le rôle Hyper-V

Sur chaque serveur qui doit héberger les VM :

```powershell
Install-WindowsFeature `
    -Name Hyper-V `
    -IncludeManagementTools `
    -Restart
```

La commande peut entraîner un redémarrage du serveur. Prévois cette opération pendant la préparation du nœud et non pendant une période où il héberge des charges critiques.

Si la machine doit être gérée à distance, vérifie également les outils disponibles sur le poste d'administration.

### 7.5 Installer Failover Clustering

Sur chaque nœud :

```powershell
Install-WindowsFeature `
    -Name Failover-Clustering `
    -IncludeManagementTools
```

Si un redémarrage est demandé par le système ou par les changements de composants, effectue-le dans le cadre de la fenêtre prévue.

Vérifie le résultat :

```powershell
Get-WindowsFeature `
    -Name Hyper-V,Failover-Clustering
```

Il est aussi possible d'installer les outils d'administration sur une machine de gestion distincte, à condition d'utiliser les composants compatibles avec la version du cluster.

## 8. Valider l'infrastructure avant la création du cluster

### 8.1 Pourquoi la validation est essentielle

La validation détecte de nombreux problèmes de configuration avant que le cluster ne soit utilisé pour héberger des services importants.

Elle peut notamment examiner :

- Le système et les composants des nœuds.
- La configuration réseau.
- Les interfaces et leurs communications.
- Les configurations de stockage.
- Certains aspects matériels et logiciels.
- La compatibilité de l'environnement.

Un cluster qui semble fonctionner pendant un test simple peut échouer lors d'une panne si une dépendance critique n'a jamais été testée.

### 8.2 Lancer la validation avec PowerShell

Sur une machine disposant du module FailoverClusters :

```powershell
Test-Cluster -Node HV01,HV02
```

Dans un environnement avec stockage partagé, réalise la validation selon les recommandations applicables au stockage prévu.

Les tests de stockage doivent être effectués dans un environnement approprié. Certains tests peuvent interagir avec les périphériques de stockage ; il faut donc examiner les prérequis et les conséquences avant d'effectuer des tests sur une infrastructure déjà en production.

### 8.3 Examiner le rapport

Après la validation, ouvre le rapport généré et examine les avertissements et erreurs.

Ne te contente pas de chercher une conclusion globale.

Pour chaque problème :

1. Identifier le test concerné.
2. Comprendre la cause.
3. Vérifier l'impact sur la disponibilité.
4. Corriger le défaut.
5. Relancer les tests pertinents.
6. Archiver le rapport validé.

Les écarts acceptables doivent être justifiés et documentés.

### 8.4 Une configuration supportée est un objectif d'exploitation

Dans une infrastructure critique, l'objectif est de satisfaire les exigences de validation et de support applicables.

Une situation dans laquelle les services fonctionnent malgré un défaut connu n'est pas une preuve que le défaut peut être ignoré.

Il faut traiter les anomalies avant d'accueillir des charges de production.

Documentation : [Valider une configuration de cluster](https://learn.microsoft.com/en-us/windows-server/failover-clustering/create-failover-cluster).

## 9. Créer le cluster Windows Server

### 9.1 Vérifier les permissions Active Directory

Un cluster associé à un domaine utilise un nom d'accès administratif et des objets Active Directory selon le scénario.

Lors de la création, il faut donc s'assurer que les autorisations nécessaires existent pour créer ou utiliser l'objet ordinateur du cluster.

Selon la politique de l'organisation, il peut être nécessaire de précréer le Cluster Name Object ou d'accorder les permissions appropriées au compte qui réalise la création.

Ne donne pas des permissions globales étendues sur l'annuaire uniquement pour contourner un problème de création.

### 9.2 Créer le cluster

La commande suivante illustre une création avec deux nœuds, une adresse IP statique et sans ajout automatique de stockage.

```powershell
New-Cluster `
    -Name "CL-HV" `
    -Node "HV01","HV02" `
    -StaticAddress "192.168.20.50" `
    -NoStorage
```

Cette adresse doit être disponible sur le réseau prévu pour l'accès au cluster.

L'option `-NoStorage` permet de différer l'ajout des disques. Elle ne doit pas être interprétée comme une configuration définitive du stockage des machines virtuelles.

Les paramètres peuvent varier selon le type d'architecture et la stratégie de déploiement choisie.

### 9.3 Vérifier l'état du cluster

```powershell
Get-Cluster
```

Lister les nœuds :

```powershell
Get-ClusterNode
```

Lister les groupes de ressources :

```powershell
Get-ClusterGroup
```

Lister les réseaux :

```powershell
Get-ClusterNetwork
```

La présence du cluster dans la console ne suffit pas. Vérifie que les nœuds sont en ligne et que les ressources attendues sont saines.

### 9.4 Vérifier l'accès au nom du cluster

Le nom du cluster et son adresse doivent se résoudre selon la configuration DNS prévue.

Exemple :

```powershell
Resolve-DnsName CL-HV.ad.lab.test
```

Si la résolution échoue, vérifie notamment :

- L'enregistrement DNS.
- L'objet ordinateur du cluster.
- Les permissions de mise à jour DNS.
- L'adresse et le réseau associés.
- La configuration du client DNS.
- L'état du cluster.

Un problème DNS sur le nom d'accès du cluster peut donner l'impression que le cluster est hors service alors que certains nœuds restent joignables directement.

## 10. Comprendre les rôles et ressources du cluster

### 10.1 Le rôle clusterisé

Le cluster gère des rôles composés de ressources dépendantes.

Un rôle peut regrouper plusieurs ressources, par exemple :

- Une ressource de nom réseau.
- Une adresse IP.
- Un disque.
- Un service.
- Une machine virtuelle.
- Des ressources de dépendance.

Le cluster organise ces ressources en groupes pour assurer leur gestion coordonnée.

### 10.2 Exemple de rôle Hyper-V

```text
Rôle clusterisé : VM-APP01
|
+-- Ressource machine virtuelle
|
+-- Configuration de VM
|
+-- Disques virtuels
|
+-- Dépendances de stockage
|
+-- Connectivité réseau virtuelle
|
+-- Nœud propriétaire courant
```

Le groupe peut être géré par le cluster et transféré à un autre nœud en cas d'incident ou lors d'une opération de maintenance.

### 10.3 Nœud propriétaire

Le nœud propriétaire est le nœud responsable du groupe clusterisé à un instant donné.

Pour examiner les groupes :

```powershell
Get-ClusterGroup |
    Select-Object Name,
                  State,
                  OwnerNode
```

Pour examiner les ressources :

```powershell
Get-ClusterResource |
    Select-Object Name,
                  ResourceType,
                  State,
                  OwnerGroup,
                  OwnerNode
```

Ces informations permettent d'identifier l'emplacement et l'état des rôles.

### 10.4 Dépendances et disponibilité

Une machine virtuelle peut dépendre du stockage, du réseau et des ressources gérées par l'hôte.

Le transfert du rôle vers un autre nœud ne corrige pas automatiquement une panne commune affectant tous les nœuds.

Exemples de points communs problématiques :

- Une baie de stockage unique non redondée.
- Un commutateur réseau unique.
- Un circuit électrique commun.
- Une mauvaise configuration partagée.
- Un service d'annuaire indisponible.
- Un réseau de stockage défaillant.

L'objectif du cluster est donc de réduire les points de défaillance, et non de les déplacer vers une seule dépendance centrale.

## 11. Quorum : le mécanisme qui évite le split-brain

### 11.1 Pourquoi le quorum existe

Le quorum détermine si suffisamment d'éléments du cluster peuvent participer pour que le cluster continue à fonctionner.

Ce mécanisme évite qu'une partition réseau conduise deux groupes de nœuds à considérer simultanément qu'ils peuvent gérer seuls les mêmes rôles et ressources.

Cette situation est généralement désignée sous le terme de **split-brain**.

```text
                 CLUSTER INITIAL
              +--------+--------+
              |                 |
             HV01              HV02
              |                 |
              +--------+--------+
                       |
                  Réseau partagé


             PARTITION RÉSEAU

          HV01                 HV02
            |                    |
      Groupe A              Groupe B
            |                    |
       Aucun accord commun sur le cluster
            |
            v
        RISQUE SPLIT-BRAIN
```

Le quorum permet au cluster de prendre une décision cohérente en fonction de sa configuration de vote.

### 11.2 Les votes

Les nœuds peuvent participer au calcul du quorum avec un vote.

Le témoin de quorum peut également fournir un vote.

Le cluster doit conserver la majorité requise pour rester opérationnel.

Le calcul exact dépend de la configuration de quorum, des votes attribués et des mécanismes dynamiques.

Il ne faut pas appliquer mécaniquement une règle simplifiée sans vérifier la configuration réelle de l'environnement.

### 11.3 Exemple de cluster à deux nœuds

Considérons deux nœuds :

```text
HV01 : 1 vote
HV02 : 1 vote

Total : 2 votes
```

Sans témoin, la perte d'un nœud peut empêcher le cluster de conserver une majorité selon la configuration de quorum et les conditions du scénario.

Avec un témoin :

```text
HV01 : 1 vote
HV02 : 1 vote
Témoin : 1 vote

Total : 3 votes
```

La combinaison des nœuds actifs et du témoin peut permettre de maintenir le quorum après certaines pannes.

Un témoin n'est toutefois pas une garantie qu'une architecture survivra à toutes les combinaisons de panne.

### 11.4 Les types de témoins

Les types de témoins courants comprennent :

**Témoin disque**

Il utilise un disque dédié accessible selon l'architecture du cluster.

**Témoin de partage de fichiers**

Il utilise un partage SMB accessible par les nœuds concernés.

**Témoin cloud**

Il utilise un service cloud pris en charge, par exemple un service de stockage adapté.

Le choix doit correspondre à l'architecture du cluster, à sa connectivité et à ses objectifs.

### 11.5 Pourquoi un partage témoin doit être indépendant

Un témoin ne doit pas dépendre exactement du même ensemble de ressources susceptibles de tomber en panne que le cluster qu'il aide à arbitrer.

Par exemple, placer le partage témoin sur un rôle de fichiers hébergé par le cluster lui-même peut introduire une dépendance circulaire.

Pour un témoin de partage de fichiers, utilise un emplacement adapté, disponible de manière indépendante du cluster concerné.

Pour les déploiements réels, vérifie les recommandations Microsoft relatives au type de cluster et au témoin choisi.

### 11.6 Exemple de configuration d'un témoin de partage

Le partage `\\FSW01\CL-HV-Witness` est supposé déjà créé avec les permissions nécessaires pour le cluster.

La commande suivante illustre la configuration :

```powershell
Set-ClusterQuorum `
    -FileShareWitness "\\FSW01\CL-HV-Witness"
```

Après la modification, contrôle la configuration :

```powershell
Get-ClusterQuorum
```

Il faut aussi vérifier l'accès du cluster au partage, la résolution DNS du serveur de fichiers et les permissions requises.

### 11.7 Observer les votes et l'état du quorum

```powershell
Get-ClusterNode |
    Select-Object Name,
                  State,
                  NodeWeight,
                  DynamicWeight
```

Les votes dynamiques peuvent être ajustés automatiquement selon la configuration du cluster et les circonstances.

Ne change pas manuellement les poids sans raison précise et sans comprendre l'ensemble des conséquences.

Le quorum doit être réévalué lorsque l'architecture évolue, notamment lors de l'ajout ou du retrait de nœuds, de changements du stockage ou d'une reprise après sinistre multisite.

### 11.8 Quorum et maintenance

Une opération de maintenance peut modifier les conditions de vote disponibles.

Avant d'arrêter un nœud :

1. Vérifier l'état général du cluster.
2. Vérifier le quorum.
3. Vérifier le témoin.
4. Vérifier l'état des autres nœuds.
5. Transférer ou vider les rôles concernés.
6. Contrôler que la capacité restante est suffisante.
7. Effectuer la maintenance.
8. Réintégrer le nœud.
9. Contrôler la santé du cluster.

Il faut éviter de redémarrer successivement plusieurs nœuds sans avoir validé les conditions de quorum et la reprise opérationnelle de chacun.

Documentation : [Quorum et témoin d'un cluster de basculement](https://learn.microsoft.com/en-us/windows-server/failover-clustering/what-is-quorum-witness).

## 12. Réseaux du cluster

### 12.1 Les principaux flux réseau

Une infrastructure Hyper-V de haute disponibilité peut utiliser différents réseaux ou segments logiques.

```text
HV01                                      HV02
|
+-- Réseau d'administration --------------+
|
+-- Réseau des VM ------------------------+
|
+-- Réseau de cluster -------------------+
|
+-- Réseau de migration à chaud ---------+
|
+-- Réseau de stockage ------------------+
|
+-- Réseau de réplication ----------------+
```

Ces réseaux peuvent être séparés physiquement, par VLAN ou par d'autres mécanismes réseau adaptés.

La séparation doit être conçue en fonction de la sécurité, de la bande passante, de la résilience et de la facilité d'exploitation.

### 12.2 Réseau d'administration

Ce réseau permet aux administrateurs de se connecter aux hôtes et d'effectuer les opérations de gestion.

Il doit être protégé, surveillé et accessible uniquement selon les règles d'administration prévues.

Évite d'exposer les interfaces de gestion sur des réseaux non fiables.

### 12.3 Réseau des machines virtuelles

Le trafic des VM passe par les commutateurs virtuels et les cartes réseau physiques utilisées par Hyper-V.

Il doit être dimensionné pour les communications des applications hébergées.

Un trafic important de sauvegarde, de réplication ou de migration peut affecter les performances des applications s'il utilise la même capacité physique sans contrôle adéquat.

### 12.4 Réseau de communication du cluster

Les nœuds échangent des informations nécessaires au fonctionnement du cluster.

Un problème de communication peut entraîner la perte d'un membre, des basculements ou une dégradation de la disponibilité.

Le réseau de communication interne doit être fiable et correctement surveillé.

### 12.5 Réseau de migration

La migration à chaud peut transférer une quantité importante de mémoire et d'état d'une VM.

Si une migration consomme la totalité de la bande passante du réseau de production, les applications peuvent subir une dégradation.

Selon l'architecture, le trafic de migration peut être isolé ou soumis à des règles de priorité adaptées.

### 12.6 Réseau de stockage

Pour un stockage réseau, la latence et la fiabilité de la connectivité sont particulièrement importantes.

Les connexions de stockage doivent respecter les recommandations du fournisseur et de la technologie retenue.

Une perte du réseau de stockage peut affecter l'accès aux disques virtuels, même si les serveurs Hyper-V restent en fonctionnement.

### 12.7 Examiner les réseaux du cluster

```powershell
Get-ClusterNetwork |
    Select-Object Name,
                  Address,
                  AddressMask,
                  Role,
                  Metric,
                  State
```

Cette inspection permet d'examiner les réseaux connus du cluster et leur configuration.

Pour modifier le rôle d'un réseau, il faut comprendre précisément les flux qui doivent l'utiliser.

Exemple de configuration d'un réseau destiné uniquement aux communications internes du cluster :

```powershell
Set-ClusterNetwork `
    -Name "Cluster Network 2" `
    -Role ClusterOnly
```

Le nom dans cet exemple doit être remplacé par celui du réseau concerné.

Ne transforme pas un réseau en réseau privé de cluster avant d'avoir vérifié qu'aucun trafic client ou autre flux nécessaire ne doit l'emprunter.

### 12.8 Redondance réseau

Deux interfaces réseau ne constituent pas nécessairement deux chemins indépendants.

Si elles sont connectées au même commutateur, à la même alimentation ou à la même infrastructure physique, une panne commune peut les affecter simultanément.

La redondance doit être analysée de bout en bout.

Exemples :

- Deux interfaces vers deux commutateurs indépendants.
- Deux chemins de stockage.
- Des alimentations redondantes.
- Des circuits électriques différents.
- Une séparation des infrastructures critiques selon les recommandations du fournisseur.

La topologie exacte dépend de la plateforme et de ses objectifs de disponibilité.

## 13. Préparer le stockage partagé et les volumes CSV

### 13.1 Principe du stockage partagé

Dans une architecture à stockage partagé, plusieurs nœuds Hyper-V peuvent avoir besoin d'accéder aux mêmes fichiers de configuration ou de disques virtuels.

Le cluster doit organiser cet accès de manière cohérente.

Un disque partagé ne doit pas être utilisé simultanément par plusieurs nœuds en dehors du mécanisme de gestion et de coordination prévu.

### 13.2 Cluster Shared Volumes

Les **Cluster Shared Volumes**, ou CSV, permettent à plusieurs nœuds d'un cluster d'accéder simultanément à un même volume compatible.

Ils sont notamment utilisés pour les machines virtuelles Hyper-V hautement disponibles.

Le chemin typique dans un cluster est de la forme :

`C:\ClusterStorage\Volume1`

Exemple :

```text
Stockage partagé
       |
       v
Volume de cluster
       |
       v
Cluster Shared Volume
       |
       +-- VM-APP01
       |    +-- APP01-OS.vhdx
       |    +-- APP01-DATA.vhdx
       |
       +-- VM-DB01
            +-- DB01-OS.vhdx
            +-- DB01-DATA.vhdx
```

Le chemin est un exemple ; les volumes réellement disponibles dépendent de l'architecture et de la configuration.

### 13.3 Pourquoi les CSV sont utiles

Les CSV facilitent l'hébergement de nombreuses machines virtuelles sur le stockage du cluster et simplifient certains déplacements entre nœuds.

Ils ne rendent pas le stockage invulnérable : ils dépendent toujours de l'architecture de stockage, de ses contrôleurs, de ses chemins et de sa résilience.

### 13.4 Ajouter un disque au cluster

Le disque doit avoir été préparé selon les recommandations de la solution de stockage.

Avant de l'ajouter, vérifie :

- Qu'il s'agit bien du disque prévu.
- Qu'il ne contient pas de données à conserver.
- Qu'il est accessible par les nœuds concernés.
- Que le stockage et les chemins sont conformes à l'architecture.
- Que les tests requis ont été réalisés.
- Que le système de fichiers et le type de disque sont adaptés.

Dans l'environnement du cluster, examiner les disques disponibles :

```powershell
Get-ClusterAvailableDisk
```

Lorsque les prérequis sont satisfaits, un disque disponible peut être ajouté au cluster :

```powershell
Get-ClusterAvailableDisk |
    Add-ClusterDisk
```

Cette commande doit être utilisée uniquement après vérification du disque concerné. Ne lance jamais une opération d'ajout ou d'initialisation de manière aveugle sur une infrastructure de stockage contenant des données.

### 13.5 Ajouter un disque en tant que CSV

Lister les ressources de disque :

```powershell
Get-ClusterResource |
    Where-Object {
        $_.ResourceType -eq "Physical Disk"
    } |
    Select-Object Name, State, OwnerGroup
```

Après avoir identifié le nom exact de la ressource et vérifié qu'elle convient :

```powershell
Add-ClusterSharedVolume `
    -Name "Cluster Disk 1"
```

Le nom `Cluster Disk 1` est fictif : utilise le nom réel affiché par le cluster.

Vérifier les CSV :

```powershell
Get-ClusterSharedVolume
```

Vérifier également que le chemin attendu existe et que les VM peuvent y accéder.

### 13.6 Multipath I/O

Dans certaines architectures de stockage, Multipath I/O (MPIO) permet de gérer plusieurs chemins vers une ressource de stockage.

Cela peut améliorer la résilience des chemins et, selon le système, participer à l'équilibrage ou à la continuité des accès.

MPIO doit être configuré conformément aux recommandations du fournisseur de stockage. Une configuration incohérente peut au contraire provoquer des pertes d'accès ou des erreurs.

Ne suppose pas que l'installation du composant MPIO suffit : les pilotes, les politiques et les chemins réels doivent être validés.

### 13.7 Stockage partagé et sauvegarde

Un CSV n'est pas une sauvegarde.

Il permet au cluster d'accéder aux données selon son architecture, mais une panne de stockage grave, une corruption logique, une suppression accidentelle ou une attaque peut affecter les données partagées.

La sauvegarde doit donc disposer d'un mécanisme indépendant, d'une politique de rétention et d'une procédure de restauration testée.

Documentation : [Gérer les Cluster Shared Volumes](https://learn.microsoft.com/en-us/windows-server/failover-clustering/failover-cluster-manage-cluster-shared-volumes).

## 14. Storage Spaces Direct

### 14.1 Objectif de S2D

Storage Spaces Direct (S2D) est une fonctionnalité de stockage défini par logiciel qui permet d'utiliser les disques internes de plusieurs serveurs pour construire un stockage résilient.

Au lieu de dépendre nécessairement d'une baie de stockage externe, les serveurs contribuent leurs ressources locales à un pool de stockage.

### 14.2 Architecture conceptuelle

```text
                CLUSTER S2D
                    |
         +----------+----------+
         |                     |
         v                     v
    +-----------+         +-----------+
    |   HV01    |         |   HV02    |
    |           |         |           |
    | Disques A |         | Disques B |
    | Disques B |         | Disques C |
    +-----------+         +-----------+
         |                     |
         +----------+----------+
                    |
          Réseau inter-nœuds
                    |
                    v
           Pool de stockage
                    |
                    v
          Volumes résilients
                    |
                    v
              Machines VM
```

Le schéma simplifie le fonctionnement réel. Les capacités de résilience, la disposition des données et le nombre de défaillances supportées dépendent de la configuration prise en charge.

### 14.3 Différence avec un SAN

Dans un cluster traditionnel à stockage partagé, les disques des VM sont fournis par une infrastructure externe commune.

Avec S2D, les disques locaux des nœuds font partie de la solution de stockage distribué.

Cette différence affecte :

- Le matériel requis.
- Les réseaux inter-nœuds.
- La résilience des données.
- Le modèle de maintenance.
- Les opérations de remplacement des disques.
- Les procédures de réparation.
- La surveillance de la capacité et de la santé.

### 14.4 Pourquoi S2D exige une conception précise

Un simple pool de disques n'est pas équivalent à une architecture S2D correctement conçue et validée.

Il faut respecter les exigences de matériels, de réseaux, de disques, de pilotes et de configurations prises en charge.

Il ne faut pas transformer à la légère des disques utilisés par des VM en disques d'un pool S2D. Une opération mal préparée peut entraîner une perte de données.

### 14.5 Cas d'utilisation

S2D peut être pertinent pour :

- Une plateforme hyperconvergée.
- Un environnement de virtualisation utilisant des disques locaux dans plusieurs nœuds.
- Une architecture de stockage définie par logiciel compatible avec les objectifs de performance et de disponibilité.

La conception d'un cluster S2D de production doit suivre le guide de déploiement correspondant à la version de Windows Server et au matériel choisi.

Documentation : [Vue d'ensemble de Storage Spaces Direct](https://learn.microsoft.com/en-us/windows-server/storage/storage-spaces/storage-spaces-direct-overview).

## 15. Réseau virtuel Hyper-V

### 15.1 Le commutateur virtuel

Le commutateur virtuel Hyper-V relie les interfaces réseau des machines virtuelles à des réseaux virtuels ou physiques selon sa configuration.

Il peut être de type :

- **Externe** : relie les VM à un réseau externe via une carte physique.
- **Interne** : permet la communication entre les VM et l'hôte.
- **Privé** : permet la communication entre les VM du commutateur sans connectivité directe à l'hôte via ce commutateur.

Le choix dépend du besoin fonctionnel et du modèle de sécurité.

### 15.2 Créer un commutateur externe

Exemple simple sur un hôte de laboratoire disposant d'une carte réseau appelée `NIC-Prod` :

```powershell
New-VMSwitch `
    -Name "vSwitch-Production" `
    -NetAdapterName "NIC-Prod" `
    -AllowManagementOS $true
```

Le nom de la carte doit être adapté au système.

La création peut modifier la configuration réseau de l'hôte, notamment lorsqu'une carte est utilisée pour le trafic de gestion. Il faut donc préparer l'opération, connaître la connectivité disponible et prévoir un accès de secours avant de modifier une interface de production.

### 15.3 Utiliser des VLAN

Les VLAN permettent de séparer logiquement différents domaines de diffusion.

Exemple :

```text
vSwitch-Production
|
+-- VM-WEB01 : VLAN 110
|
+-- VM-APP01 : VLAN 120
|
+-- VM-DB01  : VLAN 130
```

Exemple de configuration d'une interface virtuelle en mode Access :

```powershell
Set-VMNetworkAdapterVlan `
    -VMName "VM-WEB01" `
    -Access `
    -VlanId 110
```

La configuration VLAN doit correspondre à celle des commutateurs physiques et aux exigences réseau.

Une erreur d'association du VLAN peut rendre une machine inaccessible même si son système et sa carte virtuelle fonctionnent correctement.

### 15.4 Répéter les configurations nécessaires sur les nœuds

Pour qu'une machine virtuelle puisse être déplacée entre les nœuds sans perdre son accès réseau, les commutateurs virtuels et les réseaux nécessaires doivent exister de manière cohérente sur les hôtes concernés.

```text
HV01                       HV02
|
+-- vSwitch-Production     +-- vSwitch-Production
|
+-- VLAN 110               +-- VLAN 110
|
+-- VLAN 120               +-- VLAN 120
|
+-- VLAN 130               +-- VLAN 130
```

Les configurations exactes doivent correspondre aux besoins des VM et au réseau physique.

Vérifie les noms des commutateurs, les VLAN, les interfaces physiques et les règles de sécurité avant d'autoriser une migration.

### 15.5 Switch Embedded Teaming

Switch Embedded Teaming (SET) est une technologie qui permet de combiner plusieurs cartes réseau dans un commutateur virtuel Hyper-V compatible.

Elle peut participer à la résilience réseau et à la gestion de la bande passante selon la conception retenue.

Exemple de principe :

```text
             vSwitch-External
                    |
          +---------+---------+
          |                   |
         NIC1                NIC2
          |                   |
          +---------+---------+
                    |
             Réseau physique
```

La configuration réelle doit respecter les exigences de SET, des adaptateurs réseau et des commutateurs physiques.

Exemple PowerShell illustratif :

```powershell
New-VMSwitch `
    -Name "vSwitch-External" `
    -NetAdapterName "NIC1","NIC2" `
    -EnableEmbeddedTeaming $true `
    -AllowManagementOS $true
```

Ne lance pas cette commande sans vérifier les noms des cartes, leur état, le câblage, les VLAN et les conditions de prise en charge. Dans certains environnements, la création du commutateur nécessite une préparation ou une interruption réseau planifiée.

### 15.6 Vérifier les commutateurs

```powershell
Get-VMSwitch
```

Examiner les interfaces virtuelles de gestion :

```powershell
Get-VMNetworkAdapter -ManagementOS
```

Pour une VM :

```powershell
Get-VMNetworkAdapter -VMName "VM-WEB01"
```

Il faut vérifier le commutateur associé, les VLAN, la connectivité réelle et la cohérence entre les hôtes.

## 16. Créer une machine virtuelle destinée au cluster

### 16.1 Préparer l'emplacement

Dans un cluster à stockage partagé, une VM hautement disponible doit utiliser un emplacement de stockage accessible conformément au modèle du cluster.

Exemple de chemin :

`C:\ClusterStorage\Volume1\VM-APP01`

Ce chemin doit exister sur le nœud et correspondre à un volume correctement ajouté au cluster.

Avant de créer la VM, vérifie l'espace libre et les permissions, ainsi que la présence des commutateurs nécessaires.

### 16.2 Créer la VM avec PowerShell

Exemple de création d'une VM de génération 2 dans un laboratoire :

```powershell
$nomVM = "VM-APP01"
$cheminVM = "C:\ClusterStorage\Volume1\VM-APP01"
$cheminVHDX = Join-Path $cheminVM "APP01-OS.vhdx"

New-Item `
    -Path $cheminVM `
    -ItemType Directory `
    -Force | Out-Null

New-VM `
    -Name $nomVM `
    -Generation 2 `
    -MemoryStartupBytes 8GB `
    -NewVHDPath $cheminVHDX `
    -NewVHDSizeBytes 100GB `
    -Path $cheminVM `
    -SwitchName "vSwitch-Production"
```

Cette configuration est un exemple. Elle suppose que le chemin de stockage est adapté, que le commutateur existe et que la VM est destinée à un système d'exploitation compatible.

Un disque virtuel de 100 Go ne signifie pas nécessairement que 100 Go seront immédiatement consommés physiquement si le format utilise une expansion dynamique.

### 16.3 Vérifier la configuration

```powershell
Get-VM -Name "VM-APP01"
```

Contrôler le disque :

```powershell
Get-VMHardDiskDrive -VMName "VM-APP01"
```

Contrôler l'interface réseau :

```powershell
Get-VMNetworkAdapter -VMName "VM-APP01"
```

Avant d'ajouter la VM au cluster, vérifie sa configuration et démarre-la dans un contexte de test pour confirmer que le système invité fonctionne.

### 16.4 Ajouter une VM comme rôle hautement disponible

Dans un cluster Hyper-V, une VM compatible peut être ajoutée comme rôle de machine virtuelle clusterisée.

Exemple :

```powershell
Add-ClusterVirtualMachineRole `
    -VirtualMachine "VM-APP01"
```

La commande doit être exécutée depuis un environnement où le cluster et la VM sont correctement configurés, avec les permissions nécessaires.

Après l'ajout, vérifie le rôle :

```powershell
Get-ClusterGroup |
    Where-Object {
        $_.Name -like "*APP01*"
    } |
    Select-Object Name, State, OwnerNode
```

Le nom exact du groupe dépend de la configuration et de la manière dont le rôle a été créé.

Une VM qui fonctionne sur un seul hôte n'est pas automatiquement hautement disponible : il faut vérifier qu'elle est effectivement gérée par le cluster et que ses dépendances sont satisfaites.

## 17. Migration à chaud Hyper-V

### 17.1 Qu'est-ce que la migration à chaud ?

La migration à chaud, ou *Live Migration*, permet de déplacer une machine virtuelle en fonctionnement d'un hôte Hyper-V vers un autre sans interruption normalement perceptible.

Elle est utile pour :

- Mettre un hôte en maintenance.
- Rééquilibrer les charges.
- Retirer temporairement un serveur du service.
- Préparer une mise à jour.
- Réorganiser les ressources du cluster.

Elle est différente du basculement après une panne brutale.

### 17.2 Principe de fonctionnement

```text
AVANT LA MIGRATION

HV01                         HV02
|
+-- VM-APP01 : active       +-- VM-APP01 absente
|
+-- Mémoire VM
+-- État d'exécution


PENDANT LA MIGRATION

HV01                         HV02
|
+-- État mémoire ---------> +-- État en préparation
+-- Données transférées --> +-- Ressources préparées
|
+-- VM toujours active selon la phase


APRÈS LA MIGRATION

HV01                         HV02
|
+-- VM-APP01 absente       +-- VM-APP01 active
|
                            +-- Exécution sur HV02
```

Le mécanisme exact dépend des paramètres de migration, des ressources utilisées et du scénario.

### 17.3 Deux scénarios courants

**Migration avec stockage partagé**

Les fichiers des VM sont déjà sur un stockage accessible depuis les hôtes source et destination. La migration peut se concentrer sur l'état d'exécution de la VM, sous réserve des autres conditions.

**Migration avec déplacement du stockage**

Les fichiers et données nécessaires sont également déplacés ou copiés vers une destination adaptée.

Cela peut demander davantage de bande passante et de temps, selon la taille des disques et la charge d'E/S.

### 17.4 Configurer l'authentification

La migration à chaud doit utiliser une méthode d'authentification appropriée.

Deux mécanismes courants sont :

- CredSSP.
- Kerberos avec délégation contrainte correctement configurée.

CredSSP dépend notamment du contexte d'authentification utilisé pour lancer l'opération.

Kerberos permet de construire un scénario d'administration plus adapté à certains environnements distants, mais demande une configuration rigoureuse de la délégation.

**Point important pour Windows Server 2025 :** Credential Guard est activé par défaut dans certains scénarios de serveurs membres joints au domaine. Les migrations fondées sur CredSSP peuvent alors échouer après une mise à niveau. Il est donc essentiel de vérifier les recommandations relatives à la version installée et de privilégier une configuration Kerberos avec délégation contrainte correctement préparée lorsque le scénario l'exige.

### 17.5 Configuration Hyper-V pour Kerberos

Sur les hôtes Hyper-V, l'activation de la migration et le choix du protocole peuvent être réalisés à partir des paramètres Hyper-V ou de PowerShell, selon le scénario.

Exemple de configuration :

```powershell
Set-VMHost `
    -VirtualMachineMigrationEnabled $true `
    -VirtualMachineMigrationAuthenticationType Kerberos
```

Cette commande ne configure pas à elle seule toute la délégation Active Directory nécessaire au scénario Kerberos.

La délégation contrainte doit être configurée sur les comptes ordinateurs concernés, avec les services nécessaires et les destinations appropriées.

Limite le périmètre de la délégation aux hôtes et services requis par l'architecture. Ne configure pas une délégation illimitée simplement pour résoudre une erreur d'authentification.

### 17.6 Paramètres avancés de migration

Les paramètres de migration permettent notamment de choisir des réseaux, des options de performance et des mécanismes de transfert.

Selon la version et le scénario, les options de performance peuvent inclure des mécanismes de compression, de transfert TCP/IP ou des mécanismes SMB.

Le choix doit prendre en compte :

- La capacité des cartes réseau.
- La latence.
- L'utilisation du CPU.
- La taille des VM.
- Le nombre de migrations simultanées.
- L'utilisation du réseau de production.
- Les besoins de sécurité.

Il faut mesurer le résultat dans l'environnement réel plutôt que retenir un paramètre présenté comme optimal dans tous les cas.

### 17.7 Sécuriser le réseau de migration

Le trafic de migration doit être protégé par une conception réseau appropriée.

Utilise des réseaux privés ou des mécanismes de séparation de confiance adaptés, et limite l'accès aux hôtes autorisés.

Ne laisse pas circuler le trafic de migration sur un réseau non fiable sans avoir évalué et traité les risques.

### 17.8 Vérifier les migrations

Avant une migration planifiée :

1. Vérifier la santé du cluster.
2. Vérifier l'état de la VM.
3. Vérifier le stockage.
4. Vérifier les commutateurs virtuels.
5. Vérifier les permissions et l'authentification.
6. Vérifier le réseau de migration.
7. Vérifier la capacité du nœud de destination.
8. Réaliser une migration pilote.
9. Contrôler la connectivité applicative.
10. Contrôler les journaux.

Documentation : [Vue d'ensemble de la migration à chaud](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/manage/live-migration-overview).

## 18. Tester le basculement du cluster

### 18.1 Un cluster doit être testé

La présence du cluster ne prouve pas qu'il peut gérer tous les incidents prévus.

Il faut tester différents scénarios :

- Migration volontaire d'un rôle.
- Drainage d'un nœud.
- Redémarrage contrôlé.
- Perte d'une interface réseau.
- Indisponibilité d'une ressource, selon un plan de test adapté.
- Reprise d'un nœud après maintenance.

Les scénarios de perte brutale doivent être testés dans un environnement de laboratoire ou selon une procédure de changement approuvée.

Il ne faut pas couper arbitrairement un serveur de production pour vérifier que le cluster fonctionne.

### 18.2 Transférer un rôle vers un autre nœud

Exemple :

```powershell
Move-ClusterGroup `
    -Name "VM-APP01" `
    -Node "HV02"
```

Le nom du groupe doit correspondre au nom réel utilisé par le cluster.

Avant d'exécuter cette commande, vérifie que le nœud de destination peut accueillir le rôle et que l'opération correspond au comportement attendu.

### 18.3 Vérifier l'état après la migration

```powershell
Get-ClusterGroup |
    Select-Object Name,
                  State,
                  OwnerNode
```

Puis, depuis les outils Hyper-V, vérifie :

- L'état de la VM.
- La connectivité réseau.
- L'accès aux données.
- La santé des applications.
- Les journaux pertinents.
- La durée d'interruption éventuellement observée.

Un changement de nœud propriétaire est un élément de preuve technique, mais il ne garantit pas à lui seul que toutes les applications fonctionnent correctement.

### 18.4 Vérifier les scénarios de panne

Une fois le déplacement planifié testé, le laboratoire peut servir à simuler une panne d'un nœud.

Le test doit examiner :

- La détection de la panne.
- L'état du quorum.
- La disponibilité du stockage.
- Le délai avant la reprise.
- Le démarrage de la VM.
- Le fonctionnement de l'application.
- Le comportement du nœud lorsque le problème est corrigé.

Documente le résultat observé, notamment si le RTO cible n'est pas atteint.

### 18.5 Le nœud de destination doit disposer de suffisamment de ressources

Il ne faut pas considérer le basculement comme acquis si le nœud restant est déjà saturé.

Le cluster peut être en bonne santé tout en rencontrant une pression CPU, mémoire, réseau ou stockage qui rend les applications très lentes après un basculement.

La capacité de réserve est un critère de conception, pas seulement une métrique de supervision.

## 19. Maintenance des clusters

### 19.1 Pourquoi la maintenance doit être coordonnée

La maintenance de chaque nœud peut nécessiter :

- Des mises à jour Windows.
- Un redémarrage.
- Des mises à jour de pilotes.
- Des mises à jour de firmware.
- Le remplacement d'un composant.
- Une modification de réseau.
- Une intervention sur le stockage.

Dans un environnement hautement disponible, les opérations doivent être coordonnées pour préserver les services.

### 19.2 Drainage d'un nœud

Avant d'effectuer une maintenance, les rôles doivent être déplacés selon la stratégie retenue et les capacités restantes.

Le principe consiste à retirer temporairement le nœud de la charge active, effectuer la maintenance, puis le réintégrer.

```text
ÉTAT INITIAL

HV01 : VM-A, VM-B
HV02 : VM-C, VM-D


DRAINAGE DE HV01

HV01 : aucune charge clusterisée prévue
HV02 : VM-A, VM-B, VM-C, VM-D


MAINTENANCE

HV01 : mises à jour et redémarrage
HV02 : charge restante


APRÈS VALIDATION

HV01 : réintégré
HV02 : équilibre restauré selon la politique
```

Ce schéma est volontairement simplifié. Le déplacement des VM dépend de la charge, du stockage, du réseau et des politiques du cluster.

### 19.3 Cluster-Aware Updating

Cluster-Aware Updating (CAU) automatise certaines opérations de mise à jour des nœuds en coordonnant le déplacement des rôles, la mise à jour et les redémarrages.

Il peut fonctionner dans un mode dans lequel le cluster s'actualise lui-même ou dans un mode piloté depuis un ordinateur de gestion extérieur au cluster.

Le mécanisme peut notamment :

1. Placer un nœud dans un état de maintenance.
2. Déplacer les rôles clusterisés concernés.
3. Installer les mises à jour.
4. Redémarrer si nécessaire.
5. Réintégrer le nœud.
6. Continuer avec les autres nœuds selon le profil prévu.

Cette automatisation réduit les opérations manuelles, mais elle ne supprime pas la nécessité de vérifier la capacité, le quorum et la santé de la plateforme.

### 19.4 Installer et préparer CAU

La fonctionnalité de cluster est liée aux composants Failover Clustering et aux outils d'administration.

Avant de configurer CAU :

- Vérifie que le cluster est sain.
- Vérifie le quorum.
- Vérifie que les nœuds sont compatibles et correctement préparés.
- Vérifie les prérequis du mode d'exécution.
- Examine les mises à jour qui doivent être installées.
- Teste la procédure sur un environnement pilote.

CAU doit être configuré avec les droits et les composants nécessaires.

Documentation : [Vue d'ensemble de Cluster-Aware Updating](https://learn.microsoft.com/en-us/windows-server/failover-clustering/cluster-aware-updating).

### 19.5 Maintenance et capacité restante

Si un nœud est en maintenance, les ressources disponibles diminuent.

Avant de le retirer de la charge, vérifie que les nœuds restants peuvent absorber les rôles concernés sans compromettre les performances ni les exigences de disponibilité.

Il faut aussi vérifier le quorum et le statut du témoin, car une maintenance peut réduire le nombre de votes actifs.

Ne lance pas simultanément la maintenance de plusieurs nœuds sans un plan explicitement adapté à cette situation.

## 20. Hyper-V Replica et reprise après sinistre

### 20.1 Le problème du site principal

Un cluster local peut résister à la panne d'un serveur, mais il ne suffit pas nécessairement à résister à la perte complète du site.

Exemples :

- Incendie ou inondation.
- Coupure électrique prolongée.
- Perte d'accès au bâtiment.
- Panne commune de l'infrastructure de stockage.
- Incident réseau affectant tous les nœuds.
- Cyberattaque compromettant l'environnement local.

Pour ces risques, il faut prévoir une stratégie de reprise après sinistre.

### 20.2 Principe de Hyper-V Replica

Hyper-V Replica permet de maintenir une copie de machines virtuelles sur un hôte ou un cluster de réplication distinct.

La réplication est asynchrone : les changements sont transférés vers la cible selon le mécanisme et la fréquence configurés.

Le site secondaire ne fonctionne pas automatiquement comme une copie active de toutes les VM. La procédure de basculement doit être préparée et exécutée selon le scénario.

```text
               SITE PRINCIPAL
        +--------------------------+
        | Cluster Hyper-V          |
        | CL-HV                    |
        |                          |
        | VM-APP01                 |
        | VM-DB01                  |
        +-------------+------------+
                      |
                      | Réplication
                      v
               SITE SECONDAIRE
        +--------------------------+
        | Hôte ou cluster de       |
        | réplication              |
        |                          |
        | Copie de VM-APP01        |
        | Copie de VM-DB01         |
        +--------------------------+
```

Le réseau, l'espace de stockage, l'identité des machines, les dépendances applicatives et les procédures de démarrage doivent être préparés sur le site secondaire.

### 20.3 Différences entre WSFC et Replica

| Fonction | Cluster Hyper-V | Hyper-V Replica |
|---|---|---|
| Risque principalement traité | Défaillance d'un nœud local | Perte d'un hôte ou d'un site selon l'architecture |
| Mécanisme | Basculement du rôle clusterisé | Réplication de VM vers une cible |
| Stockage | Généralement accessible par les nœuds du cluster selon le modèle retenu | Copie répliquée sur l'emplacement cible |
| Basculement après panne | Peut être automatique selon le rôle et l'incident | Le basculement de reprise doit suivre le scénario préparé |
| RPO | Peut être très faible lorsque les données restent sur le stockage commun, sous réserve de la cohérence de l'application | Dépend de l'avancement de la réplication et des points de récupération |
| Sauvegarde | N'en tient pas lieu | N'en tient pas lieu |

Ces mécanismes peuvent être complémentaires.

### 20.4 Préparer le serveur de réplication

Sur le site cible, il faut configurer Hyper-V Replica selon les conditions du scénario :

- Hôte Hyper-V ou cluster pris en charge.
- Emplacement de stockage pour les copies.
- Authentification et ports autorisés.
- Certificats si le mode choisi les exige.
- Règles de pare-feu.
- Contrôle des sources autorisées.
- Permissions et connectivité.
- Capacité nécessaire pour les VM répliquées.

Pour un environnement de production, le mode d'authentification, la gestion des certificats et les ports doivent être choisis selon la sécurité et l'architecture.

### 20.5 Configurer la réplication d'une VM

La procédure générale consiste à :

1. Activer la réception de réplication sur l'hôte ou le cluster cible.
2. Configurer les méthodes d'authentification.
3. Autoriser les serveurs sources requis.
4. Vérifier le stockage de destination.
5. Activer la réplication de la VM source.
6. Choisir la fréquence disponible et adaptée.
7. Examiner l'état initial de la réplication.
8. Contrôler les erreurs et le décalage.
9. Définir les procédures de basculement.
10. Tester la restauration dans un environnement approprié.

Les fréquences et les options disponibles dépendent de la version et de la configuration. Elles ne doivent pas être confondues avec la garantie d'un RPO fixe.

Documentation : [Vue d'ensemble de Hyper-V Replica](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/replication-overview).

### 20.6 Prévoir l'adressage IP et les dépendances

Une VM qui démarre sur le site secondaire peut ne pas être immédiatement accessible.

Il faut examiner :

- L'adressage IP.
- Les VLAN.
- Le DNS.
- Les passerelles.
- Les règles de pare-feu.
- Les dépendances avec les bases de données.
- Les identités et comptes de service.
- Les noms des services.
- Les configurations applicatives.
- Les routes entre les réseaux.

Le démarrage d'une VM n'équivaudra à un rétablissement du service que lorsque les dépendances nécessaires fonctionneront.

### 20.7 Tester la reprise après sinistre

Un plan de reprise doit définir :

- Qui déclare le sinistre.
- Quand le basculement est autorisé.
- Quelles VM démarrer et dans quel ordre.
- Comment vérifier la cohérence des données.
- Comment publier les services.
- Comment prévenir les utilisateurs.
- Comment surveiller le site de secours.
- Comment revenir au site principal lorsque c'est possible.

La procédure doit être testée périodiquement. Il faut vérifier le RTO, le RPO observé et les difficultés rencontrées.

## 21. Sauvegarde et points de contrôle Hyper-V

### 21.1 Un point de contrôle n'est pas une sauvegarde

Les points de contrôle Hyper-V, appelés *checkpoints*, permettent de revenir à un état antérieur de la machine virtuelle dans certains scénarios.

Ils peuvent être utiles avant une modification importante dans un environnement de test.

Cependant, ils ne remplacent pas une sauvegarde indépendante.

Un point de contrôle conserve des dépendances avec les fichiers de la VM et peut continuer à consommer de l'espace. Une corruption ou la perte du stockage peut affecter à la fois la machine et ses points de contrôle.

### 21.2 Points de contrôle standard et de production

Les points de contrôle standards incluent l'état mémoire de la VM au moment où ils sont créés.

Les points de contrôle de production utilisent les mécanismes de sauvegarde cohérente disponibles dans le système invité, notamment VSS pour les systèmes Windows compatibles, afin de produire un état plus approprié à une restauration applicative.

Les points de contrôle de production ne sauvegardent pas la mémoire vive de la même manière qu'un point de contrôle standard.

Le choix doit correspondre à l'usage et au système invité.

### 21.3 Configurer le type de checkpoint

Pour examiner le type de point de contrôle configuré :

```powershell
Get-VM `
    -Name "VM-APP01" |
    Select-Object Name, CheckpointType
```

Pour privilégier les points de contrôle de production :

```powershell
Set-VM `
    -Name "VM-APP01" `
    -CheckpointType Production
```

Cette commande doit être utilisée en tenant compte des besoins de l'application et du comportement du système invité.

Un point de contrôle peut échouer ou ne pas fournir le résultat attendu si le système invité ou l'application ne satisfait pas les conditions nécessaires.

### 21.4 Concevoir une vraie stratégie de sauvegarde

Une stratégie robuste doit préciser :

- Les VM et applications protégées.
- La fréquence des sauvegardes.
- Les points de restauration nécessaires.
- La durée de conservation.
- La protection des copies contre les suppressions et les attaques.
- Le chiffrement éventuel.
- Les permissions d'administration.
- Les tests de restauration.
- Les objectifs RTO et RPO.
- Le stockage des journaux.
- Les modalités d'alerte en cas d'échec.

Les bases de données et les applications transactionnelles peuvent exiger des contrôles supplémentaires de cohérence et de restauration.

### 21.5 Règle de séparation des risques

Une sauvegarde conservée uniquement dans le même domaine de panne que les données originales peut être vulnérable au même incident.

Une architecture de sauvegarde doit envisager l'isolation, les droits de suppression, la protection contre les attaques et la possibilité de restaurer dans un environnement propre.

Il est prudent de tester régulièrement une restauration complète, pas uniquement de vérifier que la tâche de sauvegarde affiche un statut réussi.

Documentation : [Utiliser les points de contrôle Hyper-V](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/checkpoints).

## 22. Sécuriser la plateforme Hyper-V

### 22.1 Séparer l'administration

Les hôtes Hyper-V sont des composants critiques.

Une personne capable d'administrer l'hôte peut potentiellement contrôler les VM qu'il héberge. La sécurité de l'hôte doit donc être traitée comme un sujet majeur, distinct de la seule sécurité du système invité.

Principes recommandés :

- Limiter les administrateurs Hyper-V.
- Réserver des comptes d'administration adaptés.
- Contrôler l'accès aux interfaces de gestion.
- Protéger les informations d'authentification.
- Mettre à jour les hôtes.
- Limiter les services inutiles.
- Journaliser les changements importants.
- Protéger les sauvegardes.
- Séparer les réseaux lorsque nécessaire.
- Contrôler les accès aux fichiers de configuration et aux disques virtuels.

### 22.2 Sécuriser les machines virtuelles

Les machines virtuelles nécessitent également une politique de sécurité propre.

Selon le système invité et le besoin, cette politique peut comprendre :

- L'application des mises à jour.
- La réduction des privilèges.
- Le chiffrement des données.
- Le contrôle des accès distants.
- Le pare-feu.
- La journalisation.
- Les procédures de restauration.
- Le contrôle des logiciels installés.

L'isolation d'une VM ne la rend pas automatiquement sûre si les comptes, les applications ou les données qu'elle utilise sont compromis.

### 22.3 Protéger les secrets et les certificats

Les certificats utilisés pour certaines fonctions, les clés de récupération et les identifiants de services doivent être protégés.

Ne stocke pas de mots de passe en clair dans des scripts d'administration, dans des fichiers de configuration non protégés ou dans les notes d'exploitation du cluster.

Les autorisations d'accès doivent être attribuées aux comptes et services réellement nécessaires.

### 22.4 Protéger les communications

Il faut identifier les flux de gestion, de migration, de réplication et de stockage.

Selon le scénario, il peut être nécessaire de séparer certains flux, d'utiliser des protocoles sécurisés et de limiter les sources autorisées.

L'administration doit éviter d'exposer les interfaces de gestion ou les services de cluster à des réseaux non fiables.

### 22.5 Examiner les permissions du stockage

Les fichiers de configuration des VM, leurs disques et leurs sauvegardes sont des ressources sensibles.

Une personne qui peut modifier ces fichiers peut perturber la machine ou compromettre ses données.

Il faut donc vérifier les permissions NTFS et les permissions des partages, lorsqu'ils sont utilisés, ainsi que les droits d'accès des comptes d'administration et des solutions de sauvegarde.

## 23. Supervision et diagnostic

### 23.1 Que faut-il surveiller ?

Une infrastructure Hyper-V résiliente doit être observée à plusieurs niveaux :

**Nœuds**

- État du système.
- CPU et mémoire.
- Température et état matériel selon les outils disponibles.
- État des cartes réseau.
- État des services.
- Redémarrages et événements système.

**Cluster**

- État du quorum.
- État des nœuds.
- Santé des rôles et ressources.
- Événements de basculement.
- Réseaux du cluster.
- Santé du stockage.

**Hyper-V**

- État des VM.
- Utilisation CPU et mémoire.
- Connectivité réseau des VM.
- État des disques virtuels.
- Migrations.
- Points de contrôle et espace de stockage.

**Sauvegarde et reprise**

- Dernière sauvegarde réussie.
- Échecs de sauvegarde.
- Résultat des tests de restauration.
- Santé de la réplication.
- Retard de réplication.
- Respect des objectifs de reprise.

### 23.2 Commandes utiles

Examiner les nœuds :

```powershell
Get-ClusterNode
```

Examiner les rôles :

```powershell
Get-ClusterGroup
```

Examiner les ressources :

```powershell
Get-ClusterResource
```

Examiner les disques du cluster :

```powershell
Get-ClusterSharedVolume
```

Examiner le quorum :

```powershell
Get-ClusterQuorum
```

Examiner les VM :

```powershell
Get-VM |
    Select-Object Name,
                  State,
                  ComputerName,
                  Uptime
```

Examiner les commutateurs :

```powershell
Get-VMSwitch
```

Examiner les interfaces réseau :

```powershell
Get-NetAdapter
```

Ces commandes donnent une vue ponctuelle. Une supervision opérationnelle doit aussi recueillir les mesures dans le temps, détecter les anomalies et déclencher des alertes.

### 23.3 Générer un journal du cluster

Pour analyser des problèmes, la cmdlet `Get-ClusterLog` peut générer un journal.

Exemple :

```powershell
New-Item `
    -Path "C:\ClusterLogs" `
    -ItemType Directory `
    -Force | Out-Null

Get-ClusterLog `
    -Destination "C:\ClusterLogs" `
    -UseLocalTime
```

Le rapport généré doit être interprété en tenant compte de l'heure de l'incident, des événements Windows et des opérations exécutées.

### 23.4 Journaux d'événements

Les journaux d'événements Windows peuvent fournir des informations utiles sur :

- La santé du cluster.
- Les basculements.
- Les échecs d'accès au stockage.
- Les erreurs de migration.
- Les services Hyper-V.
- Les problèmes de connexion réseau.
- Les mises à jour.
- Les erreurs de sauvegarde.

L'analyse doit être chronologique : rechercher ce qui s'est produit avant l'incident, pendant l'incident puis après la reprise.

### 23.5 La supervision ne doit pas seulement mesurer la disponibilité du serveur

Un hôte qui répond au réseau peut héberger une VM dont l'application est bloquée.

Il faut donc mesurer la disponibilité du service, et pas uniquement celle du système physique.

Exemple :

```text
HV01 : opérationnel
   |
   +-- VM-APP01 : démarrée
          |
          +-- Service applicatif : arrêté
          |
          +-- Site Web : inaccessible
```

Un contrôle qui vérifie uniquement l'état de HV01 ne détectera pas nécessairement ce problème.

Pour les services critiques, combine les contrôles d'infrastructure et les tests fonctionnels adaptés.

## 24. Méthode de résolution des incidents

### 24.1 Cluster hors ligne

Lorsqu'un cluster est indisponible, ne commence pas par redémarrer arbitrairement les nœuds.

Procède dans l'ordre :

1. Vérifier l'état physique et logiciel des nœuds.
2. Vérifier la communication réseau.
3. Vérifier l'état du quorum et du témoin.
4. Vérifier le stockage et ses chemins.
5. Examiner les événements Windows.
6. Examiner les journaux du cluster.
7. Identifier le dernier changement.
8. Appliquer une correction contrôlée.
9. Valider le rétablissement de la santé du cluster.
10. Vérifier les applications hébergées.

Une perte de quorum ne doit pas être traitée comme un simple problème de démarrage d'un service.

### 24.2 Une VM ne démarre pas après basculement

Vérifie notamment :

- L'état du groupe clusterisé.
- La disponibilité du stockage.
- Les chemins des disques virtuels.
- Les permissions.
- Les commutateurs virtuels.
- L'état des ressources dépendantes.
- Les capacités CPU et mémoire du nœud.
- Les journaux Hyper-V.
- Les informations du cluster.

Il faut déterminer si le problème est une erreur de configuration, une dépendance manquante, une panne de stockage ou un manque de ressources.

### 24.3 Migration à chaud refusée

Les causes possibles comprennent :

- Une incompatibilité entre les hôtes.
- Une différence de configuration réseau.
- Une mauvaise configuration d'authentification.
- Des permissions insuffisantes.
- Une délégation Kerberos incorrecte.
- Des chemins de stockage indisponibles.
- Des ressources insuffisantes sur la destination.
- Un problème de version de configuration de la VM.
- Une fonctionnalité de la VM non prise en charge par l'hôte cible.

La démarche consiste à examiner le message d'erreur précis, puis à vérifier chaque dépendance.

Il ne faut pas désactiver les contrôles de sécurité pour forcer une migration.

### 24.4 Panne d'accès au stockage

Vérifie :

1. L'état du stockage.
2. Les contrôleurs et chemins.
3. Le réseau de stockage.
4. Les événements du système.
5. Les ressources de disque du cluster.
6. Les paramètres MPIO lorsque cette fonctionnalité est utilisée.
7. Les conditions de reprise du stockage.
8. Les recommandations du fournisseur.

N'initialise pas un disque ou ne reformate pas un volume pour tenter de rétablir un accès perdu.

### 24.5 Retard de réplication Hyper-V

Le retard peut provenir notamment :

- D'une bande passante insuffisante.
- D'une forte charge d'E/S.
- D'une interruption réseau.
- D'un espace de stockage insuffisant.
- D'une erreur d'authentification.
- D'un problème de configuration du serveur de réplication.
- D'une accumulation des changements à transférer.

La correction doit tenir compte de l'état de la réplication, du RPO attendu et des risques liés à une nouvelle initialisation ou à une opération de resynchronisation.

### 24.6 Appliquer une méthode de diagnostic reproductible

```text
Incident signalé
      |
      v
Déterminer le périmètre
      |
      v
Collecter les informations
      |
      v
Vérifier les dépendances
      |
      v
Identifier la cause probable
      |
      v
Préparer une correction
      |
      v
Valider le risque et le retour arrière
      |
      v
Appliquer la correction
      |
      v
Vérifier le service
      |
      v
Documenter l'incident
```

Cette méthode réduit les risques d'aggraver une panne par une série d'actions non contrôlées.

## 25. Travaux pratiques guidés

Les travaux pratiques qui suivent doivent être réalisés dans un environnement de laboratoire. Les tests de stockage, de quorum et de panne peuvent provoquer une indisponibilité ; ils ne doivent pas être exécutés à l'aveugle sur une infrastructure de production.

### TP 1 — Préparer et valider les nœuds Hyper-V

**Objectif :** vérifier les conditions nécessaires au cluster.

Préparation :

- Deux serveurs ou deux VM de laboratoire adaptées aux objectifs pédagogiques.
- Une version de Windows Server compatible.
- Un réseau de gestion.
- Un stockage de laboratoire si le scénario le nécessite.
- Des permissions d'administration adaptées.

Étapes :

1. Installer Hyper-V si nécessaire.
2. Installer Failover Clustering.
3. Vérifier les noms et les adresses IP.
4. Vérifier le DNS.
5. Vérifier la connectivité.
6. Vérifier les versions et mises à jour.
7. Lancer `Test-Cluster`.
8. Examiner le rapport de validation.
9. Corriger les anomalies.
10. Conserver les preuves de validation.

Commande :

```powershell
Test-Cluster -Node HV01,HV02
```

**Résultat attendu :** une validation documentée dont les erreurs critiques ont été corrigées ou dont les écarts sont explicitement justifiés.

### TP 2 — Créer un cluster

**Objectif :** créer et examiner un cluster de laboratoire.

Étapes :

1. Vérifier les autorisations Active Directory.
2. Vérifier l'adresse IP prévue.
3. Créer le cluster.
4. Vérifier le nom et les nœuds.
5. Vérifier les réseaux.
6. Vérifier l'accès administratif.
7. Examiner les groupes et ressources.
8. Documenter la configuration initiale.

Commande d'exemple :

```powershell
New-Cluster `
    -Name "CL-HV" `
    -Node "HV01","HV02" `
    -StaticAddress "192.168.20.50" `
    -NoStorage
```

Cette commande est valable uniquement si les conditions de réseau, de DNS, d'Active Directory et de validation sont réunies.

### TP 3 — Configurer le quorum

**Objectif :** comprendre le rôle du témoin.

Étapes :

1. Examiner la configuration du quorum.
2. Examiner le nombre de nœuds et leurs votes.
3. Préparer un partage témoin indépendant si ce scénario a été choisi.
4. Configurer le témoin.
5. Vérifier les permissions du partage.
6. Vérifier la résolution du nom du serveur témoin.
7. Confirmer la configuration.
8. Écrire ce que le cluster peut tolérer dans chaque scénario de panne étudié.

Commandes :

```powershell
Get-ClusterQuorum
```

Puis, si un partage témoin adapté a été préparé :

```powershell
Set-ClusterQuorum `
    -FileShareWitness "\\FSW01\CL-HV-Witness"
```

Enfin :

```powershell
Get-ClusterQuorum
```

Le compte du cluster doit disposer des autorisations requises sur le partage.

### TP 4 — Préparer un CSV

**Objectif :** mettre à disposition un volume de stockage de VM.

Étapes :

1. Identifier le stockage de laboratoire prévu.
2. Vérifier qu'il ne contient pas de données à conserver.
3. Vérifier l'accès des nœuds.
4. Exécuter les validations nécessaires.
5. Ajouter le disque au cluster.
6. Identifier le nom de la ressource.
7. Ajouter le disque comme CSV si l'architecture le prévoit.
8. Vérifier le chemin du volume.
9. Vérifier l'espace libre.
10. Documenter le résultat.

Une fois la ressource identifiée et vérifiée :

```powershell
Get-ClusterSharedVolume
```

Il faut vérifier que le volume correspond bien au stockage prévu avant de créer des machines virtuelles.

### TP 5 — Créer une machine virtuelle

**Objectif :** créer une VM de test dans l'espace de stockage partagé.

Prérequis :

- Un CSV fonctionnel.
- Un commutateur virtuel.
- Un système d'exploitation invité compatible.
- Un emplacement de stockage adapté.

Étapes :

1. Créer la VM.
2. Configurer son processeur et sa mémoire.
3. Vérifier les disques.
4. Vérifier le réseau virtuel.
5. Installer le système invité.
6. Vérifier le démarrage.
7. Tester une application simple.
8. Ajouter la VM au cluster.
9. Contrôler l'état du rôle.

Commande d'ajout du rôle :

```powershell
Add-ClusterVirtualMachineRole `
    -VirtualMachine "VM-APP01"
```

### TP 6 — Tester une migration à chaud

**Objectif :** déplacer une VM en fonctionnement vers un autre nœud.

Étapes :

1. Vérifier la santé du cluster.
2. Vérifier la configuration Hyper-V des deux hôtes.
3. Vérifier les réseaux virtuels.
4. Vérifier les permissions et l'authentification.
5. Vérifier l'état du stockage.
6. Démarrer la VM et vérifier son service.
7. Déplacer la VM vers le second nœud.
8. Contrôler l'état de la VM.
9. Tester le réseau et l'application.
10. Documenter le résultat.

Dans un cluster, tu peux déplacer un groupe clusterisé par exemple avec :

```powershell
Move-ClusterGroup `
    -Name "VM-APP01" `
    -Node "HV02"
```

Vérifie que cette opération correspond bien au scénario de migration planifié et que les conditions sont réunies.

### TP 7 — Simuler un incident de nœud

**Objectif :** mesurer le comportement du cluster après un incident.

Étapes :

1. Vérifier le quorum.
2. Vérifier le témoin.
3. Vérifier l'état des VM.
4. Préparer le scénario de panne.
5. Établir une fenêtre de test.
6. Observer l'incident dans le laboratoire.
7. Mesurer le temps nécessaire à la reprise.
8. Vérifier les services.
9. Examiner les journaux.
10. Rédiger un compte rendu.

Le test ne doit pas être réalisé sur une machine de production sans autorisation et sans stratégie de retour arrière.

### TP 8 — Préparer une stratégie de reprise après sinistre

**Objectif :** concevoir une protection hors du site principal.

Étapes :

1. Définir les VM critiques.
2. Fixer les RTO et RPO.
3. Choisir un hôte ou cluster cible.
4. Vérifier la connectivité et le stockage.
5. Configurer Hyper-V Replica selon le scénario.
6. Vérifier l'état de réplication.
7. Concevoir le plan d'adressage de secours.
8. Préparer un ordre de démarrage.
9. Préparer les vérifications fonctionnelles.
10. Tester une reprise contrôlée.

Le résultat attendu est un plan de reprise documenté et validé, et non uniquement un écran indiquant que la réplication est activée.

## 26. Exercices corrigés

### Exercice 1 — Cluster avec deux nœuds

Deux serveurs Hyper-V sont configurés dans un cluster. Il n'y a pas de témoin et l'administrateur veut arrêter un nœud pour maintenance.

**Question :** peut-il supposer que le cluster continuera nécessairement à fonctionner ?

**Corrigé :** non. Il doit vérifier la configuration du quorum, le nombre de votes actifs, l'état des ressources et la capacité de l'autre nœud. La décision dépend de la configuration effective du cluster. La maintenance d'un nœud ne doit pas être effectuée sans avoir confirmé que le cluster peut conserver le quorum.

### Exercice 2 — Une VM ne redémarre pas sur le second nœud

Une VM fonctionne normalement sur HV01. Après une panne de HV01, elle ne démarre pas sur HV02.

**Question :** que faut-il vérifier ?

**Corrigé :**

- État du groupe et de la ressource clusterisés.
- Disponibilité du stockage.
- Chemin des disques virtuels.
- Présence des commutateurs nécessaires.
- Capacité mémoire et CPU de HV02.
- Événements Hyper-V.
- Dépendances et permissions.
- Compatibilité de la configuration des hôtes.

Il faut déterminer la cause au lieu de supprimer ou de recréer la VM sans analyse.

### Exercice 3 — Migration avec erreur d'authentification

La migration à chaud échoue avec une erreur d'accès ou d'authentification.

**Question :** que faut-il contrôler ?

**Corrigé :**

- Le protocole d'authentification retenu.
- La configuration de délégation Kerberos si nécessaire.
- Les permissions sur les hôtes concernés.
- Les noms DNS et les identités des serveurs.
- Les SPN pertinents.
- Les restrictions imposées par la configuration de sécurité.
- Les journaux et le message d'erreur exact.

Il ne faut pas désactiver les protections de sécurité sans comprendre l'origine de l'incident.

### Exercice 4 — Une migration perturbe les applications

Pendant plusieurs migrations, les applications deviennent lentes.

**Question :** quelle explication est plausible ?

**Corrigé :** les migrations peuvent consommer de la bande passante, du CPU et des ressources de stockage. Il faut examiner les réseaux utilisés, le nombre de migrations simultanées, les options de performance et les métriques des hôtes. Une limitation ou une séparation du trafic peut être nécessaire.

### Exercice 5 — Panne complète du site principal

Le cluster possède deux nœuds, mais le bâtiment subit une coupure électrique prolongée.

**Question :** le cluster suffit-il à garantir la reprise ?

**Corrigé :** non. Les nœuds et les services peuvent être indisponibles simultanément. Une stratégie de reprise doit prévoir une copie des données ou des VM sur une infrastructure indépendante, une procédure de basculement et une méthode de validation fonctionnelle. Hyper-V Replica et une solution de sauvegarde adaptée peuvent faire partie de cette stratégie.

### Exercice 6 — S2D et SAN

Une entreprise possède une baie SAN et veut utiliser les disques internes des nœuds Hyper-V pour améliorer la redondance.

**Question :** peut-elle traiter les disques internes comme des disques CSV ordinaires sans revoir la conception ?

**Corrigé :** non. Le modèle S2D implique une architecture distincte avec des exigences matérielles, réseau et de stockage propres. Il faut valider l'architecture et les données existantes avant toute modification.

### Exercice 7 — Le disque partagé est considéré comme une sauvegarde

Un administrateur affirme que les VM n'ont pas besoin de sauvegarde, car elles utilisent un CSV accessible par les deux nœuds.

**Question :** pourquoi cette affirmation est-elle incorrecte ?

**Corrigé :** les CSV assurent l'accès partagé au stockage dans le cadre du cluster. Ils ne protègent pas contre toutes les suppressions, corruptions logiques, attaques ou pannes majeures. Une solution de sauvegarde distincte et une procédure de restauration testée sont nécessaires.

### Exercice 8 — Le témoin est placé dans le cluster qu'il arbitre

Le partage témoin se trouve sur un serveur de fichiers virtuel hébergé par le cluster lui-même.

**Question :** quel est le risque ?

**Corrigé :** le témoin peut dépendre de la disponibilité du cluster qu'il est censé aider à arbitrer. Une panne commune peut donc rendre l'arbitrage moins fiable ou indisponible. Il faut concevoir un témoin indépendant selon les recommandations applicables à l'architecture.

### Exercice 9 — La réplication est à jour, mais le service ne démarre pas

La copie de la VM a été répliquée avec succès sur le site de secours, mais l'application est inaccessible après basculement.

**Question :** quelles dépendances faut-il vérifier ?

**Corrigé :**

- Configuration IP.
- VLAN et routage.
- DNS et noms des services.
- Règles de pare-feu.
- Identités et comptes de service.
- Ordre de démarrage des VM.
- Dépendances aux bases de données.
- Cohérence applicative et données.
- Autorisations et secrets nécessaires.

La réplication de la VM n'assure pas automatiquement l'accessibilité de toute l'application.

## 27. Projet de synthèse : infrastructure Hyper-V hautement disponible

### 27.1 Contexte

Une entreprise héberge plusieurs applications métier sur des machines virtuelles Windows Server.

Elle veut réduire le risque de panne, permettre les mises à jour des hôtes sans interruption planifiée importante et disposer d'un site secondaire pour les incidents majeurs.

Elle exige :

- Un cluster Hyper-V local.
- Une stratégie de quorum.
- Un stockage résilient.
- Des migrations à chaud.
- Une politique de maintenance.
- Des sauvegardes.
- Une réplication hors site des VM critiques.
- Un plan de reprise documenté.
- Une supervision des hôtes, du cluster et des applications.

### 27.2 Architecture proposée

```text
                         UTILISATEURS
                              |
                              v
                     RÉSEAU DE PRODUCTION
                              |
              +---------------+---------------+
              |                               |
              v                               v
        +------------+                  +------------+
        |    HV01    |                  |    HV02    |
        | Hyper-V    |                  | Hyper-V    |
        | Cluster    |                  | Cluster    |
        +------------+                  +------------+
              |                               |
              +---------------+---------------+
                              |
                              v
                     STOCKAGE RÉSILIENT
                   CSV ou architecture S2D
                              |
                              v
                  VM DE PRODUCTION CRITIQUES
                              |
                              v
                       RÉPLICATION
                              |
                              v
                     SITE SECONDAIRE
                   Hôte ou cluster de DR
                              |
                              v
                 Procédure de reprise contrôlée

En parallèle :
  Sauvegardes indépendantes et protégées
  Supervision centralisée
  Journalisation et procédures d'exploitation
```

Il s'agit d'un modèle fonctionnel. Le choix du stockage, des réseaux et des mécanismes de réplication doit être adapté au matériel, aux contraintes métier et aux objectifs de reprise.

### 27.3 Travail demandé

Produis un dossier technique comprenant :

1. Le schéma de l'infrastructure.
2. Les rôles des différents réseaux.
3. La stratégie de stockage.
4. La stratégie de quorum.
5. Les critères de dimensionnement CPU et mémoire.
6. Les règles de création des VM.
7. La configuration réseau Hyper-V.
8. Le processus de migration à chaud.
9. Le processus de maintenance des hôtes.
10. La politique de mise à jour.
11. La stratégie de sauvegarde.
12. La procédure de reprise après sinistre.
13. Les indicateurs de supervision.
14. Les tests de panne.
15. Les procédures de retour arrière.

### 27.4 Livrables

Le projet doit contenir :

- Un schéma d'architecture.
- Un inventaire des hôtes, des réseaux et du stockage.
- Un rapport de validation du cluster.
- Une description du quorum.
- Un plan de capacité.
- Un rapport de migration à chaud.
- Un rapport de test de basculement.
- Une procédure de maintenance.
- Une politique de sauvegarde.
- Un plan de reprise après sinistre.
- Un rapport de tests et d'anomalies.
- Une procédure d'exploitation quotidienne.

### 27.5 Critères de réussite

Le projet est réussi lorsque :

- La configuration du cluster est validée.
- Le quorum est compris et documenté.
- Les rôles peuvent être déplacés selon les scénarios testés.
- Les applications restent accessibles selon le niveau de disponibilité attendu.
- Les ressources disponibles sont suffisantes lors d'une panne simulée.
- Les mises à jour peuvent être coordonnées.
- Les sauvegardes peuvent être restaurées.
- Le basculement vers le site secondaire est documenté et testé.
- Les objectifs de RTO et de RPO sont mesurés.
- Les opérations peuvent être reprises par un autre administrateur.

## 28. Défi final — Concevoir une plateforme critique

Tu dois concevoir une plateforme pour une entreprise de 250 utilisateurs qui héberge :

- Deux applications métier.
- Une base de données.
- Un serveur Web interne.
- Un serveur de fichiers.
- Un contrôleur de domaine.
- Plusieurs serveurs de services techniques.

L'entreprise possède deux hôtes Hyper-V et veut être capable de survivre à la panne d'un hôte, de réaliser des opérations de maintenance et de restaurer les services après la perte complète du site principal.

### Partie A — Architecture

Définis :

- Le rôle de chaque serveur.
- Les réseaux.
- Le stockage.
- Les dépendances de l'annuaire.
- Les VM les plus critiques.
- Les capacités disponibles après la perte d'un hôte.

Justifie chaque décision.

### Partie B — Haute disponibilité

Définis :

- La stratégie de cluster.
- Le quorum et le témoin.
- Les règles de basculement.
- Les conditions de déplacement des VM.
- Le plan de capacité N+1.
- Les scénarios de panne.

Explique précisément les interruptions qu'un basculement peut encore provoquer.

### Partie C — Maintenance et exploitation

Prépare :

- Le processus de drainage d'un nœud.
- La procédure de mise à jour.
- Le processus de retour du nœud.
- Les contrôles d'application.
- La documentation des changements.

### Partie D — Reprise après sinistre

Définis :

- Le RTO et le RPO de chaque service.
- L'architecture du site secondaire.
- Le mécanisme de réplication.
- La stratégie de sauvegarde.
- L'ordre de démarrage des applications.
- Le plan de communication pendant un sinistre.
- Le retour éventuel vers le site principal.

### Partie E — Validation

Prépare un plan de test couvrant :

- La migration à chaud.
- Le basculement d'un rôle.
- La perte d'un nœud.
- La perte d'un réseau.
- L'indisponibilité du stockage, dans un environnement de test adapté.
- La restauration d'une sauvegarde.
- La reprise depuis le site secondaire.
- Le contrôle de cohérence des données.

### Partie F — Exploitation

Rédige une procédure opérationnelle avec les commandes de vérification, les journaux à examiner, les indicateurs à surveiller, les seuils d'alerte et les conditions d'escalade.

Le résultat doit être un dossier d'exploitation utilisable, pas simplement une liste de commandes.

## 29. Référence opérationnelle : commandes essentielles

### Administration du cluster

```powershell
Get-Cluster
Get-ClusterNode
Get-ClusterGroup
Get-ClusterResource
Get-ClusterNetwork
Get-ClusterQuorum
Get-ClusterSharedVolume
```

### Validation et diagnostic

```powershell
Test-Cluster -Node HV01,HV02
Get-ClusterLog -Destination "C:\ClusterLogs" -UseLocalTime
```

Le dossier cible doit exister ou être créé au préalable, et le test doit être adapté au stockage ainsi qu'à l'état de l'infrastructure.

### Hyper-V

```powershell
Get-VM
Get-VMSwitch
Get-VMNetworkAdapter -VMName "VM-APP01"
Get-VMHardDiskDrive -VMName "VM-APP01"
```

### Maintenance et déplacement

```powershell
Move-ClusterGroup -Name "VM-APP01" -Node "HV02"
```

Le nom du rôle et le nœud cible doivent être vérifiés avant l'opération.

### Réseau et capacité

```powershell
Get-NetAdapter
Get-NetIPAddress -AddressFamily IPv4

Get-VM |
    Select-Object Name,
                  State,
                  ComputerName,
                  Uptime
```

### Quorum

```powershell
Get-ClusterQuorum

Get-ClusterNode |
    Select-Object Name,
                  State,
                  NodeWeight,
                  DynamicWeight
```

Ces commandes sont des points de départ pour le diagnostic. Une exploitation professionnelle nécessite de conserver les résultats utiles, de surveiller leur évolution et d'interpréter les erreurs dans leur contexte.

## 30. Bonnes pratiques de l'expert

### Conception

- Définis les objectifs RTO et RPO avant de choisir les technologies.
- Sépare les mécanismes de haute disponibilité, de réplication et de sauvegarde.
- Valide l'architecture matérielle et logicielle avant le déploiement.
- Prévois les ressources nécessaires après la panne d'un nœud.
- Élimine les points uniques de défaillance lorsque les objectifs l'exigent.
- Documente les dépendances entre les services.

### Cluster

- Valide la configuration avant la mise en production.
- Surveille le quorum et le témoin.
- Vérifie les réseaux du cluster et leur indépendance réelle.
- Vérifie le stockage avant chaque opération importante.
- Teste le comportement des rôles lors des pannes prévues.
- Ne change pas la configuration de quorum sans analyse.
- Ne redémarre pas plusieurs nœuds sans stratégie approuvée.

### Hyper-V

- Dimensionne les VM selon la charge réelle.
- Vérifie les commutateurs virtuels sur les hôtes concernés.
- Contrôle les VLAN et les permissions réseau.
- Sécurise les interfaces de gestion.
- Teste les migrations à chaud.
- Vérifie la configuration d'authentification.
- Contrôle l'espace de stockage réel des disques virtuels.
- Ne considère pas un checkpoint comme une sauvegarde.

### Stockage

- Respecte les recommandations du fournisseur.
- Vérifie les chemins, les contrôleurs et les pilotes.
- Utilise un stockage adapté aux charges de travail.
- Prévois les alertes d'espace libre et de santé.
- Protège les volumes contre les suppressions et les corruptions.
- Documente le remplacement et la réparation des composants.

### Reprise après sinistre

- Fixe le RTO et le RPO avec les responsables métier.
- Vérifie l'état de la réplication.
- Prépare les réseaux du site secondaire.
- Documente les dépendances et l'ordre de démarrage.
- Teste régulièrement les restaurations.
- Mesure les temps réellement obtenus.
- Prépare les responsabilités et les communications.
- Ne confonds pas l'état « répliqué » avec l'état « service opérationnel ».

### Sécurité

- Limite les comptes d'administration.
- Protège les réseaux de gestion et de migration.
- Sécurise les secrets et les certificats.
- Protège les accès au stockage.
- Maintiens les hôtes et les VM à jour.
- Sépare et protège les sauvegardes.
- Journalise les opérations importantes.

## 31. Glossaire expert

**Cluster :** ensemble de nœuds coordonnés pour gérer des rôles ou services selon une configuration commune.

**Nœud :** serveur participant au cluster.

**WSFC :** Windows Server Failover Clustering, mécanisme de clustering de Windows Server.

**Hyper-V :** technologie de virtualisation de Microsoft.

**Haute disponibilité :** approche visant à réduire la durée d'indisponibilité d'un service.

**Basculement (failover) :** transfert d'un rôle vers un autre nœud après un incident ou une opération prévue.

**Migration à chaud :** déplacement d'une VM en fonctionnement entre des hôtes compatibles.

**Quorum :** mécanisme de décision déterminant si le cluster dispose des votes requis pour continuer à fonctionner.

**Témoin :** ressource participant au vote de quorum dans une configuration appropriée.

**Split-brain :** situation dangereuse dans laquelle plusieurs partitions pensent simultanément pouvoir administrer les mêmes ressources.

**CSV :** Cluster Shared Volume, volume partagé utilisable simultanément par les nœuds autorisés d'un cluster.

**S2D :** Storage Spaces Direct, mécanisme de stockage défini par logiciel fondé sur les disques locaux de plusieurs nœuds.

**VHDX :** format de disque dur virtuel utilisé par Hyper-V.

**SET :** Switch Embedded Teaming, technologie associant plusieurs cartes réseau dans un commutateur virtuel Hyper-V compatible.

**MPIO :** Multipath I/O, gestion de chemins multiples vers des ressources de stockage compatibles.

**RTO :** délai maximal ciblé pour rétablir un service après un incident.

**RPO :** quantité de données qu'une organisation accepte de perdre, exprimée en durée.

**Hyper-V Replica :** technologie de réplication asynchrone de machines virtuelles entre des hôtes ou clusters compatibles.

**CAU :** Cluster-Aware Updating, mécanisme d'orchestration des mises à jour des nœuds d'un cluster.

**Checkpoint :** point de contrôle d'une VM permettant de revenir à un état antérieur selon le type de point de contrôle et les conditions de restauration.

**N+1 :** approche de dimensionnement prévoyant la capacité nécessaire pour continuer à fonctionner après la perte d'un élément.

**Résilience :** capacité de l'infrastructure à continuer à fournir un service ou à le restaurer malgré certains incidents.

## 32. Documentation officielle Microsoft

Les guides suivants permettent d'approfondir les procédures et de vérifier les prérequis propres à la version installée.

### Failover Clustering

- [Vue d'ensemble de Failover Clustering](https://learn.microsoft.com/en-us/windows-server/failover-clustering/failover-clustering-overview)
- [Créer un cluster de basculement](https://learn.microsoft.com/en-us/windows-server/failover-clustering/create-failover-cluster)
- [Quorum et témoins](https://learn.microsoft.com/en-us/windows-server/failover-clustering/what-is-quorum-witness)
- [Configurer un témoin de partage de fichiers](https://learn.microsoft.com/en-us/windows-server/failover-clustering/file-share-witness)
- [Gérer les Cluster Shared Volumes](https://learn.microsoft.com/en-us/windows-server/failover-clustering/failover-cluster-manage-cluster-shared-volumes)
- [Cluster-Aware Updating](https://learn.microsoft.com/en-us/windows-server/failover-clustering/cluster-aware-updating)
- [Dépanner Cluster-Aware Updating](https://learn.microsoft.com/en-us/troubleshoot/windows-server/high-availability/cluster-aware-updating)

### Hyper-V

- [Vue d'ensemble de Hyper-V](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/overview)
- [Commutateur virtuel Hyper-V](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/virtual-switch)
- [Vue d'ensemble de la migration à chaud](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/manage/live-migration-overview)
- [Configurer les hôtes pour la migration à chaud](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/deploy/set-up-hosts-for-live-migration-without-failover-clustering)
- [Vue d'ensemble de Hyper-V Replica](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/replication-overview)
- [Réplication d'une machine virtuelle Hyper-V](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/replication-virtual-machines)
- [Utiliser les points de contrôle Hyper-V](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/checkpoints)

### Stockage et diagnostic

- [Vue d'ensemble de Storage Spaces Direct](https://learn.microsoft.com/en-us/windows-server/storage/storage-spaces/storage-spaces-direct-overview)
- [Déployer Storage Spaces Direct](https://learn.microsoft.com/en-us/windows-server/storage/storage-spaces/deploy-storage-spaces-direct)
- [Dépanner les migrations à chaud Hyper-V](https://learn.microsoft.com/en-us/troubleshoot/windows-server/virtualization/troubleshoot-live-migration-issues)

## Conclusion

L'expertise Windows Server ne consiste pas uniquement à savoir installer Hyper-V et créer un cluster. Elle consiste à construire une architecture dans laquelle les défaillances peuvent être détectées, contenues et traitées selon des procédures maîtrisées.

La haute disponibilité locale, la migration à chaud, le stockage résilient, la réplication hors site et la sauvegarde ont des objectifs différents. Ils doivent être combinés en fonction des risques, des contraintes métier et des objectifs de reprise.

Un environnement réellement professionnel est un environnement dont la configuration a été validée, dont les dépendances sont documentées, dont les mécanismes de protection ont été testés et dont les résultats peuvent être mesurés.

La règle fondamentale de ce niveau expert est la suivante : **ne jamais considérer qu'une infrastructure est hautement disponible simplement parce que ses composants sont installés. Sa capacité à résister à une panne doit être démontrée par des tests contrôlés, des mesures et une procédure d'exploitation reproductible.**