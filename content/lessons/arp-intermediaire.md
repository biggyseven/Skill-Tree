# ARP & résolution L2/L3 - Intermédiaire

**Niveau :** Intermédiaire

Le protocole Address Resolution Protocol (ARP) assure la correspondance entre une adresse IPv4 et une adresse de couche liaison, le plus souvent une adresse MAC Ethernet de 48 bits. Il occupe une position charnière dans les réseaux IPv4 : la couche réseau identifie une destination avec une adresse IP, tandis que la couche Ethernet doit connaître l’adresse MAC du prochain saut pour construire la trame. ARP résout cette différence de représentation sur un segment de couche 2. Il ne choisit pas la route IP et ne transporte pas les paquets applicatifs ; il fournit une information de voisinage nécessaire à leur encapsulation locale.

ARP a été décrit dans la RFC 826, publiée en 1982. Le protocole est antérieur à de nombreuses fonctions de commutation, de sécurité et de virtualisation utilisées aujourd’hui, mais son mécanisme de base reste présent dans les réseaux IPv4 Ethernet. Des textes complémentaires, dont la RFC 5227, décrivent la détection de conflits d’adresses IPv4 et l’usage d’ARP Probe et d’ARP Announcement. Les implémentations modernes peuvent ajouter des vérifications et des mécanismes de protection, mais il ne faut pas attribuer au protocole ARP de base une authentification cryptographique qu’il ne fournit pas.

La résolution ARP est locale au domaine de diffusion de couche 2. Un routeur n’achemine pas une requête ARP d’un VLAN vers un autre comme il le ferait pour un paquet IP routable. Lorsqu’un hôte veut joindre une adresse hors de son sous-réseau, il résout normalement l’adresse MAC de sa passerelle par défaut, et non celle de la destination IP finale. Le routeur effectue ensuite une nouvelle décision de routage et, sur le réseau de sortie, résout au besoin l’adresse MAC du prochain saut. Cette distinction entre destination IP et prochain saut Ethernet est fondamentale pour diagnostiquer les problèmes de connectivité.

À un niveau intermédiaire, l’objectif est de comprendre non seulement la requête et la réponse ARP, mais aussi les caches, les temporisations, les comportements d’apprentissage, le Proxy ARP, les annonces gratuites, les conflits d’adresses, la segmentation VLAN et les conséquences sur le dépannage. Les administrateurs doivent également connaître les limites de sécurité d’ARP et les contrôles disponibles sur les commutateurs, notamment DHCP Snooping et Dynamic ARP Inspection (DAI), sans supposer que ces fonctions sont activées par défaut ou identiques sur toutes les plateformes.

> **Analogie** : Imagine un grand immeuble dans lequel les numéros d’appartement représentent les adresses IP et les badges physiques des résidents représentent les adresses MAC. Le service de distribution sait à quel appartement un colis doit arriver, mais le personnel présent dans un couloir doit aussi savoir à quelle porte remettre le colis. Si le destinataire est dans le même couloir, le personnel peut demander à haute voix : « Qui occupe l’appartement 12 ? » La personne concernée répond avec son identité et le badge associé à sa porte. Le demandeur mémorise temporairement cette association pour éviter de poser la même question à chaque livraison.
>
> Si le destinataire habite dans un autre bâtiment, le livreur ne cherche pas le badge de l’appartement final dans son propre couloir. Il remet le colis au concierge qui dessert la sortie, puis ce concierge l’achemine vers l’autre bâtiment. Dans le réseau IP, ce concierge correspond à la passerelle : l’hôte résout la MAC de la passerelle, alors que les routeurs successifs réalisent les résolutions locales nécessaires sur leurs propres liens.
>
> Un cache ARP ressemble au carnet temporaire du personnel. Il accélère les livraisons, mais une entrée peut devenir périmée si un résident change de badge, si un équipement est remplacé ou si une adresse IP est réattribuée. ARP de base ne dispose pas d’un service central garantissant que toute réponse est honnête. Un individu malveillant pourrait annoncer que le badge d’un autre résident lui appartient et détourner ainsi le colis. C’est l’analogie d’un empoisonnement ARP : le problème n’est pas seulement de trouver une correspondance, mais de faire confiance à la correspondance reçue.


## 1. La théorie et les algorithmes

### 1.1. Place d’ARP dans la pile réseau

Dans un réseau IPv4 sur Ethernet, les couches répondent à des questions différentes. IP détermine l’adresse logique de destination et, au niveau du routeur, choisit le prochain saut. Ethernet encapsule ensuite le paquet IP dans une trame dont l’adresse MAC source correspond à l’interface émettrice et dont l’adresse MAC destination correspond au prochain équipement sur le lien local.

Les adresses IP et MAC ne sont pas interchangeables :

| Élément | Couche principalement concernée | Rôle | Exemple |
|---|---|---|---|
| Adresse IPv4 | Couche 3 | Identifie une interface dans un plan d’adressage IP | `192.0.2.25` |
| Adresse MAC Ethernet | Couche 2 | Identifie une interface sur un segment Ethernet | `00:11:22:33:44:55` |
| Adresse réseau | Couche 3 | Identifie un préfixe IP | `192.0.2.0/24` |
| Adresse de diffusion IPv4 | Couche 3 | Cible les hôtes du sous-réseau IPv4 concerné | `192.0.2.255` pour `/24` |
| MAC de diffusion Ethernet | Couche 2 | Diffusion de trame sur le domaine L2 | `ff:ff:ff:ff:ff:ff` |
| Passerelle par défaut | Couche 3 | Prochain saut de l’hôte pour les destinations hors lien | `192.0.2.1` |

ARP résout une adresse de protocole IPv4 en adresse matérielle utilisable par la couche liaison. Sur Ethernet conventionnel, une requête ARP est envoyée dans une trame de diffusion dont la MAC destination est `ff:ff:ff:ff:ff:ff`. Tous les équipements du même domaine de diffusion peuvent recevoir la trame, même si un seul possède normalement l’adresse IPv4 recherchée.

ARP ne traverse pas directement les routeurs. Les routeurs terminent le domaine de couche 2 d’un côté, prennent une décision de routage au niveau IP, puis émettent une nouvelle trame sur le lien de sortie. Cette trame possède une adresse MAC source liée à l’interface de sortie et une adresse MAC destination liée au prochain saut sur ce réseau.

Il existe des mécanismes particuliers, comme Proxy ARP, dans lesquels un routeur répond à une requête ARP pour le compte d’une destination qu’il sait atteindre. Cela ne signifie pas que la requête a été routée comme une diffusion L2 : le routeur répond sur le segment où la demande a été reçue.

### 1.2. Décision préalable : la destination est-elle locale ?

Avant de demander une résolution ARP, l’hôte consulte sa configuration IPv4 et décide, à l’aide du masque ou du préfixe, si l’adresse IP de destination appartient au sous-réseau local.

Prenons l’exemple d’un poste possédant `192.0.2.25/24`, avec comme passerelle `192.0.2.1`.

| Destination | Décision habituelle | MAC à rechercher par ARP |
|---|---|---|
| `192.0.2.80` | Destination située dans `192.0.2.0/24` | MAC de `192.0.2.80` |
| `192.0.2.1` | Adresse de la passerelle locale | MAC de `192.0.2.1` |
| `198.51.100.50` | Destination hors du préfixe local | MAC de la passerelle `192.0.2.1` |
| `127.0.0.1` | Adresse de boucle locale | Aucune résolution ARP Ethernet normale |

Si la destination est locale, l’hôte cherche la MAC de cette destination. Si elle est distante, il cherche la MAC du prochain saut sélectionné par la table de routage, normalement la passerelle par défaut pour une route par défaut. Une route plus spécifique peut désigner un autre prochain saut. Il faut donc éviter la règle trop simpliste « toute destination distante utilise la passerelle par défaut » : c’est la route effectivement retenue qui détermine le prochain saut.

Une erreur de masque peut modifier ce choix. Un hôte configuré en `/16` alors que le plan d’adressage prévoit `/24` peut croire qu’une destination appartient au réseau local et lancer une résolution ARP qui n’aboutira pas. À l’inverse, un masque trop étroit peut pousser le poste à envoyer vers la passerelle une destination qui aurait dû être directement joignable. ARP peut alors sembler défectueux alors que l’erreur initiale se situe dans l’adressage ou le routage de l’hôte.

### 1.3. Format d’un paquet ARP Ethernet/IPv4

La RFC 826 décrit un format générique avec des champs qui indiquent le type de matériel, le protocole résolu, la longueur des adresses et l’opération demandée. Pour Ethernet et IPv4, le paquet ARP classique mesure 28 octets avant le remplissage nécessaire au support Ethernet.

| Champ | Taille pour Ethernet/IPv4 | Signification |
|---|---:|---|
| Hardware Type (`HTYPE`) | 16 bits | Type de matériel ; `1` correspond à Ethernet |
| Protocol Type (`PTYPE`) | 16 bits | Protocole de couche réseau ; `0x0800` désigne IPv4 |
| Hardware Address Length (`HLEN`) | 8 bits | Longueur de l’adresse matérielle ; `6` octets pour Ethernet |
| Protocol Address Length (`PLEN`) | 8 bits | Longueur de l’adresse IPv4 ; `4` octets |
| Operation (`OPER`) | 16 bits | `1` pour une requête, `2` pour une réponse dans le cas courant |
| Sender Hardware Address (`SHA`) | 6 octets | MAC de l’émetteur de la requête ou de la réponse |
| Sender Protocol Address (`SPA`) | 4 octets | IPv4 de l’émetteur |
| Target Hardware Address (`THA`) | 6 octets | MAC cible ; souvent inconnue dans une requête |
| Target Protocol Address (`TPA`) | 4 octets | IPv4 que l’émetteur cherche à résoudre |

Pour une requête classique, l’émetteur renseigne sa propre MAC et sa propre IPv4, mais ne connaît pas encore la MAC cible. Le champ `THA` est donc souvent rempli de zéros ou traité comme non significatif dans ce contexte. L’adresse IPv4 recherchée est placée dans `TPA`. La requête est transmise en diffusion Ethernet afin que le propriétaire éventuel de cette IPv4 puisse répondre.

Dans une réponse, le champ opération indique `2`. La réponse mentionne la MAC et l’IPv4 du répondant dans les champs émetteur et rappelle les informations du demandeur dans les champs cible. Elle est généralement adressée directement à la MAC du demandeur et non diffusée à tout le segment, bien que les détails observés puissent varier selon le type de paquet et le comportement de l’implémentation.

Le type Ethernet associé à ARP dans la trame est `0x0806`. Il faut le distinguer du champ `PTYPE` interne au paquet ARP, qui indique le protocole pour lequel une résolution est effectuée. Pour une capture Wireshark, ces valeurs permettent d’identifier la trame et d’interpréter la requête/réponse.

### 1.4. Algorithme de résolution côté émetteur

Le processus de résolution peut être décrit comme une suite d’étapes. Le détail interne dépend du système d’exploitation, mais la logique opérationnelle demeure proche de ce qui suit.

1. L’application remet des données à la pile IP.
2. IP détermine l’adresse de destination et consulte la table de routage.
3. La pile identifie la sortie et le prochain saut, qu’il s’agisse de la destination locale ou d’un routeur.
4. Le système consulte son cache de voisins IPv4/ARP à la recherche d’une entrée exploitable pour le prochain saut.
5. Si l’entrée est valide, le système peut construire immédiatement la trame Ethernet.
6. Si aucune entrée valide n’existe, le système place généralement le paquet en attente ou peut le supprimer selon son implémentation, puis émet une requête ARP.
7. Le propriétaire de l’adresse cible, ou éventuellement un équipement qui répond au nom de cette cible, renvoie une réponse.
8. Le demandeur enregistre ou actualise l’association IP–MAC, puis transmet les données lorsque la résolution et les autres conditions sont satisfaites.
9. L’entrée reste disponible selon la politique de cache jusqu’à son rafraîchissement, son expiration, son remplacement ou sa suppression.

La requête ARP n’est pas l’acheminement du paquet de données lui-même. C’est un échange de contrôle local qui permet d’obtenir l’adresse de couche 2. Une capture montrant plusieurs requêtes ARP peut traduire un cache vide, une entrée qui expire, une cible absente, une perte de réponse ou une politique de résolution répétée. Le seul volume de requêtes ne permet pas de conclure immédiatement à une attaque.

```text
+----------------------+       +-----------------------+
| Application / IP     |       | Table de routage      |
| Destination IP       |------>| Préfixe / prochain saut|
+----------------------+       +-----------+-----------+
                                           |
                                           v
                                +-----------------------+
                                | Cache ARP             |
                                | Existe-t-il une MAC ? |
                                +-----------+-----------+
                                            |
                         +------------------+------------------+
                         |                                     |
                        OUI                                   NON
                         |                                     |
                         v                                     v
              +---------------------+             +-----------------------+
              | Construire la trame |             | Diffuser une requête   |
              | Ethernet             |             | ARP sur le VLAN local |
              +---------------------+             +-----------+-----------+
                                                              |
                                                              v
                                                   +-----------------------+
                                                   | Réponse ARP reçue ?   |
                                                   +-----------+-----------+
                                                               |
                                                               v
                                                   +-----------------------+
                                                   | Actualiser le cache   |
                                                   | puis transmettre      |
                                                   +-----------------------+
```

### 1.5. Cache ARP : finalité et contenu

Le cache ARP est la table locale contenant les correspondances entre adresses IPv4 et adresses MAC. Il évite d’émettre une requête de diffusion à chaque paquet envoyé. Sans cache, un flux contenant des milliers de paquets pourrait engendrer un nombre excessif de demandes ARP, une charge inutile sur les hôtes et une augmentation du trafic de diffusion.

Une entrée peut comporter l’adresse IPv4, l’adresse matérielle, l’interface associée et un état ou type dépendant du système. Les entrées dynamiques sont apprises par les mécanismes de résolution et peuvent être remplacées ou supprimées. Les entrées statiques sont configurées par un administrateur et leur persistance varie selon la commande et la plateforme.

Sur Cisco IOS, les commandes courantes comprennent :

```cisco
show ip arp
show arp
show ip arp 192.0.2.25
clear arp-cache
```

Toutes les variantes ne sont pas disponibles sur tous les systèmes. `show ip arp` affiche généralement les correspondances IPv4–MAC connues du routeur. `clear arp-cache` peut supprimer les entrées dynamiques selon la plateforme et la syntaxe ; cette opération peut provoquer de nouvelles requêtes ARP et une courte interruption de certains flux pendant la reconstruction du cache.

Il n’existe pas une durée universelle d’expiration ARP applicable à toutes les plates-formes. Les temporisations dépendent du système d’exploitation, du matériel, de la version logicielle et parfois du type d’entrée. Il faut consulter la documentation du système concerné plutôt que mémoriser une valeur supposée universelle.

Le cache ARP ne doit pas être confondu avec la table MAC d’un commutateur. Le cache ARP associe une IPv4 à une MAC au niveau d’un hôte ou d’un équipement L3. La table de commutation Ethernet associe plutôt une MAC à un port et à un VLAN. Les deux tables répondent à des questions différentes et peuvent être utilisées ensemble pendant un diagnostic.

| Table | Correspondance mémorisée | Équipement typique | Question résolue |
|---|---|---|---|
| Cache ARP | IPv4 → MAC | Hôte, routeur, commutateur L3 | Quelle MAC utiliser pour ce prochain saut IPv4 ? |
| Table MAC/CAM | MAC → port/VLAN | Commutateur L2/L3 | Par quel port transmettre une trame destinée à cette MAC ? |
| Table de routage | Préfixe IP → prochain saut/interface | Hôte, routeur L3 | Où acheminer le paquet IP ? |

Une adresse ARP correcte ne garantit donc pas que le commutateur possède une entrée MAC stable sur le port attendu. Inversement, la présence d’une MAC dans la table CAM ne prouve pas que la correspondance IP–MAC dans le cache ARP est correcte.

### 1.6. Apprentissage ARP et remplacement des entrées

La RFC 826 décrit un traitement dans lequel les informations d’adresse source du paquet ARP peuvent être fusionnées dans la table de correspondance avant que le récepteur examine l’opération exacte. Ce principe contribue à expliquer pourquoi des paquets ARP peuvent actualiser des caches. Les implémentations contemporaines ajoutent toutefois des règles de validation, des états et des protections qui peuvent modifier ce comportement.

Il ne faut pas supposer que tout paquet ARP reçu crée obligatoirement une entrée permanente. La décision dépend de l’implémentation, de l’état antérieur, de l’adresse de l’émetteur, de la nature du paquet et des mécanismes de sécurité actifs. Lors d’un diagnostic, il faut observer le cache avant et après l’événement, capturer les paquets et consulter le comportement documenté du système.

Un remplacement inattendu d’association peut résulter d’un changement légitime, par exemple le remplacement d’une carte réseau, le déplacement d’une machine virtuelle ou la reprise d’une adresse par un autre hôte. Il peut aussi correspondre à un conflit d’IP ou à une tentative d’empoisonnement ARP. Le contexte — fréquence, MAC impliquées, journaux du commutateur et origine des paquets — permet de distinguer ces situations.

### 1.7. Résolution sur le LAN et résolution d’une destination distante

La distinction entre le paquet IP et la trame Ethernet est visible dans les captures. Lorsqu’un hôte envoie un paquet vers une adresse IP distante, l’adresse IP destination du paquet reste celle du serveur final. En revanche, l’adresse MAC destination de la trame est celle du prochain saut local, généralement la passerelle.

Exemple :

- PC-A : `192.0.2.10/24`, MAC `00:00:00:00:00:10` ;
- passerelle : `192.0.2.1`, MAC `00:00:00:00:00:01` ;
- serveur distant : `198.51.100.20`.

Le PC-A envoie un paquet IP dont la source est `192.0.2.10` et la destination `198.51.100.20`. La trame Ethernet locale utilise la MAC source du PC-A et la MAC destination de la passerelle. Une fois la trame reçue, le routeur retire l’en-tête Ethernet entrant, traite le paquet IP, décrémente normalement le TTL lors du transfert et recherche le prochain saut sur l’interface de sortie. Il crée ensuite une nouvelle trame avec les adresses MAC correspondant au lien suivant.

```text
PC-A                   Routeur R1                    Réseau distant
192.0.2.10              192.0.2.1                    198.51.100.20
MAC ...:10              MAC ...:01
   |                         |                              |
   | ARP : qui a             |                              |
   | 192.0.2.1 ?             |                              |
   |------------------------>|                              |
   |<------------------------|                              |
   | MAC de la passerelle    |                              |
   |                         |                              |
   | Trame L2 : dst MAC R1   |                              |
   | IP : dst 198.51.100.20  |                              |
   |------------------------>| Route L3 puis nouvel envoi   |
   |                         |----------------------------->|
```

C’est une erreur fréquente d’attendre d’un PC qu’il apprenne directement la MAC du serveur situé sur Internet. Les adresses MAC ne sont pas acheminées bout en bout comme les adresses IP : elles changent normalement à chaque saut de couche 2.

### 1.8. ARP gratuit, ARP Announcement et détection de conflits

Le terme « gratuitous ARP » est employé couramment pour décrire certains paquets ARP qu’un équipement émet sans avoir reçu une requête traditionnelle préalable. Ils peuvent servir à annoncer une association IP–MAC, à informer les voisins d’un changement ou à aider à détecter un conflit d’adresses. Les détails des champs et de l’usage dépendent du contexte et du système.

La RFC 5227 décrit un mécanisme de détection de conflit IPv4. Un hôte peut émettre des ARP Probe avant d’utiliser une adresse candidate. Dans une sonde, le champ adresse IPv4 source est généralement `0.0.0.0` pour signaler que l’équipement cherche à vérifier l’unicité de l’adresse candidate plutôt qu’à affirmer qu’il la possède déjà. L’adresse recherchée est placée dans le champ cible. Après avoir commencé à utiliser une adresse, un équipement peut aussi envoyer un ARP Announcement pour annoncer son association.

Un gratuitous ARP peut être observé après le démarrage d’un hôte, l’activation d’une interface, une reprise de haute disponibilité ou un basculement d’adresse virtuelle. Il peut aider certains équipements à mettre à jour leur association IP–MAC. Il ne constitue cependant pas une preuve cryptographique de propriété et ne doit pas être interprété comme une authentification.

Les systèmes et équipements réseau peuvent traiter différemment les sondes, annonces et réponses conflictuelles. Pour une analyse fiable, il faut examiner les champs `SPA`, `TPA`, `SHA`, `THA`, le type d’opération, l’adresse MAC Ethernet source et la chronologie des événements.

### 1.9. Détection de doublons d’adresses IPv4

Un conflit apparaît lorsque plusieurs équipements utilisent la même adresse IPv4 dans un même domaine où cette adresse devrait être unique. La conséquence peut être intermittente : certains paquets arrivent au bon équipement, d’autres à l’autre appareil, et les caches ARP évoluent selon les requêtes ou annonces reçues.

Les symptômes courants incluent :

- un avertissement du système d’exploitation indiquant un conflit d’IP ;
- une entrée ARP qui change fréquemment entre plusieurs MAC ;
- des interruptions de communication alors que le lien physique reste actif ;
- des doublons dans une réservation DHCP ou dans un inventaire IPAM ;
- des gratuitous ARP ou ARP Announcement inattendus ;
- des messages de journalisation d’un serveur DHCP ou d’un commutateur.

La cause peut être une adresse statique sortie du plan d’adressage, une réservation DHCP incorrecte, une machine virtuelle clonée avec une mauvaise configuration, un équipement de haute disponibilité mal configuré ou une personne ayant attribué manuellement une adresse déjà utilisée.

La procédure de résolution consiste à recenser les MAC qui annoncent l’adresse, à localiser leurs ports de commutation, à vérifier la configuration DHCP/IPAM et à déterminer lequel des équipements doit la conserver. Il ne faut pas se limiter à supprimer l’entrée du cache ARP : le cache sera reconstruit et le conflit persistera tant que la duplication n’est pas corrigée.

### 1.10. Proxy ARP et Local Proxy ARP

Le Proxy ARP permet à un routeur de répondre à une requête ARP pour une adresse IPv4 qui n’est pas nécessairement celle de son interface, lorsqu’il estime pouvoir acheminer les paquets à destination de cette adresse. Le routeur répond avec sa propre MAC. L’émetteur transmet alors ses trames au routeur, qui effectue le routage IP.

Ce mécanisme peut permettre à des hôtes mal configurés ou à des réseaux conçus selon certaines hypothèses historiques de communiquer sans avoir une passerelle configurée comme on l’attendrait aujourd’hui. Il masque toutefois une partie de l’architecture et peut rendre les problèmes d’adressage difficiles à diagnostiquer.

Le **Local Proxy ARP** correspond à un comportement apparenté dans lequel le routeur peut répondre à une demande concernant une destination considérée comme située sur le même sous-réseau logique, puis router le trafic entre interfaces ou contextes selon le design. Les conditions exactes sont dépendantes de la plateforme. Il ne faut pas considérer Proxy ARP et Local Proxy ARP comme des synonymes dans toutes les documentations.

Sur certaines plateformes Cisco IOS, Proxy ARP peut être activé par défaut sur des interfaces IP, mais les valeurs par défaut varient selon le produit, la version et la fonction d’interface. Il convient de vérifier l’état et la documentation plutôt que de supposer qu’il est toujours activé ou toujours désactivé.

La commande courante de désactivation sur une interface IOS classique est :

```cisco
interface GigabitEthernet0/0
 no ip proxy-arp
```

Elle doit être appliquée uniquement après avoir vérifié que le réseau ne dépend pas de ce comportement. Dans un réseau moderne correctement adressé, le routage explicite avec un masque et une passerelle corrects est généralement plus lisible qu’une dépendance implicite à Proxy ARP.

### 1.11. ARP, VLANs et domaines de diffusion

Un VLAN crée un domaine de couche 2 distinct. Une requête ARP de diffusion émise dans le VLAN 10 n’est normalement pas transportée comme une diffusion Ethernet dans le VLAN 20. Un trunk transporte plusieurs VLANs en préservant leur séparation logique, mais il ne fusionne pas leurs domaines de diffusion.

Par exemple, deux postes peuvent avoir des adresses appartenant à des préfixes différents ou même des adresses qui se chevauchent dans des VLANs distincts. Ils ne vont pas nécessairement se résoudre par ARP l’un l’autre, car les diffusions restent limitées à leur VLAN. Le routage inter-VLAN exige des interfaces L3 ou des SVI sur un équipement de couche 3, ainsi qu’une configuration de routage adaptée.

Un problème VLAN peut ressembler à un défaut ARP : le poste diffuse correctement une requête, mais la machine cible ne la reçoit jamais parce qu’elle se trouve dans un autre VLAN, sur un port mal configuré ou sur un trunk où le VLAN est absent de la liste autorisée. Le dépannage doit vérifier l’appartenance VLAN et l’état du trunk en plus des caches ARP.

Sur Cisco, les commandes suivantes sont souvent utiles :

```cisco
show vlan brief
show interfaces trunk
show mac address-table dynamic
show ip arp
```

La dernière commande s’applique aux équipements disposant de fonctions IPv4 L3. Un commutateur purement L2 peut maintenir une table MAC et commuter les requêtes ARP comme des trames de diffusion sans tenir lui-même un cache ARP pour le trafic des hôtes. Un commutateur L3 peut utiliser ARP pour ses SVI, interfaces routées ou autres fonctions IP.

### 1.12. ARP et commutation Ethernet

Les commutateurs apprennent normalement les adresses MAC sources des trames et associent ces MAC à des ports dans un VLAN. Une requête ARP étant généralement envoyée en diffusion Ethernet, le commutateur la propage dans le domaine de diffusion, selon les règles de VLAN et de filtrage. Une réponse ARP unicast sera ensuite transmise selon la table MAC, si l’adresse destination est connue ; sinon, les règles de commutation déterminent le comportement, généralement une diffusion inconnue dans le VLAN concerné.

ARP n’enseigne pas directement au commutateur la relation IP–MAC au sens du cache ARP. Le commutateur apprend la MAC source à partir de l’en-tête Ethernet. Des fonctions de sécurité comme DAI inspectent le contenu ARP et le comparent à des informations de confiance afin de contrôler la validité de l’association annoncée.

Pour suivre un paquet, il faut souvent corréler trois éléments : la correspondance IP–MAC vue par l’hôte, l’association MAC–port vue par le commutateur et le chemin L3 vers le prochain saut. Cette corrélation permet de déterminer si le problème se situe au niveau de la résolution, de la commutation dans le VLAN ou du routage.

### 1.13. Résolution ARP sur un routeur

Un routeur effectue lui aussi des résolutions ARP pour ses propres interfaces IPv4 Ethernet. Lorsqu’il doit envoyer un paquet sur un réseau directement connecté, il doit connaître la MAC du destinataire ou du prochain saut sur ce réseau. Pour une route statique avec prochain saut IPv4, il peut avoir besoin de résoudre la MAC de ce prochain saut sur l’interface de sortie. Pour un réseau Ethernet multiaccès, la relation dépend de la route et de la manière dont le prochain saut est déterminé.

Les entrées ARP d’un routeur concernent les réseaux auxquels il est directement connecté ou les contextes dans lesquels une résolution locale est requise. Le routeur ne conserve pas nécessairement la MAC du serveur final situé plusieurs routeurs plus loin. Les adresses de couche 2 sont locales au lien.

Si la résolution vers le prochain saut échoue, la route IP peut toujours exister dans la table de routage, mais le routeur ne peut pas construire la trame de sortie appropriée pour ce prochain saut. Cette situation permet d’expliquer pourquoi une route présente ne suffit pas à garantir le transfert effectif des paquets.

### 1.14. Entrées ARP statiques : intérêt et limites

Une entrée statique définit manuellement une relation IPv4–MAC. Selon le système, elle peut éviter une mise à jour dynamique indésirable ou garantir un comportement connu pour une adresse particulière. Dans un IOS classique, un exemple de syntaxe est :

```cisco
arp 192.0.2.50 0011.2233.4455 arpa
```

La syntaxe doit être vérifiée sur la version et le type d’équipement utilisés. Cette commande ajoute une association pour la destination indiquée, mais elle ne remplace pas une configuration correcte de VLAN, de routage ou de sécurité L2.

Les entrées statiques présentent des coûts d’exploitation : elles doivent être mises à jour lorsqu’une carte réseau est remplacée, lorsqu’un serveur migre, ou lorsque son adresse change. Une association statique obsolète peut interrompre la connectivité et être plus difficile à identifier qu’une entrée dynamique. Elles sont adaptées à des cas précis et documentés, pas comme substitut global à la gestion d’adresses.

Une entrée ARP statique sur un routeur ne garantit pas nécessairement que les caches des autres hôtes du VLAN sont également statiques. Elle n’empêche pas à elle seule tous les scénarios d’usurpation sur le segment. La protection doit être conçue à l’échelle du domaine de diffusion.

### 1.15. Différence entre ARP et NDP

ARP est destiné à la résolution d’adresses IPv4 sur les réseaux compatibles. IPv6 utilise Neighbor Discovery Protocol (NDP), basé sur ICMPv6, pour la découverte des voisins, la résolution d’adresses de couche liaison, la découverte des routeurs et certaines fonctions de détection d’injoignabilité et de conflits d’adresses.

NDP n’est pas une version d’ARP qui utilise simplement des adresses IPv6. Ses messages, ses règles et ses implications de sécurité sont différents. Le multicast IPv6 et les messages Neighbor Solicitation/Neighbor Advertisement jouent un rôle que la diffusion Ethernet classique d’ARP ne remplit pas de la même manière.

Un administrateur ne doit donc pas appliquer les mécanismes de diagnostic IPv4 à un problème IPv6 sans adaptation. Une commande `show ip arp` n’affiche pas la table des voisins IPv6 ; les commandes `show ipv6 neighbors` ou leurs variantes sont utilisées selon la plateforme. Les protections de sécurité IPv6, telles que RA Guard et les mécanismes de contrôle NDP, répondent à d’autres messages et problèmes que DAI.

### 1.16. Faiblesses intrinsèques d’ARP

Le protocole ARP de base n’authentifie pas cryptographiquement les réponses. Dans un domaine de diffusion où les hôtes acceptent des associations IP–MAC non vérifiées, un équipement peut annoncer une relation incorrecte. Si cette association est acceptée par les victimes, le trafic peut être détourné, perturbé ou observé par un intermédiaire. C’est le principe général d’ARP spoofing ou ARP poisoning.

L’impact dépend de la topologie, du sens des annonces, des caches, des mécanismes de protection et des capacités de l’attaquant. Un cache empoisonné concernant la passerelle peut affecter du trafic destiné à sortir du VLAN. Un empoisonnement concernant un autre hôte peut perturber les communications locales. Les attaques peuvent également provoquer un déni de service sans permettre une interception complète.

ARP n’authentifie pas non plus le propriétaire d’une adresse à l’aide d’une autorité centralisée. La confiance doit donc être créée par des mesures d’architecture et des contrôles externes : séparation VLAN, sécurisation des ports d’accès, contrôle des annonces ARP, supervision des changements IP–MAC et protection des équipements réseau.

> **Piège :** Une requête ARP en diffusion ne veut pas dire que le paquet IP final est envoyé à tout le monde. La diffusion concerne la trame de résolution sur le VLAN local. Une fois la MAC du prochain saut connue, le paquet IP est encapsulé dans une trame qui cible cette MAC. Pour une destination distante, la MAC destination est en général celle de la passerelle locale ; l’adresse IP destination reste celle du serveur final.

### 1.17. DHCP Snooping et Dynamic ARP Inspection

DHCP Snooping permet au commutateur de distinguer les ports de confiance qui peuvent recevoir des messages DHCP serveur des ports non fiables où se connectent normalement des clients. Sur les plateformes prises en charge, il construit une base de liaisons associant des informations telles que VLAN, adresse IP, MAC, interface et bail DHCP.

Dynamic ARP Inspection (DAI) peut utiliser ces associations pour vérifier les paquets ARP reçus sur des ports non fiables. Les requêtes et réponses qui ne correspondent pas aux associations autorisées peuvent être rejetées. Dans un environnement avec des hôtes à adresse statique, il peut être nécessaire de définir des ARP ACL ou d’utiliser des méthodes de validation compatibles avec la plateforme.

DAI est généralement configuré par VLAN et repose sur une distinction judicieuse entre ports de confiance et non fiables. Marquer un port comme trusted sans vérifier ce qui est connecté derrière lui peut créer une faille : les trames ARP entrantes depuis ce port ne sont pas nécessairement soumises aux mêmes contrôles. Les liens montants vers une infrastructure maîtrisée sont souvent configurés en confiance, mais chaque port doit être évalué par rapport à son rôle.

Un exemple générique Cisco IOS classique est présenté dans la section pratique. Les commandes exactes, la prise en charge des fonctionnalités et les valeurs par défaut varient entre Catalyst et les générations IOS/IOS XE. Il est indispensable de consulter la documentation de la plateforme, de vérifier la base de liaisons DHCP Snooping et de prévoir le cas des adresses statiques avant de déployer DAI.

### 1.18. Mesure et observation par capture de paquets

Une capture réseau permet de voir la demande ARP, la réponse, les changements d’association et le contexte temporel. Dans Wireshark, les filtres usuels incluent `arp`, `arp.opcode == 1` pour les requêtes et `arp.opcode == 2` pour les réponses. La syntaxe et les champs disponibles dépendent de la version de Wireshark, mais ces filtres sont couramment utilisés.

Pour analyser une résolution, il faut relever :

- l’adresse MAC Ethernet source de la trame ;
- l’adresse MAC de diffusion ou unicast destination ;
- le type d’opération ARP ;
- les adresses `SPA` et `TPA` ;
- la MAC `SHA` annoncée ;
- le temps entre la requête et la réponse ;
- la présence éventuelle de plusieurs réponses pour la même IPv4 ;
- le VLAN dans lequel la trame est observée, si l’outil et le point de capture exposent cette information.

Une réponse immédiate et cohérente peut confirmer que la résolution s’est déroulée normalement. L’absence de réponse peut révéler une cible absente, une erreur de VLAN, une adresse mal configurée, un filtrage, une réponse perdue ou une panne de l’interface cible. Plusieurs réponses contradictoires pour une même IPv4 nécessitent une investigation plus poussée : cela peut révéler une redondance légitime mal comprise, un proxy, un conflit ou une usurpation.

### 1.19. Indices permettant de différencier panne et attaque

Aucun indicateur isolé n’établit avec certitude une attaque ARP. Le diagnostic doit combiner plusieurs sources : tables ARP des hôtes, table MAC du commutateur, journaux DAI, associations DHCP, captures, historique de configuration et cartographie des ports.

| Observation | Explications possibles | Vérification utile |
|---|---|---|
| La MAC d’une passerelle change une fois après une maintenance | Remplacement du routeur, basculement HA | Vérifier les journaux et la MAC attendue |
| La MAC d’une IP change à répétition | Conflit, mobilité, boucle ou usurpation | Capturer les annonces et localiser les ports |
| Pas de réponse à une requête ARP | Hôte éteint, mauvais VLAN, mauvais IP, filtrage | Vérifier interface, VLAN et adresse de la cible |
| Beaucoup de requêtes vers de nombreuses IP | Découverte de voisins, cache vide, scan ou défaut | Mesurer le rythme, observer les sources et les logs |
| DAI rejette un paquet | Binding absent/incohérent, ARP invalide, statique non autorisé | Contrôler DHCP Snooping et ARP ACL |

La réponse correcte n’est pas nécessairement de vider tous les caches ARP. Cette action peut supprimer temporairement les symptômes, mais elle ne corrige ni un conflit ni une source d’annonces frauduleuses. Il faut remonter à l’équipement, au VLAN, au port et à la configuration responsable.


## 2. Configuration et Pratique

### 2.1. Laboratoire de base

Le laboratoire utilise un commutateur L2, deux hôtes et une passerelle L3. Tous les équipements se trouvent dans le VLAN 10, avec le réseau `192.0.2.0/24`.

| Équipement | Adresse IPv4 | MAC illustrative | Connexion |
|---|---|---|---|
| PC-A | `192.0.2.10/24` | `00:00:00:00:00:10` | Port d’accès Fa0/1, VLAN 10 |
| PC-B | `192.0.2.20/24` | `00:00:00:00:00:20` | Port d’accès Fa0/2, VLAN 10 |
| R1, interface LAN | `192.0.2.1/24` | `00:00:00:00:00:01` | Port d’accès ou trunk selon design |
| SW1 | SVI de gestion facultative | Dépend de l’interface L3 | VLAN de gestion distinct de préférence |

Le réseau documentaire `192.0.2.0/24` est utilisé ici à titre d’exemple. En production, choisissez les préfixes de l’organisation et vérifiez qu’ils ne se chevauchent pas avec des réseaux connectés, des VPN ou des sites distants.

```text
            VLAN 10 : 192.0.2.0/24

       +---------+                   +---------+
       |  PC-A   |                   |  PC-B   |
       | .2.10   |                   | .2.20   |
       +----+----+                   +----+----+
            | Fa0/1                       | Fa0/2
            |                             |
          +-+-----------------------------+-+
          |              SW1                |
          |             VLAN 10             |
          +----------------+----------------+
                           |
                        Gi0/1
                           |
                       +---+---+
                       |   R1  |
                       | .2.1  |
                       +-------+
```

### 2.2. Configuration de base du commutateur

La configuration exacte dépend du modèle et de l’IOS. L’exemple suivant illustre les éléments essentiels : création du VLAN et affectation des ports d’accès.

```cisco
hostname SW1

vlan 10
 name USERS

interface FastEthernet0/1
 description PC-A
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast

interface FastEthernet0/2
 description PC-B
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
```

`switchport mode access` fixe le rôle du port en accès dans ce scénario, tandis que `switchport access vlan 10` associe le port au VLAN 10. `spanning-tree portfast` est couramment utilisé sur un port reliant un terminal final, mais ne doit pas être activé sans discernement sur une liaison qui peut connecter un autre commutateur. Les noms d’interfaces peuvent être différents sur les plateformes plus récentes.

Si la passerelle R1 est reliée par un port de couche 2 dans le même VLAN, ce port doit également être affecté au VLAN 10. Si le lien est un trunk, il doit être configuré selon la conception et le VLAN concerné doit être autorisé. Un mauvais VLAN peut bloquer la résolution ARP alors que l’adresse IP du poste semble correcte.

### 2.3. Configurer l’interface de la passerelle

Sur un routeur Cisco IOS classique, une interface de couche 3 peut être configurée ainsi :

```cisco
hostname R1

interface GigabitEthernet0/0
 description LAN_VLAN10
 ip address 192.0.2.1 255.255.255.0
 no shutdown
```

Si le port du commutateur relié à un routeur traditionnel transporte un seul VLAN non tagué, une configuration d’accès peut être appropriée. Si le routeur fournit plusieurs réseaux via un trunk, une configuration à sous-interfaces 802.1Q est nécessaire. Il faut éviter de mélanger les deux modèles sans plan explicite.

Lorsque l’interface R1 est opérationnelle, le routeur peut répondre aux requêtes ARP visant `192.0.2.1`. Un PC peut ensuite envoyer vers ce routeur les paquets destinés à des préfixes distants, à condition d’avoir une passerelle configurée et que R1 dispose lui-même d’une route de sortie appropriée.

### 2.4. Vérifier le cache ARP sur Cisco IOS

Après avoir envoyé du trafic entre PC-A et PC-B, le routeur et les hôtes peuvent avoir appris leurs correspondances locales. Sur R1 :

```cisco
show ip arp
show ip arp 192.0.2.10
show interfaces GigabitEthernet0/0
```

La commande `show ip arp` présente les entrées IPv4–MAC visibles par l’équipement L3. Si R1 n’a pas encore communiqué avec PC-A ou reçu un échange lui permettant d’apprendre son association, l’entrée peut ne pas encore figurer dans la table. L’absence d’entrée n’est donc pas automatiquement une panne.

Sur le commutateur, contrôlez la table MAC :

```cisco
show mac address-table dynamic vlan 10
show mac address-table address 0000.0000.0010
show vlan brief
```

La première paire de commandes examine les MAC apprises par le commutateur, tandis que `show vlan brief` confirme l’appartenance des ports aux VLANs. Comparez la MAC découverte avec le port attendu. Si la MAC est apprise sur un port inattendu, recherchez un câblage incorrect, une mobilité d’équipement, un mini-commutateur non documenté ou une anomalie de sécurité.

### 2.5. Supprimer une entrée ARP pour un test contrôlé

Sur une plateforme qui le permet, un administrateur peut supprimer le cache dynamique afin d’observer une nouvelle résolution. Sur certains Cisco IOS, la commande globale est :

```cisco
clear arp-cache
```

Cette opération est utile pendant un laboratoire, mais en production elle peut provoquer plusieurs résolutions simultanées et augmenter momentanément le trafic ARP. La commande et sa portée varient selon les équipements ; il faut vérifier la documentation et l’impact avant l’exécution.

Après suppression, lancez un ping contrôlé vers le prochain saut ou un hôte du même VLAN, puis consultez le cache et une capture réseau. Une séquence normale devrait montrer une requête, une réponse cohérente et l’apprentissage d’une entrée. Si la résolution n’aboutit pas, poursuivez par les contrôles VLAN, interface, adressage et sécurité au lieu de répéter simplement le vidage du cache.

### 2.6. Configurer une entrée ARP statique

Sur certaines plateformes Cisco IOS classiques, une entrée peut être définie comme suit :

```cisco
arp 192.0.2.50 0011.2233.4455 arpa
```

Cet exemple associe l’adresse IPv4 `192.0.2.50` à la MAC `0011.2233.4455` pour le type matériel ARPA/Ethernet. Il sert à illustrer le concept ; l’adresse MAC et l’IP doivent correspondre à un équipement réel et documenté avant toute utilisation.

Une entrée statique doit être réservée à un besoin précis. Elle peut être utile dans certains environnements contrôlés ou de dépannage, mais elle exige une maintenance à chaque modification du matériel ou de l’adressage. Une association statique incorrecte peut diriger les trames vers la mauvaise interface, même si la table de routage demeure valide.

Après ajout, vérifiez la table, testez la connectivité et documentez l’objectif de l’entrée. Ne considérez pas la configuration statique ARP comme une méthode complète de prévention de l’ARP spoofing sur l’ensemble du VLAN.

### 2.7. Vérifier et désactiver Proxy ARP si nécessaire

Sur une interface IOS qui prend en charge ce comportement, l’état du Proxy ARP doit être vérifié avec les commandes disponibles pour la plateforme et la version. La configuration traditionnelle de désactivation s’écrit :

```cisco
interface GigabitEthernet0/0
 no ip proxy-arp
```

Le besoin de désactivation se décide après analyse. Si un réseau dépend du Proxy ARP pour atteindre certaines destinations, sa suppression peut interrompre cette connectivité. Il est préférable de corriger les masques et passerelles des hôtes, puis de vérifier les routes avant de désactiver ce mécanisme dans un environnement existant.

Le test doit inclure les destinations locales et distantes, ainsi que les hôtes qui pourraient dépendre d’un comportement historique. Consignez l’état initial, planifiez un retour arrière et assurez-vous que le changement ne modifie pas d’autres fonctions de l’interface.

### 2.8. Configurer DHCP Snooping et DAI

L’exemple suivant illustre une configuration type sur un commutateur Catalyst compatible. Il ne doit pas être copié sans adaptation : vérifiez d’abord la syntaxe, les VLANs actifs, l’emplacement du serveur DHCP et les capacités du modèle.

```cisco
ip dhcp snooping
ip dhcp snooping vlan 10

interface GigabitEthernet1/0/48
 description UPLINK_VERS_INFRASTRUCTURE_DE_CONFIANCE
 ip dhcp snooping trust
 ip arp inspection trust

interface GigabitEthernet1/0/1
 description PORT_UTILISATEUR_PC_A
 switchport mode access
 switchport access vlan 10
 ! Port utilisateur non fiable par défaut pour ces contrôles

ip arp inspection vlan 10
```

L’interface d’accès reste non fiable pour les contrôles. Le lien de confiance doit mener vers une infrastructure maîtrisée qui doit légitimement transporter les messages DHCP serveur et les associations ARP correspondantes. Il ne faut pas rendre tous les ports trusted pour faire disparaître des rejets : une telle configuration neutraliserait une partie du bénéfice de la protection.

DHCP Snooping construit la base de liaisons pour les clients DHCP. DAI compare les paquets ARP aux informations de confiance disponibles. Les hôtes configurés en IP statique peuvent nécessiter des ARP ACL ou une procédure propre à la plateforme, car ils ne disposent pas nécessairement d’une entrée DHCP Snooping. L’activation de DAI sans préparer ces associations peut bloquer des hôtes légitimes.

Commandes de vérification souvent disponibles sur Catalyst compatibles :

```cisco
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection vlan 10
show ip arp inspection interfaces
show ip arp inspection statistics vlan 10
show logging
```

Surveillez les compteurs de paquets rejetés, les journaux et les associations IP–MAC. Un rejet peut être une indication de paquet frauduleux, mais aussi une erreur de conception : binding absent, hôte statique non référencé, liaison de confiance mal définie ou différence entre les informations DHCP et la configuration réelle.

### 2.9. Configurer DAI pour les hôtes à IP statique

Dans les environnements où certains postes ou serveurs utilisent des adresses statiques, il faut planifier la validation de leurs messages ARP. Selon l’équipement, une ARP ACL peut déclarer les associations autorisées. La syntaxe exacte varie selon les familles IOS/IOS XE et les politiques de validation ; l’exemple ci-dessous donne le principe, pas une configuration universelle prête à déployer.

```cisco
! Exemple conceptuel : vérifier la syntaxe propre à la plateforme
arp access-list STATIC-HOSTS
 permit ip host 192.0.2.50 mac host 0011.2233.4455
!
ip arp inspection filter STATIC-HOSTS vlan 10
```

Une politique ARP ACL doit être testée soigneusement et relue par rapport au plan d’adressage. Une ligne trop permissive peut admettre des associations non prévues ; une liste trop restrictive peut rejeter des annonces légitimes. Il faut également comprendre le comportement de la plateforme lorsque le filtrage ACL et la base DHCP Snooping sont combinés, car les règles de priorité et de traitement peuvent différer.

### 2.10. Procédure de validation avant production

Avant d’activer la sécurité ARP dans un réseau de production, suivez une procédure structurée :

1. Inventoriez les VLANs, les liaisons montantes, les ports d’accès et les serveurs DHCP.
2. Déterminez quels hôtes utilisent DHCP et lesquels disposent d’adresses statiques.
3. Vérifiez que la base DHCP Snooping se peuple correctement et persiste selon les besoins.
4. Identifiez précisément les interfaces qui doivent être déclarées trusted.
5. Préparez les ARP ACL ou les exceptions documentées nécessaires aux hôtes statiques.
6. Activez la protection sur un VLAN pilote et surveillez les rejets.
7. Réalisez des tests de connectivité dans les deux sens, y compris pour les passerelles et les équipements de gestion.
8. Vérifiez les compteurs, les journaux et les chemins de retour.
9. Étendez la politique progressivement, avec une procédure de retour arrière.

La validation ne doit pas se limiter à un simple ping depuis un seul poste. Testez les réservations DHCP, les adresses statiques, les équipements de haute disponibilité, les imprimantes, les téléphones IP et les outils d’administration lorsqu’ils sont présents. Les environnements utilisant des mécanismes de virtualisation ou de déplacement de VM doivent également tester les changements de port et d’association MAC.

> **Astuce :** Pour isoler rapidement un problème ARP, corrèle trois observations : l’entrée IPv4–MAC du poste ou du routeur (`show ip arp`), le port/VLAN où la MAC est apprise (`show mac address-table dynamic vlan X`) et la trace de requête/réponse ARP dans une capture. Si l’association IP–MAC est absente, concentre-toi sur la résolution ; si elle est correcte mais que la MAC apparaît sur un mauvais port, inspecte le chemin L2 ; si la réponse est rejetée, consulte les statistiques DAI et les associations DHCP Snooping avant de modifier la configuration.


## 3. Dépannage et Sécurité

### 3.1. Le poste ne peut pas joindre un hôte du même VLAN

Commencez par vérifier les adresses IP et les masques des deux machines. Si elles appartiennent au même préfixe, l’hôte doit normalement résoudre directement la MAC de l’autre machine. S’il croit que la cible est distante, il peut envoyer le trafic à la passerelle à la place. S’il croit à tort qu’une cible distante est locale, il peut émettre une requête ARP qui ne recevra pas de réponse.

Ensuite, vérifiez l’état du lien, le VLAN d’accès, l’autorisation du VLAN sur les trunks et la présence de la MAC attendue dans la table de commutation. Une requête ARP émise dans le mauvais VLAN n’atteint pas la cible même si le câblage est bon.

Sur l’hôte, consultez son cache ARP ou sa table de voisins. Sur un routeur Cisco, utilisez `show ip arp`. Sur le commutateur, vérifiez `show vlan brief`, `show interfaces trunk` et `show mac address-table dynamic vlan X`. Si nécessaire, réalisez une capture au port du client et une autre à un point plus central pour déterminer si la diffusion traverse le chemin L2 attendu.

### 3.2. Le poste ne peut pas atteindre une destination distante

Pour une destination hors du sous-réseau local, observez d’abord si l’hôte résout la MAC de sa passerelle. Si l’entrée de la passerelle est absente et aucune réponse ARP n’arrive, le problème peut se trouver sur le segment local : mauvais VLAN, interface routeur désactivée, adresse de passerelle incorrecte, filtrage L2 ou passerelle non présente.

Si la MAC de la passerelle est résolue, vérifiez ensuite la table de routage et l’interface de sortie de la passerelle. Il faut examiner les routes de retour, les ACL, les pare-feu et la résolution du prochain saut sur les routeurs suivants. Ne continuez pas à investiguer ARP sur le PC une fois qu’il a une association cohérente pour sa passerelle, sauf si les éléments disponibles indiquent un changement ou un empoisonnement.

Un ping vers la passerelle est un test utile, mais n’atteste pas à lui seul de la connectivité jusqu’à une destination distante. Un ping peut également être filtré par un équipement même si certains flux applicatifs passent. Il faut combiner observations de routage, tests contrôlés et captures.

### 3.3. L’entrée ARP est incorrecte ou change souvent

Lorsqu’une adresse IPv4 est associée à une MAC inattendue, identifiez la source des paquets qui annoncent cette correspondance. Examinez les requêtes, les réponses et les annonces non sollicitées. Sur le commutateur, localisez la MAC dans la table CAM et relevez le port d’apprentissage. Comparez l’adresse avec l’inventaire matériel et l’affectation DHCP.

Les événements qui changent une association de manière légitime comprennent la migration d’une machine virtuelle, le remplacement d’une carte, un basculement de passerelle virtuelle ou une réattribution DHCP. Si le changement ne correspond pas à une opération connue, recherchez un conflit ou un comportement malveillant.

Ne supprimez pas simplement l’entrée fautive sans conserver les informations de diagnostic. Une capture courte, les journaux du commutateur, les statistiques DAI et la table DHCP Snooping peuvent permettre d’identifier l’équipement d’origine. Après correction, videz éventuellement les entrées dynamiques concernées selon une procédure contrôlée et confirmez qu’elles se reconstruisent correctement.

### 3.4. ARP spoofing et ARP poisoning

L’ARP spoofing consiste à annoncer une association IPv4–MAC qui n’est pas légitime ou autorisée. L’ARP poisoning désigne le fait d’empoisonner un ou plusieurs caches ARP pour que le trafic soit acheminé vers une MAC incorrecte. Les deux termes sont souvent utilisés de manière proche dans l’exploitation courante.

Un attaquant situé dans le même domaine L2 peut tenter de se faire passer pour la passerelle, pour un autre poste ou pour un serveur. Si le cache d’une victime accepte la fausse association, ses trames peuvent être envoyées au mauvais équipement. Un intermédiaire peut alors tenter d’observer ou modifier le trafic, tandis qu’une simple perturbation de cache peut suffire à provoquer un déni de service.

La portée reste généralement liée au domaine de diffusion, mais les conséquences peuvent s’étendre si la cible usurpée est une passerelle ou si plusieurs VLANs sont affectés par une infrastructure commune. La sécurité de couche 2 est donc particulièrement importante dans les réseaux où des utilisateurs, serveurs ou appareils IoT partagent un domaine de diffusion.

### 3.5. Détection et réponse à un soupçon d’empoisonnement

En cas de soupçon, ne commencez pas par désactiver globalement DAI ou par effacer toutes les tables. Procédez méthodiquement :

- capturez les paquets ARP contradictoires et relevez les MAC sources ;
- examinez le cache ARP des victimes et de la passerelle ;
- localisez les MAC suspectes via la table de commutation ;
- vérifiez DHCP Snooping, les bindings et les compteurs de DAI ;
- identifiez le port physique, la machine virtuelle ou l’équipement en cause ;
- isolez l’équipement si la politique de sécurité l’exige ;
- corrigez la cause, puis validez la restauration des associations ;
- conservez les journaux et la capture pour l’analyse de l’incident.

La localisation d’une MAC peut être perturbée par la mobilité, les trunks, les agrégats et les mécanismes de virtualisation. La commande de localisation doit être exécutée sur les commutateurs successifs du chemin jusqu’au port d’accès. Si la MAC est apprise sur un uplink, il faut poursuivre l’investigation plus loin dans l’infrastructure.

### 3.6. DAI : fonctionnement et limites

DAI inspecte les paquets ARP reçus sur des interfaces non fiables et compare leurs informations IP–MAC à une source de validation, généralement la base DHCP Snooping. Les paquets incohérents peuvent être rejetés et comptabilisés. Il s’agit d’un contrôle à l’entrée du port : il ne protège pas automatiquement les segments dépourvus de cette inspection ni les équipements raccordés à une infrastructure non maîtrisée.

DAI n’est pas une solution magique. Il faut comprendre où sont créées les associations de confiance, quels ports sont déclarés trusted, comment sont traités les équipements statiques et comment les paquets traversent les frontières des commutateurs. Un trunk déclaré trusted laisse passer les ARP qu’il transporte sans la même validation d’entrée sur cette interface ; cette décision doit donc correspondre à un lien réellement maîtrisé.

Les protections doivent être activées de façon cohérente dans tout le domaine de diffusion. Si un commutateur filtre les annonces mais qu’un autre équipement du même VLAN accepte les annonces non vérifiées, des hôtes non protégés peuvent rester vulnérables. Les limitations exactes dépendent de la topologie et des capacités du matériel.

### 3.7. DHCP Snooping : conception prudente

DHCP Snooping est utile pour construire une base fiable de correspondances, mais son fonctionnement dépend de la classification des interfaces. Les ports qui reçoivent des messages de serveurs DHCP légitimes doivent être configurés de manière appropriée. Les ports où des clients se connectent doivent normalement rester non fiables, afin d’empêcher qu’un serveur DHCP non autorisé fournisse des paramètres aux clients.

Une configuration de confiance trop large est un risque. Si un port d’accès utilisateur est marqué trusted, un équipement connecté à ce port peut potentiellement envoyer des messages serveur qui contourneraient les contrôles de DHCP Snooping. Il faut donc conserver une cartographie des liens et réévaluer les rôles après chaque changement de câblage.

Vérifiez également la persistance de la base de liaisons si la plateforme et l’architecture l’exigent. Après un redémarrage, l’absence de bindings nécessaires peut conduire DAI à rejeter des paquets légitimes selon le comportement et la configuration du système. Les procédures d’exploitation doivent inclure la vérification de la base après redémarrage ou modification majeure.

### 3.8. Mesures de défense complémentaires

La prévention des attaques ARP doit être multicouche :

1. **Segmentation VLAN** : limite les domaines de diffusion et la portée d’un empoisonnement.
2. **Port security** : contrôle certaines caractéristiques des adresses MAC apprises sur les ports ; ses capacités et limites dépendent du modèle.
3. **DHCP Snooping** : construit des bindings et réduit le risque de serveurs DHCP non autorisés.
4. **Dynamic ARP Inspection** : contrôle les ARP sur les ports non fiables selon une base de validation.
5. **802.1X et contrôle d’accès** : limite les équipements et utilisateurs autorisés à accéder au réseau, selon l’architecture.
6. **Supervision** : suit les changements IP–MAC, les journaux, les compteurs de rejets et les événements de port.
7. **Hygiène d’adressage** : maintient IPAM, les réservations DHCP et les adresses statiques documentées.
8. **Chiffrement applicatif** : TLS ou des mécanismes équivalents réduisent l’exposition de certaines données même lorsqu’un trafic est intercepté, sans empêcher en soi le détournement ARP ou le déni de service.

Aucune mesure unique ne couvre toutes les possibilités. Port Security ne valide pas à elle seule l’association IP–MAC ; DAI ne remplace pas un contrôle d’accès de réseau ; le chiffrement applicatif n’empêche pas la perte de connectivité. La conception doit combiner ces mécanismes selon les risques du domaine.

### 3.9. Checklist de diagnostic ARP

Avant d’escalader un incident, vérifiez successivement les éléments suivants :

- adresse IPv4, masque et route retenue sur l’hôte ;
- choix de la destination locale ou du prochain saut ;
- existence de l’entrée ARP pertinente ;
- émission de la requête ARP dans le VLAN attendu ;
- réception et contenu de la réponse ;
- appartenance VLAN des ports et autorisation sur les trunks ;
- présence de la MAC dans la table de commutation ;
- route de retour et état des interfaces L3 ;
- journaux, compteurs et bindings si DAI/DHCP Snooping sont activés ;
- conflits d’adresse, changements MAC ou annonces ARP non sollicitées ;
- impact potentiel avant tout vidage de cache ou modification de confiance.

Cette séquence évite de traiter chaque panne de connectivité comme un problème ARP. ARP n’est qu’une étape de l’acheminement IPv4 ; le problème peut être situé dans l’adressage, le routage, la commutation, la sécurité ou l’équipement final.

> **Danger :** Une annonce ARP falsifiée peut détourner le trafic d’un segment local et, lorsqu’elle usurpe la passerelle, affecter les communications vers de nombreux réseaux. Une mauvaise configuration de confiance sur un port peut rendre inefficace une partie des contrôles DAI. N’active pas la confiance sur un port simplement pour faire disparaître des rejets ; valide d’abord son rôle, les équipements situés derrière et les associations attendues. En cas d’incident, conserve les preuves, localise le port source, isole l’équipement suspect selon la procédure d’exploitation et rétablis les associations après correction de la cause.


## Points à retenir

- **ARP résout localement une IPv4 en adresse MAC pour le prochain saut.** Pour une destination distante, l’hôte résout habituellement la MAC de la passerelle, pas la MAC du serveur final. Le routage IP choisit le prochain saut ; ARP permet ensuite de construire la trame Ethernet correspondante.

- **Les tables ARP, MAC et de routage répondent à des questions différentes.** Le cache ARP mémorise IPv4 → MAC, la table MAC associe une MAC à un port/VLAN, et la table de routage associe un préfixe IP à un prochain saut ou une interface. Leur corrélation est essentielle pour localiser une panne.

- **ARP de base n’authentifie pas la propriété d’une adresse.** Les conflits et attaques d’empoisonnement doivent être traités avec des mesures d’architecture et de sécurité adaptées, notamment segmentation, DHCP Snooping, Dynamic ARP Inspection, contrôle des ports et supervision. Les adresses statiques et les liens déclarés trusted nécessitent une attention particulière.


## Références techniques

- [RFC 826 — An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826) : définition du format et du mécanisme ARP.
- [RFC 5227 — IPv4 Address Conflict Detection](https://www.rfc-editor.org/rfc/rfc5227) : ARP Probe, ARP Announcement et détection de conflits IPv4.
- [Cisco — Dynamic ARP Inspection, configuration IOS XE](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/sec-crypto/fhs-sisf/fhs-and-sisf-configuration-guide/dynamic-arp-inspection.html) : fonctionnement, dépendance à DHCP Snooping, ports trust et vérifications.
- [Cisco — Proxy ARP et Local Proxy ARP](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/ipaddresses-and-services/configuration-guide/ip-addresses-and-services-config-cisco8000/address-resolution/proxy-arp-and-local-proxy-arp.html) : distinction des comportements et configuration selon la plateforme.
