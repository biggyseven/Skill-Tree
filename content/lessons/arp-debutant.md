---
node_id: arp-debutant
title: ARP & résolution L2/L3 - Débutant
---

# ARP & résolution L2/L3 - Débutant

**Niveau :** Débutant

Le protocole **Address Resolution Protocol (ARP)** permet à un équipement IPv4 de découvrir l’adresse de couche 2 associée à une adresse IPv4 sur un réseau local compatible, notamment Ethernet. Il résout une difficulté fondamentale de l’architecture TCP/IP : une application veut communiquer avec une adresse IP, mais, pour transmettre une trame sur Ethernet, la carte réseau doit connaître une adresse MAC de destination. IP et Ethernet utilisent donc des espaces d’adressage distincts qui doivent être reliés au moment de l’émission d’une trame.

Décrit à l’origine dans la RFC 826, publiée en 1982, ARP est devenu un mécanisme classique des réseaux IPv4 sur Ethernet. Il est indépendant de la logique applicative : une session Web, un ping ou une connexion SSH peut déclencher ARP sans que l’application ait besoin de connaître le protocole. ARP ne transporte pas le contenu de la communication ; il aide simplement l’équipement à déterminer l’adresse matérielle à placer dans l’en-tête Ethernet pour le prochain saut local.

Pour comprendre ARP, il faut distinguer la couche réseau (couche 3 du modèle OSI), où l’on raisonne avec les adresses IP et les routes, de la couche liaison (couche 2), où les trames Ethernet sont acheminées à l’aide des adresses MAC au sein d’un domaine de diffusion. Une adresse IP indique où se trouve logiquement une destination ; une adresse MAC identifie l’interface de couche 2 qui doit recevoir la trame sur le segment local. Ces adresses ne sont ni interchangeables ni équivalentes.

ARP est particulièrement important pour diagnostiquer les problèmes de connectivité locale, les erreurs de passerelle, les doublons d’adresses et certaines attaques de couche 2. Il utilise des requêtes généralement diffusées en broadcast, des réponses habituellement unicast et un cache qui conserve temporairement les associations IP–MAC. Il ne traverse pas normalement un routeur : chaque réseau IPv4 local effectue sa propre résolution, au besoin, pour le prochain saut de son domaine de liaison.

> **Analogie** : Imagine un immeuble dans lequel chaque appartement possède un numéro logique utilisé par le service de distribution, mais où le livreur doit aussi connaître le nom inscrit sur l’interphone pour accéder au bon appartement. L’adresse IP ressemble au numéro d’appartement ; l’adresse MAC ressemble à l’identifiant de l’interphone sur le réseau local. Le livreur ne crie pas le nom de tous les habitants à chaque colis : lorsqu’il ne connaît pas encore la correspondance, il demande dans le hall « Qui utilise le numéro d’appartement 12 ? ». L’occupant concerné répond avec l’identifiant à utiliser. Le livreur mémorise la correspondance pour ses livraisons suivantes.
>
> Le hall représente le domaine de broadcast, souvent un VLAN. La demande initiale est entendue par les appareils de ce domaine, mais pas automatiquement par ceux d’un autre étage séparé par un routeur. Si le colis doit parvenir à un immeuble lointain, le livreur ne cherche pas l’interphone du destinataire final dans tous les immeubles du trajet : il remet d’abord le colis au centre de distribution local, c’est-à-dire à la passerelle par défaut. Cette passerelle l’achemine ensuite vers le réseau suivant et résout à son tour l’adresse de couche 2 nécessaire. Le cache ARP est comparable au carnet dans lequel le livreur conserve les correspondances récentes. Ce carnet doit être actualisé, car un appareil peut être remplacé ou une adresse IP peut être réattribuée. Enfin, si quelqu’un répond à la place de l’occupant légitime en annonçant une fausse correspondance, le livreur risque d’envoyer les colis au mauvais endroit : c’est l’idée générale d’une falsification ARP.

---

## 1. La théorie et les algorithmes

### 1.1. Le problème que résout ARP

Lorsqu’un hôte IPv4 veut envoyer des données, il commence par prendre une décision de couche 3 : la destination appartient-elle à son sous-réseau local ou faut-il passer par une passerelle ? Cette décision repose sur son adresse IP, son masque ou son préfixe, et sa table de routage. Une fois le prochain saut identifié, l’hôte doit encapsuler le paquet IP dans une trame de couche 2 qui puisse être transmise sur l’interface appropriée.

Sur Ethernet, la trame contient notamment une adresse MAC source et une adresse MAC de destination. L’adresse IP de destination reste dans le paquet IP encapsulé. Si la destination est directement accessible sur le segment local, l’hôte a besoin de la MAC correspondant à l’adresse IP de cette destination. Si la destination se trouve sur un autre réseau, il a besoin de la MAC de la passerelle choisie, et non de la MAC de la machine distante.

ARP résout cette correspondance pour IPv4. Il ne détermine pas la route à suivre, ne choisit pas la passerelle par défaut et ne remplace pas la table de routage. Il intervient après la décision de routage, au moment où l’émetteur a besoin d’une adresse de couche 2 pour le prochain saut.

Exemple : un PC possède `192.168.10.25/24` et veut joindre `192.168.10.40`. Comme les deux adresses appartiennent à `192.168.10.0/24`, le PC tente une résolution ARP pour `192.168.10.40`. En revanche, pour joindre `192.168.20.40`, il consulte sa table de routage. Si la route indique que la passerelle est `192.168.10.1`, le PC résout `192.168.10.1` en adresse MAC et envoie la trame à cette passerelle. Le paquet IP conserve `192.168.20.40` comme destination IP.

### 1.2. Adresse IP et adresse MAC : deux fonctions distinctes

Une adresse IPv4 est longue de 32 bits et est généralement écrite en quatre nombres décimaux séparés par des points, par exemple `192.168.10.25`. Le masque ou le préfixe permet de distinguer la partie réseau et la partie hôte. Une adresse MAC Ethernet classique est longue de 48 bits, habituellement affichée sous la forme de six groupes hexadécimaux, par exemple `00:1A:2B:3C:4D:5E`.

| Élément | Couche habituelle | Taille usuelle | Utilité |
|---|---|---:|---|
| Adresse IPv4 | Couche 3 | 32 bits | Identifier une interface dans un plan d’adressage IP et acheminer les paquets |
| Adresse MAC Ethernet | Couche 2 | 48 bits | Identifier la source et la destination d’une trame sur le segment Ethernet |
| Masque/préfixe IPv4 | Couche 3 | 32 bits pour le masque | Déterminer la partie réseau et la partie hôte |
| Adresse de passerelle | Couche 3 | IPv4 | Indiquer un prochain saut IP pour les destinations hors du réseau local |
| Entrée ARP | Cache local | Association IP–MAC | Conserver une correspondance utilisée pour construire une trame |

Une même interface possède généralement une adresse IP et une adresse MAC, mais la correspondance n’est pas une identité permanente. Une interface peut avoir plusieurs adresses IP ; une adresse IP peut aussi changer de carte physique au cours d’un remplacement ou d’une réaffectation. C’est l’une des raisons pour lesquelles une correspondance ARP dynamique ne doit pas être considérée comme une vérité éternelle.

L’adresse MAC n’est pas normalement routée de bout en bout à travers Internet. Un routeur retire l’en-tête Ethernet reçu, examine le paquet IP, sélectionne le prochain saut et encapsule le paquet dans une nouvelle trame pour l’interface de sortie. La nouvelle trame utilise les adresses MAC correspondant au lien suivant. Les adresses IP source et destination restent en principe inchangées lors d’un transfert IP ordinaire, sauf mécanismes supplémentaires tels que NAT.

### 1.3. Le rôle des couches L2 et L3

L’expression **L2/L3** fait référence à la relation entre la couche liaison et la couche réseau. Les commutateurs Ethernet utilisent principalement les adresses MAC pour transférer les trames dans un VLAN. Les routeurs utilisent les adresses IP et leur table de routage pour choisir le prochain saut vers un autre réseau.

Un VLAN définit un domaine de diffusion logique distinct. Deux équipements situés dans des VLAN différents ne reçoivent pas directement les broadcasts ARP l’un de l’autre. Pour communiquer entre deux VLAN, le trafic IP doit généralement passer par une fonction de routage inter-VLAN, assurée par un routeur ou un commutateur de couche 3. Chacun des segments concernés effectue sa résolution ARP propre.

```text
                 Même VLAN : 192.168.10.0/24

       PC-A                                      PC-B
  IP 192.168.10.25                          IP 192.168.10.40
  MAC AA-AA-AA-AA-AA-AA                     MAC BB-BB-BB-BB-BB-BB
       |                                            |
       +------------------+  +----------------------+
                          |  |
                    +----------------+
                    | Switch VLAN 10 |
                    +----------------+

  PC-A veut joindre PC-B :
  1. PC-A détermine que PC-B est local.
  2. PC-A cherche 192.168.10.40 dans son cache ARP.
  3. Si l'entrée manque, PC-A diffuse une requête ARP.
  4. PC-B répond avec sa MAC.
  5. PC-A envoie la trame Ethernet à la MAC de PC-B.
```

Le commutateur n’a pas besoin de comprendre l’adresse IP pour diffuser la requête ARP : au niveau Ethernet, la destination est l’adresse MAC broadcast `FF:FF:FF:FF:FF:FF`. Il apprend les adresses MAC source grâce aux trames reçues, puis les utilise pour transférer les trames unicast. Le rôle d’ARP est différent de celui de la table MAC du commutateur : ARP associe une adresse IPv4 à une adresse MAC dans le cache d’un hôte ou d’un routeur ; la table MAC associe une MAC à un port de commutateur et à un VLAN.

### 1.4. Algorithme général de résolution ARP

Le processus peut être compris comme une suite d’étapes. Les détails internes, les temporisateurs et le traitement des entrées varient selon le système d’exploitation, mais le principe reste stable.

1. **Décision de routage** : la pile IP compare l’adresse de destination aux préfixes connus et choisit l’interface de sortie et le prochain saut.
2. **Consultation du cache** : elle recherche une association ARP utilisable pour l’adresse IPv4 du prochain saut.
3. **Résolution nécessaire** : si aucune entrée ne permet de construire la trame, l’équipement place la résolution en attente et diffuse une requête ARP sur le domaine local concerné.
4. **Réception de la réponse** : le propriétaire de l’adresse IPv4 cible répond, habituellement en unicast vers l’équipement demandeur.
5. **Mise à jour du cache** : l’émetteur enregistre la correspondance IP–MAC selon les règles de son système.
6. **Transmission des données** : le paquet IP en attente peut être encapsulé dans une trame Ethernet avec la MAC résolue.
7. **Réutilisation** : tant que l’entrée est considérée valide, les paquets suivants peuvent utiliser cette correspondance sans effectuer une nouvelle requête ARP à chaque fois.

```text
+------------------------------+
| Application demande un envoi |
+---------------+--------------+
                |
                v
+------------------------------+
| La pile IP choisit la route   |
| et le prochain saut           |
+---------------+--------------+
                |
                v
+------------------------------+
| Le cache ARP contient-il une  |
| entrée utilisable ?           |
+-----------+------------------+
            |
       +----+----+
       |         |
      OUI       NON
       |         |
       v         v
+------------+  +----------------------+
| Utiliser   |  | Diffuser une requête |
| la MAC     |  | ARP sur le VLAN local|
+------+-----+  +----------+-----------+
       |                   |
       |                   v
       |          +----------------------+
       |          | Réponse ARP reçue ?  |
       |          +----------+-----------+
       |                     |
       |                     v
       |          +----------------------+
       |          | Enregistrer la MAC   |
       |          | dans le cache        |
       |          +----------+-----------+
       |                     |
       +----------+----------+
                  |
                  v
       +-----------------------+
       | Envoyer la trame L2   |
       | et le paquet IP       |
       +-----------------------+
```

Si aucune réponse n’arrive, la résolution échoue après un ou plusieurs essais et la communication ne peut pas utiliser ce prochain saut. Les symptômes visibles dépendent du système : attente, perte du premier paquet ou message d’erreur indiquant que l’hôte est inaccessible. Une absence de réponse ARP peut provenir d’une adresse incorrecte, d’un équipement hors ligne, d’un VLAN erroné, d’un problème physique ou d’un filtrage inhabituel.

### 1.5. Le format d’un paquet ARP

ARP est transporté directement dans une trame de liaison compatible, sans utiliser TCP ou UDP. Sur Ethernet II, le champ EtherType utilisé pour ARP est `0x0806`. Pour une résolution IPv4 sur Ethernet, le paquet ARP contient plusieurs champs qui identifient le type de réseau, la taille des adresses et la nature de l’opération.

| Champ | Signification | Valeur fréquente pour IPv4 sur Ethernet |
|---|---|---|
| HTYPE | Type matériel | `1` pour Ethernet |
| PTYPE | Type de protocole | `0x0800` pour IPv4 |
| HLEN | Longueur de l’adresse matérielle | `6` octets pour une MAC Ethernet de 48 bits |
| PLEN | Longueur de l’adresse de protocole | `4` octets pour IPv4 |
| OPER | Opération | `1` pour Request, `2` pour Reply |
| SHA | Sender Hardware Address | MAC de l’émetteur ARP |
| SPA | Sender Protocol Address | IPv4 de l’émetteur ARP |
| THA | Target Hardware Address | MAC de la cible, souvent inconnue dans une requête classique |
| TPA | Target Protocol Address | IPv4 recherchée |

Ces champs permettent au protocole d’être extensible à d’autres types d’adresses matérielles ou protocolaires, même si l’usage le plus courant en entreprise est la résolution d’IPv4 sur Ethernet.

Dans une requête typique de PC-A vers `192.168.10.40`, les champs peuvent indiquer l’adresse MAC source de PC-A, l’IPv4 de PC-A et l’IPv4 cible recherchée. Comme PC-A ne connaît pas encore la MAC de la cible, le champ THA est généralement inconnu ou nul dans ce type de requête. La trame Ethernet enveloppante est envoyée vers la MAC de broadcast.

La réponse indique généralement l’adresse MAC du propriétaire de l’IPv4 demandée. La réponse ARP est habituellement envoyée en unicast à la MAC du demandeur ; le format et les règles de traitement permettent toutefois plusieurs formes d’annonces et de mises à jour, dont certaines ne correspondent pas à une réponse classique provoquée par une requête.

### 1.6. Requête, réponse et broadcast

Une **requête ARP** demande : « Quelle adresse matérielle correspond à cette adresse IPv4 ? ». Dans le cas classique sur Ethernet, la requête est encapsulée dans une trame dont la MAC de destination est `FF:FF:FF:FF:FF:FF`. Tous les équipements du domaine de broadcast la reçoivent au niveau de la liaison, mais seuls les équipements concernés la traitent comme une demande pour leur adresse IP, selon leur configuration et leur pile réseau.

Une **réponse ARP** indique la correspondance IP–MAC connue. Elle est généralement envoyée en unicast vers l’équipement à l’origine de la requête. Le cache ARP est mis à jour afin d’éviter une requête répétée pour chaque paquet.

Un broadcast Ethernet est limité au domaine de couche 2 concerné. Un routeur ne relaie normalement pas une requête ARP broadcast vers un autre réseau. Cette limitation empêche qu’une demande ARP de chaque hôte se propage sur l’ensemble d’Internet et maintient la résolution au sein du lien ou VLAN approprié.

ARP n’est pas un protocole de découverte générale permettant de rechercher n’importe quelle machine de l’entreprise. Pour résoudre une destination située sur un autre sous-réseau, l’hôte contacte sa passerelle. Le routeur est chargé de transférer le paquet IP et, sur son interface de sortie, d’effectuer au besoin une autre résolution pour le prochain saut local.

### 1.7. Pourquoi une destination distante est résolue via la passerelle

Considérons un PC possédant les paramètres suivants :

- Adresse IP : `192.168.10.25`
- Masque : `255.255.255.0` (`/24`)
- Passerelle : `192.168.10.1`
- Destination IP : `192.168.20.50`

Le réseau local du PC est `192.168.10.0/24`. La destination `192.168.20.50` n’appartient pas à ce préfixe. Le PC consulte donc sa table de routage et choisit sa passerelle par défaut `192.168.10.1`. ARP est utilisé pour trouver la MAC de `192.168.10.1`, et non la MAC de `192.168.20.50`.

La trame Ethernet envoyée par le PC a comme adresse MAC de destination celle de la passerelle. À l’intérieur, le paquet IP a toujours comme adresse IP de destination `192.168.20.50`. Le routeur reçoit la trame, retire l’en-tête L2, consulte sa table de routage puis construit une nouvelle trame adaptée à son interface de sortie.

```text
 PC-A                        Routeur R1                  Serveur B
192.168.10.25                192.168.10.1                192.168.20.50
MAC AA                       MAC RR                       MAC BB
   |                             |                            |
   | ARP pour 192.168.10.1       |                            |
   |<----------------------------|                            |
   |                             |                            |
   | Trame L2 : dst MAC = RR     |                            |
   | Paquet IP : dst = .20.50    |                            |
   +---------------------------->|                            |
                                 | Route vers 192.168.20.0/24  |
                                 | ARP pour le prochain saut   |
                                 |---------------------------->| 
                                 | Trame L2 adaptée au lien   |
                                 +--------------------------->|
```

Ce comportement s’applique à chaque saut. Sur un réseau multi-routeurs, le paquet IP est transmis de routeur en routeur tandis que l’adresse MAC source et l’adresse MAC destination de la trame changent à chaque lien Ethernet traversé. Une capture de trames sur un seul segment ne montre donc pas nécessairement les adresses MAC utilisées sur les autres segments.

### 1.8. Le cache ARP

Effectuer une requête ARP avant chaque transmission serait inefficace. Les hôtes et routeurs maintiennent donc un **cache ARP** qui conserve des correspondances récemment apprises entre des adresses IPv4 et des adresses MAC.

Une entrée dynamique provient généralement du traitement des échanges ARP. Elle reste utilisable pendant une durée liée à l’implémentation, à l’état de l’entrée et au trafic observé. Lorsqu’elle expire ou n’est plus considérée valide, le système peut la supprimer ou tenter de la rafraîchir. Les détails exacts varient entre Windows, Linux, macOS, les routeurs et les équipements réseau.

Une entrée statique est configurée manuellement ou par une fonction de gestion. Elle peut rester présente jusqu’à sa suppression ou jusqu’à un changement de configuration, selon le système. Les entrées statiques peuvent être utiles dans des scénarios limités, mais elles deviennent difficiles à maintenir si elles sont multipliées sur un grand nombre d’équipements.

Les caches peuvent afficher différents états tels que l’entrée valide, incomplète, obsolète ou en cours de résolution. Les noms et la sémantique exacte des états dépendent du système. Une entrée « incomplete » signifie par exemple que l’adresse MAC recherchée n’a pas encore été résolue. Une entrée « stale » dans certains systèmes indique qu’une correspondance existe, mais qu’elle peut devoir être validée avant une utilisation ou une actualisation.

Le cache ARP n’est pas la table MAC d’un commutateur. Le cache ARP répond à la question « quelle MAC correspond à cette IPv4 ? ». La table MAC du commutateur répond plutôt à la question « sur quel port et dans quel VLAN ai-je appris cette MAC ? ». Le routeur ou l’hôte utilise l’association ARP pour créer la trame, tandis que le switch utilise son apprentissage MAC pour la transférer.

### 1.9. Entrées dynamiques et statiques

Les entrées dynamiques sont généralement préférées pour les postes et serveurs usuels, car elles s’adaptent aux changements de la topologie. En revanche, une modification non autorisée d’une association IP–MAC peut perturber la communication jusqu’à ce que l’entrée soit corrigée ou expirée.

Une entrée statique associe explicitement une IPv4 à une MAC. Elle peut être pertinente pour un besoin particulier, comme certains équipements anciens, des environnements de sécurité spécifiques ou une résolution fixe soigneusement contrôlée. Mais il ne faut pas utiliser des entrées statiques partout comme substitut à une conception réseau correcte : elles augmentent la charge d’exploitation et doivent être mises à jour lorsque le matériel ou l’adressage change.

Sur Cisco IOS classique, la configuration d’une entrée statique peut prendre une forme similaire à :

```cisco
arp 192.168.10.50 aabb.ccdd.eeff arpa
```

La syntaxe exacte dépend de la plateforme et du contexte. L’adresse MAC ci-dessus est un exemple fictif ; elle doit correspondre à l’équipement concerné. Une entrée incorrecte peut rendre un hôte inaccessible ou diriger le trafic vers la mauvaise interface. Il est donc nécessaire de documenter toute entrée statique et de prévoir une méthode de retrait.

### 1.10. ARP et DHCP : des rôles différents

DHCP attribue ou fournit les paramètres IP à un client, souvent une adresse IP, un masque, une passerelle et des serveurs DNS. ARP résout ensuite l’adresse de couche 2 nécessaire pour communiquer avec un prochain saut IPv4 sur Ethernet. Ces protocoles se complètent, mais ne font pas la même chose.

Un client peut avoir reçu correctement son adresse via DHCP et échouer malgré tout à communiquer si son VLAN est incorrect, si sa passerelle ne répond pas à ARP ou si une association ARP erronée est installée. Inversement, un échange ARP peut fonctionner entre deux équipements qui ont été configurés manuellement, même si aucun serveur DHCP n’est présent.

DHCP Snooping est une fonction de sécurité du commutateur qui observe les échanges DHCP et construit une base de liaisons entre adresse IP, adresse MAC, VLAN et port. Cette base peut ensuite être utilisée par Dynamic ARP Inspection pour vérifier si une requête ou une réponse ARP est cohérente avec les informations de liaison connues. DHCP n’authentifie pas intrinsèquement toute identité réseau ; les protections de couche 2 doivent donc être configurées correctement.

### 1.11. ARP gratuit et détection de conflit d’adresse

Un **Gratuitous ARP** (souvent abrégé GARP) désigne couramment une annonce ARP qu’un équipement envoie au sujet de sa propre adresse IPv4, plutôt que de répondre simplement à une requête ordinaire d’un autre hôte. Selon son format et son usage, cette annonce peut aider d’autres équipements à mettre à jour leurs caches, par exemple après le déplacement d’une adresse IP virtuelle entre deux équipements redondants.

Une annonce ARP spontanée ne constitue pas une garantie cryptographique de propriété. Puisque le mécanisme ARP classique n’authentifie pas cryptographiquement les annonces, un hôte malveillant peut tenter de diffuser une fausse association. Le même caractère ouvert qui rend ARP simple à déployer explique pourquoi il est vulnérable à l’usurpation dans un domaine de couche 2 insuffisamment protégé.

La détection de conflit d’adresse IPv4 fait l’objet de la RFC 5227. Les systèmes peuvent envoyer des sondes ARP avant d’utiliser une adresse, afin de vérifier si une autre machine semble déjà l’utiliser. Les comportements exacts dépendent de la pile du système d’exploitation et du mode d’attribution de l’adresse. Un conflit peut provoquer des pertes de connectivité intermittentes, des messages d’avertissement et des entrées ARP qui semblent changer entre plusieurs adresses MAC.

Il faut distinguer une annonce légitime liée à un basculement de haute disponibilité d’une usurpation malveillante. Dans les deux cas, les caches peuvent être mis à jour, mais l’intention et les conditions qui autorisent le changement sont différentes. La surveillance des événements, la documentation des adresses virtuelles et l’utilisation des mécanismes de protection L2 permettent de mieux distinguer les changements prévus des anomalies.

### 1.12. Proxy ARP

Le **Proxy ARP** est un mécanisme par lequel un routeur répond à une requête ARP destinée à une adresse IPv4 dont il n’est pas l’hôte final, lorsque ses règles de routage et sa configuration lui permettent de représenter cette destination. Il répond avec une adresse MAC locale, afin que l’émetteur envoie ensuite la trame au routeur. Celui-ci transfère le paquet IP vers la destination réelle.

Proxy ARP peut être utile dans certaines architectures anciennes ou dans des situations où les hôtes ont une compréhension limitée du routage. Il peut permettre à un hôte de communiquer avec une adresse qui semble être dans son réseau local, alors que le routeur sait atteindre cette adresse par une autre interface. Cependant, il ne doit pas être activé sans raison claire, car il peut masquer des erreurs de masque et rendre la topologie plus difficile à comprendre.

Dans le schéma suivant, PC-A pense que le serveur distant est sur le même réseau et envoie une requête ARP pour lui. Le routeur répond à la place du serveur, puis transfère le paquet au travers de sa fonction de routage.

```text
        Segment local A                         Segment distant B

   +--------+       +-----------------+          +--------+
   | PC-A   |-------| Routeur R1      |----------| Serveur|
   |        |       | Proxy ARP       |          |        |
   +--------+       +-----------------+          +--------+
       |                     |                       |
       | ARP: « Qui a         |                       |
       | l'IP du serveur ? »  |                       |
       |-------------------->|                       |
       |                     |                       |
       | Réponse ARP avec    |                       |
       | la MAC de R1        |                       |
       |<--------------------|                       |
       |                     |                       |
       | Trame vers MAC R1   | Route IP vers serveur |
       +-------------------->|---------------------->|
```

Proxy ARP ne transforme pas le routeur en commutateur et ne fait pas traverser le broadcast initial. Le routeur répond localement, puis effectue un transfert routé. Un hôte ordinaire et le serveur restent séparés par la frontière de couche 3.

Sur certaines versions Cisco IOS, Proxy ARP est activé par défaut sur les interfaces routées, mais ce comportement dépend de la plateforme et de la version. On peut le désactiver sur une interface avec `no ip proxy-arp` dans les contextes pris en charge. La bonne pratique consiste à confirmer l’état effectif et à décider en fonction du besoin, plutôt que de supposer qu’il est actif ou inactif partout.

### 1.13. ARP, commutation et routeur : ne pas confondre les tables

Trois tables sont souvent confondues par les débutants :

| Table | Question à laquelle elle répond | Exemple d’information |
|---|---|---|
| Cache ARP | Quelle MAC correspond à cette IPv4 sur le lien local ? | `192.168.10.25 → AA:AA:AA:AA:AA:AA` |
| Table MAC du switch | Sur quel port/VLAN se trouve cette MAC ? | `AA:AA:AA:AA:AA:AA → Gi1/0/5, VLAN 10` |
| Table de routage IP | Quelle route ou passerelle utiliser pour ce préfixe IP ? | `192.168.20.0/24 → via 192.168.10.1` |

Ces tables coopèrent mais n’ont pas la même fonction. Un routeur peut avoir une route correcte vers un réseau et ne pas disposer de l’entrée ARP nécessaire pour joindre le prochain saut. Un switch peut connaître le port associé à une MAC sans avoir besoin de connaître l’adresse IP associée. Enfin, un cache ARP peut contenir une association IP–MAC alors que la table de routage choisit un autre prochain saut pour une destination donnée.

Lors d’un dépannage, il est donc important de suivre la chaîne complète : route choisie, adresse IP du prochain saut, résolution ARP pour ce prochain saut, MAC associée, présence du port dans le bon VLAN et état du lien. Une erreur dans n’importe quelle partie peut bloquer le transfert.

### 1.14. ARP et IPv6 : différence importante

ARP est utilisé pour résoudre des adresses IPv4 sur les réseaux Ethernet compatibles. IPv6 n’utilise pas ARP. À la place, IPv6 utilise le **Neighbor Discovery Protocol (NDP)**, qui repose sur des messages ICMPv6, notamment Neighbor Solicitation et Neighbor Advertisement. NDP gère plus largement la découverte des voisins, la détection d’inaccessibilité, la détection de doublons d’adresses et d’autres fonctions IPv6.

Dans un réseau double pile, les équipements peuvent donc utiliser ARP pour IPv4 et NDP pour IPv6. Un cache ARP vide n’explique pas à lui seul une panne IPv6 ; il faut examiner la table des voisins IPv6, les messages ICMPv6, les règles de filtrage et la configuration des adresses IPv6.

Cette distinction compte également pour la sécurité. Dynamic ARP Inspection protège les échanges ARP IPv4 pris en charge par la fonction. Les réseaux IPv6 nécessitent des mécanismes de protection adaptés à NDP et aux annonces de routeur, selon la plateforme et l’architecture. Il ne faut pas supposer qu’une protection ARP IPv4 sécurise automatiquement IPv6.

> **Piège :** L’erreur la plus fréquente consiste à croire qu’un hôte résout toujours la MAC de l’adresse IP de destination finale. En réalité, il résout la MAC du prochain saut sélectionné par la table de routage. Pour une destination du même sous-réseau, le prochain saut est généralement l’hôte lui-même ; pour une destination distante, c’est généralement la passerelle. Autre piège : ARP ne traverse pas normalement les routeurs. Si un PC ne reçoit pas de réponse ARP, il faut d’abord vérifier le VLAN et le lien local, l’adresse recherchée et le prochain saut, puis seulement explorer les causes plus avancées.

```text
      RÉSOLUTION POUR UNE DESTINATION LOCALE

      PC-A 192.168.10.25/24
          |
          | Dest. IP = 192.168.10.40
          | ARP pour 192.168.10.40
          v
      PC-B 192.168.10.40/24

      RÉSOLUTION POUR UNE DESTINATION DISTANTE

      PC-A 192.168.10.25/24
          |
          | Dest. IP = 192.168.20.50
          | ARP pour la passerelle 192.168.10.1
          v
      Routeur 192.168.10.1
          |
          | Routage vers le réseau distant
          | nouvelle résolution L2 sur l'interface de sortie
          v
      Réseau de destination
```

---

## 2. Configuration et Pratique

### 2.1. Exemple de laboratoire

Le laboratoire utilise un commutateur de couche 2 et un routeur pour illustrer la résolution locale et la résolution de la passerelle. Les noms d’interfaces Cisco peuvent varier selon le modèle ; adaptez `GigabitEthernet0/0` et les ports de commutation aux équipements réels ou au simulateur.

| Équipement | Interface | Adresse | Fonction |
|---|---|---|---|
| PC-A | Carte Ethernet | `192.168.10.10/24` | Hôte du VLAN 10 |
| R1 | G0/0 | `192.168.10.1/24` | Passerelle du VLAN 10 |
| PC-B | Carte Ethernet | `192.168.10.20/24` | Second hôte du VLAN 10 |
| PC-C | Carte Ethernet | `192.168.20.20/24` | Hôte d’un autre réseau, si routage configuré |

PC-A et PC-B partagent le même sous-réseau. PC-A peut les joindre directement au niveau IP et utilisera ARP pour résoudre la MAC de PC-B. Pour communiquer avec PC-C, PC-A doit utiliser la passerelle `192.168.10.1`, qui doit elle-même posséder une route vers `192.168.20.0/24`.

### 2.2. Configuration minimale de l’interface Cisco

Une interface routée Cisco IOS peut être configurée comme suit :

```cisco
hostname R1

interface GigabitEthernet0/0
 description LAN_VLAN10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
```

`hostname` définit le nom de l’équipement. `interface` sélectionne l’interface physique ou logique. `ip address` attribue l’adresse IPv4 et le masque. `no shutdown` active administrativement l’interface. La configuration n’indique pas à elle seule que le câble, le port du switch et le VLAN sont corrects ; ces éléments doivent être contrôlés dans l’état opérationnel.

Si le routeur raccorde un réseau par une interface physique simple, celle-ci doit appartenir au segment de couche 2 correspondant. Si plusieurs VLAN passent sur un lien trunk vers un routeur, une architecture de sous-interfaces 802.1Q peut être nécessaire. Le laboratoire minimal ne requiert pas cette configuration avancée, mais il faut conserver une correspondance cohérente entre l’interface IP, le VLAN et le sous-réseau.

Pour vérifier l’état de l’interface :

```cisco
show ip interface brief
show interfaces GigabitEthernet0/0
```

L’interface doit être opérationnelle et posséder l’adresse prévue. Si elle est « administratively down », il faut examiner la configuration et utiliser `no shutdown` si cela correspond au plan de changement. Si elle est « down/down », la cause peut être physique ou liée à l’interface distante.

### 2.3. Consulter la table ARP sur Cisco

Les commandes suivantes sont courantes sur Cisco IOS/IOS XE, mais la disponibilité exacte dépend de la plateforme :

```cisco
show ip arp
show arp
```

La sortie affiche généralement l’adresse IP, le temps écoulé depuis l’apprentissage, l’adresse matérielle et l’interface associée. Les entrées peuvent apparaître comme dynamiques ou statiques selon la façon dont elles ont été créées.

Après qu’un équipement a tenté de joindre un voisin local, il est possible que la correspondance apparaisse dans la table. Si aucune entrée ne se trouve dans le cache, cela ne prouve pas automatiquement qu’il existe une panne : l’équipement peut ne pas avoir encore tenté de communiquer, ou l’entrée peut avoir expiré. Il faut générer un trafic de test adapté puis consulter à nouveau le cache.

Pour vérifier une entrée précise, recherchez l’adresse IP concernée et comparez la MAC affichée avec les informations attendues. Si la MAC change de façon inattendue pour une même adresse, il faut déterminer s’il existe une redondance légitime, un remplacement de matériel, un conflit IP ou un problème de sécurité.

### 2.4. Générer un test et observer la résolution

Depuis R1, PC-A ou une interface de test, un ping vers un voisin du même sous-réseau peut provoquer une résolution ARP si aucune association valide n’existe. Sur Cisco, le test prend une forme similaire à :

```cisco
ping 192.168.10.20
show ip arp
```

L’adresse `192.168.10.20` doit correspondre à PC-B dans le scénario. Si le ping échoue, il faut vérifier les adresses, les masques, les connexions et le VLAN. La commande ping utilise ICMP, mais le mécanisme ARP s’exécute en amont lorsqu’il faut construire la trame locale.

Sur un poste Windows, on peut examiner le cache avec :

```text
ipconfig /all
arp -a
ping 192.168.10.20
arp -a
```

`ipconfig /all` affiche les paramètres IP locaux, notamment l’adresse, le masque et la passerelle. `arp -a` affiche les associations présentes dans le cache. Le premier affichage peut ne pas contenir le voisin ; après le ping, l’entrée peut apparaître si la résolution a réussi.

Sur un poste Linux récent, les commandes usuelles sont :

```bash
ip address show
ip route show
ip neigh show
ping -c 3 192.168.10.20
ip neigh show
```

`ip neigh` affiche les informations de voisinage du noyau, y compris les associations IPv4 gérées par ARP. Les états affichés peuvent inclure `REACHABLE`, `STALE`, `DELAY`, `PROBE` ou `INCOMPLETE` selon la situation. Leur sémantique est propre à l’implémentation ; il ne faut pas supposer qu’ils se présentent à l’identique sur tous les systèmes.

### 2.5. Effacer une entrée ARP : précautions

Sur les systèmes Cisco compatibles, la commande suivante permet généralement de supprimer les entrées ARP dynamiques :

```cisco
clear arp-cache
```

Certaines versions proposent aussi des commandes ciblées par interface. Il faut consulter l’aide contextuelle (`clear arp ?`) sur l’équipement avant de lancer une commande en production.

Sur Windows, `arp -d *` peut supprimer des entrées du cache selon les droits et la version du système. Sous Linux, `ip neigh flush` permet de supprimer des entrées de voisinage, mais il est préférable de préciser l’interface et le périmètre si l’opération est nécessaire. Toute suppression peut provoquer une nouvelle série de requêtes ARP lors des communications suivantes.

Effacer le cache ne corrige pas à lui seul la cause sous-jacente. Si une fausse annonce ARP est toujours diffusée ou si l’équipement est branché sur le mauvais VLAN, le problème peut réapparaître immédiatement. Dans un réseau de production, il faut collecter les observations avant de supprimer les entrées, car le cache peut fournir une preuve utile pour le dépannage.

### 2.6. Configurer une entrée ARP statique : cas d’usage limité

Une entrée statique force une association IP–MAC au lieu de dépendre uniquement de l’apprentissage dynamique. Sur Cisco IOS classique, une syntaxe possible est :

```cisco
configure terminal
arp 192.168.10.20 aabb.ccdd.eeff arpa
end
show ip arp
```

Cette configuration est illustrative. Remplacez `aabb.ccdd.eeff` par la MAC réelle de l’équipement et vérifiez la syntaxe prise en charge sur la version utilisée. Une entrée incorrecte peut empêcher la communication, même si l’hôte est opérationnel. Elle doit donc être documentée, testée et supprimée lorsqu’elle n’est plus nécessaire.

Les entrées statiques conviennent mieux à des cas limités qu’à une flotte importante de postes. Elles ne protègent pas à elles seules tous les échanges ARP du segment et n’empêchent pas nécessairement un autre équipement de provoquer une perturbation ailleurs dans le domaine de couche 2. Pour lutter contre l’usurpation à l’échelle d’un VLAN, les mécanismes de sécurité du commutateur sont généralement plus adaptés.

Pour retirer une entrée statique, la syntaxe peut utiliser la forme négative de la commande ARP selon la plateforme, par exemple `no arp 192.168.10.20 aabb.ccdd.eeff arpa`. Vérifiez toujours la commande effective avec l’aide contextuelle avant d’effectuer le retrait.

### 2.7. Contrôler le VLAN et la table MAC du commutateur

Si ARP échoue entre deux appareils qui devraient se trouver dans le même sous-réseau, contrôlez d’abord que les ports appartiennent au bon VLAN et que les liaisons sont opérationnelles. Les commandes Cisco courantes incluent :

```cisco
show vlan brief
show interfaces status
show mac address-table dynamic
```

`show vlan brief` affiche les VLAN et les ports associés selon la plateforme. `show interfaces status` donne un aperçu de l’état des ports. `show mac address-table dynamic` permet de déterminer sur quel port et dans quel VLAN le commutateur a appris une adresse MAC.

Une requête ARP broadcast doit rester à l’intérieur du VLAN concerné, en suivant les règles de commutation et les trunks autorisés. Si PC-A est dans le VLAN 10 et PC-B est accidentellement dans le VLAN 20, ils ne recevront pas directement leurs requêtes ARP, même si leurs adresses paraissent appartenir au même sous-réseau. Ce type de désaccord entre plan IP et configuration L2 est une cause fréquente de panne.

Pour les trunks, il faut examiner quels VLAN sont transportés et s’assurer que le VLAN attendu est autorisé de bout en bout. Les commandes précises diffèrent selon la famille de commutateurs, mais `show interfaces trunk` est couramment disponible sur Cisco IOS de campus. N’ajoutez pas un VLAN au trunk sans vérifier le plan de changement et les conséquences sur les autres chemins.

### 2.8. Proxy ARP sur Cisco IOS

Sur certaines plateformes Cisco IOS/IOS XE, Proxy ARP peut être activé par défaut sur les interfaces routées. Pour désactiver Proxy ARP sur une interface lorsque la conception du réseau le permet :

```cisco
configure terminal
interface GigabitEthernet0/0
 no ip proxy-arp
end
```

La commande désactive la réponse Proxy ARP sur cette interface sur les plateformes qui la prennent en charge. Le comportement exact doit être vérifié avec la documentation du logiciel et la configuration effective. Si un service existant dépend explicitement de Proxy ARP, sa désactivation peut interrompre la communication ; il faut donc étudier la topologie avant le changement.

Une désactivation globale existe sur certaines versions et peut utiliser une commande telle que `ip arp proxy disable`, mais la syntaxe et la portée varient. Ne copiez pas une commande globale dans un réseau de production sans vérifier le guide correspondant à la version IOS/IOS XE déployée.

La décision ne doit pas être prise uniquement parce que Proxy ARP semble inhabituel. Il faut déterminer s’il existe un besoin opérationnel documenté, si les hôtes ont les bons masques et passerelles, et si la désactivation met en évidence une erreur de conception. Dans la plupart des réseaux modernes, un adressage clair et un routage explicite sont préférables à une dépendance implicite à Proxy ARP.

### 2.9. Sécuriser ARP avec DHCP Snooping et Dynamic ARP Inspection

ARP classique ne fournit pas une authentification cryptographique de l’identité qui annonce une association IP–MAC. Un commutateur de couche 2 peut donc être utilisé pour limiter les fausses annonces, lorsque les fonctions appropriées sont disponibles.

**DHCP Snooping** inspecte le trafic DHCP pour constituer une base de liaisons apprises. Il permet aussi de distinguer les ports de confiance, généralement ceux connectés au serveur DHCP légitime ou aux liaisons d’infrastructure prévues, des ports non fiables, généralement les ports d’accès aux utilisateurs. Une configuration incorrecte de la confiance peut empêcher les clients d’obtenir une adresse, ou laisser passer des serveurs DHCP indésirables.

**Dynamic ARP Inspection (DAI)** examine les requêtes et réponses ARP reçues sur les ports non fiables et vérifie leur cohérence avec une base de liaisons telle que celle construite par DHCP Snooping. Les paquets invalides peuvent être rejetés. Les hôtes à IP statique nécessitent souvent des règles adaptées, par exemple des listes de contrôle ARP lorsque la plateforme le permet.

Exemple schématique de configuration sur une famille de commutateurs Cisco compatible :

```cisco
ip dhcp snooping
ip dhcp snooping vlan 10
ip arp inspection vlan 10

interface GigabitEthernet1/0/24
 description UPLINK_VERS_INFRASTRUCTURE
 ip dhcp snooping trust
 ip arp inspection trust

interface GigabitEthernet1/0/5
 description PORT_UTILISATEUR
 ! Port d'accès normalement laissé non fiable
```

Cet exemple est un point de départ pédagogique et doit être adapté. Le port d’uplink ne doit être marqué trusted que si son rôle et le chemin DHCP/ARP le justifient. Les ports utilisateurs doivent rester non fiables pour que les contrôles puissent s’appliquer. Avant d’activer DAI, vérifiez la prise en charge, les VLAN concernés, les équipements à IP statique et la base DHCP Snooping. Un paramétrage incorrect peut bloquer des échanges légitimes.

### 2.10. Procédure de validation après configuration

Une validation structurée évite de conclure trop tôt qu’ARP fonctionne parce qu’une seule commande affiche une entrée. Après modification, contrôlez les interfaces, le VLAN, l’adresse IP et la passerelle, puis générez le trafic de test et observez les tables.

```cisco
show ip interface brief
show ip arp
show vlan brief
show mac address-table dynamic
show ip route
ping 192.168.10.20
```

Les sorties doivent être cohérentes avec le plan d’adressage. L’adresse MAC vue dans le cache ARP doit correspondre à l’équipement attendu, tandis que la table MAC du commutateur doit indiquer un port correct dans le VLAN adéquat. Une route vers la destination ou la passerelle doit également exister côté IP.

Pour un changement de sécurité tel que l’activation de DAI ou DHCP Snooping, ajoutez les vérifications propres à la fonctionnalité, les compteurs de paquets rejetés et les journaux disponibles. Effectuez si possible l’opération sur une plage de test avant le déploiement généralisé. Consignez les commandes exécutées, le résultat attendu et une méthode de retour arrière.

> **Astuce :** Pour une première analyse, vérifie dans cet ordre : `show ip interface brief`, `show ip route`, `show ip arp`, puis la configuration VLAN et la table MAC du commutateur. Commence par répondre à trois questions : quelle interface sortante est choisie, quelle adresse IP constitue le prochain saut, et quelle MAC est associée à ce prochain saut ? Cette méthode sépare une erreur de routage d’un échec de résolution ARP et d’un problème de commutation L2.

---

## 3. Dépannage et Sécurité

### 3.1. Symptôme : l’hôte ne joint pas un voisin local

Si deux machines du même sous-réseau ne communiquent pas, commencez par vérifier leurs adresses IP, leurs masques et leurs états de lien. Une adresse ou un masque incohérent peut amener un hôte à considérer à tort une destination comme distante ou locale.

Ensuite, vérifiez le VLAN de chaque port sur le commutateur. Même si les adresses IP semblent correctes, des ports placés dans des VLAN différents ne partagent pas le même domaine ARP. Il faut aussi contrôler le trunk si les appareils sont raccordés à des commutateurs différents.

Enfin, examinez le cache ARP. Si aucune entrée n’apparaît après un essai de communication, une requête peut avoir été envoyée sans réponse. Vérifiez si la machine cible est allumée, si son interface fonctionne, si elle utilise l’adresse attendue et si un outil de capture montre la requête ARP. Une capture permet de séparer la requête qui ne sort pas de l’interface, la requête qui n’atteint pas le segment cible et l’absence de réponse de la cible.

### 3.2. Symptôme : les destinations distantes sont inaccessibles

Si le PC joint ses voisins du même sous-réseau mais pas les autres réseaux, il faut vérifier la passerelle par défaut et la table de routage. Le PC doit résoudre la MAC de la passerelle, et le routeur doit posséder une route vers la destination et une route de retour appropriée.

Sur le PC, vérifiez l’adresse IP, le masque et la passerelle. Sur le routeur, contrôlez que l’interface de sortie est opérationnelle, que son adresse IP correspond au sous-réseau local et que les routes sont présentes. Ensuite, examinez ARP sur le segment concerné pour confirmer que le routeur peut résoudre le prochain saut.

Un cache ARP correct pour la passerelle prouve seulement que l’adresse IP de cette passerelle a été associée à une MAC locale. Cela ne prouve pas que la route distante existe, que le prochain routeur fonctionne ou que le chemin de retour est disponible. Le dépannage doit suivre chaque couche dans l’ordre.

### 3.3. Symptôme : la correspondance IP–MAC change régulièrement

Une adresse IPv4 qui apparaît alternativement avec plusieurs adresses MAC peut avoir plusieurs causes. Il peut s’agir d’une adresse virtuelle de haute disponibilité, d’un basculement de serveur, d’un changement de carte, d’une mauvaise configuration ou d’une usurpation ARP.

Avant de conclure à une attaque, vérifiez si l’adresse est associée à une passerelle redondante ou à un équipement qui migre entre ports. Consultez le plan d’adressage, les informations de haute disponibilité, les événements du switch et les journaux d’administration. Une modification planifiée peut expliquer un changement de MAC si le service utilise une adresse IP virtuelle.

Si aucune explication légitime n’existe, recherchez les annonces ARP provenant de ports inattendus et les événements d’inspection ARP. Conservez les preuves utiles avant d’effacer les caches. La suppression d’une entrée peut rétablir temporairement un état normal, mais ne neutralise pas l’émetteur d’annonces falsifiées.

### 3.4. Symptôme : une entrée ARP est présente, mais le trafic échoue

Une entrée ARP ne garantit pas que le chemin soit opérationnel. La MAC peut être incorrecte, l’équipement correspondant peut être hors ligne, la table MAC du switch peut pointer vers un port erroné ou le VLAN peut ne pas être celui attendu. Il est aussi possible que la résolution soit correcte mais que le filtrage IP, le routage ou l’application bloque ensuite le trafic.

Comparez l’adresse MAC du cache ARP aux informations de l’équipement cible. Vérifiez dans la table MAC sur quel port la MAC est apprise et dans quel VLAN. Regardez les compteurs d’erreurs des interfaces, les états des liens et les politiques de filtrage. Si la MAC est associée à un port inhabituel, déterminez si l’équipement a été déplacé ou si le port est utilisé par un hôte non autorisé.

Le diagnostic doit rester méthodique : ne modifiez pas à la fois les entrées ARP, le VLAN et les paramètres IP. Effectuez une seule modification contrôlée, vérifiez le résultat, puis continuez.

### 3.5. Conflit d’adresses IP

Un conflit IPv4 survient lorsque plusieurs équipements utilisent simultanément la même adresse dans un domaine où cette adresse est supposée unique. Les symptômes peuvent comprendre des pertes intermittentes, des sessions qui se coupent, des entrées ARP qui alternent entre deux MAC et des avertissements du système d’exploitation.

Les causes fréquentes sont une configuration statique située dans une plage DHCP, une réservation incorrecte, un clonage de machine virtuelle, une erreur de migration ou un équipement oublié qui utilise une ancienne adresse. Le conflit ne se résout pas forcément en vidant le cache : tant que les deux équipements utilisent la même IPv4, une nouvelle résolution peut produire une nouvelle association erronée.

Il faut identifier les deux équipements, attribuer des adresses uniques selon le plan d’adressage et corriger la configuration DHCP ou statique. Les journaux du serveur DHCP, la base de réservation, la table MAC du switch et l’observation des annonces ARP peuvent aider à trouver le port où se trouve chaque équipement. Pour les environnements gérés, un système IPAM réduit les risques de réutilisation accidentelle.

### 3.6. ARP spoofing et ARP poisoning

**ARP spoofing** désigne l’envoi de messages ARP falsifiés destinés à faire croire qu’une adresse IPv4 correspond à une adresse MAC contrôlée par un attaquant. L’attaque est possible parce que le mécanisme ARP classique ne signe pas cryptographiquement les correspondances annoncées. Une machine peut accepter des informations fausses selon les règles de sa pile réseau, et l’attaquant peut essayer de faire pointer la passerelle ou l’adresse de la victime vers sa propre MAC.

Dans une attaque d’interception de type *man-in-the-middle*, l’attaquant tente de convaincre la victime que la MAC de la passerelle est la sienne, et de convaincre la passerelle que la MAC de la victime est la sienne. Si le trafic circule alors par l’attaquant et que celui-ci relaie les paquets, il peut potentiellement observer ou modifier du trafic non suffisamment protégé. Le chiffrement applicatif réduit certaines possibilités d’exploitation du contenu, mais ne garantit pas à lui seul l’absence de déni de service ou de manipulation du routage local.

Une attaque peut aussi viser le déni de service : l’attaquant annonce une correspondance incorrecte qui envoie les paquets vers un appareil qui ne les relaie pas. Dans ce cas, le trafic est simplement perdu. Les symptômes comprennent des interruptions soudaines, des changements de MAC associés à la passerelle et des anomalies ARP sur un même VLAN.

La réponse opérationnelle doit combiner prévention et investigation. Limitez les ports et appareils autorisés, activez DHCP Snooping et Dynamic ARP Inspection lorsque la plateforme et l’architecture le permettent, surveillez les changements d’association et séparez les domaines de diffusion. Les adresses IP statiques doivent être prises en compte dans les règles d’inspection, faute de quoi les paquets légitimes pourraient être rejetés.

### 3.7. Dynamic ARP Inspection : principe et limites

DAI vérifie les messages ARP reçus sur les interfaces non fiables en les comparant à des informations de liaison jugées valides, souvent issues de DHCP Snooping. Les messages considérés invalides sont rejetés avant d’être transmis au domaine de commutation. Selon la plateforme, des mécanismes complémentaires permettent de vérifier les paquets pour des équipements statiques.

DAI ne fournit pas une défense universelle. Il protège les VLAN et interfaces configurés, sur les commutateurs qui prennent en charge cette fonctionnalité, et selon la qualité de la base de liaisons. Un lien marqué à tort comme trusted peut laisser passer des annonces sans la même vérification. Un environnement comportant de nombreuses adresses statiques nécessite une politique appropriée. Un commutateur non couvert par le contrôle peut laisser subsister des chemins d’attaque dans le domaine de couche 2.

Les compteurs et les journaux de rejet doivent être observés après l’activation. Une hausse des rejets peut indiquer une attaque, mais aussi une incohérence de configuration, une base DHCP incomplète ou des hôtes statiques qui ne figurent pas dans les règles. Il faut donc interpréter les alertes avec la topologie et l’inventaire des appareils.

### 3.8. Bonnes pratiques de sécurité L2/L3

La première mesure consiste à réduire les domaines de diffusion à des tailles adaptées. Une segmentation par VLAN limite la portée des requêtes ARP et des annonces d’un hôte. La segmentation seule ne filtre pas automatiquement toutes les attaques à l’intérieur d’un VLAN, mais elle réduit la portée d’un incident.

La deuxième mesure consiste à activer les fonctions d’inspection et de surveillance disponibles, en les testant dans une zone pilote. DHCP Snooping, Dynamic ARP Inspection et les contrôles d’accès aux ports peuvent réduire l’exposition aux équipements non autorisés, à condition d’être correctement configurés.

La troisième mesure consiste à maintenir un plan d’adressage documenté. Les adresses statiques, les réservations DHCP, les passerelles virtuelles et les équipements d’infrastructure doivent être identifiés. Un plan à jour aide à distinguer une annonce légitime d’une association inattendue.

La quatrième mesure consiste à surveiller les événements. Les changements d’association IP–MAC, les conflits IP, les rejets DAI et les modifications de configuration doivent être examinés lorsqu’ils sortent du comportement normal. Enfin, les accès d’administration des commutateurs et des routeurs doivent être protégés, car une compromission du plan d’administration peut contourner ou désactiver les défenses de couche 2.

> **Danger :** ARP classique n’authentifie pas cryptographiquement la correspondance IP–MAC. Sur un VLAN insuffisamment protégé, un appareil malveillant peut tenter de modifier le cache ARP d’autres équipements, intercepter une partie du trafic ou provoquer une perte de connectivité. Ne traite pas une entrée ARP comme une preuve d’identité : vérifie les associations anormales, limite les ports accessibles, configure DHCP Snooping et Dynamic ARP Inspection lorsque cela convient, et prends en compte les hôtes à IP statique. Toute activation de protection doit être testée, car une configuration de confiance erronée ou une base de liaisons incomplète peut aussi bloquer le trafic légitime.

### 3.9. Fiche de dépannage rapide

| Observation | Hypothèse à vérifier | Commandes ou actions utiles |
|---|---|---|
| Aucune entrée ARP après un ping local | La requête ne part pas, la cible ne répond pas, mauvais VLAN ou lien défaillant | `show ip arp`, `arp -a`, `ip neigh`, capture de paquets |
| L’hôte joint le LAN mais pas un réseau distant | Passerelle, route ou chemin retour incorrect | `ip route`, `show ip route`, ping de passerelle |
| Plusieurs MAC associées successivement à une IP | Conflit, redondance légitime, mobilité ou spoofing | Cache ARP, table MAC, journaux, capture ARP |
| Une MAC est apprise sur le mauvais port/VLAN | Câblage, VLAN, déplacement ou appareil inattendu | `show mac address-table`, `show vlan brief` |
| ARP fonctionne mais les applications échouent | Problème au-dessus d’ARP : routage, ACL, DNS, service ou MTU | Ping/trace, routes, ACL, logs applicatifs |
| Après activation de DAI, des clients sont bloqués | Base DHCP Snooping ou ports trusted mal configurés, IP statiques non déclarées | Vérifier bindings, VLAN, compteurs DAI et règles ARP ACL |

Cette table est un aide-mémoire. Les observations doivent être confirmées par plusieurs sources : un message d’erreur ou une seule entrée de cache ne suffit pas à établir la cause racine.

### 3.10. Limites du protocole et pratiques d’exploitation

ARP est simple et largement pris en charge, mais il a été conçu dans un environnement où les participants d’un même segment étaient supposés coopérer. Sa simplicité n’inclut pas de preuve cryptographique qu’un expéditeur est autorisé à annoncer une adresse IP. Les contrôles modernes s’effectuent donc souvent au niveau du commutateur, avec des bases de correspondances et une politique de confiance.

En exploitation, il est utile de connaître les commandes d’observation avant de modifier quoi que ce soit. `show ip arp`, `show mac address-table`, `show vlan brief`, `show ip route` et l’examen des interfaces forment une base de diagnostic Cisco. Sur les postes, `arp -a` ou `ip neigh show` permettent de vérifier la vision locale du système. Les outils de capture peuvent confirmer le type de requête, les champs IP/MAC et la direction des réponses.

Les commandes de débogage doivent être utilisées avec prudence sur des équipements chargés, car elles peuvent générer un volume élevé de messages. Il est préférable de commencer par les états, les compteurs et les journaux, puis d’effectuer une capture ciblée si nécessaire. Sur un réseau de production, consignez les observations et utilisez une procédure de changement avec validation et retour arrière.

## Points à retenir

- **ARP associe une adresse IPv4 à une adresse MAC sur le lien local.** Il intervient après la décision de routage et ne choisit pas la route ni la passerelle.
- **Pour une destination distante, l’hôte résout la MAC du prochain saut, généralement la passerelle.** L’adresse IP de destination reste celle de l’hôte final, tandis que les adresses MAC changent à chaque lien Ethernet routé.
- **Le cache ARP, la table MAC du commutateur et la table de routage IP sont trois tables distinctes.** Le dépannage doit examiner la route, le voisin ARP, le VLAN, la MAC et le port de commutation.
- **Le Proxy ARP permet à un routeur de répondre au nom d’une autre adresse IP, mais doit être justifié par la conception.** Un adressage et un routage explicites sont généralement plus simples à maintenir.
- **ARP classique est vulnérable à l’usurpation.** La segmentation, DHCP Snooping, Dynamic ARP Inspection, la surveillance et la documentation réduisent les risques, sans remplacer une configuration rigoureuse.

## Références techniques

- [RFC 826 — An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826.html)
- [RFC 5227 — IPv4 Address Conflict Detection](https://www.rfc-editor.org/rfc/rfc5227.html)
- [RFC 1027 — Using ARP to Implement Transparent Subnet Gateways (Proxy ARP)](https://www.rfc-editor.org/rfc/rfc1027.html)
- [Cisco — Address Resolution Protocol, IP Addressing Configuration Guide](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_arp-config-arp-0.html)
- [Cisco — Dynamic ARP Inspection Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/sec-crypto/fhs-sisf/fhs-and-sisf-configuration-guide/dynamic-arp-inspection.html)
