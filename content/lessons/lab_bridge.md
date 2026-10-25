# Laboratoire réseau — Bridge Ethernet (`lab_bridge.md`)

> **Parcours :** fondamentaux → pratique Linux → VLAN → dépannage → STP et conception  
> **Niveau :** débutant à intermédiaire, avec défis avancés  
> **Environnement principal :** Linux récent avec `iproute2`, `bridge`, `ping` et `tcpdump`  
> **Environnement alternatif :** Cisco Packet Tracer, GNS3 ou commutateurs de laboratoire  
> **Objectif général :** comprendre comment un bridge de couche 2 apprend les adresses MAC, transfère les trames Ethernet, sépare les domaines de broadcast avec des VLAN et évite les boucles.


## 1. Objectifs pédagogiques

À la fin du laboratoire, tu dois être capable de :

1. expliquer la différence entre un bridge de couche 2, un switch et un routeur ;
2. créer un bridge Linux et y connecter plusieurs interfaces virtuelles ;
3. observer l'apprentissage MAC dans la table de transfert (FDB) ;
4. distinguer unicast connu, unicast inconnu, broadcast et trafic destiné au bridge lui-même ;
5. diagnostiquer une panne causée par un port détaché, une adresse IP incorrecte ou un VLAN absent ;
6. activer le filtrage VLAN sur un bridge Linux et vérifier l'isolation de couche 2 ;
7. expliquer le rôle de STP/RSTP face aux boucles Ethernet et reconnaître les risques d'une topologie redondante ;
8. fournir un compte rendu contenant commandes, preuves et cause racine.

Ce TP utilise des adresses réservées à la documentation. Il ne nécessite aucune connexion à Internet ni aucun équipement de production.

## 2. Rappels : ce qu'un bridge fait réellement

Un **bridge Ethernet** relie plusieurs ports de couche 2 et transfère des trames en examinant principalement l'adresse MAC de destination. Un switch Ethernet classique se comporte lui aussi comme un bridge multiport, généralement avec une implémentation matérielle et des fonctions supplémentaires.

Le bridge apprend l'adresse MAC **source** des trames reçues et associe cette adresse au port sur lequel elle a été observée. Cette association est stockée dans une table appelée **FDB** (*Forwarding Database*).

Lorsqu'une trame arrive :

- si la MAC de destination est connue, le bridge peut transmettre la trame vers le port associé, sous réserve des règles et de l'état des ports ;
- si la destination est inconnue, le bridge diffuse généralement la trame vers les autres ports éligibles du même domaine de couche 2 ;
- une trame broadcast, comme une requête ARP IPv4, est diffusée dans le domaine de broadcast concerné ;
- le port d'entrée n'est normalement pas utilisé comme port de sortie pour la même trame ;
- si une trame est destinée à l'adresse MAC du bridge lui-même, son traitement peut différer du simple transfert.

Le bridge ne choisit pas de chemin IP et ne route pas automatiquement entre deux sous-réseaux. Pour communiquer entre des VLAN ou des sous-réseaux IP distincts, il faut un équipement ou une fonction de couche 3 et une politique de routage appropriée.

### Petit schéma de principe

```text
          h1                    h2
    192.0.2.11/24        192.0.2.12/24
          |                     |
        port1                 port2
          \                     /
             +---------------+
             |  BRIDGE br-lab|
             +---------------+
                      |
                    port3
                      |
                     h3
                192.0.2.13/24
```

Les trois hôtes sont dans le même réseau de couche 2, et le même sous-réseau IPv4. Le bridge ne nécessite pas d'adresse IP pour transférer les trames.

## 3. Préparer l'environnement

### 3.1 Prérequis

Sur une VM Linux dédiée, vérifie la disponibilité des outils :

```bash
ip -Version
bridge -Version
ping -V 2>/dev/null || true
tcpdump --version
```

Si nécessaire, installe les paquets via le gestionnaire correspondant à ta distribution. Par exemple, sur Debian/Ubuntu :

```bash
sudo apt update
sudo apt install iproute2 iputils-ping tcpdump
```

Les manipulations de réseau virtuel requièrent généralement les privilèges administrateur. Les commandes de ce laboratoire créent des interfaces et des espaces de noms nommés `br-lab`, `h1`, `h2` et `h3`. **Ne les exécute pas sur un hôte qui utilise déjà ces noms pour d'autres services.** Une VM de test est recommandée.

### 3.2 Plan d'adressage

| Nœud | Interface dans le namespace | Adresse IPv4 | Rôle |
|---|---|---|---|
| h1 | `eth0` | `192.0.2.11/24` | Hôte de test 1 |
| h2 | `eth0` | `192.0.2.12/24` | Hôte de test 2 |
| h3 | `eth0` | `192.0.2.13/24` | Hôte de test 3 / observation |
| Bridge | `br-lab` | Aucune au premier exercice | Transfert de couche 2 |

Aucune passerelle n'est requise pour la connectivité entre ces hôtes, car ils appartiennent au même sous-réseau.

## 4. TP 1 — Créer un bridge Linux et trois hôtes

### Objectif

Construire un LAN virtuel à trois hôtes, sans routeur, puis valider la communication de couche 2 et de couche 3 locale.

### 4.1 Nettoyage préalable des objets du TP

Cette commande est utile si tu relances le TP. Elle supprime uniquement les objets portant les noms réservés par le laboratoire. Vérifie bien les noms avant de l'exécuter.

```bash
sudo ip netns del h1 2>/dev/null || true
sudo ip netns del h2 2>/dev/null || true
sudo ip netns del h3 2>/dev/null || true
sudo ip link del br-lab 2>/dev/null || true
```

### 4.2 Créer les namespaces et le bridge

```bash
sudo ip netns add h1
sudo ip netns add h2
sudo ip netns add h3

sudo ip link add br-lab type bridge
sudo ip link set br-lab up
```

Un *network namespace* dispose de ses interfaces, de sa table de routage et de son contexte réseau. Chaque hôte du TP sera isolé dans son propre namespace.

### 4.3 Créer les liens virtuels

Chaque paire `veth` se comporte comme un câble Ethernet virtuel. Une extrémité reste dans le namespace principal et sera raccordée au bridge ; l'autre est placée dans l'espace de noms de l'hôte.

```bash
sudo ip link add brp1 type veth peer name eth0 netns h1
sudo ip link add brp2 type veth peer name eth0 netns h2
sudo ip link add brp3 type veth peer name eth0 netns h3

sudo ip link set brp1 master br-lab
sudo ip link set brp2 master br-lab
sudo ip link set brp3 master br-lab

sudo ip link set brp1 up
sudo ip link set brp2 up
sudo ip link set brp3 up
```

### 4.4 Configurer les hôtes

```bash
sudo ip -n h1 link set lo up
sudo ip -n h2 link set lo up
sudo ip -n h3 link set lo up

sudo ip -n h1 addr add 192.0.2.11/24 dev eth0
sudo ip -n h2 addr add 192.0.2.12/24 dev eth0
sudo ip -n h3 addr add 192.0.2.13/24 dev eth0

sudo ip -n h1 link set eth0 up
sudo ip -n h2 link set eth0 up
sudo ip -n h3 link set eth0 up
```

### 4.5 Vérifier l'état du bridge

```bash
ip -d link show br-lab
bridge link show
ip -br link
sudo ip -n h1 address show
sudo ip -n h2 address show
sudo ip -n h3 address show
```

**Résultat attendu :** `br-lab` est actif, ses ports `brp1`, `brp2` et `brp3` sont attachés, et les interfaces des hôtes sont `UP` avec les adresses prévues.

### 4.6 Tester la connectivité

```bash
sudo ip netns exec h1 ping -c 3 192.0.2.12
sudo ip netns exec h1 ping -c 3 192.0.2.13
sudo ip netns exec h2 ping -c 3 192.0.2.13
```

Les trois tests doivent réussir. Si un test échoue, n'ajoute pas immédiatement une route : commence par vérifier les interfaces, les adresses, l'état du bridge et l'attachement des ports.

## 5. TP 2 — Observer l'apprentissage MAC (FDB)

### Objectif

Prouver que le bridge apprend les MAC source et utilise ces associations pour orienter les trames.

### 5.1 Afficher la table FDB

Après avoir généré quelques pings :

```bash
bridge fdb show br br-lab
bridge -s fdb show br br-lab
```

La sortie exacte varie selon le noyau et la version d'`iproute2`. Tu dois pouvoir repérer les entrées dynamiques apprises sur les ports du bridge. Certaines entrées locales ou permanentes peuvent aussi apparaître ; ne les confonds pas avec les associations MAC dynamiques des hôtes.

### 5.2 Relever les MAC des hôtes

```bash
sudo ip -n h1 link show eth0
sudo ip -n h2 link show eth0
sudo ip -n h3 link show eth0
```

Note les adresses `link/ether`, puis recherche ces adresses dans la FDB. Vérifie que la MAC de h1 est apprise sur `brp1`, celle de h2 sur `brp2` et celle de h3 sur `brp3`.

### 5.3 Observer l'apprentissage en temps réel

Dans un premier terminal :

```bash
sudo bridge monitor fdb
```

Dans un second terminal, lance de nouveaux pings ou supprime puis renouvelle une entrée dynamique si ton environnement le permet. Observe les notifications d'apprentissage ou de suppression.

Tu peux également vider les entrées dynamiques pour refaire l'expérience :

```bash
sudo bridge fdb flush br br-lab dynamic
```

Puis relance un ping. Selon la version d'`iproute2`, les options précises disponibles peuvent différer ; consulte `bridge fdb help` si la commande n'est pas acceptée.

### Questions

1. Pourquoi le bridge apprend-il à partir de l'adresse MAC source plutôt qu'en se basant uniquement sur l'adresse de destination ?
2. Pourquoi la FDB n'est-elle pas une table de routage IP ?
3. Pourquoi les entrées dynamiques finissent-elles par expirer ?
4. Que peut-il arriver si une même adresse MAC semble alternativement provenir de deux ports ?

**Livrable :** tableau associant MAC, port, type d'entrée et preuve issue de la FDB.

## 6. TP 3 — Diffusion ARP et unicast

### Objectif

Observer la différence entre une trame broadcast et un paquet unicast à destination connue.

### 6.1 Capturer le trafic sur h3

Lance une capture dans h3 :

```bash
sudo ip netns exec h3 tcpdump -ni eth0 'arp or icmp'
```

Dans un autre terminal, génère un ping de h1 vers h2 :

```bash
sudo ip netns exec h1 ping -c 2 192.0.2.12
```

**Observation attendue :** h3 peut voir la requête ARP broadcast envoyée par h1 pour résoudre la MAC de h2. Une fois la destination connue et la FDB apprise, les trames ICMP unicast entre h1 et h2 ne devraient normalement pas être livrées à h3.

La visibilité exacte dépend du moment de capture, du contenu des caches ARP, de l'état de la FDB et des fonctions activées. Pour rendre l'essai plus lisible, vide les entrées dynamiques de la FDB puis relance les tests.

### 6.2 Identifier le chemin des paquets

```bash
sudo ip netns exec h1 ip neigh show
sudo ip netns exec h2 ip neigh show
bridge fdb show br br-lab
```

Dans Wireshark, si tu captures sur un point adapté, tu peux utiliser les filtres d'affichage `arp` et `icmp`. Attention : les filtres d'affichage Wireshark ne sont pas les mêmes que les filtres de capture `tcpdump`.

### Questions

- Pourquoi ARP utilise-t-il une requête broadcast dans le LAN IPv4 local ?
- Pourquoi le bridge ne diffuse-t-il pas normalement chaque trame unicast à tous ses ports ?
- Quelle différence entre une table ARP sur un hôte et la FDB du bridge ?

## 7. TP 4 — Dépannage : isoler une panne de port

### Objectif

Apprendre à diagnostiquer une panne de couche 2 sans modifier plusieurs paramètres simultanément.

### 7.1 Désattacher volontairement un port

Détache le port de h2 du bridge :

```bash
sudo ip link set brp2 nomaster
```

Puis teste :

```bash
sudo ip netns exec h1 ping -c 3 192.0.2.12
sudo ip netns exec h1 ping -c 3 192.0.2.13
bridge link show
```

Le ping vers h2 doit échouer, tandis que celui vers h3 doit pouvoir continuer à fonctionner. L'interface de h2 peut rester `UP`, mais elle n'est plus reliée au bridge : cela démontre qu'une interface active ne garantit pas la connectivité de bout en bout.

### 7.2 Restaurer la connectivité

```bash
sudo ip link set brp2 master br-lab
sudo ip link set brp2 up
sudo ip netns exec h1 ping -c 3 192.0.2.12
```

### 7.3 Autres pannes contrôlées

Dans le même esprit, essaie séparément :

- désactiver `brp3` puis vérifier les effets sur h3 ;
- affecter temporairement une adresse incorrecte à h2 ;
- arrêter `eth0` dans h2 ;
- examiner les voisins ARP et la FDB après chaque panne.

Pour chaque essai, réponds aux questions suivantes : quel test a échoué, quelle observation identifie la couche en cause, quelle correction minimale rétablit le service, et quelle vérification prouve le rétablissement ?

## 8. TP 5 — Bridge VLAN-aware et isolation 802.1Q

### Objectif

Activer le filtrage VLAN dans un bridge Linux et vérifier que les trames ne traversent pas automatiquement d'un VLAN à un autre.

**Important :** ce TP utilise un bridge séparé nommé `br-vlan` et des namespaces dédiés (`v1`, `v2`, `v3`). Il peut donc coexister avec le premier laboratoire sans remplacer ses adresses ou ses interfaces.

Le filtrage VLAN d'un bridge Linux doit être activé explicitement. Lorsqu'il l'est, le bridge prend en compte le VLAN ainsi que la MAC de destination pour décider du transfert. Les notions `pvid` et `untagged` permettent notamment d'associer les trames non taguées reçues sur un port à un VLAN donné et d'émettre les trames sans étiquette sur un port access. Voir la documentation du noyau Linux et la page de manuel `bridge(8)` dans les références en fin de document.

### 8.1 Préparer un bridge dédié

```bash
sudo ip netns add v1
sudo ip netns add v2
sudo ip netns add v3

sudo ip link add br-vlan type bridge vlan_filtering 1 vlan_default_pvid 1
sudo ip link set br-vlan up

sudo ip link add bv1 type veth peer name eth0 netns v1
sudo ip link add bv2 type veth peer name eth0 netns v2
sudo ip link add bv3 type veth peer name eth0 netns v3

sudo ip link set bv1 master br-vlan
sudo ip link set bv2 master br-vlan
sudo ip link set bv3 master br-vlan
sudo ip link set bv1 up
sudo ip link set bv2 up
sudo ip link set bv3 up

sudo ip -n v1 link set lo up
sudo ip -n v2 link set lo up
sudo ip -n v3 link set lo up
```

### 8.2 Définir les VLAN sur les ports

Dans cet exemple, v1 et v2 sont des ports access du VLAN 10. v3 est un port access du VLAN 20. On retire le VLAN par défaut 1 des ports avant d'ajouter le VLAN souhaité.

```bash
sudo bridge vlan del dev bv1 vid 1 2>/dev/null || true
sudo bridge vlan del dev bv2 vid 1 2>/dev/null || true
sudo bridge vlan del dev bv3 vid 1 2>/dev/null || true

sudo bridge vlan add dev bv1 vid 10 pvid untagged
sudo bridge vlan add dev bv2 vid 10 pvid untagged
sudo bridge vlan add dev bv3 vid 20 pvid untagged
```

Selon la version et la configuration du bridge, l'affichage des VLAN attachés au bridge lui-même peut aussi inclure des entrées par défaut. Vérifie la configuration effective avec `bridge vlan show` plutôt que de supposer que les commandes ont produit un résultat particulier.

### 8.3 Configurer les hôtes

Pour démontrer la séparation de couche 2, les trois hôtes utilisent volontairement des adresses du même sous-réseau dans ce test. C'est une méthode pédagogique pour montrer que les requêtes ARP du VLAN 10 ne sont pas diffusées vers le VLAN 20. **Ce n'est pas une recommandation de conception : en production, deux VLAN distincts devraient normalement avoir des préfixes distincts**, avec un routage explicite si la communication est autorisée.

```bash
sudo ip -n v1 addr add 192.0.2.11/24 dev eth0
sudo ip -n v2 addr add 192.0.2.12/24 dev eth0
sudo ip -n v3 addr add 192.0.2.13/24 dev eth0

sudo ip -n v1 link set eth0 up
sudo ip -n v2 link set eth0 up
sudo ip -n v3 link set eth0 up
```

### 8.4 Vérifications

```bash
bridge vlan show
bridge link show
sudo ip netns exec v1 ping -c 3 192.0.2.12
sudo ip netns exec v1 ping -c 3 192.0.2.13
```

**Résultat attendu :** h1 et h2 communiquent dans le VLAN 10. h1 ne joint pas h3 au niveau de ce bridge, car les requêtes ARP restent dans le VLAN 10. Aucun routeur n'est configuré pour relier les VLAN.

### 8.5 Défi d'extension

Modifie la topologie pour connecter un routeur ou un namespace de routage à un trunk transportant les VLAN 10 et 20. Crée des interfaces L3 et définis un routage inter-VLAN. Ajoute ensuite des règles de filtrage si le scénario exige que certains flux restent interdits.

Ne mélange pas les concepts : le bridge assure le transfert de couche 2 ; un routeur ou un dispositif L3 assure le transfert entre sous-réseaux ; une ACL ou un pare-feu exprime les autorisations.

## 9. TP 6 — STP et prévention des boucles

### Objectif

Comprendre pourquoi une topologie Ethernet redondante exige un mécanisme de prévention de boucle.

Une boucle de couche 2 peut provoquer une duplication de trames, une tempête de broadcast, une instabilité des entrées MAC et une dégradation rapide du réseau. Contrairement au routage IP, Ethernet ne possède pas de champ TTL dans chaque trame qui limiterait naturellement la durée de circulation d'une trame en boucle.

STP (*Spanning Tree Protocol*) construit une topologie logique sans boucle ; RSTP améliore la vitesse de convergence dans les situations prises en charge. Les mécanismes et commandes précis dépendent de l'équipement et du système.

### Manipulation conseillée dans Packet Tracer

1. Crée trois commutateurs en triangle avec un poste sur au moins deux d'entre eux.
2. Vérifie le root bridge et les états des ports avant toute modification.
3. Débranche un lien et observe la reconvergence.
4. Modifie la priorité d'un commutateur de laboratoire pour provoquer une nouvelle élection du root bridge.
5. Compare les temps observés et les états avant/après.
6. Documente le lien qui est bloqué par STP et le chemin réellement utilisé par les trames.

Commandes Cisco courantes à adapter au modèle :

```text
show spanning-tree
show spanning-tree vlan 10
show spanning-tree root
show interfaces status
```

### Extension Linux facultative

Le bridge Linux possède un paramètre STP, mais son comportement dépend du noyau, de l'outil de gestion et de la topologie. Pour l'inspecter sur une maquette dédiée :

```bash
ip -d link show br-lab
bridge link show
```

N'active pas ou ne désactive pas STP au hasard sur un bridge raccordé à un réseau réel. Une expérience de boucle doit être confinée dans une VM ou un environnement de laboratoire isolé, sans lien vers le LAN de production. Pour ce cahier, Packet Tracer est l'environnement recommandé afin d'observer sans risque les états STP.

### Questions

- Pourquoi deux liens redondants sans agrégation ni STP peuvent-ils former une boucle ?
- Quelle différence entre un port STP bloqué et un port physiquement désactivé ?
- Pourquoi le root bridge doit-il être choisi intentionnellement dans un réseau d'entreprise ?
- Quand EtherChannel est-il adapté pour utiliser plusieurs liens physiques en un lien logique, et quelles contraintes de configuration faut-il respecter ?

## 10. TP 7 — Diagnostiquer un problème de trames

### Arbre de dépannage

**Symptôme : deux hôtes ne communiquent pas.** Procède dans cet ordre :

1. **Lien :** l'interface est-elle `UP` ? Le bon port est-il attaché au bridge ?
2. **Adresse :** les hôtes ont-ils une adresse et un masque compatibles avec le test ?
3. **Couche 2 :** les ports appartiennent-ils au même bridge et, si le filtrage est actif, au même VLAN ?
4. **Apprentissage :** la FDB contient-elle la MAC attendue sur le bon port ?
5. **ARP :** la requête part-elle, atteint-elle le bon domaine de broadcast et reçoit-elle une réponse ?
6. **Filtrage :** des règles nftables, ebtables, tc ou d'autres mécanismes interfèrent-ils ?
7. **Retour :** l'hôte distant dispose-t-il des informations nécessaires pour répondre ?

Commandes utiles :

```bash
ip -br link
ip -br address
bridge link show
bridge fdb show br br-lab
bridge vlan show
sudo ip netns exec h1 ip neigh show
sudo ip netns exec h1 ip route show
sudo ip netns exec h1 tcpdump -ni eth0 'arp or icmp'
```

Ne conclus pas que le bridge est en cause uniquement parce que le ping échoue. Le ping est un test ICMP/IP ; une mauvaise adresse, un masque incorrect, un filtre ou un problème de couche 3 peuvent également expliquer l'échec.

## 11. Questions d'évaluation

Réponds par écrit sans consulter la configuration pendant la première tentative.

1. Quel est le rôle principal d'un bridge Ethernet ?
2. Quelle différence entre la FDB du bridge et la table ARP d'un poste ?
3. Comment un bridge apprend-il l'emplacement d'une MAC ?
4. Que fait-il généralement lorsqu'une MAC de destination est inconnue ?
5. Pourquoi une requête ARP est-elle visible par plusieurs ports d'un même VLAN ?
6. Pourquoi deux VLAN ne communiquent-ils pas simplement parce qu'ils utilisent le même bridge physique ?
7. À quoi servent `pvid` et `untagged` dans `bridge vlan` ?
8. Pourquoi une topologie redondante peut-elle être dangereuse sans STP ou agrégation correcte ?
9. Pourquoi un ping échoué ne permet-il pas de conclure automatiquement que le bridge est défaillant ?
10. Quel test permet de prouver qu'un flux unicast ne devrait plus être diffusé vers un port tiers une fois la FDB apprise ?

### Barème sur 20

- 4 points : topologie créée correctement et connectivité de base démontrée ;
- 4 points : table FDB expliquée à partir des adresses MAC relevées ;
- 4 points : captures ARP/ICMP commentées ;
- 4 points : panne volontaire diagnostiquée puis corrigée ;
- 4 points : VLAN et STP expliqués, limites du test clairement précisées.

## 12. Nettoyage final

Supprime les interfaces, bridges et namespaces que tu as créés pour ce laboratoire. Vérifie d'abord les noms et l'absence d'utilisation par d'autres exercices.

```bash
sudo ip netns del h1 2>/dev/null || true
sudo ip netns del h2 2>/dev/null || true
sudo ip netns del h3 2>/dev/null || true
sudo ip netns del v1 2>/dev/null || true
sudo ip netns del v2 2>/dev/null || true
sudo ip netns del v3 2>/dev/null || true
sudo ip link del br-lab 2>/dev/null || true
sudo ip link del br-vlan 2>/dev/null || true
```

La suppression d'un namespace détruit ses interfaces virtuelles attachées. La suppression d'un bridge détache les ports associés. N'utilise pas ces commandes si tu as réutilisé ces noms pour un autre service.

## 13. Modèle de compte rendu

```text
Titre du laboratoire :
Date et environnement :
Version du noyau / iproute2 :
Topologie et plan d'adressage :
Objectif du test :
Hypothèse avant manipulation :
Commandes exécutées :
Résultats observés :
Preuves (FDB, interfaces, capture) :
Panne injectée :
Cause identifiée :
Correction :
Vérification après correction :
Limites de l'expérience :
Conclusion :
```

## 14. Références techniques

- [Documentation du noyau Linux — Ethernet Bridging](https://docs.kernel.org/networking/bridge.html) : paramètres du bridge, FDB, STP, filtrage VLAN et comportement de transfert.
- [Page de manuel `bridge(8)` d'iproute2](https://manpages.debian.org/trixie/iproute2/bridge.8.en.html) : commandes pour les ports, la FDB, les VLAN et la supervision.
- [Introduction aux bridges Linux — Red Hat Developer](https://developers.redhat.com/articles/2022/04/06/introduction-linux-bridging-commands-and-features) : exemples de création et d'inspection d'un bridge.

Vérifie les options prises en charge par la version de ton noyau et d'`iproute2`. Certaines sorties et options diffèrent entre distributions.


## Conclusion

Ce laboratoire montre comment un bridge relie des segments Ethernet, apprend les adresses MAC et décide où transmettre les trames. Les captures permettent de distinguer le broadcast ARP du trafic unicast ; la FDB montre les décisions d'apprentissage ; le filtrage VLAN explique comment plusieurs domaines de couche 2 peuvent partager une infrastructure physique sans partager automatiquement leurs broadcasts.

Le bon réflexe en exploitation est de ne pas confondre lien actif, appartenance au bridge, VLAN, connectivité IP et disponibilité applicative. En dépannant couche par couche et en conservant des preuves avant/après, tu peux identifier une panne de façon reproductible au lieu de modifier la configuration au hasard.
