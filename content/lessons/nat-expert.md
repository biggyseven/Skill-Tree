---
node_id: nat-expert
title: NAT & PAT - Expert
---

# NAT & PAT - Expert

**Niveau :** Expert

La traduction d’adresses réseau, ou *Network Address Translation* (NAT), est une fonction de traitement des paquets qui modifie une ou plusieurs informations d’adressage IP pendant le transit d’un équipement. Dans sa forme IPv4 traditionnelle, elle permet notamment à des hôtes utilisant des adresses privées de communiquer avec des réseaux utilisant des adresses globalement routables. La traduction peut porter sur les adresses IP uniquement, ou également sur les identifiants de transport, par exemple les ports TCP et UDP. Cette dernière approche est généralement appelée PAT (*Port Address Translation*) ou NAPT (*Network Address and Port Translation*).

Le NAT s’est développé avec la généralisation des réseaux privés IPv4 et la limitation de l’espace d’adressage IPv4. Il répond à des contraintes opérationnelles réelles : partage d’une ou de plusieurs adresses publiques, publication de services internes, interconnexion de domaines d’adressage qui se chevauchent et transition entre certains environnements d’accès. Le NAT traditionnel est décrit dans la RFC 3022. Les comportements d’un NAT vis-à-vis de TCP, UDP et ICMP sont précisés par plusieurs documents de l’IETF, notamment les RFC 4787, 5382, 5508 et leur mise à jour RFC 7857.

À un niveau expert, NAT ne doit pas être traité comme une simple substitution de texte dans l’en-tête IP. Le traitement doit préserver la cohérence des en-têtes, des sommes de contrôle, des identifiants de flux et des états nécessaires au retour des paquets. La modification de l’adresse source ou destination influence aussi le routage, les ACL, les politiques de sécurité, les journaux, le diagnostic des applications et parfois les protocoles qui transportent des adresses à l’intérieur de leur charge utile. Le résultat dépend de l’ordre des opérations du routeur, de la direction du trafic, de la configuration des interfaces, de la méthode de traduction et des fonctionnalités de la plateforme.

NAT/PAT n’est pas un protocole de routage, une méthode de chiffrement ou, à lui seul, un pare-feu. Il ne garantit pas qu’un service soit protégé : une traduction statique peut rendre un service accessible depuis un réseau externe, et une translation dynamique ne remplace pas une politique de filtrage explicite. Une architecture robuste sépare les objectifs d’adressage, de routage, de filtrage, de journalisation, de disponibilité et de contrôle des applications.

> **Analogie** : Imagine un grand campus dont chaque bureau utilise un numéro interne, tandis que les visiteurs ne connaissent que l’adresse de l’accueil. La réception tient un registre qui associe les échanges entrants et sortants. Lorsque le bureau 12 appelle un fournisseur, la réception présente un numéro public et inscrit dans le registre que la réponse reçue pour ce numéro doit être remise au bureau 12. Si plusieurs bureaux utilisent le même numéro public, la réception doit aussi distinguer leurs appels par un identifiant de session, comparable au port TCP ou UDP. Pour publier un service, l’administrateur crée une règle explicite qui indique que les demandes visant un numéro public précis doivent être remises à un serveur interne précis. Le registre ne chiffre pas les conversations et ne décide pas si le fournisseur est digne de confiance : il fait correspondre les communications. Si le registre est perdu, si deux règles se contredisent ou si la réponse revient par un autre accueil qui ne possède pas l’état requis, les communications peuvent échouer même si les bureaux et les câbles fonctionnent.

---

## 1. La théorie et les algorithmes

### 1.1. Vocabulaire rigoureux du NAT

Les quatre termes classiques du NAT Cisco décrivent une adresse en fonction du point de vue du domaine NAT :

| Terme | Signification | Exemple |
|---|---|---|
| *Inside local* | Adresse de l’hôte interne telle qu’elle est connue dans le domaine intérieur | `10.10.10.25` |
| *Inside global* | Adresse représentant cet hôte dans le domaine extérieur | `203.0.113.25` |
| *Outside global* | Adresse réelle ou globalement visible de l’hôte extérieur | `198.51.100.80` |
| *Outside local* | Adresse de l’hôte extérieur telle qu’elle est représentée dans le domaine intérieur | Souvent identique à l’outside global, mais pas toujours |

Ces termes ne doivent pas être assimilés automatiquement à « privé » et « public ». Une adresse inside local est souvent privée RFC 1918, mais la distinction repose sur le rôle logique de l’adresse dans la traduction. L’outside local peut différer de l’outside global dans des scénarios de traduction bidirectionnelle, de chevauchement de réseaux ou d’architecture spécifique.

Il faut également distinguer plusieurs familles :

- **NAT statique** : association fixe entre une adresse locale et une adresse globale, ou entre une combinaison adresse/port locale et une combinaison globale.
- **NAT dynamique** : allocation d’une adresse globale depuis un pool pour une traduction qui dépend de l’activité et de la disponibilité des ressources.
- **PAT/NAPT** : traduction d’adresses accompagnée de la traduction d’un identifiant de transport, ce qui permet à plusieurs flux internes de partager une même adresse IPv4 globale.
- **NAT source** : modification de l’adresse source ; typique pour permettre aux réseaux internes de sortir vers l’extérieur.
- **NAT destination** : modification de l’adresse destination ; utilisée, entre autres, pour publier ou rediriger un service.
- **NAT hairpin/loopback** : un client intérieur accède à un service au moyen de son adresse extérieure publiée et le trafic retourne vers une destination située dans le même domaine intérieur.
- **NAT44, NAT64 et NPTv6** : mécanismes distincts ; NAT44 traduit IPv4 vers IPv4, NAT64 facilite certaines communications entre IPv6 et IPv4, tandis que NPTv6 traduit un préfixe IPv6 vers un autre selon un mécanisme différent. Ils ne sont pas interchangeables.

### 1.2. La traduction comme transformation d’état

Un équipement de traduction peut être sans état pour certains traitements très limités, mais le PAT courant utilise un état qui associe les flux intérieurs aux flux extérieurs. Cet état permet au dispositif d’identifier les paquets de retour et de restaurer les adresses et ports attendus.

Une entrée conceptuelle de translation peut être représentée par le tuple suivant :

```text
Protocole de transport
Adresse IP source intérieure
Port source intérieur (si présent)
Adresse IP destination
Port destination (si présent)
Adresse et port source traduits
Adresse et port destination traduits selon le type de NAT
État / temporisation / compteur d’activité
```

La structure exacte dépend de l’implémentation. Le dispositif peut stocker des valeurs supplémentaires, des informations de VRF, des identifiants de session ou des données nécessaires à la synchronisation de haute disponibilité. Un équipement PAT doit distinguer les flux qui utiliseraient sinon le même couple adresse/port global. Le protocole de transport, les ports, les adresses et les règles de filtrage participent à cette distinction.

Pour un flux TCP, l’état du NAT ne doit pas être confondu avec l’état TCP complet d’une pile terminale, même si de nombreux équipements observent les échanges TCP et utilisent des temporisations différentes selon l’état apparent de la session. Le NAT traduit les champs et suit les informations dont il a besoin ; le pare-feu stateful peut effectuer une inspection plus complète de l’établissement et de la terminaison des connexions.

### 1.3. Algorithme général de traitement d’un paquet

Le traitement logique d’un paquet à travers un NAT comprend généralement les étapes suivantes. Leur ordre exact dépend de la plateforme, de la direction du paquet et des fonctions activées.

1. **Réception** : l’interface reçoit la trame et le routeur vérifie son intégrité de couche 2.
2. **Décapsulation** : l’équipement identifie le paquet IP, son protocole, ses adresses et les champs pertinents.
3. **Classification** : il détermine la direction inside/outside, la VRF éventuelle, les politiques d’interface, les règles de NAT et les éventuelles politiques de routage.
4. **Recherche d’une traduction existante** : si une entrée compatible est déjà présente, elle peut être réutilisée.
5. **Création éventuelle d’un état** : pour un nouveau flux, l’équipement évalue les règles statiques ou dynamiques, les ACL ou route-maps, la disponibilité d’une adresse/port et les contraintes du protocole.
6. **Modification des champs** : il traduit l’adresse source, l’adresse destination, les ports ou d’autres identifiants concernés.
7. **Correction des sommes de contrôle** : les sommes de contrôle affectées doivent être recalculées ou ajustées de façon incrémentale.
8. **Recherche de transfert** : selon la direction et l’implémentation, la décision de routage précède ou suit certaines traductions.
9. **Filtrage et émission** : les politiques de sécurité, les règles de sortie, la résolution L2 et les contrôles de ressources déterminent si le paquet est transmis.
10. **Mise à jour de l’état et des compteurs** : le dispositif rafraîchit les temporisations et les compteurs, puis émet la trame vers le prochain saut.

Ce schéma est volontairement logique. Un routeur réel peut répartir ces opérations dans le chemin matériel, le moteur de transfert, les tables CEF, des accélérateurs ASIC et un plan de contrôle logiciel. L’ordre d’opérations publié pour Cisco IOS ne doit pas être supposé identique sur toutes les gammes, tous les systèmes et toutes les fonctions de routage avancé. En particulier, PBR, VRF, VPN, pare-feu intégré, NAT virtuel et redondance peuvent modifier les points de classification ou les contraintes de transfert.

### 1.4. Ordre des opérations : inside-to-outside et outside-to-inside

Sur Cisco IOS traditionnel, le principe fondamental est que la traduction n’intervient pas au même moment selon le sens du paquet. Pour de nombreux cas usuels :

- **Inside vers outside** : la décision de routage vers la destination externe est généralement prise à partir de la destination du paquet ; la traduction de source intervient ensuite dans le chemin de transfert approprié.
- **Outside vers inside** : la traduction de destination peut intervenir avant la recherche de route qui détermine comment atteindre l’adresse interne résultante.

L’effet pratique est essentiel. Une traduction de destination doit permettre au routeur de sélectionner une route vers l’adresse interne réelle du serveur. De même, une règle d’ACL peut évaluer une adresse avant ou après NAT selon son emplacement et la plateforme. Il faut consulter la documentation de la version exacte et tester en laboratoire plutôt que supposer qu’une ACL voit toujours l’adresse privée ou toujours l’adresse publique.

La documentation Cisco *NAT Order of Operation* expose les différences selon le sens du trafic. C’est une référence de conception et de dépannage, pas une garantie universelle pour toutes les familles de produits Cisco. Les routeurs IOS XE, les plates-formes de service, les pare-feu et les architectures distribuées peuvent avoir des détails distincts.

```text
TRAFIC SORTANT : INSIDE -> OUTSIDE

Hôte interne
  |
  | paquet : source 10.10.10.25, destination 198.51.100.80
  v
Interface / classification inside
  |
  v
Recherche de routage vers 198.51.100.80
  |
  v
Règle NAT source / création ou réutilisation d'état
  |
  v
Paquet émis : source 203.0.113.10, destination 198.51.100.80
  |
  v
Réseau externe
```

```text
TRAFIC ENTRANT : OUTSIDE -> INSIDE

Réseau externe
  |
  | paquet : destination 203.0.113.20
  v
Interface / classification outside
  |
  v
Correspondance NAT de destination
  |
  | destination traduite : 10.10.20.20
  v
Recherche de routage vers 10.10.20.20
  |
  v
Contrôles de sortie / résolution L2
  |
  v
Serveur interne
```

Le schéma montre le principe classique. Un diagnostic doit confirmer l’ordre réel de la plateforme, notamment lorsque des ACL, des politiques de routage ou un pare-feu sont configurés. Il est souvent utile de capturer le paquet de part et d’autre du NAT, car la comparaison des deux vues permet d’identifier exactement le champ qui a été modifié et le point où le paquet disparaît.

### 1.5. Calcul de traduction PAT

Considérons deux hôtes internes qui communiquent avec le même serveur externe HTTPS :

- Hôte A : `10.10.10.11:51500` ;
- Hôte B : `10.10.10.12:51500` ;
- Serveur externe : `198.51.100.80:443` ;
- Adresse PAT globale du routeur : `203.0.113.10`.

Le dispositif ne peut pas laisser les deux flux apparaître sur Internet comme le même couple global adresse/port lorsque cela rendrait ambigu le démultiplexage des réponses. Il peut conserver le port d’origine pour l’un et sélectionner un autre port global pour l’autre.

| Flux | Tuple source avant NAT | Tuple source possible après PAT | Destination |
|---|---|---|---|
| A | `10.10.10.11:51500` | `203.0.113.10:51500` | `198.51.100.80:443` |
| B | `10.10.10.12:51500` | `203.0.113.10:40001` | `198.51.100.80:443` |

Les ports du tableau sont illustratifs ; l’algorithme réel de sélection dépend de l’implémentation, des collisions et des ressources disponibles. Le routeur mémorise que le trafic de réponse vers `203.0.113.10:40001` doit être remis à `10.10.10.12:51500`. Une même adresse globale peut ainsi être partagée par de nombreux flux, sous réserve de la disponibilité des ports et des limites du dispositif.

PAT est donc une traduction d’adresse et de port, mais pas une promesse de capacité infinie. Les ports disponibles, le nombre de sessions, les temporisations, la taille des tables, la charge CPU ou ASIC et les limites logicielles peuvent devenir des contraintes. Il faut dimensionner les équipements à partir des profils d’usage, et pas seulement du nombre de postes.

### 1.6. Traduction des sommes de contrôle et des protocoles

La modification d’une adresse source ou destination IP nécessite une adaptation de la somme de contrôle de l’en-tête IPv4. La modification d’un port TCP ou UDP affecte également la somme de contrôle du segment, car le pseudo-en-tête de TCP/UDP contient les adresses IP sources et destinations, en plus du protocole et de la longueur. UDP IPv4 permet une somme de contrôle nulle dans des conditions historiques spécifiques ; le traitement reste dépendant du protocole et de l’implémentation.

Les traductions peuvent aussi interagir avec les paquets fragmentés. Seul le premier fragment IPv4 porte normalement l’en-tête de transport avec les ports. Pour traduire ou associer correctement les fragments suivants à une session, l’équipement doit disposer des informations nécessaires issues du premier fragment, ou appliquer un mécanisme dédié à la gestion de fragments. Les fragments reçus dans un ordre inattendu ou sans fragment initial peuvent être rejetés selon les capacités et la politique du système.

Les protocoles qui transportent des adresses ou des ports dans la charge utile peuvent exiger une passerelle applicative (ALG) ou une méthode de traversée NAT. Les exemples historiques comprennent certaines variantes de FTP, SIP et H.323. Les ALGs ne sont pas automatiquement souhaitables : une inspection erronée, un chiffrement de la signalisation ou une incompatibilité de version peut rendre la modification incorrecte. Une application moderne doit de préférence utiliser un mécanisme compatible avec NAT sans dépendre d’une inspection implicite du contenu.

IPsec présente également des contraintes spécifiques. AH protège des informations d’en-tête qui sont modifiées par un NAT, ce qui rend leur coexistence problématique. ESP ne fournit pas de ports TCP/UDP exploitables par un PAT classique. NAT Traversal encapsule généralement ESP dans UDP, souvent sur le port 4500, afin de permettre le passage dans de nombreux scénarios NAT. La compatibilité finale dépend toutefois des endpoints, du type de tunnel et des politiques de sécurité.

### 1.7. NAT statique

Le NAT statique crée une correspondance durable entre une adresse locale et une adresse globale. Il est adapté, par exemple, à un serveur qui doit être joignable sous une adresse prévisible ou à certains besoins d’interconnexion. Une translation statique d’adresse n’autorise pas automatiquement le trafic : le routage et les politiques de filtrage doivent eux aussi le permettre.

Exemple conceptuel :

```text
Serveur interne : 10.10.20.20
Adresse publiée : 203.0.113.20

Avant traduction, côté réseau extérieur :
  destination = 203.0.113.20

Après traduction, côté réseau intérieur :
  destination = 10.10.20.20
```

La correspondance d’adresse s’applique indépendamment d’un flux PAT créé par un utilisateur intérieur. Il faut vérifier que l’adresse globale est routée vers l’équipement NAT et qu’elle n’est pas utilisée simultanément par une autre translation, un pool dynamique ou une autre fonction de la plateforme. Les conflits de ressources peuvent engendrer des comportements inattendus ou empêcher la configuration de fonctionner.

Le NAT statique bidirectionnel traditionnel est distinct de la publication d’un port unique. Une traduction statique de port peut exposer un service spécifique, par exemple une session TCP externe vers le port 8443, remappée vers le port 443 d’un serveur. Là encore, elle ne remplace pas un filtrage entrant et une politique d’accès au serveur.

### 1.8. NAT dynamique et allocation de pools

Le NAT dynamique choisit une adresse globale dans un pool de traduction lorsqu’un hôte interne initie un trafic correspondant à la règle. L’entrée peut être retirée après expiration de la session ou selon les règles propres à la plateforme. Si le pool est épuisé, les nouveaux flux ne peuvent plus obtenir de translation, sauf si une autre règle applicable ou une autre ressource existe.

Le NAT dynamique sans surcharge classique utilise souvent une correspondance un-à-un temporaire entre une adresse intérieure et une adresse du pool. PAT sur pool ajoute la possibilité de partager les adresses par translation des ports. Il est essentiel de distinguer le **pool de ressources** (les adresses disponibles) de la **politique de sélection** (quels paquets sont admissibles à la règle NAT) et du **mécanisme de surcharge** (si plusieurs flux peuvent partager une adresse globale).

La définition d’un pool doit tenir compte du préfixe et de la manière dont le réseau amont route ces adresses. Si le pool n’est pas effectivement acheminé vers le routeur NAT, les paquets de retour ne lui arriveront pas. Une configuration NAT correcte n’est pas suffisante lorsque l’opérateur n’annonce pas le bloc, que le prochain saut est incorrect ou qu’une route plus spécifique détourne le trafic.

### 1.9. PAT : limites et comportement des flux

PAT permet à plusieurs hôtes de partager une adresse globale. Le routeur conserve un état de traduction à l’aide de l’adresse et du port de transport, du protocole et des critères de correspondance pertinents. Il peut allouer un port source global différent pour résoudre une collision. Les flux TCP, UDP et certains messages ICMP nécessitent des traitements distincts ; ICMP Echo Request/Reply utilise notamment un identifiant de requête plutôt que des ports TCP/UDP.

La table PAT n’est pas un registre permanent. Les entrées vieillissent afin de libérer les ressources. Les temporisations peuvent varier selon le protocole, l’état apparent de TCP, le trafic observé et la configuration. Des applications qui maintiennent des connexions inactives peuvent rencontrer une expiration prématurée, alors que des entrées trop longues peuvent consommer une capacité précieuse. Les temporisations doivent donc être choisies selon le comportement attendu des applications et les recommandations de la plateforme.

Les RFC de comportement NAT distinguent les règles de **mapping** (réutilisation ou attribution d’un endpoint externe) de celles de **filtering** (quels paquets entrants sont autorisés à utiliser cette correspondance). Ce sont deux propriétés différentes. Une translation prévisible n’implique pas un filtrage permissif, et une politique de filtrage stricte peut empêcher certaines applications pair-à-pair de fonctionner sans mécanisme de relais.

### 1.10. NAT hairpin / loopback

Le hairpin NAT permet à un client intérieur de joindre une application intérieure en utilisant le nom DNS ou l’adresse publique normalement présentée aux clients externes. Le dispositif reçoit un paquet dont la destination est l’adresse publiée ; il traduit cette destination vers le serveur intérieur. Selon la topologie, il peut aussi devoir traduire la source afin que le serveur réponde au NAT et que le retour traverse l’état de traduction approprié.

Sans hairpin, la connexion peut échouer si l’adresse publique n’est pas routable depuis le réseau intérieur ou si le routeur n’applique pas la règle de traduction dans ce sens. Une solution de conception est le DNS split-horizon : les clients internes résolvent le nom directement vers l’adresse privée, tandis que les clients externes reçoivent l’adresse publique. Cette solution n’est pas automatiquement supérieure ; il faut maintenir les zones DNS et leurs comportements cohérents.

```text
Client interne 10.10.10.40
        |
        | vise portal.exemple.tld -> 203.0.113.20
        v
+-----------------------------+
| Routeur NAT                 |
| DNAT : 203.0.113.20 ->       |
|        10.10.20.20           |
| SNAT si nécessaire pour      |
| forcer le retour par le NAT   |
+-----------------------------+
        |
        v
Serveur 10.10.20.20
        |
        | réponse via routeur NAT
        v
Client 10.10.10.40
```

Le hairpin doit être validé au niveau des routes de retour. Si le serveur voit l’adresse source réelle du client et renvoie directement vers sa passerelle habituelle, la réponse peut contourner le dispositif qui détient l’état NAT. Le client reçoit alors une réponse dont le tuple peut ne pas correspondre à la session attendue. Une traduction de source ou une route adaptée peut résoudre le problème, au prix d’une visibilité réduite sur l’adresse client côté serveur.

### 1.11. NAT et routage asymétrique

Dans un NAT à état, les deux directions d’un flux doivent généralement traverser le dispositif approprié, ou un ensemble de dispositifs partageant correctement l’état nécessaire. Si un paquet aller traverse un routeur A et le retour traverse un routeur B ne possédant pas la translation, B peut ne pas reconnaître le flux. Même si B applique une règle statique, les translations dynamiques et les ports PAT peuvent ne pas correspondre.

Les solutions possibles comprennent :

- assurer un routage symétrique vers le même routeur NAT ;
- utiliser un mécanisme de synchronisation d’état pris en charge ;
- concevoir un cluster NAT hautement disponible correctement configuré ;
- ajuster les politiques de routage et de répartition ;
- éviter de partager de manière incohérente un pool ou une adresse globale entre équipements autonomes.

La symétrie de chemin ne se déduit pas uniquement des routes par défaut. Le routage dynamique, le PBR, les ECMP, les liens de transport multi-opérateurs, les tunnels VPN et les mécanismes de redondance peuvent entraîner des chemins différents selon le sens. Le diagnostic doit examiner chaque direction de part et d’autre du NAT.

### 1.12. NAT et VPN IPsec

Les réseaux qui utilisent des adresses privées chevauchantes peuvent demander une traduction avant ou après l’encapsulation VPN. Une configuration « NAT exemption » ou une règle d’exclusion NAT peut être nécessaire pour que le trafic site-à-site conserve ses adresses d’origine à l’intérieur du tunnel. Si le trafic destiné au VPN est traduit prématurément, les ACL de chiffrement, les sélecteurs de trafic ou les routes peuvent ne plus correspondre.

Une conception doit répondre à quatre questions :

1. Quels préfixes doivent être routés dans le tunnel sans NAT ?
2. Quels préfixes doivent être traduits pour accéder à Internet ?
3. Le NAT s’effectue-t-il avant l’encapsulation ou après le décapsulation sur la plateforme concernée ?
4. Les deux extrémités partagent-elles les mêmes hypothèses de routage et de sélection de trafic ?

Un exemple de logique est d’exclure `10.20.0.0/16` vers `10.30.0.0/16` de la traduction Internet, tout en utilisant PAT pour les autres destinations. La syntaxe exacte dépend du produit : routeur IOS, IOS XE, pare-feu ASA/FTD et autres familles ne partagent pas les mêmes commandes ni le même ordre de traitement.

### 1.13. NAT entre VRF et domaines d’adressage chevauchants

Les VRF permettent de maintenir des tables de routage distinctes. Plusieurs clients peuvent réutiliser le même bloc privé, par exemple `10.0.0.0/8`, sans collision au sein de leurs tables respectives. La difficulté apparaît lorsqu’un flux doit passer d’une VRF à une autre ou rejoindre un service commun. Il faut alors définir explicitement la politique de routage, la portée du NAT et les adresses représentatives qui éviteront l’ambiguïté.

Des fonctionnalités Cisco de NAT entre VRF peuvent être disponibles selon la plateforme et la version. Elles peuvent exiger des options particulières, telles que `match-in-vrf`, des associations propres aux tables de routage ou des contraintes de pool. Une commande acceptée par le parseur ne prouve pas que la conception est prise en charge dans toutes les combinaisons de fonctions.

Un plan d’adressage « traduisible » doit inclure :

- les préfixes locaux dans chaque VRF ;
- les adresses traduites ou les pools affectés à chaque domaine ;
- les routes vers les adresses traduites ;
- les chemins de retour ;
- les règles de filtrage de chaque côté ;
- le comportement attendu pour les adresses qui se chevauchent ;
- la supervision et la journalisation permettant de retrouver le domaine d’origine.

### 1.14. NAT haute disponibilité et synchronisation d’état

La redondance de la passerelle ne signifie pas automatiquement la redondance de l’état NAT. Un protocole comme HSRP ou VRRP peut faire basculer une adresse de passerelle, mais les traductions dynamiques créées sur le routeur actif peuvent ne pas être présentes sur le routeur de secours. Si le dispositif secondaire ne possède pas la translation PAT nécessaire, les flux établis risquent d’être interrompus lors du basculement.

Une stratégie haute disponibilité doit distinguer :

- l’élection de l’équipement actif ;
- la reprise des adresses d’interface et des routes ;
- la synchronisation ou la réplication des sessions NAT ;
- le partage ou l’affectation des adresses globales et des pools ;
- la gestion du trafic asymétrique pendant le basculement ;
- l’impact sur les applications et les temporisations TCP/UDP ;
- les journaux qui associent les translations au bon équipement et au bon instant.

La méthode est spécifique au matériel et au système. Certaines plateformes prennent en charge des mécanismes de NAT stateful failover, tandis que d’autres ne répliquent que des parties de l’état ou ne prennent pas en charge une combinaison de fonctions donnée. Il faut consulter la matrice de fonctionnalités et réaliser un test de basculement en laboratoire.

### 1.15. CGNAT et partage massif d’IPv4

Le *Carrier-Grade NAT* (CGNAT) permet à un opérateur de partager un petit ensemble d’adresses IPv4 publiques entre un nombre important d’abonnés. Les clients peuvent être placés derrière un NAT domestique, puis derrière un NAT opérateur, ce qui entraîne une architecture de double NAT. Le partage réduit la demande d’adresses publiques, mais complique les connexions entrantes, l’identification des flux et certains protocoles temps réel.

Un enregistrement de traduction utilisé pour l’investigation doit généralement relier au minimum l’identifiant d’abonné, le protocole, l’adresse et le port publics, ainsi qu’un horodatage suffisamment précis. L’identification par seule adresse publique est insuffisante lorsque plusieurs abonnés partagent cette adresse à la même période. Les modèles d’allocation déterminent aussi les volumes de logs et la capacité nécessaire à leur conservation.

La RFC 6888 décrit des exigences communes relatives aux CGN. Elle souligne l’importance du dimensionnement des ressources, de l’attribution des ports, de l’identifiabilité et de la gestion des journaux. Le traitement des données doit également respecter les politiques de protection de la vie privée et les obligations légales applicables : la journalisation doit être suffisante pour les objectifs administratifs définis, sans collecter indistinctement des données superflues.

Les problèmes courants du CGNAT comprennent les limites de connexions simultanées, les applications qui nécessitent des connexions entrantes, les listes d’autorisation fondées sur l’adresse publique, les géolocalisations approximatives et les services qui interprètent le partage d’adresse comme un seul utilisateur. L’IPv6 natif peut réduire le besoin de NAT pour les connexions IPv6, mais il ne supprime pas automatiquement toutes les exigences de transition ou de filtrage.

### 1.16. NAT comportemental : mapping, filtering et temporisations

Les RFC relatives au comportement NAT décrivent plusieurs dimensions qui ne doivent pas être fusionnées :

- **Mapping** : comment une adresse et un port intérieurs sont associés à un endpoint extérieur ;
- **Filtering** : quels paquets entrants peuvent atteindre la correspondance ;
- **Hairpinning** : comment le dispositif traite un paquet qui doit revenir vers un endpoint situé de l’autre côté logique du même NAT ;
- **Temporisation** : combien de temps une association est conservée sans trafic pertinent ;
- **Gestion de TCP et ICMP** : comment le NAT traite les propriétés spécifiques de ces protocoles.

La terminologie dite *endpoint-independent mapping* décrit un comportement précis de réutilisation de mapping UDP ; elle ne signifie pas que les paquets entrants sont tous permis. La sécurité dépend notamment de la politique de filtrage, du contexte d’état et des contrôles complémentaires. Inversement, un filtrage endpoint-dependent peut gêner certaines applications pair-à-pair ou médias sans pour autant constituer un pare-feu complet.

Les RFC 4787, 5382 et 5508, mises à jour par la RFC 7857, restent des références importantes pour comprendre les attentes de comportement NAT. Elles sont particulièrement pertinentes pour les passerelles grand public, les applications temps réel, les services de traversée et les équipements d’accès opérateur.

### 1.17. NAT et fragmentation IPv4

La fragmentation ajoute une difficulté parce que les ports TCP et UDP ne figurent que dans le premier fragment. Un NAT doit pouvoir associer les fragments non initiaux au datagramme qui leur correspond. Selon l’implémentation, il peut conserver une association de fragments ou imposer des contraintes sur leur réception.

Les paquets fragmentés peuvent être rejetés par des équipements de sécurité, réassemblés, transmis ou traités avec des limites particulières. Des fragments qui arrivent avant le fragment initial peuvent constituer un cas délicat. Les attaques par fragments malformés, les recouvrements et les épuisements de mémoire sont des raisons pour lesquelles les équipements peuvent restreindre les fragments.

Le dépannage doit vérifier :

- si le premier fragment atteint le NAT ;
- si les fragments suivants suivent le même chemin ;
- si les règles de filtrage permettent les fragments nécessaires ;
- si le MTU du chemin et les messages ICMP liés à la fragmentation fonctionnent ;
- si un tunnel encapsule le trafic et réduit la MTU effective ;
- si les captures effectuées des deux côtés contiennent tous les fragments.

Il ne faut pas désactiver globalement les protections de fragmentation pour corriger une panne non comprise. Une meilleure solution consiste à déterminer si la cause vient du MTU, de la PMTUD, des filtres, de la mise en œuvre NAT ou d’un équipement intermédiaire.

### 1.18. NAT et ICMP

ICMP n’utilise pas les ports TCP/UDP. Pour certains messages, le NAT s’appuie sur l’identifiant de requête ou sur les informations liées au paquet qui a déclenché le message. Les messages d’erreur ICMP peuvent citer l’en-tête du paquet original ; la traduction doit traiter ces données de façon cohérente pour que le système final puisse associer l’erreur au flux concerné.

Les messages *Destination Unreachable*, *Time Exceeded* et ceux relatifs à la fragmentation sont particulièrement utiles au diagnostic. Un filtrage excessif d’ICMP peut empêcher la découverte de MTU ou masquer des erreurs de routage. Toutefois, autoriser tous les messages ICMP depuis toutes les sources sans politique n’est pas une exigence universelle : les règles doivent suivre la fonction de chaque type ICMP, l’architecture et les recommandations de sécurité applicables.

Si un ping échoue à travers le NAT, le problème peut provenir de l’association ICMP, d’un filtre, de la route de retour ou du fait que l’équipement distant ne répond pas aux requêtes. Il ne faut pas en déduire immédiatement que la traduction TCP/UDP est défaillante.

### 1.19. NAT et applications transportant des adresses dans la charge utile

Certaines applications peuvent inclure dans leur contenu une adresse IP ou un port en plus de ceux qui figurent dans les en-têtes. Une traduction des seuls en-têtes peut alors rendre incohérent le contenu applicatif. Historiquement, plusieurs produits ont implémenté des ALGs pour réécrire certaines données applicatives ou ouvrir des traductions associées.

Les ALGs doivent être analysés selon le protocole, sa version, le chiffrement et l’implémentation. Avec TLS ou une signalisation chiffrée, un équipement intermédiaire peut ne pas être capable de modifier la charge utile. Un ALG obsolète peut corrompre une session ou interférer avec un protocole moderne.

Pour le dépannage, comparer l’en-tête réseau ne suffit pas toujours. Une capture avant et après NAT peut montrer que les adresses IP ont été traduites correctement alors que l’application continue d’annoncer une adresse ou un port non routable. Il faut alors examiner la conception de l’application, la négociation des canaux secondaires, les mécanismes ICE/STUN/TURN pour la voix/vidéo et la politique d’inspection de la plateforme.

### 1.20. NAT n’est pas un contrôle de sécurité universel

Le fait que les machines internes utilisent des adresses privées ne signifie pas qu’elles soient protégées contre tout trafic malveillant. NAT limite souvent les communications entrantes non sollicitées parce qu’aucune translation dynamique correspondante n’existe ; cette propriété ne constitue pas une politique de sécurité explicite et ne remplace pas un pare-feu stateful.

Les traductions statiques et les redirections de ports peuvent ouvrir des services au réseau externe. Une application vulnérable reste vulnérable, même si elle est publiée derrière une adresse NAT. Le NAT ne chiffre pas le trafic, ne vérifie pas l’identité des utilisateurs et ne détermine pas si un flux est autorisé par une politique métier.

Les mesures complémentaires comprennent :

- un filtrage stateful avec une politique explicite ;
- la publication minimale des ports nécessaires ;
- un accès d’administration limité à des réseaux de gestion ;
- une segmentation des serveurs exposés dans une zone dédiée ;
- des mises à jour et une gestion des vulnérabilités ;
- la journalisation des translations et des décisions de filtrage ;
- une limitation des ressources afin d’éviter l’épuisement des tables ;
- un test de disponibilité et de retour arrière avant changement.

> **Piège :** Une translation statique n’est pas un filtre, et l’absence d’une entrée PAT dynamique n’est pas une preuve que l’équipement est correctement sécurisé. Les règles NAT et les règles de pare-feu ont des responsabilités différentes. Il faut analyser la translation, la route, les ACL et l’état de session séparément.

---

## 2. Configuration et Pratique

Les exemples ci-dessous utilisent la syntaxe classique Cisco IOS pour NAT IPv4. Les commandes exactes et les fonctionnalités disponibles dépendent du modèle, de la version IOS/IOS XE, des fonctions de sécurité activées et de la topologie. Les adresses publiques des exemples appartiennent aux plages de documentation RFC 5737 ; elles ne doivent pas être utilisées comme véritables adresses de production.

### 2.1. Topologie de laboratoire

```text
                      Réseau externe / Internet simulé
                                198.51.100.0/24
                                         |
                                  G0/1 203.0.113.2/30
                                +--------------------+
                                | R1 - NAT/PAT       |
                                |                    |
                                | G0/1 : outside     |
                                | G0/0 : inside      |
                                +--------------------+
                                  G0/0 10.10.10.1/24
                                         |
                                 +---------------+
                                 | LAN intérieur  |
                                 | 10.10.10.0/24  |
                                 +---------------+
                                   |           |
                            PC 10.10.10.11  Serveur
                                           10.10.10.20
```

Dans cette topologie, le routeur R1 traduit les adresses source du LAN intérieur pour leur permettre de joindre le réseau externe simulé. Le lien extérieur est représenté avec des adresses de documentation. En environnement réel, le prochain saut, l’adresse extérieure, les routes et le bloc NAT doivent être fournis par le plan d’adressage opérationnel.

### 2.2. Configuration de base des interfaces

```cisco
hostname R1

interface GigabitEthernet0/0
 description LAN_INSIDE
 ip address 10.10.10.1 255.255.255.0
 ip nat inside
 no shutdown

interface GigabitEthernet0/1
 description WAN_OUTSIDE
 ip address 203.0.113.2 255.255.255.252
 ip nat outside
 no shutdown

ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

`ip nat inside` et `ip nat outside` identifient les côtés intérieur et extérieur pour le NAT classique. Cette classification ne remplace pas la configuration des adresses IP, le routage ou le filtrage. La route par défaut indique un prochain saut extérieur dans cet exemple ; elle doit correspondre à la vraie topologie de laboratoire.

La route retour du réseau externe vers l’adresse globale PAT n’a pas nécessairement besoin d’une route spécifique lorsque la traduction utilise l’adresse de l’interface extérieure. En revanche, pour un pool d’adresses supplémentaires, le réseau amont doit acheminer ces adresses vers le routeur qui réalise les translations.

### 2.3. PAT avec l’adresse de l’interface extérieure

Une configuration classique PAT overload est :

```cisco
access-list 10 permit 10.10.10.0 0.0.0.255

ip nat inside source list 10 interface GigabitEthernet0/1 overload
```

L’ACL 10 sélectionne les sources qui correspondent à la règle PAT. Elle ne constitue pas, à elle seule, une ACL de filtrage du trafic entrant ou sortant. Il faut éviter de considérer une ACL utilisée pour classifier les traductions NAT comme la politique complète de sécurité réseau.

Le mot `overload` active le partage de l’adresse globale par traduction des ports ou des identifiants de flux concernés. Il permet à plusieurs hôtes intérieurs d’utiliser l’adresse de l’interface extérieure, sous réserve des limites de sessions et de ports de la plateforme.

Vérification :

```cisco
show ip nat translations
show ip nat statistics
show access-lists 10
show ip route
```

La commande `show ip nat translations` affiche les associations actives ou statiques selon la configuration. `show ip nat statistics` fournit des compteurs et informations relatives au fonctionnement NAT sur les plateformes qui proposent cette commande. Les sorties exactes varient suivant IOS et IOS XE.

Après avoir généré du trafic depuis le LAN, vérifier que les sources intérieures attendues apparaissent dans la table et que l’adresse inside global correspond à celle de l’interface extérieure. En absence d’entrée, contrôler le sens des interfaces, la sélection ACL, le routage et la génération effective du trafic.

### 2.4. NAT dynamique sur pool sans surcharge

Un exemple de pool d’adresses :

```cisco
ip nat pool PUBLIC-POOL 203.0.113.10 203.0.113.14 netmask 255.255.255.248
access-list 11 permit 10.10.10.0 0.0.0.255
ip nat inside source list 11 pool PUBLIC-POOL
```

Ce modèle illustre une traduction dynamique sans `overload`. Les capacités exactes du pool et les règles d’adressage doivent être vérifiées. L’adresse de réseau et les adresses réservées doivent être cohérentes avec le préfixe utilisé. Le réseau amont doit acheminer le bloc public vers R1, et le routeur doit disposer d’une route valide pour les destinations extérieures.

Sans surcharge, la disponibilité du pool limite le nombre de correspondances pouvant être créées simultanément selon la politique d’allocation. Si toutes les adresses sont occupées, les nouvelles traductions peuvent échouer. Il faut surveiller la consommation et dimensionner le pool selon le nombre de sessions et la durée des états.

Pour utiliser un pool avec PAT, une configuration IOS courante ajoute le mot `overload` :

```cisco
ip nat inside source list 11 pool PUBLIC-POOL overload
```

Le résultat exact dépend de la plateforme et de sa configuration. Il faut éviter de partager de façon incohérente une même adresse de pool entre plusieurs règles dynamiques ou de définir une même adresse globale dans des mécanismes statiques et dynamiques contradictoires. La FAQ NAT de Cisco met en garde contre plusieurs de ces cas.

### 2.5. NAT statique un-à-un

Pour publier une adresse interne sous une adresse extérieure fixe :

```cisco
ip nat inside source static 10.10.10.20 203.0.113.20
```

Cette commande crée une correspondance statique entre le serveur `10.10.10.20` et l’adresse inside global `203.0.113.20`. Il faut s’assurer que cette adresse est disponible et routée vers R1. Une règle de pare-feu doit définir les sources, protocoles et ports autorisés à atteindre le serveur.

La traduction ne garantit pas qu’une connexion entrante puisse arriver jusqu’au serveur. Vérifie le chemin retour, la passerelle du serveur, les routes du réseau extérieur et les éventuelles politiques de filtrage. Un test depuis le LAN peut aussi échouer si la plateforme ne prend pas en charge le comportement hairpin souhaité.

### 2.6. Publication d’un port de serveur

Pour exposer le port TCP 443 d’un serveur intérieur sur le port TCP 8443 de l’adresse globale :

```cisco
ip nat inside source static tcp 10.10.10.20 443 203.0.113.20 8443
```

Cette syntaxe montre une traduction de port statique sur des plateformes IOS compatibles. Les variantes syntaxiques et les limites de port forwarding doivent être vérifiées sur le matériel utilisé. Il faut ensuite ajouter, dans le système de filtrage approprié, une autorisation explicite vers l’adresse et le port publiés. Ne suppose pas que la commande NAT crée toutes les règles de sécurité nécessaires.

Un test utile examine chaque étape :

1. Le client externe atteint-il l’adresse `203.0.113.20` ?
2. La route extérieure dirige-t-elle les paquets vers R1 ?
3. Le port 8443 correspond-il à la traduction statique attendue ?
4. La route vers `10.10.10.20` est-elle correcte ?
5. Le serveur écoute-t-il sur le port 443 ?
6. La réponse repasse-t-elle par R1 ?
7. Le filtrage et les politiques de sécurité autorisent-ils les deux sens du trafic ?

### 2.7. Exclusion NAT pour le trafic VPN

Les exemples d’exclusion NAT varient largement selon la plateforme et le type de VPN. Dans un laboratoire IOS classique, une politique NAT fondée sur une ACL étendue ou une route-map peut empêcher certains flux de correspondre à la règle PAT générale. Il est souvent préférable de concevoir des conditions de correspondance précises plutôt que d’ajouter une large exception après coup.

Pseudo-exemple de logique (à adapter avant utilisation) :

```cisco
! Trafic site-a-site à conserver en adresses originales
access-list 120 deny   ip 10.10.10.0 0.0.0.255 10.20.20.0 0.0.0.255
! Trafic local vers destinations externes à traduire
access-list 120 permit ip 10.10.10.0 0.0.0.255 any

ip nat inside source list 120 interface GigabitEthernet0/1 overload
```

Cette illustration ne doit pas être copiée sans validation. Dans la syntaxe NAT IOS classique, le comportement d’une ACE `deny` dans l’ACL référencée par la règle NAT est généralement de signifier « ne pas traduire ce trafic » et non « bloquer le paquet », mais les détails de configuration et les interactions avec les ACL de sécurité doivent être vérifiés. Les plateformes VPN/pare-feu peuvent exiger d’autres mécanismes explicites d’exemption NAT.

La méthode sûre est de documenter les flux qui doivent garder leurs adresses, puis de tester les translations avec `show ip nat translations`, les compteurs ACL, les routes et les sélecteurs VPN. Une politique NAT trop large peut modifier le trafic avant qu’il soit reconnu comme trafic VPN.

### 2.8. Hairpin NAT : règles de conception

Il n’existe pas de configuration hairpin universelle pour tous les routeurs Cisco. La prise en charge et la syntaxe varient avec la plateforme et le système logiciel. Dans un cas simple, le paquet doit être reconnu comme trafic entrant vers une adresse publiée, traduit vers le serveur, puis traité de façon à garantir le retour via le même équipement NAT.

Avant de configurer, décider si une zone DNS interne peut résoudre directement le nom du service vers son adresse privée. Si le client interne utilise l’adresse publique, vérifier que le routeur sait effectuer à la fois la traduction de destination et, si nécessaire, la traduction de source. Capturer les paquets côté client et côté serveur permet de confirmer l’adresse source réellement vue par ce dernier.

Attention : la traduction de source pour hairpin peut faire apparaître tous les clients internes avec une seule adresse du routeur. Cela facilite le retour symétrique mais réduit la visibilité des adresses client dans les journaux applicatifs. Lorsque l’identité réelle du client est requise, privilégier une architecture qui la conserve ou utilise un mécanisme applicatif fiable de transmission d’identité, correctement sécurisé.

### 2.9. Vérification et diagnostic sans débogage

Commandes utiles sur Cisco IOS/IOS XE, sous réserve de disponibilité :

```cisco
show ip nat translations
show ip nat translations verbose
show ip nat statistics
show ip interface
show ip route
show ip cef
show access-lists
show running-config | include ip nat|access-list|route-map
show logging
```

Ne lancer que les commandes pertinentes à la plateforme. Certaines variantes de `show ip nat translations` peuvent ne pas exister sur toutes les versions. `show ip cef` aide à examiner les informations de transfert CEF mais ne remplace pas l’examen de l’état NAT.

Une procédure de diagnostic structurée :

- vérifier l’interface d’entrée et l’interface de sortie ;
- confirmer les rôles inside/outside ;
- confirmer la route vers la destination et la route retour ;
- vérifier que le trafic source correspond à la règle NAT ;
- générer une nouvelle session depuis l’hôte de test ;
- observer si une translation se crée ;
- comparer la capture avant NAT à celle après NAT ;
- vérifier les ACL et politiques de sécurité distinctes ;
- confirmer la disponibilité des ports, des pools et de la capacité d’état.

Éviter de vider la table NAT pendant les heures de pointe, car les sessions actives peuvent être interrompues. Une opération de nettoyage doit être limitée et planifiée.

### 2.10. Interpréter une table de translations

Une sortie typique peut montrer les colonnes *Pro*, *Inside global*, *Inside local*, *Outside local* et *Outside global*. Il faut lire ces champs en fonction de la direction et du type de NAT. Pour une entrée PAT, le numéro de port est essentiel pour différencier les flux. Pour une translation statique, une entrée peut apparaître même sans session utilisateur active.

Exemple illustratif :

```text
Pro  Inside global        Inside local        Outside local       Outside global
tcp  203.0.113.2:40001    10.10.10.11:51500   198.51.100.80:443   198.51.100.80:443
```

Le sens de la lecture n’est pas « global à gauche donc public partout ». Les colonnes nomment les rôles de l’adresse dans le modèle NAT classique. L’adresse extérieure peut être identique dans les champs local et global lorsque l’équipement ne traduit pas les adresses des hôtes externes.

La présence d’une entrée n’indique pas nécessairement que le serveur distant est joignable. Elle montre que l’équipement a créé ou maintient une association. Il faut encore vérifier les routes, les politiques de sécurité, les états de couche 2 et le comportement du pair distant.

### 2.11. Captures de paquets avant et après NAT

La méthode de preuve la plus claire consiste à effectuer deux captures synchronisées, l’une sur l’interface inside et l’autre sur l’interface outside. Comparer les éléments suivants :

- adresse source et adresse destination IPv4 ;
- ports TCP/UDP ou identifiant ICMP ;
- flags TCP et numéros de séquence/accusé de réception ;
- longueur des paquets et identifiants de fragments ;
- sommes de contrôle ;
- messages ICMP d’erreur associés ;
- heure d’émission et d’arrivée ;
- paquets de réponse et chemin retour.

Une capture extérieure peut montrer un paquet qui semble correctement traduit alors que le serveur ne reçoit rien. Cela peut signaler une route incorrecte, une ACL, une interface de sortie erronée ou une perte après le point de capture. Une capture intérieure peut révéler que le paquet arrive au routeur mais n’est jamais transmis à l’extérieur. L’absence d’un paquet dans une capture doit être interprétée en fonction du point exact, du sens, du filtre de capture et des limites de l’outil.

### 2.12. Débogage contrôlé

Les commandes `debug` peuvent exposer des événements de création et de suppression de translations, mais elles peuvent aussi produire un débit de messages très élevé. Les noms exacts des commandes dépendent de la plateforme et de la version. En production, commencer avec les compteurs, les tables et les captures ciblées.

Si un débogage est indispensable, limiter sa portée au trafic de test lorsque la fonction le permet, surveiller la charge CPU, définir une période très courte et prévoir un arrêt immédiat. Après l’opération, exécuter la commande de désactivation appropriée à la plateforme ; sur IOS classique, `undebug all` ou `no debug all` est souvent disponible.

Ne collecte pas des captures ou journaux contenant des informations personnelles sans politique adéquate. Les journaux NAT peuvent permettre de relier une session à un hôte interne et, dans un contexte CGNAT, à un abonné précis. Les droits d’accès, la durée de conservation et la précision temporelle doivent être définis.

> **Astuce :** Quand un flux ne fonctionne pas, vérifie séparément **(1)** la création de translation, **(2)** la route aller, **(3)** le filtrage entrant/sortant et **(4)** la route retour. Une translation existante ne prouve pas la connectivité de bout en bout ; l’absence de translation ne prouve pas que le routage est incorrect. Cette séparation réduit fortement le temps de dépannage.

---

## 3. Dépannage et Sécurité

### 3.1. Arbre de décision de dépannage

```text
Le flux échoue
      |
      v
L'hôte source envoie-t-il réellement le paquet ?
      |
      +-- NON --> vérifier application, passerelle, VLAN, route locale
      |
      +-- OUI
            |
            v
Le paquet atteint-il l'interface NAT inside ?
            |
            +-- NON --> vérifier routage amont, ACL, L2 et captures
            |
            +-- OUI
                  |
                  v
Une règle NAT correspond-elle au flux ?
                  |
                  +-- NON --> vérifier inside/outside, ACL, route-map, VRF
                  |
                  +-- OUI
                        |
                        v
Une translation est-elle créée/active ?
                        |
                        +-- NON --> pool épuisé, collision, ressource, règle
                        |
                        +-- OUI
                              |
                              v
Le paquet traduit sort-il du routeur ?
                              |
                              +-- NON --> route, filtrage, politique, CEF
                              |
                              +-- OUI
                                    |
                                    v
Le retour revient-il au même état NAT ?
                                    |
                                    +-- NON --> route retour, asymétrie, pair
                                    |
                                    +-- OUI --> examiner serveur et application
```

Ce diagramme représente un flux de diagnostic, pas une preuve absolue : les architectures multi-interfaces, multi-VRF et multi-NAT peuvent demander plus de points de contrôle. L’objectif est de localiser la première étape où le comportement observé diverge du comportement attendu.

### 3.2. Aucun état de translation n’est créé

Causes probables :

- interface incorrectement classée inside/outside ;
- l’ACL de sélection ne correspond pas à la source réelle ;
- la politique route-map sélectionne une autre interface ou une autre route ;
- le flux ne traverse pas le routeur NAT ;
- le pool est épuisé ou invalide ;
- une route, un VRF ou une autre fonction empêche le chemin attendu ;
- le trafic est exclu intentionnellement de la traduction ;
- une contrainte propre à la plateforme ou au protocole empêche la création d’état.

Procédure : compare la configuration courante à une matrice contenant source, destination, protocole, interface d’entrée, interface de sortie et translation souhaitée. Ensuite, vérifie les compteurs de la règle, l’état des interfaces et les routes. Ne modifie pas immédiatement la wildcard ACL : confirme d’abord l’adresse source réelle observée à l’entrée.

### 3.3. Translation présente, mais trafic sans réponse

Une entrée NAT confirme seulement qu’un mapping existe. Le paquet peut être bloqué par une ACL, routé vers un mauvais prochain saut, rejeté par le serveur, perdu par le réseau externe ou renvoyé par un chemin qui contourne le dispositif. Le retour peut également expirer si la temporisation NAT est trop courte pour le profil de trafic.

Comparer les captures inside/outside et vérifier les compteurs d’interface. Pour un serveur publié, contrôler l’écoute réelle sur le port, la passerelle du serveur, les règles de pare-feu de l’hôte et la route retour. Pour PAT sortant, confirmer que la réponse du serveur vise l’adresse et le port globaux exacts présents dans la table.

### 3.4. Épuisement du pool ou saturation PAT

Une panne de capacité peut apparaître lorsque toutes les adresses d’un pool sont utilisées, lorsque la consommation de ports PAT est élevée ou lorsque la plateforme atteint une limite de sessions/ressources. L’impact peut être intermittent : certaines nouvelles connexions échouent alors que des sessions plus anciennes continuent de fonctionner.

Le diagnostic doit examiner la taille du pool, le nombre d’entrées actives, les temporisations et les taux de création/suppression. Il faut également chercher les boucles d’application, les clients qui ouvrent un très grand nombre de sessions et les flux UDP qui gardent longtemps un état. Augmenter aveuglément les temporisations peut accentuer la saturation ; réduire toutes les temporisations peut casser des applications légitimes.

Les remèdes dépendent de la cause : augmenter le pool ou la capacité supportée, répartir le trafic sur plusieurs ressources, ajuster certaines temporisations justifiées, réduire le nombre de connexions inutiles, analyser les applications bavardes ou faire évoluer l’architecture d’adressage. Toute modification doit être évaluée par rapport aux limites du matériel et à l’adressage réellement routé.

### 3.5. Erreurs de translation statique et conflits d’adresses

Les erreurs de configuration incluent une adresse inside global déjà utilisée, un pool qui chevauche une adresse statique, une destination publiée qui n’est pas routée vers le NAT et une translation statique de port qui entre en collision avec une autre règle. La configuration peut être rejetée, rester inactive ou avoir des résultats inattendus suivant la plateforme.

Documenter dans un tableau l’adresse intérieure, l’adresse globale, le protocole, le port, le propriétaire du service, les ACL associées et la route amont. Avant d’ajouter une règle, comparer le nouveau mapping à toutes les autres règles, aux pools et aux adresses des interfaces. La documentation doit préciser si la translation est permanente, temporaire, redondée et supervisée.

### 3.6. Double NAT et CGNAT côté client

Lorsqu’un routeur de site traduit les adresses avant qu’un équipement opérateur n’effectue lui-même un CGNAT, le client se trouve derrière deux couches NAT. Ce fonctionnement est compatible avec de nombreux usages sortants, mais complique les communications entrantes, les VPN d’accès, les jeux en réseau, les services auto-hébergés et certaines applications temps réel.

Pour diagnostiquer, comparer l’adresse WAN du routeur au résultat observé depuis Internet. Si ces adresses diffèrent, il peut exister un NAT amont, un proxy, une architecture multi-homing ou un autre mécanisme. La différence ne prouve pas toujours un CGNAT ; il faut examiner la configuration de l’opérateur et les chemins réseau.

Les options incluent une adresse publique affectée directement, un service de redirection opérateur, un VPN sortant vers un point de présence, un relais applicatif ou l’usage d’IPv6 lorsque disponible. Le contournement doit respecter les règles et les contrôles de sécurité du réseau. Il ne faut pas exposer directement des services internes simplement pour supprimer le symptôme.

### 3.7. Routage asymétrique et clusters NAT

Les réseaux à chemins multiples doivent garantir que les translations sont cohérentes entre les appareils capables de recevoir le trafic d’un même flux. Un cluster peut synchroniser l’état, partager des adresses virtuelles ou répartir des sessions selon une affinité ; toutes les implémentations n’offrent pas les mêmes garanties.

Lors d’un basculement, examiner :

- si les adresses inside/outside et les routes restent disponibles ;
- si le secondaire reprend les mappings statiques ;
- si les états PAT dynamiques sont synchronisés ;
- si le chemin aller et retour reste cohérent ;
- si l’adresse publique est annoncée par le bon équipement ;
- si les sessions TCP en cours survivent réellement ou doivent se reconnecter ;
- si les journaux permettent de reconstruire les événements avant/après basculement.

La réussite du ping vers la passerelle virtuelle ne prouve pas la conservation des sessions NAT. Il faut tester des flux représentatifs, dont TCP longues durées, UDP, publications entrantes et VPN, et vérifier la récupération après redémarrage ou perte du lien de synchronisation.

### 3.8. NAT, pare-feu et exposition des services

NAT et filtrage répondent à des objectifs différents. NAT modifie les identifiants réseau ; un pare-feu décide si le trafic est autorisé selon une politique. Un système intégré peut exécuter les deux fonctions, mais les politiques restent conceptuellement distinctes.

Pour chaque service publié, définir :

- le propriétaire technique et le besoin métier ;
- l’adresse et le port externes ;
- le serveur et port internes ;
- les sources autorisées, si elles peuvent être limitées ;
- le protocole et les flux retour nécessaires ;
- la journalisation et la supervision ;
- le mécanisme d’authentification applicative ;
- les exigences de patching, de segmentation et de réponse aux incidents ;
- une date de révision ou d’expiration de la règle si elle est temporaire.

Éviter les redirections globales de plages de ports lorsqu’elles ne sont pas strictement nécessaires. N’exposer que les services voulus, et placer les serveurs publics dans une zone conçue à cet effet. Une translation NAT ne corrige pas une application insuffisamment sécurisée.

### 3.9. Contrôles d’accès et règles NAT

Une ACL utilisée pour déterminer quelles adresses sont traduites ne doit pas être réutilisée mentalement comme ACL de pare-feu. Une règle telle que `permit 10.10.10.0 0.0.0.255` signifie que les sources de cette plage sont candidates à la traduction PAT ; elle ne définit pas à elle seule quels ports externes sont accessibles et ne garantit pas que tout paquet sélectionné soit acheminé.

Pour éviter les erreurs :

1. nommer clairement les ACL de sélection NAT et les ACL de sécurité ;
2. documenter si les règles voient les adresses pré- ou post-traduction ;
3. tester les règles dans les deux directions ;
4. limiter les autorisations aux protocoles et sources nécessaires ;
5. contrôler les compteurs avant/après le changement ;
6. valider l’effet sur les flux existants, pas seulement sur les nouvelles connexions.

### 3.10. Journalisation, traçabilité et confidentialité

Pour un environnement d’entreprise, les journaux NAT doivent permettre de comprendre le comportement des translations et de relier les événements à l’horloge de référence. Dans les environnements où plusieurs utilisateurs partagent une adresse publique, l’adresse source publique seule n’identifie pas nécessairement un terminal ou un utilisateur.

Un ensemble de journaux utile inclut selon le contexte le protocole, les adresses et ports traduits, l’heure de création et de fin, la source interne ou un identifiant de domaine, et le dispositif qui a effectué la traduction. La granularité et le contenu doivent respecter les objectifs opérationnels, les exigences réglementaires et les politiques de confidentialité.

Synchroniser les équipements par une source de temps fiable est essentiel. Une dérive d’horloge peut rendre les rapprochements difficiles, notamment lorsque les volumes de logs sont élevés. Il faut également définir l’accès aux logs, leur intégrité, la rétention, la sauvegarde et les alertes lorsque la journalisation échoue ou que le volume dépasse la capacité prévue.

### 3.11. Protection contre l’épuisement des ressources

Un attaquant ou une application défectueuse peut tenter de provoquer une création massive d’états. Le risque inclut l’épuisement de la table NAT, des ports de traduction, de la mémoire, des ressources CPU ou des ressources de journalisation.

Les protections possibles dépendent de la plateforme : limites de sessions par source ou contexte, contrôle de débit, filtrage de trafic anormal, limitation de nouvelles connexions, supervision de l’état et capacité suffisante. Les mesures doivent être testées pour ne pas pénaliser des applications légitimes derrière un même NAT, notamment les réseaux d’entreprise, hôtels ou campus où de nombreux clients partagent une adresse globale.

La capacité PAT ne se réduit pas au nombre théorique de ports TCP. Des restrictions de la plateforme, les plages réservées, les tuples concurrents, le protocole, les temporisations et la politique d’allocation réduisent la capacité réellement utilisable. Le dimensionnement doit s’appuyer sur des mesures et les spécifications du fabricant.

### 3.12. MTU, PMTUD et problèmes d’applications

Des sessions qui s’établissent mais bloquent lors du transfert de données volumineuses peuvent révéler une difficulté MTU/PMTUD plutôt qu’une règle NAT erronée. Les tunnels et encapsulations réduisent souvent le MTU effectif. Si les messages ICMP nécessaires à la découverte du MTU sont bloqués, certaines connexions peuvent rester partiellement fonctionnelles.

Comparer de petits et grands paquets, capturer les échanges ICMP, vérifier les interfaces de tunnel, les MSS TCP et les politiques d’inspection. L’ajustement TCP MSS peut être approprié dans certains contextes, mais ne doit pas masquer une MTU incohérente ou une PMTUD défaillante. Les mécanismes et commandes disponibles dépendent du produit.

### 3.13. NAT64 et IPv6 : ne pas confondre les mécanismes

NAT44 et PAT sont des mécanismes IPv4-vers-IPv4. NAT64 est une fonction de transition permettant à des clients IPv6 de communiquer avec des serveurs IPv4 selon une architecture et un préfixe IPv6 dédiés. DNS64 peut synthétiser des réponses AAAA à partir d’enregistrements A dans certains déploiements. Le fonctionnement dépend de la solution et de l’architecture, et ne se résume pas à l’emploi d’une commande NAT44.

NPTv6, quant à lui, traduit un préfixe IPv6 à un autre sans être identique au PAT IPv4. En IPv6, la disponibilité de grandes plages d’adresses réduit le besoin de traduire de nombreux hôtes derrière une adresse unique, mais elle ne supprime pas la nécessité de filtrer, de router correctement, de gérer les préfixes et de sécuriser les services exposés.

Lors d’un incident, identifier d’abord la famille d’adresses du client, du serveur et du transport. Une application peut préférer IPv6 à IPv4 et échouer sur le chemin IPv6 alors que le NAT44 de sortie fonctionne parfaitement. Les tests doivent donc couvrir chaque chemin réellement utilisé par l’application.

### 3.14. Plan de changement et retour arrière

Avant un changement NAT en production, sauvegarder la configuration et collecter l’état courant : translations, statistiques, routes, ACL, route-maps, interfaces, VRF et journaux. Définir un plan d’essai comprenant les flux entrants et sortants, les applications critiques, les chemins VPN, les communications depuis les réseaux internes et externes et le comportement lors d’une panne.

Le plan de retour arrière doit préciser quelle commande ou quel ensemble de commandes restaurer, dans quel ordre et comment vérifier que les anciens flux et services sont de nouveau disponibles. Une modification d’une règle PAT commune peut affecter de nombreuses sessions ; la suppression d’une translation statique peut couper un service exposé immédiatement.

Après le changement, vérifier les compteurs NAT, les sessions, les interfaces, les logs et les résultats applicatifs. Les vérifications doivent être documentées avec un horodatage et un résultat attendu, puis répétées après une période représentative de trafic.

> **Danger :** Une règle NAT erronée peut interrompre massivement l’accès Internet, publier un service sensible, contourner une hypothèse de segmentation ou détourner le trafic vers un hôte inattendu. En environnement PAT/CGNAT, une saturation peut empêcher la création de nouvelles connexions pour un grand nombre d’utilisateurs. Avant de changer les mappings, les pools ou la redondance, il faut vérifier les routes, l’unicité des adresses globales, les ACL de sécurité, la capacité et le chemin retour, puis disposer d’un plan de retour arrière testé.

---

## Points à retenir

- **NAT/PAT est un mécanisme de transformation d’adresses et d’état, pas un protocole de routage ni un pare-feu.** La réussite d’une translation ne prouve ni la connectivité de bout en bout ni la sécurité du service.
- **L’ordre de traitement, la symétrie du chemin et les temporisations sont déterminants.** Les règles doivent être comprises selon la plateforme, la direction inside/outside, les VRF, le VPN, les ACL et les mécanismes de redondance.
- **La capacité, la traçabilité et le comportement applicatif doivent être conçus explicitement.** Pools, ports PAT, journaux, CGNAT, hairpin, fragmentation et traversée VPN sont des sources fréquentes d’incidents avancés.

## Références techniques

- RFC 3022 — Traditional IP Network Address Translator (Traditional NAT): https://www.rfc-editor.org/rfc/rfc3022
- RFC 1918 — Address Allocation for Private Internets: https://www.rfc-editor.org/rfc/rfc1918
- RFC 4787 — NAT Behavioral Requirements for Unicast UDP: https://www.rfc-editor.org/rfc/rfc4787
- RFC 5382 — NAT Behavioral Requirements for TCP: https://www.rfc-editor.org/rfc/rfc5382
- RFC 5508 — NAT Behavioral Requirements for ICMP: https://www.rfc-editor.org/rfc/rfc5508
- RFC 7857 — Updates to NAT Behavioral Requirements: https://www.rfc-editor.org/rfc/rfc7857
- RFC 6888 — Common Requirements for Carrier-Grade NATs: https://www.rfc-editor.org/rfc/rfc6888
- Cisco — Understand the NAT Order of Operation: https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/6209-5.html
- Cisco — Network Address Translation (NAT) Frequently Asked Questions: https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/26704-nat-faq-00.html
- Cisco — Troubleshoot Network Address Translation with Frequently Asked Questions: https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/218012-troubleshoot-network-address-translation.html
