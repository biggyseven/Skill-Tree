# Routage statique & tables - Débutant

**Niveau :** Débutant

Le routage IP est la fonction qui permet à un paquet de quitter son réseau d’origine et de traverser un ou plusieurs routeurs afin d’atteindre un réseau de destination. Dans un petit réseau, deux ordinateurs placés dans le même sous-réseau peuvent généralement communiquer directement sur leur réseau local. Dès que la destination se trouve dans un autre sous-réseau, l’équipement source remet le paquet à une passerelle, le plus souvent un routeur ou un commutateur de couche 3. Cet équipement examine la destination IP et décide par quelle interface et vers quel prochain saut le paquet doit être transmis.

Une table de routage est la base de données qui rassemble les chemins connus par un équipement de couche 3. Elle peut contenir des réseaux directement connectés, des routes ajoutées manuellement par un administrateur, des routes apprises grâce à un protocole dynamique et, lorsque cela est nécessaire, une route par défaut. Le routeur ne mémorise pas nécessairement chaque adresse IP individuelle : il travaille le plus souvent avec des préfixes, par exemple `192.168.20.0/24`, qui représentent un ensemble d’adresses. Pour choisir un chemin, il compare l’adresse de destination du paquet aux préfixes de sa table et applique des règles de sélection.

Le routage statique consiste à configurer explicitement un chemin vers une destination. L’administrateur indique le réseau à atteindre, son masque ou sa longueur de préfixe, puis le prochain saut ou l’interface de sortie. Cette méthode est simple, prévisible et utile pour les petits réseaux, les réseaux de bordure, les routes par défaut et certains chemins de secours. Elle demande toutefois une maintenance manuelle : si la topologie change, les routes statiques ne se réorganisent pas automatiquement comme peuvent le faire les protocoles dynamiques. Comprendre les routes connectées, les routes statiques, les routes par défaut et la consultation de la table constitue donc un socle indispensable avant d’étudier OSPF, EIGRP ou BGP.

> **Analogie** : Imagine un service de livraison qui doit acheminer des colis vers différentes villes. Le nom de la ville sur l’étiquette correspond à l’adresse IP de destination. La table de routage est un répertoire d’itinéraires : elle associe des régions à une sortie, à une route ou à un prochain centre de distribution. Lorsque le colis arrive à un centre, celui-ci ne connaît pas nécessairement toutes les rues de la ville finale. Il choisit seulement le prochain centre auquel confier le colis. Le centre suivant répète ensuite la décision jusqu’à ce que le colis arrive à destination.
>
> Une route statique ressemble à une instruction écrite à l’avance : « pour les colis destinés à la région Nord, envoie-les au centre B ». L’instruction reste en vigueur tant que l’administrateur ne la modifie pas ou qu’un mécanisme prévu ne la retire pas. Si la route vers le centre B est bloquée, une instruction statique simple ne sait pas forcément qu’il faut utiliser le centre C. Un itinéraire de secours doit être prévu explicitement, ou un protocole de routage dynamique doit apprendre le nouvel itinéraire.
>
> Le répertoire peut contenir une instruction générale, par exemple « pour toutes les destinations que tu ne connais pas, envoie le colis au centre de sortie ». C’est l’équivalent de la route par défaut `0.0.0.0/0`. Il peut aussi contenir une instruction très précise, par exemple « pour cette seule adresse, utilise tel centre ». Cette route d’hôte, souvent représentée par `/32` en IPv4, est plus spécifique qu’une route vers tout un réseau. Lorsque plusieurs instructions correspondent, le routeur retient normalement la plus spécifique, car elle décrit plus précisément la destination.


## 1. La théorie et les algorithmes

### 1.1. Pourquoi le routage est nécessaire

Une adresse IP comporte une partie réseau et une partie hôte, déterminées par le masque ou le préfixe. Par exemple, avec `192.168.10.25/24`, le préfixe réseau est `192.168.10.0/24` et l’adresse appartient au réseau `192.168.10.0/24`. Un ordinateur utilisant `192.168.10.50/24` se trouve dans le même sous-réseau. En revanche, un ordinateur `192.168.20.50/24` appartient à un autre réseau.

Pour une destination locale, l’hôte source peut résoudre l’adresse MAC de la destination avec ARP en IPv4 et lui transmettre une trame Ethernet directement. Pour une destination distante, il ne recherche normalement pas la MAC de l’hôte distant. Il recherche plutôt l’adresse MAC de sa passerelle par défaut et envoie la trame à cette passerelle. Le paquet IP conserve l’adresse IP de destination finale ; les adresses MAC de la trame changent à chaque liaison de couche 2 traversée.

Le routeur reçoit le paquet, vérifie les informations utiles à son transfert, diminue le TTL IPv4, puis consulte sa table de routage. Si un chemin est disponible, il choisit le prochain saut et transmet le paquet sur l’interface correspondante. Si aucun chemin utilisable n’existe et qu’aucune route par défaut ne peut être appliquée, le paquet est généralement abandonné. Le routeur peut envoyer un message ICMP Destination Unreachable selon le cas et la politique configurée.

### 1.2. Les éléments d’une table de routage

Une entrée de routage décrit au minimum une destination et un moyen de l’atteindre. Selon le système et la commande utilisée, une ligne peut afficher :

- **Le préfixe de destination** : réseau ou adresse hôte que la route permet d’atteindre.
- **Le masque ou la longueur de préfixe** : nombre de bits utilisés pour déterminer la correspondance.
- **La source de la route** : interface connectée, configuration statique ou protocole dynamique.
- **Le prochain saut** : adresse IP du routeur auquel envoyer le paquet ensuite, si un prochain saut est nécessaire.
- **L’interface de sortie** : interface utilisée pour transmettre le paquet.
- **La distance administrative** : valeur de préférence utilisée par de nombreux systèmes Cisco pour comparer les sources de routes vers une même destination.
- **La métrique** : coût propre à la source ou au protocole de routage.

Une table de routage n’est pas une simple liste ordonnée de destinations. Le routeur doit d’abord déterminer quelles routes correspondent au paquet. Ensuite, il choisit selon les règles de sélection du système. Les paramètres affichés peuvent varier entre Cisco IOS, IOS XE, les systèmes Linux et d’autres plateformes, mais les principes fondamentaux restent semblables.

### 1.3. Les routes directement connectées

Lorsqu’une interface de routeur est configurée avec une adresse IP et un masque valides et qu’elle est opérationnelle, le réseau auquel cette interface appartient peut être installé comme route directement connectée. Le routeur n’a pas besoin d’une route statique vers ce réseau : il sait qu’il peut y accéder directement par cette interface.

Exemple :

```text
Interface G0/0 : 192.168.10.1/24
Réseau connecté : 192.168.10.0/24

Interface G0/1 : 10.0.12.1/30
Réseau connecté : 10.0.12.0/30
```

Si les deux interfaces sont actives, le routeur peut généralement atteindre les hôtes de ces deux réseaux directement connectés. Les routes connectées dépendent de l’état de l’interface et de la configuration de l’adresse. Si l’interface tombe, la route connectée correspondante peut être retirée de la table. Ce comportement est différent d’une route statique ordinaire, qui reste configurée tant que l’administrateur ne la supprime pas, même si son chemin devient inutilisable selon les paramètres et le type de route.

Les équipements Cisco affichent souvent `C` pour une route connectée et `L` pour une route locale représentant l’adresse IP exacte configurée sur une interface. Par exemple, une interface `192.168.10.1/24` peut produire une route connectée `192.168.10.0/24` et une route locale `192.168.10.1/32`. La route locale permet au routeur d’identifier les paquets dont la destination est l’une de ses propres adresses.

### 1.4. Routes statiques : définition et usage

Une route statique est créée par une commande explicite dans la configuration de l’équipement. Elle indique au routeur comment joindre un réseau ou une adresse précise. Sur Cisco IOS classique, la commande de base est :

```cisco
ip route <réseau-destination> <masque> <prochain-saut>
```

Par exemple :

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.12.2
```

Cette instruction signifie : pour atteindre `192.168.30.0/24`, transmets les paquets au prochain saut `10.0.12.2`. Le prochain saut doit être joignable grâce à la connectivité existante et aux routes installées. Une route statique ne crée pas à elle seule une liaison physique et ne garantit pas que le voisin répondra ; elle indique seulement le chemin souhaité.

Les routes statiques sont souvent utilisées quand :

- le réseau est petit et peu susceptible de changer ;
- une succursale dispose d’un seul chemin vers le siège ;
- un routeur a besoin d’une route par défaut vers son fournisseur ;
- un chemin de secours est configuré avec une distance administrative plus élevée ;
- l’administrateur veut maîtriser explicitement le chemin vers un préfixe particulier ;
- certaines routes doivent être installées sans mettre en place un protocole dynamique.

Elles comportent aussi des limites. Si la topologie change sans que l’administrateur ou un mécanisme de suivi ne modifie la route, celle-ci peut devenir inutilisable ou continuer à pointer vers un chemin qui n’est plus optimal. Dans les réseaux étendus, la maintenance manuelle d’un grand nombre de routes peut devenir coûteuse et source d’erreurs.

### 1.5. Route avec prochain saut, route avec interface de sortie et route entièrement spécifiée

Une route statique peut être définie de plusieurs façons.

**Route avec prochain saut :**

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.12.2
```

Le routeur connaît l’adresse IP du prochain routeur. Il doit déterminer comment atteindre cette adresse. Sur un réseau Ethernet multiaccès, il utilise normalement la résolution de couche 2, par exemple ARP pour IPv4, pour obtenir l’adresse MAC du prochain saut.

**Route avec interface de sortie :**

```cisco
ip route 192.168.30.0 255.255.255.0 GigabitEthernet0/1
```

Cette forme indique l’interface par laquelle transmettre les paquets. Elle convient particulièrement à certains liens point-à-point. Sur un réseau Ethernet multiaccès, une route qui ne précise que l’interface de sortie peut provoquer une résolution ARP pour chaque destination finale, plutôt que seulement pour le routeur voisin, selon la plateforme et le contexte. Cela peut créer de nombreuses entrées ARP et être moins efficace qu’une route spécifiant un prochain saut.

**Route entièrement spécifiée :**

```cisco
ip route 192.168.30.0 255.255.255.0 GigabitEthernet0/1 10.0.12.2
```

Cette forme précise à la fois l’interface et le prochain saut. Elle peut être utile lorsqu’il faut lever une ambiguïté de résolution ou indiquer précisément le lien utilisé. Sa prise en charge et ses détails dépendent du système d’exploitation réseau.

Le choix entre ces formes doit correspondre à la topologie réelle. Pour une liaison Ethernet vers un routeur adjacent, la route avec prochain saut est généralement claire et facile à maintenir. Pour une liaison point-à-point, une route indiquant l’interface de sortie peut être appropriée, car il n’y a normalement qu’un seul équipement joignable sur cette liaison.

### 1.6. Route par défaut

Une route par défaut sert de solution de dernier recours lorsqu’aucune route plus spécifique ne correspond à la destination. En IPv4, elle est représentée par `0.0.0.0/0`. Le préfixe `/0` contient zéro bit significatif, donc il peut correspondre à toute destination IPv4.

Exemple :

```cisco
ip route 0.0.0.0 0.0.0.0 10.0.12.2
```

Cette route envoie vers `10.0.12.2` le trafic destiné aux réseaux qui ne sont pas couverts par une route plus spécifique. Elle est courante sur les routeurs de succursales qui disposent d’un seul chemin de sortie vers le siège ou un fournisseur d’accès.

Une route par défaut ne doit pas être confondue avec une route vers un réseau directement connecté. Elle ne prouve pas que l’ensemble d’Internet est joignable ; elle donne simplement une destination de prochain saut pour les réseaux autrement inconnus. Si le prochain saut ne peut pas acheminer le paquet, l’échec se produira plus loin dans le chemin.

La route par défaut IPv6 s’écrit généralement `::/0`. Même si le principe est similaire, les commandes IPv6 et les mécanismes voisins sont différents des commandes IPv4. Dans ce cours d’introduction, les commandes principales se concentrent sur IPv4 Cisco IOS classique.

### 1.7. Comprendre la recherche par préfixe le plus long

Lorsqu’un paquet doit être transféré, le routeur compare son adresse IP de destination aux préfixes présents dans sa base de transfert. Plusieurs routes peuvent correspondre à la même adresse. Le principe appelé **Longest Prefix Match** (LPM), ou correspondance avec le préfixe le plus long, sélectionne le préfixe correspondant qui possède le plus grand nombre de bits significatifs.

Prenons une table illustrative :

| Préfixe | Signification |
|---|---|
| `0.0.0.0/0` | Route par défaut, toutes les destinations IPv4 en l’absence de route plus spécifique |
| `10.0.0.0/8` | Réseau 10.0.0.0 à l’échelle du préfixe /8 |
| `10.20.0.0/16` | Sous-ensemble plus précis du réseau 10.0.0.0/8 |
| `10.20.30.0/24` | Sous-réseau encore plus précis |
| `10.20.30.45/32` | Une seule adresse IPv4 |

Pour un paquet destiné à `10.20.30.45`, plusieurs entrées peuvent correspondre. La route `/32` est la plus spécifique, puis vient `/24`, puis `/16`, puis `/8`, et enfin `/0`. Si la route `/32` est installée et utilisable, elle l’emporte en raison de son préfixe plus long. C’est une règle de correspondance fondamentale.

Le choix par préfixe le plus long est distinct de la distance administrative. Une route statique `/24` ne sera pas remplacée pour un paquet particulier par une route dynamique `/16` simplement parce que la route statique est plus préférée comme source. Le `/24` correspond plus précisément à la destination. La distance administrative sert principalement à choisir quelle source de routage fournit l’entrée retenue pour un même préfixe, tandis que le LPM sélectionne la route la plus spécifique parmi les préfixes correspondants.

### 1.8. Distance administrative et métrique

Sur les systèmes Cisco, la distance administrative (AD) est une mesure de préférence utilisée pour départager les sources de routes vers une même destination. Les valeurs exactes dépendent du type de route, de l’implémentation et d’éventuelles modifications de configuration.

Quelques valeurs Cisco IOS typiques sont :

| Source de route | Distance administrative courante |
|---|---:|
| Connectée | 0 |
| Statique | 1 |
| EIGRP interne | 90 |
| OSPF | 110 |
| RIP | 120 |
| EIGRP externe | 170 |

Ces valeurs sont des repères, pas des constantes universelles. Un administrateur peut les modifier, et d’autres systèmes d’exploitation utilisent des modèles de préférence différents. La distance administrative n’est pas transportée comme une qualité universelle du chemin : elle sert à départager les sources au sein de l’équipement.

La métrique, quant à elle, appartient généralement à un protocole ou à une méthode de calcul. Par exemple, OSPF utilise un coût, EIGRP une métrique composite et RIP un nombre de sauts. Il n’est pas pertinent de comparer directement une métrique OSPF à une métrique EIGRP. En général, le routeur compare d’abord les routes candidates selon les règles de préfixe et de source applicables, puis les critères propres à la source contribuent à choisir l’entrée qui peut être installée.

Pour un débutant, la distinction essentielle est :

- **Préfixe le plus long** : quelle route correspond le mieux à l’adresse de destination ?
- **Distance administrative** : de quelle source l’équipement préfère-t-il apprendre ce même préfixe ?
- **Métrique** : quel chemin préfère le protocole ou la source de routage parmi ses candidats ?

### 1.9. RIB et FIB : table de routage et table de transfert

Le terme « table de routage » est souvent utilisé pour parler de plusieurs structures qui ont pourtant des rôles distincts.

La **Routing Information Base** (RIB) est la base de routes utilisée par le plan de contrôle. Elle contient des informations sur les routes candidates et la sélection du meilleur chemin. Les routes peuvent provenir de configurations statiques, de protocoles dynamiques ou d’interfaces directement connectées.

La **Forwarding Information Base** (FIB) est la structure optimisée utilisée par le plan de transfert pour décider rapidement où envoyer chaque paquet. Selon la plateforme, une partie de cette structure peut être programmée dans des composants matériels ou accélérateurs de transfert.

La distinction exacte varie avec l’architecture de l’équipement. Sur un petit routeur logiciel, certaines fonctions peuvent être plus étroitement liées. Sur un routeur ou commutateur de performance, la RIB et la FIB représentent généralement des structures conceptuellement distinctes.

Une route présente dans un affichage de contrôle ne garantit pas toujours que le transfert matériel est dans l’état attendu. Dans des scénarios avancés, il faut examiner aussi bien la RIB que la FIB et l’état de programmation du matériel. Dans un laboratoire débutant, les commandes `show ip route` et les tests de connectivité constituent néanmoins un bon point de départ.

### 1.10. Comment un routeur transfère un paquet

Le transfert d’un paquet IP peut être présenté de façon simplifiée en plusieurs étapes :

1. Le routeur reçoit une trame sur une interface.
2. Il vérifie les informations nécessaires pour déterminer si le paquet est valide et s’il doit être traité localement ou transféré.
3. Il examine l’adresse IP de destination.
4. Il cherche les préfixes correspondants dans les informations de transfert.
5. Il choisit la route applicable, généralement la plus spécifique.
6. Il détermine le prochain saut et l’interface de sortie.
7. Si nécessaire, il résout l’adresse de couche 2 du prochain saut, par exemple avec ARP en IPv4 sur Ethernet.
8. Il prépare une nouvelle trame de couche 2 sur le réseau de sortie.
9. Il transmet le paquet en respectant les règles de TTL, de MTU et de traitement associées.

L’adresse IP de destination finale ne change généralement pas au cours du routage ordinaire. En revanche, la trame Ethernet utilisée sur chaque segment est reconstruite avec une adresse MAC source correspondant à l’interface d’émission et une adresse MAC destination correspondant au prochain saut de couche 2. Cette distinction entre adresse IP de bout en bout et adresses MAC par segment explique pourquoi le routeur peut transférer un paquet d’un réseau vers un autre sans connaître directement la MAC du terminal final distant.

### 1.11. Exemple de table de routage

Supposons qu’un routeur R1 possède les interfaces suivantes :

| Interface | Adresse | Réseau |
|---|---|---|
| G0/0 | `192.168.10.1/24` | `192.168.10.0/24` |
| G0/1 | `10.0.12.1/30` | `10.0.12.0/30` |

Les réseaux `192.168.10.0/24` et `10.0.12.0/30` sont directement connectés lorsque leurs interfaces sont opérationnelles. R1 peut alors avoir besoin d’une route vers `192.168.20.0/24`, qui se trouve derrière un routeur R2 ayant l’adresse de transit `10.0.12.2`.

La route statique pourrait être :

```cisco
ip route 192.168.20.0 255.255.255.0 10.0.12.2
```

Une route par défaut éventuelle pourrait être :

```cisco
ip route 0.0.0.0 0.0.0.0 10.0.12.2
```

La première route est spécifique à `192.168.20.0/24`. La seconde peut couvrir d’autres destinations, si elles ne correspondent à aucune route plus spécifique. Si un paquet vise `192.168.20.25`, R1 choisira la route `/24` plutôt que la route par défaut `/0`.

### 1.12. Route statique de secours

Il est possible de configurer une route statique dont la distance administrative est supérieure à celle d’une autre route vers la même destination. On parle souvent de **route statique flottante**. Elle peut servir de route de secours si la route principale disparaît de la table de routage.

Exemple de principe :

```cisco
ip route 192.168.20.0 255.255.255.0 10.0.12.2
ip route 192.168.20.0 255.255.255.0 10.0.13.2 10
```

La première route a la distance administrative statique par défaut sur Cisco IOS classique. La seconde utilise une distance plus élevée, ici `10`, et ne devient normalement le choix retenu pour ce préfixe que si aucune route plus préférée équivalente n’est installée.

Cette configuration ne garantit cependant pas que la panne d’un lien distant soit détectée. Une route statique peut rester installée si l’interface locale demeure active alors que le chemin situé plus loin est défaillant. Pour assurer une bascule basée sur la disponibilité réelle, il peut être nécessaire de recourir à un mécanisme de suivi, comme IP SLA avec tracking, à une détection de liaison adéquate ou à un protocole dynamique.

### 1.13. Route récursive

Une route statique indiquant seulement un prochain saut dépend souvent d’une recherche récursive. Le routeur doit d’abord déterminer comment atteindre ce prochain saut, puis utiliser le résultat pour transmettre le paquet vers la destination finale.

Exemple :

```cisco
ip route 192.168.40.0 255.255.255.0 10.0.12.2
```

Pour utiliser cette route, le routeur doit également disposer d’un moyen d’atteindre `10.0.12.2`. Une route connectée vers `10.0.12.0/30` peut suffire. Si le prochain saut ne peut pas être résolu à travers une route opérationnelle, la route statique peut ne pas être installée ou ne pas être utilisable, selon la plateforme et le type d’entrée.

La résolution récursive est utile, mais les dépendances doivent être comprises. Une route peut dépendre d’une autre route et former une chaîne de résolution. Dans les configurations plus complexes, il faut éviter les dépendances circulaires et s’assurer que l’adresse du prochain saut est bien atteignable indépendamment de la destination annoncée par la route elle-même.

### 1.14. Adresse réseau, masque et préfixe

Pour créer une route, il faut préciser le réseau destination et son masque. Le masque détermine quels bits de l’adresse font partie du préfixe réseau.

Par exemple :

- `192.168.20.0 255.255.255.0` correspond à `192.168.20.0/24`.
- `10.10.0.0 255.255.0.0` correspond à `10.10.0.0/16`.
- `172.16.10.0 255.255.255.192` correspond à `172.16.10.0/26`.

Le préfixe de destination doit être correctement aligné avec son masque. Une faute de masque peut créer une route trop large ou trop spécifique. Une route trop large peut détourner du trafic destiné à d’autres sous-réseaux ; une route trop spécifique peut rendre certains réseaux inaccessibles ou conduire à un chemin inattendu.

Lorsque l’on travaille avec des routes statiques, il est utile de calculer et noter les réseaux, les masques, les plages d’adresses et les prochains sauts avant d’entrer les commandes. Une simple erreur de `/24` à la place de `/16` peut modifier le comportement d’une grande partie du réseau.

### 1.15. Routes d’hôte et routes de rejet

Une route d’hôte désigne une seule adresse IP. En IPv4, elle est généralement représentée par un préfixe `/32`. Elle peut servir à contrôler précisément le chemin vers un serveur, un équipement de gestion ou une adresse particulière.

Exemple :

```cisco
ip route 192.168.20.50 255.255.255.255 10.0.12.2
```

Cette route concerne uniquement `192.168.20.50`, pas l’ensemble du réseau `192.168.20.0/24`. En raison de sa longueur de préfixe, elle est préférée à une route moins spécifique qui couvre également cette adresse.

Une route de rejet, parfois configurée avec une interface de type `Null0`, permet d’abandonner intentionnellement certains paquets. Elle est souvent utilisée dans les conceptions de résumé de routes ou pour appliquer une politique de routage. Par exemple :

```cisco
ip route 192.168.0.0 255.255.0.0 Null0
```

Cette route ne doit pas être ajoutée sans comprendre son interaction avec les routes plus spécifiques. Elle peut être utile pour empêcher des boucles vers des destinations non connues dans un agrégat, mais une route de rejet trop large peut aussi supprimer du trafic légitime. La disponibilité de `Null0` et la syntaxe exacte dépendent de la plateforme.

### 1.16. Route statique IPv6 : aperçu

Le principe des routes statiques existe également en IPv6. Une route IPv6 utilise un préfixe comme `2001:db8:20::/64`, un prochain saut IPv6 ou une interface de sortie. L’adresse IPv6 de documentation `2001:db8::/32` est réservée aux exemples et ne doit pas être utilisée comme plan d’adressage public en production.

Un exemple de route IPv6 Cisco IOS classique est :

```cisco
ipv6 route 2001:db8:20::/64 2001:db8:12::2
```

La syntaxe précise dépend de la plateforme. Le routage IPv6 nécessite également l’activation du transfert IPv6 sur certains équipements, par exemple avec `ipv6 unicast-routing` sur Cisco IOS classique, et des interfaces convenablement adressées. Les mécanismes de résolution de couche 2 pour IPv6 utilisent NDP plutôt qu’ARP.

Les principes de préfixe le plus long, de route par défaut et de séparation entre route configurée et chemin réellement disponible s’appliquent aussi à IPv6, mais les détails de configuration et de voisinage doivent être vérifiés séparément.

### 1.17. Table de routage et plan de contrôle

La table de routage est généralement alimentée par plusieurs sources : interfaces connectées, routes statiques et protocoles dynamiques. Le système doit décider quelles routes candidates sont installées pour chaque préfixe et quelles entrées sont utilisées au transfert.

Les routes connectées sont généralement générées par l’état des interfaces. Les routes statiques viennent de la configuration. Les protocoles dynamiques comme OSPF, EIGRP ou BGP apprennent et calculent les routes suivant leurs règles propres. Les routes peuvent être filtrées ou exclues de l’installation selon la politique de l’équipement.

Il faut comprendre qu’une route présente dans la configuration ne signifie pas nécessairement qu’elle apparaît comme route active dans la table. Le prochain saut peut être inaccessible, la route peut perdre la sélection face à une entrée plus préférée de même préfixe, ou la syntaxe peut être incorrecte. À l’inverse, une route directement connectée peut apparaître automatiquement sans commande `ip route` parce qu’elle est créée par l’adresse de l’interface.

### 1.18. Égalité de préfixe et routes multiples

Un routeur peut connaître plusieurs routes vers le même préfixe. Il doit alors appliquer ses règles de sélection. Sur Cisco IOS, si une route statique et une route dynamique couvrent exactement le même préfixe et que les autres critères sont comparables, la distance administrative peut départager les sources. Une route statique standard a généralement une distance de 1, ce qui la rend plus préférée que plusieurs routes dynamiques par défaut.

Cette règle ne doit pas être confondue avec le préfixe le plus long. Une route statique vers `10.20.0.0/16` ne prendra pas automatiquement le dessus sur une route OSPF vers `10.20.30.0/24` pour une destination `10.20.30.45`, car la route `/24` est plus spécifique.

Une bonne lecture de table doit donc commencer par les préfixes qui correspondent à la destination. Ensuite seulement il faut comparer les sources et les critères de sélection pour une route de même préfixe ou un ensemble de chemins candidats du même protocole.

### 1.19. Principes de conception

Les routes statiques doivent être simples à comprendre et faciles à maintenir. Il est recommandé de conserver un plan d’adressage documenté, de nommer les routes si le système le permet, de noter le rôle de chaque prochain saut et de garder une copie de la configuration avant les changements.

Dans un réseau de succursales, une route par défaut vers le siège peut suffire si le site ne possède qu’une sortie. Dans un réseau possédant plusieurs chemins, il faut évaluer les risques de panne, de routage asymétrique et de chemins non optimaux. Une route statique primaire et une route flottante secondaire ne sont utiles que si le mécanisme de détection détecte les pannes pertinentes.

Il est également préférable de limiter l’utilisation de routes statiques très larges lorsqu’elles peuvent détourner du trafic non prévu. Les résumés et les routes de rejet sont des outils de conception, pas de simples raccourcis. Il faut savoir quelles destinations sont couvertes, quelles routes plus spécifiques existent et ce qui se passera si une destination annoncée devient indisponible.

### 1.20. Résumé du processus de sélection

Lorsqu’un paquet arrive, le routeur doit déterminer si sa destination lui est propre ou si elle doit être transférée. Pour un paquet à transférer, il cherche une route utilisable vers la destination. Il retient les routes dont le préfixe correspond, puis favorise le préfixe le plus long. Si plusieurs candidats identiques restent, les critères propres à la source, la distance administrative, les métriques et les règles d’installation peuvent intervenir.

Une fois la route sélectionnée, le routeur détermine le prochain saut et l’interface de sortie. Il doit pouvoir résoudre les informations de couche 2 nécessaires sur le lien de sortie. Si aucun chemin valable n’est disponible, le paquet est abandonné et le routeur peut retourner une erreur ICMP selon la situation et la configuration.

> **Piège :** Ne pense pas qu’une route statique est automatiquement utilisée simplement parce qu’elle existe dans `running-config`. Elle doit être valide, son prochain saut doit être résoluble et elle doit être retenue par le mécanisme d’installation. Ne confonds pas non plus la distance administrative avec le préfixe le plus long : une route moins spécifique ne gagne pas uniquement parce qu’elle provient d’une source plus préférée.

```text
                           Paquet reçu
                                |
                                v
                     Lire l'IP de destination
                                |
                                v
                 Chercher les préfixes correspondants
                                |
                                v
                    Retenir le préfixe le plus long
                                |
                                v
             Plusieurs candidats de même préfixe ?
                       /                  \
                     Oui                  Non
                      |                    |
                      v                    v
          Comparer les critères          Route retenue
          de source et métrique              |
                      |                      v
                      +--------------> Déterminer le prochain saut
                                             |
                                             v
                                     Résoudre L2 si nécessaire
                                             |
                                             v
                                       Transmettre le paquet
```


## 2. Configuration et Pratique

### 2.1. Topologie du laboratoire

Le laboratoire comporte trois routeurs Cisco IOS : R1, R2 et R3. R1 héberge le LAN `192.168.10.0/24`. R2 constitue le routeur intermédiaire. R3 héberge le LAN `192.168.30.0/24`. Les deux liens de transit utilisent des sous-réseaux `/30`.

| Routeur | Interface | Adresse | Rôle |
|---|---|---|---|
| R1 | G0/0 | `192.168.10.1/24` | LAN de R1 |
| R1 | G0/1 | `10.0.12.1/30` | Transit vers R2 |
| R2 | G0/0 | `10.0.12.2/30` | Transit vers R1 |
| R2 | G0/1 | `10.0.23.2/30` | Transit vers R3 |
| R3 | G0/0 | `192.168.30.1/24` | LAN de R3 |
| R3 | G0/1 | `10.0.23.3/30` | Transit vers R2 |

```text
 LAN R1                                      LAN R3
192.168.10.0/24                           192.168.30.0/24
     |                                           |
     | G0/0                               G0/0    |
 +-------+       10.0.12.0/30       +-------+    |
 |  R1   |--------------------------|  R2   |    |
 +-------+                          +-------+    |
     G0/1                               G0/1     |
                                          \      |
                                           \ 10.0.23.0/30
                                            \    |
                                             +-------+
                                             |  R3   |
                                             +-------+
```

Le but est que R1 puisse joindre le LAN de R3, et que R3 puisse joindre le LAN de R1. Les routes doivent être configurées dans les deux directions, sauf si une route par défaut existante couvre correctement le réseau distant. Une route aller sans route de retour ne suffit pas pour obtenir une communication bidirectionnelle.

### 2.2. Configuration des interfaces de R1

```cisco
hostname R1

interface GigabitEthernet0/0
 description LAN_R1
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface GigabitEthernet0/1
 description TRANSIT_VERS_R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
```

`hostname` identifie le routeur dans l’invite de commande et dans les journaux. Chaque interface reçoit une adresse IP et un masque. `no shutdown` permet d’activer administrativement l’interface. Le nom exact des interfaces varie suivant le modèle de routeur, le simulateur et le système d’exploitation réseau.

Après la configuration, la commande `show ip interface brief` permet de vérifier les états des interfaces et les adresses configurées. Il faut attendre que les interfaces physiques et les protocoles de liaison soient opérationnels avant de conclure que le routage est en cause.

### 2.3. Configuration des interfaces de R2

```cisco
hostname R2

interface GigabitEthernet0/0
 description TRANSIT_VERS_R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown

interface GigabitEthernet0/1
 description TRANSIT_VERS_R3
 ip address 10.0.23.2 255.255.255.252
 no shutdown
```

R2 est le routeur intermédiaire. Ses deux réseaux de transit sont directement connectés lorsque les interfaces sont opérationnelles. Il n’a pas besoin de route statique vers les réseaux de transit eux-mêmes, mais il doit connaître les LAN distants au moyen de routes statiques, dynamiques ou d’une combinaison des deux.

### 2.4. Configuration des interfaces de R3

```cisco
hostname R3

interface GigabitEthernet0/0
 description LAN_R3
 ip address 192.168.30.1 255.255.255.0
 no shutdown

interface GigabitEthernet0/1
 description TRANSIT_VERS_R2
 ip address 10.0.23.3 255.255.255.252
 no shutdown
```

Les adresses des interfaces de transit doivent se trouver dans le même sous-réseau de chaque côté. Sur le lien `10.0.23.0/30`, `10.0.23.2` et `10.0.23.3` sont les deux adresses d’hôte utilisables dans ce plan d’adressage.

### 2.5. Ajouter les routes statiques

Sur R1, une route vers le LAN de R3 est nécessaire :

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.12.2
```

La commande indique à R1 de transmettre le trafic destiné à `192.168.30.0/24` vers R2, à l’adresse `10.0.12.2`.

Sur R2, deux routes sont nécessaires pour joindre les LAN utilisateurs situés derrière R1 et R3 :

```cisco
ip route 192.168.10.0 255.255.255.0 10.0.12.1
ip route 192.168.30.0 255.255.255.0 10.0.23.3
```

Sur R3, il faut ajouter une route de retour vers le LAN de R1 :

```cisco
ip route 192.168.10.0 255.255.255.0 10.0.23.2
```

Ces routes permettent à chaque routeur de connaître les réseaux distants. R2 n’a pas besoin de routes statiques vers `10.0.12.0/30` et `10.0.23.0/30` car ces préfixes sont directement connectés. Les routes ne doivent toutefois pas être configurées sans contrôler d’abord le plan d’adressage réel.

### 2.6. Configuration complète de R1

```cisco
hostname R1

interface GigabitEthernet0/0
 description LAN_R1
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface GigabitEthernet0/1
 description TRANSIT_VERS_R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown

! Route vers le LAN distant de R3 via R2
ip route 192.168.30.0 255.255.255.0 10.0.12.2

end
copy running-config startup-config
```

La ligne `!` est un commentaire dans la configuration Cisco. `end` quitte le mode de configuration. `copy running-config startup-config` sauvegarde la configuration active dans la configuration de démarrage sur les plateformes qui utilisent cette syntaxe. Dans un laboratoire, il est utile de sauvegarder uniquement après avoir vérifié que les changements fonctionnent.

### 2.7. Route par défaut sur un routeur de bordure

Si R1 est une succursale qui n’a qu’un seul chemin de sortie, il peut être plus simple d’utiliser une route par défaut vers R2 :

```cisco
ip route 0.0.0.0 0.0.0.0 10.0.12.2
```

Cette route permet à R1 d’envoyer au prochain saut les paquets pour lesquels aucune route plus spécifique n’existe. Dans une architecture réelle, R2 doit ensuite posséder une route appropriée vers les destinations concernées, souvent vers le siège ou le fournisseur. Si R2 n’a pas de route valable, le trafic sera simplement envoyé au mauvais endroit ou supprimé plus loin.

Une route par défaut est pratique, mais elle peut masquer l’absence de routes plus précises. Il faut savoir quelles destinations elle couvre et veiller à ce que le prochain saut fournisse réellement le service attendu.

### 2.8. Vérifier la configuration

Après les changements, exécute les commandes suivantes sur chaque routeur :

```cisco
show ip interface brief
show running-config
show ip route
show ip route static
```

`show ip interface brief` permet de vérifier les adresses et les états des interfaces. `show running-config` permet de relire la configuration active. `show ip route` affiche la table de routage. `show ip route static` filtre les routes statiques installées sur les versions qui prennent en charge cette commande.

Sur Cisco IOS, les routes statiques sont souvent marquées par `S`, les routes connectées par `C` et les routes locales par `L`. Une ligne typique de route statique peut ressembler à :

```text
S    192.168.30.0/24 [1/0] via 10.0.12.2
```

La notation exacte varie suivant la version, mais `[1/0]` représente couramment la distance administrative et la métrique associée à la route statique. `via 10.0.12.2` indique le prochain saut.

### 2.9. Vérifier les prochains sauts

Une route avec prochain saut doit pouvoir résoudre ce prochain saut. Dans le laboratoire, R1 doit atteindre `10.0.12.2` sur le réseau de transit directement connecté. La commande suivante permet d’examiner la connectivité de ce voisin :

```cisco
ping 10.0.12.2
```

Si ce ping échoue, il ne faut pas immédiatement incriminer la route vers le LAN de R3. La liaison de transit, l’adressage IP, l’état de l’interface, le câblage ou un filtrage ICMP peuvent être en cause. Un échec de ping ne prouve pas toujours que tous les types de trafic sont bloqués, mais il donne un premier indice.

Vérifie aussi que le prochain saut est effectivement dans le sous-réseau prévu. Une faute de frappe dans une adresse comme `10.0.21.2` au lieu de `10.0.12.2` peut conduire à une route statique qui ne peut pas être résolue.

### 2.10. Tester le transfert de bout en bout

Depuis R1, teste l’interface LAN de R3 :

```cisco
ping 192.168.30.1
traceroute 192.168.30.1
```

Depuis R3, effectue le test inverse :

```cisco
ping 192.168.10.1
traceroute 192.168.10.1
```

Le ping vérifie si des paquets ICMP Echo Request et Echo Reply peuvent traverser le chemin. Le traceroute aide à identifier les routeurs traversés en exploitant les réponses associées au TTL. Les commandes et la sortie peuvent varier selon l’IOS et les paramètres du réseau.

Si le ping fonctionne dans une direction mais pas dans l’autre, examine les routes de retour et les politiques de filtrage. Le routage est bidirectionnel pour une conversation complète : le paquet de requête et la réponse peuvent emprunter des chemins différents, mais chacun doit disposer d’un chemin de retour valide.

### 2.11. Supprimer ou corriger une route

Une route statique peut être retirée avec la forme `no` de la commande utilisée pour la créer. Par exemple :

```cisco
no ip route 192.168.30.0 255.255.255.0 10.0.12.2
```

La syntaxe doit correspondre à la route configurée. Si la route a été créée avec une interface de sortie, une distance administrative ou des options supplémentaires, il faut utiliser la commande de suppression appropriée pour la version IOS en question.

Avant de supprimer une route dans un environnement de production, vérifie quels flux l’utilisent et si une autre route prend le relais. La suppression d’une route par défaut peut interrompre l’accès à des destinations qui n’apparaissent pas explicitement dans la table. Une modification de routage doit être accompagnée d’un plan de vérification et d’un moyen de retour arrière.

### 2.12. Route statique flottante : démonstration

Une route statique flottante peut être configurée avec une distance administrative plus élevée pour servir de secours. Supposons qu’un deuxième chemin de transit vers le même réseau existe via `10.0.13.2`.

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.12.2
ip route 192.168.30.0 255.255.255.0 10.0.13.2 10
```

La route de secours porte une distance administrative de 10, supérieure à la valeur standard de 1 pour une route statique Cisco classique. Elle ne sera normalement préférée que lorsque la route principale du même préfixe n’est plus installée ou qu’une autre politique conduit à la sélectionner.

Cette simple configuration ne détecte pas nécessairement une panne située après le prochain saut. Si `10.0.12.2` reste joignable mais n’achemine plus le trafic vers le LAN de destination, la route principale peut rester active. Des mécanismes de suivi comme IP SLA et object tracking, ou un protocole de routage dynamique, peuvent être nécessaires pour surveiller la disponibilité réelle du chemin.

### 2.13. Sauvegarde et validation

Une fois les routes testées, sauvegarde la configuration si elle doit survivre à un redémarrage. Pour un environnement de production, conserve une copie de la configuration précédente et documente les changements : destination, masque, prochain saut, justification, date et procédure de retour arrière.

Avant la mise en production, vérifie :

- que les interfaces sont opérationnelles ;
- que les réseaux directement connectés sont corrects ;
- que chaque route vise le bon préfixe ;
- que chaque prochain saut est joignable ;
- que les routes de retour existent ;
- que la route par défaut est appropriée ;
- que les tests de bout en bout passent ;
- que la configuration a été sauvegardée après validation.

### 2.14. Utiliser les commandes de diagnostic dans le bon ordre

Un bon dépannage ne commence pas par la modification aléatoire de routes. Il consiste à confirmer successivement l’état des interfaces, la présence des réseaux connectés, l’installation des routes statiques, la résolution du prochain saut puis le transfert du trafic. Cette séquence limite les changements inutiles et rend les causes plus faciles à isoler.

Commence par `show ip interface brief`, puis contrôle la table avec `show ip route`. Si la route n’apparaît pas, vérifie la configuration et le prochain saut. Si elle est installée, effectue un ping vers le prochain saut, puis vers la destination finale. Si le ping direct vers le prochain saut fonctionne mais que le réseau distant échoue, examine les routes du routeur intermédiaire et la route de retour.

Lorsque le problème est plus complexe, des captures ou des commandes de diagnostic plus détaillées peuvent être utiles, mais elles doivent être utilisées avec précaution. Il faut éviter les débogages non ciblés et prolongés sur un équipement déjà chargé.

> **Astuce :** Pour vérifier une route statique, pose-toi toujours trois questions dans cet ordre : « La route apparaît-elle dans `show running-config` ? », « Est-elle installée dans `show ip route` ? », puis « Le prochain saut et le chemin de retour fonctionnent-ils ? ». Cette séquence distingue rapidement une erreur de configuration, un problème d’installation et un problème de transfert.


## 3. Dépannage et Sécurité

### 3.1. La route statique n’apparaît pas dans la table

Une route présente dans la configuration ne sera pas forcément installée. Les causes possibles incluent un prochain saut non résoluble, une interface de sortie inactive, une route concurrente préférée vers le même préfixe ou une erreur de syntaxe.

Contrôle d’abord :

```cisco
show running-config | include ^ip route
show ip route
show ip interface brief
```

La première commande filtre les lignes de routes statiques sur les versions qui supportent cette syntaxe. La deuxième montre les routes installées, et la troisième confirme l’état des interfaces. Si le prochain saut est censé être directement connecté, vérifie son adresse et le réseau de transit.

Une route statique est souvent résolue récursivement. Si son prochain saut dépend lui-même d’une route qui n’existe pas ou qui est devenue invalide, l’entrée peut ne pas apparaître comme route utilisable. Les dépendances doivent donc être examinées jusqu’à une interface directement connectée ou un chemin de résolution valable.

### 3.2. Mauvais masque ou mauvais préfixe

Une erreur de masque peut donner un résultat très différent de celui attendu. Par exemple, une route vers `192.168.30.0/16` au lieu de `/24` couvre un ensemble beaucoup plus large et peut détourner le trafic destiné à d’autres réseaux `192.168.x.x`.

Pour diagnostiquer cette erreur, compare l’adresse et le masque configurés au plan d’adressage documenté. Vérifie aussi les routes plus spécifiques qui peuvent masquer ou limiter l’impact du préfixe incorrect. Une route plus spécifique peut continuer à acheminer certains réseaux correctement tandis que d’autres destinations basculent vers le chemin trop large.

Le contrôle manuel du réseau et du masque, ainsi que la vérification de la table, sont indispensables. Il ne faut pas supposer qu’une route est correcte uniquement parce qu’elle a été saisie sans message d’erreur.

### 3.3. Le prochain saut n’est pas joignable

Si le routeur ne peut pas atteindre le prochain saut, la route statique peut ne pas fonctionner comme prévu. Les causes incluent une adresse erronée, un masque incohérent, une interface inactive, une liaison défaillante ou une route manquante vers le prochain saut.

Test initial :

```cisco
ping 10.0.12.2
show ip arp
show interfaces GigabitEthernet0/1
```

Adapte les adresses et le nom d’interface à ton laboratoire. `show ip arp` permet d’examiner les associations IPv4/MAC connues. Une entrée ARP absente ou incomplète sur un réseau Ethernet peut révéler une difficulté de résolution de couche 2. Toutefois, un ping qui échoue peut également être dû au filtrage ICMP, donc il faut confronter plusieurs observations.

### 3.4. Route aller présente, route retour absente

La cause classique d’une communication unidirectionnelle est la présence d’une route aller sans route retour. R1 peut envoyer un paquet vers le LAN de R3, mais R3 doit également savoir comment joindre l’adresse source du paquet. Si le retour est inconnu, les réponses ne rejoindront pas R1.

Il faut examiner chaque routeur impliqué :

- R1 doit savoir comment atteindre le réseau de destination ;
- R2 doit disposer des routes nécessaires pour acheminer les paquets dans les deux sens ;
- R3 doit savoir comment joindre le réseau source.

Une route par défaut peut satisfaire le besoin de retour si son prochain saut mène effectivement vers le bon domaine. Sinon, des routes plus précises sont nécessaires. Le traceroute dans les deux sens, lorsque cela est possible, aide à localiser l’endroit où le chemin cesse de fonctionner.

### 3.5. Une route par défaut détourne le trafic

Une route `0.0.0.0/0` correspond à toute destination IPv4 qui n’a pas de route plus spécifique. Si le prochain saut est incorrect, une grande variété de trafic peut être dirigée vers un endroit inadapté. Une route par défaut incorrecte peut ainsi affecter l’accès à Internet, à des applications centrales ou à des réseaux distants.

Vérifie sa présence et son prochain saut :

```cisco
show ip route 0.0.0.0
show running-config | include ^ip route 0.0.0.0
```

La syntaxe d’affichage peut varier selon IOS. Il faut aussi vérifier les routes plus spécifiques, car elles peuvent prendre le dessus pour certaines destinations. Dans un réseau d’entreprise, une route par défaut est un élément critique qui doit être documenté et testé après toute modification de topologie.

### 3.6. Conflit entre routes statiques et dynamiques

Un routeur peut recevoir une route vers un préfixe via un protocole dynamique tout en possédant une route statique vers le même préfixe. Il applique ses règles de sélection. Sur Cisco IOS, une route statique standard bénéficie habituellement d’une distance administrative de 1, ce qui lui donne la préférence sur les routes OSPF ou RIP vers le même préfixe, si aucune autre configuration ne modifie ce résultat.

La présence d’une route dynamique plus spécifique peut néanmoins diriger le trafic vers un chemin différent en raison du préfixe le plus long. Il faut donc distinguer le conflit sur un préfixe identique de la coexistence de préfixes différents.

Lorsqu’une route inattendue est installée, compare les préfixes, les sources et les distances administratives. Examine aussi les politiques de redistribution et les filtres si plusieurs protocoles échangent des informations. Ne change pas la distance administrative sans comprendre les conséquences sur les routes de même préfixe.

### 3.7. Sécurité du routage statique

Le routage statique réduit la dépendance aux échanges de contrôle des protocoles dynamiques, mais il ne garantit pas à lui seul la sécurité. Une erreur de configuration peut détourner le trafic, créer une perte de connectivité ou ouvrir un chemin non prévu vers un réseau interne.

Les bonnes pratiques comprennent :

- limiter les personnes autorisées à modifier les routes ;
- protéger les accès administratifs aux routeurs ;
- documenter chaque route et son objectif ;
- vérifier les prochains sauts et les routes de retour ;
- utiliser des ACL et des politiques de sécurité adaptées lorsque nécessaire ;
- sauvegarder les configurations avant les changements ;
- surveiller les modifications de table et les incidents de connectivité ;
- planifier les procédures de retour arrière.

Dans les réseaux comportant une route par défaut vers un fournisseur ou un réseau central, l’adresse du prochain saut mérite une attention particulière. Une erreur peut détourner un grand volume de trafic. Les changements doivent être réalisés selon une procédure approuvée, avec des critères de réussite vérifiables.

### 3.8. Éviter le routage vers soi-même et les boucles

Une route mal conçue peut envoyer un paquet vers un routeur qui le renvoie à l’équipement précédent. Dans certains cas, une route statique peut créer une dépendance circulaire ou un chemin de transfert qui entraîne une boucle jusqu’à l’expiration du TTL.

Pour limiter ce risque, vérifie que le prochain saut mène réellement vers la destination et qu’il ne pointe pas vers un équipement qui renvoie le même trafic vers l’émetteur. Vérifie les routes installées sur tous les routeurs concernés et teste les chemins dans les deux sens.

Les routes de rejet peuvent servir à empêcher certaines boucles ou à appliquer des comportements de sécurité, mais elles doivent être placées de manière cohérente avec les routes plus spécifiques. Une route de rejet trop large peut supprimer du trafic légitime ; une route de rejet trop spécifique peut être contournée par une route plus longue si cette dernière est présente.

### 3.9. Sécurité des protocoles de gestion

Les tables de routage et les routes statiques sont des éléments sensibles de la configuration. Un attaquant capable de modifier la configuration du routeur peut détourner le trafic ou provoquer une indisponibilité. Les interfaces d’administration doivent donc être protégées avec des comptes dédiés, des mots de passe robustes, des mécanismes d’accès sécurisés et des restrictions de source lorsque cela est approprié.

La gestion du routeur devrait être séparée des réseaux d’utilisateurs quand l’architecture le permet. Les journaux doivent permettre de retracer les modifications de configuration et les connexions administratives. Les sauvegardes doivent être stockées de manière sécurisée et les versions de configuration doivent être comparables.

Une route statique correctement configurée ne remplace pas le contrôle d’accès au plan de gestion. La sécurité repose sur l’ensemble de l’architecture : contrôle des comptes, segmentation, limitation des accès, contrôle des modifications et surveillance opérationnelle.

### 3.10. Plan de dépannage recommandé

Lorsqu’un réseau distant est inaccessible, applique une méthode constante :

1. **Vérifier les interfaces** avec `show ip interface brief` et, si nécessaire, `show interfaces`.
2. **Vérifier les réseaux connectés** dans `show ip route`.
3. **Vérifier la route prévue** dans la configuration active et la table installée.
4. **Vérifier le prochain saut** par ping et en examinant ARP lorsque le lien est Ethernet.
5. **Vérifier les routeurs intermédiaires** et les routes de retour.
6. **Tester de bout en bout** avec ping et traceroute.
7. **Examiner le filtrage** si les routes sont correctes mais que le trafic est toujours bloqué.
8. **Documenter la cause et la correction** pour éviter de répéter l’incident.

Le but est d’isoler chaque couche plutôt que de modifier plusieurs routes sans diagnostic. Une route absente, un prochain saut injoignable et un pare-feu qui bloque les paquets sont trois problèmes différents et doivent être traités séparément.

> **Danger :** Une route statique trop large ou une route par défaut incorrecte peut détourner le trafic d’une grande partie du réseau. Avant de modifier une route en production, vérifie son préfixe exact, son prochain saut, les routes concurrentes, les chemins retour et l’impact potentiel sur les utilisateurs. Conserve la configuration précédente et prépare une procédure de retour arrière. Ne considère jamais le simple fait qu’une commande est acceptée par l’équipement comme une preuve que le routage est correct.


## Points à retenir

- **Une table de routage indique comment atteindre une destination**, mais la présence d’une route dans la configuration ne garantit pas qu’elle soit installée ou utilisable. Les routes connectées, statiques et dynamiques peuvent coexister, et chacune a ses propres conditions de validité.

- **Le préfixe le plus long est central dans la sélection du chemin.** Le routeur retient la route la plus spécifique qui correspond à l’adresse de destination. La distance administrative et la métrique servent à départager d’autres candidats selon les règles de l’équipement et de la source de routage ; elles ne remplacent pas le principe de préfixe le plus long.

- **Une route statique doit être vérifiée dans les deux sens et sur tout le chemin.** Valide les interfaces, les prochains sauts, les routes de retour, la table installée et la connectivité de bout en bout. Documente les changements et prépare un retour arrière, surtout lorsqu’ils concernent une route par défaut ou une destination critique.


## Références techniques

- RFC 1812, *Requirements for IP Version 4 Routers*, en particulier les principes de consultation de la table de transfert et de correspondance par préfixe : https://www.rfc-editor.org/rfc/rfc1812.html
- RFC 4632, *Classless Inter-domain Routing (CIDR): The Internet Address Assignment and Aggregation Plan* : https://www.rfc-editor.org/rfc/rfc4632.html
- Documentation Cisco IOS XE, *IP Routing Configuration Guide — Basic IP Routing* : https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-routing/b-ip-routing/m_iri-iprouting.html
- Référence des commandes Cisco IOS, commande `ip route` : https://www.cisco.com/c/en/us/td/docs/ios/iproute_pi/command/reference/iri_book/iri_pi1.html
