# Cours intensif : Architecture Spine‑Leaf  
**Niveau : Administrateur Réseau Senior (CCIE)**  
**Durée estimée** : 2 jours (16 h) – 10 000 + caractères  

---  

## Table des matières  
1. [Introduction & objectifs](#introduction)  
2. [Principes fondamentaux du modèle Spine‑Leaf](#principes)  
3. [Comparaison avec l’architecture « Three‑Tier » traditionnelle](#comparaison)  
4. [Dimensionnement & calcul de la capacité](#dimensionnement)  
5. [Choix du matériel (Cisco, Arista, Juniper, Linux‑based)](#materiel)  
6. [Protocoles de transport et de contrôle](#protocoles)  
7. [Plan de câblage & topologie physique (ASCII diagrammes)](#cablage)  
8. [Configuration de base – Cisco NX‑OS & IOS‑XR](#config-cisco)  
9. [Configuration de base – Linux (FRR/OVS)](#config-linux)  
10. [Sécurité & segmentation (VXLAN, VLAN, ACL, RP‑filter)](#securite)  
11. [Monitoring & observabilité (Telemetry, Streaming, sFlow, NetFlow)](#monitoring)  
12. [Atelier de dépannage (scénarios & commandes)](#atelier)  
13. [Bonnes pratiques & checklist de mise en production](#bonnespratiques)  
14. [Références & lectures complémentaires](#references)  

---  

<a name="introduction"></a>  
## 1. Introduction & objectifs  

L’architecture **Spine‑Leaf** (ou *Clos*) est aujourd’hui le socle des data‑centers modernes, du cloud public et des environnements hyper‑convergés. Ce cours a pour objectifs :  

| Objectif | Description détaillée |
|----------|-----------------------|
| **Comprendre** | Les raisons fonctionnelles (latence, bande passante, évolutivité) qui ont conduit à l’adoption du modèle Clos. |
| **Dimensionner** | Calculer le nombre optimal de Spine et de Leaf, la densité de ports et le facteur d’oversubscription. |
| **Déployer** | Configurer une pile de commutateurs Spine‑Leaf avec BGP EVPN, VXLAN, et des services de routage. |
| **Sécuriser** | Implémenter les contrôles d’accès, la segmentation réseau et les politiques de micro‑segmentation. |
| **Observer** | Mettre en place la télémétrie, le monitoring et les alertes proactives. |
| **Dépanner** | Identifier et résoudre les pannes classiques (loop, BGP flaps, MTU mismatches, etc.). |

---  

<a name="principes"></a>  
## 2. Principes fondamentaux du modèle Spine‑Leaf  

### 2.1 Topologie en deux niveaux  

```
                +-------------------+   +-------------------+
                |      SPINE 1      |   |      SPINE 2      |
                +-------------------+   +-------------------+
                         |  \               /  |
                         |   \             /   |
                         |    \           /    |
            +------------+-----+-------+-----+------------+
            |            |     |       |     |            |
            |          LEAF 1   LEAF 2   LEAF 3   ...        |
            |            |     |       |     |            |
            +------------+-----+-------+-----+------------+
                         |    /           \    |
                         |   /             \   |
                         |  /               \  |
                +-------------------+   +-------------------+
                |      SPINE N      |   |      SPINE N+1    |
                +-------------------+   +-------------------+
```

* **Leaf** : Point d’accès pour les serveurs, hyper‑visors, appliances, et parfois les routeurs d’agrégation.  
* **Spine** : Backbone purement de commutation/forwarding, aucune connexion leaf‑leaf.  

### 2.2 Caractéristiques clés  

| Caractéristique | Impact | Exemple |
|-----------------|--------|---------|
| **Uniformité du chemin** | Tous les leafs ont le même nombre de sauts (1) vers n’importe quel spine. | Latence prévisible, O(1) pour le calcul de chemin. |
| **Oversubscription contrôlée** | Ratio entre la bande passante de l’accès (leaf‑to‑servers) et la bande passante du backbone (leaf‑to‑spine). | 1:1 pour les environnements performance‑critical, 3:1 ou 5:1 pour les workloads moins sensibles. |
| **Scalabilité horizontale** | Ajout d’un leaf augmente la capacité d’accès sans toucher le backbone. | +48 serveurs en ajoutant un leaf 48‑port. |
| **Redondance** | Chaque leaf possède plusieurs uplinks vers plusieurs spines (généralement 2 ou 4). | En cas de perte d’un spine, le trafic bascule sans perte de connectivité. |
| **Séparation du plan de données et de contrôle** | BGP EVPN gère le contrôle (MAC/IP) tandis que le plan de données utilise VXLAN/MLAG. | Simplifie le scaling du contrôle (BGP) et du data (fabric). |

---  

<a name="comparaison"></a>  
## 3. Comparaison avec l’architecture « Three‑Tier » traditionnelle  

| Critère | Three‑Tier (Core‑Distribution‑Access) | Spine‑Leaf (Clos) |
|---------|----------------------------------------|-------------------|
| **Nombre de sauts** | 3‑4 (Core → Dist → Access) | 2 (Leaf → Spine) |
| **Scalabilité verticale** | Limité par le Core (bande passante agrégée) | Illimitée tant que le nombre de spines est suffisant |
| **Oversubscription** | Souvent 10:1 ou plus dans l’Access | Typiquement 1:1 à 5:1, configurable |
| **Complexité de la configuration** | Multiples protocoles (OSPF, EIGRP, BGP) | BGP EVPN + VXLAN, moins de protocoles |
| **Résilience** | Redondance via HSRP/VRRP + STP | Redondance native (multi‑spine, MLAG) |
| **Coût** | Équipement Core haut de gamme + licences | Nombre plus élevé de commutateurs leaf mais moins cher par port |
| **Adaptabilité au Cloud** | Moins flexible pour le provisioning dynamique | Parfait pour le provisioning via API, SD‑N, Terraform |

---  

<a name="dimensionnement"></a>  
## 4. Dimensionnement & calcul de la capacité  

### 4.1 Formules de base  

1. **Nombre de leaf**  
   \[
   L = \lceil \frac{N_{servers}}{P_{leaf\_servers}} \rceil
   \]  
   où `P_leaf_servers` = nombre de serveurs supportés par un leaf (ex : 48 ports × 0,9 = 43 serveurs).  

2. **Nombre de spine** (minimum)  
   \[
   S_{min} = \lceil \frac{U_{leaf\_uplink}}{P_{spine\_ports}} \rceil
   \]  
   où `U_leaf_uplink` = uplinks par leaf (ex : 4 × 100 Gbps) et `P_spine_ports` = ports disponibles sur chaque spine.  

3. **Oversubscription Ratio (OSR)**  
   \[
   OSR = \frac{P_{leaf\_servers} \times BW_{server}}{U_{leaf\_uplink} \times BW_{spine}}
   \]  

### 4.2 Exemple de dimensionnement  

| Paramètre | Valeur |
|-----------|--------|
| Serveurs total | 2 400 |
| Ports serveur par leaf | 48 (40 % réservés) → 28 serveurs/leaf |
| Uplinks leaf → spine | 4 × 100 Gbps |
| Ports spine disponibles | 64 (48 × 100 Gbps + 16 × 40 Gbps) |
| Bande passante serveur | 25 Gbps (10 GbE × 2.5) |

**Calcul du nombre de leaf**  
\[
L = \lceil 2400 / 28 \rceil = 86\; \text{leafs}
\]

**Calcul du nombre de spine (minimum)**  
\[
U_{leaf\_uplink}=86 \times 4 = 344\; \text{uplinks}
\]  
\[
S_{min} = \lceil 344 / 48 \rceil = 8\; \text{spines}
\]  

**OSR**  
\[
OSR = \frac{28 \times 25}{4 \times 100}= \frac{700}{400}=1.75:1
\]  

=> **Oversubscription 2:1** (acceptable pour la plupart des workloads).  

### 4.3 Redondance & tolérance aux pannes  

| Scénario | Impact sur la capacité | Méthode de mitigation |
|----------|------------------------|-----------------------|
| Perte d’un spine | Réduction du bandwidth de 12,5 % (1/8) | Provisionner **spine + 1** (ex : 9 spines) pour garder > 85 % de capacité. |
| Perte d’un leaf | Aucun impact sur le backbone, perte des serveurs attachés | **MLAG** ou **vPC** entre deux leafs pour agrégation de serveurs critiques. |
| Lien uplink défaillant | BGP ré‑convergence (fast‑failover) | **BFD** (Bidirectional Forwarding Detection) < 50 ms. |

---  

<a name="materiel"></a>  
## 5. Choix du matériel  

| Vendor | Modèle | Ports (type) | OS | Licence EVPN | TLDR |
|--------|--------|--------------|----|--------------|------|
| Cisco | Nexus 93180YC‑FX2 | 48 × 10/25 GbE + 6 × 100 GbE | NX‑OS 9.x | Oui (L2/L3 EVPN) | Idéal pour data‑center hybride, intégration ACI possible |
| Cisco | Nexus 9508 | 8 × 100 GbE + 4 × 40 GbE | NX‑OS 10.x | Oui (L2/L3 EVPN) | Spine haute densité, support 400 GbE futur |
| Arista | 7280R2 | 48 × 10/25 GbE + 6 × 100 GbE | EOS | Oui (EVPN) | Très bon pour Cloud‑native, eAPI & Ansible |
| Juniper | QFX5200 | 48 × 10/25 GbE + 6 × 100 GbE | Junos | Oui (EVPN) | Compatibilité avec Contrail, bonne automatisation |
| Linux‑based | Cumulus Linux on Dell S6000 | 48 × 10 GbE + 6 × 100 GbE | Debian‑based | Oui (FRR) | Flexibilité, coût OPEX réduit, idéal pour dev‑ops |

**Critères de sélection**  

- **Scalabilité du control plane** : BGP EVPN doit pouvoir gérer > 10 000 routes.  
- **Support de l’automatisation** : NETCONF/YANG, eAPI, Ansible modules.  
- **Licence** : Vérifier la nécessité d’une licence “L2/L3 EVPN” ou “VXLAN”.  
- **Performance du data plane** : ASIC ≥ 2 Tbps, latence < 250 ns.  

---  

<a name="protocoles"></a>  
## 6. Protocoles de transport et de contrôle  

| Couche | Protocole | Rôle | Config de base (Cisco) |
|--------|-----------|------|------------------------|
| **Data‑plane** | VXLAN (VNI) | Encapsulation L2 over L3 | `interface nve1` → `member vni 5000 associate-vrf default` |
| **Control‑plane** | BGP EVPN (AFI = l2vpn‑evpn) | Distribution MAC/IP, VNI, ARP suppression | `router bgp 65001` → `address-family l2vpn evpn` |
| **Routing** | IBGP (full‑mesh) ou **BGP‑RR** | Propagation des routes EVPN entre spines | `router bgp 65001` → `neighbor 10.0.0.2 remote-as 65001` |
| **Transport** | MP‑BGP (TCP 443) | Transport fiable du contrôle EVPN | `bgp log-neighbor-changes` |
| **Détection de panne** | BFD | Fast‑failover sur les liens leaf‑spine | `bfd interval 50 min_rx 50 multiplier 3` |
| **Sécurité** | MACsec, IPsec | Chiffrement du data‑plane (optionnel) | `macsec` sous interface Ethernet |
| **Gestion** | NETCONF/YANG, gNMI | Provisionning programmatique | `netconf-yang` sur le switch |

### 6.1 Pourquoi BGP EVPN ?  

- **Scalabilité** : un seul protocole (BGP) gère le plan de contrôle, évite le besoin de STP, LACP.  
- **Multipathing** : support natif de ECMP (up to 64 equal‑cost paths).  
- **Séparation du contrôle** : le leaf ne dépend pas du spine pour la table MAC.  
- **Interopérabilité** : fonctionne sur tout matériel supportant le standard IETF.  

---  

<a name="cablage"></a>  
## 7. Plan de câblage & topologie physique  

### 7.1 Schéma ASCII de câblage 4‑spine / 8‑leaf  

```
                +-------------------+      +-------------------+
                |      SPINE 1      |      |      SPINE 2      |
                +-------------------+      +-------------------+
                       |   |   |   |            |   |   |   |
                       |   |   |   |            |   |   |   |
                +------+------+------+   +------+------ +------+
                |      |      |      |   |      |      |      |
                |  L1  |  L2  |  L3  |   |  L4  |  L5  |  L6  |
                +------+------+------+   +------+------ +------+
                       |   |   |   |            |   |   |   |
                       |   |   |   |            |   |   |   |
                +-------------------+      +-------------------+
                |      SPINE 3      |      |      SPINE 4      |
                +-------------------+      +-------------------+
```

- **Chaque leaf (L1‑L8)** possède **4 uplinks** vers **tous les spines** (full‑mesh).  
- **Câbles** :  
  - **Leaf‑Spine** : QSFP‑28 × 100 GbE (ou 400 GbE selon futur).  
  - **Leaf‑Server** : SFP‑28 × 25 GbE (ou 10 GbE).  
- **Gestion du câble** : Utiliser des **cassettes de gestion (cable trays)** pour éviter les croisements et faciliter le **patch‑panel**.  

### 7.2 Exemple de plan de câblage avec étiquetage  

| Câble | Origine | Destination | Port Origine | Port Dest. | Type |
|-------|---------|-------------|--------------|------------|------|
| C01 | Leaf‑01 | Spine‑01 | Ethernet1/1 | Ethernet1/1 | QSFP‑28 100 GbE |
| C02 | Leaf‑01 | Spine‑02 | Ethernet1/2 | Ethernet1/1 | QSFP‑28 |
| C03 | Leaf‑01 | Spine‑03 | Ethernet1/3 | Ethernet1/1 | QSFP‑28 |
| C04 | Leaf‑01 | Spine‑04 | Ethernet1/4 | Ethernet1/1 | QSFP‑28 |
| … | … | … | … | … | … |
| C33 | Leaf‑08 | Spine‑01 | Ethernet1/1 | Ethernet1/8 | QSFP‑28 |
| C34 | Leaf‑08 | Spine‑02 | Ethernet1/2 | Ethernet1/8 | QSFP‑28 |
| C35 | Leaf‑08 | Spine‑03 | Ethernet1/3 | Ethernet1/8 | QSFP‑28 |
| C36 | Leaf‑08 | Spine‑04 | Ethernet1/4 | Ethernet1/8 | QSFP‑28 |

*Conserver un **tableau d’inventaire** à jour dans un système ITSM (ex : ServiceNow) pour le suivi des changements.*  

---  

<a name="config-cisco"></a>  
## 8. Configuration de base – Cisco NX‑OS & IOS‑XR  

### 8.1 Prérequis  

- Version NX‑OS ≥ 9.3(3) (support EVPN).  
- Licence « LAN Base » + « Enterprise Services » (pour VXLAN).  

### 8.2 Configuration d’un **Leaf** (ex : Nexus 93180YC‑FX2)  

```text
!--- Global -----------------------------------------------------------------
feature bgp
feature ospf
feature interface-vlan
feature nv overlay
feature vn-segment-vlan-based
feature evpn
feature bfd

!--- NVE (VXLAN) ------------------------------------------------------------
interface nve1
  no shutdown
  source-interface loopback0
  member vni 