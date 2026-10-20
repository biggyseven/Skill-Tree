# OSPF — Link-state, aires et convergence (CCNA / Admin Réseau)

> **Objectif** : comprendre OSPF de l'échange de Hello jusqu'au calcul SPF, savoir concevoir des aires simples, configurer Cisco IOS et FRRouting, vérifier les adjacences et diagnostiquer les blocages classiques (MTU, area ID, authentification, passive interface, DR/BDR). Ce cours est orienté production : chaque notion est reliée à une commande et à un symptôme.

---

## 1. Pourquoi OSPF

OSPF (Open Shortest Path First) est un protocole de routage **link-state** normalisé par l'IETF. Chaque routeur construit une carte complète de la topologie (LSDB), puis calcule le plus court chemin avec l'algorithme de Dijkstra (SPF).

Avantages :

- standard, interopérable ;
- convergence rapide ;
- support de la hiérarchie par **aires** ;
- calcul sans boucle ;
- support de l'authentification ;
- métrique basée sur la bande passante (coût).

Inconvénients :

- consommation CPU/RAM liée à la LSDB ;
- configuration plus lourde que RIP ;
- sensibilité aux problèmes de MTU et d'aire ;
- conception d'aires à maîtriser.

---

## 2. Terminologie

| Terme | Définition |
|---|---|
| Router ID | Identifiant unique du routeur OSPF (32 bits) |
| Area | Groupe logique de routeurs ; l'area 0 est le backbone |
| ABR | Area Border Router, relié à plusieurs aires |
| ASBR | Autonomous System Boundary Router, injecte des routes externes |
| LSA | Link-State Advertisement, information de topologie |
| LSDB | Link-State Database, base des LSA |
| SPF | Shortest Path First, calcul Dijkstra |
| Hello | Message de découverte et de maintien de voisinage |
| DR/BDR | Designated Router / Backup Designated Router |
| Coût | Métrique OSPF, inversement proportionnelle à la bande passante |

---

## 3. Hello et formation du voisinage

Les routeurs OSPF envoient des **Hello** périodiquement. Pour devenir voisins, ils doivent s'accorder sur :

- **Area ID** ;
- **Hello interval** et **Dead interval** ;
- **Network type** ;
- **Authentication** ;
- **MTU** (pour l'échange des DB, pas dans le Hello) ;
- **Stub area flag**.

| Type de réseau | Hello | Dead | Remarques |
|---|---:|---:|---|
| Broadcast (Ethernet) | 10 s | 40 s | DR/BDR élu |
| Point-to-point | 10 s | 40 s | Pas de DR/BDR |
| NBMA | 30 s | 120 s | DR/BDR, voisins statiques |
| Point-to-multipoint | 30 s | 120 s | Pas de DR/BDR |

```text
R1 ---- R2
Hello (10 s) : "Je suis R1, area 0, hello 10, dead 40"
R2 vérifie la compatibilité, répond.
Les deux passent en 2-Way (broadcast) ou Full (p2p).
```

### 3.1 États de voisinage

| État | Signification |
|---|---|
| Down | Aucun Hello reçu |
| Attempt | Unicast envoyé (NBMA) |
| Init | Hello reçu, mais pas son propre Router ID dedans |
| 2-Way | Hello bidirectionnel ; DR/BDR élu |
| ExStart | Négociation du maître/esclave et du MTU |
| Exchange | Échange des DBD |
| Loading | Demande des LSA manquants |
| Full | LSDB synchronisée |

Un voisin bloqué en **ExStart/Exchange** indique souvent un **MTU mismatch**. Un voisin bloqué en **2-Way** est normal entre DROther sur un réseau broadcast.

---

## 4. DR et BDR

Sur un réseau broadcast (Ethernet), OSPF élit un **DR** et un **BDR** pour réduire le nombre d'adjacences. Les autres routeurs (DROther) n'ont pas besoin d'être Full entre eux.

Élection :

1. plus forte **priorité** d'interface (0 = ne participe pas) ;
2. si égalité, plus fort **Router ID**.

```text
            R1 (prio 1, RID 1.1.1.1)
             |
R2 (prio 100) ---- R3 (prio 1)
             |
            R4 (prio 1)

DR = R2 (priorité la plus haute)
BDR = R4 ou R1 selon Router ID (le plus haut après R2)
```

La préemption n'existe pas : un DR élu le reste jusqu'à un redémarrage ou une modification. Pour forcer une élection, changer la priorité puis `clear ip ospf process`.

```cisco
interface Gi0/1
 ip ospf priority 100
exit
clear ip ospf process
```

---

## 5. LSA et LSDB

| LSA | Nom | Contenu | Origine |
|---|---|---|---|
| Type 1 | Router | Liens et coûts du routeur | Chaque routeur |
| Type 2 | Network | Réseau broadcast et DR | DR |
| Type 3 | Summary | Préfixes inter-aires | ABR |
| Type 4 | ASBR Summary | Localisation de l'ASBR | ABR |
| Type 5 | External | Routes externes | ASBR |
| Type 7 | NSSA External | Routes externes dans une NSSA | ASBR NSSA |

La LSDB doit être identique pour tous les routeurs d'une même aire. Vérification :

```cisco
show ip ospf database
show ip ospf database router
show ip ospf database network
show ip ospf database summary
show ip ospf database external
show ip ospf database database-summary
```

---

## 6. Coût et référence de bande passante

Le coût OSPF est :

```text
coût = référence de bande passante / bande passante de l'interface
```

Par défaut, la référence est **100 Mbit/s**. Un lien 100 Mbit/s a un coût de 1 ; un lien 1 Gbit/s aussi (1), ce qui ne différencie plus les liens rapides. On augmente la référence :

```cisco
router ospf 1
 auto-cost reference-bandwidth 100000
```

Cela donne :

| Débit | Réf. 100 Mbit/s | Réf. 100 Gbit/s |
|---|---:|---:|
| 10 Mbit/s | 10 | 10 000 |
| 100 Mbit/s | 1 | 1 000 |
| 1 Gbit/s | 1 | 100 |
| 10 Gbit/s | 1 | 10 |
| 100 Gbit/s | 1 | 1 |

La référence doit être **identique sur tous les routeurs** de l'aire, sinon les coûts sont incohérents.

Coût manuel :

```cisco
interface Gi0/1
 ip ospf cost 50
```

---

## 7. Configuration Cisco

### 7.1 OSPFv2 simple

```cisco
router ospf 1
 router-id 1.1.1.1
 network 10.10.1.0 0.0.0.255 area 0
 network 10.20.2.0 0.0.0.255 area 1
 passive-interface Gi0/24
!
interface Gi0/1
 ip address 10.10.1.1 255.255.255.0
 no shutdown
```

La commande `network` active OSPF sur les interfaces dont l'IP correspond au réseau et au wildcard. Le wildcard est l'inverse du masque.

### 7.2 Configuration par interface

```cisco
interface Gi0/1
 ip ospf 1 area 0
!
router ospf 1
 router-id 1.1.1.1
 passive-interface default
 no passive-interface Gi0/1
```

Cette méthode est plus explicite et évite les erreurs de wildcard.

### 7.3 Passive interface

Une interface passive annonce le réseau mais n'envoie pas de Hello. C'est indispensable sur les interfaces LAN où aucun voisin OSPF n'est attendu.

```cisco
router ospf 1
 passive-interface Gi0/10
 passive-interface default
 no passive-interface Gi0/1
```

### 7.4 Authentification

```cisco
interface Gi0/1
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 MOT_DE_PASSE
```

Ou au niveau de l'aire :

```cisco
router ospf 1
 area 0 authentication message-digest
```

Les deux côtés doivent avoir la même clé et le même ID de clé.

### 7.5 Route par défaut

```cisco
router ospf 1
 default-information originate
```

Si l'origine de la route par défaut n'est pas locale :

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1
router ospf 1
 default-information originate
```

`default-information originate always` annonce la route même si elle n'existe pas localement, ce qui peut créer un blackhole.

---

## 8. Aires et hiérarchie

### 8.1 Règles

- L'area 0 est le **backbone**.
- Toutes les aires doivent être reliées à l'area 0 (directement ou par un virtual link).
- Les routeurs d'une aire ont la même LSDB pour cette aire.
- Les ABR résument les préfixes entre aires.

```text
        Area 0
   R1 --------- R2
   |             |
Area 1        Area 2
   |             |
 R3 ----------- R4
```

### 8.2 Types d'aires

| Type | LSA 5 | Route par défaut | Usage |
|---|---|---|---|
| Standard | Oui | Non | Aire normale |
| Stub | Non | Oui | Réduire la LSDB |
| Totally stubby | Non | Oui | Cisco, résumé total |
| NSSA | Non (LSA 7) | Non | Externes limitées |
| Totally NSSA | Non (LSA 7) | Oui | Cisco |

```cisco
router ospf 1
 area 1 stub
 area 2 nssa
 area 3 stub no-summary
```

### 8.3 Résumé inter-aires

```cisco
router ospf 1
 area 1 range 10.10.0.0 255.255.0.0
```

Le résumé doit être configuré sur l'ABR, dans l'aire source.

### 8.4 Virtual link

Un virtual link relie une aire à l'area 0 à travers une autre aire. Il est utilisé quand une aire n'est pas physiquement connectée au backbone.

```cisco
router ospf 1
 area 1 virtual-link 2.2.2.2
```

Le virtual link doit être configuré des deux côtés avec les Router ID.

---

## 9. OSPFv3

OSPFv3 route IPv6. Il utilise des adresses link-local pour les adjacences et des identifiants de routeur 32 bits.

```cisco
ipv6 unicast-routing
interface Gi0/1
 ipv6 address 2001:db8:1::1/64
 ipv6 ospf 1 area 0
!
router ospfv3 1
 router-id 1.1.1.1
 address-family ipv6 unicast
 exit-address-family
```

Vérification :

```cisco
show ospfv3 neighbor
show ospfv3 database
show ipv6 route ospf
```

---

## 10. FRRouting sous Linux

FRR est la suite de routage la plus courante sous Linux. Elle fournit `zebra`, `ospfd`, `bgpd`, etc.

```bash
apt install frr
sed -i 's/ospfd=no/ospfd=yes/' /etc/frr/daemons
systemctl restart frr
vtysh
```

Configuration :

```text
configure terminal
router ospf
 router-id 1.1.1.1
 network 10.10.1.0/24 area 0
 network 10.20.2.0/24 area 1
 passive-interface eth2
exit
write memory
```

Vérification :

```text
show ip ospf neighbor
show ip ospf database
show ip route ospf
show ip ospf interface
```

### 10.1 BIRD

BIRD est une alternative légère.

```text
protocol ospf v2 {
  area 0 {
    interface "eth0" { hello 10; dead 40; };
    interface "eth1" { stub; };
  };
}
```

```bash
birdc show ospf neighbors
birdc show route
```

### 10.2 Linux tools

```bash
ip route show
tcpdump -eni eth0 ospf
ss -lunp | grep 89
```

OSPF utilise le protocole IP **89**, multicast `224.0.0.5` (AllSPFRouters) et `224.0.0.6` (AllDRouters).

---

## 11. Dépannage OSPF

### 11.1 Pas de voisin

| Cause | Vérification |
|---|---|
| Interface down | `show ip interface brief` |
| Mauvais subnet | `show ip ospf interface` |
| Passive interface | `show ip ospf interface` |
| Mauvais area | `show ip ospf neighbor`, `show ip ospf interface` |
| Authentification | `show ip ospf interface` |
| Hello/Dead différents | `show ip ospf interface` |
| Multicast bloqué | `tcpdump`, ACL |
| MTU différent | `show ip ospf neighbor`, `show interfaces` |

### 11.2 Voisin bloqué en ExStart/Exchange

Le plus souvent, **MTU mismatch**. OSPF n'échange pas les DBD si les MTU diffèrent.

```cisco
show interfaces Gi0/1 | include MTU
show ip ospf neighbor
```

Solutions : aligner le MTU ou configurer :

```cisco
interface Gi0/1
 ip ospf mtu-ignore
```

`mtu-ignore` masque le problème mais ne corrige pas la fragmentation éventuelle.

### 11.3 Voisin bloqué en 2-Way

Normal entre DROther sur un réseau broadcast. Si un routeur doit devenir DR/BDR, vérifier la priorité. Si deux routeurs seulement sont présents et restent en 2-Way, suspecter un problème de DR ou de multicast.

### 11.4 Routes absentes

```cisco
show ip route ospf
show ip ospf database
show ip ospf interface
show ip protocols
```

Vérifier que le réseau est bien annoncé, que l'aire est correcte, que le prochain saut est reachable, et qu'il n'y a pas de filtrage.

### 11.5 Flapping

Un voisinage qui monte et descend génère des recalculs SPF. Causes : lien instable, CPU, timers, MTU, authentification, duplex.

```cisco
show logging | include OSPF
show ip ospf neighbor
show processes cpu | include OSPF
```

### 11.6 Cas réel : MTU mismatch après changement de switch

Un lien passe de 1500 à 9000 sur un côté seulement. Les voisins restent en ExStart. `show interfaces` confirme. On aligne le MTU ou on configure `ip ospf mtu-ignore` temporairement. Leçon : documenter le MTU sur les liens trunk.

### 11.7 Cas réel : area mismatch lors d'une migration

Un nouvel ABR est configuré en area 1 alors que le lien est en area 0. Aucun voisin ne monte. La correction consiste à aligner l'aire sur l'interface. Vérifier `show ip ospf interface` des deux côtés.

### 11.8 Cas réel : route par défaut absente

L'ASBR a bien une route par défaut, mais `default-information originate` n'est pas configuré. Les routeurs internes n'ont pas de route `O*E2 0.0.0.0/0`. Ajouter la commande et vérifier `show ip route ospf`.

---

## 12. Bonnes pratiques

- Router ID stable et unique, généralement une loopback.
- Référence de bande passante identique partout.
- Passive interface par défaut, activer seulement les liens de transit.
- Authentification sur tous les liens.
- Aires conçues autour de la topologie, pas au hasard.
- Résumés sur les ABR.
- Surveiller les changements de voisinage et les recalculs SPF.
- Tester la convergence après chaque modification.

---

## 13. Laboratoire

1. Configurer OSPF entre deux routeurs et vérifier `show ip ospf neighbor`.
2. Ajouter une aire 1 et un ABR, vérifier les routes `O IA`.
3. Configurer une route par défaut et `default-information originate`.
4. Provoquer un MTU mismatch et observer ExStart.
5. Configurer FRRouting sous Linux et vérifier les voisins avec `vtysh`.
6. Capturer les Hello avec `tcpdump` et identifier les multicast.

---

## 14. Mémo

```cisco
show ip ospf neighbor
show ip ospf interface
show ip ospf database
show ip ospf route
show ip route ospf
show ip protocols
show ip ospf
debug ip ospf adj
clear ip ospf process
```

```bash
vtysh -c 'show ip ospf neighbor'
vtysh -c 'show ip route ospf'
birdc show ospf neighbors
tcpdump -eni eth0 ospf
```

---

## 15. Points clés

- OSPF est link-state : chaque routeur a une carte complète de son aire.
- Les Hello doivent correspondre sur l'aire, les timers, l'authentification et le réseau.
- Le DR/BDR réduit les adjacences sur les réseaux broadcast.
- Le coût dépend de la bande passante et de la référence ; la référence doit être homogène.
- Une aire doit toucher l'area 0 ; les ABR résument les préfixes.
- Un voisin en ExStart/Exchange = souvent MTU mismatch.
- `passive-interface` est une bonne pratique sur les LAN.
- Le diagnostic repose sur `show ip ospf neighbor`, `show ip ospf interface` et `show ip route ospf`.

> **Exercice** : deux routeurs sont reliés par un lien 1 Gbit/s, mais aucun voisin OSPF ne monte. Les interfaces sont `up`, les IP sont dans le même subnet. Quelles vérifications faites-vous ? Réponse : area ID, hello/dead, authentification, passive interface, multicast, MTU, ACL.

---

## 16. Étude de cas guidée : migration d'un réseau OSPF

Une entreprise possède un cœur OSPF en area 0 et deux sites en area 1 et area 2. Elle rachète un site équipé de routeurs configurés en RIPv2. Objectif : migrer sans coupure.

**Étape 1 — Inventaire.** Relever les sous-réseaux, les Router ID, les liens WAN, les routes par défaut et les politiques de filtrage. Vérifier les MTU et les authentifications existantes.

**Étape 2 — Plan d'adressage OSPF.** Choisir des Router ID uniques (loopbacks), définir les aires, documenter les résumés et les passive interfaces. Prévoir une référence de bande passante commune, par exemple 100 Gbit/s.

**Étape 3 — Préparation.** Configurer OSPF sur les liens de transit uniquement, garder les LAN en passive interface. Annoncer les préfixes de manière explicite. Ne pas injecter de route par défaut tant que le reste n'est pas stable.

**Étape 4 — Migration progressive.** Activer OSPF sur un lien à la fois. Vérifier `show ip ospf neighbor` en état Full, puis `show ip route ospf`. Comparer les routes avant/après. Conserver temporairement les routes statiques avec une distance administrative plus élevée pour le secours.

**Étape 5 — Redistribution.** Si RIP doit coexister, configurer une redistribution contrôlée avec des route-maps et des filtres. Toujours vérifier les boucles de redistribution et les métriques. Préférer une migration nette plutôt qu'une coexistence longue.

**Étape 6 — Vérification.** Tester la convergence en coupant un lien, mesurer le temps de bascule, vérifier les logs et les recalculs SPF. Contrôler que les résumés sont présents et que les routes par défaut sont cohérentes.

**Étape 7 — Nettoyage.** Retirer les routes statiques devenues inutiles, supprimer les anciens protocoles, mettre à jour la documentation et les sauvegardes. Surveiller pendant quelques jours les voisinages et les changements de topologie.

### 16.1 Erreurs fréquentes pendant une migration

- annoncer les LAN en area 0 alors qu'ils devraient être dans une aire de site ;
- oublier `passive-interface` et envoyer des Hello sur les LAN ;
- utiliser des références de bande passante différentes ;
- redistribuer sans filtre et créer des boucles ;
- modifier le MTU d'un côté seulement ;
- changer le Router ID sans redémarrer le processus ;
- laisser une route par défaut `always` créer un blackhole.

### 16.2 Check-list de validation

```text
[ ] Tous les voisins sont Full
[ ] Les Router ID sont uniques
[ ] Les aires correspondent au plan
[ ] Les LAN sont en passive interface
[ ] La référence de bande passante est homogène
[ ] Les résumés sont visibles sur les ABR
[ ] La route par défaut est annoncée correctement
[ ] Les routes de secours sont testées
[ ] Les logs ne montrent pas de flapping
[ ] La documentation est à jour
```

Cette méthode s'applique aussi à une migration OSPFv3 ou à un remplacement de constructeur. La clé est de valider chaque lien avant de passer au suivant, et de toujours connaître la route de retour.
