## node_id: segment-routing-expert

title: Segment Routing (SR-MPLS et SRv6) - Expert

# Segment Routing (SR-MPLS et SRv6) - Expert

**Niveau :** Expert

**Prérequis :** Segment Routing Débutant (`segment-routing-debutant`), Segment Routing Intermédiaire (`segment-routing-intermediaire`)

Dans les modules précédents, nous avons analysé les fondations du *Source Routing* (SR-MPLS/SRv6), les extensions IGP (IS-IS/OSPF), la mécanique du TI-LFA (Espaces P et Q), ainsi que l'ingénierie de trafic par **SR Policy** et **Color Extended Community**.

Au niveau **Expert**, l'objectif est d'aborder les architectures d'opérateurs à très grande échelle (*Hyperscale / Multi-Domain Carriers*). Ce cours traite du calcul de chemin centralisé via **PCE/PCEP (Path Computation Element Protocol)**, de la programmation réseau **SRv6 Network Programming** (Locators, Functions, Arguments), de la technologie de compression d'en-tête **uSID (Micro-Segment)**, de la segmentation de la topologie via **Flex-Algo (Flexible Algorithm)**, de l'automatisation programmatique par gNMI/Telemetry, ainsi que des techniques de diagnostic système à bas niveau.

## 1. Architecture SR-TE Inter-Domaine & PCE / PCEP (Path Computation Element)

Dans une infrastructure multi-domaines (multi-AS ou multi-aires IGP), aucun routeur Ingress n'a une visibilité complète sur la topologie globale du réseau. Le calcul de politiques SR-TE nécessitant une garantie de bout en bout (latence minimale, disjonction stricte de chemin physique) fait alors appel à un **PCE (Path Computation Element)** centralisé.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      PCE CENTRALISÉ / CONTRÔLEUR SDN                   │
│                        (Cisco Crosswork / OpenDaylight)                │
└───────────────▲────────────────────────────────────────▲───────────────┘
                │ BGP-LS (Topology / TE)                 │ PCEP (RFC 5440)
                │                                        │ (Path Report & Instantiation)
┌───────────────┴─────────────────┐    ┌─────────────────┴───────────────┐
│          DOMAINE IGP 1          │    │          DOMAINE IGP 2          │
│                                 │    │                                 │
│  [ Headend PE1 ] ──── [ ABR1 ] ─┼────┼─ [ ABR2 ] ──── [ Egress PE2 ]   │
│   (Ingress Node)                │    │                                 │
└─────────────────────────────────┘    └─────────────────────────────────┘

```

### 1. Protocole BGP-LS (BGP Link-State)

Pour que le PCE centralisé dispose d'une carte topologique temps réel du réseau, tous les routeurs ABR/ASBR exportent leur base de données IGP (IS-IS ou OSPF) vers le PCE au moyen de l'Address Family **BGP Link-State (BGP-LS)** :

* **NLRI BGP-LS** : Transporte les nœuds (Node Attribute), les liaisons (Link Attribute), la métrique de latence unidirectionnelle (SR Delay Measurement) et les SIDs associés (Prefix-SID, Adj-SID, Flex-Algo SID).

### 2. Protocole PCEP (Path Computation Element Communication Protocol)

Le routeur source (*Path Computation Client* - PCC) communique avec le PCE centralisé en PCEP (TCP port 4189) :

* **PCC-Initiated** : Le PCC demande au PCE de calculer une trajectoire sous contraintes.

* **PCE-Initiated (Stateful PCE)** : Le PCE instancie dynamiquement une SR Policy directement sur le routeur Headend sans intervention manuelle (Message `PCRpt` / `PCUpd`).

## 2. SRv6 Network Programming & Micro-Segments (uSID)

Le **SRv6 (Segment Routing over IPv6)** remplace l'encapsulation MPLS par des adresses IPv6 natives de 128 bits. Chaque instruction SRv6 est codée dans une adresse IPv6 appelée **SRv6 SID**.

### 1. Structure d'un SRv6 SID (128 bits)

Un SRv6 SID n'est pas une simple adresse IP destination : c'est un exécutable sous forme d'adresse IP découpé en trois parties :

```
 0                                 48               80               128
+---------------------------------+----------------+----------------+
|          LOCATOR (48 bits)      | FUNCTION (32b) | ARGUMENT (48b) |
+---------------------------------+----------------+----------------+
 \───────────────────────────────/ \──────────────/ \──────────────/
   Routable sur le réseau IPv6       Action exécutée   Paramètres
   (Acheminement IGP/BGP)            sur le nœud       supplémentaires

```

* **Locator** : Partie routable du SID. Utilisée par les routeurs de transit pour acheminer le paquet vers le nœud cible via le routage IPv6 le plus court (IPv6 Prefix).

* **Function** : Code d'instruction (*Opcode*) exécuté par le processeur/ASIC du routeur récepteur (ex: décapsuler, rediriger vers une VRF, appliquer une fonction réseau VNF).

* **Argument** : Paramètres optionnels d'exécution (ex: Flow Label, métadonnées de service).

### 2. Fonctions SRv6 fondamentales (SRv6 Behaviors - RFC 8986)

| Fonction SRv6 | Nom Complet | Description / Action du plan de données |
| :--- | :--- | :--- |
| **End** | Endpoint | Instruction de base. Avance le pointeur `Segments Left` dans l'en-tête SRH et réachemine le paquet. |
| **End.X** | Endpoint with Layer-3 Cross-Connect | Équivalent à un Adj-SID. Transfère le paquet directement sur une interface de sortie spécifique. |
| **End.DT4 / End.DT6** | Endpoint with Decapsulation and IPv4/IPv6 Table Lookup | Décapsule l'en-tête IPv6/SRH externe et recherche l'IP interne dans la table de routage d'une **VRF L3VPN**. |
| **End.DX4 / End.DX6** | Endpoint with Decapsulation and Cross-Connect | Décapsule et envoie directement le paquet IPv4/IPv6 sur une sous-interface/cross-connect spécifique. |
| **End.DT2U / End.DT2M** | Endpoint with Decapsulation and L2 Table Lookup | Décapsule et injecte la trame Ethernet dans une instance **EVPN (Bridge Domain)** pour le trafic Unicast/Multicast. |

### 3. SRv6 uSID (Micro-Segment - RFC 9256)

L'un des défis majeurs du SRv6 classique est la taille de l'en-tête IPv6 lorsque plusieurs SIDs de 128 bits sont empilés dans le **SRH (Segment Routing Header)**, générant un surcoût d'en-tête (*Overhead*) important.

La technologie **uSID (Micro-Segment)** résout ce problème en compactant plusieurs SIDs de 16 bits au sein d'une seule et même adresse IPv6 de 128 bits :

```
 0                  16         32         48         64                  128
+------------------+----------+----------+----------+-------------------+
|  uSID Block (16) | Node 1   | Node 2   | Node 3   |  End.X / Active   |
|   (ex: 2001:db8) |  (uN 1)  |  (uN 2)  |  (uN 3)  |   Shift Pointer   |
+------------------+----------+----------+----------+-------------------+
 \────────────────/ \──────────────────────────────/
   Prefix commun       3 SIDs de nœuds dans 1 seule 
   du domaine SRv6     adresse IPv6 de 128 bits !

```

Au fur et à mesure que le paquet traverse les nœuds `Node 1` $\rightarrow$ `Node 2` $\rightarrow$ `Node 3`, l'adresse IPv6 destination subit une rotation de décalage vers la gauche (*Shift Operation*), éliminant complètement le besoin d'un en-tête SRH pour les chemins courts !

## 3. Topologies Virtuelles : Flex-Algo (Flexible Algorithm)

Le **Flexible Algorithm (Flex-Algo)** permet de créer plusieurs sous-topologies de routage indépendantes (Slices) à l'intérieur d'un même domaine IGP (IS-IS ou OSPF), sans nécessiter le déploiement de contrôleur centralisé ni de tunnels SR-TE complexes.

```
                    ┌──────────────────────────────────────┐
                    │       TOPOLOGIE PHYSIQUE UNIQUE      │
                    └──────────────────┬───────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────────────┐
│        FLEX-ALGO 128 (LATENCY)        │ │        FLEX-ALGO 129 (MACSEC)        │
│ - Métrique = Delay Unidirectional     │ │ - Exclut les liens non-chiffrés     │
│ - Optimisé pour la Voix / 5G URLLC    │ │ - Dédié aux flux bancaires/critiques  │
└───────────────────────────────────────┘ └───────────────────────────────────────┘

```

### Structure de définition d'un Flex-Algo (FAD - Flex-Algo Definition)

Un **Flex-Algo** est identifié par une valeur numérique comprise entre `128` et `255`. Il est défini par un triplet :

1. **Calculation Type** : Algorithme de calcul (0 = SPF standard, 1 = Strict SPF).

2. **Metric Type** : Métrique utilisée pour le calcul du plus court chemin (0 = IGP metric, 1 = TE metric, 2 = Delay Unidirectional).

3. **Constraints** : Règles d'inclusion ou d'exclusion de liaisons basées sur les **Affinity Colors / SRLG** (ex: *Exclude Link Color RED*).

Chaque routeur se voient attribuer un **Flex-Algo Prefix-SID** spécifique pour chaque algorithme auquel il participe (ex: Node-SID standard = `16001`, Flex-Algo 128 SID = `16801`).

## 4. Configuration Avancée SRv6 & Flex-Algo (Cisco IOS-XR)

La configuration suivante sur **Cisco IOS-XR (ASR 9000 / NCS 5500)** illustre la mise en œuvre de **SRv6 uSID**, l'allocation de services L3VPN via `End.DT4`, ainsi que la définition d'un **Flex-Algo 128** basé sur la latence minimale.

```
! =====================================================================
! SECTION 1 : CONFIGURATION DU LOCATOR SRv6 ET uSID
! =====================================================================
segment-routing
 srv6
  encapsulation
   source-address 2001:db8:1::3
  !
  locators
   locator MAIN-uSID
    prefix 2001:db8:1:3::/64 micro-segment behavior unode pshift-0
   !
   locator LATENCY-uSID
    prefix 2001:db8:1:f128::/64 micro-segment behavior unode pshift-0
   !
  !
 !
!

! =====================================================================
! SECTION 2 : DEFINITION DU FLEX-ALGO 128 DANS IS-IS
! =====================================================================
router isis CORE-SRv6
 net 49.0001.0000.0000.0003.00
 metric-style wide
 
 flex-algo 128
  metric-type delay
  advertise-definition
 !

 address-family ipv6 unicast
  metric-style wide
  segment-routing srv6
   locator MAIN-uSID
   !
   locator LATENCY-uSID level 2
    algo 128
   !
  !
 !

 interface TenGigE0/0/0/0
  point-to-point
  address-family ipv6 unicast
   fast-reroute per-prefix ti-lfa
  !
 !
!

! =====================================================================
! SECTION 3 : ASSOCIATION L3VPN AVEC SRv6 End.DT4 (VRF BANQUE)
! =====================================================================
vrf BANQUE
 address-family ipv4 unicast
  import route-target
   100:10
  !
  export route-target
   100:10
  !
  segment-routing srv6
   alloc mode per-vrf
   locator MAIN-uSID
  !
 !
!

```

## 5. Automation Programmatique & Diagnostic Bas-Niveau

À l'échelle Expert, le monitoring des architectures SRv6 et SR-TE s'appuie sur la télémétrie en temps réel (**gNMI / gRPC**) et sur les outils de sondage OAM natifs (RFC 8402 / RFC 8287).

### 1. Diagnostic SRv6 / SR-TE via Ping et Trace OAM

Contrairement au Ping/Traceroute IP classique, les paquets **MPLS/SRv6 OAM** interrogent directement le plan de contrôle du nœud distant pour valider l'alignement entre le segment sollicité et la VRF/Service sous-jacent.

```
# Test de connectivité vers un SRv6 SID spécifique (End.DT4)
ping srv6 2001:db8:1:3::fe10 source 2001:db8:1::1

# Inspection du chemin explicite d'une SR Policy avec affichage des SIDs
traceroute sr-te policy name POLICY_VOICE_LOW_LATENCY verbose

```

### 2. Monitoring Programmatique gNMI / YANG (Telemetry Stream)

L'extraction de l'état des tunnels SR-TE et des erreurs de basculement TI-LFA s'effectue au travers du modèle OpenConfig YANG `openconfig-segment-routing.yang` via **gNMI (gRPC Network Management Interface)**.

```python
#!/usr/bin/env python3
"""
Script Expert gNMI Client:
Abonnement en streaming aux métriques de trafic SR Policy (Cisco IOS-XR / Junos)
"""

from pygnmi.client import gNMIclient
import json

TARGET = ("10.0.0.3", 57400)
USER = "admin"
PASS = "Cisco123!"

# Chemin OpenConfig YANG pour les statistiques SR-TE
SR_POLICY_PATH = [
    "openconfig-network-instance:network-instances/network-instance[name=default]/"
    "segment-routing/te-policies/te-policy"
]

def stream_sr_telemetry():
    with gNMIclient(target=TARGET, username=USER, password=PASS, skip_verify=True) as client:
        print("[+] Etablissement de la session gNMI Streaming...")
        
        subscribe_args = {
            'path': SR_POLICY_PATH,
            'mode': 'stream',
            'submode': 'sample',
            'sample_interval': 10000000000  # 10 secondes
        }
        
        for response in client.subscribe(subscribe_args=subscribe_args):
            update = response.get('update', {})
            if 'update' in update:
                for val in update['update']:
                    path = val.get('path', '')
                    data = val.get('val', {})
                    print(f"[TELEMETRY DATA] Path: {path} | Content: {json.dumps(data)}")

if __name__ == "__main__":
    stream_sr_telemetry()
```

## Points à retenir

* **PCE / PCEP & BGP-LS** : Permet le calcul de chemin SR-TE centralisé inter-domaines. BGP-LS remonte la topologie au PCE, et PCEP (RFC 5440) instancie les politiques sur les routeurs Ingress.

* **SRv6 Network Programming** : Codé sur des adresses IPv6 de 128 bits structurées en `Locator`, `Function` (ex: `End.DT4` pour L3VPN, `End.X` pour Adj-SID) et `Argument`.

* **uSID (Micro-Segment)** : Compresse plusieurs SIDs de 16 bits au sein d'une unique adresse IPv6 de 128 bits, éliminant le surcoût de l'en-tête SRH.

* **Flex-Algo (Flexible Algorithm)** : Découpe l'IGP en topologies virtuelles autonomes (Slices 128-255) basées sur des métriques personnalisées (ex: Delay Unidirectional) ou des contraintes d'exclusion de liaisons.