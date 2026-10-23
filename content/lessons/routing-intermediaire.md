---
node_id: routing-intermediaire
title: Routage statique & tables - Intermédiaire
---

# Routage statique & tables - Intermédiaire

**Niveau :** Intermédiaire

Le routage IP est le mécanisme qui permet à un paquet de quitter son réseau d’origine et de traverser un ou plusieurs routeurs jusqu’au réseau de destination. Une fois le paquet reçu sur une interface, le routeur examine l’adresse IP de destination, consulte ses informations de transfert et sélectionne le meilleur chemin disponible. Le plan de routage produit et maintient les informations nécessaires ; le plan de transfert les utilise pour acheminer les paquets rapidement. Comprendre cette séparation est essentiel pour diagnostiquer un réseau où une route semble correcte dans la configuration mais n’est pas utilisée comme prévu.

Les routes statiques sont configurées manuellement par l’administrateur. Elles sont utiles pour les petites topologies, les réseaux de bordure, les chemins de secours, les routes vers des réseaux stables et les domaines où une politique de routage déterministe est préférable à l’apprentissage dynamique. Elles ne sont toutefois pas automatiquement conscientes de la topologie : une route statique peut rester configurée alors que le chemin réel est devenu inutilisable, à moins que sa résolution, son suivi ou une autre fonction ne la retire de la table de routage.

La table de routage n’est pas une simple liste de réseaux. Chaque entrée décrit un préfixe, sa source, sa préférence, sa métrique éventuelle et les informations permettant d’acheminer les paquets vers la destination. Plusieurs routes peuvent couvrir une même adresse de destination. Le routeur doit alors appliquer un ordre de sélection : le préfixe le plus spécifique est privilégié, puis les critères de sélection entre routes vers le même préfixe, notamment la préférence administrative et la métrique selon la plate-forme et le contexte.

Ce cours approfondit la logique des tables IPv4, le choix du prochain saut, les routes connectées, statiques et par défaut, les routes récursives, les routes flottantes, le résumé, le routage asymétrique et le dépannage Cisco IOS/IOS XE. Les exemples sont conçus pour un laboratoire et doivent être adaptés aux noms d’interfaces, aux adresses, aux versions logicielles et aux politiques réelles avant tout déploiement.

> **Analogie** : Imagine le routeur comme un centre de tri. Chaque colis porte une adresse finale, mais le centre n’a pas besoin de connaître chaque rue sur l’ensemble du trajet. Il consulte une table qui indique vers quel centre voisin envoyer le colis. Certaines entrées couvrent une grande région, comme « tout le pays », tandis que d’autres couvrent une zone beaucoup plus précise, comme « cette rue ». Si une entrée précise existe, elle prend le dessus sur la consigne plus générale, même si cette dernière est associée à une autre source. C’est l’idée du préfixe le plus long.
>
> Le centre de tri conserve aussi plusieurs informations sur la manière dont une destination a été apprise. Une route configurée manuellement peut être préférée à une route apprise automatiquement, sauf si l’administrateur lui attribue une préférence moins favorable. Une route de secours reste comme un itinéraire de remplacement : elle n’est utilisée que lorsque la route principale ne peut plus être installée. Enfin, le centre doit distinguer l’adresse du destinataire et le prochain centre de tri. Le prochain saut n’est pas la destination finale : c’est simplement l’étape vers laquelle le colis doit être transmis.

---

## 1. La théorie et les algorithmes

### 1.1. Plan de contrôle, RIB et FIB

Il est utile de distinguer trois notions : la configuration, la table de routage et la table de transfert.

- **Configuration** : règles administratives saisies par l’opérateur, par exemple une route statique.
- **RIB (*Routing Information Base*)** : base des informations de routage connues et candidates, où différents mécanismes peuvent proposer des routes.
- **FIB (*Forwarding Information Base*)** : structure optimisée utilisée par le plan de transfert pour prendre les décisions de transmission de paquets.

Les termes et l’architecture interne varient selon les systèmes d’exploitation réseau. Sur Cisco IOS/IOS XE, `show ip route` présente la table IPv4 installée avec les codes de source, les préfixes, les prochains sauts et les métriques. Les détails de la FIB peuvent être accessibles par des commandes spécifiques à la plate-forme.

Une commande présente dans la configuration ne garantit pas que sa route apparaisse dans la table de routage. Pour être installée, une route statique doit notamment être valide et son prochain saut doit être résolu selon les règles de la plate-forme. Si une route dynamique concurrente est sélectionnée pour le même préfixe et possède une préférence administrative plus favorable, la route statique peut rester configurée tout en n’étant pas la route installée.

Ce point est particulièrement important dans le dépannage : `show running-config` permet de vérifier ce qui a été configuré, tandis que `show ip route` indique ce qui est effectivement retenu dans la table IPv4. Les deux vues sont complémentaires.

### 1.2. Composition d’une entrée de routage

Une entrée de routage peut contenir les éléments suivants :

| Élément | Signification | Exemple conceptuel |
|---|---|---|
| Préfixe de destination | Réseau ou hôte couvert par la route | `192.168.40.0/24` |
| Source | Origine de l’information | Connectée, statique, OSPF, EIGRP, BGP |
| Préférence administrative | Préférence relative entre sources, spécifique à l’implémentation | Statique Cisco : 1 par défaut |
| Métrique | Coût défini par la source de routage, si applicable | Coût OSPF ou métrique EIGRP |
| Prochain saut | Routeur vers lequel transmettre le paquet | `10.0.12.2` |
| Interface de sortie | Interface de transmission, si déterminée | `GigabitEthernet0/1` |
| État / temporisation | Informations de validité ou d’âge selon le mécanisme | Dépend du protocole |

Le préfixe correspond à une adresse réseau accompagnée d’une longueur CIDR. Par exemple, `192.168.40.0/24` couvre les adresses dont les 24 premiers bits correspondent au préfixe. La route `192.168.40.128/25` est plus spécifique : elle ne couvre que la moitié supérieure de ce `/24`.

Une route de préfixe `/32` décrit une seule adresse IPv4. Une route `/0` correspond à la route par défaut, qui peut être utilisée lorsqu’aucune route plus spécifique ne correspond à la destination et qu’une route par défaut est présente et valide.

### 1.3. Algorithme de sélection : le préfixe le plus long

Le premier principe de sélection d’une route est le **Longest Prefix Match (LPM)**, ou choix du préfixe le plus long. Le routeur compare l’adresse de destination aux préfixes disponibles et privilégie celui qui correspond au plus grand nombre de bits significatifs.

Considérons cette table :

| Préfixe | Prochain saut | Rôle |
|---|---|---|
| `0.0.0.0/0` | `10.0.0.1` | Route par défaut |
| `10.0.0.0/8` | `10.0.12.2` | Préfixe général |
| `10.20.0.0/16` | `10.0.23.2` | Préfixe plus spécifique |
| `10.20.30.0/24` | `10.0.34.2` | Préfixe encore plus spécifique |

Pour la destination `10.20.30.99`, plusieurs routes correspondent : `/0`, `/8`, `/16` et `/24`. La route `/24` est sélectionnée, car elle correspond au préfixe le plus long. La préférence administrative ne permet pas à une route par défaut de supplanter une route `/24` simplement parce que sa source est jugée plus favorable.

La sélection LPM s’effectue avant la comparaison de préférence entre sources lorsqu’il s’agit de trouver la route la plus spécifique correspondant à une destination. La préférence administrative et la métrique servent plutôt à décider quelle route retenir lorsqu’il existe plusieurs candidates équivalentes pour le même préfixe, selon l’architecture de sélection de la plate-forme.

#### Schéma de sélection

```text
Destination du paquet : 10.20.30.99

Routes candidates :
  0.0.0.0/0        -> correspond,  0 bits spécifiques
  10.0.0.0/8       -> correspond,  8 bits spécifiques
  10.20.0.0/16     -> correspond, 16 bits spécifiques
  10.20.30.0/24    -> correspond, 24 bits spécifiques

                +----------------------------+
                | Comparer les préfixes      |
                +-------------+--------------+
                              |
                              v
                +----------------------------+
                | Choisir la route /24        |
                | car c'est le match le plus |
                | long et le plus spécifique |
                +-------------+--------------+
                              |
                              v
                Prochain saut : 10.0.34.2
```

> **Piège :** La distance administrative n’annule pas le principe du préfixe le plus long. Une route statique par défaut avec une distance administrative de 1 ne remplace pas une route OSPF `10.20.30.0/24`, parce que les préfixes ne couvrent pas la même portion d’espace d’adressage. Le routeur choisit d’abord la route la plus spécifique qui correspond, puis applique les règles de sélection pertinentes entre routes de même préfixe.

### 1.4. Routes connectées et locales

Lorsqu’une interface L3 est configurée avec une adresse et qu’elle est opérationnelle, le routeur installe généralement une route connectée vers le sous-réseau de l’interface. Il installe également, dans de nombreux systèmes Cisco, une route locale `/32` vers l’adresse exacte de l’interface.

Exemple :

```cisco
interface GigabitEthernet0/0
 description LAN-USERS
 ip address 192.168.10.1 255.255.255.0
 no shutdown
```

Lorsque l’interface est active, la table peut contenir des entrées de ce type :

```text
C    192.168.10.0/24 is directly connected, GigabitEthernet0/0
L    192.168.10.1/32 is directly connected, GigabitEthernet0/0
```

`C` représente habituellement une route connectée et `L` une route locale dans les systèmes Cisco concernés. La route connectée indique que le sous-réseau est joignable par cette interface. La route locale représente l’adresse propre du routeur ; les paquets destinés à cette adresse sont destinés au routeur lui-même, et non à être routés vers un autre hôte.

Si l’interface tombe, la route connectée associée est généralement retirée de la table installée. C’est une différence importante avec une route statique simplement configurée : son existence dans la configuration ne signifie pas que le chemin physique vers le prochain saut est sain.

Une route connectée ne signifie pas que tous les hôtes du sous-réseau sont actifs ou répondent. Elle indique uniquement que le réseau est directement attaché à l’interface et que le routeur peut tenter de joindre les destinations du préfixe sur ce segment.

### 1.5. Routes statiques : syntaxe et comportement

Une route IPv4 statique Cisco IOS est configurée avec la commande `ip route`. La syntaxe générale la plus courante est :

```cisco
ip route <réseau-destination> <masque> <prochain-saut-ou-interface> [distance-administrative]
```

Exemple :

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.12.2
```

Cette route demande au routeur d’envoyer les paquets destinés au réseau `192.168.30.0/24` vers le prochain saut `10.0.12.2`. Le routeur doit pouvoir résoudre ce prochain saut en un chemin de sortie valide. Une route statique utilisant uniquement une adresse de prochain saut peut nécessiter une résolution récursive : le routeur consulte sa table pour déterminer comment atteindre ce prochain saut.

Il existe plusieurs façons d’écrire une route statique selon la topologie :

```cisco
! Prochain saut explicite
ip route 192.168.30.0 255.255.255.0 10.0.12.2

! Interface de sortie explicite (souvent adaptée aux liens point-à-point)
ip route 192.168.30.0 255.255.255.0 Serial0/0/0

! Interface et prochain saut explicitement associés
ip route 192.168.30.0 255.255.255.0 GigabitEthernet0/1 10.0.12.2
```

La forme appropriée dépend de la nature du support. Sur un réseau Ethernet multiaccès, une route statique configurée uniquement avec une interface de sortie peut obliger le routeur à résoudre par ARP chaque adresse de destination finale du préfixe, au lieu de ne résoudre que le prochain saut. Cela peut produire un comportement indésirable, voire une consommation excessive de ressources ARP. Sur un lien point-à-point, indiquer l’interface de sortie est souvent naturel, car il n’existe qu’un voisin distant sur le lien.

Pour une liaison Ethernet, préciser le prochain saut évite généralement cette ambiguïté. Il faut toutefois vérifier la syntaxe et le comportement propres à la plate-forme, en particulier avec les interfaces logiques, les sous-interfaces et les architectures de commutation L3.

### 1.6. Route par défaut

La route par défaut sert de solution de dernier recours lorsque le routeur ne possède pas de route plus spécifique valide pour la destination. En IPv4, elle est représentée par le préfixe `0.0.0.0/0`.

Exemple :

```cisco
ip route 0.0.0.0 0.0.0.0 10.0.12.2
```

La route demande au routeur d’envoyer les destinations inconnues vers le prochain saut `10.0.12.2`. Elle est courante sur un routeur de succursale dont l’accès au reste du réseau passe par un routeur central ou un fournisseur d’accès.

Le routeur ne doit pas envoyer automatiquement tous les paquets vers la route par défaut. Une route plus spécifique est préférée lorsqu’elle correspond à la destination et qu’elle est valide. Par exemple, si la table contient `192.168.0.0/16` et `0.0.0.0/0`, une destination `192.168.50.10` suivra normalement le `/16`.

Une route par défaut peut être configurée manuellement, apprise d’un protocole de routage ou générée par une autre fonction selon la conception. Sur Cisco IOS, `show ip route` affiche habituellement une route par défaut statique avec le code `S*` si elle est installée et marquée comme route candidate par défaut.

Une route par défaut mal placée peut provoquer une boucle : si deux routeurs se renvoient mutuellement les destinations inconnues, les paquets peuvent circuler entre eux jusqu’à l’expiration de leur TTL. La route par défaut doit donc être associée à un chemin de sortie réel et cohérent, et le chemin de retour doit être considéré pour les communications bidirectionnelles.

### 1.7. Distance administrative et métrique

Sur Cisco IOS/IOS XE, la **distance administrative (AD)** représente la préférence relative donnée aux sources de routes pour un même préfixe. Plus sa valeur est basse, plus la source est habituellement préférée lorsqu’il faut départager des routes candidates équivalentes vers le même préfixe.

Valeurs par défaut couramment rencontrées sur les systèmes Cisco classiques :

| Source de route | Distance administrative typique |
|---|---:|
| Connectée | 0 |
| Statique | 1 |
| EIGRP interne | 90 |
| OSPF | 110 |
| RIP | 120 |
| EIGRP externe | 170 |
| Inconnue / non installée | 255 |

Ces valeurs sont des valeurs usuelles Cisco, non des valeurs universelles de tous les fournisseurs. Elles peuvent être modifiées et doivent être vérifiées sur la plateforme en production.

La **métrique** est différente. Elle mesure le coût du chemin selon les règles du protocole de routage. Par exemple, OSPF utilise un coût, tandis qu’EIGRP utilise une métrique composite. La comparaison de métrique se fait dans le contexte d’un même protocole et de ses règles. La distance administrative sert à départager la préférence des sources lorsque la comparaison porte sur le même préfixe.

Exemple : si un routeur apprend `192.168.30.0/24` par OSPF et possède aussi une route statique vers exactement `192.168.30.0/24`, la route statique par défaut est normalement préférée en raison de son AD plus faible. Si la route statique est rendue moins préférée avec une AD supérieure à celle d’OSPF, OSPF peut être installé tant qu’il demeure disponible.

> **Piège :** Ne traite pas une AD de 90 comme « plus rapide » qu’une AD de 110. La distance administrative n’est ni une latence ni une bande passante. C’est une règle de préférence locale entre sources de routage, généralement appliquée lors de la sélection d’une route pour le même préfixe.

### 1.8. Routes flottantes

Une route statique flottante est une route statique configurée avec une distance administrative plus élevée que la route principale. Elle est destinée à être installée si la route privilégiée disparaît de la table de routage.

Exemple : une route OSPF vers `192.168.30.0/24` peut avoir une AD par défaut de 110 sur un routeur Cisco. Une route statique de secours peut être configurée avec une AD de 200 :

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.99.2 200
```

Tant que la route OSPF vers le même préfixe est présente et préférée, la statique flottante reste normalement en dehors de la table installée. Si la route OSPF disparaît et que le prochain saut statique reste valide, la route statique peut être insérée.

La route flottante n’est pas forcément un mécanisme de détection de panne de bout en bout. Si la route statique utilise un prochain saut qui reste considéré comme joignable alors que le chemin applicatif est défaillant, la route peut demeurer installée. Pour une détection plus fine, la plate-forme peut prendre en charge des mécanismes de suivi tels que IP SLA et `track`, ou d’autres mécanismes appropriés à l’architecture.

Pour une route principale qui est elle-même statique, l’AD de la route de secours doit être supérieure à l’AD de la route principale. Si les deux routes ont la même préférence et le même préfixe, la sélection peut produire un comportement ECMP ou dépendre de la métrique et de l’implémentation plutôt que fournir une simple relation primaire/secours.

### 1.9. Résolution récursive du prochain saut

Lorsqu’une route statique est configurée avec une adresse de prochain saut, le routeur doit savoir comment atteindre cette adresse. Cette opération est appelée résolution récursive.

Supposons que R1 ait :

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.12.2
```

Le routeur doit déterminer par quelle interface et par quel chemin il atteint `10.0.12.2`. Si ce prochain saut appartient à un réseau directement connecté, la résolution est généralement simple. S’il est atteint au moyen d’une autre route, le routeur résout le prochain saut à travers cette route.

La récursion doit aboutir à une interface de sortie valide. Une route peut être invalide si le prochain saut n’est pas résoluble, si la résolution boucle sur elle-même ou si la profondeur de récursion dépasse les limites de l’implémentation.

#### Exemple de résolution

```text
Route voulue :
192.168.30.0/24 -> prochain saut 10.0.12.2

Recherche de 10.0.12.2 :
10.0.12.0/30 -> GigabitEthernet0/1

Résultat :
192.168.30.0/24 -> 10.0.12.2 -> GigabitEthernet0/1
```

Une erreur fréquente consiste à configurer un prochain saut dont la route de résolution dépend elle-même de la route en cours de calcul. La route peut alors être rejetée ou retirée de la table installée. La configuration doit être vérifiée avec `show ip route`, les commandes de consultation de route vers le prochain saut et les diagnostics propres à la plate-forme.

### 1.10. Routage asymétrique et chemin retour

Un paquet peut atteindre sa destination en suivant un chemin différent de celui utilisé par la réponse. C’est le routage asymétrique. Il n’est pas nécessairement incorrect : les réseaux multi-chemins et les politiques de routage peuvent produire des itinéraires aller et retour différents.

Cependant, un chemin asymétrique peut compliquer le dépannage lorsqu’un pare-feu stateful, un équipement NAT ou une politique de sécurité exige que les deux directions passent par le même dispositif ou la même instance. Un routeur peut posséder une route valide vers la destination, mais l’application échoue si le chemin retour est absent ou si un contrôle intermédiaire bloque la réponse.

Pour tester une connectivité, il faut donc analyser les deux directions. La route aller peut sembler correcte alors que la destination renvoie ses réponses via une passerelle qui ne possède pas de chemin vers le réseau source. De la même façon, un filtre peut autoriser le flux aller mais refuser le retour.

Les outils utiles comprennent `ping`, `traceroute`, `show ip route <destination>`, les captures de paquets et les journaux des pare-feu. Un échec de ping n’identifie pas automatiquement la panne : certains équipements bloquent ICMP, et le trafic applicatif peut subir un traitement différent.

### 1.11. Résumé de routes

Un résumé regroupe plusieurs préfixes contigus sous un préfixe agrégé plus large. Par exemple, les réseaux `192.168.32.0/24` à `192.168.35.0/24` peuvent être couverts par `192.168.32.0/22`, car ils constituent un bloc aligné de quatre sous-réseaux `/24`.

La route agrégée réduit le nombre d’entrées annoncées ou configurées, mais elle exige que le bloc soit correctement aligné et qu’il représente l’ensemble des destinations visées. Un résumé trop large peut couvrir des adresses qui ne sont pas réellement présentes dans la topologie.

Le risque le plus fréquent est le trou noir de routage : un routeur annonce ou installe une route agrégée, mais certaines destinations couvertes ne sont pas disponibles. Les paquets sont envoyés vers le routeur qui détient le résumé, qui peut ne pas posséder de chemin plus spécifique pour les transférer.

Une conception habituelle consiste à associer l’agrégat à une route de rejet ou à un comportement équivalent, afin d’éviter qu’une destination inconnue couverte par l’agrégat ne reparte indéfiniment vers le voisin par défaut. La syntaxe et le comportement de cette route de rejet varient selon la plate-forme.

Avant de créer un résumé, vérifie :

1. l’alignement binaire du préfixe agrégé ;
2. les sous-réseaux réellement utilisés ;
3. les trous potentiels dans la plage ;
4. l’existence d’itinéraires plus spécifiques ;
5. le chemin prévu pour les destinations absentes ;
6. l’impact sur le trafic de retour et le dépannage.

### 1.12. Routage statique avec plusieurs sorties

Un routeur peut disposer de plusieurs chemins vers un réseau distant. Selon les objectifs, l’administrateur peut utiliser une route principale et une route de secours, ou exploiter plusieurs chemins de coût équivalent si la plate-forme et la configuration le permettent.

Pour un chemin primaire et un secours, les routes statiques flottantes sont simples : une route utilise la préférence habituelle, tandis que la seconde possède une AD plus élevée. Ce mécanisme fonctionne surtout lorsque la disparition de la route principale entraîne un changement clair dans la table de routage.

Il faut toutefois définir ce que signifie « panne ». Une interface directement connectée qui tombe est généralement détectée par l’état de lien. Mais si le prochain saut répond encore sur son réseau local alors que le réseau distant en amont a échoué, une route statique simple peut rester valide. Dans ce cas, un mécanisme de suivi du chemin ou un protocole de routage dynamique peut être plus approprié.

#### Topologie primaire/secours

```text
                       Réseau distant
                         192.168.30.0/24
                              |
                     +--------+--------+
                     |                 |
                  Route A           Route B
                  principale        secours
                     |                 |
                  +------+          +------+
                  |  R2  |          |  R3  |
                  +------+          +------+
                     |                 |
                     +--------+--------+
                              |
                            +----+
                            | R1 |
                            +----+

    Route A : préférence plus favorable
    Route B : AD plus élevée (route flottante)
```

Ce schéma représente un principe. Dans une conception réelle, il faut vérifier les adresses de transit, les chemins retour, la présence des routes sur les routeurs intermédiaires et le mécanisme de détection qui rend la route principale indisponible.

### 1.13. ECMP et plusieurs routes équivalentes

ECMP (*Equal-Cost Multi-Path*) désigne l’utilisation de plusieurs chemins considérés équivalents par la fonction de routage. Lorsqu’un routeur accepte plusieurs chemins de coût égal vers un même préfixe, il peut répartir différents flux entre ces chemins selon un algorithme de hachage.

ECMP ne signifie pas nécessairement que chaque paquet d’une même conversation utilise une liaison différente. De nombreux équipements répartissent les flux en fonction de champs comme les adresses source/destination, les ports de transport et le protocole, afin de préserver l’ordre des paquets au sein d’un flux. Les champs exacts utilisés par le hachage dépendent du matériel et de la configuration.

L’équilibrage peut améliorer l’utilisation de plusieurs liaisons, mais il peut aussi compliquer le dépannage. Un flux peut emprunter une voie présentant une panne partielle tandis qu’un autre fonctionne. Les pare-feu stateful, les équipements NAT et certains mécanismes de contrôle de chemin doivent être compatibles avec le chemin réellement emprunté.

Le nombre de chemins installables, les règles ECMP et la façon dont les routes équivalentes sont traitées sont propres à chaque plate-forme. Il faut confirmer leur comportement sur le matériel concerné plutôt que supposer qu’un routeur répartit toujours les paquets de manière uniforme.

### 1.14. IPv6 : principes équivalents

Les mêmes principes de sélection par préfixe le plus long existent en IPv6. Les routes sont exprimées avec une adresse et une longueur de préfixe, par exemple `2001:db8:30::/64`. Les routes statiques IPv6 se configurent généralement avec `ipv6 route` sur Cisco IOS/IOS XE.

Exemple :

```cisco
ipv6 unicast-routing
interface GigabitEthernet0/0
 description LAN-V6
 ipv6 address 2001:db8:10::1/64
 no shutdown

ipv6 route 2001:db8:30::/64 2001:db8:12::2
```

Le préfixe `2001:db8::/32` est réservé à la documentation et ne doit pas être utilisé comme adresse de production sur Internet. Il est employé ici uniquement pour les exemples.

Les routes IPv6 présentent aussi des considérations de prochain saut et d’interface de sortie. Les adresses link-local (`FE80::/10`) sont couramment utilisées comme prochains sauts dans des protocoles et des configurations IPv6, mais elles nécessitent que l’interface de sortie soit déterminée, car une adresse link-local n’est pas globalement unique à toutes les interfaces.

Lors du dépannage IPv6, il faut examiner la table IPv6 avec les commandes appropriées, vérifier les adresses et préfixes, les routes de retour et le fonctionnement de Neighbor Discovery (NDP). ARP ne joue pas le rôle de résolution de voisin en IPv6.

### 1.15. Comparaison de routes : ce que le routeur compare réellement

La sélection de routage doit être abordée en plusieurs étapes. Une vue simplifiée peut être décrite ainsi :

1. Le routeur reçoit un paquet et extrait l’adresse IP de destination.
2. Il recherche dans la FIB les préfixes qui correspondent à l’adresse.
3. Il privilégie le préfixe le plus long.
4. Lors de la construction de la table installée, les sources concurrentes pour un même préfixe sont départagées selon les règles de préférence et de métrique propres à l’implémentation.
5. Le prochain saut est déterminé, éventuellement par résolution récursive.
6. La couche de liaison détermine l’adresse MAC du prochain saut sur un segment Ethernet, si cela est nécessaire.
7. Le paquet est encapsulé et transmis sur l’interface de sortie.

Cette séquence est volontairement simplifiée. Les routeurs modernes optimisent la recherche de route, appliquent des politiques et peuvent utiliser plusieurs tables, VRF, ACL, PBR ou d’autres fonctions. Néanmoins, la séparation entre correspondance de destination, sélection du chemin et résolution de couche 2 est indispensable pour comprendre le comportement général.

Le contrôle du prochain saut ne doit pas être confondu avec la sélection de l’adresse MAC de destination. Une route IP définit le prochain saut IP ou l’interface de sortie. Sur Ethernet, le routeur résout ensuite l’adresse de couche 2 correspondant au prochain saut sur ce segment. Pour une destination distante, il ne cherche normalement pas l’adresse MAC de l’hôte final situé sur un autre réseau : il encapsule la trame pour le routeur suivant.

### 1.16. Configuration pratique : topologie à trois routeurs

La topologie de laboratoire suivante illustre un réseau utilisateur derrière R1, un réseau intermédiaire entre R1 et R2, un autre réseau entre R2 et R3, et un LAN distant derrière R3.

| Routeur | Interface | Adresse IPv4 | Fonction |
|---|---|---|---|
| R1 | G0/0 | `192.168.10.1/24` | LAN local |
| R1 | G0/1 | `10.0.12.1/30` | Vers R2 |
| R2 | G0/0 | `10.0.12.2/30` | Vers R1 |
| R2 | G0/1 | `10.0.23.2/30` | Vers R3 |
| R3 | G0/0 | `10.0.23.3/30` | Vers R2 |
| R3 | G0/1 | `192.168.30.1/24` | LAN distant |

```text
       LAN R1                  Transits                 LAN R3
    192.168.10.0/24                                    192.168.30.0/24
           |                                                  |
      +---------+      10.0.12.0/30     +---------+   10.0.23.0/30   +---------+
      |   R1    |-----------------------|   R2    |------------------|   R3    |
      +---------+                       +---------+                  +---------+
      .10.1 / .12.1                     .12.2 / .23.2               .23.3 / .30.1
```

Les noms d’interfaces ci-dessous sont représentatifs. Sur certains routeurs, les interfaces auront d’autres noms. Les commandes doivent être adaptées au matériel et au système d’exploitation utilisé.

#### Configuration de R1

```cisco
hostname R1

interface GigabitEthernet0/0
 description LAN-R1
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface GigabitEthernet0/1
 description TRANSIT-R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown

! Réseau distant derrière R3, accessible via R2
ip route 192.168.30.0 255.255.255.0 10.0.12.2

! Réseau de transit vers R3 : nécessaire seulement si le plan le demande
ip route 10.0.23.0 255.255.255.252 10.0.12.2
```

R1 possède une route statique vers le LAN de R3 en indiquant le prochain saut R2. Le réseau de transit `10.0.23.0/30` n’a pas besoin d’être ajouté à R1 simplement pour qu’il puisse atteindre `192.168.30.0/24`. On peut néanmoins configurer une route vers ce réseau si l’architecture ou les objectifs de laboratoire l’exigent ; elle n’est pas nécessaire au transfert du trafic destiné au LAN distant via R2.

#### Configuration de R2

```cisco
hostname R2

interface GigabitEthernet0/0
 description TRANSIT-R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown

interface GigabitEthernet0/1
 description TRANSIT-R3
 ip address 10.0.23.2 255.255.255.252
 no shutdown

! LAN local à R1
ip route 192.168.10.0 255.255.255.0 10.0.12.1

! LAN local à R3
ip route 192.168.30.0 255.255.255.0 10.0.23.3
```

R2 est le routeur intermédiaire et doit savoir comment joindre les deux LAN de périphérie. Les réseaux de transit sont directement connectés et apparaissent automatiquement dans la table lorsque les interfaces sont opérationnelles.

#### Configuration de R3

```cisco
hostname R3

interface GigabitEthernet0/0
 description TRANSIT-R2
 ip address 10.0.23.3 255.255.255.252
 no shutdown

interface GigabitEthernet0/1
 description LAN-R3
 ip address 192.168.30.1 255.255.255.0
 no shutdown

! Retour vers le LAN de R1
ip route 192.168.10.0 255.255.255.0 10.0.23.2

! Route de secours par défaut vers R2 si nécessaire
! Ne pas ajouter si la politique de routage exige une route plus spécifique.
```

R3 doit avoir une route de retour vers `192.168.10.0/24`, sinon un paquet peut arriver depuis R1 mais sa réponse ne saura pas revenir. Cet exemple souligne qu’une connectivité de bout en bout exige des routes dans les deux directions.

### 1.17. Vérification des routes et de la connectivité

Les commandes suivantes sont fondamentales sur Cisco IOS/IOS XE :

```cisco
show ip interface brief
show ip route
show ip route static
show ip route 192.168.30.0
show running-config | include ^ip route
ping 192.168.30.1
traceroute 192.168.30.1
```

`show ip interface brief` donne un aperçu de l’état des interfaces et de leurs adresses. `show ip route` affiche les routes installées. `show ip route static` cible les routes statiques ; la disponibilité exacte varie selon le système d’exploitation. `show ip route 192.168.30.0` permet d’examiner la route associée à une destination spécifique, si la syntaxe est prise en charge.

La sortie attendue sur R1 doit montrer le préfixe `192.168.30.0/24` via `10.0.12.2`, à condition que le prochain saut soit résolu et que la route soit active. Sur R3, la route retour vers `192.168.10.0/24` doit apparaître via `10.0.23.2`.

Un test de ping doit être complété par l’examen du chemin retour. Si le ping échoue, les causes possibles comprennent une route manquante, une passerelle incorrecte, une ACL, une interface désactivée, une erreur d’adressage ou un équipement final qui ne répond pas à ICMP.

### 1.18. Ajouter une route flottante

Supposons que R1 possède un chemin principal dynamique vers `192.168.30.0/24` avec une AD de 110 et qu’un chemin de secours existe par une seconde liaison. Une route statique peut être configurée avec une AD plus élevée :

```cisco
ip route 192.168.30.0 255.255.255.0 10.0.99.2 200
```

Cette route statique sert de secours si la route principale préférée est retirée de la table et si le prochain saut `10.0.99.2` reste résoluble. Pour qu’elle soit utile, le routeur de secours et les routes de retour doivent également être configurés.

Il faut distinguer deux mécanismes : la préférence administrative décide quelle route candidate est préférée ; la détection de panne détermine si le routeur estime que le chemin est valide. Une route flottante ne surveille pas automatiquement chaque destination applicative. Si le lien local fonctionne mais que le réseau distant derrière le prochain saut est en panne, la route peut rester installée sans mécanisme de suivi supplémentaire.

### 1.19. Suivi d’un chemin et IP SLA

Sur les plates-formes Cisco qui le prennent en charge, IP SLA et `track` peuvent surveiller une condition de connectivité et influencer la disponibilité d’une route. La syntaxe et les fonctionnalités exactes varient selon les versions et les modèles.

Un exemple conceptuel peut sonder une adresse de test distante, associer le résultat à un objet de suivi, puis rendre une route dépendante de cet objet. Le but est de retirer ou désactiver le chemin principal lorsque le test échoue, afin de permettre à une route de secours de devenir utilisable.

Un dispositif IP SLA ne doit pas être ajouté sans concevoir correctement le test. La cible doit représenter une dépendance pertinente et le mécanisme de sondage doit éviter les faux positifs. Si la cible est trop proche, le test peut réussir alors que l’accès à l’application distante est dégradé. Si elle est mal choisie ou bloquée par une politique ICMP, le test peut déclarer une panne alors que le chemin applicatif fonctionne.

Avant d’utiliser IP SLA en production, définir : la cible, le protocole de test, l’intervalle, le délai d’expiration, le nombre d’échecs tolérés, le comportement lors du retour du service, la route de secours, et les conséquences si les deux chemins échouent.

### 1.20. Routage, ACL et plan de sécurité

Une route indique comment acheminer le paquet ; elle ne garantit pas que le trafic est autorisé. Les ACL, pare-feu, politiques de sécurité, VRF et autres mécanismes peuvent autoriser ou bloquer le paquet indépendamment de la route sélectionnée.

Lors du dépannage, il faut éviter de conclure qu’une route correcte prouve que la communication doit réussir. La route est une condition nécessaire au routage, mais la connectivité de bout en bout dépend aussi des interfaces, du chemin retour, des filtres et du comportement de la destination.

Les routes statiques peuvent également créer des chemins non souhaités si elles sont ajoutées sans revue. Une route par défaut placée sur un routeur interne peut envoyer des destinations inconnues vers une mauvaise zone. Une route plus spécifique peut détourner une plage entière vers un prochain saut qui ne la dessert pas. La revue des changements doit donc considérer le préfixe, l’interface, le prochain saut, la source concurrente et le comportement attendu lorsque le chemin échoue.

Les bonnes pratiques comprennent l’utilisation de commentaires d’interface, la documentation de chaque route statique, une sauvegarde de configuration avant changement, un test du chemin aller-retour et une procédure de rollback. Les changements doivent être introduits individuellement autant que possible afin d’en isoler l’effet.

### 1.21. Dépannage : arbre de décision

```text
Le réseau distant est inaccessible
             |
             v
  Vérifier l'état des interfaces
             |
    +--------+---------+
    |                  |
 Interface DOWN     Interfaces UP
    |                  |
 Corriger couche 1     v
                 Vérifier la table
                 de routage locale
                       |
              +--------+--------+
              |                 |
         Route absente      Route présente
              |                 |
       Vérifier la statique     v
       / préfixe / prochain saut Tester le prochain saut
                                |
                         +------+------+
                         |             |
                    Injoignable     Joignable
                         |             |
                    Lien / ARP /      v
                    mauvais next-hop  Traceroute et vérifier
                                      chemin retour / ACL
```

Cet arbre aide à organiser le diagnostic ; il ne remplace pas l’analyse des captures et des journaux lorsque le problème est complexe. Un prochain saut peut répondre au ping alors que le réseau final n’est pas disponible. Inversement, un prochain saut peut filtrer ICMP tout en acheminant correctement les paquets applicatifs.

### 1.22. Sécurité et risques des routes statiques

Les routes statiques sont parfois considérées comme sûres parce qu’elles ne dépendent pas d’un protocole d’apprentissage. En réalité, une erreur de configuration statique peut détourner du trafic, créer une boucle, établir un trou noir ou contourner une politique de routage prévue.

Les erreurs les plus risquées incluent :

- une route spécifique incorrecte qui détourne des destinations vers le mauvais voisin ;
- une route par défaut qui renvoie les destinations inconnues vers le réseau d’origine ;
- une route de secours qui reste active alors que le chemin distant est inutilisable ;
- un résumé qui couvre des plages non atteignables ;
- une route vers un prochain saut mal résolu ;
- une route de retour manquante après l’ajout d’une route aller ;
- une route administrative trop préférée qui masque une route dynamique saine.

Une stratégie de sécurité et d’exploitation doit assurer l’autorisation des modifications de configuration, l’enregistrement des changements, la sauvegarde, la validation du chemin et le contrôle de la route de retour. Sur les équipements de production, les commandes de débogage doivent être utilisées de façon limitée et maîtrisée, en particulier sur du matériel fortement sollicité.

> **Astuce :** Pour vérifier une route statique, ne te limite pas à `show running-config`. Compare la configuration avec `show ip route`, examine la résolution du prochain saut, puis teste le chemin et la route retour. Une route configurée n’est pas forcément installée, et une route installée ne garantit pas qu’un service distant réponde.

> **Danger :** Une route statique erronée vers un préfixe large peut détourner une quantité importante de trafic. Le risque est particulièrement élevé lorsqu’une route plus spécifique remplace un chemin correct ou lorsqu’une route par défaut est configurée sur un équipement qui n’est pas réellement en mesure d’acheminer les destinations inconnues. Toute modification de routage doit préciser les préfixes concernés, le prochain saut, le comportement en cas de panne et la procédure de retour arrière.

## Points à retenir

- **Le préfixe le plus long est prioritaire.** La route la plus spécifique correspondant à la destination est choisie avant de départager les sources candidates vers ce même préfixe. La distance administrative n’est ni une métrique de latence ni un remplacement du principe LPM.
- **La configuration n’est pas la table installée.** Vérifie les interfaces, le prochain saut, la résolution récursive, la table de routage et le chemin retour. Une route statique peut rester configurée sans être active si son prochain saut est invalide ou si une route concurrente plus préférée est installée.
- **Les routes de secours exigent une conception complète.** Une route flottante utilise une préférence moins favorable, mais elle ne détecte pas nécessairement les pannes applicatives. Les mécanismes de suivi, les résumés, ECMP et les routes par défaut doivent être testés avec des scénarios de panne réalistes.

---

## Références techniques

- IETF, [RFC 1812 — Requirements for IP Version 4 Routers](https://www.rfc-editor.org/rfc/rfc1812), notamment les règles de sélection de route et le comportement de transfert IPv4.
- IETF, [RFC 4632 — Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632), pour les préfixes et le routage sans classe.
- Cisco, [IP Routing: Protocol-Independent Command Reference](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_pi/command/Cisco_IOS_IP_Routing_Protocol-Independent_Command_Reference.html), pour les routes statiques, les distances administratives et les commandes de routage.
- Cisco, [Configure a Next Hop IP Address for Static Routes](https://www.cisco.com/c/en/us/support/docs/dial-access/floating-static-route/118263-technote-nexthop-00.html), pour la résolution du prochain saut et les routes statiques flottantes.

Les syntaxes, valeurs par défaut et options dépendent de la famille d’équipements et de la version IOS/IOS XE. Vérifier la documentation de la plateforme cible avant d’appliquer les configurations en production.
