# Virtual Routing and Forwarding (VRF) : Niveau Intermédiaire

Après avoir appréhendé la virtualisation des tables de routage en surface, ce cours aborde les mécanismes d'ingénierie sous-jacents de la **VRF-Lite**, la différence entre l'architecture globale et l'architecture VRF (`VRF-Aware`), ainsi que les techniques de fuite de routes (*Route Leaking*) contrôlées entre plusieurs tables.

---

## 1. De la VRF de Base à la VRF-Lite

### 1.1 Qu'est-ce que la VRF-Lite ?

Le terme **VRF-Lite** désigne l'implémentation de VRF **sans utiliser le protocole MPLS (Multi-Protocol Label Switching)** dans le réseau cœur (*Core Network*).

* **VRF classique (MPLS VPN) :** Utilisée principalement par les fournisseurs d'accès (Service Providers). Elle s'appuie sur MP-BGP et des étiquettes (Labels) MPLS pour propager les VRF d'un bout à autre d'un réseau étendu.
* **VRF-Lite :** Utilisée au sein des réseaux d'entreprise (Campus / Data Center). L'isolation VRF est maintenue localement sur chaque équipement L3 et propagée sur les liaisons inter-switchs en combinant la VRF avec le **Trunking 802.1Q (VLANs)** ou des sous-interfaces.

```
 [ Client A - VLAN 10 ] ──┐                                   ┌── [ Serveur A - VLAN 10 ]
                          ├──► [ Switch L3 A ] ═(Trunk 802.1Q)═► [ Switch L3 B ] ──┤
 [ Client B - VLAN 20 ] ──┘     (VRF A & B)     VLAN 10 & 20     (VRF A & B)    └── [ Serveur B - VLAN 20 ]

```

---

## 2. Les Composants Clés d'une VRF (`RD` & `RT`)

Pour manipuler les VRF dans des architectures complexes, deux identifiants clés sont introduits (bien que le `RD` et le `RT` soient issus du monde MPLS, la syntaxe moderne `vrf definition` les requiert sous Cisco IOS/NX-OS) :

### 2.1 Route Distinguisher (RD)

Le **Route Distinguisher** est un préfixe de **64 bits** (8 octets) ajouté à une adresse IPv4 (32 bits) pour créer une adresse unique globale appelée **VPNv4** (96 bits).

* **Format courant :** `ASN:NN` (ex: `65000:100`) ou `IP-Address:NN`.
* **Rôle :** Rendre un préfixe IP unique lorsqu'il y a chevauchement d'adresses (*Overlapping IP*).
* **Exemple :**
  * Dans la VRF_A : `65000:100` + `192.168.1.0/24` $\rightarrow$ `65000:100:192.168.1.0/24`
  * Dans la VRF_B : `65000:200` + `192.168.1.0/24` $\rightarrow$ `65000:200:192.168.1.0/24`

### 2.2 Route Target (RT)

Le **Route Target** est un attribut de communauté BGP étendu (*Extended Community*) utilisé pour contrôler le transfert et l'importation/exportation des routes entre les VRF.

* **`export route-target` :** Étiquette les routes sortant d'une VRF lorsqu'elles sont redistribuées.
* **`import route-target` :** Détermine quelles routes étiquetées doivent être acceptées et intégrées dans la table de routage de la VRF locale.

---

## 3. Communication Inter-VRF : Le Route Leaking (Fuite de Routes)

Par définition, deux VRF ne peuvent pas communiquer entre elles. Cependant, il est fréquent qu'un réseau nécessite d'accéder à un **Service Partagé** (ex: serveur DNS, serveur Active Directory, passerelle Internet ou pare-feu centralisé) depuis plusieurs VRF.

Cette interconnexion contrôlée s'appelle le **Route Leaking**.

### 3.1 Méthode 1 : Route Leaking via Static Routes (VRF-Lite)

C'est la méthode la plus simple sur un commutateur ou routeur unique.

#### Scénario :
Permettre à la **VRF_PROD** d'accéder au serveur DNS situé dans la **VRF_SHARED** (`10.50.0.100/32`).

```
! Route statique dans la VRF_PROD pointant vers le prochain saut dans la VRF_SHARED
ip route vrf VRF_PROD 10.50.0.100 255.255.255.255 GigabitEthernet0/0/2 10.50.0.1 global

! Route de retour dans la VRF_SHARED pointant vers le réseau de la VRF_PROD
ip route vrf VRF_SHARED 192.168.10.0 255.255.255.0 GigabitEthernet0/0/1 192.168.10.1 global

```

### 3.2 Méthode 2 : Route Leaking via BGP & Route Targets

C'est la méthode recommandée et la plus propre à grande échelle. Elle utilise le processus BGP local (BGP `address-family ipv4 vrf`).

```
! 1. Définition moderne de la VRF
vrf definition VRF_PROD
 rd 65000:10
 route-target export 65000:10
 route-target import 65000:10
 ! Importer le service partagé
 route-target import 65000:99
!
vrf definition VRF_SHARED
 rd 65000:99
 route-target export 65000:99
 route-target import 65000:99
 ! Importer la VRF PROD pour permettre le retour
 route-target import 65000:10

```

---

## 4. Protocole de Routage VRF-Aware

Lorsqu'un protocole de routage dynamique (OSPF, BGP, EIGRP) s'exécute sur un routeur possédant des VRF, le processus de routage doit être configuré de manière **VRF-Aware** (conscient des VRF).

### Exemple avec OSPF (Multi-Instance)

Pour isoler les tables OSPF de deux clients différents, on instancie des processus OSPF séparés ou associés à chaque VRF :

```
! Instance OSPF pour la VRF PRODUCTION
router ospf 10 vrf VRF_PROD
 router-id 1.1.1.1
 network 10.10.0.0 0.0.255.255 area 0
!
! Instance OSPF pour la VRF GUEST
router ospf 20 vrf VRF_GUEST
 router-id 2.2.2.2
 network 172.16.0.0 0.0.255.255 area 0

```

---

## 5. Dépannage et Commandes Intermédiaires

Lors du diagnostic d'un réseau VRF-Lite, **toutes les commandes d'inspection classiques doivent spécifier la VRF ciblée** :

### 1. Inspection des interfaces et de leur attribution VRF
```
show vrf
show ip interface brief | include VRF_PROD

```

### 2. Validation des tables d'adresses MAC et ARP par VRF
```
show ip arp vrf VRF_PROD

```

### 3. Analyse du comportement du routage
```
show ip route vrf VRF_PROD
show ip ospf 10 vrf VRF_PROD neighbor

```

### 4. Outils de test d'accessibilité (Ping & Traceroute)
```
! Toujours préciser le nom de la VRF d'origine !
ping vrf VRF_PROD 10.10.1.254
traceroute vrf VRF_PROD 10.10.1.254

```

---

## 6. Synthèse des Concepts Intermédiaires

1. **VRF-Lite :** Transport de plusieurs VRF sur des liens physiques partagés à l'aide de VLANs (Trunking 802.1Q) sans nécessiter MPLS.
2. **RD (Route Distinguisher) :** Garantit l'unicité d'une route IP dans un environnement multi-tenant.
3. **RT (Route Target) :** Définit les règles d'importation et d'exportation de routes entre différentes VRF.
4. **Route Leaking :** Technique permettant à deux VRF distinctes d'échanger des préfixes spécifiques pour accéder à des services partagés.