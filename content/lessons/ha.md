# Haute disponibilité : VRRP, HSRP et agrégation de liens

La haute disponibilité consiste à concevoir un réseau qui continue de fournir
le service malgré la panne d'un lien, d'un switch, d'un routeur ou d'une
alimentation. Elle ne se résume pas à acheter deux équipements : il faut aussi
prévoir le basculement, le retour à l'état normal et les tests de panne.

> Analogie : une porte d'entrée unique peut être parfaite, mais si elle est
> bloquée, tout le monde reste dehors. Une deuxième porte, avec une signalisation
> claire et des clés testées, évite que la panne devienne un arrêt total.

## 1. Les pannes à prévoir

Les causes fréquentes de coupure sont :

- panne d'alimentation ou de carte d'un équipement ;
- câble ou SFP défectueux ;
- boucle de niveau 2 ;
- saturation d'un lien ;
- bug logiciel ou mise à jour ratée ;
- erreur humaine lors d'un changement ;
- panne d'un routeur ou d'un fournisseur d'accès.

La redondance peut être physique, électrique, logicielle ou protocolaire. Une
bonne architecture combine plusieurs niveaux :

| Niveau | Exemple de redondance |
|---|---|
| Alimentation | Deux alimentations, onduleur, groupes électrogènes |
| Lien | Deux câbles, deux fibres, deux chemins |
| Commutation | Deux switches, STP, MLAG/vPC |
| Agrégation | LACP, EtherChannel |
| Passerelle | VRRP, HSRP |
| Routage | OSPF, BGP, routes de secours |
| Service | Deux serveurs, load balancer, réplication |

Le but n'est pas d'empêcher toute panne, mais de limiter son impact et de
permettre un retour rapide à un état connu.

## 2. VRRP : une passerelle virtuelle

VRRP (Virtual Router Redundancy Protocol) permet à plusieurs routeurs de
partager une adresse IP virtuelle. Les postes du LAN utilisent cette adresse
comme passerelle par défaut, sans savoir quel routeur est actif.

```text
              Réseau local
                   |
          Passerelle virtuelle 192.168.10.1
                 /             \
          R1 (master)       R2 (backup)
          192.168.10.2      192.168.10.3
```

Si R1 tombe, R2 prend l'adresse virtuelle et continue à router le trafic. Le
client conserve la même passerelle : le changement est transparent, à condition
que la panne soit détectée et que le basculement soit rapide.

### Rôles et priorités

Un routeur VRRP est **master** ou **backup**. La priorité la plus élevée
l'emporte. La priorité par défaut est 100 ; une priorité de 255 réserve
l'adresse au propriétaire de l'IP virtuelle.

En cas d'égalité, l'adresse IP la plus élevée départage les routeurs. Le master
annonce régulièrement sa présence avec des paquets VRRP. Si les backups ne
reçoivent plus ces annonces, l'un d'eux devient master.

### Préemption

La préemption permet à un routeur de reprendre le rôle de master lorsqu'il
revient avec une priorité supérieure. Elle est généralement activée par défaut
dans VRRP. Selon le besoin, on peut la désactiver pour éviter un basculement
intempestif.

> Analogie : le remplaçant peut garder la place jusqu'au retour du titulaire, ou
> lui rendre immédiatement. La préemption définit cette règle.

### Suivi d'interface

Un routeur peut baisser sa priorité si une interface importante tombe. Cela
permet de provoquer le basculement avant que les utilisateurs ne subissent une
panne complète.

Exemple Cisco :

```cisco
interface GigabitEthernet0/1
 ip address 192.168.10.2 255.255.255.0
 vrrp 10 ip 192.168.10.1
 vrrp 10 priority 120
 vrrp 10 preempt
 vrrp 10 track 1 decrement 30

track 1 interface GigabitEthernet0/0 line-protocol
```

Le routeur est master tant que son lien WAN est opérationnel. Si le lien tombe,
la priorité baisse et le backup peut prendre le relais.

### VRRP sous Linux

Keepalived est une implémentation courante de VRRP sous Linux. Exemple
simplifié :

```text
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 10
    priority 120
    advert_int 1
    virtual_ipaddress {
        192.168.10.1/24
    }
}
```

Le démon doit être autorisé à envoyer/recevoir les paquets VRRP et à manipuler
l'adresse virtuelle. En production, on utilise souvent deux nœuds avec des
priorités différentes et une vérification de santé applicative.

### VRRP et la couche 2

VRRP utilise une adresse MAC virtuelle, généralement
`00:00:5E:00:01:XX`, où `XX` est l'identifiant du groupe VRRP. Les switches
doivent apprendre cette MAC sur le port du routeur actif. Après un basculement,
la MAC peut apparaître sur un autre port ; les tables CAM et ARP doivent se
mettre à jour.

## 3. HSRP : la redondance Cisco

HSRP (Hot Standby Router Protocol) est un protocole Cisco qui remplit un rôle
proche de VRRP. Un routeur est **active**, l'autre est **standby**. Ils
partagent une adresse IP virtuelle et une MAC virtuelle.

```text
              Réseau local
                   |
          Passerelle virtuelle 192.168.10.1
                 /             \
          R1 (active)       R2 (standby)
          192.168.10.2      192.168.10.3
```

### Priorité et préemption

La priorité par défaut est 100 ; la plus élevée devient active. Contrairement à
VRRP, la préemption HSRP est désactivée par défaut sur Cisco. Il faut
l'activer explicitement pour que le routeur prioritaire reprenne la main après
son retour.

```cisco
interface GigabitEthernet0/1
 ip address 192.168.10.2 255.255.255.0
 standby 10 ip 192.168.10.1
 standby 10 priority 120
 standby 10 preempt
 standby 10 track 1 decrement 30
```

### Versions HSRP

HSRP version 1 utilise des groupes et une MAC virtuelle historique. HSRP
version 2 augmente le nombre de groupes et prend mieux en charge IPv6. Les deux
routeurs doivent utiliser la même version et le même groupe.

### Suivi d'objet

Le suivi d'interface ou d'objet permet de diminuer la priorité quand une
ressource critique tombe. Sans cela, le routeur peut rester actif alors qu'il
n'a plus d'accès utile à Internet ou au réseau central.

### VRRP ou HSRP ?

| Critère | VRRP | HSRP |
|---|---|---|
| Origine | Standard ouvert | Cisco |
| Termes | Master / backup | Active / standby |
| Priorité | Plus élevée gagne | Plus élevée gagne |
| Préemption | Souvent activée par défaut | Désactivée par défaut sur Cisco |
| MAC virtuelle | 00:00:5E:00:01:XX | MAC propre à HSRP |
| Interopérabilité | Multi-constructeurs | Surtout Cisco |

Les deux protocoles ne se mélangent pas. On choisit une solution et on
l'applique de manière cohérente sur le segment.

## 4. Le split brain

Le split brain arrive lorsque deux routeurs se croient tous les deux actifs.
Cela peut produire deux réponses ARP pour la même IP virtuelle, des
comportements erratiques et des coupures.

Causes fréquentes :

- lien de heartbeat coupé ;
- VLAN différent entre les deux routeurs ;
- filtrage multicast ou pare-feu ;
- authentification ou groupe VRRP/HSRP différent ;
- MTU incohérente ;
- version ou timers incompatibles.

Pour éviter le split brain, on utilise un lien de heartbeat redondant, une
configuration identique et une supervision des deux équipements.

## 5. LACP et EtherChannel

L'agrégation de liens consiste à regrouper plusieurs liens physiques en un lien
logique. Un **EtherChannel** Cisco ou un **bond** Linux peut augmenter la
capacité et fournir de la redondance.

> Analogie : au lieu d'un seul pont à une voie, on construit deux voies côte à
> côte. Le trafic peut être réparti, et si une voie ferme, l'autre peut encore
> servir.

### LACP

LACP (Link Aggregation Control Protocol, IEEE 802.3ad) négocie l'agrégation
entre les deux extrémités. Les modes courants sont :

- **active** : le port initie la négociation ;
- **passive** : le port attend que l'autre côté initie.

Au moins un côté doit être actif. Deux côtés passifs ne forment pas de
négociation.

### EtherChannel statique

Un canal statique (`mode on`) ne négocie pas. Il peut fonctionner, mais il ne
détecte pas les erreurs de configuration de l'autre côté. LACP est généralement
préférable car il vérifie la cohérence des paramètres.

### Répartition du trafic

LACP ne fait pas de répartition par paquet. Le switch calcule un hash à partir
de certaines informations : MAC source/destination, IP source/destination,
ports, VLAN. Tous les paquets d'un même flux peuvent donc rester sur le même
lien.

Conséquences :

- un seul gros flux peut ne pas utiliser toute l'agrégation ;
- plusieurs flux répartis utilisent mieux la capacité ;
- la politique de hash doit être choisie selon le trafic.

### Contraintes

Les membres d'un EtherChannel doivent avoir des caractéristiques compatibles :

- même vitesse et duplex ;
- même VLAN ou même mode trunk ;
- même MTU ;
- même configuration STP ;
- mêmes paramètres LACP.

Un lien mal configuré peut être suspendu ou provoquer une boucle.

### Configuration Cisco

```cisco
interface range GigabitEthernet0/1-2
 channel-group 10 mode active
 no shutdown

interface Port-channel10
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

Vérification :

```cisco
show etherchannel summary
show etherchannel 10 port-channel
show lacp neighbor
show interfaces Port-channel10
```

### Bonding Linux

Sous Linux, on peut créer un bond avec `ip link` :

```bash
ip link add bond0 type bond mode 802.3ad miimon 100 lacp_rate fast
ip link set eth1 down
ip link set eth1 master bond0
ip link set eth1 up
ip link set eth2 down
ip link set eth2 master bond0
ip link set eth2 up
ip addr add 10.10.0.1/24 dev bond0
ip link set bond0 up
```

Vérification :

```bash
cat /proc/net/bonding/bond0
ip -s link show bond0
ip route get 10.10.0.2
```

Le mode `802.3ad` correspond à LACP. Les modes `active-backup` et `balance-xor`
existent aussi, mais ne négocient pas LACP de la même façon.

## 6. Redondance de liens et de chemins

L'agrégation de liens protège contre la panne d'un câble ou d'un port. Elle ne
protège pas contre la panne d'un switch entier si les deux liens aboutissent au
même équipement.

Pour aller plus loin :

- répartir les liens sur deux switches ;
- utiliser MLAG/vPC pour présenter une agrégation logique à travers deux
  switches ;
- utiliser STP/RSTP pour les boucles de niveau 2 ;
- utiliser OSPF/BGP et des routes de secours pour le niveau 3 ;
- utiliser BFD pour détecter rapidement une panne de voisin ;
- surveiller les compteurs et les logs.

### MLAG et vPC

MLAG (Multi-Chassis Link Aggregation) et vPC (Cisco) permettent à deux switches
de former une agrégation logique vue par le serveur. Le serveur peut avoir deux
liens vers deux switches différents tout en utilisant LACP.

Le serveur croit parler à un seul partenaire logique. Les switches se
synchronisent pour présenter une vue cohérente. Une mauvaise configuration du
peer-link peut créer une boucle ou un split brain.

## 7. Concevoir une passerelle redondante

Exemple de petite entreprise :

```text
        Internet
           |
     +-----+-----+
     |           |
   R1           R2
   | \         / |
   |  \       /  |
   |   Switch   |
   |  /       \  |
   +-+         +-+
     \         /
      Réseau local
```

- R1 et R2 partagent une IP virtuelle VRRP/HSRP.
- Le switch est relié aux deux routeurs.
- Les serveurs peuvent être dual-homed avec LACP.
- Les liens WAN peuvent utiliser deux fournisseurs.

Il faut éviter que les deux routeurs dépendent de la même alimentation, du même
switch ou du même fournisseur. La redondance doit être indépendante autant que
possible.

## 8. Timers, détection et préemption

Le temps de bascule dépend de la détection de panne et du protocole de
redondance. Les valeurs par défaut sont souvent suffisantes pour un réseau de
bureau, mais pas pour une application temps réel.

| Paramètre | VRRP | HSRP |
|---|---|---|
| Annonce / hello | 1 seconde | 3 secondes |
| Délai avant bascule | Environ 3 secondes | Environ 10 secondes |
| Priorité par défaut | 100 | 100 |
| Préemption | Souvent activée | Désactivée par défaut sur Cisco |

Des timers plus courts accélèrent la détection, mais augmentent le trafic de
contrôle et le risque de faux positif. Une perte momentanée de paquets peut
provoquer un basculement inutile si les timers sont trop agressifs.

### BFD

BFD (Bidirectional Forwarding Detection) est un protocole de détection rapide
de panne entre deux équipements. Il peut être associé à OSPF, BGP, HSRP ou VRRP
pour accélérer la convergence. BFD ne remplace pas le protocole de redondance :
il fournit une détection plus rapide.

### Preempt delay

La préemption immédiate peut être dangereuse après le retour d'un routeur :
celui-ci peut ne pas avoir reconstruit ses tables, ses sessions ou son accès
WAN. Un délai de préemption permet de laisser le routeur se stabiliser avant
de reprendre le rôle actif.

### Répartition de charge avec plusieurs groupes

VRRP et HSRP peuvent utiliser plusieurs groupes sur le même segment. On peut
ainsi faire passer un VLAN par R1 et un autre par R2, ou répartir des flux
selon les groupes. Il faut documenter les adresses virtuelles et les priorités
pour éviter les doublons.

## 9. Cas concret de basculement

Une entreprise possède deux routeurs R1 et R2 reliés à un switch de coeur. Les
postes utilisent la passerelle virtuelle `192.168.10.1`.

- R1 a la priorité 120 et suit son lien WAN.
- R2 a la priorité 100 et possède un lien WAN de secours.
- Les deux routeurs échangent des annonces VRRP.
- Le switch apprend la MAC virtuelle sur le port de R1.

Le lien WAN de R1 tombe. Le suivi d'interface baisse la priorité de R1 à 90.
R2, priorité 100, devient master et répond à l'ARP pour l'IP virtuelle. Les
postes n'ont pas changé de passerelle ; leurs paquets suivant partent vers R2.
Lorsque le WAN de R1 revient, la préemption lui rend le rôle actif après un
délai de stabilisation.

Ce scénario montre l'importance du suivi d'interface : sans lui, R1 serait
resté master avec un WAN coupé, et les utilisateurs auraient perdu Internet
malgré la présence d'un routeur de secours.

## 10. Tester le basculement

Un équipement redondant non testé n'est pas une garantie. Il faut planifier des
tests :

1. Débrancher un lien d'agrégation et vérifier que le trafic continue.
2. Éteindre le routeur actif et mesurer le temps de bascule.
3. Vérifier que le routeur de secours possède la bonne route.
4. Tester le retour du routeur principal et la préemption.
5. Vérifier les logs, les compteurs et les alertes.
6. Restaurer la configuration initiale.

Un basculement de passerelle peut prendre quelques secondes. Les applications
sensibles doivent avoir des timeouts et des mécanismes de reconnexion adaptés.

## 11. Dépannage

### Le VRRP/HSRP ne bascule pas

- Vérifier que les deux routeurs sont dans le même groupe et le même VLAN.
- Vérifier les priorités et la préemption.
- Vérifier que les annonces ne sont pas filtrées.
- Vérifier le lien de heartbeat.
- Vérifier que l'IP virtuelle n'est pas déjà utilisée par un autre équipement.

### Le bond ne monte pas

- Vérifier le mode des deux côtés.
- Vérifier que les liens sont up.
- Vérifier que les membres sont compatibles.
- Vérifier la configuration LACP.
- Vérifier les logs du switch et `/proc/net/bonding/bond0`.

### Le débit n'augmente pas

- Un seul flux peut rester sur un seul lien.
- Vérifier la politique de hash.
- Vérifier que tous les liens sont actifs.
- Vérifier la capacité des uplinks et des switches.

## 12. À retenir

- VRRP et HSRP fournissent une passerelle IP virtuelle redondante.
- VRRP est standard ; HSRP est une solution Cisco.
- La priorité et la préemption déterminent le routeur actif.
- Le suivi d'interface permet de déclencher un basculement utile.
- LACP agrège plusieurs liens et négocie avec le partenaire.
- LACP ne remplace pas une architecture redondante de bout en bout.
- Un bond doit être testé en débranchant un lien.
- La supervision et les tests de bascule font partie de la haute disponibilité.

La haute disponibilité est une propriété de l'architecture, pas seulement une
case cochée dans la configuration d'un équipement.
