# Routage IP — Décision, tables et chemins (CCNA / Admin Réseau)

> **Objectif** : comprendre comment un routeur choisit un chemin, comment lire une table de routage, configurer des routes statiques et flottantes, vérifier le plan de contrôle et le plan de données, et diagnostiquer les pannes de routage les plus fréquentes. Le cours couvre IPv4 et les bases IPv6, Cisco IOS et Linux.

---

## 1. Routage : le problème à résoudre

Un hôte veut joindre un réseau distant. Il compare l'adresse destination à son propre subnet :

- même subnet → envoi direct en L2 (ARP) ;
- subnet différent → envoi à la **passerelle par défaut**.

Le routeur reçoit le paquet, retire l'en-tête L2, examine l'adresse IP destination, cherche la meilleure route, puis réécrit l'en-tête L2 pour le prochain saut.

```text
PC 10.10.1.10/24 ---- R1 ---- R2 ---- Serveur 10.20.2.20/24
      |                  |        |
   passerelle        route vers   route vers
   10.10.1.1          10.20.2.0   10.20.2.0
```

Le routage est **hop-by-hop** : chaque routeur ne connaît que le prochain saut, pas le chemin complet. La boucle de routage est un risque réel ; le TTL la limite.

---

## 2. Plan de contrôle et plan de données

| Plan | Rôle | Exemples |
|---|---|---|
| Contrôle | Apprend et choisit les routes | OSPF, BGP, statique, ARP |
| Données | Transfère les paquets | CEF, FIB, ASIC |
| Management | Administration | SSH, SNMP, syslog |

Sur Cisco, le **RIB** (Routing Information Base) est la table `show ip route`. Le **FIB** (Forwarding Information Base) est la table CEF utilisée pour le forwarding. Une route peut être dans le RIB mais pas dans le FIB si le next-hop est inaccessible.

```cisco
show ip route
show ip cef
show ip cef 10.20.2.20
show adjacency
```

Sous Linux, le kernel maintient une table de routage et une table ARP/voisin. `ip route` lit la table principale.

---

## 3. Lire une table de routage

```text
R1# show ip route
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override

Gateway of last resort is 203.0.113.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 203.0.113.1
      10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks
C       10.10.1.0/24 is directly connected, GigabitEthernet0/0
L       10.10.1.1/32 is directly connected, GigabitEthernet0/0
O       10.20.2.0/24 [110/2] via 10.10.1.2, 00:12:34, GigabitEthernet0/0
S       10.30.0.0/16 [1/0] via 10.10.1.3
```

Chaque ligne contient :

- **code** : origine de la route ;
- **préfixe/masque** ;
- **[distance administrative/métrique]** ;
- **next-hop** et interface de sortie ;
- **âge** et source pour les protocoles dynamiques.

### 3.1 Longest Prefix Match

Le routeur choisit toujours la route la plus **spécifique**, c'est-à-dire le plus long préfixe, avant de comparer les distances administratives.

```text
Destination 10.20.2.20
Routes :
  10.0.0.0/8      via A
  10.20.0.0/16    via B
  10.20.2.0/24    via C
  0.0.0.0/0       via D

Choix : 10.20.2.0/24 via C (préfixe le plus long).
```

C'est pourquoi une route plus spécifique gagne même si sa distance administrative est plus élevée. Une route host `/32` est la plus spécifique possible.

### 3.2 Distance administrative

Quand plusieurs sources proposent **exactement le même préfixe**, la plus faible distance administrative gagne.

| Source | AD Cisco | Remarques |
|---|---:|---|
| Connectée | 0 | Toujours préférée |
| Statique | 1 | Peut être modifiée |
| eBGP | 20 | |
| EIGRP interne | 90 | |
| OSPF | 110 | |
| IS-IS | 115 | |
| RIP | 120 | |
| EIGRP externe | 170 | |
| iBGP | 200 | |
| Inconnue | 255 | Jamais installée |

Une route statique flottante utilise une AD plus élevée pour servir de secours.

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1
ip route 0.0.0.0 0.0.0.0 203.0.113.2 250
```

### 3.3 Métrique

À l'intérieur d'une même source, la métrique départage les chemins. OSPF utilise le coût, EIGRP une métrique composite, BGP une sélection d'attributs. Une métrique plus faible est généralement meilleure, mais chaque protocole a ses règles.

---

## 4. Routes connectées, locales et statiques

### 4.1 Routes connectées

Quand une interface a une IP et est `up/up`, le routeur installe :

- une route **connected** pour le subnet (`C`) ;
- une route **local** pour l'IP de l'interface (`L`, /32).

```cisco
interface Gi0/0
 ip address 10.10.1.1 255.255.255.0
 no shutdown
```

```text
C 10.10.1.0/24 is directly connected, Gi0/0
L 10.10.1.1/32 is directly connected, Gi0/0
```

La route locale sert à recevoir le trafic destiné au routeur lui-même.

### 4.2 Route statique simple

```cisco
ip route 10.20.2.0 255.255.255.0 10.10.1.2
```

ou en notation CIDR :

```cisco
ip route 10.20.2.0/24 10.10.1.2
```

Une route statique peut pointer vers :

- une **IP next-hop** : le routeur résout l'ARP ;
- une **interface de sortie** : utile pour les liens point-to-point ;
- les deux : recommandé pour éviter les problèmes de résolution.

### 4.3 Route par défaut

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

La route par défaut est utilisée quand aucune route plus spécifique ne correspond. Sur un routeur de bordure, elle pointe vers le FAI. Sur un routeur interne, elle peut pointer vers le cœur.

### 4.4 Route flottante

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1
ip route 0.0.0.0 0.0.0.0 203.0.113.2 250
```

La seconde route n'est installée que si la première disparaît. C'est une solution simple de secours, mais elle ne teste pas la connectivité réelle du next-hop.

### 4.5 Route statique avec tracking

```cisco
ip sla 1
 icmp-echo 203.0.113.1 source-interface Gi0/0
 frequency 5
ip sla schedule 1 life forever start-time now
track 1 ip sla 1 reachability
ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 1
ip route 0.0.0.0 0.0.0.0 203.0.113.2 250
```

Le tracking vérifie la reachability et retire la route si le next-hop ne répond plus.

---

## 5. Routage et ARP

Pour envoyer un paquet vers un next-hop, le routeur doit connaître la MAC du next-hop. Il utilise ARP (IPv4) ou NDP (IPv6).

```text
R1 veut envoyer à 10.20.2.20 via 10.10.1.2.
1. R1 consulte sa table : next-hop 10.10.1.2.
2. R1 cherche 10.10.1.2 dans son cache ARP.
3. Si absent, ARP request broadcast "Qui a 10.10.1.2 ?".
4. R2 répond avec sa MAC.
5. R1 encapsule la trame et l'envoie.
```

Commandes :

```cisco
show arp
show ip arp 10.10.1.2
clear arp-cache
debug arp
```

```bash
ip neigh show
ip neigh show 10.10.1.2
ip neigh flush all
arping -I eth0 10.10.1.2
```

Un next-hop non résolu provoque une route inactive ou des paquets jetés. Vérifier le VLAN, le lien et l'ARP.

---

## 6. CEF et vérification du forwarding

Cisco Express Forwarding (CEF) préconstruit le FIB et les adjacences. Il est activé par défaut sur les plateformes modernes.

```cisco
show ip cef
show ip cef 10.20.2.20
show ip cef 10.20.2.20 detail
show adjacency
show adjacency detail
```

Une entrée CEF peut être `receive`, `drop`, `punt` ou `attach`. Un `drop` indique une route nulle ou une politique. Un `punt` signifie que le paquet remonte au CPU (ACL, NAT, etc.), ce qui peut limiter le débit.

Sous Linux, le forwarding est contrôlé par :

```bash
sysctl net.ipv4.ip_forward
sysctl -w net.ipv4.ip_forward=1
```

Pour le rendre persistant :

```bash
echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/99-forwarding.conf
sysctl --system
```

---

## 7. Routage Linux

### 7.1 Commandes de base

```bash
ip route show
ip route show table main
ip route get 10.20.2.20
ip route add 10.20.2.0/24 via 10.10.1.2 dev eth0
ip route add default via 203.0.113.1
ip route del 10.20.2.0/24
ip route replace 10.20.2.0/24 via 10.10.1.3
```

`ip route get` indique la route utilisée et l'interface de sortie :

```bash
$ ip route get 10.20.2.20
10.20.2.20 via 10.10.1.2 dev eth0 src 10.10.1.1 uid 0
    cache
```

### 7.2 Tables et règles

Linux supporte plusieurs tables de routage et des règles policy-based.

```bash
ip rule show
ip rule add from 10.10.1.0/24 table 100
ip route add default via 10.10.1.254 table 100
ip route show table 100
```

C'est utile pour du multi-homing, du split tunneling ou des VRFs.

### 7.3 Vérification

```bash
ip -br addr
ip route
ip neigh
ping -c 4 10.20.2.20
traceroute 10.20.2.20
mtr -rw 10.20.2.20
tcpdump -eni eth0 icmp
```

### 7.4 Routage et nftables

Pour router entre deux interfaces, le forwarding doit être activé et le firewall doit l'autoriser.

```bash
nft add table inet filter
nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'
nft add rule inet filter forward ct state established,related accept
nft add rule inet filter forward iif eth0 oif eth1 ip saddr 10.10.1.0/24 accept
nft list ruleset
```

---

## 8. Routage dynamique : vue d'ensemble

| Protocole | Type | Métrique | Convergence | Usage |
|---|---|---|---|---|
| RIP | Distance-vector | Sauts | Lente | Historique |
| OSPF | Link-state | Coût | Rapide | Entreprise |
| EIGRP | Hybride | Composite | Très rapide | Cisco |
| IS-IS | Link-state | Coût | Rapide | FAI/datacenter |
| BGP | Path-vector | Attributs | Contrôlée | Internet |

Le choix dépend de l'échelle, de la topologie, de l'interopérabilité et des besoins de politique. OSPF est le standard en entreprise ; BGP est indispensable pour Internet et les grandes architectures.

---

## 9. Routage redondant et défaillances

### 9.1 ECMP

Le routage multi-chemin à coût égal (ECMP) installe plusieurs next-hops pour le même préfixe. Le trafic est réparti par hachage (souvent 5-tuple).

```cisco
show ip route 10.20.2.0
show ip cef 10.20.2.0
```

Sous Linux :

```bash
ip route add 10.20.2.0/24 \
  nexthop via 10.10.1.2 dev eth0 weight 1 \
  nexthop via 10.10.1.3 dev eth1 weight 1
```

Un seul flux reste sur un seul chemin ; ECMP n'agrège pas la bande passante d'une connexion TCP.

### 9.2 Routage asymétrique

Le retour peut emprunter un autre chemin que l'aller. C'est souvent acceptable, mais pose problème avec les firewalls stateful, NAT et certains mécanismes de sécurité.

```text
PC -> R1 -> R2 -> Serveur
Serveur -> R3 -> R1 -> PC
```

Diagnostic : `traceroute` dans les deux sens, `tcpdump` sur les interfaces, vérifier les routes de retour.

### 9.3 Blackhole et route nulle

```cisco
ip route 10.99.0.0 255.255.0.0 Null0
```

La route nulle jette le trafic. Elle sert à bloquer un préfixe ou à éviter une boucle. Sous Linux :

```bash
ip route add blackhole 10.99.0.0/16
```

---

## 10. Dépannage du routage

### 10.1 Méthode

1. Vérifier le lien et l'adressage (`show ip interface brief`, `ip addr`).
2. Vérifier la route sur le routeur source (`show ip route <dest>`).
3. Vérifier le next-hop et l'ARP (`show arp`).
4. Vérifier la route de retour sur le destinataire.
5. Vérifier les ACL/firewalls/NAT.
6. Capturer le trafic aux deux extrémités.

### 10.2 Le ping échoue dans un sens

Cause probable : route de retour absente. Le routeur distant ne sait pas revenir vers le subnet source.

```cisco
show ip route 10.10.1.0
show ip route 10.20.2.0
```

### 10.3 Le ping fonctionne, pas le TCP

Le routage IP est bon, mais un firewall, une ACL ou un NAT bloque le port. Tester avec `telnet`, `nc`, `curl`.

```bash
nc -vz 10.20.2.20 443
curl -vk https://10.20.2.20/
```

### 10.4 MTU et fragmentation

Un ping de 1500 octets passe, un gros transfert échoue : suspecter le MTU. Tester :

```bash
ping -M do -s 1472 10.20.2.20
ping -M do -s 1473 10.20.2.20
```

Sur Cisco :

```cisco
ping 10.20.2.20 size 1500 df-bit
```

### 10.5 Boucle de routage

Le TTL décrémente et le paquet est jeté. `traceroute` montre une répétition d'adresses. Vérifier les routes statiques et les protocoles.

```bash
traceroute -n 10.20.2.20
mtr -rw 10.20.2.20
```

### 10.6 Cas réel : route par défaut manquante

Un switch L3 a des routes connectées mais pas de route par défaut. Les postes joignent les VLANs locaux mais pas Internet. `show ip route` ne montre pas de `S* 0.0.0.0/0`. Ajout :

```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

### 10.7 Cas réel : route flottante qui ne bascule pas

La route principale pointe vers un next-hop qui ne répond plus, mais le lien physique reste `up`. La route flottante ne s'active pas. Solution : utiliser IP SLA tracking, ou un protocole dynamique.

### 10.8 Cas réel : deux routes identiques, trafic intermittent

Deux routes statiques vers le même préfixe avec des next-hops différents sont installées ; le trafic alterne. Si un next-hop est mauvais, la connectivité est intermittente. Vérifier `show ip route` et supprimer la route incorrecte.

---

## 11. Laboratoire

1. Configurer deux routeurs et deux réseaux, vérifier le ping de bout en bout.
2. Ajouter une route statique de retour et observer la différence.
3. Configurer une route flottante et couper le lien principal.
4. Mettre en place IP SLA tracking et couper le next-hop sans couper le lien.
5. Configurer ECMP sous Linux et vérifier avec `ip route get`.
6. Capturer un ARP et expliquer la résolution du next-hop.

---

## 12. Mémo

```cisco
show ip route
show ip route 10.20.2.0
show ip route summary
show ip cef 10.20.2.20
show ip interface brief
show arp
show ip protocols
ping 10.20.2.20 source Gi0/0
traceroute 10.20.2.20
```

```bash
ip route show
ip route get 10.20.2.20
ip neigh show
sysctl net.ipv4.ip_forward
traceroute -n 10.20.2.20
mtr -rw 10.20.2.20
tcpdump -eni eth0 icmp
```

---

## 13. Points clés

- Le routeur choisit la route au préfixe le plus long, puis la distance administrative, puis la métrique.
- Une route connectée est toujours préférée ; une route locale /32 sert à recevoir le trafic du routeur.
- Une route statique flottante ne bascule que si la route principale disparaît ; le tracking est plus fiable.
- Le next-hop doit être résolu par ARP/NDP, sinon la route est inutilisable.
- CEF sépare le RIB du FIB ; `show ip cef` montre le forwarding réel.
- Sous Linux, `ip route get` est l'outil de diagnostic central.
- Une panne de routage se diagnostique dans les deux sens : aller et retour.
- ECMP répartit les flux, mais ne multiplie pas le débit d'un seul flux TCP.

> **Exercice** : un poste 10.10.1.10/24 joint 10.20.2.20 mais le serveur ne peut pas répondre. Que vérifier en premier ? Réponse : la route de retour vers 10.10.1.0/24 sur le routeur du serveur, puis l'ARP et les ACL.

---

## 14. Étude de cas : refonte du routage d'un site

Un site possède un routeur de bordure, deux switches de cœur L3 et plusieurs VLANs. Le routage actuel mélange des routes statiques et un ancien protocole. Les utilisateurs signalent des lenteurs et des coupures lors des bascules.

**Audit.** Relever la table de routage complète, les routes par défaut, les next-hops, les AD et les métriques. Identifier les routes statiques orphelines et les chemins asymétriques. Vérifier les ARP et les interfaces.

```cisco
show ip route
show ip route summary
show ip cef
show ip protocols
show arp
```

**Conception.** Définir un plan simple : routes connectées, une route par défaut vers le bordure, un protocole dynamique interne (OSPF) pour les VLANs et les liens redondants, des résumés aux frontières. Documenter les flux qui nécessitent des routes statiques.

**Mise en œuvre.** Configurer OSPF sur les liens de transit, garder les LAN en passive interface, annoncer les préfixes de manière explicite. Conserver temporairement les routes statiques avec une distance administrative plus élevée pour le secours. Vérifier après chaque changement.

```cisco
router ospf 1
 router-id 10.255.0.1
 network 10.0.0.0 0.255.255.255 area 0
 passive-interface default
 no passive-interface Gi0/1
!
ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

**Validation.** Tester la connectivité de chaque VLAN, la bascule d'un lien, la route de retour, et la convergence. Comparer `show ip route` avant/après. Vérifier les logs et les compteurs.

```bash
ping -c 4 10.20.2.20
traceroute -n 10.20.2.20
mtr -rw 10.20.2.20
```

### 14.1 Erreurs à éviter

- annoncer une route par défaut sans que le bordure ait une route valide ;
- laisser des routes statiques concurrentes avec le protocole dynamique ;
- oublier les passive interfaces ;
- modifier la référence de bande passante d'un seul routeur ;
- ignorer le retour pour les flux NAT ;
- tester seulement depuis un poste, pas depuis chaque VLAN.

### 14.2 Check-list

```text
[ ] Table de routage documentée
[ ] Routes par défaut vérifiées
[ ] Next-hops reachables
[ ] ARP/NDP résolus
[ ] Routes de retour présentes
[ ] ECMP ou secours testé
[ ] Convergence mesurée
[ ] Logs surveillés
[ ] Rollback prêt
```

### 14.3 Ce qu'il faut retenir

Le routage devient simple quand la topologie est simple. La plupart des incidents viennent d'une route manquante, d'un next-hop injoignable ou d'un retour asymétrique. Une table de routage lisible, des routes explicites et des tests dans les deux sens valent mieux qu'une configuration complexe.
