# IPv4 et subnetting — parcours intensif Admin Réseau Senior

> **Objectif.** À la fin de ce cours, vous devez pouvoir lire une adresse avec
> son préfixe, calculer son masque et son wildcard, trouver rapidement le réseau,
> le broadcast et la plage d'hôtes, concevoir un plan VLSM sans gaspiller
> d'adresses, puis vérifier une configuration sur un routeur Cisco ou un hôte
> Linux.
>
> **Niveau :** administrateur réseau senior, avec rappels CCNA et pratique de
> conception, d'exploitation et de dépannage.
>
> **Durée indicative :** 60 à 90 minutes, exercices et atelier compris.

## 1. Ce que représente une adresse IPv4

IPv4 identifie une interface au niveau de la couche réseau. Une adresse contient
32 bits, souvent écrits en quatre octets décimaux séparés par des points :

```text
192.168.1.130
  192   . 168 .  1  . 130      notation décimale pointée
11000000.10101000.00000001.10000010  représentation binaire
```

Le masque de sous-réseau sépare ces bits en deux champs :

```text
|<--------- préfixe réseau --------->|<------ bits hôte ------>|
11000000.10101000.00000001.10        000010
```

Un préfixe `/n` signifie que les `n` bits de gauche appartiennent à la partie
réseau. Les bits restants identifient une interface dans ce sous-réseau. Ainsi,
`192.168.1.130/26` a 26 bits réseau et `32 - 26 = 6` bits hôte.

Le préfixe ne désigne pas à lui seul une interface : il décrit l'adresse et la
taille de son sous-réseau. La même adresse configurée avec `/24` et `/26`
n'appartient pas au même réseau.

## 2. Classes historiques : A, B, C, D et E

Avant le routage sans classe (CIDR), les premiers bits de l'adresse indiquaient
une classe, et les réseaux utilisaient des masques par défaut. Cette histoire
explique plusieurs termes encore présents dans les commandes et les examens.
**Les classes A/B/C ne servent plus à attribuer le masque d'un réseau moderne** :
le préfixe configuré ou annoncé par CIDR fait foi.

| Classe | Bits de tête | Premier octet historique | Masque « par défaut » historique | Usage |
| --- | --- | ---: | --- | --- |
| A | `0` | 1–126 | `/8` (`255.0.0.0`) | Grandes organisations, notion désormais historique |
| B | `10` | 128–191 | `/16` (`255.255.0.0`) | Organisations moyennes, notion désormais historique |
| C | `110` | 192–223 | `/24` (`255.255.255.0`) | Petits réseaux, notion désormais historique |
| D | `1110` | 224–239 | Aucun masque unicast | Multicast |
| E | `1111` | 240–255 | Aucun masque unicast | Réservé / expérimental, avec exceptions spéciales |

`127.0.0.0/8` est réservé au loopback, dont `127.0.0.1`. L'adresse `0.0.0.0`
et l'adresse limitée de broadcast `255.255.255.255` ont également des rôles
spéciaux. Les règles pratiques se déterminent à partir du préfixe et de
l'allocation actuelle, pas seulement du premier octet.

### Pourquoi CIDR a remplacé les classes

Les classes forçaient des tailles très grossières : un réseau de classe C
traditionnel avait 256 adresses, tandis qu'une classe B en avait 65 536.
CIDR (*Classless Inter-Domain Routing*) autorise tout préfixe utile, par exemple
`/27`, `/20` ou `/30`, et permet l'agrégation :

```text
10.40.0.0/24
10.40.1.0/24  } peuvent être annoncés ensemble comme 10.40.0.0/23
```

Cette agrégation réduit le nombre de routes annoncées, si les blocs sont
contigus et correctement alignés. Les tables de routage sélectionnent d'abord
la route correspondant au préfixe le plus long.

## 3. Masque, préfixe et wildcard

### Convertir le préfixe en masque

Dans un masque, les bits réseau sont des `1` contigus à gauche ; les bits hôte
sont des `0` contigus à droite.

```text
/26 = 11111111.11111111.11111111.11000000
    = 255.255.255.192
```

Les valeurs possibles d'un octet de masque, lorsqu'il est partiellement rempli,
sont les sommes de bits de poids fort :

| Bits à 1 | Binaire | Décimal |
| ---: | --- | ---: |
| 0 | `00000000` | 0 |
| 1 | `10000000` | 128 |
| 2 | `11000000` | 192 |
| 3 | `11100000` | 224 |
| 4 | `11110000` | 240 |
| 5 | `11111000` | 248 |
| 6 | `11111100` | 252 |
| 7 | `11111110` | 254 |
| 8 | `11111111` | 255 |

Exemple : `/20` comprend 16 bits dans les deux premiers octets, puis 4 bits
dans le troisième :

```text
11111111.11111111.11110000.00000000
255.255.240.0
```

### Wildcard mask

Le wildcard est le complément bit à bit du masque :

```text
wildcard = 255.255.255.255 - masque
```

Exemples :

| Préfixe | Masque | Wildcard |
| --- | --- | --- |
| `/24` | `255.255.255.0` | `0.0.0.255` |
| `/26` | `255.255.255.192` | `0.0.0.63` |
| `/20` | `255.255.240.0` | `0.0.15.255` |
| `/30` | `255.255.255.252` | `0.0.0.3` |

Sur Cisco, un wildcard est souvent utilisé dans les ACL et les commandes OSPF.
`0` signifie « le bit doit correspondre » et `1` signifie « ignorer ce bit ».
Pour sélectionner `192.168.1.64/26`, la wildcard est `0.0.0.63` :

```text
access-list 10 permit 192.168.1.64 0.0.0.63
router ospf 10
 network 192.168.1.64 0.0.0.63 area 0
```

Une wildcard n'est pas toujours simplement un masque de sous-réseau classique
inversé : les ACL peuvent utiliser des wildcards non contiguës pour sélectionner
des motifs particuliers. Dans un calcul de subnetting ordinaire, utilisez le
complément du masque.

## 4. Adresse réseau, broadcast et hôtes

Pour un préfixe `/n`, le nombre de bits hôte est `h = 32 - n`. Le nombre total
de motifs binaires dans le bloc est `2^h`. Dans un sous-réseau IPv4 unicast
classique, la première adresse représente le réseau et la dernière est le
broadcast dirigé ; le nombre d'adresses hôte utilisables est donc généralement
`2^h - 2`.

| Préfixe | Bits hôte | Adresses totales | Hôtes classiques utilisables |
| --- | ---: | ---: | ---: |
| `/24` | 8 | 256 | 254 |
| `/25` | 7 | 128 | 126 |
| `/26` | 6 | 64 | 62 |
| `/27` | 5 | 32 | 30 |
| `/28` | 4 | 16 | 14 |
| `/29` | 3 | 8 | 6 |
| `/30` | 2 | 4 | 2 |
| `/31` | 1 | 2 | 2 sur un lien point-à-point RFC 3021 |
| `/32` | 0 | 1 | Une route hôte, pas un LAN partagé |

Les `/31` sont valides pour certains liens point-à-point : les deux adresses
sont utilisables comme extrémités, sans broadcast traditionnel. Un `/32`
représente une seule adresse, fréquemment utilisée pour une loopback ou une
route hôte. Ne leur appliquez donc pas aveuglément la formule `-2`.

### Opérations binaires

Conceptuellement :

```text
adresse réseau = adresse IP AND masque
broadcast      = adresse IP OR wildcard
```

Prenons `192.168.1.130/26` :

```text
IP       : 192.168.1.130 = 11000000.10101000.00000001.10 000010
Masque   : 255.255.255.192 = 11111111.11111111.11111111.11 000000
Réseau   : 192.168.1.128 = 11000000.10101000.00000001.10 000000
Broadcast: 192.168.1.191 = 11000000.10101000.00000001.10 111111
```

Donc :

| Élément | Valeur |
| --- | --- |
| Adresse configurée | `192.168.1.130/26` |
| Masque | `255.255.255.192` |
| Réseau | `192.168.1.128/26` |
| Première adresse hôte | `192.168.1.129` |
| Dernière adresse hôte | `192.168.1.190` |
| Broadcast dirigé | `192.168.1.191` |
| Capacité classique | 62 hôtes |

## 5. Subnetting mental : la méthode du pas

La méthode du pas évite de convertir les quatre octets en binaire à chaque
question.

### Procédure

1. Repérez l'octet du masque qui n'est ni `255` ni `0`.
2. Calculez le **pas** : `256 - valeur de cet octet`.
3. Les réseaux de cet octet commencent à `0`, puis progressent du pas.
4. Trouvez le plus grand multiple du pas inférieur ou égal à l'octet de l'IP.
5. Ce multiple est le début du bloc ; l'adresse juste avant le bloc suivant est
   son broadcast.
6. Ajoutez `1` au réseau et soustrayez `1` au broadcast pour la plage d'hôtes,
   sauf cas `/31` ou `/32`.

### Exemple guidé : `172.20.77.201/20`

`/20` donne le masque `255.255.240.0`. L'octet intéressant est le troisième :
`256 - 240 = 16`. Les frontières de réseau sont donc :

```text
... . 0 . ...
... .16 . ...
... .32 . ...
... .48 . ...
... .64 . ...
... .80 . ...
```

Le troisième octet vaut `77`. Il est compris entre `64` et `79` :

```text
Réseau     : 172.20.64.0/20
Broadcast  : 172.20.79.255
Hôtes      : 172.20.64.1 – 172.20.79.254
Pas        : 16 dans le troisième octet
```

### Exemple dans le quatrième octet : `10.2.5.146/27`

`/27` donne `255.255.255.224`. Le pas vaut `256 - 224 = 32`. Les blocs du
dernier octet sont `0–31`, `32–63`, `64–95`, `96–127`, `128–159`, etc.
`146` appartient à `128–159` :

```text
Réseau     : 10.2.5.128/27
Broadcast  : 10.2.5.159
Hôtes      : 10.2.5.129 – 10.2.5.158
Total      : 32 adresses, 30 hôtes classiques
Wildcard   : 0.0.0.31
```

### Astuces de calcul rapides

- Mémorisez les octets de masque `128, 192, 224, 240, 248, 252, 254`.
- Pour `/18`, le masque est `255.255.192.0`, le pas du troisième octet est 64.
- Pour `/21`, le masque est `255.255.248.0`, le pas est 8 au troisième octet.
- Pour `/23`, le masque est `255.255.254.0`, le pas est 2 au troisième octet.
- Le pas indique la taille du bloc dans l'octet intéressant, pas toujours le
  nombre d'hôtes.
- Vérifiez l'alignement : un réseau `/26` ne peut commencer que sur un multiple
  de 64 au quatrième octet (`.0`, `.64`, `.128`, `.192`).

## 6. Choisir un préfixe à partir du nombre d'hôtes

Pour dimensionner un LAN classique, trouvez le plus petit `h` tel que
`2^h - 2` soit au moins égal au nombre d'hôtes requis, puis calculez
`préfixe = 32 - h`.

**Exemple :** un service a besoin de 50 adresses pour des équipements.

```text
h = 5  -> 2^5 - 2 = 30  (insuffisant)
h = 6  -> 2^6 - 2 = 62  (suffisant)
préfixe = 32 - 6 = /26
```

Un `/26` fournit 62 adresses classiques utilisables. Tenez compte des
interfaces de routeur, imprimantes, points d'accès, équipements de management,
croissance et réserves. Les « 50 postes » annoncés ne représentent pas toujours
la totalité des adresses consommées.

## 7. VLSM : adapter les sous-réseaux aux besoins

Le **VLSM** (*Variable Length Subnet Mask*) attribue des préfixes différents à
des segments différents. Il réduit le gaspillage par rapport à une série de
sous-réseaux tous de même taille. La règle essentielle est de dimensionner le
plus grand besoin en premier, puis d'allouer chaque bloc à une frontière valide.

### Besoin d'une entreprise

On nous attribue `10.20.0.0/24` (256 adresses). Il faut planifier :

| Segment | Besoin estimé |
| --- | ---: |
| Utilisateurs | 100 hôtes |
| Wi-Fi | 50 hôtes |
| Téléphonie | 20 hôtes |
| Administration | 10 hôtes |
| Lien point-à-point entre routeurs | 2 interfaces |

Pour chaque LAN, ajoutons une marge raisonnable, puis choisissons le plus petit
bloc suffisant. Le bloc final d'un lien dédié peut être `/30` dans un exercice
classique, ou `/31` si les équipements supportent RFC 3021.

### Calcul et allocation, du plus grand au plus petit

1. **Utilisateurs :** 100 hôtes. `2^7 - 2 = 126`, donc `/25` (128 adresses).
   Première frontière disponible : `10.20.0.0`.
2. **Wi-Fi :** 50 hôtes. `/26` fournit 62 hôtes. Le bloc suivant commence à
   `10.20.0.128`, frontière correcte de 64.
3. **Téléphonie :** 20 hôtes. `/27` fournit 30 hôtes. Après `.191`, le prochain
   bloc `/27` est `.192`.
4. **Administration :** 10 hôtes. `/28` fournit 14 hôtes. Après le bloc
   `192–223`, le prochain `/28` commence à `.224`.
5. **Lien routeur :** `/30` demande une frontière multiple de 4. Le `/28`
   précédent finit à `.239`, donc on utilise le bloc `.240–.243`.

| Usage | Sous-réseau | Masque | Plage d'hôtes | Broadcast |
| --- | --- | --- | --- | --- |
| Utilisateurs | `10.20.0.0/25` | `255.255.255.128` | `.1 – .126` | `10.20.0.127` |
| Wi-Fi | `10.20.0.128/26` | `255.255.255.192` | `.129 – .190` | `10.20.0.191` |
| Téléphonie | `10.20.0.192/27` | `255.255.255.224` | `.193 – .222` | `10.20.0.223` |
| Administration | `10.20.0.224/28` | `255.255.255.240` | `.225 – .238` | `10.20.0.239` |
| Transit | `10.20.0.240/30` | `255.255.255.252` | `.241 – .242` | `10.20.0.243` |
| Réserve | `10.20.0.244 – 10.20.0.255` | — | Disponible pour extension | — |

Vue compacte :

```text
10.20.0.0                                                        10.20.0.255
|------------------- /25 -------------------|
                                            |------ /26 ------|
                                                              |-- /27 --|
                                                                        |- /28 -|
                                                                                 /30
                                                                                      réserve
```

Les frontières sont contiguës, sans chevauchement. Il reste 12 adresses brutes
dans le bloc, ce qui peut accueillir un petit transit ou être réalloué selon la
croissance. Le VLSM évite ici d'attribuer cinq `/25`, qui auraient dépassé le
bloc disponible.

### Bonnes pratiques VLSM

- Trier les besoins du plus grand au plus petit avant l'allocation.
- Réserver un bloc agrégable par site ou par résumé de routage.
- Aligner chaque réseau sur une frontière de sa taille.
- Documenter réseau, masque, gateway, broadcast, VLAN, usage et propriétaire.
- Ne pas réutiliser des blocs sans vérifier les VPN, routes statiques, ACL et
  connexions partenaires.
- Prévoir la croissance et la redondance ; un plan qui ne laisse aucune marge
  est fragile.
- Laisser des blocs réservés et documentés plutôt que de distribuer au hasard
  les dernières adresses libres.

## 8. Adresses privées, publiques et spéciales

Les plages privées définies par RFC 1918 ne sont pas annoncées sur l'Internet
public. Elles peuvent être réutilisées par des organisations différentes.

| Plage privée | Préfixe | Taille | Usage courant |
| --- | --- | ---: | --- |
| `10.0.0.0 – 10.255.255.255` | `10.0.0.0/8` | 16 777 216 adresses | Réseaux d'entreprise ou cloud |
| `172.16.0.0 – 172.31.255.255` | `172.16.0.0/12` | 1 048 576 adresses | Réseaux internes |
| `192.168.0.0 – 192.168.255.255` | `192.168.0.0/16` | 65 536 adresses | LAN domestiques et petits sites |

Autres blocs à reconnaître :

| Plage | Rôle |
| --- | --- |
| `127.0.0.0/8` | Loopback |
| `169.254.0.0/16` | Link-local IPv4 / APIPA |
| `100.64.0.0/10` | Espace partagé souvent utilisé par le CGNAT opérateur |
| `224.0.0.0/4` | Multicast |
| `255.255.255.255` | Broadcast limité |

Une adresse privée peut être routée à l'intérieur d'un domaine privé, mais les
routeurs Internet ne l'acheminent pas comme destination publique globale.
L'utilisation de plages privées n'élimine pas les conflits : deux sites
connectés par VPN peuvent tous deux utiliser `192.168.1.0/24`. Un plan IP
hiérarchique et non chevauchant évite ces problèmes.

### Où le NAT intervient

Le NAT (*Network Address Translation*) modifie une ou plusieurs adresses IP
dans les paquets qui traversent une frontière. Le PAT (souvent appelé NAT
overload) partage une adresse publique en distinguant les sessions avec les
ports de transport.

```text
PC privé                  Routeur/NAT                    Internet
10.20.0.50:51514  ---->  203.0.113.8:40001  ---->  serveur public
                           table d'état
```

Exemple de traduction :

```text
Avant : source 10.20.0.50:51514
Après : source 203.0.113.8:40001
```

La table d'état permet au routeur de traduire la réponse vers `10.20.0.50:51514`.
Le NAT ne remplace pas le routage : il faut toujours une route correcte à
l'aller et au retour. Il n'est pas non plus, à lui seul, un pare-feu ; les
politiques de filtrage et l'état des connexions doivent être configurés
explicitement.

Exemple Cisco IOS simplifié :

```text
interface GigabitEthernet0/0
 description LAN
 ip address 10.20.0.1 255.255.255.0
 ip nat inside
 no shutdown
!
interface GigabitEthernet0/1
 description Vers fournisseur
 ip address 203.0.113.8 255.255.255.252
 ip nat outside
 no shutdown
!
access-list 10 permit 10.20.0.0 0.0.0.255
ip nat inside source list 10 interface GigabitEthernet0/1 overload
ip route 0.0.0.0 0.0.0.0 203.0.113.9
```

`203.0.113.0/24` est réservé à la documentation : les adresses ci-dessus sont
des exemples, pas des paramètres à déployer sur l'Internet réel.

Commandes utiles :

```text
show ip interface brief
show ip route
show ip nat translations
show ip nat statistics
show access-lists
```

Sur Linux, `ip addr` configure les interfaces, tandis que NAT est généralement
fourni par nftables ou iptables. L'adressage et le routage restent distincts
des règles de traduction.

## 9. Configurer et vérifier une adresse

### Cisco IOS

```text
enable
configure terminal
interface GigabitEthernet0/0
 description VLAN utilisateurs
 ip address 192.168.1.129 255.255.255.192
 no shutdown
end
show ip interface brief
show running-config interface GigabitEthernet0/0
show ip route connected
```

Sur un routeur, `no shutdown` est nécessaire si l'interface est administratively
down. Une adresse de passerelle doit appartenir au même sous-réseau que les
hôtes qui l'utilisent.

### Linux (iproute2)

```bash
sudo ip address add 192.168.1.129/26 dev eth0
sudo ip link set eth0 up
ip -br address show dev eth0
ip route
ip route get 192.168.1.150
ping -c 3 192.168.1.150
```

Les commandes `ip address add` sont généralement temporaires jusqu'au prochain
redémarrage ; la configuration persistante dépend de la distribution et de son
gestionnaire réseau.

### Diagnostic par étapes

1. **Lien :** interface active, bon VLAN, vitesse/duplex et absence d'erreurs.
2. **Adresse :** IP et préfixe corrects, pas de doublon d'adresse.
3. **Réseau local :** comparer réseau calculé et gateway ; vérifier ARP.
4. **Routage :** contrôler route connectée, route par défaut et prochain saut.
5. **Retour :** vérifier que le réseau distant sait revenir vers le préfixe
   source ; un ping à sens unique indique souvent un chemin retour manquant.
6. **Filtrage/NAT :** consulter ACL, pare-feu, translations et compteurs.

```text
Cisco : show ip interface brief | show ip route | show arp
Linux : ip addr | ip route | ip neigh | ping -c 3 <destination>
```

Un ping vers sa propre adresse valide peu de choses au-delà de la pile locale.
Un ping vers la gateway teste davantage, mais un échec peut venir d'une ACL ICMP,
pas nécessairement d'une panne de routage. Complétez avec traceroute, ARP,
journaux et capture de paquets selon le contexte.

## 10. Erreurs fréquentes à éviter

- **Confondre adresse hôte et adresse réseau.** `192.168.1.130/26` est une
  adresse hôte ; son réseau est `192.168.1.128/26`.
- **Calculer le réseau avec le mauvais préfixe.** Le troisième octet peut aussi
  contenir des bits hôte, par exemple en `/20` ou `/21`.
- **Prendre le pas pour la capacité hôte.** En `/26`, le pas vaut 64 adresses,
  mais la capacité classique est 62 hôtes.
- **Utiliser les classes comme règle moderne.** `172.20.0.0` ne signifie pas
  automatiquement `/16` : c'est le préfixe qui décide.
- **Attribuer la première ou dernière adresse d'un bloc comme hôte** sur un
  LAN classique : elles identifient réseau et broadcast.
- **Oublier les liens point-à-point.** `/31` est valide dans plusieurs
  environnements ; ne le rejetez pas automatiquement comme « zéro hôte ».
- **Créer un chevauchement VLSM.** Vérifiez que le broadcast d'un bloc précède
  l'adresse réseau du suivant.
- **Penser que NAT répare une route manquante.** Le NAT traduit ; il ne crée pas
  une route vers le réseau de destination.
- **Oublier le chemin retour.** Une requête peut atteindre le serveur, mais sa
  réponse peut repartir vers une route différente ou inexistante.

## 11. Exercices avec corrigé

### Exercice A

Pour `192.168.1.130/26`, donnez le masque, le réseau, la plage d'hôtes, le
broadcast et le wildcard.

**Corrigé :** `/26 = 255.255.255.192`, pas de 64, bloc `.128–.191` ;
réseau `192.168.1.128`, hôtes `.129–.190`, broadcast `.191`, wildcard
`0.0.0.63`.

### Exercice B

Un réseau doit fournir au moins 25 adresses d'hôtes. Quel est le plus petit
préfixe classique ?

**Corrigé :** cinq bits donnent `2^5 - 2 = 30` hôtes, donc `/27`. Un `/28`
n'en fournirait que 14.

### Exercice C

Quelle est l'adresse réseau de `172.16.35.200/21` ?

**Corrigé :** masque `255.255.248.0`, pas `8` dans le troisième octet.
`35` se trouve dans le bloc `32–39` ; réseau `172.16.32.0/21`, broadcast
`172.16.39.255`.

### Exercice D

Une ACL doit correspondre à `10.4.8.0/22`. Quelle wildcard utiliser ?

**Corrigé :** le masque est `255.255.252.0`, son complément est
`0.0.3.255`.

## À retenir

```text
hôtes classiques = 2^(32 - préfixe) - 2
wildcard         = 255.255.255.255 - masque
pas              = 256 - octet de masque partiel
réseau           = adresse AND masque
```

Utilisez CIDR plutôt que les classes pour tout plan moderne. Pour un subnetting
rapide, trouvez le pas et les frontières, puis vérifiez réseau, broadcast et
plage. Pour du VLSM, allouez du plus grand besoin au plus petit, en respectant
l'alignement et en documentant chaque bloc. Enfin, séparez bien l'adressage,
le routage, le filtrage et le NAT : ce sont des fonctions complémentaires, pas
des solutions interchangeables.

---

## 12. Exploitation IPv4 avancée : le chemin d'un paquet

L'adressage n'est qu'une partie du transfert. Pour diagnostiquer un flux, suivez
le paquet à chaque décision : l'hôte choisit sa route, résout le prochain saut
sur le lien local, puis chaque routeur décrémente le TTL et choisit une route.
Les adresses source et destination restent normalement inchangées en transit;
le NAT constitue une exception explicite.

```text
Hôte A                 Passerelle R1                 Routeur R2            Serveur B
192.168.10.25/24        192.168.10.1                  10.0.0.2              10.30.4.20/23
     |                       |                             |                       |
     | IP dst=10.30.4.20     | IP dst=10.30.4.20          | IP dst=10.30.4.20     |
     | Ethernet dst=MAC-R1   | Ethernet dst=MAC-R2         | Ethernet dst=MAC-B    |
     +---------------------->|---------------------------->|---------------------->+
        nouveau en-tête L2       nouveau TTL/checksum          nouveau en-tête L2
```

L'adresse Ethernet de destination change à chaque segment Ethernet; l'adresse
IP de destination ne change pas, sauf traduction ou proxy. Le routeur ne
recherche pas la MAC du serveur distant : il recherche la MAC du **prochain saut**
sur son réseau de sortie.

### Décision de route : préfixe le plus long

Un routeur utilise la route la plus spécifique qui correspond à la destination.
Considérons cette table :

| Préfixe | Prochain saut | Interprétation |
| --- | --- | --- |
| `0.0.0.0/0` | `192.0.2.1` | route par défaut |
| `10.0.0.0/8` | `192.0.2.5` | agrégat privé |
| `10.30.0.0/16` | `192.0.2.9` | site régional |
| `10.30.4.0/23` | directement connecté | LAN du serveur |

Pour `10.30.4.20`, le `/23` gagne, même si les trois autres routes sont aussi
des correspondances. Cette règle s'appelle *longest-prefix match*. La distance
administrative et la métrique servent à départager des routes concurrentes
vers le même préfixe; elles ne font pas préférer une route moins spécifique à
un préfixe plus long.

Sur Cisco IOS :

```text
show ip route
show ip route 10.30.4.20
show ip cef 10.30.4.20
show ip protocols
```

`show ip route <destination>` explique la route retenue. `show ip cef` montre le
résultat de transfert optimisé; une route présente dans la table de routage
mais absente/inexploitable dans CEF mérite une investigation propre à la
plateforme. Sur Linux, comparez la règle et la décision réelle :

```bash
ip route
ip route get 10.30.4.20
ip rule show
ip route show table all
```

Les politiques `ip rule` et les tables multiples peuvent faire choisir une
route différente de la table `main`. Vérifiez aussi le VRF ou le namespace
concerné avant de conclure à une incohérence.

## 13. ARP, passerelle et trafic local

IPv4 utilise ARP sur un réseau local Ethernet pour associer une adresse IPv4
voisine à une adresse MAC. Un hôte compare d'abord la destination à son propre
préfixe :

1. Si la destination est sur le même réseau, il émet une requête ARP pour la
   destination.
2. Sinon, il émet ARP pour la passerelle configurée, puis envoie la trame à
   cette MAC avec l'IP distante comme destination.
3. Les entrées ARP sont mises en cache pour éviter une requête à chaque paquet.

```text
Même réseau : 192.168.10.25/24  -> ARP pour 192.168.10.80
Hors réseau : 192.168.10.25/24  -> ARP pour 192.168.10.1 (gateway)
                                      IP destination reste 10.30.4.20
```

Une erreur classique consiste à configurer une adresse correcte mais un masque
trop large. Par exemple, `192.168.10.25/16` considère `192.168.20.10` comme
local; l'hôte essaie alors ARP directement au lieu d'envoyer le paquet au
routeur. Le résultat est souvent une résolution ARP incomplète et une panne
qui semble limitée à certains sous-réseaux.

Commandes de vérification :

```text
Cisco IOS : show arp
Cisco IOS : show ip arp 192.168.10.25
Linux     : ip neigh show
Linux     : sudo ip neigh flush dev eth0
Linux     : sudo arping -I eth0 192.168.10.1
```

N'effacez pas une table ARP en production comme premier réflexe : capturez
d'abord l'entrée et son état. Une entrée `INCOMPLETE` indique qu'aucune réponse
n'a été reçue; une adresse MAC inattendue peut révéler un doublon, un proxy ARP
ou une attaque de type usurpation ARP. Les états Linux incluent notamment
`REACHABLE`, `STALE`, `DELAY`, `PROBE` et `FAILED`.

## 14. DHCP, adresses statiques et relais

DHCP automatise la configuration de l'hôte. Le cycle classique DORA est :

| Étape | Message | Rôle |
| --- | --- | --- |
| 1 | Discover | le client diffuse une recherche de serveur |
| 2 | Offer | un serveur propose un bail et des options |
| 3 | Request | le client demande l'offre retenue |
| 4 | Acknowledge | le serveur confirme le bail |

Le client initial n'ayant pas encore d'IP, les messages utilisent le broadcast
IPv4 local et UDP ports 68 (client) et 67 (serveur). Un serveur situé dans un
autre sous-réseau n'entend pas ces broadcasts : la passerelle doit relayer la
requête. Les options usuelles comprennent le masque (option 1), la passerelle
(option 3), les DNS (option 6), le nom de domaine (option 15) et la durée du
bail (option 51).

Configuration DHCP simplifiée sur IOS :

```text
configure terminal
ip dhcp excluded-address 10.50.10.1 10.50.10.30
ip dhcp pool USERS-VLAN10
 network 10.50.10.0 255.255.255.0
 default-router 10.50.10.1
 dns-server 10.50.0.53 10.50.0.54
 domain-name corp.example
 lease 7
!
interface Vlan10
 ip address 10.50.10.1 255.255.255.0
 ip helper-address 10.50.0.20
 no shutdown
end
show ip dhcp binding
show ip dhcp pool
show running-config interface Vlan10
```

`ip helper-address` relaie plusieurs types de broadcasts UDP, pas uniquement
DHCP; contrôlez les services relayés et les ACL associées. Un relais peut
ajouter l'identifiant d'interface (option 82) pour permettre au serveur de
sélectionner le bon pool. Une mauvaise adresse de relais, une route retour
absente, un pool épuisé ou un VLAN incorrect peuvent tous donner un client sans
bail.

Sur un serveur Linux de laboratoire utilisant `dnsmasq`, un exemple explicite
est :

```ini
interface=eth0
bind-interfaces
dhcp-range=10.50.10.100,10.50.10.220,255.255.255.0,12h
dhcp-option=option:router,10.50.10.1
dhcp-option=option:dns-server,10.50.0.53,10.50.0.54
dhcp-authoritative
```

La configuration exacte dépend du service et de la distribution. Ne lancez pas
un deuxième serveur DHCP sur un VLAN de production pour tester : cela peut
distribuer une passerelle ou des DNS incorrects à l'ensemble des clients.

### Gestion des baux et réservations

Une réservation DHCP associe un identifiant de client (souvent MAC ou client
identifier) à une adresse choisie. Elle facilite l'exploitation, mais ne
remplace ni une documentation IPAM ni le contrôle des doublons. Avant de
modifier un pool :

- vérifiez les baux actifs, les exclusions et les réservations;
- confirmez le masque et la gateway réellement distribués;
- estimez le pic simultané et la durée du bail, pas seulement le nombre
  d'appareils inventoriés;
- prévoyez les options différentes pour voix, Wi-Fi, téléphones et clients
  spécifiques;
- synchronisez DNS dynamique, inventaire et configuration réseau.

`ipconfig /all` (Windows), `nmcli device show` (NetworkManager) et
`resolvectl status` (systemd-resolved) aident à vérifier ce que le client a
effectivement reçu.

## 15. Sous-réseaux, agrégation et plan d'adressage à l'échelle

Une conception senior doit optimiser plus que le nombre d'adresses. Elle doit
faciliter l'agrégation des routes, les résumés par site, la croissance,
l'isolation des domaines de panne et les migrations.

### Résumer des réseaux contigus

Les réseaux `10.50.4.0/24`, `10.50.5.0/24`, `10.50.6.0/24` et
`10.50.7.0/24` sont contigus et s'agrègent en `10.50.4.0/22`. Le troisième
octet de départ (`4`) est aligné sur un multiple de quatre, exigé par le `/22`.

```text
10.50.4.0/24  ─┐
10.50.5.0/24   │        résumé 10.50.4.0/22
10.50.6.0/24   │   ─────────────────────────────>
10.50.7.0/24  ─┘        couvre .4.0 à .7.255
```

Ne résumez pas des plages simplement parce qu'elles sont proches. Un résumé
incorrect attire du trafic vers un routeur qui n'a pas les sous-réseaux
concernés; cela crée un trou noir ou un routage asymétrique. Pour vérifier le
résumé, développez-le en binaire ou avec un calculateur et comparez son début,
sa fin, son alignement et tous les réseaux qu'il couvre. Cisco peut installer
une route de rejet `Null0` pour rendre un résumé sûr contre les boucles :

```text
ip route 10.50.4.0 255.255.252.0 Null0
```

Cette route doit être conçue avec les routes plus spécifiques et le protocole
de routage; n'ajoutez pas un rejet agrégé sans comprendre son interaction avec
le trafic valide.

### Registre IPAM recommandé

Conservez au minimum ces champs pour chaque bloc :

| Champ | Exemple |
| --- | --- |
| Préfixe et masque | `10.50.10.0/24`, `255.255.255.0` |
| Site / VRF / VLAN | `PAR-01`, `CORP`, VLAN 10 |
| Fonction | postes utilisateurs |
| Gateway virtuelle | `10.50.10.1` |
| DHCP | `10.50.10.100–10.50.10.220` |
| Statique/exclusions | `10.50.10.2–10.50.10.99` |
| Routeur propriétaire | cluster de distribution PAR-01 |
| Résumé annoncé | `10.50.0.0/16` |
| Responsable / date | équipe réseau, revue trimestrielle |

Ne réutilisez pas un réseau « libre » sans vérifier les réseaux de gestion,
VPN, environnements cloud, partenaires et plans de reprise. Le chevauchement
qui paraît inoffensif dans deux sites isolés devient bloquant lors d'un VPN,
d'une fusion, d'un peering cloud ou d'un déplacement de machine virtuelle.
Utilisez des VRF pour séparer des espaces qui doivent coexister, mais souvenez-
vous que la VRF ne rend pas automatiquement les adresses globalement uniques.

## 16. En-tête IPv4, TTL, ICMP et MTU

Un paquet IPv4 contient notamment les champs suivants :

| Champ | Fonction opérationnelle |
| --- | --- |
| Version / IHL | version IP et longueur de l'en-tête |
| DSCP / ECN | classe de service et indication de congestion |
| Longueur totale | taille du paquet IPv4, en-tête compris |
| Identification / Flags / Fragment Offset | fragmentation et réassemblage |
| TTL | limite la durée de vie et empêche les boucles infinies |
| Protocol | protocole supérieur : ICMP 1, TCP 6, UDP 17, etc. |
| Header checksum | contrôle de l'en-tête, recalculé à chaque saut |
| Source / destination | adresses IPv4 de bout en bout |

Le TTL est décrémenté au passage d'un routeur. À zéro, le paquet est supprimé
et un message ICMP Time Exceeded peut être renvoyé; `traceroute` exploite ce
mécanisme avec des TTL successifs. Une ACL qui bloque ICMP peut masquer les
réponses de diagnostic sans nécessairement bloquer le trafic applicatif.

### MTU et Path MTU Discovery

L'Ethernet classique transporte généralement une charge utile IP de 1500
octets (MTU 1500), mais les tunnels, PPPoE, VPN ou encapsulations peuvent
réduire la MTU disponible. Si un paquet est trop grand :

- sans le bit DF (*Don't Fragment*), un routeur IPv4 peut le fragmenter;
- avec DF, le routeur le supprime et devrait renvoyer ICMP
  « fragmentation needed »;
- le système source ajuste sa taille selon PMTUD (*Path MTU Discovery*).

Filtrer tout ICMP peut casser PMTUD et produire une panne intermittente :
petites requêtes DNS ou ping passent, mais les sessions TLS ou transferts
volumineux se figent. Autorisez les messages ICMP utiles selon une politique
de sécurité maîtrisée plutôt que d'appliquer un « deny ICMP all » automatique.

Exemples de diagnostic Linux :

```bash
ip link show dev eth0
tracepath -n 203.0.113.20
ping -M do -s 1472 -c 3 203.0.113.20
sudo tcpdump -ni eth0 'icmp or host 203.0.113.20'
```

Pour un ping IPv4 sans options, `1472` octets de données plus 8 octets ICMP et
20 octets IPv4 font 1500 octets. Cette valeur n'est pas universelle : répétez
le test avec une taille adaptée au chemin et au type de tunnel. Sous Cisco,
les commandes disponibles dépendent de l'IOS :

```text
ping
traceroute 203.0.113.20
show interfaces GigabitEthernet0/0
show ip traffic
```

Vérifiez MTU, compteurs de fragments, drops, erreurs d'interface et messages
ICMP; un ping simple ne révèle pas toujours une panne de MTU.

## 17. Configuration Cisco : LAN, sous-interfaces et routes

### Inter-VLAN avec sous-interfaces 802.1Q

Pour un routeur-on-a-stick, le port du commutateur vers le routeur est trunk;
chaque sous-interface L3 représente la passerelle d'un VLAN :

```text
configure terminal
interface GigabitEthernet0/0
 no shutdown
!
interface GigabitEthernet0/0.10
 description Gateway VLAN 10 utilisateurs
 encapsulation dot1Q 10
 ip address 10.50.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 description Gateway VLAN 20 voix
 encapsulation dot1Q 20
 ip address 10.50.20.1 255.255.255.0
!
interface GigabitEthernet0/0.99
 description VLAN de gestion natif
 encapsulation dot1Q 99 native
 ip address 10.50.99.1 255.255.255.0
end
show ip interface brief
show interfaces GigabitEthernet0/0
show running-config | section interface
show ip route connected
```

Le VLAN natif doit correspondre aux deux extrémités du trunk; un mismatch
peut faire fuiter ou perdre des trames non taguées. En conception moderne,
préférez un plan de VLAN natif explicite, inutilisé pour les terminaux, et
vérifiez la configuration de trunk côté switch.

### Routes statiques et route par défaut

Une route statique doit pointer vers un prochain saut joignable ou une interface
de sortie adaptée au type de lien :

```text
ip route 10.60.0.0 255.255.0.0 192.0.2.6
ip route 0.0.0.0 0.0.0.0 192.0.2.1
show ip route static
show ip route 10.60.12.34
```

Une route statique vers un prochain saut inaccessible n'assure pas le transfert.
Sur un Ethernet multiaccès, une route spécifiant seulement l'interface de sortie
peut obliger le routeur à résoudre en ARP toutes les destinations distantes;
utilisez un next-hop explicite lorsque c'est approprié. Pour une route de
secours, une distance administrative plus élevée peut servir de route flottante,
à condition de surveiller l'état réel du chemin primaire :

```text
ip route 0.0.0.0 0.0.0.0 192.0.2.1
ip route 0.0.0.0 0.0.0.0 198.51.100.1 200
```

La deuxième route n'est pas une détection complète de panne si l'interface
reste up alors que le fournisseur est inaccessible. Selon la plateforme,
utilisez IP SLA avec suivi, BFD ou le protocole de routage adapté, et testez le
comportement de bascule.

## 18. Filtrage, anti-usurpation et frontières de confiance

Les adresses sources doivent être plausibles sur l'interface d'entrée. Le
filtrage ingress réduit l'usurpation d'adresse; le filtrage egress empêche un
réseau interne d'émettre des sources qui ne lui appartiennent pas. Une ACL
standard numérotée IOS exemple :

```text
ip access-list standard MGMT-SOURCES
 permit 10.50.99.0 0.0.0.255
 deny any log
!
line vty 0 4
 access-class MGMT-SOURCES in
 transport input ssh
```

Les ACL sont évaluées dans l'ordre et ont un deny implicite à la fin. Placez
une ACL étendue au plus près de la source lorsque cela réduit le trafic
indésirable sans bloquer les flux nécessaires. Validez les compteurs après
déploiement :

```text
show access-lists
show ip interface GigabitEthernet0/0
clear access-list counters
```

`clear access-list counters` remet les compteurs à zéro : utilisez-le seulement
dans une fenêtre d'observation convenue. Les noms et syntaxes exacts varient
selon les familles IOS/IOS XE.

Pour les environnements d'entreprise, corrélez la protection L2 (DHCP snooping,
Dynamic ARP Inspection, IP Source Guard) avec les liaisons fiables et les
réservations. Une table de bindings incohérente peut bloquer des hôtes légitimes.
Documentez les ports trusted, les uplinks et les exceptions avant d'activer
ces contrôles globalement.

`ip verify source` ou uRPF peut aider à vérifier la source selon la topologie,
mais le mode strict est parfois incompatible avec l'asymétrie, le multihoming
et certaines routes ECMP. Testez le chemin aller/retour et choisissez le mode
adapté; une commande de sécurité mal placée peut couper des flux valides.

## 19. Équivalents Linux : interface, routes, règles et capture

Pour configurer un laboratoire à l'exécution, sans persistance :

```bash
sudo ip link set dev eth0 up
sudo ip address replace 10.50.10.25/24 dev eth0
sudo ip route replace default via 10.50.10.1 dev eth0
ip -br address
ip route get 203.0.113.20
```

`replace` rend le changement idempotent, contrairement à `add` qui renvoie une
erreur si l'adresse existe déjà. Pour l'enlever :

```bash
sudo ip address del 10.50.10.25/24 dev eth0
sudo ip route del default via 10.50.10.1
```

La configuration persistante est gérée par NetworkManager, systemd-networkd,
Netplan ou les fichiers propres à la distribution. Ne supposez pas qu'une
commande `ip` persistera après redémarrage. Inspectez d'abord :

```bash
nmcli connection show
networkctl status eth0
resolvectl status
```

Capturer le plan de contrôle aide à distinguer une erreur de configuration
d'une erreur de transport :

```bash
sudo tcpdump -ni eth0 'arp or icmp or (udp port 67 or udp port 68)'
sudo tcpdump -ni eth0 -vv 'host 10.50.10.25'
ss -tunap
```

Une capture peut contenir des adresses internes et des données sensibles;
protégez le fichier, limitez la durée et le filtre, puis supprimez-le selon la
politique de conservation.

## 20. Étude de cas : panne intermittente après un nouveau VLAN

### Symptôme

Les clients du VLAN 30 obtiennent une adresse `10.60.30.100/23`, mais
n'atteignent pas le serveur `10.60.31.50`. La gateway déclarée est
`10.60.30.1`. Le VLAN 30 a été créé à partir d'un ancien modèle `/24`.

### Analyse structurée

1. **Calcul local :** `10.60.30.100/23` appartient à `10.60.30.0/23`, couvrant
   `10.60.30.0–10.60.31.255`. Le serveur `10.60.31.50` est donc considéré
   comme local par le client.
2. **ARP attendu :** le client cherche directement la MAC de `10.60.31.50`;
   il ne transmet pas à `10.60.30.1`.
3. **Vérification :** `ip neigh` affiche `10.60.31.50 FAILED`; la capture montre
   les requêtes ARP répétées sans réponse.
4. **Contrôle L2 :** le serveur est en réalité dans le VLAN 31, isolé au niveau
   2. Les deux préfixes `/24` ont été agrégés par erreur sur le pool DHCP.
5. **Correction :** aligner la topologie et le plan d'adressage : soit séparer
   `10.60.30.0/24` et `10.60.31.0/24` avec leurs gateways/VLAN, soit construire
   un vrai domaine L2 commun `/23`, ce qui est rarement une bonne correction
   si l'objectif est la segmentation.

### Commandes de diagnostic concrètes

```bash
ip -br address
ip route get 10.60.31.50
ip neigh show 10.60.31.50
sudo tcpdump -ni eth0 'arp or host 10.60.31.50'
```

```text
show vlan brief
show interfaces trunk
show mac address-table dynamic vlan 30
show ip interface brief
show ip route 10.60.31.50
show ip dhcp binding
```

Ne commencez pas par redémarrer le switch, le routeur ou le serveur : cela
efface parfois les indices et ne corrige pas le mauvais calcul de préfixe.
Confirmez d'abord l'adresse et le masque réellement reçus, le VLAN du port,
le réseau calculé par le client et la décision de routage.

## 21. Atelier de conception et validation

Une agence dispose du bloc privé `10.80.16.0/20`. Elle doit accueillir :

| Segment | Besoin initial |
| --- | ---: |
| Utilisateurs siège | 700 |
| Wi-Fi collaborateurs | 300 |
| Téléphones IP | 180 |
| Serveurs applicatifs | 90 |
| Gestion équipements | 45 |
| Transit routeur / pare-feu | 2 |

### Allocation possible

Réservez les blocs les plus grands d'abord, en gardant de la continuité pour
les résumés :

| Fonction | Préfixe | Capacité classique | Remarque |
| --- | --- | ---: | --- |
| Utilisateurs | `10.80.16.0/22` | 1022 | couvre `10.80.16.0–10.80.19.255` |
| Wi-Fi | `10.80.20.0/23` | 510 | couvre `10.80.20.0–10.80.21.255` |
| Téléphones | `10.80.22.0/24` | 254 | réserve de croissance incluse |
| Serveurs | `10.80.23.0/25` | 126 | sous-réseau distinct |
| Gestion | `10.80.23.128/26` | 62 | équipements d'infrastructure |
| Transit | `10.80.23.192/30` | 2 | utiliser `/31` si supporté et standardisé |

Vérifiez que chaque début est aligné : un `/22` démarre sur un troisième octet
multiple de 4; un `/23` sur un multiple de 2; un `/25`, `/26` et `/30` sur les
frontières correspondantes du dernier octet. Le bloc parent `/20` couvre
`10.80.16.0–10.80.31.255`; il reste donc une réserve contiguë, notamment les
réseaux de `10.80.24.0` à `10.80.31.255`.

### Plan de vérification avant mise en service

- [ ] Confirmer l'allocation autorisée et l'absence de chevauchement VPN/cloud.
- [ ] Réserver les gateways, VIP HSRP/VRRP, équipements statiques et DHCP.
- [ ] Documenter le VLAN/VRF, le broadcast, les exclusions et les propriétaires.
- [ ] Vérifier les résumés de routage et les routes de retour.
- [ ] Définir DHCP, relais, DNS, NTP et options propres aux clients.
- [ ] Contrôler ACL, NAT, filtrage source et flux applicatifs requis.
- [ ] Tester MTU, redondance de passerelle et bascule du WAN.
- [ ] Prévoir supervision de l'épuisement DHCP, des erreurs d'interface et des
  changements de routes.

## 22. Procédure de dépannage de niveau production

Quand un incident concerne un seul hôte, un VLAN, un site ou toutes les
destinations, cette matrice aide à réduire rapidement le domaine :

| Observation | Hypothèses prioritaires | Vérifications |
| --- | --- | --- |
| Pas d'adresse / `169.254.x.x` | DHCP, VLAN, relais, pool épuisé | DORA en capture, binding, helper |
| Gateway inaccessible | mauvais masque/VLAN, ARP, interface down | `ip neigh`, `show arp`, état L2/L3 |
| Gateway joignable, réseau local non | route ou ACL inter-VLAN | route exacte, ACL et compteur |
| IP distante joignable, nom non | DNS / suffixe / resolver | `dig`, `nslookup`, options DHCP |
| Petits paquets passent, gros flux bloqué | PMTUD/MTU, ICMP filtré | `tracepath`, DF ping, ICMP |
| Aller fonctionne, réponse absente | route retour, ACL, NAT asymétrique | capture sur les deux côtés, table NAT |
| Tous les clients d'un pool affectés | épuisement, option erronée, scope | utilisation du pool et configuration |

Séquence recommandée :

1. Fixez la portée et l'heure de début; identifiez le changement récent.
2. Relevez l'IP, le masque, la passerelle et les DNS du client affecté.
3. Calculez localement si la destination est dans le même préfixe.
4. Vérifiez link, VLAN, ARP et passerelle avant de suivre une route distante.
5. Interrogez la route pour une adresse précise aux deux extrémités.
6. Comparez les captures ou compteurs de part et d'autre du point de rupture.
7. Testez le chemin retour, les ACL, NAT, MTU et résolution DNS séparément.
8. Appliquez une correction ciblée, surveillez, documentez et prévoyez rollback.

Collectez les preuves avant changement :

```text
Cisco IOS :
show clock
show ip interface brief
show interfaces counters errors
show ip route <destination>
show arp
show access-lists
show logging
```

```bash
Linux :
date -Is
ip -details -statistics link show
ip -br address
ip route get <destination>
ip neigh
resolvectl query <nom>
sudo tcpdump -ni <interface> -c 100 '<filtre ciblé>'
```

Évitez les tests qui génèrent un volume important ou modifient une table en
production sans autorisation. Les compteurs, captures et commandes `debug`
peuvent être coûteux sur certains équipements; préférez une collecte ciblée et
une fenêtre limitée.

## 23. Questions de synthèse — niveau avancé

### A. Route locale ou passerelle ?

Un poste `10.10.8.25/21` envoie vers `10.10.15.90`. Le poste ARP-t-il pour la
destination ou pour sa passerelle ?

**Réponse :** le masque `/21` vaut `255.255.248.0`, pas 8 au troisième octet.
Les blocs sont `0–7`, `8–15`, etc. Les deux adresses sont dans
`10.10.8.0/21`; il émet ARP pour `10.10.15.90`. Si le réseau L2 ne s'étend pas
sur tout ce `/21`, la conception ou le masque est incohérent.

### B. Résumé de routes

Quatre routes `/24` couvrent `172.18.40.0` à `172.18.43.0`. Quel résumé ?

**Réponse :** `172.18.40.0/22`, car quatre `/24` contigus forment un `/22` et
40 est divisible par 4. Vérifiez qu'aucun des quatre sous-réseaux ne doit être
annoncé séparément et que le routeur de résumé peut acheminer chacun d'eux.

### C. Test de MTU

Un chemin Ethernet 1500 fonctionne avec les petites requêtes, mais un tunnel
échoue dès qu'une réponse dépasse environ 1400 octets. Quel test et quelle
cause cherchez-vous ?

**Réponse :** vérifiez la MTU de chaque encapsulation et PMTUD. Envoyez des
ICMP avec DF à des tailles contrôlées, observez ICMP « fragmentation needed »
et capturez près du tunnel. Une ACL ICMP ou une MTU tunnel incorrecte peut
bloquer les gros flux alors que les petits pings réussissent.

### D. Le DHCP offre une IP, mais aucun accès hors VLAN

Quelles options et décisions vérifiez-vous ?

**Réponse :** contrôlez le masque (option 1), la passerelle (option 3), les
routes connectées, l'ARP de la gateway, la route de retour, les ACL/NAT et la
résolution DNS séparément. Une offre DHCP ne prouve pas que le chemin L3 est
fonctionnel.

### E. Adresse privée et chevauchement VPN

Deux filiales utilisent `192.168.1.0/24`; chacune fonctionne seule, mais le
VPN intersite ne joint pas les deux LAN. Pourquoi ?

**Réponse :** les deux préfixes se chevauchent et chaque côté considère la
destination comme directement connectée; les hôtes ARP localement au lieu de
passer par le tunnel. Renumérotation ou mécanisme de traduction/segmentation
peut être nécessaire; NAT n'est qu'un contournement et complique les flux.

## Synthèse opérationnelle

```text
Adresse réseau   = IP AND masque
Wildcard         = complément du masque (pour les correspondances Cisco)
Hôtes classiques = 2^(32 - préfixe) - 2
Pas              = 256 - octet partiel du masque
Route gagnante   = préfixe correspondant le plus long
Hôte local       = ARP destination
Hôte distant     = ARP passerelle, IP destination inchangée
```

Le travail senior consiste à maintenir une cohérence entre IPAM, VLAN/VRF,
DHCP, routes, politiques de sécurité, NAT, MTU et chemin retour. Toute
modification de préfixe doit être contrôlée de bout en bout : adresse attribuée,
décision du client, passerelle, propagation de route, filtrage, DNS, supervision
et procédures de rollback. Les commandes affichent l'état observé; le calcul du
préfixe et les preuves capturées expliquent pourquoi cet état produit le
résultat constaté.
