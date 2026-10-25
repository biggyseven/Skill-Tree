# NAT & PAT - Débutant

**Niveau :** Débutant

La traduction d’adresses réseau, connue sous le nom de NAT (*Network Address Translation*), est une fonction qui modifie certaines informations d’adressage des paquets IP lorsqu’ils traversent un équipement réseau. Elle est surtout connue pour permettre à plusieurs machines utilisant des adresses IPv4 privées de communiquer avec des services situés sur Internet au moyen d’une ou de quelques adresses IPv4 publiques. Elle est aussi employée dans des réseaux d’entreprise, lors de l’interconnexion de plages d’adresses qui se chevauchent, ou pour publier certains services internes vers l’extérieur.

Le NAT est devenu courant à mesure que l’utilisation d’Internet a augmenté et que les adresses IPv4 publiques disponibles sont devenues une ressource limitée. Les blocs d’adresses privées définis par la RFC 1918 peuvent être utilisés dans les réseaux internes sans être annoncés sur l’Internet public. Ils ne sont cependant pas directement routables sur Internet : lorsqu’un poste privé doit joindre un serveur public, un routeur ou un pare-feu de bordure peut traduire l’adresse source privée en une adresse utilisable sur le réseau extérieur.

Le terme PAT (*Port Address Translation*) désigne une forme de traduction dans laquelle l’équipement utilise aussi les identifiants de transport, notamment les ports TCP ou UDP, pour distinguer plusieurs communications. Sur les équipements Cisco, cette technique est souvent appelée *NAT overload*. Elle permet à de nombreux hôtes internes de partager la même adresse IPv4 publique, car chaque flux est associé à une entrée de traduction distincte. Le NAT classique peut également fonctionner sans ports partagés, par exemple avec une correspondance statique un-pour-un.

NAT et PAT ne remplacent pas le routage, le filtrage de sécurité ou la segmentation du réseau. La traduction ne détermine pas à elle seule si un paquet a le droit de traverser un pare-feu : le routage choisit le chemin, les règles de filtrage autorisent ou refusent le trafic, et le mécanisme NAT transforme les champs pertinents puis conserve l’état nécessaire au traitement des réponses. Pour administrer correctement cette fonction, il faut comprendre les adresses avant et après traduction, le sens du trafic, la table de traduction et les commandes de vérification.

> **Analogie** : Imagine une grande entreprise dans laquelle chaque employé possède un numéro de poste interne, mais où le standard téléphonique utilise un seul numéro public. Lorsqu’un employé appelle une personne extérieure, le standard présente le numéro public de l’entreprise et conserve une fiche indiquant quel poste interne a lancé l’appel. Quand la réponse arrive au numéro public, le standard consulte sa fiche et la transmet au bon employé. PAT fonctionne de manière comparable : plusieurs machines internes peuvent partager une adresse publique, tandis que des ports différents permettent au routeur de distinguer les conversations.
>
> Une autre situation est celle d’un service qui doit être joignable depuis l’extérieur. L’entreprise peut décider qu’un numéro public précis correspond toujours au même poste interne. Cette correspondance permanente ressemble au NAT statique. Le mécanisme ne signifie pas que tous les postes internes sont publiquement accessibles : seuls les mappings et les règles de filtrage configurés déterminent les communications permises. Le standard doit aussi savoir si la ligne est destinée à un appel sortant ou à une communication entrante, tout comme un routeur NAT doit connaître le sens « inside » et « outside » des interfaces.


## 1. La théorie et les algorithmes

### 1.1. Pourquoi utiliser NAT ?

Dans IPv4, une adresse identifie une interface dans un contexte réseau. Les réseaux privés utilisent souvent des plages qui ne sont pas annoncées dans la table de routage globale d’Internet. Les plages privées classiques de la RFC 1918 sont :

| Bloc privé | Préfixe | Taille | Exemple d’utilisation |
|---|---:|---:|---|
| `10.0.0.0` à `10.255.255.255` | `10.0.0.0/8` | Très grande plage privée | Réseaux d’entreprise ou campus |
| `172.16.0.0` à `172.31.255.255` | `172.16.0.0/12` | Plage privée intermédiaire | Réseaux de sites ou de services |
| `192.168.0.0` à `192.168.255.255` | `192.168.0.0/16` | Plage privée courante | Réseaux domestiques et petits bureaux |

Une machine `192.168.10.25/24` peut communiquer directement avec une autre machine du même sous-réseau, si la couche 2 et les règles locales le permettent. Pour joindre une adresse publique, elle envoie généralement le paquet vers sa passerelle par défaut. Si cette passerelle exécute le NAT, elle peut remplacer l’adresse source `192.168.10.25` par l’adresse publique de sortie.

Les raisons principales d’utiliser NAT sont :

1. **Économiser les adresses IPv4 publiques.** Plusieurs hôtes privés peuvent partager une adresse publique par PAT.
2. **Masquer l’adressage interne dans les communications sortantes.** L’extérieur voit l’adresse traduite plutôt que l’adresse source privée d’origine.
3. **Permettre l’interconnexion de certains espaces d’adressage qui se chevauchent.** Une traduction soigneusement conçue peut résoudre certains conflits d’adresses entre réseaux, même si d’autres architectures, telles que le renumérotage ou la VRF, peuvent être préférables.
4. **Publier un service interne.** Une traduction statique ou une traduction de port peut associer une adresse publique et un port à un serveur privé, à condition que le routage et le filtrage permettent le trafic.

NAT n’est pas une solution universelle à la pénurie d’adresses. IPv6 offre un espace d’adressage bien plus grand et permet normalement de fournir des adresses globales aux équipements. Le NAT IPv4 reste toutefois très répandu dans les réseaux existants et chez les fournisseurs d’accès. Il faut également se rappeler que NAT apporte une transformation d’adresses, pas une garantie de confidentialité ou de sécurité complète.

### 1.2. NAT et PAT : différence fondamentale

Le NAT peut traduire une adresse sans modifier un port de transport. PAT utilise aussi une information de couche transport, comme un port TCP/UDP, ou un identifiant associé à certains messages ICMP, pour distinguer différentes sessions.

| Fonction | Ce qui est traduit | Usage type | Capacité de partage |
|---|---|---|---|
| NAT statique un-pour-un | Une adresse IP locale correspond à une adresse globale fixe | Serveur ou équipement devant conserver une correspondance stable | Une adresse globale pour une adresse locale |
| NAT dynamique avec pool | Une adresse locale est associée temporairement à une adresse d’un pool global | Accès sortant avec un ensemble d’adresses publiques | Limité par la disponibilité des adresses du pool, sauf surcharge |
| PAT / NAT overload | Adresse IP et identifiant de transport, notamment le port | Accès Internet de nombreux postes | Plusieurs flux et hôtes peuvent partager une adresse globale |
| PAT statique | Adresse et port de destination associés à un serveur interne | Publication d’un service précis | Plusieurs services peuvent partager une adresse globale s’ils utilisent des ports distincts |

Le PAT n’alloue pas simplement « un port unique par ordinateur ». Il crée des correspondances pour les flux et choisit des identifiants utilisables afin d’éviter les collisions de sessions. Une même machine peut avoir plusieurs connexions simultanées, chacune avec ses propres informations de transport. Plusieurs machines peuvent utiliser des ports locaux identiques sans créer de conflit si le traducteur leur attribue des associations externes distinctes.

### 1.3. Les termes « inside » et « outside »

Dans la terminologie Cisco classique, les interfaces du routeur NAT sont généralement identifiées comme *inside* ou *outside*. « Inside » désigne le côté du réseau interne du point de vue de la configuration NAT, et « outside » désigne le côté externe. Ce sont des rôles dans le mécanisme de traduction, pas des états de sécurité en eux-mêmes.

Il faut aussi distinguer les quatre termes fréquemment employés dans la documentation de NAT :

| Terme | Signification simple | Exemple |
|---|---|---|
| **Inside local** | Adresse d’un hôte interne telle qu’elle est utilisée dans le réseau interne | `192.168.10.25` |
| **Inside global** | Adresse qui représente cet hôte interne du côté extérieur | `203.0.113.10` |
| **Outside global** | Adresse de l’hôte extérieur telle qu’elle est connue sur le réseau extérieur | `198.51.100.20` |
| **Outside local** | Adresse de l’hôte extérieur telle qu’elle est représentée du côté interne, si elle est traduite | Souvent identique à l’outside global dans les configurations simples |

Les adresses `203.0.113.0/24` et `198.51.100.0/24` sont des plages de documentation ; elles sont utilisées ici pour les exemples et ne doivent pas être considérées comme des adresses publiques d’entreprise à déployer sur Internet.

Dans l’exemple classique de PAT sortant, la source du paquet est traduite de `192.168.10.25` vers `203.0.113.10`. L’adresse de destination du serveur public n’est généralement pas modifiée. Dans une configuration plus avancée, NAT peut aussi traduire les destinations et les adresses du côté outside ; le présent cours se concentre sur les situations les plus courantes pour débutants.

### 1.4. Que contient un paquet IPv4 ?

Un paquet IPv4 transporte notamment une adresse source et une adresse de destination. Lorsqu’un routeur effectue une traduction de source, il modifie l’adresse source et met à jour les informations de contrôle nécessaires à la validité du paquet. Pour TCP ou UDP, une traduction PAT peut aussi modifier le port source. Les sommes de contrôle qui dépendent des champs modifiés doivent être recalculées ou ajustées.

Exemple avant traduction :

```text
IPv4 source      : 192.168.10.25
Port source TCP  : 51514
IPv4 destination : 198.51.100.20
Port destination : 443
Protocole        : TCP
```

Exemple après PAT :

```text
IPv4 source      : 203.0.113.10
Port source TCP  : 40001
IPv4 destination : 198.51.100.20
Port destination : 443
Protocole        : TCP
```

Le routeur conserve une association entre les informations internes et les informations externes. Lorsque la réponse arrive à `203.0.113.10:40001`, il utilise cette association pour retrouver la destination interne `192.168.10.25:51514` et réécrire le paquet dans le sens retour.

L’exemple illustre le principe, pas une attribution de port garantie. Le numéro choisi par le routeur dépend de son implémentation, des sessions actives et des contraintes protocolaires. Les ports disponibles sont une ressource limitée et une table PAT est un état opérationnel qui peut contenir de nombreuses entrées.

### 1.5. Étapes d’une traduction PAT sortante

Considérons un PC `192.168.10.25` qui ouvre une session HTTPS vers un serveur public `198.51.100.20`, port TCP 443. La passerelle NAT possède l’adresse publique `203.0.113.10` sur son interface extérieure.

Le processus général est le suivant :

1. Le PC produit un paquet avec `192.168.10.25` comme source et `198.51.100.20` comme destination.
2. Comme la destination n’est pas dans son réseau local, le PC transmet le paquet à sa passerelle par défaut.
3. Le routeur reçoit le paquet sur une interface configurée comme `ip nat inside`.
4. Les règles NAT déterminent si le trafic correspond au critère de traduction, généralement défini par une ACL ou une autre politique.
5. PAT choisit une association externe disponible. L’adresse source privée est remplacée par une adresse globale et le port source peut être modifié.
6. Le routeur ajuste les sommes de contrôle appropriées et transmet le paquet après sa recherche de routage.
7. Le serveur répond à l’adresse et au port externes observés.
8. Le routeur consulte sa table de traduction, restaure les informations internes, puis transmet le paquet au PC.

Le NAT ne crée pas à lui seul une route vers Internet. Si aucune route par défaut ne permet de rejoindre le fournisseur d’accès, une traduction correcte ne suffit pas. De même, si le côté extérieur est mal défini, ou si l’ACL de traduction ne correspond pas à la source, le paquet peut ne pas être traduit.

```text
                 RÉSEAU PRIVÉ                      RÉSEAU PUBLIC

    PC                                          Serveur HTTPS
192.168.10.25                                  198.51.100.20:443
       |                                                ^
       | paquet source privée                          |
       v                                                |
+------------------+       PAT       +------------------+
| LAN / inside     |-----------------| outside / WAN    |
| 192.168.10.1     |                  | 203.0.113.10     |
|                  | table NAT :     |                  |
|                  | 192.168.10.25   |                  |
|                  | :51514           |                  |
|                  | -> 203.0.113.10  |                  |
|                  | :40001           |                  |
+------------------+                  +------------------+
       ^                                                |
       | paquet de réponse traduit                      |
       +------------------------------------------------+

    Le routeur conserve l'association pour traduire le trafic retour.
```

### 1.6. NAT statique

Le NAT statique établit une correspondance fixe entre une adresse locale et une adresse globale. Cette correspondance reste configurée même lorsque aucun trafic n’est échangé. Elle est utile quand une ressource interne doit être représentée par une adresse extérieure stable.

Exemple conceptuel :

```text
Adresse interne (inside local)  : 192.168.10.50
Adresse externe (inside global) : 203.0.113.50

Correspondance permanente :
192.168.10.50 <-> 203.0.113.50
```

Le NAT statique peut être utilisé pour un serveur qui doit être accessible par une adresse publique stable. Cependant, la traduction seule n’autorise pas automatiquement toutes les connexions entrantes : les ACL, pare-feu, routes et politiques de sécurité doivent également permettre les flux nécessaires. L’ouverture vers Internet d’une machine interne peut augmenter sa surface d’exposition et doit être planifiée.

Un mapping NAT statique un-pour-un s’écrit couramment sur Cisco IOS classique sous la forme :

```cisco
ip nat inside source static 192.168.10.50 203.0.113.50
```

La commande relie l’adresse inside local à son adresse inside global. Il faut ensuite configurer les interfaces inside/outside et vérifier que le réseau extérieur sait acheminer le préfixe contenant l’adresse publique. Selon la topologie, l’adresse traduite peut être portée par le routeur ou provenir d’un bloc routé par le fournisseur.

### 1.7. NAT dynamique avec un pool

Le NAT dynamique utilise un pool d’adresses globales. Une ACL définit généralement quelles sources sont candidates à la traduction, puis le routeur associe une adresse disponible du pool aux hôtes ou flux admissibles. Contrairement à un mapping statique, l’association n’est pas nécessairement permanente : elle est créée quand le trafic correspondant se présente et peut expirer après une période d’inactivité.

Supposons que le fournisseur fournisse quatre adresses publiques utilisables. L’administrateur peut les placer dans un pool NAT. Quand un utilisateur démarre une communication, le routeur attribue une adresse du pool selon les règles de son implémentation. Si le nombre d’utilisateurs simultanés dépasse le nombre d’adresses disponibles et qu’aucune surcharge n’est utilisée, certaines traductions peuvent échouer faute d’adresse disponible.

La logique générale est :

1. identifier les sources autorisées à être traduites ;
2. associer la règle à un pool global ;
3. marquer les interfaces inside/outside ;
4. assurer la présence des routes nécessaires ;
5. vérifier la création et l’expiration des mappings.

La configuration complète d’un pool est présentée plus loin dans la pratique. Un pool doit être composé d’adresses réellement attribuées à l’organisation et correctement acheminées ; il ne faut jamais choisir des adresses au hasard en supposant qu’elles seront joignables sur Internet.

### 1.8. PAT ou NAT overload

PAT, appelé aussi *NAT overload* dans plusieurs commandes Cisco, permet à de nombreux hôtes internes d’utiliser la même adresse IPv4 globale, en différenciant les flux par des informations de transport. Lorsqu’il traduit du trafic TCP ou UDP, le routeur prend généralement en compte les adresses et ports source/destination ainsi que le protocole pour associer la réponse à la bonne session.

Exemple :

| Hôte interne | Port source interne | Adresse/port externe attribués |
|---|---:|---|
| `192.168.10.25` | TCP 51514 | `203.0.113.10:40001` |
| `192.168.10.26` | TCP 51514 | `203.0.113.10:40002` |
| `192.168.10.25` | UDP 53000 | `203.0.113.10:40003` |

Les valeurs externes sont illustratives. Le routeur choisit des tuples utilisables sans conflit dans la table de traduction. Même si deux postes utilisent le même port local, ils peuvent communiquer via la même adresse publique grâce à des ports externes différents.

Sur Cisco IOS, une configuration très courante utilise l’adresse IP de l’interface outside avec `overload` :

```cisco
ip nat inside source list NAT-LAN interface GigabitEthernet0/1 overload
```

Cette instruction demande de traduire les sources correspondant à l’ACL `NAT-LAN` en utilisant l’adresse de l’interface `GigabitEthernet0/1`, avec partage par surcharge. La commande ne remplace pas la configuration des interfaces, le routage ni la liste d’accès.

### 1.9. NAT statique de port (PAT statique)

Un serveur interne peut être publié via une adresse globale et un port précis sans exposer l’ensemble de ses ports. C’est le principe du PAT statique. Par exemple, le TCP port 443 d’une adresse publique peut être associé au port 443 d’un serveur HTTPS interne.

Exemple de mapping :

```text
203.0.113.50:443  ->  192.168.10.50:443
```

Sur certaines versions de Cisco IOS, la syntaxe courante est :

```cisco
ip nat inside source static tcp 192.168.10.50 443 203.0.113.50 443
```

La disponibilité exacte et les détails de configuration peuvent varier suivant la plateforme et la version logicielle. La commande crée le mapping d’adresse et de port ; une ACL de filtrage ou une politique de pare-feu reste nécessaire pour contrôler le trafic entrant selon les besoins de sécurité.

Il est possible de publier différents services sur la même adresse globale en utilisant des ports externes distincts. Cela ne signifie pas que publier un port rend le serveur sûr. Les applications exposées doivent être mises à jour, protégées par authentification, journalisées et limitées au strict nécessaire.

### 1.10. Le rôle de l’ACL de traduction

Dans plusieurs configurations Cisco, une ACL standard sert à sélectionner les adresses sources qui doivent être traduites. Il est important de comprendre la différence entre une ACL utilisée pour choisir les sources NAT et une ACL de filtrage utilisée pour autoriser ou bloquer le trafic.

Exemple :

```cisco
ip access-list standard NAT-LAN
 permit 192.168.10.0 0.0.0.255
```

Cette ACL sélectionne les adresses du réseau `192.168.10.0/24` comme candidates à la traduction lorsqu’elle est référencée par une règle NAT. Dans cet usage, l’ACL n’est pas, à elle seule, un pare-feu qui interdit toute autre communication. Le routage peut continuer à acheminer des paquets dont la source ne correspond pas ; ils ne seront simplement pas traduits par cette règle précise.

La confusion entre « correspond à l’ACL NAT » et « est autorisé par le pare-feu » est une erreur fréquente. Dans un environnement sécurisé, il faut définir séparément les politiques de traduction et les politiques de filtrage, sauf si l’équipement et la conception intègrent explicitement ces fonctions dans une même politique.

### 1.11. Sommes de contrôle et champs concernés

Modifier une adresse IP dans un paquet affecte la somme de contrôle de l’en-tête IPv4. Si le NAT modifie un port TCP ou UDP, la somme de contrôle de transport dépendant de l’adresse pseudo-en-tête et des informations de transport doit également être ajustée. Certains protocoles incorporent des adresses IP dans leur charge utile, ce qui peut nécessiter un traitement spécifique par un mécanisme d’aide applicative (*ALG*) si le protocole et l’implémentation le prennent en charge.

Cette complexité explique pourquoi certains protocoles plus anciens ou certaines applications qui encodent des adresses dans leurs données peuvent avoir des difficultés derrière NAT sans mécanisme adapté. Les protocoles modernes préfèrent souvent des mécanismes de traversée compatibles avec les politiques réseau, mais le support varie selon les applications et les équipements.

Il ne faut pas supposer que NAT modifie toutes les adresses et tous les ports de chaque paquet. La traduction applique les règles pertinentes au flux sélectionné. Les champs qui ne nécessitent pas de modification restent inchangés, tandis que les informations de contrôle qui dépendent des champs modifiés sont ajustées par l’implémentation.

### 1.12. NAT et routage

Le routeur réalise une recherche de routage pour déterminer où transmettre le paquet. NAT transforme certaines informations d’adresse ; le routage choisit le chemin selon la table applicable à l’étape de traitement concernée. L’ordre exact de certaines opérations peut dépendre de la plateforme et du type de NAT, mais le principe pédagogique reste simple : il faut à la fois une traduction correcte et une route valide.

Pour du PAT sortant, une configuration typique requiert :

- une adresse et un masque corrects côté LAN ;
- une passerelle par défaut correcte sur les clients ;
- une interface inside sur le côté LAN ;
- une interface outside vers le fournisseur ;
- une règle NAT/PAT qui sélectionne le réseau interne ;
- une route par défaut ou une route adéquate vers l’extérieur ;
- le filtrage approprié pour le trafic souhaité ;
- un chemin retour fonctionnel du point de vue du réseau public.

Une règle NAT peut être parfaitement écrite mais ne pas servir si aucune route ne conduit au réseau extérieur. Inversement, le routage peut être correct mais les paquets sortir avec des adresses privées, que les routeurs Internet ne savent généralement pas acheminer vers les réseaux privés de l’entreprise.

### 1.13. NAT n’est pas un pare-feu

Le NAT est parfois décrit comme une protection parce que les connexions sortantes créent des entrées de traduction et que les paquets de réponse correspondants peuvent revenir, tandis qu’un paquet entrant inattendu ne possède pas nécessairement d’association vers un hôte interne. Cependant, cette observation ne permet pas de considérer NAT comme une politique complète de sécurité.

Un mapping statique peut explicitement fournir une correspondance vers une machine interne. Certaines translations, certaines plateformes ou certains états de flux peuvent également permettre des communications non prévues si la configuration est trop permissive. Un routeur doté de NAT peut avoir besoin d’ACL ou d’un pare-feu à états pour appliquer les politiques voulues.

La sécurité doit donc être conçue à partir des besoins d’accès, des services exposés, des zones de confiance et des règles de filtrage. Il faut documenter les flux autorisés, journaliser les événements pertinents et minimiser le nombre de services publiés. Une adresse interne masquée par NAT n’est pas une garantie contre les vulnérabilités d’application ou les menaces venant d’un flux autorisé.

### 1.14. NAT et IPv6

Le NAT traditionnel est surtout associé à IPv4. IPv6 possède un espace d’adressage considérablement plus vaste et a été conçu pour permettre l’attribution d’adresses globalement routables sans devoir traduire systématiquement les adresses de chaque hôte.

Des mécanismes de traduction IPv6/IPv4 existent pour certains besoins d’interconnexion, mais ils ont des propriétés et des cas d’usage distincts du PAT IPv4 classique. Ils ne doivent pas être confondus avec un simple `ip nat inside source ... overload` d’IOS IPv4.

Dans une architecture double pile, IPv4 et IPv6 peuvent suivre des chemins très différents : le trafic IPv4 peut traverser un PAT, tandis que le trafic IPv6 peut être routé directement avec des règles de filtrage adaptées. Il faut tester et protéger les deux familles d’adresses séparément. L’existence d’un NAT IPv4 ne protège pas automatiquement le chemin IPv6.

### 1.15. Limites et effets secondaires de NAT

NAT est utile, mais sa présence peut compliquer certains mécanismes de réseau :

- **Connexions entrantes** : une session nouvelle initiée depuis l’extérieur nécessite généralement un mapping statique, un PAT statique ou une autre forme de publication contrôlée.
- **Protocoles qui transportent des adresses dans la charge utile** : certains peuvent demander un traitement spécifique.
- **Traçabilité** : plusieurs utilisateurs peuvent partager une adresse globale ; les journaux doivent inclure des informations suffisantes sur les ports et les horodatages pour corréler les flux.
- **Applications pair-à-pair ou temps réel** : elles peuvent avoir besoin de mécanismes de traversée du NAT et ne fonctionnent pas toujours avec toutes les politiques.
- **Dépannage** : les adresses observées côté interne et côté extérieur ne sont pas les mêmes ; il faut capturer les paquets des deux côtés lorsque c’est nécessaire.
- **Redondance** : le basculement entre routeurs peut interrompre des sessions si l’état NAT/PAT n’est pas synchronisé ou rétabli selon la solution utilisée.

Il faut planifier les effets secondaires plutôt que de traiter NAT comme une simple commande. La conception doit tenir compte du nombre de sessions, des besoins de journalisation, de la disponibilité et des services publiés.

> **Piège :** Une traduction NAT n’ouvre pas automatiquement un service vers Internet et ne remplace pas une route. À l’inverse, une route par défaut fonctionnelle ne garantit pas que les sources privées seront traduites. Lorsqu’un client ne parvient pas à accéder à Internet, il faut contrôler séparément la connectivité IP, la route, la correspondance de l’ACL NAT, l’entrée dans la table de traduction et les politiques de filtrage. Ne confonds pas non plus l’ACL qui sélectionne les sources à traduire avec une ACL de sécurité qui autorise ou refuse les paquets.

```text
       CLIENT PRIVÉ               ROUTEUR NAT                    INTERNET

    192.168.10.25             +-------------------+          198.51.100.20
          |                   | G0/0: 192.168.10.1|                 |
          +------------------>| ip nat inside     |                 |
                              |                   |                 |
                              | Table PAT         |                 |
                              | 192.168.10.25:51514                 |
                              | -> 203.0.113.10:40001                |
                              |                   |                 |
                              | G0/1: 203.0.113.10|---------------->|:443
                              | ip nat outside    |                 |
                              +-------------------+                 |
          <------------------- paquet de réponse traduit <----------+

    Les informations de traduction sont nécessaires pour retrouver
    le client interne à partir du flux de retour.
```


## 2. Configuration et Pratique

### 2.1. Topologie du laboratoire

Le laboratoire utilise un routeur Cisco IOS classique qui relie un LAN privé à un réseau amont. Les noms d’interfaces peuvent varier selon le matériel ou le simulateur, par exemple Packet Tracer, CML ou une plateforme IOS XE. Adapter les interfaces avant de coller la configuration.

| Équipement / interface | Adresse | Rôle |
|---|---|---|
| PC-LAN | `192.168.10.25/24` | Poste utilisateur |
| R1 G0/0 | `192.168.10.1/24` | Passerelle du LAN, interface inside |
| R1 G0/1 | `203.0.113.10/24` | Exemple d’interface outside |
| Routeur amont | `203.0.113.1` | Prochain saut par défaut |
| Serveur de test | `198.51.100.20` | Destination de documentation |

Les préfixes `203.0.113.0/24` et `198.51.100.0/24` sont réservés à la documentation. Ils illustrent les commandes mais ne doivent pas être utilisés comme véritables adresses publiques sur Internet. Dans un laboratoire isolé, ils conviennent à un scénario de démonstration si tous les équipements sont configurés de manière cohérente. En production, utiliser les adresses réellement assignées par le fournisseur ou l’équipe IP.

```text
                         WAN / AMONT
                     Routeur 203.0.113.1
                              |
                              | réseau de transit
                              |
                     G0/1 203.0.113.10
                       +-------------+
                       |     R1      |
                       | NAT / PAT   |
                       +-------------+
                     G0/0 192.168.10.1
                              |
                         VLAN / LAN
                              |
                       PC 192.168.10.25
```

### 2.2. Préparer les interfaces

Commence par configurer les interfaces. Sur R1 :

```cisco
hostname R1-NAT
!
interface GigabitEthernet0/0
 description LAN_INTERNE
 ip address 192.168.10.1 255.255.255.0
 ip nat inside
 no shutdown
!
interface GigabitEthernet0/1
 description VERS_ROUTEUR_AMONT
 ip address 203.0.113.10 255.255.255.0
 ip nat outside
 no shutdown
!
ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

La commande `ip nat inside` marque l’interface reliée au réseau interne. La commande `ip nat outside` marque l’interface reliée au réseau extérieur. Le routeur utilise ces rôles pour appliquer les règles de traduction prévues.

La route statique par défaut indique où envoyer les paquets pour lesquels aucune route plus spécifique n’est disponible. Dans un véritable réseau, le prochain saut doit correspondre à la configuration du lien WAN et être joignable. Dans cet exemple de documentation, l’adressage est volontairement simplifié.

Vérifie les interfaces avant de poursuivre :

```cisco
show ip interface brief
show interfaces GigabitEthernet0/0
show interfaces GigabitEthernet0/1
show ip route
```

Si une interface est arrêtée ou si une adresse est incorrecte, il faut corriger ce problème avant de diagnostiquer NAT. Un état `up/up` est un bon point de départ, mais il ne prouve pas que le chemin vers le serveur distant fonctionne de bout en bout.

### 2.3. Configurer PAT avec l’adresse de l’interface WAN

C’est le cas le plus fréquent dans un petit bureau : toutes les sources du LAN doivent partager l’adresse IPv4 de l’interface WAN pour l’accès sortant.

```cisco
ip access-list standard NAT-LAN
 permit 192.168.10.0 0.0.0.255
!
ip nat inside source list NAT-LAN interface GigabitEthernet0/1 overload
```

La première partie crée une ACL standard nommée `NAT-LAN`. Elle sélectionne les sources du réseau `192.168.10.0/24`. La deuxième commande active la traduction d’adresse source en utilisant l’adresse de `GigabitEthernet0/1`, avec `overload` pour permettre le partage via PAT.

L’ACL choisit les adresses à traduire ; elle n’est pas, dans cette utilisation, une politique de filtrage complète. Il faut configurer séparément les ACL de sécurité ou les politiques de pare-feu qui déterminent le trafic autorisé.

Après activation, un poste interne doit posséder une adresse correcte, le masque `/24`, et la passerelle `192.168.10.1`. Il doit aussi pouvoir acheminer le trafic vers cette passerelle. Le routeur doit posséder une route vers l’amont et une connectivité valide sur son interface outside.

### 2.4. Vérifier PAT

Depuis un poste interne, génère du trafic vers un serveur ou une cible du laboratoire. Puis exécute sur R1 :

```cisco
show ip nat translations
show ip nat translations verbose
show ip nat statistics
```

La table de traduction doit présenter des associations créées par les sessions. Selon le protocole et la plateforme, l’affichage peut contenir les adresses locales et globales, les ports ou identifiants de transport et les informations relatives aux correspondances. La sortie ne sera pas nécessairement identique dans toutes les versions de Cisco IOS ou IOS XE.

`show ip nat statistics` aide à vérifier que le mécanisme NAT est actif, que les interfaces sont reconnues dans leurs rôles et que des statistiques de traduction sont enregistrées.

Si aucune entrée n’apparaît, vérifie d’abord que le trafic traverse effectivement le routeur, que les interfaces sont marquées inside/outside, que la source correspond à l’ACL et que le flux tente réellement de sortir. Ne commence pas par augmenter arbitrairement les temporisations ou effacer les tables.

### 2.5. Configurer le NAT dynamique avec pool

Supposons que le laboratoire dispose d’un bloc global de démonstration `203.0.113.20` à `203.0.113.29`. Dans un environnement réel, ces adresses devraient faire partie du bloc assigné et être correctement acheminées vers le routeur NAT.

```cisco
ip nat pool POOL-PUBLIC 203.0.113.20 203.0.113.29 netmask 255.255.255.0
!
ip access-list standard NAT-LAN
 permit 192.168.10.0 0.0.0.255
!
ip nat inside source list NAT-LAN pool POOL-PUBLIC
```

Le pool fournit un ensemble d’adresses globales possibles. La règle associe les sources sélectionnées par l’ACL au pool. Sans `overload`, le nombre de translations simultanées dépend de la disponibilité des adresses et du comportement de l’implémentation. Si le pool est épuisé, de nouvelles connexions qui nécessitent une nouvelle adresse peuvent ne pas être traduites.

Pour partager les adresses du pool à l’aide de PAT, la commande peut inclure `overload` lorsque la plateforme le prend en charge :

```cisco
ip nat inside source list NAT-LAN pool POOL-PUBLIC overload
```

La configuration de pool réelle doit être validée selon la plateforme et la topologie. Il faut aussi éviter les adresses déjà utilisées par des interfaces, des serveurs ou d’autres équipements. Un pool mal planifié peut causer des conflits et des problèmes d’acheminement.

### 2.6. Configurer un NAT statique un-pour-un

Un serveur interne peut être associé en permanence à une adresse globale. Exemple de documentation :

```cisco
ip nat inside source static 192.168.10.50 203.0.113.50
```

Cette commande définit un mapping statique entre l’adresse interne `192.168.10.50` et l’adresse globale `203.0.113.50`. Il faut vérifier que l’adresse globale est disponible, routée vers le routeur NAT et compatible avec le plan d’adressage extérieur.

Une correspondance statique ne rend pas automatiquement tous les services du serveur accessibles. Un filtrage approprié reste nécessaire. Pour un service exposé, il est préférable de n’autoriser que le protocole et les ports indispensables, de surveiller les journaux et de maintenir l’application à jour.

Cette fonction est différente du PAT de sortie partagé. Dans le mapping statique un-pour-un, une adresse globale est liée en permanence à une adresse interne ; dans PAT, des associations de flux permettent à plusieurs hôtes de partager une adresse externe.

### 2.7. Publier un port avec PAT statique

Pour exposer uniquement un service HTTPS interne, une entrée PAT statique peut être utilisée si elle est prise en charge par la version IOS concernée :

```cisco
ip nat inside source static tcp 192.168.10.50 443 203.0.113.50 443
```

La commande associe le port TCP 443 de l’adresse globale `203.0.113.50` au port TCP 443 du serveur interne `192.168.10.50`. Le trafic doit toujours pouvoir atteindre le routeur par le chemin extérieur, puis être acheminé vers le serveur après la traduction. Les règles de pare-feu doivent limiter l’accès à ce service selon la politique de sécurité.

La publication d’un port est une décision d’exposition. Avant de l’activer, confirmer que le service est attendu, qu’il utilise le bon port, qu’il est protégé par une authentification robuste et qu’il ne permet pas d’accéder latéralement à d’autres ressources internes.

### 2.8. Sauvegarder et documenter

Avant de modifier une configuration NAT en production, sauvegarde l’état existant, note les adresses privées et publiques, l’usage de chaque mapping, les ACL associées et la route de sortie. Les entrées dynamiques peuvent disparaître lorsque les sessions expirent ou que le routeur est rechargé ; les mappings statiques et les commandes de configuration doivent rester documentés.

Après un changement, vérifie :

1. la configuration active ;
2. l’état des interfaces inside/outside ;
3. la route par défaut ou les routes vers l’amont ;
4. l’existence de la règle de sélection NAT ;
5. la création de traductions lors d’un trafic de test ;
6. le trajet de retour ;
7. les journaux de sécurité et les règles de filtrage ;
8. les effets sur les sessions déjà établies.

Évite les opérations d’effacement de toute la table NAT comme première réaction à un incident. Elles peuvent interrompre des sessions utilisateur et masquer les indices utiles au diagnostic. Les entrées problématiques doivent être examinées et les actions de nettoyage limitées au besoin réel.


## 3. Dépannage et Sécurité

### 3.1. Méthode structurée de dépannage

Lorsqu’un hôte ne peut pas accéder à une ressource extérieure, commence par déterminer si le problème se situe avant, pendant ou après la traduction. Teste d’abord l’adresse de la passerelle interne. Vérifie ensuite la route de sortie depuis le routeur NAT, puis observe si un flux génère une entrée dans la table NAT.

Les commandes utiles comprennent :

```cisco
show ip interface brief
show ip route
show access-lists
show ip nat translations
show ip nat statistics
show running-config | section ip nat
```

Les dernières commandes disponibles varient selon la plateforme et la version logicielle. Si une syntaxe de filtrage de `show running-config` n’est pas supportée, consulte la configuration complète et repère les commandes NAT manuellement.

Une entrée de traduction présente indique que le routeur a traité le flux selon une règle NAT. Elle ne prouve pas que le serveur distant a répondu ou que le paquet de retour est parvenu jusqu’au client. Il faut aussi examiner les routes, le filtrage, le service distant et, si nécessaire, effectuer des captures sur les deux côtés du routeur.

### 3.2. Aucun mapping NAT n’apparaît

Causes fréquentes :

- Le trafic ne traverse pas le routeur NAT.
- Les interfaces ne sont pas correctement marquées `ip nat inside` et `ip nat outside`.
- L’adresse source ne correspond pas à l’ACL associée à la règle NAT.
- La règle NAT référence le mauvais pool ou la mauvaise interface.
- Le poste a une mauvaise passerelle ou une adresse IP erronée.
- Le flux n’a pas été généré pendant l’observation.

Vérifie l’adresse du client, sa passerelle, la route du routeur et la configuration NAT. Il est utile de générer un nouveau flux de test plutôt que de se baser sur une session très ancienne dont l’état pourrait avoir expiré.

### 3.3. La traduction existe, mais la connexion échoue

Quand la traduction existe, examine le parcours du paquet traduit. L’adresse externe doit être acheminée correctement et la destination doit répondre. Le paquet de retour doit atteindre l’interface outside du traducteur, puis correspondre à l’entrée NAT pertinente.

Les causes possibles comprennent :

- une route de retour absente ;
- un filtrage sur le routeur, le pare-feu ou le serveur ;
- une adresse globale non routée vers l’équipement NAT ;
- un mauvais mapping de port ;
- un service qui n’écoute pas sur le port attendu ;
- une incompatibilité du protocole avec le chemin NAT ;
- une session supprimée ou expirée ;
- un conflit avec une autre politique de traduction.

Effectuer une capture côté inside et une autre côté outside peut être utile. Comparer le même flux permet de voir où l’adresse source ou le port sont transformés et si les réponses reviennent. Les captures doivent être prises au bon endroit et interprétées avec l’ordre de traitement de la plateforme en tête.

### 3.4. L’ACL NAT ne correspond pas aux bonnes sources

Une ACL de traduction définit les sources qui peuvent être traduites par la règle qui la référence. Si le masque générique est incorrect, une partie des hôtes peut rester non traduite ou des adresses inattendues peuvent être sélectionnées.

Exemple correct pour `192.168.10.0/24` :

```cisco
ip access-list standard NAT-LAN
 permit 192.168.10.0 0.0.0.255
```

La wildcard `0.0.0.255` correspond au masque `/24`. Il faut vérifier que l’ACL est bien référencée par la commande `ip nat inside source ...`, puis observer ses compteurs lorsque des paquets de test la traversent.

Attention : une ACL NAT ne remplace pas les règles de sécurité. Si un flux ne correspond pas à la règle NAT, cela ne signifie pas nécessairement qu’il est bloqué ; il peut être routé tel quel, rejeté par une autre règle ou échouer ailleurs. Vérifie le filtrage séparément.

### 3.5. Le pool NAT est épuisé

Avec un NAT dynamique sans overload, chaque nouvel hôte qui a besoin d’une translation doit obtenir une adresse disponible du pool selon les règles de l’implémentation. Si le pool ne contient plus d’adresse libre, de nouvelles translations peuvent échouer jusqu’à la libération d’entrées ou à l’augmentation de capacité.

Il faut contrôler la taille du pool, le nombre de mappings actifs, les temporisations et le comportement réel attendu. Ne résous pas systématiquement le problème en ajoutant `overload` sans vérifier les exigences de l’architecture et les capacités de la plateforme.

PAT peut augmenter le nombre de flux pouvant partager une adresse, mais il reste limité par les ports disponibles, les ressources de traitement, les tables internes et les politiques de l’équipement. Il faut dimensionner la solution selon la charge réelle plutôt que supposer qu’une seule adresse peut supporter toute charge imaginable.

### 3.6. Accès entrant impossible

Une translation dynamique destinée au trafic sortant ne signifie pas qu’un hôte extérieur peut spontanément ouvrir une nouvelle session vers un poste interne. Pour publier un service, il faut généralement une correspondance statique appropriée et des règles de filtrage compatibles.

La démarche de dépannage doit vérifier :

1. l’adresse et le port publics ciblés ;
2. le mapping statique configuré ;
3. le routage vers l’adresse publique ;
4. les règles de filtrage sur le WAN et le LAN ;
5. le routage et la configuration IP du serveur interne ;
6. le service qui doit écouter sur le port ;
7. le trajet retour.

Une translation configurée vers un serveur ne garantit pas que l’application soit disponible. Il faut tester le service réel, non seulement la présence de la commande de mapping.

### 3.7. Chevauchement ou double NAT

Deux équipements NAT peuvent se trouver en série, notamment lorsqu’un routeur d’opérateur et un routeur domestique traduisent tous deux les adresses. Ce scénario est parfois appelé *double NAT*. Il peut fonctionner pour certains usages sortants, mais complique les connexions entrantes, les journaux, le dépannage et certaines applications.

Il faut identifier chaque frontière de traduction, les adresses utilisées de part et d’autre et l’équipement qui détient l’état de la session. Pour publier un service, il peut être nécessaire de configurer une correspondance sur chacun des traducteurs, ce qui augmente le risque d’erreur.

Lorsque possible, une architecture plus simple — un seul point de NAT clairement identifié et des routes correctement conçues — facilite l’exploitation. Le double NAT n’est pas automatiquement incorrect, mais il doit être intentionnel, documenté et testé.

### 3.8. NAT et protocoles applicatifs

Certains protocoles intègrent les adresses IP ou les ports dans leur charge utile. Une traduction qui modifie uniquement l’en-tête IP peut alors laisser une adresse ou un port incohérent dans le contenu applicatif. Historiquement, des mécanismes ALG ont été introduits pour aider certains protocoles, mais leur fonctionnement varie selon la plateforme et le protocole, et une inspection automatique peut aussi provoquer des effets secondaires.

Il faut tester les applications réellement utilisées derrière NAT. Les communications temps réel, certains protocoles multimédias ou certaines architectures pair-à-pair peuvent nécessiter des mécanismes explicites de traversée du NAT. Ne suppose pas qu’un NAT classique permet à toute application de fonctionner sans adaptation.

Les comportements dépendent également du type de NAT, de la présence d’un pare-feu à états et des politiques de filtrage. Les normes de comportement NAT, notamment pour UDP, sont abordées dans la RFC 4787, tandis que la RFC 3022 documente le NAT traditionnel. Ces documents sont utiles pour comprendre les limites, mais la capacité réelle doit être vérifiée sur le logiciel de l’équipement.

### 3.9. Journalisation et traçabilité

Avec PAT, plusieurs utilisateurs partagent la même adresse globale. Une adresse publique seule ne permet pas nécessairement d’identifier le flux interne d’origine. Une corrélation correcte peut nécessiter l’adresse et le port externes, le protocole, un horodatage précis et les journaux de traduction correspondants.

Une organisation doit définir quels événements sont conservés, combien de temps, comment l’horloge des équipements est synchronisée, qui peut consulter les journaux et comment ceux-ci sont protégés. Les exigences légales et de confidentialité varient selon le contexte ; les données de connexion doivent être traitées selon les politiques applicables.

Le volume de journaux peut devenir important. Il faut dimensionner la collecte, éviter que les messages essentiels ne soient perdus, surveiller les erreurs et préserver les éléments utiles à une enquête. Les journaux ne doivent pas être modifiables sans contrôle par les utilisateurs ordinaires.

### 3.10. Sécurité : pourquoi NAT n’est pas une défense suffisante

> **Danger :** NAT ne remplace jamais un pare-feu. Un mapping statique trop large, un PAT statique mal configuré ou une règle de filtrage permissive peut exposer un service interne. À l’inverse, une politique NAT mal comprise peut donner une fausse impression de protection alors qu’un service est accessible par un autre chemin, par IPv6 ou par une interface supplémentaire. Il faut définir explicitement les services autorisés, limiter les ports publiés, surveiller les flux et vérifier l’ensemble des chemins réseau.

Bonnes pratiques :

- Ne publier que les services strictement nécessaires.
- Limiter les sources autorisées quand c’est possible et cohérent avec le besoin métier.
- Utiliser un pare-feu à états ou des ACL adaptées au rôle de l’équipement.
- Sécuriser le routeur et ses accès d’administration.
- Tenir à jour les serveurs publiés et réduire leur surface d’attaque.
- Contrôler les tables de traduction et les journaux.
- Documenter les mappings statiques, leur propriétaire, le service et la justification.
- Vérifier les chemins IPv4 et IPv6 séparément.
- Tester les changements en laboratoire ou dans un périmètre contrôlé.

### 3.11. Commandes de diagnostic récapitulatives

| Commande Cisco IOS | Utilité principale |
|---|---|
| `show ip nat translations` | Affiche les translations actives et statiques connues |
| `show ip nat translations verbose` | Fournit davantage d’informations lorsqu’elles sont prises en charge |
| `show ip nat statistics` | Affiche les statistiques NAT et les interfaces déclarées |
| `show ip route` | Vérifie les routes et le prochain saut |
| `show ip interface brief` | Résume l’état des interfaces et leurs adresses |
| `show access-lists` | Vérifie les ACL et leurs compteurs |
| `show running-config` | Examine les règles NAT, les interfaces et les routes configurées |
| `show logging` | Recherche des événements récents du système |

Les commandes exactes et les informations de sortie peuvent varier selon la plateforme. Utilise des commandes compatibles avec la version installée et évite de lancer un débogage intensif sur un routeur de production sans plan de collecte et de retour arrière.

### 3.12. Procédure de diagnostic en étapes

Une procédure simple et reproductible aide à éviter les changements aléatoires.

**Étape 1 — Vérifier le client.** Confirme l’adresse, le masque et la passerelle. Teste la passerelle locale. Si le client ne joint pas son premier saut, NAT n’est probablement pas la première cause à traiter.

**Étape 2 — Vérifier le routeur.** Confirme que les interfaces sont opérationnelles, que l’interface LAN est inside et que l’interface WAN est outside. Vérifie la route vers l’extérieur et le retour nécessaire.

**Étape 3 — Contrôler la sélection NAT.** Examine l’ACL, le pool ou la règle overload. Vérifie que les sources attendues correspondent à la politique de traduction.

**Étape 4 — Générer du trafic.** Lance une nouvelle session vers une destination contrôlée. Une translation dynamique peut ne pas apparaître tant qu’aucun paquet correspondant n’a traversé le routeur.

**Étape 5 — Lire la table NAT.** Confirme que le mapping reflète les adresses et ports attendus. Une absence de mapping oriente l’analyse vers les rôles inside/outside, l’ACL, le chemin du paquet ou la règle NAT.

**Étape 6 — Vérifier le chemin retour.** Si le mapping existe, mais que le trafic échoue, examine le WAN, les ACL de sécurité, le serveur distant, la route de retour et les journaux.

**Étape 7 — Capturer si nécessaire.** Compare les paquets avant et après traduction. N’efface pas toute la table NAT avant d’avoir collecté les éléments utiles, car cela peut interrompre des sessions et faire disparaître un indice temporaire.

### 3.13. Astuces d’exploitation

> **Astuce :** Pendant le diagnostic, compare le même flux sur les deux côtés du routeur. Note le protocole, l’adresse source, le port source, l’adresse destination et le port destination. La différence entre la capture inside et la capture outside montre exactement quelle traduction a été appliquée. Associe ces observations à `show ip nat translations` et `show ip nat statistics` avant de modifier la configuration.

Une autre astuce consiste à conserver un schéma explicite du sens inside/outside. En cas de plusieurs interfaces WAN, de sous-interfaces VLAN ou de VRF, la simple lecture de l’adresse IP ne suffit pas toujours à connaître le rôle de l’interface. Les descriptions d’interface et la documentation du plan IP réduisent fortement les erreurs opérationnelles.

Pour une publication de service, documente le propriétaire applicatif, l’adresse interne, l’adresse publique, le protocole, le port interne, le port externe, les sources autorisées, la date de mise en production et le processus de retrait. Les mappings oubliés deviennent souvent des ouvertures de sécurité non surveillées.


## Points à retenir

- **NAT traduit certaines informations d’adressage IPv4 ; PAT différencie en plus les flux avec des identifiants de transport, comme les ports TCP/UDP.** NAT statique, NAT dynamique, PAT overload et PAT statique répondent à des besoins différents.
- **Une traduction correcte ne remplace ni le routage ni le filtrage.** Il faut des interfaces inside/outside cohérentes, une règle NAT qui sélectionne la bonne source, des routes valides et un chemin retour fonctionnel.
- **NAT n’est pas un pare-feu.** Tout service publié doit être protégé par des règles explicites, maintenu à jour et surveillé. Le dépannage doit examiner la table NAT, le routage, les ACL et les paquets avant et après traduction.


## Références techniques

- [RFC 3022 — Traditional IP Network Address Translator (Traditional NAT)](https://www.rfc-editor.org/rfc/rfc3022.html)
- [RFC 1918 — Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918.html)
- [RFC 4787 — Network Address Translation Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787.html)
- [Cisco — Configuring Static and Dynamic NAT Simultaneously](https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/13778-9.html)
- [Cisco — Troubleshoot Network Address Translation with Frequently Asked Questions](https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/218012-troubleshoot-network-address-translation.html)
