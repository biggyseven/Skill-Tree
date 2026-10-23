# Virtual Routing and Forwarding (VRF) : Architecture Avancée, MPLS L3VPN et EVPN/VXLAN

Ce document d'expertise traite des architectures VRF avancées, de leur mécanique interne au sein du plan de contrôle et de données, du fonctionnement des MPLS L3VPN (RFC 4364), de leur intégration dans les fabriques moderne Data Center (BGP-EVPN / VXLAN) ainsi que des techniques complexes de fuite de routes et d'ingénierie de trafic.

---

## 1. Architecture Système & Séparation des Plans (Control vs Data Plane)

Dans un système d'exploitation réseau moderne (Cisco IOS-XE/NX-OS, Arista EOS, Juniper JunOS), une VRF n'est pas simplement une sous-table de routage : il s'agit d'une **instance virtuelle d'instanciation de pile réseau** comprenant ses propres structures de données de plan de contrôle et de plan de transfert matériel (*Data Plane*).

```
                  ┌────────────────────────────────────────────────────────┐
                  │               PROCESSUS DU PLAN DE CONTRÔLE             │
                  │  ┌───────────────────────┐   ┌───────────────────────┐ │
                  │  │     RIB Global          │   │      RIB VRF_A        │ │
                  │  │ (OSPF/BGP Process 1)  │   │ (OSPF/BGP Process 10) │ │
                  │  └───────────┬───────────┘   └───────────┬───────────┘ │
                  └──────────────┼───────────────────────────┼─────────────┘
                                 │                           │
  ───────────────────────────────┼───────────────────────────┼───────────────────────────────
                                 ▼                           ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                 PLAN DE TRANSFERT (FIB / ASIC)         │
                  │  ┌───────────────────────┐   ┌───────────────────────┐ │
                  │  │  Global TCAM / FIB    │   │   VRF_A TCAM / FIB    │ │
                  │  │  (Table de Adjacence) │   │  (Table de Adjacence) │ │
                  │  └───────────────────────┘   └───────────────────────┘ │
                  └────────────────────────────────────────────────────────┘
```

### 1.1 Structures de Données Matérielles (TCAM & FIB)

* **RIB (Routing Information Base) :** Chaque VRF possède sa propre instance RIB isolee de la table globale (*Default/Global Table*). Les processus de routage dynamique (BGP, OSPF, IS-IS, EIGRP) s'exécutent dans des espaces mémoire isolés ou au sein de contextes VRF dédiés.
* **FIB (Forwarding Information Base) :** Pour permettre la commutation à la vitesse de la ligne (*Line Rate*), la FIB globale est partitionnée logiquement ou matériellement.
* **TCAM (Ternary Content Addressable Memory) :** Les Lookups L3 sont préfixés par un **VRF-ID** interne (un identifiant numérique sur 12 ou 16 bits attribué localement par le système). L'ASIC de commutation effectue la recherche dans la TCAM sous la forme `[VRF-ID + IP Destination]`.

---

## 2. Les Fondations des VPN MPLS L3 (RFC 4364 / PEP-CE Mechanics)

En environnement opérateur ou backbone d'entreprise, la VRF ne reste pas isolée à un seul équipement : elle s'étend à travers un réseau cœur MPLS via le protocole **MP-BGP** (*Multi-Protocol BGP*).

### 2.1 La Chaîne de Composants : PE, CE, P

* **CE (Customer Edge) :** Équipement client (ou de couche d'accès) non conscient de MPLS. Il parle IP standard avec le PE.
* **PE (Provider Edge) :** Équipement frontière. Il héberge les VRF, maintient les sessions MP-BGP et effectue l'encapsulation de labels MPLS.
* **P (Provider Core) :** Routeur de cœur de réseau. Il ne possède **aucune connaissance des VRF clients**. Il commute uniquement des labels MPLS (LDP ou Segment Routing).

### 2.2 Format VPNv4 et Identifiants MP-BGP

Lorsqu'une route privée $10.0.0.0/24$ est injectée dans une VRF sur un PE, elle doit être transportée par le cœur de réseau sans entrer en collision avec la même plage IP $10.0.0.0/24$ appartenant à un autre client.

#### 1. Route Distinguisher (RD) - 8 Octets (64 bits)
Le RD est concaténé devant le préfixe IPv4 (32 bits) pour créer une adresse **VPNv4 à 96 bits**.

$$\text{Format VPNv4} = \underbrace{\text{Route Distinguisher (64 bits)}}_{\text{Type (16) + Admin (16/32) + Assigned (32/16)}} \,+\, \underbrace{\text{Préfixe IPv4 (32 bits)}}_{\text{ex: 10.0.0.0/24}}$$

* *Structure Type 0 :* `2-octet ASN : 4-octet value` (ex: `65000:100`)
* *Structure Type 1 :* `4-octet IP : 2-octet value` (ex: `192.0.2.1:100`)
* *Structure Type 2 :* `4-octet ASN : 2-octet value`

#### 2. Route Target (RT) - Extended Community BGP (8 Octets)
Le Route Target définit la politique d'importation et d'exportation au sein du plan de contrôle MP-BGP.

* **Export RT :** Attaché à la route VPNv4 par le PE source lors de sa conversion depuis le RIB VRF local vers le RIB MP-BGP (`bgp.l3vpn.0`).
* **Import RT :** Utilisé par le PE distant pour filtrer les routes VPNv4 reçues et choisir dans quelle(s) VRF locale(s) les injecter.

```
[ CE 1 ] ──(IPv4)──► [ PE 1 (VRF A) ] ═════════ (MP-BGP VPNv4) ═════════► [ PE 2 (VRF A) ] ──(IPv4)──► [ CE 2 ]
                     • Export RT: 65000:10                               • Import RT: 65000:10
                     • RD: 65000:1                                       • Injecte dans VRF A
```

---

## 3. Mécanique de Transfert : Le Double Empilement de Labels MPLS

Lors du transfert d'un paquet à travers le backbone MPLS, le plan de données utilise un **double jeu d'étiquettes MPLS** (*Two-Label Stack*).

```
   ┌──────────────────┬──────────────────┬──────────────────┬─────────────┐
   │ Transport Label  │   VPN/VRF Label  │   Paquet IP      │ Payload Data│
   │ (LDP / SR Label) │   (BGP Allocated)│   Original       │             │
   └──────────────────┴──────────────────┴──────────────────┴─────────────┘
          ▲                      ▲
          │                      │
          │                      └── Indique au PE distant la VRF et l'interface de sortie.
          └───────────────────────── Permet de traverser les routeurs du Cœur P (LDP / SR).
```

### Processus de Commutation de Paquets :

1. **Inbound Lookup (PE Source) :** Le PE1 reçoit un paquet IP standard sur l'interface de la VRF_A. Il interroge la table CEF de la VRF_A.
2. **Push Double Label :**
   * **Inner Label (VPN Label) :** Attribué dynamiquement par le MP-BGP du PE2 pour cette route VRF spécifique.
   * **Outer Label (Transport Label) :** Attribué par LDP ou Segment Routing (SR-MPLS) pour atteindre l'adresse de Peering BGP du PE2 (IGP Loopback).
3. **Core Forwarding (P Routers) :** Les routeurs $P$ swappent uniquement le **Transport Label** (*Top Label*). Ils mènent une opération de *Penultimate Hop Popping* (PHP) sur le dernier routeur $P$.
4. **Outbound Lookup (PE Distant - PE2) :** Le PE2 reçoit le paquet avec uniquement l'**Inner Label**. Ce label identifie directement la VRF cible (ou l'adjaçence directe dans cette VRF). Le PE2 retire le label VPN et transmet le paquet IP natif au CE2.

---

## 4. Architectures Multi-VRF Avancées & Inter-VRF Route Leaking

### 4.1 Route Leaking via MP-BGP / Route Targets (Architecture Clean)

Il s'agit de la méthode la plus propre et évolutive sur les équipements L3. Elle consiste à croiser les `Route-Targets` au sein de la couche BGP locale.

```
vrf definition VRF_CORPO
 rd 65000:100
 route-target export 65000:100
 route-target import 65000:100
 route-target import 65000:999 ! Importer les routes du service partagé (DNS/Active Directory)
!
vrf definition VRF_SERVICES_PARTAGES
 rd 65000:999
 route-target export 65000:999
 route-target import 65000:999
 route-target import 65000:100 ! Importer les routes de CORPO pour autoriser le trafic retour
```

### 4.2 Route Leaking avec BGP IP-Prefix Lists & Route Maps (Leaking Sélectif)

Lorsque l'importation complète de toutes les routes via RT est trop permissive, on combine les `Route-Maps` pour restreindre la fuite à des sous-réseaux/32 spécifiques (ex. Serveur NTP ou DNS spécifique).

```
ip prefix-list PL_DNS_ONLY seq 5 permit 10.50.0.53/32

route-map RM_LEAK_DNS permit 10
 match ip address prefix-list PL_DNS_ONLY

vrf definition VRF_PRODUCTION
 rd 65000:200
 route-target export 65000:200
 route-target import 65000:200
 ! Application de la restriction d'importation
 import route-target map RM_LEAK_DNS
```

### 4.3 Pièges Critiques du Route Leaking : Le Problème de Next-Hop RPF & TTL

* **Next-Hop Unreachable :** Lors d'une fuite de route statique inter-VRF (`ip route vrf A 1.1.1.1 255.255.255.255 GigabitEthernet0/1 2.2.2.2 global`), si le Prochain Saut n'est pas explicitement résolvable dans la table cible, la route est marquée *Invalid* dans la FIB.
* **Boucles de Routage Inter-VRF :** L'importation/exportation croisée symétrique non filtrée entre trois VRF ou plus ($A \to B \to C \to A$) peut provoquer des boucles de ré-injection de routes BGP interminables.

---

## 5. VRF dans les Fabriques Modernes Data Center : BGP EVPN / VXLAN

Dans les Data Centers modernes Spine-Leaf, le transport de niveau 3 virtualisé repose sur le couple **VXLAN (Plane de Données)** et **MP-BGP EVPN (Plane de Contrôle)**.

```
       [ Leaf 1 (VTEP 1) ] ════════════ (Underlay IP / VXLAN) ════════════ [ Leaf 2 (VTEP 2) ]
        ┌─────────────────┐                                                 ┌─────────────────┐
        │  VRF RED (L3)   │                                                 │  VRF RED (L3)   │
        │  VNI L3: 50001  │                                                 │  VNI L3: 50001  │
        └────────┬────────┘                                                 └────────┬────────┘
                 │                                                                   │
        ┌────────┴────────┐                                                 ┌────────┴────────┐
        │ MAC-VRF (L2)    │                                                 │ MAC-VRF (L2)    │
        │ VLAN 10 / VNI 10010                                               │ VLAN 10 / VNI 10010
        └─────────────────┘                                                 └─────────────────┘
```

### 5.1 Symmetric vs Asymmetric IRB (Integrated Routing and Bridging)

* **Asymmetric IRB :** Le routage entre VRF est effectué sur le Leaf d'Origine (*Ingress Leaf*). Le paquet est ensuite bridgé dans le VNI L2 du destinataire à travers le VXLAN.
  * *Inconvénient :* Tous les Leafs doivent héberger tous les VLANs/VNIs de la fabrique.
* **Symmetric IRB (Standard Moderne) :** Le Leaf d'Origine effectue le routage de son VNI L2 source vers le **VNI L3 de la VRF** (`L3VNI`). Le paquet voyage dans l'Underlay encapsulé dans ce L3VNI. Le Leaf de Destination effectue le routage final du L3VNI vers le VNI L2 de destination.
  * *Avantage :* Extrême extensibilité. Un Leaf n'a besoin d'instancier que les VRF et VLANs réellement connectés à ses serveurs locaux.

### 5.2 EVPN Route Type-5 (IP Prefix Route)

Le protocole MP-BGP EVPN utilise la **Route Type 5** pour annoncer les préfixes L3 d'une VRF à travers la fabrique VXLAN.

#### Contenu d'une Route EVPN Type 5 :
* **RD & RT** de la VRF L3.
* **IP Prefix & Mask** (ex: `10.200.10.0/24`).
* **Router MAC :** Adresse MAC du VTEP émetteur.
* **L3VNI :** L'identifiant VXLAN L3 associé à la VRF (ex: `50001`).

---

## 6. Guide de Dépannage & Diagnostics de Niveau Expert

### 6.1 Matrice de Diagnostic Commandes Système (Cisco IOS-XE / NX-OS)

```bash
# 1. Vérification de l'état global des VRF et des interfaces associées
show vrf detail
show ip interface brief vrf ALL

# 2. Inspection avancée de la FIB matérielle (CEF/TCAM) pour une VRF
show ip cef vrf VRF_PRODUCTION 10.10.50.1 detail

# 3. Vérification des tables BGP VPNv4 et validation des Route Targets
show bgp vpnv4 unicast vrf VRF_PRODUCTION
show bgp vpnv4 unicast tags

# 4. Diagnostic des adjacences OSPF / EIGRP / BGP restreintes à une VRF
show ip ospf vrf VRF_PRODUCTION neighbors
show ip bgp vrf VRF_PRODUCTION summary

# 5. Diagnostic MP-BGP EVPN L3VNI (Arista EOS / Cisco NX-OS)
show bgp evpn route-type 5
show vxlan vni
```

### 6.2 Analyse de Scénario : Panne de Connectivité Inter-VRF (Traceroute Analysis)

Lors d'un dépannage inter-VRF, le `traceroute` doit être initié en forçant le sous-système de socket local à utiliser l'IP source de la VRF d'origine :

```bash
# Commande d'injection de sonde spécifique VRF avec source explicite
traceroute vrf VRF_A 10.200.1.50 source Loopback10
```

#### Causes Raçines Fréquentes de Dysfonctionnement :
1. **Asymétrie des Route Targets :** L'Export RT du PE émetteur ne correspond pas à l'Import RT du PE récepteur.
2. **Missing Label in LFIB :** Le routeur $P$ intermédiaire stoppe la commutation car l'IGP sous-jacent n'a pas généré de label LDP/SR pour la Loopback /32 du PE distant.
3. **VRF-Aware NAT Issues :** Omission de la déclaration `ip nat inside` ou `ip nat outside` configurée spécifiquement avec la sous-option `match-in-vrf`.

---

## 7. Tableau Récapitulatif : Comparatif des Technologies VRF

| Critère | VRF-Lite | MPLS L3VPN (RFC 4364) | EVPN / VXLAN L3VNI |
| :--- | :--- | :--- | :--- |
| **Domaine d'usage** | LAN Campus, Datacenter simple | Backbone Opérateur / WAN | Data Center Leaf-Spine Overlay |
| **Plane de Contrôle** | Séparation par sous-interfaces / OSPF/BGP locaux | MP-BGP (VPNv4 / VPNv6) | MP-BGP EVPN (Route Type 5) |
| **Plane de Données** | En-tête 802.1Q (VLAN Tagging) | Double Label MPLS (Transport + VPN) | Encapsulation UDP/VXLAN + VNI L3 |
| **Périmètre d'échelle** | Limité par le nombre de VLANs (4096) | Très élevé ($> 10^6$ routes) | Extrêmement élevé ($16 \times 10^6$ VNIs) |
| **Complexité d'ingénierie** | Faible à Moyenne | Élevée (Requiert LDP/SR + MP-BGP) | Élevée (Requiert Underlay IP + Overlay BGP) |
