# ACL & filtrage - Débutant

**Niveau :** Débutant

Les listes de contrôle d’accès, ou ACL (*Access Control Lists*), sont des mécanismes de filtrage utilisés par les équipements réseau pour décider quels paquets sont autorisés à traverser une interface ou à accéder à une fonction de gestion. Une ACL décrit une suite de conditions et une action associée à chaque condition : autoriser (`permit`) ou refuser (`deny`). Sur les routeurs et commutateurs de couche 3, les ACL IPv4 peuvent notamment comparer les adresses IP source et destination, le protocole de couche 3 et, lorsqu’il s’agit d’ACL étendues, certains champs des protocoles de transport comme TCP ou UDP.

Les ACL existent depuis les premières générations de systèmes de routage IP et restent un outil fondamental pour appliquer une politique de filtrage simple directement sur un équipement réseau. Elles sont utilisées pour limiter les flux entre VLANs, contrôler l’accès à certains services, réduire l’exposition des interfaces d’administration et imposer des restrictions basées sur des adresses ou des protocoles. Leur syntaxe varie selon les constructeurs et les systèmes d’exploitation. Dans ce cours, les exemples s’appuient principalement sur Cisco IOS et IOS XE ; les capacités exactes doivent toujours être vérifiées pour le modèle, la version logicielle et le type d’interface employés.

Une ACL n’est pas, à elle seule, un pare-feu à états complet. Dans son usage IP classique, elle examine les paquets qui passent par un point de filtrage et compare leurs champs aux règles configurées. Elle ne déduit pas automatiquement qu’un paquet retour appartient à une session légitime simplement parce qu’un paquet aller a été permis. Une ACL simple est généralement sans état (*stateless*) : si le trafic retour doit franchir une autre interface ou être soumis à une autre ACL, une règle appropriée doit également être prévue. Des fonctionnalités supplémentaires existent sur certaines plateformes, mais elles ne doivent pas être supposées présentes dans toute ACL.

La qualité d’une politique ACL dépend autant de la logique de filtrage que de son emplacement et de son ordre. Une règle correcte placée après une règle plus générale qui intercepte déjà le trafic n’aura aucun effet. Une ACL appliquée dans le mauvais sens peut ne pas filtrer le flux attendu, ou au contraire bloquer des communications légitimes. Une règle finale implicite refuse les paquets qui ne correspondent à aucune entrée autorisante explicite. Il faut donc concevoir, documenter et tester les ACL comme une politique de sécurité, pas comme une simple suite de commandes.

> **Analogie** : Une ACL ressemble au contrôle d’accès d’un bâtiment. À l’entrée, un agent lit la première condition applicable sur une liste : « laisser entrer les employés identifiés », « refuser les visiteurs non enregistrés », « autoriser les livraisons pendant certaines heures ». Dès qu’une condition correspond, l’agent applique la décision associée et n’examine pas les instructions suivantes pour la même demande. Si le visiteur ne correspond à aucune consigne explicite, le règlement peut prévoir de lui refuser l’accès. Dans un réseau, l’adresse IP source ressemble à l’identité déclarée du demandeur, l’adresse destination correspond au bâtiment ou au service visé, le protocole correspond au type d’accès demandé et le port TCP/UDP représente un service précis, par exemple le Web. Comme un badge peut être falsifié ou emprunté, une adresse IP source ne prouve pas à elle seule l’identité réelle d’un utilisateur. Une ACL est un moyen de faire respecter une politique à un point du réseau ; elle ne remplace donc ni l’authentification, ni la segmentation, ni les contrôles de sécurité complémentaires.


## 1. La théorie et les algorithmes

### 1.1. Définition d’une ACL

Une ACL est une liste ordonnée d’entrées de contrôle d’accès, souvent appelées ACE (*Access Control Entries*). Chaque entrée contient une condition de correspondance et une action. La condition peut porter sur une adresse source, une adresse destination, un protocole IP, un port TCP ou UDP, un type de message ICMP ou d’autres critères pris en charge par la plateforme.

Exemple conceptuel :

```text
Entrée 10 : autoriser les hôtes du réseau 192.168.10.0/24
            à accéder au serveur 192.168.20.10 en HTTPS.
Entrée 20 : refuser les autres communications du réseau utilisateur
            vers le réseau serveur 192.168.20.0/24.
Entrée 30 : autoriser le reste du trafic qui doit continuer à circuler.
Fin de la liste : refuser tout paquet encore non correspondant.
```

Une ACL ne crée pas une route et ne remplace pas le routage. La table de routage détermine normalement le chemin de transfert du paquet ; l’ACL décide si le paquet correspond à une politique de filtrage au point où cette ACL est appliquée. Il est donc possible qu’une route existe mais que le trafic soit bloqué par une ACL. Inversement, une ACL peut autoriser un paquet que le routeur ne sait pas acheminer, auquel cas la communication échoue malgré l’autorisation.

Une ACL peut être créée sans être appliquée à une interface. Dans ce cas, elle ne filtre pas nécessairement le trafic de transit : il faut l’attacher à l’interface ou à la fonction qui doit l’utiliser. La manière de l’appliquer dépend de l’objectif : filtrage entrant ou sortant sur une interface, contrôle des lignes VTY d’administration, protection du plan de contrôle ou autre fonction propre à la plateforme.

### 1.2. Les principaux types d’ACL IP

Dans l’environnement Cisco IOS classique, on distingue principalement les ACL IPv4 standard et étendues.

| Type | Critères principaux | Utilisation typique |
|---|---|---|
| ACL standard | Adresse IP source | Autoriser ou refuser des sources dans leur ensemble |
| ACL étendue | Protocole, source, destination et, selon le protocole, ports ou types | Autoriser ou refuser des services et des flux précis |
| ACL nommée | Méthode de configuration par nom ; peut être standard ou étendue | Faciliter la lecture et la maintenance |
| ACL numérotée | Méthode historique d’identification par numéro | Configurations anciennes ou exercices de base |

Le mot « nommée » ne décrit pas une capacité de filtrage différente de « standard » ou « étendue ». Une ACL nommée peut être standard ou étendue. Le nom rend souvent la politique plus lisible, par exemple `USERS_TO_SERVERS`, `VLAN10_IN` ou `MGMT_VTY_ONLY`.

Les plages de numéros historiques courantes pour les ACL IPv4 Cisco comprennent `1–99` et `1300–1999` pour des ACL standard, ainsi que `100–199` et `2000–2699` pour des ACL étendues. Ces plages sont propres à la famille de commandes et à l’histoire de Cisco IOS ; elles ne constituent pas une règle universelle pour tous les constructeurs ou toutes les fonctions. Les ACL nommées sont généralement préférables dans les nouveaux exemples, lorsqu’elles sont prises en charge.

### 1.3. ACL standard : filtrage fondé sur la source

Une ACL standard IPv4 examine principalement l’adresse IP source du paquet. Elle ne permet pas de différencier directement, par exemple, le trafic HTTPS vers un serveur du trafic SSH vers ce même serveur, car elle ne sélectionne pas le protocole de transport et le port de destination de la même manière qu’une ACL étendue.

Exemple de syntaxe numérotée :

```cisco
access-list 10 permit 192.168.10.0 0.0.0.255
access-list 10 deny any
```

La première ligne autorise les paquets dont l’adresse source appartient au réseau correspondant à `192.168.10.0 0.0.0.255`. La seconde ligne refuse les autres sources. L’entrée explicite `deny any` est redondante du point de vue du résultat final, car une ACL IP IOS possède un refus implicite à la fin. Elle peut toutefois être utile pédagogiquement ou opérationnellement pour rendre la politique lisible et, si `log` est utilisé, faciliter l’observation. Il faut se rappeler que l’ajout d’un journal sur une règle très large peut générer un grand volume de messages.

La wildcard `0.0.0.255` correspond à un masque de sous-réseau `255.255.255.0`. Elle indique quelles parties de l’adresse peuvent varier lors de la correspondance. Le fonctionnement des wildcards est détaillé dans la section 1.7.

Les ACL standard sont souvent placées près de la destination dans les exemples pédagogiques, car elles ne regardent que la source. Cette règle est une heuristique classique, pas une loi absolue : l’emplacement doit être choisi en fonction de la politique, de la topologie, de l’effet souhaité et du risque de bloquer d’autres communications légitimes.

### 1.4. ACL étendue : filtrage du protocole, de la source et de la destination

Une ACL étendue peut distinguer les flux en utilisant plusieurs critères. Elle peut, par exemple, autoriser uniquement TCP vers le port 443 d’un serveur donné, autoriser certaines requêtes ICMP ou bloquer un protocole donné entre deux réseaux.

Exemple de syntaxe :

```cisco
ip access-list extended WEB_ONLY
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255
 permit ip any any
```

L’interprétation est la suivante :

1. Autoriser TCP depuis le réseau `192.168.10.0/24` vers l’hôte `192.168.20.10`, lorsque le port TCP de destination est 443.
2. Refuser tout autre trafic IP du réseau utilisateur vers le réseau `192.168.20.0/24`.
3. Autoriser les autres paquets IP qui atteignent cette ligne.
4. Refuser implicitement tout paquet qui ne correspond à aucune entrée, bien que dans cet exemple la dernière entrée `permit ip any any` autorise le trafic restant.

La dernière ligne est déterminante. Si elle est retirée, l’ACL refusera implicitement le trafic vers toutes les autres destinations qui ne correspondent pas aux entrées précédentes lorsque l’ACL est appliquée au point de filtrage. L’objectif d’une politique doit donc être formulé avant de construire les règles : filtrer seulement l’accès à un réseau particulier, ou appliquer une politique plus restrictive à l’ensemble du trafic entrant sur une interface ?

Les ACL étendues sont souvent placées près de la source pour bloquer le trafic indésirable tôt dans le chemin. Là encore, c’est une recommandation de conception fréquente, pas une règle sans exception. Une ACL trop proche de la source peut affecter d’autres destinations si la politique est mal écrite ; une ACL plus proche de la destination peut être préférable lorsque le filtrage doit s’appliquer de façon centralisée.

### 1.5. Algorithme de correspondance : la première règle correspondante gagne

Le fonctionnement d’une ACL IPv4 classique est séquentiel du point de vue logique. Le paquet est comparé à la première entrée, puis à la deuxième si la première ne correspond pas, et ainsi de suite. Dès que la première entrée correspond, l’action est appliquée et les entrées suivantes ne sont pas évaluées pour ce paquet.

Pseudocode simplifié :

```text
fonction filtrer(paquet, ACL):
    pour chaque règle dans l'ordre de la liste:
        si paquet correspond à règle:
            retourner action de la règle
    retourner REFUSER  # refus implicite final
```

Ce modèle explique pourquoi l’ordre des règles est crucial. Considérons la liste suivante :

```text
10 permit ip any any
20 deny tcp any host 192.168.20.10 eq 23
```

La règle 10 autorise tous les paquets IP. Tout paquet correspondant à la tentative Telnet vers `192.168.20.10` correspond déjà à cette première règle. La règle 20 n’est donc jamais utilisée pour ce trafic. Si le but est de refuser Telnet, le refus doit apparaître avant l’autorisation générale.

La version logique appropriée est :

```text
10 deny   tcp any host 192.168.20.10 eq 23
20 permit ip any any
```

Les numéros indiquent l’ordre, pas une priorité numérique intrinsèque séparée : c’est leur ordre effectif dans la liste qui compte. Avec les ACL nommées modernes, les numéros de séquence facilitent l’ajout et la suppression d’entrées, mais le principe de première correspondance reste essentiel.

Une ACL ne recherche pas nécessairement « la règle la plus précise » comme le fait le mécanisme de sélection de routes par préfixe le plus long. Dans une ACL classique, la première règle qui correspond détermine l’action. Il ne faut donc pas mettre automatiquement la règle la plus générale en premier.

### 1.6. Refus implicite final

À la fin d’une ACL IP, Cisco IOS applique un refus implicite aux paquets qui n’ont correspondu à aucune entrée autorisante. Ce comportement est souvent résumé par l’expression `deny any` ou `deny ip any any` implicite, selon le type de liste.

Exemple :

```cisco
ip access-list standard ADMIN_SOURCES
 permit 192.168.99.0 0.0.0.255
```

Cette liste autorise les sources du réseau `192.168.99.0/24` et refuse les autres sources. Elle ne contient aucune ligne `deny`, mais elle n’autorise pas tout le reste. L’absence d’une règle explicite de refus ne signifie donc pas « tout est permis ».

Cette règle est l’une des sources les plus fréquentes de panne lorsqu’une ACL est ajoutée sur une interface. Une liste créée pour autoriser un seul service peut bloquer les autres flux si aucune règle ne les autorise. À l’inverse, une règle finale `permit ip any any` peut rendre la politique trop permissive si elle est placée avant un refus nécessaire ou si elle autorise des flux qui auraient dû rester interdits.

L’administrateur doit toujours rédiger la politique attendue en langage clair, puis vérifier que chaque cas nécessaire est explicitement autorisé et que le refus implicite ne bloque pas un besoin légitime. Il est également utile de tester à la fois le trafic que l’on veut autoriser et celui que l’on veut refuser.

### 1.7. Wildcard mask : comprendre les bits qui peuvent varier

Dans les ACL IPv4 Cisco, la wildcard mask est souvent utilisée pour déterminer les bits d’une adresse qui doivent correspondre exactement et ceux qui peuvent varier. Elle ressemble au masque de sous-réseau, mais elle s’interprète à l’inverse :

- un bit `0` dans la wildcard impose une correspondance avec le bit de l’adresse indiquée ;
- un bit `1` dans la wildcard autorise ce bit à varier.

Exemples courants :

| But | Adresse | Wildcard | Équivalent courant |
|---|---|---|---|
| Correspondre à un hôte exact | `192.168.10.25` | `0.0.0.0` | `host 192.168.10.25` |
| Correspondre à un `/24` | `192.168.10.0` | `0.0.0.255` | `192.168.10.0/24` |
| Correspondre à un `/16` | `10.20.0.0` | `0.0.255.255` | `10.20.0.0/16` |
| Correspondre à n’importe quelle adresse | `0.0.0.0` | `255.255.255.255` | `any` |

La relation habituelle pour un masque contigu est :

```text
Wildcard = 255.255.255.255 - masque de sous-réseau
```

Ainsi, pour un masque `255.255.255.0` :

```text
255.255.255.255
-255.255.255.0
  0.  0.  0.255
```

Cette soustraction est une aide pratique pour les masques de sous-réseau conventionnels. Les wildcards peuvent aussi permettre des correspondances plus particulières, avec des bits non contigus selon la plateforme ; il ne faut donc pas toujours les interpréter comme un masque de sous-réseau ordinaire.

Les mots-clés `host` et `any` rendent la lecture plus claire. Par exemple, `permit ip host 192.168.10.25 any` est plus lisible que `permit ip 192.168.10.25 0.0.0.0 0.0.0.0 255.255.255.255`.

### 1.8. Protocoles et ports TCP/UDP

Une ACL étendue peut distinguer des protocoles IP et certains ports. Le protocole `ip` couvre le trafic IPv4 correspondant à cette catégorie de filtrage ; il ne signifie pas exclusivement TCP. `tcp`, `udp` et `icmp` permettent de sélectionner des types de trafic plus ciblés.

Exemples de ports usuels :

| Service | Protocole | Port de destination typique | Remarque |
|---|---|---:|---|
| HTTP | TCP | 80 | Web non chiffré, encore rencontré dans certains environnements |
| HTTPS | TCP | 443 | Web chiffré sur TCP ; HTTP/3 utilise généralement QUIC sur UDP 443 |
| SSH | TCP | 22 | Administration distante sécurisée, sous réserve d’une configuration correcte |
| Telnet | TCP | 23 | Administration non chiffrée ; à éviter sur les réseaux non fiables |
| DNS | UDP et TCP | 53 | Les deux transports peuvent être nécessaires selon les échanges |
| DHCPv4 serveur/client | UDP | 67/68 | Les rôles serveur et client utilisent des ports distincts |
| NTP | UDP | 123 | Synchronisation de temps |
| SNMP | UDP | 161/162 | Requêtes et notifications selon le sens de l’échange |

Exemple d’autorisation HTTPS vers un serveur :

```cisco
permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
```

Le mot-clé `eq 443` se rapporte au port TCP indiqué dans la position de la règle. Dans cette ligne, il s’agit du port destination du paquet. La position compte : une ACL peut aussi filtrer certains ports source, par exemple pour des besoins précis, mais ce n’est pas la logique de base de la plupart des politiques de services client-serveur.

Pour autoriser DNS vers un serveur spécifique, il faut généralement considérer UDP/53 et TCP/53, selon les usages. N’autorise pas un seul protocole ou port par habitude sans avoir identifié les besoins de l’application.

### 1.9. ICMP et tests de connectivité

ICMP est utilisé par des fonctions de diagnostic et de signalisation IP. Le ping utilise ICMP Echo Request et Echo Reply en IPv4. Les commandes `permit icmp` peuvent filtrer les messages ICMP en général ou des types précis lorsque la syntaxe et la plateforme le permettent.

Bloquer tout ICMP peut compliquer le dépannage et perturber des fonctions nécessaires, notamment certaines indications d’erreur ou la découverte de MTU. Une politique bien conçue distingue les messages utiles des comportements que l’organisation souhaite restreindre.

Exemple d’autorisation d’écho vers un serveur :

```cisco
permit icmp 192.168.10.0 0.0.0.255 host 192.168.20.10 echo
```

La réponse ICMP Echo Reply est un paquet distinct. Si une autre ACL filtre aussi le trafic retour, il faut vérifier qu’elle permet le message correspondant. Une ACL n’est pas automatiquement stateful : l’autorisation d’un Echo Request ne signifie pas que toute réponse associée sera automatiquement permise par toute ACL indépendante située sur le chemin retour.

Il ne faut pas confondre « le ping échoue » avec « la route est absente ». Le ping peut être bloqué par une ACL, par un pare-feu, par le système cible ou par une politique de contrôle des messages ICMP. Le diagnostic doit examiner la route, le chemin retour et les règles de filtrage.

### 1.10. Direction `in` et `out`

Lorsqu’une ACL est appliquée à une interface, on précise généralement le sens : `in` pour les paquets qui entrent dans le routeur par cette interface, et `out` pour les paquets que le routeur envoie par cette interface. Ces termes décrivent le point de vue du routeur, pas celui de l’utilisateur ou du serveur.

```text
         Paquets entrants sur G0/0
                    |
                    v
             +-------------+
             |    ROUTEUR  |
             | ACL IN      |
             +-------------+
                    |
             décision de routage
                    |
                    v
         Paquets sortants sur G0/1
              ACL OUT éventuelle
```

Une ACL entrante examine le paquet au moment où il arrive par l’interface sélectionnée. Une ACL sortante examine le paquet quand il doit quitter cette interface. Les détails d’implémentation et d’accélération matérielle varient, mais la distinction logique demeure.

Pour décider du bon sens, il est utile de tracer le paquet dans le sens réel du flux. Exemple : un PC du VLAN utilisateurs envoie un paquet à un serveur situé dans un autre VLAN. Le paquet entre normalement dans le routeur ou commutateur L3 par l’interface/SVI du VLAN utilisateurs, puis sort par l’interface/SVI du VLAN serveur. Une ACL `in` sur le VLAN utilisateurs peut appliquer une politique aux paquets initiés depuis ce VLAN.

Le trafic retour entre par l’interface/SVI du réseau serveur et ressort vers les utilisateurs. Il ne passe pas dans l’ACL `in` du VLAN utilisateurs, car il n’entre pas dans le routeur par cette interface. Il peut cependant être soumis à d’autres ACL ou contrôles. C’est pourquoi il est essentiel de dessiner le sens des flèches avant de configurer.

### 1.11. ACL stateless et trafic retour

Une ACL IP traditionnelle est généralement sans état : elle ne tient pas automatiquement une table des sessions permettant de reconnaître que le paquet courant constitue la réponse à une connexion autorisée. Les règles évaluent les paquets qui leur sont soumis.

Supposons que la règle suivante autorise une connexion initiée depuis le réseau utilisateur vers un serveur Web :

```cisco
permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
```

Elle correspond aux paquets TCP dont la source appartient au réseau utilisateur et dont la destination est le serveur sur le port 443. La réponse du serveur a normalement comme source le port TCP 443 et comme destination un port éphémère du client. Elle ne correspond donc pas à la même condition si elle rencontre une autre ACL sur le chemin retour.

Certaines ACL Cisco offrent le mot-clé `established` pour TCP. Il s’agit d’un contrôle rudimentaire basé sur la présence des indicateurs ACK ou RST ; ce n’est pas l’équivalent d’un suivi de session complet, et il ne doit pas être présenté comme une preuve d’état ou d’identité. Les mécanismes de pare-feu à états sont conçus pour une analyse des sessions plus complète.

Quand plusieurs ACL filtrent les deux sens, il faut déterminer explicitement les flux nécessaires. Ne crée pas une large autorisation `permit ip any any` uniquement pour faire fonctionner les réponses sans évaluer les conséquences de sécurité. Utilise la politique la plus limitée compatible avec les besoins, et envisage un pare-feu à états si la politique exige la reconnaissance fiable des sessions.

### 1.12. Où placer une ACL ?

Deux conseils classiques sont souvent utilisés dans les cours Cisco : les ACL étendues sont fréquemment placées près de la source, car elles peuvent identifier précisément le service et empêcher un trafic non souhaité de traverser plusieurs segments ; les ACL standard sont fréquemment placées près de la destination, car elles ne distinguent que la source et pourraient autrement empêcher cette source d’atteindre d’autres destinations utiles.

Ces conseils sont des principes de conception, pas des règles absolues. Le placement doit prendre en compte :

- le flux que l’on veut autoriser ou interdire ;
- les autres destinations que la même source doit pouvoir atteindre ;
- les chemins de transit et la présence éventuelle de plusieurs routeurs ;
- les besoins de disponibilité et de dépannage ;
- les interfaces et fonctions où la plateforme permet d’appliquer l’ACL ;
- l’effet de la règle sur le trafic de contrôle et d’administration.

Une ACL appliquée trop tôt peut bloquer des flux légitimes destinés à d’autres sous-réseaux. Une ACL appliquée trop tard peut laisser du trafic indésirable traverser une partie du réseau avant de le bloquer. Dans les réseaux avec plusieurs chemins, il faut aussi vérifier que tous les chemins possibles sont soumis à une politique cohérente.

### 1.13. ACL nommées et numéros de séquence

Les ACL nommées améliorent la lisibilité et peuvent être révisées entrée par entrée sur les plateformes qui prennent en charge les numéros de séquence.

Exemple :

```cisco
ip access-list extended USERS_TO_WEB
 10 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
 20 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 log
 30 permit ip any any
```

Les numéros 10, 20 et 30 laissent de la place pour insérer ultérieurement une règle intermédiaire. Pour examiner la liste :

```cisco
show ip access-lists USERS_TO_WEB
```

Pour supprimer une entrée par numéro de séquence, la syntaxe disponible varie selon la version IOS/IOS XE ; sur les versions appropriées, on peut utiliser la forme `no 20` depuis le mode de configuration de l’ACL. Pour une modification en production, toujours afficher la liste après changement et confirmer l’ordre final.

N’ajoute pas aveuglément de nouvelles lignes à la fin de la liste : une nouvelle règle située après `permit ip any any` ne sera jamais utilisée pour les paquets que cette autorisation générale couvre. De même, une entrée ajoutée après une règle plus générale peut être inopérante. La révision doit tenir compte de l’ordre, pas seulement du contenu des lignes.

### 1.14. Journaux et compteurs

Les ACL Cisco peuvent afficher des compteurs de correspondance et, lorsque cela est disponible et configuré, produire des messages de journal pour certaines entrées. Ces éléments aident à confirmer qu’un trafic a réellement rencontré la règle prévue.

Commandes de base :

```cisco
show access-lists
show ip access-lists
show ip access-lists USERS_TO_WEB
```

Le nom exact ou les variantes prises en charge peuvent dépendre de la plateforme. Les compteurs permettent d’observer si les règles sont utilisées, mais ils ne constituent pas à eux seuls une preuve exhaustive du comportement de tous les paquets, notamment sur des équipements qui traitent une partie du trafic dans le matériel.

L’option `log` doit être employée avec discernement. Si une règle fréquemment sollicitée journalise chaque correspondance, elle peut générer un volume élevé de messages, charger le plan de contrôle et rendre les événements importants plus difficiles à repérer. Pour une politique de production, privilégie la journalisation ciblée, l’envoi vers un collecteur central si nécessaire et une vérification des capacités de la plateforme.

### 1.15. ACL pour l’administration : VTY et interfaces réseau

Une ACL appliquée à une interface avec `ip access-group` filtre les paquets qui traversent cette interface. Le contrôle des connexions d’administration sur les lignes VTY utilise une commande distincte, traditionnellement `access-class` dans la configuration `line vty`, lorsque la plateforme le prend en charge.

Exemple conceptuel d’autorisation limitée à un réseau d’administration :

```cisco
ip access-list standard MGMT_VTY_ONLY
 permit 192.168.99.0 0.0.0.255
!
line vty 0 4
 access-class MGMT_VTY_ONLY in
 transport input ssh
```

La première partie identifie les sources autorisées à accéder à la ligne VTY. La seconde applique cette liste à l’accès administratif entrant sur les lignes concernées et limite le transport à SSH dans cet exemple. Le nombre de lignes VTY, la syntaxe exacte et les capacités disponibles peuvent varier selon le modèle et le logiciel.

Ce mécanisme n’est pas un substitut à une authentification solide. Il faut également utiliser des comptes appropriés, des secrets robustes, SSH plutôt que Telnet lorsque c’est possible, des mécanismes de gestion sécurisés et une politique de sauvegarde de configuration. Une ACL sur VTY réduit les sources possibles, mais une source autorisée reste tenue de s’authentifier.

### 1.16. ACL IPv6 : mêmes principes, syntaxe distincte

IPv6 utilise une syntaxe et des commandes d’ACL distinctes dans Cisco IOS/IOS XE. Les principes généraux demeurent : liste ordonnée, première correspondance, autorisation ou refus, et importance des messages ICMPv6 nécessaires au fonctionnement d’IPv6.

Exemple de forme moderne sur une plateforme IOS XE prenant en charge cette syntaxe :

```cisco
ipv6 access-list V6_USERS_TO_SERVER
 permit tcp 2001:db8:10::/64 host 2001:db8:20::10 eq 443
 deny ipv6 2001:db8:10::/64 2001:db8:20::/64
 permit ipv6 any any
!
interface GigabitEthernet0/0
 ipv6 traffic-filter V6_USERS_TO_SERVER in
```

Cette configuration est illustrative et doit être vérifiée sur la plateforme visée : la forme de certaines commandes et les possibilités de filtrage peuvent varier. Le préfixe `2001:db8::/32` est réservé à la documentation ; il ne doit pas être utilisé comme préfixe public réel sur Internet.

Ne transpose pas aveuglément une politique IPv4 en IPv6 sans vérifier les mécanismes nécessaires à IPv6, notamment ICMPv6, la découverte des voisins (NDP), la découverte du routeur, la découverte de MTU et la configuration automatique éventuelle. Un filtrage IPv6 trop agressif peut casser la connectivité même si les règles TCP/UDP semblent correctes.

### 1.17. Ce qu’une ACL ne fait pas

Une ACL classique n’est ni une route, ni un mécanisme d’authentification, ni une inspection approfondie de contenu, ni nécessairement un pare-feu à états. Elle ne chiffre pas les communications et ne garantit pas que l’adresse source d’un paquet est authentique. Les adresses peuvent être usurpées dans certains contextes ; des contrôles supplémentaires au niveau des ports, des VLANs, des mécanismes d’anti-usurpation et des systèmes d’identité peuvent être nécessaires.

Une ACL IP placée sur un routeur n’inspecte généralement que le trafic qui atteint le point d’application. Elle ne bloque pas automatiquement un échange qui reste dans le même VLAN commuté au niveau 2, sauf si l’équipement et la fonction de filtrage correspondants sont configurés pour ce trafic. Sur un commutateur de couche 2, des fonctions telles que les ACL de port, les ACL VLAN ou les ACL de couche 2 dépendent du modèle et ne doivent pas être supposées équivalentes aux ACL IP d’un routeur.

Une politique composée uniquement d’ACL peut devenir difficile à maintenir si les exigences comprennent un suivi complexe des sessions, l’identification applicative, l’inspection approfondie ou des règles très dynamiques. Dans de tels cas, une solution de pare-feu appropriée peut être plus adaptée. Les ACL restent néanmoins excellentes pour des politiques ciblées, un contrôle simple et une défense en profondeur.

> **Piège :** La première règle qui correspond gagne. Une règle `permit ip any any` placée avant une règle de refus rendra généralement cette règle de refus inopérante pour les paquets couverts par l’autorisation générale. N’oublie pas non plus le refus implicite à la fin : une ACL qui autorise un seul service peut bloquer tous les autres flux traversant le point d’application. Avant d’attacher une ACL à une interface, calcule les effets sur le trafic attendu dans les deux sens.

```text
                 EXEMPLE DE FILTRAGE ENTRE VLANs

      VLAN UTILISATEURS                         VLAN SERVEURS
      192.168.10.0/24                           192.168.20.0/24

        +-----------+        G0/0       G0/1       +-----------+
        |    PC     |----------->+-----------+---->| Serveur   |
        | .10.25    |            |  ROUTEUR  |     | .20.10    |
        +-----------+            |           |     +-----------+
                                 | ACL IN    |
                                 | sur G0/0  |
                                 +-----------+

      Le paquet PC -> serveur entre par G0/0.
      L'ACL IN de G0/0 examine ce paquet.
      La réponse serveur -> PC entre par G0/1 :
      elle ne traverse pas l'ACL IN appliquée à G0/0.
      D'autres règles peuvent toutefois filtrer ce retour.
```


## 2. Configuration et Pratique

### 2.1. Objectif du laboratoire

Nous allons configurer une ACL étendue nommée sur un routeur Cisco IOS pour contrôler l’accès depuis un réseau utilisateurs vers un réseau serveurs.

Politique demandée :

- le réseau utilisateurs `192.168.10.0/24` peut atteindre le serveur Web `192.168.20.10` en HTTP et HTTPS ;
- les utilisateurs peuvent envoyer un ping au serveur pour le diagnostic ;
- les autres communications IP du réseau utilisateurs vers le réseau serveurs sont refusées ;
- le trafic destiné à d’autres réseaux continue à être autorisé par cet exemple de politique ;
- le trafic retour initié par le serveur est examiné séparément si d’autres ACL sont appliquées.

La dernière autorisation est volontairement présente afin de démontrer qu’une ACL doit exprimer la politique complète souhaitée. Dans un réseau de production, ne la copie pas sans analyse : elle permet ici le reste du trafic IP qui rencontre cette ACL.

### 2.2. Topologie et plan d’adressage

```text
                 LAN UTILISATEURS
                 192.168.10.0/24

        PC-USER                         R1
     192.168.10.25                G0/0 192.168.10.1
           |                           +---------+
           +---------------------------|         |
                                       | ROUTEUR |
                                       |         |
           +---------------------------|         |
           |                           +---------+
        SERVER-WEB                    G0/1 192.168.20.1
     192.168.20.10                         |
                                    LAN SERVEURS
                                    192.168.20.0/24
```

Ce schéma illustre les deux réseaux directement connectés à R1. Dans un environnement de production, l’adressage et les noms d’interfaces doivent être adaptés. Les noms `GigabitEthernet0/0` et `GigabitEthernet0/1` sont des exemples ; certaines plateformes utilisent des conventions différentes.

### 2.3. Configuration des interfaces

```cisco
hostname R1
!
interface GigabitEthernet0/0
 description VLAN_UTILISATEURS
 ip address 192.168.10.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 description VLAN_SERVEURS
 ip address 192.168.20.1 255.255.255.0
 no shutdown
```

Les adresses IP créent deux réseaux directement connectés lorsque les interfaces sont opérationnelles. Cette configuration ne configure pas automatiquement les adresses des postes : les hôtes doivent avoir des adresses appartenant à leur sous-réseau, un masque approprié et la passerelle correcte.

Vérifie l’état des interfaces avant d’ajouter l’ACL :

```cisco
show ip interface brief
show interfaces GigabitEthernet0/0
show interfaces GigabitEthernet0/1
```

Une interface désactivée, un VLAN absent sur un commutateur, un trunk mal configuré ou un mauvais adressage peuvent provoquer une panne qui ressemble à tort à un problème d’ACL. Il faut d’abord établir la connectivité de base, puis appliquer le filtrage.

### 2.4. Configurer l’ACL étendue nommée

```cisco
ip access-list extended USERS_TO_SERVERS
 remark Autoriser HTTP du VLAN utilisateurs vers le serveur Web
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 80
 remark Autoriser HTTPS du VLAN utilisateurs vers le serveur Web
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
 remark Autoriser Echo Request pour le diagnostic du serveur
 permit icmp 192.168.10.0 0.0.0.255 host 192.168.20.10 echo
 remark Refuser les autres flux IP vers le réseau serveurs
 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 log
 remark Autoriser les autres destinations selon la politique du labo
 permit ip any any
```

Les lignes `remark` décrivent l’intention de la politique. Elles n’autorisent et ne refusent aucun paquet. Elles facilitent cependant la lecture et la maintenance d’une liste qui pourrait autrement sembler être une suite de critères cryptiques.

Les deux premières entrées autorisent TCP vers les ports destination 80 et 443 du serveur. La troisième autorise les messages ICMP Echo Request depuis le réseau utilisateurs vers le serveur. La quatrième refuse tous les autres paquets IP du réseau utilisateurs vers n’importe quelle adresse du réseau `192.168.20.0/24`. La cinquième autorise le trafic restant qui atteint l’ACL.

Attention : la règle de refus cible le réseau source complet et le réseau destination complet. Si d’autres serveurs sont présents dans ce sous-réseau, les utilisateurs ne pourront leur envoyer aucun autre trafic IP qui arrive à cette ACL, sauf si une règle autorisante plus spécifique est ajoutée avant ce refus.

L’option `log` demande une journalisation des correspondances selon les capacités de la plateforme. Sur une règle potentiellement très sollicitée, surveille le volume de messages et les ressources consommées. En production, l’usage du journal doit être adapté à la fréquence attendue du trafic.

### 2.5. Appliquer l’ACL dans le bon sens

Dans ce laboratoire, l’objectif est de filtrer les paquets qui arrivent depuis le réseau utilisateurs. L’ACL est donc appliquée en entrée sur G0/0 :

```cisco
interface GigabitEthernet0/0
 ip access-group USERS_TO_SERVERS in
```

Le mot-clé `in` signifie que l’ACL examine les paquets entrant dans R1 par G0/0. Il ne signifie pas que le trafic qui va vers le réseau utilisateurs est filtré. Cette dernière interprétation serait incorrecte.

La règle ne filtre pas directement les paquets qui entrent par G0/1 depuis le réseau serveurs. Si une politique impose également de filtrer le trafic initié par les serveurs, il faut concevoir et appliquer des contrôles supplémentaires adaptés à cette exigence.

Après application, vérifie que la liste est présente sur l’interface attendue :

```cisco
show ip interface GigabitEthernet0/0
show ip access-lists USERS_TO_SERVERS
```

La première commande permet, selon le système, de vérifier quelles listes sont associées à l’interface et dans quel sens. La seconde permet d’examiner les entrées et les compteurs de correspondance.

### 2.6. Cas pratiques à tester

| Test | Résultat attendu avec la configuration du laboratoire | Justification |
|---|---|---|
| PC `192.168.10.25` vers `192.168.20.10:80/TCP` | Autorisé | Correspond à la première entrée |
| PC `192.168.10.25` vers `192.168.20.10:443/TCP` | Autorisé | Correspond à la deuxième entrée |
| Ping PC vers `192.168.20.10` | Echo Request autorisé | Correspond à la troisième entrée ; il faut aussi vérifier le retour |
| PC vers un autre hôte du réseau `192.168.20.0/24` en IP | Refusé | Correspond au refus ciblant le réseau serveurs |
| PC vers une destination hors des deux réseaux, si routée | Autorisé par cette ACL | Correspond à `permit ip any any`, sous réserve des autres contrôles |
| Trafic qui ne rentre pas par G0/0 | Non filtré par cette application particulière | L’ACL est appliquée uniquement en entrée sur G0/0 |

Les résultats dépendent également de la route, de l’état des interfaces, de la configuration des hôtes et de la présence d’autres politiques de filtrage. L’ACL n’est qu’un élément de la chaîne de transmission.

### 2.7. Exemple d’ACL standard pour une source précise

Si l’objectif consiste à filtrer en fonction de l’adresse source uniquement, une ACL standard peut être appropriée.

```cisco
ip access-list standard TRUSTED_SOURCES
 permit 192.168.99.0 0.0.0.255
```

Cette liste correspond aux sources du réseau `192.168.99.0/24` et refuse implicitement les autres. Elle peut être utile pour un objectif limité, mais il faut choisir avec soin son point d’application. L’appliquer sur une interface de transit peut bloquer toutes les communications provenant des autres réseaux, pas seulement l’accès à un service particulier.

Pour limiter l’accès aux lignes VTY, l’exemple suivant illustre une fonction différente de `ip access-group` :

```cisco
ip access-list standard MGMT_VTY_ONLY
 permit 192.168.99.0 0.0.0.255
!
line vty 0 4
 access-class MGMT_VTY_ONLY in
 transport input ssh
```

La liste limite les sources pouvant ouvrir une session sur les lignes VTY correspondantes. SSH demeure nécessaire pour protéger le transport ; l’ACL ne chiffre pas les identifiants et ne prouve pas l’identité de l’utilisateur. Vérifie le nombre réel de lignes VTY et la syntaxe de la plateforme avant d’utiliser cet extrait.

### 2.8. Contrôler et sauvegarder

Commandes de vérification utiles :

```cisco
show ip access-lists
show ip access-lists USERS_TO_SERVERS
show running-config interface GigabitEthernet0/0
show ip interface GigabitEthernet0/0
show ip route
```

Elles permettent d’examiner le contenu de l’ACL, son association à l’interface, les routes nécessaires et certains compteurs. Utilise également `ping` et `traceroute` pour tester les chemins, sans oublier qu’un ICMP bloqué ne prouve pas à lui seul que tous les services applicatifs sont inaccessibles.

Quand les essais sont concluants, sauvegarde la configuration selon les procédures de l’environnement :

```cisco
copy running-config startup-config
```

Cette commande sauvegarde la configuration active dans la configuration de démarrage sur les plateformes qui utilisent ce modèle. Dans un environnement professionnel, elle doit s’inscrire dans un processus de changement : sauvegarde préalable, fenêtre d’intervention, validation des tests et procédure de retour arrière.

Il est préférable d’effectuer un changement ACL à la fois. Si plusieurs règles, interfaces et fonctions sont modifiées simultanément, l’identification d’une régression devient plus difficile. Documente les objectifs, les entrées ajoutées, le point d’application et le résultat des tests.


## 3. Dépannage et Sécurité

### 3.1. Méthode structurée de dépannage

Lorsqu’un flux ne fonctionne pas après l’application d’une ACL, évite de supprimer immédiatement toute la politique. Le diagnostic doit déterminer si le paquet est bloqué par l’ACL, s’il n’atteint jamais cette ACL ou s’il échoue pour une autre raison.

Une démarche efficace suit cet ordre :

1. Confirmer la source, la destination, le protocole et le port réels du flux.
2. Vérifier les adresses IP, les masques, les passerelles et l’état des interfaces.
3. Vérifier qu’une route existe vers la destination et qu’un chemin de retour est disponible.
4. Contrôler quelle ACL est attachée à chaque interface et dans quel sens.
5. Lire l’ACL dans l’ordre exact où elle est évaluée.
6. Observer les compteurs et les journaux, en gardant à l’esprit les limites des compteurs sur certaines plateformes.
7. Tester à nouveau un seul flux, puis comparer le résultat à la politique prévue.

Le but n’est pas d’autoriser temporairement tout le trafic pour « voir si ça marche ». Une règle générale de type `permit ip any any` peut masquer l’erreur et laisser une exposition trop large. Dans un réseau de production, tout élargissement temporaire doit être maîtrisé, approuvé, limité dans le temps et documenté.

### 3.2. Symptôme : plus aucun trafic ne fonctionne

Si une ACL nouvellement appliquée bloque la plupart des communications, les causes possibles incluent un refus implicite qui n’avait pas été pris en compte, une règle `deny` trop générale, un ordre incorrect ou une ACL appliquée à la mauvaise interface ou dans le mauvais sens.

Exemple de politique trop restrictive :

```cisco
ip access-list extended TEST
 permit tcp host 192.168.10.25 host 192.168.20.10 eq 443
interface GigabitEthernet0/0
 ip access-group TEST in
```

Cette liste ne permet explicitement qu’un flux TCP correspondant à cette condition. Tous les paquets qui ne correspondent pas à cette entrée sont refusés implicitement au point d’application. Selon la manière dont l’interface est utilisée, elle peut donc bloquer DNS, ICMP, d’autres services ou le trafic destiné à d’autres réseaux.

La solution consiste à reformuler la politique complète, pas à ajouter une autorisation générale sans analyse. Identifie les communications indispensables, crée les autorisations nécessaires avant les refus appropriés et teste chaque catégorie de trafic.

### 3.3. Symptôme : une règle de refus ne semble jamais fonctionner

Une règle de refus peut avoir un compteur nul parce que le trafic ne la rencontre jamais, parce qu’il correspond à une entrée précédente ou parce que le trafic emprunte un autre chemin.

Considère :

```cisco
ip access-list extended FILTER
 10 permit ip any any
 20 deny tcp any host 192.168.20.10 eq 23
```

La règle 20 ne bloque pas Telnet correspondant à la première règle : la première correspondance l’emporte. Place le refus avant l’autorisation générale :

```cisco
ip access-list extended FILTER
 10 deny tcp any host 192.168.20.10 eq 23
 20 permit ip any any
```

Il faut aussi vérifier si le trafic entre réellement par l’interface à laquelle la liste est attachée, si la bonne version de la liste est en cours d’utilisation et si un autre dispositif effectue le filtrage en amont.

### 3.4. Symptôme : le ping échoue, mais le Web fonctionne

Ce comportement peut être normal si la politique autorise TCP/80 ou TCP/443 mais refuse les messages ICMP. L’échec du ping ne signifie pas nécessairement que le serveur est hors service. Teste le service réel avec l’outil approprié et vérifie les règles ICMP et les autres mécanismes de filtrage.

Inversement, un ping réussi ne prouve pas qu’un service TCP particulier est accessible. Le ping teste une fonction de diagnostic fondée sur ICMP ; il ne vérifie pas directement l’établissement d’une session HTTPS, la résolution DNS ou le fonctionnement applicatif.

Une politique peut autoriser ICMP pour le diagnostic tout en interdisant certains ports applicatifs. Elle peut aussi autoriser des ports applicatifs tout en restreignant certains types ICMP. L’objectif doit être de permettre les fonctions nécessaires sans ouvrir inutilement l’ensemble du trafic.

### 3.5. Symptôme : l’aller passe, mais la réponse échoue

Une ACL stateless peut autoriser un paquet dans un sens et refuser la réponse si celle-ci rencontre une autre ACL. Pour chaque flux, trace les deux directions :

```text
Initiateur --------------------> Serveur
          paquet aller

Initiateur <-------------------- Serveur
          paquet retour
```

La réponse n’a pas exactement les mêmes adresses et ports source/destination que la requête. Une ACL étendue qui filtre les deux directions doit tenir compte de ces différences. Si la politique exige un suivi rigoureux des sessions, un pare-feu à états peut être plus adapté qu’une série de règles stateless.

Vérifie le chemin retour, la présence de routes, le NAT éventuel et toutes les ACL rencontrées par la réponse. Un problème de retour peut aussi provenir d’une passerelle incorrecte ou d’un routage asymétrique, pas seulement d’une ACL.

### 3.6. Syntaxe et correspondances inattendues

Une erreur de wildcard ou une mauvaise adresse réseau peut élargir ou réduire involontairement une règle. Par exemple :

```cisco
permit ip 192.168.10.0 0.0.0.255 any
```

correspond au réseau `192.168.10.0/24` comme source, tandis que :

```cisco
permit ip 192.168.10.0 0.0.255.255 any
```

correspond à un ensemble beaucoup plus large, habituellement `192.168.0.0/16` lorsque l’adresse de base est alignée comme indiqué. Une wildcard erronée peut autoriser davantage de sources que prévu.

Relis chaque entrée en langage clair : qui est la source, qui est la destination, quel protocole est autorisé, quel port est visé et quelle est l’action finale ? Vérifie ensuite le préfixe et la wildcard avec un calcul indépendant ou un outil de validation approuvé.

### 3.7. Journaux trop abondants ou absents

L’option `log` peut aider à confirmer qu’une entrée correspond à un paquet. Cependant, un grand nombre de correspondances peut générer beaucoup de journaux. Sur un équipement sous charge, une journalisation excessive peut compliquer l’analyse et solliciter inutilement les ressources du plan de contrôle.

Si aucun journal n’est visible, cela ne prouve pas forcément que la règle n’est pas utilisée. Vérifie la présence du mot-clé `log`, le niveau de journalisation, la destination des messages, les compteurs de correspondance et les capacités de la plateforme. Certains équipements traitent en matériel une partie du trafic ; les comportements de comptage et de journalisation peuvent varier.

Pour un déploiement professionnel, préfère une journalisation ciblée sur les refus réellement utiles, un collecteur Syslog correctement protégé et une politique de rétention adaptée. Les informations de journaux peuvent contenir des adresses et des éléments de topologie qui doivent être protégés.

### 3.8. Sécurité : moindre privilège et segmentation

Une ACL doit appliquer le principe du moindre privilège : autoriser uniquement les flux dont le besoin est établi et éviter les autorisations générales inutiles. Le principe s’applique au niveau de l’adresse source, de la destination, du protocole, du port et du point où le filtrage est effectué.

Dans une architecture segmentée, chaque VLAN correspond souvent à un rôle fonctionnel : utilisateurs, serveurs, administration, voix, invités, équipements IoT. Les ACL de couche 3 peuvent limiter les flux entre ces zones. Toutefois, une segmentation efficace doit aussi tenir compte du trafic qui reste dans le même VLAN et des contrôles disponibles sur les commutateurs et les pare-feu.

Une politique robuste doit prévoir les flux nécessaires aux services d’infrastructure tels que DNS, DHCP, NTP, la supervision et l’administration. Bloquer ces fonctions sans préparation peut provoquer des pannes difficiles à identifier. Il faut documenter explicitement les dépendances et vérifier leur fonctionnement après chaque changement.

### 3.9. Usurpation d’adresse et limites d’une ACL basée sur la source

Une ACL qui autorise `192.168.10.0/24` fait confiance à la valeur d’adresse source présente dans le paquet. Cette valeur ne constitue pas une authentification cryptographique. Dans certaines situations, un attaquant peut forger une adresse source ; le succès de l’attaque dépend de la topologie, du routage, des contrôles du réseau et des possibilités de recevoir les réponses.

Les mesures complémentaires peuvent inclure le filtrage anti-usurpation à la périphérie, les contrôles d’adresse source sur les ports d’accès, DHCP Snooping et IP Source Guard lorsqu’ils sont adaptés, ainsi qu’une segmentation et une authentification convenables. Les fonctionnalités disponibles varient selon les équipements.

Ne considère pas une règle « autoriser uniquement telle adresse source » comme une preuve complète d’identité. Elle peut réduire les chemins de trafic, mais doit être combinée avec des protections adaptées au risque et au contexte.

### 3.10. Sécurité du plan d’administration

Les équipements réseau doivent être administrés à partir de sources limitées et de protocoles sécurisés. Une ACL sur les lignes VTY peut restreindre les adresses qui peuvent tenter une connexion, mais elle ne remplace pas SSH, une authentification solide, le contrôle des comptes ni la protection des secrets.

Évite de rendre l’administration accessible depuis des réseaux utilisateurs ou invités sans justification. Sépare le réseau de gestion si l’architecture le permet, limite les sources de gestion à des sous-réseaux dédiés et journalise les changements. Les accès hors bande peuvent aussi aider à récupérer un équipement si une ACL de transit provoque une panne.

Avant de modifier une ACL qui affecte l’accès administrateur, conserve une session de gestion de secours ou un accès console contrôlé, lorsque cela est possible. Une erreur de filtrage sur VTY peut empêcher l’administrateur de se reconnecter à distance. Prépare la procédure de retour arrière avant d’appliquer le changement.

### 3.11. Méthode de changement sûre

Une ACL de production doit être créée à partir d’une demande explicite, documentée et testable. Un processus raisonnable comprend :

1. **Définir l’objectif** : flux à autoriser et flux à bloquer, avec sources et destinations exactes.
2. **Cartographier le chemin** : interfaces d’entrée et de sortie, sens du trafic et chemin de retour.
3. **Construire les règles** : ordre séquentiel, wildcards vérifiées, refus explicites si utiles et prise en compte du refus implicite.
4. **Évaluer l’impact** : services d’infrastructure, gestion, routage et autres flux traversant l’interface.
5. **Sauvegarder** : conserver la configuration précédente et le plan de retour arrière.
6. **Appliquer par étapes** : éviter les changements multiples non corrélés.
7. **Tester** : cas autorisés, cas interdits, sens aller/retour, services d’infrastructure et gestion.
8. **Contrôler les compteurs et journaux** : confirmer que le trafic correspond aux règles prévues.
9. **Documenter et sauvegarder** : mise à jour du référentiel et sauvegarde de la configuration validée.

Pour les équipements qui prennent en charge des mécanismes de confirmation temporisée ou de retour arrière automatisé, vérifie les fonctionnalités et la procédure correspondantes. Ne suppose pas qu’elles existent sur chaque plateforme.

### 3.12. Liste de contrôle avant mise en production

- La politique est formulée en langage clair et validée par le propriétaire du service.
- Chaque adresse réseau et wildcard a été vérifiée.
- Les règles les plus spécifiques à appliquer en priorité se trouvent avant les autorisations plus générales.
- Le refus implicite final est compris et pris en compte.
- Le sens `in` ou `out` correspond au trajet réel des paquets.
- Les flux retour et les services d’infrastructure ont été analysés.
- Les compteurs, les journaux et les tests sont préparés.
- Les commandes de vérification sont connues et l’accès d’administration est préservé.
- La configuration précédente et le plan de retour arrière sont disponibles.
- La politique sera revue après le changement afin de retirer les règles devenues inutiles.

> **Astuce :** Écris d’abord chaque règle sous la forme « autoriser/refuser [protocole] de [source] vers [destination] sur [port/type] ». Convertis ensuite les sous-réseaux en wildcards et classe les entrées dans l’ordre réel de traitement. Cette méthode réduit les erreurs de syntaxe et permet à une autre personne de relire l’intention avant l’application. Après déploiement, compare les compteurs de `show ip access-lists` avec les tests réels.

> **Danger :** Une ACL mal placée ou trop permissive peut couper l’administration d’un routeur, bloquer des services métier, exposer un réseau interne ou perturber des services d’infrastructure. Une autorisation générale placée trop tôt peut neutraliser des refus ultérieurs. Une restriction trop large peut provoquer une panne en raison du refus implicite. Ne déploie jamais une ACL critique sans sauvegarde, tests ciblés, vérification du sens de filtrage et procédure de retour arrière.


## Points à retenir

- **Une ACL classique traite les règles dans l’ordre et applique la première correspondance.** Les entrées placées après une règle qui correspond déjà au paquet ne sont pas évaluées pour ce paquet. L’ordre des entrées est aussi important que leur contenu.
- **Le refus implicite final signifie que tout paquet non autorisé explicitement est refusé au point d’application.** Il faut définir la politique complète avant d’attacher l’ACL à une interface, puis tester les flux autorisés et interdits.
- **Les ACL standard examinent principalement la source ; les ACL étendues peuvent filtrer protocole, source, destination et ports.** Les wildcards doivent être calculées avec soin et le sens `in`/`out` doit être déterminé en suivant le paquet dans le réseau.
- **Une ACL n’est pas automatiquement stateful et ne remplace ni le routage ni l’authentification.** Le trafic retour, les routes, les services d’infrastructure, l’usurpation d’adresse et les besoins de journalisation doivent être considérés séparément.
- **La configuration doit être vérifiée et testée.** Utilise notamment `show ip access-lists`, `show ip interface`, `show running-config` et les outils de connectivité. Prépare une sauvegarde et un retour arrière avant toute modification sensible.


## Références techniques

- Cisco, *Configure IP Access Lists* : https://www.cisco.com/c/en/us/support/docs/security/ios-firewall/23602-confaccesslists.html
- Cisco, *Security Configuration Guide: Access Control Lists, Cisco IOS XE* : https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_data_acl/configuration/xe-16-9/sec-data-acl-xe-16-9-book.html
- IETF, RFC 2979, *Behavior of and Requirements for Internet Firewalls* : https://www.rfc-editor.org/rfc/rfc2979.html
- IETF, RFC 1918, *Address Allocation for Private Internets* : https://www.rfc-editor.org/rfc/rfc1918.html

Les exemples sont principalement destinés à Cisco IOS/IOS XE. Avant un déploiement réel, confirme toujours la syntaxe exacte, les fonctions prises en charge, l’ordre de traitement sur la plateforme et les exigences de la politique de sécurité de l’organisation.
