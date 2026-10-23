# Qualité de Service (QoS) - Intermédiaire

**Niveau :** Intermédiaire

**Prérequis :** QoS Débutant (`qos-debutant.md`), compréhension des en-têtes IP/Ethernet, notions de routage IP et manipulation de la ligne de commande réseau (CLI Cisco IOS/NX-OS).

Ce cours approfondit l'architecture **DiffServ (Differentiated Services)**. Il détaille les mécanismes internes du traitement des paquets, les algorithmes avancés d'ordonnancement (*scheduling*), l'évitement de la congestion (*RED/WRED*) et la mise en œuvre pratique de la QoS via le modèle **MQC (Modular QoS CLI)**.

---

## 1. L'Architecture DiffServ et le Concept de PHB

L'architecture **DiffServ** (RFC 2474 / RFC 2475) est le standard prédominant pour le déploiement de la QoS à grande échelle. Contrairement à IntServ (qui réserve des ressources bout en bout via RSVP), DiffServ est **stateless** au cœur du réseau : chaque équipement traite le paquet individuellement en fonction de sa marque.

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                           DOMAINE DIFFSERV                             │
 │                                                                        │
 │  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐       │
 │  │ Edge Router │ ──────> │ Core Router │ ──────> │ Edge Router │       │
 │  └──────┬──────┘         └──────┬───────┘         └─────────────┘       │
 └─────────┼───────────────────────┼──────────────────────────────────────┘
           │                       │
     CLASSIFICATION           TRAITEMENT
       & MARQUAGE              PHB UNUNIQUEMENT
     (Inspection lourde)     (Commutation rapide)
```

### Le traitement Per-Hop Behavior (PHB)

Le **PHB** définit le comportement d'un nœud réseau (commutateur ou routeur) lorsqu'il transmet un paquet marqué par un code DSCP donné. Il existe 4 grandes familles de PHB :

```
                  STRUCTURE ET CORRESPONDANCE DSCP / PHB
                  
   ┌───────────────────────┬───────────────┬──────────────────────────────┐
   │ Class / PHB           │ DSCP (Binary) │ Description / Usage          │
   ├───────────────────────┼───────────────┼──────────────────────────────┤
   │ Default (DF)          │ 000000 (0)    │ Best Effort (Pas de priorité)│
   │ Expedited Fwd (EF)    │ 101110 (46)   │ Faible latence/gigue (Voip)  │
   │ Class Selector (CS)   │ XXX000 (8-56) │ Rétrocompatibilité IP Preced.│
   │ Assured Fwd (AF)      │ aaadd0        │ 12 classes avec proba. de drop│
   └───────────────────────┴───────────────┴──────────────────────────────┘
```

#### Les classes Assured Forwarding (AF) en détail

Le modèle AF est structuré en **4 classes indépendantes** ($AF1x, AF2x, AF3x, AF4x$). Chaque classe contient **3 niveaux de probabilité de suppression** (Drop Preference) :

```
                        MATRICE DES CLASSES AF
                        
                   Classe 1     Classe 2     Classe 3     Classe 4
                 ┌────────────┬────────────┬────────────┬────────────┐
 Low Drop        │ AF11 (10)  │ AF21 (18)  │ AF31 (26)  │ AF41 (34)  │
 Medium Drop     │ AF12 (12)  │ AF22 (20)  │ AF32 (28)  │ AF42 (36)  │
 High Drop       │ AF13 (14)  │ AF23 (22)  │ AF33 (30)  │ AF43 (38)  │
                 └────────────┴────────────┴────────────┴────────────┘
                 
  Formule binaire AFxy :  aaa = Classe (x)   |   dd = Drop Preference (y)
```

> **Exemple :** Un paquet marqué **AF41** a la priorité absolue en termes de bande passante par rapport à AF11. Cependant, si la classe AF4 subit une congestion, un paquet **AF43** sera supprimé *avant* un paquet **AF41**.

---

## 2. Ordonnancement et Algorithmes de File d'Attente (Scheduling)

Lorsqu'une interface réseau est saturée, l'ordonnanceur (*scheduler*) décide dans quel ordre vider les files d'attente.

```
                  FONCTIONNEMENT DE LOW LATENCY QUEUING (LLQ)
                  
 [ Paquets En Entrée ]
          │
          ├────> [ File Strict Priority (PQ) ] ───────┐ (Servie TANT QU'ELLE N'EST PAS VIDE)
          │                                           │
          ├────> [ File Bande Passante 1 (CBWFQ) ] ───┼───> [ Scheduler ] ───> [ Interface ]
          │                                           │
          └────> [ File Best Effort (Default) ] ──────┘
```

### 1. FIFO (First In, First Out)
* **Mécanisme :** Aucun tri. Les paquets sortent dans leur ordre d'arrivée.
* **Inconvénient :** Un flux volumineux bloque tous les autres.

### 2. WFQ (Weighted Fair Queuing)
* **Mécanisme :** Répartit dynamiquement le débit entre les flux en attribuant un poids inversement proportionnel à la taille du paquet.

### 3. CBWFQ (Class-Based Weighted Fair Queuing)
* **Mécanisme :** Permet à l'administrateur de définir explicitement des classes de trafic et d'allouer une bande passante minimale garantie à chaque classe.
* **Inconvénient :** N'offre pas de garantie de latence minimale pour la voix.

### 4. LLQ (Low Latency Queuing)
* **Mécanisme :** Combine **CBWFQ** avec une file **Strict Priority (PQ)**.
* **Usage :** La file PQ est servie en priorité absolue (idéal pour la voix IP). Pour éviter qu'un bogue n'asphyxie les autres files, la file PQ est soumise à un **policer intégré** qui limite son débit maximal.

---

## 3. Évitement de la Congestion : RED et WRED

Plutôt que d'attendre que la file d'attente soit complètement pleine (ce qui entraîne le *Tail Drop*), les mécanismes d'évitement de la congestion suppriment proactivement des paquets **avant** la saturation.

### Le problème du Tail Drop et de la Synchronisation Globale TCP

```
                       PROBLÈME DU TAIL DROP (Sans WRED)
                       
 File d'attente pleine : [X][X][X][X][X][X][X]  <─── [ Paquets Entrants ]
                                                     (Tous jetés !)
```

1. La file se remplit. Tous les nouveaux paquets sont jetés (*Tail Drop*).
2. Toutes les sessions TCP traversant le lien perdent des paquets en même temps.
3. Toutes les sessions réduisent simultanément leur fenêtre de congestion (*TCP Slow Start*).
4. Le lien devient sous-utilisé, puis se re-remplit brutalement. C'est la **synchronisation globale TCP**.

```
  Débit Lien
     ▲
100% │     /\      /\      /\      (Oscillation permanente du débit)
     │    /  \    /  \    /  \
  0% └───/────\──/────\──/────\──────> Temps
```

### La Solution : WRED (Weighted Random Early Detection)

**WRED** supprime aléatoirement des paquets lorsque la file atteint un premier seuil (*Minimum Threshold*). Plus la file se remplit, plus la probabilité de suppression augmente.

```
                 COURBE DE PROBABILITÉ DE DROP EN WRED
                 
  Probabilité
    de Drop
     100% │                                      /│ (Tail Drop)
          │                                     / │
          │                                    /  │
          │                                   /   │
          │     (Proba max Drop) ───────────>┌    │
          │                                 /│    │
        0%└─────────────────────────────────┴─────┴──────────>
                                           Min   Max    Taille File
                                          Seuil Seuil   d'attente
```

* **Attribut "Weighted" :** WRED examine la valeur **DSCP / IP Precedence**. Un paquet marqué **AF13** commencera à être jeté à un seuil `Min` beaucoup plus bas qu'un paquet **AF11**.

---

## 4. Limitation du Trafic : Policing vs Shaping

| Caractéristique | Traffic Policing | Traffic Shaping |
| :--- | :--- | :--- |
| **Action sur excès** | **Jette (Drop)** ou Remarque le paquet. | **Retient en mémoire** (Buffer) puis lisse. |
| **Gestion mémoire** | Pas d'utilisation de mémoire tampon. | Utilise une file d'attente (Buffer). |
| **Impact Latence** | N'introduit aucune latence supplémentaire. | **Ajoute du délai/gigue** lié à la mise en mémoire. |
| **Direction** | Inbound (Entrée) et Outbound (Sortie). | **Outbound (Sortie uniquement)**. |
| **Usage Typique** | À l'entrée d'un réseau opérateur (ISP). | En sortie d'un sous-interface WAN (Interconnexion). |

```
                     POLICING vs SHAPING EN GRAPHIC
                     
   Trafic Entrant Brut                Policing (Tranché)              Shaping (Lissé)
      ▲                                  ▲                               ▲
      │   ┌─┐    ┌─┐                     │   ┌─┐    ┌─┐                  │   ┌────────┐
      │  ┌┘ └┐  ┌┘ └┐                    │───┼─┼────┼─┼─── (Limite)      │───┼────────┼─── (Limite)
      │ ┌┘   └┐┌┘   └┐                   │ ┌─┘ └─┐┌─┘ └─┐                │ ┌─┘        └─┐
      └─┴─────┴┴─────┴──>                └─┴─────┴┴─────┴──>             └─┴────────────┴──>
```

---

## 5. Mise en Œuvre Avancée en MQC (Modular QoS CLI)

Le framework **MQC** sépare la configuration en 3 étapes modulaires :
1. `class-map` : Identification du trafic.
2. `policy-map` : Application des actions (marquage, police, priorité, bande passante).
3. `service-policy` : Attachement de la politique à une interface réseau.

### Architecture d'une Configuration MQC Complète

```
                  STAGES DU MODÈLE MQC
                  
  ┌──────────────────┐
  │  1. CLASS-MAP    │ ──> Match Protocol, ACL, DSCP, CoS
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  2. POLICY-MAP   │ ──> Set DSCP, Priority (LLQ), Bandwidth, Shape, WRED
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │ 3. SERVICE-POLICY│ ──> Apply Input / Output sur Interface
  └──────────────────┘
```

### Exemple Complet : Configuration WAN d'un Siège Distant

Dans cet exemple, nous allons :
* Classer la Voix (SIP/RTP), la Vidéo et le Trafic Métier (ERP/SQL).
* Marquer les paquets en conséquence avec DSCP.
* Configurer une file prioritaire (LLQ) pour la voix, de la bande passante garantie pour le reste, et du WRED sur le trafic web standard.

```
! =========================================================
! ÉTAPE 1 : CLASSIFICATION VIA CLASS-MAP
! =========================================================
ip access-list extended ACL_VOICE_RTP
 permit udp any any range 16384 32767

ip access-list extended ACL_BUSINESS_DATA
 permit tcp any any eq 443
 permit tcp any any eq 1433

class-map match-any CM_VOICE
 match access-group name ACL_VOICE_RTP
 match protocol sip

class-map match-any CM_BUSINESS
 match access-group name ACL_BUSINESS_DATA

! =========================================================
! ÉTAPE 2 : POLITIQUE DE MARQUAGE (MARKING POLICY)
! =========================================================
policy-map PM_MARKING_INGRESS
 class CM_VOICE
  set dscp ef
 class CM_BUSINESS
  set dscp af31
 class class-default
  set dscp default

! =========================================================
! ÉTAPE 3 : POLITIQUE DE QUEUING ET SHAPING (EGRESS WAN)
! =========================================================
policy-map PM_HQ_WAN_OUT
 class CM_VOICE
  priority percent 15          ! LLQ : 15% de bande passante garantie en Strict Priority
  
 class CM_BUSINESS
  bandwidth percent 40         ! CBWFQ : 40% de bande passante minimale garantie
  queue-limit 64 packets
  
 class class-default
  bandwidth percent 35         ! 35% pour le reste du trafic
  random-detect dscp-based     ! Activation de WRED basé sur DSCP

! =========================================================
! ÉTAPE 4 : APPLICATION SUR LES INTERFACES
! =========================================================
interface GigabitEthernet0/0/0
 description ** INTERFACE LAN (MARQUAGE EN ENTRÉE) **
 service-policy input PM_MARKING_INGRESS

interface GigabitEthernet0/0/1
 description ** INTERFACE WAN 100Mbps (TRAITEMENT EN SORTIE) **
 max-reserved-bandwidth 100
 service-policy output PM_HQ_WAN_OUT
```

---

## 6. Vérification et Diagnostic QoS en Ligne de Commande

Afin de vérifier le bon fonctionnement des politiques QoS et la détection d'éventuels paquets rejetés (*drops*), utilisez les commandes suivantes sur Cisco IOS :

### Commandes Clés de Dépannage

```bash
# Vérifier l'application des politiques et les statistiques de drop en temps réel
show policy-map interface GigabitEthernet0/0/1

# Analyser les files d'attente matérielles/logicielles et le comportement WRED
show interface GigabitEthernet0/0/1 queuing

# Vérifier la correspondance des Class-Maps
show class-map
```

### Exemple de sortie de la commande `show policy-map interface` :

```text
 GigabitEthernet0/0/1 

  Service-policy output: PM_HQ_WAN_OUT

    Class-map: CM_VOICE (match-any)
      12453 packets, 1494360 bytes
      5 minute offered rate 32000 bps, drop rate 0000 bps
      Match: access-group name ACL_VOICE_RTP
      Priority: 15% (15000 kbps), burst bytes 3750, Over-limit drops: 0

    Class-map: CM_BUSINESS (match-any)
      45210 packets, 54252000 bytes
      5 minute offered rate 450000 bps, drop rate 0000 bps
      Queueing
      Output Queue: Queue size 4 hazard 0
      Bandwidth 40% (40000 kbps)

    Class-map: class-default (match-default)
      89201 packets, 114177280 bytes
      5 minute offered rate 820000 bps, drop rate 12000 bps
      BW: 35% (35000 kbps)
      WRED: drop probability 10
        dscp default: min 20 max 40 mark 10, drops 142
```

---

## Commandes et Synthèse des Valeurs Clés

| Paramètre / Valeur | Description | Usage Recommandé |
| :--- | :--- | :--- |
| **DSCP 46 (EF)** | Expedited Forwarding | Voix sur IP (Flux Média RTP). |
| **DSCP 24/34/44 (CS3/AF41)** | Assured Forwarding / Class Selector | Signalisation Voix (SIP) et Visioconférence. |
| **DSCP 0 (BE / DF)** | Best Effort | Web, Téléchargements, Courriels. |
| **Priority (LLQ)** | File à priorité stricte. | Max 33% de la bande passante globale pour éviter la starvation. |
| **Random-detect** | Active l'algorithme WRED. | Recommandé uniquement sur les files gérant du trafic TCP. |

---

## Points à Retenir

1. **Architecture DiffServ :** Elle repose sur le marquage en bordure (*Edge*) et le traitement unifié *Per-Hop Behavior* (PHB) au cœur du réseau.
2. **Matrice AF (Assured Forwarding) :** Elle combine 4 classes de débit et 3 niveaux de probabilité de rejet. Plus le deuxième chiffre d'une valeur AF est élevé, plus le paquet a de chances d'être supprimé en cas de congestion.
3. **LLQ (Low Latency Queuing) :** C'est la solution incontournable pour la Voix IP. Elle associe une file Strict Priority (PQ) bordée par un policer à un ordonnancement CBWFQ.
4. **WRED :** Il prévient la synchronisation globale TCP en supprimant des paquets de manière aléatoire et progressive avant que les files ne soient complètement saturées.
5. **Shaping vs Policing :** Le *shaping* lisse le trafic en utilisant de la mémoire tampon (en sortie), tandis que le *policing* coupe ou remarque immédiatement le trafic excédentaire (en entrée ou en sortie).