# Qualité de Service (QoS) - Expert

**Niveau :** Expert

**Prérequis :** QoS Intermédiaire (`qos-intermediaire.md`), solide maîtrise des protocoles WAN (MPLS, IPsec), de l'architecture d'interconnexion Data Center, de la théorie du contrôle de congestion TCP et de la ligne de commande CLI avancée (Cisco IOS-XE, NX-OS, Junos).

Ce cours aborde la Qualité de Service sous l'angle de l'ingénierie système et réseau avancée. Il traite des architectures QoS dans les réseaux d'opérateurs (**MPLS Exp/Traffic Engineering**), des mécanismes matériels de buffering ASIC dans les commutateurs Data Center (**RoCEv2, ECN, PFC**), des algorithmes mathématiques du Token Bucket, ainsi que de l'implémentation de la QoS dynamique dans les architectures **SD-WAN**.

---

## 1. Modélisation Mathématique des Algorithmes de Régulation (Token Bucket)

La régulation du débit (*Policing* et *Shaping*) s'appuie sur le modèle algorithmique du **Jeton de Seau** (*Token Bucket*).

```
                 MÉCANISME DU TOKEN BUCKET (SINGLE RATE 2-COLOR)

       Arrivée de jetons au débit CIR
                 │
                 ▼
       ┌───────────────────┐
       │     RESERVOIR     │
       │   (Capacité Bc)   │
       └─────────┬─────────┘
                 │
                 ▼
     [ Paquet de taille B octets ]
                 │
        ┌────────┴────────┐
        │ Jetons $\ge$ B ? │
        └───┬─────────┬───┘
         OUI│         │NON
            ▼         ▼
     [ Conforme ]   [ Non-Conforme ]
     (Jetons -= B)   (Drop / Remarque)
```

### Le Single Rate Three-Color Marker (srTCM - RFC 2697)

Le **srTCM** évalue le trafic selon trois couleurs (Vert, Jaune, Rouge) en utilisant un seul débit **CIR** (*Committed Information Rate*) et deux capacités de jetons : **Bc** (*Committed Burst Size*) et **Be** (*Excess Burst Size*).

#### Algorithme de calcul des jetons :

À chaque arrivée de paquet de taille $B$ octets au temps $t$ :

1. Les jetons sont ajoutés aux réservoirs $C$ (capacité $Bc$) et $E$ (capacité $Be$) selon le temps écoulé $\Delta t$ :
   $$T_C(t) = \min(Bc, T_C(t_{prev}) + CIR \times \Delta t)$$
   $$T_E(t) = \min(Be, T_E(t_{prev}) + (CIR \times \Delta t - (Bc - T_C(t_{prev}))))$$

2. **Évaluation de la conformité :**
   * **Vert (Conform) :** Si $T_C(t) \ge B \implies$ Le paquet passe, $T_C = T_C - B$.
   * **Jaune (Exceed) :** Si $T_C(t) < B$ et $T_E(t) \ge B \implies$ Le paquet passe mais est remarqué (ex: AFx1 $\to$ AFx3), $T_E = T_E - B$.
   * **Rouge (Violate) :** Si $T_E(t) < B \implies$ Le paquet est supprimé (*Drop*).

---

## 2. QoS dans les Réseaux Opérateurs et MPLS

Dans un réseau MPLS, les en-têtes IP d'origine sont masqués par un ou plusieurs labels MPLS. Le champ **DSCP** (6 bits) n'est plus directement accessible aux routeurs du cœur du réseau (*P Routers*).

```
                    EN-TÊTE DU LABEL MPLS (32 Bits)

   ┌───────────────────────────────────┬───────────┬───┬───────────┐
   │          LABEL (20 bits)          │ TC (3 bits│ S │ TTL (8b)  │
   └───────────────────────────────────┴─────┬─────┴───┴───────────┘
                                             │
                                  Anciennement nommé EXP
                                (Traffic Class / 8 bits CoS)
```

### Modèles d'Alignement QoS IP $\leftrightarrow$ MPLS

```
              COMPARAISON DES MODÈLES MPLS QOS

 1. UNIFORM MODEL (Modifications propagées bout-en-bout)
    [ IP DSCP ] ──(Copy)──> [ MPLS TC ] ──(DiffServ)──> [ IP DSCP Modifié ]

 2. PIPE MODEL (Préservation du marquage client)
    [ IP DSCP Client ] ────> [ MPLS TC Opérateur ] ────> [ IP DSCP Client Intact ]
                                (Utilisé dans le cœur)

 3. SHORT-PIPE MODEL (Traitement local en sortie de réseau)
    [ IP DSCP Client ] ────> [ MPLS TC Opérateur ] ────> [ Traitement d'Egress basé sur IP DSCP ]
```

* **Uniform Model :** Utilisé lorsque le client et l'opérateur partagent le même domaine de confiance QoS. Si un routeur P remarque la valeur TC (ex: réjection WRED), la modification est copiée dans l'en-tête IP à la sortie du tunnel.
* **Pipe Model :** L'opérateur applique sa propre politique QoS au niveau MPLS TC sans toucher au champ DSCP IP d'origine du client. Le traitement Egress du routeur PE de sortie est basé sur le label MPLS TC.
* **Short-Pipe Model :** Similaire au Pipe Model, à la différence que le traitement Egress sur le routeur PE de destination s'effectue en fonction du champ DSCP IP d'origine du client et non du champ MPLS TC.

---

## 3. QoS Data Center : Ultra-faible Latence et Lossless Ethernet

Dans les Data Centers modernes supportant le stockage distribué (NVMe-oF) ou le calcul IA/HPC via **RoCEv2** (RDMA over Converged Ethernet), la perte de paquets est inacceptable.

```
                  ARCHITECTURE LOSSLESS ETHERNET (RoCEv2)

  ┌──────────────────────────────────────────────────────────────────┐
  │ 1. PFC (Priority-Based Flow Control - IEEE 802.1Qbb)             │
  │    Pause par classe de CoS au lieu de pauser tout le lien L2.    │
  ├──────────────────────────────────────────────────────────────────┤
  │ 2. ECN (Explicit Congestion Notification - RFC 3168)              │
  │    Marquage CE (Congestion Encountered) dans l'en-tête IP.        │
  ├──────────────────────────────────────────────────────────────────┤
  │ 3. DCBX (Data Center Bridging Exchange)                          │
  │    Négociation LLDP des capacités QoS entre serveurs et switches.  │
  └──────────────────────────────────────────────────────────────────┘
```

### Mécanisme combiné PFC et ECN/DCQCN

```
 [ Emetteur RoCEv2 ] ───────────────────────────────────────────> [ Commutateur DC ]
         ▲                                                             │
         │                                               (Congestion détectée via WRED)
         │                                                             │
         │                                                             ▼
         │                                                 Marque le champ ECN = 11
         │                                                 (Congestion Encountered)
         │                                                             │
         │               [ Paquet CNP (Notification) ]                 │
         └─────────────────────────────────────────────────────────────┘
                         (Reçu du destinataire,
                          l'émetteur réduit son débit)
```

1. **PFC (IEEE 802.1Qbb) :** Fonctionne au niveau de la couche 2. Lorsque le buffer d'une file d'attente spécifique d'un switch franchit le xoff threshold, une trame **PFC PAUSE** est envoyée à l'équipement en amont uniquement pour la classe de priorité impactée, sans bloquer le reste du trafic.
2. **ECN (Explicit Congestion Notification) :** Utilisé conjointement avec WRED. Lorsque la file atteint le seuil minimum, au lieu de supprimer le paquet, le switch modifie les bits ECN dans l'en-tête IP ($11_2$). Le destinataire renvoie un paquet **CNP** (*Congestion Notification Packet*) pour que la source réduise le débit de transmission RoCEv2 de manière fluide.

---

## 4. QoS Dynamique dans les Architectures SD-WAN

Dans les réseaux WAN traditionnels, les politiques QoS sont statiques. En **SD-WAN**, la QoS devient dynamique et réactive aux conditions de transport en temps réel.

```
              QOS DYNAMIQUE ET OVERLAY / UNDERLAY SD-WAN

  [ Applications / VNF ]
          │
          ▼  (Classification Applicative DPI / NBAR2)
  ┌───────────────────────────────┐
  │  SD-WAN Edge Controller       │
  ├───────────────────────────────┤  Probes BFD (Latence, Gigue, Loss)
  │ Dynamic Path Selection (AAR)  │ <────────────────────────────────┐
  └──────────────┬────────────────┘                                  │
                 │                                                   │
        ┌────────┴────────┐                                          │
        ▼                 ▼                                          │
 ┌─────────────┐   ┌─────────────┐                                   │
 │ WAN1 (MPLS) │   │ WAN2 (INET) │ ──────────────────────────────────┘
 └─────────────┘   └─────────────┘
```

### Concepts Clés :

* **Per-Packet Site-to-Site Performance Monitoring :** Utilisation de sondes BFD (*Bidirectional Forwarding Detection*) injectées dans les tunnels IPsec pour mesurer la latence, la gigue et la perte de paquets toutes les millisecondes.
* **AAR (Application-Aware Routing) :** Basculement dynamique d'un flux applicatif (ex: Zoom, Microsoft 365) d'un lien à un autre sans rupture de session si un SLA QoS est franchi.
* **Adaptive Shaping / Rate Adaptation :** Ajustement dynamique de la valeur du *shaper* en sortie de l'équipement SD-WAN en cas de variation de la bande passante disponible sur un lien Internet grand public (ex: 4G/5G ou liaison Satellite Starlink).

---

## 5. Cas Pratique d'Ingénierie : Configuration Avancée Opérateur/Enterprise

Voici une configuration complète sur **Cisco IOS-XE (Router ASR 1000)** implémentant un marquage à deux débits/trois couleurs (srTCM), du shaping hiérarchique (HQoS) et l'activation d'ECN.

```
! =================================================================
! 1. CLASSIFICATION AVANCÉE VIA NBAR2 ET ACL
! =================================================================
class-map match-any CM_VOICE_CRITICAL
 match protocol rtp audio
 match ip dscp ef

class-map match-any CM_REALTIME_VIDEO
 match protocol zoom
 match protocol ms-teams

class-map match-all CM_BULK_DATA
 match protocol ftp
 match protocol bittorrent

! =================================================================
! 2. POLICER TWO-RATE THREE-COLOR (2R3C - RFC 2698)
! =================================================================
policy-map PM_INGRESS_POLICING
 class CM_BULK_DATA
  police cir 10000000 pir 20000000 conform-action transmit exceed-action set-dscp-transmit af13 violate-action drop

! =================================================================
! 3. POLITIQUE HIÉRARCHIQUE HQOS (CHILD & PARENT POLICY)
! =========================================================
! Politique Fille (Child Policy) : Allocation par classe
policy-map PM_CHILD_QUEUING
 class CM_VOICE_CRITICAL
  priority level 1
  police cir percent 10
  
 class CM_REALTIME_VIDEO
  priority level 2
  police cir percent 20
  
 class class-default
  bandwidth remaining percent 100
  random-detect dscp-based
  random-detect dscp 0 20 40 10    ! Minimum, Maximum, Drop-Probability
  random-detect ecn                ! Activation d'ECN (Explicit Congestion Notification)

! Politique Mère (Parent Policy) : Shaping global de la sous-interface WAN
policy-map PM_PARENT_HQOS
 class class-default
  shape average 100000000          ! Shaping global du lien physique à 100 Mbps
  service-policy PM_CHILD_QUEUING

! =================================================================
! 4. APPLICATION ET OPTIMISATION DE L'INTERFACE
! =================================================================
interface GigabitEthernet0/0/0.100
 encapsulation dot1Q 100
 ip address 192.168.100.1 255.255.255.252
 service-policy input PM_INGRESS_POLICING
 service-policy output PM_PARENT_HQOS
```

---

## Synthèse comparative des technologies QoS Expert

| Domaine | Problématique Clé | Technologie Majeure | Solution QoS associée |
| :--- | :--- | :--- | :--- |
| **MPLS WAN** | Masquage des en-têtes IP dans le backbone | MPLS Traffic Class (TC) | Pipe, Short-Pipe, Uniform Models |
| **Data Center / Storage** | Zero-Packet-Loss obligatoire pour NVMe/RoCE | IEEE 802.1Qbb / RFC 3168 | PFC (Priority Flow Control) + ECN/CNP |
| **Enterprise WAN** | Congestion sur liens asymétriques | HQoS (Hierarchical QoS) | Parent-Child Shaping + LLQ Multi-niveau |
| **SD-WAN** | Fluctuations des accès Internet publics | Application-Aware Routing | Sondes BFD dynamiques + Dynamic Shaping |

---

## Points à Retenir

1. **Token Bucket :** Le mécanisme mathématique sous-jacent au policing/shaping repose sur la gestion de réservoirs de jetons ($CIR, Bc, Be$).
2. **QoS MPLS :** Le choix entre les modèles *Uniform*, *Pipe*, et *Short-Pipe* détermine si le marquage QoS du client est préservé ou synchronisé avec le réseau d'infrastructures de l'opérateur.
3. **Lossless Ethernet (DC) :** RoCEv2 utilise **PFC** au niveau L2 pour bloquer les paquets sélectivement par classe et **ECN** au niveau L3/L4 pour avertir les émetteurs de réduire leur débit sans jeter de paquets.
4. **HQoS (Hierarchical QoS) :** Structure indispensable pour appliquer un lissage global (*Shaping*) tout en maintenant un ordonnancement fin (*Queuing/Priority*) à l'intérieur du canal lissé.
```

The **Expert** level module `qos-expert.md` completes the three-tier QoS learning path. Let me know if you would like to explore any of these topics further or create additional technical resources!