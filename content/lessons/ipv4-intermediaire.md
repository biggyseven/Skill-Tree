---
node_id: ipv4-intermediaire
title: Adressage IPv4 & sous-réseaux - Intermédiaire
---

# Adressage IPv4 & sous-réseaux - Intermédiaire

**Niveau :** Intermédiaire

L’adressage IPv4 ne se limite pas à reconnaître une adresse réseau et une adresse de diffusion. Dans un réseau d’entreprise, l’ingénieur doit concevoir un plan d’adressage durable, attribuer des préfixes de tailles différentes, limiter les chevauchements, prévoir les évolutions, résumer les routes et comprendre comment les masques influencent le transfert des paquets. Ces opérations sont étroitement liées à la commutation VLAN, au routage inter-VLAN, au DHCP, aux listes de contrôle d’accès et aux protocoles de routage dynamique. Une erreur d’adressage peut rester invisible tant que le réseau est peu chargé, puis provoquer des pannes difficiles à diagnostiquer lorsqu’un nouveau site ou un nouveau service est ajouté.

L’adressage IPv4 repose sur des adresses de 32 bits. L’écriture décimale pointée facilite la lecture humaine, mais les décisions de sous-réseautage et de routage s’effectuent à partir des bits. Les anciennes classes A, B et C ont une importance historique ; en exploitation moderne, le modèle dominant est le routage sans classe, décrit par CIDR (*Classless Inter-Domain Routing*). CIDR permet de choisir une longueur de préfixe adaptée au besoin réel et de résumer plusieurs réseaux contigus lorsque leur position binaire le permet. Les concepts d’allocation et d’agrégation sont notamment décrits dans la [RFC 4632](https://www.rfc-editor.org/rfc/rfc4632.html), tandis que les plages privées sont définies par la [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918.html).

Au niveau intermédiaire, l’objectif consiste à passer du calcul isolé à la conception. Il faut savoir découper un bloc en sous-réseaux de tailles différentes avec VLSM (*Variable Length Subnet Mask*), attribuer des préfixes sans gaspillage, déterminer les agrégats possibles, distinguer le plan logique de l’affectation effective des adresses et vérifier les conséquences sur les routes. Il est également nécessaire de reconnaître les plages spéciales, de comprendre les effets d’un mauvais masque, d’organiser les liaisons point-à-point et de configurer des interfaces Cisco IOS ou IOS XE avec des commandes de vérification reproductibles.

Une bonne conception IPv4 doit être lisible par un autre administrateur, exploitable avec des outils de diagnostic et suffisamment prévisible pour accueillir de nouveaux VLANs, sites ou services. Un plan réussi n’est pas seulement un tableau d’adresses correctes : c’est un ensemble cohérent de préfixes, de passerelles, de règles d’annonce et de conventions documentées. Les calculs doivent être exacts, mais les choix doivent aussi tenir compte de l’exploitation, de la sécurité, de la croissance, de la traduction d’adresses et de la possibilité de résumer les routes.

> **Analogie** : Imagine une ville dont le territoire est divisé en secteurs administratifs. Chaque secteur reçoit un identifiant et peut lui-même être découpé en quartiers plus petits. Le préfixe IPv4 joue le rôle du contour d’un secteur : il indique quelles adresses appartiennent au même ensemble logique. Une équipe informatique ne doit pas distribuer les numéros au hasard ; elle doit réserver des secteurs aux bureaux, aux serveurs, à la voix, à la gestion et aux liaisons entre routeurs.
>
> VLSM ressemble à un urbaniste qui attribue une parcelle de taille adaptée à chaque besoin. Un petit point de présence contenant deux routeurs n’a pas besoin de la même surface qu’un campus de plusieurs centaines de terminaux. Si chaque équipe recevait systématiquement une parcelle immense, beaucoup d’espace serait inutilisé. Si elle recevait une parcelle trop petite, il faudrait déplacer les limites plus tard, avec des interruptions et des changements de configuration. La bonne stratégie consiste à prévoir les besoins, classer les segments du plus grand au plus petit et attribuer les blocs sans chevauchement.
>
> CIDR et le résumé de routes ressemblent à la possibilité de représenter plusieurs quartiers contigus par une frontière administrative commune. Un routeur peut annoncer un agrégat au lieu de détailler chaque sous-réseau, à condition que les préfixes soient correctement alignés et que l’annonce ne détourne pas le trafic vers une destination inexistante. Une frontière trop large peut masquer des trous dans le plan et donner l’impression qu’une destination est accessible alors qu’elle ne l’est pas réellement.
>
> L’analogie a toutefois une limite importante : les routeurs ne raisonnent pas à partir d’une carte dessinée mais à partir d’opérations binaires. La validité d’un résumé dépend de l’alignement des bits, pas de la proximité visuelle des nombres. Deux réseaux qui semblent proches dans leur écriture décimale ne sont pas nécessairement agrégeables. Le calcul doit donc être vérifié en binaire ou à l’aide d’une méthode mathématique rigoureuse.

---

## 1. La théorie et les algorithmes

### 1.1. Rappel opérationnel : adresse, préfixe et masque

Une adresse IPv4 est une valeur de 32 bits écrite sous la forme de quatre octets décimaux séparés par des points. Un préfixe `/n` indique que les `n` premiers bits identifient le réseau et que les `32 − n` bits restants sont disponibles pour numéroter les interfaces ou représenter les adresses spéciales propres au sous-réseau.

Le masque en notation décimale pointée représente la même limite. Ses bits réseau sont à 1 et ses bits hôte à 0. Les bits à 1 doivent être contigus depuis le bit de poids fort ; un masque tel que `255.0.255.0` n’est pas un masque IPv4 normal valide, car il interrompt la séquence de bits réseau.

| Préfixe | Masque | Bits hôte | Adresses totales | Hôtes utilisables sur un sous-réseau IPv4 classique |
|---:|---|---:|---:|---:|
| `/30` | 255.255.255.252 | 2 | 4 | 2 |
| `/29` | 255.255.255.248 | 3 | 8 | 6 |
| `/28` | 255.255.255.240 | 4 | 16 | 14 |
| `/27` | 255.255.255.224 | 5 | 32 | 30 |
| `/26` | 255.255.255.192 | 6 | 64 | 62 |
| `/25` | 255.255.255.128 | 7 | 128 | 126 |
| `/24` | 255.255.255.0 | 8 | 256 | 254 |
| `/23` | 255.255.254.0 | 9 | 512 | 510 |
| `/22` | 255.255.252.0 | 10 | 1 024 | 1 022 |
| `/21` | 255.255.248.0 | 11 | 2 048 | 2 046 |
| `/20` | 255.255.240.0 | 12 | 4 096 | 4 094 |
| `/16` | 255.255.0.0 | 16 | 65 536 | 65 534 |

La règle générale pour le nombre d’adresses est :

\[
N_{total} = 2^{(32-n)}
\]

Sur un sous-réseau IPv4 multi-accès conventionnel, la formule usuelle pour les adresses d’hôtes utilisables est :

\[
N_{hôtes} = 2^{(32-n)} - 2
\]

Le retrait de deux adresses correspond à l’adresse de réseau et à l’adresse de broadcast du sous-réseau. Cette formule n’est pas universelle : des préfixes `/31` peuvent être employés sur des liaisons point-à-point selon la [RFC 3021](https://www.rfc-editor.org/rfc/rfc3021.html), et un `/32` représente une route d’hôte unique. Il faut donc toujours connaître le contexte d’utilisation du préfixe.

### 1.2. Calcul binaire et opération AND

L’adresse réseau est obtenue en appliquant un AND logique bit à bit entre l’adresse IPv4 et le masque. Pour chaque bit, le résultat vaut 1 uniquement lorsque les deux entrées valent 1.

| Adresse bit | Masque bit | AND | Signification |
|---:|---:|---:|---|
| 1 | 1 | 1 | Le bit appartient au préfixe et reste à 1 |
| 1 | 0 | 0 | Le bit est dans la partie hôte et est supprimé du résultat |
| 0 | 1 | 0 | Le bit réseau reste à 0 |
| 0 | 0 | 0 | Le bit hôte est supprimé |

Exemple : déterminer le réseau de `192.168.42.77/26`.

Le préfixe `/26` signifie que les trois premiers octets sont intégralement inclus dans le réseau, puis que les deux premiers bits du quatrième octet appartiennent au réseau. Le masque est `255.255.255.192`, dont le dernier octet binaire est `11000000`.

```text
Adresse : 192.168.42.77       01001101
Masque  : 255.255.255.192     11000000
                                 AND
Réseau  : 192.168.42.64       01000000
```

Le réseau est `192.168.42.64/26`. Les 6 bits hôte donnent 64 combinaisons. L’adresse réseau est `.64`, le broadcast est `.127`, et les hôtes utilisables vont de `.65` à `.126`.

Le calcul AND constitue une méthode universelle : il ne dépend pas d’un tableau de tailles mémorisées. En pratique, on peut accélérer les calculs grâce à la taille de bloc, mais il reste utile de savoir justifier le résultat en binaire lorsqu’une adresse est située à une frontière inhabituelle.

### 1.3. La méthode de la taille de bloc

La méthode de la taille de bloc transforme le masque en intervalle de sous-réseau dans l’octet où le masque n’est ni entièrement à 255 ni entièrement à 0. On calcule :

\[
Taille\ de\ bloc = 256 - valeur\ du\ masque\ dans\ l'octet\ variable
\]

Pour un `/26`, le masque final vaut 192, donc le bloc est `256 − 192 = 64`. Les réseaux dans le dernier octet commencent à `.0`, `.64`, `.128` et `.192`. Une adresse `192.168.42.77` se trouve donc dans le bloc allant de `.64` à `.127`.

Pour un `/20`, le masque est `255.255.240.0`. L’octet variable est le troisième : `256 − 240 = 16`. Les réseaux progressent par multiples de 16 dans le troisième octet, à l’intérieur des deux premiers octets concernés. Une adresse `10.44.37.8/20` appartient ainsi au réseau `10.44.32.0/20`, dont le troisième octet varie de 32 à 47. Le broadcast est `10.44.47.255`.

La méthode fonctionne également lorsque la limite se situe dans le deuxième octet. Pour `172.20.0.0/14`, le masque `255.252.0.0` donne une taille de bloc de 4 dans le deuxième octet. Le réseau couvre les valeurs 20 à 23 dans cet octet, soit `172.20.0.0` à `172.23.255.255`.

L’erreur fréquente consiste à considérer l’adresse donnée comme le début du sous-réseau sans vérifier l’alignement. Une interface peut être configurée avec `192.168.42.77/26`, mais son adresse réseau reste `192.168.42.64/26`. L’adresse d’interface et l’adresse de réseau sont deux objets différents.

### 1.4. Déterminer le réseau, le broadcast et la plage d’hôtes

Pour déterminer toutes les informations d’un sous-réseau, il faut procéder méthodiquement :

1. Identifier le préfixe ou convertir le masque en longueur de préfixe.
2. Calculer l’adresse réseau avec AND, ou utiliser la taille de bloc.
3. Mettre tous les bits hôte à 1 pour obtenir le broadcast conventionnel.
4. Déterminer les hôtes utilisables entre réseau + 1 et broadcast − 1.
5. Vérifier si le contexte est particulier, par exemple `/31`, `/32`, boucle locale ou adresse spéciale.

Exemple complet : `10.20.73.146/27`.

- Le masque `/27` vaut `255.255.255.224`.
- La taille de bloc dans le dernier octet est `256 − 224 = 32`.
- Les intervalles sont `.0–.31`, `.32–.63`, `.64–.95`, `.96–.127`, `.128–.159`, `.160–.191`, `.192–.223` et `.224–.255`.
- L’adresse `.146` appartient au bloc `.128–.159`.
- L’adresse réseau est `10.20.73.128`.
- Le broadcast est `10.20.73.159`.
- Les hôtes utilisables sont `10.20.73.129` à `10.20.73.158`.
- Le sous-réseau compte 32 adresses totales et 30 adresses d’hôtes conventionnelles.

Cette procédure doit devenir automatique, mais pas au prix d’une compréhension approximative. Dans un scénario de dépannage, savoir expliquer pourquoi `.146` appartient à `.128/27` permet d’identifier rapidement un masque incorrect ou une passerelle placée dans un autre sous-réseau.

### 1.5. Pourquoi les classes historiques ne suffisent plus

Le modèle historique classait les adresses selon leurs premiers bits et associait implicitement certaines plages à des masques par défaut. Les réseaux de classe A, B et C sont souvent mentionnés dans les anciens supports, mais le routage moderne se fonde sur des préfixes explicites et non sur une classe supposée à partir de l’adresse.

Avec CIDR, les préfixes `/19`, `/22`, `/27` ou `/30` sont valides indépendamment des catégories historiques. Les protocoles de routage sans classe transportent la longueur du préfixe pour que les routeurs sachent distinguer précisément les destinations. La [RFC 4632](https://www.rfc-editor.org/rfc/rfc4632.html) décrit le rôle de CIDR dans l’allocation et l’agrégation des adresses.

Cela a deux conséquences pratiques. Premièrement, on ne peut pas conclure qu’une adresse telle que `172.20.5.10` appartient à un réseau `/16` simplement parce que la plage était traditionnellement associée à une classe B. Le masque réel doit être connu. Deuxièmement, deux interfaces dont les adresses paraissent appartenir à la même plage historique peuvent être dans des sous-réseaux distincts si leurs préfixes diffèrent.

Dans les commandes de routage et les plans d’adressage, il faut toujours écrire les préfixes explicitement, par exemple `172.20.5.0/24`, plutôt que de dire seulement « le réseau 172.20 ». Une notation sans masque est ambiguë dans un environnement CIDR.

### 1.6. Sous-réseautage à taille fixe et VLSM

Le sous-réseautage à taille fixe divise un bloc parent en sous-réseaux de même longueur. Il est simple à administrer, mais peut gaspiller beaucoup d’adresses si les segments ont des besoins très différents.

VLSM autorise des préfixes de différentes tailles dans le même plan d’adressage. On peut ainsi attribuer un `/24` à un LAN de grande taille, un `/27` à un petit service et un `/31` à une liaison point-à-point compatible. Le préfixe de chaque sous-réseau doit rester aligné sur sa taille et ne doit pas chevaucher les autres.

La démarche de conception habituelle est la suivante :

1. Inventorier les segments et leur besoin maximal en adresses.
2. Ajouter une marge de croissance réaliste, sans surdimensionnement arbitraire.
3. Calculer le plus petit préfixe qui peut satisfaire le besoin.
4. Trier les besoins du plus grand au plus petit.
5. Attribuer les blocs de manière contiguë, en respectant l’alignement.
6. Réserver une partie du bloc parent pour les extensions.
7. Vérifier les plages et documenter les passerelles, VLANs et usages.

Pour un besoin de `H` hôtes dans un sous-réseau conventionnel, on cherche le plus petit nombre de bits hôte `h` qui satisfait :

\[
2^h - 2 \geq H
\]

Le préfixe correspondant est `32 − h`. On choisit la puissance de deux immédiatement suffisante, car l’espace IPv4 est organisé en blocs binaires. Si un service compte 50 équipements, 6 bits hôte donnent 62 adresses conventionnelles utilisables, donc `/26` convient. Un `/27` n’en donne que 30 et serait insuffisant.

#### Exemple de plan VLSM

Une organisation reçoit le bloc privé `10.60.8.0/22`, qui couvre `10.60.8.0` à `10.60.11.255`, soit 1 024 adresses. Elle doit adresser un LAN utilisateurs de 180 hôtes, un LAN voix de 70 hôtes, un LAN de gestion de 25 hôtes, deux petites zones de 10 hôtes chacune et deux liaisons point-à-point.

| Besoin | Taille minimale adaptée | Adresses totales | Hôtes conventionnels |
|---|---:|---:|---:|
| 180 hôtes | `/24` | 256 | 254 |
| 70 hôtes | `/25` | 128 | 126 |
| 25 hôtes | `/27` | 32 | 30 |
| 10 hôtes | `/28` | 16 | 14 |
| 10 hôtes | `/28` | 16 | 14 |
| Liaison point-à-point, si `/31` pris en charge | `/31` | 2 | 2 extrémités |
| Liaison point-à-point, méthode conventionnelle | `/30` | 4 | 2 hôtes |

Une attribution possible, en choisissant des adresses faciles à lire, est :

| Fonction | Préfixe attribué | Plage d’hôtes / endpoints | Broadcast classique |
|---|---|---|---|
| Utilisateurs | `10.60.8.0/24` | `10.60.8.1–10.60.8.254` | `10.60.8.255` |
| Voix | `10.60.9.0/25` | `10.60.9.1–10.60.9.126` | `10.60.9.127` |
| Gestion | `10.60.9.128/27` | `10.60.9.129–10.60.9.158` | `10.60.9.159` |
| Petit réseau A | `10.60.9.160/28` | `10.60.9.161–10.60.9.174` | `10.60.9.175` |
| Petit réseau B | `10.60.9.176/28` | `10.60.9.177–10.60.9.190` | `10.60.9.191` |
| Liaison R1–R2 | `10.60.9.192/31` | `10.60.9.192–10.60.9.193` | Non utilisé comme broadcast de lien `/31` |
| Liaison R2–R3 | `10.60.9.194/31` | `10.60.9.194–10.60.9.195` | Non utilisé comme broadcast de lien `/31` |

Les blocs restants de `10.60.9.196` à `10.60.11.255` sont disponibles pour des extensions, mais la réservation exacte doit être documentée. Le tableau est un exemple de méthode, pas une prescription universelle : les besoins en croissance, les politiques de sécurité, les exigences d’agrégation et les capacités des équipements peuvent conduire à un autre découpage.

L’intérêt de commencer par le plus grand besoin est de réduire le risque de fragmentation du bloc. Si les petits sous-réseaux sont placés au hasard en premier, il peut devenir difficile de trouver ensuite un bloc correctement aligné pour le grand LAN.

### 1.7. Alignement des préfixes et validation du plan

Un sous-réseau ne peut pas commencer à n’importe quelle adresse. Son début doit être aligné sur la taille du bloc. Un `/27`, par exemple, a une taille de 32 adresses et doit donc commencer sur une frontière multiple de 32 dans l’octet variable : `.0`, `.32`, `.64`, `.96`, `.128`, `.160`, `.192` ou `.224`.

L’adresse `192.168.50.96/27` est alignée. L’adresse `192.168.50.100/27` peut être utilisée comme adresse d’interface, mais `192.168.50.100/27` n’est pas l’identifiant du réseau : le réseau est `192.168.50.96/27`.

Un plan d’adressage doit être vérifié sur au moins quatre axes : capacité, absence de chevauchement, alignement et cohérence du routage. Les erreurs les plus coûteuses ne viennent pas toujours d’un calcul isolé : elles apparaissent lorsque deux blocs attribués à des équipes différentes se superposent, lorsqu’un résumé inclut des préfixes non maîtrisés ou lorsqu’un réseau est annoncé par le mauvais routeur.

Une feuille de calcul ou un outil IPAM peut automatiser certaines validations. Cependant, l’outil doit appliquer les bonnes hypothèses : notamment la prise en charge des `/31`, la distinction entre adresses utilisables et totales, les adresses réservées, et les politiques du plan d’adressage. L’automatisation ne remplace pas la définition correcte de ces règles.

### 1.8. CIDR et résumé de routes

L’agrégation consiste à annoncer un préfixe plus large qui représente plusieurs préfixes contigus. Elle réduit la quantité d’informations de routage et peut isoler une partie des détails internes d’un site. Pour être valide, l’agrégat doit couvrir exactement les blocs que l’on veut représenter, avec une frontière binaire commune et un alignement correct.

Exemple : quatre réseaux `/24` contigus `192.168.40.0/24`, `192.168.41.0/24`, `192.168.42.0/24` et `192.168.43.0/24` peuvent être agrégés en `192.168.40.0/22`, car le bloc `/22` couvre quatre valeurs consécutives du troisième octet et commence sur une frontière alignée de 4.

```text
Préfixes internes :
  192.168.40.0/24
  192.168.41.0/24
  192.168.42.0/24
  192.168.43.0/24
          |
          v
Agrégat possible :
  192.168.40.0/22

Couverture : 192.168.40.0 à 192.168.43.255
```

À l’inverse, quatre préfixes `/24` qui ne commencent pas sur une frontière alignée ne peuvent pas forcément être représentés par un seul agrégat de même taille. Il peut être nécessaire d’utiliser plusieurs agrégats ou un préfixe plus large, mais plus large signifie aussi qu’il couvre potentiellement des adresses qui ne sont pas réellement attribuées.

L’agrégation ne doit pas être évaluée seulement par le nombre de routes économisées. Il faut aussi considérer le comportement lorsqu’un sous-réseau interne est indisponible, la route de rejet vers l’agrégat, les routes plus spécifiques et la stratégie de retour. Une annonce agrégée trop large peut attirer du trafic vers un routeur qui ne sait pas le livrer.

Le routage IP applique normalement la règle du **préfixe le plus long** (*Longest Prefix Match*) : parmi les routes qui correspondent à la destination, la route ayant le préfixe le plus spécifique est choisie. Un `/24` est plus spécifique qu’un `/22`; un `/32` est plus spécifique qu’un `/24`. Les distances administratives et les métriques interviennent dans d’autres étapes de sélection, mais elles ne remplacent pas le principe du préfixe le plus long entre routes candidates installées.

### 1.9. Longest Prefix Match et décisions de transfert

Pour une adresse de destination, le routeur compare le préfixe de destination avec les entrées de sa table de routage. Il retient la route la plus spécifique correspondant à cette adresse. Si aucune route plus spécifique n’existe, une route moins spécifique ou une route par défaut peut être utilisée.

Imaginons une table contenant :

```text
10.0.0.0/8       -> Routeur A
10.20.0.0/16     -> Routeur B
10.20.30.0/24   -> Routeur C
0.0.0.0/0        -> Routeur Internet
```

Un paquet destiné à `10.20.30.55` correspond aux quatre préfixes, mais le `/24` est le plus long ; le paquet est donc envoyé vers le chemin associé à la route `10.20.30.0/24`. Un paquet vers `10.20.80.55` correspond à `10.0.0.0/8` et `10.20.0.0/16`, mais pas au `/24`; le `/16` est retenu. Un paquet vers `10.90.5.1` peut utiliser le `/8`, tandis qu’une adresse extérieure à `10.0.0.0/8` peut correspondre à la route par défaut.

Cette règle explique pourquoi une route plus spécifique peut l’emporter sur une route agrégée même si l’agrégat provient d’une source de routage considérée comme très fiable. La préférence de préfixe et la comparaison de sources de routage ont des rôles distincts. Pour comprendre un chemin, il faut consulter la route réellement installée et les critères qui ont permis son installation.

### 1.10. Adresses privées, publiques et espaces spéciaux

La [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918.html) réserve trois plages d’adresses IPv4 à l’usage privé :

| Plage | Préfixe | Taille totale | Usage habituel |
|---|---|---:|---|
| `10.0.0.0–10.255.255.255` | `10.0.0.0/8` | 16 777 216 adresses | Grands réseaux privés |
| `172.16.0.0–172.31.255.255` | `172.16.0.0/12` | 1 048 576 adresses | Réseaux privés de taille moyenne ou grande |
| `192.168.0.0–192.168.255.255` | `192.168.0.0/16` | 65 536 adresses | Réseaux locaux et petites organisations |

Ces plages ne sont pas globalement routées sur l’Internet public. Pour accéder à des ressources Internet, les réseaux privés utilisent fréquemment une traduction d’adresses, comme NAT ou PAT, ou une passerelle qui applique une politique équivalente. Le choix d’un espace privé doit néanmoins tenir compte du risque de chevauchement avec les réseaux d’un partenaire, d’un VPN ou d’un fournisseur.

Il existe d’autres plages spéciales qu’il ne faut pas confondre avec les blocs privés RFC 1918.

| Plage | Préfixe | Signification générale |
|---|---|---|
| `127.0.0.0/8` | Loopback | Trafic destiné à l’hôte local, généralement `127.0.0.1` |
| `169.254.0.0/16` | Link-local IPv4 | Adresses auto-configurées pour communication locale lorsque les mécanismes prévus les utilisent |
| `100.64.0.0–100.127.255.255` | `100.64.0.0/10` | Espace d’adresses partagé utilisé notamment dans les réseaux d’opérateurs et le CGN, défini par la [RFC 6598](https://www.rfc-editor.org/rfc/rfc6598.html) |
| `0.0.0.0` | Adresse non spécifiée selon le contexte | Utilisée notamment dans certains messages de configuration, pas comme adresse d’hôte ordinaire |
| `255.255.255.255` | Broadcast limité | Diffusion limitée au segment local ; les routeurs ne la relaient normalement pas |
| `224.0.0.0/4` | Multicast IPv4 | Adresses de groupe multicast, et non adresses d’hôtes unicast ordinaires |

La plage `100.64.0.0/10` est un cas important : elle est souvent appelée *Shared Address Space*, mais elle n’est pas une plage privée RFC 1918. La RFC 6598 la réserve notamment pour des usages d’opérateurs liés au CGN. Il est donc incorrect de traiter indistinctement `100.64.0.0/10` et `10.0.0.0/8` comme s’ils avaient exactement les mêmes règles d’utilisation.

Il faut aussi distinguer l’adresse privée d’une adresse inutilisable. Une adresse privée peut être pleinement utilisable dans un réseau interne correctement conçu. À l’inverse, une adresse publique attribuée à un site peut être inutilisable sur une interface tant que les routes, les politiques et l’attribution correspondantes ne sont pas correctes.

### 1.11. Liaisons `/31` et routes `/32`

Les liaisons point-à-point entre routeurs ont souvent besoin de seulement deux adresses d’extrémité. Un `/30` réserve quatre adresses, dont deux utilisables dans le modèle conventionnel. Un `/31` ne contient que deux adresses, mais la [RFC 3021](https://www.rfc-editor.org/rfc/rfc3021.html) permet, sur les liens point-à-point compatibles, d’utiliser les deux valeurs comme adresses des extrémités. Le gain devient important dans un réseau composé de centaines de liaisons de transit.

Il faut vérifier que les deux équipements et le contexte de liaison prennent en charge `/31`. Ce mécanisme ne doit pas être appliqué automatiquement à un LAN Ethernet multi-accès qui nécessite un comportement de broadcast conventionnel. Le `/31` est approprié au contexte décrit par la RFC : une liaison point-à-point avec deux extrémités.

Une route `/32` représente une seule adresse IPv4. Elle est souvent utilisée pour une loopback de routeur, une route d’hôte ou certains mécanismes de contrôle. Elle n’exprime pas un réseau comportant une plage d’hôtes conventionnelle. Une interface loopback peut être configurée avec un `/32`, par exemple `10.255.255.1/32`, puis annoncée dans un protocole de routage si la conception le prévoit.

Dans un plan d’adressage, il faut donc indiquer non seulement le préfixe, mais aussi son rôle : LAN multi-accès, lien point-à-point, loopback, route d’hôte ou agrégat. Le nombre de bits ne suffit pas à comprendre la signification opérationnelle de l’adresse.

### 1.12. Plan d’adressage hiérarchique et évolutivité

Un plan hiérarchique attribue des blocs en fonction des sites, régions, fonctions ou domaines de routage. Par exemple, un bloc peut être réservé à un siège, puis divisé en sous-blocs pour les VLANs utilisateurs, voix, serveurs et administration. D’autres sous-blocs sont attribués aux agences distantes.

Cette organisation facilite l’agrégation. Si tous les réseaux d’un site sont contenus dans un bloc aligné, le routeur de bordure peut annoncer ce bloc à un réseau central, sous réserve des règles du protocole de routage et du plan de secours. Le cœur du réseau connaît alors moins de routes détaillées.

Le plan doit réserver de l’espace pour les expansions futures sans créer un gaspillage non maîtrisé. Il est souvent utile de réserver des blocs contigus par site ou par fonction, de documenter le taux d’occupation et de conserver une convention pour les passerelles et adresses statiques. Une convention, par exemple `.1` comme passerelle, est une aide d’exploitation mais n’est pas une exigence du protocole IP.

Il faut éviter les plans qui attribuent les adresses en fonction de leur disponibilité immédiate sans considérer l’agrégation ou les interconnexions VPN. Si deux sites distants utilisent chacun `192.168.1.0/24`, leur connexion via VPN peut devenir ambiguë sans NAT ou renumérotation. Le risque de chevauchement doit être pris en compte dès le choix des blocs privés.

### 1.13. Adressage IPv4 et segmentation par VLAN

Un VLAN de couche 2 sépare un domaine de broadcast Ethernet, tandis qu’un sous-réseau IPv4 représente un domaine logique de préfixe IP. Dans un design d’entreprise, on associe très souvent un sous-réseau IPv4 à chaque VLAN utilisateurs, voix, serveurs, invités ou gestion. Cette correspondance simplifie les passerelles, les politiques de sécurité et les opérations de diagnostic.

La correspondance un VLAN–un sous-réseau est une convention d’architecture, pas une loi universelle. Des designs spécialisés peuvent présenter d’autres modèles, mais ils demandent une compréhension des domaines de broadcast, du routage, des mécanismes de sécurité et des contraintes de l’équipement.

Lorsqu’un poste doit communiquer avec une destination située dans son sous-réseau local, il envoie le trafic vers l’adresse MAC de la destination, généralement découverte via ARP. Lorsqu’il doit atteindre un réseau IP distant, il envoie le paquet à la passerelle par défaut. Le routeur effectue ensuite la recherche de route et transfère le paquet vers le prochain saut.

Une erreur de masque peut donner une mauvaise réponse à la question « la destination est-elle locale ? ». Avec un masque trop large, un poste peut tenter de résoudre en ARP une adresse qui devrait être atteinte via le routeur. Avec un masque trop étroit, un poste peut envoyer à la passerelle une destination qui est physiquement sur le même segment. Les deux situations peuvent provoquer des problèmes partiels qui ressemblent à une panne de routage ou d’ARP.

### 1.14. Passerelle par défaut et décision locale/distance

Un hôte IPv4 utilise son masque pour déterminer si une destination se trouve dans son sous-réseau. Si l’adresse de destination appartient au préfixe local, il peut transmettre directement au destinataire sur le réseau de couche 2. Sinon, il transmet le paquet à sa passerelle par défaut, à condition qu’une route adaptée existe.

Pour un poste `192.168.12.50/24`, la destination `192.168.12.200` appartient au réseau local `192.168.12.0/24`; la destination `192.168.13.20` n’en fait pas partie et doit être envoyée au routeur par défaut. Ce comportement dépend du masque réellement configuré sur le poste, pas seulement de la configuration du routeur.

Une passerelle doit normalement être une adresse utilisable sur le même segment de couche 2 que l’hôte et sur l’interface du routeur desservant ce sous-réseau. Configurer une passerelle qui appartient à un sous-réseau différent entraîne généralement un problème de résolution ou de connectivité. Certaines fonctionnalités avancées peuvent modifier la manière dont la passerelle est présentée, mais elles doivent être documentées séparément.

Pour un diagnostic, il faut vérifier simultanément l’adresse IP, le masque, la passerelle, le VLAN du port et l’adresse de l’interface routeur ou SVI. Une adresse IP correcte dans le mauvais VLAN reste généralement inutilisable, tout comme une adresse située dans le bon VLAN mais associée au mauvais masque.

### 1.15. DHCP, adresses statiques et réservations

Le protocole DHCP fournit dynamiquement aux clients une adresse IP et d’autres paramètres, tels que le masque, la passerelle par défaut et les serveurs DNS. Le plan d’adressage doit déterminer quelles adresses sont distribuées automatiquement, lesquelles sont réservées à l’infrastructure et comment éviter les conflits.

Une plage DHCP ne doit pas inclure par erreur les adresses utilisées par les routeurs, les commutateurs de couche 3, les serveurs statiques ou les équipements réservés si ces usages ne sont pas gérés par des réservations cohérentes. Dans les réseaux d’entreprise, la documentation doit indiquer la plage dynamique, les exclusions, les réservations et le responsable de chaque bloc.

Le relais DHCP (*DHCP relay*) est nécessaire dans les architectures où les clients et le serveur DHCP ne se trouvent pas dans le même domaine de broadcast. L’interface VLAN ou le routeur qui reçoit la diffusion DHCP la relaie au serveur configuré, en permettant à celui-ci d’identifier le sous-réseau concerné. Le mécanisme doit être prévu lors de la conception des passerelles.

Une erreur de pool DHCP peut attribuer un masque incorrect, une mauvaise passerelle ou un serveur DNS inadapté. Le diagnostic d’un client doit donc vérifier le bail obtenu, puis comparer les options avec le plan d’adressage et la configuration de l’interface de passerelle. Une adresse attribuée ne garantit pas que les autres paramètres soient corrects.

### 1.16. Effets d’un masque incorrect

Le masque détermine les frontières perçues par chaque hôte et influence le choix entre livraison locale et envoi à la passerelle. Il peut donc provoquer des symptômes qui ne ressemblent pas, au premier abord, à une erreur de sous-réseautage.

**Masque trop large :** l’hôte considère certaines destinations distantes comme locales et tente de les résoudre directement par ARP. L’équipement distant n’étant pas dans le même domaine de couche 2, la résolution échoue. L’hôte peut tout de même atteindre certaines destinations par d’autres routes, ce qui rend la panne partielle.

**Masque trop étroit :** l’hôte considère certaines destinations locales comme distantes et envoie les paquets à la passerelle. Selon la topologie et le comportement du routeur, la communication peut fonctionner mais emprunter un chemin inattendu, ou échouer si le routage de retour n’est pas prévu.

**Masques incohérents sur un même LAN :** certains hôtes pensent être dans le même sous-réseau et d’autres non. Les flux peuvent fonctionner dans un sens et échouer dans l’autre. Il faut comparer la configuration effective des terminaux, pas seulement les valeurs prévues dans la documentation.

**Mauvaise passerelle :** l’hôte peut atteindre les voisins locaux mais pas les réseaux distants. Un problème de passerelle peut être confondu avec un problème DNS, surtout lorsque l’utilisateur constate seulement que les noms de domaine ne se résolvent pas ou que les services Internet sont indisponibles.

### 1.17. Adressage et sécurité réseau

Le plan IPv4 participe à la sécurité en séparant les fonctions, en facilitant les politiques de filtrage et en réduisant les relations de confiance implicites. Une architecture qui place postes utilisateurs, serveurs, équipements de gestion et terminaux invités dans le même sous-réseau rend souvent plus difficile l’application de politiques précises.

L’adressage n’est cependant pas un mécanisme de sécurité à lui seul. La présence de sous-réseaux distincts ne garantit pas que leur communication soit filtrée. Il faut configurer les ACL, les pare-feu, les politiques de segmentation ou les contrôles de couche 2 correspondant à la stratégie de sécurité.

Le choix des plages doit aussi tenir compte des VPN et des partenaires. Des chevauchements entre réseaux privés peuvent rendre les routes ambiguës et imposer une traduction d’adresses qui complique les règles de sécurité et le dépannage. Une plage RFC 1918 est réutilisable, mais cela ne signifie pas que tous les choix d’adressage privés sont sans conséquence.

Enfin, l’adressage doit être documenté et géré comme une donnée d’exploitation. Les changements de masque, de passerelle, de sous-réseau ou d’agrégat doivent être enregistrés. Une documentation obsolète peut produire des règles ACL inexactes, des pools DHCP qui se chevauchent ou des routes statiques qui pointent vers une ancienne topologie.

> **Piège :** Ne confonds pas la taille du préfixe et le nombre d’adresses utilisables. Un `/26` contient 64 adresses au total, mais dans un sous-réseau conventionnel il fournit 62 adresses d’hôtes. Ne suppose pas non plus que tout `/31` perd deux adresses : la RFC 3021 autorise l’usage des deux adresses sur certaines liaisons point-à-point. Enfin, ne déduis pas le masque à partir de l’ancienne classe A, B ou C : en CIDR, le préfixe réel doit être fourni et vérifié.

```text
                   PLAN D'ADRESSAGE HIÉRARCHIQUE

                Bloc parent : 10.60.8.0/22
                           |
           +---------------+----------------+
           |                                |
     10.60.8.0/24                    10.60.9.0/24
     LAN utilisateurs                       |
                                  +---------+---------+
                                  |         |         |
                             10.60.9.0/25  .128/27  .160/28 ...
                                  Voix     Gestion   Petits LANs

             Routage local / agrégation selon le design
```

---

## 2. Configuration et Pratique

### 2.1. Construire un plan avant de configurer les routeurs

La configuration doit refléter le plan d’adressage validé. Avant d’entrer les commandes, il faut confirmer l’adresse réseau, le préfixe, la passerelle, le VLAN de destination, le protocole de routage éventuel et les plages réservées. La même convention doit être utilisée dans les tableaux d’adressage, les pools DHCP et la documentation de routage.

Considérons une topologie de laboratoire :

- VLAN 10 — Utilisateurs : `192.168.10.0/24`, passerelle `192.168.10.1`.
- VLAN 20 — Voix : `192.168.20.0/25`, passerelle `192.168.20.1`.
- VLAN 30 — Gestion : `192.168.30.0/27`, passerelle `192.168.30.1`.
- Lien R1–R2 : `10.255.0.0/31`, si les deux extrémités prennent en charge ce préfixe sur ce lien point-à-point.

Les blocs sont séparés et ne se chevauchent pas. Les tailles répondent à des besoins différents, ce qui illustre VLSM. Dans un réseau en production, il faudrait aussi documenter les plages DHCP, adresses statiques, réservations, équipements d’infrastructure et préfixes prévus pour la croissance.

### 2.2. Configurer des interfaces IPv4 sur Cisco IOS

Exemple pour un routeur doté d’une interface LAN :

```cisco
hostname R1
!
interface GigabitEthernet0/0
 description LAN_UTILISATEURS
 ip address 192.168.10.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 description LIEN_VERS_R2
 ip address 10.255.0.0 255.255.255.254
 no shutdown
!
end
```

La commande `ip address` associe une adresse et un masque à l’interface. `no shutdown` retire l’arrêt administratif ; elle ne garantit pas qu’une liaison physique distante soit opérationnelle. L’état doit être vérifié ensuite.

Le lien `/31` est un exemple adapté à une liaison point-à-point compatible. Son adresse de réseau apparente peut aussi être une adresse d’extrémité dans ce contexte. Si la plateforme ou le type d’interface ne prend pas en charge ce comportement, utiliser un `/30` conventionnel, par exemple `10.255.0.0/30`, avec `10.255.0.1` et `10.255.0.2` comme adresses d’extrémité.

Les noms d’interface sont propres aux modèles. Sur certains équipements, les interfaces sont nommées `GigabitEthernet0/0/0`, `TenGigabitEthernet1/0/1` ou autrement. Il faut vérifier la nomenclature réellement présentée par l’équipement plutôt que copier aveuglément un exemple.

### 2.3. Configurer des interfaces VLAN (SVI)

Sur un commutateur de couche 3 Cisco, une interface VLAN (SVI) peut servir de passerelle pour un VLAN. L’exemple suivant illustre la configuration des interfaces logiques et l’activation du routage IPv4 :

```cisco
hostname SW-CORE
!
ip routing
!
interface Vlan10
 description PASSERELLE_UTILISATEURS
 ip address 192.168.10.1 255.255.255.0
 no shutdown
!
interface Vlan20
 description PASSERELLE_VOIX
 ip address 192.168.20.1 255.255.255.128
 no shutdown
!
interface Vlan30
 description PASSERELLE_GESTION
 ip address 192.168.30.1 255.255.255.224
 no shutdown
```

Une SVI peut rester opérationnellement inactive tant que le VLAN n’existe pas ou qu’aucun port actif n’offre les conditions requises par la plateforme. Les états exacts dépendent du modèle et du système. Il faut donc créer les VLANs, affecter ou transporter les VLANs selon la topologie et vérifier l’état de chaque SVI.

La commande `ip routing` active le routage IPv4 sur les commutateurs qui utilisent cette syntaxe. Elle n’est pas nécessaire sur tous les types de commutateurs ou toutes les plateformes. Un commutateur de couche 2 ne se transforme pas en routeur complet simplement parce qu’une commande d’interface VLAN est présente.

La passerelle doit être cohérente avec le préfixe attribué aux postes. Un PC dans `192.168.20.0/25` peut utiliser `192.168.20.1/25` comme passerelle. Si le PC reçoit par erreur un `/24`, il considérera une plage de destinations plus large comme locale, ce qui peut provoquer des échecs de communication inattendus.

### 2.4. Vérifier les adresses et les états

Les commandes de vérification de base sous Cisco IOS/IOS XE comprennent :

```cisco
show ip interface brief
show interfaces GigabitEthernet0/0
show running-config interface GigabitEthernet0/0
show ip route connected
```

`show ip interface brief` présente un résumé des interfaces et de leurs adresses. `show interfaces` fournit davantage de détails sur l’état et les compteurs. `show running-config interface` affiche la configuration appliquée à l’interface si la version dispose de cette syntaxe. `show ip route connected` permet de consulter les réseaux directement connectés reconnus par la table de routage.

Il faut distinguer l’adresse configurée et la route connectée installée. Une interface administrativement désactivée ou dont l’état de protocole est inactif peut ne pas fournir la connectivité attendue même si une adresse figure dans la configuration.

Lorsqu’une route connectée manque, vérifier successivement : l’existence de l’interface, son adresse et son masque, son état, le VLAN correspondant s’il s’agit d’une SVI et la prise en charge du routage sur la plateforme. Ne pas commencer par ajouter une route statique vers un réseau qui devrait être directement connecté.

### 2.5. Routage statique et route par défaut

L’adressage permet de définir les réseaux, mais les routeurs ont aussi besoin d’informations pour atteindre les destinations distantes. Dans un petit laboratoire, des routes statiques peuvent convenir. Une route statique IPv4 Cisco suit généralement cette forme :

```cisco
ip route <réseau-destination> <masque> <prochain-saut-ou-interface>
```

Par exemple, sur R1, pour atteindre `192.168.50.0/24` via le prochain saut `10.255.0.1` :

```cisco
ip route 192.168.50.0 255.255.255.0 10.255.0.1
```

Le prochain saut doit être joignable à travers une route existante. Une route statique incorrecte peut être présente dans la configuration, mais inutilisable si le prochain saut est inaccessible ou si une meilleure route interagit avec elle. La commande `show ip route` sert à confirmer ce qui a réellement été installé.

Une route par défaut peut être configurée comme suit :

```cisco
ip route 0.0.0.0 0.0.0.0 10.255.0.1
```

Elle représente toutes les destinations qui ne correspondent à aucune route plus spécifique disponible. Elle ne signifie pas que toutes les destinations sont réellement joignables ; elle indique seulement où envoyer le trafic qui n’a pas de correspondance plus spécifique.

Dans une architecture plus large, un protocole dynamique peut distribuer les routes au lieu d’exiger une configuration statique de chaque destination. Le plan d’adressage doit alors permettre l’annonce des préfixes corrects et, si nécessaire, leur agrégation. Une route par défaut ne doit pas masquer une erreur d’adressage ou un manque de route interne.

### 2.6. Définir des plages DHCP sur Cisco IOS

Un exemple simple de configuration DHCP locale sur un routeur Cisco est présenté ci-dessous :

```cisco
ip dhcp excluded-address 192.168.10.1 192.168.10.30
!
ip dhcp pool VLAN10-USERS
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 1.1.1.1 8.8.8.8
 domain-name entreprise.example
```

La plage exclue réserve les adresses `.1` à `.30` en dehors des attributions dynamiques. Le pool indique le réseau et le masque, la passerelle par défaut, puis les serveurs DNS distribués aux clients. Les adresses DNS de l’exemple doivent être adaptées à la politique de l’organisation ; dans un environnement d’entreprise, des résolveurs internes sont souvent utilisés.

Le pool doit correspondre exactement au sous-réseau concerné. Une erreur de masque ou de passerelle distribue des paramètres incohérents aux clients. Il faut aussi vérifier que le serveur DHCP est autorisé sur le segment et qu’aucun autre serveur non prévu n’attribue des informations concurrentes.

Commandes utiles :

```cisco
show ip dhcp pool
show ip dhcp binding
show ip dhcp conflict
```

Le premier affiche les informations des pools, le second les baux attribués, et le troisième les conflits détectés selon la plateforme. Les commandes exactes et leurs détails peuvent varier avec la version logicielle.

### 2.7. Relais DHCP pour les sous-réseaux distants

Lorsqu’un serveur DHCP n’est pas directement raccordé au domaine de broadcast des clients, l’interface de couche 3 peut relayer les demandes à l’aide de `ip helper-address` sur certaines plateformes Cisco IOS.

Exemple :

```cisco
interface Vlan20
 description PASSERELLE_VOIX
 ip address 192.168.20.1 255.255.255.128
 ip helper-address 192.168.100.10
 no shutdown
```

`192.168.100.10` représente ici l’adresse du serveur DHCP. Le relais reçoit la demande client puis la transmet au serveur en préservant les informations nécessaires pour identifier le réseau d’origine. Le serveur doit disposer d’un pool correspondant à `192.168.20.0/25` et renvoyer des paramètres adaptés à ce segment.

En environnement sécurisé, la fonction de relais doit être configurée uniquement là où elle est nécessaire. Il faut également s’assurer que les ACL ou les pare-feu permettent les communications DHCP appropriées entre la passerelle et le serveur.

Le diagnostic d’un échec DHCP doit vérifier l’état du VLAN et de la SVI, l’existence du relais, l’accessibilité du serveur, la disponibilité du pool et le chemin retour vers le relais. Le serveur peut être opérationnel tout en ne distribuant aucune adresse au VLAN concerné si le pool correspondant est absent ou épuisé.

### 2.8. Configurer et vérifier un résumé de routes

Le résumé de routes est souvent configuré à la frontière d’un site ou d’un domaine de routage. La syntaxe varie selon le protocole utilisé. Le principe fondamental reste identique : n’annoncer un agrégat que si ses effets et sa couverture sont compris.

Dans EIGRP, par exemple, une agrégation manuelle peut être configurée sur une interface avec une commande de résumé prise en charge par IOS/IOS XE. La forme exacte et la portée dépendent du mode EIGRP utilisé. Avant de l’appliquer, il faut confirmer que l’agrégat représente les préfixes attendus et que l’architecture gère correctement les destinations absentes.

Dans OSPF, les mécanismes de résumé se placent dans des contextes précis, tels que les frontières entre aires ou systèmes externes, et ne sont pas équivalents à une commande d’agrégation générique sur n’importe quelle interface. Il faut donc appliquer la syntaxe du protocole réel plutôt que mélanger les exemples.

Pour valider l’agrégation :

1. Lister les préfixes internes et leurs masques.
2. Calculer la plage couverte par l’agrégat proposé.
3. Vérifier l’alignement binaire.
4. Comparer la couverture avec les préfixes réellement détenus.
5. Identifier les destinations inexistantes que l’agrégat pourrait néanmoins couvrir.
6. Vérifier les routes plus spécifiques et le comportement en cas de panne.
7. Tester l’annonce reçue par les routeurs voisins et le chemin de retour.

Une agrégation correcte simplifie le routage, mais une agrégation trop large peut masquer une panne ou conduire un routeur à attirer un trafic qu’il ne peut pas acheminer.

### 2.9. Documenter le plan d’adressage

Un tableau d’adressage exploitable devrait inclure au minimum : site, VLAN ou segment, fonction, préfixe CIDR, masque décimal, passerelle, plage DHCP, adresses réservées, broadcast lorsque pertinent, équipements qui annoncent le préfixe et statut du bloc.

Exemple de structure :

| Site | VLAN | Fonction | Préfixe | Passerelle | DHCP | Réservations |
|---|---:|---|---|---|---|---|
| Siège | 10 | Utilisateurs | `192.168.10.0/24` | `192.168.10.1` | `.50–.220` | `.2–.49` infrastructure |
| Siège | 20 | Voix | `192.168.20.0/25` | `192.168.20.1` | Selon le service voix | `.2–.19` équipements fixes |
| Siège | 30 | Gestion | `192.168.30.0/27` | `192.168.30.1` | Aucun ou réservations contrôlées | Adresses d’administration |
| Transit | — | R1–R2 | `10.255.0.0/31` | Sans passerelle LAN | Aucun | Deux extrémités point-à-point |

La documentation doit être mise à jour lorsque les VLANs, préfixes, passerelles ou pools DHCP changent. Les noms des segments doivent être cohérents entre l’IPAM, la configuration des commutateurs, les routeurs, le système de supervision et les documents d’exploitation.

### 2.10. Automatiser la validation

Dans une organisation, les calculs manuels ne sont pas toujours suffisants lorsque le nombre de préfixes augmente. Un outil IPAM, un tableur doté de contrôles ou un script d’audit peut vérifier automatiquement plusieurs règles :

- le réseau déclaré correspond à l’adresse et au préfixe calculés ;
- les préfixes ne se chevauchent pas, sauf si une superposition est délibérée et isolée ;
- les blocs sont alignés sur les frontières binaires ;
- la plage DHCP est contenue dans le sous-réseau ;
- la passerelle est une adresse autorisée du segment ;
- les agrégats couvrent les préfixes attendus et ne sont pas excessivement larges ;
- les adresses spéciales ne sont pas attribuées comme des adresses d’hôtes ordinaires dans un contexte conventionnel.

La validation automatisée devrait produire une sortie lisible et un rapport d’erreurs explicite. Un contrôle qui se contente de signaler « erreur » sans indiquer le chevauchement ou la mauvaise frontière n’aide pas assez les équipes d’exploitation.

La base d’adressage doit être la source de vérité. Si le tableau, la configuration et le système IPAM contiennent des valeurs divergentes, les équipes risquent d’appliquer un plan ancien et de créer de nouveaux chevauchements. Le processus de changement doit donc préciser quel outil est maître, qui peut approuver les modifications et comment la configuration réelle est comparée à la documentation.

> **Astuce :** Pour un calcul rapide, repère l’octet où le masque n’est ni `255` ni `0`, puis calcule `256 − masque`. Cette taille de bloc donne les frontières possibles dans cet octet. Pour valider un résumé, fais l’opération inverse : calcule le nombre d’adresses couvertes, vérifie l’alignement de l’adresse de départ et assure-toi que tous les préfixes internes sont contenus dans l’agrégat sans englober involontairement d’autres allocations.

---

## 3. Dépannage et Sécurité

### 3.1. Une méthode de diagnostic fondée sur les couches

Le dépannage doit aller du plus simple au plus spécifique. Commence par déterminer si le problème est local à un hôte, limité à un VLAN ou lié au routage entre sous-réseaux. Note l’adresse IP, le masque, la passerelle, le VLAN et la destination qui échoue. Ces informations suffisent souvent à déceler une incohérence de préfixe.

Pour un problème sur un hôte, vérifie sa configuration effective avec les outils du système d’exploitation. Sur Windows, `ipconfig /all` permet d’examiner l’adresse IPv4, le masque, la passerelle, le serveur DHCP et les DNS. Sur Linux, `ip address`, `ip route` et les outils de résolution appropriés montrent les adresses et les routes. Les commandes exactes dépendent de la distribution et de l’environnement.

Sur Cisco IOS/IOS XE, la séquence de départ peut être :

```cisco
show ip interface brief
show ip route
show arp
show interfaces status
```

Toutes les commandes ne sont pas disponibles sur chaque modèle. L’objectif est de vérifier l’état des interfaces, les routes installées, la résolution de couche 2 et l’état des ports si le matériel les prend en charge.

Ensuite, teste séparément la passerelle, une destination connue dans un autre sous-réseau et, si nécessaire, le serveur DNS. Une réussite vers la passerelle mais un échec vers les destinations distantes suggère un problème de routage, de filtrage ou de retour, mais ne permet pas à elle seule de conclure. Il faut confirmer le chemin réel et les routes nécessaires dans les deux directions.

### 3.2. Diagnostic : les hôtes locaux ne communiquent pas

Lorsque deux hôtes supposés appartenir au même sous-réseau ne communiquent pas, plusieurs causes sont possibles : masques incohérents, VLAN différents, mauvais câblage, port de commutateur mal configuré, conflit d’adresse IP, filtrage local ou problème de résolution ARP.

Les vérifications doivent comparer les préfixes réellement configurés sur les deux hôtes. Deux adresses dans la même plage décimale ne prouvent pas qu’elles utilisent le même sous-réseau : les masques peuvent être différents. Par exemple, `192.168.10.10/24` et `192.168.10.200/25` ne considèrent pas nécessairement la destination de la même manière lorsque l’adresse se trouve dans la seconde moitié de la plage.

Vérifie aussi que les deux ports appartiennent au VLAN attendu. En environnement Cisco, `show vlan brief`, `show interfaces switchport` et `show mac address-table` peuvent aider selon la plateforme. Pour un problème ARP, examine la table ARP et recherche une résolution incomplète ou une adresse MAC inattendue.

Il faut éviter d’ajouter une route au hasard lorsque le problème est sur le même segment de couche 2. Si les hôtes devraient communiquer directement, le premier diagnostic concerne l’adressage et le domaine de broadcast, pas nécessairement le routeur.

### 3.3. Diagnostic : un hôte atteint son réseau local, mais pas Internet

Si un poste communique avec les hôtes locaux, mais pas avec les réseaux distants, vérifie en premier lieu la passerelle par défaut et le masque. Le poste peut avoir une adresse correcte mais une passerelle absente, incorrecte ou située dans un autre sous-réseau logique.

Ensuite, examine la table de routage du routeur de passerelle et la présence d’une route vers la destination. Sur Cisco IOS, `show ip route` montre les préfixes connus et la route par défaut éventuelle. Une route par défaut vers un prochain saut inaccessible ne fournit pas de connectivité réelle.

Dans un réseau connecté à Internet, contrôle aussi la traduction NAT/PAT et les règles de filtrage applicables. Les adresses privées RFC 1918 ne sont normalement pas routées directement sur l’Internet public. Il faut une passerelle ou une architecture qui fournisse la connectivité sortante selon la politique du réseau.

Si l’accès par adresse IP fonctionne mais que les noms ne se résolvent pas, le problème peut relever du DNS plutôt que de l’adressage. Vérifie les serveurs DNS configurés sur le client et les paramètres distribués par DHCP. Le dépannage doit distinguer la connectivité IP de la résolution de noms.

### 3.4. Chevauchement de sous-réseaux

Un chevauchement survient lorsque deux allocations distinctes couvrent au moins certaines des mêmes adresses. Cela peut provoquer des routes ambiguës, des comportements différents entre sites et des difficultés d’interconnexion par VPN.

Exemple : un site utilise `10.10.0.0/16` et un autre utilise `10.10.20.0/24`. Ces préfixes se chevauchent, car le `/24` est contenu dans le `/16`. Les conséquences dépendent de la manière dont les réseaux sont connectés et des routes installées, mais ce type de plan doit être évité lorsqu’il s’agit de domaines d’adressage indépendants.

La détection doit comparer les plages calculées, pas seulement les chaînes de texte. Un outil IPAM est particulièrement utile pour éviter les chevauchements dans les grandes organisations. Il doit prendre en compte toutes les allocations, y compris les préfixes réservés, les liens de transit, les loopbacks, les VPN et les réseaux de partenaires.

Lorsque le chevauchement est déjà en place, les solutions peuvent inclure la renumérotation, la traduction d’adresses ou l’isolation des domaines. La solution dépend du périmètre et des exigences applicatives. Une traduction peut résoudre certains scénarios d’interconnexion, mais elle ajoute de la complexité au dépannage et peut affecter les protocoles qui transportent des adresses dans leur charge utile.

### 3.5. Route plus spécifique inattendue

Une destination peut être envoyée vers un prochain saut surprenant parce que la table contient un préfixe plus spécifique que l’agrégat attendu. Le routeur applique le *Longest Prefix Match* : la route ayant le plus grand nombre de bits de préfixe est choisie parmi les entrées correspondantes.

Si la table contient `10.0.0.0/8` via le cœur et `10.20.30.0/24` via un autre routeur, un paquet destiné à `10.20.30.5` utilisera le `/24`. La route `/8` ne sera pas utilisée pour cette destination tant que le `/24` est installé et correspond au paquet.

Ce comportement peut être voulu ou signaler une annonce incorrecte. Pour le déterminer, examine le préfixe réellement installé, sa source, sa métrique, son prochain saut et la route sur les équipements voisins. Il faut éviter de supposer qu’une route agrégée l’emporte parce qu’elle a été configurée intentionnellement.

Une route `/32` peut aussi attirer un trafic spécifique et l’éloigner du chemin normal. Dans une exploitation robuste, les annonces de préfixes hôtes doivent donc être contrôlées lorsqu’elles ne sont pas requises par la conception.

### 3.6. Incohérence entre routeur et client DHCP

Si le routeur utilise `/25` et le client obtient `/24`, les deux équipements n’ont pas la même vision des frontières réseau. Le client peut tenter de communiquer directement avec une destination qui, du point de vue du routeur, appartient à un autre sous-réseau. Les symptômes peuvent inclure des communications intermittentes, un retour asymétrique ou des connexions qui fonctionnent pour certaines destinations mais pas d’autres.

Vérifie le bail obtenu, le masque, la passerelle, la plage DHCP et les exclusions. Assure-toi que le pool est associé au bon réseau et que les demandes DHCP arrivent au serveur depuis le VLAN prévu. Si un relais est utilisé, contrôle également l’adresse de l’interface qui transmet la demande et le pool choisi par le serveur.

Il peut aussi exister plusieurs serveurs DHCP sur le même segment. Dans ce cas, certains clients reçoivent le bon masque et d’autres un masque erroné, en fonction du serveur qui répond. Le contrôle de DHCP snooping, quand il est disponible et correctement déployé sur les commutateurs, peut contribuer à limiter les serveurs DHCP non autorisés. Cette fonction relève toutefois de la protection de couche 2 et ne remplace pas la vérification des pools.

### 3.7. Adresse de passerelle et route de retour

Une communication IP a généralement besoin d’un chemin aller et d’un chemin retour. Un paquet peut arriver au serveur, mais sa réponse peut être envoyée vers une autre passerelle ou un autre routeur ne connaissant pas le réseau d’origine.

Lors d’un diagnostic, ne vérifie donc pas seulement la route du client vers le serveur. Examine aussi la route depuis le serveur vers le réseau client. Les asymétries peuvent être légitimes, mais elles doivent rester compatibles avec les mécanismes de filtrage, NAT, pare-feu à état et politiques de routage.

Une passerelle redondante, telle que HSRP ou VRRP, ajoute un niveau de complexité : l’adresse virtuelle configurée sur les clients doit correspondre au bon sous-réseau et le groupe de redondance doit fonctionner comme prévu. Les hôtes ne doivent pas recevoir une passerelle appartenant à un autre VLAN ou à un ancien plan d’adressage.

Le diagnostic doit examiner les tables de routage et, si nécessaire, les tables ARP des deux côtés. Une adresse MAC inattendue pour la passerelle peut indiquer une bascule redondante, une mauvaise configuration ou un incident de sécurité. Il faut corréler ces informations avec les journaux et l’état des équipements.

### 3.8. Contrôles de sécurité des adresses

La sécurité de l’adressage commence par la gouvernance des allocations et la limitation des communications entre segments. Les ACL et les pare-feu peuvent appliquer des règles basées sur les préfixes, mais elles ne sont efficaces que si les adresses sont cohérentes et documentées.

Les bonnes pratiques incluent :

- réserver des blocs distincts pour les utilisateurs, serveurs, équipements de gestion, invités et interconnexions ;
- limiter les annonces de routes à celles que l’équipement doit réellement publier ;
- documenter les résumés et empêcher les agrégats plus larges que nécessaire ;
- contrôler les pools DHCP et les mécanismes de relais ;
- surveiller les conflits d’adresses et les routes plus spécifiques inattendues ;
- appliquer une politique adaptée aux adresses source sur les interfaces concernées ;
- éviter la réutilisation de préfixes privés entre domaines qui doivent communiquer sans traduction.

Le filtrage d’adresses IP ne remplace pas l’authentification. Une adresse source peut être falsifiée dans certaines conditions. Les protections contre l’usurpation d’adresse, telles que l’ingress filtering, les ACL d’interface ou les fonctions de sécurité de couche 2, doivent être définies en fonction de la topologie et des capacités des équipements.

### 3.9. Erreurs de conception et conséquences opérationnelles

Un plan d’adressage devient difficile à maintenir lorsqu’il est construit sans conventions. Des passerelles sur `.1` dans certains VLANs et sur des adresses aléatoires dans d’autres, des plages DHCP qui changent selon les sites ou des sous-réseaux placés sans logique rendent les interventions plus lentes et favorisent les erreurs humaines.

L’uniformité des conventions ne signifie pas qu’il faut absolument réserver la même adresse partout. Elle signifie que chaque règle doit avoir une raison et être documentée. Par exemple, un réseau de gestion peut utiliser des adresses statiques, tandis qu’un réseau utilisateur s’appuie sur DHCP. Les conventions doivent rester adaptées aux fonctions réelles.

Une allocation sans réserve de croissance peut forcer une renumérotation lors de l’ajout d’un nouveau service. À l’inverse, attribuer des blocs excessivement larges rend les agrégats moins précis, peut compliquer les politiques de sécurité et augmenter l’étendue des plages considérées comme locales par certains hôtes mal configurés.

La revue du plan doit également examiner le routage. Des préfixes propres à chaque site facilitent l’agrégation et réduisent les risques de chevauchement avec les VPN. Le plan d’adressage et les politiques de routage doivent être conçus ensemble, et non comme deux tâches indépendantes.

### 3.10. Liste de contrôle avant mise en production

Avant de déployer un nouveau sous-réseau IPv4, vérifie les éléments suivants :

1. Le bloc est autorisé et ne chevauche aucune allocation existante.
2. Le préfixe répond au besoin présent et à une croissance raisonnable.
3. L’adresse réseau et la plage de diffusion ont été calculées correctement.
4. Le masque ou le préfixe est identique dans les systèmes qui doivent partager le même sous-réseau.
5. La passerelle se trouve dans le segment correct et son adresse est réservée.
6. Le VLAN, l’interface routeur ou la SVI sont configurés et opérationnels.
7. Les pools DHCP, exclusions, options et relais sont cohérents.
8. Les routes internes, par défaut et les agrégats reflètent l’architecture réelle.
9. Les ACL et politiques de sécurité autorisent uniquement les flux nécessaires.
10. La documentation et l’inventaire IPAM ont été mis à jour.
11. Les tests de connectivité locale, distante et de retour ont réussi.
12. Le plan de retour arrière est connu en cas d’échec.

Cette checklist ne remplace pas les tests détaillés, mais elle évite de nombreuses erreurs de conception et sert de preuve de contrôle lors des changements réseau.

### 3.11. Scénario de synthèse

Une entreprise ajoute un VLAN destiné aux postes de formation. Le besoin initial est de 42 postes, 3 imprimantes, une passerelle et quelques adresses réservées. Le premier choix pourrait être un `/26`, qui fournit 62 adresses d’hôtes utilisables dans un sous-réseau conventionnel. Avant de retenir ce choix, l’ingénieur doit vérifier l’évolution attendue et l’espace disponible dans le bloc du site.

Il attribue ensuite un préfixe aligné, par exemple `192.168.60.64/26`, si cette plage est libre. L’adresse de réseau est `.64`, le broadcast `.127`, et la plage d’hôtes conventionnelle `.65–.126`. Une passerelle peut être placée sur `.65`, tandis que le pool DHCP exclut les adresses réservées aux équipements et à l’infrastructure.

Le VLAN est créé sur les commutateurs, la SVI reçoit l’adresse de passerelle, le routage est activé sur le commutateur de couche 3 si la plateforme l’exige, et les politiques de sécurité sont définies. Si les réseaux du site sont agrégés vers le cœur, l’ingénieur vérifie que le préfixe appartient au bloc résumé et que le résumé existant couvre correctement le nouveau VLAN.

Après la mise en service, les tests vérifient l’obtention du bail DHCP, la connectivité vers la passerelle, l’accès aux services autorisés, la résolution DNS, le chemin de retour et les journaux de routage. Si le poste reçoit un masque `/24` alors que la SVI utilise `/26`, la configuration DHCP est corrigée avant l’ajout de routes. Cette démarche montre pourquoi le sous-réseautage, le DHCP, la segmentation et le routage doivent être étudiés ensemble.

> **Danger :** Un plan IPv4 erroné ne provoque pas seulement une mauvaise attribution d’adresse. Un chevauchement de préfixes, une route plus spécifique indésirable ou un résumé trop large peut détourner le trafic, interrompre un VPN, exposer un segment à des communications non prévues ou masquer une panne. Avant toute modification d’un masque, d’un pool DHCP ou d’un agrégat, vérifie les dépendances, les routes aller-retour, les règles ACL et le comportement des autres sites. Les changements d’adressage doivent être documentés, testés et accompagnés d’une procédure de retour arrière.

## Points à retenir

- **CIDR et VLSM remplacent la logique de classes dans la conception moderne.** Le préfixe doit être connu explicitement, les blocs doivent être alignés et les besoins les plus grands doivent généralement être alloués avant les plus petits. Le plan doit intégrer la croissance, les réserves et la possibilité d’agrégation.

- **La sélection de route suit le principe du préfixe le plus long parmi les routes correspondantes.** Une route plus spécifique peut l’emporter sur un agrégat plus large. Le résumé doit être calculé avec précision et ne doit pas couvrir involontairement des destinations que le routeur ne peut pas acheminer.

- **L’adressage, le VLAN, le DHCP, les routes et la sécurité forment un seul système opérationnel.** Un masque incorrect modifie la décision locale/distance d’un hôte ; un mauvais pool DHCP distribue des paramètres erronés ; une passerelle ou une route de retour incohérente peut bloquer le trafic. Toujours vérifier la configuration effective, la table de routage, les chemins aller-retour et la documentation.

---

### Références techniques

- [RFC 4632 — Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632.html)
- [RFC 1918 — Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918.html)
- [RFC 3021 — Using 31-Bit Prefixes on IPv4 Point-to-Point Links](https://www.rfc-editor.org/rfc/rfc3021.html)
- [RFC 6598 — IANA-Reserved IPv4 Prefix for Shared Address Space](https://www.rfc-editor.org/rfc/rfc6598.html)
- [IANA — IPv4 Address Space Registry](https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xhtml)
