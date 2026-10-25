# Azure : les fondamentaux du cloud Microsoft

## 1. Présentation du cours

### 1.1 Objectif général

Ce cours constitue le premier niveau du parcours Azure. Il permet de comprendre le fonctionnement du cloud Microsoft Azure, de créer des ressources, de les administrer et d'appliquer les premières règles de sécurité et de maîtrise des coûts.

L'objectif n'est pas simplement de connaître des noms de services. Il s'agit de savoir à quoi servent les composants, comment ils communiquent, comment les déployer et comment vérifier leur bon fonctionnement.

Le parcours complet suit cette progression :

```text
NIVEAU 1 : DÉBUTANT
    |
    | Comprendre Azure, créer des ressources,
    | utiliser Azure CLI et appliquer les bases
    | de la sécurité et des coûts.
    |
    v
NIVEAU 2 : INTERMÉDIAIRE
    |
    | Construire des architectures complètes,
    | configurer le réseau, les identités,
    | le stockage, la supervision et l'automatisation.
    |
    v
NIVEAU 3 : EXPERT
    |
    | Concevoir des architectures d'entreprise,
    | appliquer une gouvernance à grande échelle,
    | renforcer la sécurité et la résilience,
    | optimiser les coûts et les opérations.
```

Les sujets avancés comme les architectures réseau complexes, Azure Policy à grande échelle, les identités managées dans des chaînes d'automatisation, Terraform et la reprise après sinistre seront approfondis dans les cours suivants. Ils seront néanmoins introduits ici lorsque cela aide à comprendre les fondations.

### 1.2 Prérequis

Aucune expérience préalable d'Azure n'est obligatoire.

Il est toutefois utile de savoir :
- utiliser un terminal Windows, Linux ou macOS ;
- comprendre les notions d'adresse IP, de serveur et de réseau ;
- manipuler des fichiers et des répertoires ;
- utiliser quelques commandes de base comme `cd`, `ls`, `dir` ou `ping`.

### 1.3 Compétences visées

À la fin de ce cours, il faudra être capable de :

1. Expliquer le cloud computing et les principaux modèles de services.
2. Comprendre l'organisation géographique et administrative d'Azure.
3. Distinguer un tenant, un abonnement, un groupe de ressources et une ressource.
4. Identifier les principaux services de calcul, de réseau et de stockage.
5. Se connecter au portail Azure et à Azure CLI.
6. Créer, examiner et supprimer un groupe de ressources.
7. Comprendre les bases des machines virtuelles et des applications web.
8. Expliquer le rôle de Microsoft Entra ID et d'Azure RBAC.
9. Identifier les principaux risques de sécurité du cloud.
10. Estimer les risques financiers liés aux ressources et appliquer des mesures simples de contrôle des coûts.
11. Réaliser un petit projet cloud documenté et reproductible.

## 2. Comprendre le cloud computing

### 2.1 Qu'est-ce que le cloud ?

Le cloud computing consiste à utiliser des ressources informatiques accessibles par un réseau, généralement Internet, sans devoir posséder et administrer physiquement tous les équipements qui les hébergent.

Ces ressources peuvent être :
- des machines virtuelles ;
- des réseaux ;
- des bases de données ;
- des espaces de stockage ;
- des services d'identité ;
- des plateformes applicatives ;
- des outils d'analyse, de supervision ou d'intelligence artificielle.

Microsoft Azure est une plateforme cloud qui fournit ces services à travers des centres de données répartis dans différentes régions du monde.

### 2.2 Infrastructure traditionnelle et cloud

Dans une infrastructure traditionnelle, une entreprise achète des serveurs, installe des équipements réseau, organise l'alimentation électrique, assure le refroidissement et gère le remplacement du matériel.

Dans le cloud, elle peut provisionner des ressources à la demande, selon les services disponibles et les limites de son abonnement.

```text
INFRASTRUCTURE TRADITIONNELLE

Entreprise
   |
   +-- Salle serveur
   |     +-- Serveurs physiques
   |     +-- Stockage
   |     +-- Commutateurs et routeurs
   |     +-- Alimentation et refroidissement
   |
   +-- Maintenance matérielle
   +-- Capacité à prévoir
   +-- Investissement initial important


INFRASTRUCTURE CLOUD AZURE

Utilisateur / Administrateur
          |
          v
   Portail Azure / CLI / API
          |
          v
     Azure Resource Manager
          |
          v
   Ressources provisionnées
          |
          +-- Calcul
          +-- Réseau
          +-- Stockage
          +-- Services managés
```

Le cloud ne supprime pas la responsabilité technique. Il déplace une partie des responsabilités vers le fournisseur et modifie la manière de gérer l'infrastructure.

### 2.3 Les avantages du cloud

**Élasticité**

Il est possible d'augmenter ou de réduire les ressources lorsque la charge évolue, à condition que le service utilisé le permette.

**Provisionnement rapide**

Une machine virtuelle peut être créée en quelques minutes, sans acheter de serveur physique.

**Accès mondial**

Les ressources peuvent être déployées dans différentes régions, sous réserve des services, des quotas, des exigences réglementaires et de la disponibilité géographique.

**Services managés**

Certains services permettent de déléguer au fournisseur une partie des opérations, comme les mises à jour de la plateforme ou la gestion de la disponibilité de l'infrastructure sous-jacente.

**Automatisation**

Les ressources peuvent être créées à partir de scripts, de modèles et de pipelines de déploiement.

### 2.4 Les limites et les risques

Le cloud ne signifie pas que tout est automatiquement sécurisé, disponible ou gratuit.

Les risques comprennent :
- une mauvaise configuration réseau ;
- des permissions trop larges ;
- des données exposées publiquement ;
- des dépenses oubliées ;
- une dépendance à un service ou à une région ;
- une panne d'application malgré la disponibilité du fournisseur ;
- une mauvaise gestion des sauvegardes ;
- une perte d'accès au compte d'administration.

Le cloud exige donc des compétences en administration, en sécurité, en réseau et en gestion des coûts.

## 3. Les modèles de services cloud

### 3.1 IaaS : Infrastructure as a Service

L'IaaS fournit des composants d'infrastructure comme des machines virtuelles, des disques et des réseaux virtuels.

Le client reste responsable d'une partie importante de l'administration du système d'exploitation, des applications, des mises à jour et de la configuration.

Exemple : une machine virtuelle Linux hébergeant un serveur web.

### 3.2 PaaS : Platform as a Service

Le PaaS fournit une plateforme sur laquelle déployer une application sans administrer directement tous les éléments du système sous-jacent.

Exemple : Azure App Service pour héberger une application web.

Le fournisseur gère une plus grande partie de la plateforme, mais le client reste responsable de son application, de ses données, de ses accès et de sa configuration.

### 3.3 SaaS : Software as a Service

Le SaaS fournit un logiciel prêt à l'emploi accessible par le réseau.

Exemple : un service de messagerie ou de collaboration hébergé par un fournisseur cloud.

Le client gère généralement les utilisateurs, les données et certains paramètres, mais n'administre pas directement les serveurs qui hébergent le logiciel.

### 3.4 Comparaison des modèles

| Élément | IaaS | PaaS | SaaS |
|---|---|---|---|
| Infrastructure physique | Fournisseur | Fournisseur | Fournisseur |
| Système d'exploitation sous-jacent | Responsabilité partagée selon le service | Principalement fournisseur | Fournisseur |
| Application | Client | Client | Fournisseur, avec paramètres client |
| Données et accès | Client | Client | Responsabilité partagée |
| Contrôle technique | Élevé | Intermédiaire | Plus limité |
| Exemple Azure | Azure Virtual Machines | Azure App Service | Services logiciels Microsoft en ligne |

La répartition exacte des responsabilités dépend toujours du service choisi.

### 3.5 Cloud public, privé et hybride

**Cloud public**

Les services sont fournis par un prestataire cloud à plusieurs clients, avec une isolation logique entre leurs environnements.

**Cloud privé**

L'infrastructure est réservée à une organisation. Elle peut être hébergée dans ses propres installations ou par un prestataire.

**Cloud hybride**

Une organisation combine son infrastructure locale avec des services cloud.

```text
                    UTILISATEURS
                         |
             +-----------+-----------+
             |                       |
             v                       v
     Infrastructure locale       Microsoft Azure
             |                       |
       Serveurs internes       Machines virtuelles
       Applications locales   Stockage cloud
             |                       |
             +------ Réseau --------+
                  interconnecté
```

Une architecture hybride peut être utile lorsqu'une organisation doit conserver certains systèmes sur site, migrer progressivement ou répondre à des contraintes particulières.

## 4. Découvrir l'architecture globale d'Azure

### 4.1 Les centres de données

Les services Azure reposent sur une infrastructure physique comprenant des serveurs, des équipements réseau, des systèmes électriques et des dispositifs de refroidissement.

Le client utilise les services logiques exposés par Azure. Il n'administre généralement pas directement les serveurs physiques du fournisseur.

### 4.2 Les régions Azure

Une région Azure correspond à une zone géographique dans laquelle Microsoft exploite une infrastructure cloud.

Exemples de noms de régions utilisés dans les commandes :
- `westeurope` ;
- `northeurope` ;
- `southafricanorth` ;
- `eastus`.

Ces noms servent à identifier des régions dans les interfaces et les outils.

Une région ne propose pas nécessairement tous les services Azure. La disponibilité des services, des tailles de machines et des fonctions dépend de la région et parfois de l'abonnement.

Avant de choisir une région, il faut examiner :
- la proximité des utilisateurs ;
- les exigences de résidence et de traitement des données ;
- les services disponibles ;
- les performances réseau ;
- les coûts ;
- les exigences de continuité d'activité.

La liste officielle des régions est disponible ici :

https://learn.microsoft.com/azure/reliability/regions-list

### 4.3 Les zones de disponibilité

Certaines régions prennent en charge des zones de disponibilité.

Une zone de disponibilité correspond à un ensemble distinct de ressources de centre de données dans une région, conçu pour réduire l'impact de certaines pannes localisées.

```text
RÉGION AZURE
|
+-- Zone 1
|    +-- Infrastructure indépendante
|
+-- Zone 2
|    +-- Infrastructure indépendante
|
+-- Zone 3
     +-- Infrastructure indépendante
```

Une architecture utilisant plusieurs zones peut améliorer la résilience, si le service utilisé prend en charge cette répartition et si l'application est conçue pour fonctionner ainsi.

Attention : déployer une seule machine virtuelle dans une région ne rend pas automatiquement une application hautement disponible.

### 4.4 La paire de régions

Certaines régions Azure sont associées à une autre région dans une relation appelée *region pair*.

Cette association peut jouer un rôle dans certaines stratégies de continuité et de réplication. Elle ne signifie pas que toutes les ressources sont automatiquement répliquées vers l'autre région.

Une stratégie de reprise après sinistre doit préciser les données à répliquer, les services à recréer, le délai de reprise attendu et les procédures de bascule.

### 4.5 Les ressources Azure

Une ressource Azure est un objet administrable dans la plateforme.

Exemples :
- une machine virtuelle ;
- une carte réseau virtuelle ;
- une adresse IP publique ;
- un compte de stockage ;
- un réseau virtuel ;
- une application web ;
- une base de données managée.

Chaque ressource possède un type, un nom, un identifiant, des propriétés et un emplacement lorsque le service en utilise un.

Exemple simplifié d'identifiant :

```text
/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Compute/virtualMachines/<vm-name>
```

Cet identifiant est appelé ID de ressource. Il permet de désigner une ressource de manière structurée.

## 5. Comprendre l'organisation administrative d'Azure

### 5.1 Microsoft Entra ID et le tenant

Microsoft Entra ID est le service d'identité utilisé par Azure pour authentifier les utilisateurs, les groupes, les applications et d'autres identités.

Un tenant Microsoft Entra ID représente une frontière d'identité et d'administration.

Il contient notamment :
- des utilisateurs ;
- des groupes ;
- des applications enregistrées ;
- des principaux de service ;
- des paramètres liés aux identités et aux accès.

Un tenant ne doit pas être confondu avec un abonnement Azure.

### 5.2 L'abonnement Azure

Un abonnement constitue une frontière importante pour l'organisation, la gestion des ressources, les autorisations et la facturation.

Une organisation peut utiliser plusieurs abonnements pour séparer, par exemple :
- les environnements de développement et de production ;
- différentes équipes ;
- différentes entités de facturation ;
- des projets ou des périmètres administratifs.

Un abonnement est associé à un tenant Microsoft Entra ID.

### 5.3 Le groupe de ressources

Un groupe de ressources est un conteneur logique qui rassemble des ressources Azure.

Par exemple, une application web peut utiliser :
- une application web ;
- un compte de stockage ;
- un plan App Service ;
- des ressources de supervision.

Ces ressources peuvent être réunies dans un groupe de ressources si cela correspond à leur cycle de vie et à la manière dont elles doivent être administrées.

Un groupe de ressources possède un emplacement pour ses métadonnées. Cela ne signifie pas que toutes les ressources qu'il contient doivent nécessairement être déployées dans cette même région.

### 5.4 Hiérarchie simplifiée

```text
TENANT MICROSOFT ENTRA ID
|
+-- ABONNEMENT AZURE - DÉVELOPPEMENT
|   |
|   +-- Groupe de ressources : rg-dev-app
|   |   +-- Application web
|   |   +-- Compte de stockage
|   |
|   +-- Groupe de ressources : rg-dev-lab
|       +-- Machine virtuelle de laboratoire
|
+-- ABONNEMENT AZURE - PRODUCTION
    |
    +-- Groupe de ressources : rg-prod-app
        +-- Application web
        +-- Ressources réseau
        +-- Ressources de supervision
```

Les groupes d'administration (*management groups*) permettent d'organiser plusieurs abonnements dans une hiérarchie. Ils seront approfondis dans le niveau expert.

### 5.5 Tableau récapitulatif

| Élément | Rôle principal |
|---|---|
| Tenant | Organiser les identités et les paramètres associés |
| Abonnement | Organiser les ressources, les autorisations et la facturation |
| Groupe de ressources | Regrouper des ressources liées |
| Ressource | Représenter un service ou un composant concret |
| Région | Déterminer la zone géographique d'un service lorsque cela s'applique |

Ne pas confondre ces éléments : ils répondent à des besoins différents.

## 6. Se connecter à Azure

### 6.1 Le portail Azure

Le portail Azure est l'interface graphique d'administration.

Adresse :

https://portal.azure.com/

Il permet notamment de :
- créer des ressources ;
- consulter leur état ;
- modifier leur configuration ;
- gérer certaines autorisations ;
- consulter les métriques et les journaux ;
- visualiser les coûts.

Le portail est utile pour apprendre, mais une infrastructure professionnelle ne doit pas dépendre exclusivement de manipulations manuelles.

### 6.2 Azure Cloud Shell

Azure Cloud Shell est un environnement de terminal accessible depuis le portail Azure.

Il permet d'utiliser notamment Azure CLI et, selon l'environnement choisi, PowerShell.

Il est utile pour démarrer sans installer immédiatement les outils sur son ordinateur.

Attention : Cloud Shell et les services qu'il utilise peuvent avoir leurs propres exigences et coûts. Il faut vérifier les conditions applicables à l'environnement utilisé.

### 6.3 Azure CLI

Azure CLI est un outil en ligne de commande multiplateforme permettant de gérer les ressources Azure.

La commande principale est `az`.

Exemples :

```bash
az account show
az group list --output table
az vm list --output table
```

La documentation officielle est disponible ici :

https://learn.microsoft.com/fr-fr/cli/azure/

### 6.4 Installation d'Azure CLI

Consulter la documentation officielle pour sélectionner la procédure correspondant au système utilisé :

https://learn.microsoft.com/fr-fr/cli/azure/install-azure-cli

Après installation, ouvrir un nouveau terminal si nécessaire et vérifier la disponibilité de la commande :

```bash
az version
```

Si la commande n'est pas reconnue :
1. vérifier que l'installation s'est terminée correctement ;
2. vérifier le chemin d'installation ;
3. rouvrir le terminal ;
4. consulter les instructions propres au système d'exploitation.

### 6.5 Authentification

Pour une utilisation interactive sur un poste de travail :

```bash
az login
```

La procédure peut ouvrir un navigateur pour authentifier l'utilisateur.

Pour afficher le compte et l'abonnement actuellement sélectionnés :

```bash
az account show --output table
```

Pour lister les abonnements accessibles :

```bash
az account list --output table
```

Si plusieurs abonnements sont disponibles, sélectionner explicitement celui qui doit être utilisé :

```bash
az account set --subscription "<SUBSCRIPTION_ID>"
```

Remplacer `<SUBSCRIPTION_ID>` par l'identifiant réel de l'abonnement.

Vérifier ensuite :

```bash
az account show --output json
```

Cette vérification est importante avant toute création ou suppression de ressources.

**Bonne pratique :** ne jamais supposer qu'un terminal est connecté au bon abonnement simplement parce qu'une authentification a réussi.

## 7. Organiser les ressources et les nommer

### 7.1 Pourquoi une convention de nommage ?

Une convention de nommage rend l'infrastructure plus lisible et facilite les recherches, les scripts et la supervision.

Exemple de convention :

```text
<type>-<application>-<environnement>-<region>-<numero>
```

Exemples :

```text
rg-inventaire-dev-weu-001
vnet-inventaire-dev-weu-001
stinventairedev001
```

Les règles de nommage varient selon le type de ressource. Certains caractères sont interdits, certaines longueurs sont limitées et certains noms doivent être uniques à l'échelle d'Azure ou d'un service.

Un nom de compte de stockage, par exemple, suit des contraintes différentes de celles d'un groupe de ressources.

Il faut donc vérifier les règles du service avant d'automatiser la création de noms.

### 7.2 Les tags

Les tags sont des métadonnées sous forme de paires clé-valeur associées aux ressources qui les prennent en charge.

Exemples :

```text
Environment = Dev
Project     = Inventaire
Owner       = PlatformTeam
CostCenter  = CC-100
ManagedBy   = Manual
```

Ils aident à :
- filtrer les ressources ;
- attribuer les coûts à des équipes ou projets ;
- identifier les propriétaires ;
- distinguer les environnements ;
- préparer des politiques de gouvernance.

Les tags ne constituent pas un mécanisme de sécurité. Ils ne remplacent pas les autorisations RBAC.

## 8. Découvrir les principaux services Azure

### 8.1 Les services de calcul

Les services de calcul permettent d'exécuter des systèmes et des applications.

| Service | Utilisation typique |
|---|---|
| Azure Virtual Machines | Exécuter un système d'exploitation et des logiciels sur une machine virtuelle |
| Azure App Service | Héberger des applications web et des API |
| Azure Functions | Exécuter du code déclenché par des événements |
| Azure Container Apps | Exécuter des applications conteneurisées sans gérer directement tous les composants d'un cluster |
| Azure Kubernetes Service (AKS) | Orchestrer des conteneurs avec Kubernetes |

Le choix dépend du niveau de contrôle souhaité et des compétences disponibles.

### 8.2 Les services de stockage

Azure propose plusieurs catégories de stockage.

| Service | Utilisation |
|---|---|
| Azure Blob Storage | Stocker des fichiers, objets, sauvegardes et données non structurées |
| Azure Files | Fournir des partages de fichiers managés |
| Azure Managed Disks | Fournir des disques aux machines virtuelles |
| Azure Queue Storage | Stocker des messages simples dans une file d'attente |
| Azure Table Storage | Stocker des données structurées selon un modèle clé-attribut |

Un compte de stockage Azure peut prendre en charge plusieurs types de services, selon la configuration choisie.

Le stockage doit être choisi selon :
- le type de données ;
- la fréquence d'accès ;
- les performances attendues ;
- les exigences de disponibilité ;
- les règles de rétention ;
- les besoins de sauvegarde ;
- le coût.

### 8.3 Les services réseau

| Service | Fonction |
|---|---|
| Azure Virtual Network (VNet) | Créer un réseau privé virtuel |
| Subnet | Diviser un réseau virtuel en sous-réseaux |
| Network Security Group (NSG) | Filtrer le trafic réseau selon des règles |
| Azure Load Balancer | Distribuer du trafic réseau entre des instances |
| Azure Application Gateway | Fournir notamment des fonctions de répartition du trafic web au niveau applicatif |
| Azure DNS | Héberger et gérer des zones DNS |
| VPN Gateway | Établir certaines connexions VPN entre réseaux |

Ces services seront étudiés plus en profondeur dans le cours intermédiaire.

### 8.4 Les services de données

Azure propose des bases de données managées, notamment :
- Azure SQL Database ;
- Azure Database for PostgreSQL, selon les offres disponibles ;
- Azure Cosmos DB.

Le choix dépend du modèle de données, du moteur, de la cohérence attendue, des performances et des contraintes opérationnelles.

### 8.5 Les services de sécurité et d'administration

Les services et fonctionnalités essentiels comprennent :
- Microsoft Entra ID pour les identités ;
- Azure RBAC pour les autorisations sur les ressources ;
- Azure Key Vault pour la gestion de secrets, de clés et de certificats selon les fonctions utilisées ;
- Azure Monitor pour la supervision ;
- Microsoft Defender for Cloud pour certaines fonctions de posture de sécurité et de protection des charges de travail ;
- Azure Cost Management pour analyser les coûts.

Tous ces services ne sont pas nécessairement activés ou disponibles gratuitement dans chaque abonnement.

## 9. Créer son premier groupe de ressources

Nous allons utiliser Azure CLI pour créer un environnement de laboratoire.

### 9.1 Vérifier l'abonnement

```bash
az account show --output table
```

Si l'abonnement n'est pas le bon, sélectionner le bon identifiant :

```bash
az account set --subscription "<SUBSCRIPTION_ID>"
```

Puis vérifier à nouveau :

```bash
az account show --output table
```

### 9.2 Choisir une région

Afficher les régions disponibles pour l'abonnement :

```bash
az account list-locations --output table
```

Choisir une région adaptée au laboratoire. Le choix doit tenir compte des services disponibles et des éventuelles contraintes de l'abonnement.

Pour les exemples qui suivent, nous utiliserons `westeurope`. Il faut vérifier que la région est utilisable pour les ressources choisies.

### 9.3 Créer le groupe de ressources

```bash
az group create \
  --name rg-azure-lab-dev \
  --location westeurope \
  --tags Environment=Dev Project=AzureLearning
```

La commande crée un groupe de ressources appelé `rg-azure-lab-dev`.

Sous PowerShell, la syntaxe de continuation de ligne diffère. Pour éviter les problèmes, la commande peut être écrite sur une seule ligne :

```powershell
az group create --name rg-azure-lab-dev --location westeurope --tags Environment=Dev Project=AzureLearning
```

### 9.4 Vérifier le résultat

```bash
az group show \
  --name rg-azure-lab-dev \
  --output json
```

Pour afficher les groupes de ressources :

```bash
az group list --output table
```

Pour vérifier les tags :

```bash
az group show \
  --name rg-azure-lab-dev \
  --query tags \
  --output json
```

### 9.5 Comprendre les options

| Option | Rôle |
|---|---|
| `az group create` | Créer ou mettre à jour un groupe de ressources |
| `--name` | Définir son nom |
| `--location` | Définir l'emplacement de ses métadonnées |
| `--tags` | Associer des métadonnées |
| `--output table` | Présenter les résultats sous forme de tableau |
| `--output json` | Présenter les résultats au format JSON |

### 9.6 Pourquoi créer le groupe avant les ressources ?

Le groupe de ressources fournit un périmètre logique pour organiser les ressources d'un projet.

Avant de créer une machine virtuelle, une base de données ou un compte de stockage, il est utile de définir :
- le projet auquel appartient la ressource ;
- l'environnement ;
- le propriétaire ;
- les règles d'accès ;
- la région ;
- les limites de coûts ;
- le cycle de vie.

Cette discipline deviendra particulièrement importante dans les cours intermédiaire et expert.

## 10. Comprendre les machines virtuelles Azure

### 10.1 Qu'est-ce qu'une machine virtuelle ?

Une machine virtuelle Azure est une ressource de calcul qui exécute un système d'exploitation, par exemple Linux ou Windows.

Elle peut héberger :
- un serveur web ;
- un outil d'administration ;
- une application ;
- un service réseau ;
- un environnement de test.

```text
UTILISATEUR
    |
    | Connexion réseau autorisée
    v
+--------------------------------+
| Azure Virtual Machine          |
|                                |
|  Système d'exploitation        |
|       |                        |
|       +-- Serveur web           |
|       +-- Application           |
|       +-- Journaux              |
|                                |
|  Disque du système              |
+--------------------------------+
        |
        +-- Carte réseau virtuelle
        +-- Réseau virtuel
        +-- Règles de filtrage
```

Une machine virtuelle n'est pas simplement un serveur isolé. Elle dépend aussi de ressources de réseau, de stockage, d'identité et d'administration.

### 10.2 Les composants habituels

Une architecture simple peut comprendre :
- une machine virtuelle ;
- un disque de système d'exploitation ;
- une ou plusieurs cartes réseau virtuelles ;
- un réseau virtuel ;
- un sous-réseau ;
- des règles de sécurité réseau ;
- éventuellement une adresse IP publique.

La création de certaines machines virtuelles par Azure CLI peut automatiquement créer des ressources associées. En environnement professionnel, il est souvent préférable de comprendre ces dépendances plutôt que d'accepter aveuglément toutes les valeurs par défaut.

### 10.3 Les tailles de machines virtuelles

Les tailles déterminent notamment les capacités de calcul et de mémoire.

Selon la famille choisie, elles peuvent aussi présenter des caractéristiques différentes en matière de stockage local, de réseau et d'accélération matérielle.

Il ne faut pas choisir une taille uniquement parce qu'elle possède beaucoup de mémoire ou de processeurs.

Il faut examiner :
- la charge applicative ;
- la mémoire consommée ;
- le nombre de connexions ;
- les performances de stockage ;
- les exigences de disponibilité ;
- le coût ;
- les quotas de l'abonnement.

### 10.4 Accès SSH et RDP

Pour Linux, l'administration à distance utilise souvent SSH.

Pour Windows, l'administration utilise fréquemment RDP.

Ces protocoles ne doivent pas être exposés sans protection à l'ensemble d'Internet.

Les bonnes pratiques comprennent :
- limiter les sources réseau autorisées ;
- utiliser des méthodes d'authentification robustes ;
- protéger les clés privées ;
- éviter les mots de passe faibles ;
- privilégier les mécanismes d'accès administratifs adaptés à l'architecture ;
- supprimer les accès temporaires lorsqu'ils ne sont plus nécessaires.

Les règles précises de réseau et les solutions d'accès sécurisé seront approfondies au niveau intermédiaire.

### 10.5 Créer une VM uniquement pour apprendre ?

Une machine virtuelle peut générer des coûts même lorsque personne ne s'y connecte.

L'arrêt du système d'exploitation depuis l'intérieur de la VM ne garantit pas l'arrêt de la facturation de toutes les ressources.

Dans Azure, l'état **Stopped (deallocated)** est généralement important pour comprendre la facturation du calcul d'une VM. Les disques, certaines adresses IP et d'autres ressources associées peuvent continuer à être facturés.

Avant de créer une VM, il faut donc vérifier les prix, les conditions de l'offre, les quotas et la méthode de nettoyage.

## 11. Héberger une application web

### 11.1 Pourquoi utiliser Azure App Service ?

Azure App Service permet d'héberger des applications web et des API sans devoir administrer une machine virtuelle complète pour chaque application.

Le fournisseur gère une partie de la plateforme sous-jacente.

```text
NAVIGATEUR
    |
    | HTTPS
    v
+----------------------------+
| Azure App Service          |
|                            |
|  Plateforme managée        |
|       |                    |
|       +-- Application      |
|       +-- Configuration    |
|       +-- Journaux         |
+----------------------------+
```

Cette solution est souvent plus simple qu'une VM pour un site web classique, mais elle ne convient pas à tous les types d'applications.

### 11.2 Les composants à distinguer

**Application web**

C'est le service qui héberge le code de l'application.

**Plan App Service**

Il définit des caractéristiques importantes de la capacité de calcul, du niveau de service et de la tarification. Plusieurs applications compatibles peuvent partager un plan.

**Configuration de l'application**

Elle peut inclure les paramètres d'exécution, les variables d'environnement et les paramètres de déploiement.

**Nom DNS**

Une application web peut être accessible par un nom DNS fourni par Azure. Un nom de domaine personnalisé peut être configuré séparément.

### 11.3 Choisir entre VM et App Service

| Besoin | Choix souvent adapté |
|---|---|
| Contrôler finement le système d'exploitation | Machine virtuelle |
| Héberger rapidement une application web standard | App Service |
| Exécuter un code en réponse à des événements | Azure Functions |
| Orchestrer des conteneurs Kubernetes | AKS |
| Exécuter des conteneurs avec une gestion de plateforme simplifiée | Azure Container Apps |

Le bon choix dépend du besoin, pas seulement de la popularité du service.

## 12. Comprendre le réseau Azure

### 12.1 Réseau virtuel

Un Azure Virtual Network, ou VNet, est un réseau privé virtuel dans lequel les ressources peuvent communiquer selon la configuration réseau.

Il permet d'organiser les adresses IP et de définir des connexions avec d'autres réseaux.

### 12.2 Sous-réseaux

Un sous-réseau est une subdivision d'un réseau IP.

Exemple conceptuel :

```text
VNet : 10.10.0.0/16
|
+-- Subnet-Web : 10.10.1.0/24
|
+-- Subnet-App : 10.10.2.0/24
|
+-- Subnet-Data : 10.10.3.0/24
```

Les plages sont des exemples pédagogiques. Une architecture réelle doit éviter les chevauchements d'adresses avec les réseaux locaux ou les autres réseaux interconnectés.

Les exigences exactes varient aussi selon le service Azure utilisé.

### 12.3 Groupes de sécurité réseau

Un Network Security Group, ou NSG, contient des règles de sécurité réseau qui contrôlent certains flux entrants et sortants.

Une règle peut comporter :
- une priorité ;
- une source ;
- une destination ;
- un protocole ;
- un port ou une plage de ports ;
- une action d'autorisation ou de refus.

Exemple conceptuel :

```text
RÈGLE NSG
|
+-- Source : plage IP autorisée
+-- Destination : ressource ou sous-réseau concerné
+-- Protocole : TCP
+-- Port : 443
+-- Action : Allow
```

Une règle d'autorisation ne garantit pas à elle seule que le service est accessible : le service doit écouter sur le port concerné et les autres éléments du chemin réseau doivent être correctement configurés.

### 12.4 Réseau public et réseau privé

Une ressource disposant d'une adresse IP publique n'est pas automatiquement accessible : les règles réseau et les paramètres du service comptent aussi.

Inversement, une ressource privée peut être accessible depuis d'autres ressources ou réseaux autorisés.

Le principe fondamental est de n'autoriser que les communications nécessaires.

Les notions de VNet, de sous-réseaux, de routage, de DNS, de VPN et de filtrage seront détaillées dans le cours Azure intermédiaire.

## 13. Découvrir le stockage Azure

### 13.1 Compte de stockage

Un compte de stockage Azure est une ressource qui fournit des services de stockage compatibles avec sa configuration.

Il ne faut pas le confondre avec un disque de machine virtuelle.

### 13.2 Blob Storage

Blob Storage permet de stocker des objets tels que :
- des documents ;
- des images ;
- des archives ;
- des fichiers d'export ;
- des sauvegardes ;
- des données applicatives non structurées.

Les données sont généralement organisées dans des conteneurs et des blobs.

### 13.3 Disques de machines virtuelles

Les Managed Disks fournissent des disques utilisés par les machines virtuelles.

Ils servent notamment à stocker le système d'exploitation et les données de la VM.

Leur cycle de vie et leur facturation doivent être examinés séparément de ceux de la machine virtuelle.

### 13.4 Redondance

Azure propose différents mécanismes de redondance selon le service de stockage et la configuration.

La redondance locale, zonale ou géographique n'offre pas exactement les mêmes garanties ni les mêmes coûts.

Une copie redondante ne remplace pas systématiquement une sauvegarde : une suppression ou une corruption peut être propagée selon le mécanisme utilisé.

Avant de choisir une option, il faut déterminer :
- la durée de conservation des données ;
- les pertes de données acceptables ;
- le délai de restauration ;
- le risque de panne locale ou régionale ;
- le coût de la solution.

## 14. Identités et autorisations

### 14.1 Authentification et autorisation

Ces deux notions doivent être distinguées.

**Authentification :** déterminer quelle identité se présente.

**Autorisation :** déterminer ce que cette identité a le droit de faire.

Exemple :

```text
Administrateur
      |
      v
Authentification
      |
      v
Identité reconnue
      |
      v
Évaluation des autorisations
      |
      +-- Lire les ressources : autorisé
      |
      +-- Créer une VM : selon les rôles
      |
      +-- Modifier les autorisations : selon les rôles
```

Une connexion réussie ne signifie pas que toutes les opérations sont autorisées.

### 14.2 Azure RBAC

Azure Role-Based Access Control permet d'attribuer des rôles à des identités à différents niveaux de portée.

Les rôles courants comprennent :

**Reader**

Permet de consulter les ressources sans leur accorder les permissions générales de modification.

**Contributor**

Permet de gérer de nombreuses ressources, mais ne donne pas, par défaut, le droit général de gérer les attributions de rôles.

**Owner**

Permet une gestion étendue des ressources et des attributions d'accès au périmètre concerné.

Les permissions exactes dépendent du rôle et de la portée.

### 14.3 Portée des autorisations

Les rôles peuvent être attribués à différents niveaux, notamment :
- management group ;
- abonnement ;
- groupe de ressources ;
- ressource individuelle.

Une autorisation attribuée à un niveau supérieur peut être héritée par les niveaux inférieurs, selon les règles applicables.

Il faut donc éviter d'attribuer un rôle trop large lorsqu'un accès limité suffit.

### 14.4 Principe du moindre privilège

Le moindre privilège consiste à accorder uniquement les permissions nécessaires à une tâche.

Exemple :

```text
MAUVAISE APPROCHE
Tous les développeurs
        |
        v
Owner sur tout l'abonnement


MEILLEURE APPROCHE
Développeur
    |
    +-- Accès nécessaire aux ressources de développement
    |
    +-- Lecture des ressources partagées utiles
    |
    +-- Aucun droit d'administration global inutile
```

Le contrôle des accès est un sujet central de sécurité et sera approfondi dans les cours suivants.

Documentation officielle Azure RBAC :

https://learn.microsoft.com/en-us/azure/role-based-access-control/

## 15. Sécurité : les premières règles indispensables

### 15.1 Protéger le compte

Le compte utilisé pour administrer Azure donne potentiellement accès à des ressources sensibles.

Il faut :
- activer l'authentification multifacteur lorsque cela est applicable ;
- utiliser des méthodes d'authentification robustes ;
- protéger les comptes privilégiés ;
- limiter le nombre de comptes administrateurs ;
- éviter le partage de comptes ;
- contrôler régulièrement les permissions ;
- protéger les méthodes de récupération de compte.

### 15.2 Ne pas exposer inutilement les services

Les ports d'administration ne doivent pas être ouverts à tout Internet sans raison.

Exemples de ports sensibles :
- TCP 22 pour SSH ;
- TCP 3389 pour RDP ;
- TCP 3306 pour MySQL ;
- TCP 5432 pour PostgreSQL ;
- TCP 1433 pour SQL Server.

Ces numéros sont des ports courants, mais leur présence seule ne signifie pas qu'un service écoute sur ces ports.

La bonne approche consiste à limiter les sources, à utiliser des accès sécurisés et à éviter l'exposition publique des services internes.

### 15.3 Protéger les secrets

Les mots de passe, clés privées, jetons et chaînes de connexion ne doivent pas être publiés dans un dépôt Git ou placés dans des scripts partagés sans protection.

Pour les usages appropriés, Azure Key Vault permet de gérer des secrets, des clés et des certificats.

Il faut également limiter les personnes et les services capables de consulter ces éléments.

### 15.4 Séparer les environnements

Les environnements de développement, de test et de production n'ont pas les mêmes besoins.

Une erreur commise en développement ne devrait pas permettre de supprimer accidentellement des ressources de production.

Les séparations possibles incluent :
- des abonnements distincts ;
- des groupes de ressources distincts ;
- des permissions différentes ;
- des identités de déploiement séparées ;
- des politiques de contrôle adaptées.

Le choix dépend de l'organisation et sera développé au niveau expert.

### 15.5 Sauvegarde et restauration

Une stratégie de sauvegarde doit définir :
- les données à protéger ;
- la fréquence des sauvegardes ;
- la durée de conservation ;
- les responsables ;
- les droits d'accès ;
- les objectifs de restauration ;
- la procédure de test.

Une sauvegarde qui n'a jamais été restaurée lors d'un test ne garantit pas que la restauration fonctionnera le jour d'un incident.

## 16. Maîtriser les coûts Azure

### 16.1 Pourquoi une ressource peut-elle coûter de l'argent ?

Le coût peut dépendre :
- de la durée d'exécution ;
- de la capacité de calcul ;
- du volume de stockage ;
- des opérations réalisées ;
- du trafic réseau ;
- des sauvegardes ;
- du niveau de service ;
- de la région ;
- des options de redondance.

Les conditions varient selon les services et les contrats.

### 16.2 Gratuit ne signifie pas sans risque

Certaines offres proposent des crédits ou des quotas gratuits sous certaines conditions.

Il ne faut jamais supposer qu'un service restera gratuit sans vérifier :
- les limites de l'offre ;
- la durée de validité ;
- les services inclus ;
- les quotas ;
- les tarifs au-delà des limites ;
- les ressources associées facturables.

### 16.3 Les outils de contrôle des coûts

Azure Cost Management permet notamment d'analyser les dépenses et de suivre leur évolution.

Les budgets peuvent servir à suivre des dépenses prévues et à déclencher des alertes.

Un budget ou une alerte ne doit pas être considéré comme un arrêt automatique garanti de toutes les ressources. Les mécanismes de contrôle doivent être configurés et testés selon le besoin.

### 16.4 Bonnes pratiques financières

1. Créer un groupe de ressources dédié aux laboratoires.
2. Utiliser des noms et des tags cohérents.
3. Éviter les machines virtuelles surdimensionnées.
4. Examiner les disques, adresses IP et autres ressources associées.
5. Supprimer les ressources temporaires lorsqu'elles ne sont plus utiles.
6. Contrôler régulièrement les coûts.
7. Définir des alertes adaptées.
8. Vérifier la tarification avant les travaux pratiques.
9. Ne jamais stocker de données importantes dans un environnement de laboratoire sans stratégie de protection.
10. Vérifier les conséquences d'une suppression avant de l'exécuter.

Documentation officielle sur Cost Management :

https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management

## 17. Travaux pratiques : créer et gérer un environnement Azure

### 17.1 Objectif

Créer un environnement de laboratoire, vérifier son état, appliquer des tags, examiner les ressources et nettoyer l'environnement à la fin.

Ce TP utilise Azure CLI. Il nécessite un compte et un abonnement permettant de créer des groupes de ressources.

Il ne nécessite pas la création d'une machine virtuelle ni d'une base de données payante.

### 17.2 Étape 1 : vérifier la connexion

```bash
az login
az account show --output table
az account list --output table
```

Si plusieurs abonnements sont accessibles, sélectionner celui destiné au laboratoire.

```bash
az account set --subscription "<SUBSCRIPTION_ID>"
az account show --output table
```

### 17.3 Étape 2 : choisir la région

```bash
az account list-locations --output table
```

Sélectionner une région adaptée à l'environnement et aux ressources envisagées.

Pour ce TP, la suite utilise `westeurope`.

### 17.4 Étape 3 : créer le groupe de ressources

```bash
az group create \
  --name rg-azure-lab-dev \
  --location westeurope \
  --tags Environment=Dev Project=AzureLearning Owner=Student
```

### 17.5 Étape 4 : vérifier le groupe

```bash
az group show \
  --name rg-azure-lab-dev \
  --output json
```

Vérifier :
- le nom ;
- l'emplacement ;
- l'état de provisionnement ;
- les tags.

### 17.6 Étape 5 : examiner les ressources du groupe

```bash
az resource list \
  --resource-group rg-azure-lab-dev \
  --output table
```

Le résultat peut être vide : c'est normal, car nous n'avons créé que le groupe de ressources.

### 17.7 Étape 6 : ajouter ou modifier un tag

```bash
az tag update \
  --resource-id "$(az group show --name rg-azure-lab-dev --query id --output tsv)" \
  --operation Merge \
  --tags Training=AzureBeginner
```

Cette commande illustre l'utilisation des tags avec l'API de gestion des ressources. La prise en charge et le comportement des tags peuvent dépendre du type de ressource.

Vérifier le résultat :

```bash
az group show \
  --name rg-azure-lab-dev \
  --query tags \
  --output json
```

### 17.8 Étape 7 : afficher l'ID du groupe

```bash
az group show \
  --name rg-azure-lab-dev \
  --query id \
  --output tsv
```

Cet identifiant peut servir à référencer le groupe dans d'autres commandes et scripts.

### 17.9 Étape 8 : supprimer le laboratoire

**Attention :** la suppression d'un groupe de ressources supprime également les ressources qu'il contient. Cette opération peut entraîner une perte de données et des interruptions.

Avant toute suppression, vérifier le compte, l'abonnement, le nom et le contenu du groupe.

```bash
az account show --output table

az resource list \
  --resource-group rg-azure-lab-dev \
  --output table
```

Si le groupe est bien le laboratoire à supprimer et qu'aucune ressource utile ne doit être conservée :

```bash
az group delete \
  --name rg-azure-lab-dev \
  --yes \
  --no-wait
```

L'option `--no-wait` permet à la commande de retourner sans attendre la fin de l'opération. La suppression peut donc continuer en arrière-plan.

Vérifier ensuite l'état du groupe :

```bash
az group exists --name rg-azure-lab-dev
```

Un résultat `false` signifie que le groupe n'existe plus. Si la suppression est encore en cours, il peut être nécessaire de patienter et de vérifier à nouveau.

### 17.10 Résultat attendu

À la fin du TP, il faut savoir :
- s'authentifier auprès d'Azure ;
- identifier l'abonnement actif ;
- choisir une région ;
- créer un groupe de ressources ;
- lire les propriétés d'une ressource ;
- utiliser des tags ;
- afficher les ressources d'un groupe ;
- supprimer un environnement de laboratoire en connaissance de cause.

## 18. Travaux pratiques complémentaires : comprendre le stockage

Ce TP est facultatif. Il crée un compte de stockage, ressource susceptible d'entraîner des coûts. Consulter la tarification et supprimer le compte à la fin si aucun élément ne doit être conservé.

### 18.1 Vérifier le groupe de ressources

Le groupe `rg-azure-lab-dev` doit exister.

S'il a été supprimé lors du TP précédent, le recréer :

```bash
az group create \
  --name rg-azure-lab-dev \
  --location westeurope \
  --tags Environment=Dev Project=AzureLearning
```

### 18.2 Choisir un nom de compte

Le nom d'un compte de stockage doit respecter les règles du service, notamment l'unicité globale et les contraintes de caractères.

Choisir un nom disponible et conforme. Dans les commandes suivantes, remplacer `stazurelab12345` par un nom réellement disponible.

### 18.3 Créer le compte

```bash
az storage account create \
  --name stazurelab12345 \
  --resource-group rg-azure-lab-dev \
  --location westeurope \
  --sku Standard_LRS \
  --kind StorageV2
```

Cette configuration est un exemple de laboratoire. Le choix de la redondance doit être adapté au besoin réel.

### 18.4 Vérifier le compte

```bash
az storage account show \
  --name stazurelab12345 \
  --resource-group rg-azure-lab-dev \
  --output table
```

### 18.5 Comprendre les paramètres

| Paramètre | Signification |
|---|---|
| `--name` | Nom du compte de stockage |
| `--resource-group` | Groupe de ressources associé |
| `--location` | Région de déploiement |
| `--sku` | Référence de performance et de redondance choisie |
| `--kind` | Type de compte de stockage |

### 18.6 Nettoyer le laboratoire

Vérifier d'abord que le groupe ne contient que les ressources de test.

```bash
az resource list \
  --resource-group rg-azure-lab-dev \
  --output table
```

Si le compte et le groupe ne contiennent rien à conserver, supprimer le groupe de ressources comme indiqué dans le TP précédent.

## 19. Diagnostiquer les problèmes courants

### 19.1 `az` n'est pas reconnu

**Symptôme :**

Le terminal indique que la commande `az` est inconnue.

**Causes possibles :**
- Azure CLI n'est pas installé ;
- le terminal n'a pas été redémarré ;
- le chemin d'installation n'est pas accessible.

**Actions :**
1. vérifier l'installation ;
2. consulter la procédure officielle correspondant au système ;
3. ouvrir un nouveau terminal ;
4. exécuter `az version`.

### 19.2 L'authentification échoue

**Causes possibles :**
- problème de navigateur ;
- session expirée ;
- restrictions d'organisation ;
- compte non autorisé ;
- problème d'accès au tenant.

**Actions :**
1. vérifier le compte utilisé ;
2. exécuter `az login` ;
3. examiner les messages d'erreur ;
4. vérifier que le compte a accès à l'abonnement ;
5. contacter l'administrateur de l'organisation si nécessaire.

Ne jamais contourner les contrôles d'accès d'une organisation pour résoudre un problème d'authentification.

### 19.3 Aucun abonnement n'apparaît

Un utilisateur peut être authentifié sans disposer d'un abonnement utilisable pour créer des ressources.

Vérifier :

```bash
az account list --output table
```

Il faut qu'un abonnement adapté soit accessible et que l'utilisateur possède les permissions nécessaires.

### 19.4 Accès refusé lors de la création d'une ressource

**Causes possibles :**
- rôle insuffisant ;
- mauvais abonnement ;
- restriction de politique ;
- fournisseur de ressources non enregistré ;
- quota ou restriction de région ;
- règle d'organisation.

Vérifier le contexte :

```bash
az account show --output json
```

Puis examiner le message d'erreur et la portée des autorisations. Ne pas attribuer systématiquement un rôle Owner pour résoudre un refus d'accès.

### 19.5 Région non prise en charge

Un service ou une taille de machine peut ne pas être disponible dans la région choisie.

Vérifier la liste des régions, la documentation du service et les quotas de l'abonnement.

Une autre région peut convenir, mais il faut tenir compte de la résidence des données, des performances, des coûts et des exigences de continuité.

### 19.6 Une ressource continue à coûter de l'argent

Les ressources associées peuvent rester facturées après l'arrêt d'une machine virtuelle.

Examiner :
- les machines virtuelles ;
- les disques ;
- les adresses IP ;
- les comptes de stockage ;
- les sauvegardes ;
- les services de supervision ;
- les ressources réseau ;
- les autres services encore actifs.

Le nettoyage doit être réalisé à partir d'un inventaire, et non en supprimant des ressources au hasard.

## 20. Exercices corrigés

### Exercice 1 : choisir un modèle de service

Une équipe souhaite héberger une API web. Elle veut limiter l'administration du système d'exploitation et se concentrer sur son code.

Quel modèle est souvent le plus adapté entre IaaS et PaaS ?

**Correction :**

Le PaaS est généralement un bon candidat, par exemple Azure App Service si les caractéristiques de l'application sont compatibles. L'équipe conserve la responsabilité de son code, de ses données, de sa configuration et de ses accès.

Une machine virtuelle IaaS peut être préférable si l'application exige un contrôle du système d'exploitation ou des dépendances spécifiques.

### Exercice 2 : distinguer tenant et abonnement

Une entreprise utilise un tenant Microsoft Entra ID et deux abonnements Azure, l'un pour le développement et l'autre pour la production.

Les deux abonnements sont-ils nécessairement deux tenants différents ?

**Correction :**

Non. Plusieurs abonnements peuvent être associés au même tenant. La séparation des abonnements et la séparation des identités sont deux décisions distinctes.

### Exercice 3 : comprendre un groupe de ressources

Un groupe de ressources contient une application web et un compte de stockage.

Peut-on considérer que le groupe de ressources est lui-même une machine virtuelle ?

**Correction :**

Non. Le groupe est un conteneur logique de gestion. L'application web et le compte de stockage sont des ressources distinctes.

### Exercice 4 : interpréter une autorisation

Un utilisateur dispose du rôle Reader sur un groupe de ressources. Peut-il normalement créer une nouvelle machine virtuelle dans ce groupe ?

**Correction :**

Non. Reader permet de consulter les ressources, mais n'accorde pas les autorisations générales de création ou de modification. Il faut un rôle adapté à l'opération et à la portée concernée.

### Exercice 5 : éviter une dépense inutile

Une VM de laboratoire n'est plus utilisée. Son système d'exploitation a été arrêté, mais des coûts apparaissent encore.

Quelle est la première démarche ?

**Correction :**

Vérifier l'état de la VM dans Azure, notamment si elle est arrêtée et désallouée, puis examiner les ressources associées et leur facturation. Les disques, adresses IP et autres composants peuvent continuer à générer des coûts.

### Exercice 6 : choisir une région

Une application traite des données soumises à des contraintes de résidence. Peut-on choisir une région uniquement parce qu'elle est la moins chère ?

**Correction :**

Non. La conformité, les exigences de traitement des données, la disponibilité des services, les performances et la continuité doivent être examinées avant de comparer les coûts.

### Exercice 7 : identifier le risque réseau

Une base de données interne n'a besoin d'être accessible que par une application privée. Est-il judicieux d'exposer directement son port à tout Internet ?

**Correction :**

Non. Il faut privilégier un accès privé et restreindre les communications aux sources autorisées. Les détails de la conception réseau seront approfondis dans le cours intermédiaire.

### Exercice 8 : comprendre les tags

Une ressource porte le tag `Environment=Production`. Cela garantit-il que seuls les administrateurs de production peuvent la modifier ?

**Correction :**

Non. Un tag est une métadonnée. Il ne crée pas automatiquement une règle d'autorisation. Les accès doivent être contrôlés par les mécanismes d'identité et d'autorisation, notamment Azure RBAC.

### Exercice 9 : vérifier le contexte CLI

Quelle commande permet d'afficher l'abonnement actuellement sélectionné ?

**Correction :**

```bash
az account show --output table
```

Cette vérification est particulièrement importante avant une opération destructive.

### Exercice 10 : supprimer un groupe

Pourquoi faut-il examiner les ressources avant d'exécuter `az group delete` ?

**Correction :**

La suppression d'un groupe de ressources supprime les ressources qu'il contient. Il faut vérifier le périmètre, l'abonnement et les données avant d'effectuer cette opération.

## 21. Projet final : déployer et documenter un environnement de laboratoire Azure

### 21.1 Contexte

Une petite entreprise souhaite commencer à utiliser Azure pour organiser ses environnements techniques.

Le projet consiste à créer un périmètre de laboratoire propre, documenté et facile à nettoyer.

Aucune VM n'est nécessaire pour valider les objectifs de base.

### 21.2 Objectifs

Le projet doit :
- utiliser Azure CLI ;
- vérifier l'abonnement avant toute opération ;
- créer un groupe de ressources ;
- appliquer des tags cohérents ;
- documenter la région choisie ;
- afficher l'identifiant du groupe ;
- inventorier les ressources ;
- expliquer les autorisations nécessaires ;
- décrire les risques de coûts ;
- prévoir une procédure de suppression.

### 21.3 Arborescence de livrables

```text
projet-azure-debutant/
|
+-- README.md
|
+-- scripts/
|   +-- create-lab.sh
|   +-- inspect-lab.sh
|   +-- cleanup-lab.sh
|
+-- documentation/
    +-- architecture.md
    +-- securite.md
    +-- couts.md
```

Les scripts sont des exemples de structure. Ils doivent être adaptés au système utilisé et testés dans un abonnement autorisé.

### 21.4 Exemple de script de création

Fichier `scripts/create-lab.sh` :

```bash
#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="rg-azure-lab-dev"
LOCATION="westeurope"

echo "Compte Azure actif :"
az account show --output table

echo
echo "Vérification du groupe existant..."

if az group exists --name "$RESOURCE_GROUP" --output tsv | grep -qx true; then
  echo "Le groupe existe déjà : $RESOURCE_GROUP"
  echo "Vérifiez son contenu avant de poursuivre."
  exit 1
fi

echo "Création du groupe de ressources..."

az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --tags Environment=Dev Project=AzureLearning ManagedBy=CLI

echo
echo "Groupe créé. Détails :"

az group show \
  --name "$RESOURCE_GROUP" \
  --output table
```

Ce script :
- arrête l'exécution en cas d'erreur ;
- affiche le contexte Azure ;
- évite de poursuivre si le groupe existe déjà ;
- crée un groupe de ressources avec des tags ;
- affiche le résultat.

Le script ne peut pas déterminer à lui seul si l'abonnement sélectionné est le bon pour chaque utilisateur. Dans un contexte professionnel, il faut ajouter une vérification explicite de l'identifiant d'abonnement attendu.

### 21.5 Exemple de script d'inspection

Fichier `scripts/inspect-lab.sh` :

```bash
#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="rg-azure-lab-dev"

echo "Contexte Azure :"
az account show --output table

echo
echo "Détails du groupe :"
az group show \
  --name "$RESOURCE_GROUP" \
  --output json

echo
echo "Ressources du groupe :"
az resource list \
  --resource-group "$RESOURCE_GROUP" \
  --output table
```

Ce script permet de vérifier le contexte et le contenu du laboratoire avant toute opération importante.

### 21.6 Exemple de script de nettoyage sécurisé

Fichier `scripts/cleanup-lab.sh` :

```bash
#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="rg-azure-lab-dev"

echo "Compte Azure actif :"
az account show --output table

echo
echo "Ressources présentes :"
az resource list \
  --resource-group "$RESOURCE_GROUP" \
  --output table

echo
echo "ATTENTION : la suppression du groupe supprime ses ressources."
read -r -p "Tapez exactement DELETE-LAB pour confirmer : " CONFIRMATION

if [[ "$CONFIRMATION" != "DELETE-LAB" ]]; then
  echo "Suppression annulée."
  exit 1
fi

az group delete \
  --name "$RESOURCE_GROUP" \
  --yes \
  --no-wait

echo "Demande de suppression envoyée."
echo "Vérifiez son état avant de considérer le nettoyage terminé."
```

Cette confirmation interactive réduit le risque d'une suppression involontaire, mais ne remplace pas la vérification de l'abonnement, du groupe et de ses ressources.

Pour une utilisation réelle, il faut aussi empêcher le script d'opérer sur un abonnement inattendu.

### 21.7 Critères de validation

Le projet est validé si :
- l'authentification est fonctionnelle ;
- l'abonnement actif a été vérifié ;
- le groupe de ressources a été créé ;
- les tags sont visibles ;
- les ressources peuvent être inventoriées ;
- les commandes sont documentées ;
- les risques de coûts sont identifiés ;
- le nettoyage est expliqué et exécuté uniquement après vérification.

### 21.8 Améliorations possibles

Pour préparer le niveau intermédiaire :
- déployer un compte de stockage ;
- créer une application web ;
- automatiser le déploiement dans un pipeline ;
- ajouter des contrôles d'accès adaptés ;
- configurer la supervision ;
- définir une convention de nommage complète ;
- commencer à décrire l'infrastructure sous forme de code.

Ces extensions seront développées progressivement dans les cours suivants.

## 22. Bonnes pratiques à retenir

### Administration

- Vérifier l'abonnement avant de créer ou supprimer une ressource.
- Utiliser des groupes de ressources cohérents.
- Appliquer des conventions de nommage.
- Utiliser des tags utiles et compréhensibles.
- Inventorier les ressources avant un nettoyage.

### Sécurité

- Protéger les comptes privilégiés.
- Appliquer le moindre privilège.
- Limiter les accès réseau.
- Protéger les secrets.
- Séparer les environnements selon les besoins.
- Tester les procédures de sauvegarde et de restauration.

### Finances

- Vérifier la tarification avant un laboratoire.
- Examiner les ressources associées aux machines virtuelles.
- Mettre en place une surveillance des dépenses.
- Ne pas supposer qu'un budget arrête automatiquement les ressources.
- Supprimer les ressources temporaires après vérification.

### Exploitation

- Lire les messages d'erreur au lieu de multiplier les commandes au hasard.
- Utiliser Azure CLI pour rendre les opérations reproductibles.
- Documenter les procédures.
- Tester les scripts sur un périmètre limité.
- Ne pas exposer de secrets dans les dépôts ou les journaux.
- Ne pas considérer qu'un déploiement réussi garantit la sécurité ou la disponibilité.

## 23. Glossaire

**Azure** : plateforme cloud de Microsoft.

**Cloud computing** : utilisation de ressources informatiques accessibles à la demande par un réseau.

**IaaS** : modèle de service fournissant des ressources d'infrastructure.

**PaaS** : modèle fournissant une plateforme managée pour exécuter des applications.

**SaaS** : modèle fournissant un logiciel prêt à l'emploi.

**Région** : zone géographique Azure dans laquelle certains services sont déployés.

**Zone de disponibilité** : domaine d'infrastructure distinct au sein d'une région, utilisé pour améliorer la résilience lorsque le service le prend en charge.

**Tenant** : instance Microsoft Entra ID organisant les identités et les paramètres associés.

**Abonnement** : périmètre Azure d'organisation des ressources, des accès et de la facturation.

**Groupe de ressources** : conteneur logique pour des ressources Azure liées.

**Ressource** : instance administrable d'un service Azure.

**Azure CLI** : outil en ligne de commande permettant d'administrer Azure.

**VNet** : réseau virtuel Azure.

**Subnet** : subdivision d'un réseau IP.

**NSG** : groupe de sécurité réseau contenant des règles de filtrage.

**Azure RBAC** : système de contrôle d'accès basé sur les rôles.

**Microsoft Entra ID** : service d'identité et d'accès de Microsoft.

**Azure Blob Storage** : service de stockage d'objets.

**Azure App Service** : plateforme managée d'hébergement d'applications web et d'API.

**Azure Virtual Machines** : service de machines virtuelles.

**Tag** : paire clé-valeur associée à une ressource pour faciliter son organisation.

**Moindre privilège** : principe qui consiste à n'accorder que les permissions nécessaires.

**Désallocation** : état dans lequel une machine virtuelle a été libérée des ressources de calcul selon le modèle Azure ; certains composants associés peuvent toujours être facturés.

**Gouvernance cloud** : ensemble des règles et contrôles qui encadrent la création, l'utilisation, la sécurité et les coûts des ressources cloud.

## 24. Documentation officielle

Les références suivantes constituent les sources principales pour approfondir les notions du cours.

### Fondamentaux Azure

- Composants fondamentaux de l'architecture Azure :  
  https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/

- Documentation générale Azure :  
  https://learn.microsoft.com/fr-fr/azure/

- Liste des régions Azure :  
  https://learn.microsoft.com/azure/reliability/regions-list

### Azure CLI et gestion des ressources

- Installer Azure CLI :  
  https://learn.microsoft.com/fr-fr/cli/azure/install-azure-cli

- Documentation Azure CLI :  
  https://learn.microsoft.com/fr-fr/cli/azure/

- Gérer les groupes de ressources avec Azure CLI :  
  https://learn.microsoft.com/fr-fr/azure/azure-resource-manager/management/manage-resource-groups-cli

- Créer une machine virtuelle Linux avec Azure CLI :  
  https://learn.microsoft.com/fr-fr/azure/virtual-machines/linux/create-cli-complete

### Identités et sécurité

- Documentation Azure RBAC :  
  https://learn.microsoft.com/en-us/azure/role-based-access-control/

- Microsoft Entra ID :  
  https://learn.microsoft.com/en-us/entra/

### Coûts

- Présentation d'Azure Cost Management :  
  https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management

- Comprendre les portées de gestion des coûts :  
  https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/understand-work-scopes

## 25. Validation des acquis et passage au niveau suivant

Avant de passer au cours intermédiaire, il faut pouvoir répondre sans aide aux questions suivantes :

1. Quelle est la différence entre IaaS, PaaS et SaaS ?
2. Quelle est la différence entre un tenant et un abonnement ?
3. À quoi sert un groupe de ressources ?
4. Pourquoi une région doit-elle être choisie avec soin ?
5. À quoi servent les zones de disponibilité ?
6. Comment vérifier l'abonnement actif dans Azure CLI ?
7. Comment créer et examiner un groupe de ressources ?
8. Quelle est la différence entre authentification et autorisation ?
9. Pourquoi Azure RBAC est-il important ?
10. Pourquoi une machine virtuelle arrêtée peut-elle encore entraîner des coûts ?
11. Pourquoi une sauvegarde doit-elle être testée ?
12. Pourquoi les tags ne remplacent-ils pas les contrôles d'accès ?

Le passage au niveau intermédiaire suppose aussi d'avoir réalisé le TP de création et de nettoyage, ou d'être capable d'expliquer chacune de ses étapes.

Le cours suivant, `cloud-azure-intermediaire.md`, s'appuiera sur ces fondations pour construire des environnements plus complets : réseaux virtuels et sous-réseaux, filtrage du trafic, connectivité, stockage, identités, supervision, automatisation et déploiement de services en combinant plusieurs ressources.