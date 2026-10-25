# Réseau avancé sous Linux : VLAN, Bonds, Bridges

## 1. Présentation du cours

### Objectif général

Maîtriser la conception, la configuration, la sécurisation, l'automatisation et le dépannage d'architectures réseau avancées sous Linux, notamment dans les environnements de virtualisation, de serveurs, de datacenters et d'infrastructures d'entreprise.

Ce cours approfondit trois mécanismes essentiels du réseau Linux :

- **VLAN** : segmentation logique des réseaux Ethernet.
- **Bonding** : agrégation de plusieurs interfaces physiques pour améliorer la disponibilité et, selon le mode, répartir le trafic.
- **Bridge** : commutation Ethernet logicielle entre interfaces physiques, interfaces virtuelles et réseaux de machines virtuelles.

Ces mécanismes peuvent être utilisés séparément ou combinés. Leur association demande cependant de respecter la hiérarchie des interfaces, les propriétés de chaque couche et la configuration des équipements réseau en amont.

### Prérequis

Il est recommandé de maîtriser :

- les adresses IPv4 et IPv6, les masques et les routes ;
- les adresses MAC, ARP, NDP et le fonctionnement d'Ethernet ;
- les commandes `ip`, `ping`, `ss`, `tcpdump` et `ip route` ;
- les bases de `nftables` ;
- les principes d'administration système Linux ;
- les services réseau et la gestion persistante des interfaces.

### Environnements concernés

Les exemples sont conçus pour Linux avec les outils `iproute2`, `bridge` et, lorsque cela est pertinent, NetworkManager avec `nmcli`.

Ils peuvent être adaptés à Debian, Ubuntu, Rocky Linux, AlmaLinux et aux distributions compatibles, sous réserve des versions disponibles et de leur gestionnaire réseau.

**Important :** les commandes `ip` et `bridge` modifient généralement l'état réseau en mémoire. Elles ne garantissent pas, à elles seules, une configuration persistante après redémarrage.

Les commandes de configuration sont à exécuter en laboratoire ou dans une fenêtre de maintenance. Sur un serveur distant, une erreur sur le bond, le bridge, le VLAN ou la route par défaut peut couper la connexion SSH.


## 2. Architecture générale du réseau Linux

### 2.1 Les trois mécanismes fondamentaux

#### VLAN : séparation logique

Un VLAN crée un domaine de diffusion Ethernet distinct. Plusieurs VLAN peuvent transporter leur trafic sur un même lien physique grâce à l'encapsulation IEEE 802.1Q.

#### Bond : agrégation de liens

Un bond Linux, généralement nommé `bond0`, regroupe plusieurs interfaces physiques. Selon son mode, il fournit une tolérance à la panne, une répartition de charge ou les deux.

#### Bridge : commutation de niveau 2

Un bridge Linux, souvent nommé `br0`, agit comme un commutateur Ethernet logiciel. Il apprend les adresses MAC et transmet les trames entre ses ports.

### 2.2 Schéma global des responsabilités

```text
                     COUCHES DU RÉSEAU LINUX

+---------------------------------------------------------+
| Couche 3 : routage IP                                   |
| Adresses IP, routes, passerelles, politique de routage  |
+---------------------------------------------------------+
                           |
+---------------------------------------------------------+
| Interfaces logiques                                     |
| VLAN : bond0.10, br0.20, enp1s0.30                     |
| Interfaces virtuelles, interfaces de gestion            |
+---------------------------------------------------------+
                           |
+---------------------------------------------------------+
| Couche 2 : commutation Ethernet                         |
| Bridge : br0                                            |
| Filtrage VLAN, table MAC, STP, multicast                |
+---------------------------------------------------------+
                           |
+---------------------------------------------------------+
| Agrégation de liens                                     |
| Bond : bond0                                            |
| active-backup, 802.3ad, balance-xor, etc.               |
+---------------------------------------------------------+
                           |
+---------------------------------------------------------+
| Interfaces physiques                                   |
| enp1s0, enp2s0, ens3, ens4                              |
+---------------------------------------------------------+
                           |
+---------------------------------------------------------+
| Switch physique / infrastructure réseau                |
+---------------------------------------------------------+
```

Ce schéma illustre une architecture possible, pas une hiérarchie obligatoire dans tous les cas. Un VLAN peut être placé directement sur une interface physique, sur un bond ou sur un bridge, selon le besoin.

### 2.3 Règle fondamentale : distinguer les rôles

Ne confondez pas :

- une interface physique avec une interface logique ;
- un bond avec un bridge ;
- un VLAN créé par une interface VLAN avec un VLAN filtré par un bridge ;
- une interface qui transporte des trames avec une interface qui porte une adresse IP ;
- une agrégation active-active avec une véritable répartition du trafic sur tous les flux.

Un même paquet peut traverser plusieurs de ces mécanismes. Le dépannage doit donc déterminer à quelle étape il est perdu.


## 3. Les VLAN en profondeur

### 3.1 Rappel sur IEEE 802.1Q

Un VLAN est identifié par un numéro appelé VID, ou VLAN ID.

La plage des identifiants utilisables dans les configurations Ethernet classiques est généralement de 1 à 4094. Les identifiants 0 et 4095 ont des significations particulières et ne constituent pas des VLAN ordinaires à attribuer comme les autres.

Exemple de plan VLAN :

| VLAN | Fonction | Sous-réseau |
|---|---|---|
| 10 | Administration | `192.0.2.0/24` |
| 20 | Serveurs applicatifs | `198.51.100.0/24` |
| 30 | Stockage | `203.0.113.0/24` |
| 99 | Gestion réseau | `10.99.0.0/24` |

Les plages de documentation utilisées ici servent d'exemples. Elles ne sont pas destinées à représenter des adresses publiques réellement attribuées à une entreprise.

### 3.2 Ports access et trunk

Un port access est généralement associé à un seul VLAN non marqué pour les équipements terminaux.

Un port trunk transporte plusieurs VLAN, habituellement avec des balises 802.1Q.

```text
                  SWITCH PHYSIQUE
              +----------------------+
PC admin -----| Port access VLAN 10   |
              |                      |
Serveur ----- | Port access VLAN 20  |
              |                      |
              | Port trunk 10,20,30  |==========+
              +----------------------+          |
                                                |
                                       +----------------+
                                       | Serveur Linux  |
                                       | bond0 / bridge |
                                       +----------------+
```

Le serveur doit recevoir le type de trafic attendu par la configuration du switch. Si le switch envoie des trames non marquées alors que Linux attend des trames marquées, ou inversement, la connectivité peut échouer.

### 3.3 VLAN sur une interface physique

Supposons que l'interface `enp1s0` soit reliée à un trunk transportant le VLAN 10.

Créer le VLAN :

```bash
sudo ip link add link enp1s0 name enp1s0.10 type vlan id 10
sudo ip link set enp1s0 up
sudo ip link set enp1s0.10 up
sudo ip addr add 192.0.2.10/24 dev enp1s0.10
```

Vérifier :

```bash
ip -d link show enp1s0.10
ip -br addr show enp1s0
ip -br addr show enp1s0.10
ip route
```

Le nom `enp1s0.10` est une convention. Le VID réel est celui déclaré dans la commande.

Le tag 802.1Q est géré par le noyau et peut également être traité en partie par le matériel réseau lorsque l'offload est activé. Une capture réseau peut donc présenter des différences selon le point de capture et les capacités de la carte.

### 3.4 VLAN sur un bond

Un bond peut transporter plusieurs VLAN :

```text
          Switch avec trunk VLAN 10,20,30
                       |
               +----------------+
               |     bond0      |
               +----------------+
                  |     |     |
                enp1s0 enp2s0 ...
                  |
          +-------+-------+
          |       |       |
       bond0.10 bond0.20 bond0.30
```

Exemple :

```bash
sudo ip link add bond0 type bond mode active-backup
sudo ip link set enp1s0 down
sudo ip link set enp2s0 down

sudo ip link set enp1s0 master bond0
sudo ip link set enp2s0 master bond0

sudo ip link set enp1s0 up
sudo ip link set enp2s0 up
sudo ip link set bond0 up

sudo ip link add link bond0 name bond0.10 type vlan id 10
sudo ip link add link bond0 name bond0.20 type vlan id 20

sudo ip link set bond0.10 up
sudo ip link set bond0.20 up

sudo ip addr add 192.0.2.10/24 dev bond0.10
sudo ip addr add 198.51.100.10/24 dev bond0.20
```

Cet exemple est destiné à un environnement contrôlé. Sur une machine déjà configurée, ne rattachez pas aveuglément des interfaces à un nouveau bond : vérifiez d'abord leurs connexions existantes et leur état.

Pour les VLAN créés au-dessus d'un bond, il est préférable de créer le bond, de lui attacher ses interfaces physiques, puis de créer les interfaces VLAN. Cela évite notamment certains problèmes d'adresse MAC liés à la création prématurée des interfaces VLAN.

### 3.5 Vérifier le trafic VLAN

```bash
ip -d link show bond0
ip -d link show bond0.10
ip -s link show bond0
```

Capturer le trafic :

```bash
sudo tcpdump -eni bond0
sudo tcpdump -eni bond0.10
```

Le comportement de l'affichage des tags dépend de l'interface de capture et des mécanismes d'offload. L'absence apparente d'une balise dans une capture ne prouve donc pas, à elle seule, que le réseau n'utilise pas de VLAN.

### 3.6 MTU et VLAN

Une balise 802.1Q ajoute généralement quatre octets à la trame Ethernet. Les équipements réseau doivent prendre en charge la taille de trame nécessaire.

Sur un chemin où la MTU IP standard est de 1500 octets, les équipements Ethernet doivent accepter la trame correspondante avec son encapsulation. Les interfaces VLAN Linux gèrent normalement l'encapsulation, mais le switch, les NIC, les bridges et les équipements intermédiaires doivent être compatibles avec le trafic réel.

Vérifier :

```bash
ip link show
ip -d link show
```

Ne modifiez pas la MTU de toutes les interfaces sans vérifier la MTU de bout en bout.


## 4. Le bonding Linux en profondeur

### 4.1 Pourquoi créer un bond ?

Le bonding permet de regrouper plusieurs interfaces physiques sous une interface logique.

Ses objectifs possibles sont :

- maintenir la connectivité lorsqu'un lien tombe ;
- répartir certains flux sur plusieurs liens ;
- fournir un point d'attachement logique stable ;
- transporter plusieurs VLAN au-dessus d'un lien agrégé ;
- intégrer une architecture de virtualisation ou de stockage.

Le bonding n'augmente pas automatiquement le débit d'une connexion TCP unique. Le résultat dépend du mode, de la configuration du switch et de la distribution des flux.

### 4.2 Modes de bonding

| Mode | Nom | Caractéristique principale |
|---|---|---|
| 0 | `balance-rr` | Répartition round-robin |
| 1 | `active-backup` | Un lien actif, les autres en secours |
| 2 | `balance-xor` | Répartition selon un algorithme de hachage |
| 3 | `broadcast` | Transmission sur tous les liens |
| 4 | `802.3ad` | Agrégation LACP |
| 5 | `balance-tlb` | Répartition de charge en émission |
| 6 | `balance-alb` | Adaptation de la charge en émission et certains mécanismes en réception |

Le mode 1 est généralement adapté à la redondance simple. Le mode 4 est adapté à une agrégation LACP correctement configurée sur les équipements en face.

Les modes 0, 2, 3, 5 et 6 ont des conditions d'utilisation spécifiques. Ne les sélectionnez pas uniquement parce qu'ils portent le mot « balance ».

### 4.3 Mode active-backup

```text
             +------------------+
             |       bond0      |
             +------------------+
                 |          |
            +---------+ +---------+
            | enp1s0  | | enp2s0  |
            | ACTIF   | | SECOURS |
            +---------+ +---------+
                 |          |
                 +-----+----+
                       |
                Infrastructure
```

Une seule interface transmet normalement le trafic à un instant donné. Si le lien actif est détecté comme défaillant, un autre lien peut prendre le relais.

Cette architecture est simple, mais la détection de panne doit être adaptée. Un lien peut rester physiquement actif alors que le chemin réseau au-delà du switch est indisponible.

### 4.4 Mode 802.3ad / LACP

LACP permet de négocier une agrégation de liens entre équipements compatibles.

```text
                 Serveur Linux
              +----------------+
              |     bond0      |
              | mode 802.3ad    |
              +----------------+
                  |        |
              enp1s0    enp2s0
                  |        |
                  +---+----+
                      |
             +-------------------+
             | Switch compatible |
             |     LACP / LAG    |
             +-------------------+
```

Points à vérifier :

- les ports du switch appartiennent au même groupe d'agrégation ;
- la configuration du switch autorise les VLAN attendus ;
- les paramètres de vitesse et de duplex sont compatibles ;
- le mode LACP est configuré sur les deux extrémités ;
- le hachage de trafic correspond aux besoins ;
- le nombre de liens réellement actifs est cohérent avec l'attendu.

Le LACP ne transforme pas nécessairement deux liens de 1 Gbit/s en une connexion TCP unique de 2 Gbit/s. Plusieurs flux peuvent être répartis entre les liens selon l'algorithme de hachage. Un même flux est généralement conservé sur un lien pour éviter le désordre des paquets.

### 4.5 Créer un bond temporaire avec active-backup

Sur une machine de laboratoire dont les interfaces sont disponibles :

```bash
sudo modprobe bonding

sudo ip link add bond0 type bond mode active-backup
sudo ip link set enp1s0 down
sudo ip link set enp2s0 down

sudo ip link set enp1s0 master bond0
sudo ip link set enp2s0 master bond0

sudo ip link set enp1s0 up
sudo ip link set enp2s0 up
sudo ip link set bond0 up
```

Consulter les informations :

```bash
cat /proc/net/bonding/bond0
ip -d link show bond0
ip -s link show bond0
```

Le fichier `/proc/net/bonding/bond0` fournit notamment le mode, l'état du lien, l'interface active et les paramètres du bond.

### 4.6 Surveiller les pannes

La surveillance de lien peut utiliser des informations de porteuse ou des mécanismes de contrôle réseau selon le mode et les paramètres disponibles.

Exemple de paramètre :

```bash
sudo ip link set bond0 type bond miimon 100
```

`miimon 100` configure une surveillance périodique de l'état du lien en millisecondes. La commande exacte et les options disponibles dépendent du noyau et du pilote.

Cette surveillance détecte principalement les changements de lien. Elle ne garantit pas que la passerelle, le switch distant ou l'application restent accessibles.

Les mécanismes ARP de surveillance sont disponibles dans certaines configurations de bonding, mais doivent être réglés avec soin pour éviter les fausses détections et les comportements instables.

### 4.7 Choisir le bon mode

- **Active-backup** : privilégier la simplicité et la tolérance à la panne.
- **802.3ad** : utiliser lorsqu'un LAG LACP est prévu et correctement configuré sur les switches.
- **Balance-xor** : envisager seulement si l'algorithme et les équipements sont compatibles.
- **Balance-rr** : éviter de le choisir sans analyse des conséquences sur le réordonnancement et le comportement du réseau.

Avant un déploiement, tester la perte d'un lien, la restauration du lien, les flux établis, les VLAN transportés et les compteurs d'erreurs.


## 5. Les bridges Linux en profondeur

### 5.1 Fonctionnement

Un bridge Linux est un commutateur Ethernet logiciel.

Il relie des ports et apprend les associations entre adresses MAC et ports. Il peut transférer des trames entre interfaces physiques, interfaces virtuelles de machines virtuelles ou autres interfaces compatibles.

```text
                  +--------------------+
                  |       br0          |
                  | Bridge Linux       |
                  +--------------------+
                     |      |      |
                     |      |      |
                  enp1s0   veth0   tap0
                     |      |      |
                  Réseau   Cont.   Machine
                  physique        virtuelle
```

Le bridge traite le trafic au niveau 2. Il ne devient pas automatiquement un routeur IP.

### 5.2 Créer un bridge simple

Dans un laboratoire :

```bash
sudo ip link add br0 type bridge
sudo ip link set br0 up
```

Ajouter un port :

```bash
sudo ip link set enp1s0 down
sudo ip link set enp1s0 master br0
sudo ip link set enp1s0 up
```

Si l'hôte doit porter une adresse IP sur le réseau relié au bridge, cette adresse est normalement placée sur le bridge plutôt que sur le port physique qui lui est attaché.

Exemple de laboratoire :

```bash
sudo ip addr flush dev enp1s0
sudo ip addr add 192.0.2.10/24 dev br0
sudo ip link set br0 up
```

**Attention :** `ip addr flush` supprime les adresses présentes sur l'interface ciblée. N'utilisez pas cette commande sur une interface de production sans vérifier les conséquences.

Vérifier :

```bash
ip -br addr
bridge link
bridge fdb show br br0
```

### 5.3 Pourquoi placer l'adresse IP sur le bridge ?

Lorsqu'une interface physique est un port du bridge, le bridge représente le point logique d'accès au réseau de niveau 2.

```text
AVANT

enp1s0
  |
Adresse IP de l'hôte
  |
Réseau


APRÈS

Réseau
  |
enp1s0 (port du bridge, sans IP de gestion)
  |
br0 (adresse IP de l'hôte)
  |
Pile IP Linux
```

Cette organisation est courante sur les hyperviseurs et les serveurs qui doivent communiquer sur le même réseau Ethernet que leurs machines virtuelles.

Elle ne signifie pas que toutes les interfaces membres d'un bridge doivent obligatoirement être dépourvues de toute configuration IP dans tous les scénarios possibles. Elle décrit le modèle standard de l'hôte qui utilise le bridge comme interface de niveau 3.

### 5.4 Table de transfert MAC

Le bridge apprend les adresses MAC à partir des trames reçues et construit une base de transfert.

```text
Exemple simplifié de table FDB

+-------------------+---------+-------+
| Adresse MAC       | Port    | VLAN  |
+-------------------+---------+-------+
| 02:00:00:00:00:10 | enp1s0  | 10    |
| 02:00:00:00:00:20 | tap0    | 20    |
| 02:00:00:00:00:30 | veth0   | 10    |
+-------------------+---------+-------+
```

Cette table est illustrative. Les entrées réelles dépendent du trafic observé et des fonctionnalités activées.

Afficher les entrées :

```bash
bridge fdb show
bridge fdb show br br0
```

Une entrée MAC absente ne prouve pas nécessairement un défaut : le bridge peut ne pas avoir encore appris l'adresse ou l'entrée peut avoir expiré.

### 5.5 STP et boucles Ethernet

Un bridge connecté à plusieurs chemins de niveau 2 peut participer à une boucle Ethernet.

Les boucles peuvent provoquer des tempêtes de broadcast, des changements incessants dans les tables MAC et une dégradation importante du réseau.

Le Spanning Tree Protocol permet de gérer certains chemins redondants en bloquant les chemins qui créeraient des boucles.

Pour afficher les informations du bridge :

```bash
ip -d link show br0
bridge link show
bridge -d link show
```

Dans un environnement comportant plusieurs chemins de niveau 2, vérifiez la configuration STP et celle des équipements physiques. Ne désactivez pas STP uniquement pour faire disparaître un symptôme.


## 6. Bridge VLAN-aware : une architecture avancée

### 6.1 Deux méthodes différentes de transport des VLAN

Il faut distinguer deux approches.

**Approche A : interfaces VLAN séparées**

```text
bond0
  |
  +-- bond0.10
  |
  +-- bond0.20
  |
  +-- bond0.30
```

Cette approche crée une interface Linux distincte pour chaque VLAN.

**Approche B : bridge avec filtrage VLAN**

```text
                +---------------------+
                |   br-trunk          |
                | VLAN filtering      |
                +---------------------+
                    |             |
                 bond0           tap0
                    |             |
              Trunk physique   VM / vNIC
```

Le bridge peut gérer l'appartenance VLAN de ses ports et filtrer les trames en fonction du VID.

Ces méthodes ne sont pas interchangeables sans réfléchir à la topologie. Un bridge VLAN-aware est particulièrement utile pour les hyperviseurs qui doivent transporter plusieurs VLAN vers plusieurs machines virtuelles.

### 6.2 Architecture d'un hyperviseur

```text
                         SWITCH
                     Trunk VLAN 10,20,30
                             |
                       +-----------+
                       |   bond0   |
                       +-----------+
                             |
                       +-----------+
                       |    br0    |
                       | VLAN-aware|
                       +-----------+
                        /    |    \
                       /     |     \
                    tap10   tap20  tap30
                      |       |      |
                    VM-A    VM-B   VM-C

                  VLAN 10  VLAN 20 VLAN 30
```

Dans cette architecture, les machines virtuelles peuvent être raccordées à un bridge commun, tandis que les VLAN autorisés déterminent le trafic qu'elles peuvent émettre et recevoir.

Il faut également configurer les interfaces virtuelles et les paramètres des machines virtuelles. Le bridge ne configure pas automatiquement l'adresse IP du système invité.

### 6.3 Créer un bridge VLAN-aware en laboratoire

Prérequis : une interface physique ou un bond disponible, et un trunk physique configuré pour les VLAN concernés.

Exemple :

```bash
sudo ip link add br0 type bridge vlan_filtering 1 vlan_default_pvid 0
sudo ip link set br0 up

sudo ip link set bond0 master br0
sudo ip link set bond0 up

sudo bridge vlan add dev bond0 vid 10
sudo bridge vlan add dev bond0 vid 20
sudo bridge vlan add dev bond0 vid 30

sudo bridge vlan add dev br0 vid 10 self
sudo bridge vlan add dev br0 vid 20 self
sudo bridge vlan add dev br0 vid 30 self
```

Dans cet exemple :

- `vlan_filtering 1` active le filtrage VLAN du bridge ;
- `vlan_default_pvid 0` évite d'attribuer automatiquement un PVID ordinaire aux trames non marquées ;
- `bridge vlan add dev bond0 vid ...` autorise les VLAN indiqués sur le port `bond0` ;
- les entrées `self` concernent le bridge lui-même, lorsqu'il doit participer à ces VLAN.

Les règles du bridge doivent être cohérentes avec le switch physique. Le fait d'autoriser un VID sur Linux ne le rend pas automatiquement autorisé sur le switch.

Vérifier :

```bash
bridge vlan show
bridge link show
bridge -d link show
ip -d link show br0
```

### 6.4 Configurer les interfaces VLAN de l'hôte sur le bridge

Supposons que l'hôte doit avoir une adresse de gestion dans le VLAN 10 et une interface de service dans le VLAN 20.

Créer les interfaces VLAN sur le bridge :

```bash
sudo ip link add link br0 name br0.10 type vlan id 10
sudo ip link add link br0 name br0.20 type vlan id 20

sudo ip link set br0.10 up
sudo ip link set br0.20 up

sudo ip addr add 192.0.2.10/24 dev br0.10
sudo ip addr add 198.51.100.10/24 dev br0.20
```

Le bridge doit être membre des VLAN correspondants pour traiter le trafic local destiné à la pile réseau de l'hôte.

Afficher la configuration :

```bash
ip -d link show br0.10
ip -d link show br0.20
ip -br addr
bridge vlan show
ip route
```

Ne donnez pas la même adresse IP à `bond0`, `br0`, `br0.10` et `br0.20`. Chaque interface de niveau 3 doit être configurée selon le rôle réseau qui lui est attribué.

### 6.5 Ports access et trunk sur un bridge VLAN-aware

Pour qu'un port du bridge soit un port access du VLAN 20, il faut généralement définir son PVID et le comportement de sortie non marquée.

Exemple avec une interface virtuelle de test `tap20` :

```bash
sudo bridge vlan add dev tap20 vid 20 pvid untagged
```

Pour un port trunk autorisant plusieurs VLAN :

```bash
sudo bridge vlan add dev tap-trunk vid 10
sudo bridge vlan add dev tap-trunk vid 20
sudo bridge vlan add dev tap-trunk vid 30
```

Le port trunk doit exister et être attaché au bridge avant l'ajout de ses entrées VLAN.

Vérifier :

```bash
bridge vlan show
```

Un port trunk et un port access ne doivent pas être configurés de manière identique. Le PVID détermine le VLAN attribué aux trames entrantes non marquées. Le drapeau `untagged` indique que les trames sortantes de ce VLAN sont envoyées sans balise sur ce port.

### 6.6 VLAN natif et PVID

Les équipements peuvent traiter les trames non marquées de différentes façons selon leur configuration. Le VLAN natif d'un trunk physique et le PVID du port Linux doivent être cohérents.

Un décalage entre ces paramètres peut entraîner :

- une perte de connectivité ;
- l'arrivée de trames dans le mauvais VLAN ;
- des fuites de trafic entre segments mal configurés ;
- une exposition involontaire de services de gestion.

En production, il est souvent préférable de limiter les VLAN autorisés et de traiter explicitement les trames non marquées plutôt que de laisser une configuration implicite.


## 7. Combiner VLAN, Bond et Bridge

### 7.1 Architecture de référence

Pour un serveur de virtualisation avec deux interfaces physiques :

```text
                 SWITCH A / SWITCH B
                    LAG LACP
                  /           \
             enp1s0           enp2s0
                  \           /
                   +---------+
                   |  bond0  |
                   | 802.3ad |
                   +---------+
                        |
                   +---------+
                   |   br0   |
                   | VLAN    |
                   | filtering
                   +---------+
                    /   |   \
                   /    |    \
                 VM1   VM2   VM3
                  |     |     |
               VLAN10 VLAN20 VLAN30

              Interfaces VLAN de l'hôte :
                    br0.10
                    br0.20
```

Cette architecture convient si :

- les deux interfaces sont prises en charge par le bonding ;
- les équipements physiques forment un groupe LACP valide ;
- le groupe de ports transporte les VLAN attendus ;
- le bridge autorise les VLAN nécessaires ;
- les interfaces des machines virtuelles sont raccordées aux bons ports et VLAN.

Attention : si les liens arrivent sur deux switches distincts, ceux-ci doivent prendre en charge une technologie d'agrégation multi-châssis compatible, ou la conception doit utiliser un mode de redondance approprié. Deux switches indépendants ne peuvent pas simplement être traités comme un unique partenaire LACP.

### 7.2 Ordre logique de création

Pour cette architecture, l'ordre de création est important :

1. vérifier les interfaces physiques et leurs paramètres ;
2. créer le bond ;
3. rattacher les interfaces physiques au bond ;
4. vérifier l'état du bond ;
5. créer le bridge ;
6. rattacher le bond au bridge ;
7. activer le filtrage VLAN et configurer les VLAN ;
8. créer les interfaces VLAN de l'hôte si nécessaire ;
9. raccorder les interfaces virtuelles ;
10. valider le trafic, les routes et les règles de sécurité.

Cet ordre n'est pas une obligation universelle pour toutes les technologies réseau, mais il réduit les risques de dépendances incorrectes dans cette architecture.

### 7.3 Qui porte l'adresse IP ?

Dans une architecture où `bond0` est un port de `br0` :

- le bond sert à transporter les trames ;
- le bridge assure la commutation Ethernet ;
- les interfaces `br0.10` et `br0.20` peuvent porter les adresses IP de l'hôte ;
- les interfaces virtuelles ont leurs propres configurations selon les machines virtuelles.

Il faut éviter de placer une adresse de gestion sur un port physique devenu membre du bridge lorsque la pile IP doit utiliser le bridge.

### 7.4 Vérifications de cohérence

```bash
ip -br link
ip -br addr
ip route
ip -d link show bond0
ip -d link show br0
cat /proc/net/bonding/bond0
bridge link show
bridge vlan show
bridge fdb show
```

La configuration est cohérente si :

- le bond possède les interfaces physiques attendues ;
- le bond est actif et ses liens sont dans l'état prévu ;
- le bridge contient le bond et les ports virtuels attendus ;
- les VLAN sont autorisés sur les bons ports ;
- les interfaces de niveau 3 portent les bonnes adresses ;
- les routes correspondent aux réseaux réellement accessibles ;
- les équipements physiques acceptent les mêmes VLAN.


## 8. Configurer un bridge et un bond avec NetworkManager

Les commandes `ip` et `bridge` servent principalement à modifier et inspecter l'état courant. Pour une configuration persistante sur un système géré par NetworkManager, il est préférable d'utiliser des profils de connexion NetworkManager.

Les propriétés et leur disponibilité varient selon la version installée.

### 8.1 Créer un bond active-backup

Exemple de profils :

```bash
sudo nmcli connection add type bond \
  con-name bond0 \
  ifname bond0 \
  bond.options "mode=active-backup,miimon=100" \
  ipv4.method disabled \
  ipv6.method disabled
```

Créer les profils Ethernet membres :

```bash
sudo nmcli connection add type ethernet \
  con-name bond0-enp1s0 \
  ifname enp1s0 \
  controller bond0 \
  port-type bond

sudo nmcli connection add type ethernet \
  con-name bond0-enp2s0 \
  ifname enp2s0 \
  controller bond0 \
  port-type bond
```

Certaines versions de NetworkManager utilisent encore les propriétés historiques `master` et `slave-type` dans leurs exemples ou acceptent les anciens alias. Vérifiez les options prises en charge par votre version avec `nmcli connection add help` et la documentation locale.

### 8.2 Créer un bridge

```bash
sudo nmcli connection add type bridge \
  con-name br0 \
  ifname br0 \
  ipv4.method disabled \
  ipv6.method disabled
```

Rattacher le bond au bridge :

```bash
sudo nmcli connection add type ethernet \
  con-name br0-bond0 \
  ifname bond0 \
  controller br0 \
  port-type bridge
```

Cette configuration place le bond comme port du bridge. L'adresse IP de l'hôte sera ajoutée au bridge lui-même ou à une interface VLAN du bridge, selon l'architecture.

### 8.3 Ajouter un VLAN à l'hôte

Pour créer un VLAN 10 sur le bridge :

```bash
sudo nmcli connection add type vlan \
  con-name br0.10 \
  ifname br0.10 \
  dev br0 \
  id 10 \
  ipv4.method manual \
  ipv4.addresses 192.0.2.10/24 \
  ipv6.method disabled
```

Activer les profils selon l'ordre et les dépendances de la version NetworkManager :

```bash
nmcli connection show
nmcli device status
```

Puis, lors d'une fenêtre de maintenance :

```bash
sudo nmcli connection up bond0
sudo nmcli connection up bond0-enp1s0
sudo nmcli connection up bond0-enp2s0
sudo nmcli connection up br0
sudo nmcli connection up br0-bond0
sudo nmcli connection up br0.10
```

La commande d'activation d'un profil peut réactiver des dépendances ou interrompre une connexion existante. Il faut valider la séquence dans un environnement de test.

### 8.4 Vérifier les profils

```bash
nmcli connection show
nmcli device status
nmcli -f GENERAL,IP4,IP6 device show br0
nmcli -f connection,bond,bridge,vlan connection show
```

Les champs affichables dépendent des versions et des types de profils. Pour afficher toutes les propriétés d'un profil :

```bash
nmcli connection show br0
```

Ne confondez pas le nom d'un profil NetworkManager avec le nom de l'interface Linux qu'il configure.


## 9. Persistance avec systemd-networkd

`systemd-networkd` constitue une autre solution de gestion réseau. Il est possible de déclarer les interfaces virtuelles dans des fichiers `.netdev`, puis leur configuration dans des fichiers `.network`.

Ne faites pas gérer la même interface simultanément par NetworkManager et `systemd-networkd` sans architecture explicitement conçue pour cela.

### 9.1 Exemple de bond

Fichier `/etc/systemd/network/10-bond0.netdev` :

```ini
[NetDev]
Name=bond0
Kind=bond

[Bond]
Mode=active-backup
MIIMonitorSec=100ms
```

Fichier `/etc/systemd/network/20-enp1s0.network` :

```ini
[Match]
Name=enp1s0

[Network]
Bond=bond0
```

Fichier `/etc/systemd/network/20-enp2s0.network` :

```ini
[Match]
Name=enp2s0

[Network]
Bond=bond0
```

### 9.2 Exemple de bridge

Fichier `/etc/systemd/network/30-br0.netdev` :

```ini
[NetDev]
Name=br0
Kind=bridge

[Bridge]
VLANFiltering=yes
DefaultPVID=0
STP=yes
```

Fichier `/etc/systemd/network/30-bond0.network` :

```ini
[Match]
Name=bond0

[Network]
Bridge=br0
```

La syntaxe exacte des paramètres dépend de la version de systemd. Vérifiez la documentation de la version installée, notamment les sections `systemd.netdev` et `systemd.network`.

### 9.3 Ajouter les VLAN au bridge

Les entrées de configuration des VLAN de bridge doivent être déclarées sur les ports concernés, selon le modèle de votre version de systemd.

Exemple de principe pour un port trunk :

```ini
[Match]
Name=bond0

[Network]
Bridge=br0

[BridgeVLAN]
VLAN=10-30
```

Pour une interface de l'hôte qui doit participer au VLAN 10, la création d'une interface VLAN et sa configuration IP doivent également être déclarées.

**Ne recopiez pas une configuration persistante directement sur un serveur distant sans plan de retour arrière.** Les fichiers `.network` et `.netdev` sont lus selon des règles de correspondance et d'ordre. Une correspondance trop large peut modifier d'autres interfaces que celles visées.


## 10. MTU, performances et offloads

### 10.1 Comprendre la MTU

La MTU IP représente la taille maximale d'un paquet IP pouvant être transporté sur une interface sans fragmentation au niveau IP, dans le cas classique.

Les interfaces Ethernet peuvent transporter des trames dont la taille dépasse la MTU IP de 1500 octets, notamment lorsque les encapsulations et les options matérielles le permettent.

Une configuration jumbo frame, par exemple une MTU de 9000, doit être cohérente de bout en bout :

- carte réseau ;
- bond ;
- bridge ;
- interfaces VLAN ;
- switch ;
- routeur ;
- destination.

Une seule interface ou un seul équipement qui ne prend pas en charge la taille attendue peut provoquer des pertes.

### 10.2 Examiner la MTU

```bash
ip link show
ip -d link show bond0
ip -d link show br0
```

Tester une taille IP précise en IPv4 :

```bash
ping -M do -s 1472 192.0.2.1
```

Pour IPv4, 1472 octets de données ICMP plus 8 octets d'en-tête ICMP et 20 octets d'en-tête IPv4 donnent 1500 octets, sans options IPv4.

Ce test ne garantit pas que toutes les tailles de paquets ou tous les protocoles fonctionnent. Il ne teste qu'un chemin, un instant et une taille donnés.

### 10.3 Offloads de la carte réseau

Les cartes réseau peuvent prendre en charge des fonctionnalités telles que :

- checksum offload ;
- segmentation TCP ;
- réception de paquets agrégés ;
- traitement VLAN matériel.

Consulter les capacités :

```bash
sudo ethtool -k enp1s0
sudo ethtool -S enp1s0
```

Ne désactivez pas tous les offloads par réflexe pour résoudre un problème de capture. Les captures locales peuvent être affectées par les mécanismes d'offload alors que le trafic transmis sur le fil reste correct.


## 11. Sécurité des VLAN, bonds et bridges

### 11.1 Le VLAN n'est pas un pare-feu

Un VLAN sépare les domaines de diffusion de niveau 2. Il ne garantit pas à lui seul une isolation complète des systèmes.

Les communications entre VLAN peuvent être autorisées par un routeur, un pare-feu ou un autre mécanisme de routage. Il faut donc vérifier les règles de filtrage et les chemins de routage.

### 11.2 Principes de sécurité

- N'autoriser que les VLAN nécessaires sur les trunks.
- Ne pas exposer le VLAN de gestion aux machines virtuelles qui n'en ont pas besoin.
- Définir explicitement le comportement des trames non marquées.
- Sécuriser l'accès administratif à l'hôte.
- Vérifier la configuration des interfaces virtuelles.
- Protéger les accès aux consoles des machines virtuelles.
- Contrôler les règles de filtrage sur l'hôte et les équipements physiques.
- Examiner les risques de boucles de niveau 2.
- Journaliser les modifications et conserver un plan de retour arrière.

### 11.3 Vérifier les règles nftables

```bash
sudo nft list ruleset
```

Dans une architecture bridge, le trafic commuté au niveau 2 n'emprunte pas nécessairement le même chemin que le trafic IP destiné à la pile réseau de l'hôte. Le comportement exact dépend notamment de la configuration Netfilter, des modules disponibles et de la façon dont le bridge est utilisé.

Ne supposez donc pas qu'une règle de pare-feu IP classique filtre automatiquement toutes les trames commutées par le bridge.


## 12. Diagnostic avancé

### 12.1 Vérifier l'état des liens

```bash
ip -br link
ip -s link
ethtool enp1s0
```

Cherchez :

- une interface administrativement désactivée ;
- un lien physique absent ;
- des erreurs RX ou TX ;
- des pertes de paquets ;
- des changements répétés d'état du lien.

### 12.2 Examiner le bond

```bash
cat /proc/net/bonding/bond0
ip -d link show bond0
ip -s link show bond0
```

En mode LACP, examinez notamment l'état de l'agrégation et comparez-le à celui du switch.

En mode active-backup, vérifiez l'interface active, les états des liens et les paramètres de surveillance.

### 12.3 Examiner le bridge

```bash
bridge link show
bridge vlan show
bridge fdb show
bridge -d link show
```

Une interface peut être active sans être membre du bridge attendu. Un port peut être membre du bridge mais ne pas autoriser le VLAN requis.

### 12.4 Examiner les routes

```bash
ip -4 route
ip -6 route
ip rule show
```

Vérifiez la route de destination, la route par défaut et les règles de routage. Une configuration correcte au niveau Ethernet ne garantit pas une route IP correcte.

### 12.5 Capturer au bon endroit

```bash
sudo tcpdump -eni enp1s0
sudo tcpdump -eni bond0
sudo tcpdump -eni br0
sudo tcpdump -eni br0.10
```

Ces captures permettent de comparer plusieurs étapes, mais chaque interface ne voit pas nécessairement les mêmes trames. Les offloads, le filtrage VLAN et le chemin exact du paquet influencent les résultats.

Pour filtrer le trafic lié à un hôte :

```bash
sudo tcpdump -ni br0 host 192.0.2.20
```

Pour examiner les trames ARP :

```bash
sudo tcpdump -eni br0 arp
```

### 12.6 Méthode de diagnostic par couches

```text
Symptôme : la VM ne joint pas sa passerelle
                    |
                    v
          1. Interface VM active ?
                    |
                    v
          2. Port virtuel dans br0 ?
                    |
                    v
          3. VLAN correct sur ce port ?
                    |
                    v
          4. VLAN autorisé sur le trunk ?
                    |
                    v
          5. Bond et liens physiques actifs ?
                    |
                    v
          6. Switch configuré correctement ?
                    |
                    v
          7. Adresse IP, masque et route corrects ?
                    |
                    v
          8. Filtrage ou pare-feu en cause ?
```

Ne changez pas plusieurs paramètres simultanément. Une modification à la fois permet de savoir quel changement a corrigé ou aggravé le problème.


## 13. Automatisation et exploitation

### 13.1 Bonnes pratiques de déploiement

Un déploiement avancé doit pouvoir être :

- répété sans créer des interfaces en double ;
- contrôlé avant application ;
- validé après application ;
- journalisé ;
- annulé si les contrôles échouent ;
- adapté aux différences de distribution.

Les commandes `ip link add` et `ip addr add` ne sont pas des opérations idempotentes dans tous les scénarios : la répétition peut provoquer des erreurs ou ajouter des adresses non souhaitées.

### 13.2 Vérifier avant de modifier

Exemple de script de contrôle non destructif :

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Interfaces ==="
ip -br link
ip -br addr

echo "=== Routes IPv4 ==="
ip -4 route

echo "=== Routes IPv6 ==="
ip -6 route

echo "=== Bonds présents ==="
if [[ -d /proc/net/bonding ]]; then
    ls -1 /proc/net/bonding
    for bond in /proc/net/bonding/*; do
        [[ -f "$bond" ]] || continue
        echo "--- $bond ---"
        cat "$bond"
    done
fi

echo "=== Bridges ==="
bridge link show
bridge vlan show
```

Enregistrer le script dans un fichier tel que `audit-reseau.sh`, puis :

```bash
chmod +x audit-reseau.sh
./audit-reseau.sh
```

Ce script collecte des informations ; il ne modifie pas la configuration.

### 13.3 Automatisation avec Ansible

Pour un parc de serveurs, une approche professionnelle consiste à utiliser des rôles Ansible qui :

1. identifient le gestionnaire réseau ;
2. vérifient les noms des interfaces ;
3. valident les paramètres attendus ;
4. sauvegardent la configuration persistante ;
5. déploient les profils réseau ;
6. appliquent les changements dans une fenêtre contrôlée ;
7. testent la connectivité ;
8. signalent les écarts.

Une simple tâche Ansible exécutant systématiquement `ip link add` n'est pas une bonne stratégie de gestion persistante. Privilégiez la gestion déclarative des profils et vérifiez l'état réellement appliqué.

### 13.4 Changement distant et retour arrière

Avant une modification réseau distante :

- conserver un accès console hors bande si possible ;
- sauvegarder les profils actifs ;
- noter l'adresse de gestion, la route et les VLAN actuels ;
- préparer les commandes de restauration ;
- prévoir une fenêtre de maintenance ;
- valider la connectivité après application.

Une sauvegarde ne suffit pas si personne ne peut l'appliquer après la perte de SSH. Le retour arrière doit être testé et accessible indépendamment du chemin réseau modifié.


## 14. Travaux pratiques

### TP 1 — Créer deux VLAN

**Objectif :** créer deux interfaces VLAN sur un trunk de laboratoire.

Préconditions :

- une interface physique disponible nommée `enp1s0` ;
- un switch ou un environnement virtuel transportant les VLAN 10 et 20 ;
- aucune configuration de production à préserver sur cette interface.

Commandes :

```bash
sudo ip link add link enp1s0 name enp1s0.10 type vlan id 10
sudo ip link add link enp1s0 name enp1s0.20 type vlan id 20

sudo ip link set enp1s0 up
sudo ip link set enp1s0.10 up
sudo ip link set enp1s0.20 up

sudo ip addr add 192.0.2.10/24 dev enp1s0.10
sudo ip addr add 198.51.100.10/24 dev enp1s0.20
```

Vérification :

```bash
ip -d link show enp1s0.10
ip -d link show enp1s0.20
ip -br addr
```

**Résultat attendu :** deux interfaces VLAN distinctes, avec les adresses IP correspondant à leur segment.

### TP 2 — Créer un bond de secours

**Objectif :** comprendre la différence entre une interface physique et le bond logique.

Dans un environnement de laboratoire :

```bash
sudo ip link add bond0 type bond mode active-backup
sudo ip link set enp1s0 down
sudo ip link set enp2s0 down

sudo ip link set enp1s0 master bond0
sudo ip link set enp2s0 master bond0

sudo ip link set enp1s0 up
sudo ip link set enp2s0 up
sudo ip link set bond0 up

cat /proc/net/bonding/bond0
```

**Résultat attendu :** les deux interfaces sont rattachées au bond et son état peut être inspecté.

N'effectuez pas ce TP sur les interfaces portant votre accès distant ou votre route par défaut.

### TP 3 — Créer un bridge

**Objectif :** créer un bridge et observer ses ports.

```bash
sudo ip link add br-lab type bridge
sudo ip link set br-lab up

sudo ip link add veth-a type veth peer name veth-b
sudo ip link set veth-a master br-lab
sudo ip link set veth-a up
sudo ip link set veth-b up

bridge link show
bridge fdb show br br-lab
```

Les interfaces `veth-a` et `veth-b` constituent une paire virtuelle. Elles permettent d'étudier la commutation sans brancher un câble physique.

### TP 4 — Bridge avec filtrage VLAN

**Objectif :** activer le filtrage VLAN et examiner les membres.

Dans un environnement de laboratoire :

```bash
sudo ip link add br-vlan type bridge vlan_filtering 1 vlan_default_pvid 0
sudo ip link set br-vlan up

sudo ip link add veth-c type veth peer name veth-d
sudo ip link set veth-c master br-vlan
sudo ip link set veth-c up
sudo ip link set veth-d up

sudo bridge vlan add dev veth-c vid 10 pvid untagged
sudo bridge vlan add dev br-vlan vid 10 self

bridge vlan show
bridge link show
```

**Résultat attendu :** le bridge et le port présentent une configuration VLAN observable.

La configuration du pair et les adresses IP nécessaires à une communication de niveau 3 ne sont pas ajoutées dans ce TP ; elles dépendent du scénario de test choisi.

### TP 5 — Dépannage

**Objectif :** analyser une panne à partir de l'état du système, sans modifier la configuration.

Exécuter :

```bash
ip -br link
ip -br addr
ip route
bridge link show
bridge vlan show
cat /proc/net/bonding/bond0
```

Répondre aux questions :

1. Le bond possède-t-il les membres attendus ?
2. Le bridge contient-il le bon port ?
3. Le VLAN attendu est-il autorisé sur le port ?
4. L'interface de niveau 3 porte-t-elle la bonne adresse ?
5. La route vers la destination est-elle présente ?
6. Les compteurs indiquent-ils des erreurs ?


## 15. Exercices avec corrections

### Exercice 1 — VLAN et routage

Un serveur doit accéder à deux réseaux :

- VLAN 10 : `192.0.2.0/24` ;
- VLAN 20 : `198.51.100.0/24`.

**Question :** est-il suffisant de créer les interfaces VLAN pour que les deux réseaux puissent communiquer entre eux ?

**Correction :**

Non. Les interfaces VLAN permettent à Linux d'émettre et de recevoir le trafic de chaque segment, mais la communication entre sous-réseaux nécessite un mécanisme de routage et des règles de sécurité appropriées. Le routage peut être assuré par un routeur externe ou par Linux si celui-ci est configuré comme routeur.

### Exercice 2 — LACP et débit

Deux liens de 1 Gbit/s sont agrégés en mode 802.3ad. Une seule connexion TCP mesure environ 1 Gbit/s.

**Question :** le bond est-il nécessairement défectueux ?

**Correction :**

Non. LACP distribue les flux selon un mécanisme de hachage. Une connexion TCP unique peut rester sur un seul lien. Pour vérifier l'agrégation, examinez l'état LACP, le groupe côté switch et plusieurs flux simultanés.

### Exercice 3 — Adresse IP sur un port du bridge

Une interface `enp1s0` est rattachée à `br0`, mais l'adresse IP de gestion est toujours configurée sur `enp1s0`.

**Question :** quelle organisation faut-il normalement privilégier ?

**Correction :**

Pour le modèle courant d'un hôte qui communique à travers le bridge, l'adresse IP est placée sur `br0` ou sur une interface VLAN du bridge, selon le réseau. L'interface physique reste le port de niveau 2. La migration doit être réalisée avec précaution pour éviter de perdre la connectivité.

### Exercice 4 — Trunk incomplet

Linux autorise les VLAN 10, 20 et 30, mais le switch ne transporte que les VLAN 10 et 20.

**Question :** que se passe-t-il pour le VLAN 30 ?

**Correction :**

L'autorisation locale ne suffit pas. Le VLAN 30 ne peut pas traverser le trunk si le switch ne le transporte pas. Il faut vérifier les deux côtés de la liaison.

### Exercice 5 — MTU incohérente

Le bond utilise une MTU de 9000, mais un équipement intermédiaire n'accepte que les trames correspondant à une MTU IP de 1500.

**Question :** quel est le risque ?

**Correction :**

Les paquets trop grands peuvent être abandonnés ou nécessiter des mécanismes d'adaptation. Les pannes peuvent toucher certaines tailles de paquets seulement. Il faut valider la MTU de bout en bout plutôt que supposer qu'une MTU configurée localement est prise en charge sur tout le chemin.


## 16. Défi final : concevoir un hyperviseur Linux

### Contexte

Vous devez préparer un hyperviseur de laboratoire avec :

- deux interfaces physiques `enp1s0` et `enp2s0` ;
- un bond `bond0` en mode active-backup ;
- un bridge VLAN-aware `br0` ;
- un VLAN 10 pour la gestion ;
- un VLAN 20 pour les machines virtuelles applicatives ;
- un VLAN 30 pour les services de stockage.

Plan d'adressage :

| Segment | Adresse de l'hôte |
|---|---|
| VLAN 10 | `192.0.2.10/24` |
| VLAN 20 | `198.51.100.10/24` |
| VLAN 30 | `203.0.113.10/24` |

Les adresses sont illustratives. Le switch est supposé configuré pour transporter les trois VLAN sur le lien relié au bond.

### Travail demandé

1. Vérifier l'état des interfaces physiques.
2. Créer le bond et y rattacher les deux interfaces.
3. Créer le bridge avec filtrage VLAN.
4. Rattacher le bond au bridge.
5. Autoriser les VLAN 10, 20 et 30 sur le port trunk.
6. Configurer les VLAN nécessaires à la pile réseau de l'hôte.
7. Vérifier les routes, les adresses et les tables du bridge.
8. Définir une procédure de retour arrière.
9. Expliquer comment diagnostiquer la perte du VLAN 20.

### Correction de référence

La correction suivante illustre la logique d'une configuration temporaire sur une machine de laboratoire. Elle ne remplace pas une configuration persistante validée sur la distribution utilisée.

**Étape 1 — Vérifier les interfaces**

```bash
ip -br link
ip -br addr
ip route
```

**Étape 2 — Créer le bond**

```bash
sudo ip link add bond0 type bond mode active-backup miimon 100

sudo ip link set enp1s0 down
sudo ip link set enp2s0 down

sudo ip link set enp1s0 master bond0
sudo ip link set enp2s0 master bond0

sudo ip link set enp1s0 up
sudo ip link set enp2s0 up
sudo ip link set bond0 up
```

**Étape 3 — Créer le bridge VLAN-aware**

```bash
sudo ip link add br0 type bridge vlan_filtering 1 vlan_default_pvid 0
sudo ip link set bond0 master br0
sudo ip link set bond0 up
sudo ip link set br0 up
```

**Étape 4 — Autoriser les VLAN sur le trunk**

```bash
sudo bridge vlan add dev bond0 vid 10
sudo bridge vlan add dev bond0 vid 20
sudo bridge vlan add dev bond0 vid 30

sudo bridge vlan add dev br0 vid 10 self
sudo bridge vlan add dev br0 vid 20 self
sudo bridge vlan add dev br0 vid 30 self
```

**Étape 5 — Créer les interfaces VLAN de l'hôte**

```bash
sudo ip link add link br0 name br0.10 type vlan id 10
sudo ip link add link br0 name br0.20 type vlan id 20
sudo ip link add link br0 name br0.30 type vlan id 30

sudo ip link set br0.10 up
sudo ip link set br0.20 up
sudo ip link set br0.30 up

sudo ip addr add 192.0.2.10/24 dev br0.10
sudo ip addr add 198.51.100.10/24 dev br0.20
sudo ip addr add 203.0.113.10/24 dev br0.30
```

**Étape 6 — Vérifier l'état du système**

```bash
ip -br link
ip -br addr
ip route
cat /proc/net/bonding/bond0
bridge link show
bridge vlan show
bridge fdb show
```

**Étape 7 — Diagnostiquer la perte du VLAN 20**

Suivre la chaîne :

```text
VM applicative
     |
     v
Interface virtuelle de la VM
     |
     v
Port du bridge
     |
     v
VLAN 20 autorisé ?
     |
     v
br0 / bond0
     |
     v
VLAN 20 autorisé sur le trunk physique ?
     |
     v
Switch configuré avec VLAN 20 ?
     |
     v
Adresse IP / passerelle / filtrage
```

Si les interfaces et les VLAN sont correctement configurés, capturer le trafic aux points pertinents :

```bash
sudo tcpdump -eni br0
sudo tcpdump -eni bond0
sudo tcpdump -eni br0.20
```

Comparer les trames observées avec le comportement attendu, puis examiner les compteurs du bond et des interfaces physiques.

**Étape 8 — Retour arrière**

Sur une configuration de laboratoire, supprimer les interfaces logiques créées avant de supprimer leurs dépendances :

```bash
sudo ip link del br0.10
sudo ip link del br0.20
sudo ip link del br0.30

sudo ip link set bond0 nomaster
sudo ip link del br0

sudo ip link set enp1s0 nomaster
sudo ip link set enp2s0 nomaster
sudo ip link del bond0
```

Cette séquence retire les objets créés dans le défi, mais ne restaure pas automatiquement une ancienne configuration IP, des routes, des profils NetworkManager ou d'autres paramètres qui auraient été modifiés avant le TP. Sur un serveur réel, restaurez les profils d'origine selon une procédure testée.


## 17. Checklist de validation professionnelle

Avant de considérer une architecture réseau avancée comme opérationnelle, vérifiez :

- [ ] Les noms et rôles des interfaces physiques sont documentés.
- [ ] Le mode de bonding correspond à la configuration du switch.
- [ ] Les liens du bond présentent l'état attendu.
- [ ] Les VLAN autorisés correspondent à la politique réseau.
- [ ] Le comportement des trames non marquées est explicite.
- [ ] Les ports du bridge appartiennent aux bons VLAN.
- [ ] Les adresses IP sont placées sur les interfaces logiques appropriées.
- [ ] Les routes IPv4 et IPv6 sont correctes.
- [ ] La MTU est cohérente sur le chemin réseau.
- [ ] Le filtrage réseau est vérifié sur l'hôte et les équipements amont.
- [ ] Les compteurs d'erreurs sont examinés.
- [ ] Les tests de perte d'un lien ont été réalisés.
- [ ] Les profils persistants sont conformes à l'état courant.
- [ ] Le retour arrière est documenté et testé.
- [ ] La configuration et les changements sont documentés.


## 18. Fiche de révision rapide

### Commandes essentielles

| Besoin | Commande |
|---|---|
| Voir les interfaces | `ip -br link` |
| Voir les adresses | `ip -br addr` |
| Voir les routes | `ip route` |
| Voir un VLAN | `ip -d link show enp1s0.10` |
| Voir le bond | `cat /proc/net/bonding/bond0` |
| Voir les ports du bridge | `bridge link show` |
| Voir les VLAN du bridge | `bridge vlan show` |
| Voir les adresses MAC apprises | `bridge fdb show` |
| Capturer les trames | `tcpdump -eni INTERFACE` |
| Examiner la carte réseau | `ethtool INTERFACE` |
| Voir les profils NetworkManager | `nmcli connection show` |

### À retenir absolument

1. Un VLAN segmente le niveau 2.
2. Un bond regroupe des interfaces physiques selon un mode défini.
3. Un bridge commute des trames Ethernet.
4. LACP doit être cohérent sur Linux et sur le switch.
5. Le débit d'un flux unique n'est pas nécessairement égal à la somme des liens agrégés.
6. Le filtrage VLAN d'un bridge doit être configuré explicitement.
7. Les interfaces de niveau 3 doivent être placées au bon endroit dans la topologie.
8. Une configuration temporaire avec `ip` n'est pas automatiquement persistante.
9. La MTU et le filtrage doivent être vérifiés de bout en bout.
10. Toute modification réseau distante doit prévoir une procédure de récupération.


## 19. Glossaire

**Bonding :** regroupement logique d'interfaces réseau physiques.

**Bridge :** commutateur Ethernet logiciel fonctionnant au niveau 2.

**FDB :** Forwarding Database, table des associations entre adresses MAC et ports d'un bridge.

**LACP :** Link Aggregation Control Protocol, protocole de négociation d'une agrégation de liens.

**MTU :** taille maximale d'un paquet IP transporté sur une interface sans fragmentation au niveau IP dans le cas classique.

**PVID :** VLAN auquel sont associées les trames entrantes non marquées sur un port VLAN-aware.

**Trunk :** liaison transportant plusieurs VLAN.

**VLAN :** Virtual LAN, domaine de diffusion Ethernet logique.

**VID :** identifiant d'un VLAN.

**802.1Q :** standard d'encapsulation Ethernet utilisant une balise VLAN.

**STP :** Spanning Tree Protocol, protocole permettant de limiter les boucles de niveau 2.

**Offload :** traitement délégué à la carte réseau plutôt qu'effectué entièrement par le processeur.


## 20. Documentation officielle

- Documentation du noyau Linux — Ethernet Bridging : https://www.kernel.org/doc/html/latest/networking/bridge.html
- Documentation du noyau Linux — Bonding : https://docs.kernel.org/networking/bonding.html
- Manuel officiel de `nmcli` : https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html
- Référence des propriétés NetworkManager : https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nm-settings-nmcli.html
- Documentation de `systemd.network` : https://www.freedesktop.org/software/systemd/man/latest/systemd.network.html
- Documentation de `systemd.netdev` : https://www.freedesktop.org/software/systemd/man/latest/systemd.netdev.html

Pour chaque déploiement, consultez la documentation correspondant à la version du noyau, de NetworkManager ou de systemd réellement installée.