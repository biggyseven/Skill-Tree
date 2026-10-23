
**Objectif :** Comprendre la logique d'OSPF, configurer deux routeurs et vérifier que le voisinage fonctionne.

## 1. Pourquoi OSPF ?

OSPF (Open Shortest Path First) est le protocole de routage le plus utilisé au monde. Contrairement à EIGRP qui est propriétaire Cisco, OSPF est un **standard ouvert** normalisé par l'IETF. Il fonctionne sur tous les équipements (Cisco, Juniper, Linux/FRR, etc.).

C'est un protocole **Link-State** : chaque routeur construit une carte complète de la topologie du réseau (appelée LSDB), puis calcule le plus court chemin avec l'algorithme de Dijkstra (SPF).

## 2. Les notions de base

- **Router ID** : L'identifiant unique du routeur (généralement une adresse IP de Loopback).
- **Area (Aire)** : Pour éviter que les routeurs ne saturent, le réseau est divisé en zones. L'**Area 0** est toujours le cœur du réseau (le Backbone).
- **Coût (Cost)** : C'est la métrique d'OSPF. Elle est basée sur la bande passante. Plus la bande passante est élevée, plus le coût est bas.
- **Hello** : Les petits messages que s'envoient les routeurs pour se dire "je suis toujours là".

## 3. La configuration minimale

Sur Cisco IOS, voici comment activer OSPF. On utilise un numéro de processus (qui est local au routeur, il n'a pas besoin d'être identique partout).

```cisco
Router(config)# router ospf 1
Router(config-router)# router-id 1.1.1.1
Router(config-router)# network 10.10.1.0 0.0.0.255 area 0
Explication :

router ospf 1 : Lance le processus OSPF.

router-id 1.1.1.1 : Définit l'identifiant unique du routeur.

network 10.10.1.0 0.0.0.255 area 0 : Active OSPF sur l'interface ayant l'IP 10.10.1.x et la place dans l'Area 0. (Attention : 0.0.0.255 est un masque wildcard, l'inverse du masque de sous-réseau).

4. Vérifier que ça marche
Deux commandes sont vitales :

cisco
Router# show ip ospf neighbor
Si le voisin est à l'état "FULL" (pour un lien point-à-point) ou "2-WAY" (sur un réseau broadcast), c'est bon.

cisco
Router# show ip route ospf
Les routes apprises par OSPF sont marquées avec la lettre O.

5. Les erreurs de débutant
L'erreur d'Area : Si deux routeurs sont sur le même câble mais que l'un est dans l'Area 0 et l'autre dans l'Area 1, ils ne deviendront jamais voisins.

Le MTU Mismatch : Si la MTU n'est pas la même sur les deux interfaces, le voisinage reste bloqué en état EXSTART. C'est très fréquent.

Le Passive-Interface : Sur une interface connectée à un PC, il ne faut pas envoyer de Hello OSPF. On utilise passive-interface.

cisco
router ospf 1
 passive-interface GigabitEthernet0/2
