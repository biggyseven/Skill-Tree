# MPLS et VRF (Inter-AS VPN, CSC & Segment Routing) - Expert

**Niveau :** Expert

**Prérequis :** MPLS et VRF Intermédiaire (`mpls-intermediaire`), maîtrise approfondie de BGP (eBGP, iBGP, Route Reflectors) et des principes de commutation MPLS L3VPN.

Dans ce module de niveau **Expert**, nous abordons la mise à l'échelle des architectures MPLS L3VPN à travers plusieurs Systèmes Autonomes (**Inter-AS VPN**), le modèle **Carrier Supporting Carrier (CSC)** et l'évolution moderne vers le **Segment Routing (SR-MPLS)**.

---

## 1. Inter-AS MPLS L3VPN

Lorsque les sites d'un même client VPN sont raccordés à des fournisseurs d'accès différents (ou à des AS BGP distincts au sein du même opérateur), les routes VPN-IPv4 doivent traverser les frontières d'AS (*Autonomous System Borders*). La RFC 4364 définit trois architectures principales : **Option A**, **Option B** et **Option C**.

---

### Option A : VRF-to-VRF aux routeurs de bordure (ASBR)

L'Option A (back-to-back VRF) est l'approche la plus simple. Les routeurs **ASBR** (*Autonomous System Border Routers*) se comportent mutuellement comme des équipements **CE** (*Customer Edge*).

```
   AS 65001 (Opérateur A)              │              AS 65002 (Opérateur B)
                                       │
┌────────┐     ┌──────────┐            │            ┌──────────┐     ┌────────┐
│  PE1   │────>│  ASBR1   │──[ VRF A ]─┼──[ VRF A ]─│  ASBR2   │────>│  PE2   │
│ (VRF A)│     │(VRF A/B) │──[ VRF B ]─┼──[ VRF B ]─│(VRF A/B) │     │ (VRF A)│
└────────┘     └──────────┘            │            └──────────┘     └────────┘
                   sub-interfaces / VLANs séparés
```

#### Caractéristiques :
* **Plan de contrôle :** Pas de session MP-BGP entre les ASBR. Les routes sont échangées via eBGP standard (ou un IGP) sur des sub-interfaces/VLANs dédiés par VRF.
* **Plan de données :** Le trafic traverse les ASBR sous forme de paquets **IP natifs** (non étiquetés MPLS).
* **Avantages :** Très simple à mettre en œuvre, aucune confiance requise sur le plan MPLS entre opérateurs.
* **Inconvénients :** Manque de scalabilité. Chaque VRF nécessite une sous-interface et une session de routage dédiée entre les ASBR. Risque de saturation de la table de routage et de la mémoire des ASBR.

---

### Option B : MP-eBGP Hop-by-Hop entre ASBRs

L'Option B établit une session **MP-eBGP (VPN-IPv4)** directement entre les ASBR.

```
   AS 65001 (Opérateur A)              │              AS 65002 (Opérateur B)
                                       │
┌────────┐     ┌──────────┐  MP-eBGP   │            ┌──────────┐     ┌────────┐
│  PE1   │────>│  ASBR1   │────────────┼───────────>│  ASBR2   │────>│  PE2   │
└────────┘     └──────────┘ (VPN-IPv4) │            └──────────┘     └────────┘
                    ▲                  │                 ▲
                    └────── Swap Label ┴─ Swap Label ────┘
```

#### Caractéristiques :
* **Plan de contrôle :** Les ASBR maintiennent une session MP-eBGP. Ils reçoivent les routes VPN-IPv4, réécrivent le Next-Hop BGP (`next-hop-self`) et attribuent une nouvelle étiquette VPN (*VPN Label Swap*).
* **Plan de données :** Le trafic entre ASBR est encapsulé dans **une seule étiquette MPLS** (le VPN Label).
* **Avantages :** Plus scalable que l'Option A (pas besoin de VRF ni de sous-interfaces dédiées sur les ASBR).
* **Inconvénients :** Les ASBR doivent stocker toutes les routes VPN-IPv4 de tous les clients inter-AS dans leur mémoire BGP.

---

### Option C : Multihop MP-eBGP entre PEs avec BGP IPv4 + Label (RFC 3107)

L'Option C offre la meilleure scalabilité en établissant une session MP-eBGP end-to-end directement entre les **PEs** des deux AS (ou via des Route Reflectors).

```
   AS 65001 (Opérateur A)              │              AS 65002 (Opérateur B)
                                       │
┌────────┐                             │                             ┌────────┐
│  PE1   │=================== MP-eBGP (VPN-IPv4) ===================>│  PE2   │
└───┬────┘                             │                             └───┬────┘
    │          ┌──────────┐  eBGP+Label│ (RFC 3107)  ┌──────────┐        │
    └─────────>│  ASBR1   │────────────┼────────────>│  ASBR2   │────────┘
               └──────────┘            │             └──────────┘
```

#### Caractéristiques :
* **Plan de contrôle :**
  1. Les ASBR échangent les adresses Loopback des PEs via **eBGP RFC 3107 (BGP IPv4 + Label)** ou **Labeled BGP (SAFI 4)**.
  2. Les PEs établissent une session **MP-eBGP Multihop** directe pour échanger les routes VPN-IPv4.
* **Plan de données :** Empilement à **3 étiquettes MPLS** :
  1. *Outer Label :* IGP/LDP local vers l'ASBR.
  2. *Middle Label :* Labeled BGP (transport inter-AS vers le PE distant).
  3. *Inner Label :* VPN Label (attribué par le PE distant).
* **Avantages :** Extrêmement scalable. Les ASBR n'ont aucune connaissance des routes VPN clients ni des VPN Labels.
* **Inconvénients :** Complexité de configuration et nécessité de distribuer les boucles des PEs entre opérateurs.

---

## 2. Table Comparative des Options Inter-AS

| Critère | Option A | Option B | Option C |
| :--- | :--- | :--- | :--- |
| **Session BGP entre ASBR** | IPv4 Unicast (per-VRF) | MP-eBGP (VPN-IPv4) | Labeled BGP (IPv4 + Label) |
| **VRF requises sur ASBR** | Oui (une par client) | Non | Non |
| **Connaissance des routes VPN par ASBR** | Oui | Oui | **Non** |
| **Étiquettes MPLS entre ASBR** | 0 (IP pur) | 1 (VPN Label) | 1 (BGP Transport Label) |
| **Nombre d'étiquettes au cœur** | 2 | 2 | **3** |
| **Scalabilité** | Faible | Moyenne | **Très élevée** |

---

## 3. Carrier Supporting Carrier (CSC)

Le modèle **Carrier Supporting Carrier (CSC)** s'applique lorsqu'un opérateur de télécommunications (*Customer Carrier*) utilise le réseau de cœur MPLS d'un autre opérateur (*Backbone Carrier*) pour relier ses propres sites.

```
       [ Client Final ]
              │
              ▼
   ┌──────────────────────┐
   │  Customer Carrier    │ (Super-Réseau / FAI Client)
   │  (CSC-CE / CSC-PE)   │
   └──────────┬───────────┘
              │ MPLS / Labeled BGP
              ▼
   ┌──────────────────────┐
   │   Backbone Carrier   │ (Opérateur de Gros / Transit)
   │     (CSC-PE / P)     │
   └──────────────────────┘
```

### Fonctionnement clé :
1. Le **Customer Carrier** gère ses propres VRF et services L3VPN pour ses clients finaux.
2. Le **Backbone Carrier** fournit uniquement le transport des étiquettes d'infrastructure du Customer Carrier.
3. **Gain de scalabilité :** Le Backbone Carrier ne stocke que les routes des équipements d'infrastructure du Customer Carrier (PE Loopbacks), réduisant drastiquement la taille des tables de routage.

---

## 4. Évolution moderne : Segment Routing (SR-MPLS)

Le **Segment Routing (SR)** simplifie le plan de contrôle MPLS en éliminant le besoin de protocole de distribution dédié comme LDP ou RSVP-TE.

```
                  ┌─────────────────────────────────────────┐
                  │        Segment Routing Control          │
                  │   (Extensions IGP : IS-IS / OSPF)       │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
 ┌──────────────┐             ┌─────────────────┐             ┌──────────────┐
 │  Ingress PE  │────────────>│  Routeur P SR   │────────────>│  Egress PE   │
 │ Prefix-SID:  │             │ (Node-SID 16003)│             │  Node-SID:   │
 │   16001      │             └─────────────────┘             │    16003     │
 └──────────────┘                                             └──────────────┘
```

### Principes clés du SR-MPLS :
* **Unified Control Plane :** Les extensions IGP (**OSPF-SR** / **IS-IS-SR**) distribuent directement les étiquettes MPLS (appelées **SIDs** - *Segment Identifiers*).
* **Node-SID / Prefix-SID :** Étiquette globale unique attribuée à un routeur (ex: `16001` pour PE1, `16003` pour PE2).
* **Suppression de LDP :** Le plan de données reste l'en-tête MPLS standard (32 bits), mais la signalisation LDP n'est plus requise.
* **Source Routing :** L'Ingress PE spécifie le chemin complet à travers la pile d'étiquettes imposée au paquet.

---

## 5. Configuration Exemple : Inter-AS Option B (Cisco IOS)

### Configuration ASBR1 (AS 65001)

```
! --- Configuration de l'interface d'interconnexion Inter-AS ---
interface GigabitEthernet0/2
 description Lien vers ASBR2 (AS 65002)
 ip address 192.168.12.1 255.255.255.252
 mpls ip
!
! --- Configuration BGP ---
router bgp 65001
 bgp router-id 10.0.0.11
 neighbor 192.168.12.2 remote-as 65002
 !
 address-family vpnv4
  neighbor 192.168.12.2 activate
  neighbor 192.168.12.2 send-community extended
  ! Permet aux ASBR de conserver les routes VPNv4 sans VRF locales
  no bgp default route-target filter
 exit-address-family
```

---

## Commandes de Vérification Expert

| Commande (Cisco IOS) | Description / Objectif |
| :--- | :--- |
| `show bgp vpnv4 unicast all summary` | Vérifie l'état des sessions MP-BGP (iBGP et Inter-AS eBGP). |
| `show bgp vpnv4 unicast all labels` | Affiche les étiquettes VPN et de transport BGP associées aux préfixes. |
| `show mpls forwarding-table` | Analyse la pile complète d'étiquettes (Transport, BGP, VPN Labels). |
| `show segment-routing mpls lb` | Affiche la table des SIDs et les blocs d'étiquettes SRGB (*Segment Routing Global Block*). |

---

## Points à retenir

* **Inter-AS Option A :** Simple mais non-scalable (session VRF dédiée par client sur ASBR, pas de MPLS entre ASBR).
* **Inter-AS Option B :** Transfert VPN-IPv4 via MP-eBGP avec réécriture d'étiquettes sur les ASBRs.
* **Inter-AS Option C :** Scalabilité maximale via session MP-eBGP directe entre PEs et diffusion des Loopbacks en Labeled BGP (RFC 3107).
* **Segment Routing (SR-MPLS) :** Simplifie le plan de contrôle MPLS en intégrant la distribution des étiquettes (SIDs) directement dans l'IGP (OSPF/IS-IS), remplaçant LDP.