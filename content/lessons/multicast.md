# Cours Intensif – Multicast (PIM, IGMP)  
**Niveau : Senior Network Administrator / CCIE**  
**Durée estimée : 2 jours (16 h)**  

---  

## Table des matières  

| # | Section | Durée estimée |
|---|---------|----------------|
| 1 | Introduction au multicast | 30 min |
| 2 | Modèle OSI & Protocoles de routage multicast | 45 min |
| 3 | IGMP – Versions, états, messages | 1 h |
| 4 | PIM – Architecture, modes et algorithmes | 2 h |
| 5 | Protocoles complémentaires (MSDP, MBGP, BGP‑MVPN) | 1 h |
| 6 | Conception d’une infrastructure multicast (design) | 1 h30 |
| 7 | Configuration Cisco – IOS/IOS‑XE/IOS‑XR | 2 h |
| 8 | Configuration Linux – `mrouted`, `pimd`, `smcroute` | 1 h30 |
| 9 | Optimisations (RP, DR, SSM, ASM) | 1 h |
|10 | Sécurité & contrôle d’accès (ACL, RPF, RP Guard) | 45 min |
|11 | Atelier de dépannage (lab) | 3 h |
|12 | Bonnes pratiques, checklist, références | 30 min |

> **Objectif** : Maîtriser le fonctionnement, le dimensionnement et le dépannage d’un réseau multicast d’entreprise ou de fournisseur, avec les technologies PIM Sparse‑Mode (SM), Dense‑Mode (DM), Sparse‑Dense (SD) et Source‑Specific Multicast (SSM).  

---  

## 1. Introduction au multicast  

| Concept | Description | Exemple d’usage |
|---------|-------------|-----------------|
| **Unicast** | 1‑to‑1, chaque flux a une destination unique. | SSH, HTTP |
| **Broadcast** | 1‑to‑all sur le même segment L2. | ARP, DHCP Discover |
| **Multicast** | 1‑to‑many, les flux sont répliqués uniquement où il y a des récepteurs intéressés. | IPTV, conférences vidéo, mise à jour de logiciels (WSUS) |

- **Adresse IPv4 multicast** : 224.0.0.0/4 (classe D).  
- **Adresse IPv6 multicast** : ff00::/8.  

### Pourquoi le multicast ?  

- **Économie de bande** : Un seul flux d’origine, réplication au niveau du routeur/switch.  
- **Scalabilité** : Des milliers de récepteurs sans surcharge du serveur source.  
- **Qualité de service (QoS)** : Possibilité de prioriser le trafic (DSCP, MPLS‑TE).  

---  

## 2. Modèle OSI & Protocoles de routage multicast  

| Couche OSI | Protocoles multicast | Rôle |
|-----------|----------------------|------|
| 2 (L2) | **Ethernet MAC 01‑00‑5E‑xx‑xx‑xx** | Encapsulation MAC, IGMP snooping. |
| 3 (L3) | **IGMP (v1‑v3)**, **MLD (IPv6)** | Gestion des groupes sur le LAN. |
| 3 (L3) | **PIM (DM, SM, SD)**, **DVMRP**, **MOSPF** | Distribution inter‑domaines. |
| 4 (Transport) | **UDP** (port 0‑65535) | Transport du flux réel. |
| 5‑7 | **RTSP, SIP, RTP, SSM** | Applications de streaming. |

### 2.1. Le principe du Reverse Path Forwarding (RPF)  

```
          +-------------------+
          |   Source (S)      |
          +--------+----------+
                   |
                (RPF)
                   |
   +--------+------+-------+--------+
   |        |      |       |        |
   R1       R2     R3      R4       R5   <-- Routers
   |        |      |       |        |
   +--------+------+-------+--------+
                   |
            +------+------+
            |   Receivers |
            +-------------+
```

- Un routeur accepte un paquet multicast **seulement** s’il arrive par l’interface qui mène à la source selon sa table de routage unicast (RPF check).  
- Si le paquet ne passe pas le RPF, il est **dropped** (prévention de boucles).  

---  

## 3. IGMP – Internet Group Management Protocol  

### 3.1. Versions & différences  

| Version | Types de messages | Fonctionnalités clés |
|---------|-------------------|----------------------|
| **IGMPv1** (1992) | **Membership Query**, **Membership Report** | Join only, aucune leave. |
| **IGMPv2** (1997) | Ajout **Leave Group**, **Membership Report (v2)**, **Query (v2)** | Rapide désabonnement, Querier election. |
| **IGMPv3** (2002) | **Membership Report (v3)** avec **source filtering** (IN/EXCLUDE) | SSM, contrôle d’accès par source. |

### 3.2. États du récepteur (host)  

```
+-----------+          +-----------+          +-----------+
|   Init    |---Join-->|   Join    |---Leave->|   Leave   |
+-----------+          +-----------+          +-----------+
```

- **Init** : Pas de groupe.  
- **Join** : Envoi d’un **Report**.  
- **Leave** : Envoi d’un **Leave** (v2+) ou expiration du timer (v1).  

### 3.3. États du commutateur (IGMP Snooping)  

| État du port | Action | Condition |
|--------------|--------|-----------|
| **Querier** | Envoie **General Query** toutes les 125 s (défaut). | Élection du plus bas IP. |
| **Member** | Forward multicast vers ce port. | Réception d’un **Report**. |
| **Non‑Member** | Bloquer le flux multicast. | Aucun Report reçu. |

### 3.4. Commandes Cisco – IGMP  

```text
! Activer IGMP sur un VLAN
interface Vlan10
 ip address 10.0.10.1 255.255.255.0
 ip igmp version 3
 ip igmp snooping vlan 10

! Vérifier les groupes IGMP
show ip igmp groups
show ip igmp interface Vlan10
show ip igmp snooping vlan 10
```

### 3.5. Commandes Linux – IGMP  

```bash
# Afficher les groupes IGMP sur une interface
ip maddr show dev eth0

# Rejoindre un groupe (exemple : 239.1.1.1)
ip maddr add 239.1.1.1 dev eth0

# Quitter le groupe
ip maddr del 239.1.1.1 dev eth0
```

---  

## 4. PIM – Protocol Independent Multicast  

### 4.1. Modes de fonctionnement  

| Mode | Description | Cas d’usage |
|------|-------------|------------|
| **PIM Dense‑Mode (DM)** | Flood‑and‑prune. Tous les RPF sont initialement remplis, puis les branches inutiles sont « pruned ». | Réseaux très densément peuplés, diffusion locale. |
| **PIM Sparse‑Mode (SM)** | Source‑based, RP (Rendez‑vous Point) centralisé. Utilisé par défaut dans la plupart des opérateurs. | IPTV, diffusion à grande échelle. |
| **PIM Sparse‑Dense (SD)** | Hybrid : commence en SM, bascule en DM si le trafic devient dense. | Environnements mixtes. |
| **PIM Source‑Specific Multicast (SSM)** | Pas de RP, les récepteurs spécifient la source (IGMPv3). | Sécurité accrue, streaming unicast‑like. |

### 4.2. Architecture SM – RP, DR, Source Tree, Shared Tree  

```
               (S) Source
                 |
                 | (S,G) Shortest‑Path Tree (SPT)
                 |
            +----+----+----+----+
            |         |         |
          (R1)       (R2)      (R3)   <-- Routers
            |         |         |
            +----+----+----+----+
                 |
                 | (R,G) Shared Tree (RP)
                 |
               (RP) Rendez‑vous Point
```

- **RP (Rendez‑vous Point)** : Point d’ancrage du *shared tree* (R,G).  
- **DR (Designated Router)** : Sur chaque LAN, gère les IGMP/MLD et le **PIM Join/Prune**.  
- **S,G** : Flux spécifique à une source.  
- **R,G** : Flux partagé via le RP.  

### 4.3. Algorithmes de sélection du RP  

| Méthode | Description | Avantages | Inconvénients |
|---------|-------------|-----------|---------------|
| **Static RP** | Configuration manuelle (ex. `ip pim rp-address`). | Simplicité, prévisibilité. | Pas de redondance native. |
| **Bootstrap Router (BSR)** | Élection dynamique d’un BSR qui diffuse les RP via **BSR messages**. | Redondance, auto‑configuration. | Complexité, besoin de BSR. |
| **Any‑Source RP (ASRP) via MSDP** | RP partagé entre plusieurs domaines via **MSDP**. | Évolutif, multi‑domaines. | Charge supplémentaire, besoin de sessions MSDP. |
| **PIM‑SSM** | Pas de RP. | Sécurité, faible overhead. | Nécessite IGMPv3/MLDv2, source connue. |

### 4.4. États du PIM (Router)  

| État | Message déclencheur | Action |
|------|---------------------|--------|
| **NoInfo** | Aucun Join reçu. | Pas de (S,G) ou (R,G) dans la table. |
| **Prune‑Pending** | Prune reçu, timer en cours. | Attend le **Prune‑Timer** avant de supprimer l’arbre. |
| **Joined** | Join reçu, RPF OK. | Crée (S,G) ou (R,G) entry, envoie **Join** en amont. |
| **Assert** | Conflit de source sur le même segment. | L’interface avec le **metric le plus bas** garde le flux (Assert). |

### 4.5. Commandes Cisco – PIM  

```text
! Activer PIM Sparse‑Mode sur une interface
interface GigabitEthernet0/0/1
 ip address 192.168.1.1 255.255.255.0
 ip pim sparse-mode
 ip igmp version 3
 ip igmp snooping

! Configurer un RP statique (IPv4)
ip pim rp-address 10.0.0.1 255.255.255.0 10.0.0.254

! Activer BSR (Bootstrap Router)
ip pim bsr-candidate 10.0.0.2 priority 120

! Vérifier les états PIM
show ip pim neighbor
show ip pim rp
show ip pim rp mapping
show ip pim interface
show ip pim join
show ip pim assert

! Forcer un Assert (debug)
debug ip pim assert
```

### 4.6. Commandes Linux – `pimd` (PIM‑SM)  

```bash
# Installer le démon (Debian/Ubuntu)
apt-get install pimd

# Fichier de configuration /etc/pimd.conf (exemple)
# -------------------------------------------------
# Interface sur laquelle PIM doit être activé
interface eth0 {
    pimsm = true;          # PIM Sparse‑Mode
    rp = 10.1.1.1;         # RP statique
}
# Activer le daemon
systemctl start pimd
systemctl enable pimd

# Vérifier les tables PIM
pimdctl show pim neighbors
pimdctl show pim rp
pimdctl show pim routes
```

---  

## 5. Protocoles complémentaires  

| Protocole | Fonction | Interaction avec PIM |
|-----------|----------|----------------------|
| **MSDP (Multicast Source Discovery Protocol)** | Propagation des sources (S,G) entre différents RP. | Nécessaire pour *inter‑domain* ASM. |
| **MBGP (Multiprotocol BGP)** | Transport de routes multicast (VPN‑MPLS, VPLS). | Distribue les routes (S,G) ou (R,G) dans les réseaux MPLS. |
| **BGP‑MVPN (Multicast VPN)** | Encapsulation de multicast dans des VPN MPLS. | Utilise **PIM‑SM** à l’intérieur du VPN. |
| **PIM‑SSM** | SSM (no RP) – source‑specific. | Remplace IGMPv2/IGMPv3 *INCLUDE* mode. |
| **IGMPv3/MLDv2** | Filtrage source (INCLUDE/EXCLUDE). | Nécessaire pour SSM et contrôle d’accès. |

---  

## 6. Conception d’une infrastructure multicast  

### 6.1. Étapes de design  

1. **Analyse du trafic**  
   - Nombre de sources, nombre de récepteurs, bande passante requise.  
   - Utiliser **NetFlow** ou **sFlow** pour établir les flux.  

2. **Choix du modèle**  
   - **ASM** (Any‑Source Multicast) → RP obligatoire, plus flexible.  
   - **SSM** → Simplicité, sécurité, pas de RP.  

3. **Topologie**  
   - **Core** : PIM‑SM avec RP(s) redondants (static + BSR).  
   - **Distribution** : PIM‑DM ou **PIM‑SD** si le réseau est dense.  
   - **Edge** : IGMP Snooping, PIM‑DR, QoS.  

4. **Redondance du RP**  
   - **Anycast RP** (identical IP on multiple routers) + **BGP** for RP advertisement.  

5. **Sécurité**  
   - **RPF strict** (source‑based).  
   - **ACL** sur (S,G) ou (R,G).  
   - **RP Guard** (Cisco) pour empêcher le spoofing RP.  

### 6.2. Exemple de schéma logique (ASCII)  

```
                +-------------------+
                |   Core Router R0  |
                |  (PIM SM, RP=10.0.0.1) |
                +--------+----------+
                         |
                +--------+--------+--------+
                |        |        |        |
          +-----+-----+  +-----+-----+  +-----+-----+
          |  R1 (DR)  |  |  R2 (DR)  |  |  R3 (DR)  |
          |  IGMPv3   |  |  IGMPv3   |  |  IGMPv3   |
          +-----+-----+  +-----+-----+  +-----+-----+
                |                |                |
        +-------+-------+  +-----+-----+  +-------+-------+
        | VLAN 10 (IPTV) |  | VLAN 20  |  | VLAN 30 (VOIP)|
        +---------------+  +-----------+  +---------------+

```

---  

## 7. Configuration Cisco – Cas pratique  

### 7.1. Topologie de laboratoire  

```
[HostA]---[R1]---+---[R0]---+---[R2]---[HostB]
                |          |
               [R3]        |
                |          |
              [HostC]     [HostD]
```

- **R0** : Core, RP (static) 10.0.0.1/24.  
- **R1/R2/R3** : Edge, DR sur chaque LAN, IGMPv3.  

### 7.2. Configuration des routeurs  

#### R0 – Core (RP)  

```text
hostname R0
interface Loopback0
 ip address 10.0.0.1 255.255.255.255
 ip pim sparse-mode
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.0
 ip pim sparse-mode
!
interface GigabitEthernet0/1
 ip address 10.2.2.1 255.255.255.0
 ip pim sparse-mode
!
ip multicast-routing
ip pim rp-address 10.0.0.1 255.255.255.255 10.0.0.1
!
router ospf 1
 network 10.0.0.0 0.0.0.255 area 0
 network 10.1.1.0 0.0.0.255 area 0
 network 10.2.2.0 0.0.0.255 area 0
!
```

#### R1 – Edge (DR)  

```text
hostname R1
interface GigabitEthernet0/0
 ip address 10.1.1.2 255.255.255.0
 ip pim sparse-mode
 ip igmp version 3
 ip igmp snooping vlan 10
!
interface Loopback0
 ip address 10.1.1.2 255.255.255.255
!
ip multicast-routing
!
router ospf 1
 network 10.1.1.0 0.0.0.255 area 0
!
```

#### R2 – Edge (DR)  

```text
hostname R2
interface GigabitEthernet0/0
 ip address 