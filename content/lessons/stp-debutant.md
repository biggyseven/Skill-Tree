# Les Boucles Réseau et l'Élection de la Racine (STP)

**Niveau :** Technicien / Administrateur Junior

Imaginez un réseau local avec plusieurs switches connectés entre eux pour assurer la redondance. Si vous branchez un câble entre le Switch A et B, un autre entre B et C, et encore un entre C et A... vous venez de créer une **boucle physique**.

> **Analogie** : C'est comme un carrefour giratoire où toutes les voitures tourneraient en rond sans jamais pouvoir sortir. Très vite, le trafic sature et plus personne ne peut avancer.

## 1. Pourquoi les boucles sont mortelles en Couche 2 ?

Contrairement à la Couche 3 (où le protocole IP possède un champ TTL qui détruit les paquets après un certain nombre de sauts), la Couche 2 (Ethernet) **n'a pas de TTL**. Si une trame de diffusion (Broadcast) entre dans une boucle, elle va tourner à l'infini.

Cela provoque trois catastrophes :
1. **La tempête de broadcast** : La bande passante est saturée à 100%.
2. **L'instabilité de la table MAC** : Le switch apprend l'adresse MAC sur le port 1, puis la voit arriver sur le port 2 l'instant d'après.
3. **La duplication des trames** : Le destinataire reçoit le même paquet plusieurs fois.

## 2. La solution : Spanning Tree Protocol (STP)

Pour éviter cela, on utilise le protocole **STP (IEEE 802.1D)**. Son rôle est de **casser les boucles** en bloquant logiquement certains ports.

> 💡 **Note culturelle et technique** : Contrairement à OSPF qui utilise l'algorithme de **Dijkstra (SPF)** pour trouver le chemin le plus court, STP utilise l'algorithme de **Radia Perlman**. L'objectif de STP n'est pas d'être rapide, mais de trouver une topologie sans boucle (un arbre).

## 3. L'élection du Pont Racine (Root Bridge)

Pour créer cet arbre, STP doit d'abord élire un chef : le **Root Bridge**. Tous les switches s'envoient des messages appelés **BPDU** contenant leur **Bridge ID (BID)**.
Le **BID** est composé de la Priorité (par défaut 32768) et de l'adresse MAC.

### Règle d'élection :
1. Le switch avec la **priorité la plus basse** gagne.
2. En cas d'égalité, le switch avec la **plus petite adresse MAC** gagne.

```text
       [ Switch A ] (Prio 32768, MAC: 00:00:11:11:11:11)
             |
      [ Switch B ] (Prio 32768, MAC: 00:00:22:22:22:22)

Résultat : Le Switch A est élu Root Bridge (car sa MAC est plus petite).
4. Forcer l'élection du Root Bridge
Dans un réseau bien conçu, on ne laisse pas le hasard décider. L'administrateur choisit manuellement le switch de cœur de réseau pour être le Root Bridge.

text
Switch(config)# spanning-tree vlan 10 root primary
(Cette commande magique baisse automatiquement la priorité du switch à 24576).

🛑 Danger : Ne laissez jamais un switch d'accès (dans un bureau) devenir le Root Bridge. Cela créerait des chemins sous-optimaux et votre réseau serait très lent.

