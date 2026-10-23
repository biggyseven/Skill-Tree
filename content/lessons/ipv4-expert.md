---
node_id: ipv4-expert
title: Adressage IPv4 & sous-réseaux - Expert
---

# Adressage IPv4 & sous-réseaux - Expert

**Niveau :** Expert

L’adressage IPv4 est l’un des fondements historiques de l’architecture Internet. Défini initialement par la spécification IP publiée dans la RFC 791 en 1981, IPv4 utilise des adresses de 32 bits pour identifier les interfaces logiques et acheminer les datagrammes entre réseaux. Ce mécanisme a rendu possible l’interconnexion de technologies de liaison différentes au sein d’un système de communication commun. Au fil de la croissance d’Internet, le modèle initial de classes d’adresses s’est révélé trop rigide : les organisations obtenaient parfois des blocs disproportionnés par rapport à leurs besoins, alors que les tables de routage et les ressources d’adressage devenaient de plus en plus difficiles à gérer.

La transition vers le routage sans classe, ou CIDR (*Classless Inter-Domain Routing*), a changé la façon de représenter les réseaux IPv4. Au lieu d’inférer un masque à partir de classes historiques A, B ou C, le préfixe est explicitement indiqué par une longueur, par exemple `/20` ou `/27`. Cette représentation autorise un découpage plus précis, l’allocation de blocs de taille variable, l’agrégation des routes et une utilisation plus efficace de l’espace d’adressage. Le calcul des sous-réseaux ne se limite donc pas à une opération binaire scolaire : il influence directement la taille des domaines de diffusion, la capacité des tables de routage, les politiques de sécurité et la conception de la haute disponibilité.

Dans une architecture d’entreprise moderne, l’adressage IPv4 doit être cohérent à plusieurs niveaux : organisation des sites, segmentation par fonction, allocation des VLAN, liens point à point, réseaux de gestion, zones de sécurité, services partagés et interconnexion avec des opérateurs. Un plan d’adressage bien conçu facilite la synthèse des routes et rend les politiques de filtrage compréhensibles. À l’inverse, les chevauchements, les blocs trop fragmentés, les masques incohérents ou les résumés incorrects peuvent provoquer des pertes de connectivité difficiles à diagnostiquer. Les mécanismes de DHCP, de NAT, de routage statique et dynamique reposent tous sur une interprétation cohérente des préfixes.

IPv4 reste largement exploité malgré la disponibilité d’IPv6. Son fonctionnement doit être compris dans le détail, y compris les espaces privés, les adresses spéciales, le TTL, la fragmentation, le MTU, les mécanismes de résolution de voisinage et la sélection des routes. Au niveau expert, l’objectif n’est pas seulement de calculer une plage d’hôtes, mais de construire un plan robuste, d’anticiper son évolution, de comprendre les effets d’une décision d’adressage sur le routage et la sécurité, puis de diagnostiquer méthodiquement les cas où la réalité du réseau diverge de la conception.

> **Analogie** : Imagine que l’espace IPv4 soit un territoire national dont les adresses sont des numéros d’emplacement. Le préfixe représente une frontière administrative : un bloc `/16` correspond à un vaste district, tandis qu’un bloc `/27` constitue un secteur beaucoup plus petit. Les bits du préfixe définissent la frontière commune ; les bits restants identifient les emplacements à l’intérieur de ce territoire.
>
> Dans une organisation, une adresse IP est comparable à une adresse postale complète. La partie réseau indique dans quel quartier chercher le destinataire, et la partie hôte indique l’emplacement précis dans ce quartier. Un routeur agit comme un centre de tri : il compare l’adresse de destination aux préfixes qu’il connaît et choisit la destination la plus précise dont le territoire contient l’adresse. Si le centre connaît une route pour `10.20.0.0/16` et une route plus spécifique pour `10.20.30.0/24`, les destinations de `10.20.30.0/24` suivent la route `/24`, car elle décrit un territoire plus petit et plus précis.
>
> Le subnetting consiste à subdiviser un district en quartiers plus petits sans changer le nombre total de bits de l’adresse. Le VLSM ressemble à une planification urbaine dans laquelle les quartiers n’ont pas tous la même taille : une salle de réunion de deux routeurs nécessite très peu d’adresses, alors qu’un campus avec plusieurs centaines d’équipements nécessite un bloc nettement plus vaste. L’agrégation CIDR revient à décrire plusieurs quartiers contigus par une seule frontière plus large dans les registres des centres de tri. Cette synthèse n’est correcte que si tous les quartiers inclus sont réellement cohérents avec le domaine résumé.
>
> Enfin, une route incorrecte ressemble à une consigne de réexpédition erronée dans un centre postal. Même si l’adresse du destinataire est valide, un résumé trop large ou une route plus spécifique incorrecte peut envoyer le courrier dans la mauvaise direction. La qualité d’un plan d’adressage dépend donc autant de l’arithmétique binaire que de la cohérence des frontières, des itinéraires, des règles d’exploitation et des contrôles de sécurité.

---

## 1. La théorie et les algorithmes

### 1.1. Représentation d’une adresse IPv4

IPv4 définit une adresse sur 32 bits, généralement représentée sous la forme de quatre octets en notation décimale pointée. Chaque octet représente huit bits et peut prendre une valeur comprise entre 0 et 255.

Exemple :

```text
Adresse décimale :  192.168.34.77
Octets :            192       168       34        77
Binaire :           11000000  10101000  00100010  01001101
Bits :              8         8         8         8
Total :             32 bits
```

La représentation décimale facilite la lecture, mais les calculs de sous-réseaux se font fondamentalement sur les bits. Chaque adresse est interprétée par rapport à un préfixe. Sans masque ou longueur de préfixe, une adresse telle que `192.168.34.77` ne suffit pas à déterminer quel est son réseau : elle peut appartenir à `192.168.34.0/24`, `192.168.32.0/20`, ou à une plage différente selon le plan d’adressage.

Les catégories historiques « classe A », « classe B » et « classe C » ne doivent plus guider la conception moderne. Elles expliquent l’évolution d’IPv4, mais CIDR et les préfixes explicites constituent la règle pratique pour le calcul et le routage actuels.

### 1.2. Masque de sous-réseau et longueur de préfixe

Un masque IPv4 indique quels bits appartiennent au préfixe réseau. Dans un masque valide, les bits à 1 sont contigus en partant du bit de poids fort, puis les bits à 0 représentent la partie hôte.

| Préfixe | Masque décimal | Bits hôte | Nombre total d’adresses |
|---|---|---:|---:|
| /8 | 255.0.0.0 | 24 | 16 777 216 |
| /16 | 255.255.0.0 | 16 | 65 536 |
| /20 | 255.255.240.0 | 12 | 4 096 |
| /24 | 255.255.255.0 | 8 | 256 |
| /25 | 255.255.255.128 | 7 | 128 |
| /26 | 255.255.255.192 | 6 | 64 |
| /27 | 255.255.255.224 | 5 | 32 |
| /28 | 255.255.255.240 | 4 | 16 |
| /29 | 255.255.255.248 | 3 | 8 |
| /30 | 255.255.255.252 | 2 | 4 |
| /31 | 255.255.255.254 | 1 | 2 |
| /32 | 255.255.255.255 | 0 | 1 |

La relation entre longueur de préfixe `p` et nombre de bits hôte `h` est :

\[
h = 32 - p
\]

Le nombre total d’adresses dans un bloc est :

\[
N = 2^{32-p}
\]

Pour un sous-réseau IPv4 LAN classique, on réserve historiquement l’adresse avec tous les bits hôte à 0 pour identifier le réseau et celle dont tous les bits hôte sont à 1 pour la diffusion dirigée. Ainsi, le nombre d’adresses d’hôtes habituellement attribuables est :

\[
H = 2^{32-p} - 2
\]

Cette formule générale ne s’applique pas telle quelle à tous les préfixes. Un `/31` est utilisé sur les liens point à point conformément à la RFC 3021 : les deux adresses sont utilisables comme adresses d’extrémité dans ce contexte. Un `/32` représente une route ou une adresse d’hôte unique, et non un LAN classique avec une adresse réseau, des hôtes et une diffusion.

### 1.3. Calcul binaire de l’adresse réseau

L’adresse réseau s’obtient en appliquant un ET logique entre l’adresse IP et le masque :

\[
\text{Réseau} = \text{Adresse IP} \land \text{Masque}
\]

Considérons `192.168.34.77/27`. Le masque `/27` est `255.255.255.224` ; son dernier octet est `11100000`.

```text
Adresse IP :  192.168.34.77     11000000.10101000.00100010.01001101
Masque :      255.255.255.224   11111111.11111111.11111111.11100000
              ----------------------------------------------------- ET
Réseau :      192.168.34.64     11000000.10101000.00100010.01000000
```

Le réseau est donc `192.168.34.64/27`. Il comporte 32 adresses : l’adresse réseau `.64`, les adresses d’hôtes `.65` à `.94`, et l’adresse de diffusion `.95`.

Pour les masques qui ne s’alignent pas sur un octet, la méthode la plus rapide à la main consiste à identifier l’octet intéressant, c’est-à-dire le premier octet du masque qui n’est ni `255` ni `0`.

### 1.4. Méthode de la taille de bloc

Dans l’octet intéressant, la taille de bloc est :

\[
B = 256 - M
\]

où `M` est la valeur décimale du masque dans cet octet.

Pour un `/27`, le masque final vaut 224 :

\[
B = 256 - 224 = 32
\]

Les frontières de sous-réseau du dernier octet sont donc 0, 32, 64, 96, 128, 160, 192 et 224. L’adresse `.77` se trouve entre `.64` inclus et `.96` exclu ; le réseau est `.64`, la diffusion `.95`, et les hôtes `.65` à `.94`.

Cette méthode fonctionne pour les préfixes découpant un octet. Il faut néanmoins traiter correctement les octets suivants : pour un `/20`, le masque est `255.255.240.0`, la taille de bloc est 16 dans le troisième octet et les frontières sont `0, 16, 32, 48, ... , 240`.

Exemple : `172.22.45.137/20` appartient au réseau `172.22.32.0/20`, car 45 se situe dans l’intervalle 32–47. L’adresse de diffusion est `172.22.47.255`, et les adresses comprises dans le bloc vont de `172.22.32.0` à `172.22.47.255`.

### 1.5. Algorithme générique de subnetting

Pour traiter un problème de sous-réseau de façon reproductible :

1. Lire la longueur de préfixe et vérifier qu’elle est comprise entre 0 et 32.
2. Convertir la longueur en masque ou utiliser directement le masque fourni.
3. Calculer le réseau par ET logique entre adresse et masque.
4. Calculer la diffusion en mettant tous les bits hôte à 1.
5. Déterminer la plage attribuable en tenant compte du type de sous-réseau et du contexte.
6. Vérifier le nombre d’adresses et la cohérence des frontières.
7. Comparer le résultat aux sous-réseaux voisins pour détecter tout chevauchement.

Un algorithme de calcul peut convertir l’adresse en entier non signé 32 bits. Le masque correspond aux `p` bits les plus significatifs à 1. Le réseau est `IP & MASK`, tandis que la diffusion est `NETWORK | (~MASK & 0xFFFFFFFF)`. La plage hôte classique s’étend du réseau + 1 à la diffusion − 1, à l’exception des préfixes spéciaux comme `/31` et `/32`.

Pseudo-code :

```text
ENTRÉES : adresse IP, préfixe p
VALIDER : 0 <= p <= 32
MASK = masque composé de p bits à 1 puis de (32-p) bits à 0
NETWORK = IP AND MASK
HOST_MASK = NOT MASK limité à 32 bits
BROADCAST = NETWORK OR HOST_MASK
SI p == 31 ET lien point-à-point :
    deux adresses utilisables
SINON SI p == 32 :
    une route/adresse unique
SINON :
    plage habituelle = NETWORK+1 à BROADCAST-1
SORTIES : réseau, masque, diffusion, plage, cardinalité
```

Les calculs de production doivent en plus vérifier que l’adresse saisie est bien canonique si elle est censée représenter un préfixe. Par exemple, `192.168.34.77/27` est une adresse d’interface valide, mais n’est pas la notation canonique du réseau ; celui-ci doit être écrit `192.168.34.64/27`.

### 1.6. VLSM : allocation de tailles variables

Le *Variable Length Subnet Mask* permet de découper un bloc disponible en sous-réseaux de tailles différentes. La méthode traditionnelle consiste à classer les besoins du plus grand au plus petit, puis à allouer le premier bloc aligné qui peut contenir chaque besoin. Cet ordre limite la fragmentation de l’espace disponible.

Pour un besoin de `H` hôtes sur un LAN classique, il faut trouver le plus petit `h` tel que :

\[
2^h - 2 \geq H
\]

Le préfixe sera alors :

\[
p = 32 - h
\]

Exemple de besoins à partir du bloc `10.40.0.0/22` :

| Zone | Besoin d’hôtes | Préfixe minimum | Adresses totales |
|---|---:|---:|---:|
| Campus | 400 | /23 | 512 |
| Wi-Fi interne | 180 | /24 | 256 |
| Voix | 90 | /25 | 128 |
| Gestion | 45 | /26 | 64 |
| Transit point à point | 2 | /31 recommandé si pris en charge | 2 |

Attention : le tableau illustre des tailles minimales indépendantes, mais ces allocations doivent aussi être positionnées sans chevauchement à l’intérieur du bloc parent. Le réseau `10.40.0.0/22` contient les adresses `10.40.0.0` à `10.40.3.255`. Le sous-réseau `/23` `10.40.0.0/23` occupe les deux premiers `/24`. Il ne reste alors que `10.40.2.0/23`, qui peut être découpé en `/24`, `/25`, `/26` et des liens point à point si l’on positionne les blocs avec soin. Si les allocations dépassent la capacité du parent, il faut changer le bloc global plutôt que créer des chevauchements.

Un exemple de découpage valide peut être :

```text
Bloc parent : 10.40.0.0/22
Plage parent : 10.40.0.0 - 10.40.3.255

Campus       10.40.0.0/23     10.40.0.0 - 10.40.1.255
Wi-Fi         10.40.2.0/24     10.40.2.0 - 10.40.2.255
Voix          10.40.3.0/25     10.40.3.0 - 10.40.3.127
Gestion       10.40.3.128/26  10.40.3.128 - 10.40.3.191
Transit       10.40.3.192/31  10.40.3.192 - 10.40.3.193
Transit       10.40.3.194/31  10.40.3.194 - 10.40.3.195
Réserve       10.40.3.196 - 10.40.3.255
```

Le bloc d’exemple laisse de la capacité dans la plage résiduelle, mais il montre pourquoi la planification doit inclure les besoins futurs, la granularité et l’alignement. Les adresses de transit `/31` sont valides dans le contexte des liaisons point à point et doivent être prises en charge par les deux équipements.

### 1.7. CIDR, agrégation et réduction des tables de routage

CIDR permet d’exprimer une route en utilisant une longueur de préfixe indépendante des classes historiques. L’agrégation consiste à regrouper des préfixes contigus lorsque leurs bits de poids fort sont identiques et que le bloc résumé couvre exactement les réseaux que l’on souhaite représenter.

Par exemple, les routes suivantes peuvent être agrégées :

- `10.20.0.0/24`
- `10.20.1.0/24`
- `10.20.2.0/24`
- `10.20.3.0/24`

Ensemble, elles couvrent exactement `10.20.0.0/22`, soit les adresses `10.20.0.0` à `10.20.3.255`. L’agrégation est possible parce que les quatre `/24` constituent un bloc contigu aligné sur une frontière `/22`.

À l’inverse, quatre `/24` non contigus ne peuvent pas être remplacés par un `/22` sans annoncer des espaces supplémentaires. La synthèse ne doit donc jamais être décidée uniquement parce que les premiers nombres des réseaux se ressemblent.

L’algorithme d’agrégation peut être formulé ainsi :

1. Trier les préfixes par adresse et longueur.
2. Identifier les blocs de même taille, contigus et alignés.
3. Chercher le plus long préfixe commun à leurs adresses réseau.
4. Vérifier que le bloc résumé contient exactement les préfixes attendus, ou documenter explicitement les espaces supplémentaires.
5. Vérifier que le routeur annonçant le résumé possède un chemin valide vers chacun des sous-réseaux inclus.
6. Évaluer la route de rejet ou la route de résumé locale qui évite les boucles en cas de destination absente.

Un résumé réduit la taille des tables mais crée une frontière d’information. Si un routeur annonce `10.20.0.0/22` sans avoir de chemin vers `10.20.3.0/24`, il peut attirer le trafic vers un trou noir. Les résumés doivent donc être appuyés par une conception hiérarchique cohérente et des mécanismes de route de rejet selon la plateforme.

### 1.8. Sélection par le préfixe le plus long

Lorsqu’un paquet arrive sur un routeur, la sélection du prochain saut commence par la recherche de la route correspondante la plus spécifique. Cette règle est appelée *Longest Prefix Match* (LPM). Une route `/24` est plus spécifique qu’une route `/16`, car elle décrit un ensemble d’adresses plus petit.

Supposons une table simplifiée :

```text
10.0.0.0/8       -> Routeur A
10.20.0.0/16     -> Routeur B
10.20.30.0/24   -> Routeur C
0.0.0.0/0        -> Passerelle Internet
```

Pour une destination `10.20.30.44`, le routeur sélectionne `10.20.30.0/24`, même si les routes `/8` et `/16` existent. Pour `10.20.31.44`, il sélectionne la route `/16`. Pour `10.99.1.1`, il sélectionne la route `/8`. La route par défaut ne s’applique qu’en l’absence de route correspondante plus spécifique.

Le LPM doit être distingué des critères qui départagent plusieurs routes vers le même préfixe. D’abord, le routeur cherche le préfixe correspondant le plus long. Ensuite, parmi les routes qui couvrent ce même préfixe, les mécanismes de préférence, de distance administrative et de métrique ou de politique interviennent selon l’implémentation.

Une route plus spécifique peut détourner du trafic même si une route moins spécifique a été apprise depuis un protocole jugé plus fiable. Cette propriété est fondamentale pour comprendre les erreurs d’agrégation, les fuites de routes et certains incidents de routage.

### 1.9. Préfixe, route, interface et sous-réseau : distinctions

Les termes « adresse IP », « adresse réseau », « préfixe », « masque » et « route » sont liés mais non synonymes.

- **Adresse d’interface** : adresse attribuée à une interface, par exemple `10.10.12.1/30`.
- **Adresse réseau** : adresse canonique obtenue en mettant les bits hôte à zéro, par exemple `10.10.12.0/30`.
- **Préfixe** : notation réseau/longueur, comme `10.10.12.0/30`.
- **Masque** : représentation à 32 bits du préfixe, comme `255.255.255.252`.
- **Route** : instruction de transfert associant un préfixe de destination à une prochaine étape ou à une interface de sortie.
- **Réseau local** : segment de couche 2 ou domaine IP où les hôtes peuvent échanger directement, selon la topologie et le masque configuré.

Une adresse d’interface ne doit pas être saisie dans un champ destiné à un préfixe réseau sans normalisation. Les outils de gestion des adresses IP (IPAM) doivent vérifier la cohérence du couple adresse/masque, la plage incluse et les chevauchements potentiels.

### 1.10. Adresses privées, publiques et spéciales

Les plages privées RFC 1918 sont destinées à l’usage interne et ne sont pas globalement uniques. Elles sont couramment utilisées dans les LAN, les VPN et les réseaux d’entreprise.

| Plage | Préfixe | Taille | Usage courant |
|---|---|---:|---|
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | 16 777 216 adresses | Grands réseaux internes |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | 1 048 576 adresses | Réseaux privés moyens/grands |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | 65 536 adresses | LAN et réseaux de petite taille |

Autres adresses ou plages particulières importantes :

| Adresse/plage | Signification générale | Précaution |
|---|---|---|
| `0.0.0.0` | Adresse non spécifiée dans plusieurs contextes | Ne pas traiter comme une adresse ordinaire d’hôte |
| `0.0.0.0/0` | Route par défaut | Représente toutes les destinations IPv4 |
| `127.0.0.0/8` | Bouclage local | Le trafic reste local à l’hôte |
| `169.254.0.0/16` | Adressage link-local IPv4 | Généralement auto-attribué lorsqu’aucune configuration appropriée n’est obtenue |
| `255.255.255.255` | Diffusion limitée | Ne traverse normalement pas les routeurs |
| `224.0.0.0/4` | Multicast IPv4 | Plage de groupes multicast, pas plage d’hôtes unicast ordinaire |
| `100.64.0.0/10` | Espace partagé pour CGN | Ne doit pas être confondu avec RFC 1918 |
| `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` | Plages de documentation | Utiliser dans la documentation et les exemples, pas comme préfixes publics ordinaires |

La liste n’est pas exhaustive : il faut consulter le registre spécial IPv4 de l’IANA pour les assignations et leur statut. Une adresse appartenant à un espace spécial ne possède pas nécessairement un comportement de routage identique dans tous les contextes. L’IANA précise notamment que les blocs du registre ne sont pas automatiquement garantis routables dans un domaine particulier.

Une adresse publique n’est pas simplement « tout ce qui n’est pas privé ». Certaines plages sont réservées à des usages particuliers, à la documentation, au multicast ou à d’autres fonctions. L’attribution et la routabilité doivent être vérifiées à partir des registres et des politiques d’exploitation.

### 1.11. DHCP et allocation des adresses

DHCP permet à des clients d’obtenir une adresse IPv4 et des paramètres de configuration, tels que le masque, la passerelle par défaut, les serveurs DNS et la durée du bail. Le protocole est défini notamment par la RFC 2131. Il s’appuie sur un modèle client-serveur et utilise des mécanismes de diffusion et de relais afin de fonctionner quand le serveur ne se trouve pas dans le même sous-réseau.

Le cycle connu sous le nom DORA comprend généralement :

1. **Discover** : le client recherche un serveur DHCP.
2. **Offer** : un serveur propose une configuration.
3. **Request** : le client demande l’offre qu’il souhaite utiliser.
4. **Acknowledge** : le serveur confirme la location.

Ce cycle n’est pas l’unique chemin possible dans toutes les situations : renouvellement, réaffectation et interaction avec plusieurs serveurs conduisent à d’autres séquences. Toutefois, DORA constitue un modèle de base utile pour comprendre la mise en service d’un terminal.

Dans un réseau routé, les diffusions DHCP ne traversent normalement pas les routeurs. Un relais DHCP sur la passerelle du VLAN reçoit les requêtes clientes et les transmet au serveur configuré. Le champ `giaddr` et les informations de relais permettent au serveur d’identifier le sous-réseau concerné et de choisir un pool approprié.

Le pool DHCP doit correspondre au vrai sous-réseau de l’interface. Il faut exclure les adresses réservées aux passerelles, aux serveurs statiques, aux équipements de gestion et aux autres éléments d’infrastructure. Un pool qui chevauche des adresses configurées statiquement peut provoquer des conflits difficiles à reproduire.

### 1.12. Routage inter-VLAN et limites de couche 2

Chaque VLAN qui constitue un sous-réseau IPv4 distinct nécessite une fonction de couche 3 pour communiquer avec les autres sous-réseaux. Cette fonction peut être assurée par un routeur, un commutateur de couche 3 ou une architecture équivalente.

Le masque détermine si un hôte considère une destination comme locale ou distante. Si la destination appartient au même préfixe, l’hôte tente généralement de résoudre l’adresse de liaison du destinataire sur le réseau local. Si la destination est extérieure au préfixe, il envoie le paquet vers sa passerelle par défaut.

Une erreur de masque peut donc produire des symptômes surprenants : un hôte peut tenter de rechercher directement un voisin qui se trouve en réalité derrière un routeur, ou envoyer à sa passerelle un trafic qu’il croyait local. Les adresses et les masques doivent être cohérents sur l’ensemble d’un même domaine IP.

Un VLAN n’est pas automatiquement synonyme d’un sous-réseau IPv4, même si la conception courante associe un sous-réseau IP à chaque VLAN. Il s’agit de niveaux distincts : le VLAN segmente la couche 2, tandis que le préfixe IPv4 structure l’adressage et le routage de couche 3. Leur correspondance doit être explicitement documentée.

### 1.13. En-tête IPv4 : champs utiles à l’ingénieur

L’en-tête IPv4 de base a une longueur minimale de 20 octets, mais peut être plus long lorsque des options sont présentes. Le champ *IHL* exprime la longueur de l’en-tête en mots de 32 bits. Le champ *Total Length* donne la longueur totale du datagramme, en-tête compris, avec une limite théorique de 65 535 octets.

Les champs d’intérêt opérationnel incluent :

- **Version** : identifie IPv4 par la valeur 4.
- **DSCP/ECN** : utilisé pour le marquage de services différenciés et la notification explicite de congestion.
- **Identification, Flags et Fragment Offset** : participent à la fragmentation et à la réassemblage.
- **TTL** : limite la durée de vie logique d’un paquet en diminuant à chaque routeur traversé.
- **Protocol** : identifie le protocole de couche supérieure, par exemple TCP, UDP ou ICMP.
- **Header Checksum** : protège uniquement l’en-tête IPv4, et doit être recalculé quand certains champs changent, notamment TTL.
- **Source/Destination Address** : adresses IPv4 source et destination.

Le checksum IPv4 ne protège pas la charge utile. Les protocoles de couche supérieure peuvent fournir leurs propres sommes de contrôle, et les couches de liaison peuvent également avoir des mécanismes d’intégrité. Un équipement intermédiaire qui décrémente le TTL doit recalculer le checksum de l’en-tête dans le modèle IPv4 classique.

Le TTL est souvent présenté comme un temps en secondes, mais opérationnellement il sert de limite de sauts : chaque routeur décrémente au moins d’une unité la valeur reçue, même lorsque le temps de transit est inférieur à une seconde. Lorsque le TTL atteint zéro, le paquet est éliminé et un message ICMP approprié peut être généré selon le contexte et les politiques de filtrage.

### 1.14. MTU, fragmentation et découverte de MTU de chemin

Le MTU (*Maximum Transmission Unit*) représente la taille maximale du paquet de couche réseau qui peut être transporté sur un lien sans segmentation supplémentaire à cette couche. Sur Ethernet classique, le MTU IP le plus courant est de 1500 octets, mais les tunnels, les encapsulations, les services opérateurs et les extensions peuvent modifier le budget disponible.

IPv4 autorise la fragmentation dans certaines conditions. Les fragments utilisent les champs Identification, MF (*More Fragments*) et Fragment Offset pour permettre au destinataire de reconstituer le datagramme. L’offset est exprimé par unités de huit octets. La fragmentation augmente les coûts de traitement et une perte d’un seul fragment peut rendre inutilisable le datagramme complet.

Le bit DF (*Don't Fragment*) demande qu’un routeur ne fragmente pas le datagramme. Si le paquet dépasse le MTU de sortie et que DF est activé, le routeur le rejette normalement et peut signaler l’erreur par ICMP Destination Unreachable, code « fragmentation needed » dans IPv4. La découverte du MTU de chemin (*Path MTU Discovery*) exploite ce signal pour adapter la taille des paquets. Si ICMP est filtré de manière excessive, certains flux peuvent rencontrer un « trou noir PMTUD » : petites requêtes réussies, transferts volumineux qui se bloquent.

Les tunnels ajoutent un en-tête et réduisent la charge utile maximale. Pour une encapsulation VPN, il faut tenir compte du MTU, du MSS TCP et du comportement ICMP. Une correction appliquée sans analyse, par exemple baisser arbitrairement tous les MTU, peut masquer le problème et introduire une dégradation ailleurs.

### 1.15. NAT et conséquences sur le plan d’adressage

La traduction d’adresses réseau (NAT) modifie des informations IP et parfois des ports de couche transport. Le NAT avec surcharge, généralement appelé PAT, permet à plusieurs adresses privées d’utiliser une même adresse publique en distinguant les flux par les ports. La traduction peut faciliter la connectivité vers l’extérieur, mais elle ne remplace ni un plan d’adressage cohérent ni une politique de sécurité complète.

Les problèmes de chevauchement apparaissent souvent lorsque deux sites utilisent les mêmes plages RFC 1918 et doivent être interconnectés par VPN. Le routage ne peut pas distinguer deux préfixes identiques appartenant à des sites différents sans mécanisme d’isolation, de traduction ou de refonte d’adressage. Les solutions possibles incluent la renumérotation, la traduction NAT adaptée, l’utilisation de VRF ou une combinaison de ces méthodes.

Le NAT complique également certains protocoles qui transportent des adresses dans leur charge utile et affecte la traçabilité des sessions. Les journaux de traduction et la synchronisation temporelle deviennent essentiels pour les diagnostics et les investigations. Pour une architecture durable, il vaut mieux limiter les chevauchements dès le plan d’adressage plutôt que dépendre en permanence de traductions complexes.

### 1.16. Résumé de route, route de rejet et trou noir

Un routeur qui annonce un agrégat doit avoir un comportement défini pour les sous-réseaux inclus dans l’agrégat mais actuellement injoignables. Un résumé peut être accompagné d’une route de rejet locale (par exemple une route vers Null0 sur certaines plateformes Cisco) afin d’éviter que le routeur ne renvoie indéfiniment le trafic vers un autre routeur qui lui-même annonce le résumé.

Exemple Cisco :

```cisco
ip route 10.20.0.0 255.255.252.0 Null0
```

Cette route représente le bloc `10.20.0.0/22` comme route de rejet. Elle ne doit être déployée que si le routeur possède les routes plus spécifiques nécessaires pour acheminer les sous-réseaux présents. Grâce au LPM, une route plus spécifique existante l’emporte sur l’agrégat ; si aucun préfixe plus spécifique ne correspond, le paquet tombe dans Null0 au lieu de reboucler.

Le comportement exact dépend du protocole et de la plate-forme. Certains protocoles installent automatiquement une route de rejet lors d’un résumé. Il faut examiner la table de routage et la configuration afin de ne pas créer accidentellement un trou noir couvrant des réseaux actifs.

### 1.17. Choix des préfixes pour les liens point à point

Un lien point à point IPv4 entre deux routeurs n’a généralement besoin que de deux adresses d’extrémité. L’emploi historique d’un `/30` fournit quatre adresses, dont deux utilisables selon le modèle de sous-réseau classique. L’emploi d’un `/31`, autorisé par la RFC 3021 pour les liens point à point, permet d’utiliser les deux adresses du bloc comme adresses des extrémités.

| Type de lien | Préfixe | Adresses totales | Adresses d’extrémité exploitables |
|---|---:|---:|---:|
| Point à point historique | /30 | 4 | 2 |
| Point à point compact | /31 | 2 | 2, si pris en charge aux deux extrémités |
| Loopback ou route d’hôte | /32 | 1 | Adresse unique dans le contexte de routage |

Le `/31` ne doit pas être utilisé aveuglément sur un réseau multi-accès Ethernet contenant plusieurs hôtes. Sa pertinence vient de la nature point à point du lien et du support par les équipements. Pour une interface loopback, le `/32` est souvent employé afin de représenter une adresse unique routable, par exemple comme identifiant stable pour des protocoles ou des opérations de gestion.

### 1.18. Calcul des capacités et marge de croissance

Le nombre d’adresses doit être dimensionné sur la capacité utile, et non uniquement sur le nombre actuel d’équipements. Il faut prendre en compte les adresses réservées à l’infrastructure, la croissance, les changements d’organisation, les équipements temporaires et les migrations.

Une méthode de dimensionnement fiable :

1. Inventorier les terminaux et services actuels par segment.
2. Estimer l’évolution à l’horizon choisi, en distinguant les pics et les usages temporaires.
3. Ajouter les adresses d’infrastructure : passerelles, équipements de sécurité, imprimantes, contrôleurs, sondes et systèmes de gestion.
4. Choisir le plus petit préfixe dont la capacité est supérieure ou égale au besoin avec une marge explicitement décidée.
5. Conserver des blocs contigus pour permettre les agrégations futures.
6. Documenter la capacité libre restante et les seuils de déclenchement d’une renumérotation.

Un sous-réseau presque plein peut entraîner des échecs DHCP, des adresses dupliquées, des ajouts improvisés et une fragmentation du plan d’adressage. La surveillance du taux d’utilisation est donc une tâche opérationnelle au même titre que la surveillance CPU ou mémoire des équipements.

### 1.19. Plan d’adressage hiérarchique

Une architecture évolutive attribue des blocs selon une hiérarchie prévisible : région, site, bâtiment, fonction, environnement et sous-réseau. Une organisation peut réserver un `/16` par grand site, puis découper cet espace en `/20` pour des bâtiments ou des domaines fonctionnels, ensuite en `/24` ou `/26` selon le besoin. Le bon découpage dépend des dimensions réelles et de la politique d’agrégation.

Les objectifs sont :

- limiter les chevauchements et les exceptions ;
- faciliter la synthèse de routes par site ou région ;
- isoler les domaines de diffusion ;
- permettre des règles de sécurité lisibles ;
- prévoir la croissance sans renumérotation permanente ;
- simplifier le dépannage et la gestion IPAM.

Un plan très hiérarchique ne convient pas à toutes les architectures. La mobilité des charges, les environnements cloud, les acquisitions et les réseaux VPN peuvent exiger des règles particulières. Il faut arbitrer entre agrégation, flexibilité et simplicité opérationnelle. L’objectif n’est pas de forcer chaque réseau dans une hiérarchie théorique, mais de rendre explicites les exceptions et d’éviter les allocations opportunistes non documentées.

### 1.20. Préfixes qui se chevauchent

Deux sous-réseaux se chevauchent lorsque leurs ensembles d’adresses ont une intersection non vide sans correspondre à la relation parent/enfant intentionnellement conçue et gérée. Par exemple, `10.10.0.0/16` et `10.10.20.0/24` couvrent des adresses communes ; l’un contient l’autre. Une telle situation peut être normale dans une table de routage hiérarchique si le /24 représente une route plus spécifique, mais elle est problématique si les deux blocs sont attribués à des segments de couche 2 indépendants et supposés distincts.

Il est donc important de distinguer chevauchement de préfixes dans une table de routage et collision d’adressage dans un plan d’adressage. Le premier peut être voulu pour l’agrégation ou des routes spécifiques ; le second crée souvent une ambiguïté opérationnelle.

Une vérification d’IPAM doit comparer les intervalles numériques. Pour un préfixe IPv4, l’adresse de début est l’adresse réseau et l’adresse de fin est la diffusion ou la dernière adresse incluse dans le bloc. Deux blocs `A` et `B` se chevauchent si `startA <= endB` et `startB <= endA`. Pour des blocs d’infrastructure, ce contrôle doit être appliqué aussi aux réservations et aux plages DHCP.

### 1.21. Table de routage et ordre de décision

La décision de routage est souvent décrite comme un seul choix, alors qu’elle associe plusieurs étapes. Le routeur reçoit un paquet, valide les éléments nécessaires de l’en-tête, décrémente le TTL, consulte les informations de transfert et choisit un prochain saut ou une interface de sortie. La recherche de préfixe la plus long est centrale dans le transfert ; l’installation préalable des routes dépend de la sélection entre les sources de routage et des politiques.

Pour un même préfixe appris par plusieurs sources, les équipements utilisent une préférence administrative ou un mécanisme équivalent, puis des critères de protocole comme la métrique. La distance administrative est un concept spécifique à certaines implémentations, notamment Cisco, et ne doit pas être interprétée comme une mesure universelle normalisée par IPv4. Elle compare la crédibilité relative des sources de routes sur un équipement ; elle ne remplace pas la règle LPM entre préfixes de longueurs différentes.

Exemple conceptuel : si une route statique vers `10.20.30.0/24` est installée et qu’un protocole dynamique apprend aussi `10.20.30.0/24`, l’équipement décide quelle route retenir selon ses préférences. Mais une route vers `10.20.30.0/24` peut être sélectionnée pour une destination de ce bloc face à une route `/16`, parce que le préfixe `/24` est plus spécifique.

### 1.22. ICMP, TTL et diagnostic du chemin

ICMP IPv4 transporte des messages de contrôle nécessaires au diagnostic et à certaines fonctions du réseau. Les outils `ping` et `traceroute` s’appuient sur des messages ICMP ou sur des réponses ICMP déclenchées par des paquets de sondage. Les filtres de sécurité doivent éviter de bloquer indistinctement tous les messages utiles, notamment ceux nécessaires à la découverte du MTU de chemin.

`ping` confirme qu’un échange ICMP Echo est possible à travers le chemin et que la réponse revient, mais son échec ne prouve pas toujours l’absence de connectivité applicative. Un pare-feu peut filtrer Echo Request tout en laissant passer TCP. Inversement, un ping réussi ne garantit pas qu’un port applicatif soit ouvert.

`traceroute` exploite le TTL pour identifier progressivement les routeurs du chemin. Chaque sonde expire à un saut différent ; un routeur peut répondre par ICMP Time Exceeded. Les résultats peuvent être incomplets à cause de filtres ICMP, d’équilibrage de charge, de chemins asymétriques ou de politiques de limitation des réponses. Les étoiles dans la sortie ne signifient pas automatiquement qu’un routeur ne transfère pas le trafic.

### 1.23. Résolution IP vers couche 2

Dans un LAN Ethernet IPv4, la résolution ARP associe une adresse IPv4 locale à une adresse MAC. Quand un hôte doit transmettre un paquet à une destination locale, il recherche l’adresse MAC associée à cette destination. Lorsque la destination est distante, il résout généralement l’adresse MAC de la passerelle par défaut plutôt que celle du serveur distant.

Le masque IPv4 détermine en grande partie ce choix. Une erreur de masque peut conduire l’hôte à émettre une requête ARP pour une adresse qu’il devrait atteindre via son routeur, ou à transmettre à la passerelle une destination qu’il croit locale. Par conséquent, les problèmes de résolution ARP sont parfois des symptômes d’un adressage incorrect plutôt que des pannes ARP autonomes.

La vérification des caches ARP, des interfaces de passerelle et des VLAN contribue au diagnostic. Sur Cisco IOS, les commandes usuelles comprennent `show ip arp` ou `show arp`, selon l’équipement et la version. Sur un terminal, les commandes de consultation varient selon le système d’exploitation.

### 1.24. Adressage IPv4 et sécurité

L’adressage influence directement la segmentation de sécurité. Les sous-réseaux séparés facilitent l’application de listes de contrôle d’accès, de politiques de pare-feu et de règles de surveillance. Ils ne garantissent pas, à eux seuls, une isolation : une mauvaise configuration de routage ou une politique permissive peut permettre le trafic entre segments.

Les risques importants comprennent les serveurs DHCP non autorisés, les conflits d’adresses, l’usurpation d’adresse source, les fuites de préfixes, les routes plus spécifiques inattendues, les chevauchements entre VPN et les plages trop larges autorisées dans les ACL. La validation d’adresse à la périphérie, le filtrage anti-usurpation, DHCP snooping, IP Source Guard et les protections de plan de contrôle peuvent contribuer à réduire certains risques, selon les capacités de la plateforme.

Le plan d’adressage doit être considéré comme une donnée de sécurité. Les zones de confiance, les environnements de production, de test, de gestion et d’administration ne doivent pas être mélangés par commodité sans une justification technique. Les réservations IP, les affectations DHCP et les règles de filtrage doivent être documentées et surveillées.

> **Piège :** Ne confonds pas la règle du préfixe le plus long avec la préférence de route. Le LPM sélectionne la route la plus spécifique parmi les préfixes qui correspondent à la destination. Les préférences administratives et les métriques départagent principalement plusieurs routes candidates vers un même préfixe. Une route `/24` plus spécifique peut donc être utilisée plutôt qu’une route `/16`, même si la route `/16` provient d’une source que l’équipement privilégie habituellement. Autre piège : `/31` est valide pour les liens point à point pris en charge, tandis que `/32` représente un seul préfixe d’hôte ; il ne faut pas appliquer mécaniquement la formule « adresses totales moins deux » à ces cas.

```text
                  EXEMPLE DE DÉCOUPAGE HIÉRARCHIQUE

                  Bloc d'entreprise
                     10.64.0.0/16
                           |
          +----------------+----------------+
          |                |                |
       Site A           Site B           Site C
     10.64.0.0/18    10.64.64.0/18    10.64.128.0/18
          |                |                |
    +-----+------+   +-----+------+   +-----+------+
    |            |   |            |   |            |
  Utilisateurs  Voix Utilisateurs  IT Utilisateurs  Serveurs
  /24 ou /23    /24   /23         /24   /24        /24

  Principes :
  - Les sous-réseaux ne se chevauchent pas.
  - Les blocs de sites sont alignés et contigus dans le bloc global.
  - Le routeur de site peut annoncer un agrégat si tous les préfixes
    inclus sont gérés correctement.
  - Les exceptions et les réserves doivent être documentées.
```

---

## 2. Configuration et Pratique

### 2.1. Objectif du laboratoire

Le laboratoire suivant illustre un réseau d’entreprise composé de deux VLAN utilisateurs, d’un VLAN voix et d’une liaison point à point entre deux routeurs. Il montre comment traduire un plan d’adressage en configuration d’interface, activer un relais DHCP, fournir une route vers un site distant et vérifier les résultats.

Les noms d’interfaces et certaines commandes peuvent varier selon le matériel. La configuration est illustrative et doit être adaptée au modèle exact, à la version IOS/IOS XE et aux politiques de l’organisation. Les plages privées utilisées sont des plages de documentation interne et ne doivent pas être annoncées sur Internet.

Plan d’adressage :

| Segment | Préfixe | Passerelle | Usage |
|---|---|---|---|
| VLAN 10 | 10.64.10.0/24 | 10.64.10.1 | Utilisateurs |
| VLAN 20 | 10.64.20.0/24 | 10.64.20.1 | Voix / équipements associés |
| VLAN 99 | 10.64.99.0/24 | 10.64.99.1 | Gestion |
| Transit R1–R2 | 10.64.255.0/31 | R1 .0, R2 .1 | Point à point pris en charge |
| LAN distant | 10.80.30.0/24 | 10.80.30.1 | Site distant |

L’usage du `/31` sur le transit suppose que les deux équipements le prennent en charge. Si la plate-forme ou le contexte l’exige, employer un `/30` et adapter les adresses. Les préfixes de transit ne doivent jamais être réutilisés sur des segments multi-accès.

```text
                           Site central

       VLAN 10           VLAN 20            VLAN 99
      10.64.10/24       10.64.20/24       10.64.99/24
           |                 |                  |
           +-----------------+------------------+
                             |
                      +--------------+
                      | Switch L3    |
                      | SVI .10.1    |
                      | SVI .20.1    |
                      | SVI .99.1    |
                      +------+-------+
                             |
                        10.64.255.0/31
                             |
                         +---+---+
                         |  R1   |
                         +---+---+
                             |
                         réseau WAN
                             |
                         +---+---+
                         |  R2   |
                         +---+---+
                             |
                      10.80.30.0/24
                        Site distant
```

### 2.2. Configuration des interfaces de couche 3

Exemple sur un commutateur de couche 3 Cisco IOS :

```cisco
hostname SW-CORE
ip routing

vlan 10
 name UTILISATEURS
vlan 20
 name VOIX
vlan 99
 name MANAGEMENT

interface Vlan10
 description PASSERELLE_UTILISATEURS
 ip address 10.64.10.1 255.255.255.0
 no shutdown

interface Vlan20
 description PASSERELLE_VOIX
 ip address 10.64.20.1 255.255.255.0
 no shutdown

interface Vlan99
 description PASSERELLE_GESTION
 ip address 10.64.99.1 255.255.255.0
 no shutdown
```

`ip routing` active le routage IPv4 sur les plates-formes qui utilisent ce mécanisme pour un commutateur multicouche. Les SVI fournissent les adresses de passerelle aux équipements de chaque VLAN. Le statut opérationnel d’une SVI dépend notamment de l’existence et de l’état de ports de couche 2 associés au VLAN ; `no shutdown` à lui seul ne garantit pas que l’interface virtuelle soit opérationnelle.

La configuration de routage doit être complétée par des ports d’accès et des trunks compatibles avec le plan de VLAN. Les politiques de sécurité entre VLANs doivent être ajoutées selon les exigences : l’activation du routage inter-VLAN rend la communication de couche 3 possible, mais ne définit pas automatiquement la politique d’autorisation.

### 2.3. Configuration d’un lien point à point sur R1 et R2

Exemple pour R1 :

```cisco
hostname R1

interface GigabitEthernet0/0
 description TRANSIT_VERS_R2
 ip address 10.64.255.0 255.255.255.254
 no shutdown

ip route 10.80.30.0 255.255.255.0 10.64.255.1
```

Exemple pour R2 :

```cisco
hostname R2

interface GigabitEthernet0/0
 description TRANSIT_VERS_R1
 ip address 10.64.255.1 255.255.255.254
 no shutdown

interface GigabitEthernet0/1
 description LAN_SITE_DISTANT
 ip address 10.80.30.1 255.255.255.0
 no shutdown

ip route 10.64.0.0 255.255.0.0 10.64.255.0
```

La route statique R1 vers `10.80.30.0/24` utilise R2 comme prochain saut. La route de retour sur R2 permet d’atteindre le bloc central `10.64.0.0/16` en direction de R1. Dans un réseau de production, une route de retour trop agrégée doit être justifiée par la topologie réellement gérée par R1 ; le résumé doit couvrir uniquement des préfixes appropriés.

Les routes statiques ne remplacent pas le besoin de vérifier les routes connectées et l’état de la liaison. `show ip route` doit afficher les préfixes connectés et statiques attendus avant les tests de bout en bout.

### 2.4. Configurer un pool DHCP local

Sur un routeur ou un commutateur qui prend en charge le service DHCP IOS, un pool peut être configuré ainsi :

```cisco
ip dhcp excluded-address 10.64.10.1 10.64.10.30

ip dhcp pool VLAN10-USERS
 network 10.64.10.0 255.255.255.0
 default-router 10.64.10.1
 dns-server 1.1.1.1 8.8.8.8
 lease 7
```

La plage exclue protège les adresses réservées avant la première attribution dynamique. Le réseau et le masque du pool doivent correspondre au sous-réseau client ; `default-router` indique la passerelle que les clients doivent utiliser. Les adresses DNS d’exemple doivent être remplacées par les résolveurs approuvés dans l’environnement visé.

Une réservation DHCP statique, lorsque la syntaxe et les identifiants clients de la plateforme le permettent, doit être gérée séparément et documentée. Avant le déploiement, vérifier que les adresses statiques ne sont pas incluses dans le pool dynamique sans exclusion ou réservation cohérente.

Commandes de vérification courantes :

```cisco
show ip dhcp pool
show ip dhcp binding
show ip dhcp conflict
```

Le comportement exact de ces commandes et la disponibilité du serveur DHCP local dépendent de la plateforme IOS/IOS XE. Dans une entreprise, le service DHCP peut être centralisé sur des serveurs spécialisés, et le routeur assure alors le relais plutôt que l’allocation.

### 2.5. Configurer le relais DHCP

Si le serveur DHCP se trouve dans un autre sous-réseau, le routeur ou le commutateur L3 doit relayer les requêtes clientes vers le serveur. Exemple sur la SVI du VLAN 10 :

```cisco
interface Vlan10
 ip address 10.64.10.1 255.255.255.0
 ip helper-address 10.64.250.20
```

`10.64.250.20` représente ici l’adresse du serveur DHCP central. Le relais reçoit les requêtes de diffusion des clients et les transfère au serveur configuré. Celui-ci doit contenir un scope correspondant à `10.64.10.0/24`, avec le bon masque, la bonne passerelle et les options attendues.

Si plusieurs VLANs nécessitent DHCP, il faut placer la configuration de relais sur chaque interface de couche 3 appropriée ou utiliser l’architecture de relais supportée. Ne configure pas un relais sur une interface qui ne représente pas le sous-réseau client sans comprendre l’effet des champs d’identification de sous-réseau.

### 2.6. Configuration et validation du plan d’adressage

Avant de mettre en service les interfaces, établir un tableau de vérité contenant au minimum : nom du site, VLAN, préfixe CIDR, masque, passerelle, plage DHCP, plages statiques, réservation d’infrastructure, route d’agrégation, propriétaire et justification. Chaque sous-réseau doit avoir un identifiant unique dans le système IPAM.

L’administrateur doit vérifier :

- que l’adresse de l’interface appartient au préfixe prévu ;
- que la passerelle n’est pas déjà utilisée par un autre équipement ;
- que les plages DHCP et statiques ne se chevauchent pas ;
- que les préfixes des sites interconnectés ne se chevauchent pas ;
- que le résumé annoncé ne couvre pas un réseau administré par une autre entité ;
- que les règles ACL/pare-feu utilisent les préfixes réels et les bonnes directions.

La documentation doit aussi préciser si le premier ou le dernier hôte d’un sous-réseau est réservé par convention, car il n’existe pas de règle universelle imposant de mettre la passerelle sur la première adresse utilisable. La cohérence du plan compte davantage que la convention choisie.

### 2.7. Commandes de vérification Cisco

Les commandes suivantes constituent un point de départ utile :

```cisco
show ip interface brief
show interfaces
show ip route
show ip route connected
show ip arp
show running-config | section interface
show running-config | include ^ip route
show ip protocols
```

Utilise `show ip interface brief` pour voir les adresses configurées et l’état des interfaces ; `show ip route` pour vérifier les routes installées ; `show ip arp` pour consulter les associations IPv4/MAC ; et la configuration active pour comparer la réalité aux intentions documentées.

La sortie d’une seule commande ne suffit pas toujours à identifier la cause. Une interface peut avoir une adresse correcte mais appartenir au mauvais VLAN ; une route peut être présente sans que le chemin retour soit valide ; une table ARP peut contenir une entrée mais pointer vers une mauvaise adresse MAC. Le diagnostic doit croiser la couche 2, la couche 3, les politiques de sécurité et les services d’allocation.

### 2.8. Vérification de la connectivité

Le test doit se faire par étapes :

1. Tester l’interface locale ou la passerelle depuis le terminal.
2. Tester une adresse dans le même sous-réseau.
3. Tester la passerelle du VLAN distant.
4. Tester l’adresse du serveur distant.
5. Exécuter un traceroute pour observer le chemin.
6. Vérifier le chemin retour depuis la destination ou depuis un point de contrôle.
7. Si seules les grandes transmissions échouent, examiner le MTU, le MSS et ICMP.

Une communication inter-VLAN réussie démontre que les couches 2 et 3 fonctionnent pour cette paire de points, mais ne prouve pas qu’une politique d’accès soit correcte pour tous les flux. Les tests doivent être alignés sur les exigences de sécurité, et pas uniquement sur la possibilité d’échanger des paquets.

> **Astuce :** Pour vérifier rapidement un sous-réseau, lis le préfixe en CIDR, calcule `h = 32 − p`, puis utilise l’ET logique pour trouver le réseau. Pour la plage de diffusion, mets tous les bits hôte à 1. En pratique Cisco, croise `show ip interface brief`, `show ip route`, `show ip arp` et les tests `ping`/`traceroute`. Si une panne ne touche que les flux volumineux ou les sessions VPN, examine le MTU et la découverte de MTU de chemin avant de renuméroter les interfaces.

---

## 3. Dépannage et Sécurité

### 3.1. Méthode de diagnostic par couches

Une panne IPv4 doit être isolée dans un ordre cohérent. Commencer par les paramètres du terminal et la liaison locale ; ensuite examiner la résolution ARP, la passerelle, la table de routage, les filtres, le chemin retour et les contraintes de MTU. Changer plusieurs paramètres simultanément détruit la valeur diagnostique des observations et peut créer de nouvelles anomalies.

La liste de contrôle minimale est la suivante :

1. Vérifier adresse IP, masque et passerelle du terminal.
2. Vérifier l’état du port de commutation, le VLAN et le trunk si nécessaire.
3. Vérifier la SVI ou l’interface de passerelle et son état opérationnel.
4. Vérifier ARP et la présence de la MAC attendue.
5. Vérifier les routes de destination et de retour.
6. Examiner ACL, pare-feu, NAT et politiques de sécurité.
7. Vérifier DHCP, les baux, les exclusions et l’existence de conflits.
8. Examiner MTU, fragmentation, MSS et messages ICMP si le symptôme est lié à la taille des paquets.
9. Consulter les journaux et les compteurs d’erreurs, puis tester une hypothèse à la fois.

### 3.2. Adresse IP ou masque incorrect

Un masque trop large peut faire croire à un hôte que des adresses distantes appartiennent à son réseau local. L’hôte envoie alors des requêtes ARP directement pour ces adresses au lieu de transmettre les paquets à sa passerelle. À l’inverse, un masque trop étroit peut faire considérer comme distants des systèmes qui devraient être voisins ; le trafic est alors envoyé à la passerelle, qui peut ne pas posséder de chemin adapté.

Pour confirmer le problème, compare les informations du terminal avec le plan IPAM et avec la configuration de l’interface L3. Vérifie non seulement l’adresse, mais également la longueur du préfixe. Deux appareils qui partagent un VLAN n’appartiennent pas nécessairement au même sous-réseau si leurs masques sont incorrects, et un sous-réseau IP mal aligné peut provoquer une configuration incohérente.

### 3.3. Adresse dupliquée

Deux équipements utilisant simultanément la même adresse IPv4 peuvent provoquer des interruptions intermittentes, des entrées ARP qui changent ou des connexions qui aboutissent parfois sur le mauvais hôte. Le symptôme peut sembler aléatoire parce que les caches ARP se mettent à jour selon les réponses et les annonces reçues.

La recherche doit comparer les baux DHCP, les réservations, les adresses statiques documentées et les tables ARP des commutateurs ou passerelles. Une surveillance DHCP et des contrôles d’adresses peuvent aider à détecter le problème. Il faut ensuite déterminer quel appareil détient l’adresse conformément au plan ; changer arbitrairement l’adresse de l’un des appareils peut masquer une incohérence plus large du registre IPAM.

### 3.4. Épuisement du pool DHCP

Quand un pool DHCP n’a plus d’adresses disponibles, les nouveaux clients peuvent ne pas obtenir de configuration, alors que les clients existants continuent temporairement à fonctionner grâce à leur bail. Les causes possibles incluent une capacité de sous-réseau insuffisante, des baux trop longs pour le profil d’usage, des exclusions excessives, des terminaux qui multiplient les demandes ou un serveur qui conserve des baux inactifs.

Il faut examiner le taux d’utilisation, les baux actifs, les conflits et la configuration du scope. Augmenter le pool sans contrôle peut chevaucher des adresses statiques ou un sous-réseau adjacent. Si la capacité est réellement insuffisante, il faut planifier un élargissement du préfixe, une renumérotation ou la création d’un sous-réseau supplémentaire, puis mettre à jour le routage, le DHCP, les ACL et la documentation.

### 3.5. Routage asymétrique et route de retour manquante

Un paquet peut atteindre sa destination, mais la réponse peut emprunter une autre route ou être supprimée parce que le réseau distant ne connaît pas le préfixe source. Les pare-feu à états sont particulièrement sensibles à certaines formes d’asymétrie selon leur mode de fonctionnement.

Le diagnostic consiste à vérifier la table de routage sur les deux extrémités et les routeurs intermédiaires, en tenant compte du LPM. Il faut comparer le chemin aller et le chemin retour, puis consulter les journaux de pare-feu, NAT et ACL. La présence d’une route à l’aller ne démontre pas qu’une route de retour existe.

### 3.6. Erreur de résumé ou de routage plus spécifique

Une route agrégée peut attirer du trafic destiné à une plage qui n’existe plus ou n’est pas gérée par l’annonceur. Une route plus spécifique accidentelle peut aussi détourner une partie du trafic de son chemin habituel. Ce type de défaut peut affecter seulement une portion d’un préfixe, ce qui rend le diagnostic plus subtil.

Pour l’analyser, comparer le préfixe annoncé, la longueur de préfixe, le prochain saut et la source de chaque route. Vérifier les routes spécifiques qui l’emportent sur les agrégats. Toute modification de l’agrégation doit être vérifiée du point de vue du chemin retour et de la prévention des boucles.

### 3.7. Problèmes de MTU ou de PMTUD

Lorsque de petites requêtes fonctionnent mais que des transferts volumineux se bloquent, le MTU ou la découverte du MTU de chemin constituent des hypothèses fortes. Les tunnels VPN, certaines encapsulations et les réseaux opérateurs peuvent réduire la taille de charge utile disponible.

Vérifie le MTU de chaque interface pertinente, les paramètres de tunnel, les réglages TCP MSS et la circulation des messages ICMP « fragmentation needed ». Évite de désactiver en bloc les messages ICMP sans analyser les conséquences : certains messages sont nécessaires au fonctionnement normal et au diagnostic de PMTUD. Les correctifs doivent être appliqués sur le segment où la contrainte apparaît, puis validés par des transferts représentatifs.

### 3.8. ARP, passerelle et couche 2

Si un hôte ne peut pas joindre sa passerelle, inspecte le VLAN, la configuration du port, la SVI, l’état de l’interface et le cache ARP. Si l’hôte résout correctement la MAC de la passerelle mais ne peut joindre les destinations distantes, l’analyse passe aux routes et aux politiques de transfert.

Une entrée ARP ne prouve pas que le destinataire peut traiter le trafic. Elle prouve seulement que l’hôte détient une association IP/MAC selon les messages ou mécanismes qui ont alimenté son cache. Une association incorrecte peut provenir d’un conflit, d’une migration de machine, d’une configuration de couche 2 ou d’une attaque d’usurpation ARP.

### 3.9. Sécurité anti-usurpation d’adresse source

L’usurpation d’adresse source consiste à émettre des paquets avec une adresse IPv4 source qui ne correspond pas à l’adresse légitimement attribuée à l’équipement ou à la zone. Elle peut masquer l’origine d’un trafic, contourner des contrôles rudimentaires ou perturber certains mécanismes qui font confiance à l’adresse source.

Le filtrage anti-usurpation doit être appliqué selon la topologie. À l’entrée d’un réseau utilisateur, il peut s’appuyer sur les préfixes légitimes de la zone, DHCP snooping, IP Source Guard ou des listes de contrôle d’accès. Aux frontières d’un réseau, des règles de filtrage d’entrée/sortie et des mécanismes BCP 38/BCP 84 lorsqu’ils sont appropriés réduisent les paquets dont la source ne peut pas être légitime sur l’interface d’arrivée.

Les exceptions doivent être documentées pour les VPN, les chemins asymétriques, le routage multi-hébergé et les réseaux qui utilisent des adresses spéciales. Un filtre trop agressif peut interrompre du trafic légitime ; un filtre trop large laisse subsister les risques.

### 3.10. Sécuriser DHCP et les affectations IP

Un serveur DHCP non autorisé peut distribuer une passerelle ou des DNS malveillants aux clients. Dans les commutateurs qui prennent en charge ces fonctions, DHCP snooping aide à distinguer les ports de confiance des ports où les réponses de serveur ne doivent pas être acceptées. IP Source Guard peut utiliser les informations d’association pour contrôler l’adresse source sur les ports d’accès.

Ces fonctions doivent être configurées selon le modèle et le logiciel du commutateur. Les ports vers les serveurs DHCP légitimes ou les relais doivent être qualifiés correctement, car une mauvaise définition des ports de confiance peut soit affaiblir la protection, soit bloquer l’attribution d’adresses. Les liaisons trunk, les ports d’agrégation et les changements de topologie doivent être intégrés au plan de contrôle de sécurité.

Le système IPAM doit rester la référence de vérité pour les sous-réseaux, les réservations et les adresses statiques. Les changements importants de plan d’adressage doivent être approuvés, sauvegardés et accompagnés d’un plan de retour arrière.

### 3.11. ACL et segmentation

Les ACL IPv4 permettent de contrôler des flux selon les adresses source et destination, les protocoles et parfois les ports de transport. Les règles doivent être ordonnées, documentées et testées dans les deux sens quand cela est nécessaire. La sémantique exacte des ACL, le traitement des règles implicites et les options de journalisation dépendent de la plateforme.

Il faut éviter les plages source ou destination trop larges lorsque seuls quelques réseaux sont autorisés. À l’inverse, une politique très fragmentée peut devenir difficile à maintenir et provoquer des incohérences entre les sites. Un adressage hiérarchique améliore la lisibilité des ACL, car les préfixes peuvent correspondre à des zones de confiance ou à des rôles fonctionnels.

Le découpage en VLAN n’assure pas une isolation totale. La passerelle de couche 3, les ACL, le pare-feu, les routes disponibles et les politiques de contrôle du plan de management déterminent les communications autorisées entre sous-réseaux.

### 3.12. Journaux, télémétrie et audit de l’espace d’adressage

Un plan d’adressage expert doit être surveillé comme une ressource opérationnelle. Les indicateurs intéressants comprennent le taux d’occupation DHCP, les conflits détectés, les changements ARP significatifs, l’évolution des tables de routage, les modifications de préfixes annoncés, les routes inattendues et les événements de traduction NAT.

Les équipements doivent envoyer des journaux à une infrastructure centralisée avec une synchronisation horaire fiable. Sans horodatage cohérent, il devient difficile de faire correspondre un bail DHCP, une entrée NAT, un événement de pare-feu et une session applicative. La collecte doit respecter les exigences de confidentialité et de conservation des données.

Les audits réguliers doivent identifier les préfixes non documentés, les plages qui se chevauchent, les anciennes réservations, les routes statiques oubliées, les sous-réseaux presque saturés et les exceptions de filtrage devenues inutiles.

### 3.13. Procédure de changement et retour arrière

Avant tout changement de masque, d’adresse de passerelle ou de résumé, préparer :

1. l’état de référence de la table de routage et des interfaces ;
2. l’inventaire des pools DHCP, des plages statiques, des ACL et des routes ;
3. la liste des systèmes dépendants, y compris DNS, VPN, supervision et applications ;
4. les tests de validation depuis plusieurs VLANs et sites ;
5. un plan de retour arrière avec des conditions de déclenchement ;
6. un relevé de configuration avant et après intervention.

Une modification d’adressage peut affecter des règles de pare-feu, des listes d’accès, des enregistrements DNS, des politiques VPN et des outils de supervision. La simple modification d’une interface routeur ne constitue donc pas un changement complet. Le plan doit inclure toutes les dépendances documentées et les tests doivent vérifier les chemins aller et retour.

> **Danger :** Un résumé incorrect, une route plus spécifique non autorisée ou un chevauchement entre sites peut détourner du trafic vers un mauvais domaine, créer un trou noir ou exposer un segment qui devait être isolé. Les effets peuvent dépasser le sous-réseau configuré parce que le routage propage les informations de préfixe. Avant de publier une route ou d’élargir un résumé, vérifie son alignement, la totalité des sous-réseaux couverts, le prochain saut, le comportement de rejet en cas de destination absente et les conséquences sur les politiques de sécurité. N’utilise jamais une plage « disponible » sans consulter l’IPAM et les allocations déjà en place.

### 3.14. Références techniques et limites de plateforme

Les mécanismes IPv4 fondamentaux sont définis par des RFC, mais les commandes de configuration et le comportement de certaines fonctions sont spécifiques aux systèmes d’exploitation réseau. Le cours utilise des exemples Cisco IOS/IOS XE courants ; la syntaxe doit être confirmée dans la documentation de la version cible avant d’être déployée.

Références utiles :

- RFC 791, *Internet Protocol* : format du datagramme IPv4, TTL, fragmentation et checksum de l’en-tête — https://www.rfc-editor.org/rfc/rfc791.html
- RFC 4632, *Classless Inter-domain Routing (CIDR): The Internet Address Assignment and Aggregation Plan* — https://www.rfc-editor.org/rfc/rfc4632.html
- RFC 1918, *Address Allocation for Private Internets* — https://www.rfc-editor.org/rfc/rfc1918.html
- RFC 3021, *Using 31-Bit Prefixes on IPv4 Point-to-Point Links* — https://www.rfc-editor.org/rfc/rfc3021.html
- RFC 1812, *Requirements for IP Version 4 Routers* : exigences de transfert et règle du préfixe correspondant le plus long — https://www.rfc-editor.org/rfc/rfc1812.html
- RFC 2131, *Dynamic Host Configuration Protocol* — https://www.rfc-editor.org/rfc/rfc2131.html
- Registre IANA des espaces IPv4 à usage spécial — https://www.iana.org/assignments/iana-ipv4-special-registry

## Points à retenir

- **L’adressage IPv4 est une discipline de conception, pas seulement un calcul de masque.** La longueur CIDR détermine la frontière du préfixe ; les opérations binaires permettent de calculer réseau, diffusion et plage. Le VLSM dimensionne chaque segment, tandis que l’agrégation CIDR exige des préfixes contigus et correctement alignés.

- **La sélection de route commence par le préfixe correspondant le plus long.** Les préférences et métriques départagent les routes candidates vers un même préfixe, mais ne remplacent pas le LPM. Les routes plus spécifiques, les résumés et les routes de rejet doivent être conçus de façon à éviter les détournements de trafic et les trous noirs.

- **Un plan d’adressage robuste doit intégrer l’exploitation et la sécurité.** DHCP, ARP, le MTU/PMTUD, le NAT, les ACL, les VPN et la supervision dépendent de préfixes cohérents. Les plages spéciales doivent être vérifiées dans les registres, les chevauchements doivent être éliminés ou explicitement traités, et chaque changement doit être accompagné de tests et d’un plan de retour arrière.
