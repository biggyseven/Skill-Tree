
# Cours Intensif – EIGRP (Avancé)

**Niveau : Administrateur Réseau Senior / CCIE**

EIGRP est un protocole de routage **hybride** (distance-vector à l’origine, mais avec des caractéristiques link-state comme les adjacences et la table de topologie). Il est réputé pour sa **convergence rapide**, sa **simplicité de configuration** et son **efficacité en environnement Cisco**. Depuis la publication de la **RFC 7868** (2016), il n’est plus strictement propriétaire et est implémenté dans FRR/Quagga.

> **Analogie** : EIGRP, c’est un GPS qui connaît déjà plusieurs itinéraires de secours. Tant qu’un chemin alternatif valide existe (Feasible Successor), il l’utilise **instantanément** sans recalculer toute la carte. S’il n’y a plus d’alternative, il demande à ses voisins (Query) — c’est la « diffusion » (DUAL).


## 1. Architecture Générale et Tables Internes

```text
[ Processus EIGRP (AS) ]
   |               |
 [DUAL]       [RIB inject]
   |               |
[Neighbor T.]   [Topology Table]
   \               /
    \             /
[Routing Table (RIB)]
Process ID / AS : identifiant local (ex. router eigrp 100). Deux routeurs ne forment un voisinage que si les AS sont identiques — sauf en Named Mode.

Neighbor Table : IP du voisin, interface, uptime, hold-time, SRTT (Smooth Round-Trip Time), RTO (Retransmission Timeout).

Topology Table : pour chaque destination, le Successor (meilleure route), les Feasible Successors (backups valides), la FD et la RD de chaque voisin.

Routing Table : seules les routes Successor (et les Successors multiples si variance est configurée) sont injectées dans la RIB.

Point clé : EIGRP maintient une table de topologie plus riche que la RIB. C’est cette réserve qui permet le basculement quasi instantané vers un Feasible Successor, sans recalcul global.

2. Algorithme DUAL : Successor, FD, RD et Condition de Faisabilité
Concept	Définition
Feasible Distance (FD)	Métrique totale du routeur local vers la destination, en passant par un voisin donné.
Reported Distance (RD)	Métrique annoncée par le voisin : c’est sa propre distance vers la destination.
Successor	Voisin dont la FD est la plus faible → route installée dans la RIB.
Feasibility Condition (FC)	Un voisin B est feasible si RD(B) < FD(A), où A est le routeur local.
Feasible Successor (FS)	Voisin qui satisfait la FC → candidate de secours sans boucle garantie.
Diffusing Computation	Si aucun FS n’existe, le routeur passe en Active et envoie des Query.
États DUAL
text
      [ PASSIVE (P) ]
            |
       (aucun FS)
            |
            v
      [ ACTIVE (A) ] <----- (Reply reçue)
            |
       (Reply reçue - toutes)
            |
            v
   [ Nouveau Successor ]
Passive : route stable, aucun calcul en cours.

Active : le routeur a perdu son Successor et n’a pas de FS. Il envoie des Query à tous ses voisins.

Stuck in Active (SIA) : si un voisin ne répond pas dans le SIA timer (3 minutes par défaut), le routeur coupe l’adjacence.

3. Métrique Composite et Formule Exacte
3.1 Formule classique (EIGRP « legacy », 32 bits)
text
Metric = 256 × [ (K1 × BW + (K2 × BW) / (256 − Load) ) + (K3 × Delay) ] × [ K5 / (K4 + Reliability) ]
Avec les valeurs par défaut (K1=1, K3=1, K2=K4=K5=0), la formule se simplifie :

text
Metric = 256 × ( BW + Delay )
Attention : beaucoup de cours simplifient à BW + Delay. La vraie formule inclut le facteur 256 (scaling EIGRP). Une route Gigabit a une métrique de l’ordre de 256 × (10 000 + 10) = 2 563 840.

3.2 Formule « Wide Metrics » (Named Mode, 64 bits)
En Named Mode, EIGRP utilise des métriques 64 bits pour supporter les liens ≥ 10 Gbps. Le rib-scaling (metric rib-scale <valeur>) permet d’aligner les valeurs lors d’une migration.

4. Configuration Avancée (Named Mode)
Le Named Mode (IOS 15.x+) sépare IPv4/IPv6 et permet les wide metrics.

cisco
router eigrp PROD
 !
 address-family ipv4 unicast autonomous-system 100
  topology base
   variance 2
   maximum-paths 4
  exit-topology
  network 10.0.0.0 0.0.0.255
  passive-interface default
  no passive-interface GigabitEthernet0/0
  eigrp router-id 1.1.1.1
 exit-address-family
 !
 address-family ipv6 unicast autonomous-system 100
  eigrp router-id 1.1.1.1
 exit-address-family
5. Fonctionnalités Avancées
5.1 Stub Router
Réduit la taille de la table et limite la propagation des Query.

cisco
router eigrp 100
 eigrp stub connected summary
5.2 Variance (Multipath / Load-Balancing)
Installe plusieurs routes si leur métrique est ≤ variance × meilleure métrique.

cisco
router eigrp 100
 variance 4
 maximum-paths 4
5.3 Redistribution
Redistribuer dans EIGRP exige une métrique.

cisco
router eigrp 100
 redistribute ospf 1 metric 10000 100 255 1 1500 route-map OSPF2EIGRP
5.4 Filtrage : distribute-list et offset-list
cisco
access-list 10 permit 10.10.0.0 0.0.255.255
router eigrp 100
 distribute-list 10 in GigabitEthernet0/1
6. Sécurité et Authentification
cisco
key chain EIGRP-KEYS
 key 1
  key-string MonMotDePasse1
  cryptographic-algorithm hmac-sha-256
  accept-lifetime 00:00:00 Jan 01 2025 infinite
  send-lifetime 00:00:00 Jan 01 2025 infinite
!
interface GigabitEthernet0/0
 ip authentication mode eigrp 100 hmac-sha-256
 ip authentication key-chain eigrp 100 EIGRP-KEYS
7. Dépannage Avancé
7.1 Voisins qui ne montent pas
Vérifier l’AS : show ip protocols | include EIGRP.

Vérifier les K-values : show ip eigrp interfaces detail.

Vérifier l’authentification : show key chain.

Vérifier le multicast : show ip mroute 224.0.0.10.

Debug : debug eigrp packets hello.

7.2 Stuck in Active (SIA)
Logs : %DUAL-3-SIA: Route X stuck-in-active state.

Solutions : Stub sur les sites distants, summarisation aux frontières, vérifier les filtres. Augmenter le SIA timer temporairement (timers active-time 5) pour diagnostiquer.

7.3 Métrique incohérente
Vérifiez bandwidth et delay (show interface | include BW|DLY). Attention aux migrations Named Mode (Wide metrics vs classic metrics).

8. Annexes
8.1 Glossaire
AS : Autonomous System

DUAL : Diffusing Update Algorithm

FD : Feasible Distance

RD : Reported Distance

FC : Feasibility Condition

FS : Feasible Successor

SIA : Stuck in Active

8.2 À retenir
EIGRP est hybride : distance-vector avec adjacences.

DUAL garantit l’absence de boucle via la Condition de Faisabilité (RD < FD).

L’authentification (MD5/SHA-256) est obligatoire sur les liens de transit.

Le Named Mode est la configuration moderne.

Toujours vérifier : AS, K-values, auth, subnet, passive-interface.

