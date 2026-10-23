# MPLS & VRF - Débutant

> **Note** : Ce cours est en cours de rédaction. Utilisez Gemini pour générer le contenu complet !## node_id: mpls-debutant

title: MPLS et VRF - Débutant

# MPLS (Multiprotocol Label Switching) et VRF - Débutant

**Niveau :** Débutant  
**Prérequis :** Notions de base en routage IP (IPv4, tables de routage, IGP comme OSPF ou IS-IS) et concepts VLAN (802.1Q).

Ce cours introduit les concepts fondamentaux du **MPLS (Multiprotocol Label Switching)** et des **VRF (Virtual Routing and Forwarding)**. Nous verrons pourquoi ces technologies ont été créées, comment elles fonctionnent au niveau du plan de données (*Data Plane*) et du plan de contrôle (*Control Plane*), ainsi que les bases de la commutation par étiquettes (*Labels*).

---

## 1. Pourquoi MPLS et VRF ?

### Le problème du routage IP traditionnel

Dans le routage IP classique :
1. Chaque routeur le long du chemin consulte la **table de routage (FIB/RIB)** pour déterminer le saut suivant (*Next-Hop*).
2. La recherche s'effectue sur le masque de sous-réseau le plus long (*Longest Prefix Match* - LPM), ce qui demande un calcul à chaque saut.
3. Toutes les paquets d'une même destination empruntent exactement le même chemin défini par l'IGP.
4. Par défaut, la table de routage est unique : deux clients ou services ayant les mêmes sous-réseaux privés (ex: `192.168.1.0/24`) ne peuvent pas coexister sur les mêmes équipements sans conflit d'adressage IP.

### Les solutions apportées

* **VRF (Virtual Routing and Forwarding) :** Permet de partitionner un routeur physique en plusieurs tables de routage virtuelles indépendantes (analogue aux VLANs pour la couche 2).
* **MPLS (Multiprotocol Label Switching) :** Permet d'acheminer les paquets IP en leur ajoutant une petite étiquette (*Label*) de taille fixe. Les routeurs de transit commutent les paquets en regardant uniquement cette étiquette, sans analyser l'en-tête IP.

---

## 2. Le concept de VRF (Virtual Routing and Forwarding)

Une VRF permet de créer plusieurs instances de routage étanches sur un même équipement.

```
                  ┌─────────────────────────────────┐
                  │        ROUTEUR PHYSIQUE         │
                  │                                 │
                  │  ┌───────────┐   ┌───────────┐  │
Client A (VLAN10) ┼──┤  VRF A    │   │  VRF B    ├──┼ Client B (VLAN20)
10.0.0.0/24       │  │ (Table A) │   │ (Table B) │  │ 10.0.0.0/24
                  │  └───────────┘   └───────────┘  │
                  └─────────────────────────────────┘
```

### Caractéristiques principales d'une VRF :
1. **Table de routage dédiée :** Chaque VRF possède sa propre table IP (`show ip route vrf <nom>`).
2. **Isolation totale :** Les paquets appartenant à la VRF A ne peuvent pas communiquer avec la VRF B par défaut.
3. **Plages d'adresses overlapping :** Plusieurs clients peuvent utiliser le même espace d'adressage IP privé (ex: RFC 1918) sans interférence.
4. **Interfaces dédiées :** Une interface physique ou sous-interface (VLAN) est assignée à une seule VRF à la fois.

---

## 3. Les Fondations du MPLS

### 1. La structure de l'en-tête MPLS (Shim Header)

L'en-tête MPLS (4 octets / 32 bits) s'intercale entre la couche 2 (Ethernet) et la couche 3 (IP), d'où son appellation de protocole **Couche 2.5**.

```
 0                   1          2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                LABEL (20 bits)                | Exp |S|  TTL  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

* **Label (20 bits) :** Valeur numérique de l'étiquette (de 0 à $2^{20}-1 = 1\,048\,575$). Identifie la classe d'équivalence de transfert (FEC).
* **Experimental / TC (3 bits) :** Utilisé pour la QoS (Quality of Service / DiffServ).
* **Bottom of Stack - S (1 bit) :** Indique si cette étiquette est la dernière de la pile ($S=1$) ou s'il y en a d'autres empilées en dessous ($S=0$).
* **Time To Live - TTL (8 bits) :** Évite les boucles de routage (décrémenté à chaque saut MPLS).

---

### 2. Typologie des Routeurs MPLS

Dans une architecture MPLS, on distingue trois rôles majeurs :

```
[ Client A ] ─── ( CE1 ) ─── [ LER / PE1 ] ─── [ LSR / P ] ─── [ LER / PE2 ] ─── ( CE2 ) ─── [ Client B ]
                               (Ingress)                       (Egress)
```

1. **CE (Customer Edge) :** Routeur situé chez le client. Il n'a pas conscience du réseau MPLS et émet/reçoit des paquets IP standards.
2. **PE (Provider Edge) ou LER (Label Edge Router) :** Routeur de bordure du fournisseur de services. Il fait le pont entre le routage IP classique et le domaine MPLS.
   * **Ingress LER :** Ajoute l'étiquette MPLS au paquet IP entrant (*Push*).
   * **Egress LER :** Retire l'étiquette MPLS avant d'envoyer le paquet IP au destinataire final (*Pop*).
3. **P (Provider Router) ou LSR (Label Switching Router) :** Routeur de cœur de réseau (*Core Router*). Il ne regarde que les étiquettes MPLS pour commuter le trafic (*Swap*).

---

### 3. Les Opérations MPLS sur le Plan de Données

Un routeur MPLS effectue trois opérations fondamentales sur la pile d'étiquettes :

* **PUSH :** Ajout d'une nouvelle étiquette au sommet de la pile (ex-Ingress PE).
* **SWAP :** Remplacement de l'étiquette entrante par une étiquette sortante (ex-routeur P de transit).
* **POP :** Suppression de l'étiquette supérieure de la pile (ex-Egress PE).

```
        PUSH (Label 100)               SWAP (100 -> 200)             POP (Label 200)
IP Packet  ─────────>  [ LER Ingress ]  ─────────>  [ LSR Core ]  ─────────>  [ LER Egress ]  ─────────> IP Packet
                       [100|IP Header]              [200|IP Header]               [IP Header]
```

---

## 4. Protocole d'Échange d'Étiquettes : LDP (Label Distribution Protocol)

Pour que la commutation d'étiquettes fonctionne, les routeurs doivent s'accorder sur les étiquettes à utiliser pour chaque destination IP. Le protocole standard utilisé est **LDP (RFC 5036)**.

### Fonctionnement de LDP :
1. **Découverte des voisins :** Les routeurs s'envoient des messages Hello UDP sur le port `646`.
2. **Session TCP :** Une session TCP (port `646`) est établie entre les voisins LDP.
3. **Attribution et Annonce des Labels :**
   * Chaque routeur attribue une étiquette locale (*Local Label*) à chaque préfixe IP connu dans son IGP (OSPF/IS-IS).
   * Il informe ses voisins de l'association *(Préfixe IP $\rightarrow$ Label Local)* via des messages LDP *Mapping*.
4. **Construction des tables MPLS :**
   * **LIB (Label Information Base) :** Contient toutes les associations d'étiquettes reçues de tous les voisins LDP.
   * **LFIB (Label Forwarding Information Base) :** Contient les meilleures étiquettes retenues pour la commutation effective du plan de données.

---

## 5. Configuration de Base : VRF et MPLS LDP (Cisco IOS)

### 1. Configuration d'une VRF simple

```cisco
! Définition de la VRF pour le Client Alpha
vrf definition CLIENT_ALPHA
 address-family ipv4
 exit-address-family
!
! Assignation d'une interface à la VRF
interface GigabitEthernet0/1
 vrf forwarding CLIENT_ALPHA
 ip address 10.1.1.1 255.255.255.0
 no shutdown
```

### 2. Activation de MPLS LDP sur les interfaces de Cœur

```cisco
! 1. Identifier le routeur avec un ID LDP (souvent la Loopback0)
mpls router-id Loopback0 force

! 2. Activer MPLS globalement et sur l'interface du cœur
mpls ip

interface GigabitEthernet0/0
 description Lien vers Routeur P (Core)
 ip address 172.16.12.1 255.255.255.252
 mpls ip
!
```

---

## 6. Commandes de Vérification Essentielles

| Commande (Cisco IOS) | Description / Objectif |
| --- | --- |
| `show vrf` | Liste les VRFs configurées et leurs interfaces associées. |
| `show ip route vrf <NOM>` | Affiche la table de routage spécifique d'une VRF. |
| `show mpls ldp neighbor` | Vérifie l'état de la session LDP avec les routeurs voisins. |
| `show mpls ldp bindings` | Affiche la table **LIB** (associations préfixes/labels reçus). |
| `show mpls forwarding-table` | Affiche la table **LFIB** utilisée pour le transfert des paquets MPLS. |

---

## Points à retenir

* **VRF** isole les tables de routage IP au niveau du plan de contrôle et du plan de données sur un même routeur.
* **MPLS** ajoute un en-tête de 32 bits (Couche 2.5) contenant un **Label de 20 bits** pour accélérer et flexibiliser l'acheminement des paquets.
* **Ingress PE** applique une opération **Push**, les routeurs **P** effectuent un **Swap**, et le **Egress PE** effectue un **Pop**.
* **LDP (Label Distribution Protocol)** est le protocole du plan de contrôle utilisé pour associer et distribuer des étiquettes MPLS aux préfixes IP appris via l'IGP.