# Cours intensif – EIGRP (Enhanced Interior Gateway Routing Protocol)  
**Niveau : Administrateur Réseau Senior (CCIE)**  

---

## Table des matières  

| # | Section | Description |
|---|---------|-------------|
| 1 | Introduction & Historique | Origine, position dans le modèle OSI, licences |
| 2 | Architecture générale | Modules, processus, tables internes |
| 3 | Algorithme DUAL | Calcul de routes, états, boucle‑free |
| 4 | Métrique & formule | Bandwidth, delay, reliability, load, MTU |
| 5 | Topologie & tables internes | Topology Table, Routing Table, Neighbor Table |
| 6 | Configuration de base (Cisco IOS) | Commands, verification, bonnes pratiques |
| 7 | Fonctionnalités avancées | Stub, variance, summarisation, route‑maps, redistribution |
| 8 | EIGRP Named Mode & IPv6 | Syntaxe, avantages, migration |
| 9 | Sécurité & Authentification | MD5, key‑chains, ACLs |
|10| Comparaison avec OSPF, IS‑IS, BGP, RIP | Tableau comparatif détaillé |
|11| Déploiement sur Linux (FRR/Quagga) | Packages, configuration, interopérabilité |
|12| Optimisation & tuning | Timers, throttling, load‑balancing |
|13| Atelier de dépannage (Lab) | Scénario complet, étapes de diagnostic, solutions |
|14| Annexes | Glossaire, références, exercices supplémentaires |

---

## 1. Introduction & Historique  

- **EIGRP** a été introduit par Cisco en 1993 comme une évolution propriétaire de **IGRP** (Interior Gateway Routing Protocol).  
- En 2013, Cisco a publié **RFC 7868** – *EIGRP – A Cisco Proprietary Routing Protocol* – le rendant **ouvert** et **documenté**.  
- **Modèle OSI** : fonctionne au **niveau 3 (Network)**, mais interagit avec le **niveau 2** (liaison) via le protocole de voisinage (EIGRP Hello).  
- **Licence** : disponible sur IOS, IOS‑XE, IOS‑XR, NX‑OS, et sur les implémentations open‑source (FRR/Quagga).  

---

## 2. Architecture générale  

```
+-------------------+        +-------------------+        +-------------------+
|   EIGRP Process   | <----> |   Neighbor Table  | <----> |   Interface List  |
|   (PID 100)       |        +-------------------+        +-------------------+
|   - DUAL Engine   |        |   (Adjacency)     |        |   (IP, MAC)       |
|   - Topology Table|        +-------------------+        +-------------------+
|   - Routing Table|                ^                         ^
+-------------------+                |                         |
        ^                            |                         |
        |   +------------------------+-------------------------+
        |   |   EIGRP Packets (Multicast 224.0.0.10)        |
        +---+-----------------------------------------------+
```

- **Process ID (PID)** : identifiant logique, permet plusieurs instances EIGRP sur le même routeur.  
- **Tables internes**  
  - **Neighbor Table** – stocke les adjacences (IP, Interface, Hold‑time, Uptime).  
  - **Topology Table** – chaque destination possède un *Successor* (meilleure) et *Feasible Successors* (alternatives).  
  - **Routing Table** – les routes sélectionnées (Successor) sont injectées dans la RIB (Routing Information Base).  

---

## 3. Algorithme DUAL (Diffusing Update Algorithm)

### 3.1 Principes fondamentaux  

| Concept | Description |
|---------|-------------|
| **Successor** | Route avec le **lowest feasible distance** (FD) – installée dans la RIB. |
| **Feasible Distance (FD)** | Cumul du **metric** du routeur vers la destination (distance locale). |
| **Reported Distance (RD)** | Métrique annoncée par le voisin vers la destination. |
| **Feasibility Condition (FC)** | Un routeur B est *feasible* pour la destination X si **RD_B < FD_A** (où A est le routeur évaluant). |
| **Feasible Successor (FS)** | Voisin qui satisfait la FC – candidate de secours sans recalcul complet. |
| **Diffusing Computation** | Si aucun FS n’existe, le routeur *diffuse* une requête (Query) à ses voisins, déclenchant un recalcul global. |

### 3.2 États DUAL (ASCII State Machine)

```
          +-------------------+
          |   Passive (P)     |
          +-------------------+
                ^   |
                |   v
          +-------------------+
          |   Active (A)      |
          +-------------------+
                ^   |
                |   v
          +-------------------+
          |   Query Sent (Q)  |
          +-------------------+
                ^   |
                |   v
          +-------------------+
          |   Reply Received  |
          +-------------------+
```

- **Passive** : aucune requête en cours, la route est stable.  
- **Active** : le routeur attend des réponses (Replies) à une Query.  
- **Query Sent** : la Query a été diffusée, le routeur attend les Replies.  

---

## 4. Métrique & Formule  

EIGRP utilise une **métrique composite** basée sur **bandwidth** et **delay** par défaut (K‑values configurables).  

### 4.1 Formule de base  

```
Metric = (K1 * Bandwidth + K2 * Bandwidth) / 256  +  (K3 * Delay) / 256
```

- **Bandwidth** : 10⁶ / bande passante (kbps) → valeur *inverse* (ex : 100 Mbps → 10,000).  
- **Delay** : somme des délais (µs) / 10 → valeur *directe* (ex : 10 µs → 1).  

### 4.2 K‑values (défaut)  

| K‑value | Utilisé ? | Signification |
|---------|-----------|---------------|
| K1      | 1         | Bandwidth (poids) |
| K2      | 0         | Bandwidth (additionnel) |
| K3      | 1         | Delay |
| K4      | 0         | Reliability |
| K5      | 0         | Load |

> **NOTE** : Modifier les K‑values nécessite que **tous** les routeurs de l’AS utilisent les mêmes valeurs, sinon la FC peut être violée → loops.

### 4.3 Exemple de calcul  

| Interface | Bandwidth (kbps) | Bandwidth‑Metric | Delay (µs) | Delay‑Metric | Métrique totale |
|-----------|------------------|------------------|------------|--------------|-----------------|
| Gi0/0     | 100 000          | 10 000           | 100        | 10           | (10 000 + 10) = 10 010 |
| Gi0/1     | 1 000            | 1 000 000        | 1 000      | 100          | 1 000 100 |

Le chemin via Gi0/0 sera choisi (métrique moindre).

---

## 5. Topologie & tables internes  

| Table | Contenu | Usage |
|-------|---------|-------|
| **Neighbor Table** (`show ip eigrp neighbors`) | IP, Interface, Uptime, Hold‑time, SRTT, Retransmit Count | Vérifier l’adjacence |
| **Topology Table** (`show ip eigrp topology`) | Destination, Successor, Feasible Successors, FD, RD, Metric | Décision de routage, analyse de boucle |
| **Routing Table** (`show ip route eigrp`) | Routes installées dans la RIB | Forwarding réel |
| **Interface Table** (`show ip eigrp interfaces`) | Interfaces actives, K‑values, timers | Contrôle du périmètre EIGRP |

---

## 6. Configuration de base (Cisco IOS)

### 6.1 Activation globale  

```text
router eigrp 100               ! PID = 100
  network 10.0.0.0 0.0.0.255   ! annonce le réseau /24
  no auto-summary             ! désactive le résumé automatique (classful)
```

### 6.2 Configuration d’interface (classique)  

```text
interface GigabitEthernet0/0
  ip address 10.0.0.1 255.255.255.0
  ip hello-interval eigrp 100 5   ! 5 s d’intervalle Hello
  ip hold-time eigrp 100 15       ! 15 s de hold‑time
  ip bandwidth-percent eigrp 100 30   ! 30 % de la bande passante pour EIGRP
```

### 6.3 Vérifications  

| Commande | Description |
|----------|-------------|
| `show ip protocols` | Résumé des processus de routage actifs |
| `show ip eigrp neighbors detail` | Détails du voisinage (SRTT, RTO) |
| `show ip eigrp topology` | Table de topologie complète |
| `show ip route eigrp` | Routes installées |
| `debug eigrp packets` | Capture en temps réel (à utiliser avec précaution) |

### 6.4 Bonnes pratiques  

1. **Désactiver l’auto‑summary** sur tous les routeurs dans un réseau VLSM.  
2. **Uniformiser les K‑values** dès le départ.  
3. **Utiliser le mode named** pour une meilleure lisibilité et la prise en charge d’IPv6.  
4. **Limiter les timers Hello/Hold** pour les liaisons à haute latence (ex : WAN).  
5. **Planifier la redistribution** avec des route‑maps afin de contrôler les métriques entrantes.

---

## 7. Fonctionnalités avancées  

### 7.1 Stub Router  

```text
router eigrp 100
  eigrp stub connected summary-only
```

- **Connected** : annonce uniquement les routes directement connectées.  
- **Summary‑only** : n’annonce que les résumés configurés, masque les routes internes.  
- Réduit la taille de la table de topologie dans les zones périphériques.

### 7.2 Variance (multipath)  

```text
router eigrp 100
  variance 4
```

- Permet d’installer **n** routes tant que leur métrique ≤ `variance × best‑metric`.  
- Exemple : best = 10 000 → avec variance 4, toutes les routes ≤ 40 000 seront utilisées pour le load‑balancing.

### 7.3 Summarisation  

- **Classful** (dépréciée) : `summary-address` sur interface.  
- **Classless** (recommandée) : `summary-address <network> <mask> [metric <value>]`.  

```text
interface Serial0/0
  ip summary-address eigrp 100 172.16.0.0 255.255.0.0
```

### 7.4 Redistribution  

| Source | Commande de base | Exemple de contrôle |
|--------|------------------|---------------------|
| OSPF   | `redistribute ospf 1 metric 10000 100` | `metric` obligatoire (bandwidth, delay) |
| static | `redistribute static metric 20000 100` | `metric` obligatoire |
| BGP    | `redistribute bgp 65000 metric 30000 100` | `metric` obligatoire, `route‑map` possible |

```text
router eigrp 100
  redistribute ospf 1 metric 10000 100 route-map OSPF2EIGRP
```

```text
route-map OSPF2EIGRP permit 10
  match ip address prefix-list OSPF-EXPORT
  set metric 12000 100
```

### 7.5 Route‑maps & distribute‑list  

```text
access-list 10 permit 10.10.0.0 0.0.255.255
router eigrp 100
  distribute-list 10 out GigabitEthernet0/1
```

- **Distribute‑list** filtre les routes sortantes/incoming sur une interface.

---

## 8. EIGRP Named Mode & IPv6  

### 8.1 Syntaxe Named  

```text
router eigrp MyEIGRP
  address-family ipv4 unicast autonomous-system 100
    network 10.0.0.0 0.0.0.255
    passive-interface default
    no passive-interface GigabitEthernet0/0
    eigrp router-id 1.1.1.1
    topology base
    metric weight K1 1 K2 0 K3 1 K4 0 K5 0
  exit-address-family
  address-family ipv6 unicast autonomous-system 100
    interface GigabitEthernet0/1
    eigrp router-id 2.2.2.2
    topology base
  exit-address-family
```

- **Avantages** :  
  - Séparation claire IPv4/IPv6.  
  - Possibilité de **topologies multiples** (ex : base, backup).  
  - Gestion centralisée des **K‑values** et **metric‑weights**.

### 8.2 Configuration IPv6 (Classic)  

```text
ipv6 router eigrp 100
  eigrp router-id 10.0.0.1
  passive-interface default
  no passive-interface GigabitEthernet0/1
```

```text
interface GigabitEthernet0/1
  ipv6 address 2001:db8:1::1/64
  ipv6 eigrp 100
```

### 8.3 Migration IPv4 → IPv6  

1. **Déployer le processus named** avec les deux families.  
2. **Activer les interfaces IPv6** progressivement.  
3. **Vérifier la convergence** via `show ipv6 eigrp topology`.  
4. **Retirer** les configurations IPv4 une fois la transition terminée.

---

## 9. Sécurité & Authentification  

| Méthode | Configuration | Points forts |
|---------|----------------|--------------|
| **MD5** | `key chain EIGRP-KEYS` + `ip authentication mode eigrp 100 md5` | Authentification bidirectionnelle, clé rotative |
| **ACL** | `access-list 101 permit ip host 10.0.0.1 any` + `eigrp access-group 101 in` | Filtrage du trafic de voisinage |
| **Passive‑interface** | `passive-interface GigabitEthernet0/2` | Empêche l’établissement de voisinage sur les interfaces non‑router |

### Exemple complet MD5  

```text
key chain EIGRP-KEYS
  key 1
    key-string MySecretKey1
    cryptographic-algorithm md5
    accept-lifetime 00:00:00 Jan 01 2025 23:59:59 Dec 31 2030
  key 2
    key-string MySecretKey2
    cryptographic-algorithm md5
    start-lifetime 00:00:00 Jan 01 2031 23:59:59 Dec 31 2040

router eigrp 100
  ip authentication mode eigrp 100 md5
  ip authentication key-chain eigrp 100 EIGRP-KEYS
```

- **Rotation** : configurez les *start‑lifetime* / *accept‑lifetime* pour automatiser le basculement de clé.

---

## 10. Comparaison avec OSPF, IS‑IS, BGP, RIP  

| Caractéristique | EIGRP | OSPF (v2) | IS‑IS | BGP (iBGP) | RIP |
|-----------------|-------|-----------|-------|------------|-----|
| **Type** | Distance‑vector + link‑state (hybride) | Link‑state | Link‑state | Path‑vector | Distance‑vector |
| **Convergence** | Rapide (DUAL) | Rapide (SPF) | Rapide | Lente (path‑vector) | Très lente |
| **Scalabilité** | Jusqu’à 10 000 routes (pratique) | 65 535 routers (area) | 10 000+ routers | 100 000+ prefixes | < 15 hops |
| **Metric** | Composite (BW, Delay, etc.) | Cost (BW) | Cost (BW) | AS‑Path, MED | Hop‑count |
| **Multipath** | Load‑balancing *n*‑paths (variance) | ECMP (up to 16) | ECMP (up to 64) | ECMP (configurable) | ECMP (up to 4) |
| **VLSM** | Oui (classless) | Oui | Oui | Oui | Non |
| **Authentication** | MD5, SHA‑256 (via key‑chain) | MD5, SHA‑256 | MD