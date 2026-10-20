# Cours Intensif – QoS Avancée (LLQ, CBWFQ, Shaping)  
**Niveau : Administrateur Réseau Senior (CCIE)**  
**Durée estimée : 2 jours (≈ 16 h)**  

---  

## 1. Objectifs du cours  

| Objectif | Détails |
|----------|---------|
| Comprendre les concepts de base et avancés du QoS | Modèles de trafic, classification, marquage, policage, shaping, queuing |
| Maîtriser **LLQ** (Low‑Latency Queuing) | Priorisation stricte, interaction avec CBWFQ, configuration sur IOS, IOS‑XR, NX‑OS |
| Maîtriser **CBWFQ** (Class‑Based Weighted Fair Queuing) | Allocation de bande passante, hiérarchie, intégration avec LLQ |
| Implémenter le **shaping** à différents niveaux | Interface, policer, hierarchical shaping, QoS sur Linux (tc) |
| Concevoir une architecture QoS end‑to‑end | End‑to‑end, QoS‑aware routing, DiffServ, MPLS‑TE |
| Dépanner des problèmes courants | Analyse de perte, jitter, burst, overflow, verification avec show/debug |

---

## 2. Rappels fondamentaux  

### 2.1 Modèle DiffServ (DS)  

```
+-------------------+   +-------------------+   +-------------------+
|   Classification  | → |   Marking (DSCP)  | → |   Policing/Queue  |
+-------------------+   +-------------------+   +-------------------+
```

* **DSCP** (6 bits) – définit la classe de service (EF, AFxx, BE).  
* **PHB** (Per‑Hop Behaviour) – comportement appliqué à chaque saut (EF → Low‑Latency, AF → Assured Forwarding, BE → Best‑Effort).  

### 2.2 Pipeline QoS typique sur Cisco  

```
+-------------------+   +-------------------+   +-------------------+   +-------------------+
| 1. Classification | → | 2. Policing (if) | → | 3. Marking (DSCP) | → | 4. Queuing (LLQ/CBWFQ) |
+-------------------+   +-------------------+   +-------------------+   +-------------------+
```

* La **police** (rate‑limit) agit avant le marquage, afin d’éviter l’injection de trafic non‑conforme.  
* La **queue** est le point de décision final où le trafic attend d’être transmis.

---

## 3. LLQ – Low‑Latency Queuing  

### 3.1 Principes  

* LLQ est une **extension de CBWFQ** qui réserve une file strict‑priority (strict‑priority queue – SP) pour le trafic **EF** (Expedited Forwarding).  
* La file SP **déborde** les files CBWFQ : tant qu’il y a du trafic EF, il est servi avant tout le reste.  
* **Shaping** du trafic EF peut être appliqué via un **policy‑map** avec `priority` (ou `priority percent`).  

### 3.2 Architecture interne  

```
+--------------------------+
|  Class‑Based WFQ (CBWFQ) |
|  +--------------------+  |
|  |  Class‑Map A (AF41) |  |
|  +--------------------+  |
|  |  Class‑Map B (BE)   |  |
|  +--------------------+  |
|  |  ...                |  |
+--------------------------+
          ^
          |
          |  (Strict‑Priority)
          |
+--------------------------+
|  Priority Queue (LLQ)    |
|  (EF – VoIP, Video)      |
+--------------------------+
```

### 3.3 Configuration IOS – Exemple complet  

> **Contexte** : Routeur d’accès (Gig0/0/0) qui doit garantir 30 Mbps de bande passante pour la voix (EF) et partager les 70 Mbps restants entre plusieurs classes AF/BE.  

```
! 1. Définir les class‑maps
class-map match-any VOICE
  match dscp ef
class-map match-any VIDEO
  match dscp af41
class-map match-any CRITICAL
  match access-group name CRIT_ACL
class-map match-any BEST_EFFORT
  match any

! 2. Créer la policy‑map
policy-map QOS_OUT
  class VOICE
    priority percent 30          ! 30 % du port (≈ 30 Mbps si port 100 Mbps)
    police 30 mbps 2000 0 exceed-action drop
  class VIDEO
    bandwidth percent 25         ! 25 % du port
    queue-limit 2000
  class CRITICAL
    bandwidth percent 20
    queue-limit 1500
  class BEST_EFFORT
    bandwidth percent 25
    queue-limit 1000

! 3. Appliquer sur l’interface
interface GigabitEthernet0/0/0
  service-policy output QOS_OUT
```

### 3.4 Options avancées  

| Option | Description | Exemple |
|--------|-------------|---------|
| `priority percent <x>` | Réserve **x %** du débit total en SP (auto‑shaping). | `priority percent 20` |
| `priority <kbps>` | Réserve une bande passante fixe en kbps. | `priority 5000` |
| `police <cbs> <burst>` | Limite le trafic EF en cas de dépassement. | `police 30 mbps 2000 0 exceed-action drop` |
| `queue-limit <size>` | Taille de la file d’attente (en paquets). | `queue-limit 3000` |
| `bandwidth percent <x>` | Allocation de bande passante relative pour les classes non‑SP. | `bandwidth percent 15` |

### 3.5 Interaction avec la **QoS‑aware routing**  

* **DSCP‑preserving** : les routes doivent conserver le DSCP (ex. `ip qos dscp preserve`).  
* **MPLS‑TE** : les LSPs peuvent être configurés avec `bandwidth` et `priority` pour garantir la bande passante des classes EF.

---

## 4. CBWFQ – Class‑Based Weighted Fair Queuing  

### 4.1 Concept  

* **CBWFQ** partage la bande passante du lien entre plusieurs classes selon des **poids** (bandwidth) ou **pourcentages**.  
* Chaque classe possède sa propre **queue** (WFQ) ; les paquets sont servis en fonction du poids et du **queue‑limit**.  

### 4.2 Types de poids  

| Type | Syntax | Usage typique |
|------|--------|---------------|
| `bandwidth <kbps>` | `bandwidth 2000` | Réservation fixe (ex. 2 Mbps) |
| `bandwidth percent <x>` | `bandwidth percent 20` | Allocation relative (ex. 20 % du lien) |
| `bandwidth remaining percent <x>` | `bandwidth remaining percent 30` | Utilise la bande passante **non‑réservée** par les classes précédentes |
| `queue-limit <packets>` | `queue-limit 1000` | Contrôle de la profondeur de la file |

### 4.3 Hiérarchie CBWFQ (H‑CBWFQ)  

* Permet d’imbriquer plusieurs **policy‑maps** (parent‑child) afin de créer des **levels** de shaping/queuing.  
* Exemple : **parent** shape le trafic à 100 Mbps, **child** distribue les classes à l’intérieur.  

```
policy-map PARENT
  class class-default
    shape average 100000000
    service-policy child1

policy-map child1
  class VOICE
    priority percent 30
  class VIDEO
    bandwidth percent 25
  class DATA
    bandwidth percent 45
```

### 4.4 Configuration IOS – Exemple complet  

> **Contexte** : Lien WAN 250 Mbps, besoin de 40 Mbps pour la voix, 60 Mbps pour le trafic vidéo, le reste pour les data.  

```
! 1. Class‑maps
class-map match-any VOICE
  match dscp ef
class-map match-any VIDEO
  match dscp af41
class-map match-any DATA
  match dscp default   ! BE

! 2. Policy‑map parent (shaping)
policy-map WAN_SHAPE
  class class-default
    shape average 250000000
    service-policy WAN_QOS

! 3. Policy‑map enfant (CBWFQ+LLQ)
policy-map WAN_QOS
  class VOICE
    priority percent 16    ! 16 % de 250 Mbps ≈ 40 Mbps
  class VIDEO
    bandwidth percent 24   ! 24 % ≈ 60 Mbps
    queue-limit 3000
  class DATA
    bandwidth remaining percent 60
    queue-limit 5000

! 4. Application
interface Serial0/0/0
  service-policy output WAN_SHAPE
```

### 4.5 Points de vigilance  

| Problème | Symptom | Cause fréquente | Remédiation |
|----------|---------|-----------------|-------------|
| **Overflow** | Drops en `show interface` > `output drops` | `queue-limit` trop bas ou `bandwidth` sous‑dimensionné | Augmenter `queue-limit` ou ré‑allouer bande |
| **Under‑utilisation** | Faible utilisation du lien, trafic EF non‑servi | `priority percent` trop élevé, pas assez de trafic réel | Ajuster le pourcentage ou passer à `priority <kbps>` |
| **Starvation** | Classe BE ne voit jamais de débit | `bandwidth remaining` mal calculé, classes précédentes consomment tout | Re‑ordonner les classes ou réduire leurs poids |

---

## 5. Shaping – Contrôle du débit sortant  

### 5.1 Définitions  

| Terme | Description |
|-------|-------------|
| **Shaping** | Limite le **débit moyen** d’une classe en retardant les paquets (buffer). |
| **Policing** | Limite le débit **instantané** en droppant les paquets qui dépassent le seuil. |
| **Burst** (CBS – Committed Burst Size) | Taille maximale du burst autorisé avant que le policing/shaping n’intervienne. |

### 5.2 Shaping sur Cisco  

* **`shape average <kbps>`** – applique le shaping à la classe courante.  
* **`shape peak-rate <kbps>`** – option pour un pic autorisé (rare).  

#### Exemple – Shaping d’un trafic d’application  

```
class-map match-any APP
  match access-group name APP_ACL

policy-map SHAPE_APP
  class APP
    shape average 5000        ! 5 Mbps
    police 5 mbps 1000 0 exceed-action drop
    set dscp af31

interface GigabitEthernet1/0/1
  service-policy output SHAPE_APP
```

### 5.3 Hierarchical Shaping (H‑Shaping)  

* Permet de **shaper** à plusieurs niveaux (interface → child policy).  
* Utilisé pour **traffic‑engineered MPLS** ou **QoS‑aware WAN**.  

```
policy-map PARENT_SHAPE
  class class-default
    shape average 100000000
    service-policy CHILD_SHAPE

policy-map CHILD_SHAPE
  class VOIP
    priority percent 20
  class VIDEO
    bandwidth percent 30
    shape average 30000000
  class DATA
    bandwidth remaining percent 50
```

### 5.4 Shaping sous Linux – `tc`  

| Commande | Fonction |
|----------|----------|
| `tc qdisc add dev eth0 root handle 1: htb default 30` | Crée la hiérarchie HTB (Hierarchical Token Bucket). |
| `tc class add dev eth0 parent 1: classid 1:10 htb rate 30mbit ceil 30mbit` | Classe VOIP – débit strict. |
| `tc class add dev eth0 parent 1: classid 1:20 htb rate 70mbit ceil 100mbit` | Classe DATA – débit partagé. |
| `tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dscp 0xb8 0xfc flowid 1:10` | Filtre DSCP EF (0xb8) vers la classe VOIP. |

#### Exemple complet (script)  

```
#!/bin/bash
# Reset
tc qdisc del dev eth0 root 2>/dev/null

# Root HTB
tc qdisc add dev eth0 root handle 1: htb default 30

# Classe VOIP – 30 Mbps strict (LLQ‑like)
tc class add dev eth0 parent 1: classid 1:10 htb rate 30mbit ceil 30mbit prio 0

# Classe VIDEO – 40 Mbps WFQ
tc class add dev eth0 parent 1: classid 1:20 htb rate 40mbit ceil 50mbit prio 1

# Classe DATA – le reste
tc class add dev eth0 parent 1: classid 1:30 htb rate 30mbit ceil 70mbit prio 2

# Filtrage DSCP
tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dscp 0xb8 0xfc flowid 1:10   # EF
tc filter add dev eth0 protocol ip parent 1:0 prio 2 u32 match ip dscp 0xa8 0xfc flowid 1:20   # AF41
```

### 5.5 Points de comparaison – Cisco vs Linux  

| Aspect | Cisco IOS | Linux `tc` |
|--------|-----------|------------|
| **Modèle** | CBWFQ/LLQ + HTB (shaping) | HTB (hierarchical token bucket) |
| **Granularité** | DSCP, ACL, VLAN, MPLS | DSCP, IP, MAC, TOS, fw‑mark |
| **Policing intégré** | `police` (burst, exceed‑action) | `police` (rate, burst, drop) |
| **Gestion dynamique** | `auto qos` (wizard) | `tc` scripts + `iproute2` |
| **Statistiques** | `show policy-map interface`, `show queueing` | `tc -s qdisc show dev eth0` |

---

## 6. Conception d’une architecture QoS end‑to‑end  

### 6.1 Principes de design  

1. **Définir les exigences métier** – latence < 30 ms pour VoIP, jitter < 5 ms, perte < 0,1 % pour vidéo.  
2. **Cartographier le trafic** – identifier les flux (EF, AF, BE) à chaque point du réseau.  
3. **Déterminer les points de police & shaping** – police en entrée (ingress) pour protéger le réseau, shaping en sortie (egress) pour garantir la bande passante.  
4. **Uniformiser le marquage** – DSCP doit être conservé sur tout le chemin (`ip qos dscp preserve`).  
5. **Planifier la hiérarchie** – parent‑child policy‑maps, utilisation de **QoS‑aware routing** (OSPF/IS‑IS avec `ip ospf qos` ou `mpls traffic-eng`).  

### 6.2 Diagramme ASCII – Architecture typique  

```
+----------------------+      +----------------------+      +----------------------+
|  Edge Router (PE)    |      |  Core Switch (MPLS)  |      |  Edge Router (CE)    |
|  (Ingress policing) | ---> |  (LLQ/CBWFQ)          | ---> |  (Egress shaping)    |
+----------------------+      +----------------------+      +----------------------+

   |                                    |
   |  DSCP preserved (EF, AFxx, BE)    |
   v                                    v
+----------------------+      +----------------------+
|  Access Switch (PoE) |      |  Data‑Center Switch  |
|  LLQ for VoIP       |      |  CBWFQ for Apps      |
+----------------------+      +----------------------+
```

### 6.3 Exemple d’une chaîne complète (VoIP)  

| Hop | Action | Commande (exemple) |
|-----|--------|--------------------|
| **PE‑Ingress** | Police 50 Mbps, marquage EF | `policy-map IN_POLICE` → `class VOICE` → `police 50 mbps 1000 0 exceed-action drop` |
| **Core** | LLQ strict‑priority | `policy-map CORE_QOS` → `class VOICE` → `priority percent 30` |
| **CE‑Egress** | Shaping 30 Mbps (LLQ) | `policy-map OUT_SHAPE` → `class VOICE` → `priority percent 30` |
| **All** | DSCP preservation |