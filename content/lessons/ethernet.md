# Ethernet — Fondamentaux, commutation et diagnostic (niveau CCNA / Admin Réseau)

> **Objectif du cours** : comprendre Ethernet de la prise RJ45 jusqu'au tableau MAC du switch, savoir expliquer une trame, configurer un port Cisco, vérifier un lien sous Linux et diagnostiquer les pannes classiques (négociation, duplex, câblage, FCS, PoE, EtherChannel). Ce cours est volontairement dense : il relie la théorie, les commandes réelles et les cas de production.

---

## 1. Pourquoi Ethernet a gagné

Ethernet est une technologie de réseau local normalisée par l'IEEE sous la famille **802.3**. Elle a battu Token Ring, FDDI et ATM dans le LAN pour plusieurs raisons :

- simplicité de câblage et de coût ;
- compatibilité ascendante entre 10 Mbit/s, 100 Mbit/s, 1 Gbit/s, 10 Gbit/s, 25/40/100 Gbit/s ;
- fonctionnement en commutation, qui évite les collisions sur les liens modernes ;
- écosystème immense, du petit switch domestique au cœur de datacenter.

Ethernet est une technologie **de couche 2** au sens OSI. Il transporte des trames vers une adresse MAC, pas vers une adresse IP. Le routeur, lui, retire la trame Ethernet pour examiner le paquet IP. Cette séparation est essentielle : un problème Ethernet peut empêcher tout le reste, même si l'adressage IP est parfait.

### 1.1 Le modèle en couches appliqué à Ethernet

```text
Application      HTTP, DNS, DHCP...
Transport        TCP / UDP (ports)
Réseau           IP (adresses logiques, routage)
Data Link        Ethernet + 802.1Q + STP (MAC, VLAN)
Physique         RJ45, fibres, signaux électriques/optiques
```

Une trame Ethernet ne contient pas d'adresse IP « à sa place » : elle contient un **EtherType** qui indique le protocole encapsulé (0x0800 pour IPv4, 0x86DD pour IPv6, 0x8100 pour un tag VLAN). C'est un point souvent mal compris en dépannage.

---

## 2. Les normes et débits

| Norme | Débit | Média typique | Distance pratique | Remarques |
|---|---:|---|---:|---|
| 10BASE-T | 10 Mbit/s | UTP cat. 3/5, 2 paires | 100 m | Historique, half/full duplex |
| 100BASE-TX | 100 Mbit/s | UTP cat. 5, 2 paires | 100 m | Fast Ethernet |
| 1000BASE-T | 1 Gbit/s | UTP cat. 5e/6, 4 paires | 100 m | Le plus courant en access |
| 1000BASE-SX | 1 Gbit/s | Fibre multimode 850 nm | 220–550 m | Campus, uplinks |
| 1000BASE-LX | 1 Gbit/s | Fibre mono/multimode 1310 nm | 550 m – 10 km | Selon fibre |
| 10GBASE-T | 10 Gbit/s | UTP cat. 6a/7 | 100 m | Chaleur et coût plus élevés |
| 10GBASE-SR | 10 Gbit/s | Fibre multimode | 300–400 m | Datacenter |
| 10GBASE-LR | 10 Gbit/s | Fibre monomode | 10 km | Liaisons longue distance |
| 25GBASE-SR | 25 Gbit/s | Fibre multimode | 100 m | Serveurs/ToR |
| 40GBASE-SR4 | 40 Gbit/s | 4 paires fibre | 100–150 m | QSFP |
| 100GBASE-SR4 | 100 Gbit/s | 4 paires fibre | 70–100 m | Datacenter |

**À retenir** : la catégorie de câble et la longueur ne sont pas les seuls critères. La qualité des connecteurs, le diamètre de fibre, la propreté des ferrures et le budget optique déterminent la linkabilité réelle. Un lien qui « monte » peut être saturé d'erreurs.

### 2.1 Catégories de câbles cuivre

| Catégorie | Bande passante | Débits usuels | Blindage | Usage |
|---|---:|---|---|---|
| Cat 5 | 100 MHz | 100 Mbit/s | UTP | Ancien, à éviter |
| Cat 5e | 100 MHz | 1 Gbit/s | UTP | Access bureautique |
| Cat 6 | 250 MHz | 1 Gbit/s, 10G ≤ 55 m | UTP/FTP | Bureaux, caméras |
| Cat 6a | 500 MHz | 10 Gbit/s ≤ 100 m | FTP/STP | Datacenter, PoE |
| Cat 7 | 600 MHz | 10 Gbit/s | SFTP | Blindage exigeant |
| Cat 8 | 2000 MHz | 25/40 Gbit/s ≤ 30 m | SFTP | Très court, ToR |

Pour la **PoE**, la section des conducteurs (AWG) et la qualité du câble comptent : la puissance dissipée chauffe les faisceaux, surtout en Cat 5e.

---

## 3. La trame Ethernet en détail

### 3.1 Format 802.3 / Ethernet II

```text
+----------------+----------------+----------------+----------------+----------------+
| Préambule 7 o  | SFD 1 o        | MAC dst 6 o    | MAC src 6 o    | Type/Long. 2 o |
+----------------+----------------+----------------+----------------+----------------+
| Données + éventuel padding (46–1500 o)                        | FCS 4 o          |
+---------------------------------------------------------------+------------------+
```

| Champ | Taille | Rôle |
|---|---:|---|
| Préambule | 7 octets | Synchronisation des horloges (0xAA) |
| SFD | 1 octet | Start Frame Delimiter (0xAB) |
| MAC destination | 6 octets | Destinataire L2 |
| MAC source | 6 octets | Émetteur L2 |
| EtherType / Longueur | 2 octets | Protocole supérieur ou taille |
| Payload | 46–1500 octets | Données IP, ARP, etc. |
| FCS | 4 octets | CRC-32 de contrôle d'intégrité |

La taille minimale d'une trame Ethernet est **64 octets** (hors préambule/SFD), et la taille maximale standard est **1518 octets** (ou 1522 avec un tag 802.1Q). Le **MTU** usuel est 1500 octets pour la charge IP. Les **jumbo frames** (9000 octets) doivent être configurées de bout en bout, sinon les gros paquets sont fragmentés ou abandonnés.

### 3.2 Le FCS et les erreurs

Le FCS est calculé par l'émetteur ; le récepteur refait le calcul. Si le résultat diffère, la trame est **jetée**. Le switch compte alors une erreur :

- **CRC** : corruption pendant le transport (câble, optique, interférence, duplex) ;
- **alignment** : trame mal alignée, souvent liée à un problème physique ;
- **runt** : trame trop courte (< 64 octets) ;
- **giant** : trame trop longue (MTU incohérent, bug) ;
- **late collision** : collision détectée trop tard (half-duplex, câblage trop long) ;
- **input errors** : cumul d'erreurs de réception.

Une augmentation régulière des CRC justifie de vérifier le câble, les connecteurs, l'optique et la configuration de duplex avant d'accuser le switch.

---

## 4. Adressage MAC

Une adresse MAC est composée de **48 bits**, notés en hexadécimal : `00:1A:2B:3C:4D:5E`. Les 24 premiers bits forment l'**OUI** (Organizationally Unique Identifier), attribué à un constructeur. Les 24 derniers sont attribués par le constructeur.

| Type | Exemple | Signification |
|---|---|---|
| Unicast | `00:1A:2B:3C:4D:5E` | Une seule interface |
| Broadcast | `FF:FF:FF:FF:FF:FF` | Toutes les interfaces du domaine de diffusion |
| Multicast | `01:00:5E:xx:xx:xx` | Groupe (IPv4 multicast) |
| Localement administrée | 2e bit du 1er octet = 1 | MAC virtuelle, VM, bridge |
| Adresse de groupe | 1er bit du 1er octet = 1 | Multicast/broadcast |

Un switch apprend les MAC **sources** et filtre sur les MAC **destinations**. Une MAC de destination inconnue provoque une **flooding** dans le VLAN concerné, pas dans tous les VLANs. C'est pourquoi un domaine de diffusion trop grand dégrade les performances.

### 4.1 MAC table (CAM table)

```text
Switch# show mac address-table
          Mac Address Table
-------------------------------------------
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
  10    001a.2b3c.4d5e    DYNAMIC     Gi0/1
  10    001a.2b3c.4d5f    DYNAMIC     Gi0/2
  20    001a.2b3c.4d60    DYNAMIC     Gi0/24
  10    001a.2b3c.4d61    STATIC      Gi0/3
```

- **DYNAMIC** : apprise par la source des trames, vieillit après 300 s par défaut.
- **STATIC** : configurée manuellement, ne vieillit pas.
- **Secure** : associée à la sécurité de port (port-security).

Commandes utiles :

```cisco
show mac address-table
show mac address-table dynamic
show mac address-table interface Gi0/1
show mac address-table vlan 10
show mac address-table count
clear mac address-table dynamic
```

Sous Linux, la table est visible avec :

```bash
bridge fdb show
bridge fdb show dev br0
ip link show
```

---

## 5. Fonctionnement d'un switch

Un switch est un pont multiport qui prend des décisions en couche 2 :

1. **Apprentissage** : il lit la MAC source et l'associe au port d'arrivée.
2. **Filtrage** : si la MAC destination est connue sur le même port, il ne transmet pas.
3. **Forwarding** : si la MAC destination est connue sur un autre port, il transmet uniquement là.
4. **Flooding** : si la destination est inconnue, broadcast ou multicast, il copie dans tous les ports du VLAN sauf le port source.
5. **Aging** : il supprime les entrées inutilisées après un délai.

```text
            MAC 00:...:01
   PC A --------------- Gi0/1
                         |
                     [ SW1 ]
                         |
   PC B --------------- Gi0/2
            MAC 00:...:02

1) A envoie vers B : SW1 apprend A sur Gi0/1, flood car B inconnue.
2) B répond : SW1 apprend B sur Gi0/2, forwarde vers Gi0/1.
3) Les trames suivantes A<->B sont commutées sans flooding.
```

### 5.1 Domaines de collision et de diffusion

- **Domaine de collision** : ensemble d'interfaces qui partagent le même support half-duplex. Un switch crée un domaine de collision par port (en full-duplex, il n'y a plus de collision).
- **Domaine de diffusion** : ensemble d'interfaces qui reçoivent un broadcast. Un VLAN = un domaine de diffusion. Un routeur (ou une interface L3) sépare les domaines de diffusion.

Un réseau plat de 500 postes = un seul domaine de diffusion, donc beaucoup de broadcast (ARP, DHCP, mDNS) et une table MAC énorme. La segmentation en VLAN est la réponse classique.

---

## 6. Duplex, auto-négociation et vitesses

### 6.1 Half-duplex vs full-duplex

| Mode | Collisions | Débit effectif | Usage |
|---|---|---|---|
| Half-duplex | Oui (CSMA/CD) | Partagé | Hubs, liens anciens |
| Full-duplex | Non | Bidirectionnel simultané | Tous les liens modernes |

Un **duplex mismatch** est l'une des pannes les plus fréquentes : un côté est en full, l'autre en half. Les symptômes sont des collisions tardives, des CRC, des performances catastrophiques et des liens qui « fonctionnent » mais lentement.

```text
Switch (full)  <---->  Serveur (half)
  - le switch émet sans écouter
  - le serveur croit qu'il y a des collisions
  - late collisions + CRC + retransmissions TCP
```

**Règle d'or** : sur un lien moderne, laisser l'auto-négociation des deux côtés, ou forcer **vitesse et duplex** des deux côtés. Ne jamais forcer d'un seul côté.

### 6.2 Auto-négociation

L'auto-négociation échange des capacités via des **FLP** (Fast Link Pulses). Elle choisit le meilleur mode commun : vitesse, duplex, MDI/MDIX. Un lien fibre ne négocie généralement pas la vitesse de la même façon ; vérifier les modules et la configuration.

Commandes Cisco :

```cisco
show interfaces status
show interfaces Gi0/1
show interfaces Gi0/1 capabilities
show interfaces counters errors
```

Configuration :

```cisco
interface Gi0/1
 description Uplink vers switch d'acces
 switchport mode access
 switchport access vlan 10
 speed auto
 duplex auto
 no shutdown
```

Sous Linux :

```bash
ip -s link show eth0
ethtool eth0
ethtool -S eth0
ethtool -s eth0 speed 1000 duplex full autoneg on
```

`ethtool` affiche `Speed`, `Duplex`, `Auto-negotiation`, `Link detected`. Les compteurs `rx_crc_errors`, `rx_frame_errors`, `tx_carrier_errors` sont précieux.

---

## 7. Câblage, MDI/MDIX et fibre

### 7.1 Brochage et paires

Ethernet 10/100 utilise deux paires (TX et RX). 1000BASE-T utilise les quatre paires en full-duplex. Un câble « croisé » n'est plus nécessaire grâce à **Auto-MDIX**, mais il faut vérifier que la fonction est active.

| Signal | Broche RJ45 | Couleur T568B |
|---|---:|---|
| TX+ | 1 | Blanc/orange |
| TX− | 2 | Orange |
| RX+ | 3 | Blanc/vert |
| RX− | 6 | Vert |
| Paire 3 | 4/5 | Bleu |
| Paire 4 | 7/8 | Marron |

Un câble mal sert ne provoque pas toujours une absence de lien : il peut provoquer des erreurs intermittentes, surtout en 1 Gbit/s et en PoE.

### 7.2 Fibre optique

| Type | Cœur | Source | Distance | Usage |
|---|---:|---|---:|---|
| Multimode OM1 | 62,5 µm | LED/VCSEL | ~275 m en 1G | Ancien |
| Multimode OM2 | 50 µm | VCSEL | ~550 m en 1G | Campus |
| Multimode OM3 | 50 µm | VCSEL | ~300 m en 10G | Datacenter |
| Multimode OM4 | 50 µm | VCSEL | ~400 m en 10G | Datacenter |
| Monomode OS2 | 9 µm | Laser | 10–80 km | Longue distance |

Points de diagnostic fibre : propreté des connecteurs, puissance reçue (`show interfaces transceiver`), alarmes DOM, polarity TX/RX, budget optique. Un lien optique peut être « up » avec une puissance marginale et des CRC.

---

## 8. VLAN et trunk : ce qu'Ethernet doit savoir

Un VLAN segmente le switch en plusieurs domaines de diffusion. Un port **access** appartient à un VLAN ; un port **trunk** transporte plusieurs VLANs avec des tags **802.1Q**.

### 8.1 Tag 802.1Q

```text
+--------+--------+--------+--------+--------+--------+
| MAC dst| MAC src| 0x8100 | TCI    | Type   | Data   |
+--------+--------+--------+--------+--------+--------+
                          VLAN ID (12 bits) + PCP (3 bits)
```

Le tag ajoute 4 octets. Le **VLAN natif** d'un trunk 802.1Q circule sans tag ; une incohérence de VLAN natif entre deux switches provoque des fuites de VLAN et des problèmes difficiles à voir.

Commandes Cisco :

```cisco
vlan 10
 name DATA
vlan 20
 name VOIX
interface Gi0/1
 switchport mode access
 switchport access vlan 10
interface Gi0/24
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,99
```

Vérification :

```cisco
show vlan brief
show interfaces trunk
show interfaces switchport
show spanning-tree vlan 10
```

Sous Linux, un bridge VLAN-aware :

```bash
ip link add link eth0 name eth0.10 type vlan id 10
ip link set eth0.10 up
ip link add name br10 type bridge
ip link set eth0.10 master br10
bridge vlan add dev eth0 vid 10
bridge vlan show
```

---

## 9. EtherChannel / LACP

Un EtherChannel agrège plusieurs liens physiques en un lien logique. Il augmente la bande passante et la résilience, mais **le trafic d'un flux donné emprunte un seul lien** (hachage). Il ne faut pas s'attendre à 2 Gbit/s pour une seule copie SMB.

| Protocole | Norme | Négociation | Usage |
|---|---|---|---|
| PAgP | Cisco | Propriétaire | Ancien |
| LACP | 802.3ad | Standard | Interopérable |
| Static | — | Aucune | Les deux côtés `on` |

Contraintes : même vitesse, même duplex, même mode (access/trunk), mêmes VLANs autorisés, même MTU. Une erreur de configuration provoque souvent un blocage STP ou un lien qui ne s'agrège pas.

```cisco
interface range Gi0/1-2
 channel-group 1 mode active
interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

Vérification :

```cisco
show etherchannel summary
show etherchannel port-channel
show lacp neighbor
show interfaces Port-channel1
```

Sous Linux, bonding :

```bash
ip link add bond0 type bond mode 802.3ad miimon 100
ip link set eth0 master bond0
ip link set eth1 master bond0
ip link set bond0 up
cat /proc/net/bonding/bond0
```

---

## 10. PoE (Power over Ethernet)

La PoE transporte l'alimentation sur le câble Ethernet. Elle est très utilisée pour les téléphones IP, caméras, bornes Wi-Fi et capteurs.

| Norme | Puissance au port | Puissance disponible | Usage |
|---|---:|---:|---|
| 802.3af (PoE) | 15,4 W | 12,95 W | Téléphones, caméras |
| 802.3at (PoE+) | 30 W | 25,5 W | Bornes Wi-Fi, caméras PTZ |
| 802.3bt Type 3 | 60 W | 51 W | Écrans, bornes |
| 802.3bt Type 4 | 90 W | 71 W | Fortes charges |

Un switch doit avoir un **budget PoE** suffisant. Si le budget est dépassé, les ports peuvent être refusés ou les équipements redémarrer. Vérifier :

```cisco
show power inline
show power inline Gi0/1
show power inline module 1
```

Configuration :

```cisco
interface Gi0/1
 power inline auto
 power inline police
```

---

## 11. Sécurité de base au niveau 2

Ethernet n'a pas de sécurité native. Les menaces classiques :

- **MAC flooding** : saturer la table CAM pour forcer le flooding ;
- **ARP spoofing** : usurper une passerelle ;
- **DHCP starvation/rogue** : épuiser les baux ou fournir un faux serveur ;
- **VLAN hopping** : double tagging ou trunk negotiation ;
- **STP manipulation** : devenir root bridge.

Contre-mesures Cisco :

```cisco
interface Gi0/1
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 spanning-tree bpduguard enable
```

Vérification :

```cisco
show port-security
show port-security interface Gi0/1
show ip dhcp snooping
show ip dhcp snooping binding
```

---

## 12. Atelier pratique : switch d'accès Cisco

Objectif : connecter un PC, un téléphone IP et un uplink trunk, avec VLAN données 10 et voix 20.

```cisco
enable
configure terminal
hostname SW-ACCESS-01
vlan 10
 name DATA
vlan 20
 name VOIX
vlan 99
 name MANAGEMENT
interface range Gi0/1-10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
interface Gi0/11
 switchport mode access
 switchport access vlan 20
 switchport voice vlan 20
 spanning-tree portfast
interface Gi0/24
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
 switchport trunk native vlan 99
interface Vlan99
 ip address 192.168.99.10 255.255.255.0
 no shutdown
ip default-gateway 192.168.99.1
end
write memory
```

Vérifications :

```cisco
show vlan brief
show interfaces status
show interfaces trunk
show mac address-table
show spanning-tree summary
show ip interface brief
ping 192.168.99.1
```

### 12.1 Test avec un PC Linux

```bash
ip link set eth0 up
ip addr add 192.168.10.50/24 dev eth0
ip route add default via 192.168.10.1
ping -c 4 192.168.10.1
ip neigh show
tcpdump -eni eth0 arp or icmp
```

Si le ping échoue, vérifier dans l'ordre : lien physique, VLAN, MAC table, passerelle, ARP, ACL, routage.

---

## 13. Dépannage méthodique

### 13.1 Le lien ne monte pas

| Vérification | Commande Cisco | Commande Linux |
|---|---|---|
| État physique | `show interfaces status` | `ip link`, `ethtool eth0` |
| Vitesse/duplex | `show interfaces` | `ethtool eth0` |
| Câble/optique | `show interfaces transceiver` | `ethtool -m eth0` |
| Erreurs | `show interfaces counters errors` | `ethtool -S eth0` |
| Port administré | `show running-config interface` | `ip link set eth0 up` |

Causes fréquentes : câble débranché, mauvais port, SFP incompatible, port shutdown, err-disabled, vitesse forcée incompatible, VLAN inexistant.

### 13.2 Le lien monte mais le ping échoue

1. Le PC a-t-il une IP dans le bon subnet ?
2. Le VLAN du port est-il correct (`show vlan brief`) ?
3. La passerelle est-elle configurée ?
4. ARP répond-il (`show arp`, `ip neigh`) ?
5. Le trunk autorise-t-il le VLAN ?
6. Une ACL ou un firewall bloque-t-il ?
7. Le retour de routage existe-t-il ?

### 13.3 Performances faibles et erreurs

```cisco
show interfaces Gi0/1
show interfaces Gi0/1 counters errors
show interfaces Gi0/1 counters detailed
show logging | include Gi0/1
```

Interprétation rapide :

- `CRC` en hausse : couche physique, duplex, câble, optique ;
- `late collisions` : half-duplex ou longueur excessive ;
- `runts` : collisions, câble, bug ;
- `giants` : MTU incohérent ;
- `input errors` : cumul, regarder le détail ;
- `output drops` : congestion, QoS, buffer.

### 13.4 Cas réel : le lien 1 Gbit/s qui ne fait que 10 Mbit/s

Un utilisateur se plaint de lenteur. Le switch indique `a-100` puis `a-10`. Le câble est un vieux Cat 5 avec une paire abîmée. L'auto-négociation retombe en 10 Mbit/s. On remplace le câble par du Cat 6, on vérifie `show interfaces status` : `a-1000`. Leçon : toujours vérifier la vitesse négociée, pas seulement l'état `up`.

### 13.5 Cas réel : PoE et caméra qui redémarre

Une caméra PoE redémarre chaque nuit. `show power inline` montre une puissance proche du budget. Le switch désactive le port lors des pics. Solution : répartir les caméras sur deux switches, ou utiliser un injecteur PoE+ dédié. Vérifier aussi la longueur et la qualité du câble.

---

## 14. Laboratoire de révision

1. Dessiner une trame Ethernet transportant un ping ICMP et identifier chaque champ.
2. Configurer deux switches reliés par un trunk, deux VLANs, et vérifier la connectivité.
3. Provoquer un duplex mismatch avec `ethtool -s eth0 speed 100 duplex half autoneg off` et observer les compteurs.
4. Configurer un EtherChannel LACP entre deux switches et vérifier `show etherchannel summary`.
5. Capturer un ARP avec `tcpdump -eni eth0 arp` et expliquer le broadcast.
6. Vérifier le budget PoE et la classe d'un téléphone IP.

---

## 15. Mémo des commandes

```cisco
! Cisco
show interfaces status
show interfaces Gi0/1
show interfaces counters errors
show mac address-table
show vlan brief
show interfaces trunk
show etherchannel summary
show power inline
show spanning-tree
show logging
```

```bash
# Linux
ip -br link
ip -s link show eth0
ethtool eth0
ethtool -S eth0
bridge fdb show
bridge vlan show
tcpdump -eni eth0
cat /proc/net/bonding/bond0
```

---

## 16. Points clés à retenir

- Ethernet est une technologie L2 ; le switch commute sur MAC, le routeur route sur IP.
- Une trame standard fait 64 à 1518 octets ; le FCS détecte les erreurs mais ne les corrige pas.
- Le switch apprend les MAC sources, filtre, forwarde ou floode.
- Un VLAN = un domaine de diffusion ; un trunk transporte plusieurs VLANs avec 802.1Q.
- Le duplex mismatch et les erreurs CRC sont les pannes physiques les plus fréquentes.
- LACP agrège des liens physiques, mais un flux reste sur un seul lien.
- La PoE doit être budgétée ; un port peut refuser l'alimentation.
- Toujours diagnostiquer de la couche 1 vers la couche 3, puis vérifier le retour.

> **Exercice de synthèse** : un poste ne joint pas sa passerelle. Le lien est `up`, la MAC est apprise, le VLAN est correct, mais `show interfaces` indique des `late collisions`. Quelle est l'hypothèse la plus probable, et quelle commande permet de la confirmer ? Réponse attendue : duplex mismatch ; vérifier `show interfaces` des deux côtés et `ethtool` sur le poste, puis aligner vitesse et duplex.
