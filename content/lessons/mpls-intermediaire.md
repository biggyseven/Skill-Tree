# MPLS et VRF (MPLS L3VPN & MP-BGP) - Intermédiaire

**Niveau :** Intermédiaire

**Prérequis :** MPLS et VRF Débutant (`mpls-debutant`), notions de base sur BGP (eBGP, iBGP, Peerings).

Dans le module **Débutant**, nous avons abordé les fondamentaux des VRF et la commutation d'étiquettes MPLS unicast via LDP. Au niveau **Intermédiaire**, nous allons combiner ces deux briques pour comprendre l'architecture des réseaux privés virtuels de niveau 3 : les **MPLS L3VPN** (RFC 4364 / ancienne RFC 2547).

Ce cours détaille le rôle de **MP-BGP (Multiprotocol BGP)**, la création des sous-réseaux **VPN-IPv4**, le rôle du **Route Distinguisher (RD)**, la politique d'import/export par **Route Target (RT)**, et le fonctionnement de l'empilement à deux niveaux d'étiquettes (*Two-Level Label Stack*).

---

## 1. L'Architecture MPLS L3VPN

Dans une infrastructure d'opérateur (*Service Provider*), l'objectif est d'interconnecter plusieurs sites clients distants à travers une infrastructure IP/MPLS partagée, tout en garantissant :

1. L'étanchéité absolue entre les clients.
2. La conservation des blocs d'adresses IP privés des clients (gestion des chevauchements d'adresses IP).
3. La scalabilité du réseau de cœur (les routeurs de cœur **P** ne doivent pas connaître les routes de tous les clients).

```
 ┌──────────┐                                                               ┌──────────┐
 │ Site A1  │───( CE-A1 )                                       ( CE-A2 )───│ Site A2  │
 └──────────┘       │                                               │       └──────────┘
                    ▼                                               ▼
              ┌───────────┐         ┌───────────┐         ┌───────────┐
              │  PE1      │─────────│  Routeur  │─────────│  PE2      │
              │ (Ingress) │         │     P     │         │ (Egress)  │
              └───────────┘         └───────────┘         └───────────┘
                    ▲                                               ▲
 ┌──────────┐       │                                               │       ┌──────────┐
 │ Site B1  │───( CE-B1 )                                       ( CE-B2 )───│ Site B2  │
 └──────────┘                                                               └──────────┘
```

---

## 2. Lever le chevauchement IP : Le Route Distinguisher (RD)

Deux clients distincts peuvent utiliser le même sous-réseau privé (`10.0.0.0/24`). Si un routeur PE reçoit le préfixe `10.0.0.0/24` venant de deux VRF différentes, il ne peut pas les transmettre directement en BGP classique car ces préfixes entreraient en conflit.

### Format du Route Distinguisher (RD)
Le **Route Distinguisher (RD)** est un préfixe de **64 bits (8 octets)** ajouté au début de l'adresse IPv4 de 32 bits pour la rendre unique sur le plan de contrôle.

$$\text{VPN-IPv4 Address} = \text{Route Distinguisher (64 bits)} + \text{IPv4 Prefix (32 bits)}$$

Le résultat forme une adresse **VPN-IPv4 de 96 bits**.

```
 0                            16                           64                          96
+----------------------------+----------------------------+---------------------------+
|        Type (2 octets)     |   Administrateur / Valeur  |   Adresse IPv4 (32 bits)  |
+----------------------------+----------------------------+---------------------------+
 \───────────────────────────────────────────────────────/ \─────────────────────────/
                   Route Distinguisher (RD)                    Préfixe Client IPv4
```

* **Formats courants de RD :**
  * `ASN:nn` (ex: `65000:100`)
  * `IP-address:nn` (ex: `192.168.1.1:10`)

> **Règle capitale :** Le RD sert uniquement à rendre une route **unique** dans BGP. Il ne détermine **pas** quelles VRF peuvent échanger ou importer ces routes.

---

## 3. Le Contrôle des Topologies : Le Route Target (RT)

Pour définir la politique d'interconnexion entre les VRFs (topologie Hub-and-Spoke, Full-Mesh, Extranet), MP-BGP utilise une **BGP Extended Community (8 octets)** appelée **Route Target (RT)**.

Contrairement au RD qui est unique par route, chaque route VPN-IPv4 transporte une ou plusieurs balises RT.

```
                  ┌──────────────────────────────────────────────┐
                  │          PE1 (Export RT 100:1)               │
                  └──────────────────────┬───────────────────────┘
                                         │ MP-BGP Update
                                         │ Route: 10.1.1.0/24 (RT 100:1)
                                         ▼
         ┌───────────────────────────────┴───────────────────────────────┐
         │                                                               │
         ▼                                                               ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│  PE2 (Import RT 100:1)        │               │  PE3 (Import RT 200:2)        │
│  => ROUTE ACCEPTÉE DANS VRF A │               │  => ROUTE IGNORÉE / REJETÉE   │
└───────────────────────────────┘               └───────────────────────────────┘
```

### Types de Route Targets :
1. **Export Route Target :** Détermine les balises RT attachées à une route lorsqu'elle est exportée de la VRF locale vers MP-BGP.
2. **Import Route Target :** Détermine quelles routes MP-BGP entrantes sont acceptées et injectées dans la VRF locale.

---

## 4. Le Plan de Contrôle : MP-BGP (Multiprotocol BGP)

Le BGP standard ne prend en compte que les adresses IPv4 Unicast (`AFI=1, SAFI=1`). Pour transporter les routes VPN-IPv4 de 96 bits et leurs attributs spécifiques (RT, VPN Label), on utilise l'extension **MP-BGP (RFC 4760)**.

* **Address Family (AFI/SAFI) :** `vpnv4 unicast` (`AFI=1, SAFI=128`).
* **Attributes MP-BGP :**
  * `MP_REACH_NLRI` : Transporte le préfixe VPN-IPv4, le Next-Hop BGP (adresse du PE émetteur) et le **VPN Service Label**.
  * `Extended Community` : Transporte le **Route Target (RT)**.

---

## 5. Le Plan de Données : Empilement à Deux Étiquettes (*Two-Level Label Stack*)

Lorsqu'un paquet IP traverse le cœur MPLS d'une VRF source à une VRF destination, il est encapsulé avec **deux étiquettes MPLS** :

```
+-------------------+--------------------+------------------+-----------------+
| En-tête Ethernet  |  Outer Label (LDP) |  Inner Label     | Paquet IP Client|
|    (Couche 2)     |  Transport Label   |  (VPN Service)   |  (Données IP)   |
+-------------------+--------------------+------------------+-----------------+
```

```
[ Paquet IP ] ──> ( Ingress PE ) ──> [ Outer Label (LDP) | Inner Label (VPN) | IP ]
                                            │
                                            ▼ (Commutation par Outer Label)
                                     [ Routeur P Core ]
                                            │
                                            ▼ (PHP - Penultimate Hop Popping)
                                     [ Inner Label (VPN) | IP ]
                                            │
                                            ▼
                                      ( Egress PE ) ──> Decapsulation VPN Label ──> [ Paquet IP ] ──> VRF Client
```

1. **Outer Label (Transport / IGP Label) :**
   * Généré par **LDP** (ou RSVP-TE/SR).
   * Utilisé par les routeurs **P (Core)** pour acheminer le paquet à travers le cœur du réseau jusqu'au PE distant (*Next-Hop BGP*).
   * Subit des opérations `SWAP` à chaque saut dans le cœur.

2. **Inner Label (VPN / Service Label) :**
   * Attribué par le **PE destinataire (Egress PE)** via MP-BGP pour identifier la VRF exacte ou l'interface de sortie du client.
   * Reste **intact** pendant toute la traversée du cœur MPLS.
   * Est lu uniquement par l'Egress PE après le retrait du Transport Label (via **PHP - Penultimate Hop Popping**).

---

## 6. Configuration Exemple : MPLS L3VPN (Cisco IOS)

### 1. Configuration des VRF et des Route Targets sur le PE

```
! --- Configuration VRF Client Alpha ---
vrf definition CLIENT_ALPHA
 rd 65000:100
 !
 address-family ipv4
  route-target export 65000:100
  route-target import 65000:100
 exit-address-family
!
interface GigabitEthernet0/1
 description Interface connectee au client CE-A1
 vrf forwarding CLIENT_ALPHA
 ip address 192.168.10.1 255.255.255.0
```

### 2. Configuration MP-BGP iBGP entre les PE

```
router bgp 65000
 bgp router-id 1.1.1.1
 neighbor 3.3.3.3 remote-as 65000
 neighbor 3.3.3.3 update-source Loopback0
 !
 address-family vpnv4
  neighbor 3.3.3.3 activate
  neighbor 3.3.3.3 send-community extended
 exit-address-family
 !
 address-family ipv4 vrf CLIENT_ALPHA
  redistribute connected
 exit-address-family
```

---

## 7. Commandes de Vérification Essentielles

| Commande (Cisco IOS) | Description / Objectif |
| ----- | ----- |
| `show bgp vpnv4 unicast all` | Affiche la table de routage MP-BGP contenant toutes les routes VPN-IPv4. |
| `show bgp vpnv4 unicast vrf <NOM>` | Affiche les préfixes MP-BGP appris/annoncés pour une VRF spécifique. |
| `show ip route vrf <NOM>` | Affiche les routes injectées dans la table d'une VRF spécifique. |
| `show mpls forwarding-table` | Affiche les correspondances d'étiquettes MPLS (Transport & VPN Labels). |

---

## Points à retenir

* **VPN-IPv4 (96 bits) = RD (64 bits) + IPv4 (32 bits)** : Utilisé par MP-BGP pour lever les conflits d'adressage IP.
* **Route Target (RT)** : Une communauté BGP extended qui contrôle l'importation et l'exportation des routes dans les VRFs.
* **MP-BGP (AFI 1, SAFI 128)** : Échange les routes VPN-IPv4 et les VPN Service Labels entre les PE.
* **Deux étiquettes MPLS (Two-Label Stack)** :
  * **Outer Label (LDP)** : Transporte le paquet à travers le cœur d'un PE à un autre.
  * **Inner Label (VPN)** : Identifie la VRF destination ou le lien d'accès sur l'Egress PE.