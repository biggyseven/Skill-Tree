# IPv6 (Internet Protocol version 6) - Expert

**Niveau :** Expert

À l'échelle des grands réseaux d'opérateurs télécoms, des datacenters hyper-scalables et des architectures d'interconnexion mondiales (IXP), IPv6 cesse d'être une simple alternative d'adressage pour devenir le moteur fondamental de l'ingénierie de trafic moderne. Les exigences contemporaines ne tolèrent plus le moindre goulot d'étranglement lié à la traduction d'adresses (NAT) ni les surcoûts d'état (*stateful overhead*) imposés par les anciennes technologies de transition. Les architectures modernes reposent sur des modèles purement IPv6 (*IPv6-Only Data Centers* et *IPv6-Only Backbone*), au sein desquels IPv4 est traité comme un simple service encapsulé ou traduit à la bordure.

L'évolution de la pile protocolaire IPv6 au niveau expert s'incarne principalement dans deux paradigmes : le routage par la source de nouvelle génération via **SRv6 (Segment Routing over IPv6 Data Plane)** et les mécanismes de transition à très haute performance et sans état comme **MAP-T (Mapping of Address and Port - Translation)** ou **MAP-E**. L'introduction de SRv6 (RFC 8986, RFC 8754) exploite les en-têtes d'extension IPv6 (Routing Extension Header - SRH) pour encoder des instructions de traitement (*Segments/SIDs*) directement dans l'adresse de destination IPv6, éliminant ainsi le besoin de protocoles de signalisation MPLS complexes (LDP, RSVP-TE) sur le cœur de réseau.

Parallèlement, l'interconnexion globale en MP-BGP (Multi-Protocol BGP) pour IPv6 impose la maîtrise de concepts avancés tels que les capacités MP-BGP EVPN avec overlay IPv6, le sous-protocole BGP L3VPN (RFC 4659), la négociation de sous-familles d'adresses (AFI/SAFI), ainsi que la sécurisation des annonces BGP au niveau mondial via **RPKI (Resource Public Key Infrastructure)** et **BGPsec**. La maîtrise d'IPv6 à ce niveau d'expertise exige une compréhension microscopique du traitement matériel des paquets, de l'alignement mémoire des en-têtes d'extension et du comportement des ASICs de commutation.

> **Analogie** : Imaginez un système de transport postal mondial (Backbone IP). Au niveau basique, une lettre contient juste l'adresse d'arrivée. Au niveau intermédiaire, les centres de tri locaux placent la lettre dans un conteneur régional avec un code-barres (MPLS). Au niveau Expert avec SRv6, la lettre elle-même porte une suite d'étiquettes prédécoupées directement sur son enveloppe extérieure (IPv6 Extension Header). Chaque plateforme logistique internationale lit simplement la première étiquette visible, applique immédiatement l'instruction exacte (ex: "Consigne en chambre froide", "Traverse la mer par le vol 402", "Livre directement à la filiale Y"), puis décolle l'étiquette pour exposer la suivante. Il n'y a plus besoin de conteneurs spéciaux ni de registres locaux séparés : l'en-tête de la lettre porte de façon totalement autonome tout le programme de routage et de traitement personnalisé à travers le monde.

## 1. La théorie et les algorithmes

### 1.1. SRv6 (Segment Routing over IPv6) et l'En-tête SRH

SRv6 utilise le plan de données IPv6 natif pour mettre en œuvre le routage par segments. Au lieu de s'appuyer sur des étiquettes MPLS de 20 bits, un segment SRv6 (appelé **SID - Segment Identifier**) est structuré exactement comme une adresse IPv6 de 128 bits.

Structure standard d'un SID SRv6 (128 bits) :

* **Locator (32 à 64 bits) :** Préfixe routable par les IGP standards (ISIS/OSPFv3) guidant le paquet vers le nœud d'exécution.

* **Function (16 à 32 bits) :** Instruction opérationnelle exécutée localement par l'ASIC du nœud cible (ex: `End`, `End.X`, `End.DT4`, `End.DT6`).

* **Args (Optionnel) :** Arguments complémentaires pour la fonction.

L'en-tête d'extension **SRH (Segment Routing Header - Type 4)** est inséré après l'en-tête fixe IPv6 :

$$
\text{Next Header} = 43 \text{ (Routing)}, \quad \text{Routing Type} = 4 \text{ (SRH)}
$$

Il contient une liste ordonnée de SIDs IPv6 (`Segment List [0..n]`) lue en sens inverse. Le champ `Segments Left` agit comme un pointeur vers le segment actif, décrémenté à chaque étape de routage par la source.

```
+-----------------------------------------------------------------------------------+
|                        STRUCTURE D'UN PAQUET SRv6 (EN-TÊTE + SRH)                 |
+-----------------------------------------------------------------------------------+

 IPv6 Header:
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |Version| Traffic Class |           Flow Label                  |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |         Payload Length        | Next Header=43|   Hop Limit   |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Source Address: 2001:db8:1::1 (Ingress PE)                    |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Destination Address: 2001:db8:cafe:2::End.X (Segment Actif)  |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

 Segment Routing Header (SRH - Extension Header Type 4):
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Next Header=59| Hdr Ext Len=6 | Routing Type=4| Segments Left=1|
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Last Entry=2  | Flags=0       | Tag=0                         |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Segment List[0]: 2001:db8:cafe:3::End.DT6 (Egress Node/VPN)  |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Segment List[1]: 2001:db8:cafe:2::End.X   (Transit Node 2)   |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Segment List[2]: 2001:db8:cafe:1::End     (Transit Node 1)   |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 1.2. MP-BGP IPv6 & RPKI (Resource Public Key Infrastructure)

En MP-BGP (RFC 4760), le support d'IPv6 s'effectue via les identifiants AFI/SAFI :

* **AFI (Address Family Identifier) :** `2` pour IPv6.

* **SAFI (Subsequent Address Family Identifier) :** `1` pour Unicast, `128` pour L3VPN.

Les attributs BGP d'accessibilité sont transportés dans de nouveaux attributs optionnels non-transitifs :

* **MP_REACH_NLRI (Type 14) :** Annonce des préfixes IPv6 et de l'adresse du Next-Hop IPv6.

* **MP_UNREACH_NLRI (Type 15) :** Retrait des routes IPv6.

#### Sécurisation BGP IPv6 par RPKI / Route Origin Validation (ROV)

RPKI valide l'association entre un système autonome (AS) et un préfixe IPv6 au moyen d'objets cryptographiques signés appelés **ROA (Route Origin Authorization)**.

Lors du traitement d'une mise à jour MP-BGP IPv6, le routeur évalue la validité RPKI selon 3 états :

1. **Valid :** Le préfixe IPv6 et l'AS d'origine matchent un objet ROA cryptographiquement valide.

2. **Invalid :** Le préfixe est trouvé dans un ROA mais provient d'un AS non autorisé, ou la longueur du préfixe dépasse la longueur maximale (`max-length`) spécifiée dans le ROA.

3. **NotFound / Unknown :** Aucun ROA n'a été publié pour ce préfixe IPv6.

### 1.3. Algorithme de Transition Sans État : MAP-T (Mapping of Address and Port - Translation)

MAP-T (RFC 7599) réalise une traduction d'en-tête double (IPv4 $\leftrightarrow$ IPv6) totalement **stateless** à la frontière du réseau d'accès.

Il découpe un préfixe IPv4 unique entre plusieurs abonnés en assignant à chacun un jeu exclusif de ports TCP/UDP via un champ appelé **PSID (Port Set Identifier)**.

L'adresse IPv6 d'un utilisateur MAP-T est construite algorithmiquement :

$$
\text{Adresse IPv6 MAP-T} = [\text{Rule Prefix IPv6}] + [\text{IPv4 Address}] + [\text{PSID}] + [\text{End-User Interface ID}]
$$

Lorsqu'un paquet IPv4 sort du réseau client, le routeur CE applique l'algorithme MAP-T pour générer directement l'adresse IPv6 source et destination sans maintenir aucune table d'état en mémoire. Le routeur Border BR (*Border Relay*) inverse l'algorithme pour restituer le paquet IPv4 d'origine.

> **Piège :** Lors du chaînage d'en-têtes d'extension IPv6 (ex: IPv6 + Hop-by-Hop + SRH + ESP + Segment TCP), la profondeur de recherche (*Header Chain Depth*) peut dépasser la capacité de découpage du TCAM/ASIC des équipements d'ancienne génération. Cela provoque la chute du paquet dans le *Control Plane* (CPU) du routeur ou un rejet pur et simple du trafic (*blackholing*).

```
+-----------------------------------------------------------------------------------+
|                     ARCHITECTURE OPÉRATEUR SRv6 + MP-BGP + RPKI                  |
+-----------------------------------------------------------------------------------+

     [ Client A / IPv6-VPN ]                              [ Client B / IPv6-VPN ]
                |                                                    |
         +--------------+                                    +--------------+
         | PE-1 (Ingress|                                    | PE-2 (Egress |
         |   SRv6)      |                                    |   SRv6)      |
         +--------------+                                    +--------------+
           /          \                                        /          \
    +------------+  +------------+                      +------------+  +------------+
    |   P-1      |  |   P-2      |--- [IGP IS-IS v6] ---|   P-3      |  |   P-4      |
    +------------+  +------------+                      +------------+  +------------+
           \          /                                        \          /
         +------------------------------------------------------------------+
         | Serveur RPKI Validator (RTR Protocol - Cache de ROAs Certifiés) |
         +------------------------------------------------------------------+
```

## 2. Configuration et Pratique

Voici une configuration complète au niveau Expert pour un routeur Edge PE Cisco IOS-XR / IOS-XE combinant **MP-BGP IPv6**, **Validation RPKI**, et **SRv6 (Locator & Functions)**.

### Configuration complète Cisco IOS-XE (Enterprise/Carrier Edge)

```cisco
! ===================================================================
! CONFIGURATION DU LOCATOR SRv6 ET DU PLAN DE DONNÉES
! ===================================================================
segment-routing mpls
!
segment-routing ipv6
 encapsulation
  source-address 2001:db8:infra::1
 !
 locator MAIN_LOCATOR
  prefix 2001:db8:cafe:1::/64
 !
 Flex-algo 128
  metric-type te
 !
 locators
  locator MAIN_LOCATOR
   locator-id 1
   ! Allocation des fonctions automatiques pour les VPNs
   auto-sid
exit

! ===================================================================
! CONFIGURATION DU PROTOCOLE RPKI (RTR SERVER CONNECTION)
! ===================================================================
router bgp 65000
 bgp router-id 10.0.0.1
 bgp log-neighbor-changes
 !
 ! Validation RPKI pour la sous-famille IPv6
 rpki cache 192.168.100.50 323 port 323 refresh 300
 !
 address-family ipv6 unicast
  bgp rpki server-authoritative
  import path selection all
 exit-address-family

! ===================================================================
! ROUTE-MAPS DE SÉCURITÉ BGP ET FILTRAGE RPKI ROV
! ===================================================================
route-map BGP_PEER_IN_V6 permit 10
 match rpki valid
 ! Application d'un Local Preference supérieur pour les routes validées
 set local-preference 200
exit

route-map BGP_PEER_IN_V6 permit 20
 match rpki not-found
 set local-preference 100
exit

route-map BGP_PEER_IN_V6 deny 30
 ! Rejet strict de toutes les annonces BGP IPv6 "Invalid"
 match rpki invalid
exit

! ===================================================================
! CONFIGURATION MP-BGP EVPN / L3VPN AVEC SRv6 STEERING
! ===================================================================
router bgp 65000
 neighbor 2001:db8:infra::2 remote-as 65000
 neighbor 2001:db8:infra::2 update-source Loopback0
 !
 address-family ipv6 unicast
  neighbor 2001:db8:infra::2 activate
  neighbor 2001:db8:infra::2 route-map BGP_PEER_IN_V6 in
  neighbor 2001:db8:infra::2 send-community extended
  ! Activation de la résolution de Next-Hop via SRv6 Locator
  segment-routing ipv6 locator MAIN_LOCATOR
 exit-address-family
 !
 address-family vpnv6 unicast
  neighbor 2001:db8:infra::2 activate
  neighbor 2001:db8:infra::2 send-community extended
  neighbor 2001:db8:infra::2 segment-routing ipv6 locator MAIN_LOCATOR
 exit-address-family
exit

! ===================================================================
! INTERFACE CORE ET INFRASTRUCTURE SRv6
! ===================================================================
interface TenGigabitEthernet0/0/0
 description CORE_LINK_TO_P1
 no ip address
 ipv6 address fe80::1:1 link-local
 ipv6 address 2001:db8:infra:12::1/64
 ipv6 enable
 ! Activation d'IS-IS avec extensions SRv6
 ip router isis CORE
 isis ipv6 metric 10
exit

router isis CORE
 net 49.0001.0000.0000.0001.00
 metric-style wide
 !
 address-family ipv6 unicast
  multi-topology
  segment-routing ipv6 locator MAIN_LOCATOR
 exit-address-family
exit
```

> **Astuce :** Sur les équipements Cisco IOS-XR / XE de bordure, utilisez la commande `show segment-routing ipv6 locator` et `show bgp ipv6 unicast rpki table` pour vous assurer que les SIDs SRv6 sont correctement alloués et synchronisés avec le RIB IPv6 sans injection d'erreurs de programmation mémoire dans l'ASIC (*TCAM programming error*).

## 3. Dépannage et Sécurité

### 3.1. Diagnostic avancé des pannes SRv6 et MP-BGP

1. **SRv6 Path Blackholing (Différences PMTUD et MSS Clamping) :** L'ajout de l'en-tête SRH augmente la taille totale du paquet de $8 + (n \times 16)$ octets. Si la MTU du cœur de réseau n'est pas réhaussée à minimum 9100 octets (*Jumbo Frames*), la fragmentation IP sera déclenchée ou les paquets portant le bit DF (*Don't Fragment*) seront rejetés.

2. **Désynchronisation RPKI RTR :** Si le lien entre le routeur BGP et le validateur RPKI (Cache Server) s'interrompt, le temporisateur `expire-time` s'enclenche. À son expiration, toutes les routes préalablement marquées comme `Valid` retombent dans l'état `NotFound`, ce qui peut altérer l'ingénierie de trafic basée sur la métrique `Local-Preference`.

Commandes d'investigation niveau Expert :

* `show bgp ipv6 unicast rpki summary` : Affiche l'état des sessions RTR et le nombre de ROAs chargés en mémoire.

* `show segment-routing ipv6 sid-database` : Inspecte l'ensemble des SIDs SRv6 locaux et distants appris via l'IGP.

* `traceroute sr-mpls` / `traceroute ipv6 [Adresse] routing-header` : Permet de diagnostiquer le saut exact où un segment SRv6 est altéré.

### 3.2. Sécurisation critique de l'Infrastructure IPv6

À l'échelle opérateur, la protection du plan de contrôle et du plan de données IPv6 exige le déploiement rigoureux de contre-mesures avancées :

* **Infrastructure ACLs (iACLs) :** Bloquer les paquets IPv6 externes destinés aux adresses d'infrastructure (Locators SRv6, adresses P2P d'interconnexion de cœur).

* **Filtrage des En-têtes d'Extension IPv6 (RFC 9098) :** Configurer les équipements de bordure de l'AS pour supprimer les paquets IPv6 contenant des en-têtes d'extension non autorisés (ex: Routing Header Type 0 qui permet des attaques par rebond), tout en conservant le type 4 (SRH) strictement à l'intérieur de votre domaine de confiance administrative.

```cisco
! Filtrage rigoureux des En-têtes d'extension malveillants à la bordure de l'AS
ipv6 access-list BORDER_SECURITY_IN
 ! Rejet strict des anciens Type 0 Routing Headers
 deny ipv6 any any routing-type 0
 ! Autoriser SRH uniquement si la source appartient au domaine de confiance
 permit ipv6 2001:db8:infra::/48 any routing-type 4
 ! Rejet de tout SRH externe non sollicité
 deny ipv6 any any routing-type 4
 ! Autorisation du trafic standard
 permit ipv6 any any
exit

interface TenGigabitEthernet0/1/0
 description PEERING_EXTERNAL_IXP
 ipv6 traffic-filter BORDER_SECURITY_IN in
exit
```

> **Danger :** Ne laissez jamais fuiter un **Locator SRv6** ou des paquets transportant un en-tête **SRH** en dehors de votre Autonomous System (AS). Un attaquant externe capable de transmettre des paquets avec des SIDs SRv6 arbitraires vers votre réseau pourrait exécuter à distance des fonctions réseau internes (`End.DT4`/`End.DT6`), contournant l'intégralité de vos pare-feux et accédant directement à vos VRFs privées d'entreprise.

## Points à retenir

* **SRv6 (Segment Routing over IPv6) :** SRv6 utilise le plan de données IPv6 natif et des SIDs de 128 bits encodés dans l'en-tête d'extension SRH (Type 4) pour réaliser le routage par la source et les services VPN sans nécessiter de protocole de signalisation MPLS.

* **Sécurisation MP-BGP avec RPKI :** La validation de l'origine des routes (ROV) au moyen de certitificats RPKI/ROA protège les architectures IPv6 contre les détournements d'AS (*BGP Hijacking*) en classant les annonces en `Valid`, `Invalid` ou `NotFound`.

* **Isolation et Sécurité du Domaine SRv6 :** Les préfixes Locators SRv6 et le traitement des en-têtes SRH doivent rester strictement hermétiques au domaine d'administration de l'opérateur via des filtres iACLs et de bordure BGP.