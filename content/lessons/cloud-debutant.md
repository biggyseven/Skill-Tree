<style>
.cloud-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.2rem 0;padding:0.7rem;border:1px solid #183653;border-radius:14px;background:#07111f;color:#e5edf8;box-sizing:border-box}
.cloud-diagram svg{display:block;width:100%;height:auto;min-width:620px}
@media(max-width:680px){.cloud-diagram svg{min-width:680px}}
@media(prefers-reduced-motion:reduce){.cloud-diagram *{animation:none!important}}
</style>

# Cloud Networking — Niveau Débutant

**Niveau :** Débutant  
**Parcours :** Réseaux et infrastructure cloud  
**Objectif :** comprendre comment les ressources hébergées chez un fournisseur cloud communiquent entre elles, avec Internet et avec un réseau local.

Le cloud networking désigne l’ensemble des réseaux, services et règles qui permettent de relier des machines virtuelles, des applications, des bases de données, des utilisateurs et des sites distants dans une infrastructure cloud. Les idées fondamentales restent celles des réseaux classiques — adresses IP, sous-réseaux, routage, DNS, ports et filtrage — mais une partie de l’infrastructure est créée et administrée par logiciel.

Ce cours présente les concepts communs aux grands fournisseurs cloud. Les noms exacts varient : AWS utilise notamment les VPC, Azure les Virtual Networks (VNet) et Google Cloud les VPC networks. Les principes sont proches, mais les détails de configuration, les comportements par défaut et les tarifs ne sont pas identiques.

> **Analogie :** imagine un campus avec plusieurs bâtiments. Le réseau virtuel est le campus, les sous-réseaux sont des zones ou des bâtiments, les adresses IP sont les numéros des locaux, les routes sont les indications de circulation et les règles de sécurité sont les contrôles aux portes. Le fournisseur cloud fournit les routes et les infrastructures physiques, tandis que tu définis une grande partie de l’organisation logique.


## 1. Qu’est-ce que le cloud networking ?

Une application cloud est rarement un seul ordinateur. Elle peut comporter :
- une interface web accessible par les clients ;
- un serveur applicatif qui traite les demandes ;
- une base de données qui conserve les informations ;
- des services de stockage, de journalisation ou de supervision ;
- des mécanismes de sauvegarde et de reprise.

Ces composants doivent échanger des données. Le cloud networking fournit les chemins, l’adressage et les contrôles nécessaires à ces échanges.

### 1.1 Réseau traditionnel et réseau cloud

Dans un réseau traditionnel, une organisation peut acheter des commutateurs, des routeurs, des pare-feu et des câbles, puis les configurer. Dans le cloud, le fournisseur possède le matériel physique. Le client crée des réseaux logiques à travers une console, une API, des modèles d’infrastructure ou une interface en ligne de commande.

Cela ne signifie pas que le réseau devient magique ou qu’il n’existe plus de matériel. Les paquets circulent toujours sur des équipements physiques. Le cloud masque une partie de cette complexité et automatise la création des ressources.

| Réseau traditionnel | Réseau cloud |
|---|---|
| Routeurs et commutateurs physiques gérés par l’organisation | Infrastructure physique gérée principalement par le fournisseur |
| VLAN configurés sur les commutateurs | Réseaux virtuels et sous-réseaux définis par logiciel |
| Pare-feu matériel ou logiciel | Groupes de sécurité, ACL réseau et pare-feu managés |
| Achat et installation d’équipements | Création de ressources à la demande |
| Capacité liée au matériel installé | Capacité ajustable, dans les limites et quotas du fournisseur |
| Gestion locale et distante | Gestion par console, API, CLI ou Infrastructure as Code |

La responsabilité n’est pas entièrement transférée au fournisseur. Celui-ci sécurise l’infrastructure physique et certains services sous-jacents ; le client reste responsable de ses choix d’architecture, de ses règles réseau, des identités, des systèmes invités et des données selon le service utilisé.

### 1.2 IaaS, PaaS et SaaS : qui gère le réseau ?

- **IaaS (Infrastructure as a Service)** : tu disposes de ressources telles que des machines virtuelles et des réseaux virtuels. Tu gères généralement le système invité, les applications et une partie importante de la configuration réseau.
- **PaaS (Platform as a Service)** : le fournisseur gère davantage de composants, comme le système d’exploitation de la plateforme. Tu contrôles les paramètres réseau exposés par le service.
- **SaaS (Software as a Service)** : tu utilises une application prête à l’emploi. Tu contrôles surtout les comptes, les accès, les appareils et la connectivité de tes utilisateurs.

Le niveau de contrôle dépend du service exact. Deux services appartenant à la même catégorie peuvent offrir des options très différentes.

## 2. Les composants essentiels

### 2.1 Région et zone de disponibilité

Une **région** est une zone géographique dans laquelle un fournisseur propose des services cloud. Une **zone de disponibilité** est un domaine d’infrastructure distinct au sein d’une région, conçu pour limiter l’impact de certaines pannes. Le nom et l’organisation exacte des régions et zones dépendent du fournisseur.

Répartir des ressources entre plusieurs zones peut améliorer la disponibilité, mais cela ne suffit pas à garantir une application résiliente. Il faut aussi prévoir la réplication des données, les mécanismes de bascule, la supervision, les sauvegardes et des tests de reprise.

### 2.2 Réseau virtuel : VPC ou VNet

Un réseau virtuel est un espace réseau isolé logiquement dans le cloud. Il permet de définir un plan d’adressage, des sous-réseaux et des chemins de communication.

Selon le fournisseur, on peut rencontrer les termes :
- **VPC** : Virtual Private Cloud ;
- **VNet** : Virtual Network ;
- **VPC network** : nom utilisé par Google Cloud pour son réseau virtuel.

Ne confonds pas le réseau virtuel avec un VPN. Le réseau virtuel est le réseau logique hébergeant les ressources ; un VPN est une technologie qui chiffre et transporte du trafic entre des points, par exemple entre un ordinateur et le cloud.

### 2.3 Sous-réseau

Un sous-réseau est une plage d’adresses IP associée à une partie d’un réseau. Il permet de structurer l’adressage, de séparer les ressources et d’appliquer des règles différentes.

Exemple pédagogique pour un réseau IPv4 `10.20.0.0/16` :

| Sous-réseau | CIDR | Exemple d’usage |
|---|---|---|
| Public | `10.20.1.0/24` | Point d’entrée web ou répartiteur de charge |
| Privé applicatif | `10.20.2.0/24` | Serveurs applicatifs |
| Privé données | `10.20.3.0/24` | Base de données |
| Administration | `10.20.10.0/24` | Accès d’administration contrôlé |

Ces plages sont des exemples privés, pas une architecture universelle. Il faut choisir un plan d’adressage qui ne chevauche pas les réseaux déjà utilisés par l’entreprise, ses partenaires ou les sites distants.

### 2.4 Adresse IP et CIDR

Une adresse IPv4 est composée de 32 bits. La notation CIDR associe une adresse à un préfixe, par exemple `10.20.1.0/24`. Le `/24` signifie que les 24 premiers bits constituent la partie réseau ; les bits restants sont disponibles pour les adresses de cette plage.

Un sous-réseau IPv4 `/24` contient 256 valeurs d’adresses. Dans les réseaux classiques, deux adresses sont habituellement réservées à l’identifiant du réseau et à la diffusion. Les plateformes cloud peuvent également réserver certaines adresses pour leurs propres fonctions. Vérifie donc la capacité réellement utilisable dans la documentation du fournisseur.

Quelques tailles usuelles :
- `/16` : 65 536 adresses au total ;
- `/24` : 256 adresses au total ;
- `/26` : 64 adresses au total ;
- `/28` : 16 adresses au total.

Le nombre d’adresses utilisables ne doit pas être calculé sans tenir compte des réservations de la plateforme.

### 2.5 Routeur et table de routage

Un routeur choisit où envoyer les paquets selon leur destination. Dans le cloud, les tables de routage définissent généralement les destinations et les cibles, par exemple un réseau local, une passerelle Internet, une passerelle NAT ou une connexion privée.

Une route peut se lire comme une instruction :

> Pour joindre la destination `10.30.0.0/16`, envoie le trafic vers la connexion réseau privée prévue à cet effet.

Les routes les plus spécifiques sont généralement préférées aux routes moins spécifiques. La façon dont le fournisseur applique les routes et sélectionne les cibles doit être vérifiée dans sa documentation.

### Schéma 1 — Architecture cloud et sens des communications

<div class="cloud-diagram">
<svg viewBox="0 0 920 470" width="100%" role="img" aria-label="Architecture cloud avec flèches indiquant le sens des communications" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="c1arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8"/></marker><marker id="c1green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker><style>.c1t{font:14px Arial,sans-serif;fill:#e5edf8}.c1s{font:12px Arial,sans-serif;fill:#a9bdd5}.c1line{stroke:#38bdf8;stroke-width:3;fill:none;marker-end:url(#c1arrow)}.c1data{stroke:#34d399;stroke-width:3;fill:none;marker-end:url(#c1green);stroke-dasharray:9 7;animation:c1dash 1.8s linear infinite}@keyframes c1dash{to{stroke-dashoffset:-32}}.c1box{fill:#101e30;stroke:#38bdf8;stroke-width:1.6}.c1greenbox{fill:#0d2a27;stroke:#34d399;stroke-width:1.6}</style></defs>
<rect x="15" y="20" width="150" height="82" rx="12" class="c1box"/><text x="90" y="49" text-anchor="middle" class="c1t" font-weight="bold">Clients</text><text x="90" y="72" text-anchor="middle" class="c1s">Navigateur / mobile</text>
<rect x="220" y="20" width="145" height="82" rx="12" class="c1box"/><text x="292" y="49" text-anchor="middle" class="c1t" font-weight="bold">Internet</text><text x="292" y="72" text-anchor="middle" class="c1s">DNS / HTTPS</text>
<path d="M165 61 H215" class="c1data"/><path d="M220 83 H170" class="c1line"/>
<rect x="405" y="15" width="495" height="435" rx="20" fill="#0a1625" stroke="#60a5fa" stroke-width="2" stroke-dasharray="8 5"/><text x="652" y="43" text-anchor="middle" class="c1t" font-weight="bold">Réseau virtuel cloud (VPC / VNet)</text>
<rect x="430" y="65" width="220" height="100" rx="12" class="c1box"/><text x="540" y="91" text-anchor="middle" class="c1t" font-weight="bold">Sous-réseau public</text><text x="540" y="115" text-anchor="middle" class="c1s">Entrée web contrôlée</text><text x="540" y="138" text-anchor="middle" class="c1s">Load balancer / proxy</text>
<rect x="685" y="65" width="190" height="100" rx="12" class="c1greenbox"/><text x="780" y="91" text-anchor="middle" class="c1t" font-weight="bold">Sous-réseau privé</text><text x="780" y="115" text-anchor="middle" class="c1s">Application</text><text x="780" y="138" text-anchor="middle" class="c1s">Accès filtré</text>
<rect x="685" y="220" width="190" height="100" rx="12" class="c1greenbox"/><text x="780" y="246" text-anchor="middle" class="c1t" font-weight="bold">Données privées</text><text x="780" y="270" text-anchor="middle" class="c1s">Base de données</text><text x="780" y="293" text-anchor="middle" class="c1s">Pas d’entrée Internet directe</text>
<rect x="430" y="220" width="220" height="100" rx="12" class="c1box"/><text x="540" y="246" text-anchor="middle" class="c1t" font-weight="bold">Passerelle NAT</text><text x="540" y="270" text-anchor="middle" class="c1s">Sortie vers Internet</text><text x="540" y="293" text-anchor="middle" class="c1s">Pas une entrée publique</text>
<path d="M365 61 H425" class="c1data"/><path d="M650 115 H680" class="c1data"/><path d="M780 165 V215" class="c1data"/><path d="M430 270 H390 V350 H365" class="c1line"/>
<rect x="220" y="320" width="145" height="70" rx="12" class="c1box"/><text x="292" y="348" text-anchor="middle" class="c1t" font-weight="bold">Internet sortant</text><text x="292" y="370" text-anchor="middle" class="c1s">Mises à jour</text>
<text x="30" y="440" class="c1s">Les flèches montrent une direction logique d’exemple ; les règles réelles déterminent le trafic autorisé.</text>
</svg>
</div>

Le diagramme montre un modèle fréquent : le client atteint une entrée web publique ; celle-ci communique avec l’application ; l’application accède à la base de données privée. Une passerelle NAT peut permettre aux ressources privées d’initier des connexions vers Internet, par exemple pour télécharger des mises à jour. Les flux précis dépendent de l’architecture et des règles de sécurité.

## 3. Internet, adresses publiques et privées

### 3.1 Adresses privées

Les plages IPv4 privées courantes sont :
- `10.0.0.0/8` ;
- `172.16.0.0/12` ;
- `192.168.0.0/16`.

Elles sont utilisées dans les réseaux internes et ne sont pas routées directement sur l’Internet public. Une adresse privée peut néanmoins être utilisée dans un réseau cloud et communiquer avec d’autres réseaux via des routes privées, un VPN ou une interconnexion dédiée.

### 3.2 Adresse publique

Une adresse IP publique est routable sur Internet, sous réserve des règles et du service utilisé. Dans le cloud, attribuer une adresse publique à une ressource ne signifie pas automatiquement qu’elle est accessible : une route appropriée, des règles de sécurité, un service à l’écoute et les politiques du fournisseur doivent aussi permettre le flux.

Inversement, une ressource sans adresse publique peut être accessible par l’intermédiaire d’un répartiteur de charge, d’un proxy, d’un VPN ou d’un service privé. L’exposition publique et l’accessibilité sont deux notions distinctes.

### 3.3 Passerelle Internet

Une passerelle Internet relie un réseau virtuel à Internet. Elle ne remplace pas toutes les autres conditions de connectivité. Pour qu’une ressource soit joignable depuis Internet, il faut généralement :
1. une adresse ou un point d’entrée public approprié ;
2. une route vers la passerelle Internet ;
3. des règles réseau et pare-feu autorisant le trafic ;
4. un service actif sur le bon port ;
5. un nom DNS configuré si l’utilisateur utilise un nom de domaine.

Le fonctionnement exact varie selon le fournisseur. Certaines plateformes associent la connectivité publique aux ressources ou aux sous-réseaux d’une manière différente.

### 3.4 NAT : traduction d’adresses

Le NAT (Network Address Translation) traduit des adresses IP et parfois des ports. Une passerelle NAT cloud permet souvent à des machines privées d’établir des connexions sortantes vers Internet sans leur attribuer à chacune une adresse publique directement joignable.

Le modèle habituel est **sortant** : une machine privée initie une connexion, et les réponses liées à cette connexion peuvent revenir. Une passerelle NAT n’est pas, à elle seule, un mécanisme destiné à publier un serveur privé pour des connexions entrantes arbitraires.

Il faut aussi tenir compte des coûts, des limites de connexions, de la haute disponibilité et de la journalisation du service NAT utilisé.

## 4. Routage : suivre le chemin des paquets

### 4.1 Une table de routage simple

Une table de routage peut contenir des destinations telles que :
- le réseau local du VPC ;
- `0.0.0.0/0`, qui représente toutes les destinations IPv4 non couvertes par une route plus spécifique ;
- un réseau distant joint par VPN ;
- un point de sortie Internet ou une passerelle NAT.

Exemple conceptuel :

| Destination | Cible | Interprétation |
|---|---|---|
| `10.20.0.0/16` | Réseau local | Trafic destiné aux ressources du VPC |
| `0.0.0.0/0` | Passerelle NAT | Sortie IPv4 pour les ressources privées |
| `10.50.0.0/16` | Connexion VPN | Trafic vers le réseau d’entreprise |

Cette table n’est pas une configuration universelle. Dans certains environnements, la route par défaut d’un sous-réseau public cible une passerelle Internet, tandis que celle d’un sous-réseau privé cible une passerelle NAT. Les routes IPv6 et les routes propagées par des connexions privées peuvent exiger des entrées supplémentaires.

### 4.2 Comment lire une route

Pour comprendre une route, pose trois questions :
1. **Quelle destination ?** Le préfixe de destination indique les adresses visées.
2. **Quelle cible ?** La cible précise où le paquet est envoyé.
3. **Quelle table s’applique ?** La ressource ou le sous-réseau utilise une table de routage particulière.

Une route incorrecte peut produire une panne même si l’adresse IP et les règles de pare-feu sont correctes. Le diagnostic doit donc examiner le chemin complet.

### Schéma 2 — Décision de routage avec flèches directionnelles

<div class="cloud-diagram">
<svg viewBox="0 0 900 310" width="100%" role="img" aria-label="Décision de routage, flèches directionnelles des paquets" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="c2a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8"/></marker><marker id="c2g" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker><style>.c2t{font:14px Arial,sans-serif;fill:#e5edf8}.c2s{font:12px Arial,sans-serif;fill:#a9bdd5}.c2f{stroke:#38bdf8;stroke-width:3;fill:none;marker-end:url(#c2a)}.c2g{stroke:#34d399;stroke-width:3;fill:none;marker-end:url(#c2g);stroke-dasharray:8 6;animation:c2dash 1.5s linear infinite}@keyframes c2dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="100" width="145" height="75" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="92" y="128" text-anchor="middle" class="c2t" font-weight="bold">Machine source</text><text x="92" y="151" text-anchor="middle" class="c2s">10.20.2.15</text>
<path d="M165 138 H220" class="c2g"/>
<path d="M220 138 L265 138" class="c2f"/>
<polygon points="315,80 370,138 315,196 260,138" fill="#192a43" stroke="#a78bfa" stroke-width="2"/><text x="315" y="133" text-anchor="middle" class="c2t" font-weight="bold">Table de</text><text x="315" y="151" text-anchor="middle" class="c2t" font-weight="bold">routage</text>
<path d="M370 138 H430 V55 H490" class="c2g"/><path d="M370 138 H430 V138 H490" class="c2f"/><path d="M370 138 H430 V225 H490" class="c2f"/>
<rect x="490" y="25" width="180" height="60" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="580" y="49" text-anchor="middle" class="c2t">Réseau distant privé</text><text x="580" y="69" text-anchor="middle" class="c2s">Route VPN spécifique</text>
<rect x="490" y="108" width="180" height="60" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="580" y="132" text-anchor="middle" class="c2t">Ressource locale</text><text x="580" y="152" text-anchor="middle" class="c2s">Route VPC locale</text>
<rect x="490" y="195" width="180" height="60" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="580" y="219" text-anchor="middle" class="c2t">Sortie Internet</text><text x="580" y="239" text-anchor="middle" class="c2s">Route par défaut</text>
<path d="M670 55 H730" class="c2f"/><path d="M670 138 H730" class="c2f"/><path d="M670 225 H730" class="c2f"/>
<text x="745" y="50" class="c2s">VPN / liaison privée</text><text x="745" y="133" class="c2s">Adresse du VPC</text><text x="745" y="220" class="c2s">NAT ou passerelle</text><text x="20" y="288" class="c2s">La route choisie dépend de la destination et des règles de priorité de la plateforme.</text>
</svg>
</div>

Les flèches indiquent le sens de transmission depuis la machine source vers la cible choisie. Les réponses utilisent à leur tour les routes et contrôles applicables dans le sens retour ; une route aller correcte ne garantit donc pas toujours un chemin retour fonctionnel.

## 5. DNS et noms de domaine

Le DNS (Domain Name System) permet de traduire un nom comme `app.exemple.com` en informations nécessaires à la connexion, notamment des adresses IP. Dans le cloud, le DNS peut être public, privé ou hybride.

- **Zone publique** : contient des enregistrements visibles via le système DNS public.
- **Zone privée** : fournit des noms résolus seulement depuis les réseaux associés ou les environnements configurés.
- **DNS hybride** : permet de résoudre certains noms depuis le cloud et le réseau d’entreprise, au moyen de redirecteurs, de résolveurs ou de liaisons adaptées.

Enregistrements courants :
- `A` : nom vers adresse IPv4 ;
- `AAAA` : nom vers adresse IPv6 ;
- `CNAME` : alias vers un autre nom DNS, avec des restrictions selon le contexte ;
- `MX` : serveurs de messagerie ;
- `TXT` : données textuelles utilisées notamment pour certaines validations et politiques.

Un problème DNS peut ressembler à une panne réseau. Si une connexion échoue par nom mais fonctionne par adresse IP, le DNS mérite d’être examiné. Toutefois, tester directement une IP n’est pas toujours équivalent à accéder à un service HTTPS : le certificat, l’en-tête Host et le routage applicatif peuvent dépendre du nom.

## 6. Sécurité réseau dans le cloud

### 6.1 Principe du moindre privilège

N’autorise que les flux nécessaires, depuis les sources nécessaires, vers les destinations et ports nécessaires. Une règle large comme « autoriser tout le trafic depuis Internet » peut exposer involontairement des services d’administration ou des bases de données.

La sécurité ne doit pas reposer sur une seule barrière. Combine, selon les besoins, segmentation, filtrage, authentification, chiffrement, journalisation et supervision.

### 6.2 Groupes de sécurité

Un groupe de sécurité est généralement un ensemble de règles appliquées à des interfaces réseau ou à des ressources. Beaucoup de fournisseurs utilisent des règles avec état : le trafic retour d’une connexion autorisée est accepté automatiquement. Ce comportement n’est pas universel pour tous les mécanismes de filtrage.

Exemple de politique pour une petite application :
- autoriser HTTPS (`TCP 443`) vers le point d’entrée public ;
- autoriser le trafic du point d’entrée vers les serveurs applicatifs sur le port exact utilisé ;
- autoriser les serveurs applicatifs à joindre la base de données sur son port ;
- interdire l’accès public direct à la base de données ;
- réserver l’administration à un VPN, à un bastion ou à un service d’accès contrôlé.

Les ports doivent correspondre aux services réels. Le port 443 est commun pour HTTPS et le port 22 pour SSH, mais ces numéros ne garantissent pas à eux seuls la sécurité.

### 6.3 ACL réseau

Une liste de contrôle d’accès réseau (Network ACL) applique des règles à un niveau de sous-réseau ou de frontière réseau selon le fournisseur. Elle peut être sans état : dans ce cas, le trafic aller et le trafic retour doivent être autorisés séparément. Les groupes de sécurité et les ACL ne sont donc pas forcément interchangeables.

### 6.4 Segmentation public/privé

« Public » et « privé » décrivent la connectivité et l’exposition prévues, pas simplement le nom du sous-réseau. Une ressource dite privée doit être protégée par les routes et les contrôles effectifs ; son nom ne constitue pas une mesure de sécurité.

Une architecture pédagogique à trois couches sépare :
1. **Entrée** : répartiteur de charge, proxy ou serveur web exposé de façon contrôlée ;
2. **Application** : logique métier, sans entrée Internet directe si elle n’est pas nécessaire ;
3. **Données** : base de données et stockage, accessibles uniquement depuis les composants autorisés.

### Schéma 3 — Flux autorisés entre couches

<div class="cloud-diagram">
<svg viewBox="0 0 900 300" width="100%" role="img" aria-label="Segmentation en trois couches avec flèches directionnelles autorisées" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="c3g" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker><marker id="c3r" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><style>.c3t{font:15px Arial,sans-serif;fill:#e5edf8}.c3s{font:12px Arial,sans-serif;fill:#a9bdd5}.c3ok{stroke:#34d399;stroke-width:3;fill:none;marker-end:url(#c3g);stroke-dasharray:8 6;animation:c3dash 1.7s linear infinite}.c3no{stroke:#fb7185;stroke-width:2.5;fill:none;marker-end:url(#c3r)}@keyframes c3dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="25" y="80" width="200" height="105" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/><text x="125" y="111" text-anchor="middle" class="c3t" font-weight="bold">Couche publique</text><text x="125" y="137" text-anchor="middle" class="c3s">HTTPS entrant</text><text x="125" y="158" text-anchor="middle" class="c3s">Point d’entrée filtré</text>
<rect x="350" y="80" width="200" height="105" rx="12" fill="#0d2a27" stroke="#34d399" stroke-width="1.7"/><text x="450" y="111" text-anchor="middle" class="c3t" font-weight="bold">Couche application</text><text x="450" y="137" text-anchor="middle" class="c3s">Port applicatif requis</text><text x="450" y="158" text-anchor="middle" class="c3s">Pas d’entrée publique</text>
<rect x="675" y="80" width="200" height="105" rx="12" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.7"/><text x="775" y="111" text-anchor="middle" class="c3t" font-weight="bold">Couche données</text><text x="775" y="137" text-anchor="middle" class="c3s">Port DB précis</text><text x="775" y="158" text-anchor="middle" class="c3s">Privée</text>
<path d="M225 112 H345" class="c3ok"/><text x="285" y="99" text-anchor="middle" class="c3s">Autorisé</text><path d="M550 112 H670" class="c3ok"/><text x="610" y="99" text-anchor="middle" class="c3s">Autorisé</text>
<path d="M775 190 V240 H125 V190" class="c3no"/><text x="450" y="263" text-anchor="middle" class="c3s">Pas de chemin public direct vers la base de données</text>
<text x="25" y="35" class="c3t">Le filtrage doit correspondre aux flux métier réellement nécessaires.</text>
</svg>
</div>

Le trait rouge symbolise une connexion directe à ne pas autoriser dans cette architecture. Il ne signifie pas que tout flux retour est bloqué : les réponses aux connexions autorisées doivent être traitées conformément au comportement du mécanisme de filtrage choisi.

## 7. VPN et connectivité hybride

Une architecture **hybride** relie des ressources cloud à un réseau d’entreprise ou à un centre de données local. Les raisons courantes incluent la migration progressive, l’accès à des applications internes et le maintien temporaire de systèmes existants.

### 7.1 VPN site à site

Un VPN site à site crée généralement un tunnel chiffré entre une passerelle du réseau local et une passerelle cloud. IPsec est fréquemment utilisé. Il faut configurer les deux extrémités, les plages réseau, les paramètres cryptographiques, les routes et la supervision.

Une connexion VPN peut être établie mais ne transporter aucun trafic utile si les routes ou les règles de sécurité sont incorrectes. Le chiffrement ne remplace pas le routage.

### 7.2 VPN utilisateur

Un VPN utilisateur connecte un poste individuel à un réseau privé. Il sert par exemple à administrer des ressources internes depuis un poste distant. Il faut gérer les identités, les droits, l’authentification forte, la mise à jour des clients et la révocation des accès.

### 7.3 Connexion privée dédiée

Certains fournisseurs proposent une liaison dédiée entre le réseau d’entreprise et leur infrastructure. Elle peut fournir une connectivité plus prévisible ou répondre à des besoins de conformité, mais elle exige une conception de capacité, de redondance et de routage. Une liaison dédiée n’implique pas automatiquement le chiffrement : ce point doit être étudié séparément.

### Schéma 4 — Réseau d’entreprise relié au cloud

<div class="cloud-diagram">
<svg viewBox="0 0 900 310" width="100%" role="img" aria-label="VPN site à site entre entreprise et cloud avec flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="c4g" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker><style>.c4t{font:15px Arial,sans-serif;fill:#e5edf8}.c4s{font:12px Arial,sans-serif;fill:#a9bdd5}.c4f{stroke:#34d399;stroke-width:3;fill:none;marker-end:url(#c4g);stroke-dasharray:9 7;animation:c4dash 1.8s linear infinite}@keyframes c4dash{to{stroke-dashoffset:-32}}</style></defs>
<rect x="25" y="70" width="240" height="150" rx="14" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/><text x="145" y="100" text-anchor="middle" class="c4t" font-weight="bold">Réseau d’entreprise</text><text x="145" y="129" text-anchor="middle" class="c4s">LAN 192.168.10.0/24</text><rect x="65" y="150" width="160" height="42" rx="8" fill="#172c45" stroke="#60a5fa"/><text x="145" y="176" text-anchor="middle" class="c4t">Passerelle VPN</text>
<rect x="635" y="70" width="240" height="150" rx="14" fill="#0d2a27" stroke="#34d399" stroke-width="1.7"/><text x="755" y="100" text-anchor="middle" class="c4t" font-weight="bold">Réseau cloud privé</text><text x="755" y="129" text-anchor="middle" class="c4s">10.20.0.0/16</text><rect x="675" y="150" width="160" height="42" rx="8" fill="#123a32" stroke="#34d399"/><text x="755" y="176" text-anchor="middle" class="c4t">Passerelle VPN</text>
<path d="M225 162 H335" class="c4f"/><path d="M675 181 H565" class="c4f"/><rect x="335" y="110" width="230" height="70" rx="12" fill="#211d3a" stroke="#a78bfa" stroke-width="1.6"/><text x="450" y="138" text-anchor="middle" class="c4t" font-weight="bold">Tunnel IPsec</text><text x="450" y="160" text-anchor="middle" class="c4s">Trafic chiffré</text>
<text x="450" y="245" text-anchor="middle" class="c4s">Flèches opposées : chaque extrémité peut initier des échanges autorisés.</text><text x="25" y="285" class="c4s">Vérifier les routes aller et retour, les plages non chevauchantes, les clés et l’état du tunnel.</text>
</svg>
</div>

Le dessin représente deux sens possibles de communication, pas une permission illimitée. Les routes et les règles de filtrage déterminent quels hôtes peuvent réellement communiquer.

## 8. Équilibrage de charge et disponibilité

Un répartiteur de charge (load balancer) distribue les connexions ou requêtes entre plusieurs cibles. Il peut améliorer la disponibilité, permettre une montée en charge et éviter d’exposer directement chaque serveur applicatif.

On rencontre notamment :
- **équilibrage de couche 4** : décision fondée sur les informations de transport, telles que TCP ou UDP et les ports ;
- **équilibrage de couche 7** : décision fondée sur les protocoles applicatifs comme HTTP/HTTPS, les noms d’hôte ou les chemins d’URL, selon les capacités du produit.

Un répartiteur de charge n’est pas automatiquement un pare-feu applicatif. Les contrôles d’accès, la protection contre les attaques et la configuration TLS doivent être étudiés séparément.

Les contrôles de santé vérifient que les cibles sont disponibles selon un test défini. Un serveur peut répondre au ping mais être incapable de traiter une requête applicative. Choisis des sondes de santé adaptées et évite de déclarer une cible saine si les fonctions essentielles sont en panne.

### Schéma 5 — Répartiteur de charge

<div class="cloud-diagram">
<svg viewBox="0 0 900 290" width="100%" role="img" aria-label="Répartiteur de charge distribuant les requêtes vers trois serveurs, avec flèches" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="c5a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8"/></marker><style>.c5t{font:14px Arial,sans-serif;fill:#e5edf8}.c5s{font:12px Arial,sans-serif;fill:#a9bdd5}.c5f{stroke:#38bdf8;stroke-width:3;fill:none;marker-end:url(#c5a);stroke-dasharray:8 6;animation:c5dash 1.6s linear infinite}@keyframes c5dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="30" y="95" width="150" height="70" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="105" y="123" text-anchor="middle" class="c5t" font-weight="bold">Clients</text><text x="105" y="145" text-anchor="middle" class="c5s">HTTPS</text>
<rect x="300" y="95" width="210" height="70" rx="12" fill="#211d3a" stroke="#a78bfa" stroke-width="1.7"/><text x="405" y="123" text-anchor="middle" class="c5t" font-weight="bold">Load balancer</text><text x="405" y="145" text-anchor="middle" class="c5s">Contrôles de santé</text>
<path d="M180 130 H295" class="c5f"/><path d="M510 130 H565 V50 H625" class="c5f"/><path d="M510 130 H625" class="c5f"/><path d="M510 130 H565 V210 H625" class="c5f"/>
<rect x="625" y="20" width="230" height="60" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="740" y="45" text-anchor="middle" class="c5t">Serveur A</text><text x="740" y="65" text-anchor="middle" class="c5s">Cible saine</text>
<rect x="625" y="100" width="230" height="60" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="740" y="125" text-anchor="middle" class="c5t">Serveur B</text><text x="740" y="145" text-anchor="middle" class="c5s">Cible saine</text>
<rect x="625" y="180" width="230" height="60" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="740" y="205" text-anchor="middle" class="c5t">Serveur C</text><text x="740" y="225" text-anchor="middle" class="c5s">Exemple : cible indisponible</text>
<text x="30" y="270" class="c5s">Les flèches représentent la distribution logique ; l’algorithme exact dépend du service choisi.</text>
</svg>
</div>

Les flèches partent du répartiteur vers les cibles. Le chemin retour peut être différent selon le type de répartiteur et le service ; ne suppose pas que tous les produits conservent la même symétrie réseau.

## 9. IPv6 dans le cloud

IPv6 utilise des adresses de 128 bits. Il fournit un espace d’adressage beaucoup plus vaste qu’IPv4 et peut fonctionner en parallèle avec IPv4 (dual stack) ou selon des architectures IPv6 spécifiques.

Quelques précautions :
- prévoir l’adressage IPv6 et les préfixes de sous-réseaux ;
- contrôler les routes IPv6, notamment la route par défaut ;
- examiner les règles de filtrage IPv6 séparément ;
- vérifier la résolution DNS `AAAA` ;
- ne pas supposer qu’une ressource protégée en IPv4 est automatiquement protégée en IPv6.

L’absence de NAT IPv4 classique ne signifie pas que le réseau IPv6 est public ou privé par définition. La portée de l’adresse, les routes et les règles de sécurité restent déterminantes. Les mécanismes exacts varient selon le fournisseur.

## 10. Supervision, journaux et dépannage

La supervision réseau aide à répondre à trois questions :
1. Le chemin réseau est-il disponible ?
2. Le trafic est-il autorisé et atteint-il la bonne ressource ?
3. Les performances sont-elles suffisantes ?

Les outils courants incluent les journaux de flux réseau, les métriques de passerelles et de répartiteurs de charge, les journaux DNS, les tests de connectivité et les journaux des systèmes invités. Les journaux de flux peuvent indiquer les métadonnées des communications acceptées ou rejetées, mais ne montrent pas nécessairement le contenu applicatif.

### 10.1 Méthode de dépannage en couches

Procède de façon ordonnée :
1. **Nom** : le DNS résout-il le nom attendu ?
2. **Adresse** : l’adresse IP et le préfixe sont-ils corrects ?
3. **Route** : une route aller existe-t-elle ?
4. **Filtrage** : les groupes de sécurité, ACL et pare-feu autorisent-ils le flux ?
5. **Port** : le service écoute-t-il sur le port attendu ?
6. **Application** : l’application répond-elle correctement ?
7. **Retour** : les réponses peuvent-elles revenir par un chemin autorisé ?
8. **Dépendances** : le service dépend-il d’un DNS privé, d’une API, d’un certificat ou d’une base de données ?

Ne commence pas par désactiver toutes les règles de sécurité. Réduis plutôt le problème avec des tests ciblés et des changements temporaires, limités et documentés.

### Schéma 6 — Arbre de diagnostic

<div class="cloud-diagram">
<svg viewBox="0 0 900 360" width="100%" role="img" aria-label="Arbre de diagnostic réseau avec flèches vers les étapes suivantes" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="c6a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8"/></marker><style>.c6t{font:13px Arial,sans-serif;fill:#e5edf8}.c6s{font:11px Arial,sans-serif;fill:#a9bdd5}.c6f{stroke:#38bdf8;stroke-width:2.5;fill:none;marker-end:url(#c6a);stroke-dasharray:7 5;animation:c6dash 1.5s linear infinite}@keyframes c6dash{to{stroke-dashoffset:-24}}</style></defs>
<rect x="290" y="15" width="320" height="52" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="450" y="37" text-anchor="middle" class="c6t" font-weight="bold">La connexion échoue</text><text x="450" y="54" text-anchor="middle" class="c6s">Commencer par le nom DNS</text>
<path d="M450 67 V95" class="c6f"/><rect x="300" y="95" width="300" height="52" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><text x="450" y="117" text-anchor="middle" class="c6t" font-weight="bold">Le nom résout-il correctement ?</text><text x="450" y="134" text-anchor="middle" class="c6s">Comparer le résultat attendu et obtenu</text>
<path d="M300 121 H170 V170" class="c6f"/><path d="M600 121 H730 V170" class="c6f"/><text x="185" y="112" class="c6s">Non</text><text x="690" y="112" class="c6s">Oui</text>
<rect x="45" y="170" width="250" height="52" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="170" y="192" text-anchor="middle" class="c6t">Corriger DNS</text><text x="170" y="209" text-anchor="middle" class="c6s">Zone, enregistrement, résolveur</text>
<rect x="605" y="170" width="250" height="52" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="730" y="192" text-anchor="middle" class="c6t">Tester route et filtrage</text><text x="730" y="209" text-anchor="middle" class="c6s">Aller et retour, port cible</text>
<path d="M730 222 V250" class="c6f"/><rect x="605" y="250" width="250" height="52" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="730" y="272" text-anchor="middle" class="c6t">Tester le service</text><text x="730" y="289" text-anchor="middle" class="c6s">Écoute, logs, santé applicative</text>
<text x="45" y="270" class="c6s">Conserver les preuves</text><text x="45" y="288" class="c6s">et changer une chose à la fois.</text><text x="290" y="340" class="c6s">Une connexion réussie exige un chemin valide, des règles compatibles et un service fonctionnel.</text>
</svg>
</div>

### 10.2 Tests utiles

Sur une machine Linux, selon les outils installés :
- `ip addr` : afficher les interfaces et adresses ;
- `ip route` : examiner la table de routage ;
- `getent hosts app.exemple.com` ou `nslookup app.exemple.com` : tester la résolution DNS ;
- `ping` : vérifier certaines formes de connectivité IP, si ICMP est autorisé ;
- `traceroute` ou `tracepath` : observer une partie du chemin, selon les réponses réseau disponibles ;
- `curl -I https://app.exemple.com` : tester une requête HTTP(S) ;
- `ss -lntup` : examiner les ports à l’écoute, selon les permissions.

Sur Windows, des outils tels que `ipconfig`, `route print`, `nslookup`, `Test-NetConnection` et `tracert` sont utiles. Le résultat de `ping` ne prouve pas à lui seul qu’un service TCP fonctionne : ICMP peut être bloqué alors que HTTPS est autorisé, ou l’inverse.

## 11. Coûts et limites à anticiper

Le réseau cloud n’est pas toujours facturé uniquement au nombre de ressources. Les coûts peuvent inclure :
- le transfert de données sortant vers Internet ;
- le trafic interzone ou interrégion ;
- les passerelles NAT ;
- les connexions dédiées ;
- les services de protection, de journalisation et de supervision ;
- les adresses IP publiques ou les services d’équilibrage de charge.

Les tarifs varient selon le fournisseur, la région et le service. Avant de déployer une architecture, vérifie la grille tarifaire actuelle et estime les volumes. Un chemin réseau plus complexe peut améliorer la sécurité ou la résilience, mais aussi accroître les coûts et les points de défaillance.

Les quotas et limites de ressources comptent également : nombre de réseaux, plages de sous-réseaux, routes, connexions, interfaces, adresses ou passerelles. Une architecture viable à petite échelle peut rencontrer des limites lorsqu’elle grandit.

## 12. Infrastructure as Code et changements reproductibles

L’Infrastructure as Code (IaC) permet de décrire les ressources cloud dans des fichiers versionnés. Les outils courants incluent Terraform, OpenTofu, AWS CloudFormation, Azure Bicep et les modèles propres à d’autres plateformes.

Les avantages :
- rendre les changements répétables ;
- examiner les différences avant application ;
- conserver un historique ;
- effectuer des revues de code ;
- réduire les écarts entre environnements.

L’IaC n’élimine pas les erreurs. Une règle trop permissive définie dans un fichier est tout aussi dangereuse qu’une règle créée manuellement. Protège les secrets, utilise les revues et validations, et sépare les environnements de test et de production.

## 13. Atelier guidé : concevoir un petit réseau cloud

### Objectif

Concevoir un réseau logique pour une application web de démonstration avec :
- un point d’entrée public HTTPS ;
- deux serveurs applicatifs dans des sous-réseaux privés ou derrière un point d’entrée contrôlé ;
- une base de données privée ;
- une sortie Internet limitée pour les mises à jour ;
- un accès d’administration sécurisé ;
- des journaux permettant le dépannage.

### Étape 1 — Plan d’adressage

Choisis une plage privée qui ne chevauche pas les réseaux existants. Pour l’exercice, utilise `10.20.0.0/16`, avec des sous-réseaux comme `10.20.1.0/24` pour l’entrée, `10.20.2.0/24` pour l’application et `10.20.3.0/24` pour les données.

Avant d’utiliser ces plages dans un vrai environnement, compare-les aux plages du LAN, des VPN, des autres VPC/VNet et des réseaux partenaires. Un chevauchement peut compliquer ou empêcher le routage.

### Étape 2 — Routes

Définis conceptuellement :
- une route locale pour les destinations du réseau virtuel ;
- une route publique vers une passerelle Internet là où elle est nécessaire ;
- une route par défaut depuis les ressources privées vers une passerelle NAT si elles doivent initier des connexions Internet ;
- des routes privées vers le réseau d’entreprise uniquement si une connexion hybride est prévue.

Ne copie pas une table de routage d’un fournisseur à un autre sans l’adapter.

### Étape 3 — Règles de sécurité

Écris les besoins métier avant les règles :
1. les utilisateurs accèdent au point d’entrée en HTTPS ;
2. le point d’entrée communique avec l’application sur son port ;
3. l’application communique avec la base de données sur son port ;
4. l’administration passe par un canal séparé et authentifié ;
5. les ressources privées n’acceptent pas de connexions directes depuis Internet.

Transforme ensuite ces besoins en règles concrètes. Évite les règles qui autorisent tout trafic depuis `0.0.0.0/0` lorsqu’une source plus précise suffit.

### Étape 4 — Tests

Teste séparément :
- la résolution DNS du nom public ;
- la connexion HTTPS au point d’entrée ;
- la communication du point d’entrée vers l’application ;
- la communication de l’application vers la base de données ;
- l’absence de connexion publique directe à la base de données ;
- la sortie Internet des ressources privées, si elle est prévue ;
- les journaux pour les flux autorisés et rejetés.

### Étape 5 — Résilience

Pose les questions suivantes :
- Que se passe-t-il si une zone devient indisponible ?
- Le point d’entrée détecte-t-il une cible en panne ?
- Les données sont-elles sauvegardées et restaurables ?
- La passerelle de sortie est-elle un point de défaillance unique ?
- Qui reçoit les alertes ?
- Le plan de reprise a-t-il été testé ?

Un diagramme de réseau n’est terminé que lorsque les flux, les contrôles et les hypothèses de disponibilité sont documentés.

## 14. Erreurs fréquentes chez les débutants

**Confondre réseau virtuel et VPN.** Le réseau virtuel est le domaine réseau logique ; le VPN fournit un tunnel sécurisé entre des points.

**Penser qu’une adresse publique suffit.** Il faut aussi une route, des règles compatibles et un service actif.

**Mettre une base de données dans un sous-réseau exposé.** Place-la dans une zone privée et n’autorise que les sources applicatives nécessaires.

**Oublier le chemin retour.** Une route dans un sens ne garantit pas le retour, notamment avec les ACL sans état, les équipements intermédiaires ou des routes asymétriques.

**Croire que NAT est un pare-feu complet.** NAT traduit des adresses ; il ne remplace pas les règles de sécurité ni les contrôles applicatifs.

**Utiliser des plages qui se chevauchent.** Les connexions VPN et les interconnexions deviennent difficiles si le réseau local et le cloud utilisent les mêmes préfixes.

**Tester seulement avec ping.** ICMP peut être filtré. Teste aussi le DNS, le port et le protocole réellement utilisé.

**Ouvrir tous les ports pour “faire fonctionner”.** Cela masque la cause réelle et crée une exposition inutile. Procède par tests ciblés.

**Oublier IPv6.** Si IPv6 est activé, ses routes et ses règles doivent être examinées indépendamment.

**Ignorer les coûts réseau.** NAT, transfert de données, interzones et journaux peuvent générer des coûts significatifs.

## 15. Mini-évaluation

### Questions

1. À quoi sert un réseau virtuel cloud ?
2. Quelle est la différence entre un réseau virtuel et un VPN ?
3. Pourquoi place-t-on généralement une base de données dans un sous-réseau privé ?
4. Que signifie la destination `0.0.0.0/0` dans une table de routage IPv4 ?
5. Une machine privée peut-elle accéder à Internet sans avoir sa propre adresse publique ?
6. Pourquoi une adresse publique ne garantit-elle pas qu’un service soit joignable ?
7. Quelle différence générale existe entre un groupe de sécurité et une ACL réseau ?
8. Quel rôle joue le DNS ?
9. À quoi sert un répartiteur de charge ?
10. Pourquoi faut-il vérifier le chemin retour ?
11. Quelles sont les principales précautions d’un VPN site à site ?
12. Pourquoi faut-il vérifier le chevauchement des plages IP avant de relier deux réseaux ?
13. Que peut révéler un journal de flux réseau ?
14. Pourquoi ne faut-il pas se contenter de `ping` pour diagnostiquer HTTPS ?
15. Quels coûts réseau faut-il estimer avant un déploiement ?

### Corrigé

1. Il fournit un espace réseau logique pour relier et isoler des ressources cloud.
2. Le réseau virtuel héberge les ressources ; le VPN transporte du trafic entre des points via un tunnel sécurisé.
3. Pour réduire l’exposition et limiter les sources autorisées à communiquer avec les données.
4. Toutes les destinations IPv4 qui ne correspondent pas à une route plus spécifique.
5. Oui, souvent grâce à une passerelle NAT ou un autre service de sortie configuré.
6. Les routes, règles réseau, pare-feu et services doivent aussi autoriser le trafic.
7. Un groupe de sécurité s’applique généralement à une interface ou une ressource et est souvent à état ; une ACL s’applique généralement à une frontière de sous-réseau et peut être sans état. Les détails varient.
8. Il associe les noms de domaine à des informations réseau telles que des adresses IP.
9. Il répartit les connexions ou requêtes entre plusieurs cibles et peut contribuer à la disponibilité.
10. Parce que les réponses doivent aussi atteindre la source à travers un chemin autorisé.
11. Configurer les deux extrémités, les routes, les plages, les paramètres cryptographiques, les règles et la supervision.
12. Deux réseaux avec des plages identiques ou chevauchantes sont difficiles à router sans traduction ou redesign.
13. Des métadonnées sur des communications acceptées ou rejetées, selon la plateforme et les options activées.
14. ICMP et HTTPS utilisent des mécanismes différents ; l’un peut être bloqué alors que l’autre fonctionne.
15. Transfert de données, trafic interzone/région, NAT, IP publiques, équilibrage, liaisons dédiées et journaux.

## 16. Checklist de conception

Avant de considérer un petit réseau cloud comme prêt, vérifie les points suivants :

- [ ] Le plan d’adressage est documenté et sans chevauchement connu.
- [ ] Les sous-réseaux correspondent aux rôles des ressources.
- [ ] Les tables de routage ont été examinées, y compris la route par défaut.
- [ ] Les ressources publiques sont limitées aux points d’entrée nécessaires.
- [ ] Les bases de données ne sont pas directement exposées à Internet.
- [ ] Les groupes de sécurité, ACL et pare-feu n’autorisent que les flux nécessaires.
- [ ] Les règles IPv4 et IPv6 sont toutes deux vérifiées si IPv6 est activé.
- [ ] Le DNS public et privé est compris et testé.
- [ ] Le VPN ou la liaison hybride, s’il y en a une, possède des routes aller et retour correctes.
- [ ] Les journaux réseau et les alertes sont activés là où ils sont nécessaires.
- [ ] Les coûts estimés correspondent au volume de trafic prévu.
- [ ] Les changements sont documentés et, si possible, gérés par Infrastructure as Code.
- [ ] Les sauvegardes et scénarios de reprise ont été testés.
- [ ] Les procédures de dépannage permettent de vérifier le nom, la route, le filtrage, le port et l’application.

## 17. Glossaire

- **ACL réseau** : ensemble de règles de filtrage appliquées à un niveau réseau défini par la plateforme.
- **Adresse IP** : identifiant réseau logique attribué à une interface ou à une ressource.
- **CIDR** : notation indiquant une adresse et la longueur de son préfixe réseau.
- **Cloud networking** : conception et gestion des communications réseau dans une infrastructure cloud.
- **DNS** : système distribué de résolution des noms.
- **IaaS** : service cloud donnant accès à des ressources d’infrastructure.
- **IPsec** : suite de protocoles permettant notamment de protéger des communications IP.
- **Load balancer** : service distribuant des connexions ou requêtes entre plusieurs cibles.
- **NAT** : traduction d’adresses réseau.
- **Passerelle Internet** : composant qui fournit un chemin entre un réseau virtuel et Internet.
- **Passerelle NAT** : service permettant généralement aux ressources privées d’initier des connexions vers l’extérieur.
- **Route** : règle indiquant une cible pour un ensemble de destinations.
- **Sous-réseau** : plage d’adresses appartenant à un réseau.
- **VPC/VNet** : réseau virtuel isolé logiquement dans un fournisseur cloud.
- **VPN** : tunnel réseau qui protège le transport du trafic entre des points.
- **Zone de disponibilité** : domaine d’infrastructure cloud conçu pour limiter certains impacts de panne.

## 18. Références pour aller plus loin

Pour apprendre à configurer un réseau réel, utilise la documentation officielle correspondant au fournisseur choisi :
- AWS — documentation Amazon VPC : https://docs.aws.amazon.com/vpc/
- Microsoft Azure — documentation Virtual Network : https://learn.microsoft.com/azure/virtual-network/
- Google Cloud — documentation VPC : https://cloud.google.com/vpc/docs
- IETF — RFC 1918, allocation d’adresses IPv4 privées : https://www.rfc-editor.org/rfc/rfc1918
- IETF — RFC 4632, CIDR : https://www.rfc-editor.org/rfc/rfc4632
- IETF — RFC 8200, spécification IPv6 : https://www.rfc-editor.org/rfc/rfc8200

Les documentations fournisseurs sont les références à privilégier pour les paramètres exacts, les limitations, les coûts et les comportements par défaut. Les services évoluent : vérifie les pages actuelles avant toute configuration de production.


## À retenir

Le cloud networking applique les mêmes principes fondamentaux que les réseaux traditionnels : adressage, sous-réseaux, routage, DNS et filtrage. La différence majeure est que l’infrastructure est définie et gérée en grande partie par logiciel. Pour comprendre ou dépanner une connexion, suis le chemin de bout en bout, vérifie les routes dans les deux sens, examine les règles de sécurité et confirme que le service cible fonctionne. Les schémas de ce cours comportent des **flèches directionnelles** pour distinguer le sens des flux, les connexions possibles et les chemins de sortie.
