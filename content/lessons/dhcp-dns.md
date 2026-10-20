# DHCP et DNS — Attribution et résolution de noms (CCNA / Admin Réseau)

> **Objectif** : maîtriser DHCP (DORA, relais, options, baux, snooping) et DNS (hiérarchie, enregistrements, récursion, cache, DNSSEC), configurer Cisco IOS et Linux, et diagnostiquer les pannes qui empêchent un poste d'obtenir une adresse ou de résoudre un nom. Le cours insiste sur les chemins de retour, les options DHCP et les erreurs de configuration.

---

## 1. DHCP : le rôle

DHCP (Dynamic Host Configuration Protocol) attribue automatiquement :

- une adresse IP ;
- un masque ;
- une passerelle par défaut ;
- un ou plusieurs serveurs DNS ;
- éventuellement un domaine, un serveur NTP, un TFTP, etc.

Sans DHCP, chaque poste doit être configuré manuellement, ce qui ne passe pas à l'échelle. Un serveur DHCP mal configuré peut immobiliser tout un VLAN.

### 1.1 Ports et diffusion

| Élément | Valeur |
|---|---|
| Port serveur | UDP 67 |
| Port client | UDP 68 |
| Adresse client initiale | 0.0.0.0 |
| Adresse serveur | 255.255.255.255 ou unicast |
| Broadcast | Oui au début |

DHCP utilise des broadcasts, qui ne traversent pas les routeurs. D'où le **relais DHCP**.

---

## 2. DORA

```text
Client                       Serveur DHCP
  |------ DHCP DISCOVER ------->|  (broadcast)
  |<----- DHCP OFFER -----------|  (proposition)
  |------ DHCP REQUEST -------->|  (acceptation)
  |<----- DHCP ACK -------------|  (confirmation)
  |------ DHCP RELEASE -------->|  (libération, optionnelle)
```

| Message | Rôle |
|---|---|
| DISCOVER | Le client cherche un serveur |
| OFFER | Le serveur propose une adresse |
| REQUEST | Le client demande l'adresse proposée |
| ACK | Le serveur confirme le bail |
| NAK | Le serveur refuse |
| RELEASE | Le client libère |
| INFORM | Le client demande des options sans adresse |

### 2.1 Bail

Le bail a une durée (souvent 8 jours). À 50 % du bail, le client tente un renouvellement en unicast (REQUEST). À 87,5 %, il retente en broadcast. Si le bail expire, il repart en DISCOVER.

```text
Bail 8 jours :
  T1 = 4 jours   -> renouvellement unicast
  T2 = 7 jours   -> rebind broadcast
  T3 = 8 jours   -> expiration
```

---

## 3. Configuration Cisco IOS

### 3.1 Pool simple

```cisco
ip dhcp excluded-address 10.10.1.1 10.10.1.20
!
ip dhcp pool LAN10
 network 10.10.1.0 255.255.255.0
 default-router 10.10.1.1
 dns-server 10.10.1.53 1.1.1.1
 domain-name example.lan
 lease 0 8 0
```

### 3.2 Réservation

```cisco
ip dhcp pool IMPRIMANTE
 host 10.10.1.50 255.255.255.0
 client-identifier 01aabb.ccdd.eeff.00
 default-router 10.10.1.1
 dns-server 10.10.1.53
```

Ou avec `hardware-address` :

```cisco
ip dhcp pool IMPRIMANTE
 host 10.10.1.50 255.255.255.0
 hardware-address aabb.ccdd.eeff
```

### 3.3 Relais DHCP

Un routeur intermédiaire doit relayer les broadcasts vers le serveur.

```cisco
interface Gi0/1
 ip address 10.20.1.1 255.255.255.0
 ip helper-address 10.10.1.53
```

`ip helper-address` transforme le broadcast DHCP en unicast vers le serveur. Il relaie aussi d'autres UDP (TFTP, DNS, NTP) selon la configuration ; vérifier les services concernés.

### 3.4 Vérification

```cisco
show ip dhcp binding
show ip dhcp pool
show ip dhcp server statistics
show ip dhcp conflict
debug ip dhcp server events
```

---

## 4. DHCP sous Linux

### 4.1 dnsmasq

dnsmasq est léger et fait DHCP + DNS.

```text
interface=eth0
dhcp-range=10.10.1.100,10.10.1.200,12h
dhcp-option=3,10.10.1.1
dhcp-option=6,10.10.1.53,1.1.1.1
dhcp-option=15,example.lan
dhcp-host=aa:bb:cc:dd:ee:ff,10.10.1.50,imprimante
```

```bash
systemctl restart dnsmasq
journalctl -u dnsmasq -f
```

### 4.2 ISC DHCP

```text
subnet 10.10.1.0 netmask 255.255.255.0 {
  range 10.10.1.100 10.10.1.200;
  option routers 10.10.1.1;
  option domain-name-servers 10.10.1.53, 1.1.1.1;
  option domain-name "example.lan";
  default-lease-time 43200;
  max-lease-time 86400;
}
```

```bash
systemctl restart isc-dhcp-server
dhcpd -t -cf /etc/dhcp/dhcpd.conf
```

### 4.3 Client

```bash
dhclient -v eth0
ip addr show eth0
ip route
cat /etc/resolv.conf
resolvectl status
nmcli connection show
```

---

## 5. DHCP Snooping

DHCP Snooping bloque les serveurs DHCP non autorisés sur les ports d'accès. Les ports sont classés **trusted** (vers le serveur légitime) et **untrusted** (vers les clients).

```cisco
ip dhcp snooping
ip dhcp snooping vlan 10,20
interface Gi0/24
 ip dhcp snooping trust
interface range Gi0/1-23
 ip dhcp snooping limit rate 10
```

Vérification :

```cisco
show ip dhcp snooping
show ip dhcp snooping binding
show ip dhcp snooping statistics
```

Le binding table associe MAC, IP, VLAN et port. Il peut alimenter IP Source Guard et Dynamic ARP Inspection.

### 5.1 Option 82

L'option 82 transporte des informations sur le port d'accès. Elle permet au serveur de choisir un pool par switch/port. Certains serveurs la refusent ; vérifier la compatibilité.

---

## 6. DNS : le rôle

DNS traduit les noms en adresses IP. Sans DNS, un utilisateur doit mémoriser des adresses, et les services qui utilisent des noms (HTTP, SMTP, LDAP) échouent.

```text
www.example.com  -->  198.51.100.20
```

DNS est une base distribuée, hiérarchique et caching. Il utilise surtout UDP 53, et TCP 53 pour les réponses volumineuses ou les transferts de zone.

---

## 7. Hiérarchie DNS

```text
                 . (root)
               /     |      \
            com     org     fr
           /         |        \
      example     wikipedia   exemple
         |
        www
```

| Serveur | Rôle |
|---|---|
| Root | Délègue les TLD |
| TLD (.com, .fr) | Délègue les domaines |
| Autoritatif | Répond pour une zone |
| Récursif | Résout pour le client |
| Cache | Réduit les requêtes |

### 7.1 Résolution récursive

```text
Client -> Resolver -> Root -> TLD -> Autoritatif
         <-- réponse mise en cache <--
```

Le resolver pose les questions, le client attend une réponse finale. Un resolver peut aussi être **itératif** : il reçoit des références et poursuit lui-même.

---

## 8. Enregistrements DNS

| Type | Rôle | Exemple |
|---|---|---|
| A | IPv4 | `www 300 IN A 198.51.100.20` |
| AAAA | IPv6 | `www 300 IN AAAA 2001:db8::20` |
| CNAME | Alias | `web IN CNAME www` |
| MX | Serveur mail | `@ IN MX 10 mail` |
| TXT | Texte/SPF/DKIM | `@ IN TXT "v=spf1 ..."` |
| NS | Serveur de noms | `@ IN NS ns1` |
| PTR | Reverse | `20 IN PTR www` |
| SOA | Autorité de zone | `@ IN SOA ns1 admin` |
| SRV | Service | `_sip._tcp IN SRV ...` |
| CAA | Autorisation CA | `@ IN CAA 0 issue "letsencrypt.org"` |

### 8.1 TTL et cache

Le TTL indique combien de temps un enregistrement peut être mis en cache. Un TTL court accélère les changements mais augmente les requêtes. Un TTL long réduit la charge mais retarde les migrations.

### 8.2 CNAME

Un CNAME ne doit pas coexister avec d'autres enregistrements au même nom (sauf DNSSEC). À la racine d'une zone, utiliser des A/AAAA ou des ALIAS si le fournisseur le permet.

---

## 9. Configuration Cisco

### 9.1 Résolution

```cisco
ip name-server 10.10.1.53
ip name-server 1.1.1.1
ip domain lookup
ip domain name example.lan
```

Vérification :

```cisco
show hosts
show ip dns view
ping www.example.com
```

### 9.2 Serveur DNS local

IOS peut servir de serveur DNS pour quelques enregistrements.

```cisco
ip dns server
ip host www.example.lan 10.10.1.80
ip name-server 1.1.1.1
```

### 9.3 DHCP et DNS

```cisco
ip dhcp pool LAN10
 dns-server 10.10.1.53 1.1.1.1
 domain-name example.lan
```

Le client reçoit les serveurs DNS via l'option 6.

---

## 10. DNS sous Linux

### 10.1 Résolution

```bash
cat /etc/resolv.conf
resolvectl status
systemd-resolve --status
```

Avec systemd-resolved, `/etc/resolv.conf` peut être un stub `127.0.0.53`.

### 10.2 dig

```bash
dig example.com
dig +short example.com
dig @1.1.1.1 example.com A
dig +trace example.com
dig -x 198.51.100.20
dig example.com MX
dig example.com ANY
```

### 10.3 nslookup / host

```bash
nslookup example.com
nslookup example.com 1.1.1.1
host example.com
host -t MX example.com
```

### 10.4 BIND

```text
zone "example.lan" {
  type master;
  file "/etc/bind/db.example.lan";
};

// db.example.lan
$TTL 3600
@   IN SOA ns1.example.lan. admin.example.lan. (
        2024010101 ; serial
        3600       ; refresh
        900        ; retry
        1209600    ; expire
        300 )      ; negative TTL
    IN NS  ns1.example.lan.
ns1 IN A   10.10.1.53
www IN A   10.10.1.80
```

```bash
named-checkconf
named-checkzone example.lan /etc/bind/db.example.lan
systemctl restart bind9
```

### 10.5 dnsmasq

```text
domain-needed
bogus-priv
server=1.1.1.1
server=8.8.8.8
address=/www.example.lan/10.10.1.80
```

dnsmasq met en cache et peut servir de forwarder local.

---

## 11. DNSSEC, DoH et DoT

- **DNSSEC** signe les zones pour authentifier les réponses. Il ne chiffre pas.
- **DoT** (DNS over TLS) chiffre les requêtes sur TCP 853.
- **DoH** (DNS over HTTPS) chiffre les requêtes sur HTTPS 443.
- **DoQ** (DNS over QUIC) émerge.

Le chiffrement protège la confidentialité, mais peut contourner les politiques réseau. Les entreprises doivent décider de leur stratégie.

---

## 12. Dépannage DHCP

### 12.1 Le client n'a pas d'adresse

```bash
ip addr show
dhclient -v eth0
journalctl -u NetworkManager -f
tcpdump -eni eth0 port 67 or port 68
```

Côté Cisco :

```cisco
show ip dhcp binding
show ip dhcp server statistics
show ip interface Gi0/1
debug ip dhcp server events
```

Causes : VLAN incorrect, relais absent, pool épuisé, mauvaise passerelle, serveur down, ACL, DHCP snooping.

### 12.2 Le client a une adresse APIPA

`169.254.x.x` signifie qu'aucun serveur DHCP n'a répondu. Vérifier le lien, le VLAN, le relais et le serveur.

### 12.3 Le client obtient une adresse mais pas Internet

L'adresse est correcte, mais la passerelle ou le DNS est mauvais. Vérifier les options 3 et 6.

```bash
ip route
cat /etc/resolv.conf
ping 10.10.1.1
dig @10.10.1.53 example.com
```

### 12.4 Conflit d'adresses

```cisco
show ip dhcp conflict
clear ip dhcp conflict *
```

Un conflit vient souvent d'une IP statique dans la plage DHCP. Utiliser `excluded-address` ou une réservation.

### 12.5 Serveur pirate

DHCP Snooping + port trusted. Vérifier les logs et les baux inattendus.

---

## 13. Dépannage DNS

### 13.1 Le ping par IP fonctionne, pas par nom

```bash
ping 1.1.1.1
ping example.com
dig example.com
cat /etc/resolv.conf
```

Si `dig` fonctionne mais pas le navigateur, suspecter le proxy, le cache applicatif ou `/etc/hosts`.

### 13.2 SERVFAIL

Le resolver n'a pas pu obtenir de réponse. Vérifier la zone, les NS, la connectivité vers les autoritatifs, et les logs.

### 13.3 NXDOMAIN

Le nom n'existe pas. Vérifier l'orthographe, la zone, le TTL négatif et les CNAME.

### 13.4 Réponse lente

```bash
dig +stats example.com
resolvectl statistics
```

Un resolver surchargé ou un serveur autoritatif lent augmente la latence. Vérifier le cache et les forwarders.

### 13.5 Split DNS

Un nom interne doit résoudre vers une IP privée à l'intérieur et publique à l'extérieur. Configurer des vues DNS ou des zones internes.

### 13.6 Cas réel : DHCP relay oublié

Un nouveau VLAN est créé, mais aucun `ip helper-address`. Les postes prennent une APIPA. On ajoute le relais sur l'interface SVI, puis on renouvelle les baux.

### 13.7 Cas réel : pool épuisé

Un pool de 100 adresses pour 150 postes. Les nouveaux clients n'obtiennent rien. `show ip dhcp pool` montre 100 % utilisé. Solution : agrandir le pool, réduire le bail, ou ajouter un VLAN.

### 13.8 Cas réel : DNS interne qui fuit

Un client utilise 8.8.8.8 et contourne le DNS interne. Les noms internes ne résolvent pas. Bloquer le DNS sortant sauf pour les resolvers autorisés, et pousser les bons serveurs via DHCP.

---

## 14. Bonnes pratiques

- Réserver les adresses des passerelles, serveurs et équipements réseau.
- Un bail adapté au réseau (plus court pour les invités).
- Toujours un relais DHCP sur les VLANs sans serveur local.
- DHCP Snooping sur les ports d'accès.
- DNS interne redondé, avec cache.
- Surveiller les pools et les conflits.
- Documenter les options DHCP (NTP, TFTP, WPAD).
- Tester la résolution interne et externe.

---

## 15. Laboratoire

1. Configurer un pool DHCP Cisco et vérifier un bail.
2. Ajouter un relais DHCP sur un deuxième VLAN.
3. Configurer dnsmasq comme DHCP + DNS.
4. Configurer une zone BIND et tester avec `dig`.
5. Activer DHCP Snooping et brancher un serveur pirate.
6. Capturer DORA avec `tcpdump` et identifier les quatre messages.

---

## 16. Mémo

```cisco
show ip dhcp binding
show ip dhcp pool
show ip dhcp conflict
show ip dhcp snooping binding
show hosts
show ip name-server
```

```bash
dhclient -v eth0
tcpdump -eni eth0 port 67 or port 68
dig +trace example.com
dig @1.1.1.1 example.com
resolvectl status
journalctl -u dnsmasq -f
```

---

## 17. Points clés

- DHCP utilise DORA et les ports UDP 67/68 ; les broadcasts ne traversent pas les routeurs sans relais.
- Le bail a des timers de renouvellement et de rebind.
- DHCP Snooping bloque les serveurs pirates et alimente les bindings.
- DNS est hiérarchique, récursif et cache ; le TTL contrôle la fraîcheur.
- Les enregistrements A/AAAA, CNAME, MX, TXT, NS et PTR couvrent la plupart des besoins.
- Un client sans adresse ou sans DNS se diagnostique avec `ip addr`, `ip route`, `dig` et une capture.
- Le split DNS est indispensable pour les noms internes.
- Toujours vérifier les options 3 et 6 : passerelle et DNS.

> **Exercice** : un poste reçoit 10.10.1.100/24 mais ne peut pas joindre Internet. Il ping 10.10.1.1 mais pas 1.1.1.1. Que vérifier ? Réponse : la passerelle par défaut (option 3), la route par défaut du routeur, le NAT, puis le DNS.

---

## 18. DHCPv6 et SLAAC

IPv6 peut attribuer des adresses de deux façons principales :

- **SLAAC** : le routeur annonce un préfixe via ICMPv6 Router Advertisement, le client construit son adresse ;
- **DHCPv6** : un serveur attribue l'adresse et/ou des options (DNS, domaine).

| Mode | Adresse | DNS | DHCPv6 |
|---|---|---|---|
| SLAAC seul | Client | Via RDNSS | Non |
| SLAAC + stateless DHCPv6 | Client | Via DHCPv6 | Oui (options) |
| DHCPv6 stateful | Serveur | Via DHCPv6 | Oui |
| DHCPv6 prefix delegation | Préfixe au routeur | — | Oui |

```cisco
interface Gi0/1
 ipv6 address 2001:db8:10::1/64
 ipv6 nd other-config-flag
 ipv6 dhcp server LAN10
!
ipv6 dhcp pool LAN10
 dns-server 2001:db8:10::53
 domain-name example.lan
```

Vérification :

```cisco
show ipv6 dhcp binding
show ipv6 dhcp pool
show ipv6 interface Gi0/1
```

Sous Linux :

```bash
ip -6 addr
ip -6 route
cat /proc/sys/net/ipv6/conf/all/accept_ra
resolvectl status
```

### 18.1 Pièges IPv6

- un routeur doit envoyer des RA pour que SLAAC fonctionne ;
- `accept_ra` doit être activé sur le client ;
- le DNS doit être annoncé via RDNSS ou DHCPv6 ;
- les firewalls doivent autoriser ICMPv6 (NDP, RA, NS/NA) ;
- le préfixe /64 est la norme pour SLAAC.

---

## 19. Délégation et reverse DNS

### 19.1 Délégation de zone

Un registraire délègue un domaine aux serveurs NS. Ces serveurs sont autoritatifs pour la zone. Pour déléguer un sous-domaine :

```text
sub.example.com.  IN NS ns1.sub.example.com.
sub.example.com.  IN NS ns2.sub.example.com.
ns1.sub.example.com. IN A 10.10.1.53
```

La glue record est nécessaire quand le NS est dans le sous-domaine délégué.

### 19.2 Reverse DNS

Le reverse DNS associe une IP à un nom via la zone `in-addr.arpa` (IPv4) ou `ip6.arpa` (IPv6).

```text
20.100.51.198.in-addr.arpa. IN PTR www.example.com.
```

Le reverse est souvent utilisé par les serveurs mail pour vérifier l'identité de l'expéditeur. Un PTR absent ou incohérent peut faire classer un mail en spam.

### 19.3 Transfert de zone

```bash
dig AXFR example.com @ns1.example.com
```

Un AXFR doit être restreint aux serveurs secondaires. Un transfert ouvert expose toute la zone.

---

## 20. Erreurs fréquentes DHCP/DNS

1. Oublier `ip helper-address` sur le VLAN client.
2. Mettre la passerelle du mauvais VLAN dans le pool.
3. Épuiser le pool sans surveillance.
4. Laisser un serveur DHCP pirate sur le réseau.
5. Oublier d'exclure les IP statiques.
6. Utiliser un DNS public pour des noms internes.
7. Laisser un TTL trop long lors d'une migration.
8. Ne pas redonder le DNS interne.
9. Autoriser les transferts de zone à tout le monde.
10. Ignorer les logs de SERVFAIL et de NXDOMAIN.

---

## 21. Check-list de mise en service

```text
[ ] Pool DHCP avec plage, passerelle, DNS, bail
[ ] Exclusions pour les équipements fixes
[ ] Relais DHCP sur chaque VLAN sans serveur local
[ ] DHCP Snooping et ports trusted
[ ] DNS interne autoritatif et redondé
[ ] Forwarders configurés et testés
[ ] Zone reverse créée
[ ] TTL adapté aux changements
[ ] Supervision des pools et des résolutions
[ ] Documentation des options DHCP
```

---

## 22. Synthèse

DHCP et DNS sont des services d'infrastructure : quand ils tombent, tout le reste semble tomber. La différence entre « pas d'adresse IP » et « adresse IP mais pas de nom » oriente immédiatement le diagnostic. Toujours vérifier les options 3 et 6, le relais, le bail, puis la résolution avec `dig` et une capture. La redondance et la supervision sont indispensables en production.
