# ACL & filtrage - Intermédiaire

**Niveau :** Intermédiaire

Les listes de contrôle d'accès (*Access Control Lists*, ou ACL) sont un mécanisme de classification et de filtrage du trafic réseau. Sur les routeurs et commutateurs de couche 3, elles permettent de décider si un paquet doit être transmis ou rejeté à partir de critères tels que les adresses IPv4 ou IPv6, le protocole IP, les ports TCP/UDP, certains indicateurs de contrôle et, selon la plateforme, d'autres champs de l'en-tête. Elles constituent l'un des outils élémentaires de segmentation, de réduction de la surface d'exposition et de contrôle des flux dans une architecture Cisco.

Les ACL ne sont pas des pare-feu à inspection d'état. Une ACL IP classique évalue les caractéristiques visibles du paquet et applique une suite ordonnée de règles. Elle ne mémorise normalement pas à elle seule l'état complet d'une session TCP, l'intention applicative ni la relation dynamique entre une requête et sa réponse. Cette différence influence la façon de construire une politique : autoriser une connexion sortante et autoriser le trafic retour ne sont pas nécessairement la même décision. Les pare-feu stateful, les ACL de routeur, les listes appliquées aux lignes VTY et les mécanismes de protection du plan de contrôle répondent à des objectifs différents, même si tous utilisent des règles d'accès.

À un niveau intermédiaire, savoir écrire une règle `permit` ou `deny` ne suffit plus. Il faut comprendre l'ordre de traitement, les masques génériques (*wildcard masks*), l'emplacement d'application, les compteurs, l'interaction avec le routage, le traitement des fragments, les protocoles de contrôle et les limites propres aux plateformes. Une ACL techniquement valide peut encore couper un service essentiel, laisser passer plus de trafic que prévu ou rendre le dépannage difficile. La méthode professionnelle consiste à convertir une exigence métier en matrice de flux, à écrire une politique minimale et lisible, puis à la tester avec des commandes de vérification et des scénarios positifs et négatifs.

Les exemples de ce cours utilisent principalement Cisco IOS/IOS XE. La disponibilité exacte des commandes, des groupes d'objets, des compteurs matériels, des entrées temporisées et des options IPv6 varie selon le modèle, la version logicielle et les ressources de filtrage disponibles. Toute commande destinée à la production doit être validée sur la plateforme cible et dans une fenêtre de changement adaptée.

> **Analogie** : Une ACL ressemble à un contrôle de sécurité placé à l'entrée d'un bâtiment. Chaque règle décrit une combinaison de critères : identité annoncée, zone de provenance, destination demandée et type d'accès. L'agent examine les règles dans l'ordre et applique la première qui correspond. Si la première règle autorise l'accès à une zone sensible, une règle de refus située plus bas ne peut pas annuler cette autorisation : l'évaluation s'est déjà arrêtée. Si aucune règle ne correspond, l'accès est refusé par défaut. La position du poste de contrôle compte autant que les règles elles-mêmes : un contrôle placé à l'entrée du bâtiment ne voit pas exactement les mêmes déplacements qu'un contrôle placé devant une salle précise. Une ACL appliquée en entrée d'une interface examine les paquets lorsqu'ils arrivent sur cette interface ; une ACL en sortie examine ceux qui sont sur le point de la quitter. Enfin, un poste de contrôle qui ne garde aucune mémoire de la visite précédente ne peut pas déterminer à lui seul si une personne a déjà été autorisée à entrer. C'est la différence entre un filtrage sans état et un pare-feu qui suit les sessions.


## 1. La théorie et les algorithmes

### 1.1. Rôle d'une ACL dans le chemin d'un paquet

Lorsqu'un hôte émet un paquet IP, celui-ci traverse généralement un réseau local, un équipement de couche 2, puis un routeur ou une interface de couche 3 qui décide s'il doit être acheminé. Le routeur consulte ses informations de routage pour déterminer la sortie et peut appliquer une ACL en entrée ou en sortie, selon la configuration. Le traitement réel peut être intégré à un pipeline matériel et l'ordre interne précis dépend du système, mais le modèle de raisonnement reste utile : identifier l'interface et la direction, déterminer les champs examinés, puis vérifier la règle qui décide du paquet.

Une ACL IP classique ne crée pas une route, ne résout pas une adresse MAC et ne remplace pas une politique de routage. Elle filtre du trafic qui arrive à un point de contrôle ou qui en sort. Une route correcte vers la destination ne garantit donc pas que le paquet sera transmis : l'ACL peut le bloquer. Inversement, une règle `permit` ne rend pas une destination joignable si aucune route n'existe ou si le prochain saut est indisponible.

On distingue notamment :

- **ACL IPv4 standard** : elle examine principalement l'adresse source IPv4. Elle convient au contrôle de provenance, mais elle ne permet pas de distinguer finement plusieurs destinations ou services.
- **ACL IPv4 étendue** : elle peut examiner l'adresse source, l'adresse de destination, le protocole IP et, pour les protocoles pris en charge, les ports source et destination ou certains paramètres associés.
- **ACL IPv6** : elle filtre le trafic IPv6 en fonction des préfixes, des protocoles et des critères pris en charge par la plateforme. Sa syntaxe et son application diffèrent de celles des ACL IPv4.
- **ACL de ligne VTY** : elle limite les sources autorisées à ouvrir des sessions de gestion sur les lignes virtuelles, par exemple SSH. Elle ne doit pas être confondue avec une ACL de filtrage transit appliquée à une interface.
- **ACL de contrôle du plan de contrôle ou mécanismes apparentés** : ils protègent l'accès au processeur et aux services du routeur. Leur conception demande une analyse particulière, car ils peuvent affecter les protocoles qui maintiennent le réseau opérationnel.

### 1.2. Algorithme d'évaluation : première correspondance

L'algorithme classique d'une ACL est séquentiel : le paquet est comparé aux entrées dans leur ordre. Dès qu'une entrée correspond à tous les critères, l'action `permit` ou `deny` est appliquée et l'évaluation s'arrête. Si aucune entrée explicite ne correspond, le paquet rencontre un refus implicite à la fin de la liste.

```text
    Paquet reçu sur une interface
                 |
                 v
       +---------------------+
       | ACL présente dans   |
       | la direction choisie|
       +----------+----------+
                  |
                  v
       +---------------------+
       | Examiner l'entrée 1 |
       +----------+----------+
                  |
          Correspondance ?
             /       \
           oui       non
            |         |
            v         v
       +---------+  +------------------+
       | PERMIT  |  | Entrée suivante  |
       | ou DENY |  +--------+---------+
       +---------+           |
            ^                +----> répéter
            |
            |
       Fin d'ACL sans correspondance
            |
            v
       +-----------------+
       | DENY implicite  |
       +-----------------+
```

L'ordre des ACE (*Access Control Entries*) est par conséquent une composante fonctionnelle de la politique, pas une simple question de présentation. Considérons les entrées suivantes :

```cisco
ip access-list extended EXEMPLE
 10 permit ip any any
 20 deny tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 23
```

La deuxième règle ne sera jamais atteinte par un paquet correspondant à la première. L'intention probable — refuser Telnet tout en autorisant le reste — n'est pas obtenue. La règle de refus devrait précéder la règle générale d'autorisation, si tel est bien le besoin de sécurité.

Les ACL nommées avec numéros de séquence permettent d'insérer ou de retirer plus facilement une entrée spécifique, selon la plateforme. Les ACL numérotées historiques et certains systèmes ont des possibilités de modification plus limitées. Même si un équipement accepte une syntaxe particulière, il faut vérifier l'ordre effectivement affiché par `show access-lists` après chaque changement.

### 1.3. Refus implicite final

L'absence d'une règle `permit` correspondante équivaut à un refus final. Cette propriété favorise le principe du moindre privilège, mais provoque fréquemment des coupures lorsqu'une ACL est appliquée à une interface sans prévoir tous les flux nécessaires.

Il ne faut pas ajouter automatiquement `permit ip any any` à la fin pour « faire fonctionner le réseau ». Cette règle peut rendre l'ACL presque inutile. Il faut plutôt identifier les flux légitimes manquants : DNS, DHCP, NTP, supervision, authentification, mises à jour, applications métier ou protocoles de routage, selon le rôle de l'interface.

Avant d'appliquer une ACL en production, prévoir une matrice des flux autorisés aide à réduire les oublis. Une matrice minimale indique la source, la destination, le protocole, le port, le sens d'initiation et la justification. La matrice distingue également les flux transit des connexions destinées au routeur lui-même.

### 1.4. Wildcard masks et correspondance des adresses

Dans les ACL IPv4 Cisco classiques, un masque générique indique quels bits d'une adresse doivent être comparés. Un bit `0` signifie que le bit correspondant doit être identique ; un bit `1` signifie que ce bit peut varier. Le wildcard est souvent l'inverse bit à bit du masque de sous-réseau, mais les wildcards ne sont pas obligatoirement le complément d'un masque CIDR standard : ils peuvent exprimer d'autres motifs.

| Préfixe ou masque de réseau | Wildcard habituelle | Exemple d'utilisation |
|---|---|---|
| `255.255.255.255` (`/32`) | `0.0.0.0` | Hôte unique |
| `255.255.255.0` (`/24`) | `0.0.0.255` | Sous-réseau `/24` |
| `255.255.0.0` (`/16`) | `0.0.255.255` | Sous-réseau `/16` |
| `255.255.255.252` (`/30`) | `0.0.0.3` | Bloc de quatre adresses |
| N'importe quelle adresse | `255.255.255.255` | `any` |

La commande suivante autorise une source appartenant à `192.168.10.0/24` :

```cisco
permit ip 192.168.10.0 0.0.0.255 any
```

La commande suivante vise uniquement un hôte :

```cisco
permit ip host 192.168.10.25 any
```

Le mot-clé `host` évite d'écrire l'adresse suivie de `0.0.0.0`. Le mot-clé `any` correspond à toute adresse source ou destination dans le champ où il est utilisé. Il ne signifie pas à lui seul que tous les protocoles sont autorisés : l'action et le protocole de la règle restent déterminants.

Un wildcard non contigu peut représenter un motif complexe, mais il est plus difficile à auditer. Dans les politiques d'entreprise, privilégier les préfixes standards et les groupes nommés favorise la lisibilité. Lorsque l'intention requiert une wildcard inhabituelle, la documenter et tester plusieurs adresses positives et négatives.

### 1.5. ACL standard ou étendue

Une ACL standard est utile lorsqu'on veut autoriser ou refuser une source indépendamment de la destination. Elle se place souvent plus près de la destination, afin de ne pas bloquer cette source lorsqu'elle doit atteindre d'autres réseaux. Cette recommandation est un principe de conception, pas une loi absolue : la topologie, la capacité de l'équipement et l'objectif de sécurité peuvent justifier une autre position.

Une ACL étendue peut distinguer les destinations, les ports et les protocoles. On la place souvent près de la source afin de rejeter tôt le trafic interdit et d'éviter qu'il traverse inutilement le réseau. Cependant, une politique centralisée ou un besoin de préserver certains flux peut conduire à un placement différent. Le bon emplacement est celui qui applique la politique au point où le trafic est observable, avec le moins d'effets secondaires possible.

| Critère | ACL standard | ACL étendue |
|---|---|---|
| Adresse source | Oui | Oui |
| Adresse destination | Non, dans la logique standard classique | Oui |
| Ports TCP/UDP | Non | Oui, pour les protocoles pris en charge |
| Choix du protocole IP | Généralement non au-delà du filtrage IP source | Oui |
| Utilisation typique | Contrôle par provenance | Contrôle par flux ou service |
| Risque de surblocage | Élevé si appliquée trop tôt | Dépend de la précision et de l'emplacement |

### 1.6. Filtrage des ports TCP et UDP

Une ACL étendue peut examiner les ports source et destination des paquets TCP ou UDP. Il faut bien distinguer les deux. Dans une connexion cliente vers serveur, le client utilise généralement un port source éphémère et le serveur écoute sur un port destination connu. Pour HTTPS, la règle qui vise un serveur web doit habituellement examiner le port destination `443` du trafic initial.

Exemple :

```cisco
permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
```

Cette règle autorise le trafic TCP provenant du réseau utilisateur à destination de l'hôte `192.168.20.10`, lorsque le port de destination vaut 443. Elle n'autorise pas automatiquement tous les protocoles vers ce serveur et ne rend pas le service HTTPS disponible s'il n'écoute pas réellement sur ce port.

Les opérateurs de port courants incluent `eq` (égal), `neq` (différent), `lt` (inférieur à), `gt` (supérieur à) et des plages lorsque la syntaxe de la plateforme les prend en charge. Toujours vérifier dans quel champ s'applique l'opérateur. Par exemple, dans `permit tcp any eq 443 any`, le port 443 concerne le port source, alors que `permit tcp any any eq 443` vise le port destination.

La commande `permit tcp any any established` est parfois utilisée pour autoriser des paquets TCP qui portent certains indicateurs ACK ou RST. Elle ne constitue pas une inspection d'état complète : des paquets peuvent porter ces indicateurs sans appartenir à une session légitime. Elle ne s'applique pas à UDP et ne doit pas être présentée comme un mécanisme général de « retour de session » équivalent à un pare-feu stateful.

### 1.7. Protocole IP et ICMP

Les ACL étendues peuvent filtrer des protocoles tels que TCP, UDP, ICMP, OSPF, EIGRP ou le protocole IP générique, sous réserve des capacités de la plateforme. Le mot-clé `ip` autorise ou refuse le trafic IPv4 correspondant à tout protocole IP, pas seulement TCP et UDP.

ICMP contribue au diagnostic et au bon fonctionnement de certains mécanismes IP. Bloquer tous les messages ICMP sans analyse peut perturber le ping, le diagnostic d'erreurs, la découverte de MTU par chemin (*Path MTU Discovery*) et certains comportements de réseau. La bonne pratique consiste à décider quels types de messages sont nécessaires plutôt qu'à autoriser ou refuser ICMP aveuglément.

IPv6 dépend fortement d'ICMPv6 pour la découverte de voisins, la découverte de routeurs et la signalisation d'erreurs. Les règles IPv6 doivent donc préserver les messages requis par le protocole et la conception du réseau. Une politique copiée directement d'IPv4 sans tenir compte d'ICMPv6 peut rompre la connectivité même si les routes semblent correctes.

### 1.8. Direction in et out

Une ACL appliquée `in` est évaluée sur les paquets lorsqu'ils entrent sur l'interface. Une ACL appliquée `out` est évaluée sur les paquets qui la quittent. La direction est relative à l'interface du routeur, pas à l'utilisateur qui a initié la communication ni au sens intuitif du dessin.

```text
    PC-A ----> [ G0/0  ROUTEUR  G0/1 ] ----> Serveur B
                  |             |
             ACL IN sur      ACL OUT sur
             G0/0 examine   G0/1 examine
             le paquet à    le paquet avant
             son entrée     de quitter G0/1
```

Une même conversation est composée de paquets dans les deux sens. Lorsqu'une ACL est appliquée en entrée sur l'interface LAN des clients, elle examine le trafic qui quitte ces clients et arrive au routeur. Elle n'examine pas directement les réponses qui reviennent sur une autre interface. Une autre ACL peut les filtrer, selon la conception. Les conséquences doivent être calculées à partir du chemin réel des deux directions.

Sur un commutateur de couche 3, une ACL appliquée à une interface VLAN (SVI) suit le point de vue de cette interface logique. Une ACL `in` sur `interface Vlan10` examine le trafic venant du VLAN 10 vers le commutateur de couche 3. Une ACL `out` sur cette SVI examine généralement le trafic acheminé vers le VLAN 10. Vérifier l'architecture exacte : VLAN, ports, SVI, sous-interfaces de routeur et interfaces routées peuvent changer le point où un paquet est observé.

### 1.9. Où placer les ACL : méthode de conception

La règle de conception « ACL standard près de la destination, ACL étendue près de la source » est une bonne heuristique classique, mais elle n'est pas suffisante dans tous les environnements. L'emplacement dépend aussi de la direction, du type d'équipement, des chemins alternatifs, de la redondance et du trafic que l'organisation veut empêcher d'atteindre le réseau central.

Pour choisir un emplacement :

1. Dessiner le parcours du trafic et identifier les interfaces L3 traversées.
2. Définir le point qui voit le trafic dans le sens à filtrer.
3. Déterminer si l'ACL doit filtrer le transit, l'accès au routeur lui-même ou les deux.
4. Vérifier les protocoles de contrôle et services d'infrastructure nécessaires sur ce lien.
5. Estimer le volume de trafic et le coût du traitement, notamment sur des équipements à ressources ACL limitées.
6. Vérifier si un autre chemin contourne le point de filtrage.
7. Tester le trafic autorisé, le trafic interdit et les flux de réponse.

Placer une ACL sur un lien redondant seulement, tout en laissant une route de secours sans filtrage équivalent, crée une faille de politique. Toutes les routes possibles vers une destination sensible doivent être étudiées.

### 1.10. ACL et trafic destiné au routeur

Il faut distinguer les paquets qui traversent le routeur des paquets dont le routeur est lui-même la destination. Par exemple, un paquet SSH vers l'adresse de gestion du routeur se termine sur l'équipement, tandis qu'un paquet HTTPS que le routeur transmet vers un serveur distant constitue du trafic transit.

Les ACL d'interface peuvent influencer certains paquets en fonction de la plateforme et du traitement. Toutefois, pour administrer les lignes VTY, une ACL standard appliquée avec `access-class` fournit un contrôle ciblé des sources de gestion. La protection du plan de contrôle peut nécessiter des mécanismes supplémentaires, tels que Control Plane Policing (CoPP), auxquels une ACL de transit ne se substitue pas.

Une ACL de gestion doit être restrictive : autoriser uniquement le réseau d'administration prévu, limiter les protocoles de gestion à SSH plutôt que Telnet, et s'assurer qu'une voie de secours contrôlée existe avant toute modification à distance. Une règle VTY incorrecte peut couper l'accès à l'équipement sans affecter le trafic utilisateur, ce qui rend une procédure de retour arrière particulièrement importante.

### 1.11. ACL nommées, séquences et maintenabilité

Les ACL nommées facilitent la lecture de l'intention. Des noms tels que `USERS-IN`, `GUEST-EDGE-IN` ou `MGMT-VTY` sont plus informatifs que des numéros isolés, surtout lorsque le réseau contient de nombreuses politiques. Ajouter des commentaires au moyen de `remark` explique la raison d'une règle et peut indiquer un ticket, un propriétaire applicatif ou une date de révision.

Exemple :

```cisco
ip access-list extended USERS-IN
 remark Autoriser HTTPS vers le portail interne
 10 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
 remark Bloquer les autres acces au VLAN serveurs
 20 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 log
 30 permit ip 192.168.10.0 0.0.0.255 any
```

Les numéros de séquence permettent d'insérer une nouvelle entrée entre des règles existantes, si cette fonction est prise en charge. Une modification d'ACL active doit être faite avec précaution : certaines commandes remplacent ou réordonnent les éléments, et un comportement de plateforme ne doit pas être supposé à partir d'un autre modèle. Après modification, vérifier la sortie complète de l'ACL et ses compteurs. Il faut aussi conserver une copie de la configuration précédente pour revenir à un état connu.

### 1.12. Compteurs, journalisation et observation

Les compteurs de correspondance facilitent le dépannage. Si une règle de refus prévue affiche un compteur nul alors que le trafic est censé la traverser, la cause peut être une ACL appliquée sur la mauvaise interface, une mauvaise direction, une route qui emprunte un autre chemin, un critère trop précis ou l'absence réelle de ce trafic. Un compteur incrémenté confirme qu'un paquet a correspondu à la règle, mais ne prouve pas à lui seul que cette règle est la cause unique du problème applicatif.

L'option `log` peut générer des messages de journal lorsqu'une ACE est correspondue. Le détail et la fréquence des événements dépendent de la plateforme. Une règle `deny ... log` peut être utile pendant un diagnostic ou pour documenter certaines violations, mais la journalisation excessive d'un trafic volumineux peut solliciter le processeur ou saturer un collecteur Syslog. Il faut éviter de journaliser sans contrôle chaque paquet d'un flux de masse.

Une méthode de diagnostic efficace combine plusieurs vues :

- configuration de l'ACL et de son attachement ;
- compteurs par entrée ;
- état des interfaces et table de routage ;
- capture de paquets lorsqu'elle est possible ;
- journaux système ;
- tests depuis un hôte réellement situé dans le réseau source et vers la destination exacte.

### 1.13. Fragmentation IP et critères de couche 4

Lorsqu'un paquet IP est fragmenté, les informations de couche 4 comme le port TCP/UDP ne figurent pas nécessairement dans tous les fragments. Le premier fragment contient l'en-tête de transport ; les fragments suivants peuvent ne pas en contenir. Les plateformes peuvent traiter les règles qui examinent les ports et les fragments selon des détails d'implémentation particuliers.

Ce point compte dans la conception d'ACL avancées : une règle ciblant un port ne doit pas être supposée examiner de manière identique chaque fragment. Les règles de fragments, les ACL avec mot-clé `fragments` et le traitement des fragments non initiaux varient selon les familles logicielles et les types d'ACL. Il faut valider le comportement documenté de la plateforme et tester avec le chemin MTU réel, plutôt que copier une règle isolée.

Le filtrage des fragments doit aussi tenir compte de la découverte de MTU par chemin et des besoins de l'application. Une politique trop agressive peut laisser passer les petits paquets mais bloquer les transferts volumineux, ce qui donne l'impression d'une application intermittente.

### 1.14. ACL IPv6 : différences à respecter

Les ACL IPv6 utilisent les préfixes avec longueur explicite, comme `2001:db8:10::/64`, plutôt que les wildcard masks IPv4 traditionnelles. Sur IOS/IOS XE, une ACL IPv6 est généralement créée avec `ipv6 access-list NOM` puis appliquée à une interface à l'aide d'une commande de filtrage IPv6 prise en charge, par exemple `ipv6 traffic-filter NOM in`.

La politique IPv6 doit être conçue séparément de la politique IPv4. Un réseau en double pile peut être protégé en IPv4 tout en laissant IPv6 ouvert, ou inversement. Les règles doivent couvrir les adresses globales, les adresses link-local pertinentes et les messages ICMPv6 nécessaires au fonctionnement du réseau. Ne pas transposer automatiquement une ACL IPv4 sans plan de test IPv6.

Les champs de l'en-tête d'extension IPv6 peuvent compliquer l'inspection de la couche supérieure ; les capacités de la plateforme déterminent les options de filtrage disponibles. Dans un réseau de production, consulter la documentation de la version IOS/IOS XE exacte est indispensable.

### 1.15. ACL, VLANs et segmentation

Les VLANs séparent les domaines de diffusion de couche 2, mais ils n'empêchent pas nécessairement les communications entre réseaux lorsque le routage inter-VLAN est activé. Les ACL appliquées aux interfaces VLAN d'un commutateur de couche 3 permettent d'exprimer une politique entre ces segments.

Par exemple, les postes utilisateurs peuvent avoir besoin d'accéder à un serveur HTTPS dans le VLAN serveurs, mais ne doivent pas accéder aux interfaces d'administration des commutateurs. Le VLAN invité peut avoir besoin d'un accès Internet et DNS, sans accès aux réseaux internes. Ces exigences doivent devenir des règles explicites, plutôt que d'utiliser seulement le fait que les appareils se trouvent dans des VLANs distincts.

Une ACL n'isole que le trafic qui la traverse. Les communications dans un même VLAN commuté peuvent ne pas passer par la SVI L3 tant qu'aucun routage n'est nécessaire. Si la politique exige un filtrage entre les hôtes du même sous-réseau, il faut étudier les fonctions de sécurité de couche 2, la segmentation supplémentaire ou une architecture où le trafic traverse un point de contrôle approprié.

### 1.16. ACL et protocoles de routage

Une ACL appliquée sur une interface de transit peut bloquer les messages de protocole nécessaires à la formation d'adjacences ou à l'échange de routes. EIGRP utilise le protocole IP 88 ; OSPF utilise le protocole IP 89 ; BGP utilise TCP, généralement le port 179 ; RIP utilise UDP 520 pour IPv4. Ces exemples montrent qu'une liste qui autorise seulement TCP et UDP peut bloquer des protocoles de routage qui ne reposent pas sur ces transports.

Avant d'appliquer une ACL sur un lien de routage, inventorier les messages nécessaires dans les deux directions. Pour OSPF, il faut notamment considérer le multicast ou le comportement unicast selon le déploiement. Pour EIGRP, considérer les messages vers le multicast de contrôle utilisé sur le segment. Les détails exacts dépendent du protocole, de la configuration et de la plateforme.

Un mauvais filtrage de protocole de routage peut entraîner une perte de voisinage, la disparition de routes et des détours, même si les paquets applicatifs n'étaient pas directement visés par la règle. L'état des voisins et la table de routage doivent faire partie des tests de non-régression après changement.

### 1.17. ACL et NAT

La relation entre ACL et NAT dépend de la plateforme et du point où les critères sont évalués. Sur les routeurs Cisco IOS classiques, une ACL utilisée pour sélectionner les adresses sources à traduire par NAT n'est pas simplement une ACL de sécurité appliquée à une interface : elle sert à identifier le trafic concerné par la traduction. Une ACL NAT qui contient `permit` indique les paquets qui correspondent à la sélection NAT ; elle ne doit pas être supposée bloquer les autres paquets comme le ferait une ACL de filtrage appliquée avec `ip access-group`.

Cette distinction évite un piège courant : réutiliser la même liste pour sélectionner une traduction et pour sécuriser une interface. Il est préférable de maintenir des ACL distinctes lorsque leur finalité diffère, avec des noms explicites qui montrent la fonction de chacune.

### 1.18. ACL matérielles et limites d'échelle

Sur les commutateurs et routeurs modernes, une partie du filtrage peut être exécutée dans le matériel, notamment au travers de ressources de type TCAM. Cela permet un débit élevé, mais les ressources de correspondance ne sont pas infinies. Une politique très volumineuse ou l'utilisation de fonctions combinées peut dépasser les capacités disponibles sur une plateforme donnée ou être compilée de façon différente de ce qu'indique la configuration logique.

Les groupes d'objets peuvent simplifier les politiques et éviter de répéter des sous-réseaux ou des ports dans de nombreuses ACE. Toutefois, leur disponibilité, leur syntaxe et leur compatibilité avec certaines interfaces, fonctions ou plateformes varient. Une ACL plus courte en configuration n'est pas nécessairement moins coûteuse en ressources matérielles : il faut consulter les limites de la plateforme et les états de programmation des ACL lorsque ces outils sont disponibles.

Les ACL doivent être conçues pour être lisibles, stables et testables, pas seulement pour avoir le moins de lignes possible. Une politique découpée en listes claires par zone ou fonction est souvent plus facile à exploiter qu'une unique ACL géante.

> **Piège :** Une ACL ne doit pas être interprétée comme une liste indépendante de règles où chaque ligne serait évaluée. L'évaluation s'arrête à la première correspondance et tout paquet qui atteint la fin sans correspondance est refusé par l'entrée implicite. Autre piège fréquent : la règle `permit ip any any` placée trop tôt rend les refus suivants inopérants. Enfin, `permit tcp any any established` ne fournit pas l'état de session complet d'un pare-feu ; il ne faut pas l'utiliser comme une garantie générale de sécurité du trafic retour.

```text
    Exemple de filtrage d'un réseau utilisateur

    VLAN 10 - Utilisateurs                   VLAN 20 - Serveurs
    192.168.10.0/24                          192.168.20.0/24
    +------------------+                     +------------------+
    | PC-A              |                     | DNS  .53          |
    | PC-B              |                     | Web  .10          |
    +---------+--------+                     +---------+--------+
              |                                        |
              v                                        v
        +---------------------------------------------------+
        | Commutateur L3 / routeur                          |
        | SVI VLAN 10 : 192.168.10.1                        |
        | SVI VLAN 20 : 192.168.20.1                        |
        |                                                   |
        | ACL USERS-IN appliquee en entree sur VLAN 10      |
        | 1. Autoriser DNS vers 192.168.20.53               |
        | 2. Autoriser HTTPS vers 192.168.20.10             |
        | 3. Refuser les autres acces vers VLAN 20           |
        | 4. Autoriser le trafic utilisateur restant prevu  |
        +---------------------------+-----------------------+
                                    |
                                    v
                              Réseau amont

    Le filtrage de VLAN 10 ne remplace pas les contrôles
    applicables aux autres VLANs ni la protection des services.
```


## 2. Configuration et Pratique

### 2.1. Laboratoire et objectifs

Le laboratoire utilise un commutateur de couche 3 ou un routeur capable de réaliser le routage entre les VLANs. Les interfaces logiques sont les suivantes :

| Zone | Réseau | Passerelle | Besoin principal |
|---|---|---|---|
| Utilisateurs, VLAN 10 | `192.168.10.0/24` | `192.168.10.1` | DNS, HTTPS vers portail et autres destinations autorisées |
| Serveurs, VLAN 20 | `192.168.20.0/24` | `192.168.20.1` | DNS `192.168.20.53`, HTTPS `192.168.20.10` |
| Invités, VLAN 30 | `192.168.30.0/24` | `192.168.30.1` | DNS et accès Internet, aucun accès libre aux réseaux internes |
| Administration, VLAN 99 | `192.168.99.0/24` | `192.168.99.1` | Administration des équipements depuis un poste contrôlé |

Les exemples sont illustratifs. Les adresses doivent être remplacées par celles du réseau réel et les règles doivent refléter les services réellement nécessaires. Il faut aussi prévoir DHCP, DNS, NTP, authentification, supervision et services de sécurité si l'infrastructure en dépend.

### 2.2. ACL étendue pour le VLAN utilisateurs

La politique suivante autorise DNS vers un serveur dédié, HTTPS vers le portail interne, refuse l'accès aux autres hôtes du VLAN serveurs et autorise ensuite le reste du trafic utilisateur tel que prévu par l'architecture. L'autorisation finale vers `any` est volontairement large : en production, elle doit être remplacée par une liste d'autorisations plus étroite si les utilisateurs ne sont pas censés accéder à toutes les autres destinations.

```cisco
ip access-list extended USERS-IN
 remark DNS UDP vers le resolver interne
 10 permit udp 192.168.10.0 0.0.0.255 host 192.168.20.53 eq 53
 remark DNS TCP : réponses volumineuses et autres echanges DNS
 20 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.53 eq 53
 remark Portail interne en HTTPS
 30 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
 remark Bloquer les autres acces directs au VLAN serveurs
 40 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 log
 remark Exemple pedagogique : autoriser les autres destinations prevues
 50 permit ip 192.168.10.0 0.0.0.255 any
```

Cette ACL est appliquée en entrée de la SVI VLAN 10 :

```cisco
interface Vlan10
 description Passerelle du VLAN utilisateurs
 ip address 192.168.10.1 255.255.255.0
 ip access-group USERS-IN in
```

Il faut vérifier que l'interface VLAN existe, qu'elle est opérationnelle et que l'équipement prend en charge les ACL sur SVI. La règle 40 bloque les accès au VLAN serveurs qui ne correspondent pas aux règles DNS et HTTPS précédentes. La règle 50 permet le trafic vers les autres destinations, ce qui pourrait inclure d'autres réseaux internes. Il faut donc ajouter les refus ou autorisations nécessaires avant cette ligne et tester tous les cas de la matrice de flux.

Une politique de production plus restrictive pourrait autoriser explicitement quelques réseaux externes ou services et terminer par le refus implicite, plutôt que d'autoriser tout ce qui n'est pas dans le VLAN serveurs. Le choix est fonction du besoin réel, et non d'une préférence abstraite pour une syntaxe.

### 2.3. ACL pour le VLAN invité

Le VLAN invité doit généralement accéder aux services nécessaires à son fonctionnement et à Internet, sans accéder aux postes utilisateurs, aux serveurs internes ni à l'administration. L'exemple autorise un DNS interne et le portail HTTPS ; si les invités utilisent plutôt un résolveur public ou un portail captif, les lignes doivent être adaptées.

```cisco
ip access-list extended GUEST-IN
 remark Autoriser DNS vers le resolver approuve
 10 permit udp 192.168.30.0 0.0.0.255 host 192.168.20.53 eq 53
 20 permit tcp 192.168.30.0 0.0.0.255 host 192.168.20.53 eq 53
 remark Autoriser HTTPS vers le portail qui doit etre visible aux invites
 30 permit tcp 192.168.30.0 0.0.0.255 host 192.168.20.10 eq 443
 remark Interdire l'acces aux postes internes
 40 deny ip 192.168.30.0 0.0.0.255 192.168.10.0 0.0.0.255 log
 remark Interdire les autres acces au VLAN serveurs
 50 deny ip 192.168.30.0 0.0.0.255 192.168.20.0 0.0.0.255 log
 remark Interdire l'administration des equipements
 60 deny ip 192.168.30.0 0.0.0.255 192.168.99.0 0.0.0.255 log
 remark Autoriser le trafic vers les destinations externes
 70 permit ip 192.168.30.0 0.0.0.255 any
```

Appliquer sur l'interface VLAN 30 :

```cisco
interface Vlan30
 description Passerelle du VLAN invite
 ip address 192.168.30.1 255.255.255.0
 ip access-group GUEST-IN in
```

Cette règle d'autorisation finale ne distingue pas Internet du reste des préfixes qui ne sont pas explicitement refusés. Dans un réseau où des réseaux internes supplémentaires existent, les ajouter à la liste de refus ou, de préférence, définir les destinations autorisées de manière explicite. La segmentation doit être évaluée sur tous les chemins, y compris les tunnels VPN, les liens de secours et les routes ajoutées à l'avenir.

### 2.4. ACL standard pour protéger l'administration VTY

Une ACL standard peut limiter les sources autorisées à ouvrir une session vers les lignes virtuelles. Dans l'exemple, seules les adresses du VLAN d'administration sont permises. Adapter la plage aux postes d'administration réellement autorisés ; un réseau d'administration trop large réduit la valeur de cette mesure.

```cisco
ip access-list standard MGMT-VTY
 remark Sources autorisees a administrer les equipements
 10 permit 192.168.99.0 0.0.0.255
 20 deny any log
!
ip domain-name exemple.local
crypto key generate rsa modulus 2048
ip ssh version 2
username netadmin privilege 15 secret RemplacerParUnSecretFort
!
line vty 0 4
 login local
 transport input ssh
 access-class MGMT-VTY in
```

La commande de génération RSA peut présenter une syntaxe différente selon la version IOS/IOS XE et les politiques cryptographiques supportées. Le nom de domaine et le secret sont des exemples, à remplacer selon les standards de l'organisation. La commande `access-class` s'applique aux sessions de gestion VTY ; elle ne filtre pas à elle seule le trafic transitant par les interfaces.

**Important :** avant d'appliquer une ACL VTY à distance, vérifier que l'adresse source de la session d'administration est bien dans le périmètre autorisé. Prévoir une console locale, un accès hors bande ou une procédure de retour arrière. Une ligne erronée peut bloquer l'accès à distance au routeur.

### 2.5. Ajouter des remarques et modifier une ACE

Les remarques expliquent la finalité de la liste et le rôle de règles importantes. Une ACL lisible est plus simple à auditer et moins dangereuse à modifier. Pour ajouter une autorisation HTTPS à une destination supplémentaire, insérer une règle à un numéro de séquence approprié, avant le refus générique qui la bloquerait.

```cisco
ip access-list extended USERS-IN
 25 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.25 eq 443
```

La disponibilité de l'insertion par numéro dépend du système. Après chaque modification, vérifier l'ordre de toutes les ACE. Si la règle est placée après une règle de refus qui correspond au même paquet, le trafic restera bloqué. Une commande acceptée par l'interpréteur ne garantit pas que la politique obtenue soit celle attendue.

Pour retirer une entrée, utiliser la commande `no` correspondant à cette entrée ou à son numéro de séquence, selon la syntaxe disponible. Éviter de supprimer une ACL active sans comprendre la conséquence : le comportement peut devenir permissif ou restrictif selon le moment où elle est détachée et les autres mécanismes de filtrage présents.

### 2.6. ACL IPv6 de base

Sur les versions qui prennent en charge la syntaxe IOS classique, une ACL IPv6 peut être construite avec des préfixes explicites puis appliquée à une interface :

```cisco
ipv6 access-list USERS-V6-IN
 permit tcp 2001:db8:10::/64 host 2001:db8:20::10 eq 443
 deny ipv6 2001:db8:10::/64 2001:db8:20::/64 log
 permit ipv6 2001:db8:10::/64 any
!
interface Vlan10
 ipv6 traffic-filter USERS-V6-IN in
```

Cet exemple ne constitue pas une politique IPv6 universelle. Il ne montre pas à lui seul toutes les autorisations ICMPv6 nécessaires, les besoins du DHCPv6 ni les spécificités d'un environnement avec adresses link-local. Avant de l'appliquer, ajouter les règles indispensables au fonctionnement IPv6 de la plateforme et tester la découverte de voisins, la découverte de routeurs, la résolution de MTU et les applications. La syntaxe de filtrage et les champs pris en charge doivent être confirmés dans la documentation de la version logicielle exacte.

### 2.7. Groupes d'objets (lorsqu'ils sont supportés)

Sur certaines plateformes IOS/IOS XE, les groupes d'objets peuvent rassembler des réseaux ou des ports afin de rendre les ACL plus maintenables. Cela permet de définir une application ou une zone une fois, puis de réutiliser cette définition dans plusieurs entrées. La syntaxe et les limites matérielles varient selon le matériel, la version et les fonctionnalités activées.

Un exemple conceptuel :

```cisco
object-group network SERVEURS_WEB
 192.168.20.10
 192.168.20.25
!
object-group service WEB-PORTS tcp
 port-object eq 443
!
ip access-list extended WEB-ACCESS
 permit tcp 192.168.10.0 0.0.0.255 object-group SERVEURS_WEB object-group WEB-PORTS
```

Ce fragment illustre l'intention, mais la syntaxe précise de définition et de référence des groupes dépend de la plateforme Cisco. Certains équipements n'acceptent pas les groupes de service ou les groupes imbriqués sous cette forme. Tester la syntaxe et vérifier la configuration compilée avant de l'utiliser. Le recours aux groupes ne dispense pas de gérer l'ordre des ACE et les refus implicites.

### 2.8. Vérifier l'attachement de l'ACL

La configuration d'une ACL ne signifie pas qu'elle filtre effectivement du trafic. Il faut vérifier qu'elle est attachée à la bonne interface et dans la bonne direction.

```cisco
show access-lists
show ip interface Vlan10
show running-config interface Vlan10
show running-config | section ip access-list
```

Selon la plateforme, `show ip interface` indique les ACL entrantes et sortantes associées à l'interface. `show access-lists` affiche les ACE et peut montrer leurs compteurs. Les filtres de sortie du terminal (`| section`) sont disponibles sur de nombreux systèmes Cisco, mais il faut employer une syntaxe adaptée à l'OS exact.

Toujours confirmer :

- le nom exact de l'ACL ;
- la présence de toutes les entrées attendues ;
- leur ordre ;
- l'interface et la direction ;
- les compteurs avant et après un test ;
- l'absence de règle plus générale qui masque une règle précise.

### 2.9. Tester la politique

Une ACL doit être validée par une matrice de tests positifs et négatifs. Par exemple :

| Source | Destination | Service | Résultat attendu |
|---|---|---|---|
| Utilisateur VLAN 10 | DNS `192.168.20.53` | UDP/53 | Autorisé |
| Utilisateur VLAN 10 | DNS `192.168.20.53` | TCP/53 | Autorisé si requis |
| Utilisateur VLAN 10 | Portail `192.168.20.10` | TCP/443 | Autorisé |
| Utilisateur VLAN 10 | Serveur interne non publié | IP quelconque | Refusé par la règle VLAN serveurs |
| Invité VLAN 30 | Hôte utilisateur VLAN 10 | IP quelconque | Refusé |
| Invité VLAN 30 | Serveur interne autre que DNS/portail | IP quelconque | Refusé |
| Poste non autorisé | SSH vers routeur | TCP/22 | Refusé par l'ACL VTY |

Les tests doivent être effectués depuis de véritables sources représentatives : un test réalisé depuis le routeur lui-même peut ne pas traverser la même ACL qu'un paquet provenant d'un poste. Pour les services TCP, vérifier l'établissement de la connexion applicative, pas seulement un ping. Pour DNS, vérifier la résolution et tenir compte du choix UDP/TCP. Pour les tests négatifs, observer les compteurs et les journaux sans générer de volume excessif.

### 2.10. Procédure de changement et retour arrière

Avant de modifier une ACL active, exporter ou copier la configuration actuelle, relever les compteurs, enregistrer une liste de tests de référence et comprendre le chemin de retour arrière. Une modification doit être courte et ciblée. Ne pas corriger simultanément plusieurs ACL, le routage et la configuration DNS : si le résultat change, la cause deviendra difficile à isoler.

Procédure recommandée :

1. Lire la politique actuelle et identifier la ligne concernée.
2. Décrire le flux attendu avec source, destination, protocole et sens.
3. Vérifier les règles précédentes et suivantes pour prévenir les effets de bord.
4. Préparer la commande de changement et la commande de retour arrière.
5. Appliquer pendant une fenêtre approuvée, si le risque le justifie.
6. Tester immédiatement les flux autorisés et interdits.
7. Examiner les compteurs, journaux et états de services.
8. Sauvegarder la configuration si les résultats sont conformes ; sinon revenir à l'état précédent.

Sur les équipements qui proposent une fonction de confirmation temporisée ou un mécanisme de rollback, suivre la procédure adaptée à cette plateforme. Ne pas supposer qu'elle existe partout. Pour une intervention distante, conserver une voie d'accès de secours indépendante de l'ACL modifiée.


## 3. Dépannage et Sécurité

### 3.1. Méthode de dépannage en couches

Lorsqu'un service devient inaccessible après l'application d'une ACL, distinguer quatre hypothèses : l'ACL bloque le paquet ; le paquet n'emprunte pas l'interface attendue ; le routage ou la résolution de couche 2 est défaillant ; le service distant ne répond pas. L'erreur la plus courante est de supposer immédiatement que l'ACL est fautive parce que le problème a été observé après un changement, sans vérifier le chemin réel.

Commencer par identifier la source et la destination exactes, le protocole et le port, puis le sens initial de la communication. Vérifier ensuite la table de routage et l'état des interfaces. Examiner l'attachement de l'ACL. Lire ses entrées dans l'ordre et vérifier les compteurs avant et après un test contrôlé. Si nécessaire, analyser une capture sur les deux côtés du point de filtrage.

### 3.2. Symptôme : un flux légitime est bloqué

Causes fréquentes :

- la règle `permit` manque ;
- le wildcard ne correspond pas au préfixe attendu ;
- le port est écrit dans le champ source au lieu du champ destination ;
- un `deny` plus général précède l'autorisation ;
- une ACL est appliquée dans la mauvaise direction ;
- l'ACL est attachée à une autre interface que celle parcourue par le paquet ;
- le trafic retour est filtré par une autre politique ;
- l'application utilise un protocole ou un port supplémentaire non prévu dans la matrice de flux.

La démarche n'est pas d'ajouter aveuglément `permit ip any any`. Il faut construire une règle ciblée, l'insérer avant le refus qui la bloque, tester le flux et conserver les restrictions non concernées. Une autorisation large peut faire disparaître le symptôme tout en annulant les objectifs de segmentation.

### 3.3. Symptôme : l'ACL semble ne rien filtrer

Si un trafic interdit traverse malgré la présence d'un `deny`, vérifier d'abord si le paquet traverse bien l'interface à laquelle l'ACL est attachée. Les chemins ECMP, les routes asymétriques, les tunnels, le routage local par une autre SVI ou un chemin de secours peuvent contourner le point de contrôle. Vérifier ensuite la direction et les compteurs.

Une autre cause est l'ordre : une règle générale `permit` placée avant le refus capture les paquets et les rend invisibles à la règle située plus bas. Il peut aussi s'agir d'une ACL NAT employée à tort comme ACL de sécurité, d'un filtrage appliqué au mauvais type de trafic ou d'une confusion entre l'ACL de transit et l'ACL VTY.

La vérification doit porter sur la configuration active, pas seulement sur un extrait de configuration préparé avant le changement. Examiner `show access-lists`, `show ip interface`, `show running-config` et la table de routage sur l'équipement qui traite réellement le paquet.

### 3.4. Symptôme : le ping échoue, mais HTTPS fonctionne

Le ping utilise ICMP, alors que HTTPS utilise TCP. Une ACL peut autoriser TCP/443 tout en refusant ICMP, volontairement ou à cause d'une règle plus générale. L'échec d'un ping ne prouve donc pas que le serveur est totalement inaccessible.

En sens inverse, un ping réussi ne garantit pas qu'un port applicatif accepte les connexions. Le service peut être arrêté, filtré localement par un pare-feu hôte ou lié à une adresse différente. Tester le service exact et examiner les règles propres à son protocole.

Pour un diagnostic réseau, contrôler également ICMP nécessaire à la découverte de MTU et aux erreurs IP. Les réseaux dont les ACL bloquent certains messages d'erreur peuvent présenter des applications qui établissent une session puis échouent lors d'un transfert volumineux.

### 3.5. Symptôme : un accès SSH au routeur est perdu

Une ACL VTY appliquée avec `access-class` peut exclure l'adresse source utilisée par l'administrateur. Avant l'application, vérifier l'adresse réellement vue par le routeur : elle peut être celle d'un bastion, d'un NAT ou d'un serveur d'administration plutôt que celle du poste final.

Si l'accès est perdu, utiliser la console ou un accès hors bande, puis examiner l'ACL VTY, les lignes VTY, `transport input`, la base locale d'utilisateurs et le routage vers le réseau de gestion. Ne pas enlever tous les contrôles sans documenter l'action ; rétablir une règle ciblée et tester depuis le bastion autorisé.

La meilleure prévention consiste à effectuer les changements d'accès de gestion avec une session de secours, une commande de retour arrière préparée et une vérification depuis la source autorisée avant de terminer la session existante.

### 3.6. Symptôme : les voisins de routage disparaissent

Si une ACL est appliquée sur une interface de transit, examiner les protocoles de routage et leurs messages de contrôle. Une règle `permit tcp` suivie d'un refus général de tout le reste peut empêcher EIGRP, OSPF ou d'autres protocoles de former ou de maintenir leurs relations.

Vérifier les commandes de voisinage du protocole utilisé, les compteurs de l'ACL et les règles qui correspondent au protocole IP concerné. Ne pas autoriser un protocole entier sans comprendre les voisins et interfaces légitimes : le but est de permettre les échanges requis uniquement sur les liens attendus.

Si les routes disparaissent, les applications peuvent devenir injoignables même si l'ACL ne filtre pas directement leurs ports. Le protocole de routage fournit les chemins dont le trafic applicatif dépend ; toute politique sur les liens doit considérer ce plan de contrôle.

### 3.7. Journalisation excessive et compteurs

L'option `log` est utile pour les refus ciblés, mais peut être coûteuse si elle est appliquée à une règle correspondant à un très grand volume de paquets. Les messages peuvent être limités, agrégés ou traités différemment selon le système. Une ACL conçue pour journaliser chaque paquet entrant sur un lien chargé peut provoquer une surcharge de journaux ou solliciter le processeur.

Pour diagnostiquer, préférer une période d'observation courte et une règle de journalisation ciblée sur le flux recherché. Utiliser les compteurs de correspondance comme indice de volume et compléter par des captures ou des traces lorsque c'est nécessaire. Toujours mesurer l'impact de la journalisation avant de la conserver durablement sur une règle fréquente.

Les compteurs matériels ne sont pas toujours mis à jour ou présentés exactement comme des compteurs logiciels. Selon l'architecture, les règles peuvent être compilées et exécutées dans le matériel. Interpréter les résultats selon la documentation du modèle, plutôt que conclure à une absence de trafic sur la seule base d'un compteur qui ne change pas comme prévu.

### 3.8. Pièges de syntaxe et de logique

Quelques erreurs reviennent souvent :

- confondre masque de sous-réseau et wildcard ;
- placer le port serveur dans le champ source ;
- oublier que l'évaluation s'arrête à la première correspondance ;
- oublier le refus implicite final ;
- autoriser trop largement avec `permit ip any any` ;
- appliquer une ACL entrante quand on voulait contrôler le trafic qui sort vers cette zone ;
- supposer que `established` rend l'ACL stateful ;
- réutiliser une ACL de sélection NAT pour filtrer la sécurité ;
- filtrer IPv4 sans définir une politique IPv6 équivalente ;
- oublier les protocoles de contrôle ou les services d'infrastructure ;
- supposer que tous les flux entre deux hôtes passent par le routeur ;
- ajouter `log` à une règle très fréquente sans mesurer les conséquences.

Un audit de configuration devrait vérifier ces points avant une mise en production. Une ACL fonctionne selon sa logique exacte, pas selon le commentaire que l'administrateur voulait exprimer.

### 3.9. Sécurisation par le moindre privilège

Une bonne politique n'est ni l'ACL la plus longue ni celle qui contient le plus de refus. Elle traduit les flux autorisés par une exigence vérifiable et bloque les autres, sans empêcher le fonctionnement des services d'infrastructure nécessaires.

Le principe du moindre privilège se décline ainsi : autoriser le minimum de sources vers le minimum de destinations et de ports ; séparer les règles utilisateurs, invités, serveurs et gestion ; éviter les autorisations globales ; documenter chaque exception ; réviser les règles devenues inutiles ; surveiller les changements et protéger l'accès administratif.

Il faut aussi traiter les effets de bord : un DNS interne peut utiliser UDP et TCP ; une application peut contacter des services d'authentification, de temps ou de mise à jour ; un protocole de surveillance peut être nécessaire pour l'exploitation. Ces besoins doivent être inventoriés et testés, pas ajoutés en autorisations générales après une panne.

### 3.10. Protection des ACL de gestion et contrôle du plan de contrôle

L'ACL VTY limite les sources pouvant ouvrir une session de gestion, mais ne remplace ni SSH, ni une authentification robuste, ni une segmentation du réseau d'administration. Il est préférable de combiner une source restreinte, SSH seulement, des secrets protégés, des comptes nominatifs si disponibles, une journalisation et une séparation du trafic de gestion.

La protection du processeur du routeur peut exiger des mécanismes de contrôle du plan de contrôle. Une ACL de transit n'est pas nécessairement équivalente à une politique CoPP. Les paquets destinés au routeur et ceux qui le traversent suivent des chemins de traitement différents selon la plateforme.

Toute politique qui filtre des protocoles de routage, ICMP ou les services de gestion doit être testée sur tous les liens où ces messages sont nécessaires. Bloquer un protocole de gestion non souhaité est utile ; bloquer les messages qui gardent l'infrastructure joignable peut provoquer une panne plus large que le flux initial.

### 3.11. Sécurité IPv6

La sécurité IPv6 doit être explicitement configurée. Le fait de déployer une ACL IPv4 sur un réseau dual-stack ne protège pas le trafic IPv6. Les adresses globales, les préfixes de sous-réseau, les adresses link-local et les mécanismes de découverte doivent être étudiés dans le contexte de la plateforme.

Ne pas bloquer aveuglément ICMPv6 : certains types sont nécessaires à Neighbor Discovery, Router Advertisement et Path MTU Discovery. Une ACL IPv6 doit préserver les échanges indispensables entre nœuds du même lien et avec les routeurs autorisés, tout en contrôlant les flux applicatifs selon la politique. Les mécanismes de sécurité de couche 2 tels que RA Guard peuvent être complémentaires dans les environnements compatibles, mais ils ne remplacent pas les ACL L3.

Le test IPv6 doit être équivalent au test IPv4 : valider les services autorisés, les destinations interdites, la gestion, la résolution de voisins et le comportement de l'application avec des adresses IPv6. Ne pas supposer qu'un service inaccessible en IPv4 le sera également en IPv6.

### 3.12. Revue périodique et documentation

Avec le temps, les ACL accumulent des règles temporaires devenues permanentes, des autorisations redondantes et des exceptions dont personne ne connaît la raison. Une revue régulière doit identifier les ACE inutilisées, les règles masquées par une entrée précédente, les autorisations globales, les règles `log` trop bavardes et les références à des systèmes retirés.

Pour chaque règle importante, conserver un objectif, un propriétaire applicatif, un ticket ou une référence de changement, ainsi qu'une date de révision si les processus de l'organisation le prévoient. Les compteurs nuls ne prouvent pas forcément qu'une règle est inutile : certains flux peuvent être saisonniers ou rares. Avant de supprimer une ACE, croiser les compteurs avec les journaux, les dépendances d'application et les périodes d'activité.

Les changements d'ACL doivent être inclus dans la gestion de configuration réseau. Sauvegarder la configuration, faire une comparaison avant/après, approuver le changement, tester et conserver les résultats. Cette discipline réduit les incidents causés par des règles temporaires oubliées ou des modifications non documentées.

> **Astuce :** Pendant un diagnostic, relève les compteurs de `show access-lists`, provoque un seul test bien défini depuis la source réelle, puis affiche à nouveau l'ACL. La règle dont le compteur augmente constitue un indice utile sur le chemin de décision. Combine ce résultat avec `show ip interface` pour confirmer l'attachement et la direction, puis avec `show ip route` pour vérifier le chemin. Cette méthode est plus fiable que modifier plusieurs ACE au hasard.

> **Danger :** Une ACL mal positionnée ou trop permissive peut exposer un réseau sensible ; une ACL trop restrictive peut couper l'accès d'administration, les protocoles de routage ou des services indispensables. Ne déploie pas une règle générique pour corriger rapidement une panne sans vérifier l'impact sur l'ensemble des flux. Pour toute modification distante, prépare un retour arrière et un moyen d'accès de secours. Sur les liens de transit et en IPv6, examine particulièrement les protocoles de contrôle dont le blocage peut provoquer une panne globale.


## Points à retenir

- **Une ACL est une liste ordonnée de critères, pas un ensemble de règles indépendantes.** La première ACE qui correspond décide du traitement ; si aucune ne correspond, le refus implicite final s'applique. L'ordre, les wildcards et les champs source/destination doivent donc être vérifiés avec précision.
- **L'emplacement et la direction comptent autant que la syntaxe.** Une ACL `in` et une ACL `out` ne voient pas les mêmes paquets. Les ACL de transit, les ACL VTY, les listes utilisées pour sélectionner du NAT et les protections du plan de contrôle n'ont pas le même rôle.
- **La mise en production exige des tests positifs et négatifs.** Vérifier l'attachement, les compteurs, les routes, le chemin réel, les services de retour et les protocoles d'infrastructure. Toute politique IPv6 doit être conçue explicitement et préserver les messages ICMPv6 essentiels.

## Références techniques

- Cisco, *ACLs Configuration Guide — Access Control Lists*, documentation IOS XE : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/security/acls/acls-configuration-guide/access-control-lists.html
- Cisco, *Object-group ACLs*, documentation IOS XE : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/security/acls/acls-configuration-guide/object-group-acl.html
- Cisco, *IPv6 Access Control Lists*, documentation IOS XE : https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/security-vpn/security-vpn/m_ip6-acls-xe.html
- IETF, RFC 2979, *Behavior of and Requirements for Internet Firewalls* : https://www.rfc-editor.org/rfc/rfc2979
- IETF, RFC 4890, *Recommendations for Filtering ICMPv6 Messages in Firewalls* : https://www.rfc-editor.org/rfc/rfc4890
