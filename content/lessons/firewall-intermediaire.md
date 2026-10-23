---
node_id: firewall-intermediaire
title: Pare-feu & NGFW - Intermédiaire
---
# Pare-feu & NGFW - Intermédiaire
**Niveau :** INTERMÉDIAIRE

Un pare-feu ne se résume pas à une liste de ports autorisés ou interdits. À mesure qu'un réseau grandit, la difficulté principale devient la conception d'une politique cohérente : définir les zones de confiance, identifier les flux réellement nécessaires, gérer les connexions dans les deux sens, articuler filtrage et traduction d'adresses, puis vérifier que les règles appliquées correspondent à l'intention de sécurité. Une politique trop permissive laisse circuler des échanges inutiles ; une politique trop restrictive peut interrompre des services critiques et pousser les équipes à ajouter rapidement des exceptions mal documentées.

Le terme **NGFW** (*Next-Generation Firewall*, pare-feu de nouvelle génération) désigne généralement une plateforme qui associe le filtrage réseau traditionnel à des fonctions plus évoluées : suivi d'état, identification d'applications, prévention d'intrusion (IPS), filtrage d'URL, contrôle fondé sur l'identité, réputation de destinations et inspection de fichiers. Les fonctions exactes dépendent du produit, de sa version, des licences et des profils activés. Le sigle ne garantit ni une inspection complète ni une protection automatique contre toutes les menaces.

Ce cours intermédiaire s'appuie sur un scénario d'entreprise disposant d'un réseau utilisateurs, d'une DMZ hébergeant un serveur Web, d'un réseau d'administration et d'une sortie Internet. Il approfondit les ACL IPv4, les pare-feu à états, les zones de sécurité, la logique des règles, la relation entre NAT et filtrage, l'inspection applicative, les journaux, la haute disponibilité et une méthode de dépannage reproductible. Les exemples Cisco IOS/IOS XE illustrent des principes ; ils doivent être adaptés à la version et au modèle utilisés. La syntaxe et l'ordre de traitement d'un NGFW dédié peuvent être différents.

La règle de méthode est simple : concevoir d'abord la politique, puis la traduire dans le produit. Chaque règle doit avoir un objectif, un propriétaire métier, des sources et destinations définies, un service explicite, une action, une justification, une date de révision et un moyen de test. L'exploitation doit ensuite confirmer que la règle fonctionne réellement et ne crée pas de chemin d'accès non souhaité.

> **Analogie** : Un pare-feu d'entreprise ressemble à un bâtiment avec plusieurs secteurs. Le poste de garde extérieur contrôle l'entrée, les portes entre les secteurs limitent les déplacements, et les badges précisent qui a accès à quelle salle. Un NGFW ajoute des contrôles plus contextuels : il peut reconnaître le type d'activité, examiner certains contenus et déclencher une alerte. Mais une porte sophistiquée ne remplace pas une architecture claire ni la vérification régulière des droits.

---

## 1. La théorie et les algorithmes

### 1.1. Du filtrage simple à la politique de sécurité

Un pare-feu applique des décisions à des communications qui traversent un point de contrôle. Une politique peut se baser sur plusieurs dimensions :

- **Source** : adresse IP, sous-réseau, objet réseau, utilisateur ou groupe d'identité si cette information est disponible.
- **Destination** : serveur, plage réseau, zone, nom d'application ou objet de destination.
- **Service** : protocole IP, port TCP/UDP, type ICMP ou application reconnue.
- **Contexte** : interface d'entrée, zone source, zone de destination, horaire, état de connexion ou risque estimé.
- **Action** : autoriser, refuser, inspecter, réinitialiser, demander une authentification ou journaliser, selon les fonctions du produit.

Un filtre de paquets traditionnel peut décider essentiellement à partir des champs des couches réseau et transport. Un pare-feu à états conserve en plus le contexte d'un flux. Un NGFW peut chercher à identifier l'application au-delà de son seul port, puis appliquer des contrôles d'inspection spécifiques. Ces catégories ne sont pas toujours mutuellement exclusives : une même plateforme peut effectuer plusieurs types de contrôle.

Le filtrage ne doit pas être confondu avec le routage. Le routage détermine le chemin que le paquet peut emprunter ; le pare-feu détermine si le flux est autorisé sur ce chemin. Une route valide ne signifie pas qu'une communication est autorisée. Inversement, une règle permissive ne compense pas l'absence de route vers le réseau de destination. La résolution d'un incident demande donc de vérifier à la fois le chemin réseau et la politique de sécurité.

### 1.2. Règles ordonnées, première correspondance et refus implicite

Dans une ACL ordonnée, les entrées sont généralement examinées de haut en bas. La première entrée qui correspond au paquet détermine la décision. Il faut comprendre cette logique avant de modifier une liste : une règle de refus placée après une autorisation générale ne peut pas bloquer le trafic déjà accepté par la règle générale.

Exemple d'une ACL mal ordonnée :

```text
ip access-list extended BLOQUER-SSH
 permit ip 192.168.10.0 0.0.0.255 any
 deny tcp 192.168.10.0 0.0.0.255 any eq 22
```

La première ligne autorise tout trafic IP depuis le sous-réseau `192.168.10.0/24`. La seconde ligne ne sera donc jamais atteinte pour un paquet correspondant à cette autorisation. La correction consiste à placer l'exception spécifique avant l'autorisation plus large :

```text
ip access-list extended BLOQUER-SSH
 deny tcp 192.168.10.0 0.0.0.255 any eq 22
 permit ip 192.168.10.0 0.0.0.255 any
```

Cet exemple sert à comprendre l'ordre des lignes. En production, il est souvent préférable d'autoriser seulement les services nécessaires plutôt que de terminer par une autorisation globale `permit ip`. Sur de nombreux mécanismes ACL, une ligne de refus implicite se trouve à la fin ; si aucun élément ne correspond explicitement, le paquet est rejeté. Il faut vérifier ce comportement dans la documentation de la plateforme utilisée.

> **Piège :** Un compteur élevé sur une règle d'autorisation ne prouve pas que la règle est correcte. Il prouve seulement que du trafic correspond à ses critères. Vérifiez le sens du trafic, la destination réelle, le service et le besoin métier avant de considérer la règle comme sûre.

### 1.3. ACL standard et ACL étendue sur Cisco IOS

Une ACL standard IPv4 filtre principalement sur l'adresse source. Une ACL étendue peut comparer plusieurs champs, notamment source, destination, protocole et ports. En général, une ACL standard convient à une autorisation simple liée à l'identité réseau de la source ; une ACL étendue est préférable quand il faut préciser les services et les destinations.

Les ACL peuvent être nommées ou numérotées. Les ACL nommées facilitent la lecture et la modification, car leur nom peut exprimer un objectif. Les commentaires `remark` contribuent à rendre la politique compréhensible. Les numéros historiques ont encore un rôle dans certaines configurations, mais les ACL nommées sont souvent plus maintenables.

Exemple d'ACL étendue qui permet au réseau utilisateurs d'interroger un DNS interne et d'accéder à un serveur HTTPS de la DMZ :

```text
ip access-list extended UTILISATEURS-VERS-SERVICES
 remark DNS vers le resolueur interne
 permit udp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 53
 remark DNS sur TCP, utilise notamment les réponses volumineuses et transferts selon le role
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 53
 remark HTTPS vers le serveur de publication
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.30.20 eq 443
 remark Journaliser les autres tentatives depuis cette source si le volume est raisonnable
 deny ip 192.168.10.0 0.0.0.255 any log
```

Cette ACL n'est qu'un exemple de critères. Pour qu'elle ait un effet, elle doit être appliquée au bon emplacement et dans le bon sens, par exemple sur une interface avec `ip access-group`. Il faut connaître le chemin réel des paquets, les besoins DNS, les services requis et les conséquences des journaux avant d'utiliser la configuration. Elle ne met pas en place à elle seule une politique complète pour l'ensemble du réseau.

Un masque générique (*wildcard mask*) représente les bits comparés par une ACL Cisco. Pour le réseau `192.168.10.0/24`, le masque de sous-réseau est `255.255.255.0`, alors que le masque générique est `0.0.0.255`. Un bit à `0` exige une correspondance sur le bit correspondant ; un bit à `1` permet une différence. Pour un hôte précis, on emploie souvent `host 192.168.20.10`, équivalent conceptuel à une comparaison exacte de l'adresse.

### 1.4. Le suivi d'état (*stateful inspection*)

Dans un réseau TCP, une session commence fréquemment par un échange de synchronisation (SYN, puis SYN-ACK, puis ACK), même si les comportements réels varient selon les applications, les extensions TCP et les mécanismes intermédiaires. Un pare-feu à états maintient un enregistrement de flux, généralement composé des adresses, ports, protocole et informations d'état. Il peut autoriser les paquets de retour s'ils correspondent à une session autorisée.

Considérons un poste `192.168.10.25` qui ouvre une session HTTPS vers `203.0.113.80:443`. Son port source peut être temporaire, par exemple `53012`. Le flux peut être représenté ainsi :

```text
Client interne                              Serveur externe
192.168.10.25:53012                         203.0.113.80:443
       |                                          |
       |---------- SYN -------------------------->|
       |<--------- SYN-ACK -----------------------|
       |---------- ACK / données ---------------->| 
       |<--------- données de réponse ------------|
       |                                          |
       +---- Le pare-feu associe les paquets au même état ----+
```

Lorsqu'il reconnaît une session valide, le pare-feu stateful peut permettre le trafic de réponse sans autoriser de nouvelles connexions entrantes arbitraires vers le poste. Il ne faut toutefois pas supposer que toute réponse est automatiquement sans risque : un flux peut être abusé, une session peut être initiée par une règle trop permissive, et certaines plateformes gèrent différemment les protocoles non orientés connexion ou les délais d'expiration.

Pour UDP, qui ne réalise pas de poignée de main comparable à TCP, le suivi d'état se base sur une association de flux et des temporisations. Pour ICMP, le produit peut suivre des types et identifiants de messages. Le mot « état » signifie donc que le pare-feu conserve un contexte de communication ; il ne signifie pas que le contenu est nécessairement sûr ou que le produit comprend toutes les intentions applicatives.

Un pare-feu stateful peut rejeter des paquets qui semblent appartenir à une session mais arrivent sans état associé, expirent après une longue pause ou empruntent un chemin asymétrique. Ces rejets peuvent être légitimes ou indiquer un problème de conception. Les journaux du pare-feu, la table de sessions et une capture de paquets aident à les distinguer.

### 1.5. Règles avec états et règles sans états : conséquences opérationnelles

| Aspect | ACL sans suivi complet de session | Pare-feu à états / NGFW |
|---|---|---|
| Décision | Champs du paquet et ordre des règles | Champs du paquet, état du flux et fonctions activées |
| Trafic retour | Souvent à décrire explicitement ou à prendre en charge par une logique associée | Peut être autorisé s'il correspond à un flux établi |
| Visibilité | Compteurs et journaux disponibles selon plateforme | Journaux de sessions, applications, utilisateurs et inspection selon produit |
| Risque de complexité | Liste de règles longue et délicate à maintenir | Table de sessions, profils d'inspection, exceptions et dépendances supplémentaires |
| Usage typique | Filtrage de routeur, contrôle simple, protection d'interface | Frontière d'entreprise, segmentation, contrôle des sessions |
| Limite | Compréhension limitée du contexte de session | N'identifie pas automatiquement toute application et n'élimine pas les faux positifs |

Le choix dépend de l'architecture et du besoin. Une ACL d'interface demeure utile pour limiter les accès à un routeur, filtrer un trafic de gestion ou réduire des flux inutiles. Elle ne doit pas être présentée comme l'équivalent fonctionnel d'un NGFW avec inspection applicative et IPS.

### 1.6. Modèle de zones de sécurité

Une zone regroupe des interfaces ou réseaux ayant une fonction ou un niveau de confiance similaire. Une architecture classique peut distinguer :

- **Outside / WAN** : réseau non fiable, généralement Internet ou un opérateur.
- **Inside / LAN** : postes et services internes, sans supposer que tous les postes sont fiables.
- **DMZ** : services exposés ou accessibles depuis l'extérieur, isolés du LAN.
- **Management** : administration des équipements et serveurs d'infrastructure.
- **Guest** : équipements invités, isolés des ressources internes.
- **Serveurs internes** : applications ou bases de données dont l'accès doit être fortement limité.
- **VPN** : utilisateurs ou sites distants, avec des règles tenant compte du profil autorisé.

Le principe est de raisonner sur les communications entre zones, et non seulement entre interfaces. Les flux nécessaires doivent être décrits pour chaque paire source-destination. Une DMZ n'est pas « sûre » par son seul nom : elle le devient lorsque les règles empêchent, par exemple, un serveur Web compromis de se connecter librement aux postes utilisateurs ou à l'ensemble des bases de données.

```text
                       INTERNET / WAN
                             |
                     +----------------+
                     | Pare-feu / NGFW |
                     +----------------+
                       /      |       \
                      /       |        \
                 INSIDE      DMZ     MANAGEMENT
                utilisateurs  Web     bastion / admin
                    |          |          |
             postes et      serveur    postes admin
             applications    HTTPS     autorisés
                    |
             SERVICES INTERNES
            DNS, identité, bases

Politique type :
  WAN -> DMZ        : publications précises seulement
  WAN -> INSIDE     : refus par défaut, exceptions documentées
  INSIDE -> WAN     : sorties nécessaires avec inspection et journalisation
  DMZ -> INSIDE     : uniquement les dépendances explicitement requises
  MANAGEMENT -> FW  : administration depuis des sources autorisées
  GUEST -> INSIDE   : refus, avec accès Internet limité selon besoin
```

Selon le produit, les règles peuvent être définies par interfaces, zones, objets d'adresses, objets de services et profils de sécurité. Il faut identifier la sémantique exacte : certains appareils considèrent les zones comme des groupes d'interfaces, tandis que d'autres distinguent interfaces logiques, contextes virtuels et politiques globales.

### 1.7. DMZ : publier sans ouvrir le réseau interne

Une DMZ héberge typiquement les services qui doivent être joignables depuis Internet : serveur Web, relais de courrier ou passerelle d'accès. L'objectif est de limiter les conséquences d'une compromission d'un service exposé. La zone DMZ doit être séparée des postes internes et n'avoir que les autorisations nécessaires vers les services de soutien.

Par exemple, un serveur Web de DMZ peut recevoir des connexions HTTPS depuis Internet. S'il utilise une base de données située dans un réseau de serveurs internes, l'autorisation requise peut être limitée à l'adresse du serveur Web vers l'adresse de la base et au port réellement utilisé. Elle ne devrait pas autoriser la DMZ entière vers tous les hôtes internes sur tous les ports.

| Source | Destination | Service | Décision de principe | Justification |
|---|---|---|---|---|
| Internet | Adresse publique du serveur Web | TCP 443 | Autoriser après publication et inspection appropriées | Site accessible au public |
| Internet | LAN utilisateurs | Tout nouveau flux | Refuser | Aucun service interne à exposer directement |
| Serveur Web DMZ | Base de données précise | Port applicatif requis | Autoriser si nécessaire | Dépendance de l'application |
| Serveur Web DMZ | LAN entier | Tout | Refuser | Éviter les mouvements latéraux |
| LAN utilisateurs | DNS interne | UDP/TCP 53 | Autoriser selon besoin | Résolution des noms |
| Réseau d'administration | Équipements gérés | SSH/HTTPS d'administration | Autoriser de façon limitée | Gestion contrôlée |

L'exposition publique doit être complétée par des mises à jour, une configuration applicative sûre, une journalisation des connexions et une surveillance. Le pare-feu ne détectera pas forcément un abus légitime d'une application qui écoute sur le port attendu.

### 1.8. NAT, PAT et filtrage : trois questions différentes

La traduction d'adresses réseau (*Network Address Translation*, NAT) modifie certaines adresses ou certains ports IP afin de permettre la communication entre espaces d'adressage différents. Le PAT (*Port Address Translation*) permet à plusieurs connexions internes de partager une adresse publique en distinguant les flux avec des numéros de port ou d'autres informations de traduction.

NAT ne remplace pas le contrôle d'accès. Il faut répondre séparément à trois questions :

1. **Routage** : existe-t-il un chemin vers la destination ?
2. **Traduction** : quelles adresses/ports le flux porte-t-il avant et après NAT ?
3. **Politique de sécurité** : ce flux est-il autorisé par les règles applicables ?

L'ordre exact dans lequel un appareil traduit et évalue certaines parties d'un flux dépend de sa plateforme, du type de NAT et de la politique utilisée. Certains NGFW évaluent les règles à partir des adresses originales, d'autres affichent aussi des objets traduits ou appliquent différentes étapes internes. Il ne faut pas transposer aveuglément une hypothèse de traitement d'un constructeur à un autre.

Exemple conceptuel de NAT sortant : un poste `192.168.10.25` utilise une adresse privée pour joindre un site Internet. Le pare-feu remplace l'adresse source par une adresse publique et conserve une association de traduction afin de pouvoir acheminer les réponses vers le poste d'origine. Le trafic est également soumis à la politique de sécurité et à la table d'état selon les fonctions de la plateforme.

Exemple conceptuel de publication : l'adresse publique `203.0.113.20` est traduite vers le serveur privé de DMZ `192.168.30.20`. Cette traduction ne devrait pas être interprétée comme une autorisation globale. La règle d'accès doit encore limiter les sources, les destinations et les services à ce qui est réellement destiné au public.

> **Piège :** Ajouter une règle NAT pour publier un serveur ne signifie pas qu'il faut autoriser toutes les connexions entrantes. À l'inverse, une règle de filtrage correcte ne fonctionnera pas si la traduction, la route de retour, le DNS public ou le routage de la DMZ sont incorrects.

### 1.9. NAT sortant et NAT statique : représentations

```text
SORTIE INTERNET (PAT)

Poste privé                  Pare-feu                       Internet
192.168.10.25:53012  --->  [politique + état + PAT] --->  198.51.100.80:443
        ^                                                    |
        |              réponse vers association PAT           |
        +----------------------------------------------------+

PUBLICATION D'UN SERVEUR

Client Internet  ---> 203.0.113.20:443 ---> [DNAT / règle d'accès]
                                               |
                                               v
                                      192.168.30.20:443
                                          Serveur DMZ
```

Les adresses sont réservées à la documentation. Il ne faut pas configurer ces blocs comme des adresses publiques réelles sur Internet. Dans un exercice, remplacez-les par les adresses du laboratoire.

### 1.10. Identification applicative dans un NGFW

Le filtrage par port reste utile, mais ne suffit pas à reconnaître une application. Plusieurs applications utilisent TCP 443, d'autres utilisent des ports non standards, et une application peut encapsuler des protocoles dans du trafic chiffré. Un NGFW peut analyser des caractéristiques de session et des éléments applicatifs afin d'attribuer une identité d'application, parfois après quelques paquets ou échanges.

La visibilité dépend de plusieurs facteurs : protocoles pris en charge, mises à jour des signatures, configuration, comportement de l'application, chiffrement, encapsulation et éventuel usage d'un proxy. Si un flux ne peut être identifié, la plateforme peut appliquer une catégorie générique, attendre davantage de données ou traiter la connexion selon une politique de repli. La gestion des connexions « inconnues » doit être explicitement conçue.

L'identité applicative peut améliorer la précision de règles telles que « autoriser l'application de collaboration approuvée » plutôt que « autoriser tout TCP/443 ». Elle peut aussi introduire des faux positifs ou des faux négatifs. Tester les applications métier après toute modification de signature ou de profil reste indispensable.

### 1.11. IPS, filtrage Web, réputation et inspection de fichiers

Un système de prévention d'intrusion (*Intrusion Prevention System*, IPS) cherche à détecter et potentiellement bloquer des comportements associés à des exploits, des signatures d'attaque ou des anomalies. En mode prévention, une détection peut interrompre la connexion. En mode détection seulement, l'équipement peut alerter sans bloquer. Le mode et les profils choisis modifient fortement l'impact opérationnel.

Le filtrage Web peut appliquer une politique selon une URL, un domaine ou une catégorie de contenu. La réputation s'appuie sur des informations de menace associées à une adresse, un domaine ou un objet. Le contrôle de fichiers peut identifier les types de fichiers, analyser certains contenus ou s'intégrer à des moteurs antimalware. Les possibilités sont variables ; la présence d'une fonction dans une interface ne garantit pas qu'elle est licenciée, activée ni placée sur le bon chemin réseau.

Un profil IPS trop agressif peut bloquer des applications légitimes ; un profil trop permissif peut manquer des attaques. Le bon déploiement consiste souvent à commencer en mode observation ou dans un périmètre pilote, analyser les alertes, ajuster les exceptions avec justification, puis activer le blocage sur les services ciblés. Une exception permanente ne doit pas être ajoutée uniquement pour faire disparaître une alerte gênante.

### 1.12. Inspection TLS/SSL : avantages et limites

Le trafic HTTPS protège les données en transit grâce au chiffrement TLS, mais ce chiffrement peut empêcher un appareil intermédiaire de lire le contenu applicatif. Certains NGFW proposent une inspection TLS : l'équipement termine ou intercepte une connexion selon une architecture de déchiffrement autorisée, inspecte le contenu, puis établit une autre connexion chiffrée. Les détails diffèrent selon le mode d'inspection.

Ce mécanisme a des conséquences : déploiement d'une autorité de certification de confiance sur les postes, compatibilité avec les applications, charge CPU, confidentialité, exigences légales et exceptions nécessaires pour certains services. Les applications utilisant l'épinglage de certificat (*certificate pinning*), certains logiciels médicaux ou financiers et quelques mécanismes d'authentification peuvent échouer lorsque leur TLS est intercepté. Des données personnelles ou sensibles ne doivent pas être déchiffrées sans cadre approprié.

Une politique d'inspection doit préciser les catégories de trafic inspectées, les exclusions justifiées, la gestion des certificats, les traces conservées et les responsables de validation. Exclure tout HTTPS serait souvent trop permissif ; tenter de déchiffrer sans plan peut provoquer des interruptions et porter atteinte à la confidentialité.

### 1.13. DNS, ICMP et protocoles auxiliaires

DNS est souvent nécessaire pour que les utilisateurs accèdent aux services par leur nom. Un réseau d'entreprise peut obliger les postes à interroger des résolveurs approuvés plutôt que des serveurs externes. Ce choix améliore la cohérence et la visibilité mais doit être compatible avec les clients VPN, les équipements mobiles et les applications autorisées. DNS utilise principalement UDP 53, mais TCP 53 est également nécessaire dans différents cas, dont certaines réponses de grande taille et des opérations interserveurs.

ICMP apporte des messages de contrôle et de diagnostic. Tout bloquer peut gêner le diagnostic, les messages d'erreur de réseau et certains mécanismes liés à la découverte de la taille de paquet. La politique doit autoriser les types de messages requis plutôt que faire confiance ou refuser aveuglément l'ensemble d'ICMP. IPv6 dépend notamment de messages ICMPv6 pour des fonctions fondamentales comme la découverte de voisins ; une politique IPv6 ne doit pas réutiliser mécaniquement les hypothèses IPv4.

Les autres protocoles souvent oubliés sont NTP, DHCP, syslog, SNMP, RADIUS/TACACS+, les services d'annuaire, les mécanismes de sauvegarde et les échanges de supervision. Les ports et les directions exactes doivent correspondre à l'architecture. Avant de bloquer un flux inconnu, identifiez le service et son propriétaire au lieu de créer une autorisation générale « pour que cela fonctionne ».

### 1.14. Direction, interfaces et asymétrie de routage

L'application d'une ACL en entrée examine les paquets lorsqu'ils entrent sur une interface, avant qu'ils ne soient transmis plus loin selon le traitement de la plateforme. Une ACL en sortie examine le trafic qui quitte l'interface. Le positionnement influe sur les paquets visibles et sur la capacité à limiter les sources au plus tôt. Une ACL mal placée peut avoir l'air correcte mais ne jamais rencontrer le trafic attendu.

Avec un pare-feu stateful, une connexion initiée d'un côté crée habituellement un état qui permet au flux de retour. Si les paquets aller passent par un pare-feu, mais que les paquets retour empruntent un autre chemin qui ne partage pas la session, les réponses peuvent être rejetées. C'est l'asymétrie de routage. La haute disponibilité, le routage dynamique, le multi-homing et certaines architectures cloud peuvent créer ces situations.

```text
Chemin attendu :
Client ----> Pare-feu A ----> Serveur
Client <---- Pare-feu A <---- Serveur
                    état commun au trajet

Chemin asymétrique possible :
Client ----> Pare-feu A ----> Serveur
Client <---- Route différente / Pare-feu B <---- Serveur
             l'état initial peut manquer sur B
```

Le remède n'est pas toujours d'assouplir la sécurité. On peut corriger le routage, aligner les chemins aller-retour, utiliser une architecture de synchronisation d'état conçue et prise en charge, ou adapter le design lorsqu'une asymétrie est réellement voulue. La décision doit s'appuyer sur la documentation constructeur.

### 1.15. Règles fondées sur l'identité

Certains NGFW peuvent associer une session à un utilisateur ou à un groupe d'annuaire. Cela permet des politiques plus compréhensibles que des règles exclusivement fondées sur les adresses IP. L'identité peut toutefois devenir obsolète si une machine change d'utilisateur, si une session d'annuaire expire, si un utilisateur passe par un VPN ou si plusieurs personnes partagent le même poste.

L'identité réseau ne remplace pas une authentification forte et ne prouve pas qu'une activité est légitime. Une adresse IP peut être usurpée dans certains contextes, un poste authentifié peut être compromis, et le rôle d'un utilisateur peut changer. Les politiques sensibles doivent tenir compte du groupe approuvé, de l'état du terminal, du service ciblé et, lorsque cela est approprié, d'une authentification supplémentaire.

### 1.16. Principes de conception : moindre privilège et refus par défaut

Le **moindre privilège** consiste à accorder seulement les autorisations indispensables, pour les destinations, services, utilisateurs et périodes nécessaires. Le **refus par défaut** signifie qu'une communication non expressément prévue est bloquée, sous réserve des protocoles essentiels et des contraintes du produit. Ces principes ne doivent pas être appliqués sans analyse des dépendances : un service peut exiger un flux auxiliaire non documenté, ou un changement de règle peut affecter une fonction partagée.

La qualité d'une politique se mesure à sa capacité à répondre à des besoins vérifiables sans ouvrir davantage que nécessaire. Les règles temporaires doivent expirer ou être révisées. Les objets réseau doivent avoir des noms explicites. Les règles redondantes, ombrées par d'autres règles, sans propriétaire ou jamais utilisées doivent être analysées avant suppression. Une faible activité n'est pas automatiquement une preuve d'inutilité : certaines opérations de secours, sauvegardes ou maintenances sont périodiques.

> **Astuce :** Rédigez chaque flux en langage simple avant de créer la règle : « Les postes du VLAN utilisateurs peuvent joindre le résolveur DNS interne sur les protocoles requis ; aucune autre communication directe vers le réseau de serveurs n'est autorisée. » Cette phrase facilite la validation technique et métier.

---

## 2. Configuration et pratique

### 2.1. Laboratoire de référence

Le laboratoire comprend un routeur ou pare-feu avec trois segments logiques. Les adresses ci-dessous sont des exemples privés pour le LAN et la DMZ, accompagnés d'une plage de documentation pour la représentation de l'adresse externe. Adaptez les interfaces à votre équipement et à votre simulateur.

| Zone | Réseau / adresse | Rôle |
|---|---|---|
| INSIDE | `192.168.10.0/24` | Postes utilisateurs |
| SERVEURS | `192.168.20.0/24` | DNS interne `192.168.20.10` et services internes |
| DMZ | `192.168.30.0/24` | Serveur Web `192.168.30.20` |
| MANAGEMENT | `192.168.40.0/24` | Station d'administration approuvée |
| OUTSIDE | Selon le laboratoire | Liaison vers Internet ou simulateur |

Définissez d'abord les communications attendues. Les utilisateurs doivent pouvoir résoudre les noms via le DNS approuvé et consulter le site Web publié. Le réseau d'administration doit gérer les équipements par SSH/HTTPS depuis des machines précises. Le serveur Web de DMZ ne doit pas pouvoir initier librement des connexions vers les postes utilisateurs. Les besoins d'administration depuis la DMZ doivent être limités et documentés.

### 2.2. Construire une matrice de flux

Une matrice de flux est une liste structurée des communications requises. Elle sert de contrat de conception entre les équipes réseau, systèmes et applicatives. Les champs habituels sont : identifiant, zone source, objet source, zone destination, objet destination, application/service, direction, action, justification, propriétaire, journalisation, date de fin ou de révision et test associé.

| ID | Source | Destination | Service | Action | Motif | Test de validation |
|---|---|---|---|---|---|---|
| F-001 | INSIDE | DNS `192.168.20.10` | UDP/TCP 53 | Autoriser | Résolution interne | `nslookup` ou `dig` vers le DNS prévu |
| F-002 | INSIDE | DMZ `192.168.30.20` | TCP 443 | Autoriser | Consultation du site | Navigateur ou `curl` HTTPS |
| F-003 | MANAGEMENT approuvé | Équipement réseau | TCP 22/443 selon besoin | Autoriser | Administration | Connexion depuis le bastion prévu |
| F-004 | DMZ | INSIDE utilisateurs | Tout nouveau flux | Refuser | Prévention du mouvement latéral | Tentative contrôlée depuis le serveur de test |
| F-005 | GUEST | INSIDE | Tout | Refuser | Isolement des invités | Test depuis le VLAN invité |
| F-006 | INSIDE | OUTSIDE | Services approuvés | Autoriser selon politique | Accès Internet professionnel | Tests applicatifs, journaux et analyse DNS |

La matrice doit distinguer « nécessaire », « souhaité » et « observé ». Une capture de trafic montre qu'un flux a eu lieu, mais ne prouve pas à elle seule qu'il est légitime. Les flux historiques peuvent contenir des habitudes obsolètes, des logiciels indésirables ou des accès déjà trop ouverts.

### 2.3. Configuration d'une ACL étendue sur routeur Cisco IOS

Voici un exemple illustratif de filtrage en entrée sur l'interface côté utilisateurs. Il limite les communications autorisées vers le DNS et le serveur Web, puis refuse les autres échanges provenant du réseau utilisateurs. Les noms d'interfaces sont fictifs et doivent correspondre au laboratoire.

```text
configure terminal
!
ip access-list extended INSIDE-IN
 remark Autoriser DNS UDP vers le resolveur de l'entreprise
 permit udp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 53
 remark Autoriser DNS TCP si requis par le service
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 53
 remark Autoriser HTTPS vers le serveur Web cible
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.30.20 eq 443
 remark Refuser et compter les autres paquets de ce reseau
 deny ip 192.168.10.0 0.0.0.255 any log
!
interface GigabitEthernet0/1
 description Vers VLAN utilisateurs - exemple uniquement
 ip access-group INSIDE-IN in
!
end
show access-lists INSIDE-IN
show ip interface GigabitEthernet0/1
```

Cet exemple peut être trop strict pour un vrai poste, car une navigation Web et d'autres applications nécessitent souvent plusieurs services autorisés, notamment DHCP, NTP, authentification, mises à jour ou accès Internet. Il ne doit être déployé qu'après définition complète des besoins. Il illustre la façon de structurer les lignes, les remarques et la vérification de l'application.

Sur une ACL Cisco IOS, `log` peut générer des messages lors des correspondances de refus, mais l'impact dépend de la plateforme et de la fréquence du trafic. Évitez de produire un volume de logs excessif sur un équipement sensible. Si la syntaxe ou la commande de vérification diffère sur votre image IOS, consultez l'aide intégrée et le guide de configuration de cette version.

Pour modifier une ACL existante, il faut comprendre les numéros de séquence et l'ordre des règles. Une modification en place peut momentanément produire un comportement inattendu si des lignes sont insérées au mauvais endroit. En environnement critique, préparez une configuration complète, sauvegardez l'état actuel et définissez une procédure de retour arrière.

### 2.4. Protéger l'accès d'administration par ACL VTY

L'administration du routeur doit être réservée aux sources de confiance. Une ACL standard peut limiter les adresses pouvant établir une session VTY, en complément de SSH, d'une authentification robuste et de la gestion des comptes. Exemple pédagogique :

```text
configure terminal
ip access-list standard MGMT-ONLY
 remark Uniquement la station d'administration approuvee
 permit host 192.168.40.10
 deny any log
!
line vty 0 4
 access-class MGMT-ONLY in
 transport input ssh
 login local
!
end
show running-config | section line vty
show access-lists MGMT-ONLY
```

Les numéros de lignes VTY, l'existence de `login local`, la configuration de l'utilisateur local et les paramètres SSH varient selon les images et matériels. Dans une vraie infrastructure, privilégiez un bastion, une authentification centralisée appropriée, une authentification multifacteur lorsque disponible, des clés correctement gérées et une journalisation des sessions. Ne laissez pas l'administration exposée directement à Internet sans justification et protection explicite.

> **Danger :** Une ACL VTY mal conçue peut vous empêcher de gérer l'équipement à distance. Avant de l'appliquer, vérifiez l'adresse source réelle de votre session, conservez un accès console ou un chemin de secours et préparez une procédure de restauration. Ne faites pas ce changement sur un routeur distant critique sans fenêtre de maintenance et stratégie de retour arrière.

### 2.5. Lire les compteurs et confirmer l'application

Après configuration, vérifiez plus que la présence du texte dans la configuration. Contrôlez l'interface où l'ACL est appliquée, le sens `in` ou `out`, les lignes qui comptent les paquets, les routes et la connectivité. Une règle sans compteur peut être correcte mais non sollicitée ; elle peut aussi être placée au mauvais endroit, contenir une adresse erronée ou ne pas correspondre à la circulation réelle.

Commandes de vérification utiles sur plusieurs plateformes Cisco IOS/IOS XE, selon l'image :

```text
show access-lists
show ip access-lists
show ip interface
show ip route
show running-config | section interface
show logging
```

Les commandes `show` précises varient selon l'équipement et la version. Utilisez `?` pour examiner l'aide contextuelle. Ne partagez pas des configurations ou journaux complets à l'extérieur sans retirer les adresses sensibles, les noms internes, les secrets, les clés, les jetons et les informations permettant de cartographier le réseau.

### 2.6. Comprendre une ACL qui bloque un flux légitime

Supposons que le poste `192.168.10.25` ne puisse pas atteindre le serveur HTTPS `192.168.30.20`. Vérifiez dans l'ordre :

1. Résolution du nom : pointe-t-il vers l'adresse attendue ?
2. Adresse, masque et passerelle du poste : le poste est-il dans le bon VLAN ?
3. Route aller vers le serveur : le routeur a-t-il une route correcte ?
4. Route de retour : le serveur sait-il renvoyer les réponses au poste ?
5. ACL : la bonne liste est-elle appliquée, au bon sens, sur le bon équipement ?
6. Ordre des lignes : une règle plus large précède-t-elle l'autorisation HTTPS ?
7. Service serveur : le processus écoute-t-il sur TCP 443 et son pare-feu hôte l'autorise-t-il ?
8. État, NAT et politiques intermédiaires : la session est-elle traduite ou rejetée ailleurs ?

Une méthode en couches évite d'accuser le pare-feu trop tôt. Si une capture montre le SYN quitter le client mais aucune réponse revenir, l'échec peut se situer dans le routage retour, une ACL, le service ou un autre point de contrôle. Un simple test `ping` ne prouve ni que TCP 443 est ouvert ni que l'application est fonctionnelle.

### 2.7. Principes de configuration d'un pare-feu à zones sur Cisco IOS XE

Cisco IOS XE peut proposer un pare-feu à politiques fondées sur des zones (*Zone-Based Policy Firewall*, ZBF). Les interfaces sont affectées à des zones ; les flux entre zones peuvent être traités par des paires de zones et des politiques. La logique diffère d'une ACL étendue placée seule sur une interface. Le comportement par défaut et les règles applicables aux interfaces sans zone doivent être vérifiés dans le guide de la version utilisée.

Exemple conceptuel de composants, à adapter et tester dans un simulateur compatible :

```text
! Exemple de structure ZBF - pas un gabarit de production universel
zone security INSIDE
zone security OUTSIDE
!
class-map type inspect match-any CM-OUTBOUND-BASIC
 match protocol http
 match protocol https
 match protocol dns
!
policy-map type inspect PM-INSIDE-OUTSIDE
 class type inspect CM-OUTBOUND-BASIC
  inspect
 class class-default
  drop log
!
zone-pair security ZP-INSIDE-OUTSIDE source INSIDE destination OUTSIDE
 service-policy type inspect PM-INSIDE-OUTSIDE
!
! Les interfaces doivent être associées aux zones correspondantes.
! Leur configuration IP, le routage, le NAT et les exceptions nécessaires
! sont séparés et doivent être définis pour le laboratoire réel.
```

La disponibilité des noms de protocoles reconnus (`http`, `https`, `dns`), des types de classes et des actions dépend de l'image IOS XE. Une politique de production exige de traiter les besoins DNS, NTP, DHCP, VPN, management, ICMP, applications personnalisées et trafic vers le routeur lui-même. Ne collez pas le fragment ci-dessus dans un routeur en production sans valider la syntaxe et comprendre les règles par défaut.

Sur un pare-feu à zones, l'action `inspect` suit généralement l'état des protocoles pris en charge et peut autoriser les paquets de retour d'une session initiée de la zone source vers la zone destination. `pass` et `drop` ont des sémantiques différentes et ne doivent pas être substituées sans analyse. En particulier, une action qui ne suit pas l'état peut exiger des règles complémentaires dans l'autre sens pour assurer le trafic retour.

### 2.8. Organiser les objets sur un NGFW dédié

Les interfaces graphiques de NGFW emploient souvent des objets d'adresse, objets de réseau, groupes de services, zones et profils de sécurité. Les objets réutilisables réduisent les erreurs de saisie et facilitent l'évolution : si l'adresse d'un serveur change, un objet bien géré peut être modifié à un seul endroit. La contrepartie est qu'une modification d'objet partagé peut impacter plusieurs règles. Avant de changer un objet, examinez toutes ses références.

Préférez des noms lisibles et stables :

| Type | Exemple de nom | Contenu / objectif |
|---|---|---|
| Réseau | `NET-INSIDE-USERS` | `192.168.10.0/24` |
| Hôte | `HOST-DNS-PRIMARY` | `192.168.20.10` |
| Hôte | `HOST-WEB-DMZ` | `192.168.30.20` |
| Zone | `ZONE-DMZ` | Interfaces de la DMZ |
| Service | `SVC-HTTPS-TCP443` | TCP destination 443, si l'objet est nécessaire |
| Groupe | `GRP-DNS-SERVERS` | Résolveurs approuvés |
| Règle | `USERS-TO-DNS` | Autoriser DNS vers les résolveurs désignés |

Les conventions exactes doivent être définies par l'organisation. Évitez les noms vagues tels que `Allow1`, `Temp`, `AllServers` ou `Any-any-final`. Le nom doit exprimer l'intention sans devenir une phrase interminable.

### 2.9. Ordre recommandé d'une politique de contrôle d'accès

De nombreux moteurs évaluent les règles de haut en bas, mais les exceptions dépendent de la plateforme et certaines fonctionnalités s'appliquent à des étapes spécifiques. Une structure logique courante est :

1. Règles d'infrastructure indispensables, conformément à l'architecture validée.
2. Refus explicites de chemins interdits et facilement identifiables.
3. Autorisations précises entre zones pour les services métier.
4. Politiques de sortie et inspection applicative appropriée.
5. Règles de journalisation / détection conçues pour les événements pertinents.
6. Refus final ou règle par défaut, selon le fonctionnement du produit.

Cet ordre n'est pas une recette universelle. Par exemple, une plateforme peut gérer des listes de blocage, des pré-filtres et des règles de déchiffrement dans des moteurs différents ; une règle de blocage précoce pourrait précéder toutes les règles d'accès. La bonne pratique consiste à documenter le chemin d'évaluation du constructeur et à concevoir la politique en conséquence.

Après chaque changement, recherchez les règles ombrées, dupliquées et jamais utilisées. Une règle ombrée est une règle qui ne peut pas être atteinte parce qu'une règle précédente couvre déjà tous ses paquets. Les analyses automatiques peuvent aider, mais elles ne connaissent pas nécessairement l'intention métier ni les occurrences rares (sauvegardes mensuelles, maintenance ou bascule de secours).

### 2.10. Publier un serveur Web dans une DMZ

Pour publier un serveur, quatre éléments doivent être coordonnés : DNS public, adresse publique et NAT si requis, route jusqu'à la DMZ, et règle de sécurité qui autorise le service prévu. Sur un NGFW, la politique de sécurité peut devoir référencer une adresse réelle ou traduite suivant la plateforme. Vérifiez le guide du constructeur afin de savoir quelle adresse utiliser dans les critères de politique.

| Contrôle | Question de validation |
|---|---|
| DNS public | Le nom du site résout-il vers la bonne adresse publique ? |
| NAT / publication | L'adresse publique est-elle traduite vers le bon serveur et le bon port ? |
| Politique WAN vers DMZ | Seul le service publié est-il autorisé ? |
| Route et passerelle | Le serveur répond-il par le chemin prévu ? |
| Pare-feu hôte | Le système autorise-t-il le service localement ? |
| Certificat TLS | Le certificat, le nom du site et la chaîne de confiance sont-ils valides ? |
| Journalisation | Les autorisations et refus pertinents sont-ils visibles sans créer trop de bruit ? |
| Durcissement serveur | Le service est-il corrigé, minimal et surveillé ? |

Les tests doivent être exécutés depuis les réseaux qui représentent les utilisateurs réels : depuis Internet ou un réseau de test externe, depuis le LAN, et depuis la DMZ vers les réseaux internes. Tester seulement depuis l'intérieur peut masquer une erreur de publication ou de politique extérieure.

### 2.11. VPN distant et politique de pare-feu

Un VPN chiffre et transporte le trafic entre un utilisateur distant et le réseau de l'entreprise. Il ne doit pas automatiquement accorder au client VPN le même accès qu'un poste interne. Les pools d'adresses VPN, les groupes d'utilisateurs et les ressources accessibles doivent être déterminés dans une politique explicite.

Pour un prestataire, l'accès peut être limité à une application de maintenance ou à un bastion plutôt qu'à l'ensemble du LAN. Les règles doivent prévoir la révocation des comptes, la durée des accès, la mise à jour du client VPN, l'authentification multifacteur si disponible et la journalisation. Les profils de split tunneling, la résolution DNS, la route de retour et le chevauchement d'adresses peuvent affecter le fonctionnement ; leur conception doit être validée avant la mise en service.

Le chiffrement du tunnel ne garantit pas que le terminal distant est sain. Un poste infecté peut transporter du trafic malveillant dans un tunnel authentifié. Les contrôles d'identité, la posture de terminal, l'accès minimal et la surveillance réduisent ce risque.

### 2.12. Activer la journalisation utile

La journalisation doit répondre à des questions opérationnelles : quelle règle a autorisé ou rejeté le flux ? Quelle zone, application et identité sont concernées ? Quand le flux a-t-il commencé et combien de temps a-t-il duré ? L'événement est-il une anomalie ou un comportement attendu ? Les journaux utiles peuvent inclure les refus, les exceptions sensibles, les changements de politique, les événements IPS, les erreurs de VPN, les défaillances de haute disponibilité et les actions d'administration.

Évitez de consigner chaque paquet de chaque communication à très haut volume si le produit ou l'infrastructure de logs n'a pas été dimensionné pour cela. Un volume excessif augmente les coûts, dilue les alertes importantes et peut faire saturer la mémoire ou les systèmes de collecte. Les journaux doivent être horodatés de manière cohérente, idéalement en utilisant une synchronisation NTP fiable, centralisés lorsque possible, protégés contre la modification et conservés selon la politique de l'organisation.

| Événement | Intérêt | Attention |
|---|---|---|
| Refus vers un service sensible | Détecter une tentative non prévue | Beaucoup de bruit si une règle générale journalise tout |
| Autorisation d'administration | Reconstituer les accès privilégiés | Utiliser une source temps fiable et une identité corrélable |
| Événement IPS | Identifier une menace potentielle | Faux positifs et exceptions à contrôler |
| Changement de règle | Audit et retour arrière | Enregistrer qui, quand et pourquoi |
| Échec VPN | Diagnostiquer les accès distants | Retirer les secrets et données personnelles inutiles |
| Bascule HA | Expliquer une interruption | Corréler avec la perte de paquets et les sessions |

### 2.13. Sauvegarde, changement et retour arrière

Une modification de pare-feu doit être traitée comme un changement de production. Avant le changement, recueillez la configuration et les objets concernés, identifiez les dépendances, confirmez le propriétaire métier et préparez un test. Pendant la fenêtre, appliquez la modification de façon contrôlée, vérifiez les journaux et les flux attendus, puis décidez de poursuivre ou de revenir en arrière. Après le changement, mettez à jour la documentation et le ticket.

Une sauvegarde est utile seulement si elle peut être restaurée. Vérifiez la protection des secrets, chiffrez les fichiers sensibles, limitez les droits, documentez les étapes et testez périodiquement la procédure de restauration dans un environnement adapté. Les configurations peuvent contenir des mots de passe, des clés privées, des communautés SNMP ou des détails topologiques : ne les partagez pas sans contrôle.

> **Astuce :** Chaque changement doit posséder quatre éléments avant le déploiement : une justification, un test de succès, un test de non-régression et une condition de retour arrière. Cela transforme un dépannage improvisé en opération reproductible.

---

## 3. Dépannage et sécurité

### 3.1. Méthode de diagnostic structurée

Lorsqu'un flux ne fonctionne pas, commencez par définir précisément l'échec. Notez l'hôte source, l'hôte destination, le protocole, le port, l'heure, le message observé et le périmètre des utilisateurs touchés. « Internet ne marche pas » est trop vague ; « les postes du VLAN 10 résolvent les noms, mais les connexions TCP vers le serveur HTTPS publié échouent depuis un réseau externe » est une description exploitable.

Une bonne séquence de diagnostic comprend :

1. **Reproduire** : utiliser un test simple et reproductible, depuis un hôte défini.
2. **Vérifier l'adressage** : IP, masque, passerelle, DNS et VLAN.
3. **Vérifier le routage** : chemin aller et retour, routes par défaut et éventuelles routes plus spécifiques.
4. **Repérer les points de contrôle** : ACL, NGFW, pare-feu hôte, proxy, NAT, filtrage cloud ou opérateur.
5. **Examiner les journaux** : action, règle, zone, raison de rejet et horodatage.
6. **Comparer les compteurs** : règle censée correspondre, interface d'entrée/sortie, hits avant/après test.
7. **Capturer les paquets** lorsque la visibilité des logs ne suffit pas.
8. **Tester une hypothèse à la fois**, puis confirmer le résultat et documenter la cause.

Évitez de désactiver le pare-feu entier comme première étape. Une coupure de protection peut exposer immédiatement des services et rendre le test difficile à interpréter. Si un test d'isolation est vraiment nécessaire, limitez-le à un laboratoire, un hôte précis, une durée courte et une procédure approuvée.

### 3.2. Symptômes fréquents et causes possibles

| Symptôme | Causes possibles | Vérifications prioritaires |
|---|---|---|
| Connexion TCP expire | Filtrage silencieux, mauvaise route, service injoignable | Table de routage, compteur de règle, capture SYN/SYN-ACK |
| Connexion refusée immédiatement | Service absent, rejet explicite, pare-feu hôte | État du service, logs de refus, capture TCP RST |
| DNS échoue mais l'accès par IP marche | DNS incorrect, règle 53, mauvais résolveur | `nslookup`, configuration DNS, logs vers le résolveur |
| Un seul sens fonctionne | ACL asymétrique, route retour, état de session | Capture sur les deux côtés, table de connexions |
| Après NAT, la réponse n'arrive pas | Traduction incorrecte, retour vers une autre passerelle | Table NAT, route du serveur, adresses avant/après traduction |
| Application lente | Inspection coûteuse, congestion, retransmissions, serveur lent | CPU, latence, compteurs, capture et métriques applicatives |
| Site HTTPS seulement bloqué par inspection | Certificat, pinning, incompatibilité TLS, profil inspection | Logs de déchiffrement, chaîne certificat, test approuvé |
| VPN connecté mais application inaccessible | Pas de route, split tunnel, groupe de règles, DNS, chevauchement IP | Table de routes cliente, logs VPN/NGFW, flux ciblé |
| Fonctionne depuis le LAN mais pas Internet | NAT entrant, DNS public, règle WAN-DMZ, retour | Test externe contrôlé, table NAT et route par défaut serveur |
| Fonctionne jusqu'à un changement d'équipement | Différences de policy, ordre des règles, synchronisation d'état | Comparer configuration, objets et journaux des deux équipements |

Les symptômes n'indiquent pas une cause unique. Un délai d'expiration peut provenir d'un rejet silencieux, mais aussi d'une perte réseau ou d'un serveur surchargé. Une capture de paquets et des journaux corrélés apportent souvent une meilleure preuve qu'un test isolé.

### 3.3. Examiner un refus dans les journaux

Un événement utile devrait permettre d'identifier le moment, la règle, la zone ou l'interface, les adresses source et destination, le protocole/service, l'action et le motif, selon les possibilités du produit. Corrélez l'heure du test avec l'heure des logs et vérifiez la synchronisation NTP. Les fuseaux horaires, les événements retardés ou la collecte asynchrone peuvent compliquer la comparaison.

Si le journal indique une règle « deny », ne créez pas automatiquement une autorisation plus large. Vérifiez d'abord que le trafic est attendu, qu'il vient du bon système et qu'il cible la bonne adresse. Si un logiciel a commencé à contacter une destination inconnue, il peut être préférable d'ouvrir un ticket de sécurité plutôt que de contourner le blocage.

Une politique peut bloquer le flux au niveau du filtre initial, du profil IPS, de la réputation, de l'identification applicative, du filtrage URL ou de l'inspection TLS. Le journal d'accès peut donc dire « autorisé » tandis qu'une inspection ultérieure interrompt la session, ou inversement selon l'architecture. Explorez les journaux des différentes fonctions qui s'appliquent au flux.

### 3.4. Captures de paquets : suivre le flux sans supposer

Une capture peut répondre à des questions précises : le SYN est-il arrivé au pare-feu ? Le pare-feu l'a-t-il transmis ? Le serveur a-t-il répondu ? La réponse est-elle revenue sur le même chemin ? L'adresse a-t-elle été traduite ? Les retransmissions sont-elles nombreuses ? La session échoue-t-elle lors du handshake TLS ?

Pour être utile, la capture doit être réalisée sur des points bien choisis et sur une période pertinente. Une capture sur l'interface externe ne montre pas nécessairement la même adresse que celle de l'interface interne après NAT. Certaines plateformes capturent avant ou après différents traitements. Vérifiez les fonctionnalités et limitations du mécanisme de capture du constructeur.

Les captures peuvent contenir des noms d'hôtes, des adresses, des jetons, voire des données applicatives si le trafic n'est pas chiffré. Protégez les fichiers, limitez la collecte au strict nécessaire et supprimez-les selon la politique applicable. Ne transmettez pas de capture complète à des tiers sans examiner son contenu et les règles de partage.

### 3.5. Ordre de traitement et interaction des politiques

Un NGFW ne se comporte pas toujours comme une unique liste. Il peut combiner classification préliminaire, déchiffrement, NAT, recherche d'objet, règle d'accès, identification applicative, IPS, contrôle de fichiers, suivi d'état et routage. L'ordre exact peut dépendre du constructeur et du mode de déploiement. Les guides de référence du produit doivent être la source de vérité.

Quand une règle semble correcte mais ne fonctionne pas, posez les questions suivantes :

- L'adresse évaluée est-elle l'adresse d'origine ou l'adresse après traduction ?
- La règle est-elle appliquée dans le bon contexte virtuel ou la bonne politique ?
- Une règle antérieure ou une politique de préfiltrage interrompt-elle le flux ?
- L'application est-elle classée comme prévu, ou reste-t-elle inconnue ?
- Un profil IPS, une réputation ou le filtrage URL bloque-t-il la session ?
- La règle a-t-elle été enregistrée puis déployée sur le bon équipement ?
- L'équipement utilise-t-il une session déjà établie qui conserve un ancien état ?

Certaines modifications de politique n'affectent pas immédiatement toutes les sessions existantes. Le mécanisme dépend du produit. Ne videz pas aveuglément toute la table des sessions : cela peut interrompre des connexions critiques. Préférez une action ciblée et autorisée après avoir vérifié la procédure du constructeur.

### 3.6. Règles trop permissives et règle « any-any »

Une autorisation globale entre une zone interne et une zone externe est souvent séduisante parce qu'elle minimise les appels de dépannage. Elle réduit cependant la capacité à contrôler les applications, à comprendre les échanges et à limiter les sorties d'un poste compromis. Une règle « any-any » entre DMZ et LAN est particulièrement risquée, car un serveur exposé peut atteindre un grand nombre de systèmes internes si sa compromission permet d'exécuter du code.

Si une règle permissive est indispensable pour un diagnostic temporaire, elle doit être limitée à un environnement sûr, à une source/destination précise, à un intervalle défini et à un responsable. Le retrait doit être vérifié, pas seulement planifié. Un commentaire « temporaire » sans date de fin est une dette de sécurité.

Les règles de refus explicites peuvent améliorer la lisibilité, même lorsque le moteur applique déjà un refus implicite. Elles doivent toutefois être ordonnées correctement. Un blocage général avant les autorisations nécessaires peut interrompre le service ; une autorisation générale avant un blocage spécifique peut rendre ce dernier inopérant.

### 3.7. Revue périodique et hygiène des règles

Une politique se dégrade au fil des projets. Des serveurs sont remplacés, des adresses changent, des acquisitions ajoutent des réseaux, des accès de prestataires restent ouverts et des règles de dépannage ne sont pas retirées. Une revue périodique permet d'identifier les autorisations sans propriétaire, les objets vides, les doublons, les règles ombrées et les accès excessifs.

Une revue efficace doit croiser plusieurs sources : raison métier, propriétaire de l'application, compteurs de trafic, périodes d'utilisation, inventaire d'actifs, tickets de changements, journaux et exigences réglementaires. Les compteurs seuls ne sont pas suffisants, car une règle peut être utilisée seulement pendant une maintenance trimestrielle ou en cas de secours. Il faut prévoir une consultation du propriétaire plutôt qu'une suppression automatique.

Pour chaque règle, posez les questions suivantes :

- Quel service métier dépend de cette autorisation ?
- Le propriétaire est-il toujours présent et joignable ?
- La source est-elle aussi restreinte que possible ?
- La destination est-elle un hôte ou une zone trop large ?
- Le service est-il défini précisément ?
- La journalisation correspond-elle au risque et au volume ?
- Une durée ou date de révision est-elle requise ?
- Le test de non-régression est-il documenté ?

### 3.8. Haute disponibilité (HA) et synchronisation d'état

Les réseaux critiques utilisent parfois deux pare-feu en haute disponibilité : un actif et un secours, ou une autre architecture prise en charge. Le but est de réduire l'interruption en cas de panne. La HA peut inclure surveillance de liens, synchronisation de configuration, synchronisation de sessions et mécanismes d'élection. Toutes les plateformes ne synchronisent pas les mêmes états ni de la même façon.

La présence de deux appareils ne suffit pas à garantir la continuité. Il faut tester les scénarios de panne : perte d'alimentation, rupture de lien, défaillance d'une interface, perte du réseau de synchronisation, panne du chemin extérieur et mise à niveau logicielle. Une bascule peut interrompre des sessions si la table d'état n'est pas partagée ou si l'équipement secondaire n'a pas le bon état de routage.

La configuration doit être cohérente entre les membres, mais certains paramètres peuvent être spécifiques à chaque nœud. Les changements sont à déployer en respectant les procédures du constructeur. Avant une mise à niveau, vérifiez la compatibilité, la séquence de bascule, la sauvegarde, la durée d'interruption attendue et la procédure de retour arrière.

> **Piège :** Tester seulement que le second pare-feu devient actif ne valide pas la HA. Il faut également mesurer les pertes, confirmer les routes, vérifier les sessions essentielles, tester les règles et examiner les alarmes de synchronisation.

### 3.9. Performance, latence et capacité d'inspection

Le débit annoncé d'un pare-feu peut varier selon les fonctions actives. Le débit de filtrage simple n'est pas nécessairement comparable au débit lorsque l'IPS, la détection de fichiers, le contrôle URL, l'identification applicative et l'inspection TLS sont tous activés. Le nombre de connexions nouvelles par seconde, les sessions simultanées, les paquets par seconde et la taille moyenne des paquets influencent également la capacité.

Pour évaluer une plateforme, utilisez un profil représentatif de la production, et pas seulement un test théorique en laboratoire. Mesurez la latence, le débit, les connexions nouvelles, les sessions simultanées, l'utilisation CPU/mémoire et les pertes. Si la performance baisse après activation d'un profil, comparez les métriques avec la configuration précédente et vérifiez les journaux de saturation ou les changements de classification.

Optimiser ne signifie pas supprimer les fonctions de sécurité sans raison. On peut réduire les inspections inutiles sur des flux strictement identifiés, réviser la journalisation volumineuse, utiliser des profils adaptés, augmenter la capacité ou segmenter les chemins de trafic. Toute exception d'inspection doit être justifiée par le risque et approuvée par les personnes responsables.

### 3.10. Protection du plan de gestion

Le plan de gestion comprend les interfaces, comptes, API, consoles et protocoles employés pour administrer l'équipement. Il doit être séparé autant que possible du trafic utilisateurs. L'accès devrait passer par des sources approuvées, des protocoles chiffrés, une authentification adaptée et des comptes nominatifs lorsque le produit le permet.

Évitez d'exposer SSH, HTTPS d'administration, SNMP de gestion ou une API de configuration directement à Internet. Si un accès externe est impératif, imposez un chemin d'accès contrôlé, restreignez les sources, protégez les identifiants, activez les journaux pertinents et examinez les alertes. Les interfaces de management ne doivent pas être incluses par erreur dans une règle globale d'accès Internet.

Appliquez un contrôle de changement à la politique elle-même. Séparez, lorsque possible, les rôles qui proposent une règle, l'approuvent et la déploient. Les comptes privilégiés doivent être protégés et revus. Les sauvegardes de configuration doivent être conservées en lieu sûr, et les secrets ne doivent pas être copiés dans des tickets ou fichiers partagés sans protection.

### 3.11. Sécurité d'IPv6

Un réseau peut avoir IPv4 et IPv6 en parallèle. Une politique qui ne filtre qu'IPv4 peut laisser passer des connexions IPv6 si l'adressage et le routage IPv6 sont activés. L'inventaire doit donc déterminer si IPv6 est disponible sur les interfaces, postes, tunnels VPN, réseaux Wi-Fi et environnements cloud.

IPv6 possède des mécanismes de contrôle et de découverte qui nécessitent des règles adaptées, notamment ICMPv6 et la découverte des voisins. Une copie directe de la politique IPv4 est incorrecte, car les différences de protocoles et de fonctionnement doivent être prises en compte. La politique IPv6 doit couvrir les flux autorisés, le plan de gestion, le trafic de contrôle nécessaire et les tests de contournement possibles.

Si IPv6 n'est pas utilisé, ne supposez pas qu'il est inactif sans vérifier. La désactivation doit suivre l'architecture et les procédures du système d'exploitation ou de l'équipement. Une désactivation improvisée peut affecter des services ou masquer un besoin réel ; dans tous les cas, la politique de filtrage doit être cohérente avec l'état réel du protocole.

### 3.12. Sécurité des règles VPN, cloud et accès tiers

Les pare-feu locaux ne sont qu'une partie de la politique réseau. Les environnements cloud proposent des groupes de sécurité, des listes de contrôle réseau, des pare-feu gérés et des contrôles d'identité. Les règles peuvent s'appliquer à la carte réseau virtuelle, au sous-réseau, au projet ou à l'environnement géré. Les objets et la sémantique diffèrent des appareils physiques, même si les concepts de sources, destinations et services restent utiles.

Les accès entre sites doivent être limités par sous-réseaux et applications nécessaires. Le fait que deux sites soient reliés par un tunnel IPsec ne signifie pas que tous leurs réseaux doivent communiquer sans restriction. La segmentation doit être maintenue dans le tunnel. Les routes, sélecteurs de trafic, NAT éventuel, DNS et politiques des deux côtés doivent s'aligner.

Pour un prestataire externe, limitez l'accès à la ressource et à la durée nécessaires, utilisez un compte et un groupe identifiables, définissez un responsable interne, journalisez la session et retirez l'accès à la fin. Si plusieurs sociétés partagent le même VPN ou les mêmes plages d'adresses, documentez les risques de chevauchement et les possibilités d'accès croisé.

### 3.13. Réponse à une alerte de sécurité réseau

Lorsqu'une alerte IPS ou NGFW apparaît, ne considérez ni qu'elle prouve une compromission ni qu'elle peut être ignorée comme faux positif. Commencez par conserver le contexte : hôte source, destination, règle, signature, sévérité, horodatage, action du produit et processus métier concerné. Vérifiez si l'action a réellement bloqué le trafic ou seulement produit une alerte.

Comparez la signature avec les éléments disponibles et cherchez des événements corrélés : connexions inhabituelles, DNS suspect, changements de règles, authentifications anormales ou communications répétées. Suivez la procédure interne de réponse à incident, qui peut exiger l'isolement d'un poste, la collecte d'éléments, la préservation des journaux et l'information d'une équipe spécialisée. Ne modifiez pas arbitrairement les preuves et ne supprimez pas les logs pour faire disparaître une alerte.

Si la détection semble être un faux positif, documentez la raison, reproduisez le scénario en environnement contrôlé si possible et envisagez une exception ciblée. Limitez l'exception à la signature, à la source, à la destination et au service nécessaires lorsque le produit le permet. Affectez un responsable et une date de réévaluation. Une exemption large peut neutraliser la détection pour des flux sans rapport.

### 3.14. Cas pratique complet : utilisateur vers application Web

Un utilisateur du VLAN `192.168.10.0/24` signale que l'application Web interne ne fonctionne plus après une modification de pare-feu. L'application est hébergée sur `192.168.30.20` en DMZ et utilise HTTPS. Le DNS interne pointe correctement vers le nom de l'application.

**Étape 1 — Formuler l'hypothèse.** Le nom résout vers la bonne adresse, mais le service peut être bloqué par l'ACL, la politique interzone, le serveur ou l'inspection TLS. Il faut éviter de changer plusieurs composants avant de disposer d'une observation.

**Étape 2 — Tester la résolution.** Utilisez `nslookup nom-interne` ou l'outil DNS disponible, et vérifiez le résolveur interrogé. Si le résultat est incorrect, recherchez un problème DNS avant de modifier le filtrage HTTPS.

**Étape 3 — Tester le port.** Depuis le poste autorisé, un outil adapté peut tester la connexion TCP vers le port 443. La réussite du handshake TCP ne garantit pas que l'application ou le certificat fonctionne, mais l'échec peut orienter vers le chemin réseau, un filtre ou un service arrêté.

**Étape 4 — Consulter la politique.** Vérifiez la règle de l'INSIDE vers la DMZ : les objets source et destination correspondent-ils ? TCP 443 est-il autorisé ? Une règle antérieure ne correspond-elle pas à un blocage ? Les changements ont-ils été déployés ?

**Étape 5 — Contrôler l'état et le routage.** Recherchez l'événement de la session et, si nécessaire, capturez le SYN côté entrée et la transmission côté sortie. Si le serveur répond mais que la réponse ne revient pas au poste, inspectez la route de retour et les autres points de contrôle.

**Étape 6 — Vérifier le service.** Confirmez que le serveur Web écoute sur 443, que son certificat est valide et que son pare-feu hôte autorise l'accès depuis le sous-réseau source.

**Étape 7 — Vérifier les fonctions avancées.** Si TCP se connecte mais que le navigateur reçoit une erreur, consultez les logs de déchiffrement TLS, IPS, filtrage URL et classification applicative. Une politique peut autoriser le transport mais interrompre plus tard le contenu.

**Étape 8 — Corriger et tester.** Si une règle manque, ajoutez une autorisation précise approuvée et avant la règle générale appropriée. Retestez depuis le VLAN concerné, vérifiez que l'accès non prévu reste bloqué, puis documentez le changement.

Ce scénario montre que « pare-feu » désigne plusieurs points de contrôle possibles. Il faut identifier le mécanisme exact qui interrompt le flux plutôt que de désactiver la sécurité en bloc.

### 3.15. Exercices de révision

**Exercice 1 — Ordre de règles.** Une ACL contient `permit ip 192.168.10.0 0.0.0.255 any` avant `deny tcp 192.168.10.0 0.0.0.255 any eq 22`. Pourquoi SSH n'est-il pas bloqué comme prévu ? Réécrivez l'ordre des règles et expliquez pourquoi une autorisation large peut être difficile à auditer.

**Exercice 2 — Flux retour.** Un poste ouvre une session HTTPS vers Internet. Le pare-feu stateful permet la connexion initiale et les paquets de réponse. Pourquoi cette politique ne doit-elle pas être confondue avec « tout trafic entrant est autorisé » ? Expliquez la différence entre une nouvelle connexion et la réponse d'une session existante.

**Exercice 3 — Publication Web.** Un serveur de DMZ est accessible depuis le LAN mais pas depuis Internet. Citez au moins cinq éléments à vérifier sans désactiver le pare-feu : DNS public, NAT, règle d'accès, route retour, service local, certificat et journaux, par exemple.

**Exercice 4 — Compteurs.** Une règle de refus ne compte aucun paquet pendant votre test. Donnez quatre explications possibles : mauvaise interface/sens, mauvaise adresse, règle précédente qui capture le paquet, test qui n'a pas généré le flux ou filtrage sur un autre équipement.

**Exercice 5 — NGFW.** Un flux TCP 443 est autorisé mais une application échoue après l'établissement TCP. Quels profils ou mécanismes autres que l'ACL classique faut-il examiner ?

**Exercice 6 — Segmentation.** Proposez une matrice de trois règles pour autoriser un serveur Web en DMZ à accéder à une base de données tout en empêchant le serveur de DMZ de joindre les postes utilisateurs.

**Exercice 7 — IPv6.** Pourquoi ne suffit-il pas de valider la seule ACL IPv4 ? Décrivez deux vérifications permettant de déterminer si IPv6 peut transporter du trafic dans l'environnement.

**Exercice 8 — Exploitation.** Une règle « temporaire » n'a plus de propriétaire et n'a pas été utilisée depuis deux mois. Peut-on la supprimer immédiatement ? Quels éléments et quels propriétaires faut-il consulter avant la décision ?

### 3.16. Corrigé indicatif des exercices

**Exercice 1 :** La première règle autorise tout trafic IP de la source concernée et la seconde n'est donc pas atteinte. Placer le refus précis avant les autorisations plus larges corrige l'ordre, mais une politique de moindre privilège préférera une liste d'autorisations explicites adaptée au besoin réel.

**Exercice 2 :** Le suivi d'état associe la réponse à une session initiée et autorisée ; il ne crée pas une autorisation générale pour des connexions nouvelles venant d'Internet. L'implémentation exacte dépend du pare-feu et du protocole.

**Exercice 3 :** Vérifier la résolution publique, l'adresse NAT, la règle WAN-DMZ, l'ordre des règles, la route et la passerelle du serveur, le service TCP 443, le pare-feu hôte, le certificat, ainsi que les journaux du filtre et des profils d'inspection.

**Exercice 4 :** La règle peut être placée sur le mauvais point, le test peut cibler une autre adresse, une règle antérieure peut prendre la décision, le flux peut ne pas être généré, l'équipement peut utiliser une politique différente ou la règle peut ne pas avoir été déployée.

**Exercice 5 :** Examiner l'identification applicative, l'IPS, le filtrage URL, la réputation, l'inspection de fichiers, le déchiffrement TLS et les logs de sessions. L'établissement TCP n'assure pas la réussite du protocole applicatif.

**Exercice 6 :** Autoriser l'hôte Web vers l'hôte base uniquement sur le port applicatif requis ; refuser DMZ vers le réseau utilisateurs ; n'autoriser les flux d'administration vers le serveur que depuis une station ou un bastion approuvé. Le réseau de base de données doit également limiter les sources, idéalement indépendamment.

**Exercice 7 :** IPv6 peut être actif avec sa propre adresse, sa route et sa politique. Contrôler les paramètres des interfaces et des postes, les routes IPv6 et les règles IPv6 sur les équipements de sécurité.

**Exercice 8 :** Pas sans analyse. Consulter le propriétaire applicatif, les périodes d'activité, les journaux, les sauvegardes, le plan de continuité et les tickets. Une règle sans compteur peut être utilisée rarement ou dans un scénario de secours. En cas d'inutilité confirmée, supprimer selon la procédure, tester et documenter.

---

## Points à retenir

- Un pare-feu est un point de contrôle de trafic ; le routage, le NAT, l'état de connexion et l'inspection applicative sont des mécanismes distincts qui doivent être coordonnés.
- Une ACL ordonnée évalue les entrées selon la logique de première correspondance. Les refus spécifiques doivent se trouver avant les autorisations plus larges qui les neutraliseraient.
- Les ACL standard et étendues ne possèdent pas les mêmes critères. Sur Cisco IOS, l'ACL étendue peut contrôler source, destination, protocole et ports ; son application à une interface et à un sens précis est indispensable.
- Un pare-feu stateful maintient un contexte de session et peut permettre le retour des connexions autorisées. Cela ne signifie pas que toute connexion entrante est acceptable.
- Les zones INSIDE, OUTSIDE, DMZ et MANAGEMENT doivent représenter des besoins et niveaux de confiance compréhensibles. Une DMZ n'est utile que si les chemins vers les réseaux internes sont limités.
- NAT ne constitue pas en lui-même une autorisation. Il faut vérifier la route, la traduction, la politique de filtrage et le chemin de retour.
- Les fonctions NGFW — identité applicative, IPS, réputation, contrôle Web, inspection de fichiers et déchiffrement TLS — varient selon le produit et demandent des tests, des mises à jour et une gestion des faux positifs.
- Une matrice de flux préalable, une convention d'objets, une justification et une date de révision facilitent la maintenance de la politique.
- Les journaux sont plus utiles lorsqu'ils sont pertinents, horodatés, centralisés et corrélés aux tests ; une journalisation excessive peut créer du bruit et une charge inutile.
- En dépannage, reproduire le flux, vérifier l'adressage, les routes, les règles, NAT, le serveur et l'inspection avancée avant de changer la politique.
- Les règles temporaires, les accès de prestataires, les tunnels VPN et les flux de gestion doivent être révisés et retirés lorsqu'ils ne sont plus nécessaires.
- La haute disponibilité doit être testée du point de vue des applications, des sessions et du routage, pas uniquement en observant la bascule d'un appareil à l'autre.
- La sécurité IPv6, le pare-feu hôte et les contrôles cloud font partie de la politique globale ; une ACL IPv4 seule ne suffit pas dans un environnement dual-stack.

### Références techniques

1. NIST, *Guidelines on Firewalls and Firewall Policy*, Special Publication 800-41 Rev. 1, septembre 2009. Présente les types de pare-feu, la sélection, la configuration, les tests et la gestion des politiques. https://doi.org/10.6028/NIST.SP.800-41r1
2. Cisco, *Security and VPN Configuration Guide, Cisco IOS XE 17.x — Zone-Based Policy Firewalls*. Référence sur les zones, les classes de trafic, les policy maps et les paires de zones. https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/sec-vpn/b-security-vpn/m_sec-zone-pol-fw-xe.html
3. Cisco Secure Firewall, *Access Control Policy*. Documentation de référence sur les règles d'accès, les zones, les applications et l'articulation avec NAT et les fonctions d'inspection. https://secure.cisco.com/secure-firewall/docs/access-control-policy
4. Cisco Secure Firewall 1210/20, *Configure a Basic Policy*. Exemple de procédure de configuration initiale, interfaces, routage par défaut, PAT et politique d'accès ; les étapes sont spécifiques à la plateforme décrite. https://www.cisco.com/c/en/us/td/docs/security/secure-firewall/getting-started/1210-20/fmc-remote/csf-1210-20-ftd-get-start-fmc-remote/configure-a-basic-policy-intro.html
5. Cisco, documentation de configuration ACL IPv4 pour la version IOS/IOS XE utilisée. Consultez la documentation correspondant exactement à votre modèle et à votre image logicielle avant d'appliquer des commandes.

> **Astuce :** Avant chaque changement, résumez en une phrase ce que la règle doit permettre, puis vérifiez à la fois un test positif (le flux attendu fonctionne) et un test négatif (un flux similaire mais non autorisé reste bloqué). Une politique sûre est une politique dont le fonctionnement peut être expliqué, prouvé et maintenu.
