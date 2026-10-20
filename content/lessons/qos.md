# Cours intensif – Qualité de Service (QoS)  
**Niveau : Administrateur Réseau Senior / CCIE**  
**Durée estimée : 2 jours (environ 16 h de formation)**  

---

## Table des matières  

| # | Section | Durée approximative |
|---|---------|---------------------|
| 1 | Introduction & concepts fondamentaux | 1 h |
| 2 | Modèle OSI et points d’application de la QoS | 1 h |
| 3 | Classification, Marquage & Policing | 2 h |
| 4 | Métriques de performance (latence, jitter, perte) | 1 h |
| 5 | Algorithmes de mise en forme (shaping) & de limitation (policing) | 2 h |
| 6 | Files d’attente : FIFO, PQ, WFQ, CBWFQ, LLQ, QOS‑Map | 2 h |
| 7 | QoS sur les technologies WAN (MPLS, Metro‑Ethernet, LTE) | 2 h |
| 8 | QoS sur les datacenters (VXLAN, NVGRE, DCB) | 1,5 h |
| 9 | Configuration Cisco IOS/IOS‑XR/IOS‑XE | 2 h |
|10 | Configuration Linux (tc, iptables, nftables) | 1,5 h |
|11 | Atelier de dépannage – Scénario complet | 2 h |
|12 | Bonnes pratiques, checklist et références | 0,5 h |

> **Objectif** : Maîtriser la conception, le déploiement, la validation et le dépannage d’une politique QoS complète sur des réseaux d’entreprise, de data‑center et d’opérateurs, en s’appuyant sur les standards IETF, ITU‑T et les implémentations Cisco/Juniper/Linux.

---

## 1. Introduction & concepts fondamentaux  

### 1.1 Pourquoi la QoS ?  

| Cas d’usage | Besoin QoS | Conséquence sans QoS |
|------------|------------|----------------------|
| VoIP / téléphonie IP | Latence < 150 ms, Jitter < 30 ms, perte < 1 % | Gigue, coupures, mauvaise qualité audio |
| Vidéo en temps réel (Webex, Teams) | Bande passante réservée, faible jitter | Artefacts vidéo, freeze |
| Applications critiques (SCADA, trading) | Priorité élevée, perte nulle | Risques de sécurité, pertes financières |
| Backup / replication | Bande passante non critique, tolérance à la latence | Saturation du lien, impact sur les services temps réel |
| IoT / capteurs | Small packets, low jitter | Données corrompues, perte de synchronisation |

### 1.2 Principes de base  

| Concept | Définition | Exemple |
|---------|------------|---------|
| **Classification** | Décision sur la base de champs d’en‑tête (IP, TCP/UDP, DSCP, MPLS EXP) | `match ip dscp ef` |
| **Marquage (Marking)** | Attribution d’un champ (DSCP, COS, EXP) pour transport | `set dscp af41` |
| **Policing** | Limite le débit d’un flux, génère du *drop* ou du *remark* | `police 10Mbps 2k conform-action transmit exceed-action drop` |
| **Shaping** | Bufferise et lisse le trafic pour ne pas dépasser un débit | `shape average 5Mbps` |
| **Scheduling** | Décide quel paquet sortir en premier (PQ, WFQ, CBWFQ…) | `priority percent 30` |
| **Congestion Avoidance** | RED, WRED, ECN – prévient la perte massive | `random-detect dscp af41 15 30 5` |
| **Admission Control** | Refuse de créer de nouvelles sessions si les ressources sont saturées | `policy-map type qos admission-control` |

---

## 2. Modèle OSI et points d’application de la QoS  

```
+---------------------------+-------------------------------+
|   Couche 7 – Application  |   Détection d’applications     |
|   (SIP, RTP, HTTP, SSH)  |   DPI, classification L7      |
+---------------------------+-------------------------------+
|   Couche 4 – Transport    |   Ports TCP/UDP, flags SYN    |
+---------------------------+-------------------------------+
|   Couche 3 – Réseau       |   IP src/dst, TOS/DSCP, TTL   |
+---------------------------+-------------------------------+
|   Couche 2 – Liaison      |   VLAN ID, 802.1p COS, MPLS  |
+---------------------------+-------------------------------+
|   Couche 1 – Physique     |   Débit du lien, erreurs CRC  |
+---------------------------+-------------------------------+
```

- **Points d’injection du marquage**  
  - **Edge (ingress) router** : classification + marquage (DSCP).  
  - **Switch d’accès** : 802.1p COS → DSCP mapping (Q‑in‑Q).  
  - **Core** : uniquement *re‑mark* (exp) ou *preserve* (DSCP).  

- **Propagation du marquage**  
  - **IP** : DSCP (6 bits) → transporté à chaque hop.  
  - **MPLS** : EXP (3 bits) + Bottom of Stack (BoS) → souvent mappé à DSCP.  
  - **Ethernet** : 802.1p (3 bits) + PCP → utilisé sur LAN.  

---

## 3. Classification, Marquage & Policing  

### 3.1 Classification Cisco IOS  

```text
class-map match-any VOIP-CLASS
  description  VoIP traffic (SIP + RTP)
  match protocol sip
  match access-group name VOIP-ACL

class-map match-all VIDEO-CLASS
  description  Video (H.264, RTP, ports 5004-5006)
  match dscp ef
  match access-group name VIDEO-ACL
```

- **`match-any`** : le trafic qui satisfait *l’une* des conditions.  
- **`match-all`** : le trafic doit satisfaire *toutes* les conditions.  

### 3.2 Marquage (DSCP / COS)  

```text
policy-map MARK-TRAFFIC
  class VOIP-CLASS
    set dscp ef
  class VIDEO-CLASS
    set dscp af41
  class class-default
    set dscp default
```

| DSCP | Classe IETF | Description | Priorité |
|------|-------------|-------------|----------|
| EF   | Expedited Forwarding | Traffic à latence ultra‑faible (VoIP) | 5 |
| AF41 | Assured Forwarding 41 | Vidéo HD, flux média | 4 |
| AF31 | Assured Forwarding 31 | Traffic d’entreprise standard | 3 |
| CS2  | Class Selector 2 | Signaling, contrôle | 2 |
| CS0  | Best‑Effort | Tout le reste | 0 |

### 3.3 Policing – Exemple Cisco  

```text
policy-map POLICE-VOIP
  class VOIP-CLASS
    police 64k 8000 exceed-action drop
    police 128k 16000 exceed-action remark dscp cs2
```

- **`police <cps> <burst>`** : *Committed Information Rate* (CIR) + *burst* (CBurst).  
- **`exceed-action`** : `drop` ou `remark` (exemple : downgrade vers CS2).  

### 3.4 Policing sous Linux (tc)  

```bash
# 1. Créez une classe HTB de 10 Mbps
tc qdisc add dev eth0 root handle 1: htb default 30
tc class add dev eth0 parent 1: classid 1:10 htb rate 10mbit ceil 10mbit

# 2. Police 64 kbps pour le trafic DSCP 46 (EF)
tc filter add dev eth0 protocol ip parent 1:0 prio 1 \
    u32 match ip dsfield 0xb800 0xfc00 flowid 1:10 police rate 64kbit burst 8k drop

# 3. Marquage DSCP en sortie (iptables + mangle)
iptables -t mangle -A POSTROUTING -p udp --dport 5060 -j DSCP --set-dscp-class EF
```

---

## 4. Métriques de performance  

| Métrique | Unité | Impact sur les services | Méthode de mesure |
|----------|-------|--------------------------|-------------------|
| **Latence** | ms | Gigue, délai de conversation | `ping`, `traceroute -I`, NetFlow RTT |
| **Jitter** | ms | Artefacts audio/vidéo | `rtp‑stats`, `iperf3 -J` |
| **Perte** | % | Corruption de flux, retransmissions | `snmp` `ifInDiscards`, `pcap` |
| **Bande passante** | Mbps | Saturation, congestion | `sFlow`, `NetFlow`, `iperf3` |
| **Utilisation du buffer** | % | Bufferbloat, latence accrue | `show queue`, `tc -s qdisc` |

> **Règle d’or** : *latence + jitter + perte ≤ seuil de l’application*.  
> Exemple VoIP (ITU‑G.114) : latence < 150 ms, jitter < 30 ms, perte < 1 %.

---

## 5. Algorithmes de mise en forme (shaping) & de limitation (policing)  

### 5.1 Shaping (HTB, CBQ) – Cisco  

```text
policy-map SHAPE-OUT
  class class-default
    shape average 5Mbps
```

- **HTB** (Hierarchical Token Bucket) : crée des *buckets* hiérarchiques, chaque bucket possède un débit garanti (`rate`) et un débit maximal (`ceil`).  

### 5.2 Policing – Cisco  

```text
policy-map POLICE-DEFAULT
  class class-default
    police 20Mbps 2000 conform-action transmit exceed-action drop
```

- **CIR** = débit garanti, *exceed-action* = drop ou remark.  

### 5.3 Linux – `tc` shaping avec `tbf`  

```bash
tc qdisc add dev eth1 root tbf rate 5mbit burst 32kbit latency 50ms
```

- **`tbf`** (Token Bucket Filter) : idéal pour limiter le débit sortant sans créer de file d’attente importante.  

### 5.4 Comparatif shaping vs policing  

| Caractéristique | Shaping | Policing |
|-----------------|---------|----------|
| Buffer interne | Oui (queue) | Non (pas de buffer) |
| Action sur dépassement | Retarde le trafic | Drop ou remark |
| Impact sur latence | Augmente (buffer) | Aucun (drop immédiat) |
| Utilisation typique | WAN‑to‑LAN, trafic sortant | Entrée, contrôle d’abus (DoS) |
| Complexité | Plus élevée | Simple |

---

## 6. Files d’attente – Scheduler  

### 6.1 Principaux schedulers Cisco  

| Scheduler | Principe | Cas d’usage |
|-----------|----------|-------------|
| **Priority Queue (PQ)** | File strictement prioritaire, aucune forme de partage | VoIP (EF) |
| **Weighted Fair Queueing (WFQ)** | Partage proportionnel au poids, bonne équité | Traffic mixte |
| **Class‑Based WFQ (CBWFQ)** | WFQ appliqué par classe (DSCP) | Réseaux d’entreprise |
| **Low‑Latency Queue (LLQ)** | PQ + CBWFQ (PQ en tête) | VoIP + data |
| **Hierarchical QoS (HQoS)** | Multi‑niveau, combine shaping + scheduling | WAN, MPLS, Data‑center |

### 6.2 Exemple complet de configuration QoS sur un routeur Cisco (IOS‑XE)  

```text
!-------------------------------------------------
! 1. Définir les ACLs de classification
!-------------------------------------------------
ip access-list extended VOIP-ACL
  permit udp any any eq 5060          ! SIP
  permit udp any any range 16384 32767 ! RTP (dyn)

ip access-list extended VIDEO-ACL
  permit udp any any eq 5004
  permit udp any any eq 5005

!-------------------------------------------------
! 2. Class‑maps
!-------------------------------------------------
class-map match-any VOIP-CLASS
  match access-group name VOIP-ACL

class-map match-any VIDEO-CLASS
  match access-group name VIDEO-ACL

!-------------------------------------------------
! 3. Policy‑map de marquage
!-------------------------------------------------
policy-map MARK-TRAFFIC
  class VOIP-CLASS
    set dscp ef
  class VIDEO-CLASS
    set dscp af41
  class class-default
    set dscp default

!-------------------------------------------------
! 4. Policy‑map de shaping & scheduling (LLQ)
!-------------------------------------------------
policy-map LLQ-OUT
  class VOIP-CLASS
    priority percent 30   ! 30 % du débit total en PQ
  class VIDEO-CLASS
    bandwidth percent 40  ! 40 % en CBWFQ
    queue-limit 1000
  class class-default
    bandwidth percent 30
    fair-queue

!-------------------------------------------------
! 5. Appliquer sur l’interface
!-------------------------------------------------
interface GigabitEthernet0/0/0
  service-policy input MARK-TRAFFIC
  service-policy output LLQ-OUT
  service-policy output SHAPE-OUT   ! shaping global 5 Mbps
```

### 6.3 ASCII Diagram – Flow QoS End‑to‑End  

```
+----------------+   +----------------+   +----------------+   +----------------+
|  Edge Router   |---|  Core Switch   |---|  MPLS PE       |---|  Edge Router   |
| (Ingress Mark) |   | (QoS Preserve) |   | (EXP ↔ DSCP)   |   | (Egress Shaping)|
+----------------+   +----------------+   +----------------+   +----------------+
        |                     |                     |                     |
        | DSCP=EF             | DSCP=EF             | EXP=5 (mapped)      | Policing 10Mbps
        v                     v                     v                     v
   +----------+           +----------+           +----------+           +----------+
   |  VoIP    |  ---->    |  VoIP    |  ---->    |  VoIP    |  ---->    |  VoIP    |
   +----------+           +----------+           +----------+           +----------+
```

---

## 7. QoS sur les technologies WAN  

### 7.1 MPLS – Mapping DSCP ↔ EXP  

| DSCP | EXP | QoS Profile (Cisco) | Usage |
|------|-----|----------------------|-------|
| EF   | 5   | `exp-5`              | VoIP, video |
| AF41 | 4   | `exp-4`              | Vidéo HD |
| AF31 | 3   | `exp-3`              | Data prioritaire |
| AF21 | 2   | `exp-2`              | Signaling |
| CS0  | 0   | `exp-0`              | Best‑effort |

```text
policy-map MPLS-MAP
  class VOIP-CLASS
    set mpls experimental topmost 5
  class VIDEO-CLASS
    set mpls experimental topmost 4
```

### 7.2 Metro‑Ethernet – 802.1p + Q‑in‑Q  

- **Tag 1 (S‑Tag)** : VLAN du client (802.1ad).  
- **Tag 2 (C‑Tag)** : VLAN du provider.  
- **Mapping** : `cos 5 → dscp ef`, `cos 3 → dscp af31`.  

```text
interface GigabitEthernet0/1
  service-instance 10 ethernet
    encapsulation dot1q 100 second-dot1q 200
    rewrite ingress tag pop 1 symmetric
    rewrite egress tag push dot1q 100
    bridge-domain 10
    qos trust cos
```

### 7.3 LTE – QoS Class Identifier (QCI)  

| QCI | DSCP | Priorité | Description |
|-----|------|----------|-------------|
| 1   | EF   | 5        | Conversational voice |
| 2   | AF41 | 4        | Video streaming |
| 3   | AF31 | 3        | Interactive data |
| 4   | CS2  | 2        | Signaling |
| 9   | CS0  | 0        | Best‑effort |

---

## 8. QoS sur les Data‑centers  

| Technologie | Métrique clé | Standard | Implémentation |
|-------------|--------------|----------|----------------|
| **FCoE / DCB** | Priority Flow Control (PFC) | IEEE 802.1Qbb | `pfc enable` sur les switches |
| **RoCE v2** | Congestion Notification (ECN) | IEEE 802.1Qau | `ecn enable` |
| **VXLAN** | VNI → DSCP mapping | RFC 7348 | `vxlan udp-port 4789` + `set dscp` |
| **NVGRE** | GRE key → COS | Microsoft | `gre tunnel` + `cos` |

### 8.1 Exemple DCB sur Nexus 9000  

```text
feature dcb
interface Ethernet1/1
  spanning-tree port type network
  priority-flow-control mode priority-based
  priority-flow-control trust dscp
  priority-flow-control priority 3 0 0 0 0 0 0 0
```

- **PFC**