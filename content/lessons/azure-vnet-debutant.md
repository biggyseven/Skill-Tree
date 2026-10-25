# Azure Virtual Network (VNet) — Cours complet de niveau débutant

**Fichier :** `azure-vnet-debutant.md`  
**Domaine :** Cloud, réseaux et sécurité  
**Plateforme :** Microsoft Azure  
**Niveau :** Débutant  
**Durée indicative :** 8 à 12 heures, ateliers et challenge compris  
**Prérequis :** notions de base sur IPv4, TCP/IP et les ports réseau  
**Méthode pédagogique :** théorie progressive, schémas textuels, exemples, atelier guidé, exercices corrigés et challenge final intégré

> **Organisation du document :** le cours, les ateliers, les exercices, le corrigé et le challenge final sont tous réunis dans ce seul fichier Markdown. Aucun fichier annexe n'est nécessaire.


# Comment utiliser ce cours

Étudie les chapitres dans l'ordre. Reproduis les schémas sur papier, puis explique avec tes propres mots ce qui permet ou empêche chaque communication. Ne crée pas toutes les ressources Azure d'un coup : commence par le réseau, vérifie-le, puis ajoute les règles de sécurité et les machines virtuelles si ton budget et ton abonnement le permettent.

Les ressources cloud peuvent générer des coûts. Les ateliers marqués **OPTIONNEL — RESSOURCES FACTURABLES** peuvent créer des machines virtuelles, une passerelle NAT, Azure Bastion ou d'autres services facturés. Vérifie les tarifs de ta région et supprime les ressources quand tu as terminé.

## Objectifs pédagogiques

À la fin du cours, tu devras être capable de :

- expliquer le rôle d'un réseau virtuel Azure ;
- distinguer une région, un abonnement, un groupe de ressources, un VNet, un sous-réseau, une interface réseau et une machine virtuelle ;
- calculer une plage IPv4 CIDR et planifier plusieurs sous-réseaux sans chevauchement ;
- distinguer une adresse IP privée d'une adresse IP publique ;
- lire les routes système et comprendre le rôle d'une table de routage personnalisée ;
- créer et associer un Network Security Group (NSG) ;
- concevoir une architecture simple avec un frontal et un serveur applicatif privé ;
- expliquer les limites d'un peering de VNet ;
- comprendre le DNS Azure, NAT Gateway, Bastion et les Private Endpoints à un niveau introductif ;
- suivre une méthode de diagnostic lorsqu'une connexion échoue ;
- réaliser le challenge final et justifier tes décisions d'adressage, de routage et de sécurité.

## Parcours d'apprentissage

```text
1. Fondamentaux réseau et Azure
             |
             v
2. VNet, régions et groupes de ressources
             |
             v
3. IPv4, CIDR et sous-réseaux
             |
             v
4. Interfaces réseau et IP publiques/privées
             |
             v
5. Routage et tables de routage
             |
             v
6. NSG et filtrage des flux
             |
             v
7. Sortie Internet, NAT Gateway et accès administrateur
             |
             v
8. DNS, peering et Private Endpoint
             |
             v
9. Atelier guidé et validation
             |
             v
10. Exercices corrigés puis challenge final
```


# PARTIE I — COMPRENDRE LE RÉSEAU DANS AZURE

# 1. Pourquoi un réseau virtuel est-il nécessaire ?

## 1.1 Réseau classique et cloud

Dans une infrastructure traditionnelle, les ordinateurs et les serveurs communiquent à travers des commutateurs, des routeurs, des pare-feu et des liaisons physiques. L'administrateur configure notamment l'adressage IP, les routes et les règles de filtrage.

Dans le cloud, les équipements physiques sont gérés par le fournisseur. L'administrateur conçoit plutôt une architecture logique au moyen de ressources réseau configurables par le portail, une API, Azure CLI, PowerShell ou des outils Infrastructure as Code.

Azure propose notamment :

- des réseaux virtuels (Virtual Networks ou VNets) ;
- des sous-réseaux ;
- des interfaces réseau de machines virtuelles ;
- des adresses IP privées et publiques ;
- des Network Security Groups ;
- des tables de routage personnalisées ;
- des passerelles VPN et ExpressRoute ;
- des services de sortie Internet, d'inspection et de connectivité privée ;
- des outils d'observation et de dépannage.

Le fait qu'une machine virtuelle soit en état « Running » ne prouve pas qu'elle soit joignable. Une route manquante, un NSG restrictif, un service qui n'écoute pas sur le bon port ou une résolution DNS incorrecte peuvent interrompre la communication.

**Principe fondamental : le réseau, le filtrage, le service applicatif et le DNS sont quatre éléments différents qu'il faut diagnostiquer séparément.**

## 1.2 Exemple d'un réseau d'entreprise local

```text
                       INTERNET
                           |
                     [ Routeur WAN ]
                           |
                     [ Pare-feu LAN ]
                           |
                    [ Commutateur LAN ]
                       /         \
                      /           \
             [ Serveur Web ]   [ Serveur App ]
              192.168.1.10      192.168.1.20
```

Le routeur choisit un chemin réseau. Le pare-feu décide quels flux sont autorisés. Le serveur doit ensuite écouter sur le port attendu.

## 1.3 Exemple de réseau dans Azure

```text
                      INTERNET
                          |
                 [ Entrée publique éventuelle ]
                          |
              +-----------+-----------+
              |        Azure VNet     |
              |                       |
              |  +-----------------+  |
              |  | subnet-web      |  |
              |  | 10.20.1.0/24    |  |
              |  | [VM Web]        |  |
              |  +-----------------+  |
              |                       |
              |  +-----------------+  |
              |  | subnet-app      |  |
              |  | 10.20.2.0/24    |  |
              |  | [VM App privée] |  |
              |  +-----------------+  |
              +-----------------------+
```

Le VNet représente le réseau logique. Les sous-réseaux segmentent son espace d'adressage. Les NSG filtrent les flux. Les routes déterminent le prochain saut. Les adresses publiques et les services de sortie définissent des options de connectivité externe.

## 1.4 Les questions à poser lorsqu'une connexion échoue

Lorsqu'un client ne parvient pas à joindre un serveur, pose les questions suivantes dans cet ordre :

1. Le nom DNS se résout-il vers la bonne adresse ?
2. L'adresse IP de destination est-elle correcte ?
3. Existe-t-il un chemin de routage entre la source et la destination ?
4. Les NSG associés au sous-réseau et à l'interface autorisent-ils le flux ?
5. Un pare-feu système ou applicatif bloque-t-il la connexion ?
6. Le service écoute-t-il réellement sur l'adresse et le port attendus ?
7. Le trafic de retour peut-il revenir vers le client ?

Ne change pas plusieurs paramètres en même temps. Une modification à la fois facilite l'identification de la cause.


# 2. Les ressources Azure et leur hiérarchie

## 2.1 Région Azure

Une région Azure est une zone géographique dans laquelle Microsoft exploite des ressources cloud. Le choix de région influence la latence, la disponibilité des services, les exigences de résidence des données et les coûts.

Une ressource réseau comme un VNet est créée dans une région. Les ressources qui doivent être intégrées au même VNet doivent respecter les règles de région propres à chaque service.

## 2.2 Abonnement

L'abonnement constitue une limite importante de gestion, de facturation et de contrôle d'accès. Il contient des groupes de ressources et les ressources Azure associées.

Une entreprise peut utiliser plusieurs abonnements pour séparer la production, le développement, les équipes ou les environnements avec des contraintes différentes.

## 2.3 Groupe de ressources

Un groupe de ressources est un conteneur logique destiné à organiser des ressources Azure ayant un cycle de vie commun ou une responsabilité commune.

Exemple :

```text
Abonnement : sub-formation
|
+-- Groupe de ressources : rg-reseau-lab
|   |
|   +-- VNet : vnet-lab
|   +-- NSG : nsg-web
|   +-- Table de routage : rt-app (si nécessaire)
|   +-- Ressources de diagnostic
|
+-- Groupe de ressources : rg-calcul-lab
    |
    +-- VM Web (facultatif)
    +-- VM App (facultatif)
```

Les ressources réseau et les machines virtuelles peuvent être regroupées différemment selon les besoins d'exploitation. Le schéma ci-dessus est une organisation pédagogique, pas une obligation Azure.

## 2.4 VNet

Un VNet est un réseau privé logique dans Azure. On lui associe un ou plusieurs espaces d'adresses IP. Les sous-réseaux découpent ces plages en segments plus petits.

## 2.5 Sous-réseau

Un sous-réseau est une plage d'adresses IP appartenant à l'espace d'adressage du VNet. Il accueille les interfaces réseau et les ressources compatibles avec ce sous-réseau.

Un sous-réseau peut être associé à un NSG et à une table de routage. Certains services Azure exigent un sous-réseau dédié ou imposent une taille minimale spécifique.

## 2.6 Interface réseau (NIC)

Une interface réseau, ou Network Interface, relie une machine virtuelle à un réseau virtuel. Elle dispose d'une configuration IP privée et peut, selon la conception, être associée à une adresse IP publique.

Le trafic vers une VM passe par son interface réseau et les règles applicables au sous-réseau et à la NIC.

## 2.7 Schéma récapitulatif de la hiérarchie

```text
TENANT MICROSOFT ENTRA ID
        |
        +-- Abonnement Azure
                |
                +-- Groupe de ressources
                        |
                        +-- VNet : 10.20.0.0/16
                        |       |
                        |       +-- Sous-réseau Web
                        |       |       |
                        |       |       +-- NIC de VM Web
                        |       |
                        |       +-- Sous-réseau App
                        |               |
                        |               +-- NIC de VM App
                        |
                        +-- NSG / tables de routes / diagnostics
```

**À retenir :** le VNet n'est pas la machine virtuelle, le sous-réseau n'est pas un pare-feu et le groupe de ressources n'est pas un réseau.


# 3. Comprendre les réseaux virtuels Azure

## 3.1 Espace d'adressage d'un VNet

À la création d'un VNet, on définit un ou plusieurs blocs d'adresses. Pour un laboratoire IPv4 simple, nous utiliserons :

```text
Nom du VNet : vnet-formation
Espace IPv4 : 10.20.0.0/16
```

Ce bloc contient 65 536 adresses IPv4 au total. Il est assez large pour diviser l'espace en sous-réseaux plus petits dans le cadre d'exemples pédagogiques.

## 3.2 Les plages privées IPv4

Les trois blocs IPv4 privés définis par les usages classiques sont :

| Bloc privé | Plage |
|---|---|
| `10.0.0.0/8` | 10.0.0.0 à 10.255.255.255 |
| `172.16.0.0/12` | 172.16.0.0 à 172.31.255.255 |
| `192.168.0.0/16` | 192.168.0.0 à 192.168.255.255 |

Ces adresses sont destinées à l'adressage privé. Elles ne sont pas routées comme des adresses publiques directement sur Internet.

Les exemples de ce cours utilisent `10.20.0.0/16`, mais un plan d'adressage doit être choisi selon les réseaux existants de l'organisation.

## 3.3 Éviter les chevauchements de réseaux

Supposons que le réseau local utilise `10.20.0.0/16`, et qu'on crée un VNet Azure avec le même espace d'adressage. Une connexion entre les deux réseaux serait difficile à router, car la même plage désignerait des destinations des deux côtés.

Avant de créer les VNets, recense :

- les réseaux locaux ;
- les autres VNets Azure ;
- les plages réservées à des services conteneurisés ou à des environnements de test ;
- les réseaux de partenaires et de filiales qui pourraient être reliés plus tard.

Un espace d'adressage non chevauchant facilite le peering et la connectivité hybride.

## 3.4 Plusieurs blocs dans un même VNet

Un VNet peut utiliser plusieurs espaces d'adressage lorsque la conception le justifie. Les plages doivent rester cohérentes avec les sous-réseaux et les autres réseaux connectés.

N'ajoute pas des blocs « au hasard ». Documente leur rôle et vérifie les chevauchements avant de les associer.


# 4. Calcul IPv4 et notation CIDR

## 4.1 Qu'est-ce qu'une adresse IPv4 ?

Une adresse IPv4 est constituée de 32 bits, généralement écrits sous la forme de quatre octets décimaux.

Exemple :

```text
10.20.1.25
```

Chaque octet est compris entre 0 et 255.

## 4.2 Que signifie `/16` ou `/24` ?

Le nombre après la barre indique combien de bits forment le préfixe réseau.

```text
Adresse IPv4 : 10.20.1.25/24
Bits IPv4    : 32
Bits réseau  : 24
Bits hôtes   : 8
```

Le nombre théorique d'adresses d'un bloc IPv4 de préfixe `p` est :

`N = 2^(32 - p)`

Exemple pour `/24` :

`2^(32 - 24) = 2^8 = 256 adresses`

Exemple pour `/16` :

`2^(32 - 16) = 2^16 = 65 536 adresses`

## 4.3 Tableau de référence CIDR

| Préfixe | Masque | Nombre total d'adresses |
|---|---|---:|
| `/16` | `255.255.0.0` | 65 536 |
| `/20` | `255.255.240.0` | 4 096 |
| `/21` | `255.255.248.0` | 2 048 |
| `/22` | `255.255.252.0` | 1 024 |
| `/23` | `255.255.254.0` | 512 |
| `/24` | `255.255.255.0` | 256 |
| `/25` | `255.255.255.128` | 128 |
| `/26` | `255.255.255.192` | 64 |
| `/27` | `255.255.255.224` | 32 |
| `/28` | `255.255.255.240` | 16 |
| `/29` | `255.255.255.248` | 8 |

Ces nombres sont les quantités totales du bloc. Azure réserve cinq adresses IPv4 par sous-réseau IPv4. Il faut donc distinguer le nombre total d'adresses du nombre exploitable par les ressources. Certains services Azure requièrent des sous-réseaux plus grands que le minimum technique.

## 4.4 Exemple : sous-réseau `/24`

Pour `10.20.1.0/24`, la plage va de `10.20.1.0` à `10.20.1.255`, soit 256 adresses.

Dans Azure, cinq adresses sont réservées dans chaque sous-réseau IPv4 :

- la première adresse de la plage ;
- les trois adresses suivantes ;
- la dernière adresse de la plage.

Pour `10.20.1.0/24`, ces adresses sont `10.20.1.0`, `10.20.1.1`, `10.20.1.2`, `10.20.1.3` et `10.20.1.255`.

Le nombre restant pour les ressources est donc `256 - 5 = 251` adresses, sous réserve des autres contraintes de service et d'allocation.

## 4.5 Exemple : sous-réseau `/26`

Un `/26` contient :

`2^(32 - 26) = 64 adresses`

Azure en réserve cinq. Il reste donc 59 adresses théoriquement utilisables pour les ressources ordinaires, sans tenir compte des besoins particuliers de services qui peuvent imposer des conditions supplémentaires.

## 4.6 Concevoir des sous-réseaux non chevauchants

Pour le VNet `10.20.0.0/16`, on peut utiliser :

```text
VNet : 10.20.0.0/16
|
+-- subnet-web   : 10.20.1.0/24
+-- subnet-app   : 10.20.2.0/24
+-- subnet-data  : 10.20.3.0/24
+-- subnet-admin : 10.20.4.0/24
```

Ces plages sont toutes incluses dans le VNet et ne se chevauchent pas.

Exemple à éviter :

```text
subnet-a : 10.20.1.0/24
subnet-b : 10.20.1.128/25
```

`10.20.1.128/25` est inclus dans `10.20.1.0/24`. Deux sous-réseaux d'un même VNet ne peuvent pas se chevaucher ainsi.

## 4.7 Méthode pratique pour calculer un plan d'adressage

1. Identifie la taille totale nécessaire à moyen terme.
2. Compare les réseaux locaux et les autres VNets pour éviter les chevauchements.
3. Choisis un espace VNet suffisamment large, sans excès injustifié.
4. Réserve des plages séparées pour les rôles et les environnements.
5. Vérifie les exigences spécifiques des services Azure.
6. Documente chaque sous-réseau, son propriétaire, son objectif et sa taille.
7. Garde une réserve d'adresses pour la croissance future.

### Exemple de registre d'adressage

| Sous-réseau | CIDR | Rôle | Exposition prévue |
|---|---|---|---|
| `snet-web` | `10.20.1.0/24` | Frontend Web | Entrées HTTP/HTTPS contrôlées |
| `snet-app` | `10.20.2.0/24` | Traitement applicatif | Privée, accessible depuis le Web autorisé |
| `snet-data` | `10.20.3.0/24` | Bases de données | Privée, accès applicatif uniquement |
| `snet-admin` | `10.20.4.0/24` | Services d'administration | Accès restreint |

Les libellés ne donnent aucune protection automatique : c'est la configuration des routes, des NSG, des services et des accès qui détermine les flux autorisés.


# PARTIE II — SOUS-RÉSEAUX, ADRESSES ET CONNECTIVITÉ

# 5. Les sous-réseaux Azure

## 5.1 Pourquoi découper un VNet ?

Les sous-réseaux organisent le réseau par fonction, environnement ou niveau de confiance. Ils permettent notamment d'associer des règles NSG et des routes à un ensemble de ressources.

Exemple :

```text
VNet : 10.20.0.0/16
|
+-- subnet-web  : ressources qui reçoivent des requêtes Web
|
+-- subnet-app  : ressources qui exécutent la logique applicative
|
+-- subnet-data : ressources de données privées
```

Une architecture segmentée facilite l'application du principe du moindre privilège : chaque catégorie de ressources ne reçoit que les communications nécessaires.

## 5.2 Choisir la bonne taille

Une plage `/24` apporte 256 adresses totales, dont cinq réservées par Azure. Elle est souvent confortable pour un petit exemple, mais elle n'est pas toujours nécessaire.

Ne choisis pas une taille uniquement en fonction du nombre de machines actuelles. Prends aussi en compte :

- les futures instances ;
- les interfaces réseau supplémentaires ;
- les mises à l'échelle ;
- les services managés exigeant un sous-réseau dédié ;
- les déploiements de haute disponibilité ;
- les éventuelles contraintes de délégation de sous-réseau.

Un sous-réseau peut être difficile à agrandir ensuite si la plage adjacente est déjà utilisée. Le plan initial est donc important.

## 5.3 Sous-réseaux dédiés à certains services

Certains services Azure demandent un nom et une taille spécifiques de sous-réseau. Exemples :

- Azure Bastion utilise `AzureBastionSubnet` pour les déploiements dédiés qui le nécessitent ;
- une passerelle VPN utilise `GatewaySubnet` ;
- Azure Firewall nécessite un sous-réseau dédié selon ses prérequis ;
- d'autres services peuvent demander une délégation de sous-réseau ou une plage minimale.

Ne déduis pas les exigences d'un service à partir d'un exemple générique. Vérifie la documentation officielle avant le déploiement. Pour une architecture réelle, réserve les sous-réseaux dédiés nécessaires dès le plan d'adressage.

## 5.4 Sous-réseau public ou privé : attention au vocabulaire Azure

Le fait de nommer un sous-réseau `public` ou `private` ne change pas automatiquement son comportement. Dans Azure, on décrit souvent ainsi l'intention d'architecture :

- un sous-réseau « exposé » accueille les composants qui doivent recevoir un trafic entrant public via un mécanisme explicitement configuré ;
- un sous-réseau « privé » accueille des ressources sans exposition entrante directe et utilise une solution contrôlée pour les accès nécessaires.

Il faut vérifier l'adresse IP publique, le service frontal, les règles NSG, les routes et les services de sortie. Le nom du sous-réseau ne constitue pas un contrôle de sécurité.

Depuis le 31 mars 2026, les nouveaux réseaux virtuels Azure ne disposent plus par défaut de l'accès sortant par défaut précédemment rencontré dans de nombreuses configurations. Pour les ressources qui doivent accéder à Internet ou à des points de terminaison publics, prévois une solution explicite de sortie et vérifie la configuration de ton environnement. Azure NAT Gateway est une option courante ; Azure Firewall ou une appliance réseau peuvent convenir à des besoins d'inspection plus avancés.

## 5.5 Schéma de segmentation recommandé pour le laboratoire

```text
VNet vnet-formation : 10.20.0.0/16
|
+-- snet-web : 10.20.1.0/24
|      +-- VM Web de démonstration (facultative)
|      +-- NSG Web
|
+-- snet-app : 10.20.2.0/24
|      +-- VM App de démonstration (facultative)
|      +-- NSG App
|
+-- snet-data : 10.20.3.0/24 (réservé pour les extensions)
|
+-- AzureBastionSubnet : à créer uniquement si Bastion dédié est déployé
```

Le dernier sous-réseau ne doit pas être créé simplement pour suivre le schéma si Bastion n'est pas utilisé. Si tu choisis de déployer Bastion dédié, vérifie ses exigences de taille et de configuration dans la documentation courante.


# 6. Adresses IP privées et publiques

## 6.1 Adresse IP privée

Une IP privée permet la communication au sein du réseau privé et avec les réseaux connectés via des routes et des autorisations appropriées.

Exemples de plages privées :

```text
10.20.1.10
10.20.2.15
172.16.10.5
192.168.10.20
```

Une adresse IP privée n'est pas directement joignable depuis Internet par sa seule présence.

## 6.2 Adresse IP publique

Une IP publique permet à un service Azure compatible de présenter un point d'accès public. Cela ne signifie pas que tous les ports deviennent automatiquement accessibles : des contrôles réseau et le service applicatif restent déterminants.

Dans une architecture sécurisée, évite d'attribuer une IP publique directement à chaque VM uniquement pour simplifier l'administration.

## 6.3 Architecture à éviter

```text
INTERNET
   |
   +------ SSH 22 / RDP 3389 ------> [ VM Web avec IP publique ]
   |
   +------ SSH 22 / RDP 3389 ------> [ VM App avec IP publique ]
   |
   +------ Port base de données ---> [ VM Data avec IP publique ]
```

Cette architecture expose des points d'administration et des services de données qui n'ont généralement pas besoin d'être accessibles publiquement.

## 6.4 Architecture plus sûre

```text
                   INTERNET
                      |
               [ Accès Web autorisé ]
                      |
                 [ VM Web / Front ]
                      |
             Flux applicatif autorisé
                      |
                [ VM App privée ]
                      |
          Flux base de données autorisé
                      |
                [ VM Data privée ]

Administration : opérateur -> Azure Bastion / VPN -> VM privée
```

Le composant Web peut être un service frontal public adapté, ou une VM exposée avec un contrôle strict selon l'objectif pédagogique. Les serveurs applicatifs et de données restent privés dans l'exemple.

## 6.5 IP privée dynamique ou statique

Dans Azure, une configuration IP privée peut être dynamique ou statique. Le choix dépend de la ressource et du besoin opérationnel.

- **Dynamique :** Azure alloue une adresse à partir du sous-réseau selon la méthode d'allocation configurée.
- **Statique :** l'adresse est définie explicitement dans Azure et doit appartenir à la plage du sous-réseau sans utiliser une adresse réservée.

Ne configure pas manuellement dans le système d'exploitation invité une adresse qui contredit la configuration de l'interface réseau Azure. La configuration réseau doit rester cohérente avec la plateforme.

## 6.6 IP publique et accès entrant

Une IP publique n'est qu'un élément de l'accès. Pour recevoir une connexion, il faut notamment :

1. un point d'entrée public approprié ;
2. une route et une configuration de service cohérentes ;
3. des règles NSG compatibles ;
4. un pare-feu dans la VM qui autorise le trafic ;
5. un programme qui écoute sur le port attendu ;
6. une réponse de retour possible.

Un client qui ne peut pas joindre une VM ne prouve donc pas à lui seul qu'il manque une IP publique.


# 7. Routage dans Azure

## 7.1 À quoi sert le routage ?

Le routage détermine le chemin utilisé pour atteindre une adresse IP de destination. Dans Azure, chaque sous-réseau dispose de routes système générées par la plateforme. On peut ajouter une table de routage personnalisée, appelée User Defined Route (UDR), afin de modifier certains chemins.

**Le routage répond à la question : « Où envoyer le paquet ? »**  
**Le NSG répond à la question : « Ce flux est-il autorisé ? »**

Ces deux mécanismes sont complémentaires.

## 7.2 Routes système

Azure fournit des routes système pour les communications internes au VNet, certaines plages réservées, les destinations Internet et d'autres destinations selon les services connectés.

Exemple conceptuel :

```text
Destination                    Prochain saut
10.20.0.0/16                   Virtual network
0.0.0.0/0                      Internet (route système usuelle)
Plages vers réseaux connectés   Selon les connexions et routes apprises
```

Ce tableau est simplifié et ne doit pas être utilisé comme une sortie exacte d'une table de routes de production. La liste effective dépend de la configuration de chaque sous-réseau.

L'existence d'une route système `0.0.0.0/0` vers Internet ne signifie pas qu'une VM d'un nouveau VNet dispose automatiquement d'une connectivité sortante par défaut. Le mécanisme d'accès sortant doit être explicitement conçu dans les nouvelles configurations concernées depuis le 31 mars 2026.

## 7.3 Route personnalisée (UDR)

Une table de routage personnalisée permet d'ajouter des routes qui orientent le trafic vers un prochain saut choisi, par exemple :

- Virtual appliance, par exemple un pare-feu ou une appliance réseau ;
- Virtual network gateway, selon les capacités de la passerelle ;
- Virtual network ;
- Internet ;
- None, pour supprimer le transit vers une destination ;
- certains autres types selon le contexte Azure.

Exemple conceptuel :

```text
Table : rt-app
Associée à : snet-app

Destination     Prochain saut
10.20.0.0/16    Virtual network (route système)
0.0.0.0/0       Virtual appliance : 10.20.0.4
```

Ce modèle forcerait le trafic Internet de ce sous-réseau à passer par une appliance `10.20.0.4`, si cette architecture et cette appliance sont correctement configurées. Il ne faut pas copier cette route dans un réseau réel sans prévoir l'appliance, le transfert IP et les règles nécessaires.

## 7.4 Principe du préfixe le plus spécifique

En général, lorsqu'un paquet correspond à plusieurs routes, Azure choisit le préfixe le plus spécifique. Lorsqu'il existe plusieurs routes ayant exactement le même préfixe, la source de la route intervient dans la sélection ; les routes définies par l'utilisateur ont priorité sur certaines routes apprises ou système selon les règles Azure applicables.

Exemple simplifié :

```text
Route A : 10.20.0.0/16 -> Virtual network
Route B : 10.20.2.0/24 -> Virtual appliance

Destination : 10.20.2.15
Choix attendu : Route B, car /24 est plus spécifique que /16.
```

La priorité d'une règle NSG et la sélection d'une route sont deux mécanismes distincts. Ne les confonds pas.

## 7.5 Exemple de chemin entre deux sous-réseaux du même VNet

```text
VM Web : 10.20.1.10
         |
         | Destination : 10.20.2.10
         v
Route système vers le VNet
         |
         v
VM App : 10.20.2.10
```

Le VNet fournit la connectivité interne, mais les règles de sécurité peuvent toujours bloquer le flux.

## 7.6 Comment consulter les routes d'une interface

Dans le portail Azure :

1. Ouvre la machine virtuelle.
2. Accède à Réseau et ouvre son interface réseau.
3. Consulte les routes effectives si l'option est disponible dans le contexte de diagnostic.
4. Compare la destination, le prochain saut, la source de route et l'état de la configuration.

Les libellés exacts du portail peuvent évoluer. Pour les diagnostics réseau avancés, utilise aussi les outils Network Watcher compatibles avec la région et la ressource.

## 7.7 Erreurs classiques de routage

- Créer une UDR sans vérifier les routes système existantes.
- Envoyer `0.0.0.0/0` vers une appliance qui ne transfère pas le trafic.
- Oublier d'activer le transfert IP sur l'interface d'une VM qui joue réellement le rôle d'appliance réseau.
- Ajouter un itinéraire de retour manquant dans une architecture hybride.
- Supposer qu'un peering rend tous les VNets connectés transitivement.
- Confondre une route disponible avec une autorisation donnée par un NSG.


# PARTIE III — SÉCURISER LES FLUX

# 8. Network Security Groups (NSG)

## 8.1 Définition

Un Network Security Group est un ensemble de règles qui autorisent ou refusent le trafic réseau entrant et sortant pour les ressources associées à un sous-réseau ou à une interface réseau.

Les règles portent notamment sur :

- la direction du trafic ;
- l'action Allow ou Deny ;
- le protocole ;
- les ports source et destination ;
- la source et la destination, exprimées par des adresses, des plages ou certains tags de service ;
- la priorité de la règle.

## 8.2 Les deux directions

**Inbound (entrant)** : trafic destiné à la ressource protégée.  
**Outbound (sortant)** : trafic qui quitte la ressource protégée.

Exemple pour un serveur Web :

```text
Client Internet
     |
     | TCP destination 443
     v
[ NSG entrant : autoriser HTTPS selon la politique ]
     |
     v
[ VM Web : service HTTPS en écoute ]
     |
     v
[ NSG sortant : autoriser les réponses et les flux requis ]
```

Les NSG sont stateful : les réponses d'un flux autorisé sont prises en compte par le suivi d'état. Il reste nécessaire de configurer les flux initiés indépendamment dans chaque direction selon les besoins.

## 8.3 NSG de sous-réseau et NSG de NIC

Un NSG peut être associé à un sous-réseau et/ou à une interface réseau.

Quand les deux sont configurés, les règles doivent permettre le flux aux deux niveaux. Une règle Allow dans le NSG de sous-réseau n'annule pas un Deny applicable dans le NSG de la NIC, et inversement.

Ordre d'évaluation important :

- pour le trafic entrant : NSG du sous-réseau, puis NSG de la NIC ;
- pour le trafic sortant : NSG de la NIC, puis NSG du sous-réseau.

À chaque niveau, une seule règle correspondante décide du résultat dans son NSG : les règles sont examinées par ordre de priorité, la plus petite valeur numérique étant la priorité la plus élevée.

## 8.4 Priorité des règles

Les règles personnalisées utilisent généralement des priorités de 100 à 4096. Une priorité plus petite est examinée avant une priorité plus grande.

Exemple :

| Priorité | Nom | Action | Port destination | Source |
|---:|---|---|---|---|
| 200 | `Allow-HTTPS` | Allow | TCP 443 | `Internet` |
| 210 | `Allow-HTTP` | Allow | TCP 80 | `Internet` |
| 300 | `Deny-RDP-Internet` | Deny | TCP 3389 | `Internet` |

Une règle trop large placée avec une priorité élevée (donc évaluée plus tôt) peut autoriser un flux que tu voulais bloquer plus tard. Concevoir les règles exige d'analyser leur ordre.

## 8.5 Règles par défaut

Les NSG contiennent des règles par défaut, notamment des règles pour le trafic au sein du VNet, les équilibreurs de charge Azure, l'accès Internet sortant et les refus finaux. Ces règles ont des priorités qui les placent après les règles personnalisées usuelles.

Il est important de comprendre deux choses :

1. Ajouter un NSG change le filtrage selon les règles appliquées, y compris les règles par défaut.
2. Le comportement effectif dépend des NSG associés à la fois au sous-réseau et à la NIC, des règles personnalisées et de la configuration générale du réseau.

Pour une architecture réelle, examine les règles effectives et n'imagine pas qu'une règle Allow isolée garantit l'accès.

## 8.6 Exemple : autoriser uniquement HTTPS vers le frontal

Objectif : autoriser TCP/443 depuis Internet vers un frontal Web, et éviter d'exposer les ports d'administration.

```text
Internet
   |
   | TCP 443 autorisé
   v
[ NSG-Web ]
   |
   v
[ Frontend Web ]

TCP 22 et TCP 3389 : pas d'autorisation Internet générale
```

La configuration du service doit également être prête à répondre sur HTTPS. Le NSG ne configure pas lui-même le serveur Web.

## 8.7 Exemple : autoriser le Web à appeler l'application

Hypothèse : l'application écoute sur TCP/8080 et doit uniquement être appelée par le sous-réseau Web.

```text
VM Web : 10.20.1.10
        |
        | TCP destination 8080
        v
NSG-App : autoriser source 10.20.1.0/24 vers TCP 8080
        |
        v
VM App : 10.20.2.10
```

Une règle illustrative peut spécifier :

- Direction : Inbound
- Source : `10.20.1.0/24`
- Port source : `*`
- Destination : `10.20.2.0/24` ou l'interface concernée
- Port destination : `8080`
- Protocole : TCP
- Action : Allow
- Priorité : `200`

L'ouverture du port 8080 à `Internet` serait beaucoup trop large pour ce besoin.

## 8.8 NSG et pare-feu du système d'exploitation

Même lorsque le NSG autorise TCP/8080, le pare-feu du système d'exploitation peut bloquer le paquet. Le service peut également ne pas écouter sur ce port.

Le diagnostic doit donc vérifier :

```text
Route correcte ?
    |
    v
NSG subnet autorise ?
    |
    v
NSG NIC autorise ?
    |
    v
Pare-feu local autorise ?
    |
    v
Service réellement en écoute ?
```

## 8.9 Principe du moindre privilège

Crée la règle la plus restrictive qui remplit le besoin :

- la bonne direction ;
- la bonne source ;
- la bonne destination ;
- le protocole requis ;
- le port requis ;
- le minimum de ressources concernées.

Évite les règles du type `Any -> Any -> Any -> Allow` dans les architectures métier. Utilise une règle temporaire très limitée seulement pour un test contrôlé, puis retire-la.

## 8.10 Matrice de flux de référence

| Source | Destination | Port | Décision visée | Justification |
|---|---|---:|---|---|
| Client Internet | Frontal Web | TCP 443 | Autoriser selon l'architecture | Site HTTPS public |
| Client Internet | VM App | TCP 8080 | Refuser | Application interne |
| VM Web | VM App | TCP 8080 | Autoriser | Appel métier |
| VM Web | Base de données | TCP 1433 | Refuser, sauf besoin démontré | Le Web ne doit pas contourner la couche App |
| VM App | Base de données | Port DB défini | Autoriser | Accès métier contrôlé |
| Internet | SSH/RDP sur VM privées | TCP 22/3389 | Ne pas exposer directement | Administration via voie sécurisée |
| VM privée | Endpoint public requis | Port du service | Autoriser selon la politique de sortie | Mises à jour ou API nécessaires |

Les ports d'exemple dépendent de l'application et ne sont pas des valeurs universelles.


# 9. NSG, ASG et tags de service

## 9.1 Application Security Groups (ASG)

Les Application Security Groups permettent de regrouper des interfaces réseau selon leur rôle applicatif afin de construire des règles plus faciles à lire que de longues listes d'adresses IP, dans les scénarios pris en charge.

Exemple conceptuel :

```text
ASG-Web : interfaces des machines Web
ASG-App : interfaces des machines applicatives

Règle : ASG-Web -> ASG-App -> TCP/8080 -> Allow
```

Les ASG ne remplacent pas la segmentation ni la validation du routage. Vérifie les restrictions d'utilisation et la prise en charge de chaque scénario dans la documentation Azure.

## 9.2 Service tags

Un service tag est un identifiant logique représentant des préfixes IP gérés par Microsoft pour certains services Azure. Il évite de maintenir manuellement certaines listes de plages IP.

Le tag `Internet` ou d'autres tags disponibles peuvent servir de source ou destination dans des règles compatibles. Les service tags disponibles dépendent du service et de la région.

Ne choisis pas un service tag simplement parce que son nom semble approprié : consulte sa définition officielle et assure-toi qu'il correspond au flux que tu veux autoriser.

## 9.3 NSG et Azure Firewall ne sont pas équivalents

| Fonction | NSG | Azure Firewall |
|---|---|---|
| Filtrage de base au niveau réseau | Oui | Oui, selon règles et modes |
| Association à un sous-réseau ou à une NIC | Oui | Non : service de pare-feu dédié dans une architecture réseau |
| Règles applicatives avancées centralisées | Limité | Capacités dédiées plus avancées |
| Inspection centralisée du trafic | Non, pas à lui seul | Oui, selon la conception |
| Remplace le routage | Non | Non, le routage doit acheminer le trafic à travers le pare-feu |
| Coût et exploitation d'un service dédié | NSG sans coût de service direct habituel, vérifier le contexte | Service facturable, configuration et exploitation à prévoir |

Le NSG est adapté à la segmentation élémentaire. Les besoins d'inspection centralisée, de filtrage avancé ou de contrôle egress peuvent nécessiter Azure Firewall ou une appliance réseau.


# PARTIE IV — INTERNET, ADMINISTRATION ET SERVICES PRIVÉS

# 10. Connectivité sortante et NAT Gateway

## 10.1 Entrant et sortant sont deux besoins différents

Une VM privée peut devoir télécharger des mises à jour ou appeler une API publique sans accepter des connexions entrantes initiées depuis Internet.

Exemple :

```text
VM privée
   |
   | Connexion initiée depuis la VM
   v
[ NAT Gateway / mécanisme de sortie explicite ]
   |
   v
Internet ou service public autorisé

Connexion entrante non sollicitée depuis Internet : non permise par NAT Gateway
```

Une solution de sortie ne transforme pas automatiquement la VM en serveur public.

## 10.2 Attention au changement du 31 mars 2026

Pour les nouveaux réseaux virtuels Azure depuis le 31 mars 2026, il ne faut plus supposer que l'ancien accès sortant par défaut sera présent. Conçois explicitement le besoin de connectivité sortante.

Les options possibles dépendent du scénario :

- Azure NAT Gateway pour une sortie Internet contrôlée au niveau du sous-réseau ;
- Azure Firewall pour une sortie qui doit être inspectée ou gouvernée de manière centralisée ;
- une appliance réseau adaptée ;
- des endpoints privés vers certains services pris en charge ;
- d'autres solutions d'accès selon la topologie et la politique de sécurité.

Vérifie la documentation Azure actuelle et la configuration effective de ton abonnement avant de déployer une architecture de production.

## 10.3 NAT Gateway

Azure NAT Gateway fournit une connectivité sortante évolutive pour les ressources des sous-réseaux auxquels il est associé, lorsqu'il est correctement configuré avec une adresse IP publique ou un préfixe public compatible.

Points à retenir :

- le NAT Gateway est associé à un ou plusieurs sous-réseaux compatibles dans le même VNet ;
- il permet aux ressources de créer des connexions vers l'extérieur ;
- il ne permet pas à lui seul des connexions entrantes non sollicitées depuis Internet ;
- il réduit le risque d'épuisement des ports SNAT par rapport à des solutions de sortie moins adaptées ;
- il n'effectue pas à lui seul le filtrage applicatif approfondi d'un pare-feu dédié ;
- le SKU, la zone, la redondance, les adresses publiques et le coût sont à examiner selon les exigences.

## 10.4 Schéma de sortie contrôlée

```text
VNet : 10.20.0.0/16
|
+-- snet-app : 10.20.2.0/24
|       |
|       +-- VM App privée
|               |
|               +-- Connexion sortante vers endpoint public
|
+-- NAT Gateway associé à snet-app
        |
        +-- Adresse IP publique / préfixe public
```

Le schéma montre le rôle logique du NAT Gateway. Il ne constitue pas à lui seul une configuration complète : il faut associer le service au sous-réseau et configurer une adresse IP publique ou un préfixe public approprié.

## 10.5 NAT Gateway ou Azure Firewall ?

| Besoin | Première piste à étudier |
|---|---|
| Sortie Internet de VM privées avec gestion SNAT | NAT Gateway |
| Filtrage réseau et applicatif centralisé | Azure Firewall |
| Routage de tout le trafic via une appliance | UDR + appliance compatible et correctement configurée |
| Accès privé à un service Azure pris en charge | Private Endpoint, selon le service et le besoin |
| Administration sécurisée d'une VM privée | Azure Bastion, VPN ou une autre voie d'administration contrôlée |

Ces services peuvent être combinés, mais le routage et les comportements effectifs doivent être étudiés. Par exemple, une route personnalisée qui détourne `0.0.0.0/0` vers une appliance peut faire que le trafic ne suit pas le chemin attendu par NAT Gateway.


# 11. Administration sécurisée avec Azure Bastion

## 11.1 Problème à résoudre

Les administrateurs doivent parfois ouvrir une session SSH sur Linux ou RDP sur Windows. Une solution simple mais risquée consiste à exposer directement les ports d'administration sur Internet.

Il est préférable d'éviter les IP publiques directement attachées aux VMs d'administration ou aux serveurs internes si une voie plus contrôlée est disponible.

## 11.2 Rôle d'Azure Bastion

Azure Bastion est un service managé permettant d'accéder à des machines virtuelles au moyen de SSH ou RDP, en utilisant leurs adresses IP privées dans les scénarios pris en charge. L'accès depuis le portail passe par une connexion protégée en TLS. Les VMs n'ont ainsi pas besoin d'une IP publique uniquement pour cet accès d'administration.

Les offres et options disponibles peuvent évoluer. Le déploiement dédié classique requiert un sous-réseau spécifique nommé `AzureBastionSubnet` et une configuration répondant aux prérequis de la référence Bastion choisie. Certaines offres ont des modèles de déploiement différents.

## 11.3 Schéma d'administration

```text
Administrateur
     |
     | Connexion sécurisée via portail / client pris en charge
     v
[ Azure Bastion ]
     |
     | SSH ou RDP vers IP privée
     v
[ VM Linux ou Windows privée ]
```

Le service Bastion réduit le besoin d'exposer les ports d'administration sur les VMs. Il ne remplace pas la gestion des identités, le moindre privilège, les politiques d'accès ou la surveillance des sessions.

## 11.4 Règles de sécurité recommandées

- Ne crée pas une règle SSH/RDP ouverte à tous uniquement pour éviter de configurer Bastion ou un VPN.
- Utilise l'authentification forte et les contrôles d'accès adaptés.
- Limite les opérateurs qui peuvent ouvrir des sessions.
- Journalise et surveille les accès privilégiés selon les exigences de l'environnement.
- Vérifie le coût avant de déployer un Bastion dédié pour un simple laboratoire, puis supprime-le lorsqu'il n'est plus nécessaire.


# 12. DNS dans Azure

## 12.1 Pourquoi DNS est-il important ?

Le DNS traduit un nom comme `app.intra.example` en une adresse IP. Les applications utilisent souvent des noms parce qu'ils sont plus faciles à gérer que des adresses IP codées en dur.

Si le DNS renvoie une mauvaise adresse, la connectivité peut échouer même lorsque les routes et les NSG sont corrects.

## 12.2 Options de résolution de noms

Les options courantes comprennent :

- la résolution fournie par Azure ;
- Azure Private DNS zones pour gérer des noms privés ;
- des serveurs DNS gérés par l'organisation ;
- Azure DNS Private Resolver pour des scénarios de résolution hybride dans les architectures appropriées.

Le choix dépend du besoin : résolution dans un seul VNet, partage de noms entre VNets, intégration avec un domaine d'entreprise ou résolution depuis le réseau local.

## 12.3 Azure-provided DNS

Azure fournit une résolution de noms de base pour certains scénarios des réseaux virtuels. L'adresse spéciale utilisée par le DNS fourni par Azure est `168.63.129.16` dans les contextes documentés par Microsoft.

Cette adresse est une adresse virtuelle de plateforme et ne doit pas être traitée comme une adresse ordinaire d'un serveur public. Si tu définis des DNS personnalisés, vérifie la configuration, les règles et les procédures de renouvellement de configuration des machines virtuelles concernées.

## 12.4 Azure Private DNS zones

Une zone DNS privée permet de gérer des noms privés. Elle peut être liée à un ou plusieurs VNets selon les règles et limites du service. Les liens doivent être conçus en fonction des besoins de résolution et de l'architecture.

Exemple conceptuel :

```text
Zone DNS privée : corp.example
|
+-- app.corp.example  -> 10.20.2.10
+-- db.corp.example   -> 10.20.3.10
```

Le schéma illustre des enregistrements. Les adresses doivent correspondre aux ressources réelles et aux règles d'administration DNS choisies.

## 12.5 DNS et Private Endpoint

Un Private Endpoint crée une interface réseau avec une adresse IP privée dans le VNet pour accéder à un service alimenté par Azure Private Link.

Pour que les clients utilisent le chemin privé, la résolution DNS doit généralement retourner la bonne adresse privée pour le nom de service concerné. Une configuration DNS erronée peut faire pointer un client vers l'endpoint public, ou empêcher la connexion.

```text
VM dans VNet
   |
   | Résolution DNS correcte
   v
Nom du service Azure -> IP privée du Private Endpoint
   |
   v
Connexion via Azure Private Link
```

Le Private Endpoint ne désactive pas nécessairement à lui seul l'accès public du service cible. Les contrôles d'accès public du service doivent être configurés séparément si l'objectif est de supprimer l'accès public.


# 13. VNet Peering

## 13.1 Qu'est-ce que le peering ?

Le peering de réseaux virtuels relie deux VNets afin de permettre un échange de trafic privé selon la configuration et les règles Azure applicables. Il peut être régional ou mondial selon les offres et le scénario.

Le peering ne signifie pas qu'on a fusionné les VNets : chacun conserve son espace d'adressage et sa gestion.

## 13.2 Exemple de peering

```text
VNet A : 10.20.0.0/16
        |
        | Peering privé
        |
VNet B : 10.30.0.0/16
```

Les plages ne se chevauchent pas. Le peering permet la connectivité entre elles si les options, les routes et les NSG l'autorisent.

## 13.3 Le peering n'est pas transitif par défaut

Point fondamental : si A est pairé avec B, et B est pairé avec C, cela ne signifie pas automatiquement que A peut accéder à C à travers B.

```text
VNet A <---- peering ----> VNet B <---- peering ----> VNet C
   X                                               X
   Pas de transit automatique A -> C via B
```

Des fonctionnalités de routage et des appliances peuvent permettre des architectures de transit, mais elles doivent être conçues explicitement. N'assume pas le transit à partir de la seule présence de deux peerings.

## 13.4 Vérifications pour un peering

- Les espaces d'adresses ne se chevauchent pas.
- Les peerings sont créés et dans un état opérationnel.
- Les options nécessaires sont cohérentes de chaque côté.
- Les routes attendues existent.
- Les NSG et les pare-feux autorisent les flux.
- Le DNS résout les noms vers les bonnes adresses.
- Le retour du trafic est possible.

## 13.5 Cas d'utilisation

- relier un VNet applicatif à un VNet de services partagés ;
- permettre une communication privée entre des environnements séparés ;
- construire une topologie hub-and-spoke avec des mécanismes de transit expressément configurés ;
- connecter des environnements qui ont des fonctions ou des responsabilités distinctes.

Le peering crée une connectivité réseau ; il n'autorise pas automatiquement toutes les applications ou tous les ports.


# 14. Service Endpoints et Private Endpoints : première distinction

## 14.1 Service Endpoint

Un Service Endpoint étend l'identité du VNet ou du sous-réseau vers certains services Azure pris en charge. Le trafic vers le service reste sur le réseau backbone Microsoft, et la configuration du service peut être restreinte aux réseaux autorisés.

Le service est toujours accédé par son endpoint de service, et les détails d'adressage et de routage ne sont pas identiques à ceux d'un Private Endpoint.

## 14.2 Private Endpoint

Un Private Endpoint représente une interface réseau dans le VNet, avec une adresse IP privée, qui établit une connexion à un service via Azure Private Link.

C'est utile lorsque le client doit accéder au service au moyen d'une adresse privée dans le réseau virtuel.

## 14.3 Comparaison simplifiée

| Élément | Service Endpoint | Private Endpoint |
|---|---|---|
| Principe | Étend l'identité du sous-réseau au service pris en charge | Ajoute une interface réseau à IP privée pour atteindre le service |
| Adresse privée dans le VNet pour le service cible | Pas par le même mécanisme | Oui, pour le Private Endpoint |
| Utilité | Restreindre l'accès à certains services à des VNets/sous-réseaux compatibles | Connectivité privée vers le service via Private Link |
| DNS privé | Pas le même modèle de résolution qu'un endpoint privé | Souvent essentiel pour pointer le nom du service vers l'IP privée |
| Réduction de l'exposition publique | Dépend du service et de ses contrôles | Le private endpoint ne désactive pas automatiquement l'accès public du service |

Le choix exact dépend du service Azure ciblé, des objectifs réseau et de la sécurité. Vérifie les services pris en charge et leurs prérequis avant de choisir.


# PARTIE V — ARCHITECTURE DE RÉFÉRENCE ET ATELIER GUIDÉ

# 15. Architecture pédagogique de référence

Nous allons utiliser cette architecture dans l'atelier puis dans le challenge final.

## 15.1 Besoin métier

Une petite entreprise veut héberger une application composée de deux couches :

- un frontal Web qui reçoit les requêtes des utilisateurs ;
- une application métier qui ne doit pas être directement joignable depuis Internet.

Le cours doit montrer la segmentation et les règles de flux. Pour éviter une exposition inutile, l'exemple n'attribue pas d'adresse IP publique directement au serveur applicatif.

## 15.2 Plan d'adressage

```text
VNet : vnet-formation
CIDR : 10.20.0.0/16
Région : choisir une région proche et disponible pour l'abonnement
Groupe de ressources : rg-vnet-formation

Sous-réseaux :
- snet-web : 10.20.1.0/24
- snet-app : 10.20.2.0/24
- snet-data : 10.20.3.0/24 (réservé, non requis pour l'atelier initial)
```

L'espace est privé, contenu dans le VNet et sans chevauchement entre sous-réseaux.

## 15.3 Vue logique

```text
                                  UTILISATEUR
                                      |
                                      | HTTPS TCP/443
                                      v
                           [ Point d'entrée Web ]
                                      |
                           +----------+----------+
                           |       VNet          |
                           | 10.20.0.0/16        |
                           |                     |
                           | +-----------------+ |
                           | | snet-web        | |
                           | | 10.20.1.0/24    | |
                           | | VM/Front Web    | |
                           | +--------+--------+ |
                           |          |          |
                           |          | TCP/8080 |
                           |          v          |
                           | +-----------------+ |
                           | | snet-app        | |
                           | | 10.20.2.0/24    | |
                           | | VM App privée   | |
                           | +-----------------+ |
                           |                     |
                           +---------------------+

Administration : Bastion / VPN / accès privé contrôlé
Sortie Internet requise : solution explicite (ex. NAT Gateway)
```

Le « point d'entrée Web » est un rôle architectural. Dans le laboratoire, il peut être simulé si les ressources facturables ne sont pas déployées. Un serveur Web public réel doit disposer d'un point d'entrée correctement conçu et de règles d'accès appropriées.

## 15.4 Politique de flux souhaitée

| De | Vers | Port | Décision |
|---|---|---:|---|
| Client autorisé | Front Web | TCP 443 | Autoriser selon le besoin Web |
| Front Web | VM App | TCP 8080 | Autoriser |
| Internet | VM App | TCP 8080 | Refuser / ne pas exposer |
| Internet | VM App | TCP 22 ou 3389 | Ne pas autoriser directement |
| VM App | Internet | Ports requis par les mises à jour | Autoriser via une solution de sortie prévue, si nécessaire |
| Admin | VM privée | SSH/RDP | Via Bastion, VPN ou mécanisme approuvé |

Les règles NSG seules ne suffisent pas à fournir tous les composants de l'architecture. Il faut aussi déployer le point d'entrée, l'application, la voie d'administration et la sortie nécessaire.


# 16. Atelier guidé 1 — Créer le VNet et les sous-réseaux

**Objectif :** créer uniquement la base réseau, sans machine virtuelle obligatoire.

**Ressources :** abonnement Azure et autorisation de créer un VNet. La création d'un VNet et de sous-réseaux est généralement moins coûteuse que les services de calcul ou les passerelles, mais vérifie toujours la tarification applicable.

## 16.1 Étape 1 — Choisir le groupe de ressources

Dans le portail Azure :

1. Ouvre **Resource groups** (Groupes de ressources).
2. Crée `rg-vnet-formation`.
3. Sélectionne une région adaptée à ton apprentissage.
4. Vérifie l'abonnement choisi.
5. Crée le groupe.

Le groupe de ressources est un conteneur de gestion. Ce n'est pas lui qui attribue le réseau IP.

## 16.2 Étape 2 — Créer le VNet

1. Recherche **Virtual networks** dans le portail.
2. Sélectionne **Create**.
3. Choisis l'abonnement et le groupe `rg-vnet-formation`.
4. Donne le nom `vnet-formation`.
5. Choisis la même région que les autres ressources de l'atelier.
6. Dans l'onglet d'adressage IP, définis l'espace `10.20.0.0/16`.
7. Crée le premier sous-réseau `snet-web` avec `10.20.1.0/24`.
8. Examine la validation avant de créer.
9. Crée le VNet.

Les libellés et l'ordre des écrans peuvent changer avec l'évolution du portail. Le résultat visé demeure le VNet et son espace d'adressage.

## 16.3 Étape 3 — Ajouter le sous-réseau applicatif

1. Ouvre `vnet-formation`.
2. Ouvre **Subnets**.
3. Ajoute `snet-app`.
4. Utilise `10.20.2.0/24`.
5. Vérifie qu'il appartient au VNet `vnet-formation`.
6. Vérifie qu'il ne chevauche pas `snet-web`.
7. Enregistre.

## 16.4 Étape 4 — Contrôles après création

Tu dois obtenir :

```text
vnet-formation : 10.20.0.0/16
|
+-- snet-web : 10.20.1.0/24
+-- snet-app : 10.20.2.0/24
```

Vérifie :

- que le VNet existe dans la bonne région ;
- que l'espace d'adressage est correct ;
- que les deux sous-réseaux sont présents ;
- que les sous-réseaux ne se chevauchent pas ;
- que tu n'as pas accidentellement créé de ressource facturable non nécessaire.

### Questions de contrôle

1. Quelle est la différence entre `10.20.0.0/16` et `10.20.1.0/24` ?
2. Pourquoi `10.20.1.0/24` et `10.20.2.0/24` ne se chevauchent-ils pas ?
3. Le fait de nommer un sous-réseau `snet-web` l'expose-t-il automatiquement à Internet ?
4. Est-il possible de joindre une VM privée sans IP publique ?

Les réponses sont fournies dans la section des exercices corrigés.


# 17. Atelier guidé 2 — Créer et associer les NSG

**Objectif :** comprendre comment les règles de filtrage changent la connectivité.

## 17.1 Créer un NSG Web

Dans le portail :

1. Recherche **Network security groups**.
2. Crée `nsg-web` dans `rg-vnet-formation` et dans la région du laboratoire.
3. Ouvre **Inbound security rules**.
4. Examine les règles par défaut.
5. Ajoute uniquement les règles nécessaires au besoin de l'atelier.

Pour une démonstration conceptuelle d'un site HTTPS, la règle doit viser TCP/443 depuis les sources autorisées. Si l'exercice consiste simplement à observer le filtrage, tu peux utiliser une règle de test très limitée et la supprimer immédiatement après validation.

**Important :** n'ouvre pas SSH (TCP/22) ou RDP (TCP/3389) à toutes les adresses Internet dans une architecture réelle. Si une VM doit être administrée, prévois Bastion, un VPN ou un accès approuvé.

## 17.2 Créer un NSG App

1. Crée `nsg-app`.
2. Prépare une règle entrante autorisant TCP/8080 depuis `10.20.1.0/24` vers les ressources du sous-réseau applicatif.
3. Ne crée pas de règle TCP/8080 depuis `Internet`.
4. Examine les règles de refus et les priorités existantes.

Cette règle illustre l'accès de la couche Web vers la couche applicative. Si un service réel écoute sur un autre port, remplace 8080 par le port approprié.

## 17.3 Associer le NSG au sous-réseau

1. Ouvre le VNet `vnet-formation`.
2. Ouvre **Subnets**.
3. Modifie `snet-web` et associe `nsg-web`.
4. Modifie `snet-app` et associe `nsg-app`.
5. Enregistre et vérifie les associations.

Une association au niveau du sous-réseau s'applique aux interfaces qui s'y trouvent. Évite de multiplier sans raison les NSG de sous-réseau et de NIC : le filtrage cumulé est plus difficile à dépanner.

## 17.4 Vérification logique

```text
Source : VM Web dans 10.20.1.0/24
Destination : VM App dans 10.20.2.0/24
Protocole : TCP
Port destination : 8080

Route interne au VNet : présente selon la configuration normale
NSG Web sortant : doit autoriser le flux si une règle de refus a été ajoutée
NSG App entrant : doit autoriser le flux
Pare-feu local de la VM App : doit autoriser le flux
Service App : doit écouter sur TCP/8080
```

N'annonce pas un test réseau comme « réussi » sur la seule base d'une règle NSG. Le trafic réel doit être validé avec le service et les outils disponibles.


# 18. Atelier guidé 3 — Déployer les VMs en toute prudence (facultatif)

**OPTIONNEL — RESSOURCES FACTURABLES**

Cet atelier peut générer des frais de calcul, de stockage, d'adresse IP, d'accès sortant ou de services d'administration. Les tarifs varient selon la région, le SKU et l'utilisation. Pour apprendre l'adressage et les NSG, tu peux arrêter le cours aux ateliers précédents sans créer de VM.

## 18.1 Préparer le déploiement

Avant de créer des machines :

- vérifie le quota de calcul de l'abonnement ;
- choisis une taille de VM économique adaptée au laboratoire ;
- décide si Bastion, VPN ou une autre méthode sera utilisée pour l'administration ;
- ne prévois pas de public IP sur la VM applicative ;
- détermine comment la VM accédera aux mises à jour et aux services externes nécessaires ;
- vérifie la région et la disponibilité des images OS ;
- fixe un plan de suppression des ressources après l'exercice.

## 18.2 Déployer la VM Web

Dans le portail, crée une VM de laboratoire dans `snet-web`. Choisis une image Linux ou Windows prise en charge et une taille peu coûteuse compatible avec l'usage.

Pour une véritable exposition Web publique, utilise un point d'entrée défini par l'architecture et les règles adaptées. Ne crée pas d'accès administratif public ouvert. Dans un atelier de pur réseau, la VM peut rester sans exposition publique : l'objectif est de vérifier le filtrage interne, pas de publier un site.

## 18.3 Déployer la VM App

Crée une seconde VM dans `snet-app`.

Exigences pédagogiques :

- IP privée dans la plage du sous-réseau ;
- pas d'IP publique directement attachée pour ce scénario ;
- NSG App associé ;
- aucune règle entrante TCP/8080 depuis Internet ;
- une voie d'administration privée définie avant le besoin d'accès interactif.

## 18.4 Vérifier les adresses

Pour chaque interface réseau, vérifie :

- le VNet et le sous-réseau sélectionnés ;
- l'adresse IP privée ;
- la présence ou l'absence de configuration IP publique ;
- l'association du NSG ;
- la table de routage associée au sous-réseau, si l'une a été créée.

Les deux VMs doivent utiliser des adresses distinctes, appartenir au VNet prévu et être affectées à leurs sous-réseaux respectifs.

## 18.5 Test de service

Sur la VM App, configure un service de test qui écoute sur TCP/8080, uniquement si tu sais administrer l'OS et sécuriser ce service. Puis, depuis la VM Web, teste la connexion vers l'adresse privée de la VM App.

Si tu ne disposes pas d'une voie d'administration fiable, n'ouvre pas de port public au hasard. Utilise le portail et les outils de diagnostic ou un mécanisme d'accès approuvé.


# 19. Atelier guidé 4 — Créer le réseau avec Azure CLI

**Objectif :** automatiser le réseau de base. Les commandes ci-dessous créent un groupe de ressources, un VNet, des sous-réseaux et des NSG. Elles ne déploient pas de VM ni de Bastion.

Avant d'exécuter les commandes :

1. Installe Azure CLI depuis la documentation officielle.
2. Ouvre un terminal.
3. Connecte-toi avec `az login`.
4. Si plusieurs abonnements existent, sélectionne le bon abonnement.
5. Vérifie la région disponible pour ton abonnement.

## 19.1 Vérifier la connexion et l'abonnement

```bash
az login
az account show --output table
az account list --output table
```

Si nécessaire, sélectionne un abonnement autorisé :

```bash
az account set --subscription "NOM_OU_ID_ABONNEMENT"
az account show --output table
```

Remplace le texte entre guillemets par le nom ou l'identifiant réel de ton abonnement. Ne partage pas de jetons d'accès ou de secrets.

## 19.2 Créer le groupe de ressources

```bash
az group create \
  --name rg-vnet-formation \
  --location westeurope \
  --output table
```

`westeurope` est un exemple de nom de région Azure ; choisis une région disponible adaptée à ton abonnement et à ton environnement.

## 19.3 Créer le VNet et le sous-réseau Web

```bash
az network vnet create \
  --resource-group rg-vnet-formation \
  --name vnet-formation \
  --location westeurope \
  --address-prefixes 10.20.0.0/16 \
  --subnet-name snet-web \
  --subnet-prefixes 10.20.1.0/24 \
  --output table
```

## 19.4 Ajouter le sous-réseau App

```bash
az network vnet subnet create \
  --resource-group rg-vnet-formation \
  --vnet-name vnet-formation \
  --name snet-app \
  --address-prefixes 10.20.2.0/24 \
  --output table
```

## 19.5 Vérifier le VNet et les sous-réseaux

```bash
az network vnet show \
  --resource-group rg-vnet-formation \
  --name vnet-formation \
  --output jsonc

az network vnet subnet list \
  --resource-group rg-vnet-formation \
  --vnet-name vnet-formation \
  --output table
```

## 19.6 Créer les NSG

```bash
az network nsg create \
  --resource-group rg-vnet-formation \
  --name nsg-web \
  --location westeurope \
  --output table

az network nsg create \
  --resource-group rg-vnet-formation \
  --name nsg-app \
  --location westeurope \
  --output table
```

## 19.7 Ajouter une règle entrante HTTPS au NSG Web

La règle suivante illustre l'ouverture du port HTTPS. Elle n'est pertinente que si le frontal Web doit réellement recevoir HTTPS et que l'exposition publique est prévue par l'architecture.

```bash
az network nsg rule create \
  --resource-group rg-vnet-formation \
  --nsg-name nsg-web \
  --name Allow-HTTPS-In \
  --priority 200 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes Internet \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 443 \
  --output table
```

La règle autorise le trafic correspondant au niveau du NSG. Elle n'affecte pas d'IP publique, ne déploie pas un serveur HTTPS et ne garantit pas qu'une connexion arrive jusqu'à une application.

## 19.8 Ajouter une règle App limitée à la couche Web

```bash
az network nsg rule create \
  --resource-group rg-vnet-formation \
  --nsg-name nsg-app \
  --name Allow-App-From-Web \
  --priority 200 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes 10.20.1.0/24 \
  --source-port-ranges '*' \
  --destination-address-prefixes 10.20.2.0/24 \
  --destination-port-ranges 8080 \
  --output table
```

Cette règle est un exemple de segmentation. N'ajoute pas une règle équivalente avec `Internet` comme source : cela contredirait l'objectif de garder la couche applicative privée.

## 19.9 Associer les NSG aux sous-réseaux

Selon la version et le contexte de la CLI, la commande d'association peut accepter l'ID complet du NSG. Récupère explicitement cet ID, puis applique-le :

```bash
NSG_WEB_ID=$(az network nsg show \
  --resource-group rg-vnet-formation \
  --name nsg-web \
  --query id --output tsv)

NSG_APP_ID=$(az network nsg show \
  --resource-group rg-vnet-formation \
  --name nsg-app \
  --query id --output tsv)

az network vnet subnet update \
  --resource-group rg-vnet-formation \
  --vnet-name vnet-formation \
  --name snet-web \
  --network-security-group "$NSG_WEB_ID" \
  --output table

az network vnet subnet update \
  --resource-group rg-vnet-formation \
  --vnet-name vnet-formation \
  --name snet-app \
  --network-security-group "$NSG_APP_ID" \
  --output table
```

Ces commandes utilisent une syntaxe de shell POSIX, par exemple Bash. Dans PowerShell, la syntaxe d'affectation de variables et de continuation de lignes est différente.

## 19.10 Contrôler les règles et associations

```bash
az network nsg rule list \
  --resource-group rg-vnet-formation \
  --nsg-name nsg-web \
  --output table

az network nsg rule list \
  --resource-group rg-vnet-formation \
  --nsg-name nsg-app \
  --output table

az network vnet subnet list \
  --resource-group rg-vnet-formation \
  --vnet-name vnet-formation \
  --output jsonc
```

Vérifie les associations NSG, les préfixes des sous-réseaux et les règles personnalisées.

## 19.11 Nettoyer le laboratoire CLI

Si le groupe de ressources a été créé uniquement pour cet exercice et ne contient rien d'autre à conserver, supprime le laboratoire complet après validation :

```bash
az group delete \
  --name rg-vnet-formation \
  --yes \
  --no-wait
```

La commande de suppression est destructive. Vérifie le nom du groupe et son contenu avant de l'exécuter. `--no-wait` ne signifie pas que la suppression est instantanée : Azure effectue l'opération en arrière-plan.


# PARTIE VI — OBSERVER, TESTER ET DÉPANNER

# 20. Méthode de diagnostic réseau

## 20.1 Ne pas diagnostiquer au hasard

Une panne réseau peut venir de plusieurs couches. La démarche suivante aide à localiser l'étape en échec.

```text
1. Le nom est-il résolu correctement ?
             |
             v
2. L'adresse IP de destination est-elle correcte ?
             |
             v
3. Le chemin de routage existe-t-il ?
             |
             v
4. Les NSG autorisent-ils le flux aux deux niveaux ?
             |
             v
5. Le pare-feu local laisse-t-il passer le trafic ?
             |
             v
6. Le service écoute-t-il sur le port voulu ?
             |
             v
7. Le trafic retour fonctionne-t-il ?
```

## 20.2 Outils Azure utiles

Selon la ressource, la région et les droits d'accès, utilise :

- les vues de réseau de la VM et de son interface réseau ;
- les règles de sécurité effectives ;
- les routes effectives ;
- Azure Network Watcher ;
- IP flow verify pour certaines vérifications de flux ;
- Connection troubleshoot ;
- NSG flow logs lorsque la solution de journalisation choisie les prend en charge ;
- les journaux du pare-feu et du système d'exploitation ;
- les tests DNS et TCP exécutés depuis la bonne source.

Les fonctionnalités et leur disponibilité peuvent évoluer. Vérifie la documentation actuelle de chaque outil et les conditions de région, de type de ressource et de droits nécessaires.

## 20.3 Tableau de diagnostic

| Symptôme | Causes possibles | Vérifications prioritaires |
|---|---|---|
| La VM ne reçoit pas de connexion | IP/point d'entrée incorrect, NSG, route, pare-feu local | IP publique/privée, NSG effectifs, routes, écoute du service |
| La VM Web joint la VM App par IP mais pas par nom | DNS | Résultat de `nslookup`, zone privée, liens VNet, enregistrement |
| Une VM ne peut pas télécharger de mises à jour | Absence de sortie explicite, NSG, DNS, UDR | Route, NAT Gateway/Firewall, règles egress, résolution DNS |
| Une connexion interne échoue | NSG subnet/NIC, pare-feu local, mauvais port | Flux exact, règles effectives, service en écoute |
| Le peering existe mais le flux échoue | Plages qui se chevauchent, état/options, NSG, routes | Adressage, état du peering, itinéraire, règles et retour |
| Le Private Endpoint échoue par nom | DNS ou approbation de la connexion | Résolution DNS, état Approved, route et règles |
| SSH/RDP ne fonctionne pas | Voie d'administration ou authentification incorrecte | Bastion/VPN, IP privée, droits, NSG et pare-feu local |
| Un changement de route a interrompu la sortie | UDR incorrecte ou appliance indisponible | Routes effectives, prochain saut, état de l'appliance, retour |

## 20.4 Exemple de diagnostic : la VM App n'est pas joignable

**Situation :** la VM Web `10.20.1.10` tente d'accéder à la VM App `10.20.2.10` sur TCP/8080. La connexion échoue.

Ne commence pas par autoriser tous les ports. Procède ainsi :

1. Vérifie les IP et les sous-réseaux des deux interfaces.
2. Confirme que les deux VMs sont dans le VNet attendu ou que les VNets disposent d'une connexion explicite.
3. Vérifie la route effective vers `10.20.2.10` depuis la source.
4. Vérifie l'NSG de `snet-web`, puis celui de `snet-app`.
5. Vérifie tout NSG associé aux NIC.
6. Vérifie que la VM App autorise TCP/8080 dans son pare-feu local.
7. Vérifie que l'application écoute sur la bonne interface et sur le bon port.
8. Teste avec l'IP privée avant d'investiguer le DNS.
9. Si la connexion est établie par IP mais pas par nom, reprends l'analyse DNS.

## 20.5 Pourquoi un ping échoue-t-il ?

Un échec de ping ne prouve pas qu'un service TCP est inaccessible. ICMP peut être bloqué par la politique réseau ou par le système d'exploitation, alors que TCP/443 fonctionne. À l'inverse, un ping réussi ne garantit pas que l'application écoute sur le port requis.

Teste le protocole réellement utilisé par l'application et interprète le résultat dans son contexte.


# 21. Bonnes pratiques de conception

## 21.1 Adressage

- Choisir une plage qui ne chevauche pas le réseau local ni les autres VNets reliés.
- Documenter le plan CIDR.
- Réserver des plages pour les extensions et les services dédiés.
- Éviter de créer des sous-réseaux trop petits pour les besoins futurs.
- Contrôler les adresses réservées par Azure.

## 21.2 Sécurité

- Appliquer le moindre privilège dans les NSG.
- N'exposer que les ports nécessaires.
- Garder les services applicatifs et les bases de données privés autant que possible.
- Éviter l'administration directe depuis Internet lorsque Bastion, un VPN ou un autre mécanisme sécurisé convient.
- Vérifier les règles effectives plutôt que de regarder une seule règle isolée.
- Distinguer NSG, pare-feu local, Azure Firewall et contrôles d'accès de l'application.

## 21.3 Routage et sortie

- Comprendre les routes système avant d'ajouter une UDR.
- Vérifier les prochains sauts des routes personnalisées.
- Concevoir explicitement la sortie Internet, particulièrement pour les nouveaux VNets créés depuis le 31 mars 2026.
- Ne pas détourner tout le trafic vers une appliance sans garantir son fonctionnement et le chemin retour.
- Prévoir des routes retour cohérentes dans les architectures hybrides.

## 21.4 DNS

- Utiliser des noms stables plutôt que des IP codées en dur lorsque cela convient.
- Gérer les zones privées et leurs liens VNet explicitement.
- Contrôler la résolution DNS avant de conclure à une panne de routage.
- Vérifier les zones DNS privées lors d'un déploiement de Private Endpoint.

## 21.5 Exploitation

- Utiliser une convention de nommage cohérente.
- Documenter chaque sous-réseau et chaque règle réseau.
- Activer les diagnostics nécessaires et conserver les journaux selon les exigences.
- Contrôler les coûts et les ressources oubliées.
- Tester les changements dans un environnement non productif lorsque possible.
- Utiliser des déploiements déclaratifs (Bicep ou Terraform, par exemple) lorsque la reproductibilité devient importante.


# 22. Erreurs fréquentes des débutants

## Erreur 1 — Croire qu'un VNet donne automatiquement un accès Internet complet

**Pourquoi c'est faux :** l'accès Internet dépend de la configuration de l'adresse, du service, des routes, des contrôles réseau et d'un mécanisme de sortie approprié. Les nouveaux VNets depuis le 31 mars 2026 ne doivent plus être supposés disposer de l'ancien accès sortant par défaut.

**Bonne approche :** décider explicitement quels composants doivent communiquer vers l'extérieur et déployer une solution adaptée.

## Erreur 2 — Croire qu'un NSG crée un chemin réseau

**Pourquoi c'est faux :** un NSG autorise ou refuse des flux, mais ne crée pas à lui seul la route ni l'adresse d'un point d'entrée public.

**Bonne approche :** examiner l'adressage, le routage, les NSG et le service applicatif.

## Erreur 3 — Ouvrir tous les ports pour tester

**Pourquoi c'est dangereux :** une règle trop large expose d'autres services que celui qui doit être validé et peut rester en place après le dépannage.

**Bonne approche :** autoriser une source connue, une destination, un protocole et un port précis, puis supprimer les règles temporaires.

## Erreur 4 — Mettre une IP publique sur chaque VM

**Pourquoi c'est risqué :** les services internes et les interfaces d'administration sont exposés inutilement.

**Bonne approche :** garder les machines internes privées et utiliser Bastion, VPN ou un point d'administration approuvé.

## Erreur 5 — Utiliser des plages IP qui se chevauchent

**Pourquoi c'est bloquant :** le routage entre les réseaux devient ambigu ou impossible dans les architectures concernées.

**Bonne approche :** tenir un plan d'adressage global avant de multiplier les VNets.

## Erreur 6 — Croire que le peering est transitif

**Pourquoi c'est faux :** les peerings A-B et B-C ne créent pas automatiquement un transit A-C.

**Bonne approche :** concevoir et configurer explicitement le transit lorsqu'il est nécessaire.

## Erreur 7 — Se fier uniquement à la règle NSG visible

**Pourquoi c'est incomplet :** une seconde NSG, une UDR, un pare-feu local ou l'absence de service en écoute peuvent bloquer le flux.

**Bonne approche :** vérifier toute la chaîne de communication.

## Erreur 8 — Oublier le DNS d'un Private Endpoint

**Pourquoi c'est problématique :** un nom de service résolu vers la mauvaise adresse peut envoyer le client vers un chemin qui ne répond pas au besoin.

**Bonne approche :** tester le nom depuis la VM cliente et vérifier les zones privées et leurs liens.

## Erreur 9 — Oublier le coût d'un service laissé actif

**Pourquoi c'est coûteux :** une VM ou un service managé peut continuer à être facturé selon le tarif et l'état de la ressource.

**Bonne approche :** supprimer ou désallouer les ressources selon le service et le besoin, et vérifier la facturation. La désallocation d'une VM ne garantit pas que toutes les ressources associées cessent d'être facturées.


# PARTIE VII — EXERCICES DE COMPRÉHENSION AVEC CORRECTIONS

# 23. Exercices

Essaie de répondre sans consulter le corrigé. L'objectif n'est pas de mémoriser les noms des services, mais d'expliquer pourquoi une architecture fonctionne ou échoue.

## Exercice 1 — Identifier les ressources

Explique la différence entre :

1. abonnement ;
2. groupe de ressources ;
3. VNet ;
4. sous-réseau ;
5. interface réseau ;
6. NSG.

## Exercice 2 — CIDR

Un VNet utilise `10.20.0.0/16`.

1. Combien d'adresses contient théoriquement le VNet ?
2. Combien d'adresses IPv4 y a-t-il au total dans `10.20.1.0/24` ?
3. Combien d'adresses sont réservées par Azure dans ce sous-réseau IPv4 ?
4. Les sous-réseaux `10.20.1.0/24` et `10.20.2.0/24` se chevauchent-ils ?
5. `10.20.1.128/25` chevauche-t-il `10.20.1.0/24` ?

## Exercice 3 — Segmentation

Une entreprise dispose d'un frontal Web, d'une application et d'une base de données. Propose un découpage en trois sous-réseaux et écris une matrice des flux nécessaires.

## Exercice 4 — NSG

Une règle entrante du NSG App autorise TCP/8080 depuis Internet. La politique de sécurité stipule que seule la VM Web doit appeler l'application.

1. Pourquoi la règle est-elle inadaptée ?
2. Quelle plage source pourrais-tu utiliser dans le laboratoire ?
3. Quels autres éléments dois-tu vérifier si le flux échoue après correction de la règle ?

## Exercice 5 — Routage et filtrage

La route vers l'adresse de la VM App existe, mais la connexion TCP/8080 échoue. Est-ce que cela prouve qu'il manque une route ? Explique.

## Exercice 6 — Connectivité sortante

Une VM privée doit télécharger des mises à jour, mais elle ne doit pas accepter de connexions entrantes non sollicitées depuis Internet.

1. Quelle solution de sortie peut être étudiée ?
2. Cette solution ouvre-t-elle automatiquement le port SSH depuis Internet ?
3. Que faut-il vérifier dans un VNet créé après le 31 mars 2026 ?

## Exercice 7 — Peering

VNet A est pairé avec VNet B. VNet B est pairé avec VNet C. La VM de A ne joint pas la VM de C.

1. Pourquoi le seul peering ne suffit-il pas à conclure que le transit existe ?
2. Quels contrôles faut-il faire ?

## Exercice 8 — DNS

Une VM joint un service par son IP privée, mais pas avec son nom DNS.

1. Quelle couche faut-il investiguer en priorité ?
2. Cite trois éléments à vérifier.

## Exercice 9 — Bastion

Pourquoi est-il préférable de ne pas ouvrir SSH et RDP à Internet pour administrer des serveurs internes ? Donne deux solutions d'accès plus contrôlées.

## Exercice 10 — Analyse de panne

Une VM App n'est pas joignable depuis la VM Web. Les deux machines sont dans le VNet prévu. Établis un ordre de diagnostic en au moins six étapes.


# 24. Corrections des exercices

## Correction 1 — Identifier les ressources

1. **Abonnement :** limite de gestion, contrôle d'accès et facturation.
2. **Groupe de ressources :** conteneur logique de ressources Azure.
3. **VNet :** réseau virtuel qui possède un espace d'adressage.
4. **Sous-réseau :** portion de l'espace IP du VNet, destinée à des ressources et éventuellement associée à un NSG ou une table de routes.
5. **Interface réseau :** composant qui connecte une VM au réseau Azure et porte sa configuration IP.
6. **NSG :** ensemble de règles qui autorisent ou refusent certains flux entrants ou sortants.

## Correction 2 — CIDR

1. `/16` contient `2^(32-16) = 65 536` adresses.
2. `/24` contient `2^(32-24) = 256` adresses au total.
3. Azure réserve cinq adresses IPv4 par sous-réseau IPv4 ordinaire.
4. Non, les deux plages `/24` sont distinctes.
5. Oui. `10.20.1.128/25` est entièrement inclus dans `10.20.1.0/24`, donc elles se chevauchent.

## Correction 3 — Segmentation

Exemple valide :

```text
VNet : 10.20.0.0/16
- snet-web  : 10.20.1.0/24
- snet-app  : 10.20.2.0/24
- snet-data : 10.20.3.0/24
```

Matrice de flux possible :

| Source | Destination | Port | Décision |
|---|---|---:|---|
| Client Web autorisé | Frontal | TCP 443 | Autoriser |
| Frontal | App | TCP 8080 | Autoriser |
| App | Base de données | Port utilisé par le moteur | Autoriser |
| Internet | App | TCP 8080 | Refuser / aucune exposition directe |
| Internet | Base de données | Port de base de données | Refuser |

Le port de la base dépend du moteur utilisé. Il faut autoriser uniquement le port réellement nécessaire.

## Correction 4 — NSG

1. La source `Internet` est trop large ; l'application doit seulement recevoir le flux de la couche Web.
2. Dans le laboratoire, la source peut être `10.20.1.0/24`, si c'est bien le préfixe du sous-réseau Web.
3. Vérifie la route, le NSG Web sortant, les NSG associés à la NIC, le pare-feu local de la VM App, le port d'écoute de l'application et le trajet retour.

## Correction 5 — Routage et filtrage

Non. La route peut exister, mais un NSG ou un pare-feu local peut bloquer TCP/8080. Le service peut également ne pas écouter sur le port. Il faut isoler le niveau qui échoue.

## Correction 6 — Connectivité sortante

1. Azure NAT Gateway est une solution courante à étudier ; un pare-feu ou une architecture de sortie contrôlée peut être requis selon la politique.
2. Non. NAT Gateway ne permet pas à lui seul des connexions entrantes non sollicitées depuis Internet.
3. Ne pas supposer que l'ancien accès sortant par défaut existe. Prévoir une méthode de sortie explicite, puis vérifier les routes, les NSG et le fonctionnement du service.

## Correction 7 — Peering

1. Le peering n'est pas transitif par défaut. Deux peerings ne créent pas à eux seuls une route de transit de A vers C.
2. Vérifie le chevauchement des espaces d'adresses, l'état des peerings, les options de passerelle/transit si pertinentes, les routes effectives, les NSG, les pare-feux et les routes retour.

## Correction 8 — DNS

1. Investiguer la résolution DNS en priorité, puisque la connexion par IP privée fonctionne.
2. Vérifie la réponse de `nslookup`, la zone DNS (publique ou privée), les enregistrements, les liens de la zone privée aux VNets et la configuration du serveur DNS utilisé.

## Correction 9 — Bastion

Les ports SSH/RDP exposés directement permettent des tentatives de connexion depuis des sources non désirées et augmentent la surface d'attaque. Deux solutions possibles : Azure Bastion ou un VPN contrôlé. D'autres architectures d'administration approuvées peuvent également convenir.

## Correction 10 — Analyse de panne

Ordre de diagnostic possible :

1. Confirmer les IP et les sous-réseaux des deux VMs.
2. Vérifier la route effective vers la VM App.
3. Vérifier le NSG du sous-réseau Web pour le trafic sortant.
4. Vérifier les NSG du sous-réseau App et de la NIC App pour le trafic entrant.
5. Vérifier le pare-feu du système d'exploitation App.
6. Confirmer que le service écoute sur l'adresse attendue et le bon port.
7. Tester le protocole réel depuis la VM Web.
8. Vérifier les journaux et le retour du trafic.
9. Si un nom DNS est utilisé, tester ensuite sa résolution.


# PARTIE VIII — CHALLENGE FINAL INTÉGRÉ AU COURS

# 25. Challenge final : construire un réseau Azure segmenté

**Niveau :** débutant appliqué  
**Durée indicative :** 2 à 4 heures selon que les VMs sont déployées ou que l'exercice reste conceptuel  
**Note totale :** 100 points  
**Mode :** conception, justification, configuration et diagnostic

Le challenge est volontairement placé à la fin du cours. Il évalue les notions vues dans les chapitres précédents ; il ne remplace pas le cours.

## 25.1 Scénario

Tu rejoins une petite entreprise qui migre une application vers Azure. L'application comprend :

- un frontal Web, qui doit recevoir du trafic HTTPS autorisé ;
- un serveur applicatif, qui écoute sur TCP/8080 ;
- une future couche de données, qui doit rester privée ;
- des administrateurs qui doivent accéder aux VMs sans exposer directement SSH/RDP à Internet ;
- des VMs qui peuvent nécessiter des mises à jour ou des appels vers des points de terminaison publics.

L'entreprise souhaite un réseau facile à comprendre et à dépanner, sans ouvrir tous les ports ni créer des ressources inutiles.

## 25.2 Exigences imposées

Tu dois concevoir :

1. un VNet avec l'espace `10.20.0.0/16` ;
2. un sous-réseau Web ;
3. un sous-réseau App ;
4. un sous-réseau Data réservé à l'extension ;
5. une politique NSG limitant les flux aux besoins ;
6. un moyen de sortie explicite pour les VMs privées qui en ont besoin ;
7. une voie d'administration qui n'exige pas une règle SSH/RDP ouverte à Internet ;
8. une méthode pour tester et dépanner la connectivité ;
9. une procédure de nettoyage du laboratoire.

Tu dois aussi expliquer quels composants sont facultatifs, quels composants peuvent être facturables et quelles hypothèses restent à vérifier avant une mise en production.

## 25.3 Livrable attendu

Rends ton travail sous forme d'un plan structuré contenant :

- un schéma de l'architecture ;
- un tableau CIDR ;
- une matrice des flux autorisés et refusés ;
- une description de la sortie Internet ;
- une description de la voie d'administration ;
- un ordre de diagnostic en cas d'échec ;
- une checklist de validation ;
- une estimation qualitative des composants susceptibles de coûter de l'argent ;
- les étapes de suppression après le laboratoire.

## 25.4 Contraintes de sécurité

- La VM App n'a pas d'accès entrant direct depuis Internet.
- La couche App n'accepte TCP/8080 que depuis la couche Web ou des sources explicitement approuvées.
- Le sous-réseau Data n'expose pas de port de base de données à Internet.
- SSH et RDP ne sont pas autorisés à partir de toutes les sources Internet.
- Le trafic sortant est pensé explicitement, et non supposé disponible par défaut.
- Les règles doivent avoir des sources, ports et destinations justifiés.
- La configuration DNS est vérifiée lorsqu'un nom est utilisé.
- Le peering, s'il est ajouté, ne doit pas être considéré comme transitif par défaut.

## 25.5 Travail demandé

### Tâche A — Plan CIDR (15 points)

Propose les CIDR des trois sous-réseaux et prouve qu'ils appartiennent au VNet `10.20.0.0/16`, qu'ils ne se chevauchent pas et qu'ils disposent d'une taille raisonnable pour le laboratoire.

### Tâche B — Architecture (15 points)

Dessine les ressources et les chemins de communication. Indique où se trouvent les VMs Web et App, et comment l'administration se fera.

### Tâche C — NSG et matrice des flux (20 points)

Définis les flux nécessaires : HTTPS vers le frontal, TCP/8080 de Web vers App, accès App vers Data selon un port documenté, aucun SSH/RDP entrant depuis Internet et aucun accès direct Internet vers App/Data.

### Tâche D — Routage et sortie (15 points)

Explique les routes système, la différence entre une route et une règle NSG, et une méthode de sortie explicite pour les ressources privées qui doivent accéder aux endpoints publics.

### Tâche E — Administration et DNS (10 points)

Explique une voie d'administration sécurisée et l'approche DNS nécessaire pour joindre des services privés par leur nom.

### Tâche F — Diagnostic (15 points)

Une VM Web ne parvient pas à joindre App sur TCP/8080. Donne une séquence d'au moins six vérifications, dans un ordre logique.

### Tâche G — Exploitation et nettoyage (10 points)

Fournis une checklist de validation et indique comment éviter de laisser des ressources facturables après le laboratoire.


# 26. Exemple de correction du challenge final

La correction ci-dessous est un exemple cohérent. D'autres solutions peuvent obtenir la totalité des points si elles respectent les contraintes, justifient leurs choix et tiennent compte des exigences spécifiques des services Azure.

## 26.1 Plan d'adressage corrigé

| Ressource logique | CIDR | Adresses totales | Adresses réservées Azure par sous-réseau IPv4 |
|---|---|---:|---:|
| VNet | `10.20.0.0/16` | 65 536 | N/A, il s'agit de l'espace global |
| `snet-web` | `10.20.1.0/24` | 256 | 5 |
| `snet-app` | `10.20.2.0/24` | 256 | 5 |
| `snet-data` | `10.20.3.0/24` | 256 | 5 |

Les trois sous-réseaux sont compris dans `10.20.0.0/16`. Ils sont distincts et n'ont pas de chevauchement. La taille `/24` est confortable pour le laboratoire, mais une architecture réelle pourrait choisir des plages plus petites ou plus grandes en fonction de la croissance et des besoins du service.

## 26.2 Schéma corrigé

```text
                               CLIENTS
                                  |
                                  | HTTPS TCP/443
                                  v
                       [ Point d'entrée Web choisi ]
                                  |
               +------------------+-------------------+
               |              VNet                  |
               |         10.20.0.0/16               |
               |                                    |
               |  +-----------------------------+   |
               |  | snet-web 10.20.1.0/24       |   |
               |  | VM / frontal Web            |   |
               |  | nsg-web                     |   |
               |  +--------------+--------------+   |
               |                 |                  |
               |                 | TCP/8080         |
               |                 v                  |
               |  +-----------------------------+   |
               |  | snet-app 10.20.2.0/24       |   |
               |  | VM App privée               |   |
               |  | nsg-app                     |   |
               |  +--------------+--------------+   |
               |                 |                  |
               |                 | Port DB requis   |
               |                 v                  |
               |  +-----------------------------+   |
               |  | snet-data 10.20.3.0/24      |   |
               |  | Couche de données future    |   |
               |  +-----------------------------+   |
               |                                    |
               +------------------------------------+

Administration : Bastion / VPN / accès privé approuvé
Sortie des VM privées : NAT Gateway ou solution approuvée
```

Le frontal public est un point d'entrée logique. Dans une architecture de production, il faut décider s'il s'agit d'un service managé, d'un équilibreur, d'une appliance ou d'une VM, puis appliquer les contrôles adaptés. Le schéma ne signifie pas qu'il suffit de créer un sous-réseau pour obtenir un site Web public.

## 26.3 Matrice de flux corrigée

| Source | Destination | Protocole/port | Décision | Pourquoi |
|---|---|---|---|---|
| Clients autorisés | Point d'entrée Web | TCP/443 | Autoriser | Accès HTTPS |
| Internet | VM App | TCP/8080 | Refuser / ne pas exposer | Couche applicative privée |
| Sous-réseau Web | Sous-réseau App | TCP/8080 | Autoriser | Appel applicatif |
| Sous-réseau App | Sous-réseau Data | Port du moteur choisi | Autoriser au besoin | Accès aux données requis |
| Internet | Sous-réseau Data | Port de base de données | Refuser / ne pas exposer | Données privées |
| Internet | VMs internes | TCP/22, TCP/3389 | Ne pas autoriser directement | Administration via voie contrôlée |
| VM privée | Internet | Ports requis | Autoriser via la solution de sortie sélectionnée, si nécessaire | Mises à jour/API |

La règle exacte doit cibler les bons préfixes ou groupes de sécurité et la destination réelle. Un port de base de données ne peut pas être choisi sans connaître le moteur utilisé.

## 26.4 NSG corrigés

### NSG Web

- Autoriser TCP/443 vers le point d'entrée Web depuis les sources prévues.
- N'autoriser HTTP/80 que si nécessaire, par exemple pour redirection vers HTTPS ou pour une exigence clairement définie.
- Ne pas autoriser SSH/RDP depuis toutes les adresses Internet.
- Définir les flux sortants utiles pour les appels à la couche App et le fonctionnement de l'application.

### NSG App

- Autoriser TCP/8080 en entrant depuis le sous-réseau Web ou un groupe de sécurité prévu.
- Ne pas autoriser TCP/8080 depuis `Internet`.
- Autoriser le port de données en sortie uniquement vers la couche Data si nécessaire.
- Autoriser les autres flux nécessaires avec sources et destinations précises.

### Couche Data

- Garder les ressources privées.
- Autoriser le port du moteur de données uniquement depuis les sources applicatives approuvées.
- Refuser ou ne pas créer de règle permettant l'accès direct depuis Internet.
- Compléter la sécurité par les contrôles propres au service de données.

Les NSG ne remplacent ni les identités, ni les permissions sur la base de données, ni le chiffrement, ni les contrôles internes du service.

## 26.5 Routage et sortie corrigés

Les sous-réseaux d'un même VNet disposent normalement de routes système qui permettent le routage au sein du VNet. Il n'est donc pas nécessaire de créer une UDR de transit entre les sous-réseaux de ce schéma si aucun besoin particulier ne l'exige.

Les NSG restent responsables de l'autorisation des flux. La route ne remplace pas la règle de filtrage.

Pour les VMs privées qui doivent télécharger des mises à jour ou appeler des endpoints publics, le plan prévoit explicitement une sortie. Azure NAT Gateway est une option si le besoin est principalement la connectivité sortante. Si l'entreprise doit inspecter et gouverner les flux, Azure Firewall ou une autre architecture centralisée peut être préférable.

Pour les nouveaux VNets déployés depuis le 31 mars 2026, ne compte pas sur l'ancien accès sortant par défaut. La configuration de sortie doit être vérifiée et documentée.

## 26.6 Administration et DNS corrigés

Pour l'administration, on choisit Azure Bastion ou une connectivité VPN/privée approuvée. Les VMs internes n'ont pas besoin de public IP uniquement pour SSH ou RDP.

Pour DNS :

- utiliser des noms stables ;
- si des zones DNS privées sont utilisées, créer les enregistrements nécessaires ;
- lier la zone aux VNets qui doivent résoudre ces noms ;
- vérifier les réponses DNS depuis la ressource cliente ;
- pour les Private Endpoints, vérifier que le nom du service retourne l'adresse privée attendue.

## 26.7 Séquence de diagnostic corrigée

Pour l'échec Web -> App sur TCP/8080 :

1. Confirmer l'adresse privée et le sous-réseau de chaque VM.
2. Vérifier l'état des interfaces réseau et le VNet attendu.
3. Examiner la route effective de la source vers l'adresse de la VM App.
4. Vérifier le NSG du sous-réseau Web pour le flux sortant.
5. Vérifier le NSG du sous-réseau App et tout NSG de la NIC App.
6. Vérifier qu'aucune règle Deny plus prioritaire ne s'applique.
7. Sur la VM App, vérifier le pare-feu local et l'écoute TCP/8080.
8. Tester le port depuis la VM Web avec un outil adapté au système.
9. Si le test IP fonctionne mais pas le nom, diagnostiquer DNS.
10. Examiner les journaux réseau et applicatifs si nécessaire.

Une règle d'autorisation ajoutée au mauvais NSG ou avec la mauvaise priorité peut ne pas corriger le problème.

## 26.8 Checklist de validation corrigée

```text
[ ] VNet : 10.20.0.0/16
[ ] snet-web : 10.20.1.0/24
[ ] snet-app : 10.20.2.0/24
[ ] snet-data : 10.20.3.0/24 ou plage réservée documentée
[ ] Aucun chevauchement CIDR
[ ] NSG Web appliqué au bon périmètre
[ ] NSG App appliqué au bon périmètre
[ ] HTTPS uniquement là où il est requis
[ ] TCP/8080 depuis Web seulement
[ ] Aucun accès Internet direct inutile à App/Data
[ ] Sortie des VMs privées explicitement conçue
[ ] Accès administrateur via Bastion/VPN/voie approuvée
[ ] Routes effectives examinées
[ ] DNS vérifié depuis la ressource cliente
[ ] Tests des flux réels documentés
[ ] Ressources facturables identifiées
[ ] Nettoyage planifié et groupe vérifié avant suppression
```

## 26.9 Évaluation sur 100 points

| Critère | Points |
|---|---:|
| Plan CIDR correct, inclus et non chevauchant | 15 |
| Schéma clair, rôles bien séparés | 15 |
| Matrice de flux précise et moindre privilège | 20 |
| Routage et sortie explicitement compris | 15 |
| Administration et DNS expliqués correctement | 10 |
| Diagnostic structuré et complet | 15 |
| Exploitation, coûts et nettoyage | 10 |
| **Total** | **100** |

### Interprétation de la note

| Score | Niveau de maîtrise |
|---:|---|
| 90–100 | Très bonne compréhension des bases appliquées |
| 75–89 | Bon niveau, quelques détails à renforcer |
| 60–74 | Bases acquises, erreurs de conception encore possibles |
| 40–59 | Compréhension partielle, revoir routage et NSG |
| 0–39 | Reprendre les fondamentaux et refaire les exercices guidés |


# 27. Glossaire

| Terme | Définition simple |
|---|---|
| Azure | Plateforme cloud de Microsoft |
| VNet | Réseau virtuel Azure |
| CIDR | Notation qui décrit une plage réseau et la longueur de son préfixe |
| Sous-réseau | Portion d'un espace d'adressage de VNet |
| NIC | Interface réseau, notamment attachée à une VM |
| IP privée | Adresse destinée à la communication privée et aux réseaux connectés |
| IP publique | Adresse utilisable pour un point d'accès public, selon le service et les règles |
| Route | Instruction indiquant le chemin vers une destination |
| UDR | User Defined Route, ou route personnalisée |
| NSG | Network Security Group, règles de filtrage réseau Azure |
| ASG | Application Security Group, regroupement logique d'interfaces pour les règles compatibles |
| NAT | Traduction d'adresses réseau |
| NAT Gateway | Service managé de connectivité sortante pour les sous-réseaux associés |
| Bastion | Service managé d'accès administratif à des VMs sans IP publique sur ces VMs dans les scénarios pris en charge |
| DNS | Système de résolution de noms en adresses IP |
| Private DNS zone | Zone DNS privée gérée dans Azure |
| Peering | Connexion privée entre deux VNets, sans transit automatique entre peerings séparés |
| Service Endpoint | Fonctionnalité qui étend l'identité d'un sous-réseau vers certains services Azure pris en charge |
| Private Endpoint | Interface réseau à IP privée donnant accès à un service via Azure Private Link |
| Azure Firewall | Service de pare-feu réseau managé pour des scénarios de filtrage et d'inspection |
| Network Watcher | Ensemble d'outils de supervision et de diagnostic réseau Azure |
| Moindre privilège | N'autoriser que les accès nécessaires au besoin |
| Egress | Trafic sortant d'un environnement ou d'une ressource |
| Ingress | Trafic entrant vers une ressource |
| Haute disponibilité | Conception qui vise à maintenir un service malgré certaines pannes |


# 28. Références officielles Microsoft Learn

Les services cloud évoluent. Pour une utilisation réelle, les guides officiels suivants doivent être consultés avant de figer un design. Les liens font partie de ce même cours : il n'est pas nécessaire de télécharger un document complémentaire.

1. **Vue d'ensemble des réseaux virtuels Azure**  
   https://learn.microsoft.com/en-us/azure/virtual-network/network-overview

2. **Routage du trafic dans les réseaux virtuels Azure**  
   https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview

3. **Fonctionnement des Network Security Groups**  
   https://learn.microsoft.com/en-us/azure/virtual-network/network-security-group-how-it-works

4. **Dépannage des NSG qui bloquent le trafic**  
   https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-network/virtual-network-troubleshoot-nsg-blocking-traffic

5. **Vue d'ensemble d'Azure NAT Gateway**  
   https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview

6. **FAQ Azure NAT Gateway**  
   https://learn.microsoft.com/en-us/azure/nat-gateway/faq

7. **Vue d'ensemble d'Azure Bastion**  
   https://learn.microsoft.com/en-us/azure/bastion/bastion-overview

8. **Résolution de noms dans les réseaux virtuels Azure**  
   https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-name-resolution-for-vms-and-role-instances

9. **Vue d'ensemble des Private Endpoints**  
   https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview/

10. **Créer un réseau virtuel Azure**  
    https://learn.microsoft.com/en-us/azure/virtual-network/quick-create-portal

11. **Documentation Azure CLI**  
    https://learn.microsoft.com/en-us/cli/azure/

Les fonctionnalités disponibles, les exigences de taille de sous-réseau, les SKU et les tarifs peuvent varier ou évoluer. Pour un environnement de production, vérifie les prérequis dans la documentation en vigueur, puis valide la configuration et le coût avant le déploiement.


# 29. Bilan de fin de cours

Tu as étudié les composants essentiels d'un réseau virtuel Azure : VNet, sous-réseaux, adressage CIDR, IP privées et publiques, routes, NSG, DNS, peering, NAT Gateway, Bastion et Private Endpoints.

Le modèle mental à retenir est le suivant :

```text
ADRESSAGE
   |
   v
ROUTAGE : où le paquet peut-il aller ?
   |
   v
FILTRAGE : le flux est-il autorisé ?
   |
   v
DNS : le nom mène-t-il à la bonne adresse ?
   |
   v
SERVICE : un programme écoute-t-il sur le port attendu ?
   |
   v
VALIDATION : le flux réel fonctionne-t-il dans les deux sens requis ?
```

Une architecture réseau bien conçue ne consiste pas à ouvrir tous les ports jusqu'à ce que cela fonctionne. Elle consiste à établir un plan d'adressage clair, à prévoir les chemins, à limiter les communications au nécessaire, puis à valider chaque couche avec méthode.

**Fin du cours `azure-vnet-debutant.md` — le challenge et son corrigé sont intégrés dans ce même fichier.**
