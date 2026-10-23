## node_id: segment-routing-intermediaire

title: Segment Routing (SR-MPLS et SRv6) - Intermédiaire

# Segment Routing (SR-MPLS et SRv6) - Intermédiaire

**Niveau :** Intermédiaire

**Prérequis :** Segment Routing Débutant (`segment-routing-debutant`)

Dans le module débutant, nous avons établi les concepts fondamentaux du Segment Routing : le principe du *Source Routing*, l'élimination des protocoles d'état LDP/RSVP-TE, la distinction entre **Node SID** et **Adj-SID**, ainsi que les deux plans de données majeurs (**SR-MPLS** et **SRv6**).

Ce module **Intermédiaire** approfondit le fonctionnement interne du Segment Routing. Nous étudierons en détail le fonctionnement des extensions protocolaires IGP (IS-IS et OSPF), la mécanique avancée du calcul de protection **TI-LFA** (Espaces P et Q), le déploiement des politiques d'ingénierie de trafic (**SR Policy / SR-TE**) basées sur les communautés BGP (*Color Extended Community*), le fonctionnement du **Binding SID (BSID)**, ainsi que le codage et le dépannage pratique sous Cisco IOS-XR et IOS-XE.

---

## 1. Extensions IGP & Distribution des Segments

L'une des plus grandes forces du Segment Routing est son intégration directe dans les protocoles de routage à état de lien (Link-State IGPs). Il n'y a plus aucun protocole auxiliaire à synchroniser : IS-IS et OSPF transportent les informations d'étiquettes et de capacités SR au travers de nouvelles structures d'extensions (TLVs et Opaque LSAs).

```
+-----------------------------------------------------------------------+
|                      EXTENSIONS IGP POUR SEGMENT ROUTING              |
+-----------------------------------┬-----------------------------------+
                                    |
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
+-----------------------+                       +-----------------------+
|    IS-IS Extensions   |                       |    OSPFv2 Extensions  |
|  (RFC 8667 / RFC 8668)|                       |      (RFC 8665)       |
| - Router Capability   |                       | - RI Opaque LSA       |
|   TLV 242 (SRGB)      |                       |   (SRGB Range)        |
| - Extended IS Reach.  |                       | - Extended Link LSA   |
|   TLV 22 (Adj-SID)    |                       |   (Adj-SID Sub-TLV)   |
| - IP Reachability     |                       | - Extended Prefix LSA |
|   TLV 135/235 (Prefix)|                       |   (Prefix-SID)        |
+-----------------------+                       +-----------------------+
```

### 1. Extensions IS-IS pour Segment Routing

IS-IS utilise sa structure native basée sur les **TLV (Type-Length-Value)** pour véhiculer la topologie SR :

* **TLV 242 (IS-IS Router Capability)** : Contient le sous-TLV *SR Capability* qui annonce la plage **SRGB** (Segment Routing Global Block) localement supportée par le routeur (ex: base `16000`, taille `8000`).
* **TLV 135 / TLV 235 (Extended IP Reachability)** : Transporte le sous-TLV *Prefix-SID*. Il associe une adresse IP (généralement une interface Loopback) à un **Index SR** ou un SID absolu.
* **TLV 22 / TLV 222 (Extended IS Reachability)** : Transporte le sous-TLV *Adj-SID*. Chaque adjacence physique est annoncée avec son étiquette locale dédiée (ex: `24001`), ses drapeaux de protection (F-flag, B-flag, V-flag, L-flag) et son poids d'ingénierie.

### 2. Extensions OSPFv2 / OSPFv3 pour Segment Routing

OSPF s'appuie sur le mécanisme des **Opaque LSAs** pour diffuser la signalisation SR :

* **Router Information (RI) Opaque LSA (Type 10/11)** : Transporte l'élément *SR-Algorithm TLV* (Algorithme 0 : SPF classique, Algorithme 1 : Strict SPF) et le *SRGB Range Sub-TLV*.
* **OSPFv2 Extended Prefix Opaque LSA** : Associe le *Prefix-SID Sub-TLV* aux préfixes annoncés par le routeur.
* **OSPFv2 Extended Link Opaque LSA** : Distribue les *Adj-SIDs Sub-TLVs* pour chaque liaison active.

---

## 2. Mécanique Approfondie du TI-LFA (Espaces P et Q)

En cas de rupture d'une liaison ou d'un nœud dans un réseau classique, la re-convergence de l'IGP prend généralement entre plusieurs centaines de millisecondes et quelques secondes. Le mécanisme **TI-LFA (Topology-Independent Loop-Free Alternate)** permet de garantir une bascule sub-50ms quel que soit le type de topologie réseau.

Pour comprendre comment le routeur Ingress (nœud de réparation $S$) calcule la pile de segments nécessaire pour contourner une panne sans créer de boucle, l'algorithme s'appuie sur la théorie des **Espaces P et Q**.

```
  [ Source S ] ──(Lien protégé)──► [ Nœud Panne D ] ────────► [ Destination Destination ]
       │                                                          ▲
       │                                                          │
       ▼                                                          │
  [ Espace P ] ─────────────────────────────────────────────► [ Espace Q ]
 (Nœuds joignables par S                    (Nœuds pouvant atteindre D
  sans passer par S-D)                       sans passer par S-D)
```

### 1. Définition de l'Espace P ($P$-Space)

L'**Espace P** par rapport au lien protégé $S-D$ est l'ensemble des nœuds $N$ que le nœud de source $S$ peut atteindre en utilisant le chemin le plus court (Shortest Path) **sans emprunter le lien défaillant $S-D$**.

$$
P(S, S-D) = \{ N \in V \mid \text{Distance}_{\text{sans } S-D}(S, N) < \text{Distance}_{\text{avec } S-D}(S, N) + \text{cout}(S-D) \}
$$

### 2. Définition de l'Espace Q ($Q$-Space)

L'**Espace Q** par rapport au lien protégé $S-D$ est l'ensemble des nœuds $N$ qui peuvent atteindre le nœud de destination $D$ (ou le nœud final) en utilisant leur chemin le plus court **sans emprunter le lien défaillant $S-D$**.

$$
Q(D, S-D) = \{ N \in V \mid \text{Distance}_{\text{sans } S-D}(N, D) < \text{Distance}(N, S) + \text{Distance}_{\text{sans } S-D}(S, D) \}
$$

### 3. Le Nœud PQ et l'Encapsulation TI-LFA

1. **Cas Simple ($P \cap Q \neq \emptyset$)** : Si l'intersection entre l'Espace P et l'Espace Q contient des nœuds communs, on choisit un **Nœud PQ**. $S$ encapsule simplement le paquet à destination du Node-SID de ce nœud PQ. Le paquet navigue naturellement vers PQ sans risquer de repasser par le lien défaillant.
2. **Cas Complexe ($P \cap Q = \emptyset$)** : Si les deux espaces ne se croisent pas, $S$ sélectionne un nœud $P$ (limite de son espace P) et un nœud $Q$ (entrée de l'espace Q), puis force l'itinéraire en empilant deux SIDs : `[Push Node-SID(P), Push Adj-SID(P->Q)]`.

---

## 3. Ingénierie de Trafic Avancée : SR Policy & BGP SR-TE

Le Segment Routing permet de dépasser les contraintes du routage au plus court chemin (ECMP/SPF) en guidant dynamiquement les flux selon des critères de contraintes : latence minimale, bande passante garantie, disjonction de chemin physique ou évitement de certaines zones réseau.

### 1. Concepts d'une politique SR (SR Policy)

Une **SR Policy** est un tunnel d'ingénierie de trafic configuré sur le routeur Ingress. Elle est identifiée de manière unique par le triplet :

1. **Headend** : Le routeur source où la politique est instanciée.
2. **Color** : Une valeur numérique (ex: `100` = Latence Basse, `200` = Bande Passante Élevée) définissant l'intention ou la classe de service.
3. **Endpoint** : L'adresse IP du routeur de destination (ex: Loopback du PE distant `10.0.0.9`).

```
+-----------------------------------------------------------------------------------+
| ROUTEUR INGRESS (Headend)                                                         |
|                                                                                   |
|  Paquet BGP reçu avec Extended Community: Color 100                               |
|        │                                                                          |
|        ▼                                                                          |
|  Match SR Policy (Color 100, Endpoint 10.0.0.9)                                   |
|        │                                                                          |
|        ├─► Segment-List 1 (Active)  : [Label 16003, Label 24005, Label 16009]     |
|        └─► Binding SID (BSID)      : 24099                                        |
+-----------------------------------------------------------------------------------+
```

### 2. Le rôle du Binding SID (BSID)

Le **Binding SID (BSID)** est un identifiant de segment local (étiquette MPLS ou adresse SRv6) attribué à une SR Policy spécifique.

* **Masquage de la complexité (Label Stack Limit)** : Un routeur source ou un équipement client peut simplement pousser un unique **BSID** (`24099`). Le routeur recevant ce BSID remplace l'étiquette par toute la liste de segments définie dans la politique (`[16003, 24005, 16009]`).
* **Isolation Inter-domaines** : Il permet d'enchaîner des politiques d'ingénierie de trafic à travers plusieurs domaines d'administration sans que le nœud Ingress n'ait à connaître la topologie exacte de l'ensemble du réseau.

### 3. Association Automatique via BGP Color Extended Community

L'association entre les préfixes de service (VPNv4, EVPN, Internet) et les SR Policies s'effectue automatiquement via BGP :

1. Le routeur Egress marque une route BGP avec une communauté étendue **Color** (ex: `Color:0:100`).
2. Le routeur Ingress reçoit la route BGP. Si une **SR Policy** correspond à la paire `(Color 100, Next-Hop BGP)`, le trafic est automatiquement steeré (orienté) dans la Segment-List correspondante sans aucune route statique.

---

## 4. Configuration Pratique : SR-MPLS et SR-TE (Cisco IOS-XR / IOS-XE)

### 1. Configuration SR-MPLS et IS-IS sous Cisco IOS-XR

Le code ci-dessous illustre l'activation de SR-MPLS avec IS-IS sur un routeur de cœur sous **Cisco IOS-XR** (ex: NCS 5500 / ASR 9000).

```text
! =====================================================================
! SECTION 1 : DEFINITION DU SRGB ET ALLOCATION DU PREFIX-SID (IOS-XR)
! =====================================================================
segment-routing
 global-block 16000 23999
!

interface Loopback0
 ipv4 address 10.0.0.3 255.255.255.255
!

! =====================================================================
! SECTION 2 : CONFIGURATION DE IS-IS AVEC EXTENSIONS SEGMENT ROUTING
! =====================================================================
router isis CORE-FABRIC
 net 49.0001.0000.0000.0003.00
 metric-style wide
 
 address-family ipv4 unicast
  metric-style wide
  segment-routing mpls
 !

 interface Loopback0
  address-family ipv4 unicast
   prefix-sid index 3
  !
 !

 interface TenGigE0/0/0/0
  point-to-point
  address-family ipv4 unicast
   fast-reroute per-prefix ti-lfa
  !
 !
!
```

### 2. Configuration d'une SR Policy dynamique sous Cisco IOS-XE

Exemple d'implémentation d'une **SR Policy** dédiée aux flux à basse latence sur **Cisco IOS-XE** :

```text
! =====================================================================
! SECTION 1 : CREATION DE LA SEGMENT-LIST EXPLICITE
! =====================================================================
segment-routing traffic-eng
 segment-list PATH_LOW_LATENCY
  index 10 mpls label 16002
  index 20 mpls label 24012
  index 30 mpls label 16009
 !

! =====================================================================
! SECTION 2 : DEFINITION DE LA POLITIQUE SR (COLOR 100, ENDPOINT PE-9)
! =====================================================================
 policy POLICY_VOICE_LOW_LATENCY
  color 100 endpoint 10.0.0.9
  candidate-paths
   preference 100
    explicit segment-list PATH_LOW_LATENCY
     weight 1
    !
   !
  !
  binding-sid mpls 24100
 !
!
```

---

## 5. Dépannage et Commandes de Diagnostic Avancées

Le diagnostic des anomalies Segment Routing en niveau Intermédiaire demande de vérifier l'alignement entre le plan de contrôle (IGP/BGP) et le plan de transfert (MPLS FIB / LFIB).

### 1. Verification des structures IS-IS SR et de la LFIB

* **Vérifier l'annonce des SIDs et du SRGB dans IS-IS (IOS-XR)** :
  ```text
  show isis segment-routing label table
  show isis database verbose | include Segment-Routing
  ```

* **Inspecter la table de transfert MPLS (LFIB) pour un préfixe distant** :
  ```text
  show mpls forwarding prefix 10.0.0.9/32 detail
  ```
  *Résultat attendu :* Présence des actions `Pop Label`, `Swap Label` ou de la pile d'étiquettes imposée (`Push [16002, 24012, 16009]`).

### 2. Diagnostic des SR Policies et du Binding SID

* **Vérifier l'état opérationnel des politiques SR-TE** :
  ```text
  show segment-routing traffic-eng policy name POLICY_VOICE_LOW_LATENCY
  ```
  S'assurer que le statut indique `Admin: up / Oper: up` et que le Binding SID `24100` est correctement alloué dans la LFIB.

* **Traceroute SR-MPLS explicite avec gestion de pile d'étiquettes** :
  ```text
  traceroute sr-mpls 10.0.0.9 segment-list 16002,24012,16009
  ```

---

## Points à retenir

* **Extensions IGP** : IS-IS (TLVs 242, 135, 22) et OSPF (Opaque LSAs) transportent nativement la topologie SR, le SRGB et les SIDs sans aucun protocole auxiliaire (suppression complète de LDP/RSVP-TE).
* **Maniement du TI-LFA** : Le calcul de protection repose sur les **Espaces P** (nœuds joignables par la source) et **Espaces Q** (nœuds rejoignant la destination) pour déterminer le **Nœud PQ** et insérer la pile d'étiquettes de secours garantissant un basculement $<50\text{ ms}$.
* **SR Policy & Traffic Engineering** : Une politique SR est identifiée par la paire `(Color, Endpoint)`. L'orientation du trafic s'effectue dynamiquement via la communauté BGP **Color Extended Community**.
* **Binding SID (BSID)** : Étiquette d'abstraction représentant une politique SR complexe. Il réduit la taille de la pile d'étiquettes pour les équipements clients et isole les domaines de routage.