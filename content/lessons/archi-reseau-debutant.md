# Architecture Réseau — Niveau Débutant

> **Parcours :** Réseaux informatiques · **Niveau :** Débutant · **Public :** personnes qui découvrent la conception réseau et souhaitent comprendre comment organiser un petit réseau d’entreprise.
>
> **Objectif général :** apprendre à lire, concevoir et documenter une architecture réseau simple, évolutive, sûre et dépannable. Ce cours privilégie les principes qui se transfèrent d’un constructeur à l’autre. Les exemples de CLI Cisco sont indicatifs et doivent être adaptés au modèle, au système et à la version réellement utilisés.

## Comment utiliser ce cours

Lis les chapitres dans l’ordre, reproduis les tableaux sur papier, puis réalise le laboratoire final dans Packet Tracer ou sur du matériel de test. Les diagrammes SVG sont intégrés au présent fichier Markdown : ils n’exigent aucun dossier d’images. Si ton lecteur Markdown a un mode de prévisualisation, ouvre le fichier dans ce mode et actualise-le après remplacement d’une version.

### Compétences visées

À la fin du cours, tu devrais pouvoir expliquer la différence entre une topologie physique et logique, identifier le rôle des principaux équipements, choisir entre une architecture à deux ou trois couches, organiser des VLAN et des sous-réseaux, décrire le parcours d’un paquet, planifier les services de base, placer un pare-feu, prévoir la redondance, et documenter des décisions d’architecture.

### Prérequis

Aucun prérequis technique important. Il est utile de connaître quelques mots comme ordinateur, adresse IP et câble Ethernet, mais ils seront expliqués. Les calculs de sous-réseaux sont présentés progressivement.

## 1. Qu’est-ce qu’une architecture réseau ?

Une **architecture réseau** est le plan d’organisation des équipements, des liens, des adresses, des services et des règles qui permettent aux systèmes de communiquer. Ce n’est pas seulement un dessin de câbles. Une architecture précise aussi qui peut communiquer avec qui, par quel chemin, avec quelle capacité, et comment le service continue si un élément tombe en panne.

On distingue plusieurs vues complémentaires :

- **Vue physique :** emplacements, baies, panneaux de brassage, câbles cuivre ou fibre, ports, alimentations et chemins de câbles.
- **Vue logique :** VLAN, sous-réseaux IP, passerelles, routes, zones de sécurité, services DHCP/DNS et règles de communication.
- **Vue opérationnelle :** supervision, sauvegardes de configuration, procédure de changement, astreinte, tests de bascule et dépannage.
- **Vue de sécurité :** frontières de confiance, identité des utilisateurs ou équipements, filtrage, journalisation et accès d’administration.

Une bonne architecture répond d’abord aux besoins réels. Elle doit être compréhensible, suffisamment performante, simple à exploiter, sécurisée, extensible et raisonnablement coûteuse. Une architecture inutilement complexe peut être plus fragile qu’une architecture modeste bien documentée.

### Exemple : l’entreprise fictive Kalo Services

Kalo Services compte 35 employés, un petit serveur de fichiers, des téléphones IP, du Wi-Fi, une imprimante réseau et un accès Internet. Les visiteurs ne doivent pas accéder aux postes internes. L’entreprise veut éviter qu’une panne d’un seul câble arrête tout le bureau.

Avant de choisir les commutateurs, on liste les besoins : environ 35 ports utilisateurs aujourd’hui, une marge de croissance, séparation des invités, téléphonie, accès Internet protégé, une sauvegarde des configurations et un schéma à jour. Ces besoins déterminent les choix techniques, et non l’inverse.

### Diagramme 1 — Du poste à Internet

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="440" viewBox="0 0 1100 440"><rect x="1" y="1" width="1098" height="438" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Le chemin d’un paquet à travers le réseau</text><rect x="35" y="160" width="145" height="82" rx="14" fill="#132238" stroke="#38bdf8" stroke-width="2" /><text x="107.5" y="196.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">PC / laptop</text><text x="107.5" y="218.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">terminal</text><rect x="225" y="160" width="150" height="82" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><text x="300.0" y="196.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Switch</text><text x="300.0" y="218.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">LAN</text><rect x="425" y="160" width="150" height="82" rx="14" fill="#132238" stroke="#fbbf24" stroke-width="2" /><text x="500.0" y="196.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Routeur</text><text x="500.0" y="218.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">passerelle</text><rect x="625" y="160" width="150" height="82" rx="14" fill="#132238" stroke="#fb7185" stroke-width="2" /><text x="700.0" y="196.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Pare-feu</text><text x="700.0" y="218.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">filtrage</text><rect x="825" y="160" width="120" height="82" rx="14" fill="#132238" stroke="#c4b5fd" stroke-width="2" /><text x="885.0" y="196.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">FAI</text><text x="885.0" y="218.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">WAN</text><circle cx="1010" cy="188" r="32" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><circle cx="1033" cy="177" r="25" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><circle cx="1044" cy="196" r="27" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><line x1="985" y1="210" x2="1067" y2="210" stroke="#22d3ee" stroke-width="2" stroke-linecap="round" /><text x="1020" y="250" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Internet</text><line x1="180" y1="201" x2="225" y2="201" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="225" y1="201" x2="215.62223025734545" y2="206.74955951823725" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="225" y1="201" x2="215.62223025734545" y2="195.25044048176275" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="375" y1="201" x2="425" y2="201" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="425" y1="201" x2="415.62223025734545" y2="206.74955951823725" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="425" y1="201" x2="415.62223025734545" y2="195.25044048176275" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="575" y1="201" x2="625" y2="201" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="625" y1="201" x2="615.6222302573454" y2="206.74955951823725" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="625" y1="201" x2="615.6222302573454" y2="195.25044048176275" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="775" y1="201" x2="825" y2="201" stroke="#fb7185" stroke-width="3" stroke-linecap="round" /><line x1="825" y1="201" x2="815.6222302573454" y2="206.74955951823725" stroke="#fb7185" stroke-width="3" stroke-linecap="round" /><line x1="825" y1="201" x2="815.6222302573454" y2="195.25044048176275" stroke="#fb7185" stroke-width="3" stroke-linecap="round" /><line x1="945" y1="201" x2="978" y2="201" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="978" y1="201" x2="968.6222302573454" y2="206.74955951823725" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="978" y1="201" x2="968.6222302573454" y2="195.25044048176275" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><text x="110" y="287" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="normal" fill="#cbd5e1" text-anchor="middle">Réseau local</text><text x="500" y="287" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="normal" fill="#cbd5e1" text-anchor="middle">Interconnexion IP</text><text x="885" y="287" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="normal" fill="#cbd5e1" text-anchor="middle">Accès opérateur</text><rect x="215" y="118" width="160" height="24" rx="8" fill="#163927" stroke="#4ade80" stroke-width="1" /><text x="295" y="135" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="bold" fill="#4ade80" text-anchor="middle">Couche 2</text><rect x="415" y="118" width="370" height="24" rx="8" fill="#3c2f12" stroke="#fbbf24" stroke-width="1" /><text x="600" y="135" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="bold" fill="#fbbf24" text-anchor="middle">Couche 3 + politique de sécurité</text></svg>

Le dessin montre un chemin courant, pas une obligation universelle. Un routeur et un pare-feu peuvent être séparés ou réunis dans le même équipement. Un réseau domestique peut combiner routeur, pare-feu, point d’accès et commutateur dans une seule box. Dans un réseau d’entreprise, des fonctions distinctes facilitent parfois la sécurité, la capacité et la gestion.

## 2. Les familles de réseaux

**LAN (Local Area Network)** désigne le réseau local d’une pièce, d’un étage ou d’un bâtiment. **WLAN** désigne une connexion locale sans fil, principalement Wi-Fi. **WAN (Wide Area Network)** relie des lieux éloignés, par exemple deux agences. **MAN** décrit historiquement un réseau à l’échelle métropolitaine. Ces appellations indiquent surtout l’échelle et le contexte, pas nécessairement une technologie unique.

Un réseau d’entreprise peut réunir le LAN câblé, le WLAN, les liens entre bâtiments, les services du centre de données, les accès cloud et les connexions WAN. Les frontières géographiques et les frontières de sécurité ne sont pas forcément les mêmes : deux appareils dans le même bâtiment peuvent appartenir à des zones logiques très différentes.

### Réseaux filaires et sans fil

Le filaire Ethernet apporte généralement une connexion stable, des débits prévisibles et une faible latence. Le Wi-Fi apporte de la mobilité, mais le médium radio est partagé, sensible aux obstacles, aux interférences et à la densité d’appareils. Ils se complètent : un point d’accès Wi-Fi est souvent relié par câble au réseau d’accès.

### Les éléments principaux

| Élément | Rôle principal | Point d’attention |
|---|---|---|
| Carte réseau (NIC) | Connecte un appareil au réseau | Vitesse, duplex, pilote, adresse MAC |
| Commutateur (switch) | Transporte des trames dans un LAN | VLAN, ports, boucles, capacité des uplinks |
| Routeur | Transfère des paquets entre réseaux IP | Routes, prochaine étape, capacité |
| Commutateur L3 | Combine commutation et routage IP | Fonctions disponibles selon modèle/licence |
| Pare-feu | Autorise ou bloque les flux selon une politique | Règles, état des connexions, journalisation |
| Point d’accès Wi-Fi | Relie des clients radio au LAN | Couverture, canaux, sécurité, capacité |
| Modem/ONT | Termine le service d’accès fourni par l’opérateur | Technologie d’accès et mode de remise |
| Serveur | Fournit un service réseau ou applicatif | Disponibilité, sauvegardes, accès minimum |
| Onduleur (UPS) | Maintient temporairement l’alimentation | Autonomie, charge, tests de batterie |

### Commutateur et routeur : ne pas les confondre

Un commutateur Ethernet utilise principalement les adresses MAC pour transférer les trames à l’intérieur d’un domaine de couche 2. Un routeur utilise la destination IP et sa table de routage pour choisir le prochain saut entre réseaux IP. Les commutateurs multicouches peuvent faire les deux, mais les concepts restent distincts. Un appareil qui possède plusieurs fonctions n’abolit pas la différence entre ces fonctions.

## 3. Topologie physique et topologie logique

La **topologie physique** décrit les liens réels entre équipements. La **topologie logique** décrit comment les données circulent et comment le réseau est segmenté. Le schéma physique d’un commutateur connecté à deux autres commutateurs peut correspondre à plusieurs VLAN, donc à plusieurs domaines logiques. À l’inverse, plusieurs équipements physiques peuvent offrir une seule fonction logique redondante.

### Principales topologies

- **Étoile :** les équipements se connectent à un point central. Facile à comprendre et à dépanner ; le commutateur central devient un point important à protéger.
- **Anneau :** chaque nœud possède un voisin de chaque côté. Des technologies ou protocoles adaptés peuvent gérer la résilience, mais un anneau mal conçu peut se comporter de manière imprévisible.
- **Maillée :** plusieurs équipements sont reliés par plusieurs chemins. La résilience augmente, mais aussi le coût et la complexité de contrôle des boucles et du routage.
- **Arbre / hiérarchie :** plusieurs étoiles sont organisées en couches. C’est un modèle fréquent dans les réseaux de campus.
- **Point à point :** un lien relie directement deux équipements, souvent en fibre entre commutateurs ou routeurs.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="455" viewBox="0 0 1100 455"><rect x="1" y="1" width="1098" height="453" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Topologies physiques : compromis principaux</text><text x="180" y="86" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="bold" fill="#38bdf8" text-anchor="middle">ÉTOILE</text><text x="550" y="86" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="bold" fill="#fbbf24" text-anchor="middle">ANNEAU</text><text x="920" y="86" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="bold" fill="#4ade80" text-anchor="middle">MAILLE PARTIELLE</text><circle cx="180" cy="235" r="34" fill="#123752" stroke="#38bdf8" stroke-width="3" /><text x="180" y="241" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="bold" fill="#f8fafc" text-anchor="middle">SW</text><line x1="180" y1="235" x2="90" y2="165" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><circle cx="90" cy="165" r="20" fill="#132238" stroke="#38bdf8" stroke-width="2" /><text x="90" y="170" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="bold" fill="#f8fafc" text-anchor="middle">PC1</text><line x1="180" y1="235" x2="270" y2="165" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><circle cx="270" cy="165" r="20" fill="#132238" stroke="#38bdf8" stroke-width="2" /><text x="270" y="170" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="bold" fill="#f8fafc" text-anchor="middle">PC2</text><line x1="180" y1="235" x2="90" y2="305" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><circle cx="90" cy="305" r="20" fill="#132238" stroke="#38bdf8" stroke-width="2" /><text x="90" y="310" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="bold" fill="#f8fafc" text-anchor="middle">PC3</text><line x1="180" y1="235" x2="270" y2="305" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><circle cx="270" cy="305" r="20" fill="#132238" stroke="#38bdf8" stroke-width="2" /><text x="270" y="310" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="bold" fill="#f8fafc" text-anchor="middle">PC4</text><line x1="470" y1="160" x2="620" y2="160" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="620" y1="160" x2="620" y2="300" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="620" y1="300" x2="470" y2="300" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="470" y1="300" x2="470" y2="160" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><circle cx="470" cy="160" r="23" fill="#132238" stroke="#fbbf24" stroke-width="2" /><text x="470" y="165" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#f8fafc" text-anchor="middle">S1</text><circle cx="620" cy="160" r="23" fill="#132238" stroke="#fbbf24" stroke-width="2" /><text x="620" y="165" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#f8fafc" text-anchor="middle">S2</text><circle cx="620" cy="300" r="23" fill="#132238" stroke="#fbbf24" stroke-width="2" /><text x="620" y="305" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#f8fafc" text-anchor="middle">S3</text><circle cx="470" cy="300" r="23" fill="#132238" stroke="#fbbf24" stroke-width="2" /><text x="470" y="305" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#f8fafc" text-anchor="middle">S4</text><line x1="850" y1="160" x2="990" y2="160" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="850" y1="160" x2="850" y2="300" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="990" y1="160" x2="990" y2="300" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="850" y1="300" x2="990" y2="300" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="850" y1="160" x2="990" y2="300" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><circle cx="850" cy="160" r="23" fill="#132238" stroke="#4ade80" stroke-width="2" /><text x="850" y="165" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#f8fafc" text-anchor="middle">N1</text><circle cx="990" cy="160" r="23" fill="#132238" stroke="#4ade80" stroke-width="2" /><text x="990" y="165" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#f8fafc" text-anchor="middle">N2</text><circle cx="850" cy="300" r="23" fill="#132238" stroke="#4ade80" stroke-width="2" /><text x="850" y="305" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#f8fafc" text-anchor="middle">N3</text><circle cx="990" cy="300" r="23" fill="#132238" stroke="#4ade80" stroke-width="2" /><text x="990" y="305" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#f8fafc" text-anchor="middle">N4</text><text x="180" y="370" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#cbd5e1" text-anchor="middle">Simple à comprendre</text><text x="550" y="370" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#cbd5e1" text-anchor="middle">Chemin alternatif possible</text><text x="920" y="370" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#cbd5e1" text-anchor="middle">Plusieurs liens indépendants</text><text x="550" y="420" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#f8fafc" text-anchor="middle">Choisir selon la résilience, le coût, le câblage et le comportement des protocoles.</text></svg>

Une liaison supplémentaire ne rend pas automatiquement un réseau meilleur. Il faut savoir quel mécanisme empêchera les boucles de couche 2 ou utilisera les chemins redondants au niveau IP. Dans un réseau commuté Ethernet, les liens redondants doivent être gérés par une conception L2 adaptée, souvent avec une famille de protocoles Spanning Tree, ou par une architecture routée qui réduit la dépendance à un seul grand domaine L2.

## 4. Architecture hiérarchique : accès, distribution et cœur

Le modèle classique de réseau de campus sépare les fonctions en trois couches logiques. Il aide à organiser un réseau, mais n’impose pas forcément trois équipements physiques distincts.

### Couche d’accès

Elle relie les utilisateurs et terminaux : ordinateurs, téléphones, imprimantes, caméras, points d’accès et objets connectés. On y rencontre des ports utilisateur, des VLAN, l’alimentation PoE lorsque nécessaire, le contrôle d’accès au réseau et des protections contre certaines erreurs de bord de réseau.

### Couche de distribution

Elle agrège les commutateurs d’accès. Selon l’architecture, elle peut héberger les interfaces de passerelle des VLAN, le routage inter-VLAN, des politiques de filtrage ou de qualité de service, et la frontière entre le bloc d’accès et les autres parties du réseau. C’est un niveau important pour limiter les domaines de panne et appliquer des règles cohérentes.

### Couche cœur (core)

Elle fournit un transport rapide et résilient entre les blocs de distribution, les services partagés et les autres zones du réseau. Dans une grande architecture, le cœur doit rester aussi simple et prévisible que possible. Les fonctions de sécurité ou de politique très complexes sont souvent mieux placées à des frontières dédiées, plutôt que dispersées dans le cœur sans nécessité.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="455" viewBox="0 0 1100 455"><rect x="1" y="1" width="1098" height="453" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Architecture hiérarchique à trois couches</text><line x1="470" y1="138" x2="300" y2="198" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="300" y1="198" x2="306.92957714210445" y2="189.45711052209947" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="300" y1="198" x2="310.75671529367423" y2="200.30066861821393" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="630" y1="138" x2="800" y2="198" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="800" y1="198" x2="789.2432847063258" y2="200.30066861821393" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="800" y1="198" x2="793.0704228578956" y2="189.45711052209947" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="225" y1="270" x2="175" y2="330" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="175" y1="330" x2="176.58656792267155" y2="319.11501942001047" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="175" y1="330" x2="185.42043586311453" y2="326.4765760370463" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="375" y1="270" x2="435" y2="330" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="435" y1="330" x2="424.3033628983817" y2="327.4344679467442" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="435" y1="330" x2="432.4344679467442" y2="319.3033628983817" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="725" y1="270" x2="695" y2="330" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="695" y1="330" x2="694.0513037549995" y2="319.04098656654156" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="695" y1="330" x2="704.336428493767" y2="324.1835489359254" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="725" y1="106" x2="850" y2="106" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="850" y1="106" x2="840.6222302573454" y2="111.74955951823725" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="850" y1="106" x2="840.6222302573454" y2="100.25044048176275" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><rect x="375" y="76" width="350" height="62" rx="14" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><rect x="375" y="76" width="8" height="62" rx="3" fill="#22d3ee" stroke="#22d3ee" stroke-width="0" /><text x="550.0" y="102.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">CŒUR (CORE)</text><text x="550.0" y="124.0" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#f8fafc" text-anchor="middle">Transport rapide entre blocs</text><rect x="150" y="198" width="300" height="72" rx="14" fill="#132238" stroke="#fbbf24" stroke-width="2" /><rect x="150" y="198" width="8" height="72" rx="3" fill="#fbbf24" stroke="#fbbf24" stroke-width="0" /><text x="300.0" y="229.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">DISTRIBUTION A</text><text x="300.0" y="251.0" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#f8fafc" text-anchor="middle">Agrégation, routage, politiques</text><rect x="650" y="198" width="300" height="72" rx="14" fill="#132238" stroke="#fbbf24" stroke-width="2" /><rect x="650" y="198" width="8" height="72" rx="3" fill="#fbbf24" stroke="#fbbf24" stroke-width="0" /><text x="800.0" y="229.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">DISTRIBUTION B</text><text x="800.0" y="251.0" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#f8fafc" text-anchor="middle">Agrégation, routage, politiques</text><rect x="850" y="76" width="205" height="60" rx="14" fill="#132238" stroke="#38bdf8" stroke-width="2" /><rect x="850" y="76" width="8" height="60" rx="3" fill="#38bdf8" stroke="#38bdf8" stroke-width="0" /><text x="952.5" y="101.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">SERVICES / WAN</text><text x="952.5" y="123.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">services partagés</text><rect x="60" y="330" width="230" height="68" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="60" y="330" width="8" height="68" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="175.0" y="359.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">ACCÈS — Étage 1</text><text x="175.0" y="381.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">PC • téléphone • AP</text><rect x="320" y="330" width="230" height="68" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="320" y="330" width="8" height="68" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="435.0" y="359.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">ACCÈS — Étage 2</text><text x="435.0" y="381.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">PC • imprimantes</text><rect x="580" y="330" width="230" height="68" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="580" y="330" width="8" height="68" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="695.0" y="359.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">ACCÈS — Bâtiment B</text><text x="695.0" y="381.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">PC • Wi-Fi</text><text x="480" y="425" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#cbd5e1" text-anchor="middle">Trois couches logiques ; les couches physiques se choisissent selon la taille et les besoins.</text></svg>

### Architecture à deux couches (cœur condensé)

Un site de taille modeste peut réunir logiquement distribution et cœur. Deux commutateurs L3 peuvent prendre en charge les passerelles et relier les commutateurs d’accès. Cette architecture économise des équipements et reste hiérarchique. Elle doit toutefois être dimensionnée : une panne, une mise à jour ou une erreur de configuration affectant le bloc condensé peut toucher une grande partie du site.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="470" viewBox="0 0 1100 470"><rect x="1" y="1" width="1098" height="468" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Architecture à deux couches (cœur condensé)</text><rect x="370" y="85" width="360" height="70" rx="14" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><rect x="370" y="85" width="8" height="70" rx="3" fill="#22d3ee" stroke="#22d3ee" stroke-width="0" /><text x="550.0" y="115.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">DISTRIBUTION + CŒUR</text><text x="550.0" y="137.0" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#f8fafc" text-anchor="middle">Commutateurs L3 redondants</text><rect x="80" y="245" width="250" height="75" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="80" y="245" width="8" height="75" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="205.0" y="277.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">ACCÈS A</text><text x="205.0" y="299.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">VLAN utilisateurs</text><rect x="425" y="245" width="250" height="75" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="425" y="245" width="8" height="75" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="550.0" y="277.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">ACCÈS B</text><text x="550.0" y="299.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">VLAN téléphones / Wi-Fi</text><rect x="770" y="245" width="250" height="75" rx="14" fill="#132238" stroke="#38bdf8" stroke-width="2" /><rect x="770" y="245" width="8" height="75" rx="3" fill="#38bdf8" stroke="#38bdf8" stroke-width="0" /><text x="895.0" y="277.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">SERVEURS</text><text x="895.0" y="299.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">DHCP • DNS • fichiers</text><line x1="430" y1="155" x2="250" y2="245" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="250" y1="245" x2="255.81645106407464" y2="235.66357150623296" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="250" y1="245" x2="260.95901343345844" y2="245.94869624500052" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="155" x2="550" y2="245" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="245" x2="544.2504404817628" y2="235.62223025734545" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="245" x2="555.7495595182372" y2="235.62223025734545" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="670" y1="155" x2="895" y2="245" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="895" y1="245" x2="884.1576265832399" y2="246.85551574812325" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="895" y1="245" x2="888.4282921796724" y2="236.1788517570417" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="140" y1="320" x2="140" y2="353" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="140" y1="353" x2="140" y2="375" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="140" y1="375" x2="134.25044048176275" y2="365.62223025734545" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="140" y1="375" x2="145.74955951823725" y2="365.62223025734545" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><rect x="55" y="375" width="170" height="44" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><text x="140.0" y="403.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Postes clients</text><line x1="485" y1="320" x2="485" y2="353" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="485" y1="353" x2="485" y2="375" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="485" y1="375" x2="479.2504404817627" y2="365.62223025734545" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="485" y1="375" x2="490.7495595182373" y2="365.62223025734545" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><rect x="400" y="375" width="170" height="44" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><text x="485.0" y="403.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Wi-Fi / VoIP</text><text x="550" y="445" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#fbbf24" text-anchor="middle">Modèle adapté aux sites modestes ; il ne supprime pas les risques de panne commune.</text></svg>

### Comment choisir ?

| Situation | Point de départ raisonnable | Pourquoi |
|---|---|---|
| Petit bureau ou une pièce | Switch manageable + routeur/pare-feu | Besoin limité, configuration simple |
| Un bâtiment, plusieurs étages | Accès + distribution/cœur condensé | Agrégation et routage local organisés |
| Plusieurs bâtiments, fortes exigences | Accès + distribution + cœur dédié | Modularité, résilience et expansion |
| Sites éloignés | LAN par site + WAN/VPN/SD-WAN selon besoins | Séparer problèmes locaux et inter-sites |

Ce tableau est une orientation, pas une règle absolue. La taille du réseau, les flux, les attentes de disponibilité, les compétences de l’équipe, les distances de câblage, la densité Wi-Fi et les contraintes de maintenance influencent le choix. L’essentiel est de documenter les fonctions de chaque bloc et le comportement attendu en cas de panne.

## 5. Ethernet, ports et supports physiques

### Cuivre et fibre

Le cuivre à paires torsadées est courant pour relier les postes aux commutateurs. Le câblage permanent, les cordons de brassage, les connecteurs, la longueur du canal et la catégorie choisie doivent être cohérents avec le débit visé. La fibre optique convient notamment aux longues distances et aux liaisons montantes à haute capacité, à condition de faire correspondre le type de fibre, les modules optiques, les connecteurs et la longueur d’onde.

Ne choisis pas un module optique uniquement parce qu’il entre dans le port. Vérifie les spécifications de l’équipement, le type de fibre, le budget optique, la portée, la vitesse et les contraintes de compatibilité du fabricant. Les adaptateurs ou modules non supportés peuvent fonctionner dans certains cas, être limités dans d’autres ou être refusés par le système.

### Vitesse, duplex et auto-négociation

Les deux extrémités d’un lien doivent s’accorder sur une vitesse et un mode duplex compatibles. Une configuration manuelle incohérente peut produire des pertes, des erreurs et des performances instables. Dans les installations modernes, l’auto-négociation est généralement le choix par défaut lorsqu’elle est prise en charge correctement aux deux extrémités. Vérifie l’état opérationnel, les compteurs d’erreurs, les drops et l’état physique avant de supposer que le problème vient du routage.

### PoE

Le Power over Ethernet permet d’alimenter certains téléphones, points d’accès et caméras via le câble Ethernet. Le dimensionnement doit inclure le nombre de ports, le budget total de puissance du commutateur, le besoin maximal de chaque appareil et le comportement en cas de coupure d’alimentation. Un switch peut avoir assez de ports mais pas assez de puissance PoE pour les alimenter tous simultanément.

### Baies, brassage et étiquetage

Chaque lien doit être repérable aux deux extrémités. Un nom de port comme `SW-ET1-01 Gi1/0/12` est plus utile qu’une note vague comme « câble bureau ». Documente le commutateur, le port, la prise murale, le panneau de brassage, la pièce et l’équipement connecté. Maintiens un peu de réserve dans les ports, l’espace de baie, l’alimentation et les conduits de câbles.

## 6. VLAN : créer des segments logiques

Un **VLAN** est un domaine de couche 2 logique. Les VLAN permettent de séparer des groupes d’équipements même s’ils partagent un même commutateur physique. Par exemple : VLAN 10 pour les employés, VLAN 20 pour les invités, VLAN 30 pour les serveurs et VLAN 99 pour la gestion. Le numéro et le nom d’un VLAN sont des conventions locales : il faut un plan cohérent et documenté.

Les VLAN n’offrent pas, à eux seuls, une politique de sécurité complète. Ils séparent les domaines de diffusion L2, mais les communications entre VLANs peuvent être autorisées par le routage. Les contrôles d’accès doivent être conçus explicitement : ACL, pare-feu, contrôle d’identité ou politique adaptée au contexte.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="445" viewBox="0 0 1100 445"><rect x="1" y="1" width="1098" height="443" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Segmentation logique par VLAN</text><rect x="390" y="85" width="320" height="65" rx="14" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><rect x="390" y="85" width="8" height="65" rx="3" fill="#22d3ee" stroke="#22d3ee" stroke-width="0" /><text x="550.0" y="112.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Commutateur manageable</text><text x="550.0" y="134.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">VLAN 10 / VLAN 20</text><rect x="55" y="220" width="265" height="78" rx="14" fill="#172f25" stroke="#4ade80" stroke-width="2" /><rect x="55" y="220" width="8" height="78" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="187.5" y="254.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">VLAN 10 — Employés</text><text x="187.5" y="276.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">192.168.10.0/24</text><rect x="420" y="220" width="265" height="78" rx="14" fill="#3a202a" stroke="#fb7185" stroke-width="2" /><rect x="420" y="220" width="8" height="78" rx="3" fill="#fb7185" stroke="#fb7185" stroke-width="0" /><text x="552.5" y="254.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">VLAN 20 — Invités</text><text x="552.5" y="276.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">192.168.20.0/24</text><rect x="785" y="220" width="265" height="78" rx="14" fill="#302745" stroke="#c4b5fd" stroke-width="2" /><rect x="785" y="220" width="8" height="78" rx="3" fill="#c4b5fd" stroke="#c4b5fd" stroke-width="0" /><text x="917.5" y="254.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">VLAN 30 — Serveurs</text><text x="917.5" y="276.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">192.168.30.0/24</text><line x1="500" y1="150" x2="188" y2="220" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="150" x2="550" y2="220" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="600" y1="150" x2="918" y2="220" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="75" y1="325" x2="300" y2="325" stroke="#4ade80" stroke-width="2" stroke-linecap="round" stroke-dasharray="8 7" /><text x="188" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#4ade80" text-anchor="middle">Domaine L2 isolé</text><line x1="438" y1="325" x2="667" y2="325" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-dasharray="8 7" /><text x="550" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#fb7185" text-anchor="middle">Domaine L2 isolé</text><line x1="803" y1="325" x2="1030" y2="325" stroke="#c4b5fd" stroke-width="2" stroke-linecap="round" stroke-dasharray="8 7" /><text x="918" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#c4b5fd" text-anchor="middle">Domaine L2 isolé</text><text x="550" y="410" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">La communication entre VLANs exige du routage L3 et des règles adaptées.</text></svg>

### Ports access et trunks

- Un **port access** associe généralement le port à un VLAN non tagué pour un terminal final.
- Un **trunk** transporte plusieurs VLANs entre équipements, en utilisant un mécanisme de marquage tel que IEEE 802.1Q.
- Le **VLAN natif** sur un trunk est un sujet de cohérence et de sécurité : les deux extrémités doivent avoir une configuration compatible. Dans les conceptions récentes, il est préférable d’éviter d’utiliser le VLAN natif pour le trafic utilisateur ordinaire, si les contraintes de la plateforme le permettent.

Ne place pas un trunk sur un port utilisateur sans besoin précis. Une mauvaise configuration du trunk peut étendre un VLAN au mauvais endroit, provoquer des problèmes de connectivité ou créer une exposition évitable. Sur les ports d’accès, désactive les services de négociation automatique de trunk lorsque l’équipement offre cette possibilité et applique les protections de bord adaptées.

### Exemple de plan VLAN

| ID VLAN | Nom proposé | Usage | Exemple de sous-réseau IPv4 |
|---:|---|---|---|
| 10 | USERS | Ordinateurs d’employés | `192.168.10.0/24` |
| 20 | GUESTS | Wi-Fi visiteurs | `192.168.20.0/24` |
| 30 | SERVERS | Serveurs internes | `192.168.30.0/24` |
| 40 | VOICE | Téléphonie IP | `192.168.40.0/24` |
| 99 | MGMT | Administration réseau | `192.168.99.0/24` |

Ces adresses ne sont que des exemples privés. Vérifie qu’elles ne chevauchent pas un VPN, le réseau du fournisseur, un autre site ou un environnement cloud auquel l’entreprise doit se connecter.

## 7. Adressage IPv4 : sous-réseaux et passerelles

Une adresse IPv4 contient 32 bits. Le masque ou la longueur de préfixe détermine quelle partie identifie le réseau et quelle partie identifie les hôtes dans ce sous-réseau. Par exemple, `192.168.10.25/24` appartient au réseau `192.168.10.0/24`. Dans cet exemple classique, l’adresse réseau est `.0`, l’adresse de broadcast est `.255` et les adresses d’hôtes utilisables sont généralement `.1` à `.254`.

### Les plages IPv4 privées

Les trois blocs réservés aux usages privés par RFC 1918 sont :

| Préfixe | Plage | Exemple d’emploi |
|---|---|---|
| `10.0.0.0/8` | `10.0.0.0` à `10.255.255.255` | Grandes organisations, plans structurés |
| `172.16.0.0/12` | `172.16.0.0` à `172.31.255.255` | Réseaux de taille moyenne à grande |
| `192.168.0.0/16` | `192.168.0.0` à `192.168.255.255` | Petits réseaux ou segments de site |

Une adresse privée n’est pas directement routable sur l’Internet public par défaut. Pour accéder à Internet depuis un réseau utilisant des adresses privées IPv4, l’organisation met souvent en place du NAT à la frontière, en plus du routage, des règles de sécurité et du service du fournisseur. **NAT n’est pas un pare-feu** : la politique de sécurité doit être conçue séparément.

### Passerelle par défaut

Le poste compare l’adresse de destination avec son propre préfixe local. Si la destination est considérée comme locale, il tente de la joindre directement sur le LAN. Si elle est distante, il envoie le paquet à sa passerelle par défaut, qui choisit la suite du chemin. La passerelle est normalement une adresse du sous-réseau local du poste.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="455" viewBox="0 0 1100 455"><rect x="1" y="1" width="1098" height="453" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Deux sous-réseaux et le rôle de la passerelle</text><rect x="45" y="165" width="250" height="92" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="45" y="165" width="8" height="92" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="170.0" y="195.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Réseau A</text><text x="170.0" y="217.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">192.168.10.0/24</text><text x="170.0" y="239.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">Passerelle .1</text><rect x="405" y="165" width="290" height="92" rx="14" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><rect x="405" y="165" width="8" height="92" rx="3" fill="#22d3ee" stroke="#22d3ee" stroke-width="0" /><text x="550.0" y="195.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Routeur / switch L3</text><text x="550.0" y="217.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">Décision par préfixe IP</text><text x="550.0" y="239.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">Table de routage</text><rect x="805" y="165" width="250" height="92" rx="14" fill="#132238" stroke="#fb923c" stroke-width="2" /><rect x="805" y="165" width="8" height="92" rx="3" fill="#fb923c" stroke="#fb923c" stroke-width="0" /><text x="930.0" y="195.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Réseau B</text><text x="930.0" y="217.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">192.168.20.0/24</text><text x="930.0" y="239.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">Passerelle .1</text><line x1="295" y1="210" x2="405" y2="210" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="405" y1="210" x2="395.62223025734545" y2="215.74955951823725" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="405" y1="210" x2="395.62223025734545" y2="204.25044048176275" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="695" y1="210" x2="805" y2="210" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="805" y1="210" x2="795.6222302573454" y2="215.74955951823725" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="805" y1="210" x2="795.6222302573454" y2="204.25044048176275" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><text x="170" y="120" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">PC-A : 192.168.10.25/24</text><text x="930" y="120" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">PC-B : 192.168.20.40/24</text><rect x="320" y="290" width="460" height="80" rx="14" fill="#102c43" stroke="#38bdf8" stroke-width="2" /><text x="550" y="322" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Destination hors du sous-réseau local</text><text x="550" y="348" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="normal" fill="#22d3ee" text-anchor="middle">→ envoyer au prochain saut (passerelle)</text><text x="550" y="420" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#cbd5e1" text-anchor="middle">La passerelle doit être joignable sur le réseau local du poste.</text></svg>

### Dimensionner un sous-réseau

Choisis un préfixe en fonction du nombre d’équipements, de la croissance, des besoins de séparation et de l’exploitation. Un `/24` IPv4 contient 256 adresses totales, dont 254 adresses d’hôtes utilisables dans le modèle courant des LAN IPv4 classiques. Il ne faut pas assigner `/24` à chaque VLAN par automatisme : un petit segment peut avoir besoin de beaucoup moins, alors qu’un réseau sans fil dense peut nécessiter une conception plus fine. L’objectif est d’éviter le gaspillage, mais aussi d’éviter des sous-réseaux trop petits et de la fragmentation inutile.

### Plan d’adressage exemple

| Segment | Préfixe | Passerelle exemple | Attribution |
|---|---|---|---|
| Employés | `192.168.10.0/24` | `192.168.10.1` | DHCP |
| Invités | `192.168.20.0/24` | `192.168.20.1` | DHCP isolé |
| Serveurs | `192.168.30.0/24` | `192.168.30.1` | Statique ou réservation |
| Téléphones | `192.168.40.0/24` | `192.168.40.1` | DHCP avec options spécifiques si nécessaires |
| Gestion | `192.168.99.0/24` | `192.168.99.1` | Accès restreint |

Les adresses de passerelle présentées ici sont conventionnelles, pas obligatoires. Une passerelle peut utiliser une autre adresse du sous-réseau, et en architecture redondante l’adresse visible par les clients peut être une adresse virtuelle fournie par un protocole de redondance de premier saut.

### Notions IPv6 à connaître

IPv6 emploie des adresses de 128 bits et une écriture hexadécimale. Dans les réseaux modernes, les sous-réseaux LAN IPv6 sont couramment planifiés en `/64`, avec des mécanismes d’autoconfiguration et/ou DHCPv6 selon l’environnement. Les adresses locales uniques (ULA), définies dans RFC 4193 et appartenant au préfixe `fc00::/7`, sont destinées à la communication interne ; elles ne sont pas attendues comme préfixes routables sur l’Internet global. IPv6 n’utilise pas de broadcast IPv4 : il s’appuie notamment sur le multicast. La présence d’IPv6 doit être prise en compte dans le filtrage, la supervision et le dépannage, pas laissée comme un angle mort.

## 8. Commutation et routage

### Commutation de couche 2

Quand un commutateur reçoit une trame Ethernet, il apprend généralement l’adresse MAC source sur le port d’entrée et l’associe à ce port dans sa table MAC. Pour une destination connue, il transfère la trame sur le port correspondant à l’intérieur du VLAN. Pour une destination inconnue ou une trame de broadcast, le comportement de diffusion s’applique à l’intérieur du VLAN selon les règles Ethernet et l’état du commutateur.

### Routage de couche 3

Un routeur ou un commutateur L3 consulte sa table de routage afin de choisir le chemin vers le préfixe destination. La route la plus spécifique qui correspond à la destination est généralement retenue, sous réserve des règles de sélection et de la disponibilité de cette route. La table peut contenir des routes connectées, statiques, par défaut ou apprises par un protocole de routage dynamique.

### Routage inter-VLAN

Chaque VLAN qui doit participer au routage IP possède un sous-réseau IP distinct et une passerelle L3. Les passerelles peuvent se trouver sur des sous-interfaces de routeur (router-on-a-stick) ou directement sur un commutateur L3 via des interfaces VLAN, selon la conception. Le choix dépend de la capacité, de la résilience et des fonctions de la plateforme.

Exemple de flux : un poste du VLAN 10 contacte un serveur du VLAN 30. Le poste reconnaît que la destination est hors de son sous-réseau et envoie le paquet à la passerelle du VLAN 10. L’équipement L3 consulte la table de routage et transmet le paquet vers le VLAN 30, sous réserve des politiques de filtrage. Le serveur renvoie sa réponse via sa propre passerelle. Une route aller correcte ne garantit pas toujours un chemin retour correct.

### Notions de routage dynamique

Dans un réseau simple, des routes statiques peuvent suffire. Quand les chemins et les routeurs se multiplient, un protocole de routage dynamique comme OSPF, IS-IS, EIGRP (dans les environnements qui l’utilisent) ou BGP selon le rôle du réseau peut annoncer des préfixes et recalculer des chemins. Ces protocoles ne sont pas interchangeables dans tous les contextes. Ils nécessitent une conception, une politique, une maîtrise des métriques et une supervision. Au niveau débutant, retiens surtout qu’il faut connaître les préfixes annoncés, les voisins, les routes attendues et le comportement en cas de panne.

## 9. Services réseau essentiels

Un réseau utile dépend de services communs. Leur panne peut donner l’impression que tout le réseau est en panne alors que la connectivité IP fonctionne encore.

### DHCP

Le Dynamic Host Configuration Protocol fournit automatiquement les paramètres IP aux clients : adresse, masque/préfixe, passerelle, serveurs DNS, durée du bail et autres options si nécessaires. Une architecture doit prévoir les étendues DHCP par sous-réseau, les exclusions et réservations, la capacité du serveur, les mécanismes de relais DHCP pour les sous-réseaux distants et la protection contre des serveurs DHCP non autorisés.

### DNS

Le Domain Name System traduit des noms en informations comme des adresses IP. Un poste peut joindre une adresse IP mais échouer sur un nom si le DNS est inaccessible ou si l’enregistrement est incorrect. Documente les serveurs DNS, les domaines internes, les redirecteurs et les zones sensibles. Les serveurs DNS internes ne doivent pas être exposés à l’extérieur sans raison et sans politique adaptée.

### NTP, AAA et IPAM

- **NTP** synchronise les horloges. Des horodatages cohérents sont essentiels pour comprendre les événements dans des journaux issus de plusieurs équipements.
- **AAA** regroupe authentification, autorisation et comptabilisation (accounting), notamment pour l’accès d’administration lorsque l’infrastructure le prend en charge.
- **IPAM** aide à gérer les préfixes et les affectations d’adresses ; même un petit réseau peut démarrer avec une feuille rigoureuse et des conventions claires.
- **Syslog et télémétrie** centralisent les événements et mesures, sous réserve de stockage, de droits d’accès et de synchronisation de l’heure.

### Services locaux et hébergement

Décide quels services sont locaux, hébergés dans un centre de données ou consommés dans le cloud. Pour chaque service important, relève son propriétaire, son adresse ou son nom DNS, les ports nécessaires, les utilisateurs qui en ont besoin, la criticité, le mode de sauvegarde et la dépendance à Internet. Sans cette cartographie, les règles réseau risquent d’être trop permissives ou de bloquer un service métier essentiel.

## 10. Accès Internet, NAT et pare-feu

La frontière Internet réunit souvent un routeur opérateur, un pare-feu, un équipement de terminaison d’accès et éventuellement des services de sécurité supplémentaires. La topologie exacte dépend du fournisseur et du besoin. Le dessin logique doit clairement montrer où se trouvent la traduction d’adresses, le filtrage, les connexions VPN et la surveillance.

### NAT/PAT

Le NAT modifie une ou plusieurs composantes des adresses IP et parfois des ports. Le PAT (souvent utilisé pour les accès Internet d’un LAN) permet à plusieurs adresses privées de partager une adresse publique en distinguant les connexions par les ports. Cette fonction doit être documentée afin d’aider au dépannage, à la journalisation et à l’analyse des incidents.

### DMZ

Une DMZ est une zone intermédiaire destinée à héberger certains services accessibles depuis des zones moins fiables. Elle n’est pas automatiquement sûre : le trafic vers et depuis la DMZ doit être limité au strict nécessaire. Un serveur public n’a pas besoin, par défaut, d’un accès libre au LAN interne. Les flux d’administration doivent provenir d’un réseau ou d’une identité autorisée.

### Politique de filtrage

Une politique robuste définit les sources, destinations, services, direction, justification, propriétaire et date de révision des règles importantes. Évite les règles « any-any » persistantes sans justification. Privilégie les autorisations explicites, les refus par défaut adaptés au contexte, une journalisation utile et des tests après tout changement. La journalisation exhaustive de tous les paquets peut cependant coûter cher en stockage et masquer les événements importants : ajuste-la à l’objectif.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="465" viewBox="0 0 1100 465"><rect x="1" y="1" width="1098" height="463" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Zones de sécurité et filtrage</text><rect x="35" y="155" width="150" height="78" rx="14" fill="#132238" stroke="#fb7185" stroke-width="2" /><rect x="35" y="155" width="8" height="78" rx="3" fill="#fb7185" stroke="#fb7185" stroke-width="0" /><text x="110.0" y="189.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Internet</text><text x="110.0" y="211.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">non fiable</text><rect x="250" y="155" width="200" height="78" rx="14" fill="#172b43" stroke="#fb923c" stroke-width="2" /><rect x="250" y="155" width="8" height="78" rx="3" fill="#fb923c" stroke="#fb923c" stroke-width="0" /><text x="350.0" y="189.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Pare-feu</text><text x="350.0" y="211.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">contrôle inter-zones</text><rect x="555" y="80" width="230" height="76" rx="14" fill="#32252b" stroke="#fb7185" stroke-width="2" /><rect x="555" y="80" width="8" height="76" rx="3" fill="#fb7185" stroke="#fb7185" stroke-width="0" /><text x="670.0" y="113.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">DMZ</text><text x="670.0" y="135.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">services publiés</text><rect x="555" y="200" width="230" height="76" rx="14" fill="#173327" stroke="#4ade80" stroke-width="2" /><rect x="555" y="200" width="8" height="76" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="670.0" y="233.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">LAN interne</text><text x="670.0" y="255.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">utilisateurs</text><rect x="555" y="320" width="230" height="76" rx="14" fill="#252442" stroke="#c4b5fd" stroke-width="2" /><rect x="555" y="320" width="8" height="76" rx="3" fill="#c4b5fd" stroke="#c4b5fd" stroke-width="0" /><text x="670.0" y="353.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Réseau admin</text><text x="670.0" y="375.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">gestion protégée</text><line x1="185" y1="194" x2="250" y2="194" stroke="#fb7185" stroke-width="3" stroke-linecap="round" /><line x1="250" y1="194" x2="240.62223025734545" y2="199.74955951823725" stroke="#fb7185" stroke-width="3" stroke-linecap="round" /><line x1="250" y1="194" x2="240.62223025734545" y2="188.25044048176275" stroke="#fb7185" stroke-width="3" stroke-linecap="round" /><line x1="450" y1="175" x2="555" y2="118" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="555" y1="118" x2="549.5013829417319" y2="127.52707774957899" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="555" y1="118" x2="544.0152468188627" y2="117.42103752324105" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="450" y1="194" x2="555" y2="238" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="555" y1="238" x2="544.1288035885975" y2="239.67841847723057" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="555" y1="238" x2="548.5730485723611" y2="229.07283385688544" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="450" y1="210" x2="555" y2="358" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="555" y1="358" x2="544.8844633617973" y2="353.6784356395885" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="555" y1="358" x2="554.2630417797509" y2="347.024714464689" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><rect x="840" y="160" width="220" height="78" rx="14" fill="#132238" stroke="#38bdf8" stroke-width="2" /><rect x="840" y="160" width="8" height="78" rx="3" fill="#38bdf8" stroke="#38bdf8" stroke-width="0" /><text x="950.0" y="194.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Journalisation</text><text x="950.0" y="216.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">logs / alertes</text><line x1="785" y1="118" x2="840" y2="179" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="840" y1="179" x2="829.4501658473605" y2="175.8853572673899" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="840" y1="179" x2="837.9904286739436" y2="168.18512029260188" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="785" y1="238" x2="840" y2="210" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="840" y1="210" x2="834.2513551434887" y2="219.37833046515777" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="840" y1="210" x2="829.0343998539964" y2="209.1307397179407" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="785" y1="358" x2="840" y2="225" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="840" y1="225" x2="841.7294876998862" y2="235.86318886404644" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="840" y1="225" x2="831.103135043346" y2="231.4688325023193" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><text x="550" y="430" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#f8fafc" text-anchor="middle">Autoriser les flux nécessaires ; interdire le reste par défaut selon le contexte.</text></svg>

## 11. Relier les sites : WAN, VPN et cloud

Une agence ne doit pas être pensée comme une extension physique naïve du LAN du siège. Les liens WAN ont des délais, des pertes, des limites de capacité et des dépendances opérateur. Une conception inter-sites définit l’adressage de chaque site, le routage, les services accessibles à distance, la sécurité, les dépendances Internet et le fonctionnement en cas de perte du lien.

Un **VPN** crée un tunnel protégé sur un réseau de transport, généralement au moyen d’un mécanisme cryptographique adapté. Il peut relier deux sites (site-à-site) ou un utilisateur distant au réseau (accès distant). Le VPN ne remplace ni l’authentification, ni le contrôle d’accès, ni la supervision. Il faut aussi prévoir le renouvellement des secrets/certificats et le diagnostic des problèmes de MTU, de routage ou de résolution DNS.

Le **SD-WAN** est une approche logicielle de sélection et de gestion des chemins WAN qui peut prendre en compte plusieurs liens et des exigences applicatives. Ce n’est pas simplement « un routeur plus rapide » : la valeur vient de la politique, de l’observabilité et du comportement de bascule. Les services cloud doivent faire partie de la conception de sécurité : le trafic n’a pas toujours besoin de passer par le siège, mais tout chemin direct doit être gouverné.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="430" viewBox="0 0 1100 430"><rect x="1" y="1" width="1098" height="428" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Interconnexion de sites : WAN et VPN</text><rect x="50" y="170" width="220" height="90" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="50" y="170" width="8" height="90" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="160.0" y="210.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">SIÈGE</text><text x="160.0" y="232.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">LAN + pare-feu</text><rect x="425" y="170" width="230" height="90" rx="14" fill="#172b43" stroke="#c4b5fd" stroke-width="2" /><rect x="425" y="170" width="8" height="90" rx="3" fill="#c4b5fd" stroke="#c4b5fd" stroke-width="0" /><text x="540.0" y="210.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Réseau opérateur</text><text x="540.0" y="232.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">Internet / WAN</text><rect x="820" y="85" width="220" height="80" rx="14" fill="#132238" stroke="#38bdf8" stroke-width="2" /><rect x="820" y="85" width="8" height="80" rx="3" fill="#38bdf8" stroke="#38bdf8" stroke-width="0" /><text x="930.0" y="120.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">AGENCE A</text><text x="930.0" y="142.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">LAN distant</text><rect x="820" y="255" width="220" height="80" rx="14" fill="#132238" stroke="#38bdf8" stroke-width="2" /><rect x="820" y="255" width="8" height="80" rx="3" fill="#38bdf8" stroke="#38bdf8" stroke-width="0" /><text x="930.0" y="290.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">AGENCE B</text><text x="930.0" y="312.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">LAN distant</text><line x1="270" y1="215" x2="425" y2="215" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="425" y1="215" x2="415.62223025734545" y2="220.74955951823725" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="425" y1="215" x2="415.62223025734545" y2="209.25044048176275" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="655" y1="195" x2="820" y2="125" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="820" y1="125" x2="813.6124856096292" y2="133.95542628314286" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="820" y1="125" x2="809.1215064309532" y2="123.36954679054946" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="655" y1="235" x2="820" y2="295" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="820" y1="295" x2="809.2219615877027" y2="297.19861046641813" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="820" y1="295" x2="813.151705750026" y2="286.3918140200287" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="700" y1="170" x2="790" y2="100" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" stroke-dasharray="7 6" /><text x="735" y="124" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="bold" fill="#22d3ee" text-anchor="middle">VPN</text><line x1="700" y1="260" x2="790" y2="300" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" stroke-dasharray="7 6" /><text x="740" y="293" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="bold" fill="#22d3ee" text-anchor="middle">VPN</text><text x="550" y="385" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#f8fafc" text-anchor="middle">Planifier les adresses, la bande passante, le chiffrement et le secours WAN.</text></svg>

### Liste de vérification inter-sites

- Les préfixes sont-ils uniques entre sites, VPN, cloud et partenaires ?
- Le routage aller et retour est-il prévu ?
- Les services DNS/DHCP et les services d’identité restent-ils disponibles si le lien est coupé ?
- Les applications sensibles supportent-elles la latence et la perte estimées ?
- Le chiffrement et l’authentification sont-ils appropriés ?
- Le basculement a-t-il été testé réellement, pas uniquement supposé ?
- Le coût du lien, les quotas de données et les limites de support sont-ils connus ?

## 12. Wi-Fi : couverture, capacité et isolation

Le Wi-Fi doit être conçu pour des **clients**, des **applications** et un **environnement radio** réels. Le nombre de points d’accès ne doit pas être déterminé uniquement par la surface au sol. Les matériaux, la hauteur, les interférences, la densité d’utilisateurs, les types de terminaux, les bandes disponibles et les applications déterminent les besoins. Une couverture radio correcte ne garantit pas une bonne expérience lorsque trop de clients partagent le même temps d’antenne.

### SSID et VLAN

Un SSID est le nom du réseau sans fil annoncé aux clients. Il peut être associé à un VLAN ou à une politique dynamique, selon la plateforme. Le SSID invité doit être isolé des ressources internes et sa sortie Internet doit suivre une politique prévue. Les SSID ne sont pas des frontières de sécurité suffisantes à eux seuls : l’authentification, la segmentation, le filtrage et les réglages des clients doivent être considérés ensemble.

### Mesures importantes

Mesure la couverture utile, le rapport signal/bruit, les interférences, l’utilisation des canaux, les retransmissions, le nombre de clients par point d’accès et l’expérience applicative. Évite de modifier la puissance, la largeur des canaux ou l’affectation des fréquences au hasard ; ces réglages doivent correspondre au plan radio et à l’environnement local. Si le réseau utilise une authentification d’entreprise, documente le serveur d’identité et le comportement de secours.

## 13. Résilience et disponibilité

Une architecture résiliente est conçue pour qu’une panne identifiée ne provoque pas une interruption plus large que nécessaire. La redondance peut concerner les liens, les commutateurs, les alimentations, les routeurs, les accès WAN, le DNS/DHCP, les pare-feu et les services applicatifs. Pour autant, du matériel doublé ne garantit pas la continuité si les deux unités partagent la même alimentation, la même fibre ou la même configuration erronée.

### Domaine de panne et point unique de défaillance

Un **point unique de défaillance** est un élément dont la panne interrompt un service essentiel sans chemin ou composant de remplacement approprié. Un **domaine de panne** est l’ensemble des fonctions affectées par une panne ou une erreur. Les architectures modulaires réduisent souvent l’étendue d’une panne et permettent des changements plus maîtrisés.

### Liens redondants et boucles

En Ethernet de couche 2, des liens redondants peuvent créer une boucle de commutation. Des protocoles de prévention de boucles comme STP/RSTP sélectionnent les chemins actifs en fonction de leur logique. Dans des architectures L3, des chemins redondants peuvent être utilisés par le routage et offrir une convergence prévisible, à condition de bien concevoir les métriques et les politiques. Ne connecte jamais un lien redondant « pour être sûr » sans avoir défini la manière dont le réseau traite les boucles et les défaillances.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="445" viewBox="0 0 1100 445"><rect x="1" y="1" width="1098" height="443" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Redondance : concevoir des chemins, pas des boucles</text><line x1="390" y1="135" x2="190" y2="255" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="660" y1="135" x2="250" y2="255" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><line x1="500" y1="135" x2="820" y2="255" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" /><line x1="770" y1="135" x2="930" y2="255" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" /><rect x="335" y="65" width="220" height="70" rx="14" fill="#132238" stroke="#fbbf24" stroke-width="2" /><rect x="335" y="65" width="8" height="70" rx="3" fill="#fbbf24" stroke="#fbbf24" stroke-width="0" /><text x="445.0" y="95.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Distribution A</text><text x="445.0" y="117.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">passerelles / politiques</text><rect x="615" y="65" width="220" height="70" rx="14" fill="#132238" stroke="#fbbf24" stroke-width="2" /><rect x="615" y="65" width="8" height="70" rx="3" fill="#fbbf24" stroke="#fbbf24" stroke-width="0" /><text x="725.0" y="95.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Distribution B</text><text x="725.0" y="117.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">passerelles / politiques</text><rect x="80" y="255" width="270" height="75" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="80" y="255" width="8" height="75" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="215.0" y="287.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Switch d’accès A</text><text x="215.0" y="309.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">Postes utilisateurs</text><rect x="750" y="255" width="270" height="75" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="750" y="255" width="8" height="75" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="885.0" y="287.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Switch d’accès B</text><text x="885.0" y="309.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">Postes utilisateurs</text><rect x="305" y="355" width="490" height="62" rx="14" fill="#3b2026" stroke="#fb7185" stroke-width="2" /><text x="550" y="381" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">Redondance à concevoir selon L2/L3</text><text x="550" y="404" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="normal" fill="#cbd5e1" text-anchor="middle">STP/RSTP ou routage adapté ; tester les bascules.</text></svg>

### Tester, ne pas seulement installer

Documente les scénarios de panne : retrait d’un uplink, redémarrage d’un commutateur, coupure électrique, indisponibilité DNS, perte du fournisseur ou défaillance d’un tunnel VPN. Mesure le temps de détection, le temps de récupération, les pertes de paquets et l’effet visible pour l’utilisateur. Effectue ces tests dans une fenêtre autorisée, avec une procédure de retour arrière.

## 14. Capacité, performance et qualité de service

La performance doit se mesurer de bout en bout. Une interface à 10 Gbit/s n’implique pas que chaque application obtienne 10 Gbit/s. Le débit réel dépend du chemin complet, des files d’attente, du matériel, du protocole, de l’application, des volumes concurrents et des capacités des serveurs.

### Débit et surabonnement

Le **surabonnement** compare la somme des débits potentiels en entrée à la capacité de sortie ou d’agrégation. Par exemple, plusieurs ports utilisateurs à 1 Gbit/s peuvent être agrégés vers un uplink à 1 Gbit/s. Ce n’est pas automatiquement une erreur : les terminaux ne transmettent pas tous au débit maximum en permanence. Mais l’architecture doit être dimensionnée d’après les usages mesurés et les objectifs de performance.

### Latence, gigue et perte

- **Latence :** temps nécessaire à un paquet pour traverser le chemin.
- **Gigue :** variation de cette latence entre paquets.
- **Perte :** proportion de paquets non reçus ou rejetés.
- **Débit utile :** volume de données réellement transporté sur une période.

Voix et vidéo temps réel sont souvent sensibles à la latence, à la gigue et aux pertes. Les transferts de fichiers peuvent davantage souffrir d’un faible débit soutenu. Il faut donc associer une mesure à un besoin applicatif précis plutôt que de chercher un seul chiffre global.

### QoS

La qualité de service (QoS) classe et traite différemment certains trafics selon une politique. Elle ne crée pas de bande passante ; elle organise le traitement lorsque plusieurs flux se disputent des ressources. Une politique QoS doit être appliquée de manière cohérente sur le chemin et avec une compréhension des marques de trafic. Une mauvaise classification ou une priorité excessive peut pénaliser les autres applications.

## 15. Sécurité dès la conception

La sécurité réseau n’est pas une seule boîte de pare-feu. Elle découle d’une série de décisions : segmentation, identité, moindre privilège, gestion des équipements, protection des ports, chiffrement adapté, mises à jour, sauvegardes et surveillance.

### Principes de base

1. **Moindre privilège :** un utilisateur ou un système ne reçoit que les accès nécessaires à sa fonction.
2. **Segmentation :** séparer les équipements selon les rôles et les niveaux de confiance.
3. **Administration dédiée :** limiter l’accès de gestion à une zone et à des personnes autorisées ; éviter les interfaces d’administration ouvertes à tous les postes.
4. **Accès sécurisé :** préférer des protocoles d’administration protégés, l’authentification individuelle et, lorsqu’ils sont disponibles, des mécanismes centralisés avec journalisation.
5. **Sauvegarde et restauration :** conserver des sauvegardes contrôlées de configurations et vérifier leur utilisabilité.
6. **Journalisation :** synchroniser les horloges, centraliser les événements clés et protéger les données de log.
7. **Révision :** désactiver les ports inutilisés selon la politique locale, réviser les règles et supprimer les accès temporaires devenus inutiles.

### Réseau de gestion

Les interfaces de gestion des commutateurs, routeurs, contrôleurs Wi-Fi et pare-feu doivent être identifiées et protégées. Le réseau de gestion ne doit pas être confondu avec le VLAN utilisateur. Prévois des adresses d’administration, des rôles, l’accès de secours, et une procédure en cas de panne du service AAA central. Toute méthode de secours doit rester protégée et être documentée.

### Contrôle des changements

Avant un changement, note l’objectif, le périmètre, les risques, les commandes prévues, les tests d’acceptation et le plan de retour arrière. Après le changement, compare l’état obtenu à l’état attendu et mets à jour les schémas. Une modification non documentée finit souvent par devenir un problème de diagnostic.

## 16. Supervision et documentation

Une infrastructure qu’on ne mesure pas est difficile à exploiter. La supervision doit couvrir la disponibilité des équipements, l’état des interfaces, les erreurs et drops, l’utilisation CPU/mémoire lorsque cela est pertinent, les liens WAN, les services DNS/DHCP, les points d’accès et l’expérience des applications prioritaires.

### Indicateurs utiles

| Domaine | Exemples d’indicateurs | Pourquoi les suivre |
|---|---|---|
| Liens | état, débit, erreurs CRC, drops | Repérer pannes physiques et congestion |
| Routage | voisins, routes, changements de topologie | Voir les pertes de chemins ou instabilités |
| Services | disponibilité DNS/DHCP/NTP | Distinguer panne applicative et panne réseau |
| Wi-Fi | clients, retransmissions, radio | Comprendre l’expérience sans fil |
| Sécurité | refus de règles, authentifications, anomalies | Détecter comportements inattendus |
| Capacité | utilisation soutenue, files d’attente | Prévoir l’évolution avant la saturation |

### Documentation minimale

Maintiens une topologie physique, une topologie logique, le plan IP, le registre VLAN, la liste des équipements, le tableau des ports et câbles, les règles de flux importantes, les fournisseurs et circuits WAN, les procédures de sauvegarde, les contacts d’escalade et les dates de dernière validation. Les mots de passe et secrets ne doivent pas être copiés en clair dans les schémas ou les documents ordinaires.

## 17. Méthode de conception étape par étape

### Étape 1 — Recueillir les besoins

Demande le nombre d’utilisateurs, les types d’appareils, les applications, les locaux, les accès Internet, les contraintes de disponibilité, le budget, les contraintes réglementaires et la croissance attendue. Les exigences doivent être mesurables quand c’est possible : par exemple, combien d’utilisateurs doivent pouvoir travailler pendant la panne d’un lien ?

### Étape 2 — Faire l’inventaire

Relève les modèles, ports, débits, versions logicielles, liaisons, distances, alimentations, contrats opérateurs et services. Identifie les actifs qui sont déjà présents et ce qui peut être réutilisé sans créer une dette technique excessive.

### Étape 3 — Concevoir les blocs

Définis l’architecture hiérarchique, les frontières L2/L3, les VLAN, le plan IP, le WAN, les zones de sécurité, les services partagés et les points de redondance. Identifie les principaux chemins de flux : utilisateur vers application, invité vers Internet, administrateur vers équipement, site distant vers service interne.

### Étape 4 — Valider les risques et la capacité

Dimensionne les uplinks, les ports PoE, les équipements, la fibre, les alimentations et l’accès Internet. Vérifie les domaines de panne, les besoins de secours, l’exposition des services et les restrictions d’accès. Évite d’ajouter une technologie que personne ne sait maintenir sans plan de formation ou de support.

### Étape 5 — Construire un plan d’implémentation

Décompose la mise en œuvre en changements testables : câblage, VLAN, routage, DHCP/DNS, sécurité, Wi-Fi, supervision, migration des postes et retrait de l’ancien matériel. Prévois les tests et les critères d’acceptation à chaque étape.

### Étape 6 — Tester et documenter

Teste la connectivité, la segmentation, les services, le routage aller-retour, la bascule, la sécurité, la restauration de configuration et les alertes. Mets les diagrammes à jour après validation. Le cycle ci-dessous résume ce processus.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="425" viewBox="0 0 1100 425"><rect x="1" y="1" width="1098" height="423" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Cycle de conception d’une architecture réseau</text><circle cx="87" cy="172" r="34" fill="#132238" stroke="#38bdf8" stroke-width="3" /><text x="87" y="179" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="bold" fill="#38bdf8" text-anchor="middle">1</text><rect x="25" y="230" width="125" height="78" rx="2" fill="#132238" stroke="#38bdf8" stroke-width="2" /><text x="87" y="258" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">Besoins</text><text x="87" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="normal" fill="#cbd5e1" text-anchor="middle">utilisateurs, apps</text><line x1="151" y1="269" x2="198" y2="269" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="198" y1="269" x2="188.62223025734545" y2="274.7495595182373" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="198" y1="269" x2="188.62223025734545" y2="263.2504404817627" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><circle cx="267" cy="172" r="34" fill="#132238" stroke="#22d3ee" stroke-width="3" /><text x="267" y="179" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="bold" fill="#22d3ee" text-anchor="middle">2</text><rect x="205" y="230" width="125" height="78" rx="2" fill="#132238" stroke="#22d3ee" stroke-width="2" /><text x="267" y="258" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">Inventaire</text><text x="267" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="normal" fill="#cbd5e1" text-anchor="middle">ports, liens, locaux</text><line x1="331" y1="269" x2="378" y2="269" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="378" y1="269" x2="368.62223025734545" y2="274.7495595182373" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="378" y1="269" x2="368.62223025734545" y2="263.2504404817627" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><circle cx="447" cy="172" r="34" fill="#132238" stroke="#4ade80" stroke-width="3" /><text x="447" y="179" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="bold" fill="#4ade80" text-anchor="middle">3</text><rect x="385" y="230" width="125" height="78" rx="2" fill="#132238" stroke="#4ade80" stroke-width="2" /><text x="447" y="258" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">Conception</text><text x="447" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="normal" fill="#cbd5e1" text-anchor="middle">VLAN, IP, routes</text><line x1="511" y1="269" x2="558" y2="269" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="558" y1="269" x2="548.6222302573454" y2="274.7495595182373" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="558" y1="269" x2="548.6222302573454" y2="263.2504404817627" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><circle cx="627" cy="172" r="34" fill="#132238" stroke="#fbbf24" stroke-width="3" /><text x="627" y="179" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="bold" fill="#fbbf24" text-anchor="middle">4</text><rect x="565" y="230" width="125" height="78" rx="2" fill="#132238" stroke="#fbbf24" stroke-width="2" /><text x="627" y="258" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">Sécurité</text><text x="627" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="normal" fill="#cbd5e1" text-anchor="middle">zones, règles</text><line x1="691" y1="269" x2="738" y2="269" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="738" y1="269" x2="728.6222302573454" y2="274.7495595182373" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="738" y1="269" x2="728.6222302573454" y2="263.2504404817627" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><circle cx="807" cy="172" r="34" fill="#132238" stroke="#fb923c" stroke-width="3" /><text x="807" y="179" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="bold" fill="#fb923c" text-anchor="middle">5</text><rect x="745" y="230" width="125" height="78" rx="2" fill="#132238" stroke="#fb923c" stroke-width="2" /><text x="807" y="258" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">Validation</text><text x="807" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="normal" fill="#cbd5e1" text-anchor="middle">tests, bascule</text><line x1="871" y1="269" x2="918" y2="269" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="918" y1="269" x2="908.6222302573454" y2="274.7495595182373" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><line x1="918" y1="269" x2="908.6222302573454" y2="263.2504404817627" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" /><circle cx="987" cy="172" r="34" fill="#132238" stroke="#c4b5fd" stroke-width="3" /><text x="987" y="179" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="bold" fill="#c4b5fd" text-anchor="middle">6</text><rect x="925" y="230" width="125" height="78" rx="2" fill="#132238" stroke="#c4b5fd" stroke-width="2" /><text x="987" y="258" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">Documentation</text><text x="987" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="normal" fill="#cbd5e1" text-anchor="middle">plans, sauvegardes</text><text x="550" y="360" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">Chaque étape doit produire une décision vérifiable, pas seulement un dessin.</text><text x="550" y="396" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="normal" fill="#cbd5e1" text-anchor="middle">Prévoir la maintenance, le retour arrière et l’acceptation par les utilisateurs.</text></svg>

## 18. Laboratoire guidé : concevoir le LAN de Kalo Services

### Contexte

Le site contient 24 PC, 4 téléphones IP, 3 imprimantes, 3 points d’accès, 2 serveurs internes et un lien Internet. Le Wi-Fi invité ne doit pas accéder aux serveurs internes. Les équipements de réseau doivent être administrables uniquement depuis un poste dédié ou le réseau de gestion autorisé.

### Proposition d’architecture logique

- VLAN 10 — employés — `192.168.10.0/24`
- VLAN 20 — invités — `192.168.20.0/24`
- VLAN 30 — serveurs — `192.168.30.0/24`
- VLAN 40 — téléphonie — `192.168.40.0/24`
- VLAN 99 — gestion — `192.168.99.0/24`
- Passerelles exemples : `192.168.X.1` au sein de chaque sous-réseau
- DHCP : étendue distincte par VLAN, avec relais DHCP ou service local selon l’emplacement du serveur
- DNS : résolveur défini et documenté ; les noms internes ne sont disponibles qu’aux clients autorisés
- Pare-feu : règle invitée vers Internet autorisée selon la politique ; invité vers LAN interne refusé par défaut, sauf exception explicitement approuvée
- Accès à la gestion : seulement depuis les sources d’administration autorisées

### Schéma logique cible

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="445" viewBox="0 0 1100 445"><rect x="1" y="1" width="1098" height="443" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Segmentation logique par VLAN</text><rect x="390" y="85" width="320" height="65" rx="14" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><rect x="390" y="85" width="8" height="65" rx="3" fill="#22d3ee" stroke="#22d3ee" stroke-width="0" /><text x="550.0" y="112.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">Commutateur manageable</text><text x="550.0" y="134.5" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">VLAN 10 / VLAN 20</text><rect x="55" y="220" width="265" height="78" rx="14" fill="#172f25" stroke="#4ade80" stroke-width="2" /><rect x="55" y="220" width="8" height="78" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="187.5" y="254.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">VLAN 10 — Employés</text><text x="187.5" y="276.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">192.168.10.0/24</text><rect x="420" y="220" width="265" height="78" rx="14" fill="#3a202a" stroke="#fb7185" stroke-width="2" /><rect x="420" y="220" width="8" height="78" rx="3" fill="#fb7185" stroke="#fb7185" stroke-width="0" /><text x="552.5" y="254.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">VLAN 20 — Invités</text><text x="552.5" y="276.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">192.168.20.0/24</text><rect x="785" y="220" width="265" height="78" rx="14" fill="#302745" stroke="#c4b5fd" stroke-width="2" /><rect x="785" y="220" width="8" height="78" rx="3" fill="#c4b5fd" stroke="#c4b5fd" stroke-width="0" /><text x="917.5" y="254.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">VLAN 30 — Serveurs</text><text x="917.5" y="276.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">192.168.30.0/24</text><line x1="500" y1="150" x2="188" y2="220" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="150" x2="550" y2="220" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="600" y1="150" x2="918" y2="220" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="75" y1="325" x2="300" y2="325" stroke="#4ade80" stroke-width="2" stroke-linecap="round" stroke-dasharray="8 7" /><text x="188" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#4ade80" text-anchor="middle">Domaine L2 isolé</text><line x1="438" y1="325" x2="667" y2="325" stroke="#fb7185" stroke-width="2" stroke-linecap="round" stroke-dasharray="8 7" /><text x="550" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#fb7185" text-anchor="middle">Domaine L2 isolé</text><line x1="803" y1="325" x2="1030" y2="325" stroke="#c4b5fd" stroke-width="2" stroke-linecap="round" stroke-dasharray="8 7" /><text x="918" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#c4b5fd" text-anchor="middle">Domaine L2 isolé</text><text x="550" y="410" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">La communication entre VLANs exige du routage L3 et des règles adaptées.</text></svg>

Cette répétition du diagramme VLAN sert à associer le plan logique au laboratoire. Dans le vrai dossier d’architecture, ajoute les liens physiques, les ports, les équipements et les interfaces de passerelle.

### Exemple de configuration de commutateur Cisco

Les commandes suivantes illustrent la création de VLAN et l’affectation de ports d’accès. Elles ne constituent pas un modèle universel de production : la syntaxe, les mécanismes de sécurité et la configuration du trunk doivent être vérifiés pour la plateforme utilisée.

```text
configure terminal
vlan 10
 name USERS
vlan 20
 name GUESTS
vlan 30
 name SERVERS
vlan 40
 name VOICE
vlan 99
 name MGMT
!
interface GigabitEthernet1/0/1
 description PC-Employe-01
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
interface GigabitEthernet1/0/24
 description Uplink-vers-distribution
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,99
end
```

**Notes d’exploitation :**
- Le nom `GigabitEthernet1/0/24` dépend du matériel. Adapte-le aux ports réels.
- La commande `spanning-tree portfast` est réservée aux ports de terminaux conformément aux règles de la plateforme ; ne l’applique pas aveuglément aux trunks reliant des commutateurs.
- Selon le système, le format des VLAN autorisés, les options de trunk natif et les mécanismes de protection peuvent différer.
- Avant l’application, sauvegarde la configuration et vérifie le plan de retour arrière.

### Exemple simplifié de passerelles sur un commutateur L3

Dans une plateforme qui prend en charge le routage IP, des interfaces VLAN (SVI) peuvent servir de passerelles. L’extrait est pédagogique ; les paramètres de disponibilité, de sécurité, de relais DHCP et de routage doivent être ajoutés suivant le projet.

```text
configure terminal
ip routing
interface Vlan10
 description Passerelle-Employes
 ip address 192.168.10.1 255.255.255.0
 no shutdown
interface Vlan20
 description Passerelle-Invites
 ip address 192.168.20.1 255.255.255.0
 no shutdown
interface Vlan30
 description Passerelle-Serveurs
 ip address 192.168.30.1 255.255.255.0
 no shutdown
end
```

Le routage entre VLAN est alors possible au niveau L3 si les interfaces, routes et politiques le permettent. **La segmentation seule n’interdit pas** aux clients de joindre les autres sous-réseaux. Ajoute et teste les contrôles attendus, particulièrement entre invités, utilisateurs, serveurs et gestion. Ne déploie pas ces seules lignes comme configuration de sécurité complète.

### Tests d’acceptation

1. Un poste du VLAN 10 reçoit les paramètres DHCP appropriés.
2. Il joint sa passerelle et les services autorisés.
3. Un invité reçoit une adresse du VLAN 20 et obtient l’accès Internet prévu.
4. Un invité ne joint pas les serveurs internes, ni les interfaces d’administration.
5. Les services de téléphonie et Wi-Fi fonctionnent conformément au plan.
6. Les journaux et les alertes de perte d’un lien sont visibles.
7. La perte d’un uplink est testée selon une procédure de maintenance approuvée.
8. Les schémas, les ports et les configurations de référence sont mis à jour.

## 19. Méthode de dépannage par couches

Quand une application ne fonctionne pas, ne change pas plusieurs éléments au hasard. Pars d’un symptôme reproductible, limite le périmètre, puis vérifie les dépendances de la couche physique à la couche applicative. Un poste peut être connecté au switch mais être dans le mauvais VLAN ; il peut avoir une adresse IP mais une passerelle erronée ; le routage peut fonctionner mais le DNS échouer ; la connectivité peut être bonne mais une ACL bloquer un port applicatif.

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="455" viewBox="0 0 1100 455"><rect x="1" y="1" width="1098" height="453" rx="22" fill="#0f172a" stroke="#334155" stroke-width="2" /><text x="550.0" y="38" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="bold" fill="#f8fafc" text-anchor="middle">Méthode de dépannage par couches</text><rect x="365" y="70" width="370" height="60" rx="14" fill="#172b43" stroke="#22d3ee" stroke-width="2" /><rect x="365" y="70" width="8" height="60" rx="3" fill="#22d3ee" stroke="#22d3ee" stroke-width="0" /><text x="550.0" y="95.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">1. Définir le symptôme</text><text x="550.0" y="117.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">qui, où, depuis quand ?</text><rect x="60" y="200" width="260" height="72" rx="14" fill="#132238" stroke="#4ade80" stroke-width="2" /><rect x="60" y="200" width="8" height="72" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="0" /><text x="190.0" y="231.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">2. Physique / L2</text><text x="190.0" y="253.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">lien, VLAN, négociation</text><rect x="420" y="200" width="260" height="72" rx="14" fill="#132238" stroke="#fbbf24" stroke-width="2" /><rect x="420" y="200" width="8" height="72" rx="3" fill="#fbbf24" stroke="#fbbf24" stroke-width="0" /><text x="550.0" y="231.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">3. IP / passerelle</text><text x="550.0" y="253.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">adresse, masque, ARP</text><rect x="780" y="200" width="260" height="72" rx="14" fill="#132238" stroke="#fb923c" stroke-width="2" /><rect x="780" y="200" width="8" height="72" rx="3" fill="#fb923c" stroke="#fb923c" stroke-width="0" /><text x="910.0" y="231.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#f8fafc" text-anchor="middle">4. Routage / services</text><text x="910.0" y="253.0" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="normal" fill="#f8fafc" text-anchor="middle">route, DNS, DHCP, ACL</text><line x1="550" y1="130" x2="190" y2="200" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="130" x2="550" y2="200" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="130" x2="910" y2="200" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" /><rect x="250" y="330" width="600" height="62" rx="14" fill="#252442" stroke="#c4b5fd" stroke-width="2" /><rect x="250" y="330" width="8" height="62" rx="3" fill="#c4b5fd" stroke="#c4b5fd" stroke-width="0" /><text x="550.0" y="356.0" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="bold" fill="#f8fafc" text-anchor="middle">5. Tester chaque saut et comparer au fonctionnement normal</text><text x="550.0" y="378.0" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#f8fafc" text-anchor="middle">modifier une seule variable à la fois</text><line x1="190" y1="272" x2="330" y2="330" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="330" y1="330" x2="319.1357032033219" y2="331.7225141838863" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="330" y1="330" x2="323.5368797925208" y2="321.0989844858199" stroke="#4ade80" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="272" x2="550" y2="330" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="330" x2="544.2504404817628" y2="320.62223025734545" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="550" y1="330" x2="555.7495595182372" y2="320.62223025734545" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" /><line x1="910" y1="272" x2="770" y2="330" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="770" y1="330" x2="776.4631202074792" y2="321.0989844858199" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><line x1="770" y1="330" x2="780.8642967966781" y2="331.7225141838863" stroke="#fb923c" stroke-width="3" stroke-linecap="round" /><text x="550" y="428" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="normal" fill="#f8fafc" text-anchor="middle">Collecter des preuves : horodatage, commandes, compteurs et résultats.</text></svg>

### Ordre de vérification suggéré

1. **Physique :** alimentation, lien, câble, fibre, état du port et erreurs.
2. **Couche 2 :** VLAN correct, port access/trunk, table MAC, absence de boucle.
3. **IP locale :** adresse, préfixe/masque, route locale, résolution ARP ou voisinage IPv6.
4. **Passerelle et routage :** passerelle joignable, routes aller/retour, prochaine étape, tables de routage.
5. **Services :** DHCP, DNS, NTP, identité et disponibilité serveur.
6. **Sécurité :** ACL, règles de pare-feu, politique VPN, logs de refus.
7. **Application :** port et protocole réellement utilisés, état du serveur, certificats et paramètres du client.

Collecte les preuves avant de corriger : heure, poste concerné, destination, captures utiles, compteurs, commandes, différence entre un poste qui fonctionne et un autre en panne. Change une seule variable à la fois quand le contexte le permet. Après la résolution, explique la cause racine et la prévention, au lieu de s’arrêter à « ça remarche ».

## 20. Quiz de révision

### Questions

1. Quelle différence existe entre topologie physique et topologie logique ?
2. Quel rôle joue généralement la couche d’accès ?
3. Pourquoi une petite entreprise peut-elle utiliser une architecture à deux couches ?
4. Un VLAN fournit-il à lui seul une politique de sécurité complète ? Explique.
5. Quel est le rôle de la passerelle par défaut ?
6. Quelles plages IPv4 privées sont réservées par RFC 1918 ?
7. À quoi sert DHCP ? Et DNS ?
8. Pourquoi les liens redondants de couche 2 nécessitent-ils une conception spécifique ?
9. Que fait le NAT, et pourquoi ne faut-il pas le confondre avec un pare-feu ?
10. Pourquoi un test de bascule est-il préférable à une simple inspection du schéma ?
11. Un poste joint une adresse IP par ping mais n’ouvre pas le site par son nom. Quels éléments vérifies-tu ?
12. Quelles informations minimales conserves-tu dans un plan réseau ?
13. Pourquoi la synchronisation NTP est-elle utile au dépannage ?
14. Quelle est la différence entre latence et débit ?
15. Pourquoi un réseau invité doit-il être séparé du réseau de gestion ?

### Corrigé

1. La topologie physique décrit les câbles, ports et emplacements ; la topologie logique décrit les VLAN, sous-réseaux, routes et flux.
2. Elle connecte les terminaux au réseau et applique plusieurs fonctions de bord selon la conception.
3. Pour réduire coût et complexité lorsque la taille, les flux et les exigences de résilience le permettent ; distribution et cœur sont alors regroupés logiquement.
4. Non. Le VLAN sépare surtout les domaines de couche 2. Le routage peut autoriser la communication entre VLAN ; il faut des règles de contrôle adaptées.
5. Elle reçoit les paquets destinés à des réseaux que le poste ne considère pas locaux et les transmet vers le réseau routé.
6. `10.0.0.0/8`, `172.16.0.0/12` et `192.168.0.0/16`.
7. DHCP distribue les paramètres réseau automatiquement ; DNS traduit notamment les noms en adresses et fournit d’autres données de nommage.
8. Parce que des chemins parallèles de couche 2 peuvent créer des boucles. Un mécanisme anti-boucle ou une conception L3 appropriée est nécessaire.
9. NAT modifie des adresses et éventuellement des ports. Il ne définit pas à lui seul les autorisations et interdictions comme le ferait une politique de filtrage.
10. Un test mesure la détection, la récupération et l’effet réel sur les utilisateurs, y compris les erreurs qui ne sont pas visibles sur le dessin.
11. DNS, cache/résolveur, configuration du nom, reachability du serveur DNS, politique de filtrage UDP/TCP 53 et état du service.
12. Topologies physique/logique, VLAN et préfixes, passerelles, ports/câbles, équipements, services, routes et règles de flux importantes, contacts et procédures de restauration.
13. Des horloges cohérentes permettent d’ordonner correctement les événements issus d’équipements différents.
14. La latence est un délai ; le débit est une quantité de données transportée par unité de temps.
15. Pour empêcher qu’un client peu fiable accède aux interfaces d’administration et aux ressources internes sensibles.

## 21. Checklist de conception et de mise en service

### Besoins et conception

- [ ] Les utilisateurs, applications, volumes et contraintes sont recensés.
- [ ] Le modèle d’architecture est adapté à la taille et à la criticité.
- [ ] Les rôles de l’accès, de la distribution et du cœur sont documentés.
- [ ] Les VLAN, sous-réseaux, passerelles et routes sont planifiés.
- [ ] Les flux nécessaires entre zones sont décrits.
- [ ] Les chemins WAN, accès Internet et services cloud sont identifiés.

### Physique et capacité

- [ ] Le cuivre, la fibre, les modules optiques et les distances sont compatibles.
- [ ] Les ports, uplinks et budgets PoE disposent d’une marge adaptée.
- [ ] La baie, l’alimentation, le refroidissement et l’étiquetage sont prévus.
- [ ] Les liens redondants sont gérés par une conception L2/L3 adaptée.

### Sécurité et opérations

- [ ] L’administration est limitée et documentée.
- [ ] Les invités, serveurs et systèmes de gestion sont isolés selon la politique.
- [ ] Les services DHCP, DNS, NTP et AAA ont un plan de disponibilité.
- [ ] Les sauvegardes de configuration et secrets sont protégés.
- [ ] La supervision, les alertes et les journaux sont configurés.
- [ ] Les critères de tests et le retour arrière sont définis.
- [ ] La documentation reflète l’état réellement mis en service.

## 22. Glossaire essentiel

| Terme | Définition courte |
|---|---|
| ACL | Liste de contrôle d’accès appliquant des critères d’autorisation/refus |
| AP | Point d’accès Wi-Fi |
| Broadcast | Diffusion vers les équipements d’un même domaine de broadcast |
| Core / cœur | Couche de transport entre blocs d’un réseau de campus |
| DHCP | Attribution automatique de paramètres réseau |
| DNS | Système de nommage et résolution |
| DMZ | Zone intermédiaire pour certains services exposés ou semi-exposés |
| FIB | Structure utilisée pour transférer les paquets selon les décisions de routage installées |
| LAN | Réseau local |
| L2 / L3 | Couche liaison de données / couche réseau dans le modèle de référence |
| NAT/PAT | Traduction d’adresses / traduction avec ports pour multiplexage de flux |
| NTP | Synchronisation de l’heure |
| PoE | Alimentation électrique via Ethernet |
| QoS | Gestion différenciée du trafic selon une politique de service |
| Route par défaut | Route utilisée lorsqu’aucune route plus spécifique ne correspond |
| SVI | Interface logique associée à un VLAN sur une plateforme qui la prend en charge |
| Trunk | Liaison transportant plusieurs VLANs via un mécanisme de marquage |
| VLAN | Domaine logique de couche 2 |
| WAN | Réseau reliant des sites éloignés |

## 23. Pour aller plus loin

Après ce niveau, la suite logique est d’approfondir le switching et les VLAN, le routage inter-VLAN, le subnetting IPv4/IPv6, STP/RSTP, les protocoles de routage comme OSPF, les mécanismes de haute disponibilité, les VPN, les politiques de pare-feu et la supervision. Les cours avancés devront s’appuyer sur cette base pour éviter de répéter les définitions et développer la configuration, les scénarios de panne et les choix de conception.

### Références utiles

- Cisco, *Campus LAN and Wireless LAN Solution Design Guide* : https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-campus-lan-wlan-design-guide.html — modèle hiérarchique, modularité et principes de conception campus.
- IETF, RFC 1918, *Address Allocation for Private Internets* : https://www.rfc-editor.org/rfc/rfc1918 — plages IPv4 privées.
- IETF, RFC 4193, *Unique Local IPv6 Unicast Addresses* : https://www.rfc-editor.org/rfc/rfc4193 — format et usage des adresses IPv6 locales uniques.
- Cisco, *Cloud Campus LAN Design Guide* (version présentée comme mise à jour le 27 août 2024) : https://www.cisco.com/c/en/us/solutions/collateral/enterprise/design-zone-campus/cloud-campus-lan-design-guide.html — recommandations de conception campus contemporaines propres à l’écosystème Cisco.

> **Règle finale :** une architecture réseau réussie n’est pas celle qui comporte le plus d’équipements ou de technologies. C’est celle dont les fonctions, les chemins, les risques, les comportements en cas de panne et les responsabilités sont compris, testés et documentés.
