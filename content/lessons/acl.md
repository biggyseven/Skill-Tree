# ACL et filtrage — Contrôle d'accès en couche 3 et 4 (CCNA / Admin Réseau)

> **Objectif** : maîtriser les ACL Cisco (standard, étendues, nommées, IPv6), les wildcards, l'ordre d'évaluation et le placement, puis transposer les mêmes concepts sous Linux avec nftables. Le cours couvre aussi les interactions avec NAT, les ACL de gestion, le logging et les pièges classiques.

---

## 1. À quoi sert une ACL

Une **ACL** (Access Control List) est une liste ordonnée de règles qui autorisent ou refusent du trafic. Sur un routeur Cisco, elle peut filtrer :

- le trafic qui traverse une interface (`ip access-group`) ;
- l'accès aux lignes VTY (`access-class`) ;
- les routes (distribute-list, prefix-list) ;
- le NAT (match d'adresses) ;
- les fonctionnalités de sécurité (zone-based firewall, CoPP).

Une ACL n'est pas un firewall stateful : elle évalue chaque paquet indépendamment. Pour un filtrage stateful, utiliser une zone-based firewall ou un firewall dédié.

---

## 2. ACL standard vs étendue

| Type | Numéro Cisco | Filtre | Placement recommandé |
|---|---|---|---|
| Standard | 1–99, 1300–1999 | Source uniquement | Près de la destination |
| Étendue | 100–199, 2000–2699 | Source, destination, protocole, ports | Près de la source |
| Nommée | Nom | Selon le type | Selon le type |
| IPv6 | Nom | Source/destination IPv6 | Près de la source |

### 2.1 ACL standard

```cisco
access-list 10 permit 10.10.1.0 0.0.0.255
access-list 10 deny any
interface Gi0/1
 ip access-group 10 out
```

Une ACL standard ne filtre que la source. Si on la place trop près de la source, elle peut bloquer du trafic légitime vers d'autres destinations. On la place donc près de la destination.

### 2.2 ACL étendue

```cisco
access-list 100 permit tcp 10.10.1.0 0.0.0.255 host 198.51.100.20 eq 443
access-list 100 permit tcp 10.10.1.0 0.0.0.255 host 198.51.100.20 eq 80
access-list 100 deny ip any any log
interface Gi0/0
 ip access-group 100 in
```

### 2.3 ACL nommée

```cisco
ip access-list extended WEB-OUT
 permit tcp 10.10.1.0 0.0.0.255 host 198.51.100.20 eq 443
 permit tcp 10.10.1.0 0.0.0.255 host 198.51.100.20 eq 80
 deny ip any any log
!
interface Gi0/0
 ip access-group WEB-OUT in
```

Les ACL nommées sont plus lisibles et permettent d'insérer/supprimer des lignes avec des numéros de séquence.

```cisco
ip access-list extended WEB-OUT
 10 permit tcp 10.10.1.0 0.0.0.255 host 198.51.100.20 eq 443
 20 permit tcp 10.10.1.0 0.0.0.255 host 198.51.100.20 eq 80
 30 deny ip any any log
```

---

## 3. Wildcard masks

Le wildcard est l'inverse du masque de sous-réseau :

```text
Masque 255.255.255.0 -> wildcard 0.0.0.255
Masque 255.255.0.0   -> wildcard 0.0.255.255
```

| Wildcard | Signification |
|---|---|
| `0.0.0.0` | Correspond exactement |
| `0.0.0.255` | Tous les hôtes du /24 |
| `0.0.255.255` | Tous les hôtes du /16 |
| `255.255.255.255` | N'importe quelle adresse (`any`) |

Exemples :

```cisco
! Hôte précis
permit ip host 10.10.1.10 any

! Sous-réseau
permit ip 10.10.1.0 0.0.0.255 any

! Plage 10.10.1.0/24 et 10.10.3.0/24 (wildcard non contigu)
permit ip 10.10.1.0 0.0.2.255 any
```

Le wildcard `0.0.2.255` correspond aux bits 0 et 1 du troisième octet : 10.10.1.x et 10.10.3.x. Ce n'est pas un simple masque, c'est un motif binaire.

---

## 4. Ordre d'évaluation

Les ACL sont évaluées **de haut en bas**, première correspondance gagne. Il y a un **deny implicite** à la fin.

```text
permit tcp any host 198.51.100.20 eq 443
deny ip any any
```

Si la première règle correspond, les suivantes ne sont pas évaluées. Une règle `permit ip any any` en haut rend les suivantes inutiles.

### 4.1 Bonnes pratiques d'ordre

- Placer les règles les plus spécifiques en premier.
- Terminer par un `deny` explicite avec `log` pour compter.
- Éviter les `permit ip any any` sauf si c'est volontaire.
- Numéroter les lignes pour faciliter les modifications.
- Tester avec des paquets réels, pas seulement la configuration.

### 4.2 Deny implicite

```cisco
ip access-list extended TEST
 permit tcp 10.10.1.0 0.0.0.255 any eq 443
```

Tout le reste est refusé. C'est souvent voulu, mais il faut le documenter.

### 4.3 Schéma d'évaluation

```text
Paquet entrant sur Gi0/1
          |
          v
   +--------------+
   |  ACL IN      | -- deny --> [ drop ]
   +--------------+
          |
        permit
          |
          v
   +--------------+
   |  Routage IP  |
   +--------------+
          |
          v
   +--------------+
   |  ACL OUT     | -- deny --> [ drop ]
   +--------------+
          |
        permit
          |
          v
   Interface de sortie
```

Exemple de topologie :

```text
10.10.1.0/24 --- Gi0/1 [ R1 ] Gi0/0 --- 198.51.100.0/24
                        |
                  ACL 100 in sur Gi0/0
```

L'ACL est évaluée avant le routage pour le trafic entrant, et après le routage pour le trafic sortant. C'est pourquoi une ACL `in` peut bloquer un paquet avant même que le routeur sache où l'envoyer.

---

## 5. Placement des ACL

| ACL | Objectif | Placement |
|---|---|---|
| Standard | Filtrer une source | Près de la destination |
| Étendue | Filtrer un flux | Près de la source |
| Gestion | Protéger VTY | Sur les lignes VTY |
| NAT | Sélectionner le trafic | Sur l'interface inside |
| Routage | Filtrer les routes | Sur le protocole |

Placer une ACL étendue près de la source évite de transporter du trafic inutile jusqu'à la destination. Placer une ACL standard près de la destination évite de bloquer des flux légitimes.

---

## 6. ACL et interfaces

```cisco
interface Gi0/0
 ip access-group WEB-OUT in
!
interface Gi0/1
 ip access-group WEB-IN in
```

Une ACL `in` s'applique aux paquets entrants sur l'interface. Une ACL `out` s'applique aux paquets sortants. Une interface peut avoir une ACL dans chaque direction.

### 6.1 Vérification

```cisco
show access-lists
show access-lists WEB-OUT
show ip interface Gi0/0
show ip interface Gi0/0 | include access list
show running-config | include access-group
```

Les compteurs de correspondance sont précieux :

```cisco
show access-lists WEB-OUT
clear access-list counters WEB-OUT
```

---

## 7. ACL de gestion (VTY)

Protéger l'accès SSH/Telnet au routeur :

```cisco
ip access-list standard MGMT
 permit 10.10.99.0 0.0.0.255
 deny any log
!
line vty 0 4
 access-class MGMT in
 transport input ssh
```

Toujours autoriser le réseau de management avant de bloquer, sinon on se coupe l'accès.

---

## 8. ACL et NAT

Sur Cisco, l'ACL qui sélectionne le trafic NAT est souvent une ACL standard :

```cisco
access-list 10 permit 10.10.1.0 0.0.0.255
ip nat inside source list 10 interface Gi0/0 overload
```

L'ordre NAT/ACL varie selon la direction et la plateforme. Une ACL outside peut voir l'adresse traduite ou non. Tester avec `debug ip nat` et `show ip nat translations`.

---

## 9. ACL IPv6

```cisco
ipv6 access-list V6-WEB
 permit tcp 2001:db8:10::/64 host 2001:db8:20::20 eq 443
 deny ipv6 any any log
!
interface Gi0/0
 ipv6 traffic-filter V6-WEB in
```

Les ACL IPv6 sont nommées et utilisent `ipv6 traffic-filter`. Le deny implicite s'applique aussi.

---

## 10. Filtrage sous Linux avec nftables

nftables est le framework moderne. Il remplace iptables, ip6tables, arptables et ebtables.

### 10.1 Table et chaînes

```bash
nft add table inet filter
nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'
nft add chain inet filter output '{ type filter hook output priority 0; policy accept; }'
```

### 10.2 Règles de base

```bash
nft add rule inet filter input ct state established,related accept
nft add rule inet filter input iif lo accept
nft add rule inet filter input ip saddr 10.10.99.0/24 tcp dport 22 accept
nft add rule inet filter input icmp type echo-request accept
```

### 10.3 Forward

```bash
nft add rule inet filter forward ct state established,related accept
nft add rule inet filter forward iif eth0 oif eth1 ip saddr 10.10.1.0/24 accept
```

### 10.4 Sets et maps

```bash
nft add set inet filter MGMT '{ type ipv4_addr; flags interval; }'
nft add element inet filter MGMT '{ 10.10.99.0/24, 10.10.98.0/24 }'
nft add rule inet filter input ip saddr @MGMT tcp dport 22 accept
```

### 10.5 Vérification

```bash
nft list ruleset
nft -a list ruleset
nft monitor trace
conntrack -L
```

### 10.6 iptables (legacy)

```bash
iptables -A INPUT -p tcp --dport 22 -s 10.10.99.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP
iptables -L -n -v
```

---

## 11. ACL stateful vs stateless

Une ACL Cisco classique est **stateless** : elle ne sait pas qu'un paquet appartient à une connexion existante. Il faut autoriser explicitement le retour.

```cisco
! Autoriser le retour du web
access-list 100 permit tcp any 10.10.1.0 0.0.0.255 established
```

Le mot-clé `established` vérifie les flags TCP (ACK/RST), mais ce n'est pas un vrai suivi d'état.

Pour un filtrage stateful, utiliser :

- zone-based firewall (Cisco IOS) ;
- firewall dédié (ASA, Fortinet, pfSense) ;
- nftables avec `ct state`.

```bash
nft add rule inet filter forward ct state established,related accept
nft add rule inet filter forward ct state new tcp dport 443 accept
```

---

## 12. Logging et compteurs

```cisco
access-list 100 deny ip any any log
access-list 100 permit tcp any host 198.51.100.20 eq 443
```

`log` génère un message syslog pour chaque paquet correspondant. Attention à la charge CPU : utiliser `log-input` avec parcimonie.

```cisco
show logging | include ACL
show access-lists
clear access-list counters
```

Sous Linux :

```bash
nft add rule inet filter input tcp dport 23 log prefix "TELNET " drop
journalctl -k -f
```

---

## 13. Dépannage ACL

### 13.1 Le trafic autorisé est bloqué

- l'ACL est-elle appliquée dans la bonne direction ?
- l'ordre des règles est-il correct ?
- le wildcard est-il correct ?
- le port/protocole est-il bon ?
- le NAT a-t-il modifié l'adresse avant l'ACL ?
- une ACL sur une autre interface bloque-t-elle ?

```cisco
show access-lists
show ip interface Gi0/0
show running-config interface Gi0/0
```

### 13.2 Le retour est bloqué

Une ACL stateless doit autoriser le retour. Vérifier les règles `established` ou la politique stateful.

### 13.3 ACL de management qui coupe l'accès

Toujours inclure le réseau de management et tester depuis une session de secours. Si l'accès est perdu, utiliser la console.

### 13.4 ACL et fragments

Les fragments IP peuvent être traités différemment. Les ACL étendues Cisco peuvent correspondre aux fragments non initiaux ; vérifier les options `fragments`.

### 13.5 ACL et NAT

L'ordre d'application peut faire voir une adresse privée ou publique. Tester avec `debug ip nat` et `show ip nat translations`.

### 13.6 Cas réel : blocage de tout le VLAN

Une règle `deny ip any any` a été placée avant les permits. Les compteurs montrent que tout est refusé. On réordonne les règles et on teste.

### 13.7 Cas réel : SSH ouvert à Internet

Une ACL VTY autorise `any`. Un scan découvre SSH. On restreint au réseau de management et on désactive Telnet.

### 13.8 Cas réel : ACL trop permissive

Une ACL autorise `permit ip any any` pour « faire marcher » le réseau. Elle annule toute politique. On documente les flux nécessaires et on remplace par des règles précises.

---

## 14. Bonnes pratiques

- Privilégier des ACL nommées et numérotées.
- Commenter chaque règle (objet, propriétaire, date).
- Terminer par un deny log explicite.
- Tester avec des paquets réels et les compteurs.
- Sauvegarder la configuration avant modification.
- Utiliser des objets/groupes pour les adresses et services.
- Réviser les ACL lors des changements d'architecture.
- Surveiller les compteurs de deny.

---

## 15. Laboratoire

1. Configurer une ACL standard pour autoriser un subnet vers un serveur.
2. Configurer une ACL étendue pour autoriser HTTP/HTTPS et bloquer le reste.
3. Vérifier les compteurs avec `show access-lists`.
4. Protéger VTY avec une ACL de management.
5. Configurer nftables avec une politique `drop` et autoriser SSH/HTTP.
6. Tester une ACL stateless et ajouter la règle de retour.

---

## 16. Mémo

```cisco
show access-lists
show access-lists WEB-OUT
show ip interface Gi0/0
show running-config | include access-group
clear access-list counters
```

```bash
nft list ruleset
nft -a list ruleset
nft monitor trace
iptables -L -n -v
conntrack -L
```

---

## 17. Points clés

- Une ACL est ordonnée ; la première correspondance gagne, avec un deny implicite.
- Standard = source seule ; étendue = source, destination, protocole, ports.
- Le wildcard est un masque inversé, mais pas toujours contigu.
- Placer les ACL étendues près de la source, les standard près de la destination.
- Les ACL Cisco classiques sont stateless ; le retour doit être autorisé.
- NAT et ACL interagissent : l'ordre change l'adresse vue.
- nftables offre un filtrage stateful avec `ct state`.
- Toujours vérifier la direction, l'ordre et les compteurs.

> **Exercice** : une ACL autorise `tcp any host 198.51.100.20 eq 443` mais le serveur ne répond pas. Le client reçoit-il la réponse ? Réponse : non, si une ACL stateless bloque le retour ; il faut autoriser `established` ou utiliser un firewall stateful.

---

## 18. ACL et ICMP

Les ACL étendues filtrent aussi ICMP. Il faut distinguer les types, car bloquer tout ICMP casse le diagnostic et IPv6.

```cisco
! Autoriser echo-request et echo-reply
access-list 100 permit icmp any any echo
access-list 100 permit icmp any any echo-reply

! Autoriser les messages d'erreur essentiels
access-list 100 permit icmp any any unreachable
access-list 100 permit icmp any any time-exceeded
access-list 100 permit icmp any any packet-too-big
```

En IPv6, ICMPv6 est indispensable à NDP (Neighbor Discovery), aux Router Advertisements et à la découverte de MTU. Ne jamais bloquer tout ICMPv6.

```cisco
ipv6 access-list V6-BASE
 permit icmp any any nd-na
 permit icmp any any nd-ns
 permit icmp any any router-advertisement
 permit icmp any any packet-too-big
 permit icmp any any echo-request
 permit icmp any any echo-reply
```

---

## 19. Protection du plan de contrôle

Le plan de contrôle (CPU) est souvent oublié. Une ACL peut protéger les services exposés sur le routeur :

- SSH/Telnet (VTY) ;
- SNMP ;
- NTP ;
- BGP/OSPF ;
- HTTP de gestion.

```cisco
ip access-list extended MGMT-ONLY
 permit tcp 10.10.99.0 0.0.0.255 any eq 22
 permit udp 10.10.99.0 0.0.0.255 any eq 161
 deny ip any any log
!
line vty 0 4
 access-class MGMT-ONLY in
```

Pour un filtrage plus fin du plan de contrôle, utiliser **CoPP** (Control Plane Policing) ou une policy-map. Les ACL seules ne limitent pas le débit.

---

## 20. ACL et routage

Les ACL peuvent filtrer les routes elles-mêmes, pas seulement les paquets :

```cisco
access-list 20 permit 10.10.0.0 0.0.255.255
router ospf 1
 distribute-list 20 in
```

Pour BGP, préférer les **prefix-lists** et les route-maps. Une distribute-list mal placée peut supprimer des routes nécessaires.

```cisco
ip prefix-list PL_LAN permit 10.10.0.0/16 le 24
router bgp 65001
 neighbor 203.0.113.1 prefix-list PL_LAN in
```

---

## 21. Exemples concrets

### 21.1 Autoriser un serveur web et bloquer le reste

```cisco
ip access-list extended DMZ-IN
 permit tcp any host 198.51.100.20 eq 443
 permit tcp any host 198.51.100.20 eq 80
 permit icmp any host 198.51.100.20 echo
 deny ip any any log
!
interface Gi0/0
 ip access-group DMZ-IN in
```

### 21.2 Autoriser un subnet à administrer un switch

```cisco
ip access-list standard ADMIN
 permit 10.10.99.0 0.0.0.255
 deny any log
!
line vty 0 4
 access-class ADMIN in
```

### 21.3 Bloquer un pays ou une plage

Avec des objets ou des sets nftables :

```bash
nft add set inet filter BLOCK '{ type ipv4_addr; flags interval; }'
nft add element inet filter BLOCK '{ 198.51.100.0/24, 203.0.113.128/25 }'
nft add rule inet filter input ip saddr @BLOCK drop
```

### 21.4 Autoriser DNS et NTP sortants

```cisco
ip access-list extended BASE-OUT
 permit udp 10.10.0.0 0.0.255.255 any eq 53
 permit tcp 10.10.0.0 0.0.255.255 any eq 53
 permit udp 10.10.0.0 0.0.255.255 any eq 123
 deny ip any any log
```

### 21.5 ACL temporaire et rollback

Sur une session distante, une ACL qui coupe SSH peut vous verrouiller dehors. Utilisez `reload in 5` avant d'appliquer, puis annulez avec `reload cancel` si tout va bien.

```cisco
reload in 5
configure terminal
ip access-group NEW-ACL in
end
! vérifier SSH
reload cancel
```

---

## 22. Erreurs fréquentes

1. Oublier le deny implicite et croire que tout est autorisé.
2. Placer un `permit ip any any` avant les règles utiles.
3. Utiliser le mauvais wildcard.
4. Appliquer l'ACL dans la mauvaise direction.
5. Oublier le retour pour une ACL stateless.
6. Bloquer ICMP et casser le diagnostic.
7. Bloquer ICMPv6 et casser NDP.
8. Oublier de tester depuis une source réelle.
9. Ne pas sauvegarder avant modification.
10. Ne pas surveiller les compteurs de deny.

---

## 23. Check-list de mise en service

```text
[ ] Objectif de l'ACL documenté
[ ] Règles ordonnées et numérotées
[ ] Wildcards vérifiés
[ ] Direction et interface vérifiées
[ ] Retour autorisé ou firewall stateful
[ ] ICMP/ICMPv6 essentiels autorisés
[ ] Deny final avec log
[ ] Test depuis chaque source concernée
[ ] Compteurs vérifiés
[ ] Configuration sauvegardée
```

---

## 24. Synthèse

Une ACL est un outil simple mais dangereux : une seule règle mal ordonnée peut bloquer un service ou ouvrir une brèche. La discipline consiste à documenter le flux, à tester la direction, à vérifier le retour et à surveiller les compteurs. Pour les environnements modernes, préférer un filtrage stateful (nftables `ct state`, zone-based firewall) et réserver les ACL stateless aux cas simples ou aux protections de plan de contrôle.
