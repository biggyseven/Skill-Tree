---
node_id: vpn-expert
title: VPN & tunnels - Expert
---

# VPN & tunnels - Expert

**Niveau :** EXPERT

Un service VPN expert doit être conçu comme un système critique, et non comme une simple association de chiffrement entre deux adresses publiques. L'ingénierie doit réunir le modèle de confiance, les identités de pairs, le cycle de vie des clés, la politique de trafic, les domaines de routage, les mécanismes de convergence, la résistance aux pannes, les limites de capacité et les obligations de journalisation. Une SA active est seulement un signal parmi d'autres : elle ne prouve ni que le chemin applicatif est correct, ni que les réseaux atteignables sont les bons, ni que le niveau de sécurité reste conforme aux exigences de l'organisation.

À ce niveau, il faut savoir arbitrer entre plusieurs architectures route-based et policy-based, sélectionner les mécanismes cryptographiques compatibles avec la politique de sécurité, préparer la rotation des certificats et secrets, maîtriser les sélecteurs, concevoir des topologies à grande échelle, contrôler les routes apprises et mesurer la convergence en cas de panne. Il faut également distinguer la disponibilité du plan de contrôle de celle du plan de données, et les mécanismes qui protègent le tunnel de ceux qui autorisent réellement l'accès aux applications.

Le cours conserve des rappels structurés sur IPsec, IKEv2, ESP, GRE, NAT Traversal, MTU et accès distant, puis les relie à des problématiques expertes : gouvernance cryptographique, PKI, segmentation multi-sites, routage BGP/OSPF, haute disponibilité, VPN dans le cloud, détection d'incident, observabilité, capacité, migration et retour arrière. Les commandes Cisco IOS/IOS XE et les extraits de configuration sont des exemples d'architecture. La syntaxe, les capacités matérielles, les limitations de licences et les algorithmes disponibles varient selon la plateforme et la version ; toute mise en production exige une validation documentaire, un laboratoire représentatif et un plan de changement approuvé.

L'objectif est de concevoir un VPN qui demeure sûr, prévisible et observable dans le temps : il doit résister aux erreurs de routage, à la perte d'un lien, à la rotation d'une clé, à la panne d'une passerelle et à une tentative d'accès non autorisée. Le raisonnement attendu est fondé sur les preuves — états, compteurs, journaux corrélés, captures ciblées, mesures de perte et tests d'autorisation — et non sur la seule impression qu'un tunnel « est monté ».

> **Analogie** : Un réseau VPN d'entreprise ressemble à un réseau routier international doté de frontières, de badges, de voies prioritaires et d'un centre de supervision. La cryptographie protège le transport, les identités valident les partenaires, le routage choisit le chemin, la segmentation délimite les destinations autorisées et la télémétrie détecte les anomalies. Ajouter une seconde route sans tester la convergence ne garantit pas la continuité ; créer un tunnel entre deux réseaux sans limiter les destinations peut transformer une interconnexion en raccourci vers tout le système d'information.
---

## 1. La théorie et les algorithmes

### 1.1. Architecture VPN experte : responsabilités et frontières de confiance

Une architecture VPN comprend au minimum les hôtes ou sous-réseaux qui communiquent, les passerelles ou clients VPN, le réseau de transport, une politique de sécurité et un mécanisme de routage. Selon la solution, elle comprend aussi une autorité de certification, un service d'authentification, une plateforme de journalisation, un service de gestion de configuration et des mécanismes de haute disponibilité.

Dans un VPN site-to-site, une passerelle de chaque site représente habituellement le réseau distant. Les hôtes n'ont pas nécessairement de client VPN : ils envoient leurs paquets vers leur passerelle locale, qui décide de les transmettre dans le tunnel. Dans un VPN d'accès distant, le poste de l'utilisateur établit lui-même la connexion vers une passerelle ou un concentrateur. La passerelle attribue ou reconnaît une identité, peut fournir une adresse virtuelle et des routes, puis applique une politique qui limite les ressources atteignables.

Il faut distinguer trois plans de fonctionnement :

- **Plan de contrôle** : découverte du pair, négociation IKE, authentification, création et renouvellement des associations de sécurité, échange éventuel de routes ou de paramètres d'accès.
- **Plan de données** : paquets applicatifs effectivement transportés et protégés par IPsec ou par un autre protocole VPN.
- **Plan d'exploitation** : journaux, compteurs, supervision, inventaire de configuration, alertes, sauvegardes, procédures de rotation des secrets et tests périodiques.

Un VPN peut ainsi présenter un plan de contrôle opérationnel sans transporter les flux attendus. Le cas typique est une IKE SA active mais aucune CHILD SA correspondant au trafic, ou bien des associations actives avec des compteurs qui n'augmentent pas. Un autre cas est un plan de données fonctionnel alors que la supervision ne reçoit plus de journaux : le service est temporairement utilisable, mais l'équipe perd une partie de sa capacité à détecter et diagnostiquer les incidents.

### 1.2. Choisir la bonne famille de VPN

| Technologie | Fonction principale | Chiffrement intégré | Cas d'usage courant | Limite à retenir |
|---|---|---|---|---|
| IPsec en mode tunnel | Protéger des paquets IP entre pairs | Oui, avec une SA ESP configurée pour cela | VPN site-to-site | Politiques, sélecteurs et routage doivent être cohérents |
| IPsec avec interface VTI | Exposer un tunnel logique routable protégé par IPsec | Oui, via un profil IPsec | Interconnexion de plusieurs sous-réseaux, routage dynamique | Syntaxe et fonctions dépendent de la plateforme |
| GRE sur IPsec | Transporter un tunnel GRE dans IPsec | GRE seul non ; IPsec apporte la protection | Multicast ou protocoles de routage pris en charge par GRE | Surcharge plus élevée et double encapsulation possible |
| VPN d'accès distant IPsec/IKEv2 | Protéger la connexion d'un poste ou d'un utilisateur | Oui, selon le profil négocié | Télétravail, administration distante | Identité, attribution d'adresse et autorisation sont critiques |
| TLS VPN | Établir un accès via TLS, souvent au niveau applicatif ou IP selon le produit | TLS assure la protection du canal | Accès distant et applications publiées | Le périmètre varie : portail applicatif ou tunnel réseau complet |
| WireGuard | Tunnel IP utilisant un protocole cryptographique moderne | Oui | Interconnexion simple ou accès distant | Gestion des pairs, routes et identités à concevoir selon l'environnement |
| L2TP seul | Transport de trames de couche 2 | Pas nécessairement | Compatibilité ou anciens environnements | Ne pas le traiter comme un mécanisme de confidentialité autonome |
| GRE seul | Encapsulation générique de paquets | Non | Routage et transport logique | Un observateur du chemin peut examiner les données non protégées |

Le choix dépend des contraintes d'exploitation, de l'interopérabilité, des fonctions de routage nécessaires, des exigences de conformité, de la mobilité des pairs, de la capacité de supervision et de la compatibilité avec les équipements. Une technologie plus riche n'est pas toujours la meilleure si l'équipe ne sait pas l'exploiter. À l'inverse, choisir un tunnel simplifié sans authentification ou chiffrement adaptés peut exposer les données. Il faut rédiger les exigences avant de sélectionner la solution.

### 1.3. IPsec : politiques, associations de sécurité et paquets protégés

IPsec est un cadre de sécurité au niveau IP. Il s'appuie notamment sur des politiques qui déterminent quels paquets doivent être protégés, sur des associations de sécurité (*Security Associations*, SA) qui précisent comment le trafic sera traité, et sur ESP (*Encapsulating Security Payload*) pour protéger le trafic utilisateur. IKEv2 sert à authentifier les pairs et à négocier les paramètres nécessaires aux associations de sécurité.

Une SA est un ensemble d'informations qui décrivent, pour un sens et un contexte donnés, les algorithmes, clés, durées de vie et paramètres de protection à utiliser. Une SA IPsec n'est pas une connexion TCP. Les SA ESP sont directionnelles : un trafic de A vers B et un trafic de B vers A sont normalement protégés par des associations correspondantes dans chaque direction. Les interfaces et commandes de supervision peuvent afficher séparément les nombres de SA entrantes et sortantes.

Le vocabulaire historique parle parfois de « phase 1 » et de « phase 2 » pour expliquer IKE et la négociation du trafic. Cette terminologie peut aider à comprendre des documents anciens, mais IKEv2 emploie plus précisément les notions d'IKE SA et de CHILD SA. L'IKE SA protège les échanges de contrôle IKE entre les pairs. Une CHILD SA protège les flux de données IPsec et peut être créée lors de l'établissement initial ou ajoutée ensuite. Il faut donc interpréter les états de la plateforme au lieu de supposer que tous les équipements exposent exactement la même séquence de « phases ».

Dans une politique IPsec classique, des sélecteurs peuvent décrire le trafic à protéger, par exemple le préfixe du site A vers celui du site B. Avec une interface de tunnel routée, la sélection de destination est souvent gérée par la table de routage : le paquet est dirigé vers l'interface virtuelle et le profil IPsec protège ce qui traverse le tunnel. Ce modèle route-based simplifie certains scénarios avec plusieurs préfixes ou des protocoles de routage, mais ne supprime pas le besoin de filtrer les destinations autorisées.

```text
             PLAN DE CONTRÔLE IKEv2
        identité / algorithmes / création de clés
       [Passerelle A] <----------------> [Passerelle B]
             |                                |
             | crée SA ESP                   | crée SA ESP
             v                                v
  Réseau A --+==== paquet protégé IPsec =====+-- Réseau B
             |     plan de données           |
             +------ compteurs / journaux ----+
```

> **Piège :** Une IKE SA établie ne prouve pas qu'un trafic métier est autorisé ni même qu'une CHILD SA adaptée est active. Vérifie les associations de données, les sélecteurs, les compteurs encapsulés/décapsulés, les routes et les règles de filtrage des deux côtés.

### 1.4. IKEv2 : négociation et authentification

IKEv2 réalise la négociation des capacités, l'authentification mutuelle selon le profil et la création des associations. Les deux extrémités doivent trouver des propositions compatibles. Les paramètres comprennent notamment des algorithmes de chiffrement, une fonction d'intégrité lorsque le mode de chiffrement l'exige, des groupes d'échange de clés, des durées de vie et des méthodes d'authentification. Les détails varient selon l'implémentation et les fonctions activées.

Il ne suffit pas que chaque pair « utilise AES ». Les suites doivent être compatibles dans leur combinaison exacte. AES-GCM, par exemple, est un chiffrement authentifié qui combine confidentialité et intégrité ; dans ce cas, on ne configure généralement pas une fonction d'intégrité séparée pour le trafic ESP comme on le ferait avec un chiffrement de type AES-CBC associé à un HMAC. La liste exacte d'algorithmes disponibles et leur niveau de recommandation doivent être vérifiés dans la documentation courante du fournisseur et dans les recommandations IETF pertinentes.

Les méthodes d'authentification courantes comprennent un secret partagé (*pre-shared key*, PSK) et les certificats avec signatures numériques. Une PSK est facile à comprendre pour un petit laboratoire, mais sa gestion devient risquée si elle est réutilisée sur de nombreux pairs, stockée en clair dans des fichiers ou partagée à des personnes qui n'en ont pas besoin. Les certificats permettent une identité propre à chaque équipement et une révocation centralisée, mais nécessitent une infrastructure de clés publiques, la protection des clés privées et le suivi des expirations.

Le nom d'identité annoncé par un pair n'est pas toujours identique à l'adresse IP externe. Un pair dynamique peut changer d'adresse publique ; un certificat peut identifier un nom DNS ou une autre identité. Il faut accorder la confiance selon une règle claire : identité attendue, chaîne de certification, validité temporelle, usages de clé et éventuellement correspondance de nom. Autoriser simplement toute adresse ou toute identité sans autre restriction peut étendre excessivement la surface d'accès.

La négociation suit une séquence conceptuelle :

1. Les pairs échangent des propositions et établissent un secret partagé à partir d'un échange de clés.
2. Ils authentifient leurs identités avec la méthode configurée.
3. Ils établissent et entretiennent l'IKE SA.
4. Ils négocient une CHILD SA pour le trafic protégé, avec les sélecteurs ou la politique associés.
5. Ils renouvellent les clés avant ou au terme des durées de vie et suppriment les états qui ne sont plus nécessaires.

Cette séquence n'est pas une recette complète de paquets. Elle représente les responsabilités afin de donner du sens aux journaux et aux états de la plate-forme.

### 1.5. Chiffrement, intégrité, échange de clés et PFS

La confidentialité empêche un observateur qui ne possède pas les clés de lire le contenu protégé. L'intégrité permet de détecter des modifications non autorisées, et l'authentification des données rattache les données reçues à la SA qui les protège. Ces objectifs sont distincts. Un système doit choisir une suite cryptographique appropriée qui fournit les services attendus sans mélange incohérent de paramètres.

Les suites à chiffrement authentifié comme AES-GCM sont courantes dans des conceptions IPsec modernes, mais la disponibilité et le niveau d'efficacité dépendent du matériel. AES-CBC avec un mécanisme d'intégrité peut encore apparaître dans des environnements interopérables existants ; cela ne signifie pas qu'il faut le préférer automatiquement à un mode plus récent. Les algorithmes historiques faibles ou obsolètes doivent être évités, notamment lorsque les recommandations des standards les déprécient. Il faut examiner les capacités des deux pairs et choisir un profil restreint et explicite plutôt que conserver une liste très large uniquement pour « faire marcher » la négociation.

L'échange de clés Diffie-Hellman ou ses variantes permet aux parties de dériver un secret sans envoyer directement ce secret en clair sur le réseau. Le groupe choisi influe sur la sécurité et la charge de calcul. La *Perfect Forward Secrecy* (PFS) désigne une propriété qui limite l'impact d'une compromission de clés à long terme sur la confidentialité d'anciens échanges, selon le mécanisme et les clés effectivement utilisées. Lorsque la politique impose PFS pour les SA de données, les deux extrémités doivent être configurées de façon compatible.

Les durées de vie des SA et des clés ne doivent pas être traitées comme des nombres universels. Elles sont liées au profil de sécurité, aux capacités des équipements, à la charge et aux politiques d'exploitation. Une durée trop courte peut augmenter les renégociations et les risques de microcoupure sur certaines plateformes ; une durée trop longue peut aller à l'encontre des exigences de protection. Il faut documenter le choix, le tester et superviser les renouvellements.

> **Danger :** Ne baisse pas la sécurité cryptographique en production simplement parce que la négociation échoue. Commence par comparer les paramètres et les journaux des deux pairs. Réintroduire des algorithmes faibles pour préserver une interopérabilité de circonstance peut rendre le tunnel vulnérable. Toute exception temporaire doit avoir un propriétaire, une date d'expiration et un plan de retrait.

### 1.6. VPN route-based et policy-based

Un VPN *policy-based* détermine le trafic à protéger à partir de règles ou de sélecteurs, souvent définis par des couples de préfixes locaux et distants. Historiquement, cette approche est courante avec les cartes crypto (*crypto maps*) sur les routeurs Cisco. Elle peut convenir à des liaisons simples et à des partenaires dont les sélecteurs sont connus à l'avance.

Un VPN *route-based* associe la protection IPsec à une interface virtuelle. La table de routage dirige les paquets vers cette interface ; le tunnel peut recevoir une adresse, transporter plusieurs préfixes et, selon le produit, prendre part à un protocole de routage. Les interfaces IPsec virtuelles sont souvent appelées VTI (*Virtual Tunnel Interface*). Dans certains produits Cisco, les options de tunnel et de profil s'appellent `tunnel mode ipsec ipv4` et `tunnel protection ipsec profile`, mais les détails varient selon IOS/IOS XE, les générations et la fonction employée.

| Dimension | Policy-based | Route-based / VTI |
|---|---|---|
| Sélection courante | Sélecteurs de sous-réseaux et règles crypto | Table de routage vers l'interface virtuelle |
| Ajout de préfixes | Peut nécessiter de modifier les sélecteurs et les deux pairs | Souvent géré par la route, sous réserve des politiques de sécurité |
| Routage dynamique | Peut être limité ou nécessiter une construction supplémentaire | Souvent plus naturel sur l'interface du tunnel |
| Dépannage | Examiner les sélecteurs et les règles de chiffrement | Examiner la route, l'état de l'interface et le profil IPsec |
| Compatibilité | Très largement présente dans les équipements classiques | Dépend des versions et des fonctions du fournisseur |
| Risque typique | Un sélecteur mal aligné exclut le flux | Une route trop large envoie des destinations inattendues vers le tunnel |

Le choix doit être cohérent de bout en bout. Mélanger sans justification un côté qui attend des sélecteurs très précis et un côté qui présente un tunnel routé peut conduire à des négociations partielles ou à une sélection de trafic inattendue. Avant le déploiement, confirme le modèle supporté par les deux plateformes, les capacités de routage, le comportement NAT et les restrictions de sécurité.

### 1.7. GRE protégé par IPsec

GRE permet d'encapsuler des paquets dans un tunnel logique. Il peut être utilisé pour transporter des protocoles de routage ou certains trafics multicast que la politique IPsec de base ne transporte pas directement dans le scénario choisi. GRE seul ne chiffre pas le contenu ; il est donc courant de protéger GRE avec IPsec lorsque le tunnel passe sur un réseau non fiable.

Avec GRE sur IPsec, le paquet applicatif est d'abord transporté dans GRE, puis le paquet résultant est protégé par IPsec. Ce mécanisme facilite certains designs, mais chaque enveloppe consomme de la place dans le MTU. La surcouche est plus importante que pour une conception IPsec qui protège directement les paquets sélectionnés. Il faut donc calculer le MTU effectif, régler éventuellement le MSS TCP et tester les paquets non TCP ainsi que les messages ICMP nécessaires à la découverte de MTU.

L'utilisation de GRE n'implique pas qu'un protocole de routage doit être activé. Il est parfaitement possible d'utiliser des routes statiques sur un tunnel ; inversement, transporter OSPF ou BGP n'est pertinent que si les besoins opérationnels le justifient. Le routage dynamique apporte une convergence et une gestion des chemins utiles dans certains environnements, mais il nécessite des politiques de voisinage, une authentification lorsqu'elle est prise en charge, des filtres de préfixes et une supervision spécifique.

### 1.8. Routage statique, OSPF et BGP sur le VPN

La route doit correspondre à la politique VPN. Dans un tunnel route-based, une route vers le préfixe distant pointe souvent vers l'interface virtuelle. Dans un VPN policy-based, le routage amène généralement le trafic vers l'interface externe, tandis que la politique crypto sélectionne le flux à protéger. Les détails exacts varient par produit ; il est essentiel de distinguer route de transport vers l'adresse publique du pair et route applicative vers le réseau distant.

Un VPN peut exiger deux familles de routes : les routes qui font passer le trafic externe du tunnel vers le fournisseur d'accès, et les routes qui dirigent le trafic interne vers le tunnel. Une route par défaut mal conçue peut envoyer l'adresse externe du pair dans le tunnel lui-même, créant une récursion ou empêchant le tunnel de fonctionner. Les routes de transport doivent donc rester disponibles indépendamment des routes apprises à travers le tunnel.

Les routes statiques sont simples si les préfixes sont peu nombreux et stables. OSPF peut être adapté à une topologie interne maîtrisée ; BGP est souvent utile lorsque plusieurs sites, chemins, opérateurs ou domaines de routage doivent être gérés avec des politiques explicites. Dans tous les cas, ne diffuse pas aveuglément la route par défaut ou tous les préfixes internes. Configure des filtres, des préférences, des limites de nombre de routes et des contrôles de voisinage cohérents avec le besoin.

```text
Site A                                                    Site B
LAN 10.10.10.0/24                                         LAN 10.20.20.0/24
       |                                                           |
   [Routeur A]---- Tunnel VTI protégé par IPsec ----[Routeur B]
       |          IP tunnel 169.254.10.1/30          |
       |          OSPF ou routes statiques          |
       +------------- Internet / WAN ----------------+

Routes attendues :
- Route externe vers l'adresse publique du pair via le WAN
- Route interne vers 10.20.20.0/24 via Tunnel0 à A
- Route interne vers 10.10.10.0/24 via Tunnel0 à B
- Route retour et filtrage applicatif cohérents des deux côtés
```

### 1.9. NAT, NAT Traversal et pare-feu intermédiaires

IKEv2 utilise couramment UDP 500 pour la négociation. Lorsque la détection du NAT indique qu'une extrémité se trouve derrière une traduction d'adresses, IPsec peut transporter ESP dans UDP 4500 avec NAT Traversal (NAT-T). ESP natif est le protocole IP 50 ; GRE est le protocole IP 47. Ces nombres ne désignent ni des ports TCP ni des ports UDP. Un pare-feu intermédiaire doit autoriser les échanges nécessaires au transport choisi, tout en appliquant les restrictions de source et de destination possibles.

Le NAT peut aussi perturber la sélection des flux d'un VPN. Un réseau local peut être traduit avant ou après le point où la politique IPsec évalue le paquet, selon le moteur de traitement et la configuration du fournisseur. Il faut connaître le comportement précis de la plateforme. De nombreux sites utilisent une exemption NAT (*NAT exemption* ou règle de non-traduction) pour conserver les adresses internes des flux destinés au VPN, tandis que les flux Internet ordinaires subissent une traduction d'adresse. Une erreur de priorité peut traduire le trafic VPN et le faire sortir des sélecteurs configurés.

Quand le VPN échoue derrière une box ou une chaîne de NAT, ne pas se limiter à ouvrir tous les protocoles. Confirmer la route, l'adresse publique réellement vue par le pair, l'existence éventuelle de plusieurs NAT, les ports UDP nécessaires, la prise en charge de NAT-T et les journaux de détection. Un NAT peut aussi expirer une association UDP inactive : les mécanismes de maintien de connexion ou la stratégie de réouverture doivent être compris.

### 1.10. MTU, MSS, fragmentation et PMTUD

Chaque en-tête ajouté par GRE, IPsec, UDP ou d'autres encapsulations réduit la place disponible pour le paquet interne. Une interface Ethernet ayant une MTU de 1500 octets ne signifie donc pas qu'un paquet interne de 1500 octets passera sans difficulté à travers un tunnel. La surcharge exacte dépend de l'enveloppe extérieure, des options IP, de la version IPv4/IPv6, du mode ESP, du chiffrement authentifié, de l'alignement et d'éventuelles couches WAN.

La découverte de MTU du chemin (*Path MTU Discovery*, PMTUD) dépend des messages et du traitement prévu par le protocole. Un filtrage ICMP trop strict peut empêcher la source de recevoir l'indication qu'un paquet est trop grand. Le symptôme est parfois trompeur : ping avec petit paquet réussi, établissement TCP réussi, mais transfert volumineux ou certaines applications qui se figent. La connexion peut envoyer des segments qui ne traversent pas le chemin ou ne sont jamais retransmis de manière efficace.

La correction ne consiste pas à fixer arbitrairement une MTU très basse sur toutes les interfaces. Il faut mesurer le chemin, calculer la surcharge du tunnel, vérifier les messages ICMP pertinents, tester différentes tailles et appliquer le réglage au bon endroit. L'ajustement du MSS TCP peut aider les sessions TCP, mais ne résout pas tous les flux UDP ni tous les problèmes PMTUD. Le MSS ne remplace pas une conception correcte du MTU.

> **Astuce :** En cas de transfert bloqué avec un tunnel actif, compare les petits et grands paquets et les compteurs ESP, puis examine les messages ICMP liés à la MTU. Note l'encapsulation exacte avant de calculer une valeur. Teste chaque changement avec un retour arrière prêt, et vérifie plusieurs applications, pas seulement une requête ping.

### 1.11. VPN d'accès distant : identité, routes et autorisations

Un VPN d'accès distant ajoute plusieurs fonctions au tunnel : authentification de l'utilisateur, attribution d'une adresse virtuelle, distribution éventuelle de routes et de paramètres DNS, association de l'utilisateur à un groupe ou un rôle, et application d'une politique de sécurité. L'authentification réussie ne doit pas automatiquement autoriser l'accès à l'ensemble du réseau interne. Le modèle de moindre privilège impose de limiter les destinations et services aux besoins de l'utilisateur.

L'authentification multifacteur (MFA) réduit le risque lié au vol d'un seul facteur, mais elle ne protège pas une session déjà compromise et ne remplace pas l'hygiène du poste client. Le contrôle de conformité du terminal, la segmentation des prestataires, la durée des accès, le retrait des comptes inactifs et les journaux d'accès complètent la politique de VPN. En particulier, un poste personnel ou non maîtrisé ne devrait pas obtenir le même périmètre qu'une station d'administration gérée.

Le *split tunneling* dirige uniquement certains préfixes vers le VPN et laisse d'autres flux suivre la connectivité locale du poste. Il peut réduire la charge de la passerelle et améliorer les performances, mais crée deux chemins réseau depuis le poste et peut compliquer les contrôles de sécurité. Le *full tunneling* dirige une part beaucoup plus large du trafic vers la passerelle de l'organisation, où des politiques centralisées peuvent s'appliquer ; il augmente la consommation de bande passante et dépend de la capacité du concentrateur. La décision doit être explicite, justifiée par le risque et documentée.

Les routes et paramètres DNS poussés au client sont aussi importants que l'établissement de la session. Un utilisateur peut être authentifié et disposer d'une adresse VPN, mais ne pas joindre une application à cause d'une route absente ou d'une résolution interne incorrecte. Inversement, une route trop large peut ouvrir un chemin vers des ressources que l'utilisateur ne devrait pas atteindre. Tester l'accès distant nécessite donc une matrice d'autorisations par rôle.

### 1.12. Topologies multi-sites et chemins de secours

Une topologie en étoile, dans laquelle les agences se connectent à un siège ou à un concentrateur, simplifie souvent les règles de sécurité et la sortie vers les applications centrales. Elle peut toutefois créer un point de concentration de la bande passante et une dépendance au site central. Une topologie maillée peut offrir des chemins directs entre sites, mais augmente le nombre de tunnels, les dépendances de routage et la complexité opérationnelle.

Le nombre de tunnels peut croître rapidement. Pour un maillage complet de N sites, le nombre de liaisons pair à pair est N × (N − 1) / 2. Avec 10 sites, cela représente 45 relations de tunnel possibles ; avec 20 sites, 190. Les services de gestion centralisée, les VPN dynamiques ou les technologies SD-WAN peuvent réduire la charge manuelle, mais ils ajoutent leurs propres modèles de contrôle, de confiance et de dépannage. Il faut analyser le besoin avant de choisir la topologie.

La redondance peut être obtenue avec deux accès Internet, plusieurs concentrateurs, des tunnels vers des pairs différents ou des mécanismes de basculement. Mais posséder deux tunnels ne suffit pas à démontrer la résilience. Il faut définir ce qui est surveillé (interface, route, pair, sonde applicative), comment la décision de basculement est prise, quels délais sont acceptables, et si les sessions applicatives se rétablissent. Un tunnel secondaire qui utilise le même opérateur, la même alimentation ou le même équipement amont peut partager un risque de panne majeur.

La haute disponibilité nécessite aussi de comprendre ce qui est synchronisé : état du pair, associations de sécurité, clés, sessions, compteurs ou seules configurations. Certaines architectures imposent une nouvelle négociation et peuvent perdre des sessions lors d'un basculement. Cette conséquence doit être validée en laboratoire et documentée dans le niveau de service attendu.

### 1.13. Observabilité et indicateurs opérationnels

Une supervision utile collecte plusieurs types d'indicateurs : disponibilité de l'interface WAN, état du pair IKE, état des CHILD SA ou SA ESP, compteurs de paquets protégés, erreurs d'authentification, retransmissions ou expirations, latence, perte, utilisation CPU, capacité cryptographique et débit réel. Un seul état vert ne représente pas l'ensemble du service.

Les compteurs encapsulés augmentent lorsque le routeur protège et envoie des paquets. Les compteurs décapsulés augmentent lorsque des paquets protégés arrivent et sont traités. Si l'un augmente sans l'autre, le problème peut se situer dans le retour, le routage, le pair distant, le filtrage ou l'application. Les noms de compteurs varient selon la plateforme ; l'objectif est de comparer les deux directions et de corréler la mesure avec un test contrôlé.

Les journaux IKE et IPsec peuvent révéler une proposition rejetée, une identité non reconnue, une authentification échouée, un sélecteur incompatible ou un renouvellement en erreur. Ils peuvent aussi être trop verbeux et exposer des métadonnées sensibles. Le niveau de journalisation doit être réglé selon l'opération : augmenter temporairement le détail pour un incident, horodater les captures, recueillir les informations pertinentes puis revenir à un niveau normal. Les secrets et les clés privées ne doivent jamais être copiés dans un ticket ou un rapport d'incident.

Une alerte doit être liée à une action exploitable. Par exemple, une IKE SA qui disparaît pendant une courte fenêtre peut être normale lors d'un renouvellement ; un tunnel absent pendant plusieurs minutes alors qu'un trafic est attendu peut justifier une alerte. Il faut calibrer seuils et temporisations sur les caractéristiques du réseau pour éviter les fausses alertes et ne pas masquer les vrais incidents.

### 1.14. Menaces et modèle de confiance

Le tunnel protège les données sur un chemin donné, mais ne rend pas automatiquement les extrémités sûres. Une passerelle compromise, un poste infecté, une clé privée volée ou une politique d'autorisation trop large peut compromettre les ressources internes même si le chiffrement est solide. La sécurité du VPN doit donc être intégrée à la gestion des identités, à la segmentation, aux correctifs, à la surveillance, à la réponse aux incidents et au cycle de vie des équipements.

Les menaces à prendre en compte comprennent le vol de secret, l'utilisation d'une identité légitime par un acteur non autorisé, la force brute sur un accès distant, les algorithmes obsolètes, la confusion d'identité entre pairs, les erreurs de routage, les règles trop larges, le déni de service sur la passerelle, l'exposition d'une interface de gestion et la perte de visibilité dans les journaux.

Une politique robuste utilise des algorithmes actuellement acceptés par les standards et le fournisseur, une authentification adaptée au contexte, des secrets uniques ou une PKI correctement exploitée, une segmentation des ressources, des règles minimales et une revue périodique. Pour les équipements d'administration, employer des chemins d'accès dédiés si possible, limiter les sources autorisées, exiger un contrôle d'identité fort et enregistrer les changements. Le VPN n'est ni un substitut à un pare-feu ni une raison d'accorder une confiance implicite à tout le réseau distant.

---

## 2. Configuration et pratique

Les exemples ci-dessous illustrent une interconnexion route-based IPsec sur Cisco IOS/IOS XE. Ils servent de support de laboratoire et doivent être adaptés à la version, à la plate-forme, à la topologie, à la politique cryptographique et aux exigences du site. Les adresses publiques des exemples utilisent les plages de documentation et ne sont pas destinées à être utilisées comme des adresses de production.

### 2.1. Scénario du laboratoire

Deux sites doivent échanger du trafic entre leurs réseaux LAN. Site A : `10.10.10.0/24`, adresse externe de laboratoire `198.51.100.1`. Site B : `10.20.20.0/24`, adresse externe `203.0.113.2`. Le tunnel virtuel utilise `169.254.100.0/30`. Les passerelles disposent déjà d'une connectivité WAN et doivent pouvoir joindre l'adresse externe du pair sans envoyer cette destination dans le tunnel.

```text
 Hôte A            Routeur A                  Routeur B             Hôte B
10.10.10.10   198.51.100.1                 203.0.113.2          10.20.20.20
     |              |                            |                     |
     +--- LAN A ----+==== IPsec / Tunnel0 =======+------ LAN B --------+
                    169.254.100.1/30  .2/30
```

Avant la configuration, remplir une fiche de conception : sous-réseaux protégés, adresses publiques, modèle route-based ou policy-based, identité des pairs, méthode d'authentification, suites autorisées, MTU cible, règles de pare-feu externes, routes attendues, capacité requise et processus de retour arrière. Cette fiche est aussi utile pour la revue de changement et pour le dépannage futur.

### 2.2. Paramètres à faire correspondre

| Élément | Site A | Site B | Vérification |
|---|---|---|---|
| Adresse publique du pair | `203.0.113.2` | `198.51.100.1` | Adresse joignable par le WAN |
| Identité distante attendue | Identité de B | Identité de A | Doit correspondre à l'identité réellement présentée |
| Authentification | PSK de laboratoire ou certificats | Paramètres compatibles | Méthode et secret/certificat valides |
| Propositions IKE | Profil autorisé | Profil compatible | Chiffrement, PRF/intégrité, groupe et version |
| Paramètres ESP | Profil de données | Profil compatible | Chiffrement authentifié ou combinaison compatible |
| Tunnel interne | `169.254.100.1/30` | `169.254.100.2/30` | Adresses uniques et non chevauchantes |
| Réseau LAN | `10.10.10.0/24` | `10.20.20.0/24` | Aucun chevauchement avec le réseau distant |
| Route distante | Vers `10.20.20.0/24` | Vers `10.10.10.0/24` | Trafic interne dirigé vers le tunnel |
| Filtrage | Autorisations explicites | Autorisations explicites | Flux nécessaires seulement |

### 2.3. Exemple conceptuel de configuration IKEv2/IPsec

Les profils ci-après montrent les éléments à configurer sur chaque pair. Des noms de commandes ou champs peuvent varier selon la version. Il faut choisir des algorithmes conformément aux recommandations courantes de l'organisation et aux capacités supportées ; l'exemple de groupe Diffie-Hellman est à considérer comme une valeur illustrative, pas comme une recommandation universelle pour toutes les générations d'équipements.

Exemple de base pour le site A :

```text
! Exemple pédagogique Cisco IOS/IOS XE : valider la syntaxe sur la version cible
crypto ikev2 proposal IKEV2-PROP
 encryption aes-cbc-256
 integrity sha256
 group 14
!
crypto ikev2 policy IKEV2-POLICY
 proposal IKEV2-PROP
!
crypto ikev2 keyring VPN-KEYRING
 peer SITE-B
  address 203.0.113.2
  pre-shared-key local <SECRET_SITE_A>
  pre-shared-key remote <SECRET_SITE_B>
!
crypto ikev2 profile IKEV2-PROFILE
 match identity remote address 203.0.113.2 255.255.255.255
 authentication remote pre-share
 authentication local pre-share
 keyring local VPN-KEYRING
!
crypto ipsec transform-set ESP-TRANSFORM esp-aes 256 esp-sha256-hmac
 mode tunnel
!
crypto ipsec profile IPSEC-PROFILE
 set transform-set ESP-TRANSFORM
 set ikev2-profile IKEV2-PROFILE
!
interface Tunnel0
 ip address 169.254.100.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile IPSEC-PROFILE
```

**Important :** `aes-cbc-256` avec `sha256-hmac` est montré ici pour illustrer la séparation des paramètres IKE et ESP et pour offrir un exemple largement reconnaissable dans les maquettes Cisco ; cela ne remplace pas une revue cryptographique. Dans une conception actuelle, privilégier les suites approuvées et prises en charge telles que les modes AEAD appropriés lorsque les deux pairs les supportent, plutôt que copier ce bloc sans évaluation. Le champ `group 14` figure pour la même raison pédagogique et doit être comparé aux recommandations les plus récentes et aux capacités de la plate-forme. Ne jamais utiliser des secrets explicites dans un document partagé : les chaînes entre chevrons sont des espaces réservés.

Le site B reprend la logique en inversant les adresses, les identités et les adresses de tunnel. Le pair de B pointe vers `198.51.100.1`, la source du tunnel est l'interface WAN de B et l'adresse de `Tunnel0` est `169.254.100.2/30`. Les deux côtés doivent négocier des paramètres compatibles ; les noms locaux de profils peuvent être différents, mais ils doivent correspondre fonctionnellement.

Sur certaines versions et certains modèles, le profil peut utiliser une configuration IKEv2 différente, une identité FQDN, une authentification par certificat, un groupe dynamique ou une fonction FlexVPN. Ne force pas la correspondance uniquement par adresse si l'architecture utilise des pairs dynamiques ou des certificats. Vérifie le guide de la version qui tourne réellement sur l'équipement.

### 2.4. Routage à travers le tunnel

Si l'environnement utilise des routes statiques, une idée de configuration sur A consiste à envoyer le réseau B à travers `Tunnel0`, et symétriquement sur B. Exemple conceptuel :

```text
! Site A
ip route 10.20.20.0 255.255.255.0 Tunnel0
!
! Site B
ip route 10.10.10.0 255.255.255.0 Tunnel0
```

Cette route ne remplace pas la route de transport vers l'adresse publique du pair. Il faut conserver un acheminement WAN valable pour `203.0.113.2` depuis A et pour `198.51.100.1` depuis B. Si une route par défaut passe elle-même par `Tunnel0`, une route plus spécifique vers le pair externe peut être nécessaire pour éviter une récursion. Le comportement exact dépend du système de routage et de la conception de la VTI.

Après configuration, examiner la table de routage avant de tester les hôtes. Une route correcte vers `10.20.20.0/24` doit pointer vers la bonne interface virtuelle ou le prochain saut prévu. Vérifier aussi le chemin retour : le routeur B doit pouvoir renvoyer `10.10.10.0/24` via son tunnel, et les hôtes doivent utiliser la passerelle locale correcte. Un trafic qui entre dans le tunnel sans route de retour peut produire des compteurs asymétriques et des sessions applicatives incomplètes.

### 2.5. GRE sur IPsec et routage dynamique

Pour un cas nécessitant GRE, le tunnel logique peut transporter le routage dynamique, puis être protégé avec un profil IPsec. Exemple conceptuel abrégé :

```text
interface Tunnel10
 ip address 172.31.255.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 tunnel mode gre ip
 tunnel protection ipsec profile IPSEC-PROFILE
```

Les commandes disponibles et les combinaisons autorisées dépendent du produit et du mode de tunnel utilisé. Certaines implémentations configurent un tunnel IPsec VTI sans GRE ; d'autres combinent explicitement les deux. Ne superpose pas GRE et IPsec sans besoin réel, car la surcharge supplémentaire réduit la MTU et complique le diagnostic.

Si OSPF est utilisé sur l'interface de tunnel, établir des exigences explicites : types de réseau, timers, authentification si prise en charge, filtrage des préfixes, zones, métrique, passive-interface et comportement de convergence. OSPF ne doit pas devenir un moyen de diffuser par erreur la route par défaut ou des routes sensibles. Dans un déploiement BGP, employer des filtres d'entrée/sortie, des politiques de préférence, une limite de préfixes et une procédure de retrait du pair.

### 2.6. Exemptions NAT et politique de pare-feu

Dans de nombreux réseaux, le trafic Internet ordinaire des postes est traduit par NAT/PAT alors que les flux destinés au VPN conservent leurs adresses internes. La règle de non-traduction doit correspondre à la conception du VPN et à l'ordre de traitement du NAT sur la plate-forme. Ne copie pas un exemple trouvé pour un autre équipement sans comprendre si le NAT se produit avant ou après la sélection IPsec.

La passerelle et les pare-feu intermédiaires doivent autoriser le transport réellement utilisé. Les flux courants comprennent IKE sur UDP 500, NAT-T sur UDP 4500 et, lorsque la topologie le permet sans NAT-T, ESP comme protocole IP 50. GRE est protocole IP 47. Ces numéros ne sont pas des ports TCP/UDP. Un pare-feu à état peut gérer les retours correspondants, mais les politiques précises dépendent du fournisseur, des interfaces et de la manière dont le VPN est terminé.

Il ne faut pas ouvrir IKE depuis l'ensemble d'Internet vers toutes les passerelles quand des sources attendues peuvent être restreintes. Pour un pair à adresse stable, la liste des pairs attendus peut être limitée au niveau du filtrage. Pour les clients mobiles, l'ouverture doit être accompagnée de mécanismes d'authentification solides, d'une protection contre les tentatives abusives et d'une politique d'autorisation stricte.

### 2.7. Commandes de vérification Cisco

Les commandes ci-dessous sont couramment rencontrées dans les environnements Cisco IOS/IOS XE. Les options exactes et la disponibilité dépendent de la version :

```text
show crypto ikev2 sa
show crypto ipsec sa
show crypto session detail
show interfaces Tunnel0
show ip interface brief
show ip route
show ip route 10.20.20.0
show access-lists
show logging
```

Elles servent à répondre à des questions différentes : le pair IKE est-il établi ? Des SA ESP existent-elles ? Les compteurs de chiffrement et déchiffrement augmentent-ils ? L'interface virtuelle est-elle opérationnelle ? La route choisit-elle le tunnel ? Une ACL ou une politique de pare-feu bloque-t-elle le flux ? Les journaux donnent-ils une cause de rejet ?

Procéder par tests contrôlés. Relever les compteurs, générer un flux précis depuis un hôte du LAN A vers une destination du LAN B, puis relire les compteurs. Un ping émis directement par le routeur peut emprunter une autre interface ou utiliser une adresse source différente de celle de l'hôte ; préciser la source lors des tests et toujours vérifier le chemin retour. Les captures doivent être réalisées sur les points utiles et protégées comme des données d'exploitation, car elles peuvent inclure des adresses internes ou des métadonnées sensibles.

### 2.8. Procédure de validation avant production

Une validation ne doit pas se limiter à vérifier une seule requête ping. La checklist suivante donne une base de tests. Les résultats attendus doivent être consignés dans un ticket de changement, un cahier de test ou une procédure d'exploitation.

| Test | Résultat attendu | Preuve à collecter |
|---|---|---|
| Connectivité WAN entre pairs | Adresses externes joignables selon la politique | Route externe, capture ou sonde WAN |
| Négociation IKEv2 | IKE SA établie et identité correcte | État de SA et journal IKE |
| Négociation IPsec | CHILD SA/SA ESP appropriées présentes | État ESP et paramètres négociés |
| Trafic A vers B | Paquets encapsulés puis reçus | Compteurs et test applicatif |
| Trafic B vers A | Retour symétrique selon la conception | Compteurs inverse, routes de retour |
| Flux non autorisé | Bloqué selon la matrice de sécurité | Test négatif et journal de refus |
| DNS interne | Résolution attendue pour les clients autorisés | Requête DNS et paramètres reçus |
| Transfert volumineux | Pas de blocage dû à MTU/MSS | Test de taille, capture, observation ICMP |
| Renouvellement des clés | Nouveau SA sans rupture excessive | Journaux et mesure de session |
| Défaillance d'un lien | Basculement selon le SLA | Test contrôlé et temps de convergence |
| Redémarrage ou reconnexion | Rétablissement automatique prévu | Trace horodatée, test de récupération |
| Sauvegarde / retour arrière | Configuration récupérable | Fichier de sauvegarde et procédure testée |

Une matrice de test doit aussi distinguer les différents types de flux : TCP, UDP, ICMP, DNS, gestion, applications métier et protocoles de routage. Autoriser tout le trafic entre les deux LAN peut rendre le premier test très facile, mais ne valide pas la politique de segmentation. Les tests négatifs sont essentiels pour vérifier que les règles de sécurité fonctionnent réellement.

---

## 3. Dépannage et sécurité

### 3.1. Une méthode en couches

Le dépannage VPN devient plus efficace lorsqu'on suit une progression stable, de l'infrastructure vers l'application. La méthode suivante limite les modifications au hasard et permet de documenter l'endroit où le paquet disparaît.

1. **Transport WAN** : vérifier l'interface, l'adressage, la route externe vers le pair, le NAT et les pertes. Sans transport, IKE ne peut pas se négocier.
2. **IKE et identité** : examiner les propositions, l'identité distante, la méthode d'authentification, la validité du certificat ou la PSK, les groupes et les journaux.
3. **Associations ESP** : vérifier l'existence des SA de données, les suites cryptographiques, les sélecteurs, les durées de vie et les compteurs.
4. **Routage et NAT interne** : vérifier la route vers les réseaux distants, l'absence de récursion, le NAT exemption si requis et les routes de retour.
5. **Filtrage et politique applicative** : examiner les ACL, le pare-feu, les politiques de zone, les règles de sécurité des hôtes et les autorisations utilisateur.
6. **Services et performances** : vérifier DNS, MTU/MSS, latence, perte, fragmentation, charge CPU, débit cryptographique et comportement des applications.

Ne change qu'une variable à la fois si le service est encore partiellement opérationnel. Avant chaque changement, consigner l'état courant ; après, répéter exactement le même test. Sans cela, on ne sait pas si l'amélioration vient du changement effectué, d'un renouvellement de SA ou d'une fluctuation du réseau.

### 3.2. IKE ne se négocie pas

Quand aucune IKE SA n'apparaît, commencer par la connectivité vers l'adresse publique du pair et par le filtrage des paquets de négociation. Vérifier que le pare-feu externe autorise le protocole utilisé : généralement UDP 500 et, selon le NAT-T, UDP 4500. Ne pas ouvrir TCP/50 pour « autoriser ESP » : ESP est un numéro de protocole IP, non un port TCP.

Les causes d'échec courantes sont une mauvaise adresse de pair, une identité distante qui ne correspond pas, une PSK erronée, un certificat expiré, une chaîne de certification non reconnue, une date incorrecte, ou des propositions cryptographiques incompatibles. Un échec d'authentification doit être distingué d'un échec de compatibilité : les journaux peuvent révéler si aucun algorithme commun n'est trouvé ou si le pair a été reconnu puis rejeté.

Un certificat valide dans le navigateur d'un poste n'est pas nécessairement valide pour une passerelle VPN. Vérifier l'identité exacte, les usages de clé, la chaîne de confiance, la révocation lorsque la politique l'exige et l'heure système. Une synchronisation NTP incorrecte peut faire apparaître un certificat valide comme expiré ou pas encore valide.

Ne pas contourner le problème en supprimant toute vérification d'identité ou en autorisant n'importe quel pair. Si un fournisseur tiers ne supporte qu'un ensemble de paramètres étroit, documenter la compatibilité minimale et vérifier que les paramètres restent acceptables selon la politique de sécurité. Une exception doit être circonscrite au seul pair concerné.

### 3.3. IKE fonctionne, mais aucune SA de données n'existe

Si l'IKE SA est établie sans CHILD SA adaptée, analyser les paramètres de protection du trafic et les sélecteurs. Une divergence dans les sous-réseaux locaux et distants, une proposition ESP incompatible, une option PFS différente ou une politique qui ne correspond à aucun flux peuvent empêcher la création de l'association de données.

Sur un VPN policy-based, comparer soigneusement les préfixes source/destination vus par chaque pair. Le site A peut définir `10.10.10.0/24` vers `10.20.20.0/24`, tandis que le site B doit avoir l'équivalent inversé. Si l'une des extrémités inclut seulement un `/25`, l'autre moitié du réseau ne sera pas nécessairement protégée. Si le NAT modifie les adresses avant leur comparaison aux sélecteurs, les paramètres configurés peuvent ne plus correspondre aux paquets réels.

Sur un VPN route-based, ne pas supposer que la présence de `Tunnel0` prouve qu'une association ESP existe. Vérifier le profil attaché, les paramètres IKEv2, l'état du tunnel et les routes. Certaines plateformes créent la SA à la demande lorsqu'un trafic admissible apparaît ; la méthode de déclenchement doit être comprise avant de conclure à une panne.

### 3.4. Tunnel actif, trafic absent

Des compteurs ESP nuls signifient généralement qu'aucun trafic correspondant n'est protégé ou que le test ne passe pas par le point attendu. Vérifier la source utilisée par le test, la route vers le réseau distant, la politique crypto, les sélecteurs, l'ACL sur l'interface et le chemin de retour. Un ping lancé depuis le routeur avec sa propre adresse WAN n'est pas équivalent au ping émis depuis un hôte du LAN.

Si les compteurs encapsulés augmentent à A mais pas les compteurs décapsulés à B, l'enveloppe peut être bloquée ou routée vers une autre extrémité, ou la protection ne correspond pas à ce que B attend. Contrôler les adresses externes, le transport NAT-T, les ACL WAN, les captures et les journaux du pair distant. Si les compteurs décapsulés augmentent à B mais que l'hôte ne répond pas, suivre le paquet à l'intérieur du site B : route LAN, VLAN, ACL, pare-feu local, passerelle de l'hôte et service cible.

Si les compteurs augmentent dans les deux directions mais que l'application reste inaccessible, concentrer l'enquête sur les réseaux internes. Tester la résolution DNS, le port applicatif, la route de retour depuis le serveur, les règles de pare-feu et les journaux côté serveur. Un tunnel protège le transport ; il n'autorise pas automatiquement le service applicatif ni ne corrige les erreurs de l'hôte.

### 3.5. Problèmes NAT et sélecteurs

Une exemption NAT mal positionnée peut transformer une adresse source attendue avant que la sélection du trafic VPN ne soit appliquée. Il faut connaître l'ordre du traitement NAT et du traitement IPsec sur le système en place. Une règle qui exempte les réseaux distants doit être assez précise ; une exemption générale peut supprimer un contrôle attendu ou empêcher une traduction nécessaire pour un autre service.

Pour diagnostiquer, relever les adresses source/destination avant et après la passerelle, examiner les compteurs NAT et comparer le paquet à la politique VPN. Sur une maquette, une capture à chaque interface peut montrer si l'adresse interne est conservée, traduite ou encapsulée comme prévu. En production, respecter la politique de collecte et masquer les identifiants ou métadonnées sensibles dans les rapports.

La présence de plusieurs routeurs NAT, d'une box opérateur ou d'une adresse publique dynamique peut également compliquer la connexion. NAT-T peut permettre de transporter ESP dans UDP, mais ne résout pas toutes les problématiques d'itinéraire ou d'autorisation. Vérifier la stabilité de l'adresse vue par le pair, la durée des mappages UDP et les paramètres de maintien de session pris en charge.

### 3.6. Réseaux chevauchants et route récursive

Deux sites qui utilisent le même préfixe privé, par exemple `192.168.1.0/24`, compliquent fortement la détermination de la destination. Une table de routage classique ne peut pas distinguer deux réseaux identiques simplement parce que les hôtes sont situés dans deux sites VPN différents. La meilleure solution consiste souvent à renuméroter l'un des sites avant le déploiement.

Dans certains environnements où la renumérotation est impossible, une traduction d'adresses ciblée ou un mécanisme de chevauchement peut être étudié. Cette approche ajoute de la complexité : les journaux montrent des adresses traduites, les règles applicatives doivent comprendre le mappage et le diagnostic exige de connaître le chemin avant/après traduction. Toute solution de ce type doit être testée avec des flux aller et retour et documentée avec les adresses visibles par chaque extrémité.

Une route récursive apparaît lorsque le chemin nécessaire pour atteindre le pair externe dépend du tunnel lui-même. Par exemple, une route par défaut envoyée dans `Tunnel0` peut capturer l'adresse externe du pair et empêcher le tunnel de conserver sa connectivité de transport. Il faut identifier la route la plus spécifique qui atteint le pair, vérifier la préférence de route et s'assurer que le plan de transport demeure indépendant du trafic protégé.

### 3.7. MTU, MSS et symptômes applicatifs

Si les petites requêtes passent mais que les transferts volumineux stagnent, vérifier l'encapsulation et la MTU avant de supposer un problème de chiffrement. GRE, ESP, UDP NAT-T et les en-têtes extérieurs diminuent la taille utile du paquet. Le chemin peut aussi inclure un lien opérateur avec une MTU inférieure à celle du LAN. Une politique ICMP qui bloque les messages nécessaires à PMTUD peut empêcher la source de réduire correctement la taille des paquets.

Un test de taille graduelle peut aider à identifier un seuil, mais il faut tenir compte du type de paquet et de la manière dont le système de test utilise le bit DF. Les commandes de ping et leurs options changent selon les systèmes. Tester plusieurs directions et plusieurs applications ; ne pas extrapoler le résultat d'un seul ping à l'ensemble du trafic.

Ajuster la MTU du tunnel ou le MSS TCP peut être approprié après mesure et calcul. Le MSS ne corrige pas tous les flux UDP, ni les problèmes de fragmentation IP, ni un ICMP indispensable qui serait filtré. Une valeur très faible peut réduire l'efficacité du transport et augmenter le nombre de paquets ; il vaut mieux rechercher la bonne taille plutôt que de choisir une valeur arbitraire.

### 3.8. VPN instable, reconnexions et haute disponibilité

Les renégociations, les pertes de pair, les expirations de certificats, les changements de route, les expirations NAT et les interruptions WAN peuvent provoquer des coupures. Pour établir une corrélation, aligner les horodatages des journaux des deux passerelles, des interfaces WAN, du protocole de routage et de la supervision applicative. Une seule ligne de log peut indiquer le symptôme sans montrer la cause initiale.

Les mécanismes de détection de pair mort (*Dead Peer Detection*, DPD) ou des mécanismes proches aident à repérer un pair qui ne répond plus. Des temporisations trop agressives peuvent déclarer à tort une panne en cas de congestion ou de charge CPU. À l'inverse, des temporisations trop longues rallongent le temps de basculement. Elles doivent être choisies et validées dans le contexte des délais attendus, pas copiées sans examen.

Dans une architecture haute disponibilité, tester explicitement la perte du WAN primaire, la panne du pair, la perte d'une route dynamique, le redémarrage d'un équipement et la perte du lien de synchronisation si elle existe. Mesurer non seulement le retour du tunnel, mais aussi la récupération des applications, la durée d'interruption, la perte des sessions et la cohérence des journaux. Une bascule qui rétablit IKE mais laisse une route incorrecte n'est pas un rétablissement complet du service.

### 3.9. Sécurité opérationnelle et cycle de vie

La gestion des secrets doit être formalisée. Les PSK doivent être longues, uniques par relation de confiance, stockées dans un coffre ou un système de gestion adapté et renouvelées selon la politique. Les clés privées de certificats doivent être protégées avec des contrôles d'accès stricts. Les comptes de gestion ne doivent pas partager les mêmes identifiants que les utilisateurs ordinaires et les accès d'administration doivent être limités aux sources et rôles nécessaires.

Le cycle de vie comprend l'inventaire des pairs, la validation des versions, le suivi des certificats, la rotation des clés, les tests de restauration et le retrait des tunnels inutilisés. Un VPN oublié peut exposer un chemin de confiance longtemps après la fin d'un contrat. Les configurations doivent avoir un propriétaire et un motif métier, avec une date de revue. Les routes, règles d'accès et identités doivent être supprimées lorsque la relation de confiance est terminée.

La collecte des journaux doit fournir de quoi reconstruire un incident : identité, heure, pair, résultat d'authentification, changement d'état, volume ou compteur pertinent, cause d'échec et action administrative. Les journaux doivent être protégés contre l'altération et leur accès restreint. Éviter de collecter des secrets ou clés privées ; les données de diagnostic doivent respecter les règles de conservation et de confidentialité de l'organisation.

> **Danger :** Ne partage jamais des captures complètes de configuration qui contiennent des secrets, des clés privées, des identifiants de comptes ou des certificats sensibles. Remplace les valeurs secrètes par des espaces réservés avant de transmettre un fichier de dépannage. Les adresses privées et la topologie peuvent aussi être des informations sensibles selon le contexte.

### 3.10. Cas pratique guidé : diagnostiquer une interconnexion partielle

**Situation :** le tunnel entre deux agences indique un état établi. Les postes du site A peuvent pinguer une adresse du site B, mais les transferts de fichiers échouent après quelques secondes. Les services DNS internes sont intermittents. Les compteurs ESP augmentent dans les deux directions, mais les utilisateurs signalent que certaines applications restent figées.

**Hypothèses initiales :** MTU/MSS incorrects ; ICMP lié à PMTUD filtré ; perte ou fragmentation sur le WAN ; route asymétrique ; serveurs DNS accessibles par un chemin différent ; inspection ou filtrage applicatif sur une passerelle. Le fait que le ping réponde ne permet pas de choisir immédiatement l'une de ces hypothèses.

**Étape 1 — confirmer les mesures :** horodater un test de petite taille, un test de taille graduelle et un transfert applicatif. Vérifier les compteurs IPsec avant et après chaque test. Confirmer que la source est bien un poste du LAN et que les routes du site B reviennent vers le VPN.

**Étape 2 — observer les paquets :** comparer les captures côté LAN et WAN avec les protections appropriées. Identifier si les grands paquets disparaissent avant l'encapsulation, dans le réseau de transport ou après décapsulation. Rechercher les messages ICMP utiles à PMTUD. Examiner les pertes et erreurs d'interface.

**Étape 3 — valider DNS séparément :** demander une résolution directement au serveur DNS attendu, comparer le résultat avec celui du client, vérifier le suffixe de recherche et le chemin vers le résolveur. Si les requêtes passent par un autre tunnel ou un lien local, documenter ce chemin.

**Étape 4 — corriger de façon contrôlée :** si la mesure démontre un problème de MTU/MSS, appliquer une valeur calculée et testée sur l'interface adéquate. Si le filtrage ICMP est fautif, autoriser précisément les messages nécessaires conformément à la politique. Ne pas désactiver tout le filtrage pour régler un cas particulier.

**Étape 5 — vérifier et documenter :** reprendre les tests applicatifs, le test de taille, la résolution DNS, les tests de refus et les mesures de latence. Enregistrer les valeurs, les commandes, le résultat, la modification et le plan de retour arrière. Vérifier le comportement après renouvellement de SA et après une reconnexion.

Le but de ce cas pratique est de montrer que plusieurs symptômes peuvent être liés ou distincts. Le tunnel est une composante du service, mais la bonne analyse doit examiner l'ensemble du chemin réseau et du service applicatif.

### 3.11. Exercices avec corrigés

**Exercice 1 — IKE est établi, aucune donnée ne passe.** Quelles sont les premières vérifications ?

**Corrigé :** vérifier les CHILD SA ou associations ESP, les sélecteurs et les propositions de données ; examiner ensuite les routes, la source réelle du test, les règles de filtrage, le NAT, les compteurs d'encapsulation/décapsulation et le routage retour. Ne pas confondre l'état IKE et l'accès applicatif.

**Exercice 2 — un côté chiffre, l'autre ne reçoit rien.** Quel est le raisonnement ?

**Corrigé :** relever les compteurs des deux côtés et vérifier l'adresse externe du pair, UDP 500/4500, ESP selon le transport, les filtres WAN, le NAT et les captures sur le chemin. Une erreur de route externe peut envoyer les paquets vers une passerelle inattendue.

**Exercice 3 — pourquoi TCP/50 est-il inutile pour ESP ?**

**Corrigé :** ESP est le protocole IP numéro 50. Il ne s'agit pas d'un port TCP. IKE utilise couramment UDP 500 et NAT-T encapsule ESP dans UDP 4500 dans les scénarios concernés. Les règles doivent correspondre au protocole réellement utilisé.

**Exercice 4 — les petits paquets passent, les grands échouent.**

**Corrigé :** tester MTU/MSS, fragmentation, ICMP pour PMTUD et surcharge d'encapsulation. Comparer plusieurs tailles et observer les interfaces avant et après le tunnel. Modifier ensuite la MTU ou le MSS selon les résultats, sans choisir de valeur arbitraire.

**Exercice 5 — deux sites emploient le même sous-réseau.**

**Corrigé :** le routage ne distingue pas naturellement les deux destinations identiques. Préférer la renumérotation. Une traduction ciblée peut être étudiée si elle est impossible, mais doit être documentée et testée dans les deux sens.

**Exercice 6 — connexion utilisateur réussie, accès trop large.**

**Corrigé :** le plan d'autorisation est trop permissif. Limiter les routes, les règles de pare-feu et les groupes par rôle ; utiliser MFA, segmenter les prestataires et journaliser les accès. Une connexion authentifiée ne doit pas conférer automatiquement une confiance totale.

**Exercice 7 — panne après expiration du certificat.**

**Corrigé :** vérifier la date du certificat, sa chaîne de confiance, l'identité attendue, l'heure NTP et le processus de renouvellement. Prévoir des alertes d'expiration et une procédure de rotation testée à l'avance.

**Exercice 8 — basculement du lien primaire réussi mais l'application reste en panne.**

**Corrigé :** valider la route effective après basculement, l'état des SA, la résolution DNS, le chemin retour, le NAT, les sessions applicatives et la capacité du chemin secondaire. La restauration de l'état du tunnel n'est qu'un indicateur parmi d'autres.

### 3.12. Glossaire expert

| Terme | Définition |
|---|---|
| CHILD SA | Association de sécurité IKEv2 servant à protéger le trafic de données, généralement via ESP |
| DPD | Mécanisme de détection d'un pair VPN qui ne répond plus |
| ESP | Encapsulating Security Payload, protocole IPsec de protection du trafic |
| Full tunnel | Modèle où l'essentiel ou la totalité du trafic IP sélectionné passe par le VPN |
| GRE | Encapsulation générique, utile pour certains scénarios de transport et de routage |
| IKE SA | Association qui protège les échanges de contrôle IKEv2 entre les pairs |
| IKEv2 | Protocole de négociation, d'authentification et de gestion des clés pour IPsec |
| IPsec | Cadre de sécurité IP qui s'appuie sur des politiques et des associations de sécurité |
| MSS | Taille maximale de segment TCP, utile pour raisonner sur les transferts TCP dans un tunnel |
| MTU | Taille maximale de paquet IP supportée sans fragmentation au niveau considéré |
| NAT-T | Encapsulation UDP d'ESP facilitant le transport IPsec à travers certains NAT |
| PFS | Propriété de confidentialité persistante selon le mécanisme de gestion des clés utilisé |
| PSK | Secret prépartagé entre les pairs, à protéger et à gérer avec soin |
| Route-based | Approche où le routage dirige le trafic vers une interface de tunnel protégée |
| Policy-based | Approche où des règles/sélecteurs déterminent le trafic à protéger |
| Split tunnel | Modèle où seuls certains flux ou préfixes sont dirigés vers le VPN |
| VTI | Virtual Tunnel Interface, interface logique associée à une protection IPsec selon la plateforme |

---

## 4. Architecture experte, gouvernance et ingénierie à l'échelle

Cette section complète les mécanismes fondamentaux par les décisions qui distinguent un tunnel de laboratoire d'un service d'entreprise exploitable. Les principes ne remplacent pas les sections précédentes : ils montrent comment assembler les composants, définir les contrôles et empêcher qu'une solution localement fonctionnelle crée un risque systémique.

### 4.1. Définir les exigences avant de choisir le protocole

Avant toute configuration, formalise les besoins sous forme d'exigences vérifiables. Une demande comme « relier le siège à l'agence » ne précise ni les applications, ni les volumes, ni les objectifs de disponibilité, ni les obligations d'audit, ni la limite de confiance. Une architecture experte traduit la demande métier en un ensemble de critères d'acceptation.

| Domaine | Question d'ingénierie | Preuve attendue |
|---|---|---|
| Identité | Comment chaque pair prouve-t-il son identité ? | Certificat validé, identité IKE attendue, journal d'authentification |
| Cryptographie | Quels algorithmes et groupes sont autorisés ? | Profil versionné approuvé par la politique cryptographique |
| Flux | Quels initiateurs, destinations, protocoles et ports sont nécessaires ? | Matrice de flux validée par les responsables applicatifs |
| Routage | Quels préfixes peuvent être annoncés et acceptés ? | Politique d'import/export, table de routage contrôlée |
| Disponibilité | Quel objectif de reprise est demandé ? | Mesure de convergence et test de perte d'un chemin |
| Capacité | Quel débit chiffré, nombre de SA et taux de connexions simultanées ? | Test de charge sur du matériel représentatif |
| Observabilité | Quelles alertes permettent de distinguer les états dégradés ? | Tableau de bord, journaux corrélés, seuils et responsables |
| Exploitation | Qui renouvelle les clés et traite les certificats expirés ? | Procédure, propriétaire, calendrier et test de restauration |
| Sécurité | Que peut atteindre un pair compromis ? | Diagramme de segmentation, règles minimales et tests négatifs |
| Conformité | Quelles données doivent être tracées et combien de temps ? | Politique de journalisation et de rétention approuvée |

Chaque exigence doit avoir un propriétaire, une méthode de test, une preuve enregistrée et une condition de réussite. Une exigence sans test est difficile à maintenir ; une exigence sans propriétaire est généralement oubliée lors du renouvellement du service.

### 4.2. Modèle de menace appliqué aux passerelles VPN

Une passerelle VPN se trouve à une frontière de confiance. Elle peut avoir une interface exposée à Internet, une interface interne et des clés donnant accès à plusieurs zones. Elle est donc une cible prioritaire. Le modèle de menace doit considérer au moins : vol de clés privées ou de secrets prépartagés, vulnérabilité de l'implémentation, erreur de règle d'accès, détournement de routes, usurpation d'identité, déni de service, exploitation d'un compte d'administration, exfiltration via un tunnel autorisé et altération des journaux.

Les défenses se répartissent en couches. Premièrement, limiter l'exposition de la surface de gestion : administration depuis un réseau séparé, authentification forte, contrôle d'accès fondé sur des rôles, journalisation et, si la plateforme le permet, restriction des sources d'administration. Deuxièmement, durcir le plan VPN : algorithmes approuvés, authentification robuste, validation stricte de l'identité, limitation des pairs autorisés et mise à jour documentée. Troisièmement, restreindre les routes et les flux au strict nécessaire. Quatrièmement, transmettre les journaux à un système distant afin qu'une compromission de la passerelle ne permette pas de supprimer facilement toutes les preuves. Enfin, prévoir une procédure d'isolement qui n'exige pas l'accès à la passerelle suspecte.

La passerelle ne doit pas devenir un « réseau de confiance » par simple convention. Une interface tunnel active ne doit pas implicitement donner accès à tous les préfixes internes. Les règles d'autorisation doivent être explicites, et les nouvelles routes annoncées par un pair doivent être filtrées. Les plans de gestion, de contrôle et de données sont à protéger séparément.

> **Piège :** Une authentification mutuelle valide prouve que le pair contrôle une identité acceptée ; elle ne prouve pas que chaque route annoncée par ce pair est légitime, ni que les hôtes situés derrière lui sont sûrs. L'identité du tunnel et l'autorisation réseau sont deux contrôles distincts.

### 4.3. Gouvernance cryptographique et agilité

Les algorithmes et tailles de clés ne doivent pas être choisis au hasard, copiés d'un ancien exemple ou négociés en ouvrant successivement toutes les options proposées par les équipements. L'équipe doit maintenir un profil cryptographique approuvé qui couvre la négociation IKE, la protection ESP, l'authentification des pairs, les groupes d'échange de clés et les durées de vie. Le profil doit citer ses sources, préciser les exceptions d'interopérabilité et fournir un calendrier de révision.

L'agilité cryptographique signifie pouvoir remplacer un algorithme ou un mécanisme sans réinventer toute l'architecture. Cela exige un inventaire des équipements, de leurs versions, de leurs capacités matérielles et des dépendances externes. Pour chaque tunnel, il faut savoir quel profil est négocié, quels pairs dépendent de lui, quelle fenêtre de maintenance est disponible et comment confirmer que l'ancien profil n'est plus utilisé après la migration.

Les paramètres de chiffrement authentifié, tels qu'AES-GCM lorsqu'ils sont pris en charge conformément aux recommandations du produit, réunissent chiffrement et intégrité dans un mode AEAD ; on ne doit pas leur ajouter mécaniquement un mécanisme d'intégrité séparé comme si toutes les combinaisons étaient interchangeables. Les profils de compatibilité doivent suivre la documentation et les recommandations cryptographiques à jour. L'utilisation de paramètres faibles pour « faire passer » une négociation est une mauvaise réponse à un échec : il faut déterminer quelle proposition manque, pourquoi l'un des équipements n'offre pas le profil prévu et si une mise à jour est nécessaire.

Le secret prépartagé peut être acceptable dans des déploiements limités si sa qualité, son stockage et sa rotation sont correctement gérés. À grande échelle, des identités par certificat facilitent souvent l'identité par équipement et la révocation ciblée, mais introduisent une dépendance opérationnelle à la PKI : publication des autorités de confiance, renouvellement, révocation, validation des noms, synchronisation temporelle et disponibilité des services utiles. Il n'existe pas de méthode d'authentification qui supprime le besoin de gouvernance.

Une feuille de route cryptographique experte inclut :

1. l'inventaire des suites réellement négociées, et non uniquement celles présentes en configuration ;
2. la détection des paramètres obsolètes ou non autorisés ;
3. un environnement de préproduction représentatif des pairs ;
4. une migration compatible avec une courte période de chevauchement si la plateforme l'autorise ;
5. la suppression des anciennes propositions après validation ;
6. un contrôle post-changement prouvant que la négociation utilise désormais le profil attendu.

La « confidentialité persistante » (*Perfect Forward Secrecy*, PFS) dépend du mécanisme d'échange de clés et du profil de rekeying, pas d'une simple mention dans la documentation du projet. Le modèle de menace doit aussi prendre en compte la conservation à long terme des données chiffrées, l'évolution des capacités d'attaque et les orientations de migration publiées par les organismes compétents. Ne présente pas une technologie comme « post-quantique » sans vérifier exactement ce qu'implémentent les versions concernées, ce qui est négocié, et si le mécanisme est standardisé, pris en charge et évalué dans le contexte visé.

> **Danger :** Ne copie jamais une clé privée ou un secret VPN dans un ticket, une capture d'écran, un dépôt Git, un script de diagnostic ou un document de cours. Les sauvegardes chiffrées des configurations doivent elles-mêmes être protégées et leur restauration doit être testée.

### 4.4. PKI, certificats et identité des pairs

Une architecture à certificats doit vérifier l'ensemble de la chaîne de confiance et la correspondance entre l'identité attendue et le certificat présenté. La simple présence d'un certificat signé par une autorité connue n'est pas suffisante si le nom, l'usage de clé, les dates de validité ou les contraintes ne correspondent pas à l'usage VPN.

Les contrôles à documenter comprennent :

- l'autorité racine et les autorités intermédiaires acceptées ;
- le champ d'identité comparé par chaque pair (nom, FQDN ou autre identité autorisée) ;
- la période de validité et la synchronisation de l'horloge ;
- les usages de clé et les algorithmes de signature admis ;
- le comportement lorsque la vérification de révocation est indisponible ;
- le propriétaire du certificat, l'échéance de renouvellement et la procédure d'urgence ;
- le traitement du remplacement de certificat sans interruption évitable.

Une erreur de date peut ressembler à une panne cryptographique. Un certificat renouvelé avec un nom différent peut être valide au sens de la PKI, mais refusé par le profil IKE qui attend une identité précise. Pour le diagnostic, conserve les journaux nécessaires à la compréhension de la décision de confiance, tout en masquant les informations privées. Une politique de révocation doit préciser si l'accès est refusé quand le service de statut n'est pas joignable ; cette décision doit être explicite, car les deux choix impliquent un compromis entre disponibilité et assurance de révocation.

### 4.5. Architecture multi-sites : hub-and-spoke, maillage et hiérarchies

Dans un modèle *hub-and-spoke*, les sites distants établissent des tunnels vers un ou plusieurs concentrateurs. Cette approche facilite les politiques centralisées et réduit le nombre de relations de voisinage, mais elle peut imposer un détour du trafic entre deux agences et faire du concentrateur un point de congestion. Dans un maillage complet, chaque paire de sites peut communiquer directement, mais le nombre de relations croît rapidement. Pour N sites, un maillage complet nécessite théoriquement N × (N − 1) / 2 relations bidirectionnelles distinctes ; cette croissance affecte la configuration, l'observabilité et le dépannage.

Une hiérarchie régionale peut placer des hubs locaux devant un noyau central. Elle peut réduire la distance et contenir les domaines de panne, mais elle nécessite une politique claire d'agrégation et de transit. La sélection dépend de la matrice réelle des flux : un schéma logique intuitif peut être inefficace si les applications les plus volumineuses communiquent principalement entre agences.

| Modèle | Avantage typique | Risque principal | Contrôle expert |
|---|---|---|---|
| Hub-and-spoke simple | Administration centralisée | Concentrateur et transit central saturés | Mesure du trafic inter-sites, redondance des hubs |
| Double hub | Chemins de secours et répartition | Asymétrie, état de session et convergence | Tests de panne et politique d'annonce déterministe |
| Maillage complet | Chemins directs | Explosion du nombre de relations et des politiques | Automatisation, modèle d'identité stable, inventaire |
| Hiérarchie régionale | Compromis entre proximité et contrôle | Fuites de routes entre régions | Résumé de routes, filtres et frontières de politique |
| VPN dynamique à pairs multiples | Moins de configuration statique | Contrôle des pairs et du routage plus complexe | Autorisation de chaque identité et limites de routes |

Une redondance purement physique ne garantit pas une redondance fonctionnelle. Deux tunnels qui partagent le même accès opérateur, la même alimentation ou le même équipement de terminaison ne couvrent pas toutes les causes de panne. Le plan de résilience doit inclure les dépendances communes et la perte du service de gestion des identités, si celui-ci est nécessaire à la reconnexion.

### 4.6. Routage dynamique au travers du VPN

Le routage dynamique peut simplifier les déploiements où les préfixes changent fréquemment et permettre une convergence plus contrôlée. Il introduit toutefois un deuxième domaine de sécurité : le pair qui peut établir un tunnel ne doit pas automatiquement pouvoir annoncer des routes arbitraires. Il faut définir les préfixes admissibles, les attributs autorisés, les règles d'import/export, la portée des résumés et le comportement lors d'une perte de voisinage.

BGP convient souvent aux architectures qui exigent une politique d'annonce fine et une séparation claire des domaines de routage. OSPF peut être approprié dans un domaine administré de façon homogène, mais la conception des types de réseau, des zones et de la redistribution doit rester cohérente. Le choix ne doit pas être basé uniquement sur le nombre de commandes nécessaires. Il dépend aussi des objectifs de convergence, du modèle opérationnel et de l'expérience de l'équipe.

Les principes à appliquer comprennent :

- filtrer les préfixes reçus et annoncés ;
- limiter le nombre maximal de préfixes si la plateforme le permet ;
- définir explicitement la préférence de chemin et le comportement de secours ;
- éviter les redistributions multiples et circulaires entre protocoles ;
- protéger les sessions de routage selon les capacités et recommandations de la plateforme ;
- surveiller les changements de voisinage et les variations inattendues de table ;
- prouver qu'une route annoncée par un site ne peut pas détourner le trafic d'autres zones.

Ne fais pas dépendre la route vers l'adresse publique du pair VPN d'un préfixe qui lui-même ne peut être atteint qu'à travers ce tunnel. Cela crée une dépendance récursive : le tunnel doit être actif pour atteindre la destination nécessaire à son propre établissement. La route de transport vers le pair doit être stable et examinée séparément des routes internes.

```text
                     Réseau de transport non fiable
                  +--------------------------------+
                  |                                |
             [Hub A]                            [Hub B]
                |                                  |
        +-------+-------+                  +-------+-------+
        |               |                  |               |
     [Site 1]        [Site 2]            [Site 3]        [Site 4]
        |               |                  |               |
        +---- routes filtrées / annonces contrôlées --------+

  À vérifier : identité du pair, routes autorisées, chemin retour,
  convergence après perte d'un hub, et isolation de chaque site.
```

> **Piège :** Un tunnel chiffré peut transporter une annonce de route incorrecte tout aussi sûrement qu'une annonce correcte. IPsec protège la communication entre pairs ; il ne valide pas à lui seul la légitimité des préfixes reçus.

### 4.7. Haute disponibilité : détecter, basculer et récupérer

Une architecture redondante doit distinguer au moins quatre événements : panne de l'interface physique, perte d'accessibilité de l'adresse du pair, disparition des associations de sécurité et défaillance d'une application malgré un tunnel déclaré opérationnel. Chacun demande un mécanisme de détection différent. Un état de tunnel peut rester « up » alors que le service métier est inutilisable, par exemple à cause d'une route retour manquante ou d'une panne DNS.

Il faut choisir les délais de détection en fonction du type de panne et de la stabilité du réseau. Des sondes trop fréquentes peuvent provoquer des basculements intempestifs en cas de perte transitoire ; des sondes trop lentes prolongent l'interruption. Les mécanismes de type DPD, suivi de route, BFD et sondes applicatives n'observent pas le même objet. Ils ne sont donc pas interchangeables. La supervision doit préciser ce qui est testé et dans quelle couche.

Une procédure de test de haute disponibilité doit mesurer : le délai de détection, le délai de convergence du routage, la perte de paquets, le temps de rétablissement d'une application, le comportement des sessions existantes, les journaux émis et les routes retenues après retour du chemin principal. Le plan de test doit inclure les scénarios de récupération, car certains systèmes oscillent entre les chemins quand le lien principal flappe.

Pour réduire le risque, définis une priorité de retour au chemin préféré, un temporisateur de stabilité lorsqu'il est pris en charge, des seuils de déclenchement justifiés, et un protocole d'escalade si la redondance ne restaure pas le service. Les valeurs par défaut du fabricant ne sont pas nécessairement adaptées à l'application, mais les réduire sans mesure peut rendre l'architecture moins stable.

### 4.8. VPN et multi-cloud

Les connexions entre sites physiques et réseaux cloud ajoutent des contraintes d'adressage, de routage et de responsabilité partagée. Le fournisseur cloud expose souvent une passerelle managée, des paramètres de tunnel, des préfixes à annoncer ou accepter et des exigences concernant la disponibilité du pair. Les fonctions offertes dépendent du produit et de la région ; il faut consulter la documentation active de chaque fournisseur au moment du déploiement.

La conception doit traiter les chevauchements d'adresses privées, les routes propagées automatiquement, la séparation des environnements de production et de test, les limites de débit, les quotas, les changements d'adresse publique de certaines passerelles et les mécanismes de supervision disponibles. L'utilisation de plusieurs tunnels cloud ne garantit pas automatiquement une répartition de charge : certains services les traitent comme chemins redondants et sélectionnent un chemin principal. La répartition doit être prouvée par les règles du produit et par une mesure réelle.

Les préfixes annoncés aux services cloud doivent être aussi précis que nécessaire et éviter une exposition accidentelle de routes de transit internes. Quand une interconnexion relie plusieurs environnements, utilise des domaines de routage et des contrôles d'accès adaptés, plutôt qu'un réseau étendu « plat ». Il faut également déterminer où réside la terminaison cryptographique et quelles traces sont accessibles au client lorsque la passerelle est gérée par le fournisseur.

### 4.9. VPN d'accès distant et accès fondé sur l'identité

Le modèle d'accès distant doit traiter le poste comme potentiellement compromis et l'utilisateur comme une identité qui doit être authentifiée, autorisée et réévaluée selon la politique. Un VPN donnant une adresse dans un sous-réseau interne n'est pas une politique d'autorisation suffisante. Après l'établissement du tunnel, les règles d'accès doivent continuer de limiter les ressources, protocoles, ports et environnements accessibles.

Les contrôles usuels incluent l'authentification multifacteur, les certificats d'appareil quand ils sont adaptés, l'évaluation de conformité du poste, l'expiration des sessions, la révocation rapide des accès, la protection des comptes privilégiés et la journalisation des changements de rôle. Il faut aussi définir la différence entre le tunnel complet et le split tunneling. Le tunnel complet peut accroître la visibilité et le contrôle sur le trafic, mais exige davantage de capacité centrale et une politique claire pour les usages personnels. Le split tunneling peut améliorer les performances, mais demande de documenter les destinations qui ne passent pas par le réseau d'entreprise et les risques qui en découlent.

La décision doit être guidée par le modèle de menace, pas par une règle universelle. Pour les comptes d'administration, l'accès peut être limité à des bastions dédiés, avec une segmentation distincte de celle des utilisateurs ordinaires. Les profils VPN des fournisseurs, sous-traitants et employés ne devraient pas partager un ensemble de routes ou de permissions simplement parce qu'ils utilisent le même concentrateur.

### 4.10. Observabilité, SLI, SLO et corrélation

Une surveillance experte ne se limite pas à afficher « tunnel up ». Elle mesure la disponibilité du service, l'établissement et le renouvellement des associations, la latence, la perte, le débit, les erreurs d'encapsulation, la capacité CPU/ASIC, les changements de routes, les rejets de politique et le résultat de sondes applicatives. Les indicateurs doivent être associés à des seuils d'action et à une personne ou équipe qui reçoit l'alerte.

| Indicateur | Ce qu'il révèle | Limite d'interprétation |
|---|---|---|
| État IKE | Le pair échange les messages de contrôle | N'assure pas le transport applicatif |
| Nombre de CHILD SA | Les associations de données sont créées | Une SA inutilisée peut rester établie |
| Compteurs ESP entrants/sortants | Activité des paquets protégés | Les compteurs seuls ne prouvent pas le succès final |
| Perte et latence de sonde | Qualité du chemin testé | Une sonde peut emprunter un chemin différent du flux métier |
| État du voisinage BGP/OSPF | Fonctionnement du routage dynamique | Un voisin actif peut annoncer de mauvais préfixes |
| Débit chiffré et utilisation CPU | Charge du plan de données | Dépend de l'algorithme, des tailles de paquets et de l'accélération |
| Événements d'authentification | Succès ou échec d'identité | La journalisation peut être limitée ou retardée |
| Test applicatif | Résultat de bout en bout | Ne remplace pas le diagnostic réseau détaillé |

La corrélation exige une heure fiable sur les passerelles, les systèmes de journalisation et les équipements réseau. Des horloges divergentes compliquent la reconstruction de la séquence d'événements. Le SIEM doit recevoir les champs utiles : identifiant de pair, identité authentifiée, adresse de transport, profil IKE, changement de SA, raison de fermeture, préfixe appris et action de politique lorsque disponibles. Les secrets et les éléments permettant d'extraire des clés doivent être exclus des journaux.

Les seuils doivent différencier une anomalie momentanée et une panne durable. Une alerte « tunnel down » peut être enrichie de la dernière négociation réussie, de l'état du transport, de la disponibilité de l'adresse du pair, du nombre de SA et du changement récent de routage. L'objectif est d'accélérer la décision, pas de générer un flot d'alarmes identiques.

### 4.11. Capacité, performance et limites matérielles

Le débit utile d'un VPN dépend de plusieurs facteurs : capacité cryptographique de la plateforme, algorithme choisi, taille moyenne des paquets, nombre de SA, vitesse des interfaces, traitement des paquets trop petits, nombre de connexions simultanées, taux d'établissement de sessions et fonctions activées en parallèle. Un chiffre maximal publié par un fournisseur peut avoir été mesuré avec des paquets, des fonctions ou une topologie très différents de la production.

Un test de capacité utile doit séparer au moins le débit avec chiffrement, le débit sans chiffrement, le taux de nouveaux tunnels ou d'associations, la latence sous charge, la perte, la consommation CPU, la température ou les limitations thermiques pertinentes, et le comportement lors d'une bascule. Mesurer uniquement un transfert TCP de longue durée masque les problèmes de créations de sessions et de petits paquets. De même, une charge simulée à partir d'un seul générateur peut devenir le goulot d'étranglement et sous-estimer l'équipement testé.

La surcharge d'encapsulation réduit la taille utile du paquet intérieur. Le calcul exact dépend des versions IP, des en-têtes ESP, du mode de chiffrement, du NAT-T et d'éventuels tunnels GRE ou autres encapsulations. Ne mets pas en production une valeur de MTU ou MSS universelle tirée d'un exemple. Calcule un budget d'encapsulation pour chaque chemin et valide le comportement des paquets qui approchent la MTU.

Le dimensionnement doit inclure une marge de croissance et une situation de panne réaliste : un seul concentrateur restant peut devoir traiter tous les tunnels, toutes les associations et le trafic agrégé. Une paire redondante dont chaque membre est dimensionné à 50 % de la charge en mode normal ne peut pas nécessairement reprendre 100 % de cette charge après une panne, surtout si l'activation de l'inspection supplémentaire augmente le coût de traitement.

> **Astuce :** Conserve un jeu de mesures de référence à charge nominale et pendant une bascule contrôlée. Sans référence, une hausse de latence ou une baisse de débit restera difficile à qualifier.

### 4.12. Automatisation, gestion de configuration et dérive

L'automatisation peut réduire les erreurs de saisie, mais elle amplifie aussi une erreur de modèle si elle pousse une politique incorrecte sur tous les pairs. Une chaîne de gestion experte sépare inventaire, données propres à chaque site, modèles de configuration, secrets, validation, déploiement et preuve de conformité. Les secrets ne doivent pas être conservés en clair dans les dépôts ; un système de gestion des secrets ou un mécanisme équivalent doit contrôler les accès et la rotation.

Avant un déploiement, la pipeline peut vérifier la syntaxe, comparer les profils cryptographiques à la politique approuvée, vérifier que les préfixes annoncés sont présents dans une liste autorisée, détecter les routes par défaut non prévues, et confirmer que les interfaces de transport ne reçoivent pas de réseaux internes par erreur. La validation syntaxique n'est cependant pas une simulation complète du comportement de l'équipement. Les tests doivent inclure l'état réel de la négociation, le routage, le plan de données et les flux applicatifs.

Le système de gestion doit comparer régulièrement la configuration déclarée à la configuration réellement active. Une commande manuelle d'urgence peut être légitime, mais elle doit être enregistrée, évaluée puis réintégrée au modèle ou annulée. La dérive non traitée fait que le prochain redéploiement risque de supprimer une correction de production ou, pire, de réintroduire une configuration vulnérable.

Les déploiements doivent être progressifs : laboratoire, site pilote, petit groupe, puis élargissement contrôlé. Chaque étape doit inclure des critères d'arrêt. La capacité d'annuler doit être vérifiée avant l'exécution, notamment lorsque le tunnel sert au transport du canal d'administration. Ne laisse pas un déploiement couper le seul chemin permettant de le corriger à distance.

## 5. Laboratoire expert : interconnexion routée et validation de bout en bout

### 5.1. Scénario

Considérons deux sites et une passerelle de secours virtuelle. Le site A utilise `10.10.0.0/16`, le site B `10.20.0.0/16`, et les adresses publiques de transport sont des valeurs de documentation réservées qui doivent être remplacées dans le laboratoire. Le tunnel est route-based ; un protocole de routage peut annoncer les préfixes privés à travers le tunnel si cette fonction est prise en charge et prévue dans la conception.

La politique exige que seuls les réseaux des deux sites soient échangés. Le réseau de gestion ne doit pas être annoncé aux agences ; le tunnel ne doit pas devenir une route par défaut sauf exigence distincte, approuvée et testée. Le profil cryptographique doit provenir de la politique approuvée pour la plateforme, et le mode d'authentification doit être explicitement choisi. Les adresses et secrets de cette section sont des valeurs d'exemple ou des espaces réservés, pas des paramètres universels.

```text
 LAN A 10.10.0.0/16                           LAN B 10.20.0.0/16
        |                                             |
    [Edge A] ===== interface Tunnel / IPsec ===== [Edge B]
        |             transport public               |
        +------- routage filtré et contrôlé ----------+
```

### 5.2. Plan de validation du routage

L'ordre recommandé est : vérifier les routes de transport vers l'adresse publique du pair, établir l'identité IKE, confirmer les associations ESP, valider l'adresse et l'état de l'interface tunnel, puis examiner les voisins et les routes apprises. Une route de préfixe distant ne doit être acceptée que si elle est attendue et autorisée. Après validation du routage, vérifier les règles de pare-feu, le traitement NAT, les compteurs ESP et enfin un test applicatif depuis un hôte réel de chaque site.

Un échange de ping entre les adresses des passerelles ou des interfaces tunnel n'est pas suffisant : il peut emprunter un chemin différent de celui du sous-réseau applicatif, et il ne teste pas nécessairement la politique d'autorisation. Le jeu d'essais doit contenir un flux autorisé, un flux interdit, une connexion nouvellement initiée dans chaque sens si elle est prévue, et un test après bascule du chemin.

### 5.3. Contrôle du routage et protection contre les annonces erronées

Le protocole de routage doit recevoir une liste minimale de préfixes et annoncer une liste prévisible. Les filtres doivent être appliqués aussi bien à la réception qu'à l'émission, selon le rôle du voisin. Les résumés sont utiles mais peuvent masquer une route plus spécifique ; vérifie leur effet avec les règles de préférence et les routes de secours. En cas de redistribution entre OSPF, BGP et routes statiques, documente les routes qui peuvent entrer dans chaque domaine et celles qui doivent rester locales.

Le laboratoire doit simuler une annonce indésirable. Le test est réussi si l'annonce est rejetée, si la raison peut être retrouvée dans la configuration ou les journaux et si les routes légitimes continuent de fonctionner. Il faut aussi simuler une disparition du voisinage : la route retirée doit disparaître dans le délai attendu, sans laisser un chemin blackhole persistant.

### 5.4. Plan de test cryptographique

La vérification cryptographique doit confirmer le profil réellement négocié plutôt que se limiter au profil local. Enregistre le type d'authentification du pair, l'identité observée, les suites IKE et ESP utilisées, les groupes d'échange pris en charge, les valeurs de durée de vie et l'état des renouvellements. Si les deux équipements offrent plusieurs propositions, la politique doit déterminer explicitement lesquelles sont acceptables.

Toute migration de chiffrement doit être précédée d'un test d'interopérabilité. Quand la plateforme autorise un chevauchement temporaire, limite-le à la fenêtre nécessaire et supprime les profils historiques une fois les pairs migrés. Le succès d'un test ne doit pas être déduit du simple fait que le tunnel reste actif : il faut contrôler la nouvelle SA après le renouvellement et confirmer qu'elle respecte la nouvelle politique.

## 6. Méthode de dépannage experte

### 6.1. Construire une chronologie vérifiable

Lors d'un incident, note l'heure du début, les changements récents, les pairs affectés, les préfixes concernés, la portée applicative et l'existence d'un chemin de secours. Récupère les états IKE et ESP, les compteurs entrants/sortants, les routes actives, le voisinage de routage et les journaux du pare-feu. Utilise une capture ciblée pour confirmer ce qui sort réellement de l'interface de transport et ce qui arrive sur le pair distant.

Ne lance pas immédiatement plusieurs commandes de remise à zéro. Effacer les SA peut rétablir momentanément le service, mais supprime aussi des indices utiles et ne corrige pas la cause. Avant toute réinitialisation, capture les états, les raisons de fermeture, les temporisateurs et les changements de routes. Les actions perturbatrices doivent respecter les procédures d'exploitation et préciser leur impact.

### 6.2. Arbre de décision

```text
Le service applicatif échoue
          |
          v
Le pair de transport est-il joignable ? ---- non ---> Transport / ACL / route externe
          |
         oui
          v
IKE SA présente et identité acceptée ? ----- non ---> Authentification / propositions / PKI
          |
         oui
          v
CHILD SA / ESP opérationnels ? ------------- non ---> Sélecteurs / proposal / rekey / PFS
          |
         oui
          v
Compteurs ESP évoluent dans les deux sens ? - non ---> Route / règle / flux non sélectionné
          |
         oui
          v
Route aller-retour cohérente ? -------------- non ---> Filtres BGP/OSPF / NAT / asymétrie
          |
         oui
          v
MTU et politique applicative correctes ? ---- non ---> PMTUD / MSS / ACL / DNS / serveur
```

Cet arbre est un ordre de vérification, pas une preuve qu'une cause unique explique tous les symptômes. Une panne peut combiner une route absente et une MTU trop élevée, ou une négociation instable et une saturation du processeur.

### 6.3. Distinguer les causes proches

| Symptôme | Causes possibles | Preuve la plus utile | Test discriminant |
|---|---|---|---|
| Tunnel déclaré actif, application indisponible | Route, filtre, serveur, DNS | Route des deux côtés et journal pare-feu | Tester une destination et un port autorisés précis |
| Compteurs sortants seulement | Perte de retour, peer down, ACL distante | Capture des deux extrémités | Comparer les paquets sur les interfaces externes |
| Échec lors du rekey | Profil incompatible, horloge, ressource ou bug | Journaux au moment précis du renouvellement | Observer un cycle complet en préproduction |
| Débit bon sur petits paquets seulement | MTU, PMTUD, fragmentation | Capture ICMP et taille des segments | Tester une gamme de tailles sans fragmentation locale aveugle |
| Connexion intermittente | Flapping du transport, DPD trop agressif, HA | Chronologie des événements et pertes | Corréler route, IKE, interface et SLA applicatif |
| Une seule agence affectée | Politique, adressage chevauchant, préfixe manquant | Différences de configuration et table de routage | Comparer avec un site fonctionnel de même rôle |
| Nouveaux tunnels échouent, anciens restent actifs | PKI, quotas, rate limit, propositions nouvelles | Journaux d'authentification et métriques de capacité | Tenter depuis un pair de test approuvé et isolé |
| Après bascule, certaines sessions restent bloquées | État non synchronisé, asymétrie, cache applicatif | Logs HA, session table, routes | Test de perte planifié avec flux long et nouveau flux |

### 6.4. Captures réseau et données sensibles

Les captures sont utiles pour confirmer les transports et les tailles de paquets, mais le contenu ESP reste chiffré sans matériel autorisé de déchiffrement. Une capture publique peut montrer les adresses et ports externes, le volume, le timing et certains métadonnées. Ces informations peuvent déjà être sensibles. Limite la capture dans le temps et dans la portée, protège le fichier, consigne la personne qui y a accès et supprime-le selon la politique de rétention.

Les extraits de journal ne doivent pas révéler de secrets, de clés, de tokens, de chaînes de communauté ou de données personnelles non nécessaires. Les fichiers de configuration partagés en dehors de l'équipe doivent être nettoyés avec une méthode qui ne laisse pas les secrets dans un historique ou une section masquée. Après diagnostic, vérifie que le débogage détaillé a été désactivé si sa poursuite risquait de consommer des ressources ou d'exposer trop de données.

## 7. Changement, migration et reprise

### 7.1. Procédure de changement maîtrisée

Une modification de VPN peut couper la communication entre des sites entiers ou supprimer le seul canal d'administration. Le plan de changement doit indiquer le périmètre, les dépendances, les commandes ou objets modifiés, les tests avant/après, le point de décision de retour arrière, les responsables et le canal de communication. Le plan doit être validé sur un environnement représentatif et ne pas se contenter de vérifier que les commandes sont acceptées.

Séquence type :

1. exporter et protéger la configuration actuelle ;
2. relever les états de référence, les routes, les compteurs et la latence ;
3. vérifier l'accès de secours indépendant du tunnel à modifier ;
4. appliquer le changement sur un pair pilote ou un site non critique ;
5. confirmer la négociation et la politique cryptographique effectivement appliquée ;
6. tester les flux autorisés et les flux devant rester interdits ;
7. tester le chemin retour, le renouvellement de SA et la panne du chemin principal si cela fait partie du changement ;
8. conserver les preuves, puis élargir le déploiement selon les critères d'acceptation.

Le retour arrière doit être une procédure exécutable, non une phrase telle que « restaurer si nécessaire ». Il faut connaître la configuration antérieure, les données qui ont changé, l'ordre de restauration, les impacts de sessions et les critères déclenchant l'annulation. Si le changement modifie un certificat, la restauration peut exiger que l'ancien certificat soit encore valide et accepté par le pair distant.

### 7.2. Migration entre fournisseurs ou plateformes

Une migration entre deux systèmes VPN n'est pas toujours une simple traduction de commandes. Les produits peuvent interpréter différemment les identités, les sélecteurs, les interfaces virtuelles, le routage, les temporisateurs, le NAT-T, l'état HA ou les routes reçues. Il faut faire correspondre les capacités et les propriétés attendues, pas seulement les noms des champs.

Établis une matrice de correspondance indiquant la fonction requise, l'implémentation ancienne, l'implémentation cible, les limites, le test associé et le résultat. Déploie le nouvel équipement en mode parallèle lorsque l'architecture le permet ; valide son transport, son identité, les routes et les flux avant le basculement. Vérifie ensuite les journaux, les règles de pare-feu, les flux retour et le comportement après rekey. Retire l'ancienne configuration seulement quand la nouvelle est stable et qu'un retour n'est plus nécessaire.

### 7.3. Rotation urgente de clé ou compromission d'identité

En cas de suspicion de compromission d'un secret ou d'une clé, la priorité est de déterminer le périmètre : quels pairs utilisent l'élément compromis, quelles routes ils peuvent annoncer, quelles zones sont atteignables et quels journaux sont disponibles. Le plan de réponse peut exiger l'isolement d'un pair, la révocation d'un certificat, la rotation des secrets, la création d'un profil temporaire plus restrictif et l'examen des flux récents.

Évite une rotation globale non coordonnée lorsqu'elle risque de couper simultanément tous les chemins de secours. La stratégie doit définir l'ordre des pairs, le canal de communication de confiance, le moment de révocation, la preuve de suppression des anciens secrets et la validation que plus aucune SA ne dépend du mécanisme compromis. Dans un contexte de compromission avérée, la disponibilité peut devoir céder devant le confinement : cette décision revient au processus de gestion d'incident et aux responsables habilités.

## 8. Exercices experts avec corrigés

### Exercice 1 — IKE actif mais pas de trafic

Deux passerelles négocient une IKE SA, mais aucune CHILD SA adaptée au trafic entre `10.10.0.0/16` et `10.20.0.0/16` n'est visible. Propose les vérifications dans l'ordre.

**Corrigé :** comparer les sélecteurs et le modèle route-based/policy-based des deux côtés ; examiner la proposition ESP et les paramètres de PFS ; confirmer les routes de transport et les règles qui déclenchent le tunnel ; lire les journaux au moment d'un trafic initiateur ; vérifier que la version et les fonctions des pairs supportent le mode choisi. Une remise à zéro ne vient qu'après la collecte des éléments de diagnostic.

### Exercice 2 — Préfixe imprévu appris depuis un site distant

Un pair correctement authentifié annonce `0.0.0.0/0`, alors que seul `10.20.0.0/16` devait être échangé.

**Corrigé :** filtrer immédiatement le préfixe par une politique d'import, vérifier les routes actives et les flux qui ont pu être détournés, confirmer la politique d'annonce du voisin et inspecter toute redistribution. Ne pas considérer l'authentification réussie comme preuve de légitimité de la route. Documenter la portée de l'incident et tester qu'un préfixe non autorisé reste rejeté.

### Exercice 3 — Tunnel de secours actif, trafic toujours interrompu

Après la panne du tunnel principal, la route est annoncée via le secours, mais les sessions applicatives expirent.

**Corrigé :** mesurer le délai de détection et la convergence, vérifier que les deux sens empruntent un chemin cohérent, examiner les états de session et la synchronisation HA, confirmer que le chemin secondaire a une capacité suffisante, et tester à la fois les nouvelles sessions et les sessions existantes. Le succès du ping ne garantit pas la reprise des sessions longues.

### Exercice 4 — Les fichiers volumineux échouent, les connexions sont établies

**Corrigé :** vérifier le budget d'encapsulation, la MTU du chemin, la découverte de MTU, les messages ICMP requis, le MSS TCP négocié et les captures sur les deux extrémités. Réduire arbitrairement la MTU peut masquer la cause sans restaurer correctement toutes les applications.

### Exercice 5 — Certificat renouvelé, reconnexion impossible

**Corrigé :** vérifier la chaîne de confiance, l'identité attendue par le profil IKE, les dates et usages du certificat, l'horloge, la révocation et la disponibilité de l'intermédiaire. Comparer le certificat présenté avec les politiques d'identité, plutôt que d'abaisser la validation à un profil moins strict.

### Exercice 6 — Dimensionnement en mode dégradé

Un concentrateur traite 3 Gbit/s en nominal. Son pair de secours doit reprendre la charge en cas de panne. Quel test mener ?

**Corrigé :** ne pas se contenter de vérifier une capacité catalogue. Reproduire le trafic utile, les distributions de taille des paquets, le nombre de SA et de connexions, les fonctions d'inspection activées et une bascule réelle. Mesurer débit, latence, pertes, charge processeur et temps de convergence ; prévoir une marge en plus de la charge nominale.

## 9. Checklist de mise en production

- [ ] Chaque pair possède une identité définie et validée selon la politique.
- [ ] Le profil cryptographique est approuvé, documenté et testé sur la version cible.
- [ ] Les secrets et clés sont stockés selon une procédure contrôlée et leur rotation est planifiée.
- [ ] Les routes entrantes et sortantes sont filtrées et conformes à la matrice d'autorisation.
- [ ] Les domaines de gestion, utilisateurs, serveurs et sites distants sont segmentés.
- [ ] Le routage externe vers le pair reste indépendant des routes transportées à travers le tunnel.
- [ ] Les règles NAT et de filtrage ont été testées dans les deux sens.
- [ ] Les contraintes MTU/MSS ont été mesurées sur les chemins pertinents.
- [ ] Les journaux permettent d'identifier le pair, le profil, la SA, les changements de route et les rejets pertinents.
- [ ] Les alertes ont un propriétaire, une procédure d'escalade et des seuils éprouvés.
- [ ] La bascule et le retour au chemin principal ont été testés et mesurés.
- [ ] La procédure de changement comprend un retour arrière réalisable sans dépendre du tunnel modifié.
- [ ] Les configurations de référence et les preuves de test sont conservées de façon protégée.
- [ ] Les flux non autorisés ont été testés et sont effectivement bloqués.

## Points à retenir

- Un VPN expert est un service complet : identité, cryptographie, sélection de trafic, routage, autorisation, capacité, supervision et cycle de vie doivent être conçus ensemble.
- Une SA active indique un état technique précis ; elle ne garantit ni l'accessibilité applicative ni le respect des exigences métier.
- Le routage dynamique à travers un tunnel exige des filtres de préfixes et une gouvernance des annonces aussi rigoureux que ceux du réseau physique.
- La redondance doit être démontrée par des tests de panne et de reprise, pas déduite du nombre d'interfaces ou de tunnels configurés.
- Les politiques cryptographiques doivent être maintenues, et les paramètres historiques retirés après des migrations contrôlées.
- Les captures, configurations et journaux peuvent contenir des informations sensibles ; leur collecte et leur partage doivent être limités et documentés.
- Les mesures de capacité doivent représenter le trafic, les petites tailles de paquets, les nouvelles sessions et le fonctionnement en mode dégradé.
- Une procédure de changement doit prévoir une voie de récupération indépendante du tunnel qu'elle modifie.

### Références techniques

1. IETF, RFC 4301 — *Security Architecture for the Internet Protocol*. https://www.rfc-editor.org/rfc/rfc4301.html
2. IETF, RFC 7296 — *Internet Key Exchange Protocol Version 2 (IKEv2)*. https://www.rfc-editor.org/rfc/rfc7296.html
3. IETF, RFC 3948 — *UDP Encapsulation of IPsec ESP Packets*. https://www.rfc-editor.org/rfc/rfc3948.html
4. IETF, RFC 4106 — *The Use of Galois/Counter Mode (GCM) in IPsec ESP*. https://www.rfc-editor.org/rfc/rfc4106.html
5. IETF, RFC 8221 — *Cryptographic Algorithm Implementation Requirements and Usage Guidance for ESP and AH*, à lire avec RFC 9395 qui le met à jour. https://www.rfc-editor.org/rfc/rfc8221.html et https://www.rfc-editor.org/rfc/rfc9395.html
6. NIST, SP 800-77 Rev. 1 — *Guide to IPsec VPNs*. https://csrc.nist.gov/pubs/sp/800/77/r1/final
7. Cisco, *Security and VPN Configuration Guide, Cisco IOS XE 17.x*. https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/sec-vpn/b-security-vpn.html
8. WireGuard, documentation officielle. https://www.wireguard.com/
9. OpenVPN, documentation et ressources officielles. https://openvpn.net/community-resources/

Les références doivent être vérifiées avant le déploiement, en particulier pour les recommandations cryptographiques et les fonctions propres à une version donnée. Les extraits de configuration de ce cours servent à l'apprentissage et à l'élaboration de tests ; ils ne constituent pas une configuration universelle prête à appliquer sans adaptation.
