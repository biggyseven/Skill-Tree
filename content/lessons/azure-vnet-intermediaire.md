# Azure Virtual Network (VNet) — Cours complet de niveau intermédiaire

**Fichier :** `azure-vnet-intermediaire.md`  
**Domaine :** Réseaux cloud, architecture Azure et sécurité réseau  
**Niveau :** Intermédiaire  
**Durée indicative :** 12 à 18 heures, ateliers compris  
**Prérequis :** Connaître IPv4/CIDR, sous-réseaux, routage, ports TCP/UDP, DNS, NSG, VNet et sous-réseaux Azure.  
**Méthode :** Cours théorique, schémas textuels, exemples, ateliers guidés, commandes Azure CLI, exercices corrigés et challenge final.

> **Objectif pédagogique :** savoir concevoir, déployer, sécuriser, observer et dépanner une architecture Azure composée de plusieurs réseaux virtuels, d'un réseau central (hub), de réseaux satellites (spokes), de routes personnalisées, de services privés et d'une connectivité hybride.
>
> **Tout le cours est contenu dans ce fichier.** Le challenge final et sa correction se trouvent à la fin ; aucun document séparé n'est nécessaire.


# SOMMAIRE

1. [Positionnement du niveau intermédiaire](#1-positionnement-du-niveau-intermédiaire)
2. [Architecture de référence et plan d'adressage](#2-architecture-de-référence-et-plan-dadressage)
3. [Concevoir un plan CIDR qui évolue](#3-concevoir-un-plan-cidr-qui-évolue)
4. [Routage Azure : routes système, UDR et choix du prochain saut](#4-routage-azure--routes-système-udr-et-choix-du-prochain-saut)
5. [Architecture hub-and-spoke](#5-architecture-hub-and-spoke)
6. [VNet Peering et transit](#6-vnet-peering-et-transit)
7. [NSG, ASG et segmentation des flux](#7-nsg-asg-et-segmentation-des-flux)
8. [Azure Firewall et appliances réseau](#8-azure-firewall-et-appliances-réseau)
9. [Sortie Internet contrôlée et routage forcé](#9-sortie-internet-contrôlée-et-routage-forcé)
10. [Private Link, Private Endpoint et Service Endpoint](#10-private-link-private-endpoint-et-service-endpoint)
11. [DNS privé et résolution entre réseaux](#11-dns-privé-et-résolution-entre-réseaux)
12. [Connectivité hybride : VPN Gateway et ExpressRoute](#12-connectivité-hybride--vpn-gateway-et-expressroute)
13. [BGP et Azure Route Server](#13-bgp-et-azure-route-server)
14. [IPv6 et dual-stack](#14-ipv6-et-dual-stack)
15. [Supervision et observabilité réseau](#15-supervision-et-observabilité-réseau)
16. [Méthode de dépannage structurée](#16-méthode-de-dépannage-structurée)
17. [Automatisation avec Azure CLI et Bicep](#17-automatisation-avec-azure-cli-et-bicep)
18. [Coûts, disponibilité et bonnes pratiques d'exploitation](#18-coûts-disponibilité-et-bonnes-pratiques-dexploitation)
19. [Ateliers guidés](#19-ateliers-guidés)
20. [Exercices de compréhension et corrections](#20-exercices-de-compréhension-et-corrections)
21. [Challenge final — Architecture Azure sécurisée](#21-challenge-final--architecture-azure-sécurisée)
22. [Correction du challenge final](#22-correction-du-challenge-final)
23. [Checklist finale](#23-checklist-finale)
24. [Glossaire et documentation officielle](#24-glossaire-et-documentation-officielle)


# 1. Positionnement du niveau intermédiaire

## 1.1. Ce que l'on doit déjà maîtriser

Au niveau débutant, on a appris à créer un VNet, à définir des sous-réseaux, à associer un Network Security Group (NSG), à comprendre le routage de base et à connecter des ressources Azure.

Le niveau intermédiaire ne consiste pas simplement à créer davantage de réseaux. Il s'agit de **comprendre les interactions entre plusieurs composants** et de prévoir le comportement réel des flux.

À ce niveau, on doit notamment savoir :

- concevoir des plages IP sans chevauchement pour plusieurs VNet et un réseau local ;
- analyser les routes système et les User Defined Routes (UDR) ;
- construire une architecture hub-and-spoke ;
- distinguer peering, transit de passerelle et routage via une appliance ;
- imposer une sortie Internet contrôlée ;
- segmenter les flux avec des NSG et des Application Security Groups (ASG) ;
- connecter des services PaaS par un Private Endpoint et faire résoudre leur DNS correctement ;
- planifier une connexion hybride VPN ou ExpressRoute ;
- diagnostiquer une panne à partir des routes effectives, des règles de sécurité et des outils Network Watcher ;
- documenter une architecture et préparer son automatisation.

## 1.2. Le réseau est un ensemble de décisions cohérentes

Une connexion réseau réussie dépend de plusieurs contrôles indépendants.

```text
Application source
       |
       v
Résolution DNS correcte ?
       |
       v
Route vers la bonne destination ?
       |
       v
NSG / règles de sécurité autorisent le flux ?
       |
       v
Pare-feu ou appliance autorise et transfère le flux ?
       |
       v
La destination possède-t-elle une route de retour ?
       |
       v
Le service écoute-t-il sur le bon port ?
       |
       v
Connexion fonctionnelle
```

Un test `ping` qui échoue ne prouve donc pas, à lui seul, que le réseau est indisponible. ICMP peut être bloqué alors que TCP fonctionne. Inversement, une résolution DNS réussie ne prouve pas que le port applicatif est accessible.

## 1.3. Résultat attendu en fin de cours

À la fin du document, on doit être capable de concevoir une architecture dans laquelle :

- un réseau hub centralise les fonctions partagées ;
- plusieurs spokes hébergent des workloads distincts ;
- les flux inter-réseaux suivent un chemin documenté ;
- la sortie Internet des spokes est contrôlée par un pare-feu ;
- les services PaaS sensibles sont accessibles par une adresse privée ;
- les règles de sécurité suivent le principe du moindre privilège ;
- la connectivité hybride dispose d'un plan d'adressage et d'un plan de routage compatibles ;
- les pannes peuvent être analysées sans modifier la production au hasard.


# 2. Architecture de référence et plan d'adressage

Nous utiliserons plusieurs fois la même architecture pédagogique. Conserver un plan cohérent aide à comparer les routes, les NSG et les diagnostics d'un chapitre à l'autre.

## 2.1. Plan d'adressage de référence

| Réseau | CIDR | Rôle |
|---|---|---|
| `vnet-hub` | `10.10.0.0/16` | Services réseau partagés, pare-feu et passerelle hybride |
| `vnet-prod` | `10.20.0.0/16` | Workloads de production |
| `vnet-dev` | `10.30.0.0/16` | Workloads de développement et de test |
| Réseau local fictif | `10.250.0.0/16` | Datacenter ou réseau d'entreprise on-premises |
| `vnet-admin` (optionnel) | `10.40.0.0/16` | Administration séparée |

Ces blocs sont des exemples privés. Ils ne doivent être utilisés qu'après vérification qu'ils n'entrent pas en conflit avec les réseaux existants de l'organisation.

### Sous-réseaux du hub

| Sous-réseau | CIDR illustratif | Fonction |
|---|---|---|
| `AzureFirewallSubnet` | `10.10.0.0/26` | Sous-réseau dédié à Azure Firewall si ce service est déployé |
| `GatewaySubnet` | `10.10.1.0/27` | Sous-réseau dédié à une passerelle VPN ou ExpressRoute si elle est déployée |
| `snet-shared` | `10.10.10.0/24` | Services partagés non dédiés à une passerelle |
| `snet-management` | `10.10.20.0/24` | Administration ou bastion, selon le design |

Les tailles ci-dessus sont des **valeurs d'exemple**, pas une prescription universelle. Il faut vérifier les exigences actuelles du service, sa taille minimale de sous-réseau et ses options de mise à l'échelle avant de déployer une passerelle ou un pare-feu.

`AzureFirewallSubnet` est un nom réservé à Azure Firewall et doit respecter les exigences du service. `GatewaySubnet` est le nom attendu pour le sous-réseau d'une passerelle VNet. Éviter d'y placer des machines applicatives.

### Sous-réseaux du VNet de production

| Sous-réseau | CIDR | Fonction |
|---|---|---|
| `snet-prod-web` | `10.20.1.0/24` | Entrée Web ou reverse proxy |
| `snet-prod-app` | `10.20.2.0/24` | Services applicatifs privés |
| `snet-prod-data` | `10.20.3.0/24` | Bases de données ou services de données |
| `snet-prod-private-endpoints` | `10.20.10.0/24` | Private Endpoints, si la politique de l'organisation les centralise dans un sous-réseau dédié |

### Sous-réseaux du VNet de développement

| Sous-réseau | CIDR | Fonction |
|---|---|---|
| `snet-dev-app` | `10.30.1.0/24` | Machines et services de développement |
| `snet-dev-test` | `10.30.2.0/24` | Ressources temporaires de test |

## 2.2. Schéma global de référence

```text
                  RÉSEAU LOCAL DE L'ENTREPRISE
                       10.250.0.0/16
                               |
                     VPN S2S / ExpressRoute
                               |
                               v
+----------------------------------------------------------------+
|                         VNET-HUB                                |
|                         10.10.0.0/16                            |
|                                                                |
|   +---------------------+       +---------------------------+   |
|   | Azure Firewall      |       | GatewaySubnet             |   |
|   | IP privée exemple   |       | VPN / ExpressRoute        |   |
|   | 10.10.0.4           |       +---------------------------+   |
|   +----------+----------+                                       |
|              |                                                  |
+--------------+--------------------------------------------------+
               |                         |
       VNet Peering                VNet Peering
               |                         |
               v                         v
+---------------------------+   +---------------------------+
| VNET-PROD                 |   | VNET-DEV                  |
| 10.20.0.0/16              |   | 10.30.0.0/16              |
|                           |   |                           |
| Web  10.20.1.0/24         |   | App 10.30.1.0/24          |
| App  10.20.2.0/24         |   | Test 10.30.2.0/24         |
| Data 10.20.3.0/24         |   |                           |
+---------------------------+   +---------------------------+
```

Le pare-feu n'est pas automatiquement sur le chemin de tous les flux simplement parce qu'il est placé dans le hub. Les UDR, les peerings, les règles de pare-feu et les routes de retour doivent être conçus ensemble pour imposer ce chemin.

## 2.3. Pourquoi séparer hub et spokes ?

Le **hub** héberge les services réseau partagés : par exemple un pare-feu, une passerelle VPN, une passerelle ExpressRoute, un DNS forwarder ou des composants d'administration.

Les **spokes** hébergent les applications. Cette séparation facilite la gouvernance, le contrôle des flux et l'évolution indépendante des environnements.

Avantages :

- fonctions réseau partagées plutôt que dupliquées dans chaque VNet ;
- politiques de sécurité plus cohérentes ;
- réduction des configurations divergentes ;
- possibilité de séparer production, développement et test ;
- gestion plus claire des flux entre spokes.

Limites et coûts :

- le hub devient un composant critique à concevoir et surveiller ;
- les peerings, passerelles, pare-feu et transferts de données peuvent être facturés ;
- un routage centralisé peut ajouter de la latence et un point de congestion ;
- un routage mal conçu peut créer de l'asymétrie ou des boucles.

## 2.4. Les règles de conception avant de créer les ressources

1. Inventorier les plages IP existantes, y compris VPN, sites distants, conteneurs et réseaux partenaires.
2. Réserver des plages distinctes pour chaque VNet et chaque environnement.
3. Garder une marge de croissance : ne pas attribuer chaque bloc disponible au premier projet.
4. Documenter les sous-réseaux et leur rôle.
5. Définir quels flux doivent être directs et lesquels doivent être inspectés.
6. Décider si les services PaaS sont accessibles publiquement, par Service Endpoint ou par Private Endpoint.
7. Définir les conventions de nommage et de tags avant l'automatisation.


# 3. Concevoir un plan CIDR qui évolue

## 3.1. Calculer la taille d'une plage IPv4

Pour un préfixe IPv4 `/p`, le nombre théorique d'adresses est :

\[
N = 2^{32-p}
\]

| Préfixe | Nombre total d'adresses | Usage indicatif |
|---|---:|---|
| `/16` | 65 536 | Grand réseau virtuel |
| `/20` | 4 096 | VNet ou grande zone logique |
| `/22` | 1 024 | Sous-réseau de taille moyenne |
| `/24` | 256 | Sous-réseau courant |
| `/25` | 128 | Petit sous-réseau |
| `/26` | 64 | Sous-réseau spécialisé, selon exigences du service |
| `/27` | 32 | Petit sous-réseau spécialisé, selon exigences du service |

Azure réserve cinq adresses IPv4 dans chaque sous-réseau IPv4. Il faut donc distinguer les adresses théoriques et les adresses utilisables pour les ressources.

## 3.2. Exemple de découpage

Le VNet `10.20.0.0/16` peut être découpé ainsi :

```text
10.20.0.0/16  (ensemble de production)
|
+-- 10.20.1.0/24   Web
+-- 10.20.2.0/24   Application
+-- 10.20.3.0/24   Données
+-- 10.20.4.0/24   Intégration / workers
+-- 10.20.10.0/24  Private Endpoints
+-- réserves pour les futurs services
```

La liste est indicative. On peut préférer des plages plus grandes ou plus petites selon le nombre de ressources, la croissance, les services déployés et la stratégie d'adressage.

## 3.3. Pourquoi le chevauchement devient-il dangereux ?

Considérons :

```text
VNet-A : 10.20.0.0/16
VNet-B : 10.20.1.0/24
```

La plage de `VNet-B` se trouve à l'intérieur de celle de `VNet-A`. Cette conception ne convient pas à une interconnexion classique entre ces VNet.

Un chevauchement peut rendre ambiguë la destination d'une route. Le problème devient particulièrement compliqué avec :

- VNet Peering ;
- VPN Site-to-Site ;
- ExpressRoute ;
- Virtual WAN ;
- réseaux Kubernetes ;
- réseaux de partenaires ou d'acquisitions.

### Exercice rapide

Une entreprise possède un réseau local `10.40.0.0/16`. Peut-elle planifier `vnet-admin` avec le même CIDR et espérer une interconnexion routée simple ?

**Réponse :** non. Il faut choisir une plage non chevauchante, ou concevoir une solution de traduction d'adresses si la renumérotation est impossible. Le NAT n'est pas un substitut à une planification correcte dans une architecture nouvelle.

## 3.4. Agrégation de routes

L'agrégation consiste à représenter plusieurs routes contiguës par une plage plus large lorsque l'adressage le permet.

Par exemple, si un site annonce plusieurs blocs correctement alignés, une route agrégée peut réduire le nombre de préfixes annoncés à un routeur distant.

Mais une agrégation incorrecte peut attirer du trafic vers une destination qui ne possède pas réellement tous les sous-réseaux annoncés. Il faut donc vérifier :

- l'alignement des blocs ;
- l'absence de trous dans la plage ;
- la propriété des adresses ;
- la propagation vers les autres réseaux ;
- les routes plus spécifiques qui doivent rester prioritaires.

## 3.5. Documenter le plan d'adressage

Pour chaque plage, noter au minimum :

| Champ | Exemple |
|---|---|
| Environnement | Production |
| VNet | `vnet-prod` |
| CIDR VNet | `10.20.0.0/16` |
| Sous-réseau | `snet-prod-app` |
| CIDR sous-réseau | `10.20.2.0/24` |
| Zone / région | Région Azure choisie par le projet |
| Propriétaire | Équipe applicative |
| Flux autorisés | App vers base de données sur le port requis |
| Connectivité | Peering vers hub |
| Réserve | Oui / non |
| Justification | Application métier |

### Bonnes pratiques

- Ne pas attribuer une plage sans en vérifier l'utilisation dans l'inventaire global.
- Prévoir la croissance des Private Endpoints et des ressources éphémères.
- Réserver des blocs par environnement et par région.
- Automatiser la détection des doublons si le parc comporte de nombreux abonnements.
- Réévaluer les plages avant toute nouvelle connexion VPN ou ExpressRoute.


# 4. Routage Azure : routes système, UDR et choix du prochain saut

## 4.1. Le routage existe même sans table personnalisée

Azure fournit automatiquement des routes système à chaque sous-réseau. Une table de routage utilisateur n'est pas obligatoire pour chaque sous-réseau.

Les routes système permettent notamment :

- la communication au sein du VNet ;
- le routage vers Internet par défaut, selon les règles de la plateforme et de la ressource ;
- l'utilisation des routes apprises via une passerelle lorsqu'une connectivité hybride est en place ;
- le fonctionnement du peering et des Service Endpoints lorsqu'ils sont configurés.

Le comportement détaillé peut varier avec les services activés et les routes plus spécifiques.

## 4.2. Qu'est-ce qu'une UDR ?

UDR signifie **User Defined Route**. C'est une route personnalisée créée dans une Route Table puis associée à un sous-réseau.

Une route comporte :

- un préfixe de destination ;
- un type de prochain saut ;
- éventuellement une adresse IP de prochain saut, selon le type choisi.

Exemple conceptuel :

```text
Route Table : rt-prod-app
Préfixe destination    Prochain saut
10.30.0.0/16           Virtual appliance
0.0.0.0/0              Virtual appliance
```

Si le prochain saut est une appliance réseau, on indique l'adresse IP privée de cette appliance, sous réserve que cette IP soit directement joignable selon les exigences Azure.

## 4.3. Types courants de prochain saut

| Type | Fonction générale | Exemple d'utilisation |
|---|---|---|
| `Virtual network` | Routage vers une plage du VNet | Route correspondant à un espace d'adressage local au VNet |
| `Internet` | Routage vers Internet | Sortie directe autorisée par le design |
| `Virtual appliance` | Envoi vers une appliance réseau | Azure Firewall ou NVA compatible, à une IP privée accessible |
| `Virtual network gateway` | Envoi vers une passerelle réseau | Certains scénarios de VPN Gateway et de routage utilisateur |
| `None` | Abandon du trafic | Route de rejet explicite |

La disponibilité et le comportement du prochain saut dépendent de la topologie et du service de passerelle déployé. En particulier, ne pas supposer qu'un UDR vers `Virtual network gateway` fonctionne avec n'importe quelle combinaison de VPN Gateway, ExpressRoute, Route Server ou Virtual WAN. Vérifier la documentation du scénario exact.

## 4.4. Comment Azure choisit une route

Le principe essentiel est le **longest prefix match** : la route dont le préfixe correspondant à la destination est le plus spécifique est généralement sélectionnée.

Exemple :

```text
Destination réelle : 10.30.1.25

Route A : 10.30.0.0/16  -> Virtual network peering
Route B : 10.30.1.0/24  -> Virtual appliance 10.10.0.4
```

La route `/24` est plus spécifique que le `/16`. Le trafic destiné à `10.30.1.25` suivra donc le chemin de la route la plus spécifique, sous réserve des règles de préférence Azure pour les routes de cette nature et des contraintes de plateforme.

Quand deux routes ont le même préfixe, l'origine de la route importe également. La priorité générale est :

1. UDR ;
2. route BGP ;
3. route système.

Il existe des exceptions et des routes système spéciales, notamment celles relatives au VNet, au peering et aux Service Endpoints. Pour un diagnostic réel, examiner la table des routes effectives au lieu de se fier à une règle mémorisée isolément.

## 4.5. Les routes effectives

Une route effective est le résultat combiné des routes système, UDR et routes apprises pertinentes pour une interface ou un sous-réseau.

Dans Azure Portal, les détails réseau d'une VM permettent d'examiner les routes effectives de son interface réseau. L'outil Network Watcher Next hop aide également à comprendre le prochain saut sélectionné pour une destination.

Avant de modifier une Route Table, répondre à ces questions :

1. Quelle IP source émet le flux ?
2. Quelle est l'IP de destination obtenue après résolution DNS ?
3. Quel préfixe de destination correspond à cette IP ?
4. Quel prochain saut est sélectionné ?
5. Le prochain saut est-il joignable ?
6. Existe-t-il une route de retour cohérente ?
7. Un pare-feu inspecte-t-il le flux ?

## 4.6. Exemple : acheminer le trafic Internet d'un spoke vers le pare-feu

Hypothèses :

- `vnet-hub` : `10.10.0.0/16` ;
- `vnet-prod` : `10.20.0.0/16` ;
- l'adresse privée du pare-feu dans le hub est ici `10.10.0.4` ;
- le peering entre hub et spoke existe ;
- les règles du pare-feu autorisent uniquement les destinations nécessaires.

Dans une Route Table associée au sous-réseau applicatif de production :

```text
Préfixe : 0.0.0.0/0
Type    : Virtual appliance
Adresse : 10.10.0.4
```

Le flux suit le chemin prévu :

```text
VM privée (10.20.2.10)
          |
          v
UDR du sous-réseau app : 0.0.0.0/0
          |
          v
VNet Peering vers le hub
          |
          v
Azure Firewall (10.10.0.4)
          |
          v
Politique du pare-feu et route de sortie
          |
          v
Destination externe autorisée
```

Cette UDR ne crée pas à elle seule une sortie fonctionnelle. Il faut aussi vérifier le déploiement et la configuration du pare-feu, les règles applicatives/réseau, l'accès de retour, les routes du hub et les dépendances nécessaires aux services Azure.

## 4.7. Route par défaut et conséquences

`0.0.0.0/0` représente toute destination IPv4 qui ne correspond pas à une route plus spécifique.

L'associer à une appliance ou à une passerelle peut détourner un grand nombre de flux. Il faut notamment tenir compte :

- des services Azure accédés par adresse publique ;
- des mécanismes de Service Endpoint ;
- des dépendances de l'OS et des agents de gestion ;
- des routes apprises du réseau local ;
- des exceptions de sécurité et des besoins de mise à jour ;
- de la symétrie du trafic.

**Précaution importante :** ne pas appliquer une UDR par défaut à `GatewaySubnet` sans un design explicitement compatible avec le service de passerelle ; une route forcée mal placée peut perturber la connectivité du VPN Gateway.

## 4.8. Routage asymétrique

Le routage est asymétrique lorsque le chemin aller diffère du chemin retour.

```text
ALLER : VM-A -> Azure Firewall -> VM-B
RETOUR: VM-B ------------------> VM-A
```

Un pare-feu avec état peut rejeter les paquets de retour s'ils ne passent pas par le chemin attendu.

Pour prévenir cette situation :

- définir le chemin attendu dans les deux sens ;
- vérifier les routes effectives de chaque côté ;
- connaître le comportement du peering, de l'appliance et des passerelles ;
- vérifier les règles et le suivi de session du pare-feu ;
- tester avec l'IP réelle de destination.

## 4.9. Atelier de lecture d'une UDR

Une VM dans `10.20.2.10/24` doit joindre `10.30.1.5`. La table de son sous-réseau contient :

```text
10.30.0.0/16  -> Virtual appliance 10.10.0.4
0.0.0.0/0     -> Internet
```

Questions :

1. Quelle route correspond à `10.30.1.5` ?
2. Pourquoi la route par défaut n'est-elle pas choisie ?
3. Quelles vérifications restent nécessaires ?

**Réponse :** la route `10.30.0.0/16` est plus spécifique que `0.0.0.0/0`. Le flux doit être envoyé vers l'appliance `10.10.0.4`. Il faut ensuite vérifier le peering, la disponibilité de l'appliance, la politique du pare-feu, les routes du VNet destination et le chemin retour.


# 5. Architecture hub-and-spoke

## 5.1. Principe

Le modèle hub-and-spoke relie un réseau central, le hub, à des réseaux satellites, les spokes.

```text
                       +----------------+
                       |    VNET-HUB    |
                       | Firewall / VPN |
                       | DNS / services |
                       +-------+--------+
                               |
                +--------------+--------------+
                |                             |
         VNet Peering                  VNet Peering
                |                             |
         +------+-------+              +------+-------+
         |  VNET-PROD   |              |   VNET-DEV   |
         | 10.20/16     |              | 10.30/16     |
         +--------------+              +--------------+
```

Le hub sert de point central pour les fonctions partagées. Les spokes permettent de séparer les workloads et les équipes.

## 5.2. Ce que l'architecture ne fait pas automatiquement

Créer deux peerings n'impose pas automatiquement une inspection par pare-feu. Un peering VNet n'est pas une passerelle de transit générique qui rend chaque réseau connecté transitivement joignable à tous les autres.

Pour acheminer un flux d'un spoke à un autre via le hub, il faut un mécanisme de routage/inspection adapté, généralement avec des UDR et un équipement de transit compatible, ou un service de réseau conçu pour cette topologie.

## 5.3. Flux souhaités et flux à bloquer

Exemple de politique :

```text
Internet -> Front Web public               : autorisé sur HTTPS seulement
Web -> Application                         : autorisé sur le port applicatif
Application -> Base de données             : autorisé sur le port DB requis
Développement -> Production                : interdit par défaut
Administration autorisée -> VMs            : accès contrôlé
Tous les workloads -> Internet             : sortie via le pare-feu central
Workloads -> services PaaS sensibles       : Private Endpoint privilégié
```

La politique doit être traduite en routes et règles concrètes. Le pare-feu ne remplace pas les NSG, et les NSG ne remplacent pas une politique de pare-feu central lorsque l'inspection centralisée est requise.

## 5.4. Hub partagé par plusieurs abonnements

Dans une grande organisation, le hub peut être hébergé dans un abonnement de connectivité séparé, tandis que les applications se trouvent dans des abonnements de production et de développement.

```text
Tenant Microsoft Entra ID
|
+-- Abonnement Connectivity
|   +-- Resource group réseau central
|       +-- vnet-hub
|       +-- pare-feu
|       +-- VPN / ExpressRoute
|
+-- Abonnement Production
|   +-- vnet-prod
|
+-- Abonnement NonProduction
    +-- vnet-dev
```

Il faut alors gérer les rôles RBAC, les politiques Azure Policy, les autorisations de peering et la répartition des responsabilités. Le contrôle d'accès au plan de gestion est distinct des règles qui autorisent le trafic de données.

## 5.5. Quand ne pas choisir hub-and-spoke ?

Ce modèle n'est pas automatiquement optimal. Il faut comparer ses besoins à d'autres options, notamment Azure Virtual WAN, lorsque l'on doit connecter de nombreux sites, régions et réseaux.

Le choix dépend du nombre de VNet, des flux, des exigences d'inspection, du besoin de routage dynamique, des compétences opérationnelles et du coût total.


# 6. VNet Peering et transit

## 6.1. Fonction du VNet Peering

Le VNet Peering connecte deux VNet afin de permettre une communication privée à travers le réseau backbone Microsoft, sous réserve des routes et règles de sécurité.

On rencontre notamment :

- **Peering régional** : VNet dans la même région ;
- **Global VNet Peering** : VNet dans des régions différentes, avec des considérations de coût et de service à vérifier.

Le peering nécessite des espaces d'adressage non chevauchants pour la communication routée classique.

## 6.2. Deux directions de configuration

Un peering est configuré de chaque côté. Pour un peering entre `vnet-hub` et `vnet-prod`, il faut vérifier l'état des deux objets de peering et la cohérence de leurs options.

```text
vnet-hub  <====== VNet Peering ======>  vnet-prod
```

Un objet de peering créé d'un seul côté ne suffit pas à obtenir une relation pleinement configurée.

## 6.3. Options importantes

Les libellés précis peuvent varier selon le portail et l'outil, mais les concepts à vérifier sont :

- autoriser l'accès au réseau virtuel distant ;
- autoriser le trafic transféré depuis le réseau distant si une appliance joue un rôle de transit ;
- annoncer ou utiliser la passerelle distante lorsqu'un scénario de gateway transit le requiert ;
- ne pas activer la passerelle distante si le VNet local possède déjà sa propre passerelle incompatible avec cette option.

Le trafic transféré et le transit de passerelle sont des mécanismes distincts. L'option « allow forwarded traffic » ne transforme pas, à elle seule, un peering en routeur transitif.

## 6.4. Transit de passerelle

Dans un hub possédant une VPN Gateway ou une ExpressRoute Gateway, un spoke peut être configuré pour utiliser la passerelle distante du hub, lorsque le scénario est pris en charge.

Schéma :

```text
Réseau local 10.250.0.0/16
           |
       VPN Gateway
           |
       VNet-Hub
        /     \
  Peering     Peering
    /            \
VNet-Prod       VNet-Dev
```

Le transit de passerelle ne signifie pas que le trafic entre tous les spokes est automatiquement inspecté par un pare-feu. Le flux entre `VNet-Prod` et `VNet-Dev` doit être traité séparément selon les besoins de sécurité et de routage.

## 6.5. Peering et non-transitivité

Exemple :

```text
A <----peering----> B <----peering----> C
```

Il ne faut pas supposer que A peut joindre C simplement parce que A est peeré avec B et B avec C. Une architecture transitée nécessite une conception de routage prise en charge.

Pour faire passer un trafic entre A et C via B, on peut devoir utiliser des UDR vers une appliance, l'autorisation du trafic transféré et des routes cohérentes dans les deux sens.

## 6.6. Procédure de validation d'un peering

1. Vérifier que les adresses des VNet ne se chevauchent pas.
2. Vérifier le statut des deux peerings.
3. Vérifier les options d'accès et de transfert nécessaires.
4. Vérifier les routes effectives côté source et destination.
5. Vérifier les NSG des sous-réseaux et des interfaces.
6. Vérifier la politique de l'appliance si le flux doit être inspecté.
7. Tester le port applicatif exact, pas seulement ICMP.
8. Vérifier le retour du flux.


# 7. NSG, ASG et segmentation des flux

## 7.1. Rôle d'un Network Security Group

Un NSG contient des règles de sécurité qui autorisent ou refusent le trafic réseau entrant et sortant. Un NSG peut être associé à un sous-réseau et/ou à une interface réseau, en respectant les limites et le modèle de sécurité choisi.

Une règle comporte notamment :

- la priorité ;
- le nom ;
- la direction ;
- l'action (`Allow` ou `Deny`) ;
- le protocole ;
- les plages source et destination ;
- les ports source et destination.

Les règles de priorité plus faible numériquement sont évaluées avant celles de priorité plus élevée. Il faut éviter des règles qui se chevauchent sans raison et documenter les exceptions.

## 7.2. Exemple de politique applicative

Architecture : Web, Application, Base de données.

```text
Clients
  |
  | HTTPS 443
  v
[ WEB ] -- TCP 8080 --> [ APP ] -- TCP 1433 --> [ DB ]
```

| Source | Destination | Port | Décision | Justification |
|---|---|---:|---|---|
| Clients autorisés | Web | TCP 443 | Autoriser | Entrée HTTPS |
| Web | App | TCP 8080 | Autoriser | Appel applicatif |
| App | DB | TCP 1433 | Autoriser | Exemple SQL Server |
| Web | DB | Tout | Refuser implicitement ou explicitement selon la politique | Le Web ne doit pas contacter directement la DB |
| Dev | Prod | Tout | Refuser par défaut | Isolation des environnements |

Les ports sont des exemples. Utiliser le port réellement configuré pour l'application et la base de données.

## 7.3. NSG au sous-réseau et à l'interface

Un NSG placé sur le sous-réseau applique une politique commune à plusieurs interfaces. Un NSG sur une interface permet une politique plus spécifique à cette machine.

Lorsque plusieurs NSG s'appliquent au même flux, les autorisations doivent être cohérentes à tous les niveaux concernés. Une règle autorisant le trafic dans un NSG ne neutralise pas un refus effectué par un autre contrôle applicable.

Bonne pratique : appliquer une segmentation simple et lisible au niveau du sous-réseau, puis réserver les règles spécifiques à l'interface aux cas qui le justifient réellement.

## 7.4. Les règles par défaut

Azure ajoute des règles par défaut aux NSG, notamment pour certains flux au sein du VNet, l'équilibrage de charge et le trafic sortant. Les noms exacts des règles et leur priorité doivent être vérifiés dans le NSG réellement déployé.

Ne pas se fier uniquement à une lecture générale des règles : regarder les règles effectives et utiliser Network Watcher lorsqu'un flux est bloqué.

## 7.5. Application Security Groups (ASG)

Les ASG permettent de regrouper des interfaces réseau de machines virtuelles par rôle applicatif, puis de les utiliser dans les sources ou destinations de règles NSG, dans les limites prises en charge par Azure.

Exemple conceptuel :

```text
ASG-Web       : interfaces des serveurs Web
ASG-App       : interfaces des serveurs applicatifs
ASG-Database  : interfaces des serveurs de données
```

Politique :

```text
ASG-Web -> ASG-App      TCP 8080 : Allow
ASG-App -> ASG-Database TCP 1433 : Allow
ASG-Web -> ASG-Database Any     : pas d'autorisation dédiée
```

Les ASG améliorent la lisibilité quand les adresses IP des machines changent. Ils ne remplacent pas la planification IP, les routes ou les règles de pare-feu.

## 7.6. Entrant et sortant : deux directions à vérifier

Une connexion doit être autorisée dans le sens correspondant à son initiation et le trafic doit pouvoir revenir. Les NSG sont stateful : le trafic de retour d'une connexion autorisée est généralement géré par le suivi d'état. Cela ne dispense pas de vérifier les NSG, les routes et les pare-feu de tous les segments traversés.

Ne créez pas une règle `Any/Any/Any` pour « faire fonctionner » l'application puis ne l'oubliez pas. Utilisez un test temporaire contrôlé, une durée de validité et une suppression vérifiée si une règle de diagnostic exceptionnellement large est indispensable.

## 7.7. Priorités et erreurs courantes

Exemple de règles :

```text
Priorité 100 : Allow TCP 443 depuis les sources Web autorisées
Priorité 200 : Allow TCP 8080 depuis ASG-Web vers ASG-App
Priorité 300 : Deny tout trafic entrant non prévu (si politique explicite requise)
```

Cet exemple ne doit pas être copié tel quel sans tenir compte des règles par défaut et de l'ensemble des flux requis.

Erreurs fréquentes :

- utiliser `*` comme source pour un port d'administration ;
- ouvrir un port à Internet alors que seuls les subnets applicatifs doivent y accéder ;
- oublier un NSG attaché à l'interface de la VM ;
- supposer que le NSG permet à lui seul le flux à travers Azure Firewall ;
- confondre NSG et pare-feu invité sur le système d'exploitation ;
- oublier les règles DNS, de supervision, d'identité ou de mise à jour nécessaires à l'exploitation.


# 8. Azure Firewall et appliances réseau

## 8.1. Différence entre NSG et Azure Firewall

| Mécanisme | Rôle principal | Emplacement / portée typique |
|---|---|---|
| NSG | Filtrage réseau au niveau sous-réseau ou interface | Contrôle des flux vers les ressources |
| ASG | Regroupement logique d'interfaces pour les règles NSG | Simplification de la segmentation |
| Azure Firewall | Service de pare-feu géré, centralisé, avec règles de réseau et d'application selon le SKU et les capacités | Point de contrôle réseau central ou périmétrique |
| NVA | Appliance réseau logicielle fournie par un éditeur ou construite par l'organisation | Selon l'architecture de transit et les routes |
| Firewall du système invité | Défense locale dans la machine | Protection supplémentaire de l'OS et des services |

Ces contrôles peuvent être complémentaires. Le choix dépend des besoins d'inspection, de journalisation, de filtrage, de conformité, de disponibilité et de coût.

## 8.2. Place du pare-feu dans le hub

```text
                     Internet / réseaux externes
                                ^
                                |
                        +-------+--------+
                        | Azure Firewall |
                        +-------+--------+
                                |
                    +-----------+-----------+
                    |                       |
                VNet-Hub                VPN Gateway
                    |
              +-----+------+
              |            |
          VNet-Prod     VNet-Dev
```

La présence du pare-feu dans le hub n'assure pas, à elle seule, que tous les flux passent par lui. Les spokes doivent disposer des routes adaptées et le pare-feu doit avoir une route valide vers les destinations.

## 8.3. Règles de réseau et règles d'application

Selon les capacités et le SKU utilisés, Azure Firewall permet de créer plusieurs types de règles :

- règles réseau, basées notamment sur IP, protocole et ports ;
- règles d'application, utiles pour des flux Web identifiés par des noms de domaine et autres propriétés supportées ;
- règles NAT, utiles pour certains scénarios de publication ou de traduction.

Les détails de priorité, de traitement et de fonctionnalités disponibles varient selon le SKU et les mises à jour du service. Il faut consulter la documentation correspondant à la version choisie.

## 8.4. Flux de sortie contrôlé

Supposons que les VMs de `vnet-prod` ne doivent pas sortir directement vers Internet.

```text
VM Production
  |
  v
UDR 0.0.0.0/0 -> IP privée du pare-feu
  |
  v
VNet Peering
  |
  v
Azure Firewall
  |
  +-- règle autorise l'URL ou le flux requis --> Destination
  |
  +-- absence d'autorisation              --> Flux bloqué
```

Les dépendances de plateforme, de gestion et de mise à jour doivent être identifiées avant de bloquer tous les flux par défaut.

## 8.5. Azure Firewall ou NVA ?

Azure Firewall est un service géré. Une Network Virtual Appliance (NVA) peut fournir des fonctions spécifiques d'un fournisseur tiers ou d'une solution de sécurité particulière.

| Critère | Azure Firewall | NVA |
|---|---|---|
| Exploitation | Service Azure géré | Souvent davantage de responsabilité opérationnelle |
| Fonctionnalités | Ensemble de capacités Azure documentées | Dépend du fournisseur et de la licence |
| Mise à l'échelle | Selon le SKU et les capacités du service | Dépend de l'architecture de l'appliance |
| Routage | Intégration Azure selon le design | UDR, IP forwarding, BGP et haute disponibilité à planifier selon le produit |
| Coût | Facturation du service et du trafic applicable | VM, licences, disques, trafic et exploitation |

Ne choisissez pas uniquement selon le coût horaire apparent. Prenez en compte la redondance, la mise à jour, les licences, le support, les journaux, les performances et le coût de transfert.

## 8.6. Si une NVA doit transférer le trafic

Lorsqu'une machine virtuelle joue le rôle de routeur ou d'appliance, il peut être nécessaire d'activer **IP forwarding** sur son interface réseau et d'activer/configurer le routage dans l'OS ou l'application elle-même.

Une UDR pointant vers une IP qui n'est pas directement joignable ou qui ne transfère pas les paquets ne suffit pas. Il faut suivre la documentation Azure et celle du fournisseur de l'appliance.


# 9. Sortie Internet contrôlée et routage forcé

## 9.1. Le problème

Une équipe de sécurité peut exiger que toutes les machines privées sortent vers Internet uniquement par un point d'inspection central.

Le but peut être de :

- filtrer les destinations ;
- centraliser les journaux ;
- limiter l'exfiltration ;
- appliquer une politique réseau homogène ;
- superviser les communications externes.

## 9.2. Architecture de sortie centralisée

```text
VNet-Prod                          VNet-Hub
+-------------------+              +-------------------+
| VM privée         |              | Azure Firewall    |
| 10.20.2.10        |              | 10.10.0.4         |
+---------+---------+              +---------+---------+
          |                                  |
          | UDR 0.0.0.0/0                    | Règles et routage
          +------------> Peering ------------+
                                             |
                                             v
                                         Internet
```

## 9.3. Procédure de conception

1. Identifier toutes les destinations nécessaires aux applications et à l'OS.
2. Décider si la sortie doit être filtrée par adresse IP, protocole, FQDN ou combinaison de critères supportés.
3. Déployer le pare-feu selon la topologie recommandée par Microsoft.
4. Définir les routes UDR des sous-réseaux source.
5. Vérifier les routes du pare-feu vers les réseaux internes et les destinations externes.
6. Vérifier les NSG des sous-réseaux et interfaces.
7. Créer des règles minimales, puis tester la connectivité requise.
8. Contrôler les journaux et les routes effectives.
9. Prévoir les exceptions et la continuité de service.
10. Documenter les coûts et la procédure de retour arrière.

## 9.4. Ne pas oublier les services Azure

Une route par défaut dirigée vers une appliance peut modifier le chemin des communications vers les adresses publiques, y compris celles de certains services Azure, sauf lorsqu'une route plus spécifique ou un mécanisme prévu par la plateforme s'applique.

Lorsqu'on utilise des Service Endpoints, Azure crée des routes dédiées pour les préfixes concernés. Ces routes plus spécifiques peuvent influencer le chemin de trafic par rapport à une route par défaut.

Il faut éviter d'appliquer aveuglément une UDR `0.0.0.0/0` à un sous-réseau spécialisé, notamment `GatewaySubnet`, sans avoir validé le scénario dans la documentation officielle.

## 9.5. Sortie contrôlée et publication entrante sont deux sujets différents

Faire passer le trafic sortant d'une VM par le pare-feu ne crée pas automatiquement un accès entrant depuis Internet vers cette VM.

Pour une publication entrante, il faut étudier le point d'entrée autorisé, la terminaison TLS, le routage, la traduction ou le proxy nécessaire, les règles de pare-feu et les retours. Ne donnez pas d'adresse IP publique à une ressource privée simplement pour corriger une route sortante.


# 10. Private Link, Private Endpoint et Service Endpoint

## 10.1. Pourquoi utiliser un accès privé à un service PaaS ?

Une application Azure peut consommer un service géré tel qu'Azure Storage, Azure SQL ou un autre service compatible avec Private Link.

Sans configuration d'accès privé adaptée, l'application peut essayer de se connecter au point de terminaison public du service. Selon la politique du service, cet accès public peut être interdit, autorisé sous conditions ou filtré.

Private Link permet d'accéder à certains services par un **Private Endpoint**, c'est-à-dire une interface réseau qui possède une adresse IP privée issue d'un sous-réseau du VNet.

## 10.2. Schéma Private Endpoint

```text
VNet-Prod : 10.20.0.0/16
|
+-- Subnet applicatif
|   +-- VM-APP 10.20.2.10
|
+-- Subnet Private Endpoints
    +-- PE-Storage 10.20.10.4
              |
              v
       Azure Private Link
              |
              v
       Compte Azure Storage
```

L'adresse `10.20.10.4` est illustrative. Le Private Endpoint n'est pas un proxy qui exécute l'application ; il fournit un point d'accès réseau privé au service associé.

## 10.3. Private Endpoint ou Service Endpoint ?

| Critère | Private Endpoint / Private Link | Service Endpoint |
|---|---|---|
| Connexion au service | Via une IP privée dans le VNet | Le service reste accédé par son point de terminaison de service ; le réseau bénéficie de l'identité réseau de la fonctionnalité |
| DNS privé | Généralement essentiel pour que le nom usuel résolve vers l'IP privée | Le DNS public du service est généralement conservé |
| Exposition réseau | Peut permettre une connectivité privée au service compatible | N'ajoute pas une IP privée du service dans le VNet |
| Contrôle d'accès | Politiques Private Link et configuration du service, plus NSG selon les options et le chemin | Pare-feu du service configuré pour autoriser le VNet ou le sous-réseau concerné |
| Utilisation typique | Accès privé via une IP dans le VNet, scénarios inter-réseaux selon le design | Contrôle d'accès réseau pour certains services Azure pris en charge |

Le choix dépend de la prise en charge du service, des exigences de DNS, de la sécurité et de la topologie. Vérifier la documentation du service exact : Private Link n'est pas disponible de façon identique pour tous les services et toutes les fonctions.

## 10.4. DNS : l'élément qui surprend souvent

Le Private Endpoint peut être déployé avec succès, mais l'application peut continuer à résoudre le nom du service vers son adresse publique. Dans ce cas, le trafic n'emprunte pas le chemin privé attendu.

Exemple :

```text
Application demande : monstockage.blob.core.windows.net
                  |
                  v
DNS privé et liens de zone configurés ?
         /                       \
       Oui                       Non
        |                         |
        v                         v
Résolution vers IP privée    Résolution publique possible
        |                         |
        v                         v
Accès via Private Link       Tentative de chemin public
```

La configuration correcte dépend du service, du FQDN utilisé, de la zone DNS privée à associer et de la présence éventuelle d'un DNS personnalisé ou d'un réseau local.

## 10.5. Procédure de validation d'un Private Endpoint

1. Vérifier l'état de la connexion privée et l'approbation requise par la ressource cible.
2. Vérifier l'adresse IP privée affectée à l'interface du Private Endpoint.
3. Vérifier la zone DNS privée recommandée pour ce service.
4. Vérifier le lien de la zone DNS vers les VNet consommateurs.
5. Depuis la machine cliente, résoudre le FQDN réellement utilisé par l'application.
6. Confirmer que la réponse contient l'IP privée attendue.
7. Tester le port applicatif et observer les routes/contrôles de sécurité.
8. Vérifier la politique réseau du service cible, y compris la désactivation éventuelle de l'accès public si c'est l'objectif.

## 10.6. Exemple de résolution

```text
Nom demandé par l'application
        storageprod.blob.core.windows.net
                         |
                         v
             Configuration DNS Azure
                         |
                         v
          Adresse privée du Private Endpoint
                         |
                         v
             Routage VNet / inter-VNet
                         |
                         v
                Azure Storage via Private Link
```

La réponse DNS exacte dépend du service et de sa configuration. Il ne faut pas coder en dur l'IP du Private Endpoint dans les applications : préférer le nom de service documenté, avec une configuration DNS correcte.


# 11. DNS privé et résolution entre réseaux

## 11.1. Le rôle du DNS

Le DNS traduit un nom en adresse IP. Dans une architecture hybride, la résolution DNS doit être cohérente entre Azure et le réseau local.

Exemples de noms :

```text
app.internal.example
sqlprod.database.windows.net
storageprod.blob.core.windows.net
```

Le DNS ne choisit pas le prochain saut réseau. Il fournit une adresse ; le routage, les règles et le service déterminent ensuite si la connexion aboutit.

## 11.2. Azure Private DNS Zones

Les zones DNS privées Azure permettent de gérer des noms qui ne sont pas destinés à une résolution publique normale. Une zone privée peut être liée à un ou plusieurs VNet, dans les limites et conditions du service.

Dans le cas d'un Private Endpoint, la zone à utiliser dépend du service et du type de point de terminaison. Il faut suivre les noms de zones recommandés dans la documentation du service plutôt que deviner le suffixe.

## 11.3. Résolution dans une architecture hub-and-spoke

```text
                  Azure Private DNS Zone
                           |
                   +-------+-------+
                   |               |
                   v               v
               VNet-Hub        VNet-Prod
                   |               |
                   +-------+-------+
                           |
                    VM / Private Endpoint
```

Une zone privée doit être liée aux VNet qui doivent l'utiliser. Les liens de zone, les réglages DNS des VNet et la présence éventuelle d'un DNS personnalisé doivent être compatibles.

## 11.4. DNS personnalisé

Une organisation peut utiliser ses propres serveurs DNS, par exemple pour conserver un espace de noms historique.

Dans ce cas, planifier :

- les paramètres DNS du VNet ;
- la connectivité IP vers les serveurs DNS ;
- les règles NSG et pare-feu nécessaires ;
- les redirecteurs conditionnels ;
- la résolution des zones privées Azure ;
- les chemins entre Azure et on-premises ;
- la disponibilité des serveurs DNS.

Changer le serveur DNS d'un VNet sans vérifier l'accessibilité de ce serveur peut empêcher la résolution nécessaire aux applications et à l'administration.

## 11.5. DNS hybride : modèle avec redirecteur

```text
VM Azure
   |
   v
DNS forwarder en Azure
   |                      \
   | zones Azure privées   \ zones internes entreprise
   v                        v
Private DNS Azure       DNS on-premises
```

Ce dessin est conceptuel. La mise en œuvre précise peut utiliser Azure DNS Private Resolver ou une autre architecture de résolution prise en charge. Il faut éviter les boucles de transfert DNS : chaque zone doit avoir un chemin de résolution clairement défini.

## 11.6. Méthode de diagnostic DNS

Sur une machine cliente, comparer :

1. le nom exact utilisé par l'application ;
2. la réponse DNS ;
3. l'adresse IP obtenue ;
4. le chemin réseau vers cette adresse ;
5. le port du service ;
6. le comportement avec et sans DNS personnalisé, si cela est testé dans un environnement de laboratoire.

Exemples de commandes :

```powershell
Resolve-DnsName storageprod.blob.core.windows.net
Test-NetConnection storageprod.blob.core.windows.net -Port 443
```

```bash
nslookup storageprod.blob.core.windows.net
getent hosts storageprod.blob.core.windows.net
nc -vz storageprod.blob.core.windows.net 443
```

Les commandes doivent être adaptées au système et au client disponible. Un test sur un FQDN public ne prouve pas que le DNS privé est configuré ; comparer le résultat attendu à l'IP effective du Private Endpoint.


# 12. Connectivité hybride : VPN Gateway et ExpressRoute

## 12.1. Pourquoi connecter Azure au réseau local ?

Une organisation peut avoir besoin d'accéder depuis Azure à des services locaux : annuaire, bases de données, outils métier, serveurs de fichiers, systèmes industriels ou services d'administration.

Deux mécanismes majeurs sont le VPN Site-to-Site et ExpressRoute. Ils ont des caractéristiques différentes et ne doivent pas être confondus.

## 12.2. VPN Site-to-Site

Un VPN Site-to-Site établit un tunnel chiffré entre Azure VPN Gateway et un équipement VPN local compatible. La connectivité passe sur Internet, avec chiffrement du tunnel.

```text
Réseau local 10.250.0.0/16
           |
     Routeur / pare-feu VPN
           |
       Internet public
           |
       Tunnel IPsec
           |
      Azure VPN Gateway
           |
        VNet-Hub
           |
     VNet-Prod / VNet-Dev
```

Éléments à préparer :

- plage IP locale sans chevauchement avec Azure ;
- adresse publique de l'équipement local ;
- paramètres IKE/IPsec compatibles ;
- clé partagée ou mécanisme d'authentification prévu ;
- préfixes à annoncer ou à configurer ;
- règles de pare-feu ;
- routes dans le réseau local et les VNet Azure ;
- supervision des tunnels.

## 12.3. ExpressRoute

ExpressRoute fournit une connectivité privée entre le réseau local et Microsoft via un fournisseur et une connectivité ExpressRoute. Le chemin ne repose pas sur un tunnel VPN Internet standard.

ExpressRoute ne signifie pas que les données sont automatiquement chiffrées de bout en bout au niveau applicatif. Les exigences de chiffrement, de sécurité et d'isolation doivent être évaluées séparément.

Le choix dépend de la bande passante, de la latence, des besoins de fiabilité, du réseau existant, des régions, des opérateurs et du budget.

## 12.4. VPN et ExpressRoute : comparaison

| Critère | VPN Site-to-Site | ExpressRoute |
|---|---|---|
| Transport | Internet public avec tunnel chiffré | Connectivité privée fournie par le service et les partenaires |
| Mise en place | Souvent plus accessible pour un site de petite taille | Projet et coordination fournisseur généralement plus importants |
| Chiffrement | Tunnel VPN chiffré | Ne pas supposer un chiffrement applicatif automatique |
| Routage dynamique | BGP pris en charge dans les scénarios compatibles | BGP fait partie de la conception de routage ExpressRoute |
| Coût et exploitation | Dépend de la passerelle, du SKU et du trafic | Dépend du circuit, du fournisseur, de la passerelle et du trafic |
| Usage fréquent | Connectivité hybride chiffrée ou secours | Connectivité privée prévisible, entreprise ou forte exigence de réseau |

## 12.5. VPN Gateway et sous-réseau GatewaySubnet

Une passerelle de réseau virtuel nécessite un sous-réseau dédié généralement nommé `GatewaySubnet`. Sa taille doit tenir compte des besoins et des recommandations du type de passerelle choisi.

Règles pratiques :

- ne pas y héberger des VMs applicatives ;
- ne pas y associer une UDR hasardeuse ;
- vérifier les exigences de NSG, de routage et de disponibilité du SKU déployé ;
- prévoir les coûts et le temps de déploiement de la passerelle ;
- documenter l'adresse publique de la passerelle et les paramètres du dispositif local.

## 12.6. Haute disponibilité VPN

Azure VPN Gateway propose des configurations de disponibilité différentes, notamment active-standby et active-active selon la configuration prise en charge.

En mode active-active, les deux instances de la passerelle peuvent établir des tunnels avec le dispositif local, si celui-ci est correctement configuré et compatible. Cela améliore certains scénarios de disponibilité, mais ne suffit pas à garantir une résilience de bout en bout.

Il faut aussi étudier :

- la redondance du matériel local ;
- les deux chemins WAN lorsque requis ;
- les routes et l'utilisation de BGP ;
- les équipements électriques et opérateurs ;
- la détection de panne ;
- les tests de bascule ;
- les délais de convergence et les applications tolérantes aux interruptions.

## 12.7. BGP pour le routage hybride

BGP permet aux routeurs de s'échanger des préfixes plutôt que de maintenir exclusivement des routes statiques. Les préfixes réellement annoncés doivent être contrôlés. Une annonce trop large peut détourner un trafic important.

Checklist de routage hybride :

1. Les préfixes Azure et locaux ne se chevauchent pas.
2. Les préfixes autorisés sont annoncés dans le bon sens.
3. Les routes sont apprises de façon attendue.
4. Il n'existe pas d'agrégation qui détourne des destinations non détenues.
5. Les UDR n'annulent pas le chemin attendu.
6. Le chemin de retour est cohérent.
7. Les NSG et pare-feu autorisent les flux requis.
8. Les tunnels ou le circuit sont surveillés.


# 13. BGP et Azure Route Server

## 13.1. Pourquoi un routage dynamique ?

Dans les topologies simples, quelques UDR statiques peuvent suffire. Avec plusieurs appliances, chemins hybrides ou routes qui changent, la maintenance manuelle peut devenir difficile.

BGP permet l'échange de routes entre équipements compatibles. Les préfixes annoncés doivent être contrôlés : un protocole dynamique ne remplace ni la planification IP ni la gouvernance des routes.

## 13.2. Rôle d'Azure Route Server

Azure Route Server est un service géré qui simplifie l'échange dynamique de routes BGP entre certaines Network Virtual Appliances et le réseau défini par logiciel d'Azure.

Schéma conceptuel :

```text
          NVA / SD-WAN                    Azure SDN
          annonce les routes                  ^
                 |                            |
                 v                            |
         +-------------------+   BGP   +-------+-------+
         | Azure Route Server|<------->| VNet / routes |
         +-------------------+         +---------------+
```

Il agit comme un route reflector BGP dans les scénarios documentés. Il ne remplace pas le pare-feu, ne chiffre pas le trafic à lui seul et ne rend pas automatiquement chaque route annoncée sécurisée.

## 13.3. Quand envisager Route Server ?

Exemples d'usage :

- échange dynamique de routes avec des NVAs ;
- réduction de la maintenance manuelle des routes ;
- topologies multi-appliances ;
- architecture où les préfixes doivent évoluer dynamiquement.

Pour un petit laboratoire avec deux VNet et une UDR simple, il ajoute généralement de la complexité inutile.

## 13.4. Points de vigilance

- respecter les exigences de sous-réseau et de déploiement du service ;
- vérifier l'ASN local et les sessions BGP ;
- contrôler les routes annoncées et apprises ;
- examiner les filtres et les route maps lorsque pris en charge ;
- comprendre les interactions avec VPN Gateway, ExpressRoute et les peerings ;
- ne pas déduire le chemin réel du seul état « BGP established » ;
- tester l'impact des retraits de route et des pannes d'une NVA.

## 13.5. Route Server ou UDR statique ?

| Situation | Approche initiale à considérer |
|---|---|
| Deux spokes avec un pare-feu central stable | UDR statiques bien documentées |
| Plusieurs NVA qui annoncent des routes dynamiques | Azure Route Server peut être pertinent |
| Plusieurs sites et hubs à grande échelle | Comparer Route Server et Azure Virtual WAN selon les exigences |
| Besoin de politique de sécurité centrale | Route Server n'est pas le contrôle de sécurité ; concevoir aussi la fonction de pare-feu |


# 14. IPv6 et dual-stack

## 14.1. Pourquoi s'intéresser à IPv6 ?

IPv6 étend l'espace d'adressage et peut être nécessaire pour des services accessibles depuis des clients IPv6 ou pour des exigences d'architecture. Une architecture IPv4 peut être étendue en dual-stack si les services et scénarios choisis le prennent en charge.

Le dual-stack signifie qu'une ressource ou un chemin réseau supporte IPv4 et IPv6. Il faut configurer et tester les deux familles d'adresses ; la présence d'IPv4 fonctionnel ne prouve pas qu'IPv6 est sécurisé ou routé correctement.

## 14.2. Principes de conception

- vérifier la prise en charge IPv6 du service Azure concerné ;
- planifier les préfixes IPv6 et leurs frontières ;
- définir les règles de sécurité IPv6 explicitement ;
- vérifier DNS A et AAAA ;
- tester l'accessibilité et la route dans chaque famille ;
- vérifier les chemins de sortie et d'entrée ;
- ne pas supposer que toutes les fonctionnalités IPv4 sont identiques en IPv6.

## 14.3. Risque de sécurité

Une politique correctement restrictive en IPv4 peut rester incomplète si un chemin IPv6 est autorisé mais pas surveillé. Lors d'un déploiement dual-stack, les règles, la supervision, les tests et les procédures de réponse aux incidents doivent considérer IPv4 et IPv6.


# 15. Supervision et observabilité réseau

## 15.1. Les trois catégories à distinguer

| Catégorie | Question à laquelle elle répond | Exemples d'outils |
|---|---|---|
| Configuration | Quelle règle ou route est définie ? | Route Tables, NSG, peering, paramètres du VNet |
| Diagnostic ponctuel | Pourquoi ce flux précis échoue-t-il ? | Network Watcher, IP flow verify, Next hop, Connection troubleshoot |
| Télémétrie et historique | Que s'est-il passé dans le temps ? | VNet flow logs, Azure Monitor, Log Analytics, métriques et alertes |

Une capture ponctuelle ne remplace pas les journaux, et les journaux ne remplacent pas l'analyse des routes effectives.

## 15.2. Network Watcher

Network Watcher fournit des outils de diagnostic réseau Azure. Selon le scénario et la région, les outils disponibles peuvent inclure :

- IP flow verify pour vérifier si un flux est autorisé ou refusé par les contrôles concernés ;
- Next hop pour analyser le prochain saut retenu ;
- Connection troubleshoot pour étudier une connexion ;
- Packet capture pour capturer le trafic sur une VM prise en charge ;
- topology et diagnostics complémentaires selon les fonctions disponibles.

Utiliser les outils disponibles dans le portail actuel et vérifier leurs prérequis. Certains outils nécessitent des autorisations, un agent, une extension ou une configuration de diagnostic.

## 15.3. VNet flow logs : choix recommandé pour les nouveaux déploiements

Les **Virtual Network flow logs** collectent des informations sur le trafic IP entrant et sortant associé à un VNet. Les logs peuvent notamment inclure le sens du flux, le protocole, les adresses et ports, l'état du flux et des informations de débit, selon le format et les capacités documentés.

Point important d'actualité : Microsoft indique que la création de nouveaux NSG flow logs n'est plus prise en charge depuis le 30 juin 2025 et que les NSG flow logs doivent être retirés le 30 septembre 2027. Pour un nouveau déploiement, privilégier VNet flow logs et planifier la migration des configurations historiques.

Avant d'activer des logs, vérifier les coûts de stockage, d'analyse et de rétention. Éviter les doublons de journalisation lorsqu'on remplace un mécanisme historique par VNet flow logs.

## 15.4. Ne pas confondre flow logs et capture de paquets

Les flow logs donnent une vue des flux selon le format supporté. Une capture de paquets fournit une observation plus détaillée des paquets au point de capture, mais doit être limitée, contrôlée et utilisée en respectant la confidentialité.

Les flow logs ne constituent pas automatiquement une preuve de contenu applicatif, et une absence de log n'est pas toujours une preuve qu'aucun paquet n'a existé. Vérifier la portée, les délais de collecte, l'état de la configuration et la destination des logs.

## 15.5. Azure Monitor et alertes

Définir des alertes adaptées à l'exploitation :

- baisse ou perte de connectivité VPN ;
- saturation ou hausse anormale des connexions ;
- hausse des refus ou des flux inattendus ;
- disponibilité du pare-feu ou des appliances ;
- augmentation de la latence applicative ;
- erreurs de résolution DNS ;
- changements de configuration importants.

Les indicateurs et seuils doivent être basés sur la capacité du système. Une alerte trop sensible peut créer du bruit ; une alerte trop large peut masquer une vraie panne.

## 15.6. Conservation et sécurité des logs

Décider :

- qui peut lire les logs ;
- où ils sont stockés ;
- combien de temps ils sont conservés ;
- quels événements sont envoyés à Log Analytics ou à un SIEM ;
- comment les données sensibles sont protégées ;
- comment on teste que la collecte fonctionne ;
- qui reçoit les alertes et selon quel processus d'escalade.


# 16. Méthode de dépannage structurée

## 16.1. Règle générale

Ne modifiez pas simultanément la route, le NSG, le DNS et le pare-feu. Une série de changements simultanés peut masquer la cause réelle et introduire de nouvelles pannes.

Suivez une démarche reproductible :

1. décrire le symptôme ;
2. identifier la source, la destination, le protocole et le port ;
3. tester la résolution DNS ;
4. vérifier le chemin de routage ;
5. vérifier les règles de sécurité ;
6. vérifier le service d'écoute ;
7. consulter les journaux ;
8. corriger une hypothèse à la fois ;
9. retester le même flux ;
10. documenter la cause et la prévention.

## 16.2. La fiche d'incident minimale

```text
ID incident : INC-XXXX
Heure de début : YYYY-MM-DD HH:MM UTC
Source : VNet / subnet / IP
Destination : FQDN / IP
Port et protocole : TCP 443, par exemple
Symptôme : timeout / refus immédiat / résolution incorrecte
Dernier changement connu : ...
Routes effectives examinées : oui / non
NSG contrôlés : oui / non
Pare-feu contrôlé : oui / non
DNS contrôlé : oui / non
Cause racine : ...
Correction : ...
Prévention : ...
```

## 16.3. Cas 1 — Une VM de production ne joint pas le serveur applicatif d'un autre spoke

Hypothèse : `10.20.2.10` veut joindre `10.30.1.5` sur TCP 8080.

Vérifications :

1. Le préfixe de `10.30.1.5` est-il correctement annoncé ou routé ?
2. Quelle route effective est utilisée sur l'interface de la VM source ?
3. Existe-t-il un UDR vers le pare-feu central ?
4. Le peering existe-t-il et ses deux côtés sont-ils configurés ?
5. Le pare-feu autorise-t-il le flux ?
6. La route du côté destination renvoie-t-elle le trafic par un chemin compatible ?
7. Le NSG de destination autorise-t-il TCP 8080 depuis la source attendue ?
8. L'application écoute-t-elle sur la bonne IP et le bon port ?

Ne commencez pas par ouvrir tous les ports. Identifiez d'abord l'endroit où le flux s'interrompt.

## 16.4. Cas 2 — Un Private Endpoint existe, mais l'application utilise le point public

Symptôme : la connexion échoue alors que le Private Endpoint est à l'état approuvé.

Diagnostic :

1. résoudre le nom de service depuis le client ;
2. comparer l'IP obtenue à l'IP privée du Private Endpoint ;
3. vérifier la zone DNS privée ;
4. vérifier le lien de la zone au VNet consommateur ;
5. vérifier les DNS personnalisés et redirecteurs ;
6. tester le port ;
7. vérifier l'approbation et la configuration du service.

Une correction DNS peut résoudre le problème sans modifier les routes de l'application.

## 16.5. Cas 3 — L'accès Internet disparaît après ajout d'une UDR

Diagnostic :

1. examiner les routes effectives de la VM ;
2. confirmer le prochain saut de `0.0.0.0/0` ;
3. vérifier que le pare-feu est joignable ;
4. examiner les règles applicatives et réseau du pare-feu ;
5. vérifier la route du pare-feu vers Internet ;
6. vérifier que le pare-feu dispose de la configuration de sortie attendue ;
7. vérifier les dépendances Azure, DNS, mise à jour et administration ;
8. contrôler les journaux du pare-feu.

Si le problème est apparu immédiatement après une UDR, comparez la route précédente et la route effective actuelle. Préparez une procédure de retour arrière avant d'agir en production.

## 16.6. Cas 4 — Le VPN est établi, mais aucune application locale n'est accessible

Un tunnel « connecté » ne prouve pas que tous les préfixes sont routés.

Vérifier :

- les préfixes locaux et Azure ;
- les routes apprises depuis BGP ou les routes statiques ;
- les routes effectives dans les VNet ;
- les routes du routeur local ;
- les NSG et les pare-feu des deux côtés ;
- le DNS si l'accès se fait par nom ;
- les routes de retour ;
- le MTU et les paramètres du tunnel si le symptôme est partiel.

## 16.7. Cas 5 — Un test ICMP échoue

Un échec de `ping` peut être dû au filtrage ICMP, à la configuration du système invité ou à la politique réseau. Tester le port TCP réellement nécessaire à l'application et utiliser les outils de diagnostic Azure appropriés.

## 16.8. Tableau de diagnostic rapide

| Symptôme | Première piste | Outil ou vérification |
|---|---|---|
| Nom inconnu | DNS ou suffixe | `Resolve-DnsName`, `nslookup` |
| Nom résout vers une mauvaise IP | Zone DNS, lien de VNet, redirecteur | Résolution depuis la source concernée |
| Timeout TCP | Route, NSG, pare-feu, service arrêté | Next hop, IP flow verify, Connection troubleshoot |
| Connexion refusée | Service non en écoute ou rejet actif | Vérifier l'écoute et les logs de l'OS |
| Internet cassé après UDR | Route par défaut et firewall | Routes effectives, règles et journaux firewall |
| VPN connecté, réseau inaccessible | Préfixes et routes de retour | Route Gateway, BGP, routeur local, NSG |
| Un seul sous-réseau est touché | Association UDR/NSG | Paramètres du subnet, routes effectives |
| Service PaaS inaccessible en privé | DNS / Private Endpoint | FQDN résolu et IP du PE |


# 17. Automatisation avec Azure CLI et Bicep

## 17.1. Pourquoi automatiser ?

Une configuration manuelle est pratique pour apprendre, mais difficile à reproduire exactement sur plusieurs environnements. L'infrastructure as code améliore la répétabilité, la revue de changement et la documentation.

L'automatisation doit suivre les mêmes principes que le travail manuel : plages correctes, noms explicites, routes documentées, sécurité minimale et test de validation.

## 17.2. Préparer Azure CLI

Les commandes ci-dessous supposent que l'utilisateur est authentifié et possède les droits nécessaires. Les noms, régions et abonnements sont des exemples.

```bash
az login
az account show
az account list --output table
# Facultatif : choisir explicitement un abonnement
az account set --subscription "<SUBSCRIPTION_ID_OU_NOM>"
```

Attention au contexte d'abonnement : avant de créer des ressources, toujours vérifier le résultat de `az account show`.

## 17.3. Créer un groupe de ressources et le VNet hub

```bash
az group create \
  --name rg-network-hub \
  --location westeurope

az network vnet create \
  --resource-group rg-network-hub \
  --name vnet-hub \
  --location westeurope \
  --address-prefixes 10.10.0.0/16 \
  --subnet-name snet-shared \
  --subnet-prefixes 10.10.10.0/24
```

Cette commande crée le VNet et un premier sous-réseau non spécialisé. Les sous-réseaux réservés aux services, comme `GatewaySubnet` ou `AzureFirewallSubnet`, doivent être créés et dimensionnés conformément aux exigences du service choisi.

## 17.4. Ajouter les sous-réseaux du hub

```bash
az network vnet subnet create \
  --resource-group rg-network-hub \
  --vnet-name vnet-hub \
  --name snet-management \
  --address-prefixes 10.10.20.0/24
```

Exemple d'ajout d'un sous-réseau spécialisé pour une passerelle VPN, **uniquement après validation du design et des prérequis de la passerelle** :

```bash
az network vnet subnet create \
  --resource-group rg-network-hub \
  --vnet-name vnet-hub \
  --name GatewaySubnet \
  --address-prefixes 10.10.1.0/27
```

Ne créez pas de passerelle sur la base de cet exemple sans vérifier la taille recommandée pour le SKU et les options envisagées.

## 17.5. Créer les spokes

```bash
az group create \
  --name rg-network-prod \
  --location westeurope

az network vnet create \
  --resource-group rg-network-prod \
  --name vnet-prod \
  --location westeurope \
  --address-prefixes 10.20.0.0/16 \
  --subnet-name snet-prod-web \
  --subnet-prefixes 10.20.1.0/24

az network vnet subnet create \
  --resource-group rg-network-prod \
  --vnet-name vnet-prod \
  --name snet-prod-app \
  --address-prefixes 10.20.2.0/24

az network vnet subnet create \
  --resource-group rg-network-prod \
  --vnet-name vnet-prod \
  --name snet-prod-data \
  --address-prefixes 10.20.3.0/24
```

```bash
az group create \
  --name rg-network-dev \
  --location westeurope

az network vnet create \
  --resource-group rg-network-dev \
  --name vnet-dev \
  --location westeurope \
  --address-prefixes 10.30.0.0/16 \
  --subnet-name snet-dev-app \
  --subnet-prefixes 10.30.1.0/24

az network vnet subnet create \
  --resource-group rg-network-dev \
  --vnet-name vnet-dev \
  --name snet-dev-test \
  --address-prefixes 10.30.2.0/24
```

## 17.6. Créer un peering entre hub et production

Azure CLI nécessite deux objets de peering, un de chaque côté. Les ID de ressources sont récupérés à partir des VNet.

```bash
HUB_ID=$(az network vnet show \
  --resource-group rg-network-hub \
  --name vnet-hub \
  --query id -o tsv)

PROD_ID=$(az network vnet show \
  --resource-group rg-network-prod \
  --name vnet-prod \
  --query id -o tsv)

az network vnet peering create \
  --resource-group rg-network-hub \
  --name hub-to-prod \
  --vnet-name vnet-hub \
  --remote-vnet "$PROD_ID" \
  --allow-vnet-access

az network vnet peering create \
  --resource-group rg-network-prod \
  --name prod-to-hub \
  --vnet-name vnet-prod \
  --remote-vnet "$HUB_ID" \
  --allow-vnet-access
```

Ces commandes établissent un peering de base. Elles ne configurent pas automatiquement tout transit, inspection ou routage forcé. Les options de forwarding et de gateway transit doivent être ajoutées uniquement lorsque le scénario le demande, puis testées.

## 17.7. Créer une table de routage et une UDR

Exemple de table `rt-prod-app` qui dirige la sortie IPv4 par défaut vers une appliance dont l'IP privée est `10.10.0.4`.

**Ne lancez cette commande que si le pare-feu existe, est configuré et est directement accessible selon le design.** Sinon, vous risquez de couper la sortie du sous-réseau.

```bash
az network route-table create \
  --resource-group rg-network-prod \
  --name rt-prod-app \
  --location westeurope

az network route-table route create \
  --resource-group rg-network-prod \
  --route-table-name rt-prod-app \
  --name default-via-firewall \
  --address-prefix 0.0.0.0/0 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.10.0.4

az network vnet subnet update \
  --resource-group rg-network-prod \
  --vnet-name vnet-prod \
  --name snet-prod-app \
  --route-table rt-prod-app
```

Avant de créer une telle route en production, tester le chemin du pare-feu et préparer un retour arrière. Cette commande ne crée pas le pare-feu et n'ajoute aucune règle autorisant le trafic.

## 17.8. Commandes de contrôle

```bash
az network vnet show \
  --resource-group rg-network-prod \
  --name vnet-prod \
  --output jsonc

az network vnet subnet list \
  --resource-group rg-network-prod \
  --vnet-name vnet-prod \
  --output table

az network vnet peering list \
  --resource-group rg-network-prod \
  --vnet-name vnet-prod \
  --output table

az network route-table route list \
  --resource-group rg-network-prod \
  --route-table-name rt-prod-app \
  --output table
```

La présence d'une ressource dans la sortie de ces commandes ne prouve pas que le trafic applicatif fonctionne. Il faut aussi contrôler les routes effectives, les règles de sécurité et le port utilisé.

## 17.9. Exemple de squelette Bicep

Ce squelette illustre un VNet et deux sous-réseaux applicatifs. Il n'inclut volontairement pas de pare-feu, de passerelle, de NSG ou de Private Endpoint. Ces composants demandent des choix complémentaires.

```bicep
param location string = resourceGroup().location
param vnetName string = 'vnet-prod'
param vnetAddressPrefix string = '10.20.0.0/16'

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: 'snet-prod-web'
        properties: {
          addressPrefix: '10.20.1.0/24'
        }
      }
      {
        name: 'snet-prod-app'
        properties: {
          addressPrefix: '10.20.2.0/24'
        }
      }
      {
        name: 'snet-prod-data'
        properties: {
          addressPrefix: '10.20.3.0/24'
        }
      }
    ]
  }
}
```

La version d'API doit être vérifiée avec le fournisseur de ressources et les fonctions réellement utilisées. Pour un déploiement de production, utiliser des modules réutilisables, valider le modèle et les paramètres, appliquer une revue de changement et tester dans un environnement non productif.

## 17.10. Principes d'infrastructure as code

- garder les modèles dans un dépôt versionné ;
- séparer paramètres non sensibles et secrets ;
- ne pas stocker de clés partagées en clair ;
- utiliser des identités et rôles avec privilèges minimaux ;
- effectuer une validation avant le déploiement ;
- utiliser des modules pour les composants réutilisables ;
- appliquer un nommage et des tags cohérents ;
- vérifier les différences avant une modification importante ;
- automatiser des tests post-déploiement ;
- documenter les changements de routes, de sécurité et de DNS.


# 18. Coûts, disponibilité et bonnes pratiques d'exploitation

## 18.1. Les coûts réseau à ne pas oublier

Le coût dépend du service, du SKU, de la région, de la durée et du volume de trafic. Il peut provenir notamment :

- des passerelles VPN et ExpressRoute ;
- d'Azure Firewall ;
- d'Azure Bastion et des autres services d'administration ;
- des Private Endpoints et du traitement de données applicable ;
- du transfert inter-régions ou vers l'extérieur ;
- des services de supervision, du stockage et de l'analyse des logs ;
- des appliances réseau et licences associées.

Ne concluez pas qu'un design est économique uniquement parce qu'il comporte peu de VMs. Les services réseau gérés peuvent représenter une part importante de la facture.

## 18.2. Évaluer la disponibilité

Pour chaque composant central, demander :

- Que se passe-t-il si le pare-feu est indisponible ?
- Les passerelles sont-elles dimensionnées selon le besoin ?
- La connectivité locale a-t-elle un chemin de secours ?
- Les spokes ont-ils des dépendances sur le DNS central ?
- Quel est l'impact d'une panne régionale ?
- Les mises à jour peuvent-elles interrompre une connexion ?
- Le plan de bascule a-t-il été testé ?

La redondance d'un seul composant ne garantit pas la résilience de toute l'architecture. Il faut analyser le chemin de bout en bout.

## 18.3. Journalisation minimale d'une architecture de production

Prévoir une destination et une rétention pour les journaux importants, tels que les flux réseau, les diagnostics du pare-feu et des passerelles, les opérations de contrôle et les journaux applicatifs pertinents.

Les journaux ne doivent pas être considérés comme activés simplement parce qu'un outil peut les produire : configurer la destination, vérifier l'arrivée des données, la rétention, les accès et les alertes.

## 18.4. Gouvernance

Une organisation peut mettre en œuvre :

- Azure Policy pour imposer des standards de réseau ;
- RBAC pour séparer administrateurs réseau, équipes applicatives et auditeurs ;
- tags pour attribuer les ressources aux équipes et aux centres de coûts ;
- alertes sur les changements de configuration sensibles ;
- inventaire des plages CIDR et des peerings ;
- revue périodique des NSG et des règles de pare-feu ;
- suppression contrôlée des ressources de test.

## 18.5. Checklist de mise en production

- Les CIDR ne se chevauchent pas.
- Les plages réservées à la croissance sont documentées.
- Le chemin de chaque flux critique est dessiné.
- Les UDR sont associées aux bons sous-réseaux.
- Les routes effectives ont été vérifiées.
- Les règles NSG et pare-feu sont minimales.
- Les Private Endpoints résolvent vers les IP privées attendues.
- La résolution DNS hybride est testée.
- La connectivité VPN/ExpressRoute est surveillée si elle existe.
- Les journaux et alertes sont opérationnels.
- La procédure de retour arrière est documentée.
- Les coûts récurrents et les coûts de trafic sont estimés.
- Les tests de bascule ont été réalisés selon les exigences du service.


# 19. Ateliers guidés

Les ateliers ci-dessous forment une progression. Le challenge final reprend leurs concepts mais impose un scénario plus ouvert.

## Atelier 1 — Concevoir le plan d'adressage

### Objectif

Proposer des CIDR pour un hub, un environnement de production, un environnement de développement et un réseau local, sans chevauchement.

### Données

Le réseau local existant est `10.250.0.0/16`. Il faut prévoir une plage dédiée au hub, deux VNet de workloads, et un VNet d'administration optionnel.

### Travail demandé

1. Choisir un CIDR pour `vnet-hub`.
2. Choisir un CIDR pour `vnet-prod`.
3. Choisir un CIDR pour `vnet-dev`.
4. Choisir un CIDR pour `vnet-admin`.
5. Découper au moins trois sous-réseaux de production.
6. Ajouter une réserve pour les Private Endpoints.
7. Expliquer comment l'organisation empêchera les chevauchements futurs.

### Exemple de correction

```text
vnet-hub  : 10.10.0.0/16
vnet-prod : 10.20.0.0/16
vnet-dev  : 10.30.0.0/16
vnet-admin: 10.40.0.0/16
on-prem   : 10.250.0.0/16
```

Sous-réseaux de production :

```text
10.20.1.0/24  Web
10.20.2.0/24  Application
10.20.3.0/24  Données
10.20.10.0/24 Private Endpoints
```

Cette solution est acceptable si ces plages sont libres dans l'inventaire réel de l'organisation. Documenter la propriété de chaque bloc et réserver les plages dans un registre central.

## Atelier 2 — Construire et valider les peerings

### Objectif

Créer un peering de base entre `vnet-hub` et `vnet-prod` puis vérifier son statut.

### Étapes

1. Créer les deux VNet dans la région de laboratoire.
2. Vérifier que leurs espaces d'adressage ne se chevauchent pas.
3. Créer le peering hub vers prod.
4. Créer le peering prod vers hub.
5. Vérifier les deux états de peering.
6. Si des VMs de test sont déployées, tester la connectivité avec un port applicatif prévu.
7. Consulter les routes effectives.

### Contrôle

Un peering avec un état incorrect ou en attente ne doit pas être déclaré fonctionnel. Un peering actif ne prouve pas non plus que les règles NSG autorisent les flux.

### Questions

- Le trafic entre les deux VNet a-t-il besoin de passer par un pare-feu ?
- Si oui, quelles routes et règles supplémentaires doivent être conçues ?
- Le peering permet-il automatiquement à un troisième VNet connecté au hub d'être transitivement accessible ?

**Réponse attendue :** non, il ne faut pas considérer le peering comme transitif. Un chemin de transit explicite doit être conçu.

## Atelier 3 — Concevoir une politique NSG Web/App/DB

### Objectif

Appliquer le moindre privilège à trois niveaux d'application.

### Schéma

```text
Client -> Web -> Application -> Base de données
         443     8080          1433
```

### Travail demandé

Définir les règles nécessaires pour que :

- les clients autorisés accèdent au Web sur TCP 443 ;
- le Web puisse joindre l'application sur TCP 8080 ;
- l'application puisse joindre la base sur TCP 1433 ;
- le Web ne puisse pas accéder directement à la base ;
- les connexions d'administration ne soient pas exposées à tout Internet.

### Correction de principe

Utiliser des NSG distincts par rôle ou par sous-réseau, et des ASG lorsque cela simplifie la gestion des interfaces. Limiter les sources et destinations aux groupes ou plages nécessaires. Le port SQL `1433` n'est qu'un exemple ; adapter au moteur et à sa configuration.

## Atelier 4 — Ajouter un Private Endpoint et vérifier le DNS

### Objectif

Comprendre pourquoi un Private Endpoint nécessite une configuration DNS correcte.

### Étapes générales

1. Déployer un service PaaS compatible avec Private Link dans un environnement de test.
2. Créer un Private Endpoint dans le sous-réseau réservé.
3. Vérifier son état et son IP privée.
4. Configurer la zone DNS privée recommandée pour le service.
5. Lier la zone au VNet consommateur.
6. Depuis une VM de test, résoudre le FQDN utilisé par le service.
7. Confirmer que la résolution conduit à l'IP privée attendue.
8. Tester le port et examiner les règles réseau.

### Validation

Ne pas considérer l'atelier réussi uniquement parce que la ressource Private Endpoint apparaît dans le portail. La résolution DNS et la connexion applicative doivent être validées depuis le réseau client réel.

## Atelier 5 — Mettre en place une UDR vers un pare-feu

### Objectif

Comprendre le routage forcé sans couper par inadvertance le trafic de gestion.

### Prérequis

Un pare-feu réellement déployé, une IP privée confirmée, une politique de sortie et une route de retour valides. Si aucun pare-feu n'existe, réaliser l'exercice sur papier seulement.

### Étapes

1. Définir le sous-réseau de test et la destination de test.
2. Examiner les routes effectives avant tout changement.
3. Créer une Route Table et une UDR adaptée.
4. Associer la table au sous-réseau de test seulement.
5. Vérifier le nouveau prochain saut.
6. Tester les destinations autorisées et refusées.
7. Vérifier les journaux du pare-feu.
8. Retirer la route ou la table de test si nécessaire et confirmer le retour à l'état initial.

### Résultat attendu

L'étudiant doit expliquer la différence entre :

- une route configurée ;
- une route effective ;
- une connexion permise par NSG ;
- une connexion autorisée par le pare-feu ;
- un service applicatif effectivement à l'écoute.


# 20. Exercices de compréhension et corrections

## Exercice 1 — Capacité IPv4

On vous donne un sous-réseau `10.20.5.0/24`.

1. Combien d'adresses IPv4 contient-il au total ?
2. Combien d'adresses sont réservées par Azure dans un sous-réseau IPv4 ?
3. Pourquoi faut-il malgré tout prévoir une marge ?

### Correction

1. `2^(32-24) = 256` adresses.
2. Azure réserve cinq adresses IPv4 par sous-réseau.
3. Les ressources peuvent nécessiter davantage d'adresses que prévu, les services ont parfois des contraintes propres et le dimensionnement doit permettre la croissance.

## Exercice 2 — Chevauchement

Deux équipes proposent :

```text
vnet-prod : 10.20.0.0/16
vnet-stage: 10.20.10.0/24
```

Peut-on les interconnecter comme deux VNet distincts avec un routage classique ?

### Correction

Non. Le CIDR de `vnet-stage` se trouve à l'intérieur du CIDR de `vnet-prod`. Réattribuer une plage distincte avant le déploiement est la meilleure option.

## Exercice 3 — Route la plus spécifique

La table contient :

```text
10.30.0.0/16 -> Virtual appliance 10.10.0.4
10.30.1.0/24 -> Virtual network peering
0.0.0.0/0    -> Internet
```

Quel chemin est candidat pour `10.30.1.10` ? Que devez-vous vérifier ensuite ?

### Correction

Le `/24` est plus spécifique que le `/16` et le `/0`. La route correspondante au peering est donc la candidate la plus spécifique. Il faut vérifier les routes effectives, la validité de la route du peering et les contrôles de sécurité. Dans une architecture réelle, la présence et la préférence des routes système spéciales doivent être confirmées par les outils Azure.

## Exercice 4 — Peering transitif

A est peeré avec B. B est peeré avec C. A peut-il nécessairement joindre C ?

### Correction

Non. Il ne faut pas supposer de transit automatique entre A et C. Il faut concevoir le mécanisme de transit approprié, les routes, les paramètres de forwarding et les règles de sécurité.

## Exercice 5 — NSG ou pare-feu ?

Une NSG autorise TCP 443 entre deux machines. Le flux échoue toujours, et une UDR envoie le trafic vers Azure Firewall.

Donnez au moins quatre explications possibles.

### Correction

- la règle du pare-feu refuse le flux ;
- la route ne mène pas vers l'IP attendue ;
- l'appliance n'est pas disponible ou n'a pas le chemin de retour ;
- une autre NSG bloque le flux ;
- le service n'écoute pas sur TCP 443 ;
- la destination DNS est incorrecte ;
- les routes aller et retour sont asymétriques.

## Exercice 6 — Private Endpoint

Un Private Endpoint est approuvé et possède une IP privée. Le client résout toutefois le FQDN du service vers une IP publique.

Quelle famille de configuration faut-il vérifier en premier ?

### Correction

DNS : zone privée, lien avec le VNet, nom de zone correspondant au service et résolution depuis le client. Ensuite, vérifier le routage et les règles réseau.

## Exercice 7 — VPN connecté

Le tunnel S2S apparaît connecté, mais les serveurs Azure n'accèdent pas à un serveur local.

Citez cinq vérifications pertinentes.

### Correction

- préfixes locaux et Azure sans chevauchement ;
- routes apprises ou statiques présentes ;
- routes de retour côté local ;
- NSG et pare-feu des deux côtés ;
- DNS si le serveur est appelé par nom ;
- règles de routage et BGP ;
- état des tunnels et journaux du dispositif local.

## Exercice 8 — Flow logs

Pour un nouveau projet de journalisation du trafic réseau Azure, faut-il partir sur de nouveaux NSG flow logs ou examiner VNet flow logs ?

### Correction

Privilégier VNet flow logs. La création de nouveaux NSG flow logs n'est plus prise en charge depuis le 30 juin 2025, et leur retrait est planifié pour le 30 septembre 2027. Valider les fonctionnalités et limites actuelles avant la migration.

## Exercice 9 — Contrôle de sortie

Une VM privée perd l'accès à Internet après l'ajout de `0.0.0.0/0 -> Virtual appliance`.

Établissez l'ordre de diagnostic.

### Correction

1. confirmer la route effective ;
2. vérifier l'IP privée et l'accessibilité du pare-feu ;
3. vérifier les règles du pare-feu ;
4. vérifier le chemin de sortie et les routes du pare-feu ;
5. vérifier NSG et dépendances nécessaires ;
6. consulter les logs ;
7. tester à nouveau les destinations exactes.

## Exercice 10 — Architecture à deux régions

Une entreprise possède deux VNet dans des régions distinctes et souhaite qu'ils communiquent.

Citez les éléments à étudier avant de choisir Global VNet Peering ou Azure Virtual WAN.

### Correction

- nombre de VNet et de régions ;
- chevauchement des CIDR ;
- besoins de transit et de routage hybride ;
- inspection et segmentation ;
- exigences de disponibilité et de latence ;
- coûts de transfert et de services ;
- gouvernance multi-abonnements ;
- opérations, surveillance et évolutivité.


# 21. Challenge final — Architecture Azure sécurisée

## 21.1. Scénario

Vous êtes administrateur réseau cloud dans une entreprise qui migre une application métier vers Azure.

L'entreprise possède :

- un réseau local `10.250.0.0/16` ;
- un VNet hub `10.10.0.0/16` ;
- un VNet production `10.20.0.0/16` ;
- un VNet développement `10.30.0.0/16`.

L'objectif est de concevoir une architecture qui permet aux applications de communiquer selon une politique documentée, limite les accès non nécessaires et prépare une connectivité hybride.

## 21.2. Besoins métiers et techniques

1. Le hub centralise la sortie Internet contrôlée et la connectivité hybride.
2. Le VNet production contient une couche Web, une couche applicative et une couche données.
3. Le VNet développement ne doit pas accéder librement à la production.
4. Le Web accède à l'application sur TCP 8080.
5. L'application accède à la base sur TCP 1433 dans ce scénario pédagogique.
6. L'application doit accéder à un compte Azure Storage via Private Endpoint.
7. Le DNS utilisé par l'application doit résoudre le service Storage vers le Private Endpoint.
8. Les ressources privées ne doivent pas recevoir d'accès entrant Internet direct non justifié.
9. Le réseau local doit pouvoir joindre un sous-ensemble d'adresses de production via un VPN S2S, sous réserve de la configuration complète de la passerelle et du réseau local.
10. La solution doit pouvoir être dépannée avec routes effectives, Network Watcher et journaux réseau.

Tous les ports et noms sont des valeurs de laboratoire. Ils doivent être adaptés aux services réellement utilisés.

## 21.3. Architecture à dessiner

Produisez un schéma montrant :

- les quatre blocs CIDR ;
- les sous-réseaux importants ;
- Azure Firewall ;
- `GatewaySubnet` et la connexion hybride ;
- les peerings ;
- les Route Tables et leurs associations ;
- les règles NSG principales ;
- le Private Endpoint et la résolution DNS ;
- les directions du trafic.

## 21.4. Travail demandé

### Partie A — Adressage (15 points)

1. Confirmer l'absence de chevauchement entre les quatre CIDR.
2. Définir les sous-réseaux Web, App, Data et Private Endpoint.
3. Réserver des plages de croissance.
4. Expliquer pourquoi les sous-réseaux spécialisés ne doivent pas accueillir des VMs ordinaires.

### Partie B — Routage et peering (20 points)

1. Décrire le peering hub-prod et hub-dev.
2. Expliquer pourquoi le peering n'est pas transitif.
3. Définir la stratégie de routage vers le pare-feu pour la sortie Internet.
4. Indiquer quelles routes supplémentaires seraient nécessaires si la politique exige l'inspection des flux inter-spokes.
5. Décrire les contrôles de route aller et retour.

### Partie C — Sécurité (15 points)

Définir les principales règles NSG et la politique de pare-feu. Inclure au minimum :

- HTTPS vers Web ;
- Web vers App ;
- App vers Data ;
- interdiction d'accès libre Dev vers Prod ;
- accès d'administration limité aux sources autorisées.

### Partie D — Private Endpoint et DNS (15 points)

1. Décrire la création logique du Private Endpoint.
2. Expliquer la zone DNS privée et son lien au VNet consommateur.
3. Définir les tests prouvant que le nom Storage résout vers l'IP privée.
4. Expliquer pourquoi l'état « Approved » ne suffit pas à prouver que l'application fonctionne.

### Partie E — Connectivité hybride (10 points)

Décrire les informations nécessaires à une connexion VPN S2S, les routes du réseau local et d'Azure, et les règles à vérifier avant de déclarer le VPN opérationnel.

### Partie F — Observabilité et dépannage (15 points)

Proposer une méthode pour diagnostiquer les cinq incidents suivants :

1. L'application ne joint pas la DB.
2. Le nom Storage résout vers l'IP publique.
3. La sortie Internet tombe après ajout d'une UDR.
4. Dev atteint une ressource de production de façon inattendue.
5. Le tunnel VPN apparaît connecté mais aucun paquet applicatif n'arrive au réseau local.

### Partie G — Exploitation et gouvernance (10 points)

Définir :

- les logs à activer ;
- les alertes principales ;
- les contrôles de coûts ;
- la documentation d'exploitation ;
- les tests de changement et de retour arrière.

## 21.5. Contraintes du challenge

- Ne pas autoriser tous les ports depuis toutes les sources.
- Ne pas déclarer le peering transitif par défaut.
- Ne pas considérer le DNS comme une fonction de routage.
- Ne pas considérer un tunnel VPN connecté comme une preuve de connectivité applicative.
- Ne pas appliquer aveuglément une route par défaut à `GatewaySubnet`.
- Ne pas déclarer le Private Endpoint opérationnel sans valider DNS et accès applicatif.
- Toute route via une appliance doit préciser la logique de retour et la présence de règles adaptées.

## 21.6. Barème sur 100

| Partie | Points |
|---|---:|
| A — Adressage | 15 |
| B — Routage et peering | 20 |
| C — Sécurité | 15 |
| D — Private Endpoint et DNS | 15 |
| E — Connectivité hybride | 10 |
| F — Observabilité et dépannage | 15 |
| G — Exploitation et gouvernance | 10 |
| **Total** | **100** |

### Interprétation du résultat

- **90–100 :** conception solide, raisonnement cohérent et diagnostic structuré.
- **75–89 :** bon niveau intermédiaire ; quelques lacunes de routage ou d'exploitation à corriger.
- **60–74 :** bases acquises, mais la conception doit être revue avant une mise en production.
- **Moins de 60 :** reprendre les chapitres sur routage, NSG, hub-and-spoke et DNS privé.

Ne vous notez pas uniquement sur l'existence d'un schéma. Une solution doit décrire des flux cohérents, des contrôles de sécurité, des routes de retour et une démarche de validation.


# 22. Correction du challenge final

Cette correction est une proposition de référence. D'autres architectures peuvent être valides si elles respectent les objectifs, les fonctionnalités Azure supportées, les règles de sécurité et les contraintes de routage.

## 22.1. Correction de la partie A — Adressage

### CIDR

```text
Hub          : 10.10.0.0/16
Production   : 10.20.0.0/16
Développement: 10.30.0.0/16
On-premises  : 10.250.0.0/16
```

Les blocs ne se chevauchent pas dans ce plan d'adressage.

### Sous-réseaux proposés

```text
VNET-HUB : 10.10.0.0/16
  AzureFirewallSubnet : 10.10.0.0/26   (exemple à valider)
  GatewaySubnet       : 10.10.1.0/27   (exemple à valider)
  snet-shared         : 10.10.10.0/24

VNET-PROD : 10.20.0.0/16
  snet-prod-web       : 10.20.1.0/24
  snet-prod-app       : 10.20.2.0/24
  snet-prod-data      : 10.20.3.0/24
  snet-prod-pe        : 10.20.10.0/24

VNET-DEV : 10.30.0.0/16
  snet-dev-app        : 10.30.1.0/24
  snet-dev-test       : 10.30.2.0/24
```

Les tailles des sous-réseaux `AzureFirewallSubnet` et `GatewaySubnet` doivent être vérifiées contre le service/SKU retenu. Les adresses de ces sous-réseaux ne sont pas destinées aux VMs de l'application.

## 22.2. Correction de la partie B — Routage et peering

### Peerings

Créer un peering dans chaque sens entre `vnet-hub` et `vnet-prod`, puis entre `vnet-hub` et `vnet-dev`. Vérifier les deux états, les espaces d'adressage et les options nécessaires au scénario.

### Sortie Internet de production

Pour les sous-réseaux à sortie contrôlée, associer une Route Table avec une UDR de type :

```text
Destination : 0.0.0.0/0
Next hop    : Virtual appliance
Next hop IP : IP privée d'Azure Firewall dans le hub
```

L'IP `10.10.0.4` peut être utilisée dans le laboratoire si elle correspond réellement à l'IP privée du pare-feu déployé. Ne jamais supposer qu'elle est automatique.

Le pare-feu doit autoriser explicitement les sorties nécessaires. Les routes et les contrôles doivent être validés après déploiement.

### Flux entre spokes

Le peering hub-prod et hub-dev ne rend pas le trafic prod-dev transitif par magie. Si la politique impose que les flux inter-spokes passent par le pare-feu :

1. définir les routes destination de chaque spoke vers le prochain saut de sécurité ;
2. confirmer que le prochain saut est joignable via la topologie de peering ;
3. autoriser le trafic transféré selon les options requises ;
4. créer les règles de pare-feu correspondantes ;
5. vérifier les routes du côté source et destination ;
6. vérifier que le retour suit un chemin compatible avec l'inspection stateful ;
7. tester le flux exact et consulter les journaux.

Une route possible, selon l'architecture approuvée, peut envoyer les préfixes distants via l'IP privée du pare-feu. Il faut vérifier les routes effectives et la topologie réelle plutôt que copier un UDR universel.

### Route de retour

Un flux autorisé dans le sens aller peut échouer si le chemin de retour contourne le pare-feu ou pointe vers une route non joignable. Le diagnostic doit donc inclure la route effective du serveur de destination, pas uniquement celle du client.

## 22.3. Correction de la partie C — Sécurité

Politique minimale proposée :

| Flux | Règle attendue | Port |
|---|---|---:|
| Source externe autorisée -> Web | Autoriser HTTPS sur le point d'entrée prévu | TCP 443 |
| Web -> App | Autoriser seulement les sources Web approuvées | TCP 8080 |
| App -> Data | Autoriser l'application vers la base | TCP 1433 dans le scénario |
| Dev -> Prod | Refuser par défaut, exceptions documentées seulement | Selon le besoin validé |
| Administration -> VMs | Restreindre aux sources et méthodes approuvées | Selon la solution d'administration |
| Web -> Data | Ne pas créer d'autorisation générale | Aucun accès direct prévu |

Les NSG structurent les flux locaux aux sous-réseaux ou interfaces. Azure Firewall applique la politique centralisée lorsque le trafic passe par lui. Les deux couches doivent être cohérentes. Les règles d'administration ne doivent pas ouvrir SSH ou RDP à toutes les IP Internet.

## 22.4. Correction de la partie D — Private Endpoint et DNS

1. Créer un Private Endpoint pour le service Storage compatible et le placer dans le sous-réseau choisi.
2. Vérifier le statut de la connexion privée et l'IP privée affectée.
3. Configurer la zone DNS privée recommandée pour le type de Storage utilisé.
4. Lier la zone au VNet consommateur ou utiliser une solution DNS hybride équivalente documentée.
5. Depuis une machine qui héberge l'application, résoudre le nom exact utilisé par le client.
6. Vérifier que la réponse attendue mène à l'IP privée du Private Endpoint.
7. Tester TCP 443 et l'accès applicatif avec les identifiants et autorisations appropriés.
8. Vérifier les restrictions d'accès public au service si la politique exige la désactivation du chemin public.

L'état « Approved » prouve que la relation Private Link est approuvée. Il ne prouve pas que le DNS du client est correct, que la route est valide, que les contrôles de sécurité autorisent le trafic ou que les autorisations au niveau du service permettent l'opération.

## 22.5. Correction de la partie E — VPN Site-to-Site

Données à réunir :

- préfixes locaux et préfixes Azure ;
- adresse publique du dispositif VPN local ;
- choix du type et du SKU de VPN Gateway ;
- paramètres IPsec/IKE compatibles ;
- clé partagée ou authentification configurée selon le scénario ;
- routes statiques ou paramètres BGP ;
- règles pare-feu du côté local et Azure ;
- configuration du transit de passerelle si les spokes doivent accéder au réseau local ;
- plan de supervision et de test de bascule.

Tests requis : tunnel établi, routes apprises, route de retour présente, DNS fonctionnel si des noms sont utilisés, et accès applicatif sur les ports prévus. Le statut de tunnel ne suffit pas à certifier le chemin de données.

## 22.6. Correction de la partie F — Observabilité et dépannage

### Incident 1 : App ne joint pas Data

1. Tester le nom de la base et obtenir l'IP effective.
2. Vérifier le port réellement utilisé.
3. Contrôler la route effective de la VM applicative.
4. Vérifier les NSG au niveau source et destination.
5. Vérifier le pare-feu et les UDR si le flux le traverse.
6. Vérifier que le serveur DB écoute et que le pare-feu invité ne bloque pas.
7. Examiner les logs et consigner la cause racine.

### Incident 2 : Storage résout vers l'IP publique

1. Examiner le résultat DNS depuis la VM applicative.
2. Vérifier la zone privée et le lien au VNet.
3. Vérifier les redirecteurs et paramètres DNS personnalisés.
4. Confirmer le FQDN attendu pour le service.
5. Tester le nom à nouveau, puis TCP 443.
6. Vérifier les journaux et la politique d'accès du Storage.

### Incident 3 : Internet tombe après une UDR

1. Examiner les routes effectives.
2. Confirmer l'adresse privée du pare-feu.
3. Confirmer la connectivité vers l'IP du pare-feu.
4. Vérifier les règles réseau et d'application de la politique de pare-feu.
5. Vérifier le routage de sortie et le retour.
6. Examiner les logs de refus.
7. Corriger une seule cause à la fois et préparer le rollback.

### Incident 4 : Dev atteint Prod de façon inattendue

1. Identifier les IP source/destination et le port.
2. Examiner le peering et les routes effectives.
3. Vérifier la présence d'une UDR plus spécifique ou d'une route attendue différemment.
4. Examiner les règles NSG de la source et de la destination.
5. Vérifier la politique et les logs du pare-feu si le trafic doit le traverser.
6. Identifier si le flux passe par un chemin qui contourne le point d'inspection.
7. Restreindre le flux au niveau le plus approprié, retester et documenter.

### Incident 5 : VPN connecté, aucun paquet applicatif au site local

1. Vérifier les préfixes annoncés ou statiques.
2. Vérifier les routes effectives dans Azure.
3. Examiner les routes de retour du routeur local.
4. Vérifier les ACL et règles de pare-feu du site local.
5. Tester l'IP et le port plutôt que le seul nom DNS.
6. Vérifier BGP et les journaux du tunnel.
7. Si nécessaire, utiliser une capture de paquets contrôlée.

### Choix des outils

- IP flow verify : vérifier un verdict de sécurité pour un flux.
- Next hop : examiner le prochain saut.
- Connection troubleshoot : analyser la connexion de bout en bout dans les scénarios pris en charge.
- VNet flow logs : analyser les flux dans le temps.
- Logs Azure Firewall et journaux du VPN : localiser les refus et problèmes de connectivité.
- DNS tools : confirmer la résolution utilisée par la machine cliente.

## 22.7. Correction de la partie G — Exploitation

### Logs

Activer VNet flow logs pour une observation des flux réseau et les diagnostics des services réseau concernés. Utiliser Azure Monitor/Log Analytics ou une destination adaptée à la politique de conservation. Vérifier que les données sont effectivement reçues.

Pour un nouveau déploiement, ne pas commencer par les NSG flow logs historiques : leur création n'est plus prise en charge depuis le 30 juin 2025 et ils sont programmés pour retrait le 30 septembre 2027.

### Alertes

- indisponibilité de la passerelle ou perte du tunnel ;
- baisse de connectivité applicative ;
- volume de refus anormal ;
- changement des routes ou règles de pare-feu ;
- hausse inhabituelle de trafic ;
- échec de résolution DNS pour les services essentiels ;
- ressources réseau ou logs proches d'une limite opérationnelle.

### Coûts

Suivre les coûts Azure Firewall, VPN Gateway, ExpressRoute, Private Endpoints, transferts de données, stockage et analyse des logs. Utiliser des tags et budgets adaptés à la granularité de l'organisation.

### Documentation d'exploitation

Maintenir :

- un schéma à jour ;
- un inventaire CIDR ;
- la matrice des flux autorisés ;
- les route tables et leur association ;
- la politique de pare-feu ;
- les zones DNS et leurs liens ;
- la configuration VPN/BGP ;
- le plan d'escalade ;
- le plan de retour arrière ;
- les résultats des tests de bascule.

## 22.8. Schéma final de référence

```text
                          RÉSEAU LOCAL
                           10.250/16
                               |
                         VPN Site-to-Site
                               |
                               v
+-------------------------------------------------------------------+
| VNET-HUB : 10.10.0.0/16                                           |
|                                                                   |
|  +-------------------------+     +------------------------------+  |
|  | Azure Firewall          |     | GatewaySubnet / VPN Gateway  |  |
|  | règles centralisées     |     | routes hybrides              |  |
|  +-----------+-------------+     +------------------------------+  |
|              |                                                    |
+--------------+----------------------------------------------------+
               |                                   |
           Peering                             Peering
               |                                   |
               v                                   v
+-------------------------------+  +-------------------------------+
| VNET-PROD 10.20.0.0/16        |  | VNET-DEV 10.30.0.0/16         |
|                               |  |                               |
| Web  10.20.1.0/24             |  | App/Test                      |
|   | HTTPS entrant              |  | 10.30.1.0/24                  |
|   v                           |  |                               |
| App  10.20.2.0/24             |  | accès à Prod interdit par     |
|   | TCP 8080                   |  | défaut                        |
|   v                           |  +-------------------------------+
| Data 10.20.3.0/24             |
|   | TCP 1433                   |
|   v                           |
| Base de données               |
|                               |
| Private Endpoint 10.20.10.0/24|
|   | DNS privé                  |
|   v                           |
| Azure Storage via Private Link|
+-------------------------------+

Sortie Internet des sous-réseaux concernés : UDR -> Firewall -> règles autorisées.
Les routes, règles NSG, règles de pare-feu et retours doivent être validés des deux côtés.
```

## 22.9. Critères d'une bonne réponse

Une bonne réponse au challenge ne se limite pas à recopier le schéma. Elle doit expliquer :

- pourquoi les CIDR sont valides et non chevauchants ;
- où les routes sont appliquées ;
- pourquoi le peering n'est pas automatiquement transitif ;
- comment le pare-feu devient effectivement un point de passage ;
- comment les NSG appliquent le moindre privilège ;
- pourquoi DNS est essentiel au Private Endpoint ;
- quelles routes doivent exister sur les deux côtés du VPN ;
- comment les outils Azure permettent de distinguer DNS, routage et filtrage ;
- comment limiter les coûts et restaurer un état stable après un changement.


# 23. Checklist finale

## Adressage et topologie

- [ ] Les CIDR des VNet ne se chevauchent pas.
- [ ] Les plages on-premises et Azure sont compatibles.
- [ ] Chaque sous-réseau a un rôle documenté.
- [ ] Les sous-réseaux spécialisés respectent les exigences du service.
- [ ] Les réserves CIDR sont connues des équipes.

## Routage

- [ ] Les peerings sont établis dans les deux sens.
- [ ] Le transit n'est pas supposé automatique.
- [ ] Les UDR sont associées aux bons sous-réseaux.
- [ ] Les routes effectives ont été examinées.
- [ ] Le prochain saut est joignable.
- [ ] Les routes de retour sont cohérentes.
- [ ] Les sous-réseaux de passerelle n'ont pas reçu de routes hasardeuses.

## Sécurité

- [ ] Les règles NSG sont minimales.
- [ ] Les sources d'administration sont restreintes.
- [ ] Les règles de pare-feu correspondent aux flux documentés.
- [ ] Les flux inter-spokes suivent la politique annoncée.
- [ ] Les contrôles IPv4 et IPv6 sont cohérents si dual-stack.
- [ ] Les règles temporaires de diagnostic ont été retirées.

## Private Link et DNS

- [ ] Le Private Endpoint est approuvé et correctement connecté.
- [ ] Le DNS résout vers l'IP privée attendue.
- [ ] La zone privée est liée aux bons VNet ou résolue par le système hybride choisi.
- [ ] Le service est testé depuis le réseau client.
- [ ] Les politiques d'accès public du PaaS sont conformes à l'objectif.

## Connectivité hybride

- [ ] Les préfixes locaux et Azure sont corrects.
- [ ] Les routes BGP ou statiques sont vérifiées.
- [ ] Les retours fonctionnent.
- [ ] Le tunnel ou circuit est supervisé.
- [ ] Les tests de bascule sont documentés.

## Supervision et exploitation

- [ ] Les VNet flow logs et diagnostics nécessaires sont configurés.
- [ ] La collecte et la rétention des journaux sont vérifiées.
- [ ] Les alertes ont des responsables.
- [ ] Les coûts récurrents et le traitement de données sont estimés.
- [ ] Les procédures de changement et de retour arrière sont écrites.
- [ ] Le schéma reflète l'architecture réellement déployée.


# 24. Glossaire et documentation officielle

## 24.1. Glossaire

| Terme | Définition pratique |
|---|---|
| VNet | Réseau virtuel Azure |
| Subnet | Segment d'adressage au sein d'un VNet |
| CIDR | Notation d'une plage IP avec longueur de préfixe |
| UDR | User Defined Route, route personnalisée associée à un sous-réseau |
| NSG | Network Security Group, règles de filtrage réseau Azure |
| ASG | Application Security Group, regroupement logique d'interfaces pour les règles NSG |
| NVA | Network Virtual Appliance, appliance réseau logicielle |
| Azure Firewall | Service de pare-feu géré par Azure |
| VNet Peering | Interconnexion de deux VNet via le réseau backbone Azure |
| Gateway Transit | Possibilité pour un VNet peeré d'utiliser la passerelle d'un autre VNet dans un scénario pris en charge |
| VPN S2S | VPN Site-to-Site entre un réseau local et Azure |
| ExpressRoute | Service de connectivité privée entre un réseau et Microsoft/Azure |
| BGP | Protocole dynamique d'échange de routes |
| Private Endpoint | Interface réseau à IP privée connectée à un service via Private Link |
| Service Endpoint | Fonctionnalité donnant au service Azure un contexte de sécurité réseau du VNet, sans créer l'IP privée de service utilisée par un Private Endpoint |
| DNS | Système de résolution des noms en adresses IP |
| Flow logs | Journaux de flux IP utiles à l'observation des communications |
| Network Watcher | Ensemble d'outils Azure pour observer et diagnostiquer les réseaux |
| Longest prefix match | Choix de la route au préfixe correspondant le plus spécifique, dans les règles de sélection applicables |
| Routage asymétrique | Chemin retour différent du chemin aller |

## 24.2. Documentation Microsoft Learn

Les liens suivants sont des références officielles à consulter pour valider les limitations, les paramètres et les procédures applicables à votre déploiement. Les pages de documentation évoluent : vérifier leur date de mise à jour et le SKU/produit concerné avant une mise en production.

### Routage et VNet Peering

- Vue d'ensemble du routage des flux Azure : https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview
- Vue d'ensemble du VNet Peering : https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview
- Vue d'ensemble du réseau virtuel Azure : https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview

### Sécurité et appliances réseau

- Guide de conception NSG et ASG : https://learn.microsoft.com/en-us/azure/networking/design-guide/network-application-security-groups
- Vue d'ensemble d'Azure Firewall : https://learn.microsoft.com/en-us/azure/firewall/overview
- Documentation Azure Firewall : https://learn.microsoft.com/en-us/azure/firewall/

### Private Link et DNS

- Vue d'ensemble de Private Endpoint : https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview
- Configuration DNS des Private Endpoints : https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns
- DNS privé Azure : https://learn.microsoft.com/en-us/azure/dns/private-dns-overview

### VPN et routage dynamique

- Documentation Azure VPN Gateway : https://learn.microsoft.com/en-us/azure/vpn-gateway/
- Paramètres de configuration VPN Gateway : https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-gateway-settings
- Conception d'Azure VPN Gateway : https://learn.microsoft.com/en-us/azure/vpn-gateway/design
- Vue d'ensemble d'Azure Route Server : https://learn.microsoft.com/en-us/azure/route-server/overview
- Documentation ExpressRoute : https://learn.microsoft.com/en-us/azure/expressroute/

### Supervision et dépannage

- Vue d'ensemble des VNet flow logs : https://learn.microsoft.com/en-us/azure/network-watcher/vnet-flow-logs-overview
- FAQ Network Watcher : https://learn.microsoft.com/en-us/azure/network-watcher/frequently-asked-questions
- Conception de la supervision réseau : https://learn.microsoft.com/en-us/azure/networking/design-guide/monitor
- Dépannage des NSG qui bloquent le trafic : https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-network/virtual-network-troubleshoot-nsg-blocking-traffic

### Automatisation

- Documentation Azure CLI : https://learn.microsoft.com/en-us/cli/azure/
- Documentation Bicep : https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/


# Fin du cours — Azure VNet intermédiaire

**À retenir :** une architecture réseau cloud fiable se prouve par les routes effectives, les règles qui s'appliquent, la résolution DNS réelle et des tests applicatifs reproductibles. Un VNet, un peering, un VPN ou un Private Endpoint correctement affiché dans le portail ne suffit pas à démontrer que tout le chemin fonctionne. Concevez le flux de bout en bout, contrôlez le retour, instrumentez les logs et documentez chaque changement.
