OSPF – Intermédiaire

Maintenant que vous savez configurer OSPF, explorons comment il gère les réseaux complexes (DR/BDR) et comment fonctionne le calcul des routes (LSDB).

## 1. L'élection du DR et du BDR

Sur un réseau de type Broadcast (comme un switch Ethernet), si 10 routeurs OSPF sont connectés, ils ne vont pas s'envoyer les mises à jour entre eux (cela ferait 45 relations !). OSPF élit donc un **DR (Designated Router)** et un **BDR (Backup Designated Router)**.

- Tous les autres routeurs (DROther) n'envoient leurs mises à jour qu'au DR et au BDR.
- Le DR centralise les informations et les redistribue.

**Comment est élu le DR ?**
1. Le routeur avec la plus haute **priorité OSPF** (par défaut 1) gagne.
2. En cas d'égalité, le routeur avec le **Router-ID le plus haut** gagne.

> **Attention** : Il n'y a pas de préemption. Si un routeur avec une priorité plus haute arrive après l'élection, il ne deviendra pas DR tant que l'ancien DR n'aura pas redémarré.

## 2. Le coût OSPF (Cost)

La métrique d'OSPF est le Coût. Il est calculé avec la formule :

```text
Coût = 100 000 000 / Bande passante (en bps)
Un lien Gigabit (1 Gbps) a un coût de 1.

Un lien FastEthernet (100 Mbps) a un coût de 1 aussi (car 100 000 000 / 100 000 000 = 1).

Un lien Serial (1,5 Mbps) a un coût de 64.

Le piège : Avec cette référence par défaut de 100 Mbps, un lien Gigabit et un lien 10 Gigabit ont tous les deux un coût de 1. Pour différencier les liens rapides, on doit changer la référence de bande passante :

cisco
router ospf 1
 auto-cost reference-bandwidth 10000
(Cela change la référence à 10 Gbps).

3. Les LSA et la LSDB
Les routeurs OSPF s'échangent des LSA (Link State Advertisements) pour construire leur carte (LSDB). Il existe plusieurs types de LSA :

Type 1 (Router LSA) : Décrit les liens du routeur.

Type 2 (Network LSA) : Généré par le DR pour décrire le réseau broadcast.

Type 3 (Summary LSA) : Généré par les routeurs frontières (ABR) pour résumer les réseaux d'une aire vers une autre.

4. Les états de voisinage
Quand deux routeurs OSPF se parlent, ils passent par plusieurs états :

DOWN : Aucun Hello reçu.

INIT : Hello reçu, mais le routeur ne s'est pas vu dedans.

2-WAY : Communication bidirectionnelle établie.

EXSTART : Négociation du maître/esclave (souvent bloqué si MTU différent).

EXCHANGE : Échange des bases de données (DBD).

LOADING : Demande des LSA manquants.

FULL : Les bases de données sont synchronisées.

5. Le Multi-Area
Diviser OSPF en plusieurs aires (Areas) permet de réduire la taille de la LSDB et d'accélérer les calculs.
Toutes les aires doivent se connecter à l'Area 0. Les routeurs qui font le lien entre les aires sont appelés des ABR (Area Border Router).

cisco
router ospf 1
 network 10.0.0.0 0.0.0.255 area 0
 network 172.16.0.0 0.0.255.255 area 1
