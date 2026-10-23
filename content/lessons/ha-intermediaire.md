# VRRP, HSRP et LACP

**Niveau :** Administrateur Réseau Confirmé

Maintenant que vous comprenez la théorie de la redondance, passons à la configuration des protocoles qui permettent à deux routeurs de se partager une passerelle virtuelle (FHRP), et comment agréger des liens physiques pour créer un lien logique plus rapide et tolérant aux pannes.

> **Analogie** : VRRP et HSRP, c'est comme avoir un remplaçant prêt à prendre le poste. LACP (agrégation), c'est comme construire un pont à plusieurs voies : si une voie est fermée, les voitures continuent de circuler sur les autres.

## 1. VRRP (Virtual Router Redundancy Protocol)

VRRP est le standard ouvert (RFC 3768). Il utilise les termes **Master** (actif) et **Backup** (en veille).

- **Priorité** : Par défaut à 100. Le routeur avec la priorité la plus haute devient Master.
- **Préemption** : Activée par défaut. Si un routeur avec une priorité plus haute revient, il reprend le rôle de Master.

```cisco
interface GigabitEthernet0/1
 ip address 192.168.10.2 255.255.255.0
 vrrp 10 ip 192.168.10.1
 vrrp 10 priority 120
 vrrp 10 preempt
(Ici, R1 a une priorité de 120, il sera donc le Master par défaut).

2. HSRP (Hot Standby Router Protocol)
HSRP est le protocole propriétaire Cisco. Il utilise les termes Active et Standby.

La configuration est très similaire à VRRP.

Différence majeure : La préemption est désactivée par défaut. Il faut l'activer manuellement (standby 10 preempt).

cisco
interface GigabitEthernet0/1
 ip address 192.168.10.2 255.255.255.0
 standby 10 ip 192.168.10.1
 standby 10 priority 120
 standby 10 preempt
3. Le suivi d'interface (Tracking)
Sans suivi d'interface, si le lien WAN (Internet) du routeur Master tombe, il restera Master alors qu'il n'a plus d'accès Internet.
Le "tracking" permet de baisser la priorité du routeur si une interface critique tombe, forçant le Backup à prendre le relais.

cisco
track 1 interface GigabitEthernet0/0 line-protocol
!
interface GigabitEthernet0/1
 vrrp 10 track 1 decrement 30
4. L'agrégation de liens (LACP / EtherChannel)
L'agrégation consiste à regrouper plusieurs câbles physiques en un seul lien logique pour augmenter la bande passante et éviter les coupures.

LACP (IEEE 802.3ad) : Négocie l'agrégation.

Mode Active : Le port initie la négociation.

Mode Passive : Le port attend que l'autre côté initie.

cisco
interface range GigabitEthernet0/1-2
 channel-group 10 mode active
!
interface Port-channel10
 switchport mode trunk
Attention : Un seul gros flux (comme une sauvegarde) ne dépassera pas la vitesse d'un seul câble. LACP répartit les flux (hash), il n'additionne pas les vitesses pour un seul transfert.

