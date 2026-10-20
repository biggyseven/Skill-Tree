# Cours Intensif – VRF (Virtual Routing and Forwarding)  
**Niveau : Administrateur Réseau Senior / CCIE**  

---  

## 1. Introduction & Objectifs du cours  

| Objectif | Détail |
|----------|--------|
| **Comprendre** | Principes fondamentaux du VRF, séparation de tables de routage, isolation L3. |
| **Maîtriser** | Configuration VRF sur les plateformes Cisco (IOS, IOS‑XE, IOS‑XR, NX‑OS) et Linux. |
| **Intégrer** | VRF dans des architectures MPLS L3VPN, EVPN, VxLAN, Service‑Based Routing. |
| **Diagnostiquer** | Méthodologie de dépannage avancée (symptômes, outils, analyse de paquets). |
| **Optimiser** | Scalabilité, performance, sécurité et bonnes pratiques de conception. |

À l’issue de ce cours, vous serez capable de concevoir, déployer et dépanner des environnements multi‑VRF complexes, y compris le **route‑leaking**, les **VRF‑aware services** et les **VRF‑Lite** sur Linux.

---  

## 2. Concepts de base  

### 2.1 Définition  

- **VRF** = Virtual Routing and Forwarding.  
- Chaque VRF possède sa **table de routage indépendante**, ses **interfaces** (physiques ou logiques) et son **instance de processus de contrôle** (RIB/FIB).  
- Le **data plane** utilise le **VRF ID (ou table‑ID)** pour sélectionner la FIB adéquate.  

### 2.2 Pourquoi VRF ?  

| Besoin | Solution VRF |
|--------|--------------|
| Isolation du trafic client | Table de routage séparée → aucun chevauchement d’adresses IP. |
| Multi‑tenant (datacenter) | Chaque locataire possède son propre VRF, même si les adresses se chevauchent. |
| Sécurité & conformité | Filtrage de trafic au niveau L3 sans ACL globales. |
| Simplification du design | Pas besoin de sous‑interfaces VLAN‑aware sur chaque routeur. |
| Support de services multiples (DHCP, NAT, QoS) | Services peuvent être **VRF‑aware**. |

### 2.3 Terminologie  

| Terme | Signification |
|-------|----------------|
| **VRF‑Lite** | Implémentation VRF sur des routeurs/commutateurs non‑MPLS (IOS, NX‑OS). |
| **VRF‑Aware** | Service (DHCP, DNS, NAT, etc.) qui fonctionne dans le contexte d’une VRF. |
| **VRF‑Target** | Identifiant (RT) utilisé dans MPLS L3VPN pour associer les VRF aux VPN‑vRFs. |
| **Route Distinguisher (RD)** | Préfixe unique (ex : 65000:100) qui rend chaque VPN‑vRF unique dans le réseau MPLS. |
| **Route Target (RT)** | Attribut BGP utilisé pour le **import/export** des routes entre VRF. |
| **VRF‑Leak** | Partage sélectif de routes entre deux VRFs (via import/export ou static). |
| **VNI** | Virtual Network Identifier (VXLAN) – peut être associé à une VRF. |

---  

## 3. Architecture du VRF  

### 3.1 Vue d’ensemble (ASCII)  

```
+-------------------+        +-------------------+
|   VRF A (Table A) |        |   VRF B (Table B) |
|  RIB/FIB A        |        |  RIB/FIB B        |
+---------+---------+        +---------+---------+
          |                          |
   +------v------+            +------v------+
   |  Interface  |            |  Interface  |
   |  (Gig0/0)   |            |  (Gig0/1)   |
   +------+------|            +------+------+
          |                          |
          +-----------+--------------+
                      |
               +------v------+
               |  Physical   |
               |  Switch/    |
               |  Router     |
               +-------------+
```

- Chaque **interface** appartient à **une seule VRF** (ou à la VRF `global`).  
- Le **lookup** du routeur se fait d’abord par **VRF ID** → **RIB** → **FIB** → **output interface**.  

### 3.2 Data‑Plane vs Control‑Plane  

| Couche | Fonction | Impact VRF |
|--------|----------|------------|
| **Control‑Plane** | BGP, OSPF, EIGRP, IS‑IS, static routes. | Chaque protocole possède une instance par VRF (ex : `router bgp 65000 vrf VRF_A`). |
| **Data‑Plane** | Forwarding des paquets. | Le champ **VRF‑ID** (ou **table‑ID**) est ajouté au header (MPLS label, VNI, ou Linux netns). |
| **Management‑Plane** | CLI, SNMP, NetConf. | Les commandes sont préfixées par `vrf name`. Les MIBs sont séparés (`CISCO‑VRF‑MIB`). |

---  

## 4. Implémentations Cisco  

### 4.1 IOS / IOS‑XE (VRF‑Lite)  

#### 4.1.1 Création d’une VRF  

```text
conf t
 ip vrf VRF_A
  rd 65000:100
  route-target import 65000:100
  route-target export 65000:100
  description Client_A_VRF
 exit
!
 ip vrf VRF_B
  rd 65000:200
  route-target import 65000:200
  route-target export 65000:200
  description Client_B_VRF
 exit
```

#### 4.1.2 Association d’interfaces  

```text
interface GigabitEthernet0/0
 description Link to Client_A
 ip vrf forwarding VRF_A
 ip address 10.1.0.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 description Link to Client_B
 ip vrf forwarding VRF_B
 ip address 10.1.0.1 255.255.255.0
 no shutdown
```

> **Note** : Les deux interfaces peuvent partager la même sous‑réseau IPv4 car elles sont isolées par VRF.

#### 4.1.3 Protocoles de routage par VRF  

```text
router ospf 1 vrf VRF_A
 network 10.1.0.0 0.0.0.255 area 0
!
router ospf 1 vrf VRF_B
 network 10.1.0.0 0.0.0.255 area 0
```

#### 4.1.4 Route‑leaking (static)  

```text
ip route vrf VRF_A 0.0.0.0 0.0.0.0 GigabitEthernet0/0 10.1.0.2 name DEFAULT_A
ip route vrf VRF_B 0.0.0.0 0.0.0.0 GigabitEthernet0/1 10.1.0.2 name DEFAULT_B
```

### 4.2 IOS‑XR (VRF‑Aware MPLS)  

#### 4.2.1 Définition d’un VRF‑Lite (XR)  

```text
vrf VRF_A
 address-family ipv4 unicast
  import route-target 65000:100
  export route-target 65000:100
  rd 65000:100
  !
 exit-address-family
!
vrf VRF_B
 address-family ipv4 unicast
  import route-target 65000:200
  export route-target 65000:200
  rd 65000:200
 exit-address-family
```

#### 4.2.2 Association d’interfaces  

```text
interface GigabitEthernet0/0/0/0
 description To Client A
 ipv4 address 10.1.0.1 255.255.255.0
 vrf forwarding VRF_A
!
interface GigabitEthernet0/0/0/1
 description To Client B
 ipv4 address 10.1.0.1 255.255.255.0
 vrf forwarding VRF_B
```

#### 4.2.3 BGP VPNv4 (MPLS L3VPN)  

```text
router bgp 65000
 address-family vpnv4 unicast
  neighbor 192.0.2.2 activate
  neighbor 192.0.2.2 send-community both
 exit-address-family
!
router bgp 65000
 address-family ipv4 unicast vrf VRF_A
  redistribute ospf 1
 exit-address-family
!
router bgp 65000
 address-family ipv4 unicast vrf VRF_B
  redistribute ospf 1
 exit-address-family
```

### 4.3 NX‑OS (Data‑Center)  

#### 4.3.1 Création d’une VRF  

```text
vrf context VRF_A
  description Tenant A
  rd 65000:100
  address-family ipv4 unicast
    route-target import 65000:100
    route-target export 65000:100
  exit-address-family
!
vrf context VRF_B
  description Tenant B
  rd 65000:200
  address-family ipv4 unicast
    route-target import 65000:200
    route-target export 65000:200
  exit-address-family
```

#### 4.3.2 Interfaces & VLANs  

```text
interface Ethernet1/1
  description Link to Tenant A
  switchport mode trunk
  switchport trunk allowed vlan 10
  vrf member VRF_A
!
interface Ethernet1/2
  description Link to Tenant B
  switchport mode trunk
  switchport trunk allowed vlan 20
  vrf member VRF_B
```

#### 4.3.3 OSPFv3 (IPv6) dans une VRF  

```text
router ospfv3 1 vrf VRF_A
  router-id 1.1.1.1
  area 0.0.0.0
    interface Ethernet1/1
!
router ospfv3 1 vrf VRF_B
  router-id 2.2.2.2
  area 0.0.0.0
    interface Ethernet1/2
```

---  

## 5. Implémentation Linux (VRF‑Lite)  

### 5.1 Concepts  

- **netns** (network namespace) = isolement du stack réseau.  
- **ip vrf** (utilitaire `iproute2`) crée un **table‑id** et associe les interfaces.  
- **VRF‑FD** (Forwarding‑Domain) pour les services VRF‑aware (e.g., `dhcpd -cf /etc/dhcp/dhcpd.conf -lf /var/lib/dhcp/dhcpd.leases -pf /var/run/dhcpd.pid -user dhcp -group dhcp -4 -6 -pf /run/dhcpd.pid -cf /etc/dhcp/dhcpd.conf -sf /usr/libexec/dhcpd-script -s /run/dhcpd.sock -VVRF_A`).  

### 5.2 Création d’une VRF  

```bash
# Crée la table de routage 100 pour VRF_A
sudo ip link add VRF_A type vrf table 100
sudo ip link set dev VRF_A up

# Crée la table de routage 200 pour VRF_B
sudo ip link add VRF_B type vrf table 200
sudo ip link set dev VRF_B up
```

### 5.3 Association d’interfaces physiques  

```bash
# Associer eth0 à VRF_A
sudo ip link set dev eth0 master VRF_A
sudo ip addr add 10.1.0.2/24 dev eth0
sudo ip link set dev eth0 up

# Associer eth1 à VRF_B
sudo ip link set dev eth1 master VRF_B
sudo ip addr add 10.1.0.2/24 dev eth1
sudo ip link set dev eth1 up
```

### 5.4 Routage dynamique (OSPF via FRR)  

*Fichier `/etc/frr/daemons`*  

```text
ospfd=yes
```

*Fichier `/etc/frr/ospfd.conf`*  

```text
router ospf
  vrf VRF_A
    network 10.1.0.0/24 area 0.0.0.0
  vrf VRF_B
    network 10.1.0.0/24 area 0.0.0.0
```

Redémarrez FRR : `systemctl restart frr`.

### 5.5 Services VRF‑Aware (DHCP)  

```bash
# DHCP server pour VRF_A (exemple avec isc‑dhcp-server)
sudo dhcpd -cf /etc/dhcp/dhcpd-VRF_A.conf -pf /run/dhcpd-VRF_A.pid -user dhcp -group dhcp -4 -6 -VVRF_A
```

Le fichier `dhcpd-VRF_A.conf` contiendra les pools spécifiques à la VRF.

---  

## 6. VRF dans un réseau MPLS L3VPN  

### 6.1 Architecture logique  

```
+-------------------+      +-------------------+      +-------------------+
|   CE (VRF A)      |------|   PE (VRF A)      |------|   P (MPLS core)   |
| 10.1.0.0/24       |      |  rd 65000:100     |      |  label-switched   |
+-------------------+      +-------------------+      +-------------------+

+-------------------+      +-------------------+      +-------------------+
|   CE (VRF B)      |------|   PE (VRF B)      |------|   P (MPLS core)   |
| 10.1.0.0/24       |      |  rd 65000:200     |      |  label-switched   |
+-------------------+      +-------------------+      +-------------------+
```

- **PE** possède plusieurs **VRF‑Lite** (ou **VRF‑VFI**) chacune avec un **RD** unique.  
- **BGP VPNv4** transporte les **VPN‑IP** (RD + prefix) à travers le réseau MPLS.  

### 6.2 Configuration BGP VPNv4 (exemple Cisco IOS‑XE)  

```text
router bgp 65000
 bgp log-neighbor-changes
 neighbor 192.0.2.2 remote-as 65001
 neighbor 192.0.2.2 activate
 neighbor 192.0.2.2 send-community both
 !
 address-family vpnv4
  neighbor 192.0.2.2 activate
 exit-address-family
!
address-family ipv4 vrf VRF_A
  redistribute ospf 1
 exit-address-family
!
address-family ipv4 vrf VRF_B
  redistribute ospf 1
 exit-address-family
```

### 6.3 Import/Export via Route‑Target  

| VRF | Import‑RT | Export‑RT |
|-----|-----------|-----------|
| **VRF_A** | 65000:100 | 65000:100 |
| **VRF_B** | 65000:200 | 65000:200 |

*Pour partager des routes entre VRF_A et VRF_B, ajoutez un RT commun* :  

```text
vrf definition VRF_A
 rd 65000:100
 route-target import 65000:100 65000:300
 route-target export 65000:100 65000:300
!
vrf definition VRF_B
 rd 65000:200
 route-target import 65000:200 65000:300
 route-target export 65000:200 65000:300
```

Le **RT 300** devient le **bridge‑RT** pour le leaking.

---  

## 7. Services VRF‑Aware  

| Service | Implémentation Cisco | Implémentation Linux |
|---------|----------------------|----------------------|
| **DHCP** | `ip dhcp pool VRF_A` + `ip dhcp vrf VRF_A` | `dhcpd -VVRF_A` |
| **NAT** | `ip nat inside source list 10 interface Gig0/0 vrf VRF_A overload` | `iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE` (dans netns) |
| **QoS** | `policy-map PM_VRF_A` + `class-map` + `service-policy` (appliqué sous `vrf`) | `tc qdisc add dev eth0 root handle 1: htb` (dans netns) |
| **ACL** | `ip access-list extended ACL_VRF_A` + `ip access-group ACL_VRF