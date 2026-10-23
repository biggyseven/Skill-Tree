---
node_id: adressage-expert
title: L'adressage IP (bases) - Expert
---

# L'adressage IP (bases) - Expert

**Niveau :** Expert

L'adressage IP est le mécanisme qui donne une identité logique aux interfaces réseau et permet de structurer la portée des communications dans les réseaux interconnectés. Depuis les premières spécifications d'IPv4, publiées au début du développement de l'Internet moderne, le modèle a évolué d'un adressage historiquement classful vers CIDR, le routage sans classe et l'allocation hiérarchique des préfixes. Cette évolution répond à deux contraintes structurelles : l'espace IPv4 limité à 32 bits et la nécessité de maintenir des tables de routage mondiales exploitables. Les décisions d'adressage ne sont donc pas de simples choix de numéros ; elles influencent la taille des tables, les domaines de broadcast, les politiques de routage, la sécurité et les possibilités de croissance.

Une adresse IP est attribuée à une interface logique, et non à une machine de façon absolue. Un serveur peut posséder plusieurs interfaces, une interface peut recevoir plusieurs adresses, et une adresse virtuelle peut être partagée entre des équipements pour assurer la haute disponibilité. En IPv4, un préfixe sépare les bits de réseau des bits d'interface. Le routeur compare les préfixes de destination à sa table de routage, applique le principe du *longest prefix match* et choisit la route la plus spécifique correspondante. Les masques, les préfixes CIDR, le VLSM, l'agrégation, les routes de rejet et les adresses particulières font partie du même système de conception.

IPv6 prolonge ce modèle avec des adresses de 128 bits et un espace très vaste, tout en conservant le concept de préfixe. Il ne s'agit pas simplement d'IPv4 avec des adresses plus longues : la découverte des voisins repose sur NDP plutôt que sur ARP, l'autoconfiguration sans état peut utiliser les Router Advertisements, les adresses link-local sont essentielles au fonctionnement local et la diffusion broadcast n'existe pas. Dans un environnement double pile, le plan IPv4 et le plan IPv6 doivent être conçus, filtrés et dépannés séparément, même lorsqu'ils partagent les mêmes interfaces physiques et VLANs.

Pour un ingénieur réseau expert, maîtriser l'adressage implique de savoir construire un plan stable et résumé, calculer les frontières exactes de préfixes, anticiper les effets de la sélection de route, détecter les chevauchements, distinguer allocation et routabilité, et traiter les services qui dépendent de l'adresse : ARP/NDP, DHCP, DNS, NAT, ACL, journalisation et mécanismes de sécurité de couche 2. Les standards de référence incluent notamment CIDR (RFC 4632), les plages privées IPv4 (RFC 1918), DHCPv4 (RFC 2131), les exigences des routeurs IPv4 (RFC 1812), ainsi que les registres de blocs spéciaux publiés par l'IANA.

> **Analogie** : Imagine un réseau mondial de villes, de quartiers, de bâtiments et de pièces. Le préfixe IP est l'adresse du quartier ; les bits restants identifient l'interface à l'intérieur de ce quartier. Les routeurs sont des carrefours qui ne mémorisent pas nécessairement chaque porte de chaque bâtiment : ils retiennent surtout les directions vers des quartiers et des ensembles de quartiers. Une route agrégée ressemble à un panneau « tous les quartiers de cette zone par cette avenue ». Elle réduit le nombre de panneaux, mais devient dangereuse si elle prétend desservir une zone dont certaines parties ne sont pas réellement accessibles. Le *longest prefix match* revient à suivre le panneau le plus précis : si un panneau général indique toute la zone par l'avenue A, mais qu'un panneau spécifique indique un sous-quartier par l'avenue B, c'est ce dernier qui gagne pour les adresses qu'il couvre. Un plan d'adressage bien conçu donne aux bâtiments voisins des adresses cohérentes, permet de résumer les quartiers et évite qu'une extension de voirie oblige à renuméroter toute la ville.

---

## 1. La théorie et les algorithmes

### 1.1. Adresse, préfixe, interface et portée

Une adresse IP identifie une interface dans un contexte de routage. En pratique, on parle couramment de « l'adresse du serveur », mais un serveur multi-homé possède plusieurs adresses et une même adresse peut être utilisée par un mécanisme de redondance, une interface virtuelle ou un service déplacé. Il faut toujours demander : quelle interface porte l'adresse, sur quel lien, dans quel VRF, avec quel préfixe et pour quelle portée ?

En IPv4, une adresse comprend 32 bits, représentés en notation décimale pointée par quatre octets. Chaque octet varie de 0 à 255. Le préfixe `/p` signifie que les `p` premiers bits identifient le réseau dans le contexte donné ; les `32-p` bits restants sont disponibles pour l'identification d'interface, selon les règles du sous-réseau. Par exemple, `192.0.2.34/27` représente une adresse dont le préfixe réseau est `192.0.2.32/27`.

Le préfixe est une propriété de l'affectation et du routage, pas une partie littérale séparée de l'adresse. L'adresse et le masque doivent être examinés ensemble. `192.0.2.34/24` et `192.0.2.34/27` sont la même adresse IPv4 au format décimal, mais elles appartiennent à des sous-réseaux différents du point de vue de l'interface et peuvent produire des décisions différentes pour les destinations voisines.

En IPv6, l'adresse comporte 128 bits, généralement affichés en huit groupes hexadécimaux séparés par des deux-points. Les règles de compression suppriment les zéros en tête de chaque groupe et autorisent une seule occurrence de `::` pour une suite contiguë de groupes à zéro. Un préfixe `/64` est courant sur les LANs IPv6, mais ce n'est pas une règle universelle pour tous les liens ou toutes les architectures : les liens point-à-point et certains mécanismes ont des besoins différents.

Il faut distinguer quatre concepts :

| Concept | Signification opérationnelle | Erreur à éviter |
|---|---|---|
| Adresse IP | Identifiant logique attribué à une interface | Croire que l'adresse identifie toujours un équipement unique indépendamment du contexte |
| Préfixe | Ensemble d'adresses partageant les bits définis par la longueur de préfixe | Traiter l'adresse sans son masque ou sa longueur CIDR |
| Adresse de couche 2 | Identifiant utilisé pour acheminer une trame sur un lien local, par exemple une adresse MAC Ethernet | Confondre MAC et IP ou croire qu'une MAC traverse les routeurs comme une adresse IP |
| Portée (*scope*) | Domaine où l'adresse a un sens, par exemple link-local, privé ou globalement routable | Déduire la routabilité Internet de la seule syntaxe de l'adresse |

Une adresse privée peut être routée à l'intérieur d'une organisation, mais elle n'est pas globalement routable sur l'Internet public. Une adresse publique n'est pas automatiquement accessible : des filtres, des routes manquantes ou des mécanismes de traduction peuvent bloquer le trafic.

### 1.2. Masque de sous-réseau et calcul binaire

Un masque IPv4 est une suite de bits à `1` contigus à gauche suivis de bits à `0`. Sa représentation décimale classique peut être transformée en préfixe CIDR. Par exemple, `255.255.255.192` correspond à `/26`, car les octets binaires sont `11111111.11111111.11111111.11000000` et contiennent 26 bits à 1.

Le réseau associé à une adresse est calculé par un ET logique bit à bit entre l'adresse et le masque :

```text
Adresse :  11000000.00000000.00000010.00101110
Masque  :  11111111.11111111.11111111.11100000
           ----------------------------------- ET logique
Réseau  :  11000000.00000000.00000010.00100000
Décimal :  192.0.2.32/27
```

Pour un préfixe IPv4 `/p`, la quantité mathématique d'adresses du bloc est `2^(32-p)`. Dans un sous-réseau LAN IPv4 traditionnel, l'adresse avec tous les bits d'hôte à zéro identifie le réseau et celle avec tous les bits d'hôte à un est l'adresse de broadcast dirigé du sous-réseau. La formule habituelle des adresses d'hôte utilisables est donc `2^(32-p)-2`, mais elle ne s'applique pas de la même manière aux `/31` point-à-point (RFC 3021) et aux `/32` qui représentent une seule adresse, souvent utilisée pour une loopback ou une route d'hôte. Elle ne doit pas être transposée à IPv6.

Table de référence courante :

| Préfixe | Masque IPv4 | Adresses totales | Hôtes traditionnels utilisables |
|---|---|---:|---:|
| /24 | 255.255.255.0 | 256 | 254 |
| /25 | 255.255.255.128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 2 |
| /31 | 255.255.255.254 | 2 | 2 sur un lien point-à-point compatible |
| /32 | 255.255.255.255 | 1 | 1 adresse d'hôte/route, pas un LAN traditionnel |

La taille du bloc dans l'octet où le masque change est `256 - valeur_du_masque`. Pour un `/27`, le dernier octet du masque vaut 224 ; la taille du bloc est donc 32. Les réseaux commencent dans le dernier octet à 0, 32, 64, 96, 128, 160, 192 et 224. Une adresse telle que `192.0.2.78/27` appartient à `192.0.2.64/27`, avec plage hôte traditionnelle de `.65` à `.94`, et broadcast `.95`.

Il est dangereux de mémoriser uniquement des tableaux sans savoir retrouver les frontières. En cas de doute, convertir le masque en binaire, calculer le ET logique, puis dériver la plage. Pour les outils d'automatisation, il faut aussi tester les frontières : la première adresse, la dernière adresse et les adresses situées exactement avant et après le bloc.

### 1.3. CIDR et disparition du modèle classful

Le modèle historique distinguait les classes A, B et C avec des frontières implicites `/8`, `/16` et `/24`. Les protocoles et pratiques modernes utilisent CIDR (*Classless Inter-Domain Routing*), où un préfixe peut avoir une longueur explicite quelconque comprise entre 0 et 32 en IPv4. Les classes restent utiles à titre historique, mais elles ne doivent pas piloter un plan d'adressage moderne.

Avec CIDR, `10.16.0.0/12`, `172.20.0.0/14` et `192.0.2.0/27` sont des préfixes dont la longueur est explicitement indiquée. Les algorithmes de routage transmettent des préfixes et des métriques ou politiques, et le routeur choisit les routes installées selon le protocole et les règles du système. Le transfert des paquets utilise ensuite la recherche du préfixe le plus long.

CIDR soutient l'agrégation hiérarchique : un fournisseur peut annoncer un préfixe agrégé couvrant plusieurs réseaux clients contigus au lieu d'annoncer chacun séparément. Pour agréger correctement, les blocs doivent être alignés sur une frontière binaire et avoir une longueur commune compatible. Deux `/24` contigus ne deviennent pas automatiquement un `/23` si leur alignement est incorrect. Par exemple, `192.0.2.0/24` et `192.0.3.0/24` peuvent être agrégés en `192.0.2.0/23`, alors que `192.0.2.0/24` et `192.0.4.0/24` ne le peuvent pas en un seul `/23`.

Un résumé est sûr seulement si l'annonceur peut réellement acheminer les destinations couvertes ou s'il a prévu le traitement des destinations absentes. Les routeurs utilisent parfois une route de rejet vers Null0 pour empêcher les boucles ou les chemins de retour inattendus en présence d'un agrégat. Cela ne doit pas devenir une manière de masquer une mauvaise conception : le comportement de rejet doit être intentionnel et documenté.

### 1.4. Longest Prefix Match (LPM)

Lorsqu'un routeur transmet un paquet IPv4, il compare l'adresse de destination aux entrées de la table de transfert. Si plusieurs routes couvrent cette destination, la route au préfixe le plus long gagne. La distance administrative et la métrique interviennent lors de la sélection ou de l'installation des routes provenant des protocoles ; elles ne remplacent pas le LPM pendant la décision de transfert. Le premier choix est la correspondance de préfixe la plus spécifique dans la table installée.

Exemple de table :

```text
0.0.0.0/0       -> R-WAN-A
10.0.0.0/8      -> R-CORE
10.20.0.0/16    -> R-DATACENTER
10.20.30.0/24   -> R-SECURE-ZONE
```

Pour une destination `10.20.30.44`, le routeur choisit `10.20.30.0/24`, même si la route par défaut et les trois autres préfixes correspondent également. Pour `10.20.40.44`, il choisit `/16`. Pour `10.90.1.1`, il choisit `/8`. Une route plus spécifique peut donc détourner un trafic normalement couvert par un résumé ou une route par défaut.

Cette propriété est cruciale pour le dépannage et la sécurité. Une route `/32` inattendue peut attirer une destination précise ; un préfixe `/24` annoncé par erreur peut détourner le trafic d'un bloc beaucoup plus large ; une route par défaut ne sert que lorsqu'aucune route plus spécifique ne correspond. Il faut examiner le préfixe effectif et le prochain saut, pas seulement constater la présence d'une route générale.

### 1.5. VLSM : allocation de tailles différentes

Le VLSM (*Variable Length Subnet Mask*) permet d'allouer des sous-réseaux de tailles différentes au sein d'un même plan. C'est la méthode normale pour optimiser IPv4, puisque les besoins d'un lien de transit, d'un petit bureau et d'un grand VLAN ne sont pas identiques.

La méthode manuelle consiste à :

1. Recenser les segments et compter les adresses nécessaires, en incluant les passerelles, les interfaces d'infrastructure, les IP virtuelles et une réserve documentée.
2. Trier les segments du plus grand besoin au plus petit.
3. Choisir pour chacun le plus petit bloc dont la capacité est suffisante.
4. Aligner chaque bloc sur une frontière correspondant à sa taille.
5. Vérifier que les blocs ne se chevauchent pas et restent dans le bloc parent.
6. Réserver les plages futures sans les affecter immédiatement.
7. Documenter l'adresse réseau, le préfixe, la plage, le broadcast, la passerelle, le propriétaire et la fonction.

Exemple : un site dispose de `10.50.0.0/22` (1024 adresses). Il doit créer un VLAN de 400 clients, un VLAN de 100 clients, un VLAN de 50 clients et six liens de transit point-à-point. Pour le VLAN de 400 clients, un `/23` fournit 512 adresses au total et 510 adresses hôte traditionnelles ; c'est suffisant, sous réserve de l'architecture. Le VLAN de 100 clients nécessite au minimum un `/25` (126 hôtes traditionnels), et celui de 50 clients un `/26` (62 hôtes). Les liens point-à-point IPv4 peuvent utiliser des `/31` si les équipements les prennent en charge, ou des `/30` selon les contraintes.

Un plan possible doit ensuite être aligné sur les frontières : `10.50.0.0/23` pour le premier VLAN, `10.50.2.0/25` pour le second, `10.50.2.128/26` pour le troisième, puis les petits blocs de transit à partir de `10.50.2.192/31` et des frontières suivantes. Chaque affectation doit être vérifiée par un script ou un outil IPAM ; une suite arithmétique d'adresses ne suffit pas à garantir l'absence de chevauchement.

### 1.6. Agrégation et architecture hiérarchique

Un plan hiérarchique facilite le résumé de routes. Il est courant d'allouer un bloc par région, site, campus ou fonction, puis de le découper en sous-réseaux d'accès. Les sites doivent recevoir des blocs assez grands pour la croissance prévue, sans consommer l'espace trop rapidement. L'objectif n'est pas d'obtenir le plus petit sous-réseau possible partout ; l'objectif est de minimiser les chevauchements, rendre les annonces résumables, simplifier l'exploitation et permettre une renumérotation maîtrisée.

Exemple d'allocation :

```text
Bloc entreprise : 10.64.0.0/10
    Région Nord : 10.64.0.0/12
        Site A : 10.64.0.0/16
            Utilisateurs : 10.64.0.0/20
            Voix       : 10.64.16.0/20
            Serveurs   : 10.64.32.0/21
        Site B : 10.65.0.0/16
    Région Sud : 10.80.0.0/12
        Sites organisés en blocs contigus
```

Ce schéma est conceptuel : les sous-blocs réellement attribués doivent respecter les frontières binaires et chaque sous-réseau doit être contenu dans son parent. Dans un réseau réel, le plan doit être créé à partir d'un registre central, puis publié aux équipes réseau, système, sécurité et cloud.

Les agrégats peuvent réduire les entrées de routage et contenir la propagation de certains changements. Mais un agrégat n'est pas automatiquement un résumé sûr : si un site annonce `10.64.0.0/12` alors qu'il ne sait joindre qu'une partie de cette plage, le trafic vers les trous peut être envoyé vers ce site et tomber en panne. Les routes de rejet, les annonces plus spécifiques et les mécanismes de continuité doivent être conçus ensemble.

### 1.7. Plages IPv4 privées, publiques et spéciales

Les plages privées IPv4 définies par RFC 1918 sont :

| Bloc | Préfixe | Utilisation typique |
|---|---|---|
| 10.0.0.0 à 10.255.255.255 | 10.0.0.0/8 | Entreprises, réseaux multisites, cloud privé |
| 172.16.0.0 à 172.31.255.255 | 172.16.0.0/12 | Sites et environnements intermédiaires |
| 192.168.0.0 à 192.168.255.255 | 192.168.0.0/16 | LANs et réseaux de petite taille |

Le bloc `100.64.0.0/10` est réservé à l'espace partagé utilisé notamment dans les réseaux d'opérateurs (RFC 6598) ; ce n'est pas un bloc privé RFC 1918 et il ne doit pas être confondu avec un espace d'adressage d'entreprise ordinaire. Les préfixes de documentation tels que `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` sont prévus pour les exemples et ne doivent pas être employés en production comme adresses publiques routables.

D'autres plages ont une sémantique particulière :

| Plage | Rôle | Précaution |
|---|---|---|
| 127.0.0.0/8 | Bouclage IPv4 | Ne doit pas être annoncée comme un réseau distant ordinaire |
| 169.254.0.0/16 | Adressage link-local IPv4 | Généralement choisi automatiquement en absence de configuration appropriée ; non routé entre liens |
| 0.0.0.0/0 | Route par défaut | Préfixe de routage, pas adresse d'interface ordinaire |
| 255.255.255.255 | Broadcast limité | N'est pas transféré comme un paquet unicast routé ordinaire |
| 224.0.0.0/4 | Multicast IPv4 | Nécessite une conception et des mécanismes multicast adaptés |
| 240.0.0.0/4 | Plage réservée historiquement | Ne pas l'affecter arbitrairement à des hôtes de production |

Le registre IANA des blocs à usage spécial est la référence pour analyser les plages qui ne sont ni simplement « privées » ni universellement « publiques ». Les règles de filtrage en périphérie doivent également tenir compte des adresses sources ou destinations impossibles, réservées ou incohérentes avec l'interface d'entrée.

### 1.8. IPv6 : structure et portée

IPv6 utilise 128 bits. Une adresse est souvent notée comme huit groupes de 16 bits hexadécimaux. Par exemple, `2001:0db8:0000:0000:0000:0000:0000:0042` peut être compressée en `2001:db8::42`. Le préfixe `2001:db8::/32` est réservé à la documentation et ne doit pas servir d'espace de production.

Les principales catégories d'adresses IPv6 sont :

| Type | Préfixe/exemple | Portée et usage |
|---|---|---|
| Global unicast | Généralement `2000::/3` aujourd'hui pour les allocations globales usuelles | Routabilité globale selon l'allocation et les politiques |
| Link-local | `FE80::/10` | Communication sur le lien, indispensable à de nombreux mécanismes IPv6 |
| Unique local (ULA) | `FC00::/7`, couramment généré dans `FD00::/8` | Adressage interne ; non destiné au routage global Internet |
| Loopback | `::1/128` | Adresse locale de bouclage IPv6 |
| Unspecified | `::/128` | Valeur spéciale, notamment avant qu'une adresse source soit disponible |
| Multicast | `FF00::/8` | Communication vers un groupe multicast |
| Documentation | `2001:db8::/32` | Exemples, formation et documentation |

IPv6 ne définit pas de broadcast. Les protocoles utilisent des adresses multicast, unicast et des mécanismes adaptés. NDP, basé sur ICMPv6, remplace plusieurs fonctions d'ARP et couvre notamment la découverte de voisins et de routeurs, la vérification de joignabilité, la détection de doublons d'adresses et la redirection dans les conditions prévues par le protocole.

Sur un LAN IPv6 classique, un `/64` est généralement le préfixe de sous-réseau prévu par les mécanismes de découverte et d'autoconfiguration. Il reste important de distinguer l'espace total de 128 bits, le préfixe de routage global, le sous-réseau et l'identifiant d'interface. Une interface peut posséder plusieurs adresses IPv6, par exemple une link-local, une globale et une ou plusieurs adresses temporaires de confidentialité.

Les adresses link-local ont une portée limitée au lien local. Elles ne sont pas routées par les routeurs IP comme des destinations ordinaires. Dans la configuration des routes, une adresse link-local de prochain saut peut nécessiter que l'interface de sortie soit explicitée, car le même préfixe link-local existe potentiellement sur tous les liens.

### 1.9. DHCP, SLAAC et configuration des hôtes

DHCPv4 fournit aux clients une configuration telle que l'adresse IPv4, le masque, la passerelle par défaut et les serveurs DNS selon les options du serveur. Le mécanisme repose sur un modèle client-serveur et utilise généralement une séquence de découverte, d'offre, de demande et d'accusé de réception. Un client peut émettre une requête broadcast lorsqu'il ne dispose pas encore d'adresse utilisable. Si le serveur se trouve dans un autre sous-réseau, un relais DHCP transmet la demande à l'équipement serveur approprié.

En IPv6, la configuration peut reposer sur SLAAC, DHCPv6 ou une combinaison. Les Router Advertisements annoncent des paramètres de lien et de préfixe, et les indicateurs associés aident l'hôte à déterminer s'il doit utiliser DHCPv6 pour certaines informations. Il ne faut pas assimiler automatiquement le rôle de DHCPv4 à DHCPv6 : la passerelle par défaut IPv6 est typiquement découverte par Router Advertisement, plutôt que par une option de routeur par défaut DHCPv6.

La gestion des adresses doit inclure le cycle de vie : attribution, renouvellement, réservation éventuelle, mise hors service, journalisation et récupération après incident. Une adresse fixe configurée manuellement dans la plage dynamique peut provoquer un conflit. Les réservations DHCP et le registre IPAM aident à contrôler l'allocation, mais ils ne dispensent pas de détecter les conflits et de valider les changements.

Un serveur DHCP ne route pas nécessairement les paquets. Il fournit de la configuration ; le routage reste une fonction du plan de transfert des routeurs. De même, DNS traduit des noms en informations de nommage, tandis que DHCP peut fournir l'adresse d'un résolveur. Le succès d'une résolution DNS ne prouve pas la bonne configuration du masque, et la présence d'une adresse DHCP ne prouve pas la joignabilité de la passerelle.

### 1.10. ARP, NDP et acheminement local

Lorsqu'un hôte IPv4 doit envoyer un paquet à une destination dans le même sous-réseau, il doit généralement connaître l'adresse MAC Ethernet correspondante. ARP permet de résoudre l'adresse IPv4 locale en adresse de couche 2. Si la destination est distante selon le préfixe de l'interface, l'hôte ne cherche pas la MAC du serveur distant : il résout la MAC de sa passerelle, puis envoie la trame au routeur.

Le cache ARP conserve temporairement des correspondances. Des entrées statiques peuvent exister, mais une gestion entièrement statique n'est pas adaptée à la plupart des réseaux d'entreprise. ARP ne traverse pas les routeurs ; chaque domaine de diffusion possède son contexte de résolution. Cette limite est essentielle pour comprendre les passerelles, les VLANs et les pannes de communication.

IPv6 utilise Neighbor Discovery Protocol (NDP), basé sur ICMPv6, plutôt qu'ARP. Les messages Neighbor Solicitation et Neighbor Advertisement permettent notamment de découvrir les voisins sur le lien. Les Router Solicitation et Router Advertisement participent à la découverte de routeurs et aux paramètres d'autoconfiguration. Les mécanismes IPv6 dépendent d'ICMPv6 ; filtrer indistinctement ICMPv6 peut casser NDP, la découverte de PMTU et des fonctions indispensables à l'exploitation.

La sécurité est différente : ARP n'intègre pas un mécanisme cryptographique d'authentification des annonces. Les protections de commutateur comme DHCP Snooping et Dynamic ARP Inspection peuvent réduire certains risques si elles sont adaptées à la topologie. IPv6 expose d'autres enjeux, notamment les Router Advertisements non autorisés et les annonces NDP trompeuses ; RA Guard, protections de couche 2 et politiques de filtrage doivent être configurées avec compréhension des extensions et des capacités de la plateforme.

### 1.11. Routage, VRF et chevauchement des plans d'adressage

Une adresse n'est unique que dans son contexte de routage. Deux clients isolés dans des VRF distincts peuvent utiliser le même préfixe IPv4 privé sans conflit immédiat, car leurs tables de routage sont séparées. En revanche, lorsqu'une communication entre VRF devient nécessaire, les chevauchements compliquent le routage, la traduction d'adresses, les politiques et la supervision.

Le chevauchement est fréquent lors de fusions d'entreprises, de connexions partenaires, d'intégrations cloud ou d'environnements de laboratoire clonés. Les solutions possibles incluent la renumérotation, la segmentation persistante par VRF, l'utilisation de NAT dans une zone contrôlée ou un mécanisme d'interconnexion adapté. Le NAT peut résoudre certaines contraintes de chevauchement, mais il ajoute de l'état et peut compliquer les protocoles, les journaux, les analyses et la connectivité initiée depuis l'extérieur.

Avant de choisir NAT comme remède durable, évaluer le coût de maintenance, les exigences de traçabilité, les flux entrants, les protocoles qui transportent des adresses dans leur charge utile et les besoins de haute disponibilité. La renumérotation est souvent plus coûteuse au début, mais peut réduire la complexité opérationnelle à long terme.

### 1.12. NAT et signification de l'adresse de bout en bout

Le NAT IPv4 traduit les adresses d'un domaine vers un autre. Le NAPT/PAT traduit aussi les identifiants de transport, souvent les ports TCP ou UDP, afin que plusieurs flux partagent une adresse externe. Cette traduction est courante dans les accès à Internet et certains environnements privés, mais elle ne remplace pas le routage et ne constitue pas, à elle seule, une politique de sécurité complète.

Le NAT modifie la signification de l'adresse observée de part et d'autre de l'équipement. Les journaux doivent donc enregistrer suffisamment d'information pour relier une session externe à son hôte interne : adresse source, port source, protocole, horodatage et paramètres nécessaires selon les exigences légales et opérationnelles. Sans ces informations, l'attribution d'un événement à un hôte peut être difficile.

Les connexions initiées depuis l'extérieur nécessitent une politique de traduction explicite ou un mécanisme conçu pour ce besoin. Des applications qui transportent des adresses dans leur payload, des protocoles non TCP/UDP et certains usages d'IPsec peuvent avoir besoin d'un traitement particulier. La conception doit s'appuyer sur les exigences du trafic et les capacités réelles des équipements, pas seulement sur une règle PAT par défaut.

### 1.13. MTU, fragmentation et PMTUD

Une adresse correctement configurée ne garantit pas que des paquets de toutes tailles traverseront le chemin. Chaque liaison possède une MTU qui limite la taille du paquet ou de la charge utile IP qu'elle transporte sans fragmentation à ce niveau. En IPv4, des routeurs peuvent fragmenter un datagramme si le bit DF n'est pas défini et si les conditions le permettent ; la fragmentation augmente la complexité et peut être perturbée par des filtres qui bloquent certains fragments.

Path MTU Discovery cherche à déterminer la taille maximale supportable par le chemin. Des messages ICMP pertinents participent au mécanisme ; les filtrer sans politique de remplacement peut créer des pannes où les petites connexions fonctionnent mais les transferts de gros volumes se bloquent. IPv6 ne permet pas aux routeurs intermédiaires de fragmenter les paquets : la fragmentation, si nécessaire, relève de la source avec un en-tête de fragmentation, et PMTUD reste important.

Lorsqu'un utilisateur signale qu'un site répond au ping mais que des applications se bloquent lors d'échanges plus grands, vérifier la MTU, les tunnels, l'encapsulation, la transmission des messages ICMP requis et la cohérence de MSS TCP. Ne pas attribuer systématiquement le problème à l'adressage ; l'adressage, le routage et la taille des paquets interagissent mais représentent des plans de diagnostic différents.

### 1.14. Architecture d'un plan d'adressage en production

Un plan d'adressage d'entreprise doit être une architecture documentée, pas une liste d'IP dans un tableur isolé. Il doit couvrir les environnements physiques, virtualisés, cloud, VPN, gestion, voix, utilisateurs, serveurs, stockage, transit, loopbacks, adresses virtuelles de haute disponibilité, NAT et éventuels réseaux de services partagés.

Les règles de conception les plus importantes sont :

- réserver des blocs hiérarchiques par région, site, fonction ou domaine de sécurité ;
- attribuer des blocs de transit distincts des VLANs utilisateurs ;
- réserver des plages aux loopbacks, adresses virtuelles, équipements de gestion et infrastructures ;
- définir les préfixes autorisés pour chaque VRF, site et zone ;
- établir une politique de résumé cohérente avec les annonces BGP/IGP ;
- éviter les plages très courantes susceptibles de chevaucher les réseaux domestiques ou partenaires lorsque l'organisation s'interconnecte largement ;
- réserver explicitement les blocs futurs et enregistrer leur statut ;
- traiter IPv4 et IPv6 comme deux plans complets, avec des politiques de sécurité équivalentes ;
- automatiser la détection des chevauchements et les contrôles de cohérence ;
- versionner les changements et conserver les preuves d'approbation.

Un IPAM (*IP Address Management*) central est préférable dès que plusieurs équipes créent des réseaux. Il doit être la source de vérité pour les préfixes, les propriétaires, les usages, les plages de DHCP, les réservations, les passerelles, les routes résumées, les VRF et la date de retrait. Les configurations générées ou vérifiées à partir de l'IPAM réduisent les erreurs humaines et favorisent la répétabilité.

### 1.15. Algorithme de calcul des préfixes et validation automatisée

Pour automatiser un calcul IPv4, représenter l'adresse en entier non signé de 32 bits. Le masque d'un préfixe `/p` peut être calculé comme `((2^p)-1) << (32-p)` pour `p` entre 0 et 32, en veillant à utiliser un type numérique suffisamment large. L'adresse réseau est `adresse AND masque`. Le broadcast est `réseau OR NOT(masque)` en limitant l'opération aux 32 bits.

Un validateur de plan doit au minimum :

1. rejeter les préfixes hors intervalle ;
2. normaliser les adresses réseau à la frontière du préfixe ;
3. vérifier que chaque sous-réseau est contenu dans son bloc parent ;
4. détecter tout chevauchement entre blocs non isolés par un contexte de routage ;
5. détecter des passerelles en dehors de la plage ou utilisant une adresse réseau/broadcast quand ces règles sont pertinentes ;
6. vérifier les plages DHCP et exclusions ;
7. vérifier les résumés possibles et les trous d'agrégation ;
8. signaler les adresses appartenant à des blocs spéciaux ;
9. vérifier que les préfixes annoncés correspondent au plan de routage ;
10. produire un rapport déterministe, versionné et auditable.

Les validations ne doivent pas se limiter à l'arithmétique. Une adresse peut être mathématiquement valide et néanmoins interdite par la politique locale, dupliquée dans une autre VRF qui sera interconnectée plus tard ou incompatible avec une convention d'architecture. L'automatisation doit donc combiner calcul, inventaire et règles d'entreprise.

### 1.16. Synthèse de la théorie avancée

L'adressage IP est la rencontre entre une structure binaire et une architecture opérationnelle. Le préfixe définit la portée de l'affectation, le routage sélectionne le chemin vers une destination et la résolution de voisinage fournit la destination de couche 2 sur le lien local. DHCP, DNS, NAT, ACL, VRF, MTU et mécanismes de sécurité s'appuient sur ce socle mais n'ont pas la même fonction.

Les erreurs les plus coûteuses ne sont pas toujours des erreurs de calcul. Ce sont souvent des erreurs de périmètre : un agrégat qui annonce un réseau inaccessible, un chevauchement découvert lors d'une fusion, une plage DHCP qui entre en conflit avec des adresses statiques, un résumé qui masque une panne ou un plan IPv6 qui ne prévoit pas NDP et ICMPv6. L'expertise consiste à vérifier à la fois la valeur des bits, le contexte où ils sont utilisés et les conséquences sur le réseau complet.

> **Piège :** Ne confonds pas la préférence administrative ou la métrique d'un protocole avec le *longest prefix match*. La préférence et la métrique servent à choisir ou installer les routes issues de sources différentes selon la plateforme ; une fois les routes installées, le transfert choisit la correspondance de préfixe la plus spécifique. Une route `/32` inattendue peut donc détourner le trafic malgré une route agrégée `/16` qui semble correcte. De même, un bloc RFC 1918 n'est pas « non routable » à l'intérieur d'une organisation : il est simplement réservé à l'usage privé et n'est pas destiné au routage global public.

```text
                  PLAN D'ADRESSAGE HIÉRARCHIQUE

                +-------------------------------+
                | Bloc entreprise / VRF         |
                | 10.64.0.0/10                 |
                +---------------+---------------+
                                |
                +---------------+---------------+
                |                               |
                v                               v
        +---------------+               +---------------+
        | Région Nord   |               | Région Sud    |
        | 10.64/12      |               | 10.80/12      |
        +-------+-------+               +-------+-------+
                |                               |
          +-----+------+                  +-----+------+
          |            |                  |            |
          v            v                  v            v
       Site A        Site B             Site C       Site D
     10.64/16      10.65/16           ...            ...
          |
     +----+-------------------+
     | VLANs et sous-réseaux  |
     | Utilisateurs / Voix    |
     | Serveurs / Gestion     |
     | Transits / Loopbacks   |
     +------------------------+

   Objectifs : absence de chevauchement, résumés sûrs,
   attribution documentée et croissance contrôlée.
```

---

## 2. Configuration et Pratique

### 2.1. Exemple de plan d'adressage pour un site

Considérons une entreprise qui souhaite organiser un petit campus en trois VLANs : utilisateurs, voix et administration, avec une interface de transit vers le routeur central. L'exemple emploie des adresses privées fictives qui ne doivent pas être reprises automatiquement dans un réseau existant.

| Fonction | VLAN | Préfixe | Passerelle prévue |
|---|---:|---|---|
| Utilisateurs | 10 | 10.64.10.0/24 | 10.64.10.1 |
| Voix | 20 | 10.64.20.0/24 | 10.64.20.1 |
| Administration | 99 | 10.64.99.0/24 | 10.64.99.1 |
| Transit point-à-point | — | 10.64.255.0/31 | 10.64.255.0 et 10.64.255.1 |

Le `/31` de transit doit être utilisé uniquement si les équipements et le contexte sont compatibles avec la sémantique point-à-point définie par RFC 3021. Dans le cas contraire, choisir une configuration prise en charge, généralement un `/30`. Ne jamais appliquer la formule d'hôtes traditionnelle aux `/31` sans tenir compte de cette exception.

### 2.2. Configurer des adresses IPv4 sur Cisco IOS/IOS XE

L'exemple ci-dessous illustre une configuration de routeur avec trois sous-interfaces 802.1Q. La syntaxe exacte dépend de la plateforme, du modèle et du logiciel ; il faut confirmer la prise en charge du routage inter-VLAN sur l'interface physique concernée.

```cisco
hostname R-CAMPUS
!
interface GigabitEthernet0/0
 description TRUNK_VERS_SWITCH
 no ip address
 no shutdown
!
interface GigabitEthernet0/0.10
 description VLAN_UTILISATEURS
 encapsulation dot1Q 10
 ip address 10.64.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 description VLAN_VOIX
 encapsulation dot1Q 20
 ip address 10.64.20.1 255.255.255.0
!
interface GigabitEthernet0/0.99
 description VLAN_ADMINISTRATION
 encapsulation dot1Q 99
 ip address 10.64.99.1 255.255.255.0
!
interface GigabitEthernet0/1
 description TRANSIT_VERS_CORE
 ip address 10.64.255.0 255.255.255.254
 no shutdown
```

Avant d'utiliser cette configuration, vérifier le mode de trunk du commutateur, la liste des VLANs autorisés, le VLAN natif s'il existe et le support du `/31` par les deux extrémités. Dans une conception de production, l'administration du commutateur doit être séparée des VLANs utilisateurs, et l'accès au plan de gestion doit être limité par des ACL et des mécanismes d'authentification appropriés.

Les commandes de validation sont :

```cisco
show ip interface brief
show interfaces GigabitEthernet0/0.10
show ip route connected
show running-config interface GigabitEthernet0/0.10
```

Les interfaces doivent être opérationnelles, les adresses doivent correspondre au plan et les routes connectées doivent apparaître dans la table de routage. Une adresse sur une sous-interface ne garantit pas que le VLAN existe ou qu'il est autorisé sur le trunk ; les couches physiques, 2 et 3 doivent être vérifiées ensemble.

### 2.3. Configurer un serveur DHCP local

L'exemple ci-dessous met en place un pool DHCP pour le VLAN utilisateurs sur un routeur IOS compatible. La syntaxe et les options disponibles varient selon la version ; un serveur DHCP dédié peut offrir une gestion plus adaptée à une grande entreprise.

```cisco
ip dhcp excluded-address 10.64.10.1 10.64.10.30
!
ip dhcp pool VLAN10-USERS
 network 10.64.10.0 255.255.255.0
 default-router 10.64.10.1
 dns-server 10.64.1.53 10.64.1.54
 domain-name exemple.intra
 lease 7
```

Les adresses comprises dans la plage d'exclusion ne sont pas distribuées dynamiquement par ce pool. La passerelle fournie doit appartenir au VLAN correspondant. Les DNS doivent être joignables depuis le VLAN et la politique de sécurité doit autoriser les requêtes nécessaires.

Contrôler le fonctionnement avec :

```cisco
show ip dhcp pool
show ip dhcp binding
show ip dhcp conflict
```

Ne configure pas une réservation statique en oubliant la plage exclue ou sans synchroniser le registre IPAM. Une réservation DHCP, une exclusion et une adresse manuelle sont trois mécanismes distincts ; leur gouvernance doit prévenir les doublons.

### 2.4. Relais DHCP vers un serveur central

Si le serveur DHCP n'est pas dans le même domaine de broadcast, le routeur de passerelle du client doit généralement agir comme relais. Sur IOS, `ip helper-address` est souvent utilisé pour transmettre les requêtes DHCPv4 vers le serveur cible.

```cisco
interface GigabitEthernet0/0.10
 description VLAN_UTILISATEURS
 encapsulation dot1Q 10
 ip address 10.64.10.1 255.255.255.0
 ip helper-address 10.64.1.20
```

Il faut vérifier le routage dans les deux sens entre le relais et le serveur, les ACL, les options de relais et les scopes configurés sur le serveur. `ip helper-address` peut relayer d'autres types de broadcasts UDP selon la configuration et la plateforme ; ne pas activer cette commande sans connaître sa portée fonctionnelle.

Sur un réseau multi-VRF ou multi-tenant, le relais doit rester dans le contexte de routage approprié. Un relais qui envoie la demande vers un serveur joignable dans la mauvaise VRF peut échouer même si l'adresse du serveur semble correcte.

### 2.5. Configurer des routes statiques et comprendre les préfixes

Exemple : le routeur de campus doit envoyer les destinations non connues vers le cœur `10.64.255.1`. La commande suivante installe une route par défaut sur une plateforme IOS IPv4 classique :

```cisco
ip route 0.0.0.0 0.0.0.0 10.64.255.1
```

Pour une route plus spécifique :

```cisco
ip route 10.90.40.0 255.255.255.0 10.64.255.1
```

Une route de rejet d'agrégat peut être utilisée par certains designs afin d'éviter que les destinations non connues couvertes par le résumé ne repartent vers un autre routeur et créent une boucle. Exemple conceptuel :

```cisco
ip route 10.64.0.0 255.192.0.0 Null0 250
```

Cette dernière commande ne doit pas être copiée sans analyse : elle installe une route vers Null0, et la distance administrative indiquée dépend de la syntaxe et des besoins de conception. Une route de rejet peut être utile pour sécuriser un résumé, mais elle provoquera volontairement l'abandon des paquets pour les destinations couvertes si aucune route plus spécifique n'existe. Les routes connectées ou dynamiques plus spécifiques peuvent continuer à gagner par LPM.

Vérifier les routes installées et la route effective vers une destination :

```cisco
show ip route
show ip route 10.90.40.25
show ip cef 10.90.40.25 detail
```

`show ip cef` est disponible sur de nombreuses plateformes Cisco, mais pas nécessairement sous la même forme partout. L'objectif est de consulter la décision de transfert effective, pas uniquement la configuration.

### 2.6. Exemple de plan IPv6 et configuration double pile

Exemple illustratif : chaque VLAN possède un `/64` IPv6 distinct provenant d'un bloc global qui aurait été attribué à l'organisation. Le préfixe ci-dessous est un préfixe de documentation ; il ne doit jamais être employé pour de la connectivité IPv6 globale en production.

```cisco
interface GigabitEthernet0/0.10
 description VLAN_UTILISATEURS
 encapsulation dot1Q 10
 ip address 10.64.10.1 255.255.255.0
 ipv6 address 2001:db8:64:10::1/64
 ipv6 nd managed-config-flag
!
interface GigabitEthernet0/0.20
 description VLAN_VOIX
 encapsulation dot1Q 20
 ip address 10.64.20.1 255.255.255.0
 ipv6 address 2001:db8:64:20::1/64
!
ipv6 unicast-routing
```

La commande `ipv6 nd managed-config-flag` influence l'indicateur annoncé par Router Advertisement ; elle ne met pas à elle seule en place un serveur DHCPv6 et ne garantit pas que les clients obtiennent une adresse par DHCPv6. Le comportement doit être aligné sur la politique d'autoconfiguration IPv6, les Router Advertisements et le serveur choisi.

Le préfixe `2001:db8::/32` est réservé aux exemples. En production, utiliser le préfixe réellement alloué par le fournisseur ou l'autorité appropriée, puis découper les `/64` selon le plan. Pour un adressage interne sans besoin de routabilité globale, les ULA peuvent être envisagées, mais il faut malgré tout assurer l'unicité raisonnable du préfixe et la gestion de l'interconnexion.

### 2.7. Vérification et documentation de configuration

Une mise en production doit réunir plusieurs sources de vérité : la configuration, l'état opérationnel, les tables de routage et le registre IPAM. Les commandes suivantes forment un point de départ sur IOS/IOS XE ; leur disponibilité et leur sortie peuvent varier :

```cisco
show ip interface brief
show ipv6 interface brief
show ip route
show ipv6 route
show arp
show ipv6 neighbors
show ip dhcp binding
show running-config | section interface
```

La preuve de validation devrait être conservée dans le dossier de changement : préfixes avant/après, routes prévues, routes effectives, tests de connectivité, serveurs DHCP/DNS utilisés, contrôles de sécurité et procédure de retour arrière.

Une configuration doit rester compréhensible pour un ingénieur qui reprend le service six mois plus tard. Les descriptions d'interface, les identifiants de VLAN, les conventions de nommage, les commentaires utiles et une source de vérité IPAM valent souvent plus qu'une configuration très compacte mais impossible à auditer.

> **Astuce :** En présence d'une panne, demande d'abord trois réponses factuelles : « Quelle adresse et quel préfixe l'hôte possède-t-il ? », « Quelle route exacte le routeur utilise-t-il pour cette destination ? » et « Quel prochain saut de couche 2 est réellement résolu sur le lien ? ». Ces questions séparent le calcul du sous-réseau, la sélection de route et la résolution de voisinage. Elles évitent de changer au hasard le masque, la passerelle ou les routes statiques.

---

## 3. Dépannage et Sécurité

### 3.1. Méthode de diagnostic par couches

Le dépannage doit séparer l'adressage local, la résolution de voisinage, le routage, les services et les politiques de sécurité. Commencer par un outil ou une commande sans formuler d'hypothèse conduit souvent à accumuler des sorties sans résoudre le problème.

Ordre recommandé :

1. **Configuration de l'hôte** : adresse, préfixe/masque, passerelle, DNS, mode DHCP ou statique, interfaces actives.
2. **Port et VLAN** : état physique, VLAN d'accès, trunk, VLAN autorisés, VLAN natif, STP et politique de sécurité de couche 2.
3. **Résolution de voisinage** : cache ARP sous IPv4 ou table des voisins IPv6, MAC obtenue, erreurs et conflits.
4. **Route locale** : décision de l'hôte pour la destination, puis table de routage de la passerelle.
5. **Chemin de bout en bout** : routes aller et retour, ACL, pare-feu, NAT, VPN, MTU et politique de routage.
6. **Services** : DHCP, relais, DNS, application et état du serveur.
7. **Sécurité et changements récents** : journaux, anomalies de voisinage, annonces de route, changement d'IPAM ou déploiement d'une nouvelle plage.

### 3.2. Erreur de masque ou préfixe

Un masque incorrect produit des décisions locales de portée erronées. Si un hôte pense qu'un serveur distant appartient au même sous-réseau, il tente généralement de résoudre directement son adresse de couche 2 au lieu d'envoyer le paquet à sa passerelle. Si un hôte pense qu'une machine du même VLAN est distante, il envoie le paquet au routeur, qui peut ne pas disposer d'un chemin de retour adapté.

Exemple : l'hôte `10.20.10.25/24` considère `10.20.11.50` comme distant et envoie le paquet à la passerelle ; avec `/23`, il peut considérer cette destination locale selon l'alignement du bloc. Le diagnostic doit examiner le préfixe réellement configuré, et non seulement les trois premiers octets visuellement identiques.

Comparer la configuration de deux hôtes dans le même VLAN, le masque du SVI ou de l'interface de routeur et les préfixes DHCP. Il est possible que les interfaces de routeur soient correctes mais que le scope DHCP distribue un masque erroné. Le registre IPAM, les scopes et les configurations statiques doivent être réconciliés.

### 3.3. Chevauchement de sous-réseaux

Deux interfaces appartenant au même contexte de routage ne devraient pas utiliser des préfixes qui se chevauchent d'une manière non prise en charge. Le chevauchement peut empêcher l'installation des routes, rendre les décisions ambiguës ou créer des comportements différents selon les plateformes. Il peut aussi apparaître à travers une connexion VPN ou une interconnexion de VRF lorsqu'un réseau distant utilise un bloc déjà local.

La résolution durable exige une cartographie des préfixes des deux côtés. Les options sont la renumérotation, la séparation en VRF si l'architecture le permet, une traduction contrôlée ou une interconnexion avec des politiques spécifiques. Le choix doit intégrer la maintenance, la supervision, le dépannage, la haute disponibilité et les futures fusions.

Éviter le réflexe qui consiste à ajouter une route plus spécifique pour « réparer » immédiatement le chevauchement sans analyser l'impact. Le LPM peut masquer le problème pour une destination tout en laissant d'autres flux incohérents. Une solution de contournement doit être documentée et limitée dans le temps.

### 3.4. Conflits d'adresses IPv4 et DHCP

Un conflit survient lorsque plusieurs interfaces actives utilisent la même adresse sur un domaine de routage ou un lien où cette unicité est requise. Les symptômes incluent une connectivité intermittente, des entrées ARP qui changent, des journaux de conflit et des pertes qui semblent aléatoires.

Les causes fréquentes comprennent :

- une adresse statique placée dans une plage DHCP dynamique ;
- une réservation oubliée ou dupliquée ;
- un clone de machine virtuelle avec une configuration réseau copiée ;
- une migration de serveur qui conserve l'ancienne IP ;
- un scope DHCP incorrect ;
- un équipement non autorisé qui distribue des baux ;
- un mauvais raccordement de VLAN.

Il faut identifier les MAC associées à l'adresse, comparer les baux DHCP et les configurations statiques, examiner les événements de couche 2 et prévenir le risque qu'une simple suppression d'entrée ARP fasse disparaître l'indice. Une réponse ARP observée à un instant donné doit être corrélée avec les ports de commutateur et l'identité de l'équipement.

DHCP Snooping peut aider à bloquer des serveurs DHCP non autorisés et à construire une base de liaisons pour certaines fonctions de sécurité. Il doit être déployé avec des ports de confiance identifiés avec soin. Une mauvaise configuration des ports trusted/untrusted peut soit laisser passer un serveur rogue, soit bloquer les réponses du serveur légitime.

### 3.5. ARP spoofing et protections de couche 2

ARP ne fournit pas d'authentification cryptographique native des annonces. Un acteur capable d'émettre des paquets sur le même domaine de broadcast peut tenter de faire associer l'adresse IP d'une passerelle à une adresse MAC qu'il contrôle. Les conséquences peuvent inclure interception, altération ou interruption de trafic.

Les mesures de réduction du risque incluent la segmentation des VLANs, le contrôle physique des ports, les fonctions de sécurité de couche 2, Dynamic ARP Inspection lorsque le matériel et le plan DHCP Snooping le permettent, et la surveillance des changements d'association IP/MAC. Les entrées ARP statiques sont possibles dans certains cas, mais leur maintenance manuelle n'est pas une solution de grande échelle.

La sécurité doit s'appuyer sur une topologie connue. DAI dépend souvent d'une base fiable construite par DHCP Snooping ou de mécanismes de validation spécifiques. Les équipements utilisant des adresses statiques doivent être traités explicitement, sinon le contrôle peut bloquer leur trafic légitime. Tester le déploiement en pilote avant application généralisée.

### 3.6. Sécurité IPv6 : RA, NDP et ICMPv6

IPv6 ajoute des mécanismes de découverte indispensables au fonctionnement local. Un Router Advertisement malveillant ou incorrect peut influencer le préfixe, la route par défaut ou d'autres paramètres que les hôtes apprennent sur le lien. Les annonces NDP peuvent aussi être exploitées dans des attaques locales si le domaine de couche 2 n'est pas maîtrisé.

Les mesures comprennent la limitation des ports pouvant émettre des Router Advertisements, RA Guard sur les commutateurs compatibles, la segmentation, le contrôle d'accès et une politique ICMPv6 consciencieuse. RA Guard et d'autres protections doivent être évalués selon la prise en charge des en-têtes d'extension et les limites de l'implémentation ; une règle simple peut ne pas couvrir tous les cas ou peut bloquer du trafic légitime.

Ne pas bloquer arbitrairement ICMPv6. NDP, les messages d'erreur, Packet Too Big et d'autres fonctions nécessaires au fonctionnement IPv6 reposent sur ICMPv6. Une politique de sécurité doit distinguer les types et les directions, autoriser les messages requis et surveiller les usages anormaux.

### 3.7. Routes inattendues et détournement par préfixe plus spécifique

Lorsqu'un trafic prend un chemin inattendu, vérifier les routes réellement installées et la table de transfert. Une route très spécifique peut gagner sur le résumé attendu. Les origines possibles sont une annonce de routage accidentelle, une configuration statique oubliée, une redistribution excessive, un défaut de filtrage ou un événement de convergence.

Pour examiner un cas sur un routeur Cisco, on peut utiliser :

```cisco
show ip route <adresse-destination>
show ip cef <adresse-destination> detail
show ip protocols
show logging
```

Les commandes exactes varient selon la plateforme. L'objectif est de déterminer le préfixe gagnant, le prochain saut, l'origine probable et la stabilité de la route. En environnement BGP, examiner également les politiques d'import/export et les attributs pertinents ; en IGP, vérifier les annonces, les résumés et les distances administratives.

Des filtres de préfixes, des route-maps, des communautés et des politiques de redistribution doivent appliquer le principe du moindre privilège : n'annoncer que les blocs attendus, depuis les voisins attendus et dans les directions prévues. Les filtres doivent être conçus pour permettre les annonces légitimes et éviter les « trous » de politique qui laissent passer n'importe quel préfixe.

### 3.8. NAT, journaux et traçabilité

Le NAT/PAT peut masquer les adresses internes dans les communications externes. En incident, il faut pouvoir retrouver quel hôte interne utilisait une association donnée à une date et heure précises. Les horloges doivent être synchronisées, les journaux suffisamment détaillés et les politiques de conservation conformes aux besoins opérationnels et légaux.

Une configuration de NAT ne doit pas être considérée comme un pare-feu. Elle peut empêcher certaines sessions entrantes non sollicitées selon son fonctionnement, mais le filtrage doit rester explicite. Des translations statiques, des redirections de port ou des états de session trop larges peuvent exposer des services internes.

Le NAT peut aussi masquer une erreur d'adressage interne jusqu'à l'ajout d'un nouvel accès, d'un VPN ou d'un partenaire. Les blocs privés doivent donc être uniques lorsque l'interconnexion est prévue, sauf si une solution de chevauchement est délibérément conçue et documentée.

### 3.9. Plan de migration ou de renumérotation

La renumérotation d'un réseau ne consiste pas uniquement à changer l'adresse de l'interface du routeur. Elle touche DHCP, DNS, ACL, règles de pare-feu, VPN, listes de contrôle, supervision, scripts, certificats ou licences liées à des IP, règles NAT, enregistrements d'inventaire et applications qui contiennent parfois des adresses littérales.

Une procédure prudente comporte :

1. inventaire des adresses, services, routes, dépendances et propriétaires ;
2. choix d'un nouveau bloc sans chevauchement avec les sites, VPNs, partenaires et réseaux cloud ;
3. plan de transition, coexistence éventuelle et critères de retour arrière ;
4. préparation des pools DHCP, DNS, ACL, NAT et règles de sécurité ;
5. déploiement sur un périmètre pilote ;
6. validation de la route aller/retour, de la résolution de noms et de l'accès applicatif ;
7. migration graduelle des segments et enregistrements ;
8. surveillance renforcée et conservation des preuves ;
9. retrait des anciennes routes, scopes et règles après vérification des dépendances résiduelles.

Les plages doivent être réservées dans l'IPAM avant le début du changement. Laisser coexister deux routes couvrant des préfixes différents peut parfois faciliter la migration, mais la règle exacte de sélection doit être vérifiée pour prévenir tout détournement involontaire.

### 3.10. Liste de contrôle avant mise en production

**Plan et préfixes**
- Chaque bloc est contenu dans son bloc parent et n'empiète pas sur un bloc existant.
- Les frontières binaires sont exactes et les tailles correspondent au nombre d'interfaces prévu.
- Les plages de croissance, de transit, de loopback et d'administration sont réservées.
- Les adresses privées, partagées, spéciales et de documentation sont traitées selon leur portée.

**Routage**
- Les routes connectées, statiques et dynamiques attendues sont présentes.
- Les résumés ne couvrent pas de blocs non joignables sans route de rejet prévue.
- Les routes de retour sont testées.
- Les filtres de préfixes et la redistribution correspondent à la politique de sécurité.

**Services**
- Les scopes DHCP, exclusions, réservations et relais sont cohérents.
- Les paramètres DNS et le domaine de recherche sont corrects.
- Les entrées DNS sont mises à jour selon le cycle de vie.
- Les paramètres IPv6 (RA, préfixes, DHCPv6 éventuel, DNS) sont testés indépendamment.

**Sécurité**
- Les ports d'accès et trunks sont cohérents avec les VLANs prévus.
- DHCP Snooping, DAI, RA Guard et autres protections sont testés selon les capacités du matériel.
- ICMP/ICMPv6 requis n'est pas bloqué aveuglément.
- Les journaux, la synchronisation horaire et la procédure d'escalade sont disponibles.

**Exploitation**
- IPAM et documentation reflètent la configuration réelle.
- Les tests d'acceptation et le retour arrière sont écrits.
- La configuration est sauvegardée et le changement est approuvé.
- Les routes et adresses temporaires sont retirées à la fin de la migration.

> **Danger :** Un plan d'adressage apparemment correct peut provoquer une panne massive s'il contient un chevauchement avec un réseau partenaire, un agrégat qui attire des paquets vers un site incapable de les livrer, ou une route plus spécifique qui détourne des destinations sensibles. Les effets peuvent rester intermittents et difficiles à diagnostiquer parce que certaines destinations fonctionnent tandis que d'autres tombent dans un trou de routage. Avant d'annoncer un nouveau préfixe, valider sa propriété, sa portée, son alignement, ses relations de résumé et les politiques de filtrage ; lors de l'interconnexion de VRF ou d'organisations, vérifier également les chevauchements cachés.

### 3.11. Références techniques

Les documents suivants sont des références utiles pour approfondir les mécanismes décrits. Vérifier toujours le statut, les mises à jour et les recommandations correspondant à l'implémentation utilisée.

- **RFC 4632 — Classless Inter-domain Routing (CIDR)** : agrégation et routage sans classe. https://www.rfc-editor.org/rfc/rfc4632
- **RFC 1918 — Address Allocation for Private Internets** : blocs IPv4 privés. https://www.rfc-editor.org/rfc/rfc1918
- **RFC 3021 — Using 31-Bit Prefixes on IPv4 Point-to-Point Links** : exceptions d'adressage des liens point-à-point. https://www.rfc-editor.org/rfc/rfc3021
- **RFC 1812 — Requirements for IP Version 4 Routers** : exigences de comportement des routeurs IPv4. https://www.rfc-editor.org/rfc/rfc1812
- **RFC 2131 — Dynamic Host Configuration Protocol** : mécanismes DHCPv4. https://www.rfc-editor.org/rfc/rfc2131
- **RFC 826 — Address Resolution Protocol** : résolution IPv4 vers Ethernet. https://www.rfc-editor.org/rfc/rfc826
- **RFC 3022 — Traditional IP Network Address Translator** : NAT/NAPT et limites. https://www.rfc-editor.org/rfc/rfc3022
- **IANA — IPv4 Special-Purpose Address Registry** : portée et statut des blocs spéciaux. https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml
- **Cisco — IP Addressing Configuration Guide** : syntaxe et comportements propres à IOS/IOS XE. https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_config-ipv4-addr-0.html

## Points à retenir

- **Le préfixe est la base du calcul et du routage.** Il faut maîtriser la frontière binaire, CIDR, VLSM, l'agrégation et le *longest prefix match*. La route la plus spécifique gagne dans la table de transfert ; une route agrégée ne garantit pas que chaque destination qu'elle couvre est réellement joignable.
- **Un plan d'adressage doit être hiérarchique, unique dans les contextes destinés à communiquer et maintenu dans un IPAM.** Les plages IPv4 privées, partagées, de documentation et spéciales ne sont pas interchangeables. Les chevauchements, les scopes DHCP incohérents et les résumés erronés sont des risques d'exploitation majeurs.
- **IPv4 et IPv6 exigent une conception et un dépannage propres, même en double pile.** ARP, DHCPv4, NAT et broadcast ont des rôles différents de NDP, SLAAC, Router Advertisements et ICMPv6. Les configurations doivent être vérifiées dans la table de routage et le plan de transfert, puis testées de bout en bout avec les routes retour, les services et les contrôles de sécurité.
