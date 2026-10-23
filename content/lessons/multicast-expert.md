# Architecture Multicast Avancée : Protocoles, Ingénierie L2/L3 et Sécurité Entreprise

Ce document de niveau expert détaille la théorie des systèmes, les protocoles de routage inter-domaine et intra-domaine, l'intégration du Multicast au sein des fabriques modernisées (VXLAN/EVPN), ainsi que le diagnostic réseau à grande échelle.

---

## 1. Mécanique Fondamentale et Algorithmes de Routage Multicast

### 1.1 Le Contrat RPF (Reverse Path Forwarding) et Invariant de Non-Bouclage

Contrairement au routage Unicast qui oriente le paquet en fonction de son **adresse de destination**, le routage Multicast prend ses décisions en fonction de **l'adresse source** ($S$).

#### Algorithme de Vérification RPF :
Lorsqu'un paquet IPv4 Multicast avec la source $S$ et le groupe $G$ arrive sur l'interface $I_{in}$ :

1. Le routeur consulte sa table de routage Unicast (RIB) pour trouver la route correspondant à l'adresse de la source $S$.
2. Le routeur identifie l'interface de sortie Unicast $I_{expected}$ et le prochain saut (*Next-Hop*) associés à $S$.
3. **Condition RPF :**
   $$\text{Si } I_{in} == I_{expected} \implies \text{Test RPF Réussi (Forwarding)}$$
   $$\text{Si } I_{in} \neq I_{expected} \implies \text{Test RPF Échoué (Drop Packet)}$$

```
                  [ Source S: 10.10.10.1 ]
                             │
                             ▼
                    [ Switch Core L3 ]
                       │          │
         Interface GE0/0          Interface GE0/1
         (Chemin Unicast)         (Chemin Secondaire)
                       │          │
                       ▼          ▼
             ┌──────────────────────────┐
             │    Routeur Multicast     │
             └──────────────────────────┘
             • Paquet arrivant sur GE0/0 ──► RPF OK  ──► Transmis sur OIL
             • Paquet arrivant sur GE0/1 ──► RPF FAIL ──► Droppé immédiatement
```

#### RPF Vector & Asymétrie de Routage :
En présence d'un routage Unicast asymétrique (où le chemin Aller $A \to B$ diffère du chemin Retour $B \to A$), la vérification RPF classique peut échouer. Les extensions protocolaires (ex: *PIM RPF Vector*) permettent d'inclure une adresse explicite de prochain saut RPF dans les messages de signalisation PIM.

---

## 2. Anatomie de PIM-Sparse Mode (PIM-SM) et Évolution des Arbres

### 2.1 Les Tables d'État (mroute) : `(*, G)` vs `(S, G)`

Chaque routeur Multicast maintient une table d'état applicative (*Multicast Routing Table* - `mroute`).

* **Entrée `(*, G)` (Rendezvous Point Tree / Shared Tree) :**
  * **Wildcard wildcard :** Représente toutes les sources émettant vers le groupe $G$.
  * **Incoming Interface (IIF) :** Interface tournée vers le **Rendezvous Point (RP)**.
  * **Outgoing Interface List (OIL) :** Liste des interfaces menant aux récepteurs actifs ou aux routeurs en aval.

* **Entrée `(S, G)` (Shortest Path Tree / Source Tree) :**
  * **Specific Source :** Représente la source unique $S$ émettant vers le groupe $G$.
  * **Incoming Interface (IIF) :** Interface tournée vers la **Source $S$** (obtenue via le test RPF Unicast vers $S$).
  * **Outgoing Interface List (OIL) :** Interfaces actives pour transmettre le flux spécifique.

---

### 2.2 Séquence Complète du Flux de Signalisation PIM-SM

```
 [ Source S ]           [ First-Hop Router (FHR) ]          [ Rendezvous Point (RP) ]          [ Last-Hop Router (LHR) ]          [ Receiver ]
      │                                 │                                    │                                  │                        │
      │                                 │                                    │ ◄──────── PIM Join (*,G) ────────┤ (IGMP Report reçu)     │
      │                                 │                                    │                                  │                        │
      ├────── Flux UDP Multicast ──────►│                                    │                                  │                        │
      │                                 │ ─── PIM Register (Unicast Encaps) ─►│                                  │                        │
      │                                 │     (Contient le paquet data)      │ ────── Flux décapsulé (*,G) ─────►│                        │
      │                                 │                                    │                                  │ ─── Flux vers hôte ───►│
      │                                 │ ◄─── PIM Join (S,G) (Native Tree) ─┤                                  │                        │
      │                                 │                                    │                                  │                        │
      │ ◄────── Native Multicast ───────┤ ════════ Native Multicast ════════►│                                  │                        │
      │                                 │                                    │                                  │                        │
      │                                 │ ─── PIM Register-Stop ────────────►│                                  │                        │
      │                                 │                                    │                                  │                        │
      │                                 │                                    │ ◄─── PIM Join (S,G) (SPT Switch) ┤                        │
      │                                 │ ◄──────────────── PIM Join (S,G) ─────────────────────────────────────┤                        │
      │                                 │                                    │                                  │                        │
      │ ◄────────────────────────────── native Multicast Direct (SPT) ─────────────────────────────────────────┤                        │
      │                                 │                                    │ ─── PIM Prune (S,G) ────────────►│                        │
```

#### Étape 1 : Rejointoiement du Récepteur
1. Le récepteur envoie un **IGMP Membership Report** pour le groupe $G$.
2. Le **LHR (Last-Hop Router)** crée une entrée `(*, G)` et transmet un message **PIM Join (*, G)** saut par saut vers le **RP**.
3. Chaque routeur intermédiaire crée l'état `(*, G)` et ajoute l'interface incidente à son `OIL`.

#### Étape 2 : Enregistrement de la Source
1. La source $S$ commence à émettre des paquets vers $G$.
2. Le **FHR (First-Hop Router)** intercepte le flux, crée une entrée `(S, G)`.
3. Le FHR encapsule le paquet original dans un message Unicast **PIM Register** et l'envoie au RP.
4. Le RP déballe le paquet et le transmet le long de l'arbre partagé `(*, G)`.

#### Étape 3 : Transition vers l'Arbre Natif (RP-Tree)
1. Le RP envoie un message **PIM Join (S, G)** en direction du FHR pour établir un arbre natif non encapsulé.
2. Dès que les paquets natifs `(S, G)` arrivent au RP, celui-ci répond au FHR par un **PIM Register-Stop** pour mettre fin à l'encapsulation Unicast.

#### Étape 4 : Bascule SPT (Shortest Path Tree Switchover)
1. Par défaut (seuil de débit à 0 kbps), dès que le **LHR** reçoit le premier paquet du flux via l'arbre partagé `(*, G)`, il initie la bascule vers le chemin direct vers la source.
2. Le LHR envoie un **PIM Join (S, G)** vers la source $S$.
3. Dès que le flux arrive par l'arbre direct `(S, G)`, le LHR envoie un **PIM Prune (S, G)** vers le RP pour couper la branche redondante via l'arbre partagé.

---

## 3. Stratégies d'Infrastructures RP : Auto-RP, BSR et Anycast-RP

Pour éviter un point de défaillance unique (*Single Point of Failure*), le rôle de RP doit être redondé et découvert dynamiquement.

### 3.1 Comparatif des Mécanismes de Découverte de RP

| Critère | Static RP | Auto-RP (Propriétaire Cisco) | PIM Bootstrap Router (BSR - RFC 5059) |
| :--- | :--- | :--- | :--- |
| **Standardisation** | Indépendant | Propriétaire Cisco | Standard IETF (Open) |
| **Transport** | Configuration manuelle | Dense-Mode Flooding (`224.0.1.39`/`224.0.1.40`) | Messages PIM BSR Bipoints (`224.0.0.13`) |
| **Sélection du RP** | N/A | Le RP avec la plus haute IP gagne | Calcul de Hash-Function algorithmique par groupe |
| **Fiabilité** | Pas de bascule dynamique | Élections dynamiques via Candidate-RP | Élections dynamiques + Répartition via Hash |

---

### 3.2 Anycast-RP avec MSDP (Multicast Source Discovery Protocol)

Dans les architectures multi-domaines ou intra-domaine à très haute disponibilité, plusieurs RP partagent **exactement la même adresse IP Unicast** (ex: `10.255.255.1/32` via Loopback).

```
   [ Source S ]                                                         [ Récepteur ]
        │                                                                    │
        ▼                                                                    ▼
┌───────────────┐        Sessions MSDP Peer (TCP 639)         ┌───────────────┐
│  RP-1 (PIM)   │ ◄─────────────────────────────────────────► │  RP-2 (PIM)   │
│ 10.255.255.1  │        Message Source-Active (SA)           │ 10.255.255.1  │
└───────────────┘                                             └───────────────┘
```

1. **Routage Unicast Anycast :** Les routeurs du réseau rejoignent le RP le plus proche au sens de la métrique IGP (OSPF/IS-IS).
2. **Découverte de Source via MSDP (RFC 3618) :**
   * La source émet vers **RP-1**.
   * RP-1 crée l'état `(S, G)` et génère un message MSDP **Source-Active (SA)** contenant $(S, G)$ et l'adresse du FHR.
   * RP-1 transmet ce message SA à ses pairs MSDP (dont **RP-2**).
   * **RP-2** reçoit le message SA. Comme il possède des récepteurs inscrits en `(*, G)`, il envoie un `PIM Join (S, G)` vers la source $S$.

---

## 4. Multicast dans les Fabriques Modernes : VXLAN et BGP-EVPN

L'acheminement du trafic Multicast dans un Overlay VXLAN sans inonder le sous-jacent (*Underlay*) est un enjeu d'ingénierie majeur.

### 4.1 BGP-EVPN Route Type 6, 7 & 8 (Selective Multicast - SMET)

Pour optimiser le transport BUM (*Broadcast, Unknown Unicast, Multicast*), l'IETF a défini des routes EVPN spécifiques pour le Multicast (RFC 9251 / RFC 9252).

```
 [ Leaf 1 (NVE1) ] ────── EVPN Route Type 6 (SMET) ──────► [ Leaf 2 (NVE2) ]
 (Récepteur local)                                         (Source rattachée)
  IGMP Join 239.1.1.1                                       Génère VXLAN Data
```

1. **Route Type 6 (Selective Multicast Ethernet Tag - SMET) :**
   Lorsqu'un hôte derrière le **Leaf 1** émet un IGMP Join pour `239.1.1.1`, le Leaf 1 génère une route EVPN Type 6 annonçant :
   * Le VNI concerné.
   * L'adresse du Groupe Multicast (`239.1.1.1`) et optionnellement la Source.
   * L'adresse IP de son interface d'encapsulation (VTEP IP).

2. **Réplication Sélective (Ingress Replication) :**
   Le **Leaf 2** (connecté à la source) lit la route Type 6 et ajoute le VTEP du Leaf 1 à sa liste de réplication Head-End. Le trafic Multicast est récapitulé en Unicast VXLAN uniquement vers les Leafs ayant des récepteurs déclarés.

---

## 5. Dépannage et Commandes d'Ingénierie Systèmes

### 5.1 Matrice de Diagnostic Cisco IOS-XE / NX-OS

```bash
# 1. Vérifier la table de routage Multicast (mroute)
show ip mroute 239.10.10.1

# Exemple de sortie interprétée :
# (10.1.1.50, 239.10.10.1), 00:04:12/00:02:47, flags: FT
#   Incoming interface: GigabitEthernet0/0/0, RPF nbr 10.1.1.1
#   Outgoing interface list:
#     GigabitEthernet0/0/1, Forward/Sparse, 00:04:12/00:02:47

# 2. Diagnostiquer les échecs RPF
show ip rpf 10.1.1.50

# 3. Inspecter les voisins PIM
show ip pim neighbor

# 4. Analyser les groupes IGMP enregistrés sur une interface
show ip igmp groups GigabitEthernet0/0/1 detail
```

### 5.2 Capture de Trafic et Validation avec TShark / Wireshark

Filtrer les messages de contrôle PIM et IGMP au niveau binaire :

```bash
# Capture des paquets IGMPv3 et PIM Join/Prune
tshark -i eth0 -Y "igmp || pim" -T fields -e frame.time -e ip.src -e ip.dst -e igmp.maddr -e pim.dir.group

# Analyse des options IGMPv3 (Report type 4 = CHANGE_TO_INCLUDE_MODE)
tshark -r capture.pcap -Y "igmp.record_type == 4"
```

---

## 6. Synthèse des Flags et Timers Critiques

| Paramètre | Valeur par Défaut | Impact Métier / Recommandation |
| :--- | :--- | :--- |
| **PIM Hello Interval** | 30 secondes | Fréquence de découverte des voisins. Réduire à 1s pour le Fast-Convergence. |
| **PIM Holdtime** | $3.5 \times \text{Hello}$ (105s) | Délai avant déclenchement de panne d'un voisin PIM. |
| **IGMP Query Interval** | 125 secondes | Périodicité des requêtes d'état envoyées par le Querier. |
| **IGMP Query Response Interval** | 10 secondes | Temps accordé aux hôtes pour répondre (évite la collision d'éclats). |
| **SPT Switchover Threshold** | `0 kbps` (Immédiat) | Force le passage automatique de l'arbre RP à l'arbre direct Source (SPT). |
