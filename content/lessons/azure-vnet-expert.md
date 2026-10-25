# Azure Virtual Network (VNet) — Cours complet de niveau expert

**Fichier :** `azure-vnet-expert.md`  
**Domaine :** Architecture réseau cloud, sécurité, connectivité hybride et exploitation Azure  
**Niveau :** Expert  
**Durée indicative :** 24 à 40 heures, ateliers et challenge compris  
**Prérequis :** Maîtriser IPv4/CIDR, le routage, NSG/ASG, les UDR, VNet Peering, Azure Firewall, Private Link, DNS privé, VPN Gateway et les bases d'ExpressRoute.  
**Méthode :** Cours d'architecture approfondi, schémas textuels, matrices de flux, décisions de conception, exemples Azure CLI/Bicep, ateliers guidés, exercices corrigés et challenge final.

> **Objectif pédagogique :** concevoir, justifier, déployer et exploiter des architectures Azure réseau complexes, multi-abonnements et multi-régions, tout en maîtrisant le routage effectif, l'inspection, la connectivité hybride, le DNS, la résilience, l'observabilité et le dépannage de bout en bout.
>
> **Document autonome :** toutes les parties du cours, les schémas, les ateliers, les exercices, le challenge final et sa correction sont réunis dans ce seul fichier Markdown. Aucun fichier complémentaire n'est nécessaire.
>
> **Note d'exploitation :** les portails, SKU, quotas, options de routage et tarifs Azure évoluent. Avant une mise en production, vérifie les capacités et limitations de la région, du SKU et du service dans la documentation officielle liée à la fin du document. Les exemples d'adressage et de ressources sont pédagogiques et doivent être adaptés à l'organisation.


# SOMMAIRE

1. [Objectifs et posture d'ingénieur réseau expert](#1-objectifs-et-posture-dingénieur-réseau-expert)
2. [Architecture de référence et hypothèses](#2-architecture-de-référence-et-hypothèses)
3. [Plan d'adressage à l'échelle de l'organisation](#3-plan-dadressage-à-léchelle-de-lorganisation)
4. [Routage Azure approfondi](#4-routage-azure-approfondi)
5. [Choisir entre hub-and-spoke et Azure Virtual WAN](#5-choisir-entre-hub-and-spoke-et-azure-virtual-wan)
6. [Hub-and-spoke multi-région et inspection centralisée](#6-hub-and-spoke-multi-région-et-inspection-centralisée)
7. [Azure Firewall, NVA et chaîne d'inspection](#7-azure-firewall-nva-et-chaîne-dinspection)
8. [Connectivité hybride de niveau production](#8-connectivité-hybride-de-niveau-production)
9. [BGP, Azure Route Server et sélection des chemins](#9-bgp-azure-route-server-et-sélection-des-chemins)
10. [DNS privé et résolution hybride à grande échelle](#10-dns-privé-et-résolution-hybride-à-grande-échelle)
11. [Private Link, PaaS privé et exfiltration contrôlée](#11-private-link-paas-privé-et-exfiltration-contrôlée)
12. [Segmentation, gouvernance et défense en profondeur](#12-segmentation-gouvernance-et-défense-en-profondeur)
13. [IPv6, chiffrement réseau et contraintes particulières](#13-ipv6-chiffrement-réseau-et-contraintes-particulières)
14. [Observabilité, diagnostics et exploitation](#14-observabilité-diagnostics-et-exploitation)
15. [Performance, capacité, disponibilité et coûts](#15-performance-capacité-disponibilité-et-coûts)
16. [Automatisation et Infrastructure as Code](#16-automatisation-et-infrastructure-as-code)
17. [Méthodologie experte de dépannage](#17-méthodologie-experte-de-dépannage)
18. [Ateliers guidés](#18-ateliers-guidés)
19. [Exercices de compréhension avec corrigés](#19-exercices-de-compréhension-avec-corrigés)
20. [Challenge final — Réseau Azure d'entreprise multi-région](#20-challenge-final--réseau-azure-dentreprise-multi-région)
21. [Correction détaillée du challenge](#21-correction-détaillée-du-challenge)
22. [Checklist de revue d'architecture](#22-checklist-de-revue-darchitecture)
23. [Glossaire](#23-glossaire)
24. [Documentation officielle et références](#24-documentation-officielle-et-références)


# 1. Objectifs et posture d'ingénieur réseau expert

## 1.1. Du niveau intermédiaire au niveau expert

Le niveau débutant permet de créer un VNet, de définir des sous-réseaux, d'associer des NSG et de comprendre les routes de base. Le niveau intermédiaire ajoute les architectures hub-and-spoke, les UDR, le peering, les connexions hybrides, les services privés et les diagnostics.

Le niveau expert s'intéresse surtout aux **interactions entre domaines techniques** et aux conséquences des choix d'architecture :

- comment une route propagée par BGP interagit avec une UDR ;
- comment empêcher qu'un chemin de retour contourne un pare-feu ;
- comment centraliser l'inspection sans créer de point de défaillance ou de goulot d'étranglement ;
- comment organiser DNS privé dans plusieurs régions et avec un réseau local ;
- comment éviter qu'un accès Private Endpoint soit seulement privé en apparence ;
- comment gérer les adresses IP sur plusieurs abonnements et plusieurs équipes ;
- comment construire une stratégie de reprise après sinistre qui fonctionne réellement ;
- comment prouver qu'une politique réseau est appliquée par les routes effectives, les règles et les logs.

Un ingénieur expert n'affirme pas simplement que « le réseau est configuré ». Il peut montrer le chemin aller, le chemin retour, les routes retenues, les règles évaluées, les journaux associés et les tests reproductibles.

## 1.2. Principes d'architecture à appliquer

### Principe 1 — Raisonner en flux de bout en bout

Pour chaque flux, documenter la source, la destination, le protocole, le port, la route, le point d'inspection et le chemin de retour.

| Champ | Exemple |
|---|---|
| Source | VM Web `10.20.10.10` |
| Destination | API `10.30.20.15` |
| Protocole/port | TCP/8443 |
| Route attendue | UDR vers Azure Firewall dans le hub |
| Sécurité | NSG source, Azure Firewall, NSG destination |
| DNS | `api.contoso.internal` vers IP privée de l'API |
| Retour | API vers le même chemin d'inspection si l'architecture l'exige |
| Preuve | Route effective, test TCP, logs du pare-feu et VNet flow logs |

### Principe 2 — Ne pas confondre connectivité et autorisation

Un peering établit une connectivité entre deux VNet, mais ne remplace ni une route valide ni les règles de sécurité. Une route existante ne signifie pas que le pare-feu autorise le flux. Une règle de pare-feu qui autorise un flux ne garantit pas que le routage l'amène jusqu'à ce pare-feu.

```text
Résolution DNS correcte
        |
        v
Route de destination correcte
        |
        v
Chemin d'inspection attendu
        |
        v
Règles de sécurité autorisantes
        |
        v
Route de retour cohérente
        |
        v
Service à l'écoute + réponse applicative
```

Chaque étape doit être vérifiée indépendamment.

### Principe 3 — Éviter les exceptions implicites

Les exceptions non documentées (une UDR oubliée, une règle `Any/Any`, un peering historique ou une route BGP inattendue) sont sources de dérives. Chaque exception doit avoir un propriétaire, un motif, une portée, une date de révision et des tests.

### Principe 4 — Préférer un design démontrable

Une architecture est bonne si l'équipe peut expliquer et tester son comportement nominal, sa dégradation et son rétablissement. Un diagramme esthétique sans tables de routes effectives, flux autorisés et procédure de reprise n'est pas une preuve.

## 1.3. Les quatre plans à distinguer

| Plan | Question | Exemples |
|---|---|---|
| Plan de contrôle | Qui configure et distribue les objets réseau ? | ARM, politiques, Bicep, Azure CLI |
| Plan de routage | Où le paquet est-il envoyé ? | Routes système, UDR, BGP, next hop |
| Plan de sécurité | Le flux est-il autorisé ? | NSG, Azure Firewall, NVA, règles de service |
| Plan d'observabilité | Comment prouver ce qui s'est produit ? | Network Watcher, VNet flow logs, diagnostics, logs Firewall |

Une modification du plan de contrôle peut entraîner des changements de routage ou de sécurité. La validation doit porter sur l'état effectif, pas seulement sur la réussite d'une commande.


# 2. Architecture de référence et hypothèses

## 2.1. Scénario d'entreprise utilisé dans le cours

Nous concevons une organisation fictive nommée **Contoso**. Elle possède deux régions Azure, plusieurs applications, un réseau local, des services PaaS privés et un besoin d'inspection centralisée.

Plages de démonstration :

| Domaine | CIDR proposé | Rôle |
|---|---|---|
| Région primaire — hub | `10.0.0.0/16` | Firewall, gateways et services partagés |
| Région primaire — Spoke Web | `10.10.0.0/16` | Frontaux Web |
| Région primaire — Spoke Apps | `10.20.0.0/16` | Services applicatifs |
| Région primaire — Spoke Data | `10.30.0.0/16` | Données et services sensibles |
| Région secondaire — hub | `10.100.0.0/16` | Hub de reprise / région secondaire |
| Région secondaire — Spoke DR | `10.110.0.0/16` | Capacité de reprise |
| Réseau local | `172.20.0.0/16` | Serveurs et services de l'entreprise |
| Réseau de succursales | `172.24.0.0/16` | Sites distants |

Ces adresses ne sont que des exemples. Il faut vérifier qu'elles ne chevauchent aucune plage existante, notamment celles des partenaires, des acquisitions, des conteneurs, des réseaux VPN et des autres clouds.

## 2.2. Architecture globale cible

```text
                              INTERNET
                                  |
                         [ Accès public maîtrisé ]
                                  |
                 +----------------+----------------+
                 |                                 |
          RÉGION PRIMAIRE                    RÉGION SECONDAIRE
          Hub 10.0.0.0/16                   Hub 10.100.0.0/16
          +----------------+                +----------------+
          | Azure Firewall |                | Azure Firewall |
          | VPN/ER Gateway |                | VPN/ER Gateway |
          | DNS Resolver   |                | DNS/DR services |
          +---+--------+---+                +--------+-------+
              |        |                             |
       +------+--+  +--+-------+              +------+------+
       | Spoke   |  | Spoke    |              | Spoke DR    |
       | Web     |  | Apps     |              | 10.110/16   |
       |10.10/16 |  |10.20/16  |              +-------------+
       +---------+  +-----+----+
                          |
                    +-----+-----+
                    | Spoke Data|
                    | 10.30/16  |
                    +-----------+
                          |
                  Private Endpoints PaaS

      RÉSEAU LOCAL 172.20.0.0/16 ---- VPN / ExpressRoute ---- Hub
      SUCCURSALES  172.24.0.0/16 ---- VPN / SD-WAN --------- Hub
```

Ce dessin illustre une architecture possible, pas un déploiement imposé. Le modèle exact dépend de la taille, des objectifs de latence, du nombre de connexions, des contraintes d'exploitation, des coûts et des capacités des services dans les régions choisies.

## 2.3. Qui possède quoi ?

Une organisation peut répartir la responsabilité entre plusieurs équipes :

| Équipe | Responsabilité habituelle |
|---|---|
| Plateforme réseau | CIDR global, hubs, passerelles, routage central, DNS, pare-feu partagé |
| Équipes applicatives | Sous-réseaux et règles spécifiques au workload, selon le modèle de gouvernance |
| Sécurité | Politique de filtrage, exigences de journalisation, gestion des exceptions |
| Exploitation | Supervision, runbooks, tests et incidents |
| FinOps | Budgets, étiquetage, revue du coût des gateways, firewalls, logs et transferts |

Les droits RBAC doivent respecter la séparation des responsabilités. Un propriétaire d'application ne devrait pas pouvoir supprimer une route centrale ou désactiver l'inspection partagée sans contrôle approprié.

## 2.4. Choisir une architecture auto-gérée ou Virtual WAN

Deux modèles sont fréquents :

**Hub-and-spoke auto-géré** : l'équipe maîtrise les VNet hubs, les peerings, les UDR, Azure Firewall et les gateways. Ce modèle donne du contrôle mais demande une gouvernance précise.

**Azure Virtual WAN** : le service fournit une architecture de hubs virtuels, des connexions de branche et de VNet, des tables de routage et des options de routage centralisé. Le SKU, les fonctionnalités exactes, les limites et les coûts doivent être vérifiés avant la conception.

Le choix doit être documenté. Éviter de commencer par un produit sans connaître les exigences de routage, la topologie, le modèle d'exploitation et la manière de migrer.


# 3. Plan d'adressage à l'échelle de l'organisation

## 3.1. L'adressage est une décision d'architecture

Un plan CIDR mal conçu entraîne des renumérotations coûteuses, des routes ambiguës et des limites de connectivité lors des acquisitions ou des extensions multi-cloud.

Avant de réserver une plage, inventorier :

- les VNet existants, y compris les environnements historiques peu documentés ;
- les réseaux locaux, filiales et réseaux de partenaires ;
- les plages annoncées par BGP ;
- les plages des clusters Kubernetes et de leurs services ;
- les plages de conteneurs, de VPN clients et des environnements de test ;
- les réserves pour le développement futur, la reprise et les migrations.

## 3.2. Construire une hiérarchie d'agrégation

Exemple pédagogique :

```text
10.0.0.0/8                     Domaine cloud entreprise
|
+-- 10.0.0.0/12                Environnements de production
|   +-- 10.0.0.0/16            Hub région primaire
|   +-- 10.10.0.0/16           Spoke Web
|   +-- 10.20.0.0/16           Spoke Apps
|   +-- 10.30.0.0/16           Spoke Data
|
+-- 10.32.0.0/12               Environnements non-production
|
+-- 10.100.0.0/14              Réserve région secondaire (exemple à valider)
```

Les sous-plages doivent être mathématiquement incluses dans les préfixes parents et ne pas se chevaucher. Ne copie pas le schéma sans vérifier les alignements CIDR : c'est une représentation d'allocation, pas la preuve que chaque préfixe indiqué est une allocation optimale.

## 3.3. Concevoir les tailles de sous-réseaux

Exemple pour le spoke applicatif `10.20.0.0/16` :

| Sous-réseau | CIDR d'exemple | Fonction |
|---|---|---|
| `snet-app` | `10.20.10.0/24` | Machines applicatives |
| `snet-private-endpoints` | `10.20.20.0/24` | Private Endpoints, selon la politique choisie |
| `snet-build` | `10.20.30.0/24` | Agents de déploiement contrôlés |
| `snet-management` | `10.20.40.0/24` | Outils d'administration internes |

Le dimensionnement doit considérer les adresses réellement utilisables, les services déployés, les extensions d'architecture et les sous-réseaux réservés par certains services Azure. Des tailles incorrectes peuvent empêcher un déploiement ou une mise à l'échelle ultérieure.

## 3.4. Inventaire IP et contrôle du chevauchement

À l'échelle d'une entreprise, conserver un référentiel qui indique :

- préfixe alloué ;
- VNet et sous-réseau propriétaires ;
- région et abonnement ;
- environnement ;
- responsable ;
- date d'allocation ;
- réserves et statut ;
- préfixes annoncés par VPN/ExpressRoute ;
- dépendances de routage et de DNS.

Azure Virtual Network Manager et Azure IPAM peuvent apporter des capacités de gestion réseau à grande échelle, selon les fonctionnalités et le modèle d'organisation retenus. Il faut vérifier les fonctions et limites réellement disponibles dans l'environnement.

## 3.5. Que faire si les plages se chevauchent ?

Un chevauchement empêche souvent d'établir un routage IP direct non ambigu. Options possibles, par ordre de préférence selon le contexte :

1. renuméroter pendant une migration planifiée ;
2. isoler temporairement l'environnement et limiter les flux ;
3. utiliser une solution de traduction d'adresses prise en charge lorsqu'elle résout réellement le besoin ;
4. revoir l'architecture de connectivité plutôt que créer des routes contradictoires.

La traduction d'adresses ne doit pas être traitée comme une solution magique : elle complique les journaux, l'identité des sources, le dépannage et les flux initiés dans les deux sens.

### Exercice 3.A

Deux VNet utilisent respectivement `10.40.0.0/16` et `10.40.10.0/24`. Sont-ils disjoints ?

**Correction :** non. Le `/24` est contenu dans le `/16`. Un peering normal entre ces plages qui se chevauchent n'est pas une solution valide de connectivité. Il faut renuméroter ou définir une approche d'isolation/traduction explicitement prise en charge.


# 4. Routage Azure approfondi

## 4.1. Les sources de routes

Azure peut associer plusieurs types de routes à une interface réseau :

- **routes système** fournies par la plateforme ;
- **routes définies par l'utilisateur (UDR)**, associées à une table de routage ;
- **routes propagées par BGP**, par exemple depuis une passerelle ou une appliance prise en charge.

La table effective dépend du sous-réseau, de l'interface, de la propagation et des préférences de route. Il faut inspecter les routes réellement calculées pour l'interface concernée.

## 4.2. Comment raisonner sur la route choisie

Pour diagnostiquer un flux, procéder ainsi :

1. déterminer l'IP de destination réellement utilisée ;
2. récupérer les routes effectives de l'interface source ;
3. repérer les routes candidates qui correspondent à l'adresse de destination ;
4. comparer leur spécificité et les règles de sélection Azure documentées ;
5. examiner le next hop et vérifier qu'il peut transmettre le paquet ;
6. valider le chemin inverse depuis la destination ;
7. contrôler les règles de sécurité aux étapes traversées.

La règle du préfixe le plus spécifique est un principe central du routage IP, mais ne doit pas être utilisée seule pour deviner le comportement complet d'Azure. Les préférences entre routes de même préfixe dépendent des règles de sélection de la plateforme et de la source de route ; consulte les routes effectives et la documentation du service.

## 4.3. Exemple de table de routes d'un spoke

Le spoke `10.20.0.0/16` doit envoyer le trafic vers les autres réseaux privés et vers Internet au travers d'Azure Firewall situé à `10.0.10.4`.

| Préfixe de destination | Next hop | Adresse du next hop | Intention |
|---|---|---|---|
| `10.10.0.0/16` | Virtual appliance | `10.0.10.4` | Inspection vers le spoke Web |
| `10.30.0.0/16` | Virtual appliance | `10.0.10.4` | Inspection vers les données |
| `172.20.0.0/16` | Virtual appliance | `10.0.10.4` | Inspection vers le réseau local |
| `0.0.0.0/0` | Virtual appliance | `10.0.10.4` | Sortie contrôlée |

Cette table est illustrative. Le choix entre une route par préfixe et une route par défaut dépend des routes propagées, de la politique d'inspection et des exceptions prévues. Le sous-réseau de pare-feu lui-même ne doit pas recevoir aveuglément la même route par défaut vers lui-même.

## 4.4. Routage forcé et chemin de retour

Un schéma fréquent en hub-and-spoke consiste à envoyer les flux d'un spoke vers le pare-feu du hub au moyen d'UDR. Il faut aussi vérifier que le retour utilise un chemin cohérent.

```text
VM A (10.10.10.4)
       |
       | UDR : 10.20.0.0/16 -> Azure Firewall
       v
Azure Firewall (10.0.10.4)
       |
       | règle autorisant l'application
       v
VM B (10.20.10.5)
       |
       | retour : route compatible avec l'inspection
       v
Azure Firewall
       |
       v
VM A
```

Si la VM B retourne directement à VM A alors que l'aller traverse un équipement stateful, le flux peut être rejeté ou devenir difficile à tracer. La symétrie exacte dépend de l'architecture et du service. Toute modification de routes doit être validée dans les deux sens.

## 4.5. Routage vers Internet : ne pas confondre route et adresse publique

Une UDR `0.0.0.0/0` vers un pare-feu ne signifie pas qu'une VM possède une adresse publique. Inversement, une adresse IP publique associée à une VM ne suffit pas à garantir qu'une communication sera autorisée et opérationnelle.

Pour une sortie Internet contrôlée, vérifier :

- l'adresse de destination ;
- la route effective ;
- la route vers le pare-feu et la capacité de celui-ci à atteindre la destination ;
- les règles réseau/application et l'inspection TLS, si elle est configurée ;
- les règles NSG ;
- la résolution DNS ;
- le SNAT et l'éventuelle épuisement des ports source ;
- les exceptions imposées par des services de plateforme ou des dépendances d'application.

## 4.6. Propagation BGP et UDR

Une passerelle VPN/ExpressRoute peut annoncer des préfixes via BGP. Ces routes peuvent être propagées dans le réseau Azure si la propagation est activée sur la table de routage correspondante.

Une UDR peut être utilisée pour diriger un préfixe donné vers un équipement d'inspection. Il faut toutefois examiner les routes effectives pour confirmer le résultat et éviter d'écraser involontairement un chemin hybride voulu.

**Procédure opérationnelle :** documenter les préfixes attendus, les sources de routes et les chemins préférés ; comparer ensuite les annonces BGP, les routes apprises par la passerelle et les routes effectives des machines virtuelles.


# 5. Choisir entre hub-and-spoke et Azure Virtual WAN

## 5.1. Hub-and-spoke auto-géré

```text
                     +-------------------+
                     | Hub VNet          |
                     | Firewall / VPN / ER|
                     | DNS / Bastion      |
                     +----+----------+---+
                          |          |
                       Peering    Peering
                          |          |
                     +----+--+    +--+----+
                     |Spoke A|    |Spoke B|
                     +-------+    +-------+
```

Les équipes gèrent elles-mêmes les peerings, les tables de routes, les UDR, les routes propagées, les politiques du pare-feu et les changements inter-régions.

Avantages : contrôle explicite, adaptation fine et intégration possible à des designs existants.

Points d'attention : la complexité opérationnelle augmente avec le nombre de spokes, les régions et les réseaux hybrides. Il faut prévoir des conventions, des tests automatiques, un référentiel de préfixes et une gestion centralisée des changements.

## 5.2. Azure Virtual WAN et hubs virtuels sécurisés

Azure Virtual WAN est un service managé conçu pour relier des réseaux virtuels et des sites distants via des hubs virtuels. Il peut simplifier des topologies comportant de nombreux réseaux, des branches, du VPN, ExpressRoute et des besoins de routage multi-régions.

Le modèle comprend les connexions aux hubs, les tables de routes, les propagations/associations et, dans les architectures sécurisées, les politiques de routage visant à diriger le trafic vers une solution de sécurité.

Avec **routing intent**, un hub virtuel sécurisé peut appliquer des politiques déclaratives pour le trafic Internet et le trafic privé. Cette fonction demande le niveau de service approprié et une solution de sécurité prise en charge. Les modifications automatiques des tables de routage doivent être évaluées avant déploiement ; la suppression d'une politique ne garantit pas la restauration automatique de toutes les routes antérieures.

## 5.3. Tableau d'aide à la décision

| Critère | Hub-and-spoke auto-géré | Azure Virtual WAN |
|---|---|---|
| Maîtrise manuelle du routage | Très élevée | Encadrée par le modèle managé |
| Grand nombre de branches | Peut devenir complexe | Fonctionnalité majeure du service |
| UDR individualisées | Contrôle direct | Dépend de la conception et des capacités du hub |
| Dépendance à l'organisation existante | Bonne flexibilité | Nécessite une intégration au modèle Virtual WAN |
| Coût | Ressources et exploitation à calculer | Service, hubs, gateways, sécurité et transferts à calculer |
| Compétences nécessaires | Routes, peering, gateways, firewall, automation | Architecture Virtual WAN, tables, routing intent et sécurité |

Il n'existe pas de réponse universelle. Comparer un design concret, ses routes, son comportement de panne, ses coûts et sa charge d'exploitation.


# 6. Hub-and-spoke multi-région et inspection centralisée

## 6.1. Architecture à deux régions

```text
REGION A                                       REGION B
+-----------------------+                      +-----------------------+
| HUB A                 |                      | HUB B                 |
| Firewall A            |<---- transit ------->| Firewall B            |
| VPN/ER Gateway A      |                      | VPN/ER Gateway B      |
| DNS Resolver A        |                      | DNS Resolver B        |
+----+-------------+----+                      +----+-------------+----+
     |             |                                |             |
  Spoke Web A   Spoke Apps A                    Spoke Data B   Spoke DR B
```

Les hubs ne sont pas automatiquement interchangeables. La stratégie doit préciser si la région secondaire est active, passive ou partiellement active, quels préfixes sont annoncés, comment les routes basculent, quelle copie des données est disponible et qui décide de la reprise.

## 6.2. Routage inter-régions via pare-feu

Dans un hub-and-spoke classique, le peering ne fournit pas un transit universel et implicite entre tous les spokes. Le trafic inter-spokes ou inter-régions qui doit être inspecté exige une conception explicite : routes UDR, peerings, routage des hubs et règles de pare-feu.

Avant de déployer, écrire une matrice de routes attendues :

| Source | Destination | Chemin souhaité | Contrôle obligatoire |
|---|---|---|---|
| Spoke Web A | Spoke Apps A | Firewall régional A | Règle réseau/application |
| Spoke Apps A | Spoke Data B | Hubs A et B selon le design | Inspection et route retour |
| Spoke A | Réseau local | Gateway hybride via hub | BGP, UDR, firewall et DNS |
| Spoke B | Internet | Firewall régional local ou central | Egress filtering, SNAT, logs |

## 6.3. Risque de chemin asymétrique

Une mauvaise combinaison d'UDR, de routes BGP et de connexions inter-régions peut faire partir le trafic par le hub A et revenir par le hub B. Les pare-feu stateful, les NVA et certains flux VPN peuvent mal fonctionner avec ce type de chemin.

Avant un changement, tracer les deux sens du flux. Pour les services d'inspection stateful, il faut respecter les exigences de chemin du produit et le comportement de la topologie retenue.

## 6.4. Isolation des environnements

Une organisation peut séparer les environnements de production, de préproduction et de développement par abonnement et par VNet. L'isolation doit être soutenue par des politiques d'autorisation, des règles de routage et des contrôles de sécurité, pas seulement par des noms ou des tags.

Exemple :

```text
TENANT / LANDING ZONE
|
+-- Abonnement Connectivity
|   +-- Hubs, Firewall, DNS, Gateways
|
+-- Abonnement Production
|   +-- Spokes de production
|
+-- Abonnement NonProduction
|   +-- Spokes de développement/test
|
+-- Abonnement Management
    +-- Outils d'exploitation autorisés
```

La connectivité entre environnements doit être minimale, explicitement autorisée, enregistrée et testée.


# 7. Azure Firewall, NVA et chaîne d'inspection

## 7.1. Rôle d'Azure Firewall

Azure Firewall est un service de pare-feu managé qui filtre les flux selon des règles réseau, d'application et d'autres contrôles selon le SKU et la configuration. Il ne remplace pas les NSG : ces contrôles ont des fonctions et des points d'application différents.

Dans un hub-and-spoke, déployer Azure Firewall dans un sous-réseau dédié nommé exactement `AzureFirewallSubnet`. Pour les exigences de taille, de disponibilité, de routage, de SKU et de configuration, consulter la documentation actuelle du produit. La taille minimale documentée pour Azure Firewall est généralement `/26`; valider la documentation de la version et du scénario déployé avant de figer le plan.

## 7.2. Ordre de travail des flux

Exemple de sortie contrôlée :

```text
VM de Spoke
   |
   | UDR 0.0.0.0/0 -> IP privée du Firewall
   v
Azure Firewall
   |
   | politique autorisant le FQDN / protocole requis
   v
Destination Internet
```

Une route ne remplace pas la règle qui autorise le trafic. Une règle d'application fondée sur FQDN ne remplace pas non plus une résolution DNS fonctionnelle. Les politiques doivent être testées avec les noms, protocoles et ports effectivement utilisés par l'application.

## 7.3. Règles réseau et règles d'application

Les règles réseau s'appuient sur des paramètres comme les IP, protocoles et ports. Les règles d'application sont conçues pour contrôler le trafic applicatif, notamment HTTP/HTTPS sortant selon les capacités et les conditions du produit. La capacité réelle à filtrer un protocole ou un scénario dépend de la configuration et du SKU. Éviter de supposer qu'un FQDN est inspecté de manière identique pour tous les protocoles.

Bonnes pratiques :

- organiser les règles par application et par intention ;
- utiliser des groupes d'IP lorsque cela simplifie la maintenance ;
- limiter les règles générales ;
- documenter chaque exception ;
- activer les diagnostics nécessaires ;
- tester les effets des changements avec un scénario représentatif ;
- réviser périodiquement les règles inutilisées et les flux observés.

## 7.4. DNS proxy et filtrage par nom

Lorsque la politique dépend de noms DNS, il faut analyser la chaîne de résolution. Selon le design du firewall et du DNS, configurer un DNS proxy peut aider à aligner la résolution des clients et l'application des règles fondées sur les noms. Ce n'est pas un remplacement à la conception globale DNS.

Vérifier :

1. le résolveur utilisé par la VM ;
2. les règles de résolution et les suffixes DNS ;
3. les caches ;
4. le nom complet que l'application demande ;
5. la résolution depuis le réseau où se trouve le client ;
6. les logs du pare-feu et la décision de règle.

## 7.5. Azure Firewall ou NVA partenaire ?

Une Network Virtual Appliance (NVA) est un équipement logiciel déployé sur une infrastructure Azure pour des fonctions réseau ou de sécurité. Les capacités de routage, les mécanismes de haute disponibilité, la synchronisation d'état, la montée en charge et les licences dépendent du fournisseur.

Si une NVA est choisie :

- vérifier le support du routage et des next hops Azure ;
- documenter le comportement lorsque l'instance active tombe en panne ;
- s'assurer que les routes convergent correctement ;
- tester les flux de retour ;
- examiner les capacités, limitations et règles de licence du fournisseur ;
- prévoir la supervision et le support de niveau 3.

## 7.6. Inspection de flux est-ouest et nord-sud

- **Nord-sud** : flux entre Azure et l'extérieur, par exemple Internet ou le réseau local.
- **Est-ouest** : flux entre VNet, sous-réseaux ou workloads dans un même environnement cloud.

La politique doit préciser quels flux doivent passer par le pare-feu. Inspecter absolument tous les flux peut augmenter la complexité, la latence et les coûts. À l'inverse, autoriser des connexions directes sans justification augmente le risque de mouvement latéral.


# 8. Connectivité hybride de niveau production

## 8.1. VPN site-à-site

Un VPN site-à-site met en place un tunnel IPsec entre un réseau externe et Azure via une passerelle adaptée. La conception doit considérer les adresses des deux côtés, les paramètres de chiffrement, la compatibilité des équipements, le routage statique ou BGP, la redondance et la supervision.

```text
RÉSEAU LOCAL                                  AZURE
172.20.0.0/16                                 10.0.0.0/16
+------------------+      Tunnel IPsec       +--------------------+
| Routeur / Pare-feu|=========================| VPN Gateway        |
+------------------+                          +---------+----------+
                                                        |
                                                     Hub VNet
```

## 8.2. Redondance VPN

La disponibilité réelle dépend du nombre de tunnels, des dispositifs locaux, des paramètres BGP, des zones prises en charge par le SKU et du comportement de convergence. « Deux tunnels configurés » ne signifie pas automatiquement que tous les équipements et liens sont redondants.

Documenter les chemins nominaux, les bascules attendues, les délais tolérés, les routes annoncées et les tests de coupure exécutés.

## 8.3. ExpressRoute

ExpressRoute fournit une connectivité privée vers Microsoft via un fournisseur ou un emplacement de peering. Il faut distinguer le circuit, les connexions, les peerings, la passerelle VNet, les routes BGP et les composants côté fournisseur.

ExpressRoute n'est pas en soi une politique de filtrage. La sécurité, les routes autorisées, l'inspection et le comportement de retour doivent être conçus séparément.

## 8.4. VPN et ExpressRoute ensemble

Une entreprise peut utiliser les deux technologies pour des objectifs distincts : ExpressRoute comme chemin principal et VPN comme secours, ou des chemins séparés selon les applications. Ce choix nécessite un plan de préférence de routes validé par les mécanismes de routage disponibles.

Ne déduis pas une bascule fiable de la seule présence des deux connexions. Définir les annonces de préfixes, les préférences, les routes de secours, les tests de convergence et les alertes.

## 8.5. BGP : ce qu'il faut documenter

Le protocole BGP permet d'échanger des informations de routage entre systèmes. Dans Azure, il est notamment utilisé par des connexions hybrides et par des solutions réseau prises en charge.

Pour chaque voisin :

- adresse IP du voisin et ASN ;
- préfixes annoncés et reçus ;
- filtres de routes ;
- routes attendues par environnement ;
- politique de préférence des chemins ;
- comportement de retrait lors d'une panne ;
- mesures de supervision et alertes.

Une annonce BGP peut être présente sans être la route finalement retenue par une interface. Vérifier les routes effectives et les tables de routage du système lorsque cela est utile.


# 9. BGP, Azure Route Server et sélection des chemins

## 9.1. Rôle d'Azure Route Server

Azure Route Server permet l'échange dynamique de routes entre Azure et des appliances réseau virtuelles compatibles qui utilisent BGP. Il ne faut pas le confondre avec une passerelle VPN ou ExpressRoute : les rôles et les comportements sont différents.

Un Route Server peut simplifier l'échange de routes dans certaines topologies avec NVA. Il ne remplace pas les UDR, les règles du pare-feu ou les vérifications des routes effectives lorsque celles-ci restent nécessaires.

## 9.2. Quand l'utiliser ?

Évaluer Route Server si :

- plusieurs NVA doivent échanger dynamiquement les préfixes ;
- une topologie impose des mises à jour de routes liées à la disponibilité d'appliances ;
- les routes statiques deviennent difficiles à gérer ;
- le fournisseur de NVA prend en charge le modèle prévu.

Vérifier les exigences de sous-réseau, de BGP, d'ASNs, de nombre de pairs, les contraintes de routage et les capacités disponibles dans la région. Ne pas copier un exemple de production sans valider les limitations de la documentation actuelle.

## 9.3. Tableau de décision simplifié

| Besoin | Option à étudier | Contrôle obligatoire |
|---|---|---|
| Petites routes statiques stables | UDR | Revue des routes effectives |
| Routes hybrides apprises par la passerelle | BGP avec VPN/ExpressRoute | Filtrage des préfixes et convergence |
| NVA échangeant dynamiquement des routes | Azure Route Server, si compatible | Test de panne et de rétablissement |
| Grand réseau de branches et hubs multiples | Azure Virtual WAN | Vérifier le modèle de routage et le SKU |


# 10. DNS privé et résolution hybride à grande échelle

## 10.1. Le DNS est une dépendance réseau de premier ordre

Une application peut disposer d'une connectivité IP valide et pourtant échouer parce que le nom demandé est résolu vers une mauvaise adresse. Dans un environnement comportant des Private Endpoints, le nom public d'un service PaaS peut être résolu vers une adresse privée selon les zones DNS et la chaîne de résolution configurées.

Il faut tester le nom exact utilisé par le client depuis le réseau concerné, pas uniquement vérifier que la zone DNS existe.

## 10.2. Azure Private DNS Zones

Les zones DNS privées permettent de gérer des enregistrements DNS privés et de les rendre accessibles aux VNet liés selon le modèle de service. Un enregistrement correct dans une zone ne suffit pas si la zone n'est pas liée au bon VNet ou si le client interroge un autre résolveur.

## 10.3. Azure DNS Private Resolver

Azure DNS Private Resolver fournit une capacité de résolution DNS managée pour les scénarios hybrides. Les endpoints entrants servent à recevoir des requêtes DNS depuis des réseaux qui peuvent atteindre l'adresse de l'endpoint ; les endpoints sortants et les rulesets permettent de concevoir des transferts conditionnels vers d'autres résolveurs, selon le scénario.

Architecture conceptuelle :

```text
VM Azure ---- DNS privé / Resolver ---- règles de résolution
                                             |
                                             v
                                      DNS du réseau local

Client local ---- VPN / ExpressRoute ---- Inbound Endpoint DNS
```

Les flux UDP/TCP 53, les routes, les règles NSG, les résolveurs réellement utilisés et la redondance doivent être validés. Le DNS ne suit pas toujours intuitivement le chemin d'application : examiner la configuration du client et des serveurs DNS.

## 10.4. Conception DNS multi-région

Définir une convention pour les zones, les liens de VNet, les enregistrements privés, les règles conditionnelles et les serveurs autoritatifs. Déterminer si une région secondaire peut répondre en cas de panne de la région principale et comment les changements de données DNS se propagent.

## 10.5. Méthode de diagnostic DNS

Depuis un client représentatif :

1. relever les serveurs DNS configurés ;
2. interroger le FQDN utilisé par l'application ;
3. comparer la réponse attendue à l'adresse obtenue ;
4. vérifier la zone liée au VNet ou le ruleset concerné ;
5. inspecter les règles de transfert conditionnel ;
6. tester la résolution directe et inverse si elle est utilisée ;
7. recommencer depuis le réseau local et depuis Azure lorsque le scénario est hybride.


# 11. Private Link, PaaS privé et exfiltration contrôlée

## 11.1. Private Endpoint

Un Private Endpoint associe une interface réseau privée à un service pris en charge. Il permet d'atteindre ce service par une adresse IP privée depuis un réseau autorisé et correctement routé.

Cependant, le simple fait d'avoir une IP privée ne démontre pas que l'accès est limité au seul chemin souhaité. Les contrôles du service, les options d'accès public, le DNS, les routes et la politique d'organisation doivent être examinés ensemble.

## 11.2. DNS des Private Endpoints

Exemple conceptuel :

```text
Application -> storage.contoso.example
                    |
                    v
         Résolution privée configurée
                    |
                    v
          10.30.20.15 (Private Endpoint)
                    |
                    v
              Service PaaS
```

Le client conserve souvent le nom normal du service ; la chaîne DNS peut conduire vers une adresse privée lorsque les zones et l'intégration DNS sont correctement configurées. Le nom de zone exact dépend du service PaaS. Utiliser les zones DNS privées officielles associées au service, pas des noms devinés.

## 11.3. Private Link et Service Endpoints

| Critère | Private Endpoint / Private Link | Service Endpoint |
|---|---|---|
| Accès depuis une IP privée du VNet | Oui, via une interface privée | Le service est atteint par son endpoint de service, pas via une interface privée dans le sous-réseau |
| DNS | Souvent central dans la conception | Généralement différent du modèle Private Endpoint |
| Accès depuis réseaux connectés | Dépend du routage, DNS et contrôles associés | Dépend du modèle de service endpoint et des règles de réseau du service |
| Granularité d'exposition | Peut exposer un service/ressource précis | Contrôle basé sur le service et le sous-réseau selon le service |
| Complexité | DNS et routage Private Link à bien concevoir | Plus simple dans certains cas, avec limites différentes |

Le choix doit être fait selon le service, le niveau d'isolation, le modèle de connectivité et les exigences de gouvernance.

## 11.4. Prévenir l'exfiltration de données

Une stratégie robuste combine plusieurs contrôles :

- limiter l'accès public au service lorsque le scénario le permet ;
- appliquer une identité et une autorisation côté service ;
- contrôler les endpoints privés et l'accès DNS ;
- limiter la sortie Internet des workloads ;
- surveiller les connexions et les journaux de service ;
- utiliser les politiques de gouvernance pour contrôler la configuration ;
- tester les chemins d'accès autorisés et interdits.

Un Private Endpoint n'est pas, à lui seul, un mécanisme universel d'empêchement de l'exfiltration. Il faut gérer les accès au service, les autres chemins réseau et les identités.


# 12. Segmentation, gouvernance et défense en profondeur

## 12.1. NSG et ASG à l'échelle d'une plateforme

Les Network Security Groups filtrent les flux au niveau des sous-réseaux et des interfaces réseau, selon les associations et règles configurées. Les Application Security Groups permettent de référencer des ensembles d'interfaces dans certaines règles, ce qui facilite des politiques logiques comme `Web -> API` ou `API -> DB`.

Exemple de matrice :

| Source logique | Destination logique | Port | Décision |
|---|---|---:|---|
| Clients autorisés | Web | TCP/443 | Autoriser |
| Web | API | TCP/8443 | Autoriser |
| API | Base de données | TCP/1433 | Autoriser si nécessaire |
| Web | Base de données | Tous | Refuser par défaut si aucune exception n'est requise |
| Internet | VM d'administration | TCP/22, TCP/3389 | Ne pas exposer directement ; utiliser un chemin d'administration contrôlé |

Les ports et applications sont des exemples. Ils doivent correspondre aux services réellement déployés.

## 12.2. Azure Virtual Network Manager

Azure Virtual Network Manager peut aider à organiser la connectivité de groupes de VNet et à appliquer certaines configurations réseau à l'échelle d'une étendue. Ses fonctionnalités disponibles dépendent du service, de la région et du modèle choisi.

Les connected groups et les règles d'administration de sécurité peuvent répondre à des besoins particuliers, mais ne doivent pas être confondus avec les UDR ou les règles NSG. Tester l'ordre d'évaluation et les effets des règles centralisées avant la mise en production.

## 12.3. Séparation des responsabilités

Définir quelles équipes peuvent :

- créer ou modifier des VNet ;
- associer des peerings ;
- modifier les UDR ;
- changer les politiques Azure Firewall ;
- désactiver les logs ;
- modifier les règles d'accès public des services PaaS ;
- effectuer des tests de réseau en production.

Les politiques Azure Policy, les rôles RBAC, les déploiements IaC et les revues de code forment un ensemble cohérent. Aucun contrôle pris isolément ne suffit à garantir la sécurité.

## 12.4. Administration sécurisée

Privilégier des chemins d'administration contrôlés, des identités gérées, une authentification forte et l'absence d'IP publiques sur les machines qui n'en ont pas besoin. Azure Bastion est un choix possible pour l'accès RDP/SSH aux VM sans leur attribuer de public IP directement, sous réserve de sa configuration, du réseau et des coûts.


# 13. IPv6, chiffrement réseau et contraintes particulières

## 13.1. IPv6 dans Azure

Une architecture IPv6 nécessite un plan d'adressage et une analyse des capacités des services, des passerelles, des règles de sécurité, des appliances et des applications. Le dual-stack ne doit pas être activé sans examiner le comportement effectif des clients et des routes.

Si IPv6 est disponible pour le service et la région :

- documenter les préfixes et les sous-réseaux IPv6 ;
- vérifier les routes et les règles de sécurité IPv6 ;
- tester la résolution DNS A et AAAA ;
- confirmer qu'aucun chemin IPv6 non contrôlé ne contourne la politique IPv4 ;
- valider les connexions hybrides et la prise en charge applicative.

## 13.2. Chiffrement du trafic réseau

Le chiffrement applicatif, par exemple TLS, demeure essentiel même dans un réseau privé. Les options de chiffrement réseau Azure dépendent des types de ressources et des services concernés. Il faut vérifier la compatibilité, les limitations et les impacts sur les performances avant de concevoir un déploiement.

## 13.3. Dépendances des services de plateforme

Certaines ressources Azure exigent des sous-réseaux dédiés, des tailles minimales ou des règles particulières. La conception réseau doit intégrer ces dépendances dès la phase de dimensionnement pour éviter des migrations de sous-réseau difficiles.


# 14. Observabilité, diagnostics et exploitation

## 14.1. Les outils de Network Watcher

Network Watcher fournit des outils de diagnostic pour les réseaux Azure. Selon le scénario, on peut utiliser notamment les vérifications de connectivité, le dépannage de connexion, les routes effectives, les règles de sécurité effectives et la capture de paquets.

Les noms de fonctionnalités et les options disponibles évoluent. Les équipes doivent connaître les outils réellement disponibles pour le type de ressource et la région visés.

## 14.2. VNet flow logs et évolution des NSG flow logs

Les **VNet flow logs** sont l'option à privilégier pour de nouveaux déploiements de visibilité des flux. Les **NSG flow logs** ne permettent plus la création de nouvelles ressources depuis le 30 juin 2025 et leur retrait est annoncé pour le 30 septembre 2027. Un plan d'exploitation qui dépend encore exclusivement des NSG flow logs doit prévoir la migration vers VNet flow logs, puis vérifier la collecte et les tableaux d'analyse avant de désactiver l'ancien dispositif.

Flux de migration recommandé :

```text
Inventorier les NSG flow logs existants
               |
               v
Activer VNet flow logs sur le périmètre prévu
               |
               v
Valider stockage, Traffic Analytics et requêtes
               |
               v
Comparer couverture et volumes de données
               |
               v
Désactiver les anciens NSG flow logs après validation
```

Vérifier les coûts de stockage, les coûts d'analyse, la rétention et les règles de traitement des données.

## 14.3. Approche par couches

Quand une application ne répond plus, inspecter dans cet ordre :

1. résolution DNS ;
2. route effective à la source ;
3. sécurité réseau à la source ;
4. next hop et inspection centrale ;
5. route vers la destination ;
6. règles NSG et sécurité côté destination ;
7. service en écoute et pare-feu système d'exploitation ;
8. route de retour ;
9. logs applicatifs et authentification.

Ne pas commencer par modifier plusieurs règles au hasard. Reproduire le problème, isoler une couche, collecter une preuve, effectuer une seule modification contrôlée puis retester.

## 14.4. Network Watcher et journaux de pare-feu

Combiner les routes effectives, les outils de connectivité et les logs du pare-feu est souvent nécessaire pour comprendre un flux. L'absence d'un événement dans un seul journal ne prouve pas à elle seule que le trafic n'a pas circulé : vérifier la portée, la période, la configuration de diagnostic et les destinations de logs.

## 14.5. Requêtes et corrélation

Pour les enquêtes avancées, centraliser les diagnostics dans un espace de travail et standardiser les noms d'environnement, de VNet, de sous-réseau, de règle, de ressource et d'application. Les requêtes doivent permettre de corréler un incident réseau à un changement de configuration et à l'événement applicatif correspondant.


# 15. Performance, capacité, disponibilité et coûts

## 15.1. Distinguer les causes de latence

Une latence élevée ne prouve pas que le VNet est saturé. Les causes possibles comprennent :

- latence physique entre régions ;
- distance entre l'application et son backend ;
- inspection additionnelle par le pare-feu ;
- chemin inter-régions inattendu ;
- résolution DNS lente ;
- épuisement de ports SNAT ;
- retransmissions TCP ;
- saturation d'une appliance ;
- dépendance PaaS ou base de données.

Mesurer avant de modifier. Comparer les temps DNS, la connexion TCP, la négociation TLS et le temps de réponse applicatif.

## 15.2. Coûts à inclure

Une estimation de réseau doit inclure, selon l'architecture :

- Azure Firewall et ses options ;
- gateways VPN et ExpressRoute ;
- Azure Virtual WAN et hubs ;
- NAT Gateway ;
- transferts de données inter-régions et vers l'extérieur ;
- Private Endpoints et coûts associés ;
- stockage et analyse des logs ;
- Azure Bastion ;
- NVA et licences éditeur ;
- capacité de secours dans la région secondaire.

Les tarifs dépendent du SKU, de la région et du volume. Utiliser le calculateur Azure et les pages officielles en vigueur, pas des chiffres mémorisés dans un cours.

## 15.3. Disponibilité et objectifs de reprise

Documenter au minimum :

- RTO (durée cible de reprise) ;
- RPO (perte de données maximale visée) ;
- chemins réseau pendant une panne de région ;
- résolution DNS lorsque le service bascule ;
- disponibilité des identités et dépendances de plateforme ;
- capacité de l'environnement de secours ;
- procédure de retour à la région principale ;
- tests de reprise effectués et leurs résultats.

Le réseau peut être redondant alors que l'application reste indisponible parce que sa base de données, ses identités, ses secrets ou ses configurations ne sont pas répliqués.


# 16. Automatisation et Infrastructure as Code

## 16.1. Pourquoi automatiser ?

Les scripts réduisent les divergences entre régions et environnements, mais peuvent aussi reproduire une erreur à grande échelle. La qualité d'une automatisation se mesure à la prévisibilité, la répétabilité, la validation, la facilité de retour arrière et l'observabilité.

Toute modification réseau majeure devrait inclure :

1. revue de code ;
2. validation des préfixes ;
3. contrôle des dépendances ;
4. aperçu du changement lorsque l'outil le permet ;
5. déploiement dans un environnement de validation ;
6. tests de flux ;
7. approbation ;
8. surveillance après déploiement ;
9. procédure de retour arrière.

## 16.2. Azure CLI : consulter les ressources

```bash
# Choisir l'abonnement de travail
az account set --subscription "<SUBSCRIPTION_ID>"

# Afficher les VNet d'un groupe de ressources
az network vnet list \
  --resource-group "rg-network-prod" \
  --output table

# Afficher les sous-réseaux d'un VNet
az network vnet subnet list \
  --resource-group "rg-network-prod" \
  --vnet-name "vnet-hub-prod" \
  --output table

# Afficher les peerings d'un VNet
az network vnet peering list \
  --resource-group "rg-network-prod" \
  --vnet-name "vnet-hub-prod" \
  --output table

# Afficher les tables de routage
az network route-table list \
  --resource-group "rg-network-prod" \
  --output table
```

Ces commandes sont des exemples de consultation. Vérifier le contexte d'abonnement, les droits RBAC et les noms exacts avant de les exécuter.

## 16.3. Examiner une route effective

La disponibilité et la syntaxe exacte des commandes de routes effectives dépendent de l'interface réseau ciblée et de la version de l'extension Azure CLI. Un exemple courant est :

```bash
az network nic show-effective-route-table \
  --resource-group "rg-app-prod" \
  --name "nic-app-01" \
  --output table
```

Après exécution, examiner le préfixe, la source de la route, l'état et le next hop. Ne pas supposer qu'une route est effective parce qu'elle existe dans une table de routage non associée à la bonne interface.

## 16.4. Exemple de squelette Bicep

Le fragment suivant illustre la déclaration d'un VNet et d'un sous-réseau. Il n'est pas un module de production complet ; l'adresse, les tags, les paramètres de sécurité et les dépendances doivent être adaptés au design réel.

```bicep
param location string = resourceGroup().location
param vnetName string = 'vnet-app-prod'
param vnetPrefix string = '10.20.0.0/16'
param appSubnetPrefix string = '10.20.10.0/24'

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [vnetPrefix]
    }
    subnets: [
      {
        name: 'snet-app'
        properties: {
          addressPrefix: appSubnetPrefix
        }
      }
    ]
  }
}

output vnetResourceId string = vnet.id
```

En production, séparer les modules selon les responsabilités et prévoir des paramètres validés, des tags, des diagnostics, des politiques et des tests automatisés. Vérifier la version API encore prise en charge au moment du déploiement.

## 16.5. Contrôles automatisables

Un pipeline peut vérifier :

- absence de chevauchement CIDR dans un registre d'allocation ;
- respect des conventions de nommage et de tags ;
- absence de règles de sécurité trop larges ;
- présence de diagnostics obligatoires ;
- présence des routes attendues ;
- cohérence des links DNS privés ;
- absence d'adresses publiques non approuvées ;
- définition d'un propriétaire et d'une date de révision pour les exceptions.

Les contrôles automatisés doivent produire des erreurs compréhensibles et permettre de corriger avant que les modifications atteignent la production.


# 17. Méthodologie experte de dépannage

## 17.1. La méthode « une hypothèse, une preuve »

Pour un flux défaillant :

1. écrire le scénario exact ;
2. collecter les IP source et destination, le protocole et le port ;
3. confirmer le DNS ;
4. lire les routes effectives ;
5. examiner les NSG effectifs ;
6. vérifier les règles et les journaux du pare-feu ;
7. faire un test de connectivité depuis le bon point ;
8. vérifier le service cible ;
9. tester le retour ;
10. documenter la cause et la validation après correction.

## 17.2. Matrice de dépannage

| Symptôme | Hypothèses à examiner | Preuve à collecter |
|---|---|---|
| Nom non résolu | Résolveur, zone, lien de VNet, règle conditionnelle | Réponse DNS du client |
| IP joignable, port fermé | NSG, firewall, service non à l'écoute | Test TCP et logs de filtrage |
| Internet sortant impossible | UDR, firewall, SNAT, DNS | Route effective, logs Firewall, test DNS/TCP |
| Un seul sens fonctionne | Asymétrie, route retour, NVA stateful | Routes effectives aux deux extrémités |
| VPN établi mais aucun flux | Préfixes BGP/statique, route de retour, NSG | Routes apprises, routes effectives, logs VPN |
| Private Endpoint inaccessible | DNS, routes, règles réseau du service, NSG | Résolution FQDN, IP effective et logs service |
| Panne après changement | UDR/NSG/peering/règle modifiée | Historique de déploiement et comparaison de configuration |

## 17.3. Runbook pour une panne inter-spokes

```text
1. Identifier la source et la destination exactes.
2. Résoudre le nom depuis la VM source.
3. Vérifier l'UDR et la route effective source.
4. Vérifier que le next hop existe et accepte le flux.
5. Vérifier l'autorisation du firewall central.
6. Vérifier le peering et l'arrivée au VNet cible.
7. Vérifier le NSG de destination et le service applicatif.
8. Vérifier la route retour ; documenter le trajet inverse.
9. Corréler les logs réseau et applicatifs.
10. Corriger une seule cause, puis reproduire le test initial.
```

## 17.4. Prouver une correction

Une correction est validée si :

- le test initial échoue avant et réussit après, ou si le comportement attendu est démontré ;
- la règle autorise uniquement la portée voulue ;
- le chemin retour est valide ;
- les flux non autorisés restent bloqués ;
- les logs sont disponibles ;
- la configuration est enregistrée dans l'IaC ou le processus de changement ;
- aucune autre application n'a subi de régression évidente.


# 18. Ateliers guidés

## Atelier 1 — Revue des routes effectives dans une architecture hub-and-spoke

### Objectif

Démontrer qu'un flux inter-spokes traverse le pare-feu central comme prévu.

### Architecture

```text
Spoke A 10.10.0.0/16
  VM A 10.10.10.4
      |
      | UDR attendue : 10.20.0.0/16 -> 10.0.10.4
      v
Hub 10.0.0.0/16
  Azure Firewall 10.0.10.4
      |
      v
Spoke B 10.20.0.0/16
  VM B 10.20.10.5
```

### Étapes

1. relever le nom de l'interface réseau de VM A ;
2. afficher ses routes effectives ;
3. vérifier le préfixe de destination `10.20.0.0/16` ;
4. vérifier que le next hop est le firewall si c'est le design retenu ;
5. vérifier la règle firewall pour le port de test ;
6. confirmer le NSG de la destination ;
7. effectuer le test de connectivité ;
8. examiner le chemin retour depuis VM B ;
9. exporter les preuves dans un compte rendu.

### Critères de réussite

- route effective correcte dans les deux sens ;
- aucune règle globale inutile ;
- résultat reproductible ;
- capture des éléments de preuve ;
- procédure documentée.

## Atelier 2 — Diagnostic DNS d'un Private Endpoint

### Objectif

Identifier la différence entre une panne DNS et une panne réseau.

### Scénario

Une VM d'un spoke doit accéder à un compte de stockage via un Private Endpoint. Le nom du service renvoie une adresse qui n'appartient pas au réseau attendu.

### Étapes

1. interroger le nom depuis la VM ;
2. afficher le serveur DNS utilisé ;
3. vérifier la zone privée officielle associée au type de service ;
4. contrôler les liens de VNet et le mécanisme de résolution ;
5. vérifier l'enregistrement lié au Private Endpoint ;
6. tester la résolution depuis un deuxième réseau prévu ;
7. contrôler le routage et les règles d'accès au service ;
8. documenter la correction et ses effets.

### Critères de réussite

- le nom demandé par le client est connu ;
- le client obtient la réponse attendue ;
- la réponse privée correspond à l'endpoint voulu ;
- l'accès public indésirable n'est pas supposé désactivé sans vérification ;
- la résolution depuis un autre VNet est testée.

## Atelier 3 — Revue de résilience hybride

### Objectif

Construire un plan de test de bascule VPN/ExpressRoute sans perturber la production.

### Travaux

1. dessiner les connexions et les routes annoncées ;
2. noter les préfixes attendus ;
3. définir la priorité et le comportement des routes de secours ;
4. identifier les flux qui doivent traverser le firewall ;
5. définir la méthode de test de panne approuvée ;
6. mesurer le temps de convergence ;
7. valider DNS, accès applicatif et route retour après la bascule ;
8. définir les critères de retour à la normale.

Ne jamais couper une connexion de production sans procédure autorisée, fenêtre de maintenance et plan de retour arrière.

## Atelier 4 — Préparer une migration des logs réseau

### Objectif

Préparer la migration des NSG flow logs vers VNet flow logs.

### Étapes

1. inventaire des flux et de leurs consommateurs ;
2. définition de la destination de stockage et de la rétention ;
3. activation de VNet flow logs sur le périmètre approuvé ;
4. validation des données et du tableau Traffic Analytics, si utilisé ;
5. comparaison de la couverture et des volumes ;
6. mise à jour des requêtes, alertes et procédures ;
7. désactivation des anciens NSG flow logs après validation ;
8. contrôle des coûts et de la rétention.

Le remplacement doit préserver la capacité de l'équipe à enquêter sur les flux et les incidents. Il faut vérifier le résultat plutôt que supposer que les deux configurations sont équivalentes dans chaque environnement.


# 19. Exercices de compréhension avec corrigés

## Exercice 1 — CIDR

Un VNet utilise `10.50.0.0/16`. Une équipe souhaite créer deux sous-réseaux : `10.50.10.0/24` et `10.50.10.128/25`.

**Question :** est-ce un plan valide pour deux sous-réseaux distincts du même VNet ?

**Correction :** non, les blocs se chevauchent. `10.50.10.128/25` se situe à l'intérieur de `10.50.10.0/24`. Choisir un bloc disjoint, par exemple `10.50.11.0/24`, après vérification de l'inventaire global.

## Exercice 2 — Peering

Deux spokes sont peerés à un hub. Chaque spoke peut atteindre le hub. Peut-on en conclure que Spoke A atteindra directement Spoke B au travers du hub ?

**Correction :** non. Le peering VNet n'est pas transitif. La connectivité inter-spokes exige une conception explicite, comme des UDR vers un firewall/NVA, un peering direct ou une solution de connectivité appropriée.

## Exercice 3 — Route de retour

Une VM A envoie un flux vers VM B en passant par un pare-feu stateful. VM B répond directement à VM A sans repasser par ce pare-feu. Quel risque existe ?

**Correction :** le chemin est asymétrique. Le pare-feu peut ne pas voir la réponse attendue et rejeter le flux ou ne pas maintenir correctement l'état. Les routes des deux côtés doivent respecter la politique retenue.

## Exercice 4 — Private Endpoint

Le Private Endpoint a une IP privée, mais la VM reçoit une réponse DNS publique pour le nom du service. Que faut-il vérifier avant de toucher aux routes ?

**Correction :** le résolveur utilisé, les zones DNS privées requises pour le service, les liens de VNet, les enregistrements, les règles de résolution et le nom exact demandé par l'application. Un problème DNS peut envoyer le client vers un endpoint différent de celui prévu.

## Exercice 5 — Logs

Une équipe souhaite créer de nouveaux NSG flow logs pour un nouveau projet en octobre 2026. Quelle option recommander ?

**Correction :** préférer VNet flow logs. La création de nouveaux NSG flow logs n'est plus prise en charge depuis le 30 juin 2025 et leur retrait est prévu pour le 30 septembre 2027 selon la documentation Microsoft. Il faut planifier une migration pour les configurations existantes.

## Exercice 6 — VPN et ExpressRoute

Une organisation a un VPN et ExpressRoute. Peut-elle considérer que la bascule est automatique et correcte ?

**Correction :** non. Il faut concevoir et tester les routes, les annonces BGP, les préférences, les mécanismes de bascule, le chemin retour, les délais et les alertes. La présence de deux technologies ne garantit pas la continuité applicative.

## Exercice 7 — Route par défaut

Une UDR envoie `0.0.0.0/0` vers Azure Firewall. Pourquoi le trafic Internet d'une VM peut-il encore échouer ?

**Correction :** route incorrecte ou non associée, next hop indisponible, règles firewall manquantes, DNS défaillant, NSG, ports bloqués, SNAT, restrictions de destination ou service cible indisponible. Il faut examiner les routes effectives et les logs.

## Exercice 8 — Virtual WAN

Quelle différence générale existe entre un hub auto-géré et un hub virtuel Virtual WAN sécurisé ?

**Correction :** le premier est construit autour de VNet, peerings, UDR et ressources administrées par l'équipe. Virtual WAN offre un modèle de hubs managés et des possibilités de routage centralisé. Le choix dépend de l'échelle, des fonctionnalités, du coût, du contrôle requis et du modèle d'exploitation. Les fonctions doivent être vérifiées dans la documentation actuelle.


# 20. Challenge final — Réseau Azure d'entreprise multi-région

## 20.1. Contexte

Contoso déploie une nouvelle plateforme. L'application Web est hébergée dans `10.10.0.0/16`, les API dans `10.20.0.0/16` et les données dans `10.30.0.0/16`. Le hub de la région primaire utilise `10.0.0.0/16`. Le réseau local est `172.20.0.0/16`. Une région secondaire et un site distant doivent être préparés pour la reprise.

La solution doit permettre :

- aux utilisateurs d'accéder au service Web autorisé ;
- au Web d'appeler l'API sur un port applicatif approuvé ;
- à l'API d'accéder à la base de données sur le port requis ;
- aux spokes de joindre le réseau local par le chemin d'inspection prévu ;
- aux services PaaS approuvés d'être accessibles par Private Endpoint ;
- aux administrateurs d'utiliser un chemin sécurisé ;
- à l'équipe réseau de prouver quels flux ont été autorisés ou refusés ;
- à un incident de routage d'être diagnostiqué et documenté.

## 20.2. Schéma cible à compléter

```text
                           Utilisateurs
                                |
                          Entrée publique
                                |
                         +------+------+
                         |   HUB A     |
                         | Firewall    |
                         | VPN/ER GW   |
                         | DNS         |
                         +--+---+---+--+
                            |   |   |
               +------------+   |   +-------------+
               |                |                 |
          +----+-----+     +----+-----+      +----+-----+
          | Spoke WEB|     | Spoke API|      |Spoke DATA|
          |10.10/16  |     |10.20/16  |      |10.30/16  |
          +----------+     +----------+      +----------+
                                  |
                           Private Endpoint(s)
                                  |
                            Services PaaS

     LAN 172.20.0.0/16 ---- VPN/ExpressRoute ---- Hub A
                                             |
                                      Liaison région B
                                             |
                                           Hub B
                                             |
                                          Spoke DR
```

## 20.3. Travail demandé

### Partie A — Plan d'adressage (15 points)

1. identifier les plages qui ne doivent pas se chevaucher ;
2. proposer des sous-réseaux dédiés au firewall, aux gateways et aux workloads ;
3. expliquer comment réserver les plages futures ;
4. documenter les plages du réseau local et les réseaux partenaires.

### Partie B — Routage (20 points)

1. documenter le chemin Web vers API ;
2. documenter le chemin API vers Data ;
3. définir la sortie Internet ;
4. définir le chemin vers le réseau local ;
5. expliquer comment vérifier les routes effectives et éviter l'asymétrie.

### Partie C — Sécurité (15 points)

1. écrire une matrice minimale de flux autorisés ;
2. préciser le rôle des NSG et du firewall ;
3. limiter l'administration ;
4. expliquer pourquoi une règle `Any/Any` n'est pas acceptable.

### Partie D — DNS et PaaS privé (15 points)

1. définir les zones et liens DNS ;
2. montrer la résolution souhaitée d'un Private Endpoint ;
3. proposer des tests depuis deux VNet ;
4. expliquer le contrôle des accès publics du service.

### Partie E — Résilience et connectivité hybride (15 points)

1. proposer une stratégie VPN/ExpressRoute adaptée au besoin ;
2. documenter les préfixes et mécanismes BGP ;
3. expliquer le chemin de reprise de la région secondaire ;
4. préciser au moins trois tests de panne.

### Partie F — Observabilité et exploitation (10 points)

1. choisir les journaux utiles ;
2. définir les alertes ;
3. écrire la séquence de diagnostic d'un flux bloqué ;
4. définir un processus de changement.

### Partie G — Qualité et coûts (10 points)

1. identifier les coûts majeurs ;
2. prévoir l'usage d'IaC ;
3. fournir une checklist de mise en production ;
4. justifier les décisions qui ont le plus d'impact.

**Total : 100 points.**

## 20.4. Livrables attendus

- un schéma réseau lisible ;
- un tableau d'adressage ;
- une matrice de flux ;
- des tables de routes attendues ;
- la stratégie DNS ;
- une stratégie de connectivité hybride ;
- une matrice de tests, avec résultats attendus ;
- une checklist de sécurité et d'exploitation ;
- une justification des coûts et du choix d'architecture.


# 21. Correction détaillée du challenge

## 21.1. Architecture de référence possible

```text
                       INTERNET / CLIENTS
                               |
                  Front Door / App Gateway selon besoin
                               |
                        Hub régional A
                 +---------------------------+
                 | Azure Firewall             |
                 | VPN/ExpressRoute Gateway   |
                 | DNS Private Resolver       |
                 | Bastion selon besoin       |
                 +--+-----------+-----------+-+
                    |           |           |
                 Spoke WEB   Spoke API    Spoke DATA
                 10.10/16    10.20/16     10.30/16
                    |           |            |
                    +---- firewall / routes -+
                                |
                       Private Endpoints PaaS
                                |
                       Accès privé contrôlé

          LAN 172.20.0.0/16 -- VPN/ER -- Hub régional A
                                |
                        routage inter-région
                                |
                         Hub régional B
                                |
                           Spoke DR
```

C'est un modèle possible, et non la seule architecture valable. Une solution de production doit préciser les SKU, les zones, les routes, les endpoints DNS et les dépendances exactes.

## 21.2. Correction A — Plan d'adressage

Les plages d'exemple sont distinctes : hub A `10.0.0.0/16`, Web `10.10.0.0/16`, API `10.20.0.0/16`, Data `10.30.0.0/16`, LAN `172.20.0.0/16`. La région B doit recevoir une plage qui ne chevauche aucun réseau existant, par exemple `10.100.0.0/16` pour un hub, sous réserve du plan global.

Réserver dans le hub les sous-réseaux spéciaux requis par les services utilisés. Pour Azure Firewall, le nom `AzureFirewallSubnet` doit être exact et la taille doit satisfaire les exigences du service ; la documentation actuelle doit être consultée avant la mise en production. Éviter de dimensionner sans marge les sous-réseaux des workloads et Private Endpoints.

**Barème indicatif :** 15/15 si les plages sont disjointes, les besoins spéciaux et la croissance sont documentés.

## 21.3. Correction B — Routage

Les flux doivent être décrits des deux côtés.

| Source | Destination | Route attendue | Contrôle |
|---|---|---|---|
| Web | API | UDR vers Firewall, selon design d'inspection | NSG + Firewall |
| API | Data | UDR vers Firewall ou chemin explicite approuvé | NSG + Firewall |
| Spokes | LAN | Route vers le chemin hybride prévu | BGP/UDR + Firewall |
| Workloads | Internet | Sortie via Firewall | Règles d'egress et logs |
| Hub A | Hub B | Routes inter-régions cohérentes | Firewall et routes retour |

Le peering VNet n'est pas transitif. Ne pas considérer un hub comme un routeur universel sans configurer le chemin correspondant. Vérifier les routes effectives sur les interfaces sources, les préfixes BGP, les UDR, les routes du retour et les règles de l'équipement d'inspection.

**Barème indicatif :** 20/20 si les chemins aller et retour sont décrits et testables.

## 21.4. Correction C — Sécurité

Matrice de base possible :

| Source | Destination | Port | Décision |
|---|---|---:|---|
| Clients approuvés | Front Web | TCP/443 | Autoriser |
| Web | API | TCP/8443 | Autoriser |
| API | Base de données | TCP/1433 ou port réellement requis | Autoriser |
| Web | Data | Tous non requis | Refuser |
| Internet | VM interne | RDP/SSH direct | Refuser ; chemin d'administration contrôlé |

Appliquer les NSG pour une segmentation locale et le firewall central pour les flux devant être inspectés. Laisser la politique de service PaaS et les identités dans le modèle de protection ; un contrôle réseau n'est pas un substitut à l'autorisation applicative.

**Barème indicatif :** 15/15 si la matrice est minimale, justifiée et accompagnée de tests négatifs.

## 21.5. Correction D — DNS et PaaS privé

Le nom utilisé par l'application doit être résolu par la chaîne DNS appropriée vers l'adresse privée attendue. Les zones DNS privées doivent être celles documentées pour le service PaaS. Les VNet clients concernés doivent avoir accès à la zone selon le modèle de résolution retenu. Le DNS hybride doit acheminer les demandes de façon prévisible.

Tester depuis le spoke Web et depuis le spoke API :

1. interroger le FQDN du service ;
2. vérifier l'adresse IP retournée ;
3. tester la connectivité au port du service ;
4. consulter les journaux ;
5. vérifier les contrôles d'accès réseau et l'authentification du service ;
6. confirmer que l'accès public est désactivé ou restreint selon les exigences.

**Barème indicatif :** 15/15 si les zones, liens, résolveurs, routes et contrôles du service sont testés.

## 21.6. Correction E — Résilience hybride

Le choix entre VPN, ExpressRoute ou leur combinaison dépend des exigences de disponibilité, de débit, de délai et de coût. Il faut annoncer et filtrer les bons préfixes, documenter les voisins BGP et définir un plan de préférence des chemins. La région secondaire doit disposer des services indispensables ou de procédures de restauration testées.

Tests de panne recommandés dans un environnement autorisé :

- arrêt contrôlé d'un tunnel VPN ou retrait d'une route simulée ;
- perte du chemin principal puis observation de la convergence ;
- indisponibilité d'une ressource en région primaire et bascule de la charge ;
- vérification DNS après bascule ;
- validation du chemin retour et des logs.

Ne jamais effectuer un test destructif en production sans autorisation, fenêtre de maintenance et procédure de retour arrière.

**Barème indicatif :** 15/15 si la redondance est prouvée par des tests et non simplement annoncée.

## 21.7. Correction F — Observabilité

Collecter les diagnostics pertinents d'Azure Firewall, des connexions hybrides, des VNet flow logs, du DNS et des ressources applicatives. Définir la rétention, les droits d'accès, les alertes et la responsabilité opérationnelle.

Exemples d'alertes à envisager :

- échec ou dégradation d'une connexion VPN/ExpressRoute ;
- augmentation des flux refusés sur un service critique ;
- dérive d'une règle de sécurité ;
- échec des requêtes DNS privées ;
- dégradation d'un service applicatif ;
- absence de logs attendus.

**Barème indicatif :** 10/10 si chaque alerte est associée à une action documentée.

## 21.8. Correction G — Coûts et exploitation

Les coûts à budgéter comprennent le pare-feu, les gateways, Virtual WAN si utilisé, les transferts régionaux, Private Endpoints, le stockage et l'analyse des journaux, Bastion, les appliances partenaires et la région de reprise. Utiliser le calculateur officiel plutôt que des montants non datés.

Déployer le réseau par IaC, gérer les changements par revue de code et conserver un plan de tests. Les contrôles automatisés doivent rechercher les chevauchements CIDR, les règles trop permissives, les ressources publiques non prévues, l'absence de journaux et les routes inattendues.

**Barème indicatif :** 10/10 si les coûts sont identifiés et le déploiement peut être répété et audité.

## 21.9. Barème de réussite

| Score | Interprétation |
|---:|---|
| 90–100 | Architecture défendable, tests solides, risques et coûts explicités |
| 75–89 | Bonne architecture, quelques hypothèses ou contrôles à compléter |
| 60–74 | Fonctionnement plausible mais validation de certains chemins insuffisante |
| 40–59 | Lacunes importantes en routage, DNS ou sécurité |
| 0–39 | Architecture non démontrée ; revoir les fondamentaux du niveau intermédiaire |

Une solution ne doit pas obtenir un bon score uniquement parce qu'elle « fonctionne » dans un test simple. La résilience, les tests négatifs, la sécurité et les preuves d'exploitation font partie de la notation.


# 22. Checklist de revue d'architecture

## Adressage

- [ ] Les CIDR sont documentés et non chevauchants.
- [ ] Les plages de reprise et de partenaires sont réservées.
- [ ] Les tailles de sous-réseaux tiennent compte des besoins et des services Azure.
- [ ] Un propriétaire et une justification sont associés aux allocations.

## Routage

- [ ] Les routes effectives sont vérifiées aux points de décision importants.
- [ ] Les UDR sont associées aux bons sous-réseaux.
- [ ] Les flux inter-spokes ont un chemin explicitement conçu.
- [ ] Les routes aller et retour sont cohérentes.
- [ ] Les annonces BGP sont filtrées et surveillées.

## Sécurité

- [ ] Les règles NSG suivent le moindre privilège.
- [ ] Les règles Firewall sont justifiées, journalisées et révisées.
- [ ] Les machines qui n'en ont pas besoin ne possèdent pas d'IP publique.
- [ ] Les chemins d'administration sont contrôlés.
- [ ] Les accès publics aux services PaaS sont configurés selon la politique.

## DNS et PaaS

- [ ] Les zones DNS privées sont documentées et liées aux bons réseaux.
- [ ] La résolution hybride est testée depuis chaque contexte important.
- [ ] Les Private Endpoints ont des tests DNS et réseau associés.
- [ ] Les accès publics et privés ont été vérifiés indépendamment.

## Résilience et exploitation

- [ ] Les objectifs RTO/RPO sont documentés.
- [ ] Les bascules VPN/ExpressRoute et multi-régions ont été testées.
- [ ] Les diagnostics réseau sont activés et consultables.
- [ ] Les VNet flow logs sont envisagés pour la visibilité des flux.
- [ ] Les alertes ont un runbook et un propriétaire.
- [ ] Les coûts de sécurité, de transfert et de logs sont budgétés.
- [ ] L'IaC, la revue de code et le retour arrière sont documentés.


# 23. Glossaire

| Terme | Définition |
|---|---|
| VNet | Réseau virtuel Azure |
| Subnet | Sous-réseau d'un VNet |
| CIDR | Notation d'un préfixe réseau |
| UDR | User Defined Route, route définie par l'utilisateur |
| NSG | Network Security Group, filtrage de trafic réseau |
| ASG | Application Security Group, regroupement logique d'interfaces pour certaines règles NSG |
| VNet Peering | Connexion privée entre VNet via le backbone Azure, non transitive par défaut |
| Hub-and-spoke | Topologie autour d'un réseau central et de réseaux satellites |
| Azure Firewall | Service de pare-feu managé Azure |
| NVA | Network Virtual Appliance, appliance réseau logicielle |
| VPN Gateway | Passerelle Azure pour connexions VPN prises en charge |
| ExpressRoute | Connectivité privée vers le réseau Microsoft par un fournisseur/peering |
| BGP | Border Gateway Protocol, échange dynamique de routes |
| Route Server | Service Azure d'échange dynamique de routes avec des NVA compatibles |
| Private Link | Accès privé aux services pris en charge via une interface/connexion privée |
| Private Endpoint | Interface réseau privée associée à une ressource de service prise en charge |
| DNS Private Resolver | Service de résolution DNS managée pour des scénarios Azure et hybrides |
| VNet flow logs | Journalisation des flux réseau au niveau du VNet |
| RTO | Recovery Time Objective, objectif de durée de reprise |
| RPO | Recovery Point Objective, objectif de point de reprise/perte de données tolérée |
| IaC | Infrastructure as Code, infrastructure décrite par du code déclaratif |
| SNAT | Source Network Address Translation |
| East-west | Trafic entre réseaux/workloads internes |
| North-south | Trafic entre Azure et une destination externe |


# 24. Documentation officielle et références

Les liens ci-dessous pointent vers Microsoft Learn. Les fonctionnalités, SKU, limites, noms de paramètres et tarifs évoluent ; relire la documentation applicable au moment du déploiement.

## Architecture réseau

- Hub-and-spoke : https://learn.microsoft.com/en-us/azure/networking/design-guide/hub-spoke
- Hub-and-spoke avec Azure Virtual WAN : https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/hub-spoke-virtual-wan-architecture
- Conception Azure Virtual WAN : https://learn.microsoft.com/en-us/azure/networking/design-guide/virtual-wan
- Routage multi-hub et spoke avec Azure Firewall : https://learn.microsoft.com/en-us/azure/firewall/firewall-multi-hub-spoke

## Routage et sécurité

- Vue d'ensemble du routage VNet : https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview
- Vue d'ensemble d'Azure Firewall : https://learn.microsoft.com/en-us/azure/firewall/overview
- Azure Route Server : https://learn.microsoft.com/en-us/azure/route-server/overview
- Network Security Groups : https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview
- Azure Virtual Network Manager : https://learn.microsoft.com/en-us/azure/virtual-network-manager/overview

## Connectivité hybride

- Azure VPN Gateway : https://learn.microsoft.com/en-us/azure/vpn-gateway/
- Conception VPN Gateway : https://learn.microsoft.com/en-us/azure/vpn-gateway/design
- ExpressRoute : https://learn.microsoft.com/en-us/azure/expressroute/

## Private Link et DNS

- Private Endpoint : https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview
- DNS des Private Endpoints : https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns
- Azure Private DNS : https://learn.microsoft.com/en-us/azure/dns/private-dns-overview
- Azure DNS Private Resolver : https://learn.microsoft.com/en-us/azure/dns/dns-private-resolver-overview

## Observabilité et dépannage

- VNet flow logs : https://learn.microsoft.com/en-us/azure/network-watcher/vnet-flow-logs-overview
- Conception de la supervision réseau : https://learn.microsoft.com/en-us/azure/networking/design-guide/monitor
- Dépannage d'un NSG qui bloque le trafic : https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-network/virtual-network-troubleshoot-nsg-blocking-traffic
- Retrait des NSG flow logs et migration : https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-read-nsg-flow-logs

## Automatisation

- Azure CLI : https://learn.microsoft.com/en-us/cli/azure/
- Bicep : https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/


# Fin du cours — Azure VNet expert

À ce niveau, l'ingénieur doit pouvoir argumenter les choix de topologie, tracer les flux dans les deux sens, démontrer le comportement des routes, de la sécurité et du DNS, préparer les tests de panne, chiffrer les coûts de fonctionnement et prouver que les mécanismes d'observabilité sont utilisables pendant un incident. La réussite du challenge final dépend autant de la qualité des preuves et du plan d'exploitation que du schéma d'architecture.
