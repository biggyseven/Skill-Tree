---
node_id: vpn-intermediaire
title: VPN & tunnels - Intermédiaire
---

# VPN & tunnels - Intermédiaire

**Niveau :** INTERMÉDIAIRE

Un VPN de production ne se résume pas à établir un tunnel entre deux adresses publiques. Il faut définir précisément les réseaux autorisés, choisir un modèle de routage, négocier des paramètres cryptographiques compatibles, gérer l'authentification des pairs, traverser les mécanismes NAT éventuels, mesurer la surcharge d'encapsulation et garantir que le trafic retour emprunte un chemin cohérent. L'établissement du tunnel n'est qu'une étape du service : une solution exploitable doit également être observable, documentée, testable et récupérable après une panne.

À ce niveau, le travail consiste à passer d'une configuration élémentaire à une conception reproductible. Le choix entre VPN IPsec à politiques de chiffrement et VPN à interface de tunnel influence le routage, la capacité à transporter plusieurs préfixes et le diagnostic. La distinction entre IKE SA et CHILD SA aide à comprendre pourquoi l'authentification peut réussir alors qu'aucun trafic utile ne circule. De même, une configuration cryptographique correctement négociée peut échouer à cause d'une route absente, d'un NAT mal placé, d'un réseau local qui se chevauche ou d'une MTU inadaptée.

Le cours met l'accent sur IPsec avec IKEv2, les interfaces de tunnel, GRE protégé par IPsec, les routes statiques et les protocoles de routage sur tunnel, le VPN d'accès distant, la haute disponibilité et l'exploitation. Les exemples utilisent principalement Cisco IOS/IOS XE et servent à illustrer les mécanismes. La syntaxe exacte, les algorithmes disponibles, les options de licence et le comportement du matériel varient selon la plateforme et la version : toute configuration doit être validée dans le guide correspondant au système cible avant d'être appliquée en production.

L'objectif est de pouvoir concevoir un VPN intermédiaire, expliquer ce qui est réellement protégé, vérifier les associations de sécurité, sélectionner les flux, confirmer la route aller-retour et isoler les causes d'incident avec des mesures plutôt qu'avec des changements aléatoires. Le cours inclut des scénarios pratiques, une matrice de tests, des exemples de configuration, des schémas et des exercices corrigés.

> **Analogie** : Le VPN est comparable à un service de transport sécurisé entre deux sites. IKEv2 sert à vérifier l'identité des partenaires et à préparer les clés ; IPsec protège les colis ; la route indique où les colis doivent aller ; les sélecteurs déterminent quels colis sont acceptés ; la surveillance permet de savoir si le service fonctionne. Si les partenaires se reconnaissent mais qu'aucun colis n'est dirigé vers le tunnel, le contrôle d'identité réussit sans que le service applicatif fonctionne. Il faut donc vérifier séparément l'identité, les clés, la politique, le routage et le trajet de retour.

---

## 1. La théorie et les algorithmes

### 1.1. Anatomie d'une architecture VPN intermédiaire

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

### 3.12. Glossaire intermédiaire

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

## Points à retenir

- IKEv2 protège la négociation et l'authentification des pairs ; les SA ESP protègent le trafic de données. Un état IKE établi ne garantit pas que le trafic applicatif circule.
- Le choix route-based ou policy-based doit être cohérent avec le routage, les sélecteurs, le NAT et les capacités des équipements.
- Les configurations des deux pairs doivent être compatibles sans élargir inutilement la liste d'algorithmes autorisés. Les recommandations cryptographiques doivent être vérifiées au moment du déploiement.
- Un tunnel GRE n'apporte pas de confidentialité par lui-même ; IPsec ou un mécanisme approprié est nécessaire lorsque le trafic traverse un réseau non fiable.
- Le transport externe vers le pair doit rester accessible indépendamment des routes internes qui passent dans le tunnel. Une route récursive peut interrompre la négociation.
- Les règles de pare-feu doivent refléter le transport réel : IKE sur UDP 500, NAT-T souvent sur UDP 4500, ESP comme protocole IP 50 et GRE comme protocole IP 47. ESP et GRE ne sont pas des ports TCP/UDP.
- Les routes retour, les politiques de filtrage, l'exemption NAT, les réseaux qui se chevauchent et les paramètres MTU/MSS sont des causes courantes de panne après l'établissement du tunnel.
- Un VPN d'accès distant doit associer identité, MFA, routes minimales, autorisations par rôle et visibilité opérationnelle. L'authentification seule ne suffit pas.
- La haute disponibilité doit être testée sur le service complet, avec mesure de convergence, perte de sessions et comportement applicatif, et non uniquement sur l'état de l'interface VPN.
- Une procédure rigoureuse s'appuie sur des journaux horodatés, des compteurs, des captures ciblées et une matrice de tests positifs et négatifs.

### Références techniques

1. IETF, **RFC 4301 — Security Architecture for the Internet Protocol** : architecture IPsec, politiques et associations de sécurité. https://www.rfc-editor.org/rfc/rfc4301.html
2. IETF, **RFC 7296 — Internet Key Exchange Protocol Version 2 (IKEv2)** : négociation et authentification des pairs, création des IKE SA et CHILD SA. https://www.rfc-editor.org/rfc/rfc7296.html
3. IETF, **RFC 3948 — UDP Encapsulation of IPsec ESP Packets** : transport ESP dans UDP pour la traversée NAT. https://www.rfc-editor.org/rfc/rfc3948.html
4. IETF, **RFC 4106 — The Use of Galois/Counter Mode (GCM) in IPsec ESP** : utilisation d'AES-GCM dans ESP. https://www.rfc-editor.org/rfc/rfc4106.html
5. IETF, **RFC 8221 — Cryptographic Algorithm Implementation Requirements and Usage Guidance for ESP** : exigences et conseils sur les algorithmes ESP. https://www.rfc-editor.org/rfc/rfc8221.html
6. IETF, **RFC 8247 — Algorithm Implementation Requirements and Usage Guidance for IKEv2** : exigences et recommandations relatives aux algorithmes IKEv2. https://www.rfc-editor.org/rfc/rfc8247.html
7. NIST, **SP 800-77 Rev. 1 — Guide to IPsec VPNs** : recommandations pratiques pour la mise en œuvre des VPN IPsec. https://csrc.nist.gov/pubs/sp/800/77/r1/final
8. Cisco, documentation **Security and VPN Configuration Guide — Cisco IOS XE 17.x**, comprenant les mécanismes IKEv2 et FlexVPN. https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/sec-vpn/b-security-vpn.html
9. Cisco, documentation de configuration FlexVPN client pour IOS XE 17.x : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/sec-vpn/b-security-vpn/m_sec-cfg-flex-clnt.html
10. WireGuard, documentation officielle du protocole et de la configuration : https://www.wireguard.com/
11. OpenVPN, documentation officielle et ressources communautaires : https://openvpn.net/community-resources/

Les standards et guides cités servent de base de vérification. Avant toute mise en production, utiliser la documentation correspondant à la version exacte de chaque équipement, examiner les mises à jour des RFC et appliquer la politique cryptographique de l'organisation. Les commandes d'exemple sont des supports de laboratoire, et non une configuration universelle prête à copier sur tous les routeurs.
