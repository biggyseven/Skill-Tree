# IPv6 — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Durée indicative :** 5 à 8 heures, selon les laboratoires et les comptes rendus  
**Prérequis :** avoir terminé `ipv6-debutant.md` ou maîtriser déjà la notation des adresses et préfixes IPv6, les types d'adresses courants, le rôle des Router Advertisements, les bases de SLAAC et NDP, ainsi que les vérifications élémentaires sous Windows, Linux ou Cisco IOS/IOS XE.  
**Environnement recommandé :** Cisco Packet Tracer pour les parties compatibles, deux ou trois routeurs/commutateurs L3 virtuels ou physiques, deux postes clients, Wireshark et un accès à la configuration du DNS ou à un service DNS de laboratoire.

Ce cours est la **suite directe du niveau Débutant**. Il ne reprend pas pas à pas la lecture d'une adresse ni la définition élémentaire de SLAAC. Il utilise ces acquis pour résoudre des problèmes réalistes : organiser les préfixes d'une entreprise, combiner SLAAC et DHCPv6, faire circuler les routes, comprendre les interactions DNS/double pile, analyser les messages ICMPv6, sécuriser les annonces de routeur et établir un diagnostic reproductible. Le niveau Expert pourra ensuite s'appuyer sur ce cours pour aborder l'architecture multi-sites, les protocoles de routage à grande échelle, la délégation automatisée, la haute disponibilité, l'observabilité avancée et la réponse aux incidents complexes.

> **Convention de laboratoire :** tous les préfixes `2001:db8::/32` utilisés ici sont réservés à la documentation. Ils sont adaptés aux exemples, pas au routage public en production. Les commandes Cisco sont des modèles IOS/IOS XE ; leur syntaxe et leur prise en charge dépendent du matériel et de la version. Fais les manipulations dans un environnement isolé, sauvegarde la configuration et vérifie les sorties réelles après chaque étape.


## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- concevoir un plan d'adressage IPv6 hiérarchique à partir d'un préfixe alloué ;
- choisir des préfixes cohérents pour les sites, VLAN, liens de transit et interfaces de bouclage ;
- interpréter les indicateurs de Router Advertisement et déterminer ce que l'hôte apprend par RA, SLAAC ou DHCPv6 ;
- distinguer DHCPv6 avec état, DHCPv6 sans état, relais DHCPv6 et délégation de préfixe (Prefix Delegation) ;
- configurer et contrôler des routes IPv6 statiques et comprendre le rôle introductif d'OSPFv3 ;
- diagnostiquer un problème lié au DNS AAAA, à la double pile ou à la sélection d'adresse ;
- utiliser une capture ICMPv6/NDP pour différencier les symptômes de couche 2, de routage et de pare-feu ;
- reconnaître les symptômes d'une panne PMTUD IPv6 ;
- appliquer les protections RA Guard et les contrôles NDP/DHCPv6 lorsque la plate-forme le permet ;
- réaliser un changement documenté avec critères de réussite et retour arrière ;
- rédiger un compte rendu qui distingue les observations, les hypothèses et la cause démontrée.

## Comment utiliser les supports

Le cours mélange quatre formats complémentaires :

1. **Schémas SVG animés** pour suivre les échanges sur les liaisons. Les points animés parcourent uniquement la ligne associée au message décrit ; ils représentent un échange conceptuel, pas une durée protocolaire exacte.
2. **Diagrammes textuels** qui restent lisibles si ton lecteur Markdown filtre le SVG.
3. **Tableaux et extraits de commandes** pour comparer les états et exécuter les vérifications.
4. **Laboratoires guidés** où tu dois relever l'état initial, modifier une seule variable, contrôler le résultat puis expliquer les preuves observées.

Certains lecteurs Markdown nettoient les balises SVG ou bloquent les animations intégrées. Si un schéma ne s'affiche pas correctement, utilise son diagramme textuel de remplacement ou ouvre temporairement le bloc SVG dans un navigateur récent. Les animations sont pédagogiques et ne remplacent jamais l'analyse d'une capture réelle.


## 1. Du préfixe isolé au plan d'adressage exploitable

### 1.1. Pourquoi un plan IPv6 se conçoit avant de configurer

Au niveau Débutant, tu as appris à lire une adresse et à reconnaître un préfixe tel que `2001:db8:10::/64`. Au niveau Intermédiaire, il faut décider **qui reçoit quelle partie de l'espace, selon quelle hiérarchie, et comment cette hiérarchie apparaîtra dans les routes, les ACL et les outils d'exploitation**.

Un plan d'adressage est plus qu'une liste d'adresses. Il doit refléter au moins les sites géographiques, les fonctions (utilisateurs, voix, serveurs, Wi-Fi, gestion), les zones de sécurité, les réseaux de transit et la croissance attendue. Une adresse bien choisie facilite l'agrégation des routes et permet à un technicien d'identifier rapidement le rôle probable d'un réseau.

Une organisation qui attribue les préfixes au hasard peut encore faire fonctionner IPv6, mais ses routes deviennent difficiles à résumer et ses règles de sécurité risquent d'être répétitives ou trop larges. À l'inverse, une allocation hiérarchique permet d'associer un bloc à un site, puis de découper ce bloc en sous-réseaux avec des règles de nommage et de documentation explicites.

### 1.2. Préfixe, sous-réseau et unité d'allocation

Un préfixe IPv6 est une suite de bits identifiant un bloc d'adresses. Le nombre après la barre oblique indique le nombre de bits fixes. Par exemple, `2001:db8:1200::/48` fixe les 48 premiers bits ; les bits restants permettent de subdiviser le bloc et d'identifier les interfaces.

Pour un LAN Ethernet classique, un `/64` est le format le plus courant et celui attendu par de nombreux mécanismes d'autoconfiguration SLAAC. Il ne faut donc pas supposer que l'on peut attribuer n'importe quelle longueur de préfixe à un LAN d'utilisateurs simplement parce que l'adresse IPv6 est grande. Les liens point-à-point routés peuvent être conçus différemment, mais le choix doit être cohérent avec l'équipement, les standards et les outils d'exploitation utilisés.

| Bloc de départ | Exemple de découpage pédagogique | Usage envisageable |
|---|---|---|
| `/32` | plusieurs blocs `/40`, `/48` ou `/56` | allocation très large, opérateur ou grand réseau |
| `/48` | 65 536 sous-réseaux `/64` possibles | site ou organisation avec besoin important de sous-réseaux |
| `/56` | 256 sous-réseaux `/64` | petit site ou délégation à un client, selon la politique d'allocation |
| `/60` | 16 sous-réseaux `/64` | site à taille limitée, si cela correspond au besoin réel |
| `/64` | réseau de lien classique | LAN, VLAN ou lien dont la conception retient `/64` |
| `/127` | deux adresses de préfixe | certains liens point-à-point entre routeurs, sous conditions adaptées |

Ces exemples décrivent des capacités binaires, pas une règle universelle qui imposerait à toute entreprise un `/48` ou à chaque client un `/56`. Les tailles d'allocation sont déterminées par le fournisseur, les politiques d'adressage, le besoin de croissance et les contraintes d'interconnexion.

### 1.3. Exemple de plan hiérarchique

Supposons qu'un laboratoire utilise le bloc de documentation `2001:db8:1200::/48`. On peut attribuer le quatrième groupe hexadécimal à une zone ou à une fonction de site, puis utiliser un `/64` par VLAN.

```text
Bloc de démonstration : 2001:db8:1200::/48
│
├── Siège : 2001:db8:1200:0000::/56
│   ├── VLAN utilisateurs : 2001:db8:1200:0010::/64
│   ├── VLAN serveurs    : 2001:db8:1200:0020::/64
│   ├── VLAN voix        : 2001:db8:1200:0030::/64
│   └── VLAN gestion     : 2001:db8:1200:00f0::/64
│
├── Site A : 2001:db8:1200:0100::/56
│   ├── Utilisateurs     : 2001:db8:1200:0101::/64
│   └── Serveurs locaux  : 2001:db8:1200:0102::/64
│
└── Réserve de croissance : documentée, non attribuée au hasard
```

Dans un `/48`, les 16 bits suivants permettent de former 65 536 identifiants de sous-réseaux `/64`. Dans cet exemple, les étiquettes humaines « siège », « VLAN utilisateurs » et « site A » doivent être consignées dans une feuille d'adressage ; il ne faut pas supposer que le sens de chaque hextet est compréhensible sans documentation.

Évite de réutiliser le même `/64` sur deux liens indépendants qui doivent être routés séparément. Des exceptions existent dans certains designs spécialisés, mais elles demandent une justification technique explicite. Dans un réseau campus ordinaire, un VLAN de couche 2 distinct reçoit généralement son propre préfixe IPv6.

### 1.4. Global Unicast et Unique Local Address

Les adresses Global Unicast (GUA) sont généralement issues de l'espace global `2000::/3` et peuvent être routées mondialement si elles sont valides, allouées et annoncées correctement. Une adresse GUA n'est pas automatiquement accessible depuis Internet : le routage, le filtrage, les politiques du fournisseur et l'état du service restent déterminants.

Les Unique Local Addresses (ULA), dans `fc00::/7` et communément utilisées dans `fd00::/8`, sont destinées à la communication locale ou inter-sites contrôlée, pas au routage public sur Internet. Un préfixe ULA doit être choisi de façon à réduire le risque de chevauchement lorsqu'on fusionne des réseaux ou relie plusieurs sites ; la génération d'un Global ID pseudo-aléatoire selon la procédure recommandée est préférable à l'invention du même préfixe par plusieurs équipes.

| Besoin | Choix fréquent | Points de contrôle |
|---|---|---|
| Services devant être adressables avec une identité publique stable | GUA | allocation réelle, DNS, route, filtrage et politique de publication |
| Réseau interne indépendant d'une allocation opérateur | ULA, éventuellement en complément d'une GUA | unicité du préfixe, routes internes, DNS interne, pas d'annonce publique accidentelle |
| Réseau isolé de laboratoire | préfixe de documentation pour exemples et captures | ne pas annoncer `2001:db8::/32` comme préfixe de production |
| Infrastructure avec IPv4 et IPv6 | double pile planifiée | règles de sécurité, DNS, monitoring et procédure de dépannage pour les deux piles |

Un réseau peut utiliser simultanément GUA et ULA. Cette coexistence ajoute des choix de source et de destination : un service peut être joignable par une adresse et pas par l'autre. Les ACL, les enregistrements DNS et les routes doivent être cohérents avec la portée voulue.

### 1.5. Préparer un plan avant de configurer

Pour chaque préfixe, documente les éléments suivants :

- identifiant du site et propriétaire du réseau ;
- rôle du sous-réseau ou du VLAN ;
- préfixe et longueur ;
- adresse de passerelle ou convention d'adresse du routeur ;
- méthode de configuration des hôtes (SLAAC, DHCPv6, configuration manuelle ou combinaison) ;
- serveurs DNS et domaine de recherche attendus ;
- politique de routage et de filtrage ;
- durée de vie et stratégie de changement, lorsqu'elles sont applicables ;
- routeur ou service qui annonce le préfixe ;
- procédure de test et de retour arrière.

L'idée n'est pas de remplir un formulaire pour le plaisir. Une feuille d'adressage fiable rend possible une comparaison entre la conception et les sorties réelles des équipements. Elle facilite aussi la détection des préfixes non documentés, des annonces inattendues et des routes plus spécifiques qui détournent certains flux.


<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" role="img" aria-label="Découpage animé d'un préfixe IPv6 vers des sous-réseaux de site, VLAN et transit" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><style>.box{fill:#111827;stroke:#64748b;stroke-width:1.5}.txt{fill:#f8fafc;font-size:15px}.sub{fill:#cbd5e1;font-size:12px}.line{fill:none;stroke:#60a5fa;stroke-width:2.5}.pulse{fill:#34d399;stroke:#052e24;stroke-width:1.5}</style></defs>
  <rect class="box" x="310" y="18" width="280" height="56" rx="12"/>
  <text class="txt" x="450" y="42" text-anchor="middle">Préfixe attribué</text><text class="sub" x="450" y="60" text-anchor="middle">2001:db8:1200::/48 (exemple)</text>
  <path class="line" d="M450 74 V105 H150 V137 M450 105 V137 M450 105 H750 V137"/>
  <g transform="translate(450 74)"><circle class="pulse" cx="0" cy="0"><animateMotion dur="3s" repeatCount="indefinite" path="M0 0 V31 H-300 V63"/></circle></g>
  <g transform="translate(450 74)"><circle class="pulse" cx="0" cy="0"><animateMotion dur="3s" begin="1s" repeatCount="indefinite" path="M0 0 V31 H0 V63"/></circle></g>
  <g transform="translate(450 74)"><circle class="pulse" cx="0" cy="0"><animateMotion dur="3s" begin="2s" repeatCount="indefinite" path="M0 0 V31 H300 V63"/></circle></g>
  <rect class="box" x="45" y="137" width="210" height="60" rx="10"/><text class="txt" x="150" y="161" text-anchor="middle">Site / zone A</text><text class="sub" x="150" y="180" text-anchor="middle">Bloc réservé au site</text>
  <rect class="box" x="345" y="137" width="210" height="60" rx="10"/><text class="txt" x="450" y="161" text-anchor="middle">Site / zone B</text><text class="sub" x="450" y="180" text-anchor="middle">Bloc distinct</text>
  <rect class="box" x="645" y="137" width="210" height="60" rx="10"/><text class="txt" x="750" y="161" text-anchor="middle">Transit / réserve</text><text class="sub" x="750" y="180" text-anchor="middle">Règles documentées</text>
  <path class="line" d="M150 197 V224 H92 V244 M150 224 H208 V244 M450 197 V244 M750 197 V244"/>
  <rect class="box" x="24" y="244" width="136" height="62" rx="8"/><text class="txt" x="92" y="268" text-anchor="middle">VLAN 10</text><text class="sub" x="92" y="286" text-anchor="middle">/64</text>
  <rect class="box" x="172" y="244" width="136" height="62" rx="8"/><text class="txt" x="240" y="268" text-anchor="middle">VLAN 20</text><text class="sub" x="240" y="286" text-anchor="middle">/64</text>
  <rect class="box" x="382" y="244" width="136" height="62" rx="8"/><text class="txt" x="450" y="268" text-anchor="middle">VLAN 30</text><text class="sub" x="450" y="286" text-anchor="middle">/64</text>
  <rect class="box" x="682" y="244" width="136" height="62" rx="8"/><text class="txt" x="750" y="268" text-anchor="middle">Transit</text><text class="sub" x="750" y="286" text-anchor="middle">selon design</text>
  <text class="sub" x="450" y="338" text-anchor="middle">Un plan hiérarchique facilite la synthèse, la supervision et le dépannage.</text>
</svg>
</div>

**Lecture du schéma :** le mouvement montre la délégation logique des blocs, pas des paquets réels qui circulent dans le réseau. Chaque `/64` représente un préfixe distinct dans un LAN courant ; le transit est défini selon le design retenu.


## 2. Lire les Router Advertisements au-delà des notions de base

### 2.1. Le RA est une source de paramètres, pas seulement une adresse de routeur

Un Router Advertisement (RA), message ICMPv6 de type 134, peut transporter des informations sur le routeur par défaut, des préfixes, la durée de vie du routeur, une MTU de lien et des paramètres qui orientent le comportement de configuration des hôtes. Les détails visibles varient selon les options réellement émises et la capture utilisée.

Le poste ne doit donc pas être diagnostiqué uniquement à partir de `ipconfig` ou de `ip -6 address`. Deux machines sur le même VLAN peuvent recevoir le même préfixe mais se comporter différemment si elles interprètent différemment les indications ou si elles ont un DHCPv6, un DNS, un pare-feu ou une politique de sélection d'adresse différente.

Le point de départ d'un diagnostic sérieux est de capturer un RA valide sur le lien, puis d'inspecter les options : préfixe annoncé, indicateurs A et L de l'option Prefix Information, durées de vie, drapeau M, drapeau O, MTU et durée de vie du routeur. Il faut aussi vérifier si plusieurs routeurs émettent des RA différents sur le même lien.

### 2.2. Drapeaux M et O : indications, pas la totalité de la configuration

Les drapeaux historiques du RA sont souvent décrits de cette façon :

- **M (Managed address configuration)** : indique que les hôtes peuvent utiliser DHCPv6 pour obtenir des adresses avec état ;
- **O (Other configuration)** : indique que des informations de configuration supplémentaires sont disponibles via DHCPv6, par exemple DNS, selon le serveur et le client ;
- les informations de préfixe et l'indicateur A peuvent permettre à l'hôte d'utiliser SLAAC ;
- l'indicateur L dans Prefix Information précise si le préfixe est considéré « on-link » dans le contexte correspondant.

Ne transforme pas ces indicateurs en règle trop simpliste. Un hôte peut utiliser SLAAC et DHCPv6 en même temps. Les comportements exacts varient selon le système d'exploitation, la politique locale et les extensions implémentées. Le RA joue également un rôle essentiel dans la route par défaut : DHCPv6 ne remplace pas à lui seul la découverte du routeur par défaut au moyen de RA.

| Élément observé | Ce qu'il peut indiquer | Ce qu'il ne prouve pas à lui seul |
|---|---|---|
| M = 1 | DHCPv6 avec état peut être utilisé pour les adresses | que chaque client a reçu un bail ou qu'un serveur est joignable |
| O = 1 | des informations supplémentaires peuvent être obtenues via DHCPv6 | que DNS est correct et que les clients l'ont installé |
| A = 1 dans une option de préfixe | SLAAC est autorisé pour ce préfixe sous les autres conditions requises | que le client a réussi DAD ou qu'il possède une route vers Internet |
| L = 1 dans une option de préfixe | le préfixe est indiqué comme on-link | que chaque équipement supposé local répond réellement |
| durée de vie du routeur > 0 | le routeur est candidat à devenir routeur par défaut | que le prochain saut dispose d'une connectivité Internet saine |
| durée de vie du routeur = 0 | le RA n'annonce pas ce routeur comme défaut au-delà des autres règles applicables | que toutes les autres informations du RA doivent être ignorées |

### 2.3. Deux routeurs qui émettent des RA

Un lien peut voir plusieurs routeurs IPv6. Ils peuvent annoncer des préfixes distincts, avoir des préférences différentes, présenter différentes durées de vie et fournir des options incohérentes. Le fait que le poste possède une bonne adresse ne garantit pas que la route par défaut pointe vers le routeur attendu.

Exemple de symptomatique : un poste obtient une GUA valide et peut joindre un serveur du même VLAN, mais une partie des connexions sortantes échoue. La capture affiche deux RA : l'un est légitime ; l'autre annonce une route par défaut vers un routeur qui n'a pas de route amont correcte. Il faut identifier l'émetteur de chaque RA et la politique réseau, pas désactiver tout ICMPv6.

```text
                 VLAN CLIENTS

        +-------------------+
        | PC-01              |
        | GUA + route défaut |
        +-------------------+
             ^          ^
             | RA       | RA inattendu
             |          |
       +-----------+  +-----------+
       | R1 valide |  | R2 parasite|
       | routage OK|  | sans amont |
       +-----------+  +-----------+

Question de diagnostic : qui a annoncé la route réellement choisie ?
```

Dans un réseau commuté administré, une protection de type RA Guard peut aider à empêcher des ports d'utilisateurs d'émettre des RA indésirables. Cette protection doit être configurée avec attention : les ports faisant face aux routeurs légitimes doivent être identifiés, et la prise en charge matérielle/logicielle doit être confirmée sur la plate-forme utilisée.


<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" role="img" aria-label="Échange animé Router Solicitation puis Router Advertisement entre un poste et son routeur" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><style>.b{fill:#111827;stroke:#64748b;stroke-width:1.5}.t{fill:#f8fafc;font-size:16px}.s{fill:#cbd5e1;font-size:12px}.p{stroke:#64748b;stroke-width:2.5;fill:none}.a{fill:#38bdf8;stroke:#082f49;stroke-width:1.4}.r{fill:#fbbf24;stroke:#451a03;stroke-width:1.4}</style></defs>
  <rect class="b" x="55" y="70" width="240" height="170" rx="15"/><text class="t" x="175" y="103" text-anchor="middle">PC client</text><text class="s" x="175" y="127" text-anchor="middle">Link-local présente</text><text class="s" x="175" y="148" text-anchor="middle">Recherche les paramètres</text>
  <rect class="b" x="605" y="70" width="240" height="170" rx="15"/><text class="t" x="725" y="103" text-anchor="middle">Routeur R1</text><text class="s" x="725" y="127" text-anchor="middle">Préfixe et paramètres</text><text class="s" x="725" y="148" text-anchor="middle">Routeur par défaut</text>
  <path class="p" d="M295 155 H605"/><text class="s" x="450" y="142" text-anchor="middle">Lien IPv6 local</text>
  <path d="M310 165 H580" stroke="#38bdf8" stroke-width="2.5" fill="none" stroke-dasharray="7 5"/><text class="s" x="450" y="185" text-anchor="middle">RS · ICMPv6 type 133</text><g transform="translate(310 165)"><circle class="a" r="7" cx="0" cy="0"><animateMotion dur="2.8s" repeatCount="indefinite" path="M0 0 H270"/></circle></g>
  <path d="M580 210 H310" stroke="#fbbf24" stroke-width="2.5" fill="none" stroke-dasharray="7 5"/><text class="s" x="450" y="233" text-anchor="middle">RA · ICMPv6 type 134</text><g transform="translate(580 210)"><circle class="r" r="7" cx="0" cy="0"><animateMotion dur="3.2s" begin=".7s" repeatCount="indefinite" path="M0 0 H-270"/></circle></g>
  <rect class="b" x="315" y="270" width="270" height="55" rx="10"/><text class="t" x="450" y="293" text-anchor="middle">Le client interprète le RA</text><text class="s" x="450" y="311" text-anchor="middle">préfixe · route · indicateurs · MTU</text>
</svg>
</div>

Le schéma suit deux lignes séparées : la requête RS parcourt la liaison du client vers le routeur, puis le RA parcourt la liaison en sens inverse. Les systèmes peuvent aussi recevoir périodiquement des RA sans envoyer de RS juste avant.


## 3. SLAAC et DHCPv6 : concevoir les modes de configuration

### 3.1. SLAAC ne donne pas nécessairement tous les paramètres de l'entreprise

SLAAC permet à un hôte de former une adresse à partir des informations de préfixe annoncées par un routeur et d'un identifiant d'interface généré selon l'implémentation. Les hôtes réalisent la détection de doublon (DAD) avant d'utiliser une adresse, mais les mécanismes précis de génération de l'identifiant peuvent être stables, temporaires ou liés à une politique de confidentialité.

SLAAC ne doit pas être assimilé à un système central d'inventaire. Un administrateur peut connaître le préfixe et voir les adresses actives, sans que le routeur attribue une adresse précise par poste. Lorsque l'exploitation exige une correspondance administrative stricte entre hôte, adresse et durée d'attribution, il faut choisir une stratégie adaptée : DHCPv6 avec état, réservation lorsque disponible, inventaire de postes, DNS dynamique ou mécanisme de gestion complémentaire.

### 3.2. DHCPv6 avec état et sans état

DHCPv6 peut attribuer des adresses et/ou fournir d'autres paramètres. Le mode sans état est souvent utilisé en complément de SLAAC pour obtenir des informations comme les DNS et la liste de recherche de domaine. Le mode avec état permet au serveur de gérer l'attribution d'adresses aux clients. Le détail du résultat dépend des options prises en charge par le client et le serveur.

| Mode | Origine habituelle de l'adresse d'hôte | Rôle éventuel de DHCPv6 | Route par défaut |
|---|---|---|---|
| SLAAC seul | hôte, à partir du préfixe de RA | aucun serveur requis pour la formation d'adresse | apprise par RA |
| SLAAC + DHCPv6 sans état | SLAAC | paramètres supplémentaires, par exemple DNS | apprise par RA |
| DHCPv6 avec état | DHCPv6 pour les adresses gérées, selon la configuration client/RA | serveur garde les associations et paramètres prévus | toujours traitée via RA dans le modèle courant, pas par la seule attribution DHCPv6 |
| configuration statique | administrateur ou gestion automatisée | aucune nécessité pour l'adresse si tout est statique | configuration locale ou apprise par RA selon politique |
| combinaison entreprise | stratégie définie par interface ou segment | SLAAC et DHCPv6 peuvent coexister | RA, avec contrôles et cohérence des routes |

Ne déduis pas automatiquement le fonctionnement client du seul M/O du RA. Contrôle sur le poste quels paramètres ont réellement été installés, puis compare-les à la capture et à la configuration du routeur.

### 3.3. Séquence DHCPv6 et lecture d'une capture

Dans la séquence typique d'attribution avec serveur, le client peut envoyer **Solicit**, un ou plusieurs serveurs répondent par **Advertise**, le client choisit et envoie **Request**, puis le serveur répond **Reply**. Des messages comme Renew, Rebind, Release, Decline, Confirm, Information-request ou Relay-forward/Relay-reply interviennent dans d'autres situations. La séquence exacte varie avec le mode d'échange, les options et le protocole défini par la version en vigueur.

Le but de Wireshark n'est pas seulement de mémoriser quatre noms. Il faut identifier le premier échange qui manque : aucun Solicit (problème client ou politique), Solicit sans réponse (réseau/relay/serveur), Advertise sans Request (choix ou traitement client), Request sans Reply (serveur, filtrage ou chemin de retour), Reply reçue mais paramètres absents (client, conflit de configuration ou option non appliquée).

```text
Client IPv6             Relais (si requis)             Serveur DHCPv6
    |                           |                              |
    |---------- Solicit ------->|----------------------------->|
    |                           |<---------------- Advertise --|
    |<-------- Advertise -------|                              |
    |---------- Request ------->|----------------------------->|
    |                           |<---------------- Reply ------|
    |<----------- Reply --------|                              |
    |                           |                              |
    +---- Vérifier adresse, DNS et durée de vie réellement appliqués
```

Le diagramme est simplifié : les messages de relais encapsulent les échanges selon le protocole et certaines séquences peuvent différer. La capture doit être interprétée en fonction du service demandé et de la configuration utilisée.

### 3.4. DUID et IAID : identifier le client sans supposer l'adresse MAC

DHCPv6 emploie un **DUID** (DHCP Unique Identifier) pour identifier le client ou le serveur, et un **IAID** (Identity Association Identifier) pour distinguer une association d'identité/adresse liée à une interface ou à un besoin. Une réservation DHCPv6 ne se pense donc pas toujours comme une simple association « adresse MAC → IPv6 » telle qu'on la rencontre souvent dans des exemples DHCPv4.

Dans un diagnostic, relever le DUID et l'IAID dans la capture peut expliquer pourquoi un serveur considère une demande comme provenant d'un client déjà connu, ou pourquoi une réinstallation/suppression de configuration change le comportement attendu. Les formats de DUID et les choix de persistance dépendent du client et du système ; documente ce que l'équipement émet réellement.

### 3.5. DHCPv6 Relay

Le relais DHCPv6 permet de faire communiquer des clients et des serveurs qui ne se trouvent pas sur le même lien. Sans relais ou mécanisme équivalent correctement configuré, un serveur situé dans un autre sous-réseau ne recevra pas nécessairement le message client local.

Un relais est une fonction de chemin : il ne doit pas être supposé capable d'inventer un préfixe, de configurer le RA ou de remplacer le routeur local. Contrôle l'interface où se trouvent les clients, la destination du serveur, le chemin de retour, les règles de filtrage et la manière dont le relais identifie le lien d'origine. Les options et commandes de relais varient beaucoup selon les plateformes.

### 3.6. Prefix Delegation (DHCPv6-PD)

La délégation de préfixe répond à un problème différent de l'attribution d'une seule adresse à un poste. Un routeur client demande à un routeur amont de lui déléguer un bloc IPv6 qu'il pourra subdiviser pour ses propres LAN. Ce mécanisme est courant dans certains services d'accès Internet et dans des architectures de sites clients.

Exemple conceptuel : l'amont délègue `2001:db8:7800::/56` à un routeur de site ; celui-ci attribue un `/64` distinct au réseau utilisateurs, un autre au réseau IoT et un autre au réseau serveurs. Les RA sur chaque LAN annoncent le préfixe correspondant. Si le préfixe délégué change, la renumérotation et la mise à jour des routes/DNS deviennent un sujet d'exploitation, pas seulement une nouvelle valeur sur l'interface WAN.

```text
Routeur amont / serveur DHCPv6-PD
        |
        | délègue un bloc, ex. /56
        v
Routeur du site
        |-- LAN utilisateurs : un /64
        |-- LAN voix        : un /64
        |-- LAN serveurs    : un /64
        `-- LAN invités     : un /64
```

Le préfixe d'exemple est réservé à la documentation. Pour un service réel, la taille déléguée est fixée par l'opérateur ou la politique d'allocation. Le routeur demandeur doit gérer le bloc et ses routes conformément à son implémentation.

### 3.7. Durées de vie : preferred, valid et durée de vie du routeur

Une adresse SLAAC possède une durée de vie préférée et une durée de vie valide. Une adresse dépréciée reste généralement utilisable pour certaines communications existantes, mais elle ne devrait pas être choisie pour initier de nouvelles communications si une adresse préférée adaptée existe. Quand sa durée de vie valide expire, elle devient invalide.

Cette distinction devient importante lors d'une renumérotation. Si le routeur annonce le nouveau préfixe sans gérer correctement les durées de vie de l'ancien, certains clients peuvent continuer à sélectionner une ancienne adresse ou à garder des routes/destinations en cache. À l'inverse, annoncer des durées de vie trop courtes sans préparation peut provoquer des renouvellements, des changements d'adresse et des incidents difficiles à reproduire.

Un changement de préfixe doit donc être planifié avec les équipements de routage, les RA, le DNS, les ACL, la supervision et les applications. Le processus d'annulation doit préciser comment restaurer le préfixe précédent et quelles durées de vie seront vues par les clients.


<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" role="img" aria-label="DHCPv6 avec état : Solicit Advertise Request Reply parcourent les liaisons entre client, routeur relais et serveur" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><style>.n{fill:#111827;stroke:#64748b;stroke-width:1.5}.tx{fill:#f8fafc;font-size:15px}.sm{fill:#cbd5e1;font-size:12px}.ln{fill:none;stroke:#475569;stroke-width:2.2}.p1{fill:#38bdf8;stroke:#082f49;stroke-width:1.2}.p2{fill:#fbbf24;stroke:#451a03;stroke-width:1.2}</style></defs>
  <rect class="n" x="20" y="55" width="210" height="245" rx="12"/><text class="tx" x="125" y="87" text-anchor="middle">Client</text><text class="sm" x="125" y="108" text-anchor="middle">sur le LAN</text>
  <rect class="n" x="345" y="55" width="210" height="245" rx="12"/><text class="tx" x="450" y="87" text-anchor="middle">Relais optionnel</text><text class="sm" x="450" y="108" text-anchor="middle">routeur / L3</text>
  <rect class="n" x="670" y="55" width="210" height="245" rx="12"/><text class="tx" x="775" y="87" text-anchor="middle">Serveur DHCPv6</text><text class="sm" x="775" y="108" text-anchor="middle">pool et options</text>
  <path class="ln" d="M230 170 H345 M555 170 H670"/>
  <path d="M245 143 H330 M570 143 H655" stroke="#38bdf8" stroke-width="2.4" stroke-dasharray="6 4" fill="none"/><g transform="translate(245 143)"><circle class="p1" r="6" cx="0" cy="0"><animateMotion dur="2.3s" repeatCount="indefinite" path="M0 0 H85"/></circle></g><g transform="translate(570 143)"><circle class="p1" r="6" cx="0" cy="0"><animateMotion dur="2.3s" begin="1.2s" repeatCount="indefinite" path="M0 0 H85"/></circle></g><text class="sm" x="287" y="132" text-anchor="middle">Sol./Req.</text><text class="sm" x="612" y="132" text-anchor="middle">Relayed</text>
  <path d="M655 205 H570 M330 205 H245" stroke="#fbbf24" stroke-width="2.4" stroke-dasharray="6 4" fill="none"/><g transform="translate(655 205)"><circle class="p2" r="6" cx="0" cy="0"><animateMotion dur="2.3s" repeatCount="indefinite" path="M0 0 H-85"/></circle></g><g transform="translate(330 205)"><circle class="p2" r="6" cx="0" cy="0"><animateMotion dur="2.3s" begin="1.2s" repeatCount="indefinite" path="M0 0 H-85"/></circle></g><text class="sm" x="612" y="225" text-anchor="middle">Adv./Reply</text><text class="sm" x="287" y="225" text-anchor="middle">Réponse</text>
  <text class="sm" x="125" y="260" text-anchor="middle">Vérifier DUID/IAID</text><text class="sm" x="450" y="260" text-anchor="middle">Vérifier relais et retour</text><text class="sm" x="775" y="260" text-anchor="middle">Vérifier scope et journal</text>
  <text class="sm" x="450" y="333" text-anchor="middle">L'absence du premier message attendu localise déjà une partie du problème.</text>
</svg>
</div>


## 4. Routage IPv6 : de l'interface à la table de routage

### 4.1. Une adresse d'interface ne suffit pas

Une interface peut posséder une adresse GUA correcte et communiquer avec un voisin directement connecté, alors que tout trafic vers un autre préfixe échoue. Cela arrive si le routage IPv6 n'est pas activé sur le routeur, si une route distante manque, si une route retour est absente ou si une ACL bloque le trafic.

Pour un routeur, sépare trois questions :

1. **Interface :** est-elle active et porte-t-elle le préfixe attendu ?
2. **Table de routage :** existe-t-il une route vers la destination, et par quel prochain saut ?
3. **Retour :** le réseau distant sait-il renvoyer les paquets vers le préfixe source ?

Une commande de ping peut échouer pour d'autres raisons, dont filtrage ICMPv6, absence de résolution du voisin ou limitation du service. Il faut comparer avec une route, une capture ou un test applicatif contrôlé.

### 4.2. Activer le routage IPv6 sur Cisco IOS/IOS XE

Sur beaucoup de plateformes Cisco IOS/IOS XE, les interfaces peuvent être adressées en IPv6, mais la fonction de transfert unicast IPv6 doit également être activée au niveau global.

```cisco
configure terminal
ipv6 unicast-routing
!
interface GigabitEthernet0/0
 description LAN-UTILISATEURS
 ipv6 address 2001:DB8:1200:10::1/64
 no shutdown
!
interface GigabitEthernet0/1
 description LIEN-VERS-R2
 ipv6 address 2001:DB8:1200:ff01::1/64
 no shutdown
end
show ipv6 interface brief
show ipv6 route
```

Les interfaces de cet exemple et la syntaxe doivent être adaptées à l'équipement. N'utilise pas un préfixe de documentation sur un réseau de production connecté à Internet. Vérifie que l'interface est opérationnelle et que la route connectée apparaît avant d'ajouter des routes distantes.

### 4.3. Route statique vers un préfixe distant

Une route IPv6 statique indique explicitement le préfixe de destination et le prochain saut, ou l'interface de sortie avec les conditions propres à la plate-forme. Sur des liens Ethernet multi-accès, spécifier seulement une interface de sortie peut conduire à une résolution de voisin ambiguë ou non souhaitée ; le choix de la forme de route doit correspondre à la topologie.

Exemple schématique avec deux routeurs :

```text
LAN A -- R1 -------- R2 -- LAN B
2001:db8:1200:10::/64  2001:db8:1200:20::/64
             transit : 2001:db8:1200:ff01::/64
```

Sur R1, un modèle de route vers le LAN B peut ressembler à :

```cisco
ipv6 route 2001:DB8:1200:20::/64 2001:DB8:1200:FF01::2
```

Sur R2, il faut une route retour vers le LAN A, par exemple :

```cisco
ipv6 route 2001:DB8:1200:10::/64 2001:DB8:1200:FF01::1
```

La route retour est essentielle. La présence d'une route dans un sens ne garantit pas la communication bidirectionnelle.

Vérifications courantes :

```cisco
show ipv6 route
show ipv6 route 2001:DB8:1200:20::/64
show ipv6 interface brief
ping ipv6 2001:DB8:1200:FF01::2
traceroute ipv6 2001:DB8:1200:20::10
```

La syntaxe exacte de ping/traceroute change selon IOS/IOS XE. Certaines versions utilisent des commandes interactives ou des paramètres additionnels pour préciser l'adresse source. Lorsque le ping échoue, précise la source : une interface de transit peut répondre correctement, tandis que le chemin depuis le LAN utilisateur peut avoir une route retour absente.

### 4.4. Choix du prochain saut et adresses link-local

Les adresses link-local, généralement dans `fe80::/10`, sont utilisées sur un seul lien et sont souvent présentes sur les interfaces des routeurs. Elles peuvent servir de prochain saut dans certains protocoles de routage ou commandes, mais comme la même plage link-local peut exister sur plusieurs interfaces, il faut identifier le contexte d'interface.

Sur Linux, une commande telle que `ping -6 fe80::1%eth0` utilise l'identifiant d'interface (zone/scope) pour lever l'ambiguïté. Une simple adresse `fe80::1` sans contexte peut être insuffisante si plusieurs interfaces sont possibles. Sur Cisco, les commandes de route et leurs formes acceptées varient ; consulte l'aide intégrée (`?`) et la documentation IOS/IOS XE exacte.

### 4.5. Comprendre la sélection d'adresse source

Une machine IPv6 peut disposer de plusieurs adresses sur la même interface : link-local, globale stable, temporaire, ULA ou adresse dépréciée. Le système choisit une adresse source en fonction de règles de sélection, du scope, du statut de l'adresse, du préfixe de destination et de politiques locales. Le résultat peut surprendre un technicien qui suppose qu'une seule adresse existe.

Exemple : un client a `2001:db8:1200:10::25` et `fdab:1234:5678:10::25`. Le serveur interne dispose d'une route ULA et d'une GUA de documentation dans le laboratoire. Selon les routes et les règles de sélection, le client peut choisir une source différente de celle qu'attend le pare-feu. Lorsqu'un flux échoue, relève explicitement source et destination dans la capture : cela évite de confondre route absente et adresse source non permise par une ACL.

### 4.6. Première approche d'OSPFv3

Les routes statiques conviennent à un laboratoire court ou à une petite topologie. Un réseau avec beaucoup de préfixes doit éviter les routes manuelles incohérentes et peut utiliser un protocole de routage dynamique, par exemple OSPFv3 lorsque la conception et les équipements le justifient.

OSPFv3 est un protocole à état de liens. Les routeurs établissent des voisinages sur les liens compatibles, échangent des informations de topologie et calculent les meilleurs chemins. Selon la version et le mode (OSPFv3 traditionnel, address families, différences IOS/IOS XE), la syntaxe d'activation IPv6 peut varier. Ne mélange pas les syntaxes d'exemples de générations logicielles différentes.

Modèle pédagogique ancien/compatibilité IOS, à vérifier sur la plate-forme :

```cisco
ipv6 unicast-routing
!
interface GigabitEthernet0/1
 ipv6 address 2001:DB8:1200:FF01::1/64
 ipv6 ospf 10 area 0
!
ipv6 router ospf 10
 router-id 1.1.1.1
```

Sur des versions IOS XE plus récentes, l'activation et la famille d'adresses peuvent être configurées sous `router ospfv3` et `address-family ipv6 unicast`. Consulte la référence correspondant au logiciel. Le `router-id` est un identifiant de 32 bits écrit sous forme IPv4 ; il ne s'agit pas d'une adresse IPv4 qui serait utilisée comme prochain saut de trafic IPv6.

Avant de déployer OSPFv3, définis les routeurs participants, les aires, les interfaces, les réseaux annoncés, l'authentification et les règles de redistribution éventuelle. Pour un premier lab, limite-toi à une aire unique et à deux routeurs. Vérifie les voisinages et les routes apprises avant d'ajouter d'autres paramètres.

Commandes de vérification courantes (variantes selon plateforme) :

```cisco
show ipv6 route
show ipv6 ospf neighbor
show ipv6 ospf interface
show ipv6 protocols
```

Un voisinage OSPF qui ne s'établit pas peut être causé par une interface down, une zone incompatible, un filtrage du protocole, une absence d'activation sur l'interface ou des paramètres incohérents. Un voisinage établi ne prouve pas que toutes les routes attendues sont installées : contrôle séparément la base de routage, les filtres et la route retour.


<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="Paquet IPv6 traverse deux routeurs selon la table de routage, puis attend un chemin retour" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><style>.b{fill:#111827;stroke:#64748b;stroke-width:1.5}.t{fill:#f8fafc;font-size:15px}.s{fill:#cbd5e1;font-size:12px}.l{stroke:#38bdf8;stroke-width:3;fill:none}.d{stroke:#64748b;stroke-width:2;fill:none;stroke-dasharray:6 5}.p{fill:#34d399;stroke:#052e24;stroke-width:1.4}</style></defs>
  <rect class="b" x="20" y="90" width="175" height="95" rx="12"/><text class="t" x="108" y="120" text-anchor="middle">PC-A</text><text class="s" x="108" y="142" text-anchor="middle">source IPv6</text><text class="s" x="108" y="160" text-anchor="middle">2001:db8:...:10::25</text>
  <rect class="b" x="260" y="90" width="145" height="95" rx="12"/><text class="t" x="332" y="120" text-anchor="middle">R1</text><text class="s" x="332" y="142" text-anchor="middle">route vers B</text><text class="s" x="332" y="160" text-anchor="middle">next-hop R2</text>
  <rect class="b" x="490" y="90" width="145" height="95" rx="12"/><text class="t" x="562" y="120" text-anchor="middle">R2</text><text class="s" x="562" y="142" text-anchor="middle">route LAN B</text><text class="s" x="562" y="160" text-anchor="middle">route retour requise</text>
  <rect class="b" x="700" y="90" width="175" height="95" rx="12"/><text class="t" x="788" y="120" text-anchor="middle">PC-B</text><text class="s" x="788" y="142" text-anchor="middle">destination IPv6</text><text class="s" x="788" y="160" text-anchor="middle">2001:db8:...:20::20</text>
  <path class="d" d="M195 137 H260 M405 137 H490 M635 137 H700"/>
  <path class="l" d="M195 137 H260 M405 137 H490 M635 137 H700"/>
  <g transform="translate(195 137)"><circle class="p" cx="0" cy="0"><animateMotion dur="4s" repeatCount="indefinite" path="M0 0 H65 H210 H295 H440 H505"/></circle></g>
  <text class="s" x="450" y="225" text-anchor="middle">Un aller fonctionnel ne prouve pas le retour.</text>
  <path class="d" d="M788 185 V260 H108 V185"/><text class="s" x="450" y="282" text-anchor="middle">Route de retour vers le préfixe source + filtrage cohérent</text>
</svg>
</div>


## 5. DNS IPv6 et fonctionnement en double pile

### 5.1. Enregistrements AAAA et PTR

Un enregistrement DNS **AAAA** associe un nom à une adresse IPv6, de même que l'enregistrement A associe un nom à une adresse IPv4. La présence d'un AAAA signifie que le DNS publie une adresse IPv6 ; elle ne démontre pas que le service écoute sur cette adresse, que la route existe ou que le pare-feu autorise le trafic.

Le DNS inverse IPv6 utilise la zone `ip6.arpa` et représente l'adresse sous forme de nibbles hexadécimaux inversés. En pratique, la configuration de la délégation DNS inverse dépend du fournisseur ou de l'autorité qui contrôle le bloc. Les laboratoires peuvent utiliser `dig -x` ou les outils équivalents, mais l'absence de PTR n'empêche pas à elle seule toute communication IP.

Commandes de vérification :

```bash
# Linux / macOS si dig est installé
dig AAAA serveur.exemple.test
dig A serveur.exemple.test
dig -x 2001:db8:1200:20::10

# Outils génériques
nslookup -type=AAAA serveur.exemple.test
```

`exemple.test` est un nom réservé aux tests. Remplace-le par le nom d'un environnement que tu es autorisé à interroger.

### 5.2. Le piège du AAAA obsolète

Après une renumérotation, le DNS peut continuer à renvoyer un ancien AAAA qui n'est plus joignable, tandis que l'enregistrement A reste valide. Les symptômes dépendent de la sélection d'adresse et du comportement de l'application : délai initial, repli sur IPv4, connexion lente ou échec complet. Il faut interroger le DNS, tester l'adresse IPv6 directement et vérifier le TTL et les caches avant de modifier le routage.

Un test tel que `ping -6 hostname` peut être utile mais ne reproduit pas toujours la politique de l'application. Le navigateur ou la bibliothèque système peut faire une sélection de destination différente, tenter plusieurs adresses en parallèle ou utiliser IPv4 après un délai. Pour prouver la cause, compare les réponses DNS, les adresses essayées dans les logs/captures et les routes correspondantes.

### 5.3. Double pile : deux plans réseau à tester

En mode double pile, IPv4 et IPv6 peuvent coexister sur le même hôte mais utiliser des routes, DNS, ACL et mécanismes de découverte différents. Une application réussissant via IPv4 ne démontre pas que son chemin IPv6 est sain. De la même manière, une panne IPv6 ne signifie pas forcément que toute connectivité est indisponible.

Une fiche de test applicatif doit inclure : nom résolu, A/AAAA, adresse de destination réellement tentée, source choisie, route, prochain saut, filtrage, réponse du service et durée du test. Les règles de pare-feu doivent couvrir les flux IPv4 et IPv6 conformément à l'objectif ; activer la double pile sans mettre à jour l'exploitation crée souvent un « chemin oublié ».

### 5.4. Sélection de l'adresse source et destination

Les systèmes peuvent posséder plusieurs adresses par interface, et un nom DNS peut renvoyer plusieurs destinations. Les algorithmes de sélection tiennent compte de facteurs tels que la portée, le caractère préféré ou déprécié, la correspondance de préfixe et la politique locale. Le résultat peut aussi dépendre de l'application.

Si un serveur possède GUA et ULA, mais que seule l'une de ces familles de préfixes est routée depuis le client, un simple `curl` vers le nom DNS peut prendre un chemin inattendu. Pour isoler, utilise un test avec l'adresse de destination explicitement choisie puis compare au test par nom. Ne modifie pas immédiatement l'ordre de préférence IPv4/IPv6 global : commence par vérifier la configuration réelle et les résultats de résolution.


## 6. NDP à un niveau de diagnostic intermédiaire

### 6.1. Le cache des voisins ne remplace pas la table de routage

NDP résout notamment l'adresse de couche 2 d'un voisin IPv6 considéré comme directement joignable sur le lien. La table de routage décide si la destination est directement sur le lien ou si le paquet doit être envoyé à un routeur. Une entrée dans le cache des voisins ne signifie donc pas que toutes les destinations distantes sont joignables.

Une destination distante apparaît généralement via le voisin correspondant au prochain saut, pas via une entrée MAC pour chaque serveur Internet. Si une route indique `via fe80::1 dev eth0`, le système doit résoudre le voisin `fe80::1` sur l'interface concernée, puis envoyer les paquets à ce prochain saut.

### 6.2. États de voisin sous Linux

La commande `ip -6 neigh show` peut afficher des états tels que `INCOMPLETE`, `REACHABLE`, `STALE`, `DELAY`, `PROBE` ou `FAILED`. Ces états décrivent la manière dont la pile suit la joignabilité et la résolution du voisin. Ils ne sont pas un simple code « bon/mauvais » indépendant du contexte.

| État | Interprétation opérationnelle indicative | Action utile |
|---|---|---|
| `INCOMPLETE` | résolution commencée, mais adresse de couche 2 pas encore obtenue | capturer NS/NA et vérifier VLAN, multicast, voisin et filtrage |
| `REACHABLE` | la joignabilité est récemment confirmée | vérifier néanmoins les routes plus loin si le flux échoue |
| `STALE` | entrée connue mais non récemment confirmée | peut être normal ; observer le trafic avant de conclure |
| `DELAY` | période d'attente avant une sonde de confirmation | surveiller les échanges suivants |
| `PROBE` | le système tente de confirmer la joignabilité | capturer NS, vérifier si NA revient |
| `FAILED` | résolution/confirmation échouée selon la pile | vérifier le voisin, le lien et la capture sur le bon VLAN |

Les noms et le traitement exacts sont propres au système d'exploitation. Le point clé est de corréler la table des voisins avec la capture, l'état d'interface et la table de routage.

### 6.3. Lire une séquence Neighbor Solicitation / Neighbor Advertisement

Quand un hôte veut transmettre à un voisin directement joignable, il peut envoyer une Neighbor Solicitation (NS) vers une adresse multicast sollicitée afin d'obtenir une Neighbor Advertisement (NA). L'échange est local au lien ; il ne doit pas être traité comme un paquet qui traverse normalement le routeur vers l'Internet.

Si NS est visible mais aucune NA ne revient, plusieurs hypothèses existent : adresse cible absente, VLAN incorrect, liaison ou filtrage multicast, interface cible en panne, mauvaise observation SPAN, protection de couche 2 ou problème du système. Si une NA arrive, mais que la communication applicative échoue ensuite, il faut passer à l'analyse du routage, du filtrage et du service.

### 6.4. DAD et adresse dupliquée

La Duplicate Address Detection vérifie si une adresse candidate est déjà utilisée sur le lien. Une capture peut montrer des Neighbor Solicitation associées à une adresse cible encore non assignée. Un conflit ou une réponse inattendue peut faire échouer l'ajout de l'adresse.

Ne désactive pas DAD comme premier réflexe lorsque l'adresse ne fonctionne pas. Vérifie plutôt les annonces, la présence d'un doublon, les équipements virtuels clonés et la configuration statique qui peut réutiliser la même adresse. Dans un réseau cloné, une image de machine avec une configuration réseau identique peut introduire des conflits difficiles à repérer.

### 6.5. Pourquoi ICMPv6 ne peut pas être bloqué indistinctement

IPv6 s'appuie sur ICMPv6 pour NDP, les annonces de routeur et la signalisation des erreurs, dont Packet Too Big. Bloquer indistinctement ICMPv6 peut casser la découverte du voisin, la route par défaut ou PMTUD alors que les connexions de petite taille semblent encore fonctionner.

Une politique de sécurité doit distinguer les types de messages, le sens, le point d'application et les exigences de la topologie. Les règles spécifiques dépendent des standards, du système et des équipements. Avant de filtrer un type ICMPv6, identifie son rôle et réalise un test ciblé dans le laboratoire.


## 7. MTU, PMTUD et symptômes de connectivité partielle

### 7.1. Pourquoi IPv6 rend PMTUD incontournable

Les routeurs IPv6 ne fragmentent pas les paquets en transit comme le faisait IPv4 dans certains cas historiques. Si un paquet trop grand arrive sur un lien qui ne peut pas le transporter, le routeur supprime le paquet et devrait envoyer un message ICMPv6 **Packet Too Big** contenant l'information de MTU adaptée. La source ajuste ensuite la taille des paquets ou informe la couche supérieure.

Une panne typique apparaît quand les petits paquets passent mais que les gros transferts bloquent. Le TCP handshake peut réussir, car les paquets de contrôle sont petits, puis le transfert de données s'arrête lorsque des paquets plus grands ne passent plus. Si ICMPv6 Packet Too Big est filtré ou perdu, la source peut ne pas apprendre la contrainte et le symptôme persiste.

### 7.2. Exemple de diagnostic

Supposons que le LAN possède une MTU de 1500 octets, mais qu'un tunnel sur le chemin distant ne permette qu'une MTU plus faible. Les pings simples répondent ; un transfert de fichier se bloque. Il ne faut pas déclarer immédiatement « problème DNS » ou diminuer la MTU de toutes les interfaces. Mesure la taille du chemin, capture les messages ICMPv6 et identifie où le paquet est supprimé.

```text
PC-A -- R1 -- Tunnel / lien MTU réduit -- R2 -- Serveur
       paquet trop grand ----------X
       <--- ICMPv6 Packet Too Big (si transmis)

Si ICMPv6 est filtré, l'émetteur peut continuer à envoyer
une taille inutilisable : symptôme de black hole PMTUD.
```

### 7.3. Ordre de vérification

1. Vérifie la MTU locale et la taille des paquets réellement envoyés.
2. Reproduis le problème avec un test progressif et contrôlé.
3. Capture ICMPv6 à proximité de la source et, si possible, près du lien suspect.
4. Cherche Packet Too Big, la MTU indiquée et la corrélation avec les paquets perdus.
5. Vérifie ACL, pare-feu, tunnel, interfaces et équipements intermédiaires susceptibles de filtrer ou de modifier le traitement.
6. Corrige au point le plus ciblé ; ne désactive pas globalement le filtrage ICMPv6 pour masquer le symptôme.
7. Reteste un transfert applicatif réel ainsi que les autres destinations concernées.

### 7.4. Le ping n'est pas une preuve suffisante

Un ping réussi ne prouve pas la MTU de bout en bout ; il peut utiliser une taille faible et un trajet différent. Un ping échoué ne prouve pas à lui seul une panne IPv6, car l'écho peut être filtré. Il faut combiner tests de tailles, captures, routes et comportement applicatif.

La taille déclarée par un outil peut désigner le payload ICMP et non la taille totale du paquet IPv6. Pour comparer des valeurs, calcule les en-têtes et vérifie la façon dont la commande mesure la taille.


<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 350" role="img" aria-label="PMTUD IPv6 animé montrant un paquet trop grand, un message Packet Too Big et un nouveau paquet plus petit" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><style>.b{fill:#111827;stroke:#64748b;stroke-width:1.5}.t{fill:#f8fafc;font-size:15px}.s{fill:#cbd5e1;font-size:12px}.ln{stroke:#64748b;stroke-width:2;fill:none}.blue{fill:#38bdf8;stroke:#082f49;stroke-width:1.5}.amber{fill:#fbbf24;stroke:#451a03;stroke-width:1.5}.red{fill:#fb7185;stroke:#4c0519;stroke-width:1.5}</style></defs>
  <rect class="b" x="25" y="90" width="170" height="110" rx="12"/><text class="t" x="110" y="120" text-anchor="middle">Source</text><text class="s" x="110" y="143" text-anchor="middle">MTU estimée 1500</text><text class="s" x="110" y="161" text-anchor="middle">émission initiale</text>
  <rect class="b" x="365" y="90" width="170" height="110" rx="12"/><text class="t" x="450" y="120" text-anchor="middle">Lien contraint</text><text class="s" x="450" y="143" text-anchor="middle">MTU d'exemple 1400</text><text class="s" x="450" y="161" text-anchor="middle">paquet trop grand</text>
  <rect class="b" x="705" y="90" width="170" height="110" rx="12"/><text class="t" x="790" y="120" text-anchor="middle">Destination</text><text class="s" x="790" y="143" text-anchor="middle">non atteint d'abord</text><text class="s" x="790" y="161" text-anchor="middle">puis paquet réduit</text>
  <path class="ln" d="M195 135 H365 M535 135 H705"/>
  <path d="M205 117 H355" stroke="#38bdf8" stroke-width="3" stroke-dasharray="7 5" fill="none"/><g transform="translate(205 117)"><circle class="blue" r="7" cx="0" cy="0"><animateMotion dur="2.2s" repeatCount="indefinite" path="M0 0 H150"/></circle></g><text class="s" x="280" y="105" text-anchor="middle">Paquet large</text>
  <path d="M355 180 H205" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 5" fill="none"/><g transform="translate(355 180)"><circle class="amber" r="7" cx="0" cy="0"><animateMotion dur="2.2s" begin=".8s" repeatCount="indefinite" path="M0 0 H-150"/></circle></g><text class="s" x="280" y="198" text-anchor="middle">Packet Too Big</text>
  <path d="M205 230 H685" stroke="#34d399" stroke-width="3" stroke-dasharray="5 5" fill="none"/><g transform="translate(205 230)"><circle class="blue" r="5" cx="0" cy="0"><animateMotion dur="3.6s" begin="1.5s" repeatCount="indefinite" path="M0 0 H480"/></circle></g><text class="s" x="450" y="221" text-anchor="middle">Source adapte la taille et réessaie</text>
  <rect class="b" x="205" y="262" width="480" height="45" rx="10"/><text class="t" x="445" y="290" text-anchor="middle">Si ICMPv6 est bloqué, la correction peut ne jamais arriver</text>
  <text class="s" x="450" y="333" text-anchor="middle">Valeurs illustratives ; mesure la MTU réelle du chemin concerné.</text>
</svg>
</div>


## 8. Sécurité IPv6 sur un LAN d'entreprise

### 8.1. Ne pas supposer que « personne n'utilise IPv6 »

Un poste peut activer IPv6 même si le réseau a été conçu à l'origine pour IPv4. Un RA non autorisé peut installer une route par défaut ; NDP peut être abusé pour perturber la résolution des voisins ; un service IPv6 peut rester ouvert alors que l'ACL IPv4 a été durcie. La sécurité doit inclure la pile réellement active, pas uniquement la version IP qui apparaît dans l'inventaire historique.

La première étape consiste à inventorier les points d'émission de RA légitimes, les préfixes utilisés, les serveurs DHCPv6, les routes et les politiques de pare-feu. Il faut ensuite vérifier quels mécanismes de garde sont supportés par les commutateurs et quelles conséquences ils ont pour les trunks, le Wi-Fi, les tunnels et les équipements multi-rôles.

### 8.2. RA Guard

RA Guard peut permettre à un commutateur compatible de bloquer les Router Advertisements reçus depuis des ports qui ne devraient pas agir comme routeurs. La politique doit définir les ports de confiance et les ports clients. Il faut vérifier les limites du matériel, les versions logicielles et les environnements tunnelisés : une fonction appelée RA Guard n'offre pas nécessairement la même protection dans toutes les topologies.

Procédure de conception :

1. recenser les interfaces réellement connectées à des routeurs légitimes ;
2. décider où les RA sont autorisés et où ils doivent être bloqués ;
3. lire la documentation de la fonction pour le modèle/logiciel ;
4. activer d'abord en laboratoire et tester la réception des RA légitimes ;
5. confirmer que les postes apprennent le préfixe et la route attendus ;
6. tester qu'un RA venant d'un port utilisateur est bloqué ;
7. surveiller les compteurs et prévoir un retour arrière.

Exemple illustratif Cisco IOS XE, **à vérifier pour la plate-forme exacte** :

```cisco
! Exemple de structure de configuration, pas une recette universelle.
ipv6 nd raguard policy CLIENTS
 device-role host
!
interface GigabitEthernet1/0/10
 ipv6 nd raguard attach-policy CLIENTS
```

Les politiques et commandes exactes dépendent de l'implémentation. Cette illustration n'est pas à copier aveuglément en production ; une mauvaise classification d'un port de routeur peut supprimer des RA légitimes.

### 8.3. DHCPv6 Guard, inspection NDP et contrôles de source

Des équipements prennent en charge des mécanismes comme DHCPv6 Guard, l'inspection NDP et d'autres contrôles de couche 2. Leur but est de limiter les messages de contrôle ou les correspondances adresse/port qui ne respectent pas la politique du réseau. Leur efficacité dépend des capacités, du placement et de la topologie ; ce ne sont pas des protections magiques applicables sans inventaire.

Dans une architecture d'accès, définis les ports vers les serveurs/relays et les ports terminaux. Vérifie la prise en charge des trunks, du Wi-Fi, des tunnels, des EtherChannels et des scénarios d'hôtes virtualisés. Une règle trop stricte peut bloquer le comportement normal d'un hyperviseur, d'un routeur virtuel ou d'un point d'accès.

### 8.4. ACL IPv6 et ICMPv6

Les ACL IPv6 doivent autoriser le trafic utile, limiter les services exposés et conserver les messages de contrôle requis par la conception. Un filtre global qui bloque tous les types ICMPv6 peut casser NDP, PMTUD ou la découverte de routeurs. À l'autre extrême, laisser tous les flux ouverts parce que « IPv6 est nouveau » n'est pas une politique de sécurité.

Décompose les règles par fonction : administration, DNS, services applicatifs, routage, NDP/RA et messages d'erreur. Précise le sens et l'interface où la règle est appliquée. Après modification, vérifie les connexions locales, distantes, les flux de grande taille et les messages nécessaires au dépannage.

### 8.5. Pare-feu : filtrer le trafic entrant sans casser les retours

Les connexions IPv6 ne nécessitent généralement pas de NAT pour être filtrées. Un pare-feu stateful peut autoriser les connexions sortantes et leurs retours tout en limitant les connexions entrantes nouvelles. La politique exacte dépend des services à publier et de la frontière réseau.

Ne confonds pas « adresse globalement routable » avec « port ouvert ». Le routage rend le préfixe atteignable sur le plan IP ; le pare-feu, le service d'écoute et la politique de sécurité déterminent si une communication est autorisée et traitée.

### 8.6. Adresses temporaires et confidentialité

Certains systèmes génèrent des adresses temporaires pour limiter la corrélation triviale des activités basée sur un identifiant d'interface stable. Cela peut compliquer les journaux et l'inventaire si l'équipe suppose qu'un poste ne possède qu'une seule GUA. Il faut distinguer les adresses stables utiles à l'exploitation des adresses temporaires sélectionnées pour des connexions sortantes.

Ne désactive pas les mécanismes de confidentialité en réaction à un problème de journaux sans comprendre le but et les conséquences. Pour les services serveur, l'adresse stable, le DNS et l'inventaire doivent être définis explicitement. Pour les postes clients, la présence de plusieurs adresses peut être normale.


## 9. Méthode de dépannage : traiter les couches dans le bon ordre

### 9.1. Séparer les domaines de panne

Quand un poste IPv6 ne communique pas, ne commence pas par modifier toutes les routes ou désactiver le pare-feu. Suis cet ordre :

1. **Interface :** lien opérationnel, bon VLAN, interface IPv6 active.
2. **Adresse :** adresse attendue, préfixe, durée de vie, état préféré/déprécié, DAD.
3. **Route locale :** route on-link et route par défaut, prochain saut attendu.
4. **NDP :** résolution du voisin ou du routeur, cache des voisins, NS/NA.
5. **Routage :** route aller, route retour, prochain saut et éventuels filtres.
6. **ICMPv6 / MTU :** Packet Too Big et autres messages nécessaires.
7. **DNS :** A/AAAA, réponses obsolètes, source/destination réellement essayées.
8. **Transport/application :** port d'écoute, pare-feu stateful, certificat et configuration du service.

Cet ordre n'est pas un dogme : une capture peut révéler très vite un problème spécifique. Mais il évite de passer directement à une couche haute avant d'avoir établi les faits de base.

### 9.2. Commandes utiles par système

**Windows :**

```powershell
ipconfig /all
route print -6
netsh interface ipv6 show interfaces
netsh interface ipv6 show route
netsh interface ipv6 show neighbors
ping -6 2001:db8:1200:10::1
tracert -6 2001:db8:1200:20::10
Resolve-DnsName serveur.exemple.test -Type AAAA
```

**Linux :**

```bash
ip -6 address show
ip -6 route show
ip -6 neigh show
ip -6 route get 2001:db8:1200:20::10
ping -6 -c 4 2001:db8:1200:10::1
tracepath -6 2001:db8:1200:20::10
dig AAAA serveur.exemple.test
```

**Cisco IOS/IOS XE (selon plateforme) :**

```cisco
show ipv6 interface brief
show ipv6 interface GigabitEthernet0/0
show ipv6 route
show ipv6 neighbors
show running-config | section ipv6
show access-lists
show logging
```

Les commandes de capture, de debug et de routage dynamique changent selon IOS/IOS XE et le simulateur. En production, `debug` peut produire beaucoup d'événements ou affecter les performances ; utilise-le selon une procédure approuvée, sur une durée et un périmètre maîtrisés.

### 9.3. Captures Wireshark

Filtres utiles à adapter selon la version de Wireshark :

- `icmpv6` : tous les messages ICMPv6 décodés ;
- `icmpv6.type == 133` : Router Solicitation ;
- `icmpv6.type == 134` : Router Advertisement ;
- `icmpv6.type == 135` : Neighbor Solicitation ;
- `icmpv6.type == 136` : Neighbor Advertisement ;
- `icmpv6.type == 2` : Packet Too Big ;
- `dhcpv6` : messages DHCPv6 décodés ;
- `dns && ipv6` : échanges DNS transportés sur IPv6 lorsque le filtre est supporté.

Un filtre qui ne produit aucun résultat ne prouve pas que le message n'existe pas. Tu peux capturer sur la mauvaise interface, manquer le VLAN, observer une période où aucun échange n'a été déclenché ou utiliser un champ qui diffère selon la version du dissector. Déclenche explicitement l'action (renouvellement, ping du voisin, résolution DNS) et capture sur le bon segment.

### 9.4. Construire une hypothèse vérifiable

Un compte rendu utile ne dit pas simplement « IPv6 ne marche pas ». Il précise le contexte et les observations :

- **Symptôme :** par exemple, un transfert HTTPS se bloque après le handshake ;
- **Périmètre :** un poste, un VLAN, un site ou une destination ;
- **Observations :** adresse source, destination, route, voisins, réponses DNS ;
- **Hypothèse :** par exemple, ICMPv6 Packet Too Big n'atteint pas la source ;
- **Test discriminant :** capture sur le point de sortie et comparaison avec le point d'entrée du tunnel ;
- **Résultat :** message absent ou filtré, paquet abandonné, route erronée, etc. ;
- **Correction :** modification ciblée et approuvée ;
- **Validation :** test d'origine, test de non-régression, preuve archivée.

Cette méthode empêche de confondre une corrélation temporelle avec une cause. Si la connectivité revient après redémarrage d'un routeur, cela ne démontre pas à lui seul que le routeur était la cause racine ; un cache, une annonce de route ou une session expirée a peut-être été réinitialisé en même temps.


<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 400" role="img" aria-label="Arbre de décision animé pour dépanner une panne IPv6 en partant de l'interface jusqu'au service" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><style>.b{fill:#111827;stroke:#64748b;stroke-width:1.5}.t{fill:#f8fafc;font-size:14px}.s{fill:#cbd5e1;font-size:11px}.l{stroke:#60a5fa;stroke-width:2.5;fill:none}.p{fill:#34d399;stroke:#052e24;stroke-width:1.3}</style></defs>
  <rect class="b" x="320" y="12" width="260" height="48" rx="10"/><text class="t" x="450" y="41" text-anchor="middle">Symptôme IPv6 reproduit</text>
  <path class="l" d="M450 60 V82 H150 V105 M450 82 V105 M450 82 H750 V105"/>
  <g transform="translate(450 60)"><circle class="p" cx="0" cy="0"><animateMotion dur="4s" repeatCount="indefinite" path="M0 0 V22 H-300 V45"/></circle></g>
  <rect class="b" x="45" y="105" width="210" height="52" rx="9"/><text class="t" x="150" y="127" text-anchor="middle">Adresse et préfixe ?</text><text class="s" x="150" y="144" text-anchor="middle">validité / DAD / RA</text>
  <rect class="b" x="345" y="105" width="210" height="52" rx="9"/><text class="t" x="450" y="127" text-anchor="middle">Route et voisin ?</text><text class="s" x="450" y="144" text-anchor="middle">table + NS/NA</text>
  <rect class="b" x="645" y="105" width="210" height="52" rx="9"/><text class="t" x="750" y="127" text-anchor="middle">DNS / application ?</text><text class="s" x="750" y="144" text-anchor="middle">A/AAAA + ports</text>
  <path class="l" d="M150 157 V190 M450 157 V190 M750 157 V190"/>
  <rect class="b" x="45" y="190" width="210" height="55" rx="9"/><text class="t" x="150" y="213" text-anchor="middle">Capture RA / DAD</text><text class="s" x="150" y="231" text-anchor="middle">corriger l'adressage</text>
  <rect class="b" x="345" y="190" width="210" height="55" rx="9"/><text class="t" x="450" y="213" text-anchor="middle">Route aller + retour</text><text class="s" x="450" y="231" text-anchor="middle">NDP / ICMPv6 / MTU</text>
  <rect class="b" x="645" y="190" width="210" height="55" rx="9"/><text class="t" x="750" y="213" text-anchor="middle">Réponse du service</text><text class="s" x="750" y="231" text-anchor="middle">DNS / pare-feu / écoute</text>
  <path class="l" d="M150 245 V277 H450 V297 M450 245 V297 M750 245 V277 H450"/>
  <g transform="translate(150 245)"><circle class="p" cx="0" cy="0"><animateMotion dur="4.5s" begin=".8s" repeatCount="indefinite" path="M0 0 V32 H300 V52"/></circle></g>
  <rect class="b" x="300" y="297" width="300" height="58" rx="10"/><text class="t" x="450" y="321" text-anchor="middle">Correction minimale et preuve</text><text class="s" x="450" y="340" text-anchor="middle">ret tester + non-régression + journal</text>
  <text class="s" x="450" y="384" text-anchor="middle">Le diagramme organise le diagnostic ; il ne remplace pas les preuves réelles.</text>
</svg>
</div>


## 10. Laboratoire 1 — Construire un plan d'adressage hiérarchique

**Objectif :** découper un bloc de documentation en sites et VLAN sans chevauchement.

### Topologie / contexte

Une entreprise possède un siège et un site distant. Le bloc du laboratoire est `2001:db8:1200::/48`. Le siège doit disposer de VLAN utilisateurs, serveurs, voix et gestion. Le site distant a un VLAN utilisateurs et un VLAN serveurs. Un lien de transit connecte R1 et R2.

### Travail à réaliser

1. Attribue un `/64` distinct à chaque VLAN.
2. Prévois des blocs par site que l'équipe pourrait agréger dans les routes à l'avenir.
3. Choisis une convention d'adresse pour les passerelles.
4. Identifie au moins deux préfixes gardés en réserve et explique pourquoi ils ne sont pas affectés immédiatement.
5. Construis une table comportant préfixe, usage, site, VLAN, passerelle, méthode d'attribution et propriétaire.

### Critères de réussite

- aucun `/64` n'est attribué à deux liens indépendants ;
- les préfixes de sites ne se chevauchent pas ;
- les routes peuvent être résumées sans inclure un préfixe appartenant à un autre site ;
- la documentation indique les usages futurs et les responsabilités.

**Défi :** explique comment ton plan serait modifié si le site distant passait d'un `/56` à un `/48` délégué. Il ne suffit pas d'agrandir le texte dans la feuille : il faut contrôler le découpage existant, les agrégats et les effets du changement sur les routes.


## 11. Laboratoire 2 — Interpréter les indicateurs RA et DHCPv6

**Objectif :** expliquer exactement comment un client apprend son adresse, son DNS et sa route par défaut.

### Scénario

Un routeur annonce le préfixe `2001:db8:1200:10::/64` avec SLAAC activé. Le RA positionne M à 0 et O à 1. Un serveur DHCPv6 est disponible sur le même VLAN et fournit les DNS. Un client obtient une GUA, mais l'utilisateur rapporte qu'un nom de serveur ne se résout pas.

### Étapes

1. Capture un RA ; note le préfixe, les indicateurs A/L, M/O, les durées de vie et la route par défaut.
2. Lance une résolution DNS explicite et capture DHCPv6.
3. Vérifie si une requête DHCPv6 Information-request est émise et si un Reply revient.
4. Compare les serveurs DNS configurés localement avec les options reçues.
5. Interroge le serveur DNS directement lorsque possible, puis compare A et AAAA.
6. Rédige deux hypothèses alternatives si aucune requête DHCPv6 n'apparaît.

### Questions de compte rendu

- Pourquoi M = 0 n'interdit-il pas nécessairement tout usage de DHCPv6 ?
- Pourquoi le client peut-il avoir une GUA et une route par défaut tout en échouant sur la résolution DNS ?
- Quelles preuves permettraient de distinguer « serveur DHCPv6 indisponible » de « client n'ayant pas demandé l'information » ?

**Résultat attendu :** un tableau RA / DHCPv6 / état du client et un diagnostic fondé sur les paquets observés, et non sur l'indicateur M/O seul.


## 12. Laboratoire 3 — Configurer deux routeurs et une route de retour

**Objectif :** isoler la différence entre une route aller correcte et une communication bidirectionnelle.

### Plan d'adressage de test

| Segment | Préfixe | Adresse d'interface / hôte |
|---|---|---|
| LAN A | `2001:db8:1200:10::/64` | R1 `::1`, PC-A `::10` |
| Transit R1-R2 | `2001:db8:1200:ff01::/64` | R1 `::1`, R2 `::2` |
| LAN B | `2001:db8:1200:20::/64` | R2 `::1`, PC-B `::20` |

Les adresses `2001:db8::/32` restent des exemples de documentation. Adapte les noms d'interfaces aux équipements et au simulateur.

### Configuration indicative de R1

```cisco
ipv6 unicast-routing
interface GigabitEthernet0/0
 ipv6 address 2001:DB8:1200:10::1/64
 no shutdown
interface GigabitEthernet0/1
 ipv6 address 2001:DB8:1200:FF01::1/64
 no shutdown
ipv6 route 2001:DB8:1200:20::/64 2001:DB8:1200:FF01::2
```

### Configuration indicative de R2

```cisco
ipv6 unicast-routing
interface GigabitEthernet0/0
 ipv6 address 2001:DB8:1200:20::1/64
 no shutdown
interface GigabitEthernet0/1
 ipv6 address 2001:DB8:1200:FF01::2/64
 no shutdown
ipv6 route 2001:DB8:1200:10::/64 2001:DB8:1200:FF01::1
```

### Vérification

1. Vérifie les interfaces et les routes connectées.
2. Depuis R1, ping l'adresse de transit de R2.
3. Depuis PC-A, ping la passerelle locale, puis PC-B.
4. Retire **uniquement dans le lab** la route retour et observe les symptômes.
5. Restaure la route, reteste et compare les traces.

**Conclusion attendue :** un routeur peut transmettre le paquet vers le réseau de destination, mais le retour échoue si le réseau distant ne dispose pas de route vers le préfixe source. Les ACL et le filtrage ICMPv6 peuvent modifier l'observation : note toujours l'endroit où chaque test est lancé.


## 13. Laboratoire 4 — Lire NDP et les états de voisin

**Objectif :** distinguer une panne de résolution locale d'une panne de routage distant.

### Étapes

1. Sur Linux, relève `ip -6 address show`, `ip -6 route show` et `ip -6 neigh show` avant le test.
2. Capture `icmpv6` dans Wireshark.
3. Ping la passerelle link-local ou GUA appropriée.
4. Observe NS/NA et l'évolution de l'état de voisin.
5. Dans une maquette isolée, déconnecte le lien ou adresse une cible de test non existante ; observe la différence entre délai et échec de résolution.
6. Rétablis la topologie et compare les résultats.

### Analyse attendue

- Si le voisin du prochain saut ne peut pas être résolu, la panne peut se situer sur le lien local, dans le VLAN ou dans NDP.
- Si le voisin est connu et répond mais que la destination distante échoue, examine la table de routage et le retour.
- Une entrée `STALE` peut être normale ; ne la supprime pas pour obtenir un état « plus propre » sans avoir une hypothèse testable.
- DAD doit être distingué d'une résolution de voisin normale : la cible d'un NS de DAD correspond à une adresse candidate.

**Livrable :** capture annotée avec le paquet déterminant, sortie de cache avant/après et conclusion expliquant l'hypothèse écartée.


## 14. Laboratoire 5 — Diagnostiquer un problème DNS AAAA

**Objectif :** séparer résolution, sélection d'adresse et connectivité.

### Scénario

`app.exemple.test` renvoie un A fonctionnel et un AAAA qui pointe encore vers une ancienne adresse du laboratoire. Les utilisateurs signalent une connexion lente ou un délai avant l'ouverture de l'application.

### Étapes

1. Compare A et AAAA avec `dig` ou `Resolve-DnsName`.
2. Vérifie le TTL des enregistrements et le cache local si les outils le permettent.
3. Teste l'IPv6 explicitement et teste séparément l'IPv4.
4. Dans une capture, observe quelle adresse est effectivement tentée par le client.
5. Vérifie routes, passerelles, pare-feu et service d'écoute de l'ancienne adresse.
6. Corrige le DNS ou le service dans le périmètre de test, puis répète la résolution et le test applicatif.

### Critères de réussite

- tu peux démontrer que le problème vient du AAAA obsolète ou écarter cette hypothèse ;
- tu sais distinguer l'échec de la résolution du succès DNS suivi d'une panne IP ;
- tu documentes les caches et TTL, au lieu de déclarer le changement instantané sans preuve.


## 15. Laboratoire 6 — Panne de type PMTUD black hole

**Objectif :** comprendre pourquoi un flux IPv6 peut commencer puis se bloquer sur les paquets volumineux.

### Préparation

Utilise deux hôtes IPv6 et un routeur ou tunnel de laboratoire sur lequel une MTU contrainte peut être contrôlée. Ne modifie pas la MTU d'une interface de production pour reproduire l'exercice.

### Étapes

1. Vérifie l'adresse, la route et la connectivité de base.
2. Lance un transfert ou une session applicative qui utilise des paquets plus volumineux.
3. Capture ICMPv6 sur les deux côtés du lien suspect.
4. Recherche un Packet Too Big correspondant aux paquets envoyés et note la MTU indiquée.
5. Dans un scénario contrôlé, compare le comportement lorsque le message est transmis et lorsque la règle de filtrage de laboratoire le bloque.
6. Restaure le filtrage attendu et vérifie de nouveau un flux volumineux.

**Sécurité :** l'objectif est d'observer les conséquences d'un filtrage incorrect en laboratoire. Ne laisse pas en production une règle qui bloque indistinctement ICMPv6 pour « tester si cela aide ».

**Livrable :** chronologie des paquets, hypothèse, test discriminant, correction proposée et résultat après retour à la configuration normale.


## 16. Laboratoire 7 — Protection contre un RA non autorisé

**Objectif :** concevoir et tester la frontière de confiance RA.

### Préparation

Sur un commutateur compatible, identifie un port de routeur légitime et un port client. Dans une maquette, utilise un routeur de test sur le port client pour émettre un RA non autorisé, uniquement si tu as le contrôle de l'environnement et l'autorisation de le faire.

### Étapes

1. Capture le RA légitime et note le préfixe et la durée de vie du routeur.
2. Capture le RA de test avant toute protection ; vérifie si le client le voit et si la route par défaut change.
3. Consulte la documentation de la fonction RA Guard de la plate-forme et prépare une politique adaptée.
4. Attache la politique uniquement aux ports validés, en déclarant les ports de routeurs légitimes selon la syntaxe requise.
5. Répète la capture et confirme que le RA client est bloqué tandis que le RA légitime continue à fonctionner.
6. Vérifie les journaux/compteurs puis réalise un retour arrière contrôlé.

**Attention :** certaines versions ont des limites selon le matériel, les trunks, le tunnel ou le type d'interface. Le résultat ne doit pas être extrapolé à toutes les plates-formes.


## 17. Laboratoire 8 — Mini-audit double pile

**Objectif :** vérifier qu'une application n'est pas protégée seulement pour IPv4.

Établis un inventaire des services du lab et note pour chaque service : enregistrements A/AAAA, interfaces d'écoute, routes, règles IPv4, règles IPv6, DNS, certificats, supervision et procédure de repli. Identifie au moins un service qui répond en IPv4 mais pas en IPv6, puis établis s'il s'agit d'un choix volontaire ou d'une erreur.

Prépare un tableau de validation :

| Test | IPv4 | IPv6 | Preuve |
|---|---|---|---|
| résolution DNS | résultat A | résultat AAAA | sortie DNS horodatée |
| route | route IPv4 | route IPv6 | table de routage |
| ping/sonde | résultat | résultat | capture et sortie outil |
| connexion au port | succès/échec | succès/échec | test applicatif / logs |
| filtrage | règle appliquée | règle appliquée | export ou compteur ACL |

Ne cherche pas à rendre IPv4 et IPv6 strictement identiques si la politique d'entreprise exige des différences. L'objectif est que les différences soient intentionnelles, connues et testées.


## 18. Procédure de changement et retour arrière

Une modification IPv6 peut toucher les postes, les routes, le DNS, les règles de sécurité et les applications. Applique la discipline de changement même lorsque la commande paraît courte.

### Avant le changement

- confirmer l'autorisation, le périmètre et la fenêtre ;
- sauvegarder la configuration des routeurs, commutateurs et services concernés ;
- relever les adresses, RA, routes, voisins, DNS, compteurs et tests applicatifs ;
- identifier les préfixes et services dépendants ;
- définir les critères de réussite et d'échec ;
- préparer une procédure de retour arrière testable.

### Pendant le changement

- appliquer une seule famille de modifications à la fois ;
- lire le résultat des commandes et vérifier les messages d'erreur ;
- confirmer les routes et les RA sur le bon lien ;
- éviter les changements non liés qui compliqueraient l'attribution de la cause ;
- consigner les heures et les commandes importantes sans exposer de secrets.

### Après le changement

- vérifier l'état des interfaces et la table IPv6 ;
- confirmer les adresses et routes sur des postes représentatifs ;
- vérifier NDP et DNS ;
- tester une application réelle et un transfert de taille importante ;
- confirmer que les politiques de filtrage couvrent les flux attendus ;
- conserver les preuves et mettre à jour le plan d'adressage.

### Déclencheurs de retour arrière

Le retour arrière doit être envisagé si les critères de réussite ne sont pas satisfaits, si des préfixes inattendus apparaissent, si un RA légitime est bloqué, si la route par défaut se détourne vers un équipement non approuvé, si un service critique devient inaccessible ou si les preuves sont insuffisantes pour poursuivre en sécurité.


## 19. Erreurs intermédiaires fréquentes et comment les éviter

### Erreur 1 — « Le client a une GUA, donc IPv6 marche »

Une GUA indique qu'une adresse a été configurée, pas que le routeur, le DNS, le chemin distant et le service sont corrects. Vérifie l'adresse, les routes, NDP, les réponses DNS et le test applicatif séparément.

### Erreur 2 — Confondre DHCPv6 et route par défaut

DHCPv6 peut attribuer des adresses ou d'autres paramètres, mais la découverte de la route par défaut reste liée aux RA dans le modèle usuel. Si la GUA est valide et qu'aucune route par défaut n'existe, capture les RA et inspecte leur durée de vie et leur réception.

### Erreur 3 — Modifier le M/O sans test client

Les drapeaux M et O orientent le comportement, mais les clients, les serveurs, les options DHCPv6 et les politiques locales doivent être cohérents. Confirme le comportement réel du système d'exploitation.

### Erreur 4 — Utiliser un seul `/64` pour plusieurs VLAN indépendants

La grandeur de l'espace IPv6 peut donner envie de réutiliser un préfixe, mais cela complique le routage et l'identification du lien. Alloue en général un `/64` distinct à chaque LAN qui utilise SLAAC et documente les exceptions.

### Erreur 5 — Oublier la route retour

Une route aller fonctionnelle peut acheminer les requêtes tandis que les réponses ne reviennent pas. Contrôle la table du réseau distant et la source exacte du test.

### Erreur 6 — Bloquer tout ICMPv6

Cela peut interrompre NDP, la découverte de routeur et PMTUD. Construis une politique fondée sur les types de messages et la fonction du lien, puis teste le comportement.

### Erreur 7 — Diagnostiquer DNS avec un ping seulement

Le ping peut échouer alors que DNS et TCP fonctionnent, ou réussir alors que le port applicatif est fermé. Utilise un test approprié à chaque couche.

### Erreur 8 — Confondre état de voisin et table de routage

Une entrée de voisin représente un correspondant de lien local. Les routes déterminent le prochain saut pour une destination distante. Compare les deux états avant de modifier les interfaces.

### Erreur 9 — Oublier le plan de sécurité IPv6

Des règles IPv4 ne garantissent pas que les services IPv6 sont filtrés de manière équivalente. Vérifie les deux piles, les règles entrantes, les services d'écoute et les logs.

### Erreur 10 — Appliquer un exemple Cisco sans vérifier le mode logiciel

Les commandes IPv6 et OSPFv3 diffèrent entre versions et familles de produits. Utilise l'aide de la plateforme, le guide de configuration correspondant et un laboratoire.


## 20. Exercices d'évaluation — 15 questions corrigées

### Question 1 — Calcul de sous-réseaux

Un bloc `/48` doit être découpé en `/64`. Combien de sous-réseaux `/64` peut-il théoriquement contenir ?

**Correction :** 16 bits sont disponibles entre `/48` et `/64`. Cela donne `2^16 = 65 536` sous-réseaux `/64`. C'est une capacité mathématique ; le plan d'adressage doit encore réserver et documenter les blocs.

### Question 2 — Adresse et préfixe

Deux hôtes sont dans `2001:db8:1200:10::/64`. Le fait qu'ils partagent ce préfixe garantit-il qu'ils communiquent ?

**Correction :** non. Le préfixe suggère qu'ils appartiennent au même segment logique si la configuration le reflète, mais le VLAN, les ports, les règles de filtrage, NDP, l'état des interfaces et les politiques locales peuvent empêcher la communication.

### Question 3 — GUA mais pas de route par défaut

Un client possède une GUA valide issue de SLAAC, mais sa table ne contient pas de route par défaut. Quelle vérification est prioritaire ?

**Correction :** capturer les RA et vérifier si un routeur légitime annonce une durée de vie de routeur non nulle, si le message arrive au client et si une autre politique ou une configuration locale influence la route.

### Question 4 — M = 0, O = 1

Que peux-tu conclure de ce RA ?

**Correction :** il indique que la configuration d'adresse gérée par DHCPv6 n'est pas demandée par le drapeau M dans cette annonce, tandis que des paramètres supplémentaires peuvent être disponibles via DHCPv6 grâce à O. Cela n'interdit pas toutes les autres formes de configuration ni ne garantit que DNS a été reçu.

### Question 5 — GUA et DNS en panne

Le poste possède une GUA et peut ping la passerelle, mais un nom interne ne se résout pas. Quelles couches vérifier ?

**Correction :** interrogations DNS A/AAAA, serveurs DNS reçus/localement configurés, chemin vers le serveur DNS, filtrage UDP/TCP 53 et réponse du service. La connectivité à la passerelle ne prouve pas l'accès au DNS.

### Question 6 — Solicit sans réponse

Une capture montre des Solicit DHCPv6, mais aucun Advertise/Reply. Cite des hypothèses.

**Correction :** serveur indisponible, relais absent/mal configuré, messages filtrés, mauvais VLAN, serveur sans pool adéquat ou capture incomplète. Il faut vérifier la réception côté serveur/relay avant de choisir la cause.

### Question 7 — Pourquoi DHCPv6 Relay ?

À quoi sert un relais DHCPv6 ?

**Correction :** il permet de faire transiter les échanges entre un client et un serveur qui n'est pas sur le même lien, sous réserve d'une configuration et d'un chemin de retour corrects. Il n'attribue pas à lui seul la route par défaut.

### Question 8 — Prefix Delegation

Un routeur reçoit un préfixe `/56`. Combien de préfixes `/64` peut-il découper mathématiquement dans ce bloc ?

**Correction :** 8 bits séparent `/56` de `/64`, donc `2^8 = 256` préfixes `/64`. La taille réellement exploitable dépend du bloc alloué, des réserves et de la politique de configuration.

### Question 9 — Route aller présente

PC-A atteint R2, mais ne reçoit pas de réponse de PC-B. Quelle vérification doit suivre ?

**Correction :** vérifier la route retour depuis R2/LAN B vers le préfixe source de PC-A, puis les ACL, la connectivité du LAN B et l'état de PC-B. Le succès jusqu'à R2 ne prouve pas le chemin complet.

### Question 10 — Voisin `INCOMPLETE`

Sous Linux, un voisin reste `INCOMPLETE`. Quelle capture est utile ?

**Correction :** rechercher les NS vers l'adresse cible et la présence ou l'absence d'une NA. Vérifier le bon VLAN/lien, le voisin cible, le multicast et les filtres de couche 2.

### Question 11 — TCP se connecte, le gros transfert bloque

Quelle hypothèse IPv6 est prioritaire à tester ?

**Correction :** un problème MTU/PMTUD est plausible. Cherche les messages ICMPv6 Packet Too Big et les différences de taille, mais vérifie également les tunnels, les pertes et les règles de filtrage. Le symptôme seul n'est pas une preuve.

### Question 12 — Un RA inconnu apparaît

Quels sont les premiers gestes ?

**Correction :** identifier l'interface/port source, capturer le RA et relever le préfixe et la durée de vie du routeur ; comparer à la conception et aux routeurs autorisés ; appliquer une protection de bordure après validation de la plate-forme et du port de confiance.

### Question 13 — Une adresse temporaire apparaît

Est-ce nécessairement un doublon ou une erreur ?

**Correction :** non. Certains systèmes utilisent des adresses temporaires pour limiter la corrélation des activités. Il faut analyser leur statut et la politique de confidentialité avant de les considérer comme anormales.

### Question 14 — AAAA ancien, A correct

Quel est le risque ?

**Correction :** le client peut tenter l'adresse IPv6 ancienne, subir une attente ou échouer avant le repli IPv4. Vérifie le TTL, les caches, l'adresse testée et la route ; corrige la source DNS ou le service de manière contrôlée.

### Question 15 — Pourquoi ne pas bloquer ICMPv6 globalement ?

**Correction :** NDP et les RA utilisent ICMPv6 et PMTUD IPv6 dépend de Packet Too Big pour signaler une contrainte de taille. Un blocage indiscriminé peut casser la découverte des voisins, les routes et les grands transferts. Les règles doivent être conçues au cas par cas selon le rôle du message.


## 21. Scénario final — Diagnostic complet d'un VLAN IPv6

### Situation

Un poste de VLAN utilisateurs obtient une GUA et peut communiquer avec la passerelle locale. Il résout le nom d'un serveur interne en une adresse AAAA, mais la connexion HTTPS échoue parfois. Les postes du VLAN serveurs fonctionnent correctement en IPv6. Le même nom est accessible en IPv4 depuis le poste incriminé.

### Travail demandé

Produis un plan de diagnostic qui teste au minimum les hypothèses suivantes :

1. AAAA obsolète ou destination IPv6 injoignable ;
2. mauvais routeur par défaut appris d'un RA ;
3. route de retour ou ACL incohérente pour le préfixe utilisateurs ;
4. problème NDP vers la passerelle ou prochain saut ;
5. problème PMTUD sur un chemin qui transporte des paquets volumineux ;
6. différence de politique entre IPv4 et IPv6 sur le pare-feu ou le service.

### Format du compte rendu

| Élément | À renseigner |
|---|---|
| Symptôme exact | message d'erreur, durée, fréquence, poste et service |
| Adresse réellement tentée | source, destination IPv6 et réponse DNS |
| Route | route la plus spécifique et prochain saut |
| NDP | voisin du prochain saut et échanges NS/NA |
| Capture | RA, TCP, ICMPv6 et Packet Too Big selon le cas |
| Hypothèse démontrée | preuve qui confirme et preuve qui écarte les alternatives |
| Correction minimale | changement unique, justification et risque |
| Validation | tests réussis, non-régression IPv4/IPv6 et résultats archivés |

**Critère de réussite :** le rapport ne doit pas annoncer une cause racine sans preuve. Si la capture ne permet pas de trancher, précise le prochain point d'observation nécessaire au lieu d'inventer une conclusion.


## 22. Fiche de révision intermédiaire

### Plan d'adressage

- Un plan hiérarchique permet d'agréger les routes et de reconnaître les sites et les fonctions.
- Un `/64` est le format courant d'un LAN IPv6 qui utilise SLAAC ; les liens spéciaux doivent être conçus et documentés explicitement.
- GUA et ULA répondent à des portées et politiques différentes ; une GUA n'implique pas qu'un service est ouvert à Internet.

### SLAAC / DHCPv6

- Le RA communique le préfixe, la durée de vie du routeur et d'autres options.
- Les drapeaux M et O sont des indications sur l'usage de DHCPv6, pas une preuve de réussite de l'attribution.
- DHCPv6 peut gérer les adresses, donner d'autres paramètres ou déléguer un préfixe ; ces usages doivent être distingués.
- DHCPv6 ne remplace pas la découverte de la route par défaut via RA dans le modèle courant.

### Routage et DNS

- Une interface correctement adressée ne garantit pas une route distante.
- Une route aller doit être accompagnée d'une route retour correcte.
- Les AAAA doivent pointer vers des destinations qui existent et sont accessibles selon la politique voulue.
- Double pile signifie deux plans de connectivité et de sécurité à contrôler.

### Diagnostic et sécurité

- NDP résout les voisins du lien ; la table de routage choisit le prochain saut.
- ICMPv6 remplit des fonctions nécessaires, notamment NDP et PMTUD ; ne le bloque pas globalement.
- RA Guard et les protections DHCPv6/NDP exigent une politique de confiance et une vérification des limites de plateforme.
- Le diagnostic doit associer une hypothèse, un test discriminant et une preuve recueillie au bon endroit.


## 23. Glossaire ciblé

| Terme | Définition dans le contexte de ce cours |
|---|---|
| A / AAAA | Enregistrements DNS pour IPv4 / IPv6 |
| DAD | Duplicate Address Detection : détection d'une adresse IPv6 dupliquée sur le lien |
| DUID | Identifiant utilisé par DHCPv6 pour reconnaître client ou serveur |
| GUA | Global Unicast Address, adresse unicast globale |
| IAID | Identifiant d'association DHCPv6, utile pour distinguer des associations |
| L flag | Indique le caractère on-link d'un préfixe dans l'option de préfixe de RA |
| M / O | Drapeaux de RA associés à la disponibilité de la configuration DHCPv6 |
| NDP | Neighbor Discovery Protocol, mécanismes IPv6 de découverte de voisins/routeurs |
| NS / NA | Neighbor Solicitation / Neighbor Advertisement |
| OSPFv3 | Version d'OSPF prenant en charge IPv6 et, dans des modes plus récents, des familles d'adresses différentes |
| PD | Prefix Delegation : délégation d'un bloc de préfixes à un routeur demandeur |
| PMTUD | Path MTU Discovery, découverte de la taille maximale utilisable sur le chemin |
| RA / RS | Router Advertisement / Router Solicitation |
| RA Guard | Contrôle de couche 2 visant à bloquer des RA non autorisés sur les ports définis |
| SLAAC | Stateless Address Autoconfiguration, autoconfiguration d'adresse sans serveur DHCPv6 avec état |
| ULA | Unique Local Address, espace unicast destiné à l'usage local/interne |


## 24. Références techniques

Les RFC décrivent le protocole et les standards ; elles ne garantissent pas que chaque système ou plate-forme propose la même commande. Pour un changement matériel, vérifie le guide de la version logicielle et les limites de la fonction.

- **RFC 8200 — Internet Protocol, Version 6 (IPv6) Specification** : https://www.rfc-editor.org/rfc/rfc8200.html
- **RFC 4291 — IP Version 6 Addressing Architecture** : https://www.rfc-editor.org/rfc/rfc4291.html
- **RFC 5952 — A Recommendation for IPv6 Address Text Representation** : https://www.rfc-editor.org/rfc/rfc5952.html
- **RFC 4861 — Neighbor Discovery for IP version 6 (IPv6)** : https://www.rfc-editor.org/rfc/rfc4861.html
- **RFC 4862 — IPv6 Stateless Address Autoconfiguration** : https://www.rfc-editor.org/rfc/rfc4862.html
- **RFC 9915 — Dynamic Host Configuration Protocol for IPv6 (DHCPv6)**, publié en janvier 2026 et remplaçant RFC 8415 : https://www.rfc-editor.org/rfc/rfc9915.html
- **RFC 4193 — Unique Local IPv6 Unicast Addresses** : https://www.rfc-editor.org/rfc/rfc4193.html
- **RFC 6724 — Default Address Selection for IPv6** : https://www.rfc-editor.org/rfc/rfc6724.html
- **RFC 8981 — Temporary Address Extensions for SLAAC** : https://www.rfc-editor.org/rfc/rfc8981.html
- **RFC 8201 — Path MTU Discovery for IPv6** : https://www.rfc-editor.org/rfc/rfc8201.html
- **RFC 4443 — Internet Control Message Protocol (ICMPv6)** : https://www.rfc-editor.org/rfc/rfc4443.html
- **Cisco IOS XE — IPv6 Static Routing** : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m_ip6-route-static-xe.html
- **Cisco IOS XE — OSPFv3** : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m_ip6-route-ospfv3-xe.html
- **Cisco IOS XE — IPv6 RA Guard** : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/sec-vpn/b-security-vpn/m_ip6-ra-guard.html


## Conclusion — Ce qui change au niveau Intermédiaire

Au niveau Débutant, tu apprenais à lire une adresse, reconnaître les messages NDP et faire fonctionner une première configuration IPv6. Au niveau Intermédiaire, tu dois être capable d'expliquer **pourquoi** une configuration réelle fonctionne ou échoue : quel préfixe est annoncé, comment le client interprète le RA, si DHCPv6 a répondu, quelle route a été sélectionnée, quel voisin correspond au prochain saut, quelle adresse source a été utilisée, et si un message ICMPv6 indispensable a été filtré.

Le niveau Expert pourra ensuite utiliser ces acquis pour concevoir des architectures multi-sites plus complexes, examiner la convergence et la résilience du routage, mettre en œuvre une délégation et une renumérotation à grande échelle, auditer les frontières de confiance et automatiser des contrôles à partir de mesures reproductibles.

La règle centrale reste la même : **une adresse configurée n'est pas une preuve de connectivité**. La connectivité doit être démontrée du lien local à l'application, dans les deux sens, avec des routes cohérentes, une découverte de voisin opérationnelle, une résolution DNS vérifiée et les messages ICMPv6 requis par le chemin.
