# Ethernet et couche 2 — Niveau Débutant

**Niveau : Débutant** · **Domaine : Réseaux informatiques** · **Format : cours guidé, exemples, ateliers et autoévaluation**

## Objectifs pédagogiques

À la fin de ce cours, tu devrais pouvoir expliquer le rôle de la couche 2, lire les champs essentiels d’une trame Ethernet, distinguer une adresse MAC d’une adresse IP, décrire comment un commutateur apprend où se trouvent les appareils, comprendre la fonction des VLAN et d’ARP, reconnaître les risques de boucle, et appliquer une démarche de dépannage simple.

> **Idée centrale :** Ethernet organise la livraison des trames sur un réseau local. Les commutateurs utilisent principalement les adresses MAC pour décider sur quel port transférer une trame. Les adresses IP servent, elles, à l’acheminement de couche 3.

## 1. Où se situe la couche 2 ?

Les communications réseau sont souvent expliquées avec le modèle OSI à sept couches. La couche 1, dite **physique**, concerne le signal et le support : cuivre, fibre, connecteurs, niveaux électriques ou optiques. La couche 2, dite **liaison de données**, organise les échanges sur un lien local : trames, adresses MAC, détection d’erreurs au niveau de la trame et contrôle d’accès au média selon la technologie. La couche 3, dite **réseau**, s’occupe notamment de l’adressage IP et du routage entre réseaux.

Exemple : un ordinateur veut joindre une imprimante située sur le même VLAN. L’application produit des données, TCP ou UDP peut les transporter, IP les place dans un paquet, puis Ethernet encapsule ce paquet dans une trame destinée à l’adresse MAC appropriée. Le commutateur lit la trame Ethernet pour la transmettre sur le bon port.

### Les fonctions de la couche 2

- **Encapsulation :** placer les données de couche supérieure dans une trame.
- **Adressage local :** utiliser des adresses MAC source et destination.
- **Commutation :** transférer les trames entre les ports d’un switch.
- **Séparation logique :** les VLAN créent plusieurs domaines de diffusion sur une même infrastructure physique.
- **Détection d’erreurs de trame :** le FCS permet notamment de détecter certaines corruptions ; Ethernet ne corrige pas lui-même toutes les erreurs.

La couche 2 ne remplace pas le routage. Pour joindre un réseau IP distant, l’hôte envoie généralement la trame à la MAC de sa passerelle par défaut, puis le routeur effectue le transfert IP.

## 2. Ethernet et la trame

Ethernet est une famille de technologies LAN normalisées, notamment par IEEE 802.3. Une trame Ethernet II courante comporte une adresse MAC destination, une adresse MAC source, un champ EtherType, les données transportées et un FCS. Dans une capture logicielle, le préambule et le Start Frame Delimiter ne sont habituellement pas présentés comme les champs ordinaires d’une trame capturée, car ils sont gérés par l’interface réseau.

<div class="lesson-svg"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 278" role="img" aria-label="Structure simplifiée d'une trame Ethernet II" width="100%"><defs><marker id="eth1-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67e8f9"/></marker><style>@keyframes eth1-flow{to{stroke-dashoffset:-28}}.eth1-path{stroke-dasharray:7 7;animation:eth1-flow 1.5s linear infinite}@media(prefers-reduced-motion:reduce){.eth1-path{animation:none}}</style></defs><rect x="2" y="2" width="976" height="274" rx="16" fill="#090f1b" stroke="#26364d"/><text x="490" y="30" font-family="Arial,sans-serif" font-size="20" text-anchor="middle" fill="#f8fafc" font-weight="700">Trame Ethernet II — champs principaux</text><g font-family="Arial,sans-serif" font-size="13" text-anchor="middle"><rect x="30" y="72" width="170" height="66" rx="8" fill="#123047" stroke="#38bdf8"/><text x="115" y="99" fill="#e0f2fe" font-weight="700">MAC destination</text><text x="115" y="119" fill="#bae6fd">6 octets</text><rect x="208" y="72" width="170" height="66" rx="8" fill="#123047" stroke="#38bdf8"/><text x="293" y="99" fill="#e0f2fe" font-weight="700">MAC source</text><text x="293" y="119" fill="#bae6fd">6 octets</text><rect x="386" y="72" width="112" height="66" rx="8" fill="#34254c" stroke="#c084fc"/><text x="442" y="99" fill="#f3e8ff" font-weight="700">EtherType</text><text x="442" y="119" fill="#e9d5ff">2 octets</text><rect x="506" y="72" width="282" height="66" rx="8" fill="#163a32" stroke="#34d399"/><text x="647" y="99" fill="#d1fae5" font-weight="700">Données + éventuel remplissage</text><text x="647" y="119" fill="#a7f3d0">46 à 1500 octets en Ethernet classique</text><rect x="796" y="72" width="154" height="66" rx="8" fill="#49351a" stroke="#fbbf24"/><text x="873" y="99" fill="#fef3c7" font-weight="700">FCS</text><text x="873" y="119" fill="#fde68a">4 octets</text></g><path class="eth1-path" d="M34 162 H944" fill="none" stroke="#67e8f9" stroke-width="2" marker-end="url(#eth1-arrow)"/><text x="490" y="193" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#cbd5e1">Le switch s’appuie surtout sur les MAC et les informations de contrôle de la trame.</text><text x="490" y="218" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#94a3b8">Le préambule/SFD est omis du dessin ; les tags VLAN ajoutent 4 octets par tag 802.1Q.</text><text x="490" y="247" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#94a3b8">Le FCS est contrôlé au niveau Ethernet ; certaines cartes ou captures ne l’exposent pas.</text></svg></div>

### À retenir sur les tailles

Une trame Ethernet standard porte souvent jusqu’à 1500 octets de charge utile IP, mais **1500 octets est la MTU Ethernet habituelle**, pas la taille totale de la trame. Les détails exacts dépendent du type de trame, des tags et de la technologie. Le dessin ci-dessus présente les champs principaux de la trame Ethernet II et non tous les éléments physiques transmis sur le média.

### EtherType : quel protocole est transporté ?

Dans Ethernet II, l’EtherType indique le protocole encapsulé. Quelques valeurs souvent rencontrées :

| EtherType | Signification |
|---|---|
| `0x0800` | IPv4 |
| `0x0806` | ARP |
| `0x86DD` | IPv6 |
| `0x8100` | Tag VLAN 802.1Q dans le cas courant |

Ces valeurs aident à comprendre les captures, mais elles ne suffisent pas à diagnostiquer un réseau à elles seules.

## 3. Les adresses MAC

Une adresse MAC Ethernet fait habituellement 48 bits, soit six octets, souvent écrits en hexadécimal : `00:1A:2B:3C:4D:5E`. Une adresse MAC identifie une interface au niveau du lien. Elle n’indique pas directement où se trouve l’appareil dans un réseau IP et n’est pas un mécanisme d’authentification fiable : certaines interfaces permettent de modifier l’adresse utilisée.

### Les trois types de destination à reconnaître

- **Unicast :** une interface précise ; le bit de groupe du premier octet est à 0.
- **Multicast :** un groupe d’interfaces ; le bit de groupe est à 1.
- **Broadcast :** diffusion locale à toutes les stations du domaine de broadcast Ethernet, avec `FF:FF:FF:FF:FF:FF` comme adresse MAC destination.

Le broadcast n’est normalement pas transféré par un routeur vers tous les réseaux. Il reste dans son domaine de diffusion, sauf mécanismes spécifiques configurés explicitement.

### MAC source et MAC destination

La source est normalement l’interface qui a émis la trame sur le lien observé. La destination est l’interface à laquelle la trame est destinée sur ce segment. Quand un paquet IP traverse un routeur, les adresses MAC de la trame changent à chaque saut Ethernet, tandis que les adresses IP source/destination demeurent généralement les mêmes de bout en bout, à l’exception de mécanismes comme le NAT.

## 4. Ce que fait un commutateur Ethernet

Un commutateur (switch) apprend à partir de l’adresse MAC **source** des trames reçues. Il associe cette MAC au port d’entrée et au VLAN de la trame. Pour transférer une trame unicast, il cherche ensuite la MAC destination dans sa table de commutation, souvent appelée table MAC, FDB ou CAM table.

- **Destination connue :** le switch transmet généralement la trame uniquement sur le port associé, sans la renvoyer au port d’entrée.
- **Destination inconnue :** le switch inonde (flood) la trame sur les autres ports du même VLAN, selon les règles de commutation.
- **Broadcast :** la trame est diffusée aux ports du même VLAN concernés, à l’exception du port d’entrée.
- **Apprentissage dynamique :** les entrées sont réactualisées lorsque des trames sources sont observées et peuvent expirer après une période d’inactivité.

<div class="lesson-svg"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 350" role="img" aria-label="Un switch apprend les MAC sources et transfère vers le port de destination connu" width="100%"><defs><marker id="eth2-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67e8f9"/></marker><style>@keyframes eth2-flow{to{stroke-dashoffset:-24}}.eth2-path{stroke-dasharray:6 6;animation:eth2-flow 1.3s linear infinite}@media(prefers-reduced-motion:reduce){.eth2-path{animation:none}}</style></defs><rect x="2" y="2" width="976" height="346" rx="16" fill="#090f1b" stroke="#26364d"/><text x="490" y="30" font-family="Arial,sans-serif" font-size="20" font-weight="700" text-anchor="middle" fill="#f8fafc">Apprentissage et transfert dans un switch</text><g font-family="Arial,sans-serif"><rect x="36" y="92" width="170" height="76" rx="12" fill="#123047" stroke="#38bdf8" stroke-width="2"/><text x="121" y="121" font-size="16" font-weight="700" text-anchor="middle" fill="#e0f2fe">PC-A</text><text x="121" y="144" font-size="12" text-anchor="middle" fill="#bae6fd">MAC A</text><rect x="376" y="84" width="230" height="100" rx="12" fill="#18352f" stroke="#34d399" stroke-width="2"/><text x="491" y="117" font-size="18" font-weight="700" text-anchor="middle" fill="#d1fae5">Switch</text><text x="491" y="140" font-size="12" text-anchor="middle" fill="#a7f3d0">Table MAC : A → port 1</text><text x="491" y="160" font-size="12" text-anchor="middle" fill="#a7f3d0">B → port 2</text><rect x="774" y="92" width="170" height="76" rx="12" fill="#34254c" stroke="#c084fc" stroke-width="2"/><text x="859" y="121" font-size="16" font-weight="700" text-anchor="middle" fill="#f3e8ff">PC-B</text><text x="859" y="144" font-size="12" text-anchor="middle" fill="#e9d5ff">MAC B</text><path class="eth2-path" d="M206 130 H366" stroke="#67e8f9" stroke-width="3" fill="none" marker-end="url(#eth2-arrow)"/><path class="eth2-path" d="M616 130 H764" stroke="#c084fc" stroke-width="3" fill="none" marker-end="url(#eth2-arrow)"/><text x="286" y="116" font-size="12" text-anchor="middle" fill="#bae6fd">1 · entrée</text><text x="691" y="116" font-size="12" text-anchor="middle" fill="#e9d5ff">2 · sortie</text><rect x="170" y="226" width="640" height="82" rx="10" fill="#111c2d" stroke="#3a4c65"/><text x="490" y="250" font-size="14" font-weight="700" text-anchor="middle" fill="#f8fafc">Règle de base</text><text x="490" y="273" font-size="13" text-anchor="middle" fill="#cbd5e1">Le switch apprend la MAC source à l’entrée, puis recherche la MAC destination.</text><text x="490" y="293" font-size="12" text-anchor="middle" fill="#94a3b8">Si la destination est inconnue, il inonde le VLAN (sauf le port d’entrée).</text></g></svg></div>

### Exemple de table MAC

| VLAN | Adresse MAC | Port appris | Interprétation |
|---|---|---|---|
| 10 | `00:11:22:33:44:55` | Gi1/0/1 | La source a été observée sur le port 1 du VLAN 10 |
| 10 | `00:AA:BB:CC:DD:EE` | Gi1/0/2 | Une autre source se trouve derrière le port 2 |
| 20 | `00:11:22:33:44:55` | Gi1/0/8 | Une MAC peut apparaître dans une autre entrée si elle est légitimement présente dans un autre contexte VLAN, selon la topologie |

En pratique, l’association est liée au VLAN. Pour commencer un dépannage, vérifie le VLAN, la MAC recherchée et le port indiqué. Une MAC qui saute souvent entre deux ports peut révéler une boucle, un problème de câblage, une mobilité légitime ou une configuration redondante ; il faut recueillir des preuves avant de conclure.

### Pourquoi un switch n’envoie-t-il pas toujours une trame à tous les ports ?

Une destination connue permet de limiter le trafic inutile. Le flooding est normal pour les broadcasts, certains multicasts et les unicasts inconnus. Si la table MAC est vide ou si elle vient d’expirer, le switch peut temporairement inonder certaines trames jusqu’à avoir appris la destination.

## 5. ARP : trouver la MAC correspondant à une IPv4

Sur un réseau IPv4 local, l’hôte connaît souvent l’adresse IP de destination mais doit connaître la MAC à utiliser dans la trame. **ARP** (Address Resolution Protocol) permet d’obtenir cette association sur le lien local.

1. L’hôte consulte son cache ARP.
2. Si aucune entrée utilisable n’existe, il émet une requête ARP en broadcast : « Qui possède cette adresse IPv4 ? »
3. L’hôte concerné répond généralement avec son adresse MAC.
4. L’émetteur peut mettre l’association en cache pendant un délai limité.
5. Le paquet IP est ensuite encapsulé dans une trame Ethernet dirigée vers la MAC obtenue.

<div class="lesson-svg"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 348" role="img" aria-label="Échange ARP entre un PC et la passerelle locale" width="100%"><defs><marker id="eth3-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67e8f9"/></marker><marker id="eth3-arrow2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker><style>@keyframes eth3-flow{to{stroke-dashoffset:-25}}.eth3-path{stroke-dasharray:7 6;animation:eth3-flow 1.4s linear infinite}@media(prefers-reduced-motion:reduce){.eth3-path{animation:none}}</style></defs><rect x="2" y="2" width="976" height="344" rx="16" fill="#090f1b" stroke="#26364d"/><text x="490" y="30" font-family="Arial,sans-serif" font-size="20" font-weight="700" text-anchor="middle" fill="#f8fafc">Résolution ARP sur le réseau local</text><rect x="60" y="70" width="220" height="80" rx="12" fill="#123047" stroke="#38bdf8" stroke-width="2"/><text x="170" y="99" font-family="Arial,sans-serif" font-size="16" font-weight="700" text-anchor="middle" fill="#e0f2fe">PC-A</text><text x="170" y="122" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#bae6fd">192.168.10.20</text><rect x="700" y="70" width="220" height="80" rx="12" fill="#18352f" stroke="#34d399" stroke-width="2"/><text x="810" y="99" font-family="Arial,sans-serif" font-size="16" font-weight="700" text-anchor="middle" fill="#d1fae5">Passerelle</text><text x="810" y="122" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#a7f3d0">192.168.10.1</text><path class="eth3-path" d="M280 95 H690" fill="none" stroke="#67e8f9" stroke-width="3" marker-end="url(#eth3-arrow)"/><text x="490" y="82" font-family="Arial,sans-serif" font-size="13" font-weight="700" text-anchor="middle" fill="#bae6fd">1 · Requête ARP (broadcast)</text><path class="eth3-path" d="M700 134 H290" fill="none" stroke="#34d399" stroke-width="3" marker-end="url(#eth3-arrow2)"/><text x="490" y="157" font-family="Arial,sans-serif" font-size="13" font-weight="700" text-anchor="middle" fill="#a7f3d0">2 · Réponse ARP (unicast habituellement)</text><rect x="105" y="212" width="770" height="90" rx="10" fill="#111c2d" stroke="#3a4c65"/><text x="490" y="238" font-family="Arial,sans-serif" font-size="14" font-weight="700" text-anchor="middle" fill="#f8fafc">Puis seulement : trame contenant le paquet IP</text><text x="490" y="262" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#cbd5e1">MAC destination = MAC de la passerelle lorsque la destination IP est distante.</text><text x="490" y="284" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#94a3b8">ARP sert à IPv4 ; IPv6 utilise Neighbor Discovery (NDP), pas ARP.</text></svg></div>

### Destination dans le même réseau ou dans un réseau distant

- **Destination IPv4 dans le même sous-réseau :** l’hôte cherche la MAC du destinataire final avec ARP.
- **Destination IPv4 hors sous-réseau :** l’hôte cherche la MAC de sa passerelle par défaut. Le paquet IP garde normalement l’adresse IP distante comme destination, alors que la trame Ethernet est adressée à la MAC de la passerelle.

ARP ne traverse pas les routeurs comme un broadcast Ethernet ordinaire. Si ARP échoue, l’hôte peut ne pas pouvoir envoyer ses paquets IPv4 sur le lien même si l’adresse IP paraît correcte.

## 6. VLAN et domaines de broadcast

Un **VLAN** (Virtual LAN) sépare logiquement un réseau de niveau 2 en domaines de broadcast distincts. Deux ports peuvent appartenir au même switch physique, mais s’ils sont dans des VLAN différents, ils ne sont pas dans le même domaine de broadcast. Pour communiquer entre VLAN, il faut un équipement ou une fonction de couche 3, par exemple un routeur ou un switch multicouche correctement configuré.

- **Port access :** transporte normalement le trafic d’un seul VLAN non tagué côté terminal.
- **Port trunk :** transporte plusieurs VLAN, généralement avec des tags IEEE 802.1Q ; les détails du VLAN natif varient selon la configuration.
- **VLAN ID :** dans le champ 802.1Q, l’identifiant VLAN standard utilisable va de 1 à 4094 ; les valeurs 0 et 4095 ont des significations réservées/spéciales.
- **Segmentation :** les VLAN peuvent séparer postes, téléphones, serveurs, invités ou gestion, mais la sécurité dépend aussi des politiques de couche 3 et des contrôles d’accès.

<div class="lesson-svg"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 348" role="img" aria-label="Deux VLAN distincts sur un même switch et lien trunk vers un switch voisin" width="100%"><defs><marker id="eth4-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67e8f9"/></marker><style>@keyframes eth4-flow{to{stroke-dashoffset:-24}}.eth4-path{stroke-dasharray:7 6;animation:eth4-flow 1.4s linear infinite}@media(prefers-reduced-motion:reduce){.eth4-path{animation:none}}</style></defs><rect x="2" y="2" width="976" height="344" rx="16" fill="#090f1b" stroke="#26364d"/><text x="490" y="30" font-family="Arial,sans-serif" font-size="20" font-weight="700" text-anchor="middle" fill="#f8fafc">Segmentation logique par VLAN</text><rect x="350" y="76" width="280" height="78" rx="12" fill="#18352f" stroke="#34d399" stroke-width="2"/><text x="490" y="107" font-family="Arial,sans-serif" font-size="17" font-weight="700" text-anchor="middle" fill="#d1fae5">Switch A</text><text x="490" y="130" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#a7f3d0">Ports access + trunk</text><rect x="45" y="68" width="225" height="92" rx="10" fill="#123047" stroke="#38bdf8" stroke-width="2"/><text x="157" y="96" font-family="Arial,sans-serif" font-size="15" font-weight="700" text-anchor="middle" fill="#e0f2fe">VLAN 10</text><text x="157" y="119" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#bae6fd">PC / utilisateurs</text><text x="157" y="140" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#bae6fd">Broadcast limité au VLAN 10</text><rect x="710" y="68" width="225" height="92" rx="10" fill="#34254c" stroke="#c084fc" stroke-width="2"/><text x="822" y="96" font-family="Arial,sans-serif" font-size="15" font-weight="700" text-anchor="middle" fill="#f3e8ff">VLAN 20</text><text x="822" y="119" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#e9d5ff">Serveurs / imprimantes</text><text x="822" y="140" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#e9d5ff">Broadcast limité au VLAN 20</text><path class="eth4-path" d="M270 114 H340" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#eth4-arrow)"/><path class="eth4-path" d="M700 114 H640" fill="none" stroke="#c084fc" stroke-width="3" marker-end="url(#eth4-arrow)"/><rect x="145" y="220" width="690" height="80" rx="10" fill="#111c2d" stroke="#3a4c65"/><text x="490" y="246" font-family="Arial,sans-serif" font-size="14" font-weight="700" text-anchor="middle" fill="#f8fafc">Lien trunk 802.1Q vers un autre switch</text><text x="490" y="270" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#cbd5e1">Plusieurs VLAN peuvent traverser le lien ; le tag identifie le VLAN de la trame.</text><text x="490" y="288" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#94a3b8">Un trunk ne permet pas automatiquement le routage entre VLAN.</text></svg></div>

### Erreurs VLAN courantes

- Un poste est branché sur un port access du mauvais VLAN.
- Un VLAN n’est pas autorisé sur le trunk.
- Les deux extrémités du trunk ne s’accordent pas sur les paramètres pertinents.
- La passerelle de couche 3 n’existe pas ou est mal adressée.
- Un VLAN est présent sur un switch mais pas propagé ou créé là où il est nécessaire.

Toujours vérifier le VLAN réel du port et le chemin complet entre les équipements. Le simple fait que le voyant du port soit allumé ne prouve pas que le VLAN ou le routage est correct.

## 7. Boucles de couche 2 et Spanning Tree

Ethernet de base ne dispose pas d’un mécanisme général de durée de vie comparable au TTL IP permettant à une trame de broadcast de se supprimer toute seule lorsqu’elle tourne en boucle. Une boucle de couche 2 peut provoquer des tempêtes de broadcast, des duplications de trames et une instabilité de la table MAC (parfois appelée MAC flapping).

**Spanning Tree Protocol (STP)** et ses variantes, dont RSTP, permettent de construire une topologie sans boucle de transfert active pour un VLAN ou une instance donnée, tout en laissant des liens redondants disponibles comme chemins de secours. La façon exacte dont STP opère dépend du protocole, de la configuration et du modèle de commutation.

<div class="lesson-svg"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 366" role="img" aria-label="Boucle Ethernet entre trois switches et lien bloqué par Spanning Tree" width="100%"><defs><marker id="eth5-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67e8f9"/></marker><style>@keyframes eth5-flow{to{stroke-dashoffset:-22}}.eth5-path{stroke-dasharray:6 6;animation:eth5-flow 1.5s linear infinite}@media(prefers-reduced-motion:reduce){.eth5-path{animation:none}}</style></defs><rect x="2" y="2" width="976" height="362" rx="16" fill="#090f1b" stroke="#26364d"/><text x="490" y="30" font-family="Arial,sans-serif" font-size="20" font-weight="700" text-anchor="middle" fill="#f8fafc">Pourquoi éviter les boucles de niveau 2 ?</text><rect x="390" y="70" width="200" height="62" rx="10" fill="#18352f" stroke="#34d399" stroke-width="2"/><text x="490" y="96" font-family="Arial,sans-serif" font-size="15" font-weight="700" text-anchor="middle" fill="#d1fae5">Switch A</text><text x="490" y="116" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#a7f3d0">Pont racine (exemple)</text><rect x="110" y="230" width="200" height="62" rx="10" fill="#123047" stroke="#38bdf8" stroke-width="2"/><text x="210" y="257" font-family="Arial,sans-serif" font-size="15" font-weight="700" text-anchor="middle" fill="#e0f2fe">Switch B</text><text x="210" y="277" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#bae6fd">Lien redondant</text><rect x="670" y="230" width="200" height="62" rx="10" fill="#34254c" stroke="#c084fc" stroke-width="2"/><text x="770" y="257" font-family="Arial,sans-serif" font-size="15" font-weight="700" text-anchor="middle" fill="#f3e8ff">Switch C</text><text x="770" y="277" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#e9d5ff">Lien redondant</text><path class="eth5-path" d="M420 132 L270 220" fill="none" stroke="#67e8f9" stroke-width="3" marker-end="url(#eth5-arrow)"/><path class="eth5-path" d="M560 132 L710 220" fill="none" stroke="#67e8f9" stroke-width="3" marker-end="url(#eth5-arrow)"/><path d="M310 261 H660" fill="none" stroke="#f87171" stroke-width="3" stroke-dasharray="8 7"/><path d="M464 250 L484 270 M484 250 L464 270" stroke="#f87171" stroke-width="4"/><text x="490" y="242" font-family="Arial,sans-serif" font-size="12" font-weight="700" text-anchor="middle" fill="#fecaca">Lien logique bloqué par STP/RSTP</text><rect x="90" y="312" width="800" height="36" rx="8" fill="#2a171d" stroke="#7f1d1d"/><text x="490" y="335" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#fecaca">Sans contrôle de boucle : broadcast storms, doublons et MAC flapping peuvent survenir.</text></svg></div>

### Indices d’une boucle possible

- Le réseau devient lent ou instable juste après une modification de câblage.
- Les voyants de plusieurs ports clignotent intensément sans raison habituelle.
- Les journaux signalent des changements répétés de topologie ou des MAC apprises alternativement sur différents ports.
- Les broadcasts augmentent fortement.

Ne débranche pas des liens au hasard sur un réseau de production. Identifie la topologie, vérifie l’état STP/RSTP et suis la procédure de changement ou d’escalade de l’organisation.

## 8. Négociation de lien, duplex et erreurs physiques

Avant d’étudier une trame, vérifie que le lien fonctionne à une vitesse et un mode duplex cohérents. Les connexions modernes utilisent généralement l’auto-négociation, et il faut éviter de fixer manuellement une valeur d’un seul côté sans raison technique documentée.

Termes à reconnaître :

- **Vitesse du lien :** par exemple 100 Mb/s, 1 Gb/s ou davantage.
- **Full-duplex :** émission et réception simultanées sur le lien commuté habituel.
- **Half-duplex :** mode historique partagé qui peut utiliser CSMA/CD ; il est rare sur les liens modernes en switch.
- **CRC/FCS errors :** peuvent signaler une corruption physique, un problème de câble, de connecteur, de transceiver ou d’équipement.
- **Drops/discards :** peuvent être liés à la congestion, aux buffers, aux politiques ou à d’autres conditions ; il faut interpréter les compteurs dans leur contexte.

Une capture de paquets n’expose pas forcément tous les défauts physiques. Un compteur d’erreurs qui augmente à l’interface et une capture côté hôte apportent des indices différents, qu’il faut corréler.

## 9. Dépanner Ethernet couche 2 : une méthode simple

Procède du plus proche au plus éloigné. Note les faits et l’heure de chaque test. Change une chose à la fois, si possible, pour savoir ce qui a réellement amélioré ou aggravé la situation.

<div class="lesson-svg"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 470" role="img" aria-label="Arbre de diagnostic de couche 2, du lien physique aux VLAN et à la table MAC" width="100%"><defs><marker id="eth6-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67e8f9"/></marker><style>@keyframes eth6-flow{to{stroke-dashoffset:-22}}.eth6-path{stroke-dasharray:6 6;animation:eth6-flow 1.5s linear infinite}@media(prefers-reduced-motion:reduce){.eth6-path{animation:none}}</style></defs><rect x="2" y="2" width="976" height="466" rx="16" fill="#090f1b" stroke="#26364d"/><text x="490" y="30" font-family="Arial,sans-serif" font-size="20" font-weight="700" text-anchor="middle" fill="#f8fafc">Diagnostic de base : du physique à la logique</text><rect x="340" y="54" width="300" height="54" rx="10" fill="#123047" stroke="#38bdf8" stroke-width="2"/><text x="490" y="77" font-family="Arial,sans-serif" font-size="14" font-weight="700" text-anchor="middle" fill="#e0f2fe">1 · Le lien est-il opérationnel ?</text><text x="490" y="95" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#bae6fd">Voyants, état de port, câble, erreurs</text><path class="eth6-path" d="M490 108 V134" fill="none" stroke="#67e8f9" stroke-width="3" marker-end="url(#eth6-arrow)"/><rect x="340" y="138" width="300" height="54" rx="10" fill="#18352f" stroke="#34d399" stroke-width="2"/><text x="490" y="160" font-family="Arial,sans-serif" font-size="14" font-weight="700" text-anchor="middle" fill="#d1fae5">2 · Le port est-il dans le bon VLAN ?</text><text x="490" y="178" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#a7f3d0">Access, trunk, VLAN autorisés</text><path class="eth6-path" d="M490 192 V218" fill="none" stroke="#67e8f9" stroke-width="3" marker-end="url(#eth6-arrow)"/><rect x="340" y="222" width="300" height="54" rx="10" fill="#34254c" stroke="#c084fc" stroke-width="2"/><text x="490" y="244" font-family="Arial,sans-serif" font-size="14" font-weight="700" text-anchor="middle" fill="#f3e8ff">3 · La MAC est-elle apprise ?</text><text x="490" y="262" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#e9d5ff">Table MAC / FDB et port attendu</text><path class="eth6-path" d="M490 276 V302" fill="none" stroke="#67e8f9" stroke-width="3" marker-end="url(#eth6-arrow)"/><rect x="340" y="306" width="300" height="54" rx="10" fill="#49351a" stroke="#fbbf24" stroke-width="2"/><text x="490" y="328" font-family="Arial,sans-serif" font-size="14" font-weight="700" text-anchor="middle" fill="#fef3c7">4 · ARP / passerelle / IP ?</text><text x="490" y="346" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#fde68a">Séparer L2 du diagnostic L3</text><path class="eth6-path" d="M490 360 V386" fill="none" stroke="#67e8f9" stroke-width="3" marker-end="url(#eth6-arrow)"/><rect x="230" y="390" width="520" height="56" rx="10" fill="#111c2d" stroke="#3a4c65"/><text x="490" y="413" font-family="Arial,sans-serif" font-size="14" font-weight="700" text-anchor="middle" fill="#f8fafc">5 · Vérifier STP, compteurs et chemin complet</text><text x="490" y="432" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#cbd5e1">Collecter les preuves avant de modifier la configuration.</text></svg></div>

### Étapes de contrôle

1. **Définir le symptôme.** Un seul terminal est-il concerné ou tout le VLAN ? Depuis quand ? Quel changement a précédé la panne ?
2. **Vérifier le physique.** État du port, câble, transceiver, vitesse/duplex et compteurs d’erreurs.
3. **Vérifier la commutation.** VLAN du port, état administratif, table MAC, apprentissage et port de sortie.
4. **Vérifier le trunk.** VLAN présent et autorisé sur chaque trunk du chemin ; config cohérente aux extrémités.
5. **Vérifier ARP et IP.** Cache ARP, adresse IP, masque, passerelle et test vers une destination locale, puis distante.
6. **Inspecter les protections de boucle.** État STP/RSTP, ports bloqués, changements de topologie et MAC flapping.
7. **Capturer si nécessaire.** Une capture peut montrer ARP sans réponse, broadcasts répétés ou retransmissions, mais le point de capture influence ce qu’on observe.
8. **Documenter.** Horodatage, ports, VLAN, MAC/IP, commandes exécutées, résultats et actions envisagées.

### Quelques commandes d’observation

La syntaxe diffère selon le constructeur, le modèle et la version. Les exemples Cisco IOS sont courants mais doivent être adaptés à l’environnement :

```text
show interfaces status
show interfaces counters errors
show mac address-table dynamic
show vlan brief
show interfaces trunk
show spanning-tree
show arp
```

Ces commandes sont principalement destinées à **observer**. Dans un environnement de production, privilégie d’abord les commandes en lecture seule et respecte les procédures d’accès. N’exécute pas de commande de configuration ou de redémarrage sans comprendre ses effets et obtenir l’autorisation requise.

## 10. Lire une petite capture Wireshark

Wireshark permet d’observer les trames lorsqu’une interface ou une méthode de capture appropriée est disponible. Sur un port commuté, l’ordinateur ne voit pas automatiquement toutes les communications des autres ports. Un port miroir/SPAN, un TAP ou une capture à un point pertinent peut être nécessaire, sous réserve des autorisations et des règles de confidentialité.

Filtres d’affichage utiles :

```text
eth
eth.dst == ff:ff:ff:ff:ff:ff
arp
vlan
eth.src == 00:11:22:33:44:55
```

Les filtres exacts dépendent des champs exposés par la version de Wireshark. Pour une requête ARP, cherche notamment l’adresse IP recherchée et vérifie si une réponse correspondante arrive. Pour une trame VLAN-tagged, inspecte le tag 802.1Q et le VLAN ID. L’absence d’un paquet dans une capture ne prouve pas à elle seule qu’il n’a jamais existé : il peut être masqué par le point de capture, l’offload, un filtre ou une perte de capture.

## 11. Sécurité de niveau 2 : les bases

La couche 2 est une partie importante de la surface d’attaque d’un LAN. Plusieurs mécanismes peuvent réduire les risques, selon les équipements et l’architecture :

- **Port security :** limiter ou contrôler les MAC apprises sur certains ports, si la politique de l’organisation le prévoit.
- **DHCP snooping :** aider à protéger l’infrastructure DHCP en distinguant ports de confiance et non fiables ; la configuration doit être cohérente avec la topologie.
- **Dynamic ARP Inspection (DAI) :** valider certains messages ARP en s’appuyant notamment sur des informations de confiance disponibles sur le switch.
- **BPDU Guard / protections STP :** protéger des ports d’accès contre certains branchements incorrects ; une mauvaise configuration peut aussi interrompre une connexion légitime.
- **Désactivation des ports inutilisés :** réduire les connexions non autorisées, avec une documentation et un processus de changement.

Aucune fonctionnalité ne doit être activée sans vérifier les dépendances, les ports de confiance, les exceptions légitimes et la compatibilité des équipements. Par exemple, DHCP snooping configuré incorrectement peut empêcher l’attribution d’adresses à des clients légitimes.

## 12. Atelier pratique guidé

### Scénario A — Un poste ne communique plus avec son voisin

**Contexte :** PC-A et PC-B sont censés se trouver dans le VLAN 10. PC-A peut accéder à sa propre configuration, mais ne reçoit aucune réponse du PC-B.

**Procédure :**

1. Confirmer les adresses IPv4, les masques et le VLAN attendu des deux postes.
2. Vérifier l’état des ports et que les ports d’accès appartiennent bien au VLAN 10.
3. Rechercher les deux MAC dans la table MAC du switch.
4. Effacer ou renouveler le cache ARP uniquement si cela est approprié et autorisé ; sinon observer d’abord son état.
5. Capturer ARP au point approprié : la requête est-elle émise ? Arrive-t-elle à PC-B ? Une réponse repart-elle ?
6. Si les postes sont dans le même sous-réseau, vérifier les pare-feux hôtes et l’adresse de destination ; ne pas supposer qu’une absence de ping indique toujours une panne Ethernet.

**Interprétation :** si PC-A émet ARP mais que la requête n’atteint pas PC-B, examine d’abord VLAN, trunk et chemin de couche 2. Si PC-B reçoit la requête et répond mais que PC-A ne voit pas la réponse, suis le retour et vérifie les tables MAC ainsi que les politiques pertinentes.

### Scénario B — Des postes obtiennent parfois le réseau, parfois non

**Contexte :** plusieurs ports deviennent instables après le branchement d’un petit switch non géré.

**Hypothèses à tester :** boucle de couche 2, comportement STP, port flapping, câble défectueux, alimentation instable ou congestion. Le symptôme ne suffit pas à choisir une cause.

**Actions :** relever les journaux, les changements STP, les MAC qui changent de port et les compteurs de broadcasts. Identifier précisément l’équipement ajouté et ses câbles. Appliquer la procédure locale de confinement ou d’escalade ; éviter les débranchements improvisés si d’autres services sont dépendants de ce lien.

### Scénario C — Un poste rejoint le VLAN 10, mais le serveur est dans le VLAN 20

**Question :** Pourquoi une requête ARP de PC-A ne trouve-t-elle pas directement le serveur ?

**Réponse :** les VLAN 10 et 20 constituent normalement des domaines de broadcast séparés. PC-A doit utiliser sa passerelle de couche 3 pour joindre le réseau IP distant. Il résout donc la MAC de la passerelle dans le VLAN 10, puis le routeur/switch L3 route le paquet vers le VLAN 20. Il faut vérifier les routes, les interfaces VLAN et les politiques, pas étendre le broadcast d’ARP entre les VLAN sans raison.

## 13. Erreurs fréquentes et idées fausses

**« La MAC identifie l’appareil sur Internet. »** Non. C’est un identifiant de couche 2 utilisé sur un lien local ; le routage se fonde sur les adresses IP.

**« Un switch connaît toutes les MAC dès qu’il démarre. »** Non. Il apprend dynamiquement à partir des MAC source observées, sauf entrées statiques ou mécanismes spécifiques.

**« Un broadcast atteint tout le réseau de l’entreprise. »** Pas nécessairement. Un broadcast Ethernet est limité à son domaine de broadcast/VLAN, sauf dispositifs spécifiques configurés pour relayer certains messages.

**« VLAN 10 et VLAN 20 peuvent communiquer parce qu’ils sont sur le même switch. »** Pas sans une fonction de routage et des politiques adaptées.

**« Si le lien est vert, tout est correct. »** Non. Un lien actif ne valide ni l’appartenance VLAN, ni le trunk, ni la table MAC, ni le routage IP ou la sécurité.

**« Tout paquet absent de Wireshark n’a pas circulé. »** Non. Le point de capture, les filtres, l’offload et les pertes de capture peuvent modifier la visibilité.

## 14. Fiche de diagnostic à remplir

Copie ce modèle dans un ticket ou un compte rendu :

```text
Incident :
Date et heure de début :
Utilisateurs/services impactés :
Topologie et ports concernés :
VLAN attendu / VLAN observé :
MAC source / MAC destination :
Adresses IP et masque :
État du lien / vitesse-duplex :
Compteurs d'erreurs :
Table MAC :
État du trunk / VLAN autorisés :
État STP/RSTP :
Résultats ARP / tests locaux :
Capture effectuée (où, quand, filtre) :
Constats vérifiés :
Hypothèses restantes :
Actions réalisées et heure :
Résultat après intervention :
Prochaine action / responsable :
```

Sépare toujours les **faits observés**, les **hypothèses** et les **actions**. Cette discipline évite de présenter une supposition comme la cause racine.

## 15. Exercices d’autoévaluation

### Questions

1. À quoi servent les adresses MAC dans Ethernet ?
2. Quelle adresse apprend habituellement un switch pour alimenter sa table MAC : source ou destination ?
3. Que fait un switch quand il ne connaît pas la MAC destination d’une trame unicast ?
4. Quelle différence y a-t-il entre un port access et un trunk ?
5. Pourquoi un PC utilise-t-il la MAC de la passerelle pour joindre une IP distante ?
6. Quel protocole permet la résolution IPv4-vers-MAC sur le LAN ?
7. Cite deux indices possibles d’une boucle de couche 2.
8. Pourquoi le routage est-il nécessaire pour communiquer entre deux VLAN séparés ?
9. Que peut indiquer une hausse de compteurs CRC/FCS ?
10. Pourquoi une capture sur un poste ne voit-elle pas forcément le trafic des autres ports du switch ?

### Corrigé

1. Elles fournissent l’adressage de couche 2 pour livrer une trame sur le lien local.
2. L’adresse MAC source de la trame reçue.
3. Il inonde généralement le VLAN concerné sur les autres ports admissibles, sauf le port d’entrée.
4. Un port access transporte normalement un VLAN non tagué pour un terminal ; un trunk transporte plusieurs VLAN, généralement au moyen de tags 802.1Q.
5. Parce que la destination IP est hors du réseau local et que la trame Ethernet du premier saut doit être envoyée à la passerelle.
6. ARP.
7. Par exemple, tempêtes de broadcast, changements de topologie répétés, MAC flapping et réseau fortement dégradé.
8. Les VLAN forment des domaines de broadcast distincts ; un équipement de couche 3 doit acheminer les paquets entre eux.
9. Possiblement une corruption physique ou un problème de câble/connecteur/transceiver, à confirmer avec d’autres mesures.
10. Le switch envoie en général les unicasts connus seulement sur le port de sortie ; une capture doit être placée à un point qui voit le trafic pertinent.

## 16. Glossaire essentiel

| Terme | Définition simple |
|---|---|
| **Ethernet** | Technologie de réseau local pour transporter des trames. |
| **Trame** | Unité de données de couche 2. |
| **Adresse MAC** | Adresse de couche 2 utilisée sur le lien local. |
| **Switch** | Équipement qui transfère les trames selon ses informations de commutation. |
| **Table MAC / FDB** | Association des MAC apprises avec un VLAN et un port. |
| **Flooding** | Transmission d’une trame sur plusieurs ports admissibles du même VLAN. |
| **Broadcast** | Trame destinée à toutes les interfaces du domaine de broadcast local. |
| **ARP** | Protocole de résolution IPv4-vers-MAC sur le lien local. |
| **VLAN** | Segment logique de couche 2 isolant un domaine de broadcast. |
| **802.1Q** | Mécanisme courant d’identification des VLAN avec un tag dans la trame. |
| **Trunk** | Lien qui transporte plusieurs VLAN. |
| **STP/RSTP** | Protocoles qui évitent les boucles de transfert actives tout en autorisant la redondance. |
| **FCS** | Champ de contrôle utilisé pour détecter certaines erreurs de trame. |
| **MTU** | Taille maximale de la charge utile réseau qu’un lien permet de transporter sans fragmentation de couche supérieure selon le contexte. |

## 17. Résumé final

La couche 2 organise l’échange local des trames. Les adresses MAC permettent d’identifier les interfaces sur le lien ; le switch apprend les MAC sources et consulte sa table pour transférer les trames. Les trames broadcast et les destinations inconnues peuvent être diffusées dans le VLAN, ce qui rend la segmentation importante. ARP associe une adresse IPv4 à une MAC locale ; si la destination IP est distante, l’hôte envoie la trame à sa passerelle. Les VLAN séparent les domaines de broadcast, les trunks transportent plusieurs VLAN, et STP/RSTP aide à éviter les boucles. Pour dépanner, avance du physique au logique, vérifie les ports/VLAN/tables MAC, puis ARP et le routage, tout en documentant les preuves.

## Références utiles

- [IEEE 802.3 Ethernet Working Group](https://www.ieee802.org/3/) — informations sur les standards Ethernet.
- [IEEE 802.1Q](https://www.ieee802.org/1/pages/802.1Q.html) — ponts et réseaux virtuels/VLAN.
- [RFC 826 — An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826) — définition historique d’ARP pour IPv4.
- [RFC 9293 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293) — contexte transport TCP, utile pour distinguer transport et couche liaison.
- [Wireshark User’s Guide](https://www.wireshark.org/docs/wsug_html/) — capture et analyse des trames.
- [Cisco — VLAN Configuration Guide](https://www.cisco.com/c/en/us/support/switches/catalyst-9200-series-switches/products-installation-and-configuration-guides-list.html) — documentation d’exemple pour les switches Cisco ; les commandes changent selon la gamme et la version.

> **Bonne pratique :** les commandes et la logique générale du cours sont transférables, mais les noms d’interfaces, la syntaxe CLI et certains comportements varient selon le fabricant et la version logicielle. Utilise toujours la documentation adaptée à ton équipement et respecte les procédures de changement.
