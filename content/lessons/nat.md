# NAT et PAT — Traduction d'adresses en pratique (CCNA / Admin Réseau)

> **Objectif** : comprendre pourquoi et comment NAT traduit les adresses, configurer les formes static, dynamic et overload sur Cisco IOS et Linux (nftables), diagnostiquer les problèmes de retour, de port forwarding, de hairpin et de NAT applicatif. Le cours traite aussi de CGNAT, NAT64 et des limites de NAT.

---

## 1. Pourquoi NAT

NAT (Network Address Translation) modifie les adresses IP (et parfois les ports) dans les paquets qui traversent un routeur ou un firewall. Les motivations historiques :

- économiser les adresses IPv4 publiques ;
- masquer la topologie interne ;
- permettre à un réseau privé d'accéder à Internet ;
- publier un service interne sur une adresse publique ;
- interconnecter des réseaux qui se chevauchent.

NAT est souvent confondu avec un firewall. Ce n'est pas un mécanisme de sécurité à lui seul : il masque, mais ne filtre pas. Un NAT sans politique de filtrage peut exposer des services.

### 1.1 Adressage privé

| Plage | RFC | Taille |
|---|---|---|
| 10.0.0.0/8 | 1918 | 16 777 216 adresses |
| 172.16.0.0/12 | 1918 | 1 048 576 adresses |
| 192.168.0.0/16 | 1918 | 65 536 adresses |
| 100.64.0.0/10 | 6598 | CGNAT |

Ces adresses ne sont pas routables sur Internet. NAT permet de les traduire vers une adresse publique.

---

## 2. Les types de NAT

| Type | Traduction | Session | Usage |
|---|---|---|---|
| Static NAT | 1 IP privée ↔ 1 IP publique | Non | Publier un serveur |
| Dynamic NAT | 1 IP privée ↔ 1 IP publique (pool) | Non | Pool d'adresses |
| PAT / overload | IP:port privé ↔ IP publique:port | Oui | Accès Internet |
| Static PAT (port forwarding) | IP:port public → IP:port privé | Oui | Publier un service |
| Twice NAT | Source et destination | Oui | Chevauchement, VPN |
| NAT64 | IPv6 ↔ IPv4 | Oui | Transition |

### 2.1 NAT statique

Une adresse privée est toujours traduite vers la même adresse publique.

```cisco
interface Gi0/0
 ip address 203.0.113.10 255.255.255.248
 ip nat outside
interface Gi0/1
 ip address 10.10.1.1 255.255.255.0
 ip nat inside
!
ip nat inside source static 10.10.1.50 203.0.113.10
```

Un serveur web interne en 10.10.1.50 est joignable en 203.0.113.10.

### 2.2 NAT dynamique

Un pool d'adresses publiques est utilisé pour traduire les hôtes internes.

```cisco
ip nat pool POOL_PUB 203.0.113.20 203.0.113.30 netmask 255.255.255.240
access-list 10 permit 10.10.1.0 0.0.0.255
ip nat inside source list 10 pool POOL_PUB
```

Sans `overload`, une adresse publique est réservée à un hôte à la fois. Le pool peut s'épuiser.

### 2.3 PAT / overload

PAT traduit aussi les **ports** source, ce qui permet à des milliers d'hôtes de partager une seule adresse publique.

```cisco
access-list 10 permit 10.10.1.0 0.0.0.255
ip nat inside source list 10 interface Gi0/0 overload
```

Table de traduction :

```text
Pro Inside global      Inside local       Outside local      Outside global
tcp 203.0.113.10:40001 10.10.1.10:51000 198.51.100.20:443 198.51.100.20:443
tcp 203.0.113.10:40002 10.10.1.11:51001 198.51.100.20:443 198.51.100.20:443
udp 203.0.113.10:40003 10.10.1.12:5353  8.8.8.8:53         8.8.8.8:53
```

### 2.4 Static PAT / port forwarding

```cisco
ip nat inside source static tcp 10.10.1.80 80 203.0.113.10 8080
ip nat inside source static tcp 10.10.1.80 443 203.0.113.10 443
```

Le port public 8080 est redirigé vers le port 80 du serveur interne. C'est la base de la publication de services.

---

## 3. Ordre des opérations

Sur Cisco IOS, l'ordre est important :

1. routage vers l'interface de sortie ;
2. NAT inside-to-outside ou outside-to-inside ;
3. application des ACL ;
4. chiffrement (IPsec), si applicable ;
5. transmission.

Une ACL peut voir l'adresse **avant** ou **après** NAT selon la direction et la plateforme. C'est une source classique de confusion. Tester avec `debug ip nat` et `show ip nat translations`.

```text
Paquet de 10.10.1.10 vers 198.51.100.20
  -> route vers Gi0/0
  -> NAT traduit source en 203.0.113.10:40001
  -> ACL outside voit 203.0.113.10
  -> paquet envoyé
```

---

## 4. NAT et retours

NAT maintient une table d'états. Le retour doit correspondre à une entrée existante. Si la table est vide ou expirée, le paquet est jeté.

| Problème | Symptôme | Cause |
|---|---|---|
| Pas de route de retour | Ping sort, pas de réponse | Route vers l'IP publique |
| NAT asymétrique | Un sens fonctionne | Deux routeurs NAT |
| Table expirée | Connexion coupée après inactivité | Timeout trop court |
| Port déjà utilisé | Erreur de traduction | Conflit de port |
| Hairpin | Interne vers IP publique | NAT loopback absent |

### 4.1 Timeouts

```cisco
ip nat translation timeout 3600
ip nat translation tcp-timeout 86400
ip nat translation udp-timeout 300
ip nat translation icmp-timeout 60
```

Les valeurs par défaut varient. Un timeout trop court coupe les sessions longues (SSH, bases de données).

### 4.2 Hairpin / NAT loopback

Un utilisateur interne accède au serveur via son adresse publique. Le paquet entre et sort par la même interface. Sans hairpin, le NAT ne sait pas rediriger.

```cisco
ip nat inside source static tcp 10.10.1.80 443 203.0.113.10 443
!
interface Gi0/1
 ip nat enable
```

Sur certaines plateformes, il faut `ip nat enable` au lieu de `ip nat inside/outside`, ou une règle dédiée.

---

## 5. NAT sous Linux avec nftables

nftables remplace iptables. Les règles NAT sont placées dans des chaînes `prerouting` (DNAT) et `postrouting` (SNAT/masquerade).

```bash
sysctl -w net.ipv4.ip_forward=1

nft add table ip nat
nft add chain ip nat prerouting '{ type nat hook prerouting priority dstnat; policy accept; }'
nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'

# Masquerade pour le LAN vers Internet
nft add rule ip nat postrouting oifname "eth0" ip saddr 10.10.1.0/24 masquerade

# Port forwarding 8080 -> 80
nft add rule ip nat prerouting iifname "eth0" tcp dport 8080 dnat to 10.10.1.80:80
```

Vérification :

```bash
nft list ruleset
conntrack -L
conntrack -L -p tcp --dport 443
sysctl net.ipv4.ip_forward
tcpdump -eni eth0 port 8080
```

### 5.1 SNAT statique

```bash
nft add rule ip nat postrouting ip saddr 10.10.1.50 snat to 203.0.113.10
```

### 5.2 DNAT avec plage de ports

```bash
nft add rule ip nat prerouting iifname "eth0" tcp dport 8000-8010 dnat to 10.10.1.80
```

### 5.3 iptables (legacy)

```bash
iptables -t nat -A POSTROUTING -s 10.10.1.0/24 -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 8080 -j DNAT --to-destination 10.10.1.80:80
iptables -t nat -L -n -v
```

---

## 6. NAT et applications

NAT modifie les en-têtes IP et TCP/UDP, mais certaines applications embarquent des adresses dans leurs données. Un **ALG** (Application Layer Gateway) peut réécrire ces payloads.

| Protocole | Problème | Solution |
|---|---|---|
| FTP actif | Adresse/port dans le payload | ALG ou FTP passif |
| SIP | IP dans les entêtes | ALG, SBC |
| H.323 | Adresses multiples | ALG |
| IPSec | Pas de NAT natif | NAT-T |
| DNS | Réponses avec IP privée | Split DNS |

Les ALG sont souvent fragiles. En pratique, on préfère un SBC pour SIP ou du FTP passif.

---

## 7. CGNAT et NAT64

### 7.1 CGNAT

Le Carrier-Grade NAT (CGNAT) est utilisé par les FAI pour partager une adresse publique entre de nombreux abonnés. Il utilise la plage 100.64.0.0/10.

Conséquences : les abonnés n'ont pas d'IP publique dédiée, le port forwarding est difficile, certains jeux/services peer-to-peer échouent, et la géolocalisation est imprécise.

### 7.2 NAT64

NAT64 permet à des hôtes IPv6 de joindre des serveurs IPv4 via un préfixe de traduction (souvent 64:ff9b::/96) et DNS64.

```text
Client IPv6 --- NAT64 --- Internet IPv4
2001:db8::1 -> 64:ff9b::c000:228 -> 192.0.2.40
```

---

## 8. Dépannage NAT

### 8.1 Vérifier la configuration

```cisco
show running-config | include ip nat
show ip nat statistics
show ip nat translations
show ip nat translations verbose
show ip interface Gi0/0
show ip interface Gi0/1
```

Les interfaces doivent être correctement marquées `ip nat inside` et `ip nat outside`.

### 8.2 Vérifier le trafic

```cisco
debug ip nat
debug ip nat detailed
```

Attention : le debug peut être coûteux en production. Utiliser une ACL de debug ou une fenêtre courte.

### 8.3 Le ping sort mais ne revient pas

- la route de retour vers l'IP publique existe-t-elle ?
- le FAI filtre-t-il l'IP publique ?
- le NAT source est-il bien appliqué ?
- une ACL outside bloque-t-elle ?
- le serveur distant répond-il à l'IP publique ?

### 8.4 Le port forwarding ne fonctionne pas

- l'interface est-elle `outside` ?
- la règle statique est-elle correcte (protocole, ports) ?
- le serveur écoute-t-il sur le bon port ?
- une ACL autorise-t-elle le trafic entrant ?
- le serveur a-t-il une route de retour vers le client ?
- le NAT hairpin est-il nécessaire ?

### 8.5 NAT et VPN

Un tunnel IPsec peut être perturbé par NAT. NAT-T encapsule ESP dans UDP 4500. Vérifier les politiques et les ACL.

### 8.6 Cas réel : deux réseaux qui se chevauchent

Une entreprise fusionne avec une autre qui utilise aussi 192.168.1.0/24. Le VPN ne peut pas router les deux. Solution : NAT twice ou renumérotation. Le NAT twice traduit source et destination.

```cisco
ip nat inside source static 192.168.1.50 10.99.1.50
ip nat outside source static 192.168.1.60 10.99.1.60
```

### 8.7 Cas réel : serveur web interne inaccessible depuis l'intérieur

Le DNS interne renvoie l'IP publique. Les postes internes ne peuvent pas revenir. Solution : split DNS (DNS interne renvoie l'IP privée) ou hairpin NAT.

### 8.8 Cas réel : SIP coupe après 30 secondes

Le NAT expire la session UDP ou l'ALG réécrit mal les entêtes. Solution : SBC, keepalive, timeout plus long, ou SIP over TLS.

---

## 9. Bonnes pratiques

- Documenter chaque règle NAT (qui, quoi, pourquoi).
- Utiliser des objets/groupes pour les adresses.
- Éviter le NAT si un routage propre est possible.
- Surveiller l'utilisation du pool et les épuisements.
- Vérifier les timeouts pour les applications longues.
- Tester le retour, pas seulement l'aller.
- Pour les services publics, préférer un reverse proxy ou un load balancer.
- Garder une trace des ports forwarding et des propriétaires.

---

## 10. Laboratoire

1. Configurer PAT sur Cisco et vérifier la table avec deux clients.
2. Publier un serveur HTTP via static PAT et tester depuis l'extérieur.
3. Configurer le hairpin et tester depuis l'intérieur.
4. Configurer nftables masquerade et DNAT sous Linux.
5. Provoquer un épuisement de pool et observer les erreurs.
6. Capturer le trafic avant/après NAT avec `tcpdump`.

---

## 11. Mémo

```cisco
show ip nat translations
show ip nat statistics
show ip nat translations verbose
debug ip nat
clear ip nat translation *
show running-config | include ip nat
```

```bash
nft list ruleset
conntrack -L
sysctl net.ipv4.ip_forward
tcpdump -eni eth0 port 8080
iptables -t nat -L -n -v
```

---

## 12. Points clés

- NAT traduit adresses et parfois ports ; PAT partage une IP publique entre plusieurs hôtes.
- Static NAT publie un serveur ; static PAT publie un port.
- L'ordre NAT/ACL dépend de la direction et de la plateforme.
- Le retour doit correspondre à une entrée de traduction ; les timeouts comptent.
- Hairpin NAT est nécessaire pour l'accès interne via l'IP publique.
- CGNAT et NAT64 ont des contraintes spécifiques.
- NAT n'est pas un firewall ; il ne remplace pas une politique de filtrage.
- Toujours tester l'aller **et** le retour.

> **Exercice** : un serveur interne est publié sur 203.0.113.10:443, mais les utilisateurs internes ne peuvent pas y accéder via cette adresse. Quelle est la cause probable et quelle solution ? Réponse : absence de hairpin NAT ou DNS interne qui renvoie l'IP publique ; ajouter une règle hairpin ou un split DNS.

---

## 13. NAT et DNS : le duo qui piège

Quand un service interne est publié, deux visions coexistent :

- les utilisateurs **externes** doivent utiliser l'adresse publique ;
- les utilisateurs **internes** doivent souvent utiliser l'adresse privée.

Si le DNS interne renvoie l'adresse publique, le trafic interne sort vers le routeur de bordure, qui doit faire du **hairpin** pour revenir. Si le hairpin n'est pas configuré, la connexion échoue ou le retour est asymétrique.

### 13.1 Split DNS

Le split DNS (ou split-horizon) maintient deux zones :

```text
Zone interne : app.example.com -> 10.10.1.80
Zone externe : app.example.com -> 203.0.113.10
```

Les clients internes reçoivent l'IP privée, les clients externes l'IP publique. C'est la solution la plus propre, mais elle exige un DNS interne autoritatif et une gestion rigoureuse des deux zones.

### 13.2 Hairpin NAT

Le hairpin (ou NAT loopback) permet à un client interne de joindre une IP publique qui appartient au routeur, puis d'être redirigé vers le serveur interne.

```cisco
ip nat inside source static tcp 10.10.1.80 443 203.0.113.10 443
!
interface Gi0/1
 ip nat enable
```

Sur certaines plateformes, la configuration exacte diffère. Toujours tester depuis un poste interne et vérifier la table de traductions.

### 13.3 DNS et TTL

Lors d'une migration, un TTL élevé peut maintenir l'ancienne adresse publique pendant des heures. Prévoir de baisser le TTL **avant** le changement, puis de le remonter après stabilisation.

---

## 14. NAT et voix sur IP

La VoIP est particulièrement sensible au NAT :

- SIP embarque des adresses IP et des ports dans le payload ;
- RTP utilise des ports UDP dynamiques ;
- les timeouts UDP coupent les sessions ;
- les ALG SIP sont souvent incomplets.

Symptômes : appel qui sonne mais pas de voix, appel coupé après 30 secondes, audio dans un seul sens.

Solutions :

- **SBC** (Session Border Controller) devant le NAT ;
- **STUN/TURN/ICE** pour les clients WebRTC ;
- **keepalive** SIP et RTP ;
- plage de ports RTP fixe et règle NAT dédiée ;
- désactiver l'ALG SIP s'il corrompt les entêtes.

```text
Téléphone 10.10.20.10:5060 --- NAT --- Internet
SIP : entêtes avec IP privée -> SBC réécrit
RTP : ports 10000-20000 -> NAT statique ou SBC
```

---

## 15. NAT et peer-to-peer

Les applications peer-to-peer, les jeux en ligne et certains VPN nécessitent des connexions entrantes. Derrière un NAT, elles utilisent :

- UPnP/NAT-PMP pour ouvrir un port ;
- STUN pour découvrir l'adresse publique ;
- TURN pour relayer ;
- hole punching pour percer le NAT.

En entreprise, ces mécanismes sont souvent bloqués. Il faut documenter les besoins et ouvrir uniquement les ports nécessaires, avec une politique de sécurité.

---

## 16. NAT64 et DNS64 en détail

NAT64 traduit IPv6 vers IPv4. DNS64 synthétise des enregistrements AAAA à partir de A lorsque le serveur n'a pas d'IPv6.

```text
Client IPv6 --- DNS64 ---> AAAA synthétique 64:ff9b::198.51.100.20
Client IPv6 --- NAT64 ---> paquet IPv4 vers 198.51.100.20
```

Limites : applications qui embarquent des adresses IPv4, checksums, IPsec, et certains protocoles. NAT64 est une solution de transition, pas une solution native.

---

## 17. Vérifications de bout en bout

### 17.1 Depuis le client

```bash
ip addr
ip route
curl -vk https://203.0.113.10/
nc -vz 203.0.113.10 443
```

### 17.2 Sur le routeur NAT

```cisco
show ip nat translations
show ip nat statistics
show ip interface Gi0/0
show ip interface Gi0/1
show access-lists
```

### 17.3 Sur le serveur

```bash
ss -tulpn | grep 443
tail -f /var/log/nginx/access.log
tcpdump -eni eth0 port 443
```

### 17.4 Sur le retour

Le serveur doit avoir une route vers l'adresse **publique** du NAT (ou vers le client traduit). Si le serveur répond à l'adresse privée, le paquet est jeté.

```bash
ip route get 203.0.113.10
```

---

## 18. Check-list de mise en service

```text
[ ] Interfaces inside/outside correctes
[ ] Route par défaut vers Internet
[ ] Pool ou overload configuré
[ ] ACL NAT correcte
[ ] Règle de port forwarding testée depuis l'extérieur
[ ] Hairpin ou split DNS pour les internes
[ ] Timeouts adaptés aux applications
[ ] Retour vérifié depuis le serveur
[ ] Logs et compteurs surveillés
[ ] Documentation des règles
```

---

## 19. Erreurs fréquentes

1. Oublier `ip nat inside` ou `ip nat outside`.
2. Mettre l'ACL NAT dans le mauvais sens.
3. Publier un port sans autoriser le trafic dans le firewall.
4. Oublier la route de retour sur le serveur.
5. Utiliser un pool trop petit.
6. Laisser le timeout par défaut couper les sessions longues.
7. Croire que NAT protège des attaques.
8. Oublier le hairpin pour les utilisateurs internes.
9. Configurer un ALG SIP qui casse les entêtes.
10. Ne pas tester après un changement de FAI ou d'adresse publique.

---

## 20. Synthèse

NAT est simple en apparence, mais ses interactions avec le routage, le DNS, les firewalls et les applications en font une source fréquente d'incidents. La règle est de toujours raisonner en **flux complet** : source, destination, traduction, retour, application. Une table de traduction vide, un timeout trop court ou une route de retour absente expliquent la majorité des pannes.
