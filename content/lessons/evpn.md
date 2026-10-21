# EVPN-VXLAN : le plan de contrôle BGP des fabrics modernes — Niveau Expert

> **node_id :** `evpn` · **Niveau :** CCIE Data Center / Enterprise Infrastructure · **Prérequis :** `vxlan`, `spine-leaf`, `bgp-advanced`, `vrf`

---

## 1. Le problème que résout EVPN

VXLAN seul (sans plan de contrôle) repose sur le **flood-and-learn** : le trafic BUM (Broadcast, Unknown unicast, Multicast) est inondé vers tous les VTEP pour apprendre les MAC. Cela exige du multicast dans l'underlay, ne passe pas à l'échelle et ne gère pas bien le multihoming.

**EVPN** (RFC 7432, RFC 8365 pour VXLAN) utilise **MP-BGP** (famille d'adresses `l2vpn evpn`) pour distribuer les informations MAC/IP et préfixes IP. On passe de l'apprentissage par le plan de données à un **apprentissage par le plan de contrôle**.

| Critère | VXLAN flood-and-learn | EVPN-VXLAN |
|---|---|---|
| Apprentissage MAC | Plan de données (flood) | Plan de contrôle (BGP) |
| Multicast underlay | Nécessaire (ou head-end static) | Optionnel (ingress replication BGP) |
| Suppression ARP | Non | **Oui** (ARP/ND suppression) |
| Multihoming actif/actif | vPC propriétaire | **ESI** (standard) |
| Routage inter-VNI | Centralisé ou HSRP | **Anycast gateway distribuée** (IRB) |
| Mobilité des VM | Flood, convergence lente | **MAC mobility** (sequence number) |
| Multi-tenant L3 | Difficile | VRF + **route type 5** |
| Interopérabilité multi-constructeurs | Faible | Standard IETF |

---

## 2. Architecture de référence

```
                   +---------+            +---------+
                   | SPINE1  |            | SPINE2  |    <- Route Reflectors EVPN
                   | AS65000 |            | AS65000 |       (iBGP, loopback0)
                   +----+----+            +----+----+
                  /   |      \             /   |     \
                 /    |       \           /    |      \
         +------+  +--+---+  +--+---+  +------+
         |LEAF1 |  |LEAF2 |  |LEAF3 |  |LEAF4 |      <- VTEP (NVE, loopback1)
         +--+---+  +--+---+  +--+---+  +--+---+
            |         |         |         |
          Srv A     Srv B     Srv C     Srv D
     (VLAN10)   (VLAN10)   (VLAN20)  (VLAN20)

   Underlay : OSPF ou eBGP, liens routés /31, MTU 9216
   Overlay  : VXLAN, BGP EVPN (spines = RR)
   L2VNI : VLAN10 -> 10010 ; VLAN20 -> 10020
   L3VNI : VRF TENANT-A -> 50001
```

### 2.1 Les trois couches

| Couche | Rôle | Technologies |
|---|---|---|
| **Underlay** | Joignabilité IP entre toutes les loopbacks VTEP | OSPF/IS-IS ou eBGP, ECMP, MTU 9216 |
| **Overlay (data plane)** | Encapsulation du trafic tenant | VXLAN (UDP 4789, VNI 24 bits ≈ 16 M segments) |
| **Overlay (control plane)** | Distribution MAC/IP et préfixes | MP-BGP `l2vpn evpn` |

### 2.2 Terminologie

| Terme | Définition |
|---|---|
| **VTEP** | *VXLAN Tunnel End Point* : le leaf qui encapsule/décapsule |
| **NVE** | *Network Virtualization Edge* : interface logique VTEP (`interface nve1`) |
| **L2VNI** | VNI associé à un VLAN/bridge domain (commutation) |
| **L3VNI** | VNI associé à une VRF (routage symétrique) |
| **IRB** | *Integrated Routing and Bridging* : SVI avec passerelle distribuée |
| **ESI** | *Ethernet Segment Identifier* : identifie un lien multihomé (10 octets) |
| **RT / RD** | Route-Target (import/export) / Route-Distinguisher |
| **DF** | *Designated Forwarder* : élu pour le trafic BUM d'un segment |

---

## 3. Underlay : points de contrôle

Avant EVPN, l'underlay doit être **irréprochable** :

```
interface Ethernet1/1
  description to-SPINE1
  no switchport
  mtu 9216
  ip address 10.1.1.1/31
  ip ospf network point-to-point
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface loopback0
  description Router-ID / BGP
  ip address 10.255.0.11/32
  ip router ospf UNDERLAY area 0.0.0.0

interface loopback1
  description VTEP source (NVE)
  ip address 10.255.1.11/32
  ip router ospf UNDERLAY area 0.0.0.0
```

- **MTU** : VXLAN ajoute **50 octets** (+4 si 802.1Q) → MTU underlay ≥ 9216 conseillé.
- **Loopback0** = session BGP ; **loopback1** = source VTEP (une IP distincte facilite le dépannage ; en vPC on utilise une IP secondaire partagée).
- Test : `ping 10.255.1.13 source 10.255.1.11 df-bit packet-size 1572`.

---

## 4. Types de routes EVPN

| Type | Nom | Rôle | Utilisation principale |
|---|---|---|---|
| **1** | Ethernet Auto-Discovery | Annonce un ESI et permet l'aliasing / mass withdraw | Multihoming |
| **2** | MAC/IP Advertisement | Distribue MAC (+ IP optionnelle) d'un hôte | Commutation L2, ARP suppression, routage hôte |
| **3** | Inclusive Multicast Ethernet Tag | Liste des VTEP participant à un VNI | Réplication BUM |
| **4** | Ethernet Segment | Élection du DF entre PE du même ESI | Multihoming |
| **5** | IP Prefix | Annonce un préfixe IP (pas seulement un hôte) | Routage externe / inter-fabric |

### 4.1 Contenu d'une route type 2

```
Route Type 2 (MAC/IP Advertisement)
+------------------------------------------+
| Route Distinguisher   (ex. 10.255.0.13:32777)
| ESI                   (0 si single-homed)
| Ethernet Tag ID       (0 en VXLAN)
| MAC Address           (0050.56aa.bb01)
| IP Address            (10.10.10.21)  [optionnel]
| Label1 = L2VNI        (10010)
| Label2 = L3VNI        (50001)  [si MAC+IP]
+------------------------------------------+
Extended communities : RT L2 (65000:10010), RT L3 (65000:50001),
                       Router MAC (symétrique), MAC Mobility (seq), Encapsulation VXLAN
```

### 4.2 Génération automatique des RD/RT

Sur NX-OS, `rd auto` génère `RouterID:VLAN+32767` et `route-target both auto` génère `ASN:VNI`. En eBGP multi-AS (un AS par leaf), utilisez des RT **explicites** ou `route-target ... auto` avec un AS commun, car la valeur `auto` dépend de l'AS local.

---

## 5. Configuration complète d'un leaf (NX-OS)

### 5.1 Fonctionnalités et passerelle anycast

```
nv overlay evpn
feature ospf
feature bgp
feature interface-vlan
feature vn-segment-vlan-based
feature nv overlay

fabric forwarding anycast-gateway-mac 0000.2222.3333
```

### 5.2 VLAN, VNI et VRF

```
vlan 10
  name WEB
  vn-segment 10010
vlan 20
  name APP
  vn-segment 10020
vlan 3999
  name L3VNI-TENANT-A
  vn-segment 50001

vrf context TENANT-A
  vni 50001
  rd auto
  address-family ipv4 unicast
    route-target both auto
    route-target both auto evpn
```

### 5.3 SVI (passerelle distribuée) et SVI L3VNI

```
interface Vlan10
  no shutdown
  vrf member TENANT-A
  ip address 10.10.10.1/24
  fabric forwarding mode anycast-gateway

interface Vlan20
  no shutdown
  vrf member TENANT-A
  ip address 10.10.20.1/24
  fabric forwarding mode anycast-gateway

interface Vlan3999
  no shutdown
  vrf member TENANT-A
  ip forward
```

> **Anycast gateway :** tous les leafs portent **la même IP et la même MAC virtuelle** de passerelle. L'hôte parle toujours à son leaf local, quel que soit l'endroit où la VM migre.

### 5.4 Interface NVE

```
interface nve1
  no shutdown
  host-reachability protocol bgp
  source-interface loopback1
  member vni 10010
    suppress-arp
    ingress-replication protocol bgp
  member vni 10020
    suppress-arp
    ingress-replication protocol bgp
  member vni 50001 associate-vrf
```

- `host-reachability protocol bgp` : active le plan de contrôle EVPN.
- `ingress-replication protocol bgp` : le BUM est répliqué en unicast vers les VTEP découverts via les routes type 3. Alternative : `mcast-group 239.1.1.10` (underlay PIM requis).
- `suppress-arp` : le leaf répond localement aux requêtes ARP à partir de sa table EVPN.

### 5.5 Section EVPN et BGP

```
evpn
  vni 10010 l2
    rd auto
    route-target import auto
    route-target export auto
  vni 10020 l2
    rd auto
    route-target import auto
    route-target export auto

router bgp 65000
  router-id 10.255.0.11
  neighbor 10.255.0.1
    remote-as 65000
    update-source loopback0
    address-family l2vpn evpn
      send-community
      send-community extended
  neighbor 10.255.0.2
    remote-as 65000
    update-source loopback0
    address-family l2vpn evpn
      send-community
      send-community extended
  vrf TENANT-A
    address-family ipv4 unicast
      advertise l2vpn evpn
```

### 5.6 Spine en Route Reflector

```
router bgp 65000
  router-id 10.255.0.1
  neighbor 10.255.0.11
    remote-as 65000
    update-source loopback0
    address-family l2vpn evpn
      send-community
      send-community extended
      route-reflector-client
```

Les spines n'ont **ni NVE ni VNI** : ils transportent uniquement les routes EVPN. Sur un spine, il faut `retain route-target all` dans `address-family l2vpn evpn` si le spine ne fait pas d'import (sinon il filtre les routes sans RT correspondant).

---

## 6. Routage inter-VNI : IRB asymétrique vs symétrique

| Critère | IRB asymétrique | IRB symétrique (recommandé) |
|---|---|---|
| Routage effectué | Sur le leaf **source** seulement | Sur le leaf source **et** le leaf destination |
| VNI nécessaires | Tous les L2VNI sur **tous** les leafs | L2VNI locaux + **un L3VNI par VRF** |
| Pont retour | Via VNI du sous-réseau destination | Via le L3VNI (VRF) |
| Scalabilité | Faible (état MAC global) | **Élevée** |
| Table ARP/MAC | Doit connaître tous les hôtes | Seulement les hôtes locaux + préfixes /32 |

Flux symétrique entre Srv A (VLAN10, LEAF1) et Srv C (VLAN20, LEAF3) :

```
Srv A 10.10.10.21 --> LEAF1 (anycast GW 10.10.10.1)
   1. Routage dans VRF TENANT-A (lookup /32 de Srv C appris par route type 2)
   2. Encapsulation VXLAN avec L3VNI 50001, MAC dest = Router-MAC de LEAF3
   3. Transport underlay LEAF1 -> LEAF3
LEAF3 décapsule (L3VNI 50001) --> routage dans VRF --> VLAN20 --> Srv C 10.10.20.31
```

---

## 7. Multihoming actif/actif avec ESI-LAG

L'ESI remplace le vPC propriétaire par un mécanisme standard : un serveur est connecté à **deux leafs** via un LAG (LACP), et chaque leaf annonce le même **ESI**.

```
          LEAF1                LEAF2
            \                   /
        Eth1/10             Eth1/10
             \                 /
              +----- LAG -----+        ESI = 00:11:22:33:44:55:66:77:88:99
                    Srv A
```

| Route | Fonction dans le multihoming |
|---|---|
| **Type 4** | Élection du **DF** par segment Ethernet (modulo VLAN par défaut) |
| **Type 1 par ESI** | *Mass withdraw* : si le lien tombe, retrait de tous les MAC en un seul message |
| **Type 1 par EVI** | *Aliasing* : un VTEP distant peut load-balancer vers les deux leafs |
| **Split-horizon** | Étiquette ESI pour éviter le retour du BUM sur le LAG d'origine |

```
evpn esi multihoming

interface port-channel10
  switchport mode trunk
  switchport trunk allowed vlan 10,20
  ethernet-segment 10
    system-mac 0000.0000.0010
```

> La syntaxe varie selon les plateformes (NX-OS ci-dessus ; Arista utilise `evpn ethernet-segment` + `identifier`). Retenez surtout le **concept** : même ESI et même system-mac LACP sur les deux leafs, pour que le serveur voie un seul partenaire LACP.

---

## 8. Mobilité MAC et protection contre les boucles

Quand une VM migre de LEAF1 à LEAF3, LEAF3 annonce la MAC avec un **MAC Mobility Extended Community** dont le **sequence number est incrémenté**. La route avec le plus grand numéro de séquence gagne : les autres VTEP basculent immédiatement.

| Mécanisme | Défaut (NX-OS) | Effet |
|---|---|---|
| Détection de duplication MAC | **5 déplacements en 180 s** | La MAC est gelée (« duplicate ») pendant 30 s environ |
| Annonce GARP/RARP | VM migrée envoie un RARP | Déclenche la mise à jour rapide |
| Sticky MAC | Configurable | Empêche la mobilité (pare-feu, VIP) |

```
show l2route evpn mac all
show l2route evpn mac-ip all
show bgp l2vpn evpn 0050.56aa.bb01
```

---

## 9. Route type 5 : connectivité externe et inter-fabric

Un **border leaf** connecté à un routeur externe (WAN, Internet, pare-feu) annonce les préfixes IP externes dans EVPN via des routes type 5.

```
router bgp 65000
  vrf TENANT-A
    address-family ipv4 unicast
      advertise l2vpn evpn
    neighbor 192.0.2.2
      remote-as 65500
      address-family ipv4 unicast
        send-community
        route-map PERMIT-ALL out
```

```
         Internet / WAN
              |
        Routeur externe (AS65500)
              |  eBGP VRF TENANT-A
         BORDER LEAF  ---- EVPN type 5 ----> LEAF1, LEAF2, LEAF3, LEAF4
```

Un **default route** externe injectée dans la VRF devient une route type 5 distribuée dans toute la fabric. Les autres leafs routent ensuite vers le border leaf via le L3VNI.

---

## 10. ARP suppression et réduction du BUM

1. LEAF1 apprend (MAC, IP) de Srv A par ARP/GARP et l'annonce en type 2.
2. Srv B émet un ARP request pour 10.10.10.21.
3. LEAF2, qui connaît déjà l'entrée (par BGP), **répond localement** (proxy ARP) : le broadcast n'est jamais propagé.

Gain : moins de trafic BUM, moins de CPU sur les hôtes, meilleure scalabilité. Limites : hôtes « silencieux » (non encore appris) : le leaf doit alors inonder (ou on utilise **unknown unicast suppression**).

---

## 11. Vérification et dépannage

### 11.1 Commandes essentielles (NX-OS)

```
show nve peers
show nve vni
show nve interface nve1 detail
show bgp l2vpn evpn summary
show bgp l2vpn evpn route-type 2
show bgp l2vpn evpn route-type 5
show l2route evpn mac all
show ip route vrf TENANT-A
show vxlan interface
show forwarding vrf TENANT-A
```

### 11.2 Tableau diagnostic

| Symptôme | Cause probable | Vérification |
|---|---|---|
| Peer NVE « Down » | Loopback1 non joignable (underlay) | `ping <vtep> source loopback1` |
| Session BGP EVPN Idle/Active | `update-source` incorrect, ACL, ASN | `show bgp l2vpn evpn summary` |
| MAC non apprise sur le leaf distant | `send-community extended` manquant | `show bgp l2vpn evpn route-type 2` |
| Type 2 reçu mais pas installé | RT import ne correspond pas | `show bgp l2vpn evpn vni-id 10010` |
| Ping inter-VLAN KO, intra-VLAN OK | L3VNI mal associé (`associate-vrf`) ou SVI 3999 down | `show nve vni` |
| Paquets > 1450 perdus | MTU underlay insuffisant | `ping ... df-bit` |
| Trafic coincé sur un seul leaf (ESI) | Aliasing / type 1 absent | `show bgp l2vpn evpn route-type 1` |

### 11.3 Méthode

1. **Underlay** : tous les loopbacks se pingent, MTU ok.
2. **BGP EVPN** : sessions Established, `send-community extended`.
3. **VNI/NVE** : VNI « Up », peers visibles.
4. **Contrôle** : type 3 présents pour chaque VNI, type 2 pour chaque hôte.
5. **Données** : encapsulation et MAC du routeur (symétrique), capture de paquets (VXLAN UDP 4789).

---

## 12. Bonnes pratiques et pièges

- **Anycast gateway** partout, même MAC virtuelle.
- **Symmetric IRB** et un L3VNI par VRF.
- Spines en **route reflectors** (2 minimum) ; leafs clients.
- `send-community extended` : sans lui, aucune RT ne circule.
- Normaliser les plans : VLAN → `100xx`, L3VNI → `50xxx`.
- MTU 9216 sur l'underlay ; MSS clamp côté hôtes si besoin.
- Activer `suppress-arp` sur tous les L2VNI de serveurs.
- **Piège classique :** l'`ip forward` (et non `ip address`) sur la SVI L3VNI.
- **Piège classique :** RT `auto` dépend de l'ASN ; en multi-AS, utilisez des RT explicites.
- **Piège classique :** la mobilité MAC requiert que le type 2 inclue le sequence number ; ne pas filtrer l'extended community.

---

## 13. Aide-mémoire

| Besoin | Élément à retenir |
|---|---|
| Plan de contrôle | MP-BGP, AFI `l2vpn` SAFI `evpn` |
| Transport | VXLAN, UDP 4789 |
| MAC/IP | Type 2 |
| BUM (liste VTEP) | Type 3 |
| Multihoming | Types 1 et 4 |
| Préfixe IP | Type 5 |
| Gateway distribuée | `fabric forwarding anycast-gateway-mac` |
| Routage symétrique | L3VNI + `member vni X associate-vrf` |
| Réduction ARP | `suppress-arp` |
| Vérification | `show nve peers`, `show bgp l2vpn evpn` |

---

## 14. Points à retenir

1. EVPN transforme VXLAN en **plan de contrôle BGP** : plus de flood-and-learn.
2. **5 types de routes** : 1 (A-D), 2 (MAC/IP), 3 (IMET), 4 (ES), 5 (préfixe IP).
3. **L2VNI** pour la commutation, **L3VNI** pour le routage symétrique entre sous-réseaux.
4. **Anycast gateway** : même IP/MAC de passerelle sur tous les leafs.
5. **ESI** : multihoming actif/actif standard avec DF, aliasing et mass withdraw.
6. **MAC mobility** : le sequence number le plus élevé gagne, protection anti-boucle intégrée.
7. L'**underlay** (MTU, ECMP, loopbacks) conditionne toute la fiabilité de l'overlay.
