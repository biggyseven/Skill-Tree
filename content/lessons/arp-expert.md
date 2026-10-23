---
node_id: arp-expert
title: ARP & résolution L2/L3 - Expert
---

# ARP & résolution L2/L3 - Expert

**Niveau :** Expert

Address Resolution Protocol (ARP) est le mécanisme historique qui permet à IPv4 d’utiliser un réseau de liaison comme Ethernet sans confondre les adresses logiques IP et les adresses de livraison de couche 2. Défini initialement dans la RFC 826 en novembre 1982, ARP a été conçu pour associer une adresse de protocole, par exemple IPv4, à une adresse de réseau local, par exemple une adresse MAC Ethernet. Son ancienneté ne le rend pas secondaire : il intervient dans presque chaque première communication IPv4 sur un segment Ethernet et reste indispensable au fonctionnement des réseaux d’entreprise, des environnements virtualisés et de nombreuses infrastructures de centres de données.

ARP se situe à la frontière entre la décision de routage IP et la transmission sur un lien. Le moteur de routage détermine si la destination est directement connectée ou si un prochain saut doit être utilisé. Une fois ce choix effectué, le système doit connaître l’adresse de couche 2 du voisin qui recevra la trame. ARP fournit cette correspondance pour IPv4 sur les réseaux qui utilisent cette méthode de résolution. Il ne choisit pas la route, ne transporte pas les données applicatives et ne traverse normalement pas les routeurs comme une diffusion Ethernet ordinaire.

Le protocole est simple en apparence, mais ses conséquences opérationnelles sont importantes. Ses messages sont diffusés dans le domaine de couche 2, les implémentations apprennent souvent des associations à partir des champs émis par les pairs, et le protocole ne possède pas d’authentification cryptographique native. Les caches ARP, les annonces non sollicitées, les réponses de Proxy ARP, les mécanismes de détection de doublons et les protections de commutation influencent donc directement la disponibilité et la sécurité d’un réseau IPv4.

Une analyse experte d’ARP doit relier plusieurs tables et décisions : table de routage, cache de voisins, table MAC du commutateur, association VLAN, informations DHCP, règles de filtrage et parfois état d’un overlay tel que VXLAN/EVPN. Un ping qui échoue ne signifie pas nécessairement qu’ARP est en panne ; une entrée ARP qui semble correcte ne prouve pas non plus que le bon port de commutateur, le bon VLAN ou le chemin de retour est utilisé. L’objectif de ce cours est d’analyser la résolution de bout en bout, de maîtriser les détails du protocole et de traiter les scénarios de conception, de dépannage et de sécurité avec méthode.

> **Analogie** : Imagine une entreprise qui possède un annuaire interne avec les noms logiques des employés, mais qui doit remettre physiquement chaque courrier à un poste précis dans un bâtiment. L’adresse IP correspond à l’identité logique du destinataire dans l’entreprise ; l’adresse MAC correspond à l’identifiant du poste qui recevra la trame sur le réseau local. Le service de routage décide d’abord si le destinataire travaille dans le même bâtiment ou si le courrier doit être envoyé à un relais. ARP ne choisit pas ce relais : il traduit le nom du relais sélectionné en identifiant de poste afin que le commutateur puisse livrer le courrier.
>
> Le cache ARP ressemble à un carnet d’associations utilisé pour éviter de demander à chaque fois où se trouve le même poste. Lorsqu’une association est inconnue ou expirée, le système lance une question publique dans le segment local. Tous les équipements présents dans ce domaine de diffusion peuvent l’entendre, mais seul l’équipement concerné est normalement censé fournir la réponse appropriée. Un routeur configuré en Proxy ARP peut parfois répondre à la place d’un autre équipement : il se comporte alors comme un guichet qui accepte le courrier et promet de le faire suivre. Ce comportement est utile dans certains designs, mais dangereux si l’architecture est mal comprise, car le carnet du demandeur associe alors la destination distante à l’identifiant du relais.
>
> Le problème de sécurité apparaît parce que les réponses ne sont pas accompagnées d’une preuve cryptographique que l’expéditeur possède réellement l’adresse IP annoncée. Un imposteur peut donc tenter de faire inscrire son identifiant de poste à la place de celui du routeur ou d’un serveur. Le carnet devient incorrect, et le courrier peut passer par l’imposteur. Le contrôle des associations, la segmentation, la surveillance des annonces et les protections des commutateurs jouent donc le rôle d’un registre officiel plutôt que de faire confiance à toute annonce entendue dans le bâtiment.

---

## 1. La théorie et les algorithmes

### 1.1. La place exacte d’ARP dans le traitement d’un paquet

ARP ne doit être invoqué qu’après la décision de routage. Le système émetteur commence par analyser l’adresse IP de destination, consulte les routes disponibles et choisit une route selon les règles de l’implémentation, notamment la correspondance du préfixe le plus long, les éventuelles politiques de routage et les critères de sélection applicables. Cette opération détermine l’interface de sortie et, le cas échéant, l’adresse IP du prochain saut.

Si la destination est directement connectée au lien de sortie, le prochain saut à résoudre est généralement l’adresse IPv4 de destination elle-même. Si la destination se trouve sur un réseau distant, l’adresse à résoudre est celle du routeur de prochain saut, pas celle de l’hôte distant. C’est la séparation fondamentale entre couche 3 et couche 2 : l’en-tête IP conserve l’adresse IP finale tandis que l’en-tête Ethernet cible le prochain équipement local.

Exemple : un poste `192.0.2.10/24` veut contacter `192.0.2.40`. La route connectée indique que les deux sont dans le même préfixe ; le poste résout `192.0.2.40` par ARP. Si le même poste contacte `198.51.100.25`, la route par défaut désigne `192.0.2.1` comme passerelle ; le poste résout `192.0.2.1` par ARP, puis envoie une trame à la MAC de la passerelle contenant un paquet IP destiné à `198.51.100.25`.

Cette distinction évite une erreur fréquente de dépannage : l’absence d’entrée ARP pour l’adresse IP distante n’est pas forcément un défaut. Dans un réseau routé classique, l’hôte final ne doit pas maintenir une association ARP directe vers chaque hôte de l’Internet. Il maintient une association vers son prochain saut local.

L’algorithme conceptuel est le suivant :

1. Déterminer la destination IP du paquet.
2. Effectuer la recherche de route et choisir l’interface de sortie.
3. Déterminer le prochain saut L3 : destination directement connectée ou routeur.
4. Chercher l’association IPv4/MAC dans le cache du voisinage adapté à cette interface et à ce domaine L2.
5. Si une association valide existe, construire la trame Ethernet.
6. Sinon, créer une entrée incomplète et émettre une requête ARP sur le lien local.
7. Attendre une réponse ou l’expiration des tentatives ; pendant l’attente, la pile peut mettre en file d’attente, retarder ou abandonner les paquets concernés selon l’OS.
8. Mettre à jour le cache avec les informations validées selon les règles de l’implémentation, puis reprendre l’émission.

Une fois la trame reçue, le commutateur s’appuie sur la MAC de destination et sa table d’adresses MAC pour choisir le port de sortie. ARP et la table MAC du commutateur sont donc deux mécanismes différents : le premier associe une adresse IPv4 à une MAC dans les hôtes et routeurs ; la seconde associe une MAC à un port et à un VLAN dans le plan de commutation.

### 1.2. Domaines de diffusion, VLAN et limites de propagation

Une requête ARP Ethernet typique est envoyée à la MAC de diffusion `FF:FF:FF:FF:FF:FF`. Le commutateur la propage sur les ports du même VLAN, à l’exception du port d’entrée, sous réserve des politiques de sécurité et du comportement de la plateforme. Les ports en mode trunk transportent la trame dans les VLAN autorisés conformément à la configuration 802.1Q. Un routeur IP ne retransmet pas simplement la diffusion ARP vers un autre réseau IP.

Le domaine de diffusion L2 doit donc correspondre à l’endroit où la résolution directe peut fonctionner. Deux hôtes peuvent utiliser des adresses IPv4 appartenant au même préfixe logique tout en étant séparés dans des domaines L2 distincts ; sans mécanisme particulier, ils ne recevront pas les requêtes ARP de l’autre. Une telle incohérence de conception conduit souvent à des échecs où les masques semblent corrects, mais où ARP reste sans réponse.

À l’inverse, étendre inutilement un VLAN étend la portée des diffusions, y compris les requêtes ARP. Le coût d’une requête isolée est faible, mais un grand domaine L2 multiplie le nombre d’équipements qui doivent la traiter et augmente le périmètre potentiel d’une attaque par empoisonnement ou par saturation. La segmentation VLAN limite le domaine, mais ne protège pas à elle seule les hôtes du même VLAN contre ARP spoofing.

Un tag 802.1Q ne fait pas partie du message ARP lui-même : il est ajouté dans l’encapsulation Ethernet lorsque la trame traverse un trunk. Dans une capture, l’ordre général est MAC destination, MAC source, champ EtherType ou combinaison taguée, puis la charge ARP. Le VLAN doit être contrôlé quand une requête est visible sur un port mais ne parvient pas au destinataire attendu.

### 1.3. Format du paquet ARP Ethernet/IPv4

La RFC 826 décrit un format générique dans lequel les longueurs d’adresse dépendent du type de matériel et du protocole réseau. Dans le cas Ethernet/IPv4 le plus courant, le paquet ARP comprend 28 octets de champs ARP. Les valeurs classiques sont les suivantes :

| Champ | Taille Ethernet/IPv4 | Valeur ou rôle |
|---|---:|---|
| Hardware Type (`HTYPE`) | 2 octets | `1` pour Ethernet |
| Protocol Type (`PTYPE`) | 2 octets | `0x0800` pour IPv4 |
| Hardware Address Length (`HLEN`) | 1 octet | `6` pour une adresse MAC Ethernet |
| Protocol Address Length (`PLEN`) | 1 octet | `4` pour une adresse IPv4 |
| Operation (`OPER`) | 2 octets | `1` requête, `2` réponse dans le cas classique |
| Sender Hardware Address (`SHA`) | 6 octets | MAC annoncée par l’émetteur ARP |
| Sender Protocol Address (`SPA`) | 4 octets | IPv4 annoncée par l’émetteur |
| Target Hardware Address (`THA`) | 6 octets | MAC cible, souvent nulle dans la requête |
| Target Protocol Address (`TPA`) | 4 octets | IPv4 que l’émetteur cherche à résoudre |

L’EtherType Ethernet pour ARP est `0x0806`. Le type de protocole dans le paquet ARP (`PTYPE=0x0800`) identifie IPv4 ; ce champ ne doit pas être confondu avec l’EtherType de la trame contenant ARP. Les nombres sont encodés selon l’ordre réseau, octet de poids fort en premier.

Dans une requête conventionnelle, `SHA` et `SPA` indiquent l’adresse MAC et l’adresse IPv4 de l’émetteur ; `TPA` contient l’adresse qu’il souhaite résoudre. Le champ `THA` n’est souvent pas encore connu et est mis à zéro. Le destinataire Ethernet est la diffusion, car le demandeur ne connaît précisément aucune MAC à laquelle envoyer la demande.

Dans une réponse conventionnelle, le matériel source fournit sa MAC dans `SHA` et l’adresse IP recherchée dans `SPA`. Le destinataire ARP correspond au demandeur, tandis que la trame Ethernet de réponse est généralement unicast vers la MAC du demandeur. Le protocole n’impose pas qu’une réponse soit toujours précédée d’une requête correspondante ; cette capacité contribue à l’utilité des annonces ARP, mais ouvre aussi la porte à l’empoisonnement du cache.

Une trame Ethernet minimale doit respecter la taille minimale imposée par Ethernet. Le contenu ARP de 28 octets est donc accompagné d’un padding lorsque nécessaire. Les captures effectuées par certains outils réseau peuvent ne pas présenter le padding ou le FCS comme on s’attendrait à le voir à partir de la longueur du signal physique. Une différence de longueur dans Wireshark n’est donc pas automatiquement une trame malformée.

### 1.4. Séquence de résolution normale

Considérons deux hôtes dans le même VLAN : H1 `192.0.2.10/24` et H2 `192.0.2.20/24`. H1 dispose déjà de son adresse IP mais ne connaît pas la MAC associée à H2.

```text
H1                         Switch L2                         H2
|                              |                              |
| ARP Request                  |                              |
| Who has 192.0.2.20?          |                              |
| SHA=MAC-H1                   |                              |
| SPA=192.0.2.10               |                              |
| TPA=192.0.2.20               |                              |
|----------------------------->|----------------------------->|
|                              |                              |
|                              | ARP Request reçu en diffusion|
|                              |                              |
|                              |<-----------------------------|
| ARP Reply                    |                              |
| 192.0.2.20 is at MAC-H2      |                              |
|<-----------------------------|                              |
|                              |                              |
| Cache H1: 192.0.2.20 -> MAC-H2                              |
| Transmission IP vers MAC-H2 sur Ethernet                    |
```

La requête est traitée dans le VLAN concerné. H2 peut apprendre ou rafraîchir une association à partir des champs émetteur selon l’algorithme de réception et les règles de son système. H2 répond généralement en unicast à H1. H1 enregistre alors l’association IPv4/MAC et peut émettre les trames IP attendues.

Il existe des différences d’implémentation dans les politiques d’apprentissage, les délais de cache, les traitements des annonces non sollicitées et les réponses aux sondes de détection de conflit. Les opérateurs ne doivent pas supposer que tous les systèmes exploitent chaque champ ARP exactement de la même manière. Les règles protocolaires, la politique de sécurité de l’OS et les optimisations de pile réseau influencent le résultat pratique.

### 1.5. Résolution d’une destination distante

La même logique est différente si H1 `192.0.2.10/24` souhaite contacter `198.51.100.25`. La décision IP indique que la destination n’appartient pas au préfixe local. H1 sélectionne donc sa passerelle `192.0.2.1` pour la route par défaut ou pour une route plus spécifique.

```text
             Domaine VLAN 10                        Réseau distant

 H1                     R1                              Serveur
192.0.2.10          192.0.2.1                       198.51.100.25
    |                    |                                  |
    | Route lookup       |                                  |
    | 198.51.100.25      |                                  |
    | via 192.0.2.1      |                                  |
    |                    |                                  |
    | ARP pour .2.1      |                                  |
    |------------------->|                                  |
    | MAC de R1          |                                  |
    |<-------------------|                                  |
    |                    |                                  |
    | Ethernet dst=MAC-R1, IP dst=198.51.100.25              |
    |------------------->| Routage L3 puis nouveau L2       |
```

Le routeur retire l’en-tête Ethernet reçu et utilise l’adresse IP finale pour prendre une nouvelle décision de routage. Il diminue généralement le TTL IPv4, met à jour les champs d’en-tête associés et crée une nouvelle trame sur le lien de sortie. Il effectue ensuite sa propre résolution de voisinage si la MAC du prochain saut sur ce lien est inconnue.

Un routeur ne transmet pas la MAC Ethernet de H1 à travers le réseau distant. Les en-têtes Ethernet sont locaux à chaque segment. L’adresse IP finale demeure stable pendant le routage ordinaire, hors fonctions comme NAT, tunnel ou autres traitements de réseau, tandis que la MAC source et destination sont remplacées à chaque saut L2.

### 1.6. Cache ARP : rôle, états et vieillissement

Le cache ARP mémorise les associations IPv4/MAC afin d’éviter une requête de résolution pour chaque paquet. Il est propre à une pile réseau, un espace de routage ou un contexte de plateforme. Sur un routeur, plusieurs interfaces et VRF peuvent utiliser des associations séparées ; l’adresse IP seule n’est donc pas toujours une clé suffisante pour raisonner sur toutes les tables ARP d’un équipement.

Les implémentations utilisent des modèles d’état différents. Les concepts fréquents incluent :

- **Incomplete** : une résolution a été initiée, mais aucun voisin n’a encore répondu.
- **Reachable/valid** : l’association est utilisable d’après la politique de l’implémentation.
- **Stale** : l’entrée existe, mais sa validité récente n’est pas démontrée ; une sollicitation peut être déclenchée au moment de la réutilisation.
- **Permanent/static** : l’association a été configurée ou verrouillée administrativement.
- **Failed** : une résolution a échoué ou a atteint ses limites de tentative sur les systèmes qui exposent cet état.

Ces libellés sont particulièrement visibles dans les tables de voisinage de systèmes comme Linux. Cisco IOS, Windows et d’autres OS présentent des informations différentes. Il ne faut pas comparer directement deux valeurs d’état sans connaître le modèle de chaque système.

Le vieillissement d’une entrée n’est pas universel. Des versions Cisco IOS utilisent traditionnellement un délai ARP dynamique de plusieurs heures et permettent de le configurer, alors que les systèmes d’exploitation et autres constructeurs suivent leurs propres politiques. Une entrée qui a expiré n’indique pas nécessairement un incident : il s’agit souvent d’un fonctionnement normal destiné à éviter de conserver indéfiniment une association devenue obsolète.

Un changement légitime de MAC peut se produire à la suite d’un remplacement de carte réseau, d’une migration de VM, d’un basculement de haute disponibilité ou d’une modification d’infrastructure. Les annonces ARP appropriées et l’expiration des caches contribuent à converger vers la nouvelle association. Si certains équipements conservent une ancienne entrée, le réseau peut connaître une panne partielle jusqu’au rafraîchissement ou à l’effacement du cache.

Une entrée statique peut contourner certains mécanismes dynamiques, mais elle crée une dette d’exploitation. Les changements de matériel, de redondance ou d’adressage doivent alors être accompagnés d’une mise à jour de toutes les associations statiques. Les entrées statiques ne sont pas une mesure générale et évolutive de défense contre l’empoisonnement dans les réseaux d’entreprise.

### 1.7. Réception ARP et apprentissage des associations

Un point subtil de la RFC 826 est que le récepteur utilise les champs émetteur d’un message ARP pour construire ou rafraîchir sa table de traduction, sous réserve des règles de traitement prévues. Le fonctionnement historique n’impose pas une authentification de la correspondance annoncée. Cette caractéristique permet un apprentissage efficace lorsque les hôtes communiquent, mais elle signifie aussi qu’une annonce fabriquée peut tenter de modifier une entrée existante.

Les implémentations modernes peuvent appliquer des politiques supplémentaires : vérifier certains champs, ignorer des annonces selon le contexte, protéger des entrées statiques, limiter les rafraîchissements ou utiliser d’autres signaux de confiance. Il n’est pas prudent de compter sur une supposée règle universelle selon laquelle toute réponse non sollicitée serait rejetée. Le comportement doit être mesuré sur les versions d’OS concernées.

Le champ `SPA` est particulièrement important. Dans une requête ARP normale, il contient l’adresse IPv4 de l’émetteur. Dans une sonde ARP destinée à vérifier si une adresse est déjà utilisée, `SPA` est mis à `0.0.0.0` afin de ne pas prétendre posséder l’adresse testée. Une capture de ce type ne doit pas être interprétée comme une annonce ordinaire.

Le champ `THA` peut être nul dans une requête et doit être interprété avec le type d’opération. Une analyse forensique doit comparer l’en-tête Ethernet externe, les champs ARP internes, le VLAN, le port d’entrée et le contexte de l’hôte. Un désaccord entre MAC source Ethernet et SHA ARP peut être suspect, mais il peut aussi provenir d’une fonctionnalité particulière ou d’une encapsulation observée à un point de capture atypique ; il demande une explication plutôt qu’une conclusion automatique.

### 1.8. ARP gratuit, annonce ARP et sondes de conflits

L’expression *gratuitous ARP* est souvent utilisée comme terme générique pour des messages ARP qui annoncent ou vérifient une association sans qu’une requête classique d’un pair les ait déclenchés. Il faut distinguer les usages précis : sonde de conflit d’adresse, annonce d’une adresse nouvellement activée, mise à jour des caches après un basculement et réponse ARP non sollicitée.

La RFC 5227 définit un mécanisme de détection de conflit IPv4. Avant d’utiliser une adresse, un hôte peut émettre des **ARP Probes** : les requêtes ont leur `SPA` égal à `0.0.0.0` et leur `TPA` égale à l’adresse candidate. L’objectif est de voir si une autre machine revendique déjà cette adresse, sans utiliser prématurément l’adresse candidate comme adresse source. Si un conflit est détecté, l’hôte ou l’application de configuration doit suivre sa politique de traitement du doublon.

Après l’allocation d’une adresse, un hôte peut annoncer celle-ci en envoyant des ARP Announcements. Une forme classique utilise l’adresse annoncée dans `SPA` et `TPA`, mais les détails doivent être rapprochés de la RFC 5227 plutôt que de considérer tout paquet couramment appelé GARP comme identique. Un gratuitous ARP peut aussi servir à informer les caches de voisins d’un changement, notamment lors d’un basculement d’adresse IP virtuelle.

Les systèmes de haute disponibilité, tels que certaines implémentations HSRP ou VRRP, peuvent envoyer des annonces ARP ou modifier les MAC virtuelles pour que les hôtes et commutateurs réapprennent le chemin. Le comportement précis dépend du protocole de redondance et de l’implémentation. Il ne faut pas supposer que chaque basculement utilise toujours exactement le même motif de paquets.

Les annonces sont utiles, mais leur absence ne signifie pas forcément qu’un service est mal configuré. La convergence dépend aussi du vieillissement du cache, du comportement des piles hôtes, de la table MAC des commutateurs, du mécanisme de redondance et de l’emplacement des captures. Les annonces non sollicitées sont également un vecteur possible de cache poisoning ; le réseau doit les valider si une protection adaptée est déployée.

### 1.9. Détection et défense contre les conflits IPv4

Un conflit d’adresse se produit lorsque plusieurs interfaces revendiquent la même adresse IPv4 dans un contexte où elles sont censées être uniques. Les symptômes courants comprennent une connectivité intermittente, des réponses qui arrivent au mauvais appareil, des entrées ARP qui alternent entre plusieurs MAC et des avertissements d’adresse dupliquée.

La RFC 5227 décrit notamment trois phases :

1. **Probing** : vérifier qu’une adresse candidate n’est pas déjà utilisée.
2. **Announcing** : annoncer l’adresse après son attribution, afin d’aider les voisins à rafraîchir leurs associations.
3. **Ongoing conflict detection/defense** : surveiller les conflits ultérieurs et appliquer une stratégie de défense définie par le protocole.

Ces procédures réduisent certains conflits accidentels, mais ne constituent pas une preuve d’unicité ni une authentification. Une machine malveillante peut ignorer les règles, émettre des messages trompeurs ou provoquer un conflit. Les systèmes peuvent aussi avoir des limitations lorsqu’ils démarrent, sont suspendus, sortent d’un réseau sans fil ou restaurent un état de VM.

La meilleure prévention reste une gestion d’adresses rigoureuse : DHCP correctement administré, réservation documentée, absence de chevauchement entre adresses statiques et pools dynamiques, contrôle du plan d’adressage, inventaire IPAM et surveillance des conflits. La détection ARP vient compléter ces moyens ; elle ne remplace pas la gouvernance de l’adressage.

### 1.10. Proxy ARP et Local Proxy ARP

Avec le Proxy ARP, un routeur répond à une requête ARP visant une autre adresse IP lorsque les conditions de routage et de configuration le permettent. Le routeur répond alors avec sa propre adresse MAC, ce qui amène le demandeur à transmettre les trames au routeur. Celui-ci route ensuite le paquet IP vers sa destination réelle.

Dans le modèle classique, le routeur doit disposer d’une route vers la destination et la route doit généralement sortir par une interface différente de l’interface sur laquelle la requête a été reçue. Le détail exact dépend de l’implémentation. Le Proxy ARP a historiquement permis de faire communiquer des hôtes utilisant des hypothèses d’adressage imparfaites, mais il peut masquer une mauvaise conception et rendre le dépannage moins évident.

**Local Proxy ARP** répond à un autre besoin : il peut permettre à deux hôtes appartenant au même préfixe IP de communiquer alors qu’ils sont séparés au niveau L2, en faisant passer le trafic par un routeur ou une passerelle L3. Il est notamment utile dans certains scénarios de private VLAN ou lorsqu’une architecture souhaite imposer un point de contrôle de couche 3 entre des équipements que l’adressage présente comme appartenant au même réseau.

| Fonction | Cible de la requête | Finalité typique | Conséquence |
|---|---|---|---|
| ARP ordinaire | Voisin local réel | Résoudre le voisin sur le lien | Le demandeur apprend la MAC du voisin |
| Proxy ARP | Adresse d’un hôte atteignable derrière le routeur | Masquer au demandeur la séparation L3 | Le demandeur apprend la MAC du routeur |
| Local Proxy ARP | Hôte du même préfixe IP mais séparé à L2 | Faire transiter le trafic par un point L3 | Le routage peut imposer un contrôle entre hôtes |

Le Proxy ARP doit être documenté, car il modifie le lien apparent entre préfixe et voisin. Une désactivation peut interrompre des hôtes qui dépendent de ce mécanisme ; une activation injustifiée peut rendre le réseau plus difficile à comprendre, augmenter l’exposition à certains détournements et masquer une erreur de masque ou de segmentation. La décision doit donc provenir du design, et non d’un dépannage improvisé.

### 1.11. Proxy ARP et mauvaises hypothèses de masque

Une erreur fréquente consiste à configurer un masque trop large sur un hôte. Ce dernier croit alors que certaines adresses distantes sont directement connectées et diffuse des demandes ARP au lieu d’envoyer le paquet à sa passerelle. Si un routeur fournit un Proxy ARP, il peut répondre et rendre la connectivité partiellement fonctionnelle malgré l’erreur d’adressage. Le symptôme est alors trompeur : l’accès fonctionne pour certaines destinations, mais le chemin emprunté ou les règles de sécurité peuvent être inattendus.

Un autre cas se produit lorsqu’une infrastructure sépare deux groupes dans des domaines L2 distincts tout en leur attribuant des adresses du même préfixe. Chaque hôte tente une résolution ARP directe qui ne franchit pas la frontière L2. Le Local Proxy ARP, une correction du plan IP ou un changement de segmentation peut être nécessaire selon le design. Étendre le VLAN pour « faire passer ARP » n’est pas automatiquement la bonne solution, car cela peut annuler les frontières de sécurité souhaitées.

Dans les réseaux modernes, les mécanismes de proxying peuvent aussi exister dans les fabrics et overlays, par exemple pour réduire la diffusion ARP dans certains environnements VXLAN/EVPN. Là, la réponse peut provenir d’une base de correspondances distribuée ou du point d’attachement du réseau virtuel. Il faut distinguer ce proxy d’un routeur IP traditionnel, même si le résultat visible sur le segment est similaire : répondre à la résolution afin d’éviter une diffusion plus large.

### 1.12. Table ARP et table MAC : deux tables, deux directions

Le cache ARP associe une adresse IPv4 à une MAC. La table MAC d’un commutateur associe une MAC à un port dans un VLAN. Les deux tables sont complémentaires, mais elles ne représentent pas le même état.

```text
Décision IP sur le routeur / hôte
              |
              |  Route vers 192.0.2.20
              v
Cache ARP / voisinage
192.0.2.20  ->  00:11:22:33:44:55
              |
              |  MAC de destination de la trame
              v
Table CAM du commutateur
VLAN 10, 00:11:22:33:44:55 -> Gi1/0/12
              |
              v
Envoi de la trame sur le port sélectionné
```

Si le cache ARP du routeur est correct, mais que la table MAC du commutateur pointe vers un port inattendu, le problème peut venir du déplacement d’une machine, d’une boucle L2, d’une MAC virtuelle, d’un trunk ou d’une usurpation de MAC. Inversement, une table MAC correcte ne garantit pas que le cache ARP de l’hôte associe l’adresse IP à la bonne MAC.

Lors d’une analyse, relever au minimum : le préfixe et la prochaine étape L3, l’association ARP observée sur le bon VLAN/VRF, la MAC de destination de la trame, le VLAN transporté et le port d’apprentissage de cette MAC. Sans corrélation entre ces éléments, il est facile de vider un cache sans corriger la cause réelle.

### 1.13. ARP dans les réseaux de haute disponibilité et de virtualisation

Le remplacement d’une interface, le déplacement d’une VM ou la bascule d’un routeur virtuel peuvent modifier la MAC associée à une adresse IP ou la topologie de livraison. La convergence exige que plusieurs états se mettent à jour : ARP sur les hôtes, tables MAC sur les commutateurs, associations des hyperviseurs et mécanismes d’overlay.

Une adresse IP virtuelle n’est pas nécessairement liée à la même MAC physique que l’adresse IP de gestion du routeur actif. Selon HSRP, VRRP et l’implémentation, une MAC virtuelle standardisée ou une MAC spécifique peut être utilisée. Les hôtes résolvent l’IP virtuelle en une MAC ; après un basculement, les annonces et le déplacement de l’association MAC doivent permettre d’atteindre le nouveau routeur actif.

Dans un environnement de VM, la MAC peut être visible à travers plusieurs couches de commutation : vSwitch/hyperviseur, switch ToR, overlay et passerelle. Une capture réalisée dans la VM peut ne pas montrer exactement les mêmes tags ou encapsulations qu’une capture sur le lien physique du serveur. Il est essentiel de comparer les points de capture et d’identifier l’endroit où ARP est encapsulé, décapsulé ou supprimé.

Dans VXLAN, la diffusion ARP d’un tenant peut être transportée dans l’overlay selon le modèle de contrôle et les mécanismes de flooding utilisés. Dans les architectures EVPN, la signalisation MAC/IP et les fonctions de suppression ARP permettent, lorsque le design et les équipements le prennent en charge, de répondre localement au lieu de diffuser chaque demande partout. Cette optimisation réduit le flooding, mais introduit une dépendance envers la cohérence de la base de correspondances du plan de contrôle.

### 1.14. ARP spoofing, cache poisoning et homme du milieu

ARP n’inclut pas d’authentification cryptographique intégrée qui permettrait au destinataire de prouver indépendamment qu’une annonce IPv4/MAC est légitime. Un attaquant présent dans le même domaine de diffusion peut essayer de diffuser de fausses annonces, par exemple prétendre que l’IP de la passerelle correspond à sa propre MAC. Si les hôtes acceptent la mise à jour, ils peuvent envoyer les trames destinées à la passerelle à l’attaquant.

Dans une attaque de type *man-in-the-middle*, l’attaquant tente de tromper plusieurs participants : la victime associe l’IP de la passerelle à la MAC de l’attaquant, et la passerelle ou les autres hôtes peuvent être amenés à associer l’IP de la victime à la MAC de l’attaquant. L’attaquant peut alors relayer le trafic pour préserver la connectivité tout en observant ou modifiant certains flux, ou au contraire interrompre le trafic dans une attaque de déni de service.

Les symptômes possibles sont des associations IP/MAC qui changent fréquemment, une MAC inhabituelle associée à la passerelle, plusieurs hôtes déclarant une adresse source identique, un grand nombre de réponses ARP non sollicitées ou des interruptions corrélées à un événement de couche 2. Aucun symptôme isolé ne suffit à prouver une attaque : la haute disponibilité, le déplacement d’une VM ou un conflit accidentel peuvent produire des changements de MAC légitimes.

L’attaquant doit généralement être présent dans le domaine L2 concerné ou contrôler une fonction capable d’injecter des trames dans ce domaine. Le risque s’étend donc à la taille et à la connectivité du domaine de diffusion. La segmentation limite le périmètre d’une attaque, mais tous les appareils dans le même VLAN ne sont pas protégés simplement parce que le VLAN possède un identifiant distinct.

### 1.15. Dynamic ARP Inspection et DHCP Snooping

Dynamic ARP Inspection (DAI), sur les commutateurs Cisco et autres plateformes qui disposent d’une fonction équivalente, vérifie les paquets ARP reçus sur des ports non approuvés. Dans le design courant, DAI compare les associations IP/MAC avec la base créée par DHCP Snooping. Les paquets qui ne respectent pas les associations attendues peuvent être rejetés et journalisés.

DHCP Snooping construit une base d’associations liée aux baux DHCP reçus et permet de distinguer les ports de confiance des ports non approuvés. Les interfaces vers des serveurs DHCP ou des équipements réseau légitimes peuvent nécessiter le statut trusted. Les ports utilisateurs sont normalement untrusted. Une erreur de confiance peut avoir un impact majeur : si le mauvais port est trusted, un équipement peut contourner les validations ; si le bon port n’est pas correctement intégré, des paquets légitimes ou réponses DHCP/ARP peuvent être bloqués.

DAI ne valide pas automatiquement toute adresse configurée statiquement si aucune association correspondante n’existe dans la base DHCP Snooping. Les réseaux avec des serveurs, imprimantes, équipements industriels ou adresses statiques peuvent nécessiter des ARP ACL ou les mécanismes propres à la plateforme. Le déploiement doit être testé avec les hôtes fixes, la haute disponibilité, les relais DHCP, les trunks et les liens EtherChannel concernés.

DAI est généralement appliqué à l’entrée des interfaces concernées et à des VLAN sélectionnés. Il ne contrôle pas universellement tout ARP dans tout le réseau, et sa disponibilité ou ses détails de comportement varient selon les familles de commutateurs et versions logicielles. La conception doit préciser les VLANs couverts, les trunks de confiance, la persistance de la base de bindings et les procédures de changement.

### 1.16. Autres contrôles de sécurité et leurs limites

La sécurité ARP ne repose pas sur un seul réglage. Les mesures complémentaires incluent :

- segmentation des domaines de diffusion selon les rôles et niveaux de confiance ;
- DHCP Snooping et DAI lorsque la plateforme les prend en charge ;
- limitation de débit des requêtes ARP sur les ports utilisateur, avec dimensionnement adapté ;
- contrôle de l’accès au réseau, par exemple via 802.1X/NAC ;
- journalisation des changements d’associations IP/MAC ;
- gestion de l’adressage, réservations DHCP et inventaire IPAM ;
- contrôle des ports physiques, des trunks et des accès non utilisés ;
- protection des équipements d’infrastructure et séparation du réseau de gestion.

Le port security qui limite des adresses MAC n’est pas l’équivalent de DAI. Il peut réduire certains abus de MAC selon sa configuration, mais il ne vérifie pas nécessairement que l’adresse IPv4 annoncée dans chaque paquet ARP correspond à la MAC source. De même, un pare-feu IP L3 peut ne jamais voir une attaque ARP qui perturbe la résolution à l’intérieur du VLAN.

Les entrées ARP statiques sont utiles pour certains environnements petits ou très contrôlés, mais elles ne s’adaptent pas bien à des milliers d’hôtes dynamiques, à des clusters ou à des migrations de VM. Une association statique erronée peut créer une panne silencieuse et compliquer la reprise après remplacement d’équipement.

### 1.17. Diagnostic par capture de paquets

Une capture ARP doit être analysée en considérant les champs Ethernet et ARP, le VLAN, l’interface de capture et le contexte temporel. Dans Wireshark, le filtre d’affichage `arp` permet de voir le trafic ARP. Des filtres plus ciblés peuvent être utilisés selon les champs exposés par la version : `arp.opcode == 1` pour les requêtes, `arp.opcode == 2` pour les réponses, ou une recherche par adresse IPv4/MAC dans les champs détaillés.

Pour une requête sans réponse, les questions principales sont :

1. La requête est-elle émise sur la bonne interface et dans le bon VLAN ?
2. L’adresse cible est-elle bien le prochain saut que la table de routage a choisi ?
3. La requête atteint-elle le domaine L2 attendu ?
4. L’équipement qui possède cette IP reçoit-il la requête ?
5. La réponse est-elle générée mais filtrée ou perdue en chemin ?
6. La réponse atteint-elle le demandeur avec les champs attendus ?
7. Le demandeur apprend-il effectivement l’association ou continue-t-il à émettre des requêtes ?

Pour un soupçon d’empoisonnement, il faut identifier l’adresse IP annoncée, la MAC revendiquée, l’adresse MAC Ethernet source, le port d’entrée et la périodicité. Il faut comparer les observations à l’inventaire d’adresses et à la table MAC du commutateur. Une MAC de passerelle modifiée après un basculement HA n’est pas automatiquement malveillante ; les journaux de redondance et les annonces GARP peuvent confirmer une cause légitime.

Une capture prise sur un port miroir peut perdre des trames si le SPAN est surchargé ou ne reflète pas le bon VLAN. Une capture logicielle sur l’hôte peut être effectuée avant ou après certaines transformations, selon l’interface et les fonctions d’offload. En cas d’incohérence, comparer plusieurs points de capture et les compteurs matériels plutôt que supposer que le premier PCAP reflète absolument tous les échanges sur le fil.

### 1.18. Particularités de systèmes d’exploitation

Les commandes de diagnostic et les politiques de voisinage varient selon les systèmes. Sur Linux moderne, `ip neigh show` est la référence habituelle pour consulter le cache des voisins ; `ip neigh flush` permet de demander la suppression de certaines entrées, avec des filtres qu’il faut manipuler prudemment. La commande historique `arp -n` existe encore sur certains systèmes mais n’est pas la méthode moderne privilégiée.

Sur Windows, `arp -a` affiche les associations IPv4 accessibles via l’outil historique. `Get-NetNeighbor` offre une vue PowerShell structurée, avec la famille d’adresses, l’interface et l’état du voisin. Les commandes de capture ou les outils de diagnostic doivent être lancés avec les permissions nécessaires.

Sur Cisco IOS/IOS XE, `show ip arp` affiche la table ARP IPv4 dans le contexte concerné, tandis que `show mac address-table` porte sur l’apprentissage MAC du commutateur. Les commandes exactes pour effacer ou inspecter les caches dépendent du logiciel et du type d’équipement. Un `clear arp-cache` peut provoquer une vague de nouvelles résolutions et doit donc être utilisé avec discernement sur une infrastructure chargée.

Il faut éviter de diagnostiquer une anomalie en vidant immédiatement tous les caches. Cela supprime des indices utiles et peut créer un pic de diffusion. Avant toute modification, capturer l’état initial, noter la MAC annoncée, l’interface, le VLAN, les compteurs et les horodatages. L’intervention doit viser la cause et conserver les éléments permettant de confirmer le rétablissement.

### 1.19. Algorithme d’investigation en situation d’incident

L’approche suivante permet de structurer l’analyse d’une panne ARP :

```text
Départ : un hôte ne peut pas joindre une destination IPv4
                         |
                         v
             Consulter la table de routage
                         |
                         v
         Identifier la véritable IP du prochain saut
                         |
                         v
           Consulter le cache ARP/voisinage
                         |
             +-----------+-----------+
             |                       |
        Association présente     Entrée absente/incomplète
             |                       |
             v                       v
 Vérifier la MAC et le VLAN       Capturer la requête ARP
             |                       |
             v                       v
 Corréler table MAC/port       Requête reçue par la cible ?
             |                       |
             v                 +-----+------+
 Vérifier chemin L2/L3         |            |
                         Oui / réponse    Non
                              |            |
                              v            v
                    Réponse émise ?   VLAN, trunk, ACL,
                              |        lien ou port erroné
                              v
                    Réponse reçue et
                    entrée installée ?
                              |
                              v
                  Vérifier filtrage, cache,
                  conflit IP ou association
```

Cette démarche est volontairement structurée du L3 vers le L2 : elle évite de supposer qu’une requête ARP doit être faite pour la destination IP finale alors que la route indique un prochain saut différent. Elle sépare également le problème de résolution de celui de l’acheminement après résolution.

> **Piège :** Ne confonds pas « l’adresse IP est dans le même préfixe » et « les deux hôtes partagent réellement le même domaine L2 ». Une erreur de masque peut forcer un hôte à rechercher directement une MAC qui n’est pas accessible dans son VLAN. Inversement, Proxy ARP peut masquer cette erreur en donnant la MAC du routeur. Avant de modifier ARP, vérifie la route sélectionnée, le préfixe, le VLAN, l’interface et le véritable prochain saut.

```text
Scénario A : ARP ordinaire

Hôte A                 VLAN 10                 Hôte B
192.0.2.10/24     diffusion FF:FF:FF:FF:FF:FF  192.0.2.20/24
   |-------------------- ARP Request ------------->|
   |<------------------- ARP Reply -----------------|
   |                                                |
   +---- cache : 192.0.2.20 -> MAC-B ---------------+

Scénario B : destination distante

Hôte A             Passerelle                    Hôte distant
192.0.2.10         192.0.2.1                     198.51.100.20
   |-- ARP pour 192.0.2.1 -->|
   |<-- MAC de passerelle ---|
   |-- Trame MAC-R1, IP-dst=198.51.100.20 -------->|
                         routage et nouvelle trame

Scénario C : cache poisoning (conceptuel)

Victime cache : 192.0.2.1 -> MAC légitime
Attaquant annonce : 192.0.2.1 -> MAC attaquant
Si la mise à jour est acceptée, certaines trames vers
la passerelle peuvent être dirigées vers l'attaquant.
```

---

## 2. Configuration et Pratique

### 2.1. Principes de configuration opérationnelle

ARP est généralement automatique dès qu’une interface IPv4 possède une adresse et participe à un réseau Ethernet compatible. La plupart des configurations n’exigent donc pas une activation globale du protocole. Le travail d’ingénierie porte plutôt sur l’adressage IP, le routage, les caches, les associations statiques lorsque leur usage est justifié, le Proxy ARP et les protections de couche 2.

Les commandes Cisco changent selon la famille de matériel et la version IOS/IOS XE/NX-OS. Les blocs ci-dessous illustrent les concepts courants ; il faut vérifier la syntaxe précise sur la plateforme utilisée et éviter de les copier sans adapter les noms d’interface, les VLAN, les adresses et la politique de sécurité.

### 2.2. Configuration d’un routeur avec un LAN et une passerelle

Exemple : un routeur joue la passerelle du VLAN 10 (`192.0.2.0/24`). Les hôtes doivent résoudre la MAC de `192.0.2.1` lorsqu’ils contactent un réseau distant.

```cisco
hostname R1

interface GigabitEthernet0/0
 description LAN_VLAN10
 ip address 192.0.2.1 255.255.255.0
 no shutdown

! Exemple seulement : l'interface WAN ou de transit est à adapter.
interface GigabitEthernet0/1
 description TRANSIT_VERS_RESEAU_AMONT
 ip address 198.51.100.2 255.255.255.252
 no shutdown

! Exemple de route par défaut ; le prochain saut doit être réellement joignable.
ip route 0.0.0.0 0.0.0.0 198.51.100.1
```

Dans ce scénario, ARP sur le LAN sert à résoudre les hôtes locaux ou la MAC de la passerelle vue par les clients. ARP sur le réseau de transit permet au routeur de résoudre son prochain saut `198.51.100.1`, si le type de lien et la configuration utilisent Ethernet. La route par défaut n’ajoute pas directement une entrée ARP ; elle indique seulement comment choisir un prochain saut.

Les commandes de vérification de base sont :

```cisco
show ip interface brief
show ip route
show ip arp
show interfaces GigabitEthernet0/0
```

`show ip arp` permet de confirmer les associations connues par le routeur. Il faut observer l’adresse IP, la MAC et l’interface associées. Une entrée absente peut être normale si aucune résolution n’a encore eu lieu vers la destination ou si elle a expiré.

### 2.3. Association ARP statique

Une entrée statique associe administrativement une adresse IPv4 à une MAC. Sur Cisco IOS, une forme classique de commande globale est :

```cisco
arp 192.0.2.50 0011.2233.4455 arpa
```

Cette commande est illustrative : il faut vérifier la syntaxe et le comportement sur la plate-forme visée. L’adresse `192.0.2.50` appartient à une plage réservée à la documentation ; remplace-la par l’adresse d’un laboratoire réel lors des essais.

Une association statique peut être utilisée dans un réseau limité, pour certains équipements particuliers ou dans des scénarios contrôlés. Elle peut empêcher l’apprentissage dynamique de modifier la correspondance visée selon l’implémentation. Toutefois, la stratégie augmente la charge de gestion : si la carte réseau change, si la VM migre ou si la destination passe derrière une nouvelle MAC, la configuration statique doit être mise à jour.

Ne déploie pas d’entrées statiques en masse comme substitut à DAI, à la segmentation ou à un mécanisme de contrôle de l’accès. Si le nombre d’hôtes est important, les associations doivent être gérées par des mécanismes de sécurité évolutifs et des outils d’inventaire.

### 2.4. Temporisation du cache ARP

Certaines plateformes Cisco permettent de régler le délai d’expiration des entrées ARP dynamiques au moyen d’une commande telle que `arp timeout` sur l’interface. La portée et la syntaxe peuvent varier selon l’OS réseau et la version.

```cisco
interface GigabitEthernet0/0
 ! Exemple à valider selon IOS/IOS XE et le modèle :
 arp timeout 600
```

La valeur d’exemple ne doit pas être utilisée sans étude préalable. Un délai trop court provoque davantage de résolutions et potentiellement davantage de diffusion ; un délai trop long peut conserver plus longtemps une correspondance devenue obsolète après une migration ou une bascule. La bonne valeur dépend du comportement du réseau, des mécanismes de haute disponibilité et des exigences opérationnelles.

Avant de toucher aux temporisateurs, mesurer la fréquence des requêtes, la nature des incidents et le fonctionnement de l’apprentissage MAC. Une panne après déplacement de serveur peut être liée à la table MAC, à ARP ou aux deux. Raccourcir un timer sans identifier quel état est obsolète ne constitue pas un diagnostic.

### 2.5. Activer ou désactiver Proxy ARP

Sur de nombreuses plateformes Cisco IOS, le Proxy ARP est contrôlé par une commande d’interface. La forme classique est :

```cisco
interface GigabitEthernet0/0
 ip proxy-arp
```

Pour le désactiver sur une interface où il n’est pas requis :

```cisco
interface GigabitEthernet0/0
 no ip proxy-arp
```

Vérifie l’état et le comportement selon la version logicielle. Ne désactive pas aveuglément Proxy ARP sur un réseau existant : des hôtes configurés avec des masques erronés ou des designs historiques peuvent en dépendre. À l’inverse, ne l’active pas pour réparer un problème de connectivité avant d’avoir confirmé le plan d’adressage et la topologie L2/L3.

Le Local Proxy ARP porte une syntaxe et une prise en charge qui varient selon les gammes. Sur certaines plateformes, le mot-clé de configuration ressemble à `ip local-proxy-arp`. Le document de configuration de l’équipement doit être consulté avant toute mise en œuvre. Il faut vérifier le cas d’usage spécifique, par exemple l’isolation L2 d’hôtes partageant un préfixe IP, et mesurer le trafic qui sera forcé à passer par la passerelle.

### 2.6. Déployer DHCP Snooping et Dynamic ARP Inspection

Dans un design d’accès Cisco IOS/IOS XE qui prend en charge ces fonctions, un exemple conceptuel est présenté ci-dessous. Il suppose que le VLAN 10 utilise DHCP et qu’un lien uplink conduit vers l’infrastructure DHCP. Les commandes et options exactes varient selon la gamme et la version.

```cisco
! Activer DHCP Snooping globalement et sur le VLAN concerné
ip dhcp snooping
ip dhcp snooping vlan 10

! Activer DAI sur le VLAN concerné
ip arp inspection vlan 10

interface GigabitEthernet1/0/10
 description POSTE_UTILISATEUR_VLAN10
 switchport mode access
 switchport access vlan 10
 ! Le port utilisateur reste untrusted par défaut.

interface GigabitEthernet1/0/48
 description UPLINK_VERS_INFRASTRUCTURE_DHCP
 switchport mode trunk
 ! N'accorder le statut trust que si ce lien et le chemin en amont
 ! sont approuvés et protégés conformément au design.
 ip dhcp snooping trust
 ip arp inspection trust
```

Ce bloc ne doit pas être transposé tel quel sans confirmer la topologie. L’interface de confiance doit correspondre à une connexion de réseau maîtrisée, pas simplement à un port qui « ressemble à un uplink ». Un équipement compromis connecté à un port trusted peut potentiellement contourner les vérifications DAI qui s’appliquent aux ports untrusted.

Si le réseau utilise des adresses statiques, des serveurs, des imprimantes ou des équipements d’infrastructure qui n’obtiennent pas leurs adresses via DHCP, la base de DHCP Snooping peut ne pas contenir leurs associations. Il peut être nécessaire de configurer les ARP ACL prises en charge, ou d’utiliser le mécanisme de validation correspondant à la plateforme. Tester d’abord un VLAN pilote évite de bloquer des équipements critiques.

### 2.7. Limitation du débit ARP

DAI et certaines fonctions de sécurité permettent de limiter le débit de paquets ARP entrant sur certains ports. Le but est de détecter ou de limiter une émission anormalement intensive, sans empêcher le trafic normal d’un poste ou d’un serveur.

Une limite trop faible peut bloquer les annonces légitimes lors d’un démarrage en masse, d’une restauration de VM, d’un événement de haute disponibilité ou d’une migration. Une limite trop élevée peut ne pas contrôler efficacement un abus. Il faut utiliser les valeurs recommandées par la documentation de la plateforme comme point de départ, puis valider les volumes dans l’environnement réel.

Un contrôle de débit ne remplace pas la validation IP/MAC. Un attaquant peut émettre à faible débit et tenter quand même un empoisonnement ; inversement, de nombreux hôtes qui démarrent en même temps peuvent générer un pic légitime. Les métriques, la journalisation et la définition des ports de confiance doivent être conçues ensemble.

### 2.8. Commandes de vérification sur les commutateurs

Les commandes suivantes permettent de vérifier les états qui influencent la résolution :

```cisco
show ip arp
show mac address-table dynamic
show vlan brief
show interfaces trunk
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection
show ip arp inspection statistics
show logging
```

Selon la plateforme, certaines commandes peuvent être absentes ou porter une syntaxe différente. Leur objectif est de répondre à des questions précises : quelle IP est associée à quelle MAC ? Dans quel VLAN cette MAC est-elle apprise ? Le port est-il access ou trunk ? Le VLAN est-il autorisé sur le trunk ? Le binding DHCP existe-t-il ? DAI a-t-il rejeté des paquets ?

Ne te contente pas d’une sortie globale. Cherche l’entrée concernée, relève l’interface et compare-la au plan physique et à la table de voisinage du routeur ou de l’hôte. Pour un incident intermittent, répète les relevés avec horodatage ou collecte des logs afin d’identifier les changements.

### 2.9. Commandes de diagnostic sur les hôtes

| Système | Consultation du cache | Capture conseillée |
|---|---|---|
| Linux | `ip neigh show` | `tcpdump -eni eth0 arp` |
| Windows | `arp -a` ou `Get-NetNeighbor` | Wireshark ou capture ETW adaptée |
| Cisco IOS/IOS XE | `show ip arp` | SPAN/ERSPAN ou mécanismes de capture disponibles |
| Wireshark | Filtre `arp` | Comparer requêtes, réponses, VLAN et MAC |

Sur Linux, `ip neigh show dev eth0` limite l’observation à une interface particulière. Pour supprimer une entrée dans un laboratoire, une commande telle que `ip neigh del 192.0.2.20 dev eth0` peut être utilisée si l’entrée existe ; elle doit être exécutée avec les privilèges appropriés et avec une adresse/interface correctes. Sur Windows, les opérations de suppression et de rafraîchissement dépendent des commandes disponibles et des droits administratifs.

Le but d’un effacement de cache pendant un diagnostic est de reproduire une résolution et d’observer le protocole. Il faut éviter de le faire sur tous les postes ou sur une passerelle de production en l’absence de plan, car l’opération peut provoquer une hausse des diffusions et supprimer des indices forensiques.

### 2.10. Capture ciblée et filtres Wireshark

Un filtre d’affichage Wireshark courant est :

```text
arp
```

Pour se concentrer sur les requêtes ou réponses, selon les noms de champs pris en charge par la version :

```text
arp.opcode == 1
arp.opcode == 2
```

Il est aussi possible de filtrer sur une adresse ciblée avec les champs ARP visibles dans le décodeur. Le nom exact du champ doit être confirmé dans la version de Wireshark utilisée. La lecture de la colonne Info est utile pour une première analyse, mais les détails de paquets sont nécessaires pour valider `SPA`, `TPA`, `SHA`, `THA`, EtherType et VLAN.

Une bonne capture comprend suffisamment de contexte avant et après l’événement. Le premier paquet peut être une sonde de conflit, une annonce après une bascule ou une résolution normale ; les paquets suivants montrent si une réponse correspond, si l’association se modifie ou si les tentatives continuent. Un seul paquet ARP isolé ne prouve pas l’intention de l’émetteur.

### 2.11. Exemple de procédure de changement sécurisé

Avant de modifier Proxy ARP, DAI, les temporisateurs ou une entrée statique, préparer une procédure de changement :

1. documenter les adresses IP, les MAC, les interfaces et les VLAN concernés ;
2. sauvegarder la configuration et relever les tables ARP/MAC initiales ;
3. confirmer quels équipements utilisent DHCP et lesquels sont statiques ;
4. tester le changement dans un VLAN pilote ou une fenêtre de maintenance ;
5. mesurer les rejets ARP, les journaux, la connectivité et la convergence ;
6. appliquer le changement par lots limités ;
7. conserver un plan de retour arrière qui rétablit la configuration précédente ;
8. valider les flux aller et retour, les applications critiques et les bascules éventuelles.

La surveillance après changement est aussi importante que la validation immédiate. Un poste peut déjà posséder une entrée ARP correcte et rester fonctionnel alors que le nouveau contrôle bloque une résolution future. Il faut donc provoquer prudemment une nouvelle résolution sur un hôte de test et surveiller les logs DAI/Snooping.

> **Astuce :** Avant d’effacer un cache ARP, capture d’abord la correspondance suspecte et l’état de la table MAC du commutateur. Note la MAC, le VLAN, le port et l’horodatage. Ensuite seulement, dans une fenêtre maîtrisée, provoque une nouvelle résolution et compare le résultat. Cette séquence conserve les indices de la panne et permet de distinguer une entrée simplement obsolète d’un apprentissage incorrect qui se reproduit.

---

## 3. Dépannage et Sécurité

### 3.1. La requête ARP n’obtient aucune réponse

Commence par confirmer que l’hôte doit réellement résoudre la cible par ARP. Examine le masque et la route sélectionnée. Pour une destination distante, la cible ARP sera probablement la passerelle et non le serveur. Sur le routeur, la table de routage doit indiquer le prochain saut ou le réseau directement connecté attendu.

Si la cible est bien locale, vérifie l’adresse IP de l’hôte, son interface, le VLAN, le trunk et l’état de la liaison. Capture la requête sur le port source puis sur le segment cible si possible. Si elle n’arrive pas à destination, chercher une erreur de VLAN, une liste de VLAN autorisés sur un trunk, un filtrage L2, un port err-disabled ou une séparation de domaine de diffusion. Si elle arrive, mais qu’aucune réponse n’est émise, confirmer que l’hôte possède l’adresse et que sa pile IPv4 est opérationnelle.

Si une réponse est émise, mais que le demandeur ne l’apprend pas, examiner le chemin retour, l’association Ethernet destination, une éventuelle inspection ARP, les ACL de couche 2 et les politiques de sécurité. Une entrée `INCOMPLETE` qui persiste peut indiquer que le système a lancé la résolution mais n’a pas accepté de réponse avant l’expiration de ses tentatives.

### 3.2. L’adresse IP est associée à une MAC inattendue

Ne supprime pas immédiatement l’entrée. Capture le trafic qui a créé ou rafraîchi l’association ; vérifie la source Ethernet et les champs ARP, puis corrèle la MAC avec la table MAC du commutateur et l’inventaire d’actifs. Compare le moment du changement avec les événements HSRP/VRRP, migration de VM, remplacement de NIC ou modification de chemin.

Si une MAC inattendue se trouve sur un port utilisateur et revendique l’IP de la passerelle, il peut s’agir d’une usurpation. Si la MAC apparaît sur le port d’un nouveau routeur actif à la suite d’une bascule documentée, le changement peut être légitime. Le traitement doit s’appuyer sur des preuves : capture, logs, bindings DHCP, localisation physique et état du plan de contrôle.

Lorsque DAI est actif, vérifie les statistiques de rejets, les ARP ACL et la base DHCP Snooping. Un blocage de trafic légitime peut provenir d’un binding absent, d’une association IP/MAC statique non déclarée ou d’un port de confiance mal configuré. Il ne faut pas désactiver DAI globalement pour rétablir rapidement un seul poste sans avoir trouvé la règle de validation en cause.

### 3.3. Conflit IP intermittent

Un conflit IP peut produire un comportement qui ressemble à une panne d’ARP : les entrées changent entre deux MAC et les réponses arrivent parfois au mauvais équipement. Il faut rechercher les annonces où `SPA` égale l’adresse contestée, les probes de détection, les événements DHCP et les journaux des terminaux.

Vérifie ensuite :

- si l’adresse appartient à un pool DHCP actif ;
- si elle a été attribuée en statique à un serveur, une imprimante ou une appliance ;
- si une réservation ou une ancienne entrée DHCP est toujours présente ;
- si deux VLANs qui ne devraient pas communiquer partagent une extension L2 inattendue ;
- si une VM clonée a conservé une configuration IP statique ;
- si une bascule HA ou une IP virtuelle explique l’annonce.

La correction définitive consiste à éliminer le doublon à la source et à mettre à jour l’inventaire. Vider le cache sur le client peut restaurer temporairement une association, mais le conflit continuera tant que deux équipements revendiquent la même IP.

### 3.4. DAI bloque des hôtes légitimes

DAI compare généralement les paquets ARP reçus aux associations de confiance. Un hôte à adresse statique peut ne pas avoir de binding DHCP ; un serveur DHCP ou une appliance peut se trouver derrière un port d’accès ou un trunk qui a été classé incorrectement. Il faut contrôler le VLAN ciblé, les trusts, les bindings, les ARP ACL, les journaux et les restrictions de la plate-forme.

La séquence de vérification est :

1. identifier le paquet rejeté, le port d’entrée, le VLAN, SPA/SHA et TPA/THA ;
2. vérifier si la MAC/IP existe dans la base DHCP Snooping ;
3. si la machine est statique, comparer la configuration à la politique d’ARP ACL ;
4. vérifier que la confiance du lien est justifiée et cohérente avec le design ;
5. ajouter uniquement la déclaration nécessaire, en suivant la documentation de la version ;
6. retester avec une résolution neuve et confirmer que le taux de rejets est revenu à la normale.

Le port trusted est une décision de sécurité. Le rendre trusted uniquement pour contourner une erreur de binding peut supprimer l’inspection sur un chemin plus large que prévu. La modification doit être limitée, documentée et testée avec le chemin complet.

### 3.5. Cache ARP obsolète après basculement

Après un changement d’équipement actif, un routeur ou un serveur peut reprendre la même IP en utilisant une autre MAC. Certains voisins mettent à jour leur cache grâce aux annonces ARP ou aux requêtes ultérieures ; d’autres continuent temporairement à utiliser l’ancienne association. La table MAC du commutateur peut également devoir apprendre l’emplacement actuel de la MAC.

Vérifie le protocole de redondance, la MAC virtuelle prévue, les annonces au moment de la bascule et les entrées ARP sur les voisins affectés. Si la MAC doit rester constante, examine plutôt le déplacement de cette MAC à travers la structure de commutation et les états de port. Si elle change légitimement, confirme que les annonces et la convergence sont conformes à la conception.

Un effacement de cache ciblé peut servir de test, mais ne prouve pas que le réseau converge correctement de manière autonome. Le test de résilience doit mesurer le temps de rétablissement sans intervention manuelle et vérifier les hôtes représentatifs de plusieurs VLANs.

### 3.6. Problème ARP à travers un trunk ou un EtherChannel

Lorsqu’une requête est visible sur un port d’accès mais pas sur l’uplink attendu, vérifier l’état du VLAN, les VLANs autorisés sur le trunk, l’encapsulation, les ports membres de l’EtherChannel et les états STP. Une discordance de configuration sur un seul membre peut entraîner des comportements asymétriques ou des sorties différentes selon le hachage du trafic.

Pour un problème qui concerne un seul VLAN, la cause peut être une liste de VLANs autorisés ou un VLAN natif incohérent plutôt qu’ARP. Dans une capture, vérifier les métadonnées VLAN et le point où le tag est inséré ou retiré. Une capture logicielle à l’intérieur d’un serveur peut montrer la trame avant le tagging physique, tandis qu’un SPAN externe peut présenter le tag.

La table MAC du commutateur permet de localiser l’apprentissage de l’adresse cible. Si la MAC se déplace sans explication entre plusieurs ports, rechercher une boucle L2, une redondance mal configurée, une virtualisation ou une usurpation. L’analyse doit associer l’événement MAC-move aux horodatages de la panne ARP.

### 3.7. Charge élevée de requêtes ARP

Une augmentation du trafic ARP peut résulter d’un grand domaine de diffusion, d’un cache qui expire trop fréquemment, de nombreuses adresses IP destinées à des voisins absents, d’une boucle applicative, d’un scan, d’un conflit de configuration ou d’une attaque. Le volume doit être comparé à l’activité réelle du VLAN.

Commence par grouper les paquets par IP source, MAC source, TPA et port d’entrée. Une seule source qui émet un grand nombre de demandes vers de multiples cibles peut indiquer un scan ou une application mal configurée. De nombreuses sources demandant une seule IP peuvent révéler une passerelle ou un serveur indisponible. Une hausse simultanée de broadcast et des erreurs L2 peut orienter vers une boucle ou un problème de commutation.

Les limites de débit et storm control peuvent réduire l’impact, mais elles doivent être dimensionnées afin de ne pas bloquer des événements normaux, notamment au démarrage de centaines de VM ou de terminaux. Il faut identifier la cause et restaurer la cohérence de la résolution plutôt que simplement masquer le symptôme.

### 3.8. Analyse des risques de sécurité

ARP doit être considéré comme un protocole de confiance locale : dans son fonctionnement de base, il n’authentifie pas l’identité du propriétaire d’une adresse. Les risques importants sont :

- **Cache poisoning** : fausser les correspondances IPv4/MAC pour rediriger des trames.
- **Man-in-the-middle** : intercepter et éventuellement relayer le trafic à travers l’équipement attaquant.
- **Déni de service** : faire pointer des voisins vers une MAC inexistante ou rendre les associations incohérentes.
- **Usurpation d’adresse** : revendiquer l’adresse IP ou MAC d’une infrastructure légitime.
- **Saturation de diffusion** : multiplier les résolutions et consommer les ressources de contrôle.
- **Conflit accidentel ou malveillant** : provoquer une alternance de réponses pour la même adresse IP.

L’impact varie selon les contrôles en place, les applications, le chiffrement de bout en bout, la visibilité de l’attaquant et le domaine L2. Le chiffrement applicatif peut limiter l’exploitation de certaines données interceptées, mais n’empêche pas le déni de service ni le détournement de trafic et ne doit pas être considéré comme un substitut à la sécurité de couche 2.

### 3.9. Réponse à incident ARP spoofing

Une réponse structurée doit préserver les preuves et contenir le problème sans élargir inutilement l’interruption :

1. relever les associations anormales, les captures et les logs avant de vider les caches ;
2. déterminer le ou les ports qui injectent les annonces suspectes en corrélant MAC, table CAM et inventaire ;
3. confirmer si l’événement correspond à une bascule autorisée ou à une modification connue ;
4. si une compromission est probable, isoler le port ou l’appareil selon la procédure d’incident ;
5. vérifier DAI, DHCP Snooping, les trusts et la politique de VLAN sur tous les chemins concernés ;
6. rétablir les associations légitimes et tester les flux critiques ;
7. conserver les captures, les journaux et la chronologie de l’incident ;
8. corriger la cause et étendre les contrôles à tout le domaine touché lorsque nécessaire.

Une coupure immédiate du port peut être nécessaire pour contenir une attaque, mais elle doit être menée selon l’impact métier et les procédures d’escalade. Si le port appartient à un trunk ou à un serveur d’infrastructure mutualisé, l’isolement peut affecter de nombreux services ; la localisation de la source doit donc être aussi précise que possible.

### 3.10. Limites de la protection et architecture défensive

DAI protège les domaines et les ports où il est activement configuré. Un équipement non géré, un commutateur sans inspection ou un VLAN non couvert peut constituer un contournement. La politique doit donc être appliquée de façon cohérente dans toute la chaîne L2, en particulier lorsqu’un VLAN s’étend sur plusieurs commutateurs ou traverse plusieurs chemins d’accès.

Les ports de confiance doivent être réduits au strict nécessaire. Dans les liens entre commutateurs, DAI et DHCP Snooping doivent être conçus selon les rôles de chaque équipement et la manière dont les associations sont distribuées. La base DHCP Snooping doit survivre aux événements de maintenance selon les capacités de la plateforme. Les équipements à adresse statique doivent être traités explicitement, plutôt que de désactiver la vérification pour le VLAN entier.

Une architecture à défense en profondeur combine DAI, DHCP Snooping, segmentation, contrôle d’accès, supervision, gestion des actifs et procédure d’intervention. Aucune de ces mesures n’étant parfaite, la visibilité des changements de MAC/IP est essentielle. Les journaux doivent être envoyés vers une infrastructure de collecte et leur rétention doit permettre de reconstruire la chronologie des événements.

> **Danger :** Une fausse association ARP peut rediriger les flux internes sans modifier les tables de routage IP. Le routeur peut conserver des routes parfaitement correctes tandis que les trames sont envoyées vers une MAC contrôlée par un autre équipement. Ce découplage rend l’empoisonnement difficile à détecter avec des outils purement L3. Contrôle les associations IP/MAC, la table MAC des commutateurs et les journaux de sécurité ; n’accorde pas une confiance implicite aux annonces ARP provenant d’un VLAN utilisateur.

### 3.11. Liste de validation avant mise en production

Avant de livrer une configuration ARP, Proxy ARP ou DAI, vérifier les points suivants :

- Le plan IP et les masques sont cohérents avec les véritables domaines L2.
- Les routes et prochains sauts attendus sont confirmés sur les équipements clés.
- Les associations ARP/MAC sont observables et corrélées aux ports/VLANs.
- Les interfaces de confiance DAI/DHCP Snooping sont justifiées, documentées et minimales.
- Les adresses statiques ont une méthode de validation adaptée.
- Les serveurs DHCP, les relais, les trunks et les EtherChannels ont été testés.
- Les procédures de haute disponibilité et les migrations ont été validées.
- Les seuils de débit et la journalisation ont été dimensionnés selon le trafic réel.
- La procédure de retour arrière est documentée.
- Les tests couvrent la connectivité aller-retour, la nouvelle résolution après expiration et le basculement.

### 3.12. Références techniques de référence

- **RFC 826 — An Ethernet Address Resolution Protocol** : format ARP et algorithme de traduction des adresses de protocole en adresses matérielles. https://www.rfc-editor.org/rfc/rfc826
- **RFC 5227 — IPv4 Address Conflict Detection** : sondes, annonces et détection des conflits d’adresse IPv4. https://www.rfc-editor.org/rfc/rfc5227
- **RFC 1122 — Requirements for Internet Hosts — Communication Layers** : exigences et comportements attendus pour les hôtes Internet, dont les aspects de résolution d’adresse. https://www.rfc-editor.org/rfc/rfc1122
- **Cisco IOS XE — Address Resolution Protocol** : configuration et vérification ARP, entrées statiques, cache et Proxy ARP. https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_arp-config-arp-0.html
- **Cisco IOS XE — Dynamic ARP Inspection** : inspection IP/MAC, rôle de DHCP Snooping, ports trusted/untrusted et procédures de configuration. https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/sec-crypto/fhs-sisf/fhs-and-sisf-configuration-guide/dynamic-arp-inspection.html
- **Cisco — Proxy ARP and Local Proxy ARP** : différences entre réponses Proxy ARP classiques et Local Proxy ARP dans les contextes pris en charge. https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/ipaddresses-and-services/configuration-guide/ip-addresses-and-services-config-cisco8000/address-resolution/proxy-arp-and-local-proxy-arp.html
- **RFC 7348 — VXLAN** : transport L2 sur un réseau L3 et rôle de la résolution ARP dans un overlay VXLAN. https://www.rfc-editor.org/rfc/rfc7348

## Points à retenir

- **ARP ne choisit pas la route : il résout la MAC du prochain saut déterminé par la couche 3.** Pour une destination distante, le demandeur résout généralement la passerelle ou le prochain routeur, tandis que l’adresse IP finale demeure dans le paquet IP.
- **La table ARP et la table MAC du commutateur sont complémentaires, mais distinctes.** Le cache ARP associe IP et MAC ; la table MAC associe MAC, VLAN et port. Un diagnostic fiable doit corréler les deux avec la route, l’interface et le domaine de diffusion.
- **ARP de base n’authentifie pas cryptographiquement les associations annoncées.** Les annonces gratuites, les changements de MAC légitimes et les attaques peuvent parfois se ressembler ; la capture et la corrélation avec les logs sont indispensables.
- **Proxy ARP est un mécanisme de conception, pas un correctif universel.** Il peut masquer des erreurs de masque ou permettre une isolation L2 intentionnelle, mais il doit être documenté et testé.
- **DAI et DHCP Snooping exigent une politique de confiance exacte.** Les ports trusted doivent être limités, les hôtes statiques pris en charge explicitement et les VLANs couverts validés avant le déploiement global.
- **Préserve les preuves avant de nettoyer les caches.** Relever les associations, la table MAC, les captures, les bindings DHCP et les événements de redondance permet de distinguer une entrée périmée, un conflit IP, un défaut L2 et une attaque.
