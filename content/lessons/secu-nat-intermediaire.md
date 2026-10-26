# NAT et sécurité du périmètre

> **Mise en contexte**
>
> Une entreprise utilise des adresses privées pour ses postes et ses serveurs. Son routeur doit permettre aux employés d'accéder à Internet, tandis que certains services internes doivent être publiés de manière contrôlée. La traduction d'adresses réseau, ou NAT, aide à relier des espaces d'adressage différents ; mais elle ne remplace ni le pare-feu, ni le routage, ni la segmentation. Une redirection de port mal maîtrisée peut exposer un service sensible sans que l'administrateur s'en rende compte.
>
> Ce cours approfondit les types de NAT, le PAT, les adresses inside local/global et outside local/global, les ACL utilisées pour sélectionner le trafic à traduire, les redirections de services, les interactions avec les pare-feu et les VPN, les limites du NAT, ainsi que le diagnostic sur Cisco IOS. Tous les scénarios sont fictifs et prévus pour un laboratoire autorisé. Toute configuration qui publie un service ou modifie le périmètre doit être préparée, testée et accompagnée d'un plan de retour arrière.

## 1. Objectifs pédagogiques et prérequis

À la fin de ce cours, tu devras savoir expliquer pourquoi la traduction d'adresses est utilisée, distinguer NAT statique, NAT dynamique et PAT, lire les quatre terminologies d'adresses du NAT traditionnel, calculer l'effet d'une traduction sur un flux, configurer des exemples Cisco IOS dans un laboratoire, publier un service à l'aide d'une redirection de port limitée, expliquer pourquoi une ACL de sélection NAT n'est pas nécessairement une ACL de sécurité, diagnostiquer les erreurs de NAT, évaluer les risques du NAT à double étage et proposer une architecture de périmètre plus sûre.

Les prérequis sont les adresses IPv4 privées et publiques, les masques, les routes, TCP/UDP, les ports et le rôle d'un pare-feu. Les exemples de commandes utilisent la syntaxe courante de Cisco IOS/IOS XE ; elle peut varier selon la version et la gamme d'équipement. Consulte toujours la documentation correspondant au système réel.

## 2. Pourquoi utiliser NAT ?

Les adresses IPv4 privées sont utilisées à l'intérieur de nombreux réseaux qui ne sont pas directement routés sur l'Internet public. Une traduction à la frontière permet à ces systèmes de communiquer avec des destinations externes tout en utilisant un espace d'adressage interne. Le NAT peut également faciliter des changements d'adressage interne ou la publication contrôlée d'un service à une adresse externe.

La traduction d'adresses de base associe une adresse interne à une adresse externe. La traduction d'adresses et de ports, connue sous les appellations PAT ou NAPT, permet à plusieurs hôtes de partager une seule adresse IPv4 publique en différenciant des sessions grâce aux informations de transport, notamment les ports TCP/UDP. Ce partage est courant dans les routeurs domestiques et les réseaux d'entreprise.

~~~text
Poste A 192.168.10.11:51001 --\
Poste B 192.168.10.12:51001 ----> [ Routeur NAT ] ----> Internet
Poste C 192.168.10.13:51001 --/     198.51.100.25
                                    adresse publique
~~~

Le schéma est conceptuel. Chaque session peut être associée à un port externe distinct pour que le routeur sache à quel hôte interne renvoyer les réponses. Même lorsque deux postes utilisent le même port source local, la traduction peut leur attribuer des ports externes différents.

Le NAT ne remplace pas la route par défaut. Le routeur doit savoir où envoyer le paquet et la destination doit pouvoir acheminer la réponse. Il ne remplace pas non plus le filtrage de sécurité : le fait qu'une adresse interne soit traduite ne constitue pas, à lui seul, une autorisation ou un refus explicite.

## 3. NAT et sécurité : ne pas confondre les rôles

Il faut distinguer plusieurs fonctions qui se trouvent souvent sur le même routeur ou pare-feu :

- **Routage :** choisit le prochain saut et la route vers une destination.
- **NAT :** traduit des adresses IP et parfois des ports.
- **Filtrage :** décide si le trafic est autorisé selon une politique.
- **Suivi d'état :** suit les sessions afin de distinguer les paquets de retour d'une nouvelle connexion, selon les capacités du dispositif.
- **Publication applicative :** expose un service interne selon une adresse et un port externes précis.
- **Journalisation :** enregistre des événements utiles au diagnostic et à l'investigation.

Une redirection de port peut être configurée en même temps qu'une règle de pare-feu autorisant l'accès, mais ce sont deux opérations conceptuellement différentes. La traduction indique où le paquet doit être envoyé après traduction ; le filtrage détermine si la communication est autorisée. Certains produits associent automatiquement des effets à leurs règles NAT ou utilisent un modèle unifié : il faut lire la documentation au lieu de supposer que tous les appareils se comportent pareil.

Une adresse IPv4 privée rend généralement le service non directement routable depuis Internet, mais elle ne protège pas les services d'un accès non autorisé provenant du réseau local, du VPN, d'un VLAN adjacent ou d'une redirection configurée. Un NAT ne détecte pas les vulnérabilités d'une application et ne fournit pas d'authentification forte.

## 4. Terminologie du NAT traditionnel

**Schéma pédagogique — Les termes inside local/global désignent l'adresse interne avant et après traduction.**

~~~text
Hote interne avant NAT: 192.168.10.25 (inside local)
                       |
                       v
                 [NAT/PAT]
                       |
                       v
Adresse traduite: 198.51.100.10 (inside global)
                       |
                       v
                 [Internet]

La terminologie outside local/global concerne l'adresse externe dans le contexte de traduction.
~~~


Le vocabulaire NAT décrit une adresse par rapport au réseau interne et au réseau externe. Les termes ci-dessous se rencontrent dans la documentation Cisco et dans les références historiques sur le NAT traditionnel.

**Inside local** : adresse réelle d'un hôte interne telle qu'elle est utilisée dans le réseau local, avant sa traduction vers l'extérieur. Exemple : 192.168.10.11.

**Inside global** : adresse par laquelle cet hôte interne est représenté sur le réseau externe après traduction. Exemple : 198.51.100.25 si le PAT partage une adresse publique ; pour plusieurs formes de NAT, il peut s'agir d'une adresse publique dédiée.

**Outside global** : adresse réelle de la destination externe telle qu'elle est représentée sur le réseau public. Exemple documentaire : 203.0.113.80.

**Outside local** : adresse par laquelle la destination externe est représentée au regard du réseau interne. Elle peut être identique à l'outside global, mais certaines configurations de NAT la traduisent également.

Exemple d'une session sortante simple :

~~~text
Hôte interne : 192.168.10.11:51001
       inside local
             |
             v
      Routeur NAT
             |
             v
Adresse traduite : 198.51.100.25:62010
       inside global
             |
             v
Destination externe : 203.0.113.80:443
       outside global
~~~

Le port externe présenté ici est un exemple. Il peut être différent du port source local du client. Les quatre termes sont particulièrement utiles pour comprendre les journaux, les tables de traduction et les cas où les adresses externes sont elles-mêmes représentées par des adresses locales différentes.

Ces termes décrivent la perspective de la traduction ; ils ne sont pas quatre catégories de sécurité. Les mots local et global ne signifient pas, à eux seuls, qu'une adresse est fiable ou malveillante.

## 5. NAT statique

Le NAT statique associe de façon permanente une adresse interne à une adresse de traduction précise. Il est utile lorsqu'un service interne doit être représenté à l'extérieur par une adresse stable ou lorsqu'un équipement doit garder une correspondance fixe.

Exemple documentaire :

~~~text
ip nat inside source static 192.168.20.10 203.0.113.10
~~~

Dans une configuration Cisco IOS classique, cette ligne établit une traduction statique entre l'hôte interne 192.168.20.10 et l'adresse 203.0.113.10. Les adresses utilisées ici sont réservées à la documentation ; ne les configure pas sur un réseau réel sans plan d'adressage valide.

Les interfaces doivent également être identifiées comme inside ou outside, et les routes doivent permettre aux paquets d'atteindre la destination. La traduction ne garantit pas que tous les ports de l'hôte interne doivent être publiés. Un filtrage explicite et adapté au produit doit limiter les services accessibles.

Le NAT statique peut faciliter le diagnostic car la correspondance reste stable. Son risque principal est de rendre un hôte représentable de façon permanente à l'extérieur, avec une exposition qui dépend du filtrage et du service lui-même. Un serveur publié doit être durci, corrigé, supervisé et placé dans une zone appropriée, souvent une DMZ.

## 6. NAT dynamique avec pool

Le NAT dynamique choisit une adresse dans un pool d'adresses de traduction en fonction des règles et de la disponibilité. Les correspondances sont créées pour les communications, puis peuvent expirer selon la plateforme et le type de trafic.

Exemple conceptuel :

~~~text
Pool de traduction : 198.51.100.40 à 198.51.100.50
Hôtes internes     : 192.168.10.0/24
Besoin              : attribuer une adresse de traduction disponible
~~~

Cette solution permet d'utiliser plusieurs adresses publiques sans attribuer une correspondance statique à chaque hôte. En revanche, un pool peut être épuisé si trop de traductions simultanées sont nécessaires ou si les entrées ne libèrent pas leurs ressources comme prévu. Il faut surveiller les statistiques, la capacité du pool et les besoins du trafic.

La sélection des hôtes internes qui peuvent être traduits est souvent définie par une ACL. Dans le modèle Cisco classique, cette ACL sert à sélectionner le trafic concerné par la traduction. Une ligne permit dans cette ACL ne signifie pas nécessairement que le pare-feu autorise tout ce trafic à traverser l'équipement. C'est une distinction essentielle entre l'ACL de sélection NAT et la politique de filtrage.

## 7. PAT ou NAT overload

**Schéma pédagogique — PAT permet à plusieurs connexions de partager une adresse traduite en distinguant les sessions.**

~~~text
192.168.10.10:51500 ---\
192.168.10.11:51501 ----+--> [PAT 198.51.100.10]
192.168.10.12:51502 ---/            |
                                    +--> 198.51.100.10:40001 vers destination A
                                    +--> 198.51.100.10:40002 vers destination B

Les correspondances reelles incluent protocole et contexte de session.
~~~


PAT permet à plusieurs hôtes internes de partager une seule adresse de traduction, en différenciant les communications par des ports ou d'autres identifiants de transport pris en charge. On l'appelle souvent NAT overload dans la syntaxe Cisco IOS.

Exemple courant pour un réseau de laboratoire :

~~~text
access-list 10 permit 192.168.10.0 0.0.0.255

interface GigabitEthernet0/0
 ip nat inside

interface GigabitEthernet0/1
 ip nat outside

ip nat inside source list 10 interface GigabitEthernet0/1 overload
~~~

L'exemple suppose que GigabitEthernet0/0 fait face au réseau interne et GigabitEthernet0/1 au fournisseur d'accès ou réseau externe. Il faut aussi configurer les adresses des interfaces et le routage. Dans IOS, la ligne d'ACL 10 sélectionne ici les sources internes à traduire ; l'overload permet de partager l'adresse portée par l'interface externe.

PAT est particulièrement pratique lorsque le fournisseur n'a attribué qu'une seule adresse IPv4 publique. Cependant, la table de traductions a une capacité et des ressources finies. Les sessions, expirations, protocoles, ports et éventuelles limites de matériel doivent être surveillés si le trafic est important.

PAT n'est pas une protection complète contre les attaques entrantes. Le routeur peut ne pas avoir de correspondance pour un nouveau flux entrant, mais les autorisations, redirections de ports, services d'administration et politiques du pare-feu déterminent l'exposition réelle. Ne déduis pas qu'un serveur est protégé uniquement parce que les utilisateurs partagent une adresse publique.

## 8. Configurer NAT : méthode de laboratoire

Avant d'entrer des commandes, décris la topologie et confirme les interfaces. Un exemple de laboratoire comprend :
- LAN interne : 192.168.10.0/24, routeur 192.168.10.1 ;
- interface externe : adresse attribuée au réseau de test ;
- route par défaut vers le routeur amont ;
- besoin : permettre aux hôtes du LAN de sortir vers un réseau externe simulé.

Sur le routeur, identifie l'interface côté LAN comme inside et l'interface côté WAN comme outside. Sélectionne les sources internes dans une ACL dédiée, puis configure l'overload si le réseau externe utilise l'adresse de l'interface WAN.

Exemple de configuration illustrative :

~~~text
access-list 10 permit 192.168.10.0 0.0.0.255
!
interface GigabitEthernet0/0
 description LAN_INTERNE
 ip address 192.168.10.1 255.255.255.0
 ip nat inside
 no shutdown
!
interface GigabitEthernet0/1
 description WAN_LAB
 ip address 198.51.100.2 255.255.255.0
 ip nat outside
 no shutdown
!
ip nat inside source list 10 interface GigabitEthernet0/1 overload
ip route 0.0.0.0 0.0.0.0 198.51.100.1
~~~

Les adresses externes de documentation ne doivent pas être utilisées comme adresses publiques réelles sur Internet. Le routeur amont de laboratoire doit être configuré en conséquence. Les commandes et noms d'interface dépendent du simulateur ou du modèle.

Le NAT ne corrige pas une mauvaise passerelle côté client. Un hôte interne doit avoir une adresse et un masque cohérents, une passerelle orientée vers le routeur NAT et, pour la navigation par nom, un DNS fonctionnel. Le routeur doit avoir une route de retour ou une route par défaut valide. Vérifie chaque composant séparément.

## 9. L'ACL de NAT n'est pas un pare-feu

Dans l'exemple PAT, l'ACL 10 sélectionne les adresses internes qui seront concernées par la traduction. Elle ne dit pas automatiquement que tous les flux de ces hôtes sont autorisés par une politique de sécurité. Le comportement de filtrage dépend de la configuration de l'équipement et de ses autres règles.

~~~text
access-list 10 permit 192.168.10.0 0.0.0.255
ip nat inside source list 10 interface GigabitEthernet0/1 overload
~~~

Cette configuration indique au mécanisme NAT quelles sources traduire. Elle ne constitue pas une politique complète pour décider quels services doivent être autorisés vers Internet, quelles destinations doivent être bloquées ou quels flux entrants sont permis.

En environnement d'entreprise, documente les rôles des ACL : sélection de NAT, filtrage d'interface, contrôle d'administration ou autre. Des ACL différentes peuvent être utilisées pour des objectifs différents. Évite de réutiliser un même objet sans comprendre les interactions qui en résultent.

Pour un diagnostic, demande-toi où se produit le refus : l'ACL NAT peut ne pas faire correspondre la source, une ACL de filtrage peut bloquer le paquet, une route peut manquer, le serveur distant peut ne pas répondre, ou une politique de sortie peut limiter le trafic. La solution dépend de la couche réellement en cause.

## 10. Publication de service et redirection de port

**Schéma pédagogique — La publication redirige un service entrant vers une cible ; elle ne doit pas ouvrir plus que nécessaire.**

~~~text
Internet client
      |
      v TCP/443 vers 198.51.100.20
[NAT / pare-feu perimetrique]
      |
      v translation destination + politique HTTPS
[DMZ: serveur Web 10.30.0.20:443]
      |
      X pas d'acces general au LAN interne

La traduction et la décision de filtrage sont distinctes.
~~~


Une redirection de port traduit une combinaison d'adresse et de port externe vers une adresse et un port internes. Elle permet de rendre un service particulier atteignable depuis l'extérieur, sous réserve du routage et du filtrage.

Exemple Cisco IOS statique PAT pour publier un serveur Web fictif :

~~~text
ip nat inside source static tcp 192.168.20.10 443 203.0.113.10 443
~~~

Cette syntaxe est représentative de Cisco IOS, mais la prise en charge et le modèle exact varient. Dans cet exemple, TCP/443 sur l'adresse traduite 203.0.113.10 pointe vers TCP/443 de l'hôte 192.168.20.10. Les interfaces inside/outside et les routes doivent être configurées séparément, et une règle de filtrage peut être nécessaire selon le produit.

N'expose pas tous les ports d'un serveur parce qu'un seul service doit être publié. Définis le service, les sources autorisées si elles peuvent être limitées, l'adresse et le port interne, le propriétaire de l'application, les besoins d'authentification, le niveau de journalisation et le plan de retrait. Un serveur exposé doit être régulièrement mis à jour et idéalement placé dans une DMZ plutôt que dans le même segment que des postes de travail.

Avant de créer une redirection, vérifie si le fournisseur donne réellement une adresse IPv4 publique. Certains accès résidentiels utilisent CGNAT ; dans ce cas, l'adresse WAN du routeur peut être privée ou appartenir à une plage partagée et la redirection locale n'est pas suffisante pour rendre le service accessible depuis Internet. Il faut alors un service ou une architecture pris en charge par le fournisseur ou l'organisation, plutôt que tenter de contourner ses contrôles.

## 11. PAT statique et plusieurs services

Une adresse publique peut parfois publier plusieurs services internes en utilisant des ports externes différents, à condition que le dispositif et le besoin le permettent. Par exemple, une adresse externe peut diriger le port HTTPS public vers un serveur Web et un autre port vers un service spécifique. Mais un port non standard n'est pas une protection robuste à lui seul.

Lorsque plusieurs serveurs se partagent une adresse publique, il faut éviter les chevauchements de port et documenter la destination exacte de chaque règle. Deux redirections qui utilisent le même protocole, la même adresse externe et le même port externe ne peuvent généralement pas désigner simultanément deux serveurs différents, sauf mécanisme applicatif ou architecture distincte.

Les services d'administration ne devraient pas être publiés à Internet par simple commodité. Privilégie un VPN ou un bastion administré, l'authentification forte et des sources restreintes. Si une publication directe est nécessaire, documente le risque, limite l'accès autant que possible, surveille les connexions et prépare le retrait.

## 12. NAT, pare-feu stateful et zones de sécurité

Un pare-feu stateful suit les sessions et peut reconnaître le trafic de retour d'une communication initiée et autorisée depuis l'intérieur. NAT peut créer une correspondance pour cette session, mais la traduction et le suivi d'état ne sont pas la même fonction. Certains dispositifs les intègrent dans une même appliance ; les responsabilités logiques demeurent distinctes.

Une architecture de périmètre typique sépare les zones LAN, serveurs, DMZ, invités et administration. Les règles déterminent les communications permises entre ces zones. Le NAT est configuré sur les points de traduction nécessaires. Une redirection d'un service public vers la DMZ n'autorise pas automatiquement le serveur de DMZ à communiquer librement vers les réseaux internes.

Il faut également contrôler les flux sortants. Un poste compromis peut tenter d'envoyer des données vers des destinations externes, même si aucune connexion entrante n'est autorisée. L'egress filtering peut limiter certains flux à des résolveurs DNS, services de mise à jour, proxys ou API approuvés, mais il exige un inventaire des dépendances et des tests de compatibilité.

La configuration doit être pensée en termes de flux : source, destination avant et après traduction, protocole, port, direction, zone de sécurité et action. Cela permet de comprendre si le problème relève du NAT, du routage, d'une ACL ou d'un état de session.

## 13. VPN et exemptions de NAT

**Schéma pédagogique — Le trafic destiné au réseau distant doit souvent préserver ses adresses internes pour correspondre aux politiques du tunnel.**

~~~text
LAN 192.168.10.0/24
         |
         +---- destination 10.20.0.0/16 ----> exemption NAT --> VPN
         |
         +---- destination Internet ---------> PAT ----------> WAN

L'ordre des règles et les conditions d'exemption dépendent de la plateforme.
~~~


Un VPN site-à-site peut relier deux réseaux privés. Selon la configuration, le trafic entre les sous-réseaux distants ne doit pas être traduit, afin que les adresses attendues par les politiques IPsec, les routes ou les applications restent cohérentes. Certaines plateformes exigent une règle d'exemption ou une politique de NAT spéciale ; l'ordre exact dépend du produit.

Exemple conceptuel : le réseau 192.168.10.0/24 doit joindre le réseau distant 10.20.0.0/16 via un tunnel. Si le routeur traduit la source interne vers son adresse WAN au lieu de préserver l'adresse prévue, la politique du tunnel peut ne pas reconnaître le trafic. Le résultat possible est un tunnel qui semble actif mais ne transporte pas les applications attendues.

Une exemption NAT n'est pas la même chose qu'une autorisation pare-feu. Elle décrit le trafic qui ne doit pas subir la traduction normale. Il reste nécessaire de contrôler les sources, destinations et ports autorisés dans le VPN. Les réseaux et utilisateurs distants ne doivent pas obtenir plus de droits simplement parce que le tunnel est établi.

Lors du dépannage, compare les sélecteurs ou sous-réseaux du VPN, les routes, la règle d'exemption, l'ordre des règles NAT et les ACL de filtrage. Vérifie le trafic dans les deux sens. N'applique pas une règle no NAT générale sans confirmer l'étendue souhaitée, car elle peut affecter la connectivité Internet d'autres flux.

## 14. NAT à double étage et CGNAT

Le double NAT survient lorsque deux équipements traduisent successivement un flux, par exemple le routeur du fournisseur et un routeur personnel placé derrière lui. Il peut fonctionner pour la navigation sortante, mais compliquer les publications de services, les VPN, le diagnostic, certains jeux et les protocoles qui dépendent d'une connectivité entrante.

Pour diagnostiquer un double NAT, compare l'adresse WAN du routeur personnel à l'adresse publique observée par un service fiable et examine l'architecture du fournisseur. Si l'adresse WAN appartient à une plage privée RFC1918 ou à la plage partagée de CGNAT 100.64.0.0/10, l'équipement peut être derrière un autre niveau de traduction. Une adresse peut aussi être fournie via une architecture opérateur spécifique : il faut vérifier les informations de l'ISP.

CGNAT (Carrier-Grade NAT) permet à un fournisseur de partager un ensemble d'adresses IPv4 publiques entre plusieurs abonnés. Il réduit le besoin d'adresses publiques, mais peut empêcher l'abonné de publier un service directement sans assistance du fournisseur. Une redirection définie uniquement sur le routeur domestique n'a alors pas le contrôle de la traduction amont.

Les options correctes peuvent être demander une adresse publique, utiliser une méthode d'accès distant administrée, publier le service via une passerelle contrôlée ou utiliser une architecture de tunnel adaptée. Ne suppose pas que la désactivation du pare-feu du routeur résout un CGNAT : ce n'est pas la même couche du problème.

## 15. NAT et IPv6

IPv6 dispose d'un espace d'adressage beaucoup plus grand et n'exige pas généralement un partage d'adresses analogue au PAT IPv4 pour permettre à des appareils de disposer d'adresses globales. Cela ne signifie pas que tous les hôtes doivent être accessibles librement depuis Internet : le pare-feu IPv6, le routage et la politique de sécurité restent nécessaires.

Il existe des mécanismes de traduction en IPv6 dans certains cas, mais il ne faut pas traiter le NAT IPv4 comme un modèle de sécurité universel pour toutes les architectures. Le passage à IPv6 demande d'inventorier les adresses, routes, services exposés, règles et dispositifs de filtrage. Une politique IPv4 restrictive ne garantit pas une politique IPv6 équivalente.

N'utilise pas la présence d'une adresse globale IPv6 comme preuve que le service est exposé, ni l'absence de NAT comme preuve que le réseau est dangereux. La question pertinente est : quels flux sont routables, quelle politique est appliquée et quel service écoute sur quelle interface ?

## 16. Vérifier NAT sous Cisco IOS

Dans un laboratoire IOS ou IOS XE, les commandes suivantes aident à examiner la traduction :

~~~text
show ip nat translations
show ip nat statistics
show running-config | include ip nat
show running-config interface GigabitEthernet0/0
show running-config interface GigabitEthernet0/1
show access-lists
show ip route
~~~

show ip nat translations affiche les correspondances présentes et peut permettre de comparer les adresses locales et globales. show ip nat statistics présente les statistiques NAT et les interfaces définies comme inside/outside, selon la version. Les commandes de configuration permettent de vérifier les règles NAT et les interfaces. show ip route permet d'examiner le routage.

Une table vide peut simplement indiquer qu'aucun flux correspondant n'a été tenté depuis le début, que les entrées ont expiré, ou que l'ACL de sélection ne correspond pas. Reproduis une tentative contrôlée depuis un hôte connu puis examine la table. Vérifie aussi les compteurs, les interfaces et la route de retour.

Évite d'effacer les traductions actives sur un routeur de production : la commande de suppression peut interrompre des sessions. Une commande comme clear ip nat translation *, lorsqu'elle existe et est appropriée, est destructive et doit être réservée à un laboratoire ou à une procédure approuvée avec un impact connu. La consultation de la table est une première étape plus sûre.

## 17. Méthode de dépannage : NAT ne fonctionne pas

**Schéma pédagogique — Suivre le paquet de bout en bout permet de distinguer traduction, filtrage et routage.**

~~~text
[Paquet source/destination initial]
           |
           v
     [Route entrante]
           |
           v
     [Regle NAT ?] ---> [Table des translations]
           |
           v
     [Politique pare-feu]
           |
           v
     [Route de sortie] ---> [Serveur / Internet]
                               |
                               v
                      [Route de retour ?]

Relever les adresses avant/apres traduction et les compteurs.
~~~


Un diagnostic efficace suit une progression du client vers la sortie du réseau :
1. Vérifie l'adresse interne, le masque, la passerelle et le DNS du client.
2. Vérifie que le client peut atteindre la passerelle et que la route vers la destination existe.
3. Confirme que l'interface interne est marquée ip nat inside.
4. Confirme que l'interface externe est marquée ip nat outside.
5. Vérifie que l'ACL de sélection NAT couvre la source réelle avec le bon wildcard.
6. Confirme que la règle NAT correspond au type de traduction attendu.
7. Génère un flux de test, puis consulte les traductions et statistiques.
8. Examine l'ACL de filtrage, la route de retour et la réponse du serveur externe.
9. Vérifie les politiques du fournisseur, un éventuel double NAT ou CGNAT.
10. Consigne le résultat et teste les autres flux pour s'assurer que la correction reste limitée.

Le succès du ping vers la passerelle ne prouve pas que NAT, la route de sortie et le service distant fonctionnent. Le ping vers Internet peut être bloqué ou ignoré par la destination. Utilise un test qui correspond au protocole applicatif et compare les points de passage.

### Interpréter les symptômes

**Aucune traduction ne s'ajoute :** vérifie les interfaces inside/outside, le match de l'ACL, les routes et si le trafic traverse vraiment le routeur NAT.

**La traduction existe, mais le service échoue :** le problème peut se situer après NAT, dans le filtrage, la route de retour, un proxy, le serveur distant, DNS ou TLS.

**La sortie Internet fonctionne, mais la publication entrante échoue :** examine la redirection, l'adresse WAN publique, le filtrage entrant, la route du serveur, le port à l'écoute et le double NAT.

**Un seul sous-réseau n'accède pas :** vérifie l'ACL de sélection, le wildcard, le masque, la route et les règles inter-VLAN.

**Le problème apparaît à charge élevée :** examine la capacité, le nombre de translations actives, les expirations et les limites de ressources du routeur.

## 18. Sécurité du périmètre : contrôle des publications

Chaque publication entrante doit avoir un propriétaire et un objectif. Il faut préciser le nom du service, l'hôte interne, l'adresse et le port externes, les sources autorisées lorsque c'est possible, les contrôles d'authentification, les journaux, les exigences de correctifs et le plan de retrait.

Ne publie pas les interfaces de gestion de routeurs, commutateurs, hyperviseurs ou bases de données par défaut. Préfère une voie d'administration contrôlée, comme un VPN avec authentification forte ou un bastion. Si une publication directe est nécessaire, restreins le service, applique les mises à jour, contrôle les accès et surveille les tentatives.

Place les services publics dans une DMZ lorsque l'architecture le permet. Depuis la DMZ, seuls les flux indispensables vers les applications internes doivent être permis. Une redirection de port vers un serveur qui se trouve dans le VLAN des postes peut exposer davantage de ressources que prévu si une compromission survient.

Revois régulièrement les redirections. Un test de migration peut laisser un port ouvert après la fin du besoin. Les règles sans propriétaire, sans justification ou sans date de revue doivent être investiguées et retirées après validation.

## 19. Documentation et gestion des changements

Avant d'installer NAT ou de modifier une règle, conserve la configuration actuelle et documente les interfaces, les routes, les ACL et les traductions existantes. Détermine les services affectés, la fenêtre de changement, les personnes concernées et le plan de retour arrière.

Après le changement, vérifie non seulement que le flux souhaité fonctionne, mais aussi que les flux non souhaités restent impossibles. Consulte les tables de traduction, les compteurs et les journaux. Un test qui prouve seulement l'accès Internet ne suffit pas à confirmer la sécurité d'une publication.

Les changements de routeur peuvent impacter les sessions existantes, les VPN et les applications. La sauvegarde doit être restaurable et accessible même si la voie réseau est indisponible. Utilise un canal de gestion distinct lorsque c'est possible et ne supprime pas les entrées actives sur un routeur de production sans procédure approuvée.

## 20. Erreurs fréquentes à éviter

- Confondre la sélection de traduction NAT et l'autorisation de filtrage.
- Oublier de marquer les interfaces inside et outside.
- Utiliser le mauvais wildcard dans l'ACL qui sélectionne les sources.
- Croire qu'une route par défaut suffit sans route de retour.
- Supposer qu'une adresse WAN est publique alors qu'elle se trouve derrière CGNAT ou un autre routeur.
- Publier un port de gestion sans besoin et sans restriction.
- Oublier la politique du pare-feu après une redirection.
- Utiliser un NAT comme seule mesure de sécurité.
- Faire une exemption NAT trop générale qui perturbe d'autres destinations.
- Oublier que les services à l'écoute, les routes et la traduction sont des problèmes distincts.
- Effacer les traductions pendant les heures de service pour essayer de forcer une nouvelle entrée.
- Considérer une table de traductions vide comme preuve que le NAT est mal configuré.
- Ignorer IPv6 parce que le NAT IPv4 fonctionne.
- Oublier les règles et dépendances lors d'une migration du routeur.
- Laisser une publication temporaire active après la fin du besoin.

## 21. TP 1 — PAT sortant pour un LAN

Un LAN de laboratoire utilise 192.168.10.0/24. R1 a 192.168.10.1/24 côté LAN et 198.51.100.2/24 côté WAN de test. Le routeur amont de laboratoire a l'adresse 198.51.100.1. Le besoin est de permettre aux clients du LAN de communiquer avec un service externe simulé.

Étapes :
1. Confirme les adresses et le nom exact des interfaces.
2. Configure l'adresse interne et marque l'interface avec ip nat inside.
3. Configure l'adresse externe et marque l'interface avec ip nat outside.
4. Ajoute une ACL qui sélectionne uniquement 192.168.10.0/24.
5. Configure NAT overload sur l'adresse de l'interface externe.
6. Ajoute et vérifie la route par défaut.
7. Depuis un client, génère une connexion de test vers une destination atteignable.
8. Consulte show ip nat translations et show ip nat statistics.
9. Vérifie que l'adresse source est traduite dans le flux sortant.
10. Teste une source qui n'est pas dans le réseau sélectionné et confirme le comportement prévu.

Correction de laboratoire :

~~~text
access-list 10 permit 192.168.10.0 0.0.0.255
!
interface GigabitEthernet0/0
 description LAN_INTERNE
 ip address 192.168.10.1 255.255.255.0
 ip nat inside
 no shutdown
!
interface GigabitEthernet0/1
 description WAN_LAB
 ip address 198.51.100.2 255.255.255.0
 ip nat outside
 no shutdown
!
ip nat inside source list 10 interface GigabitEthernet0/1 overload
ip route 0.0.0.0 0.0.0.0 198.51.100.1
~~~

La configuration est un modèle à adapter au laboratoire. Les adresses documentaires ne sont pas utilisables comme adresses publiques réelles. Les clients doivent avoir une passerelle et un DNS adaptés. Le routeur amont de test doit également disposer d'un retour correct.

L'ACL 10 sert à sélectionner les sources internes à traduire. Elle n'est pas, par elle-même, une règle de pare-feu qui autorise tous les paquets de ces sources. Pour la validation, compare les adresses internes aux valeurs présentes dans la table de traductions et vérifie qu'une connexion de test utilise l'adresse externe attendue.

## 22. TP 2 — Publier uniquement HTTPS vers une DMZ

Le routeur dispose d'une adresse publique réservée au laboratoire et le serveur Web de DMZ utilise 192.168.50.10. Le besoin est de publier TCP/443 et de ne pas exposer SSH ni les autres ports.

Dessine le chemin du paquet de l'extérieur vers le serveur. Identifie l'adresse et le port externes, puis la cible interne. Vérifie la route vers la DMZ, les interfaces NAT, la politique de filtrage et le service à l'écoute sur l'hôte. Indique comment tu testerais un flux autorisé et un flux non autorisé.

Correction raisonnée : une forme de PAT statique peut exprimer une traduction TCP/443 publique vers TCP/443 du serveur, selon les capacités du routeur. La configuration exacte dépend de l'adresse attribuée à l'interface ou à l'objet externe et de la syntaxe du système. Il faut en plus vérifier le filtrage pour que seuls les services voulus soient acceptés.

Ne crée pas de traduction pour TCP/22 si SSH n'a pas à être publié. Ne suppose pas que la seule traduction bloque le reste : examine les règles de sécurité de l'équipement et les politiques sur le serveur. Teste depuis une source externe autorisée et vérifie depuis les journaux que la demande atteint la destination attendue.

Le serveur doit être corrigé, supervisé et isolé des ressources internes. Si l'application Web nécessite une base de données, n'autorise que le flux de la source applicative vers la base et le port requis. Les visiteurs ne doivent pas joindre directement la base.

## 23. TP 3 — NAT et VPN

Deux sites ont les réseaux 192.168.10.0/24 et 10.20.0.0/16. Le VPN est destiné à rendre ces réseaux joignables l'un depuis l'autre. Le trafic entre les sous-réseaux doit être traité selon les sélecteurs du tunnel et les règles de sécurité ; il ne doit pas être traduit par la règle Internet générale si l'architecture attend les adresses d'origine.

Diagnostic guidé :
- Confirme que les routes vers le réseau distant existent.
- Vérifie les sous-réseaux négociés par le tunnel et les adresses attendues aux deux extrémités.
- Examine l'ACL de sélection de NAT et les éventuelles exemptions.
- Vérifie l'ordre de la politique NAT et les règles de filtrage.
- Génère un test entre une source et une destination connues.
- Consulte les compteurs et journaux des deux côtés.
- Vérifie le chemin retour et les politiques de chaque site.

Une exemption NAT n'accorde pas un accès à tous les hôtes distants. Elle empêche la traduction pour le flux spécifié. Il faut toujours garder des règles de filtrage et une segmentation appropriée.

## 24. Exercices corrigés

### Exercice 1 — Pourquoi utiliser PAT ?

Plusieurs postes disposent d'adresses privées et partagent une adresse IPv4 externe pour naviguer.

**Correction :** PAT différencie les sessions à l'aide d'informations de transport et associe les réponses à la source interne correspondante. Cela permet à plusieurs appareils de partager une adresse traduite, sous réserve des limites du routeur.

### Exercice 2 — NAT et pare-feu

Une ACL utilisée par la règle NAT contient permit 192.168.10.0 0.0.0.255. Cela signifie-t-il que tous les flux de cette plage sont autorisés par le pare-feu ?

**Correction :** non. Dans ce contexte, l'ACL sélectionne les sources qui peuvent être traduites. L'autorisation de filtrage doit être analysée séparément selon la plateforme et la configuration.

### Exercice 3 — Table NAT vide

Quelle série de vérifications est raisonnable ?

**Correction :** confirmer que le client envoie du trafic, que les interfaces sont correctement marquées inside/outside, que l'ACL correspond à la source, que la règle NAT est présente et que le paquet traverse le routeur. Ensuite, générer un test contrôlé et examiner les statistiques. Une table vide seule ne permet pas d'identifier la cause.

### Exercice 4 — La navigation sortante fonctionne, mais le serveur n'est pas accessible depuis Internet

**Correction :** vérifier si la WAN possède une adresse publique, si une redirection existe, si le filtrage permet le flux, si le service écoute, si la route de retour est correcte et si un double NAT ou CGNAT est présent. Le PAT sortant ne crée pas automatiquement une redirection entrante.

### Exercice 5 — Pourquoi publier les services dans une DMZ ?

**Correction :** une DMZ permet d'isoler les services exposés des réseaux internes et d'appliquer des règles spécifiques. Elle ne rend pas le serveur invulnérable ; elle réduit les chemins possibles vers les autres zones si la segmentation est correcte.

### Exercice 6 — Le réseau interne n'atteint pas le réseau distant via VPN

**Correction :** vérifier routes, sélecteurs de tunnel, ACL, exemption NAT, ordre des règles et route de retour. Une règle Internet générale peut traduire un flux qui doit préserver les adresses d'origine, selon l'architecture.

### Exercice 7 — Double NAT

Un routeur personnel est branché derrière la box du fournisseur. Le service publié ne répond pas depuis Internet.

**Correction :** vérifier l'adresse WAN du routeur personnel, la box amont et l'éventuel CGNAT. Une redirection peut devoir être créée au niveau amont ou remplacée par une architecture validée par l'opérateur. Désactiver le pare-feu local ne résout pas un problème de traduction amont.

### Exercice 8 — NAT statique

Pourquoi une traduction statique ne signifie-t-elle pas que tous les ports doivent être ouverts ?

**Correction :** l'association d'adresses rend la correspondance stable mais la politique de filtrage et les services à l'écoute déterminent l'accessibilité. Publie uniquement les ports nécessaires et durcis le serveur.

### Exercice 9 — NAT et IPv6

Le NAT IPv4 fonctionne. Peut-on conclure que le réseau est protégé en IPv6 ?

**Correction :** non. IPv6 doit avoir ses routes, services exposés et règles de filtrage vérifiés séparément. La sécurité vient de la politique, pas de la présence d'un NAT IPv4.

### Exercice 10 — Risque d'effacer la table NAT

Pourquoi faut-il éviter de vider les traductions actives sur un routeur de production ?

**Correction :** la suppression peut interrompre des sessions légitimes et provoquer une panne. Commence par lire la table et les statistiques ; toute suppression doit être faite en laboratoire ou selon une procédure approuvée avec impact connu.

## 25. Défi final — concevoir un périmètre cohérent

Une petite entreprise possède un réseau utilisateurs 192.168.10.0/24, un réseau serveurs 192.168.20.0/24, une DMZ 192.168.50.0/24, un réseau d'administration 192.168.40.0/24 et une seule adresse IPv4 externe dans le laboratoire. Les utilisateurs doivent accéder à Internet. Le serveur Web 192.168.50.10 doit être accessible en HTTPS de l'extérieur. Les interfaces d'administration restent limitées au réseau de gestion. Les serveurs de DMZ ne doivent pas accéder librement aux systèmes internes. Un VPN relie un second site et doit préserver les adresses de ses sous-réseaux privés.

**Correction complète :**

1. **Préparer le schéma et les routes.** Établis les interfaces inside/outside, la passerelle externe, les routes vers les zones et les routes retour. Vérifie que le plan d'adressage est sans chevauchement et que l'adresse externe est réellement disponible pour le laboratoire. Si l'accès est derrière CGNAT, adapte le scénario avec une solution autorisée.
2. **Configurer le PAT sortant.** Sélectionne uniquement le sous-réseau utilisateurs qui doit sortir et utilise overload sur l'adresse externe, après avoir marqué les interfaces et configuré la route par défaut. Si d'autres zones ont besoin d'Internet, décide explicitement si elles sont incluses au lieu d'ajouter tous les réseaux automatiquement.
3. **Publier uniquement HTTPS.** Configure une redirection TCP/443 vers 192.168.50.10 et vérifie le filtrage entrant correspondant. Ne publie pas SSH, les interfaces d'administration ou les ports de la base de données. Teste que le site répond et que les autres ports ne sont pas accessibles depuis les sources non autorisées.
4. **Protéger la DMZ.** Autorise seulement le serveur Web vers les services internes indispensables, si l'application en a réellement besoin. Applique les règles sur le point de passage qui voit le trafic et vérifie les flux dans les deux sens. Les utilisateurs et les invités n'ont pas à accéder directement aux services de gestion de la DMZ.
5. **Protéger l'administration.** Restreins SSH et les interfaces de gestion au réseau d'administration ou à un bastion. Complète les ACL avec des comptes robustes, une authentification forte, des mises à jour et une journalisation. N'ouvre pas la gestion sur l'adresse externe par facilité.
6. **Préserver le trafic VPN.** Confirme les routes, les sélecteurs de tunnel et les sous-réseaux autorisés. Exempte du NAT Internet le trafic qui doit garder ses adresses internes, selon la plateforme, mais garde le filtrage entre les réseaux du tunnel. Le fait qu'un VPN soit actif ne doit pas donner automatiquement accès à tous les systèmes.
7. **Valider les flux.** Teste la navigation depuis un utilisateur, l'accès HTTPS externe vers la DMZ, le refus de SSH depuis une source publique, le refus d'accès direct des invités aux réseaux internes et la communication attendue à travers le VPN. Vérifie la table NAT, les statistiques, les routes et les journaux pour localiser les décisions.
8. **Documenter et préparer la récupération.** Sauvegarde la configuration, vérifie qu'une console ou un accès de secours existe, note la justification et le propriétaire de chaque traduction et redirection, puis fixe une date de revue. Retire les règles de test à la fin du laboratoire.

Le défi est réussi quand chaque flux nécessaire fonctionne, les flux qui doivent être refusés le sont réellement, les traductions sont compréhensibles, le VPN préserve le plan d'adressage attendu et une personne autre que l'auteur peut relire la politique.

## 26. Glossaire

**NAT :** traduction d'adresses IP.

**PAT / NAPT :** mécanisme qui traduit aussi les identifiants de transport afin de faire partager une adresse de traduction à plusieurs sessions.

**NAT statique :** association fixe entre une adresse interne et une adresse de traduction.

**NAT dynamique :** attribution d'une adresse dans un pool à la demande.

**Overload :** fonctionnalité Cisco courante pour le PAT qui partage l'adresse d'une interface ou d'un pool.

**Inside local :** adresse de l'hôte interne telle qu'elle est utilisée à l'intérieur.

**Inside global :** adresse par laquelle l'hôte interne est représenté sur le réseau externe.

**Outside global :** adresse de la destination externe telle qu'elle est utilisée dans l'espace externe.

**Outside local :** adresse sous laquelle la destination externe est représentée depuis l'espace interne.

**Redirection de port :** traduction d'un port externe vers un hôte et un port internes.

**CGNAT :** traduction opérateur qui partage des adresses IPv4 entre plusieurs abonnés.

**Double NAT :** situation où plusieurs dispositifs traduisent successivement les flux.

**Exemption NAT :** règle empêchant certains flux, par exemple ceux du VPN, de subir la traduction normale.

**DMZ :** zone intermédiaire pour les services exposés, séparée des réseaux internes.

**Table de traductions :** état conservé par le dispositif pour associer les adresses et ports avant et après traduction.

**Périmètre de sécurité :** limite logique où sont appliqués les contrôles entre zones ou réseaux de confiance différente.

## 27. Références

- Cisco, guide de configuration NAT, exemples de NAT statique, dynamique et overload : https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/13772-12.html
- Cisco IOS XE, guide de configuration NAT : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr3-fwd/nat/nat-configuration-guide/nat.html
- RFC 3022, Traditional IP Network Address Translator : https://www.rfc-editor.org/rfc/rfc3022
- Cisco, NAT et conservation d'adresses : https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr_nat/configuration/15-2mt/iadnat-addr-consv.html

La syntaxe et les capacités NAT varient selon les versions et les gammes. Consulte la documentation correspondant à l'équipement réel, utilise les adresses d'exemple uniquement dans un laboratoire et teste la politique de filtrage indépendamment de la traduction.

Fin du cours.

## 28. Cas pratiques complémentaires de dépannage

Les situations suivantes approfondissent la méthode de diagnostic et les risques du périmètre. Elles ne sont pas des recettes à appliquer aveuglément : chaque correction doit correspondre à l'architecture et à la politique réelle.

### Cas de dépannage 1 — La table de traductions reste vide

**Analyse.** Aucune session n'a peut-être été générée, la source ne correspond pas à l'ACL NAT, les interfaces inside/outside sont mal identifiées ou le trafic contourne ce routeur. Vérifie l'adressage du client, sa passerelle, les interfaces marquées et l'ACL de sélection. Génère un flux de test puis consulte show ip nat translations et show ip nat statistics. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne conclus pas à une panne NAT sur la seule observation d'une table vide. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 2 — La navigation sortante fonctionne, pas la publication entrante

**Analyse.** Le PAT sortant ne crée pas automatiquement une redirection de port. Le service peut aussi être derrière CGNAT ou bloqué par le filtrage entrant. Confirme l'adresse WAN publique, la redirection exacte, l'écoute du service, les règles de sécurité et le chemin de retour. Vérifie s'il existe un routeur amont. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne désactive pas le pare-feu pour compenser l'absence d'une traduction ou d'une adresse publique. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 3 — Une redirection HTTPS cible le mauvais serveur

**Analyse.** L'adresse interne peut avoir changé, la règle peut pointer vers une IP d'un autre VLAN ou le serveur peut avoir plusieurs interfaces. Vérifie l'IP réelle du serveur, le port en écoute, le mappage externe-interne et les routes. Teste le service depuis le réseau local avant de le tester depuis l'extérieur. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne publie pas un service tant que la destination interne n'est pas identifiée. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 4 — L'ACL de sélection NAT autorise une plage trop large

**Analyse.** Le wildcard ou les lignes de sélection peuvent inclure des réseaux qui ne devraient pas être traduits. Calcule le wildcard, compare les préfixes au plan d'adressage et limite la sélection aux sources qui ont besoin de traduction. Vérifie les compteurs après changement. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne réutilise pas une ACL de NAT comme autorisation générale de sécurité. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 5 — Une ACL permit est présente, mais le trafic reste bloqué

**Analyse.** L'ACL sélectionne peut-être la traduction sans autoriser le paquet dans le pare-feu. Une route, le service ou une autre politique peut également manquer. Examine séparément la correspondance NAT, les règles de filtrage, la route et le service distant. Vérifie quel équipement a effectivement refusé la communication. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne confonds pas une correspondance de NAT avec une décision d'autorisation complète. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 6 — Le tunnel VPN est actif mais les applications échouent

**Analyse.** Le trafic à destination du réseau distant peut être traduit par la règle Internet au lieu de préserver ses adresses attendues. Vérifie les routes, sélecteurs du tunnel, exemption NAT, ordre des règles et politiques de filtrage sur les deux sites. Teste une paire source-destination précise. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne crée pas une exemption pour tous les flux sans analyser les réseaux concernés. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 7 — Les connexions sortantes échouent seulement pour un VLAN

**Analyse.** L'ACL NAT peut ne sélectionner que le réseau utilisateurs, ou le VLAN peut avoir une route ou une passerelle différente. Compare l'adresse source et le VLAN à la liste de sélection, vérifie l'interface de routage et les règles de sécurité. Ajoute le sous-réseau seulement si le besoin est validé. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne change pas le masque d'une règle existante sans connaître tous les réseaux qu'il couvre. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 8 — Le routeur est derrière une box et le service reste inaccessible

**Analyse.** Un double NAT nécessite parfois une traduction correspondante sur la box amont. Si la box est elle-même derrière CGNAT, l'abonné ne contrôle pas la dernière traduction. Compare l'adresse WAN du routeur personnel à la topologie de l'opérateur et vérifie toutes les couches de traduction. Choisis une solution autorisée par le fournisseur ou une passerelle approuvée. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Désactiver le filtrage local ne corrige pas une traduction amont absente. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 9 — Les connexions échouent après effacement de traductions

**Analyse.** La suppression peut avoir interrompu des sessions actives dont les entrées étaient nécessaires à la traduction des réponses. Examine les sessions et journaux, puis laisse les clients établir de nouvelles connexions ou applique la procédure de récupération approuvée si les symptômes persistent. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** N'efface pas la table NAT complète sur un routeur de production en tant que premier réflexe. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 10 — Le PAT manque de ressources à forte charge

**Analyse.** Le nombre de sessions ou de ports disponibles peut approcher les limites du matériel ou de la configuration. Examine statistiques, nombre de traductions, expirations, CPU, mémoire et modèles de trafic. Identifie les clients ou services créant un volume anormal et vérifie la capacité documentée. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** N'augmente pas les délais ou la taille de la table sans comprendre les limites et le risque. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 11 — Les clients peuvent joindre Internet par IP mais pas par nom

**Analyse.** La traduction et le routage peuvent fonctionner alors que DNS est bloqué ou mal configuré. Vérifie le résolveur client, sa route, les règles vers UDP/53 et TCP/53 selon le besoin, puis teste la résolution séparément de l'accès Web. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** N'autorise pas tous les ports sortants pour corriger DNS. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 12 — Le serveur publié fonctionne localement mais pas depuis Internet

**Analyse.** La redirection peut être absente, la route de retour incorrecte, le filtrage amont restrictif ou l'adresse WAN non publique. Teste d'abord le service depuis le LAN, puis vérifie la traduction, le filtrage, la route, l'adresse WAN et les journaux externes. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne confonds pas accessibilité locale et publication Internet réussie. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 13 — Une redirection expose SSH inutilement

**Analyse.** Une règle de PAT statique publie peut-être un port d'administration sans besoin opérationnel. Retire la redirection si elle n'est pas nécessaire. Préfère un VPN ou un bastion, limite les sources et vérifie les journaux et les comptes. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Changer SSH vers un autre port n'est pas une protection suffisante à lui seul. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 14 — Deux services veulent le même port public

**Analyse.** Une seule combinaison adresse-protocole-port ne peut généralement pas être redirigée simultanément vers deux hôtes de la même manière. Clarifie le besoin, utilise des adresses publiques distinctes, un proxy applicatif ou des ports externes différents si c'est compatible avec la politique. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne crée pas deux redirections qui se chevauchent en espérant que l'équipement devinera la destination. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 15 — Le trafic externe arrive sur une adresse, mais le serveur ne reçoit rien

**Analyse.** La traduction peut être correcte alors que le filtrage ou la route interne bloque le paquet, ou le serveur n'écoute pas sur la cible. Consulte les translations, compteurs et journaux, puis vérifie la route vers le serveur et le port d'écoute. Confirme les zones de sécurité traversées. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne crée pas une règle any-any pour contourner un point de blocage non identifié. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 16 — Une règle statique NAT subsiste après retrait du service

**Analyse.** Une publication ancienne peut laisser une correspondance permanente vers un hôte ou un port inutilisé. Identifie le propriétaire du service, confirme l'absence de dépendance, retire la règle selon la procédure de changement puis vérifie l'exposition externe. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne garde pas une redirection parce qu'elle ne génère plus de trafic. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 17 — Le serveur a changé d'adresse DHCP

**Analyse.** La redirection statique ou l'ACL vise encore l'ancienne adresse interne. Utilise une adresse réservée ou statique conforme au plan, mets à jour la cible après approbation et vérifie les routes et la sécurité du serveur. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne lie pas un service publié à une adresse fluctuante sans stratégie d'adressage. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 18 — La règle NAT utilise l'interface externe incorrecte

**Analyse.** La traduction peut se faire avec une adresse qui n'est pas celle du chemin de sortie prévu. Vérifie la route effective, le WAN actif, l'adresse de l'interface et la règle NAT. Si plusieurs fournisseurs sont présents, examine les chemins de retour asymétriques. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne suppose pas que la première interface WAN dans la configuration est celle qu'utilise le trafic. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 19 — Une politique bloque le flux après traduction

**Analyse.** Les règles de filtrage peuvent évaluer les adresses avant ou après traduction selon la plateforme et l'étape du traitement. Consulte la documentation du produit, identifie l'adresse vue au point de filtrage et vérifie les journaux. Écris la règle dans le référentiel d'adresses réellement évalué. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne suppose pas un ordre NAT/filtrage universel sur tous les équipements. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 20 — Un service publié reçoit des tentatives répétées

**Analyse.** La publication peut être normale mais exposer un service à des scans et tentatives d'accès Internet. Vérifie les sources, la fréquence, les journaux applicatifs et les authentifications. Restreins les sources si possible, corrige le service et applique les contrôles de détection. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Le NAT n'est pas un mécanisme d'identification ni un pare-feu applicatif. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 21 — L'ACL NAT utilise any

**Analyse.** La règle peut sélectionner des sources qui ne devraient pas être traduites ou inclure un trafic inattendu. Remplace le large sélecteur par les préfixes nécessaires, vérifie les routes et teste les flux de chaque réseau prévu. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne traduis pas automatiquement tous les réseaux sans inventaire. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 22 — La session VPN ne fonctionne qu'en un sens

**Analyse.** Le chemin de retour, le filtrage, les sélecteurs de chiffrement ou la politique NAT peuvent être asymétriques. Vérifie les routes dans les deux sens, les sous-réseaux autorisés des deux pairs, l'exemption NAT et les journaux de chaque extrémité. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne modifie pas seulement la règle du côté qui affiche le symptôme sans examiner le pair distant. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 23 — Un service reste joignable après la suppression d'une redirection

**Analyse.** Une autre règle, une adresse publique différente, un autre routeur ou un accès IPv6 peut publier le service. Examine l'ensemble des traductions, les règles de filtrage, les autres équipements WAN et les services IPv6. Confirme le point de passage réel avant de conclure. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne suppose pas qu'une seule entrée NAT était l'unique chemin vers le service. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 24 — Un réseau interne ne peut pas joindre un service par son adresse publique

**Analyse.** Le routeur peut ne pas prendre en charge la réflexion NAT, ou la route et le DNS interne peuvent être mal adaptés. Vérifie si les clients internes doivent utiliser l'adresse privée, un DNS divisé ou une fonctionnalité de réflexion NAT documentée. Teste depuis LAN et WAN séparément. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne considère pas l'échec de réflexion NAT comme preuve que la publication externe est en panne. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 25 — Après changement d'opérateur, NAT cesse de fonctionner

**Analyse.** L'adresse WAN, la route par défaut, le mode d'accès ou les règles amont peuvent avoir changé. Confirme l'adresse reçue, la passerelle, la route, les interfaces inside/outside et les politiques du nouveau lien. Valide l'accès IP avant de diagnostiquer DNS. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne réutilise pas automatiquement l'ancienne adresse publique dans les règles. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 26 — Les journaux NAT n'identifient pas directement le client

**Analyse.** Le journal peut n'afficher que l'adresse traduite, le détail des ports peut manquer ou plusieurs utilisateurs peuvent partager une adresse publique. Corrèle heure, ports, journaux du dispositif, DHCP et autres événements disponibles. Assure une synchronisation temporelle et respecte les règles d'accès aux données. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne prétends pas qu'une adresse publique partagée identifie seule un utilisateur. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 27 — Un service de DMZ peut atteindre tous les serveurs

**Analyse.** Le filtrage inter-zone est trop permissif ; NAT ne limite pas les mouvements latéraux après la traduction. Rédige les flux indispensables de la DMZ vers les systèmes internes et bloque les autres communications. Teste depuis un hôte de simulation de la zone exposée. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne considère pas qu'un serveur placé en DMZ est automatiquement isolé. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 28 — La traduction statique répond mais l'application échoue

**Analyse.** Le transport peut arriver jusqu'au serveur tandis que TLS, le nom d'hôte, les dépendances applicatives ou l'authentification échouent. Examine le test TCP, le certificat, les journaux de l'application, le DNS public et le service à l'écoute. Sépare la traduction du diagnostic applicatif. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne publie pas davantage de ports lorsqu'une connexion atteint déjà le bon service. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 29 — L'entreprise migre vers IPv6

**Analyse.** Le NAT IPv4 existant ne décrit pas nécessairement la politique IPv6 et certains services peuvent avoir des adresses globales. Inventorie les adresses IPv6, les routes, les règles de pare-feu et les services exposés. Valide les accès autorisés et refusés sur la pile IPv6. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne suppose pas que l'absence de NAT signifie l'absence de sécurité ou que le NAT IPv4 protège IPv6. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 30 — La route de retour passe par un autre routeur

**Analyse.** Une asymétrie peut empêcher le dispositif de traduire correctement les réponses ou de suivre l'état de session. Dessine les deux directions du chemin, vérifie les routes et la conception de sortie. Assure-toi que les paquets de réponse reviennent par le dispositif qui détient l'état NAT. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne modifie pas aléatoirement les délais NAT pour corriger une route asymétrique. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

### Cas de dépannage 31 — Une règle temporaire de publication reste active

**Analyse.** Une redirection utilisée lors d'un test peut rester oubliée et maintenir une surface d'attaque inutile. Vérifie son propriétaire et les usages récents, retire-la après validation et ajoute une date de revue aux futures publications temporaires. Distingue toujours le résultat de la traduction, la décision de filtrage, le chemin de routage et le fonctionnement du service. Note l'heure et les paramètres du test afin de reproduire le même flux après correction.

**Erreur à éviter.** Ne laisse pas une publication non documentée parce qu'aucun incident n'a été signalé. Après la correction, teste l'accès légitime et un accès qui doit rester bloqué. Documente la cause, l'action, le responsable et la date de revue.

Fin du cours.