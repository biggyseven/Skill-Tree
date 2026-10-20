# BGP Avancé – Route Reflector & Communautés  
*Cours intensif – Niveau Administrateur Réseau Senior (CCIE‑Ready)*  

---

## Table des matières  

| # | Section | Durée estimée |
|---|---------|----------------|
| 1 | Rappel rapide des bases BGP | 15 min |
| 2 | Architecture avancée BGP | 20 min |
| 3 | **Route Reflector (RR)** – concepts & design | 35 min |
| 4 | Configuration RR – Cisco IOS / IOS‑XR / NX‑OS | 30 min |
| 5 | RR – bonnes pratiques, limites et alternatives | 20 min |
| 6 | **Communautés BGP** – types & syntaxe | 30 min |
| 7 | Implémentation des politiques (route‑maps, policy‑statements) | 30 min |
| 8 | Interaction RR ↔ Communautés | 15 min |
| 9 | Sécurité & filtrage (BGP‑MD5, RPKI, BMP) | 20 min |
|10 | **Atelier de dépannage** – scénario complet | 45 min |
|11 | Résumé & points d’attention | 10 min |
|12 | Bibliographie & ressources | – |

> **Objectif** : À l’issue de ce cours, le participant doit être capable de concevoir, déployer, optimiser et dépanner un réseau BGP d’envergure incluant des Route Reflectors et des politiques basées sur les communautés, tout en respectant les exigences de scalabilité, de résilience et de sécurité.

---

## 1. Rappel rapide des bases BGP  

| Élément | Description | Valeur par défaut (Cisco) |
|---------|-------------|---------------------------|
| **AS_PATH** | Liste ordonnée des AS traversés | – |
| **NEXT_HOP** | Adresse IP du prochain saut BGP | Adresse de l’interface du voisin |
| **LOCAL_PREF** | Priorité interne (plus haut = préféré) | 100 |
| **MED** (Multi‑Exit Discriminator) | Influence la sortie d’un AS (plus bas = préféré) | 0 |
| **WEIGHT** (Cisco‑only) | Valeur locale au routeur (plus haut = préféré) | 0 |
| **ORIGIN** | IGP, EGP ou INCOMPLETE | IGP (i) |

> **Note** : Ces attributs sont la base du processus de sélection du meilleur chemin (BGP Decision Process). Le RR et les communautés viennent enrichir ce processus sans modifier la logique fondamentale.

---

## 2. Architecture avancée BGP  

### 2.1. Problématique de l’échelle  

| Problème | Impact si non résolu |
|----------|----------------------|
| **Full‑mesh iBGP** | O(N²) sessions → saturation du CPU/mémoire, temps de convergence élevé |
| **Loop‑prevention** | Risque de boucles de routage si les route‑reflectors ne sont pas correctement configurés |
| **Policy‑centralisation** | Gestion de filtres et de communautés dispersée → erreurs humaines |

### 2.2. Solutions classiques  

| Solution | Avantages | Inconvénients |
|----------|-----------|----------------|
| **Route Reflector (RR)** | Réduction du nombre de sessions, centralisation du contrôle | Risque de sous‑optimalité (path‑selection non‑déterministe) |
| **BGP Confederation** | Découpage logique, chaque sous‑AS a son propre iBGP full‑mesh | Complexité d’opération, besoin de re‑tagging AS_PATH |
| **BGP Large Communities** (RFC 8092) | 96‑bits, évite collisions, plus d’espace d’adressage | Nécessite support logiciel récent |
| **BGP Add‑Path** | Multiples chemins pour le même préfixe, améliore la redondance | Augmente la charge de la table de routage |

---

## 3. Route Reflector (RR) – Concepts & Design  

### 3.1. Définitions clés  

| Terme | Signification |
|-------|----------------|
| **Route Reflector (RR)** | Routeur BGP qui “réflète” les routes iBGP vers ses clients, éliminant le besoin de full‑mesh. |
| **RR‑Client** | Voisin iBGP configuré comme client du RR (via `route-reflector-client`). |
| **Non‑client (ou “peer”)** | Voisin iBGP qui n’est pas client ; échange les routes comme dans un full‑mesh classique. |
| **Cluster‑ID** | Identifiant unique (généralement l’IP Loopback du RR) qui empêche les boucles de réflexion. |

### 3.2. Algorithme de réflexion  

```
+-------------------+          +-------------------+
|   RR (Cluster‑ID) |---+----->|  RR‑Client A      |
+-------------------+   |      +-------------------+
        ^               |                ^
        |               |                |
        |   +-----------+                |
        |   |                            |
        v   v                            v
+-------------------+          +-------------------+
|   RR‑Client B     |<-------->|  RR‑Client C      |
+-------------------+          +-------------------+
```

1. **Reception** : RR reçoit une mise à jour d’un client ou d’un non‑client.  
2. **Reflection** :  
   - Si la mise à jour provient d’un **client**, le RR la reflète **à tous les autres clients** **et** aux **non‑clients** (mais pas à l’émetteur).  
   - Si la mise à jour provient d’un **non‑client**, le RR la reflète **uniquement aux clients**.  
3. **Cluster‑ID** est ajouté à l’attribut **Cluster‑List** ; si un RR voit son propre Cluster‑ID dans la liste, il **rejette** la route (prévention de boucle).

### 3.3. Topologies recommandées  

| Topologie | Description | Quand l’utiliser |
|-----------|-------------|------------------|
| **RR‑Hierarchical** | Plusieurs niveaux (RR‑Tier‑1, RR‑Tier‑2) – chaque niveau possède ses propres clients | Grand réseau avec plusieurs zones géographiques, besoin de résilience locale |
| **RR‑Redundant (dual‑RR)** | Deux RR dans le même cluster (Cluster‑ID identique) – chaque RR a ses propres clients | Haute disponibilité, élimination du point unique de défaillance |
| **RR‑Mixed (RR + Confederation)** | RR pour la plupart du trafic, confédération pour les sous‑domains très isolés | Environnements hybrides, migration progressive |

#### ASCII – Topologie RR‑Hierarchical (3‑tiers)

```
                     +-------------------+
                     |   RR Tier‑1 (C1)  |
                     +--------+----------+
                              |
        +---------------------+---------------------+
        |                                           |
+-------+-------+                           +-------+-------+
| RR Tier‑2 A   |                           | RR Tier‑2 B   |
+-------+-------+                           +-------+-------+
        |                                           |
  +-----+-----+                               +-----+-----+
  | Clients A |                               | Clients B |
  +-----------+                               +-----------+
```

- **C1** = Cluster‑ID partagé entre les deux RR Tier‑2 (redondance).  
- Chaque client n’a qu’une session iBGP vers son RR local → **O(N)** sessions au lieu de **O(N²)**.

### 3.4. Calcul du nombre de sessions  

| Nombre de routeurs (N) | Full‑mesh iBGP | RR (single‑RR) | RR (dual‑RR) |
|------------------------|----------------|----------------|-------------|
| 10                     | 45             | 9 (1+9)        | 18 (2+16)   |
| 50                     | 1 225          | 49 (1+49)      | 98 (2+96)   |
| 200                    | 19 900         | 199 (1+199)    | 398 (2+396) |

> **Formule** : Full‑mesh = N·(N‑1)/2 ; RR‑single = N‑1 + 1 (RR) ; RR‑dual = 2·(N‑1) + 2 (RRs).  

---

## 4. Configuration RR – Cisco IOS / IOS‑XR / NX‑OS  

### 4.1. IOS (Classic) – Exemple complet  

```text
! -------------------------------------------------
! 1️⃣ Création d’un Loopback qui servira de Router ID
! -------------------------------------------------
interface Loopback0
 ip address 10.0.0.1 255.255.255.255
!
router bgp 65000
 bgp router-id 10.0.0.1
 bgp log-neighbor-changes
!
! -------------------------------------------------
! 2️⃣ Définition du RR (cluster-id = Loopback0)
! -------------------------------------------------
 bgp cluster-id 10.0.0.1
!
! -------------------------------------------------
! 3️⃣ Configuration des clients
! -------------------------------------------------
 neighbor 192.0.2.2 remote-as 65000
 neighbor 192.0.2.2 update-source Loopback0
 neighbor 192.0.2.2 route-reflector-client
!
 neighbor 192.0.2.3 remote-as 65000
 neighbor 192.0.2.3 update-source Loopback0
 neighbor 192.0.2.3 route-reflector-client
!
! -------------------------------------------------
! 4️⃣ Configuration d’un non‑client (peering full‑mesh)
! -------------------------------------------------
 neighbor 192.0.2.10 remote-as 65000
 neighbor 192.0.2.10 update-source Loopback0
!
! -------------------------------------------------
! 5️⃣ Politique d’entrée (exemple : accepter uniquement les routes du client A)
! -------------------------------------------------
ip prefix-list CLIENT_A seq 5 permit 203.0.113.0/24 le 24
!
route-map CLIENT_A_IN permit 10
 match ip address prefix-list CLIENT_A
 set local-preference 200
!
router bgp 65000
 neighbor 192.0.2.2 route-map CLIENT_A_IN in
!
! -------------------------------------------------
! 6️⃣ Vérifications
! -------------------------------------------------
do show ip bgp summary
do show ip bgp neighbors 192.0.2.2 advertised-routes
do show ip bgp neighbors 192.0.2.2 routes
```

### 4.2. IOS‑XR – Exemple (RR redondant)  

```text
router bgp 65000
 bgp router-id 10.0.0.1
 bgp log-neighbor-changes
 bgp cluster-id 10.0.0.1
 !
 address-family ipv4 unicast
  neighbor 192.0.2.2
   remote-as 65000
   update-source Loopback0
   route-reflector-client
   address-family ipv4 unicast
  neighbor 192.0.2.3
   remote-as 65000
   update-source Loopback0
   route-reflector-client
   address-family ipv4 unicast
  neighbor 192.0.2.10
   remote-as 65000
   update-source Loopback0
   address-family ipv4 unicast
 !
```

### 4.3. NX‑OS – Exemple (RR + BGP‑EVPN)  

```text
router bgp 65000
  router-id 10.0.0.1
  address-family ipv4 unicast
    neighbor 192.0.2.2 remote-as 65000
    neighbor 192.0.2.2 update-source Loopback0
    neighbor 192.0.2.2 route-reflector-client
    neighbor 192.0.2.3 remote-as 65000
    neighbor 192.0.2.3 update-source Loopback0
    neighbor 192.0.2.3 route-reflector-client
    neighbor 192.0.2.10 remote-as 65000
    neighbor 192.0.2.10 update-source Loopback0
  exit-address-family
  bgp cluster-id 10.0.0.1
!
```

### 4.4. Vérifications rapides (IOS/NX‑OS)  

| Commande | Objectif |
|----------|----------|
| `show ip bgp summary` | État des sessions BGP (Uptime, BGP‑state) |
| `show ip bgp neighbors <IP> advertised-routes` | Routes que le RR envoie au voisin |
| `show ip bgp neighbors <IP> received-routes` | Routes reçues du voisin |
| `show ip bgp` | Table BGP complète (attribues, path) |
| `show ip bgp regexp <regex>` | Recherche de routes contenant un attribut (ex. `^65000` ) |
| `show bgp vpnv4 unicast all` | BGP‑VPN (utile en EVPN) |
| `show running-config | include route-reflector-client` | Vérifier la configuration client |

---

## 5. RR – Bonnes pratiques, limites et alternatives  

| Bonnes pratiques | Pourquoi |
|------------------|----------|
| **Utiliser un Loopback comme source** (`update-source Loopback0`) | Stabilité du peering, même si l’interface physique tombe |
| **Attribuer un Cluster‑ID unique par groupe de RR** | Évite les boucles inter‑clusters |
| **Déployer au minimum 2 RR par cluster (dual‑RR)** | Redondance sans perte de réflexion |
| **Séparer les clients de type “leaf” et “spine”** | Contrôle granulaire du Local‑Pref et du MED |
| **Appliquer des filtres d’entrée (prefix‑list, route‑map)** | Limite les routes indésirables, prévient le “route‑flap” |
| **Activer le BGP Graceful‑Restart** | Convergence plus rapide après redémarrage du RR |
| **Surveiller le nombre de routes reflétées** (`show ip bgp | inc ^ *`) | Détecte les “route‑leaks” ou les boucles |

### 5.1. Limites du RR  

| Limite | Conséquence | Mitigation |
|--------|-------------|------------|
| **Non‑déterminisme du meilleur chemin** (les clients peuvent choisir différents chemins) | Sous‑optimalité du trafic | Utiliser **Local‑Pref** ou **MED** uniformes, ou introduire **BGP Add‑Path** |
| **Propagation de routes non‑optimales** (ex. routes avec AS‑PATH plus long) | Augmentation du coût de transit | Filtrage strict des AS‑PATH, utilisation de **AS‑PATH prepend** côté client |
| **Scalabilité du RR** (table de routage massive) | Consommation CPU/MEM | Partitionner en plusieurs clusters, activer **BGP route‑refresh** pour limiter les mises à jour inutiles |
| **Boucles de réflexion** (Cluster‑List mal configuré) | Perte de routes | Vérifier `show ip bgp neighbors <IP> received-routes` pour la présence du propre Cluster‑ID |

### 5.2. Alternatives / Compléments  

| Solution | Cas d’usage | Points forts |
|----------|-------------|--------------|
| **BGP Confederation** | Réseaux très grands avec besoin d’isolation administrative | Full‑mesh interne à chaque sous‑AS, AS‑PATH reste court |
| **BGP Add‑Path** | Besoin de plusieurs chemins pour le même préfixe (ex. multi‑homing) | Améliore la résilience, évite la perte de connectivité lors d’un fail‑over |
| **BGP EVPN** (Overlay) | Data‑center, L2VPN + L3VPN, besoin de MAC learning via BGP | Séparation du contrôle (BGP) et du transport (VXLAN) |
| **BGP PIC (Prefix‑Independent Convergence)** | Réduction du temps de convergence dans les grands iBGP | Implémenté sur IOS‑XR, NX‑OS, Junos |

---

## 6. Communautés BGP – Types & Syntaxe  

### 6.1. Rappel de la syntaxe standard  

- **Standard Community** : 32 bits, format `AA:NN` (AS : value)  
  - Exemple : `65000:100` (définit un attribut de politique)  

| Valeur (AA) | Signification (RFC 1997) |
|-------------|--------------------------|
| `no-export` (0:0) | Ne pas annoncer à eBGP |
| `no-advertise` (0:65535) | Ne pas annoncer du tout |
| `local-AS` (65535:AS) | Propagation uniquement à l’intérieur du même AS |

- **Extended Community** : 64 bits, format `type:subtype:value` (ex. `rt:65000:100` pour route‑target)  
- **Large Community** : 96 bits, format `AAA:BBB:CCC` (RFC 8092) – évite les collisions et facilite le filtrage multi‑tenant.

### 6.2