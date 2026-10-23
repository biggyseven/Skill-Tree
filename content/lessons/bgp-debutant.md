
# BGP – Débutant

**Objectif :** Comprendre ce qu'est un Système Autonome (AS) et configurer une session eBGP basique entre deux routeurs.--

## 1. C'est quoi BGP ?

BGP (Border Gateway Protocol) est le protocole de routage qui relie les réseaux entre eux sur **Internet**. C'est un protocole de type **Path-Vector** (vecteur de chemin). 

Contrairement à OSPF qui cherche le chemin le plus rapide, BGP cherche le chemin qui respecte les **politiques** et les **règles** des entreprises.

> **Analogie** : OSPF, c'est le GPS de votre ville (il cherche le chemin le plus court). BGP, c'est le routage aérien international (il doit respecter les frontières, les douanes et les accords entre pays).

## 2. Les Systèmes Autonomes (AS)

Un **AS (Autonomous System)** est un ensemble de réseaux gérés par une seule entité (une entreprise, un fournisseur d'accès, une université). Chaque AS possède un numéro unique (ASN) attribué par l'IANA, par exemple `AS 15169` pour Google.

Il existe deux types de BGP :
- **eBGP (External BGP)** : Entre deux AS différents.
- **iBGP (Internal BGP)** : À l'intérieur d'un même AS.

## 3. La configuration minimale (eBGP)

Pour connecter deux routeurs de deux AS différents (par exemple AS 65001 et AS 65002) :

```cisco
R1(config)# router bgp 65001
R1(config-router)# neighbor 192.168.1.2 remote-as 65002
(Le routeur R2 doit avoir la configuration inverse : router bgp 65002 et neighbor 192.168.1.1 remote-as 65001).

4. Annoncer un réseau
Contrairement à OSPF, la commande network dans BGP ne "découvre" pas le réseau. Elle injecte dans BGP une route qui existe déjà dans la table de routage.

cisco
R1(config-router)# network 10.10.10.0 mask 255.255.255.0
(Il faut que le routeur R1 ait déjà ce réseau dans sa table de routage pour que la commande fonctionne).

5. Vérifier que ça marche
La commande reine dans BGP :

cisco
Router# show ip bgp summary
Vous devez voir l'état Established en face de l'adresse IP du voisin. Si l'état est Active ou Idle, il y a un problème de connectivité ou d'AS.