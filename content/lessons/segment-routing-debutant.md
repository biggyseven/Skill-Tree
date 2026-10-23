# Segment Routing (SR-MPLS et SRv6) - Débutant

**Niveau :** Débutant

Dans les réseaux IP/MPLS traditionnels d'opérateurs et de grandes entreprises, l'acheminement des paquets repose sur une combinaison complexe de protocoles. Pour acheminer le trafic de manière optimale, un réseau classique doit faire fonctionner un protocole de routage sous-jacent (IGP comme OSPF ou IS-IS), doublé d'un protocole de distribution d'étiquettes MPLS (LDP - *Label Distribution Protocol*) ou d'un protocole d'ingénierie de trafic exigeant (RSVP-TE - *Resource Reservation Protocol - Traffic Engineering*). 

Bien que très efficaces, ces architectures traditionnelles souffrent d'une grande complexité opérationnelle. LDP et RSVP-TE nécessitent la maintenance d'états d'invalidation et de sessions de signalisation sur **chaque routeur intermédiaire** du réseau (*Stateful Network*). Dans un réseau comptant des milliers de nœuds, maintenir ces états de signalisation devient un véritable casse-tête d'évolutivité (scalabilité), de convergence et de dépannage.

Le **Segment Routing (SR)** a été inventé par l'IETF pour résoudre fondamentalement cette complexité. Le principe clé du Segment Routing est le **Source Routing** (routage à la source) : c'est le nœud d'entrée du réseau (le routeur Ingress) qui définit l'intégralité du chemin que doit emprunter un paquet, puis enserre cette instruction directement dans l'en-tête du paquet sous la forme d'une liste ordonnée d'instructions appelées **Segments**. 

Grâce au Segment Routing, les routeurs intermédiaires du cœur de réseau (*Transit Nodes*) n'ont plus besoin de maintenir le moindre état de session pour chaque flux ou tunnel. Ils se contentent de lire l'instruction du segment courant, d'exécuter l'action associée et d'acheminer le paquet vers le segment suivant. Le réseau redevient **Stateless** (sans état intermédiaire), ce qui simplifie radicalement les opérations, améliore la rapidité de convergence à moins de 50 millisecondes et s'intègre naturellement avec les contrôleurs logiciels SDN (*Software-Defined Networking*).

Le Segment Routing s'appuie sur deux architectures de plan de données (*Data Plane*) principales :
1. **SR-MPLS** : Réutilise l'en-tête et les étiquettes MPLS de 20 bits existants.
2. **SRv6** : Utilise les adresses IPv6 natives de 128 bits et l'en-tête d'extension IPv6 (*Segment Routing Header* - SRH).

> **Analogie** : Imaginez un voyage en avion avec plusieurs escales : Paris $\rightarrow$ Francfort $\rightarrow$ Dubaï $\rightarrow$ Tokyo.
>
> **Dans le modèle traditionnel (LDP / RSVP-TE)** : À chaque fois que vous arrivez dans un aéroport intermédiaire, vous devez vous enregistrer auprès d'un guichet local (session LDP/RSVP). Le guichet vérifie une base de données locale pour savoir où vous envoyer ensuite et vous donne un nouveau ticket de transit local. Chaque aéroport doit maintenir un registre actif de tous les passagers en transit.
>
> **Dans le modèle Segment Routing (Source Routing)** : Avant votre départ de Paris (routeur Ingress), la compagnie aérienne vous remet un carnet d'embarquement complet contenant une pile de tickets : `[Ticket 1: Francfort, Ticket 2: Dubaï, Ticket 3: Tokyo]`. Les agents dans les aéroports de transit (routeurs de cœur) n'ont pas besoin de vous enregistrer dans un système complexe : ils regardent simplement le ticket au sommet de votre pile, vous dirigent vers la porte d'embarquement correspondante, et détachent le ticket utilisé (*Pop*). Les aéroports intermédiaires n'ont plus aucun registre à maintenir !

## 1. La théorie et les principes fondamentaux

### 1. La notion de Segment et Identifiants (SID - Segment Identifier)

Dans l'architecture Segment Routing, un **Segment** représente une instruction élémentaire de transfert ou de traitement réseau. Chaque segment est identifié de manière unique par une valeur appelée **SID (*Segment Identifier*)**.

Selon le plan de données utilisé :
* En **SR-MPLS**, un SID est représenté par une **étiquette MPLS** (valeur entière sur 20 bits, ex: `16001`).
* En **SRv6**, un SID est représenté sous la forme d'une **adresse IPv6** de 128 bits (ex: `2001:db8:1:1::1`).

Les segments sont distribués directement par les extensions des protocoles de routage internes (**IGP**) existants (OSPFv3 ou IS-IS), éliminant définitivement le besoin de déployer le protocole LDP ou RSVP-TE !

```
+-----------------------------------------------------------------------+
|                   PLANS DE DONNÉES SEGMENT ROUTING                    |
+-----------------------------------┬-----------------------------------+
                                    |
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
+-----------------------+                       +-----------------------+
|        SR-MPLS        |                       |         SRv6          |
|  (Data Plane MPLS)    |                       |  (Data Plane IPv6)    |
| - Réutilise en-tête   |                       | - Réutilise adresses  |
|   MPLS classique      |                       |   IPv6 (128-bit)      |
| - SID = Label MPLS    |                       | - Extension Header    |
|   (ex: 16001)         |                       |   (SRH - Type 4)      |
+-----------------------+                       +-----------------------+
```

### 2. Les principaux types de Segments IGP

On distingue deux types de segments fondamentaux générés par l'IGP dans un réseau Segment Routing :

1. **Node SID (ou Prefix SID)** :
   * Identifie un nœud/routeur spécifique de manière globale dans tout le domaine réseau (souvent rattaché à son adresse de Loopback).
   * **Portée (Scope)** : **Globale**. La valeur du Prefix SID est unique et connue de tous les routeurs du domaine.
   * **Comportement** : Le paquet est acheminé vers ce nœud en suivant le chemin le plus court calculé par l'IGP (ECMP - *Equal-Cost Multi-Path* supporté).

2. **Adjacency SID (Adj-SID)** :
   * Identifie une liaison/interface physique spécifique entre deux routeurs adjacents.
   * **Portée (Scope)** : **Locale**. Il est attribué dynamiquement par le routeur local pour désigner une adjacence précise.
   * **Comportement** : Forcer le paquet à emprunter cette liaison spécifique, indépendamment du métrique ou du chemin le plus court IGP.

```
       [ Node SID: 16001 ]                   [ Node SID: 16002 ]
         +--------------+                      +--------------+
         |  Routeur A   |======================|  Routeur B   |
         +--------------+   Adj-SID: 24001     +--------------+
```

### 3. La structure globale des étiquettes : SRGB et SRLB

Pour éviter les conflits d'étiquettes dans SR-MPLS, la plage d'étiquettes est structurée en deux blocs :

* **SRGB (*Segment Routing Global Block*)** : Plage d'étiquettes réservée à l'échelle globale pour les Prefix/Node SIDs (par défaut souvent de `16000` à `23999`). Chaque routeur calcule l'étiquette MPLS finale en additionnant son *Index* à la base SRGB :

$$\text{Label MPLS} = \text{SRGB}_{\text{base}} + \text{Prefix-Index}$$

* **SRLB (*Segment Routing Local Block*)** : Plage d'étiquettes réservée à l'attribution locale pour les Adjacency SIDs (par défaut généralement au-delà de `150000`).

### 4. Mécanisme de Protection Instantanée : TI-LFA (Topology-Independent Loop-Free Alternate)

L'un des avantages majeurs du Segment Routing est sa capacité à offrir une protection absolue contre les pannes de lien ou de nœud en moins de 50 millisecondes grâce au mécanisme **TI-LFA**.

Contrairement au LFA traditionnel qui échouait dans certaines topologies complexes (non-couverture à 100%), TI-LFA garantit une couverture de protection à **100%** sur n'importe quelle topologie réseau :
1. L'IGP calcule à l'avance (en temps de paix) le chemin de secours le plus court en excluant le lien protégé.
2. Si ce chemin de secours nécessite d'emprunter des nœuds non-naturels, le routeur calcule la liste exacte de segments (Node/Adj SIDs) à empiler pour contourner la panne sans créer de boucle de routage (*Loop-Free*).
3. Lors de la rupture du lien, le routeur bascule le trafic sur ce chemin de secours encapsulé en quelques millisecondes, directement au niveau du matériel (*Hardware ASIC*).

> **Piège :** Une erreur fréquente chez les débutants est de penser que le Segment Routing nécessite obligatoirement la mise en place d'un contrôleur SDN centralisé. C'est faux ! Le Segment Routing de base (Node SID, Adj-SID, TI-LFA) fonctionne de manière totalement autonome grâce aux extensions IGP (OSPF/IS-IS) sur chaque routeur. Le contrôleur SDN devient utile uniquement pour l'ingénierie de trafic avancée inter-domaines (*SR TE Policy*).

---

## 2. Configuration et Pratique

Dans les déploiements d'entreprise et d'opérateurs, la configuration de **SR-MPLS** s'effectue directement au sein du protocole d'IGP (ex: IS-IS ou OSPFv2/v3).

Voici une configuration de référence d'un routeur de cœur de réseau sous Cisco IOS-XE (ex: ASR 1000 ou ISR 4000) activant SR-MPLS avec **OSPFv2** et la protection **TI-LFA**.

```
! =====================================================================
! SECTION 1 : ACTIVATION DU SEGMENT ROUTING MPLS ET DEFINITION DU SRGB
! =====================================================================
segment-routing mpls
 !
 ! Définition du bloc global d'étiquettes (SRGB)
 global-block 16000 23999
 !
 connected-prefix-sid-map
  address-family ipv4
   ! Attribution d'un Prefix-Index fixe (1) sur la Loopback0 (10.0.0.1)
   ! Label MPLS calculé = 16000 + 1 = 16001
   10.0.0.1/32 index 1 range 1
  exit-address-family
 !
exit

! =====================================================================
! SECTION 2 : CONFIGURATION DES INTERFACES ET ROUTEUR OSPF
! =====================================================================
interface Loopback0
 ip address 10.0.0.1 255.255.255.255
 ip ospf 1 area 0
!

interface GigabitEthernet1
 description *** Liaison Core vers Routeur B ***
 ip address 192.168.12.1 255.255.255.252
 mpls ip
 ip ospf 1 area 0
 ! Activation de la protection rapide TI-LFA sur l'interface
 ip ospf fast-reroute per-prefix ti-lfa
!

! =====================================================================
! SECTION 3 : INTEGRATION DU SEGMENT ROUTING DANS IGP (OSPF)
! =====================================================================
router ospf 1
 router-id 10.0.0.1
 ! Activation des extensions Segment Routing dans OSPF
 segment-routing mpls
 segment-routing area 0
 ! Activation globale du calcul Fast-Reroute TI-LFA
 fast-reroute per-prefix priority high ti-lfa
!
```

> **Astuce :** Pour vérifier rapidement sous Cisco IOS-XE si le Segment Routing a correctement alloué les étiquettes globales et locales, utilisez la commande :
> `show mpls forwarding-table` ou `show segment-routing mpls connected-prefix-sid-map`.

---

## 3. Dépannage et Sécurité

### 1. Méthodologie et Commandes de Diagnostic

Le dépannage d'un réseau Segment Routing s'articule autour de la vérification de la base de données IGP et de la table de transfert MPLS (*LFIB*) :

1. **Validation de l'allocation des SIDs dans l'IGP** :
   S'assurer que l'IGP propage bien les sous-blocks TLV Segment Routing :
   ```bash
   show ip ospf segment-routing sid-database
   ```

2. **Inspection de la table de transfert MPLS (LFIB)** :
   Vérifier l'association entre les étiquettes et les instructions d'action (*Pop*, *Swap*, *Push*) :
   ```bash
   show mpls forwarding-table
   ```
   *Exemple d'affichage attendu :*
   `Local Label: 16002 | Outgoing Label: Pop Label | Prefix: 10.0.0.2/32 | Next-Hop: 192.168.12.2`

3. **Validation du calcul de secours TI-LFA** :
   Vérifier que le chemin de protection précalculé est prêt en cas de coupure de lien :
   ```bash
   show ip ospf fast-reroute ti-lfa summary
   ```

### 2. Considérations de Sécurité

* **Protection des frontières du domaine (SRGB Filtering)** : Les étiquettes SRGB ne doivent pas pouvoir être injectées depuis un réseau externe non maîtrisé. Il convient de configurer un filtrage MPLS/IPv6 rigoureux aux frontières d'administration du réseau (*Edge Routers*).
* **Sécurisation de l'IGP** : Le Segment Routing reposant entièrement sur OSPF ou IS-IS, l'authentification des messages IGP (via HMAC-SHA256) est indispensable pour empêcher un attaquant d'injecter de faux Node-SIDs ou de détourner le trafic.

> **Danger :** En cas d'incohérence dans la configuration de la plage **SRGB** entre les différents routeurs d'un même domaine (ex: Routeur A configuré avec `16000-23999` et Routeur B avec `20000-30000`), le calcul de conversion Index $\rightarrow$ Label devient incorrect. Cela peut entraîner un trou noir de routage (*Blackholing*) ou une boucle de paquets non détectée par l'IGP.

---

## Points à retenir

* **Source Routing & Stateless Core** : Le Segment Routing place les instructions de guidage (*SIDs*) à la source du paquet. Les routeurs du cœur de réseau n'ont plus à maintenir d'états de signalisation (suppression de LDP et RSVP-TE).
* **SIDs principaux** : 
  * **Node SID (Prefix SID)** : Portée globale, identifie un nœud via le chemin le plus court IGP.
  * **Adj-SID (Adjacency SID)** : Portée locale, identifie une liaison physique spécifique.
* **Plans de données (Data Planes)** : SR-MPLS (réutilise les étiquettes MPLS) et SRv6 (réutilise les adresses IPv6 et le Segment Routing Header - SRH).
* **TI-LFA (Topology-Independent Loop-Free Alternate)** : Offre une protection sub-50ms garantie à 100% contre les pannes sur n'importe quelle topologie réseau.