# Segment Routing (SR-MPLS & SRv6) — Niveau Expert

> **node_id :** `segment-routing` · **Niveau :** CCIE Service Provider / Enterprise Infrastructure · **Prérequis :** `mpls`, `ospf-advanced`, `bgp-advanced`

---

## 1. Pourquoi Segment Routing ?

Dans un backbone MPLS classique, on empile plusieurs protocoles : un IGP (OSPF/IS-IS), **LDP** pour distribuer les labels, et **RSVP-TE** pour l'ingénierie de trafic. Chaque protocole garde de l'état par flux dans chaque routeur du chemin, et LDP/IGP peuvent se désynchroniser.

**Segment Routing (SR)** applique le principe du *source routing* : le routeur d'entrée encode le chemin voulu sous forme d'une liste ordonnée de **segments** (instructions). Les routeurs intermédiaires n'ont plus d'état par flux : ils exécutent simplement l'instruction du segment actif.

| Critère | LDP + RSVP-TE | Segment Routing |
|---|---|---|
| Protocoles de signalisation | IGP + LDP + RSVP-TE | IGP uniquement (extensions) |
| État par flux dans le cœur | Oui (RSVP-TE) | Non (état seulement chez la tête de ligne) |
| Protection rapide (FRR) | RSVP-TE FRR / LFA (couverture partielle) | **TI-LFA** (100 % de couverture topologique) |
| Ingénierie de trafic | Tunnels RSVP-TE, scalabilité limitée | **SR-TE policies**, scalable |
| Synchronisation IGP/LDP | Problème classique (`mpls ldp sync`) | Inexistant (labels portés par l'IGP) |
| Plan de données | MPLS | MPLS (**SR-MPLS**) ou IPv6 (**SRv6**) |
| Intégration SDN / PCE | Complexe | Native (PCEP, BGP-LS, BGP SR-TE) |

---

## 2. Concepts fondamentaux

### 2.1 Le segment et le SID

Un **segment** est une instruction topologique ou de service. Il est identifié par un **SID** (Segment Identifier) :

- en **SR-MPLS**, le SID est un **label MPLS** (32 bits dont 20 de label) ;
- en **SRv6**, le SID est une **adresse IPv6 de 128 bits**.

### 2.2 Types de SID

| SID | Portée | Signification | Exemple |
|---|---|---|---|
| **Prefix-SID** | Globale | Chemin le plus court (ECMP) vers un préfixe | Label 16005 → loopback de PE2 |
| **Node-SID** | Globale | Prefix-SID d'une loopback identifiant un routeur (flag N) | Node-SID de P1 |
| **Anycast-SID** | Globale | Prefix-SID partagé par plusieurs routeurs | Paire de ABR |
| **Adjacency-SID (Adj-SID)** | **Locale** | Force la sortie par une interface/adjacence précise | Label dynamique 24001 |
| **Binding-SID (BSID)** | Locale | Représente toute une SR policy (liste de segments) | BSID 24100 → policy GOLD |
| **Prefix-SID Flex-Algo** | Globale | Prefix-SID calculé selon un algorithme personnalisé | Algo 128 |

### 2.3 SRGB et SRLB

Le **SRGB** (*Segment Routing Global Block*) est la plage de labels réservée aux SID globaux. Le label réellement utilisé est :

```
Label = SRGB_base + Index du Prefix-SID
```

Exemple : SRGB = 16000–23999, index de PE2 = 5 → **label 16005**.

> **Bonne pratique :** utiliser le **même SRGB sur tous les routeurs** du domaine. Ainsi le label d'un préfixe est identique partout, ce qui simplifie l'exploitation et le dépannage. Si les SRGB diffèrent, chaque routeur doit calculer le label sortant avec le SRGB du voisin (fonctionne, mais difficile à lire).

Le **SRLB** (*Local Block*, défaut 15000–15999 sur IOS-XR) réserve des labels pour les SID locaux configurés manuellement.

### 2.4 Commandes de plan de données MPLS

| Opération | Rôle |
|---|---|
| **PUSH** | Insère un ou plusieurs labels (routeur d'entrée) |
| **CONTINUE** | Conserve le label actif (le routeur n'est pas la destination du segment) |
| **NEXT** (pop/swap) | Le segment est consommé, on passe au suivant |
| **PHP** | *Penultimate Hop Popping* : l'avant-dernier routeur retire le label |

---

## 3. Extensions IGP

SR n'a pas besoin de nouveau protocole : les SID sont annoncés dans l'IGP.

| Information | IS-IS | OSPFv2 |
|---|---|---|
| Capacités SR (SRGB, algos) | Sub-TLV *SR-Capabilities* (TLV 242) | RI LSA – *SR-Algorithm*, *SID/Label Range* |
| Prefix-SID | Sub-TLV dans TLV 135/236 | Extended Prefix LSA (type 7) |
| Adj-SID | Sub-TLV dans TLV 22/222 | Extended Link LSA (type 8) |
| Flags importants | N (node), P (no-PHP), E (explicit-null), V, L | idem |
| Limite de profondeur (MSD) | Sub-TLV *Node MSD* | Idem |

> **MSD** (*Maximum SID Depth*) : nombre maximal de labels qu'un routeur peut imposer. Une SR policy dont la liste dépasse le MSD de la tête de ligne ne peut pas être installée.

---

## 4. Schéma de référence

```
                     Domaine SR-MPLS  (IS-IS L2, SRGB 16000-23999)

   CE1 ---- PE1 -------- P1 -------- PE2 ---- CE2
  AS65101  (idx 1)    (idx 11)      (idx 5)   AS65102
                \          |         /
                 \         |        /
                  +------- P2 -----+
                         (idx 12)

   Loopbacks :  PE1 10.0.0.1/32   P1 10.0.0.11/32
                P2  10.0.0.12/32  PE2 10.0.0.5/32

   Labels globaux (SRGB identique partout) :
        PE1 = 16001   PE2 = 16005   P1 = 16011   P2 = 16012
```

Chemin PE1 → PE2 par le plus court chemin (via P1) :

```
 PE1               P1                PE2
 [PUSH 16005] --> [NEXT: SWAP 16005 --> PHP]  --> [reçoit IP/VPN label]
   Pile : |16005|    |16005| → pop (PHP)       Pile : |service label|
```

Chemin forcé par P2 (SR-TE) avec deux segments :

```
 PE1 impose la pile : [ 16012 | 16005 ]
 PE1 --> P2 : label 16012 (Node-SID P2) → P2 consomme (NEXT) → reste 16005
 P2  --> PE2: label 16005 → PHP avant PE2
```

---

## 5. Configuration SR-MPLS avec IS-IS (Cisco IOS-XR)

### 5.1 SRGB et IS-IS

```
segment-routing
 global-block 16000 23999
!
router isis CORE
 is-type level-2-only
 net 49.0001.0000.0000.0001.00
 address-family ipv4 unicast
  metric-style wide
  segment-routing mpls
 !
 interface Loopback0
  passive
  address-family ipv4 unicast
   prefix-sid index 1
  !
 !
 interface HundredGigE0/0/0/0
  point-to-point
  address-family ipv4 unicast
  !
 !
!
```

- `metric-style wide` est **obligatoire** (TLV étendus).
- `prefix-sid index 1` : le label sera `SRGB_base + 1 = 16001`.
- Option absolute : `prefix-sid absolute 16001`.
- Sur la loopback, le flag **N** est positionné automatiquement : le SID est un Node-SID.

### 5.2 Équivalent OSPFv2

```
router ospf 1
 router-id 10.0.0.1
 segment-routing mpls
 area 0
  interface Loopback0
   prefix-sid index 1
  !
  interface HundredGigE0/0/0/0
   network point-to-point
  !
 !
!
```

### 5.3 Vérification

```
RP/0/RP0/CPU0:PE1# show isis segment-routing label table
RP/0/RP0/CPU0:PE1# show isis database verbose PE2 | include SID
RP/0/RP0/CPU0:PE1# show route 10.0.0.5/32 detail
RP/0/RP0/CPU0:PE1# show mpls forwarding prefix 10.0.0.5/32
RP/0/RP0/CPU0:PE1# show segment-routing mapping-server prefix-sid-map ipv4
RP/0/RP0/CPU0:PE1# ping sr-mpls 10.0.0.5/32 fec-type igp isis
RP/0/RP0/CPU0:PE1# traceroute sr-mpls 10.0.0.5/32 fec-type igp isis
```

Équivalent IOS-XE : `show isis segment-routing`, `show mpls forwarding-table`, `show segment-routing mpls connected-prefix-sid-map ipv4`.

---

## 6. Interopérabilité avec LDP (migration)

La migration se fait **sans rupture** : on active SR à côté de LDP, puis on retire LDP.

| Scénario | Mécanisme |
|---|---|
| Îlot SR et îlot LDP | **SRMS** (*Segment Routing Mapping Server*) : annonce des Prefix-SID pour le compte des routeurs LDP-only |
| Chemin SR → LDP | Le routeur d'interconnexion fait du *swap* SR-label → LDP-label |
| Chemin LDP → SR | Le préfixe doit avoir un SID via le SRMS |
| Préférence | Par défaut, **SR est préféré à LDP** quand les deux existent (IOS-XR) |

```
segment-routing
 mapping-server
  prefix-sid-map
   address-family ipv4
    10.0.0.50/32 index 50 range 4
   !
  !
 !
!
router isis CORE
 address-family ipv4 unicast
  segment-routing prefix-sid-map advertise-local
```

Étapes types : (1) SRGB identique, (2) activer SR dans l'IGP, (3) vérifier la préférence SR, (4) retirer LDP interface par interface, (5) valider les services L3VPN/EVPN.

---

## 7. TI-LFA : protection rapide à couverture totale

**LFA classique** n'offre pas toujours un voisin de secours (« remote-LFA » étend un peu la couverture). **TI-LFA** (*Topology-Independent Loop-Free Alternate*) garantit une protection **100 % topologique** :

1. Le PLR (*Point of Local Repair*) calcule le **post-convergence path** : le chemin qu'emprunterait l'IGP après la panne.
2. Il détermine l'espace **P** (nœuds atteignables sans passer par l'élément en panne) et l'espace **Q** (nœuds qui atteignent la destination sans passer par l'élément en panne).
3. Il encode le chemin de secours avec 0 à 2-3 segments (Node-SID du point P + Adj-SID vers Q).
4. En cas de panne, bascule en **moins de 50 ms** (précalculé dans la FIB/hardware).

```
router isis CORE
 interface HundredGigE0/0/0/0
  point-to-point
  address-family ipv4 unicast
   fast-reroute per-prefix
   fast-reroute per-prefix ti-lfa
   metric 10
  !
 !
!
```

Protection de nœud et SRLG (optionnel) :

```
  address-family ipv4 unicast
   fast-reroute per-prefix ti-lfa node-protecting
   fast-reroute per-prefix srlg-protection weighted-global
```

Vérification :

```
show isis fast-reroute 10.0.0.5/32 detail
show cef 10.0.0.5/32 detail
show isis fast-reroute summary
```

> **Piège :** TI-LFA s'appuie sur des listes de segments : la pile de labels de secours s'ajoute à la pile existante. Vérifiez que le MSD du PLR est suffisant.

---

## 8. SR-TE : politiques d'ingénierie de trafic

Une **SR policy** est identifiée par le triplet **(tête de ligne, couleur, extrémité)**.

| Élément | Description |
|---|---|
| **Color** | Entier (ex. 100 = « faible latence », 200 = « chemin évitant le lien X ») |
| **Endpoint** | Loopback de destination (ex. 10.0.0.5) |
| **Candidate path** | Chemin candidat avec une *préférence* ; le plus préféré valide est actif |
| **Segment-list** | Liste ordonnée de SID (explicite) |
| **Dynamic** | Calculé par la tête de ligne ou un **PCE** selon une métrique (IGP, TE, latence) et des contraintes |
| **BSID** | Label pointant sur la policy, utilisable pour chaîner des domaines |

### 8.1 Politique explicite

```
segment-routing
 traffic-eng
  segment-list VIA-P2
   index 10 mpls label 16012
   index 20 mpls label 16005
  !
  policy GOLD
   color 100 end-point ipv4 10.0.0.5
   binding-sid mpls 24100
   candidate-paths
    preference 200
     explicit segment-list VIA-P2
    !
    preference 100
     dynamic
      metric
       type igp
      !
     !
    !
   !
  !
 !
!
```

### 8.2 Dynamique avec contrainte de latence

```
segment-routing
 traffic-eng
  policy LOWLAT
   color 200 end-point ipv4 10.0.0.5
   candidate-paths
    preference 100
     dynamic
      metric
       type delay
      !
      constraints
       affinity
        exclude-any
         name RED
```

(Pré-requis : mesure de délai via *performance-measurement* et annonce des *link delay* dans l'IGP.)

### 8.3 Automated Steering (AS) et ODN

Les services BGP (L3VPN, EVPN) portent une **extended community Color**. Si une policy `(color, endpoint = next-hop BGP)` existe, le trafic est **automatiquement** dirigé dedans. Avec **ODN** (*On-Demand Next-hop*), la policy est même **créée à la demande** à partir d'un modèle.

```
extcommunity-set opaque COLOR-100
  100
end-set
!
route-policy SET-GOLD
  set extcommunity color COLOR-100
end-policy
!
router bgp 65000
 neighbor 10.0.0.5
  address-family vpnv4 unicast
   route-policy SET-GOLD in
!
segment-routing
 traffic-eng
  on-demand color 100
   dynamic
    metric
     type igp
```

Vérification :

```
show segment-routing traffic-eng policy
show segment-routing traffic-eng policy color 100 endpoint ipv4 10.0.0.5 detail
show bgp vpnv4 unicast vrf CLIENT-A 192.168.50.0/24 detail
```

---

## 9. Flex-Algo (Flexible Algorithm)

Flex-Algo permet de définir **plusieurs « plans » de topologie** dans le même IGP, chacun avec sa métrique et ses contraintes. Les algorithmes personnalisés utilisent les valeurs **128 à 255**.

| Algorithme | Métrique | Contrainte | Usage |
|---|---|---|---|
| 0 | IGP | aucune | SPF standard |
| 1 | IGP | aucune | Strict SPF |
| 128 | **Delay** (latence min.) | exclut lien « RED » | Voix / trading |
| 129 | IGP | inclut seulement « GREEN » | Plan « données » séparé |

```
router isis CORE
 flex-algo 128
  metric-type delay
  affinity exclude-any RED
  advertise-definition
 !
 interface Loopback0
  address-family ipv4 unicast
   prefix-sid algorithm 128 index 101
```

Un service est ensuite lié à l'algorithme 128 via une SR policy ou une couleur ODN dont le chemin dynamique utilise `sid-algorithm 128`.

---

## 10. SRv6 : Segment Routing sur plan de données IPv6

SRv6 supprime MPLS : le SID est une **adresse IPv6**, et la liste de segments est portée dans un **SRH** (*Segment Routing Header*, extension IPv6 de type 4).

### 10.1 Structure d'un SID SRv6

```
|<------------ 128 bits ------------>|
+---------+----------+--------------+-----------+
| Locator | Function | Arguments    |  (optionnel)
+---------+----------+--------------+-----------+
 (route)   (comportement)
```

Le **locator** est un préfixe routé par l'IGP qui mène au nœud propriétaire. La **function** définit l'action.

### 10.2 Comportements courants

| Comportement | Rôle |
|---|---|
| **End** | Équivalent Node-SID : décrémente SL et copie le prochain segment dans l'adresse de destination |
| **End.X** | Équivalent Adj-SID : transmet via une adjacence précise |
| **End.DT4 / DT6 / DT46** | Décapsule et recherche dans une table VRF (L3VPN) |
| **End.DX2 / DT2U** | Services L2 (EVPN E-Line / E-LAN) |
| **H.Encaps** | Encapsulation IPv6 + SRH à l'entrée |
| **uN / uA (uSID)** | Versions compressées sur 16 bits dans un bloc partagé |

### 10.3 Compression uSID

Un SID de 128 bits par segment alourdit les en-têtes. Avec **uSID** (micro-segments), un conteneur de 128 bits transporte jusqu'à **6 uSID de 16 bits** après le bloc commun :

```
fcbb:bb00 : 0001 : 0011 : 0005 : e000 : 0000 : 0000
 bloc 32b   uN P1   uN P2   uN PE2  (end-of-carrier)
```

### 10.4 Configuration IOS-XR de base

```
segment-routing
 srv6
  locators
   locator MAIN
    micro-segment behavior unode psp-usp
    prefix fcbb:bb00:1::/48
   !
  !
 !
!
router isis CORE
 address-family ipv6 unicast
  metric-style wide
  segment-routing srv6
   locator MAIN
  !
 !
!
router bgp 65000
 segment-routing srv6
  locator MAIN
 !
 vrf CLIENT-A
  address-family ipv4 unicast
   segment-routing srv6
    alloc mode per-vrf
```

Vérification :

```
show segment-routing srv6 locator
show segment-routing srv6 sid
show route ipv6 fcbb:bb00:5::/48
```

### 10.5 SR-MPLS ou SRv6 ?

| Critère | SR-MPLS | SRv6 |
|---|---|---|
| Maturité / déploiements | Très large | Croissante |
| Plan de données | MPLS existant | IPv6 natif, pas de MPLS |
| Programmabilité réseau | Bonne | **Excellente** (function + arguments) |
| Overhead | Faible (4 octets/label) | Fort sans uSID, faible avec uSID |
| Interconnexion avec Internet | Besoin de passerelles | Natif IPv6 |

---

## 11. Dépannage méthodique

| Symptôme | Cause probable | Commande de diagnostic |
|---|---|---|
| Aucun label 160xx dans la LFIB | `segment-routing mpls` absent de l'IGP | `show isis segment-routing label table` |
| Label différent selon le routeur | SRGB différents | `show segment-routing mpls state` |
| Trafic perdu sur un chemin SR-TE | SID invalide dans la segment-list | `show segment-routing traffic-eng policy detail` |
| Policy « down » | Aucun candidate path valide / MSD dépassé | `show segment-routing traffic-eng policy ... detail` |
| Pas de FRR TI-LFA | Lien non point-to-point ou IGP sans `ti-lfa` | `show isis fast-reroute summary` |
| Collision de Prefix-SID | Même index sur deux loopbacks | `show isis segment-routing prefix-sid-map active-policy` |
| Fragmentation, paquets perdus | Pile de labels trop grande, MTU insuffisant | `ping sr-mpls`, vérifier le MTU du cœur |

Méthode en 5 étapes : **(1)** l'IGP est-il sain ? **(2)** le SID est-il annoncé et sans conflit ? **(3)** le label existe-t-il dans la LFIB de chaque saut ? **(4)** la policy est-elle active (candidate path valide) ? **(5)** le service BGP est-il bien « colorié » ?

---

## 12. Bonnes pratiques et pièges d'examen

- Même **SRGB** partout ; plage de labels documentée.
- **Index uniques** par loopback ; plan d'adressage des SID documenté (ex. PE 1-99, P 100-199).
- Activer **TI-LFA** sur toutes les interfaces cœur point-to-point.
- Utiliser **Anycast-SID** pour la redondance d'ABR/passerelles.
- Surveiller le **MSD** : privilégier les **Binding-SID** pour raccourcir les piles.
- Préférer **ODN + AS** à des policies statiques par service.
- Migration LDP → SR : toujours via **SRMS** et validations par îlots.
- **Piège :** un Prefix-SID est global, un Adj-SID est **local** : ne jamais annoncer un Adj-SID comme s'il était global.
- **Piège :** PHP est actif par défaut ; le flag **P** (no-PHP) ou **E** (explicit-null) change le comportement à l'avant-dernier saut.

---

## 13. Aide-mémoire (cheat sheet)

| Besoin | Mot-clé / commande |
|---|---|
| Définir le SRGB | `segment-routing global-block 16000 23999` |
| Activer SR dans IS-IS | `segment-routing mpls` sous `address-family ipv4 unicast` |
| Prefix-SID | `prefix-sid index N` sous l'interface Loopback IGP |
| TI-LFA | `fast-reroute per-prefix ti-lfa` |
| SR policy | `segment-routing traffic-eng policy NAME color C end-point ipv4 X` |
| Colorer un service | `set extcommunity color COLOR-100` |
| Flex-Algo | `flex-algo 128` + `prefix-sid algorithm 128 index N` |
| SRv6 locator | `segment-routing srv6 locators locator NAME prefix ...` |
| Test data-plane | `ping sr-mpls` / `traceroute sr-mpls` |

---

## 14. Points à retenir

1. SR remplace **LDP et RSVP-TE** par des extensions IGP et du *source routing*.
2. Le label = **SRGB + index**, d'où l'importance d'un SRGB homogène.
3. **Prefix-SID** (global, ECMP) vs **Adj-SID** (local, interface forcée).
4. **TI-LFA** : protection < 50 ms avec couverture totale.
5. **SR-TE + couleur + ODN** = ingénierie de trafic automatisée, sans état dans le cœur.
6. **Flex-Algo** permet des plans réseau distincts dans un seul IGP.
7. **SRv6** remplace MPLS par IPv6 + SRH ; **uSID** réduit l'overhead.
