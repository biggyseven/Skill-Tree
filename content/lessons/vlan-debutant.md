---
node_id: vpn-debutant
title: VPN & tunnels - Débutant
---

# VPN & tunnels - Débutant

**Niveau :** DÉBUTANT

Un réseau privé virtuel, ou VPN (*Virtual Private Network*), permet de relier des appareils ou des réseaux à travers une infrastructure qui n'est pas entièrement maîtrisée, par exemple Internet, tout en apportant des mécanismes de protection et de contrôle. Le terme recouvre plusieurs technologies : certaines chiffrent le trafic, d'autres créent surtout un chemin logique entre deux points, et beaucoup associent plusieurs mécanismes. Il est donc important de ne pas confondre un tunnel avec le chiffrement lui-même.

Dans un réseau d'entreprise, un VPN peut relier deux agences, permettre à un employé de travailler à distance, donner à un technicien un accès limité à un environnement d'administration ou transporter des réseaux virtuels dans une infrastructure existante. Un tunnel peut également servir à transporter un protocole qui n'est pas pris en charge directement par le réseau sous-jacent. Les technologies disponibles ont des objectifs différents et ne sont pas automatiquement interchangeables.

Ce cours présente les notions nécessaires pour comprendre les VPN avant de passer à des déploiements avancés. Il explique les adresses internes et externes, l'encapsulation, le chiffrement, l'authentification, les grandes familles de tunnels, les paramètres essentiels, ainsi que les causes fréquentes de panne. Des exemples Cisco IOS illustrent les principes de configuration, mais leur syntaxe peut varier selon le modèle, l'image logicielle, la licence et la version. Les commandes doivent toujours être validées sur l'équipement utilisé.

L'objectif n'est pas de mémoriser une suite de commandes sans comprendre leur rôle. À la fin du cours, l'apprenant doit pouvoir représenter un VPN avec un schéma, distinguer les principaux types de VPN, expliquer le trajet d'un paquet, reconnaître les paramètres qui doivent correspondre entre deux extrémités, effectuer les contrôles de base et appliquer une démarche de dépannage structurée.

> **Analogie** : Imaginez deux bâtiments séparés par une route publique. Un tunnel routier privé représente le chemin logique entre les bâtiments ; une enveloppe verrouillée représente le chiffrement ; un badge représente l'authentification. Le tunnel, le verrou et le badge sont trois fonctions différentes, même si un VPN les utilise souvent ensemble.

---

## 1. La théorie et les algorithmes

### 1.1. Comprendre le besoin d'un VPN

Un réseau local permet à des appareils proches, ou reliés par une infrastructure contrôlée, de communiquer selon des règles communes. Dès que la communication passe par Internet ou par un réseau opérateur dont on ne contrôle pas tous les équipements, plusieurs questions se posent : qui peut lire les données, qui peut les modifier, comment reconnaître le correspondant légitime et comment empêcher un utilisateur non autorisé d'atteindre un sous-réseau interne ? Un VPN aide à répondre à ces questions, mais seulement s'il est conçu et administré correctement.

Un VPN ne rend pas automatiquement un appareil anonyme, invisible ou invulnérable. Le serveur VPN connaît au minimum certaines métadonnées de la connexion ; les sites consultés peuvent toujours identifier un utilisateur par son compte, ses cookies ou son empreinte numérique ; et un poste déjà infecté peut envoyer des informations à travers un tunnel pourtant chiffré. Un VPN protège principalement un chemin réseau et les flux couverts par sa politique. Il ne remplace ni la mise à jour des systèmes, ni l'authentification multifacteur, ni la gestion des droits, ni les sauvegardes.

Les organisations déploient souvent des VPN pour trois besoins principaux. Le premier est l'interconnexion de sites, appelée *site-to-site*. Le deuxième est l'accès distant d'un utilisateur ou d'un appareil, appelé *remote access*. Le troisième est le transport logique de paquets ou de réseaux au sein d'une infrastructure, par exemple avec GRE ou d'autres mécanismes de tunneling. Certaines solutions combinent ces besoins ou ajoutent une inspection des applications, une authentification de l'utilisateur et des politiques de sécurité centralisées.

### 1.2. Vocabulaire essentiel

| Terme | Définition simple | Exemple |
|---|---|---|
| VPN | Connexion logique protégée ou administrée entre des points | Un employé accède au réseau de son entreprise |
| Tunnel | Mécanisme d'encapsulation qui transporte un paquet dans un autre | Un paquet IP est transporté dans un paquet GRE |
| Extrémité du tunnel | Appareil qui encapsule ou décapsule le trafic | Un routeur de chaque agence |
| Pair (*peer*) | Autre extrémité reconnue par la configuration | Le routeur distant d'un VPN IPsec |
| Encapsulation | Ajout d'un en-tête ou d'une enveloppe autour des données | Paquet IP placé dans un paquet IPsec/GRE |
| Chiffrement | Transformation visant à rendre le contenu illisible sans la clé | AES-GCM avec des clés négociées |
| Intégrité | Détection de modifications des données protégées | Un paquet modifié est rejeté |
| Authentification | Vérification de l'identité d'un utilisateur ou d'un équipement | Certificat ou secret partagé |
| Route | Indication du prochain saut utilisé pour atteindre une destination | Route vers le sous-réseau du siège via le VPN |
| Sélecteur de trafic | Critère indiquant quel trafic peut être protégé | Réseau source et réseau de destination |
| Passerelle VPN | Équipement qui termine un tunnel pour un réseau | Pare-feu ou routeur de l'agence |

Le mot « privé » ne signifie pas nécessairement qu'un câble physique est réservé à l'organisation. Un VPN s'appuie souvent sur un réseau public ou partagé, et ajoute une séparation logique, des mécanismes de sécurité ou les deux. La confidentialité dépend des paramètres réellement négociés ; elle ne doit pas être déduite du seul fait qu'une interface s'appelle `Tunnel0` ou qu'un utilisateur clique sur « Connecter ».

### 1.3. Comment fonctionne un tunnel ?

Sans tunnel, un ordinateur de l'agence A envoie un paquet IP vers la destination qu'il souhaite joindre. Le réseau intermédiaire achemine ce paquet selon son adresse de destination. Avec un tunnel, l'extrémité d'entrée prend le paquet original et l'encapsule dans une structure extérieure. Le réseau de transport achemine l'enveloppe extérieure jusqu'à l'extrémité de sortie, qui la retire et récupère le paquet original. Ce dernier peut ensuite être routé vers le destinataire final.

Le paquet transporté est parfois appelé paquet interne (*inner packet*) ; l'enveloppe utilisée pour traverser le réseau est le paquet externe (*outer packet*). Le paquet externe contient généralement les adresses des extrémités du tunnel. Le paquet interne conserve les adresses qui identifient les hôtes ou sous-réseaux qui communiquent. En tunnel IPsec, l'en-tête externe sert à faire parvenir les données au pair VPN, tandis que le paquet interne est protégé par ESP lorsque le chiffrement et l'intégrité sont négociés.

```text
PC agence A             Internet / réseau de transport           PC agence B
10.10.10.10                                                       10.20.20.20
     |                                                                  ^
     | paquet interne : source 10.10.10.10, destination 10.20.20.20     |
     v                                                                  |
[Passerelle A] === paquet externe protégé ====> [Passerelle B] ----------
     |                 adresses des pairs                 |
     |                                                   décapsulation
     +-- encapsulation et protection                     +--> réseau B
```

Le dessin est conceptuel : le paquet peut traverser plusieurs routeurs, pare-feu et opérateurs entre les deux passerelles. Ces intermédiaires n'ont généralement pas besoin de connaître les adresses internes si celles-ci sont protégées dans la partie encapsulée. Ils doivent cependant pouvoir acheminer l'adresse externe de la passerelle distante et laisser passer les protocoles et ports nécessaires.

> **Piège :** Un tunnel qui monte n'implique pas que tout le trafic passe dedans. Le tunnel peut exister alors qu'une route manque, qu'une ACL bloque les paquets, que les sous-réseaux ne sont pas inclus dans la politique VPN ou que le retour prend un chemin différent.

### 1.4. Encapsulation et chiffrement : deux fonctions distinctes

Un mécanisme de tunneling ajoute une enveloppe ou un en-tête pour transporter un paquet à travers un autre réseau. L'encapsulation, à elle seule, ne rend pas le contenu secret. GRE, par exemple, peut transporter des paquets IPv4 ou IPv6 et fournir un lien logique, mais il ne chiffre pas le contenu par défaut. Une personne capable d'observer le trafic GRE peut, en l'absence d'une protection supplémentaire, être en mesure de lire les paquets transportés.

Le chiffrement transforme le contenu protégé en données qui ne peuvent pas être comprises sans la clé appropriée. Un VPN IPsec utilisant ESP peut fournir confidentialité, intégrité et protection contre certaines répétitions de paquets, selon les suites cryptographiques et les options négociées. D'autres VPN s'appuient sur TLS ou sur une conception cryptographique propre, telle que celle de WireGuard. Dans tous les cas, la sécurité dépend de la version utilisée, des paramètres autorisés, de l'authentification et de la qualité de la mise en œuvre.

Il est donc possible d'avoir :

- un tunnel sans chiffrement, tel qu'un tunnel GRE seul ;
- un protocole de protection appliqué directement à des paquets IP, tel qu'IPsec en mode transport ;
- un tunnel sécurisé qui encapsule des paquets internes, tel qu'IPsec en mode tunnel ;
- un tunnel logique associé à une protection séparée, par exemple GRE transporté à travers IPsec.

La bonne question n'est pas uniquement « existe-t-il un tunnel ? », mais « quels paquets sont transportés, lesquels sont protégés, par quel mécanisme, entre quelles identités et sous quelle politique ? ».

### 1.5. Les objectifs de sécurité d'un VPN

**Confidentialité.** Un observateur qui capture les paquets ne doit pas pouvoir lire leur contenu lorsqu'ils sont couverts par un chiffrement approprié. La confidentialité dépend de l'algorithme, de la gestion des clés, de la validation de l'identité distante et de la manière dont le trafic est sélectionné. Un tunnel mal configuré peut laisser des flux sortir hors VPN.

**Intégrité.** Le destinataire doit pouvoir détecter une modification non autorisée des données protégées. Les protocoles modernes combinent souvent chiffrement et authentification dans une construction AEAD, par exemple AES-GCM ou ChaCha20-Poly1305, selon le protocole et l'implémentation. La présence d'un chiffrement ancien sans protection d'intégrité ne constitue pas un choix acceptable pour une nouvelle conception.

**Authentification.** Chaque extrémité doit s'assurer qu'elle communique avec le bon pair. Un secret partagé, un certificat ou une clé publique peut servir à authentifier une passerelle ou un client. La seule connaissance d'une adresse IP publique n'est pas une preuve d'identité suffisante.

**Anti-rejeu.** Certains protocoles empêchent un attaquant de réinjecter facilement un ancien paquet valide. Des numéros de séquence et des fenêtres de réception peuvent contribuer à cette protection. Le traitement exact varie selon le protocole et sa configuration.

**Contrôle d'accès.** Le VPN doit limiter les ressources qu'un utilisateur ou un site peut joindre. L'établissement d'un tunnel ne devrait pas automatiquement donner accès à tous les réseaux internes. Les autorisations doivent suivre le principe du moindre privilège.

**Disponibilité.** Une coupure Internet, une panne de passerelle, une attaque par déni de service, une mauvaise configuration ou l'expiration d'un certificat peuvent empêcher le fonctionnement du service. Un VPN améliore certaines propriétés de sécurité, mais il ajoute aussi des composants à superviser.

> **Astuce :** Lors d'une revue de conception, examine séparément cinq questions : le pair est-il authentifié ? Le contenu est-il chiffré ? Les modifications sont-elles détectées ? Le trafic autorisé est-il limité ? La panne est-elle détectée et traitée ?

### 1.6. Les principaux types de VPN

#### VPN site-to-site

Un VPN site-to-site relie des réseaux entiers à travers deux passerelles. Les postes des utilisateurs n'ont généralement pas besoin d'installer un client VPN. Ils envoient leur trafic à leur routeur local comme d'habitude ; le routeur reconnaît les destinations distantes et protège le trafic correspondant. Ce modèle est adapté à deux agences, à un siège et une filiale, ou à un réseau local et un environnement hébergé dans le cloud.

Le VPN site-to-site simplifie l'administration de nombreux postes, mais il demande une planification claire des sous-réseaux, des routes, du pare-feu et de la redondance. Si deux sites utilisent le même sous-réseau, par exemple `192.168.1.0/24`, la décision de routage peut devenir ambiguë. Des adresses non chevauchantes sont préférables ; la traduction d'adresses pour résoudre un chevauchement est possible dans certains scénarios, mais ajoute de la complexité.

#### VPN d'accès distant

Un VPN d'accès distant permet à un utilisateur ou à un appareil de se connecter depuis l'extérieur. Le client établit un tunnel vers une passerelle d'entreprise, s'authentifie, puis reçoit des paramètres, par exemple une adresse virtuelle, des routes et des serveurs DNS. La politique détermine si l'appareil peut accéder uniquement à une application ou à plusieurs sous-réseaux internes.

Le fait qu'un utilisateur soit connecté au VPN ne doit pas être considéré comme une garantie que son appareil est sain. Les solutions d'entreprise peuvent combiner le VPN avec l'authentification multifacteur, une vérification de conformité du poste, une gestion des certificats et des règles d'accès adaptées au rôle. Les droits d'un sous-traitant ne devraient pas nécessairement être les mêmes que ceux d'un administrateur réseau.

#### VPN personnel ou commercial

Les services VPN commerciaux acheminent généralement le trafic du client vers un serveur du fournisseur. Le site final voit souvent l'adresse IP de sortie du fournisseur plutôt que l'adresse publique d'origine du client. Cela peut protéger le trafic sur certains réseaux d'accès et modifier l'adresse IP apparente, mais le fournisseur devient un intermédiaire de confiance. Il faut comprendre sa politique de confidentialité, ses méthodes de journalisation et les limites de son service.

Un VPN personnel n'est pas identique au VPN d'entreprise. Un VPN d'entreprise vise surtout à relier un utilisateur ou un site aux ressources autorisées de l'organisation. Un VPN commercial ne donne pas automatiquement accès à un réseau professionnel. Le choix dépend de l'objectif et du modèle de confiance.

#### Tunnel de transport

Un tunnel de transport est souvent utilisé pour porter des protocoles ou créer une topologie logique. GRE est un exemple fréquent dans les environnements de routage. Comme GRE ne fournit pas de chiffrement par défaut, il est couramment combiné avec IPsec lorsqu'il faut protéger le trafic. D'autres mécanismes d'encapsulation existent selon la technologie, le fournisseur et l'architecture.

### 1.7. IPsec : la famille de protocoles la plus courante en entreprise

IPsec apporte des services de sécurité au niveau IP. Ce n'est pas un unique algorithme, mais une architecture qui associe des protocoles, des associations de sécurité, des sélecteurs de trafic, des algorithmes et une gestion des clés. Les équipements se mettent d'accord sur les paramètres nécessaires avant de protéger les données. La politique peut indiquer quels flux doivent être protégés, rejetés ou autorisés sans IPsec.

**ESP (*Encapsulating Security Payload*)** est le protocole de protection couramment utilisé avec IPsec. Selon les paramètres négociés, ESP peut fournir le chiffrement, l'intégrité, l'authentification de l'origine des données et l'anti-rejeu. Pour la plupart des nouveaux déploiements de VPN, ESP est plus habituel qu'AH.

**AH (*Authentication Header*)** fournit des services d'intégrité et d'authentification, mais ne chiffre pas les données. Il est peu utilisé dans les déploiements actuels, notamment parce que certains changements d'en-têtes par des équipements intermédiaires et le NAT compliquent son fonctionnement. Il ne faut pas le choisir par réflexe simplement parce que son nom contient le mot « Authentication ».

**IKE (*Internet Key Exchange*)** négocie les paramètres de sécurité et contribue à l'authentification des pairs ainsi qu'à l'établissement et au renouvellement des clés. IKEv2 est défini par la RFC 7296. Il est important de distinguer les échanges de contrôle IKE du trafic utilisateur transporté par ESP : le tunnel peut échouer au stade de la négociation, ou être établi alors que le trafic de données ne fonctionne pas.

#### Mode transport et mode tunnel

En mode transport, la protection porte principalement sur le contenu transporté par le paquet IP original, et l'en-tête IP externe reste celui des extrémités qui communiquent. Ce mode est souvent employé pour une protection hôte-à-hôte, même si des architectures plus spécifiques existent.

En mode tunnel, le paquet IP original est transporté à l'intérieur d'un nouvel en-tête IP. L'en-tête externe identifie les extrémités IPsec ; le paquet interne identifie les hôtes ou réseaux qui communiquent. Le mode tunnel est particulièrement adapté à l'interconnexion de passerelles réseau.

```text
Mode transport (schéma simplifié)
[IP original][ESP][données protégées]

Mode tunnel (schéma simplifié)
[IP externe][ESP][IP interne][données protégées]
```

Ce schéma simplifie les détails de format réels. Les champs exacts et leur ordre dépendent du protocole, des options cryptographiques et de l'encapsulation utilisée.

### 1.8. Négociation : ce que les deux extrémités doivent accepter

Les deux pairs doivent trouver un ensemble commun de paramètres compatibles et conformes à la politique de sécurité. Ces paramètres peuvent inclure la méthode d'authentification, les algorithmes de chiffrement et d'intégrité, les groupes Diffie-Hellman, les durées de vie, les identités, les réseaux ou ports protégés et les options de détection de pair. Une seule divergence peut empêcher la négociation.

Le vocabulaire des équipements peut différer. Certains produits affichent une « phase 1 » et une « phase 2 », tandis que d'autres présentent une SA IKE et une ou plusieurs SA de données. Les concepts restent proches, mais les noms de menus et commandes ne sont pas identiques partout. Il faut donc comparer les paramètres fonctionnels plutôt que d'espérer retrouver exactement le même écran chez tous les fabricants.

Les durées de vie indiquent notamment quand renouveler une association de sécurité ou les clés. Elles ne signifient pas nécessairement que le tunnel doit tomber à intervalles fixes : de nombreux équipements renégocient les clés avant l'expiration pour maintenir le service. Les mécanismes de détection d'un pair injoignable, les keepalives et les politiques de reconnexion varient selon les solutions.

Pour un nouvel environnement, il faut privilégier les algorithmes modernes approuvés par l'organisation et supportés des deux côtés, désactiver les suites obsolètes et utiliser IKEv2 lorsqu'il est disponible et adapté. Un paramétrage historique trouvé sur Internet n'est pas automatiquement sûr ou compatible avec les exigences d'aujourd'hui.

### 1.9. Authentification : secret partagé, certificats et identités

Un secret partagé, souvent appelé *pre-shared key* ou PSK, est une valeur configurée aux deux extrémités. Il est simple pour un petit laboratoire ou quelques passerelles, mais sa gestion devient difficile lorsque le nombre de pairs augmente. Un secret faible ou réutilisé sur trop d'équipements peut compromettre plusieurs connexions. Il ne doit pas être envoyé dans un ticket public, un dépôt de code ou un fichier de configuration accessible à tous.

Les certificats utilisent une infrastructure de clés publiques. Chaque équipement présente un certificat lié à une identité, et l'autre extrémité vérifie que ce certificat est valide et digne de confiance selon la politique. Une gestion par certificats peut simplifier la mise à l'échelle et la révocation, mais demande une infrastructure de confiance, la protection des clés privées, la surveillance des dates d'expiration et une procédure de renouvellement.

L'identité n'est pas toujours exactement la même chose que l'adresse IP du pair. Un équipement peut être connu par un nom, une identité de certificat ou un identifiant IKE. Si un changement d'adresse publique intervient, une configuration trop rigide peut échouer alors que l'équipement distant reste légitime. Il faut choisir le modèle d'identité en fonction du scénario et du produit.

L'authentification du pair VPN ne doit pas être confondue avec l'autorisation de chaque utilisateur. Un routeur peut être authentifié comme passerelle d'une agence, tandis que les règles de pare-feu déterminent les serveurs et ports que les utilisateurs de cette agence peuvent joindre. En accès distant, il peut aussi exister une identité utilisateur distincte et un contrôle multifacteur.

### 1.10. GRE, IP-in-IP et autres tunnels

**GRE (*Generic Routing Encapsulation*)** est un mécanisme d'encapsulation qui peut transporter certains paquets dans un paquet extérieur. Il est utilisé dans des scénarios de routage, pour des maquettes ou pour transporter certains types de trafic à travers un réseau IP. GRE ne chiffre pas automatiquement les données et ne remplace donc pas IPsec lorsqu'une confidentialité est requise.

**IP-in-IP** encapsule un paquet IP dans un autre paquet IP selon un format plus simple que GRE. Comme les autres mécanismes de tunneling sans protection intégrée, il doit être évalué selon le besoin de sécurité. La disponibilité du mécanisme et les détails de configuration dépendent des systèmes employés.

**L2TP** transporte des trames de couche 2, mais L2TP seul ne chiffre pas nécessairement le trafic. Il a souvent été combiné à IPsec pour protéger le transport. La présence du mot « VPN » dans le nom d'un ancien client ne garantit pas que la solution utilise des mécanismes modernes.

**PPTP** est un protocole ancien dont les mécanismes de sécurité sont considérés comme insuffisants pour de nouveaux déploiements. Il ne doit pas être choisi pour protéger des données sensibles dans une nouvelle installation. La bonne démarche consiste à migrer vers une solution actuelle supportée par l'organisation.

**TLS VPN** désigne couramment des solutions d'accès distant qui utilisent TLS pour établir une connexion protégée. Les implémentations diffèrent : certaines fournissent un accès par portail à des applications précises, d'autres créent une interface réseau qui transporte davantage de trafic. TLS est également utilisé dans d'autres contextes, par exemple pour les sites Web ; il ne faut donc pas supposer que toutes les connexions TLS sont des VPN.

**WireGuard** est une technologie VPN moderne qui repose sur un ensemble défini de primitives cryptographiques et une configuration souvent concise. Elle utilise des clés publiques comme identités de pairs et s'appuie sur une liste d'adresses autorisées pour associer les destinations à un pair. Son comportement exact, ses options d'intégration et son modèle d'administration doivent être compris avant déploiement, notamment en présence de routage dynamique, de NAT ou d'environnements multi-utilisateurs.

### 1.11. Adresses et routage : pourquoi le VPN peut se connecter sans transporter le trafic

Un tunnel ne remplace pas automatiquement le routage. Supposons que le site A utilise `10.10.10.0/24` et le site B `10.20.20.0/24`. Pour qu'un poste de A atteigne un serveur de B, son paquet doit d'abord être envoyé à la passerelle locale. Cette passerelle doit ensuite décider que le trafic vers `10.20.20.0/24` doit être protégé ou transféré dans le tunnel. La passerelle de B doit décapsuler le trafic et pouvoir le router vers son réseau local. Enfin, le retour doit aussi disposer d'un chemin valide.

Deux grandes approches sont courantes. Dans un VPN à politique, l'équipement sélectionne le trafic à protéger en fonction de critères comme les réseaux source et destination. Dans une architecture à interface de tunnel, une interface logique reçoit le trafic comme une interface de routage ordinaire, et les routes déterminent les destinations qui passent par elle. Certaines plateformes prennent en charge les deux approches, d'autres imposent des contraintes précises.

Il faut aussi distinguer la route vers le réseau distant de la route vers l'adresse publique du pair. Si une route par défaut est redirigée dans le VPN sans exception pour l'adresse externe du serveur, la connexion peut tenter d'envoyer son propre trafic de transport dans le tunnel. Ce problème de récursion ou de chemin de sortie peut interrompre le VPN. Les solutions varient : route plus spécifique vers le pair via la passerelle Internet, règles de séparation de routes, ou mécanismes conçus par le produit.

Les réseaux source et destination doivent être cohérents avec les sélecteurs IPsec ou les adresses autorisées du système. Si la politique protège `10.10.10.0/24` vers `10.20.20.0/24`, mais que le poste utilise réellement `10.10.30.25`, le trafic peut être exclu. Il faut regarder les adresses réelles des interfaces, les masques, les routes et les règles NAT au lieu de supposer que le nom du site suffit.

### 1.12. NAT et traversée NAT

Le NAT traduit certaines adresses IP, parfois aussi les ports TCP ou UDP. Les réseaux domestiques utilisent couramment le NAT pour permettre à plusieurs appareils de partager une adresse publique. IPsec et NAT doivent être compatibles, car certaines parties des paquets et des contrôles cryptographiques sont sensibles aux modifications en transit. IKEv2 peut détecter la présence d'un NAT et utiliser une encapsulation UDP adaptée.

Avec IPsec NAT Traversal, le trafic IKE utilise généralement UDP 500 au début de la négociation, puis peut basculer sur UDP 4500 si la traversée NAT est utilisée. Les paquets ESP sont alors transportés dans UDP, ce qui permet aux équipements NAT de créer des associations de ports. Le comportement réel peut varier : certains produits utilisent UDP 4500 par défaut, même lorsqu'aucun NAT n'est détecté.

Il faut donc vérifier le chemin complet : pare-feu du site local, routeur ou box d'accès, NAT éventuel, pare-feu du site distant et passerelle VPN. Laisser passer UDP 500 uniquement peut permettre une partie de la négociation mais bloquer la communication de données dans un scénario qui nécessite UDP 4500. ESP natif, le protocole IP numéro 50, peut être nécessaire dans certains cas sans NAT-T, selon l'implémentation ; ce n'est pas un port TCP ou UDP.

Une traduction NAT qui modifie le réseau source des paquets peut aussi empêcher les sélecteurs IPsec de correspondre. Certains déploiements font volontairement du NAT avant ou après IPsec ; cela doit être conçu explicitement. Pour apprendre, éviter le NAT à l'intérieur des flux VPN est souvent plus simple, à condition que les sous-réseaux et l'architecture le permettent.

> **Piège :** ESP n'est pas « le port 50 ». ESP est un protocole IP identifié par le numéro 50. UDP 500 et UDP 4500 sont des ports utilisés pour IKE et l'encapsulation NAT-T. Cette distinction est essentielle lors de la création de règles de pare-feu.

### 1.13. DNS et choix du trafic qui passe dans le VPN

Un utilisateur connecté à un VPN d'accès distant peut recevoir des routes vers quelques réseaux internes, ou une route par défaut qui fait passer la majorité du trafic dans le tunnel. Ces approches sont souvent appelées *split tunnel* et *full tunnel*. Avec le split tunnel, seuls les préfixes sélectionnés passent par l'entreprise ; le trafic Internet général utilise généralement la connexion locale. Avec le full tunnel, le trafic Internet passe également par la passerelle de l'entreprise, sous réserve du comportement du client et de la politique.

Le split tunnel peut réduire la charge et améliorer les performances, mais il augmente la complexité des chemins et des contrôles de sécurité. Le full tunnel permet une inspection plus centralisée du trafic Internet, mais nécessite une capacité de sortie suffisante, une politique claire et une configuration correcte des DNS. Il n'existe pas de réponse universelle : la décision dépend du risque, des exigences et de l'architecture.

Le DNS est une cause fréquente de confusion. Un client peut accéder à une adresse IP interne, mais ne pas résoudre le nom du serveur parce qu'il utilise un résolveur DNS public au lieu du résolveur interne. À l'inverse, une zone DNS interne peut renvoyer une adresse qui n'est pas routable depuis le client. Il faut vérifier l'adresse du serveur DNS, les suffixes de recherche, la résolution du nom, la route et les autorisations de pare-feu.

Le contrôle DNS doit aussi être considéré dans la stratégie de sécurité : si le trafic est censé être inspecté par la passerelle d'entreprise, l'utilisation d'un résolveur externe directement depuis le poste peut contourner une partie de la visibilité prévue. Les détails dépendent du système d'exploitation, du client VPN et de l'usage éventuel de DNS chiffré.

### 1.14. MTU, surcharge et fragmentation

Chaque couche d'encapsulation ajoute des octets. Un paquet qui tient dans le MTU habituel du réseau local peut devenir trop grand après ajout des en-têtes du tunnel et d'IPsec. Le MTU (*Maximum Transmission Unit*) indique la taille maximale d'un paquet de couche 3 sur une interface sans fragmentation, selon la technologie et la configuration. Le MTU Ethernet courant est souvent de 1500 octets, mais ce nombre n'est pas une garantie universelle pour tous les chemins.

Lorsque les paquets sont trop grands, plusieurs comportements sont possibles selon IPv4, IPv6, la configuration DF (*Don't Fragment*), les équipements et le tunnel : fragmentation, rejet avec message ICMP, ajustement de la taille d'envoi ou blocage si les messages nécessaires ne passent pas. Le symptôme peut être surprenant : les petits pings réussissent, alors que le chargement d'une page, le transfert d'un fichier ou une session applicative échoue ou se bloque.

Une correction peut consister à ajuster le MTU de tunnel, le MSS TCP, ou à permettre les messages ICMP nécessaires à la découverte de MTU. Ces réglages ne doivent pas être appliqués au hasard. La surcharge exacte dépend du protocole, du mode, des algorithmes, des options et de la présence éventuelle de GRE ou de NAT-T. Il faut mesurer et tester les flux réels.

```text
Paquet IP interne
+-------------------------------+
| En-tête IP | TCP/UDP | données|
+-------------------------------+

Après encapsulation et protection :
+----------------------------------------------------+
| En-tête externe | IPsec/encapsulation | paquet interne |
+----------------------------------------------------+
                  <--- surcharge supplémentaire --->
```

Un ping de taille standard ne suffit pas à démontrer que la MTU est correcte. Les tests devraient inclure différentes tailles de paquets, les applications représentatives et une capture si nécessaire. Une modification du MTU peut affecter d'autres flux ; elle doit être documentée et vérifiée après mise en œuvre.

### 1.15. Menaces et erreurs de conception courantes

Un attaquant peut tenter de deviner des secrets faibles, usurper une identité, exploiter un client vulnérable, compromettre un poste autorisé ou provoquer une saturation. Le VPN peut également être exposé à des erreurs de configuration : algorithmes obsolètes, certificats expirés, règles trop ouvertes, tunnels oubliés, comptes de prestataires non désactivés ou versions de firmware non maintenues.

Un tunnel chiffré peut transporter un logiciel malveillant ou des données exfiltrées. Le chiffrement empêche certains observateurs de lire le contenu, mais il peut aussi réduire la visibilité d'outils qui n'inspectent pas le trafic au point de terminaison. C'est pourquoi l'accès VPN doit être combiné à une sécurité des postes, à l'authentification forte, à la journalisation, à la segmentation et à la supervision.

Le plus grand risque n'est pas toujours une faiblesse cryptographique. Un compte volé avec des droits trop larges, une passerelle non mise à jour ou un accès d'administration exposé peut suffire. Les contrôles de configuration et le principe du moindre privilège sont donc aussi importants que le choix de l'algorithme.

> **Danger :** Ne configurez pas un VPN avec une PSK faible, ne partagez pas un même secret entre de nombreux sites sans nécessité, et ne publiez pas la configuration contenant les clés ou les mots de passe dans un dépôt public. En cas de doute sur une clé exposée, traitez-la comme compromise, remplacez-la et révoquez les accès concernés selon la procédure de l'organisation.

---

## 2. Configuration et pratique

### 2.1. Préparer un laboratoire simple

Un laboratoire peut être construit avec deux routeurs Cisco, deux commutateurs et deux PC, ou avec des routeurs virtuels dans une plateforme de simulation. Les interfaces, les images logicielles et les commandes disponibles varient ; il faut d'abord vérifier que l'environnement prend en charge les fonctions étudiées. Les exemples ci-dessous sont des modèles pédagogiques à adapter, et non des blocs à coller aveuglément sur un équipement de production.

Plan d'adressage proposé :

| Équipement | Interface / rôle | Adresse |
|---|---|---|
| Routeur A | LAN | `10.10.10.1/24` |
| PC A | Réseau local du site A | `10.10.10.10/24` |
| Routeur A | WAN | `198.51.100.10/30` |
| Routeur B | WAN | `203.0.113.10/30` |
| Routeur B | LAN | `10.20.20.1/24` |
| PC B | Réseau local du site B | `10.20.20.20/24` |

Les adresses `198.51.100.0/24` et `203.0.113.0/24` appartiennent à des plages de documentation réservées aux exemples. Elles ne doivent pas être utilisées comme adresses publiques réelles sur Internet. Dans un laboratoire isolé, elles servent de représentation des adresses WAN.

```text
LAN A                         Réseau de transport                        LAN B
10.10.10.0/24                                                            10.20.20.0/24
 PC A -- R-A WAN 198.51.100.10 ===== Internet simulé ===== 203.0.113.10 R-B -- PC B
               <--------- tunnel IPsec site-to-site --------->
```

Avant de configurer un VPN, il faut faire fonctionner l'adressage et le routage de base. Les deux routeurs doivent pouvoir joindre les adresses WAN de l'autre à travers le réseau de transport. Si ce test ne fonctionne pas, commencer par résoudre ce problème au lieu de modifier les paramètres cryptographiques.

### 2.2. Vérifier l'état initial avec Cisco IOS

Les commandes suivantes sont courantes sur de nombreux équipements Cisco, mais certaines sorties ou options dépendent de la version. Elles servent à vérifier les interfaces, les routes et la connectivité du plan de transport.

```text
enable
show ip interface brief
show ip route
show running-config | section interface
ping 203.0.113.10
traceroute 203.0.113.10
```

Depuis le routeur A, la commande `ping 203.0.113.10` vérifie la connectivité IP vers le WAN du routeur B, si l'adressage de laboratoire est ainsi configuré. Sur le routeur B, effectuer le test dans l'autre sens. Si le ping échoue, vérifier l'état physique ou virtuel des interfaces, les masques, l'adresse de passerelle, les routes et les règles de filtrage. Un ping qui réussit ne prouve toutefois pas que les paramètres IPsec sont compatibles : il ne teste que la connectivité IP que le ping peut utiliser.

Les commandes `show running-config` peuvent afficher des secrets selon leur type et la plateforme. En production, ne publiez pas la sortie complète sans la nettoyer. Les mots de passe, clés prépartagées, adresses d'administration et détails de topologie doivent être traités selon la politique de confidentialité de l'organisation.

### 2.3. Comprendre la configuration avant de l'écrire

Une configuration VPN site-to-site comprend généralement plusieurs éléments :

1. une connectivité IP entre les adresses des passerelles ;
2. une méthode d'authentification des pairs ;
3. une politique IKE qui définit les paramètres de négociation ;
4. une proposition IPsec pour protéger les données ;
5. des sélecteurs ou une politique indiquant les réseaux à protéger ;
6. une association entre cette politique et l'interface ou le pair distant ;
7. des routes cohérentes pour les réseaux distants ;
8. des règles de pare-feu autorisant le trafic de négociation et les flux protégés ;
9. des contrôles de journalisation, de surveillance et de renouvellement.

Les fabricants présentent ces étapes de façon différente. Certains appareils utilisent des politiques numérotées, des crypto maps et des listes d'accès ; d'autres utilisent des objets, des profils IKE et des règles de sécurité. Il faut comprendre l'objectif de chaque objet et la manière dont il est appliqué au chemin des paquets.

### 2.4. Exemple conceptuel de VPN IPsec avec Cisco IOS

Les exemples de commande ci-dessous illustrent une architecture de VPN IPsec site-to-site sur des variantes de Cisco IOS/IOS XE capables de prendre en charge IKEv2 et les commandes indiquées. La syntaxe réelle varie selon la plateforme et la version. Il faut consulter le guide officiel correspondant à l'équipement, choisir les algorithmes approuvés et vérifier la compatibilité des deux pairs avant utilisation.

**Hypothèses du laboratoire :**

- routeur A : WAN `198.51.100.10`, LAN `10.10.10.0/24` ;
- routeur B : WAN `203.0.113.10`, LAN `10.20.20.0/24` ;
- IKEv2 avec PSK uniquement pour un exercice isolé ;
- sélecteurs limités aux deux réseaux de laboratoire.

Un squelette de configuration peut ressembler à ceci sur une plateforme compatible :

```text
! Exemple pédagogique seulement : adapter à la version IOS/IOS XE.
! Routeur A
crypto ikev2 proposal IKEV2-PROP
 encryption aes-cbc-256
 integrity sha256
 group 14
!
crypto ikev2 policy IKEV2-POL
 proposal IKEV2-PROP
!
crypto ikev2 keyring VPN-KEYS
 peer ROUTEUR-B
  address 203.0.113.10
  pre-shared-key local <SECRET_A>
  pre-shared-key remote <SECRET_B>
!
crypto ikev2 profile VPN-PROFILE
 match identity remote address 203.0.113.10 255.255.255.255
 authentication local pre-share
 authentication remote pre-share
 keyring local VPN-KEYS
!
ip access-list extended VPN-TRAFFIC
 permit ip 10.10.10.0 0.0.0.255 10.20.20.0 0.0.0.255
!
crypto ipsec transform-set VPN-TS esp-aes 256 esp-sha256-hmac
 mode tunnel
!
crypto map VPN-MAP 10 ipsec-isakmp
 set peer 203.0.113.10
 set transform-set VPN-TS
 set ikev2-profile VPN-PROFILE
 match address VPN-TRAFFIC
!
interface GigabitEthernet0/0
 description WAN
 crypto map VPN-MAP
```

Cet extrait sert à illustrer les concepts et la relation entre objets. Selon l'image IOS/IOS XE, les commandes de proposition, de transform-set, de crypto map et de profils peuvent différer ou ne pas être disponibles sous cette forme. Certaines configurations exigent aussi des paramètres IKE, des durées de vie, un traitement NAT, un routage ou des politiques de pare-feu supplémentaires. Il faut valider la syntaxe et les exigences de sécurité de la plateforme officielle avant de l'exécuter. Le laboratoire doit être isolé et ne pas réutiliser un secret sensible.

Le routeur B doit avoir une configuration symétrique, avec l'adresse du pair A et les réseaux inversés dans la liste de trafic : source `10.20.20.0/24`, destination `10.10.10.0/24`. Les paramètres cryptographiques et d'authentification doivent être compatibles. Les deux côtés n'ont pas toujours besoin d'être textuellement identiques, mais ils doivent parvenir à une suite négociée commune et à des identités reconnues.

> **Astuce :** Les symboles `<SECRET_A>` et `<SECRET_B>` sont des marqueurs de remplacement, pas des commandes à saisir littéralement. N'écrivez pas une clé sensible directement dans un support de cours partagé. Dans un vrai déploiement, utilisez le mécanisme de gestion de secrets approuvé par l'organisation.

### 2.5. Définir la politique de trafic

Dans le modèle de configuration précédent, une liste de trafic identifie les flux qui doivent être protégés. La règle `permit ip 10.10.10.0 0.0.0.255 10.20.20.0 0.0.0.255` sélectionne le trafic IPv4 provenant du LAN A et allant vers le LAN B. Le masque générique `0.0.0.255` correspond à un sous-réseau `/24` dans cet exemple. Il ne faut pas utiliser la même règle sans l'adapter à l'adressage réel.

Le mot `permit` dans la liste de trafic ne signifie pas nécessairement que le pare-feu de la passerelle laisse directement passer le paquet en clair. Dans ce contexte, il sert à classer le trafic qui correspond à la politique IPsec. Le comportement global dépend de l'application de la crypto map, du reste de la configuration et du produit. Cette distinction est importante, car une ACL utilisée pour sélectionner un trafic VPN ne possède pas toujours le même rôle qu'une ACL utilisée pour filtrer l'accès aux interfaces.

Les sélecteurs doivent être cohérents des deux côtés. Si A utilise `10.10.10.0/24` vers `10.20.20.0/24`, B doit généralement sélectionner le flux inverse. Si l'un des côtés attend `/24` tandis que l'autre attend `/16`, la négociation peut échouer ou aboutir à une politique ne couvrant pas le trafic voulu, selon l'implémentation. Vérifier les journaux et l'état des SA plutôt que de supposer que le tunnel est correctement formé.

### 2.6. Les routes vers les réseaux distants

Dans un modèle à crypto map, la route vers le réseau distant dirige généralement le paquet vers l'interface WAN sur laquelle la politique IPsec est appliquée ; la politique reconnaît alors le flux et le protège. Dans un modèle à interface de tunnel, une route peut viser directement l'interface logique. L'approche exacte dépend de la plateforme et du type de VPN.

Pour un petit laboratoire, on peut avoir une route statique vers le réseau distant. Un exemple conceptuel serait :

```text
! Exemple de route pour une architecture à routage via le WAN.
! La syntaxe et le prochain saut sont à adapter à la topologie.
ip route 10.20.20.0 255.255.255.0 <NEXT_HOP_WAN>
```

Le prochain saut doit être le prochain routeur de transport réellement joignable, et non une adresse arbitraire. Dans une architecture à interface de tunnel, la route et l'interface peuvent être différentes. Ne copiez pas cette route si elle n'est pas cohérente avec le plan d'adressage du laboratoire.

Il faut aussi vérifier le chemin retour. Si le PC A peut envoyer un paquet vers B mais que le routeur B n'a pas de route pour `10.10.10.0/24`, le retour échoue. De même, la passerelle par défaut du PC B doit pointer vers une passerelle qui sait atteindre le VPN. Un test réussi dans un seul sens n'est pas une validation complète.

### 2.7. GRE : créer un tunnel logique de routage

GRE est surtout utile pour comprendre la différence entre tunnel et protection. Sur deux routeurs compatibles, un tunnel GRE peut être configuré avec des adresses source et destination externes, puis recevoir une adresse IP de tunnel. Les exemples suivants sont illustratifs ; adaptez les noms d'interface et assurez-vous que les adresses externes sont routables l'une vers l'autre.

```text
! Routeur A - exemple conceptuel
interface Tunnel0
 description Tunnel GRE vers routeur B
 ip address 172.16.0.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.10
!
! Routeur B - extrémité symétrique
interface Tunnel0
 description Tunnel GRE vers routeur A
 ip address 172.16.0.2 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 198.51.100.10
```

Les adresses de tunnel `172.16.0.1/30` et `172.16.0.2/30` illustrent un lien point à point. Les routes vers les réseaux distants peuvent ensuite utiliser ce tunnel si le routage sous-jacent et la plateforme le permettent. Les commandes exactes de vérification incluent souvent `show interfaces tunnel0` ou des variantes équivalentes.

GRE seul ne chiffre pas les paquets. Dans un environnement réel nécessitant confidentialité et intégrité sur un réseau non fiable, on doit protéger GRE par une solution appropriée, souvent IPsec ou une architecture alternative approuvée. Attention aussi aux boucles de routage : le réseau extérieur doit pouvoir joindre directement l'adresse de destination du tunnel sans renvoyer ce trafic à travers le tunnel qu'il sert à créer.

### 2.8. Les clients d'accès distant

La configuration d'un client VPN dépend fortement du fournisseur, mais le processus général se ressemble. L'utilisateur installe un client approuvé, indique l'adresse de la passerelle ou importe un profil, s'authentifie, puis reçoit les routes et les paramètres autorisés. Le client peut créer une interface virtuelle. Le système d'exploitation utilise alors des routes pour décider quel trafic passe par cette interface.

Avant de dépanner une connexion, demander quelles ressources doivent être accessibles et quels noms de serveur sont utilisés. Une connexion peut être active mais n'offrir qu'un accès partiel par conception. Il faut éviter de désactiver systématiquement le pare-feu local ou l'antivirus pour « faire fonctionner » le VPN. Les tests doivent isoler le problème sans supprimer les contrôles de sécurité.

Un profil d'accès distant doit être protégé. Ne le distribuez pas sur un canal public s'il contient des informations sensibles. Les mots de passe doivent être saisis dans le client officiel et ne pas être intégrés à des scripts partagés. L'organisation doit prévoir la révocation des comptes et certificats lorsqu'un employé quitte l'équipe ou qu'un appareil est perdu.

### 2.9. Vérifier qu'un VPN fonctionne

La validation doit être faite par couches, du bas vers le haut :

1. **Transport externe :** les interfaces WAN sont actives et les adresses des pairs sont joignables.
2. **Négociation :** les identités et paramètres de sécurité sont compatibles ; les journaux ne signalent pas d'échec d'authentification ou de proposition.
3. **Associations de sécurité :** les SA IKE et de données appropriées existent.
4. **Routage :** les réseaux distants sont atteints par le chemin prévu.
5. **Sélecteurs / autorisations :** les adresses et protocoles du test correspondent à la politique.
6. **Pare-feu :** les règles permettent le trafic nécessaire et le retour.
7. **Application :** le service distant répond réellement, par exemple DNS, HTTPS ou SSH selon les droits.
8. **Supervision :** les journaux et compteurs démontrent un fonctionnement stable.

Sur certaines plateformes Cisco, des commandes de vérification utiles sont :

```text
show crypto ikev2 sa
show crypto ipsec sa
show crypto session
show access-lists
show ip route
show interfaces
```

La disponibilité exacte de ces commandes et leur sortie varie selon la famille logicielle. La commande `show crypto ipsec sa` peut notamment afficher les compteurs de paquets encapsulés et décapsulés. Si le compteur d'encapsulation augmente mais que celui de décapsulation reste nul, il faut examiner le chemin retour, les règles distantes, les sélecteurs et la réception des paquets. Ce symptôme donne une piste, mais ne désigne pas à lui seul la cause.

### 2.10. Plan de test minimal

Un plan de test évite de se limiter à un seul ping. Utilisez un tableau comme celui-ci et complétez-le avec les résultats, l'heure et l'équipement testé.

| Test | Résultat attendu | Si le test échoue, vérifier en premier |
|---|---|---|
| Ping entre adresses WAN des pairs | Réponse si ICMP est autorisé | IP, masque, route, filtrage WAN |
| État IKE | SA établie | Identité, authentification, algorithmes, ports |
| État IPsec | SA de données présente | Sélecteurs, proposition, politique IPsec |
| Ping du LAN A vers la passerelle LAN B | Réponse si ICMP est autorisé | Route, sélecteurs, filtrage et retour |
| Résolution DNS d'un nom interne | Adresse attendue | DNS fourni, suffixe, route, ACL |
| Connexion à l'application autorisée | Service accessible | Port, service, pare-feu hôte, droits |
| Transfert de données volumineux | Débit stable sans blocage | MTU/MSS, pertes, capacité, inspection |
| Reconnexion après coupure contrôlée | VPN rétabli selon le délai cible | DPD, temporisations, routes, supervision |

Une documentation doit préciser quels tests ont été exécutés, depuis quel poste, vers quelle destination, à quelle heure et avec quel résultat. Un message « le VPN marche » ne fournit pas assez d'information pour une exploitation professionnelle.

---

## 3. Dépannage et sécurité

### 3.1. Méthode générale de dépannage

Le dépannage d'un VPN doit partir d'un symptôme précis. « Ça ne marche pas » n'indique pas si le client ne s'authentifie pas, si la négociation IKE échoue, si les SA sont établies mais qu'aucun paquet ne circule, si seuls certains réseaux sont inaccessibles ou si la connexion se coupe au bout de quelques minutes. Le premier travail consiste à définir une situation reproductible : qui se connecte, depuis où, vers quelle ressource, avec quelle adresse ou quel nom, et depuis quand le problème existe-t-il ?

Vérifiez ensuite les changements récents. Une modification d'ACL, une mise à jour, un remplacement de certificat, un changement d'adresse publique, une nouvelle politique NAT ou une modification du routage peut expliquer une panne apparue brusquement. Comparez la configuration actuelle avec la dernière version validée, sans restaurer aveuglément une sauvegarde qui pourrait réintroduire un problème de sécurité.

Procédez par couches. Vérifiez d'abord l'accès réseau de base, puis la négociation et l'authentification, ensuite les associations de sécurité, les routes, les sélecteurs, les règles de pare-feu et enfin l'application. Collectez les preuves avant de modifier les réglages : états, compteurs, journaux horodatés, captures appropriées et description des tests. Changez une variable à la fois afin de savoir quelle modification a réellement corrigé ou aggravé le problème.

### 3.2. Symptôme : le VPN ne s'établit pas

Les causes courantes sont une mauvaise adresse du pair, une route absente vers l'IP publique, un blocage UDP 500/4500, une PSK incorrecte, un certificat invalide, une identité distante qui ne correspond pas, ou des algorithmes/groupes cryptographiques sans proposition commune. Une différence d'horloge importante peut aussi poser problème dans certains processus liés aux certificats.

Commencez par confirmer que les deux passerelles peuvent communiquer sur le réseau extérieur. Puis vérifiez les journaux IKE des deux côtés, idéalement à la même période. Il est fréquent qu'un seul côté affiche un message explicite, car l'autre ne reçoit pas la réponse attendue. Comparez méthodiquement l'authentification, les identités, les propositions IKE, les groupes cryptographiques et les paramètres attendus.

Ne corrigez pas un échec en activant toutes les suites anciennes possibles. Le but est de trouver une proposition commune acceptable, non de faire accepter n'importe quel algorithme. Si un pair ancien ne prend pas en charge les paramètres requis par la politique de sécurité, il peut être nécessaire de mettre à jour le logiciel, de remplacer l'équipement ou de réviser l'architecture via une procédure formelle.

### 3.3. Symptôme : IKE est établi, mais aucun trafic ne passe

Cette situation indique souvent que le contrôle et le plan de données doivent être diagnostiqués séparément. Vérifiez la présence des SA IPsec, les sélecteurs de trafic, l'application de la politique à l'interface correcte, les routes, les ACL de transit et la politique NAT. Confirmez que le trafic de test utilise bien les sous-réseaux annoncés dans le VPN.

Un cas classique survient lorsque le tunnel est configuré pour `10.10.10.0/24` vers `10.20.20.0/24`, mais que le poste source est connecté à `10.10.30.0/24`. Le trafic ne correspond alors pas au sélecteur attendu. Autre possibilité : les paquets sont envoyés dans le tunnel, mais le réseau distant n'a pas de route de retour, ou un pare-feu local bloque le service.

Comparez les compteurs de paquets encapsulés et décapsulés. Si l'encapsulation augmente lorsque le PC envoie un ping mais que le côté distant ne montre aucune réception, examinez le transport externe, les règles en chemin et le pair. Si les paquets sont décapsulés mais qu'aucune réponse ne revient, examinez la route du réseau local distant, la politique de filtrage et la réponse de l'hôte. Les compteurs sont des indices ; complétez-les avec les journaux et les captures quand c'est nécessaire.

### 3.4. Symptôme : un seul sens fonctionne

Un tunnel peut transporter les paquets dans une direction et échouer au retour à cause d'un routage asymétrique, de sélecteurs mal appariés, d'un NAT inattendu ou d'un pare-feu qui n'autorise pas le flux inverse. Certains pare-feu stateful traitent différemment les connexions qui ne traversent pas le même appareil dans les deux sens. Dans un environnement redondant, les deux chemins doivent être pris en compte.

Vérifiez d'abord si le paquet du test arrive à la passerelle distante. Ensuite, vérifiez s'il est décapsulé, s'il est transmis vers le LAN distant, et si la réponse revient à la passerelle. Une capture côté LAN et une capture côté WAN peuvent révéler l'endroit où le paquet disparaît. Il est important de comparer les adresses avant et après NAT.

Ne supposez pas que l'ICMP est toujours autorisé. Le test peut échouer à cause d'une règle qui bloque les pings alors que l'application fonctionne, ou inversement. Testez un service réellement autorisé, par exemple HTTPS ou un port d'administration contrôlé, tout en respectant les règles du site distant.

### 3.5. Symptôme : certains sites ou applications ne fonctionnent pas

Des problèmes de MTU/MSS et de découverte de MTU peuvent faire échouer les transferts volumineux, les connexions TLS ou les applications qui envoient des segments de taille importante, alors que les petits paquets passent. Des règles DNS peuvent faire apparaître une panne uniquement lorsque l'utilisateur utilise le nom du serveur au lieu de son adresse IP. Une application peut également utiliser un protocole ou un port non inclus dans la politique.

Pour isoler le problème, comparez la résolution DNS, la connexion TCP ou UDP au service, les routes effectives, et le comportement avec de petites puis de grandes charges. Évitez de conclure que le VPN est en cause uniquement parce que l'application échoue pendant que le VPN est connecté. Une panne de service côté serveur, un certificat applicatif expiré, un proxy ou un pare-feu hôte peut produire un symptôme similaire.

Si le problème concerne uniquement un sous-réseau ou un protocole, relisez les sélecteurs et les ACL plutôt que de recréer tout le tunnel. Si le problème est lié aux gros paquets, examinez le MTU du chemin et les messages ICMP utiles. Tout ajustement doit être mesuré, consigné et testé sur plusieurs flux.

### 3.6. Symptôme : le VPN se coupe régulièrement

Une déconnexion périodique peut provenir de la perte d'Internet, d'une expiration de certificat, d'une mauvaise synchronisation d'heure, d'un changement d'adresse publique, d'un NAT qui expire, d'un problème de keepalive, d'une charge CPU élevée, d'une panne de haute disponibilité ou d'une incompatibilité de renouvellement de clés. Elle peut aussi être liée à la politique de sécurité du client ou à une mise en veille de l'ordinateur.

Le premier objectif est de mettre en relation l'heure exacte de la coupure avec les journaux IKE, les événements d'interface et les journaux réseau. Si chaque coupure intervient à un intervalle proche d'une durée de vie, examinez le renouvellement des SA et les paramètres de rekey. Si elle coïncide avec la perte de connectivité Internet, le tunnel peut simplement perdre son chemin extérieur. Si la coupure ne concerne qu'un seul utilisateur, examinez son client, son accès réseau et l'état de son appareil.

Évitez de désactiver les mécanismes de détection du pair sans comprendre leur rôle. Ils peuvent être nécessaires pour détecter rapidement une panne et libérer les ressources. Le réglage des keepalives et temporisations doit tenir compte du NAT, du coût des reconnections et des exigences de disponibilité.

### 3.7. Pare-feu et ports à connaître

La liste exacte des flux à autoriser dépend du protocole VPN et de son mode d'encapsulation. Pour IPsec/IKEv2, les éléments suivants sont fréquemment pertinents :

| Protocole / port | Fonction fréquente | Remarque |
|---|---|---|
| UDP 500 | Établissement IKE | Généralement utilisé au début de la négociation |
| UDP 4500 | IKE et ESP encapsulé pour NAT-T | Souvent nécessaire si NAT-T est utilisé ; certaines implémentations l'utilisent par défaut |
| ESP, protocole IP 50 | Transport IPsec sans encapsulation UDP | Ce n'est pas un port TCP ou UDP |
| GRE, protocole IP 47 | Tunnel GRE | Numéro de protocole IP, pas un port 47 |
| TCP/UDP propres au service | Application transportée | Par exemple HTTPS, DNS ou SSH selon la politique |

Les numéros ci-dessus sont des informations générales ; les règles requises dépendent des extrémités et de la méthode de transport. Il ne faut pas ouvrir largement tous les protocoles de tunnel sur toutes les interfaces. Autorisez uniquement les flux nécessaires entre les adresses des pairs et vérifiez que les règles s'appliquent dans le bon sens.

GRE est identifié par le numéro de protocole IP 47, et ESP par le numéro de protocole IP 50. Ces nombres ne doivent pas être saisis comme s'il s'agissait de ports TCP ou UDP. Une interface d'administration distante ne devrait pas être exposée simplement parce qu'un VPN a été ajouté : l'accès d'administration doit rester limité à des sources approuvées.

### 3.8. Sécuriser un VPN d'entreprise

**Authentification forte.** Pour l'accès distant, associez si possible le VPN à une authentification multifacteur et à des identités individuelles. Évitez les comptes partagés qui empêchent l'attribution des actions à une personne. Pour les passerelles, adoptez des secrets robustes et uniques ou, lorsque c'est adapté, des certificats administrés par une autorité de confiance.

**Moindre privilège.** N'autorisez pas automatiquement tous les clients à joindre tout le réseau interne. Séparez les accès aux applications, aux environnements de développement, aux serveurs de production et à l'administration. Les droits doivent correspondre au rôle et être révisés régulièrement.

**Maintenance.** Mettez à jour les passerelles, les clients VPN et les systèmes d'exploitation selon un processus testé. Suivez les avis de sécurité des fabricants et retirez les versions non supportées. Une technologie cryptographiquement correcte peut être compromise par une vulnérabilité de mise en œuvre ou une mauvaise configuration.

**Gestion des clés et certificats.** Limitez l'accès aux secrets, prévoyez leur renouvellement, leur révocation et le traitement de leur exposition. Surveillez les expirations de certificats avant qu'elles ne provoquent une interruption. Documentez le propriétaire de chaque tunnel et le processus de récupération.

**Journalisation.** Enregistrez les connexions, échecs d'authentification, changements de configuration, événements de tunnel et alertes importantes. Protégez les journaux contre la modification, limitez leur accès et définissez une durée de conservation adaptée. Évitez de journaliser plus de données personnelles ou de contenu que nécessaire.

**Segmentation.** Utilisez des règles de pare-feu pour contrôler les réseaux et services accessibles au travers du tunnel. Un tunnel site-to-site ne devrait pas être considéré comme une autorisation implicite entre toutes les machines des deux sites.

**Résilience.** Prévoyez comment le service réagit à la panne d'une liaison, d'un équipement ou d'une passerelle. La redondance ne suffit pas si l'état des sessions, les routes, les identités ou les politiques ne sont pas cohérents après le basculement.

### 3.9. Principes de sécurité cryptographique

N'autorisez pas les algorithmes uniquement parce qu'ils sont disponibles dans un vieux modèle de configuration. Pour une nouvelle installation, appuyez-vous sur les recommandations de sécurité actualisées de l'organisation, de l'éditeur et des référentiels reconnus. Utilisez des paramètres modernes et maintenus, notamment des suites qui fournissent la confidentialité et l'intégrité, et évitez les protocoles obsolètes comme PPTP.

Ne créez pas de suites cryptographiques « sur mesure » sans expertise. Les constructions modernes combinent des composants dont l'interaction est délicate. Il est préférable d'utiliser les profils supportés et recommandés par la plateforme, avec une compatibilité vérifiée des deux côtés. Si un équipement ancien ne permet pas les paramètres nécessaires, le risque doit être documenté et la migration planifiée.

La confidentialité persistante (*Perfect Forward Secrecy*, ou PFS) peut limiter l'impact de la compromission ultérieure d'une clé selon le mécanisme et la configuration. Elle repose sur des choix précis de groupes et de renouvellement ; elle ne doit pas être considérée comme automatiquement activée parce que le tunnel est chiffré. Le détail doit être vérifié dans la documentation technique du produit.

### 3.10. Sauvegardes et changement de configuration

Avant tout changement, exportez une sauvegarde sécurisée de la configuration, notez la version logicielle, l'heure, le propriétaire du service, les dépendances et la méthode de retour arrière. Évitez d'inclure inutilement des secrets en clair dans les sauvegardes ou de les stocker au même endroit que les documents de dépannage. La sauvegarde doit être accessible uniquement aux personnes autorisées.

Définissez une fenêtre de maintenance si le changement peut interrompre le service. Prévoyez un plan de retour arrière qui a été compris et testé, pas seulement une intention générale. Vérifiez les deux extrémités : une configuration n'est pas validée parce qu'elle a été appliquée à un seul routeur. Les tests doivent couvrir le plan de données, la résolution DNS, les applications attendues et le comportement après reconnexion.

Après la mise en service, comparez les journaux et compteurs avec l'état de référence. Documentez les écarts et les éventuels risques résiduels. Un changement de clé doit être coordonné pour éviter qu'une extrémité utilise la nouvelle clé tandis que l'autre attend encore l'ancienne, sauf si le produit dispose d'un mécanisme de transition explicitement prévu.

### 3.11. Checklist de validation avant mise en service

Utilisez cette liste pour un nouveau tunnel site-to-site ou une extension importante :

- [ ] Les deux réseaux internes utilisent des préfixes compatibles et idéalement non chevauchants.
- [ ] Les adresses de transport des pairs sont correctes et joignables.
- [ ] Les identités des pairs sont définies et vérifiées.
- [ ] La méthode d'authentification et les secrets ou certificats sont gérés de façon sûre.
- [ ] Les propositions cryptographiques sont compatibles et conformes à la politique.
- [ ] Les sélecteurs de trafic correspondent aux sous-réseaux réellement utilisés.
- [ ] Les routes aller et retour ont été vérifiées.
- [ ] Les règles de pare-feu n'autorisent que les flux nécessaires.
- [ ] Les règles NAT n'interfèrent pas involontairement avec les sélecteurs.
- [ ] Le MTU/MSS a été vérifié avec les applications représentatives.
- [ ] Les journaux, alertes et compteurs utiles sont disponibles.
- [ ] La reconnexion après une interruption contrôlée fonctionne comme prévu.
- [ ] La sauvegarde et la procédure de retour arrière sont disponibles.
- [ ] Les propriétaires, accès autorisés et date de révision sont documentés.

### 3.12. Mini-cas pratique : relier deux agences

Une entreprise possède un siège utilisant `10.10.10.0/24` et une agence utilisant `10.20.20.0/24`. Chaque site dispose d'une passerelle avec une adresse WAN routable. Les employés du siège doivent accéder à un serveur de fichiers dans l'agence, mais ils ne doivent pas accéder au réseau d'administration des équipements. Le besoin est donc un VPN site-to-site avec une politique restrictive.

**Étape 1 — cadrer le besoin.** Déterminer les hôtes qui communiquent, le protocole utilisé par le serveur, les ports nécessaires, les exigences de disponibilité et le modèle d'authentification. Éviter une règle générale qui autorise tout le trafic IP entre les deux `/24` si seuls quelques services sont nécessaires.

**Étape 2 — préparer le transport.** Vérifier que les passerelles se joignent sur leurs adresses externes et que les routeurs intermédiaires permettent les protocoles requis. Si une des passerelles est derrière un NAT, vérifier le support de NAT-T et les règles UDP 500/4500 adaptées.

**Étape 3 — configurer la protection.** Choisir IPsec/IKEv2 ou une solution équivalente supportée, définir l'authentification, les algorithmes approuvés et les sélecteurs nécessaires. Les deux côtés doivent être compatibles. Ne pas utiliser un secret faible ou un profil obsolète pour accélérer le test.

**Étape 4 — routage et filtrage.** Installer les routes ou la politique de tunnel appropriée, puis limiter l'accès au serveur de fichiers et aux ports réellement requis. S'assurer que le pare-feu autorise la réponse et que les réseaux de gestion restent isolés.

**Étape 5 — tester et documenter.** Valider la négociation, les SA, les routes, les compteurs d'encapsulation, la résolution de nom et l'accès au serveur. Essayer aussi un service qui doit rester interdit pour confirmer que la segmentation fonctionne. Enregistrer les résultats et le plan de retour arrière.

**Résultat attendu.** Les utilisateurs autorisés atteignent le serveur de fichiers avec un trafic protégé entre les passerelles. Les autres ressources restent bloquées conformément à la politique. Le tunnel peut être surveillé et la procédure de rétablissement est documentée.

### 3.13. Exercices de révision avec corrigés

**Exercice 1 — tunnel ou chiffrement ?** Un administrateur crée un tunnel GRE entre deux routeurs. Peut-il affirmer que les données sont secrètes sur Internet ?

**Corrigé :** Non. GRE fournit l'encapsulation mais pas le chiffrement par défaut. Il faut ajouter une protection appropriée, comme IPsec dans une architecture validée, si la confidentialité est requise.

**Exercice 2 — tunnel connecté, serveur inaccessible.** L'état IPsec indique des associations établies, mais le client A ne joint pas le serveur B. Citez quatre contrôles.

**Corrigé :** Vérifier les routes, les sélecteurs de trafic, les règles de pare-feu sur les deux sites, les passerelles par défaut des hôtes, le NAT et le service côté serveur. Vérifier aussi les compteurs encapsulés/décapsulés pour savoir où le paquet disparaît.

**Exercice 3 — UDP 500 suffit-il toujours ?** Une passerelle échange des messages IKE sur UDP 500, mais les données ne circulent pas derrière un NAT. Quel élément faut-il examiner ?

**Corrigé :** Vérifier si NAT Traversal est utilisé et si UDP 4500 est autorisé. Selon la solution et le chemin, ESP natif peut aussi être pertinent. Il faut confirmer le transport réellement négocié dans les journaux plutôt que d'appliquer une règle générique.

**Exercice 4 — pourquoi DNS échoue-t-il ?** L'utilisateur peut joindre `10.20.20.50`, mais `files.agence.example` ne se résout pas.

**Corrigé :** Le tunnel IP peut fonctionner, alors que le client ne reçoit pas le bon serveur DNS, n'utilise pas le suffixe interne, ou reçoit une réponse DNS incorrecte. Tester la résolution, vérifier les paramètres du client VPN et vérifier le routage vers le résolveur.

**Exercice 5 — réseaux chevauchants.** Deux sites utilisent tous deux `192.168.1.0/24`. Pourquoi cela complique-t-il le VPN ?

**Corrigé :** Les routes ne permettent pas de distinguer clairement les destinations identiques. Il est préférable de renuméroter l'un des sites. Une traduction d'adresses spécifique peut parfois être utilisée, mais elle complique la conception, le dépannage et la visibilité des adresses.

**Exercice 6 — petits paquets réussis, gros transferts bloqués.** Quelle hypothèse tester ?

**Corrigé :** Un problème de MTU/MSS ou de découverte de MTU est possible. Mesurer le comportement avec plusieurs tailles, vérifier les messages ICMP nécessaires et calculer la surcharge du tunnel avant de modifier le MTU.

**Exercice 7 — VPN d'accès distant.** Un prestataire se connecte avec succès, mais peut atteindre beaucoup trop de serveurs.

**Corrigé :** Le tunnel est établi mais la politique d'autorisation est trop large. Réduire les routes et règles de pare-feu, appliquer le moindre privilège et, si nécessaire, isoler le prestataire dans une zone dédiée. Vérifier aussi l'authentification multifacteur et la traçabilité.

**Exercice 8 — quel est le port d'ESP ?** Un collègue veut ouvrir TCP/50 pour IPsec.

**Corrigé :** ESP est le protocole IP numéro 50, pas un port TCP. IKE utilise couramment UDP 500 et l'encapsulation NAT-T UDP 4500.

### 3.14. Glossaire rapide

| Mot | Explication |
|---|---|
| ACL | Liste de contrôle d'accès utilisée pour sélectionner ou filtrer des flux selon son contexte |
| AES | Famille d'algorithmes de chiffrement symétrique |
| Chiffrement | Transformation du contenu pour limiter sa lecture aux détenteurs de la clé |
| Décapsulation | Retrait de l'enveloppe de tunnel à l'extrémité de sortie |
| ESP | Encapsulating Security Payload, protocole de protection IPsec |
| GRE | Generic Routing Encapsulation, mécanisme de tunneling sans chiffrement intégré |
| IKEv2 | Protocole de négociation et de gestion de clés pour IPsec |
| MTU | Taille maximale de paquet de couche 3 supportée sans fragmentation sur un lien donné |
| NAT | Traduction d'adresses réseau, parfois accompagnée d'une traduction de ports |
| NAT-T | Encapsulation UDP d'IPsec pour faciliter le passage à travers un NAT |
| Pair | Extrémité distante reconnue dans la configuration VPN |
| PFS | Propriété de confidentialité persistante, selon les mécanismes de clés utilisés |
| PSK | Secret partagé configuré aux deux extrémités |
| SA | Association de sécurité qui définit des paramètres pour protéger le trafic |
| Sélecteur | Critère permettant de déterminer quel trafic est concerné par la politique VPN |
| Split tunnel | Mode où seuls certains réseaux passent par le VPN |
| Full tunnel | Mode où la majeure partie ou la totalité du trafic IP sélectionné passe par le VPN |
| Tunnel | Chemin logique utilisant l'encapsulation pour transporter le trafic |
| VPN | Réseau privé virtuel s'appuyant sur une infrastructure de transport partagée ou non maîtrisée |

---

## Points à retenir

- Un VPN est une architecture de communication ; le terme ne décrit pas à lui seul un mécanisme de chiffrement précis.
- L'encapsulation transporte un paquet à l'intérieur d'un autre ; elle ne garantit pas la confidentialité.
- GRE crée un tunnel logique mais ne chiffre pas les données par défaut. IPsec ou un mécanisme adapté peut fournir la protection nécessaire.
- IPsec utilise des politiques, ESP et des mécanismes de gestion de clés comme IKEv2. ESP est couramment utilisé pour protéger les données.
- Le mode tunnel ajoute un en-tête IP externe au paquet transporté et convient souvent aux VPN entre passerelles.
- Les deux extrémités doivent être compatibles sur l'authentification, les paramètres cryptographiques, les identités et les sélecteurs de trafic.
- Un VPN peut être établi alors que les applications sont inaccessibles. Il faut contrôler les routes, le filtrage, le NAT, le DNS, le retour et le MTU.
- UDP 500 et UDP 4500 sont utilisés pour IKE/NAT-T dans de nombreux déploiements. ESP correspond au protocole IP 50, et GRE au protocole IP 47 ; ce ne sont pas des ports TCP/UDP.
- Les réseaux non chevauchants simplifient la conception et le dépannage.
- En accès distant, l'authentification forte, la segmentation et le moindre privilège sont essentiels.
- Les technologies obsolètes, les secrets faibles et les règles trop ouvertes doivent être évités.
- La validation nécessite un plan de test qui vérifie la négociation, les associations de sécurité, les routes, les applications et la reconnexion.

### Références techniques

1. IETF, **RFC 4301 — Security Architecture for the Internet Protocol**. Architecture IPsec, politiques de sécurité, mode transport et mode tunnel : https://www.rfc-editor.org/rfc/rfc4301.html
2. IETF, **RFC 7296 — Internet Key Exchange Protocol Version 2 (IKEv2)**. Négociation IKEv2, authentification et gestion des associations de sécurité : https://www.rfc-editor.org/rfc/rfc7296.html
3. IETF, **RFC 3948 — UDP Encapsulation of IPsec ESP Packets**. Encapsulation UDP d'ESP pour la traversée NAT : https://www.rfc-editor.org/rfc/rfc3948.html
4. IETF, **RFC 9329 — TCP Encapsulation of IKE and IPsec Packets**. Solution d'encapsulation TCP pour les environnements où le transport UDP ne convient pas, avec des considérations de performance : https://www.rfc-editor.org/rfc/rfc9329.html
5. Cisco, documentation officielle **Security and VPN Configuration Guides** pour la version exacte de Cisco IOS/IOS XE utilisée. Consulter les guides spécifiques au routeur avant d'appliquer des commandes : https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-software/products-installation-and-configuration-guides-list.html
6. Cisco, portail de documentation et de configuration IPsec VPN : https://www.cisco.com/c/en/us/support/security/vpn-products/tsd-products-support-series-home.html
7. WireGuard, documentation officielle du protocole et de sa configuration : https://www.wireguard.com/
8. OpenVPN, documentation officielle : https://openvpn.net/community-resources/

Ces références servent à approfondir les notions. Les commandes et les exigences exactes évoluent selon les versions logicielles, les familles d'équipements et la politique de sécurité de l'organisation. Pour un déploiement réel, privilégier les guides officiels à jour de la plateforme retenue et les standards IETF pertinents.
