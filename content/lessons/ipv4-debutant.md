# Adressage IPv4 & sous-réseaux - Débutant

**Niveau :** Débutant

L’adressage IPv4 est l’un des fondements du fonctionnement des réseaux informatiques. Chaque hôte qui communique au moyen d’IPv4 utilise une adresse logique permettant aux équipements réseau d’identifier la source et la destination des paquets. Cette adresse intervient aussi dans les décisions de routage : un routeur examine l’adresse IP de destination et choisit une route correspondant au préfixe approprié. Sans un plan d’adressage cohérent, les postes, serveurs, imprimantes, téléphones IP et équipements d’interconnexion ne peuvent pas communiquer correctement, même si les câbles et les commutateurs fonctionnent.

IPv4 a été défini dans les premières étapes du développement de l’Internet et utilise des adresses de 32 bits. L’écriture décimale pointée, comme `192.168.10.25`, rend ces 32 bits plus simples à lire pour un administrateur. À l’origine, l’adressage a été organisé selon des classes A, B et C. Cette organisation historique a été remplacée dans l’exploitation moderne par l’adressage sans classe, ou CIDR, qui permet d’attribuer des préfixes de longueur variable. Ce changement a rendu l’utilisation de l’espace IPv4 plus efficace et a permis d’agréger les routes. Les principes sont décrits notamment dans les RFC 791, RFC 1918 et RFC 4632.

Le sous-réseautage consiste à diviser un bloc d’adresses en réseaux plus petits. Un masque de sous-réseau, ou une longueur de préfixe telle que `/24`, indique quelle partie de l’adresse identifie le réseau et quelle partie peut identifier les interfaces à l’intérieur de ce réseau. La capacité à calculer correctement un réseau, sa plage d’adresses, son adresse de diffusion et le nombre d’hôtes utilisables est indispensable pour configurer des postes, dimensionner un LAN, définir des VLANs et préparer les interfaces d’un routeur.

Dans un environnement professionnel, un plan IPv4 bien conçu facilite l’administration, le dépannage, la segmentation, le routage et l’évolution du réseau. Il évite les chevauchements de sous-réseaux, réduit les erreurs de passerelle et facilite la création de règles de sécurité. Cette compétence est également centrale pour les certifications réseau : elle sert dans les exercices de commutation, de routage statique, d’OSPF, d’EIGRP, de DHCP, d’ACL et de dépannage général.

> **Analogie** : Imagine une grande ville organisée en quartiers, rues et numéros de maison. L’adresse IP ressemble à l’adresse complète d’une habitation. Le préfixe réseau identifie le quartier ou la rue logique à laquelle appartient l’habitation ; la partie hôte identifie l’habitation elle-même à l’intérieur de ce secteur. Le masque est le plan qui permet de séparer les informations du quartier de celles de la maison.
>
> Un routeur joue le rôle d’un centre de tri postal. Il ne connaît pas nécessairement chaque maison du monde, mais il sait vers quelle région envoyer un colis en fonction de l’adresse de destination. Si une maison appartient au même quartier logique que l’expéditeur, celui-ci peut généralement communiquer directement avec elle sur le réseau local. Si elle se trouve dans un autre quartier, il envoie le paquet au routeur qui sert de passerelle. Le routeur examine alors l’adresse de destination et choisit le prochain tronçon.
>
> Le sous-réseautage revient à diviser un grand quartier en secteurs plus petits. Au lieu d’avoir un immense réseau où tous les équipements partagent le même domaine de diffusion, l’administrateur définit plusieurs sous-réseaux, souvent associés à des VLANs ou à des fonctions différentes. La taille de chaque secteur est déterminée par son préfixe. Un `/24` fournit, dans le cas classique, 254 adresses hôtes utilisables, tandis qu’un `/26` en fournit 62. Il ne suffit donc pas de choisir un nombre de chiffres : il faut déterminer le nombre de bits réservés au réseau et le nombre de bits restants pour les hôtes.
>
> L’adresse de réseau peut être comparée au nom d’un quartier, et l’adresse de diffusion à une annonce destinée à tous les logements de ce quartier. Ces deux adresses ne sont normalement pas attribuées aux hôtes dans les sous-réseaux IPv4 classiques. Cette analogie a cependant des limites : les adresses et les préfixes sont des valeurs binaires, et les routeurs prennent leurs décisions sur des bits, pas sur des noms de quartiers.

---

## 1. La théorie et les algorithmes

### 1.1. Qu’est-ce qu’une adresse IPv4 ?

IPv4 signifie *Internet Protocol version 4*. Le protocole décrit notamment le format du paquet IP et les règles de base permettant l’acheminement entre réseaux. Une adresse IPv4 contient exactement **32 bits**, regroupés en quatre octets de 8 bits. Chaque octet est affiché sous forme décimale, avec des points entre les valeurs.

Exemple :

```text
Adresse IPv4 : 192.168.10.25

Octets :       192     168      10      25
Bits :      11000000.10101000.00001010.00011001
             8 bits   8 bits   8 bits   8 bits

Total : 4 x 8 = 32 bits
```

Chaque octet peut prendre une valeur de 0 à 255. En binaire, un octet contient huit positions dont les poids sont 128, 64, 32, 16, 8, 4, 2 et 1. Le bit le plus à gauche a le poids le plus élevé. Pour convertir un octet binaire en décimal, on additionne les poids des positions contenant `1`.

Par exemple :

```text
Binaire : 11000000
Poids   : 128 64 32 16 8 4 2 1
Valeur  : 128 + 64 = 192
```

Autre exemple :

```text
Binaire : 00011001
Valeur  : 16 + 8 + 1 = 25
```

L’adresse `192.168.10.25` correspond ainsi à la suite de 32 bits indiquée dans le schéma. La notation décimale facilite la lecture, mais les opérations de masque et de routage sont fondées sur les bits.

Une adresse IPv4 est une adresse logique, et non l’adresse matérielle d’une carte réseau. L’adresse MAC est employée au niveau de la liaison locale, notamment sur Ethernet. L’adresse IP permet l’identification logique de la source et de la destination au niveau réseau. ARP, dans IPv4 sur les réseaux Ethernet, contribue à découvrir l’adresse MAC correspondant à une adresse IPv4 locale.

### 1.2. Adresse, masque et préfixe

Une adresse IPv4 configurée sur une interface doit être interprétée avec un masque de sous-réseau ou une longueur de préfixe. Le masque détermine quels bits représentent le réseau et quels bits sont réservés à la partie hôte.

Un masque IPv4 valide est constitué d’une série continue de bits `1` à gauche, suivie d’une série de bits `0` à droite. Les bits `1` forment la partie réseau ; les bits `0` forment la partie hôte.

| Préfixe CIDR | Masque décimal | Bits réseau | Bits hôte |
|---|---|---:|---:|
| `/8` | 255.0.0.0 | 8 | 24 |
| `/16` | 255.255.0.0 | 16 | 16 |
| `/24` | 255.255.255.0 | 24 | 8 |
| `/25` | 255.255.255.128 | 25 | 7 |
| `/26` | 255.255.255.192 | 26 | 6 |
| `/27` | 255.255.255.224 | 27 | 5 |
| `/28` | 255.255.255.240 | 28 | 4 |
| `/29` | 255.255.255.248 | 29 | 3 |
| `/30` | 255.255.255.252 | 30 | 2 |
| `/31` | 255.255.255.254 | 31 | 1 |
| `/32` | 255.255.255.255 | 32 | 0 |

La notation `/24` signifie que les 24 premiers bits sont utilisés pour identifier le préfixe réseau. Les huit bits restants peuvent représenter la partie hôte. Dans le sous-réseau classique `192.168.10.0/24`, l’adresse de réseau est `192.168.10.0`, l’adresse de diffusion dirigée vers le sous-réseau est `192.168.10.255`, et les adresses généralement attribuables aux hôtes vont de `192.168.10.1` à `192.168.10.254`.

Le préfixe et l’adresse doivent toujours être considérés ensemble. L’adresse `192.168.10.25` peut appartenir à `192.168.10.0/24`, mais aussi à un préfixe plus petit comme `192.168.10.0/26`, selon le plan d’adressage utilisé. L’adresse seule ne permet pas de déterminer sans ambiguïté le sous-réseau.

### 1.3. L’opération binaire AND

Pour calculer l’adresse de réseau, on applique une opération logique **AND** entre chaque bit de l’adresse IP et le bit correspondant du masque. Le résultat est le préfixe réseau, avec des zéros dans la partie hôte.

La table de vérité de l’opération AND est simple : le résultat vaut `1` uniquement lorsque les deux entrées sont égales à `1`.

| Bit IP | Bit masque | Résultat AND |
|---:|---:|---:|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

Exemple pour `192.168.10.25/24` :

```text
IP      : 11000000.10101000.00001010.00011001
Masque  : 11111111.11111111.11111111.00000000
          ----------------------------------- AND
Réseau  : 11000000.10101000.00001010.00000000

Résultat : 192.168.10.0/24
```

Cette opération fonctionne aussi pour les préfixes non alignés sur un octet, par exemple `/26` ou `/27`. C’est précisément là que le calcul manuel demande de l’attention.

Pour une interface configurée avec `192.168.10.25 255.255.255.192`, le masque du dernier octet vaut `192`, soit `11000000` en binaire. L’opération AND du dernier octet est :

```text
Adresse du dernier octet : 25 = 00011001
Masque du dernier octet  : 192 = 11000000
AND                       :      00000000 = 0
```

Le réseau correspondant est `192.168.10.0/26`. Les blocs `/26` du dernier octet sont `0–63`, `64–127`, `128–191` et `192–255`.

### 1.4. Comment calculer le nombre d’adresses

Si un préfixe IPv4 contient `p` bits réseau, il reste `32 - p` bits pour la partie hôte. Le nombre total de combinaisons d’adresses du sous-réseau est :


a) Nombre total d’adresses :

\[
2^{32-p}
\]

Dans le sous-réseau IPv4 classique, deux valeurs sont réservées : l’adresse de réseau (tous les bits hôte à zéro) et l’adresse de diffusion dirigée (tous les bits hôte à un). Le nombre d’adresses hôtes utilisables est donc habituellement :

\[
2^{32-p} - 2
\]

Cette règle s’applique aux sous-réseaux classiques comme `/24`, `/26`, `/27`, `/28`, `/29` et `/30`. Il existe des exceptions importantes : les préfixes `/31` peuvent être utilisés sur les liens point à point conformément à la RFC 3021, et `/32` représente une adresse unique, souvent utilisée comme route d’hôte ou adresse de loopback. Ne leur applique pas mécaniquement la formule « moins deux ».

| Préfixe | Bits hôte | Adresses totales | Hôtes utilisables dans un sous-réseau classique |
|---|---:|---:|---:|
| `/24` | 8 | 256 | 254 |
| `/25` | 7 | 128 | 126 |
| `/26` | 6 | 64 | 62 |
| `/27` | 5 | 32 | 30 |
| `/28` | 4 | 16 | 14 |
| `/29` | 3 | 8 | 6 |
| `/30` | 2 | 4 | 2 |
| `/31` | 1 | 2 | 2 sur un lien point à point compatible |
| `/32` | 0 | 1 | une adresse individuelle, pas un LAN ordinaire |

Exemple : `/27` laisse cinq bits pour les hôtes. Le sous-réseau possède donc `2^5 = 32` adresses au total et, dans le cas classique, `32 - 2 = 30` adresses utilisables.

> **Piège :** Ne confonds pas le nombre d’adresses totales et le nombre d’hôtes utilisables. Un `/27` contient 32 adresses, mais généralement 30 seulement peuvent être attribuées à des interfaces d’hôtes sur un LAN classique. Les exceptions `/31` et `/32` existent pour des usages particuliers et ne doivent pas être traitées comme des LAN ordinaires.

### 1.5. Déterminer l’adresse réseau, la diffusion et la plage hôte

Pour déterminer les informations d’un sous-réseau, il faut identifier le bloc auquel appartient l’adresse. Lorsque le masque n’est pas aligné sur une limite d’octet, la méthode du **pas de sous-réseau** simplifie le calcul.

Dans l’octet où le masque change de `255` vers une valeur inférieure à `255`, le pas est calculé ainsi :

\[
\text{Pas} = 256 - \text{valeur du masque dans cet octet}
\]

Exemples :

| Masque du dernier octet | Préfixe correspondant | Pas |
|---:|---:|---:|
| 128 | `/25` | 128 |
| 192 | `/26` | 64 |
| 224 | `/27` | 32 |
| 240 | `/28` | 16 |
| 248 | `/29` | 8 |
| 252 | `/30` | 4 |

Pour un `/26`, les blocs du dernier octet commencent à 0, 64, 128 et 192. Une adresse dont le dernier octet est compris entre 64 et 127 appartient au bloc qui commence à 64.

Exemple complet : déterminer le sous-réseau, l’adresse de diffusion et la plage utilisable de `192.168.10.77/26`.

1. Le masque `/26` vaut `255.255.255.192`.
2. Le pas du dernier octet vaut `256 - 192 = 64`.
3. Les débuts de blocs sont 0, 64, 128 et 192.
4. Le dernier octet `77` se trouve dans le bloc 64–127.
5. L’adresse réseau est `192.168.10.64`.
6. L’adresse de diffusion est `192.168.10.127`.
7. Les hôtes utilisables vont de `192.168.10.65` à `192.168.10.126`.

```text
Sous-réseau : 192.168.10.64/26
Masque      : 255.255.255.192
Réseau      : 192.168.10.64
Premier hôte: 192.168.10.65
Dernier hôte: 192.168.10.126
Diffusion   : 192.168.10.127
Total       : 64 adresses
Hôtes       : 62 utilisables
```

Il est souvent plus facile de calculer l’adresse de diffusion en prenant le dernier numéro du bloc. Pour un bloc qui démarre à 64 et dont le pas vaut 64, la fin est `64 + 64 - 1 = 127`.

### 1.6. Sous-réseaux alignés sur les octets

Les préfixes `/8`, `/16` et `/24` sont particulièrement simples à comprendre parce qu’ils se terminent sur une limite d’octet.

**Exemple `/24` :**

Adresse : `192.168.5.37/24`

- Masque : `255.255.255.0`
- Réseau : `192.168.5.0`
- Diffusion : `192.168.5.255`
- Plage hôte classique : `192.168.5.1` à `192.168.5.254`
- Hôtes utilisables : 254

**Exemple `/16` :**

Adresse : `172.20.9.41/16`

- Masque : `255.255.0.0`
- Réseau : `172.20.0.0`
- Diffusion : `172.20.255.255`
- Plage hôte classique : `172.20.0.1` à `172.20.255.254`
- Hôtes utilisables : 65 534

**Exemple `/8` :**

Adresse : `10.14.20.30/8`

- Masque : `255.0.0.0`
- Réseau : `10.0.0.0`
- Diffusion : `10.255.255.255`
- Plage hôte classique : `10.0.0.1` à `10.255.255.254`
- Hôtes utilisables : 16 777 214

Ces exemples montrent que plus le préfixe est court, plus le nombre de bits hôte est élevé et plus le sous-réseau contient d’adresses. Un préfixe plus long représente un bloc plus petit.

### 1.7. Préfixes CIDR et adressage sans classe

CIDR signifie *Classless Inter-Domain Routing*. Cette approche permet d’exprimer un réseau par une adresse et une longueur de préfixe, sans dépendre des anciennes classes A, B et C.

Historiquement, les adresses étaient souvent interprétées selon la première plage d’octets :

- Classe A historique : premier octet de 1 à 126 dans l’usage classful classique ;
- Classe B historique : premier octet de 128 à 191 ;
- Classe C historique : premier octet de 192 à 223.

Cette classification est surtout utile pour comprendre des documents anciens et l’évolution du routage. Dans les réseaux modernes, le masque ou préfixe configure la vraie frontière réseau. Une adresse commençant par `192` n’implique pas automatiquement un `/24`, et une adresse commençant par `10` n’impose pas un `/8` sur chaque interface.

Le préfixe `/20`, par exemple, couvre 20 bits réseau et 12 bits hôte. Il peut découper les limites d’octets, ce qui explique l’utilité du calcul binaire et du pas de sous-réseau.

CIDR permet également le résumé des routes. Plusieurs réseaux contigus peuvent être représentés par un préfixe agrégé si leur alignement binaire le permet et si la topologie justifie cet agrégat. Un agrégat trop large peut néanmoins annoncer des adresses qui ne sont pas réellement joignables ; les résumés doivent donc être conçus avec soin.

La RFC 4632 décrit les objectifs de l’adressage sans classe et de l’agrégation : limiter la croissance des tables de routage et utiliser l’espace d’adresses plus efficacement. L’administrateur réseau doit comprendre le préfixe non seulement pour compter les hôtes, mais aussi pour lire les routes, planifier les réseaux et éviter les chevauchements.

### 1.8. Adresses IPv4 privées et publiques

Les adresses IPv4 privées sont réservées aux réseaux internes et ne sont pas destinées à être routées directement sur l’Internet public. La RFC 1918 définit trois plages privées :

| Plage privée | Préfixe | Taille | Exemple d’utilisation |
|---|---|---:|---|
| `10.0.0.0` à `10.255.255.255` | `10.0.0.0/8` | 16 777 216 adresses | Grandes entreprises, campus ou réseaux multisites |
| `172.16.0.0` à `172.31.255.255` | `172.16.0.0/12` | 1 048 576 adresses | Réseaux internes de taille moyenne ou grande |
| `192.168.0.0` à `192.168.255.255` | `192.168.0.0/16` | 65 536 adresses | Réseaux domestiques, petites entreprises et laboratoires |

Les plages privées peuvent être utilisées simultanément par des organisations indépendantes. Le routeur de bordure réalise souvent une traduction d’adresses (NAT) pour permettre à des systèmes privés de communiquer avec des services Internet, selon l’architecture déployée. NAT ne rend pas à lui seul un réseau sûr ; les règles de pare-feu, la segmentation et la gestion des accès restent indispensables.

Une adresse publique est une adresse globalement attribuable dans le plan d’adressage Internet, sous réserve des règles d’allocation et des plages particulières. Il ne faut pas conclure qu’une adresse est publiquement routable simplement parce qu’elle ne fait pas partie des plages privées RFC 1918 : il existe aussi des blocs réservés à des usages spéciaux.

### 1.9. Quelques plages IPv4 particulières

Toutes les adresses IPv4 ne doivent pas être attribuées à des hôtes ordinaires. Certaines ont une fonction particulière.

| Plage ou adresse | Préfixe | Usage général |
|---|---|---|
| `0.0.0.0` | `0.0.0.0/32` pour cette adresse | Adresse non spécifiée dans des contextes précis ; la route `0.0.0.0/0` est la route par défaut |
| `127.0.0.0` à `127.255.255.255` | `127.0.0.0/8` | Bouclage local ; `127.0.0.1` est couramment utilisé pour tester la pile IP locale |
| `169.254.0.0` à `169.254.255.255` | `169.254.0.0/16` | Adressage IPv4 link-local, souvent autoattribué lorsqu’aucune configuration valable n’est reçue |
| `224.0.0.0` à `239.255.255.255` | `224.0.0.0/4` | Multicast IPv4 |
| `255.255.255.255` | `/32` | Diffusion limitée au réseau local IPv4 |
| `192.0.2.0/24` | `/24` | Documentation et exemples (TEST-NET-1) |
| `198.51.100.0/24` | `/24` | Documentation et exemples (TEST-NET-2) |
| `203.0.113.0/24` | `/24` | Documentation et exemples (TEST-NET-3) |

Les adresses TEST-NET ne sont destinées qu’aux exemples, aux manuels et aux documents. Il faut éviter de les utiliser comme adresses de production routables sur l’Internet public.

La route par défaut `0.0.0.0/0` ne signifie pas que l’adresse source d’un poste doit être `0.0.0.0`. Elle représente une route dont le préfixe ne fixe aucun bit, et qui peut donc servir de route de repli lorsqu’aucune route plus spécifique ne correspond.

### 1.10. Différence entre adresse réseau, adresse hôte et diffusion

Pour un sous-réseau classique IPv4, trois éléments sont importants :

- **Adresse réseau** : tous les bits de la partie hôte sont à zéro. Elle identifie le préfixe ou sous-réseau lui-même.
- **Adresse hôte** : une adresse valide attribuée à une interface à l’intérieur du sous-réseau, hors valeurs réservées dans l’usage classique.
- **Adresse de diffusion du sous-réseau** : tous les bits de la partie hôte sont à un. Elle sert à transmettre un paquet à tous les hôtes du sous-réseau, selon les conditions de routage et de filtrage.

Exemple avec `192.168.20.64/26` :

```text
Adresse réseau    : 192.168.20.64
Première adresse  : 192.168.20.65
Exemple d'hôte    : 192.168.20.90
Dernière adresse  : 192.168.20.126
Diffusion         : 192.168.20.127

Bloc complet      : 192.168.20.64 à 192.168.20.127
Nombre total      : 64 adresses
Adresses hôtes    : 62
```

Une erreur classique consiste à attribuer l’adresse réseau ou l’adresse de diffusion à un poste. Une autre consiste à penser que l’adresse de diffusion est toujours `.255`. Elle ne vaut `.255` que dans certaines configurations comme un `/24` dont le dernier octet représente entièrement la partie hôte. Dans un `/26`, la diffusion peut être `.63`, `.127`, `.191` ou `.255`, selon le bloc.

### 1.11. Comment un hôte décide-t-il d’envoyer directement ou via une passerelle ?

Lorsqu’un ordinateur souhaite envoyer un paquet IPv4, il compare l’adresse de destination avec son propre préfixe réseau. Si la destination appartient au même sous-réseau local, il essaie normalement de la joindre directement sur le lien local. Dans un réseau Ethernet, il doit connaître l’adresse MAC de destination, souvent en utilisant ARP si elle n’est pas déjà présente dans le cache.

Si la destination est située hors du sous-réseau local, l’hôte envoie normalement le paquet à la passerelle par défaut. La trame Ethernet est adressée à la MAC du routeur, tandis que le paquet IP conserve l’adresse IP du destinataire final. Le routeur retire l’en-tête de liaison reçu, examine l’adresse IP de destination, sélectionne une route et construit un nouvel en-tête de liaison sur l’interface de sortie.

```text
 PC-A                                           Serveur distant
192.168.1.10/24                                203.0.113.20
Passerelle : 192.168.1.1
     |                                                |
     | Paquet vers 203.0.113.20                       |
     v                                                |
+-------------+       +----------------+              |
| Switch LAN  |-------| Routeur R1     |--------------+
+-------------+       | 192.168.1.1    |
                      +----------------+

Destination hors du /24 : PC-A envoie la trame à la MAC
de sa passerelle ; le paquet IP vise toujours le serveur.
```

La passerelle par défaut doit être joignable sur le réseau local de l’interface. Configurer une adresse de passerelle qui se trouve dans un autre sous-réseau conduit généralement à une configuration incorrecte, sauf architecture particulière explicitement prise en charge.

La passerelle est également une dépendance importante du réseau : un poste peut communiquer avec d’autres hôtes du même sous-réseau sans routeur, mais il ne pourra généralement pas atteindre les réseaux distants si aucune passerelle valide n’est configurée.

### 1.12. Comment un routeur sélectionne une route IPv4

Un routeur consulte sa table de routage pour déterminer comment acheminer le paquet. Chaque route contient un préfixe de destination et des informations comme le prochain saut ou l’interface de sortie. Lorsque plusieurs routes correspondent à la destination, le principe général de transfert IP est de choisir la route correspondant au **préfixe le plus long** (*Longest Prefix Match*).

Exemple : la table contient :

```text
192.168.0.0/16     via 10.0.0.1
192.168.10.0/24    via 10.0.0.2
192.168.10.64/26   via 10.0.0.3
0.0.0.0/0          via 10.0.0.254
```

Pour une destination `192.168.10.77`, plusieurs préfixes correspondent. Le `/26` est le plus long et correspond au bloc `192.168.10.64–192.168.10.127`. Le routeur choisit donc la route `/26` si elle est installée et valide. La route par défaut est utilisée lorsqu’aucune route plus spécifique ne correspond.

Il faut distinguer le choix du préfixe le plus long de la sélection entre plusieurs routes candidates vers un même préfixe. Les protocoles de routage et les paramètres d’administration déterminent quelles routes sont installées ; le transfert IPv4 utilise ensuite la route correspondante la plus spécifique.

Une table de routage peut contenir des routes connectées, statiques, dynamiques ou une route par défaut. Lorsqu’une interface est correctement adressée et opérationnelle, le routeur ajoute normalement une route connectée correspondant au sous-réseau associé. Pour atteindre les autres réseaux, il faut des routes statiques ou un protocole de routage dynamique.

### 1.13. Calcul du sous-réseau avec une méthode mécanique

Pour résoudre un exercice, utilise toujours la même procédure :

1. Écris l’adresse IP et le préfixe, par exemple `172.16.35.123/20`.
2. Convertis le préfixe en masque : `/20` donne `255.255.240.0`.
3. Identifie l’octet non complet : ici le troisième octet du masque vaut 240.
4. Calcule le pas : `256 - 240 = 16`.
5. Trouve le multiple de 16 immédiatement inférieur ou égal au troisième octet de l’IP. `35` se situe dans le bloc `32–47`.
6. Fixe les bits hôte à zéro pour le réseau : `172.16.32.0`.
7. Fixe tous les bits hôte à un pour la diffusion : `172.16.47.255`.
8. Pour un sous-réseau classique, les hôtes utilisables vont de `172.16.32.1` à `172.16.47.254`.

Résultat :

```text
IP d'origine : 172.16.35.123/20
Masque       : 255.255.240.0
Pas          : 16 dans le troisième octet
Réseau       : 172.16.32.0/20
Diffusion    : 172.16.47.255
Premier hôte : 172.16.32.1
Dernier hôte : 172.16.47.254
Total        : 4096 adresses
Hôtes        : 4094 utilisables
```

Le calcul du troisième octet fonctionne parce que les 16 bits du premier et du deuxième octets sont entièrement dans le réseau et que le troisième octet est partagé entre la partie réseau et la partie hôte. Le dernier octet est entièrement destiné aux bits hôte dans cet exemple.

### 1.14. VLSM : utiliser des sous-réseaux de tailles différentes

VLSM signifie *Variable Length Subnet Mask*. Cela permet de diviser un espace d’adressage en sous-réseaux de tailles différentes selon les besoins de chaque segment. Par exemple, un réseau de postes utilisateurs peut avoir besoin de 100 adresses, tandis qu’un lien point à point entre deux routeurs n’en demande que deux.

Sans VLSM, l’administrateur pourrait être tenté d’attribuer de grands sous-réseaux identiques à tous les segments. Cette méthode peut gaspiller beaucoup d’adresses et rendre plus difficile la gestion d’un espace limité.

La méthode de base consiste à classer les besoins du plus grand au plus petit, choisir un préfixe qui fournit assez d’adresses, puis attribuer les blocs de manière alignée sans chevauchement.

Exemple de besoins :

| Segment | Besoin approximatif | Préfixe classique proposé | Hôtes utilisables |
|---|---:|---:|---:|
| LAN Administration | 50 postes | `/26` | 62 |
| LAN Support | 25 postes | `/27` | 30 |
| LAN Imprimantes | 10 appareils | `/28` | 14 |
| Lien routeur-routeur | 2 interfaces | `/30` | 2 |

Si le bloc de départ est `192.168.50.0/24`, un plan possible est :

```text
192.168.50.0/26     Administration : .0 à .63
192.168.50.64/27    Support        : .64 à .95
192.168.50.96/28   Imprimantes    : .96 à .111
192.168.50.112/30  Transit        : .112 à .115
```

Les plages sont contiguës, correctement alignées et ne se chevauchent pas. Les autres adresses du `/24` restent disponibles pour une croissance ou d’autres sous-réseaux. Dans une entreprise, le plan réel doit aussi intégrer les passerelles, les équipements de gestion, les réserves de croissance, les besoins de DHCP et les conventions documentaires.

### 1.15. Déterminer un préfixe à partir d’un nombre d’hôtes

Pour choisir le sous-réseau, il faut que le nombre d’adresses hôtes utilisables soit au moins égal au besoin. Dans le cas des réseaux classiques, cherche le plus petit nombre de bits hôte `h` satisfaisant :

\[
2^h - 2 \geq \text{nombre d'hôtes requis}
\]

Le préfixe est ensuite :

\[
p = 32 - h
\]

Exemple : 25 hôtes doivent être adressés. Avec 4 bits hôte, on obtient `2^4 - 2 = 14`, ce qui est insuffisant. Avec 5 bits, on obtient `2^5 - 2 = 30`, ce qui suffit. Il faut donc au moins 5 bits hôte, soit un préfixe `/27`.

Exemple : 100 hôtes. Sept bits donnent `128 - 2 = 126` hôtes, ce qui suffit ; six bits ne donnent que 62 hôtes. Le préfixe nécessaire est donc `/25`.

| Besoin d’hôtes | Bits hôte minimaux | Préfixe minimal adapté | Hôtes utilisables |
|---:|---:|---:|---:|
| 2 | 2 dans le cas classique | `/30` | 2 |
| 6 | 3 | `/29` | 6 |
| 12 | 4 | `/28` | 14 |
| 25 | 5 | `/27` | 30 |
| 50 | 6 | `/26` | 62 |
| 100 | 7 | `/25` | 126 |
| 200 | 8 | `/24` | 254 |
| 500 | 9 | `/23` | 510 |

Le tableau illustre la règle « moins deux » pour les sous-réseaux classiques. Les liens point à point IPv4 avec `/31` constituent une exception standardisée ; ils ne doivent pas être dimensionnés comme des LAN de postes.

### 1.16. Routage statique et route par défaut

Une route statique est une entrée ajoutée explicitement par l’administrateur dans la table de routage. Elle peut définir une destination, un préfixe et un prochain saut, ou une interface de sortie selon le type de réseau et la configuration.

Exemple Cisco IOS :

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.12.2
```

Cette commande indique au routeur qu’il doit acheminer le trafic vers `192.168.30.0/24` via le prochain saut `10.0.12.2`, sous réserve que ce prochain saut soit joignable et que la route soit installée.

Une route par défaut permet de définir un chemin de repli :

```cisco
ip route 0.0.0.0 0.0.0.0 10.0.12.2
```

Le préfixe `0.0.0.0/0` correspond à toutes les destinations IPv4 possibles, mais il est utilisé seulement lorsque la table ne contient pas de route plus spécifique applicable. Une route par défaut ne garantit pas que la destination sera atteinte : elle fournit un prochain saut à essayer.

Les routes statiques sont utiles dans des topologies petites ou stables, pour des routes spécifiques, ou comme route de secours lorsque la conception le justifie. Dans des réseaux plus grands, des protocoles dynamiques comme OSPF ou EIGRP facilitent l’adaptation aux changements. Quel que soit le mécanisme, l’adressage et les préfixes doivent être corrects.

### 1.17. Adresse IP et masque d’un poste

Un poste de travail IPv4 a généralement besoin de plusieurs paramètres :

- une adresse IPv4 locale unique dans son sous-réseau ;
- un masque ou préfixe cohérent ;
- une passerelle par défaut si des réseaux distants doivent être atteints ;
- un ou plusieurs serveurs DNS pour résoudre les noms, selon l’environnement.

Exemple de configuration conceptuelle :

```text
Adresse IPv4 : 192.168.1.25
Masque       : 255.255.255.0
Préfixe      : /24
Passerelle   : 192.168.1.1
DNS          : adresse du serveur DNS choisi par l'organisation
```

L’adresse de la passerelle appartient au même sous-réseau local : `192.168.1.1` se trouve dans `192.168.1.0/24`. Le poste peut donc résoudre l’adresse MAC de la passerelle et lui transmettre les paquets destinés à l’extérieur du sous-réseau.

Le DNS n’est pas un substitut au routage. Il traduit des noms tels que `intranet.example` en informations utiles, notamment des adresses IP, mais une résolution réussie ne prouve pas que le chemin IP fonctionne. Inversement, une adresse IP peut être joignable alors que le nom DNS ne se résout pas.

### 1.18. DHCP et configuration manuelle

Une adresse peut être configurée manuellement ou être attribuée dynamiquement au moyen de DHCP. En pratique, les postes utilisateurs reçoivent souvent leurs paramètres IPv4 par DHCP tandis que les équipements d’infrastructure utilisent des adresses fixes ou des réservations planifiées.

DHCP permet de distribuer notamment une adresse, un masque, une passerelle et des serveurs DNS. Le serveur doit disposer d’un pool correctement dimensionné et correspondant au sous-réseau concerné. Une configuration incorrecte du masque dans le pool peut empêcher les hôtes de joindre la passerelle ou de classifier correctement les destinations locales et distantes.

Le service DHCP ne remplace pas le plan d’adressage. L’administrateur doit déterminer les blocs utilisés, réserver les adresses des équipements d’infrastructure, éviter les plages concurrentes et documenter les exclusions. Plusieurs serveurs DHCP mal contrôlés sur un même LAN peuvent distribuer des paramètres contradictoires.

Quand un poste reçoit une adresse `169.254.x.x`, il s’agit souvent d’une adresse link-local autoattribuée sous Windows lorsque le poste ne reçoit pas de configuration DHCP utilisable. Ce symptôme invite à vérifier la connectivité, le VLAN, le service DHCP, le relais DHCP et le pool d’adresses. Il ne signifie pas automatiquement qu’une carte réseau est physiquement défectueuse.

### 1.19. Plan d’adressage et segmentation par VLAN

Un VLAN est une séparation logique de niveau 2. Dans une conception courante, chaque VLAN routé possède un sous-réseau IPv4 distinct et une interface de passerelle correspondante, soit sur un routeur, soit sur un commutateur de couche 3.

Exemple de plan simple :

| VLAN | Fonction | Sous-réseau | Passerelle possible |
|---:|---|---|---|
| 10 | Administration | `192.168.10.0/24` | `192.168.10.1` |
| 20 | Utilisateurs | `192.168.20.0/24` | `192.168.20.1` |
| 30 | Imprimantes | `192.168.30.0/24` | `192.168.30.1` |
| 40 | Invités | `192.168.40.0/24` | `192.168.40.1` |

Le fait d’utiliser un VLAN ne fournit pas à lui seul une sécurité complète entre groupes. Le routage inter-VLAN peut autoriser les communications entre sous-réseaux. Des listes de contrôle d’accès, des pare-feu et des politiques appropriées sont nécessaires pour définir les flux permis.

Il faut éviter d’utiliser le même sous-réseau IPv4 sur deux VLANs distincts routés comme s’ils représentaient un seul LAN, sauf cas particulier explicitement conçu. Si deux interfaces de routeur sont configurées dans des sous-réseaux qui se chevauchent, l’installation des routes et l’acheminement deviennent ambigus ou sont refusés par la plateforme.

### 1.20. Vérifier qu’il n’y a pas de chevauchement

Deux sous-réseaux se chevauchent lorsque certaines de leurs adresses appartiennent simultanément à leurs plages. Un plan peut paraître différent à la lecture des adresses tout en se chevauchant si les préfixes sont différents.

Exemple : `192.168.10.0/24` couvre `192.168.10.0` à `192.168.10.255`. Le réseau `192.168.10.128/25` se trouve intégralement à l’intérieur de ce `/24`. Les deux blocs se chevauchent, et ils ne peuvent pas être utilisés comme deux réseaux indépendants sur des interfaces de routage classiques sans architecture spécifique.

À l’inverse, `192.168.10.0/25` et `192.168.10.128/25` sont deux moitiés distinctes du `/24`, sans chevauchement :

```text
192.168.10.0/24
|-----------------------------------------------------|
192.168.10.0/25                 192.168.10.128/25
|---------------|                |-------------------|
0             127              128                  255
```

Avant d’attribuer un réseau, compare les bornes du bloc à ceux déjà utilisés. Dans les entreprises multisites, il faut également vérifier les plages des VPN, des réseaux cloud, des sites distants et des environnements de laboratoire. Un chevauchement entre deux réseaux privés devient particulièrement gênant lorsqu’il faut les interconnecter au travers d’un VPN.

### 1.21. Résumé des méthodes de calcul

Trois méthodes se complètent :

**Méthode binaire :** applique un AND entre l’adresse et le masque. Elle est fiable pour tous les préfixes, mais nécessite de convertir correctement les bits.

**Méthode du pas :** repère l’octet partiellement masqué, calcule `256 - masque`, puis recherche le multiple de pas qui contient la valeur de l’octet. Elle est rapide pour les exercices courants.

**Méthode du nombre de bits :** calcule les adresses hôtes possibles avec `2^h`, puis détermine le préfixe `32-h`. Elle est surtout utile pour dimensionner une plage à partir d’un besoin en équipements.

Le choix de méthode dépend de la question. Pour déterminer l’adresse réseau d’une IP existante, le AND ou le pas sont pratiques. Pour choisir un préfixe pour 70 hôtes, la méthode du nombre de bits est plus directe. Dans les cas réels, un calculateur de sous-réseau peut servir à vérifier le résultat, mais il faut être capable d’expliquer les étapes et de détecter une saisie erronée.

---

## 2. Configuration et Pratique

### 2.1. Topologie de laboratoire Cisco

Le laboratoire suivant met en place deux LANs séparés par deux routeurs. Il sert à pratiquer l’adressage des interfaces, le routage statique et la vérification de connectivité.

```text
 PC-A                                                   PC-B
192.168.10.10/24                                    192.168.20.10/24
GW 192.168.10.1                                      GW 192.168.20.1
     |                                                      |
     |                                                      |
+------------+      10.0.12.0/30      +------------+        |
|    R1      |------------------------|    R2      |--------+
| G0/0 .10.1 |        .12.2 / .12.1   | G0/0 .20.1 |
+------------+                        +------------+

Plan exact :
R1 G0/0 : 192.168.10.1/24
R1 G0/1 : 10.0.12.1/30
R2 G0/1 : 10.0.12.2/30
R2 G0/0 : 192.168.20.1/24
```

Le nom des interfaces peut changer selon la plateforme. L’objectif est d’utiliser une interface LAN sur chaque routeur et un lien de transit entre eux. Les adresses des postes doivent se situer dans les plages associées à leurs passerelles respectives.

### 2.2. Configuration de R1 sous Cisco IOS

```cisco
hostname R1

interface GigabitEthernet0/0
 description LAN_ADMINISTRATION
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface GigabitEthernet0/1
 description TRANSIT_VERS_R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown

ip route 192.168.20.0 255.255.255.0 10.0.12.2
```

La commande `hostname` attribue un nom au routeur. Sur chaque interface, `description` ajoute un commentaire administratif qui facilite la lecture de la configuration. `ip address` associe une adresse IPv4 et un masque. `no shutdown` active l’interface lorsqu’elle était administrativement désactivée.

La route statique indique que le LAN de R2, `192.168.20.0/24`, est accessible via `10.0.12.2`. Le prochain saut doit se trouver dans un réseau directement joignable depuis R1 ; ici, `10.0.12.2` est dans `10.0.12.0/30`, auquel appartient l’interface de transit de R1.

Le réseau directement connecté `192.168.10.0/24` est normalement présent dans la table de routage de R1 lorsque son interface LAN est opérationnelle. Il n’est pas nécessaire d’ajouter une route statique vers ce réseau local.

### 2.3. Configuration de R2

```cisco
hostname R2

interface GigabitEthernet0/0
 description LAN_UTILISATEURS
 ip address 192.168.20.1 255.255.255.0
 no shutdown

interface GigabitEthernet0/1
 description TRANSIT_VERS_R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown

ip route 192.168.10.0 255.255.255.0 10.0.12.1
```

R2 a besoin d’une route de retour vers `192.168.10.0/24`. Sans cette route, R2 pourrait recevoir un paquet de PC-A mais ne saurait pas nécessairement acheminer la réponse à sa destination. Le routage IP nécessite que les chemins aller et retour soient cohérents.

Cette configuration suppose que les interfaces sont reliées à la bonne topologie et que les adresses ne sont pas déjà utilisées sur le réseau. Dans un laboratoire Packet Tracer, vérifie le type de câble ou le lien simulé, les ports employés et l’état des interfaces.

### 2.4. Configurer les postes

Sur PC-A :

```text
Adresse IPv4 : 192.168.10.10
Masque       : 255.255.255.0
Passerelle   : 192.168.10.1
DNS          : facultatif pour un test par adresse IP
```

Sur PC-B :

```text
Adresse IPv4 : 192.168.20.10
Masque       : 255.255.255.0
Passerelle   : 192.168.20.1
DNS          : facultatif pour un test par adresse IP
```

Les deux postes appartiennent à des sous-réseaux différents. Pour communiquer entre eux, ils doivent envoyer les paquets à leurs passerelles. Les routeurs doivent avoir les routes nécessaires vers les sous-réseaux opposés.

### 2.5. Vérifier l’état des interfaces et les adresses

Sur Cisco IOS :

```cisco
show ip interface brief
show interfaces GigabitEthernet0/0
show running-config
```

`show ip interface brief` affiche un résumé des interfaces et de leur état. `show interfaces` fournit davantage d’informations sur une interface sélectionnée. `show running-config` permet de vérifier les adresses et les routes configurées.

Les interfaces nécessaires doivent être opérationnelles. Si l’interface est indiquée `administratively down`, vérifie la présence de `no shutdown`. Si elle est down pour une autre raison, examine le lien physique, le port de commutation, le module ou la configuration de la plateforme.

Une adresse correcte sur une interface ne garantit pas la connectivité à travers tout le réseau. Il faut ensuite vérifier les routes et réaliser des tests de bout en bout.

### 2.6. Vérifier la table de routage

```cisco
show ip route
show ip route static
```

La première commande affiche la table de routage complète. La seconde, lorsqu’elle est disponible sur la plateforme, permet de filtrer les routes statiques. Les routes connectées sont généralement indiquées par `C` et les routes locales de l’interface par `L` sur Cisco IOS moderne. Les routes statiques apparaissent habituellement avec le code `S`.

Sur R1, la table devrait contenir :

- une route connectée vers `192.168.10.0/24` si l’interface LAN est opérationnelle ;
- une route connectée vers `10.0.12.0/30` si l’interface de transit est opérationnelle ;
- une route statique vers `192.168.20.0/24` via `10.0.12.2`.

Sur R2, l’équivalent doit exister pour le réseau de PC-A. Si une route statique n’apparaît pas, vérifie la syntaxe, la joignabilité du prochain saut et la disponibilité d’une route permettant de résoudre ce prochain saut selon les règles de la plateforme.

### 2.7. Tester la connectivité

Depuis R1, teste d’abord le prochain saut :

```cisco
ping 10.0.12.2
```

Puis teste l’adresse de PC-B :

```cisco
ping 192.168.20.10
```

Depuis PC-A, teste la passerelle locale :

```text
ping 192.168.10.1
```

Ensuite, teste PC-B :

```text
ping 192.168.20.10
```

Si le test vers la passerelle locale échoue, ne commence pas par modifier la route distante. Vérifie l’adressage de PC-A, le VLAN ou le segment de couche 2, le lien du poste et l’interface LAN du routeur. Si la passerelle fonctionne, mais que le réseau distant ne répond pas, examine le routage entre R1 et R2 puis le chemin retour.

Certains hôtes peuvent filtrer ICMP. Un ping en échec doit être interprété en fonction de la politique de sécurité et des autres tests disponibles. Dans un laboratoire contrôlé, les réponses ICMP constituent cependant un moyen simple d’observer les étapes de connectivité.

### 2.8. Exemple de découpage en quatre sous-réseaux

On demande de diviser `192.168.40.0/24` en quatre sous-réseaux de même taille. Deux bits doivent être empruntés à la partie hôte, car `2^2 = 4`. Le nouveau préfixe est `/26`.

Chaque bloc `/26` contient 64 adresses, dont 62 utilisables dans le cas classique.

| Sous-réseau | Réseau | Première adresse hôte | Dernière adresse hôte | Diffusion |
|---:|---|---|---|---|
| 1 | `192.168.40.0/26` | `192.168.40.1` | `192.168.40.62` | `192.168.40.63` |
| 2 | `192.168.40.64/26` | `192.168.40.65` | `192.168.40.126` | `192.168.40.127` |
| 3 | `192.168.40.128/26` | `192.168.40.129` | `192.168.40.190` | `192.168.40.191` |
| 4 | `192.168.40.192/26` | `192.168.40.193` | `192.168.40.254` | `192.168.40.255` |

La première adresse de chaque bloc représente le réseau et la dernière représente la diffusion. Les adresses hôtes sont comprises entre les deux, en excluant ces limites. Le quatrième bloc se termine par `.255`, mais les trois autres sous-réseaux montrent pourquoi il est incorrect de supposer que chaque diffusion IPv4 finit par `.255`.

### 2.9. Configurer un réseau local sur un commutateur de couche 3

Sur un commutateur de couche 3 Cisco IOS, une interface VLAN (*Switched Virtual Interface*, SVI) peut jouer le rôle de passerelle pour les postes d’un VLAN. Le détail dépend du modèle et de la licence logicielle, mais un exemple classique est :

```cisco
vlan 10
 name ADMINISTRATION

interface Vlan10
 description PASSERELLE_ADMINISTRATION
 ip address 192.168.10.1 255.255.255.0
 no shutdown

ip routing
```

La commande `vlan 10` crée le VLAN sur les plateformes qui utilisent cette syntaxe. L’interface `Vlan10` fournit une interface logique de couche 3 avec une adresse IPv4. La commande `ip routing` active le routage IPv4 sur les commutateurs de couche 3 qui en ont besoin.

Cette configuration doit être complétée par l’affectation des ports d’accès au VLAN 10 et, le cas échéant, par la configuration des trunks. Si l’interface VLAN reste down, vérifie l’état du VLAN et des ports membres selon les règles de la plateforme. Une SVI n’est pas toujours opérationnelle simplement parce que l’adresse IP est configurée.

### 2.10. Configuration DHCP simple sur Cisco IOS

Un routeur peut fournir le service DHCP à un LAN dans un petit laboratoire, si la plateforme prend en charge cette fonction. Exemple :

```cisco
ip dhcp excluded-address 192.168.10.1 192.168.10.20

ip dhcp pool LAN_ADMIN
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 1.1.1.1 8.8.8.8
```

La commande d’exclusion réserve des adresses, notamment pour la passerelle et les équipements configurés manuellement. Le pool définit le réseau desservi, la passerelle par défaut et les serveurs DNS proposés aux clients. Les adresses DNS de l’exemple sont des serveurs publics ; dans une entreprise, il est préférable d’utiliser les serveurs DNS approuvés par l’organisation.

Après la configuration, vérifie les baux et les paramètres du pool avec les commandes DHCP appropriées à la plateforme, par exemple `show ip dhcp binding` et `show ip dhcp pool`. Il faut veiller à ce que le pool corresponde exactement au sous-réseau et ne distribue pas les adresses de la passerelle ou d’autres équipements statiques.

### 2.11. Routeur, réseau connecté et routage dynamique

Lorsqu’une interface d’un routeur possède une adresse valide et est opérationnelle, le routeur connaît normalement le réseau auquel cette interface est directement connectée. Il peut donc acheminer les paquets vers ce réseau sans route statique supplémentaire.

Pour joindre un sous-réseau non directement connecté, une route doit exister. Cette route peut être statique, reçue d’un protocole de routage, ou correspondre à la route par défaut.

Dans une petite topologie, les routes statiques sont faciles à comprendre. Dans une architecture plus importante, elles demandent une mise à jour manuelle lorsque la topologie évolue. Les protocoles dynamiques diffusent ou échangent des informations de routage et peuvent recalculer les chemins lors de changements.

Quelle que soit la méthode de routage, un préfixe trop large ou erroné peut influencer la sélection du chemin. Il est donc essentiel de vérifier l’adresse réseau, le masque et la plage hôte avant de mettre en place les routes.

> **Astuce :** Pour diagnostiquer un problème IPv4, procède de proche en proche : vérifie d’abord l’adresse, le masque et la passerelle du poste ; teste la passerelle locale ; examine ensuite `show ip interface brief`, `show ip route` et le ping vers le prochain saut sur le routeur. Cette méthode évite de modifier la table de routage alors que l’erreur peut venir d’un masque incorrect ou d’un mauvais VLAN.

---

## 3. Dépannage et Sécurité

### 3.1. Mauvais masque de sous-réseau

Un masque incorrect est l’une des erreurs d’adressage les plus fréquentes. Un poste peut avoir une adresse qui semble correcte mais considérer à tort une destination comme locale ou distante.

Supposons que deux postes soient prévus dans `192.168.10.0/24`. Le premier est configuré `192.168.10.10/24`, tandis que le second est configuré `192.168.10.200/25`. Avec le premier masque, les deux adresses se trouvent dans `192.168.10.0/24`. Avec le deuxième masque, `192.168.10.200` appartient à `192.168.10.128/25`. Le deuxième poste peut donc tenter d’envoyer certains paquets à sa passerelle au lieu de les transmettre directement, ce qui produit des comportements inattendus si les passerelles et routes ne sont pas prévues pour cette segmentation.

La méthode de dépannage consiste à relever l’adresse IP, le masque et la passerelle des deux extrémités. Ne compare pas seulement les adresses visibles : vérifie le préfixe associé à chaque interface et calcule le sous-réseau.

Sous Windows, `ipconfig /all` affiche les paramètres d’interface. Sur Cisco IOS, `show ip interface brief` donne une vue courte et `show running-config` permet de vérifier les configurations. Les commandes précises de consultation des paramètres IP varient selon le système d’exploitation.

### 3.2. Adresse IP en double

Deux interfaces qui utilisent la même adresse IPv4 dans le même domaine réseau peuvent provoquer un conflit. Les symptômes peuvent inclure une connectivité intermittente, des réponses qui semblent provenir de plusieurs appareils ou des changements d’association entre une adresse IP et une adresse MAC dans les caches ARP.

Pour résoudre le conflit :

1. Vérifie l’inventaire des adresses attribuées manuellement et des réservations DHCP.
2. Contrôle le bail DHCP et les exclusions du pool.
3. Identifie les équipements utilisant l’adresse en conflit à l’aide des outils disponibles dans l’environnement.
4. Attribue une adresse unique conforme au plan d’adressage.
5. Contrôle de nouveau la connectivité et les entrées ARP après correction.

Une adresse attribuée manuellement à l’intérieur de la plage DHCP peut entrer en conflit avec une adresse distribuée à un client. Les plages d’adresses statiques, les réservations et les pools DHCP doivent être documentés et coordonnés.

### 3.3. Mauvaise passerelle par défaut

La passerelle par défaut est le routeur auquel un hôte transmet les paquets destinés aux réseaux hors de son préfixe local. Si la passerelle est incorrecte, le poste peut communiquer avec certains hôtes locaux tout en échouant vers les réseaux distants.

Exemple d’erreur : le poste `192.168.10.25/24` est configuré avec la passerelle `192.168.20.1`. Cette adresse ne se trouve pas dans son sous-réseau local `192.168.10.0/24`. Dans une configuration standard, le poste ne peut pas résoudre directement cette passerelle par ARP sur son LAN.

La passerelle doit normalement être une adresse de routeur située dans le sous-réseau de l’interface hôte. Le dépannage consiste à vérifier le masque, la passerelle configurée et l’adresse réelle de l’interface routeur ou SVI.

### 3.4. Route de retour absente

Lorsque le trafic quitte un réseau, le routeur de destination ou l’hôte distant doit disposer d’une route permettant de renvoyer la réponse. Une route aller correcte ne suffit donc pas nécessairement à assurer une session complète.

Dans l’exemple de deux routeurs, R1 peut posséder une route vers `192.168.20.0/24`, mais si R2 ne dispose pas de route vers `192.168.10.0/24`, les réponses de PC-B peuvent être perdues. Il faut examiner la table de routage des deux côtés et vérifier les passerelles configurées sur les postes.

Un test de ping peut être perturbé par un filtrage ICMP. Pour déterminer la cause réelle, utilise plusieurs observations : tables de routage, interfaces, traçage, journaux et tests de services si cela est autorisé.

### 3.5. Réseau qui se chevauche

Un chevauchement apparaît lorsqu’un préfixe est inclus dans un autre bloc qui est déjà utilisé comme réseau indépendant. Par exemple, `10.1.0.0/16` englobe toutes les adresses de `10.1.20.0/24`. Si ces deux blocs sont attribués à des domaines de couche 3 distincts sans architecture adaptée, le routage devient ambigu et certains équipements peuvent refuser la configuration.

Les chevauchements sont fréquents lors de la connexion de deux organisations, de la mise en place d’un VPN ou de l’intégration de réseaux cloud dont les plages privées ont été choisies indépendamment.

Pour les éviter, maintiens un registre centralisé des préfixes utilisés, réserve des blocs par site et par fonction, et vérifie les plages avant toute nouvelle attribution. Si deux réseaux existent déjà avec des plages qui se chevauchent, une renumérotation est souvent la solution à long terme la plus propre ; des mécanismes de traduction peuvent parfois être utilisés temporairement, au prix d’une complexité accrue.

### 3.6. Panne DHCP et adresse 169.254.x.x

Si un poste qui devrait recevoir une adresse par DHCP affiche une adresse de la plage `169.254.0.0/16`, il n’a probablement pas obtenu les paramètres attendus. Les causes possibles comprennent un serveur DHCP indisponible, un pool épuisé, un port dans le mauvais VLAN, un trunk mal configuré, un relais DHCP absent ou des règles de sécurité qui bloquent les échanges.

Le diagnostic doit vérifier la couche de liaison, le VLAN, la présence d’un serveur DHCP, l’état du pool et le relais si le serveur se trouve dans un autre réseau. Une adresse link-local peut permettre certains échanges sur le segment local, mais elle ne remplace pas un adressage d’entreprise prévu pour le routage général.

Il est incorrect de supposer que le poste doit simplement être configuré manuellement pour contourner le problème. Cette action peut masquer la cause réelle et créer ultérieurement un conflit d’adresses.

### 3.7. Pourquoi le ping peut échouer

Un ping en échec n’indique pas à lui seul quelle couche est fautive. Parmi les causes possibles :

- interface désactivée ou mauvais câblage ;
- VLAN incorrect ;
- adresse ou masque erroné ;
- passerelle manquante ;
- route absente ou prochain saut inaccessible ;
- filtrage ICMP ;
- route de retour absente ;
- conflit d’adresse ;
- problème de MTU dans certains scénarios ;
- hôte distant hors service.

La démarche consiste à tester les points connus dans l’ordre : adresse locale, boucle locale (`127.0.0.1`), adresse de l’interface locale si approprié, passerelle, prochain saut et destination distante. L’ordre exact dépend du type de panne, mais chaque test doit vérifier une hypothèse précise.

### 3.8. Risques de sécurité liés à l’adressage

L’adressage IPv4 n’est pas à lui seul un mécanisme d’authentification. Une adresse privée ne rend pas un équipement sûr, et une adresse publique ne signifie pas automatiquement qu’un service est accessible. Les règles de filtrage, la configuration des interfaces, les routes, les pare-feu et les mécanismes de sécurité du réseau déterminent les flux réels.

Des erreurs d’adressage peuvent exposer des services sur un segment inattendu. Une route trop large peut envoyer le trafic vers une destination non prévue. Un pool DHCP mal géré peut permettre à un équipement de recevoir des paramètres incohérents ou de causer un conflit. Les réseaux d’administration, d’utilisateurs, d’invités et d’équipements doivent être séparés lorsque la politique de sécurité le demande.

Les plages privées RFC 1918 doivent être utilisées dans les réseaux internes conformément au plan d’adressage. Elles ne garantissent pas l’isolation : des machines d’un même réseau privé peuvent communiquer si les contrôles de couche 2 et de couche 3 l’autorisent.

> **Danger :** Un plan d’adressage incohérent peut provoquer une panne qui semble intermittente, détourner le trafic ou exposer un réseau à une zone qui ne devait pas être joignable. Un chevauchement entre un réseau local et un réseau distant, en particulier dans un VPN, peut envoyer les paquets vers le mauvais côté sans que les applications indiquent clairement la cause. Avant d’activer un nouveau VLAN, un VPN ou un site, valide les préfixes, les routes, les passerelles et les règles de filtrage ; documente les réservations DHCP et garde une possibilité de retour arrière.

### 3.9. Bonnes pratiques d’un plan IPv4 professionnel

Un plan d’adressage doit être documenté avant la configuration des équipements. Pour chaque sous-réseau, conserve au minimum :

- le préfixe et le masque ;
- la fonction et le site d’utilisation ;
- la passerelle ;
- les plages réservées aux équipements statiques ;
- la plage DHCP ;
- les adresses réservées et exclusions ;
- les liens de transit éventuels ;
- les dépendances de routage, de VPN et de filtrage.

Utilise des blocs agrégables lorsque cela correspond à la topologie. Attribue des plages distinctes aux sites et aux fonctions. Évite les choix ponctuels qui rendent la croissance difficile. Prévois une réserve raisonnable, mais ne gaspille pas systématiquement de grands blocs lorsqu’un petit sous-réseau suffit.

Dans un réseau multisite, définis une convention de nommage et des plages cohérentes. Le plan doit être compris par les personnes chargées de l’exploitation et du dépannage, pas seulement par son auteur initial.

### 3.10. Procédure de dépannage de base

Lorsqu’un utilisateur signale qu’il n’a pas accès à un réseau distant, recueille d’abord les paramètres IP et le contexte : appareil, VLAN, emplacement, heure de début du problème et destination concernée.

Ensuite :

1. Vérifie l’adresse, le masque et la passerelle du poste.
2. Vérifie que l’adresse appartient au sous-réseau prévu et qu’elle n’est pas en conflit.
3. Teste la connectivité avec la passerelle locale.
4. Vérifie les interfaces et le VLAN de raccordement.
5. Examine la table de routage du routeur ou du commutateur de couche 3.
6. Vérifie le chemin aller et le chemin retour.
7. Examine les filtres, les ACL, les politiques de pare-feu et les journaux.
8. Corrige une cause à la fois, puis répète les tests.
9. Documente la modification et le résultat.

Cette méthode réduit les changements hasardeux. Elle aide aussi à comprendre si le problème est lié à la configuration IP du terminal, à la commutation, au routage, à la résolution de noms ou à la politique de sécurité.

### 3.11. Exercices résolus

**Exercice 1 :** `192.168.1.54/24`.

- Masque : `255.255.255.0`.
- Réseau : `192.168.1.0`.
- Diffusion : `192.168.1.255`.
- Plage hôte : `192.168.1.1` à `192.168.1.254`.
- Nombre d’hôtes utilisables : 254.

**Exercice 2 :** `192.168.1.150/26`.

- Masque : `255.255.255.192`.
- Pas : `256 - 192 = 64`.
- Le dernier octet 150 se situe dans le bloc 128–191.
- Réseau : `192.168.1.128`.
- Diffusion : `192.168.1.191`.
- Plage hôte : `192.168.1.129` à `192.168.1.190`.
- Nombre d’hôtes utilisables : 62.

**Exercice 3 :** besoin de 12 hôtes.

- Quatre bits hôte donnent 16 adresses totales, dont 14 utilisables.
- Le préfixe est `32 - 4 = /28`.
- Un `/28` est suffisant pour 12 hôtes.

**Exercice 4 :** `172.20.90.10/20`.

- Masque : `255.255.240.0`.
- Pas du troisième octet : `256 - 240 = 16`.
- Le troisième octet 90 appartient au bloc 80–95.
- Réseau : `172.20.80.0/20`.
- Diffusion : `172.20.95.255`.
- Hôtes utilisables : `172.20.80.1` à `172.20.95.254`.

**Exercice 5 :** déterminer si `192.168.50.65/26` et `192.168.50.100/26` appartiennent au même sous-réseau.

- Les blocs `/26` sont 0–63, 64–127, 128–191 et 192–255.
- Les deux adresses se trouvent dans le bloc 64–127.
- Elles appartiennent donc à `192.168.50.64/26`.

### 3.12. Exercices d’application

Résous les exercices suivants avant de consulter les réponses. Pour chacun, identifie le masque, le réseau, la diffusion, le premier hôte, le dernier hôte et le nombre d’adresses hôtes utilisables quand la formule classique s’applique.

1. `10.20.30.40/24`
2. `192.168.12.130/25`
3. `192.168.12.190/27`
4. `172.16.70.35/20`
5. `10.10.10.10/30`
6. Quel préfixe classique choisir pour au moins 55 hôtes ?
7. Combien d’adresses au total sont contenues dans un `/23` ? Combien sont utilisables dans le cas classique ?
8. Les adresses `192.168.4.10/25` et `192.168.4.150/25` appartiennent-elles au même sous-réseau ?
9. Le préfixe `192.168.8.0/24` chevauche-t-il `192.168.8.128/25` ? Explique pourquoi.
10. Un poste `192.168.30.20/24` possède comme passerelle `192.168.31.1`. Quel est le problème probable ?

#### Réponses

1. Réseau `10.20.30.0/24`, diffusion `10.20.30.255`, hôtes `.1` à `.254`, 254 hôtes utilisables.
2. `/25` utilise le masque `255.255.255.128`. Le pas vaut 128. Le dernier octet 130 se trouve dans le bloc 128–255 ; réseau `192.168.12.128`, diffusion `192.168.12.255`, hôtes `.129` à `.254`, 126 hôtes.
3. `/27` utilise le masque `255.255.255.224`. Le pas vaut 32. Le dernier octet 190 se situe dans le bloc 160–191 ; réseau `192.168.12.160`, diffusion `192.168.12.191`, hôtes `.161` à `.190`, 30 hôtes.
4. `/20` utilise `255.255.240.0`. Le troisième octet 70 appartient au bloc 64–79 ; réseau `172.16.64.0`, diffusion `172.16.79.255`, hôtes `172.16.64.1` à `172.16.79.254`.
5. `/30` utilise `255.255.255.252`, pas 4. Le dernier octet 10 se situe dans le bloc 8–11 ; réseau `10.10.10.8`, diffusion `10.10.10.11`, hôtes `.9` et `.10`.
6. Un `/26` offre 62 adresses hôtes classiques, donc il est adapté à 55 hôtes.
7. Un `/23` a 9 bits hôte : `2^9 = 512` adresses totales et 510 utilisables dans le cas classique.
8. Non. La première appartient à `192.168.4.0/25` et la deuxième à `192.168.4.128/25`.
9. Oui. Le `/25` `192.168.8.128/25` fait partie du bloc plus vaste `192.168.8.0/24` ; les deux préfixes se chevauchent.
10. La passerelle appartient à `192.168.31.0/24`, alors que le poste se trouve dans `192.168.30.0/24`. Dans une configuration standard, la passerelle n’est pas directement joignable sur le LAN du poste ; il faut corriger le paramètre ou revoir la conception.

### 3.13. Liste de contrôle avant mise en production

Avant de mettre en service un nouveau sous-réseau, confirme les éléments suivants :

- Le préfixe n’est pas déjà utilisé ailleurs dans l’entreprise, les VPN ou le cloud.
- L’adresse réseau et la diffusion ont été calculées correctement.
- Le nombre d’adresses utilisables répond au besoin actuel et à la croissance prévue.
- La passerelle est définie et appartient au sous-réseau.
- Les adresses statiques et la plage DHCP ne se chevauchent pas.
- Le VLAN et les ports de commutation sont correctement configurés.
- Les routes nécessaires existent dans les deux sens.
- Les ACL et les politiques de sécurité sont cohérentes avec les flux autorisés.
- Les équipements de supervision et de documentation ont été mis à jour.
- Un plan de retour arrière est disponible pour les changements sensibles.

Une vérification documentée avant le déploiement coûte moins cher qu’un dépannage d’urgence dans un réseau en production. L’adressage n’est pas seulement une opération de saisie : il constitue une décision d’architecture qui détermine l’organisation des routes et les frontières logiques du réseau.

## Points à retenir

- **IPv4 utilise 32 bits.** Le masque ou préfixe sépare la partie réseau de la partie hôte ; la notation CIDR `/p` indique le nombre de bits réseau.
- **Pour les sous-réseaux classiques, le nombre d’adresses hôtes utilisables est généralement `2^(32-p) - 2`.** Les `/31` pour les liens point à point et les `/32` pour une adresse unique sont des exceptions importantes.
- **Le sous-réseautage repose sur le calcul binaire et l’alignement des blocs.** L’opération AND donne l’adresse réseau, le pas permet de trouver rapidement les limites d’un bloc, et la diffusion correspond à la fin de la plage dans le cas classique.
- **Un bon plan d’adressage évite les chevauchements et facilite l’exploitation.** Il distingue les LANs, les liens de transit, les plages DHCP, les adresses statiques et les passerelles.
- **La connectivité dépend du chemin aller et du chemin retour.** Une adresse correcte ne suffit pas si le masque, la passerelle ou les routes sont erronés.
- **Les plages privées RFC 1918 ne sont pas un mécanisme de sécurité.** Il faut compléter l’adressage par une segmentation adaptée, des ACL ou des pare-feu, ainsi qu’une gestion rigoureuse des annonces et des configurations.

## Références techniques

- RFC 791 — *Internet Protocol*: https://www.rfc-editor.org/rfc/rfc791
- RFC 1918 — *Address Allocation for Private Internets*: https://www.rfc-editor.org/rfc/rfc1918
- RFC 4632 — *Classless Inter-domain Routing (CIDR): The Internet Address Assignment and Aggregation Plan*: https://www.rfc-editor.org/rfc/rfc4632
- RFC 3021 — *Using 31-Bit Prefixes on IPv4 Point-to-Point Links*: https://www.rfc-editor.org/rfc/rfc3021
- RFC 5737 — *IPv4 Address Blocks Reserved for Documentation*: https://www.rfc-editor.org/rfc/rfc5737
- IANA — *IPv4 Special-Purpose Address Registry*: https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml