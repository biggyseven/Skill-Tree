# Cisco SD-Access — Niveau Débutant

> **Fichier :** `sd-access-debutant.md`  
> **Parcours :** Architecture réseau → Cisco SD-Access → Niveau Débutant  
> **Objectif :** comprendre l’architecture, les rôles, les plans opérationnels et les grands principes de déploiement d’une fabric Cisco SD-Access, sans prétendre remplacer un guide de déploiement validé pour une version précise.

## Comment utiliser ce cours

Ce support est conçu pour une progression autonome. Lis les sections dans l’ordre, refais les schémas à la main, puis réponds aux questions avant de consulter les corrigés. Les commandes et écrans peuvent varier selon le modèle matériel, IOS XE, Cisco Catalyst Center, Cisco ISE, les licences et la version de la solution. SD-Access est une architecture orchestrée : les déploiements réels doivent s’appuyer sur la matrice de compatibilité et le guide Cisco correspondant aux versions retenues.

### Prérequis

Il est utile de connaître les bases d’Ethernet, VLAN, IPv4/IPv6, routage IP, DHCP, DNS, 802.1X et les équipements Cisco Catalyst. Si ces notions ne sont pas encore solides, révise d’abord le cours d’architecture réseau débutant. Le but ici n’est pas de mémoriser des écrans de contrôleur, mais de comprendre ce qui est automatisé, ce qui circule sur le réseau et où chercher lorsqu’un service ne fonctionne pas.

## 1. Pourquoi Cisco SD-Access ?

Cisco **Software-Defined Access (SD-Access)** est une architecture de campus pilotée par l’intention. Elle vise à automatiser le déploiement des réseaux filaires et sans fil, à appliquer des politiques de segmentation cohérentes et à améliorer la visibilité opérationnelle. Elle s’appuie sur une fabric : un réseau physique qui transporte un ou plusieurs réseaux logiques isolés.

Dans un campus traditionnel, la connectivité repose souvent sur une combinaison de VLAN, de trunks, de passerelles, d’ACL et de configurations répétées sur les commutateurs. Chaque changement de bâtiment ou de commutateur peut nécessiter plusieurs ajustements. Les VLAN restent utiles et ne disparaissent pas magiquement avec SD-Access, mais la logique de segmentation et de transport est orchestrée différemment : le réseau logique est construit au-dessus d’un underlay IP, tandis que des politiques fondées sur l’identité peuvent être appliquées sur la fabric.

SD-Access ne signifie pas que le réseau n’a plus de CLI, ni que tous les problèmes sont automatiquement corrigés. Il déplace une partie importante du travail vers un modèle centralisé, déclaré et vérifié. La qualité des prérequis, du plan IP, de la connectivité du underlay, des politiques et des procédures de changement reste essentielle.

### Les objectifs typiques

- **Automatiser** l’intégration et le provisionnement des équipements compatibles.
- **Segmenter** les utilisateurs, appareils IoT, invités et serveurs de manière cohérente.
- **Unifier les politiques** filaires et sans fil lorsque les fonctions et modes de déploiement retenus le permettent.
- **Améliorer la visibilité** sur les équipements, les terminaux, leur santé et certains chemins réseau.
- **Réduire les opérations manuelles répétitives** et les risques d’incohérences entre les équipements.

### Diagramme 1 — LAN classique et SD-Access

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="490" viewBox="0 0 1000 490"><rect x="1" y="1" width="998" height="488" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">De la LAN classique à la fabric SD-Access</text><rect x="24" y="70" width="450" height="390" rx="18" fill="#111D30" stroke="#3E536F" stroke-width="2" /><rect x="526" y="70" width="450" height="390" rx="18" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="249" y="105" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#68AEFF" text-anchor="middle">LAN classique</text><text x="751" y="105" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#36D6B0" text-anchor="middle">Cisco SD-Access</text><rect x="55" y="142" width="130" height="60" rx="12" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="120" y="166" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VLAN 10</text><text x="120" y="187" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Utilisateurs</text><rect x="55" y="236" width="130" height="60" rx="12" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="120" y="260" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VLAN 20</text><text x="120" y="281" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Invités</text><rect x="235" y="183" width="95" height="74" rx="12" fill="#1D3553" stroke="#52708F" stroke-width="2" /><text x="282" y="210" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Switch</text><text x="282" y="231" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">L2/L3</text><line x1="185" y1="172" x2="225.81929652782102" y2="198.94073570836187" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="235,205 222.6684790961692,203.71470151389494 228.97011395947285,194.1667699028288" fill="#68AEFF" /><line x1="185" y1="266" x2="225.9038084772352" y2="238.18541023548008" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="235,232 229.12022179968483,242.91542982731778 222.68739515478558,233.45539064364237" fill="#FFBD69" /><rect x="347" y="185" width="95" height="70" rx="12" fill="#182941" stroke="#3E536F" stroke-width="2" /><text x="394" y="211" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Core</text><text x="394" y="232" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">routage</text><line x1="330" y1="220" x2="336.0" y2="220.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="347,220 336.0,225.72 336.0,214.28" fill="#F4F7FB" /><text x="249" y="340" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">Segmentation souvent liée</text><text x="249" y="363" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">aux VLAN et aux ACL</text><text x="249" y="404" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FF7788" text-anchor="middle">Configuration par équipement</text><rect x="555" y="142" width="120" height="60" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="615" y="166" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Employés</text><text x="615" y="187" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN CORP</text><rect x="555" y="236" width="120" height="60" rx="12" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="615" y="260" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Invités</text><text x="615" y="281" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN GUEST</text><rect x="720" y="181" width="110" height="80" rx="12" fill="#1D3553" stroke="#36D6B0" stroke-width="2" /><text x="775" y="208" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Edge node</text><text x="775" y="229" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VXLAN</text><rect x="863" y="181" width="90" height="80" rx="12" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="908" y="207" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border</text><text x="908" y="227" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">réseau ext.</text><line x1="675" y1="172" x2="711.1295450455873" y2="198.4949997000973" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="720,205 707.7469448896379,203.10763627639196 714.5121452015367,193.88236312380266" fill="#36D6B0" /><line x1="675" y1="266" x2="710.75371861397" y2="242.9587146709971" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="720,237 713.8522502428885,247.76678099173267 707.6551869850515,238.15064835026152" fill="#C4A1FF" /><line x1="830" y1="221" x2="852.0" y2="221.0" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="863,221 852.0,226.72 852.0,215.28" fill="#68AEFF" /><line x1="744" y1="280" x2="744" y2="305" stroke="#36D6B0" stroke-width="2" stroke-linecap="round" /><line x1="744" y1="305" x2="917" y2="305" stroke="#36D6B0" stroke-width="2" stroke-linecap="round" /><line x1="917" y1="305" x2="917" y2="280" stroke="#36D6B0" stroke-width="2" stroke-linecap="round" /><text x="830" y="335" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#36D6B0" text-anchor="middle">Overlay logique sur underlay IP</text><text x="751" y="378" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">VN/VRF + SGT + automatisation</text><text x="751" y="413" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#36D6B0" text-anchor="middle">Politique fondée sur l’identité</text></svg>

**À retenir :** SD-Access n’est pas un type de câble ou un protocole unique. C’est une architecture combinant automatisation, fabric, virtualisation réseau et application de politiques.

## 2. Les composants majeurs

### Cisco Catalyst Center

Cisco Catalyst Center est la plateforme de gestion, d’orchestration, de provisionnement et d’assurance utilisée par SD-Access. Elle aide à représenter les sites, inventorier les équipements, définir des paramètres réseau, construire la fabric, déployer des politiques et observer l’état du réseau. Les noms de menus et workflows peuvent évoluer entre versions ; on doit donc suivre le guide correspondant à l’installation utilisée.

Catalyst Center n’est pas le commutateur qui transporte physiquement chaque paquet. Il automatise et coordonne les configurations et collecte des informations d’état. La perte du contrôleur ne doit pas être assimilée automatiquement à l’arrêt immédiat de la transmission de tous les paquets : le comportement exact dépend des fonctions déjà provisionnées et du scénario de panne. En revanche, les opérations de gestion, les changements, certaines fonctions de contrôle et la visibilité peuvent être affectés.

### Cisco Identity Services Engine (ISE)

Cisco ISE fournit des fonctions d’identité, d’authentification et d’autorisation. Dans les designs intégrés, il peut contribuer à déterminer qui se connecte, quel type de terminal est reconnu et quelle politique s’applique. Les méthodes incluent notamment 802.1X et, dans certains scénarios, MAB (*MAC Authentication Bypass*). MAB est moins fort que 802.1X du point de vue de l’identité : une adresse MAC peut être usurpée ; son usage doit donc être encadré.

### Équipements réseau compatibles fabric

Les commutateurs et plateformes compatibles exécutent les fonctions fabric. Le rôle logique dépend du design et du provisionnement, pas seulement du nom commercial du matériel. Toujours vérifier la compatibilité des modèles, des modules et des versions logicielles dans la matrice Cisco officielle avant de dessiner l’architecture finale.

### Terminaux et services partagés

Les terminaux peuvent être des ordinateurs, téléphones, imprimantes, capteurs IoT, points d’accès ou autres appareils. Les services partagés incluent typiquement DHCP, DNS, NTP, serveurs d’authentification, applications, services de sécurité et accès Internet. Leur localisation et leur méthode de raccordement doivent être définies dans le design.

## 3. Les quatre plans opérationnels

SD-Access sépare quatre fonctions conceptuelles :

1. **Plan de gestion :** Catalyst Center pour l’orchestration, la gestion et l’assurance.
2. **Plan de contrôle :** LISP (*Locator/ID Separation Protocol*) pour les échanges et les mappings de localisation des endpoints.
3. **Plan de données :** VXLAN pour transporter les paquets dans la fabric avec une encapsulation de tunnel.
4. **Plan de politique :** Cisco TrustSec et les Security Group Tags (SGT), associés aux règles de segmentation et d’accès.

Ce découpage permet de répondre à quatre questions différentes : *comment gère-t-on le réseau ? comment trouve-t-on le terminal de destination ? comment transporte-t-on son trafic ? quelle communication est autorisée ?* Une panne ou une erreur dans un plan peut produire des symptômes qui ressemblent à ceux d’un autre plan ; le dépannage consiste à isoler les fonctions plutôt qu’à modifier toutes les configurations en même temps.

### Diagramme 2 — Les quatre plans

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="470" viewBox="0 0 1000 470"><rect x="1" y="1" width="998" height="468" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Les quatre plans opérationnels</text><rect x="92" y="92" width="816" height="72" rx="14" fill="#182941" stroke="#C4A1FF" stroke-width="3" /><text x="114" y="121" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#C4A1FF" text-anchor="start">GESTION</text><text x="114" y="147" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="start">Catalyst Center — orchestration, déploiement, assurance</text><rect x="92" y="184" width="816" height="72" rx="14" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="114" y="213" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#68AEFF" text-anchor="start">PLAN DE CONTRÔLE</text><text x="114" y="239" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="start">LISP — association EID (endpoint) ↔ RLOC (nœud de fabric)</text><rect x="92" y="276" width="816" height="72" rx="14" fill="#182941" stroke="#36D6B0" stroke-width="3" /><text x="114" y="305" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#36D6B0" text-anchor="start">PLAN DE DONNÉES</text><text x="114" y="331" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="start">VXLAN — encapsulation des paquets dans le réseau IP</text><rect x="92" y="368" width="816" height="72" rx="14" fill="#182941" stroke="#FFBD69" stroke-width="3" /><text x="114" y="397" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#FFBD69" text-anchor="start">PLAN DE POLITIQUE</text><text x="114" y="423" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="start">Cisco TrustSec / SGT — décision d’accès selon les groupes</text></svg>

## 4. Comprendre la fabric : underlay et overlay

### L’underlay : le réseau IP de transport

L’**underlay** est la fondation physique et IP de la fabric. Il comprend les liens entre équipements et le routage qui permet d’atteindre les adresses de localisation des nœuds fabric, souvent décrites comme des RLOC (*Routing Locators*). Le design campus SD-Access privilégie généralement une structure routée de couche 3, notamment pour rendre la convergence et les chemins plus prévisibles.

Les terminaux et leurs sous-réseaux utilisateurs appartiennent au réseau logique overlay, pas au plan d’adressage de transport de l’underlay. Cela ne veut pas dire que le réseau d’accès physique n’a aucun lien avec les terminaux : les commutateurs edge les raccordent, mais le transport de fabric est séparé de la logique d’adressage des endpoints.

L’underlay doit être stable et correctement dimensionné. Il faut vérifier la connectivité IP, le routage, la redondance, les boucles de routage, la cohérence du MTU et la capacité du matériel. VXLAN ajoute un surcoût d’encapsulation ; le MTU exact à configurer ne doit pas être inventé universellement. Il faut le déduire du design validé, des liens de bout en bout et des éventuels réseaux WAN intermédiaires.

### L’overlay : les réseaux logiques

L’**overlay** est construit au-dessus de l’underlay. SD-Access peut transporter plusieurs *Virtual Networks* (VN) qui sont, dans les designs courants, représentés par des instances VRF pour isoler les tables de routage. Les terminaux peuvent alors utiliser des espaces d’adressage et politiques logiques différents tout en partageant la même infrastructure physique.

Imagine deux départements : le réseau CORP et le réseau GUEST. Une VN distincte peut séparer leurs tables de routage. Une telle séparation de macro-segmentation ne garantit pas, à elle seule, chaque règle de sécurité à l’intérieur d’une même VN ; elle doit être complétée, quand nécessaire, par des politiques plus fines.

### Diagramme 3 — Underlay et overlay

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="450" viewBox="0 0 1000 450"><rect x="1" y="1" width="998" height="448" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Underlay et overlay : deux couches complémentaires</text><text x="250" y="88" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="700" fill="#68AEFF" text-anchor="middle">UNDERLAY : transport IP réel</text><text x="750" y="88" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="700" fill="#36D6B0" text-anchor="middle">OVERLAY : réseaux logiques</text><line x1="100" y1="170" x2="250" y2="130" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><line x1="250" y1="130" x2="380" y2="175" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><line x1="100" y1="170" x2="170" y2="305" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><line x1="250" y1="130" x2="170" y2="305" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><line x1="380" y1="175" x2="330" y2="325" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><line x1="170" y1="305" x2="330" y2="325" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><line x1="250" y1="130" x2="330" y2="325" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><circle cx="100" cy="170" r="27" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="100" y="176" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#F4F7FB" text-anchor="middle">E1</text><circle cx="250" cy="130" r="27" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="250" y="136" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#F4F7FB" text-anchor="middle">I1</text><circle cx="380" cy="175" r="27" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="380" y="181" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#F4F7FB" text-anchor="middle">I2</text><circle cx="170" cy="305" r="27" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="170" y="311" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#F4F7FB" text-anchor="middle">I3</text><circle cx="330" cy="325" r="27" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="330" y="331" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#F4F7FB" text-anchor="middle">E2</text><rect x="470" y="134" width="190" height="72" rx="16" fill="#182941" stroke="#36D6B0" stroke-width="3" /><text x="565" y="167" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#F4F7FB" text-anchor="middle">VN CORP</text><text x="565" y="192" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">VRF isolée</text><rect x="695" y="134" width="190" height="72" rx="16" fill="#182941" stroke="#C4A1FF" stroke-width="3" /><text x="790" y="167" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#F4F7FB" text-anchor="middle">VN INVITÉS</text><text x="790" y="192" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">VRF isolée</text><rect x="470" y="274" width="190" height="72" rx="16" fill="#182941" stroke="#FFBD69" stroke-width="3" /><text x="565" y="307" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#F4F7FB" text-anchor="middle">VN IoT</text><text x="565" y="332" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">VRF isolée</text><rect x="695" y="274" width="190" height="72" rx="16" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="790" y="307" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#F4F7FB" text-anchor="middle">VN SERVEURS</text><text x="790" y="332" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">VRF isolée</text><text x="250" y="398" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Liens L3 + routage + reachabilité RLOC</text><text x="750" y="398" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Même transport physique, plusieurs VN</text><line x1="455" y1="245" x2="499.0" y2="245.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="510,245 499.0,250.72 499.0,239.28" fill="#F4F7FB" /></svg>

### Analogie simple

- Underlay : les routes, ponts et rues physiques.
- Overlay : les itinéraires logiques et les quartiers isolés qu’on superpose à ces routes.
- Plan de contrôle : le répertoire qui indique comment joindre une destination.
- Plan de données : le transport réel du paquet.
- Politique : les règles qui décident si une communication est permise.

L’analogie aide à se repérer, mais ne remplace pas la description technique : les paquets sont transférés par des équipements et protocoles réels, et les politiques dépendent de la configuration effective.

## 5. Les rôles de la fabric

Les rôles sont des fonctions logicielles exécutées sur du matériel compatible. Un même équipement peut, dans certains designs supportés, héberger plusieurs rôles ; les séparer peut faciliter la résilience, la capacité et l’exploitation. Le rôle exact doit être choisi en fonction du modèle, de la taille du site et des recommandations correspondant à la version.

### Fabric edge node

Le **fabric edge** connecte les terminaux utilisateurs et IoT. Il apprend ou reçoit le contexte des endpoints, les enregistre auprès du plan de contrôle selon le design et applique les fonctions d’accès. Il fournit généralement une passerelle Anycast pour les sous-réseaux associés à la VN. Dans l’architecture logique, le edge fonctionne comme un point d’entrée et de sortie de tunnel (xTR) pour le trafic fabric.

### Control plane node

Le **control plane node** héberge les fonctions LISP qui suivent les associations entre identités des endpoints (EID, *Endpoint Identifiers*) et localisations de routage (RLOC). Cette base permet au fabric de localiser un endpoint sans traiter l’adresse comme si elle révélait seule la position physique. Pour la haute disponibilité, on planifie les nœuds et leur capacité selon les recommandations du design, la taille du site et le nombre d’endpoints.

### Border node

Le **border node** permet la communication entre la fabric et les réseaux externes : campus traditionnel, WAN, réseau de datacenter, Internet ou autre fabric selon le design. Il prend part à l’encapsulation ou à la décapsulation fabric et au raccordement de routes externes. Les routes de retour sont tout aussi importantes que le chemin aller : une route aller correcte n’implique pas que les réponses reviendront par un chemin valide.

### Intermediate node

Un nœud intermédiaire transporte le trafic IP de l’underlay entre les appareils qui portent les rôles fabric. Il assure la connectivité physique et IP ; il ne devient pas un edge ou border simplement parce que des paquets VXLAN le traversent.

### Fabric site et fabric zone

Un **fabric site** est une construction logique représentant un ensemble d’équipements qui participent à une fabric. Une **fabric zone** permet d’organiser des parties d’un site selon les fonctions et capacités prises en charge. Ces concepts ne doivent pas être confondus avec une VN/VRF ou avec un SGT : ils organisent le déploiement et l’exploitation, tandis que les VN et SGT remplissent des fonctions de segmentation.

### Diagramme 4 — Rôles de fabric

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="430" viewBox="0 0 1000 430"><rect x="1" y="1" width="998" height="428" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Rôles d’une fabric : edge, control plane, intermediate, border</text><rect x="32" y="200" width="125" height="82" rx="13" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="94" y="226" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Postes</text><text x="94" y="247" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">utilisateurs</text><rect x="205" y="180" width="150" height="120" rx="16" fill="#1D3553" stroke="#36D6B0" stroke-width="3" /><text x="280" y="217" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Fabric edge</text><text x="280" y="239" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">nœud d’accès</text><text x="280" y="261" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">xTR / GW</text><rect x="445" y="94" width="150" height="92" rx="15" fill="#182941" stroke="#C4A1FF" stroke-width="3" /><text x="520" y="125" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Control plane</text><text x="520" y="147" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">LISP mapping</text><rect x="445" y="250" width="150" height="92" rx="15" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="520" y="281" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Intermediate</text><text x="520" y="303" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">underlay IP</text><rect x="690" y="180" width="150" height="120" rx="16" fill="#1D3553" stroke="#FFBD69" stroke-width="3" /><text x="765" y="217" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border node</text><text x="765" y="239" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">sortie fabric</text><text x="765" y="261" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">VXLAN ↔ IP</text><rect x="873" y="200" width="95" height="82" rx="13" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="920" y="226" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">WAN / DC</text><text x="920" y="246" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Internet</text><line x1="157" y1="241" x2="194.0" y2="241.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="205,241 194.0,246.72 194.0,235.28" fill="#36D6B0" /><line x1="355" y1="220" x2="436.54956592442886" y2="152.0420283963093" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="445,145 440.21142069050967,156.4362541156063 432.88771115834805,147.6478026770123" fill="#C4A1FF" /><line x1="355" y1="258" x2="434.82620139501944" y2="290.8174383512858" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="445,295 432.651269337688,296.1078136258757 437.00113345235087,285.52706307669587" fill="#68AEFF" /><line x1="595" y1="145" x2="681.2777241102001" y2="211.29761957941693" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="690,218 677.7924862914969,215.83320304211287 684.7629619289033,206.762036116721" fill="#C4A1FF" /><line x1="595" y1="296" x2="679.7137896464417" y2="263.89793234450633" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="690,260 681.740714465585,269.24676172835666 677.6868648272983,258.549102960656" fill="#68AEFF" /><line x1="840" y1="241" x2="862.0" y2="241.0" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="873,241 862.0,246.72 862.0,235.28" fill="#FFBD69" /><text x="520" y="67" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C4A1FF" text-anchor="middle">Plan de contrôle : échange de mappings</text><text x="519" y="383" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Nœud intermédiaire : transporte le trafic IP</text><text x="765" y="343" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FFBD69" text-anchor="middle">Le border relie fabric et réseaux externes</text></svg>

## 6. LISP : trouver la localisation d’un endpoint

LISP sépare deux notions :

- **EID (Endpoint Identifier) :** identifiant de l’endpoint, par exemple son adresse IP dans la fabric.
- **RLOC (Routing Locator) :** localisation d’un nœud de fabric joignable dans l’underlay.

Le plan de contrôle conserve les associations EID–RLOC. Lorsqu’un endpoint se déplace d’un edge à un autre, son contexte de localisation peut changer alors que son identité réseau logique reste la même. Le système de contrôle actualise les mappings selon le comportement supporté par le design.

Pour un débutant, il est suffisant de retenir que LISP répond à la question **« où se trouve l’endpoint de destination dans la fabric ? »**. Il ne remplace pas le routage IP de l’underlay ; les RLOC doivent rester joignables. Si le underlay est brisé, le fait qu’un mapping existe ne suffit pas à livrer le paquet.

### Diagramme 5 — EID et RLOC

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420"><rect x="1" y="1" width="998" height="418" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">LISP : séparer identité et localisation</text><rect x="38" y="140" width="205" height="105" rx="14" fill="#182941" stroke="#36D6B0" stroke-width="3" /><text x="140" y="172" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Endpoint A</text><text x="140" y="194" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">EID : 10.10.10.10</text><text x="140" y="211" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#C1CCDA" text-anchor="middle">Edge A / RLOC A</text><rect x="383" y="115" width="235" height="150" rx="14" fill="#1D3553" stroke="#C4A1FF" stroke-width="3" /><text x="500" y="150" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="500" fill="#F4F7FB" text-anchor="middle">Nœud de contrôle LISP</text><text x="500" y="184" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Base des mappings</text><text x="500" y="215" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#C1CCDA" text-anchor="middle">EID destination → RLOC</text><rect x="757" y="140" width="205" height="105" rx="14" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="859" y="172" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Endpoint B</text><text x="859" y="194" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">EID : 10.20.20.20</text><text x="859" y="211" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#C1CCDA" text-anchor="middle">Edge B / RLOC B</text><line x1="243" y1="183" x2="372.0" y2="183.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="383,183 372.0,188.72 372.0,177.28" fill="#36D6B0" /><line x1="618" y1="183" x2="746.0" y2="183.0" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="757,183 746.0,188.72 746.0,177.28" fill="#68AEFF" /><text x="313" y="160" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="middle">requête mapping</text><text x="685" y="160" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#68AEFF" text-anchor="middle">RLOC appris</text><rect x="275" y="318" width="450" height="66" rx="12" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="500" y="343" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">EID = identité/ID du terminal ; RLOC = localisation du tunnel</text><text x="500" y="367" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#C1CCDA" text-anchor="middle">LISP répond à « où joindre cet endpoint ? »</text><line x1="500" y1="265" x2="500.0" y2="307.0" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="500,318 494.28,307.0 505.72,307.0" fill="#C4A1FF" /></svg>

### LISP ne transporte pas le trafic utilisateur

Les échanges de contrôle qui mettent à jour ou consultent les mappings ne sont pas le paquet applicatif lui-même. Une fois la destination localisée, le plan de données transporte le paquet sur la fabric. En cas de panne, vérifie à la fois les informations de mapping et la connectivité du underlay ; ces deux états sont différents.

## 7. VXLAN : transporter les paquets dans l’overlay

VXLAN encapsule le paquet interne dans un transport UDP/IP externe. Pour simplifier : la trame et les informations IP de l’endpoint sont conservées dans l’enveloppe interne ; l’en-tête extérieur permet au réseau underlay d’acheminer le paquet jusqu’au nœud fabric distant. Les identifiants de segmentation portés par le VXLAN permettent de distinguer les réseaux logiques.

Dans SD-Access, VXLAN est la base du plan de données de la fabric. Il ne faut pas réduire le protocole à « ajouter un tag » : il s’agit d’une encapsulation permettant de transporter le trafic à travers un réseau IP. L’underlay route le paquet extérieur vers la destination de tunnel ; le nœud de sortie de tunnel traite ensuite le paquet interne selon la logique fabric.

### Diagramme 6 — Vue simplifiée de l’encapsulation

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="440" viewBox="0 0 1000 440"><rect x="1" y="1" width="998" height="438" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Plan de données : lecture simplifiée d’un paquet VXLAN</text><rect x="28" y="160" width="150" height="120" rx="12" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="103.0" y="207" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Ethernet</text><text x="103.0" y="228" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">interne</text><rect x="188" y="160" width="160" height="120" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="3" /><text x="268.0" y="207" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">IP / transport</text><text x="268.0" y="228" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">interne</text><rect x="358" y="160" width="130" height="120" rx="12" fill="#182941" stroke="#C4A1FF" stroke-width="3" /><text x="423.0" y="207" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VXLAN</text><text x="423.0" y="228" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VNI / segment</text><rect x="498" y="160" width="90" height="120" rx="12" fill="#182941" stroke="#FFBD69" stroke-width="3" /><text x="543.0" y="222" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="600" fill="#F4F7FB" text-anchor="middle">UDP</text><rect x="598" y="160" width="185" height="120" rx="12" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="690.5" y="207" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">IP externe</text><text x="690.5" y="228" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">RLOC source/destination</text><rect x="793" y="160" width="175" height="120" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="3" /><text x="880.5" y="207" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Ethernet</text><text x="880.5" y="228" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">physique</text><text x="500" y="105" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#C1CCDA" text-anchor="middle">Encapsulation : conserver le paquet interne, ajouter un transport de fabric</text><text x="500" y="325" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="600" fill="#36D6B0" text-anchor="middle">Le réseau underlay route le paquet externe vers le RLOC distant.</text><text x="500" y="358" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">Le VNI identifie le segment logique ; VXLAN ne remplace pas l’authentification.</text><text x="500" y="400" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#FFBD69" text-anchor="middle">Prévoir un MTU suffisant selon le chemin et le design validé.</text></svg>

### Pourquoi le MTU compte

L’encapsulation ajoute des octets. Si une chaîne de liens ne permet pas le paquet encapsulé de taille attendue, le problème peut apparaître sous forme de pertes sélectives ou de comportements étranges sur les paquets volumineux. Les petites pings peuvent réussir alors que certains flux d’application échouent. Le MTU doit être validé de bout en bout : edge, intermédiaires, border et éventuel transport WAN. Si un réseau intermédiaire impose un MTU inférieur, le design doit prévoir la stratégie compatible, y compris une éventuelle adaptation de MSS TCP lorsqu’elle est prise en charge et recommandée.

## 8. Segmentation : VN/VRF et SGT

### Macro-segmentation avec les Virtual Networks

Une VN fournit une séparation de niveau réseau, souvent à travers une VRF dédiée. Elle est adaptée lorsque des populations doivent disposer de tables de routage distinctes, par exemple employés et invités. Les échanges entre VN doivent être conçus explicitement à travers un chemin contrôlé, tel qu’un pare-feu ou une intégration de routage sécurisée prévue par l’architecture.

### Micro-segmentation avec SGT

Les **Security Group Tags (SGT)** permettent de représenter un groupe de sécurité, par exemple employés, imprimantes, IoT ou administrateurs. La politique peut être définie selon les groupes source et destination plutôt qu’en multipliant des règles uniquement basées sur des adresses IP. Cisco TrustSec et ses mécanismes d’application de politiques sont associés au plan de politique de SD-Access.

Le tag n’est pas lui-même une politique complète : il identifie le groupe. Il faut également que le groupe soit attribué de manière correcte et que les règles entre groupes soient définies et appliquées aux bons points du réseau. Une politique illustrative pourrait autoriser les postes administratifs à gérer les commutateurs via SSH, autoriser les employés à joindre des applications métier, et empêcher des objets IoT de lancer des connexions arbitraires vers les postes utilisateurs.

### Diagramme 7 — Macro et micro-segmentation

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="450" viewBox="0 0 1000 450"><rect x="1" y="1" width="998" height="448" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Segmentation : VN/VRF et SGT répondent à deux besoins distincts</text><rect x="30" y="86" width="440" height="335" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><rect x="530" y="86" width="440" height="335" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="250" y="120" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="700" fill="#68AEFF" text-anchor="middle">Macro-segmentation : VN / VRF</text><text x="750" y="120" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="700" fill="#FFBD69" text-anchor="middle">Micro-segmentation : SGT</text><rect x="65" y="150" width="170" height="84" rx="12" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="150" y="182" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN CORP</text><text x="150" y="204" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">VRF distincte</text><rect x="275" y="150" width="160" height="84" rx="12" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="355" y="182" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN INVITÉS</text><text x="355" y="204" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">VRF distincte</text><line x1="235" y1="192" x2="275" y2="192" stroke="#FF7788" stroke-width="3" stroke-linecap="round" /><text x="255" y="178" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="600" fill="#FF7788" text-anchor="middle">isolé</text><text x="250" y="275" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">Routage entre VN uniquement via</text><text x="250" y="300" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">un chemin explicitement autorisé</text><text x="250" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#68AEFF" text-anchor="middle">Sépare des tables de routage</text><rect x="570" y="151" width="125" height="66" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="632" y="178" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">SGT 10</text><text x="632" y="199" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Employés</text><rect x="725" y="151" width="125" height="66" rx="12" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="787" y="178" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">SGT 20</text><text x="787" y="199" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">IoT</text><rect x="850" y="151" width="95" height="66" rx="12" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="897" y="178" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">SGT 30</text><text x="897" y="199" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">IT</text><text x="750" y="258" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">Matrice de politiques entre groupes</text><rect x="577" y="276" width="350" height="86" rx="10" fill="#1D3553" stroke="#526984" stroke-width="1" /><text x="595" y="300" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="start">Source</text><text x="700" y="300" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="start">Destination</text><text x="815" y="300" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="start">Action</text><text x="595" y="325" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">Employés</text><text x="700" y="325" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">Serveurs</text><text x="815" y="325" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="start">Autoriser*</text><text x="595" y="350" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">IoT</text><text x="700" y="350" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">Employés</text><text x="815" y="350" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#FF7788" text-anchor="start">Refuser*</text><text x="750" y="395" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FFBD69" text-anchor="middle">SGT = groupe ; matrice/SGACL = décision</text></svg>

### Comment choisir ?

| Besoin | Construction à examiner | Question de validation |
|---|---|---|
| Isoler des tables de routage | VN / VRF | Quels flux doivent sortir de la VN ? |
| Distinguer des groupes dans un même domaine réseau | SGT et politiques de groupe | Où la politique est-elle appliquée ? |
| Autoriser un accès à une application précise | Politique de sécurité et contrôle de service | Les protocoles, ports et chemins retour sont-ils cohérents ? |
| Isoler les invités du réseau interne | VN dédiée, politiques et sortie contrôlée | DHCP, DNS, Internet et accès internes sont-ils testés séparément ? |

Ne traite pas la VN, le VLAN local, le SGT et le site comme des synonymes. Ils correspondent à des niveaux de conception différents.

## 9. Admission et identité des terminaux

Quand un utilisateur branche son poste ou rejoint le Wi-Fi, le réseau doit identifier le terminal et appliquer la politique prévue. Un workflow typique implique le port d’accès ou le chemin Wi-Fi, le mécanisme d’authentification, ISE pour l’identité et l’autorisation, puis l’attribution ou l’application du contexte de segmentation pris en charge par le design.

**802.1X** permet d’authentifier un supplicant à travers un authentificateur réseau avec un serveur AAA. **MAB** peut être utilisé pour certains équipements qui ne supportent pas 802.1X, mais ce mécanisme se fonde généralement sur une adresse MAC, donc il exige des mesures de compensation adaptées au risque. Une imprimante inconnue ne devrait pas recevoir les mêmes privilèges qu’un poste administrateur simplement parce qu’elle a réussi un mécanisme de secours.

### Diagramme 8 — Identité et politique

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420"><rect x="1" y="1" width="998" height="418" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Admission réseau : identité, autorisation et segmentation</text><rect x="24" y="162" width="130" height="90" rx="13" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="89" y="195" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Terminal</text><text x="89" y="216" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">802.1X / MAB</text><rect x="210" y="162" width="150" height="90" rx="13" fill="#1D3553" stroke="#68AEFF" stroke-width="2" /><text x="285" y="193" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Fabric edge</text><text x="285" y="215" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">port d’accès</text><rect x="416" y="88" width="170" height="90" rx="13" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="501" y="119" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Cisco ISE</text><text x="501" y="141" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">identité / AAA</text><rect x="416" y="255" width="170" height="90" rx="13" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="501" y="286" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Catalyst Center</text><text x="501" y="308" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">provisionnement</text><rect x="650" y="162" width="145" height="90" rx="13" fill="#1D3553" stroke="#36D6B0" stroke-width="2" /><text x="722" y="193" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN + SGT</text><text x="722" y="215" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">résultat policy</text><rect x="850" y="162" width="125" height="90" rx="13" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="912" y="193" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Accès</text><text x="912" y="215" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">contrôlé</text><line x1="154" y1="207" x2="199.0" y2="207.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="210,207 199.0,212.72 199.0,201.28" fill="#36D6B0" /><line x1="360" y1="187" x2="408.0107726020925" y2="141.56123307301957" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="416,134 411.9426138000627,145.71563131993145 404.07893140412233,137.40683482610768" fill="#C4A1FF" /><line x1="360" y1="226" x2="409.3621306279591" y2="291.2285297583745" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="416,300 404.80096610231385,294.6802218318358 413.9232951536044,287.77683768491323" fill="#FFBD69" /><line x1="586" y1="134" x2="641.3317318890298" y2="177.22791553830453" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="650,184 637.8102479689481,181.73541495600904 644.8532158091115,172.72041612060002" fill="#C4A1FF" /><line x1="586" y1="300" x2="642.5775388050057" y2="238.118316932025" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="650,230 646.7990636096587,241.97799675342205 638.3560140003527,234.25863711062797" fill="#FFBD69" /><line x1="795" y1="207" x2="839.0" y2="207.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="850,207 839.0,212.72 839.0,201.28" fill="#36D6B0" /><text x="285" y="140" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="middle">authentification</text><text x="501" y="66" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C4A1FF" text-anchor="middle">Décideur d’identité</text><text x="501" y="378" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#FFBD69" text-anchor="middle">Orchestration/configuration</text><text x="720" y="290" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="middle">Résultat déployé</text></svg>

### Exemple de logique de politique

1. Le terminal se connecte à un port ou au réseau Wi-Fi.
2. Le réseau lance le mécanisme d’authentification configuré.
3. ISE évalue l’identité, les attributs et la politique d’autorisation.
4. Le réseau reçoit la décision et le contexte pris en charge (par exemple accès, VN et groupe de sécurité).
5. Le trafic est soumis à la segmentation et aux règles de sécurité prévues.
6. L’opérateur vérifie le résultat dans les outils de visibilité et les journaux, sans se fier uniquement à l’affichage d’un statut « connecté ».

L’intégration exacte, les attributs retournés et leur représentation dans Catalyst Center dépendent des versions et des profils de déploiement. On évite d’inventer une commande universelle pour tous ces workflows.

## 10. Le rôle de Catalyst Center dans le déploiement

Le contrôleur transforme l’intention de réseau en configuration cohérente sur les équipements compatibles. Un déploiement sérieux commence par la préparation, pas par le clic sur « provisionner ».

### Étape 1 — Définir l’inventaire et les contraintes

Recenser les modèles, versions logicielles, modules, licences, versions de Catalyst Center et ISE, types de terminaux, nombres de ports, besoins Wi-Fi, besoins d’isolement et dépendances applicatives. Vérifier les combinaisons prises en charge dans la matrice officielle. Les capacités de chaque rôle de fabric et les fonctions disponibles ne sont pas identiques sur tous les matériels.

### Étape 2 — Préparer les services réseau

Prévoir l’adressage de gestion et de transport, DNS, NTP, AAA, SNMP, syslog, accès au contrôleur, accès aux services partagés et procédures de sauvegarde. Les horloges cohérentes sont essentielles pour corréler les événements. Préparer également un plan de rollback et un accès hors bande quand c’est possible.

### Étape 3 — Construire un underlay stable

Déployer ou automatiser le réseau IP routé sous-jacent. Vérifier les adjacences de routage, les routes, les RLOC, la redondance, les métriques et le MTU. Ne commence pas le test des politiques overlay tant que la connectivité underlay n’est pas stable.

### Étape 4 — Définir les sites et les rôles de fabric

Organiser les équipements et sites logiques, choisir les edge, border et control plane nodes, déterminer si certains rôles seront colocalisés, et prévoir la redondance. La colocalisation peut convenir à certains sites ; elle n’est pas un choix automatique pour toutes les tailles et tous les profils de mobilité.

### Étape 5 — Créer les VN, pools et passerelles

Définir chaque VN, l’adressage et les pools, la passerelle Anycast et les services nécessaires. Une passerelle Anycast utilise une adresse de passerelle cohérente pour le sous-réseau logique sur les edge concernés. Cela simplifie la mobilité à l’intérieur du domaine fabric prévu, mais n’élimine pas le besoin de concevoir le DHCP, le DNS, le routage et les dépendances applicatives.

### Étape 6 — Déployer l’identité et les politiques

Intégrer ISE lorsque le design le demande ; organiser les groupes, les règles d’autorisation et les politiques entre groupes. Partir d’une politique documentée et testable, pas d’une liste d’exceptions ajoutées au fil des incidents.

### Étape 7 — Tester, observer et documenter

Effectuer les tests d’accès, d’isolation, de mobilité, de sortie vers les réseaux externes, de résilience et de surveillance. Documenter le résultat attendu, le résultat réel, les compteurs et les conditions de retour arrière.

### Diagramme 9 — Séquence de déploiement

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="470" viewBox="0 0 1000 470"><rect x="1" y="1" width="998" height="468" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Déploiement guidé : de l’inventaire à la validation</text><rect x="45" y="105" width="270" height="110" rx="14" fill="#1D3553" stroke="#68AEFF" stroke-width="2" /><circle cx="75" cy="137" r="18" fill="#68AEFF" stroke="#0B1220" stroke-width="1" /><text x="75" y="143" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#0B1220" text-anchor="middle">1</text><text x="200" y="140" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#F4F7FB" text-anchor="middle">Préparer</text><text x="180" y="173" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="middle">Inventaire, IP, DNS, NTP, AAA</text><rect x="365" y="105" width="270" height="110" rx="14" fill="#1D3553" stroke="#36D6B0" stroke-width="2" /><circle cx="395" cy="137" r="18" fill="#36D6B0" stroke="#0B1220" stroke-width="1" /><text x="395" y="143" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#0B1220" text-anchor="middle">2</text><text x="520" y="140" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#F4F7FB" text-anchor="middle">Underlay</text><text x="500" y="173" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="middle">Routage L3, reachability, MTU</text><rect x="685" y="105" width="270" height="110" rx="14" fill="#1D3553" stroke="#C4A1FF" stroke-width="2" /><circle cx="715" cy="137" r="18" fill="#C4A1FF" stroke="#0B1220" stroke-width="1" /><text x="715" y="143" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#0B1220" text-anchor="middle">3</text><text x="840" y="140" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#F4F7FB" text-anchor="middle">Contrôleur</text><text x="820" y="173" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="middle">Catalyst Center + intégration ISE</text><rect x="45" y="285" width="270" height="110" rx="14" fill="#1D3553" stroke="#FFBD69" stroke-width="2" /><circle cx="75" cy="317" r="18" fill="#FFBD69" stroke="#0B1220" stroke-width="1" /><text x="75" y="323" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#0B1220" text-anchor="middle">4</text><text x="200" y="320" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#F4F7FB" text-anchor="middle">Fabric</text><text x="180" y="353" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="middle">Edge, border, control plane</text><rect x="365" y="285" width="270" height="110" rx="14" fill="#1D3553" stroke="#36D6B0" stroke-width="2" /><circle cx="395" cy="317" r="18" fill="#36D6B0" stroke="#0B1220" stroke-width="1" /><text x="395" y="323" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#0B1220" text-anchor="middle">5</text><text x="520" y="320" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#F4F7FB" text-anchor="middle">Politique</text><text x="500" y="353" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="middle">VN, pools, gateways, SGT</text><rect x="685" y="285" width="270" height="110" rx="14" fill="#1D3553" stroke="#68AEFF" stroke-width="2" /><circle cx="715" cy="317" r="18" fill="#68AEFF" stroke="#0B1220" stroke-width="1" /><text x="715" y="323" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#0B1220" text-anchor="middle">6</text><text x="840" y="320" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#F4F7FB" text-anchor="middle">Valider</text><text x="820" y="353" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="middle">Tests, assurance, rollback</text><line x1="315" y1="160" x2="354.0" y2="160.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="365,160 354.0,165.72 354.0,154.28" fill="#F4F7FB" /><line x1="635" y1="160" x2="674.0" y2="160.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="685,160 674.0,165.72 674.0,154.28" fill="#F4F7FB" /><line x1="820" y1="215" x2="820.0" y2="274.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="820,285 814.28,274.0 825.72,274.0" fill="#F4F7FB" /><line x1="685" y1="340" x2="646.0" y2="340.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="635,340 646.0,334.28 646.0,345.72" fill="#F4F7FB" /><line x1="365" y1="340" x2="326.0" y2="340.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="315,340 326.0,334.28 326.0,345.72" fill="#F4F7FB" /><text x="500" y="448" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#FFBD69" text-anchor="middle">Ne passer à l’étape suivante qu’après des tests d’acceptation reproductibles.</text></svg>

## 11. La passerelle Anycast

Dans un LAN classique, une passerelle de sous-réseau est généralement l’interface L3 qui répond aux hôtes de ce sous-réseau. Dans SD-Access, la passerelle Anycast permet que des edge nodes qui desservent le même réseau logique utilisent la même adresse IP de passerelle selon le design provisionné. Cela évite que la passerelle logique soit simplement attachée à une position physique unique.

**Exemple pédagogique :** le sous-réseau `10.10.10.0/24` utilise `10.10.10.1` comme passerelle logique. Un terminal peut se connecter sur un edge différent tout en utilisant la passerelle attendue pour son réseau logique. Le vrai plan d’adressage doit toutefois être globalement cohérent et ne pas chevaucher des pools ou réseaux externes incompatibles.

Vérifie notamment : le pool et le sous-réseau associés à la VN, la présence de la passerelle sur les nœuds prévus, l’attribution DHCP, la résolution ARP/ND, les politiques de sécurité et le chemin de retour vers les services.

## 12. Border et connectivité externe

La fabric n’est pas isolée du monde réel : elle doit souvent atteindre des services partagés, un datacenter, une DMZ, un WAN ou Internet. Le border fait le lien entre les mécanismes de la fabric et la méthode de raccordement au réseau externe.

Deux grandes familles de transit inter-sites existent dans les designs SD-Access :

- **IP-based transit :** le trafic entre sites fabric est dé-encapsulé au border puis routé dans le réseau IP traditionnel entre les sites ; le border distant reconstitue la fabric selon le design. Les contextes VN et SGT doivent être examinés pour s’assurer que les politiques prévues restent cohérentes au-delà du domaine fabric.
- **SD-Access transit :** le trafic reste encapsulé dans la fabric entre sites, ce qui peut transporter les constructions de macro- et micro-segmentation à travers le transit. Cette option possède ses propres prérequis de reachability, de MTU, de contrôle et de compatibilité ; elle ne doit pas être choisie sans validation de la topologie et des versions.

Ces modèles ne sont pas interchangeables dans tous les cas. Le besoin de conserver les politiques de groupe d’un site à l’autre, la topologie WAN existante et les fonctions supportées contribuent au choix. Pour un cours débutant, retiens que le border est le point d’intégration, et que le chemin retour et les politiques aux frontières sont essentiels.

### Diagramme 10 — Sortie et transit

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="455" viewBox="0 0 1000 455"><rect x="1" y="1" width="998" height="453" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Raccordement externe : border, transit et autres réseaux</text><rect x="30" y="100" width="250" height="300" rx="14" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="155" y="135" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#36D6B0" text-anchor="middle">FABRIC SITE A</text><rect x="65" y="165" width="180" height="65" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="155" y="191" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Edge nodes</text><text x="155" y="212" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">terminaux</text><rect x="65" y="285" width="180" height="65" rx="12" fill="#1D3553" stroke="#FFBD69" stroke-width="2" /><text x="155" y="311" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border nodes</text><text x="155" y="332" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">sortie</text><rect x="376" y="135" width="250" height="220" rx="16" fill="#1D3553" stroke="#C4A1FF" stroke-width="3" /><text x="501" y="171" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#C4A1FF" text-anchor="middle">WAN / TRANSIT</text><text x="501" y="218" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">IP transit : routage IP</text><text x="501" y="239" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">handoff VRF-Lite</text><text x="501" y="260" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">politiques à mapper</text><text x="501" y="311" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#36D6B0" text-anchor="middle">ou SD-Access transit</text><text x="501" y="332" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#36D6B0" text-anchor="middle">VXLAN inter-sites + SGT*</text><rect x="720" y="100" width="250" height="300" rx="14" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="845" y="135" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#36D6B0" text-anchor="middle">FABRIC SITE B</text><rect x="755" y="165" width="180" height="65" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="845" y="191" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Edge nodes</text><text x="845" y="212" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">terminaux</text><rect x="755" y="285" width="180" height="65" rx="12" fill="#1D3553" stroke="#FFBD69" stroke-width="2" /><text x="845" y="311" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border nodes</text><text x="845" y="332" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">sortie</text><line x1="245" y1="317" x2="365.64621433262965" y2="273.7147169951634" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="376,270 367.57786717011464,279.098685542196 363.71456149514466,268.33074844813086" fill="#FFBD69" /><line x1="626" y1="270" x2="744.6646135920522" y2="313.2343940994299" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="755,317 742.7064985237557,318.60879503156275 746.6227286603487,307.85999316729703" fill="#FFBD69" /><text x="500" y="424" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">*Selon modèle, release et design pris en charge</text></svg>

## 13. Wi-Fi et SD-Access

SD-Access peut intégrer le Wi-Fi à l’architecture fabric afin d’aligner l’accès sans fil avec les réseaux logiques, l’identité et les politiques. Les points d’accès, les contrôleurs sans fil, le réseau underlay, les nœuds fabric et les services d’identité ont des responsabilités distinctes. Le chemin réel du trafic dépend du mode de déploiement sans fil, des versions et de la conception retenue ; il ne faut pas supposer que toutes les architectures font transiter toutes les données de la même manière par le contrôleur WLAN.

Lors de la préparation, il faut planifier les SSID, profils radio, pools d’adresses, identités, affectation VN/politique, mobilité, redondance du contrôleur et accès aux services partagés. Il faut aussi examiner la capacité radio, les zones de couverture, les canaux et l’expérience utilisateur : une bonne fabric ne corrige pas une couverture RF insuffisante.

### Diagramme 11 — Wi-Fi intégré à la fabric

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="445" viewBox="0 0 1000 445"><rect x="1" y="1" width="998" height="443" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Wi-Fi fabric : intégration du client dans les politiques de la fabric</text><rect x="35" y="180" width="135" height="90" rx="13" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="102" y="213" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Client Wi-Fi</text><text x="102" y="234" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">SSID</text><rect x="230" y="180" width="135" height="90" rx="13" fill="#1D3553" stroke="#36D6B0" stroke-width="2" /><text x="297" y="213" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Point d’accès</text><text x="297" y="234" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">AP</text><rect x="427" y="180" width="145" height="90" rx="13" fill="#1D3553" stroke="#68AEFF" stroke-width="2" /><text x="499" y="210" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Fabric edge</text><text x="499" y="231" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VXLAN</text><rect x="645" y="90" width="150" height="80" rx="13" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="720" y="119" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">WLC</text><text x="720" y="140" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">gestion radio</text><rect x="645" y="278" width="150" height="80" rx="13" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="720" y="307" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">ISE</text><text x="720" y="328" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">identité</text><rect x="855" y="180" width="110" height="90" rx="13" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="910" y="213" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN / services</text><text x="910" y="233" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">autorisés</text><line x1="170" y1="225" x2="219.0" y2="225.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="230,225 219.0,230.72 219.0,219.28" fill="#36D6B0" /><line x1="365" y1="225" x2="416.0" y2="225.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="427,225 416.0,230.72 416.0,219.28" fill="#36D6B0" /><line x1="572" y1="218" x2="844.0" y2="218.0" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="855,218 844.0,223.72 844.0,212.28" fill="#68AEFF" /><line x1="720" y1="170" x2="720.0" y2="267.0" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="720,278 714.28,267.0 725.72,267.0" fill="#C4A1FF" /><line x1="645" y1="318" x2="580.0489372801193" y2="257.49764020613856" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="572,250 583.9477101873114,253.3121928204765 576.1501643729272,261.6830875918006" fill="#FFBD69" /><text x="500" y="68" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">La signalisation et le chemin de données ne sont pas forcément le même trajet.</text><text x="500" y="410" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FFBD69" text-anchor="middle">Le mode exact dépend du design WLAN/fabric et des versions supportées.</text></svg>

## 14. Assurance, visibilité et dépannage

Le dépannage doit associer l’expérience utilisateur à un chemin de vérification. « Le poste ne fonctionne pas » ne décrit pas encore une cause. Il faut préciser si l’équipement obtient une adresse IP, résout DNS, atteint sa passerelle, atteint une destination dans la même VN, atteint une autre VN ou sort vers un réseau externe.

Une méthode simple consiste à vérifier les couches dans l’ordre :

1. Connectivité locale et état du port ou de l’accès Wi-Fi.
2. Authentification et résultat d’autorisation, identité et politique attribuée.
3. Connectivité IP du underlay et reachability des RLOC.
4. État des registrations et mappings du plan de contrôle.
5. Transport de données, encapsulation, MTU et politiques VN/SGT.
6. Border, route externe, pare-feu et chemin retour.

Les outils d’assurance et de télémétrie de Catalyst Center peuvent aider à associer un terminal, un équipement, une configuration et des événements. Ils doivent être complétés, au besoin, par les sorties CLI adaptées à l’équipement et à la version, les journaux ISE, les données de routage et les tests applicatifs. Ne collecte pas seulement des captures : note l’heure, le terminal, l’IP, la VN, le port, la destination et les conditions de reproduction.

### Diagramme 12 — Arbre de dépannage

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="490" viewBox="0 0 1000 490"><rect x="1" y="1" width="998" height="488" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Dépannage méthodique : remonter couche par couche</text><rect x="75" y="78" width="850" height="48" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><circle cx="103" cy="102" r="15" fill="#36D6B0" stroke="#0B1220" stroke-width="1" /><text x="103" y="108" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#0B1220" text-anchor="middle">1</text><text x="145" y="98" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#36D6B0" text-anchor="start">Accès</text><text x="145" y="117" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">Lien, PoE, VLAN de transport local, état du port</text><rect x="75" y="140" width="850" height="48" rx="10" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><circle cx="103" cy="164" r="15" fill="#C4A1FF" stroke="#0B1220" stroke-width="1" /><text x="103" y="170" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#0B1220" text-anchor="middle">2</text><text x="145" y="160" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#C4A1FF" text-anchor="start">Identité</text><text x="145" y="179" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">802.1X/MAB, résultat ISE, VLAN/VN, SGT</text><rect x="75" y="202" width="850" height="48" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><circle cx="103" cy="226" r="15" fill="#68AEFF" stroke="#0B1220" stroke-width="1" /><text x="103" y="232" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#0B1220" text-anchor="middle">3</text><text x="145" y="222" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#68AEFF" text-anchor="start">Underlay</text><text x="145" y="241" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">IP RLOC, adjacences, routes, MTU</text><rect x="75" y="264" width="850" height="48" rx="10" fill="#182941" stroke="#FFBD69" stroke-width="2" /><circle cx="103" cy="288" r="15" fill="#FFBD69" stroke="#0B1220" stroke-width="1" /><text x="103" y="294" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#0B1220" text-anchor="middle">4</text><text x="145" y="284" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#FFBD69" text-anchor="start">Control plane</text><text x="145" y="303" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">Enregistrement EID, mapping LISP, nœud CP</text><rect x="75" y="326" width="850" height="48" rx="10" fill="#182941" stroke="#FF7788" stroke-width="2" /><circle cx="103" cy="350" r="15" fill="#FF7788" stroke="#0B1220" stroke-width="1" /><text x="103" y="356" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#0B1220" text-anchor="middle">5</text><text x="145" y="346" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#FF7788" text-anchor="start">Data / policy</text><text x="145" y="365" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">Encapsulation VXLAN, VN/SGT, ACL/SGACL</text><rect x="75" y="388" width="850" height="48" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><circle cx="103" cy="412" r="15" fill="#36D6B0" stroke="#0B1220" stroke-width="1" /><text x="103" y="418" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#0B1220" text-anchor="middle">6</text><text x="145" y="408" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#36D6B0" text-anchor="start">Sortie</text><text x="145" y="427" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">Border, route externe, firewall, chemin retour</text><text x="500" y="466" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#FFBD69" text-anchor="middle">Mesurer et isoler la couche en défaut avant de modifier la configuration.</text></svg>

### Commandes et vérifications : prudence sur la version

Les commandes exactes visibles sur les commutateurs dépendent de la plateforme et du logiciel. Dans un environnement de formation, l’approche suivante est recommandée :

- Vérifier les interfaces, l’adressage de gestion et la reachability IP.
- Vérifier l’état du protocole de routage underlay et la table de routage.
- Examiner les états et informations fabric via Catalyst Center et les commandes supportées pour la version.
- Examiner les résultats d’authentification dans ISE et les journaux associés.
- Tester la résolution DNS, DHCP, la passerelle, un service de même VN, puis la destination externe.
- Vérifier le MTU avec une méthode adaptée aux équipements et aux chemins réellement utilisés.

Ne colle pas des commandes trouvées dans une version différente sans vérifier leur disponibilité. Un même rôle logique peut exposer des commandes, compteurs et modèles de configuration différents selon le matériel.

## 15. Exemple guidé : petit campus

Une entreprise possède un bâtiment principal, environ 300 utilisateurs, des imprimantes, des objets IoT et des invités Wi-Fi. Elle souhaite simplifier l’administration, isoler les invités et réduire les accès latéraux non souhaités.

### Besoins

- Les employés accèdent aux applications métier et aux services partagés nécessaires.
- Les invités disposent d’un accès Internet contrôlé et ne peuvent pas atteindre les réseaux internes.
- Les imprimantes ne peuvent accepter que les protocoles nécessaires depuis les groupes autorisés.
- Les objets IoT n’ont pas de privilèges généraux vers les postes ou les serveurs.
- Les équipes IT conservent un chemin de gestion limité et surveillé.

### Proposition conceptuelle

- Un underlay L3 routé et redondant.
- Une VN CORP pour les utilisateurs internes, une VN GUEST pour les invités et des VN supplémentaires si l’isolation de tables de routage le justifie réellement.
- Des SGT pour distinguer les groupes au sein de chaque zone logique et une matrice de politiques validée avec les équipes sécurité.
- Des edge nodes répartis sur les accès du bâtiment, des borders redondants selon le besoin de disponibilité et des control plane nodes dimensionnés selon le design.
- Catalyst Center pour le provisionnement/assurance et ISE pour les fonctions d’identité et de politique prévues.
- Une sortie externe avec règles pare-feu, DHCP/DNS et chemin retour testés.

Cette proposition est pédagogique, pas un BOM ou un design certifié. Le nombre et les modèles d’équipements, les licences, les méthodes d’intégration, les limites d’échelle et les fonctions exactes doivent être déterminés à partir de la matrice de compatibilité et d’une conception détaillée.

### Tests d’acceptation

| Test | Résultat attendu | Preuve à conserver |
|---|---|---|
| Poste employé authentifié | Accès aux services métier autorisés | Résultat ISE + test applicatif |
| Terminal invité | Internet selon politique, pas d’accès interne non autorisé | Tests positifs et négatifs |
| Imprimante | Accès seulement depuis les sources et ports requis | Tests de flux et journaux |
| Endpoint déplacé | Accès cohérent sur un autre edge dans le périmètre prévu | Test de mobilité + assurance |
| Perte d’un lien underlay | Convergence dans les objectifs définis | Horodatages, routes, perte/latence |
| Panne d’un équipement redondant | Service maintenu selon le SLA convenu | Procédure de test de panne |
| Paquet de grande taille | Pas de perte due à un MTU mal dimensionné | Tests de MTU de bout en bout |

## 16. Erreurs fréquentes chez les débutants

**Confondre VN et SGT.** Une VN sépare le domaine de routage logique ; le SGT représente un groupe de sécurité utilisé par les politiques. Les deux peuvent être complémentaires.

**Penser que Catalyst Center transporte les paquets.** Il automatise et supervise ; la transmission de données est assurée par les équipements fabric.

**Penser que VXLAN règle l’identité ou la sécurité à lui seul.** VXLAN fournit un mécanisme d’encapsulation et de transport. La segmentation et la politique reposent sur les constructions et règles prévues par l’architecture.

**Commencer par l’overlay avant d’avoir validé l’underlay.** Si les RLOC sont injoignables ou le MTU incorrect, le diagnostic du trafic fabric devient beaucoup plus difficile.

**Supposer que chaque switch doit toujours porter un seul rôle.** Certains designs colocalisent des rôles ; d’autres les séparent pour la résilience et l’échelle. La compatibilité et les bonnes pratiques doivent guider le choix.

**Croire qu’un terminal « connecté » est forcément autorisé à accéder à tout.** L’accès physique, l’authentification, l’affectation au réseau et l’autorisation de joindre un service sont des étapes distinctes.

**Copier une configuration d’une ancienne version.** Les capacités, workflows et commandes évoluent. Toujours contrôler les guides et la matrice correspondant au matériel et au logiciel réellement déployés.

## 17. Laboratoire pédagogique

### Objectif

Dessiner une fabric conceptuelle avec deux edge nodes, un control plane node, un border node, un nœud intermédiaire et trois types de terminaux : employé, IoT et invité. Produire ensuite un plan d’adressage fictif et une matrice d’accès.

### Étape A — Dessiner la topologie

1. Place deux edge nodes redondants pour illustrer l’accès utilisateur.
2. Ajoute un control plane node et explique son rôle de base de mappings.
3. Relie les rôles par un underlay L3 routé avec au moins un chemin alternatif.
4. Ajoute un border vers un pare-feu ou un réseau externe.
5. Indique où se trouvent Catalyst Center et ISE ; distingue la gestion et l’identité du chemin de données.

### Étape B — Définir les VN et groupes

Construis une table de conception avec `VN_CORP`, `VN_GUEST`, et si nécessaire `VN_IOT`. Associe à chacune un sous-réseau de laboratoire non utilisé dans ton environnement réel. Définis ensuite des groupes tels que `EMPLOYES`, `IOT`, `INVITES`, `IT_ADMIN` et établis quelles communications sont autorisées ou refusées.

### Étape C — Écrire la matrice de test

Pour chaque flux important, note : source, destination, protocole/port, VN source, VN destination, groupe source, groupe destination, décision attendue, point de contrôle et preuve. Inclue des cas autorisés **et** refusés ; une politique de sécurité doit être testée dans les deux sens.

### Étape D — Vérifier les dépendances

Liste les services dont chaque terminal a besoin : DHCP, DNS, NTP, authentification, applications, accès Internet. Vérifie la route aller et la route retour, les règles du pare-feu et les contraintes de MTU. Définis un plan de retour arrière avant un changement affectant les utilisateurs.

### Livrable du laboratoire

Un schéma, un plan IP, une table VN/SGT, une matrice de flux, une séquence de déploiement et une checklist d’acceptation. Le laboratoire ne doit pas être exécuté sur un réseau de production sans matériels compatibles, procédure de changement et plan de retour arrière.

## 18. Quiz de validation

Réponds d’abord sans regarder les corrigés.

1. Quel problème général SD-Access cherche-t-il à traiter ?
2. Quelle est la différence entre underlay et overlay ?
3. Quel composant gère et automatise le déploiement SD-Access ?
4. Quel protocole sert de base au plan de contrôle de la fabric ?
5. Quel mécanisme fournit le plan de données de la fabric ?
6. Quelle est la fonction générale d’un fabric edge node ?
7. Quelle est la fonction générale d’un control plane node ?
8. Quel rôle joue le border node ?
9. À quoi sert un EID-to-RLOC mapping ?
10. Pourquoi le MTU doit-il être vérifié sur l’ensemble du chemin ?
11. Quelle différence de conception existe entre une VN/VRF et un SGT ?
12. À quoi sert Cisco ISE dans un design SD-Access intégré ?
13. Pourquoi MAB ne doit-il pas être assimilé à une authentification forte ?
14. Que vérifies-tu si le poste obtient une adresse IP mais ne rejoint pas une application externe ?
15. Pourquoi les commandes et fonctionnalités doivent-elles être vérifiées pour la version et le modèle utilisés ?

### Corrigé

1. Automatiser et rendre plus cohérent le réseau campus, la segmentation, l’accès filaire/sans fil et la visibilité.
2. L’underlay transporte le trafic IP entre localisateurs de fabric ; l’overlay porte les réseaux logiques et le trafic des endpoints.
3. Cisco Catalyst Center.
4. LISP, dans l’architecture SD-Access classique documentée.
5. VXLAN.
6. Connecter les endpoints et assurer les fonctions de bord d’accès de fabric, notamment la passerelle Anycast selon le design.
7. Conserver et distribuer les mappings qui permettent de localiser les endpoints dans la fabric.
8. Raccorder la fabric aux réseaux externes ou au transit selon le design.
9. Relier une identité d’endpoint à son localisateur de fabric pour orienter le trafic.
10. L’encapsulation ajoute un surcoût ; un MTU insuffisant peut provoquer des pertes sélectives.
11. La VN/VRF sépare le contexte de routage ; le SGT représente un groupe de sécurité utilisé par les politiques.
12. Fournir des fonctions d’identité, d’authentification et d’autorisation dans les scénarios d’intégration prévus.
13. Il repose souvent sur l’adresse MAC, qui peut être usurpée, et ne prouve pas la même identité qu’un mécanisme cryptographique correctement configuré.
14. Vérifier DNS, passerelle, VN/SGT, route et chemin retour, border, règles de pare-feu, politique d’accès et MTU, à partir d’un test reproductible.
15. Parce que les combinaisons de matériel, versions logicielles, licences et fonctions supportées varient ; les guides actuels sont la référence opérationnelle.

## 19. Glossaire essentiel

| Terme | Définition simplifiée |
|---|---|
| SD-Access | Architecture Cisco de campus pilotée par l’intention et reposant sur une fabric. |
| Fabric | Ensemble logique de nœuds réseau qui implémentent la connectivité et les politiques fabric. |
| Underlay | Réseau IP de transport qui relie les localisateurs de fabric. |
| Overlay | Réseaux logiques superposés à l’underlay. |
| VN | Virtual Network, réseau logique de la fabric. |
| VRF | Table de routage isolée ; une VN SD-Access est représentée par une VRF dans les designs courants. |
| LISP | Protocole de contrôle qui relie EID et RLOC. |
| EID | Endpoint Identifier : identité réseau logique de l’endpoint. |
| RLOC | Routing Locator : localisateur de nœud de fabric sur le réseau IP. |
| VXLAN | Encapsulation de données de couche 2 dans un transport IP/UDP. |
| SGT | Security Group Tag : identifiant de groupe de sécurité. |
| TrustSec | Technologies Cisco de segmentation et de politique basées sur des groupes de sécurité. |
| Catalyst Center | Plateforme de gestion, orchestration et assurance utilisée par SD-Access. |
| ISE | Identity Services Engine ; identité, authentification et autorisation. |
| Edge node | Raccordement des terminaux à la fabric. |
| Control plane node | Point de contrôle des mappings endpoint-localisateur. |
| Border node | Raccordement vers les réseaux externes ou transit. |
| Anycast gateway | Passerelle logique cohérente présente sur les edge concernés. |
| MTU | Taille maximale du paquet transportable sur un lien sans fragmentation au niveau considéré. |
| 802.1X | Cadre de contrôle d’accès réseau basé sur l’authentification d’un supplicant. |
| MAB | Méthode de contrôle d’accès fondée sur l’adresse MAC, généralement utilisée comme solution de compatibilité. |

## 20. Checklist avant de considérer un design prêt

- [ ] Les besoins, les flux et les zones de sécurité sont documentés.
- [ ] Le matériel, les versions et les fonctions sont validés dans la matrice Cisco.
- [ ] Les services de gestion, NTP, DNS, DHCP, AAA et journalisation sont prévus.
- [ ] L’underlay L3, les RLOC, la redondance et le MTU ont été testés.
- [ ] Les rôles de fabric et leur placement sont justifiés par le design.
- [ ] Les VN, sous-réseaux, pools et passerelles Anycast sont cohérents.
- [ ] Les groupes SGT et la matrice de politiques ont un propriétaire métier/sécurité.
- [ ] Les sorties externes et les chemins retour ont été testés.
- [ ] Les tests comprennent des flux autorisés et interdits.
- [ ] La procédure de changement, la sauvegarde et le rollback sont documentés.
- [ ] La supervision et les preuves d’acceptation sont définies avant la migration.

## 21. Références officielles

Les guides Cisco évoluent ; pour un déploiement réel, ouvrir la documentation correspondant à la version logicielle et au matériel retenus.

1. **Cisco Design Zone — Software-Defined Access** : https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-sda-design-guide.html
2. **SD-Access Deployment Using Cisco Catalyst Center** : https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/cisco-validated-solution-profiles/validated-profile-sda-deployment.html
3. **Cisco Catalyst Center Compatibility Matrix** : accessible depuis la documentation de déploiement Cisco SD-Access et la section de compatibilité correspondante.

### Limites et prudence

Ce cours est une introduction technique destinée à l’apprentissage. Il ne constitue pas une recommandation de dimensionnement, une liste de matériels, un devis, un guide de migration certifié ni une procédure de changement pour un réseau de production. Les fonctions disponibles et la séquence de configuration dépendent de la compatibilité matérielle, des versions, licences, topologie, capacités de l’underlay et du design documenté. En production, utiliser les documents officiels en vigueur et tester la solution dans un environnement approprié avant la migration.
