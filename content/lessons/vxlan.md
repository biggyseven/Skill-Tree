# Cours Intensif – VXLAN & Datacenter  
**Niveau : Administrateur Réseau Senior (CCIE)**  
**Durée estimée : 2 jours (8 h/jour)**  

---

## Table des matières
1. [Introduction & motivations](#introduction--motivations)  
2. [Principes fondamentaux de VXLAN](#principes-fondamentaux-de-vxlan)  
3. [Architecture & composantes](#architecture--composantes)  
4. [Encapsulation – format du paquet](#encapsulation--format-du-paquet)  
5. [Plan de données vs plan de contrôle](#plan-de-données--vs-plan-de-contrôle)  
6. [VXLAN avec BGP EVPN (le standard de facto)](#vxlan-avec-bgp‑evpn-le-standard-de-facto)  
7. [Modèles de déploiement (L2, L3, Multi‑tenant)](#modèles-de-déploiement)  
8. [Comparaison avec d’autres solutions d’overlay](#comparaison-avec-dautres-solutions-doverlay)  
9. [Implémentations Cisco (NX‑OS, IOS‑XR, IOS‑XE)](#implémentations-cisco)  
10. [Implémentations Linux (OVS, VPP, kernel‑vxlan)](#implémentations-linux)  
11. [Commandes d’administration – Cisco & Linux](#commandes-dadministration)  
12. [Monitoring, collecte de statistiques et logs](#monitoring‑collecte‑de-statistiques-et-logs)  
13. [Atelier de dépannage – Lab pratique](#atelier-de-dépannage)  
14. [Bonnes pratiques & checklist de mise en production](#bonnes-pratiques--checklist)  
15. [Références & lectures complémentaires](#références--lectures-complémentaires)  

---

## 1. Introduction & motivations  

| **Contexte Datacenter moderne** | **Limites des VLAN classiques** | **Objectifs de VXLAN** |
|--------------------------------|----------------------------------|------------------------|
| • 10 000+ serveurs (hyper‑scale) | • 4096 VLANs par domaine broadcast | • Extension L2 au-delà du domaine L3 |
| • Multitenancy & isolation stricte | • Saturation du STP (BPDU storms) | • Scalabilité (16 M VNI) |
| • Cloud hybride & micro‑services | • Difficulté à migrer VM entre sites | • Découplage du plan de contrôle |
| • Besoin d’automatisation (API, SDN) | • Gestion manuelle des trunks | • Support natif des solutions SD‑N (OpenStack, VMware NSX) |

> **Conclusion** : VXLAN répond aux exigences de **scalabilité**, **flexibilité** et **automatisation** tout en conservant la transparence du réseau L2.

---

## 2. Principes fondamentaux de VXLAN  

* **VXLAN** = **V**irtual **e**Xtensible **LAN**.  
* Standardisé par **IETF (RFC 7348)**, complété par **BGP EVPN (RFC 7432)** pour le contrôle.  
* **VNI (VXLAN Network Identifier)** : champ 24 bits → 16 777 216 réseaux virtuels.  
* Fonctionne comme un **overlay** L2 sur un **underlay** IP (IPv4 ou IPv6).  

### 2.1. Terminologie clé  

| Terme | Définition |
|-------|------------|
| **VTEP (VXLAN Tunnel End Point)** | Point d’entrée/sortie du tunnel, généralement un commutateur ou un hyperviseur. |
| **VNI** | Identifiant du réseau virtuel, équivalent au VLAN ID mais 24 bits. |
| **Overlay** | Réseau logique L2 (VXLAN) transporté sur l’underlay IP. |
| **Underlay** | Infrastructure IP (OSPF/ISIS/BGP) qui assure la connectivité L3. |
| **EVPN** | Ethernet VPN, protocole de signalisation BGP pour la découverte des VTEP et la distribution MAC/IP. |
| **Multicast Group** | Adresse IP multicast utilisée (optionnelle) pour la diffusion des BUM (Broadcast, Unknown‑unicast, Multicast). |
| **Head‑End Replication (HER)** | Technique de réplication de BUM sans multicast, via le contrôle BGP‑EVPN. |

---

## 3. Architecture & composantes  

```
+-------------------+          +-------------------+          +-------------------+
|   VTEP (leaf)     |---IP---->|   Underlay Core   |---IP---->|   VTEP (leaf)     |
|  (NX‑OS/OVS)      |          | (BGP/OSPF/ISIS)   |          |  (Linux host)    |
+-------------------+          +-------------------+          +-------------------+

Overlay (VXLAN) : VNI <-> VTEP MAC tables
Underlay (IP)   : IGP/BGP routing tables
```

* **Leaf‑Spine** : Topologie la plus répandue. Les VTEP sont généralement sur les **leaf**.  
* **VTEP‑to‑VTEP** : Chaque VTEP possède une interface **Vxlan0** (ou **nve1** sur NX‑OS).  
* **BGP‑EVPN** : Distribue les **MAC/IP** et les **VNI** entre les VTEP.  

### 3.1. Flux de données typique  

```
+-------------------+          +-------------------+          +-------------------+
| VM A (10.0.0.10)  |          |  VTEP A (nve1)    |          |  VTEP B (nve1)    |
|   MAC AA:AA:AA    |          |  VNI 5000         |          |  VNI 5000         |
+--------+----------+          +--------+----------+          +--------+----------+
         |                               |                               |
         | 1. Ethernet frame (dst MAC BB) |                               |
         |------------------------------->|                               |
         |                               | 2. Lookup VNI → nve1            |
         |                               | 3. Encapsulate VXLAN (VNI 5000) |
         |                               | 4. UDP/IPv4 (dst IP VTEP B)     |
         |                               |------------------------------->|
         |                               |                               |
         |                               | 5. Decapsulate, forward to VM B|
         |                               |<-------------------------------|
         |                               |                               |
```

---

## 4. Encapsulation – format du paquet  

| **Champ** | **Taille** | **Valeur** | **Commentaires** |
|-----------|------------|------------|------------------|
| Destination MAC | 6 octets | MAC du VTEP (ou multicast) | |
| Source MAC | 6 octets | MAC du VTEP source | |
| EtherType | 2 octets | 0x0800 (IPv4) ou 0x86DD (IPv6) | |
| **IP Header** | 20‑40 octets | Src/Dst IP du VTEP | |
| **UDP Header** | 8 octets | Src port 4789 (IANA) <br>Dst port 4789 | |
| **VXLAN Header** | 8 octets | Flags (I‑bit = 1) <br>VNI (24 bits) | |
| **Inner Ethernet** | 14 octets | Original L2 frame | |
| **Payload** | 0‑1500 octets | Original L3/L4 data | |
| **FCS** | 4 octets | CRC Ethernet | (optionnel selon impl.) |

### 4.1. Schéma ASCII du paquet VXLAN  

```
+-------------------+-------------------+-------------------+-------------------+
|   Ethernet (outer) (14 B)          |   IPv4 (20 B)                     |
|   DA = VTEP B MAC                  |   Src = VTEP A IP                |
|   SA = VTEP A MAC                  |   Dst = VTEP B IP                |
+-------------------+-------------------+-------------------+-------------------+
|   UDP (8 B)                         |   VXLAN (8 B)                     |
|   Src port = 4789                  |   Flags = 0x08 (I‑bit)            |
|   Dst port = 4789                  |   VNI = 0x001388 (5000)           |
+-------------------+-------------------+-------------------+-------------------+
|   Inner Ethernet (14 B)             |   Inner payload (≤1500 B)        |
|   DA = VM B MAC                    |   IP/ARP/TCP/UDP …                |
|   SA = VM A MAC                    |                                   |
+------------------------------------+-----------------------------------+
```

---

## 5. Plan de données vs plan de contrôle  

| **Aspect** | **Plan de données** | **Plan de contrôle** |
|------------|---------------------|----------------------|
| **Fonction** | Transport des frames encapsulées (VXLAN) | Découverte des VTEP, distribution des MAC/IP, synchronisation des VNI |
| **Protocoles** | UDP/IP, VXLAN, parfois multicast | BGP EVPN (AFI = L2VPN), OSPF‑BGP, IS‑IS |
| **État** | Stateless (pas de session) | Stateful (BGP sessions) |
| **Scalabilité** | Dépend de la capacité du sous‑réseau IP (MTU) | Dépend du nombre de routes (max ≈ 1 M) |
| **Redondance** | Multipathing IP (ECMP) | BGP multipath, route‑reflectors |
| **Sécurité** | ACLs UDP/4789, IPsec (optionnel) | BGP MD5, TTL security, route‑target filtering |

---

## 6. VXLAN avec BGP EVPN (le standard de facto)

### 6.1. Types de routes EVPN  

| **Route Type** | **Code** | **Objectif** |
|----------------|----------|--------------|
| **Type 1** – Ethernet Auto‑Discovery (AD) | 1 | Découverte VTEP, transport du VNI |
| **Type 2** – MAC/IP Advertisement | 2 | Distribution MAC + IP (ARP) |
| **Type 3** – Inclusive Multicast Ethernet Tag (IMET) | 3 | Distribution des groupes multicast (option HER) |
| **Type 4** – Ethernet Segment (ES) | 4 | Support du Multi‑Home (LAG, MLAG) |
| **Type 5** – IP Prefix | 5 | Distribution de routes IP (L3‑VPN) |
| **Type 6** – IP Prefix + MAC | 6 | L3‑VPN avec service insertion (service chaining) |

### 6.2. Exemple de configuration BGP EVPN sur un **leaf Cisco NX‑OS**  

```text
feature bgp
feature evpn
feature interface-vlan
feature nv overlay

router bgp 65001
  bgp log-neighbor-changes
  address-family evpn
    neighbor 10.0.0.2 remote-as 65002
    neighbor 10.0.0.2 activate
    neighbor 10.0.0.2 route-reflector-client
  exit-address-family

  address-family ipv4 unicast
    redistribute connected
  exit-address-family

vlan 10
  name VXLAN-VMs
  vn-segment 5000
  exit

interface nve1
  no shutdown
  source-interface loopback0
  member vni 5000
    ingress-replication protocol bgp
    exit
```

### 6.3. Flux de découverte MAC avec EVPN  

1. **VM A** envoie ARP → VTEP A encapsule en VXLAN et envoie **Type 2** (MAC/IP) via BGP‑EVPN.  
2. **VTEP B** reçoit la route, apprend MAC = AA:AA:AA, IP = 10.0.0.10 → ajoute à sa table MAC‑VTEP.  
3. **FUTUR** trafic unicast de VM B vers VM A est acheminé directement (unicast VXLAN) sans passer par le contrôle.  

---

## 7. Modèles de déploiement  

| **Modèle** | **Description** | **Cas d’usage** | **Avantages** | **Inconvénients** |
|------------|----------------|-----------------|---------------|-------------------|
| **L2‑Only (single‑tenant)** | Un VNI unique par tenant, pas de routage interne. | Migration VM intra‑datacenter, isolation VLAN‑to‑VXLAN. | Simplicité, aucune redistribution IP. | Pas de routage L3, besoin de sous‑net unique. |
| **L3‑Overlay (EVPN‑L3)** | Chaque VNI possède un SVI (interface VLAN) avec IP. | Segmentation L3, micro‑segmentation, service chaining. | Routage intra‑VXLAN, support du **IP‑VPN**. | Complexité BGP, plus de routes. |
| **Multi‑Tenant (VXLAN‑EVPN)** | Un VNI par tenant, route‑targets (RT) pour isolation. | Cloud public, multi‑customer. | Isolation forte, contrôle granulaire. | Gestion du RT/RT‑import/export. |
| **Hybrid (VXLAN + MPLS)** | VXLAN overlay sur un backbone MPLS (L3VPN). | Inter‑site, migration vers le cloud. | Réutilise l’infrastructure MPLS existante. | Overhead supplémentaire, double encapsulation. |
| **Head‑End Replication (HER)** | Pas de multicast, les BUM sont répliqués par le contrôle. | Datacenters sans support multicast. | Simplicité réseau, pas de groupe multicast. | Charge CPU supplémentaire sur VTEP, trafic de réplication. |

---

## 8. Comparaison avec d’autres solutions d’overlay  

| **Critère** | **VXLAN (BGP‑EVPN)** | **NVGRE** | **Geneve** | **STT** |
|-------------|----------------------|-----------|------------|---------|
| **Standardisation** | IETF RFC 7348 + RFC 7432 | Microsoft (propriétaire) | IETF RFC 8926 | Cisco (propriétaire) |
| **Identifiant réseau** | VNI (24 bits) | VSID (24 bits) | VNI (24 bits) | VNI (24 bits) |
| **Port UDP** | 4789 (IANA) | 6081 | 6081 (default) | 0 (direct Ethernet) |
| **Contrôle** | BGP‑EVPN, OSPF‑EVPN, LISP | Hyper‑V, SCVMM | Extensible (TLVs) | Cisco Fabric |
| **Multicast requis** | Optionnel (HER) | Oui (multicast) | Optionnel | Non |
| **Interopérabilité** | Large (Cisco, Arista, Juniper, OVS) | Limité à Microsoft | En cours d’adoption | Cisco only |
| **Performance** | UDP + checksum, offload possible | UDP, similaire | UDP, extensible | Pas de checksum (faster) |
| **Support de service chaining** | Oui (EVPN‑L3, BGP‑SR) | Limité | Oui (via TLVs) | Oui (Cisco ACI) |

---

## 9. Implémentations Cisco  

### 9.1. NX‑OS (Data Center)  

| **Objet** | **Commande** | **Description** |
|-----------|--------------|-----------------|
| Activer le VxLAN | `feature nv overlay` | Active le module NVE. |
| Créer un VNI | `vlan 10` → `vn-segment 5000` | Associe VLAN 10 → VNI 5000. |
| Configurer NVE | `interface nve1` → `source-interface loopback0` → `member vni 5000` | Déclare le VTEP et le VNI. |
| Ingress‑replication BGP | `member vni 5000` → `ingress-replication protocol bgp` | Utilise BGP‑EVPN pour BUM. |
| BGP‑EVPN | `router bgp 65001` → `address-family evpn` | Contrôle le plan de signalisation. |
| MTU | `system mtu 9216` | Nécessaire pour éviter la fragmentation. |

#### Exemple complet (leaf)  

```text
!--- System ---
hostname leaf01
feature interface-vlan
feature nv overlay
feature bgp
feature evpn
system mtu 9216

!--- Loopback pour NVE ---
interface loopback0
  ip address 10.0.0.1/32
  no shutdown

!--- VLAN & VNI ---
vlan 10