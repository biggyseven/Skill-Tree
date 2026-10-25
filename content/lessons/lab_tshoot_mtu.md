# Laboratoire de dépannage MTU et PMTUD — `lab_tshoot_mtu.md`

> **Parcours :** débutant → intermédiaire → expert  
> **Environnement principal :** Linux avec `iproute2`, `ping`, `tcpdump` et `nftables` dans des espaces de noms réseau dédiés.  
> **Environnements complémentaires :** Cisco IOS/IOS XE, Wireshark, GNS3 ou CML.  
> **Fil conducteur :** NovaTech, dont certaines applications échouent uniquement lorsque les paquets deviennent volumineux, alors que les petits pings et les états d'interface paraissent normaux.


## 1. Objectifs pédagogiques

À la fin de ce laboratoire, tu dois pouvoir :

1. expliquer la différence entre MTU d'interface, MTU de chemin (PMTU), taille de trame Ethernet et MSS TCP ;
2. calculer la taille d'un paquet de test à partir de la taille de données demandée par `ping` ;
3. reconnaître le comportement IPv4 lorsque le bit DF est activé ou désactivé ;
4. expliquer pourquoi un routeur IPv6 ne fragmente pas les paquets IPv6 en transit ;
5. observer un message ICMP « fragmentation nécessaire » ou ICMPv6 « Packet Too Big » ;
6. reproduire un **PMTU black hole**, où les messages ICMP nécessaires sont bloqués et les gros paquets disparaissent silencieusement ;
7. utiliser `ping`, `tracepath`, `tcpdump` et Wireshark pour localiser une limite MTU ;
8. identifier les effets de l'encapsulation dans GRE, IPsec, VXLAN ou d'autres overlays ;
9. distinguer une panne de MTU d'une panne DNS, d'un problème de routage ou d'un filtrage applicatif ;
10. documenter le diagnostic, la correction et les tests de non-régression.

Ce cahier privilégie la démonstration. Chaque changement doit être effectué dans un laboratoire isolé et accompagné de preuves avant/après.

## 2. Précautions indispensables

- Effectue les expériences dans une VM dédiée, un simulateur ou des namespaces créés expressément pour ce TP. N'injecte pas de pannes MTU ou de filtrage ICMP dans un réseau de production.
- Les plages `192.0.2.0/24`, `198.51.100.0/24` et `2001:db8::/32` sont réservées aux exemples documentaires.
- Les commandes de ce cahier créent les namespaces `h1`, `r1` et `h2`, ainsi que des interfaces virtuelles portant des noms précis. Vérifie qu'ils ne sont pas déjà utilisés.
- Les expériences `nftables` modifient le filtrage **dans le namespace du routeur de laboratoire**, pas volontairement dans le pare-feu général de l'hôte. Ne copie pas les règles à l'aveugle sur une machine réelle.
- Sauvegarde les sorties de commande avant de modifier une MTU ou un filtre. Une correction efficace doit être justifiée par une cause observée.


## 3. Les notions indispensables

### 3.1 MTU : Maximum Transmission Unit

La **MTU** est la taille maximale de paquet de couche 3 que l'interface ou le lien peut transporter dans les conditions considérées. Sur Ethernet classique, une MTU IP courante est de **1500 octets**. Cette valeur ne doit pas être confondue avec la taille physique totale de la trame sur le fil : les en-têtes Ethernet et le FCS s'ajoutent selon les conventions de comptage. Les tags VLAN et les encapsulations peuvent modifier la taille de trame requise ; ils ne signifient pas automatiquement que chaque équipement doit réduire la MTU IP de quatre octets.

La valeur affichée par une commande doit être interprétée selon l'OS et le type d'interface. Une interface physique, un tunnel, un bridge et une interface overlay peuvent chacun exposer une MTU différente.

### 3.2 PMTU : Path MTU

La **Path MTU** est la plus grande taille de paquet IP qui peut traverser le chemin considéré sans fragmentation interdite ou perte causée par une limite MTU. Pour un chemin stable et simple, elle est généralement déterminée par le plus petit MTU de couche 3 des liens du parcours. Les tunnels, les routes multiples et les changements de chemin peuvent compliquer le résultat : la PMTU observée peut varier selon le chemin réellement emprunté.

Une interface configurée à 1500 octets ne garantit donc pas qu'un paquet IP de 1500 octets puisse traverser tout le trajet.

### 3.3 IPv4 : fragmentation et bit DF

En IPv4, le champ **DF** (*Don't Fragment*) indique qu'un paquet ne doit pas être fragmenté par les routeurs en transit.

- Lorsque DF n'est pas activé, un routeur IPv4 peut fragmenter le paquet si le prochain lien ne peut pas transporter le paquet complet, à condition que les conditions de transmission et la configuration le permettent.
- Lorsque DF est activé et qu'un paquet dépasse le MTU du prochain lien, le routeur doit généralement le rejeter et signaler le problème par ICMP Destination Unreachable, code « Fragmentation Needed » (Type 3, Code 4).
- Si le message ICMP est bloqué, la source peut ne pas apprendre la taille maximale utilisable. Le paquet peut alors être perdu à répétition.

### 3.4 IPv6 : ICMPv6 Packet Too Big

Les routeurs IPv6 ne fragmentent pas les paquets IPv6 en transit. Lorsqu'un paquet dépasse le MTU du prochain lien, le routeur l'écarte et envoie normalement un message **ICMPv6 Packet Too Big** (Type 2). La source doit réduire la taille des paquets ou utiliser un mécanisme de découverte approprié. Les messages ICMPv6 utiles ne doivent pas être bloqués aveuglément : ils sont nécessaires à plusieurs fonctions IPv6, y compris la découverte du MTU de chemin.

Le MTU de lien IPv6 minimal prévu par la spécification est de 1280 octets. Un chemin ou tunnel IPv6 doit être conçu et traité en conséquence.

### 3.5 Taille `ping` et taille réelle du paquet

Sous Linux, `ping -s N` indique la quantité de **données ICMP** envoyées, pas la taille totale du paquet IP. Pour un ping classique sans options IP supplémentaires :

- IPv4 : taille paquet IP ≈ `N + 20 octets d'en-tête IPv4 + 8 octets d'en-tête ICMP`, donc `N + 28` ;
- IPv6 : taille paquet IPv6 ≈ `N + 40 octets d'en-tête IPv6 + 8 octets d'en-tête ICMPv6`, donc `N + 48`.

Ces formules supposent l'absence d'en-têtes IP supplémentaires. Les options, les extensions, les encapsulations ou des particularités d'implémentation changent les calculs. La documentation `ping(8)` décrit l'option `-s` et le mode de découverte MTU `-M`.

**Exemple IPv4 sur un chemin MTU 1300 :**

- `ping -M do -s 1272 ...` construit normalement un paquet IP de 1300 octets ;
- `ping -M do -s 1273 ...` construit normalement un paquet IP de 1301 octets ; ce second paquet ne doit pas franchir un lien MTU 1300 sans fragmentation autorisée.

**Exemple IPv6 sur un chemin MTU 1300 :**

- `ping -6 -M do -s 1252 ...` correspond normalement à un paquet IPv6 de 1300 octets ;
- `ping -6 -M do -s 1253 ...` correspond normalement à 1301 octets.

Les options Linux `ping` doivent être vérifiées sur la version installée. Sous Windows, macOS et certains simulateurs, les options et le calcul de la taille peuvent être différents.

### 3.6 MSS TCP : ce n'est pas la MTU

La **MSS** (*Maximum Segment Size*) exprime la quantité maximale de données TCP dans un segment, hors en-têtes IP/TCP. Avec une MTU IP de 1500 octets, les valeurs usuelles calculées avec des en-têtes sans options sont :

- IPv4 : `1500 - 20 - 20 = 1460` octets ;
- IPv6 : `1500 - 40 - 20 = 1440` octets.

Les options TCP et d'autres en-têtes influencent la place restante dans un paquet réel. Le MSS clamping peut être un contournement utile pour certains flux TCP, notamment à travers des tunnels, mais il ne règle pas le MTU pour UDP, ICMP, QUIC ou tous les autres protocoles. Il ne remplace pas le diagnostic de la PMTU.


## 4. Topologie de référence du laboratoire Linux

Nous allons créer trois namespaces : deux hôtes et un routeur entre eux. Les interfaces côté h1 et côté routeur sont réglées à MTU 1500. Le lien de sortie vers h2 est volontairement limité à MTU 1300.

```text
h1                                      r1                                      h2
192.0.2.10/24 ---- r1-h1 192.0.2.1/24     198.51.100.1/24 r1-h2 ---- 198.51.100.10/24
    MTU 1500       MTU 1500        routeur Linux        MTU 1300       MTU 1300
                                      IPv4 forward
```

Adresses IPv6 complémentaires :

- h1 : `2001:db8:10::10/64` ; r1 côté h1 : `2001:db8:10::1/64` ;
- r1 côté h2 : `2001:db8:20::1/64` ; h2 : `2001:db8:20::10/64`.

### 4.1 Préparer les outils

Sur Debian/Ubuntu, dans une VM de laboratoire :

```bash
sudo apt update
sudo apt install iproute2 iputils-ping tcpdump nftables traceroute iputils-tracepath
```

Certains paquets ou noms de commandes diffèrent selon la distribution. `tracepath` n'est pas toujours inclus par défaut. Les tests principaux restent possibles avec `ping`, `ip` et `tcpdump`.

### 4.2 Vérifier que les noms ne sont pas déjà utilisés

```bash
ip netns list
ip link show br-mtu 2>/dev/null || true
```

Ce laboratoire ne crée pas de bridge `br-mtu`, mais cette vérification rappelle qu'il faut éviter de supprimer des objets qui appartiennent à d'autres exercices.

### 4.3 Créer les namespaces

Les commandes de nettoyage ci-dessous sont limitées aux noms réservés dans ce cahier. N'utilise ces noms pour aucun autre service pendant le TP.

```bash
sudo ip netns del h1 2>/dev/null || true
sudo ip netns del r1 2>/dev/null || true
sudo ip netns del h2 2>/dev/null || true

sudo ip netns add h1
sudo ip netns add r1
sudo ip netns add h2
```

### 4.4 Créer les liens veth

```bash
sudo ip link add h1-r1 type veth peer name r1-h1
sudo ip link add r1-h2 type veth peer name h2-r1

sudo ip link set h1-r1 netns h1
sudo ip link set r1-h1 netns r1
sudo ip link set r1-h2 netns r1
sudo ip link set h2-r1 netns h2
```

Chaque paire veth est un câble Ethernet virtuel. Les noms sont distincts pour faciliter l'observation des interfaces de chaque côté.

### 4.5 Attribuer les adresses IPv4 et régler les MTU

```bash
sudo ip -n h1 link set lo up
sudo ip -n r1 link set lo up
sudo ip -n h2 link set lo up

sudo ip -n h1 addr add 192.0.2.10/24 dev h1-r1
sudo ip -n r1 addr add 192.0.2.1/24 dev r1-h1
sudo ip -n r1 addr add 198.51.100.1/24 dev r1-h2
sudo ip -n h2 addr add 198.51.100.10/24 dev h2-r1

sudo ip -n h1 link set h1-r1 mtu 1500 up
sudo ip -n r1 link set r1-h1 mtu 1500 up
sudo ip -n r1 link set r1-h2 mtu 1300 up
sudo ip -n h2 link set h2-r1 mtu 1300 up

sudo ip -n h1 route add default via 192.0.2.1
sudo ip -n h2 route add default via 198.51.100.1
sudo ip netns exec r1 sysctl -w net.ipv4.ip_forward=1
```

Le paramètre `ip_forward` n'est activé que dans le namespace r1. Il ne modifie donc pas volontairement le routage IPv4 de l'hôte principal.

### 4.6 Ajouter IPv6

```bash
sudo ip -n h1 -6 addr add 2001:db8:10::10/64 dev h1-r1
sudo ip -n r1 -6 addr add 2001:db8:10::1/64 dev r1-h1
sudo ip -n r1 -6 addr add 2001:db8:20::1/64 dev r1-h2
sudo ip -n h2 -6 addr add 2001:db8:20::10/64 dev h2-r1

sudo ip -n h1 -6 route add default via 2001:db8:10::1
sudo ip -n h2 -6 route add default via 2001:db8:20::1
sudo ip netns exec r1 sysctl -w net.ipv6.conf.all.forwarding=1
```

Le lien de MTU 1300 respecte la valeur minimale habituelle de 1280 pour un lien IPv6. Les adresses `2001:db8::/32` sont réservées à la documentation.

### 4.7 Vérifier l'état initial

```bash
sudo ip -n h1 -br address
sudo ip -n r1 -br address
sudo ip -n h2 -br address
sudo ip -n h1 route show
sudo ip -n r1 route show
sudo ip -n h2 route show
sudo ip -n r1 -6 route show
```

Teste les petits pings IPv4 et IPv6 :

```bash
sudo ip netns exec h1 ping -c 3 198.51.100.10
sudo ip netns exec h1 ping -6 -c 3 2001:db8:20::10
```

Les petits paquets doivent passer. Si ces tests échouent, corrige l'adressage, le routage ou le forwarding avant de commencer les tests MTU.


## 5. TP 1 — Trouver la limite MTU avec IPv4

**Niveau :** débutant → intermédiaire  
**Objectif :** observer le passage à la limite MTU et l'erreur renvoyée quand un paquet IPv4 DF dépasse cette limite.

### 5.1 Vérifier la MTU de chaque interface

```bash
sudo ip -n h1 link show h1-r1
sudo ip -n r1 link show r1-h1
sudo ip -n r1 link show r1-h2
sudo ip -n h2 link show h2-r1
```

Résultat attendu : MTU 1500 sur h1-r1 et r1-h1, MTU 1300 sur r1-h2 et h2-r1.

### 5.2 Tester un paquet au-dessous de la limite

```bash
sudo ip netns exec h1 ping -4 -M do -s 1200 -c 3 198.51.100.10
```

Le paquet IPv4 a normalement une taille de `1200 + 28 = 1228` octets, inférieure à 1300. Il doit arriver à h2 et obtenir une réponse si l'environnement est configuré comme prévu.

### 5.3 Tester exactement la limite de 1300 octets

```bash
sudo ip netns exec h1 ping -4 -M do -s 1272 -c 3 198.51.100.10
```

La taille IP attendue est `1272 + 28 = 1300` octets. Elle correspond à la MTU de sortie de r1 et devrait passer.

### 5.4 Dépasser la limite d'un octet

```bash
sudo ip netns exec h1 ping -4 -M do -s 1273 -c 3 198.51.100.10
```

La taille IP attendue est 1301 octets. Comme le ping demande à ne pas fragmenter, r1 doit normalement rejeter le paquet et renvoyer un message ICMP « fragmentation nécessaire ». Sur Linux, le texte d'erreur peut ressembler à `Frag needed and DF set (mtu = 1300)`.

Le message exact dépend des versions et outils. L'important est la relation entre la taille demandée, la MTU de sortie et l'indication ICMP reçue.

### 5.5 Vérifier la table de routage et les caches PMTU

```bash
sudo ip netns exec h1 ip route get 198.51.100.10
sudo ip netns exec h1 ip route show cache 2>/dev/null || true
```

Les versions modernes de Linux n'exposent pas toutes les informations de cache PMTU sous la même forme. Le retour du message ICMP peut aussi influencer l'état PMTU associé à la destination ; les tests suivants doivent en tenir compte.

**Questions :**

- Pourquoi le ping de 1200 octets réussit-il alors que celui de 1273 échoue ?
- Pourquoi le petit ping initial ne prouvait-il pas que le chemin pouvait transporter des paquets de 1500 octets ?
- Quel message permet au client d'apprendre la limite du chemin ?

**À rendre :** sorties des trois pings, MTU des interfaces et calcul des tailles IP.


## 6. TP 2 — Observer le message ICMP « fragmentation nécessaire »

**Niveau :** intermédiaire  
**Objectif :** prouver où le paquet est rejeté et comment le retour ICMP aide la source.

### 6.1 Capturer sur le routeur

Dans un premier terminal :

```bash
sudo ip netns exec r1 tcpdump -ni any 'icmp or icmp6'
```

Dans un autre terminal :

```bash
sudo ip netns exec h1 ping -4 -M do -s 1273 -c 1 198.51.100.10
```

Avec `-i any`, la capture peut observer le paquet entrant sur `r1-h1` et le message ICMP généré par r1 puis envoyé vers h1. Si tu préfères capturer une interface précise, lance une capture séparée sur `r1-h1` pour l'échange aller/retour. Le paquet IPv4 trop grand ne doit normalement pas être transmis sur `r1-h2`.

### 6.2 Capturer au niveau de h1

```bash
sudo ip netns exec h1 tcpdump -ni h1-r1 'icmp or icmp6'
```

Refais le test de dépassement. Cherche la requête ICMP Echo sortante puis le message d'erreur en retour. Wireshark peut aider à afficher le type et le code ICMP.

### 6.3 Filtres Wireshark utiles

Filtres d'affichage :

```text
icmp
icmp.type == 3 && icmp.code == 4
icmpv6.type == 2
```

Le second filtre vise les messages IPv4 Destination Unreachable / Fragmentation Needed. Le troisième cible les messages ICMPv6 Packet Too Big. Les filtres d'affichage Wireshark ne sont pas les mêmes que les filtres de capture BPF utilisés par `tcpdump`.

### Résultat attendu

Le paquet volumineux avec DF ne passe pas le lien de MTU plus faible. Lorsque le message d'erreur ICMP revient à la source, celle-ci peut réduire la taille effective des paquets pour le chemin concerné. La PMTU n'est pas forcément identique pour toutes les destinations ni pour tous les chemins.


## 7. TP 3 — IPv4 sans DF : observer la fragmentation

**Niveau :** intermédiaire

En IPv4, un routeur peut fragmenter un paquet lorsque DF n'est pas activé et que le lien de sortie l'exige. La fragmentation a un coût et n'est pas un substitut à une conception MTU correcte, mais son observation permet de comprendre la différence avec le test précédent.

### Procédure

Utilise un paquet total de 1428 octets : une charge ICMP de 1400 octets plus les 28 octets usuels d'en-têtes IPv4/ICMP. Il tient sur le lien amont de 1500 mais dépasse la MTU de sortie de r1 à 1300.

```bash
sudo ip netns exec h1 ping -4 -M dont -s 1400 -c 2 198.51.100.10
```

Le comportement attendu dans cette topologie est que le paquet IPv4 puisse être fragmenté en transit par r1 et que h2 reçoive les fragments et reconstitue le paquet, tant que le filtrage et les autres paramètres le permettent.

Capture sur le lien de sortie :

```bash
sudo ip netns exec r1 tcpdump -ni r1-h2 'icmp'
```

Dans Wireshark, examine le champ `More fragments`, l'offset de fragment et les tailles. Les détails de réassemblage peuvent varier selon le point de capture : une capture avant la fragmentation ne montre pas nécessairement la même séquence qu'une capture après.

### Questions

- Pourquoi la fragmentation peut-elle fonctionner avec DF désactivé mais pas avec DF activé ?
- Quel est le coût opérationnel de la fragmentation ?
- Pourquoi une application peut-elle rencontrer une panne si les messages de découverte PMTU sont filtrés, même si certains petits paquets passent ?


## 8. TP 4 — Reproduire un PMTU black hole

**Niveau :** avancé  
**Objectif :** comprendre une panne où les gros paquets disparaissent sans que la source reçoive le message ICMP nécessaire.

Un **PMTU black hole** apparaît notamment lorsque des paquets trop gros sont rejetés en chemin et que le message ICMP « fragmentation nécessaire » (IPv4) ou Packet Too Big (IPv6) n'atteint pas la source. La source continue alors à envoyer des paquets trop grands, qui disparaissent. Les petits pings peuvent réussir ; une connexion peut s'établir puis sembler bloquée lorsqu'elle transfère beaucoup de données.

> Pour éviter qu'un résultat PMTU appris lors du TP précédent influence cet exercice, commence de préférence par un laboratoire recréé à neuf ou assure-toi que la destination de test n'a pas déjà enregistré de PMTU réduite.

### 8.1 Créer une règle de test dans r1

La règle suivante ne doit être créée que dans le namespace de laboratoire `r1`. Elle bloque les messages IPv4 Destination Unreachable sortant du routeur de labo, ce qui englobe le message « fragmentation nécessaire » utilisé ici.

```bash
sudo ip netns exec r1 nft add table inet labmtu
sudo ip netns exec r1 nft 'add chain inet labmtu output { type filter hook output priority 0; policy accept; }'
sudo ip netns exec r1 nft add rule inet labmtu output ip protocol icmp icmp type destination-unreachable drop
sudo ip netns exec r1 nft list table inet labmtu
```

La table ne modifie pas volontairement le pare-feu principal de l'hôte : elle se trouve à l'intérieur du namespace r1. Les autres règles présentes dans ce namespace peuvent cependant continuer à s'appliquer.

### 8.2 Tester les paquets

Le petit paquet doit continuer à fonctionner :

```bash
sudo ip netns exec h1 ping -4 -M do -s 1200 -c 2 198.51.100.10
```

Le paquet supérieur à 1300 octets :

```bash
sudo ip netns exec h1 ping -4 -M do -s 1273 -c 3 198.51.100.10
```

Avec l'erreur ICMP bloquée, le grand paquet devrait expirer sans explication claire. Capture simultanément sur le routeur et le client pour confirmer le comportement : le paquet arrive à r1, mais l'indication d'erreur ne parvient pas à h1.

### 8.3 Supprimer le filtre et retester

```bash
sudo ip netns exec r1 nft delete table inet labmtu
sudo ip netns exec r1 nft list ruleset
```

Refais le test de 1273 octets. Une fois le retour ICMP autorisé, l'erreur de MTU devrait à nouveau être visible au client, à moins que son état PMTU ou un autre élément de la maquette ait déjà évolué. Au besoin, reconstruis la topologie de test puis recommence.

### Analyse

Le symptôme n'est pas nécessairement une panne complète. Les flux petits ou interactifs peuvent fonctionner, alors que les gros transferts échouent. Un navigateur peut établir une connexion puis rester bloqué au chargement d'un contenu volumineux ; un tunnel peut sembler établi mais transporter certains flux de façon dégradée.

**À rendre :** captures avant/après blocage ICMP, différence entre petit et grand ping, et explication du black hole.


## 9. TP 5 — Découverte MTU en IPv6

**Niveau :** avancé

IPv6 doit être traité séparément d'IPv4. Un routeur IPv6 intermédiaire ne fragmente pas les paquets : il transmet un message ICMPv6 Packet Too Big si la taille dépasse le MTU de sortie et si le mécanisme fonctionne.

### 9.1 Tester sous la MTU de 1300

```bash
sudo ip netns exec h1 ping -6 -M do -s 1200 -c 3 2001:db8:20::10
```

### 9.2 Tester à 1300 octets

```bash
sudo ip netns exec h1 ping -6 -M do -s 1252 -c 3 2001:db8:20::10
```

Taille théorique : `1252 + 40 octets IPv6 + 8 octets ICMPv6 = 1300`.

### 9.3 Dépasser la MTU

```bash
sudo ip netns exec h1 ping -6 -M do -s 1253 -c 2 2001:db8:20::10
```

Taille théorique : 1301 octets. Le routeur r1 ne fragmente pas le paquet en transit. Il devrait retourner un ICMPv6 Packet Too Big vers h1.

### 9.4 Capturer ICMPv6

```bash
sudo ip netns exec r1 tcpdump -ni any 'icmp6'
```

Le message Packet Too Big est généré par r1 puis envoyé en direction de h1 ; il ne sort donc pas normalement sur l'interface `r1-h2`. La capture `any` permet d'observer l'arrivée du paquet sur `r1-h1` et le retour ICMPv6 sur cette interface.

Et dans Wireshark, filtre l'affichage avec :

```text
icmpv6.type == 2
```

### Questions

- Quelle différence fondamentale sépare la fragmentation IPv4 de la découverte MTU IPv6 ?
- Pourquoi un pare-feu IPv6 ne doit-il pas bloquer aveuglément tous les messages ICMPv6 ?
- Quelle taille de paquet est testée quand `ping -6 -s 1253` est utilisé dans ce laboratoire ?


## 10. TP 6 — MTU, interface de tunnel et overhead d'encapsulation

**Niveau :** intermédiaire → expert

Les tunnels ajoutent des en-têtes autour du paquet interne. Si un paquet interne approche déjà la MTU du lien underlay, le paquet encapsulé peut dépasser la MTU du transport. Le tunnel peut alors fragmenter selon le mécanisme utilisé, réduire sa MTU effective, dépendre de PMTUD ou perdre certains paquets.

### 10.1 Principe de calcul

Une approximation utile est :

`MTU intérieure utilisable ≈ MTU underlay − overhead d'encapsulation pertinent`

L'overhead exact dépend du protocole, du mode, d'IPv4 ou IPv6 outer, des options, de la protection cryptographique, du NAT-T et d'autres détails. Il faut calculer avec la technologie réellement utilisée, puis mesurer. Ne réutilise pas une valeur générique d'IPsec ou de VXLAN comme si elle s'appliquait à toutes les implémentations.

### 10.2 Exemple VXLAN pédagogique

Pour VXLAN avec underlay Ethernet/IP standard, l'encapsulation courante comprend un en-tête IP externe, UDP, VXLAN et un en-tête Ethernet interne avant le paquet IP interne. Avec outer IPv4 sans options, cela représente typiquement 20 + 8 + 8 + 14 = 50 octets d'overhead au-dessus du paquet IP interne si l'underlay MTU compte le paquet IP externe. Une underlay MTU de 1500 peut donc conduire à une MTU IP intérieure d'environ 1450 octets dans ce scénario simple.

Avec outer IPv6, les 40 octets d'en-tête IPv6 externe remplacent les 20 octets IPv4, ce qui augmente l'overhead dans ce calcul. Les détails d'implémentation et le chemin physique doivent toujours être vérifiés.

Pour GRE, IPsec, WireGuard, PPPoE et d'autres tunnels, calcule l'overhead selon le mode exact et les en-têtes réellement ajoutés. Le chiffre n'est pas universel.

### 10.3 Manipulation dans le laboratoire

1. Vérifie les MTU du lien et des interfaces de tunnel si le simulateur en fournit.
2. Teste un paquet de petite taille puis augmente progressivement la taille.
3. Capture à l'entrée du tunnel et à la sortie underlay, si l'outil le permet.
4. Compare la taille interne avec la taille externe encapsulée.
5. Vérifie la MTU configurée du tunnel et les messages PMTUD qui doivent atteindre la source.
6. Ne réduis la MTU interne qu'après avoir établi le calcul et observé le comportement.

Commandes Linux possibles :

```bash
ip -d link show
ip link show dev INTERFACE_TUNNEL
tracepath -n DESTINATION
```

Remplace les valeurs symboliques par les interfaces réellement utilisées. La commande disponible et les informations de PMTU varient selon le tunnel et la version.


## 11. TP 7 — MSS clamping : utile, mais pas une solution universelle

**Niveau :** avancé

Quand une connexion TCP traverse un tunnel qui réduit la MTU effective, un réglage MSS cohérent peut éviter que les hôtes n'envoient des segments TCP trop volumineux pour le chemin. Cette technique est souvent appelée **MSS clamping**.

### Ce qu'il faut comprendre

- Le MSS est annoncé dans les options des paquets TCP SYN/SYN-ACK.
- Il représente la quantité maximale de données TCP que le pair souhaite recevoir dans un segment, selon les règles TCP et les en-têtes pris en compte.
- Le clamp modifie le MSS annoncé ou transmis dans certaines directions, selon la fonction de pare-feu/routeur utilisée.
- Il concerne TCP ; il ne corrige pas directement UDP, QUIC, ICMP, DNS sur UDP ou d'autres protocoles non TCP.
- Il peut masquer une mauvaise conception MTU sans supprimer le problème pour les flux non TCP.

### Exercice de conception

Suppose que le chemin intérieur utile soit estimé à 1400 octets. Pour des en-têtes IPv4 et TCP de base, l'estimation théorique du MSS est de 1360 octets (`1400 - 20 - 20`). Pour IPv6 et TCP de base, elle est de 1340 (`1400 - 40 - 20`). Ces estimations doivent tenir compte de la configuration réelle, des options et de l'encapsulation.

Propose ensuite un plan de validation :

1. capture les SYN et SYN-ACK avant modification ;
2. relève les MSS annoncés ;
3. effectue un transfert TCP de laboratoire représentatif ;
4. vérifie le comportement après application d'un clamp adapté à la plateforme ;
5. teste aussi UDP et IPv6, afin de prouver les limites du correctif ;
6. documente pourquoi le réglage existe et dans quelles conditions il doit être revu.

Ne copie pas de règle MSS provenant d'un autre réseau sans connaître la PMTU réelle et le contexte des deux extrémités.


## 12. TP 8 — Problème MTU avec transfert TCP applicatif

**Niveau :** avancé

Le ping est un outil de diagnostic, pas une représentation parfaite de tous les flux. Un chemin peut traiter les pings différemment des flux TCP ou UDP selon les règles de filtrage, les politiques et la manière dont les hôtes génèrent les paquets.

### Scénario

Les petits pings entre les deux hôtes réussissent, mais un transfert de fichier ou un échange HTTPS semble se bloquer après le début de la session.

### Procédure

1. Vérifie la connectivité de base et la résolution DNS séparément.
2. Capture les SYN/SYN-ACK et note le MSS échangé.
3. Observe si de gros segments TCP sont retransmis.
4. Vérifie la taille du paquet IP et les messages ICMP associés.
5. Confirme la MTU des interfaces de tunnel ou des overlays éventuels.
6. Compare avec un transfert utilisant une charge différente si l'application de test le permet.
7. Examine si le problème se produit sur un seul chemin ou uniquement quand un transport spécifique est sélectionné.

### Interprétation

- Une poignée de main TCP réussie ne prouve pas que les segments de données volumineux passent.
- Des retransmissions TCP ne prouvent pas à elles seules une MTU erronée : elles peuvent aussi venir de congestion, de perte ou de filtrage.
- Le blocage des messages ICMP de PMTUD peut être une cause, mais il faut le confirmer avec une capture et des tests de taille.
- Si seuls les flux TCP sont affectés, un problème de MSS ou de PMTUD TCP est plausible, mais pas automatiquement démontré.

**À rendre :** capture annotée, MSS observé et différence entre le trafic de contrôle TCP et le trafic de données.


## 13. TP 9 — Dépanner depuis un routeur Cisco

**Niveau :** intermédiaire → expert

Dans un simulateur Cisco ou un routeur de laboratoire, utilise les commandes disponibles pour la version de l'OS.

### Vérifier les MTU et les interfaces

```text
show interfaces
show ip interface
show interfaces tunnel
show ip route
```

Dans la sortie de `show interfaces`, recherche notamment la MTU d'interface, les erreurs, les drops et l'état physique/logique. Les compteurs ne sont pas tous spécifiques au MTU, et leur interprétation doit être faite dans le contexte de l'équipement.

### Effectuer un ping étendu

Sur IOS/IOS XE, selon la plateforme, le ping étendu interactif permet de choisir la destination, la taille du datagramme et le bit DF. Utilise l'aide CLI et le guide de ta version pour la syntaxe exacte. L'objectif est de faire varier une taille de paquet connue, tout en demandant de ne pas fragmenter, puis de comparer le résultat à une taille inférieure.

Ne suppose pas que l'argument « taille » d'un ping interactif Cisco est défini comme le `-s` de Linux : vérifie ce que la commande de l'OS compte exactement.

### Contrôler le filtrage ICMP

```text
show access-lists
show ip interface
show logging
```

Cherche un filtrage de messages ICMP utiles au diagnostic et à PMTUD. Évite la règle simpliste « autoriser tous les ICMP sans condition » ou l'inverse « bloquer tous les ICMP ». Une politique sûre doit autoriser les messages nécessaires au fonctionnement attendu, avec la portée et les protections adaptées.

### Exercice

Construis un trajet avec une MTU réduite sur un lien ou une interface de tunnel. Observe ce qui arrive au ping DF lorsque la taille dépasse la limite. Répète la mesure avec un paquet plus petit puis explique les résultats. Enregistre les commandes exécutées, la MTU réelle et le type de message observé.


## 14. TP 10 — Chemins alternatifs et MTU incohérente

**Niveau :** expert

Deux chemins peuvent être joignables mais ne pas avoir la même PMTU. Cela peut se produire avec ECMP, SD-WAN, VPN multipath, chemins Internet distincts, circuits opérateur ou bascule automatique.

### Scénario

- Chemin A : PMTU 1500 ;
- Chemin B : PMTU 1300 ;
- une politique de routage peut faire varier le chemin pour une destination ou une classe de flux.

Un ping volumineux fonctionne sur A et échoue sur B. Si le trafic change de chemin en cours de diagnostic, les résultats peuvent sembler intermittents.

### Méthode

1. Mesure la taille maximale sur chacun des chemins séparément si tu peux les forcer dans le laboratoire.
2. Note l'interface de sortie et le prochain saut pour chaque test.
3. Capture l'erreur ICMP sur le chemin B.
4. Force une bascule contrôlée, puis répète le test.
5. Vérifie si la PMTU apprise est associée au chemin attendu et si les flux peuvent emprunter des chemins de tailles différentes.
6. Propose une politique de conception : uniformiser le MTU, conserver un MTU intérieur suffisamment conservateur, ou utiliser des mécanismes de découverte et de vérification compatibles avec la plateforme.

### Questions

- Pourquoi un seul test réussi sur le chemin A ne prouve-t-il pas que le chemin B accepte la même taille ?
- Quels risques posent les chemins multiples avec des PMTU différentes ?
- Pourquoi faut-il corréler les mesures MTU aux transports, aux routes et aux politiques effectives ?


## 15. TP 11 — Plan de dépannage des symptômes typiques

| Symptôme | Première hypothèse MTU à tester | Contrôles complémentaires |
|---|---|---|
| Petits pings OK, gros pings échouent | Limite MTU ou PMTUD | DF, ICMP frag-needed, capture des deux côtés |
| Ping normal OK, HTTPS se bloque à l'envoi de données | PMTUD/MSS possible | SYN/SYN-ACK, MSS, retransmissions, ICMP |
| Un VPN est établi, mais certains flux échouent | MTU intérieure trop élevée | MTU underlay, overhead du tunnel, test par tailles |
| IPv4 fonctionne, IPv6 bloque sur gros paquets | ICMPv6 Packet Too Big filtré ou MTU IPv6 | Capture ICMPv6, MTU des interfaces, route retour |
| UDP ou QUIC dégradé, TCP semble fonctionner | Taille datagramme/PLPMTUD spécifique au protocole | Capture UDP, tailles des datagrammes, comportement applicatif |
| Un seul chemin ECMP échoue aux grandes tailles | PMTU différente entre chemins | Forcer le chemin, comparer interface et next-hop |
| Tout le trafic échoue | Cause probablement plus large que MTU seule | Lien, routage, ACL, service et adressage |
| Des transferts volumineux sont lents plutôt que totalement bloqués | Retransmissions, fragmentation ou congestion | Stats TCP, drops, queue, MTU, charge du lien |

Le MTU est une hypothèse à tester, pas une explication universelle de tous les problèmes de gros paquets.


## 16. Arbre de décision MTU

```text
Les petits paquets passent-ils ?
        | non                              | oui
        v                                  v
Vérifier d'abord la connectivité      Tester des tailles croissantes
et le routage de base                       |
                                           v
                         Paquet au-dessus de la limite échoue ?
                                | oui                 | non
                                v                     v
                 Un ICMP frag-needed/PTB revient ?   Tester le vrai flux applicatif
                       | oui          | non
                       v              v
              PMTU détectée        Suspicion de PMTU black hole,
              ou autre limite     filtrage ICMP ou autre perte silencieuse
                       |              |
                       +-------> Capturer aux deux extrémités
                                      |
                                      v
                     Comparer MTU interface, tunnel, route,
                     message d'erreur, chemin aller et retour
```


## 17. Procédure de diagnostic réutilisable

Quand un ticket mentionne une panne qui ressemble à un problème MTU, suis les étapes ci-dessous et conserve les preuves.

### A. Définir le flux

Noter source, destination, protocole, port, famille IP, application et chemin sélectionné. Définir si le problème est permanent, intermittent ou associé à une bascule.

### B. Capturer l'état initial

```bash
ip -br address
ip route show table all
ip -d link show
ip neigh show
```

Pour IPv6, compléter avec :

```bash
ip -6 address show
ip -6 route show table all
ip -6 neigh show
```

### C. Tester la taille

Commence par les petits paquets, puis augmente progressivement la taille. Utilise DF lorsque tu veux vérifier une limite sans fragmentation IPv4. Note la taille de données demandée, puis calcule la taille IP totale.

### D. Capturer le message attendu

Capture les requêtes et les erreurs ICMP/ICMPv6 sur le routeur ou les extrémités. Si le message ne revient pas, cherche à quel point il est perdu. Ne conclus pas automatiquement que l'ICMP est filtré sans preuve.

### E. Corriger la bonne couche

Selon le résultat, la correction peut concerner l'underlay, le MTU du tunnel, le filtrage des messages ICMP utiles, la taille des segments TCP ou un mécanisme de découverte supporté. La solution dépend de la technologie précise.

### F. Tester le trafic réel

Après correction, valide le protocole de l'application, un transfert représentatif, les deux directions, IPv4/IPv6 si utilisé, les chemins alternatifs et les mécanismes de sécurité.


## 18. Nettoyage du laboratoire

Supprime uniquement les namespaces créés pour ce cahier :

```bash
sudo ip netns del h1 2>/dev/null || true
sudo ip netns del r1 2>/dev/null || true
sudo ip netns del h2 2>/dev/null || true
```

La suppression d'un namespace supprime les interfaces qui lui sont attachées. La table nftables `inet labmtu` disparaît avec le namespace r1 ; si tu l'as créée dans un autre espace de noms par erreur, supprime-la uniquement après avoir identifié le contexte qui la contient. Ne lance pas les commandes de nettoyage si les noms sont réutilisés par un autre exercice.


## 19. Modèle de compte rendu

```text
TP / incident :
Date et environnement :
Noyau / iproute2 / OS réseau :
Source et destination :
Protocole et famille IP :
MTU source :
MTU(s) du chemin :
MTU du tunnel, le cas échéant :
Taille du paquet testé :
Calcul de taille IP totale :
Résultat avec petite taille :
Résultat avec grande taille :
DF activé ou non :
ICMP frag-needed / ICMPv6 PTB observé :
Résultats de capture :
Cause racine prouvée :
Correction appliquée :
Tests de non-régression :
Limites / risques restants :
```

### Barème suggéré sur 20

- 4 points : topologie et MTU des interfaces correctement relevées ;
- 4 points : calcul correct des tailles et distinction MTU/MSS ;
- 4 points : message ICMP ou absence de message correctement interprété ;
- 4 points : cause reproduite puis correction validée ;
- 4 points : rapport, capture et tests de non-régression.


## 20. Erreurs fréquentes à éviter

1. **Déduire qu'un chemin accepte 1500 octets parce qu'un ping normal fonctionne.** Le ping par défaut est généralement bien plus petit.
2. **Confondre la charge `ping -s` avec la taille totale du paquet IP.** Il faut ajouter les en-têtes IP et ICMP appropriés.
3. **Diminuer la MTU au hasard.** Commence par mesurer et localiser la limite.
4. **Bloquer tous les messages ICMP.** Certains sont nécessaires à PMTUD et à d'autres mécanismes réseau.
5. **Croire que les routeurs IPv6 fragmentent les paquets en transit.** Ils envoient un message Packet Too Big ; la source doit s'adapter.
6. **Confondre MTU et MSS.** Le MSS concerne les données TCP par segment, pas la taille complète de tout paquet IP.
7. **Utiliser MSS clamping comme solution à tous les protocoles.** Il ne couvre pas UDP, QUIC, ICMP et les autres flux non TCP.
8. **Oublier l'overhead des tunnels.** Le MTU interne peut être inférieur au MTU de l'underlay.
9. **Ne tester que le chemin aller.** Les messages de découverte et les réponses nécessitent un retour fonctionnel.
10. **Ignorer les chemins multiples.** Un autre transport peut avoir une PMTU différente.
11. **Appliquer un calcul VXLAN/IPsec universel.** L'overhead dépend du mode et des options réels.
12. **Ne pas nettoyer les règles temporaires.** Une règle de test laissée en place peut fausser les prochains laboratoires.
13. **Conclure que toute retransmission TCP prouve une panne MTU.** La congestion, les drops et les problèmes de service doivent aussi être exclus.


## 21. Références techniques

1. [RFC 1191 — Path MTU Discovery pour IPv4](https://www.rfc-editor.org/rfc/rfc1191.html) : mécanisme de découverte MTU de chemin IPv4 et messages ICMP associés.
2. [RFC 8201 — Path MTU Discovery pour IPv6](https://www.rfc-editor.org/rfc/rfc8201.html) : fonctionnement et considérations de découverte PMTU en IPv6.
3. [RFC 4821 — Packetization Layer Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc4821.html) : découverte au niveau de la couche de paquetisation, sans dépendre uniquement des messages ICMP.
4. [RFC 8899 — PLPMTUD pour les transports datagrammes](https://www.rfc-editor.org/rfc/rfc8899.html) : approche de découverte PMTU au niveau transport/couche de paquetisation pour les datagrammes.
5. [Linux `ping(8)`](https://man7.org/linux/man-pages/man8/ping.8.html) : options `-s` et `-M` et comportement de l'outil.
6. [Documentation du noyau Linux — paramètres IP](https://docs.kernel.org/networking/ip-sysctl.html) : notamment `tcp_mtu_probing` pour l'implémentation Linux de mécanismes de découverte MTU côté TCP.

Les RFC décrivent les mécanismes protocolaires. La syntaxe des commandes, le comportement des tunnels et les fonctions de PMTUD ou PLPMTUD dépendent de l'implémentation et de la version. Consulte aussi la documentation spécifique du routeur, du pare-feu, du VPN ou de l'overlay réellement utilisé.


## Conclusion

Le diagnostic MTU repose sur une idée simple : un paquet peut être valide pour l'interface source et néanmoins dépasser la capacité d'un lien situé plus loin sur son chemin. Les petits pings peuvent réussir alors que de gros paquets échouent. En IPv4, le bit DF et les messages ICMP « fragmentation nécessaire » permettent de mettre en évidence la limite ; en IPv6, les messages ICMPv6 Packet Too Big sont essentiels car les routeurs intermédiaires ne fragmentent pas les paquets.

Une démarche robuste mesure la taille, identifie le lien limitant, capture le message d'erreur, vérifie le chemin retour, examine l'overhead d'encapsulation et teste le trafic réel après correction. L'objectif n'est pas seulement de faire réussir un ping, mais de démontrer que la PMTU est cohérente pour les applications et les chemins utilisés.
