# Cours intensif : MPLS & VRF  
**Niveau** : Administrateur Réseau Senior (CCIE‑Ready)  
**Durée estimée** : 2 jours (16 h) – atelier pratique inclus  

---

## Table des matières
| # | Chapitre | Description |
|---|----------|-------------|
| 1 | Introduction & concepts de base | Historique, objectifs, terminologie |
| 2 | Architecture MPLS | Plan de données, plan de contrôle, composants |
| 3 | Distribution d’étiquettes | LDP, RSVP‑TE, BGP‑EVPN, segment routing |
| 4 | Forwarding MPLS | Table de commutation (LFIB), PHP, Penultimate Hop Popping |
| 5 | MPLS‑L3VPN (VRF‑Lite vs VRF‑VPN) | Modèle de service, BGP/MPLS IP VPN |
| 6 | VRF (Virtual Routing and Forwarding) | Concepts, isolation, route‑leaking |
| 7 | Configuration Cisco IOS/IOS‑XR/NX‑OS | Exemples complets, bonnes pratiques |
| 8 | Configuration Juniper (Junos) | Exemples, comparaison |
| 9 | Implémentation Linux (FRR, BIRD, VPP) | Lab, exemples de scripts |
|10 | Comparaison des technologies | Tableau récapitulatif |
|11 | Design & dimensionnement | Scalabilité, redondance, sécurité |
|12 | QoS & Traffic Engineering | MPLS‑TE, Fast Reroute, DiffServ |
|13 | Atelier de dépannage | Scénario, méthodologie, commandes, check‑list |
|14 | Annexes | Glossaire, références, exercices supplémentaires |

> **Objectif** : Maîtriser la conception, le déploiement, l’optimisation et le dépannage d’environnements MPLS et VRF complexes, en s’appuyant sur des configurations réelles (Cisco, Juniper, Linux) et des scénarios d’ingénierie de trafic.

---

## 1. Introduction & concepts de base  

| Concept | Définition | Pourquoi c’est important |
|---------|------------|--------------------------|
| **MPLS (Multiprotocol Label Switching)** | Technique de commutation basée sur des **étiquettes** (labels) plutôt que sur l’adresse IP. | Permet le **forwarding rapide**, le **traffic engineering** et la **segmentation** de services (VPN, L2VPN, L3VPN). |
| **VRF (Virtual Routing and Forwarding)** | Table de routage logique isolée au sein d’un même routeur. | Fournit **l’isolation de tables de routage** (multi‑tenant) sans matériel supplémentaire. |
| **L3VPN** | Service VPN de couche 3 basé sur MPLS + BGP. | Permet à plusieurs clients d’avoir leurs propres tables de routage sur le même backbone. |
| **L2VPN** | Service VPN de couche 2 (VPLS, VPWS). | Transport transparent de trames Ethernet sur MPLS. |
| **TE (Traffic Engineering)** | Optimisation du chemin des flux selon la capacité, la latence, la politique. | Utilisé pour éviter la congestion et garantir la SLA. |

### 1.1 Historique rapide
- **1997‑1999** : Définition initiale (RFC 3031).  
- **2000‑2005** : Adoption massive par les fournisseurs (IP‑VPN, L2VPN).  
- **2006‑2015** : Introduction de **RSVP‑TE**, **Segment Routing (SR‑MPLS)**.  
- **2016‑2024** : Convergence avec **SD‑WAN**, **Network Automation (Ansible, Nornir)**, **Service Mesh**.

---

## 2. Architecture MPLS  

```
+----------------------+      +----------------------+      +----------------------+
|   PE (Provider Edge) |------|   P (Provider)       |------|   PE (Provider Edge) |
|  (VRF + CE)          |      |  (Core MPLS)         |      |  (VRF + CE)          |
+----------------------+      +----------------------+      +----------------------+

Plan de contrôle : IGP (OSPF/IS‑IS) + BGP + LDP/RSVP‑TE
Plan de données   : LFIB (Label Forwarding Information Base)
```

### 2.1 Composants clés
| Élément | Rôle | Protocoles associés |
|---------|------|---------------------|
| **PE (Provider Edge)** | Interface client (CE) & réseau MPLS. Gère les VRF. | BGP, LDP/RSVP‑TE, MP‑BGP (VPNv4) |
| **P (Provider)** | Transport pur MPLS, aucune fonction de routage IP. | LDP, RSVP‑TE, IS‑IS/OSPF |
| **CE (Customer Edge)** | Routeur du client, aucune connaissance MPLS. | BGP, OSPF, static |
| **Label Switch Router (LSR)** | Commute les paquets en fonction du label. | LDP/RSVP‑TE, SR‑MPLS |
| **Label Edge Router (LER)** | Entrée/sortie du réseau MPLS, push/pop labels. | LDP/RSVP‑TE, BGP, VRF |

### 2.2 Plan de contrôle vs plan de données
- **Plan de contrôle** construit la **RIB** (Routing Information Base) puis la **FIB** (Forwarding Information Base).  
- **Plan de données** utilise la **LFIB** (Label FIB) dérivée de la FIB + tables d’étiquettes.  

> **Note** : Dans un réseau SR‑MPLS, le **segment identifier (SID)** remplace les labels distribués par LDP/RSVP‑TE.

---

## 3. Distribution d’étiquettes  

### 3.1 LDP (Label Distribution Protocol)  
- **Mode** : *Down‑stream* (label‑binding).  
- **RFC** : 5036.  
- **Fonction** : Distribue un label pour chaque **FEC** (Forwarding Equivalence Class).  

#### 3.1.1 Exemple de configuration LDP (Cisco IOS)

```text
router ospf 1
  network 10.0.0.0 0.0.0.255 area 0
  network 172.16.0.0 0.0.255.255 area 0

mpls ip
mpls label protocol ldp

interface GigabitEthernet0/0
  ip address 10.0.0.1 255.255.255.0
  mpls ip
  mpls label protocol ldp
```

#### 3.1.2 Commandes de vérification

| Commande | Description |
|----------|-------------|
| `show mpls ldp neighbor` | État des pairs LDP. |
| `show mpls forwarding-table` | Table LFIB (labels → nexthop). |
| `show mpls ldp bindings` | Bindings label/FEC. |
| `debug mpls ldp events` | Traces d’évènements LDP. |

---

### 3.2 RSVP‑TE (Resource Reservation Protocol – Traffic Engineering)  

- **Mode** : *Up‑stream* (signalling).  
- **RFC** : 2205, 3209 (TE extensions).  
- **Utilité** : Réserve la bande passante, crée des **LSP** (Label Switched Paths) explicites.  

#### 3.2.1 Exemple de configuration RSVP‑TE (Cisco IOS)

```text
router ospf 1
  router-id 1.1.1.1
  auto-cost reference-bandwidth 1000
  mpls traffic-eng router-id Loopback0
  mpls traffic-eng area 0

interface Loopback0
  ip address 1.1.1.1 255.255.255.255
  mpls ip

interface GigabitEthernet0/0
  ip address 10.0.0.1 255.255.255.0
  mpls traffic-eng tunnels
  mpls ip

! Création d’un LSP explicite
router bgp 65000
  address-family vpnv4 unicast
    neighbor 2.2.2.2 activate
    neighbor 2.2.2.2 route-reflector-client
    neighbor 2.2.2.2 send-community both
    neighbor 2.2.2.2 next-hop-self
    neighbor 2.2.2.2 capability extended-nexthop
    neighbor 2.2.2.2 soft-reconfiguration inbound

! Tunnel TE
interface Tunnel0
  ip unnumbered Loopback0
  tunnel mode mpls traffic-eng
  tunnel destination 2.2.2.2
  tunnel mpls traffic-eng path-option 1 explicit name PATH1
  tunnel mpls traffic-eng bandwidth 1000
```

#### 3.2.2 Commandes de vérification RSVP‑TE

| Commande | Description |
|----------|-------------|
| `show mpls traffic-eng tunnels` | Liste les tunnels TE et leur état. |
| `show mpls rsvp interface` | Statistiques RSVP sur chaque interface. |
| `show mpls rsvp neighbor` | Pairs RSVP et leurs capacités. |
| `show ip ospf traffic` | Vérifie le calcul du poids OSPF (bandwidth). |

---

### 3.3 BGP‑EVPN & SR‑MPLS (option avancée)

| Technologie | Cas d’usage | Avantages |
|-------------|-------------|-----------|
| **BGP‑EVPN** | L2VPN (VxLAN, VPLS) + L3VPN unifié | Scalabilité (BGP), Multi‑homing, MAC learning distribuée. |
| **Segment Routing (SR‑MPLS)** | Simplification du contrôle, élimination du LDP/RSVP | Programmabilité (SID), intégration SD‑N, moins d’état. |

> **Exemple** : injection d’un SID sur un routeur Cisco IOS‑XR  
> `segment-routing global-block 16000 23999`  
> `segment-routing mpls`  
> `interface GigabitEthernet0/0/0/0`  
> `  mpls traffic-eng admin-weight 100`  
> `  segment-routing mpls`  

---

## 4. Forwarding MPLS  

### 4.1 LFIB (Label Forwarding Information Base)

| Champ | Description |
|-------|-------------|
| **Label** | 20‑bit label (0‑1048575). |
| **Incoming label** | Label reçu sur l’interface. |
| **Outgoing label** | Label à pousser (ou POP). |
| **Next‑hop** | Adresse IP du LSR suivant. |
| **Action** | POP, SWAP, PUSH, PHP. |

#### 4.1.1 Exemple de LFIB (Cisco)

```text
show mpls forwarding-table
Label   Prefix                Outgoing Label   Nexthop           Interface
16001   10.0.0.0/24           POP              192.0.2.2        Gi0/0
16002   172.16.0.0/16         SWAP 26001       192.0.2.3        Gi0/1
```

### 4.2 Penultimate Hop Popping (PHP)

- **Principe** : Le **penultimate LSR** retire le label avant d’envoyer le paquet au dernier LSR (LER).  
- **Bénéfice** : Économise une opération de pop sur le LER, réduit la charge CPU.

```
CE1 --> PE1 (push label L1) --> P‑LSR (PHP) --> PE2 (pop) --> CE2
```

### 4.3 MPLS‑IP vs MPLS‑VPN

| Fonction | MPLS‑IP (LDP) | MPLS‑VPN (BGP) |
|----------|--------------|----------------|
| **Étiquette** | 1 label par FEC (IP prefix) | 2 labels (VPN label + transport label) |
| **Isolation** | Pas d’isolation (tout le trafic partage LFIB) | Isolation par VRF, chaque client a son propre VPN label |
| **Scalabilité** | Limité par nombre de FECs | Limité par nombre de VPNv4 routes (BGP) |

---

## 5. MPLS‑L3VPN (VRF‑Lite vs VRF‑VPN)

### 5.1 Modèle VRF‑Lite (sans MPLS)

- **Utilisation** : Petits sites, routeurs de bordure.  
- **Isolation** : Table de routage séparée, mais pas d’étiquetage MPLS.  
- **Limite** : Pas de transport centralisé, pas de TE.

#### 5.1.1 Exemple VRF‑Lite (Cisco)

```text
ip vrf CUSTOMER_A
  rd 65000:100
  route-target export 65000:100
  route-target import 65000:100

interface GigabitEthernet0/1
  ip vrf forwarding CUSTOMER_A
  ip address 10.1.1.1 255.255.255.0

router bgp 65000
  address-family ipv4 vrf CUSTOMER_A
    neighbor 10.1.1.2 remote-as 65001
    neighbor 10.1.1.2 activate
```

### 5.2 Modèle VRF‑VPN (MPLS L3VPN)

- **Composants** : PE‑VRF, MP‑BGP (VPNv4), LDP/RSVP‑TE (transport).  
- **Flux** :  
  1. CE injecte route dans VRF du PE.  
  2. PE exporte route sous forme d’**VPNv4** (RD+IP).  
  3. Les PE échangent les routes via **MP‑BGP**.  
  4. Chaque PE attribue un **VPN label** (per‑VRF) et un **transport label** (LDP).  
  5. Le paquet transite avec deux labels (VPN, transport).  

#### 5.2.1 Diagramme ASCII d’un L3VPN

```
CE1 ---- PE1 (VRF A) ----+---- P‑Core (LDP) ----+---- PE2 (VRF A) ---- CE2
                         |                       |
                         |--- P‑Core (RSVP‑TE) --|
```

#### 5.2.2 Configuration complète (Cisco IOS)

```text
!--- 1. Création du VRF
ip vrf CUSTOMER_A
  rd 65000:100
  route-target export 65000:100
  route-target import 65000:100

!--- 2. Interface CE ↔ PE
interface GigabitEthernet0/0
  ip vrf forwarding CUSTOMER_A
  ip address 10.10.10.1 255.255.255.0

!--- 3. OSPF intra‑VRF (optional)
router ospf 10 vrf CUSTOMER_A
  network 10.10.10.0 0.0.0.255 area 0

!--- 4. BGP MP‑VPN
router bgp 65000
  bgp log-neighbor-changes
  address-family vpnv4 unicast
    neighbor 192.0.2.2 remote-as 65001
    neighbor 192.0.2.2 activate
    neighbor 192.0.2.2 send-community both
    neighbor 192.0.2.2 route-reflector-client
    neighbor 192.0.2.2 next-hop-self
    neighbor 192.0.2.2 soft-reconfiguration inbound
  exit-address-family

!--- 5. Activation du transport MPLS
mpls ip
mpls label protocol ldp
```

#### 5.2.3 Vérifications essentielles

| Commande | Résultat attendu |
|----------|------------------|
| `show ip vrf` | Liste des VRF, RD, RT. |
| `show bgp vpnv4 unicast all` | Routes VPNv4 avec RD. |
| `show mpls forwarding-table vrf CUSTOMER_A` | Labels VPN + transport. |
| `show ip route vrf CUSTOMER_A` | Table de routage isolée. |
| `show mpls ldp neighbor` | Pair LDP fonctionnels. |

---

## 6. VRF (Virtual Routing and Forwarding)  

### 6.1 Principes fondamentaux

| Élément | Fonction |
|---------|----------|
| **RD (Route Distinguisher)** | Unicité globale de la route VPN (ex : `65000:100`). |
| **RT (Route Target)** | Politique d’import/export via BGP (ex : `65000:100`). |
| **VRF‑Lite** | Table de routage locale, aucune diffusion BGP. |
| **VRF‑VPN** | Table de routage distribuée via MP‑BGP (VPNv4). |

### 6.2 Isolation et inter‑VRF

- **Isolation** : Chaque VRF possède sa propre **RIB**, **FIB**, **LFIB**.  
- **Route‑leaking** : Permet d’importer/exporter des routes entre VRFs via des **RT** communs ou via `bgp import-map/export-map`.  

#### 6.2.1 Exemple de route‑leak (Cisco IOS)

```text
! VRF A exporte vers VRF B
router bgp 65000
  address-family ipv4 vrf VRF_A
    neighbor 10.0.0.2 remote-as 65001
    neighbor 10.0.0.2 activate
    neighbor 