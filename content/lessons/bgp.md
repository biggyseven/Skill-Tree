# BGP — Interconnexion et politique de routage (CCNA / Admin Réseau)

> **Objectif** : comprendre pourquoi BGP existe, comment il diffère des protocoles intérieurs, comment se forme une session eBGP/iBGP, comment sont choisies les routes, et comment filtrer proprement. Le cours couvre les attributs, le best path, les route reflectors, les communautés, la sécurité et le dépannage sur Cisco IOS et FRRouting.

---

## 1. Le rôle de BGP

BGP (Border Gateway Protocol) est le protocole de routage qui relie les **systèmes autonomes** (AS) sur Internet. Il est décrit comme un **path-vector** : chaque route transporte la liste des AS traversés, ce qui permet de détecter les boucles et d'appliquer des politiques.

| Protocole | Portée | Métrique | Politique |
|---|---|---|---|
| OSPF | Intérieur (IGP) | Coût | Limitée |
| EIGRP | Intérieur | Composite | Limitée |
| BGP | Extérieur (EGP) | Attributs | Très riche |

BGP n'est pas conçu pour la convergence rapide. Il est conçu pour **contrôler** quels préfixes sont annoncés, reçus et préférés. Un opérateur peut annoncer un préfixe à un pair et pas à un autre, préférer un transit plutôt qu'un autre, ou filtrer une communauté.

### 1.1 AS et numéros

Un AS est identifié par un numéro sur 32 bits (les numéros 16 bits historiques sont toujours utilisés). Les AS privés (64512–65534, et 4200000000–4294967294 en 32 bits) ne doivent pas apparaître sur Internet.

```text
AS 65001 (entreprise) ---- AS 64500 (FAI) ---- AS 15169 (Google)
        eBGP                    eBGP
```

---

## 2. eBGP et iBGP

| Caractéristique | eBGP | iBGP |
|---|---|---|
| AS | Différents | Même AS |
| TTL | 1 par défaut | 255 |
| Next-hop | Réécrit | Conservé |
| Synchronisation | Non | Historique |
| Boucle | AS_PATH | Split horizon iBGP |
| Port | TCP 179 | TCP 179 |

### 2.1 eBGP

Deux routeurs de systèmes autonomes différents échangent des préfixes. Le next-hop est généralement l'IP du voisin eBGP. La session doit être directe (ou `ebgp-multihop`).

```cisco
router bgp 65001
 neighbor 203.0.113.1 remote-as 64500
 network 198.51.100.0 mask 255.255.255.0
```

### 2.2 iBGP

Deux routeurs du même AS échangent des routes apprises d'ailleurs. iBGP ne réannonce pas une route apprise d'un pair iBGP à un autre pair iBGP (split horizon) : il faut un **route reflector** ou une **confédération**, ou un maillage complet.

```cisco
router bgp 65001
 neighbor 10.0.0.2 remote-as 65001
 neighbor 10.0.0.2 update-source Loopback0
 neighbor 10.0.0.2 next-hop-self
```

`next-hop-self` est souvent nécessaire pour que les routeurs internes puissent résoudre le next-hop d'une route eBGP.

---

## 3. Établissement d'une session

BGP utilise **TCP 179**. Les états d'une session :

| État | Signification |
|---|---|
| Idle | Pas de session, attente |
| Connect | Tentative TCP en cours |
| Active | Échec, nouvelle tentative |
| OpenSent | OPEN envoyé, attente de l'OPEN du pair |
| OpenConfirm | OPEN reçu, attente du KEEPALIVE |
| Established | Session établie, échange des UPDATE |

```text
R1                         R2
 |---- TCP SYN 179 -------->|
 |<--- SYN-ACK --------------|
 |---- ACK ----------------->|
 |---- OPEN ----------------->|
 |<--- OPEN ------------------|
 |---- KEEPALIVE ----------->|
 |<--- KEEPALIVE -------------|
 |===== Established =========|
```

Un blocage en `Active` signifie souvent que le TCP n'aboutit pas : IP, route, ACL, firewall, port 179, ou mauvais `remote-as`.

### 3.1 Vérification

```cisco
show ip bgp summary
show ip bgp neighbors 203.0.113.1
show tcp brief
show ip bgp
show ip route bgp
```

Extrait :

```text
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
203.0.113.1     4 64500    1204    1198       42    0    0 02:14:33       12
10.0.0.2        4 65001     890     901       42    0    0 01:02:11       35
```

`State/PfxRcd` affiche `Established` ou un nombre de préfixes reçus. `Active` ou `Idle` indique un problème.

---

## 4. Les attributs BGP

| Attribut | Type | Rôle |
|---|---|---|
| AS_PATH | Bien connu, obligatoire | Liste des AS traversés |
| NEXT_HOP | Bien connu, obligatoire | Prochain saut IP |
| ORIGIN | Bien connu, obligatoire | Origine (IGP, EGP, incomplete) |
| LOCAL_PREF | Bien connu, discrétionnaire | Préférence locale, iBGP seulement |
| MED | Optionnel, non transitif | Indication au voisin eBGP |
| COMMUNITY | Optionnel, transitif | Étiquette de politique |
| ORIGINATOR_ID | Optionnel, non transitif | Route reflector |
| CLUSTER_LIST | Optionnel, non transitif | Boucle de cluster |
| WEIGHT | Cisco, local | Préférence locale, non transmis |

### 4.1 AS_PATH

AS_PATH liste les AS traversés. Plus il est court, plus la route est généralement préférée. C'est aussi un mécanisme anti-boucle : un routeur rejette une route contenant son propre AS.

```text
198.51.100.0/24  65001 64500 15169
198.51.100.0/24  65001 64501 64502 15169
```

La première route est préférée (AS_PATH plus court). On peut rallonger artificiellement un chemin avec **AS_PATH prepending** pour influencer le trafic entrant.

```cisco
route-map PREPEND permit 10
 set as-path prepend 65001 65001 65001
```

### 4.2 NEXT_HOP

Pour eBGP, le next-hop est l'IP du voisin. Pour iBGP, il est conservé ; si le next-hop n'est pas reachable dans l'IGP, la route est inutilisable. `next-hop-self` force le routeur à annoncer sa propre IP.

### 4.3 LOCAL_PREF

LOCAL_PREF est échangé uniquement en iBGP. Valeur plus haute = préférée. C'est l'attribut de politique interne par excellence.

```cisco
route-map PREFER_PRIMARY permit 10
 set local-preference 200
!
router bgp 65001
 neighbor 10.0.0.2 route-map PREFER_PRIMARY in
```

### 4.4 MED

MED (Multi-Exit Discriminator) indique à un AS voisin quel point d'entrée préférer. Valeur plus basse = préférée. Il est échangé entre eBGP et peut être non transitif.

```cisco
route-map MED_LOW permit 10
 set metric 50
```

### 4.5 Communautés

Les communautés sont des étiquettes (ex. `65001:100`) utilisées pour appliquer des politiques. Elles sont très utilisées par les FAI.

```cisco
route-map SET_COMM permit 10
 set community 65001:100 additive
!
router bgp 65001
 neighbor 203.0.113.1 send-community
 neighbor 203.0.113.1 route-map SET_COMM out
```

Communautés bien connues : `no-export`, `no-advertise`, `local-as`.

---

## 5. Best path selection

L'ordre Cisco (simplifié) :

1. **Weight** le plus élevé (local Cisco) ;
2. **LOCAL_PREF** le plus élevé ;
3. route originaire localement (`network` ou redistribution) ;
4. **AS_PATH** le plus court ;
5. **ORIGIN** (IGP < EGP < incomplete) ;
6. **MED** le plus bas ;
7. eBGP préféré à iBGP ;
8. route avec le next-hop IGP le plus proche ;
9. plus ancienne route eBGP ;
10. plus faible Router ID ;
11. plus faible adresse de voisin.

```text
Weight  ->  LocalPref  ->  Local  ->  AS_PATH  ->  Origin
        ->  MED  ->  eBGP/iBGP  ->  IGP cost  ->  age
        ->  Router ID  ->  neighbor address
```

**Attention** : Weight est local au routeur et n'est pas transmis. LOCAL_PREF est transmis en iBGP. MED est une indication au voisin.

---

## 6. Annonce de préfixes

BGP n'annonce pas automatiquement les routes connectées. Il faut :

- `network` avec le masque exact ;
- ou redistribution avec précaution.

```cisco
router bgp 65001
 network 198.51.100.0 mask 255.255.255.0
```

La route doit exister dans la table de routage (sauf `network ... route-map` avec un default). Vérifier :

```cisco
show ip route 198.51.100.0
show ip bgp
show ip bgp neighbors 203.0.113.1 advertised-routes
```

### 6.1 Agrégation

```cisco
router bgp 65001
 aggregate-address 198.51.100.0 255.255.255.0 summary-only
```

L'agrégation réduit la table mais peut créer des trous si tous les préfixes ne sont pas présents. `summary-only` supprime les annonces détaillées.

---

## 7. Filtrage et politique

### 7.1 Prefix-list

```cisco
ip prefix-list PL_ALLOW_10 permit 10.0.0.0/8 le 24
ip prefix-list PL_DENY_ALL deny 0.0.0.0/0 le 32
!
router bgp 65001
 neighbor 203.0.113.1 prefix-list PL_ALLOW_10 in
 neighbor 203.0.113.1 prefix-list PL_DENY_ALL in
```

### 7.2 Route-map

```cisco
route-map RM_IN permit 10
 match ip address prefix-list PL_ALLOW_10
 set local-preference 150
route-map RM_IN deny 20
!
router bgp 65001
 neighbor 203.0.113.1 route-map RM_IN in
```

Une route-map sans `deny` final peut tout autoriser. Toujours terminer par un `deny`.

### 7.3 Maximum-prefix

Protection contre un pair qui annonce trop de préfixes (erreur ou attaque) :

```cisco
router bgp 65001
 neighbor 203.0.113.1 maximum-prefix 1000 80 restart 15
```

### 7.4 TTL security et BFD

```cisco
router bgp 65001
 neighbor 203.0.113.1 ttl-security hops 1
 neighbor 203.0.113.1 fall-over bfd
```

`ttl-security` protège contre les sessions BGP forgées à distance. BFD accélère la détection de panne.

---

## 8. Route reflectors et confédérations

iBGP exige un maillage complet : avec n routeurs, il faut n(n−1)/2 sessions. Un **route reflector** centralise et réfléchit les routes.

```text
        RR
       /  \
      /    \
   R1 ---- R2

RR a deux clients iBGP. Il réfléchit les routes de R1 vers R2.
```

```cisco
router bgp 65001
 neighbor 10.0.0.1 remote-as 65001
 neighbor 10.0.0.1 route-reflector-client
 neighbor 10.0.0.2 remote-as 65001
 neighbor 10.0.0.2 route-reflector-client
```

Les attributs **ORIGINATOR_ID** et **CLUSTER_LIST** évitent les boucles. Les confédérations divisent l'AS en sous-AS pour réduire le maillage.

---

## 9. BGP sous Linux avec FRRouting

```bash
apt install frr
sed -i 's/bgpd=no/bgpd=yes/' /etc/frr/daemons
systemctl restart frr
vtysh
```

```text
configure terminal
router bgp 65001
 bgp router-id 10.0.0.1
 neighbor 203.0.113.1 remote-as 64500
 network 198.51.100.0/24
!
address-family ipv4 unicast
 neighbor 203.0.113.1 activate
 exit-address-family
```

Vérification :

```text
show bgp summary
show bgp ipv4 unicast
show bgp neighbors 203.0.113.1
show ip route bgp
```

### 9.1 BIRD

```text
protocol bgp upstream {
  local as 65001;
  neighbor 203.0.113.1 as 64500;
  ipv4 {
    import filter { accept; };
    export filter { accept; };
  };
}
```

```bash
birdc show protocols
birdc show route
```

### 9.2 Capture

```bash
tcpdump -eni eth0 tcp port 179
ss -tnp | grep 179
```

---

## 10. Dépannage BGP

### 10.1 Session bloquée en Active

- IP du voisin joignable ? `ping`
- route vers le voisin ? `show ip route`
- TCP 179 autorisé ? ACL/firewall
- `remote-as` correct ?
- `update-source` correct ?
- eBGP multihop nécessaire ?

```cisco
show ip bgp summary
show ip bgp neighbors 203.0.113.1
show tcp brief
debug ip bgp 203.0.113.1
```

### 10.2 Session Established mais aucune route

- le pair n'annonce rien ;
- les prefix-lists filtrent tout ;
- le next-hop est inaccessible ;
- la route n'existe pas localement ;
- `network` sans masque exact.

```cisco
show ip bgp neighbors 203.0.113.1 advertised-routes
show ip bgp neighbors 203.0.113.1 routes
show ip bgp
show ip route 198.51.100.0
```

### 10.3 Route non installée dans la table

BGP peut avoir une route valide mais non best. Vérifier :

```cisco
show ip bgp 198.51.100.0
```

Les symboles `*>` signifient best. `*` valide mais non best, `r` RIB failure, `h` history.

### 10.4 AS_PATH loop

Une route contenant son propre AS est rejetée. Vérifier `show ip bgp` et les políticas de prepending. Un `local-as` mal configuré peut aussi créer des surprises.

### 10.5 Flapping

```cisco
show ip bgp summary
show logging | include BGP
show ip bgp neighbors 203.0.113.1 | include flaps
```

Causes : lien instable, MTU, CPU, keepalive, BFD, max-prefix. Un flap répété peut déclencher un dampening.

### 10.6 Cas réel : next-hop inaccessible

Un routeur iBGP reçoit une route eBGP avec un next-hop externe qu'il ne peut pas joindre. La route est dans `show ip bgp` mais pas dans `show ip route`. Solution : `next-hop-self` sur le routeur de bordure, ou annoncer le next-hop dans l'IGP.

### 10.7 Cas réel : max-prefix atteint

Un pair annonce accidentellement la table complète. Le routeur coupe la session. `show ip bgp summary` montre `PfxRcd` élevé et la session `Idle`. On augmente temporairement la limite, on filtre, puis on redémarre.

### 10.8 Cas réel : préfixe annoncé mais pas reçu

L'annonce est filtrée par une prefix-list sortante ou par un `distribute-list`. Vérifier `advertised-routes` côté émetteur et `routes` côté récepteur. Les deux côtés doivent être examinés.

---

## 11. Sécurité BGP

- authentification TCP MD5 (ou TCP-AO) ;
- TTL security ;
- prefix-list stricte en entrée et en sortie ;
- maximum-prefix ;
- filtrage des AS privés et des préfixes bogon ;
- protection contre les annonces de préfixes trop spécifiques ;
- surveillance des changements d'AS_PATH ;
- RPKI dans la mesure du possible.

```cisco
router bgp 65001
 neighbor 203.0.113.1 password MOT_DE_PASSE
 neighbor 203.0.113.1 ttl-security hops 1
 neighbor 203.0.113.1 maximum-prefix 1000
```

---

## 12. Laboratoire

1. Configurer une session eBGP entre deux AS et annoncer un préfixe.
2. Configurer iBGP avec `next-hop-self` et vérifier la table.
3. Ajouter un route reflector et supprimer le maillage complet.
4. Utiliser LOCAL_PREF pour préférer un chemin, puis AS_PATH prepending pour le trafic entrant.
5. Filtrer un préfixe avec une prefix-list et vérifier `advertised-routes`.
6. Provoquer un max-prefix et observer la session.

---

## 13. Mémo

```cisco
show ip bgp summary
show ip bgp
show ip bgp 198.51.100.0
show ip bgp neighbors 203.0.113.1
show ip bgp neighbors 203.0.113.1 advertised-routes
show ip bgp neighbors 203.0.113.1 routes
show ip route bgp
show tcp brief
clear ip bgp * soft
```

```bash
vtysh -c 'show bgp summary'
vtysh -c 'show bgp ipv4 unicast'
birdc show protocols
tcpdump -eni eth0 tcp port 179
```

---

## 14. Points clés

- BGP est un protocole de politique, pas seulement de plus court chemin.
- eBGP entre AS, iBGP dans un AS ; iBGP ne réannonce pas les routes iBGP sans RR.
- Les attributs déterminent la sélection : Weight, LOCAL_PREF, AS_PATH, ORIGIN, MED.
- Le next-hop doit être reachable via l'IGP, sinon la route est inutilisable.
- `network` exige un masque exact et une route présente localement.
- Les prefix-lists et route-maps sont indispensables pour filtrer.
- `maximum-prefix` et TTL security protègent la session.
- Une session `Active` est un problème TCP ; une session `Established` sans routes est un problème de politique.

> **Exercice** : une route est visible dans `show ip bgp` mais absente de `show ip route`. Donnez trois causes possibles. Réponse : next-hop inaccessible, route non best, ou RIB failure ; vérifier `show ip bgp <préfixe>` et la route vers le next-hop.

---

## 15. Étude de cas : double connexion à deux FAI

Une entreprise dispose de deux liens vers deux FAI, avec un bloc d'adresses publiques et un AS. Objectif : préférer le FAI principal, basculer sur le second en cas de panne, et ne jamais devenir un transit.

**Plan d'adressage.** Un AS public, deux sessions eBGP, un bloc IPv4 et un bloc IPv6. Les routeurs de bordure sont reliés au cœur par iBGP. Le bloc est annoncé par les deux routeurs, mais l'un est préféré.

**Politique sortante.** Utiliser LOCAL_PREF pour préférer le FAI principal.

```cisco
route-map PREF_FAI1 permit 10
 set local-preference 200
route-map PREF_FAI2 permit 10
 set local-preference 100
!
router bgp 65001
 neighbor 203.0.113.1 remote-as 64500
 neighbor 203.0.113.1 route-map PREF_FAI1 in
 neighbor 198.51.100.1 remote-as 64501
 neighbor 198.51.100.1 route-map PREF_FAI2 in
```

**Politique entrante.** Utiliser AS_PATH prepending pour influencer le trafic entrant, avec précaution. Le prepending n'est pas une garantie : les FAI peuvent appliquer leurs propres politiques.

```cisco
route-map TO_FAI2 permit 10
 set as-path prepend 65001 65001
!
router bgp 65001
 neighbor 198.51.100.1 route-map TO_FAI2 out
```

**Filtrage.** Annoncer uniquement le bloc détenu, jamais les routes apprises des FAI. Utiliser une prefix-list sortante stricte.

```cisco
ip prefix-list OUR_BLOCK permit 198.51.100.0/24
ip prefix-list DENY_ALL deny 0.0.0.0/0 le 32
!
router bgp 65001
 neighbor 203.0.113.1 prefix-list OUR_BLOCK out
 neighbor 203.0.113.1 prefix-list DENY_ALL out
```

**Vérification.** Contrôler les sessions, les routes reçues, les routes annoncées, et le best path.

```cisco
show ip bgp summary
show ip bgp
show ip bgp neighbors 203.0.113.1 advertised-routes
show ip route bgp
```

**Bascule.** Couper le lien principal et vérifier que le trafic sortant passe par le FAI 2. Vérifier que le retour arrive toujours. Un changement de préférence sortante ne garantit pas le retour ; il faut tester dans les deux sens.

### 15.1 Pièges

- annoncer les routes apprises des FAI (transit accidentel) ;
- oublier `next-hop-self` en iBGP ;
- utiliser des communautés sans documentation ;
- laisser `maximum-prefix` trop haut ;
- ne pas filtrer les préfixes bogon ;
- modifier LOCAL_PREF sans comprendre l'impact sur tous les routeurs ;
- oublier IPv6.

### 15.2 Check-list

```text
[ ] Sessions eBGP/iBGP Established
[ ] Préfixes annoncés conformes au bloc
[ ] Aucun transit accidentel
[ ] LOCAL_PREF documenté
[ ] AS_PATH prepending testé
[ ] Prefix-lists entrantes et sortantes
[ ] maximum-prefix configuré
[ ] Next-hop reachable
[ ] Bascule testée dans les deux sens
[ ] Supervision des sessions
```

### 15.3 Ce qu'il faut retenir

BGP est un outil de politique. Une configuration qui « marche » peut être dangereuse si elle annonce trop de préfixes ou accepte n'importe quoi. La sécurité et la documentation comptent autant que le best path. Toujours vérifier ce qui est annoncé, pas seulement ce qui est reçu.
