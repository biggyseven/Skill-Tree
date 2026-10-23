---
node_id: routing-expert
title: Routage statique & tables - Expert
---

# Routage statique & tables - Expert

**Niveau :** Expert

Le routage statique reste une fonction structurante des réseaux d’entreprise, même dans les architectures qui utilisent largement OSPF, IS-IS, EIGRP ou BGP. Une route statique exprime une décision explicite de transfert : pour atteindre un préfixe, le routeur doit utiliser un prochain saut, une interface de sortie, ou une combinaison des deux. Cette simplicité apparente masque plusieurs mécanismes distincts : validation de la route configurée, résolution récursive du prochain saut, sélection dans la table de routage, installation dans la base de transfert et traitement réel des paquets par le plan de données. La maîtrise de ces étapes est indispensable pour déployer des routes prévisibles, comprendre les pannes et éviter les boucles ou les trous noirs.

L’architecture IP moderne n’utilise plus le routage classful historique comme modèle de décision. Les préfixes CIDR représentent un réseau à l’aide d’une adresse et d’une longueur de préfixe, par exemple `10.40.16.0/20`. Les routeurs maintiennent généralement une base de routage, souvent appelée RIB (*Routing Information Base*), alimentée par les routes connectées, statiques et dynamiques. Une fonction de sélection choisit les routes admissibles pour la RIB, puis le système installe les informations nécessaires dans une base de transfert, souvent appelée FIB (*Forwarding Information Base*). Le chemin réellement emprunté par un paquet dépend du préfixe le plus spécifique installé qui correspond à sa destination, et pas simplement de la route qui semble la plus « prioritaire » dans la configuration.

Une route statique ne mesure pas spontanément la qualité du chemin ni la disponibilité de toute une destination. Elle peut rester configurée alors que le chemin situé au-delà du prochain saut est en panne. Certaines plateformes retirent une route lorsque son interface de sortie ou la résolution récursive devient invalide ; cela ne prouve pas que le service distant est joignable. Pour transformer une route statique en solution de basculement utile, il faut distinguer la disponibilité de l’interface, celle du prochain saut et celle d’un service ou d’une destination distante. Des mécanismes de suivi, tels qu’IP SLA et Object Tracking sur les plateformes Cisco qui les supportent, permettent de conditionner l’installation d’une route à un test ciblé.

Le routage statique est particulièrement pertinent pour les réseaux de bordure simples, les routes par défaut, les réseaux de gestion, les préfixes de rejet, les routes de secours, les VRF et les cas où une politique explicite doit primer sur l’apprentissage automatique. Il devient néanmoins risqué lorsqu’il est multiplié sans convention de nommage, sans documentation, sans contrôle des dépendances récursives et sans procédure de validation. Ce cours traite donc les routes statiques comme un mécanisme d’ingénierie complet : conception, décision, plan de contrôle, plan de données, convergence, sécurité et exploitation.

> **Analogie** : Considère un routeur comme un centre de tri qui doit envoyer chaque colis vers la prochaine plateforme logistique. La RIB est le registre des itinéraires possibles : elle décrit les destinations, les prochains relais et les conditions associées. La FIB est la version optimisée de ce registre utilisée par les équipements de transfert pour agir rapidement sur chaque colis. Une route statique ressemble à une instruction manuelle : « pour le secteur X, confie le colis au relais Y ». Cette instruction n’est exploitable que si le routeur sait réellement joindre Y. Si Y est accessible par un autre itinéraire, le centre de tri doit résoudre cette dépendance avant d’utiliser la route. C’est le routage récursif.
>
> Imagine maintenant que deux itinéraires soient enregistrés vers le même secteur. L’itinéraire principal a une préférence supérieure, tandis qu’un itinéraire de secours est prévu pour n’être utilisé que lorsque le principal disparaît de la table de routage. Il s’agit d’une route statique flottante. Mais si le premier relais répond encore alors que le pont situé plus loin est détruit, le centre de tri peut continuer à envoyer les colis dans la mauvaise direction. Pour éviter cela, le système doit vérifier un point situé au-delà du relais, ou recevoir une information de routage fiable qui retire le chemin devenu invalide.
>
> Enfin, si le registre annonce un grand secteur comme accessible alors qu’une partie de ce secteur n’a aucun itinéraire valide, les colis destinés aux adresses inconnues peuvent tourner en boucle ou être envoyés vers une destination incorrecte. Une route de rejet vers une interface nulle agit comme une zone de traitement des colis non reconnus : elle évite de réinjecter indéfiniment les paquets vers un autre centre qui annonce le même agrégat. Cette analogie rappelle que la justesse d’une route dépend autant de ses conditions et de ses dépendances que de la commande qui la crée.

---

## 1. La théorie et les algorithmes

### 1.1. Le chemin complet d’une route statique

Une route configurée ne passe pas directement de la ligne de commande au transfert matériel. Le système doit d’abord analyser la configuration, vérifier la forme de la destination et de son masque, déterminer le prochain saut ou l’interface de sortie, puis résoudre les dépendances nécessaires. Si la route est valide, elle peut devenir candidate à l’installation dans la RIB. Si une autre source annonce le même préfixe, le processus de sélection compare les sources selon les règles de l’implémentation, notamment la distance administrative et les métriques applicables. Une fois retenue, l’information est programmée dans la FIB ou les structures équivalentes propres à la plateforme.

Le modèle conceptuel est le suivant :

```text
                   Configuration ou apprentissage
                                |
                                v
                      +--------------------+
                      | Validation route   |
                      | préfixe / next-hop |
                      +---------+----------+
                                |
                                v
                      +--------------------+
                      | Résolution         |
                      | récursive éventuelle|
                      +---------+----------+
                                |
                                v
                      +--------------------+
                      | Routes candidates  |
                      +---------+----------+
                                |
                                v
                      +--------------------+
                      | Sélection RIB      |
                      | AD / métrique      |
                      +---------+----------+
                                |
                                v
                      +--------------------+
                      | Installation FIB   |
                      +---------+----------+
                                |
                                v
                      +--------------------+
                      | Transfert paquet   |
                      | LPM sur destination|
                      +--------------------+
```

Ce schéma sépare deux décisions souvent confondues. La sélection des routes dans la RIB détermine quelles informations seront disponibles pour le transfert ; la recherche de transfert dans la FIB cherche ensuite la route installée la plus spécifique correspondant à l’adresse de destination du paquet. Les détails d’implémentation peuvent varier, mais cette séparation permet de raisonner correctement sur la plupart des plateformes.

### 1.2. Les composants d’une table de routage

Une entrée de routage comprend habituellement une destination et une longueur de préfixe ou un masque, une source ou un protocole, une préférence, une métrique, un prochain saut, une interface de sortie et des attributs spécifiques à l’implémentation. La ligne exacte affichée par CLI peut agréger plusieurs routes candidates ou montrer des informations de résolution qui ne sont pas visibles dans une représentation simplifiée.

| Élément | Rôle opérationnel | Question de diagnostic |
|---|---|---|
| Préfixe de destination | Définit l’ensemble d’adresses couvertes | Le paquet correspond-il à ce préfixe ? |
| Longueur ou masque | Détermine la précision de la route | Existe-t-il une route plus spécifique ? |
| Source | Identifie route connectée, statique ou dynamique | Quelle fonction a fourni cette information ? |
| Distance administrative (AD) | Compare des sources concurrentes pour une destination équivalente sur les plateformes qui l’utilisent | Quelle source est préférée pour ce même préfixe ? |
| Métrique | Compare des chemins selon les règles propres au protocole ou à la fonction | Le chemin est-il préférable au sein de cette source ? |
| Prochain saut | Adresse du routeur suivant | Cette adresse est-elle résoluble et joignable ? |
| Interface de sortie | Interface par laquelle le paquet doit partir | L’interface est-elle active et adaptée au lien ? |
| État / suivi | Détermine si la route est admissible ou conditionnelle | Quelle condition la fait installer ou retirer ? |

Une table de routage n’est pas une simple liste ordonnée dans laquelle le premier élément gagne toujours. La précision du préfixe, la comparaison des sources, la métrique et les règles d’installation interviennent à des étapes distinctes. Lorsqu’un paquet est transféré, l’algorithme de recherche privilégie normalement la correspondance la plus longue parmi les routes installées correspondant à sa destination.

### 1.3. Longest Prefix Match : décision au plan de données

Le *Longest Prefix Match* (LPM) sélectionne la route installée dont le préfixe correspond à l’adresse de destination sur le plus grand nombre de bits. La route la plus précise l’emporte donc sur une route agrégée plus générale lorsqu’elles sont toutes les deux installées et correspondent à la destination.

Supposons les routes suivantes :

```text
0.0.0.0/0          -> 198.51.100.1
10.0.0.0/8         -> 10.1.0.1
10.40.0.0/16       -> 10.2.0.1
10.40.12.0/24      -> 10.3.0.1
```

Pour la destination `10.40.12.77`, trois préfixes spécifiques plus la route par défaut peuvent correspondre. Le choix de transfert est `10.40.12.0/24`, car `/24` est la correspondance la plus longue. Pour `10.40.80.9`, la route `/24` ne correspond pas ; `10.40.0.0/16` devient le préfixe le plus précis. Pour une destination publique non couverte par les réseaux internes, la route par défaut peut être utilisée.

LPM n’est pas la même chose que la distance administrative. La distance administrative est utilisée lors de la sélection d’une source de route vers un préfixe donné. LPM est utilisé lors de la sélection de l’entrée de transfert pour une adresse de destination parmi les préfixes installés. Par conséquent, une route statique `/24` peut être utilisée pour son sous-réseau même si une route dynamique `/16` a été retenue pour le préfixe plus large. Une AD plus basse ne rend pas une route moins spécifique capable de supplanter une route plus spécifique au plan de transfert.

> **Piège :** Ne dis pas « la route avec la plus faible distance administrative est toujours utilisée ». Cette règle est incomplète. La préférence administrative détermine généralement quelle source gagne pour un même préfixe lorsque plusieurs sources sont en compétition ; la recherche de transfert applique ensuite le préfixe le plus long. Il faut donc comparer les routes dans le bon ordre conceptuel et examiner la table réellement installée.

### 1.4. Distance administrative et métrique

Sur Cisco IOS/IOS XE, la distance administrative exprime le degré de confiance attribué à la source d’une route. Les valeurs par défaut courantes incluent : route connectée `0`, route statique `1`, EIGRP interne `90`, OSPF `110`, RIP `120` et EIGRP externe `170`. eBGP est couramment associé à `20` sur IOS. Ces valeurs peuvent varier selon les systèmes, versions et configurations, et ne sont pas des standards universels de l’IP.

La métrique est différente : elle exprime le coût défini par la source ou le protocole. OSPF peut utiliser un coût, EIGRP une métrique composite, BGP un ensemble d’attributs et une politique de sélection. Une route statique ne possède pas habituellement de métrique dynamique mesurant la qualité de la liaison ; son éventuelle valeur de préférence sur Cisco est souvent l’AD configurée à la fin de la commande.

Exemple IOS :

```cisco
! Route statique primaire vers le réseau distant
ip route 192.0.2.0 255.255.255.0 10.0.12.2

! Route concurrente de secours, préférée seulement si l'AD 1 disparaît
ip route 192.0.2.0 255.255.255.0 10.0.13.2 200
```

La deuxième route est généralement appelée route statique flottante. Sa distance administrative supérieure à celle de la route primaire la rend moins préférée pour le même préfixe. Elle ne devient utile que si la route plus préférée n’est plus admissible ou est retirée de la RIB. Si le prochain saut primaire reste résolu mais que le réseau situé derrière lui est injoignable, cette route flottante peut ne pas être activée automatiquement. Il faut alors un mécanisme de détection plus adapté.

### 1.5. Route directe, route avec prochain saut et route entièrement spécifiée

Une route statique peut référencer uniquement une adresse de prochain saut, uniquement une interface de sortie, ou les deux. Le choix a une conséquence sur la résolution et sur la façon dont l’équipement construit l’adjacence de couche 2.

**Route récursive par prochain saut :**

```cisco
ip route 192.0.2.0 255.255.255.0 10.0.12.2
```

Le routeur doit déterminer comment atteindre `10.0.12.2`. Si ce prochain saut est directement connecté, la résolution est simple. S’il est atteint par une autre route, cette route devient une dépendance récursive. La chaîne doit se terminer sur une interface ou une adjacency valide, et ne pas retomber sur la route qu’elle tente de résoudre.

**Route avec interface de sortie :**

```cisco
ip route 192.0.2.0 255.255.255.0 GigabitEthernet0/1
```

Sur une liaison point-à-point, cette forme peut être appropriée. Sur un segment Ethernet multiaccès, elle peut conduire le routeur à traiter les destinations du préfixe comme directement accessibles sur ce segment, avec une résolution ARP pour chaque destination finale. Cela peut être inefficace et causer des problèmes si le réseau n’est pas réellement directement joignable sur ce domaine L2.

**Route entièrement spécifiée :**

```cisco
ip route 192.0.2.0 255.255.255.0 GigabitEthernet0/1 10.0.12.2
```

Elle précise l’interface de sortie et le prochain saut. Elle peut rendre la résolution plus explicite, notamment lorsque la plateforme ou la topologie exige que l’interface soit fixée. La syntaxe et le comportement exacts dépendent du type d’interface et de l’OS réseau.

### 1.6. Résolution récursive du prochain saut

Prenons une route vers `172.20.40.0/24` via `10.20.0.2`. Si le routeur possède une route connectée `10.20.0.0/30` sur G0/0, il résout directement le prochain saut grâce à cette route connectée. Si l’adresse `10.20.0.2` était atteinte par un autre préfixe et une autre passerelle, le système devrait poursuivre la résolution jusqu’à obtenir une interface de sortie exploitable.

```text
Destination du paquet : 172.20.40.10
             |
             v
Route installée : 172.20.40.0/24 via 10.20.0.2
             |
             v
Résoudre 10.20.0.2 dans la table
             |
             v
Route connectée : 10.20.0.0/30 sur G0/0
             |
             v
Adjacence L2 vers 10.20.0.2 (ARP en IPv4)
             |
             v
Transmettre la trame sur G0/0
```

La récursion est utile : elle sépare la destination finale du prochain saut immédiat. Mais elle crée aussi une dépendance. Si la route qui permet de résoudre le prochain saut disparaît, la route statique dépendante peut être retirée. Une récursion circulaire est invalide : par exemple, une route vers un préfixe utilise un next-hop que seule cette même route permettrait de joindre. Les systèmes modernes détectent généralement l’auto-récursion et n’installent pas la route concernée, mais le diagnostic doit se faire sur la plateforme réelle.

Les routes récursives complexes augmentent les possibilités de mauvaise conception. Il est préférable de garder les chemins de résolution explicites, d’éviter les chaînes longues et de documenter l’interface ou la route qui fournit la joignabilité du prochain saut.

### 1.7. Route par défaut

La route par défaut IPv4 représente le préfixe `0.0.0.0/0`, qui correspond à toute destination ne disposant pas d’un préfixe plus spécifique dans la table de transfert. Sous Cisco IOS :

```cisco
ip route 0.0.0.0 0.0.0.0 198.51.100.1
```

Elle doit pointer vers un prochain saut joignable. Installer une route par défaut ne crée pas la connectivité Internet à elle seule : il faut une interface active, un chemin valide vers le FAI, des politiques de filtrage correctes et un chemin retour. La route par défaut est aussi une décision de politique ; dans un routeur multihomé, une route par défaut unique peut faire sortir tout le trafic par une seule connexion, même si d’autres liens existent.

Une route par défaut peut être reçue par un protocole dynamique ou configurée statiquement. La route qui est choisie parmi plusieurs possibilités dépend des règles de sélection, des paramètres de redistribution et de la politique du domaine. Une route par défaut statique vers un FAI ne doit pas être annoncée à d’autres domaines sans intention explicite.

IPv6 utilise une route par défaut `::/0`. Exemple IOS classique :

```cisco
ipv6 unicast-routing
ipv6 route ::/0 2001:db8:100::1
```

L’adresse `2001:db8::/32` est réservée à la documentation et ne doit pas être utilisée comme adressage Internet réel ; l’exemple est seulement illustratif. La syntaxe exacte varie selon le modèle de routeur et la version IOS/IOS XE.

### 1.8. Routes flottantes et basculement

La route flottante a une préférence administrative moins élevée, au sens de confiance, parce que sa valeur numérique d’AD est plus grande. Exemple : la route primaire a une AD de `1`, tandis que la route de secours a une AD de `200`. Pour un même préfixe, la route secondaire reste en dehors de la RIB tant qu’une route plus préférée et admissible existe, selon le comportement de la plateforme.

```text
                  Réseau distant 192.0.2.0/24
                         /           \
                        /             \
                 WAN primaire      WAN secours
                 R1 -> ISP-A        R1 -> ISP-B
                 AD 1               AD 200
                        \             /
                         \           /
                          +--- R1 ---+

   Tant que la route primaire reste installée, le secours flotte.
   Si elle est retirée de la RIB, le secours peut être sélectionné.
```

Une route flottante ne constitue pas, à elle seule, une détection de panne de bout en bout. Si l’interface WAN reste `up/up`, si le modem répond ou si le prochain saut est toujours résolu, une route statique peut rester présente malgré la perte du chemin au-delà. Une détection conditionnelle peut être construite avec IP SLA et Object Tracking, lorsque le matériel et le logiciel le permettent.

Un suivi bien conçu doit tester une destination représentative du service à protéger, pas seulement une adresse qui reste joignable alors que le chemin utile est cassé. Il faut aussi éviter les sondes dont le chemin de retour ou le routage en cas de basculement rend le résultat ambigu. Lorsque le lien secondaire prend le relais, une sonde mal définie peut parfois continuer à réussir en passant par le secours et conserver le primaire dans un état indésirable, ou à l’inverse provoquer des oscillations.

### 1.9. IP SLA et Object Tracking

Une configuration indicative pour Cisco IOS/IOS XE peut ressembler à ceci. Les commandes exactes et les fonctionnalités sont dépendantes de la plateforme ; elles doivent être validées dans le guide de configuration correspondant à la version logicielle.

```cisco
! Sonde ICMP vers une cible située au-delà du premier saut
ip sla 10
 icmp-echo 203.0.113.10 source-interface GigabitEthernet0/0
 frequency 5
exit
ip sla schedule 10 life forever start-time now

! Objet de suivi basé sur la réussite de la sonde
track 10 ip sla 10 reachability

! Route par défaut primaire conditionnée par le suivi
ip route 0.0.0.0 0.0.0.0 198.51.100.1 track 10

! Route par défaut secondaire, flottante
ip route 0.0.0.0 0.0.0.0 198.51.100.5 200
```

Dans cette illustration, `203.0.113.10` et les adresses de `198.51.100.0/24` appartiennent à des blocs de documentation RFC 5737. Ils servent à présenter la syntaxe et doivent être remplacés par des adresses réellement prévues dans l’architecture.

Le principe est le suivant : la sonde mesure un critère de reachability ; l’objet `track` traduit le résultat en état ; la route primaire dépend de cet état ; si la condition échoue et que la fonctionnalité est correctement configurée, la route suivie peut être retirée, permettant au secours flottant de devenir actif. Il faut vérifier les détails de traitement, les temporisations et la prise en charge exacte sur la plateforme utilisée.

Précautions de conception :

- choisir une cible disponible uniquement si le chemin souhaité l’est réellement ;
- fixer une source de sonde cohérente avec la topologie ;
- contrôler le routage retour des paquets de test ;
- choisir fréquence et temporisations sans provoquer de flapping ;
- tester le retour au primaire, pas uniquement la panne primaire ;
- vérifier les journaux et états de l’objet de suivi avant le déploiement.

### 1.10. Routes statiques à coût égal (ECMP)

Plusieurs routes vers un même préfixe peuvent être configurées avec une préférence équivalente et différents prochains sauts. Selon la plateforme et les conditions d’installation, elles peuvent contribuer à un partage de charge à coût égal, appelé ECMP (*Equal-Cost Multi-Path*). La répartition effective est généralement effectuée à partir d’un hachage de champs de flux plutôt qu’en alternant strictement chaque paquet entre les chemins. Cela permet souvent de préserver l’ordre des paquets d’un même flux, mais peut produire une distribution inégale si peu de flux sont actifs ou si leurs caractéristiques de hachage sont déséquilibrées.

Exemple indicatif :

```cisco
ip route 10.60.0.0 255.255.0.0 10.0.12.2
ip route 10.60.0.0 255.255.0.0 10.0.13.2
```

Ces lignes ne garantissent pas à elles seules un partage particulier sur tous les modèles. Le nombre de chemins installés, les règles de résolution et les fonctionnalités de transfert doivent être vérifiés avec les commandes du système. La redondance ECMP n’est utile que si les chemins ont une connectivité réellement distincte et des capacités compatibles.

ECMP ne signifie pas que chaque paquet d’un même flux sera envoyé sur un chemin différent. Le partage par flux est courant pour réduire le risque de réordonnancement, mais les algorithmes et champs utilisés dépendent du matériel et de la configuration. Lors du dépannage, il faut comparer les compteurs et les flux, pas uniquement constater que deux routes sont visibles dans le plan de contrôle.

### 1.11. Agrégation, route de rejet et trous noirs

L’agrégation résume plusieurs préfixes plus spécifiques en un préfixe plus large. Elle réduit le volume de routes dans les tables et peut stabiliser les changements du domaine agrégé. Mais elle est sûre uniquement lorsque l’agrégat représente une décision de routage cohérente et que les destinations couvertes par l’agrégat sont traitées correctement.

Un danger classique apparaît lorsqu’un routeur annonce ou installe `10.20.0.0/16` alors qu’il ne connaît que quelques sous-réseaux à l’intérieur de ce bloc. Un paquet vers un sous-réseau absent peut être envoyé vers un autre routeur qui possède le même agrégat, puis revenir en boucle. Une route de rejet vers Null0 ou une interface nulle est souvent utilisée pour absorber les destinations couvertes par l’agrégat mais qui ne disposent pas d’un itinéraire plus spécifique.

```cisco
! Exemple illustratif d'agrégat local et de route de rejet
ip route 10.20.0.0 255.255.0.0 Null0 250

! Les routes plus spécifiques réellement disponibles restent préférées
ip route 10.20.10.0 255.255.255.0 10.0.12.2
ip route 10.20.20.0 255.255.255.0 10.0.12.6
```

Le préfixe `/24` est plus spécifique que le `/16` Null0 et gagne pour ses destinations. Pour une adresse au sein du `/16` qui ne correspond à aucun `/24`, la route Null0 est utilisée et le paquet est détruit localement plutôt que d’être envoyé dans une boucle. La distance de l’agrégat doit être choisie selon l’objectif ; la valeur d’exemple `250` est volontairement peu préférée sur de nombreuses plateformes Cisco, mais doit être vérifiée dans le contexte d’exploitation. Elle ne doit pas être copiée sans analyse.

Une route de rejet agrégée ne doit pas remplacer une politique de routage correctement conçue. Il faut confirmer que le routeur possède les routes spécifiques attendues, que l’agrégat ne couvre pas des plages appartenant à d’autres domaines et que l’éventuelle annonce de l’agrégat est conditionnée à l’existence des routes nécessaires. Le RFC 4632 décrit notamment l’usage du longest-match et la nécessité d’un next-hop nul pour les destinations incluses dans un agrégat sans route plus spécifique.

### 1.12. RIB, FIB, adjacency et plan de données

La RIB contient les décisions du plan de contrôle. La FIB est optimisée pour le transfert et peut être programmée dans un ASIC, un processeur réseau ou une structure logicielle. Pour transmettre une trame IPv4 sur Ethernet, le routeur doit non seulement savoir quelle route utiliser, mais aussi déterminer l’interface et l’adresse de couche 2 du prochain saut. La résolution ARP fournit souvent cette association IPv4-MAC sur un segment Ethernet.

Une route peut être visible dans la RIB tandis que le transfert rencontre un problème d’adjacence, de résolution ARP, d’ACL, de MTU ou de programmation matérielle. Inversement, un chemin peut être disponible dans la configuration mais ne pas être installé car son prochain saut n’est pas résolu. Le diagnostic doit donc distinguer la validité de la route, son installation, son adjacency L2 et les politiques appliquées au paquet.

Les commandes Cisco usuelles incluent :

```cisco
show ip route
show ip route 10.20.10.10
show ip cef 10.20.10.10 detail
show adjacency detail
show arp
show ip interface brief
```

Toutes les commandes ne sont pas prises en charge sous la même forme sur chaque plateforme. `show ip cef` et les commandes d’adjacency sont particulièrement utiles lorsqu’elles existent, car elles permettent de comparer la route visible et la façon dont le transfert a été construit.

### 1.13. Route statique, route connectée et route dynamique

Une route connectée apparaît généralement lorsqu’une interface routée est configurée avec une adresse IP et qu’elle est opérationnelle. Le routeur sait alors que le préfixe est directement accessible sur cette interface. Les routes statiques sont créées par la configuration ; les routes dynamiques proviennent d’un protocole et de ses règles de sélection.

Un préfixe peut être présent dans plusieurs sources. Par exemple, une route statique et une route OSPF peuvent annoncer le même `/24`. L’AD permet habituellement de choisir la source installée pour ce préfixe sur IOS/IOS XE. Mais si la route OSPF est un `/16` et la route statique un `/24`, le `/24` plus spécifique peut servir au trafic qui correspond à ce bloc, indépendamment du fait que la source OSPF ait une préférence administrative par défaut meilleure que certaines autres sources.

Il est important de ne pas déployer une route statique concurrente d’un protocole dynamique sans documenter le comportement désiré. Une route statique à AD `1` peut supplanter une route dynamique vers le même préfixe et empêcher le protocole de choisir un chemin différent. Une route flottante correctement configurée peut au contraire être utile comme secours si la route dynamique devient indisponible.

### 1.14. VRF et routes statiques isolées

Une VRF (*Virtual Routing and Forwarding*) maintient un contexte de routage séparé sur un même équipement. Les routes et les interfaces associées à une VRF ne sont pas automatiquement visibles dans la table globale ni dans les autres VRF. Une route statique doit être créée dans le bon contexte, et la résolution du prochain saut doit s’effectuer dans le contexte prévu.

Exemple indicatif Cisco IOS/IOS XE :

```cisco
vrf definition CLIENT-A
 address-family ipv4
 exit-address-family
!
interface GigabitEthernet0/2
 description Acces_CLIENT_A
 vrf forwarding CLIENT-A
 ip address 10.10.10.1 255.255.255.0
 no shutdown
!
ip route vrf CLIENT-A 192.0.2.0 255.255.255.0 10.10.10.2
```

L’ordre de configuration de `vrf forwarding` et de l’adresse IP peut être significatif, car l’affectation à une VRF peut supprimer une adresse préexistante sur certaines plateformes. Il faut vérifier la syntaxe et les contraintes dans la documentation de l’OS utilisé. Le prochain saut `10.10.10.2` doit être joignable dans la VRF `CLIENT-A`, pas simplement dans la table globale.

Les VRF sont particulièrement utiles lorsque des clients ou des entités utilisent des plages RFC 1918 qui se chevauchent. Une route statique mal placée dans la table globale peut exposer du trafic vers un mauvais domaine ou provoquer un mélange de connectivité entre clients. Le diagnostic doit toujours commencer par identifier le contexte de routage concerné.

### 1.15. Routage par politique (PBR) et routes statiques : distinction

La route statique classique répond à une question liée à la destination : « pour cette adresse de destination, quel chemin doit être utilisé ? ». Le routage par politique, ou PBR (*Policy-Based Routing*), peut appliquer une décision à partir d’autres critères, comme l’adresse source, une ACL ou une route-map, selon les capacités de la plateforme. PBR est donc un mécanisme distinct de la simple table de routage.

Un routeur peut avoir une route statique correcte vers une destination et envoyer malgré tout certains paquets sur un autre chemin si une politique de routage s’applique avant la décision habituelle, ou si une autre fonction modifie le traitement. Lors du dépannage, il faut examiner les fonctionnalités de PBR, les ACL, les VRF, le routage basé sur des applications ou d’autres politiques spécifiques à la plateforme.

La PBR peut être utile pour un besoin explicite de sélection de chemin, mais elle accroît la complexité. Elle doit être documentée, limitée au trafic attendu et accompagnée d’un mécanisme de vérification. Utiliser PBR pour corriger un plan d’adressage défectueux masque souvent la cause au lieu de la résoudre.

### 1.16. IPv6 : routes statiques et next-hop link-local

IPv6 conserve les grands principes du routage par préfixe, mais son adressage et la résolution de voisinage diffèrent d’IPv4. Une route IPv6 doit préciser le préfixe et un prochain saut ou une interface selon la syntaxe de la plateforme. Les adresses link-local `fe80::/10` ne sont valides que sur un lien ; lorsqu’un prochain saut link-local est utilisé, l’interface de sortie doit généralement être indiquée afin de lever l’ambiguïté.

Exemple conceptuel IOS :

```cisco
ipv6 unicast-routing
ipv6 route 2001:db8:200:10::/64 GigabitEthernet0/1 fe80::2
ipv6 route ::/0 2001:db8:100::1
```

Ces préfixes et adresses de documentation sont illustratifs. La première route fixe une interface et un next-hop link-local. La seconde représente une route par défaut IPv6 vers un prochain saut global qui doit être joignable selon la topologie. La syntaxe exacte est à vérifier sur la version IOS/IOS XE ciblée.

Pour examiner la table IPv6 :

```cisco
show ipv6 route
show ipv6 route static
show ipv6 neighbors
```

La présence d’une route ne suffit pas à garantir que Neighbor Discovery a résolu l’adresse de liaison du prochain saut. Il faut distinguer la sélection du préfixe de routage du fonctionnement de la couche 2 et de la résolution de voisinage IPv6.

### 1.17. Routage asymétrique et chemins retour

Le routage asymétrique signifie que le chemin emprunté par les paquets aller diffère de celui du retour. Ce comportement n’est pas intrinsèquement incorrect dans IP, mais il peut poser problème lorsque des pare-feu à états, des systèmes NAT, des appliances d’inspection ou des règles de filtrage supposent que les deux directions traversent le même équipement.

Une route statique peut envoyer le trafic aller par WAN-A, alors que le réseau distant renvoie les réponses par WAN-B. Sans contrôle de cohérence, le pare-feu de WAN-A peut voir une session incomplète ou le NAT peut ne pas retrouver la traduction attendue. Dans les architectures multi-liens, il faut vérifier non seulement le prochain saut local, mais aussi les annonces du réseau distant, les règles de NAT, la symétrie souhaitée et les états conservés par les équipements de sécurité.

Le traceroute dans un seul sens ne montre pas toujours le chemin de retour. Il faut croiser les tables des routeurs, les journaux de pare-feu, les captures des deux côtés et les données de suivi du lien. Le routage asymétrique peut également expliquer pourquoi une sonde IP SLA réussit ou échoue d’une façon qui semble contradictoire avec la disponibilité du lien.

### 1.18. Route permanente, disponibilité et mauvaises hypothèses

Certaines versions Cisco IOS proposent l’option `permanent` pour maintenir une route statique dans la table même lorsque l’interface concernée est inactive, selon les conditions décrites par la plateforme. Cette fonction ne prouve pas que le chemin existe. Elle peut être utile dans un cas spécifique de conception, mais elle peut aussi maintenir un trou noir actif si elle est employée pour contourner les mécanismes normaux de validité.

Une route « présente dans la table » n’est pas l’équivalent d’une route « fonctionnelle ». Pour raisonner sur la disponibilité, il faut établir le critère requis : interface active, prochain saut résolu, sonde vers une destination, session applicative réussie, ou autre signal fiable. Le mécanisme choisi doit correspondre au service à protéger et à son modèle de panne.

### 1.19. Mesure de convergence et stabilité

Le temps de basculement dépend de la détection de panne, du délai de retrait de la route primaire, de l’installation de la route de secours, de la programmation FIB, de la résolution de couche 2 et de la récupération du chemin retour. Une détection basée uniquement sur le lien peut être très rapide pour une coupure physique, mais ne détectera pas nécessairement une défaillance en amont. Une sonde IP SLA peut identifier une panne plus éloignée, mais sa fréquence et ses délais de timeout déterminent une partie du temps de réaction.

Il faut également éviter les oscillations. Une sonde instable peut retirer puis réinstaller la route de manière répétée, perturber des sessions et faire varier les chemins. Des délais d’hystérésis, des temporisations cohérentes ou un seuil de résultats manqués peuvent être disponibles selon la fonction. Le système doit être testé non seulement lors d’une panne nette, mais aussi lors d’une perte intermittente, d’une latence élevée et d’un retour partiel du service.

### 1.20. Tableau des erreurs d’ingénierie les plus fréquentes

| Erreur | Conséquence possible | Contrôle recommandé |
|---|---|---|
| Route statique vers un next-hop non résolu | Route non installée ou retrait inattendu | Examiner la résolution récursive et l’interface de sortie |
| Route flottante sans suivi de bout en bout | Pas de basculement malgré la panne amont | Tester un mécanisme de tracking ciblé |
| Agrégat sans route de rejet appropriée | Boucles pour les adresses couvertes mais absentes | Route Null0 et vérification des préfixes plus spécifiques |
| Route par défaut annoncée sans intention | Sortie du trafic par un domaine non prévu | Contrôler la redistribution et les filtres |
| Route Ethernet avec interface seulement | ARP des destinations finales ou adjacence incorrecte | Préférer souvent un next-hop IP ou une route spécifiée |
| Route statique globale pour un client VRF | Fuite ou perte de connectivité inter-domaines | Vérifier le contexte de routage |
| ECMP supposé sans vérification | Répartition inégale ou chemin non utilisé | Examiner FIB, hash et compteurs d’interface |
| PBR oubliée dans le dépannage | Trafic ne suit pas la route attendue | Inspecter route-maps et politiques d’interface |
| Permanence utilisée comme mécanisme de disponibilité | Route conservée vers une destination inaccessible | Lier l’installation à un signal de disponibilité pertinent |

### 1.21. Principes de conception pour un plan de routage statique

Un plan statique fiable doit être minimal, déterministe et révisable. Chaque route doit avoir une raison, un propriétaire, un préfixe précis, un prochain saut documenté, une méthode de vérification et, lorsqu’il est nécessaire, une procédure de retrait. Les routes par défaut doivent être placées là où l’architecture justifie la sortie de trafic, pas ajoutées mécaniquement à chaque routeur.

Les conventions peuvent inclure : noms de routes explicites lorsque la plateforme les prend en charge, commentaire de configuration, tableau d’adressage à jour, identification des routes principales et de secours, et sauvegarde de l’état avant changement. Les changements devraient être testés dans une fenêtre maîtrisée, avec critères de succès et plan de retour arrière clairement définis.

Pour les routes de secours, il faut documenter ce qui déclenche le basculement. Une AD supérieure est une préférence, pas un test de connectivité. Pour les agrégats, il faut documenter les préfixes inclus et le comportement attendu en cas de destination absente. Pour les VRF, il faut préciser le contexte de routage associé. Pour les routes IPv6, il faut prendre en compte les link-local et la résolution NDP.

---

## 2. Configuration et Pratique

### 2.1. Laboratoire de référence

Le laboratoire utilise trois routeurs Cisco IOS/IOS XE. R1 relie un LAN d’entreprise, R2 joue le rôle de transit, et R3 relie un réseau applicatif. L’objectif est de déployer des routes statiques, une route par défaut, une route de secours et un chemin vers le réseau distant.

| Routeur | Interface | Adresse illustrative | Rôle |
|---|---|---|---|
| R1 | G0/0 | 10.10.10.1/24 | LAN utilisateurs |
| R1 | G0/1 | 10.0.12.1/30 | Transit vers R2 |
| R2 | G0/0 | 10.0.12.2/30 | Transit vers R1 |
| R2 | G0/1 | 10.0.23.2/30 | Transit vers R3 |
| R3 | G0/0 | 10.0.23.3/30 | Transit vers R2 |
| R3 | G0/1 | 192.0.2.1/24 | LAN applicatif de documentation |

Les adresses du bloc `192.0.2.0/24` sont réservées à la documentation et ne doivent pas être utilisées comme adresse de production sur Internet. Dans un laboratoire privé, remplace-les par des préfixes adaptés à l’environnement. Les noms d’interfaces doivent être ajustés à la plateforme.

```text
       LAN utilisateurs                         LAN applicatif
        10.10.10.0/24                            192.0.2.0/24
              |                                        |
         G0/0 |                                        | G0/1
         +---------+    10.0.12.0/30     +---------+    |
         |   R1    |---------------------|   R2    |----| 
         +---------+                     +---------+    |
              |                            10.0.23.0/30 |
              | route par défaut et secours             |
              +------------------------------------+    |
                                                   |    |
                                              +---------+
                                              |   R3    |
                                              +---------+

        R1 atteint le LAN de R3 via R2 ; les routes de retour
        doivent être présentes sur R2 et R3 également.
```

### 2.2. Configurer R1

```cisco
hostname R1
!
interface GigabitEthernet0/0
 description LAN_UTILISATEURS
 ip address 10.10.10.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 description TRANSIT_VERS_R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
! Route vers le LAN applicatif derrière R3
ip route 192.0.2.0 255.255.255.0 10.0.12.2
!
! Route par défaut vers le chemin primaire (exemple pédagogique)
ip route 0.0.0.0 0.0.0.0 10.0.12.2
```

La route vers `192.0.2.0/24` est plus spécifique que la route par défaut. Les paquets vers ce préfixe utiliseront donc la route dédiée ; les autres destinations IPv4 non couvertes par un préfixe plus spécifique pourront utiliser la route par défaut. La route par défaut de ce laboratoire est volontairement simple et n’implique pas une connectivité Internet réelle.

### 2.3. Configurer R2

```cisco
hostname R2
!
interface GigabitEthernet0/0
 description TRANSIT_VERS_R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description TRANSIT_VERS_R3
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
! R2 connaît le LAN de R1 et le LAN de R3
ip route 10.10.10.0 255.255.255.0 10.0.12.1
ip route 192.0.2.0 255.255.255.0 10.0.23.3
```

R2 dispose déjà de routes connectées vers les deux réseaux de transit. Les deux routes statiques lui permettent d’atteindre les LAN situés derrière R1 et R3. Dans un réseau réel, l’administrateur pourrait choisir un protocole dynamique pour ces routes, mais le laboratoire vise à isoler le comportement des routes statiques.

### 2.4. Configurer R3

```cisco
hostname R3
!
interface GigabitEthernet0/0
 description TRANSIT_VERS_R2
 ip address 10.0.23.3 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description LAN_APPLICATIF
 ip address 192.0.2.1 255.255.255.0
 no shutdown
!
! Chemin de retour vers le LAN de R1
ip route 10.10.10.0 255.255.255.0 10.0.23.2
!
! Route par défaut de retour vers R2 pour les destinations inconnues
ip route 0.0.0.0 0.0.0.0 10.0.23.2
```

Le chemin de retour est indispensable. R1 peut avoir une route correcte vers `192.0.2.0/24`, mais le trafic échouera si R3 ne sait pas joindre `10.10.10.0/24`. La route par défaut sur R3 est illustrative et doit être utilisée seulement si R2 constitue effectivement la passerelle de retour prévue pour les autres destinations.

### 2.5. Vérifier les interfaces et routes

Commence par vérifier l’état opérationnel :

```cisco
show ip interface brief
show interfaces GigabitEthernet0/1
```

Confirme ensuite les routes :

```cisco
show ip route
show ip route 192.0.2.10
show ip route static
```

Puis teste les prochains sauts et la destination :

```cisco
ping 10.0.12.2
ping 10.0.23.3
ping 192.0.2.1
traceroute 192.0.2.1
```

La syntaxe des commandes de ping et de traceroute peut varier selon la version. Les tests doivent être effectués dans les deux sens lorsqu’on valide un chemin aller-retour. Il faut distinguer un échec ICMP isolé d’une panne générale de transport, car certains équipements filtrent ou limitent les réponses ICMP.

### 2.6. Ajouter une route flottante

Dans une architecture redondante, le même préfixe peut disposer d’un chemin primaire et d’un chemin secondaire. Le secondaire doit être moins préféré, mais rester valide quand il est nécessaire.

```cisco
! Route primaire via le prochain saut principal
ip route 192.0.2.0 255.255.255.0 10.0.12.2 1

! Route secondaire via une autre liaison, si elle existe réellement
ip route 192.0.2.0 255.255.255.0 10.0.13.2 200
```

Ce code est un exemple de syntaxe, pas une configuration autonome : `10.0.13.2` doit être joignable sur une interface et une liaison de secours réellement configurées. Dans le laboratoire de référence, aucune liaison `10.0.13.0/30` n’a été définie ; il faut donc l’ajouter avant de tester la route secondaire.

Après configuration, provoque une panne contrôlée de la route principale, puis examine la RIB et le chemin effectif. Ne te contente pas de vérifier la présence de deux lignes `ip route` dans la configuration : une route configurée peut ne pas être installée si son prochain saut est invalide.

### 2.7. Exemple de route de rejet Null0

```cisco
! Route d'agrégat volontairement peu préférée pour éviter une boucle
ip route 10.20.0.0 255.255.0.0 Null0 250
!
! Routes plus spécifiques vers des réseaux réellement joignables
ip route 10.20.10.0 255.255.255.0 10.0.12.2
ip route 10.20.20.0 255.255.255.0 10.0.13.2
```

La route Null0 est utile si le routeur représente ou annonce un agrégat. Les routes `/24` plus spécifiques gagnent pour les sous-réseaux réellement connus. Toute destination du `/16` sans route plus spécifique est rejetée localement, ce qui évite une boucle. Cette technique doit être évaluée en fonction des annonces produites et des routes réellement contenues dans l’agrégat.

### 2.8. Exemple de suivi IP SLA

```cisco
ip sla 20
 icmp-echo 203.0.113.20 source-interface GigabitEthernet0/1
 frequency 5
exit
ip sla schedule 20 life forever start-time now
track 20 ip sla 20 reachability
!
! La route principale n'est installée que si l'objet suivi est valide
ip route 0.0.0.0 0.0.0.0 198.51.100.1 track 20
!
! Secours flottant
ip route 0.0.0.0 0.0.0.0 198.51.100.5 200
```

Remplace les adresses de documentation par des destinations et prochains sauts valides dans ton réseau. La sonde doit traverser la liaison qu’elle cherche à surveiller ; sinon, elle pourrait réussir par le chemin secondaire et ne plus représenter l’état du primaire. Selon la plateforme, des commandes supplémentaires peuvent être nécessaires pour définir les timeouts, les seuils ou le type de suivi.

### 2.9. Routes IPv6 de base

```cisco
ipv6 unicast-routing
!
interface GigabitEthernet0/1
 ipv6 address 2001:db8:12::1/64
 no shutdown
!
ipv6 route 2001:db8:40::/64 2001:db8:12::2
ipv6 route ::/0 2001:db8:12::2
```

Les préfixes `2001:db8::/32` sont réservés à la documentation. Le routeur doit être configuré avec une véritable topologie IPv6 avant que ces routes soient testées. Vérifie la route et le voisin :

```cisco
show ipv6 route
show ipv6 route static
show ipv6 neighbors
ping ipv6 2001:db8:12::2
```

Pour un next-hop link-local `fe80::/10`, l’interface de sortie est normalement requise afin d’identifier le lien concerné. Les commandes et formats exacts doivent être adaptés à l’OS utilisé.

### 2.10. Sauvegarde, changement et retour arrière

Avant un changement de routage, capture l’état de référence :

```cisco
show running-config | include ^ip route|^ipv6 route
show ip route
show ip route static
show ip interface brief
show logging
```

Sauvegarde ensuite la configuration selon la politique de l’organisation. Ajoute les routes une par une, vérifie l’installation, teste les destinations de contrôle et inspecte le chemin retour. Ne supprime la route existante qu’après validation du nouveau chemin, sauf si le scénario exige explicitement de tester une panne contrôlée.

Un plan de retour arrière doit préciser la commande de suppression exacte, les anciens prochains sauts, les critères de retour à l’état antérieur et les commandes de validation. Les modifications d’AD, de routes par défaut, de résumé et de routes de rejet peuvent avoir un impact très large ; elles doivent être réalisées avec une fenêtre et un périmètre clairement définis.

---

## 3. Dépannage et Sécurité

### 3.1. Route configurée mais absente de la table

Une route peut être présente dans la configuration sans être installée dans la RIB. Les causes comprennent un prochain saut non résolu, une interface inactive, une VRF incorrecte, une route concurrente préférée pour le même préfixe, une route récursive circulaire ou une limitation particulière de la plateforme.

Procédure :

1. Vérifie la syntaxe et le préfixe de la commande de route.
2. Confirme que le prochain saut peut être résolu par une route valide.
3. Vérifie l’état de l’interface de sortie et la connectivité L2.
4. Examine la RIB pour le préfixe et pour l’adresse du prochain saut.
5. Vérifie le contexte VRF et la famille d’adresses.
6. Recherche une route concurrente, une politique ou un mécanisme de suivi qui retirerait l’entrée.

Commandes usuelles :

```cisco
show running-config | include ^ip route
show ip route 10.20.10.0
show ip route 10.0.12.2
show ip interface brief
show arp
```

Les résultats sont dépendants de la plateforme. Pour un diagnostic de récursion complexe, compare l’entrée candidate, le chemin permettant de résoudre le next-hop et toute route qui pourrait retomber sur la route elle-même.

### 3.2. Route présente, mais trafic perdu

Une route présente dans la RIB n’assure pas que les paquets soient livrés. Il faut vérifier la FIB, l’adjacence, ARP/NDP, les ACL, les pare-feu, le MTU et le chemin retour. Le premier diagnostic consiste à effectuer des tests du plus proche au plus éloigné : interface, prochain saut, routeur intermédiaire, destination finale.

```cisco
show ip route 192.0.2.10
show ip cef 192.0.2.10 detail
show arp
show interfaces counters errors
ping 10.0.12.2
traceroute 192.0.2.10
```

Si le ping du prochain saut échoue, le problème est probablement plus proche du lien local ou de l’adresse de prochain saut. Si le prochain saut répond mais que la destination échoue, inspecte le routage au-delà du prochain saut, les ACL et le chemin retour. Un traceroute ne garantit pas toujours d’identifier le point exact de panne, car les réponses ICMP intermédiaires peuvent être filtrées.

### 3.3. La route de secours ne s’active pas

Une route flottante n’entre pas en service simplement parce que l’application distante est indisponible. Si la route primaire reste admissible dans la RIB, elle peut continuer à être utilisée.

Vérifie :

- si l’interface primaire est encore `up/up` ;
- si le prochain saut est toujours résolu ;
- si la route primaire est directement connectée, statique ou dynamique ;
- si un objet de suivi est configuré et passe réellement à l’état down ;
- si la route secondaire est elle-même admissible ;
- si le test de disponibilité suit le chemin attendu et ne réussit pas via le secours.

La correction consiste souvent à choisir une détection de panne adaptée, à revoir le next-hop ou à corriger les dépendances de résolution, plutôt qu’à augmenter arbitrairement l’AD. Une route secondaire ne peut pas remplacer un mécanisme de surveillance absent.

### 3.4. Boucle ou trou noir provoqué par un agrégat

Un agrégat incorrect peut provoquer un trafic envoyé vers un routeur qui renvoie les paquets vers l’émetteur. Le TTL finit par expirer, ce qui gaspille les ressources du réseau. Une destination non couverte par une route spécifique peut aussi être envoyée vers le mauvais chemin en raison d’une route générale trop large.

Pour diagnostiquer :

1. affiche toutes les routes correspondant au préfixe ;
2. identifie la route la plus spécifique pour l’adresse testée ;
3. vérifie s’il existe une route de rejet pour l’agrégat ;
4. examine le chemin sur les routeurs voisins ;
5. retire ou corrige l’agrégat seulement selon un plan contrôlé.

Le principe du longest-prefix match signifie qu’une route spécifique vers un sous-réseau connu prévaut sur l’agrégat. L’agrégat doit néanmoins être conçu pour ne pas renvoyer indéfiniment les paquets destinés à des adresses couvertes mais absentes.

### 3.5. Problème de chemin retour et routage asymétrique

Si le paquet arrive à destination, mais que le terminal ne répond pas, il est possible que le routeur ou l’hôte distant ne dispose pas d’une route retour. Dans un réseau multi-WAN, le retour peut utiliser un autre fournisseur. Le NAT, le pare-feu à états ou une ACL peuvent alors interrompre la session.

La démarche doit couvrir les deux directions : tracer le chemin aller, vérifier la table de routage à destination, contrôler la passerelle de l’hôte distant et tester le retour vers le préfixe source. Dans un environnement NAT, vérifie aussi la table de translations, car le chemin retour doit correspondre à l’état de translation créé lors du trafic aller.

### 3.6. Problèmes liés aux VRF

Lorsqu’une route existe dans la table globale, cela ne signifie pas qu’elle existe dans une VRF. Les commandes doivent être exécutées dans le contexte approprié. Il faut également vérifier si le prochain saut est résolu dans la même VRF et si la route est destinée à être importée ou exportée entre contextes.

Les erreurs classiques comprennent une route statique configurée avec `ip route` au lieu de `ip route vrf`, une interface affectée au mauvais contexte ou un prochain saut présent dans la table globale uniquement. Ces erreurs peuvent entraîner une absence de route ou une fuite de trafic si des mécanismes d’importation/exportation ont été configurés incorrectement.

### 3.7. Débogage sans provoquer une panne secondaire

Les commandes de debug peuvent produire un volume important de messages et consommer les ressources du routeur. En production, commence par les commandes d’état et les journaux ; n’utilise les traces ciblées qu’avec un périmètre et une durée définis. Après le test, arrête les débogages et confirme qu’aucune capture ou session de diagnostic ne demeure active sans besoin.

La configuration et les sorties de commande peuvent contenir des adresses internes, noms d’équipement ou éléments sensibles. Collecte et partage ces informations selon les règles de sécurité de l’organisation. Une capture de paquets peut révéler des informations de trafic, même si elle ne contient pas de mots de passe en clair.

### 3.8. Menaces et protection du plan de routage

Le routage statique réduit l’exposition à certaines formes d’annonces dynamiques non autorisées, mais ne supprime pas le risque d’erreur de configuration ni les menaces au plan de données. Un attaquant qui obtient des privilèges de configuration peut modifier une route par défaut, ajouter un next-hop malveillant ou créer une route plus spécifique pour détourner le trafic. Une règle de routage inattendue peut aussi créer une fuite entre VRF ou domaines de sécurité.

Les contrôles de sécurité doivent inclure :

- l’authentification forte et la limitation des accès administratifs ;
- l’usage de SSH et de protocoles de gestion sécurisés ;
- le contrôle des changements de configuration et la journalisation ;
- la segmentation des réseaux de gestion ;
- le filtrage des flux et la validation des routes de sortie ;
- la protection des sauvegardes et l’accès contrôlé aux fichiers de configuration ;
- la revue des routes par défaut, des agrégats, des routes Null0 et des routes statiques de secours.

Les listes de contrôle d’accès et les pare-feu restent nécessaires pour limiter les communications. Une route qui permet l’acheminement d’un paquet ne doit pas être interprétée comme une autorisation de sécurité.

### 3.9. Validation des changements de routage

Avant de déployer une modification, définis des critères de succès mesurables. Par exemple : le préfixe attendu apparaît dans la RIB et dans la FIB ; le prochain saut est correct ; des tests de connectivité réussissent dans les deux sens ; aucune route inattendue n’est ajoutée ; le trafic utilise bien le lien voulu ; les compteurs et les journaux ne révèlent pas d’instabilité.

Un test de basculement doit inclure la panne réelle du chemin surveillé, l’activation du secours, le maintien des applications critiques, le retour du chemin primaire et l’absence d’oscillations. Une route de secours non testée est une hypothèse, pas une garantie de disponibilité.

### 3.10. Checklist d’exploitation

- Vérifier les interfaces et l’adressage des prochains sauts.
- Contrôler la RIB, la FIB et la résolution ARP/NDP.
- Vérifier le préfixe le plus spécifique pour chaque destination critique.
- Distinguer AD, métrique et LPM.
- Documenter routes principales, routes flottantes, agrégats et Null0.
- Tester la détection et le basculement au-delà du lien physique.
- Vérifier les chemins aller et retour, y compris dans les VRF et avec NAT.
- Sauvegarder la configuration, définir une fenêtre de changement et préparer le rollback.
- Contrôler la configuration après changement et surveiller les journaux.

> **Astuce :** Pour une destination problématique, procède dans cet ordre : `show ip route <destination>`, puis vérifie la résolution du prochain saut avec `show ip route <next-hop>`, examine ARP avec `show ip arp` ou `show arp`, puis compare la FIB avec `show ip cef <destination> detail` lorsque la plateforme le permet. Cette séquence sépare rapidement un problème de sélection de route d’un problème d’adjacence L2 ou de transfert. Pour un secours, vérifie en plus l’état exact de l’objet de suivi et teste le scénario de panne contrôlée.

> **Danger :** Une route statique apparemment valide peut continuer à envoyer tout le trafic vers un chemin dont le service distant est hors ligne. Une route par défaut incorrecte peut détourner des flux entiers ; une route plus spécifique indésirable peut détourner un seul sous-réseau ; un agrégat sans route de rejet peut créer des boucles. Toute modification de routage doit être considérée comme un changement de plan de contrôle à impact potentiellement large. Valide la RIB, la FIB, les chemins aller/retour et le mécanisme de détection avant de déclarer le service protégé.

## Points à retenir

- **La sélection de route et le transfert sont deux étapes distinctes.** La RIB choisit les routes admissibles à partir de la source, de l’AD et des règles applicables ; la FIB utilise le préfixe le plus long pour chaque destination. AD, métrique et LPM ne sont pas interchangeables.
- **Une route statique dépend de la résolution et de la disponibilité du chemin.** Le prochain saut doit être résolu, et une route flottante ne détecte pas nécessairement une panne située au-delà d’une interface ou d’un routeur encore joignable. IP SLA/Object Tracking peut aider si la sonde représente correctement le service attendu.
- **Agrégation, VRF, ECMP et routage asymétrique doivent être conçus, pas supposés.** Les routes de rejet empêchent certaines boucles d’agrégation ; les VRF imposent un contexte de routage distinct ; ECMP dépend de l’installation et du hachage ; les chemins retour doivent être validés.
- **La sécurité du routage exige de contrôler la configuration et les changements.** Protéger l’accès administratif, documenter les routes, filtrer les flux, tester le basculement et conserver un plan de rollback sont indispensables pour exploiter des routes statiques de manière fiable.

## Références techniques

- IETF, [RFC 1812 — Requirements for IP Version 4 Routers](https://www.rfc-editor.org/rfc/rfc1812.html) : traitement du routage IPv4, recherche de préfixe et comportement des routeurs.
- IETF, [RFC 4632 — Classless Inter-domain Routing (CIDR)](https://www.rfc-editor.org/rfc/rfc4632.html) : préfixes CIDR, longest-match, agrégation et protection contre certaines boucles dues aux agrégats.
- Cisco, [IP Routing Configuration Guide, Cisco IOS XE 17.x](https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing.html) : configuration et comportement des routes statiques sur IOS XE.
- Cisco, [Recursive Static Route — Cisco IOS XE](https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m_iri-recursive-static-route-xe.html) : résolution récursive et prise en charge selon la plateforme.
- Cisco, [Static Route — modèles IOS XE](https://netascode.cisco.com/docs/data_models/iosxe/device/static_route/) : exemples de routes statiques, distances administratives, ECMP et suivi conditionnel.

Les commandes et exemples sont fournis comme modèles pédagogiques. Vérifie toujours la syntaxe, les options et la prise en charge dans la documentation correspondant au modèle du routeur et à sa version IOS/IOS XE avant un déploiement en production.
